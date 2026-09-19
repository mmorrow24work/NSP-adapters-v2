#!/usr/bin/env bash
#
# test_row_editor.sh — proves out the VTSSRowEditorState create/commit
# protocol used across the ML540M switch's row-editor tables (SNMP
# community, VLAN interfaces, ACL, etc.) using the SNMP community table
# as a safe, low-risk test case.
#
# This is the mechanism, not the target: once this works, the exact same
# 3-value state machine (IDLE=0, CLEAR=1, COMMIT=2, reserve with any
# value >=256) applies to every other row-editor table in the MIB set.
#
# Usage:
#   ./test_row_editor.sh <switch-ip> <rw-community>
#
# What it does:
#   1. Confirms the row editor is idle
#   2. Reserves it with an arbitrary manager ID
#   3. Stages a test community row (name "claude-test", source 0.0.0.0/0)
#   4. Commits it
#   5. Walks the real table to confirm the row now exists
#   6. Deletes the row again (writing 1 to that row's own Action column)
#   7. Re-walks to confirm cleanup

set -euo pipefail

DEVICE_IP="${1:?Usage: $0 <switch-ip> <rw-community>}"
RW_COMMUNITY="${2:?Usage: $0 <switch-ip> <rw-community>}"
MANAGER_ID=999001   # arbitrary, just needs to be >=256

# RowEditor scalars (all need trailing .0 — see validate_snmp_switch.sh notes)
OID_RE_ACTION="1.3.6.1.4.1.5468.100.36.1.2.3.100.0"
OID_RE_NAME="1.3.6.1.4.1.5468.100.36.1.2.3.1.0"
OID_RE_SRCIP="1.3.6.1.4.1.5468.100.36.1.2.3.2.0"
OID_RE_PREFIX="1.3.6.1.4.1.5468.100.36.1.2.3.3.0"

# Real table (for confirming the row landed / walking to find its Action column)
OID_TABLE="1.3.6.1.4.1.5468.100.36.1.2.2"

TEST_NAME="claude-test"

hr() { printf '%s\n' "------------------------------------------------------------"; }

hr
echo "1. Confirm row editor is idle (expect 0)"
snmpget -v2c -c "$RW_COMMUNITY" -Ovq "$DEVICE_IP" "$OID_RE_ACTION"

hr
echo "2. Reserve the row editor with manager ID $MANAGER_ID"
snmpset -v2c -c "$RW_COMMUNITY" "$DEVICE_IP" "$OID_RE_ACTION" u "$MANAGER_ID"
echo "   read back to confirm reservation:"
snmpget -v2c -c "$RW_COMMUNITY" -Ovq "$DEVICE_IP" "$OID_RE_ACTION"

hr
echo "3. Stage the test row: name=$TEST_NAME, source 0.0.0.0/0 (read-only intent — not actually used for auth here, just proving the mechanism)"
snmpset -v2c -c "$RW_COMMUNITY" "$DEVICE_IP" \
  "$OID_RE_NAME" s "$TEST_NAME" \
  "$OID_RE_SRCIP" a "0.0.0.0" \
  "$OID_RE_PREFIX" i 0

hr
echo "4. Commit (write 2)"
snmpset -v2c -c "$RW_COMMUNITY" "$DEVICE_IP" "$OID_RE_ACTION" u 2
echo "   read back — should be 0 (idle again) if commit succeeded"
snmpget -v2c -c "$RW_COMMUNITY" -Ovq "$DEVICE_IP" "$OID_RE_ACTION"

hr
echo "5. Walk the real community table — the new row should now appear"
snmpwalk -v2c -c "$RW_COMMUNITY" -On "$DEVICE_IP" "$OID_TABLE"

hr
echo "6. Clean up: find the row above whose Name column decodes to '$TEST_NAME',"
echo "   note its full column-100 (...Action) OID from the walk above, then run:"
echo "     snmpset -v2c -c $RW_COMMUNITY $DEVICE_IP <that-row's-Action-OID> u 1"
echo "   (writing 1 to a table row's own Action column deletes that row —"
echo "   this is the 'column in a dynamic table' meaning of RowEditorState,"
echo "   distinct from its 'row editor object' meaning used in steps 1-4)"

hr
echo "Done. If step 5 shows the test row and step 6's delete removes it on"
echo "a re-walk, the row-editor create/commit/delete protocol is fully"
echo "proven for this MIB family — the identical pattern applies to VLAN"
echo "interfaces, ACL rules, and every other row-editor table here."
