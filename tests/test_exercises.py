"""The exercise catalog — loads from garmin-fit-sdk and validates against it (offline)."""

import pytest
from pydantic import ValidationError

from gym_buddy.models.exercises import (
    Exercise,
    categories,
    exercises_in,
    find,
    humanise,
)

THRUST = Exercise("HIP_RAISE", "BARBELL_HIP_THRUST_WITH_BENCH")
SQUAT = Exercise("SQUAT", "BARBELL_BACK_SQUAT")


class TestCatalog:
    def test_loads_uppercase_catalog(self):
        cats = categories()
        assert len(cats) > 40
        assert "SQUAT" in cats
        assert all(c == c.upper() for c in cats)

    def test_exercises_in_is_case_insensitive_and_safe(self):
        assert exercises_in("squat") == exercises_in("SQUAT")
        assert "GOBLET_SQUAT" in exercises_in("SQUAT")
        assert exercises_in("NOPE") == []


class TestExerciseValidation:
    def test_category_only(self):
        assert Exercise("PLANK").name is None

    def test_rejects_unknown_category(self):
        with pytest.raises(ValidationError):
            Exercise("NOT_A_CATEGORY")

    def test_rejects_name_not_in_category(self):
        with pytest.raises(ValidationError):
            Exercise("SQUAT", "BENCH_PRESS")

    def test_normalizes_case(self):
        assert Exercise("squat", "goblet_squat") == Exercise("SQUAT", "GOBLET_SQUAT")
        assert Exercise(category="squat").category == "SQUAT"


class TestFind:
    def test_finds_across_catalog(self):
        assert Exercise("SQUAT", "GOBLET_SQUAT") in find("goblet")


class TestHumanise:
    @pytest.mark.parametrize("exercise,expected", [
        (THRUST, "Hip Thrust"),
        (SQUAT, "Back Squat"),
        (Exercise("PULL_UP", "WIDE_GRIP_LAT_PULLDOWN"), "Wide Grip Lat Pulldown"),
        (Exercise("BENCH_PRESS"), "Bench Press"),
    ])
    def test_strips_equipment_and_setup_words(self, exercise, expected):
        assert humanise(exercise) == expected
