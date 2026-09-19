"""INDEX specifications for the tables the pollers walk.

Every spec here is transcribed from the INDEX clause of the corresponding
``...Entry`` object in the vendor MIBs and is checked against them by
``tests/test_index_specs_match_mibs.py``, so a MIB revision that changes a
table's index fails the build rather than silently corrupting collected data.
"""
from __future__ import annotations

from ..snmp.oid import INTEGER, IPADDRESS, STRING, IndexSpec

# --- switch: ML540M-SYSTEM-MIB ---------------------------------------------
# currentAlarmEntry INDEX { currentAlarmRowId }
SWITCH_CURRENT_ALARM = IndexSpec(names=["rowId"], kinds=[INTEGER])
SWITCH_HISTORY_ALARM = IndexSpec(names=["rowId"], kinds=[INTEGER])

# --- switch: ML540M-PERF-MONITOR-MIB ---------------------------------------
# ...LmEntry INDEX { ...LmIntervalId, ...LmEntryId }      -- TWO components.
# ...DmEntry INDEX { ...DmIntervalId, ...DmEntryId }      -- TWO components.
# The original poller used only the last sub-identifier, so the per-row DmUnit
# could be paired with delay values from a different interval.
SWITCH_LM = IndexSpec(names=["intervalId", "entryId"], kinds=[INTEGER, INTEGER])
SWITCH_DM = IndexSpec(names=["intervalId", "entryId"], kinds=[INTEGER, INTEGER])

# --- DSL modem: HDSL2-SHDSL-LINE-MIB (RFC 4319, as shipped by Actelis) ------
# hdsl2Shdsl15MinIntervalEntry INDEX {
#   ifIndex, hdsl2ShdslInvIndex, hdsl2ShdslEndpointSide,
#   hdsl2ShdslEndpointWirePair, hdsl2Shdsl15MinIntervalNumber }   -- FIVE.
DSL_15MIN_INTERVAL = IndexSpec(
    names=["ifIndex", "invIndex", "endpointSide", "wirePair", "intervalNumber"],
    kinds=[INTEGER, INTEGER, INTEGER, INTEGER, INTEGER])
DSL_1DAY_INTERVAL = IndexSpec(
    names=["ifIndex", "invIndex", "endpointSide", "wirePair", "intervalNumber"],
    kinds=[INTEGER, INTEGER, INTEGER, INTEGER, INTEGER])

# --- DSL modem: ACTELIS-ALARM-MIB ------------------------------------------
# alarmEntry INDEX { alarmIndex }
DSL_ALARM = IndexSpec(names=["alarmIndex"], kinds=[INTEGER])

# --- switch: ML540M-SNMP-MIB (the row-editor proof target) ------------------
SWITCH_SNMP_COMMUNITY = IndexSpec(
    names=["name", "sourceIP", "prefixSize"], kinds=[STRING, IPADDRESS, INTEGER])

INDEX_SPECS_BY_ENTRY = {
    "currentAlarmEntry": SWITCH_CURRENT_ALARM,
    "historyAlarmEntry": SWITCH_HISTORY_ALARM,
    "ml540mPerfMonitorStatusStatisticsLmEntry": SWITCH_LM,
    "ml540mPerfMonitorStatusStatisticsDmEntry": SWITCH_DM,
    "hdsl2Shdsl15MinIntervalEntry": DSL_15MIN_INTERVAL,
    "hdsl2Shdsl1DayIntervalEntry": DSL_1DAY_INTERVAL,
    "alarmEntry": DSL_ALARM,
    "ml540mSnmpConfigCommunityEntry": SWITCH_SNMP_COMMUNITY,
}
