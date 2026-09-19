"""Row-editor specs generated from the vendor MIBs.

DO NOT EDIT BY HAND -- regenerate with:
    python3 tools/gen_row_editor_specs.py > src/actelis_mediation/rowedit/specs.py

64 tables in ML540M-MIB.7z use the VTSSRowEditorState mechanism
proven end-to-end against the lab unit on 2026-09-18
(docs/lab-results/ml540m-row-editor-20260918.txt). Only that one table --
SNMP_CONFIG_COMMUNITY_TABLE -- has been exercised on real hardware; the
rest are mechanically derived and carry the same protocol, but should be
treated as unproven per-table until walked against a device.
"""
from __future__ import annotations

from ..snmp.oid import IndexSpec
from . import EditorField, RowEditorSpec

ACCESS_MANAGEMENT_CONFIG_IPV4_TABLE = RowEditorSpec(
    name="ml540mAccessManagementConfigIpv4Table",
    action_oid="1.3.6.1.4.1.5468.100.51.1.2.3.100.0",
    table_oid="1.3.6.1.4.1.5468.100.51.1.2.2",
    row_action_column_oid="1.3.6.1.4.1.5468.100.51.1.2.2.1.100",
    index_spec=IndexSpec(names=['accessIndex'], kinds=['integer']),
    fields={
        'accessIndex': EditorField("1.3.6.1.4.1.5468.100.51.1.2.3.1.0", "i"),   # Integer32 (0..2147483647)
        'vlanId': EditorField("1.3.6.1.4.1.5468.100.51.1.2.3.2.0", "u"),   # VTSSUnsigned16
        'startAddress': EditorField("1.3.6.1.4.1.5468.100.51.1.2.3.3.0", "a"),   # IpAddress
        'endAddress': EditorField("1.3.6.1.4.1.5468.100.51.1.2.3.4.0", "a"),   # IpAddress
        'webServices': EditorField("1.3.6.1.4.1.5468.100.51.1.2.3.5.0", "i"),   # TruthValue
        'snmpServices': EditorField("1.3.6.1.4.1.5468.100.51.1.2.3.6.0", "i"),   # TruthValue
        'telnetServices': EditorField("1.3.6.1.4.1.5468.100.51.1.2.3.7.0", "i"),   # TruthValue
    },
)

ACCESS_MANAGEMENT_CONFIG_IPV6_TABLE = RowEditorSpec(
    name="ml540mAccessManagementConfigIpv6Table",
    action_oid="1.3.6.1.4.1.5468.100.51.1.2.5.100.0",
    table_oid="1.3.6.1.4.1.5468.100.51.1.2.4",
    row_action_column_oid="1.3.6.1.4.1.5468.100.51.1.2.4.1.100",
    index_spec=IndexSpec(names=['accessIndex'], kinds=['integer']),
    fields={
        'accessIndex': EditorField("1.3.6.1.4.1.5468.100.51.1.2.5.1.0", "i"),   # Integer32 (0..2147483647)
        'vlanId': EditorField("1.3.6.1.4.1.5468.100.51.1.2.5.2.0", "u"),   # VTSSUnsigned16
        'startAddress': EditorField("1.3.6.1.4.1.5468.100.51.1.2.5.3.0", "x"),   # InetAddressIPv6
        'endAddress': EditorField("1.3.6.1.4.1.5468.100.51.1.2.5.4.0", "x"),   # InetAddressIPv6
        'webServices': EditorField("1.3.6.1.4.1.5468.100.51.1.2.5.5.0", "i"),   # TruthValue
        'snmpServices': EditorField("1.3.6.1.4.1.5468.100.51.1.2.5.6.0", "i"),   # TruthValue
        'telnetServices': EditorField("1.3.6.1.4.1.5468.100.51.1.2.5.7.0", "i"),   # TruthValue
    },
)

ACL_CONFIG_ACE = RowEditorSpec(
    name="ml540mAclConfigAce",
    action_oid="1.3.6.1.4.1.5468.100.17.1.2.4.2.10000.0",
    table_oid="1.3.6.1.4.1.5468.100.17.1.2.4.1",
    row_action_column_oid="1.3.6.1.4.1.5468.100.17.1.2.4.1.1.10000",
    index_spec=IndexSpec(names=['aceId'], kinds=['integer']),
    fields={
        'aceId': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.1.0", "i"),   # Integer32 (0..2147483647)
        'nextAceId': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.2.0", "u"),   # Unsigned32
        'hitAction': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.101.0", "i"),   # VTSSAclHitAction
        'redirectPortList': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.102.0", "s"),   # VTSSPortList
        'redirectPortListSwitchPort': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.103.0", "u"),   # Unsigned32
        'egressPortList': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.104.0", "s"),   # VTSSPortList
        'rateLimiterId': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.105.0", "u"),   # Unsigned32
        'evcPolicerId': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.106.0", "u"),   # VTSSUnsigned16
        'mirror': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.107.0", "i"),   # TruthValue
        'logging': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.108.0", "i"),   # TruthValue
        'shutdown': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.109.0", "i"),   # TruthValue
        'ingressPortListMode': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.201.0", "i"),   # VTSSAclAceIngressPortListMode
        'ingressPortList': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.202.0", "s"),   # VTSSPortList
        'ingressPortListSwitch': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.203.0", "u"),   # Unsigned32
        'ingressPortListSwitchPort': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.204.0", "u"),   # Unsigned32
        'policyValue': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.205.0", "u"),   # VTSSUnsigned8
        'policyMask': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.206.0", "u"),   # VTSSUnsigned8
        'secondLookup': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.207.0", "i"),   # TruthValue
        'vlanId': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.301.0", "u"),   # VTSSUnsigned16
        'vlanTagPriority': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.302.0", "i"),   # VTSSVlanTagPriority
        'vlanTagged': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.303.0", "i"),   # VTSSAclAceVlanTagged
        'frameType': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.401.0", "i"),   # VTSSAclAceFrameType
        'destMacOp': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.402.0", "i"),   # VTSSAdvDestMacType
        'etherSrcMacOp': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.501.0", "i"),   # VTSSASType
        'etherSrcMac': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.502.0", "x"),   # MacAddress
        'etherDestMac': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.503.0", "x"),   # MacAddress
        'etherType': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.504.0", "u"),   # VTSSUnsigned16
        'arpSrcMacOp': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.601.0", "i"),   # VTSSASType
        'arpSrcMac': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.602.0", "x"),   # MacAddress
        'arpSenderIp': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.603.0", "a"),   # IpAddress
        'arpSenderIpMask': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.604.0", "a"),   # IpAddress
        'arpTargetIp': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.605.0", "a"),   # IpAddress
        'arpTargetIpMask': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.606.0", "a"),   # IpAddress
        'arpOpcode': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.607.0", "i"),   # VTSSAclAceArpOp
        'arpFlagReq': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.608.0", "i"),   # VTSSBitType
        'arpFlagSha': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.609.0", "i"),   # VTSSBitType
        'arpFlagTha': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.610.0", "i"),   # VTSSBitType
        'arpFlagHln': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.611.0", "i"),   # VTSSBitType
        'arpFlagHrd': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.612.0", "i"),   # VTSSBitType
        'arpFlagPro': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.613.0", "i"),   # VTSSBitType
        'ipv4ProtocolOp': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.701.0", "i"),   # VTSSASType
        'ipv4Protocol': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.702.0", "u"),   # VTSSUnsigned8
        'ipv4SrcIp': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.703.0", "a"),   # IpAddress
        'ipv4SrcIpMask': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.704.0", "a"),   # IpAddress
        'ipv4DestIp': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.705.0", "a"),   # IpAddress
        'ipv4DestIpMask': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.706.0", "a"),   # IpAddress
        'ipv4IcmpTypeOp': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.707.0", "i"),   # VTSSASType
        'ipv4IcmpType': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.708.0", "u"),   # VTSSUnsigned8
        'ipv4IcmpCodeOp': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.709.0", "i"),   # VTSSASType
        'ipv4IcmpCode': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.710.0", "u"),   # VTSSUnsigned8
        'ipv4SrcPortOp': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.711.0", "i"),   # VTSSASRType
        'ipv4SrcPort': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.712.0", "u"),   # VTSSUnsigned16
        'ipv4SrcPortRange': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.713.0", "u"),   # VTSSUnsigned16
        'ipv4DestPortOp': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.714.0", "i"),   # VTSSASRType
        'ipv4DestPort': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.715.0", "u"),   # VTSSUnsigned16
        'ipv4DestPortRange': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.716.0", "u"),   # VTSSUnsigned16
        'ipv4FlagTtl': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.717.0", "i"),   # VTSSBitType
        'ipv4FlagFragment': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.718.0", "i"),   # VTSSBitType
        'ipv4FlagIpOption': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.719.0", "i"),   # VTSSBitType
        'ipv4TcpFlagFin': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.720.0", "i"),   # VTSSBitType
        'ipv4TcpFlagSyn': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.721.0", "i"),   # VTSSBitType
        'ipv4TcpFlagRst': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.722.0", "i"),   # VTSSBitType
        'ipv4TcpFlagPsh': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.723.0", "i"),   # VTSSBitType
        'ipv4TcpFlagAck': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.724.0", "i"),   # VTSSBitType
        'ipv4TcpFlagUrg': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.725.0", "i"),   # VTSSBitType
        'ipv6NextHeaderOp': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.801.0", "i"),   # VTSSASType
        'ipv6NextHeader': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.802.0", "u"),   # VTSSUnsigned8
        'ipv6Icmpv6TypeOp': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.803.0", "i"),   # VTSSASType
        'ipv6Icmpv6Type': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.804.0", "u"),   # VTSSUnsigned8
        'ipv6Icmpv6CodeOp': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.805.0", "i"),   # VTSSASType
        'ipv6Icmpv6Code': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.806.0", "u"),   # VTSSUnsigned8
        'ipv6SrcIp': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.807.0", "x"),   # InetAddressIPv6
        'ipv6SrcIpMask': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.808.0", "x"),   # InetAddressIPv6
        'ipv6SrcPortOp': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.809.0", "i"),   # VTSSASRType
        'ipv6SrcPort': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.810.0", "u"),   # VTSSUnsigned16
        'ipv6SrcPortRange': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.811.0", "u"),   # VTSSUnsigned16
        'ipv6DestPortOp': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.812.0", "i"),   # VTSSASRType
        'ipv6DestPort': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.813.0", "u"),   # VTSSUnsigned16
        'ipv6DestPortRange': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.814.0", "u"),   # VTSSUnsigned16
        'ipv6FlagTtl': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.815.0", "i"),   # VTSSBitType
        'ipv6TcpFlagFin': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.816.0", "i"),   # VTSSBitType
        'ipv6TcpFlagSyn': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.817.0", "i"),   # VTSSBitType
        'ipv6TcpFlagRst': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.818.0", "i"),   # VTSSBitType
        'ipv6TcpFlagPsh': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.819.0", "i"),   # VTSSBitType
        'ipv6TcpFlagAck': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.820.0", "i"),   # VTSSBitType
        'ipv6TcpFlagUrg': EditorField("1.3.6.1.4.1.5468.100.17.1.2.4.2.821.0", "i"),   # VTSSBitType
    },
)

AGGR_CONFIG_GROUP_TABLE = RowEditorSpec(
    name="ml540mAggrConfigGroupTable",
    action_oid="1.3.6.1.4.1.5468.100.19.1.2.3.100.0",
    table_oid="1.3.6.1.4.1.5468.100.19.1.2.2",
    row_action_column_oid="1.3.6.1.4.1.5468.100.19.1.2.2.1.100",
    index_spec=IndexSpec(names=['aggrIndexNo'], kinds=['integer']),
    fields={
        'aggrIndexNo': EditorField("1.3.6.1.4.1.5468.100.19.1.2.3.1.0", "i"),   # VTSSInterfaceIndex
        'portMembers': EditorField("1.3.6.1.4.1.5468.100.19.1.2.3.2.0", "s"),   # VTSSPortList
    },
)

ARP_INSPECTION_CONFIG_STATIC_TABLE = RowEditorSpec(
    name="ml540mArpInspectionConfigStaticTable",
    action_oid="1.3.6.1.4.1.5468.100.63.1.2.6.100.0",
    table_oid="1.3.6.1.4.1.5468.100.63.1.2.5",
    row_action_column_oid="1.3.6.1.4.1.5468.100.63.1.2.5.1.100",
    index_spec=IndexSpec(names=['ifIndex', 'vlanId', 'macAddress', 'ipAddress'], kinds=['integer', 'integer', 'string', 'ipaddress']),
    fields={
        'ifIndex': EditorField("1.3.6.1.4.1.5468.100.63.1.2.6.1.0", "i"),   # VTSSInterfaceIndex
        'vlanId': EditorField("1.3.6.1.4.1.5468.100.63.1.2.6.2.0", "i"),   # Integer32 (1..4095)
        'macAddress': EditorField("1.3.6.1.4.1.5468.100.63.1.2.6.3.0", "x"),   # MacAddress
        'ipAddress': EditorField("1.3.6.1.4.1.5468.100.63.1.2.6.4.0", "a"),   # IpAddress
    },
)

ARP_INSPECTION_CONFIG_VLAN_TABLE = RowEditorSpec(
    name="ml540mArpInspectionConfigVlanTable",
    action_oid="1.3.6.1.4.1.5468.100.63.1.2.4.100.0",
    table_oid="1.3.6.1.4.1.5468.100.63.1.2.3",
    row_action_column_oid="1.3.6.1.4.1.5468.100.63.1.2.3.1.100",
    index_spec=IndexSpec(names=['vlanId'], kinds=['integer']),
    fields={
        'vlanId': EditorField("1.3.6.1.4.1.5468.100.63.1.2.4.1.0", "i"),   # Integer32 (1..4095)
        'logType': EditorField("1.3.6.1.4.1.5468.100.63.1.2.4.2.0", "i"),   # VTSSArpInspectionLogType
    },
)

DHCP6_CLIENT_CONFIG_INTERFACE_TABLE = RowEditorSpec(
    name="ml540mDhcp6ClientConfigInterfaceTable",
    action_oid="1.3.6.1.4.1.5468.100.126.1.2.1.2.100.0",
    table_oid="1.3.6.1.4.1.5468.100.126.1.2.1.1",
    row_action_column_oid="1.3.6.1.4.1.5468.100.126.1.2.1.1.1.100",
    index_spec=IndexSpec(names=['ifIndex'], kinds=['integer']),
    fields={
        'ifIndex': EditorField("1.3.6.1.4.1.5468.100.126.1.2.1.2.1.0", "i"),   # VTSSInterfaceIndex
        'rapidCommit': EditorField("1.3.6.1.4.1.5468.100.126.1.2.1.2.2.0", "i"),   # TruthValue
    },
)

DHCP_SERVER_CONFIG_EXCLUDED_IP_TABLE = RowEditorSpec(
    name="ml540mDhcpServerConfigExcludedIpTable",
    action_oid="1.3.6.1.4.1.5468.100.109.1.2.4.100.0",
    table_oid="1.3.6.1.4.1.5468.100.109.1.2.3",
    row_action_column_oid="1.3.6.1.4.1.5468.100.109.1.2.3.1.100",
    index_spec=IndexSpec(names=['lowIpAddress', 'highIpAddress'], kinds=['ipaddress', 'ipaddress']),
    fields={
        'lowIpAddress': EditorField("1.3.6.1.4.1.5468.100.109.1.2.4.1.0", "a"),   # IpAddress
        'highIpAddress': EditorField("1.3.6.1.4.1.5468.100.109.1.2.4.2.0", "a"),   # IpAddress
    },
)

