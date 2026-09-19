"""VTSSRowEditorState reserve -> stage -> commit -> delete protocol.

The protocol itself is taken verbatim from the ``VTSSRowEditorState``
TEXTUAL-CONVENTION in ``ML540M-TC.mib`` and was proven end-to-end against the
lab ML540M on 2026-09-18 (docs/lab-results/ml540m-row-editor-20260918.txt).
That proof is solid and is kept as-is.

Two defects in the original helper are fixed here:

1. **Field types.** ``RowEditorSession.stage()`` sent every field as net-snmp
   type ``s`` (OCTET STRING). The one spec the module shipped -- the SNMP
   community table -- has an ``IpAddress`` column and an integer prefix
   length, and the lab script that proved the protocol used ``s``, ``a`` and
   ``i`` respectively. So the shipped spec could not actually be used with
   the shipped convenience method: the agent answers ``wrongType``. Fields
   now carry their net-snmp type char, taken from the MIB SYNTAX.

2. **Stale reservations.** The TC's state machine has no timeout: IDLE ->
   RESERVED happens on a MANAGER-ID write, and *only* CLEAR or COMMIT
   returns it to IDLE. If a Communicator is killed between reserve and
   commit, the editor stays reserved forever and every subsequent row
   creation on that table -- by anyone, including the CLI and any other NMS
   -- fails. The original raised "clear it by hand before retrying". Since
   the TC places no restriction on who may write CLEAR, recovery is
   available programmatically; ``reclaim_stale`` implements it, gated behind
   an explicit opt-in because it does stamp on whoever holds the editor.

This is a device-wide mutual-exclusion primitive. That has a direct bearing
on NSP deployment topology (NSP is normally clustered): two Communicator
instances writing the same switch will contend for it. See
docs/adr/0004-row-editor-concurrency.md.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from collections.abc import Mapping

from ..snmp.backend import SnmpBackend, SnmpTarget
from ..snmp.errors import SnmpError

logger = logging.getLogger(__name__)

IDLE = 0
CLEAR_ACTION = 1
COMMIT_ACTION = 2
MIN_MANAGER_ID = 256
MAX_MANAGER_ID = 4294967295


class RowEditorError(SnmpError):
    pass


class RowEditorBusy(RowEditorError):
    """The editor is reserved by another manager ID."""
    def __init__(self, message: str, holder: int | None = None):
        super().__init__(message)
        self.holder = holder


@dataclass(frozen=True)
class EditorField:
    """One row-editor field: its scalar OID and net-snmp type char.

    ``type_char`` follows net-snmp convention and must match the MIB SYNTAX:
    i=INTEGER, u=Gauge32/Unsigned32, s=OCTET STRING/DisplayString,
    a=IpAddress, x=hex string, o=OID, d=decimal string, b=bits.
    """
    oid: str
    type_char: str


@dataclass(frozen=True)
class RowEditorSpec:
    name: str
    action_oid: str                      # row-editor Action scalar (needs .0)
    fields: Mapping[str, EditorField]
    table_oid: str                       # the real table rows land in
    row_action_column_oid: str           # per-row Action column (delete)
    index_spec: object | None = None     # snmp.oid.IndexSpec for the table

    def row_action_oid(self, index_suffix: str) -> str:
        return f"{self.row_action_column_oid}.{index_suffix}"


@dataclass
class RowEditorSession:
    """Context manager over reserve -> stage -> commit.

        with RowEditorSession(backend, target, SNMP_COMMUNITY_EDITOR) as row:
            row.stage(name="nsp-ro", srcIp="10.0.0.0", prefix=8)
            row.commit()

    On any exception inside the block the reservation is cleared, so a failed
    stage does not leave the table locked for every other manager.
    """
    backend: SnmpBackend
    target: SnmpTarget
    spec: RowEditorSpec
    manager_id: int = 999001
    reclaim_stale: bool = False
    _reserved: bool = field(default=False, init=False)
    _committed: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        if not (MIN_MANAGER_ID <= self.manager_id <= MAX_MANAGER_ID):
            raise RowEditorError(
                f"manager_id must be in {MIN_MANAGER_ID}..{MAX_MANAGER_ID} "
                f"(0-255 are reserved by the protocol); got {self.manager_id}")

    # -- state --------------------------------------------------------------

    def read_state(self) -> int:
        vb = self.backend.get(self.target, [self.spec.action_oid])
        raw = next(iter(vb.values())).value.strip()
        if ":" in raw:
            raw = raw.split(":", 1)[1].strip()
        try:
            return int(raw)
        except ValueError as exc:
            raise RowEditorError(
                f"{self.spec.name}: row-editor state is not numeric: {raw!r}") from exc

    # -- lifecycle ----------------------------------------------------------

    def __enter__(self) -> RowEditorSession:
        self.reserve()
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        if self._reserved and not self._committed:
            try:
                self.clear()
            except Exception:                     # noqa: BLE001 - best effort
                logger.exception("%s: failed to clear reservation on %s; the "
                                 "row editor may be left locked",
                                 self.spec.name, self.target.host)
        return False

    def reserve(self) -> None:
        state = self.read_state()
        if state != IDLE:
            if not self.reclaim_stale:
                raise RowEditorBusy(
                    f"{self.spec.name} on {self.target.host}: row editor held by "
                    f"manager {state}. VTSSRowEditorState has no reservation "
                    f"timeout, so this will not self-clear. Re-run with "
                    f"reclaim_stale=True to force-clear it, after confirming no "
                    f"other manager is mid-edit.", holder=state)
            logger.warning("%s on %s: force-clearing reservation held by manager %d",
                           self.spec.name, self.target.host, state)
            self.backend.set(self.target, [(self.spec.action_oid, "u", str(CLEAR_ACTION))])
            if self.read_state() != IDLE:
                raise RowEditorBusy(f"{self.spec.name}: force-clear did not return "
                                    f"the editor to idle", holder=state)

        self.backend.set(self.target, [(self.spec.action_oid, "u", str(self.manager_id))])
        got = self.read_state()
        if got != self.manager_id:
            raise RowEditorBusy(
                f"{self.spec.name}: reservation not confirmed (wrote "
                f"{self.manager_id}, read back {got}) -- another manager most "
                f"likely won the race", holder=got)
        self._reserved = True

    def stage(self, **values: object) -> None:
        """Stage field values by logical name, using each field's MIB type."""
        binds: list[tuple[str, str, str]] = []
        for name, value in values.items():
            fld = self.spec.fields.get(name)
            if fld is None:
                raise RowEditorError(
                    f"{self.spec.name}: unknown field {name!r}; expected one of "
                    f"{sorted(self.spec.fields)}")
            binds.append((fld.oid, fld.type_char, str(value)))
        if not binds:
            return
        self.backend.set(self.target, binds)

    def commit(self) -> None:
        if not self._reserved:
            raise RowEditorError(f"{self.spec.name}: commit() before reserve()")
        self.backend.set(self.target, [(self.spec.action_oid, "u", str(COMMIT_ACTION))])
        state = self.read_state()
        if state != IDLE:
            raise RowEditorError(
                f"{self.spec.name}: commit left the editor in state {state} rather "
                f"than idle; the row was probably rejected. Check the staged values "
                f"against the table's constraints.")
        self._committed = True

    def clear(self) -> None:
        self.backend.set(self.target, [(self.spec.action_oid, "u", str(CLEAR_ACTION))])
        self._reserved = False


def delete_row(backend: SnmpBackend, target: SnmpTarget, spec: RowEditorSpec,
               index_suffix: str) -> None:
    """Delete a row by writing 1 to that row's own Action column.

    This is the 'column in a dynamic table' meaning of VTSSRowEditorState,
    distinct from the row-editor object used above -- per the TC: "If the
    value 1 is written to this object the given row will be deleted."
    """
    backend.set(target, [(spec.row_action_oid(index_suffix), "u", str(CLEAR_ACTION))])
