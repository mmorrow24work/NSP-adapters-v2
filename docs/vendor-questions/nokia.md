# Questions for Nokia — NSP adaptor project

Ready to paste into an email or use as a meeting agenda. Rewritten from the
original: the SNMPv3 premise was wrong and has been removed, MDM-vs-MDC is
largely answered from public documentation so the question is narrowed, and
the access ask leads because it is the long pole.

**Where we are.** MIB analysis, an OID-to-attribute schema (2,583 objects
across two device families), MIB-grounded alarm/PM mapping tables, and a
standalone non-NSP Communicator prototype that polls, decodes and stores —
with the SNMP row-creation protocol proven end-to-end against a lab switch.
We have **no NSP or SDK access**, which is the current hard gate.

---

## 1. Access and onboarding — the critical path

1. What is the process and typical timeline for **Network Developer Portal**
   enrolment for NSP SDK training? Self-service, or sponsored by our account
   team?
2. Actelis is not a device family Nokia ships adaptors for. We understand
   Nokia can co-develop customer-specific adaptors with early Developer
   Portal access — is that the right path here, and what does engaging it
   involve (account-team request, scoping call, SOW)? Is there a cost, or is
   it self-service once access is granted?
3. Is there a **sandbox or simulator NSP instance** available during SDK
   training, so we can validate a Device Model and Communicator without
   touching a production system?
4. Could we see the source of an existing **third-party SNMP adaptor** as a
   worked example? A close analogue — SNMPv2c-only device, no NETCONF — would
   be worth more to us than the documentation set.

## 2. Adaptor structure

Your architecture documentation states MDM covers *"multi-vendor IP devices
managed using SNMP"*, so we have proceeded on the basis that MDM is correct
for SNMP-only devices and that the MDC cut-through pattern addresses a
different need (operator session proxying, no Device Model).

5. Please confirm that reading is right, and tell us whether cut-through is
   worth adding alongside MDM for operator CLI access.
6. Can multiple related device types **share code** within one adaptor project
   — SNMP session handling, a generic row-editor helper, trap plumbing — or
   is each device type expected to be a fully separate codebase? We expect
   two device types (an EAD/DSL family and an L2 switch) with substantial
   common ground.
7. Do NFM-P third-party adaptors offer a shorter path for any part of this in
   a classic deployment, or should we treat MDM as the only route?

## 3. Device Model schema

8. Our switch device has ~2,000 candidate attributes across 57 MIB modules.
   Is there guidance on Device Model granularity, or is "one Device Model per
   physical device type, however large" the norm?
9. We have preserved SNMP textual conventions (`RowStatus`,
   `VTSSRowEditorState`, `Hdsl2ShdslTransmissionModeType`) as named types
   rather than flattening them to primitives. Is that the right instinct for
   porting into NSP's Device Model format?
10. For a table whose row creation uses a vendor reserve → stage → commit
    protocol rather than RFC 2579 `RowStatus`, does that workflow belong in
    the Device Model, or entirely in the Communicator with the Device Model
    exposing only the resulting list?
11. Is there a naming convention we should adopt now? Our attribute names and
    flat PM metric names are local inventions and we would rather converge
    early than rename 2,000 attributes later.

## 4. Fault model

12. What is NSP Fault Management's **actual severity enum** — exact label set
    and string values? Our mapping tables use the generic X.733 set
    (Critical/Major/Minor/Warning/Indeterminate/Cleared) as an explicit
    placeholder.
13. Is there a standard **probable-cause** taxonomy adaptors map into (X.733 /
    3GPP style), or is it effectively free text?
14. **Alarm resynchronisation:** what does NSP expect when a Communicator
    restarts, misses a trap, or the device renumbers its alarm table after a
    reboot? We track alarm state and emit raise/change/clear transitions
    locally, reconciled against a full poll — we want to align that with
    NSP's own resync model rather than duplicate it.
15. Does the Communicator framework provide a **trap listener**, or is
    SNMPv2c trap decoding the adaptor's own job? Our prototype pipes
    `snmptrapd` output through a parser as a stand-in.

## 5. Concurrency and config push

16. The switch's row-creation mechanism is a **device-wide mutex with no
    timeout** — a manager reserves a table's row editor and only an explicit
    clear or commit releases it. How does a **clustered** Communicator
    serialise writes so two instances do not contend, and what happens to a
    reservation if the instance holding it dies?
17. Is there a generic helper in the Communicator SDK for reserve/stage/commit
    row creation, or does each adaptor implement its own state machine?
18. Config backup/restore and firmware upgrade on both device families work by
    SNMP SET triggering an on-device **FTP** push/pull. Does NSP have an
    established pattern for this, reusing its file-server facilities?
19. Is bulk/templated provisioning squarely Intent Manager / Workflow Manager
    territory, or does the adaptor layer expose batching primitives?

## 6. Performance Manager

20. Both families do on-device interval binning with a finite rolling window
    (the switch keeps Y.1731 LM/DM intervals; the EAD family keeps 96×15-min
    + 7×1-day for line counters, but only a single `Curr`/`Prev` pair for its
    EVC counters — one completed interval, overwritten by the next). Is there
    a recommended polling/archival pattern the Communicator SDK expects for
    periodic-pull PM, or is that the adaptor's own scheduler?
21. What **timestamp semantics** does Performance Manager want for binned
    counters — collection time, or the bin's own start time? This determines
    how we model the bin index and we would rather get it right first time.
22. Is there a PM metric naming/format convention, or do Device Model metric
    definitions drive it?

## 7. Security

23. Does the NSP Communicator support **SNMPv3 USM** for third-party adaptors,
    and how are credentials stored and rotated? The switch family supports
    SNMPv3 authPriv (SHA/AES) and we intend to use it rather than SNMPv2c.
24. For any device that genuinely is SNMPv2c-only, does NSP have a stated
    position or recommended mitigation pattern beyond network-level controls?
25. Is provisioning device-level AAA (local users, RADIUS/TACACS+) from NSP
    typically in scope for a v1 adaptor, or left to a separate bootstrap/ZTP
    process?

## 8. Planning

26. For a project this size — two SNMP-only device types, no NETCONF, no EMS
    — what is a realistic path length from "SDK training complete" to
    "adaptor live against production NSP"? We need to set internal
    expectations.
27. Who is the right ongoing technical contact for SDK/adaptor questions?

---

*Happy to share our attribute schema, alarm/PM mapping tables and the
standalone Communicator prototype as a concrete starting point for a review.*
