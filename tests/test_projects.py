from __future__ import annotations

import pytest

from harness_manager.app_paths import AppPaths
from harness_manager.db import connect, initialize_database
from harness_manager.repositories import ProjectRepository


def test_project_repository_creates_lists_and_updates_projects(app_root, tmp_path):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    initialize_database(conn)
    repo = ProjectRepository(conn)
    project_path = tmp_path / "demo"
    project_path.mkdir()

    project = repo.create("Demo", project_path, "说明")
    updated = repo.update(project.id, "Demo 2", project_path, "新说明")

    assert updated.name == "Demo 2"
    assert updated.path == project_path.resolve()
    assert updated.description == "新说明"
    assert repo.list_all()[0].id == project.id


def test_project_repository_rejects_duplicate_paths(app_root, tmp_path):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    initialize_database(conn)
    repo = ProjectRepository(conn)
    project_path = tmp_path / "demo"
    project_path.mkdir()

    repo.create("Demo", project_path, "")

    with pytest.raises(ValueError, match="项目路径已存在"):
        repo.create("Other", project_path, "")
