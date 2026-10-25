# Volume: how much work

## Hard sets

- A **hard set** is a working set ended at RIR ≤ 3, at any rep count. It's the unit volume is
  counted in. The cutoff is a practical convention: hypertrophy rises as sets approach
  failure, with no established universal boundary (Robinson et al. 2024).
- `gym volume` counts them per muscle with fractional credit: 1 = prime mover, 0.5 / 0.25 =
  synergist. Counting a synergist's set as half fit the dose-response data best (Pelland
  2026). The 0.25 value and the per-exercise credits are estimates, not measured. A working set
  with no RIR shows as "not judged" (an upper bound), never silently counted or dropped.
- Warm-ups, timed holds and missed reps never count.
- A planned RIR of 3 sits on the hard-set edge: a lifter who ends one rep further from
  failure drops out of the count. Don't rely on RIR-3 sets to reach the weekly band.
- Low-rep sets count fully if their RIR qualifies. Heavy loads maximise strength but likely
  build less muscle per set at 2–4RM (Schoenfeld et al. 2021). Mention it if a muscle's
  volume is mostly low-rep work.
- Count hard sets, never tonnage.

## Weekly sets per muscle

- About **10–20 hard sets per week** for a muscle the lifter is actively training. ≥ 10 is
  associated with more hypertrophy (ACSM 2026; Pelland 2026). Gains keep rising with more
  volume but by less each time, with no specific point where they stop (Pelland 2026), so
  the 20 is a convention for the top of the band. Over it is information, not an error.
  Novices grow on less: ~4 sets per muscle was the most effective dose for untrained
  lifters (Rhea 2003; `progression.md`).
- Apply it to **directly trained** muscles only. A muscle that only gets synergist credit
  isn't held to the minimum.
- "Not enough" only if even the not-judged bound falls short.
- "Add sets" is the wrong advice when the lifter's limit is recovery (other training, outside
  activity, life stress), not volume.
- If one muscle dominates the week's hard sets and that isn't the lifter's goal, mention
  it.
- Read a week as a window (`gym volume`, default the last 7 days). Add the drafted session
  with `--plan` to see where the week lands.

## Rep ranges

- Hypertrophy happens across a wide range of loads when sets are taken close to failure (the
  repetition continuum, Schoenfeld et al. 2021). The rep ranges in `progression.md` are
  practical defaults, not requirements.
- Strength is load-specific: heavy loads build 1RM best (Schoenfeld 2017; Lopez 2021), so a
  lifter chasing a heavier single needs some heavier, lower-rep work.

## Rest

- More than 2 minutes maximises strength gains in trained lifters, and 60–120 s is enough for
  untrained ones (Grgic 2018). In trained men, 3 minutes beat 1 minute for strength and some
  hypertrophy outcomes (Schoenfeld 2016). Hypertrophy gains a little from resting more than
  60 s, and nothing past ~90 s (Singer 2024).
- Default: at least ~2 minutes for compounds. Shorter rest for isolation is a convention:
  single-joint lifts also kept more reps with longer rest (Senna 2011).
- Put it in the plan as `rest_s`: the session page prints it in the exercise header.
