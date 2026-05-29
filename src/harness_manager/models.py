from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

ClientType = Literal["codex", "claude_code", "opencode"]
InstallStatus = Literal["installed", "uninstalled", "missing", "modified", "failed"]


@dataclass(frozen=True)
class ClientConfig:
    id: int
    type: ClientType
    name: str
    default_path: Path | None
    custom_path: Path | None
    enabled: bool

    @property
    def effective_path(self) -> Path | None:
        return self.custom_path or self.default_path


@dataclass(frozen=True)
class Skill:
    id: str
    name: str
    source_client: ClientType | None
    relative_path: str
    fingerprint: str


@dataclass(frozen=True)
class Package:
    id: str
    name: str
    description: str


@dataclass(frozen=True)
class InstallRecord:
    id: str
    package_id: str
    skill_id: str
    client_type: ClientType
    target_path: Path
    installed_path: Path
    fingerprint: str
    status: InstallStatus

AssetType = Literal["agents_md", "mcp", "skill"]


@dataclass(frozen=True)
class Asset:
    id: str
    type: AssetType
    name: str
    source_type: str | None
    relative_path: str
    fingerprint: str
    metadata_json: str


@dataclass(frozen=True)
class Harness:
    id: str
    name: str
    description: str


@dataclass(frozen=True)
class Project:
    id: str
    name: str
    path: Path
    description: str


@dataclass(frozen=True)
class HarnessAsset:
    harness_id: str
    asset_id: str
    asset_type: AssetType
    sort_order: int
