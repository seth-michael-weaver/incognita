"""Angular-momentum algebra: Clebsch-Gordan and Racah coefficients, Legendre polynomials
(vectorised, float64).

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T1 (physics/hf/CONTRACT.md §7). Acceptance test: A-cn2 (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    clebsch.f90:1 (clebsch)
    racah.f90:1 (racah)
    plegendre.f90:1 (plegendre)
    compoundinit.f90:1 (compoundinit)

TALYS evaluates both coefficients from a table of log-factorials `logfact(k) = ln((k-1)!)`
(compoundinit.f90:82-86, `numfact = 6 numl = 360` entries) with a closed product form and a
Horner-style sum `s = 1 - s t` over the Racah series. The port keeps that algorithm, including
the integer rounding of the spins (`int(2 j + 1e-3)`), the early returns for forbidden
couplings, and the cap `(j1 + j2 + j3)/2 + 2 > numfact -> 0`, and vectorises it over any batch
shape: the series loop runs to the batch's longest series with finished elements frozen. The
log-factorials are lgamma in float64 instead of TALYS's single-precision running sum.

Callers in TALYS: comptarget.f90:680-685 (compound angular distributions), where both are
called with m = 0 for Clebsch-Gordan.
"""

from __future__ import annotations

import torch
from torch import Tensor

from physics.hf.core.tensors import DTYPE

NUMFACT = 6 * 60  # A0_talys_mod.f90:65, numfact = 6 * numl
_EPS = 1.0e-3


def logfact(k: Tensor) -> Tensor:
    """TALYS's `logfact(k) = ln((k - 1)!)` for integer k >= 1 (compoundinit.f90:82-86), as
    lgamma(k) in float64.

    TALYS: compoundinit.f90:1 (compoundinit)
    Test: A-cn2
    """
    kk = torch.as_tensor(k, dtype=DTYPE)
    if kk.device.type == "cpu" and not kk.requires_grad and kk.numel():
        # CCFAST2: every caller passes integer k in [1, NUMFACT + 2] (clebsch/racah indices, the
        # `_g` clamp), so the values are lgamma's own at those integers, read from a table built
        # by the same torch.lgamma -- bit-identical, without a special-function evaluation per
        # element (0.19 CPU-s of an Nd-150 run on the Mac, 1,548 calls from dwba's Clebsches).
        idx = kk.to(torch.int64)
        if bool((idx.to(DTYPE) == kk).all()) and int(idx.min()) >= 0 and int(idx.max()) < _LF_N:
            return _LOGFACT_TABLE[idx]
    return torch.lgamma(kk)


_LF_N = NUMFACT + 64
_LOGFACT_TABLE = torch.lgamma(torch.arange(_LF_N, dtype=DTYPE))  # lgamma(0) = inf, never read


def _twice(j: Tensor) -> Tensor:
    # int(2. * aj + eps): truncation toward zero, as the Fortran `int`
    return torch.trunc(2.0 * j + _EPS).to(torch.int64)


def _twice_m(m: Tensor) -> Tensor:
    # int(2. * am + sign(eps, am)): sign(eps, 0.) is +eps in Fortran
    return torch.trunc(2.0 * m + torch.where(m >= 0, _EPS, -_EPS)).to(torch.int64)


def _g(k: Tensor) -> Tensor:
    # g(k) with an out-of-range guard: indices < 1 only occur on masked-out elements
    return logfact(torch.clamp(k, min=1))


def _horner(n: Tensor, factor) -> Tensor:
    """s after `do j = 1, n: t = factor(q); s = 1 - s t; q = q - 1`, q starting at n - 1,
    vectorised with per-element n (elements with smaller n skip the leading iterations)."""
    nmax = int(n.max()) if n.numel() else 0
    s = torch.ones(n.shape, dtype=DTYPE, device=n.device)
    for step in range(nmax):
        q = torch.as_tensor(float(nmax - 1 - step), dtype=DTYPE, device=n.device)
        live = q <= (n - 1).to(DTYPE)
        s = torch.where(live, 1.0 - s * factor(q), s)
    return s


