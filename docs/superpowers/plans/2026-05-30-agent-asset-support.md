# Agent Asset Support Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add first-phase Agent assets to Harness Manager so Codex, Claude Code, and OpenCode agent definition files can be imported, joined to harnesses, deployed, undeployed, and exported/imported without breaking existing AGENTS.md, MCP, and Skill flows.

**Architecture:** Treat `agent` as a generic file asset with metadata describing target client, format, source filename, and deploy filename. Deployment copies the managed agent file to client-specific `agents/` directories and tracks it with the existing harness deploy record/fingerprint safety model. GUI adds an Agent library tab and harness details group while keeping business logic in services/controllers.

**Tech Stack:** Python 3.11+, sqlite3 repositories, PySide6 Qt Widgets, pytest.

---

## File Map

- Modify: `src/harness_manager/asset_paths.py` - add `agent` storage under `assets/agent_configs/<asset_id>`.
- Modify: `src/harness_manager/services.py` - add agent metadata helpers, import/create/update methods, deploy layout `agent_root`, destination/matching/undeploy support, offline manifest support.
- Modify: `src/harness_manager/gui/controllers.py` - expose Agent CRUD methods.
- Modify: `src/harness_manager/gui/dialogs.py` - add Agent create/edit/import metadata dialogs if needed.
- Modify: `src/harness_manager/gui/main_window.py` - add Agent navigation, toolbar, summaries, item display, details grouping.
- Modify: `tests/test_asset_imports.py` - service-level Agent import/create tests.
- Modify: `tests/test_harness_assets_flow.py` or create `tests/test_agent_assets_flow.py` - deploy/undeploy/export/import Agent tests.
- Modify: `tests/test_gui_navigation.py` and localization tests - GUI contract for Agent tab and Chinese text.
- Modify: `AGENTS.md` - update project map after explicit user approval already given in chat.

## Task 1: Agent asset path and service import

- [ ] Write failing tests in `tests/test_asset_imports.py` for importing a Codex TOML Agent and creating a Claude/OpenCode Markdown Agent.
- [ ] Run `python -m pytest -q tests/test_asset_imports.py::test_import_agent_asset_stores_metadata tests/test_asset_imports.py::test_create_agent_asset_writes_content_and_metadata` and confirm failure.
- [ ] Add `agent` path mapping in `src/harness_manager/asset_paths.py`.
- [ ] Add `HarnessService.import_agent_asset` and `HarnessService.create_agent_asset` in `src/harness_manager/services.py` using `assets/agent_configs/<id>/agent.<ext>` and metadata keys: `client_type`, `agent_format`, `agent_name`, `description`, `entry_filename`, `deploy_filename`.
- [ ] Re-run the two tests and confirm pass.

## Task 2: Agent deployment and undeployment

- [ ] Write failing tests for deploying one Agent asset to global and project targets for Codex, Claude Code, and OpenCode.
- [ ] Run focused tests and confirm expected failure.
- [ ] Extend `DeployLayout` with `agent_root`.
- [ ] Map agent roots: Codex global `config_root/agents`, Codex project `.codex/agents`; Claude global `config_root/agents`, Claude project `.claude/agents`; OpenCode global `config_root/agents`, OpenCode project `.opencode/agents`.
- [ ] Add `_agent_deploy_filename`, copy deployment, fingerprint match, and undeploy removal using existing record safety checks.
- [ ] Re-run focused tests and confirm pass.

## Task 3: Offline harness import/export

- [ ] Write failing test that exports a harness containing `agent`, inspects manifest type, imports it into a fresh app root, and confirms the Agent asset remains joinable/deployable.
- [ ] Allow `agent` in `_validated_offline_harness_manifest`.
- [ ] Ensure generic file asset export/import preserves metadata and fingerprint.
- [ ] Re-run focused test and confirm pass.

## Task 4: GUI Agent library

- [ ] Write failing GUI contract tests for `Agent` navigation button, toolbar, summary, list item metadata, and harness detail group `已加入的 Agent`.
- [ ] Add UI text and button wiring in `main_window.py`.
- [ ] Add controller methods for Agent create/import/update.
- [ ] Add minimal dialogs for Agent content creation/editing only if required by the toolbar.
- [ ] Re-run GUI contract tests and confirm pass.

## Task 5: Documentation and full verification

- [ ] Update `AGENTS.md` to include `agent` asset type and `assets/agent_configs/` runtime directory.
- [ ] Run `python -m pytest -q`.
- [ ] Run `python -m compileall -q src tests`.
- [ ] Run `python -c "from harness_manager.gui.main_window import MainWindow; print('gui import ok')"`.
- [ ] Check `git status --short --branch`.
- [ ] Commit all changes.
