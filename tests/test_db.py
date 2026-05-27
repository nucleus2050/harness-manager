from __future__ import annotations

from harness_manager.app_paths import AppPaths
from harness_manager.db import connect, initialize_database
from harness_manager.repositories import ClientRepository, PackageRepository, SkillRepository


def test_initialize_database_seeds_clients(app_root):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)

    initialize_database(conn)

    clients = ClientRepository(conn).list_clients()
    assert [client.type for client in clients] == ["codex", "claude_code", "opencode"]
    assert [client.name for client in clients] == ["Codex", "Claude Code", "OpenCode"]


def test_create_skill_and_package_membership(app_root):
    paths = AppPaths(app_root)
    paths.ensure()
    conn = connect(paths.db_path)
    initialize_database(conn)

    skills = SkillRepository(conn)
    packages = PackageRepository(conn)
    skills.upsert_skill("skill-a", "Skill A", "codex", "skills/skill-a", "abc")
    package_id = packages.create_package("Work A", "Daily workflow")
    packages.add_skill(package_id, "skill-a", 1)

    package_skills = packages.list_package_skills(package_id)
    assert package_skills[0].id == "skill-a"
    assert package_skills[0].name == "Skill A"
