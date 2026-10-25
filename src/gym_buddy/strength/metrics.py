"""Strength metrics — estimated 1RM, reps in reserve, and the uncertainty around both.

Pure functions only: no I/O, no state, no imports from this package's other modules.

## Two reps conventions — keep them apart

- **Formula inputs are effective reps** (`reps + RIR`): `e1rm`, `reps_at`, `e1rm_interval`
  and `confidence` take the reps the set would have reached at failure; the caller adds RIR.
- **Everything that takes RIR separately takes reps COMPLETED**: `load_interval`,
  `rir_interval`, `estimate_caveats` and `load_for` (`reps` + `target_rir`) add the RIR
  themselves. Never pass effective reps to those and RIR as well.

## What these numbers are, and are not

An e1RM is a **model estimate**, not a measurement. Three things follow, and they govern
every function here:

1. **The formulas are correlated approximations, not independent votes.** `e1rm_interval`
   and `rir_interval` run the default formulas as a *sensitivity analysis* — they answer "does this
   conclusion survive a reasonable change of model?", not "what do three instruments agree
   on?". A narrow interval describes model agreement, not accurate individual capacity.
2. **Rep capacity at a given %1RM varies by exercise and by person.** The Nuzzo et al.
   meta-regression estimated ~14.1 reps at 70% 1RM for bench press but ~19.0 for leg press,
   and training status did not clearly moderate it. For a lift without direct data the
   generic curve is a population approximation and nothing more.
3. **A computed RIR assumes a fresh set against an anchor that was itself near failure.**
   It does not model inter-set fatigue, rest interval, or execution, and if the anchor set
   had reps left in it then every formula underestimates the true max. `estimate_caveats`
   surfaces these; callers must not present a computed RIR as a measured one.

## Formula choice

Default is **Brzycki** — the most widely used, compared against directly measured 1RMs
by LeSuer et al. (untrained students; exercise-dependent bias, every equation
under-predicted the deadlift), and well-behaved at r=1, where it returns the load itself.

Use estimates as advisory starting points and adjust to observed effort and performance.

See the Coach's knowledge files (`plugin/knowledge/`), *Estimating 1RM from a submaximal set*.
"""

from __future__ import annotations

from typing import Literal, NamedTuple

Formula = Literal["brzycki", "epley"]
Confidence = Literal["high", "medium", "low"]

#: Run as a sensitivity analysis. Order is stable so output is reproducible.
SENSITIVITY_FORMULAS: tuple[Formula, ...] = ("brzycki", "epley")

#: Brzycki must not be extrapolated past ~10 reps: it has an asymptote at r=37 and diverges
#: hard before it (100kg x20 -> 212kg, x30 -> 516kg). Excluded from the sensitivity set
#: above this, rather than silently poisoning the interval.
BRZYCKI_MAX_REPS = 10

#: Up to this many effective reps an e1RM is rated "high" confidence. A practical
#: convention, not a validated threshold.
HIGH_CONFIDENCE_MAX_REPS = 5

#: Above this, ANY of these formulas is extrapolating further than its validation supports.
RELIABLE_MAX_REPS = 10

#: HEURISTIC. Below ~5 kg the smallest available increment is large relative to the load,
#: and the e1RM equations were validated on heavier multi-joint lifts, so such sets stay
#: history but never anchor a load (`confidence` is "low", `estimate_caveats` warns).
LIGHT_LOAD_FLOOR_KG = 5.0

#: HEURISTIC. A prescribed set this many effective reps (reps + RIR) below the anchor is
#: extrapolating down the rep range; a rep or two is within the models' normal error, so
#: warning on any difference would fire on nearly every prescription.
REP_EXTRAPOLATION_GAP = 3


class Interval(NamedTuple):
    """A range across the sensitivity formulas, with what produced it."""
    low: float
    high: float
    formulas: tuple[str, ...]

    @property
    def spread(self) -> float:
        return self.high - self.low

    @property
    def extrapolated(self) -> bool:
        """True when fewer than all sensitivity formulas were usable. A single-formula
        interval is a point, not a range -- display it as "~X kg (extrapolated, Epley only)"."""
        return len(self.formulas) < len(SENSITIVITY_FORMULAS)

    def straddles(self, threshold: float) -> bool:
        """True when the models disagree about which side of `threshold` the answer is on."""
        return self.low <= threshold <= self.high


def e1rm(weight_kg: float, reps: float, formula: Formula = "brzycki") -> float:
    """Estimated one-rep max from a set taken to (or very near) failure.

    `reps` is EFFECTIVE reps (the formula input): what was completed with nothing left. If
    the set stopped short, add the reps in reserve first -- otherwise this underestimates.

    A point estimate. For anything that drives a decision, prefer `e1rm_interval`.
    """
    if weight_kg <= 0:
        raise ValueError(f"weight_kg must be positive, got {weight_kg}")
    if reps < 1:
        raise ValueError(f"reps must be at least 1, got {reps}")

    if formula == "brzycki":
        if reps >= 37:
            raise ValueError(f"brzycki is undefined at {reps} reps (asymptote at 37)")
        return weight_kg * 36 / (37 - reps)
    if formula == "epley":
        return weight_kg * (1 + reps / 30)
    raise ValueError(f"unknown formula {formula!r}")


