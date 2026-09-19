#!/usr/bin/env python3
"""
build_alarm_pm_mapping.py

Generates the two mapping spreadsheets from roadmap Phase 0 item 3:
  - alarm-severity-mapping.csv : Actelis alarm/event severity -> NSP severity
  - pm-counter-mapping.csv     : Actelis PM counters -> NSP PM metric names/units

Grounded directly in the vendor MIB text (ACTELIS-ALARM-MIB.mib,
HDSL2-SHDSL-LINE-MIB.mib, EFM-CU-MIB.mib for the modem; ML540M-SYSTEM-MIB.mib,
ML540M-PERF-MONITOR-MIB.mib for the switch) -- not guessed. Rows sourced from
a closed SNMP enum are marked confidence=confirmed; rows describing
free-text TL1 fields with no closed catalog in the MIB are marked
confidence=inferred and flagged for live-unit or TL1-doc confirmation.
"""
import csv
from pathlib import Path

# Original hardcoded /home/claude/NSP-adapters/docs/mapping-tables, which
# made this runnable on exactly one machine. Resolved relative to the repo.
OUT_DIR = Path(__file__).resolve().parent.parent / "data" / "mapping-tables"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Alarm / event severity mapping
# ---------------------------------------------------------------------------

ALARM_FIELDS = [
    "device_type", "source_mib_object", "source_value", "source_meaning",
    "nsp_severity", "nsp_probable_cause", "service_affecting",
    "confidence", "notes",
]

alarm_rows = []

# --- DSL modem: ACTELIS-ALARM-MIB.mib ---
# alarmSeverity is DisplayString carrying literal TL1 codes (CR/MJ/MN/NA) --
# confirmed from the object's own DESCRIPTION text, not a closed SNMP enum.
dsl_severity_map = [
    ("CR", "Critical (TL1)", "Critical", "confirmed",
     "Service-affecting condition requiring immediate action."),
    ("MJ", "Major (TL1)", "Major", "confirmed",
     "Serious condition, action required but not immediately service-down."),
    ("MN", "Minor (TL1)", "Minor", "confirmed",
     "Non-serious condition, does not affect service."),
    ("NA", "Non-alarmed / reported condition (TL1)", "Warning", "confirmed",
     "TL1 RTRV-COND reports NA conditions too (per alarmTable DESCRIPTION) -- "
     "these are informational/condition reports, not true alarms. Map to "
     "Warning or Indeterminate rather than Cleared; confirm against NSP's "
     "exact enum once SDK access exists."),
]
for code, meaning, sev, conf, note in dsl_severity_map:
    alarm_rows.append({
        "device_type": "dsl-modem",
        "source_mib_object": "alarmSeverity (ACTELIS-ALARM-MIB)",
        "source_value": code,
        "source_meaning": meaning,
        "nsp_severity": sev,
        "nsp_probable_cause": "(see alarmName / alarmDescription text -- "
                               "free-text, not a closed enum; see notes)",
        "service_affecting": "see alarmServiceAffect (SA/NSA) on same row",
        "confidence": conf,
        "notes": note,
    })

alarm_rows.append({
    "device_type": "dsl-modem",
    "source_mib_object": "alarmServiceAffect (ACTELIS-ALARM-MIB)",
    "source_value": "SA",
    "source_meaning": "Service-affecting (TL1)",
    "nsp_severity": "(modifier, not a severity itself)",
    "nsp_probable_cause": "n/a",
    "service_affecting": "yes",
    "confidence": "confirmed",
    "notes": "Text field per object DESCRIPTION -- 'SA' for service affecting.",
})
alarm_rows.append({
    "device_type": "dsl-modem",
    "source_mib_object": "alarmServiceAffect (ACTELIS-ALARM-MIB)",
    "source_value": "NSA",
    "source_meaning": "Non-service-affecting (TL1)",
    "nsp_severity": "(modifier, not a severity itself)",
    "nsp_probable_cause": "n/a",
    "service_affecting": "no",
    "confidence": "confirmed",
    "notes": "Text field per object DESCRIPTION -- 'NSA' for non-service affecting.",
})

