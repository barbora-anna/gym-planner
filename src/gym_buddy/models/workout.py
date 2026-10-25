"""A completed workout — what `gym log save` stores, the unit of history.

The Coach writes it (`drafts/<id>.json`), from the session page's rows (`gym log
from-artifact` does the transcription), from Strava, or from what the lifter tells it.
Only what was actually done: a blank stays blank, a target is never copied in as a result.

Zero load, missed attempts and blanks:
- `weight_kg` None on a `load`-mode lift = the load is missing. On a bodyweight or timed
  lift it means no added load: a complete set.
- `reps = 0` is a missed attempt: kept in history, never a hard set.
- A timed set has `seconds`, never `reps = 0`.
"""

from __future__ import annotations

import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .common import LOAD_CONVENTION, Role, Slug
from .exercises import Exercise

__all__ = ["FlatSet", "LoggedExercise", "LoggedSet", "Workout"]


class LoggedSet(BaseModel):
    model_config = ConfigDict(extra="forbid")
    role: Role | None = None                 # None = unknown; never inferred
    weight_kg: float | None = Field(default=None, ge=0, description=LOAD_CONVENTION)
    reps: int | None = Field(default=None, ge=0)
    seconds: int | None = Field(default=None, gt=0)
    rir: float | None = Field(
        default=None, ge=0, le=10,
        description="Reps in reserve as reported by the lifter; None = not recorded.")

    @model_validator(mode="after")
    def _one_measure(self) -> LoggedSet:
        if self.reps is not None and self.seconds is not None:
            raise ValueError("a set has reps or seconds, not both")
        return self


class LoggedExercise(BaseModel):
    model_config = ConfigDict(extra="forbid")
    exercise: Exercise                       # "CATEGORY:NAME"
    note: str | None = None
    sets: list[LoggedSet] = Field(min_length=1)


class Workout(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: Slug                                 # "2026-10-24-glutes-full-body"
    date: datetime.date
    session: str | None = None               # the planned session id, if it had one
    source: str | None = None                # "artifact", "strava", "artifact+strava", "told"
    note: str | None = None
    exercises: list[LoggedExercise] = Field(min_length=1)

    def flat(self) -> list[FlatSet]:
        """Every set in order, with its exercise and date: what history queries read."""
        out: list[FlatSet] = []
        for ex in self.exercises:
            for s in ex.sets:
                out.append(FlatSet(workout_id=self.id, date=self.date, ord=len(out),
                                   exercise=ex.exercise, **s.model_dump()))
        return out


class FlatSet(LoggedSet):
    """One stored set with where it came from."""
    workout_id: str
    date: datetime.date
    ord: int
    exercise: Exercise
