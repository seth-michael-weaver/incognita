"""NATIVEX2 lever `ld2`: the tabulated level densities (`density/ld2_nx2.py`, `native/nx2_ld2.c`)
and `tables.density_table`'s column arithmetic against the paths they replace, `HF_NX2_LD2=0`
against `=1`. Kernels to closeness (skipped without a `libnx2` build), the table itself to the bit.
"""

from __future__ import annotations

import numpy as np
import pytest
import torch

from physics.hf.native import nx2

# actinide residuals (ldmodel >= 4 tables, fission barriers) of their targets
CASES = [(92, 239, 92, 238), (92, 237, 92, 238), (90, 233, 90, 232), (91, 238, 92, 238),
         (94, 240, 94, 239)]


@pytest.fixture(autouse=True)
def _one_thread():
    prev = torch.get_num_threads()
    torch.set_num_threads(1)
    yield
    torch.set_num_threads(prev)


def _close(a, b, rel=1e-12):
    a, b = np.asarray(a, float), np.asarray(b, float)
    assert a.shape == b.shape
    scale = np.maximum(np.abs(a), np.abs(b))
    bad = np.abs(a - b) > rel * scale + 1e-300
    assert not bad.any(), (np.argwhere(bad)[:5], a[bad][:5], b[bad][:5])


def _arms(monkeypatch, fn):
    out = []
    for arm in ("0", "1"):
        monkeypatch.setenv("HF_NX2_LD2", arm)
        out.append(fn())
    return out


def _ld(Z, A, Zt, At):
    from physics.hf.compound.dens_reference import _ld_of

    try:
        ld = _ld_of(Z, A, Zt, At)[0]
    except Exception as exc:  # noqa: BLE001  (structure database absent on this machine)
        pytest.skip(f"no level density for {Z}-{A}: {exc}")
    if not ld.has_table(0):
        pytest.skip("no ground-state table")
    return ld


@pytest.mark.parametrize("Z,A,Zt,At", CASES)
def test_density_table_is_the_loop_bitwise(monkeypatch, Z, A, Zt, At):
    from physics.hf.density.tables import density_table

    ld = _ld(Z, A, Zt, At)
    fl = _fission_ld(Z, A, Zt, At)
    cases = [(ld.ldmodel, 0, None, True), (ld.ldmodel, 0, None, False), (4, 0, None, True)]
    for ib in range(1, fl.nfisbar + 1):
        cases.append((ld.ldmodel, ib, None, True))
        for ax in (1, 2, 3, 5):
            cases.append((ld.ldmodel, ib, _with_axtype(fl, ib, ax), True))
    for model, ib, ldx, par in cases:
        a, b = _arms(monkeypatch, lambda: density_table(Z, A, model, ib, flagparity=par, ld=ldx))
        assert (a is None) == (b is None)
        if a is None:
            continue
        for f in ("ldtable_per_mev", "ldtottable_per_mev", "ldtottableP_per_mev", "ldtableT_mev",
                  "ldtableN"):
            x, y = getattr(a, f), getattr(b, f)
            assert x.shape == y.shape and x.dtype == y.dtype and torch.equal(x, y), (f, model, ib)
        assert (a.nendens, a.Edensmax_mev) == (b.nendens, b.Edensmax_mev)


def _fission_ld(Z, A, Zt, At):
    """The level density with fission barriers, as `fission.chain` builds it."""
    from physics.hf.compound.dens_reference import structure_of
    from physics.hf.density.matching import densitymatch
    from physics.hf.density.parameters import densitypar
    from physics.hf.density.tables import attach_tables
    from physics.hf.fission.parameters import barrier_levels, fission_parameters
    from physics.hf.structure.levels import discrete_levels

    o, p, m = structure_of(Zt, At)
    fp = fission_parameters(Z, A, o, p, masses=m)
    lv = discrete_levels(Z, A, o, m, p)
    return densitymatch(attach_tables(densitypar(Z, A, o, p, m, lv, barriers=barrier_levels(fp))))


