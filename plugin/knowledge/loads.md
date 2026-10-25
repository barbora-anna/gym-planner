# Loads: choosing the weight

## e1RM: what it is and isn't

- `gym calc` gives every estimate as a range across two formulas (Brzycki, Epley). The
  width is how much the models disagree, not how precise the number is.
- **Effective reps = reps + RIR.** The estimate is trusted up to ~10 effective reps:
  prediction equations hold up to about 10 reps (Reynolds 2006). Past that, Brzycki drops out and the result is marked rough. Isolation sets of 10–15 reps and
  top-of-range compound sets are often past it: their e1RM is a weak basis. Prefer a lower-rep
  set as the `--from` anchor when one exists. If none does, progress that lift by double
  progression from last time's load (see `progression.md`), not from an e1RM.
- Anchor on the latest **set 1** of a lift. Later sets are fatigued, so their e1RMs read low
  ("Working-set structure" below).
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

## Working-set structure

At one load, every set is harder than the one before, even with 3–5 minutes' rest. Sets to
failure lose reps from about set 3 (Senna 2011, 10RM; Scudese 2015, 3RM bench). Stopping at
a target RIR, trained lifters lost about 3 reps (RIR 3) to 5 (RIR 1) from set 1 to set 6 at
75% 1RM with 4 minutes' rest, roughly half a rep to a rep per set (Refalo 2023b). The drift at a target RIR is untested on heavier, shorter sets. So never print the same reps and RIR on every set.

**Straight sets** are the default. Straight, pyramid and drop sets gave equal results at
matched volume (Angleri 2017, 50–85% 1RM).
- Pick the load so **set 1** lands at the target RIR (`gym calc load REPS --rir R --from
  <recent set> --step <increment>`). Keep that load for every working set.
- Print set 1 with its target (`6 @2`) and later sets with the honest one: the bottom of the
  reps one lower, the RIR half a point lower but never below 1 (`5–6 @1–2`: `"label": "5–6"`,
  `"rir": 1.5`; after `3 @1`: `2–3 @1`).
  The lifter does the full reps while at least 1 is left, otherwise stops one short. The
  label is a convention: the drift was measured at 75% 1RM, not on heavier sets.
- Falling 1–2 reps short on later sets is fatigue, not a miss. "Up to 2" is a convention.
- If a later set would fall below the bottom of the rep range, the load is too heavy: drop
  one increment.
- No back-off sets by default. This is a product simplification, not a finding: set
  structures did alike (above). No trial compares
  a top set plus back-offs with straight sets. The one small trial added back-offs to a
  heavy single and compared that with the single alone (Androulakis-Korakakis 2021, n = 8
  per group), and no trial compares back-off drop sizes. For volume around heavy work, add
  moderate-rep accessories for the same muscles, or alternate heavy and moderate days
  (`progression.md`).

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

Basis (small trials, mostly young trained men, measuring that session only, not gains over
weeks; the evidence is mixed):
- Heavy dynamic warm-ups improve strength and power performance (McCrary 2015, systematic
  review of upper-body warm-ups).
- For working-set reps, the one trial with a no-warm-up control found no effect: 4 sets to
  failure at 80% 1RM in bench press, squat and curl went alike after no warm-up, a specific
  one, cardio, or both (Ribeiro AS 2014).
- Among warm-ups, one heavier, low-rep set did best: 5 reps at 80% of W gave more total reps
  over 3 sets to failure than 10 at 60% or 15 at 40% (Viveiros 2024; clear on bench press,
  borderline on leg press). On bar speed, 6 reps at 40% of W was the weakest warm-up for
  squat and bench (Ribeiro B 2020; differences ~0.02 m/s).
- A heavy set above the working load (90% 1RM before sets at 75% 1RM) is potentiation, not
  a warm-up step: it gave no more squat reps overall (Souza 2024; more in set 1 only).

So keep reps low as the load rises, and reach a step near 80% of W before barbell work. The
number of steps, their percentages and reps are conventions. Ramping to ~90% before
near-max work is a testing convention, not trial-tested. Isolation warm-ups are optional:
none of these trials tested isolation. Rehearsing the lift and reading the day's readiness
are practical reasons, untested. No study has tested whether warming up prevents injury in
lifting (McCrary 2015 found none for the upper body): don't promise it.
- Keep every step's reps well short of failure. A warm-up must never be a hard set.
- Rest about 1 minute between early steps, and 2–3 minutes before the first working set
  (convention).
- A general warm-up (easy cardio) is optional, and never goes in the plan as an exercise. If
  the lifter does one, keep it easy:
  - 15 minutes of easy cycling raised leg-press 1RM ~3%, 15 minutes at moderate-hard effort
    lowered it ~4%, and 5 minutes changed nothing (Barroso 2013, 16 trained men);
  - before sets to failure at 80% 1RM, cardio made no difference (Ribeiro AS 2014).
- Static stretching isn't needed. If the lifter likes it: under ~60 s per muscle, then the
  ramp.
  - Holds of 60 s or more cost ~4.6%, vs ~1.1% for shorter ones (Behm 2016).
  - Holds under 30–45 s showed no significant loss (Kay 2012).
  - With dynamic activity afterwards, there was no clear effect (Behm 2016).
- Still open: whether one 80% × 5 step is enough before moderate-rep barbell work (every
  trial above tested single warm-up sets; none compared one step with a multi-step ramp),
  the rest before the first working set, jump sizes for very heavy lifters, and floor-pull
  ramps beyond the plate floor.
