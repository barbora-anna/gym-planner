"""Shared vocabulary: slugs, the small literals, and the load convention."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import StringConstraints

__all__ = ["LOAD_CONVENTION", "ProgressionMode", "Role", "Slug"]

Slug = Annotated[str, StringConstraints(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")]

Role = Literal["warmup", "working"]
# How an exercise progresses (strength/modes.py has the shipped table):
#   load  add reps, then load; 0 kg / None = a missing load; an e1RM makes sense
#   reps  add reps, then a harder variation or load; 0 kg = no added load
#   hold  add seconds, then a harder variation or load; never a hard set
#   none  maintain ("as last time"): dead bugs, mobility, warm-ups, conditioning, cardio
ProgressionMode = Literal["load", "reps", "hold", "none"]

# What `weight_kg` means, used as the Field description wherever a load is stored.
LOAD_CONVENTION = (
    "Barbell: total load including the bar. Dumbbell / kettlebell: per implement (per hand). "
    "Machine / cable: the true load the lifter moves — if a pulley halves (or otherwise "
    "changes) the load, the lifter accounts for it. Plate-loaded machine / Smith machine: "
    "the plates loaded, always — never the sled or carriage, which differs from gym to gym. "
    "Bodyweight movement: the added load only; a bodyweight or timed exercise (plank, "
    "pull-up) legitimately has no load. "
    "Assisted: the number is the assistance, not load; progress by reducing it."
)
