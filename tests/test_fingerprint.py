from __future__ import annotations

from harness_manager.fingerprint import fingerprint_directory


def test_fingerprint_directory_matches_for_same_relative_paths_and_contents(tmp_path):
    first = tmp_path / "first"
    second = tmp_path / "second"
    (first / "nested").mkdir(parents=True)
    (second / "nested").mkdir(parents=True)
    (first / "root.txt").write_text("same", encoding="utf-8")
    (second / "root.txt").write_text("same", encoding="utf-8")
    (first / "nested" / "child.bin").write_bytes(b"\x00\x01")
    (second / "nested" / "child.bin").write_bytes(b"\x00\x01")

    assert fingerprint_directory(first) == fingerprint_directory(second)


def test_fingerprint_directory_changes_when_file_changes(tmp_path):
    directory = tmp_path / "skill"
    directory.mkdir()
    file_path = directory / "skill.md"
    file_path.write_text("before", encoding="utf-8")
    original = fingerprint_directory(directory)

    file_path.write_text("after", encoding="utf-8")

    assert fingerprint_directory(directory) != original