# alarmName is free text (DisplayString) -- the MIB gives only 3 examples in
# its DESCRIPTION ("LOSW, HSLDWN or INTRUDER"). No closed catalog exists in
# the MIB itself; a definitive list needs either a live unit's alarm table
# or Actelis's TL1 command reference (RTRV-ALARM/RTRV-COND). The rows below
# are common DSL/EFM/telco alarm names that plausibly appear on this
# platform, proposed from the object's own examples plus the counters this
# device exposes elsewhere (HDSL2-SHDSL-LINE-MIB, EFM-CU-MIB) -- NOT
# confirmed against a live unit or vendor TL1 doc. Treat as a starting
# draft to validate, not a finished mapping.
dsl_alarm_names_inferred = [
    ("LOSW", "Loss of Sync Word -- DSL line sync lost", "Loss Of Signal",
     "Matches hdsl2ShdslEndpointCurrStatus loss-of-sync-word bit "
     "(HDSL2-SHDSL-LINE-MIB) -- plausible pairing, not confirmed."),
    ("LOS", "Loss of Signal -- no signal detected on the line",
     "Loss Of Signal", "Standard telco condition name; not seen verbatim in "
     "the MIB text, included as a likely candidate."),
    ("HSLDWN", "High-Speed Link Down (example given in the MIB itself)",
     "Link Failure", "Verbatim example from alarmName's own DESCRIPTION."),
    ("INTRUDER", "Unauthorized access attempt (example given in the MIB itself)",
     "Unauthorized Access Attempt", "Verbatim example from alarmName's own "
     "DESCRIPTION -- a security event, not a line-fault condition."),
    ("SESH", "Severely Errored Seconds threshold crossed",
     "Excessive Bit Error Rate", "Plausible name given hdsl2Shdsl SES "
     "counters and Hdsl2ShdslPerfIntervalThreshold objects exist on this "
     "device -- not confirmed."),
]
for name, meaning, cause, note in dsl_alarm_names_inferred:
    alarm_rows.append({
        "device_type": "dsl-modem",
        "source_mib_object": "alarmName (ACTELIS-ALARM-MIB) -- free text, no closed enum",
        "source_value": name,
        "source_meaning": meaning,
        "nsp_severity": "(see alarmSeverity CR/MJ/MN/NA mapping above)",
        "nsp_probable_cause": cause,
        "service_affecting": "(see alarmServiceAffect on same row)",
        "confidence": "inferred -- needs live-unit or TL1-doc confirmation",
        "notes": note,
    })

# --- Switch: ML540M-SYSTEM-MIB.mib -- fully closed SNMP enums, extracted verbatim ---
switch_alarm_level = [
    ("alm-minor(1)", "Minor", "confirmed"),
    ("alm-major(2)", "Major", "confirmed"),
]
switch_alarm_state = [
    ("alm-Set(1)", "(alarm raised -- combine with level for full severity)", "confirmed"),
    ("alm-Cleared(2)", "Cleared", "confirmed"),
]
switch_alarm_types = [
    ("alarmGEPortNLinkDown(101-125)", "Link Failure",
     "One value per GE port (101=port1 .. 125=port25)."),
    ("alarmSystemOverHeat(400)", "Temperature Unacceptable", ""),
    ("alarmPower1NotFeed(301)", "Power Problem", "Power supply 1 not feeding."),
    ("alarmPower2NotFeed(302)", "Power Problem", "Power supply 2 not feeding."),
]

for val, meaning, conf in switch_alarm_level:
    alarm_rows.append({
        "device_type": "switch",
        "source_mib_object": "currentAlarmLevel / historyAlarmLevel / alarmProfileLevel "
                              "(VTSSAlarmLevel, ML540M-SYSTEM-MIB)",
        "source_value": val,
        "source_meaning": meaning,
        "nsp_severity": meaning,
        "nsp_probable_cause": "(see currentAlarmTypeId / VTSSAlarmType)",
        "service_affecting": "n/a -- not modeled on this platform",
        "confidence": conf,
        "notes": "Only two levels exist on this platform -- no Critical/Warning "
                 "distinction at the switch-alarm level. If NSP needs finer "
                 "granularity, it has to come from elsewhere (e.g. per-trap "
                 "semantics in MSTP/ERPS/EPS MIBs) rather than this field.",
    })

for val, meaning, conf in switch_alarm_state:
    alarm_rows.append({
        "device_type": "switch",
        "source_mib_object": "currentAlarmState / historyAlarmState "
                              "(VTSSAlarmState, ML540M-SYSTEM-MIB)",
        "source_value": val,
        "source_meaning": meaning,
        "nsp_severity": "Cleared" if "Cleared" in meaning else "(use with alarm level)",
        "nsp_probable_cause": "n/a",
        "service_affecting": "n/a",
        "confidence": conf,
        "notes": "State transition, not itself a severity -- pair with "
                 "currentAlarmLevel for the full NSP alarm record.",
    })

for val, cause, note in switch_alarm_types:
    alarm_rows.append({
        "device_type": "switch",
        "source_mib_object": "currentAlarmTypeId / historyAlarmTypeId / alarmProfileId "
                              "(VTSSAlarmType, ML540M-SYSTEM-MIB)",
        "source_value": val,
        "source_meaning": val,
        "nsp_severity": "(see currentAlarmLevel on same row/index)",
        "nsp_probable_cause": cause,
        "service_affecting": "yes" if "Link" in cause else "no",
        "confidence": "confirmed",
        "notes": note,
    })

