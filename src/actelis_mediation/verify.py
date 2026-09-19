"""Verify the code's OID constants and index specs against the vendor MIBs.

This is the guard the original project had no equivalent of. Every OID in
``poll/oids.py`` and every INDEX spec in ``model/tables.py`` is checked
against the MIB archives in ``mibs/actelis/`` by extracting and parsing them
at test time. Consequences:

  * a vendor MIB revision that moves an object, renumbers a column, or adds
    an index component fails the build instead of silently mis-polling;
  * the "firmware / MIB drift across device generations" risk becomes a
    mechanical check rather than a code review;
  * the parse is independent of whatever tool produced the CSV OID maps, so
    it is a genuine second opinion rather than a restatement.

Needs ``py7zr``; skipped (not failed) if the archives are absent.
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TOOLS = REPO / "tools"


def load_mibs() -> tuple[dict, dict]:
    """Extract both archives and return (defs_by_name, defs_by_oid)."""
    import py7zr
    sys.path.insert(0, str(TOOLS))
    import mibscan                                                  # noqa: PLC0415

    tmp = tempfile.mkdtemp(prefix="actelis-mibs-")
    for archive in sorted((REPO / "mibs" / "actelis").glob("*.7z")):
        with py7zr.SevenZipFile(archive) as z:
            z.extractall(path=os.path.join(tmp, archive.stem))
    defs, _mods, _files = mibscan.scan([tmp])
    oids = mibscan.resolve(defs)
    for d in defs.values():
        d["oid"] = oids.get(d["name"], "")
    by_oid: dict[str, dict] = {}
    for d in defs.values():
        if d["oid"]:
            by_oid.setdefault(d["oid"], d)
    return defs, by_oid


def expected_oids() -> dict[str, tuple[str, str]]:
    """{label: (oid, expected MIB object name)}."""
    from .poll import oids as O
    out: dict[str, tuple[str, str]] = {
        "switch.productModel": (O.SWITCH_PRODUCT_MODEL, "productModel"),
        "switch.swVersion": (O.SWITCH_SW_VERSION, "swVersion"),
        "switch.portCount": (O.SWITCH_PORT_COUNT, "portCount"),
        "switch.currentAlarmEntry": (O.SWITCH_CURRENT_ALARM_ENTRY, "currentAlarmEntry"),
        "dsl.alarmEntry": (O.DSL_ALARM_ENTRY, "alarmEntry"),
        "dsl.servMonSystemModel": (O.DSL_SERVMON_MODEL, "servMonSystemModel"),
        "dsl.15minEntry": (O.DSL_15MIN_ENTRY, "hdsl2Shdsl15MinIntervalEntry"),
        "dsl.1dayEntry": (O.DSL_1DAY_ENTRY, "hdsl2Shdsl1DayIntervalEntry"),
        "switch.lmEntry": (O.SWITCH_LM_ENTRY, "ml540mPerfMonitorStatusStatisticsLmEntry"),
        "switch.dmEntry": (O.SWITCH_DM_ENTRY, "ml540mPerfMonitorStatusStatisticsDmEntry"),
        "switch.dmUnit": (O.SWITCH_DM_UNIT_COLUMN,
                          "ml540mPerfMonitorStatusStatisticsDmUnit"),
        "dsl.trapAlarmRaised": (O.DSL_TRAP_ALARM_RAISED, "alarmRaised"),
        "dsl.trapAlarmCleared": (O.DSL_TRAP_ALARM_CLEARED, "alarmCleared"),
        "switch.snmpVersion": (O.SWITCH_SNMP_VERSION, "ml540mSnmpConfigGlobalsVersion"),
        "switch.snmpWriteCommunity": (O.SWITCH_SNMP_WRITE_COMMUNITY,
                                      "ml540mSnmpConfigGlobalsWriteCommunity"),
    }
    for col, oid in O.SWITCH_ALARM_COLUMNS.items():
        out[f"switch.alarm.{col}"] = (oid, f"currentAlarm{col[0].upper()}{col[1:]}")
    for name, oid in {**O.DSL_15MIN_COLUMNS, **O.DSL_1DAY_COLUMNS,
                      **O.SWITCH_LM_COLUMNS, **O.SWITCH_DM_COLUMNS}.items():
        out[f"column.{name}"] = (oid, name)
    return out


def verify_oids() -> list[str]:
    """Return a list of human-readable mismatches; empty means all good."""
    _defs, by_oid = load_mibs()
    problems: list[str] = []
    for label, (oid, expected) in expected_oids().items():
        got = by_oid.get(oid.lstrip("."))
        if got is None:
            problems.append(f"{label}: {oid} is not defined in any vendor MIB")
        elif got["name"] != expected:
            problems.append(
                f"{label}: {oid} is {got['name']} in the MIB, expected {expected}")
    return problems


def verify_index_specs() -> list[str]:
    """Check each IndexSpec against the INDEX clause of its ...Entry object."""
    from .model.tables import INDEX_SPECS_BY_ENTRY
    defs, _ = load_mibs()
    problems: list[str] = []
    for entry_name, spec in INDEX_SPECS_BY_ENTRY.items():
        entry = defs.get(entry_name)
        if entry is None:
            problems.append(f"{entry_name}: not found in the vendor MIBs")
            continue
        components = [c.strip() for c in entry["index"].split(",") if c.strip()]
        if len(components) != len(spec.names):
            problems.append(
                f"{entry_name}: MIB INDEX has {len(components)} component(s) "
                f"{components}, spec declares {len(spec.names)} {list(spec.names)}")
    return problems
