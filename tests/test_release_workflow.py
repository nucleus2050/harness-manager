from __future__ import annotations

from pathlib import Path


def test_project_version_is_initial_release():
    pyproject = Path("pyproject.toml").read_text(encoding="utf-8")

    assert 'version = "0.0.1"' in pyproject


def test_release_workflow_builds_windows_zip_and_release():
    workflow = Path(".github/workflows/release.yml")
    assert workflow.is_file()

    source = workflow.read_text(encoding="utf-8")
    for token in [
        "windows-latest",
        "scripts\\build.ps1",
        "pytest -q",
        "python -m compileall -q src tests",
        "Compress-Archive",
        "HarnessManager-${{ env.RELEASE_VERSION }}-windows-x64.zip",
        "gh release create",
        "gh release upload",
        "workflow_dispatch",
        "v0.0.1",
    ]:
        assert token in source
