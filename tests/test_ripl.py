"""WP-10: RIPL-4 parsers against known values (238U, 56Fe, 90Zr, 208Pb) and the join
into ``StructureParams``. Skipped when ``raw/ripl4/RIPL-4`` is not on disk."""

from __future__ import annotations

import math

import polars as pl
import pytest

from data.ingest import ripl as R
from data.schema import Source, StructureParams

pytestmark = pytest.mark.skipif(
    not (R.RIPL4_ROOT / "resonances" / "resonances_L0.dat").exists(),
    reason="RIPL-4 raw data not present",
)


def _row(df: pl.DataFrame, **cond) -> dict:
    out = df
    for k, v in cond.items():
        out = out.filter(pl.col(k) == v)
    assert out.height == 1, f"expected one row for {cond}, got {out.height}"
    return out.row(0, named=True)


# --------------------------------------------------------------------------- fixed width


def test_fortran_slices_groups_and_scale_factors():
    sl = R.fortran_slices("(3i4,2x,a2,1p,2e12.3,2(1x,f5.1))")
    kinds = [k for k, _, _ in sl]
    assert kinds == ["i", "i", "i", "a", "e", "e", "f", "f"]
    assert sl[3] == ("a", 14, 16)
    assert sl[-1] == ("f", 47, 52)
    line = "   1   2   3  Fe   1.000E+00" + " " * 12 + " " + "*****" + " " + "  2.5"
    vals = R.parse_fixed(line, sl)
    assert vals[:4] == [1, 2, 3, "Fe"]
    assert vals[4] == 1.0 and vals[5] is None  # blank field → None
    assert vals[6] is None and vals[7] == 2.5  # Fortran overflow → None


def test_symbol_to_z():
    assert R.symbol_to_z("Fe") == 26 and R.symbol_to_z("PB") == 82
    assert R.symbol_to_z("n") == 0 and R.symbol_to_z("120") == 120
    with pytest.raises(ValueError):
        R.symbol_to_z("Xx")


# --------------------------------------------------------------------------- resonances


@pytest.fixture(scope="module")
def res0() -> pl.DataFrame:
    return R.read_resonances(R.RIPL4_ROOT, 0)


@pytest.fixture(scope="module")
def rp() -> pl.DataFrame:
    return R.resonance_params(R.RIPL4_ROOT)


def test_resonance_file_counts(res0):
    assert res0.height == 324  # readme: 324 nuclides in resonances_L0.dat
    assert R.read_resonances(R.RIPL4_ROOT, 1).height == 248
    assert (res0["A"] == res0["Z"] + res0["N"]).all()
    assert set(res0["source"]) == {Source.MEASURED.value}


def test_u238_resonance_parameters(res0, rp):
    raw = _row(res0, Z=92, A=238)
    assert raw["d_ripl3_ev"] == pytest.approx(20.3)
    assert raw["d_ripl3_sigma_ev"] == pytest.approx(0.6)
    assert raw["d_bnl_ev"] == pytest.approx(20.26)
    assert raw["gg_ripl3_ev"] == pytest.approx(0.0236)  # 23.6 meV
    assert raw["gg_bnl_ev"] == pytest.approx(0.0229)
    assert raw["s_ripl3_1e4"] == pytest.approx(1.03) and raw["s_bnl_1e4"] == pytest.approx(1.29)
    assert raw["Sn_mev"] == pytest.approx(4.806)
    r = _row(rp, Z=92, A=238)
    assert r["d0_ev"] == pytest.approx(20.3, abs=0.05)
    assert r["s0"] == pytest.approx(1.03e-4, rel=1e-6)
    assert r["gg_mev"] == pytest.approx(23.6)
    assert r["d0_origin"] == "RIPL-3"
    assert r["d1_ev"] == pytest.approx(7.7) and r["s1"] == pytest.approx(1.6e-4)


def test_bnl_fallback_when_ripl3_missing(res0, rp):
    # 48Ca has only a BNL S0; 40K has only a BNL D0
    assert _row(rp, Z=20, A=48)["s0_origin"] == "BNL2018"
    assert _row(rp, Z=19, A=40)["d0_ev"] == pytest.approx(840.0)
    bnl = R.resonance_params(R.RIPL4_ROOT, prefer="bnl")
    assert _row(bnl, Z=92, A=238)["d0_ev"] == pytest.approx(20.26)


