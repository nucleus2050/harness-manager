# Harness Manager

Windows desktop GUI for managing task harnesses. A harness can include AGENTS.md instructions, MCP configuration assets, and skills. Hook support is deferred.

## Development

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .[dev]
pytest
python -m harness_manager
```

## Build

```powershell
.\scripts\build.ps1
```

## Runtime Data

The app stores runtime data under the directory where it is launched:

- `data/harness.db`
- `skills/`
- `assets/`
- `exports/`
- `config/`

Use a writable directory such as `D:\Tools\HarnessManager` for normal use.

## Safety

Uninstall removes only paths recorded in `install_records`. If an installed skill has been edited after installation, uninstall marks it as modified and leaves it in place.
