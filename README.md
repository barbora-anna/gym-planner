# gym-planner

A strength coach for Claude Code. Two parts, one repo:

- **The Coach** — a Claude Code plugin (`plugin/`) that gets to know you, plans each
  session and publishes it as a page you log your sets on at the gym, then reads your
  results back (plus Strava, if you use it) and progresses you. It runs from your training
  data home (`$GYM_BUDDY_HOME`, default `~/training`), never from this repo. Setup:
  `plugin/README.md`.
- **The `gym` CLI** — the Python package (`src/gym_buddy/`) behind it: the workout log,
  e1RM / RIR / load calculations, lift history, hard sets per muscle, the exercise catalog
  and the session page renderer. The Coach decides; `gym` does the arithmetic, so no number
  is worked out by hand.

Strength only. Status: early.

## Development

```
uv sync
uv run pytest        # fully offline
```

## License

MIT — see `LICENSE`.
