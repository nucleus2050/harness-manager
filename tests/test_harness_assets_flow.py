from __future__ import annotations

from skillpkg.app_paths import AppPaths
from skillpkg.db import connect
from skillpkg.gui.controllers import MainController


def test_controller_adds_asset_to_harness(app_root, tmp_path):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    controller = MainController(app_root, conn)
    harness = controller.create_harness("代码审查", "")
    source = tmp_path / "AGENTS.md"
    source.write_text("# Rules\n", encoding="utf-8")
    asset = controller.import_agents_md_asset(source, "规则")

    controller.add_asset_to_harness(harness.id, asset.id, asset.type)

    assets = controller.list_harness_assets(harness.id)
    assert [item.id for item in assets] == [asset.id]


def test_controller_lists_harness_assets_by_type(app_root, tmp_path, sample_skill):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    controller = MainController(app_root, conn)
    harness = controller.create_harness("前端任务", "")

    agents_file = tmp_path / "AGENTS.md"
    agents_file.write_text("# Frontend Rules\n", encoding="utf-8")
    agents_asset = controller.import_agents_md_asset(agents_file, "前端规则")
    skill_asset = controller.import_skill_directory(sample_skill, "codex")

    controller.add_asset_to_harness(harness.id, agents_asset.id, agents_asset.type)
    controller.add_asset_to_harness(harness.id, skill_asset.id, "skill")

    assert [asset.id for asset in controller.list_harness_assets_by_type(harness.id, "agents_md")] == [
        agents_asset.id
    ]
    assert [asset.id for asset in controller.list_harness_assets_by_type(harness.id, "skill")] == [
        skill_asset.id
    ]
