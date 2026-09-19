"""SQLite persistence.

Two defects in the original schema are fixed here.

1. **PM samples had no identity.** A row recorded only the metric name, value
   and a ``bin_window`` string -- not which port, endpoint side, wire pair or
   bin number it came from. For a job whose entire purpose is "archive the
   device's interval bins before they roll off", that makes the archive
   unusable: 96 bins x ports x wire pairs all collapse into
   indistinguishable rows. ``pm_samples`` now carries the decoded index.

2. **Re-polling duplicated everything.** The HDSL2-SHDSL table holds 24h of
   15-minute bins; polling every 5 minutes re-read all 96 and inserted all 96
   again, ~288 copies of each bin per day. A UNIQUE constraint on the bin's
   real identity plus INSERT ... ON CONFLICT makes re-polling idempotent, so
   the poll interval can be set for safety (beat the rollover) without
   inflating the archive.

Alarms are stored as state plus transitions rather than as a stream of
repeated observations -- see model/alarms.py.
"""
from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from collections.abc import Iterable

from ..model.alarms import Alarm, AlarmTransition, Severity

SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS devices (
    name         TEXT PRIMARY KEY,
    device_type  TEXT NOT NULL,
    host         TEXT NOT NULL,
    first_seen   TEXT NOT NULL,
    last_polled  TEXT
);

CREATE TABLE IF NOT EXISTS identity_samples (
    device_name  TEXT NOT NULL REFERENCES devices(name),
    collected_at TEXT NOT NULL,
    attribute    TEXT NOT NULL,
    value        TEXT,
    PRIMARY KEY (device_name, attribute, value)
);

-- One row per (device, metric, table row, bin). Re-polling the same bin is a
-- no-op rather than a duplicate.
CREATE TABLE IF NOT EXISTS pm_samples (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    device_name      TEXT NOT NULL REFERENCES devices(name),
    collected_at     TEXT NOT NULL,
    metric           TEXT NOT NULL,
    source_object    TEXT NOT NULL,
    index_key        TEXT NOT NULL,   -- canonical decoded index, e.g. ifIndex=101;wirePair=1
    index_json       TEXT NOT NULL,   -- full decoded index for querying
    bin_window       TEXT NOT NULL,   -- '15min' | '1day' | 'evc-lm' | 'evc-dm' | 'current'
    bin_id           TEXT NOT NULL,   -- interval number / interval id ('' if not binned)
    raw_value        TEXT,
    value            REAL,            -- scaled
    unit             TEXT,
    unit_verified    INTEGER NOT NULL DEFAULT 1,
    UNIQUE (device_name, source_object, index_key, bin_window, bin_id)
);

CREATE TABLE IF NOT EXISTS alarm_state (
    device_name     TEXT NOT NULL REFERENCES devices(name),
    alarm_key       TEXT NOT NULL,
    severity        TEXT NOT NULL,
    probable_cause  TEXT,
    entity          TEXT,
    source_value    TEXT,
    raised_at       TEXT NOT NULL,
    last_seen_at    TEXT NOT NULL,
    PRIMARY KEY (device_name, alarm_key)
);

CREATE TABLE IF NOT EXISTS alarm_events (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    device_name       TEXT NOT NULL REFERENCES devices(name),
    occurred_at       TEXT NOT NULL,
    transition        TEXT NOT NULL,   -- raised | changed | cleared
    alarm_key         TEXT NOT NULL,
    severity          TEXT NOT NULL,
    previous_severity TEXT,
    probable_cause    TEXT,
    entity            TEXT,
    source_value      TEXT,
    origin            TEXT NOT NULL,   -- poll | trap
    raw               TEXT
);

-- Capability gaps: an OID the agent does not implement. Recorded once rather
-- than re-logged every cycle (the ML540M fw 00.00.16 LLDP case).
CREATE TABLE IF NOT EXISTS capability_gaps (
    device_name  TEXT NOT NULL REFERENCES devices(name),
    oid          TEXT NOT NULL,
    detail       TEXT,
    first_seen   TEXT NOT NULL,
    last_seen    TEXT NOT NULL,
    PRIMARY KEY (device_name, oid)
);

