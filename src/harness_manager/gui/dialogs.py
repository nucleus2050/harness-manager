from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import json

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from harness_manager.gui.styles import _THEME_TOKENS

if TYPE_CHECKING:
    from harness_manager.models import Asset, Harness, Project

DIALOG_TEXT = {
    "zh-CN": {
        "ok": "确定",
        "cancel": "取消",
        "confirm_delete": "确认删除",
        "create": "创建",
        "save": "保存",
        "choose_harness": "选择任务套件",
        "choose_harness_message": "请选择要加入的任务套件",
        "join": "加入",
        "no_description": "暂无描述",
        "choose_asset": "选择组件",
        "choose_asset_message": "请选择要加入任务套件的组件",
        "continue": "继续",
        "harness_name": "套件名称",
        "harness_description": "套件描述",
        "add_agents": "添加 AGENTS.md",
        "agents_content": "# AGENTS.md\n\n在此输入提示词内容...",
        "name": "名称",
        "agents_name_placeholder": "例如：项目默认提示词",
        "description": "描述",
        "description_placeholder": "可选的描述信息",
        "content": "内容",
        "import_file": "选择文件导入",
        "choose_agents_file": "选择 AGENTS.md 文件",
        "all_files": "所有文件 (*)",
        "new_mcp": "新建 MCP 配置",
        "mcp_title": "MCP 标题（唯一）",
        "display_name": "显示名称",
        "mcp_display_placeholder": "例如 @modelcontextprotocol/server-time",
        "mcp_desc_placeholder": "例如：用于网页抓取、数据库查询或时间服务",
        "full_json": "完整 JSON 配置",
        "format": "格式化",
        "import_offline": "导入离线包",
        "harness_zip_filter": "任务套件 (*.harness.zip);;Zip 压缩包 (*.zip);;所有文件 (*)",
        "zip_filter": "Zip 压缩包 (*.zip);;所有文件 (*)",
        "export_config": "导出全部配置",
        "choose_harness_export": "选择套件导出目录",
        "choose_project_directory": "选择项目文件夹",
        "project_name": "项目名称",
        "project_path": "项目路径",
        "project_description": "项目描述",
        "project_name_placeholder": "例如：Harness Manager",
        "project_path_placeholder": "选择项目根目录",
        "add_project": "添加项目",
        "edit_project": "编辑项目",
        "manage_projects": "管理项目",
        "browse": "浏览",
        "import_config": "导入全部配置",
    },
    "en-US": {
        "ok": "OK",
        "cancel": "Cancel",
        "confirm_delete": "Delete",
        "create": "Create",
        "save": "Save",
        "choose_harness": "Choose Harness",
        "choose_harness_message": "Choose the harness to add to",
        "join": "Add",
        "no_description": "No description",
        "choose_asset": "Choose Component",
        "choose_asset_message": "Choose the component to add to the harness",
        "continue": "Continue",
        "harness_name": "Harness name",
        "harness_description": "Harness description",
        "add_agents": "Add AGENTS.md",
        "agents_content": "# AGENTS.md\n\nEnter instruction content here...",
        "name": "Name",
        "agents_name_placeholder": "Example: Default project instructions",
        "description": "Description",
        "description_placeholder": "Optional description",
        "content": "Content",
        "import_file": "Import from File",
        "choose_agents_file": "Choose AGENTS.md File",
        "all_files": "All Files (*)",
        "new_mcp": "New MCP Config",
        "mcp_title": "MCP title (unique)",
        "display_name": "Display name",
        "mcp_display_placeholder": "Example: @modelcontextprotocol/server-time",
        "mcp_desc_placeholder": "Example: web scraping, database queries, or time services",
        "full_json": "Full JSON Config",
        "format": "Format",
        "import_offline": "Import Offline Bundle",
        "harness_zip_filter": "Harness (*.harness.zip);;Zip archive (*.zip);;All Files (*)",
        "zip_filter": "Zip archive (*.zip);;All Files (*)",
        "export_config": "Export Full Config",
        "choose_harness_export": "Choose Harness Export Folder",
        "choose_project_directory": "Choose Project Folder",
        "project_name": "Project Name",
        "project_path": "Project Path",
        "project_description": "Project Description",
        "project_name_placeholder": "Example: Harness Manager",
        "project_path_placeholder": "Choose project root folder",
        "add_project": "Add Project",
        "edit_project": "Edit Project",
        "manage_projects": "Manage Projects",
        "browse": "Browse",
        "import_config": "Import Full Config",
    },
}


