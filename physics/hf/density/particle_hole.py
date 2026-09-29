"""Particle-hole state densities for the exciton model (one- and two-component, with Pauli and
well-depth corrections).

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T8 (physics/hf/CONTRACT.md §7). Acceptance test: A-pe (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    phdens.f90:1 (phdens)
    phdens2.f90:1 (phdens2)
    phdensitytable.f90:1 (phdensitytable)
    phdensitytablejp.f90:1 (phdensitytablejp)
    finitewell.f90:1 (finitewell)
    preeqpair.f90:1 (preeqpair)
    preeqinit.f90:1 (preeqinit)   -- the Apauli / Apauli2 / nfac / ncomb tables only

Everything is batched: the exciton numbers ``ppi, hpi, pnu, hnu`` are integer tensors that
broadcast against the float64 energy/level-density tensors, so one call covers
(case, energy, exciton state) at once. Differentiable with respect to ``gsp``/``gsn`` (the
single-particle densities, §4.4 ``g``/``gp``/``gn``) and the well depth ``Ewell`` (``esurf``).

`phmodel` 2 (the tabulated particle-hole densities of `phdensitytable.f90`) is not ported:
TALYS's default is `phmodel 1` and the reference dumps are all phmodel 1. `phdens`/`phdens2`
raise if asked for the table branch, rather than silently returning the analytical density.
"""

from __future__ import annotations

from functools import lru_cache

import numpy as np
import torch
from torch import Tensor

from physics.hf.core.tensors import DTYPE

EFERMI_MEV = 38.0  # preeqinit.f90:79 (Efermi = 38.)
NUMEXC = 12  # A0_talys_mod.f90, parameter numexc
NUMPARX = NUMEXC // 2  # A0_talys_mod.f90, parameter numparx = numexc/2
PHDENS_FLOOR = 1.0e-10  # phdens2.f90 "if (phdens2 < 1.e-10) phdens2 = 0."


def _nfac(n: int) -> float:
    """`nfac(n)` = n! as preeqinit.f90:81-87 builds it."""
    out = 1.0
    for i in range(2, n + 1):
        out *= float(i)
    return out


_NFAC = tuple(_nfac(n) for n in range(2 * NUMEXC + 2))


def nfac_table(device=None) -> Tensor:
    """`nfac(0:numexc)` as a float64 tensor (preeqinit.f90:81-87).

    TALYS: preeqinit.f90:1 (preeqinit)
    Test: A-pe
    """
    return torch.tensor(_NFAC, dtype=DTYPE, device=device)


@lru_cache(maxsize=8)
def _nfac_tensor(device) -> Tensor:
    """`nfac_table`, built once per device for `factorial` (which only indexes it)."""
    return nfac_table(device)


def ncomb(n: int, k: int) -> float:
    """`ncomb(n, k)` = n!/(k!(n-k)!) [dimensionless] (preeqinit.f90:84-86).

    TALYS: preeqinit.f90:1 (preeqinit)
    Test: A-pe
    """
    if k < 0 or k > n:
        return 0.0
    return _NFAC[n] / (_NFAC[k] * _NFAC[n - k])


def factorial(n: Tensor) -> Tensor:
    """n! for an integer tensor, read out of TALYS's `nfac` table [dimensionless].

    TALYS: preeqinit.f90:1 (preeqinit)
    Test: A-pe
    """
    tab = _nfac_tensor(n.device)
    return tab[n.clamp(min=0, max=len(_NFAC) - 1)]


def apauli(p: Tensor, h: Tensor, gs: Tensor) -> Tensor:
    """One-component Pauli correction `Apauli(p, h)` [MeV] (preeqinit.f90:89-98).

    ``Apauli = max(p,h)**2/gs - (p*p + h*h + p + h)/(4 gs)``; zero where either index is -1.

    TALYS: preeqinit.f90:1 (preeqinit)
    Test: A-pe
    """
    p = p.to(torch.int64)
    h = h.to(torch.int64)
    pf, hf = p.to(DTYPE), h.to(DTYPE)
    epp = torch.maximum(pf, hf) ** 2 / gs
    factor = (pf * pf + hf * hf + pf + hf) / (4.0 * gs)
    out = epp - factor
    return torch.where((p == -1) | (h == -1), torch.zeros_like(out), out)


