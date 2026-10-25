"""The strength-exercise catalog — every exercise Garmin knows, validated at the source.

Garmin's exercises are a two-level taxonomy: a `category` (e.g. `SQUAT`) and an optional,
more specific `name` within it (e.g. `GOBLET_SQUAT`). The full, authoritative list is the
official **`garmin-fit-sdk`** FIT Profile — 51 categories (the raw enum has 53; `unknown`
and `cardio_sensors` are skipped, see `_SKIP`), ~1,846 named exercises. We load
it live at import (offline, no network) so the catalog is always exactly what the current
SDK version knows; there is no hand-curated subset to drift.

The FIT Profile spells values lowercase (`goblet_squat`); Garmin Connect's workout/activity
API uses UPPERCASE (`GOBLET_SQUAT`). We store and expose UPPERCASE — the form the Connect
API wants — so an `Exercise` translates straight through.

`Exercise` validates against the catalog on construction: an unknown category, or a name
that isn't in its category, raises. So a workout can never carry an exercise Garmin would
reject — the guarantee is enforced here, before anything reaches the wire.
"""

from __future__ import annotations

from garmin_fit_sdk import Profile
from pydantic import BaseModel, model_serializer, model_validator

__all__ = ["Exercise", "categories", "exercises_in", "find", "humanise", "weighted_twin"]

# Categories present in the taxonomy but not real prescribable exercises.
_SKIP = {"unknown", "cardio_sensors"}


def _load_catalog() -> dict[str, frozenset[str]]:
    """Build {CATEGORY: frozenset(EXERCISE_NAMES)} from the FIT Profile, UPPERCASE."""
    types = Profile["types"]
    catalog: dict[str, frozenset[str]] = {}
    for cat_key in types["exercise_category"].values():   # {int: 'squat', ...}
        if cat_key in _SKIP:
            continue
        names = types.get(f"{cat_key}_exercise_name", {})  # {int: 'goblet_squat', ...}
        catalog[cat_key.upper()] = frozenset(n.upper() for n in names.values())
    return catalog


# Built once at import — the single source of truth for validation and discovery.
_CATALOG: dict[str, frozenset[str]] = _load_catalog()


class Exercise(BaseModel, frozen=True):
    """A Garmin strength exercise: a category, optionally narrowed to a specific name.

    `Exercise("SQUAT")` is category-only; `Exercise("SQUAT", "GOBLET_SQUAT")` is specific.
    Both category and name are validated against the FIT catalog, case-insensitively —
    the FIT profile's own lowercase spelling (`goblet_squat`) is accepted and stored
    UPPERCASE, the form the Connect API wants.
    """
    category: str
    name: str | None = None

    def __init__(self, category: str | None = None, name: str | None = None, /, **data):
        # Allow positional use: Exercise("SQUAT", "GOBLET_SQUAT")
        if category is not None:
            data["category"] = category
        if name is not None:
            data["name"] = name
        super().__init__(**data)

    @model_validator(mode="before")
    @classmethod
    def _uppercase(cls, data):
        if isinstance(data, str):            # "CATEGORY:NAME" or "CATEGORY", as files write it
            category, _, name = data.partition(":")
            data = {"category": category, "name": name or None}
        if isinstance(data, dict):
            data = {k: v.upper() if k in ("category", "name") and isinstance(v, str) else v
                    for k, v in data.items()}
        return data

    @model_validator(mode="after")
    def _known_to_garmin(self) -> Exercise:
        names = _CATALOG.get(self.category)
        if names is None:
            raise ValueError(
                f"unknown exercise category {self.category!r} — see categories()"
            )
        if self.name is not None and self.name not in names:
            raise ValueError(
                f"{self.name!r} is not a known exercise in category {self.category!r} — "
                f"see exercises_in({self.category!r})"
            )
        return self

    def __str__(self) -> str:
        return self.name or self.category

    @model_serializer
    def _as_key(self) -> str:
        """Files carry `CATEGORY:NAME`, the same form they're read in."""
        return self.key

    @property
    def key(self) -> str:
        """`CATEGORY:NAME` (or `CATEGORY`): the form files and the CLI use."""
        return f"{self.category}:{self.name}" if self.name else self.category


def categories() -> list[str]:
    """All known exercise categories (UPPERCASE), sorted."""
    return sorted(_CATALOG)


def exercises_in(category: str) -> list[str]:
    """Named exercises in a category (UPPERCASE), sorted. Empty if none / unknown."""
    return sorted(_CATALOG.get(category.upper(), ()))


def find(query: str) -> list[Exercise]:
    """Every exercise whose `CATEGORY:NAME` contains every word of `query` (case-insensitive).

    The discovery helper for building strength workouts — e.g. `find("hip thrust")` surfaces
    every hip-thrust variant across the whole catalog so the Coach can pick a real one.
    """
    words = query.upper().replace(":", " ").replace("_", " ").split()
    hits: list[Exercise] = []
    for cat, names in _CATALOG.items():
        for name in (None, *names):
            text = f"{cat} {name or ''}".replace("_", " ")
            if all(w in text for w in words):
                hits.append(Exercise(cat, name))
    return sorted(hits, key=lambda e: e.key)


#: Equipment and setup words that say how a lift was loaded, not which lift it was.
_EQUIPMENT_PREFIXES = ("BARBELL_", "DUMBBELL_", "CABLE_", "MACHINE_", "WEIGHTED_",
                       "BANDED_", "BAND_", "KETTLEBELL_", "SMITH_")
_SETUP_SUFFIXES = ("_WITH_BENCH", "_ON_FLOOR", "_MACHINE", "_WITH_DUMBBELL", "_WITH_BAND")


def humanise(exercise: Exercise) -> str:
    """A readable lift name: BARBELL_HIP_THRUST_WITH_BENCH -> 'Hip Thrust'.

    Strips the equipment prefix and setup suffix, which describe how the lift was loaded
    rather than which lift it was. Best-effort prose for display, never an identity.
    """
    name = exercise.name or exercise.category
    for suffix in _SETUP_SUFFIXES:
        if name.endswith(suffix) and len(name) > len(suffix):
            name = name[: -len(suffix)]
    for prefix in _EQUIPMENT_PREFIXES:
        if name.startswith(prefix) and len(name) > len(prefix):
            name = name[len(prefix):]
            break
    return name.replace("_", " ").title()


def weighted_twin(exercise: Exercise) -> Exercise | None:
    """`X` to its `WEIGHTED_X` in the same category, if the catalog has one."""
    if exercise.name is None or exercise.name.startswith("WEIGHTED_"):
        return None
    twin = f"WEIGHTED_{exercise.name}"
    return Exercise(exercise.category, twin) if twin in exercises_in(exercise.category) else None
