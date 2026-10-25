---
name: plan-session
description: Plan the lifter's next strength session (or a week of them) from their logged history, check it against the checklist, and publish it as a session page they log on. Use for "what do I lift today", "plan Monday", "plan my week", "change Monday's session".
---

# Plan a session

The plan you show must be complete and right the first time. Everything you need from the
lifter is asked in one message *before* you draft.

## 1. Read first

- The knowledge files, every time: `../../knowledge/loads.md`, `progression.md`,
  `volume.md`, `session-design.md`, `recovery.md` (paths relative to this skill's folder).
- `athlete/profile.md`: level, goals, split, equipment (bars, increments, machines),
  preferences, health. If it doesn't exist, run onboard first.
- `plan-format.md` and `checklist.md` in this folder.

## 2. Make sure the log is current

- `gym log show --last 3`. Compare it with the files in `sessions/`: a past session whose
  page has results but no logged workout → run log-workout first. Planning on stale history
  repeats last week.
- If the lifter uses Strava, check for strength sessions not in the log, and glance at the
  last ~3 days of other activity as recovery context (a practical window, `recovery.md`).

## 3. Gather the numbers

- The last session of the same kind (same slug or focus): `gym log show <id>`.
- For each lift you're likely to plan: `gym lift <CATEGORY:NAME>`. Note the most recent
  working sets, their RIR, and the e1RM range. A floor (no RIR) needs the lifter's RIR before
  you prescribe from it (see `loads.md`).
- This week so far: `gym volume`.

## 4. Ask, in one round

Only what the profile and log don't already answer. Use `AskUserQuestion` for the
fixed-choice items (one call, up to 4 questions): which session (the next in their split
first), time available, "stick with your exercises or try something new?" (with your 2–3
concrete options as choices), and how they feel. Ask the open items (an RIR, a missing
equipment fact) in a short chat message after it.

What to cover:
- Which session or focus today (offer the next one in their split), and time available.
- **Stick with their exercises, or try something new for a muscle group?** If they might
  want new, offer 2–3 concrete options from `gym find --muscle <m>`, with your pick.
- How they feel: sleep, soreness, any pain. Recent hard activity if Strava shows some.
- Any RIR you need for a floor anchor ("Your last hip thrust 135×5 had no RIR. How many
  were left?").
- Equipment facts you're missing (a bar's weight, a machine's steps), only if the plan
  depends on them.

Wait for the answers. Record anything durable (new equipment, a pain, a preference) in the
profile once they confirm it.

## 5. Draft

For each exercise, in order:
1. **Working sets.** Choose reps and target RIR from `progression.md` (by lift type and the
   lifter's level) and last time's result. Compute the load:
   `gym calc load <reps> --rir <rir> --from <recent set KGxREPS@RIR> --step <their increment>`.
   Use the first (low) value. No usable anchor (new lift, isolation past 10 effective reps,
   under 5 kg, bodyweight-plus or assisted) → progress from last time's load by the
   double-progression rule, or start conservatively (`progression.md` → "When things
   change").
2. **Warm-ups** from the ramp table in `loads.md`:
   `gym calc pct <W> <percents> --step <increment> --min <floor>`. Drop steps that collapse
   onto each other or sit within one increment of W.
3. **Rest** (`rest_s`) and a one-line tip (`notes`): a technique cue, or what matters today
   for this lift. The readiness rule goes in the top-level notes, not here.

Write it to `sessions/<date>-<slug>.json` (format: `plan-format.md`). Put the readiness rule
(`recovery.md`) in the top-level `notes`, with this session's up and down loads computed by
`gym calc load`.

## 6. Check it: `checklist.md`

Go through **every** item against the file you wrote. Run the commands it names. Fix the plan
and re-check until every item passes. Then `gym volume --plan sessions/<file>.json` to see
where the week lands.

## 7. Publish

1. `gym render sessions/<date>-<slug>.json` writes the `.html` next to it.
2. Publish that HTML with the Artifact tool. Pass capabilities `{"db": {}, "user": {}}` (the
   page saves each set to its own database) and a short icon word like `dumbbell`.
3. Add the artifact URL to the plan JSON as `artifact_url`. log-workout finds the page by it.

**One session = one artifact = one workout.** A new session always gets a new page; never
publish a session over another session's page.

**Changing a session that's already published:**

1. First check for logged data: with the ArtifactData tool, list the page's `sets` collection
   (and `notes`) at the plan's `artifact_url`. Any row with a weight, reps, seconds or RIR
   filled in, or any note, counts as logged.
2. **Nothing logged:** edit the plan JSON, re-check it (step 6), re-render, and republish the
   HTML to the same `artifact_url`. The lifter keeps the same link.
3. **Something logged:** keep the logged sets exactly as they are and change only the rest,
   then republish to the same `artifact_url`. Set ids follow positions in the plan (exercise
   number, set number), so only edits that leave every position in place are safe:
   - **OK:** change kg, reps, RIR or label on unlogged sets; add sets to the end of an
     exercise; add exercises to the end of the session; remove unlogged sets or exercises
     from the end.
   - **Not OK:** insert, remove or reorder anything before a logged set or exercise, or
     change a logged set. It would attach saved sets to the wrong lift.

   If the change the lifter wants isn't in the OK list (say, swapping an exercise in the
   middle once later ones are logged), tell them plainly that the session has logged sets
   that would end up on the wrong lift, and ask how to go on (`AskUserQuestion`): e.g. put
   the new exercise at the end instead, or leave the session as it is.

## 8. Show it

A compact summary: exercises with working sets (kg × reps @ RIR), warm-ups as one line each,
the page link, and one or two sentences on what changed from last time and why. Don't
narrate the checklist. Mention only judgement calls the lifter should know about (an
assumed RIR, a held load after a grind).

For a week: plan each session the same way, and run `gym volume --plan` with all of them.
