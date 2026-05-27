# AGENTS.md

## Project Overview

This project is evolving from a Skill Package Manager into Harness Manager.

Harness Manager is a local Windows desktop application for managing the resources needed to complete a task. A harness is a reusable task toolkit. In the current design direction, a harness can include:

- `AGENTS.md` instructions
- MCP configuration assets
- Skill assets

Hook support is intentionally deferred because Codex, Claude Code, OpenCode, and other tools differ significantly in hook models and installation conventions.

## Core Product Design

### Harness

A Harness represents the complete reusable context and tooling for a task or workflow, such as code review, frontend development, writing, data analysis, or a project-specific workflow.

A Harness is the successor to the earlier package concept. Existing package behavior should gradually migrate toward Harness behavior without breaking the working skill-management flow.

### Asset

An Asset is a managed reusable resource. The first upgraded asset types are:

- `agents_md`: project or task instructions stored as AGENTS.md content.
- `mcp`: MCP server configuration snippets or files.
- `skill`: existing managed skill directories.

The future `hook` asset type is out of scope until its cross-tool behavior is designed.

### Import Sources

The app supports importing assets from:

- Codex default/custom directories
- Claude Code default/custom directories
- OpenCode default/custom directories
- user-defined custom directories
- offline harness packages

For known tool directories, import should use the configured path directly. Ask the user to choose a directory only when automatic detection or stored configuration is missing or invalid.

## Architecture

The app uses a small layered Python architecture:

- `src/skillpkg/app_paths.py`: resolves app-root runtime directories.
- `src/skillpkg/db.py`: SQLite schema initialization and transaction handling.
- `src/skillpkg/repositories.py`: database CRUD access.
- `src/skillpkg/services.py`: core filesystem/database use cases.
- `src/skillpkg/file_ops.py`: safe copy/remove/archive helpers.
- `src/skillpkg/fingerprint.py`: deterministic asset fingerprinting.
- `src/skillpkg/client_detection.py`: default path detection for supported tools.
- `src/skillpkg/gui/`: PySide6 user interface, dialogs, styles, and controller wiring.
- `tests/`: pytest coverage for paths, database, services, archives, GUI text/style contracts, and import-source behavior.

Core services should stay independent from Qt. GUI code should call controllers/services instead of performing database or filesystem operations directly.

## Technology Stack

- Language: Python 3.11+
- GUI: PySide6 / Qt Widgets
- Database: SQLite via the Python standard library `sqlite3`
- Tests: pytest
- Packaging: PyInstaller through `scripts/build.ps1`
- Runtime data: stored under the application working directory

## Runtime Layout Direction

Current runtime layout is still skill-oriented in places. The target Harness Manager layout is:

```text
HarnessManager/
  data/
    harness.db
  assets/
    agents/
      <asset_id>/AGENTS.md
    mcp/
      <asset_id>/mcp.json
    skills/
      <asset_id>/...
  exports/
    <harness-name>.harness.zip
  config/
    settings.json
```

Existing `skills/` and `.skillpkg.zip` behavior may remain during migration, but new design work should move toward `assets/` and `.harness.zip`.

## Development Rules For Agents

1. Keep this `AGENTS.md` self-maintaining. When the technical architecture, product design, or major functionality changes, propose an update to this file. Do not write the update until the user explicitly agrees.
2. Every completed task must be committed to git. Before committing, run the relevant verification command for the change and confirm the working tree state.
3. Preserve the current working skill flow while migrating toward Harness Manager. Avoid large rewrites that break existing import, install, uninstall, export, or test behavior.
4. Keep core logic testable without PySide6. Business logic belongs in services/repositories; GUI code should stay thin.
5. Treat filesystem operations as high risk. Validate paths, avoid path traversal, avoid destructive deletes outside recorded install paths, and keep fingerprint checks for uninstall safety.
6. Keep user-facing UI text in Chinese unless the user asks otherwise.
7. Do not implement hook support until its cross-tool model is explicitly designed and approved.

## Verification Expectations

For ordinary code changes, run:

```powershell
pytest -q
python -m compileall -q src tests
```

For GUI-only changes where runtime launch is not practical, also verify imports, for example:

```powershell
python -c "from skillpkg.gui.main_window import MainWindow; print('gui import ok')"
```

For build-related changes, validate `scripts/build.ps1` syntax and PyInstaller invocation.
