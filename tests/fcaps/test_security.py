"""FCAPS · Security — credentials, transport, and what the repo leaks.

The original analysis concluded these devices are SNMPv2c-only and that
cleartext communities are therefore an unavoidable constraint to be mitigated
at the network layer. The MIBs say otherwise for the switch, and these
assertions pin that down so the posture cannot quietly regress.
"""
from __future__ import annotations

import logging
import re
from pathlib import Path

import pytest

from actelis_mediation.snmp.errors import SnmpAuthorization, SnmpBadValue
from actelis_mediation.snmp.redact import REDACTED, redact_args, redact_text

pytestmark = pytest.mark.fcaps("security")

REPO = Path(__file__).resolve().parents[2]
DEFAULT_COMMUNITIES = ("public", "private")


# --- what the repository itself discloses ----------------------------------

def test_no_default_communities_committed_in_config_or_source():
    """The original shipped devices.yaml with public/private inline.

    Historical lab captures under docs/lab-results/ legitimately record what
    was observed and are excluded; config and source are not.
    """
    pattern = re.compile(
        r"""(ro|rw|read|write)_community\s*[:=]\s*["']?(public|private)\b""",
        re.IGNORECASE)
    offenders = []
    for path in list((REPO / "etc").rglob("*")) + list((REPO / "src").rglob("*.py")):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for m in pattern.finditer(text):
            offenders.append(f"{path.relative_to(REPO)}: {m.group(0)}")
    assert offenders == [], f"default SNMP communities committed: {offenders}"


def test_the_live_config_is_not_tracked():
    """etc/devices.yaml holds real hosts; only the .example is committed."""
    gitignore = (REPO / ".gitignore").read_text()
    assert "etc/devices.yaml" in gitignore


def test_example_config_resolves_credentials_from_the_environment():
    text = (REPO / "etc" / "devices.yaml.example").read_text()
    assert "ro_community_env" in text
    assert not re.search(r"ro_community\s*:\s*\w", text)


# --- credential handling at runtime ----------------------------------------

def test_missing_credential_environment_variable_fails_loudly(tmp_path, monkeypatch):
    from actelis_mediation.config import AppConfig, ConfigError
    cfg = tmp_path / "d.yaml"
    cfg.write_text(
        "devices:\n"
        "  - name: sw\n    device_type: switch\n    host: 192.0.2.10\n"
        "    ro_community_env: DEFINITELY_NOT_SET_XYZ\n"
        "storage:\n  sqlite_path: x.db\n")
    monkeypatch.delenv("DEFINITELY_NOT_SET_XYZ", raising=False)
    with pytest.raises(ConfigError, match="DEFINITELY_NOT_SET_XYZ"):
        AppConfig.load(cfg)


def test_credentials_are_redacted_from_command_lines():
    args = ["snmpget", "-v2c", "-c", "s3cr3t-community", "-Ovq", "host", "1.3.6"]
    out = redact_args(args)
    assert "s3cr3t-community" not in out
    assert REDACTED in out
    assert "snmpget" in out and "1.3.6" in out, "redaction must stay debuggable"


def test_credentials_are_redacted_from_tool_output():
    text = "Error in packet: snmpset -c s3cr3t 192.0.2.10 failed"
    assert "s3cr3t" not in redact_text(text, secrets=["s3cr3t"])
    assert "s3cr3t" not in redact_text("timeout running -c s3cr3t")


def test_community_never_reaches_an_exception_message(monkeypatch):
    """Regression, exercising the real error path.

    The original raised SnmpTimeout with ' '.join(args). Even after that was
    fixed, subprocess.TimeoutExpired stringifies its own argv -- so chaining
    it with `raise ... from exc` still leaked the community into every
    timeout traceback. Caught by writing this test.
    """
    import subprocess

    from actelis_mediation.snmp import netsnmp as ns
    from actelis_mediation.snmp.backend import SnmpTarget
    from actelis_mediation.snmp.errors import SnmpTimeout

    secret = "s3cr3t-community"

    def fake_run(args, **kwargs):
        raise subprocess.TimeoutExpired(args, kwargs.get("timeout", 1))

    monkeypatch.setattr(ns.subprocess, "run", fake_run)
    target = SnmpTarget(host="192.0.2.10", ro_community=secret, retries=0)

    with pytest.raises(SnmpTimeout) as exc:
        ns.NetSnmpBackend().get(target, ["1.3.6.1.2.1.1.1.0"])

    assert secret not in str(exc.value)
    assert REDACTED in str(exc.value)
    # and nothing in the chained context either
    chained = exc.value.__cause__ or exc.value.__context__
    assert chained is None or secret not in str(chained)