DHCP_SERVER_CONFIG_POOL_TABLE = RowEditorSpec(
    name="ml540mDhcpServerConfigPoolTable",
    action_oid="1.3.6.1.4.1.5468.100.109.1.2.6.100.0",
    table_oid="1.3.6.1.4.1.5468.100.109.1.2.5",
    row_action_column_oid="1.3.6.1.4.1.5468.100.109.1.2.5.1.100",
    index_spec=IndexSpec(names=['poolName'], kinds=['string']),
    fields={
        'poolName': EditorField("1.3.6.1.4.1.5468.100.109.1.2.6.1.0", "s"),   # VTSSDisplayString (SIZE(0..32))
        'poolType': EditorField("1.3.6.1.4.1.5468.100.109.1.2.6.2.0", "i"),   # VTSSDhcpServerPoolEnum
        'ipv4Address': EditorField("1.3.6.1.4.1.5468.100.109.1.2.6.3.0", "a"),   # IpAddress
        'subnetMask': EditorField("1.3.6.1.4.1.5468.100.109.1.2.6.4.0", "a"),   # IpAddress
        'subnetBroadcast': EditorField("1.3.6.1.4.1.5468.100.109.1.2.6.5.0", "a"),   # IpAddress
        'leaseDay': EditorField("1.3.6.1.4.1.5468.100.109.1.2.6.6.0", "u"),   # Unsigned32
        'leaseHour': EditorField("1.3.6.1.4.1.5468.100.109.1.2.6.7.0", "u"),   # Unsigned32
        'leaseMinute': EditorField("1.3.6.1.4.1.5468.100.109.1.2.6.8.0", "u"),   # Unsigned32
        'domainName': EditorField("1.3.6.1.4.1.5468.100.109.1.2.6.9.0", "s"),   # VTSSDisplayString (SIZE(0..32))
        'defaultRouter1': EditorField("1.3.6.1.4.1.5468.100.109.1.2.6.10.0", "a"),   # IpAddress
        'defaultRouter2': EditorField("1.3.6.1.4.1.5468.100.109.1.2.6.11.0", "a"),   # IpAddress
        'defaultRouter3': EditorField("1.3.6.1.4.1.5468.100.109.1.2.6.12.0", "a"),   # IpAddress
        'defaultRouter4': EditorField("1.3.6.1.4.1.5468.100.109.1.2.6.13.0", "a"),   # IpAddress
        'dnsServer1': EditorField("1.3.6.1.4.1.5468.100.109.1.2.6.14.0", "a"),   # IpAddress
        'dnsServer2': EditorField("1.3.6.1.4.1.5468.100.109.1.2.6.15.0", "a"),   # IpAddress
        'dnsServer3': EditorField("1.3.6.1.4.1.5468.100.109.1.2.6.16.0", "a"),   # IpAddress
        'dnsServer4': EditorField("1.3.6.1.4.1.5468.100.109.1.2.6.17.0", "a"),   # IpAddress
        'ntpServer1': EditorField("1.3.6.1.4.1.5468.100.109.1.2.6.18.0", "a"),   # IpAddress
        'ntpServer2': EditorField("1.3.6.1.4.1.5468.100.109.1.2.6.19.0", "a"),   # IpAddress
        'ntpServer3': EditorField("1.3.6.1.4.1.5468.100.109.1.2.6.20.0", "a"),   # IpAddress
        'ntpServer4': EditorField("1.3.6.1.4.1.5468.100.109.1.2.6.21.0", "a"),   # IpAddress
        'netbiosNodeType': EditorField("1.3.6.1.4.1.5468.100.109.1.2.6.22.0", "i"),   # VTSSDhcpServerNetbiosNodeEnum
        'netbiosScope': EditorField("1.3.6.1.4.1.5468.100.109.1.2.6.23.0", "s"),   # VTSSDisplayString (SIZE(0..32))
        'netbiosNameServer1': EditorField("1.3.6.1.4.1.5468.100.109.1.2.6.24.0", "a"),   # IpAddress
        'netbiosNameServer2': EditorField("1.3.6.1.4.1.5468.100.109.1.2.6.25.0", "a"),   # IpAddress
        'netbiosNameServer3': EditorField("1.3.6.1.4.1.5468.100.109.1.2.6.26.0", "a"),   # IpAddress
        'netbiosNameServer4': EditorField("1.3.6.1.4.1.5468.100.109.1.2.6.27.0", "a"),   # IpAddress
        'nisDomainName': EditorField("1.3.6.1.4.1.5468.100.109.1.2.6.28.0", "s"),   # VTSSDisplayString (SIZE(0..32))
        'nisServer1': EditorField("1.3.6.1.4.1.5468.100.109.1.2.6.29.0", "a"),   # IpAddress
        'nisServer2': EditorField("1.3.6.1.4.1.5468.100.109.1.2.6.30.0", "a"),   # IpAddress
        'nisServer3': EditorField("1.3.6.1.4.1.5468.100.109.1.2.6.31.0", "a"),   # IpAddress
        'nisServer4': EditorField("1.3.6.1.4.1.5468.100.109.1.2.6.32.0", "a"),   # IpAddress
        'clientIdentifierType': EditorField("1.3.6.1.4.1.5468.100.109.1.2.6.33.0", "i"),   # VTSSDhcpServerClientIdentifierEnum
        'clientIdentifierFqdn': EditorField("1.3.6.1.4.1.5468.100.109.1.2.6.34.0", "s"),   # VTSSDisplayString (SIZE(0..64))
        'clientIdentifierMac': EditorField("1.3.6.1.4.1.5468.100.109.1.2.6.35.0", "x"),   # MacAddress
        'clientHardwareAddress': EditorField("1.3.6.1.4.1.5468.100.109.1.2.6.36.0", "x"),   # MacAddress
        'clientName': EditorField("1.3.6.1.4.1.5468.100.109.1.2.6.37.0", "s"),   # VTSSDisplayString (SIZE(0..32))
        'vendorClassId1': EditorField("1.3.6.1.4.1.5468.100.109.1.2.6.38.0", "s"),   # VTSSDisplayString (SIZE(0..64))
        'vendorSpecificInfo1': EditorField("1.3.6.1.4.1.5468.100.109.1.2.6.39.0", "s"),   # VTSSDisplayString (SIZE(0..66))
        'vendorClassId2': EditorField("1.3.6.1.4.1.5468.100.109.1.2.6.40.0", "s"),   # VTSSDisplayString (SIZE(0..64))
        'vendorSpecificInfo2': EditorField("1.3.6.1.4.1.5468.100.109.1.2.6.41.0", "s"),   # VTSSDisplayString (SIZE(0..66))
        'vendorClassId3': EditorField("1.3.6.1.4.1.5468.100.109.1.2.6.42.0", "s"),   # VTSSDisplayString (SIZE(0..64))
        'vendorSpecificInfo3': EditorField("1.3.6.1.4.1.5468.100.109.1.2.6.43.0", "s"),   # VTSSDisplayString (SIZE(0..66))
        'vendorClassId4': EditorField("1.3.6.1.4.1.5468.100.109.1.2.6.44.0", "s"),   # VTSSDisplayString (SIZE(0..64))
        'vendorSpecificInfo4': EditorField("1.3.6.1.4.1.5468.100.109.1.2.6.45.0", "s"),   # VTSSDisplayString (SIZE(0..66))
    },
)

EPS_CONFIG_INSTANCE = RowEditorSpec(
    name="ml540mEpsConfigInstance",
    action_oid="1.3.6.1.4.1.5468.100.45.1.2.2.100.0",
    table_oid="1.3.6.1.4.1.5468.100.45.1.2.1",
    row_action_column_oid="1.3.6.1.4.1.5468.100.45.1.2.1.1.100",
    index_spec=IndexSpec(names=['id'], kinds=['integer']),
    fields={
        'id': EditorField("1.3.6.1.4.1.5468.100.45.1.2.2.1.0", "i"),   # Integer32 (0..2147483647)
        'architecture': EditorField("1.3.6.1.4.1.5468.100.45.1.2.2.2.0", "i"),   # VTSSEpsArchitecture
        'workingFlow': EditorField("1.3.6.1.4.1.5468.100.45.1.2.2.3.0", "i"),   # VTSSInterfaceIndex
        'protectingFlow': EditorField("1.3.6.1.4.1.5468.100.45.1.2.2.4.0", "i"),   # VTSSInterfaceIndex
    },
)

ERPS_CONFIG = RowEditorSpec(
    name="ml540mErpsConfig",
    action_oid="1.3.6.1.4.1.5468.100.72.1.2.2.100.0",
    table_oid="1.3.6.1.4.1.5468.100.72.1.2.1",
    row_action_column_oid="1.3.6.1.4.1.5468.100.72.1.2.1.1.100",
    index_spec=IndexSpec(names=['groupIndex'], kinds=['integer']),
    fields={
        'groupIndex': EditorField("1.3.6.1.4.1.5468.100.72.1.2.2.1.0", "i"),   # Integer32 (0..2147483647)
        'ringType': EditorField("1.3.6.1.4.1.5468.100.72.1.2.2.2.0", "i"),   # VTSSErpsRingType
        'port0': EditorField("1.3.6.1.4.1.5468.100.72.1.2.2.3.0", "i"),   # VTSSInterfaceIndex
        'port1': EditorField("1.3.6.1.4.1.5468.100.72.1.2.2.4.0", "i"),   # VTSSInterfaceIndex
        'interconnectMajorRingGroupIndex': EditorField("1.3.6.1.4.1.5468.100.72.1.2.2.5.0", "u"),   # Unsigned32
        'virtualChannel': EditorField("1.3.6.1.4.1.5468.100.72.1.2.2.6.0", "i"),   # TruthValue
        'port0SignalFailMepIndex': EditorField("1.3.6.1.4.1.5468.100.72.1.2.2.7.0", "u"),   # Unsigned32
        'port0ApsMepIndex': EditorField("1.3.6.1.4.1.5468.100.72.1.2.2.8.0", "u"),   # Unsigned32
        'port1SignalFailMepIndex': EditorField("1.3.6.1.4.1.5468.100.72.1.2.2.9.0", "u"),   # Unsigned32
        'port1ApsMepIndex': EditorField("1.3.6.1.4.1.5468.100.72.1.2.2.10.0", "u"),   # Unsigned32
        'holdOffTime': EditorField("1.3.6.1.4.1.5468.100.72.1.2.2.11.0", "u"),   # Unsigned32
        'waitToRestoreTime': EditorField("1.3.6.1.4.1.5468.100.72.1.2.2.12.0", "u"),   # Unsigned32
        'guardTime': EditorField("1.3.6.1.4.1.5468.100.72.1.2.2.13.0", "u"),   # Unsigned32
        'rplMode': EditorField("1.3.6.1.4.1.5468.100.72.1.2.2.14.0", "i"),   # VTSSErpsRplMode
        'rplPort': EditorField("1.3.6.1.4.1.5468.100.72.1.2.2.15.0", "i"),   # VTSSErpsPort
        'revertive': EditorField("1.3.6.1.4.1.5468.100.72.1.2.2.16.0", "i"),   # TruthValue
        'version': EditorField("1.3.6.1.4.1.5468.100.72.1.2.2.17.0", "i"),   # VTSSErpsVersion
        'topologyChange': EditorField("1.3.6.1.4.1.5468.100.72.1.2.2.18.0", "i"),   # TruthValue
        'protectedVlans0Kto1K': EditorField("1.3.6.1.4.1.5468.100.72.1.2.2.19.0", "s"),   # VTSSVlanListQuarter
        'protectedVlans1Kto2K': EditorField("1.3.6.1.4.1.5468.100.72.1.2.2.20.0", "s"),   # VTSSVlanListQuarter
        'protectedVlans2Kto3K': EditorField("1.3.6.1.4.1.5468.100.72.1.2.2.21.0", "s"),   # VTSSVlanListQuarter
        'protectedVlans3Kto4K': EditorField("1.3.6.1.4.1.5468.100.72.1.2.2.22.0", "s"),   # VTSSVlanListQuarter
    },
)

EVC_CONFIG_ECE_TABLE = RowEditorSpec(
    name="ml540mEvcConfigEceTable",
    action_oid="1.3.6.1.4.1.5468.100.62.1.2.5.2.10000.0",
    table_oid="1.3.6.1.4.1.5468.100.62.1.2.5.1",
    row_action_column_oid="1.3.6.1.4.1.5468.100.62.1.2.5.1.1.10000",
    index_spec=IndexSpec(names=['eceId'], kinds=['integer']),
    fields={
        'eceId': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.1.0", "i"),   # Integer32 (1..4096)
        'nextId': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.2.0", "u"),   # Unsigned32
        'advLookup': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.3.0", "i"),   # TruthValue
        'uniPortList': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.4.0", "s"),   # VTSSPortList
        'srcMac': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.10.0", "x"),   # MacAddress
        'srcMacMask': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.11.0", "x"),   # MacAddress
        'destMacType': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.12.0", "i"),   # VTSSDestMacType
        'destMac': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.13.0", "x"),   # MacAddress
        'destMacMask': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.14.0", "x"),   # MacAddress
        'otMatchType': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.20.0", "i"),   # VTSSVlanTagType
        'otMatchVid': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.21.0", "u"),   # Unsigned32
        'otMatchPcp': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.22.0", "i"),   # VTSSVlanTagPriority
        'otMatchDei': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.23.0", "i"),   # VTSSBitType
        'itMatchType': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.30.0", "i"),   # VTSSVlanTagType
        'itMatchVid': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.31.0", "u"),   # Unsigned32
        'itMatchPcp': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.32.0", "i"),   # VTSSVlanTagPriority
        'itMatchDei': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.33.0", "i"),   # VTSSBitType
        'frameType': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.50.0", "i"),   # VTSSevcFrameType
        'etype': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.100.0", "u"),   # VTSSUnsigned16
        'etypeMask': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.101.0", "u"),   # VTSSUnsigned16
        'etypeData': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.102.0", "u"),   # VTSSUnsigned16
        'etypeDataMask': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.103.0", "u"),   # VTSSUnsigned16
        'llcDsap': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.200.0", "u"),   # VTSSUnsigned8
        'llcDsapMask': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.201.0", "u"),   # VTSSUnsigned8
        'llcSsap': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.202.0", "u"),   # VTSSUnsigned8
        'llcSsapMask': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.203.0", "u"),   # VTSSUnsigned8
        'llcControl': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.204.0", "u"),   # VTSSUnsigned8
        'llcControlMask': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.205.0", "u"),   # VTSSUnsigned8
        'llcPid': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.206.0", "u"),   # VTSSUnsigned16
        'llcPidMask': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.207.0", "u"),   # VTSSUnsigned16
        'snapOui': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.300.0", "u"),   # Unsigned32
        'snapOuiMask': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.301.0", "u"),   # Unsigned32
        'snapPid': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.302.0", "u"),   # VTSSUnsigned16
        'snapPidMask': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.303.0", "u"),   # VTSSUnsigned16
        'l2cpType': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.400.0", "i"),   # VTSSevcL2cpType
        'ipv4Dscp': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.500.0", "u"),   # Unsigned32
        'ipv4Proto': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.501.0", "u"),   # VTSSUnsigned8
        'ipv4ProtoMask': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.502.0", "u"),   # VTSSUnsigned8
        'ipv4Fragment': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.503.0", "i"),   # VTSSBitType
        'ipv4SrcIp': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.504.0", "a"),   # IpAddress
        'ipv4SrcIpMask': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.505.0", "a"),   # IpAddress
        'ipv4DestIp': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.506.0", "a"),   # IpAddress
        'ipv4DestIpMask': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.507.0", "a"),   # IpAddress
        'ipv4SrcPort': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.508.0", "u"),   # Unsigned32
        'ipv4DestPort': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.509.0", "u"),   # Unsigned32
        'ipv6Dscp': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.600.0", "u"),   # Unsigned32
        'ipv6Proto': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.601.0", "u"),   # VTSSUnsigned8
        'ipv6ProtoMask': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.602.0", "u"),   # VTSSUnsigned8
        'ipv6SrcIp': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.603.0", "x"),   # InetAddressIPv6
        'ipv6SrcIpMask': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.604.0", "x"),   # InetAddressIPv6
        'ipv6DestIp': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.605.0", "x"),   # InetAddressIPv6
        'ipv6DestIpMask': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.606.0", "x"),   # InetAddressIPv6
        'ipv6SrcPort': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.607.0", "u"),   # Unsigned32
        'ipv6DestPort': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.608.0", "u"),   # Unsigned32
        'direction': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.1000.0", "i"),   # VTSSevcDirection
        'ruleType': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.1010.0", "i"),   # VTSSevcRuleType
        'txLookup': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.1011.0", "i"),   # VTSSevcTxLookup
        'popTag': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.1020.0", "i"),   # VTSSevcPopTag
        'otAddEnable': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.1100.0", "i"),   # TruthValue
        'otAddVid': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.1101.0", "u"),   # VTSSUnsigned16
        'otAddPcpMode': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.1102.0", "i"),   # VTSSevcPcpMode
        'otAddPcpDeiPreserve': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.1103.0", "i"),   # TruthValue
        'otAddPcp': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.1104.0", "u"),   # Unsigned32
        'otAddDeiMode': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.1105.0", "i"),   # VTSSevcDeiMode
        'otAddDei': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.1106.0", "u"),   # VTSSUnsigned8
        'itAddType': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.1200.0", "i"),   # VTSSevcInnerTagType
        'itAddVid': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.1201.0", "u"),   # VTSSUnsigned16
        'itAddPcpMode': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.1202.0", "i"),   # VTSSevcPcpMode
        'itAddPcpDeiPreserve': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.1203.0", "i"),   # TruthValue
        'itAddPcp': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.1204.0", "u"),   # Unsigned32
        'itAddDeiMode': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.1205.0", "i"),   # VTSSevcDeiMode
        'itAddDei': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.1206.0", "u"),   # VTSSUnsigned8
        'evcId': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.1300.0", "u"),   # VTSSUnsigned16
        'policerOp': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.1301.0", "i"),   # VTSSevcPolicerOp
        'policerId': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.1302.0", "u"),   # VTSSUnsigned16
        'policyNo': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.1310.0", "u"),   # Unsigned32
        'cosEnable': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.1320.0", "i"),   # TruthValue
        'cos': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.1321.0", "u"),   # Unsigned32
        'dpEnable': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.1330.0", "i"),   # TruthValue
        'dp': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.1331.0", "u"),   # VTSSUnsigned8
        'l2cpMode': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.1332.0", "i"),   # VTSSevcEceL2cpMode
        'l2cpDmac': EditorField("1.3.6.1.4.1.5468.100.62.1.2.5.2.1333.0", "i"),   # VTSSevcL2cpDmac
    },
)

