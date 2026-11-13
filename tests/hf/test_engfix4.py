"""ENGFIX4 (bug hunt round 4, engine code): switches read per call, the grid's NUMEN error, `equispec`
on the reference grid, the `INCOGNITA_GRIDTOP` exits, the isomer's targetE, the compound record key, EWFC's memo identity.

The stage disk cache key is tested in tests/hf/test_stagedisk.py, the per-run results of normal
targets by the bit-identity checks (tests/hf/test_perfhf_gate.py, test_perfcasc_gate.py, ...)."""

from __future__ import annotations

import gc

import numpy as np
import pytest
import torch


@pytest.fixture
def fresh(monkeypatch):
    """Per-target caches dropped on the way in and out; no deck lines; `INCOGNITA_GRIDTOP` at its default (ON)."""
    from physics.hf import chartrun
    from physics.hf.input import fitlib

    monkeypatch.delenv("INCOGNITA_GRIDTOP", raising=False)  # conftest pins the TALYS grid
    for k in (fitlib.ENV, fitlib.ENV_LINES, fitlib.ENV_LINES_FILE):
        monkeypatch.delenv(k, raising=False)
    fitlib.deactivate()
    chartrun.drop_target_caches()

    def deck(Z: int, A: int, lines: str, Ltarget: int = 0):
        monkeypatch.setenv(fitlib.ENV, "lines")
        monkeypatch.setenv(fitlib.ENV_LINES, lines)
        fitlib.deactivate()
        chartrun.drop_target_caches()
        assert fitlib.activate(Z, A, Ltarget=Ltarget) is not None

    yield deck
    fitlib.deactivate()
    chartrun.drop_target_caches()


# ---------------------------------------------------------------------------------------- 2. switches per call


def _now(mod, fn: str, const: str):
    """The module's value now: the ENGFIX4 function, or the import-time constant it replaced."""
    f = getattr(mod, fn, None)
    return f() if f is not None else getattr(mod, const)


def test_switches_follow_the_environment_after_import(monkeypatch):
    from physics.hf.ecis import incident as I
    from physics.hf.ecis import solver
    from physics.hf.gamma import actphys, ggnorm, scissors
    from physics.hf.omp import regional

    for var, val, get, want in (
            ("INCOGNITA_OMP_REGION", "1", regional.enabled, True),
            ("INCOGNITA_OMP_DEFORMED", "1", regional.deformed_enabled, True),
            ("INCOGNITA_GGAMMA_NORM", "ripl3", ggnorm.mode, "ripl3"),
            ("INCOGNITA_ACTPHYS", "gg", actphys.mode, "gg"),
            ("INCOGNITA_M1_SCISSORS", "k17", scissors.mode, "k17"),
            ("INCOGNITA_ECMSTABLE", "0", lambda: _now(solver, "ecmstable", "ECMSTABLE"), False)):
        monkeypatch.delenv(var, raising=False)
        before = get()
        monkeypatch.setenv(var, val)
        assert get() == want, var
        monkeypatch.delenv(var)
        assert get() == before, var
    e = torch.tensor([0.001, 0.05, 0.0501, 20.0], dtype=torch.float64)
    monkeypatch.setenv("HF_INC_REFINE", "2")
    assert I._refine_axis(e, 1).tolist() == [2, 2, 1, 1]
    monkeypatch.setenv("HF_INC_REFINE_EMAX", "1.0")
    assert I._refine_axis(e, 1).tolist() == [2, 2, 2, 1]


def test_numen_follows_the_environment(monkeypatch):
    from physics.hf.core import grids

    monkeypatch.delenv("INCOGNITA_NUMEN", raising=False)
    assert len(grids.egrid_values(25.0)[0]) == 261
    monkeypatch.setenv("INCOGNITA_NUMEN", "300")
    assert len(grids.egrid_values(25.0)[0]) == 301


def test_set_mode_writes_the_switch(monkeypatch):
    from physics.hf.gamma import scissors
    from physics.hf.omp import regional

    monkeypatch.delenv("INCOGNITA_M1_SCISSORS", raising=False)
    monkeypatch.delenv("INCOGNITA_OMP_REGION", raising=False)
    try:
        assert scissors.set_mode("s2") == ""
        assert scissors.mode() == "s2"
        assert regional.set_enabled(True) is False and regional.enabled()
    finally:
        scissors.set_mode("")
        regional.set_enabled(False)
    assert scissors.mode() == "" and not regional.enabled()


# ---------------------------------------------------------------------------------------- 8. NUMEN overflow


def test_grid_past_numen_raises():
    from physics.hf.core.grids import egrid_values

    eg, maxen = egrid_values(30.0, 1, 260)  # a normal grid: well inside
    assert maxen < 260 and eg[maxen] <= 30.0
    with pytest.raises(ValueError, match="numen"):
        egrid_values(30.0, 1, 60)  # 60 points end near 4 MeV
    with pytest.raises(ValueError, match="numen"):
        egrid_values(2000.0, 1, 260)
    eg, maxen = egrid_values(30.0, 1, 60, True, 20.0)  # equispec replaces the grid: no error
    assert maxen == 58


