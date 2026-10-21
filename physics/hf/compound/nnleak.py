"""NNLEAK (Incognita extension, not TALYS; keyword `nnleak y|n`, default y; env INCOGNITA_NNLEAK=0 = TALYS).

The top continuum bin of the initial compound nucleus, [Etotal - dEx, Etotal], is populated only by
primary photons with Egamma = Etotal - Ex, so its population density goes as Egamma^3 f(Egamma) rho(Ex)
(dipole; f finite at Egamma -> 0): the slice of the bin within u = Etotal - Ex of the top holds
(u / dEx)^4 of it. densprepare.f90:250-256 (continuum -> discrete, "type 4") treats every mother bin as
uniformly filled and gives the slice above Exm = Ex(level) + S a LINEAR open fraction
Rboundary = (Ex0plus - Exm) / dExinc, at the bin-centre energy 0.5 (Ex0plus + Exm) - S - Ex(level).
Below the first excited level that books (n, gamma n) to the target ground state as sub-threshold
(n,n') of 1e-3..8e-3 mb, scaling ~ dEx^3 with the bin width (ARTSCAN item 3).

ON (default): for that bin only and particle exits only (type >= 1), continuum -> discrete rows that are
partly open get Rboundary = q^4, q = (Ex0plus - Exm) / dExinc, and the Egamma^3-weighted mean emission
energy Eout = Eout_TALYS - 0.3 (Ex0plus - Exm) (mean u over [0, Ex0plus - Exm] with weight u^3 is
0.8 of the slice, TALYS uses 0.5). Continuum -> continuum rows (the triangle Rboundary) and every other
mother bin keep TALYS. OFF reproduces TALYS bitwise (nothing is evaluated).

Sites (all must agree): prepare._eout_and_rboundary(_rows) via DensPrepareInputs.nnleak_top,
decay_batch.NucleusDecay, decay_fast._Geometry, capture_fast_batch, capture_gpu_setup,
gpu_full_setup/_kernels/_cascade; C: nativex.c nx_widths (ip[10]) via widths_native and engine_decay.c.
specout (emission-spectrum shape) keeps TALYS: its integrals come from the corrected widths.
Test: tests/hf/test_nnleak.py.
"""

from __future__ import annotations

import os

import numpy as np

EOUT_SHIFT = 0.3  # 0.8 - 0.5: Egamma^3-weighted minus uniform mean position of the open slice


def enabled(options) -> bool:
    """`nnleak` on: keyword (default y) and INCOGNITA_NNLEAK != 0."""
    return bool(getattr(options, "nnleak", True)) and os.environ.get("INCOGNITA_NNLEAK", "1") != "0"


def top_bin(options, zix: int, nix: int, maxex: int, nlast: int) -> int:
    """The mother bin index the rule applies to (the initial compound nucleus's top bin, when it is
    a continuum bin: maxex > Nlast), or -1."""
    if zix == 0 and nix == 0 and maxex > nlast and enabled(options):
        return int(maxex)
    return -1


def adjust(rb_d, eout_d, part, ex0plus, exm, dexinc, sel):
    """(rb_d, eout_d) with the rule applied where `part & sel` (numpy, broadcastable shapes).

    `sel` marks (mother bin of the rule) x (type >= 1); everything else is returned unchanged."""
    m = np.logical_and(part, sel)
    if not np.any(m):
        return rb_d, eout_d
    with np.errstate(divide="ignore", invalid="ignore"):
        d = ex0plus - exm
        q = d / dexinc
        rb_new = np.where(m, q * q * q * q, rb_d)
        eout_new = np.where(m, eout_d - EOUT_SHIFT * d, eout_d)
    return rb_new, eout_new


def adjust_torch(rb_d, eout_d, part, ex0plus, exm, dexinc, sel):
    """`adjust` for torch tensors."""
    import torch

    m = part & sel
    if not bool(m.any()):
        return rb_d, eout_d
    d = ex0plus - exm
    q = d / dexinc
    return torch.where(m, q * q * q * q, rb_d), torch.where(m, eout_d - EOUT_SHIFT * d, eout_d)


def scalar(rb, eout, ex0plus, exm, dexinc):
    """The rule for one partly-open continuum -> discrete row (caller checked bin, type and part)."""
    d = ex0plus - exm
    q = d / dexinc
    return q * q * q * q, eout - EOUT_SHIFT * d


def native_arm(options) -> None:
    """Switch the C cascade's rule (engine_decay.c ce_set_nnleak) for this run; nx_widths reads its ip[10]."""
    import ctypes

    from physics.hf import engine_c

    flag = 1 if enabled(options) else 0
    so = engine_c.lib()
    if so is not None and hasattr(so, "ce_set_nnleak"):
        so.ce_set_nnleak.argtypes = [ctypes.c_int64]; so.ce_set_nnleak.restype = None
        so.ce_set_nnleak(flag)
    elif flag and so is not None:
        raise NotImplementedError("NNLEAK: libengdecay without ce_set_nnleak (rebuild the native libraries)")