def _language(parent: QWidget | None) -> str:
    return getattr(parent, "current_language", "zh-CN")


def _tr(parent: QWidget | None, key: str) -> str:
    language = _language(parent)
    return DIALOG_TEXT.get(language, DIALOG_TEXT["zh-CN"]).get(
        key, DIALOG_TEXT["zh-CN"].get(key, key)
    )


def _dialog_theme_name(theme_source: QWidget | str | None) -> str:
    if isinstance(theme_source, str):
        return theme_source
    return getattr(theme_source, "current_theme", "light")


def _dialog_stylesheet(theme_source: QWidget | str | None = None) -> str:
    theme = _dialog_theme_name(theme_source)
    tokens = _THEME_TOKENS.get(theme, _THEME_TOKENS["light"])
    return f"""
    QDialog {{
        background: {tokens['card']};
        border-radius: 18px;
    }}
    QLabel {{
        background: transparent;
        color: {tokens['title']};
        font-family: "Segoe UI", "Microsoft YaHei UI", sans-serif;
    }}
    QLabel#DialogTitle {{
        font-size: 18px;
        font-weight: 800;
    }}
    QLabel#DialogMessage {{
        color: {tokens['muted']};
        font-size: 13px;
    }}
    QDialog#MessageDialog {{
        background: transparent;
    }}
    QFrame#DialogShell {{
        background: {tokens['card']};
        border: 1px solid {tokens['card_border']};
        border-radius: 22px;
    }}
    QFrame#DialogAccent {{
        background: {tokens['danger_text']};
        border-radius: 2px;
    }}
    QDialog#MessageDialog QLabel {{
        color: {tokens['title']};
    }}
    QDialog#MessageDialog QLabel#DialogMessage {{
        color: {tokens['muted']};
        font-size: 13px;
    }}
    QDialog#MessageDialog QLabel#DialogTitle {{
        color: {tokens['title']};
        font-size: 18px;
        font-weight: 900;
    }}
    QPushButton#DialogCloseButton {{
        min-width: 30px;
        max-width: 30px;
        min-height: 30px;
        max-height: 30px;
        border-radius: 15px;
        border: 1px solid transparent;
        background: transparent;
        color: {tokens['muted']};
        font-size: 16px;
        padding: 0;
    }}
    QPushButton#DialogCloseButton:hover {{
        background: {tokens['hover_bg']};
        border-color: {tokens['hover_border']};
        color: {tokens['title']};
    }}
    QLabel#DialogIcon {{
        min-width: 36px;
        min-height: 36px;
        max-width: 36px;
        max-height: 36px;
        border-radius: 18px;
        color: white;
        font-weight: 900;
        font-size: 18px;
    }}
    QLineEdit {{
        background: {tokens['soft_card']};
        border: 1px solid {tokens['compact_border']};
        border-radius: 12px;
        padding: 9px 11px;
        color: {tokens['title']};
        font-size: 13px;
    }}
    QLineEdit::placeholder {{
        color: {tokens['muted']};
    }}
    QPlainTextEdit {{
        background: {tokens['soft_card']};
        border: 1px solid {tokens['compact_border']};
        border-radius: 12px;
        padding: 9px 11px;
        color: {tokens['title']};
        font-size: 13px;
    }}
    QPushButton {{
        min-width: 82px;
        min-height: 34px;
        border-radius: 12px;
        border: 1px solid {tokens['compact_border']};
        background: {tokens['button_bg']};
        color: {tokens['button_text']};
        font-weight: 700;
        padding: 6px 14px;
    }}
    QPushButton:hover {{
        background: {tokens['hover_bg']};
        border-color: {tokens['hover_border']};
    }}
    QPushButton#PrimaryDialogButton {{
        background: {tokens['primary']};
        border-color: {tokens['primary']};
        color: #ffffff;
    }}
    QPushButton#PrimaryDialogButton:hover {{
        background: {tokens['primary_hover']};
    }}
    QPushButton#DangerDialogButton {{
        background: {tokens['danger_bg']};
        border-color: {tokens['danger_border']};
        color: {tokens['danger_text']};
    }}
    QPushButton#DangerDialogButton:hover {{
        background: {tokens['danger_hover']};
    }}
    QPushButton#GhostDialogButton {{
        background: {tokens['button_bg']};
        border-color: {tokens['compact_border']};
        color: {tokens['button_text']};
    }}
    QListWidget#HarnessPickerList {{
        background: {tokens['soft_card']};
        border: 1px solid {tokens['soft_border']};
        border-radius: 16px;
        padding: 8px;
    }}
    QListWidget#HarnessPickerList::item {{
        background: {tokens['card']};
        border: 1px solid {tokens['card_border']};
        border-radius: 14px;
        margin: 6px 0;
        padding: 14px;
        min-height: 54px;
        color: {tokens['list_text']};
    }}
    QListWidget#HarnessPickerList::item:selected {{
        background: {tokens['selected_bg']};
        border: 1px solid {tokens['selected_border']};
    }}
    """


