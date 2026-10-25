"""Strength metrics — e1RM, RIR and the uncertainty around them (pure math, offline).

The cases that matter are two real prescriptions, because they are where the design is
actually decided: one is robust to model choice and should be enforced, the other is not and
must not be.
"""

from pathlib import Path

import pytest

from gym_buddy.strength import metrics
from gym_buddy.strength.metrics import (
    BRZYCKI_MAX_REPS,
    LIGHT_LOAD_FLOOR_KG,
    REP_EXTRAPOLATION_GAP,
    SENSITIVITY_FORMULAS,
    confidence,
    e1rm,
    e1rm_interval,
    estimate_caveats,
    is_hard_set,
    load_for,
    load_interval,
    reps_at,
    rir,
    rir_interval,
)
from gym_buddy.strength.volume import HARD_SET_RIR_MAX

RIR_MAX = HARD_SET_RIR_MAX


class TestE1rm:
    @pytest.mark.parametrize("weight,reps,expected", [
        (140, 3, 148.2), (120, 7, 144.0), (60, 5, 67.5),
    ])
    def test_brzycki_is_the_default(self, weight, reps, expected):
        assert e1rm(weight, reps) == pytest.approx(expected, abs=0.1)

    def test_single_rep_returns_the_load_itself(self):
        """Brzycki's useful property — Epley reports 103.3% of a completed single."""
        assert e1rm(100, 1) == pytest.approx(100.0)
        assert e1rm(100, 1, formula="epley") != pytest.approx(100.0)

    def test_sensitivity_formulas(self):
        assert e1rm(140, 3, formula="epley") == pytest.approx(154.0, abs=0.1)

    def test_brzycki_refuses_its_asymptote(self):
        with pytest.raises(ValueError, match="asymptote"):
            e1rm(100, 37, formula="brzycki")

    @pytest.mark.parametrize("weight,reps", [(0, 5), (-10, 5), (100, 0)])
    def test_rejects_nonsense(self, weight, reps):
        with pytest.raises(ValueError):
            e1rm(weight, reps)


class TestRepsAt:
    @pytest.mark.parametrize("formula", SENSITIVITY_FORMULAS)
    def test_inverts_e1rm(self, formula):
        for weight, reps in [(140, 3), (120, 7), (60, 5)]:
            estimated = e1rm(weight, reps, formula=formula)
            assert reps_at(estimated, weight, formula=formula) == pytest.approx(reps, abs=0.01)

    def test_above_max_does_not_promise_a_single(self):
        assert reps_at(150, 150) == 1.0
        assert reps_at(150, 160) == 0.0


class TestLoadFor:
    @pytest.mark.parametrize("formula", SENSITIVITY_FORMULAS)
    def test_round_trips_with_rir(self, formula):
        load = load_for(153, reps=8, target_rir=2, formula=formula)
        assert rir(load, 8, 153, formula=formula) == pytest.approx(2, abs=0.01)

    def test_rejects_negative_reserve(self):
        with pytest.raises(ValueError):
            load_for(153, 8, target_rir=-1)


    def test_more_reserve_at_ten_effective_reps(self):
        """Brzycki's ceiling is 10 effective reps, so the old 8 x RIR 3 case moved to RIR 2."""
        assert load_for(153, 8, target_rir=2) < load_for(153, 8, target_rir=0)

    def test_more_reserve_means_less_load_epley(self):
        assert (load_for(153, 8, target_rir=3, formula="epley")
                < load_for(153, 8, target_rir=0, formula="epley"))

    def test_brzycki_refuses_past_its_ceiling_but_not_at_it(self):
        assert load_for(153, 8, target_rir=2, formula="brzycki") > 0   # exactly 10
        with pytest.raises(ValueError, match="brzycki"):
            load_for(153, 8, target_rir=3, formula="brzycki")           # 11
        with pytest.raises(ValueError, match="brzycki"):
            load_for(153, 12, formula="brzycki")

    def test_other_formulas_are_not_capped(self):
        assert load_for(153, 12, target_rir=3, formula="epley") > 0


