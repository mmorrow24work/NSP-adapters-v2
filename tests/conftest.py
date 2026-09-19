import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))


def pytest_addoption(parser):
    parser.addoption("--device", action="store", default=None,
                     help="device name from the config to run hardware-marked "
                          "FCAPS tests against; without it they are skipped")
    parser.addoption("--device-config", action="store", default="etc/devices.yaml",
                     help="device inventory to use for hardware-marked tests")


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "fcaps(pillar): an FCAPS acceptance assertion "
                   "(fault|configuration|accounting|performance|security)")
    config.addinivalue_line(
        "markers", "hardware: needs a reachable device; requires --device")
    config.addinivalue_line(
        "markers", "writes: performs an SNMP SET against a real device")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--device"):
        return
    skip = pytest.mark.skip(reason="needs --device <name> and a reachable unit")
    for item in items:
        if "hardware" in item.keywords:
            item.add_marker(skip)
