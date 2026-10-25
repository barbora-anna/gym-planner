"""`gym render <plan.json>`: the session page, ready to publish with the Artifact tool.

The page logs each set to its own artifact database (collection `sets`, one row per set,
keyed by `PlannedSession.set_id`; extra sets get a random id) and per-exercise notes to
`notes`. `gym log from-artifact` reads those rows back.
"""

from __future__ import annotations

import html
import json
from importlib.resources import files
from pathlib import Path

from ..models.session import PlannedSession
from ._common import read_json, validated

TEMPLATE = files("gym_buddy") / "templates" / "session.html"


def register(sub) -> None:
    p = sub.add_parser("render", help="plan JSON → session page HTML")
    p.add_argument("plan")
    p.add_argument("-o", "--out", help="default: the plan's path with .html")
    p.set_defaults(func=_render)


def page_data(plan: PlannedSession) -> dict:
    return {
        "session": plan.id,
        "title": plan.title,
        "subtitle": plan.subtitle,
        "dateLabel": plan.date.strftime("%A %-d %B"),
        "notes": plan.notes,
        "exercises": [{
            "ex": ex.exercise.key,
            "name": ex.display_name,
            "rest": ex.rest_s or 120,
            "tip": ex.notes,
            "sets": [{"id": plan.set_id(i, j), "role": s.role, "kg": s.weight_kg,
                      "reps": s.reps, "seconds": s.seconds, "rir": s.rir, "label": s.label}
                     for j, s in enumerate(ex.sets)],
        } for i, ex in enumerate(plan.exercises)],
    }


def render(plan: PlannedSession) -> str:
    data = json.dumps(page_data(plan), ensure_ascii=False).replace("</", "<\\/")
    return (TEMPLATE.read_text()
            .replace("__TITLE__", html.escape(plan.title))
            .replace("/*__DATA__*/null", data))


def _render(args) -> int:
    plan = validated(PlannedSession, read_json(args.plan), args.plan)
    out = Path(args.out) if args.out else Path(args.plan).with_suffix(".html")
    out.write_text(render(plan))
    print(f"WROTE  {out}")
    print("Publish it with the Artifact tool, capabilities {\"db\": {}, \"user\": {}}.")
    return 0
