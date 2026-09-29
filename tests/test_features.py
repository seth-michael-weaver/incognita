import numpy as np
import pytest

from physics.features import FEATURE_NAMES, feature_matrix, feature_table


def test_pb208_is_doubly_magic():
    t = feature_table(82, 126)
    assert t["Z_is_magic"][0] == 1 and t["N_is_magic"][0] == 1
    assert t["Z_valence"][0] == 0 and t["N_valence"][0] == 0
    assert t["casten_P"][0] == 0.0


def test_valence_counts_midshell():
    # 154Sm: Z=62 (12 above 50, 20 below 82) N=92 (10 above 82)
    t = feature_table(62, 92)
    assert t["Z_particles"][0] == 12 and t["Z_holes"][0] == 20 and t["Z_valence"][0] == 12
    assert t["N_particles"][0] == 10 and t["N_valence"][0] == 10
    assert abs(t["casten_P"][0] - 12 * 10 / 22) < 1e-12


def test_liquid_drop_reasonable():
    # 56Fe binding ~ 492 MeV; LDM within ~1%
    t = feature_table(26, 30)
    assert abs(t["ld_binding"][0] - 492.25) < 6


def test_matrix_shape():
    m = feature_matrix([1, 2, 92], [0, 2, 146])
    assert m.shape == (3, len(FEATURE_NAMES))
    assert np.isfinite(m).all()


@pytest.mark.needs_main("staging/structure_params.parquet")
def test_resonance_parameters_come_from_the_compound_not_the_target():
    """RIPL indexes D0 and Gamma_gamma by the compound; capture on (Z,N) forms (Z,N+1).

    Keying on the target instead returns the neighbouring system's parameters without
    failing: before 2026-09-10 U-238 was fed D0 = 3.5 eV instead of 20.3 and Ta-181 got
    1.2 instead of 4.2, both flagged 'measured', while Au-197 and Fe-56 -- whose own (Z,N)
    is absent from the table -- got nothing at all. Anchored on literature values so the
    test fails if the lookup ever slides back by a neutron.
    """
    from models.stage_c_data import compound_id, resonance_features

    assert compound_id("Z079N118M0") == "Z079N119M0"

    # (target id, literature D0 of the compound in eV)
    cases = [("Z079N118M0", 15.5), ("Z026N030M0", 25400.0), ("Z092N146M0", 20.3),
             ("Z073N108M0", 4.2)]
    ids = [nid for nid, _ in cases]
    out = resonance_features(ids)
    # columns: log-scaled d0, gamma_gamma, s0, then one present-flag each
    for i, (nid, d0_lit) in enumerate(cases):
        assert out[i, 3] == 1.0, f"{nid}: D0 should be present via the compound"
        d0 = 10 ** (out[i, 0] * 3.0 + 3.0)          # invert (log10(v) - 3.0) / 3.0
        assert np.isclose(d0, d0_lit, rtol=0.02), f"{nid}: D0 {d0:.3g} != {d0_lit}"


@pytest.mark.needs_main("staging/structure_params.parquet")
def test_urr_norm_is_the_capture_normalisation_and_only_where_both_are_measured():
    """2*pi*Gamma_gamma/D0 sets the average capture cross section above the resolved region."""
    from models.stage_c_data import urr_norm_features

    out = urr_norm_features(["Z079N118M0", "Z001N000M0"])
    assert out[0, 1] == 1.0 and out[1, 1] == 0.0, "flag must mark where the ratio is real"
    ratio = 10 ** (out[0, 0] * 2.0 - 2.0)
    # Au-197: Gamma_gamma ~ 128 meV, D0 ~ 15.5 eV -> 2*pi*0.128/15.5 ~ 0.052
    assert 0.02 < ratio < 0.12, ratio
    assert out[1, 0] == 0.0, "absent must encode as zero, not as a fabricated ratio"


def test_deformation_columns_are_physical_not_fill_values():
    """No beta2 column may carry a fill value dressed as a number.

    HFB-27 records -99.999 for Ir-180 where it has no shape. Because that is a NUMBER and not
    NaN it passed every missing-data check in the project -- polars `null_count()` is 0 for the
    whole feature table, and models/data.py standardises with nanmean/nanstd, which skips NaN
    and not this. The single cell inflated that column's standard deviation 8.8x (0.194 ->
    1.713), so the standardised feature handed to the encoder spanned +-0.29 instead of +-2.4:
    3,557 nuclides lost about nine tenths of the signal to one bad row.

    A quadrupole deformation is bounded; the tables run about -0.4 to +0.7. |beta2| > 1 is not
    a shape.
    """
    import pathlib

    import polars as pl
    import pytest

    path = pathlib.Path(__file__).resolve().parents[1] / "features" / "nuclide_features.parquet"
    if not path.exists():
        pytest.skip("nuclide_features.parquet not present in this checkout")
    df = pl.read_parquet(path)
    offenders = {}
    for col in (c for c in df.columns if c.startswith("beta2_")):
        v = df[col].to_numpy().astype(float)
        bad = np.abs(v) > 1.0          # NaN compares False, so genuine gaps are ignored
        if bad.any():
            offenders[col] = sorted({float(x) for x in v[bad]})[:5]
    assert not offenders, f"deformation columns carry fill values: {offenders}"
