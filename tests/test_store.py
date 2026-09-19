"""Store: idempotency and alarm state persistence."""
from actelis_mediation.model.alarms import Alarm, AlarmState, Severity
from actelis_mediation.store import Store


def sample(bin_id, value="3", ifindex=101):
    return {"collected_at": "2026-09-19T00:00:00Z", "metric": "dslLine.es",
            "source_object": "hdsl2Shdsl15MinIntervalES",
            "index": {"ifIndex": ifindex, "intervalNumber": bin_id},
            "index_key": f"ifIndex={ifindex};intervalNumber={bin_id}",
            "bin_window": "15min", "bin_id": bin_id, "raw_value": value,
            "value": float(value), "unit": "count", "unit_verified": True}


def test_repolling_the_same_bins_does_not_duplicate(tmp_path):
    """The original re-read all 96 historical bins every 5 minutes and
    inserted them all again: ~288 copies of every bin per day."""
    with Store(tmp_path / "t.db") as st:
        st.upsert_device("d", "dsl-modem", "192.0.2.1", "now")
        rows = [sample(i) for i in range(1, 97)]
        st.record_pm("d", rows)
        st.record_pm("d", rows)
        st.record_pm("d", rows)
        assert len(st.recent_pm("d", limit=1000)) == 96


def test_distinct_ports_and_bins_are_distinct_rows(tmp_path):
    with Store(tmp_path / "t.db") as st:
        st.upsert_device("d", "dsl-modem", "192.0.2.1", "now")
        st.record_pm("d", [sample(1, ifindex=101), sample(1, ifindex=102)])
        assert len(st.recent_pm("d", limit=10)) == 2


def test_alarm_transitions_persist_and_reload(tmp_path):
    with Store(tmp_path / "t.db") as st:
        st.upsert_device("s", "switch", "192.0.2.2", "now")
        state = AlarmState()
        a = Alarm(key="switch:port7", severity=Severity.MAJOR,
                  probable_cause="link down", source_value="alm-major(2)",
                  entity="GigabitEthernet 7")
        st.apply_transitions("s", "t1", state.reconcile([a]))
        assert len(st.standing_alarms("s")) == 1

        # A fresh process reloads standing alarms and does not re-raise them.
        reloaded = AlarmState()
        reloaded.load(st.load_alarm_state("s"))
        assert reloaded.reconcile([a]) == []

        st.apply_transitions("s", "t2", reloaded.reconcile([]))
        assert len(st.standing_alarms("s")) == 0
        events = st.recent_alarm_events("s", limit=10)
        assert [e["transition"] for e in events] == ["cleared", "raised"]


def test_capability_gap_recorded_once(tmp_path):
    with Store(tmp_path / "t.db") as st:
        st.upsert_device("s", "switch", "192.0.2.2", "now")
        for _ in range(5):
            st.record_capability_gap("s", "1.3.6.1.4.1.5468.100.34.1.3.2",
                                     "No Such Object (fw 00.00.16 LLDP)", "now")
        assert len(st.capability_gaps("s")) == 1
