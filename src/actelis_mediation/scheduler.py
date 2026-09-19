"""Drift-corrected interval scheduler.

The original design was sound and is kept: schedule from the intended time
rather than from completion, so a slow poll does not compound into drift.
Added here: per-job health (consecutive failures, last error), so an
unreachable device is visible rather than just noisy in the log, and
exponential backoff of a job that keeps failing so a dead device does not get
hammered every 60 seconds forever.

Default intervals still beat the device-side rollover windows:
  PM 5 min       -- 3x inside the 15-minute bin; also inside the modem's
                    ACTELIS-SERV-MON-MIB Curr/Prev pair, which keeps only one
                    completed interval and overwrites it.
  alarms 60 s    -- until traps are proven, polling is the primary fault path.
  identity 30 min
"""
from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from collections.abc import Callable

logger = logging.getLogger(__name__)

DEFAULT_PM_INTERVAL_S = 5 * 60
DEFAULT_ALARM_INTERVAL_S = 60
DEFAULT_IDENTITY_INTERVAL_S = 30 * 60
MAX_BACKOFF_MULTIPLIER = 16


@dataclass
class ScheduledJob:
    name: str
    interval_s: float
    fn: Callable[[], None]
    consecutive_failures: int = 0
    last_error: str = ""
    last_success: float | None = None
    runs: int = 0
    _next_run: float = field(default=0.0, repr=False)

    def due(self, now: float) -> bool:
        return now >= self._next_run

    def run_and_reschedule(self, now: float) -> None:
        self.runs += 1
        try:
            self.fn()
            self.consecutive_failures = 0
            self.last_error = ""
            self.last_success = now
            delay = self.interval_s
        except Exception as exc:                        # noqa: BLE001
            self.consecutive_failures += 1
            self.last_error = f"{exc.__class__.__name__}: {exc}"
            logger.warning("job %s failed (%d consecutive): %s",
                           self.name, self.consecutive_failures, exc)
            mult = min(2 ** min(self.consecutive_failures, 4), MAX_BACKOFF_MULTIPLIER)
            delay = self.interval_s * mult
        self._next_run = max(now, self._next_run) + delay


class Scheduler:
    def __init__(self, tick_s: float = 1.0):
        self.tick_s = tick_s
        self.jobs: list[ScheduledJob] = []
        self._stop = threading.Event()

    def add_job(self, name: str, interval_s: float, fn: Callable[[], None]) -> ScheduledJob:
        job = ScheduledJob(name=name, interval_s=interval_s, fn=fn)
        self.jobs.append(job)
        return job

    def run_once_all(self) -> None:
        now = time.monotonic()
        for job in self.jobs:
            job.run_and_reschedule(now)

    def run_forever(self) -> None:
        now = time.monotonic()
        for job in self.jobs:
            job._next_run = now
        while not self._stop.is_set():
            now = time.monotonic()
            for job in self.jobs:
                if job.due(now):
                    job.run_and_reschedule(now)
            self._stop.wait(self.tick_s)

    def health(self) -> list[dict]:
        return [{"job": j.name, "runs": j.runs,
                 "consecutive_failures": j.consecutive_failures,
                 "last_error": j.last_error} for j in self.jobs]

    def stop(self) -> None:
        self._stop.set()
