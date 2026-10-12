"""KDABS `wddecay` keyword (env INCOGNITA_WDDECAY): neutron KD03 W_D(E) * exp(-delta E); default 0 = TALYS (bit-identical)."""

from __future__ import annotations

import dataclasses
import math

import numpy as np
import pytest
import torch

from physics.hf.input.defaults import default_options, default_params
from physics.hf.omp import omp_nx2 as N
from physics.hf.omp import parameters as P

E = torch.tensor([0.001, 1.0, 5.0, 8.0, 14.0, 20.0], dtype=torch.float64)


def _run(Z, A, k=1, **kw):
    o = default_options(Z, A)
    if kw:
        o = dataclasses.replace(o, **kw)
    p = default_params(Z, A, o)
    nuc = P.omppar(Z, A, o)
    return o, p, nuc, P.opticalnp(nuc[k], k, Z, A, E, p, options=o)


def test_default_is_off(monkeypatch):
    monkeypatch.delenv(P.ENV_WDDECAY, raising=False)
    assert default_options(26, 56).wddecay == 0.0 and P.wddecay(default_options(26, 56)) == 0.0


def test_off_bit_identical_and_ratio(monkeypatch):
    monkeypatch.delenv(P.ENV_WDDECAY, raising=False)
    *_, base = _run(26, 56)
    *_, on = _run(26, 56, wddecay=0.0075)
    r = (on["wd_mev"] / base["wd_mev"]).numpy()
    assert np.allclose(r, np.exp(-0.0075 * E.numpy()), rtol=1e-12, atol=0)
    for c in base:
        if c != "wd_mev":
            assert torch.equal(torch.as_tensor(base[c]), torch.as_tensor(on[c])), c


def test_env_equals_keyword_and_protons_untouched(monkeypatch):
    monkeypatch.delenv(P.ENV_WDDECAY, raising=False)
    *_, kw = _run(40, 90, wddecay=0.01)
    *_, pb = _run(40, 90, k=2)
    monkeypatch.setenv(P.ENV_WDDECAY, "0.01")
    *_, env = _run(40, 90)
    *_, pe = _run(40, 90, k=2)
    assert torch.equal(kw["wd_mev"], env["wd_mev"])
    assert torch.equal(pb["wd_mev"], pe["wd_mev"])


def test_float_path_matches_torch(monkeypatch):
    monkeypatch.delenv(P.ENV_WDDECAY, raising=False)
    o, p, nuc, t = _run(26, 56, wddecay=0.0075)
    fac = N._factors(p)
    for i, e in enumerate(E.tolist()):
        f = N._opticalnp(N._Scal, nuc[1], 1, 26, 56, e, fac, o, None)
        assert math.isclose(f["wd_mev"], float(t["wd_mev"][i]), rel_tol=1e-12)
