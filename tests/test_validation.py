"""WP-16 differential harness: metrics recover a known offset, RRR exclusion, MACS analytics,
coverage math, the prediction contract round trip, and the EXFOR / covariance paths on
synthetic inputs (no staging data needed)."""

from __future__ import annotations

import math

import numpy as np
import polars as pl
import pytest

from physics.grid import ENERGY_GRID_EV as G
from validation import cache as VC
from validation import differential as D

LOG10E = math.log10(math.e)


def _flat(nid="Z050N070M0", mt=102, value=1.0, unc=None, **kw) -> D.Prediction:
    s = np.full(G.size, value)
    u = None if unc is None else np.full(G.size, unc)
    return D.Prediction(nid, mt, G, s, u, **kw)


# ----------------------------------------------------------------------------- point metrics


def test_point_metrics_recover_known_offset():
    ref = np.logspace(-2, 2, 500)
    pred = ref * 10**0.3  # +0.3 dex everywhere
    m = D.point_metrics(pred, ref)
    assert m["n"] == 500
    assert m["rms_log10"] == pytest.approx(0.3, abs=1e-12)
    assert m["median_abs_log10"] == pytest.approx(0.3, abs=1e-12)
    assert m["bias_log10"] == pytest.approx(0.3, abs=1e-12)
    assert m["median_rel_err"] == pytest.approx(10**0.3 - 1, rel=1e-12)
    assert math.isnan(m["cov_1s"]) and m["n_unc"] == 0  # no uncertainties given


def test_point_metrics_weights_and_bad_points():
    ref = np.ones(6)
    pred = np.array([10.0, 1.0, 1.0, np.nan, -1.0, 1.0])  # NaN / negative dropped
    w = np.array([1.0, 0.0, 0.0, 5.0, 5.0, 0.0])
    m = D.point_metrics(pred, ref, weights=w)
    assert m["n"] == 4
    assert m["rms_log10"] == pytest.approx(0.5)
    assert m["rms_log10_w"] == pytest.approx(1.0)  # only the offset point has weight


def test_coverage_math():
    rng = np.random.default_rng(0)
    ref = np.full(20000, 5.0)
    unc = np.full(20000, 0.5)
    pred = ref + rng.normal(0.0, 0.5, size=ref.size)
    m = D.point_metrics(pred, ref, pred_unc=unc)
    assert m["n_unc"] == 20000
    assert m["cov_1s"] == pytest.approx(0.6827, abs=0.01)
    assert m["cov_2s"] == pytest.approx(0.9545, abs=0.006)
    assert m["chi2_ndf"] == pytest.approx(1.0, abs=0.03)
    # combined: pred and ref uncertainties add in quadrature
    m2 = D.point_metrics(pred, ref, pred_unc=unc * 0, ref_unc=unc)
    assert m2["cov_1s"] == pytest.approx(m["cov_1s"])
    # stated uncertainty twice too small -> coverage falls to ~38 %
    m3 = D.point_metrics(pred, ref, pred_unc=unc / 2)
    assert m3["cov_1s"] == pytest.approx(0.3829, abs=0.012)


def test_chi2_with_covariance_matches_diagonal_and_handles_rank():
    d = np.array([0.1, -0.2, 0.05])
    cov = np.diag([0.01, 0.04, 0.0025])
    chi2, ndf = D.chi2_with_covariance(d, cov)
    assert ndf == 3
    assert chi2 == pytest.approx(np.sum(d**2 / np.diag(cov)))
    # fully correlated block (rank 1): a common scale factor costs one degree of freedom
    full = np.full((3, 3), 0.01)
    chi2, ndf = D.chi2_with_covariance(np.full(3, 0.1), full)
    assert ndf == 1
    assert chi2 == pytest.approx(1.0)


# ----------------------------------------------------------------------------- MACS


def test_macs_of_1_over_v_equals_sigma_at_kT():
    kT = 30e3
    sigma0, E0 = 3.0, 1e3
    s = sigma0 * np.sqrt(E0 / G)
    macs, cov = D.maxwellian_average(G, s, kT)
    assert cov == pytest.approx(1.0)
    assert macs == pytest.approx(sigma0 * np.sqrt(E0 / kT), rel=1e-6)


