"""PEPAULI: `pewindow p|q` = WA + exact spectrum (p) or two exact nodes (q) inside the endpoint segments only."""
from types import SimpleNamespace

import numpy as np
import pytest
import torch

from physics.hf.density.particle_hole import phdens2
from physics.hf.preeq import exciton as X
from tests.hf.test_pecollapse import _case


def test_mode():
    for v in ("p", "q"):
        assert X.pewindow_mode(SimpleNamespace(pewindow=v)) == v
    with pytest.raises(ValueError):
        X.pewindow_mode(SimpleNamespace(pewindow="z"))


def test_onset_formula_matches_phdens2():
    # the threshold used by pepauli_onsets (Apauli2 from the CN g + factors from the residual g) is where phdens2 switches on
    rng = np.random.default_rng(3)
    for _ in range(40):
        ppi, hpi, pnu, hnu = (int(v) for v in rng.integers(0, 4, 4))
        if ppi + hpi + pnu + hnu == 0:
            continue
        gpc, gnc, gsp, gsn = rng.uniform(2.0, 8.0, 4)
        ap = (max(ppi, hpi) ** 2 / gpc + max(pnu, hnu) ** 2 / gnc - (ppi * ppi + hpi * hpi + ppi + hpi) / (4 * gpc)
              - (pnu * pnu + hnu * hnu + pnu + hnu) / (4 * gnc))
        up = ap + (ppi * ppi + hpi * hpi + ppi + hpi) / (4 * gsp) + (pnu * pnu + hnu * hnu + pnu + hnu) / (4 * gsn)
        T = lambda v: torch.tensor([v])  # noqa: E731
        d = lambda u: float(phdens2(T(ppi), T(hpi), T(pnu), T(hnu), T(gsp), T(gsn), T(u), T(38.0), False,  # noqa: E731
                                     gsp_pauli=T(gpc), gsn_pauli=T(gnc))[0])
        assert d(up - 1e-9) == 0.0
        assert d(up + 1e-9) > 0.0 or ppi + hpi + pnu + hnu > 6  # PHDENS_FLOOR can hide a tiny density at onset


def test_integral_piecewise_exact():
    f = lambda e: np.where(e < 1.3, (1.3 - e + 0.2) ** 3 * (1 + 0.1 * e), 0.0)  # noqa: E731
    got = X.pepauli_integral(f, 0.5, 2.0, np.array([1.3]))
    P = np.polynomial.Polynomial
    ref = (P([1.5, -1.0]) ** 3 * P([1.0, 0.1])).integ()
    assert abs(got - (ref(1.3) - ref(0.5))) <= 1e-13 * got


def _cell(mode, monkeypatch, fexact):
    spectra, inp, disc = _case()
    y = spectra["xspreeq"][0, 2].numpy().astype(float).copy()
    eg = inp.egrid_mev[0].numpy().astype(float)
    y[eg > 13.0] = 0.0  # spectrum closes between 13.0 and 13.5 MeV (one endpoint segment)
    x = eg.copy()
    esd = [float(v) for v in disc.eoutdis_mev[0][2]][:8]
    NL = 7
    elast = esd[NL]
    lev = list(range(1, NL + 1))
    up = [0.5 * (esd[i] + esd[i - 1]) for i in lev]
    lo = [elast if i == NL else 0.5 * (esd[i] + esd[i + 1]) for i in lev]
    u1 = up[0]
    sh = X._cumlin(x, y, np.array(up)) - X._cumlin(x, y, np.array(lo))
    union = float(X._cumlin(x, y, np.array([u1]))[0] - X._cumlin(x, y, np.array([elast]))[0])
    win = dict(lev=lev, lo=lo, up=up, sh=[float(v) for v in sh], union=union)
    ons = np.array([13.17])
    monkeypatch.setattr(X, "pepauli_onsets", lambda *a, **k: ons)
    monkeypatch.setattr(X, "pepauli_spectrum", lambda res, pre, inp_, o, p, s, c, e: (np.tile(fexact(e), (7, 1)), 0.0))
    out = X._pepauli_cell({}, {}, inp, dict(options=None, params=None, states=None), 0, 2, x, y, eg, win, [], elast, u1, mode)
    return x, y, win, out, lo, up


def test_cell_p_and_q(monkeypatch):
    k = None
    def fex(e, y13=None):
        return np.where(e < 13.17, 0.05 * (13.17 - e + 0.3) ** 2, 0.0)
    for mode in ("p", "q"):
        x, y, win, out, lo, up = _cell(mode, monkeypatch, fex)
        assert out["pp_nseg"] == 1 and out["pp_fallback"] == ""
        k = int(np.searchsorted(x, 13.0))
        a, b = x[k], x[k + 1]
        for m, (l_, u_) in enumerate(zip(lo, up)):
            if u_ <= a or l_ >= b:  # windows outside the endpoint segment: bit-identical to WA
                assert out["sh"][m] == win["sh"][m]
        # tiling: sum of levels = union
        assert abs(sum(out["sh"]) - out["union"]) <= 1e-12 * out["union"]
