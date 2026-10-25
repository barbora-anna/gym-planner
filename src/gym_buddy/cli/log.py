"""`gym log …`: store and read finished workouts.

`from-artifact` transcribes the session page's rows into a workout draft (so no number is
retyped); the Coach reviews it with the lifter, fills what's blank, then `save`s it.
Saving over a stored workout prints the diff and writes only with `--confirm`.
"""

from __future__ import annotations

import json
from pathlib import Path

from ..models.session import PlannedSession
from ..models.workout import LoggedSet, Workout
from ..storage.workouts import diff
from ..strength.modes import progression_mode
from ._common import UserError, date, kg, read_json, repo, validated


def register(sub) -> None:
    p = sub.add_parser("log", help="store and read finished workouts")
    log = p.add_subparsers(dest="log", required=True)

    s = log.add_parser("save", help="store a workout JSON (diff + --confirm to overwrite)")
    s.add_argument("file")
    s.add_argument("--confirm", action="store_true")
    s.set_defaults(func=_save)

    sh = log.add_parser("show", help="stored workouts, newest last")
    sh.add_argument("id", nargs="?")
    sh.add_argument("--last", type=int, default=3)
    sh.add_argument("--from", dest="from_date", type=date)
    sh.add_argument("--to", dest="to_date", type=date)
    sh.add_argument("--json", action="store_true", help="the stored JSON, e.g. to edit and re-save")
    sh.set_defaults(func=_show)

    rm = log.add_parser("rm", help="delete a stored workout")
    rm.add_argument("id")
    rm.add_argument("--confirm", action="store_true")
    rm.set_defaults(func=_rm)

    fa = log.add_parser("from-artifact", help="session page rows + plan → workout draft JSON")
    fa.add_argument("rows", help="the page's `sets` rows (ArtifactData list output)")
    fa.add_argument("plan", help="the plan JSON the page was rendered from")
    fa.add_argument("--notes", help="the page's `notes` rows, optional")
    fa.add_argument("-o", "--out", help="write here instead of stdout")
    fa.set_defaults(func=_from_artifact)


# --- save / show / rm ------------------------------------------------------------------

def _save(args) -> int:
    new = validated(Workout, read_json(args.file), args.file)
    r = repo()
    old = r.get(new.id)
    if old is not None:
        changes = diff(old, new)
        if not changes:
            print(f"UNCHANGED  {new.id}")
            return 0
        print(f"{new.id} is already stored. Saving replaces it:")
        print("\n".join(changes))
        if not args.confirm:
            print("NOT SAVED  re-run with --confirm once the lifter agrees")
            return 2
    r.save(new)
    print(f"SAVED  {new.id}")
    print("\n".join(_workout_lines(new)))
    blanks = _blanks(new)
    if blanks:
        print("BLANKS — ask the lifter, then re-save:")
        print("\n".join(blanks))
    return 0


def _show(args) -> int:
    r = repo()
    if args.id:
        w = r.get(args.id)
        if w is None:
            raise UserError(f"no workout {args.id!r} — `gym log show` lists them")
        found = [w]
    else:
        found = r.workouts(args.from_date, args.to_date, last=args.last)
    if args.json:
        print(json.dumps([json.loads(w.model_dump_json(exclude_none=True)) for w in found], indent=2))
        return 0
    if not found:
        print("No workouts logged.")
    for w in found:
        print("\n".join(_workout_lines(w)) + "\n")
    return 0


def _rm(args) -> int:
    r = repo()
    w = r.get(args.id)
    if w is None:
        raise UserError(f"no workout {args.id!r}")
    if not args.confirm:
        print("\n".join(_workout_lines(w)))
        print("NOT REMOVED  re-run with --confirm once the lifter agrees")
        return 2
    r.remove(args.id)
    print(f"REMOVED  {args.id}")
    return 0


def _workout_lines(w: Workout) -> list[str]:
    head = f"{w.date} {w.date.strftime('%a')}  {w.id}"
    head += "".join(f"  [{x}]" for x in (w.source, w.session) if x)
    lines = [head] + ([f"  note: {w.note}"] if w.note else [])
    for ex in w.exercises:
        lines.append(f"  {ex.exercise.key}" + (f"  — {ex.note}" if ex.note else ""))
        lines += [f"    {_set_text(s)}" for s in ex.sets]
    return lines


