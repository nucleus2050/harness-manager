from __future__ import annotations

from harness_manager.app_paths import AppPaths
from harness_manager.db import connect
from harness_manager.gui.controllers import MainController


def _skill_dir(root, name):
    skill = root / name
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(f"# {name}\n", encoding="utf-8")
    return skill


def test_controller_imports_all_skills_from_client_default_path(app_root, tmp_path):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    controller = MainController(app_root, conn)
    source = tmp_path / "codex-skills"
    _skill_dir(source, "a")
    _skill_dir(source, "b")
    controller.clients.set_custom_path("codex", source)
    conn.commit()

    imported = controller.import_from_client_source("codex")

    assert [skill.name for skill in imported] == ["a", "b"]
    assert [skill.source_client for skill in imported] == ["codex", "codex"]


def test_controller_adds_custom_import_source_and_imports(app_root, tmp_path):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    controller = MainController(app_root, conn)
    source = tmp_path / "my-skills"
    _skill_dir(source, "custom-a")

    source_id = controller.add_custom_import_source("我的技能库", source)
    imported = controller.import_from_custom_source(source_id)

    assert [skill.name for skill in imported] == ["custom-a"]
    assert imported[0].source_client == f"custom:{source_id}"
    assert controller.list_custom_import_sources()[0]["name"] == "我的技能库"


def test_controller_skips_non_skill_directories(app_root, tmp_path):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    controller = MainController(app_root, conn)
    source = tmp_path / "mixed"
    _skill_dir(source, "valid")
    (source / "notes").mkdir()
    (source / "notes" / "README.md").write_text("not a skill", encoding="utf-8")

    imported = controller.import_skill_library(source, "codex")

    assert [skill.name for skill in imported] == ["valid"]


def test_controller_rejects_direct_import_of_non_skill_directory(app_root, tmp_path):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    controller = MainController(app_root, conn)
    source = tmp_path / "not-skill"
    source.mkdir()

    try:
        controller.import_skill_directory(source, "codex")
    except ValueError as exc:
        assert "不是有效的 Skill 目录" in str(exc)
    else:
        raise AssertionError("non-skill directory should fail")


def test_controller_removes_only_custom_source(app_root, tmp_path):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    controller = MainController(app_root, conn)
    source = tmp_path / "custom"
    _skill_dir(source, "custom-a")
    source_id = controller.add_custom_import_source("我的技能库", source)
    imported = controller.import_from_custom_source(source_id)

    controller.remove_custom_import_source(source_id)

    assert controller.list_custom_import_sources() == []
    assert [skill.id for skill in controller.list_skills()] == [imported[0].id]
    assert (paths.skills_dir / imported[0].id).exists()
