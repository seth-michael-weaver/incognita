"""Numerical helpers TALYS uses, vectorised: Gauss-Legendre and Gauss-Laguerre quadrature, cubic
splines, table location and first/second order interpolation, the trapezoid refinement stage,
the Coulomb self-energy factor, and bracketing root finders.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T1 (physics/hf/CONTRACT.md §7). Acceptance test: A-grid (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    gauleg.f90:1 (gauleg)
    gaulag.f90:1 (gaulag)
    spline.f90:1 (spline)
    splint.f90:1 (splint)
    locate.f90:1 (locate)
    pol1.f90:1 (pol1)
    pol2.f90:1 (pol2)
    trapzd.f90:1 (trapzd)
    fcoul.f90:1 (fcoul)
    rtbis.f90:1 (rtbis)
    zbrak.f90:1 (zbrak)

Everything is float64 (contract §4.1). TALYS computes all of these in single precision, so its
values differ from these at ~1e-7 relative; the algorithms, node orders, edge conventions and
quirks are TALYS's. Quirks reproduced on purpose, each documented where it lives:
``gauleg`` for odd n, ``gaulag`` being a fixed 32-point table, ``trapzd`` discarding the
previous estimate, and ``pol1`` dividing by zero when x1 == x2.

What TALYS calls Coulomb functions for the optical model (regular/irregular Coulomb wave
functions) live inside ECIS (`ecist.f`) and are ported with the optical solver (T5/T13); the
only free-standing Coulomb routine in TALYS's source is `fcoul`, the Coulomb self-energy
shape factor of the fission barrier model, ported here.
"""

from __future__ import annotations

from collections.abc import Callable

import torch
from torch import Tensor

from physics.hf.core.tensors import DTYPE

_GAULAG32_X = (
    4.4489365833267018e-02,
    2.3452610951961854e-01,
    5.7688462930188643e-01,
    1.0724487538178176e00,
    1.7224087764446454e00,
    2.5283367064257949e00,
    3.4922132730219945e00,
    4.6164567697497674e00,
    5.9039585041742439e00,
    7.3581267331862411e00,
    8.9829409242125961e00,
    1.0783018632539972e01,
    1.2763697986742725e01,
    1.4931139755522557e01,
    1.7292454336715315e01,
    1.9855860940336055e01,
    2.2630889013196774e01,
    2.5628636022459248e01,
    2.8862101816323475e01,
    3.2346629153964737e01,
    3.6100494805751974e01,
    4.0145719771539442e01,
    4.4509207995754938e01,
    4.9224394987308639e01,
    5.4333721333396907e01,
    5.9892509162134018e01,
    6.5975377287935053e01,
    7.2687628090662709e01,
    8.0187446977913523e01,
    8.8735340417892399e01,
    9.8829542868283973e01,
    1.1175139809793770e02,
)  # gaulag.f90:37-68
_GAULAG32_W = (
    0.3304819843083507,
    0.4587407851268658,
    0.4849878654872182,
    0.4426096880693881,
    0.3605326424695436,
    0.2656663769951280,
    0.1782159154205232,
    0.1091705767816519,
    6.1145860813398685e-02,
    3.1317779401083899e-02,
    1.4658271344239885e-02,
    6.2612634252105599e-03,
    2.4360914623364682e-03,
    8.6118549562028460e-04,
    2.7576380979237979e-04,
    7.9690665868882078e-05,
    2.0691503017038005e-05,
    4.8019782297417133e-06,
    9.8991814251114182e-07,
    1.7993892457523653e-07,
    2.8586401388458671e-08,
    3.9270011884309682e-09,
    4.6041202092947340e-10,
    4.5325816857372190e-11,
    3.6701261376652915e-12,
    2.3793474169186305e-13,
    1.1910333939327800e-14,
    4.3742147803396949e-16,
    1.0919014424838086e-17,
    1.6344758239998953e-19,
    1.1569861460303905e-21,
    2.1238022963305632e-24,
)  # gaulag.f90:69-100


def _t(x, like: Tensor | None = None) -> Tensor:
    dev = like.device if isinstance(like, Tensor) else None
    return torch.as_tensor(x, dtype=DTYPE, device=dev)


