"""The YANDF parser and the TALYS reference harness (physics/hf/yandf.py, talys_reference.py).

Fixtures are verbatim excerpts of a TALYS-2.24 Fe-56 run (tests/hf/fixtures/talys/)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from physics.hf import talys_reference as T
from physics.hf.yandf import parse_blocks

FIX = Path(__file__).parent / "fixtures" / "talys"


def test_transmission_file_has_one_block_per_energy_with_its_energy():
    b = parse_blocks(FIX / "transmission_n.out")
    assert len(b) == 3
    assert [blk.meta_float("energy") for blk in b] == pytest.approx(
        [1.018033e-3, 2.036066e-3, 5.090164e-3]
    )
    assert b[0].columns == ["L", "T(L-1/2,L)", "T(L+1/2,L)", "T(L))"]
    # "entries" counts something other than rows (block 3 declares 2 and holds l = 0, 1, 2)
    assert b[0].data.shape == (2, 4) and b[2].data.shape == (3, 4)
    assert b[0].data[0, 2] == pytest.approx(0.1133237)


def test_cross_section_table_and_units():
    (b,) = parse_blocks(FIX / "ng.tot")
    assert b.columns[:2] == ["E", "xs"] and b.units[:2] == ["[MeV]", "[mb]"]
    assert b.meta_float("Q-value") == pytest.approx(7.646171)
    assert b.column("xs")[1] == pytest.approx(25.95691)


def test_adjacent_column_names_split_on_the_declared_count():
    # "Compound_elast. Shape_elastic" touch in the header; whitespace splitting loses a column
    (b,) = parse_blocks(FIX / "all.tot")
    assert len(b.columns) == 11 and b.data.shape == (5, 11)
    assert "Shape_elastic" in b.columns and "Compound_elast." in b.columns


def test_names_with_spaces_and_the_level_density_tables():
    blocks = parse_blocks(FIX / "ld026057.gs")
    assert blocks[0].meta["level density model"] == "Constant-Temperature"
    assert blocks[0].meta_float("experimental D0") == pytest.approx(2.54e4)
    rho = blocks[1]
    assert "rho(J)=  0.5" in rho.columns and len(rho.columns) == 46
    assert rho.data.shape == (5, 46)


def test_binE_units_row_is_talys_own_shifted_labels():
    blocks = parse_blocks(FIX / "binE0001.000.out")
    b = blocks[0]
    # contract §4.1 trap: TALYS labels `bin` [mb] and `Ex` []; kept verbatim, not "fixed"
    assert b.units[:3] == ["[mb]", "[]", "[mb]"]
    assert b.columns[:4] == ["bin", "Ex", "population", "JP= 0.5-"]


def test_non_numeric_and_ragged_rows_are_kept_not_dropped():
    (d,) = parse_blocks(FIX / "directE0001.000.out")
    assert d.data.shape[0] == 0 and len(d.raw_rows) == 1 and "2.0 +" in d.raw_rows[0][1]
    (lv,) = parse_blocks(FIX / "levels026057.out")
    assert lv.data.shape[0] == 0 and any("--->" in r for _, r in lv.raw_rows)


# ---- harness ---------------------------------------------------------------------------------

PHYSICS_KEYWORDS_ALLOWED = {"widthmode"}  # only the wfc_off variant sets physics


def _keys(text):
    return [ln.split()[0] for ln in text.splitlines() if ln.strip()]


def test_default_variant_sets_no_physics_keyword():
    allowed = {"projectile", "element", "mass", "energy"} | set(T.OUTPUT_KEYWORDS)
    allowed |= set(T.FISSION_OUTPUT_KEYWORDS)
    for t in T.REFERENCE_SET:
        inp, _ = T.input_text("default", t)
        extra = set(_keys(inp)) - allowed
        assert not extra, f"{t.tag}: physics keywords in a defaults run: {extra}"


def test_wfc_off_differs_from_default_by_widthmode_only():
    t = T.REFERENCE_SET[1]
    d = set(_keys(T.input_text("default", t)[0]))
    w = set(_keys(T.input_text("wfc_off", t)[0]))
    assert w - d == PHYSICS_KEYWORDS_ALLOWED and d - w == set()


def test_fission_output_keywords_only_above_a150():
    # `outfission y` on A <= 150 is a fatal TALYS error with exit code 0
    for t in T.REFERENCE_SET:
        keys = set(_keys(T.input_text("default", t)[0]))
        assert ("outfission" in keys) == (t.A > 150), t.tag


def test_no_keyword_takes_a_level_number():
    assert "filediscrete" not in T.OUTPUT_KEYWORDS


def test_energies_ascend_and_span_1kev_to_20mev():
    e = np.array(T.ENERGIES_MEV)
    assert (np.diff(e) > 0).all() and e[0] == 1e-3 and e[-1] == 20.0
    _, en = T.input_text("default", T.REFERENCE_SET[0])
    assert [float(x) for x in en.split()] == pytest.approx(list(e))


def test_reference_set_and_jobs():
    tags = [t.tag for t in T.REFERENCE_SET]
    assert len(tags) == len(set(tags)) == 24
    assert {t.shape for t in T.REFERENCE_SET} == {"spherical", "deformed", "actinide"}
    assert len(T.jobs(["default", "wfc_off", "minimal"])) == 54
    assert set(T.VARIANTS["minimal"]["targets"]) <= set(tags)
    assert T.VARIANTS["population"].get("on_demand")
    # the invariance check compares against what the production sweeps actually write
    from physics.talys.runner import DEFAULT_KEYWORDS

    assert T.MINIMAL_KEYWORDS == DEFAULT_KEYWORDS


def test_talys_out_incident_scalars_are_absolute_not_print_units():
    (row,) = T.parse_talys_out(FIX / "talys_out_excerpt.out")
    assert row["e_inc_mev"] == pytest.approx(1e-3)
    assert row["flagwidth"] is True
    assert row["sigma_tot_omp_mb"] == pytest.approx(1.2005e4)
    assert row["s0"] == pytest.approx(0.4667e-4) and row["s1"] == pytest.approx(4.79e-4)
    assert row["r_prime_fm"] == pytest.approx(6.6185)
    assert row["norm_sum_tjl_mb"] == pytest.approx(6500.6123)


def test_empty_blocks_keep_their_own_energy():
    # regression (T1 report): a flush that waited for rows gave each `entries: -1` block the NEXT
    # block's energy -- Ni-58 alpha started at 0.43 MeV instead of 0.32 and repeated 3.4 MeV
    import re

    path = FIX / "Ni058_transmission_a.out"
    printed = [float(x) for x in re.findall(r"energy \[MeV\]:\s+(\S+)", path.read_text())]
    blocks = parse_blocks(path)
    energies = [blk.meta_float("energy") for blk in blocks]
    assert energies == printed and len(set(energies)) == len(energies)
    assert energies[0] == pytest.approx(0.3218569)
    assert blocks[0].data.shape == (0, 2) and blocks[-1].data.shape[0] > 0
    assert all(blk.meta["particle"] == "alpha" for blk in blocks)  # file-level key inherited


def test_block_does_not_inherit_a_key_the_previous_block_had():
    # regression (T1 report): the proton block of binE has no continuum and no
    # `number of discrete levels`; it must not borrow the gamma block's 30
    gamma, proton, alpha = parse_blocks(FIX / "Ni058_binE0001.000.out")
    assert gamma.meta["ejectile"] == "gamma" and gamma.meta["number of discrete levels"] == "30"
    assert proton.meta["ejectile"] == "proton" and "number of discrete levels" not in proton.meta
    assert "continuum bin size [MeV]" not in proton.meta
    assert proton.meta_float("maximum excitation energy") == pytest.approx(1.383721)
    assert alpha.meta["number of discrete levels"] == "30"
    assert all(b.meta_float("E-incident") == pytest.approx(1.0) for b in (gamma, proton, alpha))