def apauli2(ppi: Tensor, hpi: Tensor, pnu: Tensor, hnu: Tensor, gsp: Tensor, gsn: Tensor) -> Tensor:
    """Two-component Pauli correction `Apauli2(ppi, hpi, pnu, hnu)` [MeV] (preeqinit.f90:100-119).

    TALYS fills this table once in `preeqinit` with the *compound nucleus* ``gp(0,0)``,
    ``gn(0,0)`` and then uses it for residual nuclei and for shell-damped ``g`` as well; pass
    the compound-nucleus values here to stay faithful (see `phdens2`).

    TALYS: preeqinit.f90:1 (preeqinit)
    Test: A-pe
    """
    ppi, hpi = ppi.to(torch.int64), hpi.to(torch.int64)
    pnu, hnu = pnu.to(torch.int64), hnu.to(torch.int64)
    ppif, hpif = ppi.to(DTYPE), hpi.to(DTYPE)
    pnuf, hnuf = pnu.to(DTYPE), hnu.to(DTYPE)
    eppi = torch.maximum(ppif, hpif) ** 2 / gsp
    epnu = torch.maximum(pnuf, hnuf) ** 2 / gsn
    factorp = (ppif * ppif + hpif * hpif + ppif + hpif) / (4.0 * gsp)
    factorn = (pnuf * pnuf + hnuf * hnuf + pnuf + hnuf) / (4.0 * gsn)
    out = eppi + epnu - factorp - factorn
    bad = (ppi == -1) | (hpi == -1) | (pnu == -1) | (hnu == -1)
    return torch.where(bad, torch.zeros_like(out), out)


@lru_cache(maxsize=64)
def _signed_ncomb_table(hmax: int, device) -> Tensor:
    """``(-1)^k ncomb(n, k)`` for k = 1..hmax (rows) and n = 0..2 numexc + 1 (columns), built
    once per (hmax, device); callers only index it, which copies."""
    rows = [
        [((-1.0) ** k) * ncomb(n, k) for n in range(2 * NUMEXC + 2)] for k in range(1, hmax + 1)
    ]
    return torch.tensor(rows, dtype=DTYPE, device=device).reshape(hmax, 2 * NUMEXC + 2)


def _pad(x: Tensor, ndim: int) -> Tensor:
    return x.reshape((1,) * (ndim - x.dim()) + tuple(x.shape))


def _sum_terms(ee: Tensor, ew: Tensor, h: Tensor, nm1: Tensor, hmax: int) -> Tensor:
    """1 + sum_{k=1..h} sgn(k) ncomb(h,k) ((ee - k*ew)/ee)^(n-1), terms with E<=0 dropped.

    ``ew`` carries one leading axis more than ``ee``, ``h``, ``nm1`` (all padded to the same
    rank): the well depths it is evaluated at. All k are evaluated at once along a new leading
    axis; the k-terms are then added to 1 one k at a time, in TALYS's order.
    """
    if hmax <= 0:
        shape = torch.broadcast_shapes(ew.shape, ee.shape, h.shape)
        return torch.ones(shape, dtype=DTYPE, device=ee.device)
    if ee.device.type == "cpu" and not (torch.is_grad_enabled()
                                        and (ee.requires_grad or ew.requires_grad)):
        return _sum_terms_np(ee, ew, h, nm1, hmax)
    one = torch.ones((), dtype=DTYPE, device=ee.device)
    kview = (hmax,) + (1,) * ew.dim()
    ks = torch.arange(1, hmax + 1, device=ee.device)
    e_k = ee - ks.to(DTYPE).reshape(kview) * ew  # (K, J, ...)
    ok = (e_k > 0) & (h >= ks.reshape(kview)) & (ee > 0)
    safe_ee = torch.where(ee > 0, ee, one)
    ratio = torch.where(ok, e_k / safe_ee, one)
    coef = _signed_ncomb_table(hmax, ee.device)[:, h.clamp(min=0, max=2 * NUMEXC + 1)]
    # pow per (k, well depth), on arrays shaped as TALYS's loop has them: torch's CPU pow takes a
    # SIMD path for blocks of 8 elements and libm for the rest, which can differ in the last bit,
    # so which path an element takes must not change with the batching
    kj = ratio.shape[:2]
    pw = torch.stack([r**nm1 for r in ratio.reshape((-1,) + ratio.shape[2:]).unbind(0)])
    pw = pw.reshape(kj + pw.shape[1:])
    term = coef.reshape((hmax,) + (1,) * (ew.dim() - h.dim()) + tuple(h.shape)) * pw
    term = torch.where(ok, term, torch.zeros_like(term))
    acc = torch.ones_like(ok[0], dtype=DTYPE)
    for k in range(hmax):
        acc = acc + term[k]
    return acc


