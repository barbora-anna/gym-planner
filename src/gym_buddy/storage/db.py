"""`gym.db`: the SQLite log of completed workouts.

Each workout is stored whole (`doc`) and flattened into `set` rows for history queries.
Stdlib `sqlite3`, no ORM. The schema version lives in `PRAGMA user_version`;
`MIGRATIONS[i]` takes version *i* to *i + 1*. Callers wrap each command in `with conn:` (one transaction).
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from .. import paths

__all__ = ["MIGRATIONS", "SCHEMA_VERSION", "SchemaTooNew", "connect"]

_V1 = """
CREATE TABLE workout (
  id       TEXT PRIMARY KEY,
  date     TEXT NOT NULL,
  session  TEXT,
  doc      TEXT NOT NULL,                -- the saved workout JSON, verbatim
  saved_at TEXT NOT NULL
);
CREATE TABLE "set" (                     -- the same sets, flattened for history queries
  workout_id TEXT NOT NULL REFERENCES workout(id) ON DELETE CASCADE,
  ord        INTEGER NOT NULL,
  category   TEXT NOT NULL,
  name       TEXT,
  role       TEXT CHECK (role IN ('warmup','working')),
  weight_kg  REAL,
  reps       INTEGER,
  seconds    INTEGER,
  rir        REAL,
  PRIMARY KEY (workout_id, ord),
  CHECK (reps IS NULL OR seconds IS NULL)
);
CREATE INDEX set_exercise ON "set"(category, name);
"""

#: Entry *i* takes `user_version` *i* to *i + 1*.
MIGRATIONS: list[str] = [_V1]
SCHEMA_VERSION = len(MIGRATIONS)


class SchemaTooNew(RuntimeError):
    """gym.db was written by a newer gym."""


def _migrate(conn: sqlite3.Connection) -> None:
    version = conn.execute("PRAGMA user_version").fetchone()[0]
    if version > SCHEMA_VERSION:
        raise SchemaTooNew(f"gym.db is schema v{version}; this gym knows v{SCHEMA_VERSION} "
                           "— update gym")
    for target in range(version, SCHEMA_VERSION):
        # executescript commits first, so BEGIN..COMMIT here is the migration's own transaction
        # and the version bump is part of it.
        conn.executescript(f"BEGIN;\n{MIGRATIONS[target]}\nPRAGMA user_version = {target + 1};\nCOMMIT;")


def connect(path: Path | str | None = None) -> sqlite3.Connection:
    """Open `gym.db` (default: under the data home, resolved now), migrated to the latest schema."""
    path = Path(path) if path is not None else paths.home() / "gym.db"
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    try:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        _migrate(conn)
    except BaseException:
        conn.close()
        raise
    return conn