def test_macs_of_constant_is_2_over_sqrt_pi():
    macs, _ = D.maxwellian_average(G, np.full(G.size, 2.0), 30e3)
    assert macs == pytest.approx(2.0 * 2.0 / math.sqrt(math.pi), rel=1e-9)


def test_macs_1v_extrapolation_and_coverage():
    kT = 30e3
    s = 3.0 * np.sqrt(1e3 / G)
    s[G < 1e3] = np.nan  # a TALYS-style prediction that starts at 1 keV
    macs, cov = D.maxwellian_average(G, s, kT)
    assert 0.99 < cov < 1.0
    assert macs == pytest.approx(3.0 * np.sqrt(1e3 / kT), rel=1e-6)  # 1/v fill is exact here
    macs_nofill, _ = D.maxwellian_average(G, s, kT, extrapolate_1v=False)
    assert macs_nofill < macs


def test_macs_table_cm_correction_direction():
    # a 1/v curve tabulated in lab energy: E_cm = E_lab A/(A+1) < E_lab, so σ(E_cm) is larger
    ps = D.PredictionSet([D.Prediction("Z026N030M0", 102, G, np.sqrt(1e3 / G))])
    with_cm = D.macs_table(ps, (30.0,), cm_correction=True)["macs_mb"][0]
    no_cm = D.macs_table(ps, (30.0,), cm_correction=False)["macs_mb"][0]
    # E_cm = E_lab·A/(A+1): the σ tabulated at a lab energy belongs to a lower cm energy,
    # so read at a given E_cm the 1/v curve is smaller by sqrt(A/(A+1)) and so is the MACS
    assert with_cm < no_cm
    assert with_cm / no_cm == pytest.approx(math.sqrt(56 / 57), rel=1e-6)


# ----------------------------------------------------------------------------- vs library


class _FakeLib:
    """Duck-typed reference with one nuclide: flat 1 b, RRR to 1 keV, URR to 100 keV,
    a two-bin MF33 block (10 % uncorrelated) above the RRR."""

    name = "FAKE"
    version = "fake-0"

    def __init__(self, value=1.0, rrr=1e3, urr=1e5, cov=True):
        self.value, self.rrr, self.urr, self.cov = value, rrr, urr, cov

    def has(self, nid, mt):
        return nid == "Z050N070M0" and mt == 102

    def curve(self, nid, mt):
        return np.full(G.size, self.value), self.rrr, self.urr

    def rel_unc_on_grid(self, nid, mt, grid=G):
        if not self.cov:
            return None
        rel = np.full(len(grid), np.nan)
        rel[grid > self.rrr] = 0.1
        return rel

    def covariance(self, nid, mt):
        if not self.cov:
            return None
        bounds = np.array([self.rrr, self.urr, 20e6])
        return bounds, np.diag([0.01, 0.01])


def test_compare_to_library_rrr_exclusion_and_regions():
    lib = _FakeLib()
    # prediction: +0.2 dex above 1 keV, wildly wrong (x100) inside the RRR
    s = np.where(G > 1e3, 10**0.2, 100.0)
    ps = D.PredictionSet([D.Prediction("Z050N070M0", 102, G, s)])
    rows = D.compare_to_library(ps, lib)
    by = {r["region"]: r for r in rows.iter_rows(named=True)}
    assert set(by) == {"above_rrr", "urr", "fast"}
    for r in by.values():
        assert r["rms_log10"] == pytest.approx(0.2, abs=1e-9)  # RRR junk never counted
    assert by["above_rrr"]["e_lo_ev"] > 1e3
    assert by["urr"]["e_hi_ev"] <= 1e5 < by["fast"]["e_lo_ev"]
    assert by["above_rrr"]["n"] == by["urr"]["n"] + by["fast"]["n"]
    # with the reference's 10 % error bar a +58 % offset is ~5.8σ: coverage 0, χ² large
    assert by["fast"]["cov_2s"] == 0.0
    assert by["fast"]["chi2_ndf"] > 20
    assert by["above_rrr"]["cov_ndf"] == 2
    assert by["above_rrr"]["chi2_cov_ndf"] == pytest.approx((10**0.2 - 1) ** 2 / 0.01, rel=1e-6)


