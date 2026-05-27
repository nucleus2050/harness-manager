from __future__ import annotations

from skillpkg.app_paths import AppPaths
from skillpkg.db import connect
from skillpkg.gui.controllers import MainController


def test_controller_can_create_empty_package(app_root):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    controller = MainController(app_root, conn)

    package = controller.create_package("Work A", "Empty starter package")

    assert package.name == "Work A"
    assert controller.list_skills(0) == []
