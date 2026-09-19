#!/usr/bin/env python3
"""Generate typed RowEditorSpec definitions for every row-editor table.

The VTSSRowEditorState protocol was proven end-to-end against one table (the
SNMP community table) on the lab ML540M. The MIB set contains 64 tables that
use the identical mechanism. Rather than hand-writing a spec per table -- the
error-prone step, and the one that produced the wrong-type bug in the
original -- this derives every spec mechanically from the MIBs: field OIDs,
their net-snmp type chars, the real table OID, the per-row Action column, and
the table's INDEX clause.

    python3 tools/gen_row_editor_specs.py > src/actelis_mediation/rowedit/specs.py
"""
from __future__ import annotations

import collections
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(__file__))
import mibscan                                              # noqa: E402
from mib_types import index_kind, type_char                 # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_switch_mibs():
    import py7zr
    tmp = tempfile.mkdtemp(prefix="ml540m-mibs-")
    with py7zr.SevenZipFile(os.path.join(REPO, "mibs", "actelis", "ML540M-MIB.7z")) as z:
        z.extractall(path=tmp)
    defs, _per_module, _files = mibscan.scan([tmp])
    oids = mibscan.resolve(defs)
    for d in defs.values():
        d["oid"] = oids.get(d["name"], "")
    return defs, getattr(mibscan, "ALL_TCS", {})


def main() -> int:
    defs, tcs = load_switch_mibs()
    by_name = defs
    editors: dict[str, list[dict]] = collections.defaultdict(list)
    for v in defs.values():
        if v["kind"] == "OBJECT-TYPE" and "RowEditor" in v["name"]:
            editors[v["name"].split("RowEditor")[0]].append(v)

    out: list[str] = []
    generated = 0
    for stem in sorted(editors):
        fields = [o for o in editors[stem] if not o["name"].endswith("RowEditorAction")]
        action = [o for o in editors[stem] if o["name"].endswith("RowEditorAction")]
        if not action or not fields:
            continue
        table_name = stem if stem.endswith("Table") else stem + "Table"
        table = by_name.get(table_name)
        entry = by_name.get(table_name[:-5] + "Entry") if table_name.endswith("Table") else None
        if entry is None:
            entry = by_name.get(stem + "Entry")

        if table is None or entry is None:
            # Vendor naming is not perfectly regular: the DHCP excluded-IP
            # editor is `...ExcludedIpTableRowEditor` while its table is
            # `...ExcludedTable`. Fall back to structure -- the row-editor
            # group is the sibling immediately after its table, so the table
            # is at the preceding sub-identifier.
            head, _, last = action[0]["oid"].rpartition(".")      # strip Action subid
            group_oid = head
            parent, _, idx = group_oid.rpartition(".")
            if idx.isdigit() and int(idx) > 1:
                sibling = f"{parent}.{int(idx) - 1}"
                by_oid = {v["oid"]: v for v in defs.values() if v["oid"]}
                cand = by_oid.get(sibling)
                if cand is not None and cand["syntax"].startswith("SEQUENCE OF"):
                    table = cand
                    entry = by_oid.get(f"{sibling}.1")
                    table_name = cand["name"]

        if table is None or entry is None or not table["oid"]:
            print(f"SKIP {stem}: no table/entry found", file=sys.stderr)
            continue

        # per-row Action column: the column of `entry` whose syntax is the
        # row-editor TC (same '100' convention proven in the lab capture).
        row_action = None
        for v in defs.values():
            if (v["kind"] == "OBJECT-TYPE" and v["oid"].startswith(entry["oid"] + ".")
                    and v["oid"].count(".") == entry["oid"].count(".") + 1
                    and "RowEditorState" in v["syntax"]):
                row_action = v
        if row_action is None:
            continue

        # Index component names are shortened against the table's own prefix
        # so they read as fields (`name`, `sourceIP`) rather than as the full
        # module-qualified object names.
        base = table_name[:-5] if table_name.endswith("Table") else stem
        idx_names, idx_kinds = [], []
        for comp in [c.strip() for c in entry["index"].split(",") if c.strip()]:
            col = by_name.get(comp)
            short = comp[len(base):] if comp.startswith(base) else comp
            short = (short[0].lower() + short[1:]) if short else comp
            idx_names.append(short)
            idx_kinds.append(index_kind(col["syntax"] if col else "", tcs))

        field_lines = []
        for f in sorted(fields, key=lambda x: int(x["oid"].split(".")[-1])):
            logical = f["name"].split("RowEditor", 1)[1]
            logical = logical[0].lower() + logical[1:]
            field_lines.append(
                f'        {logical!r}: EditorField("{f["oid"]}.0", '
                f'"{type_char(f["syntax"], tcs)}"),   # {f["syntax"][:44]}')

        var = _var_name(stem)
        out.append(f'''
{var} = RowEditorSpec(
    name="{stem}",
    action_oid="{action[0]["oid"]}.0",
    table_oid="{table["oid"]}",
    row_action_column_oid="{row_action["oid"]}",
    index_spec=IndexSpec(names={idx_names!r}, kinds={idx_kinds!r}),
    fields={{
{chr(10).join(field_lines)}
    }},
)''')
        generated += 1

    print('"""Row-editor specs generated from the vendor MIBs.')
    print()
    print("DO NOT EDIT BY HAND -- regenerate with:")
    print("    python3 tools/gen_row_editor_specs.py > src/actelis_mediation/rowedit/specs.py")
    print()
    print(f"{generated} tables in ML540M-MIB.7z use the VTSSRowEditorState mechanism")
    print("proven end-to-end against the lab unit on 2026-09-18")
    print("(docs/lab-results/ml540m-row-editor-20260918.txt). Only that one table --")
    print("SNMP_CONFIG_COMMUNITY_TABLE -- has been exercised on real hardware; the")
    print("rest are mechanically derived and carry the same protocol, but should be")
    print("treated as unproven per-table until walked against a device.")
    print('"""')
    print("from __future__ import annotations")
    print()
    print("from ..snmp.oid import IndexSpec")
    print("from . import EditorField, RowEditorSpec")
    print("\n".join(out))
    print()
    print("ALL_SPECS = {s.name: s for s in [")
    for stem in sorted(editors):
        v = _var_name(stem)
        if any(f"\n{v} = RowEditorSpec(" in o for o in out):
            print(f"    {v},")
    print("]}")
    print(f"\n# generated: {generated} specs", file=sys.stderr)
    return 0


def _var_name(stem: str) -> str:
    s = stem[len("ml540m"):] if stem.startswith("ml540m") else stem
    out = []
    for i, ch in enumerate(s):
        if ch.isupper() and i and not s[i - 1].isupper():
            out.append("_")
        out.append(ch.upper())
    return "".join(out)


if __name__ == "__main__":
    raise SystemExit(main())