class _MessageDialog(QDialog):
    def __init__(self, parent: QWidget, title: str, message: str, kind: str) -> None:
        super().__init__(parent)
        self.setObjectName("MessageDialog")
        self.setWindowTitle(title)
        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowCloseButtonHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.setMinimumWidth(440)
        self.setStyleSheet(_dialog_stylesheet(parent))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        shell = QFrame()
        shell.setObjectName("DialogShell")
        shell_layout = QVBoxLayout(shell)
        shell_layout.setContentsMargins(20, 18, 20, 18)
        shell_layout.setSpacing(16)

        top = QHBoxLayout()
        top.setSpacing(10)
        title_label = QLabel(title)
        title_label.setObjectName("DialogTitle")
        close = QPushButton("×")
        close.setObjectName("DialogCloseButton")
        close.clicked.connect(self.reject)
        top.addWidget(title_label, 1)
        top.addWidget(close)
        shell_layout.addLayout(top)

        accent = QFrame()
        accent.setObjectName("DialogAccent")
        accent.setFixedHeight(4)
        if kind != "error":
            accent.setStyleSheet("background: #2563eb; border-radius: 2px;")
        shell_layout.addWidget(accent)

        body = QHBoxLayout()
        body.setSpacing(14)
        icon = QLabel("!" if kind == "error" else "i")
        icon.setObjectName("DialogIcon")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet(
            "background: #ef4444;" if kind == "error" else "background: #2563eb;"
        )
        text = QVBoxLayout()
        message_label = QLabel(message)
        message_label.setObjectName("DialogMessage")
        message_label.setWordWrap(True)
        text.addWidget(message_label)
        body.addWidget(icon)
        body.addLayout(text, 1)
        shell_layout.addLayout(body)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        ok = QPushButton(_tr(parent, "ok"))
        ok.setObjectName("DangerDialogButton" if kind == "error" else "PrimaryDialogButton")
        ok.clicked.connect(self.accept)
        buttons.addWidget(ok)
        shell_layout.addLayout(buttons)
        layout.addWidget(shell)


class _ConfirmDialog(QDialog):
    def __init__(self, parent: QWidget, title: str, message: str) -> None:
        super().__init__(parent)
        self.setObjectName("MessageDialog")
        self.setWindowTitle(title)
        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowCloseButtonHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.setMinimumWidth(460)
        self.setStyleSheet(_dialog_stylesheet(parent))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        shell = QFrame()
        shell.setObjectName("DialogShell")
        shell_layout = QVBoxLayout(shell)
        shell_layout.setContentsMargins(20, 18, 20, 18)
        shell_layout.setSpacing(16)

        message_label = QLabel(message)
        message_label.setObjectName("DialogMessage")
        message_label.setWordWrap(True)
        shell_layout.addWidget(message_label)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        cancel = QPushButton(_tr(parent, "cancel"))
        cancel.setObjectName("GhostDialogButton")
        confirm = QPushButton(_tr(parent, "confirm_delete"))
        confirm.setObjectName("DangerDialogButton")
        cancel.clicked.connect(self.reject)
        confirm.clicked.connect(self.accept)
        buttons.addWidget(cancel)
        buttons.addWidget(confirm)
        shell_layout.addLayout(buttons)
        layout.addWidget(shell)


