from __future__ import annotations

from skillpkg.client_detection import detect_default_paths


def test_detect_default_paths_uses_userprofile(monkeypatch, tmp_path):
    profile = tmp_path / "profile"
    monkeypatch.setenv("USERPROFILE", str(profile))

    paths = detect_default_paths()

    assert paths == {
        "codex": profile / ".codex" / "skills",
        "claude_code": profile / ".claude" / "skills",
        "opencode": profile / ".opencode" / "skills",
    }