switch_event_level = [
    ("evt-Error(1)", "Error", "Warning"),
    ("evt-Notice(2)", "Notice", "Indeterminate"),
    ("evt-Warning(3)", "Warning", "Warning"),
    ("evt-Info(4)", "Info", "Indeterminate"),
]
for val, meaning, nsp_sev in switch_event_level:
    alarm_rows.append({
        "device_type": "switch",
        "source_mib_object": "eventLevel (VTSSEventLevel, ML540M-SYSTEM-MIB)",
        "source_value": val,
        "source_meaning": meaning,
        "nsp_severity": nsp_sev,
        "nsp_probable_cause": "(see the specific VTSSEventType value on the same row)",
        "service_affecting": "n/a",
        "confidence": "confirmed for source_value; nsp_severity mapping is a "
                       "reasonable default, not NSP-confirmed",
        "notes": "The event log (link up/down, config save, login/logout, LED "
                 "state, etc.) is a separate, lower-priority stream from the "
                 "alarm table above -- useful for NSP's event/audit trail but "
                 "distinct from fault-management alarms. Only login/logout/"
                 "config-save carry no fault meaning at all; consider whether "
                 "NSP should surface those as alarms or just as log entries.",
    })

# --- Switch: feature MIBs (ERPS/EPS/MSTP/loop-protection/PSEC/MEP) ---
# Roadmap Phase 0 item 3 originally assumed these conditions were carried as
# their own SNMP traps in each feature MIB. Checked directly against the
# vendor source (57 switch feature MIBs, /tmp/mibwork/switch_mibs/ as of
# 2026-09-19): only ML540M-SYSTEM-MIB.mib defines any NOTIFICATION-TYPE --
# already fully mapped above. None of MSTP/ERPS/EPS/LACP/LLDP/etc. define a
# single trap. Every fault condition in those MIBs is instead exposed as a
# read-only *polled status object* (a TruthValue flag or a small state enum)
# -- the Communicator has to poll and diff these, not listen for a trap.
# This corrects that assumption; see docs/alarm-pm-mapping.md for the fuller
# writeup. Rows below cover the fault-relevant status objects found across
# ERPS, EPS, MSTP, loop-protection, port-security, and 802.1ag CFM (MEP) --
# not every status object in these MIBs, just the ones whose own DESCRIPTION
# clearly identifies a fault/defect/protection-switch condition.
switch_erps_fields = [
    ("ml540mErpsStatusFopAlarm", "TruthValue", "TRUE",
     "FailureOfProtocol alarm active", "Major",
     "ERPS Protocol Failure", "no",
     "APS signaling itself is unreliable -- the ring may still be passing "
     "traffic on its current (possibly non-optimal) path."),
    ("ml540mErpsStatusProtectionState", "VTSSErpsProtectionState", "protected(3)",
     "Ring has switched onto its protection path", "Major",
     "Ring Protection Switch Active", "yes",
     "A working link/node has failed and traffic is running on the backup "
     "path -- the fault itself is elsewhere (e.g. a GE port link-down "
     "alarm on the failed span), this is the ring's response to it."),
    ("ml540mErpsStatusProtectionState", "VTSSErpsProtectionState",
     "forcedSwitch(4) / manualSwitch(5)", "Operator-forced ring switch", "Warning",
     "Ring Protection Manually Forced", "no",
     "Deliberate operator action, not a device fault -- flag so it isn't "
     "mistaken for an autonomous failure."),
    ("ml540mErpsStatusProtectionState", "VTSSErpsProtectionState", "pending(6)",
     "Ring protection state transition in progress (hold-off/guard/WTR timer)",
     "Indeterminate", "Ring Protection State Transitioning", "no",
     "Transient -- re-poll; settles to idle(2)/protected(3) once the timer "
     "expires."),
    ("ml540mErpsStatusProtectionState", "VTSSErpsProtectionState",
     "none(1) / idle(2)", "Normal (no ring / ring healthy, RPL blocked as designed)",
     "Cleared", "n/a", "n/a", "Steady-state -- not a fault."),
]
for obj, syntax, val, meaning, sev, cause, svc, note in switch_erps_fields:
    alarm_rows.append({
        "device_type": "switch",
        "source_mib_object": f"{obj} ({syntax}, ML540M-ERPS-MIB)",
        "source_value": val,
        "source_meaning": meaning,
        "nsp_severity": sev,
        "nsp_probable_cause": cause,
        "service_affecting": svc,
        "confidence": "confirmed for source_value; nsp_severity mapping is a "
                       "reasonable default, not NSP-confirmed",
        "notes": note,
    })

