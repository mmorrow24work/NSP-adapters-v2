"""Loads the MIB-grounded alarm/PM mapping tables.

These CSVs are among the most valuable artefacts in the original project --
built from vendor MIB text with an explicit confirmed/inferred flag per row --
and are carried over unchanged in content.

The original's real latent bug is kept fixed and made the default: indexing
alarm rows by ``(device_type, source_value)`` alone collides for the ~20
switch fault-status rows that all use ``source_value="TRUE"`` (a plain
TruthValue), so only the last one loaded was findable. Both indexes are kept,
but ``lookup_by_object`` is now the recommended call and ``lookup`` warns when
it resolves an ambiguous key.
"""
from __future__ import annotations

import csv
import logging
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[3]
DATA = REPO_ROOT / "data" / "mapping-tables"
ALARM_CSV = DATA / "alarm-severity-mapping.csv"
PM_CSV = DATA / "pm-counter-mapping.csv"


@dataclass(frozen=True)
class AlarmMappingRow:
    device_type: str
    source_mib_object: str
    source_value: str
    source_meaning: str
    nsp_severity: str
    nsp_probable_cause: str
    service_affecting: str
    confidence: str
    notes: str


@dataclass(frozen=True)
class PmMappingRow:
    device_type: str
    source_mib_object: str
    source_mib: str
    bin_window: str
    raw_unit: str
    nsp_metric_name: str
    nsp_unit: str
    aggregation: str
    polling_note: str


def bare_object_name(source_mib_object: str) -> str:
    """'ml540mErpsStatusFopAlarm (TruthValue, ML540M-ERPS-MIB)' -> bare name."""
    return source_mib_object.split(" (", 1)[0].strip()


def _load(path: Path, row_cls):
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found -- run tools/build_alarm_pm_mapping.py first")
    with open(path, newline="", encoding="utf-8") as fh:
        return [row_cls(**rec) for rec in csv.DictReader(fh)]


class AlarmMapping:
    def __init__(self, rows: list[AlarmMappingRow] | None = None):
        self.rows = rows if rows is not None else _load(ALARM_CSV, AlarmMappingRow)
        self._by_value: dict[tuple[str, str], AlarmMappingRow] = {}
        self._ambiguous: set[tuple[str, str]] = set()
        self._by_object: dict[tuple[str, str, str], AlarmMappingRow] = {}
        for r in self.rows:
            key = (r.device_type, r.source_value)
            if key in self._by_value:
                self._ambiguous.add(key)
            else:
                self._by_value[key] = r
            self._by_object[(r.device_type, bare_object_name(r.source_mib_object),
                             r.source_value)] = r

    @classmethod
    def load(cls) -> AlarmMapping:
        return cls()

    def lookup(self, device_type: str, source_value: str) -> AlarmMappingRow | None:
        key = (device_type, source_value)
        if key in self._ambiguous:
            logger.warning(
                "alarm mapping: %r is ambiguous for %s (%d rows share it, e.g. plain "
                "TruthValue status flags) -- use lookup_by_object()",
                source_value, device_type,
                sum(1 for r in self.rows if (r.device_type, r.source_value) == key))
        return self._by_value.get(key)

    def lookup_by_object(self, device_type: str, mib_object: str,
                         source_value: str) -> AlarmMappingRow | None:
        return self._by_object.get((device_type, bare_object_name(mib_object), source_value))

    @property
    def ambiguous_values(self) -> set[tuple[str, str]]:
        return set(self._ambiguous)


class PmMapping:
    def __init__(self, rows: list[PmMappingRow] | None = None):
        self.rows = rows if rows is not None else _load(PM_CSV, PmMappingRow)
        self._by_object = {(r.device_type, bare_object_name(r.source_mib_object)): r
                           for r in self.rows}

    @classmethod
    def load(cls) -> PmMapping:
        return cls()

    def lookup(self, device_type: str, source_mib_object: str) -> PmMappingRow | None:
        return self._by_object.get((device_type, bare_object_name(source_mib_object)))

    def metrics_for(self, device_type: str) -> list[PmMappingRow]:
        return [r for r in self.rows if r.device_type == device_type]
