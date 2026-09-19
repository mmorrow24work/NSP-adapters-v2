#!/usr/bin/env python3
"""Build the per-device-type attribute schema from the raw OID maps.

Mechanical transform of every object in the source MIBs -- it does NOT decide
which objects NSP should expose (that curation needs a real NSP Device Model
to target).

Three defects in the original are fixed:

1. ``REPO`` was hardcoded to ``/home/claude/NSP-adapters``, so the script
   could only ever run on one machine despite the docs calling it
   reproducible. Now resolved relative to this file.

2. ``infer_unit()`` lowercased the description and then matched the
   case-sensitive patterns ``\\bdBm\\b`` and ``\\bdB\\b`` against it, so those
   two patterns could never fire. Every object measured in dB silently got a
   blank unit -- including ``efmCuPmePeerSnrMgn``, ``efmCuPmeLineAtn`` and
   ``efmCuPmePeerLineAtn``, i.e. exactly the DSL line-quality metrics that
   matter most. Matching is now case-insensitive on the original text.

3. Units were inferred only from free-text descriptions, ignoring the
   object's own type and UNITS clause. A ``VTSSPercent`` column is a percent
   whether or not its description says so. Type-derived units now take
   precedence, and the source of each unit is recorded in a new
   ``unit_source`` column so a reader can tell evidence from inference.

Also adds ``textual_convention`` as its own column rather than encoding it
inside ``data_type``, and preserves TC names even when the SYNTAX carries a
size or range constraint (``VTSSDisplayString (SIZE(0..32))`` previously fell
through to a bare ``string``).

Usage:  python3 tools/build_attribute_schema.py
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT_DIR = REPO / "data" / "attribute-schema"

SOURCES = {
    "dsl-modem": [REPO / "data/oid-maps/dsl-modem/actelis_oid_map.csv",
                  REPO / "data/oid-maps/dsl-modem/actelis_servmon_oid_map.csv"],
    "switch": [REPO / "data/oid-maps/switch/ml540m_core_oid_map.csv",
               REPO / "data/oid-maps/switch/ml540m_extended_oid_map.csv"],
}

FIELDNAMES = ["device_type", "mib_module", "object_name", "oid", "kind", "data_type",
              "textual_convention", "unit", "unit_source", "access", "configurable",
              "table_index", "nsp_attribute_name", "description"]

_TC_RE = re.compile(r"^([A-Za-z][A-Za-z0-9]*)\s*(\(.*\))?$")


def split_syntax(syntax: str) -> tuple[str, str]:
    """Return (base data type, textual convention name or '')."""
    s = " ".join((syntax or "").split())
    if s.startswith("INTEGER {") or s.startswith("INTEGER{"):
        return "enum", ""
    bare = re.sub(r"\s*\(.*\)$", "", s).strip()
    known = {
        "INTEGER": "integer", "Integer32": "integer", "Unsigned32": "unsigned32",
        "Counter64": "counter64", "Counter32": "counter32", "Counter": "counter32",
        "Gauge32": "gauge32", "Gauge": "gauge32", "IpAddress": "ipv4-address",
        "TimeTicks": "timeticks", "OBJECT IDENTIFIER": "oid", "BITS": "bitmap",
        "OCTET STRING": "string", "DisplayString": "string",
        "TruthValue": "boolean", "MacAddress": "mac-address",
        "PhysAddress": "mac-address",
    }
    if bare in known:
        return known[bare], ("" if bare in ("INTEGER", "Integer32", "Unsigned32",
                                            "Counter32", "Counter64", "Gauge32",
                                            "OCTET STRING", "OBJECT IDENTIFIER",
                                            "BITS", "IpAddress", "TimeTicks")
                             else bare)
    if s.startswith("SEQUENCE"):
        return "row-sequence", ""
    m = _TC_RE.match(s)
    if m:
        return "textual-convention", m.group(1)
    return "string", ""


def enum_is_boolean(syntax: str) -> bool:
    values = re.findall(r"\((\d+)\)", syntax or "")
    return len(values) == 2 and set(values) == {"1", "2"}


# Units derivable from the type itself -- stronger evidence than description text.
TC_UNITS = {
    "VTSSPercent": "percent", "Hdsl2ShdslPerfTimeElapsed": "seconds",
    "PerfCurrentCount": "count", "PerfIntervalCount": "count",
    "Hdsl2ShdslPerfCurrDayCount": "count", "Hdsl2Shdsl1DayIntervalCount": "count",
}
TYPE_UNITS = {"timeticks": "centiseconds", "counter32": "count", "counter64": "count"}

UNIT_PATTERNS = [
    (r"\bdBm\b", "dBm"), (r"\bdB\b", "dB"),
    (r"\bmilliseconds?\b|\bmsec\b", "milliseconds"),
    (r"\bmicroseconds?\b|\busec\b", "microseconds"),
    (r"\bnanoseconds?\b", "nanoseconds"),
    (r"\bseconds?\b|\bsec\b", "seconds"), (r"\bminutes?\b", "minutes"),
    (r"\bhours?\b", "hours"), (r"\bdays?\b", "days"),
    (r"\bpercent(age)?\b|%", "percent"),
    (r"\bkbps\b", "kbps"), (r"\bmbps\b", "mbps"), (r"\bgbps\b", "gbps"),
    (r"\bbytes?\b", "bytes"), (r"\boctets?\b", "octets"), (r"\bpackets?\b", "packets"),
    (r"\bframes?\b", "frames"),
    (r"\bcelsius\b|\bdegrees?\s*c\b", "celsius"), (r"\bvolts?\b|\bvdc\b", "volts"),
    (r"\bmiles?\b|\bkm\b|\bmeters?\b|\bfeet\b", "distance"),
]


def infer_unit(description: str, units_clause: str, tc: str, data_type: str) -> tuple[str, str]:
    """Return (unit, source-of-evidence)."""
    if units_clause and units_clause.strip():
        return units_clause.strip(), "UNITS clause"
    if tc and tc in TC_UNITS:
        return TC_UNITS[tc], f"textual convention {tc}"
    if data_type in TYPE_UNITS:
        return TYPE_UNITS[data_type], f"SMI type {data_type}"
    for pattern, unit in UNIT_PATTERNS:
        # case-INSENSITIVE against the original text: the original lowercased
        # first and then matched case-sensitive \bdBm\b, which never matched.
        if re.search(pattern, description or "", re.IGNORECASE):
            return unit, "description text"
    return "", ""


STRIP_PREFIXES = ["ml540m", "actelis", "servMon"]


def propose_attribute_name(object_name: str) -> str:
    name = object_name
    for prefix in STRIP_PREFIXES:
        if name.lower().startswith(prefix.lower()) and len(name) > len(prefix):
            rest = name[len(prefix):]
            if rest[:1].isupper():
                name = rest[0].lower() + rest[1:]
                break
    return (name[0].lower() + name[1:]) if name else name


def dedupe_names(rows: list[dict]) -> int:
    """Make nsp_attribute_name unique per device type. Returns #collisions fixed."""
    fixed = 0
    by_device: dict[str, list[dict]] = {}
    for row in rows:
        by_device.setdefault(row["device_type"], []).append(row)
    for device_rows in by_device.values():
        seen: dict[str, list[dict]] = {}
        for row in device_rows:
            seen.setdefault(row["nsp_attribute_name"], []).append(row)
        for _name, dupes in seen.items():
            if len(dupes) <= 1:
                continue
            for row in dupes:
                # Fall back to the fully-qualified object name, which is unique
                # per MIB; if that still collides, qualify with the module.
                candidate = row["object_name"][0].lower() + row["object_name"][1:]
                if sum(1 for d in dupes if d["object_name"] == row["object_name"]) > 1:
                    candidate = f"{row['mib_module'].lower().replace('-', '_')}_{candidate}"
                row["nsp_attribute_name"] = candidate
                fixed += 1
    return fixed


