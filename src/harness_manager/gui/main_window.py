from __future__ import annotations

import ctypes
import json
import logging
import sys
from collections.abc import Callable
from pathlib import Path

from PySide6.QtCore import QEvent, QPoint, QSize, Qt
from PySide6.QtGui import QColor, QCursor, QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from harness_manager.app_paths import AppPaths
from harness_manager.db import connect
from harness_manager.gui import dialogs
from harness_manager.gui.controllers import MainController
from harness_manager.gui.styles import build_stylesheet
from harness_manager.models import Asset, ClientConfig, ClientType, Harness, Skill
from harness_manager.services import skill_description

logger = logging.getLogger(__name__)


WM_NCHITTEST = 0x0084
HTCLIENT = 1
HTCAPTION = 2
HTLEFT = 10
HTRIGHT = 11
HTTOP = 12
HTTOPLEFT = 13
HTTOPRIGHT = 14
HTBOTTOM = 15
HTBOTTOMLEFT = 16
HTBOTTOMRIGHT = 17

RESIZE_BORDER_WIDTH = 8
RESIZE_GRIP_WIDTH = 18
CORNER_GRIP_WIDTH = 34
WINDOW_SHADOW_MARGIN = 10
TITLE_BAR_HEIGHT = 42
CLIENT_CARD_MIN_HEIGHT = 92
CLIENT_SOURCE_VISIBLE_ROWS = 4
SKILL_DESCRIPTION_MAX_LENGTH = 180
AGENTS_SUMMARY_MAX_LENGTH = 96
MCP_SUMMARY_MAX_LENGTH = 96

UI_TEXT: dict[str, dict[str, str]] = {
    "zh-CN": {
        "window_title": "Harness Manager（任务套件管理器）",
        "settings": "设置",
        "settings_tip": "设置",
        "harnesses": "任务套件",
        "applications": "智能体",
        "agents": "AGENTS.md",
        "mcp": "MCP",
        "skills": "技能库 Skills",
        "new": "新建",
        "edit": "编辑",
        "delete": "删除",
        "import": "导入",
        "export": "导出",
        "custom_source": "添加自定义目录",
        "zh": "中文",
        "en": "English",
        "theme_light": "浅色",
        "theme_dark": "深色",
        "theme_obsidian": "黑曜",
        "theme_matrix": "矩阵",
        "theme_neon": "霓虹",
        "theme_sunset": "日落",
        "theme_forest": "森林",
        "theme_aurora": "极光",
        "theme_ember": "余烬",
        "theme_porcelain": "瓷白",
        "back": "返回",
        "export_config": "导出全部配置",
        "import_config": "导入全部配置",
        "select_harness": "选择一个任务套件",
        "harness_hint": "任务套件详情会显示在这里。",
        "app_title": "任务套件",
        "app_subtitle": "整理、打包并部署本地 AI 技能",
        "import_sources": "导入来源",
        "stat_skill": "技能",
        "settings_desc": "管理界面语言和全量配置备份。",
        "interface_language": "界面语言",
        "appearance_theme": "外观主题",
        "config_backup": "配置备份",
        "hero_subtitle": "整理可复用技能集合，导出离线包，并部署到 Codex、Claude Code 或 OpenCode。",
        "harnesses_desc": "把 AGENTS.md、MCP 和技能整理成可复用的任务工作台。",
        "mcp_management": "MCP 服务器管理",
        "mcp_management_desc": "维护任务套件可复用的 MCP JSON 配置。",
        "new_mcp": "+ 新增 MCP",
        "agents_management": "AGENTS.md 管理",
        "agents_management_desc": "维护可复用的提示词文件，可直接编辑或从文件导入。",
        "new_agents": "+ 新增 AGENTS.md",
        "configured_agents": "已配置 {count} 个 AGENTS.md",
        "configured_mcp": "已配置 {count} 个 MCP",
        "component_library": "组件库",
        "component_library_desc": "按类型查看全部技能、AGENTS.md 与 MCP，并加入任务套件。",
        "applications_desc": "从智能体角度查看 Codex、Claude Code、OpenCode 当前安装了哪些组件。",
        "installed_components": "已安装组件",
        "installed_empty": "暂无已安装组件",
        "configured_path": "配置路径",
        "ready": "就绪",
        "missing": "缺失",
        "custom": "自定义",
        "not_configured_path": "未配置路径",
        "error": "错误",
        "empty_harness_list": "暂无任务套件\n可以先新建空套件，再导入或关联组件。",
        "component_count": "{count} 个组件",
        "global": "全局",
        "project": "项目",
        "deploy_claude": "部署套件到 Claude Code",
        "deploy_codex": "部署套件到 Codex",
        "deploy_opencode": "部署套件到 OpenCode",
        "deployed_action": "已部署，点击撤销",
        "undeployed_action": "未部署，点击部署",
        "scope_toggle": "切换部署范围：全局默认目录 / 当前项目目录",
        "global_scope": "全局默认目录",
        "project_scope": "当前项目目录",
        "empty_agents": "暂无 AGENTS.md\n请先在任务套件详情中添加 AGENTS.md。",
        "empty_mcp": "暂无 MCP\n请先在任务套件详情中添加 MCP 配置。",
        "empty_skills": "暂无技能\n请从左侧选择 Skill 来源并导入技能。",
        "not_selected_harness": "未选择任务套件\n请从左侧列表选择一个任务套件。",
        "description_prefix": "描述",
        "joined_skills": "已加入的技能",
        "joined_agents": "已加入的 AGENTS.md",
        "joined_mcp": "已加入的 MCP",
        "asset_group_empty": "{title}\n0 个组件 - {empty}",
        "asset_group": "{title}\n{count} 个组件：{names}",
        "skill_label": "技能",
        "component_label": "组件",
        "choose_harness_first": "请先选择一个任务套件。",
        "current_app": "当前应用",
        "config_directory": "配置目录：{name}",
        "add_custom_source_title": "添加自定义目录",
        "source_name": "来源名称",
        "new_harness": "新建任务套件",
        "edit_harness": "编辑任务套件",
        "delete_harness": "删除任务套件",
        "delete_harness_message": "确认删除任务套件「{name}」？\n\n删除后不会删除技能、MCP、AGENTS.md 本体，只会移除套件及其关联关系。",
        "add_agents": "添加 AGENTS.md",
        "new_mcp_config": "新建 MCP 配置",
        "edit_mcp_config": "编辑 MCP 配置",
        "no_harness_error": "当前没有任务套件，请先新建任务套件。",
        "choose_remove_harness": "选择要移出的任务套件",
        "choose_remove_message": "请选择要移出该组件的任务套件",
        "remove": "移出",
        "delete_skill": "删除技能",
        "delete_skill_message": "确认删除技能「{name}」？\n\n删除后会移除技能文件及其任务套件关联。",
        "agents_description_prefix": "AGENTS.md 描述",
        "content_summary_prefix": "内容摘要",
        "mcp_description_prefix": "MCP 描述",
        "config_summary_prefix": "配置摘要",
        "type_prefix": "类型",
        "source_prefix": "来源",
        "local": "本地",
        "skill_description_prefix": "技能描述",
        "add_to_harness": "加入套件",
        "already_joined": "已加入",
        "no_harness": "无套件",
        "remove_from_harness": "移出套件",
        "not_joined": "未加入",
        "no_description": "暂无描述",
        "file_missing": "文件缺失",
        "no_content": "暂无内容",
        "config_file_missing": "配置文件缺失",
        "type_word": "类型",
        "command_word": "命令",
    },
    "en-US": {
        "window_title": "Harness Manager",
        "settings": "Settings",
        "settings_tip": "Settings",
        "harnesses": "Harnesses",
        "applications": "Agents",
        "agents": "AGENTS.md",
        "mcp": "MCP",
        "skills": "Skills",
        "new": "New",
        "edit": "Edit",
        "delete": "Delete",
        "import": "Import",
        "export": "Export",
        "custom_source": "Add Custom Folder",
        "zh": "Chinese",
        "en": "English",
        "theme_light": "Light",
        "theme_dark": "Dark",
        "theme_obsidian": "Obsidian",
        "theme_matrix": "Matrix",
        "theme_neon": "Neon",
        "theme_sunset": "Sunset",
        "theme_forest": "Forest",
        "theme_aurora": "Aurora",
        "theme_ember": "Ember",
        "theme_porcelain": "Porcelain",
        "back": "Back",
        "export_config": "Export Full Config",
        "import_config": "Import Full Config",
        "select_harness": "Select a harness",
        "harness_hint": "Harness details appear here.",
        "app_title": "Harnesses",
        "app_subtitle": "Organize, package, and deploy local AI skills",
        "import_sources": "Import Sources",
        "stat_skill": "Skills",
        "settings_desc": "Manage interface language and full configuration backups.",
        "interface_language": "Interface Language",
        "appearance_theme": "Appearance Theme",
        "config_backup": "Configuration Backup",
        "hero_subtitle": "Organize reusable skill sets, export offline bundles, and deploy to Codex, Claude Code, or OpenCode.",
        "harnesses_desc": "Group AGENTS.md, MCP, and skills into reusable task workbenches.",
        "mcp_management": "MCP Server Management",
        "mcp_management_desc": "Maintain reusable MCP JSON configurations for harnesses.",
        "new_mcp": "+ New MCP",
        "agents_management": "AGENTS.md Management",
        "agents_management_desc": "Maintain reusable instruction files by editing directly or importing a file.",
        "new_agents": "+ New AGENTS.md",
        "configured_agents": "{count} AGENTS.md configured",
        "configured_mcp": "{count} MCP configured",
        "component_library": "Component Library",
        "component_library_desc": "Browse all skills, AGENTS.md, and MCP components by type and add them to harnesses.",
        "applications_desc": "View installed components in Codex, Claude Code, and OpenCode from the agent perspective.",
        "installed_components": "Installed Components",
        "installed_empty": "No installed components",
        "configured_path": "Configured Path",
        "ready": "Ready",
        "missing": "Missing",
        "custom": "Custom",
        "not_configured_path": "No path configured",
        "error": "Error",
        "empty_harness_list": "No harnesses yet\nCreate an empty harness first, then import or link components.",
        "component_count": "{count} components",
        "global": "Global",
        "project": "Project",
        "deploy_claude": "Deploy harness to Claude Code",
        "deploy_codex": "Deploy harness to Codex",
        "deploy_opencode": "Deploy harness to OpenCode",
        "deployed_action": "Deployed, click to undo",
        "undeployed_action": "Not deployed, click to deploy",
        "scope_toggle": "Switch deploy scope: global default directory / current project directory",
        "global_scope": "global default directory",
        "project_scope": "current project directory",
        "empty_agents": "No AGENTS.md\nAdd AGENTS.md from the harness details first.",
        "empty_mcp": "No MCP\nAdd an MCP configuration from the harness details first.",
        "empty_skills": "No skills\nSelect a Skill source on the left and import skills.",
        "not_selected_harness": "No harness selected\nSelect a harness from the list.",
        "description_prefix": "Description",
        "joined_skills": "Joined skills",
        "joined_agents": "Joined AGENTS.md",
        "joined_mcp": "Joined MCP",
        "asset_group_empty": "{title}\n0 components - {empty}",
        "asset_group": "{title}\n{count} components: {names}",
        "skill_label": "Skill",
        "component_label": "Component",
        "choose_harness_first": "Select a harness first.",
        "current_app": "Current app",
        "config_directory": "Config directory: {name}",
        "add_custom_source_title": "Add Custom Folder",
        "source_name": "Source Name",
        "new_harness": "New Harness",
        "edit_harness": "Edit Harness",
        "delete_harness": "Delete Harness",
        "delete_harness_message": "Delete harness \"{name}\"?\n\nThis will not delete Skill, MCP, or AGENTS.md assets. It only removes the harness and its links.",
        "add_agents": "Add AGENTS.md",
        "new_mcp_config": "New MCP Config",
        "edit_mcp_config": "Edit MCP Config",
        "no_harness_error": "No harness exists. Create a harness first.",
        "choose_remove_harness": "Choose Harness to Remove From",
        "choose_remove_message": "Choose the harness to remove this component from.",
        "remove": "Remove",
        "delete_skill": "Delete Skill",
        "delete_skill_message": "Delete skill \"{name}\"?\n\nThis will remove the skill files and its harness links.",
        "agents_description_prefix": "AGENTS.md description",
        "content_summary_prefix": "Content summary",
        "mcp_description_prefix": "MCP description",
        "config_summary_prefix": "Config summary",
        "type_prefix": "Type",
        "source_prefix": "Source",
        "local": "Local",
        "skill_description_prefix": "Skill description",
        "add_to_harness": "Add",
        "already_joined": "Added",
        "no_harness": "No harness",
        "remove_from_harness": "Remove",
        "not_joined": "Not added",
        "no_description": "No description",
        "file_missing": "File missing",
        "no_content": "No content",
        "config_file_missing": "Config file missing",
        "type_word": "type",
        "command_word": "command",
    },
}