EVC_CONFIG_EVC_TABLE = RowEditorSpec(
    name="ml540mEvcConfigEvcTable",
    action_oid="1.3.6.1.4.1.5468.100.62.1.2.4.2.10000.0",
    table_oid="1.3.6.1.4.1.5468.100.62.1.2.4.1",
    row_action_column_oid="1.3.6.1.4.1.5468.100.62.1.2.4.1.1.10000",
    index_spec=IndexSpec(names=['evcId'], kinds=['integer']),
    fields={
        'evcId': EditorField("1.3.6.1.4.1.5468.100.62.1.2.4.2.1.0", "i"),   # Integer32 (0..4095)
        'vid': EditorField("1.3.6.1.4.1.5468.100.62.1.2.4.2.2.0", "u"),   # VTSSUnsigned16
        'ivid': EditorField("1.3.6.1.4.1.5468.100.62.1.2.4.2.3.0", "u"),   # VTSSUnsigned16
        'nniPortList': EditorField("1.3.6.1.4.1.5468.100.62.1.2.4.2.4.0", "s"),   # VTSSPortList
        'learning': EditorField("1.3.6.1.4.1.5468.100.62.1.2.4.2.5.0", "i"),   # TruthValue
        'policerOp': EditorField("1.3.6.1.4.1.5468.100.62.1.2.4.2.6.0", "i"),   # VTSSevcPolicerOp
        'policerId': EditorField("1.3.6.1.4.1.5468.100.62.1.2.4.2.7.0", "u"),   # VTSSUnsigned16
        'uniVid': EditorField("1.3.6.1.4.1.5468.100.62.1.2.4.2.8.0", "u"),   # VTSSUnsigned16
        'itAddType': EditorField("1.3.6.1.4.1.5468.100.62.1.2.4.2.9.0", "i"),   # VTSSevcInnerTagType
        'itInnerVid': EditorField("1.3.6.1.4.1.5468.100.62.1.2.4.2.10.0", "i"),   # TruthValue
        'itAddVid': EditorField("1.3.6.1.4.1.5468.100.62.1.2.4.2.11.0", "u"),   # VTSSUnsigned16
        'itAddPcpDeiPreserve': EditorField("1.3.6.1.4.1.5468.100.62.1.2.4.2.12.0", "i"),   # TruthValue
        'itAddPcp': EditorField("1.3.6.1.4.1.5468.100.62.1.2.4.2.13.0", "u"),   # Unsigned32
        'itAddDei': EditorField("1.3.6.1.4.1.5468.100.62.1.2.4.2.14.0", "u"),   # VTSSUnsigned8
        'leafVid': EditorField("1.3.6.1.4.1.5468.100.62.1.2.4.2.15.0", "u"),   # VTSSUnsigned16
        'leafIvid': EditorField("1.3.6.1.4.1.5468.100.62.1.2.4.2.16.0", "u"),   # VTSSUnsigned16
        'leafPortList': EditorField("1.3.6.1.4.1.5468.100.62.1.2.4.2.17.0", "s"),   # VTSSPortList
    },
)

EVC_CONFIG_MPLS_TP_PW_TABLE = RowEditorSpec(
    name="ml540mEvcConfigMplsTpPwTable",
    action_oid="1.3.6.1.4.1.5468.100.62.1.2.7.2.10000.0",
    table_oid="1.3.6.1.4.1.5468.100.62.1.2.7.1",
    row_action_column_oid="1.3.6.1.4.1.5468.100.62.1.2.7.1.1.10000",
    index_spec=IndexSpec(names=['evcId', 'ifIndex'], kinds=['integer', 'integer']),
    fields={
        'evcId': EditorField("1.3.6.1.4.1.5468.100.62.1.2.7.2.1.0", "i"),   # Integer32 (0..4095)
        'ifIndex': EditorField("1.3.6.1.4.1.5468.100.62.1.2.7.2.2.0", "i"),   # VTSSInterfaceIndex
        'splitHorizon': EditorField("1.3.6.1.4.1.5468.100.62.1.2.7.2.4.0", "i"),   # TruthValue
    },
)

HQOS_CONFIG_INTERFACE_HQOS_TABLE = RowEditorSpec(
    name="ml540mHqosConfigInterfaceHqosTable",
    action_oid="1.3.6.1.4.1.5468.100.125.1.2.2.3.10000.0",
    table_oid="1.3.6.1.4.1.5468.100.125.1.2.2.2",
    row_action_column_oid="1.3.6.1.4.1.5468.100.125.1.2.2.2.1.10000",
    index_spec=IndexSpec(names=['ifIndex', 'hqosId'], kinds=['integer', 'integer']),
    fields={
        'ifIndex': EditorField("1.3.6.1.4.1.5468.100.125.1.2.2.3.1.0", "i"),   # VTSSInterfaceIndex
        'hqosId': EditorField("1.3.6.1.4.1.5468.100.125.1.2.2.3.2.0", "i"),   # Integer32 (0..255)
        'dwrrCount': EditorField("1.3.6.1.4.1.5468.100.125.1.2.2.3.3.0", "u"),   # VTSSUnsigned8
        'shaperEnable': EditorField("1.3.6.1.4.1.5468.100.125.1.2.2.3.4.0", "i"),   # TruthValue
        'shaperRate': EditorField("1.3.6.1.4.1.5468.100.125.1.2.2.3.5.0", "u"),   # Unsigned32
        'minRate': EditorField("1.3.6.1.4.1.5468.100.125.1.2.2.3.6.0", "u"),   # Unsigned32
        'shaperRateType': EditorField("1.3.6.1.4.1.5468.100.125.1.2.2.3.7.0", "i"),   # VTSSHqosShaperRateType
    },
)

IP_CONFIG_INTERFACES_TABLE = RowEditorSpec(
    name="ml540mIpConfigInterfacesTable",
    action_oid="1.3.6.1.4.1.5468.100.102.1.2.2.2.100.0",
    table_oid="1.3.6.1.4.1.5468.100.102.1.2.2.1",
    row_action_column_oid="1.3.6.1.4.1.5468.100.102.1.2.2.1.1.100",
    index_spec=IndexSpec(names=['ifIndex'], kinds=['integer']),
    fields={
        'ifIndex': EditorField("1.3.6.1.4.1.5468.100.102.1.2.2.2.1.0", "i"),   # VTSSInterfaceIndex
    },
)

IP_CONFIG_ROUTES_IPV4 = RowEditorSpec(
    name="ml540mIpConfigRoutesIpv4",
    action_oid="1.3.6.1.4.1.5468.100.102.1.2.3.2.100.0",
    table_oid="1.3.6.1.4.1.5468.100.102.1.2.3.1",
    row_action_column_oid="1.3.6.1.4.1.5468.100.102.1.2.3.1.1.100",
    index_spec=IndexSpec(names=['networkAddress', 'networkPrefixSize', 'nextHop'], kinds=['ipaddress', 'integer', 'ipaddress']),
    fields={
        'networkAddress': EditorField("1.3.6.1.4.1.5468.100.102.1.2.3.2.1.0", "a"),   # IpAddress
        'networkPrefixSize': EditorField("1.3.6.1.4.1.5468.100.102.1.2.3.2.2.0", "i"),   # Integer32 (0..32)
        'nextHop': EditorField("1.3.6.1.4.1.5468.100.102.1.2.3.2.3.0", "a"),   # IpAddress
    },
)

IP_CONFIG_ROUTES_IPV6 = RowEditorSpec(
    name="ml540mIpConfigRoutesIpv6",
    action_oid="1.3.6.1.4.1.5468.100.102.1.2.3.4.100.0",
    table_oid="1.3.6.1.4.1.5468.100.102.1.2.3.3",
    row_action_column_oid="1.3.6.1.4.1.5468.100.102.1.2.3.3.1.100",
    index_spec=IndexSpec(names=['networkAddress', 'networkPrefixSize', 'nextHop', 'nextHopInterface'], kinds=['string', 'integer', 'string', 'integer']),
    fields={
        'networkAddress': EditorField("1.3.6.1.4.1.5468.100.102.1.2.3.4.1.0", "x"),   # InetAddressIPv6
        'networkPrefixSize': EditorField("1.3.6.1.4.1.5468.100.102.1.2.3.4.2.0", "i"),   # Integer32 (0..128)
        'nextHop': EditorField("1.3.6.1.4.1.5468.100.102.1.2.3.4.3.0", "x"),   # InetAddressIPv6
        'nextHopInterface': EditorField("1.3.6.1.4.1.5468.100.102.1.2.3.4.4.0", "i"),   # VTSSInterfaceIndex
    },
)

IPMC_MVR_CONFIG_INTERFACE_TABLE = RowEditorSpec(
    name="ml540mIpmcMvrConfigInterfaceTable",
    action_oid="1.3.6.1.4.1.5468.100.68.1.2.4.100.0",
    table_oid="1.3.6.1.4.1.5468.100.68.1.2.3",
    row_action_column_oid="1.3.6.1.4.1.5468.100.68.1.2.3.1.100",
    index_spec=IndexSpec(names=['ifIndex'], kinds=['integer']),
    fields={
        'ifIndex': EditorField("1.3.6.1.4.1.5468.100.68.1.2.4.1.0", "i"),   # VTSSInterfaceIndex
        'name': EditorField("1.3.6.1.4.1.5468.100.68.1.2.4.2.0", "s"),   # VTSSDisplayString (SIZE(0..16))
        'igmpQuerierAddress': EditorField("1.3.6.1.4.1.5468.100.68.1.2.4.3.0", "a"),   # IpAddress
        'mode': EditorField("1.3.6.1.4.1.5468.100.68.1.2.4.4.0", "i"),   # VTSSIpmcMvrVlanInterfaceMode
        'tagging': EditorField("1.3.6.1.4.1.5468.100.68.1.2.4.5.0", "i"),   # VTSSIpmcMvrVlanInterfaceTagging
        'priority': EditorField("1.3.6.1.4.1.5468.100.68.1.2.4.6.0", "u"),   # VTSSUnsigned8
        'lastListenerQueryInt': EditorField("1.3.6.1.4.1.5468.100.68.1.2.4.7.0", "u"),   # Unsigned32
        'channelProfile': EditorField("1.3.6.1.4.1.5468.100.68.1.2.4.8.0", "s"),   # VTSSDisplayString (SIZE(0..16))
    },
)

IPMC_PROFILE_CONFIG_IPV4_ADDRESS_RANGE_TABLE = RowEditorSpec(
    name="ml540mIpmcProfileConfigIpv4AddressRangeTable",
    action_oid="1.3.6.1.4.1.5468.100.38.1.2.5.100.0",
    table_oid="1.3.6.1.4.1.5468.100.38.1.2.4",
    row_action_column_oid="1.3.6.1.4.1.5468.100.38.1.2.4.1.100",
    index_spec=IndexSpec(names=['rangeName'], kinds=['string']),
    fields={
        'rangeName': EditorField("1.3.6.1.4.1.5468.100.38.1.2.5.1.0", "s"),   # VTSSDisplayString (SIZE(0..16))
        'startAddress': EditorField("1.3.6.1.4.1.5468.100.38.1.2.5.2.0", "a"),   # IpAddress
        'endAddress': EditorField("1.3.6.1.4.1.5468.100.38.1.2.5.3.0", "a"),   # IpAddress
    },
)

IPMC_PROFILE_CONFIG_IPV6_ADDRESS_RANGE_TABLE = RowEditorSpec(
    name="ml540mIpmcProfileConfigIpv6AddressRangeTable",
    action_oid="1.3.6.1.4.1.5468.100.38.1.2.7.100.0",
    table_oid="1.3.6.1.4.1.5468.100.38.1.2.6",
    row_action_column_oid="1.3.6.1.4.1.5468.100.38.1.2.6.1.100",
    index_spec=IndexSpec(names=['rangeName'], kinds=['string']),
    fields={
        'rangeName': EditorField("1.3.6.1.4.1.5468.100.38.1.2.7.1.0", "s"),   # VTSSDisplayString (SIZE(0..16))
        'startAddress': EditorField("1.3.6.1.4.1.5468.100.38.1.2.7.2.0", "x"),   # InetAddressIPv6
        'endAddress': EditorField("1.3.6.1.4.1.5468.100.38.1.2.7.3.0", "x"),   # InetAddressIPv6
    },
)

IPMC_PROFILE_CONFIG_MANAGEMENT_TABLE = RowEditorSpec(
    name="ml540mIpmcProfileConfigManagementTable",
    action_oid="1.3.6.1.4.1.5468.100.38.1.2.3.100.0",
    table_oid="1.3.6.1.4.1.5468.100.38.1.2.2",
    row_action_column_oid="1.3.6.1.4.1.5468.100.38.1.2.2.1.100",
    index_spec=IndexSpec(names=['profileName'], kinds=['string']),
    fields={
        'profileName': EditorField("1.3.6.1.4.1.5468.100.38.1.2.3.1.0", "s"),   # VTSSDisplayString (SIZE(0..16))
        'profileDescription': EditorField("1.3.6.1.4.1.5468.100.38.1.2.3.2.0", "s"),   # VTSSDisplayString (SIZE(0..64))
    },
)

