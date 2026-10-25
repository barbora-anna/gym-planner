# Progression: what changes next time

Progressive overload is necessary for continued adaptation (ACSM 2009, consensus). Two rules:
- **Load first** (the default where `gym calc` is valid: target reps + RIR ≤ ~10): keep the
  reps, add weight. Reps are the fallback when one load step is too big.
- **Double progression** (above ~10 effective reps, lifts with no e1RM, or when the lifter
  prefers it): reps to the top of a range, then one step.

## Start from their usual scheme

If the lifter has a usual scheme for a lift (sets × reps, how hard), plan from it. This is a
product choice, not a training claim: the evidence allows it but doesn't require it.
Trained lifters rated enjoyment and load preference alike at 70% and 83% 1RM to failure
(Emanuel 2021). A self-selected session felt better than the same session prescribed
(Barton 2025, one session, one exercise). No study tested adherence by rep range in trained
lifters. Planning near the anchor's reps also keeps `gym calc` extrapolation short.

- The load still comes from `gym calc load` at the target RIR, never from their usual
  number. If their usual load doesn't fit their latest set, ask.
- Effort comes from this file, not from habit. Usual sets ending at RIR 0 move to RIR 1–2:
  failure isn't needed (Grgic 2022) and strength is similar across RIR (Robinson 2024).
  Sets ending beyond RIR 3 aren't hard sets. Left to choose, trainees pick ~53% 1RM on
  average (Steele 2022).
- Say so when their scheme works against their goal (only 12+ reps when chasing a heavier
  max; near-max singles for a novice). Give the reason and let them choose.

## Rep ranges and effort (`load`-mode lifts)

Start from the lifter's usual scheme for the lift, if they have one (above). Otherwise:

| Lift | Level | Reps | Target RIR |
|---|---|---|---|
| Main lift for a strength goal: the lifts they want heavier, and close variants | intermediate, advanced | 3–6 | 2 (1 allowed on the session's first lift; at ≤ 3 reps that's near-max, see `session-design.md`) |
| Other compounds | any | 6–10 | 2 |
| Isolation | any | 10–15 | 2 |
| Any lift | novice | compound 6–10, isolation 10–15 | 2 (3 on an unfamiliar lift) |

- **Heavy for a heavier max.** Programmes at ≥ 80% 1RM gained the most strength in a
  network meta-analysis of 178 trials, and training status didn't change it (Currier
  2023). ≤ 8RM beat 9–15RM by a small, non-significant margin (Lopez 2021). In trained men,
  2–4RM beat 8–12RM for squat 1RM (Schoenfeld 2016a), and 3–5 reps beat 10–12 for bench
  1RM (Mangine 2015). ACSM 2009 (consensus): intermediate and advanced lifters use 1–12
  RM, eventually emphasising 1–6 RM, for strength; novices use 8–12 RM.
- **What it doesn't show.** The trials in trained lifters are small (17–29 men), last 8
  weeks, and take sets mostly to failure. No trial tested trained women or the hip thrust, and
  none compared loads at the same RIR short of failure.
- **3–6 at RIR 2 is a convention.** Reps + RIR then lands at 5–8, about 80–90% 1RM by
  `gym`'s formulas. No study set these bounds. Stopping at RIR 2 isn't shown to cost strength:
  gains are similar across a wide RIR range (Robinson 2024, exploratory), and failure adds at most a trivial
  hypertrophy edge (Refalo 2023a, ES 0.19).
- **Muscle per set.** Muscle growth is similar across loads near failure (Currier 2023;
  Lopez 2021), so accessories stay at moderate reps. Low reps may build less muscle per
  set: 8–12RM grew the thigh more than 2–4RM at equal sets (Schoenfeld 2016a), and it took
  7 sets of 3RM to match 3 sets of 10RM for the biceps (Schoenfeld 2014). Not every trial
  agrees (Mangine 2015).
- **Heavier anchors make better data.** e1RM formulas are trusted up to ~10 effective reps
  (Reynolds 2006), and RIR is predicted more accurately with heavier loads and fewer reps
  (Halperin 2022).
- **Heavy sets need longer rest:** 3–5 min for heavy loading (1–6 RM, i.e. reps + RIR ≤ 6) (ACSM 2009,
  consensus; `volume.md` → "Rest"), and the near-max warm-up (`loads.md`).
- **6–10 and 10–15 elsewhere:** muscle growth is similar across loads when sets end near
  failure (Schoenfeld 2021), and ACSM 2009 emphasises 6–12 RM for hypertrophy. No study set
  these bounds.

