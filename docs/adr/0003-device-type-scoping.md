# ADR-0003 · Two NSP device types, not four

**Status:** Proposed — confirm by reading `servMonSystemModel` off a unit.

## Context

The project was asked to extend from ML540M + ML620R to also cover **ML540,
ML622 and ML684**, and queued four questions to Actelis asking which product
lines these are and which MIB packages they need. The README records them as
"not yet MIB-analyzed".

## Evidence already in the repo

`ACTELIS-SERV-MON-MIB.mib` (in `ML600_MIB.7z`) defines a `Models` textual
convention — a closed 53-value enum of Actelis network element models, read
back from the device through `servMonSystemModel`
(`1.3.6.1.4.1.5468.4.1.1.1`):

```
Models ::= TEXTUAL-CONVENTION
    DESCRIPTION "Actelis Network Element Models, new models are always
                 added at the end of the enumerator"
    SYNTAX INTEGER { unknown(0), ... ml684-501RG0048(11), ...
                     ml622-501R00016(28), ml622-501RG0016(29),
                     ml622i-501RG0062(30), ... ml530-501RG0530(44),
                     ml622i-501RG0162(46), ... ml684d-501RG0220(50), ... }
```

* **ML684** — present, twice (`ml684-501RG0048`, `ml684d-501RG0220`).
* **ML622** — present, four times including the `i` and `d` variants.
* **ML540** — *not* present, consistent with ML540 being the switch line
  (`ML540M`), whose identity is a free-text `productModel` string instead.

So ML622 and ML684 are ML600-family EAD/DSL devices already covered by the
MIB archive in this repo. They are not new product families needing new MIB
packages.

## Decision

Scope **two NSP device types**:

1. **ML600-family EAD/DSL** — one Device Model, one discovery adaptor, one
   Communicator, with the specific model discovered at runtime from
   `servMonSystemModel` and per-model capability differences handled as
   capability detection rather than as separate device types.
2. **ML540M switch** — separate OID namespace, separate capability set,
   separate Device Model.

## Why this matters beyond tidiness

* It removes a blocking vendor dependency from the critical path: the scope
  question no longer waits on an Actelis reply.
* Four adaptors is roughly twice the Device Model, discovery and Communicator
  work of two, and more to certify with Nokia.
* It gives the discovery adaptor a principled variant-detection mechanism
  instead of per-model branching.

## How to confirm — cheap

```bash
snmpget -v2c -c "$RO" -Ovq <any-ML600-family-unit> 1.3.6.1.4.1.5468.4.1.1.1.0
```

If it returns a `Models` enum value, the mechanism is real and the decision
holds. Until then this ADR is Proposed, and the (narrowed) question to Actelis
asks them to confirm the mapping and whether the enum is kept current across
firmware releases.

## Risk

The `Models` enum is only as good as the firmware implementing it. A unit
running firmware predating a model's addition may report `unknown(0)`. The
discovery adaptor should fall back to `sysDescr` / `servMonSystemTID` and
record a capability gap rather than failing discovery.
