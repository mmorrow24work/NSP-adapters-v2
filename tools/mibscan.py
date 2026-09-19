#!/usr/bin/env python3
"""Independent SMIv2 extractor: object inventory + OID resolution.

Deliberately NOT smidump. The original project's OID maps and object counts
were produced with libsmi; this is a second, independent implementation so
those numbers can be cross-checked rather than taken on trust. (Doing so
confirmed the headline figures -- ML620R-MIB 290 objects / 164 read-write,
13 alarm traps covering GE ports 1-10 only, exactly one SMIv2 Entry
sub-identifier violation in ACTELIS-SERV-MON-MIB -- and surfaced the
coverage gaps documented in docs/mib-analysis/coverage-gaps.md.)

It is also what makes MIB drift a build failure: tests/test_mib_conformance.py
uses it to check every OID constant and index spec in the code against the
vendor archives.

Usage:
    python3 tools/mibscan.py <dir> [<dir> ...] [-o out.json]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import defaultdict

DEF_RE = re.compile(
    r"(?ms)^[ \t]*(?!IMPORTS\b)(?P<name>[a-zA-Z][\w-]*)[ \t]+"
    r"(?P<kind>OBJECT-TYPE|NOTIFICATION-TYPE|MODULE-IDENTITY|OBJECT-IDENTITY|"
    r"OBJECT-GROUP|NOTIFICATION-GROUP|MODULE-COMPLIANCE|AGENT-CAPABILITIES)"
    r"\b(?![ \t]*,)(?P<body>.*?)::=\s*\{(?P<parent>[^}]*)\}")
OI_RE = re.compile(
    r"(?m)^\s*(?P<name>[a-zA-Z][\w-]*)\s+OBJECT\s+IDENTIFIER\s*::=\s*\{(?P<parent>[^}]*)\}")
TC_RE = re.compile(
    r"(?ms)^\s*(?P<name>[A-Za-z][\w-]*)\s*::=\s*TEXTUAL-CONVENTION(?P<body>.*?)"
    r"SYNTAX\s+(?P<syntax>.*?)(?=\n\s*\n|\n[A-Za-z][\w-]*\s*::=|\nEND)")
SYNTAX_RE = re.compile(
    r"(?ms)\bSYNTAX\s+(?P<v>.*?)(?=\n\s*(?:UNITS|MAX-ACCESS|ACCESS|STATUS|DESCRIPTION|"
    r"REFERENCE|INDEX|AUGMENTS|DEFVAL)\b)")
ACCESS_RE = re.compile(r"\b(?:MAX-ACCESS|ACCESS)\s+([a-z-]+)")
INDEX_RE = re.compile(r"(?ms)\bINDEX\s*\{(?P<v>[^}]*)\}")
AUGMENTS_RE = re.compile(r"(?ms)\bAUGMENTS\s*\{(?P<v>[^}]*)\}")
UNITS_RE = re.compile(r'(?ms)\bUNITS\s+"(?P<v>[^"]*)"')
DESC_RE = re.compile(r'(?ms)\bDESCRIPTION\s+"(?P<v>.*?)"')
OBJECTS_RE = re.compile(r"(?ms)\bOBJECTS\s*\{(?P<v>[^}]*)\}")
SUBID_RE = re.compile(r"^[A-Za-z][\w-]*\((\d+)\)$")

ROOTS = {
    "iso": "1", "org": "1.3", "dod": "1.3.6", "internet": "1.3.6.1",
    "directory": "1.3.6.1.1", "mgmt": "1.3.6.1.2", "mib-2": "1.3.6.1.2.1",
    "transmission": "1.3.6.1.2.1.10", "experimental": "1.3.6.1.3",
    "private": "1.3.6.1.4", "enterprises": "1.3.6.1.4.1", "snmpV2": "1.3.6.1.6",
    "snmpModules": "1.3.6.1.6.3", "snmpMIB": "1.3.6.1.6.3.1",
}


def _squash(match, key="v"):
    return " ".join(match.group(key).split()) if match else ""


def parse_file(path: str) -> tuple[str, dict, dict]:
    with open(path, encoding="utf-8", errors="replace") as fh:
        txt = re.sub(r"--[^\n]*", "", fh.read())
    mod = re.search(r"(?m)^\s*([A-Za-z][\w-]*)\s+DEFINITIONS\s*::=\s*BEGIN", txt)
    module = mod.group(1) if mod else os.path.basename(path)

    defs: dict[str, dict] = {}
    for m in DEF_RE.finditer(txt):
        body = m.group("body")
        defs[m.group("name")] = {
            "name": m.group("name"), "kind": m.group("kind"), "module": module,
            "parent": m.group("parent").split(),
            "syntax": _squash(SYNTAX_RE.search(body)),
            "access": (ACCESS_RE.search(body).group(1) if ACCESS_RE.search(body) else ""),
            "index": _squash(INDEX_RE.search(body)),
            "augments": _squash(AUGMENTS_RE.search(body)),
            "units": _squash(UNITS_RE.search(body)),
            "objects": _squash(OBJECTS_RE.search(body)),
            "description": _squash(DESC_RE.search(body))[:400],
        }
    for m in OI_RE.finditer(txt):
        defs.setdefault(m.group("name"), {
            "name": m.group("name"), "kind": "OBJECT IDENTIFIER", "module": module,
            "parent": m.group("parent").split(), "syntax": "", "access": "",
            "index": "", "augments": "", "units": "", "objects": "", "description": ""})

    tcs = {f"{module}:{m.group('name')}": " ".join(m.group("syntax").split())
           for m in TC_RE.finditer(txt)}
    return module, defs, tcs


def resolve(all_defs: dict) -> dict[str, str]:
    """Resolve every name to a dotted numeric OID."""
    oid = dict(ROOTS)

    def subid(token: str) -> str | None:
        m = SUBID_RE.match(token)          # handles `{ enterprises actelis(5468) 5 }`
        if m:
            return m.group(1)
        return token if token.isdigit() else None

    def res(name: str, seen: set | None = None) -> str | None:
        seen = seen or set()
        if name in oid:
            return oid[name]
        if name in seen or name not in all_defs:
            return None
        seen.add(name)
        parent = all_defs[name]["parent"]
        if not parent:
            return None
        if parent[0].isdigit():
            value = ".".join(p for p in parent if p.isdigit())
        else:
            base = res(parent[0], seen)
            if base is None:
                return None
            tail = [s for s in (subid(p) for p in parent[1:]) if s]
            value = base + ("." + ".".join(tail) if tail else "")
        oid[name] = value
        return value

    for name in list(all_defs):
        res(name)
    return oid


def scan(dirs: list[str]) -> tuple[dict, dict, list[str]]:
    all_defs: dict[str, dict] = {}
    per_module: dict[str, dict] = defaultdict(dict)
    all_tcs: dict[str, str] = {}
    files: list[str] = []
    for d in dirs:
        for root, _dirs, names in os.walk(d):
            files.extend(os.path.join(root, n) for n in names
                         if n.lower().endswith((".mib", ".my")))
    for path in sorted(files):
        try:
            module, defs, tcs = parse_file(path)
        except Exception as exc:                       # noqa: BLE001
            print(f"PARSE FAIL {path}: {exc}", file=sys.stderr)
            continue
        per_module[module].update(defs)
        all_tcs.update(tcs)
        for key, value in defs.items():
            all_defs.setdefault(key, value)
    scan.tcs = all_tcs                                  # type: ignore[attr-defined]
    global ALL_TCS
    ALL_TCS = all_tcs
    return all_defs, per_module, sorted(files)


ALL_TCS: dict[str, str] = {}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("dirs", nargs="+")
    ap.add_argument("-o", "--out", help="write the full parse to this JSON file")
    args = ap.parse_args()

    all_defs, per_module, files = scan(args.dirs)
    oids = resolve(all_defs)
    for d in all_defs.values():
        d["oid"] = oids.get(d["name"], "")

    resolved = sum(1 for d in all_defs.values() if d["oid"])
    print(f"files={len(files)} modules={len(per_module)} defs={len(all_defs)} "
          f"resolved={resolved}")
    if args.out:
        with open(args.out, "w") as fh:
            json.dump({"tcs": ALL_TCS, "defs": all_defs,
                       "modules": {m: list(d) for m, d in per_module.items()},
                       "files": files}, fh)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