def clebsch(
    j1: Tensor, j2: Tensor, j3: Tensor, m1: Tensor, m2: Tensor, m3: Tensor | None = None
) -> Tensor:
    """Clebsch-Gordan coefficient <j1 m1 j2 m2 | j3 m3>, same phase convention and algorithm as
    clebsch.f90. `m3` defaults to m1 + m2; when given and m1 + m2 != m3 the coefficient is 0.
    Batched over the broadcast shape of the arguments (spins as floats, half-integers allowed).
    Dimensionless.

    clebsch.f90 contains a second branch for m = 0 couplings behind
    ``if (m3 /= 0 .or. m1 /= 0 .or. m1 /= 1)``, a condition that is always true (m1 cannot be
    both 0 and 1), so that branch is dead code in TALYS and is not ported.

    TALYS: clebsch.f90:1 (clebsch)
    Test: A-cn2
    """
    a = [torch.as_tensor(v, dtype=DTYPE) for v in (j1, j2, j3, m1, m2)]
    if m3 is None:
        a.append(a[3] + a[4])
    else:
        a.append(torch.as_tensor(m3, dtype=DTYPE))
    aj1, aj2, aj3, am1, am2, am3 = torch.broadcast_tensors(*a)
    J1, J2, J3 = _twice(aj1), _twice(aj2), _twice(aj3)
    M1, M2, M3 = _twice_m(am1), _twice_m(am2), _twice_m(am3)
    ok = (M1 + M2 - M3) == 0
    i10 = torch.div(J1 + J2 + J3, 2, rounding_mode="trunc") + 2
    i11 = J3 + 2
    ok &= i10 <= NUMFACT
    raw = [
        J1 + J2 - J3,
        J2 + J3 - J1,
        J3 + J1 - J2,
        J1 - M1,
        J1 + M1,
        J2 - M2,
        J2 + M2,
        J3 - M3,
        J3 + M3,
    ]
    n = i10.clone()
    ii = []
    for r in raw:
        k = torch.div(r, 2, rounding_mode="trunc")
        ok &= (r == 2 * k) & (k >= 0)
        n = torch.minimum(n, k)
        ii.append(k + 1)
    i1, i2, i3, i4, i5, i6, i7, i8, i9 = ii
    la = i1 - i5
    lb = i1 - i6
    il = torch.clamp(torch.maximum(la, lb), min=0)
    c = (
        _g(i11)
        - _g(i11 - 1)
        + _g(i1)
        + _g(i2)
        + _g(i3)
        - _g(i10)
        + _g(i4)
        + _g(i5)
        + _g(i6)
        + _g(i7)
        + _g(i8)
        + _g(i9)
    ) * 0.5
    k1, k2, k3 = i1 - il, i4 - il, i7 - il
    n1, n2, n3 = il + 1, il - la + 1, il - lb + 1
    c = c - _g(k1) - _g(k2) - _g(k3) - _g(n1) - _g(n2) - _g(n3)
    c = torch.exp(c)
    c = torch.where(il % 2 != 0, -c, c)
    aa, bb, hh = (k1 - 1).to(DTYPE), (k2 - 1).to(DTYPE), (k3 - 1).to(DTYPE)
    dd, ee, ff = n1.to(DTYPE), n2.to(DTYPE), n3.to(DTYPE)
    nn = torch.where(ok, n, torch.zeros_like(n))
    s = _horner(nn, lambda q: (aa - q) / (dd + q) * (bb - q) / (ee + q) * (hh - q) / (ff + q))
    val = torch.where(nn == 0, c, c * s)
    return torch.where(ok & (n >= 0), val, torch.zeros_like(val))


