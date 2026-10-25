"""Progression mode per exercise — the data behind "what does 0 kg mean, and may an e1RM drive
this lift?".

Every exercise has a mode (`load`, `reps`, `hold`, `none`), set per Garmin category with exact
name overrides and one name-prefix rule, in `progression-modes.json`.
The mode table may NOT leave a category out (unlike the muscle map): "unknown -> loaded" is the
bug this replaces, so a missing category raises rather than falling back to a default.

Lookup, first match wins: the `CATEGORY:NAME` override > a name-prefix rule > the category.
The Coach can override a mode for one lifter in their profile; code doesn't need to know.
"""

from __future__ import annotations

import json
from functools import cache
from importlib.resources import files
from pathlib import Path
from typing import Literal, NamedTuple

from ..models.common import ProgressionMode
from ..models.exercises import Exercise

DEFAULT_MODE_PATH = files("gym_buddy") / "data" / "progression-modes.json"

ModeLevel = Literal["exercise", "prefix", "category"]


class ModeMatch(NamedTuple):
    mode: ProgressionMode
    matched: ModeLevel           # where it came from


def _flatten(groups: list[dict]) -> dict[str, dict]:
    """Grouped overrides -> `{"CATEGORY:NAME": {"mode", "why"}}`. An exercise in two groups raises."""
    flat: dict[str, dict] = {}
    for group in groups:
        for key in group["exercises"]:
            if key in flat:
                raise ValueError(f"progression override {key!r} appears in more than one group")
            flat[key] = {"mode": group["mode"], "why": group["why"]}
    return flat


class ModeTable:
    """The loaded progression table. Holds the data; the lookup rules live here with it."""

    def __init__(self, data: dict):
        self._categories: dict[str, dict] = data.get("categories", {})
        self._overrides = _flatten(data.get("overrides", []))
        self._prefix_rules: list[dict] = data.get("prefix_rules", [])
        self.modes: dict[str, str] = data.get("modes", {})
        self.reviewed_on: str | None = data.get("_reviewed_on")

    def mode_for(self, exercise: Exercise) -> ModeMatch:
        """Most specific match wins. Raises `KeyError` naming the category if none matches."""
        if exercise.name is not None:
            key = f"{exercise.category}:{exercise.name}"
            if key in self._overrides:
                return ModeMatch(self._overrides[key]["mode"], "exercise")
            for rule in self._prefix_rules:
                if (exercise.name.startswith(rule["prefix"])
                        and exercise.category not in rule.get("except_categories", ())):
                    return ModeMatch(rule["mode"], "prefix")
        if exercise.category in self._categories:
            return ModeMatch(self._categories[exercise.category]["mode"], "category")
        raise KeyError(
            f"no progression mode for category {exercise.category!r} — add it to "
            "progression-modes.json (never default it)")


@cache
def _load_cached(path: str) -> ModeTable:
    return ModeTable(json.loads(Path(path).read_text()))


@cache
def _load_default() -> ModeTable:
    return ModeTable(json.loads(DEFAULT_MODE_PATH.read_text()))


def load_mode_table(path: Path | str | None = None) -> ModeTable:
    """The mode table. Cached per path; pass one explicitly in tests."""
    if path is None:
        return _load_default()
    return _load_cached(str(path))


def progression_mode(exercise: Exercise, path: Path | str | None = None) -> ModeMatch:
    """Convenience wrapper over the default table."""
    return load_mode_table(path).mode_for(exercise)
