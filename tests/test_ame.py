"""AME2020 parser: known values, column-position guards, internal consistency."""

import math

import numpy as np
import pytest

from data.ingest.ame import (
    AME_DIR,
    RCT1_QUANTITIES,
    RCT2_QUANTITIES,
    derived_separation_energies,
    load_ame,
    parse_rct_table,
)

pytestmark = pytest.mark.skipif(not AME_DIR.exists(), reason="raw/ame2020 not downloaded")


@pytest.fixture(scope="module")
def ame():
    return load_ame()


def row(ame, Z, A):
    r = ame[(ame["Z"] == Z) & (ame["A"] == A)]
    assert len(r) == 1
    return r.iloc[0]


def test_pb208_mass_excess(ame):
    r = row(ame, 82, 208)
    assert r["symbol"] == "Pb" and r["N"] == 126
    assert r["mass_excess_kev"] == pytest.approx(-21748.519, abs=0.001)
    assert r["mass_excess_unc_kev"] == pytest.approx(1.148, abs=0.001)
    assert not r["mass_excess_extrapolated"]
    assert r["binding_per_a_kev"] == pytest.approx(7867.4530, abs=0.001)
    assert r["atomic_mass_u"] == pytest.approx(207.976652005, abs=1e-8)


def test_fe56_mass_excess(ame):
    r = row(ame, 26, 56)
    assert r["mass_excess_kev"] == pytest.approx(-60607.163, abs=0.001)
    assert r["mass_excess_unc_kev"] == pytest.approx(0.268, abs=0.001)
    assert r["binding_per_a_kev"] == pytest.approx(8790.3563, abs=0.001)


def test_u235_mass_and_separation_energies(ame):
    r = row(ame, 92, 235)
    assert r["mass_excess_kev"] == pytest.approx(40918.782, abs=0.001)
    assert r["sn_kev"] == pytest.approx(5297.4952, abs=0.001)
    assert r["sp_kev"] == pytest.approx(6709.0586, abs=0.001)
    assert r["s2n_kev"] == pytest.approx(12142.9649, abs=0.001)
    assert r["s2p_kev"] == pytest.approx(12390.8022, abs=0.001)
    assert r["q_alpha_kev"] == pytest.approx(4678.0559, abs=0.001)
    assert r["q_beta_minus_kev"] == pytest.approx(-124.2619, abs=0.001)


def test_pb208_sn(ame):
    assert row(ame, 82, 208)["sn_kev"] == pytest.approx(7367.8686, abs=0.001)


def test_extrapolated_flag_and_star(ame):
    li3 = row(ame, 3, 3)  # 3Li: "28667#  2000#" -> extrapolated
    assert li3["mass_excess_extrapolated"]
    assert li3["mass_excess_kev"] == pytest.approx(28667.0)
    assert li3["mass_excess_unc_kev"] == pytest.approx(2000.0)
    h1 = row(ame, 1, 1)  # beta-decay energy is "*" for 1H
    assert math.isnan(h1["q_beta_minus_kev"])
    assert not h1["mass_excess_extrapolated"]


def test_counts_measured_vs_extrapolated(ame):
    n_meas = int((~ame["mass_excess_extrapolated"] & ame["mass_excess_kev"].notna()).sum())
    n_ext = int(ame["mass_excess_extrapolated"].sum())
    assert 2400 <= n_meas <= 2700  # AME2020: 2550
    assert 700 <= n_ext <= 1100  # AME2020: 1008
    assert len(ame) == n_meas + n_ext
    assert 3300 <= len(ame) <= 3700


def test_keys_unique_and_consistent(ame):
    assert not ame.duplicated(["Z", "N"]).any()
    assert (ame["A"] == ame["Z"] + ame["N"]).all()
    assert ame["Z"].min() == 0 and ame["Z"].max() >= 118


def test_separation_energies_agree_with_masses(ame):
    """S_n, S_p, S_2n, S_2p recomputed from mass excesses must match AME's rct columns to
    rounding on measured rows (the '#' rows are rounded to the keV in the mass file)."""
    d = derived_separation_energies(ame)
    for q in ("sn", "sp", "s2n", "s2p"):
        diff = (d[f"{q}_calc_kev"] - ame[f"{q}_kev"]).abs()
        meas = ~ame[f"{q}_extrapolated"] & ~ame["mass_excess_extrapolated"] & diff.notna()
        assert meas.sum() > 2000
        assert float(diff[meas].max()) < 0.01, q
        ext = diff.notna() & ~meas
        assert float(diff[ext].max()) < 2.0, q  # keV-rounded estimates


def test_rct_quantities_present(ame):
    for q in RCT1_QUANTITIES + RCT2_QUANTITIES:
        assert f"{q}_kev" in ame.columns and f"{q}_extrapolated" in ame.columns
    # every nuclide with a measured mass and a measured lighter isotope has S_n
    assert ame["sn_kev"].notna().sum() > 3000


def test_rct_parser_rejects_wrong_quantity_count():
    with pytest.raises(ValueError):
        parse_rct_table(AME_DIR / "rct1.mas20.txt", ("a", "b"))


def test_uncertainties_nonnegative(ame):
    for c in [c for c in ame.columns if c.endswith("_unc_kev")]:
        v = ame[c].to_numpy()
        assert np.nanmin(v) >= 0.0, c
