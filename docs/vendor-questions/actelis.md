# Questions for Actelis — NSP adaptor project

Ready to paste into an email. Rewritten from the original list: **two of the
original questions have been answered from the MIB archive you already
supplied**, so they are gone, and the rest are sharpened to ask only what the
MIBs genuinely cannot tell us.

*Context: we are building Nokia NSP device adaptors for Actelis equipment via
direct SNMP, working from the `ML600_MIB.7z` and `ML540M-MIB.7z` archives
supplied to us.*

---

## 1. The MetaAssist EMS northbound interface

`NMS-ALARM-MIB.my` in the ML600 archive defines what looks like an EMS-level
OSS interface at `1.3.6.1.4.1.5468.9.1` — a cross-device open-alarms table
with a stable `alarmID`, `alarmAdded`/`alarmCleared`/`alarmModified`
notifications, and a `topologyTable` with parent/child relationships.

1. Is this interface current and supported, and which MetaAssist EMS versions
   expose it?
2. Is `alarmID` stable across an EMS restart, and is it unique across the
   whole managed estate?
3. Does `topologyTable` reflect discovered adjacency (e.g. from LLDP), or only
   the parent/child registration held in the EMS?
4. Is there documentation for this interface beyond the MIB file?

*Why we're asking: we have designed for direct-to-device SNMP, but this
interface offers alarm correlation and topology that per-device polling does
not, and we would like to evaluate a hybrid rather than rule it out by
default.*

## 2. Model scope — confirmation, not discovery

We were asked to extend coverage to ML540, ML622 and ML684. From
`ACTELIS-SERV-MON-MIB`'s `Models` textual convention (read back via
`servMonSystemModel`) we believe:

* **ML622** — ML600 family; enum values 28, 29, 30, 46 including `i` variants.
* **ML684** — ML600 family; enum values 11 (`ml684-501RG0048`) and 50
  (`ml684d-501RG0220`).
* **ML540** — not in that enum; we assume it refers to the ML540M switch line.

5. Is that correct — are ML622 and ML684 covered by the ML600 MIB package we
   already have, needing no additional MIB archive?
6. Is "ML540" the same SNMP/MIB surface as ML540M, or a distinct variant?
7. Is the `Models` enum kept current across firmware releases, i.e. can we
   rely on `servMonSystemModel` to identify the variant at discovery time?
8. Which ML600-family models differ materially in **implemented** SNMP
   surface (not just MIB-declared)? We would rather handle that as capability
   detection than discover it per model in the field.

## 3. DSL/EAD alarm-name catalogue

`ACTELIS-ALARM-MIB`'s `alarmName` is free text with no closed enum; the
object's `DESCRIPTION` gives only three examples (`LOSW`, `HSLDWN`,
`INTRUDER`). We need the full set to map alarms into NSP's fault model.

9. Is there a published TL1 command reference (`RTRV-ALARM` / `RTRV-COND`)
   listing every `alarmName` value and its meaning? We understand this is
   served from a live unit at `http://<device-IP>/support` — is there a copy
   obtainable without a unit, via the support portal or your documentation
   team?
10. Is there a maintained alarm dictionary (name → severity → probable cause →
    service-affecting) for the ML600 line?

## 4. ACTELIS-SERV-MON-MIB authoring bug

`servMonMEPLossFLFLR1DayELANEntry ::= { servMonMEPLossFLFLR1DayELANTable 2 }`
— SMIv2 requires a table's `Entry` to be sub-identifier `1`. We have confirmed
this is the only such instance in the file.

11. **Does the live agent implement this table at `...Table.1` (standard) or
    at `...Table.2` (matching the MIB source)?** This is the one that actually
    affects us: a poller built from a corrected MIB would walk the wrong OID
    if the agent follows its own file.
12. Is a corrected MIB available? We are happy to share our one-line fix.

## 5. Switch EVC performance-monitoring scale

`ml540mPerfMonitorStatusStatisticsLmNearEndLossRate` / `...FarEndLossRate` are
`Unsigned32` with no scale stated in `SYNTAX`, `UNITS` or `DESCRIPTION`, and
`ML540M-MEP-MIB` does not state it either.

13. What is the scale — raw ratio, percent, or a pre-multiplied fixed-point
    value? (The ML600 side states its equivalents explicitly in the
    `DESCRIPTION` — e.g. *"provided as 1 = 0.0001%"* — so we suspect the
    switch MIB simply omits it rather than differing.)
14. For `ml540mPerfMonitorStatusStatisticsDmBinTable`, what are the delay-range
    boundaries for each `DmBinBucketId`? The MIB defines the index but not the
    bucket boundaries.

## 6. Switch alarm-trap coverage

15. `ML540M-SYSTEM-MIB` defines a link-down trap only for GE ports **1–10**
    (13 alarm traps total), while `VTSSAlarmType` and `currentAlarmTable`
    cover all 25 ports. Is that intentional, or a gap expected to close in a
    later MIB/firmware revision? If intentional, is polling `currentAlarmTable`
    the recommended way to catch link-down on ports 11–25?

## 7. SNMPv3 on the ML600 family

`ML540M-SNMP-MIB` shows full SNMPv3/USM support on the switch (MD5/SHA,
DES/AES, authPriv, VACM). The ML600 archive ships `SNMP-FRAMEWORK-MIB` but
`ML620R-MIB` exposes only plain community scalars.

16. Do ML600-family devices support SNMPv3, and from which firmware version?
    We would prefer not to manage this estate over SNMPv2c.

## 8. Row-creation semantics on the ML600 family

17. For tables using a `RowStatus`-style column (e.g. `vlanConfigurationTable`,
    `dhcpPoolTable`), does row creation follow the standard RFC 2579
    `RowStatus` state machine, or the reserve → stage → commit "row editor"
    pattern we confirmed on the ML540M (`VTSSRowEditorState`)? One example
    SET sequence creating a single row would settle it.

## 9. General

18. Is there a reference architecture or third-party NMS integration guide for
    Actelis equipment we should be working from?
19. Who is the right ongoing technical contact for MIB/SNMP questions?

---

*Happy to share our OID maps, attribute schema and alarm/PM mapping tables if
useful context.*
