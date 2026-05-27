from __future__ import annotations

from pathlib import Path

from harness_manager.app_paths import AppPaths
from harness_manager.db import connect, initialize_database
from harness_manager.fingerprint import fingerprint_directory
from harness_manager.repositories import PackageRepository
from harness_manager.services import HarnessService, _slug
from harness_manager.services import skill_description


def _service(app_root: Path) -> HarnessService:
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    initialize_database(conn)
    return HarnessService(paths, conn)


def test_slug_normalizes_to_safe_lowercase_id():
    assert _slug("My Fancy Skill!") == "my-fancy-skill"


def test_import_skill_copies_sample_skill_to_managed_library(app_root, sample_skill):
    service = _service(app_root)

    skill = service.import_skill(sample_skill, "codex")

    managed_path = app_root / "skills" / "sample-skill"
    assert skill.id == "sample-skill"
    assert skill.name == "sample-skill"
    assert skill.source_client == "codex"
    assert skill.relative_path == "skills/sample-skill"
    assert managed_path.is_dir()
    assert (managed_path / "SKILL.md").read_text(encoding="utf-8") == "# Sample Skill\n\nBody\n"
    assert skill.fingerprint == fingerprint_directory(sample_skill)


def test_import_skill_reuses_existing_skill_with_same_fingerprint(app_root, sample_skill, tmp_path):
    service = _service(app_root)
    first = service.import_skill(sample_skill, "codex")
    duplicate = tmp_path / "renamed-copy"
    duplicate.mkdir()
    (duplicate / "SKILL.md").write_text("# Sample Skill\n\nBody\n", encoding="utf-8")

    second = service.import_skill(duplicate, "claude_code")

    assert second == first
    assert not (app_root / "skills" / "renamed-copy").exists()


def test_create_package_with_imported_skill(app_root, sample_skill):
    service = _service(app_root)
    skill = service.import_skill(sample_skill, "codex")

    package = service.create_package("Daily Tools", "Useful daily workflow", [skill.id])

    assert package.name == "Daily Tools"
    assert package.description == "Useful daily workflow"
    package_skills = PackageRepository(service.conn).list_package_skills(package.id)
    assert [package_skill.id for package_skill in package_skills] == [skill.id]
    log_rows = service.conn.execute(
        "SELECT action, package_id, skill_id FROM operation_logs ORDER BY created_at"
    ).fetchall()
    assert ("import_skill", None, skill.id) in [tuple(row) for row in log_rows]
    assert ("create_package", package.id, None) in [tuple(row) for row in log_rows]


def test_skill_description_reads_frontmatter_description(tmp_path):
    skill = tmp_path / "described-skill"
    skill.mkdir()
    (skill / "SKILL.md").write_text(
        "---\ndescription: 用于长文总结\n---\n# Skill\n\nBody\n",
        encoding="utf-8",
    )

    assert skill_description(skill) == "用于长文总结"