def test_fe56_zr90_pb208_resonances(rp):
    fe = _row(rp, Z=26, A=56)
    assert fe["d0_ev"] == pytest.approx(25400.0) and fe["gg_mev"] == pytest.approx(920.0)
    assert fe["s0"] == pytest.approx(2.3e-4)
    zr = _row(rp, Z=40, A=90)
    assert zr["d0_ev"] == pytest.approx(6000.0) and zr["s0"] == pytest.approx(0.54e-4)
    pb = _row(rp, Z=82, A=208)
    assert pb["d0_ev"] == pytest.approx(90000.0) and pb["gg_mev"] is None


# --------------------------------------------------------------------------- levels


def test_levels_param_fe56():
    lp = R.read_levels_param(R.RIPL4_ROOT)
    assert lp.height > 3500
    fe = _row(lp, Z=26, A=56)
    assert fe["Nlev"] == 297 and fe["Nmax"] == 79 and fe["Nc"] == 6
    assert fe["Umax_mev"] == pytest.approx(5.4023)
    assert fe["ct_T_mev"] == pytest.approx(1.07035)
    assert fe["sigma_discrete"] == pytest.approx(2.556)
    assert fe["fit"] == "*" and fe["flag"] == ""
    assert _row(lp, Z=92, A=239)["flag"] == "F"


def test_discrete_levels_known_first_excited_states():
    lv = R.read_discrete_levels(R.RIPL4_ROOT, Z=[26, 82, 92])
    fe = lv.filter((pl.col("Z") == 26) & (pl.col("A") == 56)).sort("level_index")
    assert fe.height == 297
    assert fe.row(1, named=True)["energy_mev"] == pytest.approx(0.846778)
    assert fe.row(1, named=True)["jpi_raw"] == "2+"
    assert fe.row(0, named=True)["half_life_s"] == -1.0  # stable
    pb = lv.filter((pl.col("Z") == 82) & (pl.col("A") == 208)).sort("level_index")
    assert pb.height == 611
    assert pb.row(1, named=True)["energy_mev"] == pytest.approx(2.614522)
    assert pb.row(1, named=True)["spin"] == 3.0 and pb.row(1, named=True)["parity"] == -1
    u = lv.filter((pl.col("Z") == 92) & (pl.col("A") == 238)).sort("level_index")
    assert u.height == 285
    assert u.row(1, named=True)["energy_mev"] == pytest.approx(0.044916)
    gs = u.row(0, named=True)
    assert gs["n_decay_modes"] == 3 and gs["decay_modes"][0].endswith("%A")
    assert gs["half_life_s"] == pytest.approx(1.408e17)


def test_level_headers_match_param_file():
    h = R.read_level_headers(R.RIPL4_ROOT, Z=[26])
    fe = _row(h, A=56)
    assert fe["Nol"] == 297 and fe["Nog"] == 426 and fe["Nmax"] == 79
    assert fe["Sn_mev"] == pytest.approx(11.19706)


def test_gammas_are_attached_to_levels():
    lv, g = R.read_discrete_levels(R.RIPL4_ROOT, Z=[26], include_gammas=True)
    fe = g.filter(pl.col("A") == 56)
    assert fe.height == 426
    first = fe.filter(pl.col("level_index") == 2).row(0, named=True)
    assert first["final_index"] == 1 and first["e_gamma_mev"] == pytest.approx(0.8468)
    assert lv.filter(pl.col("A") == 56)["n_gammas"].sum() == 426


# --------------------------------------------------------------------------- densities


def test_egsm_level_density_parameters():
    eg = R.read_egsm(R.RIPL4_ROOT)
    assert eg.height == 291
    # The EGSM fit file uses the RIPL-3 column of the resonance file ("RIPL-4 Do"):
    # 56Fe target D0 = 25.4 keV (BNL says 22.0). Note 239U is absent from this file.
    fe57 = _row(eg, Z=26, A=57)
    assert fe57["D0_kev"] == pytest.approx(25.4) and fe57["ld_model"] == "EGSM"
    assert 3 < fe57["a_exp"] < 6
    pu239 = _row(eg, Z=94, A=239)  # compound of n + 238Pu
    assert pu239["D0_kev"] == pytest.approx(0.0083) and 18 < pu239["a_exp"] < 22
    assert eg.filter((pl.col("Z") == 92) & (pl.col("A") == 239)).height == 0
    assert set(eg["source"]) == {Source.MEASURED.value}


