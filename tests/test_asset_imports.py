from __future__ import annotations

from harness_manager.app_paths import AppPaths
from harness_manager.db import connect, initialize_database
from harness_manager.services import HarnessService


def _service(app_root):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    initialize_database(conn)
    return paths, conn, HarnessService(paths, conn)


def test_import_agents_md_asset(app_root, tmp_path):
    paths, conn, service = _service(app_root)
    source = tmp_path / "AGENTS.md"
    source.write_text("# Rules\n", encoding="utf-8")

    asset = service.import_agents_md_asset(source, "项目规则", "custom")

    assert asset.type == "agents_md"
    assert asset.name == "项目规则"
    assert (paths.root / asset.relative_path).read_text(encoding="utf-8") == "# Rules\n"


def test_import_mcp_asset(app_root, tmp_path):
    paths, conn, service = _service(app_root)
    source = tmp_path / "mcp.json"
    source.write_text('{"mcpServers": {}}', encoding="utf-8")

    asset = service.import_mcp_asset(source, "本地 MCP", "custom")

    assert asset.type == "mcp"
    assert asset.name == "本地 MCP"
    assert (paths.root / asset.relative_path).is_file()


def test_create_mcp_config_asset_writes_json_and_metadata(app_root):
    paths, conn, service = _service(app_root)

    asset = service.create_mcp_config_asset(
        title="fetch",
        display_name="Fetch Server",
        config_json='{"type":"stdio","command":"uvx","args":["mcp-server-fetch"]}',
    )

    assert asset.type == "mcp"
    assert asset.name == "fetch"
    assert asset.source_type == "custom"
    assert '"display_name": "Fetch Server"' in asset.metadata_json
    assert "mcp_kind" not in asset.metadata_json
    assert "enabled_clients" not in asset.metadata_json
    assert (paths.root / asset.relative_path).read_text(encoding="utf-8").startswith("{\n")


def test_create_mcp_config_asset_rejects_invalid_json(app_root):
    paths, conn, service = _service(app_root)

    try:
        service.create_mcp_config_asset(
            title="broken",
            display_name="Broken",
            config_json="{not json}",
        )
    except ValueError as exc:
        assert "MCP JSON 配置无效" in str(exc)
    else:
        raise AssertionError("invalid JSON should fail")


def test_update_mcp_config_asset_rewrites_json_and_metadata(app_root):
    paths, conn, service = _service(app_root)
    asset = service.create_mcp_config_asset(
        title="fetch",
        display_name="Fetch Server",
        config_json='{"type":"stdio","command":"uvx"}',
    )

    updated = service.update_mcp_config_asset(
        asset_id=asset.id,
        title="fetch-v2",
        display_name="Fetch Server V2",
        config_json='{"type":"stdio","command":"node"}',
    )

    assert updated.id == asset.id
    assert updated.name == "fetch-v2"
    assert '"display_name": "Fetch Server V2"' in updated.metadata_json
    assert "enabled_clients" not in updated.metadata_json
    assert '"node"' in (paths.root / updated.relative_path).read_text(encoding="utf-8")
