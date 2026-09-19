#!/usr/bin/env python3
"""
Extracts ACTELIS-SERV-MON-MIB.mib into the same OID-map CSV format used
for the rest of the DSL modem's oid-maps/dsl-modem/actelis_oid_map.csv
(MIB Module, Object Name, OID, Kind, Syntax, Access, Description),
using smidump's python output format (a literal dict we can exec/import).
"""
from pathlib import Path
import csv
import sys

sys.path.insert(0, "/tmp")
import importlib.util

spec = importlib.util.spec_from_file_location("servmon", "/tmp/servmon.py")
servmon = importlib.util.module_from_spec(spec)
spec.loader.exec_module(servmon)

nodes = servmon.MIB["nodes"]

SYNTAX_MAP_KEYWORDS = {
    "integer32": "Integer32",
    "unsigned32": "Unsigned32",
    "counter32": "Counter32",
    "counter64": "Counter64",
    "gauge32": "Gauge32",
    "octetstring": "OCTET STRING",
}


def format_syntax(node):
    syntax = node.get("syntax")
    if not syntax:
        return ""
    type_info = syntax.get("type", {})
    module = type_info.get("module", "")
    name = type_info.get("name", "")
    if module and module != node.get("moduleName") and module not in ("SNMPv2-SMI",):
        return name  # textual convention / imported type -- keep its name
    return name


def format_access(node):
    access = node.get("access", "")
    mapping = {
        "readonly": "read-only",
        "readwrite": "read-write",
        "readcreate": "read-create",
        "notify": "notify-only",
        "noaccess": "not-accessible",
    }
    return mapping.get(access, access)


rows = []
for name, node in nodes.items():
    nodetype = node.get("nodetype")
    if nodetype not in ("scalar", "column"):
        continue
    description = (node.get("description") or "").strip().replace("\n", " ")
    description = " ".join(description.split())  # collapse whitespace
    rows.append({
        "MIB Module": node.get("moduleName", "ACTELIS-SERV-MON-MIB"),
        "Object Name": name,
        "OID": node.get("oid", ""),
        "Kind": nodetype,
        "Syntax": format_syntax(node),
        "Access": format_access(node),
        "Description": description[:500],
    })

rows.sort(key=lambda r: [int(x) for x in r["OID"].split(".")])

# Original hardcoded an absolute path under /home/claude.
out_path = str(Path(__file__).resolve().parent.parent
               / "data" / "oid-maps" / "dsl-modem" / "actelis_servmon_oid_map.csv")
with open(out_path, "w", newline="", encoding="utf-8") as fh:
    writer = csv.DictWriter(fh, fieldnames=[
        "MIB Module", "Object Name", "OID", "Kind", "Syntax", "Access", "Description",
    ])
    writer.writeheader()
    writer.writerows(rows)

print(f"wrote {len(rows)} objects -> {out_path}")
