"""OID constants, each annotated with the MIB object it comes from.

Every constant in this module is checked against the vendor MIBs by
``tests/test_oid_constants.py``, which extracts the archives and resolves the
OIDs independently. A vendor MIB revision that moves an object fails the test
suite instead of silently polling the wrong branch.

All OIDs verified against ML540M-MIB.7z / ML600_MIB.7z on 2026-09-19.
Scalars carry an explicit ``.0`` at the point of use -- the lesson the
original project paid for on its first lab run.
"""
from __future__ import annotations

# --- switch identity: ML540M-SYSTEM-MIB ------------------------------------
SWITCH_PRODUCT_MODEL = "1.3.6.1.4.1.5468.100.1.1.1"   # productModel
SWITCH_SW_VERSION = "1.3.6.1.4.1.5468.100.1.1.2"      # swVersion
SWITCH_PORT_COUNT = "1.3.6.1.4.1.5468.100.1.1.5"      # portCount

SWITCH_IDENTITY = {
    "productModel": SWITCH_PRODUCT_MODEL + ".0",
    "swVersion": SWITCH_SW_VERSION + ".0",
    "portCount": SWITCH_PORT_COUNT + ".0",
}

# --- DSL modem identity -----------------------------------------------------
# ACTELIS-ALARM-MIB carries no system identity. ACTELIS-SERV-MON-MIB does, and
# servMonSystemModel is a closed `Models` enum naming every Actelis NE model --
# which is what lets one Device Model cover the whole ML600 family and
# discriminate members at discovery time. The original used only the RFC1213
# System group.
DSL_SYS_DESCR = "1.3.6.1.2.1.1.1"
DSL_SYS_NAME = "1.3.6.1.2.1.1.5"
DSL_SERVMON_MODEL = "1.3.6.1.4.1.5468.4.1.1.1"        # servMonSystemModel
DSL_SERVMON_SW_VERSION = "1.3.6.1.4.1.5468.4.1.1.2"   # servMonSystemSWversion
DSL_SERVMON_TID = "1.3.6.1.4.1.5468.4.1.1.3"          # servMonSystemTID

DSL_IDENTITY = {
    "sysDescr": DSL_SYS_DESCR + ".0",
    "sysName": DSL_SYS_NAME + ".0",
    "model": DSL_SERVMON_MODEL + ".0",
    "swVersion": DSL_SERVMON_SW_VERSION + ".0",
    "tid": DSL_SERVMON_TID + ".0",
}

# --- switch alarms: ML540M-SYSTEM-MIB --------------------------------------
SWITCH_CURRENT_ALARM_ENTRY = "1.3.6.1.4.1.5468.100.1.2.2.1.1"
SWITCH_ALARM_COLUMNS = {
    "rowId": SWITCH_CURRENT_ALARM_ENTRY + ".1",
    "seqId": SWITCH_CURRENT_ALARM_ENTRY + ".2",
    "typeId": SWITCH_CURRENT_ALARM_ENTRY + ".3",
    "level": SWITCH_CURRENT_ALARM_ENTRY + ".4",
    "state": SWITCH_CURRENT_ALARM_ENTRY + ".5",
    "time": SWITCH_CURRENT_ALARM_ENTRY + ".6",
}

# --- DSL alarms: ACTELIS-ALARM-MIB -----------------------------------------
DSL_ALARM_ENTRY = "1.3.6.1.4.1.5468.5.4.1"
DSL_ALARM_COLUMNS = {
    "index": DSL_ALARM_ENTRY + ".1",
    "tid": DSL_ALARM_ENTRY + ".2",
    "name": DSL_ALARM_ENTRY + ".3",
    "aid": DSL_ALARM_ENTRY + ".4",
    "oid": DSL_ALARM_ENTRY + ".5",
    "dateTime": DSL_ALARM_ENTRY + ".6",
    "serviceAffect": DSL_ALARM_ENTRY + ".7",
    "severity": DSL_ALARM_ENTRY + ".8",
    "description": DSL_ALARM_ENTRY + ".9",
}

# --- DSL PM: HDSL2-SHDSL-LINE-MIB (RFC 4319) -------------------------------
DSL_15MIN_ENTRY = "1.3.6.1.2.1.10.48.1.6.1"
DSL_15MIN_COLUMNS = {
    "hdsl2Shdsl15MinIntervalES": DSL_15MIN_ENTRY + ".2",
    "hdsl2Shdsl15MinIntervalSES": DSL_15MIN_ENTRY + ".3",
    "hdsl2Shdsl15MinIntervalCRCanomalies": DSL_15MIN_ENTRY + ".4",
    "hdsl2Shdsl15MinIntervalLOSWS": DSL_15MIN_ENTRY + ".5",
    "hdsl2Shdsl15MinIntervalUAS": DSL_15MIN_ENTRY + ".6",
}
DSL_1DAY_ENTRY = "1.3.6.1.2.1.10.48.1.7.1"
DSL_1DAY_COLUMNS = {
    "hdsl2Shdsl1DayIntervalES": DSL_1DAY_ENTRY + ".3",
    "hdsl2Shdsl1DayIntervalSES": DSL_1DAY_ENTRY + ".4",
    "hdsl2Shdsl1DayIntervalCRCanomalies": DSL_1DAY_ENTRY + ".5",
    "hdsl2Shdsl1DayIntervalLOSWS": DSL_1DAY_ENTRY + ".6",
    "hdsl2Shdsl1DayIntervalUAS": DSL_1DAY_ENTRY + ".7",
}

