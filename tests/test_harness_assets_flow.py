from __future__ import annotations

import pytest

from harness_manager.app_paths import AppPaths
from harness_manager.db import connect
from harness_manager.fingerprint import fingerprint_directory
from harness_manager.gui.controllers import MainController


def test_controller_adds_asset_to_harness(app_root, tmp_path):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    controller = MainController(app_root, conn)
    harness = controller.create_harness("代码审查", "")
    source = tmp_path / "AGENTS.md"
    source.write_text("# Rules\n", encoding="utf-8")
    asset = controller.import_agents_md_asset(source, "规则")

    controller.add_asset_to_harness(harness.id, asset.id, asset.type)

    assets = controller.list_harness_assets(harness.id)
    assert [item.id for item in assets] == [asset.id]


def test_controller_lists_harness_assets_by_type(app_root, tmp_path, sample_skill):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    controller = MainController(app_root, conn)
    harness = controller.create_harness("前端任务", "")

    agents_file = tmp_path / "AGENTS.md"
    agents_file.write_text("# Frontend Rules\n", encoding="utf-8")
    agents_asset = controller.import_agents_md_asset(agents_file, "前端规则")
    skill_asset = controller.import_skill_directory(sample_skill, "codex")

    controller.add_asset_to_harness(harness.id, agents_asset.id, agents_asset.type)
    controller.add_asset_to_harness(harness.id, skill_asset.id, "skill")

    assert [asset.id for asset in controller.list_harness_assets_by_type(harness.id, "agents_md")] == [
        agents_asset.id
    ]
    assert [asset.id for asset in controller.list_harness_assets_by_type(harness.id, "skill")] == [
        skill_asset.id
    ]


def test_controller_lists_only_harnesses_without_asset(app_root, tmp_path):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    controller = MainController(app_root, conn)
    first = controller.create_harness("已有组件", "")
    second = controller.create_harness("可加入", "")
    source = tmp_path / "AGENTS.md"
    source.write_text("# Rules\n", encoding="utf-8")
    asset = controller.import_agents_md_asset(source, "规则")
    controller.add_asset_to_harness(first.id, asset.id, asset.type)

    available = controller.list_harnesses_without_asset(asset.id)

    assert [harness.id for harness in available] == [second.id]


def test_controller_allows_only_one_agents_md_per_harness(app_root, tmp_path):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    controller = MainController(app_root, conn)
    harness = controller.create_harness("单提示词套件", "")
    first = controller.create_agents_md_asset("规则一", "第一份", "# One")
    second = controller.create_agents_md_asset("规则二", "第二份", "# Two")

    controller.add_asset_to_harness(harness.id, first.id, first.type)

    with pytest.raises(ValueError, match="只能加入一个 AGENTS.md"):
        controller.add_asset_to_harness(harness.id, second.id, second.type)
    assert controller.list_harnesses_available_for_asset(second) == []


def test_controller_lists_harnesses_with_asset_and_removes_membership(app_root, tmp_path):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    controller = MainController(app_root, conn)
    first = controller.create_harness("已有组件", "")
    controller.create_harness("未加入", "")
    source = tmp_path / "AGENTS.md"
    source.write_text("# Rules\n", encoding="utf-8")
    asset = controller.import_agents_md_asset(source, "规则")
    controller.add_asset_to_harness(first.id, asset.id, asset.type)

    joined = controller.list_harnesses_with_asset(asset.id)
    controller.remove_asset_from_harness(first.id, asset.id)

    assert [harness.id for harness in joined] == [first.id]
    assert controller.list_harness_assets(first.id) == []


def test_controller_deploys_harness_by_id_without_package_row(app_root, tmp_path, sample_skill):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    controller = MainController(app_root, conn)
    harness = controller.create_harness("可部署套件", "")
    skill = controller.import_skill_directory(sample_skill, "codex")
    controller.add_asset_to_harness(harness.id, skill.id, "skill")
    target = tmp_path / "codex-skills"
    target.mkdir()

    installed = controller.deploy_harness_by_id(harness.id, "codex", target)

    assert installed == [target / skill.id]
    assert (target / skill.id / "SKILL.md").is_file()


def test_controller_deploys_harness_creates_missing_target_directory(
    app_root, tmp_path, sample_skill
):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    controller = MainController(app_root, conn)
    harness = controller.create_harness("默认目录部署", "")
    skill = controller.import_skill_directory(sample_skill, "claude_code")
    controller.add_asset_to_harness(harness.id, skill.id, "skill")
    target = tmp_path / ".claude" / "skills"

    installed = controller.deploy_harness_by_id(harness.id, "claude_code", target)

    assert target.is_dir()
    assert installed == [target / skill.id]
    assert (target / skill.id / "SKILL.md").is_file()


