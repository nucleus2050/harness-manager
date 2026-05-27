from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def app_root(tmp_path: Path) -> Path:
    root = tmp_path / "SkillPkgManager"
    root.mkdir()
    return root


@pytest.fixture
def sample_skill(tmp_path: Path) -> Path:
    skill = tmp_path / "sample-skill"
    skill.mkdir()
    (skill / "SKILL.md").write_text("# Sample Skill\n\nBody\n", encoding="utf-8")
    return skill
