"""TFOLD: `tfold y` = the TRITON3 T2 finite-size fold in the engine: a' = sqrt(a^2 + (1.74/pi)^2) on av/aw/avd/awd of t and 3He
(torch path and the float nx2 path), cstrip t/h x0.99; `tfold n` = TALYS point geometry. The per-target deck lines it replaces
(factor sqrt(1 + (r_m/(pi a))^2), 4 decimals) must give the same potential to ~1e-4."""

from __future__ import annotations

import dataclasses
import math

import numpy as np
import pytest
import torch

from physics.hf.input.defaults import default_options, default_params
from physics.hf.omp import omp_nx2, tfold
from physics.hf.omp import parameters as P

DT = torch.float64


@pytest.fixture(autouse=True)
def _fold_unpinned(monkeypatch):
    monkeypatch.delenv("INCOGNITA_TFOLD", raising=False)
E = torch.tensor([0.5, 3.0, 10.0, 25.0], dtype=DT)
COLS = ("av_fm", "aw_fm", "avd_fm", "awd_fm")


def _run(Z, A, k, on, nx2=False):
    o = dataclasses.replace(default_options(Z, A), tfold=on)
    p = default_params(Z, A, o)
    if nx2:
        out = omp_nx2.omp_columns(Z, A - Z, k, E.numpy(), p, o)
        return None if out is None else {c: out[i] for i, c in enumerate(P.COLUMNS)}
    par = P.omp_parameters(Z, A - Z, k, E, p, o)
    return {c: getattr(par, c).detach().numpy() for c in P.COLUMNS}


@pytest.mark.parametrize("Z,A", [(28, 58), (82, 208), (8, 16)])
@pytest.mark.parametrize("k", [4, 5])
def test_fold_is_quadrature_on_the_four_diffusenesses(Z, A, k):
    Zr, Ar = Z - 1, A - 3
    off, on = _run(Zr, Ar, k, False), _run(Zr, Ar, k, True)
    for c in COLS:
        np.testing.assert_allclose(on[c], np.sqrt(off[c] ** 2 + (1.74 / math.pi) ** 2), rtol=1e-13)
    for c in set(P.COLUMNS) - set(COLS):  # radii, depths: untouched
        np.testing.assert_array_equal(on[c], off[c])


def test_deck_factor_equals_engine_fold_to_4_decimals():
    Zr, Ar = 27, 56
    off = _run(Zr, Ar, 4, False)
    on = _run(Zr, Ar, 4, True)
    for c in ("av_fm", "avd_fm"):
        f = round(float(on[c][0] / off[c][0]), 4)
        np.testing.assert_allclose(off[c] * f, on[c], rtol=1e-4)


def test_other_particles_untouched_and_nx2_agrees():
    for k in (1, 2, 3, 6):
        a, b = _run(27, 56, k, False), _run(27, 56, k, True)
        for c in P.COLUMNS:
            np.testing.assert_array_equal(a[c], b[c])
    for k in (4, 5):
        t, n = _run(27, 56, k, True), _run(27, 56, k, True, nx2=True)
        if n is None:
            pytest.skip("nx2 declines")
        for c in P.COLUMNS:
            np.testing.assert_allclose(n[c], t[c], rtol=1e-12, atol=1e-300)


def test_enabled_env_off(monkeypatch):
    o = default_options(27, 56)
    assert tfold.enabled(o) and not tfold.enabled(dataclasses.replace(o, tfold=False))
    monkeypatch.setenv("INCOGNITA_TFOLD", "0")
    assert not tfold.enabled(o)
