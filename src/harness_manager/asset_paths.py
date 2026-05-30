from __future__ import annotations

from pathlib import Path

from harness_manager.app_paths import AppPaths


def asset_dir(paths: AppPaths, asset_type: str, asset_id: str) -> Path:
    if asset_type == "agents_md":
        return paths.root / "assets" / "agents" / asset_id
    if asset_type == "mcp":
        return paths.root / "assets" / "mcp" / asset_id
    if asset_type == "skill":
        return paths.root / "assets" / "skills" / asset_id
    if asset_type == "agent":
        return paths.root / "assets" / "agent_configs" / asset_id
    raise ValueError(f"Unsupported asset type: {asset_type}")
