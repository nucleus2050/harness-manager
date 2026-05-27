from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from harness_manager.app_paths import AppPaths
from harness_manager.db import connect, initialize_database
from harness_manager.file_ops import make_zip
from harness_manager.fingerprint import fingerprint_directory
from harness_manager.services import HarnessService


def _service(app_root: Path) -> HarnessService:
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    initialize_database(conn)
    return HarnessService(paths, conn)


def _offline_archive(
    tmp_path: Path,
    manifest: dict,
    skill_name: str = "sample-skill",
    skill_body: str = "# Sample Skill\n\nBody\n",
) -> Path:
    staging = tmp_path / "staging"
    staging.mkdir()
    skill_dir = staging / "skills" / skill_name
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(skill_body, encoding="utf-8")
    (staging / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return make_zip(staging, tmp_path / f"{skill_name}.harness.zip")


def test_export_then_import_offline_package_round_trips_sample_skill(
    app_root, sample_skill, tmp_path
):
    source_service = _service(app_root)
    skill = source_service.import_skill(sample_skill, "codex")
    package = source_service.create_package("Daily Tools", "Useful daily workflow", [skill.id])

    archive_path = source_service.export_package(package.id)

    fresh_root = tmp_path / "FreshHarnessManager"
    fresh_root.mkdir()
    fresh_service = _service(fresh_root)
    imported_package_id = fresh_service.import_offline_package(archive_path)

    imported_package = fresh_service.packages.get(imported_package_id)
    imported_skills = fresh_service.packages.list_package_skills(imported_package_id)
    assert imported_package.name == "Daily Tools"
    assert imported_package.description == "Useful daily workflow"
    assert [imported_skill.id for imported_skill in imported_skills] == ["sample-skill"]
    assert (fresh_root / "skills" / "sample-skill" / "SKILL.md").read_text(
        encoding="utf-8"
    ) == "# Sample Skill\n\nBody\n"

    with zipfile.ZipFile(archive_path) as archive:
        manifest = json.loads(archive.read("manifest.json"))
    assert manifest["schema_version"] == 1
    assert manifest["package"]["id"] == package.id
    assert manifest["skills"] == [
        {
            "id": "sample-skill",
            "name": "sample-skill",
            "relative_path": "skills/sample-skill",
            "fingerprint": skill.fingerprint,
        }
    ]


def test_import_offline_package_rejects_manifest_relative_path_escape(tmp_path):
    app_root = tmp_path / "HarnessManager"
    app_root.mkdir()
    service = _service(app_root)
    staging = tmp_path / "staging"
    staging.mkdir()
    (staging / "manifest.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "package": {"id": "pkg", "name": "Bad Package", "description": ""},
                "skills": [
                    {
                        "id": "bad",
                        "name": "bad",
                        "relative_path": "../outside",
                        "fingerprint": "ignored",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    archive_path = make_zip(staging, tmp_path / "bad.harness.zip")

    with pytest.raises(ValueError):
        service.import_offline_package(archive_path)


@pytest.mark.parametrize(
    "manifest",
    [
        {"schema_version": 1, "skills": []},
        {"schema_version": 1, "package": {"id": "pkg", "name": "Bad Package"}},
    ],
)
def test_import_offline_package_rejects_malformed_manifest_missing_required_objects(
    tmp_path, manifest
):
    app_root = tmp_path / "HarnessManager"
    app_root.mkdir()
    service = _service(app_root)
    archive_path = _offline_archive(tmp_path, manifest)

    with pytest.raises(ValueError):
        service.import_offline_package(archive_path)


def test_import_offline_package_rejects_fingerprint_mismatch_without_package(
    tmp_path,
):
    app_root = tmp_path / "HarnessManager"
    app_root.mkdir()
    service = _service(app_root)
    manifest = {
        "schema_version": 1,
        "package": {"id": "pkg", "name": "Tampered Package", "description": ""},
        "skills": [
            {
                "id": "sample-skill",
                "name": "sample-skill",
                "relative_path": "skills/sample-skill",
                "fingerprint": "not-the-real-fingerprint",
            }
        ],
    }
    archive_path = _offline_archive(tmp_path, manifest)

    with pytest.raises(ValueError):
        service.import_offline_package(archive_path)

    assert service.packages.list_packages() == []
    assert service.skills.list_skills() == []
    assert not (app_root / "skills" / "sample-skill").exists()


def test_import_offline_package_rejects_duplicate_package_name_before_importing_skill(
    tmp_path, sample_skill
):
    app_root = tmp_path / "HarnessManager"
    app_root.mkdir()
    service = _service(app_root)
    existing_skill = service.import_skill(sample_skill, "codex")
    service.create_package("Daily Tools", "Existing package", [existing_skill.id])
    manifest = {
        "schema_version": 1,
        "package": {"id": "pkg", "name": "Daily Tools", "description": "Duplicate"},
        "skills": [
            {
                "id": "new-skill",
                "name": "new-skill",
                "relative_path": "skills/new-skill",
                "fingerprint": "",
            }
        ],
    }
    staging = tmp_path / "duplicate-staging"
    staging.mkdir()
    skill_dir = staging / "skills" / "new-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("# New Skill\n\nBody\n", encoding="utf-8")
    manifest["skills"][0]["fingerprint"] = fingerprint_directory(skill_dir)
    (staging / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    archive_path = make_zip(staging, tmp_path / "duplicate.harness.zip")

    with pytest.raises(ValueError):
        service.import_offline_package(archive_path)

    assert [package.name for package in service.packages.list_packages()] == ["Daily Tools"]
    assert [skill.id for skill in service.skills.list_skills()] == [existing_skill.id]
    assert not (app_root / "skills" / "new-skill").exists()


def test_import_offline_package_rolls_back_new_skill_when_package_logging_fails(
    tmp_path, monkeypatch
):
    app_root = tmp_path / "HarnessManager"
    app_root.mkdir()
    service = _service(app_root)
    staging = tmp_path / "rollback-staging"
    staging.mkdir()
    skill_dir = staging / "skills" / "new-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("# New Skill\n\nBody\n", encoding="utf-8")
    manifest = {
        "schema_version": 1,
        "package": {"id": "pkg", "name": "Rollback Package", "description": ""},
        "skills": [
            {
                "id": "new-skill",
                "name": "new-skill",
                "relative_path": "skills/new-skill",
                "fingerprint": fingerprint_directory(skill_dir),
            }
        ],
    }
    (staging / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    archive_path = make_zip(staging, tmp_path / "rollback.harness.zip")
    original_add = service.logs.add

    def fail_package_log(action, *args, **kwargs):
        if action == "import_package":
            raise RuntimeError("package log failed")
        return original_add(action, *args, **kwargs)

    monkeypatch.setattr(service.logs, "add", fail_package_log)

    with pytest.raises(RuntimeError, match="package log failed"):
        service.import_offline_package(archive_path)

    assert service.packages.list_packages() == []
    assert service.skills.list_skills() == []
    assert not (app_root / "skills" / "new-skill").exists()
