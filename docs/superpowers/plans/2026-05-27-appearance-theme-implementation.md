# Appearance Theme Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add light, dark, and system-following appearance themes to the PySide6 settings page.

**Architecture:** Persist the theme in the existing JSON settings service. Keep theme resolution in GUI/style code so core settings remain Qt-free. Reuse the current settings page and button object-name styling pattern.

**Tech Stack:** Python 3.11+, PySide6 Qt Widgets, pytest, sqlite3-backed controller wiring.

---

### Task 1: Settings Model

**Files:**
- Modify: `tests/test_settings_backup.py`
- Modify: `src/skillpkg/settings.py`

- [ ] Add failing tests for default `theme == "system"`, `save_theme("dark")`, and preserving language when saving theme.
- [ ] Run `pytest tests/test_settings_backup.py -q` and confirm the new tests fail because `theme` and `save_theme` are missing.
- [ ] Add `theme` to `AppSettings`, validate values, preserve loaded settings when saving language/theme.
- [ ] Run `pytest tests/test_settings_backup.py -q` and confirm it passes.

### Task 2: Controller And Styles

**Files:**
- Modify: `tests/test_gui_controller.py`
- Modify: `tests/test_gui_styles.py`
- Modify: `src/skillpkg/gui/controllers.py`
- Modify: `src/skillpkg/gui/styles.py`

- [ ] Add failing tests for `controller.save_theme("dark")` and different light/dark stylesheet colors.
- [ ] Run targeted tests and confirm they fail.
- [ ] Add `save_theme` to `MainController` and extend `build_stylesheet(theme)` to support `light`, `dark`, and `system`.
- [ ] Run targeted tests and confirm they pass.

### Task 3: Settings Page UI

**Files:**
- Modify: `tests/test_gui_navigation.py`
- Modify: `src/skillpkg/gui/main_window.py`

- [ ] Add failing source contract tests for “外观主题”“浅色”“深色”“跟随系统” and `_save_theme`.
- [ ] Run `pytest tests/test_gui_navigation.py::test_settings_page_text_and_actions_exist -q` and confirm it fails.
- [ ] Add theme buttons, initialize theme from saved settings, apply stylesheet after saving, and polish buttons.
- [ ] Run GUI/navigation/style/controller/settings tests and confirm they pass.

### Task 4: Final Verification And Commit

**Files:**
- Modify: project verification output only

- [ ] Run `pytest -q`.
- [ ] Run `python -m compileall -q src tests`.
- [ ] Run `python -c "from skillpkg.gui.main_window import MainWindow; print('gui import ok')"`.
- [ ] Check `git status --short` and ensure ignored build outputs are no longer tracked.
- [ ] Commit all intentional changes with a feature message.
