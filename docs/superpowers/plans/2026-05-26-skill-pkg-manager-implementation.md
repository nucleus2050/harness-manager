# Skill Package Manager Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a PySide6 Windows desktop app that imports skills from Codex, Claude Code, and OpenCode, groups them into SQLite-backed packages, installs and uninstalls package skills, and imports or exports offline package archives.

**Architecture:** Use a small layered Python application: core filesystem/database services are independent of Qt, and the GUI calls those services through a thin controller layer. SQLite stores clients, skills, packages, package membership, install records, and operation logs; real skill files live under the app root in `skills/`.

**Tech Stack:** Python 3.11+, PySide6, SQLite via stdlib `sqlite3`, pytest, PyInstaller.

---

## File Structure

- `pyproject.toml` - package metadata, runtime dependencies, pytest config, console script.
- `README.md` - setup, test, run, and build commands.
- `src/skillpkg/__init__.py` - package marker and version.
- `src/skillpkg/__main__.py` - `python -m skillpkg` entry point.
- `src/skillpkg/app_paths.py` - resolves app root and managed folders.
- `src/skillpkg/models.py` - dataclasses shared by services and GUI.
- `src/skillpkg/db.py` - SQLite connection, schema creation, and transaction helper.
- `src/skillpkg/repositories.py` - database CRUD functions.
- `src/skillpkg/fingerprint.py` - deterministic directory hashing.
- `src/skillpkg/file_ops.py` - safe copy, remove, zip, and extraction helpers.
- `src/skillpkg/client_detection.py` - default skill directory detection for Codex, Claude Code, and OpenCode.
- `src/skillpkg/services.py` - use cases for import, package management, install, uninstall, archive import/export.
- `src/skillpkg/gui/main_window.py` - three-column PySide6 main window.
- `src/skillpkg/gui/dialogs.py` - reusable dialogs.
- `src/skillpkg/gui/controllers.py` - connects UI actions to services.
- `scripts/build.ps1` - PyInstaller build script.
- `tests/` - pytest coverage for database, paths, hashing, client detection, services, and archives.

---

### Task 1: Project Scaffold

**Files:**
- Create: `pyproject.toml`
- Create: `README.md`
- Create: `src/skillpkg/__init__.py`
- Create: `src/skillpkg/__main__.py`
- Create: `tests/conftest.py`

- [ ] **Step 1: Create `pyproject.toml`**

```toml
[build-system]
requires = ["setuptools>=69", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "skillpkg-manager"
version = "0.1.0"
description = "Desktop skill package manager for Codex, Claude Code, and OpenCode"
requires-python = ">=3.11"
dependencies = ["PySide6>=6.7"]

[project.optional-dependencies]
dev = ["pytest>=8.2", "pyinstaller>=6.8"]

[project.scripts]
skillpkg = "skillpkg.__main__:main"

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

- [ ] **Step 2: Create `README.md`**

```markdown
# Skill Package Manager

Windows desktop GUI for managing local skills across Codex, Claude Code, and OpenCode.

## Development

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .[dev]
pytest
python -m skillpkg
```

## Build

```powershell
.\scripts\build.ps1
```
```

- [ ] **Step 3: Create entry files**

`src/skillpkg/__init__.py`:

```python
__version__ = "0.1.0"
```

`src/skillpkg/__main__.py`:

```python
from __future__ import annotations

import sys


def main() -> int:
    from skillpkg.gui.main_window import run_app

    return run_app(sys.argv)


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Create shared pytest fixtures**

`tests/conftest.py`:

```python
from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def app_root(tmp_path: Path) -> Path:
    root = tmp_path / "SkillPkgManager"
    root.mkdir()
    return root


@pytest.fixture
def sample_skill(tmp_path: Path) -> Path:
    skill = tmp_path / "sample-skill"
    skill.mkdir()
    (skill / "SKILL.md").write_text("# Sample Skill\n\nBody\n", encoding="utf-8")
    return skill
```

- [ ] **Step 5: Verify scaffold**

Run: `pytest -q`

Expected: pytest starts successfully and either reports no tests collected or passes fixture loading.

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml README.md src/skillpkg/__init__.py src/skillpkg/__main__.py tests/conftest.py
git commit -m "chore: scaffold skill package manager"
```

If the workspace is not a git repository, record this checkpoint in the implementation summary instead of committing.

---

### Task 2: App Paths And Models

**Files:**
- Create: `src/skillpkg/app_paths.py`
- Create: `src/skillpkg/models.py`
- Test: `tests/test_app_paths.py`

- [ ] **Step 1: Write failing tests**

`tests/test_app_paths.py`:

```python
from __future__ import annotations

from skillpkg.app_paths import AppPaths


def test_app_paths_create_required_directories(app_root):
    paths = AppPaths(app_root)

    paths.ensure()

    assert paths.data_dir.is_dir()
    assert paths.skills_dir.is_dir()
    assert paths.exports_dir.is_dir()
    assert paths.config_dir.is_dir()
    assert paths.db_path == app_root / "data" / "skillpkg.db"


def test_skill_path_uses_skill_id(app_root):
    paths = AppPaths(app_root)

    assert paths.skill_path("abc") == app_root / "skills" / "abc"
```

- [ ] **Step 2: Verify failing test**

Run: `pytest tests/test_app_paths.py -q`

Expected: FAIL with `ModuleNotFoundError: No module named 'skillpkg.app_paths'`.

- [ ] **Step 3: Implement app paths**

