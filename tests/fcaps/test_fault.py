"""FCAPS · Fault — can NSP be given a usable fault feed from these devices?

The acceptance question is not "does the alarm table respond" but "does what
comes out of it satisfy a fault manager": closed severity vocabulary, stable
identity across polls, a clear event when the condition ends, and agreement
between the polled and trapped paths.
"""
from __future__ import annotations

import pytest

from actelis_mediation.model.alarms import (AlarmState, Severity, Transition,
                                            parse_severity)
from actelis_mediation.poll import observe_alarms_dsl, observe_alarms_switch
from actelis_mediation.snmp.backend import FakeBackend
from actelis_mediation.traps import SWITCH_ALARM_TRAP_TYPES, DecodedTrap, trap_to_alarm

from .conftest import dsl_alarm_rows, switch_image

pytestmark = pytest.mark.fcaps("fault")


# --- the alarm feed itself -------------------------------------------------

def test_switch_alarm_table_yields_normalised_alarms(switch_backend, target, alarm_mapping):
    alarms = observe_alarms_switch(switch_backend, target, alarm_mapping)
    assert alarms, "a populated alarm table must produce at least one alarm"
    a = alarms[0]
    assert a.severity is Severity.MAJOR
    assert a.entity == "GigabitEthernet 7"
    assert a.probable_cause, "every alarm needs a probable cause for NSP FM"
    assert a.key


def test_dsl_alarm_table_yields_normalised_alarms(target, alarm_mapping):
    be = FakeBackend(values=dsl_alarm_rows([
        (1, "LOSW", "MDM-1-1", "CR", "SA", "Loss of sync word"),
        (2, "HSLDWN", "HSL-1", "MJ", "SA", "High speed link down"),
    ]))
    alarms = observe_alarms_dsl(be, target, alarm_mapping)
    assert len(alarms) == 2
    by_key = {a.key: a for a in alarms}
    assert "dsl:MDM-1-1:LOSW" in by_key
    assert by_key["dsl:MDM-1-1:LOSW"].severity is Severity.CRITICAL
    assert by_key["dsl:MDM-1-1:LOSW"].service_affecting is True


def test_alarm_severities_come_from_a_closed_vocabulary(alarm_mapping):
    """Every `nsp_severity` is either a real severity or a marked cross-reference.

    The CSV uses a parenthesised pointer -- e.g. "(see alarmSeverity CR/MJ/MN/NA
    mapping above)" -- for rows whose severity is carried by a different column
    of the same device alarm. That is a defensible authoring convention, but it
    means the column is not uniformly a severity: 12 of 50 rows hold prose.
    Anything that is NOT parenthesised must be a valid member of the model, so
    a genuine typo still fails here.
    """
    valid = {s.value for s in Severity}
    bad = sorted({r.nsp_severity for r in alarm_mapping.rows
                  if r.nsp_severity
                  and not r.nsp_severity.startswith("(")
                  and r.nsp_severity not in valid})
    assert bad == [], f"mapping rows carry severities outside the model: {bad}"


def test_severity_parsing_never_raises_on_any_mapping_row(alarm_mapping):
    """Regression: the pollers used to call `Severity(row.nsp_severity)`.

    On any of the 12 cross-reference rows that raises ValueError and takes
    down the whole polling cycle. Found by writing this suite.
    """
    for row in alarm_mapping.rows:
        assert isinstance(parse_severity(row.nsp_severity), Severity)
    assert parse_severity("(see alarmSeverity above)") is Severity.INDETERMINATE
    assert parse_severity("Sev1") is Severity.INDETERMINATE
    assert parse_severity("") is Severity.INDETERMINATE
    assert parse_severity("Major") is Severity.MAJOR


def test_confirmed_rows_are_fully_populated(alarm_mapping):
    """A row flagged `confirmed` is claimed to be settled — so it must be."""
    incomplete = [r.source_value for r in alarm_mapping.rows
                  if r.confidence.startswith("confirmed")
                  and not (r.nsp_severity and r.nsp_probable_cause)]
    assert incomplete == [], f"confirmed rows missing severity/cause: {incomplete}"


