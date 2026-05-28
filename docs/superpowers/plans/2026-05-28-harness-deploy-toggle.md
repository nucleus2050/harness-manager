# Harness Deploy Toggle Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make each task suite deployment button stateful: click once to deploy, click again to撤销部署.

**Architecture:** Reuse `install_records` as the deployment state source, storing `harness_id` in `package_id` for harness deployments. The service records fingerprints on deploy, safely removes unchanged deployed skills on撤销, and the GUI queries active state to style each client icon.

**Tech Stack:** Python 3.11, PySide6 Qt Widgets, SQLite, pytest.

---

### Task 1: Service and Controller State APIs

**Files:**
- Modify: `src/harness_manager/repositories.py`
- Modify: `src/harness_manager/services.py`
- Modify: `src/harness_manager/gui/controllers.py`
- Test: `tests/test_harness_assets_flow.py`

- [ ] **Step 1: Add failing tests**

Add tests that deploy a harness, confirm active state, toggle撤销, and confirm files are removed safely.

- [ ] **Step 2: Implement repository/service/controller methods**

Add active install lookup, write install records in `deploy_harness`, add `undeploy_harness`, and expose `harness_deploy_status` / `toggle_harness_deploy` through controller.

- [ ] **Step 3: Run targeted tests**

Run: `pytest tests/test_harness_assets_flow.py -q`
Expected: PASS.

### Task 2: GUI Stateful Deployment Buttons

**Files:**
- Modify: `src/harness_manager/gui/main_window.py`
- Modify: `src/harness_manager/gui/styles.py`
- Test: `tests/test_gui_navigation.py`
- Test: `tests/test_gui_styles.py`

- [ ] **Step 1: Add source-level GUI assertions**

Assert the main window calls `harness_deploy_status`, uses checked deploy object names, and calls a toggle method instead of one-way deploy.

- [ ] **Step 2: Implement UI state rendering**

When building each harness card, query status for each client and scope, set tooltip to deploy/撤销, and style active icons with `HarnessDeployIconActive`.

- [ ] **Step 3: Run targeted GUI tests**

Run: `pytest tests/test_gui_navigation.py tests/test_gui_styles.py -q`
Expected: PASS.

### Task 3: Verification and Commit

**Files:**
- Verify only

- [ ] **Step 1: Run full verification**

Run:
`pytest -q`
`python -m compileall -q src tests`
`python -c "from harness_manager.gui.main_window import MainWindow; print('gui import ok')"`
Expected: all pass.

- [ ] **Step 2: Commit changes**

Run:
`git add docs/superpowers/plans/2026-05-28-harness-deploy-toggle.md src/harness_manager/repositories.py src/harness_manager/services.py src/harness_manager/gui/controllers.py src/harness_manager/gui/main_window.py src/harness_manager/gui/styles.py tests/test_harness_assets_flow.py tests/test_gui_navigation.py tests/test_gui_styles.py`
`git commit -m "feat: toggle harness deployments"`
