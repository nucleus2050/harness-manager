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

from harness_manager.gui.controllers import MainController


def test_controller_tracks_harness_deployments_per_project(app_root, tmp_path, sample_skill):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    controller = MainController(app_root, conn)
    first_path = tmp_path / "first"
    second_path = tmp_path / "second"
    first_path.mkdir()
    second_path.mkdir()
    first = controller.create_project("First", first_path, "")
    second = controller.create_project("Second", second_path, "")
    harness = controller.create_harness("项目套件", "")
    skill = controller.import_skill_directory(sample_skill, "codex")
    controller.add_asset_to_harness(harness.id, skill.id, "skill")

    controller.toggle_harness_deploy(harness.id, "codex", first.path, scope="project")

    assert controller.harness_deploy_status(harness.id, "codex", first.path, scope="project")
    assert not controller.harness_deploy_status(harness.id, "codex", second.path, scope="project")


def test_controller_lists_harness_deployment_locations(app_root, tmp_path, sample_skill):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    controller = MainController(app_root, conn)
    project_path = tmp_path / "project"
    project_path.mkdir()
    project = controller.create_project("Project A", project_path, "")
    harness = controller.create_harness("部署摘要", "")
    skill = controller.import_skill_directory(sample_skill, "codex")
    controller.add_asset_to_harness(harness.id, skill.id, "skill")

    controller.toggle_harness_deploy(harness.id, "codex", project.path, scope="project")

    locations = controller.harness_deployment_locations(harness.id)

    assert locations == [
        {
            "scope": "project",
            "name": "Project A",
            "path": project.path,
            "clients": {"codex": True, "claude_code": False, "opencode": False},
        }
    ]