IPMC_PROFILE_CONFIG_RULE_TABLE = RowEditorSpec(
    name="ml540mIpmcProfileConfigRuleTable",
    action_oid="1.3.6.1.4.1.5468.100.38.1.2.9.100.0",
    table_oid="1.3.6.1.4.1.5468.100.38.1.2.8",
    row_action_column_oid="1.3.6.1.4.1.5468.100.38.1.2.8.1.100",
    index_spec=IndexSpec(names=['profileName', 'ruleRange'], kinds=['string', 'string']),
    fields={
        'profileName': EditorField("1.3.6.1.4.1.5468.100.38.1.2.9.1.0", "s"),   # VTSSDisplayString (SIZE(0..16))
        'ruleRange': EditorField("1.3.6.1.4.1.5468.100.38.1.2.9.2.0", "s"),   # VTSSDisplayString (SIZE(0..16))
        'nextRuleRange': EditorField("1.3.6.1.4.1.5468.100.38.1.2.9.3.0", "s"),   # VTSSDisplayString (SIZE(0..16))
        'ruleAction': EditorField("1.3.6.1.4.1.5468.100.38.1.2.9.4.0", "i"),   # VTSSIpmcProfileRuleActionType
        'ruleLog': EditorField("1.3.6.1.4.1.5468.100.38.1.2.9.5.0", "i"),   # TruthValue
    },
)

IPMC_SNOOPING_CONFIG_IGMP_INTERFACE_TABLE = RowEditorSpec(
    name="ml540mIpmcSnoopingConfigIgmpInterfaceTable",
    action_oid="1.3.6.1.4.1.5468.100.69.1.2.4.100.0",
    table_oid="1.3.6.1.4.1.5468.100.69.1.2.3",
    row_action_column_oid="1.3.6.1.4.1.5468.100.69.1.2.3.1.100",
    index_spec=IndexSpec(names=['ifIndex'], kinds=['integer']),
    fields={
        'ifIndex': EditorField("1.3.6.1.4.1.5468.100.69.1.2.4.1.0", "i"),   # VTSSInterfaceIndex
        'adminState': EditorField("1.3.6.1.4.1.5468.100.69.1.2.4.2.0", "i"),   # TruthValue
        'querierElection': EditorField("1.3.6.1.4.1.5468.100.69.1.2.4.3.0", "i"),   # TruthValue
        'querierAddress': EditorField("1.3.6.1.4.1.5468.100.69.1.2.4.4.0", "a"),   # IpAddress
        'compatibility': EditorField("1.3.6.1.4.1.5468.100.69.1.2.4.5.0", "i"),   # VTSSIpmcSnoopingIgmpInterfaceCompatibilityEn
        'priority': EditorField("1.3.6.1.4.1.5468.100.69.1.2.4.6.0", "u"),   # VTSSUnsigned8
        'rv': EditorField("1.3.6.1.4.1.5468.100.69.1.2.4.7.0", "u"),   # Unsigned32
        'qi': EditorField("1.3.6.1.4.1.5468.100.69.1.2.4.8.0", "u"),   # Unsigned32
        'qri': EditorField("1.3.6.1.4.1.5468.100.69.1.2.4.9.0", "u"),   # Unsigned32
        'lmqi': EditorField("1.3.6.1.4.1.5468.100.69.1.2.4.10.0", "u"),   # Unsigned32
        'uri': EditorField("1.3.6.1.4.1.5468.100.69.1.2.4.11.0", "u"),   # Unsigned32
    },
)

IPMC_SNOOPING_CONFIG_MLD_INTERFACE_TABLE = RowEditorSpec(
    name="ml540mIpmcSnoopingConfigMldInterfaceTable",
    action_oid="1.3.6.1.4.1.5468.100.69.1.2.8.100.0",
    table_oid="1.3.6.1.4.1.5468.100.69.1.2.7",
    row_action_column_oid="1.3.6.1.4.1.5468.100.69.1.2.7.1.100",
    index_spec=IndexSpec(names=['ifIndex'], kinds=['integer']),
    fields={
        'ifIndex': EditorField("1.3.6.1.4.1.5468.100.69.1.2.8.1.0", "i"),   # VTSSInterfaceIndex
        'adminState': EditorField("1.3.6.1.4.1.5468.100.69.1.2.8.2.0", "i"),   # TruthValue
        'querierElection': EditorField("1.3.6.1.4.1.5468.100.69.1.2.8.3.0", "i"),   # TruthValue
        'compatibility': EditorField("1.3.6.1.4.1.5468.100.69.1.2.8.4.0", "i"),   # VTSSIpmcSnoopingMldInterfaceCompatibilityEnu
        'priority': EditorField("1.3.6.1.4.1.5468.100.69.1.2.8.5.0", "u"),   # VTSSUnsigned8
        'rv': EditorField("1.3.6.1.4.1.5468.100.69.1.2.8.6.0", "u"),   # Unsigned32
        'qi': EditorField("1.3.6.1.4.1.5468.100.69.1.2.8.7.0", "u"),   # Unsigned32
        'qri': EditorField("1.3.6.1.4.1.5468.100.69.1.2.8.8.0", "u"),   # Unsigned32
        'llqi': EditorField("1.3.6.1.4.1.5468.100.69.1.2.8.9.0", "u"),   # Unsigned32
        'uri': EditorField("1.3.6.1.4.1.5468.100.69.1.2.8.10.0", "u"),   # Unsigned32
    },
)

JSON_RPC_NOTIFICATION_CONFIG_DESTINATION = RowEditorSpec(
    name="ml540mJsonRpcNotificationConfigDestination",
    action_oid="1.3.6.1.4.1.5468.100.129.1.2.2.100.0",
    table_oid="1.3.6.1.4.1.5468.100.129.1.2.1",
    row_action_column_oid="1.3.6.1.4.1.5468.100.129.1.2.1.1.100",
    index_spec=IndexSpec(names=['name'], kinds=['string']),
    fields={
        'name': EditorField("1.3.6.1.4.1.5468.100.129.1.2.2.1.0", "s"),   # VTSSDisplayString (SIZE(0..16))
        'url': EditorField("1.3.6.1.4.1.5468.100.129.1.2.2.2.0", "s"),   # VTSSDisplayString (SIZE(0..254))
        'authType': EditorField("1.3.6.1.4.1.5468.100.129.1.2.2.3.0", "i"),   # VTSSJsonRpcNotificationDestAuthType
        'username': EditorField("1.3.6.1.4.1.5468.100.129.1.2.2.4.0", "s"),   # VTSSDisplayString (SIZE(0..32))
        'password': EditorField("1.3.6.1.4.1.5468.100.129.1.2.2.5.0", "s"),   # VTSSDisplayString (SIZE(0..32))
    },
)

JSON_RPC_NOTIFICATION_CONFIG_NOTIFICATION = RowEditorSpec(
    name="ml540mJsonRpcNotificationConfigNotification",
    action_oid="1.3.6.1.4.1.5468.100.129.1.2.4.100.0",
    table_oid="1.3.6.1.4.1.5468.100.129.1.2.3",
    row_action_column_oid="1.3.6.1.4.1.5468.100.129.1.2.3.1.100",
    index_spec=IndexSpec(names=['destination', 'notification'], kinds=['string', 'string']),
    fields={
        'destination': EditorField("1.3.6.1.4.1.5468.100.129.1.2.4.1.0", "s"),   # VTSSDisplayString (SIZE(0..16))
        'notification': EditorField("1.3.6.1.4.1.5468.100.129.1.2.4.2.0", "s"),   # VTSSDisplayString (SIZE(0..96))
    },
)

LLDP_CONFIG_MED_POLICY = RowEditorSpec(
    name="ml540mLldpConfigMedPolicy",
    action_oid="1.3.6.1.4.1.5468.100.34.1.2.3.6.100.0",
    table_oid="1.3.6.1.4.1.5468.100.34.1.2.3.2",
    row_action_column_oid="1.3.6.1.4.1.5468.100.34.1.2.3.2.1.100",
    index_spec=IndexSpec(names=['lldpmedPolicy'], kinds=['integer']),
    fields={
        'lldpmedPolicy': EditorField("1.3.6.1.4.1.5468.100.34.1.2.3.6.1.0", "i"),   # Integer32 (0..31)
        'applicationType': EditorField("1.3.6.1.4.1.5468.100.34.1.2.3.6.3.0", "i"),   # VTSSlldpmedRemoteNetworkPolicyApplicationTyp
        'tagged': EditorField("1.3.6.1.4.1.5468.100.34.1.2.3.6.4.0", "i"),   # TruthValue
        'vlanId': EditorField("1.3.6.1.4.1.5468.100.34.1.2.3.6.5.0", "u"),   # VTSSUnsigned16 (1..4095)
        'l2Priority': EditorField("1.3.6.1.4.1.5468.100.34.1.2.3.6.6.0", "u"),   # VTSSUnsigned8 (0..7)
        'dscp': EditorField("1.3.6.1.4.1.5468.100.34.1.2.3.6.7.0", "u"),   # VTSSUnsigned8 (0..63)
    },
)

MAC_CONFIG_FDB_TABLE = RowEditorSpec(
    name="ml540mMacConfigFdbTable",
    action_oid="1.3.6.1.4.1.5468.100.12.1.2.3.100.0",
    table_oid="1.3.6.1.4.1.5468.100.12.1.2.2",
    row_action_column_oid="1.3.6.1.4.1.5468.100.12.1.2.2.1.100",
    index_spec=IndexSpec(names=['vlanId', 'macAddress'], kinds=['integer', 'string']),
    fields={
        'vlanId': EditorField("1.3.6.1.4.1.5468.100.12.1.2.3.1.0", "u"),   # VTSSVlan
        'macAddress': EditorField("1.3.6.1.4.1.5468.100.12.1.2.3.2.0", "x"),   # MacAddress
        'portList': EditorField("1.3.6.1.4.1.5468.100.12.1.2.3.3.0", "s"),   # VTSSPortList
    },
)

MEP_CONFIG_AIS = RowEditorSpec(
    name="ml540mMepConfigAis",
    action_oid="1.3.6.1.4.1.5468.100.46.1.2.10.2.101.0",
    table_oid="1.3.6.1.4.1.5468.100.46.1.2.10.1",
    row_action_column_oid="1.3.6.1.4.1.5468.100.46.1.2.10.1.1.101",
    index_spec=IndexSpec(names=['id'], kinds=['integer']),
    fields={
        'id': EditorField("1.3.6.1.4.1.5468.100.46.1.2.10.2.1.0", "i"),   # Integer32 (0..2147483647)
        'protection': EditorField("1.3.6.1.4.1.5468.100.46.1.2.10.2.2.0", "i"),   # TruthValue
        'rate': EditorField("1.3.6.1.4.1.5468.100.46.1.2.10.2.3.0", "i"),   # VTSSMepTxRate
    },
)

MEP_CONFIG_APS = RowEditorSpec(
    name="ml540mMepConfigAps",
    action_oid="1.3.6.1.4.1.5468.100.46.1.2.9.2.101.0",
    table_oid="1.3.6.1.4.1.5468.100.46.1.2.9.1",
    row_action_column_oid="1.3.6.1.4.1.5468.100.46.1.2.9.1.1.101",
    index_spec=IndexSpec(names=['id'], kinds=['integer']),
    fields={
        'id': EditorField("1.3.6.1.4.1.5468.100.46.1.2.9.2.1.0", "i"),   # Integer32 (0..2147483647)
        'prio': EditorField("1.3.6.1.4.1.5468.100.46.1.2.9.2.3.0", "u"),   # Unsigned32
        'apsType': EditorField("1.3.6.1.4.1.5468.100.46.1.2.9.2.4.0", "i"),   # VTSSMepApsType
        'cast': EditorField("1.3.6.1.4.1.5468.100.46.1.2.9.2.5.0", "i"),   # VTSSMepCast
        'rapsOctet': EditorField("1.3.6.1.4.1.5468.100.46.1.2.9.2.6.0", "u"),   # Unsigned32
    },
)

MEP_CONFIG_BFD = RowEditorSpec(
    name="ml540mMepConfigBfd",
    action_oid="1.3.6.1.4.1.5468.100.46.1.2.15.2.100.0",
    table_oid="1.3.6.1.4.1.5468.100.46.1.2.15.1",
    row_action_column_oid="1.3.6.1.4.1.5468.100.46.1.2.15.1.1.100",
    index_spec=IndexSpec(names=['id'], kinds=['integer']),
    fields={
        'id': EditorField("1.3.6.1.4.1.5468.100.46.1.2.15.2.1.0", "i"),   # Integer32 (0..2147483647)
        'enable': EditorField("1.3.6.1.4.1.5468.100.46.1.2.15.2.2.0", "i"),   # TruthValue
        'isIndependent': EditorField("1.3.6.1.4.1.5468.100.46.1.2.15.2.3.0", "i"),   # TruthValue
        'ccOnly': EditorField("1.3.6.1.4.1.5468.100.46.1.2.15.2.4.0", "i"),   # TruthValue
        'txAuthEnabled': EditorField("1.3.6.1.4.1.5468.100.46.1.2.15.2.5.0", "i"),   # TruthValue
        'rxAuthEnabled': EditorField("1.3.6.1.4.1.5468.100.46.1.2.15.2.6.0", "i"),   # TruthValue
        'txAuthKeyId': EditorField("1.3.6.1.4.1.5468.100.46.1.2.15.2.7.0", "u"),   # VTSSUnsigned8
        'ccPeriod': EditorField("1.3.6.1.4.1.5468.100.46.1.2.15.2.8.0", "u"),   # Unsigned32
        'rxFlow': EditorField("1.3.6.1.4.1.5468.100.46.1.2.15.2.9.0", "u"),   # Unsigned32
    },
)

MEP_CONFIG_BFD_AUTH = RowEditorSpec(
    name="ml540mMepConfigBfdAuth",
    action_oid="1.3.6.1.4.1.5468.100.46.1.2.16.2.100.0",
    table_oid="1.3.6.1.4.1.5468.100.46.1.2.16.1",
    row_action_column_oid="1.3.6.1.4.1.5468.100.46.1.2.16.1.1.100",
    index_spec=IndexSpec(names=['id'], kinds=['integer']),
    fields={
        'id': EditorField("1.3.6.1.4.1.5468.100.46.1.2.16.2.1.0", "i"),   # Integer32 (0..2147483647)
        'keyType': EditorField("1.3.6.1.4.1.5468.100.46.1.2.16.2.2.0", "i"),   # VTSSMepBfdAuthenticationType
        'keyLen': EditorField("1.3.6.1.4.1.5468.100.46.1.2.16.2.3.0", "u"),   # VTSSUnsigned8
        'key': EditorField("1.3.6.1.4.1.5468.100.46.1.2.16.2.4.0", "s"),   # OCTET STRING (SIZE(20))
    },
)

MEP_CONFIG_CC = RowEditorSpec(
    name="ml540mMepConfigCc",
    action_oid="1.3.6.1.4.1.5468.100.46.1.2.3.2.100.0",
    table_oid="1.3.6.1.4.1.5468.100.46.1.2.3.1",
    row_action_column_oid="1.3.6.1.4.1.5468.100.46.1.2.3.1.1.100",
    index_spec=IndexSpec(names=['id'], kinds=['integer']),
    fields={
        'id': EditorField("1.3.6.1.4.1.5468.100.46.1.2.3.2.1.0", "i"),   # Integer32 (0..2147483647)
        'prio': EditorField("1.3.6.1.4.1.5468.100.46.1.2.3.2.3.0", "u"),   # Unsigned32
        'rate': EditorField("1.3.6.1.4.1.5468.100.46.1.2.3.2.4.0", "i"),   # VTSSMepTxRate
        'tlv': EditorField("1.3.6.1.4.1.5468.100.46.1.2.3.2.5.0", "i"),   # TruthValue
    },
)