switch_eps_fields = [
    ("ml540mEpsStatusProtectionState", "VTSSEpsProtectionState",
     "signalFailWorking(5) / signalFailProtecting(6)",
     "Signal fail on working or protecting flow", "Major",
     "EPS Protection Switch -- Signal Fail", "yes",
     "G.8031 1+1/1:1 linear protection has switched due to a real signal "
     "failure on one flow."),
    ("ml540mEpsStatusProtectionState", "VTSSEpsProtectionState",
     "lockOut(3) / forcedSwitch(4) / manualSwitchWorking(7) / "
     "manualSwitchProtecting(8) / doNotRevert(14)",
     "Operator-forced EPS state", "Warning",
     "EPS Manually Forced / Locked Out", "no",
     "Deliberate operator action (or a lock-out preventing autonomous "
     "protection), not a device fault by itself -- but doNotRevert/lockOut "
     "left in place means a subsequent real failure won't be protected."),
    ("ml540mEpsStatusProtectionState", "VTSSEpsProtectionState",
     "waitToRestore(9) / exerciseWorking(10) / exerciseProtecting(11) / "
     "reverseRequestWorking(12) / reverseRequestProtecting(13)",
     "EPS transitional/test state", "Indeterminate",
     "EPS State Transitioning", "no", "Transient -- re-poll."),
    ("ml540mEpsStatusProtectionState", "VTSSEpsProtectionState",
     "noRequestWorking(1) / noRequestProtecting(2)", "Normal, no active request",
     "Cleared", "n/a", "n/a", "Steady-state -- not a fault."),
    ("ml540mEpsStatusWorkingState / ml540mEpsStatusProtectingState",
     "VTSSEpsDefectState", "sf(2)",
     "Signal fail on this specific flow (working or protecting)", "Major",
     "EPS Flow Signal Fail", "yes",
     "Per-flow defect state underlying the protection-state transition above."),
    ("ml540mEpsStatusWorkingState / ml540mEpsStatusProtectingState",
     "VTSSEpsDefectState", "sd(1)",
     "Signal degrade on this specific flow", "Minor",
     "EPS Flow Signal Degrade", "no",
     "Below signal-fail threshold but degraded -- worth surfacing before it "
     "becomes a full sf(2)."),
    ("ml540mEpsStatusDfopPm", "TruthValue", "TRUE",
     "FOP Protection-type mismatch (unexpected B bit)", "Major",
     "EPS Protocol Failure -- Protection Type Mismatch", "no",
     "APS protocol-level fault; ring/flow itself may still be up."),
    ("ml540mEpsStatusDfopCm", "TruthValue", "TRUE",
     "FOP Configuration mismatch (APS received on working)", "Major",
     "EPS Protocol Failure -- Configuration Mismatch", "no", ""),
    ("ml540mEpsStatusDfopNr", "TruthValue", "TRUE",
     "FOP Not-expected-Request (received request != transmitted)", "Major",
     "EPS Protocol Failure -- Unexpected Request", "no", ""),
    ("ml540mEpsStatusDfopNoAps", "TruthValue", "TRUE",
     "FOP No APS received", "Major",
     "EPS Protocol Failure -- No APS Received", "no",
     "APS keepalive missing -- protection state can't be trusted until it "
     "clears."),
]
for obj, syntax, val, meaning, sev, cause, svc, note in switch_eps_fields:
    alarm_rows.append({
        "device_type": "switch",
        "source_mib_object": f"{obj} ({syntax}, ML540M-EPS-MIB)",
        "source_value": val,
        "source_meaning": meaning,
        "nsp_severity": sev,
        "nsp_probable_cause": cause,
        "service_affecting": svc,
        "confidence": "confirmed for source_value; nsp_severity mapping is a "
                       "reasonable default, not NSP-confirmed",
        "notes": note,
    })

alarm_rows.append({
    "device_type": "switch",
    "source_mib_object": "ml540mMstpStatusBridgeTopologyChange (TruthValue, ML540M-MSTP-MIB)",
    "source_value": "TRUE",
    "source_meaning": "MSTP topology change flag currently set",
    "nsp_severity": "Warning",
    "nsp_probable_cause": "Spanning Tree Topology Change",
    "service_affecting": "transient (brief flooding/relearning while MAC "
                          "tables converge)",
    "confidence": "confirmed for source_value; nsp_severity mapping is a "
                   "reasonable default, not NSP-confirmed",
    "notes": "Informational/transient rather than a persistent fault -- pairs "
             "with ml540mMstpStatusBridgeTopologyChangeCount for trending "
             "(frequent flapping is the actual problem worth alarming on, "
             "not a single change).",
})

