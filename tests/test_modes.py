"""Progression mode per exercise — the shipped table's integrity, the lookup, the rules."""

import json
import re
from importlib.resources import files

import pytest

from gym_buddy.models.exercises import Exercise, categories, exercises_in
from gym_buddy.strength.modes import ModeTable, load_mode_table, progression_mode

MODES = {"load", "reps", "hold", "none"}
PATH = files("gym_buddy") / "data" / "progression-modes.json"
BLOCK = json.loads(PATH.read_text())
# the groups flattened to {"CATEGORY:NAME": {"mode", "why"}}
FLAT = {k: {"mode": g["mode"], "why": g["why"]} for g in BLOCK["overrides"] for k in g["exercises"]}
TABLE = load_mode_table()
ALL = [Exercise(c, n) for c in categories() for n in [None, *exercises_in(c)]]
CARDIO_LIKE = {"BIKE", "BIKE_OUTDOOR", "ELLIPTICAL", "FLOOR_CLIMB", "INDOOR_BIKE", "INDOOR_ROW",
               "LADDER", "RUN", "RUN_INDOOR", "STAIR_STEPPER", "CARDIO", "MOVE", "POSE",
               "WARM_UP", "BATTLE_ROPE", "SLEDGE_HAMMER", "PLYO", "TOTAL_BODY"}


def mode(category, name=None, **kw):
    return progression_mode(Exercise(category, name), **kw)


def _strings(node):
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for v in node.values():
            yield from _strings(v)
    elif isinstance(node, list):
        for v in node:
            yield from _strings(v)


class TestDataIntegrity:
    def test_every_catalog_category_has_an_entry_and_nothing_else(self):
        assert set(BLOCK["categories"]) == set(categories())
        assert len(categories()) == 51

    def test_override_keys_are_real_exercises(self):
        for key in FLAT:
            category, name = key.split(":", 1)
            assert name in exercises_in(category), key

    def test_prefixes_match_something_and_exceptions_are_categories(self):
        for rule in BLOCK["prefix_rules"]:
            assert any(n.startswith(rule["prefix"]) for c in categories()
                       for n in exercises_in(c)), rule["prefix"]
            assert set(rule["except_categories"]) <= set(categories())

    def test_every_entry_has_a_valid_mode_and_a_why(self):
        entries = [*BLOCK["categories"].values(), *BLOCK["prefix_rules"],
                   *FLAT.values()]
        for e in entries:
            assert e["mode"] in MODES, e
            assert e["why"].strip(), e
        assert set(BLOCK["modes"]) == MODES

    def test_no_exercise_is_in_two_groups(self):
        keys = [k for g in BLOCK["overrides"] for k in g["exercises"]]
        assert len(keys) == len(set(keys)) == len(FLAT)

    def test_a_duplicate_across_groups_raises_on_load(self):
        group = {"mode": "none", "why": "x", "exercises": ["PLANK:PLANK"]}
        with pytest.raises(ValueError, match="PLANK:PLANK"):
            ModeTable({"overrides": [group, {**group, "mode": "reps"}]})

    def test_no_group_is_empty_or_missing_its_reason(self):
        for g in BLOCK["overrides"]:
            assert g["exercises"] and g["why"].strip(), g
            assert g["mode"] in MODES

    def test_groups_are_sorted_for_stable_diffs(self):
        assert [g["exercises"] for g in BLOCK["overrides"]] == [
            sorted(g["exercises"]) for g in BLOCK["overrides"]]
        firsts = [(g["mode"], g["exercises"][0]) for g in BLOCK["overrides"]]
        assert firsts == sorted(firsts)

    def test_no_override_is_redundant(self):
        for key, entry in FLAT.items():
            category, name = key.split(":", 1)
            without = ModeTable({**BLOCK, "overrides": [
                {**g, "exercises": [k for k in g["exercises"] if k != key]}
                for g in BLOCK["overrides"]]})
            assert without.mode_for(Exercise(category, name)).mode != entry["mode"], key

    def test_the_block_carries_no_athlete_or_running_text(self):
        text = "\n".join(_strings(BLOCK)).lower()
        for banned in ("athlete", "strength-science", "hip-thrust", "ht200", "rc3", "watch"):
            assert banned not in text
        assert not re.search(r"\brun(s|ning|ner)?\b|hik(e|ing)", text)

    def test_reviewed_and_loaded_through_importlib_resources(self):
        assert TABLE.reviewed_on == BLOCK["_reviewed_on"] == "2026-10-17"
        assert "agent" not in str(PATH)

    def test_the_lunge_loads_are_written_out_not_computed(self):
        written = {k for k, v in FLAT.items()
                   if k.startswith("LUNGE:") and v["mode"] == "load"}
        named = {f"LUNGE:{n}" for n in exercises_in("LUNGE")
                 if "BARBELL" in n or "DUMBBELL" in n}
        assert len(named) == 37       # spec says 34; the catalog has 37 barbell/dumbbell lunge names, all written out
        assert named <= written


