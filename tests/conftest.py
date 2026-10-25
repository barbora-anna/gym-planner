import pytest


@pytest.fixture(autouse=True)
def _isolated_home(monkeypatch, tmp_path):
    """Safety net: no test can touch the real data home (~/training)."""
    monkeypatch.setenv("GYM_BUDDY_HOME", str(tmp_path))


@pytest.fixture
def gym(capsys):
    """Run `gym <argv>` through `cli.main`: returns (exit code, stdout)."""
    from gym_buddy.cli import main

    def run(*argv):
        capsys.readouterr()
        code = main([str(a) for a in argv])
        return code, capsys.readouterr().out
    return run
