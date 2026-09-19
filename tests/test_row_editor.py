"""Row-editor protocol, including the two defects fixed from the original."""
import pytest

from actelis_mediation.rowedit import (CLEAR_ACTION, COMMIT_ACTION, RowEditorBusy, RowEditorError,
                                       RowEditorSession, delete_row)
from actelis_mediation.rowedit.specs import SNMP_CONFIG_COMMUNITY_TABLE
from actelis_mediation.snmp.backend import FakeBackend, SnmpTarget

TARGET = SnmpTarget(host="192.0.2.10", ro_community="ro", rw_community="rw")
ACTION = SNMP_CONFIG_COMMUNITY_TABLE.action_oid


def backend(state="0"):
    return FakeBackend(values={ACTION.lstrip("."): state})


def test_generated_spec_matches_the_lab_proven_types():
    """The lab script used: name=s, srcIp=a, prefix=i.

    The original helper hardcoded 's' for every field, so staging this very
    table would have been rejected with wrongType by the agent.
    """
    f = SNMP_CONFIG_COMMUNITY_TABLE.fields
    assert f["name"].type_char == "s"
    assert f["sourceIP"].type_char == "a"
    assert f["sourceIPPrefixSize"].type_char == "i"


def test_row_action_column_matches_the_lab_capture():
    assert SNMP_CONFIG_COMMUNITY_TABLE.row_action_column_oid == \
        "1.3.6.1.4.1.5468.100.36.1.2.2.1.100"
    assert SNMP_CONFIG_COMMUNITY_TABLE.row_action_oid(
        "11.99.108.97.117.100.101.45.116.101.115.116.0.0.0.0.0") == \
        "1.3.6.1.4.1.5468.100.36.1.2.2.1.100." \
        "11.99.108.97.117.100.101.45.116.101.115.116.0.0.0.0.0"


def _agent_returns_to_idle(be):
    """Model the agent: writing CLEAR or COMMIT moves the editor back to IDLE."""
    original = be.set
    def set_(target, binds):
        out = original(target, binds)
        for oid, _t, value in binds:
            if oid.lstrip(".") == ACTION.lstrip(".") and value in ("1", "2"):
                be.values[ACTION.lstrip(".")] = "0"
        return out
    be.set = set_
    return be


def test_happy_path_reproduces_the_proven_sequence():
    be = _agent_returns_to_idle(backend())
    with RowEditorSession(be, TARGET, SNMP_CONFIG_COMMUNITY_TABLE, manager_id=999001) as row:
        row.stage(name="claude-test", sourceIP="0.0.0.0", sourceIPPrefixSize=0)
        row.commit()
    oids = [s[0] for s in be.sets]
    types = {s[0]: s[1] for s in be.sets}
    assert oids[0] == ACTION.lstrip(".")                       # reserve
    assert be.sets[0][2] == "999001"
    assert types[SNMP_CONFIG_COMMUNITY_TABLE.fields["sourceIP"].oid.lstrip(".")] == "a"
    assert types[SNMP_CONFIG_COMMUNITY_TABLE.fields["sourceIPPrefixSize"].oid.lstrip(".")] == "i"
    assert be.sets[-1][2] == str(COMMIT_ACTION)


def test_exception_inside_the_block_clears_the_reservation():
    be = backend()
    with pytest.raises(RowEditorError), \
            RowEditorSession(be, TARGET, SNMP_CONFIG_COMMUNITY_TABLE) as row:
        row.stage(nonexistent="x")
    assert be.sets[-1][2] == str(CLEAR_ACTION)


def test_reservation_held_by_another_manager_is_refused_by_default():
    be = backend(state="424242")
    with pytest.raises(RowEditorBusy) as exc:
        RowEditorSession(be, TARGET, SNMP_CONFIG_COMMUNITY_TABLE).reserve()
    assert exc.value.holder == 424242
    assert "no reservation timeout" in str(exc.value)


def test_stale_reservation_can_be_reclaimed_when_opted_in():
    """VTSSRowEditorState has no timeout: a crashed manager locks the table
    for everyone until someone writes CLEAR. The original's only advice was
    'clear it by hand'."""
    be = _agent_returns_to_idle(backend(state="424242"))
    session = RowEditorSession(be, TARGET, SNMP_CONFIG_COMMUNITY_TABLE,
                               manager_id=999001, reclaim_stale=True)
    session.reserve()
    assert be.sets[0][2] == str(CLEAR_ACTION)     # force-clear first
    assert be.sets[1][2] == "999001"              # then reserve


def test_manager_id_below_the_reserved_range_is_rejected():
    for bad in (0, 1, 2, 255):
        with pytest.raises(RowEditorError, match="reserved by the protocol"):
            RowEditorSession(backend(), TARGET, SNMP_CONFIG_COMMUNITY_TABLE, manager_id=bad)


def test_commit_that_does_not_return_to_idle_is_an_error():
    be = backend()
    session = RowEditorSession(be, TARGET, SNMP_CONFIG_COMMUNITY_TABLE)
    session.reserve()
    be.values[ACTION.lstrip(".")] = "999001"      # stuck: row rejected
    with pytest.raises(RowEditorError, match="rather than idle"):
        session.commit()


def test_delete_writes_one_to_the_rows_own_action_column():
    be = FakeBackend()
    suffix = "11.99.108.97.117.100.101.45.116.101.115.116.0.0.0.0.0"
    delete_row(be, TARGET, SNMP_CONFIG_COMMUNITY_TABLE, suffix)
    assert be.sets == [(SNMP_CONFIG_COMMUNITY_TABLE.row_action_oid(suffix).lstrip("."),
                        "u", "1")]


def test_all_generated_specs_are_structurally_sound():
    from actelis_mediation.rowedit import specs
    assert len(specs.ALL_SPECS) >= 60
    for name, spec in specs.ALL_SPECS.items():
        assert spec.action_oid.endswith(".0"), name
        assert spec.fields, name
        for fname, fld in spec.fields.items():
            assert fld.type_char in "iusaxotbd", f"{name}.{fname}={fld.type_char}"
            assert fld.oid.endswith(".0"), f"{name}.{fname} missing scalar .0"
        assert spec.row_action_column_oid.startswith(spec.table_oid + ".")


def test_row_editor_action_subid_is_not_always_100():
    """Worth pinning: the '.100' Action sub-identifier seen on the proven
    community table is a convention, not a rule. Across the 63 row-editor
    tables the MIBs use .100 (51), .101 (6) and .10000 (6). Hand-writing
    specs on the assumption of .100 would silently target a field OID on a
    fifth of the tables -- which is why they are generated from the MIB.
    """
    from actelis_mediation.rowedit import specs
    subids = {s.action_oid.rsplit(".", 2)[-2] for s in specs.ALL_SPECS.values()}
    assert subids == {"100", "101", "10000"}
