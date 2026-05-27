from __future__ import annotations

from harness_manager.client_detection import detect_default_paths


def test_detect_default_paths_uses_userprofile(monkeypatch, tmp_path):
    profile = tmp_path / "profile"
    monkeypatch.setenv("USERPROFILE", str(profile))

    paths = detect_default_paths()

    assert paths == {
        "codex": profile / ".codex" / "skills",
        "claude_code": profile / ".claude" / "skills",
        "opencode": profile / ".config" / "opencode" / "skills",
    }


def test_detect_default_paths_uses_opencode_config_dir(monkeypatch, tmp_path):
    profile = tmp_path / "profile"
    config_dir = tmp_path / "opencode-config"
    monkeypatch.setenv("USERPROFILE", str(profile))
    monkeypatch.setenv("OPENCODE_CONFIG_DIR", str(config_dir))

    paths = detect_default_paths()

    assert paths["opencode"] == config_dir / "skills"
