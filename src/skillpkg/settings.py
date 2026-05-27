from __future__ import annotations

import json
import shutil
import tempfile
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from skillpkg.app_paths import AppPaths
from skillpkg.file_ops import extract_zip, make_zip, safe_remove_directory


@dataclass(frozen=True)
class AppSettings:
    language: str = "zh-CN"


class SettingsService:
    def __init__(self, paths: AppPaths) -> None:
        self.paths = paths
        self.paths.ensure()

    @property
    def settings_path(self) -> Path:
        return self.paths.config_dir / "settings.json"

    def load(self) -> AppSettings:
        if not self.settings_path.is_file():
            return AppSettings()
        data = json.loads(self.settings_path.read_text(encoding="utf-8"))
        language = data.get("language", "zh-CN")
        if language not in {"zh-CN", "en-US"}:
            language = "zh-CN"
        return AppSettings(language=language)

    def save_language(self, language: str) -> AppSettings:
        if language not in {"zh-CN", "en-US"}:
            raise ValueError(f"Unsupported language: {language}")
        self.settings_path.write_text(
            json.dumps({"language": language}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return AppSettings(language=language)

    def export_full_config(self, destination: Path | str | None = None) -> Path:
        staging = Path(tempfile.mkdtemp(prefix="harness-config-export-"))
        try:
            for name in ["data", "assets", "skills", "config"]:
                source = self.paths.root / name
                if source.exists():
                    shutil.copytree(source, staging / name)
            target = (
                Path(destination)
                if destination is not None
                else self.paths.exports_dir / f"harness-manager-config-{_timestamp()}.zip"
            )
            return make_zip(staging, target)
        finally:
            safe_remove_directory(staging)

    def import_full_config(self, archive_path: Path | str) -> Path:
        backup = self.paths.exports_dir / f"backup-before-import-{_timestamp()}.zip"
        self.export_full_config(backup)
        extracted = extract_zip(archive_path)
        try:
            for name in ["data", "assets", "skills", "config"]:
                destination = self.paths.root / name
                if destination.exists():
                    safe_remove_directory(destination)
                source = extracted / name
                if source.exists():
                    shutil.copytree(source, destination)
                else:
                    destination.mkdir(parents=True, exist_ok=True)
            return backup
        finally:
            safe_remove_directory(extracted)


def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")
