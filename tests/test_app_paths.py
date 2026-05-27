from __future__ import annotations

import pytest

from skillpkg.app_paths import AppPaths


def test_app_paths_create_required_directories(app_root):
    paths = AppPaths(app_root)

    paths.ensure()

    assert paths.data_dir.is_dir()
    assert paths.skills_dir.is_dir()
    assert paths.exports_dir.is_dir()
    assert paths.config_dir.is_dir()
    assert paths.db_path == app_root / "data" / "skillpkg.db"


def test_skill_path_uses_skill_id(app_root):
    paths = AppPaths(app_root)

    assert paths.skill_path("abc") == app_root / "skills" / "abc"


@pytest.mark.parametrize("skill_id", ["abc", "skill-a", "skill_a", "skill.a"])
def test_skill_path_accepts_safe_skill_ids(app_root, skill_id):
    paths = AppPaths(app_root)

    assert paths.skill_path(skill_id) == app_root / "skills" / skill_id


@pytest.mark.parametrize(
    "skill_id",
    [
        "..",
        "../evil",
        "evil/child",
        r"evil\child",
        r"C:\tmp",
        "C:/tmp",
        r"\\server\share",
    ],
)
def test_skill_path_rejects_unsafe_skill_ids(app_root, skill_id):
    paths = AppPaths(app_root)

    with pytest.raises(ValueError):
        paths.skill_path(skill_id)
