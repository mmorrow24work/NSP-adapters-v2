"""Command-line construction for the net-snmp backend.

This file exists because of a bug that reached real hardware: the first live
`poll-once` against the lab ML540M failed on every walk with a net-snmp USAGE
banner, because the max-repetitions option was emitted as two argv tokens
("-Cr", "25") instead of one ("-Cr25").

Nothing in the rest of the suite could have caught it. `FakeBackend` answers
at the Python level and never builds a command line, so the argv was
completely untested — a gap in the test strategy, not just a typo. These
tests close it by asserting the argv without invoking net-snmp.
"""
from unittest import mock

import pytest

from actelis_mediation.snmp.backend import SnmpTarget
from actelis_mediation.snmp.errors import SnmpInvocationError
from actelis_mediation.snmp.netsnmp import NetSnmpBackend

OID = "1.3.6.1.4.1.5468.100.1.2.2.1.1.3"
AUTH = ["-c", "community"]


def args_for(target, *, bulkwalk_available=True):
    with mock.patch("actelis_mediation.snmp.netsnmp.shutil.which",
                    return_value="/usr/bin/snmpbulkwalk" if bulkwalk_available else None):
        return NetSnmpBackend.walk_args(target, OID, AUTH)


def test_max_repetitions_is_one_concatenated_token():
    """net-snmp takes -C sub-options joined to their value.

    Passing "-Cr" and "25" separately makes 25 look like a positional
    argument; net-snmp reads it as the agent address and aborts with USAGE.
    """
    args = args_for(SnmpTarget(host="h", ro_community="c", max_repetitions=25))
    assert "-Cr25" in args
    assert "-Cr" not in args, "must not appear as a bare token"
    assert "25" not in args, "the value must not be a standalone argv token"


def test_bulkwalk_is_used_when_available_and_enabled():
    args = args_for(SnmpTarget(host="h", ro_community="c"))
    assert args[0] == "snmpbulkwalk"


def test_bulkwalk_can_be_disabled_per_device():
    """Escape hatch for agents that implement GETBULK poorly."""
    args = args_for(SnmpTarget(host="h", ro_community="c", use_bulkwalk=False))
    assert args[0] == "snmpwalk"
    assert not any(a.startswith("-Cr") for a in args), \
        "-Cr is a bulkwalk option and is invalid for snmpwalk"


def test_falls_back_to_snmpwalk_when_bulkwalk_is_not_installed():
    args = args_for(SnmpTarget(host="h", ro_community="c"), bulkwalk_available=False)
    assert args[0] == "snmpwalk"
    assert not any(a.startswith("-Cr") for a in args)


def test_argv_shape_is_stable():
    t = SnmpTarget(host="192.168.1.99", ro_community="c", port=161, timeout_s=3.0)
    assert args_for(t) == [
        "snmpbulkwalk", "-v2c", "-c", "community", "-r", "0", "-t", "3.0",
        "-On", "-Cr25", "192.168.1.99:161", OID]


def test_agent_and_oid_are_the_last_two_arguments():
    """Anything that shifts these breaks the invocation in exactly the way
    the live run did."""
    for target in (SnmpTarget(host="h", ro_community="c"),
                   SnmpTarget(host="h", ro_community="c", use_bulkwalk=False),
                   SnmpTarget(host="h", ro_community="c", max_repetitions=1)):
        args = args_for(target)
        assert args[-1] == OID
        assert args[-2] == "h:161"


def test_a_usage_banner_is_a_bug_in_this_code_not_a_device_fault():
    """Classified as SnmpInvocationError and never retried -- retrying a
    malformed command line just delays the real diagnosis behind N backoffs,
    which is what happened on the first live run."""
    backend = NetSnmpBackend()
    calls = {"n": 0}

    def fake_run(args, **kwargs):
        calls["n"] += 1
        return mock.Mock(returncode=1, stdout="", stderr=(
            "USAGE: snmpbulkwalk [OPTIONS] AGENT [OID]\n\n  Version:  5.9.4.pre2\n"))

    with mock.patch("actelis_mediation.snmp.netsnmp.subprocess.run", fake_run), \
            pytest.raises(SnmpInvocationError, match="rejected the command line"):
        backend.walk(SnmpTarget(host="h", ro_community="c", retries=3), OID)
    assert calls["n"] == 1, "a usage error must not be retried"