def reps_at(one_rm: float, weight_kg: float, formula: Formula = "brzycki") -> float:
    """How many reps this load should be good for — the inverse of `e1rm`.

    Returns a float: 8.4 reps is a meaningful answer when judging whether a prescription of
    8 leaves reserve.
    """
    if one_rm <= 0:
        raise ValueError(f"one_rm must be positive, got {one_rm}")
    if weight_kg <= 0:
        raise ValueError(f"weight_kg must be positive, got {weight_kg}")
    if weight_kg > one_rm:
        return 0.0  # outside the estimated capacity, not an achievable maximal single
    if weight_kg == one_rm:
        return 1.0

    if formula == "brzycki":
        return 37 - 36 * weight_kg / one_rm
    if formula == "epley":
        return 30 * (one_rm / weight_kg - 1)
    raise ValueError(f"unknown formula {formula!r}")


def rir(weight_kg: float, reps: float, one_rm: float,
        formula: Formula = "brzycki") -> float:
    """Model-implied reps left in reserve after `reps` at `weight_kg`.

    Assumes a fresh set. Does not account for inter-set fatigue, rest, or execution, so the
    second set of a pair will sit below this. See `estimate_caveats`.
    """
    return reps_at(one_rm, weight_kg, formula=formula) - reps


def rir_from_rpe(rpe: float) -> float:
    """Reps in reserve from a RIR-based RPE, for RPE 7 to 10 in half steps.

    The RIR-based RPE scale of Zourdos et al. 2016 (Fig. 1; also Helms et al. 2016, Table 1)
    only -- not session RPE or Borg CR-10. RPE 10 and 9.5 are both 0: at 9.5 no more reps
    could be done, though a little more load could. Otherwise `10 - rpe`; 8.5 and 7.5 are the
    midpoints of the scale's published ranges (1-2 and 2-3 reps in reserve), not published
    values. Below 7 the scale is a band, not a count (5-6 means 4-6 reps in reserve), so
    there is no single RIR to return.
    """
    if rpe < 7:
        raise ValueError(
            f"RPE {rpe:g} is below 7: on the RIR-based scale that is a band (5-6 = 4-6 reps "
            "in reserve), not a count — ask for RIR, or leave it unknown")
    if rpe > 10 or (rpe * 2) % 1:
        raise ValueError(f"RPE {rpe:g} is not on the RIR-based scale: use 7 to 10 in steps of 0.5")
    return 0.0 if rpe >= 9.5 else 10.0 - rpe


def load_for(one_rm: float, reps: float, target_rir: float = 0.0,
             formula: Formula = "brzycki") -> float:
    """The load at which `reps` would leave `target_rir` in the tank.

    The evidence base prefers autoregulation over percentage-of-1RM for *prescribing*. Use
    this to sanity-check a load or seed one the lifter then adjusts by feel. For a load
    that drives a decision, prefer `load_interval`.

    Brzycki is refused when `reps + target_rir` exceeds `BRZYCKI_MAX_REPS`: it diverges
    toward its asymptote there.
    """
    if reps < 1:
        raise ValueError(f"reps must be at least 1, got {reps}")
    if target_rir < 0:
        raise ValueError(f"target_rir cannot be negative, got {target_rir}")

    ceiling = reps + target_rir
    if formula == "brzycki":
        if ceiling > BRZYCKI_MAX_REPS:
            raise ValueError(
                f"brzycki is not usable past {BRZYCKI_MAX_REPS} effective reps, got {ceiling:g}")
        return one_rm * (37 - ceiling) / 36
    if formula == "epley":
        return one_rm / (1 + ceiling / 30)
    raise ValueError(f"unknown formula {formula!r}")


def _usable_formulas(*rep_counts: float) -> tuple[Formula, ...]:
    """Drop formulas that would be extrapolating past their validated range."""
    worst = max(rep_counts)
    return tuple(f for f in SENSITIVITY_FORMULAS
                 if not (f == "brzycki" and worst > BRZYCKI_MAX_REPS))


def e1rm_interval(weight_kg: float, reps: float) -> Interval:
    """e1RM across the sensitivity formulas — the honest form of the estimate.

    `reps` is EFFECTIVE reps (the formula input): completed reps plus reps in reserve."""
    formulas = _usable_formulas(reps)
    values = {f: e1rm(weight_kg, reps, formula=f) for f in formulas}
    return Interval(min(values.values()), max(values.values()), tuple(values))


