from __future__ import annotations

import os
from PySide6.QtWidgets import QApplication

from harness_manager.db import connect
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
