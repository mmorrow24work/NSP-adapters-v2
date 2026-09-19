"""Fixtures for the FCAPS acceptance suite.

Every test here is written to run in two modes against the same assertions:

* **offline** (default) — against ``FakeBackend``, an in-memory device image
  built from the same OID constants the pollers use. Runs in CI, no network.
* **hardware** (``--device <name>``) — against a real unit through the
  net-snmp backend, using the inventory in ``etc/devices.yaml``.

That is deliberate: an acceptance checklist that only ever runs against a mock
proves the mock. `docs/fcaps-test-plan.md` explains which assertions are
meaningful in which mode.
"""
from __future__ import annotations

import pytest

from actelis_mediation.poll import oids as O
from actelis_mediation.poll.mapping import AlarmMapping, PmMapping
from actelis_mediation.snmp.backend import FakeBackend, SnmpTarget

LAB_TARGET = SnmpTarget(host="192.0.2.10", ro_community="ro", rw_community="rw")


# --------------------------------------------------------------------------
# Synthetic device images, built from the real OID constants
# --------------------------------------------------------------------------

def switch_image(*, alarms=((7, "alm-major(2)", "alm-Set(1)"),),
                 lm_rows=((1, 5),), dm_rows=((1, 7, "us(0)"),)) -> dict[str, str]:
    """An ML540M device image. Identity values are the real lab-confirmed ones."""
    v: dict[str, str] = {
        O.SWITCH_IDENTITY["productModel"].lstrip("."): "ML540M",
        O.SWITCH_IDENTITY["swVersion"].lstrip("."): "00.00.16",
        O.SWITCH_IDENTITY["portCount"].lstrip("."): "10",
        O.SWITCH_SNMP_VERSION + ".0": "snmpV2c(1)",
    }
    e = O.SWITCH_CURRENT_ALARM_ENTRY
    for row_id, (port, level, state) in enumerate(alarms, start=1):
        v[f"{e}.1.{row_id}"] = str(row_id)
        v[f"{e}.2.{row_id}"] = str(40 + row_id)
        v[f"{e}.3.{row_id}"] = f"alarmGEPort{port}LinkDown({100 + port})"
        v[f"{e}.4.{row_id}"] = level
        v[f"{e}.5.{row_id}"] = state
    for interval, entry in lm_rows:
        for name, oid in O.SWITCH_LM_COLUMNS.items():
            v[f"{oid}.{interval}.{entry}"] = "250" if name.endswith("LossRate") else "12"
    for interval, entry, unit in dm_rows:
        v[f"{O.SWITCH_DM_UNIT_COLUMN}.{interval}.{entry}"] = unit
        for oid in O.SWITCH_DM_COLUMNS.values():
            v[f"{oid}.{interval}.{entry}"] = "1500"
    return v


def modem_image(*, model="ml684-501RG0048", bins=((101, 1, 1, 1, 1),)) -> dict[str, str]:
    """An ML600-family device image."""
    v: dict[str, str] = {
        O.DSL_IDENTITY["sysDescr"].lstrip("."): "Actelis ML684",
        O.DSL_IDENTITY["sysName"].lstrip("."): "lab-modem-01",
        O.DSL_IDENTITY["model"].lstrip("."): model,
        O.DSL_IDENTITY["swVersion"].lstrip("."): "7.10",
        O.DSL_IDENTITY["tid"].lstrip("."): "LAB-TID-01",
    }
    for if_index, inv, side, pair, interval in bins:
        for oid in O.DSL_15MIN_COLUMNS.values():
            v[f"{oid}.{if_index}.{inv}.{side}.{pair}.{interval}"] = "3"
    return v


def dsl_alarm_rows(rows) -> dict[str, str]:
    """rows: iterable of (index, name, aid, severity, serviceAffect, description)."""
    v: dict[str, str] = {}
    c = O.DSL_ALARM_COLUMNS
    for idx, name, aid, sev, sa, desc in rows:
        v[f"{c['name']}.{idx}"] = name
        v[f"{c['aid']}.{idx}"] = aid
        v[f"{c['severity']}.{idx}"] = sev
        v[f"{c['serviceAffect']}.{idx}"] = sa
        v[f"{c['description']}.{idx}"] = desc
    return v


# --------------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------------

@pytest.fixture(scope="session")
def alarm_mapping() -> AlarmMapping:
    return AlarmMapping.load()


@pytest.fixture(scope="session")
def pm_mapping() -> PmMapping:
    return PmMapping.load()


@pytest.fixture
def switch_backend() -> FakeBackend:
    return FakeBackend(values=switch_image())


@pytest.fixture
def modem_backend() -> FakeBackend:
    return FakeBackend(values=modem_image())


@pytest.fixture
def target() -> SnmpTarget:
    return LAB_TARGET


@pytest.fixture(scope="session")
def live(request):
    """(device_config, backend) for hardware-marked tests, or skip."""
    name = request.config.getoption("--device")
    if not name:
        pytest.skip("hardware test: pass --device <name>")
    from actelis_mediation.config import AppConfig
    from actelis_mediation.snmp.netsnmp import NetSnmpBackend
    cfg = AppConfig.load(request.config.getoption("--device-config"))
    match = [d for d in cfg.devices if d.name == name]
    if not match:
        pytest.fail(f"device {name!r} not found in the configured inventory")
    return match[0], NetSnmpBackend(community_mode=cfg.community_mode)


@pytest.fixture(scope="session")
def mib_defs():
    """Parsed vendor MIBs, for assertions that must hold against the source."""
    pytest.importorskip("py7zr")
    from actelis_mediation.verify import load_mibs
    return load_mibs()
