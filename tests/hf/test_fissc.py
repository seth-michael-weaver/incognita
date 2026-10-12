"""FISSC (development notes): the fission ladder with fewer exp/log (F2 grid, F3 WKB weights
by recurrence), distinct-energy rows and active-triple contraction (F3/F4) and an exact-input ladder
cache (F1), against the CENGFIS kernels they replace (`HF_NX2_FISSC=0`, bitwise the base; see
tests/hf/test_cengfis.py). Held to closeness: slopes and weights 1e-10, widths and transmissions 1e-9.
"""

from __future__ import annotations

import numpy as np
import pytest

from physics.hf.native import nx2

from tests.hf.test_cengfis import CASES, TALYS_DIR, _nucleus, _one_thread, _tops  # noqa: F401

pytestmark = [
    pytest.mark.skipif(nx2.lib() is None, reason="no libnx2 build"),
    pytest.mark.skipif(not (TALYS_DIR / "structure").is_dir(), reason="no TALYS structure/"),
]


def _close(a, b, rel, tiny=1e-300):
    a, b = np.asarray(a, float), np.asarray(b, float)
    assert a.shape == b.shape
    bad = np.abs(a - b) > rel * np.maximum(np.abs(a), np.abs(b)) + tiny
    assert not bad.any(), (np.argwhere(bad)[:5], a[bad][:5], b[bad][:5])


def _fresh(n):
    n.__dict__.pop("_ceng_coef", None)
    n.__dict__.pop("_fissc_ladder", None)


def test_off_selects_the_cengfis_kernels(monkeypatch):
    from physics.hf.fission import fis_ceng

    monkeypatch.setenv("HF_NX2_FISSC", "0")
    assert not any(fis_ceng._fissc(f) for f in ("F1", "F2", "F3", "F4"))
    monkeypatch.setenv("HF_NX2_FISSC", "1")
    assert all(fis_ceng._fissc(f) for f in ("F1", "F2", "F3", "F4"))
    monkeypatch.setenv("HF_NX2_FISSC_F2", "0")
    assert not fis_ceng._fissc("F2") and fis_ceng._fissc("F3")


@pytest.mark.parametrize("Zt,At,Z,A", CASES)
def test_grid_slopes_and_weights_close(Zt, At, Z, A, monkeypatch):
    from physics.hf.fission import fis2_nx2, fis_ceng

    chain, n = _nucleus(Zt, At, Z, A)
    for top in _tops(n):
        got = {}
        for flag in ("0", "1"):
            monkeypatch.setenv("HF_NX2_FISSC", flag)
            _fresh(n)
            got[flag] = (fis_ceng.grid_coefficients(chain, n, top), fis_ceng._kernels()[1])
        for ibar in range(1, int(n.fp.nfisbar) + 1):
            ref, new = got["0"][0][ibar], got["1"][0][ibar]
            assert (ref is None) == (new is None)
            if ref is None:
                continue
            for k, (r, g) in enumerate(zip(ref, new, strict=True)):
                if k < 3:
                    assert np.array_equal(r, g)  # the grid energies themselves
                else:
                    _close(r, g, 1e-10)
            elow, emid, eup = ref[:3]
            e = np.sort(np.concatenate([np.linspace(0.0, top + 1.0, 97), elow[::7], emid[::11],
                                        [float(n.fp.fecont_mev[ibar])]]))
            mode, bfis, wfis, u, col, nbins = fis2_nx2._penetrability(n.fp, ibar, n.ld.deltaW_mev)
            S, E = elow.shape[0], e.shape[0]
            outs = []
            for fn in (got["0"][1], got["1"][1]):
                W1, W2 = np.zeros((E, S)), np.zeros((E, S))
                assert fn(nx2.ptr(elow), nx2.ptr(emid), nx2.ptr(eup), S,
                          float(n.fp.fecont_mev[ibar]), nx2.ptr(e), E, mode, bfis, wfis,
                          2.0 * np.pi, nx2.ptr(u), nx2.ptr(col), nbins, nx2.ptr(W1),
                          nx2.ptr(W2)) == 0
                outs.append((W1, W2))
            for a, b in zip(outs[0], outs[1], strict=True):
                assert np.array_equal(a == 0.0, b == 0.0)
                _close(a, b, 1e-10)


@pytest.mark.parametrize("Zt,At,Z,A", CASES)
@pytest.mark.parametrize("hill_wheeler", [False, True])
def test_ladder_and_target_close(Zt, At, Z, A, hill_wheeler, monkeypatch):
    from physics.hf.fission import fis_ceng

    chain, n = _nucleus(Zt, At, Z, A, hill_wheeler)
    for top in _tops(n):
        m = 37
        dex = np.full(m, max(top, 1.0) / m)
        ex = (np.arange(m) + 0.5) * dex
        exmax = float(ex[-1] + 0.5 * dex[-1])
        for nj in (chain.maxj + 1, 23):
            res = {}
            for flag in ("0", "1"):
                monkeypatch.setenv("HF_NX2_FISSC", flag)
                _fresh(n)
                res[flag] = (fis_ceng.ladder_widths(chain, n, ex, dex, exmax, top, 0.93, nj),
                             fis_ceng.target_transmission(chain, n, top, 1.07))
            _close(res["0"][0], res["1"][0], 1e-9)
            for a, b in zip(res["0"][1], res["1"][1], strict=True):
                _close(a, b, 1e-9)


def test_ladder_cache_is_exact_and_a_copy(monkeypatch):
    from physics.hf.fission import fis_ceng

    monkeypatch.setenv("HF_NX2_FISSC", "1")
    chain, n = _nucleus(92, 238, 92, 239)
    _fresh(n)
    top = _tops(n)[0]
    m = 31
    dex = np.full(m, top / m)
    ex = (np.arange(m) + 0.5) * dex
    exmax = float(ex[-1] + 0.5 * dex[-1])
    a = fis_ceng.ladder_widths(chain, n, ex, dex, exmax, top, 0.93, 30)
    assert len(n.__dict__["_fissc_ladder"]) == 1
    a[...] = -1.0  # the caller's array is its own
    b = fis_ceng.ladder_widths(chain, n, ex, dex, exmax, top, 0.93, 30)
    monkeypatch.setenv("HF_NX2_FISSC_F1", "0")
    c = fis_ceng.ladder_widths(chain, n, ex, dex, exmax, top, 0.93, 30)
    assert np.array_equal(b, c)
    d = fis_ceng.ladder_widths(chain, n, ex, dex * (1 + 1e-15), exmax, top, 0.93, 30)
    assert d.shape == c.shape  # a different input is a miss, not a hit