CREATE INDEX IF NOT EXISTS idx_pm_device_metric ON pm_samples (device_name, metric, bin_window);
CREATE INDEX IF NOT EXISTS idx_alarm_events_device ON alarm_events (device_name, occurred_at);
"""


class Store:
    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path))
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(SCHEMA)
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> Store:
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    @contextmanager
    def _tx(self):
        cur = self._conn.cursor()
        try:
            yield cur
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            raise
        finally:
            cur.close()

    # -- devices ------------------------------------------------------------

    def upsert_device(self, name: str, device_type: str, host: str, now: str) -> None:
        with self._tx() as cur:
            cur.execute(
                "INSERT INTO devices (name, device_type, host, first_seen, last_polled) "
                "VALUES (?,?,?,?,?) ON CONFLICT(name) DO UPDATE SET "
                "device_type=excluded.device_type, host=excluded.host, "
                "last_polled=excluded.last_polled",
                (name, device_type, host, now, now))

    def record_identity(self, device: str, now: str, attributes: dict[str, str]) -> None:
        with self._tx() as cur:
            cur.executemany(
                "INSERT INTO identity_samples (device_name, collected_at, attribute, value) "
                "VALUES (?,?,?,?) ON CONFLICT DO NOTHING",
                [(device, now, k, v) for k, v in attributes.items()])

    # -- PM -----------------------------------------------------------------

    def record_pm(self, device: str, samples: Iterable[dict]) -> int:
        rows = [(device, s["collected_at"], s["metric"], s["source_object"],
                 s["index_key"], json.dumps(s.get("index", {}), sort_keys=True),
                 s["bin_window"], str(s.get("bin_id", "")), s.get("raw_value"),
                 s.get("value"), s.get("unit", ""), 1 if s.get("unit_verified", True) else 0)
                for s in samples]
        if not rows:
            return 0
        with self._tx() as cur:
            cur.executemany(
                "INSERT INTO pm_samples (device_name, collected_at, metric, source_object,"
                " index_key, index_json, bin_window, bin_id, raw_value, value, unit,"
                " unit_verified) VALUES (?,?,?,?,?,?,?,?,?,?,?,?) "
                "ON CONFLICT (device_name, source_object, index_key, bin_window, bin_id) "
                "DO NOTHING", rows)
            return cur.rowcount

    # -- alarms -------------------------------------------------------------

    def load_alarm_state(self, device: str) -> list[Alarm]:
        cur = self._conn.execute(
            "SELECT alarm_key, severity, probable_cause, entity, source_value "
            "FROM alarm_state WHERE device_name=?", (device,))
        return [Alarm(key=r["alarm_key"], severity=Severity(r["severity"]),
                      probable_cause=r["probable_cause"] or "", entity=r["entity"] or "",
                      source_value=r["source_value"] or "") for r in cur.fetchall()]

    def apply_transitions(self, device: str, now: str,
                          transitions: Iterable[AlarmTransition],
                          origin: str = "poll") -> int:
        n = 0
        with self._tx() as cur:
            for t in transitions:
                a = t.alarm
                cur.execute(
                    "INSERT INTO alarm_events (device_name, occurred_at, transition,"
                    " alarm_key, severity, previous_severity, probable_cause, entity,"
                    " source_value, origin, raw) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (device, now, t.transition.value, a.key, a.severity.value,
                     t.previous_severity.value if t.previous_severity else None,
                     a.probable_cause, a.entity, a.source_value, origin, a.raw))
                if t.transition.value == "cleared":
                    cur.execute("DELETE FROM alarm_state WHERE device_name=? AND alarm_key=?",
                                (device, a.key))
                else:
                    cur.execute(
                        "INSERT INTO alarm_state (device_name, alarm_key, severity,"
                        " probable_cause, entity, source_value, raised_at, last_seen_at)"
                        " VALUES (?,?,?,?,?,?,?,?) ON CONFLICT(device_name, alarm_key) DO UPDATE"
                        " SET severity=excluded.severity, probable_cause=excluded.probable_cause,"
                        " last_seen_at=excluded.last_seen_at",
                        (device, a.key, a.severity.value, a.probable_cause, a.entity,
                         a.source_value, now, now))
                n += 1
        return n

    # -- capability gaps ----------------------------------------------------

    def record_capability_gap(self, device: str, oid: str, detail: str, now: str) -> None:
        with self._tx() as cur:
            cur.execute(
                "INSERT INTO capability_gaps (device_name, oid, detail, first_seen, last_seen)"
                " VALUES (?,?,?,?,?) ON CONFLICT(device_name, oid) DO UPDATE SET"
                " last_seen=excluded.last_seen", (device, oid, detail, now, now))

    # -- read-side ----------------------------------------------------------

    def recent_pm(self, device: str, limit: int = 20) -> list[sqlite3.Row]:
        return self._conn.execute(
            "SELECT * FROM pm_samples WHERE device_name=? ORDER BY id DESC LIMIT ?",
            (device, limit)).fetchall()

    def standing_alarms(self, device: str) -> list[sqlite3.Row]:
        return self._conn.execute(
            "SELECT * FROM alarm_state WHERE device_name=? ORDER BY severity, alarm_key",
            (device,)).fetchall()

    def recent_alarm_events(self, device: str, limit: int = 20) -> list[sqlite3.Row]:
        return self._conn.execute(
            "SELECT * FROM alarm_events WHERE device_name=? ORDER BY id DESC LIMIT ?",
            (device, limit)).fetchall()

    def capability_gaps(self, device: str) -> list[sqlite3.Row]:
        return self._conn.execute(
            "SELECT * FROM capability_gaps WHERE device_name=?", (device,)).fetchall()
