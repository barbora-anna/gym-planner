"""Where the lifter's data home lives. Never hardcode it elsewhere — call `home()`."""

import os
from pathlib import Path

DEFAULT_HOME = "~/training"


def home() -> Path:
    """The data home: `$GYM_BUDDY_HOME`, else `~/training`."""
    return Path(os.environ.get("GYM_BUDDY_HOME") or DEFAULT_HOME).expanduser()
