# ADR-0002 · Model-Driven Mediation (MDM), not the MDC cut-through pattern

**Status:** Accepted. Confirm details with Nokia once SDK access exists.

## Context

The original project assumed MDM without recording why, and then asked Nokia
(question 6) whether the **MDC "cut-through"** pattern might fit better given
these are SNMPv2c-only devices with no NETCONF and no EMS in the path. Fair
question — but it can be largely answered before the meeting.

## Decision

**MDM is the right pattern.** Nokia's own architecture documentation states
MDM provides mediation for *"devices managed using YANG model-based
interfaces"* **and** *"multi-vendor IP devices managed using SNMP"*. SNMP-only
is an explicitly supported MDM case, not a workaround.

The cut-through pattern solves a different problem. Cut-through gives an
operator a proxied session to the device's own management interface — useful
for CLI access through NSP, but it produces no Device Model, so it yields no
inventory, no normalised alarms, and no PM. Nothing in this project's goals
(FCAPS parity with the EMS, NSP Fault Management, NSP Performance Manager) is
achievable through cut-through alone.

They are complementary, not alternatives: MDM for the managed model,
cut-through as a possible convenience on top.

## Consequences

* The three-part structure (discovery adaptor + Device Model + Communicator)
  stands, and the existing Phase 0 artefacts map onto it directly.
* Question 6 to Nokia is reframed from "which pattern?" to "confirm MDM for
  SNMP-only, and is cut-through worth adding for operator CLI access?"
* One thing still genuinely open, asked separately: whether multiple related
  device types can **share code** inside one adaptor project, or whether each
  device type is a fully separate codebase. That materially affects how the
  shared SNMP/row-editor/trap layer is packaged, and public documentation
  does not answer it.

## Also worth raising

Nokia's docs mention **NFM-P adaptors for managing third-party equipment** in
classic deployments. If Telent runs NFM-P alongside NSP, there may be a
shorter path for some FCAPS functions. Worth one question, not a redesign.

## Sources

* [NSP network mediation](https://documentation.nokia.com/nsp/24-4/NSP_System_Architecture_Guide/NSP-network-mediation.html)
* [MDM glossary entry](https://documentation.nokia.com/nsp/24-4/Glossary/mdm_def.html)
* [NSP SDK](https://www.nokia.com/networks/training/nsp/self-paced/sdk/)
