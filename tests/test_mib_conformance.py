"""Check the code's OID constants and index specs against the vendor MIBs.

This is the guard against firmware/MIB drift: the archives are extracted and
parsed independently at test time, so a vendor MIB revision that moves an
object or adds an index component fails the build rather than silently
corrupting collected data.

Skipped (not failed) when py7zr or the archives are unavailable.
"""
import pytest

pytest.importorskip("py7zr")

from actelis_mediation.verify import verify_index_specs, verify_oids   # noqa: E402


@pytest.fixture(scope="module")
def oid_problems():
    return verify_oids()


def test_every_oid_constant_resolves_to_its_expected_mib_object(oid_problems):
    assert oid_problems == []


def test_every_index_spec_matches_its_mib_index_clause():
    assert verify_index_specs() == []


def test_generated_row_editor_specs_point_at_real_mib_objects():
    from actelis_mediation.rowedit import specs
    from actelis_mediation.verify import load_mibs
    _defs, by_oid = load_mibs()
    checked = 0
    for name, spec in specs.ALL_SPECS.items():
        assert by_oid.get(spec.action_oid[:-2].lstrip(".")), f"{name}: action OID not in MIB"
        assert by_oid.get(spec.table_oid.lstrip(".")), f"{name}: table OID not in MIB"
        for fname, fld in spec.fields.items():
            obj = by_oid.get(fld.oid[:-2].lstrip("."))
            assert obj is not None, f"{name}.{fname}: {fld.oid} not in MIB"
            assert obj["access"] in ("read-write", "read-create"), \
                f"{name}.{fname} is {obj['access']}, cannot be staged"
            checked += 1
    assert checked > 300
