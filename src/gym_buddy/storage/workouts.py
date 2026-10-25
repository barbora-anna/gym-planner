"""The workout log: save, read, remove. Saving over an existing workout is the caller's
decision — `diff` shows what would change, and the CLI asks for `--confirm`."""

from __future__ import annotations

import datetime
import sqlite3

from ..models.exercises import Exercise
from ..models.workout import FlatSet, Workout

__all__ = ["WorkoutRepo", "diff"]

_FIELDS = ("role", "weight_kg", "reps", "seconds", "rir")


class WorkoutRepo:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def get(self, workout_id: str) -> Workout | None:
        row = self.conn.execute("SELECT doc FROM workout WHERE id = ?", (workout_id,)).fetchone()
        return Workout.model_validate_json(row["doc"]) if row else None

    def save(self, workout: Workout) -> None:
        """Insert, or replace a workout of the same id (its sets with it)."""
        with self.conn:
            self.conn.execute("DELETE FROM workout WHERE id = ?", (workout.id,))
            self.conn.execute(
                "INSERT INTO workout (id, date, session, doc, saved_at) VALUES (?, ?, ?, ?, ?)",
                (workout.id, workout.date.isoformat(), workout.session,
                 workout.model_dump_json(exclude_none=True),
                 datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds")))
            self.conn.executemany(
                'INSERT INTO "set" (workout_id, ord, category, name, role, weight_kg, reps, '
                "seconds, rir) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                [(s.workout_id, s.ord, s.exercise.category, s.exercise.name, s.role,
                  s.weight_kg, s.reps, s.seconds, s.rir) for s in workout.flat()])

    def remove(self, workout_id: str) -> bool:
        with self.conn:
            return self.conn.execute("DELETE FROM workout WHERE id = ?",
                                     (workout_id,)).rowcount > 0

    def workouts(self, from_date: datetime.date | None = None,
                 to_date: datetime.date | None = None,
                 last: int | None = None) -> list[Workout]:
        """Oldest first. `last` keeps the most recent N of the matches."""
        sql, args = "SELECT doc FROM workout WHERE 1=1", []
        if from_date:
            sql += " AND date >= ?"
            args.append(from_date.isoformat())
        if to_date:
            sql += " AND date <= ?"
            args.append(to_date.isoformat())
        rows = self.conn.execute(sql + " ORDER BY date, id", args).fetchall()
        found = [Workout.model_validate_json(r["doc"]) for r in rows]
        return found[-last:] if last else found

    def sets(self, exercise: Exercise | None = None,
             from_date: datetime.date | None = None,
             to_date: datetime.date | None = None) -> list[FlatSet]:
        """Stored sets, oldest first; one exercise (exact identity) or all of them."""
        sql = ('SELECT s.*, w.date FROM "set" s JOIN workout w ON w.id = s.workout_id '
               "WHERE 1=1")
        args: list = []
        if exercise is not None:
            sql += " AND s.category = ? AND s.name IS ?"
            args += [exercise.category, exercise.name]
        if from_date:
            sql += " AND w.date >= ?"
            args.append(from_date.isoformat())
        if to_date:
            sql += " AND w.date <= ?"
            args.append(to_date.isoformat())
        rows = self.conn.execute(sql + " ORDER BY w.date, w.id, s.ord", args).fetchall()
        return [FlatSet(workout_id=r["workout_id"], date=r["date"], ord=r["ord"],
                        exercise=Exercise(r["category"], r["name"]),
                        **{f: r[f] for f in _FIELDS}) for r in rows]

    def logged_exercises(self) -> dict[Exercise, datetime.date]:
        """Every exercise ever logged, with the last date it was done."""
        rows = self.conn.execute(
            'SELECT s.category, s.name, MAX(w.date) AS last FROM "set" s '
            "JOIN workout w ON w.id = s.workout_id GROUP BY s.category, s.name").fetchall()
        return {Exercise(r["category"], r["name"]): datetime.date.fromisoformat(r["last"])
                for r in rows}


def diff(old: Workout, new: Workout) -> list[str]:
    """What saving `new` over `old` changes, one line per difference. Empty = identical."""
    lines = [f"  {f}: {getattr(old, f)!r} → {getattr(new, f)!r}"
             for f in ("date", "session", "source", "note") if getattr(old, f) != getattr(new, f)]
    old_sets = {(s.exercise.key, n): s for n, s in _numbered(old)}
    new_sets = {(s.exercise.key, n): s for n, s in _numbered(new)}
    for k in sorted(old_sets.keys() | new_sets.keys(), key=lambda k: (k[0], k[1])):
        a, b = old_sets.get(k), new_sets.get(k)
        where = f"  {k[0]} set {k[1]}"
        if a is None:
            lines.append(f"{where}: added")
        elif b is None:
            lines.append(f"{where}: removed")
        else:
            lines += [f"{where} {f}: {getattr(a, f)!r} → {getattr(b, f)!r}"
                      for f in _FIELDS if getattr(a, f) != getattr(b, f)]
    return lines


def _numbered(w: Workout):
    """Each set with its 1-based number within its exercise."""
    counts: dict[str, int] = {}
    for s in w.flat():
        counts[s.exercise.key] = counts.get(s.exercise.key, 0) + 1
        yield counts[s.exercise.key], s
