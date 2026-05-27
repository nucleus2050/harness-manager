from __future__ import annotations

from pathlib import Path


def test_main_window_has_skill_library_and_client_selection_text():
    source = Path("src/skillpkg/gui/main_window.py").read_text(encoding="utf-8")

    for text in [
        "技能库",
        "任务套件",
        "加入套件",
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


def test_mcp_config_management_text_is_present():
    source = Path("src/skillpkg/gui/main_window.py").read_text(encoding="utf-8")
    dialog_source = Path("src/skillpkg/gui/dialogs.py").read_text(encoding="utf-8")

    for text in ["新增 MCP", "MCP 服务器管理", "已配置", "编辑", "完整 JSON 配置", "格式化", "MCP 标题（唯一）"]:
        assert text in source + dialog_source

    assert "ask_mcp_config" in source
    assert "McpConfigDialog" in dialog_source


def test_mcp_page_uses_management_layout_not_full_width_button():
    source = Path("src/skillpkg/gui/main_window.py").read_text(encoding="utf-8")

    assert "_build_mcp_toolbar" in source
    assert "_build_mcp_summary" in source
    assert "McpToolbar" in source
    assert "McpSummary" in source
    assert "self.asset_library_header_layout.addWidget(self._build_mcp_toolbar())" in source


def test_mcp_config_dialog_has_no_builtin_type_buttons():
    dialog_source = Path("src/skillpkg/gui/dialogs.py").read_text(encoding="utf-8")

    for text in ["sequential-thinking", "context7", "mcp_kind", "setCheckable"]:
        assert text not in dialog_source


def test_main_window_tracks_selected_client():
    source = Path("src/skillpkg/gui/main_window.py").read_text(encoding="utf-8")

    assert "selected_client_type" in source
    assert "_select_client" in source
    assert "_show_harnesses_view" in source
    assert "_show_skills_view" in source


def test_asset_tab_switch_refreshes_visible_library():
    source = Path("src/skillpkg/gui/main_window.py").read_text(encoding="utf-8")

    assert "_refresh_current_asset_library()" in source
    assert "self.current_view = asset_type\n        self._refresh_current_asset_library()" in source
    assert "self.current_view = \"skills\"\n        self._refresh_current_asset_library()" in source


def test_join_harness_prompts_for_target_harness():
    main_source = Path("src/skillpkg/gui/main_window.py").read_text(encoding="utf-8")
    dialog_source = Path("src/skillpkg/gui/dialogs.py").read_text(encoding="utf-8")

    assert "choose_harness" in main_source
    assert "list_harnesses_without_asset(asset.id)" in main_source
    assert "已经加入所有任务套件" in main_source
    assert "选择任务套件" in dialog_source
    assert "请选择要加入的任务套件" in dialog_source


def test_harness_picker_uses_refined_card_style():
    dialog_source = Path("src/skillpkg/gui/dialogs.py").read_text(encoding="utf-8")

    assert "HarnessPickerDialog" in dialog_source
    assert "QListWidget#HarnessPickerList" in dialog_source
    assert "QPushButton#GhostDialogButton" in dialog_source
    assert "setMinimumSize(560, 460)" in dialog_source


def test_asset_library_adds_harness_action_on_each_item():
    source = Path("src/skillpkg/gui/main_window.py").read_text(encoding="utf-8")

    assert "_asset_library_item" in source
    assert "setItemWidget" in source
    assert "加入套件" in source
    assert "移出套件" in source
    assert "join_harness_button" not in source


def test_asset_library_removes_component_from_selected_harness():
    source = Path("src/skillpkg/gui/main_window.py").read_text(encoding="utf-8")
    dialog_source = Path("src/skillpkg/gui/dialogs.py").read_text(encoding="utf-8")

    assert "_remove_asset_from_chosen_harness" in source
    assert "list_harnesses_with_asset(asset.id)" in source
    assert "remove_asset_from_harness" in source
    assert "选择要移出的任务套件" in source
    assert "confirm_text" in dialog_source


def test_asset_library_item_has_safe_height_and_layout():
    source = Path("src/skillpkg/gui/main_window.py").read_text(encoding="utf-8")

    assert "QSize" in source
    assert "row.setMinimumHeight(78)" in source
    assert "item.setSizeHint(QSize(0, 86))" in source
    assert "add_button.setMinimumWidth(92)" in source


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


def test_empty_harness_asset_group_uses_single_list_item():
    source = Path("src/skillpkg/gui/main_window.py").read_text(encoding="utf-8")

    assert 'self.skill_list.addItem(f"{title}\\n0 个组件 - {empty_text}")' in source
    assert 'self.skill_list.addItem(empty_text)' not in source


def test_harness_asset_group_lists_concrete_component_names():
    source = Path("src/skillpkg/gui/main_window.py").read_text(encoding="utf-8")

    assert 'names = "、".join(asset.name for asset in assets)' in source
    assert 'self.skill_list.addItem(f"{title}\\n{len(assets)} 个组件：{names}")' in source
    assert 'self.skill_list.addItem(f"{asset.name}\\nID：{asset.id}")' not in source
