"""
OID and table-index handling.

This module exists because of the single most consequential defect found in
the original prototype: every table poller reduced a row's index to
``oid.rsplit(".", 1)[-1]`` -- the *last* sub-identifier only.

That is correct only for single-component indices. It is wrong for:

  * ``ml540mPerfMonitorStatusStatisticsDmEntry``
    INDEX { ...DmIntervalId, ...DmEntryId }                    -- 2 components
  * ``hdsl2Shdsl15MinIntervalEntry``
    INDEX { ifIndex, hdsl2ShdslInvIndex, hdsl2ShdslEndpointSide,
            hdsl2ShdslEndpointWirePair, hdsl2Shdsl15MinIntervalNumber }
                                                                -- 5 components
  * ``ml540mSnmpConfigCommunityEntry`` -- a length-prefixed OCTET STRING
    index followed by an IpAddress and a prefix length.

Consequences in the original: the per-row ``DmUnit`` (us(0)/ns(1)) was keyed
on ``DmEntryId`` alone, so a unit read from one measurement interval could be
applied to delay values from another -- a silent 1000x error in exactly the
field the project's own notes warned must not be guessed. And because no
index was stored at all, archived PM bins carried no port, endpoint, wire
pair or bin number, making the archive unusable for its stated purpose.

Everything here is pure functions over OID strings: no I/O, fully testable.
"""
from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Iterator, Sequence


def normalize(oid: str) -> str:
    """Strip a leading dot and surrounding whitespace. ``.1.3.6`` -> ``1.3.6``."""
    return oid.strip().lstrip(".")


def as_tuple(oid: str) -> tuple[int, ...]:
    return tuple(int(p) for p in normalize(oid).split(".") if p != "")


def is_within(oid: str, base: str) -> bool:
    """True if ``oid`` is at or below ``base`` in the OID tree.

    Compares sub-identifier by sub-identifier, so ``1.3.6.1.4.1.5468.1002``
    is correctly *not* considered within ``1.3.6.1.4.1.5468.100`` -- a plain
    string ``startswith`` gets that wrong.
    """
    o, b = as_tuple(oid), as_tuple(base)
    return len(o) >= len(b) and o[: len(b)] == b


def index_suffix(oid: str, column_oid: str) -> str:
    """Return the index portion of ``oid`` relative to its column OID.

    >>> index_suffix("1.3.6.1.2.1.10.48.1.6.1.2.101.1.1.1.5", "1.3.6.1.2.1.10.48.1.6.1.2")
    '101.1.1.1.5'
    """
    if not is_within(oid, column_oid):
        raise ValueError(f"{oid} is not under column {column_oid}")
    o, c = as_tuple(oid), as_tuple(column_oid)
    return ".".join(str(p) for p in o[len(c):])


def split_index(suffix: str) -> tuple[int, ...]:
    return tuple(int(p) for p in str(suffix).split(".") if p != "")


# ---------------------------------------------------------------------------
# Index decoding
#
# SMIv2 encodes an INDEX clause into OID sub-identifiers by type:
#   Integer32/Unsigned32/InterfaceIndex/enum -> one sub-identifier
#   IpAddress                                -> four sub-identifiers
#   OCTET STRING / DisplayString (variable)  -> length byte, then one
#                                               sub-identifier per octet
#   OCTET STRING (fixed SIZE(n))             -> n sub-identifiers, no length
# ---------------------------------------------------------------------------

INTEGER = "integer"
IPADDRESS = "ipaddress"
STRING = "string"          # variable length, length-prefixed
FIXED_STRING = "string%d"  # produced by fixed_string(n)


def fixed_string(n: int) -> str:
    return f"fixed-string:{n}"


