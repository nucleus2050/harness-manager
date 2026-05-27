from __future__ import annotations

import ctypes
import sys
from collections.abc import Callable
from pathlib import Path

from PySide6.QtCore import QEvent, QPoint, QSize, Qt
from PySide6.QtGui import QColor, QCursor, QIcon, QPalette, QPixmap
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
        self.asset_library_header_layout: QVBoxLayout | None = None
        self.selected_client_type: ClientType | None = None
        self.selected_custom_source_id: str | None = None
        self.current_view = "harnesses"
        self.last_business_view = "harnesses"
        self.current_theme = self.controller.get_settings().theme
        self.title_bar: QFrame | None = None
        self.app_shell: QFrame | None = None
        self.shell_layout: QVBoxLayout | None = None
        self.maximize_button: QPushButton | None = None

        self.setWindowTitle("Harness Manager（任务套件管理器）")
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
        self.current_harness_title = self._label("选择一个任务套件", "SectionTitle")
        self.current_harness_meta = self._label("任务套件详情会显示在这里。", "MutedText")

        self.import_skill_button = self._button("选择客户端", "PrimaryButton")
        self.add_custom_source_button = self._button("添加自定义目录", "CompactButton")
        self.settings_button = self._button("⚙", "IconButton")
        self.settings_button.setToolTip("设置")
        self.harnesses_view_button = self._button("任务套件", "SegmentButtonChecked")
        self.agents_view_button = self._button("AGENTS.md", "SegmentButton")
        self.mcp_view_button = self._button("MCP", "SegmentButton")
        self.skills_view_button = self._button("技能库 Skills", "SegmentButton")
        self.new_package_button = self._button("新建套件", "PrimaryButton")
        self.edit_harness_button = self._button("编辑套件", "CompactButton")
        self.import_archive_button = self._button("导入套件", "CompactButton")
        self.export_archive_button = self._button("导出套件", "CompactButton")
        self.add_agents_button = self._button("添加 AGENTS.md", "CompactButton")
        self.add_mcp_button = self._button("添加 MCP", "CompactButton")
        self.new_mcp_config_button = self._button("+ 新增 MCP", "PrimaryButton")
        self.add_skill_asset_button = self._button("添加技能", "CompactButton")
        self.install_codex_button = self._button("安装", "DeployInstallButton")
        self.uninstall_codex_button = self._button("卸载", "DeployUninstallButton")
        self.install_claude_button = self._button("安装", "DeployInstallButton")
        self.uninstall_claude_button = self._button("卸载", "DeployUninstallButton")
        self.install_opencode_button = self._button("安装", "DeployInstallButton")
        self.uninstall_opencode_button = self._button("卸载", "DeployUninstallButton")
        self.language_zh_button = self._button("中文", "PrimaryButton")
        self.language_en_button = self._button("English", "CompactButton")
        self.theme_light_button = self._button("浅色", "CompactButton")
        self.theme_dark_button = self._button("深色", "CompactButton")
        self.theme_system_button = self._button("跟随系统", "PrimaryButton")
        self.back_to_business_button = self._button("返回", "CompactButton")
        self.export_config_button = self._button("导出全部配置", "PrimaryButton")
        self.import_config_button = self._button("导入全部配置", "CompactButton")
        for button in [
            self.export_archive_button,
            self.install_codex_button,
            self.uninstall_codex_button,
            self.install_claude_button,
            self.uninstall_claude_button,
            self.install_opencode_button,
            self.uninstall_opencode_button,
        ]:
            button.setEnabled(False)
            button.setToolTip("任务套件部署将在组件安装语义确定后接入。")

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
        title = self._label("Harness Manager（任务套件管理器）", "TitleText")
        layout.addWidget(icon)
        layout.addWidget(title)
        layout.addStretch(1)

        self.minimize_button = self._window_button("—", "MinimizeButton")
        self.maximize_button = self._window_button("□", "MaximizeButton")
        self.close_button = self._window_button("×", "CloseButton")
        layout.addWidget(self.settings_button)
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

        title = self._label("任务套件", "AppTitle")
        subtitle = self._label("整理、打包并部署本地 AI 技能", "SidebarSubtitle")
        subtitle.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(8)

        stats = self._sidebar_card()
        layout.addWidget(stats)

        clients_title = self._sidebar_label("导入来源")
        layout.addWidget(clients_title)
        clients_container = QWidget()
        self.client_cards_layout = QVBoxLayout(clients_container)
        self.client_cards_layout.setContentsMargins(0, 0, 0, 0)
        self.client_cards_layout.setSpacing(10)
        self.client_cards_layout.addStretch(1)
        layout.addWidget(clients_container, 1)

        self.import_skill_button.setObjectName("SidebarButton")
        layout.addWidget(self.import_skill_button)
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

        harness_label = self._label("任务套件", "SidebarSubtitle")
        skill_label = self._label("技能", "SidebarSubtitle")
        mcp_label = self._label("MCP", "SidebarSubtitle")
        agents_label = self._label("AGENTS.md", "SidebarSubtitle")
        self.harness_count_value.setStyleSheet("color: #f8fafc;")
        self.skill_count_value.setStyleSheet("color: #f8fafc;")
        self.mcp_count_value.setStyleSheet("color: #f8fafc;")
        self.agents_count_value.setStyleSheet("color: #f8fafc;")
        layout.addWidget(self.harness_count_value, 0, 0)
        layout.addWidget(self.skill_count_value, 0, 1)
        layout.addWidget(harness_label, 1, 0)
        layout.addWidget(skill_label, 1, 1)
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
        settings_copy = self._section_header("设置", "管理界面语言和全量配置备份。")
        settings_header.addLayout(settings_copy, 1)
        settings_header.addWidget(self.back_to_business_button)
        layout.addLayout(settings_header)

        language_card = self._card()
        language_layout = QVBoxLayout(language_card)
        language_layout.setContentsMargins(18, 16, 18, 18)
        language_layout.setSpacing(12)
        language_layout.addWidget(self._label("界面语言", "SectionTitle"))
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
        theme_layout.addWidget(self._label("外观主题", "SectionTitle"))
        theme_row = QHBoxLayout()
        theme_row.addWidget(self.theme_light_button)
        theme_row.addWidget(self.theme_dark_button)
        theme_row.addWidget(self.theme_system_button)
        theme_row.addStretch(1)
        theme_layout.addLayout(theme_row)
        layout.addWidget(theme_card)

        backup_card = self._card()
        backup_layout = QVBoxLayout(backup_card)
        backup_layout.setContentsMargins(18, 16, 18, 18)
        backup_layout.setSpacing(12)
        backup_layout.addWidget(self._label("配置备份", "SectionTitle"))
        backup_row = QHBoxLayout()
        backup_row.addWidget(self.export_config_button)
        backup_row.addWidget(self.import_config_button)
        backup_row.addStretch(1)
        backup_layout.addLayout(backup_row)
        layout.addWidget(backup_card)
        layout.addStretch(1)
        return card

    def _build_view_switch(self) -> QFrame:
        switch = QFrame()
        switch.setObjectName("ActionBar")
        layout = QHBoxLayout(switch)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        layout.addWidget(self.harnesses_view_button)
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
        copy.addWidget(self._label("Harness Manager（任务套件管理器）", "PageTitle"))
        subtitle = self._label(
            "整理可复用技能集合，导出离线包，并部署到 Codex、Claude Code 或 OpenCode。",
            "MutedText",
        )
        subtitle.setWordWrap(True)
        copy.addWidget(subtitle)
        layout.addLayout(copy, 1)

        hero_stat = QFrame()
        hero_stat.setObjectName("StatCard")
        stat_layout = QVBoxLayout(hero_stat)
        stat_layout.setContentsMargins(16, 12, 16, 12)
        stat_layout.setSpacing(2)
        stat_layout.addWidget(self._label("本地工作流", "StatLabel"))
        stat_layout.addWidget(self._label("任务套件管理中心", "MutedText"))
        layout.addWidget(hero_stat, 0)
        return hero

    def _build_harnesses_card(self) -> QFrame:
        card = self._card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 20)
        layout.setSpacing(12)
        header = self._section_header("任务套件", "把 AGENTS.md、MCP 和技能整理成可复用的任务工作台。")
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
        asset_actions = QFrame()
        asset_actions.setObjectName("ActionBar")
        asset_layout = QHBoxLayout(asset_actions)
        asset_layout.setContentsMargins(10, 10, 10, 10)
        asset_layout.setSpacing(8)
        asset_layout.addWidget(self.add_agents_button)
        asset_layout.addWidget(self.add_mcp_button)
        asset_layout.addWidget(self.add_skill_asset_button)
        asset_layout.addStretch(1)
        layout.addWidget(asset_actions)
        layout.addWidget(self.skill_list, 1)

        layout.addWidget(self._label("部署套件（待接入）", "SectionTitle"))
        layout.addWidget(
            self._deploy_row("Codex", "C", self.install_codex_button, self.uninstall_codex_button)
        )
        layout.addWidget(
            self._deploy_row(
                "Claude Code", "CC", self.install_claude_button, self.uninstall_claude_button
            )
        )
        layout.addWidget(
            self._deploy_row(
                "OpenCode", "OC", self.install_opencode_button, self.uninstall_opencode_button
            )
        )
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
        title = self._label("MCP 服务器管理", "SectionTitle")
        subtitle = self._label("维护任务套件可复用的 MCP JSON 配置。", "MutedText")
        copy = QVBoxLayout()
        copy.setSpacing(4)
        copy.addWidget(title)
        copy.addWidget(subtitle)
        layout.addLayout(copy, 1)
        layout.addWidget(self.new_mcp_config_button)
        return toolbar

    def _build_mcp_summary(self) -> QWidget:
        summary = QFrame()
        summary.setObjectName("McpSummary")
        layout = QHBoxLayout(summary)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.addWidget(self._label(f"已配置 {len(self.library_assets)} 个 MCP", "MutedText"))
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
        if self.current_view == "mcp":
            self.asset_library_header_layout.addWidget(self._build_mcp_toolbar())
            self.asset_library_header_layout.addWidget(self._build_mcp_summary())
        else:
            self.asset_library_header_layout.addLayout(
                self._section_header("组件库", "按类型查看全部技能、AGENTS.md 与 MCP，并加入任务套件。")
            )

    def _asset_library_item(self, asset: Asset) -> QWidget:
        row = QFrame()
        row.setObjectName("AssetLibraryItem")
        row.setMinimumHeight(78)
        layout = QHBoxLayout(row)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        copy = QVBoxLayout()
        copy.setSpacing(4)
        title = self._label(asset.name, "ClientName")
        meta = self._label(
            f"类型：{self._asset_type_label(asset.type)} - 来源：{asset.source_type or '本地'} - ID：{asset.id}",
            "MutedText",
        )
        meta.setWordWrap(True)
        copy.addWidget(title)
        copy.addWidget(meta)
        layout.addLayout(copy, 1)

        add_button = self._button("加入套件", "CompactButton")
        add_button.setMinimumWidth(92)
        add_button.clicked.connect(
            self._guard(lambda asset=asset: self._add_asset_to_chosen_harness(asset))
        )
        layout.addWidget(add_button)

        if asset.type == "mcp":
            edit_button = self._button("编辑", "CompactButton")
            edit_button.setMinimumWidth(76)
            edit_button.clicked.connect(self._guard(lambda asset=asset: self._edit_mcp_config(asset)))
            layout.addWidget(edit_button)

        remove_button = self._button("移出套件", "CompactButton")
        remove_button.setMinimumWidth(92)
        remove_button.clicked.connect(
            self._guard(lambda asset=asset: self._remove_asset_from_chosen_harness(asset))
        )
        layout.addWidget(remove_button)
        return row

    def _deploy_row(
        self, title: str, badge: str, install_button: QPushButton, uninstall_button: QPushButton
    ) -> QFrame:
        row = QFrame()
        row.setObjectName("DeployRow")
        layout = QHBoxLayout(row)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)

        badge_label = self._label(badge, "MutedText")
        badge_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge_label.setFixedWidth(34)
        badge_label.setStyleSheet(
            "background: #dbeafe; color: #1d4ed8; border-radius: 10px; font-weight: 800;"
        )
        name = self._label(title, "SectionTitle")
        layout.addWidget(badge_label)
        layout.addWidget(name, 1)
        layout.addWidget(install_button)
        layout.addWidget(uninstall_button)
        return row

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
        status = self._label("就绪" if ready else "缺失", "ClientStatusReady" if ready else "ClientStatusMissing")
        status.setMinimumWidth(48)
        status.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        header.addWidget(name, 1)
        header.addWidget(status)
        layout.addLayout(header)

        path_label = self._label(str(path) if path else "未配置路径", "ClientPath")
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
        status = self._label("自定义", "ClientStatusReady")
        status.setMinimumWidth(48)
        status.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        header.addWidget(status)
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
        self.import_skill_button.clicked.connect(self._guard(self._import_skill))
        self.add_custom_source_button.clicked.connect(self._guard(self._add_custom_source))
        self.settings_button.clicked.connect(self._show_settings_view)
        self.back_to_business_button.clicked.connect(self._show_previous_business_view)
        self.harnesses_view_button.clicked.connect(self._show_harnesses_view)
        self.agents_view_button.clicked.connect(lambda: self._show_asset_view("agents_md"))
        self.mcp_view_button.clicked.connect(lambda: self._show_asset_view("mcp"))
        self.skills_view_button.clicked.connect(self._show_skills_view)
        self.new_package_button.clicked.connect(self._guard(self._new_harness))
        self.edit_harness_button.clicked.connect(self._guard(self._edit_harness))
        self.add_agents_button.clicked.connect(self._guard(self._import_agents_to_harness))
        self.add_mcp_button.clicked.connect(self._guard(self._import_mcp_to_harness))
        self.new_mcp_config_button.clicked.connect(self._guard(self._new_mcp_config))
        self.add_skill_asset_button.clicked.connect(self._guard(self._add_first_skill_to_harness))
        self.import_archive_button.clicked.connect(self._guard(self._import_archive))
        self.export_archive_button.clicked.connect(self._guard(self._export_archive))
        self.install_codex_button.clicked.connect(self._guard(lambda: self._install("codex")))
        self.uninstall_codex_button.clicked.connect(self._guard(lambda: self._uninstall("codex")))
        self.install_claude_button.clicked.connect(
            self._guard(lambda: self._install("claude_code"))
        )
        self.uninstall_claude_button.clicked.connect(
            self._guard(lambda: self._uninstall("claude_code"))
        )
        self.install_opencode_button.clicked.connect(
            self._guard(lambda: self._install("opencode"))
        )
        self.uninstall_opencode_button.clicked.connect(
            self._guard(lambda: self._uninstall("opencode"))
        )
        self.language_zh_button.clicked.connect(self._guard(lambda: self._save_language("zh-CN")))
        self.language_en_button.clicked.connect(self._guard(lambda: self._save_language("en-US")))
        self.theme_light_button.clicked.connect(self._guard(lambda: self._save_theme("light")))
        self.theme_dark_button.clicked.connect(self._guard(lambda: self._save_theme("dark")))
        self.theme_system_button.clicked.connect(self._guard(lambda: self._save_theme("system")))
        self.export_config_button.clicked.connect(self._guard(self._export_full_config))
        self.import_config_button.clicked.connect(self._guard(self._import_full_config))

    def _guard(self, callback: Callable[[], None]) -> Callable[[], None]:
        def wrapped() -> None:
            try:
                callback()
            except Exception as exc:
                dialogs.show_error(self, "错误", str(exc))

        return wrapped

    def refresh(self) -> None:
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

        self.harness_list.clear()
        if self.harnesses:
            for index, harness in enumerate(self.harnesses):
                skills = self.controller.list_harness_assets(harness.id)
                description = harness.description or "暂无描述"
                self.harness_list.addItem(
                    f"{harness.name}\n{len(skills)} 个组件 - {description}"
                )
            self.harness_list.setCurrentRow(min(max(selected_row, 0), len(self.harnesses) - 1))
        else:
            self.harness_list.addItem("暂无任务套件\n可以先新建空套件，再导入或关联组件。")
            self._refresh_harness_assets(-1)
        self._refresh_asset_library(all_skills)

    def _refresh_view_state(self) -> None:
        harness_active = self.current_view == "harnesses"
        self.harnesses_body.setVisible(harness_active)
        settings_active = self.current_view == "settings"
        self.settings_body.setVisible(settings_active)
        self.skills_body.setVisible(not harness_active and not settings_active)
        self.harnesses_view_button.setObjectName(
            "SegmentButtonChecked" if harness_active else "SegmentButton"
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
        self.skills_view_button.style().unpolish(self.skills_view_button)
        self.skills_view_button.style().polish(self.skills_view_button)
        self.agents_view_button.style().unpolish(self.agents_view_button)
        self.agents_view_button.style().polish(self.agents_view_button)
        self.mcp_view_button.style().unpolish(self.mcp_view_button)
        self.mcp_view_button.style().polish(self.mcp_view_button)
        self.new_mcp_config_button.setVisible(self.current_view == "mcp")
        self.settings_button.setObjectName(
            "IconButtonChecked" if settings_active else "IconButton"
        )
        self.settings_button.style().unpolish(self.settings_button)
        self.settings_button.style().polish(self.settings_button)

    def _refresh_asset_library(self, skills: list[Skill]) -> None:
        self.library_skill_list.clear()
        if self.current_view == "agents_md":
            self.library_assets = self.controller.list_assets_by_type("agents_md")
            empty_text = "暂无 AGENTS.md\n请先在任务套件详情中添加 AGENTS.md。"
        elif self.current_view == "mcp":
            self.library_assets = self.controller.list_assets_by_type("mcp")
            empty_text = "暂无 MCP\n请先在任务套件详情中添加 MCP 配置。"
        else:
            self.library_assets = self.controller.list_assets_by_type("skill")
            empty_text = "暂无技能\n请从左侧选择客户端并导入技能。"
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
            item.setSizeHint(QSize(0, 86))
            self.library_skill_list.addItem(item)
            self.library_skill_list.setItemWidget(item, widget)
        self._refresh_asset_library_header()

    def _refresh_current_asset_library(self) -> None:
        self._refresh_asset_library(self.controller.list_skills())

    def _show_harnesses_view(self) -> None:
        self.current_view = "harnesses"
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
        client_name = self._selected_client_name()
        self.import_skill_button.setText(f"从 {client_name} 导入" if client_name else "从选中来源导入")
        self._clear_client_cards()
        for client in self.clients:
            self._add_client_card(client)
        for source in self.controller.list_custom_import_sources():
            self._add_custom_source_card(source)

    def _select_custom_source(self, source_id: str) -> None:
        self.selected_client_type = None
        self.selected_custom_source_id = source_id
        self.import_skill_button.setText("从自定义目录导入")
        self._clear_client_cards()
        for client in self.clients:
            self._add_client_card(client)
        for source in self.controller.list_custom_import_sources():
            self._add_custom_source_card(source)

    def _selected_client_name(self) -> str | None:
        for client in self.clients:
            if client.type == self.selected_client_type:
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
            self.current_harness_title.setText("选择一个任务套件")
            self.current_harness_meta.setText("任务套件详情会显示在这里。")
            self.skill_list.addItem("未选择任务套件\n请从左侧列表选择一个任务套件。")
            return

        harness = self.harnesses[row]
        self.harness_assets = self.controller.list_harness_assets(harness.id)
        self.current_harness_title.setText(harness.name)
        self.current_harness_meta.setText(
            f"包含 {len(self.harness_assets)} 个组件"
            + (f" - {harness.description}" if harness.description else "")
        )
        self._add_asset_group(
            "已加入的技能",
            self.controller.list_harness_assets_by_type(harness.id, "skill"),
            "暂无技能",
        )
        self._add_asset_group(
            "已加入的 AGENTS.md",
            self.controller.list_harness_assets_by_type(harness.id, "agents_md"),
            "暂无 AGENTS.md",
        )
        self._add_asset_group(
            "已加入的 MCP",
            self.controller.list_harness_assets_by_type(harness.id, "mcp"),
            "暂无 MCP",
        )

    def _add_asset_group(self, title: str, assets: list[Asset], empty_text: str) -> None:
        if not assets:
            self.skill_list.addItem(f"{title}\n0 个组件 - {empty_text}")
            return
        names = "、".join(asset.name for asset in assets)
        self.skill_list.addItem(f"{title}\n{len(assets)} 个组件：{names}")

    def _asset_type_label(self, asset_type: str) -> str:
        return {"agents_md": "AGENTS.md", "mcp": "MCP", "skill": "技能"}.get(asset_type, "组件")

    def _selected_harness_row(self) -> int | None:
        row = self.harness_list.currentRow()
        return row if 0 <= row < len(self.harnesses) else None

    def _require_harness_row(self) -> int:
        row = self._selected_harness_row()
        if row is None:
            raise ValueError("请先选择一个任务套件。")
        return row

    def _import_skill(self) -> None:
        if self.selected_custom_source_id is not None:
            imported = self.controller.import_from_custom_source(self.selected_custom_source_id)
            self.refresh()
            dialogs.show_info(self, "导入完成", f"已导入 {len(imported)} 个技能。")
            return
        if self.selected_client_type is None:
            raise ValueError("请先选择导入来源。")
        try:
            imported = self.controller.import_from_client_source(self.selected_client_type)
        except (ValueError, NotADirectoryError):
            client_name = self._selected_client_name() or "当前应用"
            source = dialogs.choose_directory(self, f"配置目录：{client_name}")
            if source is None:
                return
            self.controller.set_client_custom_path(self.selected_client_type, source)
            imported = self.controller.import_from_client_source(self.selected_client_type)
        self.refresh()
        dialogs.show_info(self, "导入完成", f"已导入 {len(imported)} 个技能。")

    def _add_custom_source(self) -> None:
        source = dialogs.choose_directory(self, "添加自定义目录")
        if source is None:
            return
        name = dialogs.ask_text(self, "添加自定义目录", "来源名称")
        if not name:
            name = source.name
        source_id = self.controller.add_custom_import_source(name, source)
        self.refresh()
        self._select_custom_source(source_id)
        dialogs.show_info(self, "添加完成", f"已添加自定义目录 {name}。")

    def _new_harness(self) -> None:
        details = dialogs.ask_harness_details(self, "新建任务套件")
        if details is None:
            return
        name, description = details
        self.controller.create_harness(name, description)
        self.refresh()
        dialogs.show_info(self, "创建完成", f"已创建任务套件 {name}。")

    def _edit_harness(self) -> None:
        harness = self._selected_harness()
        details = dialogs.ask_harness_details(
            self, "编辑任务套件", harness.name, harness.description
        )
        if details is None:
            return
        name, description = details
        self.controller.update_harness(harness.id, name, description)
        self.refresh()
        dialogs.show_info(self, "保存完成", f"已更新任务套件 {name}。")

    def _selected_harness(self) -> Harness:
        row = self._require_harness_row()
        return self.harnesses[row]

    def _import_agents_to_harness(self) -> None:
        source = dialogs.choose_asset_file(self, "导入 AGENTS.md", "AGENTS.md (AGENTS.md);;Markdown (*.md);;所有文件 (*)")
        if source is None:
            return
        name = dialogs.ask_text(self, "添加 AGENTS.md", "组件名称") or source.stem
        asset = self.controller.import_agents_md_asset(source, name)
        self.controller.add_asset_to_harness(self._selected_harness().id, asset.id, asset.type)
        self.refresh()
        dialogs.show_info(self, "添加完成", f"已将 {name} 加入任务套件。")

    def _import_mcp_to_harness(self) -> None:
        source = dialogs.choose_asset_file(self, "导入 MCP", "JSON 配置 (*.json);;所有文件 (*)")
        if source is None:
            return
        name = dialogs.ask_text(self, "添加 MCP", "组件名称") or source.stem
        asset = self.controller.import_mcp_asset(source, name)
        self.controller.add_asset_to_harness(self._selected_harness().id, asset.id, asset.type)
        self.refresh()
        dialogs.show_info(self, "添加完成", f"已将 {name} 加入任务套件。")

    def _new_mcp_config(self) -> None:
        details = dialogs.ask_mcp_config(self, "新建 MCP 配置")
        if details is None:
            return
        title, display_name, config_json = details
        self.controller.create_mcp_config_asset(title, display_name, config_json)
        self.refresh()
        dialogs.show_info(self, "保存完成", f"已保存 MCP 配置 {title}。")

    def _edit_mcp_config(self, asset: Asset) -> None:
        config_path = self.controller.paths.root / asset.relative_path
        details = dialogs.ask_mcp_config(
            self,
            "编辑 MCP 配置",
            asset.name,
            asset.name,
            config_path.read_text(encoding="utf-8"),
        )
        if details is None:
            return
        title, display_name, config_json = details
        self.controller.update_mcp_config_asset(asset.id, title, display_name, config_json)
        self.refresh()
        dialogs.show_info(self, "保存完成", f"已更新 MCP 配置 {title}。")

    def _apply_theme(self, theme: str) -> None:
        self.current_theme = theme
        self.setStyleSheet(build_stylesheet(self._resolved_theme(theme)))

    def _resolved_theme(self, theme: str) -> str:
        if theme != "system":
            return theme
        window_color = QApplication.palette().color(QPalette.ColorRole.Window)
        return "dark" if window_color.lightness() < 128 else "light"

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
        self.theme_system_button.setObjectName(
            "PrimaryButton" if settings.theme == "system" else "CompactButton"
        )
        for button in [
            self.language_zh_button,
            self.language_en_button,
            self.theme_light_button,
            self.theme_dark_button,
            self.theme_system_button,
        ]:
            button.style().unpolish(button)
            button.style().polish(button)

    def _save_language(self, language: str) -> None:
        settings = self.controller.save_language(language)
        self._refresh_settings_buttons(settings)
        dialogs.show_info(self, "保存完成", "语言设置已保存。")

    def _save_theme(self, theme: str) -> None:
        settings = self.controller.save_theme(theme)
        self._apply_theme(settings.theme)
        self._refresh_settings_buttons(settings)
        dialogs.show_info(self, "保存完成", "外观主题已保存。")

    def _export_full_config(self) -> None:
        destination = dialogs.choose_export_zip(self)
        if destination is None:
            return
        archive = self.controller.export_full_config(destination)
        dialogs.show_info(self, "导出完成", f"已导出到 {archive}。")

    def _import_full_config(self) -> None:
        archive = dialogs.choose_config_archive(self)
        if archive is None:
            return
        backup = self.controller.import_full_config(archive)
        self.refresh()
        dialogs.show_info(self, "导入完成", f"已导入配置，原配置已备份到 {backup}。")

    def _add_first_skill_to_harness(self) -> None:
        skills = self.controller.list_assets_by_type("skill")
        if not skills:
            raise ValueError("当前没有可加入的技能，请先从左侧导入技能。")
        asset = skills[0]
        self.controller.add_asset_to_harness(self._selected_harness().id, asset.id, asset.type)
        self.refresh()
        dialogs.show_info(self, "添加完成", f"已将技能 {asset.name} 加入任务套件。")

    def _add_asset_to_chosen_harness(self, asset: Asset) -> None:
        available_harnesses = self.controller.list_harnesses_without_asset(asset.id)
        if not available_harnesses:
            if self.harnesses:
                dialogs.show_info(self, "无需重复加入", f"{asset.name} 已经加入所有任务套件。")
                return
            raise ValueError("当前没有任务套件，请先新建任务套件。")
        harness = dialogs.choose_harness(self, available_harnesses)
        if harness is None:
            return
        self.controller.add_asset_to_harness(harness.id, asset.id, asset.type)
        self.refresh()
        dialogs.show_info(self, "添加完成", f"已将 {asset.name} 加入 {harness.name}。")

    def _remove_asset_from_chosen_harness(self, asset: Asset) -> None:
        joined_harnesses = self.controller.list_harnesses_with_asset(asset.id)
        if not joined_harnesses:
            dialogs.show_info(self, "无需移出", f"{asset.name} 尚未加入任何任务套件。")
            return
        harness = dialogs.choose_harness(
            self,
            joined_harnesses,
            title="选择要移出的任务套件",
            message="请选择要移出该组件的任务套件",
            confirm_text="移出",
        )
        if harness is None:
            return
        self.controller.remove_asset_from_harness(harness.id, asset.id)
        self.refresh()
        dialogs.show_info(self, "移出完成", f"已将 {asset.name} 从 {harness.name} 移出。")

    def _import_archive(self) -> None:
        archive = dialogs.choose_archive(self)
        if archive is None:
            return
        self.controller.import_offline_package(archive)
        self.refresh()
        dialogs.show_info(self, "导入完成", f"已导入 {archive.name}。")

    def _export_archive(self) -> None:
        archive = self.controller.export_package_by_row(self._require_harness_row())
        dialogs.show_info(self, "导出完成", f"已导出到 {archive}。")

    def _install(self, client_type: ClientType) -> None:
        installed = self.controller.install_package_by_row(
            self._require_harness_row(), client_type
        )
        dialogs.show_info(self, "安装完成", f"已安装 {len(installed)} 个技能。")

    def _uninstall(self, client_type: ClientType) -> None:
        result = self.controller.uninstall_package_by_row(
            self._require_harness_row(), client_type
        )
        if result:
            message = ", ".join(f"{skill_id}: {status}" for skill_id, status in result.items())
        else:
            message = "没有找到可卸载的安装记录。"
        dialogs.show_info(self, "卸载结果", message)


def run_app(argv: list[str] | None = None) -> int:
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
