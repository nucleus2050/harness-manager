from __future__ import annotations

import os
from pathlib import Path

from harness_manager.models import ClientType


def detect_default_paths() -> dict[ClientType, Path]:
    profile = Path(os.environ["USERPROFILE"]) if os.environ.get("USERPROFILE") else Path.home()
    opencode_config = Path(
        os.environ.get("OPENCODE_CONFIG_DIR", profile / ".config" / "opencode")
    )
    return {
        "codex": profile / ".codex" / "skills",
        "claude_code": profile / ".claude" / "skills",
        "opencode": opencode_config / "skills",
    }
