# Loads: choosing the weight

## e1RM: what it is and isn't

- `gym calc` gives every estimate as a range across two formulas (Brzycki, Epley). The
  width is how much the models disagree, not how precise the number is.
- **Effective reps = reps + RIR.** The estimate is trusted up to ~10 effective reps:
  prediction equations hold up to about 10 reps (Reynolds 2006). Past that, Brzycki drops out and the result is marked rough. Isolation sets of 10–15 reps and
  top-of-range compound sets are often past it: their e1RM is a weak basis. Prefer a lower-rep
  set as the `--from` anchor when one exists. If none does, progress that lift by double
  progression from last time's load (see `progression.md`), not from an e1RM.
- **No RIR = a floor.** A set logged without RIR is treated as taken to failure, so the
  estimate understates the max and loads computed from it come out too light. Before
  prescribing from such a set, ask the lifter how many reps they had left. If they can't
  say, you may assume RIR 2 on a top set that wasn't to failure, **only with their
  agreement**, and say the load rests on an assumed RIR. No study supports that number, and
  it lifts the load above the floor, so it's the less cautious choice. Use it only as the
  `--from` input. Never write an assumed RIR into the log.
- Rep capacity at a given %1RM varies by lift and person: ~14 reps at 70% 1RM on bench
  press vs ~19 on leg press (Nuzzo et al.). On high-rep-capacity lifts (leg press, machines),
  extrapolating down in reps overestimates the load. `gym calc load` warns when the gap is
  ≥ 3 reps (a tool threshold, not from a study); take the low end of the range.
- Brzycki is the most widely used formula, but LeSuer et al. (in untrained students) found
  exercise-dependent bias, and every equation under-predicted the deadlift.
- Don't anchor on very light sets (under ~5 kg): one increment is a large share of the load,
  and the validation studies used heavier lifts (LeSuer 1997; Reynolds 2006).
