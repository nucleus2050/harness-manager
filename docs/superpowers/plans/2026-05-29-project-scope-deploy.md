# Project Scope Deploy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let users select a project folder and deploy harness assets into that project using each agent's project-level conventions.

**Architecture:** Add a deployment layout resolver in `services.py` so global and project targets can map to different skill/config destinations. Store active deploy records against the resolved skill root while writing file assets to layout-specific files.

**Tech Stack:** Python 3.11+, PySide6, sqlite3, pytest.

---

### Task 1: Project Layout Tests

**Files:**
- Modify: `tests/test_harness_assets_flow.py`

- [ ] Add failing tests for Codex, Claude Code and OpenCode project deployments.
- [ ] Run the new tests and confirm they fail because project paths are not implemented.

### Task 2: Service Layout Resolver

**Files:**
- Modify: `src/harness_manager/services.py`
- Modify: `src/harness_manager/gui/controllers.py`

- [ ] Add a scope-aware deploy layout resolver.
- [ ] Keep global behavior unchanged.
- [ ] Make project deployment write to the documented project paths.
- [ ] Run project deployment tests and existing harness asset tests.

### Task 3: GUI Project Folder Selection

**Files:**
- Modify: `src/harness_manager/gui/main_window.py`
- Modify: `src/harness_manager/gui/dialogs.py`
- Modify: GUI tests as needed.

- [ ] Add project folder chooser text.
- [ ] Store selected project root in the main window.
- [ ] Prompt for project folder when entering project mode or deploying without a selected project.
- [ ] Use project root when building deployment target paths.

### Task 4: Verification and Commit

**Files:**
- Verify all modified files.

- [ ] Run `pytest -q`.
- [ ] Run `python -m compileall -q src tests`.
- [ ] Commit the implementation.