class TestLookup:
    def test_every_catalog_exercise_resolves(self):
        for ex in ALL:
            assert progression_mode(ex).mode in MODES, ex

    def test_most_specific_match_wins_and_is_reported(self):
        assert mode("HIP_STABILITY", "DEAD_BUG") == ("none", "category")
        assert mode("HIP_STABILITY", "STANDING_HIP_ABDUCTION") == ("load", "exercise")
        assert mode("PUSH_UP", "WEIGHTED_PUSH_UP") == ("load", "prefix")
        assert mode("PLANK") == ("hold", "category")

    def test_an_override_beats_the_prefix(self):
        # WEIGHTED_ prefix says load; this exact name is overridden
        rows = [(k, v) for k, v in FLAT.items()
                if k.split(":", 1)[1].startswith("WEIGHTED_") and v["mode"] != "load"]
        for key, entry in rows:
            assert progression_mode(Exercise(*key.split(":", 1))) == (entry["mode"], "exercise")

    def test_excepted_categories_get_the_category_default_for_weighted_names(self):
        for category in ("CARDIO", "PLYO", "TOTAL_BODY"):
            for name in exercises_in(category):
                if name.startswith("WEIGHTED_"):
                    assert progression_mode(Exercise(category, name)) == ("none", "category")

    def test_calf_raises(self):
        assert mode("CALF_RAISE", "STANDING_CALF_RAISE").mode == "reps"
        assert mode("CALF_RAISE", "WEIGHTED_STANDING_CALF_RAISE") == ("load", "prefix")

    def test_an_explicit_path_is_honoured(self, tmp_path):
        path = tmp_path / "m.json"
        path.write_text(json.dumps({"categories": {"SQUAT": {"mode": "hold"}}}))
        assert progression_mode(Exercise("SQUAT"), path=path).mode == "hold"

    def test_a_missing_category_raises_naming_it(self, tmp_path):
        path = tmp_path / "m.json"
        path.write_text(json.dumps({"categories": {}}))
        with pytest.raises(KeyError, match="SQUAT"):
            progression_mode(Exercise("SQUAT"), path=path)