def test_compare_to_library_prediction_own_rrr_bound_is_respected():
    lib = _FakeLib(rrr=1e3)
    s = np.where(G > 5e4, 1.0, 1e3)  # garbage below 50 keV, but the prediction declares it RRR
    ps = D.PredictionSet([D.Prediction("Z050N070M0", 102, G, s, rrr_upper_ev=5e4)])
    rows = D.compare_to_library(ps, lib)
    r = rows.filter(pl.col("region") == "above_rrr").row(0, named=True)
    assert r["rms_log10"] == pytest.approx(0.0, abs=1e-12)
    assert r["rrr_upper_ev"] == 5e4


def test_aggregate_library_rows_pools_by_points():
    lib = _FakeLib(cov=False)
    ps = D.PredictionSet([D.Prediction("Z050N070M0", 102, G, np.full(G.size, 10**0.1))])
    agg = D.aggregate_library_rows(D.compare_to_library(ps, lib), ["region"])
    assert agg.height == 3
    row = agg.filter(pl.col("region") == "above_rrr").row(0, named=True)
    assert row["rms_log10_pooled"] == pytest.approx(0.1, abs=1e-9)
    assert row["n_with_cov"] == 0
    assert row["cov_1s"] is None or math.isnan(row["cov_1s"])


# ----------------------------------------------------------------------------- vs EXFOR


def _points(rows: list[dict], mode="consensus") -> D.ExforPoints:
    base = {
        "mt": 102,
        "kind": "sig",
        "bin": 0,
        "sigma_log10": 0.05 * LOG10E,
        "weight": 1.0,
        "n_datasets": 1,
        "n_points": 3,
        "dataset_key": None,
        "year": 2000,
        "trust": 0.9,
    }
    recs = []
    for i, r in enumerate(rows):
        rec = base | {"bin": i} | r
        rec["e_mid_ev"] = math.sqrt(rec["e_lo_ev"] * rec["e_hi_ev"])
        recs.append(rec)
    schema = {
        "nuclide_id": pl.Utf8,
        "mt": pl.Int32,
        "kind": pl.Utf8,
        "bin": pl.Int32,
        "e_lo_ev": pl.Float64,
        "e_hi_ev": pl.Float64,
        "e_mid_ev": pl.Float64,
        "meas_b": pl.Float64,
        "sigma_log10": pl.Float64,
        "weight": pl.Float64,
        "n_datasets": pl.Int32,
        "n_points": pl.Int64,
        "dataset_key": pl.Utf8,
        "year": pl.Int64,
        "trust": pl.Float64,
    }
    return D.ExforPoints(pl.DataFrame(recs, schema=schema), mode=mode)


def test_compare_to_exfor_recovers_offset_and_excludes_rrr():
    ps = D.PredictionSet([_flat(value=2.0)])
    pts = _points(
        [
            {"nuclide_id": "Z050N070M0", "e_lo_ev": 10.0, "e_hi_ev": 12.6, "meas_b": 50.0},  # RRR
            {"nuclide_id": "Z050N070M0", "e_lo_ev": 1e4, "e_hi_ev": 1.26e4, "meas_b": 1.0},
            {
                "nuclide_id": "Z050N070M0",
                "e_lo_ev": 1e5,
                "e_hi_ev": 1.26e5,
                "meas_b": 1.0,
                "weight": 3.0,
            },
            {"nuclide_id": "Z050N070M0", "e_lo_ev": 1e6, "e_hi_ev": 1.26e6, "meas_b": 4.0},
        ]
    )
    sc = D.compare_to_exfor(ps, pts, rrr={"Z050N070M0": 1e3})
    assert sc.height == 4
    assert sc["above_rrr"].to_list() == [False, True, True, True]
    assert sc["pred_b"].to_numpy() == pytest.approx(2.0)
    s = D.summarize_exfor(sc).row(0, named=True)
    assert s["n"] == 3
    lr = np.log10(np.array([2.0, 2.0, 0.5]))
    assert s["rms_log10"] == pytest.approx(np.sqrt(np.mean(lr**2)))
    w = np.array([1.0, 3.0, 1.0])
    assert s["rms_log10_w"] == pytest.approx(np.sqrt(np.sum(w * lr**2) / w.sum()))
    assert s["cov_1s"] == 0.0  # 5 % error bars vs a factor 2: nothing is covered
    s_all = D.summarize_exfor(sc, above_rrr_only=False).row(0, named=True)
    assert s_all["n"] == 4


