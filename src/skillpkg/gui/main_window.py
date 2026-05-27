from __future__ import annotations

import sys
from collections.abc import Callable
from pathlib import Path

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
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

from skillpkg.app_paths import AppPaths
from skillpkg.db import connect
from skillpkg.gui import dialogs
from skillpkg.gui.controllers import MainController
from skillpkg.gui.styles import build_stylesheet
from skillpkg.models import Asset, ClientConfig, ClientType, Harness, Skill


class MainWindow(QMainWindow):
    def __init__(self, controller: MainController) -> None:
        super().__init__()
        self.controller = controller
        self.clients: list[ClientConfig] = []
        self.harnesses: list[Harness] = []
        self.harness_assets: list[Asset] = []
        self.library_assets: list[Asset] = []
        self.client_cards_layout: QVBoxLayout | None = None
        self.selected_client_type: ClientType | None = None
        self.selected_custom_source_id: str | None = None
        self.current_view = "harnesses"

        self.setWindowTitle("Harness Manager（任务套件管理器）")
        self.resize(1240, 760)
        self.setMinimumSize(980, 620)
        self.setStyleSheet(build_stylesheet())

        self.harness_list = QListWidget()
        self.skill_list = QListWidget()
        self.library_skill_list = QListWidget()
        self.harness_count_value = self._label("0", "StatValue")
        self.skill_count_value = self._label("0", "StatValue")
        self.current_harness_title = self._label("选择一个任务套件", "SectionTitle")
        self.current_harness_meta = self._label("任务套件详情会显示在这里。", "MutedText")

        self.import_skill_button = self._button("选择客户端", "PrimaryButton")
        self.add_custom_source_button = self._button("添加自定义目录", "CompactButton")
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
        self.new_mcp_config_button = self._button("新建 MCP 配置", "PrimaryButton")
        self.add_skill_asset_button = self._button("添加技能", "CompactButton")
        self.install_codex_button = self._button("安装", "DeployInstallButton")
        self.uninstall_codex_button = self._button("卸载", "DeployUninstallButton")
        self.install_claude_button = self._button("安装", "DeployInstallButton")
        self.uninstall_claude_button = self._button("卸载", "DeployUninstallButton")
        self.install_opencode_button = self._button("安装", "DeployInstallButton")
        self.uninstall_opencode_button = self._button("卸载", "DeployUninstallButton")
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
        shell = QHBoxLayout(root)
        shell.setContentsMargins(18, 18, 18, 18)
        shell.setSpacing(18)

        shell.addWidget(self._build_sidebar(), 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setWidget(self._build_workspace())
        shell.addWidget(scroll, 1)
        self.setCentralWidget(root)

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
        layout.setHorizontalSpacing(18)
        layout.setVerticalSpacing(4)

        harness_label = self._label("任务套件", "SidebarSubtitle")
        skill_label = self._label("技能", "SidebarSubtitle")
        self.harness_count_value.setStyleSheet("color: #f8fafc;")
        self.skill_count_value.setStyleSheet("color: #f8fafc;")
        layout.addWidget(self.harness_count_value, 0, 0)
        layout.addWidget(self.skill_count_value, 0, 1)
        layout.addWidget(harness_label, 1, 0)
        layout.addWidget(skill_label, 1, 1)
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
        return workspace

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
        layout.addLayout(
            self._section_header("组件库", "按类型查看全部技能、AGENTS.md 与 MCP，并加入任务套件。")
        )
        layout.addWidget(self.new_mcp_config_button)
        layout.addWidget(self.library_skill_list, 1)
        return card

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
        card.setMinimumHeight(76)
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.mousePressEvent = lambda _event, client_type=client.type: self._select_client(client_type)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 11, 14, 11)
        layout.setSpacing(4)

        header = QHBoxLayout()
        name = self._label(client.name, "ClientName")
        status = self._label("就绪" if ready else "缺失", "ClientStatusReady" if ready else "ClientStatusMissing")
        status.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        header.addWidget(name, 1)
        header.addWidget(status)
        layout.addLayout(header)

        path_label = self._label(str(path) if path else "未配置路径", "ClientPath")
        path_label.setWordWrap(True)
        layout.addWidget(path_label)
        return card

    def _custom_source_card(self, source: dict[str, object]) -> QFrame:
        selected = source["id"] == self.selected_custom_source_id
        card = QFrame()
        card.setObjectName("ClientCardSelected" if selected else "ClientCard")
        card.setMinimumHeight(76)
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        source_id = str(source["id"])
        card.mousePressEvent = lambda _event, current_id=source_id: self._select_custom_source(
            current_id
        )
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 11, 14, 11)
        layout.setSpacing(4)
        header = QHBoxLayout()
        header.addWidget(self._label(str(source["name"]), "ClientName"), 1)
        status = self._label("自定义", "ClientStatusReady")
        status.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        header.addWidget(status)
        layout.addLayout(header)
        path_label = self._label(str(source["path"]), "ClientPath")
        path_label.setWordWrap(True)
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
        self.harness_list.currentRowChanged.connect(self._refresh_harness_assets)
        self.import_skill_button.clicked.connect(self._guard(self._import_skill))
        self.add_custom_source_button.clicked.connect(self._guard(self._add_custom_source))
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

    def _guard(self, callback: Callable[[], None]) -> Callable[[], None]:
        def wrapped() -> None:
            try:
                callback()
            except Exception as exc:
                dialogs.show_error(self, "错误", str(exc))

        return wrapped

    def refresh(self) -> None:
        selected_row = self.harness_list.currentRow()
        self.clients = self.controller.list_clients()
        self.harnesses = self.controller.list_harnesses()

        all_skills = self.controller.list_skills()
        self.harness_count_value.setText(str(len(self.harnesses)))
        self.skill_count_value.setText(str(len(all_skills)))
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
        self.skills_body.setVisible(not harness_active)
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
            return
        for asset in self.library_assets:
            item = QListWidgetItem()
            widget = self._asset_library_item(asset)
            item.setSizeHint(QSize(0, 86))
            self.library_skill_list.addItem(item)
            self.library_skill_list.setItemWidget(item, widget)

    def _show_harnesses_view(self) -> None:
        self.current_view = "harnesses"
        self._refresh_view_state()

    def _show_asset_view(self, asset_type: str) -> None:
        self.current_view = asset_type
        self._refresh_view_state()

    def _show_skills_view(self) -> None:
        self.current_view = "skills"
        self._refresh_view_state()

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
        title, display_name, mcp_kind, config_json = details
        self.controller.create_mcp_config_asset(title, display_name, mcp_kind, config_json)
        self.refresh()
        dialogs.show_info(self, "保存完成", f"已保存 MCP 配置 {title}。")

    def _edit_mcp_config(self, asset: Asset) -> None:
        config_path = self.controller.paths.root / asset.relative_path
        details = dialogs.ask_mcp_config(
            self,
            "编辑 MCP 配置",
            asset.name,
            asset.name,
            "custom",
            config_path.read_text(encoding="utf-8"),
        )
        if details is None:
            return
        title, display_name, mcp_kind, config_json = details
        self.controller.update_mcp_config_asset(asset.id, title, display_name, mcp_kind, config_json)
        self.refresh()
        dialogs.show_info(self, "保存完成", f"已更新 MCP 配置 {title}。")

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

