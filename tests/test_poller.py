"""Poller behaviour, using a fake device image -- no network, no net-snmp."""
from actelis_mediation.model.alarms import Severity
from actelis_mediation.poll import (observe_alarms_switch, poll_identity,
                                    poll_pm_dsl, poll_pm_switch)
from actelis_mediation.poll import oids as O
from actelis_mediation.poll.mapping import (AlarmMapping, AlarmMappingRow,
                                            PmMapping, PmMappingRow)
from actelis_mediation.snmp.backend import FakeBackend, SnmpTarget

TARGET = SnmpTarget(host="192.0.2.10", ro_community="ro")


def alarm_mapping():
    return AlarmMapping([
        AlarmMappingRow("switch", "currentAlarmLevel (VTSSAlarmLevel, ML540M-SYSTEM-MIB)",
                        "alm-major(2)", "major", "Major", "", "", "confirmed", ""),
        AlarmMappingRow("switch", "currentAlarmTypeId (VTSSAlarmType, ML540M-SYSTEM-MIB)",
                        "alarmGEPortNLinkDown(101-125)", "port link down", "Major",
                        "linkDown", "SA", "confirmed", ""),
    ])


def pm_mapping():
    return PmMapping([
        PmMappingRow("dsl-modem", "hdsl2Shdsl15MinIntervalES", "HDSL2-SHDSL-LINE-MIB",
                     "15min", "count", "dslLine.es", "count", "binned", ""),
        PmMappingRow("switch", "ml540mPerfMonitorStatusStatisticsDm2WayDelayAverage",
                     "ML540M-PERF-MONITOR-MIB", "evc-dm", "", "evc.dm.twoWayAvg", "", "", ""),
    ])


def test_identity_survives_one_unimplemented_oid():
    """The original raised on any 'No Such Instance' and discarded the values
    that did come back -- on a device family already known to ship firmware
    with missing subtrees."""
    be = FakeBackend(values={O.SWITCH_IDENTITY["productModel"].lstrip("."): "ML540M",
                             O.SWITCH_IDENTITY["swVersion"].lstrip("."): "00.00.16"},
                     unimplemented={O.SWITCH_PORT_COUNT})
    got = poll_identity(be, TARGET, "switch")
    assert got["productModel"] == "ML540M"
    assert got["swVersion"] == "00.00.16"
    assert "portCount" not in got


def test_switch_alarm_rows_become_per_port_alarms():
    e = O.SWITCH_CURRENT_ALARM_ENTRY
    be = FakeBackend(values={
        f"{e}.3.1": "alarmGEPort7LinkDown(107)", f"{e}.4.1": "alm-major(2)",
        f"{e}.5.1": "alm-Set(1)", f"{e}.2.1": "41",
        f"{e}.3.2": "alarmGEPort8LinkDown(108)", f"{e}.4.2": "alm-major(2)",
        f"{e}.5.2": "alm-Set(1)", f"{e}.2.2": "42",
    })
    alarms = observe_alarms_switch(be, TARGET, alarm_mapping())
    assert {a.entity for a in alarms} == {"GigabitEthernet 7", "GigabitEthernet 8"}
    assert all(a.severity is Severity.MAJOR for a in alarms)
    assert len({a.key for a in alarms}) == 2


def test_alm_cleared_state_maps_to_cleared_on_the_poll_path():
    """The original read currentAlarmState but only put it in a text field, so
    a cleared row was still recorded at its alarm severity."""
    e = O.SWITCH_CURRENT_ALARM_ENTRY
    be = FakeBackend(values={f"{e}.3.1": "alarmGEPort7LinkDown(107)",
                             f"{e}.4.1": "alm-major(2)", f"{e}.5.1": "alm-Cleared(2)",
                             f"{e}.2.1": "41"})
    assert observe_alarms_switch(be, TARGET, alarm_mapping())[0].severity is Severity.CLEARED


def test_dsl_pm_samples_carry_full_bin_identity():
    """Regression: the original stored no index at all, so 96 bins x ports x
    wire pairs collapsed into indistinguishable rows."""
    col = O.DSL_15MIN_COLUMNS["hdsl2Shdsl15MinIntervalES"]
    be = FakeBackend(values={f"{col}.101.1.1.1.1": "3", f"{col}.101.1.1.1.2": "7",
                             f"{col}.102.1.1.1.1": "0"})
    samples = poll_pm_dsl(be, TARGET, pm_mapping())
    assert len(samples) == 3
    by_key = {(s["index"]["ifIndex"], s["index"]["intervalNumber"]): s for s in samples}
    assert by_key[(101, 1)]["raw_value"] == "3"
    assert by_key[(101, 2)]["raw_value"] == "7"
    assert by_key[(102, 1)]["raw_value"] == "0"
    s = by_key[(101, 2)]
    assert s["metric"] == "dslLine.es"
    assert s["bin_window"] == "15min" and s["bin_id"] == 2
    assert s["index"]["wirePair"] == 1 and s["index"]["endpointSide"] == 1


def test_dm_unit_is_joined_on_the_full_index_not_the_last_subid():
    """The 1000x bug: two DM rows sharing entryId=7 across intervals 1 and 2,
    with different units. Keying on the last sub-identifier applies one unit
    to both."""
    avg = O.SWITCH_DM_COLUMNS["ml540mPerfMonitorStatusStatisticsDm2WayDelayAverage"]
    unit = O.SWITCH_DM_UNIT_COLUMN
    be = FakeBackend(values={f"{unit}.1.7": "us(0)", f"{avg}.1.7": "1500",
                             f"{unit}.2.7": "ns(1)", f"{avg}.2.7": "1500"})
    samples = [s for s in poll_pm_switch(be, TARGET, pm_mapping())
               if s["bin_window"] == "evc-dm"]
    by_interval = {s["index"]["intervalId"]: s for s in samples}
    assert by_interval[1]["unit"] == "microseconds"
    assert by_interval[2]["unit"] == "nanoseconds"
    assert by_interval[1]["value"] == 1500.0 and by_interval[2]["value"] == 1500.0


def test_dm_row_without_a_unit_is_not_silently_assumed():
    avg = O.SWITCH_DM_COLUMNS["ml540mPerfMonitorStatusStatisticsDm2WayDelayAverage"]
    be = FakeBackend(values={f"{avg}.1.7": "1500"})     # no DmUnit column
    s = [x for x in poll_pm_switch(be, TARGET, pm_mapping()) if x["bin_window"] == "evc-dm"][0]
    assert s["value"] is None
    assert s["unit_verified"] is False
    assert "unknown" in s["unit"]


def test_unverified_loss_rate_scale_is_not_applied():
    rate = O.SWITCH_LM_COLUMNS["ml540mPerfMonitorStatusStatisticsLmNearEndLossRate"]
    cnt = O.SWITCH_LM_COLUMNS["ml540mPerfMonitorStatusStatisticsLmNearEndLossCount"]
    be = FakeBackend(values={f"{rate}.1.5": "250", f"{cnt}.1.5": "12"})
    samples = {s["source_object"]: s for s in poll_pm_switch(be, TARGET, pm_mapping())}
    r = samples["ml540mPerfMonitorStatusStatisticsLmNearEndLossRate"]
    assert r["value"] is None and r["raw_value"] == "250"
    assert r["unit_verified"] is False and "UNVERIFIED" in r["unit"]
    c = samples["ml540mPerfMonitorStatusStatisticsLmNearEndLossCount"]
    assert c["value"] == 12.0 and c["unit_verified"] is True
