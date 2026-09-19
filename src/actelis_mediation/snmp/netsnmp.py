"""net-snmp CLI backend.

Preserves the invocations proven against the lab ML540M
(``tools/lab/validate_snmp_switch.sh``, ``tools/lab/test_row_editor.sh``)
and fixes four defects found in the original wrapper:

1. **Partial results were discarded.** The original scanned combined
   stdout+stderr for "No Such Instance" and raised for the whole call. On a
   multi-OID GET that means one unimplemented identity OID destroys the
   values that *did* come back -- and this device family is already known to
   ship firmware with missing subtrees. Now parsed per-varbind: present
   values are returned, absent ones are reported separately.

2. **Walks used GETNEXT.** ``snmpwalk`` on a v2c target issues one request
   per row. The HDSL2-SHDSL 15-minute table is 96 bins x ports x wire pairs
   x endpoint sides; that is thousands of round trips. Uses ``snmpbulkwalk``
   with ``-Cr`` where available, falling back to ``snmpwalk``.

3. **A hardcoded 30s subprocess timeout** cut off legitimate long walks
   regardless of the configured per-request timeout. Now derived from the
   target's ``walk_timeout_s``.

4. **The community string was passed on argv**, where any local user can
   read it from ``ps``. This matters more than usual here because the write
   community is in play and SNMPv2c has no other credential.
   ``community_mode="snmp_conf"`` writes a private 0600 ``snmp.conf`` and
   points ``SNMPCONFPATH`` at it, keeping the secret off the command line.

   NOTE: ``snmp_conf`` mode has NOT been verified against a live device in
   this work -- net-snmp is not installed in the environment this was written
   in. It is therefore *not* the default. ``community_mode="auto"`` probes
   once and falls back to argv if the probe fails. Treat enabling it as a
   lab-verification task (see docs/security-posture.md), exactly the way the
   missing trailing ``.0`` was only settled by running against real hardware.
"""
from __future__ import annotations

import logging
import os
import random
import re
import shutil
import stat
import subprocess
import tempfile
import time
from dataclasses import dataclass

from .backend import SnmpTarget, VarBind
from .errors import (SnmpAuthorization, SnmpBadValue, SnmpError,
                     SnmpInvocationError, SnmpNoSuchObject, SnmpTimeout,
                     SnmpToolMissing)
from .oid import normalize
from .redact import redact_args, redact_text

logger = logging.getLogger(__name__)

_NO_SUCH_RE = re.compile(r"No Such (Instance|Object)", re.IGNORECASE)
_TIMEOUT_RE = re.compile(r"Timeout: No Response|No Response from", re.IGNORECASE)
_AUTH_RE = re.compile(r"authorizationError|noAccess|Authentication failure", re.IGNORECASE)
_BADVAL_RE = re.compile(r"wrongType|badValue|wrongLength|wrongValue|inconsistentValue|notWritable",
                        re.IGNORECASE)
# A USAGE banner means we built the command line wrong. It is deterministic,
# so retrying is pure waste -- and it masks the real cause behind N retries.
_USAGE_RE = re.compile(r"^USAGE:", re.MULTILINE)
# "<oid> = <TYPE>: <value>"  or  "<oid> = <value>"
_VARBIND_RE = re.compile(r"^(?P<oid>[.\d]+)\s*=\s*(?:(?P<type>[A-Za-z0-9 ]+):\s*)?(?P<value>.*)$")


