from gym_buddy.models.exercises import Exercise
from gym_buddy.strength.volume import count

THRUST = Exercise("HIP_RAISE", "BARBELL_HIP_THRUST_WITH_BENCH")


def test_only_working_sets_near_failure_count():
    v = count([(THRUST, "working", 8, None, 2),
               (THRUST, "working", 8, None, 5),       # too easy
               (THRUST, "warmup", 5, None, None)])
    assert v.hard_sets == 1 and v.hard["glute_max"] == 1.0


def test_credit_is_fractional_per_muscle():
    v = count([(THRUST, "working", 8, None, 1)])
    assert v.hard == {"glute_max": 1.0, "hamstrings": 0.5, "quads": 0.25}


def test_no_rir_is_not_judged_rather_than_dropped():
    v = count([(THRUST, "working", 8, None, None)])
    assert v.hard_sets == 0 and v.not_judged_sets == 1 and v.not_judged["glute_max"] == 1.0


def test_timed_missed_and_unknown_role_never_count():
    v = count([(Exercise("PLANK"), "working", None, 60, 1),
               (THRUST, "working", 0, None, 0),
               (THRUST, None, 8, None, 1)])
    assert v.hard_sets == 0 and v.not_judged_sets == 0 and v.unknown_role_sets == 1


def test_unmapped_exercises_are_named_not_zeroed():
    v = count([(Exercise("TOTAL_BODY"), "working", 10, None, 2)])
    assert v.unmapped == {"TOTAL_BODY"}
    assert any("TOTAL_BODY" in line for line in v.lines())
