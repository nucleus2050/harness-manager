# Harness Manager Upgrade Design

## Goal

Upgrade the current Skill Package Manager into Harness Manager: a desktop tool for managing the set of resources needed to complete a task. A harness is a reusable task toolkit that can include AGENTS.md instructions, MCP configuration, and skills. Hooks are intentionally deferred because each target tool handles hooks differently.

## Confirmed Direction

- Use a gradual migration instead of a one-shot rewrite.
- Rename the product from Skill Package Manager to Harness Manager.
- Rename package-level concepts from Package to Harness.
- Generalize managed content from skills-only to typed assets.
- First upgraded scope includes three asset types:
  - `agents_md`
  - `mcp`
  - `skill`
- Defer hook support to a later phase.
- Preserve the current working skill import/install/uninstall behavior while introducing the broader model.
- Keep the app as a local Windows desktop application built with Python and PySide6.
- Keep SQLite in the app directory as the source of truth.

## Product Concepts

### Harness

A Harness represents the resources needed for a task or workflow.

Examples:

- Code Review Harness
- Frontend Development Harness
- Writing Harness
- Data Analysis Harness
- Project A Harness

A Harness can contain multiple assets, grouped by type.

```text
Harness
  - AGENTS.md assets
  - MCP assets
  - Skill assets
```

### Asset

An Asset is a managed reusable resource.

Asset types for this phase:

- `agents_md`: project or task instructions stored as AGENTS.md content.
- `mcp`: MCP server configuration snippets or files.
- `skill`: existing managed skill directories.

Deferred asset type:

- `hook`: future support only. It should not be implemented in this phase.

## Scope

### In Scope For This Upgrade

- Rename UI text to Harness Manager terminology.
- Introduce a generic asset model in the database.
- Treat existing skills as `asset.type = 'skill'`.
- Add asset library views for:
  - Harnesses
  - AGENTS.md
  - MCP
  - Skills
- Allow a Harness to contain assets of the three in-scope types.
- Preserve existing skill import sources:
  - Codex
  - Claude Code
  - OpenCode
  - custom directories
- Preserve skill installation/uninstallation to Codex, Claude Code, and OpenCode.
- Add AGENTS.md import and library visibility.
- Add MCP config import and library visibility.
- Support associating AGENTS.md and MCP assets with a Harness.
- Upgrade offline export/import format toward `.harness.zip`.

### Out Of Scope For This Upgrade

- Hook management.
- Automatic hook installation.
- Deep MCP config merging into tool-specific config files.
- Automatic conversion between different client formats.
- Cloud sync or team accounts.

## Directory Layout

Current runtime data should evolve from skills-only layout to asset-oriented layout.

```text
HarnessManager/
  data/
    harness.db
  assets/
    agents/
      <asset_id>/
        AGENTS.md
    mcp/
      <asset_id>/
        mcp.json
    skills/
      <asset_id>/
        ...skill content
  exports/
    <harness-name>.harness.zip
  config/
    settings.json
```

Compatibility note: the existing `skills/` directory can remain temporarily during migration. New code should prefer `assets/skills/` once migration is implemented.

## Database Model

### `harnesses`

Replaces the product concept currently named `packages`.

Columns:

- `id` text primary key
- `name` text unique
- `description` text
- `created_at` text
- `updated_at` text

Migration path:

- Existing `packages` rows become `harnesses` rows.

### `assets`

Generic asset table.

Columns:

- `id` text primary key
- `type` text, one of `agents_md`, `mcp`, `skill`
- `name` text
- `source_type` text nullable, such as `codex`, `claude_code`, `opencode`, `custom`, `offline`
- `relative_path` text
- `fingerprint` text
- `metadata_json` text
- `created_at` text
- `updated_at` text

Migration path:

- Existing `skills` rows become `assets` rows where `type = 'skill'`.
- Existing skill `relative_path` values remain valid until files are moved to `assets/skills/`.

### `harness_assets`

Many-to-many relationship between harnesses and assets.

Columns:

- `harness_id` text
- `asset_id` text
- `asset_type` text
- `sort_order` integer
- `created_at` text

Primary key: `(harness_id, asset_id)`.

Migration path:

- Existing `package_skills` rows become `harness_assets` rows where `asset_type = 'skill'`.

### `install_records`

Installation records should become asset-aware.

Columns should include:

- `id` text primary key
- `harness_id` text
- `asset_id` text
- `asset_type` text
- `target_type` text, such as `codex`, `claude_code`, `opencode`, `workspace`
- `target_path` text
- `installed_path` text
- `fingerprint` text
- `status` text
- `installed_at` text
- `uninstalled_at` text nullable

Compatibility note: existing install records for skills can be migrated by mapping `package_id` to `harness_id` and `skill_id` to `asset_id`.

## UI Design

### Navigation

Replace the current package/skill framing with Harness/Asset framing.

Primary sections:

```text
[Harness] [AGENTS.md] [MCP] [Skills]
```

Hooks should not appear in the first upgraded version except possibly as disabled future text in documentation.

### Left Sidebar

Keep the left sidebar for import sources and target context.

Content:

