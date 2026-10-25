"""Exercise -> muscle attribution, so per-muscle volume is arithmetic instead of argument.

Without this, weekly volume can only be estimated by hand, and the hand-estimate was wrong
three ways at once: back squat excluded from glute volume, hip abduction pooled with glute
max, and an exercise's zero contribution never scored. All three are now data, in
`data/exercise-map.json`, with the reasoning beside them.

Lookup is most-specific-first: the exact `CATEGORY:NAME`, then the `CATEGORY` default. A
category default makes a whole movement pattern scorable; name entries exist only where a
variant differs materially from its category (leg press is not a back squat; a good morning
is not a leg curl, despite Garmin filing it under `LEG_CURL`).

**An unmapped exercise is never a silent zero.** `contributions_for` returns a result whose
`matched` is `None`, and callers must surface it — an exercise quietly worth nothing is how
volume gets under-counted.
"""

from __future__ import annotations

import json
from functools import cache
from importlib.resources import files
from pathlib import Path
from typing import Literal, NamedTuple

from ..models.exercises import Exercise

DEFAULT_MAP_PATH = files("gym_buddy") / "data" / "exercise-map.json"

MatchLevel = Literal["exercise", "category"]


class MuscleContribution(NamedTuple):
    """What one hard set of an exercise is worth, per muscle, and where that came from."""
    muscles: dict[str, float]
    matched: MatchLevel | None

    @property
    def is_mapped(self) -> bool:
        return self.matched is not None

    def credit(self, muscle: str) -> float:
        """Fractional hard-set credit for one muscle. Zero for an unmapped exercise —
        check `is_mapped` first; this cannot distinguish 'trains nothing' from 'unknown'."""
        return self.muscles.get(muscle, 0.0)


class MuscleMap:
    """The loaded attribution table. Holds the data; the lookup rules live here with it."""

    def __init__(self, data: dict):
        self._categories: dict[str, dict[str, float]] = data.get("categories", {})
        self._exercises: dict[str, dict[str, float]] = data.get("exercises", {})
        self.vocabulary: dict[str, str] = data.get("vocabulary", {})
        self.evidence_notes: dict[str, str] = data.get("evidence_notes", {})
        self.reviewed_on: str | None = data.get("_reviewed_on")

    def contributions_for(self, exercise: Exercise) -> MuscleContribution:
        """Most specific match wins; no match returns an explicitly unmapped result."""
        if exercise.name is not None:
            key = f"{exercise.category}:{exercise.name}"
            if key in self._exercises:
                return MuscleContribution(dict(self._exercises[key]), "exercise")
        if exercise.category in self._categories:
            return MuscleContribution(dict(self._categories[exercise.category]), "category")
        return MuscleContribution({}, None)

    def muscles(self) -> list[str]:
        """The canonical muscle vocabulary, in declaration order."""
        return list(self.vocabulary)

    def entry(self, key: str) -> dict[str, float]:
        """The credits stored under one map key (`CATEGORY:NAME` or `CATEGORY`)."""
        return dict(self._exercises.get(key) or self._categories.get(key) or {})

    def trains(self, muscle: str) -> list[str]:
        """Every mapped key contributing to `muscle`, strongest first — for auditing."""
        hits = [(k, v[muscle]) for k, v in
                {**self._categories, **self._exercises}.items() if muscle in v]
        return [k for k, _ in sorted(hits, key=lambda kv: (-kv[1], kv[0]))]


@cache
def _load_cached(path: str) -> MuscleMap:
    return MuscleMap(json.loads(Path(path).read_text()))


@cache
def _load_default() -> MuscleMap:
    return MuscleMap(json.loads(DEFAULT_MAP_PATH.read_text()))


def load_muscle_map(path: Path | str | None = None) -> MuscleMap:
    """The attribution table. Cached per path; pass one explicitly in tests."""
    if path is None:
        return _load_default()
    return _load_cached(str(path))


def contributions_for(exercise: Exercise, path: Path | str | None = None) -> MuscleContribution:
    """Convenience wrapper over the default map."""
    return load_muscle_map(path).contributions_for(exercise)
