from __future__ import annotations

from pathlib import Path


def test_app_icon_resources_exist():
    icon = Path("src/harness_manager/resources/app.ico")
    source = Path("src/harness_manager/resources/app.svg")

    assert icon.is_file()
    assert source.is_file()
    assert icon.stat().st_size > 100


def test_main_window_sets_window_icon():
    source = Path("src/harness_manager/gui/main_window.py").read_text(encoding="utf-8")

    assert "QIcon" in source
    assert "app.ico" in source
    assert "setWindowIcon" in source


def test_build_script_uses_app_icon():
    source = Path("scripts/build.ps1").read_text(encoding="utf-8")

    assert "--icon" in source
    assert "src/harness_manager/resources/app.ico" in source