def _sum_terms_np(ee: Tensor, ew: Tensor, h: Tensor, nm1: Tensor, hmax: int) -> Tensor:
    """`_sum_terms` off the autograd graph, in numpy (`_sum_terms_arr`)."""
    return torch.from_numpy(_sum_terms_arr(ee.detach().numpy(), ew.detach().numpy(), h.numpy(),
                                           nm1.detach().numpy(), hmax, ee.device))


def _sum_terms_arr(een: np.ndarray, ewn: np.ndarray, hn: np.ndarray, nmn: np.ndarray, hmax: int,
                   device="cpu") -> np.ndarray:
    """COREX: `_sum_terms` on arrays: each k-term is computed only where it is kept (E - k Ewell >
    0, h >= k, E > 0; ufuncs with `where=`), one pass per k. Not bit-identical to the torch path
    (pow's SIMD/libm split, the batching): the sums agree to ~1e-15 absolute
    (tests/hf/test_corex.py)."""
    if hmax <= 0:
        return np.ones(np.broadcast_shapes(ewn.shape, een.shape, hn.shape))
    shape = np.broadcast_shapes(ewn.shape, een.shape, hn.shape, nmn.shape)
    tab = _signed_ncomb_table(hmax, device).numpy()
    from physics.hf.native import nativex

    so = nativex.lib()
    if so is not None:
        # NATIVEX: the same k-sum per element in C (libm pow; values to rounding)
        e_, w_, h_, m_ = (np.ascontiguousarray(np.broadcast_to(a, shape), dtype=d) for a, d in (
            (een, np.float64), (ewn, np.float64), (hn, np.int64), (nmn, np.float64)))
        tabc = np.ascontiguousarray(tab, dtype=np.float64)
        out = np.empty(shape)
        so.nx_sum_terms(out.size, nativex.ptr(e_), nativex.ptr(w_), nativex.ptr(h_),
                        nativex.ptr(m_), hmax, nativex.ptr(tabc), tabc.shape[1], nativex.ptr(out))
        return out
    hc = np.clip(hn, 0, 2 * NUMEXC + 1)
    pos = een > 0
    safe = np.where(pos, een, 1.0)
    acc = np.ones(shape)
    term = np.empty(shape)
    with np.errstate(all="ignore"):
        for k in range(1, hmax + 1):  # added to 1 one k at a time, in TALYS's order
            e_k = een - k * ewn
            ok = np.broadcast_to((e_k > 0) & (hn >= k) & pos, shape)
            term.fill(0.0)
            np.power(e_k / safe, nmn, out=term, where=ok)
            np.multiply(tab[k - 1][hc], term, out=term, where=ok)
            acc += term
    return acc


def _no_graph(*xs) -> bool:
    """COREX: the numpy paths apply: grad mode is off and every tensor argument is on the CPU."""
    if torch.is_grad_enabled():
        return False
    return all(x.device.type == "cpu" for x in xs if isinstance(x, Tensor))


