"""Actelis -> Nokia NSP mediation: MIB analysis, and a standalone Communicator
prototype that becomes the data-fetch layer of the real NSP Communicator.

Layout mirrors the eventual NSP split deliberately:
    snmp/     transport (replaceable: net-snmp CLI today, NSP SDK later)
    model/    device-independent semantics -- units, alarm state, table indices
    poll/     per-device-type collection
    traps/    asynchronous fault path
    store/    local persistence (replaced by NSP's Device Model at Phase 1)
"""
__version__ = "0.2.0"
