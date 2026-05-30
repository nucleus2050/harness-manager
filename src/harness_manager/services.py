from __future__ import annotations

import json
import logging
import shutil
import uuid
import re
import sqlite3
import tempfile
import hashlib
from dataclasses import dataclass
from pathlib import Path

from harness_manager.app_paths import AppPaths
from harness_manager.asset_paths import asset_dir
from harness_manager.db import transaction
from harness_manager.file_ops import copy_directory, extract_zip, make_zip, safe_remove_directory
from harness_manager.fingerprint import fingerprint_directory
from harness_manager.models import Asset, ClientType, InstallStatus, Package, Skill
from harness_manager.repositories import (
    AssetRepository,
    HarnessDeployRepository,
    HarnessRepository,
    InstallRepository,
    LogRepository,
    PackageRepository,
    SkillRepository,
)

logger = logging.getLogger(__name__)

HARNESS_BLOCK_START = "<!-- harness-manager:start:{harness_id}:{asset_id} -->"
HARNESS_BLOCK_END = "<!-- harness-manager:end:{harness_id}:{asset_id} -->"
DeployScope = str


@dataclass(frozen=True)
class DeployLayout:
    root: Path
    skill_root: Path
    agents_file: Path
    mcp_file: Path
    agent_root: Path


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "skill"


def is_skill_directory(path: Path | str) -> bool:
    return (Path(path) / "SKILL.md").is_file()


def skill_description(path: Path | str) -> str:
    skill_md = Path(path) / "SKILL.md"
    if not skill_md.is_file():
        return "暂无描述。"
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            lines = text[3:end].splitlines()
            for index, line in enumerate(lines):
                key, separator, value = line.partition(":")
                if separator and key.strip() == "description":
                    parts = [value.strip().strip("\"'")]
                    for next_line in lines[index + 1 :]:
                        if not next_line.startswith((" ", "\t")):
                            break
                        parts.append(next_line.strip().strip("\"'"))
                    return _compact_text(" ".join(parts)) or "暂无描述。"
    for line in text.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and stripped != "---":
            return _compact_text(stripped)
    return "暂无描述。"


def _compact_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _resolve_under(path: Path, root: Path, description: str) -> Path:
    resolved_path = path.resolve()
    resolved_root = root.resolve()
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError(f"{description} escapes {resolved_root}: {path}") from exc
    return resolved_path


