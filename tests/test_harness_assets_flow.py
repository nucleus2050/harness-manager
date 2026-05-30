from __future__ import annotations

import json

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


def test_global_codex_deploy_installs_skill_agents_and_mcp_assets(
    app_root, tmp_path, sample_skill
):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    controller = MainController(app_root, conn)
    harness = controller.create_harness("完整套件", "")
    skill = controller.import_skill_directory(sample_skill, "codex")
    agents = controller.create_agents_md_asset("全局规则", "说明", "# Codex Rules")
    mcp = controller.create_mcp_config_asset(
        "fetch",
        "Fetch",
        '{"type":"stdio","command":"uvx","args":["mcp-server-fetch"]}',
    )
    controller.add_asset_to_harness(harness.id, skill.id, "skill")
    for asset in [agents, mcp]:
        controller.add_asset_to_harness(harness.id, asset.id, asset.type)
    target = tmp_path / ".codex" / "skills"

    installed = controller.deploy_harness_by_id(harness.id, "codex", target)

    codex_home = target.parent
    assert target / skill.id in installed
    assert codex_home / "AGENTS.md" in installed
    assert codex_home / "config.toml" in installed
    assert (target / skill.id / "SKILL.md").is_file()
    assert "<!-- harness-manager:start:" in (codex_home / "AGENTS.md").read_text(encoding="utf-8")
    config_text = (codex_home / "config.toml").read_text(encoding="utf-8")
    assert "[mcp_servers.fetch]" in config_text
    assert 'command = "uvx"' in config_text
    assert 'args = ["mcp-server-fetch"]' in config_text
    assert 'type = "stdio"' not in config_text
    assert controller.harness_deploy_status(harness.id, "codex", target)


def test_global_claude_deploy_writes_claude_md_and_user_mcp_json(
    app_root, tmp_path
):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    controller = MainController(app_root, conn)
    harness = controller.create_harness("Claude 套件", "")
    agents = controller.create_agents_md_asset("Claude 规则", "", "# Claude Rules")
    mcp = controller.create_mcp_config_asset(
        "fetch",
        "Fetch",
        '{"type":"stdio","command":"uvx","args":["mcp-server-fetch"]}',
    )
    controller.add_asset_to_harness(harness.id, agents.id, agents.type)
    controller.add_asset_to_harness(harness.id, mcp.id, mcp.type)
    target = tmp_path / ".claude" / "skills"

    installed = controller.deploy_harness_by_id(harness.id, "claude_code", target)

    claude_home = target.parent
    assert claude_home / "CLAUDE.md" in installed
    assert tmp_path / ".claude.json" in installed
    assert "# Claude Rules" in (claude_home / "CLAUDE.md").read_text(encoding="utf-8")
    user_config = json.loads((tmp_path / ".claude.json").read_text(encoding="utf-8"))
    assert user_config["mcpServers"]["fetch"]["command"] == "uvx"
    assert controller.harness_deploy_status(harness.id, "claude_code", target)


def test_global_opencode_deploy_writes_agents_and_mcp_config(app_root, tmp_path):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    controller = MainController(app_root, conn)
    harness = controller.create_harness("OpenCode 套件", "")
    agents = controller.create_agents_md_asset("OpenCode 规则", "", "# OpenCode Rules")
    mcp = controller.create_mcp_config_asset(
        "fetch",
        "Fetch",
        '{"type":"stdio","command":"uvx","args":["mcp-server-fetch"]}',
    )
    controller.add_asset_to_harness(harness.id, agents.id, agents.type)
    controller.add_asset_to_harness(harness.id, mcp.id, mcp.type)
    target = tmp_path / ".config" / "opencode" / "skills"

    installed = controller.deploy_harness_by_id(harness.id, "opencode", target)

    opencode_home = target.parent
    assert opencode_home / "AGENTS.md" in installed
    assert opencode_home / "opencode.json" in installed
    assert "# OpenCode Rules" in (opencode_home / "AGENTS.md").read_text(encoding="utf-8")
    config = json.loads((opencode_home / "opencode.json").read_text(encoding="utf-8"))
    assert config["mcp"]["fetch"] == {
        "type": "local",
        "command": ["uvx", "mcp-server-fetch"],
    }
    assert controller.harness_deploy_status(harness.id, "opencode", target)


