from __future__ import annotations

from skillpkg.app_paths import AppPaths
from skillpkg.db import connect, initialize_database
from skillpkg.repositories import AssetRepository, HarnessRepository


def test_create_harness_and_asset_membership(app_root):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    initialize_database(conn)

    harnesses = HarnessRepository(conn)
    assets = AssetRepository(conn)
    harness = harnesses.create("代码审查", "审查任务工具包")
    asset = assets.upsert(
        asset_id="asset-1",
        asset_type="agents_md",
        name="规则",
        source_type="custom",
        relative_path="assets/agents/asset-1/AGENTS.md",
        fingerprint="abc",
        metadata_json="{}",
    )
    harnesses.add_asset(harness.id, asset.id, asset.type, 1)

    listed_assets = harnesses.list_assets(harness.id)
    assert listed_assets == [asset]


def test_harness_tables_are_additive_to_existing_package_tables(app_root):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    initialize_database(conn)

    table_names = {
        row["name"]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
    }

    assert "packages" in table_names
    assert "skills" in table_names
    assert "harnesses" in table_names
    assert "assets" in table_names
    assert "harness_assets" in table_names
