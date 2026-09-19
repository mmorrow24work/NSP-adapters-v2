# Glossary

Abbreviations and terms used across this repo, grouped by where you are
likely to meet them first. Entries say what the thing *is here*, not just
what the letters stand for — and where a term matters to a decision, it
points at the document that decision lives in.

---

## Project and process

**ADR — Architecture Decision Record**
A short, numbered note recording one significant design decision: the
context that forced it, what was decided, and what it costs. The convention
comes from Michael Nygard's 2011 post *Documenting Architecture Decisions*;
the shape is Title / Status / Context / Decision / Consequences.

Records are **immutable** — you don't edit a decision, you supersede it with
a new one, so the old reasoning stays readable. `Status` is load-bearing:
*Proposed* means the decision is argued but not yet confirmed (ADR-0003 is
Proposed pending one `snmpget` against a live unit), *Accepted* means it
stands. The point is that "why" decays fastest: anyone can read the code and
see *that* we poll devices directly, but nothing in the code says we
considered the EMS and rejected it, or on what evidence.
See [`adr/`](adr/).

**FCAPS — Fault, Configuration, Accounting, Performance, Security**
The ISO/ITU-T model for what a network management system has to do. Used
here as the acceptance framework: "EMS parity" means covering the same five
pillars. [`fcaps-parity.md`](fcaps-parity.md) is the analysis;
[`fcaps-test-plan.md`](fcaps-test-plan.md) is the executable version.

**CI — Continuous Integration**
The GitHub Actions workflow in `.github/workflows/ci.yml`: lint, tests, MIB
conformance, a check that generated artefacts are not stale, and a check
that every Mermaid diagram still renders.

---

## Nokia NSP

**NSP — Network Services Platform**
Nokia's network management and orchestration platform. The target system:
everything in this repo exists to let NSP manage Actelis equipment.

