"""`gym lift` (one lift's history, with an e1RM per working set) and `gym find` (the catalog)."""

from __future__ import annotations

from itertools import groupby

from ..models.exercises import find as catalog_find
from ..strength.modes import progression_mode
from ..strength.muscles import load_muscle_map
from ._common import UserError, kg, repo, resolve_exercise
from .calc import SetSpec, e1rm_text

_FIND_LIMIT = 40


def register(sub) -> None:
    p = sub.add_parser("lift", help="one lift's history with e1RM estimates")
    p.add_argument("query", help="CATEGORY:NAME, or words matching a lift you've logged")
    p.add_argument("--last", type=int, default=6, help="workouts to show (default 6)")
    p.set_defaults(func=_lift)

    f = sub.add_parser("find", help="search the exercise catalog")
    f.add_argument("query", nargs="?", help="words, e.g. 'hip thrust'")
    f.add_argument("--muscle", help="exercises crediting this muscle, strongest first")
    f.set_defaults(func=_find)


def _lift(args) -> int:
    r = repo()
    exercise = resolve_exercise(args.query, r.logged_exercises())
    mode = progression_mode(exercise).mode
    sets = r.sets(exercise)
    print(f"{exercise.key}  (mode: {mode})")
    if not sets:
        print("  never logged")
        return 0
    workouts = [list(g) for _, g in groupby(sets, key=lambda s: (s.date, s.workout_id))]
    for group in workouts[-args.last:]:
        print(f"{group[0].date} {group[0].date.strftime('%a')}  {group[0].workout_id}")
        for s in group:
            role = {"warmup": "warm-up", "working": "working", None: "role ?"}[s.role]
            measure = f"{s.seconds} s" if s.seconds is not None else f"{'?' if s.reps is None else s.reps}"
            rir = "" if s.role == "warmup" else f" @ RIR {kg(s.rir)}"
            line = f"  {role:<8} {kg(s.weight_kg)} kg × {measure}{rir}"
            if mode == "load" and s.role != "warmup" and s.weight_kg and s.reps:
                line += f"   e1RM {e1rm_text(SetSpec(s.weight_kg, s.reps, s.rir))}"
            print(line)
    if len(workouts) > args.last:
        print(f"  … {len(workouts) - args.last} earlier workout(s): --last {len(workouts)}")
    return 0


def _find(args) -> int:
    if not args.query and not args.muscle:
        raise UserError("give words to search for, or --muscle")
    mm = load_muscle_map()
    logged = repo().logged_exercises()
    if args.muscle:
        if args.muscle not in mm.muscles():
            raise UserError(f"unknown muscle {args.muscle!r} — one of: {', '.join(mm.muscles())}")
        keys = mm.trains(args.muscle)
        if args.query:
            words = args.query.upper().split()
            keys = [k for k in keys if all(w in k.replace("_", " ") for w in words)]
        print(f"Credits {args.muscle}, strongest first (a CATEGORY line covers every name in it "
              "unless listed on its own):")
        for k in keys[:_FIND_LIMIT]:
            credit = mm.entry(k)[args.muscle]
            last = [d for e, d in logged.items() if e.key == k or e.category == k]
            print(f"  {credit:<4g} {k}" + (f"  (last done {max(last)})" if last else ""))
        return 0
    hits = catalog_find(args.query)
    if not hits:
        print(f"Nothing in the catalog matches {args.query!r}.")
        return 0
    for e in hits[:_FIND_LIMIT]:
        muscles = mm.contributions_for(e)
        top = ", ".join(m for m, c in sorted(muscles.muscles.items(), key=lambda kv: -kv[1]) if c >= 0.75)
        bits = [progression_mode(e).mode, top or ("unmapped" if not muscles.is_mapped else "")]
        if e in logged:
            bits.append(f"last done {logged[e]}")
        print(f"  {e.key}  ({'; '.join(b for b in bits if b)})")
    if len(hits) > _FIND_LIMIT:
        print(f"  … {len(hits) - _FIND_LIMIT} more — add a word to narrow it")
    return 0
