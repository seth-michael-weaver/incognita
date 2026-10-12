"""CTKINK: `ctwindow2` (env INCOGNITA_CT_WINDOW2) = ctwindow's complete-window CT anchor with (T, E0, Ex) solved jointly, so the
USED level density (densitytot) is continuous in value and log-slope at Exmatch. OFF must be TALYS's path unchanged and must
leave the frozen `ctwindow` (B51) untouched; ON must be continuous to 1e-6 and count exactly the window's known levels."""
import math
from dataclasses import replace

import numpy as np
import pytest
import torch

from physics.hf.compound.dens_reference import structure_of
from physics.hf.density import ctwindow, ctwindow2
from physics.hf.density.matching import densitymatch
from physics.hf.density.parameters import densitypar
from physics.hf.density.tables import attach_tables
from physics.hf.input.defaults import default_options
from physics.hf.structure.levels import discrete_levels

try:
    ctwindow._levels_param()
    HAVE_RIPL = True
except FileNotFoundError:
    HAVE_RIPL = False

NUCLEI = [(26, 57, 26, 56), (64, 158, 64, 157), (72, 177, 72, 176), (40, 95, 40, 94)]


def _ld(Z, A, Zt, At):
    o, p, m = structure_of(Zt, At)
    return attach_tables(densitypar(Z, A, o, p, m, discrete_levels(Z, A, o, m, p)))


def _jump(ld, eps=1e-9, h=1e-5):
    """(ln rho(Ex+) - ln rho(Ex-), slope(Ex+)/slope(Ex-) - 1) of the used density, one-sided 3-point slopes."""
    x = float(ld.Exmatch_mev[0])
    lo = np.log(ctwindow2.used_density(ld, [x - eps, x - eps - h, x - eps - 2 * h]))
    hi = np.log(ctwindow2.used_density(ld, [x + eps, x + eps + h, x + eps + 2 * h]))
    s_lo = (3 * lo[0] - 4 * lo[1] + lo[2]) / (2 * h)
    s_hi = -(3 * hi[0] - 4 * hi[1] + hi[2]) / (2 * h)
    return hi[0] - lo[0], s_hi / s_lo - 1.0


def _count_used(ld, EL, EP, n=4000):
    """Levels of the used density in [EL, EP], integrated piecewise on either side of Exmatch."""
    x = float(ld.Exmatch_mev[0])
    out = 0.0
    for a, b in ((EL, min(EP, x)), (max(EL, x), EP)):
        if b > a:
            E = np.linspace(a, b, n + 1)
            E[0], E[-1] = a + 1e-12, b - 1e-12
            out += ctwindow2._simpson(ctwindow2.used_density(ld, E), a, b)
    return out


def test_default_off_and_switches(monkeypatch):
    monkeypatch.delenv("INCOGNITA_CT_WINDOW2", raising=False)
    assert not ctwindow2.enabled(default_options(26, 56))
    assert ctwindow2.enabled(default_options(26, 56, overrides={"ctwindow2": "y"}))
    assert not ctwindow.enabled(default_options(26, 56, overrides={"ctwindow2": "y"}))
    monkeypatch.setenv("INCOGNITA_CT_WINDOW2", "1")
    assert ctwindow2.enabled(default_options(26, 56))


@pytest.mark.skipif(not HAVE_RIPL, reason="RIPL-4 levels-param.data not available")
def test_off_is_talys_and_ctwindow_frozen():
    ld = _ld(26, 57, 26, 56)
    a, b = densitymatch(ld), densitymatch(ld, ctwindow2=False)
    c, d = densitymatch(ld, ctwindow=True), ctwindow.anchor(densitymatch(ld))
    for f in ("T_mev", "E0_mev", "Exmatch_mev"):
        assert torch.equal(getattr(a, f), getattr(b, f))
        assert torch.equal(getattr(c, f), getattr(d, f))


@pytest.mark.skipif(not HAVE_RIPL, reason="RIPL-4 levels-param.data not available")
@pytest.mark.parametrize("ct", [0.0, -0.5, 0.4])
@pytest.mark.parametrize("Z,A,Zt,At", NUCLEI)
def test_on_continuous_and_counts_the_window(Z, A, Zt, At, ct):
    ld = _ld(Z, A, Zt, At)
    if ct:
        c = ld.ctable.clone()
        c[0] = ct
        ld = replace(ld, ctable=c)
    on = densitymatch(ld, ctwindow2=True)
    assert (Z, A) not in ctwindow2.WHY
    rec = ctwindow2.LAST[(Z, A)]
    dv, ds = _jump(on)
    assert abs(dv) < 1e-6 and abs(ds) < 1e-6
    n = _count_used(on, rec["EL"], rec["EP"])
    assert n == pytest.approx(rec["NP"] - rec["NL"], rel=1e-5)
    assert float(on.T_mev[0]) == pytest.approx(rec["T"], rel=1e-15)


@pytest.mark.skipif(not HAVE_RIPL, reason="RIPL-4 levels-param.data not available")
def test_ctwindow_v1_kink_is_what_v2_removes():
    """Zr-95 (default structure): v1's T comes from FG tables of the already-matched record (spin cutoff interpolated below the
    old Exmatch), so its join has a slope kink of a few per cent; v2's does not."""
    ld = _ld(40, 95, 40, 94)
    _, ds1 = _jump(densitymatch(ld, ctwindow=True))
    _, ds2 = _jump(densitymatch(ld, ctwindow2=True))
    assert abs(ds1) > 1e-2 and abs(ds2) < 1e-6


@pytest.mark.skipif(not HAVE_RIPL, reason="RIPL-4 levels-param.data not available")
def test_unanchorable_kept(monkeypatch):
    monkeypatch.setattr(ctwindow2, "_window", lambda ld: (None, "no_umax"))
    ld = _ld(26, 57, 26, 56)
    off, on = densitymatch(ld), densitymatch(ld, ctwindow2=True)
    assert ctwindow2.WHY[(26, 57)] == "no_umax"
    assert torch.equal(off.Exmatch_mev, on.Exmatch_mev) and torch.equal(off.T_mev, on.T_mev)
    assert math.isfinite(float(on.E0_mev[0]))
