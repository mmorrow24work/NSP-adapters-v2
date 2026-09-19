"""snmptrapd-fed trap decoding.

Unchanged in approach from the original -- consuming ``snmptrapd`` output
rather than adding an untested trap-receiving library is a reasonable call,
and the varbind orders here are transcribed from the NOTIFICATION-TYPE
OBJECTS clauses in ACTELIS-ALARM-MIB and ML540M-SYSTEM-MIB.

STILL UNPROVEN, and this must not be forgotten when reading the code: no real
trap payload has ever been captured from either device family in this
project. "Matches the MIB" and "matches what the agent emits" are different
claims. docs/testing-strategy.md has the 20-minute lab procedure that would
settle it.

What changed: decoded traps now flow through the same ``Alarm`` /
``AlarmState`` path as polled alarms, so a trap-raised alarm and a
poll-discovered one converge on one row rather than producing two
independent records, and a trap clear actually clears the standing alarm.

Note the coverage limit, which is a vendor MIB gap rather than a choice:
``alarmTraps`` defines a link-down trap only for GE ports 1-10, while
``VTSSAlarmType`` and ``currentAlarmTable`` cover all 25. Ports 11-25 can
therefore only be caught by polling -- confirmed by counting the
NOTIFICATION-TYPE definitions in the MIB (13 alarm traps, 41 event traps,
all in ML540M-SYSTEM-MIB; no other switch MIB defines any notification).
"""
from __future__ import annotations

import logging
import re
import sys
from dataclasses import dataclass
from datetime import datetime, UTC

from ..model.alarms import Alarm, Severity, normalise_switch_alarm_type, strip_enum_label
from ..poll import oids
from ..poll.mapping import AlarmMapping

logger = logging.getLogger(__name__)

_SOURCE_RE = re.compile(r"^(?P<host>\d{1,3}(?:\.\d{1,3}){3})\b")
SNMP_TRAP_OID = "1.3.6.1.6.3.1.1.4.1.0"

SWITCH_ALARM_TRAP_TYPES = {
    f"{oids.SWITCH_ALARM_TRAP_PREFIX}.1.1": "alarmSystemOverHeat(400)",
    f"{oids.SWITCH_ALARM_TRAP_PREFIX}.1.2": "alarmPower1NotFeed(301)",
    f"{oids.SWITCH_ALARM_TRAP_PREFIX}.1.3": "alarmPower2NotFeed(302)",
    **{f"{oids.SWITCH_ALARM_TRAP_PREFIX}.2.{p}": f"alarmGEPort{p}LinkDown({100+p})"
       for p in range(1, 11)},
}


@dataclass(frozen=True)
class DecodedTrap:
    host: str
    trap_oid: str
    varbinds: list[str]
    received_at: str


def _split_varbinds(rest: str) -> list[str]:
    tokens, current, in_quotes = [], "", False
    for ch in rest:
        if ch == '"':
            in_quotes = not in_quotes
            current += ch
        elif ch.isspace() and not in_quotes:
            if current:
                tokens.append(current)
                current = ""
        else:
            current += ch
    if current:
        tokens.append(current)
    return tokens


def decode_trap_line(line: str) -> DecodedTrap | None:
    line = line.strip()
    if not line:
        return None
    m = _SOURCE_RE.match(line)
    if not m:
        return None
    tokens = _split_varbinds(line)
    for i, tok in enumerate(tokens):
        if tok.lstrip(".") == SNMP_TRAP_OID and i + 1 < len(tokens):
            pairs = tokens[i + 2:]
            return DecodedTrap(
                host=m.group("host"), trap_oid=tokens[i + 1].lstrip("."),
                varbinds=[pairs[j + 1] for j in range(0, len(pairs) - 1, 2)],
                received_at=datetime.now(UTC).isoformat())
    return None


