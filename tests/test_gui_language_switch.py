from __future__ import annotations

import os
from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QApplication, QLabel, QListWidget, QPushButton, QWidget

from harness_manager.db import connect
from harness_manager.gui.dialogs import AgentsMdDialog, McpConfigDialog
from harness_manager.gui.controllers import MainController
from harness_manager.gui.main_window import MainWindow


def _app() -> QApplication:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    return QApplication.instance() or QApplication([])


def test_language_switch_retranslates_visible_chrome(app_root):
    _app()
    controller = MainController(app_root, connect(":memory:"))
    window = MainWindow(controller)

    window._save_language("en-US")

    assert window.windowTitle() == "Harness Manager"
    assert window.settings_button.toolTip() == "Settings"
    assert window.harnesses_view_button.text() == "Harnesses"
    assert window.new_package_button.text() == "New"

    window._save_language("zh-CN")

    assert window.windowTitle() == "Harness Manager（任务套件管理器）"
    assert window.settings_button.toolTip() == "设置"
    assert window.harnesses_view_button.text() == "任务套件"
    assert window.new_package_button.text() == "新建"


def test_english_mode_has_no_chinese_in_core_views(app_root):
    _app()
    controller = MainController(app_root, connect(":memory:"))
    controller.create_harness("Demo", "sample")
    window = MainWindow(controller)
    window.show()
    window._save_language("en-US")

    for show_view in [
        window._show_harnesses_view,
        window._show_skills_view,
        lambda: window._show_asset_view("mcp"),
        lambda: window._show_asset_view("agents_md"),
        window._show_settings_view,
    ]:
        show_view()
        window.refresh()
        QApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        QApplication.processEvents()
        assert not _visible_chinese_texts(window)


def test_english_dialogs_have_no_chinese_chrome():
    _app()
    parent = QWidget()
    parent.current_language = "en-US"
    parent.current_theme = "obsidian"

    for dialog in [AgentsMdDialog(parent), McpConfigDialog(parent)]:
        assert not _visible_chinese_texts(dialog)


def _visible_chinese_texts(window: MainWindow) -> list[str]:
    texts: list[str] = []
    for label in window.findChildren(QLabel):
        if label.isVisibleTo(window) and _has_chinese(label.text()):
            texts.append(label.text())
    for button in window.findChildren(QPushButton):
        if not button.isVisibleTo(window):
            continue
        for text in [button.text(), button.toolTip()]:
            if _has_chinese(text):
                texts.append(text)
    for list_widget in window.findChildren(QListWidget):
        if not list_widget.isVisibleTo(window):
            continue
        for index in range(list_widget.count()):
            item_text = list_widget.item(index).text()
            if _has_chinese(item_text):
                texts.append(item_text)
    return texts


def _has_chinese(text: str) -> bool:
    if ":\\" in text or ":/" in text:
        return False
    return any("\u4e00" <= char <= "\u9fff" for char in text)