- **`gym calc` assumes the number is the whole load moved.** Never use it on bodyweight-plus
  lifts (weighted pull-ups, dips): the bodyweight is missing, so the result is wrong. Never
  use it on assisted lifts either: the number is assistance, so the maths runs backwards.
  Progress those by double progression from last time's load. On plate-loaded machines it
  slightly understates load changes (the sled isn't counted).

## RIR

- RIR = reps left in reserve when the set ended. The lifter reports it on the session page.
  It's the number Strava never records, so collect it every session.
- Lifters under-predict their reps to failure by ~1 on average (Halperin et al. 2022), so
  loads computed from reported RIR err light. The spread between people was small (SD ~1.5
  reps), but results varied a lot between studies. Treat a reported RIR as ±1. Whether
  experience helps is contested: accuracy tended to improve with experience in one study
  (Steele 2017), while Halperin found no effect of training status.
- Accuracy is worse in sets of more than ~12 reps to failure (reps + RIR) (Halperin 2022).
- Recalled RIR ("I think I had 2 left", the next day): no study tested next-day recall; the
  validation studies collected RIR right at the set. Prefer RIR logged at the time.
- A computed RIR (`gym calc rir`) assumes a fresh set. Later sets at the same load sit
  lower: fatigue isn't modelled.

## Straight sets (the default working structure)

Straight, pyramid and drop sets gave equal results at matched volume (Angleri 2017):
- Pick the load so **set 1** lands at the target RIR (`gym calc load REPS --rir R --from
  <recent set> --step <increment>`).
- Keep that load for every working set and let reps fall by up to 2 across the sets (Senna
  2011: reps decline from about set 3 even with 3–5 minutes' rest).
- "Up to 2" is a convention: how far reps fall depends on rest and load.
- If a later set would fall below the bottom of the rep range, the load is too heavy: drop
  one increment.
- No back-off sets for now. The evidence on them is thin: one small exploratory trial
  (Androulakis-Korakakis 2021, n = 8 per group) compared a heavy single plus back-offs with
  the single alone, not with straight sets, and no trial compares back-off drop sizes.

## Rounding and equipment

- Always round **down** to a load the lifter can actually make (`--step`). Use their real
  increments from the profile: plate pairs (usually 2.5 kg total on a barbell; 1.0 or 0.5 kg
  with fractional plates), dumbbell jumps, machine stack steps.
- `gym calc load` prints the rounded-down low end first ("120 kg (up to 122.5 kg)"). **Use
  the first value.**
- `--step` rounds from zero, so it only fits regular steps. For fixed or irregular loads (an
  8 kg EZ bar, fixed 30/40 kg bars, a dumbbell rack with gaps), take the heaviest load they
  have at or below the low end. Check it with `gym calc rir`, and if it's off by more than 1
  rep, change the reps rather than the load.
- Barbell loads include the bar. Know which bars they have and what each weighs (for
  example 20 / 30 / 40 kg fixed bars, a 15 kg women's bar). A barbell load can never be
  below the bar.
- Dumbbells and kettlebells: per hand. Machines and cables: the true load moved. If a
  pulley halves the load, the lifter accounts for it (remind them the first time).
  Plate-loaded machines and the Smith machine: the plates only, never the sled or carriage.
  Bodyweight lifts: added load only. Assisted lifts: the number is the assistance, so less is
  progress.
- 30% 1RM is a guide for the lightest useful working set, not a cutoff. 20% 1RM still
  produced some hypertrophy, less than heavier loads (Lasevicius 2018). Light sets only
  work taken close to failure (Lasevicius 2022).

## Warm-up ramps

W = the first working load. The step pattern follows the evidence below. The exact
percentages and rep counts per row are conventions no trial set. Compute each step with
`gym calc pct W <percents> --step <increment> --min <floor>`. The floor is the bar weight,
the lightest dumbbell pair or the machine minimum. For floor pulls (deadlift) and the hip
thrust, it's the bar plus full-diameter plates (usually 60 kg on a 20 kg bar). Drop any
step that rounds onto the step before it, or that lands within one increment of W.

| Situation | Steps (load × reps) | Warm-up sets |
|---|---|---|
| First barbell compound, near-max (see below) | bar × 5–10 → 50% × 5 → 70% × 3 → 80% × 2 → 90% × 1 | 4–5 |
| Any other first barbell compound | bar × 8–10 → 50% × 5 → 70% × 3 → 85% × 1–2 | 3–4 |
| Second compound for muscles already worked (RDL after squat, incline after bench) | 60% × 5 → 80% × 2–3 | 1–2 |
| Machine or cable compound, first for those muscles | 50% × 8 → 80% × 3–5 | 1–2 |
| Dumbbell compound | (50–60% × 6–8 →) 80% × 3–5 | 1–2 |
| Isolation, muscle already worked | none | 0 |
| Isolation, first for that joint | 50–60% × 8–10 | 0–1 |
| Bodyweight or bodyweight-plus | a few bodyweight reps, or an easier variant | 0–1 |

**Near-max** = a working set at ≥ 90% of the e1RM range's low end, or ≤ 3 reps at RIR ≤ 1
(a definition: 3 reps at RIR 1 is ≈ 88–92% 1RM by Brzycki and Epley). A 12-rep set at RIR 1
is hard, but it isn't near-max.

Basis (small trials that measured performance in that session only, not gains over weeks;
the evidence is mixed): the step that matters is a heavy one, ~80% of W for 5 reps or fewer.
In trained men, one warm-up of 5 reps at 80% of W before each exercise gave more total reps
over 3 sets to failure than 10 reps at 60% or 15 at 40%: clearly on bench press, borderline
on leg press (Viveiros et al. 2024). Light, few-rep warm-ups weren't enough for squat and
bench (Ribeiro 2020). Not every trial agrees: a 3-rep warm-up at 90% gave no more squat reps
than a light one (Souza et al. 2024). A 3-rep step at 90% before sets at 75% 1RM gave more
reps (Alves 2021). Ramping to ~90% before *near-max* work is a testing convention, not
trial-tested. Keep reps low as the load rises: the light, high-rep warm-up did worst (Viveiros
2024). Isolation warm-ups are optional; none of these studies tested isolation. Warm-ups
also rehearse the lift and check the day's readiness.
- Keep every step's reps well short of failure. A warm-up must never be a hard set.
- Rest about 1 minute between early steps, and 2–3 minutes before the first working set
  (convention).
- Still open: whether one 80% × 5 step is enough before moderate-rep barbell work
  (Viveiros 2024 tested only that, against our 3–4-step ramp; Ribeiro 2020 found a 2-set
  warm-up best for bench but a single 80% set for squat), jump sizes for very heavy lifters,
  and floor-pull ramps beyond the plate floor.