def trap_to_alarm(trap: DecodedTrap, mapping: AlarmMapping) -> Alarm | None:
    """Map a decoded trap onto the same Alarm shape the pollers produce."""
    oid = trap.trap_oid
    vb = trap.varbinds

    if oid == oids.DSL_TRAP_ALARM_RAISED and len(vb) >= 8:
        # OBJECTS: alarmTID, alarmName, alarmedAID, alarmedOID, alarmDateTime,
        #          alarmServiceAffect, alarmSeverity, alarmDescription
        name, aid = vb[1].strip('"'), vb[2].strip('"')
        sa, severity_raw, description = vb[5].strip('"'), vb[6].strip('"'), vb[7].strip('"')
        sev = mapping.lookup("dsl-modem", severity_raw)
        name_row = mapping.lookup("dsl-modem", name)
        return Alarm(key=f"dsl:{aid}:{name}" if aid else f"dsl:{name}",
                     severity=Severity(sev.nsp_severity) if sev else Severity.INDETERMINATE,
                     probable_cause=name_row.nsp_probable_cause if name_row else name,
                     source_value=severity_raw, entity=aid,
                     service_affecting=(sa.upper() == "SA" if sa else None),
                     raw=description or name)

    if oid == oids.DSL_TRAP_ALARM_CLEARED and len(vb) >= 3:
        name, aid = vb[1].strip('"'), vb[2].strip('"')
        return Alarm(key=f"dsl:{aid}:{name}" if aid else f"dsl:{name}",
                     severity=Severity.CLEARED, probable_cause=name,
                     source_value="cleared", entity=aid, raw=f"{name} cleared")

    if oid in SWITCH_ALARM_TRAP_TYPES and len(vb) >= 4:
        # OBJECTS: currentAlarmSeqId, ifIndex, currentAlarmLevel,
        #          currentAlarmState, currentAlarmTime
        type_key, entity = normalise_switch_alarm_type(SWITCH_ALARM_TRAP_TYPES[oid])
        level_raw, state_raw = strip_enum_label(vb[2]), strip_enum_label(vb[3])
        cleared = "cleared" in state_raw.lower()
        level_row = mapping.lookup("switch", level_raw)
        type_row = mapping.lookup("switch", type_key)
        return Alarm(key=f"switch:{type_key}:{entity}" if entity else f"switch:{type_key}",
                     severity=(Severity.CLEARED if cleared else
                               Severity(level_row.nsp_severity) if level_row
                               else Severity.INDETERMINATE),
                     probable_cause=type_row.nsp_probable_cause if type_row else type_key,
                     source_value=level_raw, entity=entity,
                     raw=f"trap {oid} level={level_raw} state={state_raw}")

    if oid.startswith(oids.SWITCH_EVENT_TRAP_PREFIX):
        # General events carry 4 varbinds; per-port events insert ifIndex, 5.
        if len(vb) == 5:
            level_raw, message = strip_enum_label(vb[2]), vb[4].strip('"')
        elif len(vb) == 4:
            level_raw, message = strip_enum_label(vb[1]), vb[3].strip('"')
        else:
            return None
        level_row = mapping.lookup("switch", level_raw)
        return Alarm(key=f"switch-event:{oid}", severity=(
                         Severity(level_row.nsp_severity) if level_row
                         else Severity.INDETERMINATE),
                     probable_cause=message or oid, source_value=level_raw, raw=message)

    logger.debug("unrecognised trap OID %s from %s", oid, trap.host)
    return None


def run(config_path: str, db_path: str | None = None) -> None:
    """Read snmptrapd lines from stdin and apply them as alarm transitions."""
    from ..model.alarms import AlarmState
    from ..config import AppConfig
    from ..store import Store

    cfg = AppConfig.load(config_path)
    by_host = {d.target.host: d.name for d in cfg.devices}
    mapping = AlarmMapping.load()
    states: dict[str, AlarmState] = {}

    with Store(db_path or cfg.db_path) as store:
        for line in sys.stdin:
            trap = decode_trap_line(line)
            if trap is None:
                continue
            device = by_host.get(trap.host)
            if device is None:
                logger.info("trap from unknown device %s ignored", trap.host)
                continue
            alarm = trap_to_alarm(trap, mapping)
            if alarm is None:
                continue
            state = states.get(device)
            if state is None:
                state = states[device] = AlarmState()
                state.load(store.load_alarm_state(device))
            # A trap is a single-alarm observation, not a full inventory, so
            # it must not be treated as authoritative for everything else.
            transitions = _single(state, alarm)
            store.apply_transitions(device, trap.received_at, transitions, "trap")


def _single(state, alarm):
    from ..model.alarms import AlarmTransition, Transition
    prev = state.standing.get(alarm.key)
    if alarm.severity is Severity.CLEARED:
        if prev is None:
            return []
        del state.standing[alarm.key]
        return [AlarmTransition(Transition.CLEARED, alarm, prev.severity)]
    state.standing[alarm.key] = alarm
    if prev is None:
        return [AlarmTransition(Transition.RAISED, alarm)]
    if prev.severity != alarm.severity:
        return [AlarmTransition(Transition.CHANGED, alarm, prev.severity)]
    return []


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Decode snmptrapd output into alarm transitions")
    p.add_argument("--config", required=True)
    p.add_argument("--db")
    a = p.parse_args()
    logging.basicConfig(level=logging.INFO)
    run(a.config, a.db)