def _np(x, dtype=np.float64) -> np.ndarray:
    return np.asarray(x.detach().numpy() if isinstance(x, Tensor) else x, dtype=dtype)


def _padn(x: np.ndarray, ndim: int) -> np.ndarray:
    return x.reshape((1,) * (ndim - x.ndim) + x.shape)


_NFAC_NP = np.array(_NFAC)


def _finitewell_arr(p, h, eex, ewell, surfwell, efermi_mev: float) -> np.ndarray:
    """COREX: `finitewell` on arrays (p, h int64; eex, ewell float64; surfwell bool or bool
    array), the torch path's operations in its order."""
    n = p + h
    nm1 = (n - 1).astype(np.float64)
    surf_on = np.asarray(surfwell, dtype=bool) & (ewell < (efermi_mev - 0.5))
    hmax = max(int(h.max()) if h.size else 0, 0)
    nd = max(p.ndim, h.ndim, eex.ndim, ewell.ndim)
    ee_, h_, nm1_ = _padn(eex, nd), _padn(h, nd), _padn(nm1, nd)
    with np.errstate(all="ignore"):
        plain = _sum_terms_arr(ee_, _padn(ewell, nd)[None], h_, nm1_, hmax)[0]
        plain = np.where((eex <= ewell) | ((h == 1) & (n == 1)), 1.0, plain)
        if not surf_on.any():
            return np.where(surf_on, plain, plain)
        widthdis = ewell * (efermi_mev - ewell) / (2.0 * efermi_mev)
        wd = np.where(widthdis > 0, widthdis, 1.0)
        hole = 1.0 / (1.0 + np.exp((eex - ewell) / wd))
        hole = np.where(eex < ewell, 1.0, hole)
        hole = np.where(eex > 1.16 * efermi_mev, 0.0, hole)
        js = np.arange(-4, 5, dtype=np.float64).reshape((9,) + (1,) * widthdis.ndim)
        ewj = ewell + js * widthdis
        inrange = (ewj <= efermi_mev) & (ewj >= 0) & (widthdis > 0)
        x = np.where(inrange, (ewj - ewell) / wd, 0.0)
        wt = np.where(inrange & (x <= 80.0), 1.0 / ((1.0 + np.exp(x)) * (1.0 + np.exp(-x))), 0.0)
        ew_j = np.where(inrange, ewj, 1.0)
        tail = (9,) + (1,) * (nd - ewell.ndim) + ewell.shape
        fwell = _sum_terms_arr(ee_, ew_j.reshape(tail), h_, nm1_, hmax)
        fwell = np.where(ee_ > 0, fwell, 0.0)
        wt = wt.reshape(tail)
        wfw = wt * fwell
        wtsum = np.zeros_like(eex)
        fwtsum = np.zeros_like(eex)
        for j in range(9):
            wtsum = wtsum + wt[j]
            fwtsum = fwtsum + wfw[j]
        averaged = np.where(wtsum > 0, fwtsum / np.where(wtsum > 0, wtsum, 1.0), 1.0)
        surf_val = np.where((p == 0) & (h == 1), hole, averaged)
        return np.where(surf_on, surf_val, plain)


def _apauli2_arr(ppi, hpi, pnu, hnu, gsp, gsn) -> np.ndarray:
    ppif, hpif = ppi.astype(np.float64), hpi.astype(np.float64)
    pnuf, hnuf = pnu.astype(np.float64), hnu.astype(np.float64)
    with np.errstate(all="ignore"):
        eppi = np.maximum(ppif, hpif) ** 2 / gsp
        epnu = np.maximum(pnuf, hnuf) ** 2 / gsn
        factorp = (ppif * ppif + hpif * hpif + ppif + hpif) / (4.0 * gsp)
        factorn = (pnuf * pnuf + hnuf * hnuf + pnuf + hnuf) / (4.0 * gsn)
        out = eppi + epnu - factorp - factorn
    bad = (ppi == -1) | (hpi == -1) | (pnu == -1) | (hnu == -1)
    return np.where(bad, 0.0, out)


