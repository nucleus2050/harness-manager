from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import json

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from skillpkg.models import Asset, Harness


def _dialog_stylesheet() -> str:
    return """
    QDialog {
        background: #f8fafc;
        border-radius: 18px;
    }
    QLabel {
        background: transparent;
        color: #0f172a;
        font-family: "Segoe UI", "Microsoft YaHei UI", sans-serif;
    }
    QLabel#DialogTitle {
        font-size: 18px;
        font-weight: 800;
    }
    QLabel#DialogMessage {
        color: #475569;
        font-size: 13px;
    }
    QLabel#DialogIcon {
        min-width: 36px;
        min-height: 36px;
        max-width: 36px;
        max-height: 36px;
        border-radius: 18px;
        color: white;
        font-weight: 900;
        font-size: 18px;
    }
    QLineEdit {
        background: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 12px;
        padding: 9px 11px;
        color: #0f172a;
        font-size: 13px;
    }
    QPlainTextEdit {
        background: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 12px;
        padding: 9px 11px;
        color: #0f172a;
        font-size: 13px;
    }
    QPushButton {
        min-width: 82px;
        min-height: 34px;
        border-radius: 12px;
        border: 1px solid #cbd5e1;
        background: #ffffff;
        color: #334155;
        font-weight: 700;
        padding: 6px 14px;
    }
    QPushButton#PrimaryDialogButton {
        background: #2563eb;
        border-color: #2563eb;
        color: #ffffff;
    }
    QPushButton#DangerDialogButton {
        background: #ef4444;
        border-color: #ef4444;
        color: #ffffff;
    }
    QPushButton#GhostDialogButton {
        background: #ffffff;
        border-color: #d8e1ee;
        color: #172033;
    }
    QListWidget#HarnessPickerList {
        background: #f8fafc;
        border: 1px solid #dbe4f0;
        border-radius: 16px;
        padding: 8px;
    }
    QListWidget#HarnessPickerList::item {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        margin: 6px 0;
        padding: 14px;
        min-height: 54px;
        color: #172033;
    }
    QListWidget#HarnessPickerList::item:selected {
        background: #dbeafe;
        border: 1px solid #2563eb;
    }
    """


class _MessageDialog(QDialog):
    def __init__(self, parent: QWidget, title: str, message: str, kind: str) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(420)
        self.setStyleSheet(_dialog_stylesheet())

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 18)
        layout.setSpacing(18)

        body = QHBoxLayout()
        body.setSpacing(14)
        icon = QLabel("!" if kind == "error" else "i")
        icon.setObjectName("DialogIcon")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet(
            "background: #ef4444;" if kind == "error" else "background: #2563eb;"
        )
        text = QVBoxLayout()
        title_label = QLabel(title)
        title_label.setObjectName("DialogTitle")
        message_label = QLabel(message)
        message_label.setObjectName("DialogMessage")
        message_label.setWordWrap(True)
        text.addWidget(title_label)
        text.addWidget(message_label)
        body.addWidget(icon)
        body.addLayout(text, 1)
        layout.addLayout(body)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        ok = QPushButton("确定")
        ok.setObjectName("DangerDialogButton" if kind == "error" else "PrimaryDialogButton")
        ok.clicked.connect(self.accept)
        buttons.addWidget(ok)
        layout.addLayout(buttons)


class _TextDialog(QDialog):
    def __init__(self, parent: QWidget, title: str, label: str) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(460)
        self.setStyleSheet(_dialog_stylesheet())
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
        cancel = QPushButton("取消")
        create = QPushButton("创建")
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
        title: str = "选择任务套件",
        message: str = "请选择要加入的任务套件",
        confirm_text: str = "加入",
    ) -> None:
        super().__init__(parent)
        self.harnesses = harnesses
        self.setObjectName("HarnessPickerDialog")
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumSize(560, 460)
        self.setStyleSheet(_dialog_stylesheet())

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
            description = harness.description or "暂无描述"
            self.list_widget.addItem(f"{harness.name}\n{description}")
        if harnesses:
            self.list_widget.setCurrentRow(0)
        layout.addWidget(self.list_widget)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        cancel = QPushButton("取消")
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
        self.setWindowTitle("选择组件")
        self.setModal(True)
        self.setMinimumWidth(520)
        self.setStyleSheet(_dialog_stylesheet())

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 18)
        layout.setSpacing(14)

        title_label = QLabel("选择组件")
        title_label.setObjectName("DialogTitle")
        message = QLabel("请选择要加入任务套件的组件")
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
        cancel = QPushButton("取消")
        confirm = QPushButton("继续")
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
        self.setStyleSheet(_dialog_stylesheet())

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("套件名称")
        self.name_input.setText(name)
        self.description_input = QPlainTextEdit()
        self.description_input.setPlaceholderText("套件描述")
        self.description_input.setPlainText(description)
        self.description_input.setMinimumHeight(92)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 18)
        layout.setSpacing(14)
        title_label = QLabel(title)
        title_label.setObjectName("DialogTitle")
        layout.addWidget(title_label)
        layout.addWidget(QLabel("套件名称"))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("套件描述"))
        layout.addWidget(self.description_input)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        cancel = QPushButton("取消")
        confirm = QPushButton("保存")
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


