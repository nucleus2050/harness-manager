from __future__ import annotations

from pathlib import Path


def test_main_window_has_skill_library_and_source_selection_text():
    source = Path("src/harness_manager/gui/main_window.py").read_text(encoding="utf-8")

    for text in [
        "技能库",
        "任务套件",
        "加入套件",
        "+ 新增 AGENTS.md",
        "+ 新增 MCP",
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
        'self.back_to_business_button = self._button(self._t("back"), "CompactButton")',
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

    for text in ["新增 MCP", "MCP 服务器管理", "已配置", "编辑", "完整 JSON 配置", "格式化", "MCP 标题（唯一）", "描述"]:
        assert text in source + dialog_source

    assert "ask_mcp_config" in source
    assert "McpConfigDialog" in dialog_source
    assert '"mcp_description_prefix": "MCP 描述"' in source
    assert '"config_summary_prefix": "配置摘要"' in source
    assert "_mcp_description" in source
    assert "_mcp_config_summary" in source
    assert "_mcp_display_name(asset)" in source


def test_agents_md_creation_dialog_supports_editor_and_file_import():
    source = Path("src/harness_manager/gui/main_window.py").read_text(encoding="utf-8")
    dialog_source = Path("src/harness_manager/gui/dialogs.py").read_text(encoding="utf-8")
    controller_source = Path("src/harness_manager/gui/controllers.py").read_text(encoding="utf-8")
    service_source = Path("src/harness_manager/services.py").read_text(encoding="utf-8")
    agents_toolbar_source = source.split("def _build_agents_toolbar", 1)[1].split("\n    def ", 1)[0]

    for text in ["添加 AGENTS.md", "名称", "描述", "内容", "选择文件导入", "在此输入提示词内容"]:
        assert text in dialog_source
    assert "AgentsMdDialog" in dialog_source
    assert "ask_agents_md" in dialog_source
    assert "_build_agents_toolbar" in source
    assert "_build_agents_summary" in source
    assert "self.asset_library_header_layout.addWidget(self._build_agents_toolbar())" in source
    assert 'new_agents_button = self._button(self._t("new_agents"), "PrimaryButton")' in agents_toolbar_source
    assert "new_agents_button.clicked.connect(self._guard(self._new_agents_md_asset))" in agents_toolbar_source
    for obsolete in [
        "self.add_agents_button",
        "self.add_mcp_button",
        "self.add_skill_asset_button",
        "def _import_agents_to_harness",
        "def _import_mcp_to_harness",
        "def _add_first_skill_to_harness",
        "asset_actions",
        "添加技能",
    ]:
        assert obsolete not in source
    assert "ask_agents_md" in source
    assert "def _new_agents_md_asset" in source
    assert "create_agents_md_asset" in controller_source
    assert "create_agents_md_asset" in service_source
    assert "metadata_json" in service_source


def test_mcp_config_dialog_uses_current_app_theme():
    dialog_source = Path("src/harness_manager/gui/dialogs.py").read_text(encoding="utf-8")
    mcp_dialog_source = dialog_source.split("class McpConfigDialog", 1)[1].split("\n\nclass ", 1)[0]

    assert "_THEME_TOKENS" in dialog_source
    assert "getattr(theme_source, \"current_theme\"" in dialog_source
    assert "self.setStyleSheet(_dialog_stylesheet(parent))" in dialog_source
    assert "QPlainTextEdit" in dialog_source
    assert "tokens['card']" in dialog_source
    assert "FramelessWindowHint" in mcp_dialog_source
    assert "DialogCloseButton" in mcp_dialog_source
    assert "close.clicked.connect(self.reject)" in mcp_dialog_source


def test_mcp_page_uses_management_layout_not_full_width_button():
    source = Path("src/harness_manager/gui/main_window.py").read_text(encoding="utf-8")
    toolbar_source = source.split("def _build_mcp_toolbar", 1)[1].split("\n    def ", 1)[0]

    assert "_build_mcp_toolbar" in source
    assert "_build_mcp_summary" in source
    assert "McpToolbar" in source
    assert "McpSummary" in source
    assert "self.asset_library_header_layout.addWidget(self._build_mcp_toolbar())" in source
    assert "self.new_mcp_config_button" not in source
    assert "new_mcp_config_button = self._button" in toolbar_source
    assert "new_mcp_config_button.clicked.connect" in toolbar_source


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


def test_import_source_scroll_can_shrink_when_window_is_short():
    source = Path("src/harness_manager/gui/main_window.py").read_text(encoding="utf-8")
    method = source.split("def _refresh_client_source_scroll_height", 1)[1].split("\n    def ", 1)[0]

    assert "self.client_scroll.setMinimumHeight(CLIENT_CARD_MIN_HEIGHT + 14)" in method
    assert "self.client_scroll.setMaximumHeight(height)" in method
    assert "self.client_scroll.setMinimumHeight(height)" not in method


def test_applications_view_lists_installed_components():
    source = Path("src/harness_manager/gui/main_window.py").read_text(encoding="utf-8")
    controller_source = Path("src/harness_manager/gui/controllers.py").read_text(encoding="utf-8")

    for token in [
        "self.applications_view_button",
        '"applications": "智能体"',
        '"applications": "Agents"',
        "从智能体角度查看 Codex、Claude Code、OpenCode 当前安装了哪些组件。",
        "_build_applications_card",
        "self.applications_body",
        "_refresh_applications_view",
        "list_application_components",
        "component_count",
        "component_name",
        "asset_count",
    ]:
        assert token in source
    assert "list_application_components" in controller_source
    method = source.split("def _installed_component_row", 1)[1].split("\n    def ", 1)[0]
    assert "asset_name" not in method
    assert "_asset_type_label" not in method


def test_asset_tab_switch_refreshes_visible_library():
    source = Path("src/harness_manager/gui/main_window.py").read_text(encoding="utf-8")

    assert "_refresh_current_asset_library()" in source
    assert "self.current_view = asset_type\n        self._refresh_current_asset_library()" in source
    assert "self.current_view = \"skills\"\n        self._refresh_current_asset_library()" in source


def test_join_harness_prompts_for_target_harness():
    main_source = Path("src/harness_manager/gui/main_window.py").read_text(encoding="utf-8")
    dialog_source = Path("src/harness_manager/gui/dialogs.py").read_text(encoding="utf-8")

    assert "choose_harness" in main_source
    assert "list_harnesses_available_for_asset(asset)" in main_source
    assert "available_harnesses = self.controller.list_harnesses_available_for_asset(asset)" in main_source
    assert "add_button.setEnabled(bool(available_harnesses))" in main_source
    assert 'add_button.setText(self._t("already_joined") if self.harnesses else self._t("no_harness"))' in main_source
    assert "remove_button.setEnabled(bool(joined_harnesses))" in main_source
    assert 'remove_button.setText(self._t("not_joined"))' in main_source
    assert "dialogs.show_info" not in main_source
    assert "选择任务套件" in dialog_source
    assert "请选择要加入的任务套件" in dialog_source


def test_agents_md_library_item_shows_description_and_summary_not_technical_ids():
    source = Path("src/harness_manager/gui/main_window.py").read_text(encoding="utf-8")

    assert "_agents_md_description" in source
    assert "_agents_md_summary" in source
    assert '"agents_description_prefix": "AGENTS.md 描述"' in source
    assert '"content_summary_prefix": "内容摘要"' in source
    assert "AGENTS_SUMMARY_MAX_LENGTH" in source
    assert "_truncate_text(self._agents_md_summary(asset), AGENTS_SUMMARY_MAX_LENGTH)" in source
    assert "summary.setMaximumHeight(34)" in source
    assert "description.setMaximumHeight(18)" in source
    assert "asset.type == \"agents_md\"" in source
    assert "类型：{self._asset_type_label(asset.type)} - 来源：{asset.source_type or '本地'} - ID：{asset.id}" not in source


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


def test_confirm_dialog_has_no_redundant_title_or_accent():
    dialog_source = Path("src/harness_manager/gui/dialogs.py").read_text(encoding="utf-8")
    confirm_source = dialog_source.split("class _ConfirmDialog", 1)[1].split("\n\nclass ", 1)[0]

    assert "DialogTitle" not in confirm_source
    assert "DialogAccent" not in confirm_source
    assert "title_label" not in confirm_source
    assert "message_label = QLabel(message)" in confirm_source
    assert '_tr(parent, "confirm_delete")' in confirm_source


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


def test_successful_gui_actions_do_not_show_info_dialogs():
    source = Path("src/harness_manager/gui/main_window.py").read_text(encoding="utf-8")

    assert "dialogs.show_info" not in source


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


def test_harness_delete_action_uses_confirm_and_single_row_actions():
    source = Path("src/harness_manager/gui/main_window.py").read_text(encoding="utf-8")
    controller_source = Path("src/harness_manager/gui/controllers.py").read_text(encoding="utf-8")
    dialog_source = Path("src/harness_manager/gui/dialogs.py").read_text(encoding="utf-8")
    action_builder = source.split("def _build_harness_actions", 1)[1].split("\n    def ", 1)[0]
    delete_method = source.split("def _delete_harness", 1)[1].split("\n    def ", 1)[0]

    assert "delete_harness_button" in source
    assert 'self._button(self._t("delete"), "DangerButton")' in source
    for redundant_label in ["新建套件", "编辑套件", "删除套件", "导入套件", "导出套件"]:
        assert redundant_label not in source
    assert "delete_harness(" in controller_source
    assert "ask_confirm" in dialog_source
    assert "delete_harness_message" in delete_method
    assert "controller.delete_harness" in delete_method
    assert "dialogs.show_info" not in delete_method
    assert "QHBoxLayout(bar)" in action_builder
    assert "archive_row" not in action_builder
    assert action_builder.index("new_package_button") < action_builder.index("edit_harness_button")
    assert action_builder.index("delete_harness_button") < action_builder.index("import_archive_button")


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


def test_skill_library_delete_requires_confirmation_without_success_dialog():
    source = Path("src/harness_manager/gui/main_window.py").read_text(encoding="utf-8")
    method = source.split("def _delete_skill_asset", 1)[1].split("\n    def ", 1)[0]

    assert "ask_confirm" in method
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
    stylesheet = Path("src/harness_manager/gui/styles.py").read_text(encoding="utf-8")

    assert "QSize" in source
    assert "_asset_library_item_height(asset)" in source
    assert "return 118" in source
    assert "actions = QFrame()" in source
    assert 'actions.setObjectName("AssetLibraryActions")' in source
    assert "actions.setFixedWidth(312)" in source
    assert "actions_layout = QHBoxLayout(actions)" in source
    assert "actions_layout.setContentsMargins(12, 0, 12, 0)" in source
    assert "actions_layout.setSpacing(14)" in source
    assert "actions_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)" in source
    assert "button.setFixedWidth(88)" in source
    assert "QFrame#AssetLibraryActions" in stylesheet
    assert "QFrame#AssetLibraryActions {{\n        background: transparent;" in stylesheet


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
    list_card = main_source.split("def _harness_list_card", 1)[1].split("\n    def ", 1)[0]
    details_refresh = main_source.split("def _refresh_harness_assets", 1)[1].split("\n    def ", 1)[0]

    assert "ask_harness_details" in main_source
    assert "编辑任务套件" in main_source
    assert "套件描述" in dialog_source
    assert "QPlainTextEdit" in dialog_source
    assert "harness.description or \"暂无描述\"" not in list_card
    assert "description_prefix" in details_refresh
    assert "component_count" in details_refresh


def test_harness_details_show_components_grouped_by_type():
    source = Path("src/harness_manager/gui/main_window.py").read_text(encoding="utf-8")

    for text in ["已加入的技能", "已加入的 AGENTS.md", "已加入的 MCP"]:
        assert text in source

    assert "list_harness_assets_by_type(harness.id, \"skill\")" in source
    assert "list_harness_assets_by_type(harness.id, \"agents_md\")" in source
    assert "list_harness_assets_by_type(harness.id, \"mcp\")" in source


def test_empty_harness_asset_group_uses_single_list_item():
    source = Path("src/harness_manager/gui/main_window.py").read_text(encoding="utf-8")

    assert '"asset_group_empty": "{title}\\n0 个组件 - {empty}"' in source
    assert 'self.skill_list.addItem(empty_text)' not in source


def test_harness_asset_group_lists_concrete_component_names():
    source = Path("src/harness_manager/gui/main_window.py").read_text(encoding="utf-8")

    assert 'names = "、".join(asset.name for asset in assets)' in source
    assert '"asset_group": "{title}\\n{count} 个组件：{names}"' in source
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
