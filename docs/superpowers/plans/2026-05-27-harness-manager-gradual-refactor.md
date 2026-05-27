# Harness Manager Gradual Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Gradually refactor the working Skill Package Manager into Harness Manager while preserving the current skill import/install/uninstall flow.

**Architecture:** Add the Harness/Asset model alongside the existing package/skill model, then migrate reads and UI terminology toward Harness Manager. Keep core logic in services/repositories and keep PySide6 code as a thin presentation layer.

**Tech Stack:** Python 3.11+, PySide6/Qt Widgets, SQLite via `sqlite3`, pytest, PyInstaller.

---

## File Structure

- Modify: `src/skillpkg/models.py` - add `AssetType`, `Asset`, `Harness`, and `HarnessAsset` dataclasses.
- Modify: `src/skillpkg/db.py` - add additive schema for `harnesses`, `assets`, and `harness_assets`.
- Modify: `src/skillpkg/repositories.py` - add `AssetRepository` and `HarnessRepository` without removing existing repositories.
- Create: `src/skillpkg/asset_paths.py` - asset path helpers for `assets/agents`, `assets/mcp`, and `assets/skills`.
- Modify: `src/skillpkg/services.py` - add import methods for AGENTS.md and MCP assets; keep existing skill methods working.
- Modify: `src/skillpkg/gui/controllers.py` - expose Harness/Asset operations to the GUI.
- Modify: `src/skillpkg/gui/main_window.py` - rename UI to Harness Manager and add AGENTS.md/MCP asset library sections.
- Modify: `src/skillpkg/gui/styles.py` - add any required section styles while preserving current theme.
- Modify: `tests/` - add focused tests for additive schema, repositories, asset imports, migration parity, and GUI text contracts.
- Modify: `AGENTS.md` only after user approval if implementation changes the documented architecture beyond this plan.

---

### Task 1: Add Harness And Asset Domain Model

**Files:**
- Modify: `src/skillpkg/models.py`
- Test: `tests/test_harness_models.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_harness_models.py`:

```python
from __future__ import annotations

from skillpkg.models import Asset, Harness


def test_asset_model_stores_type_and_path():
    asset = Asset(
        id="asset-1",
        type="agents_md",
        name="代码审查规则",
        source_type="custom",
        relative_path="assets/agents/asset-1/AGENTS.md",
        fingerprint="abc123",
        metadata_json="{}",
    )

    assert asset.type == "agents_md"
    assert asset.relative_path.endswith("AGENTS.md")


def test_harness_model_stores_name_and_description():
    harness = Harness(id="h1", name="代码审查 Harness", description="审查任务工具包")

    assert harness.name == "代码审查 Harness"
    assert harness.description == "审查任务工具包"
```

- [ ] **Step 2: Run tests and verify failure**

Run: `pytest tests/test_harness_models.py -q`

Expected: FAIL because `Asset` and `Harness` do not exist.

- [ ] **Step 3: Add models**

Append to `src/skillpkg/models.py`:

