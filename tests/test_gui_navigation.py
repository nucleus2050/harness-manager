from __future__ import annotations

from pathlib import Path


def test_main_window_has_skill_library_and_client_selection_text():
    source = Path("src/skillpkg/gui/main_window.py").read_text(encoding="utf-8")

    for text in [
        "技能库",
        "任务套件",
        "加入任务套件",
        "添加 AGENTS.md",
        "添加 MCP",
        "添加技能",
        "从选中来源导入",
        "选择导入来源",
        "全部技能",
        "来源",
    ]:
        assert text in source

    assert "软件包" not in source


def test_main_window_tracks_selected_client():
    source = Path("src/skillpkg/gui/main_window.py").read_text(encoding="utf-8")

    assert "selected_client_type" in source
    assert "_select_client" in source
    assert "_show_harnesses_view" in source
    assert "_show_skills_view" in source


def test_join_harness_prompts_for_target_harness():
    main_source = Path("src/skillpkg/gui/main_window.py").read_text(encoding="utf-8")
    dialog_source = Path("src/skillpkg/gui/dialogs.py").read_text(encoding="utf-8")

    assert "choose_harness" in main_source
    assert "选择任务套件" in dialog_source
    assert "请选择要加入的任务套件" in dialog_source


def test_harness_form_supports_description_and_editing():
    main_source = Path("src/skillpkg/gui/main_window.py").read_text(encoding="utf-8")
    dialog_source = Path("src/skillpkg/gui/dialogs.py").read_text(encoding="utf-8")

    assert "ask_harness_details" in main_source
    assert "编辑任务套件" in main_source
    assert "套件描述" in dialog_source
    assert "QPlainTextEdit" in dialog_source


def test_harness_details_show_components_grouped_by_type():
    source = Path("src/skillpkg/gui/main_window.py").read_text(encoding="utf-8")

    for text in ["已加入的技能", "已加入的 AGENTS.md", "已加入的 MCP"]:
        assert text in source

    assert "list_harness_assets_by_type(harness.id, \"skill\")" in source
    assert "list_harness_assets_by_type(harness.id, \"agents_md\")" in source
    assert "list_harness_assets_by_type(harness.id, \"mcp\")" in source
