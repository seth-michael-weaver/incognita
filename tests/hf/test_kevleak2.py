"""KEVLEAK2 (`pe` part = KEVLEAK re-ported; `dup` part below). pe: the projectile's continuum pre-equilibrium is zero where its last discrete level is closed (Elast <= 0).

Synthetic `preeq_total` inputs (no data files): type 1 = neutron = projectile (k0 = 1), type 2 = proton.
"""
from types import SimpleNamespace

import numpy as np
import pytest
import torch

from physics.hf.preeq import exciton as X


@pytest.fixture(autouse=True)
def _no_eff(monkeypatch):  # KEVLEAK3 gate candidate: a run's kevleak2.sync value must not leak into these unit tests
    monkeypatch.delenv("INCOGNITA_KEVLEAK2_EFF", raising=False)

E, P = 6, 3


def _case(elast_n, elast_p=0.5):
    C = 1
    eg = torch.tensor([[0.0, 0.0005, 0.0015, 0.0025, 0.0035, 0.0045]], dtype=torch.float64)
    de = torch.full((C, E), 0.001, dtype=torch.float64)
    inp = SimpleNamespace(C=C, E=E, egrid_mev=eg, deltae_mev=de, k0=1,
                          xsflux_mb=torch.tensor([1.0e5], dtype=torch.float64))
    eout = [[np.array([0.004, 0.003, 0.002]), np.array([0.004, 0.003, elast_n]), np.array([1.0, 0.8, elast_p]),
             None, None, None, None]]
    disc = SimpleNamespace(ebegin=[1, 1, 1, 9, 9, 9, 9], eend=[[5, 5, 5, 1, 1, 1, 1]], nendisc=[[3, 1, 4, 1, 1, 1, 1]],
                           eoutdis_mev=eout, nlast=[2] * 7, etop_mev=torch.full((C, E), 0.002, dtype=torch.float64))
    g = torch.Generator().manual_seed(7)
    sp = {k: torch.rand(C, 7, E, generator=g, dtype=torch.float64) * 100 for k in ("xspreeq", "xspreeqps", "xspreeqki", "xspreeqbu")}
    sp["xsstep"] = torch.rand(C, 7, P, E, generator=g, dtype=torch.float64) * 100
    sp["xsstep2"] = torch.rand(C, 2, 7, E, generator=g, dtype=torch.float64) * 100
    return sp, inp, disc


def _run(monkeypatch, on, elast_n):
    if on:
        monkeypatch.setenv("INCOGNITA_KEVLEAK2", "pe")
    else:
        monkeypatch.setenv("INCOGNITA_KEVLEAK2", "0")  # OFF (default is now 2)
    monkeypatch.delenv("INCOGNITA_C6FIX", raising=False)
    sp, inp, disc = _case(elast_n)
    return X.preeq_total(sp, inp, disc)


def test_off_counts_sentinel_bin(monkeypatch):
    r = _run(monkeypatch, False, -0.3)
    assert float(r["xspreeqtot"][0, 1]) > 0.0  # the TALYS sentinel: bin [1, 1] counted as continuum


def test_on_zeroes_projectile_only(monkeypatch):
    off, on = _run(monkeypatch, False, -0.3), _run(monkeypatch, True, -0.3)
    assert float(on["xspreeqtot"][0, 1]) == 0.0
    assert float(on["xssteptot"][0, 1].abs().sum()) == 0.0
    assert float(on["xspreeq"][0, 1].abs().sum()) == 0.0 and float(on["xsstep2"][0, :, 1].abs().sum()) == 0.0
    for t in (0, 2):  # photon and proton books untouched (proton keeps flux, so the photon gate does not fire)
        assert torch.equal(off["xspreeqtot"][0, t], on["xspreeqtot"][0, t])
    assert np.isclose(float(off["xspreeqsum"][0]) - float(on["xspreeqsum"][0]), float(off["xspreeqtot"][0, 1]))


def test_open_last_level_bitwise(monkeypatch):
    off, on = _run(monkeypatch, False, 0.0005), _run(monkeypatch, True, 0.0005)
    for k in ("xspreeqtot", "xssteptot", "xspreeq", "xsstep", "xsstep2", "xspreeqsum"):
        assert torch.equal(off[k], on[k]), k


# --- dup: a daughter named twice in a level's branch list (Hg-197 L16 -> L5 twice) ---------------------------------------
def _nuc():
    J, NJ = 2, 5
    jd = torch.tensor([0, 1, 2, 1], dtype=torch.float64)
    par = torch.tensor([1, 1, -1, 1], dtype=torch.float64)
    xs = torch.zeros(4, NJ, 2, dtype=torch.float64)
    xs[3, 1, 1] = 10.0
    return SimpleNamespace(jdis=jd, parlev=par, xspop_mb=xs, xspopex_mb=torch.tensor([0.0, 0.0, 0.0, 10.0], dtype=torch.float64),
                           branch={3: [(1, 0.3), (0, 0.5), (1, 0.2)]}, zcomp=0, ncomp=0)


def _gc(monkeypatch, v):
    from physics.hf.emission import multiple as M
    if v:
        monkeypatch.setenv("INCOGNITA_KEVLEAK2", v)
    else:
        monkeypatch.setenv("INCOGNITA_KEVLEAK2", "0")  # OFF (default is now 2)
    nuc = _nuc()
    return M.gamma_cascade(nuc, 3), nuc


def test_dup_off_keeps_last_only(monkeypatch):
    rec, nuc = _gc(monkeypatch, None)
    assert rec == {1: 2.0, 0: 5.0}  # TALYS cascade.f90:72: the record keeps the last branch to level 1
    assert float(nuc.xspopex_mb[1]) == 5.0  # the population gets both


def test_dup_on_record_equals_population(monkeypatch):
    for v in ("dup", "1"):
        rec, nuc = _gc(monkeypatch, v)
        assert rec == {1: 5.0, 0: 5.0}
        assert sum(rec.values()) == 10.0 and float(nuc.xspopex_mb[3]) == 0.0


def test_parts_select(monkeypatch):
    from physics.hf import kevleak2 as K
    monkeypatch.setenv("INCOGNITA_KEVLEAK2", "pe")
    assert K.on("pe") and not K.on("dup")
    monkeypatch.setenv("INCOGNITA_KEVLEAK2", "y")
    assert K.on("pe") and K.on("dup")
    monkeypatch.setenv("INCOGNITA_KEVLEAK2", "0")
    assert not K.on("pe") and not K.on("dup")
    monkeypatch.delenv("INCOGNITA_KEVLEAK2")  # KEVLEAK3 gate candidate: unset = default 2 = dup2 + pe2
    assert K.on("dup") and K.on("dup2") and K.on("pe2") and not K.on("pe")