alarm_rows.append({
    "device_type": "switch",
    "source_mib_object": "ml540mLoopProtectionStatusInterfaceLoopDetected "
                          "(TruthValue, ML540M-LOOP-PROTECTION-MIB)",
    "source_value": "TRUE",
    "source_meaning": "Loop detected on this port",
    "nsp_severity": "Major",
    "nsp_probable_cause": "Ethernet Loop Detected",
    "service_affecting": "yes",
    "confidence": "confirmed for source_value; nsp_severity mapping is a "
                   "reasonable default, not NSP-confirmed",
    "notes": "Real risk of a broadcast storm -- the device's own configured "
             "action (ml540mLoopProtectionConfigInterfaceParamAction) may "
             "already shut the port; ml540mPsecStatusPortShutdown below is "
             "the general-purpose version of that outcome.",
})

switch_psec_fields = [
    ("ml540mPsecStatusPortShutdown", "TRUE", "Port shut down by port security",
     "Major", "Port Security Violation -- Port Shutdown", "yes",
     "Port is down as a direct consequence -- treat like any other link-down "
     "condition."),
    ("ml540mPsecStatusPortLimitReached", "TRUE", "MAC address limit reached on port",
     "Warning", "Port Security -- MAC Limit Reached", "no",
     "Port still forwarding for already-learned MACs; new MACs are being "
     "rejected. Precursor to Shutdown if the configured action escalates."),
]
for obj, val, meaning, sev, cause, svc, note in switch_psec_fields:
    alarm_rows.append({
        "device_type": "switch",
        "source_mib_object": f"{obj} (TruthValue, ML540M-PSEC-MIB)",
        "source_value": val,
        "source_meaning": meaning,
        "nsp_severity": sev,
        "nsp_probable_cause": cause,
        "service_affecting": svc,
        "confidence": "confirmed for source_value; nsp_severity mapping is a "
                       "reasonable default, not NSP-confirmed",
        "notes": note,
    })

# --- Switch: 802.1ag CFM (MEP) defect flags, ML540M-MEP-MIB.mib ---
# The same CFM mechanism ACTELIS-SERV-MON-MIB's EVC PM data rides on
# (see servmon-mib-recovery.md) -- these are the underlying per-MEP
# defect-detection flags, all TruthValue, all read-only.
switch_mep_fields = [
    ("ml540mMepStatusInstanceCssf", "SSF (Server Signal Fail) state", "Major",
     "CFM Server Signal Fail", "yes", ""),
    ("ml540mMepStatusInstanceCais", "AIS (Alarm Indication Signal) received", "Major",
     "CFM AIS Received", "yes",
     "Upstream fault being propagated downstream via AIS -- the root cause "
     "is elsewhere in the network, not necessarily this device."),
    ("ml540mMepStatusInstanceClck", "LCK (locked signal) received", "Warning",
     "CFM Locked Signal Received", "yes",
     "Maintenance action upstream (link intentionally locked), not "
     "necessarily an unplanned fault."),
    ("ml540mMepStatusInstanceCloop", "Loop detected (CCM received with own MEP ID/SMAC)",
     "Major", "CFM Loop Detected", "yes", ""),
    ("ml540mMepStatusInstanceCconfig", "Configuration error (CCM received with own MEP ID)",
     "Major", "CFM Configuration Error", "no",
     "Misconfiguration (duplicate MEP ID), not a live traffic fault by "
     "itself, but blocks reliable CFM monitoring until fixed."),
    ("ml540mMepStatusInstanceCdeg", "Signal degraded", "Minor",
     "CFM Signal Degrade", "no",
     "Below signal-fail threshold -- an early-warning signal, not yet a hard "
     "failure."),
    ("ml540mMepStatusInstancePeerCloc", "CCM Loss Of Continuity from peer MEP",
     "Major", "CFM Loss of Continuity (Peer)", "yes",
     "Peer stopped sending CCMs -- classic CFM connectivity-fault signal, "
     "the modem-side equivalent of a link-down."),
    ("ml540mMepStatusInstancePeerCrdi", "CCM Remote Defect Indication from peer MEP",
     "Warning", "CFM Remote Defect Indication", "no",
     "Peer is reporting ITS OWN defect to us via RDI -- the fault is at (or "
     "beyond) the peer, not necessarily on this device's own facing link."),
]
for obj, meaning, sev, cause, svc, note in switch_mep_fields:
    alarm_rows.append({
        "device_type": "switch",
        "source_mib_object": f"{obj} (TruthValue, ML540M-MEP-MIB)",
        "source_value": "TRUE",
        "source_meaning": meaning,
        "nsp_severity": sev,
        "nsp_probable_cause": cause,
        "service_affecting": svc,
        "confidence": "confirmed for source_value; nsp_severity mapping is a "
                       "reasonable default, not NSP-confirmed",
        "notes": note,
    })

# ---------------------------------------------------------------------------
# PM counter mapping
# ---------------------------------------------------------------------------

PM_FIELDS = [
    "device_type", "source_mib_object", "source_mib", "bin_window",
    "raw_unit", "nsp_metric_name", "nsp_unit", "aggregation",
    "polling_note",
]

pm_rows = []