def gauleg(n: int, x1: float = -1.0, x2: float = 1.0, single: bool = True) -> tuple[Tensor, Tensor]:
    """Gauss-Legendre nodes and weights, in TALYS's node order: the first n/2 are the positive
    roots in descending order (cos of increasing angles), the second n/2 their negatives in the
    same order. TALYS always integrates on [-1, 1]; `x1`, `x2` map the nodes affinely (nodes
    x1..x2, weights scaled by (x2 - x1)/2), with the defaults reproducing TALYS exactly.

    Normalisation: TALYS's weights `(1 - x^2)/(n P_{n-1})^2` are HALF the textbook
    Gauss-Legendre weights, i.e. they sum to 1 on [-1, 1] and `sum w f` is the *average* of f
    over [-1, 1]. The mapped weights keep that normalisation (they sum to (x2 - x1)/2, so
    `sum w f` is half the integral).

    Newton iterations: exactly 10, from the asymptotic initial guess, as gauleg.f90:43-60.
    `gauleg.f90:50` then forms the weight from `p2` as it stood BEFORE the last Newton step --
    the derivative at the previous iterate, not the converged one. Reproduced as written.

    `single` (the default) runs the whole iteration in float32, the precision every variable in
    `gauleg.f90` is declared at, and widens afterwards. **This is not a fidelity nicety.** The
    weight comes out of an (n-1)-term recurrence for `P_{n-1}`, whose accumulated roundoff is
    worst exactly where `P_{n-1}` is smallest -- at the outermost node. For n = 50 that weight is
    **9.8e-4 high** against the exact one, versus 3.5e-5 for its two neighbours and ~1e-7 in the
    bulk. TALYS's GOE triple integral is dominated by that node, so `single=False` -- the exact
    float64 table, which is what a convergence study wants -- shifts the capture-channel width
    fluctuation factor by 9e-4, thirty times the compound port's whole error budget. Use the
    default whenever the goal is to reproduce TALYS.

    Quirk for odd n (TALYS only calls it with n = 50, compoundinit.f90:70-75): the middle root is
    never computed; entry n/2+1 is set to -node(1) and entry n to node(1), duplicating nodes.
    Reproduced as written; do not use odd n.

    TALYS: gauleg.f90:1 (gauleg)
    Test: tests/hf/test_core.py (the table itself); A-cn2 via compound/wfc.goe_prepare
    """
    dt = torch.float32 if single else DTYPE
    ns2 = n // 2
    i = torch.arange(1, ns2 + 1, dtype=dt)
    pi = torch.tensor(3.14159265358979323, dtype=dt)
    ti = (4 * i - 1) * pi / (4 * n + torch.tensor(2.0, dtype=dt))
    oi = torch.cos(ti + 1.0 / (8.0 * n * n * torch.tan(ti)))
    p = p2 = torch.ones_like(oi)
    for _ in range(10):
        p2 = torch.ones_like(oi)
        p1 = oi
        for k in range(2, n + 1):
            p = ((2 * k - 1) * oi * p1 - (k - 1) * p2) / torch.tensor(float(k), dtype=dt)
            p2 = p1
            p1 = p
        oi = oi - p * (1.0 - oi * oi) / (n * (p2 - oi * p))
    t = torch.zeros(n, dtype=DTYPE)
    w = torch.zeros(n, dtype=DTYPE)
    t[:ns2] = oi.to(DTYPE)
    w[:ns2] = ((1.0 - oi * oi) / ((n * p2) * (n * p2))).to(DTYPE)
    for j in range(ns2 + 1, n + 1):  # tgl(j) = -tgl(j - ns2), sequential as in Fortran
        t[j - 1] = -t[j - ns2 - 1]
        w[j - 1] = w[j - ns2 - 1]
    half = 0.5 * (x2 - x1)
    return 0.5 * (x2 + x1) + half * t, half * w


def gaulag(n: int = 32, alf: float = 0.0) -> tuple[Tensor, Tensor]:
    """Gauss-Laguerre nodes and weights for the Moldauer width-fluctuation integral
    (compoundinit.f90:58-59). TALYS does not compute them: gaulag.f90 is a hard-coded table of
    the 32-point rule for weight exp(-x) (alpha = 0), nodes ascending. Any other `n` or `alf`
    is refused rather than silently answered with the 32-point table.

    The tabulated "weights" are the SQUARE ROOTS of the Gauss-Laguerre weights: molprepare.f90
    forms `fxmsqrt = wmo * exp(0.5 x)` and uses `fxmsqrt * prod * fxmsqrt`, i.e. w * exp(x),
    the weight for integrating f(x) dx over [0, inf). They are returned as tabulated.

    TALYS: gaulag.f90:1 (gaulag)
    Test: A-cn2
    """
    if n != 32 or alf != 0.0:
        raise ValueError("TALYS's gaulag is the fixed 32-point, alpha = 0 table")
    return _t(_GAULAG32_X), _t(_GAULAG32_W)