class _TextDialog(QDialog):
    def __init__(self, parent: QWidget, title: str, label: str) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(460)
        self.setStyleSheet(_dialog_stylesheet(parent))
        self.input = QLineEdit()
        self.input.setPlaceholderText(label)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 18)
        layout.setSpacing(14)
        title_label = QLabel(title)
        title_label.setObjectName("DialogTitle")
        label_text = QLabel(label)
        label_text.setObjectName("DialogMessage")
        layout.addWidget(title_label)
        layout.addWidget(label_text)
        layout.addWidget(self.input)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        cancel = QPushButton(_tr(parent, "cancel"))
        create = QPushButton(_tr(parent, "create"))
        create.setObjectName("PrimaryDialogButton")
        cancel.clicked.connect(self.reject)
        create.clicked.connect(self.accept)
        buttons.addWidget(cancel)
        buttons.addWidget(create)
        layout.addLayout(buttons)

    def value(self) -> str | None:
        text = self.input.text().strip()
        return text or None


class _HarnessDialog(QDialog):
    def __init__(
        self,
        parent: QWidget,
        harnesses: list["Harness"],
        title: str | None = None,
        message: str | None = None,
        confirm_text: str | None = None,
    ) -> None:
        super().__init__(parent)
        title = title or _tr(parent, "choose_harness")
        message = message or _tr(parent, "choose_harness_message")
        confirm_text = confirm_text or _tr(parent, "join")
        self.harnesses = harnesses
        self.setObjectName("HarnessPickerDialog")
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumSize(560, 460)
        self.setStyleSheet(_dialog_stylesheet(parent))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 20)
        layout.setSpacing(16)

        title_label = QLabel(title)
        title_label.setObjectName("DialogTitle")
        message_label = QLabel(message)
        message_label.setObjectName("DialogMessage")
        layout.addWidget(title_label)
        layout.addWidget(message_label)

        self.list_widget = QListWidget()
        self.list_widget.setObjectName("HarnessPickerList")
        for harness in harnesses:
            description = harness.description or _tr(parent, "no_description")
            self.list_widget.addItem(f"{harness.name}\n{description}")
        if harnesses:
            self.list_widget.setCurrentRow(0)
        layout.addWidget(self.list_widget)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        cancel = QPushButton(_tr(parent, "cancel"))
        cancel.setObjectName("GhostDialogButton")
        confirm = QPushButton(confirm_text)
        confirm.setObjectName("PrimaryDialogButton")
        cancel.clicked.connect(self.reject)
        confirm.clicked.connect(self.accept)
        buttons.addWidget(cancel)
        buttons.addWidget(confirm)
        layout.addLayout(buttons)

    def selected_harness(self) -> "Harness | None":
        row = self.list_widget.currentRow()
        if row < 0 or row >= len(self.harnesses):
            return None
        return self.harnesses[row]


