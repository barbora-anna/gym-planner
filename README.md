# gym-planner

A strength coach for Claude Code. It gets to know you, plans each session and publishes it
as a page you log your sets on at the gym, then reads your results back (plus Strava, if
you use it) and progresses you from your own numbers.

Strength only. Status: early.

## Quick start

You need [Claude Code](https://claude.com/claude-code) and [uv](https://docs.astral.sh/uv/).

```bash
uv tool install git+https://github.com/barbora-anna/gym-planner
gym init
cd ~/training && claude
```

What each step does, and how to connect Strava: [`plugin/README.md`](plugin/README.md).

## How to read your session page

Each session is a page you open on your phone at the gym: a training diary with the plan
already written in.

- **The top** has the session's title, a short aim (e.g. "Working sets: aim for 2 reps
  left"), progress through the working sets, and a box with the session's rules, such as
  how to adjust the load if the first set feels easy or hard.
- **Each exercise** has its name, the rest to take between working sets, and sometimes a
  one-line cue. Below that is one line per set.
- **On each set line,** the left side is the plan and the right side is where you write
  what you did:
  - `W` marks a warm-up; `1`, `2`, `3` number the working sets.
  - `135 × 5` means 135 kg for 5 reps. `14 × 8–10` means anywhere from 8 to 10 reps.
    `45 s` is a timed hold.
  - `@2` is the target **RIR (reps in reserve)**: finish the set with about 2 more reps
    you could have done. `@1–2` means 1 to 2. Warm-ups have no RIR target.
  - `optional` means do the set if you feel up to it.
- **Write down kg, reps (or seconds) and RIR** for each set you do. The faint numbers in
  empty fields are the targets. Tap a plan to copy it in when you did exactly that. A line
  with reps filled in counts as logged and turns cyan. Leave lines empty for sets you
  didn't do.
- **"+ Add a set"** logs a set that wasn't planned. The note under each exercise is for
  anything worth remembering ("machine maxes out at 80", "left knee felt off"). The Coach
  reads these too.

Everything saves as you type. Afterwards, tell the Coach you're done: it reads the page
back into your log and plans what's next from it.

## Built on evidence, not guesses

- **Every training rule cites its research.** Loads, progression, volume, session design
  and recovery are written down in [`plugin/knowledge/`](plugin/knowledge/), with full
  references in [`sources.md`](plugin/knowledge/sources.md). Where no study exists, the
  text says so plainly and treats the rule as a default your own log can override.
- **Numbers come from code, not from the model.** e1RM, reps in reserve, loads, plate
  rounding and hard-set counts are computed by `gym` from your logged sets, and estimates
  are shown as ranges. The Coach makes the decisions, but it never does the arithmetic in
  its head.
- **No guessing about your data.** If an exercise name is ambiguous, the Coach lists the
  candidates and asks you instead of picking one. Logged workouts are never overwritten
  silently: you see a diff and confirm.

## Two parts, one repo

- **The Coach** — a Claude Code plugin (`plugin/`): the persona, its skills (onboard, plan
  a session, log a workout) and the evidence base it plans from. It runs from your training
  data home (`$GYM_BUDDY_HOME`, default `~/training`), never from this repo.
- **The `gym` CLI** — the Python package behind it (`src/gym_buddy/`). The Coach decides;
  `gym` does the arithmetic and keeps the log, so no number is worked out by hand.

| Command | What it does |
|---|---|
| `gym init` | Set up the data home for the Coach |
| `gym log` | Store and read finished workouts (transcribes the session page) |
| `gym lift` | One lift's history with e1RM estimates |
| `gym find` | Search the exercise catalog |
| `gym calc` | e1RM, implied RIR, loads for a target RIR, percentages |
| `gym volume` | Hard sets per muscle (default: the last 7 days) |
| `gym render` | Plan JSON → session page HTML |

The package is named `gym-buddy` (hence `gym_buddy` and `GYM_BUDDY_HOME`); the product is
gym-planner.

## Development

```bash
uv sync
uv run pytest        # fully offline; never touches a real data home
```

To try your working copy of the plugin, launch it from the data home:

```bash
cd ~/training && claude --plugin-dir <repo>/plugin
```

## License

MIT — see `LICENSE`.
