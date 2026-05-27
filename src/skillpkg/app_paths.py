from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath, PureWindowsPath


@dataclass(frozen=True)
class AppPaths:
    root: Path

    @property
    def data_dir(self) -> Path:
        return self.root / "data"

    @property
    def skills_dir(self) -> Path:
        return self.root / "skills"

    @property
    def exports_dir(self) -> Path:
        return self.root / "exports"

    @property
    def config_dir(self) -> Path:
        return self.root / "config"

    @property
    def db_path(self) -> Path:
        return self.data_dir / "skillpkg.db"

    def skill_path(self, skill_id: str) -> Path:
        windows_path = PureWindowsPath(skill_id)
        posix_path = PurePosixPath(skill_id)
        if (
            not skill_id
            or skill_id in {".", ".."}
            or "/" in skill_id
            or "\\" in skill_id
            or windows_path.drive
            or windows_path.is_absolute()
            or posix_path.is_absolute()
        ):
            raise ValueError(f"Invalid skill ID: {skill_id!r}")
        return self.skills_dir / skill_id

    def ensure(self) -> None:
        for directory in (self.data_dir, self.skills_dir, self.exports_dir, self.config_dir):
            directory.mkdir(parents=True, exist_ok=True)
