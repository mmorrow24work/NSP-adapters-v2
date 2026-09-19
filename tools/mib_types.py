"""Map SMIv2 SYNTAX (including vendor textual conventions) to net-snmp type chars.

net-snmp `snmpset` type characters:
  i INTEGER   u unsigned   s string   x hex string   a IpAddress
  o OID       t timeticks  b bits     d decimal string

Getting this right is not cosmetic: the original row-editor helper sent every
staged field as `s`, which the agent rejects with wrongType for the IpAddress
and Integer32 columns of the very table it shipped a spec for.
"""
from __future__ import annotations

import re

_DIRECT = {
    "IpAddress": "a", "Integer32": "i", "INTEGER": "i", "Unsigned32": "u",
    "Gauge32": "u", "Gauge": "u", "Counter32": "u", "Counter64": "u",
    "TimeTicks": "t", "OBJECT IDENTIFIER": "o", "OCTET STRING": "s",
    "DisplayString": "s", "TruthValue": "i", "MacAddress": "x",
    "PhysAddress": "x", "BITS": "b", "SnmpAdminString": "s",
    "InetAddressIPv6": "x", "RowStatus": "i", "DateAndTime": "x",
}


def base_syntax(syntax: str, tcs: dict[str, str], _depth: int = 0) -> str:
    """Resolve a SYNTAX string down to a base SMI type, following TCs."""
    s = re.sub(r"\s+", " ", (syntax or "").strip())
    s = re.sub(r"\s*\(.*\)$", "", s).strip()          # drop (SIZE(..)) / ranges
    if _depth > 8 or not s:
        return s
    if s.startswith("INTEGER {") or s.startswith("INTEGER{"):
        return "INTEGER"
    if s in _DIRECT:
        return s
    for key, val in tcs.items():                       # "MODULE:TCName" -> syntax
        if key.split(":", 1)[1] == s:
            return base_syntax(val, tcs, _depth + 1)
    return s


def type_char(syntax: str, tcs: dict[str, str]) -> str:
    base = base_syntax(syntax, tcs)
    if base.startswith("INTEGER"):
        return "i"
    if base in _DIRECT:
        return _DIRECT[base]
    if base.startswith("OCTET STRING"):
        return "s"
    return "s"


def index_kind(syntax: str, tcs: dict[str, str]) -> str:
    """Map an INDEX column's syntax to an snmp.oid index kind."""
    base = base_syntax(syntax, tcs)
    if base == "IpAddress":
        return "ipaddress"
    if base in ("OCTET STRING", "DisplayString", "SnmpAdminString", "MacAddress",
                "PhysAddress", "InetAddressIPv6", "DateAndTime"):
        return "string"
    return "integer"