- Codex source
- Claude Code source
- OpenCode source
- custom import directories
- add custom directory action

The sidebar should continue to support selecting import sources.

### Harness View

Main area:

- Harness list
- create Harness
- import/export Harness
- selected Harness details

Details panel should show asset counts:

- AGENTS.md: N
- MCP: N
- Skills: N

Actions:

- add AGENTS.md asset
- add MCP asset
- add Skill asset
- install skill assets to selected client
- export Harness

### AGENTS.md Library View

Shows all managed AGENTS.md assets.

Each row should show:

- name
- source
- fingerprint short value
- relative path

Actions:

- import AGENTS.md file
- preview content
- associate with selected Harness

First version can import one AGENTS.md file at a time.

### MCP Library View

Shows all managed MCP assets.

Each row should show:

- name
- config file type or inferred format
- source
- fingerprint short value
- relative path

Actions:

- import MCP config file
- preview raw config
- associate with selected Harness

First version should avoid automatic merging into live client config.

### Skills Library View

This view is the current skill library, renamed and integrated into asset terminology.

Each row should show:

- skill name
- source
- asset id
- fingerprint short value

Actions:

- import from selected source
- associate with selected Harness

## Core Workflows

### Create Harness

1. User clicks create Harness.
2. User enters name and optional description.
3. App creates `harnesses` row.
4. Empty Harness is allowed.

### Import Skill Asset

Use the existing import source workflow.

1. User selects an import source.
2. If source path exists, app scans child directories and imports each as a skill asset.
3. If source path is missing, app prompts for a path and saves it.
4. App stores each imported skill as an `assets` row with `type = 'skill'`.
5. App copies files into the managed asset library.

### Import AGENTS.md Asset

1. User selects an AGENTS.md file.
2. App validates that it is a file.
3. App copies it to `assets/agents/<asset_id>/AGENTS.md`.
4. App calculates fingerprint.
5. App stores an `assets` row with `type = 'agents_md'`.

### Import MCP Asset

1. User selects an MCP config file.
2. App validates that it is a file.
3. App copies it to `assets/mcp/<asset_id>/<original-name>`.
4. App calculates fingerprint.
5. App stores an `assets` row with `type = 'mcp'`.

### Associate Asset With Harness

1. User selects a Harness.
2. User opens an asset library view.
3. User chooses an asset and clicks add to Harness.
4. App writes `harness_assets` row.

### Install Harness

First upgraded version should keep installation conservative.

- Skill assets: install to Codex, Claude Code, or OpenCode using existing safe copy/uninstall behavior.
- AGENTS.md assets: install to a user-selected workspace path as `AGENTS.md`.
- MCP assets: export or copy config snippets to a user-selected location. Avoid automatic merge in this phase.

## Offline Export Format

Use `.harness.zip`.

```text
example.harness.zip
  manifest.json
  assets/
    agents/<asset_id>/AGENTS.md
    mcp/<asset_id>/mcp.json
    skills/<asset_id>/...
```

Manifest shape:

```json
{
  "schema_version": 2,
  "harness": {
    "id": "harness-id",
    "name": "代码审查 Harness",
    "description": "代码审查任务工具包"
  },
  "assets": [
    {
      "id": "asset-id",
      "type": "skill",
      "name": "review-skill",
      "relative_path": "assets/skills/asset-id",
      "fingerprint": "sha256..."
    },
    {
      "id": "asset-id",
      "type": "agents_md",
      "name": "代码审查规则",
      "relative_path": "assets/agents/asset-id/AGENTS.md",
      "fingerprint": "sha256..."
    }
  ]
}
```

## Migration Strategy

Use additive migration first.

1. Add new tables: `harnesses`, `assets`, `harness_assets`.
2. Copy existing `packages` into `harnesses`.
3. Copy existing `skills` into `assets(type='skill')`.
4. Copy existing `package_skills` into `harness_assets`.
5. Keep old tables during transition for rollback and compatibility.
6. Update repositories/services to read from the new model.
7. Remove old code paths only after tests verify parity.

## Testing Strategy

### Unit Tests

- Create Harness with no assets.
- Import skill as asset.
- Import AGENTS.md as asset.
- Import MCP config as asset.
- Associate each asset type with Harness.
- Migrate packages to harnesses.
- Migrate skills to assets.

### Integration Tests

- Existing skill import/install/uninstall still works.
- Harness with skills exports and imports correctly.
- Harness with AGENTS.md exports and imports correctly.
- Harness with MCP exports and imports correctly.
- AGENTS.md install to workspace writes only expected path.
- MCP copy/export does not mutate live config unless explicitly selected.

### UI Checks

- Product title reads Harness Manager.
- Main navigation shows Harness, AGENTS.md, MCP, Skills.
- Hook is not shown as an active section.
- Existing custom import source workflow still works.
- Empty Harness creation works.

## Open Decisions For Later

- Exact MCP merge strategy per client.
- Hook model and installation behavior.
- Whether AGENTS.md can have multiple variants per Harness.
- Whether Harness install should support workspace profiles.
- Whether old `.skillpkg.zip` imports should remain supported after `.harness.zip` exists.
