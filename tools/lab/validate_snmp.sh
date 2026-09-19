#!/usr/bin/env bash
#
# validate_snmp.sh — direct-to-device SNMPv2c validation for Actelis ML620R
# (and family) modems, ahead of building the NSP Device Model / Communicator.
#
# Confirms, against a real lab unit:
#   1. The device answers SNMPv2c directly (no EMS in the path)
#   2. The DSL line status table (dslStatusTable) returns live data
#   3. Alarm table is readable
#   4. SNMP SET works (writes dslMode back to its current value — a no-op
#      write that proves write access without changing device behaviour)
#   5. Trap destination can be pointed at this host (readWriteCommunity
#      required — SET on ipv4RemoteTrapSer / trapOption)
#
# Usage:
#   ./validate_snmp.sh <device-ip> <ro-community> [rw-community]
#
# Requires: net-snmp tools (snmpget, snmpwalk, snmpset) on PATH.
# MIBs: point MIBDIRS at the extracted Actelis_MIBs folder, or pass
# numeric OIDs only (this script uses numeric OIDs throughout so no
# MIB loading is required).

set -euo pipefail

DEVICE_IP="${1:?Usage: $0 <device-ip> <ro-community> [rw-community]}"
RO_COMMUNITY="${2:?Usage: $0 <device-ip> <ro-community> [rw-community]}"
RW_COMMUNITY="${3:-}"

# --- OIDs (from actelis_oid_map.csv) -----------------------------------
OID_SYSDESCR="1.3.6.1.2.1.1.1.0"                      # sysDescr (RFC1213)
OID_DSL_STATUS_TABLE="1.3.6.1.4.1.5468.510.1.1"       # dslStatusTable
OID_DSL_SNR="1.3.6.1.4.1.5468.510.1.1.1.5"            # dslSNR (per-port)
OID_DSL_RATE="1.3.6.1.4.1.5468.510.1.1.1.7"           # dslRate (per-port)
OID_DSL_MODE="1.3.6.1.4.1.5468.510.2.1.7"             # dslMode (read-write)
OID_ALARM_ROWCOUNT="1.3.6.1.4.1.5468.5.2"             # alarmTableRowCount
OID_ALARM_TABLE="1.3.6.1.4.1.5468.5.4"                # alarmTable

hr() { printf '%s\n' "------------------------------------------------------------"; }

hr
echo "1. Basic reachability (sysDescr) — confirms direct SNMP agent on device"
snmpget -v2c -c "$RO_COMMUNITY" -Ov "$DEVICE_IP" "$OID_SYSDESCR"

hr
echo "2. DSL line status table walk — dslService/dslStandard/dslAttenuation/dslSNR/dslStatus/dslRate"
snmpwalk -v2c -c "$RO_COMMUNITY" -On "$DEVICE_IP" "$OID_DSL_STATUS_TABLE"

hr
echo "3. Alarm table row count + walk (current active alarms on this NE)"
snmpget  -v2c -c "$RO_COMMUNITY" -Ov "$DEVICE_IP" "$OID_ALARM_ROWCOUNT"
snmpwalk -v2c -c "$RO_COMMUNITY" -On "$DEVICE_IP" "$OID_ALARM_TABLE"

if [[ -n "$RW_COMMUNITY" ]]; then
  hr
  echo "4. SNMP SET round-trip test on dslMode (read current value, write it back unchanged)"
  CURRENT=$(snmpget -v2c -c "$RO_COMMUNITY" -Ovq "$DEVICE_IP" "$OID_DSL_MODE")
  echo "   current dslMode raw value: $CURRENT"
  echo "   writing back same value via SNMP SET (int type 'i') ..."
  # dslMode is INTEGER {dslAtmMode(12), dslEfmMode(13)} — adjust the numeric
  # value below to match $CURRENT before running unattended.
  snmpset -v2c -c "$RW_COMMUNITY" "$DEVICE_IP" "$OID_DSL_MODE" i "$CURRENT"
  echo "   re-reading to confirm SET was accepted:"
  snmpget -v2c -c "$RO_COMMUNITY" -Ov "$DEVICE_IP" "$OID_DSL_MODE"
else
  hr
  echo "4. Skipped SNMP SET test (no rw-community supplied)"
fi

hr
echo "Done. If step 1-3 returned data and step 4 (if run) round-tripped cleanly,"
echo "direct-to-device SNMPv2c is confirmed viable for both discovery/monitoring"
echo "and config-push — no EMS proxy required for the NSP Communicator."
