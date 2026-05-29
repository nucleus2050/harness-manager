# Multi Project Management Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add persistent multi-project management so harness deployments can be viewed and controlled per global scope or per project.

**Architecture:** Introduce a `Project` model, SQLite `projects` table, and repository/controller APIs. Replace the single transient GUI project path with a selected project record and reuse the existing scope-aware deploy layout for project deployments.

**Tech Stack:** Python 3.11+, sqlite3, PySide6, pytest.

---

## File Map

- Modify: `src/harness_manager/models.py` — add `Project` dataclass.
- Modify: `src/harness_manager/db.py` — add `projects` table.
- Modify: `src/harness_manager/repositories.py` — add `ProjectRepository`.
- Modify: `src/harness_manager/gui/controllers.py` — expose project CRUD and project-aware deploy helpers.
- Modify: `src/harness_manager/gui/dialogs.py` — add project editor and project manager dialogs.
- Modify: `src/harness_manager/gui/main_window.py` — replace transient project path with project selector UI.
- Modify: `tests/` — add repository, controller, service, and GUI contract tests.

---

### Task 1: Project Persistence

**Files:**
- Modify: `src/harness_manager/models.py`
- Modify: `src/harness_manager/db.py`
- Modify: `src/harness_manager/repositories.py`
- Test: create `tests/test_projects.py`

- [ ] **Step 1: Write failing repository tests**

Add tests for project create/list/update/delete and duplicate path rejection.

```python
from pathlib import Path

import pytest

from harness_manager.app_paths import AppPaths
from harness_manager.db import connect
from harness_manager.repositories import ProjectRepository


def test_project_repository_creates_lists_and_updates_projects(app_root, tmp_path):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    repo = ProjectRepository(conn)
    project_path = tmp_path / "demo"
    project_path.mkdir()

    project = repo.create("Demo", project_path, "说明")
    updated = repo.update(project.id, "Demo 2", project_path, "新说明")

    assert updated.name == "Demo 2"
    assert updated.path == project_path.resolve()
    assert repo.list_all()[0].id == project.id


def test_project_repository_rejects_duplicate_paths(app_root, tmp_path):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    repo = ProjectRepository(conn)
    project_path = tmp_path / "demo"
    project_path.mkdir()

    repo.create("Demo", project_path, "")

    with pytest.raises(ValueError, match="项目路径已存在"):
        repo.create("Other", project_path, "")
```

- [ ] **Step 2: Run failing tests**

Run: `pytest -q tests/test_projects.py`

Expected: fail because `ProjectRepository` does not exist.

- [ ] **Step 3: Implement persistence**

Add `Project` to `models.py`, `projects` schema to `db.py`, and `ProjectRepository` to `repositories.py`.

- [ ] **Step 4: Verify**

Run: `pytest -q tests/test_projects.py`

Expected: pass.

- [ ] **Step 5: Commit**

```powershell
git add src/harness_manager/models.py src/harness_manager/db.py src/harness_manager/repositories.py tests/test_projects.py
git commit -m "feat: add project persistence"
```

### Task 2: Controller APIs and Project Deploy Status

**Files:**
- Modify: `src/harness_manager/gui/controllers.py`
- Test: `tests/test_projects.py`

- [ ] **Step 1: Write failing controller tests**

Add a test that creates two projects, deploys the same harness to one project, and verifies the other project remains undeployed.

```python
def test_controller_tracks_harness_deployments_per_project(app_root, tmp_path, sample_skill):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    controller = MainController(app_root, conn)
    first_path = tmp_path / "first"
    second_path = tmp_path / "second"
    first_path.mkdir()
    second_path.mkdir()
    first = controller.create_project("First", first_path, "")
    second = controller.create_project("Second", second_path, "")
    harness = controller.create_harness("项目套件", "")
    skill = controller.import_skill_directory(sample_skill, "codex")
    controller.add_asset_to_harness(harness.id, skill.id, "skill")

    controller.toggle_harness_deploy(harness.id, "codex", first.path, scope="project")

    assert controller.harness_deploy_status(harness.id, "codex", first.path, scope="project")
    assert not controller.harness_deploy_status(harness.id, "codex", second.path, scope="project")
```

- [ ] **Step 2: Run failing test**