def test_credentials_are_not_written_to_logs(caplog):
    from actelis_mediation.snmp.backend import SnmpTarget
    from actelis_mediation.snmp.netsnmp import NetSnmpBackend
    from actelis_mediation.snmp.errors import SnmpTimeout

    secret = "s3cr3t-community"
    target = SnmpTarget(host="192.0.2.10", ro_community=secret, retries=1,
                        timeout_s=0.01)

    class _Failing(NetSnmpBackend):
        def _run(self, args, *, timeout_s, env=None, secrets=None):
            raise SnmpTimeout("no response from device")

    backend = _Failing()
    backend.backoff_base_s = 0.0
    with caplog.at_level(logging.DEBUG), pytest.raises(SnmpTimeout):
        backend.get(target, ["1.3.6.1.2.1.1.1.0"])
    assert secret not in caplog.text


# --- retry behaviour that matters for AAA-backed devices -------------------

def test_authorization_failures_are_never_retried():
    """Retrying a rejected credential is how account lockouts happen."""
    from actelis_mediation.snmp.backend import SnmpTarget
    from actelis_mediation.snmp.netsnmp import NetSnmpBackend

    calls = {"n": 0}

    class _Denied(NetSnmpBackend):
        def _run(self, args, *, timeout_s, env=None, secrets=None):
            calls["n"] += 1
            raise SnmpAuthorization("authorizationError")

    with pytest.raises(SnmpAuthorization):
        _Denied().get(SnmpTarget(host="h", ro_community="c", retries=5),
                      ["1.3.6.1.2.1.1.1.0"])
    assert calls["n"] == 1


def test_bad_value_on_a_write_is_not_retried():
    """A SET that the agent rejected must not be replayed."""
    from actelis_mediation.snmp.backend import SnmpTarget
    from actelis_mediation.snmp.netsnmp import NetSnmpBackend

    calls = {"n": 0}

    class _Bad(NetSnmpBackend):
        def _run(self, args, *, timeout_s, env=None, secrets=None):
            calls["n"] += 1
            raise SnmpBadValue("wrongType")

    with pytest.raises(SnmpBadValue):
        _Bad().set(SnmpTarget(host="h", ro_community="c", rw_community="c", retries=5),
                   [("1.3.6.1.4.1.5468.100.36.1.2.3.2.0", "a", "0.0.0.0")])
    assert calls["n"] == 1


# --- what the devices actually support -------------------------------------

def test_the_switch_supports_snmpv3(mib_defs):
    """Contradicts the original premise that these devices are v2c-only.

    If this holds, cleartext on the switch is a configuration choice and the
    mitigation is authPriv, not an OOB network.
    """
    import mibscan
    tcs = {k.split(":")[-1]: v for k, v in mibscan.ALL_TCS.items()}
    assert "snmpV3" in tcs["VTSSSnmpVersion"]
    assert "snmpAuthPriv" in tcs["VTSSSnmpSecurityLevel"]
    assert "snmpSHAAuthProtocol" in tcs["VTSSSnmpAuthProtocl"]
    assert "snmpAESPrivProtocol" in tcs["VTSSSnmpPrivProtocl"]
    assert "usm" in tcs["VTSSSnmpSecurityModel"]

    defs, _ = mib_defs
    assert "ml540mSnmpConfigUserTable" in defs, "USM user provisioning table"
    assert "ml540mSnmpConfigAccessGroupTable" in defs, "VACM access groups"


def test_the_write_community_is_readable_and_that_is_the_exposure(mib_defs):
    """Documented as a bootstrap convenience in the original. It is also the
    whole v2c security model: read access yields write access."""
    defs, _ = mib_defs
    write = defs["ml540mSnmpConfigGlobalsWriteCommunity"]
    assert write["access"] in ("read-write", "read-only"), (
        "the write community is retrievable over SNMP -- any RO credential "
        "escalates to RW, which is why SNMPv3 matters here")


def test_source_restricted_community_table_is_available_as_a_mitigation(mib_defs):
    defs, _ = mib_defs
    assert "ml540mSnmpConfigCommunityTable" in defs
    from actelis_mediation.rowedit.specs import SNMP_CONFIG_COMMUNITY_TABLE
    assert "sourceIP" in SNMP_CONFIG_COMMUNITY_TABLE.fields


# --- hardware ---------------------------------------------------------------

@pytest.mark.hardware
def test_live_device_is_not_on_factory_default_communities(live):
    device, _backend = live
    assert device.target.ro_community not in DEFAULT_COMMUNITIES, (
        f"{device.name} is still using a factory-default read community")
    if device.target.rw_community:
        assert device.target.rw_community not in DEFAULT_COMMUNITIES, (
            f"{device.name} is still using a factory-default write community")


@pytest.mark.hardware
def test_live_snmp_version_setting(live):
    from actelis_mediation.poll import oids as O
    device, backend = live
    if device.device_type != "switch":
        pytest.skip("ML540M-specific object")
    vb = backend.get(device.target, [O.SWITCH_SNMP_VERSION + ".0"])
    version = next(iter(vb.values())).value
    print(f"\n{device.name} SNMP version setting: {version}")
    if "v3" not in version.lower():
        pytest.xfail(f"{device.name} is running {version}; SNMPv3 authPriv is "
                     f"supported by this platform and should be the target")
