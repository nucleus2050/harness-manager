from __future__ import annotations

from pathlib import Path


def test_main_window_user_facing_text_is_chinese():
    source = Path("src/skillpkg/gui/main_window.py").read_text(encoding="utf-8")

    for text in [
        "技能包管理器",
        "软件包",
        "新建包",
        "导入包",
        "导出包",
        "部署包",
        "选择一个软件包",
        "暂无软件包",
        "导入技能",
        "安装",
        "卸载",
    ]:
        assert text in source

    for text in [
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

    for text in ["取消", "创建", "导入离线包", "技能包", "所有文件"]:
        assert text in source

    for text in ["Cancel", "Create", "Import Offline Package", "All Files"]:
        assert text not in source
