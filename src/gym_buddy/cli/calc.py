"""`gym calc …`: the arithmetic, so no load or RIR is ever worked out by hand.

A set is written `KGxREPS` or `KGxREPS@RIR` (`135x5@2`). Every answer is a range across
the formulas (Brzycki, Epley): the width is model disagreement, not precision. A set with
no RIR is treated as taken to failure, so the e1RM it gives is a floor.
"""

from __future__ import annotations

import math
import re
from typing import NamedTuple

from ..strength.metrics import (
    BRZYCKI_MAX_REPS,
    RELIABLE_MAX_REPS,
    SENSITIVITY_FORMULAS,
    Interval,
    e1rm_interval,
    load_for,
    load_interval,
    reps_at,
    rir_interval,
)
from ._common import UserError, kg

_SET = re.compile(r"^(\d+(?:[.,]\d+)?)x(\d+)(?:@(\d+(?:[.,]\d+)?))?$", re.IGNORECASE)


class SetSpec(NamedTuple):
    weight_kg: float
    reps: int
    rir: float | None

    @property
    def effective(self) -> float:
        return self.reps + (self.rir or 0)

    def __str__(self) -> str:
        return f"{self.weight_kg:g}×{self.reps}" + (f" @{self.rir:g}" if self.rir is not None else "")


def parse_set(text: str) -> SetSpec:
    m = _SET.match(text.strip())
    if not m:
        raise UserError(f"{text!r} is not a set — write KGxREPS or KGxREPS@RIR, e.g. 135x5@2")
    weight, reps, rir = (float(m[1].replace(",", ".")), int(m[2]),
                         None if m[3] is None else float(m[3].replace(",", ".")))
    if weight <= 0 or reps < 1:
        raise UserError(f"{text!r}: an estimate needs a load above 0 and at least 1 rep")
    return SetSpec(weight, reps, rir)


def rng(i: Interval, unit: str = " kg") -> str:
    sep = " to " if i.low < 0 else "–"
    text = f"{i.low:.1f}{unit}" if math.isclose(i.low, i.high, abs_tol=0.05) \
        else f"{i.low:.1f}{sep}{i.high:.1f}{unit}"
    return text + (" (Epley only: extrapolated)" if i.extrapolated else "")


def e1rm_text(s: SetSpec) -> str:
    """The e1RM of a set as one phrase, with the caveats that change how it reads."""
    text = rng(e1rm_interval(s.weight_kg, s.effective))
    if s.rir is None:
        text = "≥ " + text + " (no RIR: a floor)"
    if s.effective > RELIABLE_MAX_REPS:
        text += f" (rough: {s.effective:g} reps from failure is past where the formulas hold)"
    return text


def round_down(value: float, step: float) -> float:
    return math.floor(value / step + 1e-9) * step


def _from_e1rm(one_rm: float, fn) -> Interval:
    values = {}
    for f in SENSITIVITY_FORMULAS:
        try:
            values[f] = fn(f)
        except ValueError:                   # Brzycki past its range
            continue
    if not values:
        raise UserError("no formula is usable for that many reps")
    return Interval(min(values.values()), max(values.values()), tuple(values))


def register(sub) -> None:
    p = sub.add_parser("calc", help="e1RM, implied RIR, loads, percentages")
    calc = p.add_subparsers(dest="calc", required=True)

    e = calc.add_parser("e1rm", help="estimated 1RM from a set: gym calc e1rm 135x5@2")
    e.add_argument("set")
    e.set_defaults(func=_e1rm)

    r = calc.add_parser("rir", help="reps left a set would leave: gym calc rir 130x8 --from 135x5@2")
    r.add_argument("set")
    _basis(r)
    r.set_defaults(func=_rir)

    lo = calc.add_parser("load", help="load for reps at a target RIR: gym calc load 8 --rir 2 --from 135x5@2 --step 2.5")
    lo.add_argument("reps", type=int)
    lo.add_argument("--rir", type=float, required=True, help="target reps in reserve")
    lo.add_argument("--step", type=float, help="round down to this increment (kg)")
    _basis(lo)
    lo.set_defaults(func=_load)

    pc = calc.add_parser("pct", help="percentages of a working load: gym calc pct 135 40 60 80 --step 2.5 --min 20")
    pc.add_argument("load", type=float)
    pc.add_argument("percents", type=float, nargs="+")
    pc.add_argument("--step", type=float, help="round down to this increment (kg)")
    pc.add_argument("--min", type=float, help="never below this, e.g. the empty bar")
    pc.set_defaults(func=_pct)


def _basis(p) -> None:
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--from", dest="anchor", metavar="KGxREPS@RIR", help="a recent set to estimate from")
    g.add_argument("--e1rm", type=float, help="a known or estimated 1RM (kg)")


def _e1rm(args) -> int:
    s = parse_set(args.set)
    print(f"e1RM from {s}: {e1rm_text(s)}")
    return 0


def _rir(args) -> int:
    s = parse_set(args.set)
    if args.anchor:
        a = parse_set(args.anchor)
        i = rir_interval(s.weight_kg, s.reps, a.weight_kg, a.reps, anchor_rir=a.rir)
        basis = f"from {a}" + (" (anchor RIR unknown: real reserve is likely higher)" if a.rir is None else "")
    else:
        i = _from_e1rm(args.e1rm, lambda f: reps_at(args.e1rm, s.weight_kg, f) - s.reps)
        basis = f"from e1RM {args.e1rm:g} kg"
    print(f"{s}: {rng(i, ' reps')} in reserve, {basis}")
    if i.high < 0:
        print("  beyond failure on every formula: this set isn't doable as written")
    print("  a fresh set: later sets of the same load sit lower (fatigue isn't modelled)")
    return 0


def _load(args) -> int:
    if args.reps < 1 or args.rir < 0:
        raise UserError("reps must be at least 1 and --rir at least 0")
    if args.anchor:
        a = parse_set(args.anchor)
        i = load_interval(a.weight_kg, a.reps, args.reps, target_rir=args.rir, anchor_rir=a.rir)
        basis = f"from {a}" + (" (anchor RIR unknown: a floor)" if a.rir is None else "")
        if a.effective - (args.reps + args.rir) >= 3:
            basis += "; far fewer reps than the anchor: may overestimate on high-rep-capacity lifts (leg press)"
    else:
        i = _from_e1rm(args.e1rm, lambda f: load_for(args.e1rm, args.reps, args.rir, f))
        basis = f"from e1RM {args.e1rm:g} kg"
    print(f"{args.reps} reps @ RIR {args.rir:g}: {rng(i)}, {basis}")
    if args.step:
        lo, hi = round_down(i.low, args.step), round_down(i.high, args.step)
        print(f"  at {args.step:g} kg steps: {lo:g} kg" + (f" (up to {hi:g} kg)" if hi != lo else ""))
    if args.reps + args.rir > BRZYCKI_MAX_REPS:
        print(f"  {args.reps + args.rir:g} reps from failure: past where the formulas hold, treat as rough")
    return 0


def _pct(args) -> int:
    for p in args.percents:
        value = args.load * p / 100
        if args.step:
            value = round_down(value, args.step)
        if args.min is not None:
            value = max(value, args.min)
        print(f"  {p:g}%  {kg(value)} kg")
    return 0
