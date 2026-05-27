# Skill Package Manager Design

## Goal

Build a Windows desktop GUI tool for managing skills across Codex, Claude Code, and OpenCode. The tool keeps a unified local skill library, lets users group skills into packages, and installs or uninstalls a package's skills into a selected client with one action.

## Confirmed Decisions

- Application type: local Windows desktop app.
- Technology stack: Python with PySide6.
- Database: SQLite stored under the tool installation directory.
- Skill storage: real skill files live under the tool installation directory in `skills/`.
- Package model: a package is an abstract grouping stored in SQLite, not a normal directory.
- Client support: Codex, Claude Code, and OpenCode.
- Client paths: automatically detect default skill directories first; allow manual override when detection fails or users want a custom path.
- Skill format conversion: no conversion. Skills are copied as-is. The user is responsible for importing skills that already match the target client's expected format.
- Offline sharing: support exporting a package as a zip that contains a manifest and complete skill contents.

## Directory Layout

```text
SkillPkgManager/
  SkillPkgManager.exe
  data/
    skillpkg.db
  skills/
    <skill_id>/
      ...complete skill content
  exports/
    <pkg-name>.skillpkg.zip
  config/
    settings.json
```

Notes:

- The installation directory must be writable. Installing under `C:\Program Files` may require elevated permissions, so the recommended deployment path is a user-writable tools directory.
- `skills/` is the source of truth for managed skill files.
- SQLite is the source of truth for package membership and installation history.

## Main UI

Use a three-column workbench layout.

### Left Column: Clients

Shows Codex, Claude Code, and OpenCode.

For each client, display:

- detected default path or manual custom path
- whether the path exists and is writable
- whether the client is enabled

Actions:

- scan and import skills from a selected client
- open client path settings
- refresh default path detection

### Middle Column: Packages

Shows package list.

Actions:

- create package
- rename or delete package
- import offline package
- export offline package

Each package row shows:

- package name
- description summary
- number of included skills
- last updated time

### Right Column: Package Detail

Shows selected package details.

Actions:

- add skills from the tool library
- remove skills from the package
- install package to Codex
- uninstall package from Codex
- install package to Claude Code
- uninstall package from Claude Code
- install package to OpenCode
- uninstall package from OpenCode

Future extension: add install/uninstall for all configured clients.

## SQLite Schema

### `clients`

Stores known client configurations.

Columns:

- `id` integer primary key
- `type` text unique, one of `codex`, `claude_code`, `opencode`
- `name` text
- `default_path` text
- `custom_path` text nullable
- `enabled` integer boolean
- `created_at` text
- `updated_at` text

The effective path is `custom_path` when set, otherwise `default_path`.

### `skills`

Stores skills imported into the tool library.

Columns:

- `id` text primary key
- `name` text
- `source_client` text nullable
- `relative_path` text
- `fingerprint` text
- `created_at` text
- `updated_at` text

`relative_path` points to `skills/<skill_id>/` under the tool installation directory.

`fingerprint` is a deterministic hash of the skill directory contents. It is used for duplicate detection and safe uninstall checks.

### `packages`

Stores package metadata.

Columns:

- `id` text primary key
- `name` text unique
- `description` text
- `created_at` text
- `updated_at` text

### `package_skills`

Stores package-to-skill membership.

Columns:

- `package_id` text
- `skill_id` text
- `sort_order` integer
- `created_at` text

Primary key: `(package_id, skill_id)`.

### `install_records`

Stores exact installation history. Uninstall uses this table as the primary authority.

Columns:

- `id` text primary key
- `package_id` text
- `skill_id` text
- `client_type` text
- `target_path` text
- `installed_path` text
- `fingerprint` text
- `installed_at` text
- `uninstalled_at` text nullable
- `status` text, one of `installed`, `uninstalled`, `missing`, `modified`, `failed`

### `operation_logs`

Stores user-visible operation history.

Columns:

- `id` text primary key
- `action` text
- `client_type` text nullable
- `package_id` text nullable
- `skill_id` text nullable
- `message` text
- `created_at` text

## Core Flows

### Startup

