"""Helpers every `gym` subcommand shares: input errors, files, dates, exercise lookup."""

from __future__ import annotations

import datetime
import json
from pathlib import Path

from pydantic import ValidationError

from ..models.exercises import Exercise
from ..models.exercises import find as catalog_find
from ..storage.db import connect
from ..storage.workouts import WorkoutRepo


class UserError(Exception):
    """A problem with the input: printed as one ERROR line, exit 1."""


def repo() -> WorkoutRepo:
    return WorkoutRepo(connect())


def date(text: str) -> datetime.date:
    try:
        return datetime.date.fromisoformat(text)
    except ValueError:
        raise UserError(f"{text!r} is not a date (YYYY-MM-DD)") from None


def read_json(path: str):
    try:
        return json.loads(Path(path).read_text())
    except FileNotFoundError:
        raise UserError(f"no such file: {path}") from None
    except json.JSONDecodeError as e:
        raise UserError(f"{path} is not valid JSON: {e}") from None


def validated(model, data, path: str):
    """`model.model_validate(data)`, with pydantic's errors as one readable UserError."""
    try:
        return model.model_validate(data)
    except ValidationError as e:
        problems = "; ".join(f"{'.'.join(map(str, err['loc'])) or '(top)'}: {err['msg']}"
                             for err in e.errors())
        raise UserError(f"{path}: {problems}") from None


def kg(value: float | None) -> str:
    return "?" if value is None else f"{value:g}"


def resolve_exercise(query: str, logged: dict[Exercise, datetime.date]) -> Exercise:
    """An exact `CATEGORY:NAME`, else the one logged exercise matching every word. Anything
    else lists candidates and stops — never guess an identity."""
    try:
        exact = Exercise.model_validate(query.strip().upper())
        if ":" in query or exact in logged:    # a bare category is a search, unless logged as such
            return exact
    except ValidationError:
        pass
    words = query.upper().replace("_", " ").split()
    mine = [e for e in logged if all(w in e.key.replace("_", " ") for w in words)]
    if len(mine) == 1:
        return mine[0]
    candidates = mine or catalog_find(query)
    if not candidates:
        raise UserError(f"no exercise matches {query!r} — try `gym find`")
    shown = "\n".join(f"  {e.key}" + (f"  (last done {logged[e]})" if e in logged else "")
                      for e in candidates[:20])
    more = f"\n  … {len(candidates) - 20} more" if len(candidates) > 20 else ""
    raise UserError(f"{query!r} is ambiguous — pass one of these as CATEGORY:NAME\n{shown}{more}")
