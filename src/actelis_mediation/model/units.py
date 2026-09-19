"""Unit and scale handling for PM counters.

The original project flagged the FLR / frame-delay / MEF-10.2 percentile
units as "unconfirmed -- needs a live modem or Actelis documentation" and
raised them as vendor questions 4 and 9. That was over-cautious: the scales
are stated in the vendor MIB, just in the DESCRIPTION text rather than in
SYNTAX or a UNITS clause, so a SYNTAX-only reading misses them.

Verbatim evidence from ``ACTELIS-SERV-MON-MIB.mib`` (ML600_MIB.7z):

  flFlrELANCurr1DayFLR / flFlrELine*FLRIngress / ...FLREgress
    "Frame Loss Ratio measurement provided as 1 = 0.0001% , i.e. 50 means
     0.005% of Frame Loss Ratio."
      -> 1 count = 1e-4 percent; 100% = 1 000 000 counts.

  fdFdvELANCurr1DayFD / ...FDV  (8 objects)
    "It is measured in microsecond units. 1000 microseconds = 1 msec."
      -> microseconds.

  servMonMEFServAvailObjectiveCU / ...CA / servMonMEFServ1wayFLRObjectiveL
    "Unit 1 = 0.001%. 90000 means >= 90% FLR ..."
      -> 1 count = 1e-3 percent; 100% = 100 000 counts.

  servMonMEFServ1wayFDObjectiveD
    "One-way Frame Delay Objective, in microseconds."

  portEgressUtilization / portIngressUtilization
    "Reported in units of 1 = 0.001% , i.e. 5985 means 5.985% ..."

  inBWPolicyDiscardedBW / outBWPolicyDiscardedBW / cirRXAverageBW (6 objects)
    "Measured in Kbps."

NOTE THE TRAP: *measured* FLR uses 1 = 0.0001% while *configured* MEF-10.2
FLR objectives use 1 = 0.001%. Two different scales for the same quantity in
one MIB, a factor of 10 apart. Comparing a measured FLR against its objective
without rescaling gives a silently wrong verdict.

Still genuinely unresolved (kept as a vendor question):
  * ``ml540mPerfMonitorStatusStatisticsLm{Near,Far}EndLossRate`` on the
    SWITCH -- plain Unsigned32, DESCRIPTION is only "The near end loss
    ratio.", and ML540M-MEP-MIB says nothing either. MEF SOAM-PM convention
    for this field is milli-percent (1 = 0.001%), which is the sensible
    working assumption, but it is an assumption: flagged UNVERIFIED and
    never silently applied.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Scale:
    """A unit conversion with its provenance."""
    unit: str                   # canonical unit after applying `factor`
    factor: float               # multiply the raw SNMP integer by this
    evidence: str               # where the scale comes from
    verified: bool = True       # False => assumption, must not be trusted silently

    def apply(self, raw: str | int | float) -> float | None:
        try:
            return float(raw) * self.factor
        except (TypeError, ValueError):
            return None


MIB_DESCRIPTION = "ACTELIS-SERV-MON-MIB DESCRIPTION text"

# --- DSL modem (ML600 family), resolved from the vendor MIB -----------------
FLR_MEASURED = Scale("percent", 1e-4, f"{MIB_DESCRIPTION}: 'provided as 1 = 0.0001%'")
FLR_OBJECTIVE = Scale("percent", 1e-3, f"{MIB_DESCRIPTION}: 'Unit 1 = 0.001%'")
FRAME_DELAY = Scale("microseconds", 1.0, f"{MIB_DESCRIPTION}: 'measured in microsecond units'")
UTILIZATION = Scale("percent", 1e-3, f"{MIB_DESCRIPTION}: 'units of 1 = 0.001%'")
BANDWIDTH_KBPS = Scale("kbps", 1.0, f"{MIB_DESCRIPTION}: 'Measured in Kbps'")

# --- switch (ML540M) --------------------------------------------------------
# VTSSPerfMonitorMepDmTimeUnit ::= INTEGER { us(0), ns(1) } -- per ROW, so the
# unit must be read from the row's own DmUnit column, never assumed.
DM_UNIT_BY_CODE = {
    "0": Scale("microseconds", 1.0, "VTSSPerfMonitorMepDmTimeUnit us(0)"),
    "us": Scale("microseconds", 1.0, "VTSSPerfMonitorMepDmTimeUnit us(0)"),
    "us(0)": Scale("microseconds", 1.0, "VTSSPerfMonitorMepDmTimeUnit us(0)"),
    "1": Scale("nanoseconds", 1.0, "VTSSPerfMonitorMepDmTimeUnit ns(1)"),
    "ns": Scale("nanoseconds", 1.0, "VTSSPerfMonitorMepDmTimeUnit ns(1)"),
    "ns(1)": Scale("nanoseconds", 1.0, "VTSSPerfMonitorMepDmTimeUnit ns(1)"),
}

SWITCH_LM_LOSS_RATE = Scale(
    "percent", 1e-3,
    "ASSUMED from MEF SOAM-PM milli-percent convention; ML540M-PERF-MONITOR-MIB "
    "states no scale. Confirm against a live unit before trusting.",
    verified=False)

# RFC 4319 HDSL2-SHDSL counters are plain event counts -- no scaling.
EVENT_COUNT = Scale("count", 1.0, "RFC 4319 performance counters are event counts")


def resolve_dm_unit(raw: str) -> Scale | None:
    """Resolve a row's DmUnit varbind into a Scale, or None if unrecognised.

    Returning None rather than guessing is deliberate: an unrecognised unit
    that silently defaults to microseconds is a 1000x error in a delay value.
    """
    v = (raw or "").strip()
    if ":" in v:
        v = v.split(":", 1)[1].strip()
    return DM_UNIT_BY_CODE.get(v)
