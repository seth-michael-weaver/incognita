"""WP-10: ENSDF adopted-levels parser — field grammar (pure), then known values from
the archive (56Fe, 90Zr, 208Pb, 238U) and the level-count comparison with RIPL-4.
Archive-dependent tests are skipped when ``raw/ensdf/ensdf_260901.zip`` is missing."""

from __future__ import annotations

import polars as pl
import pytest

from data.ingest import ensdf as E

needs_zip = pytest.mark.skipif(not E.ENSDF_ZIP.exists(), reason="ENSDF archive not present")


# --------------------------------------------------------------------------- pure parsers


@pytest.mark.parametrize(
    "e, de, expected",
    [
        ("846.7778", "19", (846.7778, 0.0019, None, None)),
        ("0.0", "", (0.0, None, None, None)),
        ("2614.522", "10", (2614.522, 0.010, None, None)),
        ("1234+X", "", (1234.0, None, "X", None)),
        ("X+123.4", "5", (123.4, 0.5, "X", None)),
        ("X", "", (None, None, "X", None)),
        ("SN+100", "AP", (100.0, None, "SN", "AP")),
        ("2500", "AP", (2500.0, None, None, "AP")),
        ("2.5E3", "2", (2500.0, 200.0, None, None)),
        ("", "", (None, None, None, None)),
    ],
)
def test_parse_energy(e, de, expected):
    got = E.parse_energy(e, de)
    for g, x in zip(got, expected, strict=True):
        if isinstance(x, float):
            assert g == pytest.approx(x)
        else:
            assert g == x


def test_parse_half_life_units_and_widths():
    hl = E.parse_half_life("4.468E9 Y", "6")
    assert hl["half_life_s"] == pytest.approx(4.468e9 * 365.25 * 86400)
    assert hl["half_life_sigma_s"] == pytest.approx(0.006e9 * 365.25 * 86400)
    assert E.parse_half_life("16.7 PS", "3")["half_life_s"] == pytest.approx(16.7e-12)
    asym = E.parse_half_life("35 FS", "+19-9")
    assert asym["half_life_s"] == pytest.approx(35e-15)
    assert asym["half_life_sigma_s"] == pytest.approx(19e-15)  # max of the asymmetric pair
    w = E.parse_half_life("1.10 EV", "")
    assert w["width_ev"] == pytest.approx(1.1)
    assert w["half_life_s"] == pytest.approx(E.HBAR_LN2_EV_S / 1.1)
    lt = E.parse_half_life("1.2 KEV", "LT")
    assert lt["width_ev"] == pytest.approx(1200.0) and lt["half_life_qualifier"] == "LT"
    assert E.parse_half_life("STABLE", "")["is_stable"] is True
    assert E.parse_half_life("", "")["half_life_s"] is None


@pytest.mark.parametrize(
    "raw, js, ps, tentative, unique",
    [
        ("3/2+", [1.5], [1], False, True),
        ("0+", [0.0], [1], False, True),
        ("(2+)", [2.0], [1], True, False),
        ("1/2-,3/2-", [0.5, 1.5], [-1, -1], False, False),
        ("(1,2)+", [1.0, 2.0], [1, 1], True, False),
        ("3/2(+)", [1.5], [1], True, False),
        ("1:4", [1.0, 2.0, 3.0, 4.0], [0, 0, 0, 0], False, False),
        ("1- TO 4-", [1.0, 2.0, 3.0, 4.0], [-1] * 4, False, False),
        ("(1+ TO 3+)", [1.0, 2.0, 3.0], [1, 1, 1], True, False),
        ("2+,(3)+", [2.0, 3.0], [1, 1], True, False),
        ("2+,3,4+", [2.0, 3.0, 4.0], [1, 0, 1], False, False),
        ("+", [], [1], False, False),
        ("GE 2", [], [], False, False),
        ("(>3-)", [], [], True, False),
        ("J", [], [], False, False),
        ("", [], [], False, False),
    ],
)
def test_parse_jpi(raw, js, ps, tentative, unique):
    assert E.parse_jpi(raw) == (js, ps, tentative, unique)


# --------------------------------------------------------------------------- archive


@pytest.fixture(scope="module")
def parsed() -> tuple[pl.DataFrame, pl.DataFrame]:
    if not E.ENSDF_ZIP.exists():
        pytest.skip("ENSDF archive not present")
    members = ["ensdf.056", "ensdf.090", "ensdf.208", "ensdf.238"]
    return E.read_adopted_levels(E.ENSDF_ZIP, members=members)


def _nuc(levels: pl.DataFrame, Z: int, A: int) -> pl.DataFrame:
    return levels.filter((pl.col("Z") == Z) & (pl.col("A") == A)).sort("level_index")


