from __future__ import annotations

from harness_manager.models import Asset, Harness


def test_asset_model_stores_type_and_path():
    asset = Asset(
        id="asset-1",
        type="agents_md",
        name="代码审查规则",
        source_type="custom",
        relative_path="assets/agents/asset-1/AGENTS.md",
        fingerprint="abc123",
        metadata_json="{}",
    )

    assert asset.type == "agents_md"
    assert asset.relative_path.endswith("AGENTS.md")


def test_harness_model_stores_name_and_description():
    harness = Harness(id="h1", name="代码审查 Harness", description="审查任务工具包")

    assert harness.name == "代码审查 Harness"
    assert harness.description == "审查任务工具包"
