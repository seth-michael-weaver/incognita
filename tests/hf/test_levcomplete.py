"""HFGAMMA (INCOGNITA_LEVCOMPLETE): the continuum starts at the RIPL-4 complete scheme's upper end. Reproducer: Hf-182 lists 30
levels to 3.869 MeV, complete only to 1.988 MeV, so a 3-4.5 MeV neutron on Hf-182 found no continuum exit (B55/B61: capture
164 mb, gamma-fed flux 409 mb at 4 MeV). OFF leaves every Levels object as TALYS reads it; ON cuts and keeps the LD matching."""
import pytest
import torch

from physics.hf.compound.dens_reference import structure_of
from physics.hf.density import ctwindow
from physics.hf.density.parameters import densitypar
from physics.hf.structure import levcomplete
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


def test_modes(monkeypatch):
    for v, m in (("0", ""), ("1", "all"), ("all", "all"), ("tgt", "tgt"), ("n", "")):
        monkeypatch.setenv(levcomplete.ENV, v)
        assert levcomplete.mode() == m
    monkeypatch.setenv(levcomplete.ENV, "tgt")
    assert levcomplete.applies(True) and not levcomplete.applies(False)


def test_off_untouched(monkeypatch):
    monkeypatch.delenv(levcomplete.ENV, raising=False)
    lv, _ = _lv(72, 182, 72, 182)
    assert lv.nlev == 30 and lv.nlev_ld == -1 and abs(float(lv.e_mev[30]) - 3.8692) < 1e-3


@pytest.mark.skipif(not HAVE_RIPL, reason="RIPL-4 levels-param.data not available")
@pytest.mark.parametrize("val", ["all", "tgt"])
def test_on_cuts_target_keeps_ld(monkeypatch, val):
    monkeypatch.delenv(levcomplete.ENV, raising=False)
    off, (o, p, m) = _lv(72, 182, 72, 182)
    ld_off = densitypar(72, 182, o, p, m, off)
    monkeypatch.setenv(levcomplete.ENV, val)
    on, _ = _lv(72, 182, 72, 182)
    ld_on = densitypar(72, 182, o, p, m, on)
    assert on.nlev == 21 and on.nlev_ld == 30 and abs(float(on.e_mev[21]) - 1.9884) < 1e-3
    assert torch.equal(on.e_mev, off.e_mev[:22])
    assert ld_on.Ntop == ld_off.Ntop and ld_on.Nlow == ld_off.Nlow


@pytest.mark.skipif(not HAVE_RIPL, reason="RIPL-4 levels-param.data not available")
def test_tgt_leaves_other_nuclei(monkeypatch):
    # Hf-183 (no RIPL-4 Umax) is never cut; Hf-181 (E30 < Umax) is never cut; Hf-182 as a residual of Hf-183 + n: tgt keeps it
    monkeypatch.setenv(levcomplete.ENV, "all")
    assert _lv(72, 183, 72, 182)[0].nlev == 30 and _lv(72, 181, 72, 182)[0].nlev == 30
    monkeypatch.setenv(levcomplete.ENV, "tgt")
    off_tgt = _lv(72, 182, 72, 183)[0]
    monkeypatch.setenv(levcomplete.ENV, "all")
    on_all = _lv(72, 182, 72, 183)[0]
    assert on_all.nlev < off_tgt.nlev or off_tgt.nlev == on_all.nlev == 1
