"""The planned session — the plan JSON the Coach writes and `gym render` turns into a page.

`sessions/<date>-<slug>.json`. Every model forbids unknown keys: a mistyped `"weight": 60`
in a draft must fail, not silently drop a load. The session id is derived
(`ps-<date>-<slug>`), never authored, so it can't drift from its date.
"""

from __future__ import annotations

import datetime

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator

from .common import LOAD_CONVENTION, Role, Slug
from .exercises import Exercise, humanise

__all__ = ["PlannedExercise", "PlannedSession", "PlannedSet"]


class PlannedSet(BaseModel):
    """One prescribed set. Exactly one of `reps` / `seconds` (a timed hold)."""
    model_config = ConfigDict(extra="forbid")
    role: Role                               # required — planned sets are never inferred
    reps: int | None = Field(default=None, ge=1)
    seconds: int | None = Field(default=None, gt=0)
    weight_kg: float | None = Field(default=None, gt=0, description=LOAD_CONVENTION)
    rir: float | None = Field(
        default=None, ge=0, le=10,
        description="Target reps in reserve — a prescription, never an observation.")
    label: str | None = None                 # shown instead of the reps, e.g. "3–4" or "optional"

    @model_validator(mode="after")
    def _reps_xor_seconds(self) -> PlannedSet:
        if (self.reps is None) == (self.seconds is None):
            raise ValueError("a set needs exactly one of reps or seconds")
        return self


class PlannedExercise(BaseModel):
    """One exercise in a session with its sets."""
    model_config = ConfigDict(extra="forbid")
    exercise: Exercise                       # "CATEGORY:NAME"
    name: str | None = None                  # display name; defaults to the humanised one
    notes: str | None = None                 # the tip shown under the name
    rest_s: int | None = Field(default=None, gt=0)
    sets: list[PlannedSet] = Field(min_length=1)

    @property
    def display_name(self) -> str:
        return self.name or humanise(self.exercise)


class PlannedSession(BaseModel):
    model_config = ConfigDict(extra="forbid")
    slug: Slug                               # "lower-a"
    date: datetime.date
    title: str = Field(min_length=1)
    subtitle: str | None = None              # one line under the title
    notes: str | None = None                 # the rules box at the top of the page
    artifact_url: str | None = None
    exercises: list[PlannedExercise] = Field(min_length=1)

    @computed_field
    @property
    def id(self) -> str:
        return f"ps-{self.date.isoformat()}-{self.slug}"

    @model_validator(mode="before")
    @classmethod
    def _drop_matching_id(cls, data):
        """Accept an `id` key (it round-trips) only if it equals the derived one."""
        if not isinstance(data, dict) or "id" not in data:
            return data
        data = dict(data)
        incoming = data.pop("id")
        if incoming != f"ps-{data.get('date')}-{data.get('slug')}":
            raise ValueError(f"id {incoming!r} doesn't match date/slug — leave it out")
        return data

    def set_id(self, exercise_index: int, set_index: int) -> str:
        """The id the session page keys each set's row on: stable for a given plan."""
        return f"{self.id}-e{exercise_index + 1}s{set_index + 1}"