class TestLoadInterval:
    def test_brackets_each_formulas_self_consistent_load(self):
        interval = load_interval(140, 3, 8, target_rir=2, anchor_rir=0)
        assert interval.formulas == SENSITIVITY_FORMULAS
        for f in interval.formulas:
            anchor = e1rm(140, 3, formula=f)
            assert interval.low <= load_for(anchor, 8, 2, formula=f) <= interval.high

    def test_pinned_values(self):
        """Brzycki 111.18 kg, Epley 115.5 kg: 140 x 3 (RIR 0) -> 8 reps @ RIR 2."""
        interval = load_interval(140, 3, 8, target_rir=2, anchor_rir=0)
        assert interval.low == pytest.approx(111.18, abs=0.01)
        assert interval.high == pytest.approx(115.5, abs=0.01)
        assert interval.formulas == ("brzycki", "epley")

    def test_anchor_rir_is_added_internally(self):
        """140 x 3 @ RIR 2 is a 5-effective-rep anchor; unknown RIR is a floor (RIR 0)."""
        with_rir = load_interval(140, 3, 8, target_rir=2, anchor_rir=2)
        floor = load_interval(140, 3, 8, target_rir=2)
        assert with_rir.low > floor.low and with_rir.high > floor.high
        assert floor == load_interval(140, 3, 8, target_rir=2, anchor_rir=0)
        assert with_rir == load_interval(140, 5, 8, target_rir=2, anchor_rir=0)

    def test_target_rir_is_required(self):
        with pytest.raises(TypeError):
            load_interval(140, 3, 8)

    def test_round_trips_through_rir(self):
        interval = load_interval(140, 3, 8, target_rir=2)
        for f in interval.formulas:
            anchor = e1rm(140, 3, formula=f)
            load = load_for(anchor, 8, 2, formula=f)
            assert rir(load, 8, anchor, formula=f) == pytest.approx(2, abs=0.01)

    def test_brzycki_dropped_when_the_anchor_exceeds_ten(self):
        interval = load_interval(100, 12, 8, target_rir=0)
        assert interval.formulas == ("epley",)

    def test_brzycki_dropped_when_the_target_exceeds_ten(self):
        interval = load_interval(140, 3, 8, target_rir=3)
        assert interval.formulas == ("epley",)
        assert load_interval(140, 3, 8, target_rir=2).formulas == SENSITIVITY_FORMULAS

    def test_brzycki_dropped_when_anchor_rir_pushes_it_past_ten(self):
        assert load_interval(100, 8, 5, target_rir=0, anchor_rir=3).formulas == ("epley",)


class TestExtrapolated:
    def test_two_formula_interval_is_not_extrapolated(self):
        assert not e1rm_interval(140, 3).extrapolated
        assert not load_interval(140, 3, 8, target_rir=2).extrapolated
        assert not rir_interval(120, 8, anchor_weight_kg=140, anchor_reps=3).extrapolated

    def test_one_formula_interval_is_extrapolated(self):
        assert e1rm_interval(100, 12).extrapolated
        assert load_interval(100, 12, 8, target_rir=0).extrapolated
        assert rir_interval(100, 12, anchor_weight_kg=140, anchor_reps=3).extrapolated