def test_bin_prediction_averages_inside_bin_and_interpolates_narrow_bins():
    p = D.Prediction("Z050N070M0", 102, G, np.sqrt(1e3 / G))
    e_lo = np.array([1e4, 2.0e4])
    e_hi = np.array([1.26e4, 2.0e4 * 1.0001])  # second bin narrower than the grid spacing
    pb, pu = D.bin_prediction(p, e_lo, e_hi)
    assert pu.tolist() == pytest.approx([np.nan, np.nan], nan_ok=True)
    mid = math.sqrt(e_lo[1] * e_hi[1])
    assert pb[1] == pytest.approx(np.sqrt(1e3 / mid), rel=1e-6)
    assert np.sqrt(1e3 / 1.26e4) < pb[0] < np.sqrt(1e3 / 1e4)


# ----------------------------------------------------------------------------- contract


def test_prediction_parquet_round_trip(tmp_path):
    unc = np.full(G.size, 0.1)
    ps = D.PredictionSet(
        [
            D.Prediction("Z050N070M0", 102, G, np.full(G.size, 1.5), unc, 1e3, 1e5, "x"),
            D.Prediction("Z050N072M0", 102, np.array([1e3, 1e6]), np.array([2.0, 0.5])),
        ],
        label="synthetic",
    )
    path = ps.to_parquet(tmp_path / "pred.parquet")
    back = D.PredictionSet.from_parquet(path)
    assert set(back) == set(ps)
    q = back[("Z050N070M0", 102)]
    assert q.rrr_upper_ev == 1e3 and q.urr_upper_ev == 1e5
    assert q.sigma_unc_b is not None and q.sigma_unc_b[0] == 0.1
    r = back[("Z050N072M0", 102)]
    assert r.sigma_unc_b is None
    s, _ = r.on_grid()
    assert np.isnan(s[0]) and np.isnan(s[-1])  # outside the tabulated range


def test_grid_id_parquet_and_bad_grid(tmp_path):
    from physics.grid import GRID_ID

    df = pl.DataFrame(
        {
            "nuclide_id": ["Z026N030M0"],
            "mt": [102],
            "grid_id": [GRID_ID],
            "sigma_b": [np.ones(G.size).tolist()],
        }
    )
    df.write_parquet(tmp_path / "g.parquet")
    ps = D.PredictionSet.from_parquet(tmp_path / "g.parquet")
    assert ps[("Z026N030M0", 102)].energy_ev is G or np.allclose(
        ps[("Z026N030M0", 102)].energy_ev, G
    )
    df.with_columns(grid_id=pl.lit("other")).write_parquet(tmp_path / "bad.parquet")
    with pytest.raises(ValueError):
        D.PredictionSet.from_parquet(tmp_path / "bad.parquet")


def test_from_callable_and_subset():
    def fn(nid, mt, e):
        return np.full(e.size, 0.5), np.full(e.size, 0.05)

    ps = D.PredictionSet.from_callable(fn, ["Z026N030M0", "Z092N146M0"], label="cb")
    assert len(ps) == 2 and ps[("Z092N146M0", 102)].sigma_unc_b is not None
    assert ps.subset(nuclides=["Z026N030M0"]).nuclides == ["Z026N030M0"]


def test_mass_region_and_ids():
    assert D.mass_region(26, 56) == "Fe-Sn"
    assert D.mass_region(50, 120) == "Fe-Sn"
    assert D.mass_region(51, 121) == "Sn-Pb"
    assert D.mass_region(82, 208) == "Sn-Pb"
    assert D.mass_region(92, 238) == "actinide"
    assert D.mass_region(8, 16) == "light"
    assert D.parse_nuclide_id(D.nuclide_id(79, 118)) == (79, 118, 0)
    with pytest.raises(ValueError):
        D.parse_nuclide_id("Au197")


