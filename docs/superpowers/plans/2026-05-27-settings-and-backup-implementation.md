# Settings And Backup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add sidebar asset counts, a settings page, language preference storage, and full configuration import/export.

**Architecture:** Add a focused settings/backup service independent of Qt. Expose operations through `MainController`; keep `MainWindow` as presentation and dialog wiring.

**Tech Stack:** Python 3.11+, PySide6/Qt Widgets, SQLite, pytest, zipfile.

---

## Tasks

### Task 1: Settings And Backup Service

**Files:**
- Create: `src/skillpkg/settings.py`
- Test: `tests/test_settings_backup.py`

- [ ] Write failing tests for default settings, saving language, exporting config, and importing config.
- [ ] Implement `AppSettings`, `SettingsService`, `export_full_config`, and `import_full_config`.
- [ ] Run `pytest tests/test_settings_backup.py -q`.
- [ ] Commit `feat: add settings backup service`.

### Task 2: Controller Wiring

**Files:**
- Modify: `src/skillpkg/gui/controllers.py`
- Test: `tests/test_gui_controller.py`

- [ ] Write failing tests for controller settings and backup methods.
- [ ] Expose `get_settings`, `save_language`, `export_full_config`, and `import_full_config`.
- [ ] Run `pytest tests/test_gui_controller.py tests/test_settings_backup.py -q`.
- [ ] Commit `feat: expose settings backup controller`.

### Task 3: GUI Settings Page And Counts

**Files:**
- Modify: `src/skillpkg/gui/main_window.py`
- Modify: `src/skillpkg/gui/dialogs.py`
- Test: `tests/test_gui_navigation.py`
- Test: `tests/test_gui_localization.py`

- [ ] Write failing GUI contract tests for MCP/AGENTS.md counts, settings entry, language buttons, and import/export buttons.
- [ ] Add sidebar 2x2 stats and settings page.
- [ ] Wire language save, config export, and config import actions.
- [ ] Run GUI tests.
- [ ] Commit `feat: add settings page`.

### Task 4: Full Verification

- [ ] Run `pytest -q`.
- [ ] Run `python -m compileall -q src tests`.
- [ ] Run GUI import check.
