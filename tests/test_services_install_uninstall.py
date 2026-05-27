from __future__ import annotations

from pathlib import Path

import pytest

from harness_manager.app_paths import AppPaths
from harness_manager.db import connect, initialize_database
from harness_manager.fingerprint import fingerprint_directory
from harness_manager.services import HarnessService


def _service(app_root: Path) -> HarnessService:
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    initialize_database(conn)
    return HarnessService(paths, conn)


def _package_with_sample(service: HarnessService, sample_skill: Path) -> tuple[str, str]:
    skill = service.import_skill(sample_skill, "codex")
    package = service.create_package("Daily Tools", "Useful daily workflow", [skill.id])
    return package.id, skill.id


def test_install_package_copies_skills_to_target_and_records_install(app_root, sample_skill, tmp_path):
    service = _service(app_root)
    package_id, skill_id = _package_with_sample(service, sample_skill)
    target = tmp_path / "codex-skills"
    target.mkdir()

    installed_paths = service.install_package(package_id, "codex", target)

    installed_path = target / skill_id
    assert installed_paths == [installed_path]
    assert (installed_path / "SKILL.md").read_text(encoding="utf-8") == "# Sample Skill\n\nBody\n"
    record = service.conn.execute(
        """
        SELECT package_id, skill_id, client_type, target_path, installed_path, fingerprint, status
        FROM install_records
        """
    ).fetchone()
    assert tuple(record) == (
        package_id,
        skill_id,
        "codex",
        str(target),
        str(installed_path),
        fingerprint_directory(installed_path),
        "installed",
    )


def test_install_package_requires_existing_target_directory(app_root, sample_skill, tmp_path):
    service = _service(app_root)
    package_id, _skill_id = _package_with_sample(service, sample_skill)

    with pytest.raises(NotADirectoryError):
        service.install_package(package_id, "codex", tmp_path / "missing")


def test_install_package_rejects_malicious_skill_id_escape(app_root, tmp_path):
    service = _service(app_root)
    package_id = service.packages.create_package("Bad Package", "")
    service.skills.upsert_skill(
        "../evil",
        "evil",
        "codex",
        "skills/../evil",
        "fingerprint",
    )
    service.packages.add_skill(package_id, "../evil", 1)
    service.conn.commit()
    target = tmp_path / "codex-skills"
    target.mkdir()

    with pytest.raises(ValueError):
        service.install_package(package_id, "codex", target)

    assert not (tmp_path / "evil").exists()


def test_install_package_rejects_skill_relative_path_outside_managed_skills(app_root, tmp_path):
    service = _service(app_root)
    outside_source = tmp_path / "outside-source"
    outside_source.mkdir()
    (outside_source / "SKILL.md").write_text("# Outside\n", encoding="utf-8")
    package_id = service.packages.create_package("Bad Package", "")
    service.skills.upsert_skill(
        "safe-id",
        "safe-id",
        "codex",
        str(outside_source),
        fingerprint_directory(outside_source),
    )
    service.packages.add_skill(package_id, "safe-id", 1)
    service.conn.commit()
    target = tmp_path / "codex-skills"
    target.mkdir()

    with pytest.raises(ValueError):
        service.install_package(package_id, "codex", target)

    assert not (target / "safe-id").exists()


def test_install_package_cleans_up_previous_copy_when_later_skill_copy_fails(
    app_root, sample_skill, tmp_path
):
    service = _service(app_root)
    first = service.import_skill(sample_skill, "codex")
    second_source = tmp_path / "second-skill"
    second_source.mkdir()
    (second_source / "SKILL.md").write_text("# Second\n", encoding="utf-8")
    second = service.import_skill(second_source, "codex")
    package = service.create_package("Two Skills", "", [first.id, second.id])
    target = tmp_path / "codex-skills"
    target.mkdir()
    (target / second.id).mkdir()

    with pytest.raises(FileExistsError):
        service.install_package(package.id, "codex", target)

    assert not (target / first.id).exists()
    assert (target / second.id).is_dir()
    active_record = service.conn.execute(
        """
        SELECT id FROM install_records
        WHERE skill_id = ? AND status = 'installed'
        """,
        (first.id,),
    ).fetchone()
    assert active_record is None


def test_uninstall_package_deletes_unchanged_installed_skill(app_root, sample_skill, tmp_path):
    service = _service(app_root)
    package_id, skill_id = _package_with_sample(service, sample_skill)
    target = tmp_path / "codex-skills"
    target.mkdir()
    installed_path = service.install_package(package_id, "codex", target)[0]

    statuses = service.uninstall_package(package_id, "codex")

    assert statuses == {skill_id: "uninstalled"}
    assert not installed_path.exists()
    record = service.conn.execute(
        "SELECT status, uninstalled_at FROM install_records WHERE skill_id = ?", (skill_id,)
    ).fetchone()
    assert record["status"] == "uninstalled"
    assert record["uninstalled_at"] is not None


def test_uninstall_package_refuses_modified_installed_skill(app_root, sample_skill, tmp_path):
    service = _service(app_root)
    package_id, skill_id = _package_with_sample(service, sample_skill)
    target = tmp_path / "codex-skills"
    target.mkdir()
    installed_path = service.install_package(package_id, "codex", target)[0]
    (installed_path / "SKILL.md").write_text("# Local Edit\n", encoding="utf-8")

    statuses = service.uninstall_package(package_id, "codex")

    assert statuses == {skill_id: "modified"}
    assert installed_path.exists()
    record = service.conn.execute(
        "SELECT status, uninstalled_at FROM install_records WHERE skill_id = ?", (skill_id,)
    ).fetchone()
    assert record["status"] == "modified"
    assert record["uninstalled_at"] is None


def test_uninstall_package_refuses_tampered_installed_path_outside_target(
    app_root, sample_skill, tmp_path
):
    service = _service(app_root)
    package_id, skill_id = _package_with_sample(service, sample_skill)
    target = tmp_path / "codex-skills"
    target.mkdir()
    service.install_package(package_id, "codex", target)
    arbitrary_dir = tmp_path / "do-not-delete"
    arbitrary_dir.mkdir()
    (arbitrary_dir / "SKILL.md").write_text("# Important\n", encoding="utf-8")
    service.conn.execute(
        """
        UPDATE install_records
        SET installed_path = ?, fingerprint = ?
        WHERE skill_id = ?
        """,
        (str(arbitrary_dir), fingerprint_directory(arbitrary_dir), skill_id),
    )
    service.conn.commit()

    statuses = service.uninstall_package(package_id, "codex")

    assert statuses[skill_id] != "uninstalled"
    assert arbitrary_dir.exists()
    record = service.conn.execute(
        "SELECT status FROM install_records WHERE skill_id = ?", (skill_id,)
    ).fetchone()
    assert record["status"] == "modified"


def test_uninstall_package_marks_missing_install_record(app_root, sample_skill, tmp_path):
    service = _service(app_root)
    package_id, skill_id = _package_with_sample(service, sample_skill)
    target = tmp_path / "codex-skills"
    target.mkdir()
    installed_path = service.install_package(package_id, "codex", target)[0]
    installed_path.rmdir() if not any(installed_path.iterdir()) else None
    for child in installed_path.iterdir():
        child.unlink()
    installed_path.rmdir()

    statuses = service.uninstall_package(package_id, "codex")

    assert statuses == {skill_id: "missing"}
    record = service.conn.execute(
        "SELECT status FROM install_records WHERE skill_id = ?", (skill_id,)
    ).fetchone()
    assert record["status"] == "missing"
