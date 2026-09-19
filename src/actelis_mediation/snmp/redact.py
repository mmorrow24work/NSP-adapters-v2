"""Keep community strings out of logs, exceptions and tracebacks.

SNMPv2c has exactly one credential and it is sent in clear. Anything that
formats a net-snmp command line into an error message or a log record leaks
it — including the *write* community, which on these devices is also readable
with the read community, so one leak is total.

The original wrapper raised ``SnmpTimeout(f"process timed out: {' '.join(args)}")``,
which puts the community into every timeout traceback.
"""
from __future__ import annotations

import re

REDACTED = "<redacted>"
# Flags whose *following* argument is a secret.
_SECRET_FLAGS = {"-c", "-A", "-X", "-u"}
_INLINE_RE = re.compile(r"(-(?:c|A|X|u))[= ]([^\s]+)")


def redact_args(args: list[str]) -> str:
    """Render a command line with credential arguments masked."""
    out: list[str] = []
    mask_next = False
    for arg in args:
        if mask_next:
            out.append(REDACTED)
            mask_next = False
            continue
        out.append(arg)
        if arg in _SECRET_FLAGS:
            mask_next = True
    return " ".join(out)


def redact_text(text: str, secrets: list[str] | None = None) -> str:
    """Mask credential flags, plus any explicitly-known secret values."""
    masked = _INLINE_RE.sub(lambda m: f"{m.group(1)} {REDACTED}", text or "")
    for secret in secrets or []:
        if secret:
            masked = masked.replace(secret, REDACTED)
    return masked
