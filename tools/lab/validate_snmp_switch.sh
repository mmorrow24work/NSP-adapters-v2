#!/usr/bin/env bash
#
# validate_snmp_switch.sh — direct SNMPv2c validation for the Actelis
# ML540M layer-2 switch, ahead of building its NSP Device Model /
# Communicator (separate device type from the ML620R DSL modems).
#
# Confirms, against a real lab unit:
#   1. The switch answers SNMPv2c directly, and identifies itself
#      (productModel / swVersion / portCount)
#   2. LLDP neighbor table is readable — useful for NSP topology discovery
#   3. LACP aggregation config is readable
#   4. SNMP SET works (writes the LLDP tx interval back to its current
#      value — a no-op write that proves write access)
#
# Usage:
#   ./validate_snmp_switch.sh <switch-ip> <ro-community> [rw-community]
#
# Requires: net-snmp tools (snmpget, snmpwalk, snmpset) on PATH.
# Uses numeric OIDs throughout — no MIB loading required.

set -euo pipefail

DEVICE_IP="${1:?Usage: $0 <switch-ip> <ro-community> [rw-community]}"
RO_COMMUNITY="${2:?Usage: $0 <switch-ip> <ro-community> [rw-community]}"
RW_COMMUNITY="${3:-}"

# --- OIDs (from ml540m_core_oid_map.csv), all under ml540mSwitchMgmt ---
# 1.3.6.1.4.1.5468.100
# NOTE: scalar OIDs need a trailing .0 for GET (the MIB entry is the OBJECT
# TYPE definition; the actual instance is always ".0" for a scalar). The
# first version of this script omitted that and got "No Such Instance" for
# every scalar while table walks (which don't need it) worked fine.
OID_SYSDESCR="1.3.6.1.2.1.1.1.0"                            # sysDescr (RFC1213)
OID_PRODUCT_MODEL="1.3.6.1.4.1.5468.100.1.1.1.0"            # productModel
OID_SW_VERSION="1.3.6.1.4.1.5468.100.1.1.2.0"               # swVersion
OID_PORT_COUNT="1.3.6.1.4.1.5468.100.1.1.5.0"               # portCount
OID_LLDP_ADMIN_STATE="1.3.6.1.4.1.5468.100.34.1.2.2.1.3"    # ml540mLldpConfigAdminState (per-port, walk)
OID_LLDP_NEIGHBORS="1.3.6.1.4.1.5468.100.34.1.3.2"          # ml540mLldpStatusNeighborsInformationTable
OID_LACP_CONFIG="1.3.6.1.4.1.5468.100.35.1.2"               # ml540mLacpConfigPortTable
OID_LLDP_TX_INTERVAL="1.3.6.1.4.1.5468.100.34.1.2.1.3"      # ml540mLldpConfigGlobalMsgTxInterval (scalar, needs .0 too — fixed below)

hr() { printf '%s\n' "------------------------------------------------------------"; }

hr
echo "1. Basic reachability + identity (productModel / swVersion / portCount)"
snmpget -v2c -c "$RO_COMMUNITY" -Ov "$DEVICE_IP" \
  "$OID_PRODUCT_MODEL" "$OID_SW_VERSION" "$OID_PORT_COUNT" 2>/dev/null || \
snmpget -v2c -c "$RO_COMMUNITY" -Ov "$DEVICE_IP" "$OID_SYSDESCR"

hr
echo "2a. LLDP admin state per port — confirms whether LLDP is even enabled"
echo "    before treating an empty neighbor table as a problem"
snmpwalk -v2c -c "$RO_COMMUNITY" -On "$DEVICE_IP" "$OID_LLDP_ADMIN_STATE"

hr
echo "2b. LLDP neighbor table walk — for NSP topology discovery"
echo "    (expect this to be empty unless LLDP is enabled AND a neighbor"
echo "    that also speaks LLDP is connected on that port)"
snmpwalk -v2c -c "$RO_COMMUNITY" -On "$DEVICE_IP" "$OID_LLDP_NEIGHBORS"

hr
echo "3. LACP aggregation config table walk"
snmpwalk -v2c -c "$RO_COMMUNITY" -On "$DEVICE_IP" "$OID_LACP_CONFIG"

if [[ -n "$RW_COMMUNITY" ]]; then
  hr
  echo "4. SNMP SET round-trip test on LLDP tx interval (read, write back unchanged)"
  CURRENT=$(snmpget -v2c -c "$RO_COMMUNITY" -Ovq "$DEVICE_IP" "${OID_LLDP_TX_INTERVAL}.0")
  echo "   current tx interval: $CURRENT"
  snmpset -v2c -c "$RW_COMMUNITY" "$DEVICE_IP" "${OID_LLDP_TX_INTERVAL}.0" u "$CURRENT"
  echo "   re-reading to confirm SET was accepted:"
  snmpget -v2c -c "$RO_COMMUNITY" -Ov "$DEVICE_IP" "${OID_LLDP_TX_INTERVAL}.0"
else
  hr
  echo "4. Skipped SNMP SET test (no rw-community supplied)"
fi

hr
echo "Done. If steps 1, 2a and 3 returned data, direct-to-switch SNMPv2c is"
echo "confirmed for the ML540M. An empty 2b is expected if nothing LLDP-aware"
echo "is plugged into this unit right now — not a failure of the OID itself."