class _AssetDialog(QDialog):
    def __init__(self, parent: QWidget, assets: list["Asset"]) -> None:
        super().__init__(parent)
        self.assets = assets
        self.setWindowTitle(_tr(parent, "choose_asset"))
        self.setModal(True)
        self.setMinimumWidth(520)
        self.setStyleSheet(_dialog_stylesheet(parent))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 18)
        layout.setSpacing(14)

        title_label = QLabel(_tr(parent, "choose_asset"))
        title_label.setObjectName("DialogTitle")
        message = QLabel(_tr(parent, "choose_asset_message"))
        message.setObjectName("DialogMessage")
        layout.addWidget(title_label)
        layout.addWidget(message)

        self.list_widget = QListWidget()
        for asset in assets:
            self.list_widget.addItem(f"{asset.name}\n{asset.type} - {asset.id}")
        if assets:
            self.list_widget.setCurrentRow(0)
        layout.addWidget(self.list_widget)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        cancel = QPushButton(_tr(parent, "cancel"))
        confirm = QPushButton(_tr(parent, "continue"))
        confirm.setObjectName("PrimaryDialogButton")
        cancel.clicked.connect(self.reject)
        confirm.clicked.connect(self.accept)
        buttons.addWidget(cancel)
        buttons.addWidget(confirm)
        layout.addLayout(buttons)

    def selected_asset(self) -> "Asset | None":
        row = self.list_widget.currentRow()
        if row < 0 or row >= len(self.assets):
            return None
        return self.assets[row]


class _HarnessDetailsDialog(QDialog):
    def __init__(
        self,
        parent: QWidget,
        title: str,
        name: str = "",
        description: str = "",
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(520)
        self.setStyleSheet(_dialog_stylesheet(parent))

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(_tr(parent, "harness_name"))
        self.name_input.setText(name)
        self.description_input = QPlainTextEdit()
        self.description_input.setPlaceholderText(_tr(parent, "harness_description"))
        self.description_input.setPlainText(description)
        self.description_input.setMinimumHeight(92)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 18)
        layout.setSpacing(14)
        title_label = QLabel(title)
        title_label.setObjectName("DialogTitle")
        layout.addWidget(title_label)
        layout.addWidget(QLabel(_tr(parent, "harness_name")))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel(_tr(parent, "harness_description")))
        layout.addWidget(self.description_input)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        cancel = QPushButton(_tr(parent, "cancel"))
        confirm = QPushButton(_tr(parent, "save"))
        confirm.setObjectName("PrimaryDialogButton")
        cancel.clicked.connect(self.reject)
        confirm.clicked.connect(self.accept)
        buttons.addWidget(cancel)
        buttons.addWidget(confirm)
        layout.addLayout(buttons)

    def value(self) -> tuple[str, str] | None:
        name = self.name_input.text().strip()
        if not name:
            return None
        return name, self.description_input.toPlainText().strip()


class AgentsMdDialog(QDialog):
    def __init__(
        self,
        parent: QWidget,
        title: str | None = None,
        name: str = "",
        description: str = "",
        content: str | None = None,
    ) -> None:
        title = title or _tr(parent, "add_agents")
        content = content or _tr(parent, "agents_content")
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowCloseButtonHint
        )
        self.setModal(True)
        self.setMinimumSize(760, 640)
        self.setStyleSheet(_dialog_stylesheet(parent))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 20)
        layout.setSpacing(14)

        title_row = QHBoxLayout()
        title_label = QLabel(title)
        title_label.setObjectName("DialogTitle")
        close = QPushButton("×")
        close.setObjectName("DialogCloseButton")
        close.clicked.connect(self.reject)
        title_row.addWidget(title_label, 1)
        title_row.addWidget(close)
        layout.addLayout(title_row)

        layout.addWidget(QLabel(_tr(parent, "name")))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(_tr(parent, "agents_name_placeholder"))
        self.name_input.setText(name)
        layout.addWidget(self.name_input)

        layout.addWidget(QLabel(_tr(parent, "description")))
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText(_tr(parent, "description_placeholder"))
        self.description_input.setText(description)
        layout.addWidget(self.description_input)

        content_header = QHBoxLayout()
        content_header.addWidget(QLabel(_tr(parent, "content")))
        content_header.addStretch(1)
        import_button = QPushButton(_tr(parent, "import_file"))
        import_button.setObjectName("GhostDialogButton")
        import_button.clicked.connect(self._import_file)
        content_header.addWidget(import_button)
        layout.addLayout(content_header)

        self.content_input = QPlainTextEdit()
        self.content_input.setPlainText(content)
        self.content_input.setMinimumHeight(280)
        layout.addWidget(self.content_input, 1)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        cancel = QPushButton(_tr(parent, "cancel"))
        save = QPushButton(_tr(parent, "save"))
        save.setObjectName("PrimaryDialogButton")
        cancel.clicked.connect(self.reject)
        save.clicked.connect(self.accept)
        buttons.addWidget(cancel)
        buttons.addWidget(save)
        layout.addLayout(buttons)

    def _import_file(self) -> None:
        value, _ = QFileDialog.getOpenFileName(
            self,
            _tr(self.parentWidget(), "choose_agents_file"),
            "",
            f"AGENTS.md (AGENTS.md);;Markdown (*.md);;{_tr(self.parentWidget(), 'all_files')}",
        )
        if not value:
            return
        path = Path(value)
        self.content_input.setPlainText(path.read_text(encoding="utf-8", errors="replace"))
        if not self.name_input.text().strip():
            self.name_input.setText(path.stem)

    def value(self) -> tuple[str, str, str] | None:
        name = self.name_input.text().strip()
        content = self.content_input.toPlainText().strip()
        if not name or not content:
            return None
        return name, self.description_input.text().strip(), content


