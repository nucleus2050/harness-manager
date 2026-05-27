from __future__ import annotations

from pathlib import Path


def test_main_window_has_custom_source_text_and_direct_import_flow():
    source = Path("src/skillpkg/gui/main_window.py").read_text(encoding="utf-8")

    for text in ["导入来源", "添加自定义目录", "配置目录", "从自定义目录导入"]:
        assert text in source

    assert "selected_custom_source_id" in source
    assert "_add_custom_source" in source
    assert "import_from_client_source" in source
    assert "import_from_custom_source" in source
