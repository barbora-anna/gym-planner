"""Exercise -> muscle attribution — including the three errors that motivated it."""

import json
import re
from importlib.resources import files

import pytest

from gym_buddy.models.exercises import Exercise, categories, exercises_in
from gym_buddy.strength.muscles import (
    DEFAULT_MAP_PATH,
    MuscleMap,
    contributions_for,
    load_muscle_map,
)

MAP = load_muscle_map()


def _string_values(node):
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for v in node.values():
            yield from _string_values(v)
    elif isinstance(node, list):
        for v in node:
            yield from _string_values(v)


class TestTheRC3Errors:
    """Three attribution mistakes made by hand, now arithmetic. See evidence_notes."""

    def test_back_squat_counts_toward_glute_max(self):
        """Plotkin 2023: equivalent glute hypertrophy to hip thrust by MRI, untrained."""
        c = contributions_for(Exercise("SQUAT", "BARBELL_BACK_SQUAT"))
        assert c.credit("glute_max") == 1.0

    def test_hip_abduction_is_glute_med_not_glute_max(self):
        c = contributions_for(Exercise("HIP_STABILITY", "WEIGHTED_STANDING_HIP_ABDUCTION"))
        assert c.credit("glute_med") == 1.0
        assert c.credit("glute_max") == 0.0
        assert c.is_mapped                       # a real zero, not an unknown

    def test_an_unmapped_exercise_is_distinguishable_from_a_real_zero(self):
        """The third error: a zero contribution that was never scored, only argued about."""
        unmapped = contributions_for(Exercise("BANDED_EXERCISES", "LEG_ABDUCTION"))
        assert not unmapped.is_mapped
        assert unmapped.matched is None
        assert unmapped.credit("glute_max") == 0.0   # same number, different meaning


class TestLookupPrecedence:
    def test_name_entry_beats_category_default(self):
        """Leg press is filed under SQUAT but is not a back squat."""
        squat = contributions_for(Exercise("SQUAT", "BARBELL_BACK_SQUAT"))
        press = contributions_for(Exercise("SQUAT", "LEG_PRESS"))
        assert press.matched == "exercise"
        assert squat.matched == "category"
        assert press.credit("glute_max") < squat.credit("glute_max")

    def test_good_morning_is_a_hinge_despite_its_category(self):
        """Garmin files good mornings under LEG_CURL. They train the whole posterior chain."""
        curl = contributions_for(Exercise("LEG_CURL", "WEIGHTED_LEG_CURL"))
        gm = contributions_for(Exercise("LEG_CURL", "GOOD_MORNING"))
        assert curl.credit("glute_max") == 0.0
        assert gm.credit("glute_max") > 0
        assert gm.credit("erectors") > 0

    def test_category_only_exercise_resolves_to_its_default(self):
        assert contributions_for(Exercise("BENCH_PRESS")).matched == "category"

    def test_callers_get_a_copy_not_the_table(self):
        c = contributions_for(Exercise("SQUAT"))
        c.muscles["glute_max"] = 0.0
        assert contributions_for(Exercise("SQUAT")).credit("glute_max") == 1.0


class TestMapIntegrity:
    """The map is hand-authored data — these guard it against rot."""

    def test_every_key_exists_in_the_garmin_catalog(self):
        """A typo would silently never match, under-counting volume forever."""
        data = json.loads(DEFAULT_MAP_PATH.read_text())
        for category in data["categories"]:
            assert category in categories(), category
        for key in data["exercises"]:
            category, name = key.split(":", 1)
            assert category in categories(), key
            assert name in exercises_in(category), key

    def test_every_muscle_is_in_the_vocabulary(self):
        data = json.loads(DEFAULT_MAP_PATH.read_text())
        vocabulary = set(data["vocabulary"])
        for table in ("categories", "exercises"):
            for key, muscles in data[table].items():
                assert set(muscles) <= vocabulary, key

    def test_contributions_are_fractional_set_credit(self):
        data = json.loads(DEFAULT_MAP_PATH.read_text())
        for table in ("categories", "exercises"):
            for key, muscles in data[table].items():
                for muscle, value in muscles.items():
                    assert 0 < value <= 1.0, f"{key}:{muscle}={value}"

    def test_loads_through_importlib_resources(self):
        resource = files("gym_buddy") / "data" / "exercise-map.json"
        assert json.loads(resource.read_text()) == json.loads(DEFAULT_MAP_PATH.read_text())
        assert "agent" not in str(DEFAULT_MAP_PATH)

    def test_no_athlete_specific_text(self):
        # string VALUES only: the progression block's keys are catalog names (RUN, RUN_INDOOR)
        text = "\n".join(_string_values(json.loads(DEFAULT_MAP_PATH.read_text()))).lower()
        for banned in ("athlete", "strength-science", "hip-thrust", "ht200", "rc3", "watch"):
            assert banned not in text
        assert not re.search(r"\brun(s|ning|ner)?\b|hik(e|ing)", text)

    def test_the_map_carries_a_review_date(self):
        assert MAP.reviewed_on is not None


class TestGenerality:
    """Coverage is by movement pattern, not by the current campaign's lifts."""

    @pytest.mark.parametrize("pattern,category", [
        ("squat", "SQUAT"), ("hinge", "DEADLIFT"), ("horizontal push", "BENCH_PRESS"),
        ("vertical push", "SHOULDER_PRESS"), ("horizontal pull", "ROW"),
        ("vertical pull", "PULL_UP"), ("single leg", "LUNGE"), ("calf", "CALF_RAISE"),
        ("core", "PLANK"), ("biceps", "CURL"), ("triceps", "TRICEPS_EXTENSION"),
        ("hip hinge dynamic", "HIP_SWING"), ("hip stability", "HIP_STABILITY"),
    ])
    def test_every_movement_pattern_is_scorable(self, pattern, category):
        assert contributions_for(Exercise(category)).is_mapped, pattern

    def test_upper_body_is_mapped_not_just_the_goal_lift(self):
        """A bench campaign or an upper-body block must score too."""
        for muscle in ("pecs", "lats", "triceps", "biceps", "side_delts", "calves"):
            assert MAP.trains(muscle), muscle

    def test_mixed_categories_have_no_default_on_purpose(self):
        """Their contents span the whole body, so any default would be wrong more than right."""
        for category in ("BANDED_EXERCISES", "TOTAL_BODY", "SUSPENSION"):
            assert not contributions_for(Exercise(category)).is_mapped, category


class TestLoading:
    def test_an_explicit_path_is_honoured(self, tmp_path):
        path = tmp_path / "m.json"
        path.write_text(json.dumps({
            "vocabulary": {"glute_max": "x"},
            "categories": {"SQUAT": {"glute_max": 0.5}},
            "exercises": {},
        }))
        assert load_muscle_map(path).contributions_for(Exercise("SQUAT")).credit("glute_max") == 0.5

    def test_an_empty_map_reports_everything_unmapped(self):
        empty = MuscleMap({})
        assert not empty.contributions_for(Exercise("SQUAT")).is_mapped
