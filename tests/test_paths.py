from pathlib import Path

from gym_buddy import paths


def test_home_from_env(monkeypatch, tmp_path):
    monkeypatch.setenv("GYM_BUDDY_HOME", str(tmp_path))
    assert paths.home() == tmp_path


def test_home_default(monkeypatch):
    monkeypatch.delenv("GYM_BUDDY_HOME", raising=False)
    assert paths.home() == Path("~/training").expanduser()


def test_home_empty_env_falls_back(monkeypatch):
    monkeypatch.setenv("GYM_BUDDY_HOME", "")
    assert paths.home() == Path("~/training").expanduser()