def locate(xx: Tensor, x: Tensor, ib: int = 1, ie: int | None = None) -> Tensor:
    """Index j with xx[j] <= x < xx[j+1], batched over x, with TALYS's locate.f90 conventions.

    `xx` is a Fortran-indexed table (position k = Fortran index k, TALYS declares it
    ``xx(0:ie)``); the search runs over positions ib..ie (default 1..len-1). Bisection result
    `jl` in ib-1..ie, then: j = ib when x == xx[ib], j = ie-1 when x == xx[ie], else jl.
    Works for ascending and descending tables (`ascend = xx[ie] >= xx[ib]`); j = 0 if ib > ie.
    For a strictly monotone table this equals TALYS's bisection exactly (ties in the table may
    resolve to a different equal index). int64, same shape as x.

    TALYS: locate.f90:1 (locate)
    Test: A-grid
    """
    ie = xx.shape[-1] - 1 if ie is None else ie
    x = torch.as_tensor(x, dtype=xx.dtype, device=xx.device)
    if ib > ie:
        return torch.zeros(x.shape, dtype=torch.int64, device=xx.device)
    seg = xx[ib : ie + 1]
    ascend = bool(xx[ie] >= xx[ib])
    if ascend:
        # number of table entries <= x  ->  last position with xx <= x
        cnt = torch.searchsorted(seg.contiguous(), x.contiguous(), right=True)
    else:
        # descending: last position with xx > x
        cnt = torch.searchsorted((-seg).contiguous(), (-x).contiguous(), right=False)
    jl = ib - 1 + cnt
    j = torch.where(x == xx[ib], torch.full_like(jl, ib), jl)
    j = torch.where((x == xx[ie]) & (x != xx[ib]), torch.full_like(jl, ie - 1), j)
    return j


def pol1(x1: Tensor, x2: Tensor, y1: Tensor, y2: Tensor, x: Tensor) -> Tensor:
    """Linear interpolation exactly as TALYS's pol1: `y1 + (x - x1)/(x2 - x1) * (y2 - y1)`.
    TALYS has no x1 == x2 guard, so that case yields inf/NaN here too; callers that can hit it
    must mask first (contract §4.2). Units of y. Differentiable in all arguments.

    TALYS: pol1.f90:1 (pol1)
    Test: A-grid
    """
    if (type(x) is Tensor and type(x1) is Tensor and type(x2) is Tensor and type(y1) is Tensor
            and type(y2) is Tensor and not (x.ndim or x1.ndim or x2.ndim or y1.ndim or y2.ndim)
            and not (x.requires_grad or x1.requires_grad or x2.requires_grad or y1.requires_grad
                     or y2.requires_grad)
            and x.dtype is _F64 and x1.dtype is _F64 and x2.dtype is _F64 and y1.dtype is _F64
            and y2.dtype is _F64 and x.is_cpu and y1.is_cpu and y2.is_cpu):
        # COREX: one point off the graph (no argument asks for one): the same five operations on
        # Python floats
        fx1 = float(x1)
        den = float(x2) - fx1
        if den != 0.0:
            fy1 = float(y1)
            return torch.tensor(fy1 + (float(x) - fx1) / den * (float(y2) - fy1), dtype=_F64)
    fac = (x - x1) / (x2 - x1)
    return y1 + fac * (y2 - y1)


_F64 = torch.float64


def pol2(
    x1: Tensor, x2: Tensor, x3: Tensor, y1: Tensor, y2: Tensor, y3: Tensor, x: Tensor
) -> Tensor:
    """Quadratic (3-point Lagrange) interpolation as TALYS's pol2, term order preserved. Units of y.

    TALYS: pol2.f90:1 (pol2)
    Test: A-grid
    """
    yy1 = (x - x2) * (x - x3) / ((x1 - x2) * (x1 - x3)) * y1
    yy2 = (x - x1) * (x - x3) / ((x2 - x1) * (x2 - x3)) * y2
    yy3 = (x - x1) * (x - x2) / ((x3 - x1) * (x3 - x2)) * y3
    return yy1 + yy2 + yy3


