from __future__ import annotations

import sqlite3
import logging
from pathlib import Path

from harness_manager.app_paths import AppPaths
from harness_manager.client_detection import detect_default_paths
from harness_manager.db import initialize_database, transaction
from harness_manager.models import ClientConfig, ClientType, InstallStatus, Package, Skill
from harness_manager.repositories import (
    ClientRepository,
    ImportSourceRepository,
    AssetRepository,
    HarnessRepository,
    PackageRepository,
    SkillRepository,
)
from harness_manager.services import HarnessService, is_skill_directory
from harness_manager.settings import SettingsService

logger = logging.getLogger(__name__)


class MainController:
    def __init__(self, app_root: Path | str, conn: sqlite3.Connection) -> None:
        self.paths = AppPaths(Path(app_root))
        self.paths.ensure()
        self.conn = conn
        initialize_database(conn)
        self.clients = ClientRepository(conn)
        self.import_sources = ImportSourceRepository(conn)
        self.harnesses = HarnessRepository(conn)
        self.assets = AssetRepository(conn)
        self.skills = SkillRepository(conn)
        self.packages = PackageRepository(conn)
        self.service = HarnessService(self.paths, conn)
        self.settings = SettingsService(self.paths)
        self.refresh_default_paths()

    def refresh_default_paths(self) -> None:
        detected = detect_default_paths()
        with transaction(self.conn):
            for client_type, default_path in detected.items():
                self.clients.set_default_path(client_type, default_path)


    def create_harness(self, name: str, description: str = ""):
        with transaction(self.conn):
            return self.harnesses.create(name, description)

    def update_harness(self, harness_id: str, name: str, description: str = ""):
        with transaction(self.conn):
            return self.harnesses.update(harness_id, name, description)

    def delete_harness(self, harness_id: str) -> None:
        self.service.delete_harness(harness_id)

    def list_harnesses(self):
        return self.harnesses.list_harnesses()

    def list_harnesses_without_asset(self, asset_id: str):
        return self.harnesses.list_harnesses_without_asset(asset_id)

    def list_harnesses_with_asset(self, asset_id: str):
        return self.harnesses.list_harnesses_with_asset(asset_id)

    def list_assets_by_type(self, asset_type: str):
        return self.assets.list_by_type(asset_type)

    def get_settings(self):
        return self.settings.load()

    def save_language(self, language: str):
        return self.settings.save_language(language)

    def save_theme(self, theme: str):
        return self.settings.save_theme(theme)

    def export_full_config(self, destination: Path | str | None = None):
        return self.settings.export_full_config(destination)

    def import_full_config(self, archive_path: Path | str):
        return self.settings.import_full_config(archive_path)

    def list_clients(self) -> list[ClientConfig]:
        return self.clients.list_clients()

    def list_packages(self) -> list[Package]:
        return self.packages.list_packages()

    def list_skills(self, package_row: int | None = None) -> list[Skill]:
        if package_row is None:
            return self.skills.list_skills()
        package = self._package_by_row(package_row)
        return self.packages.list_package_skills(package.id)


    def import_agents_md_asset(self, source_file: Path | str, name: str):
        return self.service.import_agents_md_asset(Path(source_file), name, "custom")

    def create_agents_md_asset(self, name: str, description: str, content: str):
        return self.service.create_agents_md_asset(name, description, content)

    def import_mcp_asset(self, source_file: Path | str, name: str):
        return self.service.import_mcp_asset(Path(source_file), name, "custom")

    def create_mcp_config_asset(self, title: str, display_name: str, config_json: str):
        return self.service.create_mcp_config_asset(
            title=title,
            display_name=display_name,
            config_json=config_json,
        )

    def update_mcp_config_asset(
        self, asset_id: str, title: str, display_name: str, config_json: str
    ):
        return self.service.update_mcp_config_asset(
            asset_id=asset_id,
            title=title,
            display_name=display_name,
            config_json=config_json,
        )

    def add_asset_to_harness(self, harness_id: str, asset_id: str, asset_type: str) -> None:
        current = self.harnesses.list_assets(harness_id)
        if any(asset.id == asset_id for asset in current):
            raise ValueError("该组件已在任务套件中。")
        with transaction(self.conn):
            self.harnesses.add_asset(harness_id, asset_id, asset_type, len(current) + 1)

    def remove_asset_from_harness(self, harness_id: str, asset_id: str) -> None:
        with transaction(self.conn):
            self.harnesses.remove_asset(harness_id, asset_id)

    def list_harness_assets(self, harness_id: str):
        return self.harnesses.list_assets(harness_id)

    def list_harness_assets_by_type(self, harness_id: str, asset_type: str):
        return self.harnesses.list_assets_by_type(harness_id, asset_type)

    def import_skill_directory(
        self, source_dir: Path | str, source_client: ClientType | None = None
    ) -> Skill:
        return self.service.import_skill(source_dir, source_client)

    def import_skill_library(
        self, source_dir: Path | str, source_client: ClientType | None = None
    ) -> list[Skill]:
        source = Path(source_dir)
        if not source.is_dir():
            raise NotADirectoryError(source)
        imported: list[Skill] = []
        for child in sorted(path for path in source.iterdir() if path.is_dir()):
            if not is_skill_directory(child):
                continue
            imported.append(self.service.import_skill(child, source_client))
        return imported

    def import_from_client_source(self, client_type: ClientType) -> list[Skill]:
        target = self._client_target(client_type)
        return self.import_skill_library(target, client_type)

    def set_client_custom_path(self, client_type: ClientType, path: Path | str) -> None:
        with transaction(self.conn):
            self.clients.set_custom_path(client_type, Path(path))

    def add_custom_import_source(self, name: str, path: Path | str) -> str:
        with transaction(self.conn):
            return self.import_sources.add(name, Path(path))

    def list_custom_import_sources(self) -> list[dict[str, object]]:
        return [
            {"id": row["id"], "name": row["name"], "path": Path(row["path"])}
            for row in self.import_sources.list_sources()
        ]

    def import_from_custom_source(self, source_id: str) -> list[Skill]:
        source = self.import_sources.get(source_id)
        return self.import_skill_library(Path(source["path"]), f"custom:{source_id}")

    def remove_custom_import_source(self, source_id: str) -> None:
        with transaction(self.conn):
            self.import_sources.disable(source_id)

    def delete_skill_asset(self, skill_id: str) -> None:
        self.service.delete_skill(skill_id)

    def create_package(self, name: str, description: str = "") -> Package:
        return self.service.create_package(name, description, [])

    def create_package_from_all_skills(self, name: str, description: str = "") -> Package:
        skills = self.skills.list_skills()
        return self.service.create_package(name, description, [skill.id for skill in skills])

    def export_package_by_row(self, package_row: int) -> Path:
        return self.service.export_package(self._package_by_row(package_row).id)

    def export_harness_by_row(
        self, harness_row: int, destination: Path | str | None = None
    ) -> Path:
        harnesses = self.harnesses.list_harnesses()
        if harness_row < 0 or harness_row >= len(harnesses):
            raise IndexError("任务套件选择超出范围。")
        return self.service.export_harness(harnesses[harness_row].id, destination)

    def import_offline_package(self, archive_path: Path | str) -> str:
        return self.service.import_offline_package(archive_path)

    def install_package_by_row(
        self,
        package_row: int,
        client_type: ClientType,
        target_path: Path | str | None = None,
        overwrite: bool = False,
    ) -> list[Path]:
        package = self._package_by_row(package_row)
        target = Path(target_path) if target_path is not None else self._client_target(client_type)
        return self.service.install_package(package.id, client_type, target, overwrite=overwrite)

    def deploy_harness_by_id(
        self,
        harness_id: str,
        client_type: ClientType,
        target_path: Path | str | None = None,
        overwrite: bool = False,
    ) -> list[Path]:
        target = (Path(target_path) if target_path is not None else self._client_target(client_type)).resolve()
        logger.info("Deploy harness %s to %s for %s", harness_id, target, client_type)
        target.mkdir(parents=True, exist_ok=True)
        return self.service.deploy_harness(harness_id, client_type, target, overwrite=overwrite)

    def harness_deploy_status(
        self,
        harness_id: str,
        client_type: ClientType,
        target_path: Path | str | None = None,
    ) -> bool:
        target = (Path(target_path) if target_path is not None else self._client_target(client_type)).resolve()
        return self.service.harness_deploy_status(harness_id, client_type, target)

    def toggle_harness_deploy(
        self,
        harness_id: str,
        client_type: ClientType,
        target_path: Path | str | None = None,
    ) -> tuple[str, list[Path] | dict[str, InstallStatus]]:
        target = (Path(target_path) if target_path is not None else self._client_target(client_type)).resolve()
        is_deployed = self.service.harness_deploy_status(harness_id, client_type, target)
        has_invalid_records = self.service.has_invalid_active_harness_deploy(
            harness_id, client_type, target
        )
        if is_deployed or has_invalid_records:
            logger.info("Toggle undeploy harness %s from %s for %s", harness_id, target, client_type)
            return "undeployed", self.service.undeploy_harness(harness_id, client_type, target)
        logger.info("Toggle deploy harness %s to %s for %s", harness_id, target, client_type)
        target.mkdir(parents=True, exist_ok=True)
        return "deployed", self.service.deploy_harness(harness_id, client_type, target)

    def uninstall_package_by_row(
        self, package_row: int, client_type: ClientType
    ) -> dict[str, InstallStatus]:
        package = self._package_by_row(package_row)
        return self.service.uninstall_package(package.id, client_type)

    def _package_by_row(self, package_row: int) -> Package:
        packages = self.packages.list_packages()
        if package_row < 0 or package_row >= len(packages):
            raise IndexError("Package selection is out of range.")
        return packages[package_row]

    def _client_target(self, client_type: ClientType) -> Path:
        for client in self.clients.list_clients():
            if client.type == client_type:
                if client.effective_path is None:
                    raise ValueError(f"No target path configured for {client.name}.")
                return client.effective_path
        raise ValueError(f"Unknown client type: {client_type}")
