"""CTWFREEZE: `ctwindow` (env INCOGNITA_CT_WINDOW) = CTWIN arm W's constant-temperature anchor on the complete level window
(E <= RIPL-4 Umax), TALYS branch-A match, default OFF. OFF must be TALYS's path unchanged; ON must count exactly the known
levels of the window with the used density and join the Fermi gas without a kink. Engine-level OFF fingerprint and the
equality with the registered runner-side patch: development notes"""
import math

import numpy as np
import pytest
import torch

from physics.hf.compound.dens_reference import structure_of
from physics.hf.density import ctwindow
from physics.hf.density.matching import _fermi_tables, densitymatch
from physics.hf.density.parameters import densitypar
from physics.hf.density.tables import attach_tables
from physics.hf.input.defaults import default_options
from physics.hf.structure.levels import discrete_levels

try:
    ctwindow._levels_param()
    HAVE_RIPL = True
except FileNotFoundError:
    HAVE_RIPL = False


def _ld(Z, A, Zt, At):
    o, p, m = structure_of(Zt, At)
    return attach_tables(densitypar(Z, A, o, p, m, discrete_levels(Z, A, o, m, p)))


def test_default_off_and_switches(monkeypatch):
    monkeypatch.delenv("INCOGNITA_CT_WINDOW", raising=False)
    assert not ctwindow.enabled(default_options(26, 56))
    assert ctwindow.enabled(default_options(26, 56, overrides={"ctwindow": "y"}))
    monkeypatch.setenv("INCOGNITA_CT_WINDOW", "1")
    assert ctwindow.enabled(default_options(26, 56))


def test_off_is_talys():
    ld = _ld(26, 57, 26, 56)
    a, b = densitymatch(ld), densitymatch(ld, ctwindow=False)
    for f in ("T_mev", "E0_mev", "Exmatch_mev"):
        assert torch.equal(getattr(a, f), getattr(b, f))


@pytest.mark.skipif(not HAVE_RIPL, reason="RIPL-4 levels-param.data not available")
@pytest.mark.parametrize("Z,A,Zt,At", [(26, 57, 26, 56), (64, 158, 64, 157), (72, 177, 72, 176)])
def test_on_counts_the_window(Z, A, Zt, At):
    ld = _ld(Z, A, Zt, At)
    off, on = densitymatch(ld), densitymatch(ld, ctwindow=True)
    rec = ctwindow.LAST[(Z, A)]
    assert float(on.Exmatch_mev[0]) != float(off.Exmatch_mev[0])
    T, E0, Ex = float(on.T_mev[0]), float(on.E0_mev[0]), float(on.Exmatch_mev[0])
    # no kink: T equals the Fermi-gas temperature table at Ex; the CT count over [EL, EP] equals NP - Nlow
    logrho, temprho, _, _ = _fermi_tables(ld, 0)
    assert T == pytest.approx(ctwindow._interp(temprho.double().numpy(), Ex), rel=1e-12)
    r = math.exp((Ex - E0) / T) / T
    n = ctwindow._count(r, T, rec["EL"], rec["EP"], Ex, rec["ct"], rec["pt"])
    assert n == pytest.approx(rec["NP"] - rec["NL"], rel=1e-3)


@pytest.mark.skipif(not HAVE_RIPL, reason="RIPL-4 levels-param.data not available")
def test_unanchorable_kept(monkeypatch):
    monkeypatch.setattr(ctwindow, "ripl_umax", lambda Z, A: (0, 0.0))
    ld = _ld(26, 57, 26, 56)
    off, on = densitymatch(ld), densitymatch(ld, ctwindow=True)
    assert ctwindow.WHY[(26, 57)] == "no_umax"
    assert torch.equal(off.Exmatch_mev, on.Exmatch_mev) and torch.equal(off.T_mev, on.T_mev)
    assert np.isfinite(float(on.E0_mev[0]))