def _set_text(s: LoggedSet) -> str:
    role = {"warmup": "warm-up", "working": "working", None: "role ?"}[s.role]
    measure = f"{s.seconds} s" if s.seconds is not None else f"{'?' if s.reps is None else s.reps}"
    load = f"{kg(s.weight_kg)} kg × " if s.weight_kg is not None or s.seconds is None else ""
    rir = "" if s.role == "warmup" else f" @ RIR {kg(s.rir)}"
    return f"{role:<8} {load}{measure}{rir}"


def _blanks(w: Workout) -> list[str]:
    """What a later decision would trip on: no load on a loaded lift, no reps, no RIR on a
    working set, no role."""
    out: list[str] = []
    for ex in w.exercises:
        loaded = progression_mode(ex.exercise).mode == "load"
        for n, s in enumerate(ex.sets, 1):
            missing = [name for name, gap in (
                ("role", s.role is None),
                ("kg", loaded and not s.weight_kg),
                ("reps", s.reps is None and s.seconds is None),
                ("RIR", s.role == "working" and s.seconds is None and s.rir is None)) if gap]
            if missing:
                out.append(f"  {ex.exercise.key} set {n}: no {', no '.join(missing)}")
    return out


# --- from-artifact -----------------------------------------------------------------------

def _rows(data, path: str) -> list[dict]:
    """ArtifactData list output (`[{id, data, …}]`, or `{"docs": [...]}`) → the row data."""
    if isinstance(data, dict):
        data = data.get("docs") or data.get("rows") or data.get("items") or []
    if not isinstance(data, list):
        raise UserError(f"{path}: expected a list of rows")
    return [r["data"] if isinstance(r, dict) and isinstance(r.get("data"), dict) else r
            for r in data if isinstance(r, dict)]


def _from_artifact(args) -> int:
    plan = validated(PlannedSession, read_json(args.plan), args.plan)
    rows = [r for r in _rows(read_json(args.rows), args.rows) if r.get("session") == plan.id]
    if not rows:
        raise UserError(f"no rows for session {plan.id} in {args.rows}")
    position = {plan.set_id(i, j): (i, j) for i, ex in enumerate(plan.exercises)
                for j in range(len(ex.sets))}
    planned_keys = [ex.exercise.key for ex in plan.exercises]

    def order(r: dict):
        if r.get("planned_set_id") in position:
            return position[r["planned_set_id"]] + ("",)
        # an extra set: after its exercise's planned sets, else after the whole plan
        i = planned_keys.index(r["exercise"]) if r.get("exercise") in planned_keys else len(planned_keys)
        return (i, 10_000, r.get("updatedAt") or "")

    notes = {}
    if args.notes:
        notes = {n.get("exercise"): n.get("note") for n in _rows(read_json(args.notes), args.notes)
                 if n.get("session") == plan.id and n.get("note")}

    exercises: list[dict] = []
    for r in sorted((r for r in rows if r.get("status") == "done"), key=order):
        if not exercises or exercises[-1]["exercise"] != r["exercise"]:
            exercises.append({"exercise": r["exercise"], "sets": []})
            if notes.get(r["exercise"]):
                exercises[-1]["note"] = notes[r["exercise"]]
        exercises[-1]["sets"].append({k: r.get(k) for k in LoggedSet.model_fields if r.get(k) is not None})
    if not exercises:
        raise UserError("no set is marked done yet")
    draft = {"id": f"{plan.date}-{plan.slug}", "date": plan.date.isoformat(), "session": plan.id,
             "source": "artifact", "exercises": exercises}
    w = validated(Workout, draft, args.rows)          # fail here, not at save
    text = json.dumps(json.loads(w.model_dump_json(exclude_none=True)), indent=2)
    if args.out:
        Path(args.out).write_text(text + "\n")
        print(f"WROTE  {args.out}")
        blanks = _blanks(w)
        if blanks:
            print("BLANKS — ask the lifter, fill them in the draft:")
            print("\n".join(blanks))
    else:
        print(text)
    return 0