def test_comb_ld_normalisation_and_table():
    ld = R.read_comb_ld(R.RIPL4_ROOT, "bskg3")
    assert ld.height > 1000
    u = _row(ld, Z=92, A=238)
    assert u["alpha"] == pytest.approx(0.705) and u["delta_mev"] == pytest.approx(0.6402)
    tab = R.read_comb_table(R.RIPL4_ROOT, "bskg3", 92)
    u239 = tab.filter((pl.col("A") == 239) & (pl.col("parity") == 1)).sort("U_mev")
    assert u239.height == 60 and u239["U_mev"][0] == pytest.approx(0.25)
    assert u239["n_cumul"].is_sorted()


# --------------------------------------------------------------------------- gamma


def test_gdr_parameters_measured_vs_systematics():
    g = R.gdr_params(R.RIPL4_ROOT, "slo")
    assert g.height == 8980
    pb = _row(g, Z=82, A=208)
    assert pb["source"] == Source.MEASURED.value
    assert pb["er1_mev"] == pytest.approx(13.37) and pb["csp1_mb"] == pytest.approx(645.493)
    assert pb["er1_sigma_mev"] is not None and pb["er2_mev"] is None
    u = _row(g, Z=92, A=238)
    assert u["er1_mev"] == pytest.approx(11.06) and u["er2_mev"] == pytest.approx(14.26)
    fe = _row(g, Z=26, A=56)
    assert fe["source"] == Source.SYSTEMATICS.value and fe["er1_sigma_mev"] is None
    assert (g["is_experimental"] == 1).sum() == 135


def test_gdr_exp_recommended_is_first_entry():
    ge = R.read_gdr_exp(R.RIPL4_ROOT, "slo")
    u = ge.filter((pl.col("Z") == 92) & (pl.col("A") == 238))
    assert u.height == 4 and u["is_recommended"].to_list() == [True, False, False, False]
    assert u.row(0, named=True)["e_range_ref"].endswith("1976Gu1")


def test_gsf_inventory_and_one_table():
    idx = R.list_gsf_tables(R.RIPL4_ROOT)
    assert idx.filter(pl.col("archive") == "smlo_E1").height == 8980
    member = idx.filter(
        (pl.col("Z") == 92) & (pl.col("A") == 238) & (pl.col("archive") == "smlo_E1")
    )
    t = R.read_gsf_table(R.RIPL4_ROOT, "smlo_E1", member["member"][0])
    assert t.height == 300 and t.columns[0] == "E_mev" and "T=0.0" in t.columns


# --------------------------------------------------------------------------- fission


def test_empirical_fission_barriers():
    fe = R.read_fission_empirical(R.RIPL4_ROOT)
    assert fe.height == 77
    u = _row(fe, Z=92, A=238)
    assert u["Va_mev"] == pytest.approx(6.3) and u["dVa_mev"] == pytest.approx(0.2)
    assert u["hwa_mev"] == pytest.approx(1.0) and u["Vb_mev"] == pytest.approx(5.7)
    assert u["sym_a"] == "GA" and u["sym_b"] == "MA"
    hg = _row(fe, Z=80, A=196)
    assert hg["Va_mev"] == pytest.approx(16.9) and hg["Vb_mev"] is None
    assert R.read_fission_bskg3(R.RIPL4_ROOT).height == 2449
    assert R.read_fission_d1m(R.RIPL4_ROOT).height == 45
    assert R.read_fission_empire(R.RIPL4_ROOT).height == 76
    assert R.read_fission_wmm(R.RIPL4_ROOT, "actinides_inner").height == 75


# --------------------------------------------------------------------------- masses


def test_mass_models_present_and_u238():
    assert R.list_mass_models(R.RIPL4_ROOT) == ["ame20", "bskg3", "d1m", "frdm12", "hfb27", "ws4"]
    frdm = R.read_mass_table(R.RIPL4_ROOT, "frdm12")
    u = _row(frdm, Z=92, A=238)
    assert u["flag"] == 2 and u["mexp_mev"] == pytest.approx(47.31, abs=0.01)
    assert abs(u["mth_mev"] - u["mexp_mev"]) < 2.0
    assert not u["mexp_extrapolated"]
    ame = R.read_mass_table(R.RIPL4_ROOT, "ame20")
    assert ame.filter(pl.col("flag") == 1).height > 0  # extrapolated masses are flagged


