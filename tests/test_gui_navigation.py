from __future__ import annotations

from pathlib import Path


def test_main_window_has_skill_library_and_source_selection_text():
    source = Path("src/harness_manager/gui/main_window.py").read_text(encoding="utf-8")

    for text in [
        "技能库",
        "任务套件",
        "加入套件",
        "添加 AGENTS.md",
        "添加 MCP",
        "添加技能",
        "导入来源",
        "选择 Skill 来源",
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
        "黑曜",
        "矩阵",
        "霓虹",
        "日落",
        "森林",
        "极光",
        "余烬",
        "瓷白",
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
    assert "跟随系统" not in source
    assert "theme_grid.addWidget" in source


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
        "layout.addWidget(self.client_scroll, 1)",
        "layout.addWidget(self.add_custom_source_button)",
        '"SourceImportButton"',
        "_import_from_client_source",
        "_import_from_custom_source",
    ]:
        assert token in source
    assert "layout.addWidget(self.import_skill_button)" not in source


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


def test_message_dialog_uses_app_like_custom_chrome():
    dialog_source = Path("src/harness_manager/gui/dialogs.py").read_text(encoding="utf-8")

    for token in [
        "FramelessWindowHint",
        "MessageDialog",
        "DialogShell",
        "DialogCloseButton",
        "DialogAccent",
    ]:
        assert token in dialog_source
    assert "QMessageBox" not in dialog_source


def test_harness_deploy_icons_are_stateful_toggles():
    source = Path("src/harness_manager/gui/main_window.py").read_text(encoding="utf-8")
    stylesheet = Path("src/harness_manager/gui/styles.py").read_text(encoding="utf-8")

    for token in [
        "harness_deploy_status",
        "_toggle_harness_deployment",
        "HarnessDeployIconActive",
        "已部署，点击撤销",
        "未部署，点击部署",
    ]:
        assert token in source + stylesheet
    assert "_deploy_harness(" not in source


def test_successful_harness_deploy_uses_icon_state_without_dialog():
    source = Path("src/harness_manager/gui/main_window.py").read_text(encoding="utf-8")
    method = source.split("def _toggle_harness_deployment", 1)[1].split("\n    def ", 1)[0]

    assert "self.refresh()" in method
    assert "toggle_harness_deploy" in method
    assert "dialogs.show_info" not in method


def test_export_harness_button_is_enabled_and_uses_harness_export():
    source = Path("src/harness_manager/gui/main_window.py").read_text(encoding="utf-8")
    controller_source = Path("src/harness_manager/gui/controllers.py").read_text(encoding="utf-8")
    dialog_source = Path("src/harness_manager/gui/dialogs.py").read_text(encoding="utf-8")
    export_method = source.split("def _export_archive", 1)[1].split("\n    def ", 1)[0]

    assert "export_harness_by_row" in source
    assert "export_harness_by_row" in controller_source
    assert "choose_harness_export_directory" in dialog_source
    assert "choose_harness_export_directory(self)" in export_method
    assert "export_harness_by_row(" in export_method
    assert "self._require_harness_row(), destination" in export_method
    assert "for button in [self.export_archive_button]" not in source
    assert "export_package_by_row(self._require_harness_row())" not in source


def test_harness_delete_action_uses_confirm_and_split_actions():
    source = Path("src/harness_manager/gui/main_window.py").read_text(encoding="utf-8")
    controller_source = Path("src/harness_manager/gui/controllers.py").read_text(encoding="utf-8")
    dialog_source = Path("src/harness_manager/gui/dialogs.py").read_text(encoding="utf-8")
    action_builder = source.split("def _build_harness_actions", 1)[1].split("\n    def ", 1)[0]
    delete_method = source.split("def _delete_harness", 1)[1].split("\n    def ", 1)[0]

    assert "delete_harness_button" in source
    assert 'self._button("删除", "DangerButton")' in source
    for redundant_label in ["新建套件", "编辑套件", "删除套件", "导入套件", "导出套件"]:
        assert redundant_label not in source
    assert "delete_harness(" in controller_source
    assert "ask_confirm" in dialog_source
    assert "删除后不会删除技能、MCP、AGENTS.md 本体" in delete_method
    assert "controller.delete_harness" in delete_method
    assert action_builder.count("QHBoxLayout()") >= 2
    assert "archive_row" in action_builder


def test_asset_library_adds_harness_action_on_each_item():
    source = Path("src/harness_manager/gui/main_window.py").read_text(encoding="utf-8")

    assert "_asset_library_item" in source
    assert "setItemWidget" in source
    assert "加入套件" in source
    assert "移出套件" in source
    assert "删除" in source
    assert "delete_skill_asset" in source
    assert "asset.type == \"skill\"" in source
    assert "join_harness_button" not in source


def test_skill_library_delete_is_direct_without_confirmation():
    source = Path("src/harness_manager/gui/main_window.py").read_text(encoding="utf-8")
    method = source.split("def _delete_skill_asset", 1)[1].split("\n    def ", 1)[0]

    assert "delete_skill_asset(asset.id)" in method
    assert "self.refresh()" in method
    assert "dialogs.show_info" not in method
    assert "confirm_text" not in method


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
    assert "_asset_library_item_height(asset)" in source
    assert "return 86" in source
    assert "add_button.setMinimumWidth(92)" in source


def test_skill_library_item_shows_truncated_description_by_default():
    source = Path("src/harness_manager/gui/main_window.py").read_text(encoding="utf-8")
    services_source = Path("src/harness_manager/services.py").read_text(encoding="utf-8")

    assert "_asset_library_item_height" in source
    assert "_skill_description" in source
    assert "SKILL_DESCRIPTION_MAX_LENGTH" in source
    assert "_truncate_description" in source
    assert "copy.setAlignment(Qt.AlignmentFlag.AlignTop)" in source
    assert "return 124" in source
    assert "description.setContentsMargins(0, 0, 0, 0)" in source
    assert '"SkillDescription"' in source
    assert "技能描述" in source
    assert "SKILL.md" in services_source
    assert "itemClicked.connect" not in source


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

    assert '_add_wrapped_harness_asset_group(f"{title}\\n0 个组件 - {empty_text}")' in source
    assert 'self.skill_list.addItem(empty_text)' not in source


def test_harness_asset_group_lists_concrete_component_names():
    source = Path("src/harness_manager/gui/main_window.py").read_text(encoding="utf-8")

    assert 'names = "、".join(asset.name for asset in assets)' in source
    assert '_add_wrapped_harness_asset_group(f"{title}\\n{len(assets)} 个组件：{names}")' in source
    assert 'self.skill_list.addItem(f"{asset.name}\\nID：{asset.id}")' not in source


def test_harness_asset_groups_wrap_and_grow_for_long_text():
    source = Path("src/harness_manager/gui/main_window.py").read_text(encoding="utf-8")

    assert "_add_wrapped_harness_asset_group" in source
    assert "_harness_asset_group_height" in source
    assert "self.skill_list.setSelectionMode(QListWidget.SelectionMode.NoSelection)" in source
    assert "self.skill_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)" in source
    assert "item.setFlags(Qt.ItemFlag.NoItemFlags)" in source
    assert "label.setWordWrap(True)" in source
    assert "title_label = self._label(title, \"SectionTitle\")" in source
    assert "body_label = self._label(body, \"MutedText\")" in source
    assert "item.setSizeHint(QSize(0, self._harness_asset_group_height(text)))" in source
    assert "self.skill_list.setItemWidget(item, frame)" in source
    assert "return 112 + extra_lines * 20" in source
