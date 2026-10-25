"""`gym init`: make the data home and its Claude Code settings, so `claude` there is the Coach.

The settings register this repo as a plugin marketplace and enable the Coach for the data
home only (never at user scope, or every session would become the Coach). An existing
settings file is never overwritten: init says what it lacks and stops.
"""

from __future__ import annotations

import json

from ..paths import home

REPO = "barbora-anna/gym-planner"
PLUGIN = "gym-planner@gym-planner"


def register(sub) -> None:
    p = sub.add_parser("init", help="set up the data home for the Coach")
    p.set_defaults(func=_init)


def settings() -> dict:
    return {
        "permissions": {
            "allow": ["Bash(gym:*)", "mcp__strava-mcp__*"],
            "deny": ["Bash(sqlite3:*)"],
        },
        "env": {"GYM_BUDDY_HOME": str(home())},
        "extraKnownMarketplaces": {"gym-planner": {"source": {"source": "github", "repo": REPO}}},
        "enabledPlugins": {PLUGIN: True},
    }


def missing(have: dict, want: dict) -> dict:
    """What of `want` is absent from `have`: list entries, dict keys and scalars."""
    out = {}
    for key, value in want.items():
        if key not in have:
            out[key] = value
        elif isinstance(value, dict) and isinstance(have[key], dict):
            if sub := missing(have[key], value):
                out[key] = sub
        elif isinstance(value, list) and isinstance(have[key], list):
            if lacking := [v for v in value if v not in have[key]]:
                out[key] = lacking
        elif have[key] != value:
            out[key] = value
    return out


def _init(args) -> int:
    path = home() / ".claude" / "settings.json"
    want = settings()
    if path.exists():
        try:
            have = json.loads(path.read_text())
        except json.JSONDecodeError as e:
            print(f"ERROR  {path} is not valid JSON ({e}); fix it, then run `gym init` again.")
            return 1
        if lacking := missing(have, want):
            print(f"ERROR  {path} exists, so it was left alone. Add this to it:")
            print(json.dumps(lacking, indent=2))
            return 1
        print(f"OK     {path} is already set up.")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(want, indent=2) + "\n")
        print(f"WROTE  {path}")
    print(f"Next:  cd {home()} && claude   (trust the folder when asked; the Coach installs itself)")
    return 0
