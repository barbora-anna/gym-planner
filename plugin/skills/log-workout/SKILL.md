---
name: log-workout
description: Get a finished workout into the log, from the session page (and Strava if the lifter uses it), clarifying anything missing with the lifter, then give a short read on how it went. Use for "I trained", "logged it", "how did it go", or when a planned session's results aren't in the log yet.
---

# Log a workout

The log is what every later plan trusts. Transcribe with `gym`, ask about gaps, and save
only what really happened.

Read first: `../../knowledge/loads.md` (RIR) and `../../knowledge/progression.md` (paths
relative to this skill's folder).

## 1. Find what to log

- `gym log show --last 3`, and the plans in `sessions/`. The candidate is the most recent
  planned session with an `artifact_url` and no logged workout.
- If it's unclear which session they trained (a different day, a swapped session), ask.
  Never link a workout to a plan on a guess.

## 2. From the session page

1. With the ArtifactData tool, list the `sets` collection of the page at the plan's
   `artifact_url`, and the `notes` collection. (If the tool isn't loaded, load it first.)
2. Save each result **verbatim** to `imports/<session id>-sets.json` and
   `imports/<session id>-notes.json`.
3. Run `gym log from-artifact imports/<id>-sets.json sessions/<plan>.json --notes
   imports/<id>-notes.json -o drafts/<date>-<slug>.json`. It orders the sets by the plan,
   keeps only sets marked done, and lists the BLANKS.

## 3. From Strava (only if the lifter uses it)

- Find the activity for that date (`list_activities`), then
  `get_strength_workout_details`. Save the result verbatim to `imports/strava-<activity id>.json`.
- **With a page draft:** Strava only fills blanks the page left (a kg or reps the lifter
  didn't type). It never overrides the page, and never supplies RIR or role. If the two
  disagree on a set, ask which is right. Then set `"source": "artifact+strava"`.
- **Strava only** (no page): write the draft yourself in the workout format below.
  - Map each Strava exercise name to an exact catalog identity. Check the profile's
    "Strava names" section first, then `gym find`. If more than one candidate fits, ask the
    lifter, then add the mapping to the profile.
  - Strava writes 0 kg for an unlogged weight. On a loaded lift that's a blank, not 0.
  - Strava has no RIR and no warm-up/working split: ask for both.

## 4. Clarify, in one round

Show a compact summary of the draft, then ask. Missing RIRs and unknown roles have fixed
answers, so use `AskUserQuestion`: one question per set, up to 4 per call (e.g. "Hip thrust
set 3, 135×5: reps left?" with options 0 / 1 / 2 / 3, and "Other" for more). Open items
(a missing kg, a note to explain) go in a short chat message.

What to cover:
- **RIR for each working set without one.** This matters most: without it, the next plan's
  loads are floors. Accept "about 2" or "2–3" (take the lower number and say so). RIR
  remembered after the session is less reliable: add "RIR recalled <date>" to that
  exercise's `note`.
- Missing kg or reps, sets with an unknown role, anything that looks like a typo (a load
  far off last time's).
- Anything the notes raise ("machine maxed out", "knee twinged").

Fill the answers into the draft. Don't invent values. If they don't remember, leave the
field out.

## 5. Save

`gym log save drafts/<file>.json`.
- `SAVED`: done. It lists any BLANKS left. Fine if the lifter truly doesn't know.
- If the workout is already stored, it prints the field-by-field diff and doesn't save.
  Show the diff to the lifter, and re-run with `--confirm` only on their yes.
- An ERROR names the bad field: fix the draft, never the database.
- To correct a stored workout later: `gym log show <id> --json` gives the stored JSON
  (inside a list: take the one object). Edit a copy in `drafts/`, then save it the same way.

## 6. A short read

Three to five lines, not a report:
- Per main lift, vs last time (`gym lift <exercise>`): load and reps up, held, or down.
  Mention the e1RM range only if it moved meaningfully.
- What it means for next time, by `progression.md` (load first or double progression: add
  load / add a rep / hold).
- The week so far, from `gym volume`, only if something stands out.
- Health: if they mentioned pain, record it in the profile and say how you'll plan around it.

## Workout format (`drafts/<date>-<slug>.json`)

```json
{
  "id": "2026-10-24-glutes-full-body",
  "date": "2026-10-24",
  "session": "ps-2026-10-24-glutes-full-body",
  "source": "artifact",
  "note": "Gym was packed, rests ran long.",
  "exercises": [
    {"exercise": "HIP_RAISE:BARBELL_HIP_THRUST_WITH_BENCH", "note": "felt strong",
     "sets": [
       {"role": "warmup", "weight_kg": 60, "reps": 5},
       {"role": "working", "weight_kg": 135, "reps": 6, "rir": 2}]},
    {"exercise": "PLANK", "sets": [{"role": "working", "seconds": 50}]}
  ]
}
```

- `id`: lowercase words with hyphens, usually `<date>-<slug>`. `session`: the plan's id, or
  leave it out for an unplanned workout.
- Per set: `role`, `weight_kg`, `reps` *or* `seconds`, `rir` (reported, never the target).
  `reps: 0` = a missed attempt. Leave out anything unknown.