def _phdens2_arr(ppi, hpi, pnu, hnu, gsp, gsn, ex, ewell, surfwell, ap2, efermi_mev):
    """COREX: `phdens2` on arrays, the torch path's operations in its order."""
    from physics.hf.preeq import preeq_nx2

    out = preeq_nx2.phdens2_arr(ppi, hpi, pnu, hnu, gsp, gsn, ex, ewell, surfwell, ap2, efermi_mev)
    if out is not None:  # NATIVEX2: the same density per element in C (nx2_preeq_phdens2)
        return out
    ppif, hpif = ppi.astype(np.float64), hpi.astype(np.float64)
    pnuf, hnuf = pnu.astype(np.float64), hnu.astype(np.float64)
    top = len(_NFAC) - 1
    with np.errstate(all="ignore"):
        factorn = (pnuf * pnuf + hnuf * hnuf + pnuf + hnuf) / (4.0 * gsn)
        factorp = (ppif * ppif + hpif * hpif + ppif + hpif) / (4.0 * gsp)
        n = ppi + hpi + pnu + hnu
        p = ppi + pnu
        h = hpi + hnu
        n1 = (n - 1).astype(np.float64)
        zero = np.zeros(np.broadcast_shapes(np.shape(ex), np.shape(ap2)))
        ok = ((ppi >= 0) & (hpi >= 0) & (pnu >= 0) & (hnu >= 0) & (n != 0)
              & (ap2 + factorn + factorp < ex))
        fac = [_NFAC_NP[np.clip(v, 0, top)] for v in (ppi, hpi, pnu, hnu, n - 1)]
        fac1 = fac[0] * fac[1] * fac[2] * fac[3] * fac[4]
        npi, nnu = (ppi + hpi).astype(np.float64), (pnu + hnu).astype(np.float64)
        factor = gsp**npi * gsn**nnu / fac1
        u = np.where(ok, ex - ap2, np.ones_like(zero))
        dens = factor * u**n1
        dens = dens * _finitewell_arr(p, h, np.asarray(ex, dtype=np.float64),
                                      np.asarray(ewell, dtype=np.float64), surfwell, efermi_mev)
        dens = np.where(ok, dens, zero)
        return np.where(dens < PHDENS_FLOOR, zero, dens)


