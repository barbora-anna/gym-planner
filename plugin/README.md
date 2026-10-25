# gym-planner Coach plugin

A strength coach that plans your sessions, logs what you did, and progresses you from your
own numbers. The coaching is Claude's. The arithmetic and the log are the `gym` CLI.

## Setup

```bash
uv tool install git+https://github.com/barbora-anna/gym-planner
gym init
cd ~/training && claude
```

1. Installs the `gym` CLI ([uv](https://docs.astral.sh/uv/) fetches the Python it needs).
2. Makes your data home, `~/training` (set `GYM_BUDDY_HOME` first to put it elsewhere), with
   the Claude Code settings that turn the Coach on there and only there. An existing
   settings file is never overwritten.
3. Starts the Coach. Trust the folder when asked, and the plugin installs itself.

Strava is optional: connect it in Claude and the Coach reads your history from it.

**Working on the plugin itself:** launch with `claude --plugin-dir <repo>/plugin` from the
data home to use your working copy instead of the published one.

## What's inside

- `agents/coach.md`: the persona and the rules it always follows.
- `skills/onboard`, `skills/log-workout`, `skills/plan-session` (with `checklist.md` and
  `plan-format.md`).
- `knowledge/`: the evidence the Coach plans from.
