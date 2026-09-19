# Roadmap — Actelis adaptors for Nokia NSP

Supersedes `build-roadmap.md`. Same Phase 0 / Phase 1 spine, because that
split was right, with the sequencing corrected and the workstreams the
original did not identify added.

---

## What actually gates what

The original framed everything as "Phase 0 = doable now, Phase 1 = blocked on
NSP/SDK access". That is mostly true but it hid three things:

1. **Some "done" Phase 0 work will need redoing once NSP schema constraints
   are known** — specifically attribute *naming* and the flat `nsp_metric_name`
   convention, which were invented locally. That is fine, but it should be
   planned as rework rather than discovered as rework.
2. **Some work described as blocked is not.** The DSL `alarmName` catalogue
   and the servmon units were both called "needs a lab unit or Actelis";
   the units were in the MIB all along (F-08), and the model-scope question
   is answered by the `Models` enum.
3. **The single highest-value unblocked action is not on the roadmap at all**
   — running the existing code against the lab switch that is already
   reachable. Everything in the Communicator is unit-tested against canned
   data and has never touched hardware.

---

## Now — highest value per hour, nothing blocked

### N1 · Run the Communicator against the lab ML540M  ⏱ ~1 hour
Still the biggest single gap. `poll-once` has never been executed against
`192.168.1.99`. Every OID is verified against the MIBs, so this is about
agent behaviour, not correctness of the numbers: response formats, walk
durations, whether `snmpbulkwalk` is accepted, whether the PM tables are
populated at all on this firmware.

```bash
export LAB_SWITCH_RO=... LAB_SWITCH_RW=...
actelis-mediation --config etc/devices.yaml poll-once --device lab-switch-01
actelis-mediation --config etc/devices.yaml alarms  --device lab-switch-01
```

### N2 · Walk the *standard* LLDP-MIB on the switch  ⏱ 5 minutes
Retires or confirms the flagged topology risk (F-07). The proprietary branch
returned `No Such Object`; the standard MIB was never tried.

```bash
snmpwalk -v2c -c "$LAB_SWITCH_RO" -On 192.168.1.99 1.0.8802.1.1.2.1.4   # lldpRemTable
```

### N3 · Capture one real trap  ⏱ ~20 minutes
The trap decoder has never seen a real payload — the one part of the original
honestly labelled a sketch, and still the least-evidenced component. Admin-
down a port with `snmptrapd -Lo -On -f -Oq` running and keep the raw line as
a fixture. Procedure in `docs/testing-strategy.md`.

### N4 · Decide the device-type scoping question from evidence  ⏱ ~2 hours
The `Models` enum (F-08) says ML622 and ML684 are ML600-family. Confirm by
reading `servMonSystemModel` off any reachable unit, then settle: **two NSP
device types (ML600 family, ML540M switch) with model variants**, not four
adaptors. This changes the shape of the Nokia conversation, so do it before
that meeting.

### N5 · Close the MIB coverage gaps that matter  ⏱ ~1 day
Not all 3,600 unanalysed objects — the ones with a consumer
(`docs/mib-analysis/coverage-gaps.md` prioritises):
`ML540M-MEP-MIB` (the alarm mapping already cites it), `ENTITY-MIB` +
`IF-MIB` on the DSL side (NSP inventory and interface PM), `ML540M-DDMI-MIB`
(optical thresholds), and a triage pass on `FTTN-MIB`'s 521 objects to
determine whether it is the modem's real provisioning surface.

### N6 · Harden the lab unit's SNMP, and prove SNMPv3 works  ⏱ ~2 hours
Factory `public`/`private` are live on a unit that already holds a write
community. Change them, restrict via `ml540mSnmpConfigCommunityTable` (using
the row-editor helper — a genuinely useful first production use), then
configure a USM user and confirm SNMPv3 authPriv end to end (F-04). If it
works, the security posture for the whole switch estate changes.

---

## Next — before or alongside NSP access

### X1 · Send the vendor questions
Both docs are rewritten: `docs/vendor-questions/actelis.md` drops the two
questions now answered and sharpens the rest;
`docs/vendor-questions/nokia.md` drops the incorrect SNMPv3 premise and leads
with the access ask. **Send the Nokia one this week** — Developer Portal
enrolment is the long pole and is pure calendar time.

