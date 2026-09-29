"""Photon strength functions for every `strength` / `strengthM1` model TALYS supports, default
SMLO-2019 tables (strength 9) and IAEA-CRP M1 with upbend (strengthM1 3).

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T7 (physics/hf/CONTRACT.md §7). Acceptance test: A-psf (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    fstrength.f90:1 (fstrength)
    locate.f90:1 (locate) -- private copy until T1's core.numerics lands

Vectorised over the gamma energy: TALYS calls fstrength once per (Egamma); here `e_gamma_mev`
is a tensor and every per-point branch of the Fortran (temperature bracket, table interval,
log-versus-linear interpolation) is taken elementwise with torch.where, so the result is the
same as the scalar loop point by point.

Not ported (raise): strength / strengthM1 11 (D1M-intra, J-pi resolved tables) and user
`Exlfile` tables.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import torch
from torch import Tensor

from physics.hf.core.constants import talys_constants
from physics.hf.core.tensors import DTYPE
from physics.hf.gamma.parameters import NUMGAMQRPA, PI2H2C2, GammaParameters, table_arrays

if TYPE_CHECKING:
    from physics.hf.input.defaults import Options

TWOPI = float(talys_constants()["twopi"])


def kgr(l: int) -> float:  # noqa: E741
    """kgr(l) = pi2h2c2 / (2l + 1), set at strucinitial.f90 line 499.

    TALYS: strucinitial.f90:1 (strucinitial)
    Test: A-psf
    """
    return PI2H2C2 / (2 * l + 1.0)


def _locate(xx: Tensor, x: Tensor) -> Tensor:
    """TALYS locate(xx, 0, ie, x, j) for ascending xx(0:ie), batched over x -- `_bisect`'s
    result, read from a per-table lookup.

    SPEEDD: the bisection's answer is a step function of x that can only change AT a table
    value (every comparison is `x >= xx(jm)`), so it is fixed by its value at each distinct table
    value and at one point inside each gap between them. `_partition` evaluates the literal
    bisection there once per table; a query is then a searchsorted into the sorted table values.
    Integer-identical to `_bisect` for every x, including NaN and x outside the table.
    TALYS: locate.f90:1
    """
    ie = xx.shape[0] - 1
    xs = xx.detach()
    xv = x.detach()
    bps, j_at, j_in, j_nan = _partition(xs)
    pos = torch.searchsorted(bps, xv.contiguous(), right=False)
    hit = (pos < bps.shape[0]) & (bps[pos.clamp(max=bps.shape[0] - 1)] == xv)
    jl = torch.where(hit, j_at[pos.clamp(max=bps.shape[0] - 1)], j_in[pos])
    jl = torch.where(torch.isnan(xv), torch.full_like(jl, j_nan), jl)
    j = torch.where(xv == xs[0], torch.zeros_like(jl), jl)
    j = torch.where((xv != xs[0]) & (xv == xs[ie]), torch.full_like(jl, ie - 1), j)
    return j


_PARTITIONS: dict = {}


def _partition(xs: Tensor):
    """(sorted distinct table values, bisection j at each, bisection j inside each of the len+1
    open gaps, bisection j at NaN) for one table, cached by its bytes."""
    key = (xs.shape[0], xs.numpy().tobytes())
    got = _PARTITIONS.get(key)
    if got is None:
        import math

        bps = torch.unique(xs[~torch.isnan(xs)])  # sorted
        vals = bps.tolist()
        inner = []
        lo = -math.inf
        for k, v in enumerate(vals + [math.inf]):
            if k == 0:
                inner.append(math.nextafter(v, -math.inf) if vals else 0.0)
            elif k == len(vals):
                inner.append(math.nextafter(lo, math.inf))
            else:
                mid = 0.5 * (lo + v)
                inner.append(mid if lo < mid < v else lo)  # an empty gap is never looked up
            lo = v
        j_at = _bisect(xs, bps)
        j_in = _bisect(xs, torch.tensor(inner, dtype=xs.dtype))
        j_nan = int(_bisect(xs, torch.tensor([math.nan], dtype=xs.dtype))[0])
        got = (bps, j_at, j_in, j_nan)
        if len(_PARTITIONS) > 256:
            _PARTITIONS.clear()
        _PARTITIONS[key] = got
    return got


def _bisect(xx: Tensor, x: Tensor) -> Tensor:
    """TALYS locate(xx, 0, ie, x, j) for ascending xx(0:ie), batched over x.

    Kept private on purpose: core.numerics.locate uses searchsorted, exact only on strictly
    monotone tables, and the wtable stretch makes TALYS's PSF energy table non-monotone
    (e(0) = 0, e(1) < 0), where only the literal bisection reproduces TALYS.
    TALYS: locate.f90:1 -- j = jl from the bisection, except x == xx(0) -> 0 and
    x == xx(ie) -> ie - 1.
    """
    ie = xx.shape[0] - 1
    xs = xx.detach()
    xv = x.detach()
    jl = torch.full(xv.shape, -1, dtype=torch.int64)
    ju = torch.full(xv.shape, ie + 1, dtype=torch.int64)
    ascend = bool(xs[ie] >= xs[0])
    # the Fortran bisection verbatim: the table need not be monotonic (the wtable stretch can
    # push e(1) below e(0) = 0), so searchsorted would not reproduce it
    while bool(((ju - jl) > 1).any()):
        active = (ju - jl) > 1
        jm = (ju + jl) // 2
        go_up = (xv >= xs[jm.clamp(0, ie)]) == ascend
        jl = torch.where(active & go_up, jm, jl)
        ju = torch.where(active & ~go_up, jm, ju)
    j = torch.where(xv == xs[0], torch.zeros_like(jl), jl)
    j = torch.where((xv != xs[0]) & (xv == xs[ie]), torch.full_like(jl, ie - 1), j)
    return j


def _interp(e: Tensor, eb: Tensor, ee: Tensor, gamb: Tensor, game: Tensor) -> Tensor:
    """fstrength.f90 table interpolation: log10-linear when both ends > 0, else linear."""
    both = (gamb > 0.0) & (game > 0.0)
    safe_b = torch.where(both, gamb, torch.ones_like(gamb))
    safe_e = torch.where(both, game, torch.ones_like(game))
    frac = (e - eb) / (ee - eb)
    logv = torch.pow(10.0, torch.log10(safe_b) + frac * (torch.log10(safe_e) - torch.log10(safe_b)))
    lin = gamb + frac * (game - gamb)
    return torch.where(both, logv, lin)


def _min20(efs):
    """`min(Efs, 20.)` for a float or, elementwise, for a tensor of Efs (one per case)."""
    if isinstance(efs, Tensor):
        return torch.clamp(efs, max=20.0)
    return min(efs, 20.0)


def _scalar(x) -> Tensor:
    return torch.as_tensor(x, dtype=DTYPE)


def _table_strength(
    gp: GammaParameters,
    efs_mev: float,
    e_gamma: Tensor,
    irad: int,
    l: int,  # noqa: E741
) -> Tensor:
    """The tabulated branch of fstrength.f90 (the `else` path after the model-11 block)."""
    e_tab, f_tab = table_arrays(gp, irad, 1)  # fstrength reads qrpa(...)%e(nen, irad, 1)
    n_t0 = gp.n_tqrpa if (irad == 1 and l == 1) else 1
    eq_last = e_tab[NUMGAMQRPA]
    if n_t0 > 1:
        e = _min20(efs_mev) + _scalar(gp.S_k0_mev) - _scalar(gp.delta_mev) - e_gamma
        alev = _scalar(gp.alev_per_mev)
        ok = (e > 0.0) & (alev > 0.0)
        tnuc = torch.where(
            ok, torch.sqrt(torch.where(ok, e, torch.ones_like(e)) / alev), torch.zeros_like(e)
        )
        tq = gp.tqrpa_mev
        # nT = it - 1 for the first Tqrpa(it) > Tnuc, else nT0 (Tqrpa ascends)
        n_t = (tq.unsqueeze(0) <= tnuc.detach().unsqueeze(-1)).sum(-1).clamp(max=n_t0)
        tb = tq[(n_t.clamp(min=1) - 1)]
        te = torch.where(n_t < n_t0, tq[n_t.clamp(max=n_t0 - 1)], tb)
        itemp = 2
    else:
        tnuc = torch.zeros_like(e_gamma)
        n_t = torch.ones_like(e_gamma, dtype=torch.int64)
        tb = torch.zeros_like(e_gamma)
        te = torch.zeros_like(e_gamma)
        itemp = 1

    inside = e_gamma <= eq_last
    nen_in = _locate(e_tab, e_gamma).clamp(0, NUMGAMQRPA - 1)
    nen = torch.where(inside, nen_in, torch.full_like(nen_in, NUMGAMQRPA - 1))
    fvals = []
    for it in range(1, itemp + 1):
        jt = n_t if it == 1 else n_t + 1
        jt = jt.clamp(max=n_t0)  # `if (jt > nT0) jt = nT0`
        et = tb if it == 1 else te
        eb = e_tab[nen]
        ee = e_tab[nen + 1]
        col = jt - 1  # 1-based temperature index -> 0-based column
        f_jt_b = f_tab[nen, col]
        f_jt_e = f_tab[nen + 1, col]
        f_1_b = f_tab[nen, 0]
        f_1_e = f_tab[nen + 1, 0]
        # inside the table: column jt only below the bracket temperature (fstrength.f90:417-426)
        gamb = torch.where(inside & ~(eb <= et), f_1_b, f_jt_b)
        game = torch.where(inside & ~(ee <= et), f_1_e, f_jt_e)
        fvals.append(_interp(e_gamma, eb, ee, gamb, game))
    f2 = fvals[-1]
    if n_t0 > 1:
        fb, fe = fvals
        span = te - tb
        do_t = span != 0.0
        f_t = _interp(tnuc, tb, torch.where(do_t, te, tb + 1.0), fb, fe)
        f2 = torch.where(do_t, f_t, f2)
    return f2


def fstrength_gp(
    gp: GammaParameters,
    efs_mev: float,
    e_gamma_mev: Tensor,
    irad: int,
    l: int,  # noqa: E741
    e_inc_mev: float | None = None,
) -> Tensor:
    """f_XL(E_gamma) [MeV^-3]; fstrength.f90 with the nucleus' parameters passed explicitly.

    efs_mev    (a float, or a tensor broadcastable against e_gamma_mev for many cases at once)
               Efs, the incident-energy-like argument TALYS passes (0 for the psf file, Einc in
               tgamma, E in radwidtheory); enters the temperature Tnuc and the E1 upbend.
    e_inc_mev  the global Einc, read only by strength 1 and 5 (`Egamma /= Einc`).

    TALYS: fstrength.f90:1 (fstrength)
    Test: A-psf
    """
    if gp.strength == 11 or gp.strengthM1 == 11:
        raise NotImplementedError("T7: strength 11 not ported")
    e_gamma = torch.as_tensor(e_gamma_mev, dtype=DTYPE)
    flag_m1 = irad == 0 and l == 1
    flag_e1 = irad == 1 and l == 1
    out = torch.zeros_like(e_gamma)
    egam2 = e_gamma**2
    S = _scalar(gp.S_k0_mev)
    delta = _scalar(gp.delta_mev)
    alev = _scalar(gp.alev_per_mev)
    einc = efs_mev if e_inc_mev is None else e_inc_mev
    k = kgr(l)

    def tnuc_of(efs: float) -> Tensor:
        e = _min20(efs) + S - delta - e_gamma
        ok = (e > 0.0) & (alev > 0.0)
        return torch.where(
            ok, torch.sqrt(torch.where(ok, e, torch.ones_like(e)) / alev), torch.zeros_like(e)
        )

    for i in range(1, gp.ngr[irad][l] + 1):  # fstrength.f90:94
        sgr1 = gp.sgr_mb[irad, l, i]
        egr1 = gp.egr_mev[irad, l, i]
        ggr1 = gp.ggr_mev[irad, l, i]
        egr2 = egr1**2
        ggr2 = ggr1**2
        if (
            gp.strength == 1 and flag_e1
        ):  # Kopecky-Uhl generalised Lorentzian, fstrength.f90:131-144
            tn = torch.where(e_gamma != einc, tnuc_of(efs_mev), torch.zeros_like(e_gamma))
            ggredep0 = ggr1 * TWOPI**2 * tn**2 / egr2
            ggredep = ggredep0 + ggr1 * egam2 / egr2
            enum = ggredep * e_gamma
            denom = (egam2 - egr2) ** 2 + egam2 * ggredep**2
            out = out + k * sgr1 * ggr1 * (enum / denom + 0.7 * ggredep0 / egr1**3)
        slo = (
            gp.strength == 2
            or ((gp.strength in (3, 4) or gp.strength >= 6) and not gp.qrpaexist(1, 1))
            or l != 1
            or irad != 1
        )
        if slo:  # standard Lorentzian, fstrength.f90:148-156
            pos = e_gamma > 0.001
            enum = ggr2 * e_gamma ** (3 - 2 * l)
            denom = (egam2 - egr2) ** 2 + egam2 * ggr2
            out = out + torch.where(pos, k * sgr1 * enum / denom, torch.zeros_like(e_gamma))
        table = (gp.strength in (3, 4) or gp.strength >= 6) and (
            (gp.qrpaexist(1, 1) and flag_e1)
            or (gp.qrpaexist(0, 1) and gp.strengthM1 >= 8 and flag_m1)
        )
        if table:  # assignment, not a sum (fstrength.f90:356)
            out = _table_strength(gp, efs_mev, e_gamma, irad, l)
        if gp.strength == 5 and flag_e1:  # Goriely hybrid, fstrength.f90:360-372
            tn = torch.where(e_gamma != einc, tnuc_of(efs_mev), torch.zeros_like(e_gamma))
            pos = e_gamma > 0.0
            eg = torch.where(pos, e_gamma, torch.ones_like(e_gamma))
            ggredep = 0.7 * ggr1 * (eg / egr1 + TWOPI**2 * tn**2 / eg / egr1)
            enum = ggredep * eg
            denom = (egam2 - egr2) ** 2 + egam2 * ggredep * ggr1
            out = out + torch.where(pos, k * sgr1 * ggr1 * enum / denom, torch.zeros_like(e_gamma))

    for i in (1, 2):  # pygmy / scissors resonances, fstrength.f90:377-406
        tpr1 = gp.tpr_mb[irad, l, i]
        if float(tpr1.detach()) <= 0.0:
            continue
        epr2 = gp.epr_mev[irad, l, i] ** 2
        gpr2 = gp.gpr_mev[irad, l, i] ** 2
        pos = e_gamma > 0.001
        enum = gpr2 * e_gamma ** (3 - 2 * l)
        denom = (egam2 - epr2) ** 2 + egam2 * gpr2
        out = out + torch.where(pos, k * tpr1 * enum / denom, torch.zeros_like(e_gamma))

    if gp.flagupbend:  # fstrength.f90:410-420
        upc = gp.upbend[irad, l, 1]
        upe = gp.upbend[irad, l, 2]
        upf = gp.upbend[irad, l, 3]
        if gp.strengthM1 in (8, 10) and flag_m1 and gp.zix + gp.nix >= 105:
            upf = upf * 0.0
        if flag_e1:
            e = _min20(efs_mev) + S
            if isinstance(efs_mev, Tensor) and e.numel() > 1:
                out = out + torch.where(e > 1.0, upc * e / (1.0 + torch.exp(e_gamma - upe)), 0.0)
            elif float(e.detach()) > 1.0:
                out = out + upc * e / (1.0 + torch.exp(e_gamma - upe))
        if irad == 0:
            out = out + upc * torch.exp(-upe * e_gamma) * torch.exp(
                -upf * torch.abs(_scalar(gp.beta2))
            )
    return out


def fstrength(
    Zcomp: int,
    Ncomp: int,
    e_fs_mev: float,
    e_gamma_mev: Tensor,
    irad: int,
    l: int,  # noqa: E741 -- TALYS argument name (fstrength.f90:1)
    gp: GammaParameters,
    options: Options | None = None,
    e_inc_mev: float | None = None,
) -> Tensor:
    """f_XL(E_gamma) [MeV^-3] as fstrength.f90; compare psfZZZAAA.E1/M1 (see the psf trap in
    tests/hf/test_gamma.py: the E2/M2 files carry the l = 1 strength).

    TALYS: fstrength.f90:1 (fstrength)
    Test: A-psf
    """
    if (Zcomp, Ncomp) != (gp.zix, gp.nix):
        raise ValueError(f"gp is for (Zix, Nix) = ({gp.zix}, {gp.nix}), not ({Zcomp}, {Ncomp})")
    return fstrength_gp(gp, e_fs_mev, e_gamma_mev, irad, l, e_inc_mev)
