from __future__ import annotations

import sys
from collections.abc import Callable
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
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
from skillpkg.models import ClientConfig, ClientType, Package, Skill


class MainWindow(QMainWindow):
    def __init__(self, controller: MainController) -> None:
        super().__init__()
        self.controller = controller
        self.clients: list[ClientConfig] = []
        self.packages: list[Package] = []
        self.package_skills: list[Skill] = []
        self.client_cards_layout: QVBoxLayout | None = None
        self.selected_client_type: ClientType | None = None
        self.selected_custom_source_id: str | None = None
        self.current_view = "packages"

        self.setWindowTitle("Harness Manager（技能包管理器）")
        self.resize(1240, 760)
        self.setMinimumSize(980, 620)
        self.setStyleSheet(build_stylesheet())

        self.package_list = QListWidget()
        self.skill_list = QListWidget()
        self.library_skill_list = QListWidget()
        self.package_count_value = self._label("0", "StatValue")
        self.skill_count_value = self._label("0", "StatValue")
        self.current_package_title = self._label("选择一个软件包", "SectionTitle")
        self.current_package_meta = self._label("软件包详情会显示在这里。", "MutedText")

        self.import_skill_button = self._button("选择客户端", "PrimaryButton")
        self.add_custom_source_button = self._button("添加自定义目录", "CompactButton")
        self.packages_view_button = self._button("软件包", "SegmentButtonChecked")
        self.agents_view_button = self._button("AGENTS.md", "SegmentButton")
        self.mcp_view_button = self._button("MCP", "SegmentButton")
        self.skills_view_button = self._button("技能库 Skills", "SegmentButton")
        self.new_package_button = self._button("新建包", "PrimaryButton")
        self.import_archive_button = self._button("导入包", "CompactButton")
        self.export_archive_button = self._button("导出包", "CompactButton")
        self.install_codex_button = self._button("安装", "DeployInstallButton")
        self.uninstall_codex_button = self._button("卸载", "DeployUninstallButton")
        self.install_claude_button = self._button("安装", "DeployInstallButton")
        self.uninstall_claude_button = self._button("卸载", "DeployUninstallButton")
        self.install_opencode_button = self._button("安装", "DeployInstallButton")
        self.uninstall_opencode_button = self._button("卸载", "DeployUninstallButton")

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

        title = self._label("技能包", "AppTitle")
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

        package_label = self._label("软件包", "SidebarSubtitle")
        skill_label = self._label("技能", "SidebarSubtitle")
        self.package_count_value.setStyleSheet("color: #f8fafc;")
        self.skill_count_value.setStyleSheet("color: #f8fafc;")
        layout.addWidget(self.package_count_value, 0, 0)
        layout.addWidget(self.skill_count_value, 0, 1)
        layout.addWidget(package_label, 1, 0)
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
        self.packages_body = QWidget()
        packages_body_layout = QHBoxLayout(self.packages_body)
        packages_body_layout.setContentsMargins(0, 0, 0, 0)
        packages_body_layout.setSpacing(16)
        packages_body_layout.addWidget(self._build_packages_card(), 5)
        packages_body_layout.addWidget(self._build_details_card(), 4)
        layout.addWidget(self.packages_body, 1)
        self.skills_body = self._build_skills_library_card()
        layout.addWidget(self.skills_body, 1)
        return workspace

    def _build_view_switch(self) -> QFrame:
        switch = QFrame()
        switch.setObjectName("ActionBar")
        layout = QHBoxLayout(switch)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        layout.addWidget(self.packages_view_button)
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
        copy.addWidget(self._label("Harness Manager（技能包管理器）", "PageTitle"))
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
        stat_layout.addWidget(self._label("技能包管理中心", "MutedText"))
        layout.addWidget(hero_stat, 0)
        return hero

    def _build_packages_card(self) -> QFrame:
        card = self._card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 20)
        layout.setSpacing(12)
        header = self._section_header("软件包", "把技能整理成可一键安装的工作集合。")
        layout.addLayout(header)
        layout.addWidget(self._build_package_actions())
        layout.addWidget(self.package_list, 1)
        return card

    def _build_package_actions(self) -> QFrame:
        bar = QFrame()
        bar.setObjectName("ActionBar")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        layout.addWidget(self.new_package_button)
        layout.addWidget(self.import_archive_button)
        layout.addWidget(self.export_archive_button)
        layout.addStretch(1)
        return bar

    def _build_details_card(self) -> QFrame:
        card = self._card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 20)
        layout.setSpacing(14)
        layout.addWidget(self.current_package_title)
        layout.addWidget(self.current_package_meta)
        layout.addWidget(self.skill_list, 1)

        layout.addWidget(self._label("部署包", "SectionTitle"))
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
        layout.addLayout(self._section_header("全部技能 Skills", "当前工具管理的所有技能，包含来源与内部 ID。"))
        layout.addWidget(self.library_skill_list, 1)
        return card

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
        self.package_list.currentRowChanged.connect(self._refresh_package_skills)
        self.import_skill_button.clicked.connect(self._guard(self._import_skill))
        self.add_custom_source_button.clicked.connect(self._guard(self._add_custom_source))
        self.packages_view_button.clicked.connect(self._show_packages_view)
        self.skills_view_button.clicked.connect(self._show_skills_view)
        self.new_package_button.clicked.connect(self._guard(self._new_package))
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
        selected_row = self.package_list.currentRow()
        self.clients = self.controller.list_clients()
        self.packages = self.controller.list_packages()

        all_skills = self.controller.list_skills()
        self.package_count_value.setText(str(len(self.packages)))
        self.skill_count_value.setText(str(len(all_skills)))
        self._refresh_view_state()

        self._clear_client_cards()
        for client in self.clients:
            self._add_client_card(client)
        for source in self.controller.list_custom_import_sources():
            self._add_custom_source_card(source)

        self.package_list.clear()
        if self.packages:
            for index, package in enumerate(self.packages):
                skills = self.controller.list_skills(index)
                description = package.description or "暂无描述"
                self.package_list.addItem(
                    f"{package.name}\n{len(skills)} 个技能 - {description}"
                )
            self.package_list.setCurrentRow(min(max(selected_row, 0), len(self.packages) - 1))
        else:
            self.package_list.addItem("暂无软件包\n可以先新建空包，再导入或关联技能。")
            self._refresh_package_skills(-1)
        self._refresh_skill_library(all_skills)

    def _refresh_view_state(self) -> None:
        package_active = self.current_view == "packages"
        self.packages_body.setVisible(package_active)
        self.skills_body.setVisible(not package_active)
        self.packages_view_button.setObjectName(
            "SegmentButtonChecked" if package_active else "SegmentButton"
        )
        self.skills_view_button.setObjectName(
            "SegmentButtonChecked" if not package_active else "SegmentButton"
        )
        self.packages_view_button.style().unpolish(self.packages_view_button)
        self.packages_view_button.style().polish(self.packages_view_button)
        self.skills_view_button.style().unpolish(self.skills_view_button)
        self.skills_view_button.style().polish(self.skills_view_button)

    def _refresh_skill_library(self, skills: list[Skill]) -> None:
        self.library_skill_list.clear()
        if not skills:
            self.library_skill_list.addItem("暂无技能\n请从左侧选择客户端并导入技能。")
            return
        for skill in skills:
            source = skill.source_client or "离线包"
            self.library_skill_list.addItem(
                f"{skill.name}\n来源：{source} - ID：{skill.id}"
            )

    def _show_packages_view(self) -> None:
        self.current_view = "packages"
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

    def _refresh_package_skills(self, row: int) -> None:
        self.skill_list.clear()
        self.package_skills = []
        if row < 0 or row >= len(self.packages):
            self.current_package_title.setText("选择一个软件包")
            self.current_package_meta.setText("软件包详情会显示在这里。")
            self.skill_list.addItem("未选择软件包\n请从左侧列表选择一个软件包。")
            return

        package = self.packages[row]
        self.package_skills = self.controller.list_skills(row)
        self.current_package_title.setText(package.name)
        self.current_package_meta.setText(
            f"包含 {len(self.package_skills)} 个技能"
            + (f" - {package.description}" if package.description else "")
        )
        if not self.package_skills:
            self.skill_list.addItem("此软件包暂无技能\n可以稍后导入并关联技能。")
            return
        for skill in self.package_skills:
            source = skill.source_client or "离线包"
            self.skill_list.addItem(f"{skill.name}\n{source} - {skill.id}")

    def _selected_package_row(self) -> int | None:
        row = self.package_list.currentRow()
        return row if 0 <= row < len(self.packages) else None

    def _require_package_row(self) -> int:
        row = self._selected_package_row()
        if row is None:
            raise ValueError("请先选择一个软件包。")
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

    def _new_package(self) -> None:
        name = dialogs.ask_text(self, "新建软件包", "软件包名称")
        if not name:
            return
        self.controller.create_package(name, "")
        self.refresh()
        dialogs.show_info(self, "创建完成", f"已创建软件包 {name}。")

    def _import_archive(self) -> None:
        archive = dialogs.choose_archive(self)
        if archive is None:
            return
        self.controller.import_offline_package(archive)
        self.refresh()
        dialogs.show_info(self, "导入完成", f"已导入 {archive.name}。")

    def _export_archive(self) -> None:
        archive = self.controller.export_package_by_row(self._require_package_row())
        dialogs.show_info(self, "导出完成", f"已导出到 {archive}。")

    def _install(self, client_type: ClientType) -> None:
        installed = self.controller.install_package_by_row(
            self._require_package_row(), client_type
        )
        dialogs.show_info(self, "安装完成", f"已安装 {len(installed)} 个技能。")

    def _uninstall(self, client_type: ClientType) -> None:
        result = self.controller.uninstall_package_by_row(
            self._require_package_row(), client_type
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

