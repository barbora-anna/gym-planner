"""`gym init` against a tmp data home (conftest sets GYM_BUDDY_HOME)."""

import json

from gym_buddy.cli.init import PLUGIN, settings


def test_writes_settings_into_a_fresh_home(gym, tmp_path):
    code, out = gym("init")
    path = tmp_path / ".claude" / "settings.json"
    assert code == 0 and "WROTE" in out
    written = json.loads(path.read_text())
    assert written == settings()
    assert written["enabledPlugins"] == {PLUGIN: True}
    assert written["env"]["GYM_BUDDY_HOME"] == str(tmp_path)


def test_running_twice_is_fine(gym):
    gym("init")
    code, out = gym("init")
    assert code == 0 and "already set up" in out


def test_never_overwrites_an_existing_file_and_says_what_is_missing(gym, tmp_path):
    path = tmp_path / ".claude" / "settings.json"
    path.parent.mkdir()
    mine = {"permissions": {"allow": ["Bash(gym:*)", "Bash(ls:*)"]}, "model": "opus"}
    path.write_text(json.dumps(mine))
    code, out = gym("init")
    assert code == 1 and "left alone" in out
    assert json.loads(path.read_text()) == mine
    lacking = json.loads(out.split("Add this to it:\n", 1)[1])
    assert lacking["permissions"] == {"allow": ["mcp__strava-mcp__*"], "deny": ["Bash(sqlite3:*)"]}
    assert lacking["enabledPlugins"] == {PLUGIN: True}


def test_extra_keys_in_an_existing_file_still_count_as_set_up(gym, tmp_path):
    path = tmp_path / ".claude" / "settings.json"
    path.parent.mkdir()
    want = settings()
    want["permissions"]["allow"].append("Bash(ls:*)")
    path.write_text(json.dumps({**want, "model": "opus"}))
    code, out = gym("init")
    assert code == 0 and "already set up" in out


def test_invalid_json_is_reported_not_replaced(gym, tmp_path):
    path = tmp_path / ".claude" / "settings.json"
    path.parent.mkdir()
    path.write_text("{oops")
    code, out = gym("init")
    assert code == 1 and "not valid JSON" in out
    assert path.read_text() == "{oops"