MEP_CONFIG_CLIENT_FLOW = RowEditorSpec(
    name="ml540mMepConfigClientFlow",
    action_oid="1.3.6.1.4.1.5468.100.46.1.2.12.3.100.0",
    table_oid="1.3.6.1.4.1.5468.100.46.1.2.12.2",
    row_action_column_oid="1.3.6.1.4.1.5468.100.46.1.2.12.2.1.100",
    index_spec=IndexSpec(names=['id', 'flowId'], kinds=['integer', 'integer']),
    fields={
        'id': EditorField("1.3.6.1.4.1.5468.100.46.1.2.12.3.1.0", "i"),   # Integer32 (0..2147483647)
        'flowId': EditorField("1.3.6.1.4.1.5468.100.46.1.2.12.3.2.0", "i"),   # VTSSInterfaceIndex
        'aisPrio': EditorField("1.3.6.1.4.1.5468.100.46.1.2.12.3.3.0", "u"),   # VTSSUnsigned8
        'lckPrio': EditorField("1.3.6.1.4.1.5468.100.46.1.2.12.3.4.0", "u"),   # VTSSUnsigned8
        'level': EditorField("1.3.6.1.4.1.5468.100.46.1.2.12.3.5.0", "u"),   # VTSSUnsigned8
    },
)

MEP_CONFIG_INSTANCE = RowEditorSpec(
    name="ml540mMepConfigInstance",
    action_oid="1.3.6.1.4.1.5468.100.46.1.2.1.2.100.0",
    table_oid="1.3.6.1.4.1.5468.100.46.1.2.1.1",
    row_action_column_oid="1.3.6.1.4.1.5468.100.46.1.2.1.1.1.100",
    index_spec=IndexSpec(names=['id'], kinds=['integer']),
    fields={
        'id': EditorField("1.3.6.1.4.1.5468.100.46.1.2.1.2.1.0", "i"),   # Integer32 (0..2147483647)
        'mode': EditorField("1.3.6.1.4.1.5468.100.46.1.2.1.2.2.0", "i"),   # VTSSMepInstanceMode
        'direction': EditorField("1.3.6.1.4.1.5468.100.46.1.2.1.2.3.0", "i"),   # VTSSMepInstanceDirection
        'flow': EditorField("1.3.6.1.4.1.5468.100.46.1.2.1.2.4.0", "i"),   # VTSSInterfaceIndex
        'port': EditorField("1.3.6.1.4.1.5468.100.46.1.2.1.2.5.0", "i"),   # VTSSInterfaceIndex
        'level': EditorField("1.3.6.1.4.1.5468.100.46.1.2.1.2.6.0", "u"),   # Unsigned32
        'vid': EditorField("1.3.6.1.4.1.5468.100.46.1.2.1.2.7.0", "u"),   # VTSSUnsigned16
        'voe': EditorField("1.3.6.1.4.1.5468.100.46.1.2.1.2.8.0", "i"),   # TruthValue
        'mac': EditorField("1.3.6.1.4.1.5468.100.46.1.2.1.2.9.0", "x"),   # MacAddress
        'format': EditorField("1.3.6.1.4.1.5468.100.46.1.2.1.2.10.0", "i"),   # VTSSMepMegIdFormat
        'name': EditorField("1.3.6.1.4.1.5468.100.46.1.2.1.2.11.0", "s"),   # VTSSDisplayString (SIZE(0..16))
        'meg': EditorField("1.3.6.1.4.1.5468.100.46.1.2.1.2.12.0", "s"),   # VTSSDisplayString (SIZE(0..16))
        'mep': EditorField("1.3.6.1.4.1.5468.100.46.1.2.1.2.13.0", "u"),   # Unsigned32
        'evcPag': EditorField("1.3.6.1.4.1.5468.100.46.1.2.1.2.14.0", "u"),   # Unsigned32
        'evcQos': EditorField("1.3.6.1.4.1.5468.100.46.1.2.1.2.15.0", "u"),   # Unsigned32
    },
)

MEP_CONFIG_INSTANCE_PEER = RowEditorSpec(
    name="ml540mMepConfigInstancePeer",
    action_oid="1.3.6.1.4.1.5468.100.46.1.2.1.4.100.0",
    table_oid="1.3.6.1.4.1.5468.100.46.1.2.1.3",
    row_action_column_oid="1.3.6.1.4.1.5468.100.46.1.2.1.3.1.100",
    index_spec=IndexSpec(names=['id', 'peerId'], kinds=['integer', 'integer']),
    fields={
        'id': EditorField("1.3.6.1.4.1.5468.100.46.1.2.1.4.1.0", "i"),   # Integer32 (0..2147483647)
        'peerId': EditorField("1.3.6.1.4.1.5468.100.46.1.2.1.4.2.0", "i"),   # Integer32 (0..2147483647)
        'mac': EditorField("1.3.6.1.4.1.5468.100.46.1.2.1.4.3.0", "x"),   # MacAddress
    },
)

MEP_CONFIG_LB = RowEditorSpec(
    name="ml540mMepConfigLb",
    action_oid="1.3.6.1.4.1.5468.100.46.1.2.6.2.101.0",
    table_oid="1.3.6.1.4.1.5468.100.46.1.2.6.1",
    row_action_column_oid="1.3.6.1.4.1.5468.100.46.1.2.6.1.1.101",
    index_spec=IndexSpec(names=['id'], kinds=['integer']),
    fields={
        'id': EditorField("1.3.6.1.4.1.5468.100.46.1.2.6.2.1.0", "i"),   # Integer32 (0..2147483647)
        'dei': EditorField("1.3.6.1.4.1.5468.100.46.1.2.6.2.2.0", "i"),   # TruthValue
        'prio': EditorField("1.3.6.1.4.1.5468.100.46.1.2.6.2.3.0", "u"),   # Unsigned32
        'cast': EditorField("1.3.6.1.4.1.5468.100.46.1.2.6.2.4.0", "i"),   # VTSSMepCast
        'mep': EditorField("1.3.6.1.4.1.5468.100.46.1.2.6.2.5.0", "u"),   # Unsigned32
        'mac': EditorField("1.3.6.1.4.1.5468.100.46.1.2.6.2.6.0", "x"),   # MacAddress
        'toSend': EditorField("1.3.6.1.4.1.5468.100.46.1.2.6.2.7.0", "u"),   # Unsigned32
        'size': EditorField("1.3.6.1.4.1.5468.100.46.1.2.6.2.8.0", "u"),   # Unsigned32
        'interval': EditorField("1.3.6.1.4.1.5468.100.46.1.2.6.2.9.0", "u"),   # Unsigned32
        'timeToLive': EditorField("1.3.6.1.4.1.5468.100.46.1.2.6.2.10.0", "u"),   # VTSSUnsigned8
    },
)

MEP_CONFIG_LCK = RowEditorSpec(
    name="ml540mMepConfigLck",
    action_oid="1.3.6.1.4.1.5468.100.46.1.2.11.2.101.0",
    table_oid="1.3.6.1.4.1.5468.100.46.1.2.11.1",
    row_action_column_oid="1.3.6.1.4.1.5468.100.46.1.2.11.1.1.101",
    index_spec=IndexSpec(names=['id'], kinds=['integer']),
    fields={
        'id': EditorField("1.3.6.1.4.1.5468.100.46.1.2.11.2.1.0", "i"),   # Integer32 (0..2147483647)
        'rate': EditorField("1.3.6.1.4.1.5468.100.46.1.2.11.2.2.0", "i"),   # VTSSMepTxRate
    },
)

MEP_CONFIG_LT = RowEditorSpec(
    name="ml540mMepConfigLt",
    action_oid="1.3.6.1.4.1.5468.100.46.1.2.8.2.101.0",
    table_oid="1.3.6.1.4.1.5468.100.46.1.2.8.1",
    row_action_column_oid="1.3.6.1.4.1.5468.100.46.1.2.8.1.1.101",
    index_spec=IndexSpec(names=['id'], kinds=['integer']),
    fields={
        'id': EditorField("1.3.6.1.4.1.5468.100.46.1.2.8.2.1.0", "i"),   # Integer32 (0..2147483647)
        'prio': EditorField("1.3.6.1.4.1.5468.100.46.1.2.8.2.3.0", "u"),   # Unsigned32
        'mep': EditorField("1.3.6.1.4.1.5468.100.46.1.2.8.2.4.0", "u"),   # Unsigned32
        'mac': EditorField("1.3.6.1.4.1.5468.100.46.1.2.8.2.5.0", "x"),   # MacAddress
        'timeToLive': EditorField("1.3.6.1.4.1.5468.100.46.1.2.8.2.6.0", "u"),   # Unsigned32
    },
)

MEP_CONFIG_RT = RowEditorSpec(
    name="ml540mMepConfigRt",
    action_oid="1.3.6.1.4.1.5468.100.46.1.2.17.2.100.0",
    table_oid="1.3.6.1.4.1.5468.100.46.1.2.17.1",
    row_action_column_oid="1.3.6.1.4.1.5468.100.46.1.2.17.1.1.100",
    index_spec=IndexSpec(names=['id'], kinds=['integer']),
    fields={
        'id': EditorField("1.3.6.1.4.1.5468.100.46.1.2.17.2.1.0", "i"),   # Integer32 (0..2147483647)
        'trafficClass': EditorField("1.3.6.1.4.1.5468.100.46.1.2.17.2.2.0", "u"),   # VTSSUnsigned8
        'srcIdTlv': EditorField("1.3.6.1.4.1.5468.100.46.1.2.17.2.3.0", "i"),   # TruthValue
        'dstIdTlv': EditorField("1.3.6.1.4.1.5468.100.46.1.2.17.2.4.0", "i"),   # TruthValue
        'padTlvType': EditorField("1.3.6.1.4.1.5468.100.46.1.2.17.2.5.0", "i"),   # VTSSMepRtPadTlvType
        'padTlvLen': EditorField("1.3.6.1.4.1.5468.100.46.1.2.17.2.6.0", "u"),   # VTSSUnsigned16
        'flags': EditorField("1.3.6.1.4.1.5468.100.46.1.2.17.2.7.0", "u"),   # VTSSUnsigned8
        'maxTimeToLive': EditorField("1.3.6.1.4.1.5468.100.46.1.2.17.2.8.0", "u"),   # VTSSUnsigned8
    },
)

MEP_CONFIG_TST = RowEditorSpec(
    name="ml540mMepConfigTst",
    action_oid="1.3.6.1.4.1.5468.100.46.1.2.7.2.101.0",
    table_oid="1.3.6.1.4.1.5468.100.46.1.2.7.1",
    row_action_column_oid="1.3.6.1.4.1.5468.100.46.1.2.7.1.1.101",
    index_spec=IndexSpec(names=['id'], kinds=['integer']),
    fields={
        'id': EditorField("1.3.6.1.4.1.5468.100.46.1.2.7.2.1.0", "i"),   # Integer32 (0..2147483647)
        'txEnable': EditorField("1.3.6.1.4.1.5468.100.46.1.2.7.2.2.0", "i"),   # TruthValue
        'rxEnable': EditorField("1.3.6.1.4.1.5468.100.46.1.2.7.2.3.0", "i"),   # TruthValue
        'dei': EditorField("1.3.6.1.4.1.5468.100.46.1.2.7.2.4.0", "i"),   # TruthValue
        'prio': EditorField("1.3.6.1.4.1.5468.100.46.1.2.7.2.5.0", "u"),   # Unsigned32
        'mep': EditorField("1.3.6.1.4.1.5468.100.46.1.2.7.2.6.0", "u"),   # Unsigned32
        'rate': EditorField("1.3.6.1.4.1.5468.100.46.1.2.7.2.7.0", "u"),   # Unsigned32
        'size': EditorField("1.3.6.1.4.1.5468.100.46.1.2.7.2.8.0", "u"),   # Unsigned32
        'pattern': EditorField("1.3.6.1.4.1.5468.100.46.1.2.7.2.9.0", "i"),   # VTSSMepTstPattern
        'sequence': EditorField("1.3.6.1.4.1.5468.100.46.1.2.7.2.10.0", "i"),   # TruthValue
    },
)

MPLS_CONFIG_COS_MAP = RowEditorSpec(
    name="ml540mMplsConfigCosMap",
    action_oid="1.3.6.1.4.1.5468.100.127.1.2.6.2.100.0",
    table_oid="1.3.6.1.4.1.5468.100.127.1.2.6.1",
    row_action_column_oid="1.3.6.1.4.1.5468.100.127.1.2.6.1.1.100",
    index_spec=IndexSpec(names=['groupIndex'], kinds=['integer']),
    fields={
        'groupIndex': EditorField("1.3.6.1.4.1.5468.100.127.1.2.6.2.1.0", "i"),   # Integer32 (0..2147483647)
        'inTcToCos0': EditorField("1.3.6.1.4.1.5468.100.127.1.2.6.2.10.0", "u"),   # VTSSUnsigned8 (0..7)
        'inTcToCos1': EditorField("1.3.6.1.4.1.5468.100.127.1.2.6.2.11.0", "u"),   # VTSSUnsigned8 (0..7)
        'inTcToCos2': EditorField("1.3.6.1.4.1.5468.100.127.1.2.6.2.12.0", "u"),   # VTSSUnsigned8 (0..7)
        'inTcToCos3': EditorField("1.3.6.1.4.1.5468.100.127.1.2.6.2.13.0", "u"),   # VTSSUnsigned8 (0..7)
        'inTcToCos4': EditorField("1.3.6.1.4.1.5468.100.127.1.2.6.2.14.0", "u"),   # VTSSUnsigned8 (0..7)
        'inTcToCos5': EditorField("1.3.6.1.4.1.5468.100.127.1.2.6.2.15.0", "u"),   # VTSSUnsigned8 (0..7)
        'inTcToCos6': EditorField("1.3.6.1.4.1.5468.100.127.1.2.6.2.16.0", "u"),   # VTSSUnsigned8 (0..7)
        'inTcToCos7': EditorField("1.3.6.1.4.1.5468.100.127.1.2.6.2.17.0", "u"),   # VTSSUnsigned8 (0..7)
        'inTcToDp0': EditorField("1.3.6.1.4.1.5468.100.127.1.2.6.2.20.0", "u"),   # VTSSUnsigned8 (0..7)
        'inTcToDp1': EditorField("1.3.6.1.4.1.5468.100.127.1.2.6.2.21.0", "u"),   # VTSSUnsigned8 (0..7)
        'inTcToDp2': EditorField("1.3.6.1.4.1.5468.100.127.1.2.6.2.22.0", "u"),   # VTSSUnsigned8 (0..7)
        'inTcToDp3': EditorField("1.3.6.1.4.1.5468.100.127.1.2.6.2.23.0", "u"),   # VTSSUnsigned8 (0..7)
        'inTcToDp4': EditorField("1.3.6.1.4.1.5468.100.127.1.2.6.2.24.0", "u"),   # VTSSUnsigned8 (0..7)
        'inTcToDp5': EditorField("1.3.6.1.4.1.5468.100.127.1.2.6.2.25.0", "u"),   # VTSSUnsigned8 (0..7)
        'inTcToDp6': EditorField("1.3.6.1.4.1.5468.100.127.1.2.6.2.26.0", "u"),   # VTSSUnsigned8 (0..7)
        'inTcToDp7': EditorField("1.3.6.1.4.1.5468.100.127.1.2.6.2.27.0", "u"),   # VTSSUnsigned8 (0..7)
        'outCosDpToTc00': EditorField("1.3.6.1.4.1.5468.100.127.1.2.6.2.30.0", "u"),   # VTSSUnsigned8 (0..7)
        'outCosDpToTc10': EditorField("1.3.6.1.4.1.5468.100.127.1.2.6.2.31.0", "u"),   # VTSSUnsigned8 (0..7)
        'outCosDpToTc20': EditorField("1.3.6.1.4.1.5468.100.127.1.2.6.2.32.0", "u"),   # VTSSUnsigned8 (0..7)
        'outCosDpToTc30': EditorField("1.3.6.1.4.1.5468.100.127.1.2.6.2.33.0", "u"),   # VTSSUnsigned8 (0..7)
        'outCosDpToTc40': EditorField("1.3.6.1.4.1.5468.100.127.1.2.6.2.34.0", "u"),   # VTSSUnsigned8 (0..7)
        'outCosDpToTc50': EditorField("1.3.6.1.4.1.5468.100.127.1.2.6.2.35.0", "u"),   # VTSSUnsigned8 (0..7)
        'outCosDpToTc60': EditorField("1.3.6.1.4.1.5468.100.127.1.2.6.2.36.0", "u"),   # VTSSUnsigned8 (0..7)
        'outCosDpToTc70': EditorField("1.3.6.1.4.1.5468.100.127.1.2.6.2.37.0", "u"),   # VTSSUnsigned8 (0..7)
        'outCosDpToTc01': EditorField("1.3.6.1.4.1.5468.100.127.1.2.6.2.40.0", "u"),   # VTSSUnsigned8 (0..7)
        'outCosDpToTc11': EditorField("1.3.6.1.4.1.5468.100.127.1.2.6.2.41.0", "u"),   # VTSSUnsigned8 (0..7)
        'outCosDpToTc21': EditorField("1.3.6.1.4.1.5468.100.127.1.2.6.2.42.0", "u"),   # VTSSUnsigned8 (0..7)
        'outCosDpToTc31': EditorField("1.3.6.1.4.1.5468.100.127.1.2.6.2.43.0", "u"),   # VTSSUnsigned8 (0..7)
        'outCosDpToTc41': EditorField("1.3.6.1.4.1.5468.100.127.1.2.6.2.44.0", "u"),   # VTSSUnsigned8 (0..7)
        'outCosDpToTc51': EditorField("1.3.6.1.4.1.5468.100.127.1.2.6.2.45.0", "u"),   # VTSSUnsigned8 (0..7)
        'outCosDpToTc61': EditorField("1.3.6.1.4.1.5468.100.127.1.2.6.2.46.0", "u"),   # VTSSUnsigned8 (0..7)
        'outCosDpToTc71': EditorField("1.3.6.1.4.1.5468.100.127.1.2.6.2.47.0", "u"),   # VTSSUnsigned8 (0..7)
    },
)