`src/skillpkg/app_paths.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppPaths:
    root: Path

    @property
    def data_dir(self) -> Path:
        return self.root / "data"

    @property
    def skills_dir(self) -> Path:
        return self.root / "skills"

    @property
    def exports_dir(self) -> Path:
        return self.root / "exports"

    @property
    def config_dir(self) -> Path:
        return self.root / "config"

    @property
    def db_path(self) -> Path:
        return self.data_dir / "skillpkg.db"

    def skill_path(self, skill_id: str) -> Path:
        return self.skills_dir / skill_id

    def ensure(self) -> None:
        for directory in (self.data_dir, self.skills_dir, self.exports_dir, self.config_dir):
            directory.mkdir(parents=True, exist_ok=True)
```

- [ ] **Step 4: Implement models**

`src/skillpkg/models.py`:

```python
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
```

- [ ] **Step 5: Verify**

Run: `pytest tests/test_app_paths.py -q`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/skillpkg/app_paths.py src/skillpkg/models.py tests/test_app_paths.py
git commit -m "feat: add app paths and domain models"
```

---

### Task 3: SQLite Schema And Repositories

**Files:**
- Create: `src/skillpkg/db.py`
- Create: `src/skillpkg/repositories.py`
- Test: `tests/test_db.py`

- [ ] **Step 1: Write database tests**

`tests/test_db.py`:

```python
from __future__ import annotations

from skillpkg.app_paths import AppPaths
from skillpkg.db import connect, initialize_database
from skillpkg.repositories import ClientRepository, PackageRepository, SkillRepository


def test_initialize_database_seeds_clients(app_root):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)

    initialize_database(conn)

    clients = ClientRepository(conn).list_clients()
    assert [client.type for client in clients] == ["codex", "claude_code", "opencode"]


def test_create_skill_and_package_membership(app_root):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    initialize_database(conn)

    skills = SkillRepository(conn)
    packages = PackageRepository(conn)
    skills.upsert_skill("skill-a", "Skill A", "codex", "skills/skill-a", "abc")
    package_id = packages.create_package("Work A", "Daily workflow")
    packages.add_skill(package_id, "skill-a", 1)

    package_skills = packages.list_package_skills(package_id)
    assert package_skills[0].id == "skill-a"
    assert package_skills[0].name == "Skill A"
