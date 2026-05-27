from __future__ import annotations

from skillpkg.app_paths import AppPaths
from skillpkg.db import connect
from skillpkg.gui.controllers import MainController


def test_controller_creates_empty_harness(app_root):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    controller = MainController(app_root, conn)

    harness = controller.create_harness("代码审查", "审查任务工具包")

    assert harness.name == "代码审查"
    assert controller.list_harnesses()[0].id == harness.id
