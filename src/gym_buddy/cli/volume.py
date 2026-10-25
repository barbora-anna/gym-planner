"""`gym volume`: hard sets per muscle over a window of the log, plus any planned sessions."""

from __future__ import annotations

import datetime

from ..models.session import PlannedSession
from ..strength.volume import HARD_SET_RIR_MAX, count
from ._common import date, read_json, repo, validated


def register(sub) -> None:
    p = sub.add_parser("volume", help="hard sets per muscle (default: the last 7 days)")
    p.add_argument("--from", dest="from_date", type=date)
    p.add_argument("--to", dest="to_date", type=date)
    p.add_argument("--plan", nargs="+", default=[], metavar="PLAN_JSON",
                   help="add planned sessions, counted at their target RIR")
    p.set_defaults(func=_volume)


def _volume(args) -> int:
    to_date = args.to_date or datetime.date.today()
    from_date = args.from_date or to_date - datetime.timedelta(days=6)
    r = repo()
    logged = r.sets(from_date=from_date, to_date=to_date)
    rows = [(s.exercise, s.role, s.reps, s.seconds, s.rir) for s in logged]
    done = {w.session for w in r.workouts(from_date, to_date) if w.session}
    plans = 0
    for path in args.plan:
        plan = validated(PlannedSession, read_json(path), path)
        if plan.id in done:
            print(f"{plan.id} is already logged: counted once, from the log")
            continue
        plans += 1
        rows += [(ex.exercise, s.role, s.reps, s.seconds, s.rir)
                 for ex in plan.exercises for s in ex.sets]
    workouts = len({s.workout_id for s in logged})
    planned = f" + {plans} planned session(s) at target RIR" if plans else ""
    print(f"{from_date} → {to_date}: {workouts} logged workout(s){planned}")
    print(f"Hard set = working set at RIR ≤ {HARD_SET_RIR_MAX:g}. Credit per muscle: 1 = prime "
          "mover, 0.5 / 0.25 = synergist (estimates).")
    print("\n".join(count(rows).lines()))
    return 0