class TestCatalogRules:
    def test_weighted_names_are_load_outside_conditioning(self):
        for ex in ALL:
            if ex.name and ex.name.startswith("WEIGHTED_") and ex.category not in {
                    "CARDIO", "PLYO", "TOTAL_BODY"}:
                assert progression_mode(ex).mode == "load", ex

    def test_cardio_conditioning_and_mobility_are_never_load(self):
        for ex in ALL:
            if ex.category in CARDIO_LIKE:
                assert progression_mode(ex).mode != "load", ex

    def test_every_barbell_or_dumbbell_lunge_is_load(self):
        for n in exercises_in("LUNGE"):
            if "BARBELL" in n or "DUMBBELL" in n:
                assert mode("LUNGE", n).mode == "load", n

    def test_twin_fixture_exactly_these_plain_names_are_load(self):
        """Of the plain names with a WEIGHTED_ twin (Garmin's bodyweight versions)."""
        twins = [ex for ex in ALL if ex.name
                 and f"WEIGHTED_{ex.name}" in exercises_in(ex.category)
                 and not ex.name.startswith("WEIGHTED_")]
        assert len(twins) == 370
        loads = {f"{ex.category}:{ex.name}" for ex in twins if progression_mode(ex).mode == "load"}
        assert loads == {
            "BENCH_PRESS:ONE_ARM_FLOOR_PRESS", "CALF_RAISE:SEATED_CALF_RAISE",
            "HIP_STABILITY:STANDING_ADDUCTION", "HIP_STABILITY:STANDING_HIP_ABDUCTION",
            "LEG_CURL:LEG_CURL", "ROW:ROW", "SQUAT:BACK_SQUATS", "SQUAT:SQUAT"}

    @pytest.mark.parametrize("category,name,expected", [
        ("HIP_STABILITY", "DEAD_BUG", "none"), ("TOTAL_BODY", "BURPEE", "none"),
        ("SUSPENSION", "INVERTED_ROW", "reps"), ("SUSPENSION", "PLANK", "hold"),
        ("HIP_STABILITY", "STANDING_HIP_ABDUCTION", "load"), ("LATERAL_RAISE", None, "load"),
        ("PLANK", None, "hold"), ("PUSH_UP", "WEIGHTED_PUSH_UP", "load"),
        ("SIT_UP", "THE_TEASER_WEIGHTED", "load"), ("CORE", "BARBELL_ROLLOUT", "reps"),
        ("PULL_UP", "LAT_PULLDOWN", "load"), ("PULL_UP", "BAND_ASSISTED_PULL_UP", "reps"),
        ("HIP_RAISE", "BARBELL_HIP_THRUST_WITH_BENCH", "load"), ("SQUAT", "LEG_PRESS", "load"),
        ("LUNGE", "LUNGE", "reps"), ("SQUAT", "STEP_UP", "reps"), ("PUSH_UP", None, "reps"),
        ("ROW", "INVERTED_ROW", "reps"), ("CALF_RAISE", "SEATED_CALF_RAISE", "load"),
    ])
    def test_pinned_cases(self, category, name, expected):
        assert mode(category, name).mode == expected

    def test_a_suspension_name_is_reps(self):
        names = [n for n in exercises_in("SUSPENSION") if n not in
                 {"PLANK", "SIDE_PLANK", "REVERSE_PLANK"} and not n.startswith("WEIGHTED_")
                 and f"SUSPENSION:{n}" not in FLAT]
        assert names and all(mode("SUSPENSION", n).mode == "reps" for n in names)


# Every catalog exercise, named and category-only (ALL). The approved totals quoted in the
# review (834/471/497/44) came to 1846 exercises; this enumeration has 1897.
SNAPSHOT_COUNTS = {"load": 852, "reps": 484, "none": 516, "hold": 45}
SNAPSHOT_SHA256 = "14e448c5f0c973703b3b2946e66b2252918554d7758c58058c22dc9fb1ec217e"


class TestSnapshot:
    def test_the_approved_table_is_unchanged(self):
        import hashlib
        from collections import Counter
        lines = sorted(f"{ex.category}:{ex.name or ''}={progression_mode(ex).mode}" for ex in ALL)
        counts = dict(Counter(line.rsplit("=", 1)[1] for line in lines))
        digest = hashlib.sha256("\n".join(lines).encode()).hexdigest()
        assert (counts, digest) == (SNAPSHOT_COUNTS, SNAPSHOT_SHA256), (
            "progression table changed: needs an evidence review and lifter "
            "approval; bump _reviewed_on and update this snapshot")
