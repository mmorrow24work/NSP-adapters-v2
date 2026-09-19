"""Device inventory configuration.

Credentials are NOT stored in the repo. Each device names an environment
variable holding its community string; the original shipped a config with
``public``/``private`` inline, which is how factory-default credentials end
up committed and then deployed.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .snmp.backend import SnmpTarget


class ConfigError(Exception):
    pass


def _secret(spec: dict, key: str, device: str, required: bool = True) -> str | None:
    """Resolve a credential from ``<key>_env`` (preferred) or ``<key>``."""
    env_name = spec.get(f"{key}_env")
    if env_name:
        value = os.environ.get(env_name)
        if not value and required:
            raise ConfigError(
                f"{device}: {key}_env points at ${env_name}, which is not set")
        return value
    if key in spec:
        return str(spec[key])
    if required:
        raise ConfigError(f"{device}: no {key} or {key}_env configured")
    return None


@dataclass
class DeviceConfig:
    name: str
    device_type: str
    target: SnmpTarget
    intervals: dict[str, float] = field(default_factory=dict)


@dataclass
class AppConfig:
    devices: list[DeviceConfig]
    db_path: str
    community_mode: str = "argv"

    @classmethod
    def load(cls, path: str | Path) -> AppConfig:
        raw = yaml.safe_load(Path(path).read_text())
        if not raw or "devices" not in raw:
            raise ConfigError(f"{path}: no 'devices' section")
        devices = []
        for spec in raw["devices"]:
            name = spec.get("name") or "<unnamed>"
            dtype = spec.get("device_type")
            if dtype not in ("switch", "dsl-modem"):
                raise ConfigError(f"{name}: device_type must be 'switch' or 'dsl-modem'")
            devices.append(DeviceConfig(
                name=name, device_type=dtype,
                target=SnmpTarget(
                    host=spec["host"],
                    ro_community=_secret(spec, "ro_community", name),
                    rw_community=_secret(spec, "rw_community", name, required=False),
                    port=int(spec.get("port", 161)),
                    timeout_s=float(spec.get("timeout_s", 3.0)),
                    retries=int(spec.get("retries", 2)),
                    walk_timeout_s=float(spec.get("walk_timeout_s", 300.0)),
                ),
                intervals=spec.get("poll", {}) or {}))
        storage = raw.get("storage", {})
        return cls(devices=devices,
                   db_path=storage.get("sqlite_path", "actelis-mediation.db"),
                   community_mode=raw.get("snmp", {}).get("community_mode", "argv"))
