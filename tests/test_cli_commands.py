"""The `gym` subcommands end to end, against a tmp data home (conftest sets GYM_BUDDY_HOME)."""

import json

import pytest

SID = "ps-2026-10-24-glutes"
PLAN = {"slug": "glutes", "date": "2026-10-24", "title": "Glutes </script> & Co", "notes": "Easy day.",
        "exercises": [
            {"exercise": "HIP_RAISE:BARBELL_HIP_THRUST_WITH_BENCH", "rest_s": 180, "sets": [
                {"role": "warmup", "weight_kg": 60, "reps": 5},
                {"role": "working", "weight_kg": 135, "reps": 5, "rir": 2},
                {"role": "working", "weight_kg": 135, "reps": 5, "rir": 2}]},
            {"exercise": "PLANK", "sets": [{"role": "working", "seconds": 45}]}]}


def row(set_id, **data):
    return {"id": set_id or "extra", "data": {"session": SID, "planned_set_id": set_id, "status": "done", **data}}


ROWS = [
    row(f"{SID}-e1s3", exercise="HIP_RAISE:BARBELL_HIP_THRUST_WITH_BENCH", role="working", weight_kg=135, reps=5, rir=None),
    row(None, exercise="HIP_RAISE:BARBELL_HIP_THRUST_WITH_BENCH", role="working", weight_kg=135, reps=4, rir=1),
    row(f"{SID}-e1s1", exercise="HIP_RAISE:BARBELL_HIP_THRUST_WITH_BENCH", role="warmup", weight_kg=60, reps=5),
    row(f"{SID}-e1s2", exercise="HIP_RAISE:BARBELL_HIP_THRUST_WITH_BENCH", role="working", weight_kg=135, reps=6, rir=2),
    row(f"{SID}-e2s1", exercise="PLANK", role="working", seconds=50),
    {"id": "other", "data": {"session": "ps-2026-10-01-x", "status": "done", "exercise": "SQUAT", "reps": 5}},
    {"id": "p", "data": {"session": SID, "planned_set_id": f"{SID}-e1s1", "status": "pending",
                         "exercise": "HIP_RAISE:BARBELL_HIP_THRUST_WITH_BENCH"}},
]


@pytest.fixture
def files(tmp_path):
    (tmp_path / "plan.json").write_text(json.dumps(PLAN))
    (tmp_path / "rows.json").write_text(json.dumps(ROWS))
    return tmp_path


@pytest.fixture
def logged(gym, files):
    gym("log", "from-artifact", files / "rows.json", files / "plan.json", "-o", files / "w.json")
    gym("log", "save", files / "w.json")
    return files / "w.json"


class TestFromArtifact:
    def test_orders_by_plan_puts_extras_last_and_keeps_only_done_rows(self, gym, files):
        code, out = gym("log", "from-artifact", files / "rows.json", files / "plan.json")
        assert code == 0
        w = json.loads(out)
        assert w["id"] == "2026-10-24-glutes" and w["session"] == SID and w["source"] == "artifact"
        thrust = w["exercises"][0]["sets"]
        assert [(s["role"], s["reps"]) for s in thrust] == [("warmup", 5), ("working", 6), ("working", 5), ("working", 4)]
        assert w["exercises"][1] == {"exercise": "PLANK", "sets": [{"role": "working", "seconds": 50}]}

    def test_lists_blanks_but_not_rir_on_timed_sets(self, gym, files):
        _, out = gym("log", "from-artifact", files / "rows.json", files / "plan.json", "-o", files / "w.json")
        assert "BARBELL_HIP_THRUST_WITH_BENCH set 3: no RIR" in out
        assert "PLANK" not in out

    def test_notes_are_attached_to_their_exercise(self, gym, files):
        (files / "notes.json").write_text(json.dumps([{"id": "n", "data": {
            "session": SID, "exercise": "PLANK", "note": "shaky"}}]))
        _, out = gym("log", "from-artifact", files / "rows.json", files / "plan.json", "--notes", files / "notes.json")
        assert json.loads(out)["exercises"][1]["note"] == "shaky"

    def test_nothing_done_is_an_error(self, gym, files):
        (files / "rows.json").write_text(json.dumps([ROWS[-1]]))
        code, out = gym("log", "from-artifact", files / "rows.json", files / "plan.json")
        assert code == 1 and "no set is marked done" in out


