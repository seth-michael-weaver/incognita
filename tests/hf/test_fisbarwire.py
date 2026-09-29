"""FISBARWIRE: `fismodel` / `fisbaradjust` / `fishwadjust` as PARAMWIRE parameters, reaching every
fission path. The Hill-Wheeler height and curvature (`barriers.barrier_height`) carry the adjust
factors (t1barrier.f90:99-121); the torch loop, NATIVEX2's `fis2` C kernels and CENGFIS's
`fission.c` are held to each other at 1e-12 under `fismodel 1` with both factors off 1, and the
WKB default ignores them bit for bit, as TALYS does. Skipped without a `libnx2` build or TALYS's
structure data.
"""

from __future__ import annotations

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

ZT, AT = 92, 235
FIT = (("fismodel", 0, 0, 1.0), ("fisbaradjust", 92, 236, 1.15), ("fishwadjust", 92, 236, 0.9))


@pytest.fixture(autouse=True)
def _one_thread():
    prev = torch.get_num_threads()
    torch.set_num_threads(1)
    yield
    torch.set_num_threads(prev)


def _chain(fit=FIT):
    from physics.hf.density.overrides import fit_params
    from physics.hf.fission.chain import FissionChain
    from physics.hf.input.defaults import default_options

    return FissionChain(ZT, AT, default_options(ZT, AT), fit=fit_params(fit))


def _close(a, b, rel=1e-12, tiny=1e-300):
    a, b = np.asarray(a, float), np.asarray(b, float)
    assert a.shape == b.shape
    bad = np.abs(a - b) > rel * np.maximum(np.abs(a), np.abs(b)) + tiny
    assert not bad.any(), (np.argwhere(bad)[:5], a[bad][:5], b[bad][:5])


def test_parameter_set_routing():
    from physics.hf.density import overrides as ov
    from physics.hf.emission.feeding import Cascade

    with pytest.raises(ValueError):
        ov.fit_params([("fismodel", 92, 236, 1.0)])
    with pytest.raises(ValueError):
        ov.fit_params([("fismodel", 0, 0, 7.0)])
    cas = Cascade.__new__(Cascade)
    cas.set_fit_params([*FIT, ("aadjust", 92, 236, 1.1)])
    assert cas.fit == (("aadjust", 92, 236, 1.1),)
    assert {e[0] for e in cas.fission_fit} == set(ov.FISSION_KEYS)


def test_barrier_height_carries_the_factors():
    from physics.hf.fission.barriers import barrier_height

    chain, base = _chain(), _chain(fit=(("fismodel", 0, 0, 1.0),))
    n, n0 = chain.nucleus(92, 236), base.nucleus(92, 236)
    assert n.fp.fismodelx == 1 and n.fp.nfisbar == 2 and n0.fp.fbaradjust is None
    for ibar in (1, 2):
        b, w = barrier_height(n.fp, ibar, n.ld.deltaW_mev)
        b0, w0 = barrier_height(n0.fp, ibar, n0.ld.deltaW_mev)
        assert float(b) == float(b0) * 1.15 and float(w) == float(w0) * 0.9  # no shell correction
    # a residual the parameter set does not name keeps its factors at 1
    assert chain.nucleus(92, 235).fp.fbaradjust is None
    assert _chain(fit=()).nucleus(92, 236).fp.fbaradjust is None


@pytest.mark.parametrize("Z,A", [(92, 236), (92, 235)])
def test_torch_fis2_and_cengfis_agree_under_fismodel_1(monkeypatch, Z, A):
    from physics.hf.fission import fis_ceng
    from physics.hf.fission.fission_batch_ladder import ladder_bin_widths
    from physics.hf.fission.transmission import fission_transmission

    chain = _chain()
    n = chain.nucleus(Z, A)
    m = 37
    for top in (7.3, 13.9):
        dex = np.full(m, top / m)
        ex = (np.arange(m) + 0.5) * dex
        exmax = float(ex[-1] + 0.5 * dex[-1])
        monkeypatch.setenv("HF_NX2_FIS2", "0")
        monkeypatch.setenv("HF_NX2_CENGFIS", "0")
        grid = chain._grid(n, top)
        ref_w = ladder_bin_widths(n.fp, grid, n.ld, ex, dex, exmax, chain.o, maxj=chain.maxj,
                                  fnorm=0.93)
        ref_t = fission_transmission(n.fp, chain._grid(n, top), n.ld, top, 0.0, chain.o,
                                     exmax_mev=top, odd=n.odd, maxj=chain.maxj, primary=True)
        assert fis_ceng.ladder_widths(chain, n, ex, dex, exmax, top, 0.93, chain.maxj + 1) is None
        monkeypatch.setenv("HF_NX2_FIS2", "1")
        fis2_w = ladder_bin_widths(n.fp, grid, n.ld, ex, dex, exmax, chain.o, maxj=chain.maxj,
                                   fnorm=0.93)
        fis2_t = fission_transmission(n.fp, grid, n.ld, top, 0.0, chain.o, exmax_mev=top,
                                      odd=n.odd, maxj=chain.maxj, primary=True)
        monkeypatch.setenv("HF_NX2_CENGFIS", "1")
        ceng_w = fis_ceng.ladder_widths(chain, n, ex, dex, exmax, top, 0.93, chain.maxj + 1)
        tf, ta, ra = fis_ceng.target_transmission(chain, n, top, 1.0)
        assert float(ref_t.tfis.sum()) > 0.0
        _close(ref_w, fis2_w)
        _close(ref_w, ceng_w)
        _close(ref_t.tfis.numpy(), fis2_t.tfis.numpy())
        _close(ref_t.tfis.numpy(), tf)
        _close(ref_t.tfisA.numpy(), ta)
        _close(ref_t.rhofisA.numpy(), ra)


def test_factors_move_hill_wheeler_and_not_wkb():
    from physics.hf.fission import fis_ceng

    def tfis(fit):
        chain = _chain(fit)
        return fis_ceng.target_transmission(chain, chain.nucleus(92, 236), 6.6, 1.0)[0]

    adj = (("fisbaradjust", 92, 236, 1.15), ("fishwadjust", 92, 236, 0.9))
    # fismodel 6: twkbint, the factors are never read. Not array_equal: after other fission tests
    # the per-process caches leave last-bit (~2e-16) differences between two otherwise equal calls.
    _close(tfis(adj), tfis(()), rel=1e-14)
    hw, hw0 = tfis(FIT), tfis((("fismodel", 0, 0, 1.0),))
    assert float(hw.sum()) < 0.5 * float(hw0.sum())  # a 15% higher barrier closes most of it