def test_unmapped_alarm_degrades_rather_than_crashes(target, alarm_mapping):
    be = FakeBackend(values=switch_image(alarms=((7, "alm-unheard-of(9)", "alm-Set(1)"),)))
    alarms = observe_alarms_switch(be, target, alarm_mapping)
    assert alarms[0].severity is Severity.INDETERMINATE
    assert alarms[0].confidence in ("unmapped", "") or alarms[0].confidence


# --- lifecycle: the part NSP actually consumes -----------------------------

def test_raise_then_clear_emits_exactly_one_of_each(target, alarm_mapping):
    state = AlarmState()
    up = FakeBackend(values=switch_image(alarms=((7, "alm-major(2)", "alm-Set(1)"),)))
    down = FakeBackend(values=switch_image(alarms=()))

    raised = state.reconcile(observe_alarms_switch(up, target, alarm_mapping))
    assert [t.transition for t in raised] == [Transition.RAISED]

    repeat = state.reconcile(observe_alarms_switch(up, target, alarm_mapping))
    assert repeat == [], "a standing alarm must not be re-emitted every poll"

    cleared = state.reconcile(observe_alarms_switch(down, target, alarm_mapping))
    assert [t.transition for t in cleared] == [Transition.CLEARED]


def test_device_reported_clear_state_is_honoured(target, alarm_mapping):
    """VTSSAlarmState alm-Cleared(2) must clear, not record at alarm severity."""
    state = AlarmState()
    up = FakeBackend(values=switch_image(alarms=((7, "alm-major(2)", "alm-Set(1)"),)))
    state.reconcile(observe_alarms_switch(up, target, alarm_mapping))
    done = FakeBackend(values=switch_image(alarms=((7, "alm-major(2)", "alm-Cleared(2)"),)))
    out = state.reconcile(observe_alarms_switch(done, target, alarm_mapping))
    assert [t.transition for t in out] == [Transition.CLEARED]


def test_alarm_identity_is_stable_across_table_reindexing(target, alarm_mapping):
    """currentAlarmRowId is a reusable slot number, so it must not be the key.

    Same fault, different row id: one alarm, no spurious clear-and-raise.
    """
    state = AlarmState()
    first = FakeBackend(values=switch_image(alarms=((7, "alm-major(2)", "alm-Set(1)"),)))
    state.reconcile(observe_alarms_switch(first, target, alarm_mapping))
    # Device reboots; the same fault now occupies row 1 behind another alarm.
    reindexed = FakeBackend(values=switch_image(
        alarms=((9, "alm-minor(1)", "alm-Set(1)"), (7, "alm-major(2)", "alm-Set(1)"))))
    out = state.reconcile(observe_alarms_switch(reindexed, target, alarm_mapping))
    assert [t.transition for t in out] == [Transition.RAISED]
    assert out[0].alarm.entity == "GigabitEthernet 9"


def test_restart_does_not_replay_standing_alarms(target, alarm_mapping):
    up = FakeBackend(values=switch_image())
    state = AlarmState()
    state.reconcile(observe_alarms_switch(up, target, alarm_mapping))
    restarted = AlarmState()
    restarted.load(list(state.standing.values()))
    assert restarted.reconcile(observe_alarms_switch(up, target, alarm_mapping)) == []


def test_poll_and_trap_paths_agree_on_alarm_identity(target, alarm_mapping):
    """A port-7 link-down seen by trap and by poll must be ONE alarm.

    If the keys differ, a trap raises an alarm the next poll can never clear.
    """
    polled = observe_alarms_switch(
        FakeBackend(values=switch_image(alarms=((7, "alm-major(2)", "alm-Set(1)"),))),
        target, alarm_mapping)[0]

    trap_oid = next(o for o, t in SWITCH_ALARM_TRAP_TYPES.items() if t.endswith("(107)"))
    trapped = trap_to_alarm(
        DecodedTrap(host="192.0.2.10", trap_oid=trap_oid,
                    varbinds=["41", "7", "alm-major(2)", "alm-Set(1)", "0"],
                    received_at="2026-09-19T00:00:00Z"),
        alarm_mapping)
    assert trapped is not None
    assert trapped.key == polled.key