def spline(x: Tensor, y: Tensor, yp1: float = 2.0e30, ypn: float = 2.0e30) -> Tensor:
    """Second derivatives y2 for a cubic spline through (x, y), TALYS spline.f90 conventions:
    an end slope > 0.99e30 means a natural end (y2 = 0); otherwise the first derivative there
    is `yp1`/`ypn`. Batched over leading dimensions of x and y (..., n); the tridiagonal sweep
    is a loop over nodes with tensor operations inside. Differentiable in y (and x).

    TALYS: spline.f90:1 (spline)
    Test: A-grid
    """
    x = torch.as_tensor(x, dtype=DTYPE)
    y = torch.as_tensor(y, dtype=DTYPE, device=x.device)
    x, y = torch.broadcast_tensors(x, y)
    n = x.shape[-1]
    zero = torch.zeros(x.shape[:-1], dtype=DTYPE, device=x.device)
    y2 = [None] * n
    u = [None] * n
    if yp1 > 0.99e30:
        y2[0], u[0] = zero, zero
    else:
        dx = x[..., 1] - x[..., 0]
        y2[0] = zero - 0.5
        u[0] = (3.0 / dx) * ((y[..., 1] - y[..., 0]) / dx - yp1)
    for i in range(1, n - 1):
        sig = (x[..., i] - x[..., i - 1]) / (x[..., i + 1] - x[..., i - 1])
        psp = sig * y2[i - 1] + 2.0
        y2[i] = (sig - 1.0) / psp
        u[i] = (
            6.0
            * (
                (y[..., i + 1] - y[..., i]) / (x[..., i + 1] - x[..., i])
                - (y[..., i] - y[..., i - 1]) / (x[..., i] - x[..., i - 1])
            )
            / (x[..., i + 1] - x[..., i - 1])
            - sig * u[i - 1]
        ) / psp
    if ypn > 0.99e30:
        qn, un = zero, zero
    else:
        dx = x[..., n - 1] - x[..., n - 2]
        qn = zero + 0.5
        un = (3.0 / dx) * (ypn - (y[..., n - 1] - y[..., n - 2]) / dx)
    y2[n - 1] = (un - qn * u[n - 2]) / (qn * y2[n - 2] + 1.0)
    for k in range(n - 2, -1, -1):
        y2[k] = y2[k] * y2[k + 1] + u[k]
    return torch.stack(y2, dim=-1)


def splint(xa: Tensor, ya: Tensor, y2a: Tensor, x: Tensor) -> Tensor:
    """Cubic spline evaluation at x (any shape) on one table (xa, ya, y2a) of length n, as
    splint.f90: the bracketing interval is found by TALYS's bisection, which clamps to the first
    and last intervals, so x outside the table extrapolates the end cubic. Raises on a repeated
    abscissa (TALYS stops with 'bad xa input in splint'). Differentiable in ya, y2a and x.

    TALYS: splint.f90:1 (splint)
    Test: A-grid
    """
    xa = torch.as_tensor(xa, dtype=DTYPE)
    x = torch.as_tensor(x, dtype=DTYPE, device=xa.device)
    n = xa.shape[-1]
    # bisection: klo = last k (1-based, 1..n-1) with xa(k) <= x
    cnt = torch.searchsorted(xa.detach().contiguous(), x.detach().contiguous(), right=True)
    klo = torch.clamp(cnt - 1, 0, n - 2)
    khi = klo + 1
    hsp = xa[khi] - xa[klo]
    if bool((hsp == 0).any()):
        raise ValueError("bad xa input in splint")
    a = (xa[khi] - x) / hsp
    b = (x - xa[klo]) / hsp
    return (
        a * ya[klo] + b * ya[khi] + ((a**3 - a) * y2a[klo] + (b**3 - b) * y2a[khi]) * (hsp**2) / 6.0
    )