**MDM — Model-Driven Mediation**
NSP's framework for managing third-party devices. An adaptor has three
parts: a **discovery adaptor** (finds the device, pulls basic inventory), a
**Device Model** (NSP's internal representation of it), and a
**Communicator** (talks the device's actual protocol and maps onto the
model). Nokia's documentation states MDM covers "multi-vendor IP devices
managed using SNMP", which is why it is the right pattern here even with no
NETCONF. See [`adr/0002-mdm-vs-mdc.md`](adr/0002-mdm-vs-mdc.md).

**MDC — cut-through adaptor pattern**
An NSP pattern that proxies an operator session through to the device's own
management interface. Useful for CLI access, but it produces no Device
Model, so no inventory, alarms or PM. Complementary to MDM, not an
alternative — the question ADR-0002 settles.

**SDK — Software Development Kit**
Nokia's NSP adaptor development kit, reached through the Network Developer
Portal. Access to it is the current hard gate on Phase 1.

**NFM-P**
Nokia's classic network management product. Mentioned because its
third-party adaptors may offer a shorter path for some functions in a
classic deployment — a question to Nokia, not a decision.

**YANG / NETCONF**
The model-driven config stack NSP prefers. Neither Actelis family speaks
NETCONF, hence SNMP throughout. The Device Model format is described as
YANG-like.

---

## SNMP and MIBs

**SNMP — Simple Network Management Protocol**
The only management protocol either device family exposes. **SNMPv2c** uses
a cleartext "community string" as its sole credential. **SNMPv3** adds user
based authentication and encryption — and, contrary to the original
project's premise, the ML540M supports it. See
[`security-posture.md`](security-posture.md).

**MIB — Management Information Base**
The vendor's machine-readable description of every object its SNMP agent
exposes: names, OIDs, types, access, and prose descriptions. The archives in
`mibs/actelis/` are the evidence base for this whole project.

**OID — Object Identifier**
A dotted numeric address for one SNMP object, e.g.
`1.3.6.1.4.1.5468.100.1.1.1`. The `5468` is Actelis's enterprise number.
**Scalar** OIDs need a trailing `.0` at the point of use — a lesson this
project paid for on its first lab run.

**SMIv2 — Structure of Management Information, version 2**
The rules MIB files must follow (RFC 2578). `ACTELIS-SERV-MON-MIB` violates
one of them in exactly one place, which is why it failed to compile.

**TC — Textual Convention**
A named type layered on a base SNMP type, carrying extra meaning —
`RowStatus`, `TruthValue`, `VTSSRowEditorState`. Preserved rather than
flattened to string/integer in the attribute schema, so the semantics stay
visible.

**INDEX clause**
The part of a MIB table definition naming the columns that identify a row.
Encoded into the trailing sub-identifiers of each OID. Getting this wrong is
the most serious defect found in the review: an index can be 1, 2 or 5
components, and truncating it to the last one silently destroys the data.

**GET / WALK / SET / trap**
The four SNMP operations used here: read one object, read a subtree, write
an object, and an unsolicited notification pushed by the device.

**Community string**
The SNMPv2c credential. `public` / `private` are the factory defaults, still
live on the lab unit. On these devices the *read* community can retrieve the
*write* community, so read access escalates to write.

**USM / VACM**
SNMPv3's User-based Security Model (authentication and privacy) and
View-based Access Control Model (who may see which subtree). Both are
implemented on the ML540M and configurable over SNMP.

**RowStatus / VTSSRowEditorState**
Two different mechanisms for creating table rows over SNMP. `RowStatus` is
the RFC 2579 standard state machine. `VTSSRowEditorState` is the
Microsemi/VTSS pattern the ML540M uses instead: reserve → stage → commit.
See [`adr/0004-row-editor-concurrency.md`](adr/0004-row-editor-concurrency.md).

**VTSS**
Vitesse, now Microsemi/Microchip — the switch silicon vendor whose MIB
framework the ML540M's MIBs are derived from. Every `VTSS*` type name comes
from there, which is why the switch MIBs look nothing like the Actelis-
authored ones.

**net-snmp**
The open-source SNMP toolset (`snmpget`, `snmpwalk`, `snmpbulkwalk`,
`snmpset`, `snmptrapd`) this project shells out to. Type characters in a SET
follow its convention: `i` integer, `u` unsigned, `s` string, `a` IP
address, `x` hex.

---

## The devices

**ML540M**
The Actelis L2 aggregation/access switch. Enterprise OID root
`1.3.6.1.4.1.5468.100`. VTSS-derived MIBs, 4,527 objects across 57 files.

**ML600 family**
The Actelis EAD/DSL copper modems — ML620R, ML622, ML684 and other variants
enumerated in the `Models` textual convention. One MIB package covers all of
them. See [`adr/0003-device-type-scoping.md`](adr/0003-device-type-scoping.md).

**EAD — Ethernet Access Device**
Equipment delivering Ethernet services over copper.

**DSL / SHDSL / HDSL2**
Digital Subscriber Line technologies. `HDSL2-SHDSL-LINE-MIB` (RFC 4319) is
the standards-based line-performance MIB these modems implement.

**EFM — Ethernet in the First Mile**
IEEE 802.3ah, Ethernet over copper access. `EFM-CU-MIB` carries the
copper-pair line quality objects — SNR margin, attenuation.

**EMS — Element Management System**
Actelis's own management system (MetaAssist). The alternative to talking to
devices directly. Its northbound OSS interface (`NMS-ALARM-MIB`) offers
alarm correlation and topology the direct path lacks, which is why
[`adr/0001-direct-snmp-vs-ems.md`](adr/0001-direct-snmp-vs-ems.md)
recommends a hybrid rather than a clean choice.

**OSS — Operations Support System**
The upstream systems that consume network management data. NSP is one.

**TL1 — Transaction Language 1**
A telecoms management command language. The ML600 alarm table is
TL1-derived, which is why its severities are the literal strings `CR`
(critical), `MJ` (major), `MN` (minor), `NA` (non-alarmed) rather than an
SNMP enum, and why alarms carry an **AID** (Access Identifier — the entity
the alarm is raised against) and an **SA/NSA** flag (service-affecting or
not).

---

## Fault management

**Alarm vs event**
An alarm is a standing condition that is raised and later cleared. An event
is a point-in-time occurrence. The switch keeps both in separate tables.

**X.733**
The ITU-T alarm model NSP-style fault management is built on. Supplies the
severity vocabulary used throughout: Critical, Major, Minor, Warning,
Indeterminate, Cleared — and the idea of a **probable cause**. Marked as a
placeholder here because NSP's exact enum is still unconfirmed.

**Trap**
An unsolicited SNMP notification. Note the coverage limit: the ML540M
defines link-down traps for GE ports 1–10 only, though its alarm table
covers all 25 — so ports 11–25 can only be caught by polling.

**AAA — Authentication, Authorization, Accounting**
Device-level access control (local users, RADIUS, TACACS+). Whether NSP
provisions this is an open question to Nokia.

---

## Performance monitoring

**PM — Performance Monitoring**
Counters and measurements collected over time. Both families bin PM on-device
into fixed intervals with a finite rolling window, so the adaptor's job is to
poll before a bin rolls off rather than build its own history.

**Interval bin**
A completed measurement window. `HDSL2-SHDSL-LINE-MIB` keeps 96 × 15-minute
bins (24h) plus 7 × 1-day bins. `ACTELIS-SERV-MON-MIB` keeps only `Curr`
(in progress) and `Prev` (one completed interval) — so a missed poll loses
data permanently.

**ES / SES / UAS / LOSWS / CRC anomalies**
The RFC 4319 line-quality counters: Errored Seconds, Severely Errored
Seconds, Unavailable Seconds, Loss Of Sync Word Seconds, and CRC error
events.

**CFM — Connectivity Fault Management**
IEEE **802.1ag**, Ethernet service-layer OAM. A **MEP** (Maintenance entity
group End Point) is a monitoring point at the edge of a service; MEPs
exchange continuity checks and carry the defect flags the switch exposes as
polled status objects.

**Y.1731**
ITU-T's Ethernet OAM performance measurement, built on 802.1ag. Supplies
**LM** (Loss Measurement) and **DM** (Delay Measurement). The switch's
Y.1731 counters live in `ML540M-PERF-MONITOR-MIB`.

**MEF 10.2 / SOAM**
Metro Ethernet Forum service attributes and Service OAM. Defines the
service-level metrics the ML600 family reports: **FLR** (Frame Loss Ratio),
**FD** (Frame Delay), **FDV** (Frame Delay Variation) and percentile
availability figures.

Watch the scales — they are stated in the MIB but differ between objects:
measured FLR is `1 = 0.0001%`, the MEF-10.2 FLR *objective* is `1 = 0.001%`.
A factor of ten, in the same file. See
[`mib-analysis/units-resolved.md`](mib-analysis/units-resolved.md).

**EVC — Ethernet Virtual Connection**
A MEF construct: one logical Ethernet service across a provider network.
Most service-level PM here is per-EVC or per-MEP rather than per-port.

**DDMI**
Digital Diagnostics Monitoring Interface — optical transceiver telemetry
(temperature, voltage, Tx/Rx power, usually in **dBm**). Present on the
switch and not yet mapped.

---

## Switch features

**VLAN / PVLAN** — Virtual LAN; Private VLAN.
**ACL** — Access Control List, packet filtering rules.
**QoS** — Quality of Service, traffic classification and shaping.
**LACP** — Link Aggregation Control Protocol (IEEE 802.3ad), bonding ports.
**LLDP** — Link Layer Discovery Protocol, how neighbours advertise
themselves; the usual basis for automatic topology discovery. The
proprietary LLDP status subtree is missing on the lab unit's firmware; the
**standard** `LLDP-MIB` (`1.0.8802.1.1.2`) has not yet been tried.
**MSTP** — Multiple Spanning Tree Protocol.
**ERPS** — Ethernet Ring Protection Switching (ITU-T G.8032).
**EPS** — Ethernet Protection Switching (ITU-T G.8031), linear protection.
**PSEC** — Port Security, MAC-based access limiting.
**UDLD** — Unidirectional Link Detection.
**GVRP** — GARP VLAN Registration Protocol.
**MVR / IGMP** — Multicast VLAN Registration; Internet Group Management
Protocol, for multicast snooping.
**PTP** — Precision Time Protocol (IEEE 1588), sub-microsecond clock
distribution. Often a hard requirement in critical-infrastructure networks;
present on the switch and unanalysed.
**MPLS** — Multiprotocol Label Switching. The switch supports it; unmentioned
in the original analysis.
**GE** — Gigabit Ethernet, as in `alarmGEPort7LinkDown`.

---

## Operations

**OOB — Out Of Band**
A separate management network, physically or logically isolated from the
service path. The usual mitigation for cleartext SNMPv2c — though on the
ML540M, configuring SNMPv3 is the better answer.

**ZTP — Zero Touch Provisioning**
Automated first-boot configuration. Raised as the question of whether device
AAA is bootstrapped outside NSP.

**FTP**
Config backup/restore and firmware upgrade on both families work by SNMP SET
*triggering* an on-device FTP transfer, rather than moving data over SNMP.

**CLI** — Command Line Interface, the device's own console.
**CSV** — the format the OID maps, attribute schema and mapping tables use.
**RFC** — an IETF standards document. RFC 4319 (HDSL2-SHDSL PM), RFC 2578
(SMIv2), RFC 2579 (RowStatus) are the ones that matter here.
**WAL** — Write-Ahead Logging, the SQLite journal mode the local store uses.

---

## Sources

* [Documenting Architecture Decisions — Michael Nygard](https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
* [adr.github.io](https://adr.github.io/) — ADR templates and tooling
* [RFC 4319 — HDSL2/SHDSL Line MIB](https://www.rfc-editor.org/rfc/rfc4319)
* [RFC 2578 — SMIv2](https://www.rfc-editor.org/rfc/rfc2578) ·
  [RFC 2579 — Textual Conventions](https://www.rfc-editor.org/rfc/rfc2579)
* [NSP network mediation](https://documentation.nokia.com/nsp/24-4/NSP_System_Architecture_Guide/NSP-network-mediation.html)
