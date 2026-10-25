import datetime

import pytest
from pydantic import ValidationError

from gym_buddy.models.exercises import Exercise, find
from gym_buddy.models.session import PlannedSession
from gym_buddy.models.workout import Workout

PLAN = {"slug": "lower-a", "date": "2026-10-24", "title": "Lower A", "exercises": [
    {"exercise": "SQUAT:BARBELL_BACK_SQUAT",
     "sets": [{"role": "warmup", "reps": 5, "weight_kg": 20},
              {"role": "working", "reps": 5, "weight_kg": 80, "rir": 2}]}]}


class TestExercise:
    def test_parses_the_key_form(self):
        assert Exercise.model_validate("squat:barbell_back_squat") == Exercise("SQUAT", "BARBELL_BACK_SQUAT")
        assert Exercise.model_validate("PLANK") == Exercise("PLANK")

    def test_key_round_trips(self):
        assert Exercise("SQUAT", "LEG_PRESS").key == "SQUAT:LEG_PRESS"
        assert Exercise("PLANK").key == "PLANK"

    def test_an_unknown_name_is_refused(self):
        with pytest.raises(ValidationError):
            Exercise.model_validate("SQUAT:MOON_SQUAT")

    def test_find_matches_every_word(self):
        keys = [e.key for e in find("hip thrust")]
        assert "HIP_RAISE:BARBELL_HIP_THRUST_WITH_BENCH" in keys
        assert all("HIP" in k and "THRUST" in k for k in keys)


class TestPlannedSession:
    def test_id_and_set_ids_derive_from_date_and_slug(self):
        plan = PlannedSession.model_validate(PLAN)
        assert plan.id == "ps-2026-10-24-lower-a"
        assert plan.set_id(0, 1) == "ps-2026-10-24-lower-a-e1s2"

    def test_a_matching_id_round_trips_and_a_wrong_one_fails(self):
        assert PlannedSession.model_validate({**PLAN, "id": "ps-2026-10-24-lower-a"})
        with pytest.raises(ValidationError):
            PlannedSession.model_validate({**PLAN, "id": "ps-2026-10-25-lower-a"})

    def test_a_typo_fails_instead_of_dropping_a_load(self):
        bad = {**PLAN, "exercises": [{"exercise": "SQUAT", "sets": [{"role": "working", "reps": 5, "weight": 60}]}]}
        with pytest.raises(ValidationError):
            PlannedSession.model_validate(bad)

    def test_a_set_needs_reps_or_seconds(self):
        bad = {**PLAN, "exercises": [{"exercise": "SQUAT", "sets": [{"role": "working"}]}]}
        with pytest.raises(ValidationError):
            PlannedSession.model_validate(bad)

    def test_display_name_defaults_to_the_humanised_one(self):
        assert PlannedSession.model_validate(PLAN).exercises[0].display_name == "Back Squat"


class TestWorkout:
    def test_flat_numbers_sets_in_order(self):
        w = Workout.model_validate({"id": "2026-10-24-a", "date": "2026-10-24", "exercises": [
            {"exercise": "SQUAT", "sets": [{"role": "working", "reps": 5, "weight_kg": 80}]},
            {"exercise": "PLANK", "sets": [{"role": "working", "seconds": 40}]}]})
        flat = w.flat()
        assert [s.ord for s in flat] == [0, 1]
        assert flat[1].exercise == Exercise("PLANK") and flat[1].date == datetime.date(2026, 10, 24)

    def test_reps_and_seconds_are_exclusive(self):
        with pytest.raises(ValidationError):
            Workout.model_validate({"id": "x", "date": "2026-10-24", "exercises": [
                {"exercise": "PLANK", "sets": [{"reps": 5, "seconds": 40}]}]})

    def test_id_must_be_a_slug(self):
        with pytest.raises(ValidationError):
            Workout.model_validate({"id": "Not A Slug", "date": "2026-10-24", "exercises": [
                {"exercise": "SQUAT", "sets": [{"reps": 5}]}]})