def test_project_codex_deploy_writes_project_level_assets(
    app_root, tmp_path, sample_skill
):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    controller = MainController(app_root, conn)
    harness = controller.create_harness("Codex 项目", "")
    skill = controller.import_skill_directory(sample_skill, "codex")
    agents = controller.create_agents_md_asset("项目规则", "", "# Project Rules")
    mcp = controller.create_mcp_config_asset(
        "fetch",
        "Fetch",
        '{"type":"stdio","command":"uvx","args":["mcp-server-fetch"]}',
    )
    controller.add_asset_to_harness(harness.id, skill.id, "skill")
    for asset in [agents, mcp]:
        controller.add_asset_to_harness(harness.id, asset.id, asset.type)
    project_root = tmp_path / "project"

    installed = controller.deploy_harness_by_id(
        harness.id, "codex", project_root, scope="project"
    )

    skill_root = project_root / ".agents" / "skills"
    assert skill_root / skill.id in installed
    assert project_root / "AGENTS.md" in installed
    assert project_root / ".codex" / "config.toml" in installed
    assert (skill_root / skill.id / "SKILL.md").is_file()
    assert "# Project Rules" in (project_root / "AGENTS.md").read_text(encoding="utf-8")
    config_text = (project_root / ".codex" / "config.toml").read_text(encoding="utf-8")
    assert "[mcp_servers.fetch]" in config_text
    assert controller.harness_deploy_status(
        harness.id, "codex", project_root, scope="project"
    )


def test_project_claude_deploy_writes_project_level_assets(
    app_root, tmp_path, sample_skill
):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    controller = MainController(app_root, conn)
    harness = controller.create_harness("Claude 项目", "")
    skill = controller.import_skill_directory(sample_skill, "claude_code")
    agents = controller.create_agents_md_asset("项目规则", "", "# Claude Project Rules")
    mcp = controller.create_mcp_config_asset(
        "fetch",
        "Fetch",
        '{"type":"stdio","command":"uvx","args":["mcp-server-fetch"]}',
    )
    controller.add_asset_to_harness(harness.id, skill.id, "skill")
    for asset in [agents, mcp]:
        controller.add_asset_to_harness(harness.id, asset.id, asset.type)
    project_root = tmp_path / "project"

    installed = controller.deploy_harness_by_id(
        harness.id, "claude_code", project_root, scope="project"
    )

    skill_root = project_root / ".claude" / "skills"
    assert skill_root / skill.id in installed
    assert project_root / "CLAUDE.md" in installed
    assert project_root / ".mcp.json" in installed
    assert (skill_root / skill.id / "SKILL.md").is_file()
    assert "# Claude Project Rules" in (project_root / "CLAUDE.md").read_text(
        encoding="utf-8"
    )
    config = json.loads((project_root / ".mcp.json").read_text(encoding="utf-8"))
    assert config["mcpServers"]["fetch"]["command"] == "uvx"
    assert controller.harness_deploy_status(
        harness.id, "claude_code", project_root, scope="project"
    )


def test_project_opencode_deploy_writes_project_level_assets(
    app_root, tmp_path, sample_skill
):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    controller = MainController(app_root, conn)
    harness = controller.create_harness("OpenCode 项目", "")
    skill = controller.import_skill_directory(sample_skill, "opencode")
    agents = controller.create_agents_md_asset("项目规则", "", "# OpenCode Project Rules")
    mcp = controller.create_mcp_config_asset(
        "fetch",
        "Fetch",
        '{"type":"stdio","command":"uvx","args":["mcp-server-fetch"]}',
    )
    controller.add_asset_to_harness(harness.id, skill.id, "skill")
    for asset in [agents, mcp]:
        controller.add_asset_to_harness(harness.id, asset.id, asset.type)
    project_root = tmp_path / "project"

    installed = controller.deploy_harness_by_id(
        harness.id, "opencode", project_root, scope="project"
    )

    skill_root = project_root / ".opencode" / "skills"
    assert skill_root / skill.id in installed
    assert project_root / "AGENTS.md" in installed
    assert project_root / "opencode.json" in installed
    assert (skill_root / skill.id / "SKILL.md").is_file()
    config = json.loads((project_root / "opencode.json").read_text(encoding="utf-8"))
    assert config["mcp"]["fetch"] == {
        "type": "local",
        "command": ["uvx", "mcp-server-fetch"],
    }
    assert "AGENTS.md" in config["instructions"]
    assert controller.harness_deploy_status(
        harness.id, "opencode", project_root, scope="project"
    )


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


