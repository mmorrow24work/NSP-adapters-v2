# PM units — resolved from the vendor MIBs

The original project flagged the frame-loss, frame-delay and MEF-10.2
percentile units as `unconfirmed`, and raised them as questions 4 and 9 to
Actelis:

> *"Units for FLR/FD/FDV/MEF10.2 percentiles aren't stated in the SNMP
> `SYNTAX` (plain `Unsigned32` throughout) — flagged `unconfirmed` in the PM
> mapping rather than guessed. Needs either a live modem or Actelis's own
> MEF10.2 configuration/reporting documentation to pin down scale."*

They are stated — in the `DESCRIPTION` text, which a `SYNTAX`/`UNITS`-only
reading misses. All quotes below are verbatim from
`ACTELIS-SERV-MON-MIB.mib` in `ML600_MIB.7z`.

## Resolved

| Objects | Stated scale | MIB wording |
|---|---|---|
| `flFlrELine*FLRIngress`, `...FLREgress`, `flFlrELAN*FLR`, `...FLRFEND` (14) | **1 unit = 0.0001 %**  → 100 % = 1 000 000 | *"Frame Loss Ratio … measurement provided as 1 = 0.0001% , i.e. 50 means 0.005% of Frame Loss Ratio."* |
| `fdFdvELAN*FD`, `fdFdvELAN*FDV` (8) | **microseconds** | *"It is measured in microsecond units. 1000 microseconds = 1 msec."* |
| `servMonMEFServAvailObjectiveCU`, `...CA`, `servMonMEFServ1wayFLRObjectiveL` | **1 unit = 0.001 %** → 100 % = 100 000 | *"Unit 1 = 0.001%. 90000 means >= 90% FLR is assumed unavailable Service threshold"* |
| `servMonMEFServ1wayFDObjectiveD` | **microseconds** | *"One-way Frame Delay Objective, in microseconds. 1000 microseconds = 1 msec. Default is 3msec."* |
| `portEgressUtilization`, `portIngressUtilization` | **1 unit = 0.001 %** | *"Reported in units of 1 = 0.001% , i.e. 5985 means 5.985% of port throughput capability is utilized."* |
| `inBWPolicyDiscardedBW`, `outBWPolicyDiscardedBW`, `cirRXAverageBW` (6) | **Kbps** | *"Measured in Kbps."* |
| `ml540mPerfMonitorStatusStatisticsDmUnit` (switch, per row) | `us(0)` / `ns(1)` | `VTSSPerfMonitorMepDmTimeUnit ::= INTEGER { us(0), ns(1) }` |

## The 10× trap

**Measured FLR is `1 = 0.0001%`. The MEF-10.2 FLR *objective* is
`1 = 0.001%`.** Same quantity, same MIB, scales a factor of ten apart.

Comparing a measured frame-loss ratio against its configured objective
without rescaling one of them produces a silently wrong verdict — and it is a
comparison any service-assurance integration will want to make. Encoded as
two distinct `Scale` values (`FLR_MEASURED`, `FLR_OBJECTIVE`) in
`src/actelis_mediation/model/units.py`, with a test asserting they differ.

## Still genuinely unresolved

`ml540mPerfMonitorStatusStatisticsLmNearEndLossRate` and `...FarEndLossRate`
on the **switch** are plain `Unsigned32`, `DESCRIPTION` only *"The near end
loss ratio."*, no `UNITS` clause — and `ML540M-PERF-MONITOR-MIB` and
`ML540M-MEP-MIB` say nothing further. This is a real gap, not an oversight.

The MEF SOAM-PM convention for this field is milli-percent (`1 = 0.001%`),
which is the sensible working assumption and is what `SWITCH_LM_LOSS_RATE`
records — but it is marked `verified=False` and **the scale is never applied**:
the poller stores the raw value with the unit labelled `UNVERIFIED`. An
assumption that looks like data is worse than a gap that looks like a gap.

Narrowed to question 13 in `docs/vendor-questions/actelis.md`.

## Why this matters beyond the numbers

Two of the four questions queued for Actelis were answerable from an archive
committed to the repo. Each vendor round-trip is days to weeks of calendar
time on a project whose critical path is already vendor-gated. The method
that found them is cheap and repeatable: **grep the `DESCRIPTION` text, not
just the `SYNTAX`.**

```bash
python3 tools/mibscan.py <mib-dir> -o /tmp/scan.json
python3 - <<'EOF'
import json, re
defs = json.load(open("/tmp/scan.json"))["defs"]
pat = re.compile(r"provided as|expressed (in|as)|measured in|1 = |units? of", re.I)
for v in defs.values():
    if v["description"] and pat.search(v["description"]) and not v["units"]:
        print(v["name"], "->", v["description"][:120])
EOF
```