MPLS_CONFIG_LINK = RowEditorSpec(
    name="ml540mMplsConfigLink",
    action_oid="1.3.6.1.4.1.5468.100.127.1.2.2.2.100.0",
    table_oid="1.3.6.1.4.1.5468.100.127.1.2.2.1",
    row_action_column_oid="1.3.6.1.4.1.5468.100.127.1.2.2.1.1.100",
    index_spec=IndexSpec(names=['groupIfIndex'], kinds=['integer']),
    fields={
        'groupIfIndex': EditorField("1.3.6.1.4.1.5468.100.127.1.2.2.2.1.0", "i"),   # VTSSInterfaceIndex
        'port': EditorField("1.3.6.1.4.1.5468.100.127.1.2.2.2.2.0", "i"),   # VTSSInterfaceIndex
        'mACAddressNextHop': EditorField("1.3.6.1.4.1.5468.100.127.1.2.2.2.3.0", "x"),   # MacAddress
        'mACAddress': EditorField("1.3.6.1.4.1.5468.100.127.1.2.2.2.4.0", "x"),   # MacAddress
        'vLANTagType': EditorField("1.3.6.1.4.1.5468.100.127.1.2.2.2.5.0", "i"),   # VTSSMplsTagType
        'vLANId': EditorField("1.3.6.1.4.1.5468.100.127.1.2.2.2.6.0", "u"),   # VTSSUnsigned16
        'vLANpcp': EditorField("1.3.6.1.4.1.5468.100.127.1.2.2.2.7.0", "u"),   # Unsigned32
        'vLANdei': EditorField("1.3.6.1.4.1.5468.100.127.1.2.2.2.8.0", "u"),   # VTSSUnsigned8
        'srcNodeId': EditorField("1.3.6.1.4.1.5468.100.127.1.2.2.2.9.0", "a"),   # IpAddress
        'srcGlobalId': EditorField("1.3.6.1.4.1.5468.100.127.1.2.2.2.10.0", "u"),   # Unsigned32
        'dstNodeId': EditorField("1.3.6.1.4.1.5468.100.127.1.2.2.2.11.0", "a"),   # IpAddress
        'dstGlobalId': EditorField("1.3.6.1.4.1.5468.100.127.1.2.2.2.12.0", "u"),   # Unsigned32
        'dstIfNum': EditorField("1.3.6.1.4.1.5468.100.127.1.2.2.2.13.0", "u"),   # Unsigned32
        'srcNodeIdValid': EditorField("1.3.6.1.4.1.5468.100.127.1.2.2.2.14.0", "i"),   # TruthValue
        'srcGlobalIdValid': EditorField("1.3.6.1.4.1.5468.100.127.1.2.2.2.15.0", "i"),   # TruthValue
        'dstGlobalIdValid': EditorField("1.3.6.1.4.1.5468.100.127.1.2.2.2.16.0", "i"),   # TruthValue
    },
)

MPLS_CONFIG_LSP = RowEditorSpec(
    name="ml540mMplsConfigLsp",
    action_oid="1.3.6.1.4.1.5468.100.127.1.2.4.2.100.0",
    table_oid="1.3.6.1.4.1.5468.100.127.1.2.4.1",
    row_action_column_oid="1.3.6.1.4.1.5468.100.127.1.2.4.1.1.100",
    index_spec=IndexSpec(names=['groupIndex'], kinds=['integer']),
    fields={
        'groupIndex': EditorField("1.3.6.1.4.1.5468.100.127.1.2.4.2.1.0", "i"),   # Integer32 (0..2147483647)
        'xcName': EditorField("1.3.6.1.4.1.5468.100.127.1.2.4.2.2.0", "s"),   # VTSSDisplayString (SIZE(0..31))
        'srcNodeId': EditorField("1.3.6.1.4.1.5468.100.127.1.2.4.2.3.0", "a"),   # IpAddress
        'srcNodeIdIsDefined': EditorField("1.3.6.1.4.1.5468.100.127.1.2.4.2.4.0", "i"),   # TruthValue
        'srcGlobalId': EditorField("1.3.6.1.4.1.5468.100.127.1.2.4.2.5.0", "u"),   # Unsigned32
        'srcGlobalIdIsDefined': EditorField("1.3.6.1.4.1.5468.100.127.1.2.4.2.6.0", "i"),   # TruthValue
        'srcTunnelTpNum': EditorField("1.3.6.1.4.1.5468.100.127.1.2.4.2.7.0", "u"),   # VTSSUnsigned16
        'dstNodeId': EditorField("1.3.6.1.4.1.5468.100.127.1.2.4.2.8.0", "a"),   # IpAddress
        'dstGlobalId': EditorField("1.3.6.1.4.1.5468.100.127.1.2.4.2.9.0", "u"),   # Unsigned32
        'dstGlobalIdIsDefined': EditorField("1.3.6.1.4.1.5468.100.127.1.2.4.2.10.0", "i"),   # TruthValue
        'dstTunnelTpNum': EditorField("1.3.6.1.4.1.5468.100.127.1.2.4.2.11.0", "u"),   # VTSSUnsigned16
        'srcLspNumber': EditorField("1.3.6.1.4.1.5468.100.127.1.2.4.2.12.0", "u"),   # VTSSUnsigned16
        'dstLspNumber': EditorField("1.3.6.1.4.1.5468.100.127.1.2.4.2.13.0", "u"),   # VTSSUnsigned16
        'forwardIngressLabel': EditorField("1.3.6.1.4.1.5468.100.127.1.2.4.2.14.0", "u"),   # Unsigned32 (16..1048575)
        'forwardEgressLabel': EditorField("1.3.6.1.4.1.5468.100.127.1.2.4.2.15.0", "u"),   # Unsigned32 (16..1048575)
        'forwardAttachInterface': EditorField("1.3.6.1.4.1.5468.100.127.1.2.4.2.16.0", "i"),   # VTSSInterfaceIndex
        'forwardInCosMapId': EditorField("1.3.6.1.4.1.5468.100.127.1.2.4.2.17.0", "u"),   # VTSSUnsigned8
        'forwardOutCosMapId': EditorField("1.3.6.1.4.1.5468.100.127.1.2.4.2.18.0", "u"),   # VTSSUnsigned8
        'forwardIsLLsp': EditorField("1.3.6.1.4.1.5468.100.127.1.2.4.2.19.0", "i"),   # TruthValue
        'forwardHQoSId': EditorField("1.3.6.1.4.1.5468.100.127.1.2.4.2.20.0", "u"),   # VTSSUnsigned16 (0..256)
        'forwardLLspCos': EditorField("1.3.6.1.4.1.5468.100.127.1.2.4.2.21.0", "u"),   # VTSSUnsigned8 (0..7)
        'reverseIngressLabel': EditorField("1.3.6.1.4.1.5468.100.127.1.2.4.2.22.0", "u"),   # Unsigned32 (16..1048575)
        'reverseEgressLabel': EditorField("1.3.6.1.4.1.5468.100.127.1.2.4.2.23.0", "u"),   # Unsigned32 (16..1048575)
        'reverseAttachInterface': EditorField("1.3.6.1.4.1.5468.100.127.1.2.4.2.24.0", "i"),   # VTSSInterfaceIndex
        'reverseInCosMapId': EditorField("1.3.6.1.4.1.5468.100.127.1.2.4.2.25.0", "u"),   # VTSSUnsigned8
        'reverseOutCosMapId': EditorField("1.3.6.1.4.1.5468.100.127.1.2.4.2.26.0", "u"),   # VTSSUnsigned8
        'reverseIsLLsp': EditorField("1.3.6.1.4.1.5468.100.127.1.2.4.2.27.0", "i"),   # TruthValue
        'reverseLLspCos': EditorField("1.3.6.1.4.1.5468.100.127.1.2.4.2.28.0", "u"),   # VTSSUnsigned8 (0..7)
        'reverseHQoSId': EditorField("1.3.6.1.4.1.5468.100.127.1.2.4.2.29.0", "u"),   # VTSSUnsigned16 (0..256)
    },
)

MPLS_CONFIG_PW = RowEditorSpec(
    name="ml540mMplsConfigPw",
    action_oid="1.3.6.1.4.1.5468.100.127.1.2.5.2.100.0",
    table_oid="1.3.6.1.4.1.5468.100.127.1.2.5.1",
    row_action_column_oid="1.3.6.1.4.1.5468.100.127.1.2.5.1.1.100",
    index_spec=IndexSpec(names=['groupIfIndex'], kinds=['integer']),
    fields={
        'groupIfIndex': EditorField("1.3.6.1.4.1.5468.100.127.1.2.5.2.1.0", "i"),   # VTSSInterfaceIndex
        'inLabel': EditorField("1.3.6.1.4.1.5468.100.127.1.2.5.2.2.0", "u"),   # Unsigned32 (16..1048575)
        'outLabel': EditorField("1.3.6.1.4.1.5468.100.127.1.2.5.2.3.0", "u"),   # Unsigned32 (16..1048575)
        'controlWord': EditorField("1.3.6.1.4.1.5468.100.127.1.2.5.2.4.0", "u"),   # Unsigned32 (0..268435455)
        'useControlWord': EditorField("1.3.6.1.4.1.5468.100.127.1.2.5.2.5.0", "i"),   # TruthValue
        'tunnelMode': EditorField("1.3.6.1.4.1.5468.100.127.1.2.5.2.6.0", "i"),   # VTSSMplsTunnelMode
        'trafficClass': EditorField("1.3.6.1.4.1.5468.100.127.1.2.5.2.7.0", "u"),   # VTSSUnsigned8 (0..7)
        'ttl': EditorField("1.3.6.1.4.1.5468.100.127.1.2.5.2.8.0", "u"),   # VTSSUnsigned8 (0..255)
        'inCosMapId': EditorField("1.3.6.1.4.1.5468.100.127.1.2.5.2.9.0", "u"),   # VTSSUnsigned8
        'outCosMapId': EditorField("1.3.6.1.4.1.5468.100.127.1.2.5.2.10.0", "u"),   # VTSSUnsigned8
        'isLLsp': EditorField("1.3.6.1.4.1.5468.100.127.1.2.5.2.11.0", "i"),   # TruthValue
        'lLspCos': EditorField("1.3.6.1.4.1.5468.100.127.1.2.5.2.12.0", "u"),   # VTSSUnsigned8 (0..7)
        'attachInterface': EditorField("1.3.6.1.4.1.5468.100.127.1.2.5.2.13.0", "i"),   # VTSSInterfaceIndex
        'stitchPwInterface': EditorField("1.3.6.1.4.1.5468.100.127.1.2.5.2.14.0", "i"),   # VTSSInterfaceIndex
        'vccvType': EditorField("1.3.6.1.4.1.5468.100.127.1.2.5.2.15.0", "i"),   # VTSSMplsVccvType
        'hQoSId': EditorField("1.3.6.1.4.1.5468.100.127.1.2.5.2.16.0", "u"),   # VTSSUnsigned16 (0..256)
        'srcNodeId': EditorField("1.3.6.1.4.1.5468.100.127.1.2.5.2.17.0", "a"),   # IpAddress
        'srcNodeIdIsDefined': EditorField("1.3.6.1.4.1.5468.100.127.1.2.5.2.18.0", "i"),   # TruthValue
        'srcGlobalId': EditorField("1.3.6.1.4.1.5468.100.127.1.2.5.2.19.0", "u"),   # Unsigned32
        'srcGlobalIdIsDefined': EditorField("1.3.6.1.4.1.5468.100.127.1.2.5.2.20.0", "i"),   # TruthValue
        'dstNodeId': EditorField("1.3.6.1.4.1.5468.100.127.1.2.5.2.21.0", "a"),   # IpAddress
        'dstGlobalId': EditorField("1.3.6.1.4.1.5468.100.127.1.2.5.2.22.0", "u"),   # Unsigned32
        'dstGlobalIdIsDefined': EditorField("1.3.6.1.4.1.5468.100.127.1.2.5.2.23.0", "i"),   # TruthValue
        'srcAcId': EditorField("1.3.6.1.4.1.5468.100.127.1.2.5.2.24.0", "u"),   # Unsigned32
        'dstAcId': EditorField("1.3.6.1.4.1.5468.100.127.1.2.5.2.25.0", "u"),   # Unsigned32
        'srcAgiValue': EditorField("1.3.6.1.4.1.5468.100.127.1.2.5.2.26.0", "s"),   # OCTET STRING (SIZE(8))
        'dstAgiValue': EditorField("1.3.6.1.4.1.5468.100.127.1.2.5.2.27.0", "s"),   # OCTET STRING (SIZE(8))
        'srcAgiType': EditorField("1.3.6.1.4.1.5468.100.127.1.2.5.2.28.0", "u"),   # VTSSUnsigned8
        'srcAgiLength': EditorField("1.3.6.1.4.1.5468.100.127.1.2.5.2.29.0", "u"),   # VTSSUnsigned8 (0..7)
        'dstAgiType': EditorField("1.3.6.1.4.1.5468.100.127.1.2.5.2.30.0", "u"),   # VTSSUnsigned8
        'dstAgiLength': EditorField("1.3.6.1.4.1.5468.100.127.1.2.5.2.31.0", "u"),   # VTSSUnsigned8 (0..7)
    },
)