def test_toggle_harness_undeploy_removes_global_codex_file_assets(
    app_root, tmp_path, sample_skill
):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    controller = MainController(app_root, conn)
    harness = controller.create_harness("完整撤销", "")
    skill = controller.import_skill_directory(sample_skill, "codex")
    agents = controller.create_agents_md_asset("全局规则", "", "# Codex Rules")
    mcp = controller.create_mcp_config_asset(
        "fetch",
        "Fetch",
        '{"type":"stdio","command":"uvx","args":["mcp-server-fetch"]}',
    )
    controller.add_asset_to_harness(harness.id, skill.id, "skill")
    for asset in [agents, mcp]:
        controller.add_asset_to_harness(harness.id, asset.id, asset.type)
    target = tmp_path / ".codex" / "skills"

    controller.toggle_harness_deploy(harness.id, "codex", target)
    action, result = controller.toggle_harness_deploy(harness.id, "codex", target)

    assert action == "undeployed"
    assert result == {
        skill.id: "uninstalled",
        agents.id: "uninstalled",
        mcp.id: "uninstalled",
    }
    codex_home = target.parent
    assert not (target / skill.id).exists()
    assert not (codex_home / "AGENTS.md").exists()
    assert not (codex_home / "config.toml").exists()
    assert not controller.harness_deploy_status(harness.id, "codex", target)


def test_toggle_harness_undeploy_removes_global_json_mcp_assets(app_root, tmp_path):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    controller = MainController(app_root, conn)
    harness = controller.create_harness("MCP 撤销", "")
    claude_mcp = controller.create_mcp_config_asset(
        "fetch",
        "Fetch",
        '{"type":"stdio","command":"uvx","args":["mcp-server-fetch"]}',
    )
    controller.add_asset_to_harness(harness.id, claude_mcp.id, claude_mcp.type)
    claude_target = tmp_path / ".claude" / "skills"
    controller.toggle_harness_deploy(harness.id, "claude_code", claude_target)

    action, _ = controller.toggle_harness_deploy(
        harness.id, "claude_code", claude_target
    )

    assert action == "undeployed"
    assert not (tmp_path / ".claude.json").exists()

    opencode_target = tmp_path / ".config" / "opencode" / "skills"
    controller.toggle_harness_deploy(harness.id, "opencode", opencode_target)

    action, _ = controller.toggle_harness_deploy(
        harness.id, "opencode", opencode_target
    )

    assert action == "undeployed"
    assert not (opencode_target.parent / "opencode.json").exists()


def test_deploy_and_undeploy_global_agent_assets(app_root, tmp_path):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    controller = MainController(app_root, conn)
    harness = controller.create_harness("Agent 套件", "")
    agent = controller.service.create_agent_asset(
        name="Codex Reviewer",
        client_type="codex",
        agent_format="codex_toml",
        agent_name="reviewer",
        description="Review code",
        content='name = "reviewer"\ndescription = "Review code"\ndeveloper_instructions = "Be strict."',
    )
    controller.add_asset_to_harness(harness.id, agent.id, "agent")
    target = tmp_path / ".codex" / "skills"

    action, deployed = controller.toggle_harness_deploy(harness.id, "codex", target)

    deployed_agent = tmp_path / ".codex" / "agents" / "reviewer.toml"
    assert action == "deployed"
    assert deployed == [deployed_agent]
    assert deployed_agent.read_text(encoding="utf-8").startswith('name = "reviewer"')
    assert controller.harness_deploy_status(harness.id, "codex", target)

    action, result = controller.toggle_harness_deploy(harness.id, "codex", target)

    assert action == "undeployed"
    assert result == {agent.id: "uninstalled"}
    assert not deployed_agent.exists()
    assert not (tmp_path / ".codex" / "agents").exists()


