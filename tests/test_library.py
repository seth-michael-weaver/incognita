import hashlib

import numpy as np
import pandas as pd
import pytest

from incognita import library as L


def test_nuclide_id_parsing():
    assert L.nuclide_id("Fe-56") == "Z026N030M0"
    assert L.nuclide_id("fe56") == "Z026N030M0"
    assert L.nuclide_id("197Au") == "Z079N118M0"
    assert L.nuclide_id("Z026N030M0") == "Z026N030M0"
    with pytest.raises(ValueError):
        L.nuclide_id("Xx-12")


def test_library_checksums():
    sums = (L.LIBRARY / "SHA256SUMS").read_text().split("\n")
    for line in filter(None, sums):
        digest, name = line.split(maxsplit=1)
        assert hashlib.sha256((L.LIBRARY / name.strip()).read_bytes()).hexdigest() == digest, name


def test_capture_table_shape_and_tiers():
    t = L.load_capture()
    assert t.nuclide_id.is_unique
    assert set(t.tier) <= set(L.TIERS)
    e = np.asarray(t.energy_ev.iloc[0], float)
    assert e.min() == pytest.approx(1e3) and e.max() == pytest.approx(2e7)
    assert "anchor_macs30_mb" not in t.columns  # third-party compilation values are not redistributed


def test_capture_curve_bands_are_ordered():
    c = L.capture_curve("Fe-56")
    ok = np.isfinite(c.sigma_b) & (c.sigma_b > 0)
    assert ok.any()
    c = c[ok]
    assert (c.lo95_b <= c.lo68_b).all() and (c.lo68_b <= c.sigma_b).all()
    assert (c.sigma_b <= c.hi68_b).all() and (c.hi68_b <= c.hi95_b).all()


def test_v02_reads_and_bands_are_ordered():
    t = L.load_capture(version="v0.2")
    assert t.nuclide_id.is_unique and set(t.tier) <= set(L.TIERS)
    c = L.capture_curve("Fe-56", table=t)
    assert (c.lo95_b <= c.lo68_b).all() and (c.lo68_b <= c.sigma_b).all()
    assert (c.sigma_b <= c.hi68_b).all() and (c.hi68_b <= c.hi95_b).all()
    with pytest.raises(ValueError):
        L.load_capture(version="v9")


def test_v021_cm_macs_and_unchanged_curves():
    """v0.2.1: MACS in the centre-of-mass frame; only the 21 ANCHORED curves differ from v0.2."""
    t1, t2 = L.load_capture(version="v0.2.1"), L.load_capture(version="v0.2")
    assert list(t1.nuclide_id) == list(t2.nuclide_id) and (t1.tier.values == t2.tier.values).all()
    diff = [n for n, a, b in zip(t1.nuclide_id, t1.sigma_b, t2.sigma_b) if not np.array_equal(np.asarray(a), np.asarray(b))]
    assert set(diff) == set(t1.nuclide_id[t1.tier == "ANCHORED"])
    # macs30_mb is the centre-of-mass Maxwellian average of the shipped curve (1/v below the 1 keV grid start)
    for nid in ("Z008N008M0", "Z079N118M0"):
        r = t1[t1.nuclide_id == nid].iloc[0]
        e, sb, A, kt = np.asarray(r.energy_ev, float), np.asarray(r.sigma_b, float), int(r.A), 3e4
        g = np.exp(np.linspace(np.log(1e-6), np.log(e[-1] * A / (A + 1)), 400_001)); el = g * (A + 1) / A
        ls = np.where(el < e[0], np.log(sb[0]) + 0.5 * np.log(e[0] / el), np.interp(np.log(el), np.log(e), np.log(sb)))
        m = 2 / np.sqrt(np.pi) * np.trapezoid(np.exp(ls) * g * g * np.exp(-g / kt), np.log(g)) / kt ** 2 * 1e3
        assert r.macs30_mb == pytest.approx(m, rel=1e-6)


def test_v022_engine_below_1kev_and_reduced_mass():
    """v0.2.2: the engine's own capture below 1 keV joins the v0.2 curve; rates use mu = m_n M / (m_n + M)."""
    t3, t2 = L.load_capture(version="v0.2.2"), L.load_capture(version="v0.2")
    assert list(t3.nuclide_id) == list(t2.nuclide_id) and (t3.tier.values == t2.tier.values).all()
    diff = [n for n, a, b in zip(t3.nuclide_id, t3.sigma_b, t2.sigma_b) if not np.array_equal(np.asarray(a), np.asarray(b))]
    assert set(diff) == set(t3.nuclide_id[t3.tier == "ANCHORED"])
    r = t3[t3.nuclide_id == "Z079N118M0"].iloc[0]
    assert r.below1keV_source.startswith("engine") and len(r.sigma_below1keV_b) == 15
    el, sl = np.asarray(r.energy_below1keV_ev, float), np.asarray(r.sigma_below1keV_b, float)
    assert el[0] == pytest.approx(2.0) and (np.diff(sl) < 0).all() and sl[-1] > np.asarray(r.sigma_b)[0]
    rt = pd.read_csv(L.LIBRARY.parent / "v0.2.2" / "rates_v022.csv").set_index("nuclide_id")
    m = rt.loc["Z079N118M0"]
    assert m.reduced_mass_u == pytest.approx(1.00866491590 * m.target_mass_u / (1.00866491590 + m.target_mass_u), rel=1e-12)
