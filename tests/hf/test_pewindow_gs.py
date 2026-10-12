"""pewindow g: `pewindow g` = `p` + the ground state's TALYS window [mid(E0, E1), E0] integrated exactly (endpoint segments included)."""
from types import SimpleNamespace

import numpy as np

from physics.hf.preeq import exciton as X
from tests.hf.test_pecollapse import _case


def test_mode():
    assert X.pewindow_mode(SimpleNamespace(pewindow="g")) == "g"


def _gs_cell(mode, monkeypatch):
    spectra, inp, disc = _case()
    y = spectra["xspreeq"][0, 2].numpy().astype(float).copy()
    eg = inp.egrid_mev[0].numpy().astype(float)
    y[eg > 14.0] = 0.0  # spectrum closes between 14.0 and 14.5 MeV: above u1 = 13.95, inside the g.s. window [13.95, 14.1]
    y[(eg > 12.0) & (eg <= 14.0)] = 0.2
    x = eg.copy()
    esd = [float(v) for v in disc.eoutdis_mev[0][2]][:8]
    NL = 7
    elast = esd[NL]
    lev = list(range(1, NL + 1))
    up = [0.5 * (esd[i] + esd[i - 1]) for i in lev]
    lo = [elast if i == NL else 0.5 * (esd[i] + esd[i + 1]) for i in lev]
    u1 = up[0]
    utop = u1
    if mode == "g":
        lev.append(0); lo.append(u1); up.append(esd[0]); utop = esd[0]
    sh = X._cumlin(x, y, np.array(up)) - X._cumlin(x, y, np.array(lo))
    union = float(X._cumlin(x, y, np.array([u1]))[0] - X._cumlin(x, y, np.array([elast]))[0])
    win = dict(lev=lev, lo=lo, up=up, sh=[float(v) for v in sh], union=union, utop=utop)
    monkeypatch.setattr(X, "pepauli_onsets", lambda *a, **k: np.array([14.05]))
    fex = lambda e: np.where(e < 14.05, 0.2 + 2.0 * (14.05 - e), 0.0)  # noqa: E731
    monkeypatch.setattr(X, "pepauli_spectrum", lambda res, pre, inp_, o, p, s, c, e: (np.tile(fex(e), (7, 1)), 0.0))
    out = X._pepauli_cell({}, {}, inp, dict(options=None, params=None, states=None), 0, 2, x, y, eg, win, [], elast, u1, mode)
    return win, out


def test_gs_window_exact(monkeypatch):
    win, out = _gs_cell("p", monkeypatch)
    assert out["pp_nseg"] == 0 and "sh" not in out  # p: the segment above u1 is not an endpoint segment of its range
    win, out = _gs_cell("g", monkeypatch)
    assert out["pp_nseg"] == 1 and out["pp_fallback"] == ""
    lin = 0.2 * (14.0 - 13.95)  # [13.95, 14.0]: open segment, linear = exact
    ex = 0.2 * 0.05 + 2.0 * 0.05 ** 2 / 2  # [14.0, 14.05] exact spectrum, closed above the onset
    assert abs(out["sh"][-1] - (lin + ex)) <= 1e-12
    assert out["sh"][:-1] == win["sh"][:-1]  # levels 1..NL: windows below u1, untouched by the g.s. segment
    assert abs(out["union"] - win["union"]) <= 1e-15  # union [Elast, u1] unchanged