```python
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
class HarnessAsset:
    harness_id: str
    asset_id: str
    asset_type: AssetType
    sort_order: int
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_harness_models.py -q`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/skillpkg/models.py tests/test_harness_models.py
git commit -m "feat: add harness asset domain models"
```

---

### Task 2: Add Additive Harness/Asset SQLite Schema And Repositories

**Files:**
- Modify: `src/skillpkg/db.py`
- Modify: `src/skillpkg/repositories.py`
- Test: `tests/test_harness_repositories.py`

- [ ] **Step 1: Write failing repository tests**

Create `tests/test_harness_repositories.py`:

```python
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
```

- [ ] **Step 2: Run tests and verify failure**

Run: `pytest tests/test_harness_repositories.py -q`

Expected: FAIL because `AssetRepository` and `HarnessRepository` do not exist.

- [ ] **Step 3: Add schema**

Add to the `SCHEMA` string in `src/skillpkg/db.py`:

```sql
CREATE TABLE IF NOT EXISTS harnesses (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  description TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS assets (
  id TEXT PRIMARY KEY,
  type TEXT NOT NULL,
  name TEXT NOT NULL,
  source_type TEXT,
  relative_path TEXT NOT NULL,
  fingerprint TEXT NOT NULL,
  metadata_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS harness_assets (
  harness_id TEXT NOT NULL REFERENCES harnesses(id) ON DELETE CASCADE,
  asset_id TEXT NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
  asset_type TEXT NOT NULL,
  sort_order INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (harness_id, asset_id)
);
```

- [ ] **Step 4: Add repositories**

Append to `src/skillpkg/repositories.py`:

```python
from skillpkg.models import Asset, Harness


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
            "SELECT id, type, name, source_type, relative_path, fingerprint, metadata_json FROM assets WHERE id = ?",
            (asset_id,),
        ).fetchone()
        if row is None:
            raise KeyError(asset_id)
        return _asset_from_row(row)

    def list_by_type(self, asset_type: str) -> list[Asset]:
        rows = self.conn.execute(
            "SELECT id, type, name, source_type, relative_path, fingerprint, metadata_json FROM assets WHERE type = ? ORDER BY name",
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

    def list_harnesses(self) -> list[Harness]:
        rows = self.conn.execute("SELECT id, name, description FROM harnesses ORDER BY name").fetchall()
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
```

- [ ] **Step 5: Run tests**

Run: `pytest tests/test_harness_repositories.py tests/test_db.py -q`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/skillpkg/db.py src/skillpkg/repositories.py tests/test_harness_repositories.py
git commit -m "feat: add harness asset repositories"
```

---

### Task 3: Add Asset Paths And File Imports For AGENTS.md/MCP

**Files:**
- Create: `src/skillpkg/asset_paths.py`
- Modify: `src/skillpkg/services.py`
- Test: `tests/test_asset_imports.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_asset_imports.py`:

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
```

- [ ] **Step 2: Run tests and verify failure**

Run: `pytest tests/test_asset_imports.py -q`

Expected: FAIL because `import_agents_md_asset` and `import_mcp_asset` do not exist.

- [ ] **Step 3: Create asset path helper**

Create `src/skillpkg/asset_paths.py`:

```python
from __future__ import annotations

from pathlib import Path

from skillpkg.app_paths import AppPaths


def asset_dir(paths: AppPaths, asset_type: str, asset_id: str) -> Path:
    if asset_type == "agents_md":
        return paths.root / "assets" / "agents" / asset_id
    if asset_type == "mcp":
        return paths.root / "assets" / "mcp" / asset_id
    if asset_type == "skill":
        return paths.root / "assets" / "skills" / asset_id
    raise ValueError(f"Unsupported asset type: {asset_type}")
```

- [ ] **Step 4: Add service imports**

Modify `src/skillpkg/services.py` imports:

```python
import shutil
import uuid
from skillpkg.asset_paths import asset_dir
from skillpkg.repositories import AssetRepository
```

In `SkillPkgService.__init__`, add:

```python
self.assets = AssetRepository(conn)
```

Append methods:

```python
    def import_agents_md_asset(self, source_file: Path, name: str, source_type: str | None):
        if not source_file.is_file():
            raise FileNotFoundError(source_file)
        asset_id = uuid.uuid4().hex
        destination_dir = asset_dir(self.paths, "agents_md", asset_id)
        destination_dir.mkdir(parents=True, exist_ok=True)
        destination = destination_dir / "AGENTS.md"
        try:
            shutil.copy2(source_file, destination)
            fingerprint = fingerprint_directory(destination_dir)
            with transaction(self.conn):
                asset = self.assets.upsert(
                    asset_id,
                    "agents_md",
                    name,
                    source_type,
                    destination.relative_to(self.paths.root).as_posix(),
                    fingerprint,
                    "{}",
                )
                self.logs.add("import_asset", f"Imported AGENTS.md asset {name}")
            return asset
        except Exception:
            safe_remove_directory(destination_dir)
            raise

    def import_mcp_asset(self, source_file: Path, name: str, source_type: str | None):
        if not source_file.is_file():
            raise FileNotFoundError(source_file)
        asset_id = uuid.uuid4().hex
        destination_dir = asset_dir(self.paths, "mcp", asset_id)
        destination_dir.mkdir(parents=True, exist_ok=True)
        destination = destination_dir / source_file.name
        try:
            shutil.copy2(source_file, destination)
            fingerprint = fingerprint_directory(destination_dir)
            with transaction(self.conn):
                asset = self.assets.upsert(
                    asset_id,
                    "mcp",
                    name,
                    source_type,
                    destination.relative_to(self.paths.root).as_posix(),
                    fingerprint,
                    "{}",
                )
                self.logs.add("import_asset", f"Imported MCP asset {name}")
            return asset
        except Exception:
            safe_remove_directory(destination_dir)
            raise
```

- [ ] **Step 5: Run tests**

Run: `pytest tests/test_asset_imports.py -q`

Expected: PASS.

- [ ] **Step 6: Run service regression tests**

Run: `pytest tests/test_services_import.py tests/test_services_install_uninstall.py tests/test_offline_package.py tests/test_asset_imports.py -q`

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add src/skillpkg/asset_paths.py src/skillpkg/services.py tests/test_asset_imports.py
git commit -m "feat: import agents and mcp assets"
```

---

### Task 4: Add Harness Controller Methods And UI Terminology

**Files:**
- Modify: `src/skillpkg/gui/controllers.py`
- Modify: `src/skillpkg/gui/main_window.py`
- Test: `tests/test_harness_controller.py`
- Test: `tests/test_gui_localization.py`

- [ ] **Step 1: Write controller tests**

Create `tests/test_harness_controller.py`:

```python
from __future__ import annotations

from skillpkg.app_paths import AppPaths
from skillpkg.db import connect
from skillpkg.gui.controllers import MainController


def test_controller_creates_empty_harness(app_root):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    controller = MainController(app_root, conn)

    harness = controller.create_harness("代码审查", "审查任务工具包")

    assert harness.name == "代码审查"
    assert controller.list_harnesses()[0].id == harness.id
```

- [ ] **Step 2: Update GUI localization tests**

Add assertions to `tests/test_gui_localization.py`:

```python

def test_main_window_uses_harness_manager_terms():
    source = Path("src/skillpkg/gui/main_window.py").read_text(encoding="utf-8")

    for text in ["Harness Manager", "Harness", "AGENTS.md", "MCP", "Skills"]:
        assert text in source

    assert "Skill Package Manager" not in source
```

- [ ] **Step 3: Run tests and verify failure**

Run: `pytest tests/test_harness_controller.py tests/test_gui_localization.py -q`

Expected: FAIL because controller methods and UI terms are not updated.

- [ ] **Step 4: Add controller methods**

Modify `src/skillpkg/gui/controllers.py` imports:

```python
from skillpkg.repositories import HarnessRepository, AssetRepository
```

In `MainController.__init__`, add:

```python
self.harnesses = HarnessRepository(conn)
self.assets = AssetRepository(conn)
```

Add methods:

```python
    def create_harness(self, name: str, description: str = ""):
        with transaction(self.conn):
            return self.harnesses.create(name, description)

    def list_harnesses(self):
        return self.harnesses.list_harnesses()

    def list_assets_by_type(self, asset_type: str):
        return self.assets.list_by_type(asset_type)
```

- [ ] **Step 5: Update visible UI terms**

In `src/skillpkg/gui/main_window.py`:

- Window title should be `Harness Manager`.
- Main title should be `Harness Manager`.
- Main navigation should include Chinese labels with asset types: `Harness`, `AGENTS.md`, `MCP`, `Skills`.
- Existing Chinese UI requirement remains; use labels such as `Harness`, `AGENTS.md`, `MCP`, and `Skills` only as product terms.
- Do not add Hook as active navigation.

- [ ] **Step 6: Run tests**

Run: `pytest tests/test_harness_controller.py tests/test_gui_localization.py -q`

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add src/skillpkg/gui/controllers.py src/skillpkg/gui/main_window.py tests/test_harness_controller.py tests/test_gui_localization.py
git commit -m "feat: add harness controller and terminology"
```

---

### Task 5: Associate Assets With Harnesses

**Files:**
- Modify: `src/skillpkg/gui/controllers.py`
- Test: `tests/test_harness_assets_flow.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_harness_assets_flow.py`:

```python
from __future__ import annotations

from skillpkg.app_paths import AppPaths
from skillpkg.db import connect
from skillpkg.gui.controllers import MainController


def test_controller_adds_asset_to_harness(app_root, tmp_path):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    controller = MainController(app_root, conn)
    harness = controller.create_harness("代码审查", "")
    source = tmp_path / "AGENTS.md"
    source.write_text("# Rules\n", encoding="utf-8")
    asset = controller.import_agents_md_asset(source, "规则")

    controller.add_asset_to_harness(harness.id, asset.id, asset.type)

    assets = controller.list_harness_assets(harness.id)
    assert [item.id for item in assets] == [asset.id]
```

- [ ] **Step 2: Run test and verify failure**

Run: `pytest tests/test_harness_assets_flow.py -q`

Expected: FAIL because controller methods do not exist.

- [ ] **Step 3: Add controller methods**

Modify `src/skillpkg/gui/controllers.py`:

```python
    def import_agents_md_asset(self, source_file: Path | str, name: str):
        return self.service.import_agents_md_asset(Path(source_file), name, "custom")

    def import_mcp_asset(self, source_file: Path | str, name: str):
        return self.service.import_mcp_asset(Path(source_file), name, "custom")

    def add_asset_to_harness(self, harness_id: str, asset_id: str, asset_type: str) -> None:
        current = self.harnesses.list_assets(harness_id)
        with transaction(self.conn):
            self.harnesses.add_asset(harness_id, asset_id, asset_type, len(current) + 1)

    def list_harness_assets(self, harness_id: str):
        return self.harnesses.list_assets(harness_id)
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_harness_assets_flow.py tests/test_asset_imports.py -q`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/skillpkg/gui/controllers.py tests/test_harness_assets_flow.py
git commit -m "feat: associate assets with harnesses"
```

---

### Task 6: Full Regression And Documentation Update

**Files:**
- Modify: `README.md`
- Modify: `AGENTS.md` only if the user approves wording changes before this task starts.

- [ ] **Step 1: Update README product name and scope**

Modify `README.md` to include:

```markdown
# Harness Manager

Windows desktop GUI for managing task harnesses. A harness can include AGENTS.md instructions, MCP configuration assets, and skills. Hook support is deferred.
```

Keep existing development and build commands.

- [ ] **Step 2: Run full verification**

Run: `pytest -q`

Expected: PASS.

Run: `python -m compileall -q src tests`

Expected: exit code 0.

Run: `python -c "from skillpkg.gui.main_window import MainWindow; print('gui import ok')"`

Expected: prints `gui import ok`.

- [ ] **Step 3: Check git status**

Run: `git status --short`

Expected: only intended files changed.

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: describe harness manager scope"
```

---

## Final Verification Checklist

- [ ] Existing tests pass with `pytest -q`.
- [ ] `python -m compileall -q src tests` succeeds.
- [ ] GUI import check succeeds.
- [ ] Existing skill import-source tests still pass.
- [ ] Existing install/uninstall tests still pass.
- [ ] Harness and Asset repository tests pass.
- [ ] AGENTS.md and MCP asset import tests pass.
- [ ] No active Hook UI or service behavior is introduced.

## Spec Coverage Self-Review

- Product shift to Harness Manager: covered by Task 4 and Task 6.
- Additive Harness/Asset model: covered by Task 1 and Task 2.
- Preserve existing skill flow: protected by regression commands in Tasks 3 and 6.
- AGENTS.md asset import: covered by Task 3 and Task 5.
- MCP asset import: covered by Task 3 and Task 5.
- Hook deferred: explicitly excluded from tasks and final checklist.
- SQLite remains source of truth: covered by Task 2.
- GUI remains thin: controller methods in Tasks 4 and 5 call services/repositories.
