"""KWCOV B7b: the JLM microscopic optical model (jlmomp y, jlmmode, radialmodel, radialfile, l*adjust, micro y) and
the alpha folding potentials (alphaomp 3-5, adepthcor, aradialcor), docs/hf/COVERAGE_PLAN.md batch B7b.

Stock numbers: TALYS-2.25 runs under ~/kwcov/stock/b7b, transcribed here: n + Fe-56 `jlmomp y; outomp y;
outinverse y` at 1/5/14 MeV (radial.out, omp.out, transmission_n.out, talys.out's incident cross sections) and
alpha + Fe-56 `alphaomp 3|4|5; outomp y` at 10/15/20 MeV.
"""
from __future__ import annotations

import numpy as np
import pytest
import torch

from physics.hf.input import defaults as D
from physics.hf.omp import jlm
from physics.hf.omp.schrodinger import nucleus_mass_amu


def _opts(Z=26, A=56, proj="n", **ov):
    return D.default_options(Z, A, proj, ov)


# ------------------------------------------------------------------------------------------------ densities
def test_radial_table_is_radial_out():
    # radial.out (r, protons, neutrons) of the n + Fe-56 run holds the COMPOUND nucleus Fe-57 (inverseecis.f90:213
    # prints rhojlm(Zcomp, Ncomp) under the target's title); the file's r = 0 line is skipped, then extrapolated
    rad, rp, rn = jlm.radial_table(26, 57)
    for r, p, n in ((0.1, 8.728240e-02, 8.996720e-02), (0.3, 8.630020e-02, 9.004240e-02),
                    (14.4, 4.748510e-14, 6.976750e-14), (15.0, 2.411570e-15, 3.745440e-15),
                    (20.0, 9.793163e-27, 2.772640e-26)):
        i = int(round(r * 10)) - 1
        assert rad[i] == pytest.approx(r, abs=1e-5)
        assert rp[i, 0] == pytest.approx(p, rel=2e-6) and rn[i, 0] == pytest.approx(n, rel=2e-6)
    assert jlm.radial_table(26, 200) is None  # mass not in Fe.rad: jlmexist stays false
    assert jlm.radial_table(26, 57, radialmodel=1)[1][0, 0] != rp[0, 0]  # bskg3 vs d1m


# ------------------------------------------------------------------------------------------------ potential
OMP_OUT = {  # omp.out of the incident channel: (E, r) -> V, W, Vso, Wso
    (1.0, 0.1): (51.3564, 0.578062, 2.20947, 0.0498809),
    (1.0, 1.3): (50.4659, 0.686379, 0.449277, 0.0101428),
    (1.0, 6.8): (1.01108, None, None, None),
    (5.0, 5.0): (13.5909, None, None, None),
    (5.0, 0.7): (None, None, 1.0701, None),
    (14.0, 5.2): (10.1262, None, None, None),
    (14.0, 6.3): (None, 1.01229, None, None),
    (14.0, 5.5): (None, None, 0.139057, None),
}


@pytest.mark.parametrize("key", list(OMP_OUT))
def test_jlm_potential_is_stock_omp_out(key):
    e, r = key
    c, so, rc = jlm.potential(26, 56, 1, np.array([e]))
    i = int(round(r * 10)) - 1
    ours = (-c.real[0, i], -c.imag[0, i], -so.real[0, i], -so.imag[0, i])
    for o, s in zip(ours, OMP_OUT[key]):
        if s is not None:
            assert o == pytest.approx(s, rel=1e-5)
    assert rc == pytest.approx(1.274025, abs=1e-6)  # Elton


def test_normalisations_jlmmode_and_adjust():
    e = np.array([1.0, 14.0])
    base = jlm.normalisations(e)
    assert base[4, 0] == pytest.approx(40.0 + 130.0 * np.exp(-0.013))  # lvso
    assert base[5, 0] == pytest.approx(3.8)  # lwso = -0.2 (e - 20)
    assert np.allclose(jlm.normalisations(e, 3)[1], 2.0 * base[1])  # jlmmode 3 doubles lw
    assert not np.allclose(jlm.normalisations(e, 1)[3], base[3])  # jlmmode 1/2: lw1's lambda
    p = D.default_params(26, 56, _opts(), overrides={"lvadjust": 1.1, "lwsoadjust": 0.5})
    adj = jlm.normalisations(e, 0, p)
    assert np.allclose(adj[0], np.float32(1.1) * base[0]) and np.allclose(adj[5], 0.5 * base[5])
    assert np.allclose(adj[1:5], base[1:5])


# ------------------------------------------------------------------------------------------------ solve
def test_incident_cross_sections_are_stock():
    o = _opts(jlmomp="y")
    assert o.flagjlm and o.flagspher
    p = D.default_params(26, 56, o)
    m = nucleus_mass_amu(26, 56)
    # talys.out "Optical model results": total, reaction, elastic [mb]
    for e, (tot, reac, el) in {1.0: (2642.5, 1312.9, 1329.7), 5.0: (3647.3, 1420.6, 2226.8),
                               14.0: (2381.3, 1379.4, 1001.9)}.items():
        tr = jlm.solve(26, 56, 1, torch.tensor([e], dtype=torch.float64), m, 60, o, p)
        assert float(tr.sigma_tot_mb[0, 0, 0]) == pytest.approx(tot, rel=5e-5)
        assert float(tr.sigma_reac_mb[0, 0, 0]) == pytest.approx(reac, rel=5e-5)
        assert float(tr.sigma_shape_el_mb[0, 0, 0]) == pytest.approx(el, rel=5e-5)


