"""Scoring bug hunt round 2 (BUGSCORE2, 2026-11-07): one regression test per finding. Synthetic inputs only; no library
file, no curated table. Findings whose fix would change a published number or file are registered as amendment drafts
(docs/release/amendments/BUGSCORE2.md) and their tests are strict xfails until the amendment is adopted."""
from __future__ import annotations

import math

import numpy as np
import polars as pl
import pytest

from incognita.bench import binavg as BA
from incognita.bench import score as S
from incognita.eval import spectra as SP
from validation import differential as D
from validation.differential import core as DC

# ----------------------------------------------------------------------------------------------- 1, 2: load_exfor_points


def _cells(rows):
    base = dict(dataset_key="d1", group_key="g", nuclide="Z030N038M0", mt=107, kind="sig", state="", branch="", bin=150,
                n_pts=1, mean_b=0.01, ln_mean=math.log(0.01), stat_rel=0.05, sys_rel=0.05, sem_rel=0.05, e_lo_ev=1e6,
                e_hi_ev=1.2e6, trust=0.9, inflation=1.0, year=2000, decision="keep", usable=True)
    return pl.DataFrame([{**base, **r} for r in rows])


def _cons(rows):
    base = dict(group_key="g", nuclide="Z030N038M0", mt=107, branch="", kind="sig", state="", bin=150, e_lo_ev=1e6,
                e_hi_ev=1.2e6, e_mid_ev=1.1e6, consensus_b=0.01, consensus_log=math.log(0.01), sigma_log=0.1,
                spread_log=0.0, birge_ratio=1.0, chi2_ndf=1.0, n_datasets=1, n_points=1)
    return pl.DataFrame([{**base, **r} for r in rows])


def _load(tmp_path, monkeypatch, cells, cons, **kw):
    pc, pk = tmp_path / "cells.parquet", tmp_path / "cons.parquet"
    cells.write_parquet(pc)
    cons.write_parquet(pk)
    monkeypatch.setattr(DC.C, "cache_exfor_cells", lambda **_: pc)
    monkeypatch.setattr(DC, "VERBOSE_DROPS", False)
    return D.load_exfor_points(consensus_path=pk, mts=(107,), **kw)


def test_consensus_mode_drops_orphan_and_below_floor_bins(tmp_path, monkeypatch):
    """Item 1: consensus mode scored bins below the 1e-5 b channel floor (the cell cache excludes them, the consensus
    table keeps them) and gave bins with no usable dataset behind them a sentinel weight 1.0 at min_trust = 0."""
    cells = _cells([
        dict(dataset_key="ok", bin=150, mean_b=0.01),
        dict(dataset_key="tiny", bin=151, mean_b=3.8e-12, decision="exclude"),   # the floor marks it excluded
        dict(dataset_key="bad", bin=152, mean_b=0.02, decision="exclude"),       # excluded for another reason
    ])
    cons = _cons([dict(bin=150, consensus_b=0.01), dict(bin=151, consensus_b=3.8e-12), dict(bin=152, consensus_b=0.02)])
    pts = _load(tmp_path, monkeypatch, cells, cons, mode="consensus", channel="na")
    assert pts.frame["bin"].to_list() == [150]
    assert (pts.frame["weight"] == 0.9).all()
    d = D.LAST_EXFOR_LOAD_DROPS
    assert d["dropped_consensus_floor"] == 1 and d["dropped_consensus_no_surviving_dataset"] == 1


def test_fix_unit_cells_do_not_enter_unweighted_rows(tmp_path, monkeypatch):
    """Item 2: a fix-unit cell keeps its value as compiled (x1000) with trust 0; trust only silences it in weighted sums,
    and the datasets-mode rows (macs_constraint reads them unweighted) carried it."""
    cells = _cells([dict(dataset_key="ok", mean_b=0.3, kind="mxw"),
                    dict(dataset_key="unit", mean_b=300.0, kind="mxw", trust=0.0, decision="fix-unit")])
    pts = _load(tmp_path, monkeypatch, cells, _cons([dict(kind="mxw", consensus_b=0.3)]), mode="datasets",
                channel="capture", kinds=("mxw",))
    assert pts.frame["dataset_key"].to_list() == ["ok"]
    assert D.LAST_EXFOR_LOAD_DROPS["dropped_fix_unit"] == 1


# ----------------------------------------------------------------------------------------------- 3: interp_loglog

@pytest.mark.xfail(strict=True, reason="BUGSCORE2 amendment E (threshold rows of the point scorer): moves the ch-na "
                                       "ranking; not applied")