@dataclass(frozen=True)
class IndexSpec:
    """The INDEX clause of one table, as a list of index kinds.

    ``names`` is parallel to ``kinds`` and gives each component a label, so a
    decoded row carries meaningful identity (``ifIndex=101``, ``wirePair=1``)
    instead of an anonymous tuple.
    """
    names: Sequence[str]
    kinds: Sequence[str]

    def __post_init__(self) -> None:
        if len(self.names) != len(self.kinds):
            raise ValueError("names and kinds must be the same length")

    def decode(self, suffix: str) -> dict[str, object]:
        parts = list(split_index(suffix))
        out: dict[str, object] = {}
        pos = 0
        for name, kind in zip(self.names, self.kinds, strict=True):
            if kind == INTEGER:
                if pos >= len(parts):
                    raise ValueError(f"index {suffix!r}: ran out of sub-ids at {name!r}")
                out[name] = parts[pos]
                pos += 1
            elif kind == IPADDRESS:
                if pos + 4 > len(parts):
                    raise ValueError(f"index {suffix!r}: truncated IpAddress at {name!r}")
                out[name] = ".".join(str(p) for p in parts[pos: pos + 4])
                pos += 4
            elif kind == STRING:
                if pos >= len(parts):
                    raise ValueError(f"index {suffix!r}: truncated string at {name!r}")
                length = parts[pos]
                pos += 1
                if pos + length > len(parts):
                    raise ValueError(
                        f"index {suffix!r}: string {name!r} claims length {length} "
                        f"but only {len(parts) - pos} sub-ids remain")
                out[name] = "".join(chr(p) for p in parts[pos: pos + length])
                pos += length
            elif kind.startswith("fixed-string:"):
                n = int(kind.split(":", 1)[1])
                if pos + n > len(parts):
                    raise ValueError(f"index {suffix!r}: truncated fixed string at {name!r}")
                out[name] = "".join(chr(p) for p in parts[pos: pos + n])
                pos += n
            else:
                raise ValueError(f"unknown index kind {kind!r}")
        if pos != len(parts):
            raise ValueError(
                f"index {suffix!r} has {len(parts) - pos} trailing sub-identifier(s) "
                f"not consumed by spec {list(self.names)} -- the INDEX clause in the "
                f"MIB probably has more components than this spec declares")
        return out

    def encode(self, **values: object) -> str:
        parts: list[str] = []
        for name, kind in zip(self.names, self.kinds, strict=True):
            v = values[name]
            if kind == INTEGER:
                parts.append(str(int(v)))  # type: ignore[arg-type]
            elif kind == IPADDRESS:
                parts.extend(str(o) for o in str(v).split("."))
            elif kind == STRING:
                s = str(v)
                parts.append(str(len(s)))
                parts.extend(str(ord(c)) for c in s)
            elif kind.startswith("fixed-string:"):
                parts.extend(str(ord(c)) for c in str(v))
            else:
                raise ValueError(f"unknown index kind {kind!r}")
        return ".".join(parts)


@dataclass(frozen=True)
class TableRow:
    """One decoded table row: its raw index suffix plus the decoded fields."""
    suffix: str
    index: dict[str, object]
    values: dict[str, str]

    def key(self) -> tuple:
        return tuple(self.index[n] for n in sorted(self.index))


def rows_from_columns(
    column_walks: dict[str, dict[str, str]],
    column_oids: dict[str, str],
    spec: IndexSpec,
    *,
    strict: bool = False,
) -> list[TableRow]:
    """Join several single-column walks into whole rows, keyed by full index.

    ``column_walks`` maps a logical column name to that column's walk result
    ({full_oid: value}); ``column_oids`` maps the same names to the column's
    base OID. Rows are assembled on the *complete* index suffix, which is what
    makes multi-component indices correct.

    With ``strict=False`` (default) a row whose index cannot be decoded is
    skipped rather than aborting the whole poll -- a device that returns an
    unexpected row should degrade one row, not the collection cycle. Set
    ``strict=True`` in tests to surface spec/MIB mismatches loudly.
    """
    by_suffix: dict[str, dict[str, str]] = {}
    for col_name, walk in column_walks.items():
        base = column_oids[col_name]
        for oid, value in walk.items():
            try:
                suffix = index_suffix(oid, base)
            except ValueError:
                if strict:
                    raise
                continue
            by_suffix.setdefault(suffix, {})[col_name] = value

    rows: list[TableRow] = []
    for suffix in sorted(by_suffix, key=split_index):
        try:
            decoded = spec.decode(suffix)
        except ValueError:
            if strict:
                raise
            continue
        rows.append(TableRow(suffix=suffix, index=decoded, values=by_suffix[suffix]))
    return rows


def iter_subtree(walk: dict[str, str], base: str) -> Iterator[tuple[str, str]]:
    for oid, value in walk.items():
        if is_within(oid, base):
            yield oid, value
