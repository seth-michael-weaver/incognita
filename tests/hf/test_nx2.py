"""NATIVEX2: the native kernels against the numpy/torch paths they replace (closeness, not
bits). Skipped without a `libnx2` build (scripts/build_nx2_native.sh)."""

from __future__ import annotations

import numpy as np
import pytest

from physics.hf.native import nx2

pytestmark = pytest.mark.skipif(nx2.lib() is None, reason="no libnx2 build")


def _close(a, b, rel=1e-12):
    a, b = np.asarray(a, float), np.asarray(b, float)
    assert a.shape == b.shape
    scale = np.maximum(np.abs(a), np.abs(b))
    bad = np.abs(a - b) > rel * scale + 1e-300
    assert not bad.any(), (np.argwhere(bad)[:5], a[bad][:5], b[bad][:5])


@pytest.mark.parametrize("Z,A", [(26, 56), (82, 208), (20, 40), (40, 90), (26, 55), (66, 163),
                                 (92, 238), (50, 119)])
def test_psf_points_and_photon_rows_match_psf_fast(Z, A):
    import physics.hf.compound.dens_reference as dr
    from physics.hf.compound.psf_fast import fstrength_np
    from physics.hf.compound.psf_nx2 import photon_rows, tgam_points

    gp, _ = dr._gamma_parameters(Z, A)
    if fstrength_np(gp, 5.0, np.array([1.0]), 1, 1) is None:
        pytest.skip("parameter set outside psf_fast")
    rng = np.random.default_rng(Z * 1000 + A)
    L = gp.gammax
    twopi, fn1 = 6.283185307179586, 0.87
    for trial in range(3):
        K = int(rng.integers(1, 1500))
        eg = np.sort(rng.random(K) * rng.choice([2, 10, 25])) + 1e-3
        efs = float(rng.random() * 25)
        got = tgam_points(gp, L, efs, eg, twopi, fn1)
        assert got is not None
        for l in range(1, L + 1):  # noqa: E741
            for irad in (0, 1):
                ref = twopi * eg ** (2 * l + 1) * fn1 * fstrength_np(gp, efs, eg, irad, l)
                _close(got[:, l, irad], ref)
    m, n = 17, 40
    exinc = np.sort(rng.random(m) * 20.0)
    ex0 = np.sort(rng.random(n) * 12.0)
    nexmax0 = rng.integers(-1, n, m)
    s_n = 7.3
    tg = photon_rows(gp, L, exinc, ex0, nexmax0, n, s_n, twopi, fn1)
    ref = np.zeros_like(tg)
    egam = exinc[:, None] - ex0[None, :]
    pos = (egam > 0.0) & (np.arange(n)[None, :] <= nexmax0[:, None])
    ii, kk = np.nonzero(pos)
    for l in range(1, L + 1):  # noqa: E741
        for irad in (0, 1):
            eg = egam[ii, kk]
            ref[ii, kk, l, irad] = (twopi * eg ** (2 * l + 1) * fn1
                                    * fstrength_np(gp, exinc[ii] - s_n, eg, irad, l))
    _close(tg, ref)


def test_psf_table_block_parse_is_the_field_read(monkeypatch):
    """gamma.parameters._psf_block_fast against the per-field read, on the tables of the nuclei a
    few runs read (every tabulated multipole, every temperature column)."""
    import physics.hf.compound.dens_reference as dr
    import physics.hf.gamma.parameters as gpm

    def tables():
        gpm._read_psf_table.cache_clear()
        dr._gamma_parameters.cache_clear()
        out = {}
        for Z, A in ((26, 56), (82, 208), (40, 90), (66, 163), (92, 238), (50, 119), (3, 7)):
            gp, _ = dr._gamma_parameters(Z, A)
            for key, tab in gp.tables.items():
                out[(Z, A, key)] = (tab.e_raw_mev.numpy().copy(), tab.f_raw_mev3.numpy().copy())
        return out

    fast = tables()
    monkeypatch.setattr(gpm, "_psf_block_fast", lambda *a: None)
    slow = tables()
    monkeypatch.undo()
    gpm._read_psf_table.cache_clear()
    dr._gamma_parameters.cache_clear()
    assert fast and fast.keys() == slow.keys()
    for k in fast:
        assert np.array_equal(fast[k][0], slow[k][0]) and np.array_equal(fast[k][1], slow[k][1]), k


@pytest.mark.parametrize("Z,A", [(92, 239), (90, 233), (94, 240), (95, 242)])
def test_wkb_native_matches_wkbfis(Z, A, monkeypatch):
    """fission.wkb.wkb with `nx2_fis_wkb` against the Python `wkbfis` loop (HF_NX2_FIS=0)."""
    import torch

    from physics.hf.fission import wkb as W

    path = W.read_hfbpath(Z, A, 6)
    if path is None:
        pytest.skip("no HFB path")
    got = W.wkb(Z, A, path)
    monkeypatch.setenv("HF_NX2_FIS", "0")
    ref = W.wkb(Z, A, path)
    for name in ("uwkb_mev", "twkb", "twkbdir", "twkbtrans", "twkbphase", "vheight_mev"):
        a, b = getattr(got, name), getattr(ref, name)
        assert a.shape == b.shape, name
        assert torch.allclose(a, b, rtol=1e-11, atol=1e-300), (name, (a - b).abs().max())
