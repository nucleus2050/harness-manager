from pathlib import Path
import zipfile

import pytest

import harness_manager.file_ops as file_ops
from harness_manager.file_ops import copy_directory, extract_zip, safe_remove_directory


def _make_directory_symlink(link: Path, target: Path) -> None:
    try:
        link.symlink_to(target, target_is_directory=True)
    except (NotImplementedError, OSError) as exc:
        pytest.skip(f"directory symlinks are not available: {exc}")


def test_safe_remove_directory_nonexistent_is_noop(tmp_path: Path) -> None:
    safe_remove_directory(tmp_path / "missing")


def test_safe_remove_directory_file_path_raises(tmp_path: Path) -> None:
    file_path = tmp_path / "file.txt"
    file_path.write_text("content", encoding="utf-8")

    with pytest.raises(NotADirectoryError):
        safe_remove_directory(file_path)


def test_safe_remove_directory_refuses_filesystem_root(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    root = Path(tmp_path.anchor)

    def fail_if_called(path: Path) -> None:
        raise AssertionError(f"rmtree must not be called for root: {path}")

    monkeypatch.setattr("harness_manager.file_ops.shutil.rmtree", fail_if_called)

    with pytest.raises(ValueError):
        safe_remove_directory(root)


def test_safe_remove_directory_refuses_directory_symlink(tmp_path: Path) -> None:
    target = tmp_path / "target"
    target.mkdir()
    link = tmp_path / "link"
    _make_directory_symlink(link, target)

    with pytest.raises(ValueError):
        safe_remove_directory(link)

    assert target.is_dir()


def test_copy_directory_overwrite_refuses_directory_symlink_destination(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "source.txt").write_text("content", encoding="utf-8")
    target = tmp_path / "target"
    target.mkdir()
    link = tmp_path / "destination"
    _make_directory_symlink(link, target)

    with pytest.raises(ValueError):
        copy_directory(source, link, overwrite=True)

    assert target.is_dir()


def test_extract_zip_rejects_too_many_entries(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(file_ops, "MAX_ZIP_ENTRIES", 2, raising=False)
    archive_path = tmp_path / "too-many.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("one.txt", "1")
        archive.writestr("two.txt", "2")
        archive.writestr("three.txt", "3")

    with pytest.raises(ValueError, match="too many entries"):
        extract_zip(archive_path)


def test_extract_zip_rejects_oversized_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(file_ops, "MAX_ZIP_FILE_BYTES", 4, raising=False)
    archive_path = tmp_path / "oversized-file.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("large.txt", "12345")

    with pytest.raises(ValueError, match="too large"):
        extract_zip(archive_path)


def test_extract_zip_rejects_oversized_total(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(file_ops, "MAX_ZIP_TOTAL_BYTES", 6, raising=False)
    archive_path = tmp_path / "oversized-total.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("one.txt", "1234")
        archive.writestr("two.txt", "5678")

    with pytest.raises(ValueError, match="total uncompressed size"):
        extract_zip(archive_path)


def test_extract_zip_rejects_high_compression_ratio(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(file_ops, "MAX_ZIP_COMPRESSION_RATIO", 1, raising=False)
    archive_path = tmp_path / "high-ratio.zip"
    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("compressed.txt", "0" * 100)

    with pytest.raises(ValueError, match="compression ratio"):
        extract_zip(archive_path)