### X2 · Structure the Nokia conversation as co-development, not support
Actelis is not a family Nokia ships adaptors for, so this is either
co-development or solo build against the SDK. Go in with: the attribute
schema, the mapping tables, the proven row-editor protocol, and this working
prototype. That reframes it from "help us learn" to "review our model" — a
different and much faster conversation. Ask specifically for a **reference
SNMP-only adaptor** to read; one worked example is worth more than the
documentation set.

### X3 · Build a device simulator  ⏱ ~2 days
The highest-leverage thing not on the original roadmap. There is one lab
switch, no modem, and an unknown wait for NSP access. A simulator — a
`snmpsim`-style agent seeded from the OID maps and the real lab captures —
gives: a reachable ML600-family device before one exists; repeatable CI
against an "agent"; the ability to test failure modes (a stuck row editor, a
bin rolling over mid-poll, a subtree returning `No Such Object`) that cannot
be provoked on demand on real hardware. The repo already has everything
needed to seed it.

### X4 · Prepare the Device Model port as a mechanical transform
Step 7 is "port the attribute mapping into NSP's schema… should be fast if
step 1 was done properly". Make that literal: keep the schema as data and
write the emitter once the target format is known, rather than hand-porting
2,000 rows. Budget for the naming convention to change.

### X5 · Settle PM archival semantics before writing the PM path
The modem's servmon counters keep only `Curr`/`Prev` — one completed
interval, overwritten by the next. HDSL2-SHDSL keeps 96×15min + 7×1day.
Those need different collection strategies, and NSP Performance Manager will
have opinions about which timestamps it wants. Resolve with Nokia (question
13/14) before implementing, not after.

---

## Phase 1 — once NSP/SDK access exists

Unchanged in shape from the original; sequencing sharpened.

6. **SDK training** — Device Model + Communicator, discovery adaptors, MDC.
7. **Device Model per device type** — two, not four (N4). Emit from the
   schema (X4).
8. **Discovery adaptor, smallest milestone** — switch first: `productModel` /
   `swVersion` / `portCount` are lab-confirmed and make ready-made fixtures.
   For the ML600 family, discover the variant from `servMonSystemModel`.
9. **Communicator** — layer in order: live status → alarms → PM → config push.
   The data-fetch logic ports from `src/actelis_mediation/` largely intact;
   `snmp/backend.py` is the seam where the NSP SDK's SNMP stack replaces
   net-snmp.
10. **Config push and row creation** — implementation, not discovery. 63
    generated specs are ready. Resolve the clustering question first
    (`docs/adr/0004-row-editor-concurrency.md`).
11. **FCAPS validation** — `docs/fcaps-parity.md` as the acceptance checklist.

---

## Workstreams the original did not identify

### W1 · Firmware and MIB drift as a standing process
The estate will not run one firmware. `00.00.16` already lacks an entire LLDP
subtree; production units will differ. Two mechanisms now exist and should be
kept running: `capability_gaps` records per-device what an agent does not
implement, and `tests/test_mib_conformance.py` fails the build when a vendor
MIB revision moves an object or changes an index. Add: a per-firmware
capability matrix, populated from the first production walk.
See `docs/firmware-mib-drift.md`.

### W2 · Alarm lifecycle and NSP resynchronisation
Beyond mapping severities: what happens when the Communicator restarts, or
misses a trap, or the device reboots and renumbers `currentAlarmRowId`? The
state machine here handles restart and full-poll reconciliation, but NSP has
its own resync expectations. Needs to be an explicit question to Nokia.

### W3 · Scale and collection budget
Nothing in the project states the target device count. It determines almost
every design decision: 20 devices is a loop, 2,000 is a distributed collector
with connection pooling. Walking the full HDSL2-SHDSL interval set per modem
is tens of thousands of varbinds. Get the number, then measure one device
(N1 gives the data) and multiply.

### W4 · Security review before production
`docs/security-posture.md`: SNMPv3 migration for the switch, credential
handling, the write-community bootstrap pattern (convenient, and a finding in
its own right — a read-only community discloses the write community), and
whether NSP provisions device AAA at all.

### W5 · Operational readiness
The prototype logs and stores; a production Communicator needs health
endpoints, metrics (poll duration, failure rate, per-device reachability),
and alerting on collection failure. Partly seeded by `Scheduler.health()`.

### W6 · Rollback and blast radius for config push
Row creation is proven; row *deletion* is one SNMP SET with no confirmation
step. Before NSP drives this against production: what is the rollback path,
what does a failed multi-field stage leave behind, and how is a bulk change
staged? `saveConfiguration` / `loadConfigurationFile` via FTP exist on the
modem — that is the backup hook, and it should be wired in before the first
production write.
