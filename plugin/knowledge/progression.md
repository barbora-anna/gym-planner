# Progression: what changes next time

Progressive overload is necessary for continued adaptation (ACSM 2009, consensus). Whether
you progress with load or with reps is close to a free choice: adding load and adding reps
worked equally in untrained (Chaves 2024) and trained lifters (Plotkin 2022).

## Double progression (the default for `load`-mode lifts)

| Type | Rep range | Target RIR | Jump |
|---|---|---|---|
| Compound | 6–10 | 2 | the smallest real step: +2.5 kg on a barbell, the next dumbbell, one machine step |
| Isolation | 10–15 | 2 | the smallest real step available |

- **Rep ranges:** inside the range where hypertrophy is similar when sets are taken near
  failure (Schoenfeld 2021), and close to ACSM 2009's 6–12 RM. No study set these exact
  bounds.
- **RIR 2:** strength gains are similar across a wide RIR range (Robinson 2024), and failure
  adds at most a trivial hypertrophy edge (Refalo 2023, ES 0.19).
- **Jump:** the smallest real step, within ACSM 2009's 2–10% load increase.

Judge it on last time's working sets, from `gym lift <exercise>`. Straight sets put later
sets lower by design, so judge effort on **set 1**:
- **Every working set reached the top of the range, and set 1 ended at or above the target
  RIR** → next load up (one step). Plan the reps where `gym calc rir <new load>x<reps>
  --from <last time's set 1>` gives the target RIR, usually 1–2 below the top of the range.
  If one step is more than ~10% of the load (light dumbbells, coarse stacks), raise the rep
  ceiling instead: that keeps the jump within ACSM 2009's 2–10%.
- **Within the range** → same load, aim for +1 rep on at least one set.
- **A grind** (set 1 more than 1 rep below the target RIR, or any missed rep) → hold the
  load. Reported RIR is accurate to about ±1 (Halperin 2022; Refalo 2024), so a 1-rep miss
  is noise. Later sets ~1 RIR below set 1 are fatigue, not a grind: reps fall across sets
  from about set 3 even with 3–5 minutes' rest (Senna 2011, sets to failure). The "~1" itself
  is a convention.
- **Below the bottom of the range two sessions in a row** → drop one step. No study defines
  when to cut load; two sessions avoids reacting to one bad day.
- **RIR unknown** → ask the lifter before deciding. Don't add load on a guess.
- A jump of more than ~10% *and* more than one step week on week is more likely a logging
  slip than adaptation. Check it, and say why if you mean it.

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
- **Method and jump size don't depend on level.** Adding load or adding reps worked equally in
  untrained (Chaves 2024) and trained lifters (Plotkin 2022). ACSM 2009: +2–10% load once
  the lifter beats the target reps by 1–2, at every level. No study shows novices need
  smaller jumps; they just earn them more often.
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

- **load**: double progression as above.
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