class McpConfigDialog(QDialog):
    def __init__(
        self,
        parent: QWidget,
        title: str = "新建 MCP 配置",
        mcp_title: str = "",
        display_name: str = "",
        mcp_kind: str = "custom",
        config_json: str = '{\n  "type": "stdio",\n  "command": "uvx"\n}',
    ) -> None:
        super().__init__(parent)
        self.mcp_kind = mcp_kind
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumSize(720, 620)
        self.setStyleSheet(_dialog_stylesheet())

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 20)
        layout.setSpacing(14)
        title_label = QLabel(title)
        title_label.setObjectName("DialogTitle")
        layout.addWidget(title_label)

        kind_row = QHBoxLayout()
        for kind in ["custom", "fetch", "time", "memory", "sequential-thinking", "context7"]:
            button = QPushButton("自定义" if kind == "custom" else kind)
            button.setCheckable(True)
            button.setChecked(kind == self.mcp_kind)
            button.clicked.connect(lambda _checked=False, value=kind: self._select_kind(value))
            kind_row.addWidget(button)
        kind_row.addStretch(1)
        layout.addLayout(kind_row)

        layout.addWidget(QLabel("MCP 标题（唯一）"))
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("my-mcp-server")
        self.title_input.setText(mcp_title)
        layout.addWidget(self.title_input)

        layout.addWidget(QLabel("显示名称"))
        self.display_name_input = QLineEdit()
        self.display_name_input.setPlaceholderText("例如 @modelcontextprotocol/server-time")
        self.display_name_input.setText(display_name)
        layout.addWidget(self.display_name_input)

        header = QHBoxLayout()
        header.addWidget(QLabel("完整 JSON 配置"))
        header.addStretch(1)
        format_button = QPushButton("格式化")
        format_button.clicked.connect(self._format_json)
        header.addWidget(format_button)
        layout.addLayout(header)

        self.config_input = QPlainTextEdit()
        self.config_input.setPlainText(config_json)
        self.config_input.setMinimumHeight(260)
        layout.addWidget(self.config_input)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        cancel = QPushButton("取消")
        save = QPushButton("保存")
        save.setObjectName("PrimaryDialogButton")
        cancel.clicked.connect(self.reject)
        save.clicked.connect(self.accept)
        buttons.addWidget(cancel)
        buttons.addWidget(save)
        layout.addLayout(buttons)

    def _select_kind(self, value: str) -> None:
        self.mcp_kind = value

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
            self.mcp_kind,
            self.config_input.toPlainText(),
        )


def choose_directory(parent: QWidget, title: str) -> Path | None:
    value = QFileDialog.getExistingDirectory(parent, title)
    return Path(value) if value else None


def choose_archive(parent: QWidget) -> Path | None:
    value, _ = QFileDialog.getOpenFileName(
        parent,
        "导入离线包",
        "",
        "任务套件 (*.harness.zip);;兼容技能包 (*.skillpkg.zip);;Zip 压缩包 (*.zip);;所有文件 (*)",
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
    title: str = "选择任务套件",
    message: str = "请选择要加入的任务套件",
    confirm_text: str = "加入",
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


def ask_mcp_config(
    parent: QWidget,
    title: str = "新建 MCP 配置",
    mcp_title: str = "",
    display_name: str = "",
    mcp_kind: str = "custom",
    config_json: str = '{\n  "type": "stdio",\n  "command": "uvx"\n}',
) -> tuple[str, str, str, str] | None:
    dialog = McpConfigDialog(parent, title, mcp_title, display_name, mcp_kind, config_json)
    if dialog.exec() != QDialog.DialogCode.Accepted:
        return None
    return dialog.value()


def show_error(parent: QWidget, title: str, message: str) -> None:
    _MessageDialog(parent, title, message, "error").exec()


def show_info(parent: QWidget, title: str, message: str) -> None:
    _MessageDialog(parent, title, message, "info").exec()
