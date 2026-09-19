# FCAPS parity with the Actelis EMS

Revised from `fcaps-parity-with-ems.md`. The Fault, Configuration,
Performance and Accounting analysis was sound and is kept; Security is
rewritten because its central premise was wrong, and each pillar now
distinguishes *lab-proven* from *MIB-derived* from *assumed*.

## Fault

| | ML600 family (EAD/DSL) | ML540M (switch) |
|---|---|---|
| Alarm table | `ACTELIS-ALARM-MIB` `alarmTable` (`1.3.6.1.4.1.5468.5.4`) — TL1-style: AID, severity `CR/MJ/MN/NA`, service-affecting flag | `currentAlarmTable` (`…100.1.2.2.1`) — `VTSSAlarmType` (28 values), `VTSSAlarmLevel` (2), `VTSSAlarmState` (Set/Cleared) |
| Traps | `alarmRaised` / `alarmCleared` (`…5468.5.0.1/.2`) | 13 alarm traps + 41 event traps, **all** in `ML540M-SYSTEM-MIB` |
| Trap destination | `ipv4RemoteTrapSer` / `trapOption`, SNMP-writable | `ML540M-SNMP-MIB` target config |

**Verdict: achievable.** Three caveats the original understated:

1. **Trap coverage is incomplete by design.** Link-down traps exist only for
   GE ports **1–10**, though the alarm table covers all 25. Ports 11–25 must
   be polled. Verified by counting `NOTIFICATION-TYPE` definitions across all
   57 switch MIBs — only `ML540M-SYSTEM-MIB` defines any.
2. **No feature-MIB traps at all.** ERPS, EPS, MSTP, loop protection, port
   security and CFM expose fault conditions as polled read-only status
   objects, not notifications. The Communicator must poll and diff them. (The
   original caught and corrected this itself — good.)
3. **No stable alarm identity.** `currentAlarmRowId` is a reusable slot
   number; `alarmIndex` is a table position. Correlation keys are synthesised
   locally (`model/alarms.py`). The EMS northbound MIB has a real `alarmID` —
   see ADR-0001.

The severity model is shallower than the modem's: `alm-minor(1)` /
`alm-major(2)` only — no Critical, no Warning.

## Configuration

Broadly read-write over SNMP: 164 of 290 `ML620R-MIB` objects; 2,044 of 4,527
switch objects. On the switch this is **lab-proven**, including genuine row
creation via `VTSSRowEditorState`.

* **63 row-editor tables** use the proven mechanism — VLAN, ACL (86 fields),
  EVC ECE (82), DHCP pools (45), MEP instances, IP routes, static FDB, SNMP
  users. Typed specs are generated for all of them.
* **Config backup/restore and firmware upgrade are SNMP-triggered FTP**, not
  pure SNMP: `saveConfiguration` / `loadConfigurationFile` / `ftpServerIP` on
  the modem, `ML540M-FIRMWARE-MIB` and `ML540M-ICFG-MIB` on the switch.

**Real gap** (unchanged): bulk/templated provisioning is NSP Intent Manager /
Workflow Manager work, not adaptor work.

**Added concern:** row *deletion* is a single SET with no confirmation step,
and there is no rollback path defined. See ROADMAP W6 — wire up the
FTP config backup before the first production write.

## Performance

**Verdict: achievable, and genuinely strong** — the original's assessment
holds up.

* `HDSL2-SHDSL-LINE-MIB` (RFC 4319) gives real on-device interval history:
  96×15-min + 7×1-day of ES/SES/CRC anomalies/LOSWS/UAS. Standards-based, so
  portable across any compliant NE.
* `ACTELIS-SERV-MON-MIB` adds EVC-level CFM/MEF-10.2 PM — frame loss, delay,
  delay variation, percentile availability — **but keeps only `Curr`/`Prev`**,
  one completed interval, overwritten by the next. Different collection
  strategy from the 96-bin tables, and less forgiving of a missed poll.
* The switch has Y.1731 LM/DM binned measurements.

Two additions:

* **Units are now resolved** (`docs/mib-analysis/units-resolved.md`) rather
  than flagged unknown, except the switch loss-rate scale.
* **`IF-MIB` interface counters are entirely absent from the PM mapping.**
  They are the universal PM source and NSP Performance Manager will expect
  them. See `coverage-gaps.md`.

## Security

Rewritten — see `docs/security-posture.md`. Summary: **the switch supports
SNMPv3 with USM, SHA/AES and authPriv**, all configurable over SNMP. The
original's premise that these are SNMPv2c-only devices, and that cleartext is
therefore unavoidable, is wrong for the switch and unverified for the modem.

Also standing: the read-only community discloses the read-write community on
both families, and the lab unit still answers to factory defaults.

Security MIBs remain outside the attribute schema (`AUTH` 68 objects, `USERS`
12, `PRIVILEGE` 7, `ACCESS-MANAGEMENT` 53, `SSH` 1, `HTTPS` 2, `SYSLOG` 15) —
so the "achievable" verdict on this pillar is MIB-derived, not analysed.

## Accounting

Unchanged, and the original's conclusion is right: for this platform
"Accounting" means **inventory**, not billing. Identity objects are
lab-confirmed on the switch (`productModel`, `swVersion`, `portCount`) and the
ML600 family adds `servMonSystemModel` / `servMonSWversion` / `servMonTID`.

Worth adding: **`ENTITY-MIB` (39 objects) ships in the ML600 archive and is
unanalysed.** It is the standard way NSP builds a physical equipment
hierarchy, and it is the obvious inventory source.

No usage/billing MIB exists on either family. If true accounting is required
it is a non-SNMP integration (RADIUS accounting, if the AUTH MIB's RADIUS
support includes it).

## Where the parity gap actually sits

Not in SNMP coverage. Three things, all Communicator or NSP-side:

1. **Alarm correlation and lifecycle** — no vendor-supplied stable alarm ID on
   the direct path; synthesised locally, and the EMS alternative is worth
   evaluating.
2. **PM archival cadence** — pull bins before they roll off, and handle the
   servmon `Curr`/`Prev` pair differently from the 96-bin tables.
3. **Topology** — no confirmed source. Proprietary LLDP is absent on the
   tested firmware; standard `LLDP-MIB` is untested; the EMS `topologyTable`
   exists but is unevaluated.
