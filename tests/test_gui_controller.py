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


def test_controller_saves_language_setting(app_root):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    controller = MainController(app_root, conn)

    settings = controller.save_language("en-US")

    assert settings.language == "en-US"
    assert controller.get_settings().language == "en-US"


def test_controller_saves_theme_setting(app_root):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    controller = MainController(app_root, conn)

    settings = controller.save_theme("dark")

    assert settings.theme == "dark"
    assert controller.get_settings().theme == "dark"


def test_controller_exports_full_config(app_root):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    controller = MainController(app_root, conn)

    archive = controller.export_full_config()

    assert archive.is_file()