def finitewell(
    p: Tensor,
    h: Tensor,
    eex_mev: Tensor,
    ewell_mev: Tensor,
    surfwell: bool | Tensor = False,
    efermi_mev: float = EFERMI_MEV,
) -> Tensor:
    """Finite-well correction `finitewell(p, h, Eex, Ewell, surfwell)`, dimensionless.

    Three branches, exactly as the Fortran:
      * `surfwell` and `Ewell < Efermi - 0.5`, `(p, h) = (0, 1)`: a Fermi-like damping of the
        single surface hole, zero above 1.16 Efermi;
      * `surfwell` and `Ewell < Efermi - 0.5`, otherwise: the standard correction averaged over
        nine well depths `Ewell + j*widthdis`, `j = -4..4`, weighted by `1/((1+e^x)(1+e^-x))`;
      * no surface effect: the standard `sum_k (-1)^k C(h,k) ((Eex - k Ewell)/Eex)^(n-1)`.

    The sums over k and over the nine well depths are array axes, not Python loops; every
    element sees the same float64 operations in the same order (the running sums are still
    added term by term). The surface branches are skipped when no element takes them.

    TALYS: finitewell.f90:1 (finitewell)
    Test: A-pe
    """
    if _no_graph(p, h, eex_mev, ewell_mev, surfwell):
        return torch.as_tensor(np.asarray(_finitewell_arr(
            _np(p, np.int64), _np(h, np.int64), _np(eex_mev), _np(ewell_mev), _np(surfwell, bool),
            efermi_mev)))
    p = p.to(torch.int64)
    h = h.to(torch.int64)
    n = p + h
    nm1 = (n - 1).to(DTYPE)
    eex = eex_mev
    ewell = ewell_mev
    one = torch.ones((), dtype=DTYPE, device=eex.device)

    surf = torch.as_tensor(surfwell, device=eex.device)
    surf_on = surf & (ewell < (efermi_mev - 0.5))

    hmax = int(h.max().item()) if h.numel() else 0
    hmax = max(hmax, 0)
    nd = max(p.dim(), h.dim(), eex.dim(), ewell.dim())
    ee_, h_, nm1_ = _pad(eex, nd), _pad(h, nd), _pad(nm1, nd)

    # --- branch 3: no surface effect (finitewell.f90:96-105)
    plain = _sum_terms(ee_, _pad(ewell, nd).unsqueeze(0), h_, nm1_, hmax)[0]
    plain = torch.where((eex <= ewell) | ((h == 1) & (n == 1)), torch.ones_like(plain), plain)
    # no element takes a surface branch: skip them (unless autograd needs their graph)
    needs_graph = torch.is_grad_enabled() and (eex.requires_grad or ewell.requires_grad)
    if not needs_graph and not bool(surf_on.any()):
        return torch.where(surf_on, plain, plain)

    # --- branch 1: the single surface hole (finitewell.f90:66-73)
    widthdis = ewell * (efermi_mev - ewell) / (2.0 * efermi_mev)
    wd = torch.where(widthdis > 0, widthdis, one)
    hole = 1.0 / (1.0 + torch.exp((eex - ewell) / wd))
    hole = torch.where(eex < ewell, torch.ones_like(hole), hole)
    hole = torch.where(eex > 1.16 * efermi_mev, torch.zeros_like(hole), hole)

    # --- branch 2: average over the well-depth distribution (finitewell.f90:75-94)
    js = torch.arange(-4, 5, dtype=DTYPE, device=eex.device).reshape((9,) + (1,) * widthdis.dim())
    ewj = ewell + js * widthdis  # (J, ...)
    inrange = (ewj <= efermi_mev) & (ewj >= 0) & (widthdis > 0)
    x = torch.where(inrange, (ewj - ewell) / wd, torch.zeros_like(ewj))
    exp_x = torch.stack([torch.exp(xj) for xj in x.unbind(0)])  # per well depth, as pow above
    exp_mx = torch.stack([torch.exp(-xj) for xj in x.unbind(0)])
    wt = torch.where(
        inrange & (x <= 80.0),
        1.0 / ((1.0 + exp_x) * (1.0 + exp_mx)),
        torch.zeros_like(x),
    )
    # fwell starts at k = 0 here (the k = 0 term is exactly 1 when Eex > 0)
    ew_j = torch.where(inrange, ewj, one)
    fwell = _sum_terms(
        ee_, ew_j.reshape((9,) + (1,) * (nd - ewell.dim()) + tuple(ewell.shape)), h_, nm1_, hmax
    )
    fwell = torch.where(ee_ > 0, fwell, torch.zeros_like(fwell))
    wt = wt.reshape((9,) + (1,) * (nd - ewell.dim()) + tuple(ewell.shape))
    wfw = wt * fwell
    wtsum = torch.zeros_like(eex)
    fwtsum = torch.zeros_like(eex)
    for j in range(9):
        wtsum = wtsum + wt[j]
        fwtsum = fwtsum + wfw[j]
    averaged = torch.where(
        wtsum > 0, fwtsum / torch.where(wtsum > 0, wtsum, one), torch.ones_like(wtsum)
    )

    surf_val = torch.where((p == 0) & (h == 1), hole, averaged)
    return torch.where(surf_on, surf_val, plain)


def ncomb_tensor(h: Tensor, k: int) -> Tensor:
    """`ncomb(h, k)` for an integer tensor h (preeqinit.f90:84-86).

    TALYS: preeqinit.f90:1 (preeqinit)
    Test: A-pe
    """
    tab = torch.tensor([ncomb(n, k) for n in range(2 * NUMEXC + 2)], dtype=DTYPE, device=h.device)
    return tab[h.clamp(min=0, max=2 * NUMEXC + 1)]