# ----------------------------------------------------------------------------- KADoNiS


def test_compare_to_kadonis_with_synthetic_table():
    kad = pl.DataFrame(
        {
            "nuclide_id": ["Z050N070M0", "Z050N070M0"],
            "kT_keV": [30.0, 100.0],
            "kadonis_mb": [100.0, 50.0],
            "kadonis_err_mb": [10.0, None],
        }
    )
    # flat 0.1 b -> MACS = 2/sqrt(pi) * 100 mb = 112.8 mb at every kT
    ps = D.PredictionSet([_flat(value=0.1, unc=0.01)])
    sc = D.compare_to_kadonis(ps, (30.0, 100.0), kadonis=kad)
    assert sc.height == 2
    r30 = sc.filter(pl.col("kT_keV") == 30.0).row(0, named=True)
    assert r30["macs_mb"] == pytest.approx(200 / math.sqrt(math.pi), rel=1e-6)
    assert r30["macs_unc_mb"] == pytest.approx(20 / math.sqrt(math.pi), rel=1e-6)
    expected_z = abs(r30["macs_mb"] - 100) / math.sqrt(10**2 + r30["macs_unc_mb"] ** 2)
    assert r30["z"] == pytest.approx(expected_z)
    s = D.summarize_macs(sc, ["kT_keV"])
    assert s.height == 2


# ------------------------------------------------------------------- drop accounting (WP-16 audit)
#
# "Every filter here prints its drop tally, because a silent filter is indistinguishable from
# a correct one" (docs/failure-modes.md). These pin the tallies to the arithmetic they claim,
# so a future filter that quietly removes rows shows up as a test failure rather than as a
# slightly better RMS.


def test_compare_to_exfor_accounts_for_every_row_it_drops():
    ps = D.PredictionSet(
        # covers 1 keV upward only: the thermal bin below is outside its range
        [
            D.Prediction(
                "Z050N070M0",
                102,
                G,
                np.where(G >= 1e3, 2.0, np.nan),
            )
        ],
        label="drop-probe",
    )
    pts = _points(
        [
            {"nuclide_id": "Z050N070M0", "e_lo_ev": 1.0, "e_hi_ev": 1.26, "meas_b": 50.0},
            {"nuclide_id": "Z050N070M0", "e_lo_ev": 1e4, "e_hi_ev": 1.26e4, "meas_b": 1.0},
            {"nuclide_id": "Z050N070M0", "e_lo_ev": 1e6, "e_hi_ev": 1.26e6, "meas_b": 1.0},
            # a nuclide the prediction does not carry
            {"nuclide_id": "Z050N071M0", "e_lo_ev": 1e4, "e_hi_ev": 1.26e4, "meas_b": 1.0},
        ]
    )
    sc = D.compare_to_exfor(ps, pts, rrr={"Z050N070M0": 1e3, "Z050N071M0": 1e3})
    d = D.LAST_EXFOR_SCORE_DROPS
    assert d["rows_in"] == 4
    assert d["dropped_other_mt"] == 0
    assert d["rows_on_prediction"] == 3
    assert d["dropped_no_prediction_nuclide"] == 1
    assert d["dropped_pred_not_finite"] == 1  # the 1 eV bin: prediction is NaN there
    assert d["rows_scored"] == sc.height == 2
    assert d["rows_above_rrr"] == 2
    # the tally has to close: nothing may vanish without a counter
    assert (
        d["rows_in"]
        == d["rows_scored"]
        + d["dropped_other_mt"]
        + d["dropped_no_prediction_nuclide"]
        + d["dropped_pred_not_finite"]
    )
    assert d["nuclides_without_rrr_bound"] == 0


