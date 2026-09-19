"""Per-device polling: identity, alarms, PM bins.

Compared with the original prototype the important behavioural changes are:

* table rows are assembled on their **full** index (see snmp/oid.py), and the
  decoded index travels with every sample, so PM data is attributable to a
  port / endpoint side / wire pair / bin number;
* alarms produce **state transitions** rather than a repeated stream, and the
  switch's ``alm-Cleared`` state is honoured on the poll path (it previously
  was only on the trap path);
* PM values are **scaled** using the units resolved from the MIBs, and a
  value whose unit could not be resolved is stored raw and flagged rather
  than silently assumed;
* an unimplemented subtree is recorded once as a capability gap instead of
  being retried and re-logged every cycle.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, UTC

from ..model import alarms as am
from ..model import tables, units
from ..model.alarms import Alarm, AlarmState, Severity
from ..snmp.backend import SnmpBackend, SnmpTarget
from ..snmp.errors import SnmpNoSuchObject
from ..snmp.oid import rows_from_columns
from ..store import Store
from . import oids
from .mapping import AlarmMapping, PmMapping

logger = logging.getLogger(__name__)


def now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _index_key(index: dict) -> str:
    return ";".join(f"{k}={index[k]}" for k in sorted(index))


def _unwrap(walk) -> dict[str, str]:
    """{oid: VarBind} -> {oid: value}."""
    return {o: (vb.value if hasattr(vb, "value") else vb) for o, vb in walk.items()}


# ---------------------------------------------------------------------------
# Identity
# ---------------------------------------------------------------------------

def poll_identity(backend: SnmpBackend, target: SnmpTarget, device_type: str) -> dict[str, str]:
    spec = oids.SWITCH_IDENTITY if device_type == "switch" else oids.DSL_IDENTITY
    found = backend.get(target, list(spec.values()))
    out = {}
    for name, oid in spec.items():
        vb = found.get(oid.lstrip("."))
        if vb is not None:
            out[name] = vb.value
    return out


# ---------------------------------------------------------------------------
# Alarms
# ---------------------------------------------------------------------------

def observe_alarms_switch(backend: SnmpBackend, target: SnmpTarget,
                          mapping: AlarmMapping) -> list[Alarm]:
    cols = {k: oids.SWITCH_ALARM_COLUMNS[k] for k in ("typeId", "level", "state", "seqId")}
    walks = {}
    for name, oid in cols.items():
        try:
            walks[name] = _unwrap(backend.walk(target, oid))
        except SnmpNoSuchObject:
            walks[name] = {}
    rows = rows_from_columns(walks, cols, tables.SWITCH_CURRENT_ALARM)

    out: list[Alarm] = []
    for row in rows:
        raw_type = am.strip_enum_label(row.values.get("typeId", ""))
        raw_level = am.strip_enum_label(row.values.get("level", ""))
        raw_state = am.strip_enum_label(row.values.get("state", ""))
        type_key, entity = am.normalise_switch_alarm_type(raw_type)

        type_row = mapping.lookup("switch", type_key)
        level_row = mapping.lookup("switch", raw_level)

        # The alarm key must survive re-indexing: currentAlarmRowId is a slot
        # number the device reuses, so it is deliberately NOT part of the key.
        key = f"switch:{type_key}:{entity}" if entity else f"switch:{type_key}"

        cleared = raw_state in am.SWITCH_ALARM_STATE_CLEARED
        severity = (Severity.CLEARED if cleared else
                    Severity(level_row.nsp_severity) if level_row else Severity.INDETERMINATE)

        out.append(Alarm(
            key=key, severity=severity,
            probable_cause=(type_row.nsp_probable_cause if type_row else raw_type),
            source_value=raw_level, entity=entity,
            confidence=(type_row.confidence if type_row else "unmapped"),
            raw=f"type={raw_type} level={raw_level} state={raw_state} "
                f"seq={row.values.get('seqId','')}"))
    return out


def observe_alarms_dsl(backend: SnmpBackend, target: SnmpTarget,
                       mapping: AlarmMapping) -> list[Alarm]:
    cols = {k: oids.DSL_ALARM_COLUMNS[k]
            for k in ("name", "aid", "serviceAffect", "severity", "description")}
    walks = {}
    for name, oid in cols.items():
        try:
            walks[name] = _unwrap(backend.walk(target, oid))
        except SnmpNoSuchObject:
            walks[name] = {}
    rows = rows_from_columns(walks, cols, tables.DSL_ALARM)

    out: list[Alarm] = []
    for row in rows:
        name = row.values.get("name", "").strip('"')
        aid = row.values.get("aid", "").strip('"')
        severity_raw = row.values.get("severity", "").strip('"')
        sa_raw = row.values.get("serviceAffect", "").strip('"')

        sev_row = mapping.lookup("dsl-modem", severity_raw)
        name_row = mapping.lookup("dsl-modem", name)

        # TL1 AID + alarm name is the natural stable identity for this table;
        # alarmIndex is a table slot and is not stable across clears.
        out.append(Alarm(
            key=f"dsl:{aid}:{name}" if aid else f"dsl:{name}",
            severity=Severity(sev_row.nsp_severity) if sev_row else Severity.INDETERMINATE,
            probable_cause=(name_row.nsp_probable_cause if name_row else name),
            source_value=severity_raw, entity=aid,
            service_affecting=(sa_raw.upper() == "SA" if sa_raw else None),
            confidence=(name_row.confidence if name_row else "unmapped"),
            raw=row.values.get("description", "").strip('"') or name))
    return out


# ---------------------------------------------------------------------------
# PM
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PmSpec:
    columns: dict[str, str]
    index_spec: object
    bin_window: str
    bin_field: str | None            # index component that identifies the bin
    scale: units.Scale


DSL_PM_SPECS = [
    PmSpec(oids.DSL_15MIN_COLUMNS, tables.DSL_15MIN_INTERVAL, "15min",
           "intervalNumber", units.EVENT_COUNT),
    PmSpec(oids.DSL_1DAY_COLUMNS, tables.DSL_1DAY_INTERVAL, "1day",
           "intervalNumber", units.EVENT_COUNT),
]


def poll_pm_dsl(backend: SnmpBackend, target: SnmpTarget, mapping: PmMapping) -> list[dict]:
    collected = now_iso()
    out: list[dict] = []
    for spec in DSL_PM_SPECS:
        walks = {}
        for name, oid in spec.columns.items():
            try:
                walks[name] = _unwrap(backend.walk(target, oid))
            except SnmpNoSuchObject:
                walks[name] = {}
        for row in rows_from_columns(walks, spec.columns, spec.index_spec):
            bin_id = row.index.get(spec.bin_field, "") if spec.bin_field else ""
            for col_name, raw in row.values.items():
                m = mapping.lookup("dsl-modem", col_name)
                out.append({
                    "collected_at": collected, "source_object": col_name,
                    "metric": m.nsp_metric_name if m else col_name,
                    "index": row.index, "index_key": _index_key(row.index),
                    "bin_window": spec.bin_window, "bin_id": bin_id,
                    "raw_value": raw, "value": spec.scale.apply(raw),
                    "unit": spec.scale.unit, "unit_verified": spec.scale.verified,
                })
    return out


def poll_pm_switch(backend: SnmpBackend, target: SnmpTarget, mapping: PmMapping) -> list[dict]:
    collected = now_iso()
    out: list[dict] = []

    # --- LM ---------------------------------------------------------------
    lm_walks = {}
    for name, oid in oids.SWITCH_LM_COLUMNS.items():
        try:
            lm_walks[name] = _unwrap(backend.walk(target, oid))
        except SnmpNoSuchObject:
            lm_walks[name] = {}
    for row in rows_from_columns(lm_walks, oids.SWITCH_LM_COLUMNS, tables.SWITCH_LM):
        for col_name, raw in row.values.items():
            m = mapping.lookup("switch", col_name)
            is_rate = col_name.endswith("LossRate")
            scale = units.SWITCH_LM_LOSS_RATE if is_rate else units.EVENT_COUNT
            out.append({
                "collected_at": collected, "source_object": col_name,
                "metric": m.nsp_metric_name if m else col_name,
                "index": row.index, "index_key": _index_key(row.index),
                "bin_window": "evc-lm", "bin_id": row.index.get("intervalId", ""),
                "raw_value": raw,
                # An unverified scale is NOT applied: the raw value is kept and
                # flagged, so nothing downstream mistakes an assumption for data.
                "value": None if is_rate else scale.apply(raw),
                "unit": scale.unit if not is_rate else f"{scale.unit} (UNVERIFIED)",
                "unit_verified": scale.verified,
            })

    # --- DM: the per-row unit must be joined on the FULL index -------------
    dm_cols = dict(oids.SWITCH_DM_COLUMNS)
    dm_cols["__unit"] = oids.SWITCH_DM_UNIT_COLUMN
    dm_walks = {}
    for name, oid in dm_cols.items():
        try:
            dm_walks[name] = _unwrap(backend.walk(target, oid))
        except SnmpNoSuchObject:
            dm_walks[name] = {}
    for row in rows_from_columns(dm_walks, dm_cols, tables.SWITCH_DM):
        scale = units.resolve_dm_unit(row.values.get("__unit", ""))
        for col_name, raw in row.values.items():
            if col_name == "__unit":
                continue
            m = mapping.lookup("switch", col_name)
            out.append({
                "collected_at": collected, "source_object": col_name,
                "metric": m.nsp_metric_name if m else col_name,
                "index": row.index, "index_key": _index_key(row.index),
                "bin_window": "evc-dm", "bin_id": row.index.get("intervalId", ""),
                "raw_value": raw,
                "value": scale.apply(raw) if scale else None,
                "unit": scale.unit if scale else "unknown (DmUnit missing for this row)",
                "unit_verified": bool(scale),
            })
    return out


# ---------------------------------------------------------------------------
# Top-level
# ---------------------------------------------------------------------------

def poll_device(name: str, backend: SnmpBackend, target: SnmpTarget, device_type: str,
                store: Store, alarm_mapping: AlarmMapping, pm_mapping: PmMapping,
                what=("identity", "alarms", "pm")) -> dict[str, int]:
    now = now_iso()
    store.upsert_device(name, device_type, target.host, now)
    result = {"identity": 0, "alarm_transitions": 0, "pm_samples": 0}

    if "identity" in what:
        try:
            identity = poll_identity(backend, target, device_type)
            store.record_identity(name, now, identity)
            result["identity"] = len(identity)
        except SnmpNoSuchObject as exc:
            store.record_capability_gap(name, "identity", str(exc)[:300], now)

    if "alarms" in what:
        state = AlarmState()
        state.load(store.load_alarm_state(name))
        try:
            observed = (observe_alarms_switch(backend, target, alarm_mapping)
                        if device_type == "switch"
                        else observe_alarms_dsl(backend, target, alarm_mapping))
        except SnmpNoSuchObject as exc:
            store.record_capability_gap(name, "alarm-table", str(exc)[:300], now)
            observed = []
        transitions = state.reconcile(observed)
        result["alarm_transitions"] = store.apply_transitions(name, now, transitions, "poll")

    if "pm" in what:
        try:
            samples = (poll_pm_switch(backend, target, pm_mapping) if device_type == "switch"
                       else poll_pm_dsl(backend, target, pm_mapping))
        except SnmpNoSuchObject as exc:
            store.record_capability_gap(name, "pm-tables", str(exc)[:300], now)
            samples = []
        store.record_pm(name, samples)
        result["pm_samples"] = len(samples)

    return result
