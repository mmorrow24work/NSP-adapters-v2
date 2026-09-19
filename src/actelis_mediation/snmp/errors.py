"""SNMP error taxonomy.

Split finer than the original prototype's three classes, because the poller
needs to make different decisions for different failures:

  * ``SnmpTimeout``        -> device unreachable / wrong community: retry with
                              backoff, then mark the device unreachable.
  * ``SnmpNoSuchObject``   -> the agent does not implement this OID (the
                              ML540M firmware 00.00.16 LLDP case): do NOT
                              retry, record a capability gap once.
  * ``SnmpAuthorization``  -> community rejected for a SET: never retry, this
                              is a configuration error and retrying can lock
                              accounts on AAA-backed devices.
  * ``SnmpBadValue``       -> wrongType/badValue/inconsistentValue from a SET.
                              The original sent every row-editor field as a
                              string, which produces exactly this.
"""
from __future__ import annotations


class SnmpError(Exception):
    """Base class for anything that is not a clean SNMP response."""


class SnmpTimeout(SnmpError):
    """No response. Usually unreachable, or the wrong community string."""


class SnmpNoSuchObject(SnmpError):
    """noSuchObject / noSuchInstance: the agent does not implement this OID.

    Distinguishing this from a timeout matters: it is deterministic, so
    retrying is pure waste, and it is the signature of a firmware capability
    gap rather than a network fault.
    """


class SnmpAuthorization(SnmpError):
    """The agent refused the request (no access / wrong community)."""


class SnmpBadValue(SnmpError):
    """wrongType, badValue, wrongLength, inconsistentValue on a SET."""


class SnmpToolMissing(SnmpError):
    """The net-snmp CLI tools are not installed or not on PATH."""
