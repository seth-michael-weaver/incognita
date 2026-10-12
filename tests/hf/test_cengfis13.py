"""CENGFIS13 (development notes): `wkb.parab_fit` is bitwise reproducible whatever the memory
layout of its inputs (torch.linalg.lstsq, the MKL LAPACK path it replaced, is not: its last bit
follows the heap alignment, which made test_fisbarwire's fismodel-6 bitwise claim flaky), and it is
the least-squares estimator lstsq computes to roundoff.
"""

from __future__ import annotations

import numpy as np
import pytest
import torch

from physics.hf.core.tensors import DTYPE
from physics.hf.fission import wkb


def _path(beta, v):
    class P:  # the three fields parab_fit reads
        pass

    p = P()
    p.betafis, p.vfis_mev, p.nbeta = beta, v, beta.shape[0] - 1
    return p


def _views(src, off):
    big = torch.empty(off + src.shape[0] + 64, dtype=DTYPE)
    view = big[off:off + src.shape[0]]
    view.copy_(src)
    return view


@pytest.mark.parametrize("seed", range(4))
def test_parab_fit_does_not_depend_on_layout(seed):
    g = torch.Generator().manual_seed(seed)
    beta = torch.cumsum(torch.rand(30, dtype=DTYPE, generator=g), 0)
    v = 6.0 - (beta - beta[15]) ** 2 + 0.1 * torch.rand(30, dtype=DTYPE, generator=g)
    got = set()
    for off in range(24):
        h, w = wkb.parab_fit(15, 3, 0.054 * 238 ** (5 / 3), _path(_views(beta, off), _views(v, off + 3)))
        got.add((float(h), float(w)))
    assert len(got) == 1


@pytest.mark.parametrize("seed", range(4))
def test_parab_fit_is_the_lstsq_estimator(seed, monkeypatch):
    g = torch.Generator().manual_seed(seed)
    beta = torch.arange(30, dtype=DTYPE)  # fismodel 6: the abscissa is the row index
    v = 6.0 - 0.02 * (beta - 15) ** 2 + 0.05 * torch.rand(30, dtype=DTYPE, generator=g)
    p = _path(beta, v)
    new = [float(t) for t in wkb.parab_fit(15, 3, 50.0, p)]
    monkeypatch.setenv("HF_WKB_LSTSQ", "1")
    old = [float(t) for t in wkb.parab_fit(15, 3, 50.0, p)]
    assert np.allclose(new, old, rtol=1e-12, atol=0)


def test_parab_fit_keeps_the_gradient():
    beta = torch.arange(30, dtype=DTYPE)
    v = (6.0 - 0.02 * (beta - 15) ** 2).requires_grad_(True)
    _h, w = wkb.parab_fit(15, 3, 50.0, _path(beta, v))
    w.backward()
    assert v.grad is not None and float(v.grad.abs().sum()) > 0