@needs_zip
def test_dataset_selection_and_q_record(parsed):
    levels, datasets = parsed
    assert set(datasets["A"]) == {56, 90, 208, 238}
    assert datasets["dsid"].str.starts_with("ADOPTED LEVELS").all()
    fe = datasets.filter((pl.col("Z") == 26) & (pl.col("A") == 56)).row(0, named=True)
    assert fe["sn_kev"] == pytest.approx(11197.10, abs=0.05)
    assert fe["sp_kev"] == pytest.approx(10183.67, abs=0.05)
    assert fe["date"] == "201105" and fe["n_levels"] == 299
    assert levels.schema == pl.Schema(E.LEVEL_SCHEMA)


@needs_zip
def test_fe56_first_excited_level(parsed):
    levels, _ = parsed
    fe = _nuc(levels, 26, 56)
    assert fe.height == 299
    gs, first = fe.row(0, named=True), fe.row(1, named=True)
    assert gs["energy_kev"] == 0.0 and gs["is_stable"] and gs["jpi_raw"] == "0+"
    assert first["energy_kev"] == pytest.approx(846.7778)
    assert first["energy_sigma_kev"] == pytest.approx(0.0019)
    assert first["jpi_raw"] == "2+" and first["j_values"] == [2.0] and first["j_unique"]
    assert first["half_life_s"] == pytest.approx(6.07e-12)
    assert first["half_life_sigma_s"] == pytest.approx(0.23e-12)
    assert first["n_gammas"] == 1 and first["n_continuation"] >= 2
    assert first["comment_flag"] == "E"


@needs_zip
def test_pb208_and_u238_first_excited_levels(parsed):
    levels, _ = parsed
    pb = _nuc(levels, 82, 208)
    assert pb.height == 611
    l1 = pb.row(1, named=True)
    assert l1["energy_kev"] == pytest.approx(2614.522)
    assert l1["jpi_raw"] == "3-" and l1["parities"] == [-1]
    assert l1["half_life_s"] == pytest.approx(16.7e-12)
    u = _nuc(levels, 92, 238)
    assert u.height == 285
    assert u.row(0, named=True)["half_life_s"] == pytest.approx(4.468e9 * 365.25 * 86400)
    l1 = u.row(1, named=True)
    assert l1["energy_kev"] == pytest.approx(44.916)
    assert l1["energy_sigma_kev"] == pytest.approx(0.013)
    assert l1["jpi_raw"] == "2+" and l1["half_life_s"] == pytest.approx(206e-12)
    zr = _nuc(levels, 40, 90)
    assert zr.row(1, named=True)["energy_kev"] == pytest.approx(1760.71, abs=0.05)
    assert zr.row(1, named=True)["jpi_raw"] == "0+"


@needs_zip
def test_level_counts_against_ripl_cutoff(parsed):
    from data.ingest import ripl as R

    levels, _ = parsed
    if not (R.RIPL4_ROOT / "levels" / "levels-param.data").exists():
        pytest.skip("RIPL-4 levels segment not present")
    counts = E.level_counts(levels, R.read_levels_param(R.RIPL4_ROOT))
    fe = counts.filter(pl.col("nuclide_id") == "Z026N030M0").row(0, named=True)
    assert fe["ripl_nmax"] == 79 and fe["ripl_umax_mev"] == pytest.approx(5.4023)
    # ENSDF 2026-09 has one more level below Umax than RIPL-4's Oct-2025 snapshot
    assert fe["n_below_umax"] in (79, 80)
    assert fe["n_levels"] == 299 and fe["n_known_energy"] == 299
    assert 2.3 < fe["spin_cutoff_discrete"] < 3.0  # RIPL quotes 2.556 with inferred spins
    pb = counts.filter(pl.col("nuclide_id") == "Z082N126M0").row(0, named=True)
    assert pb["n_below_umax"] == pb["ripl_nmax"] == 182
    u = counts.filter(pl.col("nuclide_id") == "Z092N146M0").row(0, named=True)
    assert u["n_below_umax"] == u["ripl_nmax"] == 45
    zr = counts.filter(pl.col("nuclide_id") == "Z040N050M0").row(0, named=True)
    assert zr["n_below_umax"] == zr["ripl_nmax"] == 81
    cum = E.cumulative_levels(levels)
    fe_cum = cum.filter(pl.col("nuclide_id") == "Z026N030M0").row(0, named=True)
    assert fe_cum["energies_kev"][:3] == pytest.approx([0.0, 846.7778, 2085.1045])
    assert fe_cum["n_known_energy"] == 299


@needs_zip
def test_unknown_offset_levels_are_excluded_from_counts(parsed):
    levels, _ = parsed
    off = levels.filter(pl.col("energy_offset").is_not_null())
    assert off.height > 0
    counts = E.level_counts(levels)
    nid = off["nuclide_id"][0]
    row = counts.filter(pl.col("nuclide_id") == nid).row(0, named=True)
    assert row["n_known_energy"] < row["n_levels"]
