"""SNMP transport backend interface.

The original prototype shelled out to the net-snmp CLI tools, for good
reasons that are preserved here: those exact invocations are already proven
end-to-end against the lab ML540M, they need no MIB compilation, and they add
no Python dependency that is untested against these devices.

What is added is an *interface* boundary. Everything above this module works
against ``SnmpBackend``, so:

  * tests use ``FakeBackend`` with no subprocess and no network;
  * a pysnmp (or NSP-SDK-native) backend can be dropped in later without
    touching the pollers -- which is the actual porting job when NSP access
    lands, since the NSP Communicator will supply its own SNMP stack;
  * the net-snmp behaviour that is proven stays proven.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class SnmpTarget:
    host: str
    ro_community: str
    rw_community: str | None = None
    port: int = 161
    timeout_s: float = 3.0
    retries: int = 2
    # Upper bound on a whole walk, not a single request. The original had a
    # hardcoded 30s subprocess timeout, which silently truncates a 96-bin x
    # N-port HDSL2-SHDSL interval walk on a slow link.
    walk_timeout_s: float = 300.0
    max_repetitions: int = 25
    # GETBULK is much faster on large tables, but embedded agents vary in how
    # well they implement it. Set false to force plain GETNEXT walks when
    # comparing behaviour against a specific device.
    use_bulkwalk: bool = True
    def write_community(self) -> str:
        if not self.rw_community:
            raise ValueError(f"{self.host}: no write community configured; cannot SET")
        return self.rw_community


@dataclass(frozen=True)
class VarBind:
    oid: str
    value: str
    type_name: str = ""


class SnmpBackend(Protocol):
    def get(self, target: SnmpTarget, oids: list[str]) -> dict[str, VarBind]: ...
    def walk(self, target: SnmpTarget, base_oid: str) -> dict[str, VarBind]: ...
    def set(self, target: SnmpTarget, binds: list[tuple[str, str, str]]) -> dict[str, VarBind]: ...


@dataclass
class FakeBackend:
    """In-memory backend for tests. Holds a flat {oid: value} device image."""
    values: dict[str, str] = field(default_factory=dict)
    unimplemented: set[str] = field(default_factory=set)
    sets: list[tuple[str, str, str]] = field(default_factory=list)
    fail_next_set: Exception | None = None

    def get(self, target: SnmpTarget, oids: list[str]) -> dict[str, VarBind]:
        from .errors import SnmpNoSuchObject
        from .oid import is_within, normalize
        out: dict[str, VarBind] = {}
        missing = []
        for oid in oids:
            o = normalize(oid)
            if any(is_within(o, u) for u in self.unimplemented):
                missing.append(o)
                continue
            if o in self.values:
                out[o] = VarBind(o, self.values[o])
            else:
                missing.append(o)
        if missing and not out:
            raise SnmpNoSuchObject(f"no such object: {', '.join(missing)}")
        return out

    def walk(self, target: SnmpTarget, base_oid: str) -> dict[str, VarBind]:
        from .errors import SnmpNoSuchObject
        from .oid import is_within, normalize
        base = normalize(base_oid)
        if any(is_within(base, u) or is_within(u, base) and u == base
               for u in self.unimplemented):
            raise SnmpNoSuchObject(f"No Such Object available on this agent at {base}")
        return {o: VarBind(o, v) for o, v in self.values.items() if is_within(o, base)}

    def set(self, target: SnmpTarget, binds: list[tuple[str, str, str]]) -> dict[str, VarBind]:
        if self.fail_next_set is not None:
            exc, self.fail_next_set = self.fail_next_set, None
            raise exc
        from .oid import normalize
        out = {}
        for oid, _type_char, value in binds:
            o = normalize(oid)
            self.sets.append((o, _type_char, value))
            self.values[o] = value
            out[o] = VarBind(o, value)
        return out
