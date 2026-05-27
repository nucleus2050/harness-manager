# Skill Package Manager

Windows desktop GUI for managing local skills across Codex, Claude Code, and OpenCode.

## Development

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .[dev]
pytest
python -m skillpkg
```

## Build

```powershell
.\scripts\build.ps1
```

## Runtime Data

The app stores runtime data under the directory where it is launched:

- `data/skillpkg.db`
- `skills/`
- `exports/`
- `config/`

Use a writable directory such as `D:\Tools\SkillPkgManager` for normal use.

## Safety

Uninstall removes only paths recorded in `install_records`. If an installed skill has been edited after installation, uninstall marks it as modified and leaves it in place.