class TestSave:
    def test_save_then_unchanged(self, gym, logged):
        code, out = gym("log", "save", logged)
        assert (code, out.strip()) == (0, "UNCHANGED  2026-10-24-glutes")

    def test_overwrite_needs_confirm_and_shows_the_diff(self, gym, logged):
        w = json.loads(logged.read_text())
        w["exercises"][0]["sets"][2]["rir"] = 1
        logged.write_text(json.dumps(w))
        code, out = gym("log", "save", logged)
        assert code == 2 and "set 3 rir: None → 1.0" in out and "NOT SAVED" in out
        code, out = gym("log", "save", logged, "--confirm")
        assert code == 0 and "SAVED" in out
        assert gym("log", "save", logged)[1].startswith("UNCHANGED")

    def test_an_invalid_file_is_one_readable_error(self, gym, tmp_path):
        (tmp_path / "bad.json").write_text(json.dumps({"id": "x", "date": "2026-10-24", "exercises": [
            {"exercise": "SQUAT:MOON_SQUAT", "sets": [{"reps": 5}]}]}))
        code, out = gym("log", "save", tmp_path / "bad.json")
        assert code == 1 and out.startswith("ERROR") and "MOON_SQUAT" in out

    def test_show_and_rm(self, gym, logged):
        assert "135 kg × 6 @ RIR 2" in gym("log", "show")[1]
        assert json.loads(gym("log", "show", "2026-10-24-glutes", "--json")[1])[0]["id"] == "2026-10-24-glutes"
        assert gym("log", "rm", "2026-10-24-glutes")[0] == 2
        assert gym("log", "rm", "2026-10-24-glutes", "--confirm")[0] == 0
        assert "No workouts" in gym("log", "show")[1]


class TestLiftAndFind:
    def test_lift_shows_e1rm_and_marks_floors(self, gym, logged):
        code, out = gym("lift", "hip thrust")
        assert code == 0 and "(mode: load)" in out
        assert "135 kg × 5 @ RIR ?   e1RM ≥" in out and "a floor" in out
        assert "60 kg × 5" in out and "60 kg × 5   e1RM" not in out      # no e1RM on warm-ups

    def test_an_ambiguous_lift_lists_candidates(self, gym):
        code, out = gym("lift", "squat")
        assert code == 1 and "ambiguous" in out and "more" in out

    def test_find_by_words_and_by_muscle(self, gym, logged):
        out = gym("find", "hip thrust")[1]
        assert "HIP_RAISE:BARBELL_HIP_THRUST_WITH_BENCH  (load; glute_max; last done 2026-10-24)" in out
        out = gym("find", "--muscle", "glute_max")[1]
        assert "1    HIP_RAISE  (last done 2026-10-24)" in out
        assert gym("find", "--muscle", "booty")[0] == 1


class TestCalc:
    def test_e1rm_is_a_range_and_a_floor_without_rir(self, gym):
        assert gym("calc", "e1rm", "135x5@2")[1].strip() == "e1RM from 135×5 @2: 162.0–166.5 kg"
        assert "a floor" in gym("calc", "e1rm", "100x5")[1]

    def test_load_rounds_down_to_the_step(self, gym):
        out = gym("calc", "load", "8", "--rir", "2", "--from", "135x5@2", "--step", "2.5")[1]
        assert "121.5–124.9 kg" in out and "at 2.5 kg steps: 120 kg (up to 122.5 kg)" in out

    def test_load_from_an_e1rm(self, gym):
        assert "5 reps @ RIR 2: 129.7–133.3 kg" in gym("calc", "load", "5", "--rir", "2", "--e1rm", "160")[1]

    def test_rir_flags_an_impossible_set(self, gym):
        out = gym("calc", "rir", "150x8", "--e1rm", "160")[1]
        assert "beyond failure" in out and " to " in out

    def test_pct_rounds_down_and_respects_the_bar(self, gym):
        out = gym("calc", "pct", "40", "30", "75", "--step", "2.5", "--min", "20")[1]
        assert "30%  20 kg" in out and "75%  30 kg" in out

    def test_a_bad_set_is_an_error(self, gym):
        assert gym("calc", "e1rm", "135x")[0] == 1


class TestVolumeAndRender:
    def test_volume_counts_the_log_and_skips_a_logged_plan(self, gym, logged, files):
        code, out = gym("volume", "--to", "2026-10-25", "--plan", files / "plan.json")
        assert code == 0 and "already logged" in out
        assert "Hard sets: 2 (+1 working sets with no RIR, not judged)" in out

    def test_volume_adds_an_unlogged_plan(self, gym, files):
        out = gym("volume", "--to", "2026-10-25", "--plan", files / "plan.json")[1]
        assert "+ 1 planned session(s)" in out and "Hard sets: 2" in out

    def test_render_embeds_the_plan_safely(self, gym, files):
        code, _ = gym("render", files / "plan.json")
        html = (files / "plan.html").read_text()
        assert code == 0
        assert "<title>Glutes &lt;/script&gt; &amp; Co</title>" in html
        assert "</script> & Co" not in html.split("const DATA = ")[1].split(";\n")[0]
        data = json.loads(html.split("const DATA = ")[1].split(";\n")[0].replace("<\\/", "</"))
        assert data["exercises"][0]["sets"][1]["id"] == f"{SID}-e1s2"
        assert data["exercises"][0]["rest"] == 180 and data["exercises"][1]["rest"] == 120
