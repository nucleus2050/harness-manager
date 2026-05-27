from __future__ import annotations

from pathlib import Path


def test_main_window_has_skill_library_and_client_selection_text():
    source = Path("src/skillpkg/gui/main_window.py").read_text(encoding="utf-8")

    for text in [
        "技能库",
        "软件包",
        "从选中来源导入",
        "选择导入来源",
        "全部技能",
        "来源",
    ]:
        assert text in source


def test_main_window_tracks_selected_client():
    source = Path("src/skillpkg/gui/main_window.py").read_text(encoding="utf-8")

    assert "selected_client_type" in source
    assert "_select_client" in source
    assert "_show_packages_view" in source
    assert "_show_skills_view" in source
