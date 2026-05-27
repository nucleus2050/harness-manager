from __future__ import annotations

import sqlite3
import uuid
from pathlib import Path

from skillpkg.models import Asset, ClientConfig, Harness, Package, Skill


def _path_or_none(value: str | None) -> Path | None:
    return Path(value) if value else None


def _skill_from_row(row: sqlite3.Row) -> Skill:
    return Skill(
        id=row["id"],
        name=row["name"],
        source_client=row["source_client"],
        relative_path=row["relative_path"],
        fingerprint=row["fingerprint"],
    )


def _package_from_row(row: sqlite3.Row) -> Package:
    return Package(id=row["id"], name=row["name"], description=row["description"])


class ClientRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def list_clients(self) -> list[ClientConfig]:
        rows = self.conn.execute(
            """
            SELECT id, type, name, default_path, custom_path, enabled
            FROM clients
            ORDER BY id
            """
        ).fetchall()
        return [
            ClientConfig(
                id=row["id"],
                type=row["type"],
                name=row["name"],
                default_path=_path_or_none(row["default_path"]),
                custom_path=_path_or_none(row["custom_path"]),
                enabled=bool(row["enabled"]),
            )
            for row in rows
        ]

    def set_default_path(self, client_type: str, path: Path | None) -> None:
        self.conn.execute(
            """
            UPDATE clients
            SET default_path = ?, updated_at = CURRENT_TIMESTAMP
            WHERE type = ?
            """,
            (str(path) if path else None, client_type),
        )

    def set_custom_path(self, client_type: str, path: Path | None) -> None:
        self.conn.execute(
            """
            UPDATE clients
            SET custom_path = ?, updated_at = CURRENT_TIMESTAMP
            WHERE type = ?
            """,
            (str(path) if path else None, client_type),
        )


class SkillRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def upsert_skill(
        self,
        skill_id: str,
        name: str,
        source_client: str | None,
        relative_path: str,
        fingerprint: str,
    ) -> None:
        self.conn.execute(
            """
            INSERT INTO skills(id, name, source_client, relative_path, fingerprint)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
              name = excluded.name,
              source_client = excluded.source_client,
              relative_path = excluded.relative_path,
              fingerprint = excluded.fingerprint,
              updated_at = CURRENT_TIMESTAMP
            """,
            (skill_id, name, source_client, relative_path, fingerprint),
        )

    def find_by_fingerprint(self, fingerprint: str) -> Skill | None:
        row = self.conn.execute(
            """
            SELECT id, name, source_client, relative_path, fingerprint
            FROM skills
            WHERE fingerprint = ?
            """,
            (fingerprint,),
        ).fetchone()
        return _skill_from_row(row) if row else None

    def get(self, skill_id: str) -> Skill:
        row = self.conn.execute(
            """
            SELECT id, name, source_client, relative_path, fingerprint
            FROM skills
            WHERE id = ?
            """,
            (skill_id,),
        ).fetchone()
        if row is None:
            raise KeyError(skill_id)
        return _skill_from_row(row)

    def list_skills(self) -> list[Skill]:
        rows = self.conn.execute(
            """
            SELECT id, name, source_client, relative_path, fingerprint
            FROM skills
            ORDER BY name
            """
        ).fetchall()
        return [_skill_from_row(row) for row in rows]


class PackageRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def create_package(self, name: str, description: str) -> str:
        package_id = uuid.uuid4().hex
        self.conn.execute(
            "INSERT INTO packages(id, name, description) VALUES (?, ?, ?)",
            (package_id, name, description),
        )
        return package_id

    def get(self, package_id: str) -> Package:
        row = self.conn.execute(
            "SELECT id, name, description FROM packages WHERE id = ?",
            (package_id,),
        ).fetchone()
        if row is None:
            raise KeyError(package_id)
        return _package_from_row(row)

    def list_packages(self) -> list[Package]:
        rows = self.conn.execute(
            "SELECT id, name, description FROM packages ORDER BY name"
        ).fetchall()
        return [_package_from_row(row) for row in rows]

    def add_skill(self, package_id: str, skill_id: str, sort_order: int) -> None:
        self.conn.execute(
            """
            INSERT INTO package_skills(package_id, skill_id, sort_order)
            VALUES (?, ?, ?)
            ON CONFLICT(package_id, skill_id) DO UPDATE SET
              sort_order = excluded.sort_order
            """,
            (package_id, skill_id, sort_order),
        )

    def remove_skill(self, package_id: str, skill_id: str) -> None:
        self.conn.execute(
            "DELETE FROM package_skills WHERE package_id = ? AND skill_id = ?",
            (package_id, skill_id),
        )

    def list_package_skills(self, package_id: str) -> list[Skill]:
        rows = self.conn.execute(
            """
            SELECT s.id, s.name, s.source_client, s.relative_path, s.fingerprint
            FROM package_skills ps
            JOIN skills s ON s.id = ps.skill_id
            WHERE ps.package_id = ?
            ORDER BY ps.sort_order, s.name
            """,
            (package_id,),
        ).fetchall()
        return [_skill_from_row(row) for row in rows]


class InstallRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def add_installed(
        self,
        package_id: str,
        skill_id: str,
        client_type: str,
        target_path: Path,
        installed_path: Path,
        fingerprint: str,
    ) -> str:
        record_id = uuid.uuid4().hex
        self.conn.execute(
            """
            INSERT INTO install_records(
              id, package_id, skill_id, client_type, target_path,
              installed_path, fingerprint, status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, 'installed')
            """,
            (
                record_id,
                package_id,
                skill_id,
                client_type,
                str(target_path),
                str(installed_path),
                fingerprint,
            ),
        )
        return record_id

    def list_active(self, package_id: str, client_type: str) -> list[sqlite3.Row]:
        return self.conn.execute(
            """
            SELECT id, package_id, skill_id, client_type, target_path,
                   installed_path, fingerprint, status
            FROM install_records
            WHERE package_id = ? AND client_type = ? AND status = 'installed'
            ORDER BY installed_at
            """,
            (package_id, client_type),
        ).fetchall()

    def mark_status(self, record_id: str, status: str) -> None:
        uninstalled_at = "CURRENT_TIMESTAMP" if status == "uninstalled" else "uninstalled_at"
        self.conn.execute(
            f"""
            UPDATE install_records
            SET status = ?, uninstalled_at = {uninstalled_at}
            WHERE id = ?
            """,
            (status, record_id),
        )


class LogRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def add(
        self,
        action: str,
        message: str,
        client_type: str | None = None,
        package_id: str | None = None,
        skill_id: str | None = None,
    ) -> None:
        self.conn.execute(
            """
            INSERT INTO operation_logs(id, action, client_type, package_id, skill_id, message)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (uuid.uuid4().hex, action, client_type, package_id, skill_id, message),
        )


class ImportSourceRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def add(self, name: str, path: Path) -> str:
        source_id = uuid.uuid4().hex
        self.conn.execute(
            """
            INSERT INTO import_sources(id, name, path)
            VALUES (?, ?, ?)
            """,
            (source_id, name, str(path)),
        )
        return source_id

    def list_sources(self) -> list[sqlite3.Row]:
        return self.conn.execute(
            """
            SELECT id, name, path, enabled
            FROM import_sources
            WHERE enabled = 1
            ORDER BY created_at, name
            """
        ).fetchall()

    def get(self, source_id: str) -> sqlite3.Row:
        row = self.conn.execute(
            """
            SELECT id, name, path, enabled
            FROM import_sources
            WHERE id = ? AND enabled = 1
            """,
            (source_id,),
        ).fetchone()
        if row is None:
            raise KeyError(source_id)
        return row



def _asset_from_row(row: sqlite3.Row) -> Asset:
    return Asset(
        id=row["id"],
        type=row["type"],
        name=row["name"],
        source_type=row["source_type"],
        relative_path=row["relative_path"],
        fingerprint=row["fingerprint"],
        metadata_json=row["metadata_json"],
    )


def _harness_from_row(row: sqlite3.Row) -> Harness:
    return Harness(id=row["id"], name=row["name"], description=row["description"])


class AssetRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def upsert(
        self,
        asset_id: str,
        asset_type: str,
        name: str,
        source_type: str | None,
        relative_path: str,
        fingerprint: str,
        metadata_json: str = "{}",
    ) -> Asset:
        self.conn.execute(
            """
            INSERT INTO assets(id, type, name, source_type, relative_path, fingerprint, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
              type = excluded.type,
              name = excluded.name,
              source_type = excluded.source_type,
              relative_path = excluded.relative_path,
              fingerprint = excluded.fingerprint,
              metadata_json = excluded.metadata_json,
              updated_at = CURRENT_TIMESTAMP
            """,
            (asset_id, asset_type, name, source_type, relative_path, fingerprint, metadata_json),
        )
        return self.get(asset_id)

    def get(self, asset_id: str) -> Asset:
        row = self.conn.execute(
            """
            SELECT id, type, name, source_type, relative_path, fingerprint, metadata_json
            FROM assets
            WHERE id = ?
            """,
            (asset_id,),
        ).fetchone()
        if row is None:
            raise KeyError(asset_id)
        return _asset_from_row(row)

    def find_by_type_and_name(self, asset_type: str, name: str) -> Asset | None:
        row = self.conn.execute(
            """
            SELECT id, type, name, source_type, relative_path, fingerprint, metadata_json
            FROM assets
            WHERE type = ? AND name = ?
            """,
            (asset_type, name),
        ).fetchone()
        return _asset_from_row(row) if row else None

    def list_by_type(self, asset_type: str) -> list[Asset]:
        rows = self.conn.execute(
            """
            SELECT id, type, name, source_type, relative_path, fingerprint, metadata_json
            FROM assets
            WHERE type = ?
            ORDER BY name
            """,
            (asset_type,),
        ).fetchall()
        return [_asset_from_row(row) for row in rows]


class HarnessRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def create(self, name: str, description: str) -> Harness:
        harness_id = uuid.uuid4().hex
        self.conn.execute(
            "INSERT INTO harnesses(id, name, description) VALUES (?, ?, ?)",
            (harness_id, name, description),
        )
        return self.get(harness_id)

    def get(self, harness_id: str) -> Harness:
        row = self.conn.execute(
            "SELECT id, name, description FROM harnesses WHERE id = ?",
            (harness_id,),
        ).fetchone()
        if row is None:
            raise KeyError(harness_id)
        return _harness_from_row(row)

    def update(self, harness_id: str, name: str, description: str) -> Harness:
        self.conn.execute(
            """
            UPDATE harnesses
            SET name = ?, description = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (name, description, harness_id),
        )
        return self.get(harness_id)

    def list_harnesses(self) -> list[Harness]:
        rows = self.conn.execute(
            "SELECT id, name, description FROM harnesses ORDER BY name"
        ).fetchall()
        return [_harness_from_row(row) for row in rows]

    def list_harnesses_without_asset(self, asset_id: str) -> list[Harness]:
        rows = self.conn.execute(
            """
            SELECT h.id, h.name, h.description
            FROM harnesses h
            WHERE NOT EXISTS (
              SELECT 1
              FROM harness_assets ha
              WHERE ha.harness_id = h.id AND ha.asset_id = ?
            )
            ORDER BY h.name
            """,
            (asset_id,),
        ).fetchall()
        return [_harness_from_row(row) for row in rows]

    def list_harnesses_with_asset(self, asset_id: str) -> list[Harness]:
        rows = self.conn.execute(
            """
            SELECT h.id, h.name, h.description
            FROM harnesses h
            JOIN harness_assets ha ON ha.harness_id = h.id
            WHERE ha.asset_id = ?
            ORDER BY h.name
            """,
            (asset_id,),
        ).fetchall()
        return [_harness_from_row(row) for row in rows]

    def add_asset(self, harness_id: str, asset_id: str, asset_type: str, sort_order: int) -> None:
        self.conn.execute(
            """
            INSERT INTO harness_assets(harness_id, asset_id, asset_type, sort_order)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(harness_id, asset_id) DO UPDATE SET
              asset_type = excluded.asset_type,
              sort_order = excluded.sort_order
            """,
            (harness_id, asset_id, asset_type, sort_order),
        )

    def remove_asset(self, harness_id: str, asset_id: str) -> None:
        self.conn.execute(
            "DELETE FROM harness_assets WHERE harness_id = ? AND asset_id = ?",
            (harness_id, asset_id),
        )

    def list_assets(self, harness_id: str) -> list[Asset]:
        rows = self.conn.execute(
            """
            SELECT a.id, a.type, a.name, a.source_type, a.relative_path, a.fingerprint, a.metadata_json
            FROM harness_assets ha
            JOIN assets a ON a.id = ha.asset_id
            WHERE ha.harness_id = ?
            ORDER BY ha.sort_order, a.name
            """,
            (harness_id,),
        ).fetchall()
        return [_asset_from_row(row) for row in rows]

    def list_assets_by_type(self, harness_id: str, asset_type: str) -> list[Asset]:
        rows = self.conn.execute(
            """
            SELECT a.id, a.type, a.name, a.source_type, a.relative_path, a.fingerprint, a.metadata_json
            FROM harness_assets ha
            JOIN assets a ON a.id = ha.asset_id
            WHERE ha.harness_id = ? AND a.type = ?
            ORDER BY ha.sort_order, a.name
            """,
            (harness_id, asset_type),
        ).fetchall()
        return [_asset_from_row(row) for row in rows]
