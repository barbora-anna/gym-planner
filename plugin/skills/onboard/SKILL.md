---
name: onboard
description: Get to know a new lifter (or update what changed) and write their profile; optionally bring in recent strength history from Strava. Use on first run when athlete/profile.md doesn't exist, or for "update my weight", "new gym", "I tweaked my knee", "change my split".
---

# Onboard the lifter

Read first: `../../knowledge/session-design.md` (splits) and `../../knowledge/loads.md`
(equipment and load conventions), paths relative to this skill's folder.

## 1. Strava first

Before anything else, ask one question (`AskUserQuestion`): do they log workouts on Strava?
If yes, a lot of the interview can be read instead of asked.

## 2. Read what Strava knows (Strava users only)

- `get_athlete_profile`: name, sex, weight, and their preferred units.
- `list_activities` for the last ~8 weeks, then `get_strength_workout_details` for each
  strength session. From these, work out:
  - **schedule**: strength sessions per week, and typical session length;
  - **training history**: how far back regular strength sessions go (a hint for level, not
    the answer: ask how long they've trained overall);
  - **their exercises**: what they do often (likes), and the names to map to the catalog;
  - **recent loads**: the latest sets per main lift (no RIR: Strava never records it);
  - **equipment hints**: dumbbell weights and load steps they've used.
- Glance at other activity (runs, rides) as recovery context only.

Then show a short summary of what you found ("Looks like you lift 3× a week, about 60 min,
mostly hip thrust, RDL, bench…") and let them confirm or correct it. Never treat a guess
from the data as fact: anything you inferred gets confirmed.

## 3. Ask only what's still missing

Skip what you already know from Strava or earlier answers. A range stays a range; unknown
stays unknown. Ask in rounds, not all at once:

1. **Clickable** (`AskUserQuestion`, one call) for anything with fixed answers that's still
   open: how long they've trained consistently (never / under 6 months / 6 months–2 years /
   longer), days per week, session length, where they train.
2. **Then chat**, at most ~3 open questions per message: name and body stats (whatever
   Strava didn't give); goals in their words; equipment (bars and their weights first:
   Strava can't tell you those); health; likes and dislikes; RIR on the recent Strava sets
   ("your last bench was 40×5: how many reps were left?"). If RIR is new to them, explain it
   in one line first (step 6) rather than leaving them to guess what you mean. Without Strava, ask for recent
   sets they're sure of instead. Use `AskUserQuestion` whenever a question has fixed answers
   (a split to agree on).

What to cover:

- **Basics:** name or nickname, age, sex, height, bodyweight.
- **Level:** how long they've trained consistently, and what. Classify with ACSM 2009's
  definitions (`progression.md` → "By lifter level"): novice = no resistance training, or
  none for several years; intermediate ≈ 6 months of consistent training; advanced = years.
  Say which you chose and why.
- **Goals:** in their words (bigger glutes, first bodyweight bench, feel strong). Any target
  lift or date.
- **Schedule:** days per week, session length. Agree a split from `session-design.md`:
  suggest one, with the reason.
- **Equipment:** where they train, which barbells and **what each weighs** (don't assume
  20 kg: women's, technique and fixed bars differ), smallest plates, dumbbell range and
  steps, machines they use and their quirks (stack steps, pulley ratio, sled). Remind them of
  the load conventions (dumbbells per hand, plate-loaded machines count plates only).
- **Preferences:** lifts they love or hate, exercises they want to learn.
- **Health:** current pain or injuries, what aggravates them, anything a doctor said.
  Record, don't diagnose.
- **Recent numbers:** for their main lifts, a recent set they're confident in (kg × reps,
  and roughly how many reps they had left).

## 4. Write `athlete/profile.md`

Show the draft and write it on their yes. Use these sections so the other skills find
things:

```markdown
# <Name>

## Basics
## Level
## Goals
## Schedule and split
## Equipment
- Bars: 20 kg Olympic; fixed 30 / 40 kg
- Plates: smallest 1.25 kg (so 2.5 kg jumps on a barbell)
- Dumbbells: 2–30 kg in 2 kg steps
- Machines: leg press (plates only, sled not counted); cable stack 2.5 kg steps
## Preferences
## Health
## Strava
- Uses Strava: yes/no
### Strava names
- "Hip Thrust" → HIP_RAISE:BARBELL_HIP_THRUST_WITH_BENCH
## Notes
```

On later updates, change only what changed, show the edit, and write it on their yes. Date
health entries.

## 5. Recent history

- **With Strava:** log the strength sessions you read in step 2 (the last ~4 weeks is
  enough), each with the log-workout skill's Strava path: map names (ask when ambiguous, record the mapping),
  ask about warm-ups and RIR where they remember, and save each with `gym log save`. Old
  sets without RIR are fine: they're floors, and `gym` marks them.
- **Without Strava, but with specific recent sets they're sure of:** log them as one
  workout per approximate date (`"source": "told"`), with RIR if they know it.
- **Only vague numbers** ("I benched about 50 once"): don't log them. A logged set becomes
  an anchor for loads, and a fuzzy or old number must not set the first plans. Put it in
  the profile's Notes. Their first sessions are planned conservatively (RIR 3) and become
  the real anchors.

## 6. Teach the logging basics

Before the first session, make sure they know what to write on the session page and why it
matters. Keep it short and in plain words, then check RIR with one example; don't lecture.

- **kg:** the load as the profile's conventions count it (dumbbells per hand, plate-loaded
  machines plates only).
- **Reps (or seconds):** what they actually did, not what was planned. A missed rep is
  information, not a failure.
- **RIR, reps in reserve:** how many more good reps they could have done when they stopped.
  0 = couldn't do another. An honest estimate is enough: reported RIR is treated as ±1
  (`loads.md` → "RIR"). Write it right after the set: RIR recalled the next day
  has never been tested, while RIR given at the set has. Warm-ups need no RIR.
- **Why RIR matters:** loads are worked out from it. A set without RIR counts as a set to
  failure (a floor, `loads.md`), so next time's load comes out more cautious than it needs
  to be.
- **Notes:** anything a number can't hold: equipment facts ("machine maxes out at 80"),
  pain, a bad night's sleep.

Then check understanding with one quick question (`AskUserQuestion`), for example: "You
planned 8 reps, did 8, and could have squeezed out 2 more. What's the RIR?" (2). If they
miss it, explain once more with their own lift.

## 7. Hand over

One short paragraph: what you understood, the agreed split, and what's next (usually
"want me to plan your first session?").
