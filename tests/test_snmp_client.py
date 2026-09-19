"""net-snmp output parsing and error classification."""
import pytest

from actelis_mediation.snmp.errors import (SnmpAuthorization, SnmpBadValue,
                                           SnmpTimeout)
from actelis_mediation.snmp.netsnmp import NetSnmpBackend


def parse(text):
    return NetSnmpBackend._parse(text)


def test_parses_lines_lifted_from_the_real_lab_capture():
    """Verbatim from docs/lab-results/ml540m-20260918.txt."""
    found, missing = parse(
        ".1.3.6.1.4.1.5468.100.35.1.2.1.1.2.1000001 = INTEGER: 2\n"
        ".1.3.6.1.4.1.5468.100.35.1.2.1.1.3.1000001 = Gauge32: 0\n"
        ".1.3.6.1.4.1.5468.100.35.1.2.1.1.6.1000010 = Gauge32: 32768\n")
    assert not missing
    assert found["1.3.6.1.4.1.5468.100.35.1.2.1.1.2.1000001"].value == "2"
    assert found["1.3.6.1.4.1.5468.100.35.1.2.1.1.2.1000001"].type_name == "INTEGER"
    assert found["1.3.6.1.4.1.5468.100.35.1.2.1.1.6.1000010"].value == "32768"


def test_missing_oids_are_separated_from_good_ones():
    """The original discarded every value in the response if any one OID was
    missing."""
    found, missing = parse(
        ".1.3.6.1.4.1.5468.100.1.1.1.0 = STRING: ML540M\n"
        ".1.3.6.1.4.1.5468.100.1.1.5.0 = No Such Instance currently exists at this OID\n")
    assert found["1.3.6.1.4.1.5468.100.1.1.1.0"].value == "ML540M"
    assert missing == ["1.3.6.1.4.1.5468.100.1.1.5.0"]


def test_no_such_object_from_the_real_lldp_capture():
    found, missing = parse(
        ".1.3.6.1.4.1.5468.100.34.1.3.2 = No Such Object available on this agent at this OID\n")
    assert not found and missing == ["1.3.6.1.4.1.5468.100.34.1.3.2"]


def test_multiline_string_values_are_not_dropped():
    found, _ = parse('.1.3.6.1.2.1.1.1.0 = STRING: Actelis ML624\nHardware rev B\n')
    assert found["1.3.6.1.2.1.1.1.0"].value == "Actelis ML624\nHardware rev B"


class _Backend(NetSnmpBackend):
    """Stubs out the subprocess so error classification can be tested."""
    def __init__(self, output):
        super().__init__()
        self._output = output
    def _run(self, args, *, timeout_s, env=None, secrets=None):
        from actelis_mediation.snmp.netsnmp import (_AUTH_RE, _BADVAL_RE, _TIMEOUT_RE)
        if _TIMEOUT_RE.search(self._output):
            raise SnmpTimeout(self._output)
        if _AUTH_RE.search(self._output):
            raise SnmpAuthorization(self._output)
        if _BADVAL_RE.search(self._output):
            raise SnmpBadValue(self._output)
        return self._output


def test_deterministic_failures_are_not_retried():
    """Retrying a wrongType or an authorizationError is pure waste, and
    retrying auth failures can trip lockouts on AAA-backed devices."""
    from actelis_mediation.snmp.backend import SnmpTarget
    t = SnmpTarget(host="h", ro_community="c", rw_community="c", retries=3)

    calls = {"n": 0}
    be = _Backend("wrongType (The set datatype does not match)")
    orig = be._run
    def counted(*a, **k):
        calls["n"] += 1
        return orig(*a, **k)
    be._run = counted
    with pytest.raises(SnmpBadValue):
        be.set(t, [("1.3.6.1.4.1.5468.100.36.1.2.3.2.0", "s", "0.0.0.0")])
    assert calls["n"] == 1          # no retries


def test_wrong_type_is_what_the_original_row_editor_would_have_hit():
    """Staging an IpAddress column as net-snmp type 's' produces exactly this."""
    from actelis_mediation.snmp.backend import SnmpTarget
    be = _Backend("Reason: wrongType (The set datatype does not match the data type "
                  "the agent expects)")
    with pytest.raises(SnmpBadValue, match="wrongType"):
        be.set(SnmpTarget(host="h", ro_community="c", rw_community="c"),
               [("1.3.6.1.4.1.5468.100.36.1.2.3.2.0", "s", "0.0.0.0")])