1. Create required folders: `data/`, `skills/`, `exports/`, and `config/`.
2. Open or initialize `data/skillpkg.db`.
3. Seed `clients` with Codex, Claude Code, and OpenCode rows if missing.
4. Detect default skill directories for each client.
5. Show client path status in the UI.

### Import Skills From Client

1. User selects a source client.
2. Tool scans the effective client skill directory.
3. Tool displays detected skill directories.
4. User selects skills to import.
5. Tool copies selected skill directories into `skills/<skill_id>/`.
6. Tool calculates fingerprints and writes `skills` rows.
7. If the same fingerprint already exists, offer to reuse the existing skill instead of importing a duplicate.

### Create Or Edit Package

1. User creates a package with name and optional description.
2. User selects skills from the tool library.
3. Tool writes `packages` and `package_skills` rows.
4. The package detail panel immediately reflects the selected skills.

### Install Package To Client

1. User selects a package and target client.
2. Tool reads package skills from `package_skills`.
3. Tool validates the target client path exists and is writable.
4. Tool previews all destination paths.
5. If a destination directory already exists, ask whether to skip, overwrite, or cancel.
6. Tool copies each skill directory from `skills/<skill_id>/` to the target client skill directory.
7. Tool writes an `install_records` row for each successfully installed skill.
8. Tool writes operation log entries.

Default conflict behavior: skip existing paths unless the user explicitly confirms overwrite.

### Uninstall Package From Client

1. User selects a package and target client.
2. Tool reads active `install_records` for the package and client.
3. For each record, tool checks whether `installed_path` exists.
4. If missing, mark the record as `missing`.
5. If present, recompute fingerprint and compare with the recorded fingerprint.
6. If unchanged, delete the installed skill directory and mark the record as `uninstalled`.
7. If changed, mark as `modified` and do not delete by default.
8. Tool writes operation log entries.

Safety rule: uninstall only deletes directories that have matching active install records. It does not delete by package name alone.

### Export Offline Package

1. User selects a package.
2. Tool reads package metadata and associated skills.
3. Tool creates a temporary staging directory.
4. Tool writes `manifest.json`.
5. Tool copies complete skill directories into `skills/` inside the package.
6. Tool zips the result to `exports/<pkg-name>.skillpkg.zip`.

Recommended manifest shape:

```json
{
  "schema_version": 1,
  "package": {
    "id": "pkg-id",
    "name": "Work A",
    "description": "Skills needed for Work A"
  },
  "skills": [
    {
      "id": "skill-id",
      "name": "Skill A1",
      "relative_path": "skills/skill-id",
      "fingerprint": "sha256..."
    }
  ],
  "exported_at": "2026-05-26T00:00:00Z"
}
```

### Import Offline Package

1. User selects a `.skillpkg.zip` file.
2. Tool extracts it to a temporary directory.
3. Tool validates `manifest.json` and required skill directories.
4. Tool imports skills into the local `skills/` directory.
5. If a skill with the same fingerprint exists, reuse it.
6. If the package name already exists, ask whether to rename, merge, or cancel.
7. Tool writes package and package-skill rows.
8. Tool writes operation log entries.

## Error Handling And Safety

- All install and uninstall operations perform a preview before changing files.
- File deletion is limited to paths recorded in `install_records`.
- Modified installed skills are not deleted by default.
- Existing destination directories are skipped by default.
- All operations write logs.
- Database writes should happen in transactions.
- File operations should use staging paths when possible, then move into place.
- UI should report partial success clearly when some skills succeed and others fail.

## Testing Strategy

### Unit Tests

- database initialization and migrations
- fingerprint generation
- package creation and membership updates
- client path resolution
- offline package manifest validation

### Integration Tests

- import skill from a fake client directory
- install a package into a fake client directory
- uninstall unchanged installed skills
- refuse to uninstall modified installed skills
- export and import offline package round trip

### Manual UI Checks

- first launch with no database
- missing client paths
- manual path override
- install conflict prompt
- uninstall modified-skill warning
- package import/export from the UI

## Out Of Scope For First Version

- Converting skill formats between clients.
- Downloading skills from remote repositories.
- Syncing packages through cloud storage.
- Multi-user permissions or team accounts.
- Automatic client restart or live reload.