## Progression: load first (default where target reps + RIR ≤ ~10)

Keep the reps, add load. ACSM 2009 (consensus): add 2–10% once the lifter beats the target
reps by 1–2. Adding load and adding reps grew muscle alike in trained (Plotkin 2022) and
untrained lifters (Chaves 2024). Strength slightly favoured adding load in trained lifters
(+2.0 kg, 90% CI −2.4 to 7.8, Plotkin 2022). Both trials started at 8–12 RM, took every
set to failure and lasted 8–10 weeks; neither tested heavy low-rep work. Adding reps at a
fixed load drifts to a lighter share of 1RM, and strength is load-specific (Currier 2023).
So for a strength goal, reps are the fallback. Loads adjusted by RIR, RPE or bar speed
matched percentage-based loading for 1RM in trained lifters (Hickmott 2022; Helms 2018).

The step is the smallest real one: +2.5 kg or +5 kg on a barbell (the lifter's smallest
plates), the next dumbbell, one machine step.

Judge it on last time's working sets, from `gym lift <exercise>`. Later sets are fatigued
(`loads.md` → "Working-set structure"), so judge effort on **set 1**:
- **Set 1 made the target reps at or above the target RIR** → check one step up with
  `gym calc rir <load+step>x<reps> --from <last time's set 1>`. If the low end is no more than
  ~1 rep below the target RIR, and above 0 (so a target of RIR 1 never computes to failure),
  use that load next time with the same reps.
- **The step is too big for this load** (that check lands more than ~1 rep below the
  target, or one step is more than ~10% of the load) → keep the load and add a rep to set 1
  each session (while reps + RIR stay ≤ ~10, so `gym calc` stays valid) until the check
  passes at the target reps; then take the step and go back to the target reps. If that takes
  the lift outside its rep range, say so and suggest fractional plates or a dumbbell
  variant. If the ~10 cap comes first, take the step at the reps `gym calc rir` gives, as in
  double progression. One rep is about 3% of 1RM by `gym`'s formulas, so a 5 kg step on
  a 60 kg squat is worth 2–3 reps. Light lifts with coarse plates are meant to progress this
  way; fractional plates, if the lifter has them, keep it load first.
- **Set 1 made the target reps, but below the target RIR (by up to ~1)** → same load, same
  reps.
- **Double progression** (for sets above ~10 effective reps, such as most isolation work
  and the top of 6–10; lifts with no e1RM: bodyweight-plus, assisted, under 5 kg, see
  `loads.md`; or when the lifter prefers it): every working set at the top of the range and
  set 1 at or above the target RIR → one step up. Reps go to where `gym calc rir` gives the
  target RIR if an e1RM applies, otherwise to the bottom of the range. Within the range →
  same load, +1 rep on at least one set. If one step is more than ~10% of the load, raise the
  rep ceiling instead.
- **A grind** (set 1 more than 1 rep below the target RIR, a missed rep on set 1, or a later
  set more than one rep below its printed range) → hold the load. Reported RIR is accurate to about ±1
  (Halperin 2022; Refalo 2024), so a 1-rep miss is noise. Later sets inside their printed
  range (`5–6 @1–2`) are on plan, not a grind: reps and reserve fall across sets even with
  3–5 minutes' rest (Senna 2011; Refalo 2023b). The "~1" itself is a convention.
- **Set 1 short of its target reps (or the bottom of the range) two sessions in a row** → drop
  one step. No study defines when to cut load; two sessions avoids reacting to one bad day.
- **RIR unknown** → ask the lifter before deciding. Don't add load on a guess.
- A jump of more than ~10% *and* more than one step week on week is more likely a logging
  slip than adaptation. Check it, and say why if you mean it.

**Heavy and moderate days** (intermediate or advanced, strength goal, optional). At matched
volume, alternating loads across the week beat linear progression for 1RM in trained lifters
(ES 0.61, CI 0.00–1.22, Moesgaard 2022), with no difference in muscle. Contested (Harries
2015; Schoenfeld 2016b, varied vs constant zones; Rodríguez-Rosell 2021). Offer it; don't
make it the default. Judge each day type against the last session of the same kind:
`gym lift`'s latest set may be from the other day type.

## By lifter level

Classify level as ACSM 2009 does: **novice** = no resistance training, or none for several
years; **intermediate** ≈ 6 months of consistent training; **advanced** = years. Treat
"untrained" as novice.

