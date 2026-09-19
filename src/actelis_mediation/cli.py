"""Command line entry point.

    actelis-mediation --config etc/devices.yaml poll-once
    actelis-mediation --config etc/devices.yaml poll-loop
    actelis-mediation --config etc/devices.yaml show --device lab-switch-01
    actelis-mediation --config etc/devices.yaml alarms --device lab-switch-01
    actelis-mediation verify-oids          # code OIDs vs the vendor MIBs
"""
from __future__ import annotations

import argparse
import json
import logging
import sys

from .config import AppConfig
from .poll import poll_device
from .poll.mapping import AlarmMapping, PmMapping
from .scheduler import (DEFAULT_ALARM_INTERVAL_S, DEFAULT_IDENTITY_INTERVAL_S,
                        DEFAULT_PM_INTERVAL_S, Scheduler)
from .snmp.netsnmp import NetSnmpBackend
from .store import Store

log = logging.getLogger("actelis")


def _backend(cfg: AppConfig) -> NetSnmpBackend:
    return NetSnmpBackend(community_mode=cfg.community_mode)


def cmd_poll_once(args) -> int:
    cfg = AppConfig.load(args.config)
    backend = _backend(cfg)
    am, pm = AlarmMapping.load(), PmMapping.load()
    failures = 0
    with Store(cfg.db_path) as store:
        for dev in cfg.devices:
            if args.device and dev.name != args.device:
                continue
            print(f"polling {dev.name} ({dev.device_type} @ {dev.target.host}) ...")
            try:
                result = poll_device(dev.name, backend, dev.target, dev.device_type,
                                     store, am, pm)
                print(f"  ok: {result['identity']} identity, "
                      f"{result['alarm_transitions']} alarm transition(s), "
                      f"{result['pm_samples']} PM sample(s)")
            except Exception as exc:                      # noqa: BLE001
                failures += 1
                print(f"  FAILED: {exc.__class__.__name__}: {exc}")
    return 1 if failures else 0


def cmd_poll_loop(args) -> int:
    cfg = AppConfig.load(args.config)
    backend = _backend(cfg)
    am, pm = AlarmMapping.load(), PmMapping.load()
    sched = Scheduler()
    with Store(cfg.db_path) as store:
        for dev in cfg.devices:
            def make(dev=dev, what=()):
                return lambda: poll_device(dev.name, backend, dev.target, dev.device_type,
                                           store, am, pm, what=what)
            iv = dev.intervals
            sched.add_job(f"{dev.name}-identity",
                          iv.get("identity_interval_s", DEFAULT_IDENTITY_INTERVAL_S),
                          make(what=("identity",)))
            sched.add_job(f"{dev.name}-alarms",
                          iv.get("alarm_interval_s", DEFAULT_ALARM_INTERVAL_S),
                          make(what=("alarms",)))
            sched.add_job(f"{dev.name}-pm",
                          iv.get("pm_interval_s", DEFAULT_PM_INTERVAL_S),
                          make(what=("pm",)))
        print(f"scheduled {len(sched.jobs)} jobs across {len(cfg.devices)} device(s); Ctrl-C to stop")
        try:
            sched.run_forever()
        except KeyboardInterrupt:
            sched.stop()
            print("\n" + json.dumps(sched.health(), indent=2))
    return 0


def cmd_show(args) -> int:
    cfg = AppConfig.load(args.config)
    with Store(cfg.db_path) as store:
        rows = store.recent_pm(args.device, limit=args.limit)
        if not rows:
            print(f"no PM samples recorded for {args.device}")
            return 0
        for r in rows:
            flag = "" if r["unit_verified"] else "  [UNVERIFIED UNIT]"
            value = r["value"] if r["value"] is not None else r["raw_value"]
            print(f"{r['collected_at']}  {r['metric']:44s} {str(value):>14s} "
                  f"{r['unit'] or '':<14s} [{r['bin_window']}:{r['bin_id']}] "
                  f"{r['index_key']}{flag}")
        gaps = store.capability_gaps(args.device)
        if gaps:
            print(f"\ncapability gaps recorded for {args.device}:")
            for g in gaps:
                print(f"  {g['oid']}: {g['detail'][:110]}")
    return 0


def cmd_alarms(args) -> int:
    cfg = AppConfig.load(args.config)
    with Store(cfg.db_path) as store:
        standing = store.standing_alarms(args.device)
        print(f"standing alarms on {args.device}: {len(standing)}")
        for a in standing:
            print(f"  {a['severity']:<14s} {a['alarm_key']:<46s} {a['probable_cause'] or ''}")
        print("\nrecent transitions:")
        for e in store.recent_alarm_events(args.device, limit=args.limit):
            prev = f" (was {e['previous_severity']})" if e["previous_severity"] else ""
            print(f"  {e['occurred_at']}  {e['transition']:<8s} {e['severity']:<14s}"
                  f"{prev} {e['alarm_key']}  [{e['origin']}]")
    return 0


def cmd_verify_oids(args) -> int:
    from .verify import verify_oids
    problems = verify_oids()
    if not problems:
        print("all OID constants resolve to the expected MIB objects")
        return 0
    for p in problems:
        print(f"MISMATCH {p}")
    return 1


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="actelis-mediation", description=__doc__)
    p.add_argument("--config", default="etc/devices.yaml")
    p.add_argument("-v", "--verbose", action="store_true")
    sub = p.add_subparsers(dest="command", required=True)

    once = sub.add_parser("poll-once", help="poll every device once and exit")
    once.add_argument("--device")
    once.set_defaults(func=cmd_poll_once)

    loop = sub.add_parser("poll-loop", help="poll forever on each device's intervals")
    loop.set_defaults(func=cmd_poll_loop)

    show = sub.add_parser("show", help="print recently collected PM samples")
    show.add_argument("--device", required=True)
    show.add_argument("--limit", type=int, default=20)
    show.set_defaults(func=cmd_show)

    alarms = sub.add_parser("alarms", help="standing alarms and recent transitions")
    alarms.add_argument("--device", required=True)
    alarms.add_argument("--limit", type=int, default=20)
    alarms.set_defaults(func=cmd_alarms)

    verify = sub.add_parser("verify-oids", help="check OID constants against the MIBs")
    verify.set_defaults(func=cmd_verify_oids)

    args = p.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(asctime)s %(levelname)-7s %(name)s %(message)s")
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