def test_controller_tracks_and_toggles_harness_deployment(app_root, tmp_path, sample_skill):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    controller = MainController(app_root, conn)
    harness = controller.create_harness("可撤销部署", "")
    skill = controller.import_skill_directory(sample_skill, "codex")
    controller.add_asset_to_harness(harness.id, skill.id, "skill")
    target = tmp_path / "codex-skills"

    assert not controller.harness_deploy_status(harness.id, "codex", target)

    action, result = controller.toggle_harness_deploy(harness.id, "codex", target)

    assert action == "deployed"
    assert result == [target / skill.id]
    assert controller.harness_deploy_status(harness.id, "codex", target)
    assert (target / skill.id / "SKILL.md").is_file()

    action, result = controller.toggle_harness_deploy(harness.id, "codex", target)

    assert action == "undeployed"
    assert result == {skill.id: "uninstalled"}
    assert not controller.harness_deploy_status(harness.id, "codex", target)
    assert not (target / skill.id).exists()


def test_controller_does_not_undeploy_modified_harness_skill(app_root, tmp_path, sample_skill):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    controller = MainController(app_root, conn)
    harness = controller.create_harness("保护本地修改", "")
    skill = controller.import_skill_directory(sample_skill, "codex")
    controller.add_asset_to_harness(harness.id, skill.id, "skill")
    target = tmp_path / "codex-skills"
    controller.toggle_harness_deploy(harness.id, "codex", target)
    (target / skill.id / "SKILL.md").write_text("# Local Edit\n", encoding="utf-8")

    action, result = controller.toggle_harness_deploy(harness.id, "codex", target)

    assert action == "undeployed"
    assert result == {skill.id: "modified"}
    assert (target / skill.id).exists()
    assert not controller.harness_deploy_status(harness.id, "codex", target)


def test_controller_adopts_existing_identical_skill_as_deployed(
    app_root, tmp_path, sample_skill
):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    controller = MainController(app_root, conn)
    harness = controller.create_harness("认领已有技能", "")
    skill = controller.import_skill_directory(sample_skill, "codex")
    controller.add_asset_to_harness(harness.id, skill.id, "skill")
    target = tmp_path / "codex-skills"
    target.mkdir()
    existing = target / skill.id
    existing.mkdir()
    (existing / "SKILL.md").write_text("# Sample Skill\n\nBody\n", encoding="utf-8")

    action, result = controller.toggle_harness_deploy(harness.id, "codex", target)

    assert action == "deployed"
    assert result == [existing]
    assert controller.harness_deploy_status(harness.id, "codex", target)


def test_controller_rejects_existing_different_skill_without_record(
    app_root, tmp_path, sample_skill
):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    controller = MainController(app_root, conn)
    harness = controller.create_harness("冲突技能", "")
    skill = controller.import_skill_directory(sample_skill, "codex")
    controller.add_asset_to_harness(harness.id, skill.id, "skill")
    target = tmp_path / "codex-skills"
    target.mkdir()
    existing = target / skill.id
    existing.mkdir()
    (existing / "SKILL.md").write_text("# Other Skill\n", encoding="utf-8")

    with pytest.raises(ValueError, match="目标已存在"):
        controller.toggle_harness_deploy(harness.id, "codex", target)

    assert not controller.harness_deploy_status(harness.id, "codex", target)
    assert (existing / "SKILL.md").read_text(encoding="utf-8") == "# Other Skill\n"


def test_harness_deploy_status_requires_all_assets_and_matching_fingerprint(
    app_root, tmp_path, sample_skill
):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    controller = MainController(app_root, conn)
    harness = controller.create_harness("完整状态", "")
    first = controller.import_skill_directory(sample_skill, "codex")
    second_source = tmp_path / "second-skill"
    second_source.mkdir()
    (second_source / "SKILL.md").write_text("# Second\n", encoding="utf-8")
    second = controller.import_skill_directory(second_source, "codex")
    controller.add_asset_to_harness(harness.id, first.id, "skill")
    controller.add_asset_to_harness(harness.id, second.id, "skill")
    target = tmp_path / "codex-skills"
    target.mkdir()
    first_target = target / first.id
    first_target.mkdir()
    (first_target / "SKILL.md").write_text("# Sample Skill\n\nBody\n", encoding="utf-8")
    controller.service.harness_deploys.add_deployed(
        harness.id,
        first.id,
        "codex",
        target,
        first_target,
        fingerprint_directory(first_target),
    )
    conn.commit()

    assert not controller.harness_deploy_status(harness.id, "codex", target)

    controller.toggle_harness_deploy(harness.id, "codex", target)

    assert controller.harness_deploy_status(harness.id, "codex", target)
    (target / first.id / "SKILL.md").write_text("# Changed\n", encoding="utf-8")
    assert not controller.harness_deploy_status(harness.id, "codex", target)
