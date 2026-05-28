from __future__ import annotations

from harness_manager.app_paths import AppPaths
from harness_manager.db import connect
from harness_manager.gui.controllers import MainController


def test_controller_creates_empty_harness(app_root):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    controller = MainController(app_root, conn)

    harness = controller.create_harness("代码审查", "审查任务工具包")

    assert harness.name == "代码审查"
    assert controller.list_harnesses()[0].id == harness.id


def test_controller_updates_harness_description(app_root):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    controller = MainController(app_root, conn)
    harness = controller.create_harness("代码审查", "初始描述")

    updated = controller.update_harness(harness.id, "代码审查", "更新后的描述")

    assert updated.description == "更新后的描述"
    assert controller.list_harnesses()[0].description == "更新后的描述"


def test_controller_creates_mcp_config_asset(app_root):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    controller = MainController(app_root, conn)

    asset = controller.create_mcp_config_asset(
        title="fetch",
        display_name="Fetch Server",
        config_json='{"type":"stdio","command":"uvx"}',
    )

    assert asset.type == "mcp"
    assert controller.list_assets_by_type("mcp")[0].id == asset.id


def test_controller_lists_installed_harnesses_by_application(app_root, tmp_path, sample_skill):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    controller = MainController(app_root, conn)
    harness = controller.create_harness("代码审查", "审查任务工具包")
    skill = controller.import_skill_directory(sample_skill, "codex")
    controller.add_asset_to_harness(harness.id, skill.id, "skill")
    target = tmp_path / "codex-skills"

    controller.deploy_harness_by_id(harness.id, "codex", target)

    applications = controller.list_application_components()
    codex = next(item for item in applications if item["client_type"] == "codex")
    assert codex["component_count"] == 1
    assert codex["components"][0]["component_name"] == "代码审查"
    assert codex["components"][0]["asset_count"] == 1
    assert "path_status" not in codex
    assert "configured_path" not in codex
    assert "status" not in codex["components"][0]
    assert "target_path" not in codex["components"][0]
    assert "asset_name" not in codex["components"][0]
    assert "asset_type" not in codex["components"][0]
