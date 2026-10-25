# Plan checklist

Go through every item against the plan file before you show it. A "no" means fix the plan
and check again, not explain it away. Items marked ⚙ need a `gym` command: run it, don't
eyeball it.

## Structure, per exercise

- [ ] Every exercise has **at least one working set**.
- [ ] Sets go **warm-ups first, then working sets**. No warm-up after a working set.
- [ ] Working sets are **straight**: one load across all of them (`loads.md` →
      "Working-set structure"). No back-offs, pyramids or drop sets, unless that's the
      lifter's usual scheme.
- [ ] **No copied rows.** Set 1 prints its target (`6 @2`). Later working sets print the
      honest one (`5–6 @1–2`: `label` one rep lower at the bottom, `rir` half a point
      lower but never below 1; after `3 @1`: `2–3 @1`), never a copy of set 1.
- [ ] **No fake warm-ups.** Every set with the same load as the working sets is a working
      set. A run of identical sets labelled warm-up is a mistake.
- [ ] Warm-ups **ascend**: no two at the same load, each **strictly below** the working load,
      none within one increment of it.
- [ ] Warm-ups **follow the ramp table** (`loads.md`) for this exercise's situation: first
      compound vs already-worked muscle vs isolation vs bodyweight. Loads are the table's %
      of W, and reps are no more than the table's. Fewer sets than the table is fine once
      collapsed steps are dropped. Isolation after its muscle was worked has none.
- [ ] **No warm-up is a hard set** ⚙: `gym calc rir <step>x<reps> --from <anchor>` on the
      heaviest warm-up of more than 3 reps. The low end must be ≥ 4. Top singles and
      doubles of a near-max ramp are exempt (a convention, untested).
- [ ] A **near-max** working set (≥ 90% of the e1RM's low end, or ≤ 3 reps at RIR ≤ 1) on a
      compound has the near-max ramp from `loads.md`, unless the same pattern was already
      trained earlier in the session. (The ~90% top step is a testing convention.)

## Loads

- [ ] **Every working load came from `gym calc load`** ⚙ (its first, low value), rounded down
      to the lifter's real increment, from a recent anchor (a set 1) named in your notes. Or, where
      `loads.md` says no e1RM applies (new lift, isolation past 10 effective reps, under
      5 kg, bodyweight-plus or assisted), it's last time's load by the double-progression
      rule, with the reason in notes. Nothing typed from memory.
- [ ] **Every warm-up load came from `gym calc pct`** ⚙ with `--min` set to the floor.
- [ ] **First working set implied RIR** ⚙: `gym calc rir <W>x<reps> --from <anchor>` lands
      within ~1 rep of the planned RIR (the accuracy of reported RIR, Halperin 2022). Later
      sets sit lower: their printed targets say so.
      Every formula beyond failure → the load is wrong.
- [ ] The anchor's RIR was known, or the lifter agreed to an assumed RIR (and the plan says
      so). A floor anchor (no RIR) was never used silently.
- [ ] **Change vs last time** (`gym lift`): the working load went up only if the
      load-first rule says so (`progression.md`: the `gym calc rir` check on load + step
      passed), or because the anchor changed (a newly reported RIR).
      Any jump over ~10% *and* more than one increment has a reason you can state.
- [ ] **Loads exist.** Barbell loads are ≥ the bar's weight and make up from the lifter's
      plates. Fixed bars and dumbbells are weights they actually have. Machine loads match
      the stack steps or plates. Plate-loaded machines count plates only.
- [ ] Load conventions are right: dumbbells per hand, the true load on cables, added load on
      bodyweight lifts.
- [ ] Measure fits the lift (`gym find` shows the mode): reps on `load`/`reps` lifts, seconds
      on holds. No load on a bodyweight lift unless it's the weighted variant.

## Reps and effort

- [ ] Rep ranges and target RIR fit the lift type and the lifter's level (`progression.md` →
      "Rep ranges and effort"). Novices: no near-max work needed, RIR 2 (3 on an unfamiliar
      lift).
- [ ] Main lifts for an intermediate or advanced lifter's strength goal use the heavy row
      (3–6 reps), or their usual scheme. If the plan departs from their usual scheme, the
      summary says so and why.
- [ ] Every working *rep* set has a target RIR. Timed holds don't need one.
- [ ] At most one near-max effort, on the first lift. Later heavy lifts carry a little more
      RIR.

## The session

- [ ] Heavy and skill-demanding compounds come first, isolation later.
- [ ] Exercise identities are exact catalog names (`gym find`), and each was either done
      before or agreed with the lifter as new.
- [ ] It respects the profile: equipment, dislikes, health notes, anything they said today.
- [ ] It fits the time they have. Count roughly sets × (work + rest).
- [ ] Rest (`rest_s`) is set for every exercise, following `volume.md` → "Rest": compounds
      ≥ ~120 s for trained lifters, 3–5 min for heavy sets (reps + RIR ≤ 6; ACSM 2009,
      consensus); 60–120 s is enough for novices; or shorter with a stated reason.
- [ ] **Week view** ⚙: `gym volume --plan <this plan>`. Directly trained muscles are heading
      for about 10–20 hard sets this week, judged against level and recovery. Nothing is
      wildly over or forgotten.

## Ready to show

- [ ] Every value is filled in: no "?", no "TBD", nothing the lifter has to work out or
      correct.
- [ ] Top-level `notes` has the readiness rule (`recovery.md`) with this session's computed
      up and down loads, or "no mid-session increase" for a novice (Helms 2016, an expert
      recommendation).
- [ ] Each exercise's `notes` is one useful line, not filler.
- [ ] Anything assumed (an RIR, a machine's weight) is stated, and was agreed.
