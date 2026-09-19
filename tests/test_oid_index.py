"""Index handling -- the regression suite for the most serious original defect.

The original reduced every row index to the last sub-identifier. These tests
pin the correct behaviour for each index shape actually present in the vendor
MIBs, including the exact bytes captured from the lab unit.
"""
import pytest

from actelis_mediation.model import tables
from actelis_mediation.snmp.oid import (STRING, IndexSpec,
                                        index_suffix, is_within,
                                        rows_from_columns)


def test_is_within_does_not_confuse_sibling_prefixes():
    # A plain string startswith() would wrongly call 5468.1002 a child of
    # 5468.100 -- and 5468.100 is the switch's entire enterprise subtree.
    assert is_within("1.3.6.1.4.1.5468.100.1", "1.3.6.1.4.1.5468.100")
    assert not is_within("1.3.6.1.4.1.5468.1002", "1.3.6.1.4.1.5468.100")
    assert is_within("1.3.6.1.4.1.5468.100", "1.3.6.1.4.1.5468.100")


def test_index_suffix_strips_the_column_not_a_fixed_count():
    assert index_suffix("1.3.6.1.2.1.10.48.1.6.1.2.101.1.1.1.5",
                        "1.3.6.1.2.1.10.48.1.6.1.2") == "101.1.1.1.5"


def test_decodes_the_real_lab_captured_community_row():
    """Bytes lifted verbatim from docs/lab-results/ml540m-row-editor-20260918.txt."""
    suffix = "11.99.108.97.117.100.101.45.116.101.115.116.0.0.0.0.0"
    assert tables.SWITCH_SNMP_COMMUNITY.decode(suffix) == {
        "name": "claude-test", "sourceIP": "0.0.0.0", "prefixSize": 0}


def test_community_index_round_trips():
    spec = tables.SWITCH_SNMP_COMMUNITY
    suffix = spec.encode(name="nsp-ro", sourceIP="10.20.30.0", prefixSize=24)
    assert spec.decode(suffix) == {"name": "nsp-ro", "sourceIP": "10.20.30.0",
                                   "prefixSize": 24}


def test_pre_existing_lab_rows_decode():
    # The same walk showed the factory 'public' and 'private' community rows.
    assert tables.SWITCH_SNMP_COMMUNITY.decode(
        "6.112.117.98.108.105.99.0.0.0.0.0")["name"] == "public"
    assert tables.SWITCH_SNMP_COMMUNITY.decode(
        "7.112.114.105.118.97.116.101.0.0.0.0.0")["name"] == "private"


def test_hdsl2_shdsl_index_has_five_components():
    got = tables.DSL_15MIN_INTERVAL.decode("101.1.2.1.42")
    assert got == {"ifIndex": 101, "invIndex": 1, "endpointSide": 2,
                   "wirePair": 1, "intervalNumber": 42}
    # The original kept only the last sub-identifier, i.e. "42" -- which loses
    # the port, the endpoint side and the wire pair entirely.
    assert got["ifIndex"] != 42


def test_trailing_subids_are_rejected_not_silently_ignored():
    with pytest.raises(ValueError, match="trailing sub-identifier"):
        tables.SWITCH_LM.decode("1.2.3")


def test_truncated_string_index_is_rejected():
    with pytest.raises(ValueError, match="claims length"):
        IndexSpec(names=["n"], kinds=[STRING]).decode("11.99.108")


def test_rows_joined_on_full_two_component_index():
    """The DmUnit bug: two rows sharing an entryId across different intervals."""
    unit_col = "1.3.6.1.4.1.5468.100.117.1.3.1.2.1.16"
    avg_col = "1.3.6.1.4.1.5468.100.117.1.3.1.2.1.27"
    walks = {
        "__unit": {f"{unit_col}.1.7": "us(0)", f"{unit_col}.2.7": "ns(1)"},
        "avg":    {f"{avg_col}.1.7": "1500",  f"{avg_col}.2.7": "1500"},
    }
    rows = rows_from_columns(walks, {"__unit": unit_col, "avg": avg_col},
                             tables.SWITCH_DM, strict=True)
    assert len(rows) == 2
    by_interval = {r.index["intervalId"]: r for r in rows}
    # Interval 1 is in microseconds, interval 2 in nanoseconds. Keying on the
    # last sub-identifier alone (7) would collapse these into one row and
    # apply one unit to both -- a 1000x error.
    assert by_interval[1].values["__unit"] == "us(0)"
    assert by_interval[2].values["__unit"] == "ns(1)"


def test_undecodable_row_is_skipped_not_fatal_by_default():
    col = "1.3.6.1.4.1.5468.100.117.1.3.1.1.1.18"
    walks = {"c": {f"{col}.1.2": "5", f"{col}.9.9.9": "6"}}
    rows = rows_from_columns(walks, {"c": col}, tables.SWITCH_LM)
    assert len(rows) == 1          # the malformed row is dropped
    with pytest.raises(ValueError):
        rows_from_columns(walks, {"c": col}, tables.SWITCH_LM, strict=True)