def test_trap_clear_clears_a_poll_raised_alarm(target, alarm_mapping):
    state = AlarmState()
    state.reconcile(observe_alarms_switch(
        FakeBackend(values=switch_image(alarms=((7, "alm-major(2)", "alm-Set(1)"),))),
        target, alarm_mapping))
    trap_oid = next(o for o, t in SWITCH_ALARM_TRAP_TYPES.items() if t.endswith("(107)"))
    cleared = trap_to_alarm(
        DecodedTrap(host="192.0.2.10", trap_oid=trap_oid,
                    varbinds=["42", "7", "alm-major(2)", "alm-Cleared(2)", "0"],
                    received_at="2026-09-19T00:01:00Z"),
        alarm_mapping)
    assert cleared.severity is Severity.CLEARED
    assert cleared.key in state.standing


# --- coverage limits that must be designed around --------------------------

def test_link_down_traps_exist_only_for_ports_1_to_10(mib_defs):
    """A vendor gap, asserted so it cannot be forgotten.

    VTSSAlarmType enumerates 25 per-port link-down conditions and
    currentAlarmTable carries rows for all of them, but ML540M-SYSTEM-MIB
    defines a trap for ports 1-10 only. Ports 11-25 are reachable ONLY by
    polling, so any design that assumes traps are the primary fault path is
    silently blind on more than half the ports.
    """
    defs, _ = mib_defs
    trapped = {int(n.removeprefix("trapAlmGEPort").removesuffix("LinkDown"))
               for n in defs if n.startswith("trapAlmGEPort") and n.endswith("LinkDown")}
    assert trapped == set(range(1, 11)), "trap coverage changed -- re-check the design"

    # The alarm TABLE, by contrast, covers all 25 ports.
    from actelis_mediation.model.alarms import GE_PORT_LINK_DOWN_ROW, normalise_switch_alarm_type
    for port in (11, 18, 25):
        key, entity = normalise_switch_alarm_type(f"alarmGEPort{port}LinkDown({100 + port})")
        assert key == GE_PORT_LINK_DOWN_ROW
        assert entity == f"GigabitEthernet {port}"


def test_only_the_system_mib_defines_notifications(mib_defs):
    """Confirms the project's own correction: ERPS/EPS/MSTP/loop-protection/
    PSEC/MEP fault conditions are polled status objects, not traps."""
    defs, _ = mib_defs
    switch_modules = {v["module"] for v in defs.values()
                      if v["kind"] == "NOTIFICATION-TYPE" and v["module"].startswith("ML540M-")}
    assert switch_modules == {"ML540M-SYSTEM-MIB"}, (
        "a switch feature MIB now defines traps -- the polled-status design "
        f"for fault detection may need revisiting: {sorted(switch_modules)}")

    counts = {}
    for v in defs.values():
        if v["kind"] == "NOTIFICATION-TYPE" and v["module"] == "ML540M-SYSTEM-MIB":
            counts[v["name"]] = v["oid"]
    alarm_traps = [o for o in counts.values() if o.startswith("1.3.6.1.4.1.5468.100.1.2.3.2")]
    event_traps = [o for o in counts.values() if o.startswith("1.3.6.1.4.1.5468.100.1.2.3.1")]
    assert len(alarm_traps) == 13
    assert len(event_traps) == 41


# --- hardware ---------------------------------------------------------------

@pytest.mark.hardware
def test_live_alarm_table_is_walkable(live, alarm_mapping):
    device, backend = live
    observe = (observe_alarms_switch if device.device_type == "switch"
               else observe_alarms_dsl)
    alarms = observe(backend, device.target, alarm_mapping)
    for a in alarms:
        assert a.severity.value in {s.value for s in Severity}
        assert a.key
    print(f"\n{len(alarms)} standing alarm(s) on {device.name}")
