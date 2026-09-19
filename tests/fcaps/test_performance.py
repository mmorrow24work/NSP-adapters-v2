"""FCAPS · Performance — is the collected PM data actually usable?

Both families do on-device interval binning, so the adaptor's job is to pull
bins before they roll off and hand NSP numbers that mean something. Three
things have to hold for that to be true, and all three were broken in the
original: every sample must be attributable to a specific port/endpoint/bin,
re-polling must not inflate the archive, and a value must never carry a unit
the MIB did not state.
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from actelis_mediation.model import units
from actelis_mediation.poll import poll_device, poll_pm_dsl, poll_pm_switch
from actelis_mediation.snmp.backend import FakeBackend
from actelis_mediation.store import Store

from .conftest import modem_image, switch_image

pytestmark = pytest.mark.fcaps("performance")

REPO = Path(__file__).resolve().parents[2]


# --- attributability -------------------------------------------------------

def test_every_dsl_sample_identifies_its_port_endpoint_and_bin(modem_backend, target, pm_mapping):
    samples = poll_pm_dsl(modem_backend, target, pm_mapping)
    assert samples
    for s in samples:
        for component in ("ifIndex", "invIndex", "endpointSide", "wirePair",
                          "intervalNumber"):
            assert component in s["index"], (
                f"{s['source_object']} sample cannot be attributed: missing "
                f"{component}. An archive of unattributable bins is not PM data.")
        assert s["bin_window"] in ("15min", "1day")
        assert s["bin_id"] != ""


def test_bins_from_different_ports_do_not_collide(target, pm_mapping):
    be = FakeBackend(values=modem_image(bins=(
        (101, 1, 1, 1, 5), (102, 1, 1, 1, 5), (101, 1, 1, 2, 5))))
    samples = poll_pm_dsl(be, target, pm_mapping)
    keys = {s["index_key"] for s in samples}
    assert len(keys) == 3, "same bin number on different ports/pairs must stay distinct"


def test_every_switch_pm_sample_identifies_its_interval(switch_backend, target, pm_mapping):
    for s in poll_pm_switch(switch_backend, target, pm_mapping):
        assert "intervalId" in s["index"] and "entryId" in s["index"]


# --- archive integrity -----------------------------------------------------

def test_repolling_does_not_inflate_the_archive(target, tmp_path, alarm_mapping, pm_mapping):
    """The device keeps 96 bins; polling every 5 minutes must not store 288
    copies of each one per day."""
    be = FakeBackend(values=modem_image(
        bins=tuple((101, 1, 1, 1, n) for n in range(1, 97))))
    with Store(tmp_path / "pm.db") as store:
        for _ in range(5):
            poll_device("m", be, target, "dsl-modem", store, alarm_mapping,
                        pm_mapping, what=("pm",))
        rows = store.recent_pm("m", limit=10000)
    assert len(rows) == 96 * len(__import__(
        "actelis_mediation.poll.oids", fromlist=["x"]).DSL_15MIN_COLUMNS)


def test_pm_interval_beats_every_rollover_window():
    """Configured polling cadence must beat the tightest on-device window.

    The ML600 EVC counters keep only Curr/Prev -- one completed interval,
    overwritten by the next -- so a poll slower than the interval silently
    loses data with no way to recover it.
    """
    cfg = yaml.safe_load((REPO / "etc" / "devices.yaml.example").read_text())
    shortest_window_s = 15 * 60
    for device in cfg["devices"]:
        interval = device.get("poll", {}).get("pm_interval_s")
        assert interval is not None, f"{device['name']}: no pm_interval_s configured"
        assert interval < shortest_window_s, (
            f"{device['name']}: pm_interval_s={interval} does not beat the "
            f"{shortest_window_s}s bin window")
        assert interval <= shortest_window_s / 3, (
            f"{device['name']}: pm_interval_s={interval} leaves no margin for "
            f"a missed or slow poll")


# --- units: the part that silently corrupts data ---------------------------

def test_stated_scales_match_the_mib_worked_examples():
    """Each scale is checked against the example the MIB itself gives."""
    assert units.FLR_MEASURED.apply(50) == 0.005          # "50 means 0.005%"
    assert units.FLR_OBJECTIVE.apply(90_000) == 90.0      # "90000 means >= 90%"
    assert round(units.UTILIZATION.apply(5985), 3) == 5.985   # "5985 means 5.985%"


def test_measured_and_objective_loss_ratios_use_different_scales():
    """A 10x trap: comparing a measurement to its threshold without rescaling
    gives a silently wrong verdict."""
    assert units.FLR_MEASURED.factor == pytest.approx(1e-4)
    assert units.FLR_OBJECTIVE.factor == pytest.approx(1e-3)


def test_delay_unit_is_read_per_row_never_assumed(target, pm_mapping):
    be = FakeBackend(values=switch_image(
        dm_rows=((1, 7, "us(0)"), (2, 7, "ns(1)"))))
    dm = {s["index"]["intervalId"]: s for s in poll_pm_switch(be, target, pm_mapping)
          if s["bin_window"] == "evc-dm"}
    assert dm[1]["unit"] == "microseconds"
    assert dm[2]["unit"] == "nanoseconds"


def test_an_unstated_scale_is_never_silently_applied(switch_backend, target, pm_mapping):
    """The switch loss-rate scale is genuinely unknown. A plausible assumption
    presented as a value is worse than an obvious gap."""
    rates = [s for s in poll_pm_switch(switch_backend, target, pm_mapping)
             if s["source_object"].endswith("LossRate")]
    assert rates
    for s in rates:
        assert s["value"] is None
        assert s["unit_verified"] is False
        assert s["raw_value"] is not None, "the raw reading must still be kept"


def test_unknown_delay_unit_does_not_default_to_microseconds(target, pm_mapping):
    be = FakeBackend(values=switch_image(dm_rows=((1, 7, "ps(2)"),)))
    dm = [s for s in poll_pm_switch(be, target, pm_mapping) if s["bin_window"] == "evc-dm"]
    assert dm and all(s["value"] is None and not s["unit_verified"] for s in dm)


def test_every_pm_mapping_row_is_usable(pm_mapping):
    for r in pm_mapping.rows:
        assert r.nsp_metric_name, f"{r.source_mib_object} has no metric name"
        assert r.bin_window, f"{r.source_mib_object} has no bin window"
        assert r.device_type in ("switch", "dsl-modem")


def test_counters_are_stored_absolute_with_identity(modem_backend, target, pm_mapping):
    """Deltas and 32-bit rollover are handled downstream, not in collection.

    Storing the absolute reading with its bin identity keeps that possible;
    storing a pre-computed delta would not survive a missed poll.
    """
    for s in poll_pm_dsl(modem_backend, target, pm_mapping):
        assert s["raw_value"] is not None
        assert s["index_key"]


# --- hardware ---------------------------------------------------------------

@pytest.mark.hardware
def test_live_pm_tables_are_populated(live, pm_mapping):
    device, backend = live
    poll = poll_pm_switch if device.device_type == "switch" else poll_pm_dsl
    samples = poll(backend, device.target, pm_mapping)
    print(f"\n{len(samples)} PM sample(s) from {device.name}")
    if not samples:
        pytest.skip("no PM rows on this firmware/config -- record as a "
                    "capability gap rather than a failure")
    for s in samples:
        assert s["index_key"], "a live sample with no index is the original defect"