def _with_axtype(ld, ib, ax):
    from dataclasses import replace

    t = list(ld.axtype)
    t[ib] = ax
    return replace(ld, axtype=tuple(t))


@pytest.mark.skipif(nx2.lib() is None, reason="no libnx2 build")
@pytest.mark.parametrize("Z,A,Zt,At", CASES)
def test_table_density_matches_the_torch_branch(monkeypatch, Z, A, Zt, At):
    from physics.hf.density.models import density

    ld = _ld(Z, A, Zt, At)
    rng = np.random.default_rng(Z * 1000 + A)
    # below 0, below ptable, on edens nodes, inside, past Edensmax
    e = np.concatenate([[-1.0, 0.0, 0.1, 0.25, 5.0, 10.0, 30.0, 150.0, 200.0, 210.0],
                        rng.random(40) * 25.0])
    ee = torch.tensor(e, dtype=torch.float64)
    for odd in (0, 0.5):
        J = torch.arange(41, dtype=torch.float64) + odd
        for par in (-1, 1):
            a, b = _arms(monkeypatch,
                         lambda: density(ld, ee.reshape(-1, 1), J.reshape(1, -1), par, 0))
            _close(a.numpy(), b.numpy())
            a, b = _arms(monkeypatch, lambda: density(ld, ee, torch.full_like(ee, 7.5), par, 0))
            _close(a.numpy(), b.numpy())


@pytest.mark.skipif(nx2.lib() is None, reason="no libnx2 build")
@pytest.mark.parametrize("Z,A,Zt,At", CASES)
def test_table_rhogrid_matches_rhogrid_of(monkeypatch, Z, A, Zt, At):
    from physics.hf.compound.dens_reference import rhogrid_of
    from physics.hf.density.parameters import NUMJ

    _ld(Z, A, Zt, At)
    rng = np.random.default_rng(Z * 1000 + A + 1)
    for n, top in ((40, 12.0), (25, 25.0)):
        ex = np.sort(rng.random(n)) * top
        dex = np.full(n, top / n)
        maxj = rng.integers(-1, NUMJ + 1, n).astype(np.int64)
        for nlast in (0, 5, n):
            a, b = _arms(monkeypatch, lambda: rhogrid_of(Z, A, Zt, At, ex, dex, maxj, nlast))
            assert isinstance(b, np.ndarray)
            _close(a, b, 1e-11)


@pytest.mark.skipif(nx2.lib() is None, reason="no libnx2 build")
def test_a_gradient_keeps_the_torch_branch():
    from physics.hf.density.ld2_nx2 import table_density

    ld = _ld(*CASES[0])
    tab = ld.tables[0]
    ct = torch.tensor(float(ld.ctable[0]), dtype=torch.float64, requires_grad=True)
    e = torch.tensor([3.0], dtype=torch.float64)
    assert table_density(tab, ct, ld.ptable_mev[0], e, e, 1, 39) is None


@pytest.mark.skipif(nx2.lib() is None, reason="no libnx2 build")
@pytest.mark.parametrize("Z,A,Zt,At", CASES)
def test_fission_level_densities_match_the_density_loop(monkeypatch, Z, A, Zt, At):
    from physics.hf.compound.dens_reference import structure_of
    from physics.hf.fission.parameters import fission_parameters
    from physics.hf.fission.transmission import fission_level_densities

    _ld(Z, A, Zt, At)
    ld = _fission_ld(Z, A, Zt, At)
    o, p, m = structure_of(Zt, At)
    fp = fission_parameters(Z, A, o, p, masses=m)
    if int(fp.nfisbar) == 0:
        pytest.skip("no barrier")
    for top in (3.0, 6.3, 12.0, 30.0):
        a, b = _arms(monkeypatch, lambda: fission_level_densities(fp, ld, top, odd=A % 2))
        assert a.nbintfis == b.nbintfis
        assert torch.equal(a.eintfis_mev, b.eintfis_mev)
        _close(a.rhofis.numpy(), b.rhofis.numpy())