class McpConfigDialog(QDialog):
    def __init__(
        self,
        parent: QWidget,
        title: str | None = None,
        mcp_title: str = "",
        display_name: str = "",
        description: str = "",
        config_json: str = '{\n  "type": "stdio",\n  "command": "uvx"\n}',
    ) -> None:
        title = title or _tr(parent, "new_mcp")
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowCloseButtonHint
        )
        self.setModal(True)
        self.setMinimumSize(720, 620)
        self.setStyleSheet(_dialog_stylesheet(parent))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 20)
        layout.setSpacing(14)
        title_row = QHBoxLayout()
        title_row.setSpacing(10)
        title_label = QLabel(title)
        title_label.setObjectName("DialogTitle")
        close = QPushButton("×")
        close.setObjectName("DialogCloseButton")
        close.clicked.connect(self.reject)
        title_row.addWidget(title_label, 1)
        title_row.addWidget(close)
        layout.addLayout(title_row)

        layout.addWidget(QLabel(_tr(parent, "mcp_title")))
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("my-mcp-server")
        self.title_input.setText(mcp_title)
        layout.addWidget(self.title_input)

        layout.addWidget(QLabel(_tr(parent, "display_name")))
        self.display_name_input = QLineEdit()
        self.display_name_input.setPlaceholderText(_tr(parent, "mcp_display_placeholder"))
        self.display_name_input.setText(display_name)
        layout.addWidget(self.display_name_input)

        layout.addWidget(QLabel(_tr(parent, "description")))
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText(_tr(parent, "mcp_desc_placeholder"))
        self.description_input.setText(description)
        layout.addWidget(self.description_input)

        header = QHBoxLayout()
        header.addWidget(QLabel(_tr(parent, "full_json")))
        header.addStretch(1)
        format_button = QPushButton(_tr(parent, "format"))
        format_button.clicked.connect(self._format_json)
        header.addWidget(format_button)
        layout.addLayout(header)

        self.config_input = QPlainTextEdit()
        self.config_input.setPlainText(config_json)
        self.config_input.setMinimumHeight(260)
        layout.addWidget(self.config_input)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        cancel = QPushButton(_tr(parent, "cancel"))
        save = QPushButton(_tr(parent, "save"))
        save.setObjectName("PrimaryDialogButton")
        cancel.clicked.connect(self.reject)
        save.clicked.connect(self.accept)
        buttons.addWidget(cancel)
        buttons.addWidget(save)
        layout.addLayout(buttons)

    def _format_json(self) -> None:
        parsed = json.loads(self.config_input.toPlainText())
        self.config_input.setPlainText(json.dumps(parsed, ensure_ascii=False, indent=2))

    def value(self) -> tuple[str, str, str, str] | None:
        title = self.title_input.text().strip()
        if not title:
            return None
        return (
            title,
            self.display_name_input.text().strip(),
            self.description_input.text().strip(),
            self.config_input.toPlainText(),
        )


