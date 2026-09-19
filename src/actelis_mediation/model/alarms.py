"""Alarm normalisation and state tracking.

The original prototype treated every alarm poll as a fresh list of events and
inserted all of them. With the documented 60-second alarm interval, one
standing alarm becomes 1,440 identical rows per day, there is no clear event
when it goes away, and nothing downstream can tell a new alarm from one that
has been up for a week.

NSP Fault Management -- like any X.733-style fault system -- consumes alarm
*state transitions*: raised, changed, cleared. So this module keeps a keyed
view of what is currently standing and emits only transitions.

The switch's ``currentAlarmTable`` carries ``currentAlarmState``
(``VTSSAlarmState ::= INTEGER { alm-Set(1), alm-Cleared(2) }``), which the
original read into a free-text description field but never acted on: a row in
the ``alm-Cleared`` state was still recorded at its alarm severity. Here a
cleared row maps to severity ``Cleared``, matching what the trap path already
did -- the poll and trap paths now agree.

Severity vocabulary is the industry-standard X.733 set
(Critical/Major/Minor/Warning/Indeterminate/Cleared) that the mapping tables
were built against. It is still NOT confirmed against NSP's own enum -- that
remains an open question for Nokia -- so it is defined in one place here for a
single-point swap once confirmed.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from collections.abc import Iterable


class Severity(str, Enum):  # noqa: UP042 - str+Enum keeps 3.11 compat
    CRITICAL = "Critical"
    MAJOR = "Major"
    MINOR = "Minor"
    WARNING = "Warning"
    INDETERMINATE = "Indeterminate"
    CLEARED = "Cleared"


class Transition(str, Enum):  # noqa: UP042
    RAISED = "raised"
    CHANGED = "changed"
    CLEARED = "cleared"


@dataclass(frozen=True)
class Alarm:
    """One alarm as observed on a device at a point in time.

    ``key`` must identify the same fault across polls. For the switch that is
    the alarm type plus the entity it is raised against (NOT the table row id,
    which is a volatile slot number); for the DSL modem it is the TL1 AID plus
    the alarm name.
    """
    key: str
    severity: Severity
    probable_cause: str
    source_value: str
    entity: str = ""
    service_affecting: bool | None = None
    raw: str = ""
    confidence: str = ""

    def is_clear(self) -> bool:
        return self.severity is Severity.CLEARED


@dataclass(frozen=True)
class AlarmTransition:
    transition: Transition
    alarm: Alarm
    previous_severity: Severity | None = None


@dataclass
class AlarmState:
    """Tracks standing alarms per device and emits transitions.

    Deliberately a plain in-memory dict rebuilt from the store on startup, so
    a restart does not replay every standing alarm as newly raised.
    """
    standing: dict[str, Alarm] = field(default_factory=dict)

    def reconcile(self, observed: Iterable[Alarm]) -> list[AlarmTransition]:
        """Diff a full poll result against what is currently standing.

        A full poll is authoritative: anything previously standing that is
        absent from ``observed`` has gone away and is emitted as cleared.
        """
        out: list[AlarmTransition] = []
        seen: dict[str, Alarm] = {}

        for alarm in observed:
            if alarm.is_clear():
                prev = self.standing.pop(alarm.key, None)
                if prev is not None:
                    out.append(AlarmTransition(Transition.CLEARED, alarm, prev.severity))
                continue
            seen[alarm.key] = alarm
            prev = self.standing.get(alarm.key)
            if prev is None:
                out.append(AlarmTransition(Transition.RAISED, alarm))
            elif (prev.severity != alarm.severity
                  or prev.probable_cause != alarm.probable_cause):
                out.append(AlarmTransition(Transition.CHANGED, alarm, prev.severity))

        for key, prev in list(self.standing.items()):
            if key not in seen:
                cleared = Alarm(key=key, severity=Severity.CLEARED,
                                probable_cause=prev.probable_cause,
                                source_value=prev.source_value, entity=prev.entity,
                                raw="no longer present in the device alarm table")
                out.append(AlarmTransition(Transition.CLEARED, cleared, prev.severity))
                del self.standing[key]

        self.standing.update(seen)
        return out

    def load(self, alarms: Iterable[Alarm]) -> None:
        self.standing = {a.key: a for a in alarms if not a.is_clear()}


# --- source-value normalisation --------------------------------------------

# VTSSAlarmType has one enum value per port (alarmGEPort1LinkDown(101) ..
# alarmGEPort25LinkDown(125)). The mapping CSV collapses those 25 rows into
# one generalised row, so a per-port value is folded onto it before lookup --
# but the port number is preserved as the alarm's entity, which is what makes
# the alarm key stable and per-port.
import re  # noqa: E402

_GE_PORT_LINK_DOWN = re.compile(r"^alarmGEPort(?P<port>\d+)LinkDown\((?P<num>\d+)\)$")
GE_PORT_LINK_DOWN_ROW = "alarmGEPortNLinkDown(101-125)"


def normalise_switch_alarm_type(value: str) -> tuple[str, str]:
    """Return (mapping-table key, entity). Entity is '' when not per-port."""
    m = _GE_PORT_LINK_DOWN.match(value.strip())
    if m:
        return GE_PORT_LINK_DOWN_ROW, f"GigabitEthernet {m.group('port')}"
    return value.strip(), ""


def strip_enum_label(raw: str) -> str:
    """'INTEGER: alm-major(2)' -> 'alm-major(2)'."""
    v = (raw or "").strip()
    if ":" in v:
        v = v.split(":", 1)[1].strip()
    return v.strip('"')


SWITCH_ALARM_STATE_CLEARED = {"alm-Cleared(2)", "alm-Cleared", "2"}
