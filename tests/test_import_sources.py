from __future__ import annotations

from skillpkg.app_paths import AppPaths
from skillpkg.db import connect
from skillpkg.gui.controllers import MainController


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
    assert controller.list_custom_import_sources()[0]["name"] == "我的技能库"
