# ACTELIS-SERV-MON-MIB Parse-Error Root Cause & Recovery

**Purpose:** closes the open item from `build-roadmap.md` item 2 ("manually
review `ACTELIS-SERV-MON-MIB.mib`'s parse errors"). Short version: it
wasn't a broken vendor file needing a rewrite — two fixable issues, both
now understood, and 163 previously-inaccessible objects have been
recovered as a result. See `data/oid-maps/dsl-modem/actelis_servmon_oid_map.csv`
for the recovered objects and `docs/mib-analysis/units-resolved.md` /
`data/mapping-tables/pm-counter-mapping.csv` for how the PM-relevant subset
feeds into the alarm/PM mapping (28 new rows added there).

## What this MIB is

Per its own `DESCRIPTION`: Actelis system-model identification, port/EVC
throughput monitoring, and **802.1ag CFM (Connectivity Fault Management) +
MEF10.2-based EVC performance monitoring** — frame loss (FL/FLR), frame
delay and delay variation (FD/FDV), and MEF10.2 percentile-based
availability/performance metrics, all per-MEP (Maintenance Entity Point).
This is a materially different — and in some ways richer — PM dataset than
the HDSL2-SHDSL line counters already mapped: it's EVC/service-level, not
line-level, and it's the modem-side counterpart to the switch's Y.1731
LM/DM measurements already in the PM mapping.

## Root cause 1: unresolved cross-MIB import (severity 1, the abort trigger)

```
ACTELIS-SERV-MON-MIB.mib:17: [1] failed to locate MIB module `IEEE8021-CFM-MIB'
```

The MIB imports six types/objects from `IEEE8021-CFM-MIB` (the standard
IEEE 802.1ag CFM MIB — `dot1agCfmMdIndex`, `dot1agCfmMepId`, etc.). That
file **is** present in the same vendor archive
(`mibs/actelis/ML600_MIB.7z` → `IEEE8021-CFM-MIB.mib`) — this was never a
missing dependency, just `smidump`'s default search path not including
it. Passing it explicitly as a second module (`-p` flag) resolves every
downstream "unknown object identifier label" / "unknown type" error that
cascaded from this one root cause (12 of the 14 severity-1/2 errors
`smilint` reported were this cascade, not independent bugs).

## Root cause 2: one genuine vendor authoring bug (severity 2)

```
ACTELIS-SERV-MON-MIB.mib:1133: [2] subidentifier of row node `servMonMEPLossFLFLR1DayELANEntry' must be 1
```

SMIv2 requires a table's `...Entry` object to be subidentifier `1` under
its `...Table` (the row is always the table's first and only child in the
naming tree). Line 1133 has:

```
::= { servMonMEPLossFLFLR1DayELANTable 2 }
```

— a `2` instead of `1`, almost certainly copy-pasted from a neighboring
table definition without updating the trailing index. This is the one
object in the whole MIB with this bug (confirmed by re-running `smilint`
against every other table in the file — no other instances). Locally
correcting this single line, on top of fixing root cause 1, produces a
**clean parse with zero errors or warnings beyond routine metadata
warnings** (revision-order nitpicks, hyphens in enum labels — cosmetic,
not structural).

## What this means for the vendor file

This is not a request to Actelis to fix anything urgent — the bug affects
exactly one table's *tooling-visible* OID structure, not the device's
actual SNMP behavior (the live device's agent presumably implements the
correct `.../1/...` OID regardless of what this MIB source line says,
since the file compiles and ships as-is). Worth flagging to Actelis if a
support channel is used for other reasons, but not vendor-support-worthy
on its own.

## What was recovered

163 objects, extracted via `smidump -f python` against a locally-patched
copy (the one-line fix above; the original vendor file is untouched in
`mibs/actelis/`) with `IEEE8021-CFM-MIB.mib` passed as an explicit import
path. Categories:

- System identity (`servMonSystemModel`, `servMonSystemSWversion`,
  `servMonSystemTID`) — redundant with objects already in the main OID
  map, included for completeness.
- Port/EVC bandwidth and utilization (`portEgressBW`, `evcConfBWProfile*`,
  policy-discard counters).
- **Frame loss (FL/FLR)** per MEP, both E-Line (point-to-point:
  ingress/egress) and E-LAN (point-to-multipoint: near-end/far-end)
  variants, at 15-min and 1-day granularity.
- **Frame delay/delay-variation (FD/FDV)** per MEP — E-LAN only (no E-Line
  variant exists in this MIB), same two granularities.
- **MEF10.2 percentile performance metrics**
  (`ServiceAvailability`/`OnewayFLRPerformance`/`OnewayFDPerformance`/
  `OnewayIFDVPerformance`) — the standards-based summary numbers that sit
  on top of the raw FL/FD counters, likely the most directly
  EMS-comparable PM data on the modem side.

## Important operational difference from HDSL2-SHDSL

The HDSL2-SHDSL interval tables (already mapped) keep a genuine rolling
history: 96×15-min bins (24h) and 7×1-day bins (a week). **This MIB does
not** — every counter here only has a `Curr` (in-progress partial
interval) and a single `Prev` (the most recently completed interval, one
generation of history, not a table). If the Communicator doesn't poll
faster than the interval length, a completed interval's data is
overwritten by the next one before it's ever read — there's no 96-bin
buffer to fall back on. This is called out per-row in
`pm-counter-mapping.csv`'s `polling_note` column.

## Independently verified in review (2026-09-19)

Both root causes above were reproduced with a second, independently-written
SMIv2 parser (`tools/mibscan.py`, not `smidump`): the `IEEE8021-CFM-MIB`
import is present in the same archive, and a scan of every `...Entry` object
in the file found **exactly one** sub-identifier violation — the one named
here. This analysis is correct and precise.

One item below is now closed, and one is sharpened.

## Still open

- **Units for FLR/FD/FDV/MEF10.2 percentiles aren't stated in the SNMP
  `SYNTAX`** (plain `Unsigned32` throughout) — flagged `unconfirmed` in
  the PM mapping rather than guessed. Needs either a live modem or
  Actelis's own MEF10.2 configuration/reporting documentation to pin down
  scale (e.g. is `OnewayFDPerformance` in microseconds, milliseconds, or
  something else).
- Not yet validated against a live ML600-family unit — same blocker as the
  rest of the DSL side.
- **Which OID does the agent actually use for the mis-numbered table?** The
  MIB source says `...Table.2`; SMIv2 says it must be `...Table.1`. A poller
  built from the corrected file walks `.1` and would silently collect nothing
  if the agent follows its own MIB. Two `snmpwalk`s settle it on the first
  available unit — now question 11 in
  [`../vendor-questions/actelis.md`](../vendor-questions/actelis.md).
- The recovered `dot1agCfmMepId`-typed columns (from the now-resolved
  `IEEE8021-CFM-MIB` import) aren't independently added to the attribute
  schema as their own textual-convention type beyond what
  `build_attribute_schema.py`'s existing normalization already does — they
  fall out correctly as `textual-convention:Dot1agCfmMepId` automatically.