class TestSensitivityIntervals:
    """The enforcement rule: act on what survives a change of model, not on a point estimate."""

    def test_todays_progression_trigger_is_robustly_wrong(self):
        """3x8 @ 120kg is written as '1-2 RIR'. Every model says it is a max effort."""
        interval = rir_interval(120, 8, anchor_weight_kg=140, anchor_reps=3)
        assert interval.high < 1
        assert interval.spread < 1
        assert not interval.straddles(2)      # robust -> enforceable

    def test_the_sep14_prescription_is_uncertain_not_wrong(self):
        """2x10 @ 100kg: the models disagree across the hard-set boundary, so it cannot be
        called a definite error from load and reps alone."""
        interval = rir_interval(100, 10, anchor_weight_kg=140, anchor_reps=3)
        assert interval.low == pytest.approx(2.7, abs=0.1)
        assert interval.high == pytest.approx(6.2, abs=0.1)
        assert interval.straddles(RIR_MAX)   # not enforceable

    def test_anchor_rir_is_added_to_the_anchor_once(self):
        with_rir = rir_interval(120, 8, anchor_weight_kg=140, anchor_reps=3, anchor_rir=2)
        assert with_rir == rir_interval(120, 8, anchor_weight_kg=140, anchor_reps=5)
        assert with_rir != rir_interval(120, 8, anchor_weight_kg=140, anchor_reps=3)

    def test_brzycki_is_dropped_when_extrapolating(self):
        beyond = rir_interval(100, BRZYCKI_MAX_REPS + 5, anchor_weight_kg=140, anchor_reps=3)
        assert "brzycki" not in beyond.formulas
        within = rir_interval(100, BRZYCKI_MAX_REPS, anchor_weight_kg=140, anchor_reps=3)
        assert "brzycki" in within.formulas

    def test_e1rm_interval_brackets_every_formula(self):
        interval = e1rm_interval(140, 3)
        for formula in interval.formulas:
            assert interval.low <= e1rm(140, 3, formula=formula) <= interval.high


class TestEstimateCaveats:
    def test_a_clean_low_rep_anchor_with_a_personal_curve_has_none(self):
        assert estimate_caveats(reps=5, anchor_reps=3, anchor_rir=0,
                                has_personal_curve=True) == ()

    @pytest.mark.parametrize("kwargs,fragment", [
        ({"reps": 15, "anchor_reps": 3, "anchor_rir": 0}, "beyond where 1RM models are validated"),
        ({"reps": 10, "target_rir": 2, "anchor_reps": 3, "anchor_rir": 0},
         "12 effective reps — beyond where 1RM"),
        ({"reps": 8, "anchor_reps": 8, "anchor_rir": 3}, "anchor set is 11 effective reps"),
        ({"reps": 5, "anchor_reps": 15, "anchor_rir": 0}, "weak basis"),
        ({"reps": 5, "anchor_reps": 3, "anchor_rir": None}, "unrecorded"),
        ({"reps": 5, "anchor_reps": 3, "anchor_rir": 3}, "reported reserve"),
        ({"reps": 5, "anchor_reps": 3, "anchor_rir": 0, "weight_kg": 2.5}, "unreliable"),
        ({"reps": 5, "anchor_reps": 10, "anchor_rir": 0}, "effective reps below the anchor"),
    ])
    def test_flags_each_disqualifier(self, kwargs, fragment):
        caveats = estimate_caveats(has_personal_curve=True, **kwargs)
        assert any(fragment in c for c in caveats), caveats

    def test_missing_personal_curve_is_always_a_caveat(self):
        assert any("personal curve" in c
                   for c in estimate_caveats(reps=5, anchor_reps=3, anchor_rir=0))


class TestNoPrescribedSet:
    def test_reps_none_skips_the_prescribed_side_and_the_gap(self):
        caveats = estimate_caveats(reps=None, anchor_reps=10, anchor_rir=0, has_personal_curve=True)
        assert caveats == ()
        caveats = estimate_caveats(reps=None, anchor_reps=10, anchor_rir=2, has_personal_curve=True)
        assert any("weak basis" in c for c in caveats)
        assert not any("prescribed set" in c for c in caveats)

    def test_a_prescribed_set_is_still_judged(self):
        assert any("prescribed set" in c for c in estimate_caveats(reps=15, anchor_reps=3, anchor_rir=0))