# ---------------------------------------------------------------------------------------- 6. equispec


def test_equispec_reference_grid(fresh):
    from physics.hf.compound.dens_reference import run_grid

    fresh(26, 56, "equispec y")
    rg = run_grid(26, 56, 20.0)
    assert rg.options.flagequispec
    assert rg.maxen == 248  # numen 250 - 2 (grid.f90:149)
    assert rg.egrid[125] == pytest.approx(12.5, abs=1e-5)


# ---------------------------------------------------------------------------------------- 7. gridtop exits


def test_gridtop_exits_rule():
    from physics.hf.core.grids import gridtop_exits

    s = [0.0, 7.5, 6.0, 9.0, 10.0, 8.0, -3.6]
    full = np.ones((5, 5))
    assert gridtop_exits(s, full) == s
    no_alpha_residual = full.copy()
    no_alpha_residual[2, 2] = 0.0
    assert gridtop_exits(s, no_alpha_residual) == s[:6]
    assert gridtop_exits(s, full, (True, True, True, True, True, True, False)) == s[:6]


@pytest.mark.parametrize("Z,A", [(1, 2), (2, 3), (3, 6), (3, 7), (4, 9)])
def test_gridtop_ignores_exits_without_a_residual(fresh, Z, A):
    """The grid top of a very light target is set by exits that exist: every exit whose residual
    has no mass is left out of the gridtop margin."""
    from physics.hf.compound.dens_reference import run_grid
    from physics.hf.core.grids import emission_limit

    rg = run_grid(Z, A, 20.0)
    m = rg.m.mass_amu.numpy()
    pz, pn = (0, 0, 1, 1, 1, 2, 2), (0, 1, 0, 1, 2, 1, 2)
    real = [rg.s0[t] for t in range(7) if m[pz[t], pn[t]] > 0.0]
    want = emission_limit(20.0, rg.s0[rg.options.k0], 0.0, s_exits_mev=real)
    top = rg.egrid[rg.maxen]
    assert top <= want < top + 2.0 + 1e-4  # the last point below Elimit (steps <= 2 MeV under 200 MeV)


# ---------------------------------------------------------------------------------------- 3. isomeric targets


def test_isomer_energy_enters_etotal_and_grid(fresh, monkeypatch):
    """targetE (nuclides.f90:234) is in Etotal (energies.f90:131) and the grid top (grid.f90:123).

    Stock TALYS-2.25 cannot run Hf-178m2 (level 109 > numlev = 40), so targetE is injected here as
    Hf-178m2's 2.446090 MeV on a ground-state run (the real excited-target runs: tests/hf/test_kwcov_biso.py)."""
    from physics.hf import chartrun
    from physics.hf.compound.dens_reference import run_grid
    from physics.hf.core.grids import f32
    from physics.hf.emission.feed_reference import etotal_of
    from physics.hf.structure import scalars

    Z, A, E, te = 72, 178, 14.0, 2.446090
    g_gs, et_gs = run_grid(Z, A, E), etotal_of(Z, A, E, 1.0, 1)
    assert g_gs.target_e == 0.0
    chartrun.drop_target_caches()
    monkeypatch.setattr(scalars, "target_energy_mev", lambda Z, A, o, m, p: te)
    g_m = run_grid(Z, A, E)
    assert g_m.target_e == te
    assert etotal_of(Z, A, E, 1.0, 1) - et_gs == pytest.approx(float(f32(te)), abs=2e-6)
    step = g_m.egrid[g_m.maxen] - g_m.egrid[g_m.maxen - 1]
    assert g_m.egrid[g_m.maxen] - g_gs.egrid[g_gs.maxen] == pytest.approx(te, abs=step + 1e-4)
    chartrun.drop_target_caches()


def test_excited_target_hf178m2_out_of_talys_range(fresh):
    """KWCOV GAP (isomeric targets, docs/hf/ISOMERIC_TARGETS.md): the excited target is ported now, but Hf-178m2 is
    level 109 and the run stops where stock TALYS-2.25 does (checkvalue.f90:467, numlev = 40), before any level is
    read; the energy bookkeeping itself is the test above."""
    from physics.hf.compound.dens_reference import _structure_of
    from physics.hf.input.defaults import reject_unported
    from physics.hf.structure.scalars import target_energy_mev

    fresh(72, 178, "ltarget 109", Ltarget=109)
    o, p, m = _structure_of(72, 178)
    assert o.Ltarget == 109
    for call in (lambda: target_energy_mev(72, 178, o, m, p), lambda: reject_unported(o)):
        with pytest.raises(ValueError, match="0 <= Ltarget <= 40"):
            call()


# ---------------------------------------------------------------------------------------- 4. compound record key


