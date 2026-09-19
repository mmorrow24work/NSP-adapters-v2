"""Unit scales resolved from the vendor MIBs."""
from actelis_mediation.model import units


def test_flr_measured_scale_matches_the_mib_worked_example():
    """ACTELIS-SERV-MON-MIB: 'provided as 1 = 0.0001%, i.e. 50 means 0.005%'."""
    assert units.FLR_MEASURED.apply(50) == 0.005
    assert units.FLR_MEASURED.apply(1_000_000) == 100.0
    assert units.FLR_MEASURED.verified


def test_flr_objective_uses_a_different_scale_than_measured_flr():
    """The 10x trap: 'Unit 1 = 0.001%. 90000 means >= 90% FLR'."""
    assert units.FLR_OBJECTIVE.apply(90_000) == 90.0
    assert units.FLR_MEASURED.factor != units.FLR_OBJECTIVE.factor


def test_utilisation_matches_the_mib_worked_example():
    """'units of 1 = 0.001%, i.e. 5985 means 5.985%'."""
    assert round(units.UTILIZATION.apply(5985), 3) == 5.985


def test_dm_unit_resolves_both_enum_spellings():
    assert units.resolve_dm_unit("us(0)").unit == "microseconds"
    assert units.resolve_dm_unit("INTEGER: ns(1)").unit == "nanoseconds"
    assert units.resolve_dm_unit("0").unit == "microseconds"


def test_unknown_dm_unit_returns_none_rather_than_guessing():
    # Defaulting to microseconds on an unrecognised value is a 1000x error.
    assert units.resolve_dm_unit("ps(2)") is None
    assert units.resolve_dm_unit("") is None


def test_switch_loss_rate_scale_is_flagged_unverified():
    """Genuinely unstated in ML540M-PERF-MONITOR-MIB -- must not be trusted."""
    assert units.SWITCH_LM_LOSS_RATE.verified is False
    assert "ASSUMED" in units.SWITCH_LM_LOSS_RATE.evidence