def test_inverse_transmission_is_stock():
    o = _opts(jlmomp="y")
    p = D.default_params(26, 56, o)
    m = nucleus_mass_amu(26, 56)
    # transmission_n.out of Fe-56 (the ECIS energy): l, T(l-1/2), T(l+1/2)
    for e, rows in {1.018033e-3: ((0, 0.0, 4.404220e-02), (1, 2.594455e-05, 1.340614e-05)),
                    14.2525: ((0, 0.0, 8.667812e-01), (2, 8.922384e-01, 8.532118e-01),
                              (3, 8.396001e-01, 8.888031e-01))}.items():
        tr = jlm.solve(26, 56, 1, torch.tensor([e], dtype=torch.float64), m, 30, o, p)
        for l, tm, tp in rows:  # noqa: E741
            assert float(tr.tjl[0, 0, 0, l, 0]) == pytest.approx(tm, rel=1e-4, abs=1e-12)
            assert float(tr.tjl[0, 0, 0, l, 1]) == pytest.approx(tp, rel=1e-4)


def test_active_only_where_a_density_exists():
    o = _opts(jlmomp="y")
    assert jlm.active(o, 26, 56, 1) and jlm.active(o, 26, 56, 2)
    assert not jlm.active(o, 26, 56, 3) and not jlm.active(o, 26, 56, 6)
    assert not jlm.active(_opts(), 26, 56, 1)
    assert not jlm.active(o, 26, 200, 1)
    a = _opts(alphaomp=4)
    assert jlm.active(a, 26, 56, 6) and not jlm.active(a, 26, 56, 1)


# ------------------------------------------------------------------------------------------------ alpha folding
ALPHA_REAC = {  # alpha + Fe-56 talys.out "Reaction cross section" [mb] at 10 / 15 / 20 MeV
    3: (312.60, 878.04, 1125.3), 4: (300.75, 865.75, 1125.2), 5: (329.56, 883.44, 1102.2)}
ALPHA_W = {3: 14.59, 4: 9.26988, 5: 22.155}  # omp.out W at r = 1 fm, 10 MeV


@pytest.mark.parametrize("mode", [3, 4, 5])
def test_alpha_folding_is_stock(mode):
    o = _opts(proj="a", alphaomp=mode)
    p = D.default_params(26, 56, o)
    c, _so, _rc = jlm.potential(26, 56, 6, np.array([10.0]), params=p, alpha_options=o)
    assert -c.imag[0, 9] == pytest.approx(ALPHA_W[mode], rel=2e-5)
    m = nucleus_mass_amu(26, 56)
    for e, reac in zip((10.0, 15.0, 20.0), ALPHA_REAC[mode]):
        tr = jlm.solve(26, 56, 6, torch.tensor([e], dtype=torch.float64), m, 60, o, p)
        assert float(tr.sigma_reac_mb[0, 0, 0]) == pytest.approx(reac, rel=1e-4)


def test_alpha_folding_real_part_vs_omp_out():
    # omp.out V (nuclear + Coulomb printed together) at r = 1 fm, alphaomp 4, 10 MeV: 179.38; Coulomb removed
    o = _opts(proj="a", alphaomp=4)
    c, _so, rc = jlm.potential(26, 56, 6, np.array([10.0]), params=D.default_params(26, 56, o), alpha_options=o)
    Rc = round(rc, 5) * nucleus_mass_amu(26, 56) ** (1 / 3)
    e2z = 197.326968 / 137.03599911 * 52
    assert -c.real[0, 9] == pytest.approx(179.38 + e2z / (2 * Rc) * (3 - (1.0 / Rc) ** 2), rel=2e-5)


# ------------------------------------------------------------------------------------------------ keywords
def test_refusals_and_accepted():
    D.reject_unported(_opts(jlmomp="y"))
    D.reject_unported(_opts(micro="y"))
    for a in (3, 4, 5):
        D.reject_unported(_opts(alphaomp=a))
    for ov, msg in (({"jlmomp": "y", "preeqmode": 3}, "preeqmode 3"), ({"jlmomp": "y", "racap": "y"}, "racap"),
                    ({"jlmomp": "y", "optmodall": "y"}, "optmodall"), ({"jlmomp": "y", "alphaomp": 4}, "alphaomp 3-5"),
                    ({"alphaomp": 5, "optmodall": "y"}, "optmodall")):
        with pytest.raises(NotImplementedError, match=msg):
            D.reject_unported(_opts(**ov))


def test_radialfile_deck_line(tmp_path, monkeypatch):
    from physics.hf.omp import ompdeck

    src = jlm.radial_file(26)
    f = tmp_path / "myfe.rad"
    f.write_text(open(src).read())
    keep, deck = ompdeck.extract([f"radialfile 26 {f}", "jlmomp y"], 26, 56)
    assert keep == ("jlmomp y",) and deck.files == ((26, jlm.RADIALFILE_K, str(f)),)
    monkeypatch.setattr(ompdeck, "active", lambda: deck)
    assert jlm.radial_file(26) == str(f) and jlm.radial_file(26, 1) == str(f)
    assert ompdeck.local_file(26, 1) is None  # not an optmodfilen
    from physics.hf.input import fitlib

    assert "radialfile" in fitlib.FILE_KEYS


def test_token():
    assert jlm.token(_opts()) == ()
    assert jlm.token(_opts(jlmomp="y"))[0] == "jlm"
    assert jlm.token(_opts(alphaomp=3))[0] == "jlm"


def test_energy_local_l_adjust_is_skipped():
    from physics.hf.input import fitlib as F

    _o, _c, g, _p, skipped = F._split(["lvadjust 1.1", "adepthcor 1.2 3 10 5 1.2"], True)
    assert g == [("lvadjust", 1.1)] and skipped and "energy-local" in skipped[0][1]