def trapzd(func: Callable[[Tensor], Tensor], a: float, b: float, n: int) -> Tensor:
    """The n-th trapezoid refinement stage of trapzd.f90 for integrand `func` (vectorised: func
    is called once on all abscissae of the stage).

    Quirk reproduced exactly: TALYS resets `snew = 0` on entry, so it never carries the previous
    estimate. Stage 1 returns the trapezoid `0.5 (b - a)(f(a) + f(b))`; stage n >= 2 returns
    `0.5 (b - a) * mean of f at the 2**(n-2) midpoints`, i.e. HALF the midpoint rule, not the
    refined trapezoid. trans.f90 iterates stages until consecutive values agree to 1%, so the
    fission transmission it produces carries this. The midpoint abscissae are accumulated
    (`x = x + del`) as in the Fortran.

    TALYS: trapzd.f90:1 (trapzd)
    Test: A-fis
    """
    a_t, b_t = _t(a), _t(b)
    if n == 1:
        return 0.5 * (b_t - a_t) * (func(a_t.reshape(1)) + func(b_t.reshape(1)))[0]
    it = 2 ** (n - 2)
    tnm = float(it)
    delta = (b_t - a_t) / tnm
    steps = torch.full((it,), float(delta), dtype=DTYPE)
    steps[0] = float(a_t + 0.5 * delta)
    xs = torch.cumsum(steps, dim=0)
    s = func(xs).sum()
    return 0.5 * (0.0 + (b_t - a_t) * s / tnm)


def fcoul(eps: Tensor) -> Tensor:
    """Coulomb self-energy shape factor of a spheroid with eccentricity parameter `eps`
    (Brosa fission model, used by bdef.f90:31): (1 + e^2)^(1/3) atan(e)/e for e < 0, 1 at 0,
    (1 - e^2)^(1/3) ln((1 + e)/(1 - e))/(2e) for e > 0 (fcoul.f90's arithmetic IF).
    Dimensionless, differentiable away from e = 0.

    TALYS: fcoul.f90:1 (fcoul)
    Test: A-fis
    """
    e = torch.as_tensor(eps, dtype=DTYPE)
    one = torch.ones_like(e)
    safe = torch.where(e == 0, one, e)
    neg = (1.0 + safe**2) ** (1.0 / 3.0) / safe * torch.atan(safe)
    sp = torch.where(e > 0, safe, 0.5 * one)
    pos = (1.0 - sp**2) ** (1.0 / 3.0) / (2.0 * sp) * torch.log((1.0 + sp) / (1.0 - sp))
    return torch.where(e < 0, neg, torch.where(e > 0, pos, one))


def rtbis(func: Callable[[Tensor], Tensor], x1: Tensor, x2: Tensor, xacc: float) -> Tensor:
    """Root of `func` by bisection as rtbis.f90, batched: orient on the sign of f(x1) (f < 0 ->
    start at x1 and step toward x2), halve 40 times at most, stop per element when |dx| < xacc
    or f(xmid) == 0. No bracketing check, as in TALYS: an unbracketed interval returns an end.
    func must accept and return tensors of the batch shape.

    TALYS: rtbis.f90:1 (rtbis)
    Test: A-ld
    """
    x1 = torch.as_tensor(x1, dtype=DTYPE)
    x2 = torch.as_tensor(x2, dtype=DTYPE, device=x1.device)
    f = func(x1)
    neg = f < 0.0
    root = torch.where(neg, x1, x2)
    dx = torch.where(neg, x2 - x1, x1 - x2)
    active = torch.ones_like(root, dtype=torch.bool)
    for _ in range(40):
        dx = torch.where(active, dx * 0.5, dx)
        xmid = root + dx
        fmid = func(xmid)
        root = torch.where(active & (fmid <= 0.0), xmid, root)
        active = active & ~((dx.abs() < xacc) | (fmid == 0.0))
        if not bool(active.any()):
            break
    return root


def zbrak(
    func: Callable[[Tensor], Tensor], x1: float, x2: float, n: int, nb: int
) -> tuple[Tensor, Tensor]:
    """Brackets of sign changes of `func` on [x1, x2] split into n steps (zbrak.f90): returns the
    lower and upper ends of at most `nb` brackets, in order (length = number found). The grid is
    accumulated `x = x + dx` as in the Fortran; func is called once on all n+1 points.

    TALYS: zbrak.f90:1 (zbrak)
    Test: A-ld
    """
    dx = (x2 - x1) / n
    steps = torch.full((n + 1,), dx, dtype=DTYPE)
    steps[0] = x1
    xs = torch.cumsum(steps, dim=0)
    fv = func(xs)
    change = (fv[1:] * fv[:-1]) < 0.0
    idx = torch.nonzero(change).flatten()[:nb]
    return xs[idx], xs[idx + 1]