class _WindowsMSG(ctypes.Structure):
    _fields_ = [
        ("hwnd", ctypes.c_void_p),
        ("message", ctypes.c_uint),
        ("wParam", ctypes.c_void_p),
        ("lParam", ctypes.c_longlong),
        ("time", ctypes.c_uint),
        ("pt_x", ctypes.c_long),
        ("pt_y", ctypes.c_long),
    ]


def _app_icon_path() -> Path:
    return Path(__file__).resolve().parents[1] / "resources" / "app.ico"


class MainWindow(QMainWindow):
    def _t(self, key: str) -> str:
        return UI_TEXT.get(self.current_language, UI_TEXT["zh-CN"]).get(
            key, UI_TEXT["zh-CN"].get(key, key)
        )

    def __init__(self, controller: MainController) -> None:
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowMinMaxButtonsHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.controller = controller
        self.clients: list[ClientConfig] = []
        self.harnesses: list[Harness] = []
        self.harness_assets: list[Asset] = []
        self.library_assets: list[Asset] = []
        self.client_cards_layout: QVBoxLayout | None = None
        self.client_scroll: QScrollArea | None = None
        self.applications_layout: QVBoxLayout | None = None
        self.asset_library_header_layout: QVBoxLayout | None = None
        self.selected_client_type: ClientType | None = None
        self.selected_custom_source_id: str | None = None
        self.current_view = "harnesses"
        self.last_business_view = "harnesses"
        settings = self.controller.get_settings()
        self.current_theme = settings.theme
        self.current_language = settings.language
        self.deploy_scope = "global"
        self.title_bar: QFrame | None = None
        self.app_shell: QFrame | None = None
        self.shell_layout: QVBoxLayout | None = None
        self.maximize_button: QPushButton | None = None

        self.setWindowTitle(self._t("window_title"))
        self.setWindowIcon(QIcon(str(_app_icon_path())))
        self.resize(1240, 760)
        self.setMinimumSize(980, 620)
        self._apply_theme(self.current_theme)

        self.harness_list = QListWidget()
        self.skill_list = QListWidget()
        self.library_skill_list = QListWidget()
        self.harness_count_value = self._label("0", "StatValue")
        self.skill_count_value = self._label("0", "StatValue")
        self.mcp_count_value = self._label("0", "StatValue")
        self.agents_count_value = self._label("0", "StatValue")
        self.current_harness_title = self._label(self._t("select_harness"), "SectionTitle")
        self.current_harness_meta = self._label(self._t("harness_hint"), "MutedText")

        self.add_custom_source_button = self._button(self._t("custom_source"), "CompactButton")
        self.settings_button = self._button("⚙", "IconButton")
        self.settings_button.setToolTip(self._t("settings_tip"))
        self.harnesses_view_button = self._button(self._t("harnesses"), "SegmentButtonChecked")
        self.applications_view_button = self._button(self._t("applications"), "SegmentButton")
        self.agents_view_button = self._button(self._t("agents"), "SegmentButton")
        self.mcp_view_button = self._button(self._t("mcp"), "SegmentButton")
        self.skills_view_button = self._button(self._t("skills"), "SegmentButton")
        self.new_package_button = self._button(self._t("new"), "PrimaryButton")
        self.edit_harness_button = self._button(self._t("edit"), "CompactButton")
        self.delete_harness_button = self._button(self._t("delete"), "DangerButton")
        self.import_archive_button = self._button(self._t("import"), "CompactButton")
        self.export_archive_button = self._button(self._t("export"), "CompactButton")
        self.language_zh_button = self._button(self._t("zh"), "PrimaryButton")
        self.language_en_button = self._button(self._t("en"), "CompactButton")
        self.theme_light_button = self._button(self._t("theme_light"), "CompactButton")
        self.theme_dark_button = self._button(self._t("theme_dark"), "CompactButton")
        self.theme_obsidian_button = self._button(self._t("theme_obsidian"), "PrimaryButton")
        self.theme_matrix_button = self._button(self._t("theme_matrix"), "CompactButton")
        self.theme_neon_button = self._button(self._t("theme_neon"), "CompactButton")
        self.theme_sunset_button = self._button(self._t("theme_sunset"), "CompactButton")
        self.theme_forest_button = self._button(self._t("theme_forest"), "CompactButton")
        self.theme_aurora_button = self._button(self._t("theme_aurora"), "CompactButton")
        self.theme_ember_button = self._button(self._t("theme_ember"), "CompactButton")
        self.theme_porcelain_button = self._button(self._t("theme_porcelain"), "CompactButton")
        self.back_to_business_button = self._button(self._t("back"), "CompactButton")
        self.export_config_button = self._button(self._t("export_config"), "PrimaryButton")
        self.import_config_button = self._button(self._t("import_config"), "CompactButton")
        self._build_layout()
        self._connect_actions()
        self.refresh()

    def _build_layout(self) -> None:
        root = QWidget()
        root.setObjectName("RootSurface")
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(
            WINDOW_SHADOW_MARGIN,
            WINDOW_SHADOW_MARGIN,
            WINDOW_SHADOW_MARGIN,
            WINDOW_SHADOW_MARGIN,
        )
        root_layout.setSpacing(0)

        self.app_shell = QFrame()
        self.app_shell.setObjectName("AppShell")
        self.app_shell.setGraphicsEffect(self._build_window_shadow())
        self.shell_layout = QVBoxLayout(self.app_shell)
        self.shell_layout.setContentsMargins(0, 0, 0, 0)
        self.shell_layout.setSpacing(0)
        self.shell_layout.addWidget(self._build_title_bar())

        content = QWidget()
        content.setObjectName("ContentSurface")
        shell = QHBoxLayout(content)
        shell.setContentsMargins(18, 12, 18, 18)
        shell.setSpacing(18)

        shell.addWidget(self._build_sidebar(), 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setWidget(self._build_workspace())
        shell.addWidget(scroll, 1)
        self.shell_layout.addWidget(content, 1)
        root_layout.addWidget(self.app_shell)
        self.setCentralWidget(root)
        self._install_resize_cursor_tracking(root)
        self._update_window_margins()

    def _build_window_shadow(self) -> QGraphicsDropShadowEffect:
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(28)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 95))
        return shadow

    def _build_title_bar(self) -> QFrame:
        title_bar = QFrame()
        title_bar.setObjectName("TitleBar")
        title_bar.setFixedHeight(TITLE_BAR_HEIGHT)
        title_bar.mouseDoubleClickEvent = self._title_bar_double_click
        self.title_bar = title_bar

        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(14, 0, 8, 0)
        layout.setSpacing(10)

        icon = QLabel()
        icon.setObjectName("TitleIcon")
        icon.setPixmap(QPixmap(str(_app_icon_path())).scaled(
            16,
            16,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        ))
        self.title_bar_title = self._label(self._t("window_title"), "TitleText")
        layout.addWidget(icon)
        layout.addWidget(self.title_bar_title)
        layout.addStretch(1)

        self.minimize_button = self._window_button("—", "MinimizeButton")
        self.maximize_button = self._window_button("□", "MaximizeButton")
        self.close_button = self._window_button("×", "CloseButton")
        layout.addWidget(self.minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(self.close_button)
        return title_bar

    def _window_button(self, text: str, object_name: str) -> QPushButton:
        button = QPushButton(text)
        button.setObjectName(object_name)
        button.setFixedSize(44, 32)
        button.setCursor(Qt.CursorShape.ArrowCursor)
        return button

    def _build_sidebar(self) -> QWidget:
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(286)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(22, 24, 22, 24)
        layout.setSpacing(18)

        self.sidebar_title = self._label(self._t("app_title"), "AppTitle")
        self.sidebar_subtitle = self._label(self._t("app_subtitle"), "SidebarSubtitle")
        subtitle = self.sidebar_subtitle
        subtitle.setWordWrap(True)
        layout.addWidget(self.sidebar_title)
        layout.addWidget(subtitle)
        layout.addSpacing(8)

        stats = self._sidebar_card()
        layout.addWidget(stats)

        self.clients_title = self._sidebar_label(self._t("import_sources"))
        clients_title = self.clients_title
        layout.addWidget(clients_title)
        clients_container = QWidget()
        self.client_cards_layout = QVBoxLayout(clients_container)
        self.client_cards_layout.setContentsMargins(0, 0, 0, 0)
        self.client_cards_layout.setSpacing(10)
        self.client_cards_layout.addStretch(1)
        self.client_scroll = QScrollArea()
        self.client_scroll.setObjectName("ClientSourceScroll")
        self.client_scroll.setWidgetResizable(True)
        self.client_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.client_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.client_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.client_scroll.setWidget(clients_container)
        layout.addWidget(self.client_scroll, 1)

        layout.addWidget(self.add_custom_source_button)
        layout.addStretch(1)
        return sidebar

    def _sidebar_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("SidebarCard")
        layout = QGridLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setHorizontalSpacing(14)
        layout.setVerticalSpacing(6)

        self.stat_harness_label = self._label(self._t("harnesses"), "SidebarSubtitle")
        self.stat_skill_label = self._label(self._t("stat_skill"), "SidebarSubtitle")
        mcp_label = self._label("MCP", "SidebarSubtitle")
        agents_label = self._label("AGENTS.md", "SidebarSubtitle")
        self.harness_count_value.setStyleSheet("color: #f8fafc;")
        self.skill_count_value.setStyleSheet("color: #f8fafc;")
        self.mcp_count_value.setStyleSheet("color: #f8fafc;")
        self.agents_count_value.setStyleSheet("color: #f8fafc;")
        layout.addWidget(self.harness_count_value, 0, 0)
        layout.addWidget(self.skill_count_value, 0, 1)
        layout.addWidget(self.stat_harness_label, 1, 0)
        layout.addWidget(self.stat_skill_label, 1, 1)
        layout.addWidget(self.mcp_count_value, 2, 0)
        layout.addWidget(self.agents_count_value, 2, 1)
        layout.addWidget(mcp_label, 3, 0)
        layout.addWidget(agents_label, 3, 1)
        return card

    def _build_workspace(self) -> QWidget:
        workspace = QWidget()
        workspace.setMinimumWidth(860)
        layout = QVBoxLayout(workspace)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        layout.addWidget(self._build_hero())

        layout.addWidget(self._build_view_switch())
        self.harnesses_body = QWidget()
        harnesses_body_layout = QHBoxLayout(self.harnesses_body)
        harnesses_body_layout.setContentsMargins(0, 0, 0, 0)
        harnesses_body_layout.setSpacing(16)
        harnesses_body_layout.addWidget(self._build_harnesses_card(), 5)
        harnesses_body_layout.addWidget(self._build_details_card(), 4)
        layout.addWidget(self.harnesses_body, 1)
        self.applications_body = self._build_applications_card()
        layout.addWidget(self.applications_body, 1)
        self.skills_body = self._build_skills_library_card()
        layout.addWidget(self.skills_body, 1)
        self.settings_body = self._build_settings_card()
        layout.addWidget(self.settings_body, 1)
        return workspace

    def _build_settings_card(self) -> QFrame:
        card = self._card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 20, 22, 22)
        layout.setSpacing(18)
        settings_header = QHBoxLayout()
        settings_copy = QVBoxLayout()
        settings_copy.setSpacing(4)
        self.settings_title_label = self._label(self._t("settings"), "SectionTitle")
        self.settings_desc_label = self._label(self._t("settings_desc"), "MutedText")
        self.settings_desc_label.setWordWrap(True)
        settings_copy.addWidget(self.settings_title_label)
        settings_copy.addWidget(self.settings_desc_label)
        settings_header.addLayout(settings_copy, 1)
        settings_header.addWidget(self.back_to_business_button)
        layout.addLayout(settings_header)

        language_card = self._card()
        language_layout = QVBoxLayout(language_card)
        language_layout.setContentsMargins(18, 16, 18, 18)
        language_layout.setSpacing(12)
        self.language_title_label = self._label(self._t("interface_language"), "SectionTitle")
        language_layout.addWidget(self.language_title_label)
        language_row = QHBoxLayout()
        language_row.addWidget(self.language_zh_button)
        language_row.addWidget(self.language_en_button)
        language_row.addStretch(1)
        language_layout.addLayout(language_row)
        layout.addWidget(language_card)

        theme_card = self._card()
        theme_layout = QVBoxLayout(theme_card)
        theme_layout.setContentsMargins(18, 16, 18, 18)
        theme_layout.setSpacing(12)
        self.theme_title_label = self._label(self._t("appearance_theme"), "SectionTitle")
        theme_layout.addWidget(self.theme_title_label)
        theme_grid = QGridLayout()
        theme_grid.setHorizontalSpacing(10)
        theme_grid.setVerticalSpacing(10)
        for index, button in enumerate(
            [
                self.theme_obsidian_button,
                self.theme_matrix_button,
                self.theme_neon_button,
                self.theme_aurora_button,
                self.theme_ember_button,
                self.theme_dark_button,
                self.theme_light_button,
                self.theme_sunset_button,
                self.theme_forest_button,
                self.theme_porcelain_button,
            ]
        ):
            theme_grid.addWidget(button, index // 5, index % 5)
        theme_layout.addLayout(theme_grid)
        layout.addWidget(theme_card)

        backup_card = self._card()
        backup_layout = QVBoxLayout(backup_card)
        backup_layout.setContentsMargins(18, 16, 18, 18)
        backup_layout.setSpacing(12)
        self.backup_title_label = self._label(self._t("config_backup"), "SectionTitle")
        backup_layout.addWidget(self.backup_title_label)
        backup_row = QHBoxLayout()
        backup_row.addWidget(self.export_config_button)
        backup_row.addWidget(self.import_config_button)
        backup_row.addStretch(1)
        backup_layout.addLayout(backup_row)
        layout.addWidget(backup_card)
        layout.addStretch(1)
        return card

    def _build_applications_card(self) -> QFrame:
        card = self._card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 20, 22, 22)
        layout.setSpacing(14)
        self.applications_title_label = self._label(self._t("applications"), "SectionTitle")
        self.applications_desc_label = self._label(self._t("applications_desc"), "MutedText")
        self.applications_desc_label.setWordWrap(True)
        layout.addWidget(self.applications_title_label)
        layout.addWidget(self.applications_desc_label)
        self.applications_layout = QVBoxLayout()
        self.applications_layout.setSpacing(12)
        layout.addLayout(self.applications_layout)
        layout.addStretch(1)
        return card

    def _refresh_applications_view(self) -> None:
        if self.applications_layout is None:
            return
        self._clear_layout_widgets(self.applications_layout)
        for application in self.controller.list_application_components():
            self.applications_layout.addWidget(self._application_card(application))
        self.applications_layout.addStretch(1)

    def _application_card(self, application: dict[str, object]) -> QFrame:
        card = self._card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        header = QHBoxLayout()
        header.setSpacing(12)
        name = self._label(str(application["client_name"]), "ClientName")
        count = self._label(
            self._t("component_count").format(count=application["component_count"]),
            "HarnessCountPill",
        )
        count.setFixedWidth(88)
        count.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_key = str(application["path_status"])
        status = self._label(self._t(status_key), f"ClientStatus{status_key.title()}")
        header.addWidget(name, 1)
        header.addWidget(count)
        header.addWidget(status)
        layout.addLayout(header)

        configured_path = application["configured_path"] or self._t("not_configured_path")
        path = self._label(f"{self._t('configured_path')}: {configured_path}", "ClientPath")
        path.setWordWrap(True)
        layout.addWidget(path)

        components = list(application["components"])
        if not components:
            layout.addWidget(self._label(self._t("installed_empty"), "MutedText"))
            return card

        layout.addWidget(self._label(self._t("installed_components"), "MutedText"))
        for component in components:
            layout.addWidget(self._installed_component_row(component))
        return card

    def _installed_component_row(self, component: dict[str, object]) -> QFrame:
        row = QFrame()
        row.setObjectName("AssetLibraryItem")
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(12, 8, 12, 8)
        row_layout.setSpacing(12)
        copy = QVBoxLayout()
        copy.setSpacing(3)
        title = self._label(
            str(component["component_name"]),
            "ClientName",
        )
        source = self._label(self._t("component_count").format(count=component["asset_count"]), "MutedText")
        target = self._label(str(component["target_path"]), "ClientPath")
        target.setWordWrap(True)
        copy.addWidget(title)
        copy.addWidget(source)
        copy.addWidget(target)
        row_layout.addLayout(copy, 1)
        status_key = str(component["status"])
        status = self._label(self._t(status_key), f"ClientStatus{status_key.title()}")
        row_layout.addWidget(status, 0, Qt.AlignmentFlag.AlignTop)
        return row

    def _build_view_switch(self) -> QFrame:
        switch = QFrame()
        switch.setObjectName("ActionBar")
        layout = QHBoxLayout(switch)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        layout.addWidget(self.harnesses_view_button)
        layout.addWidget(self.applications_view_button)
        layout.addWidget(self.agents_view_button)
        layout.addWidget(self.mcp_view_button)
        layout.addWidget(self.skills_view_button)
        layout.addStretch(1)
        return switch

    def _build_hero(self) -> QFrame:
        hero = QFrame()
        hero.setObjectName("HeroCard")
        layout = QHBoxLayout(hero)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(20)

        copy = QVBoxLayout()
        copy.setSpacing(5)
        self.hero_title_label = self._label(self._t("window_title"), "PageTitle")
        copy.addWidget(self.hero_title_label)
        self.hero_subtitle_label = self._label(self._t("hero_subtitle"), "MutedText")
        subtitle = self.hero_subtitle_label
        subtitle.setWordWrap(True)
        copy.addWidget(subtitle)
        layout.addLayout(copy, 1)

        hero_actions = QHBoxLayout()
        hero_actions.setSpacing(10)
        hero_actions.addWidget(self.settings_button)
        layout.addLayout(hero_actions, 0)
        return hero

    def _build_harnesses_card(self) -> QFrame:
        card = self._card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 20)
        layout.setSpacing(12)
        header = QVBoxLayout()
        header.setSpacing(4)
        self.harnesses_title_label = self._label(self._t("harnesses"), "SectionTitle")
        self.harnesses_desc_label = self._label(self._t("harnesses_desc"), "MutedText")
        self.harnesses_desc_label.setWordWrap(True)
        header.addWidget(self.harnesses_title_label)
        header.addWidget(self.harnesses_desc_label)
        layout.addLayout(header)
        layout.addWidget(self._build_harness_actions())
        layout.addWidget(self.harness_list, 1)
        return card

    def _build_harness_actions(self) -> QFrame:
        bar = QFrame()
        bar.setObjectName("ActionBar")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        layout.addWidget(self.new_package_button)
        layout.addWidget(self.edit_harness_button)
        layout.addWidget(self.delete_harness_button)
        layout.addWidget(self.import_archive_button)
        layout.addWidget(self.export_archive_button)
        layout.addStretch(1)
        return bar

    def _build_details_card(self) -> QFrame:
        card = self._card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 20)
        layout.setSpacing(14)
        layout.addWidget(self.current_harness_title)
        layout.addWidget(self.current_harness_meta)
        self.skill_list.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        self.skill_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        layout.addWidget(self.skill_list, 1)
        return card

    def _build_skills_library_card(self) -> QFrame:
        card = self._card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 20)
        layout.setSpacing(12)
        self.asset_library_header = QWidget()
        self.asset_library_header_layout = QVBoxLayout(self.asset_library_header)
        self.asset_library_header_layout.setContentsMargins(0, 0, 0, 0)
        self.asset_library_header_layout.setSpacing(12)
        layout.addWidget(self.asset_library_header)
        layout.addWidget(self.library_skill_list, 1)
        return card

    def _build_mcp_toolbar(self) -> QWidget:
        toolbar = QFrame()
        toolbar.setObjectName("McpToolbar")
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(4, 0, 4, 0)
        layout.setSpacing(12)
        title = self._label(self._t("mcp_management"), "SectionTitle")
        subtitle = self._label(self._t("mcp_management_desc"), "MutedText")
        copy = QVBoxLayout()
        copy.setSpacing(4)
        copy.addWidget(title)
        copy.addWidget(subtitle)
        layout.addLayout(copy, 1)
        new_mcp_config_button = self._button(self._t("new_mcp"), "PrimaryButton")
        new_mcp_config_button.clicked.connect(self._guard(self._new_mcp_config))
        layout.addWidget(new_mcp_config_button)
        return toolbar

    def _build_agents_toolbar(self) -> QWidget:
        toolbar = QFrame()
        toolbar.setObjectName("AgentsToolbar")
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(4, 0, 4, 0)
        layout.setSpacing(12)
        title = self._label(self._t("agents_management"), "SectionTitle")
        subtitle = self._label(self._t("agents_management_desc"), "MutedText")
        copy = QVBoxLayout()
        copy.setSpacing(4)
        copy.addWidget(title)
        copy.addWidget(subtitle)
        layout.addLayout(copy, 1)
        new_agents_button = self._button(self._t("new_agents"), "PrimaryButton")
        new_agents_button.clicked.connect(self._guard(self._new_agents_md_asset))
        layout.addWidget(new_agents_button)
        return toolbar

    def _build_agents_summary(self) -> QWidget:
        summary = QFrame()
        summary.setObjectName("AgentsSummary")
        layout = QHBoxLayout(summary)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.addWidget(self._label(self._t("configured_agents").format(count=len(self.library_assets)), "MutedText"))
        layout.addStretch(1)
        return summary

    def _build_mcp_summary(self) -> QWidget:
        summary = QFrame()
        summary.setObjectName("McpSummary")
        layout = QHBoxLayout(summary)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.addWidget(self._label(self._t("configured_mcp").format(count=len(self.library_assets)), "MutedText"))
        layout.addStretch(1)
        return summary

    def _refresh_asset_library_header(self) -> None:
        if self.asset_library_header_layout is None:
            return
        while self.asset_library_header_layout.count():
            item = self.asset_library_header_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            child_layout = item.layout()
            if child_layout is not None:
                self._clear_layout_widgets(child_layout)
        if self.current_view == "mcp":
            self.asset_library_header_layout.addWidget(self._build_mcp_toolbar())
            self.asset_library_header_layout.addWidget(self._build_mcp_summary())
        elif self.current_view == "agents_md":
            self.asset_library_header_layout.addWidget(self._build_agents_toolbar())
            self.asset_library_header_layout.addWidget(self._build_agents_summary())
        else:
            self.asset_library_header_layout.addLayout(
                self._section_header(self._t("component_library"), self._t("component_library_desc"))
            )

    def _clear_layout_widgets(self, layout: QVBoxLayout | QHBoxLayout | QGridLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            child_layout = item.layout()
            if child_layout is not None:
                self._clear_layout_widgets(child_layout)

    def _asset_library_item(self, asset: Asset) -> QWidget:
        row = QFrame()
        row.setObjectName("AssetLibraryItem")
        row.setMinimumHeight(self._asset_library_item_height(asset))
        layout = QHBoxLayout(row)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        copy = QVBoxLayout()
        copy.setSpacing(2)
        copy.setAlignment(Qt.AlignmentFlag.AlignTop)
        title_text = self._mcp_display_name(asset) if asset.type == "mcp" else asset.name
        title = self._label(title_text, "ClientName")
        title.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        copy.addWidget(title)
        if asset.type == "agents_md":
            description = self._label(
                f"{self._t('agents_description_prefix')}: {self._agents_md_description(asset)}",
                "MutedText",
            )
            summary = self._label(
                f"{self._t('content_summary_prefix')}: {self._truncate_text(self._agents_md_summary(asset), AGENTS_SUMMARY_MAX_LENGTH)}",
                "SkillDescription",
            )
            description.setWordWrap(False)
            description.setMaximumHeight(18)
            summary.setWordWrap(True)
            summary.setMaximumHeight(34)
            for label in [description, summary]:
                label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
                copy.addWidget(label)
        elif asset.type == "mcp":
            description = self._label(
                f"{self._t('mcp_description_prefix')}: {self._mcp_description(asset)}",
                "MutedText",
            )
            summary = self._label(
                f"{self._t('config_summary_prefix')}: {self._truncate_text(self._mcp_config_summary(asset), MCP_SUMMARY_MAX_LENGTH)}",
                "SkillDescription",
            )
            description.setWordWrap(False)
            description.setMaximumHeight(18)
            summary.setWordWrap(True)
            summary.setMaximumHeight(34)
            for label in [description, summary]:
                label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
                copy.addWidget(label)
        else:
            meta = self._label(
                f"{self._t('type_prefix')}: {self._asset_type_label(asset.type)} - {self._t('source_prefix')}: {asset.source_type or self._t('local')}",
                "MutedText",
            )
            meta.setWordWrap(True)
            meta.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
            copy.addWidget(meta)
        if asset.type == "skill":
            description = self._label(
                f"{self._t('skill_description_prefix')}: {self._truncate_description(self._skill_description(asset))}",
                "SkillDescription",
            )
            description.setWordWrap(True)
            description.setContentsMargins(0, 0, 0, 0)
            description.setMaximumHeight(34)
            description.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
            copy.addWidget(description)
        layout.addLayout(copy, 1)

        available_harnesses = self.controller.list_harnesses_available_for_asset(asset)
        joined_harnesses = self.controller.list_harnesses_with_asset(asset.id)

        actions = QFrame()
        actions.setObjectName("AssetLibraryActions")
        actions.setFixedWidth(312)
        actions.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        actions_layout = QHBoxLayout(actions)
        actions_layout.setContentsMargins(12, 0, 12, 0)
        actions_layout.setSpacing(14)
        actions_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        add_button = self._button(self._t("add_to_harness"), "CompactButton")
        add_button.setFixedWidth(88)
        add_button.setEnabled(bool(available_harnesses))
        if not available_harnesses:
            add_button.setText(self._t("already_joined") if self.harnesses else self._t("no_harness"))
        add_button.clicked.connect(
            self._guard(lambda asset=asset: self._add_asset_to_chosen_harness(asset))
        )
        actions_layout.addWidget(add_button)

        if asset.type == "mcp":
            edit_button = self._button(self._t("edit"), "CompactButton")
            edit_button.setFixedWidth(88)
            edit_button.clicked.connect(self._guard(lambda asset=asset: self._edit_mcp_config(asset)))
            actions_layout.addWidget(edit_button)

        remove_button = self._button(self._t("remove_from_harness"), "CompactButton")
        remove_button.setFixedWidth(88)
        remove_button.setEnabled(bool(joined_harnesses))
        if not joined_harnesses:
            remove_button.setText(self._t("not_joined"))
        remove_button.clicked.connect(
            self._guard(lambda asset=asset: self._remove_asset_from_chosen_harness(asset))
        )
        actions_layout.addWidget(remove_button)
        if asset.type == "skill":
            delete_button = self._button(self._t("delete"), "CompactButton")
            delete_button.setFixedWidth(88)
            delete_button.clicked.connect(
                self._guard(lambda asset=asset: self._delete_skill_asset(asset))
            )
            actions_layout.addWidget(delete_button)
        layout.addWidget(actions, 0, Qt.AlignmentFlag.AlignVCenter)
        return row

    def _asset_library_item_height(self, asset: Asset) -> int:
        if asset.type == "skill":
            return 124
        return 118

    def _agents_md_description(self, asset: Asset) -> str:
        metadata = self._asset_metadata(asset)
        description = metadata.get("description")
        return description if isinstance(description, str) and description else self._t("no_description")

    def _asset_metadata(self, asset: Asset) -> dict:
        try:
            metadata = json.loads(asset.metadata_json or "{}")
        except json.JSONDecodeError:
            return {}
        return metadata if isinstance(metadata, dict) else {}

    def _agents_md_summary(self, asset: Asset) -> str:
        source = self.controller.paths.root / asset.relative_path
        if not source.is_file():
            return self._t("file_missing")
        lines = [
            line.strip()
            for line in source.read_text(encoding="utf-8", errors="replace").splitlines()
            if line.strip()
        ]
        return " ".join(lines) or self._t("no_content")

    def _mcp_display_name(self, asset: Asset) -> str:
        display_name = self._asset_metadata(asset).get("display_name")
        return display_name if isinstance(display_name, str) and display_name else asset.name

    def _mcp_description(self, asset: Asset) -> str:
        description = self._asset_metadata(asset).get("description")
        return description if isinstance(description, str) and description else self._t("no_description")

    def _mcp_config_summary(self, asset: Asset) -> str:
        source = self.controller.paths.root / asset.relative_path
        if not source.is_file():
            return self._t("config_file_missing")
        try:
            parsed = json.loads(source.read_text(encoding="utf-8", errors="replace"))
        except json.JSONDecodeError:
            return source.read_text(encoding="utf-8", errors="replace").strip()
        if isinstance(parsed, dict):
            command = parsed.get("command")
            server_type = parsed.get("type")
            parts = []
            if isinstance(server_type, str):
                parts.append(f"{self._t('type_word')} {server_type}")
            if isinstance(command, str):
                parts.append(f"{self._t('command_word')} {command}")
            return "，".join(parts) or json.dumps(parsed, ensure_ascii=False)
        return json.dumps(parsed, ensure_ascii=False)

    def _skill_description(self, asset: Asset) -> str:
        skill_root = self.controller.paths.root / asset.relative_path
        return skill_description(skill_root)

    def _truncate_description(self, description: str) -> str:
        return self._truncate_text(description, SKILL_DESCRIPTION_MAX_LENGTH)

    def _truncate_text(self, text: str, max_length: int) -> str:
        if len(text) <= max_length:
            return text
        return text[:max_length].rstrip() + "..."

    def _client_card(self, client: ClientConfig) -> QFrame:
        path = client.effective_path
        ready = path is not None and path.exists()
        card = QFrame()
        selected = client.type == self.selected_client_type
        card.setObjectName(
            "ClientCardSelected" if selected else "ClientCardReady" if ready else "ClientCard"
        )
        card.setMinimumHeight(CLIENT_CARD_MIN_HEIGHT)
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.mousePressEvent = lambda _event, client_type=client.type: self._select_client(client_type)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)

        header = QHBoxLayout()
        header.setSpacing(8)
        name = self._label(client.name, "ClientName")
        name.setWordWrap(True)
        status = self._label(self._t("ready") if ready else self._t("missing"), "ClientStatusReady" if ready else "ClientStatusMissing")
        status.setMinimumWidth(48)
        status.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        header.addWidget(name, 1)
        header.addWidget(status)
        import_button = self._button(self._t("import"), "SourceImportButton")
        import_button.setMaximumWidth(48)
        import_button.clicked.connect(
            self._guard(
                lambda _checked=False, client_type=client.type: self._import_from_client_source(
                    client_type
                )
            )
        )
        header.addWidget(import_button)
        layout.addLayout(header)

        path_label = self._label(str(path) if path else self._t("not_configured_path"), "ClientPath")
        path_label.setWordWrap(True)
        path_label.setMinimumHeight(34)
        layout.addWidget(path_label)
        return card

    def _custom_source_card(self, source: dict[str, object]) -> QFrame:
        selected = source["id"] == self.selected_custom_source_id
        card = QFrame()
        card.setObjectName("ClientCardSelected" if selected else "ClientCard")
        card.setMinimumHeight(CLIENT_CARD_MIN_HEIGHT)
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        source_id = str(source["id"])
        card.mousePressEvent = lambda _event, current_id=source_id: self._select_custom_source(
            current_id
        )
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)
        header = QHBoxLayout()
        header.setSpacing(8)
        name = self._label(str(source["name"]), "ClientName")
        name.setWordWrap(True)
        header.addWidget(name, 1)
        status = self._label(self._t("custom"), "ClientStatusReady")
        status.setMinimumWidth(48)
        status.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        delete_button = self._button(self._t("delete"), "SourceDeleteButton")
        delete_button.setMaximumWidth(48)
        import_button = self._button(self._t("import"), "SourceImportButton")
        import_button.setMaximumWidth(48)
        import_button.clicked.connect(
            self._guard(
                lambda _checked=False, current_id=source_id: self._import_from_custom_source(
                    current_id
                )
            )
        )
        delete_button.clicked.connect(
            self._guard(
                lambda _checked=False, current_id=source_id: self._remove_custom_source(
                    current_id
                )
            )
        )
        header.addWidget(status)
        header.addWidget(import_button)
        header.addWidget(delete_button)
        layout.addLayout(header)
        path_label = self._label(str(source["path"]), "ClientPath")
        path_label.setWordWrap(True)
        path_label.setMinimumHeight(34)
        layout.addWidget(path_label)
        return card

    def _section_header(self, title: str, subtitle: str) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.setSpacing(4)
        layout.addWidget(self._label(title, "SectionTitle"))
        text = self._label(subtitle, "MutedText")
        text.setWordWrap(True)
        layout.addWidget(text)
        return layout

    def _card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        return card

    def _button(self, text: str, object_name: str) -> QPushButton:
        button = QPushButton(text)
        button.setObjectName(object_name)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        return button

    def _label(self, text: str, object_name: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName(object_name)
        return label

    def _sidebar_label(self, text: str) -> QLabel:
        label = QLabel(text.upper())
        label.setStyleSheet("color: #94a3b8; font-size: 11px; font-weight: 800;")
        return label

    def _connect_actions(self) -> None:
        self.minimize_button.clicked.connect(self.showMinimized)
        self.maximize_button.clicked.connect(self._toggle_maximized)
        self.close_button.clicked.connect(self.close)
        self.harness_list.currentRowChanged.connect(self._refresh_harness_assets)
        self.add_custom_source_button.clicked.connect(self._guard(self._add_custom_source))
        self.settings_button.clicked.connect(self._show_settings_view)
        self.back_to_business_button.clicked.connect(self._show_previous_business_view)
        self.harnesses_view_button.clicked.connect(self._show_harnesses_view)
        self.applications_view_button.clicked.connect(self._show_applications_view)
        self.agents_view_button.clicked.connect(lambda: self._show_asset_view("agents_md"))
        self.mcp_view_button.clicked.connect(lambda: self._show_asset_view("mcp"))
        self.skills_view_button.clicked.connect(self._show_skills_view)
        self.new_package_button.clicked.connect(self._guard(self._new_harness))
        self.edit_harness_button.clicked.connect(self._guard(self._edit_harness))
        self.delete_harness_button.clicked.connect(self._guard(self._delete_harness))
        self.import_archive_button.clicked.connect(self._guard(self._import_archive))
        self.export_archive_button.clicked.connect(self._guard(self._export_archive))
        self.language_zh_button.clicked.connect(self._guard(lambda: self._save_language("zh-CN")))
        self.language_en_button.clicked.connect(self._guard(lambda: self._save_language("en-US")))
        self.theme_light_button.clicked.connect(self._guard(lambda: self._save_theme("light")))
        self.theme_dark_button.clicked.connect(self._guard(lambda: self._save_theme("dark")))
        self.theme_obsidian_button.clicked.connect(self._guard(lambda: self._save_theme("obsidian")))
        self.theme_matrix_button.clicked.connect(self._guard(lambda: self._save_theme("matrix")))
        self.theme_neon_button.clicked.connect(self._guard(lambda: self._save_theme("neon")))
        self.theme_sunset_button.clicked.connect(self._guard(lambda: self._save_theme("sunset")))
        self.theme_forest_button.clicked.connect(self._guard(lambda: self._save_theme("forest")))
        self.theme_aurora_button.clicked.connect(self._guard(lambda: self._save_theme("aurora")))
        self.theme_ember_button.clicked.connect(self._guard(lambda: self._save_theme("ember")))
        self.theme_porcelain_button.clicked.connect(self._guard(lambda: self._save_theme("porcelain")))
        self.export_config_button.clicked.connect(self._guard(self._export_full_config))
        self.import_config_button.clicked.connect(self._guard(self._import_full_config))

    def _guard(self, callback: Callable[[], None]) -> Callable[[], None]:
        def wrapped() -> None:
            try:
                logger.debug("Running GUI action %s", getattr(callback, "__name__", repr(callback)))
                callback()
            except Exception as exc:
                logger.exception("GUI action failed")
                dialogs.show_error(self, self._t("error"), str(exc))

        return wrapped

    def refresh(self) -> None:
        logger.debug("Refreshing main window")
        selected_row = self.harness_list.currentRow()
        self._refresh_settings_buttons(self.controller.get_settings())
        self.clients = self.controller.list_clients()
        self.harnesses = self.controller.list_harnesses()

        all_skills = self.controller.list_skills()
        mcp_assets = self.controller.list_assets_by_type("mcp")
        agents_assets = self.controller.list_assets_by_type("agents_md")
        self.harness_count_value.setText(str(len(self.harnesses)))
        self.skill_count_value.setText(str(len(all_skills)))
        self.mcp_count_value.setText(str(len(mcp_assets)))
        self.agents_count_value.setText(str(len(agents_assets)))
        self._refresh_view_state()

        self._clear_client_cards()
        for client in self.clients:
            self._add_client_card(client)
        for source in self.controller.list_custom_import_sources():
            self._add_custom_source_card(source)
        self._refresh_client_source_scroll_height()
        self._refresh_client_source_scroll_height()
        self._refresh_applications_view()

        self.harness_list.clear()
        if self.harnesses:
            for index, harness in enumerate(self.harnesses):
                assets = self.controller.list_harness_assets(harness.id)
                item = QListWidgetItem()
                item.setSizeHint(QSize(0, 116))
                self.harness_list.addItem(item)
                self.harness_list.setItemWidget(
                    item, self._harness_list_card(index, harness, assets)
                )
            self.harness_list.setCurrentRow(min(max(selected_row, 0), len(self.harnesses) - 1))
        else:
            self.harness_list.addItem(self._t("empty_harness_list"))
            self._refresh_harness_assets(-1)
        has_harness = bool(self.harnesses)
        self.edit_harness_button.setEnabled(has_harness)
        self.delete_harness_button.setEnabled(has_harness)
        self.export_archive_button.setEnabled(has_harness)
        self._refresh_asset_library(all_skills)

    def _harness_list_card(self, row: int, harness: Harness, assets: list[Asset]) -> QWidget:
        card = QFrame()
        card.setObjectName("HarnessListCard")
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.mousePressEvent = lambda _event, row=row: self.harness_list.setCurrentRow(row)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        header = QHBoxLayout()
        header.setSpacing(14)

        copy = QVBoxLayout()
        copy.setSpacing(6)
        title_row = QHBoxLayout()
        title_row.setSpacing(10)
        title = self._label(harness.name, "ClientName")
        title.setWordWrap(True)
        title_row.addWidget(title, 1)
        copy.addLayout(title_row)

        header.addLayout(copy, 1)

        actions = QFrame()
        actions.setObjectName("HarnessActions")
        actions.setFixedWidth(258)
        actions_layout = QHBoxLayout(actions)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(10)
        count_label = self._label(self._t("component_count").format(count=len(assets)), "HarnessCountPill")
        count_label.setFixedWidth(72)
        count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        actions_layout.addWidget(count_label)

        deploy_frame = QFrame()
        deploy_frame.setObjectName("HarnessDeployBar")
        deploy_frame.setFixedWidth(176)
        deploy_layout = QHBoxLayout(deploy_frame)
        deploy_layout.setContentsMargins(10, 6, 10, 6)
        deploy_layout.setSpacing(6)
        scope_text = self._t("global") if self.deploy_scope == "global" else self._t("project")
        scope_label = self._label(scope_text, "HarnessScopeLabel")
        deploy_layout.addWidget(scope_label)
        deploy_layout.addWidget(self._scope_toggle_button())
        for client_type, icon, tooltip in [
            ("claude_code", "✹", self._t("deploy_claude")),
            ("codex", "◎", self._t("deploy_codex")),
            ("opencode", "✦", self._t("deploy_opencode")),
        ]:
            target_path = self._deploy_target_path(client_type)
            active = self.controller.harness_deploy_status(harness.id, client_type, target_path)
            button = self._button(
                icon, "HarnessDeployIconActive" if active else "HarnessDeployIcon"
            )
            action_text = self._t("deployed_action") if active else self._t("undeployed_action")
            button.setToolTip(f"{tooltip} ({self._deploy_scope_label()}): {action_text}")
            button.clicked.connect(
                self._guard(
                    lambda harness_id=harness.id, client_type=client_type: self._toggle_harness_deployment(
                        harness_id, client_type
                    )
                )
            )
            deploy_layout.addWidget(button)
        actions_layout.addWidget(deploy_frame)
        header.addWidget(actions, 0, Qt.AlignmentFlag.AlignTop)
        layout.addLayout(header)
        return card

    def _scope_toggle_button(self) -> QPushButton:
        button = self._button("⌂" if self.deploy_scope == "global" else "▣", "HarnessScopeIcon")
        button.setToolTip(self._t("scope_toggle"))
        button.clicked.connect(self._guard(self._toggle_deploy_scope))
        return button

    def _toggle_deploy_scope(self) -> None:
        self.deploy_scope = "project" if self.deploy_scope == "global" else "global"
        self.refresh()

    def _deploy_scope_label(self) -> str:
        return self._t("global_scope") if self.deploy_scope == "global" else self._t("project_scope")

    def _deploy_target_path(self, client_type: ClientType) -> Path | None:
        if self.deploy_scope == "project":
            return self._project_deploy_target(client_type)
        return None

    def _refresh_view_state(self) -> None:
        harness_active = self.current_view == "harnesses"
        self.harnesses_body.setVisible(harness_active)
        applications_active = self.current_view == "applications"
        self.applications_body.setVisible(applications_active)
        settings_active = self.current_view == "settings"
        self.settings_body.setVisible(settings_active)
        self.skills_body.setVisible(not harness_active and not applications_active and not settings_active)
        self.harnesses_view_button.setObjectName(
            "SegmentButtonChecked" if harness_active else "SegmentButton"
        )
        self.applications_view_button.setObjectName(
            "SegmentButtonChecked" if applications_active else "SegmentButton"
        )
        self.skills_view_button.setObjectName(
            "SegmentButtonChecked" if self.current_view == "skills" else "SegmentButton"
        )
        self.agents_view_button.setObjectName(
            "SegmentButtonChecked" if self.current_view == "agents_md" else "SegmentButton"
        )
        self.mcp_view_button.setObjectName(
            "SegmentButtonChecked" if self.current_view == "mcp" else "SegmentButton"
        )
        self.harnesses_view_button.style().unpolish(self.harnesses_view_button)
        self.harnesses_view_button.style().polish(self.harnesses_view_button)
        self.applications_view_button.style().unpolish(self.applications_view_button)
        self.applications_view_button.style().polish(self.applications_view_button)
        self.skills_view_button.style().unpolish(self.skills_view_button)
        self.skills_view_button.style().polish(self.skills_view_button)
        self.agents_view_button.style().unpolish(self.agents_view_button)
        self.agents_view_button.style().polish(self.agents_view_button)
        self.mcp_view_button.style().unpolish(self.mcp_view_button)
        self.mcp_view_button.style().polish(self.mcp_view_button)
        self.settings_button.setObjectName(
            "IconButtonChecked" if settings_active else "IconButton"
        )
        self.settings_button.style().unpolish(self.settings_button)
        self.settings_button.style().polish(self.settings_button)

    def _refresh_asset_library(self, skills: list[Skill]) -> None:
        self.library_skill_list.clear()
        if self.current_view == "agents_md":
            self.library_assets = self.controller.list_assets_by_type("agents_md")
            empty_text = self._t("empty_agents")
        elif self.current_view == "mcp":
            self.library_assets = self.controller.list_assets_by_type("mcp")
            empty_text = self._t("empty_mcp")
        else:
            self.library_assets = self.controller.list_assets_by_type("skill")
            empty_text = self._t("empty_skills")
            if not self.library_assets:
                self.library_assets = [
                    Asset(skill.id, "skill", skill.name, skill.source_client, skill.relative_path, skill.fingerprint, "{}")
                    for skill in skills
                ]

        if not self.library_assets:
            self.library_skill_list.addItem(empty_text)
            self._refresh_asset_library_header()
            return
        for asset in self.library_assets:
            item = QListWidgetItem()
            widget = self._asset_library_item(asset)
            item.setSizeHint(QSize(0, self._asset_library_item_height(asset)))
            self.library_skill_list.addItem(item)
            self.library_skill_list.setItemWidget(item, widget)
        self._refresh_asset_library_header()

    def _refresh_current_asset_library(self) -> None:
        self._refresh_asset_library(self.controller.list_skills())

    def _show_harnesses_view(self) -> None:
        self.current_view = "harnesses"
        self.last_business_view = self.current_view
        self._refresh_view_state()

    def _show_applications_view(self) -> None:
        self.current_view = "applications"
        self._refresh_applications_view()
        self.last_business_view = self.current_view
        self._refresh_view_state()

    def _show_asset_view(self, asset_type: str) -> None:
        self.current_view = asset_type
        self._refresh_current_asset_library()
        self.last_business_view = self.current_view
        self._refresh_view_state()

    def _show_skills_view(self) -> None:
        self.current_view = "skills"
        self._refresh_current_asset_library()
        self.last_business_view = self.current_view
        self._refresh_view_state()

    def _show_settings_view(self) -> None:
        if self.current_view != "settings":
            self.last_business_view = self.current_view
        self.current_view = "settings"
        self._refresh_view_state()

    def _show_previous_business_view(self) -> None:
        previous = self.last_business_view if self.last_business_view != "settings" else "harnesses"
        if previous in {"agents_md", "mcp"}:
            self._show_asset_view(previous)
        elif previous == "applications":
            self._show_applications_view()
        elif previous == "skills":
            self._show_skills_view()
        else:
            self._show_harnesses_view()

    def _toggle_maximized(self) -> None:
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
        self._update_window_margins()

    def _title_bar_double_click(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._toggle_maximized()
            event.accept()

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            global_pos = event.globalPosition().toPoint()
            edges = self._resize_edges_at_position(global_pos)
            if edges:
                if self._start_system_resize(edges):
                    event.accept()
                    return
            if self._is_title_bar_drag_area(global_pos):
                if self._start_system_move():
                    event.accept()
                    return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        self._refresh_resize_cursor(event.globalPosition().toPoint())
        super().mouseMoveEvent(event)

    def leaveEvent(self, event) -> None:
        self.unsetCursor()
        super().leaveEvent(event)

    def eventFilter(self, watched, event) -> bool:
        if event.type() == QEvent.Type.MouseMove and self.isActiveWindow():
            self._refresh_resize_cursor(event.globalPosition().toPoint())
        elif event.type() == QEvent.Type.Leave:
            if not self.rect().contains(self.mapFromGlobal(QCursor.pos())):
                self.unsetCursor()
        return super().eventFilter(watched, event)

    def changeEvent(self, event) -> None:
        super().changeEvent(event)
        if event.type() == QEvent.Type.WindowStateChange:
            self._update_window_margins()
            if self.maximize_button is not None:
                self.maximize_button.setText("❐" if self.isMaximized() else "□")

    def _update_window_margins(self) -> None:
        if self.centralWidget() is None:
            return
        margin = 0 if self.isMaximized() else WINDOW_SHADOW_MARGIN
        self.centralWidget().layout().setContentsMargins(margin, margin, margin, margin)
        if self.app_shell is not None and self.app_shell.graphicsEffect() is not None:
            self.app_shell.graphicsEffect().setEnabled(not self.isMaximized())

    def nativeEvent(self, event_type, message):
        if sys.platform != "win32":
            return False, 0
        msg = _WindowsMSG.from_address(int(message))
        if msg.message != WM_NCHITTEST:
            return False, 0
        x, y = self._global_position_from_lparam(msg.lParam)
        hit = self._hit_test_result(QPoint(x, y))
        return (hit != HTCLIENT), hit

    def _global_position_from_lparam(self, lparam: int) -> tuple[int, int]:
        x = lparam & 0xFFFF
        y = (lparam >> 16) & 0xFFFF
        if x & 0x8000:
            x -= 0x10000
        if y & 0x8000:
            y -= 0x10000
        return x, y

    def _start_system_resize(self, edges: Qt.Edge) -> bool:
        handle = self.windowHandle()
        return bool(handle and handle.startSystemResize(edges))

    def _start_system_move(self) -> bool:
        handle = self.windowHandle()
        return bool(handle and handle.startSystemMove())

    def _install_resize_cursor_tracking(self, widget: QWidget) -> None:
        widget.setMouseTracking(True)
        widget.installEventFilter(self)
        for child in widget.findChildren(QWidget):
            child.setMouseTracking(True)
            child.installEventFilter(self)

    def _refresh_resize_cursor(self, global_pos: QPoint) -> None:
        if self.isMaximized():
            self.unsetCursor()
            return
        cursor = self._cursor_for_edges(self._resize_edges_at_position(global_pos))
        if cursor == Qt.CursorShape.ArrowCursor:
            self.unsetCursor()
        else:
            self.setCursor(cursor)

    def _resize_edges_at_position(self, global_pos: QPoint) -> Qt.Edge:
        if self.isMaximized():
            return Qt.Edge(0)
        local = self.mapFromGlobal(global_pos)
        border = RESIZE_GRIP_WIDTH + WINDOW_SHADOW_MARGIN
        corner = CORNER_GRIP_WIDTH + WINDOW_SHADOW_MARGIN
        edges = Qt.Edge(0)
        if local.x() <= border:
            edges |= Qt.Edge.LeftEdge
        elif local.x() >= self.width() - border:
            edges |= Qt.Edge.RightEdge
        if local.y() <= corner and (local.x() <= corner or local.x() >= self.width() - corner):
            edges |= Qt.Edge.TopEdge
        elif local.y() >= self.height() - corner and (
            local.x() <= corner or local.x() >= self.width() - corner
        ):
            edges |= Qt.Edge.BottomEdge
        elif local.y() <= border:
            edges |= Qt.Edge.TopEdge
        elif local.y() >= self.height() - border:
            edges |= Qt.Edge.BottomEdge
        return edges

    def _cursor_for_edges(self, edges: Qt.Edge) -> Qt.CursorShape:
        if edges in (
            Qt.Edge.TopEdge | Qt.Edge.LeftEdge,
            Qt.Edge.BottomEdge | Qt.Edge.RightEdge,
        ):
            return Qt.CursorShape.SizeFDiagCursor
        if edges in (
            Qt.Edge.TopEdge | Qt.Edge.RightEdge,
            Qt.Edge.BottomEdge | Qt.Edge.LeftEdge,
        ):
            return Qt.CursorShape.SizeBDiagCursor
        if edges & (Qt.Edge.LeftEdge | Qt.Edge.RightEdge):
            return Qt.CursorShape.SizeHorCursor
        if edges & (Qt.Edge.TopEdge | Qt.Edge.BottomEdge):
            return Qt.CursorShape.SizeVerCursor
        return Qt.CursorShape.ArrowCursor

    def _hit_test_result(self, global_pos: QPoint) -> int:
        if self.isMaximized():
            return HTCAPTION if self._is_title_bar_drag_area(global_pos) else HTCLIENT

        local = self.mapFromGlobal(global_pos)
        width = self.width()
        height = self.height()
        border = RESIZE_BORDER_WIDTH
        on_left = local.x() <= border
        on_right = local.x() >= width - border
        on_top = local.y() <= border
        on_bottom = local.y() >= height - border

        if on_top and on_left:
            return HTTOPLEFT
        if on_top and on_right:
            return HTTOPRIGHT
        if on_bottom and on_left:
            return HTBOTTOMLEFT
        if on_bottom and on_right:
            return HTBOTTOMRIGHT
        if on_left:
            return HTLEFT
        if on_right:
            return HTRIGHT
        if on_top:
            return HTTOP
        if on_bottom:
            return HTBOTTOM
        if self._is_title_bar_drag_area(global_pos):
            return HTCAPTION
        return HTCLIENT

    def _is_title_bar_drag_area(self, global_pos: QPoint) -> bool:
        if self.title_bar is None:
            return False
        title_pos = self.title_bar.mapFromGlobal(global_pos)
        if not self.title_bar.rect().contains(title_pos):
            return False
        child = self.childAt(self.mapFromGlobal(global_pos))
        while child is not None:
            if child.objectName() in {"MinimizeButton", "MaximizeButton", "CloseButton"}:
                return False
            child = child.parentWidget()
        return True

    def _select_client(self, client_type: ClientType) -> None:
        self.selected_client_type = client_type
        self.selected_custom_source_id = None
        self._clear_client_cards()
        for client in self.clients:
            self._add_client_card(client)
        for source in self.controller.list_custom_import_sources():
            self._add_custom_source_card(source)
        self._refresh_client_source_scroll_height()

    def _select_custom_source(self, source_id: str) -> None:
        self.selected_client_type = None
        self.selected_custom_source_id = source_id
        self._clear_client_cards()
        for client in self.clients:
            self._add_client_card(client)
        for source in self.controller.list_custom_import_sources():
            self._add_custom_source_card(source)
        self._refresh_client_source_scroll_height()

    def _selected_client_name(self, client_type: ClientType | None = None) -> str | None:
        target_type = client_type or self.selected_client_type
        for client in self.clients:
            if client.type == target_type:
                return client.name
        return None

    def _clear_client_cards(self) -> None:
        if self.client_cards_layout is None:
            return
        while self.client_cards_layout.count():
            item = self.client_cards_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.client_cards_layout.addStretch(1)

    def _refresh_client_source_scroll_height(self) -> None:
        if self.client_scroll is None:
            return
        source_count = len(self.clients) + len(self.controller.list_custom_import_sources())
        visible_rows = CLIENT_SOURCE_VISIBLE_ROWS if source_count else 1
        height = visible_rows * (CLIENT_CARD_MIN_HEIGHT + 10) + 4
        self.client_scroll.setMinimumHeight(CLIENT_CARD_MIN_HEIGHT + 14)
        self.client_scroll.setMaximumHeight(height)

    def _add_client_card(self, client: ClientConfig) -> None:
        if self.client_cards_layout is None:
            return
        stretch = self.client_cards_layout.takeAt(self.client_cards_layout.count() - 1)
        self.client_cards_layout.addWidget(self._client_card(client))
        self.client_cards_layout.addItem(stretch)

    def _add_custom_source_card(self, source: dict[str, object]) -> None:
        if self.client_cards_layout is None:
            return
        stretch = self.client_cards_layout.takeAt(self.client_cards_layout.count() - 1)
        self.client_cards_layout.addWidget(self._custom_source_card(source))
        self.client_cards_layout.addItem(stretch)

    def _refresh_harness_assets(self, row: int) -> None:
        self.skill_list.clear()
        self.harness_assets = []
        if row < 0 or row >= len(self.harnesses):
            self.current_harness_title.setText(self._t("select_harness"))
            self.current_harness_meta.setText(self._t("harness_hint"))
            self.skill_list.addItem(self._t("not_selected_harness"))
            return

        harness = self.harnesses[row]
        self.harness_assets = self.controller.list_harness_assets(harness.id)
        self.current_harness_title.setText(harness.name)
        self.current_harness_meta.setText(
            f"{self._t('description_prefix')}: {harness.description or self._t('no_description')}\n"
            f"{self._t('component_count').format(count=len(self.harness_assets))}"
        )
        self._add_asset_group(
            self._t("joined_skills"),
            self.controller.list_harness_assets_by_type(harness.id, "skill"),
            self._t("empty_skills").split("\n", 1)[0],
        )
        self._add_asset_group(
            self._t("joined_agents"),
            self.controller.list_harness_assets_by_type(harness.id, "agents_md"),
            self._t("empty_agents").split("\n", 1)[0],
        )
        self._add_asset_group(
            self._t("joined_mcp"),
            self.controller.list_harness_assets_by_type(harness.id, "mcp"),
            self._t("empty_mcp").split("\n", 1)[0],
        )

    def _add_asset_group(self, title: str, assets: list[Asset], empty_text: str) -> None:
        if not assets:
            self._add_wrapped_harness_asset_group(
                self._t("asset_group_empty").format(title=title, empty=empty_text)
            )
            return
        names = "、".join(asset.name for asset in assets)
        self._add_wrapped_harness_asset_group(
            self._t("asset_group").format(title=title, count=len(assets), names=names)
        )

    def _add_wrapped_harness_asset_group(self, text: str) -> None:
        title, separator, body = text.partition("\n")
        item = QListWidgetItem()
        item.setFlags(Qt.ItemFlag.NoItemFlags)
        item.setSizeHint(QSize(0, self._harness_asset_group_height(text)))
        frame = QFrame()
        frame.setObjectName("AssetLibraryItem")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(5)
        title_label = self._label(title, "SectionTitle")
        body = body if separator else ""
        body_label = self._label(body, "MutedText")
        body_label.setWordWrap(True)
        layout.addWidget(title_label)
        layout.addWidget(body_label)
        self.skill_list.addItem(item)
        self.skill_list.setItemWidget(item, frame)

    def _harness_asset_group_height(self, text: str) -> int:
        extra_lines = max(0, len(text) // 58)
        return 112 + extra_lines * 20

    def _asset_type_label(self, asset_type: str) -> str:
        return {"agents_md": "AGENTS.md", "mcp": "MCP", "skill": self._t("skill_label")}.get(
            asset_type, self._t("component_label")
        )

    def _selected_harness_row(self) -> int | None:
        row = self.harness_list.currentRow()
        return row if 0 <= row < len(self.harnesses) else None

    def _require_harness_row(self) -> int:
        row = self._selected_harness_row()
        if row is None:
            raise ValueError(self._t("choose_harness_first"))
        return row

    def _import_from_client_source(self, client_type: ClientType) -> None:
        self.selected_client_type = client_type
        self.selected_custom_source_id = None
        try:
            self.controller.import_from_client_source(client_type)
        except (ValueError, NotADirectoryError):
            client_name = self._selected_client_name(client_type) or self._t("current_app")
            source = dialogs.choose_directory(self, self._t("config_directory").format(name=client_name))
            if source is None:
                return
            self.controller.set_client_custom_path(client_type, source)
            self.controller.import_from_client_source(client_type)
        self.refresh()

    def _import_from_custom_source(self, source_id: str) -> None:
        self.selected_client_type = None
        self.selected_custom_source_id = source_id
        self.controller.import_from_custom_source(source_id)
        self.refresh()

    def _add_custom_source(self) -> None:
        source = dialogs.choose_directory(self, self._t("add_custom_source_title"))
        if source is None:
            return
        name = dialogs.ask_text(self, self._t("add_custom_source_title"), self._t("source_name"))
        if not name:
            name = source.name
        source_id = self.controller.add_custom_import_source(name, source)
        self.refresh()
        self._select_custom_source(source_id)

    def _remove_custom_source(self, source_id: str) -> None:
        self.controller.remove_custom_import_source(source_id)
        if self.selected_custom_source_id == source_id:
            self.selected_custom_source_id = None
        self.refresh()

    def _new_harness(self) -> None:
        details = dialogs.ask_harness_details(self, self._t("new_harness"))
        if details is None:
            return
        name, description = details
        self.controller.create_harness(name, description)
        self.refresh()

    def _edit_harness(self) -> None:
        harness = self._selected_harness()
        details = dialogs.ask_harness_details(
            self, self._t("edit_harness"), harness.name, harness.description
        )
        if details is None:
            return
        name, description = details
        self.controller.update_harness(harness.id, name, description)
        self.refresh()

    def _delete_harness(self) -> None:
        harness = self._selected_harness()
        confirmed = dialogs.ask_confirm(
            self,
            self._t("delete_harness"),
            self._t("delete_harness_message").format(name=harness.name),
        )
        if not confirmed:
            return
        self.controller.delete_harness(harness.id)
        self.refresh()

    def _selected_harness(self) -> Harness:
        row = self._require_harness_row()
        return self.harnesses[row]

    def _new_agents_md_asset(self) -> None:
        details = dialogs.ask_agents_md(self, self._t("add_agents"))
        if details is None:
            return
        name, description, content = details
        self.controller.create_agents_md_asset(name, description, content)
        self.refresh()

    def _new_mcp_config(self) -> None:
        details = dialogs.ask_mcp_config(self, self._t("new_mcp_config"))
        if details is None:
            return
        title, display_name, description, config_json = details
        self.controller.create_mcp_config_asset(title, display_name, config_json, description)
        self.refresh()

    def _edit_mcp_config(self, asset: Asset) -> None:
        config_path = self.controller.paths.root / asset.relative_path
        details = dialogs.ask_mcp_config(
            self,
            self._t("edit_mcp_config"),
            asset.name,
            self._mcp_display_name(asset),
            self._mcp_description(asset),
            config_path.read_text(encoding="utf-8"),
        )
        if details is None:
            return
        title, display_name, description, config_json = details
        self.controller.update_mcp_config_asset(
            asset.id, title, display_name, config_json, description
        )
        self.refresh()

    def _apply_theme(self, theme: str) -> None:
        self.current_theme = theme
        self.setStyleSheet(build_stylesheet(theme))

    def _refresh_settings_buttons(self, settings) -> None:
        self.language_zh_button.setObjectName(
            "PrimaryButton" if settings.language == "zh-CN" else "CompactButton"
        )
        self.language_en_button.setObjectName(
            "PrimaryButton" if settings.language == "en-US" else "CompactButton"
        )
        self.theme_light_button.setObjectName(
            "PrimaryButton" if settings.theme == "light" else "CompactButton"
        )
        self.theme_dark_button.setObjectName(
            "PrimaryButton" if settings.theme == "dark" else "CompactButton"
        )
        self.theme_obsidian_button.setObjectName(
            "PrimaryButton" if settings.theme == "obsidian" else "CompactButton"
        )
        self.theme_matrix_button.setObjectName(
            "PrimaryButton" if settings.theme == "matrix" else "CompactButton"
        )
        self.theme_neon_button.setObjectName(
            "PrimaryButton" if settings.theme == "neon" else "CompactButton"
        )
        self.theme_sunset_button.setObjectName(
            "PrimaryButton" if settings.theme == "sunset" else "CompactButton"
        )
        self.theme_forest_button.setObjectName(
            "PrimaryButton" if settings.theme == "forest" else "CompactButton"
        )
        self.theme_aurora_button.setObjectName(
            "PrimaryButton" if settings.theme == "aurora" else "CompactButton"
        )
        self.theme_ember_button.setObjectName(
            "PrimaryButton" if settings.theme == "ember" else "CompactButton"
        )
        self.theme_porcelain_button.setObjectName(
            "PrimaryButton" if settings.theme == "porcelain" else "CompactButton"
        )
        for button in [
            self.language_zh_button,
            self.language_en_button,
            self.theme_light_button,
            self.theme_dark_button,
            self.theme_obsidian_button,
            self.theme_matrix_button,
            self.theme_neon_button,
            self.theme_sunset_button,
            self.theme_forest_button,
            self.theme_aurora_button,
            self.theme_ember_button,
            self.theme_porcelain_button,
        ]:
            button.style().unpolish(button)
            button.style().polish(button)

    def _retranslate_static_ui(self) -> None:
        self.setWindowTitle(self._t("window_title"))
        self.title_bar_title.setText(self._t("window_title"))
        self.settings_button.setToolTip(self._t("settings_tip"))
        self.harnesses_view_button.setText(self._t("harnesses"))
        self.applications_view_button.setText(self._t("applications"))
        self.agents_view_button.setText(self._t("agents"))
        self.mcp_view_button.setText(self._t("mcp"))
        self.skills_view_button.setText(self._t("skills"))
        self.new_package_button.setText(self._t("new"))
        self.edit_harness_button.setText(self._t("edit"))
        self.delete_harness_button.setText(self._t("delete"))
        self.import_archive_button.setText(self._t("import"))
        self.export_archive_button.setText(self._t("export"))
        self.add_custom_source_button.setText(self._t("custom_source"))
        self.language_zh_button.setText(self._t("zh"))
        self.language_en_button.setText(self._t("en"))
        self.theme_light_button.setText(self._t("theme_light"))
        self.theme_dark_button.setText(self._t("theme_dark"))
        self.theme_obsidian_button.setText(self._t("theme_obsidian"))
        self.theme_matrix_button.setText(self._t("theme_matrix"))
        self.theme_neon_button.setText(self._t("theme_neon"))
        self.theme_sunset_button.setText(self._t("theme_sunset"))
        self.theme_forest_button.setText(self._t("theme_forest"))
        self.theme_aurora_button.setText(self._t("theme_aurora"))
        self.theme_ember_button.setText(self._t("theme_ember"))
        self.theme_porcelain_button.setText(self._t("theme_porcelain"))
        self.back_to_business_button.setText(self._t("back"))
        self.export_config_button.setText(self._t("export_config"))
        self.import_config_button.setText(self._t("import_config"))
        self.sidebar_title.setText(self._t("app_title"))
        self.sidebar_subtitle.setText(self._t("app_subtitle"))
        self.clients_title.setText(self._t("import_sources"))
        self.stat_harness_label.setText(self._t("harnesses"))
        self.stat_skill_label.setText(self._t("stat_skill"))
        self.settings_title_label.setText(self._t("settings"))
        self.settings_desc_label.setText(self._t("settings_desc"))
        self.applications_title_label.setText(self._t("applications"))
        self.applications_desc_label.setText(self._t("applications_desc"))
        self.language_title_label.setText(self._t("interface_language"))
        self.theme_title_label.setText(self._t("appearance_theme"))
        self.backup_title_label.setText(self._t("config_backup"))
        self.hero_title_label.setText(self._t("window_title"))
        self.hero_subtitle_label.setText(self._t("hero_subtitle"))
        self.harnesses_title_label.setText(self._t("harnesses"))
        self.harnesses_desc_label.setText(self._t("harnesses_desc"))
        if self.harness_list.currentRow() < 0:
            self.current_harness_title.setText(self._t("select_harness"))
            self.current_harness_meta.setText(self._t("harness_hint"))

    def _save_language(self, language: str) -> None:
        settings = self.controller.save_language(language)
        self.current_language = settings.language
        self._retranslate_static_ui()
        self._refresh_settings_buttons(settings)
        self.refresh()

    def _save_theme(self, theme: str) -> None:
        settings = self.controller.save_theme(theme)
        self._apply_theme(settings.theme)
        self._refresh_settings_buttons(settings)

    def _export_full_config(self) -> None:
        destination = dialogs.choose_export_zip(self)
        if destination is None:
            return
        self.controller.export_full_config(destination)

    def _import_full_config(self) -> None:
        archive = dialogs.choose_config_archive(self)
        if archive is None:
            return
        self.controller.import_full_config(archive)
        self.refresh()

    def _add_asset_to_chosen_harness(self, asset: Asset) -> None:
        available_harnesses = self.controller.list_harnesses_available_for_asset(asset)
        if not available_harnesses:
            if self.harnesses:
                return
            raise ValueError(self._t("no_harness_error"))
        harness = dialogs.choose_harness(self, available_harnesses)
        if harness is None:
            return
        self.controller.add_asset_to_harness(harness.id, asset.id, asset.type)
        self.refresh()

    def _remove_asset_from_chosen_harness(self, asset: Asset) -> None:
        joined_harnesses = self.controller.list_harnesses_with_asset(asset.id)
        if not joined_harnesses:
            return
        harness = dialogs.choose_harness(
            self,
            joined_harnesses,
            title=self._t("choose_remove_harness"),
            message=self._t("choose_remove_message"),
            confirm_text=self._t("remove"),
        )
        if harness is None:
            return
        self.controller.remove_asset_from_harness(harness.id, asset.id)
        self.refresh()

    def _delete_skill_asset(self, asset: Asset) -> None:
        confirmed = dialogs.ask_confirm(
            self,
            self._t("delete_skill"),
            self._t("delete_skill_message").format(name=asset.name),
        )
        if not confirmed:
            return
        self.controller.delete_skill_asset(asset.id)
        self.refresh()

    def _import_archive(self) -> None:
        archive = dialogs.choose_archive(self)
        if archive is None:
            return
        self.controller.import_offline_package(archive)
        self.refresh()

    def _export_archive(self) -> None:
        destination = dialogs.choose_harness_export_directory(self)
        if destination is None:
            return
        self.controller.export_harness_by_row(
            self._require_harness_row(), destination
        )

    def _toggle_harness_deployment(self, harness_id: str, client_type: ClientType) -> None:
        logger.info("Toggling harness deployment: harness=%s client=%s", harness_id, client_type)
        target_path = self._deploy_target_path(client_type)
        self.controller.toggle_harness_deploy(harness_id, client_type, target_path)
        self.refresh()

    def _project_deploy_target(self, client_type: ClientType) -> Path:
        base = self.controller.paths.root
        if client_type == "codex":
            return base / ".codex" / "skills"
        if client_type == "claude_code":
            return base / ".claude" / "skills"
        return base / ".opencode" / "skills"

    def _install(self, client_type: ClientType) -> None:
        self.controller.install_package_by_row(
            self._require_harness_row(), client_type
        )

    def _uninstall(self, client_type: ClientType) -> None:
        self.controller.uninstall_package_by_row(
            self._require_harness_row(), client_type
        )


def run_app(argv: list[str] | None = None) -> int:
    from harness_manager.logging_config import configure_logging

    configure_logging()
    logger.info("Starting Harness Manager GUI")
    app = QApplication(argv or sys.argv)
    app_root = Path.cwd()
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    try:
        controller = MainController(app_root, conn)
        window = MainWindow(controller)
        window.show()
        return int(app.exec())
    finally:
        conn.close()
