from __future__ import annotations

import shutil
import tempfile
import zipfile
from pathlib import Path

MAX_ZIP_ENTRIES = 1000
MAX_ZIP_TOTAL_BYTES = 250 * 1024 * 1024
MAX_ZIP_FILE_BYTES = 50 * 1024 * 1024
MAX_ZIP_COMPRESSION_RATIO = 100


def copy_directory(source: Path | str, destination: Path | str, overwrite: bool = False) -> Path:
    source_path = Path(source)
    destination_path = Path(destination)
    if not source_path.is_dir():
        raise NotADirectoryError(source_path)
    if destination_path.exists():
        if not overwrite:
            raise FileExistsError(destination_path)
        safe_remove_directory(destination_path)
    return Path(shutil.copytree(source_path, destination_path))


def safe_remove_directory(path: Path | str) -> None:
    directory = Path(path)
    if not directory.exists():
        return
    if directory.is_symlink() and directory.is_dir():
        raise ValueError(f"Refusing to remove directory symlink: {directory}")
    if not directory.is_dir():
        raise NotADirectoryError(directory)

    resolved = directory.resolve()
    if resolved.parent == resolved or resolved == Path.home().resolve():
        raise ValueError(f"Refusing to remove unsafe directory: {directory}")
    shutil.rmtree(directory)


def make_zip(source_dir: Path | str, zip_path: Path | str) -> Path:
    source_path = Path(source_dir)
    archive_path = Path(zip_path)
    if not source_path.is_dir():
        raise NotADirectoryError(source_path)

    archive_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for file_path in sorted(source_path.rglob("*"), key=lambda path: path.relative_to(source_path).as_posix()):
            if file_path.is_file():
                archive.write(file_path, file_path.relative_to(source_path).as_posix())
    return archive_path


def extract_zip(zip_path: Path | str) -> Path:
    archive_path = Path(zip_path)
    temp_dir = Path(tempfile.mkdtemp(prefix="skillpkg-"))
    root = temp_dir.resolve()

    try:
        with zipfile.ZipFile(archive_path) as archive:
            entries = archive.infolist()
            if len(entries) > MAX_ZIP_ENTRIES:
                raise ValueError(
                    f"Zip has too many entries: {len(entries)} > {MAX_ZIP_ENTRIES}"
                )

            total_size = 0
            for info in entries:
                target = (root / info.filename).resolve()
                if not target.is_relative_to(root):
                    raise ValueError(f"Zip entry escapes extraction directory: {info.filename}")
                if info.is_dir():
                    continue
                if info.file_size > MAX_ZIP_FILE_BYTES:
                    raise ValueError(
                        f"Zip entry too large: {info.filename} ({info.file_size} bytes)"
                    )
                total_size += info.file_size
                if total_size > MAX_ZIP_TOTAL_BYTES:
                    raise ValueError(
                        f"Zip total uncompressed size too large: {total_size} bytes"
                    )
                if info.file_size and info.compress_size == 0:
                    raise ValueError(
                        f"Zip entry compression ratio too high: {info.filename}"
                    )
                if info.compress_size:
                    ratio = info.file_size / info.compress_size
                    if ratio > MAX_ZIP_COMPRESSION_RATIO:
                        raise ValueError(
                            f"Zip entry compression ratio too high: {info.filename}"
                        )
            archive.extractall(root)
    except Exception:
        shutil.rmtree(root, ignore_errors=True)
        raise

    return root