- **Novices gain fastest; gains slow with training age.** Over 21 weeks, untrained men gained
  21% maximal force vs 4% in strength athletes on the same programme (Ahtiainen 2003,
  n = 8 + 8). In 14,690 adults on a minimal-dose programme, strength rose ~30–50% in year 1
  and had nearly plateaued by 1–2 years (Steele 2023). Stronger male powerlifters improve
  more slowly (Latella 2020). For intermediate and advanced lifters, weeks at one load with
  reps creeping up are expected, not a stall.
- **Novices need a smaller dose.** Meta-analyses put the most effective dose at ~60% 1RM,
  3 days/week, 4 sets per muscle for untrained; ~80%, 2 days, 4 sets for recreationally
  trained; ~85%, 2 days, 8 sets for athletes (Rhea 2003; Peterson 2004, 2005). These pool
  pre–post changes across studies, so they are associations, not tested optima. ACSM 2009
  (consensus) recommends 8–12 RM loads for novices; 1–12 RM, eventually emphasising 1–6 RM,
  for intermediate and advanced lifters. A novice doesn't need near-max work to get stronger.
  Heavy work earns its place with training status, or when a heavier single is the goal
  (heavy loads build 1RM best: Schoenfeld 2017; Lopez 2021).
- **Failure isn't needed.** Failure vs non-failure made no overall difference to strength or
  size; failure helped hypertrophy slightly only in trained subgroups (Grgic 2022). Strength
  gains are similar across a wide RIR range (Robinson 2024). Target RIR 2 suits every level;
  a novice on an unfamiliar lift can sit at RIR 3 at little cost (no trial compared RIR 1 vs
  3 in novices). **Exception, light loads:** in untrained men, 30% 1RM sets grew muscle only
  when taken to failure; at 80% 1RM, stopping short matched failure (Lasevicius 2022).
- **Method and jump size don't depend on level.** Adding load or adding reps grew muscle
  alike in untrained (Chaves 2024) and trained lifters (Plotkin 2022), within 8–12 RM.
  ACSM 2009: +2–10% load once the lifter beats the target reps by 1–2, at every level. No
  study shows novices need smaller jumps; they just earn them more often.
- **A novice's RIR is weaker evidence.** Accuracy improved with experience in one study
  (n = 141, Steele 2017); a meta-analysis found no effect of training status (Halperin 2022).
  This is contested, so be conservative: judge a novice's progression on completed reps
  first, and don't raise load mid-session on their RIR (Helms 2016: an expert
  recommendation, not a trial).
- **Novice e1RMs go stale fast** (1RM isn't stable early, Helms 2016): anchor on recent sets.
- **New lifts start lighter, at any level.** An unaccustomed exercise causes the most
  soreness the first time, and that bout protects against the next (repeated-bout effect,
  Hyldahl 2017). Whether starting light helps technique or long-term gains is untested.
- **Individual response is huge.** On one 12-week arm programme, untrained adults' 1RM gains
  ranged from 0 to +250% (Hubal 2005, n = 585). Level sets the starting defaults; the
  lifter's log overrides them.

## By progression mode (from `gym find` / `gym lift`)

- **load**: load first, as above.
- **reps** (bodyweight, bands): add reps up to ~20, then a harder variation or added load.
  ~20 is a practical cap: 30% 1RM sets of ~34 reps to failure still grew muscle (Lasevicius
  2022), but RIR estimates degrade past ~12 reps (Halperin 2022).
- **hold** (planks, timed holds): add seconds up to ~60 s, then a harder variation or load. No
  study tested a cutoff.
- **none** (mobility, conditioning, warm-up drills): as last time.
- **Assisted** lifts: the number is the assistance, so less is progress.

## When things change

- **New exercise**: no history, so no e1RM. Pick a conservative starting load from a related
  lift if there's an obvious one (and say so), or from the lifter's estimate. Plan RIR 3: a
  margin for an unknown load (untested). The first session becomes the anchor.
- **After a layoff** (a lift not trained for ≥ ~3 weeks): strength held for up to ~3 weeks
  of detraining in elite athletes, then declined (McMaster 2013). Maximal force declines with
  the length of the break, more in older and inactive people (Bosquet 2013), with no
  threshold for how much to reduce. Show how old the last data is (`gym lift` dates) and ask
  how they feel. Restart at the bottom of the rep range at RIR 3 (untested), then build back.
- **A rough day** isn't a trend. Two or three sessions are (no study sets the number).
- Recovery and test sessions aren't a reference for progression.