MPLS_CONFIG_TUNNEL = RowEditorSpec(
    name="ml540mMplsConfigTunnel",
    action_oid="1.3.6.1.4.1.5468.100.127.1.2.3.2.100.0",
    table_oid="1.3.6.1.4.1.5468.100.127.1.2.3.1",
    row_action_column_oid="1.3.6.1.4.1.5468.100.127.1.2.3.1.1.100",
    index_spec=IndexSpec(names=['groupIfIndex'], kinds=['integer']),
    fields={
        'groupIfIndex': EditorField("1.3.6.1.4.1.5468.100.127.1.2.3.2.1.0", "i"),   # VTSSInterfaceIndex
        'tunnelName': EditorField("1.3.6.1.4.1.5468.100.127.1.2.3.2.2.0", "s"),   # VTSSDisplayString (SIZE(0..31))
        'tunnelMode': EditorField("1.3.6.1.4.1.5468.100.127.1.2.3.2.3.0", "i"),   # VTSSMplsTunnelMode
        'srcNodeId': EditorField("1.3.6.1.4.1.5468.100.127.1.2.3.2.4.0", "a"),   # IpAddress
        'srcGlobalId': EditorField("1.3.6.1.4.1.5468.100.127.1.2.3.2.5.0", "u"),   # Unsigned32
        'dstNodeId': EditorField("1.3.6.1.4.1.5468.100.127.1.2.3.2.6.0", "a"),   # IpAddress
        'dstGlobalId': EditorField("1.3.6.1.4.1.5468.100.127.1.2.3.2.7.0", "u"),   # Unsigned32
        'dstTunnelTpNum': EditorField("1.3.6.1.4.1.5468.100.127.1.2.3.2.8.0", "u"),   # Unsigned32
        'srcTunnelTpNum': EditorField("1.3.6.1.4.1.5468.100.127.1.2.3.2.9.0", "u"),   # VTSSUnsigned16
        'srcLspNum': EditorField("1.3.6.1.4.1.5468.100.127.1.2.3.2.10.0", "u"),   # VTSSUnsigned16
        'dstLspNum': EditorField("1.3.6.1.4.1.5468.100.127.1.2.3.2.11.0", "u"),   # VTSSUnsigned16
        'isSpme': EditorField("1.3.6.1.4.1.5468.100.127.1.2.3.2.12.0", "i"),   # TruthValue
        'srcNodeIsValid': EditorField("1.3.6.1.4.1.5468.100.127.1.2.3.2.13.0", "i"),   # TruthValue
        'srcGlobalIdValid': EditorField("1.3.6.1.4.1.5468.100.127.1.2.3.2.14.0", "i"),   # TruthValue
        'dstGlobalIdValid': EditorField("1.3.6.1.4.1.5468.100.127.1.2.3.2.15.0", "i"),   # TruthValue
        'ingressLabel': EditorField("1.3.6.1.4.1.5468.100.127.1.2.3.2.16.0", "u"),   # Unsigned32 (16..1048575)
        'egressLabel': EditorField("1.3.6.1.4.1.5468.100.127.1.2.3.2.17.0", "u"),   # Unsigned32 (16..1048575)
        'attachInterface': EditorField("1.3.6.1.4.1.5468.100.127.1.2.3.2.18.0", "i"),   # VTSSInterfaceIndex
        'trafficClass': EditorField("1.3.6.1.4.1.5468.100.127.1.2.3.2.19.0", "u"),   # VTSSUnsigned8 (0..7)
        'ttl': EditorField("1.3.6.1.4.1.5468.100.127.1.2.3.2.20.0", "u"),   # VTSSUnsigned8 (0..255)
        'inCosMapId': EditorField("1.3.6.1.4.1.5468.100.127.1.2.3.2.21.0", "u"),   # VTSSUnsigned8
        'outCosMapId': EditorField("1.3.6.1.4.1.5468.100.127.1.2.3.2.22.0", "u"),   # VTSSUnsigned8
        'isLLsp': EditorField("1.3.6.1.4.1.5468.100.127.1.2.3.2.23.0", "i"),   # TruthValue
        'lLspCos': EditorField("1.3.6.1.4.1.5468.100.127.1.2.3.2.24.0", "u"),   # VTSSUnsigned8 (0..7)
    },
)

PTP_CONFIG_CLOCKS_DEFAULT_DS_TABLE = RowEditorSpec(
    name="ml540mPtpConfigClocksDefaultDsTable",
    action_oid="1.3.6.1.4.1.5468.100.65.1.2.2.2.100.0",
    table_oid="1.3.6.1.4.1.5468.100.65.1.2.2.1",
    row_action_column_oid="1.3.6.1.4.1.5468.100.65.1.2.2.1.1.100",
    index_spec=IndexSpec(names=['clockId'], kinds=['integer']),
    fields={
        'clockId': EditorField("1.3.6.1.4.1.5468.100.65.1.2.2.2.1.0", "i"),   # Integer32 (0..32767)
        'deviceType': EditorField("1.3.6.1.4.1.5468.100.65.1.2.2.2.2.0", "u"),   # VTSSUnsigned8
        'twoStepFlag': EditorField("1.3.6.1.4.1.5468.100.65.1.2.2.2.3.0", "i"),   # TruthValue
        'priority1': EditorField("1.3.6.1.4.1.5468.100.65.1.2.2.2.4.0", "u"),   # VTSSUnsigned8
        'priority2': EditorField("1.3.6.1.4.1.5468.100.65.1.2.2.2.5.0", "u"),   # VTSSUnsigned8
        'oneWay': EditorField("1.3.6.1.4.1.5468.100.65.1.2.2.2.6.0", "i"),   # TruthValue
        'domainNumber': EditorField("1.3.6.1.4.1.5468.100.65.1.2.2.2.7.0", "u"),   # VTSSUnsigned8
        'protocol': EditorField("1.3.6.1.4.1.5468.100.65.1.2.2.2.8.0", "u"),   # VTSSUnsigned8
        'vlanTagEnable': EditorField("1.3.6.1.4.1.5468.100.65.1.2.2.2.9.0", "i"),   # TruthValue
        'vid': EditorField("1.3.6.1.4.1.5468.100.65.1.2.2.2.10.0", "u"),   # VTSSUnsigned16
        'pcp': EditorField("1.3.6.1.4.1.5468.100.65.1.2.2.2.11.0", "u"),   # VTSSUnsigned8
        'mep': EditorField("1.3.6.1.4.1.5468.100.65.1.2.2.2.12.0", "i"),   # Integer32
    },
)

PVLAN_CONFIG_INTERFACE_VLAN_MEMBERSHIP_TABLE = RowEditorSpec(
    name="ml540mPvlanConfigInterfaceVlanMembershipTable",
    action_oid="1.3.6.1.4.1.5468.100.23.1.2.1.2.100.0",
    table_oid="1.3.6.1.4.1.5468.100.23.1.2.1.1",
    row_action_column_oid="1.3.6.1.4.1.5468.100.23.1.2.1.1.1.100",
    index_spec=IndexSpec(names=['pvlanIndex'], kinds=['integer']),
    fields={
        'pvlanIndex': EditorField("1.3.6.1.4.1.5468.100.23.1.2.1.2.1.0", "u"),   # Unsigned32
        'portList': EditorField("1.3.6.1.4.1.5468.100.23.1.2.1.2.2.0", "s"),   # VTSSPortList
    },
)

QOS_CONFIG_QCE_TABLE = RowEditorSpec(
    name="ml540mQosConfigQceTable",
    action_oid="1.3.6.1.4.1.5468.100.14.1.2.3.2.10000.0",
    table_oid="1.3.6.1.4.1.5468.100.14.1.2.3.1",
    row_action_column_oid="1.3.6.1.4.1.5468.100.14.1.2.3.1.1.10000",
    index_spec=IndexSpec(names=['qceId'], kinds=['integer']),
    fields={
        'qceId': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.1.0", "i"),   # Integer32 (0..2147483647)
        'nextQceId': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.2.0", "u"),   # Unsigned32
        'switchId': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.3.0", "u"),   # Unsigned32
        'portList': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.4.0", "s"),   # VTSSPortList
        'destMacType': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.5.0", "i"),   # VTSSDestMacType
        'destMac': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.6.0", "x"),   # MacAddress
        'destMacMask': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.7.0", "x"),   # MacAddress
        'srcMac': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.8.0", "x"),   # MacAddress
        'srcMacMask': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.9.0", "x"),   # MacAddress
        'vlanTagType': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.10.0", "i"),   # VTSSVlanTagType
        'vlanIdOp': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.11.0", "i"),   # VTSSASRType
        'vlanId': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.12.0", "u"),   # VTSSUnsigned16
        'vlanIdRange': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.13.0", "u"),   # VTSSUnsigned16
        'pcp': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.14.0", "i"),   # VTSSVlanTagPriority
        'dei': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.15.0", "i"),   # VTSSBitType
        'innerVlanTagType': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.16.0", "i"),   # VTSSVlanTagType
        'innerVlanIdOp': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.17.0", "i"),   # VTSSASRType
        'innerVlanId': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.18.0", "u"),   # VTSSUnsigned16
        'innerVlanIdRange': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.19.0", "u"),   # VTSSUnsigned16
        'innerPcp': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.20.0", "i"),   # VTSSVlanTagPriority
        'innerDei': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.21.0", "i"),   # VTSSBitType
        'frameType': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.100.0", "i"),   # VTSSQosQceFrameType
        'etype': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.101.0", "u"),   # VTSSEtherType
        'llcDsap': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.200.0", "u"),   # VTSSUnsigned8
        'llcDsapMask': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.201.0", "u"),   # VTSSUnsigned8
        'llcSsap': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.202.0", "u"),   # VTSSUnsigned8
        'llcSsapMask': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.203.0", "u"),   # VTSSUnsigned8
        'llcControl': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.204.0", "u"),   # VTSSUnsigned8
        'llcControlMask': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.205.0", "u"),   # VTSSUnsigned8
        'snapPid': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.302.0", "u"),   # VTSSUnsigned16
        'snapPidMask': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.303.0", "u"),   # VTSSUnsigned16
        'ipv4Fragment': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.400.0", "i"),   # VTSSBitType
        'ipv4DscpOp': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.401.0", "i"),   # VTSSASRType
        'ipv4Dscp': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.402.0", "u"),   # VTSSUnsigned16
        'ipv4DscpRange': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.403.0", "u"),   # VTSSUnsigned16
        'ipv4Protocol': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.404.0", "u"),   # VTSSUnsigned8
        'ipv4ProtocolMask': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.405.0", "u"),   # VTSSUnsigned8
        'ipv4SrcIp': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.406.0", "a"),   # IpAddress
        'ipv4SrcIpMask': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.407.0", "a"),   # IpAddress
        'ipv4DestIp': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.408.0", "a"),   # IpAddress
        'ipv4DestIpMask': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.409.0", "a"),   # IpAddress
        'ipv4SrcPortOp': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.410.0", "i"),   # VTSSASRType
        'ipv4SrcPort': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.411.0", "u"),   # VTSSUnsigned16
        'ipv4SrcPortRange': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.412.0", "u"),   # VTSSUnsigned16
        'ipv4DestPortOp': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.413.0", "i"),   # VTSSASRType
        'ipv4DestPort': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.414.0", "u"),   # VTSSUnsigned16
        'ipv4DestPortRange': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.415.0", "u"),   # VTSSUnsigned16
        'ipv6DscpOp': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.500.0", "i"),   # VTSSASRType
        'ipv6Dscp': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.501.0", "u"),   # VTSSUnsigned16
        'ipv6DscpRange': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.502.0", "u"),   # VTSSUnsigned16
        'ipv6Protocol': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.503.0", "u"),   # VTSSUnsigned8
        'ipv6ProtocolMask': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.504.0", "u"),   # VTSSUnsigned8
        'ipv6SrcIp': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.506.0", "x"),   # InetAddressIPv6
        'ipv6SrcIpMask': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.508.0", "x"),   # InetAddressIPv6
        'ipv6DestIp': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.510.0", "x"),   # InetAddressIPv6
        'ipv6DestIpMask': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.512.0", "x"),   # InetAddressIPv6
        'ipv6SrcPortOp': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.513.0", "i"),   # VTSSASRType
        'ipv6SrcPort': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.514.0", "u"),   # VTSSUnsigned16
        'ipv6SrcPortRange': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.515.0", "u"),   # VTSSUnsigned16
        'ipv6DestPortOp': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.516.0", "i"),   # VTSSASRType
        'ipv6DestPort': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.517.0", "u"),   # VTSSUnsigned16
        'ipv6DestPortRange': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.518.0", "u"),   # VTSSUnsigned16
        'actionCosEnable': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.1000.0", "i"),   # TruthValue
        'actionCos': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.1001.0", "u"),   # Unsigned32
        'actionDplEnable': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.1002.0", "i"),   # TruthValue
        'actionDpl': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.1003.0", "u"),   # VTSSUnsigned8
        'actionDscpEnable': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.1004.0", "i"),   # TruthValue
        'actionDscp': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.1005.0", "u"),   # VTSSUnsigned8
        'actionPcpDeiEnable': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.1006.0", "i"),   # TruthValue
        'actionPcp': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.1007.0", "u"),   # Unsigned32
        'actionDei': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.1008.0", "u"),   # VTSSUnsigned8
        'actionPolicyEnable': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.1009.0", "i"),   # TruthValue
        'actionPolicy': EditorField("1.3.6.1.4.1.5468.100.14.1.2.3.2.1010.0", "u"),   # Unsigned32
    },
)

SNMP_CONFIG_ACCESS_GROUP_TABLE = RowEditorSpec(
    name="ml540mSnmpConfigAccessGroupTable",
    action_oid="1.3.6.1.4.1.5468.100.36.1.2.9.100.0",
    table_oid="1.3.6.1.4.1.5468.100.36.1.2.8",
    row_action_column_oid="1.3.6.1.4.1.5468.100.36.1.2.8.1.100",
    index_spec=IndexSpec(names=['accessGroupName', 'securityModel', 'securityLevel'], kinds=['string', 'integer', 'integer']),
    fields={
        'accessGroupName': EditorField("1.3.6.1.4.1.5468.100.36.1.2.9.1.0", "s"),   # VTSSDisplayString (SIZE(0..32))
        'securityModel': EditorField("1.3.6.1.4.1.5468.100.36.1.2.9.2.0", "i"),   # VTSSSnmpSecurityModel
        'securityLevel': EditorField("1.3.6.1.4.1.5468.100.36.1.2.9.3.0", "i"),   # VTSSSnmpSecurityLevel
        'readViewName': EditorField("1.3.6.1.4.1.5468.100.36.1.2.9.4.0", "s"),   # VTSSDisplayString (SIZE(0..32))
        'writeViewName': EditorField("1.3.6.1.4.1.5468.100.36.1.2.9.5.0", "s"),   # VTSSDisplayString (SIZE(0..32))
    },
)

SNMP_CONFIG_COMMUNITY_TABLE = RowEditorSpec(
    name="ml540mSnmpConfigCommunityTable",
    action_oid="1.3.6.1.4.1.5468.100.36.1.2.3.100.0",
    table_oid="1.3.6.1.4.1.5468.100.36.1.2.2",
    row_action_column_oid="1.3.6.1.4.1.5468.100.36.1.2.2.1.100",
    index_spec=IndexSpec(names=['name', 'sourceIP', 'sourceIPPrefixSize'], kinds=['string', 'ipaddress', 'integer']),
    fields={
        'name': EditorField("1.3.6.1.4.1.5468.100.36.1.2.3.1.0", "s"),   # VTSSDisplayString (SIZE(0..32))
        'sourceIP': EditorField("1.3.6.1.4.1.5468.100.36.1.2.3.2.0", "a"),   # IpAddress
        'sourceIPPrefixSize': EditorField("1.3.6.1.4.1.5468.100.36.1.2.3.3.0", "i"),   # Integer32 (0..32)
    },
)

SNMP_CONFIG_USER_TABLE = RowEditorSpec(
    name="ml540mSnmpConfigUserTable",
    action_oid="1.3.6.1.4.1.5468.100.36.1.2.5.100.0",
    table_oid="1.3.6.1.4.1.5468.100.36.1.2.4",
    row_action_column_oid="1.3.6.1.4.1.5468.100.36.1.2.4.1.100",
    index_spec=IndexSpec(names=['engineId', 'userName'], kinds=['string', 'string']),
    fields={
        'engineId': EditorField("1.3.6.1.4.1.5468.100.36.1.2.5.1.0", "s"),   # OCTET STRING (SIZE(5..32))
        'userName': EditorField("1.3.6.1.4.1.5468.100.36.1.2.5.2.0", "s"),   # VTSSDisplayString (SIZE(0..32))
        'securityLevel': EditorField("1.3.6.1.4.1.5468.100.36.1.2.5.3.0", "i"),   # VTSSSnmpSecurityLevel
        'authProtocol': EditorField("1.3.6.1.4.1.5468.100.36.1.2.5.4.0", "i"),   # VTSSSnmpAuthProtocl
        'authPassword': EditorField("1.3.6.1.4.1.5468.100.36.1.2.5.5.0", "s"),   # VTSSDisplayString
        'privProtocol': EditorField("1.3.6.1.4.1.5468.100.36.1.2.5.6.0", "i"),   # VTSSSnmpPrivProtocl
        'privPassword': EditorField("1.3.6.1.4.1.5468.100.36.1.2.5.7.0", "s"),   # VTSSDisplayString
    },
)