```

- [ ] **Step 2: Verify failing tests**

Run: `pytest tests/test_db.py -q`

Expected: FAIL because `skillpkg.db` and `skillpkg.repositories` do not exist.

- [ ] **Step 3: Implement SQLite schema**

`src/skillpkg/db.py`:

```python
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS clients (
  id INTEGER PRIMARY KEY,
  type TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  default_path TEXT,
  custom_path TEXT,
  enabled INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS skills (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  source_client TEXT,
  relative_path TEXT NOT NULL,
  fingerprint TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS packages (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  description TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS package_skills (
  package_id TEXT NOT NULL REFERENCES packages(id) ON DELETE CASCADE,
  skill_id TEXT NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
  sort_order INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (package_id, skill_id)
);

CREATE TABLE IF NOT EXISTS install_records (
  id TEXT PRIMARY KEY,
  package_id TEXT NOT NULL REFERENCES packages(id),
  skill_id TEXT NOT NULL REFERENCES skills(id),
  client_type TEXT NOT NULL,
  target_path TEXT NOT NULL,
  installed_path TEXT NOT NULL,
  fingerprint TEXT NOT NULL,
  installed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  uninstalled_at TEXT,
  status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS operation_logs (
  id TEXT PRIMARY KEY,
  action TEXT NOT NULL,
  client_type TEXT,
  package_id TEXT,
  skill_id TEXT,
  message TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

CLIENT_SEEDS = [("codex", "Codex"), ("claude_code", "Claude Code"), ("opencode", "OpenCode")]


def connect(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_database(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    conn.executemany("INSERT OR IGNORE INTO clients(type, name) VALUES (?, ?)", CLIENT_SEEDS)
    conn.commit()


@contextmanager
def transaction(conn: sqlite3.Connection) -> Iterator[None]:
    try:
        yield
    except Exception:
        conn.rollback()
        raise
    else:
        conn.commit()
```

- [ ] **Step 4: Implement repositories**

`src/skillpkg/repositories.py`:

```python
from __future__ import annotations

import sqlite3
import uuid
from pathlib import Path

from skillpkg.models import ClientConfig, Package, Skill


def _path_or_none(value: str | None) -> Path | None:
    return Path(value) if value else None


class ClientRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def list_clients(self) -> list[ClientConfig]:
        rows = self.conn.execute(
            "SELECT id, type, name, default_path, custom_path, enabled FROM clients ORDER BY id"
        ).fetchall()
        return [
            ClientConfig(row["id"], row["type"], row["name"], _path_or_none(row["default_path"]), _path_or_none(row["custom_path"]), bool(row["enabled"]))
            for row in rows
        ]

    def set_default_path(self, client_type: str, path: Path | None) -> None:
        self.conn.execute(
            "UPDATE clients SET default_path = ?, updated_at = CURRENT_TIMESTAMP WHERE type = ?",
            (str(path) if path else None, client_type),
        )

    def set_custom_path(self, client_type: str, path: Path | None) -> None:
        self.conn.execute(
            "UPDATE clients SET custom_path = ?, updated_at = CURRENT_TIMESTAMP WHERE type = ?",
            (str(path) if path else None, client_type),
        )


class SkillRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def upsert_skill(self, skill_id: str, name: str, source_client: str | None, relative_path: str, fingerprint: str) -> None:
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
            "SELECT id, name, source_client, relative_path, fingerprint FROM skills WHERE fingerprint = ?",
            (fingerprint,),
        ).fetchone()
        return None if row is None else Skill(row["id"], row["name"], row["source_client"], row["relative_path"], row["fingerprint"])

    def get(self, skill_id: str) -> Skill:
        row = self.conn.execute(
            "SELECT id, name, source_client, relative_path, fingerprint FROM skills WHERE id = ?",
            (skill_id,),
        ).fetchone()
        if row is None:
            raise KeyError(skill_id)
        return Skill(row["id"], row["name"], row["source_client"], row["relative_path"], row["fingerprint"])

    def list_skills(self) -> list[Skill]:
        rows = self.conn.execute(
            "SELECT id, name, source_client, relative_path, fingerprint FROM skills ORDER BY name"
        ).fetchall()
        return [Skill(row["id"], row["name"], row["source_client"], row["relative_path"], row["fingerprint"]) for row in rows]


class PackageRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def create_package(self, name: str, description: str) -> str:
        package_id = uuid.uuid4().hex
        self.conn.execute("INSERT INTO packages(id, name, description) VALUES (?, ?, ?)", (package_id, name, description))
        return package_id

    def get(self, package_id: str) -> Package:
        row = self.conn.execute("SELECT id, name, description FROM packages WHERE id = ?", (package_id,)).fetchone()
        if row is None:
            raise KeyError(package_id)
        return Package(row["id"], row["name"], row["description"])

    def list_packages(self) -> list[Package]:
        rows = self.conn.execute("SELECT id, name, description FROM packages ORDER BY name").fetchall()
        return [Package(row["id"], row["name"], row["description"]) for row in rows]

    def add_skill(self, package_id: str, skill_id: str, sort_order: int) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO package_skills(package_id, skill_id, sort_order) VALUES (?, ?, ?)",
            (package_id, skill_id, sort_order),
        )

    def remove_skill(self, package_id: str, skill_id: str) -> None:
        self.conn.execute("DELETE FROM package_skills WHERE package_id = ? AND skill_id = ?", (package_id, skill_id))

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
        return [Skill(row["id"], row["name"], row["source_client"], row["relative_path"], row["fingerprint"]) for row in rows]


class InstallRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def add_installed(self, package_id: str, skill_id: str, client_type: str, target_path: Path, installed_path: Path, fingerprint: str) -> str:
        record_id = uuid.uuid4().hex
        self.conn.execute(
            """
            INSERT INTO install_records(id, package_id, skill_id, client_type, target_path, installed_path, fingerprint, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'installed')
            """,
            (record_id, package_id, skill_id, client_type, str(target_path), str(installed_path), fingerprint),
        )
        return record_id

    def list_active(self, package_id: str, client_type: str) -> list[sqlite3.Row]:
        return self.conn.execute(
            """
            SELECT id, package_id, skill_id, client_type, target_path, installed_path, fingerprint, status
            FROM install_records
            WHERE package_id = ? AND client_type = ? AND status = 'installed'
            ORDER BY installed_at
            """,
            (package_id, client_type),
        ).fetchall()

    def mark_status(self, record_id: str, status: str) -> None:
        uninstalled_expr = "CURRENT_TIMESTAMP" if status == "uninstalled" else "uninstalled_at"
        self.conn.execute(f"UPDATE install_records SET status = ?, uninstalled_at = {uninstalled_expr} WHERE id = ?", (status, record_id))


class LogRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def add(self, action: str, message: str, client_type: str | None = None, package_id: str | None = None, skill_id: str | None = None) -> None:
        self.conn.execute(
            """
            INSERT INTO operation_logs(id, action, client_type, package_id, skill_id, message)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (uuid.uuid4().hex, action, client_type, package_id, skill_id, message),
        )
```

- [ ] **Step 5: Verify**

Run: `pytest tests/test_db.py -q`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/skillpkg/db.py src/skillpkg/repositories.py tests/test_db.py
git commit -m "feat: add sqlite schema and repositories"
```

---

### Task 4: Fingerprints, File Operations, And Client Detection

**Files:**
- Create: `src/skillpkg/fingerprint.py`
- Create: `src/skillpkg/file_ops.py`
- Create: `src/skillpkg/client_detection.py`
- Test: `tests/test_fingerprint.py`
- Test: `tests/test_client_detection.py`

- [ ] **Step 1: Write fingerprint tests**

`tests/test_fingerprint.py`:

```python
from __future__ import annotations

from skillpkg.fingerprint import fingerprint_directory


def test_fingerprint_is_stable_for_same_contents(tmp_path):
    first = tmp_path / "first"
    second = tmp_path / "second"
    first.mkdir()
    second.mkdir()
    (first / "SKILL.md").write_text("hello", encoding="utf-8")
    (second / "SKILL.md").write_text("hello", encoding="utf-8")

    assert fingerprint_directory(first) == fingerprint_directory(second)


def test_fingerprint_changes_when_file_changes(tmp_path):
    skill = tmp_path / "skill"
    skill.mkdir()
    target = skill / "SKILL.md"
    target.write_text("hello", encoding="utf-8")
    before = fingerprint_directory(skill)

    target.write_text("changed", encoding="utf-8")

    assert fingerprint_directory(skill) != before
```

- [ ] **Step 2: Write client detection tests**

`tests/test_client_detection.py`:

```python
from __future__ import annotations

from skillpkg.client_detection import detect_default_paths


def test_detect_default_paths_uses_user_profile(monkeypatch, tmp_path):
    profile = tmp_path / "User"
    profile.mkdir()
    monkeypatch.setenv("USERPROFILE", str(profile))

    paths = detect_default_paths()

    assert paths["codex"] == profile / ".codex" / "skills"
    assert paths["claude_code"] == profile / ".claude" / "skills"
    assert paths["opencode"] == profile / ".opencode" / "skills"
```

- [ ] **Step 3: Verify failing tests**

Run: `pytest tests/test_fingerprint.py tests/test_client_detection.py -q`

Expected: FAIL because modules do not exist.

- [ ] **Step 4: Implement fingerprinting**

`src/skillpkg/fingerprint.py`:

```python
from __future__ import annotations

import hashlib
from pathlib import Path

IGNORED_NAMES = {".DS_Store", "Thumbs.db", "__pycache__"}


def fingerprint_directory(directory: Path) -> str:
    if not directory.is_dir():
        raise NotADirectoryError(directory)

    digest = hashlib.sha256()
    for path in sorted(p for p in directory.rglob("*") if p.is_file()):
        if any(part in IGNORED_NAMES for part in path.parts):
            continue
        relative = path.relative_to(directory).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()
```

- [ ] **Step 5: Implement file operations**

`src/skillpkg/file_ops.py`:

```python
from __future__ import annotations

import shutil
import tempfile
import zipfile
from pathlib import Path


def copy_directory(source: Path, destination: Path, overwrite: bool = False) -> None:
    if not source.is_dir():
        raise NotADirectoryError(source)
    if destination.exists():
        if not overwrite:
            raise FileExistsError(destination)
        safe_remove_directory(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination)


def safe_remove_directory(path: Path) -> None:
    if path.exists() and not path.is_dir():
        raise NotADirectoryError(path)
    if path.exists():
        shutil.rmtree(path)


def make_zip(source_dir: Path, zip_path: Path) -> None:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_path in sorted(p for p in source_dir.rglob("*") if p.is_file()):
            archive.write(file_path, file_path.relative_to(source_dir).as_posix())


def extract_zip(zip_path: Path) -> Path:
    temp_dir = Path(tempfile.mkdtemp(prefix="skillpkg-import-"))
    with zipfile.ZipFile(zip_path, "r") as archive:
        for member in archive.infolist():
            target = temp_dir / member.filename
            resolved = target.resolve()
            if not str(resolved).startswith(str(temp_dir.resolve())):
                raise ValueError(f"Unsafe archive member: {member.filename}")
        archive.extractall(temp_dir)
    return temp_dir
```

- [ ] **Step 6: Implement client detection**

`src/skillpkg/client_detection.py`:

```python
from __future__ import annotations

import os
from pathlib import Path

from skillpkg.models import ClientType


def _home() -> Path:
    user_profile = os.environ.get("USERPROFILE")
    if user_profile:
        return Path(user_profile)
    return Path.home()


def detect_default_paths() -> dict[ClientType, Path]:
    home = _home()
    return {
        "codex": home / ".codex" / "skills",
        "claude_code": home / ".claude" / "skills",
        "opencode": home / ".opencode" / "skills",
    }
```

- [ ] **Step 7: Verify**

Run: `pytest tests/test_fingerprint.py tests/test_client_detection.py -q`

Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add src/skillpkg/fingerprint.py src/skillpkg/file_ops.py src/skillpkg/client_detection.py tests/test_fingerprint.py tests/test_client_detection.py
git commit -m "feat: add file hashing and client path detection"
```

---

### Task 5: Core Services

**Files:**
- Create: `src/skillpkg/services.py`
- Test: `tests/test_services_import.py`
- Test: `tests/test_services_install_uninstall.py`

- [ ] **Step 1: Write import and package tests**

`tests/test_services_import.py`:

```python
from __future__ import annotations

from skillpkg.app_paths import AppPaths
from skillpkg.db import connect, initialize_database
from skillpkg.repositories import PackageRepository, SkillRepository
from skillpkg.services import SkillPkgService


def test_import_skill_copies_to_managed_library(app_root, sample_skill):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    initialize_database(conn)
    service = SkillPkgService(paths, conn)

    skill = service.import_skill(sample_skill, "codex")

    assert (paths.skill_path(skill.id) / "SKILL.md").read_text(encoding="utf-8") == "# Sample Skill\n\nBody\n"
    assert SkillRepository(conn).get(skill.id).fingerprint == skill.fingerprint


def test_create_package_with_skills(app_root, sample_skill):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    initialize_database(conn)
    service = SkillPkgService(paths, conn)
    skill = service.import_skill(sample_skill, "codex")

    package_id = service.create_package("Work A", "Daily", [skill.id])

    skills = PackageRepository(conn).list_package_skills(package_id)
    assert [item.id for item in skills] == [skill.id]
```

- [ ] **Step 2: Write install and uninstall tests**

`tests/test_services_install_uninstall.py`:

```python
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


def test_install_package_copies_skills_and_records_install(app_root, sample_skill, tmp_path):
    paths, conn, service = _service(app_root)
    skill = service.import_skill(sample_skill, "codex")
    package_id = service.create_package("Work A", "Daily", [skill.id])
    target = tmp_path / "codex-skills"
    target.mkdir()

    installed = service.install_package(package_id, "codex", target)

    assert len(installed) == 1
    assert (target / skill.id / "SKILL.md").is_file()


def test_uninstall_package_deletes_unchanged_installed_skill(app_root, sample_skill, tmp_path):
    paths, conn, service = _service(app_root)
    skill = service.import_skill(sample_skill, "codex")
    package_id = service.create_package("Work A", "Daily", [skill.id])
    target = tmp_path / "codex-skills"
    target.mkdir()
    service.install_package(package_id, "codex", target)

    result = service.uninstall_package(package_id, "codex")

    assert result[skill.id] == "uninstalled"
    assert not (target / skill.id).exists()


def test_uninstall_package_refuses_modified_skill(app_root, sample_skill, tmp_path):
    paths, conn, service = _service(app_root)
    skill = service.import_skill(sample_skill, "codex")
    package_id = service.create_package("Work A", "Daily", [skill.id])
    target = tmp_path / "codex-skills"
    target.mkdir()
    service.install_package(package_id, "codex", target)
    (target / skill.id / "SKILL.md").write_text("changed", encoding="utf-8")

    result = service.uninstall_package(package_id, "codex")

    assert result[skill.id] == "modified"
    assert (target / skill.id).exists()
```

- [ ] **Step 3: Verify failing tests**

Run: `pytest tests/test_services_import.py tests/test_services_install_uninstall.py -q`

Expected: FAIL because `SkillPkgService` does not exist.

- [ ] **Step 4: Implement core services**

`src/skillpkg/services.py`:

```python
from __future__ import annotations

import json
import re
import shutil
import sqlite3
import tempfile
import uuid
from pathlib import Path

from skillpkg.app_paths import AppPaths
from skillpkg.db import transaction
from skillpkg.file_ops import copy_directory, extract_zip, make_zip, safe_remove_directory
from skillpkg.fingerprint import fingerprint_directory
from skillpkg.models import ClientType, Skill
from skillpkg.repositories import InstallRepository, LogRepository, PackageRepository, SkillRepository


def _slug(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_.-]+", "-", value.strip()).strip("-._")
    return cleaned.lower() or uuid.uuid4().hex


class SkillPkgService:
    def __init__(self, paths: AppPaths, conn: sqlite3.Connection) -> None:
        self.paths = paths
        self.conn = conn
        self.skills = SkillRepository(conn)
        self.packages = PackageRepository(conn)
        self.installs = InstallRepository(conn)
        self.logs = LogRepository(conn)

    def import_skill(self, source_dir: Path, source_client: ClientType | None) -> Skill:
        fingerprint = fingerprint_directory(source_dir)
        existing = self.skills.find_by_fingerprint(fingerprint)
        if existing:
            return existing

        skill_id = _slug(source_dir.name)
        destination = self.paths.skill_path(skill_id)
        if destination.exists():
            skill_id = f"{skill_id}-{uuid.uuid4().hex[:8]}"
            destination = self.paths.skill_path(skill_id)

        with transaction(self.conn):
            copy_directory(source_dir, destination)
            relative_path = f"skills/{skill_id}"
            self.skills.upsert_skill(skill_id, source_dir.name, source_client, relative_path, fingerprint)
            self.logs.add("import_skill", f"Imported {source_dir} as {skill_id}", source_client, skill_id=skill_id)
        return self.skills.get(skill_id)

    def create_package(self, name: str, description: str, skill_ids: list[str]) -> str:
        with transaction(self.conn):
            package_id = self.packages.create_package(name, description)
            for index, skill_id in enumerate(skill_ids):
                self.packages.add_skill(package_id, skill_id, index)
            self.logs.add("create_package", f"Created package {name}", package_id=package_id)
        return package_id

    def install_package(self, package_id: str, client_type: ClientType, target_path: Path, overwrite: bool = False) -> list[Path]:
        if not target_path.is_dir():
            raise NotADirectoryError(target_path)

        installed_paths: list[Path] = []
        package_skills = self.packages.list_package_skills(package_id)
        with transaction(self.conn):
            for skill in package_skills:
                source = self.paths.root / skill.relative_path
                destination = target_path / skill.id
                copy_directory(source, destination, overwrite=overwrite)
                self.installs.add_installed(package_id, skill.id, client_type, target_path, destination, skill.fingerprint)
                self.logs.add("install_skill", f"Installed {skill.id} to {destination}", client_type, package_id, skill.id)
                installed_paths.append(destination)
        return installed_paths

    def uninstall_package(self, package_id: str, client_type: ClientType) -> dict[str, str]:
        result: dict[str, str] = {}
        records = self.installs.list_active(package_id, client_type)
        with transaction(self.conn):
            for record in records:
                installed_path = Path(record["installed_path"])
                skill_id = record["skill_id"]
                if not installed_path.exists():
                    self.installs.mark_status(record["id"], "missing")
                    result[skill_id] = "missing"
                    continue
                current_fingerprint = fingerprint_directory(installed_path)
                if current_fingerprint != record["fingerprint"]:
                    self.installs.mark_status(record["id"], "modified")
                    result[skill_id] = "modified"
                    continue
                safe_remove_directory(installed_path)
                self.installs.mark_status(record["id"], "uninstalled")
                self.logs.add("uninstall_skill", f"Uninstalled {skill_id} from {installed_path}", client_type, package_id, skill_id)
                result[skill_id] = "uninstalled"
        return result
```

- [ ] **Step 5: Verify**

Run: `pytest tests/test_services_import.py tests/test_services_install_uninstall.py -q`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/skillpkg/services.py tests/test_services_import.py tests/test_services_install_uninstall.py
git commit -m "feat: add core skill package services"
```

---

### Task 6: Offline Package Import And Export

**Files:**
- Modify: `src/skillpkg/services.py`
- Test: `tests/test_offline_package.py`

- [ ] **Step 1: Write archive round-trip test**

`tests/test_offline_package.py`:

```python
from __future__ import annotations

from skillpkg.app_paths import AppPaths
from skillpkg.db import connect, initialize_database
from skillpkg.repositories import PackageRepository
from skillpkg.services import SkillPkgService


def _make_service(root):
    paths = AppPaths(root)
    paths.ensure()
    conn = connect(paths.db_path)
    initialize_database(conn)
    return paths, conn, SkillPkgService(paths, conn)


def test_export_and_import_offline_package(app_root, sample_skill, tmp_path):
    paths, conn, service = _make_service(app_root)
    skill = service.import_skill(sample_skill, "codex")
    package_id = service.create_package("Work A", "Daily", [skill.id])

    archive = service.export_package(package_id)

    imported_root = tmp_path / "ImportedApp"
    imported_paths, imported_conn, imported_service = _make_service(imported_root)
    imported_package_id = imported_service.import_offline_package(archive)

    imported_skills = PackageRepository(imported_conn).list_package_skills(imported_package_id)
    assert [item.name for item in imported_skills] == ["sample-skill"]
    assert (imported_paths.skills_dir / imported_skills[0].id / "SKILL.md").is_file()
```

- [ ] **Step 2: Verify failing test**

Run: `pytest tests/test_offline_package.py -q`

Expected: FAIL because archive methods do not exist.

- [ ] **Step 3: Add export and import methods**

Append to `SkillPkgService` in `src/skillpkg/services.py`:

```python
    def export_package(self, package_id: str) -> Path:
        package = self.packages.get(package_id)
        skills = self.packages.list_package_skills(package_id)
        staging = Path(tempfile.mkdtemp(prefix="skillpkg-export-"))
        try:
            skill_entries = []
            skills_dir = staging / "skills"
            skills_dir.mkdir(parents=True)
            for skill in skills:
                source = self.paths.root / skill.relative_path
                destination = skills_dir / skill.id
                copy_directory(source, destination)
                skill_entries.append(
                    {
                        "id": skill.id,
                        "name": skill.name,
                        "relative_path": f"skills/{skill.id}",
                        "fingerprint": skill.fingerprint,
                    }
                )
            manifest = {
                "schema_version": 1,
                "package": {"id": package.id, "name": package.name, "description": package.description},
                "skills": skill_entries,
            }
            (staging / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            archive_path = self.paths.exports_dir / f"{_slug(package.name)}.skillpkg.zip"
            make_zip(staging, archive_path)
            self.logs.add("export_package", f"Exported package {package.name} to {archive_path}", package_id=package_id)
            self.conn.commit()
            return archive_path
        finally:
            shutil.rmtree(staging, ignore_errors=True)

    def import_offline_package(self, archive_path: Path) -> str:
        extracted = extract_zip(archive_path)
        try:
            manifest_path = extracted / "manifest.json"
            if not manifest_path.is_file():
                raise ValueError("manifest.json is missing")
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if manifest.get("schema_version") != 1:
                raise ValueError("Unsupported schema_version")
            package = manifest["package"]
            imported_skill_ids: list[str] = []
            with transaction(self.conn):
                for entry in manifest["skills"]:
                    imported = self.import_skill(extracted / entry["relative_path"], None)
                    imported_skill_ids.append(imported.id)
                package_id = self.packages.create_package(package["name"], package.get("description", ""))
                for index, skill_id in enumerate(imported_skill_ids):
                    self.packages.add_skill(package_id, skill_id, index)
                self.logs.add("import_package", f"Imported package {package['name']} from {archive_path}", package_id=package_id)
            return package_id
        finally:
            shutil.rmtree(extracted, ignore_errors=True)
```

- [ ] **Step 4: Verify archive flow**

Run: `pytest tests/test_offline_package.py -q`

Expected: PASS.

- [ ] **Step 5: Run all core tests**

Run: `pytest tests/test_db.py tests/test_fingerprint.py tests/test_client_detection.py tests/test_services_import.py tests/test_services_install_uninstall.py tests/test_offline_package.py -q`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/skillpkg/services.py tests/test_offline_package.py
git commit -m "feat: import and export offline packages"
```

---

### Task 7: PySide6 Main Window

**Files:**
- Create: `src/skillpkg/gui/__init__.py`
- Create: `src/skillpkg/gui/main_window.py`
- Create: `src/skillpkg/gui/dialogs.py`
- Create: `src/skillpkg/gui/controllers.py`

- [ ] **Step 1: Create dialog helpers**

`src/skillpkg/gui/dialogs.py`:

```python
from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QFileDialog, QInputDialog, QMessageBox, QWidget


def choose_directory(parent: QWidget, title: str) -> Path | None:
    value = QFileDialog.getExistingDirectory(parent, title)
    return Path(value) if value else None


def choose_archive(parent: QWidget) -> Path | None:
    value, _ = QFileDialog.getOpenFileName(parent, "Import Offline Package", "", "Skill Package (*.skillpkg.zip);;Zip (*.zip)")
    return Path(value) if value else None


def ask_text(parent: QWidget, title: str, label: str) -> str | None:
    value, ok = QInputDialog.getText(parent, title, label)
    text = value.strip()
    return text if ok and text else None


def show_error(parent: QWidget, title: str, message: str) -> None:
    QMessageBox.critical(parent, title, message)


def show_info(parent: QWidget, title: str, message: str) -> None:
    QMessageBox.information(parent, title, message)
```

- [ ] **Step 2: Create GUI controller**

`src/skillpkg/gui/controllers.py`:

```python
from __future__ import annotations

import sqlite3
from pathlib import Path

from skillpkg.app_paths import AppPaths
from skillpkg.client_detection import detect_default_paths
from skillpkg.db import initialize_database
from skillpkg.repositories import ClientRepository, PackageRepository, SkillRepository
from skillpkg.services import SkillPkgService


class MainController:
    def __init__(self, app_root: Path, conn: sqlite3.Connection) -> None:
        self.paths = AppPaths(app_root)
        self.paths.ensure()
        self.conn = conn
        initialize_database(conn)
        self.service = SkillPkgService(self.paths, conn)
        self.clients = ClientRepository(conn)
        self.skills = SkillRepository(conn)
        self.packages = PackageRepository(conn)
        self.refresh_default_paths()

    def refresh_default_paths(self) -> None:
        for client_type, path in detect_default_paths().items():
            self.clients.set_default_path(client_type, path)
        self.conn.commit()

    def list_clients(self):
        return self.clients.list_clients()

    def list_packages(self):
        return self.packages.list_packages()

    def list_skills(self):
        return self.skills.list_skills()

    def import_skill_directory(self, source_dir: Path, client_type: str):
        skill = self.service.import_skill(source_dir, client_type)  # type: ignore[arg-type]
        self.conn.commit()
        return skill

    def create_package_from_all_skills(self, name: str, description: str) -> str:
        skill_ids = [skill.id for skill in self.skills.list_skills()]
        return self.service.create_package(name, description, skill_ids)

    def export_package_by_row(self, row: int) -> Path:
        package = self.packages.list_packages()[row]
        return self.service.export_package(package.id)

    def import_offline_package(self, archive: Path) -> str:
        package_id = self.service.import_offline_package(archive)
        self.conn.commit()
        return package_id

    def install_package_by_row(self, row: int, client_type: str, target_path: Path):
        package = self.packages.list_packages()[row]
        return self.service.install_package(package.id, client_type, target_path)  # type: ignore[arg-type]

    def uninstall_package_by_row(self, row: int, client_type: str):
        package = self.packages.list_packages()[row]
        return self.service.uninstall_package(package.id, client_type)  # type: ignore[arg-type]
```

- [ ] **Step 3: Create main window**

`src/skillpkg/gui/main_window.py`:

```python
from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication, QHBoxLayout, QLabel, QListWidget, QMainWindow, QPushButton, QVBoxLayout, QWidget

from skillpkg.app_paths import AppPaths
from skillpkg.db import connect
from skillpkg.gui.controllers import MainController


class MainWindow(QMainWindow):
    def __init__(self, controller: MainController) -> None:
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Skill Package Manager")
        self.resize(1180, 720)

        self.client_list = QListWidget()
        self.package_list = QListWidget()
        self.skill_list = QListWidget()
        self.import_client_button = QPushButton("Import Skill Directory")
        self.new_package_button = QPushButton("New Package From All Skills")
        self.import_archive_button = QPushButton("Import Offline Package")
        self.export_archive_button = QPushButton("Export Offline Package")
        self.install_codex_button = QPushButton("Install To Codex")
        self.uninstall_codex_button = QPushButton("Uninstall From Codex")
        self.install_claude_button = QPushButton("Install To Claude Code")
        self.uninstall_claude_button = QPushButton("Uninstall From Claude Code")
        self.install_opencode_button = QPushButton("Install To OpenCode")
        self.uninstall_opencode_button = QPushButton("Uninstall From OpenCode")

        root = QWidget()
        layout = QHBoxLayout(root)
        layout.addWidget(self._client_panel())
        layout.addWidget(self._package_panel())
        layout.addWidget(self._detail_panel())
        self.setCentralWidget(root)
        self.connect_actions()
        self.refresh()

    def _client_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.addWidget(QLabel("Clients"))
        layout.addWidget(self.client_list)
        layout.addWidget(self.import_client_button)
        return panel

    def _package_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.addWidget(QLabel("Packages"))
        layout.addWidget(self.package_list)
        layout.addWidget(self.new_package_button)
        layout.addWidget(self.import_archive_button)
        layout.addWidget(self.export_archive_button)
        return panel

    def _detail_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.addWidget(QLabel("Package Skills"))
        layout.addWidget(self.skill_list)
        for button in (
            self.install_codex_button,
            self.uninstall_codex_button,
            self.install_claude_button,
            self.uninstall_claude_button,
            self.install_opencode_button,
            self.uninstall_opencode_button,
        ):
            layout.addWidget(button)
        return panel

    def connect_actions(self) -> None:
        self.import_client_button.clicked.connect(self._import_skill)
        self.new_package_button.clicked.connect(self._new_package)
        self.import_archive_button.clicked.connect(self._import_archive)
        self.export_archive_button.clicked.connect(self._export_archive)
        self.install_codex_button.clicked.connect(lambda: self._install("codex"))
        self.uninstall_codex_button.clicked.connect(lambda: self._uninstall("codex"))
        self.install_claude_button.clicked.connect(lambda: self._install("claude_code"))
        self.uninstall_claude_button.clicked.connect(lambda: self._uninstall("claude_code"))
        self.install_opencode_button.clicked.connect(lambda: self._install("opencode"))
        self.uninstall_opencode_button.clicked.connect(lambda: self._uninstall("opencode"))

    def refresh(self) -> None:
        self.client_list.clear()
        for client in self.controller.list_clients():
            path = client.effective_path or "not configured"
            self.client_list.addItem(f"{client.name}: {path}")

        self.package_list.clear()
        for package in self.controller.list_packages():
            self.package_list.addItem(package.name)

        self.skill_list.clear()
        for skill in self.controller.list_skills():
            self.skill_list.addItem(skill.name)

    def _selected_package_row(self) -> int | None:
        row = self.package_list.currentRow()
        return row if row >= 0 else None

    def _import_skill(self) -> None:
        from skillpkg.gui import dialogs

        source = dialogs.choose_directory(self, "Choose Skill Directory To Import")
        if source is None:
            return
        self.controller.import_skill_directory(source, "codex")
        self.refresh()
        dialogs.show_info(self, "Imported", f"Imported {source.name}")

    def _new_package(self) -> None:
        from skillpkg.gui import dialogs

        name = dialogs.ask_text(self, "New Package", "Package name")
        if not name:
            return
        self.controller.create_package_from_all_skills(name, "")
        self.refresh()

    def _import_archive(self) -> None:
        from skillpkg.gui import dialogs

        archive = dialogs.choose_archive(self)
        if archive is None:
            return
        self.controller.import_offline_package(archive)
        self.refresh()
        dialogs.show_info(self, "Imported", f"Imported {archive.name}")

    def _export_archive(self) -> None:
        from skillpkg.gui import dialogs

        row = self._selected_package_row()
        if row is None:
            dialogs.show_error(self, "No Package", "Select a package first.")
            return
        archive = self.controller.export_package_by_row(row)
        dialogs.show_info(self, "Exported", f"Exported to {archive}")

    def _install(self, client_type: str) -> None:
        from skillpkg.gui import dialogs

        row = self._selected_package_row()
        if row is None:
            dialogs.show_error(self, "No Package", "Select a package first.")
            return
        target = dialogs.choose_directory(self, f"Choose {client_type} Skill Directory")
        if target is None:
            return
        installed = self.controller.install_package_by_row(row, client_type, target)
        dialogs.show_info(self, "Installed", f"Installed {len(installed)} skills.")

    def _uninstall(self, client_type: str) -> None:
        from skillpkg.gui import dialogs

        row = self._selected_package_row()
        if row is None:
            dialogs.show_error(self, "No Package", "Select a package first.")
            return
        result = self.controller.uninstall_package_by_row(row, client_type)
        dialogs.show_info(self, "Uninstall Result", str(result))


def run_app(argv: list[str] | None = None) -> int:
    app = QApplication(argv or sys.argv)
    app_root = Path.cwd()
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    controller = MainController(app_root, conn)
    window = MainWindow(controller)
    window.show()
    return app.exec()
```

- [ ] **Step 4: Create GUI package marker**

`src/skillpkg/gui/__init__.py`:

```python
"""Qt GUI for Skill Package Manager."""
```

- [ ] **Step 5: Manual GUI smoke test**

Run: `python -m skillpkg`

Expected: a desktop window opens with three columns and buttons for import, package creation, archive import/export, install, and uninstall.

- [ ] **Step 6: Run core tests**

Run: `pytest -q`

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add src/skillpkg/gui src/skillpkg/__main__.py
git commit -m "feat: add PySide6 skill manager UI"
```

---

### Task 8: Build Script And Final Verification

**Files:**
- Create: `scripts/build.ps1`
- Modify: `README.md`

- [ ] **Step 1: Create PyInstaller build script**

`scripts/build.ps1`:

```powershell
$ErrorActionPreference = "Stop"

python -m pip install -e .[dev]
python -m PyInstaller `
  --noconfirm `
  --windowed `
  --name SkillPkgManager `
  --paths src `
  -m skillpkg

Write-Host "Built dist\SkillPkgManager\SkillPkgManager.exe"
```

- [ ] **Step 2: Append runtime notes to README**

```markdown
## Runtime Data

The app stores runtime data under the directory where it is launched:

- `data/skillpkg.db`
- `skills/`
- `exports/`
- `config/`

Use a writable directory such as `D:\Tools\SkillPkgManager` for normal use.

## Safety

Uninstall removes only paths recorded in `install_records`. If an installed skill has been edited after installation, uninstall marks it as modified and leaves it in place.
```

- [ ] **Step 3: Run tests**

Run: `pytest -q`

Expected: PASS.

- [ ] **Step 4: Build executable**

Run: `powershell -ExecutionPolicy Bypass -File scripts/build.ps1`

Expected: `dist\SkillPkgManager\SkillPkgManager.exe` exists.

- [ ] **Step 5: Smoke test executable**

Run: `dist\SkillPkgManager\SkillPkgManager.exe`

Expected: the main window opens and creates `data/skillpkg.db`, `skills/`, `exports/`, and `config/` in the launch directory.

- [ ] **Step 6: Commit**

```bash
git add scripts/build.ps1 README.md
git commit -m "chore: add windows build script"
```

---

## Final Verification Checklist

- [ ] `pytest -q` passes.
- [ ] `python -m skillpkg` opens the desktop app.
- [ ] Importing a skill copies files into `skills/<skill_id>/`.
- [ ] Creating a package writes rows to SQLite.
- [ ] Installing a package copies skills to a selected client directory.
- [ ] Uninstalling removes unchanged installed skills only.
- [ ] Modified installed skills are not deleted.
- [ ] Export creates a `.skillpkg.zip` with `manifest.json` and `skills/`.
- [ ] Importing that zip recreates the package and skill files in a fresh app root.
- [ ] `scripts/build.ps1` creates `dist\SkillPkgManager\SkillPkgManager.exe`.

## Spec Coverage Self-Review

- Windows desktop app with PySide6: Tasks 7 and 8.
- SQLite under installation directory: Tasks 2 and 3.
- Tool-managed `skills/` directory: Tasks 2 and 5.
- Abstract database-only packages: Tasks 3 and 5.
- Codex, Claude Code, and OpenCode path detection: Task 4.
- No skill format conversion: services copy directories as-is in Tasks 5 and 6.
- One-click install and uninstall: Task 5 service behavior and Task 7 GUI buttons.
- Safe uninstall by install records and fingerprint: Task 5.
- Offline package export and import: Task 6 and Task 7 GUI wiring.
- Build as Windows executable: Task 8.
