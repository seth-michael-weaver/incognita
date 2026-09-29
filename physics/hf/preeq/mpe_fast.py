"""SPEEDW: `preeq.multi.multiple_preequilibrium` on the compiled kernel (`native/speedw.c`).

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: SPEEDW (the speed wave; no physics of its own). Acceptance test: A-mpe / E2E, and
`tests/hf/test_mpe_fast.py` (the kernel against the torch loop on every mother bin of a 20 MeV
cascade).

TALYS routines the kernel computes:
    multipreeq2.f90:1 (multipreeq2)

multipreeq2 runs only at `Einc >= emulpre` (20 MeV), and there it was ~40% of a whole 23-energy
run (3.2-3.7 CPU-s of 6.4-8.0 on the four harness targets): ~150 mother bins, each walking up to
729 particle-hole pairs with scalar torch operations. The kernel is the same loop in C. It is not
bit-identical to the torch loop -- glibc `pow` against torch's SIMD pow on arrays of eight or more
elements, and left-to-right row sums against `torch.sum`'s lanes -- so it moves the 20 MeV numbers
in the last bits; the speed golden (no 20 MeV energy) does not see it and E2E §4's 1e-12 bounds
it (docs/results/hf-speed-profile.md, "Whole runs").

The torch loop stays the reference and the differentiable path: anything on the autograd graph,
`flaggshell`, a non-CPU tensor, no build, `HF_NATIVE=0` or `HF_SPEEDW_NATIVE=0` takes it.
"""

from __future__ import annotations

import numpy as np
import torch

from physics.hf.preeq.multi import (
    MultiPreeqInputs,
    MultiPreeqResult,
    _zero,
    FEED_MIN_MB,
    multiple_preequilibrium,
)

def _lib():
    from physics.hf.native.speedw import lib

    return lib()


def available() -> bool:
    return _lib() is not None


def _ptr(a: np.ndarray) -> int:
    return a.__array_interface__["data"][0]


def _on_graph(inp: MultiPreeqInputs) -> bool:
    ts = [inp.exinc_mev, inp.dexinc_mev, inp.xspopex_mother_mb, inp.xspopph2_mb, inp.gp_comp,
          inp.gn_comp, inp.gp_cn0, inp.gn_cn0, inp.rnj, inp.rnjsum]
    for d in inp.daughters:
        ts += [d.gp, d.gn, d.ex_mev, d.dex_mev, d.tswave]
    return any(isinstance(t, torch.Tensor) and (t.requires_grad or t.device.type != "cpu")
               for t in ts)


def _f(x) -> float:
    return float(x)


def multiple_preequilibrium_fast(inp: MultiPreeqInputs, numj: int = 40) -> MultiPreeqResult:
    """`multiple_preequilibrium`, on the kernel where it applies (module docstring).

    TALYS: multipreeq2.f90:1 (multipreeq2)
    Test: A-mpe
    """
    lib = _lib()
    if (lib is None or inp.mpreeqmode != 2 or not inp.flag2comp or inp.flaggshell
            or len(inp.daughters) != 2 or _on_graph(inp)):
        return multiple_preequilibrium(inp, numj=numj)
    if inp.zcomp == 0 and inp.ncomp == 0:
        return _zero(inp, numj)
    if float(inp.xspopph2_mb.sum()) <= FEED_MIN_MB:
        return _zero(inp, numj)
    P = inp.maxpar
    P1 = P + 1
    d1, d2 = inp.daughters
    b = d1.ex_mev.shape[0]
    nj1 = numj + 1
    mother = inp.xspopph2_mb.detach().numpy().astype(np.float64, copy=True)
    mother = np.ascontiguousarray(mother.reshape(-1))
    # :272-277's `Jterm` weights, as `multiple_preequilibrium` hoists them (elementwise, so numpy
    # gives torch's bits)
    jj = np.arange(nj1, dtype=np.float64)
    w = 0.5 * (2.0 * jj + 1.0) * inp.rnj.detach().numpy().astype(np.float64) / _f(inp.rnjsum)
    jw = np.zeros((2, b, nj1))
    for d in inp.daughters:
        for nexout in range(b):
            k = min(int(d.maxj[nexout]), numj) + 1
            jw[d.type - 1, nexout, :k] = w[:k]
    i64 = np.int64
    d_type = np.array([d1.type, d2.type], dtype=i64)
    d_zix = np.array([d1.zix, d2.zix], dtype=i64)
    d_nix = np.array([d1.nix, d2.nix], dtype=i64)
    d_nlast = np.array([d1.nlast, d2.nlast], dtype=i64)
    d_nexmax = np.array([d1.nexmax, d2.nexmax], dtype=i64)
    d_parskip = np.array([int(d1.parskip), int(d2.parskip)], dtype=i64)
    d_s = np.array([_f(d1.s_mev), _f(d2.s_mev)])
    d_gp = np.array([_f(d1.gp), _f(d2.gp)])
    d_gn = np.array([_f(d1.gn), _f(d2.gn)])

    def rows(name):
        return np.ascontiguousarray(np.stack(
            [getattr(d, name).detach().numpy().astype(np.float64)[:b] for d in (d1, d2)]))

    d_ex, d_dex, d_tsw = rows("ex_mev"), rows("dex_mev"), rows("tswave")
    scal = np.zeros(5)
    term_tot = np.zeros((2, b))
    xspop_add = np.zeros((2, b, nj1))
    key_of = np.empty(2 * P1 ** 4, dtype=i64)
    cap = 2 * P1 ** 4
    keys = np.empty((cap, 5), dtype=i64)
    dpop = np.empty((cap, b))
    term = np.empty(2 * b)
    n = lib.sw_mpe_bin(
        P, b, nj1, _ptr(mother), _f(inp.exinc_mev), _f(inp.dexinc_mev), _f(inp.gp_comp),
        _f(inp.gn_comp), _f(inp.gp_cn0), _f(inp.gn_cn0), float(inp.efermi_mev),
        _ptr(d_type), _ptr(d_zix), _ptr(d_nix), _ptr(d_nlast), _ptr(d_nexmax), _ptr(d_parskip),
        _ptr(d_s), _ptr(d_gp), _ptr(d_gn), _ptr(d_ex), _ptr(d_dex), _ptr(d_tsw), _ptr(jw),
        _ptr(scal), _ptr(term_tot), _ptr(xspop_add), _ptr(key_of), _ptr(keys), _ptr(dpop), cap,
        _ptr(term))
    if n < 0:  # cannot happen (cap is every key there is); the torch loop is always right
        return multiple_preequilibrium(inp, numj=numj)
    dt = inp.xspopph2_mb.dtype
    summpe = torch.tensor(scal[0], dtype=dt)
    dpop_t = {tuple(int(x) for x in keys[i]): torch.from_numpy(dpop[i].copy()) for i in range(n)}
    return MultiPreeqResult(
        dmulti=summpe / inp.xspopex_mother_mb, summpe_mb=summpe,
        term_mb=torch.from_numpy(term_tot), sumtype_mb=torch.from_numpy(scal[1:3].copy()),
        xspop_add_mb=torch.from_numpy(xspop_add),
        xspopph2_mother_mb=torch.from_numpy(mother.reshape((P1,) * 4)),
        xspopph2_daughter_mb=dpop_t, mulpre=(bool(scal[3]), bool(scal[4])))