Run: `pytest -q tests/test_projects.py::test_controller_tracks_harness_deployments_per_project`

Expected: fail because controller project methods do not exist.

- [ ] **Step 3: Implement controller APIs**

Add `self.projects = ProjectRepository(conn)` and methods `create_project`, `update_project`, `delete_project`, `list_projects`, `get_project`.

- [ ] **Step 4: Verify**

Run: `pytest -q tests/test_projects.py tests/test_harness_assets_flow.py`

Expected: pass.

- [ ] **Step 5: Commit**

```powershell
git add src/harness_manager/gui/controllers.py tests/test_projects.py
git commit -m "feat: expose project management controller APIs"
```

### Task 3: Project Dialogs

**Files:**
- Modify: `src/harness_manager/gui/dialogs.py`
- Test: `tests/test_gui_navigation.py`

- [ ] **Step 1: Write failing GUI contract tests**

Assert that `ProjectEditorDialog`, `ProjectManagerDialog`, and Chinese/English text keys exist.

- [ ] **Step 2: Run failing test**

Run: `pytest -q tests/test_gui_navigation.py`

Expected: fail on missing dialog tokens.

- [ ] **Step 3: Implement dialogs**

Implement project editor with name, path, description, folder picker, save/cancel. Implement project manager list with edit/delete actions.

- [ ] **Step 4: Verify**

Run: `pytest -q tests/test_gui_navigation.py`

Expected: pass.

- [ ] **Step 5: Commit**

```powershell
git add src/harness_manager/gui/dialogs.py tests/test_gui_navigation.py
git commit -m "feat: add project management dialogs"
```

### Task 4: Main Window Project Selector

**Files:**
- Modify: `src/harness_manager/gui/main_window.py`
- Test: `tests/test_gui_navigation.py`

- [ ] **Step 1: Write failing GUI contract tests**

Assert that the main window uses `selected_project_id`, `project_selector`, `add_project`, and `manage_projects`, and no longer relies on `selected_project_root` as the main state.

- [ ] **Step 2: Run failing test**

Run: `pytest -q tests/test_gui_navigation.py`

Expected: fail until UI tokens exist.

- [ ] **Step 3: Implement selector UI**

Add deployment scope row to harness page: global/project selector, project dropdown, add/manage buttons. When project scope has no selected project, deployment is disabled or prompts to add project.

- [ ] **Step 4: Wire deployment target**

Update `_deploy_target_path` and `_toggle_harness_deployment` to resolve the selected project record path when `deploy_scope == "project"`.

- [ ] **Step 5: Verify**

Run: `pytest -q tests/test_gui_navigation.py tests/test_projects.py tests/test_harness_assets_flow.py`

Expected: pass.

- [ ] **Step 6: Commit**

```powershell
git add src/harness_manager/gui/main_window.py tests/test_gui_navigation.py
git commit -m "feat: add multi-project deploy selector"
```

### Task 5: Deployment Location Summary

**Files:**
- Modify: `src/harness_manager/services.py` or `src/harness_manager/gui/controllers.py`
- Modify: `src/harness_manager/gui/main_window.py`
- Test: `tests/test_projects.py`, `tests/test_gui_navigation.py`

- [ ] **Step 1: Write failing tests**

Add controller test returning deployment locations for a harness across global and projects. Add GUI contract test for `deployment_locations` section.

- [ ] **Step 2: Implement summary API**

Add controller method that combines active deploy records with project records and returns grouped status per location/client.

- [ ] **Step 3: Render summary**

Show a read-only “部署位置” section in harness details.

- [ ] **Step 4: Verify**

Run: `pytest -q tests/test_projects.py tests/test_gui_navigation.py`

Expected: pass.

- [ ] **Step 5: Commit**

```powershell
git add src/harness_manager/gui/controllers.py src/harness_manager/gui/main_window.py tests/test_projects.py tests/test_gui_navigation.py
git commit -m "feat: show harness deployment locations"
```

### Task 6: Full Verification

**Files:**
- Verify all modified files.

- [ ] **Step 1: Run full tests**

Run: `pytest -q`

Expected: all tests pass.

- [ ] **Step 2: Compile**

Run: `python -m compileall -q src tests`

Expected: exit code 0.

- [ ] **Step 3: Push**

```powershell
git push origin master
```
