from __future__ import annotations

from pathlib import Path


def test_python_package_and_project_names_are_harness_manager():
    pyproject = Path("pyproject.toml").read_text(encoding="utf-8")

    assert 'name = "harness-manager"' in pyproject
    assert 'harness-manager = "harness_manager.__main__:main"' in pyproject
    assert "skillpkg" not in pyproject
    assert Path("src/harness_manager/__main__.py").is_file()
    assert not Path("src/skillpkg").exists()


def test_build_script_outputs_harness_manager_exe():
    script = Path("scripts/build.ps1").read_text(encoding="utf-8")

    assert "--name HarnessManager" in script
    assert "src/harness_manager/resources/app.ico" in script
    assert "src/harness_manager/__main__.py" in script
    assert "dist\\HarnessManager\\HarnessManager.exe" in script
    assert "SkillPkgManager" not in script
