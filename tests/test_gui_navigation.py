from __future__ import annotations

from pathlib import Path


def test_main_window_has_skill_library_and_client_selection_text():
    source = Path("src/harness_manager/gui/main_window.py").read_text(encoding="utf-8")

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


def test_sidebar_stats_include_mcp_and_agents_counts():
    source = Path("src/harness_manager/gui/main_window.py").read_text(encoding="utf-8")

    assert "mcp_count_value" in source
    assert "agents_count_value" in source
    assert 'list_assets_by_type("mcp")' in source
    assert 'list_assets_by_type("agents_md")' in source


def test_settings_page_text_and_actions_exist():
    source = Path("src/harness_manager/gui/main_window.py").read_text(encoding="utf-8")
    dialog_source = Path("src/harness_manager/gui/dialogs.py").read_text(encoding="utf-8")

    for text in [
        "设置",
        "界面语言",
        "中文",
        "English",
        "外观主题",
        "浅色",
        "深色",
        "跟随系统",
        "配置备份",
        "导出全部配置",
        "导入全部配置",
    ]:
        assert text in source
    assert "_show_settings_view" in source
    assert "save_language" in source
    assert "save_theme" in source
    assert "export_full_config" in source
    assert "import_full_config" in source
    assert "choose_export_zip" in dialog_source


def test_settings_uses_compact_gear_and_can_return_to_business_view():
    source = Path("src/harness_manager/gui/main_window.py").read_text(encoding="utf-8")

    for token in [
        'self.settings_button = self._button("⚙", "IconButton")',
        'self.back_to_business_button = self._button("返回", "CompactButton")',
        "last_business_view",
        "_show_previous_business_view",
        "hero_actions.addWidget(self.settings_button)",
        "settings_header.addWidget(self.back_to_business_button)",
        "self.back_to_business_button.clicked.connect(self._show_previous_business_view)",
    ]:
        assert token in source
    assert "layout.addWidget(self.settings_button)" not in source
    assert "bottom_actions.addWidget(self.settings_button" not in source
    assert 'self.current_view = "settings"' in source


def test_hero_removes_local_workflow_badge():
    source = Path("src/harness_manager/gui/main_window.py").read_text(encoding="utf-8")

    assert "本地工作流" not in source
    assert "任务套件管理中心" not in source
    assert "hero_actions.addWidget(self.settings_button)" in source


def test_main_window_uses_custom_frameless_title_bar():
    source = Path("src/harness_manager/gui/main_window.py").read_text(encoding="utf-8")

    for token in [
        "FramelessWindowHint",
        "WA_TranslucentBackground",
        "_build_title_bar",
        "TitleBar",
        "TitleIcon",
        "TitleText",
        "MinimizeButton",
        "MaximizeButton",
        "CloseButton",
        "_toggle_maximized",
        "_update_window_margins",
    ]:
        assert token in source


def test_main_window_supports_native_resize_snap_and_shadow():
    source = Path("src/harness_manager/gui/main_window.py").read_text(encoding="utf-8")

    for token in [
        "WM_NCHITTEST",
        "HTCAPTION",
        "HTTOPLEFT",
        "HTBOTTOMRIGHT",
        "nativeEvent",
        "_hit_test_result",
        "QGraphicsDropShadowEffect",
        "setBlurRadius",
    ]:
        assert token in source


def test_main_window_uses_qt_system_move_resize_fallbacks():
    source = Path("src/harness_manager/gui/main_window.py").read_text(encoding="utf-8")

    for token in [
        "startSystemResize",
        "startSystemMove",
        "RESIZE_GRIP_WIDTH",
        "CORNER_GRIP_WIDTH",
        "_resize_edges_at_position",
        "_start_system_resize",
        "_start_system_move",
        "_install_resize_cursor_tracking",
        "_refresh_resize_cursor",
        "installEventFilter",
        "MouseMove",
        "mousePressEvent",
        "mouseMoveEvent",
        "SizeFDiagCursor",
        "SizeBDiagCursor",
        "SizeHorCursor",
        "SizeVerCursor",
    ]:
        assert token in source


def test_mcp_config_management_text_is_present():
    source = Path("src/harness_manager/gui/main_window.py").read_text(encoding="utf-8")
    dialog_source = Path("src/harness_manager/gui/dialogs.py").read_text(encoding="utf-8")

    for text in ["新增 MCP", "MCP 服务器管理", "已配置", "编辑", "完整 JSON 配置", "格式化", "MCP 标题（唯一）"]:
        assert text in source + dialog_source

    assert "ask_mcp_config" in source
    assert "McpConfigDialog" in dialog_source


def test_mcp_page_uses_management_layout_not_full_width_button():
    source = Path("src/harness_manager/gui/main_window.py").read_text(encoding="utf-8")

    assert "_build_mcp_toolbar" in source
    assert "_build_mcp_summary" in source
    assert "McpToolbar" in source
    assert "McpSummary" in source
    assert "self.asset_library_header_layout.addWidget(self._build_mcp_toolbar())" in source


def test_mcp_config_dialog_has_no_builtin_type_buttons():
    dialog_source = Path("src/harness_manager/gui/dialogs.py").read_text(encoding="utf-8")

    for text in ["sequential-thinking", "context7", "mcp_kind", "setCheckable"]:
        assert text not in dialog_source


def test_main_window_tracks_selected_client():
    source = Path("src/harness_manager/gui/main_window.py").read_text(encoding="utf-8")

    assert "selected_client_type" in source
    assert "_select_client" in source
    assert "_show_harnesses_view" in source
    assert "_show_skills_view" in source