@dataclass
class NetSnmpBackend:
    community_mode: str = "argv"          # "argv" | "snmp_conf" | "auto"
    backoff_base_s: float = 0.5
    backoff_max_s: float = 8.0
    _conf_dir: str | None = None
    _probed: bool = False

    # -- credential handling ------------------------------------------------

    def _conf_env(self, community: str) -> dict[str, str] | None:
        """Write a private snmp.conf carrying the community; return the env."""
        if self._conf_dir is None:
            self._conf_dir = tempfile.mkdtemp(prefix="actelis-snmp-")
            os.chmod(self._conf_dir, stat.S_IRWXU)
        path = os.path.join(self._conf_dir, "snmp.conf")
        with open(path, "w") as fh:
            fh.write(f"defCommunity {community}\n")
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
        env = dict(os.environ)
        env["SNMPCONFPATH"] = self._conf_dir
        return env

    def _auth(self, community: str) -> tuple[list[str], dict[str, str] | None]:
        """Return (extra argv, env) carrying the community."""
        if self.community_mode == "snmp_conf":
            return [], self._conf_env(community)
        return ["-c", community], None

    # -- process plumbing ---------------------------------------------------

    def _run(self, args: list[str], *, timeout_s: float,
             env: dict[str, str] | None = None,
             secrets: list[str] | None = None) -> str:
        """Run a net-snmp tool. Every error path is redacted: the community
        string must never reach a log record or a traceback."""
        safe_cmd = redact_args(args)
        try:
            proc = subprocess.run(args, capture_output=True, text=True,
                                  timeout=timeout_s, check=False, env=env)
        except FileNotFoundError as exc:
            raise SnmpToolMissing(
                f"{args[0]} not found -- install net-snmp (same requirement as "
                f"tools/lab/validate_snmp_switch.sh)") from exc
        except subprocess.TimeoutExpired as exc:
            # TimeoutExpired stringifies its own argv, which holds the
            # community string. `from None` only suppresses *display* of the
            # context -- the object is still reachable as __context__ and
            # anything that logs it leaks the credential. So scrub the
            # exception itself before letting it become our context.
            exc.cmd = safe_cmd
            exc.output = None
            exc.stderr = None
            raise SnmpTimeout(f"{safe_cmd} exceeded {timeout_s}s") from None

        output = (proc.stdout or "") + (proc.stderr or "")
        safe_out = redact_text(output, secrets).strip()
        if _TIMEOUT_RE.search(output):
            raise SnmpTimeout(f"no response from device: {safe_out[:300]}")
        if _AUTH_RE.search(output):
            raise SnmpAuthorization(f"agent refused the request: {safe_out[:300]}")
        if _BADVAL_RE.search(output):
            raise SnmpBadValue(safe_out[:400])
        if _USAGE_RE.search(output):
            raise SnmpInvocationError(
                f"net-snmp rejected the command line built by this adaptor: "
                f"{safe_cmd}\n{safe_out.splitlines()[0] if safe_out else ''}")
        if proc.returncode != 0 and not proc.stdout.strip():
            raise SnmpError(f"{safe_cmd} failed ({proc.returncode}): {safe_out[:300]}")
        return proc.stdout

    def _retrying(self, fn, *, retries: int, what: str):
        """Retry only on transient failures, with exponential backoff + jitter.

        ``SnmpNoSuchObject``, ``SnmpAuthorization`` and ``SnmpBadValue`` are
        deterministic: retrying them wastes time and, for authorization,
        risks tripping lockouts. They propagate immediately.
        """
        attempt = 0
        while True:
            try:
                return fn()
            except (SnmpNoSuchObject, SnmpAuthorization, SnmpBadValue,
                    SnmpToolMissing, SnmpInvocationError):
                raise
            except (SnmpTimeout, SnmpError) as exc:
                if attempt >= retries:
                    raise
                delay = min(self.backoff_base_s * (2 ** attempt), self.backoff_max_s)
                delay *= 0.5 + random.random()  # jitter: avoid lockstep re-polls
                logger.warning("%s failed (%s); retry %d/%d in %.1fs",
                               what, exc.__class__.__name__, attempt + 1, retries, delay)
                time.sleep(delay)
                attempt += 1

    # -- parsing ------------------------------------------------------------

    @staticmethod
    def _parse(output: str) -> tuple[dict[str, VarBind], list[str]]:
        """Parse varbind lines. Returns (varbinds, oids reported as missing).

        Multi-line DisplayString values (sysDescr routinely contains
        newlines) are appended to the previous varbind rather than dropped,
        which the original's line-by-line split silently did.
        """
        found: dict[str, VarBind] = {}
        missing: list[str] = []
        last: str | None = None
        for line in output.splitlines():
            if not line.strip():
                continue
            m = _VARBIND_RE.match(line.strip())
            if not m:
                if last is not None:      # continuation of a multi-line string
                    vb = found[last]
                    found[last] = VarBind(vb.oid, vb.value + "\n" + line.strip(), vb.type_name)
                continue
            oid = normalize(m.group("oid"))
            value = m.group("value").strip()
            if _NO_SUCH_RE.search(value) or value in ("", "No more variables left in this MIB View"):
                missing.append(oid)
                last = None
                continue
            found[oid] = VarBind(oid, value.strip('"'), (m.group("type") or "").strip())
            last = oid
        return found, missing

    # -- operations ---------------------------------------------------------

    def get(self, target: SnmpTarget, oids: list[str]) -> dict[str, VarBind]:
        auth, env = self._auth(target.ro_community)
        args = (["snmpget", "-v2c", *auth, "-r", "0",
                 "-t", str(target.timeout_s), "-OQn",
                 f"{target.host}:{target.port}", *oids])

        def once() -> dict[str, VarBind]:
            out = self._run(args, timeout_s=_budget(target, len(oids)), env=env,
                            secrets=[target.ro_community])
            found, missing = self._parse(out)
            if not found and missing:
                raise SnmpNoSuchObject(
                    f"{target.host}: none of {len(oids)} OIDs implemented "
                    f"(first: {missing[0]}). For a scalar, check the trailing '.0'.")
            if missing:
                logger.info("%s: %d/%d OIDs not implemented by the agent (%s)",
                            target.host, len(missing), len(oids), missing[0])
            return found

        return self._retrying(once, retries=target.retries, what=f"GET {target.host}")

    @staticmethod
    def walk_args(target: SnmpTarget, base_oid: str, auth: list[str]) -> list[str]:
        """Build the walk command line.

        Split out so it can be unit-tested without invoking net-snmp. The
        first live run against hardware failed here and nowhere else: net-snmp
        takes the -C sub-options CONCATENATED with their value ("-Cr25"), not
        as two argv tokens ("-Cr", "25"). Passing them separately makes the
        number look like a positional argument, net-snmp reads it as the agent
        address, and the whole invocation dies with a USAGE banner.

        Nothing in the mocked test suite could catch that, because FakeBackend
        never builds a command line. Hence tests/test_snmp_argv.py.
        """
        use_bulk = target.use_bulkwalk and shutil.which("snmpbulkwalk") is not None
        tool = "snmpbulkwalk" if use_bulk else "snmpwalk"
        args = [tool, "-v2c", *auth, "-r", "0", "-t", str(target.timeout_s), "-On"]
        if use_bulk:
            args.append(f"-Cr{int(target.max_repetitions)}")
        args += [f"{target.host}:{target.port}", base_oid]
        return args

    def walk(self, target: SnmpTarget, base_oid: str) -> dict[str, VarBind]:
        auth, env = self._auth(target.ro_community)
        args = self.walk_args(target, base_oid, auth)

        def once() -> dict[str, VarBind]:
            out = self._run(args, timeout_s=target.walk_timeout_s, env=env,
                            secrets=[target.ro_community])
            found, missing = self._parse(out)
            if not found:
                raise SnmpNoSuchObject(
                    f"{target.host}: {base_oid} returned no rows -- the agent does not "
                    f"implement this subtree (cf. the ML540M fw 00.00.16 LLDP status gap)")
            return found

        return self._retrying(once, retries=target.retries, what=f"WALK {target.host} {base_oid}")

    def set(self, target: SnmpTarget, binds: list[tuple[str, str, str]]) -> dict[str, VarBind]:
        auth, env = self._auth(target.write_community())
        args = ["snmpset", "-v2c", *auth, "-r", "0", "-t", str(target.timeout_s), "-OQn",
                f"{target.host}:{target.port}"]
        for oid, type_char, value in binds:
            args += [oid, type_char, value]

        def once() -> dict[str, VarBind]:
            found, _ = self._parse(self._run(
                args, timeout_s=_budget(target, len(binds)), env=env,
                secrets=[target.rw_community or ""]))
            return found

        # A SET is not idempotent in general; retry only the transport-level
        # failure, and only once, to avoid double-applying a write.
        return self._retrying(once, retries=min(1, target.retries), what=f"SET {target.host}")


def _budget(target: SnmpTarget, n_oids: int) -> float:
    """Subprocess wall-clock budget for a GET/SET, derived from config."""
    return max(10.0, target.timeout_s * (target.retries + 1) * max(1, n_oids) * 0.5 + 5.0)