def test_interp_loglog_does_not_hold_the_threshold_value_flat():
    """Item 3: below the first positive point of a threshold curve the scorer returned that point's value (JENDL-5
    Ga-71 (n,2n) at 9.44 MeV, Mo-92 at 12.92 MeV). Between the last zero and the first positive point the curve ramps
    lin-lin; below the last zero point it is zero (row not covered). The top end keeps the last value."""
    x = np.array([1e6, 2e6, 3e6, 4e6, 5e6])
    y = np.array([0.0, 0.0, 0.1, 0.2, 0.3])
    assert math.isclose(S.interp_loglog(x, y, 3.5e6), math.exp(np.interp(math.log(3.5e6), np.log(x[2:]), np.log(y[2:]))))
    assert math.isclose(S.interp_loglog(x, y, 2.5e6), 0.05)
    assert S.interp_loglog(x, y, 1.5e6) == 0.0
    assert math.isclose(S.interp_loglog(x, y, 6e6), 0.3)        # above the table end: last value held (grid end)
    cur = S.Curves({(31, 71, 16): np.where(S.G >= 9.5e6, 0.05, 0.0)}, S.G)
    import pandas as pd
    T = pd.DataFrame({"Z": [31], "A": [71], "quantity": ["n2n"], "energy_ev": [9.0e6], "spectrum": [""]})
    assert np.isnan(S.predict(T, cur)[0])


# ----------------------------------------------------------------------------------------------- 4: SACS grid


def test_sacs_fold_covers_the_whole_fission_spectrum():
    """Item 4: the SACS integrals started at 100 keV. For sigma = c / sqrt(E) in a Maxwellian sqrt(E) exp(-E/T) the full
    average is c * 2 / sqrt(pi T); the 100 keV grid gave it 0.024 dex low."""
    e = S.G
    s_mb = 1e3 / np.sqrt(e / 1e6)                       # 1 b at 1 MeV, 1/v
    exact = 1e3 * 2 / math.sqrt(math.pi * 1.42)
    assert abs(math.log10(SP.fold(e, s_mb, "cf252") / exact)) < 1e-3
    assert abs(math.log10(SP.fold(e, s_mb, "cf252", ef=SP.OLD_EF) / exact) + 0.024) < 2e-3   # the bug, for the record


# ----------------------------------------------------------------------------------------------- 5: R11 frame


@pytest.mark.xfail(strict=True, reason="BUGSCORE2 amendment D (R11 centre-of-mass MACS): needs the curation register "
                                       "regenerated from the EXFOR master; not applied")
def test_r11_series_macs_is_centre_of_mass():
    """Item 5: R11 (MACSCHECK) Maxwellian-averaged the series curve in the lab frame. For sigma = c / sqrt(E_lab) the
    centre-of-mass MACS is c sqrt(A / ((A + 1) kT)), lower than the lab-frame value by 0.5 log10(1 + 1/A)."""
    from incognita.curation import rules
    a, kt = 56, 3e4
    e = np.geomspace(10.0, 3e6, 400)
    lo, hi = e / 1.01, e * 1.01
    macs, cov = rules.Engine.macs_over(lo, hi, e, 1.0 / np.sqrt(e), kt, a=a)
    assert cov > 0.99
    assert math.isclose(macs, math.sqrt(a / ((a + 1) * kt)), rel_tol=2e-3)


# ----------------------------------------------------------------------------------------------- 7: binavg vs score.py


def test_binavg_keeps_na_given_only_inside_mt5():
    """Amendment C (applied: no published row affected): a file with no MT 107 / 800-849 whose (n,a) is made inside MT 5 has an (n,a) curve for score.py
    (alpha.na_total) but none for binavg.channel_curves, so the dated tracks leave the row uncovered."""
    x = np.array([1e6, 5e6, 1e7, 2e7])
    pend = {5: (x, np.array([0.0, 0.1, 0.2, 0.2])), 102: (x, np.array([1e-3] * 4))}
    cur = BA.channel_curves(pend, [5, 102], mt5_na=(x, np.array([0.0, 0.01, 0.02, 0.02])))
    assert "na" in cur


def test_binavg_mt5_incomplete_rule_matches_the_scorer():
    """Amendment B (applied: no published row affected): score.py counts a row as comparator-incomplete only when the unread MT 5 part (bounded by sigma_5)
    may exceed 1 % of the value (alpha.is_incomplete); binavg blanks the (n,a) curve wherever sigma_5 > 0."""
    x = np.array([1e6, 5e6, 1e7, 2e7])
    pend = {107: (x, np.array([0.0, 0.1, 0.1, 0.1])), 5: (x, np.array([0.0, 1e-5, 1e-5, 1e-5]))}
    cur = BA.channel_curves(pend, [5, 107], mt5_na=("incomplete", x, pend[5][1]))
    assert np.isfinite(cur["na"][1]).all()


# ----------------------------------------------------------------------------------------------- 8: TENDL-Y


def test_tendl_y_uses_the_release_year():
    """Item 8 (amendment A): capture-retro's TENDL-Y entry chose the release by the year in its name; TENDL-2023 was
    released in 2024 and TENDL-2015 in 2016 (DATED_Y), so neither is a retrodiction at Y = 2023 / 2015."""
    cy = np.array([2015, 2016, 2021, 2023, 2024])
    preds = {k: np.full(5, float(yr)) for yr, k in S.TENDL_DATED}
    v = S.tendl_y(cy, preds)
    assert np.isnan(v[0])
    assert v[1:].tolist() == [2015.0, 2021.0, 2021.0, 2023.0]
