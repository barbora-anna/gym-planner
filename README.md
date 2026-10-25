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
