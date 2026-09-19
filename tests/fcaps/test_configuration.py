"""FCAPS · Configuration — can NSP push config, including creating rows?

Row creation was the biggest technical risk on the switch and is proven on
one table. These assertions guard the generalisation of that proof to the
other 62, and the failure modes that leave a device worse off than before.
"""
from __future__ import annotations

import pytest

from actelis_mediation.rowedit import (CLEAR_ACTION, COMMIT_ACTION, RowEditorBusy,
                                       RowEditorError, RowEditorSession, delete_row)
from actelis_mediation.rowedit.specs import ALL_SPECS, SNMP_CONFIG_COMMUNITY_TABLE
from actelis_mediation.snmp.backend import FakeBackend

pytestmark = pytest.mark.fcaps("configuration")

ACTION = SNMP_CONFIG_COMMUNITY_TABLE.action_oid.lstrip(".")


def editor_backend(state="0"):
    be = FakeBackend(values={ACTION: state})
    original = be.set

    def set_(t, binds):
        out = original(t, binds)
        for oid, _type, value in binds:
            if oid.lstrip(".") == ACTION and value in ("1", "2"):
                be.values[ACTION] = "0"          # the agent returns to idle
        return out
    be.set = set_
    return be


# --- the proven sequence, generalised --------------------------------------

def test_row_creation_issues_the_lab_proven_sequence(target):
    be = editor_backend()
    with RowEditorSession(be, target, SNMP_CONFIG_COMMUNITY_TABLE, manager_id=999001) as row:
        row.stage(name="nsp-ro", sourceIP="10.20.30.0", sourceIPPrefixSize=24)
        row.commit()
    values = [v for _o, _t, v in be.sets]
    assert values[0] == "999001", "reserve with a manager ID first"
    assert values[-1] == str(COMMIT_ACTION), "commit last"
    types = {o: t for o, t, _v in be.sets}
    fields = SNMP_CONFIG_COMMUNITY_TABLE.fields
    assert types[fields["name"].oid.lstrip(".")] == "s"
    assert types[fields["sourceIP"].oid.lstrip(".")] == "a"
    assert types[fields["sourceIPPrefixSize"].oid.lstrip(".")] == "i"


def test_every_staged_field_type_matches_its_mib_syntax(mib_defs):
    """The defect that made the original helper unusable, asserted across all
    63 generated specs rather than the one that was hand-written."""
    from mib_types import type_char
    defs, by_oid = mib_defs
    import actelis_mediation.verify as verify  # noqa: F401  (ensures tools on path)
    tcs = __import__("mibscan").ALL_TCS
    checked = 0
    for spec_name, spec in ALL_SPECS.items():
        for fname, fld in spec.fields.items():
            obj = by_oid.get(fld.oid[:-2].lstrip("."))
            assert obj is not None, f"{spec_name}.{fname}: {fld.oid} not in the MIBs"
            assert fld.type_char == type_char(obj["syntax"], tcs), (
                f"{spec_name}.{fname}: declared '{fld.type_char}' but MIB SYNTAX is "
                f"{obj['syntax']!r}")
            checked += 1
    assert checked > 300


def test_every_staged_field_is_actually_writable(mib_defs):
    _defs, by_oid = mib_defs
    for spec_name, spec in ALL_SPECS.items():
        for fname, fld in spec.fields.items():
            obj = by_oid[fld.oid[:-2].lstrip(".")]
            assert obj["access"] in ("read-write", "read-create"), (
                f"{spec_name}.{fname} is {obj['access']} and cannot be staged")


def test_creatable_table_coverage_is_complete(mib_defs):
    """Every row-editor table in the MIB set must have a generated spec.

    The proven mechanism applies to all of them; a missing spec means a
    creatable table silently has no supported path from NSP.
    """
    defs, _ = mib_defs
    action_objects = {v["name"] for v in defs.values()
                      if v["kind"] == "OBJECT-TYPE"
                      and v["name"].endswith("RowEditorAction")
                      and v["module"].startswith("ML540M-")}
    covered = {f"{s.name}RowEditorAction" for s in ALL_SPECS.values()}
    missing = sorted(action_objects - covered)
    assert missing == [], f"row-editor tables with no generated spec: {missing}"
    assert len(ALL_SPECS) == len(action_objects) == 64


