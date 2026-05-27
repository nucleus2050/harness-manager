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
