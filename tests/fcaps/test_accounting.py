"""FCAPS · Accounting — for this platform, that means inventory.

Neither device family exposes a usage/billing MIB, so the pillar reduces to
"can NSP populate and keep an accurate inventory record". These assertions
cover identity collection, the model-variant discovery that makes one Device
Model cover the whole ML600 family, and graceful degradation when a firmware
build does not implement part of the identity group.
"""
from __future__ import annotations

import pytest

from actelis_mediation.poll import poll_device, poll_identity
from actelis_mediation.poll import oids as O
from actelis_mediation.snmp.backend import FakeBackend
from actelis_mediation.store import Store

from .conftest import switch_image

pytestmark = pytest.mark.fcaps("accounting")


def test_switch_identity_populates_the_inventory_record(switch_backend, target):
    identity = poll_identity(switch_backend, target, "switch")
    assert identity["productModel"] == "ML540M"
    assert identity["swVersion"] == "00.00.16"
    assert identity["portCount"] == "10"


def test_ml600_identity_includes_the_model_variant(modem_backend, target):
    """One Device Model covers the whole ML600 family; the variant comes from
    servMonSystemModel, which is what makes that possible (ADR-0003)."""
    identity = poll_identity(modem_backend, target, "dsl-modem")
    assert identity["model"] == "ml684-501RG0048"
    assert identity["tid"] == "LAB-TID-01"
    assert identity["sysName"] == "lab-modem-01"


def test_extended_scope_models_exist_in_the_vendor_enum(mib_defs):
    """ADR-0003 as an executable assertion.

    ML622 and ML684 were queued as questions to Actelis. The `Models` textual
    convention answers both: they are ML600-family devices already covered by
    the MIB archive in this repo. If a MIB revision ever drops them, this
    fails and the scoping decision gets revisited.
    """
    import mibscan
    models = next(v for k, v in mibscan.ALL_TCS.items()
                  if k.endswith(":Models"))
    for model in ("ml684", "ml622"):
        assert model in models, f"{model} missing from the Models enum"
    assert "ml540" not in models, (
        "ML540 has appeared in the ML600 Models enum -- the two-device-type "
        "scoping decision in ADR-0003 needs revisiting")


def test_partial_identity_degrades_and_is_recorded(target, tmp_path):
    """A firmware that omits part of the identity group must not lose the rest.

    Exactly the shape of the known LLDP gap on firmware 00.00.16.
    """
    be = FakeBackend(values=switch_image(), unimplemented={O.SWITCH_PORT_COUNT})
    identity = poll_identity(be, target, "switch")
    assert identity["productModel"] == "ML540M"
    assert "portCount" not in identity


def test_identity_collection_is_idempotent(target, tmp_path, alarm_mapping, pm_mapping):
    """Re-polling an unchanged device must not grow the inventory record."""
    be = FakeBackend(values=switch_image())
    with Store(tmp_path / "inv.db") as store:
        for _ in range(4):
            poll_device("sw", be, target, "switch", store, alarm_mapping,
                        pm_mapping, what=("identity",))
        rows = store._conn.execute(
            "SELECT COUNT(*) c FROM identity_samples WHERE device_name='sw'").fetchone()
        assert rows["c"] == 3, "one row per attribute, not one per poll"


def test_unreachable_identity_is_recorded_as_a_capability_gap(
        target, tmp_path, alarm_mapping, pm_mapping):
    be = FakeBackend(values={}, unimplemented={"1.3.6.1.4.1.5468.100.1.1",
                                               "1.3.6.1.2.1.1"})
    with Store(tmp_path / "inv.db") as store:
        poll_device("sw", be, target, "switch", store, alarm_mapping,
                    pm_mapping, what=("identity",))
        gaps = store.capability_gaps("sw")
        assert len(gaps) == 1
        assert gaps[0]["oid"] == "identity"


def test_entity_mib_is_available_for_physical_inventory(mib_defs):
    """ENTITY-MIB ships in the ML600 archive and is the standard source for an
    NSP equipment hierarchy. It is not yet in the attribute schema -- asserted
    here so the gap stays visible rather than being quietly forgotten."""
    defs, _ = mib_defs
    entity = [v for v in defs.values() if v["module"] == "ENTITY-MIB"]
    assert len(entity) > 30
    assert any(v["name"] == "entPhysicalTable" for v in entity)


# --- hardware ---------------------------------------------------------------

@pytest.mark.hardware
def test_live_identity_is_complete(live):
    device, backend = live
    identity = poll_identity(backend, device.target, device.device_type)
    expected = (O.SWITCH_IDENTITY if device.device_type == "switch" else O.DSL_IDENTITY)
    missing = sorted(set(expected) - set(identity))
    print(f"\n{device.name} identity: {identity}")
    if missing:
        pytest.fail(f"agent does not implement: {missing} -- record as a "
                    f"capability gap for this firmware build")
