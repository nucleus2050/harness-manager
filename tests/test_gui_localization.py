from __future__ import annotations

from pathlib import Path


def test_main_window_user_facing_text_is_chinese():
    source = Path("src/skillpkg/gui/main_window.py").read_text(encoding="utf-8")

    for text in [
        "任务套件管理器",
        "任务套件",
        "新建套件",
        "导入套件",
        "导出套件",
        "部署套件",
        "选择一个任务套件",
        "暂无任务套件",
        "导入技能",
        "安装",
        "卸载",
    ]:
        assert text in source

    for text in [
        "软件包",
        "技能包管理器",
        "New Package",
        "Import Package",
        "Export Package",
        "Deploy package",
        "Select a package",
        "No packages yet",
        "Install ",
        "Uninstall ",
    ]:
        assert text not in source


def test_dialog_user_facing_text_is_chinese():
    source = Path("src/skillpkg/gui/dialogs.py").read_text(encoding="utf-8")

    for text in ["取消", "创建", "导入离线包", "任务套件", "所有文件"]:
        assert text in source

    for text in ["Cancel", "Create", "Import Offline Package", "All Files"]:
        assert text not in source


def test_main_window_uses_harness_manager_terms():
    source = Path("src/skillpkg/gui/main_window.py").read_text(encoding="utf-8")

    for text in ["Harness Manager", "任务套件", "AGENTS.md", "MCP", "技能"]:
        assert text in source

    assert "Skill Package Manager" not in source
