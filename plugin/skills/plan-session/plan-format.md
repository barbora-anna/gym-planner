# Plan format: `sessions/<date>-<slug>.json`

`gym render` and `gym volume --plan` read this file, and validate it strictly: an unknown or
misspelled key is an error, so a typo can't silently drop a load.

```json
{
  "slug": "glutes-full-body",
  "date": "2026-10-24",
  "title": "Glutes & Full Body",
  "subtitle": "Working sets: aim for 2 reps left",
  "notes": "First working set tells you the day. 4+ reps left: hip thrust 140 kg for the rest. 0 left or reps missed: 125 kg. Otherwise keep the load.",
  "exercises": [
    {
      "exercise": "HIP_RAISE:BARBELL_HIP_THRUST_WITH_BENCH",
      "name": "Barbell hip thrust",
      "rest_s": 180,
      "notes": "Chin tucked, ribs down; pause one second at the top.",
      "sets": [
        {"role": "warmup", "weight_kg": 60, "reps": 8},
        {"role": "warmup", "weight_kg": 67.5, "reps": 5},
        {"role": "warmup", "weight_kg": 92.5, "reps": 3},
        {"role": "warmup", "weight_kg": 112.5, "reps": 2},
        {"role": "working", "weight_kg": 135, "reps": 5, "rir": 2},
        {"role": "working", "weight_kg": 135, "reps": 5, "rir": 2}
      ]
    },
    {
      "exercise": "PLANK",
      "sets": [{"role": "working", "seconds": 45}]
    }
  ]
}
```

| Field | Notes |
|---|---|
| `slug`, `date` | The session id is derived: `ps-<date>-<slug>`. Lowercase words with hyphens. |
| `title`, `subtitle` | Shown at the top of the page. |
| `notes` | The rules box at the top: the readiness rule, anything that applies to the whole session. |
| `exercise` | Exact `CATEGORY:NAME` from `gym find`. |
| `name` | Display name. Optional, defaults to a readable version of the catalog name. |
| `rest_s` | Rest after a working set, in seconds. Printed in the exercise header on the session page (default 120). |
| `notes` (exercise) | One line under the exercise name. |
| `role` | `warmup` or `working`. Required. |
| `reps` or `seconds` | Exactly one. |
| `weight_kg` | Optional (bodyweight, holds). Follows the load conventions in `loads.md`. |
| `rir` | Target RIR. Every working rep set has one (not needed on timed holds). Use 1.5 for "1–2". |
| `label` | Optional text shown instead of the reps (`"3–4"`), or `"optional"` to mark a set as skippable. |
| `artifact_url` | Added after publishing. |

`gym render` gives each set a stable id (`<session id>-e<exercise>s<set>`), which the page's
saved rows carry. Don't reorder or remove exercises in a plan after it's been published and
logged against. Plan a new session instead.
