from __future__ import annotations

import json
import shutil
import uuid
import re
import sqlite3
import tempfile
from pathlib import Path

from harness_manager.app_paths import AppPaths
from harness_manager.asset_paths import asset_dir
from harness_manager.db import transaction
from harness_manager.file_ops import copy_directory, extract_zip, make_zip, safe_remove_directory
from harness_manager.fingerprint import fingerprint_directory
from harness_manager.models import Asset, ClientType, InstallStatus, Package, Skill
from harness_manager.repositories import (
    AssetRepository,
    InstallRepository,
    LogRepository,
    PackageRepository,
    SkillRepository,
)


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

    def import_offline_package(self, archive_path: Path | str) -> str:
        extracted = extract_zip(archive_path)
        try:
            package_name, package_description, skill_entries = (
                self._validated_offline_manifest(extracted)
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

    def _validated_offline_manifest(self, extracted: Path) -> tuple[str, str, list[dict]]:
        manifest_path = extracted / "manifest.json"
        if not manifest_path.is_file():
            raise FileNotFoundError(manifest_path)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if not isinstance(manifest, dict):
            raise ValueError("Offline package manifest must be an object")
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


def _import_mcp_asset(self: HarnessService, source_file: Path | str, name: str, source_type: str | None) -> Asset:
    source_path = Path(source_file)
    return _copy_file_asset(self, source_path, "mcp", name, source_type, source_path.name)


def _normalized_mcp_json(config_json: str) -> str:
    try:
        parsed = json.loads(config_json)
    except json.JSONDecodeError as exc:
        raise ValueError(f"MCP JSON 配置无效: {exc.msg}") from exc
    return json.dumps(parsed, ensure_ascii=False, indent=2)


def _mcp_metadata(display_name: str) -> str:
    return json.dumps(
        {
            "display_name": display_name,
            "config_filename": "mcp.json",
        },
        ensure_ascii=False,
    )


def _create_mcp_config_asset(
    self: HarnessService,
    title: str,
    display_name: str,
    config_json: str,
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
                _mcp_metadata(display_name),
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
            _mcp_metadata(display_name),
        )


HarnessService.import_agents_md_asset = _import_agents_md_asset
HarnessService.import_mcp_asset = _import_mcp_asset
HarnessService.create_mcp_config_asset = _create_mcp_config_asset
HarnessService.update_mcp_config_asset = _update_mcp_config_asset