# --------------------------------------------------------------------------- optical


def test_optical_index_and_potentials():
    idx = R.read_optical_index(R.RIPL4_ROOT)
    kd = _row(idx, iref=2405)
    assert kd["projectile"] == "n" and kd["Zmin"] == 13 and kd["Amax"] == 209
    entries, terms = R.read_optical_potentials(R.RIPL4_ROOT)
    assert entries.height == 589 and entries["parse_ok"].all()
    e = _row(entries, iref=2405)
    assert e["author"].startswith("A.J.Koning") and e["imodel"] == 0 and e["irel"] == 1
    kd_terms = terms.filter(pl.col("iref") == 2405)
    assert kd_terms.height == 5  # real/imag volume, imag surface, real/imag spin-orbit
    rv = kd_terms.filter(pl.col("term") == "real_volume").row(0, named=True)
    assert len(rv["rco"]) == 13 and len(rv["aco"]) == 13 and len(rv["pot"]) == 25
    assert 2405 in R.omp_irefs_for(entries, 26, 56)
    assert 2405 not in R.omp_irefs_for(entries, 92, 238)  # KD03 ends at A = 209
    cc = _row(entries, iref=2420)
    assert cc["imodel"] == 5 and cc["n_coupled_isotopes"] == 4


# --------------------------------------------------------------------------- join


def test_build_structure_params_known_rows():
    from data.ingest.build_structure import build_structure_params, load_ripl

    tabs = load_ripl(R.RIPL4_ROOT, "ripl3")
    recs = {r.key: r for r in build_structure_params(tabs)}
    assert len(recs) > 9000
    u239 = recs[(92, 147, 0)]  # compound of n + 238U carries the resonance labels
    assert u239.d0_ev.value == pytest.approx(20.3) and u239.d0_ev.source == Source.MEASURED
    assert u239.gamma_gamma_mev.value == pytest.approx(23.6)
    assert u239.s0.value == pytest.approx(1.03e-4)
    assert u239.ld_a is None  # 239U is not in the EGSM fit file
    assert "resonances=RIPL-3" in u239.source_version
    pu239 = recs[(94, 145, 0)]
    assert pu239.ld_model == "EGSM" and 18 < pu239.ld_a.value < 22
    assert pu239.ld_a.source == Source.MEASURED
    u238 = recs[(92, 146, 0)]
    assert u238.d0_ev.value == pytest.approx(3.5)  # = D0 of the n + 237U target, by convention
    assert u238.n_discrete_levels == 45 and u238.level_cutoff_mev == pytest.approx(1.38119)
    assert [b.index for b in u238.fission_barriers] == [1, 2]
    assert u238.fission_barriers[0].height_mev.value == pytest.approx(6.3)
    assert u238.fission_barriers[0].curvature_mev.value == pytest.approx(1.0)
    assert u238.fission_barriers[0].height_mev.source == Source.MEASURED
    assert len(u238.gdr) == 2 and u238.gdr[0].energy_mev.source == Source.MEASURED
    assert u238.omp_form == "RIPL-local" and 2420 in u238.omp_irefs
    fe56 = recs[(26, 30, 0)]
    assert fe56.omp_form == "KD03" and fe56.n_discrete_levels == 79
    assert fe56.ct_temperature_mev.value == pytest.approx(1.07035)
    assert fe56.discrete_spin_cutoff == pytest.approx(2.556)
    assert fe56.gdr[0].energy_mev.source == Source.SYSTEMATICS
    pb208 = recs[(82, 126, 0)]
    assert pb208.gdr[0].energy_mev.value == pytest.approx(13.37)
    assert pb208.fission_barriers[0].height_mev.value == pytest.approx(27.4)
    th230 = recs[(90, 140, 0)]  # BSkG3-only barrier rows are systematics
    assert th230.fission_barriers[0].height_mev.source == Source.MEASURED
    hfb_only = recs[(90, 110, 0)]
    assert hfb_only.fission_barriers[0].height_mev.source == Source.SYSTEMATICS
    # every record round-trips through Arrow
    table = StructureParams.to_arrow([u239, u238, fe56, pb208])
    back = StructureParams.from_arrow(table)
    assert back[0] == u239 and math.isclose(back[2].discrete_spin_cutoff, 2.556)
