from __future__ import annotations

from skillpkg.app_paths import AppPaths
from skillpkg.db import connect, initialize_database
from skillpkg.services import SkillPkgService


def _service(app_root):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    initialize_database(conn)
    return paths, conn, SkillPkgService(paths, conn)


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