SNMP_CONFIG_USER_TO_ACCESS_GROUP_TABLE = RowEditorSpec(
    name="ml540mSnmpConfigUserToAccessGroupTable",
    action_oid="1.3.6.1.4.1.5468.100.36.1.2.7.100.0",
    table_oid="1.3.6.1.4.1.5468.100.36.1.2.6",
    row_action_column_oid="1.3.6.1.4.1.5468.100.36.1.2.6.1.100",
    index_spec=IndexSpec(names=['securityModel', 'userOrCommunity'], kinds=['integer', 'string']),
    fields={
        'securityModel': EditorField("1.3.6.1.4.1.5468.100.36.1.2.7.1.0", "i"),   # VTSSSnmpSecurityModel
        'userOrCommunity': EditorField("1.3.6.1.4.1.5468.100.36.1.2.7.2.0", "s"),   # VTSSDisplayString (SIZE(0..32))
        'accessGroupName': EditorField("1.3.6.1.4.1.5468.100.36.1.2.7.3.0", "s"),   # VTSSDisplayString (SIZE(0..32))
    },
)

SNMP_CONFIG_VIEW_TABLE = RowEditorSpec(
    name="ml540mSnmpConfigViewTable",
    action_oid="1.3.6.1.4.1.5468.100.36.1.2.11.100.0",
    table_oid="1.3.6.1.4.1.5468.100.36.1.2.10",
    row_action_column_oid="1.3.6.1.4.1.5468.100.36.1.2.10.1.100",
    index_spec=IndexSpec(names=['name', 'subtree'], kinds=['string', 'string']),
    fields={
        'name': EditorField("1.3.6.1.4.1.5468.100.36.1.2.11.1.0", "s"),   # VTSSDisplayString (SIZE(0..32))
        'subtree': EditorField("1.3.6.1.4.1.5468.100.36.1.2.11.2.0", "s"),   # VTSSDisplayString (SIZE(0..64))
        'viewType': EditorField("1.3.6.1.4.1.5468.100.36.1.2.11.3.0", "i"),   # VTSSSnmpViewType
    },
)

TT_LOOP_CONFIG_INSTANCE = RowEditorSpec(
    name="ml540mTtLoopConfigInstance",
    action_oid="1.3.6.1.4.1.5468.100.128.1.2.2.100.0",
    table_oid="1.3.6.1.4.1.5468.100.128.1.2.1",
    row_action_column_oid="1.3.6.1.4.1.5468.100.128.1.2.1.1.100",
    index_spec=IndexSpec(names=['id'], kinds=['integer']),
    fields={
        'id': EditorField("1.3.6.1.4.1.5468.100.128.1.2.2.1.0", "i"),   # Integer32 (0..2147483647)
        'name': EditorField("1.3.6.1.4.1.5468.100.128.1.2.2.2.0", "s"),   # VTSSDisplayString (SIZE(0..32))
        'type': EditorField("1.3.6.1.4.1.5468.100.128.1.2.2.3.0", "i"),   # VTSSTtLoopInstanceType
        'direction': EditorField("1.3.6.1.4.1.5468.100.128.1.2.2.4.0", "i"),   # VTSSTtLoopInstanceDirection
        'flow': EditorField("1.3.6.1.4.1.5468.100.128.1.2.2.6.0", "i"),   # VTSSInterfaceIndex
        'port': EditorField("1.3.6.1.4.1.5468.100.128.1.2.2.7.0", "i"),   # VTSSInterfaceIndex
        'level': EditorField("1.3.6.1.4.1.5468.100.128.1.2.2.8.0", "u"),   # Unsigned32
        'subscriber': EditorField("1.3.6.1.4.1.5468.100.128.1.2.2.9.0", "i"),   # VTSSTtLoopInstanceSubscriber
        'adminState': EditorField("1.3.6.1.4.1.5468.100.128.1.2.2.10.0", "i"),   # VTSSTtLoopInstanceAdminState
    },
)

USERS_CONFIG_TABLE = RowEditorSpec(
    name="ml540mUsersConfigTable",
    action_oid="1.3.6.1.4.1.5468.100.58.1.2.2.100.0",
    table_oid="1.3.6.1.4.1.5468.100.58.1.2.1",
    row_action_column_oid="1.3.6.1.4.1.5468.100.58.1.2.1.1.100",
    index_spec=IndexSpec(names=['username'], kinds=['string']),
    fields={
        'username': EditorField("1.3.6.1.4.1.5468.100.58.1.2.2.1.0", "s"),   # VTSSDisplayString (SIZE(0..31))
        'privilege': EditorField("1.3.6.1.4.1.5468.100.58.1.2.2.2.0", "u"),   # Unsigned32
        'encrypted': EditorField("1.3.6.1.4.1.5468.100.58.1.2.2.3.0", "i"),   # TruthValue
        'password': EditorField("1.3.6.1.4.1.5468.100.58.1.2.2.4.0", "s"),   # VTSSDisplayString (SIZE(0..44))
    },
)

VCL_CONFIG_IP = RowEditorSpec(
    name="ml540mVclConfigIp",
    action_oid="1.3.6.1.4.1.5468.100.79.1.2.2.2.100.0",
    table_oid="1.3.6.1.4.1.5468.100.79.1.2.2.1",
    row_action_column_oid="1.3.6.1.4.1.5468.100.79.1.2.2.1.1.100",
    index_spec=IndexSpec(names=['ipSubnetAddress', 'ipSubnetMaskLength'], kinds=['ipaddress', 'integer']),
    fields={
        'ipSubnetAddress': EditorField("1.3.6.1.4.1.5468.100.79.1.2.2.2.1.0", "a"),   # IpAddress
        'ipSubnetMaskLength': EditorField("1.3.6.1.4.1.5468.100.79.1.2.2.2.2.0", "i"),   # Integer32 (1..32)
        'vlanId': EditorField("1.3.6.1.4.1.5468.100.79.1.2.2.2.3.0", "i"),   # Integer32 (1..4095)
        'portList': EditorField("1.3.6.1.4.1.5468.100.79.1.2.2.2.4.0", "s"),   # VTSSPortList
    },
)

VCL_CONFIG_MAC = RowEditorSpec(
    name="ml540mVclConfigMac",
    action_oid="1.3.6.1.4.1.5468.100.79.1.2.1.2.100.0",
    table_oid="1.3.6.1.4.1.5468.100.79.1.2.1.1",
    row_action_column_oid="1.3.6.1.4.1.5468.100.79.1.2.1.1.1.100",
    index_spec=IndexSpec(names=['macAddress'], kinds=['string']),
    fields={
        'macAddress': EditorField("1.3.6.1.4.1.5468.100.79.1.2.1.2.1.0", "x"),   # MacAddress
        'vlanId': EditorField("1.3.6.1.4.1.5468.100.79.1.2.1.2.2.0", "i"),   # Integer32 (1..4095)
        'portList': EditorField("1.3.6.1.4.1.5468.100.79.1.2.1.2.3.0", "s"),   # VTSSPortList
    },
)

VCL_CONFIG_PROTOCOL_GROUP = RowEditorSpec(
    name="ml540mVclConfigProtocolGroup",
    action_oid="1.3.6.1.4.1.5468.100.79.1.2.3.2.2.100.0",
    table_oid="1.3.6.1.4.1.5468.100.79.1.2.3.2.1",
    row_action_column_oid="1.3.6.1.4.1.5468.100.79.1.2.3.2.1.1.100",
    index_spec=IndexSpec(names=['protocolGroupName'], kinds=['string']),
    fields={
        'protocolGroupName': EditorField("1.3.6.1.4.1.5468.100.79.1.2.3.2.2.1.0", "s"),   # VTSSDisplayString (SIZE(0..16))
        'vlanId': EditorField("1.3.6.1.4.1.5468.100.79.1.2.3.2.2.2.0", "i"),   # Integer32 (1..4095)
        'portList': EditorField("1.3.6.1.4.1.5468.100.79.1.2.3.2.2.3.0", "s"),   # VTSSPortList
    },
)

VCL_CONFIG_PROTOCOL_PROTO = RowEditorSpec(
    name="ml540mVclConfigProtocolProto",
    action_oid="1.3.6.1.4.1.5468.100.79.1.2.3.1.2.100.0",
    table_oid="1.3.6.1.4.1.5468.100.79.1.2.3.1.1",
    row_action_column_oid="1.3.6.1.4.1.5468.100.79.1.2.3.1.1.1.100",
    index_spec=IndexSpec(names=['protocolEncapsulation'], kinds=['string']),
    fields={
        'protocolEncapsulation': EditorField("1.3.6.1.4.1.5468.100.79.1.2.3.1.2.1.0", "s"),   # VTSSVclProtoEncap
        'protocolGroupName': EditorField("1.3.6.1.4.1.5468.100.79.1.2.3.1.2.2.0", "s"),   # VTSSDisplayString (SIZE(0..16))
    },
)

VLAN_CONFIG_INTERFACES_SVL_TABLE = RowEditorSpec(
    name="ml540mVlanConfigInterfacesSvlTable",
    action_oid="1.3.6.1.4.1.5468.100.13.1.2.2.3.100.0",
    table_oid="1.3.6.1.4.1.5468.100.13.1.2.2.2",
    row_action_column_oid="1.3.6.1.4.1.5468.100.13.1.2.2.2.1.100",
    index_spec=IndexSpec(names=['vlanId'], kinds=['integer']),
    fields={
        'vlanId': EditorField("1.3.6.1.4.1.5468.100.13.1.2.2.3.1.0", "u"),   # VTSSVlan
        'filterId': EditorField("1.3.6.1.4.1.5468.100.13.1.2.2.3.2.0", "u"),   # VTSSUnsigned16
    },
)

VLAN_TRANSLATION_CONFIG_TRANSLATION = RowEditorSpec(
    name="ml540mVlanTranslationConfigTranslation",
    action_oid="1.3.6.1.4.1.5468.100.85.1.2.1.2.100.0",
    table_oid="1.3.6.1.4.1.5468.100.85.1.2.1.1",
    row_action_column_oid="1.3.6.1.4.1.5468.100.85.1.2.1.1.1.100",
    index_spec=IndexSpec(names=['groupId', 'vlanId'], kinds=['integer', 'integer']),
    fields={
        'groupId': EditorField("1.3.6.1.4.1.5468.100.85.1.2.1.2.1.0", "i"),   # Integer32 (1..65535)
        'vlanId': EditorField("1.3.6.1.4.1.5468.100.85.1.2.1.2.2.0", "i"),   # Integer32 (1..4095)
        'tVlanId': EditorField("1.3.6.1.4.1.5468.100.85.1.2.1.2.3.0", "i"),   # Integer32 (1..4095)
    },
)

VOICE_VLAN_CONFIG_OUI_TABLE = RowEditorSpec(
    name="ml540mVoiceVlanConfigOuiTable",
    action_oid="1.3.6.1.4.1.5468.100.70.1.2.3.2.100.0",
    table_oid="1.3.6.1.4.1.5468.100.70.1.2.3.1",
    row_action_column_oid="1.3.6.1.4.1.5468.100.70.1.2.3.1.1.100",
    index_spec=IndexSpec(names=['prefix'], kinds=['string']),
    fields={
        'prefix': EditorField("1.3.6.1.4.1.5468.100.70.1.2.3.2.1.0", "s"),   # OCTET STRING (SIZE(3..3))
        'description': EditorField("1.3.6.1.4.1.5468.100.70.1.2.3.2.2.0", "s"),   # VTSSDisplayString (SIZE(0..32))
    },
)

ALL_SPECS = {s.name: s for s in [
    ACCESS_MANAGEMENT_CONFIG_IPV4_TABLE,
    ACCESS_MANAGEMENT_CONFIG_IPV6_TABLE,
    ACL_CONFIG_ACE,
    AGGR_CONFIG_GROUP_TABLE,
    ARP_INSPECTION_CONFIG_STATIC_TABLE,
    ARP_INSPECTION_CONFIG_VLAN_TABLE,
    DHCP6_CLIENT_CONFIG_INTERFACE_TABLE,
    DHCP_SERVER_CONFIG_EXCLUDED_IP_TABLE,
    DHCP_SERVER_CONFIG_POOL_TABLE,
    EPS_CONFIG_INSTANCE,
    ERPS_CONFIG,
    EVC_CONFIG_ECE_TABLE,
    EVC_CONFIG_EVC_TABLE,
    EVC_CONFIG_MPLS_TP_PW_TABLE,
    HQOS_CONFIG_INTERFACE_HQOS_TABLE,
    IP_CONFIG_INTERFACES_TABLE,
    IP_CONFIG_ROUTES_IPV4,
    IP_CONFIG_ROUTES_IPV6,
    IPMC_MVR_CONFIG_INTERFACE_TABLE,
    IPMC_PROFILE_CONFIG_IPV4_ADDRESS_RANGE_TABLE,
    IPMC_PROFILE_CONFIG_IPV6_ADDRESS_RANGE_TABLE,
    IPMC_PROFILE_CONFIG_MANAGEMENT_TABLE,
    IPMC_PROFILE_CONFIG_RULE_TABLE,
    IPMC_SNOOPING_CONFIG_IGMP_INTERFACE_TABLE,
    IPMC_SNOOPING_CONFIG_MLD_INTERFACE_TABLE,
    JSON_RPC_NOTIFICATION_CONFIG_DESTINATION,
    JSON_RPC_NOTIFICATION_CONFIG_NOTIFICATION,
    LLDP_CONFIG_MED_POLICY,
    MAC_CONFIG_FDB_TABLE,
    MEP_CONFIG_AIS,
    MEP_CONFIG_APS,
    MEP_CONFIG_BFD,
    MEP_CONFIG_BFD_AUTH,
    MEP_CONFIG_CC,
    MEP_CONFIG_CLIENT_FLOW,
    MEP_CONFIG_INSTANCE,
    MEP_CONFIG_INSTANCE_PEER,
    MEP_CONFIG_LB,
    MEP_CONFIG_LCK,
    MEP_CONFIG_LT,
    MEP_CONFIG_RT,
    MEP_CONFIG_TST,
    MPLS_CONFIG_COS_MAP,
    MPLS_CONFIG_LINK,
    MPLS_CONFIG_LSP,
    MPLS_CONFIG_PW,
    MPLS_CONFIG_TUNNEL,
    PTP_CONFIG_CLOCKS_DEFAULT_DS_TABLE,
    PVLAN_CONFIG_INTERFACE_VLAN_MEMBERSHIP_TABLE,
    QOS_CONFIG_QCE_TABLE,
    SNMP_CONFIG_ACCESS_GROUP_TABLE,
    SNMP_CONFIG_COMMUNITY_TABLE,
    SNMP_CONFIG_USER_TABLE,
    SNMP_CONFIG_USER_TO_ACCESS_GROUP_TABLE,
    SNMP_CONFIG_VIEW_TABLE,
    TT_LOOP_CONFIG_INSTANCE,
    USERS_CONFIG_TABLE,
    VCL_CONFIG_IP,
    VCL_CONFIG_MAC,
    VCL_CONFIG_PROTOCOL_GROUP,
    VCL_CONFIG_PROTOCOL_PROTO,
    VLAN_CONFIG_INTERFACES_SVL_TABLE,
    VLAN_TRANSLATION_CONFIG_TRANSLATION,
    VOICE_VLAN_CONFIG_OUI_TABLE,
]}