def racah(a: Tensor, b: Tensor, c: Tensor, d: Tensor, e: Tensor, f: Tensor) -> Tensor:
    """Racah W(a b c d; e f) coefficient as racah.f90 (same sign convention), batched over the
    broadcast shape of the arguments; 0 for couplings violating a triangle or parity rule.
    Dimensionless.

    TALYS: racah.f90:1 (racah)
    Test: A-cn2
    """
    args = torch.broadcast_tensors(*[torch.as_tensor(v, dtype=DTYPE) for v in (a, b, c, d, e, f)])
    ja, jb, jc, jd, je, jf = (_twice(v) for v in args)
    raw = [
        ja + jb - je,
        jb + je - ja,
        je + ja - jb,
        jc + jd - je,
        jd + je - jc,
        je + jc - jd,
        ja + jc - jf,
        jc + jf - ja,
        jf + ja - jc,
        jb + jd - jf,
        jd + jf - jb,
        jf + jb - jd,
    ]
    i13, i14, i15, i16 = ja + jb + je, jc + jd + je, ja + jc + jf, jb + jd + jf
    n = i16.clone()
    ok = torch.ones(n.shape, dtype=torch.bool, device=n.device)
    ii = []
    for r in raw:
        k = torch.div(r, 2, rounding_mode="trunc")
        ok &= (r == 2 * k) & (k >= 0)
        n = torch.minimum(n, k)
        ii.append(k + 1)
    i1, i2, i3, i4, i5, i6, i7, i8, i9, i10, i11, i12 = ii
    i13, i14, i15, i16 = (torch.div(v, 2, rounding_mode="trunc") for v in (i13, i14, i15, i16))
    il = torch.maximum(
        torch.maximum(torch.maximum(i13, i14), torch.maximum(i15, i16)), torch.zeros_like(i13)
    )
    j1, j2, j3, j4 = il - i13 + 1, il - i14 + 1, il - i15 + 1, il - i16 + 1
    j5, j6, j7 = i13 + i4 - il, i15 + i5 - il, i16 + i6 - il
    ok &= (j5 >= 1) & (j6 >= 1) & (j7 >= 1)
    h = -torch.exp(
        0.5
        * (
            _g(i1)
            + _g(i2)
            + _g(i3)
            - _g(i13 + 2)
            + _g(i4)
            + _g(i5)
            + _g(i6)
            - _g(i14 + 2)
            + _g(i7)
            + _g(i8)
            + _g(i9)
            - _g(i15 + 2)
            + _g(i10)
            + _g(i11)
            + _g(i12)
            - _g(i16 + 2)
        )
        + _g(il + 2)
        - _g(j1)
        - _g(j2)
        - _g(j3)
        - _g(j4)
        - _g(j5)
        - _g(j6)
        - _g(j7)
    )
    h = torch.where(j5 % 2 != 0, -h, h)
    p = (il + 2).to(DTYPE)
    r_, o_, v_, w_ = j1.to(DTYPE), j2.to(DTYPE), j3.to(DTYPE), j4.to(DTYPE)
    x_, y_, z_ = (j5 - 1).to(DTYPE), (j6 - 1).to(DTYPE), (j7 - 1).to(DTYPE)
    nn = torch.where(ok, n, torch.zeros_like(n))
    s = _horner(
        nn,
        lambda q: (
            (p + q) / (r_ + q) * (x_ - q) / (o_ + q) * (y_ - q) / (v_ + q) * (z_ - q) / (w_ + q)
        ),
    )
    val = torch.where(nn == 0, h, h * s)
    return torch.where(ok & (n >= 0), val, torch.zeros_like(val))


def plegendre(lmax: int, x: Tensor) -> Tensor:
    """Legendre polynomials P_0..P_lmax at x, shape (..., lmax+1), by the upward recurrence of
    plegendre.f90 (which returns only P_l; `plegendre_l` gives that). Differentiable in x.

    TALYS: plegendre.f90:1 (plegendre)
    Test: A-cn2
    """
    x = torch.as_tensor(x, dtype=DTYPE)
    pl = [torch.ones_like(x), x]
    for i in range(2, lmax + 1):
        pl.append((x * (2 * i - 1) * pl[i - 1] - (i - 1) * pl[i - 2]) / i)
    return torch.stack(pl[: lmax + 1], dim=-1)


def plegendre_l(l: int, x: Tensor) -> Tensor:  # noqa: E741
    """P_l(x), the value TALYS's plegendre(l, x) function returns.

    TALYS: plegendre.f90:1 (plegendre)
    Test: A-cn2
    """
    return plegendre(max(l, 1), x)[..., l]