def process_csv(path: Path, device_type: str) -> list[dict]:
    out = []
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            syntax = (row.get("Syntax") or "").strip()
            access = (row.get("Access") or "").strip()
            description = (row.get("Description") or "").strip()
            units_clause = (row.get("Units") or "").strip()
            data_type, tc = split_syntax(syntax)
            if data_type == "enum" and enum_is_boolean(syntax):
                data_type = "boolean-enum"
            unit, unit_source = infer_unit(description, units_clause, tc, data_type)
            out.append({
                "device_type": device_type,
                "mib_module": (row.get("MIB Module") or "").strip(),
                "object_name": (row.get("Object Name") or "").strip(),
                "oid": (row.get("OID") or "").strip(),
                "kind": (row.get("Kind") or "").strip(),
                "data_type": data_type,
                "textual_convention": tc,
                "unit": unit,
                "unit_source": unit_source,
                "access": access,
                "configurable": "yes" if access in ("read-write", "read-create") else "no",
                "table_index": "yes" if (access == "not-accessible"
                                         and (row.get("Kind") or "").strip() == "column") else "no",
                "nsp_attribute_name": propose_attribute_name((row.get("Object Name") or "").strip()),
                "description": description,
            })
    return out


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for device_type, paths in SOURCES.items():
        rows: list[dict] = []
        for path in paths:
            if not path.exists():
                print(f"WARNING: missing source {path}", file=sys.stderr)
                continue
            rows.extend(process_csv(path, device_type))
        collisions = dedupe_names(rows)
        out_path = OUT_DIR / f"{device_type}-attribute-schema.csv"
        with open(out_path, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=FIELDNAMES)
            w.writeheader()
            w.writerows(rows)
        configurable = sum(1 for r in rows if r["configurable"] == "yes")
        united = sum(1 for r in rows if r["unit"])
        print(f"  {device_type:11s} {len(rows):5d} objects  {configurable:5d} configurable  "
              f"{united:4d} with units  {collisions:3d} name collisions resolved  -> {out_path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