# --- DSL modem: HDSL2-SHDSL-LINE-MIB.mib (RFC 4319) ---
hdsl2_counters = [
    ("ES", "Errored Seconds", "count"),
    ("SES", "Severely Errored Seconds", "count"),
    ("CRCanomalies", "CRC Anomalies", "count"),
    ("LOSWS", "Loss Of Sync Word Seconds", "count"),
    ("UAS", "Unavailable Seconds", "count"),
]
for window, table_obj_prefix, elapsed_obj in [
    ("current (partial) 15-min", "hdsl2ShdslEndpointCurr15Min", "hdsl2ShdslEndpointCurr15MinTimeElapsed"),
    ("historical 15-min (96 bins, ~24h rolling)", "hdsl2Shdsl15MinInterval", None),
    ("current (partial) 1-day", "hdsl2ShdslEndpointCurr1Day", "hdsl2ShdslEndpointCurr1DayTimeElapsed"),
    ("historical 1-day (7 bins, ~1wk rolling)", "hdsl2Shdsl1DayInterval", None),
]:
    for suffix, meaning, raw_unit in hdsl2_counters:
        pm_rows.append({
            "device_type": "dsl-modem",
            "source_mib_object": f"{table_obj_prefix}{suffix}",
            "source_mib": "HDSL2-SHDSL-LINE-MIB (RFC 4319)",
            "bin_window": window,
            "raw_unit": raw_unit,
            "nsp_metric_name": f"dslLine.{suffix.lower()}",
            "nsp_unit": "seconds" if suffix in ("ES", "SES", "LOSWS", "UAS") else "count",
            "aggregation": "sum over interval (standards-defined telco PM counter)",
            "polling_note": "Historical bins roll off after 24h (15-min) / 7d "
                             "(1-day) -- Communicator must poll each bin at "
                             "least once inside that window or the sample is "
                             "lost. Current-interval object gives the "
                             "in-progress partial bin for near-real-time "
                             "dashboards between rollovers.",
        })

# --- EFM-CU-MIB.mib PM counters (2B/10P PME line-quality) ---
efmcu_counters = [
    ("efmCuPmeTCCodingErrors", "PME coding errors", "count"),
    ("efmCuPmeTCCrcErrors", "PME CRC errors", "count"),
    ("efmCuPme10PFECCorrectedBlocks", "10P FEC-corrected blocks", "count"),
    ("efmCuPme10PFECUncorrectedBlocks", "10P FEC-uncorrected blocks", "count"),
    ("efmCuPAFInErrors", "Port Aggregation Function input errors", "count"),
    ("efmCuPAFInLostFragments", "PAF lost fragments", "count"),
]
for obj, meaning, raw_unit in efmcu_counters:
    pm_rows.append({
        "device_type": "dsl-modem",
        "source_mib_object": obj,
        "source_mib": "EFM-CU-MIB (RFC-derived, EFM copper)",
        "bin_window": "cumulative counter (no interval binning -- poll and delta)",
        "raw_unit": raw_unit,
        "nsp_metric_name": f"efmCu.{obj[6:7].lower()}{obj[7:]}",
        "nsp_unit": "count",
        "aggregation": "delta between polls (plain Counter32/Unsigned32, not "
                        "an interval-binned PM object like the HDSL2-SHDSL set)",
        "polling_note": "No on-device history window here -- unlike the "
                         "HDSL2-SHDSL interval tables, these are running "
                         "counters. NSP-side archival/delta computation is "
                         "needed if trending is wanted; miss a poll and the "
                         "delta is just larger next time (32-bit rollover is "
                         "the real risk on a busy line).",
    })

