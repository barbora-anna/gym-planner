import datetime

import pytest

from gym_buddy.models.exercises import Exercise
from gym_buddy.models.workout import Workout
from gym_buddy.storage.db import SCHEMA_VERSION, SchemaTooNew, connect
from gym_buddy.storage.workouts import WorkoutRepo, diff


def workout(id="2026-10-24-a", date="2026-10-24", reps=5, **extra):
    return Workout.model_validate({"id": id, "date": date, **extra, "exercises": [
        {"exercise": "SQUAT:BARBELL_BACK_SQUAT", "sets": [
            {"role": "warmup", "reps": 5, "weight_kg": 40},
            {"role": "working", "reps": reps, "weight_kg": 80, "rir": 2}]}]})


@pytest.fixture
def repo(tmp_path):
    return WorkoutRepo(connect(tmp_path / "gym.db"))


def test_save_and_get_round_trip(repo):
    w = workout(note="felt good")
    repo.save(w)
    assert repo.get(w.id) == w


def test_saving_again_replaces_the_sets(repo):
    repo.save(workout(reps=5))
    repo.save(workout(reps=4))
    reps = [s.reps for s in repo.sets(Exercise("SQUAT", "BARBELL_BACK_SQUAT"))]
    assert reps == [5, 4]


def test_sets_filter_by_exact_exercise_and_date(repo):
    repo.save(workout("2026-10-20-a", "2026-10-20"))
    repo.save(workout("2026-10-24-a", "2026-10-24"))
    assert repo.sets(Exercise("SQUAT")) == []
    recent = repo.sets(from_date=datetime.date(2026, 10, 22))
    assert {s.workout_id for s in recent} == {"2026-10-24-a"}


def test_workouts_last_keeps_the_newest(repo):
    for d in ("2026-10-18", "2026-10-20", "2026-10-24"):
        repo.save(workout(f"{d}-a", d))
    assert [w.id for w in repo.workouts(last=2)] == ["2026-10-20-a", "2026-10-24-a"]


def test_remove_cascades_to_sets(repo):
    repo.save(workout())
    assert repo.remove("2026-10-24-a")
    assert repo.sets() == [] and not repo.remove("2026-10-24-a")


def test_logged_exercises_carry_the_last_date(repo):
    repo.save(workout("2026-10-20-a", "2026-10-20"))
    repo.save(workout("2026-10-24-a", "2026-10-24"))
    assert repo.logged_exercises() == {Exercise("SQUAT", "BARBELL_BACK_SQUAT"): datetime.date(2026, 10, 24)}


def test_diff_names_each_changed_field():
    assert diff(workout(), workout()) == []
    lines = diff(workout(reps=5), workout(reps=4, note="x"))
    assert "  note: None → 'x'" in lines
    assert "  SQUAT:BARBELL_BACK_SQUAT set 2 reps: 5 → 4" in lines


def test_diff_shows_added_and_removed_sets():
    shorter = Workout.model_validate({"id": "2026-10-24-a", "date": "2026-10-24", "exercises": [
        {"exercise": "SQUAT:BARBELL_BACK_SQUAT", "sets": [{"role": "warmup", "reps": 5, "weight_kg": 40}]}]})
    assert diff(workout(), shorter) == ["  SQUAT:BARBELL_BACK_SQUAT set 2: removed"]
    assert diff(shorter, workout()) == ["  SQUAT:BARBELL_BACK_SQUAT set 2: added"]


def test_a_newer_schema_is_refused(tmp_path):
    path = tmp_path / "gym.db"
    connect(path).execute(f"PRAGMA user_version = {SCHEMA_VERSION + 1}")
    with pytest.raises(SchemaTooNew):
        connect(path)
