from __future__ import annotations

import hashlib
from pathlib import Path

IGNORED_PATH_PARTS = {".DS_Store", "Thumbs.db", "__pycache__"}


def fingerprint_directory(path: Path | str) -> str:
    directory = Path(path)
    if not directory.is_dir():
        raise NotADirectoryError(directory)

    digest = hashlib.sha256()
    for file_path in _iter_files(directory):
        relative_path = file_path.relative_to(directory).as_posix()
        file_bytes = file_path.read_bytes()
        digest.update(relative_path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(len(file_bytes).to_bytes(8, "big"))
        digest.update(file_bytes)
    return digest.hexdigest()


def _iter_files(directory: Path) -> list[Path]:
    files = [
        path
        for path in directory.rglob("*")
        if path.is_file() and not (set(path.relative_to(directory).parts) & IGNORED_PATH_PARTS)
    ]
    return sorted(files, key=lambda path: path.relative_to(directory).as_posix())
