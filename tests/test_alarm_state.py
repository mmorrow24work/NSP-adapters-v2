"""Alarm state transitions.

The original recorded every standing alarm on every poll (1,440 duplicate
rows/day at the documented 60s interval) and never emitted a clear.
"""
from actelis_mediation.model.alarms import (Alarm, AlarmState, Severity,
                                            Transition, normalise_switch_alarm_type)


def alarm(key, severity=Severity.MAJOR, cause="link down", entity=""):
    return Alarm(key=key, severity=severity, probable_cause=cause,
                 source_value="alm-major(2)", entity=entity)


def test_first_sighting_raises_once_and_is_not_repeated():
    state = AlarmState()
    assert [t.transition for t in state.reconcile([alarm("a")])] == [Transition.RAISED]
    assert state.reconcile([alarm("a")]) == []          # still standing: silence
    assert state.reconcile([alarm("a")]) == []


def test_disappearance_from_the_table_emits_a_clear():
    state = AlarmState()
    state.reconcile([alarm("a"), alarm("b")])
    out = state.reconcile([alarm("a")])
    assert len(out) == 1
    assert out[0].transition is Transition.CLEARED
    assert out[0].alarm.key == "b"
    assert out[0].previous_severity is Severity.MAJOR


def test_severity_change_emits_changed_with_the_previous_value():
    state = AlarmState()
    state.reconcile([alarm("a", Severity.MINOR)])
    out = state.reconcile([alarm("a", Severity.MAJOR)])
    assert out[0].transition is Transition.CHANGED
    assert out[0].previous_severity is Severity.MINOR
    assert out[0].alarm.severity is Severity.MAJOR


def test_explicitly_cleared_row_clears_the_standing_alarm():
    """currentAlarmState alm-Cleared(2) -- honoured on the poll path now."""
    state = AlarmState()
    state.reconcile([alarm("a")])
    out = state.reconcile([alarm("a", Severity.CLEARED)])
    assert out[0].transition is Transition.CLEARED
    assert "a" not in state.standing


def test_restart_does_not_replay_standing_alarms_as_new():
    state = AlarmState()
    state.reconcile([alarm("a")])
    restarted = AlarmState()
    restarted.load(list(state.standing.values()))
    assert restarted.reconcile([alarm("a")]) == []


def test_per_port_alarm_type_folds_to_mapping_row_but_keeps_the_port():
    key, entity = normalise_switch_alarm_type("alarmGEPort7LinkDown(107)")
    assert key == "alarmGEPortNLinkDown(101-125)"
    assert entity == "GigabitEthernet 7"
    # Non-port alarms pass through untouched.
    assert normalise_switch_alarm_type("alarmSystemOverHeat(400)") == (
        "alarmSystemOverHeat(400)", "")


def test_two_ports_down_are_two_distinct_alarms():
    state = AlarmState()
    a7 = Alarm(key="switch:alarmGEPortNLinkDown(101-125):GigabitEthernet 7",
               severity=Severity.MAJOR, probable_cause="link down", source_value="x")
    a8 = Alarm(key="switch:alarmGEPortNLinkDown(101-125):GigabitEthernet 8",
               severity=Severity.MAJOR, probable_cause="link down", source_value="x")
    assert len(state.reconcile([a7, a8])) == 2
    assert len(state.standing) == 2
