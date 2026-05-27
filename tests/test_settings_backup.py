from __future__ import annotations

import json
import zipfile

from harness_manager.app_paths import AppPaths
from harness_manager.settings import SettingsService


def test_settings_default_and_save_language(app_root):
    paths = AppPaths(app_root)
    paths.ensure()
    service = SettingsService(paths)

    assert service.load().language == "zh-CN"

    saved = service.save_language("en-US")

    assert saved.language == "en-US"
    assert json.loads((paths.config_dir / "settings.json").read_text(encoding="utf-8")) == {
        "language": "en-US",
        "theme": "obsidian",
    }


def test_settings_default_and_save_theme(app_root):
    paths = AppPaths(app_root)
    paths.ensure()
    service = SettingsService(paths)

    assert service.load().theme == "obsidian"

    saved = service.save_theme("dark")

    assert saved.theme == "dark"
    assert saved.language == "zh-CN"
    assert json.loads((paths.config_dir / "settings.json").read_text(encoding="utf-8")) == {
        "language": "zh-CN",
        "theme": "dark",
    }


def test_settings_accepts_extra_visual_themes(app_root):
    paths = AppPaths(app_root)
    paths.ensure()
    service = SettingsService(paths)

    for theme in ["obsidian", "matrix", "neon", "sunset", "forest", "aurora", "ember", "porcelain"]:
        assert service.save_theme(theme).theme == theme


def test_settings_preserves_theme_and_language(app_root):
    paths = AppPaths(app_root)
    paths.ensure()
    service = SettingsService(paths)

    service.save_language("en-US")
    settings = service.save_theme("light")
    settings = service.save_language("zh-CN")

    assert settings.language == "zh-CN"
    assert settings.theme == "light"


def test_settings_invalid_theme_falls_back_to_obsidian(app_root):
    paths = AppPaths(app_root)
    paths.ensure()
    (paths.config_dir / "settings.json").write_text(
        json.dumps({"language": "en-US", "theme": "sepia"}),
        encoding="utf-8",
    )

    settings = SettingsService(paths).load()

    assert settings.language == "en-US"
    assert settings.theme == "obsidian"


def test_export_full_config_includes_runtime_directories(app_root):
    paths = AppPaths(app_root)
    paths.ensure()
    (paths.data_dir / "harness.db").write_text("db", encoding="utf-8")
    (paths.root / "assets" / "mcp" / "a").mkdir(parents=True)
    (paths.root / "assets" / "mcp" / "a" / "mcp.json").write_text("{}", encoding="utf-8")
    (paths.skills_dir / "skill-a").mkdir()
    (paths.skills_dir / "skill-a" / "SKILL.md").write_text("# Skill", encoding="utf-8")

    archive = SettingsService(paths).export_full_config()

    with zipfile.ZipFile(archive) as zf:
        names = set(zf.namelist())
    assert "data/harness.db" in names
    assert "assets/mcp/a/mcp.json" in names
    assert "skills/skill-a/SKILL.md" in names


def test_import_full_config_replaces_current_and_creates_backup(app_root, tmp_path):
    paths = AppPaths(app_root)
    paths.ensure()
    (paths.skills_dir / "old").mkdir()
    (paths.skills_dir / "old" / "SKILL.md").write_text("old", encoding="utf-8")
    source_root = tmp_path / "source"
    (source_root / "skills" / "new").mkdir(parents=True)
    (source_root / "skills" / "new" / "SKILL.md").write_text("new", encoding="utf-8")
    archive = tmp_path / "config.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.write(source_root / "skills" / "new" / "SKILL.md", "skills/new/SKILL.md")

    backup = SettingsService(paths).import_full_config(archive)

    assert backup.is_file()
    assert not (paths.skills_dir / "old").exists()
    assert (paths.skills_dir / "new" / "SKILL.md").read_text(encoding="utf-8") == "new"
