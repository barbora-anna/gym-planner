"""Hard sets per muscle — counts only; whether they're enough is the Coach's call.

A hard set is a working set ended within `HARD_SET_RIR_MAX` reps of failure, at any rep
count. Each one credits muscles fractionally through `exercise-map.json`. A working set with
no RIR can't be judged, so its credit goes in a separate "not judged" column (an upper
bound), never silently in or out. Warm-ups, timed sets and missed attempts (0 reps) never
count. An exercise missing from the muscle map is listed, never a silent zero.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

from ..models.exercises import Exercise
from .metrics import is_hard_set
from .muscles import MuscleMap, load_muscle_map

__all__ = ["HARD_SET_RIR_MAX", "Volume", "count"]

#: Practical convention, not a biological boundary: hypertrophy rises as sets approach
#: failure with no established cutoff (Robinson et al. 2024). Sets at RIR 0–3 count.
HARD_SET_RIR_MAX = 3.0


@dataclass
class Volume:
    hard: dict[str, float] = field(default_factory=dict)
    not_judged: dict[str, float] = field(default_factory=dict)
    hard_sets: int = 0
    not_judged_sets: int = 0
    unknown_role_sets: int = 0
    unmapped: set[str] = field(default_factory=set)

    def lines(self) -> list[str]:
        out = [f"Hard sets: {self.hard_sets}"
               + (f" (+{self.not_judged_sets} working sets with no RIR, not judged)"
                  if self.not_judged_sets else "")]
        muscles = sorted(self.hard.keys() | self.not_judged.keys(),
                         key=lambda m: (-self.hard.get(m, 0.0), m))
        if muscles:
            out.append(f"  {'muscle':<12} {'hard':>5}  not judged")
        for m in muscles:
            nj = self.not_judged.get(m)
            out.append(f"  {m:<12} {self.hard.get(m, 0.0):>5.2f}" + (f"  +{nj:.2f}" if nj else ""))
        if self.unknown_role_sets:
            out.append(f"  {self.unknown_role_sets} set(s) of unknown role: not counted")
        if self.unmapped:
            out.append(f"  not in the muscle map, not counted: {', '.join(sorted(self.unmapped))}")
        return out


def count(sets: Iterable[tuple[Exercise, str | None, int | None, int | None, float | None]],
          muscle_map: MuscleMap | None = None) -> Volume:
    """`sets` = (exercise, role, reps, seconds, rir) for each set, logged or planned."""
    mm = muscle_map or load_muscle_map()
    v = Volume()
    for exercise, role, reps, seconds, rir in sets:
        if role is None:
            v.unknown_role_sets += 1
            continue
        if role != "working" or seconds is not None or reps == 0:
            continue
        credit = mm.contributions_for(exercise)
        if not credit.is_mapped:
            v.unmapped.add(exercise.key)
            continue
        if rir is None:
            v.not_judged_sets += 1
            target = v.not_judged
        elif is_hard_set(rir, HARD_SET_RIR_MAX):
            v.hard_sets += 1
            target = v.hard
        else:
            continue
        for muscle, c in credit.muscles.items():
            target[muscle] = target.get(muscle, 0.0) + c
    return v
