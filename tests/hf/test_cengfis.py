"""CENGFIS (ROUTE100 WP7): the fission transmissions from `fission/fis_ceng.py` and
`native/fission.c` against the NATIVEX2 `fis2`/`ld2` paths they replace on the chart. The barrier
slopes and ladder weights are bit-identical; the widths and transmissions are held to 1e-13.
Skipped without a `libnx2` build or TALYS's structure data.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest
import torch

from physics.hf.native import nx2

TALYS_DIR = Path(__import__("os").environ.get("TALYS_DIR", Path.home() / "opt/talys-src"))
pytestmark = [
    pytest.mark.skipif(nx2.lib() is None, reason="no libnx2 build"),
    pytest.mark.skipif(not (TALYS_DIR / "structure").is_dir(), reason="no TALYS structure/"),
]

# (target, nucleus): two- and three-humped barriers, even and odd A
CASES = [(92, 238, 92, 239), (92, 238, 92, 237), (90, 232, 90, 233), (88, 223, 88, 224)]


@pytest.fixture(autouse=True)
def _one_thread():
    prev = torch.get_num_threads()
    torch.set_num_threads(1)
    yield
    torch.set_num_threads(prev)


def _close(a, b, rel=1e-13, tiny=1e-300):
    a, b = np.asarray(a, float), np.asarray(b, float)
    assert a.shape == b.shape
    bad = np.abs(a - b) > rel * np.maximum(np.abs(a), np.abs(b)) + tiny
    assert not bad.any(), (np.argwhere(bad)[:5], a[bad][:5], b[bad][:5])


def _nucleus(Zt, At, Z, A, hill_wheeler=False):
    from physics.hf.fission.chain import FissionChain, _Nucleus
    from physics.hf.input.defaults import default_options

    chain = FissionChain(Zt, At, default_options(Zt, At))
    n = chain.nucleus(Z, A)
    if n is None:
        pytest.skip("does not fission")
    if hill_wheeler:
        n = _Nucleus(fp=replace(n.fp, fismodelx=3), ld=n.ld, odd=n.odd, grids={})
    return chain, n


def _tops(n):
    hi = float(n.fp.fecont_mev[1:int(n.fp.nfisbar) + 1].max())
    # refined bins (dex < DEXMIN), a full grid, far above. A top at or below a barrier's fecont is
    # left out: the fis2 path then reads its all-zero grid's 500 points from an array sized by the
    # other barriers, out of bounds, and an energy at or above that fecont picks up whatever lies
    # there (the chart's cells are bitwise equal, so it never did; test_below_every_barrier).
    return [hi + 3.0, 13.9, 24.3]


@pytest.mark.parametrize("Zt,At,Z,A", CASES)
def test_grid_slopes_and_weights_are_the_fis2_bits(Zt, At, Z, A):
    from physics.hf.fission import fis2_nx2, fis_ceng

    chain, n = _nucleus(Zt, At, Z, A)
    coef_fn = fis2_nx2._kernels()[0]
    wfn = nx2.kernel("nx2_fis2_ladder_weights",
                     [nx2.P, nx2.P, nx2.P, nx2.I64, nx2.DBL, nx2.P, nx2.I64, nx2.I64, nx2.DBL,
                      nx2.DBL, nx2.DBL, nx2.P, nx2.P, nx2.I64, nx2.P, nx2.P], nx2.INT)
    w_ceng = fis_ceng._kernels()[1]
    for top in _tops(n):
        co = fis_ceng.grid_coefficients(chain, n, top)
        grid = chain._grid(n, top)
        for ibar in range(1, int(n.fp.nfisbar) + 1):
            ref = fis2_nx2._coefficients(coef_fn, grid, ibar) if grid.nbintfis[ibar] >= 3 else None
            got = co[ibar]
            assert (ref is None) == (got is None)
            if ref is None:
                continue
            for r, g in zip(ref, got, strict=True):
                assert np.array_equal(r, g)
            elow, emid, eup = got[:3]
            e = np.sort(np.concatenate([np.linspace(0.0, top + 1.0, 97), elow[::7], emid[::11],
                                        [float(n.fp.fecont_mev[ibar])]]))
            mode, bfis, wfis, u, col, nbins = fis2_nx2._penetrability(n.fp, ibar, n.ld.deltaW_mev)
            S, E = elow.shape[0], e.shape[0]
            outs = []
            for fn in (wfn, w_ceng):
                W1, W2 = np.zeros((E, S)), np.zeros((E, S))
                assert fn(nx2.ptr(elow), nx2.ptr(emid), nx2.ptr(eup), S,
                          float(n.fp.fecont_mev[ibar]), nx2.ptr(e), E, mode, bfis, wfis,
                          2.0 * np.pi, nx2.ptr(u), nx2.ptr(col), nbins, nx2.ptr(W1),
                          nx2.ptr(W2)) == 0
                outs.append((W1, W2))
            assert np.array_equal(outs[0][0], outs[1][0]) and np.array_equal(outs[0][1], outs[1][1])


@pytest.mark.parametrize("Zt,At,Z,A", CASES)
@pytest.mark.parametrize("hill_wheeler", [False, True])
def test_ladder_widths_match_ladder_bin_widths(Zt, At, Z, A, hill_wheeler):
    from physics.hf.fission import fis_ceng
    from physics.hf.fission.fission_batch_ladder import ladder_bin_widths

    chain, n = _nucleus(Zt, At, Z, A, hill_wheeler)
    for top in _tops(n):
        m = 37
        dex = np.full(m, max(top, 1.0) / m)
        ex = (np.arange(m) + 0.5) * dex
        exmax = float(ex[-1] + 0.5 * dex[-1])
        ref = ladder_bin_widths(n.fp, chain._grid(n, top), n.ld, ex, dex, exmax, chain.o,
                                maxj=chain.maxj, fnorm=0.93)
        for nj in (chain.maxj + 1, 23):
            got = fis_ceng.ladder_widths(chain, n, ex, dex, exmax, top, 0.93, nj)
            assert got.shape == (m, nj, 2)
            _close(ref[:, :nj], got)


@pytest.mark.parametrize("Zt,At,Z,A", CASES)
@pytest.mark.parametrize("hill_wheeler", [False, True])
def test_target_transmission_matches_fission_transmission(Zt, At, Z, A, hill_wheeler):
    from physics.hf.fission import fis_ceng
    from physics.hf.fission.transmission import fission_transmission

    chain, n = _nucleus(Zt, At, Z, A, hill_wheeler)
    hi = float(n.fp.fecont_mev[1:int(n.fp.nfisbar) + 1].max())
    for e in [*_tops(n), hi + 0.017]:  # not at a fecont: see _tops (fis2 would read past its grid)
        ft = fission_transmission(n.fp, chain._grid(n, e), n.ld, e, 0.0, chain.o, exmax_mev=e,
                                  odd=n.odd, maxj=chain.maxj, primary=True, fnorm=1.07)
        tf, ta, ra = fis_ceng.target_transmission(chain, n, e, 1.07)
        _close(ft.tfis.numpy(), tf)
        _close(ft.tfisA.numpy(), ta)
        _close(ft.rhofisA.numpy(), ra)


@pytest.mark.parametrize("Zt,At,Z,A", CASES[:2])
def test_below_every_barrier(Zt, At, Z, A):
    """A top at or below every fecont: one all-zero triple per barrier, zero widths, zero tfis,
    and t1barrier's 1e-30 floor on tfisA(0) only where the energy reaches fecont."""
    from physics.hf.fission import fis_ceng

    chain, n = _nucleus(Zt, At, Z, A)
    nb = int(n.fp.nfisbar)
    lo = float(n.fp.fecont_mev[1:nb + 1].min())
    co = fis_ceng.grid_coefficients(chain, n, lo - 0.5)
    assert all(co[i][0].shape == (1,) and not co[i][3].any() for i in range(1, nb + 1))
    ex = np.array([0.1, 0.3, lo - 0.6])
    w = fis_ceng.ladder_widths(chain, n, ex, np.full(3, 0.2), lo - 0.5, lo - 0.5, 1.0, 12)
    assert w.shape == (3, 12, 2) and not w.any()
    tf, ta, ra = fis_ceng.target_transmission(chain, n, lo - 0.5, 1.0)
    assert not tf.any() and not ta.any() and np.all(ra == 1.0)


