from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

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
    from skillpkg.models import Harness


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
    def __init__(self, parent: QWidget, harnesses: list["Harness"]) -> None:
        super().__init__(parent)
        self.harnesses = harnesses
        self.setWindowTitle("选择任务套件")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setStyleSheet(_dialog_stylesheet())

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 18)
        layout.setSpacing(14)

        title_label = QLabel("选择任务套件")
        title_label.setObjectName("DialogTitle")
        message = QLabel("请选择要加入的任务套件")
        message.setObjectName("DialogMessage")
        layout.addWidget(title_label)
        layout.addWidget(message)

        self.list_widget = QListWidget()
        for harness in harnesses:
            description = harness.description or "暂无描述"
            self.list_widget.addItem(f"{harness.name}\n{description}")
        if harnesses:
            self.list_widget.setCurrentRow(0)
        layout.addWidget(self.list_widget)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        cancel = QPushButton("取消")
        confirm = QPushButton("加入")
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


def choose_harness(parent: QWidget, harnesses: list["Harness"]) -> "Harness | None":
    dialog = _HarnessDialog(parent, harnesses)
    if dialog.exec() != QDialog.DialogCode.Accepted:
        return None
    return dialog.selected_harness()


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


def show_error(parent: QWidget, title: str, message: str) -> None:
    _MessageDialog(parent, title, message, "error").exec()


def show_info(parent: QWidget, title: str, message: str) -> None:
    _MessageDialog(parent, title, message, "info").exec()