def test_project_agent_assets_deploy_to_client_agent_directories(app_root, tmp_path):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    controller = MainController(app_root, conn)
    project_root = tmp_path / "project"

    cases = [
        ("codex", "codex_toml", ".toml", project_root / ".codex" / "agents" / "reviewer.toml"),
        ("claude_code", "claude_md", ".md", project_root / ".claude" / "agents" / "reviewer.md"),
        ("opencode", "opencode_md", ".md", project_root / ".opencode" / "agents" / "reviewer.md"),
    ]
    for client_type, agent_format, extension, expected_path in cases:
        harness = controller.create_harness(f"{client_type} Agent", "")
        content = (
            'name = "reviewer"\ndescription = "Review code"\ndeveloper_instructions = "Be strict."'
            if extension == ".toml"
            else "---\ndescription: Review code\n---\n\nReview code."
        )
        agent = controller.service.create_agent_asset(
            name=f"{client_type} Reviewer",
            client_type=client_type,
            agent_format=agent_format,
            agent_name="reviewer",
            description="Review code",
            content=content,
        )
        controller.add_asset_to_harness(harness.id, agent.id, "agent")

        action, deployed = controller.toggle_harness_deploy(
            harness.id, client_type, project_root, scope="project"
        )

        assert action == "deployed"
        assert deployed == [expected_path]
        assert expected_path.is_file()


def test_project_undeploy_removes_empty_generated_files_and_directories(
    app_root, tmp_path, sample_skill
):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    controller = MainController(app_root, conn)
    harness = controller.create_harness("项目撤销", "")
    skill = controller.import_skill_directory(sample_skill, "opencode")
    agents = controller.create_agents_md_asset("项目规则", "", "# Project Rules")
    mcp = controller.create_mcp_config_asset(
        "fetch",
        "Fetch",
        '{"type":"stdio","command":"uvx","args":["mcp-server-fetch"]}',
    )
    controller.add_asset_to_harness(harness.id, skill.id, "skill")
    for asset in [agents, mcp]:
        controller.add_asset_to_harness(harness.id, asset.id, asset.type)
    project_root = tmp_path / "project"

    controller.toggle_harness_deploy(
        harness.id, "opencode", project_root, scope="project"
    )
    action, result = controller.toggle_harness_deploy(
        harness.id, "opencode", project_root, scope="project"
    )

    assert action == "undeployed"
    assert result == {
        skill.id: "uninstalled",
        agents.id: "uninstalled",
        mcp.id: "uninstalled",
    }
    assert not (project_root / ".opencode").exists()
    assert not (project_root / "AGENTS.md").exists()
    assert not (project_root / "opencode.json").exists()


def test_project_undeploy_preserves_non_empty_agent_directories(
    app_root, tmp_path, sample_skill
):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    controller = MainController(app_root, conn)
    harness = controller.create_harness("保留用户目录", "")
    skill = controller.import_skill_directory(sample_skill, "opencode")
    controller.add_asset_to_harness(harness.id, skill.id, "skill")
    project_root = tmp_path / "project"

    controller.toggle_harness_deploy(
        harness.id, "opencode", project_root, scope="project"
    )
    user_file = project_root / ".opencode" / "user-tool.json"
    user_file.write_text('{"owner":"user"}\n', encoding="utf-8")

    action, result = controller.toggle_harness_deploy(
        harness.id, "opencode", project_root, scope="project"
    )

    assert action == "undeployed"
    assert result == {skill.id: "uninstalled"}
    assert user_file.is_file()
    assert (project_root / ".opencode").is_dir()
    assert not (project_root / ".opencode" / "skills" / skill.id).exists()


def test_global_codex_deploy_status_and_undeploy_support_multiple_mcp_assets(
    app_root, tmp_path
):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    controller = MainController(app_root, conn)
    harness = controller.create_harness("多 MCP", "")
    fetch = controller.create_mcp_config_asset(
        "fetch",
        "Fetch",
        '{"type":"stdio","command":"uvx","args":["mcp-server-fetch"]}',
    )
    browser = controller.create_mcp_config_asset(
        "browser",
        "Browser",
        '{"type":"stdio","command":"npx","args":["@playwright/mcp"]}',
    )
    for asset in [fetch, browser]:
        controller.add_asset_to_harness(harness.id, asset.id, asset.type)
    target = tmp_path / ".codex" / "skills"

    controller.toggle_harness_deploy(harness.id, "codex", target)

    assert controller.harness_deploy_status(harness.id, "codex", target)

    action, result = controller.toggle_harness_deploy(harness.id, "codex", target)

    assert action == "undeployed"
    assert result == {fetch.id: "uninstalled", browser.id: "uninstalled"}
    assert not (target.parent / "config.toml").exists()


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