def rir_interval(weight_kg: float, reps: float,
                 anchor_weight_kg: float, anchor_reps: float,
                 *, anchor_rir: float | None = None) -> Interval:
    """Model-implied RIR across the sensitivity formulas, each anchored self-consistently.

    Each formula estimates the max from the anchor set *and* evaluates the prescribed set,
    so no formula is scored against another's 1RM.

    Reps convention: `reps` and `anchor_reps` are reps COMPLETED; the anchor's RIR is passed
    as `anchor_rir` and added here (None = unknown, counted as 0, so the max is a floor).

    The width is the point. A narrow interval describes model agreement, not individual accuracy.
    Neither a narrow nor a wide interval justifies blocking a prescription.
    """
    anchor_effective = anchor_reps + (anchor_rir or 0)
    formulas = _usable_formulas(reps, anchor_effective)
    values = {}
    for f in formulas:
        anchor = e1rm(anchor_weight_kg, anchor_effective, formula=f)
        values[f] = rir(weight_kg, reps, anchor, formula=f)
    return Interval(min(values.values()), max(values.values()), tuple(values))


def load_interval(anchor_weight_kg: float, anchor_reps: float, reps: float,
                  *, target_rir: float, anchor_rir: float | None = None) -> Interval:
    """The honest form of a prescribed load: `load_for` across the sensitivity formulas.

    Each formula estimates the max from the anchor *and* inverts with the same formula, so
    none is scored against another's 1RM.

    Reps convention: `anchor_reps` and `reps` are reps COMPLETED; RIR is passed separately
    and added here. `target_rir` is required (a prescription always has an intended
    reserve); `anchor_rir=None` is counted as 0, so the result is a floor. Brzycki drops out
    when the anchor's or the target's effective reps exceed `BRZYCKI_MAX_REPS`; check
    `extrapolated`.
    """
    anchor_effective = anchor_reps + (anchor_rir or 0)
    formulas = _usable_formulas(anchor_effective, reps + target_rir)
    values = {}
    for f in formulas:
        anchor = e1rm(anchor_weight_kg, anchor_effective, formula=f)
        values[f] = load_for(anchor, reps, target_rir, formula=f)
    return Interval(min(values.values()), max(values.values()), tuple(values))


def is_hard_set(reps_in_reserve: float, rir_max: float) -> bool:
    """A hard set is terminated within `rir_max` RIR -- the unit hypertrophy volume counts in.

    `rir_max` comes from `volume.HARD_SET_RIR_MAX`; it is required so the number has one
    source. The band's edge is a practical convention, not a measured
    biological boundary -- hypertrophy rises as sets approach failure, with no established
    universal cutoff (Robinson et al. 2024)."""
    return 0 <= reps_in_reserve <= rir_max


def confidence(reps: float, weight_kg: float | None = None) -> Confidence:
    """How much to trust an e1RM derived from a set of this many reps.

    `reps` is EFFECTIVE reps (the formula input), as for `e1rm`.

    Prediction accuracy improves as rep count falls; the 5/10 boundaries here are practical
    conventions rather than validated thresholds.
    """
    if weight_kg is not None and weight_kg < LIGHT_LOAD_FLOOR_KG:
        return "low"
    if reps <= HIGH_CONFIDENCE_MAX_REPS:
        return "high"
    if reps <= RELIABLE_MAX_REPS:
        return "medium"
    return "low"


def estimate_caveats(reps: float | None, anchor_reps: float,
                     anchor_rir: float | None = None,
                     has_personal_curve: bool = False,
                     weight_kg: float | None = None,
                     target_rir: float | None = None) -> tuple[str, ...]:
    """Reasons a computed RIR should not be enforced as fact.

    These qualify advisory findings. An empty tuple does not make an estimate exact
    or suitable for blocking a plan.

    Reps convention: `reps` and `anchor_reps` are reps COMPLETED; `target_rir` and
    `anchor_rir` are passed separately and added here (None counts as 0). `reps=None`
    means there is no prescribed set (only the anchor is being judged): the prescribed-side
    and rep-gap checks are skipped.
    """
    out: list[str] = []
    effective = None if reps is None else reps + (target_rir or 0)
    anchor_effective = anchor_reps + (anchor_rir or 0)
    if effective is not None and effective > RELIABLE_MAX_REPS:
        out.append(f"prescribed set is {effective:g} effective reps — beyond where 1RM models are validated")
    if anchor_effective > RELIABLE_MAX_REPS:
        out.append(f"anchor set is {anchor_effective:g} effective reps — a weak basis for an e1RM")
    if anchor_rir is None:
        out.append("anchor set's proximity to failure is unrecorded — the max may be underestimated")
    elif anchor_rir > 1:
        out.append(f"anchor set stopped at ~{anchor_rir:g} RIR — estimate depends on reported reserve")
    if weight_kg is not None and weight_kg < LIGHT_LOAD_FLOOR_KG:
        out.append(f"load is under {LIGHT_LOAD_FLOOR_KG:g} kg, where the models are unreliable")
    gap = None if effective is None else anchor_effective - effective
    if gap is not None and gap >= REP_EXTRAPOLATION_GAP:
        out.append(f"prescribed set is {gap:g} effective reps below the anchor — on lifts that "
                   "allow many reps at a given %1RM (e.g. leg press) the load may be overestimated")
    if not has_personal_curve:
        out.append("no calibrated personal curve for this exercise — using a population approximation")
    return tuple(out)