def test_import_sources_use_scroll_area_with_fixed_actions():
    source = Path("src/harness_manager/gui/main_window.py").read_text(encoding="utf-8")

    for token in [
        "self.client_scroll = QScrollArea()",
        'self.client_scroll.setObjectName("ClientSourceScroll")',
        "self.client_scroll.setWidgetResizable(True)",
        "self.client_scroll.setWidget(clients_container)",
        "layout.addWidget(self.client_scroll, 0)",
        "self.import_skill_button.setObjectName(\"SidebarButton\")",
        "layout.addWidget(self.import_skill_button)",
        "layout.addWidget(self.add_custom_source_button)",
    ]:
        assert token in source


def test_import_source_scroll_height_adapts_to_content():
    source = Path("src/harness_manager/gui/main_window.py").read_text(encoding="utf-8")

    for token in [
        "self.client_scroll",
        "CLIENT_SOURCE_VISIBLE_ROWS",
        "_refresh_client_source_scroll_height",
        "self.client_scroll.setMaximumHeight",
        "self.client_scroll.setMinimumHeight",
        "source_count = len(self.clients) + len(self.controller.list_custom_import_sources())",
    ]:
        assert token in source


def test_asset_tab_switch_refreshes_visible_library():
    source = Path("src/harness_manager/gui/main_window.py").read_text(encoding="utf-8")

    assert "_refresh_current_asset_library()" in source
    assert "self.current_view = asset_type\n        self._refresh_current_asset_library()" in source
    assert "self.current_view = \"skills\"\n        self._refresh_current_asset_library()" in source


def test_join_harness_prompts_for_target_harness():
    main_source = Path("src/harness_manager/gui/main_window.py").read_text(encoding="utf-8")
    dialog_source = Path("src/harness_manager/gui/dialogs.py").read_text(encoding="utf-8")

    assert "choose_harness" in main_source
    assert "list_harnesses_without_asset(asset.id)" in main_source
    assert "已经加入所有任务套件" in main_source
    assert "选择任务套件" in dialog_source
    assert "请选择要加入的任务套件" in dialog_source


def test_harness_picker_uses_refined_card_style():
    dialog_source = Path("src/harness_manager/gui/dialogs.py").read_text(encoding="utf-8")

    assert "HarnessPickerDialog" in dialog_source
    assert "QListWidget#HarnessPickerList" in dialog_source
    assert "QPushButton#GhostDialogButton" in dialog_source
    assert "setMinimumSize(560, 460)" in dialog_source


def test_asset_library_adds_harness_action_on_each_item():
    source = Path("src/harness_manager/gui/main_window.py").read_text(encoding="utf-8")

    assert "_asset_library_item" in source
    assert "setItemWidget" in source
    assert "加入套件" in source
    assert "移出套件" in source
    assert "join_harness_button" not in source


def test_asset_library_removes_component_from_selected_harness():
    source = Path("src/harness_manager/gui/main_window.py").read_text(encoding="utf-8")
    dialog_source = Path("src/harness_manager/gui/dialogs.py").read_text(encoding="utf-8")

    assert "_remove_asset_from_chosen_harness" in source
    assert "list_harnesses_with_asset(asset.id)" in source
    assert "remove_asset_from_harness" in source
    assert "选择要移出的任务套件" in source
    assert "confirm_text" in dialog_source


def test_asset_library_item_has_safe_height_and_layout():
    source = Path("src/harness_manager/gui/main_window.py").read_text(encoding="utf-8")

    assert "QSize" in source
    assert "row.setMinimumHeight(78)" in source
    assert "item.setSizeHint(QSize(0, 86))" in source
    assert "add_button.setMinimumWidth(92)" in source


def test_client_source_cards_have_safe_height_and_wrapping():
    source = Path("src/harness_manager/gui/main_window.py").read_text(encoding="utf-8")

    assert "CLIENT_CARD_MIN_HEIGHT" in source
    assert "card.setMinimumHeight(CLIENT_CARD_MIN_HEIGHT)" in source
    assert "card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)" in source
    assert "name.setWordWrap(True)" in source
    assert "status.setMinimumWidth(48)" in source
    assert "path_label.setMinimumHeight(34)" in source


def test_harness_form_supports_description_and_editing():
    main_source = Path("src/harness_manager/gui/main_window.py").read_text(encoding="utf-8")
    dialog_source = Path("src/harness_manager/gui/dialogs.py").read_text(encoding="utf-8")

    assert "ask_harness_details" in main_source
    assert "编辑任务套件" in main_source
    assert "套件描述" in dialog_source
    assert "QPlainTextEdit" in dialog_source


def test_harness_details_show_components_grouped_by_type():
    source = Path("src/harness_manager/gui/main_window.py").read_text(encoding="utf-8")

    for text in ["已加入的技能", "已加入的 AGENTS.md", "已加入的 MCP"]:
        assert text in source

    assert "list_harness_assets_by_type(harness.id, \"skill\")" in source
    assert "list_harness_assets_by_type(harness.id, \"agents_md\")" in source
    assert "list_harness_assets_by_type(harness.id, \"mcp\")" in source


def test_empty_harness_asset_group_uses_single_list_item():
    source = Path("src/harness_manager/gui/main_window.py").read_text(encoding="utf-8")

    assert 'self.skill_list.addItem(f"{title}\\n0 个组件 - {empty_text}")' in source
    assert 'self.skill_list.addItem(empty_text)' not in source


def test_harness_asset_group_lists_concrete_component_names():
    source = Path("src/harness_manager/gui/main_window.py").read_text(encoding="utf-8")

    assert 'names = "、".join(asset.name for asset in assets)' in source
    assert 'self.skill_list.addItem(f"{title}\\n{len(assets)} 个组件：{names}")' in source
    assert 'self.skill_list.addItem(f"{asset.name}\\nID：{asset.id}")' not in source
