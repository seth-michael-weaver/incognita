"""FIXENG F14 (INCOGNITA_GGDEADEND): the capture-entry dead end. Reproducer: Xe-140 + n and Rh-105 + n, whose compound
level lists (Xe-141, Rh-106) are yrast bands running past S_n, gave <Gamma_gamma>_s = 0 / 2.6e-7 eV in B55/B59.
OFF must leave every Levels object as TALYS reads it; ON cuts only the dead-end lists and leaves the LD matching alone."""
import pytest
import torch

from physics.hf.compound.dens_reference import structure_of
from physics.hf.density import ctwindow
from physics.hf.density.parameters import densitypar
from physics.hf.structure import ggdeadend
from physics.hf.structure.levels import _LEVELS_CACHE, discrete_levels

try:
    ctwindow._levels_param()
    HAVE_RIPL = True
except FileNotFoundError:
    HAVE_RIPL = False


def _lv(Z, A, Zt, At):
    _LEVELS_CACHE.clear()
    o, p, m = structure_of(Zt, At)
    return discrete_levels(Z, A, o, m, p), (o, p, m)


def test_rule_on_lists():
    # entry 1/2+ (even target): a 5/2, 7/2, ... list below S_n has no dipole partner
    e = [0.0, 0.04, 0.11, 3.4]
    assert ggdeadend.is_dead_end(e, [2.5, 3.5, 4.5, 1.5], 3, 3.28, 0.0)
    assert not ggdeadend.is_dead_end(e, [2.5, 1.5, 4.5, 1.5], 3, 3.28, 0.0)   # a 3/2 below S_n
    assert not ggdeadend.is_dead_end(e, [2.5, 3.5, 4.5, 1.5], 2, 3.28, 0.0)   # continuum below S_n
    assert ggdeadend.entry_spins(0.0) == [0.5] and ggdeadend.entry_spins(3.5) == [3.0, 4.0]


def test_off_untouched(monkeypatch):
    monkeypatch.delenv(ggdeadend.ENV, raising=False)
    lv, _ = _lv(54, 141, 54, 140)
    assert lv.nlev == 30 and lv.nlev_ld == -1
    assert float(lv.e_mev[30]) > 3.28


@pytest.mark.skipif(not HAVE_RIPL, reason="RIPL-4 levels-param.data not available")
@pytest.mark.parametrize("Z,A,Zt,At,n_cut", [(54, 141, 54, 140, 1), (45, 106, 45, 105, 8)])
def test_on_cuts_dead_end_keeps_ld(monkeypatch, Z, A, Zt, At, n_cut):
    monkeypatch.delenv(ggdeadend.ENV, raising=False)
    off, (o, p, m) = _lv(Z, A, Zt, At)
    ld_off = densitypar(Z, A, o, p, m, off)
    monkeypatch.setenv(ggdeadend.ENV, "1")
    on, _ = _lv(Z, A, Zt, At)
    ld_on = densitypar(Z, A, o, p, m, on)
    assert on.nlev == n_cut and on.nlev_ld == off.nlev
    assert torch.equal(on.e_mev, off.e_mev[: n_cut + 1])
    assert ld_on.Nlast[0] == n_cut and ld_off.Nlast[0] == off.nlev
    assert ld_on.Ntop == ld_off.Ntop and ld_on.Nlow == ld_off.Nlow
    assert torch.equal(ld_on.scutoffdisc_sq if hasattr(ld_on, "scutoffdisc_sq") else ld_on.scutoffdisc,
                       ld_off.scutoffdisc_sq if hasattr(ld_off, "scutoffdisc_sq") else ld_off.scutoffdisc)


@pytest.mark.skipif(not HAVE_RIPL, reason="RIPL-4 levels-param.data not available")
@pytest.mark.parametrize("Z,A,Zt,At", [(26, 57, 26, 56), (79, 198, 79, 197), (8, 17, 8, 16)])
def test_on_leaves_normal_lists(monkeypatch, Z, A, Zt, At):
    monkeypatch.delenv(ggdeadend.ENV, raising=False)
    off, _ = _lv(Z, A, Zt, At)
    monkeypatch.setenv(ggdeadend.ENV, "1")
    on, _ = _lv(Z, A, Zt, At)
    assert on.nlev == off.nlev and on.nlev_ld == -1