# --- switch PM: ML540M-PERF-MONITOR-MIB (Y.1731 LM/DM) ---------------------
SWITCH_LM_ENTRY = "1.3.6.1.4.1.5468.100.117.1.3.1.1.1"
SWITCH_LM_COLUMNS = {
    "ml540mPerfMonitorStatusStatisticsLmNearEndLossCount": SWITCH_LM_ENTRY + ".18",
    "ml540mPerfMonitorStatusStatisticsLmNearEndLossRate": SWITCH_LM_ENTRY + ".19",
    "ml540mPerfMonitorStatusStatisticsLmFarEndLossCount": SWITCH_LM_ENTRY + ".20",
    "ml540mPerfMonitorStatusStatisticsLmFarEndLossRate": SWITCH_LM_ENTRY + ".21",
}
SWITCH_DM_ENTRY = "1.3.6.1.4.1.5468.100.117.1.3.1.2.1"
SWITCH_DM_UNIT_COLUMN = SWITCH_DM_ENTRY + ".16"      # VTSSPerfMonitorMepDmTimeUnit, PER ROW
SWITCH_DM_COLUMNS = {
    "ml540mPerfMonitorStatusStatisticsDmFarToNearDelayAverage": SWITCH_DM_ENTRY + ".19",
    "ml540mPerfMonitorStatusStatisticsDmFarToNearDelayAverageVariation": SWITCH_DM_ENTRY + ".20",
    "ml540mPerfMonitorStatusStatisticsDmFarToNearDelayMin": SWITCH_DM_ENTRY + ".21",
    "ml540mPerfMonitorStatusStatisticsDmFarToNearDelayMax": SWITCH_DM_ENTRY + ".22",
    "ml540mPerfMonitorStatusStatisticsDmNearToFarDelayAverage": SWITCH_DM_ENTRY + ".23",
    "ml540mPerfMonitorStatusStatisticsDmNearToFarDelayAverageVariation": SWITCH_DM_ENTRY + ".24",
    "ml540mPerfMonitorStatusStatisticsDmNearToFarDelayMin": SWITCH_DM_ENTRY + ".25",
    "ml540mPerfMonitorStatusStatisticsDmNearToFarDelayMax": SWITCH_DM_ENTRY + ".26",
    "ml540mPerfMonitorStatusStatisticsDm2WayDelayAverage": SWITCH_DM_ENTRY + ".27",
    "ml540mPerfMonitorStatusStatisticsDm2WayDelayAverageVariation": SWITCH_DM_ENTRY + ".28",
    "ml540mPerfMonitorStatusStatisticsDm2WayDelayMin": SWITCH_DM_ENTRY + ".29",
    "ml540mPerfMonitorStatusStatisticsDm2WayDelayMax": SWITCH_DM_ENTRY + ".30",
}

# --- traps ------------------------------------------------------------------
DSL_TRAP_ALARM_RAISED = "1.3.6.1.4.1.5468.5.0.1"
DSL_TRAP_ALARM_CLEARED = "1.3.6.1.4.1.5468.5.0.2"
SWITCH_ALARM_TRAP_PREFIX = "1.3.6.1.4.1.5468.100.1.2.3.2"
SWITCH_EVENT_TRAP_PREFIX = "1.3.6.1.4.1.5468.100.1.2.3.1"

# --- SNMPv3 / security (ML540M-SNMP-MIB) -----------------------------------
# The switch DOES implement SNMPv3: VTSSSnmpVersion { snmpV1(0), snmpV2c(1),
# snmpV3(2) }, USM users with MD5/SHA auth and DES/AES privacy, and VACM
# access groups and views -- all configurable over SNMP. See
# docs/security-posture.md; this contradicts the original project's premise
# that these devices are SNMPv2c-only.
SWITCH_SNMP_VERSION = "1.3.6.1.4.1.5468.100.36.1.2.1.2"        # ml540mSnmpConfigGlobalsVersion
SWITCH_SNMP_READ_COMMUNITY = "1.3.6.1.4.1.5468.100.36.1.2.1.3"
SWITCH_SNMP_WRITE_COMMUNITY = "1.3.6.1.4.1.5468.100.36.1.2.1.4"