class ProjectEditorDialog(QDialog):
    def __init__(
        self,
        parent: QWidget,
        title: str | None = None,
        name: str = "",
        path: Path | str | None = None,
        description: str = "",
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title or _tr(parent, "add_project"))
        self.setModal(True)
        self.setMinimumWidth(620)
        self.setStyleSheet(_dialog_stylesheet(parent))

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(_tr(parent, "project_name_placeholder"))
        self.name_input.setText(name)
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText(_tr(parent, "project_path_placeholder"))
        self.path_input.setText(str(path) if path else "")
        self.description_input = QPlainTextEdit()
        self.description_input.setPlaceholderText(_tr(parent, "description_placeholder"))
        self.description_input.setPlainText(description)
        self.description_input.setMinimumHeight(88)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 20)
        layout.setSpacing(14)
        title_label = QLabel(self.windowTitle())
        title_label.setObjectName("DialogTitle")
        layout.addWidget(title_label)
        layout.addWidget(QLabel(_tr(parent, "project_name")))
        layout.addWidget(self.name_input)

        path_row = QHBoxLayout()
        path_row.setSpacing(10)
        path_row.addWidget(self.path_input, 1)
        browse = QPushButton(_tr(parent, "browse"))
        browse.setObjectName("GhostDialogButton")
        browse.clicked.connect(self._choose_path)
        path_row.addWidget(browse)
        layout.addWidget(QLabel(_tr(parent, "project_path")))
        layout.addLayout(path_row)

        layout.addWidget(QLabel(_tr(parent, "project_description")))
        layout.addWidget(self.description_input)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        cancel = QPushButton(_tr(parent, "cancel"))
        save = QPushButton(_tr(parent, "save"))
        save.setObjectName("PrimaryDialogButton")
        cancel.clicked.connect(self.reject)
        save.clicked.connect(self.accept)
        buttons.addWidget(cancel)
        buttons.addWidget(save)
        layout.addLayout(buttons)

    def _choose_path(self) -> None:
        path = choose_project_directory(self)
        if path is None:
            return
        self.path_input.setText(str(path))
        if not self.name_input.text().strip():
            self.name_input.setText(path.name)

    def value(self) -> tuple[str, Path, str] | None:
        path_text = self.path_input.text().strip()
        if not path_text:
            return None
        path = Path(path_text)
        name = self.name_input.text().strip() or path.name
        if not name:
            return None
        return name, path, self.description_input.toPlainText().strip()


class ProjectManagerDialog(QDialog):
    def __init__(self, parent: QWidget, projects: list["Project"]) -> None:
        super().__init__(parent)
        self.projects = projects
        self.setWindowTitle(_tr(parent, "manage_projects"))
        self.setModal(True)
        self.setMinimumSize(620, 460)
        self.setStyleSheet(_dialog_stylesheet(parent))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 20)
        layout.setSpacing(14)
        title = QLabel(_tr(parent, "manage_projects"))
        title.setObjectName("DialogTitle")
        layout.addWidget(title)

        self.list_widget = QListWidget()
        self.list_widget.setObjectName("ProjectManagerDialogList")
        for project in projects:
            self.list_widget.addItem(f"{project.name}\n{project.path}")
        if projects:
            self.list_widget.setCurrentRow(0)
        layout.addWidget(self.list_widget, 1)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        cancel = QPushButton(_tr(parent, "cancel"))
        cancel.clicked.connect(self.reject)
        buttons.addWidget(cancel)
        layout.addLayout(buttons)

    def selected_project(self) -> "Project | None":
        row = self.list_widget.currentRow()
        if row < 0 or row >= len(self.projects):
            return None
        return self.projects[row]


def choose_directory(parent: QWidget, title: str) -> Path | None:
    value = QFileDialog.getExistingDirectory(parent, title)
    return Path(value) if value else None


def choose_archive(parent: QWidget) -> Path | None:
    value, _ = QFileDialog.getOpenFileName(
        parent,
        _tr(parent, "import_offline"),
        "",
        _tr(parent, "harness_zip_filter"),
    )
    return Path(value) if value else None