def test_record_key_follows_options_deck_and_env(monkeypatch):
    import dataclasses
    from types import SimpleNamespace

    from physics.hf.input.defaults import default_options
    from physics.hf.record import caches

    o = default_options(26, 56)

    def cas(**kw):
        base = dict(Zt=26, At=56, k0=1, enincmax=20.0, energies=(1.0, 20.0), fit=(), options=o,
                    density_overrides=None, omp_overrides=None, diff_params=False)
        return SimpleNamespace(**{**base, **kw})

    monkeypatch.delenv("INCOGNITA_ALPHATEMP", raising=False)
    key = caches.record_key(cas())
    caches.check_key(key, cas())
    for bad in (cas(options=dataclasses.replace(o, tfold=False)),
                cas(options=dataclasses.replace(o, alphatemp=0.0)),
                cas(_fit_cards=("ltarget", 2))):
        with pytest.raises(caches.RecordMismatch):
            caches.check_key(key, bad)
    caches.check_key(key, cas(options=dataclasses.replace(o, strength=8)))  # a PSF option: not an input
    monkeypatch.setenv("INCOGNITA_ALPHATEMP", "0")
    with pytest.raises(caches.RecordMismatch):
        caches.check_key(key, cas())


# ---------------------------------------------------------------------------------------- 5. EWFC memo identity


class _Opts:
    soswitch_mev = 3.0


def test_ewfc_memo_never_serves_another_options_object(monkeypatch):
    """`cc_blocks` keys on id(options): a new Options at a freed one's address must not get its blocks."""
    from physics.hf.compound import ewfc

    made = []
    monkeypatch.setattr(ewfc, "_cc_blocks_compute", lambda Z, A, e, band, options, tj: made.append(options) or object())
    ewfc._MEMO.clear()
    o1 = _Opts()
    v1 = ewfc.cc_blocks(26, 56, 1.0, {}, o1, 3)
    assert ewfc.cc_blocks(26, 56, 1.0, {}, o1, 3) is v1 and len(made) == 1
    old = id(o1)
    del o1, made[:]
    gc.collect()
    keep, o2 = [], None
    for _ in range(20000):  # CPython hands a freed object's address to the next one of its size
        x = _Opts()
        if id(x) == old:
            o2 = x
            break
        keep.append(x)
    if o2 is not None:  # the old object was freed and its address reused
        assert ewfc.cc_blocks(26, 56, 1.0, {}, o2, 3) is not v1
    else:  # the memo holds the old object, so its address cannot be reused
        assert any(v[0] is not None and id(v[0]) == old for v in ewfc._MEMO.values())
    ewfc._MEMO.clear()


# ---------------------------------------------------------------------------------------- CC cache keys


@pytest.mark.parametrize("var,val", [("INCOGNITA_ECMSTABLE", "0"), ("INCOGNITA_CCSOCB", "1"),
                                     ("INCOGNITA_OMP_REGION", "1"), ("INCOGNITA_OMP_DEFORMED", "1"),
                                     ("HF_INC_REFINE", "2"), ("HF_INC_REFINE_EMAX", "1.0"),
                                     ("HF_CC_MODNUM", "0")])
def test_cc_cache_keys_follow_every_switch_per_call(monkeypatch, tmp_path, var, val):
    """The CC row cache's version and the row / batch-carry keys (`ccdisk.env_token`, which every
    `incident._SOLVED` key ends in) follow the switches without a cache reset."""
    from physics.hf.ecis import ccdisk

    monkeypatch.setenv(ccdisk.ENV_VAR, str(tmp_path))
    monkeypatch.delenv(var, raising=False)
    v0, t0 = ccdisk._version(), ccdisk.env_token()
    monkeypatch.setenv(var, val)
    assert ccdisk._version() != v0 and ccdisk.env_token() != t0
    monkeypatch.setenv("INCOGNITA_STAGE_CACHE", str(tmp_path))  # a cache location: not a key
    assert ccdisk.env_token() == ccdisk.env_token()
    t1 = ccdisk.env_token()
    monkeypatch.delenv("INCOGNITA_STAGE_CACHE")
    assert ccdisk.env_token() == t1
    monkeypatch.delenv(var)
    assert ccdisk._version() == v0 and ccdisk.env_token() == t0


def test_cc_cache_keys_ignore_switches_the_solve_never_reads(monkeypatch):
    """A production run sets hold-rule / pre-equilibrium switches between its set-up passes; they
    are not CC inputs, so the rows the run already solved are reused (re-solving them in another
    batch would move last bits)."""
    from physics.hf.ecis import ccdisk

    t0 = ccdisk.env_token()
    for var, val in (("INCOGNITA_ISOHOLD", "79,198,0.98"), ("INCOGNITA_ISOE2", "e"), ("INCOGNITA_FEWRES", "off"),
                     ("INCOGNITA_PEWINDOW", "g"), ("INCOGNITA_CC_BATCHCACHE", "/tmp/x"), ("INCOGNITA_TRAPFIX", "1")):
        monkeypatch.setenv(var, val)
    assert ccdisk.env_token() == t0
    assert "INCOGNITA_ECMSTABLE" in ccdisk.env_names() and "HF_INC_REFINE" in ccdisk.env_names()