def test_compare_to_exfor_counts_nuclides_with_no_rrr_bound():
    """A nuclide missing from the bound map is read as "resolved region ends at 0 eV", so
    every bin of it -- thermal resonances included -- is scored as ``above_rrr``. That is
    failure-mode §2; the count must be reported rather than left silent."""
    ps = D.PredictionSet([_flat(value=2.0)], label="no-bound-probe")
    pts = _points(
        [
            {"nuclide_id": "Z050N070M0", "e_lo_ev": 1.0, "e_hi_ev": 1.26, "meas_b": 50.0},
            {"nuclide_id": "Z050N070M0", "e_lo_ev": 1e4, "e_hi_ev": 1.26e4, "meas_b": 1.0},
        ]
    )
    sc = D.compare_to_exfor(ps, pts, rrr={})  # no bound known for this nuclide
    assert sc["above_rrr"].to_list() == [True, True]  # the thermal bin too — that is the trap
    d = D.LAST_EXFOR_SCORE_DROPS
    assert d["nuclides_without_rrr_bound"] == 1
    assert d["rows_without_rrr_bound"] == 2
    # and a known bound leaves the counter at zero
    D.compare_to_exfor(ps, pts, rrr={"Z050N070M0": 1e3})
    assert D.LAST_EXFOR_SCORE_DROPS["nuclides_without_rrr_bound"] == 0


def test_compare_to_exfor_tally_survives_an_empty_intersection():
    ps = D.PredictionSet([_flat(value=2.0)], label="empty-probe")
    pts = _points([{"nuclide_id": "Z050N071M0", "e_lo_ev": 1e4, "e_hi_ev": 1.26e4, "meas_b": 1.0}])
    sc = D.compare_to_exfor(ps, pts, rrr={})
    assert sc.height == 0
    assert D.LAST_EXFOR_SCORE_DROPS["rows_in"] == 1
    assert D.LAST_EXFOR_SCORE_DROPS["rows_scored"] == 0


def test_summarize_exfor_reports_nothing_rather_than_zero_on_an_empty_slice():
    """A slice with no cells must not score 0.0 -- a perfect-looking region made of no data."""
    ps = D.PredictionSet([_flat(value=2.0)])
    pts = _points(
        [{"nuclide_id": "Z050N070M0", "e_lo_ev": 10.0, "e_hi_ev": 12.6, "meas_b": 1.0}]  # in RRR
    )
    sc = D.compare_to_exfor(ps, pts, rrr={"Z050N070M0": 1e3})
    assert sc.height == 1 and not sc["above_rrr"][0]
    out = D.summarize_exfor(sc)  # above_rrr_only=True leaves nothing
    assert out.height == 0  # not a row of zeros


# --------------------------------------------------------- real-data pins (skipped without cache)

_CELLS = VC.cells_cache_path("capture")
_CONS = VC.channel_consensus("capture")
needs_exfor = pytest.mark.skipif(
    not (_CELLS.is_file() and _CONS.is_file()), reason="WP-12 curated capture tables not built"
)


@needs_exfor
def test_load_exfor_points_tally_closes():
    pts = D.load_exfor_points(mts=(102,))
    d = D.LAST_EXFOR_LOAD_DROPS
    assert d["mode"] == "consensus"
    assert d["cells_total"] == d["cells_after_quantity"] + d["dropped_quantity"]
    assert d["cells_after_quantity"] == d["cells_after_curation"] + d["dropped_curation"]
    assert d["cells_after_curation"] == d["cells_after_trust"] + d["dropped_trust"]
    assert d["consensus_total"] == d["consensus_after_quantity"] + d["dropped_consensus_quantity"]
    assert d["rows"] == pts.frame.height
    # the kind/state/branch selection is the defence against failure-mode §5 and it is not a
    # no-op: the curated table carries quantities that are not the total cross section
    assert d["dropped_quantity"] > 0


@needs_exfor
def test_consensus_min_trust_demotes_rather_than_promotes():
    """``min_trust`` used to reweight rather than filter in consensus mode: a bin whose every
    dataset fell below the cut lost its join and was filled with weight 1.0, *above* the
    median real weight -- so raising the cut promoted exactly the bins it was asked to drop.
    The default (0.0) must be untouched by the fix."""
    base = D.load_exfor_points(mts=(102,))
    assert D.LAST_EXFOR_LOAD_DROPS["consensus_bins_without_cells"] == 0
    strict = D.load_exfor_points(mts=(102,), min_trust=0.3)
    assert strict.frame.height < base.frame.height  # it must actually remove bins
    # and it must never invent a sentinel weight for a bin it just emptied
    assert (strict.frame["weight"] == 1.0).sum() == 0
    assert strict.frame["weight"].min() > 0