def choose_export_zip(parent: QWidget, title: str | None = None) -> Path | None:
    value, _ = QFileDialog.getSaveFileName(
        parent,
        title or _tr(parent, "export_config"),
        "harness-manager-config.zip",
        _tr(parent, "zip_filter"),
    )
    return Path(value) if value else None


def choose_harness_export_directory(parent: QWidget) -> Path | None:
    value = QFileDialog.getExistingDirectory(parent, _tr(parent, "choose_harness_export"))
    return Path(value) if value else None


def choose_project_directory(parent: QWidget) -> Path | None:
    value = QFileDialog.getExistingDirectory(parent, _tr(parent, "choose_project_directory"))
    return Path(value) if value else None


def choose_config_archive(parent: QWidget) -> Path | None:
    value, _ = QFileDialog.getOpenFileName(
        parent,
        _tr(parent, "import_config"),
        "",
        _tr(parent, "zip_filter"),
    )
    return Path(value) if value else None


def choose_asset_file(parent: QWidget, title: str, filter_text: str) -> Path | None:
    value, _ = QFileDialog.getOpenFileName(parent, title, "", filter_text)
    return Path(value) if value else None


def ask_text(parent: QWidget, title: str, label: str) -> str | None:
    dialog = _TextDialog(parent, title, label)
    if dialog.exec() != QDialog.DialogCode.Accepted:
        return None
    return dialog.value()


def choose_harness(
    parent: QWidget,
    harnesses: list["Harness"],
    title: str | None = None,
    message: str | None = None,
    confirm_text: str | None = None,
) -> "Harness | None":
    dialog = _HarnessDialog(parent, harnesses, title, message, confirm_text)
    if dialog.exec() != QDialog.DialogCode.Accepted:
        return None
    return dialog.selected_harness()


def choose_asset(parent: QWidget, assets: list["Asset"]) -> "Asset | None":
    dialog = _AssetDialog(parent, assets)
    if dialog.exec() != QDialog.DialogCode.Accepted:
        return None
    return dialog.selected_asset()


def ask_harness_details(
    parent: QWidget,
    title: str,
    name: str = "",
    description: str = "",
) -> tuple[str, str] | None:
    dialog = _HarnessDetailsDialog(parent, title, name, description)
    if dialog.exec() != QDialog.DialogCode.Accepted:
        return None
    return dialog.value()


def ask_agents_md(
    parent: QWidget,
    title: str | None = None,
    name: str = "",
    description: str = "",
    content: str | None = None,
) -> tuple[str, str, str] | None:
    dialog = AgentsMdDialog(parent, title, name, description, content)
    if dialog.exec() != QDialog.DialogCode.Accepted:
        return None
    return dialog.value()


def ask_mcp_config(
    parent: QWidget,
    title: str | None = None,
    mcp_title: str = "",
    display_name: str = "",
    description: str = "",
    config_json: str = '{\n  "type": "stdio",\n  "command": "uvx"\n}',
) -> tuple[str, str, str, str] | None:
    dialog = McpConfigDialog(parent, title, mcp_title, display_name, description, config_json)
    if dialog.exec() != QDialog.DialogCode.Accepted:
        return None
    return dialog.value()


def ask_project_details(
    parent: QWidget,
    title: str | None = None,
    name: str = "",
    path: Path | str | None = None,
    description: str = "",
) -> tuple[str, Path, str] | None:
    dialog = ProjectEditorDialog(parent, title, name, path, description)
    if dialog.exec() != QDialog.DialogCode.Accepted:
        return None
    return dialog.value()


def manage_projects_dialog(parent: QWidget, projects: list["Project"]) -> "Project | None":
    dialog = ProjectManagerDialog(parent, projects)
    if dialog.exec() != QDialog.DialogCode.Accepted:
        return None
    return dialog.selected_project()


def show_error(parent: QWidget, title: str, message: str) -> None:
    _MessageDialog(parent, title, message, "error").exec()


def show_info(parent: QWidget, title: str, message: str) -> None:
    _MessageDialog(parent, title, message, "info").exec()


def ask_confirm(parent: QWidget, title: str, message: str) -> bool:
    return _ConfirmDialog(parent, title, message).exec() == QDialog.DialogCode.Accepted