class TestRepGapCaveat:
    GAP = "effective reps below the anchor"

    def _has(self, **kwargs):
        caveats = estimate_caveats(has_personal_curve=True, **kwargs)
        return any(self.GAP in c for c in caveats)

    def test_gap_of_five_warns(self):
        assert self._has(reps=5, anchor_reps=10, anchor_rir=0)

    def test_an_entry_checked_against_itself_has_no_gap(self):
        assert not self._has(reps=5, target_rir=3, anchor_reps=5, anchor_rir=3)

    def test_compares_effective_reps_on_both_sides(self):
        """7 effective reps each side: no gap, however the RIR is split."""
        assert not self._has(reps=5, target_rir=2, anchor_reps=5, anchor_rir=2)

    def test_exactly_the_gap_warns_one_less_does_not(self):
        assert self._has(reps=5, anchor_reps=8, anchor_rir=0)        # gap 3
        assert not self._has(reps=5, anchor_reps=7, anchor_rir=0)    # gap 2

    def test_target_rir_narrows_the_gap(self):
        assert not self._has(reps=5, target_rir=2, anchor_reps=8, anchor_rir=0)   # gap 1

    def test_constant_and_its_label(self):
        assert REP_EXTRAPOLATION_GAP == 3
        source = Path(metrics.__file__).read_text()
        line = source.index("REP_EXTRAPOLATION_GAP = 3")
        assert "HEURISTIC" in source[max(0, line - 400):line]


class TestHardSet:
    @pytest.mark.parametrize("reps_in_reserve,expected", [
        (0, True), (2, True), (RIR_MAX, True), (3.5, False), (6, False), (-1, False),
    ])
    def test_band_is_zero_to_the_configured_max(self, reps_in_reserve, expected):
        assert is_hard_set(reps_in_reserve, RIR_MAX) is expected

    def test_the_max_is_required(self):
        with pytest.raises(TypeError):
            is_hard_set(2)

    def test_a_tighter_max_narrows_the_band(self):
        assert is_hard_set(2, rir_max=1) is False
        assert is_hard_set(1, rir_max=1) is True

    def test_there_is_no_second_copy_of_the_edge(self):
        assert not hasattr(metrics, "HARD_SET_RIR_MAX")


class TestConfidence:
    @pytest.mark.parametrize("reps,expected", [
        (1, "high"), (5, "high"), (6, "medium"), (8, "medium"),
        (10, "medium"), (11, "low"), (12, "low"),
    ])
    def test_degrades_with_rep_count(self, reps, expected):
        assert confidence(reps) == expected

    def test_light_loads_are_low_confidence_whatever_the_reps(self):
        assert confidence(3, weight_kg=LIGHT_LOAD_FLOOR_KG - 0.5) == "low"


class TestRirFromRpe:
    """RIR-based RPE (Zourdos et al. 2016; Helms et al. 2016), 7 to 10 only."""

    @pytest.mark.parametrize("rpe,expected", [(10, 0), (9.5, 0), (9, 1), (8.5, 1.5), (8, 2), (7.5, 2.5), (7, 3)])
    def test_ten_minus_rpe_with_nine_and_a_half_at_zero(self, rpe, expected):
        assert metrics.rir_from_rpe(rpe) == expected

    @pytest.mark.parametrize("rpe", [6.5, 6, 5, 0])
    def test_below_seven_is_a_band_not_a_count(self, rpe):
        with pytest.raises(ValueError, match="below 7"):
            metrics.rir_from_rpe(rpe)

    @pytest.mark.parametrize("rpe", [8.3, 11, 7.25])
    def test_off_scale_values_are_rejected(self, rpe):
        with pytest.raises(ValueError, match="not on the RIR-based scale"):
            metrics.rir_from_rpe(rpe)

    def test_the_docstring_cites_both_sources(self):
        assert "Zourdos" in metrics.rir_from_rpe.__doc__ and "Helms" in metrics.rir_from_rpe.__doc__