def phdens(
    p: Tensor,
    h: Tensor,
    gs: Tensor,
    eex_mev: Tensor,
    ewell_mev: Tensor,
    ap: Tensor,
    surfwell: bool | Tensor = False,
    efermi_mev: float = EFERMI_MEV,
    phmodel: int = 1,
) -> Tensor:
    """One-component particle-hole state density [MeV^-1] (phdens.f90:59-78).

    ``ap`` is `Apauli(p, h)` from `apauli`, which TALYS tabulates with the compound-nucleus
    ``g(0,0)`` and reuses everywhere.

    TALYS: phdens.f90:1 (phdens)
    Test: A-pe
    """
    if phmodel != 1:
        raise NotImplementedError("T8: phmodel 2 (phdensitytable.f90) is not ported")
    p = p.to(torch.int64)
    h = h.to(torch.int64)
    n = p + h
    pf, hf = p.to(DTYPE), h.to(DTYPE)
    factor_pauli = (pf * pf + hf * hf + pf + hf) / (4.0 * gs)
    zero = torch.zeros_like(eex_mev)
    ok = (p >= 0) & (h >= 0) & (n != 0) & (ap + factor_pauli < eex_mev)
    n1 = (n - 1).to(DTYPE)
    fac1 = factorial(p) * factorial(h) * factorial(n - 1)
    u = torch.where(ok, eex_mev - ap, torch.ones_like(eex_mev))
    dens = gs**n / fac1 * u**n1
    dens = dens * finitewell(p, h, eex_mev, ewell_mev, surfwell, efermi_mev)
    dens = torch.where(ok, dens, zero)
    return torch.where(dens < PHDENS_FLOOR, zero, dens)