def test_compound_target_and_lever_off(monkeypatch):
    from physics.hf.fission.chain import FissionChain
    from physics.hf.input.defaults import default_options

    outs = []
    for arm in ("0", "1"):
        monkeypatch.setenv("HF_NX2_CENGFIS", arm)
        chain = FissionChain(92, 238, default_options(92, 238))
        outs.append([chain.compound_target(92, 239, e, fnorm=1.0) for e in (4.9, 11.3, 20.2)])
    for a, b in zip(*outs, strict=True):
        assert a["nfisbar"] == b["nfisbar"] and a["tfis"].keys() == b["tfis"].keys()
        for k in a["tfis"]:
            _close(a["tfis"][k], b["tfis"][k])
            _close(a["tfisA"][k], b["tfisA"][k])
            _close(a["rhofisA"][k], b["rhofisA"][k])
    monkeypatch.setenv("HF_NX2_CENGFIS", "0")
    from physics.hf.fission import fis_ceng

    assert fis_ceng._kernels() is None


def test_hfbpath_parse_cache_is_the_uncached_read():
    from physics.hf.fission import wkb

    for fismodel in (5, 6):
        wkb._PARSED.clear()
        cold = wkb.read_hfbpath(92, 238, fismodel, vfiscor=1.1, rmiufiscor=0.9)
        warm = wkb.read_hfbpath(92, 238, fismodel, vfiscor=1.1, rmiufiscor=0.9)
        if cold is None:
            assert warm is None
            continue
        for f in ("betafis", "vfis_mev"):
            assert torch.equal(getattr(cold, f), getattr(warm, f))
        path = str(wkb.hfbpath_file(92, fismodel))
        blocks = {ia: rows for ia, _nb, rows in wkb._blocks(Path(path), fismodel)}
        parsed = {ia: rows for ia, _nb, rows in wkb._PARSED[(path, fismodel)]}
        line = blocks[238][3]
        if fismodel == 5:
            assert parsed[238][3] == (float(np.float32(line[0:10])), float(np.float32(line[30:40])))
        else:
            tok = line.split()
            assert parsed[238][3][3] == int(tok[5])