# --- DSL modem: ACTELIS-SERV-MON-MIB.mib -- CFM/MEF10.2 EVC-level PM ---
# Recovered by fixing a vendor authoring bug (a table Entry's own OID
# subidentifier was 2 instead of the required 1) plus preloading
# IEEE8021-CFM-MIB as an explicit smidump import path -- see
# docs/servmon-mib-recovery.md for the full root-cause writeup. 163
# objects recovered; the PM-relevant subset (frame loss/delay, MEF10.2
# availability percentiles) is mapped here.
#
# Unlike HDSL2-SHDSL's 96x15-min/7x1-day rolling history, this MIB only
# keeps ONE current (in-progress) and ONE previous (most recently
# completed) interval per window size -- poll more often than the
# interval length or a completed interval is lost before it's read.
servmon_flflr_fields = [
    ("flFlrELineCurr{window}FLIngress", "Frame loss, ingress (E-Line, point-to-point)", "count"),
    ("flFlrELineCurr{window}FLEgress", "Frame loss, egress (E-Line, point-to-point)", "count"),
    ("flFlrELineCurr{window}FLRIngress", "Frame loss ratio, ingress (E-Line)", "ratio (see notes)"),
    ("flFlrELineCurr{window}FLREgress", "Frame loss ratio, egress (E-Line)", "ratio (see notes)"),
    ("flFlrELANCurr{window}FL", "Frame loss, near-end (E-LAN, point-to-multipoint)", "count"),
    ("flFlrELANCurr{window}FLR", "Frame loss ratio, near-end (E-LAN)", "ratio (see notes)"),
    ("flFlrELANCurr{window}FLFEND", "Frame loss, far-end (E-LAN)", "count"),
    ("flFlrELANCurr{window}FLRFEND", "Frame loss ratio, far-end (E-LAN)", "ratio (see notes)"),
]
servmon_fdfdv_fields = [
    ("fdFdvELANCurr{window}FD", "Frame delay, near-end (E-LAN)", "raw (unit not stated in SYNTAX -- see notes)"),
    ("fdFdvELANCurr{window}FDV", "Frame delay variation, near-end (E-LAN)", "raw (unit not stated in SYNTAX -- see notes)"),
]
for window, mib_window_label in [
    ("1Day", "current (partial) 1-day, CFM/MEF"),
    ("15min", "current (partial) 15-min, CFM/MEF"),
]:
    for obj_template, meaning, raw_unit in servmon_flflr_fields + servmon_fdfdv_fields:
        obj = obj_template.format(window=window)
        metric_suffix = obj_template.split("Curr{window}")[-1]
        pm_rows.append({
            "device_type": "dsl-modem",
            "source_mib_object": obj,
            "source_mib": "ACTELIS-SERV-MON-MIB (CFM/802.1ag + MEF10.2 EVC-level PM)",
            "bin_window": mib_window_label,
            "raw_unit": raw_unit,
            "nsp_metric_name": f"evc.cfm.{metric_suffix[0].lower()}{metric_suffix[1:]}",
            "nsp_unit": "count" if "ratio" not in raw_unit and "raw" not in raw_unit else "unconfirmed",
            "aggregation": "per-interval snapshot, per MEP/RMEP (indexed by "
                            "dot1agCfmMdIndex/MaIndex/MepIdentifier + RMEP index)",
            "polling_note": "Only ONE current + ONE previous interval retained "
                             "per window size (not a 96-bin rolling history like "
                             "HDSL2-SHDSL) -- the Communicator must poll faster "
                             "than the interval length (15min/1day) or a "
                             "completed interval's Prev* twin gets overwritten "
                             "before it's ever read. FLR/FD/FDV units aren't "
                             "stated in the object's SNMP SYNTAX (plain "
                             "Unsigned32) -- confirm scale against a live value "
                             "(no lab modem available to do that yet).",
        })

# MEF10.2 percentile-based availability/performance metrics -- the
# EMS-parity-relevant summary numbers built on top of the raw FL/FD counters.
servmon_mef_fields = [
    ("ServiceAvailability", "MEF10.2 service availability percentile"),
    ("OnewayFLRPerformance", "MEF10.2 one-way frame-loss-ratio performance percentile"),
    ("OnewayFDPerformance", "MEF10.2 one-way frame-delay performance percentile"),
    ("OnewayIFDVPerformance", "MEF10.2 one-way inter-frame-delay-variation performance percentile"),
]
for window, mib_window_label in [
    ("1Day", "current (partial) 1-day, MEF10.2"),
    ("15Min", "current (partial) 15-min, MEF10.2"),
]:
    for suffix, meaning in servmon_mef_fields:
        obj = f"mefCurr{window}{suffix}"
        pm_rows.append({
            "device_type": "dsl-modem",
            "source_mib_object": obj,
            "source_mib": "ACTELIS-SERV-MON-MIB (MEF10.2 percentile performance)",
            "bin_window": mib_window_label,
            "raw_unit": "Unsigned32, scale/unit not stated in SYNTAX",
            "nsp_metric_name": f"evc.mef.{suffix[0].lower()}{suffix[1:]}",
            "nsp_unit": "unconfirmed -- percentile/percent is likely given the "
                        "object's own name, but not stated in its SNMP SYNTAX",
            "aggregation": "per-interval percentile summary, per MEP",
            "polling_note": "Same one-current/one-previous retention caveat as "
                             "the raw FL/FD counters above. This is the "
                             "MEF10.2-standard summary metric set -- likely the "
                             "most directly EMS-comparable PM data on the "
                             "modem side, pending unit confirmation.",
        })