def _is_resolved_under(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def _required_non_empty_string(mapping: dict, key: str, description: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{description}.{key} must be a non-empty string")
    return value


def _optional_string(mapping: dict, key: str, description: str, default: str = "") -> str:
    value = mapping.get(key, default)
    if not isinstance(value, str):
        raise ValueError(f"{description}.{key} must be a string")
    return value


class HarnessService:
    def __init__(self, paths: AppPaths, conn: sqlite3.Connection) -> None:
        self.paths = paths
        self.conn = conn
        self.skills = SkillRepository(conn)
        self.assets = AssetRepository(conn)
        self.harnesses = HarnessRepository(conn)
        self.harness_deploys = HarnessDeployRepository(conn)
        self.packages = PackageRepository(conn)
        self.installs = InstallRepository(conn)
        self.logs = LogRepository(conn)

    def import_skill(self, source_dir: Path | str, source_client: ClientType | None) -> Skill:
        source_path = Path(source_dir)
        if not is_skill_directory(source_path):
            raise ValueError(f"不是有效的 Skill 目录: {source_path}")
        skill: Skill | None = None
        created_new = False
        try:
            with transaction(self.conn):
                skill, created_new = self._import_skill_without_transaction(
                    source_path, source_client
                )
        except Exception:
            if created_new and skill is not None:
                destination = self.paths.skill_path(skill.id)
                if destination.exists():
                    self._remove_owned_directory(destination, self.paths.skills_dir)
            raise
        return skill

    def delete_skill(self, skill_id: str) -> None:
        skill = self.skills.get(skill_id)
        destination = self.paths.skill_path(skill.id)
        with transaction(self.conn):
            self.skills.delete(skill.id)
            self.logs.add(
                "delete_skill",
                f"Deleted skill {skill.id}",
                skill.source_client,
                skill_id=skill.id,
            )
        if destination.exists():
            self._remove_owned_directory(destination, self.paths.skills_dir)

    def delete_harness(self, harness_id: str) -> None:
        harness = self.harnesses.get(harness_id)
        if self.harness_deploys.has_active_for_harness(harness_id):
            logger.error("Refusing to delete deployed harness %s", harness_id)
            raise ValueError("该任务套件仍有已部署内容，请先撤销部署后再删除。")
        with transaction(self.conn):
            self.harnesses.delete(harness_id)
            self.logs.add(
                "delete_harness",
                f"Deleted harness {harness.name}",
                package_id=harness_id,
            )
        logger.info("Deleted harness %s", harness_id)

    def _import_skill_without_transaction(
        self, source_path: Path, source_client: ClientType | None
    ) -> tuple[Skill, bool]:
        fingerprint = fingerprint_directory(source_path)
        existing = self.skills.find_by_fingerprint(fingerprint)
        if existing is not None:
            self.assets.upsert(
                existing.id,
                "skill",
                existing.name,
                source_client,
                existing.relative_path,
                existing.fingerprint,
                "{}",
            )
            self.logs.add(
                "import_skill",
                f"Reused existing skill {existing.id} from matching fingerprint",
                source_client,
                skill_id=existing.id,
            )
            return existing, False

        skill_id = self._unique_skill_id(_slug(source_path.name))
        destination = self.paths.skill_path(skill_id)
        destination_preexisted = destination.exists()
        try:
            copy_directory(source_path, destination)

            relative_path = destination.relative_to(self.paths.root).as_posix()
            skill = Skill(
                id=skill_id,
                name=source_path.name,
                source_client=source_client,
                relative_path=relative_path,
                fingerprint=fingerprint,
            )
            self.skills.upsert_skill(
                skill.id,
                skill.name,
                skill.source_client,
                skill.relative_path,
                skill.fingerprint,
            )
            self.assets.upsert(
                skill.id,
                "skill",
                skill.name,
                skill.source_client,
                skill.relative_path,
                skill.fingerprint,
                "{}",
            )
            self.logs.add(
                "import_skill",
                f"Imported skill {skill.id}",
                source_client,
                skill_id=skill.id,
            )
        except Exception:
            if not destination_preexisted and destination.exists():
                self._remove_owned_directory(destination, self.paths.skills_dir)
            raise
        return skill, True

    def create_package(self, name: str, description: str, skill_ids: list[str]) -> Package:
        with transaction(self.conn):
            package_id = self.packages.create_package(name, description)
            for sort_order, skill_id in enumerate(skill_ids, start=1):
                self.skills.get(skill_id)
                self.packages.add_skill(package_id, skill_id, sort_order)
            self.logs.add(
                "create_package",
                f"Created package {name}",
                package_id=package_id,
            )
        return self.packages.get(package_id)

    def export_package(self, package_id: str) -> Path:
        package = self.packages.get(package_id)
        skills = self.packages.list_package_skills(package_id)
        staging = Path(tempfile.mkdtemp(prefix="harness-manager-export-"))
        try:
            staging_skills = staging / "skills"
            manifest_skills = []
            for skill in skills:
                source = self._validated_managed_skill_source(skill)
                copy_directory(source, staging_skills / skill.id)
                manifest_skills.append(
                    {
                        "id": skill.id,
                        "name": skill.name,
                        "relative_path": f"skills/{skill.id}",
                        "fingerprint": skill.fingerprint,
                    }
                )

            manifest = {
                "schema_version": 1,
                "package": {
                    "id": package.id,
                    "name": package.name,
                    "description": package.description,
                },
                "skills": manifest_skills,
            }
            (staging / "manifest.json").write_text(
                json.dumps(manifest, indent=2), encoding="utf-8"
            )
            archive_path = self.paths.exports_dir / f"{_slug(package.name)}.harness.zip"
            make_zip(staging, archive_path)
            with transaction(self.conn):
                self.logs.add(
                    "export_package",
                    f"Exported package {package_id} to {archive_path}",
                    package_id=package_id,
                )
            return archive_path
        finally:
            self._remove_owned_directory(staging, staging.parent)

    def export_harness(
        self, harness_id: str, export_destination: Path | str | None = None
    ) -> Path:
        harness = self.harnesses.get(harness_id)
        assets = self.harnesses.list_assets(harness_id)
        staging = Path(tempfile.mkdtemp(prefix="harness-manager-export-"))
        try:
            manifest_assets = []
            for asset in assets:
                source = self.paths.root / asset.relative_path
                if asset.type == "skill":
                    source = self._validated_managed_asset_source(asset)
                    export_relative_path = f"assets/skill/{asset.id}"
                    copy_directory(source, staging / export_relative_path)
                else:
                    if not source.is_file():
                        raise FileNotFoundError(source)
                    export_relative_path = f"assets/{asset.type}/{asset.id}/{source.name}"
                    asset_destination = staging / export_relative_path
                    asset_destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, asset_destination)
                manifest_assets.append(
                    {
                        "id": asset.id,
                        "type": asset.type,
                        "name": asset.name,
                        "relative_path": export_relative_path,
                        "fingerprint": asset.fingerprint,
                        "metadata_json": asset.metadata_json,
                    }
                )

            manifest = {
                "schema_version": 2,
                "harness": {
                    "id": harness.id,
                    "name": harness.name,
                    "description": harness.description,
                },
                "assets": manifest_assets,
            }
            (staging / "manifest.json").write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            archive_path = self._harness_export_path(harness.name, export_destination)
            make_zip(staging, archive_path)
            with transaction(self.conn):
                self.logs.add(
                    "export_harness",
                    f"Exported harness {harness_id} to {archive_path}",
                    package_id=harness_id,
                )
            logger.info("Exported harness %s to %s", harness_id, archive_path)
            return archive_path
        except Exception:
            logger.exception("Failed to export harness %s", harness_id)
            raise
        finally:
            self._remove_owned_directory(staging, staging.parent)

    def _harness_export_path(self, harness_name: str, destination: Path | str | None) -> Path:
        archive_name = f"{_slug(harness_name)}.harness.zip"
        if destination is None:
            return self.paths.exports_dir / archive_name
        destination_path = Path(destination)
        if destination_path.suffix.lower() == ".zip":
            return destination_path
        return destination_path / archive_name

    def import_offline_package(self, archive_path: Path | str) -> str:
        extracted = extract_zip(archive_path)
        try:
            manifest = self._read_offline_manifest(extracted)
            if manifest.get("schema_version") == 2:
                return self._import_offline_harness(extracted, manifest)
            package_name, package_description, skill_entries = (
                self._validated_offline_manifest(extracted, manifest)
            )
            if self._package_name_exists(package_name):
                raise ValueError(f"Package already exists: {package_name}")

            imported_skill_ids: list[str] = []
            new_skill_ids: list[str] = []
            try:
                with transaction(self.conn):
                    for entry in skill_entries:
                        relative_path = entry["relative_path"]
                        source = self._validated_offline_skill_source(
                            extracted, relative_path
                        )
                        skill, created_new = self._import_skill_without_transaction(
                            source, None
                        )
                        imported_skill_ids.append(skill.id)
                        if created_new:
                            new_skill_ids.append(skill.id)

                    package_id = self.packages.create_package(
                        package_name, package_description
                    )
                    for sort_order, skill_id in enumerate(imported_skill_ids, start=1):
                        self.packages.add_skill(package_id, skill_id, sort_order)
                    self.logs.add(
                        "import_package",
                        f"Imported offline package {package_name}",
                        package_id=package_id,
                    )
            except Exception:
                for skill_id in reversed(new_skill_ids):
                    destination = self.paths.skill_path(skill_id)
                    if destination.exists():
                        self._remove_owned_directory(destination, self.paths.skills_dir)
                raise
            return package_id
        finally:
            self._remove_owned_directory(extracted, extracted.parent)

    def _import_offline_harness(self, extracted: Path, manifest: dict) -> str:
        harness_name, harness_description, asset_entries = self._validated_offline_harness_manifest(
            extracted, manifest
        )
        if any(harness.name == harness_name for harness in self.harnesses.list_harnesses()):
            raise ValueError(f"Harness already exists: {harness_name}")

        new_skill_ids: list[str] = []
        created_asset_dirs: list[Path] = []
        try:
            with transaction(self.conn):
                harness = self.harnesses.create(harness_name, harness_description)
                for sort_order, entry in enumerate(asset_entries, start=1):
                    asset_type = entry["type"]
                    if asset_type == "skill":
                        source = self._validated_offline_skill_source(
                            extracted, entry["relative_path"]
                        )
                        skill, created_new = self._import_skill_without_transaction(source, None)
                        if created_new:
                            new_skill_ids.append(skill.id)
                        asset_id = skill.id
                    else:
                        source = self._validated_offline_file_asset_source(
                            extracted, entry["relative_path"]
                        )
                        asset = self._import_file_asset_without_transaction(
                            source,
                            asset_type,
                            entry["name"],
                            "offline",
                            source.name,
                            entry.get("metadata_json", "{}"),
                        )
                        created_asset_dirs.append((self.paths.root / asset.relative_path).parent)
                        asset_id = asset.id
                    self.harnesses.add_asset(harness.id, asset_id, asset_type, sort_order)
                self.logs.add(
                    "import_harness",
                    f"Imported offline harness {harness_name}",
                    package_id=harness.id,
                )
            return harness.id
        except Exception:
            for skill_id in reversed(new_skill_ids):
                destination = self.paths.skill_path(skill_id)
                if destination.exists():
                    self._remove_owned_directory(destination, self.paths.skills_dir)
            for directory in reversed(created_asset_dirs):
                if directory.exists():
                    self._remove_owned_directory(directory, self.paths.root)
            raise

    def install_package(
        self,
        package_id: str,
        client_type: ClientType,
        target_path: Path | str,
        overwrite: bool = False,
    ) -> list[Path]:
        target = Path(target_path)
        if not target.is_dir():
            raise NotADirectoryError(target)

        skills = self.packages.list_package_skills(package_id)
        installed_paths: list[Path] = []
        copied_destinations: list[Path] = []
        try:
            with transaction(self.conn):
                for skill in skills:
                    source = self._validated_managed_skill_source(skill)
                    destination = self._validated_install_destination(target, skill.id)
                    destination_preexisted = destination.exists()
                    try:
                        copy_directory(source, destination, overwrite=overwrite)
                    except Exception:
                        if not destination_preexisted and destination.exists():
                            self._remove_owned_directory(destination, target)
                        raise
                    if not destination_preexisted:
                        copied_destinations.append(destination)
                    installed_fingerprint = fingerprint_directory(destination)
                    self.installs.add_installed(
                        package_id,
                        skill.id,
                        client_type,
                        target,
                        destination,
                        installed_fingerprint,
                    )
                    installed_paths.append(destination)
                self.logs.add(
                    "install_package",
                    f"Installed package {package_id} to {target}",
                    client_type,
                    package_id=package_id,
                )
        except Exception:
            for destination in reversed(copied_destinations):
                if destination.exists():
                    self._remove_owned_directory(destination, target)
            raise
        return installed_paths

    def deploy_harness(
        self,
        harness_id: str,
        client_type: ClientType,
        target_path: Path | str,
        scope: DeployScope = "global",
        overwrite: bool = False,
    ) -> list[Path]:
        target = Path(target_path).resolve()
        if not target.is_dir():
            raise NotADirectoryError(target)

        layout = _deploy_layout(client_type, target, scope)
        layout.skill_root.mkdir(parents=True, exist_ok=True)
        self.harnesses.get(harness_id)
        harness_assets = self.harnesses.list_assets(harness_id)
        active_records = self.harness_deploys.list_active(harness_id, client_type, target)
        active_asset_ids = {record["asset_id"] for record in active_records}
        deployed_paths: list[Path] = []
        copied_destinations: list[Path] = []
        logger.info("Deploying harness %s to %s for %s", harness_id, target, client_type)
        try:
            with transaction(self.conn):
                for asset in harness_assets:
                    if asset.id in active_asset_ids:
                        logger.debug("Skipping active deployed asset %s", asset.id)
                        deployed_paths.append(
                            self._harness_asset_deploy_destination(
                                asset, client_type, target, scope
                            )
                        )
                        continue
                    destination = self._harness_asset_deploy_destination(
                        asset, client_type, target, scope
                    )
                    if asset.type != "skill":
                        source = self._validated_managed_asset_source(asset)
                        self._deploy_file_asset_to_client(
                            harness_id, asset, client_type, target, scope, source, destination
                        )
                        self.harness_deploys.add_deployed(
                            harness_id,
                            asset.id,
                            client_type,
                            target,
                            destination,
                            self._harness_deployed_fingerprint(asset, destination),
                        )
                        deployed_paths.append(destination)
                        continue
                    source = self._validated_managed_asset_source(asset)
                    destination_preexisted = destination.exists()
                    if destination_preexisted and not overwrite:
                        source_fingerprint = fingerprint_directory(source)
                        destination_fingerprint = fingerprint_directory(destination)
                        if destination_fingerprint != source_fingerprint:
                            logger.error(
                                "Deploy conflict for harness %s asset %s at %s",
                                harness_id,
                                asset.id,
                                destination,
                            )
                            raise ValueError(
                                f"目标已存在且内容不同，无法部署: {destination}"
                            )
                        logger.info(
                            "Adopting existing identical skill %s at %s",
                            asset.id,
                            destination,
                        )
                        self.harness_deploys.add_deployed(
                            harness_id,
                            asset.id,
                            client_type,
                            target,
                            destination,
                            destination_fingerprint,
                        )
                        deployed_paths.append(destination)
                        continue
                    try:
                        destination.parent.mkdir(parents=True, exist_ok=True)
                        copy_directory(source, destination, overwrite=overwrite)
                    except Exception:
                        if not destination_preexisted and destination.exists():
                            self._remove_owned_directory(destination, target)
                        raise
                    if not destination_preexisted:
                        copied_destinations.append(destination)
                    deployed_fingerprint = fingerprint_directory(destination)
                    self.harness_deploys.add_deployed(
                        harness_id,
                        asset.id,
                        client_type,
                        target,
                        destination,
                        deployed_fingerprint,
                    )
                    deployed_paths.append(destination)
                self.logs.add(
                    "deploy_harness",
                    f"Deployed harness {harness_id} to {target}",
                    client_type,
                    package_id=harness_id,
                )
        except Exception:
            for destination in reversed(copied_destinations):
                if destination.exists():
                    self._remove_owned_directory(destination, target)
            logger.exception("Failed to deploy harness %s to %s", harness_id, target)
            raise
        return deployed_paths

    def _harness_deployed_fingerprint(self, asset: Asset, destination: Path) -> str:
        if asset.type == "agent":
            return _fingerprint_file_content(destination)
        if asset.type == "skill":
            return fingerprint_directory(destination)
        return fingerprint_directory(self._validated_managed_asset_source(asset))

    def harness_deploy_status(
        self,
        harness_id: str,
        client_type: ClientType,
        target_path: Path | str,
        scope: DeployScope = "global",
    ) -> bool:
        self.harnesses.get(harness_id)
        target = Path(target_path).resolve()
        harness_assets = self.harnesses.list_assets(harness_id)
        if not harness_assets:
            return False
        records = self.harness_deploys.list_active(harness_id, client_type, target)
        records_by_asset = {record["asset_id"]: record for record in records}
        if set(records_by_asset) != {asset.id for asset in harness_assets}:
            return False
        for asset in harness_assets:
            record = records_by_asset[asset.id]
            try:
                installed_path = self._validated_harness_undeploy_path(record, asset, scope)
            except ValueError:
                logger.debug("Deploy record for asset %s is invalid", asset.id)
                return False
            if asset.type == "skill":
                if not installed_path.is_dir():
                    return False
                fingerprint = fingerprint_directory(installed_path)
                if fingerprint != record["fingerprint"]:
                    return False
            else:
                if not installed_path.is_file():
                    return False
                if not self._harness_file_asset_matches(record, asset, installed_path):
                    return False
        return True

    def has_active_harness_deploy(
        self,
        harness_id: str,
        client_type: ClientType,
        target_path: Path | str,
    ) -> bool:
        self.harnesses.get(harness_id)
        return self.harness_deploys.is_active(
            harness_id, client_type, Path(target_path).resolve()
        )

    def has_invalid_active_harness_deploy(
        self,
        harness_id: str,
        client_type: ClientType,
        target_path: Path | str,
        scope: DeployScope = "global",
    ) -> bool:
        target = Path(target_path).resolve()
        records = self.harness_deploys.list_active(harness_id, client_type, target)
        assets = {asset.id: asset for asset in self.harnesses.list_assets(harness_id)}
        for record in records:
            try:
                installed_path = self._validated_harness_undeploy_path(
                    record, assets.get(record["asset_id"]), scope
                )
            except ValueError:
                return True
            asset = assets.get(record["asset_id"])
            if asset is None:
                return True
            if asset.type == "skill":
                if not installed_path.is_dir():
                    return True
                fingerprint = fingerprint_directory(installed_path)
                if fingerprint != record["fingerprint"]:
                    return True
            else:
                if not installed_path.is_file():
                    return True
                if not self._harness_file_asset_matches(record, asset, installed_path):
                    return True
        return False

    def undeploy_harness(
        self,
        harness_id: str,
        client_type: ClientType,
        target_path: Path | str,
        scope: DeployScope = "global",
    ) -> dict[str, InstallStatus]:
        target = Path(target_path).resolve()
        records = self.harness_deploys.list_active(harness_id, client_type, target)
        assets = {asset.id: asset for asset in self.harnesses.list_assets(harness_id)}
        statuses: dict[str, InstallStatus] = {}
        logger.info("Undeploying harness %s from %s for %s", harness_id, target, client_type)
        with transaction(self.conn):
            for record in records:
                asset_id = record["asset_id"]
                asset = assets.get(asset_id)
                try:
                    installed_path = self._validated_harness_undeploy_path(record, asset, scope)
                except ValueError:
                    self.harness_deploys.mark_status(record["id"], "modified")
                    status = "modified"
                else:
                    if asset is not None and asset.type != "skill":
                        status = self._undeploy_harness_file_record(
                            record, asset, installed_path, scope
                        )
                    else:
                        cleanup_root = (
                            _deploy_layout(client_type, target, scope).root
                            if asset is not None
                            else target
                        )
                        status = self._undeploy_harness_record(
                            record["id"],
                            installed_path,
                            record["fingerprint"],
                            cleanup_root,
                        )
                statuses[asset_id] = status
            self.logs.add(
                "undeploy_harness",
                f"Undeployed harness {harness_id} from {client_type}",
                client_type,
                package_id=harness_id,
            )
        return statuses

    def uninstall_package(
        self, package_id: str, client_type: ClientType
    ) -> dict[str, InstallStatus]:
        records = self.installs.list_active(package_id, client_type)
        statuses: dict[str, InstallStatus] = {}

        with transaction(self.conn):
            for record in records:
                skill_id = record["skill_id"]
                try:
                    installed_path = self._validated_uninstall_path(record)
                except ValueError:
                    self.installs.mark_status(record["id"], "modified")
                    status = "modified"
                else:
                    status = self._uninstall_record(
                        record["id"], installed_path, record["fingerprint"]
                    )
                statuses[skill_id] = status
            self.logs.add(
                "uninstall_package",
                f"Uninstalled package {package_id} from {client_type}",
                client_type,
                package_id=package_id,
            )
        return statuses

    def _unique_skill_id(self, base_id: str) -> str:
        candidate = base_id
        suffix = 2
        while True:
            self.paths.skill_path(candidate)
            if not (self.paths.skills_dir / candidate).exists() and not self._skill_exists(candidate):
                return candidate
            candidate = f"{base_id}-{suffix}"
            suffix += 1

    def _skill_exists(self, skill_id: str) -> bool:
        try:
            self.skills.get(skill_id)
        except KeyError:
            return False
        return True

    def _package_name_exists(self, package_name: str) -> bool:
        row = self.conn.execute(
            "SELECT 1 FROM packages WHERE name = ? LIMIT 1", (package_name,)
        ).fetchone()
        return row is not None

    def _read_offline_manifest(self, extracted: Path) -> dict:
        manifest_path = extracted / "manifest.json"
        if not manifest_path.is_file():
            raise FileNotFoundError(manifest_path)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if not isinstance(manifest, dict):
            raise ValueError("Offline package manifest must be an object")
        return manifest

    def _validated_offline_manifest(
        self, extracted: Path, manifest: dict | None = None
    ) -> tuple[str, str, list[dict]]:
        manifest = manifest or self._read_offline_manifest(extracted)
        if manifest.get("schema_version") != 1:
            raise ValueError("Unsupported offline package schema_version")

        package_info = manifest.get("package")
        if not isinstance(package_info, dict):
            raise ValueError("Offline package manifest.package must be an object")
        _required_non_empty_string(package_info, "id", "manifest.package")
        package_name = _required_non_empty_string(
            package_info, "name", "manifest.package"
        )
        package_description = _optional_string(
            package_info, "description", "manifest.package"
        )

        skill_entries = manifest.get("skills")
        if not isinstance(skill_entries, list):
            raise ValueError("Offline package manifest.skills must be a list")
        for index, entry in enumerate(skill_entries):
            if not isinstance(entry, dict):
                raise ValueError(f"manifest.skills[{index}] must be an object")
            _required_non_empty_string(entry, "id", f"manifest.skills[{index}]")
            _required_non_empty_string(entry, "name", f"manifest.skills[{index}]")
            relative_path = _required_non_empty_string(
                entry, "relative_path", f"manifest.skills[{index}]"
            )
            expected_fingerprint = _required_non_empty_string(
                entry, "fingerprint", f"manifest.skills[{index}]"
            )
            source = self._validated_offline_skill_source(extracted, relative_path)
            actual_fingerprint = fingerprint_directory(source)
            if actual_fingerprint != expected_fingerprint:
                raise ValueError(
                    f"Offline skill {entry['id']!r} fingerprint mismatch"
                )
        return package_name, package_description, skill_entries

    def _validated_offline_harness_manifest(
        self, extracted: Path, manifest: dict
    ) -> tuple[str, str, list[dict]]:
        if manifest.get("schema_version") != 2:
            raise ValueError("Unsupported offline harness schema_version")
        harness_info = manifest.get("harness")
        if not isinstance(harness_info, dict):
            raise ValueError("Offline harness manifest.harness must be an object")
        _required_non_empty_string(harness_info, "id", "manifest.harness")
        harness_name = _required_non_empty_string(harness_info, "name", "manifest.harness")
        harness_description = _optional_string(
            harness_info, "description", "manifest.harness"
        )

        asset_entries = manifest.get("assets")
        if not isinstance(asset_entries, list):
            raise ValueError("Offline harness manifest.assets must be a list")
        for index, entry in enumerate(asset_entries):
            if not isinstance(entry, dict):
                raise ValueError(f"manifest.assets[{index}] must be an object")
            _required_non_empty_string(entry, "id", f"manifest.assets[{index}]")
            asset_type = _required_non_empty_string(
                entry, "type", f"manifest.assets[{index}]"
            )
            if asset_type not in {"skill", "agents_md", "mcp", "agent"}:
                raise ValueError(f"Unsupported offline asset type: {asset_type}")
            _required_non_empty_string(entry, "name", f"manifest.assets[{index}]")
            relative_path = _required_non_empty_string(
                entry, "relative_path", f"manifest.assets[{index}]"
            )
            expected_fingerprint = _required_non_empty_string(
                entry, "fingerprint", f"manifest.assets[{index}]"
            )
            if asset_type == "skill":
                source = self._validated_offline_skill_source(extracted, relative_path)
            else:
                source = self._validated_offline_file_asset_source(extracted, relative_path)
                source = source.parent
            actual_fingerprint = fingerprint_directory(source)
            if actual_fingerprint != expected_fingerprint:
                raise ValueError(f"Offline asset {entry['id']!r} fingerprint mismatch")
        return harness_name, harness_description, asset_entries

    def _validated_managed_skill_source(self, skill: Skill) -> Path:
        source = self.paths.skill_path(skill.id)
        source_resolved = _resolve_under(source, self.paths.skills_dir, "Skill source")
        persisted_source = self.paths.root / skill.relative_path
        persisted_resolved = _resolve_under(
            persisted_source,
            self.paths.skills_dir,
            "Persisted skill relative path",
        )
        if persisted_resolved != source_resolved:
            raise ValueError(
                f"Persisted skill path for {skill.id!r} does not match managed source"
            )
        if not source.is_dir():
            raise NotADirectoryError(source)
        return source

    def _validated_managed_asset_source(self, asset: Asset) -> Path:
        source = self.paths.root / asset.relative_path
        _resolve_under(source, self.paths.root, "Managed asset source")
        if source.is_file():
            return source.parent
        if not source.is_dir():
            raise NotADirectoryError(source)
        return source

    def _validated_offline_skill_source(
        self, extracted_root: Path, relative_path: str
    ) -> Path:
        candidate = Path(relative_path)
        if candidate.is_absolute():
            raise ValueError(
                f"Offline skill relative_path must be relative: {relative_path!r}"
            )
        source = _resolve_under(
            extracted_root / candidate, extracted_root, "Offline skill path"
        )
        if not source.is_dir():
            raise NotADirectoryError(source)
        return source

    def _validated_offline_file_asset_source(
        self, extracted_root: Path, relative_path: str
    ) -> Path:
        candidate = Path(relative_path)
        if candidate.is_absolute():
            raise ValueError(
                f"Offline asset relative_path must be relative: {relative_path!r}"
            )
        source = _resolve_under(
            extracted_root / candidate, extracted_root, "Offline asset path"
        )
        if not source.is_file():
            raise FileNotFoundError(source)
        return source

    def _import_file_asset_without_transaction(
        self,
        source_file: Path,
        asset_type: str,
        name: str,
        source_type: str | None,
        destination_name: str,
        metadata_json: str,
    ) -> Asset:
        if not source_file.is_file():
            raise FileNotFoundError(source_file)
        asset_id = uuid.uuid4().hex
        destination_dir = asset_dir(self.paths, asset_type, asset_id)
        destination_dir.mkdir(parents=True, exist_ok=True)
        destination = destination_dir / destination_name
        try:
            shutil.copy2(source_file, destination)
            fingerprint = fingerprint_directory(destination_dir)
            asset = self.assets.upsert(
                asset_id,
                asset_type,
                name,
                source_type,
                destination.relative_to(self.paths.root).as_posix(),
                fingerprint,
                metadata_json,
            )
            self.logs.add("import_asset", f"Imported {asset_type} asset {name}")
            return asset
        except Exception:
            safe_remove_directory(destination_dir)
            raise

    def _validated_install_destination(self, target: Path, skill_id: str) -> Path:
        self.paths.skill_path(skill_id)
        destination = target / skill_id
        _resolve_under(destination, target, "Install destination")
        return destination

    def _validated_uninstall_path(self, record: sqlite3.Row) -> Path:
        skill_id = record["skill_id"]
        self.paths.skill_path(skill_id)
        target = Path(record["target_path"])
        installed_path = Path(record["installed_path"])
        expected_path = target / skill_id
        if installed_path.resolve() != expected_path.resolve():
            raise ValueError(
                f"Install record path for {skill_id!r} does not match expected target path"
            )
        if not _is_resolved_under(installed_path, target):
            raise ValueError(f"Install record path for {skill_id!r} escapes target")
        return expected_path

    def _validated_harness_undeploy_path(
        self,
        record: sqlite3.Row,
        asset: Asset | None = None,
        scope: DeployScope = "global",
    ) -> Path:
        asset_id = record["asset_id"]
        if asset is None or asset.type == "skill":
            self.paths.skill_path(asset_id)
        target = Path(record["target_path"])
        installed_path = Path(record["installed_path"])
        expected_path = (
            self._harness_asset_deploy_destination(
                asset, record["client_type"], target, scope
            )
            if asset is not None
            else target / asset_id
        )
        if installed_path.resolve() != expected_path.resolve():
            raise ValueError(
                f"Deploy record path for {asset_id!r} does not match expected target path"
            )
        owner_root = (
            _deploy_layout(record["client_type"], target, scope).root
            if asset is not None
            else target
        )
        if not _is_resolved_under(installed_path, owner_root):
            raise ValueError(f"Deploy record path for {asset_id!r} escapes target")
        return expected_path

    def _harness_asset_deploy_destination(
        self,
        asset: Asset,
        client_type: ClientType | str,
        target: Path,
        scope: DeployScope = "global",
    ) -> Path:
        layout = _deploy_layout(client_type, target, scope)
        if asset.type == "skill":
            destination = layout.skill_root / asset.id
            _resolve_under(destination, layout.skill_root, "Install destination")
            return destination
        if asset.type == "agents_md":
            return layout.agents_file
        if asset.type == "mcp":
            return layout.mcp_file
        if asset.type == "agent":
            destination = layout.agent_root / _agent_deploy_filename(asset)
            _resolve_under(destination, layout.agent_root, "Agent deploy destination")
            return destination
        raise ValueError(f"Unsupported asset type: {asset.type}")

    def _deploy_file_asset_to_client(
        self,
        harness_id: str,
        asset: Asset,
        client_type: ClientType,
        target: Path,
        scope: DeployScope,
        source: Path,
        destination: Path,
    ) -> None:
        layout = _deploy_layout(client_type, target, scope)
        _resolve_under(destination, layout.root, "Deploy destination")
        destination.parent.mkdir(parents=True, exist_ok=True)
        if asset.type == "agents_md":
            payload = source / "AGENTS.md"
            if not payload.is_file():
                raise FileNotFoundError(payload)
            _upsert_marked_text_block(destination, harness_id, asset.id, payload.read_text(encoding="utf-8"))
            if scope == "project" and client_type == "opencode":
                _append_json_list_item(layout.mcp_file, "instructions", "AGENTS.md")
            return
        if asset.type == "mcp":
            payload = source / "mcp.json"
            if not payload.is_file():
                json_files = sorted(source.glob("*.json"))
                if not json_files:
                    raise FileNotFoundError(payload)
                payload = json_files[0]
            mcp_config = json.loads(payload.read_text(encoding="utf-8"))
            if client_type == "codex":
                _upsert_codex_mcp(
                    destination, asset.name, _mcp_config_for_client(client_type, mcp_config)
                )
            elif client_type == "claude_code":
                _upsert_json_object(
                    destination,
                    ["mcpServers", asset.name],
                    _mcp_config_for_client(client_type, mcp_config),
                )
            else:
                _upsert_json_object(
                    destination,
                    ["mcp", asset.name],
                    _mcp_config_for_client(client_type, mcp_config),
                )
            return
        if asset.type == "agent":
            payload = source / _agent_entry_filename(asset)
            if not payload.is_file():
                candidates = sorted(
                    child for child in source.iterdir() if child.is_file()
                )
                if not candidates:
                    raise FileNotFoundError(payload)
                payload = candidates[0]
            shutil.copy2(payload, destination)
            return
        raise ValueError(f"Unsupported file asset type: {asset.type}")

    def _remove_owned_directory(self, directory: Path, owner_root: Path) -> None:
        _resolve_under(directory, owner_root, "Directory cleanup target")
        safe_remove_directory(directory)

    def _uninstall_record(
        self, record_id: str, installed_path: Path, installed_fingerprint: str
    ) -> InstallStatus:
        if not installed_path.exists():
            self.installs.mark_status(record_id, "missing")
            return "missing"
        if not installed_path.is_dir():
            self.installs.mark_status(record_id, "modified")
            return "modified"
        if fingerprint_directory(installed_path) != installed_fingerprint:
            self.installs.mark_status(record_id, "modified")
            return "modified"

        safe_remove_directory(installed_path)
        self.installs.mark_status(record_id, "uninstalled")
        return "uninstalled"

    def _undeploy_harness_record(
        self,
        record_id: str,
        installed_path: Path,
        installed_fingerprint: str,
        cleanup_root: Path | None = None,
    ) -> InstallStatus:
        if not installed_path.exists():
            self.harness_deploys.mark_status(record_id, "missing")
            return "missing"
        if not installed_path.is_dir():
            self.harness_deploys.mark_status(record_id, "modified")
            return "modified"
        if fingerprint_directory(installed_path) != installed_fingerprint:
            self.harness_deploys.mark_status(record_id, "modified")
            return "modified"

        safe_remove_directory(installed_path)
        if cleanup_root is not None:
            _prune_empty_parents(installed_path.parent, cleanup_root)
        self.harness_deploys.mark_status(record_id, "uninstalled")
        return "uninstalled"

    def _undeploy_harness_file_record(
        self,
        record: sqlite3.Row,
        asset: Asset,
        installed_path: Path,
        scope: DeployScope = "global",
    ) -> InstallStatus:
        record_id = record["id"]
        if not installed_path.exists():
            self.harness_deploys.mark_status(record_id, "missing")
            return "missing"
        if not installed_path.is_file():
            self.harness_deploys.mark_status(record_id, "modified")
            return "modified"
        file_status = self._harness_file_asset_status(record, asset, installed_path)
        if file_status == "missing":
            self.harness_deploys.mark_status(record_id, "missing")
            return "missing"
        if file_status == "modified":
            self.harness_deploys.mark_status(record_id, "modified")
            return "modified"
        if asset.type == "agents_md":
            _remove_marked_text_block(installed_path, record["harness_id"], asset.id)
            if scope == "project" and record["client_type"] == "opencode":
                layout = _deploy_layout(record["client_type"], Path(record["target_path"]), scope)
                _remove_json_list_item(layout.mcp_file, "instructions", "AGENTS.md")
        elif asset.type == "mcp":
            client_type = record["client_type"]
            if client_type == "codex":
                _remove_codex_mcp(installed_path, asset.name)
            elif client_type == "claude_code":
                _remove_json_object(installed_path, ["mcpServers", asset.name])
            else:
                _remove_json_object(installed_path, ["mcp", asset.name])
        elif asset.type == "agent":
            installed_path.unlink(missing_ok=True)
        else:
            self.harness_deploys.mark_status(record_id, "modified")
            return "modified"
        layout = _deploy_layout(record["client_type"], Path(record["target_path"]), scope)
        _prune_empty_parents(installed_path.parent, layout.root)
        self.harness_deploys.mark_status(record_id, "uninstalled")
        return "uninstalled"

    def _harness_file_asset_matches(
        self, record: sqlite3.Row, asset: Asset, installed_path: Path
    ) -> bool:
        return self._harness_file_asset_status(record, asset, installed_path) == "installed"

    def _harness_file_asset_status(
        self, record: sqlite3.Row, asset: Asset, installed_path: Path
    ) -> InstallStatus:
        source = self._validated_managed_asset_source(asset)
        if asset.type == "agents_md":
            payload = source / "AGENTS.md"
            if not payload.is_file():
                return "modified"
            block = _extract_marked_text_block(
                installed_path, record["harness_id"], asset.id
            )
            if block is None:
                return "missing"
            payload_text = payload.read_text(encoding="utf-8").strip()
            return "installed" if block.strip() == payload_text else "modified"
        if asset.type == "mcp":
            try:
                expected = _mcp_payload_config(source)
            except (FileNotFoundError, json.JSONDecodeError):
                return "modified"
            client_type = record["client_type"]
            expected = _mcp_config_for_client(client_type, expected)
            try:
                if client_type == "codex":
                    current = _extract_codex_mcp(installed_path, asset.name)
                    if current is None:
                        return "missing"
                    expected_block = _codex_mcp_toml_block(asset.name, expected).strip()
                    return "installed" if current.strip() == expected_block else "modified"
                keys = (
                    ["mcpServers", asset.name]
                    if client_type == "claude_code"
                    else ["mcp", asset.name]
                )
                current_json = _get_json_object(installed_path, keys)
            except (json.JSONDecodeError, ValueError):
                return "modified"
            if current_json is None:
                return "missing"
            return "installed" if current_json == expected else "modified"
        if asset.type == "agent":
            payload = source / _agent_entry_filename(asset)
            if not payload.is_file():
                return "modified"
            if not installed_path.is_file():
                return "missing"
            return (
                "installed"
                if _fingerprint_file_content(installed_path) == _fingerprint_file_content(payload)
                else "modified"
            )
        return "modified"



def _client_config_root(client_type: ClientType | str, skill_target: Path) -> Path:
    return Path(skill_target).resolve().parent


def _prune_empty_parents(start: Path, stop_root: Path) -> None:
    current = start.resolve()
    root = stop_root.resolve()
    while current != root and _is_resolved_under(current, root):
        try:
            current.rmdir()
        except OSError:
            break
        current = current.parent


def _deploy_layout(
    client_type: ClientType | str, target: Path | str, scope: DeployScope = "global"
) -> DeployLayout:
    resolved = Path(target).resolve()
    if scope == "project":
        project_root = resolved
        if client_type == "codex":
            return DeployLayout(
                root=project_root,
                skill_root=project_root / ".agents" / "skills",
                agents_file=project_root / "AGENTS.md",
                mcp_file=project_root / ".codex" / "config.toml",
                agent_root=project_root / ".codex" / "agents",
            )
        if client_type == "claude_code":
            return DeployLayout(
                root=project_root,
                skill_root=project_root / ".claude" / "skills",
                agents_file=project_root / "CLAUDE.md",
                mcp_file=project_root / ".mcp.json",
                agent_root=project_root / ".claude" / "agents",
            )
        return DeployLayout(
            root=project_root,
            skill_root=project_root / ".opencode" / "skills",
            agents_file=project_root / "AGENTS.md",
            mcp_file=project_root / "opencode.json",
            agent_root=project_root / ".opencode" / "agents",
        )
    config_root = _client_config_root(client_type, resolved)
    if client_type == "claude_code":
        agents_file = config_root / "CLAUDE.md"
        mcp_file = config_root.parent / ".claude.json"
        agent_root = config_root / "agents"
    elif client_type == "codex":
        agents_file = config_root / "AGENTS.md"
        mcp_file = config_root / "config.toml"
        agent_root = config_root / "agents"
    else:
        agents_file = config_root / "AGENTS.md"
        mcp_file = config_root / "opencode.json"
        agent_root = config_root / "agents"
    return DeployLayout(
        root=config_root.parent,
        skill_root=resolved,
        agents_file=agents_file,
        mcp_file=mcp_file,
        agent_root=agent_root,
    )


def _fingerprint_file(path: Path | str) -> str:
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(file_path)
    file_bytes = file_path.read_bytes()
    digest = hashlib.sha256()
    digest.update(file_path.name.encode("utf-8"))
    digest.update(b"\0")
    digest.update(len(file_bytes).to_bytes(8, "big"))
    digest.update(file_bytes)
    return digest.hexdigest()


def _fingerprint_file_content(path: Path | str) -> str:
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(file_path)
    digest = hashlib.sha256()
    digest.update(file_path.read_bytes())
    return digest.hexdigest()


def _marked_block(harness_id: str, asset_id: str, body: str) -> str:
    start = HARNESS_BLOCK_START.format(harness_id=harness_id, asset_id=asset_id)
    end = HARNESS_BLOCK_END.format(harness_id=harness_id, asset_id=asset_id)
    return f"{start}\n{body.strip()}\n{end}\n"


def _upsert_marked_text_block(destination: Path, harness_id: str, asset_id: str, body: str) -> None:
    existing = destination.read_text(encoding="utf-8") if destination.exists() else ""
    start = HARNESS_BLOCK_START.format(harness_id=harness_id, asset_id=asset_id)
    end = HARNESS_BLOCK_END.format(harness_id=harness_id, asset_id=asset_id)
    pattern = re.compile(
        rf"{re.escape(start)}\n.*?\n{re.escape(end)}\n?",
        re.DOTALL,
    )
    replacement = _marked_block(harness_id, asset_id, body)
    if pattern.search(existing):
        updated = pattern.sub(replacement, existing)
    else:
        separator = "\n" if existing and not existing.endswith("\n") else ""
        updated = f"{existing}{separator}\n{replacement}" if existing else replacement
    destination.write_text(updated, encoding="utf-8")


def _remove_marked_text_block(destination: Path, harness_id: str, asset_id: str) -> None:
    existing = destination.read_text(encoding="utf-8") if destination.exists() else ""
    start = HARNESS_BLOCK_START.format(harness_id=harness_id, asset_id=asset_id)
    end = HARNESS_BLOCK_END.format(harness_id=harness_id, asset_id=asset_id)
    pattern = re.compile(
        rf"\n?{re.escape(start)}\n.*?\n{re.escape(end)}\n?",
        re.DOTALL,
    )
    updated = pattern.sub("\n", existing).strip()
    if not updated:
        destination.unlink(missing_ok=True)
        return
    destination.write_text(updated + "\n", encoding="utf-8")


def _extract_marked_text_block(destination: Path, harness_id: str, asset_id: str) -> str | None:
    existing = destination.read_text(encoding="utf-8") if destination.exists() else ""
    start = HARNESS_BLOCK_START.format(harness_id=harness_id, asset_id=asset_id)
    end = HARNESS_BLOCK_END.format(harness_id=harness_id, asset_id=asset_id)
    pattern = re.compile(
        rf"{re.escape(start)}\n(.*?)\n{re.escape(end)}",
        re.DOTALL,
    )
    match = pattern.search(existing)
    return match.group(1) if match else None


def _upsert_json_object(destination: Path, keys: list[str], value: dict) -> None:
    data = {}
    if destination.exists() and destination.read_text(encoding="utf-8").strip():
        data = json.loads(destination.read_text(encoding="utf-8"))
    cursor = data
    for key in keys[:-1]:
        next_value = cursor.setdefault(key, {})
        if not isinstance(next_value, dict):
            raise ValueError(f"JSON config key is not an object: {key}")
        cursor = next_value
    cursor[keys[-1]] = value
    destination.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _get_json_object(destination: Path, keys: list[str]) -> object | None:
    if not destination.exists() or not destination.read_text(encoding="utf-8").strip():
        return None
    data = json.loads(destination.read_text(encoding="utf-8"))
    cursor: object = data
    for key in keys:
        if not isinstance(cursor, dict) or key not in cursor:
            return None
        cursor = cursor[key]
    return cursor


def _append_json_list_item(destination: Path, key: str, value: str) -> None:
    data = {}
    if destination.exists() and destination.read_text(encoding="utf-8").strip():
        data = json.loads(destination.read_text(encoding="utf-8"))
    current = data.setdefault(key, [])
    if not isinstance(current, list):
        raise ValueError(f"JSON config key is not a list: {key}")
    if value not in current:
        current.append(value)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _remove_json_list_item(destination: Path, key: str, value: str) -> None:
    if not destination.exists() or not destination.read_text(encoding="utf-8").strip():
        return
    data = json.loads(destination.read_text(encoding="utf-8"))
    current = data.get(key)
    if isinstance(current, list) and value in current:
        data[key] = [item for item in current if item != value]
        if not data[key]:
            data.pop(key, None)
    if not data:
        destination.unlink(missing_ok=True)
        return
    destination.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _remove_json_object(destination: Path, keys: list[str]) -> None:
    if not destination.exists() or not destination.read_text(encoding="utf-8").strip():
        destination.unlink(missing_ok=True)
        return
    data = json.loads(destination.read_text(encoding="utf-8"))
    cursor = data
    parents: list[tuple[dict, str]] = []
    for key in keys[:-1]:
        next_value = cursor.get(key)
        if not isinstance(next_value, dict):
            destination.write_text(
                json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            return
        parents.append((cursor, key))
        cursor = next_value
    cursor.pop(keys[-1], None)
    for parent, key in reversed(parents):
        child = parent.get(key)
        if isinstance(child, dict) and not child:
            parent.pop(key, None)
    if not data:
        destination.unlink(missing_ok=True)
        return
    destination.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _upsert_codex_mcp(destination: Path, name: str, value: dict) -> None:
    existing = destination.read_text(encoding="utf-8") if destination.exists() else ""
    header = f"[mcp_servers.{name}]"
    pattern = re.compile(
        rf"(?ms)^\[mcp_servers\.{re.escape(name)}\]\n.*?(?=^\[|\Z)"
    )
    block = _codex_mcp_toml_block(name, value)
    if pattern.search(existing):
        updated = pattern.sub(block, existing)
    else:
        separator = "\n" if existing and not existing.endswith("\n") else ""
        updated = f"{existing}{separator}\n{block}" if existing else block
    destination.write_text(updated, encoding="utf-8")


def _extract_codex_mcp(destination: Path, name: str) -> str | None:
    existing = destination.read_text(encoding="utf-8") if destination.exists() else ""
    pattern = re.compile(
        rf"(?ms)^\[mcp_servers\.{re.escape(name)}\]\n.*?(?=^\[|\Z)"
    )
    match = pattern.search(existing)
    return match.group(0) if match else None


def _remove_codex_mcp(destination: Path, name: str) -> None:
    existing = destination.read_text(encoding="utf-8") if destination.exists() else ""
    pattern = re.compile(
        rf"(?ms)^\[mcp_servers\.{re.escape(name)}\]\n.*?(?=^\[|\Z)"
    )
    updated = pattern.sub("", existing).strip()
    if not updated:
        destination.unlink(missing_ok=True)
        return
    destination.write_text(updated + "\n", encoding="utf-8")


def _mcp_payload_config(source: Path) -> dict:
    payload = source / "mcp.json"
    if not payload.is_file():
        json_files = sorted(source.glob("*.json"))
        if not json_files:
            raise FileNotFoundError(payload)
        payload = json_files[0]
    data = json.loads(payload.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("MCP config payload must be a JSON object")
    return data


def _mcp_config_for_client(client_type: ClientType | str, value: dict) -> dict:
    if client_type == "opencode":
        return _opencode_mcp_config(value)
    if client_type == "codex":
        return _codex_mcp_config(value)
    return dict(value)


def _codex_mcp_config(value: dict) -> dict:
    config = dict(value)
    if config.get("type") in {"stdio", "local"}:
        config.pop("type", None)
    if "environment" in config and "env" not in config:
        config["env"] = config.pop("environment")
    return config


def _opencode_mcp_config(value: dict) -> dict:
    config = dict(value)
    args = config.pop("args", [])
    if "env" in config and "environment" not in config:
        config["environment"] = config.pop("env")
    command = config.get("command")
    if isinstance(command, str):
        config["command"] = [command, *_list_value(args)]
    elif isinstance(command, list) and args:
        config["command"] = [*command, *_list_value(args)]
    if config.get("type") in {None, "stdio", "local"}:
        config["type"] = "local"
    return config


def _list_value(value: object) -> list:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _codex_mcp_toml_block(name: str, value: dict) -> str:
    lines = [f"[mcp_servers.{name}]"]
    for key, item in value.items():
        lines.append(f"{key} = {_toml_value(item)}")
    return "\n".join(lines) + "\n"


def _toml_value(value: object) -> str:
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        return "[" + ", ".join(_toml_value(item) for item in value) + "]"
    if isinstance(value, dict):
        return "{" + ", ".join(f"{key} = {_toml_value(item)}" for key, item in value.items()) + "}"
    if value is None:
        return '""'
    return json.dumps(str(value), ensure_ascii=False)


def _copy_file_asset(service: HarnessService, source_file: Path, asset_type: str, name: str, source_type: str | None, destination_name: str):
    if not source_file.is_file():
        raise FileNotFoundError(source_file)
    asset_id = uuid.uuid4().hex
    destination_dir = asset_dir(service.paths, asset_type, asset_id)
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / destination_name
    try:
        shutil.copy2(source_file, destination)
        fingerprint = fingerprint_directory(destination_dir)
        with transaction(service.conn):
            asset = service.assets.upsert(
                asset_id,
                asset_type,
                name,
                source_type,
                destination.relative_to(service.paths.root).as_posix(),
                fingerprint,
                "{}",
            )
            service.logs.add("import_asset", f"Imported {asset_type} asset {name}")
        return asset
    except Exception:
        safe_remove_directory(destination_dir)
        raise


def _import_agents_md_asset(self: HarnessService, source_file: Path | str, name: str, source_type: str | None) -> Asset:
    return _copy_file_asset(self, Path(source_file), "agents_md", name, source_type, "AGENTS.md")


def _create_agents_md_asset(
    self: HarnessService,
    name: str,
    description: str,
    content: str,
) -> Asset:
    name = name.strip()
    content = content.strip()
    if not name:
        raise ValueError("AGENTS.md 名称不能为空。")
    if not content:
        raise ValueError("AGENTS.md 内容不能为空。")
    asset_id = uuid.uuid4().hex
    destination_dir = asset_dir(self.paths, "agents_md", asset_id)
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / "AGENTS.md"
    metadata_json = json.dumps({"description": description.strip()}, ensure_ascii=False)
    try:
        destination.write_text(content + "\n", encoding="utf-8")
        fingerprint = fingerprint_directory(destination_dir)
        with transaction(self.conn):
            return self.assets.upsert(
                asset_id,
                "agents_md",
                name,
                "custom",
                destination.relative_to(self.paths.root).as_posix(),
                fingerprint,
                metadata_json,
            )
    except Exception:
        safe_remove_directory(destination_dir)
        raise


def _import_mcp_asset(self: HarnessService, source_file: Path | str, name: str, source_type: str | None) -> Asset:
    source_path = Path(source_file)
    return _copy_file_asset(self, source_path, "mcp", name, source_type, source_path.name)


def _normalized_mcp_json(config_json: str) -> str:
    try:
        parsed = json.loads(config_json)
    except json.JSONDecodeError as exc:
        raise ValueError(f"MCP JSON 配置无效: {exc.msg}") from exc
    return json.dumps(parsed, ensure_ascii=False, indent=2)


def _mcp_metadata(display_name: str, description: str = "") -> str:
    return json.dumps(
        {
            "display_name": display_name,
            "description": description.strip(),
            "config_filename": "mcp.json",
        },
        ensure_ascii=False,
    )


def _agent_file_extension(agent_format: str) -> str:
    if agent_format == "codex_toml":
        return ".toml"
    if agent_format in {"claude_md", "opencode_md"}:
        return ".md"
    if agent_format == "opencode_json":
        return ".json"
    raise ValueError(f"不支持的 Agent 格式: {agent_format}")


def _safe_agent_name(agent_name: str) -> str:
    sanitized = _slug(agent_name.strip())
    if not sanitized:
        raise ValueError("Agent 名称不能为空。")
    return sanitized


def _agent_metadata(
    client_type: str,
    agent_format: str,
    agent_name: str,
    description: str,
) -> str:
    safe_name = _safe_agent_name(agent_name)
    extension = _agent_file_extension(agent_format)
    return json.dumps(
        {
            "client_type": client_type,
            "agent_format": agent_format,
            "agent_name": safe_name,
            "description": description.strip(),
            "entry_filename": f"agent{extension}",
            "deploy_filename": f"{safe_name}{extension}",
        },
        ensure_ascii=False,
    )


def _agent_metadata_dict(metadata_json: str) -> dict:
    try:
        metadata = json.loads(metadata_json or "{}")
    except json.JSONDecodeError:
        metadata = {}
    return metadata if isinstance(metadata, dict) else {}


def _agent_entry_filename(asset: Asset) -> str:
    metadata = _agent_metadata_dict(asset.metadata_json)
    filename = metadata.get("entry_filename")
    return filename if isinstance(filename, str) and filename else "agent.md"


def _agent_deploy_filename(asset: Asset) -> str:
    metadata = _agent_metadata_dict(asset.metadata_json)
    filename = metadata.get("deploy_filename")
    if isinstance(filename, str) and filename:
        return Path(filename).name
    agent_name = metadata.get("agent_name")
    agent_format = metadata.get("agent_format")
    if isinstance(agent_name, str) and isinstance(agent_format, str):
        return f"{_safe_agent_name(agent_name)}{_agent_file_extension(agent_format)}"
    return f"{_safe_agent_name(asset.name)}.md"


def _import_agent_asset(
    self: HarnessService,
    source_file: Path | str,
    name: str,
    source_type: str | None,
    client_type: str,
    agent_format: str,
    agent_name: str,
    description: str = "",
) -> Asset:
    source_path = Path(source_file)
    metadata_json = _agent_metadata(client_type, agent_format, agent_name, description)
    entry_filename = str(_agent_metadata_dict(metadata_json)["entry_filename"])
    if not source_path.is_file():
        raise FileNotFoundError(source_path)
    asset_id = uuid.uuid4().hex
    destination_dir = asset_dir(self.paths, "agent", asset_id)
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / entry_filename
    try:
        shutil.copy2(source_path, destination)
        fingerprint = fingerprint_directory(destination_dir)
        with transaction(self.conn):
            asset = self.assets.upsert(
                asset_id,
                "agent",
                name.strip(),
                source_type,
                destination.relative_to(self.paths.root).as_posix(),
                fingerprint,
                metadata_json,
            )
            self.logs.add("import_asset", f"Imported agent asset {name}")
        return asset
    except Exception:
        safe_remove_directory(destination_dir)
        raise


def _create_agent_asset(
    self: HarnessService,
    name: str,
    client_type: str,
    agent_format: str,
    agent_name: str,
    description: str,
    content: str,
) -> Asset:
    name = name.strip()
    content = content.strip()
    if not name:
        raise ValueError("Agent 标题不能为空。")
    if not content:
        raise ValueError("Agent 内容不能为空。")
    metadata_json = _agent_metadata(client_type, agent_format, agent_name, description)
    entry_filename = str(_agent_metadata_dict(metadata_json)["entry_filename"])
    asset_id = uuid.uuid4().hex
    destination_dir = asset_dir(self.paths, "agent", asset_id)
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / entry_filename
    try:
        destination.write_text(content + "\n", encoding="utf-8")
        fingerprint = fingerprint_directory(destination_dir)
        with transaction(self.conn):
            return self.assets.upsert(
                asset_id,
                "agent",
                name,
                "custom",
                destination.relative_to(self.paths.root).as_posix(),
                fingerprint,
                metadata_json,
            )
    except Exception:
        safe_remove_directory(destination_dir)
        raise


def _create_mcp_config_asset(
    self: HarnessService,
    title: str,
    display_name: str,
    config_json: str,
    description: str = "",
) -> Asset:
    title = title.strip()
    if not title:
        raise ValueError("MCP 标题不能为空。")
    if self.assets.find_by_type_and_name("mcp", title) is not None:
        raise ValueError(f"MCP 标题已存在: {title}")

    normalized_json = _normalized_mcp_json(config_json)
    asset_id = uuid.uuid4().hex
    destination_dir = asset_dir(self.paths, "mcp", asset_id)
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / "mcp.json"
    try:
        destination.write_text(normalized_json, encoding="utf-8")
        fingerprint = fingerprint_directory(destination_dir)
        with transaction(self.conn):
            return self.assets.upsert(
                asset_id,
                "mcp",
                title,
                "custom",
                destination.relative_to(self.paths.root).as_posix(),
                fingerprint,
                _mcp_metadata(display_name, description),
            )
    except Exception:
        safe_remove_directory(destination_dir)
        raise


def _update_mcp_config_asset(
    self: HarnessService,
    asset_id: str,
    title: str,
    display_name: str,
    config_json: str,
    description: str = "",
) -> Asset:
    title = title.strip()
    if not title:
        raise ValueError("MCP 标题不能为空。")
    existing = self.assets.get(asset_id)
    duplicate = self.assets.find_by_type_and_name("mcp", title)
    if duplicate is not None and duplicate.id != asset_id:
        raise ValueError(f"MCP 标题已存在: {title}")

    normalized_json = _normalized_mcp_json(config_json)
    destination = self.paths.root / existing.relative_path
    destination_dir = destination.parent
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination.write_text(normalized_json, encoding="utf-8")
    fingerprint = fingerprint_directory(destination_dir)
    with transaction(self.conn):
        return self.assets.upsert(
            asset_id,
            "mcp",
            title,
            "custom",
            destination.relative_to(self.paths.root).as_posix(),
            fingerprint,
            _mcp_metadata(display_name, description),
        )


HarnessService.import_agents_md_asset = _import_agents_md_asset
HarnessService.create_agents_md_asset = _create_agents_md_asset
HarnessService.import_mcp_asset = _import_mcp_asset
HarnessService.create_mcp_config_asset = _create_mcp_config_asset
HarnessService.update_mcp_config_asset = _update_mcp_config_asset
HarnessService.import_agent_asset = _import_agent_asset
HarnessService.create_agent_asset = _create_agent_asset
