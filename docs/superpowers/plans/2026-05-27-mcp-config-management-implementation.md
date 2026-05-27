# MCP Config Management Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add user-managed MCP configuration assets with create, edit, JSON validation, listing, and task-suite membership actions.

**Architecture:** Reuse the existing `assets` table with `type = 'mcp'`; store MCP metadata in `metadata_json` and the full JSON config as `assets/mcp/<asset_id>/mcp.json`. Keep business logic in services/repositories/controllers and keep PySide6 code as a thin presentation layer.

**Tech Stack:** Python 3.11+, PySide6/Qt Widgets, SQLite via `sqlite3`, pytest.

---

## File Structure

- Modify `src/skillpkg/repositories.py`: add asset lookup helpers for duplicate MCP names.
- Modify `src/skillpkg/services.py`: add create/update MCP config asset methods with JSON validation and safe file writes.
- Modify `src/skillpkg/gui/controllers.py`: expose MCP config create/update operations.
- Modify `src/skillpkg/gui/dialogs.py`: add MCP config editor dialog and JSON formatting helper behavior.
- Modify `src/skillpkg/gui/main_window.py`: update MCP tab/list behavior and card actions.
- Modify tests in `tests/`: cover service, controller, and GUI text contracts.

---

### Task 1: Add MCP Config Service Behavior

**Files:**
- Modify: `src/skillpkg/repositories.py`
- Modify: `src/skillpkg/services.py`
- Test: `tests/test_asset_imports.py`

- [ ] **Step 1: Write failing tests**

Add tests for creating an MCP config, rejecting invalid JSON, and editing an existing config.

- [ ] **Step 2: Verify RED**

Run:

```powershell
pytest tests/test_asset_imports.py -q
```

Expected: fail because `create_mcp_config_asset` and `update_mcp_config_asset` do not exist.

- [ ] **Step 3: Implement repository and service methods**

Add an `AssetRepository.find_by_type_and_name(asset_type, name)` helper. Add service methods that parse JSON, write `mcp.json`, calculate fingerprint, and upsert the asset.

- [ ] **Step 4: Verify GREEN**

Run:

```powershell
pytest tests/test_asset_imports.py -q
```

Expected: pass.

- [ ] **Step 5: Commit**

```powershell
git add src/skillpkg/repositories.py src/skillpkg/services.py tests/test_asset_imports.py
git commit -m "feat: manage mcp config assets"
```

---

### Task 2: Expose MCP Config Operations To GUI Controller

**Files:**
- Modify: `src/skillpkg/gui/controllers.py`
- Test: `tests/test_harness_controller.py`

- [ ] **Step 1: Write failing controller test**

Add a test that calls `MainController.create_mcp_config_asset()` and verifies the asset appears in `list_assets_by_type("mcp")`.

- [ ] **Step 2: Verify RED**

Run:

```powershell
pytest tests/test_harness_controller.py -q
```

Expected: fail because the controller method does not exist.

- [ ] **Step 3: Implement controller wrapper methods**

Add `create_mcp_config_asset(...)` and `update_mcp_config_asset(...)` that delegate to `SkillPkgService`.

- [ ] **Step 4: Verify GREEN**

Run:

```powershell
pytest tests/test_harness_controller.py -q
```

Expected: pass.

- [ ] **Step 5: Commit**

```powershell
git add src/skillpkg/gui/controllers.py tests/test_harness_controller.py
git commit -m "feat: expose mcp config controller"
```

---

### Task 3: Add MCP Editor Dialog And MCP List Actions

**Files:**
- Modify: `src/skillpkg/gui/dialogs.py`
- Modify: `src/skillpkg/gui/main_window.py`
- Test: `tests/test_gui_navigation.py`
- Test: `tests/test_gui_localization.py`

- [ ] **Step 1: Write failing GUI contract tests**

Assert the GUI source contains `新建 MCP 配置`, `编辑`, `完整 JSON 配置`, `格式化`, and `MCP 标题（唯一）`.

- [ ] **Step 2: Verify RED**

Run:

```powershell
pytest tests/test_gui_navigation.py tests/test_gui_localization.py -q
```

Expected: fail because the dialog and new MCP page actions do not exist.

- [ ] **Step 3: Implement dialog and list actions**

Add an MCP config dialog with type chips, text fields, client checkboxes, JSON editor, format button, and save/cancel. In the MCP list, show cards with `编辑`, `加入套件`, and `移出套件`.

- [ ] **Step 4: Verify GREEN**

Run:

```powershell
pytest tests/test_gui_navigation.py tests/test_gui_localization.py -q
```

Expected: pass.

- [ ] **Step 5: Commit**

```powershell
git add src/skillpkg/gui/dialogs.py src/skillpkg/gui/main_window.py tests/test_gui_navigation.py tests/test_gui_localization.py
git commit -m "feat: add mcp config editor ui"
```

---

### Task 4: Full Verification

**Files:**
- No source changes expected.

- [ ] **Step 1: Run full test suite**

```powershell
pytest -q
```

Expected: all tests pass.

- [ ] **Step 2: Run compile check**

```powershell
python -m compileall -q src tests
```

Expected: exit code 0.

- [ ] **Step 3: Run GUI import check**

```powershell
python -c "from skillpkg.gui.main_window import MainWindow; print('gui import ok')"
```

Expected: prints `gui import ok`.

---

## Self-Review

- Spec coverage: create/edit MCP config, JSON validation, metadata, file storage, list display, and suite membership actions are covered.
- Scope control: no automatic MCP discovery, no live config writes, no MCP server health check.
- TDD: each implementation task starts with failing tests.