# --- failure modes that must not leave the device worse off ----------------

def test_failed_stage_releases_the_reservation(target):
    """A half-finished edit must not lock the table for every other manager."""
    be = editor_backend()
    with pytest.raises(RowEditorError), \
            RowEditorSession(be, target, SNMP_CONFIG_COMMUNITY_TABLE) as row:
        row.stage(no_such_field="x")
    assert be.sets[-1][2] == str(CLEAR_ACTION)
    assert be.values[ACTION] == "0", "editor must be idle after a failed edit"


def test_reservation_held_elsewhere_is_refused_with_the_holder_named(target):
    be = editor_backend(state="424242")
    with pytest.raises(RowEditorBusy) as exc:
        RowEditorSession(be, target, SNMP_CONFIG_COMMUNITY_TABLE).reserve()
    assert exc.value.holder == 424242
    assert "no reservation timeout" in str(exc.value)


def test_stale_reservation_is_recoverable_without_a_reboot(target):
    be = editor_backend(state="424242")
    RowEditorSession(be, target, SNMP_CONFIG_COMMUNITY_TABLE,
                     manager_id=999001, reclaim_stale=True).reserve()
    assert be.sets[0][2] == str(CLEAR_ACTION)
    assert be.sets[1][2] == "999001"


def test_rejected_commit_is_reported_not_swallowed(target):
    be = FakeBackend(values={ACTION: "0"})       # never returns to idle
    session = RowEditorSession(be, target, SNMP_CONFIG_COMMUNITY_TABLE)
    session.reserve()
    be.values[ACTION] = "999001"
    with pytest.raises(RowEditorError, match="rather than idle"):
        session.commit()


def test_delete_targets_the_rows_own_action_column(target):
    be = FakeBackend()
    suffix = SNMP_CONFIG_COMMUNITY_TABLE.index_spec.encode(
        name="nsp-ro", sourceIP="10.20.30.0", sourceIPPrefixSize=24)
    delete_row(be, target, SNMP_CONFIG_COMMUNITY_TABLE, suffix)
    oid, type_char, value = be.sets[0]
    assert oid.startswith(SNMP_CONFIG_COMMUNITY_TABLE.row_action_column_oid)
    assert (type_char, value) == ("u", "1")


def test_write_without_a_write_community_fails_before_touching_the_device(target):
    from actelis_mediation.snmp.backend import SnmpTarget
    ro_only = SnmpTarget(host="192.0.2.10", ro_community="ro")
    with pytest.raises(ValueError, match="no write community"):
        ro_only.write_community()


# --- hardware ---------------------------------------------------------------

@pytest.mark.hardware
def test_live_row_editors_are_all_idle(live):
    """Pre-flight check before any bulk provisioning run.

    A non-zero row-editor Action means someone is mid-edit -- or something
    died mid-edit and left the table locked.
    """
    device, backend = live
    if device.device_type != "switch":
        pytest.skip("row editors are an ML540M mechanism")
    busy = []
    for name, spec in sorted(ALL_SPECS.items()):
        try:
            vb = backend.get(device.target, [spec.action_oid])
        except Exception:
            continue                      # table not implemented on this firmware
        state = next(iter(vb.values())).value.strip()
        if state not in ("0", "IDLE", "IDLE(0)"):
            busy.append((name, state))
    assert busy == [], f"row editors left reserved: {busy}"


@pytest.mark.hardware
@pytest.mark.writes
def test_live_scalar_set_round_trip(live):
    """Mirrors the proven lab test: read a scalar, write it back unchanged."""
    device, backend = live
    if device.device_type != "switch":
        pytest.skip("uses a switch-specific scalar")
    oid = "1.3.6.1.4.1.5468.100.34.1.2.1.3.0"      # lldp tx interval
    before = next(iter(backend.get(device.target, [oid]).values())).value
    backend.set(device.target, [(oid, "u", before)])
    after = next(iter(backend.get(device.target, [oid]).values())).value
    assert after == before