# --- Switch: ML540M-PERF-MONITOR-MIB.mib -- Y.1731 EVC LM/DM ---
lm_fields = [
    ("NearEndLossCount", "Near-end frame loss count", "count"),
    ("NearEndLossRate", "Near-end frame loss rate", "ratio (see notes)"),
    ("FarEndLossCount", "Far-end frame loss count", "count"),
    ("FarEndLossRate", "Far-end frame loss rate", "ratio (see notes)"),
    ("Tx", "Frames transmitted in interval", "count"),
    ("Rx", "Frames received in interval", "count"),
]
for suffix, meaning, raw_unit in lm_fields:
    pm_rows.append({
        "device_type": "switch",
        "source_mib_object": f"ml540mPerfMonitorStatusStatisticsLm{suffix}",
        "source_mib": "ML540M-PERF-MONITOR-MIB (Y.1731 ETH-LM, per-MEP)",
        "bin_window": "per ml540mPerfMonitorStatusStatisticsLmIntervalId "
                       "(configurable via ml540mPerfMonitorConfigGlobalsMgmt"
                       "LossMeasurementInterval)",
        "raw_unit": raw_unit,
        "nsp_metric_name": f"evc.lm.{suffix[0].lower()}{suffix[1:]}",
        "nsp_unit": "percent" if "Rate" in suffix else "frames",
        "aggregation": "per-interval snapshot, indexed by "
                        "(LmIntervalId, LmEntryId) per MEP",
        "polling_note": "Rate fields' exact scale (raw ratio vs. "
                         "pre-multiplied percent) isn't stated in the object's "
                         "SYNTAX (plain Unsigned32) -- confirm the scale "
                         "against a live value before wiring the NSP unit; "
                         "flagged, not assumed, in this row.",
    })

dm_fields = [
    ("FarToNearDelayAverage", "Far-to-near average delay"),
    ("FarToNearDelayAverageVariation", "Far-to-near delay variation"),
    ("FarToNearDelayMin", "Far-to-near min delay"),
    ("FarToNearDelayMax", "Far-to-near max delay"),
    ("NearToFarDelayAverage", "Near-to-far average delay"),
    ("NearToFarDelayAverageVariation", "Near-to-far delay variation"),
    ("NearToFarDelayMin", "Near-to-far min delay"),
    ("NearToFarDelayMax", "Near-to-far max delay"),
    ("2WayDelayAverage", "Two-way average delay"),
    ("2WayDelayAverageVariation", "Two-way delay variation"),
    ("2WayDelayMin", "Two-way min delay"),
    ("2WayDelayMax", "Two-way max delay"),
]
for suffix, meaning in dm_fields:
    pm_rows.append({
        "device_type": "switch",
        "source_mib_object": f"ml540mPerfMonitorStatusStatisticsDm{suffix}",
        "source_mib": "ML540M-PERF-MONITOR-MIB (Y.1731 ETH-DM, per-MEP)",
        "bin_window": "per ml540mPerfMonitorStatusStatisticsDmIntervalId "
                       "(configurable via ml540mPerfMonitorConfigGlobalsMgmt"
                       "DelayMeasurementInterval)",
        "raw_unit": "integer, resolution given by ml540mPerfMonitorStatus"
                    "StatisticsDmUnit (us(0) or ns(1)) on the SAME row",
        "nsp_metric_name": f"evc.dm.{suffix[0].lower()}{suffix[1:]}",
        "nsp_unit": "microseconds or nanoseconds -- read per-row from DmUnit, "
                    "do not assume a fixed unit across devices/rows",
        "aggregation": "per-interval snapshot, indexed by "
                        "(DmIntervalId, DmEntryId) per MEP",
        "polling_note": "Must read ml540mPerfMonitorStatusStatisticsDmUnit "
                         "alongside every delay value -- it's per-row, not "
                         "global, so a single device could in principle "
                         "report mixed resolutions across MEPs.",
    })

pm_rows.append({
    "device_type": "switch",
    "source_mib_object": "ml540mPerfMonitorStatusStatisticsDmBinHitCount "
                          "(+ BinType/BinDirection/BinBucketId as index)",
    "source_mib": "ML540M-PERF-MONITOR-MIB (Y.1731 delay-histogram bins)",
    "bin_window": "per ml540mPerfMonitorStatusStatisticsDmBinIntervalId",
    "raw_unit": "count",
    "nsp_metric_name": "evc.dm.histogramBinHitCount",
    "nsp_unit": "count",
    "aggregation": "histogram bucket count -- BinType/BinDirection/BinBucketId "
                    "together define which delay-range bucket this is; needs "
                    "its own small lookup once the exact bucket boundaries "
                    "are confirmed (not given directly in this table).",
    "polling_note": "Lower priority than the LM/DM summary stats above for a "
                     "first Communicator pass -- useful for delay-distribution "
                     "dashboards later, not needed for basic EMS-parity PM.",
})


def write_csv(path, fieldnames, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows):4d} rows -> {path}")


write_csv(OUT_DIR / "alarm-severity-mapping.csv", ALARM_FIELDS, alarm_rows)
write_csv(OUT_DIR / "pm-counter-mapping.csv", PM_FIELDS, pm_rows)