def phdens2(
    ppi: Tensor,
    hpi: Tensor,
    pnu: Tensor,
    hnu: Tensor,
    gsp: Tensor,
    gsn: Tensor,
    ex_mev: Tensor,
    ewell_mev: Tensor,
    surfwell: bool | Tensor = False,
    *,
    ap2: Tensor | None = None,
    gsp_pauli: Tensor | None = None,
    gsn_pauli: Tensor | None = None,
    efermi_mev: float = EFERMI_MEV,
    phmodel: int = 1,
) -> Tensor:
    """Two-component particle-hole state density [MeV^-1] (phdens2.f90:58-79).

    ``omega(ppi, hpi, pnu, hnu, U) = gsp^(ppi+hpi) gsn^(pnu+hnu) (U - Apauli2)^(n-1)
    / (ppi! hpi! pnu! hnu! (n-1)!) * finitewell``.

    The Pauli correction ``Apauli2`` is TALYS's *precomputed table*, built once from the
    compound nucleus's ``gp(0,0)``/``gn(0,0)``: pass it as `ap2`, or give the compound-nucleus
    densities as `gsp_pauli`/`gsn_pauli`. The cut-off test
    ``Ap + factorn + factorp >= Eex`` (phdens2.f90:45) uses the *passed* ``gsp``/``gsn`` for
    the two `factor` terms even when ``Ap`` came from the table, which is what makes the two
    sets of densities matter separately; both are reproduced here.

    TALYS: phdens2.f90:1 (phdens2)
    Test: A-pe
    """
    if phmodel != 1:
        raise NotImplementedError("T8: phmodel 2 (phdensitytable.f90) is not ported")
    if _no_graph(ppi, hpi, pnu, hnu, gsp, gsn, ex_mev, ewell_mev, surfwell, ap2, gsp_pauli,
                 gsn_pauli):
        ip, ih, jp, jh = (_np(x, np.int64) for x in (ppi, hpi, pnu, hnu))
        gp_, gn_ = _np(gsp), _np(gsn)
        if ap2 is None:
            ap = _apauli2_arr(ip, ih, jp, jh, gp_ if gsp_pauli is None else _np(gsp_pauli),
                              gn_ if gsn_pauli is None else _np(gsn_pauli))
        else:
            ap = _np(ap2)
        return torch.as_tensor(np.asarray(_phdens2_arr(
            ip, ih, jp, jh, gp_, gn_, _np(ex_mev), _np(ewell_mev), _np(surfwell, bool), ap,
            efermi_mev)))
    ppi, hpi = ppi.to(torch.int64), hpi.to(torch.int64)
    pnu, hnu = pnu.to(torch.int64), hnu.to(torch.int64)
    if ap2 is None:
        ap2 = apauli2(
            ppi,
            hpi,
            pnu,
            hnu,
            gsp if gsp_pauli is None else gsp_pauli,
            gsn if gsn_pauli is None else gsn_pauli,
        )
    ppif, hpif = ppi.to(DTYPE), hpi.to(DTYPE)
    pnuf, hnuf = pnu.to(DTYPE), hnu.to(DTYPE)
    factorn = (pnuf * pnuf + hnuf * hnuf + pnuf + hnuf) / (4.0 * gsn)
    factorp = (ppif * ppif + hpif * hpif + ppif + hpif) / (4.0 * gsp)

    n = ppi + hpi + pnu + hnu
    p = ppi + pnu
    h = hpi + hnu
    npi = ppi + hpi
    nnu = pnu + hnu
    n1 = (n - 1).to(DTYPE)

    zero = torch.zeros_like(ex_mev + ap2)
    ok = (
        (ppi >= 0)
        & (hpi >= 0)
        & (pnu >= 0)
        & (hnu >= 0)
        & (n != 0)
        & (ap2 + factorn + factorp < ex_mev)
    )
    fac1 = factorial(ppi) * factorial(hpi) * factorial(pnu) * factorial(hnu) * factorial(n - 1)
    factor = gsp ** npi.to(DTYPE) * gsn ** nnu.to(DTYPE) / fac1
    u = torch.where(ok, ex_mev - ap2, torch.ones_like(zero))
    dens = factor * u**n1
    dens = dens * finitewell(p, h, ex_mev, ewell_mev, surfwell, efermi_mev)
    dens = torch.where(ok, dens, zero)
    return torch.where(dens < PHDENS_FLOOR, zero, dens)


def preeqpair(
    pair_cn_mev: Tensor,
    gs: Tensor,
    n: Tensor,
    e_mev: Tensor,
    pairmodel: int = 2,
) -> Tensor:
    """Pre-equilibrium pairing energy [MeV] (preeqpair.f90:44-70).

    `pairmodel 2` (TALYS's default) returns the ground-state pairing energy unchanged;
    `pairmodel 1` is Fu's exciton-number- and energy-dependent formula. ``gs`` is
    ``gp + gn`` for the two-component model and ``g`` for the one-component model.

    TALYS: preeqpair.f90:1 (preeqpair)
    Test: A-pe
    """
    zero = torch.zeros_like(pair_cn_mev + e_mev * 0.0)
    if pairmodel != 1:
        return torch.where(pair_cn_mev > 0, pair_cn_mev + zero, zero)
    nf = n.to(DTYPE)
    pos = pair_cn_mev > 0
    pcn = torch.where(pos, pair_cn_mev, torch.ones_like(pair_cn_mev))
    pair0 = torch.sqrt(pcn / (0.25 * gs))
    tc = 2.0 * pair0 / 3.5
    ncrit = 2.0 * gs * tc * float(torch.log(torch.tensor(2.0, dtype=DTYPE)))
    ratio = e_mev / pcn
    cond = ratio >= (0.716 + 2.44 * (nf / ncrit) ** 2.17)
    pairex = pair0 * (0.996 - 1.76 * (nf / ncrit) ** 1.6 / (ratio.clamp(min=1e-30) ** 0.68))
    pairex = torch.where(cond, pairex, torch.zeros_like(pairex))
    out = pcn - 0.25 * gs * pairex**2
    return torch.where(pos, out, zero)
