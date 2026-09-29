"""Matching of the constant-temperature and Fermi-gas regions (T, E0, Ematch), matching to discrete
levels (Nlow, Ntop), the effective a on fission barriers, and the cumulative level count.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T6 (physics/hf/CONTRACT.md §7). Acceptance test: A-ld (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    densitymatch.f90:1 (densitymatch)
    matching.f90:1 (matching)
    match.f90:1 (match)
    aldmatch.f90:1 (aldmatch)
    densitycum.f90:1 (densitycum)

What flows through the matching energy (contract §4.4)
------------------------------------------------------
TALYS finds Exmatch by bracketing (zbrak) and bisecting (rtbis) the condition that the
constant-temperature formula reproduce the discrete levels Nlow..Ntop, then takes T and E0 from
the Fermi-gas log-density table at that point. Root finding and table indices are hard branches:
the port evaluates the Fermi-gas tables (`logrho`, `temprho`) with autograd enabled, so T and E0
carry gradients with respect to a, the shell correction, pairing and the spin cutoff *at fixed
Exmatch* (the bisection result is a leaf, as in any implicit root the Fortran does not
differentiate). A gradient of Exmatch itself is not provided.

The degenerate matching window (Nlow == Ntop), and why the port does not chase TALYS's root
-------------------------------------------------------------------------------------------
When ``Nlow == Ntop`` the constant-temperature model has no window of discrete levels to match
against: ``EL == EP`` and the matching condition of match.f90 is identically zero, so *every*
energy in zbrak's bracket is a root. TALYS does not see zero. It writes

    factor2 = exp(dble(EP / temp))
    if (EL /= 0.) factor2 = factor2 - exp(EL / temp)

-- the first ``exp`` is double precision, the second single, so ``factor2`` is the float32
rounding error of ``exp`` rather than 0. It is of order 1e-7 relative, it changes sign on a
scale of ~1e-7 MeV, and zbrak duly brackets it and returns a root of TALYS's own rounding:
Exmatch = 1.871067 MeV for Nb-91, 1.386450 for Ta-179, 0.4469783 for Ir-188.

That number is noise, but it is not harmless: the port used to return "no root" here and fall
back to the empirical temperature, which puts Exmatch a factor of 2-19 higher (Nb-91 8.4992,
Ta-179 4.3851, Ir-188 3.5545) and moves the residual's level density right where its continuum
opens. It is worth 60 of CHART1's cells and up to `r` = 0.94 on `(n,g)` and `(n,n')`
(docs/results/hf-open2.md section 1).

So the port returns a root -- a *definite* one. ``matching`` hands back ``x1 + dx``, the first
point of zbrak's own scan (``dx = (x2 - x1) / 100``), computed in float32 as zbrak computes it.
The justification is measured, not asserted:

* Every energy in the bracket solves the condition, so any of them is as much "the root" as
  TALYS's is. TALYS's three values all land in zbrak's *second* segment, i.e. within one `dx`
  of what the port returns.
* For Ir-188 and Nb-91 the observables do not depend on the choice at all. Forcing Exmatch
  anywhere from ``x1`` up to the top of the discrete level scheme (1.7538 and 2.8819 MeV) gives
  the same cross sections to 1.5e-4: below that energy the constant-temperature branch is never
  evaluated, because the discrete levels are. Both nuclides' cells land at max `r` 2.3e-5 and
  1.5e-4.
* Ta-179 is the one case where it does matter, because TALYS's root (1.3864) sits *above* its
  last discrete level (0.9379) and the CTM is live in between. ``x1 + dx`` = 1.2961 leaves four
  cells at 1.1e-3 to 2.6e-3 instead of 25 cells at up to 0.79.

The alternative -- emulating match.f90's mixed ``dble``/``sgl`` exponentials to land on TALYS's
own root -- was costed and rejected. It does not stop at ``expf``: ``temp`` comes from a float32
``temprho`` built by *subtracting two nearly equal float32 logs*, so reproducing the sign of the
residue needs ignatyuk, colenhance, fermi and spincut reimplemented operation by operation in
single precision. Rounding the port's float64 logs to float32 is not enough on its own: those
routines' own single-precision arithmetic moves ``logrholoc`` by ~1e-7 against a float32 quantum
of ~2e-6 there, so a few per cent of table entries land on the neighbouring float32 value, and
one wrong entry anywhere below the root loses the bracket -- let alone the 40 consecutive sign
decisions rtbis needs. It would also make Exmatch a chaotic function of the level-density
parameters -- fatal to DIFFPARAM's gradients -- and tie the answer to the libm of whatever
built TALYS.
Contract section 4.1 calls this out ("differences larger than the section 6 tolerances are port
bugs until TALYS's own rounding is shown to be the cause"); it is shown here rather than
assumed, and the residue left behind is the four Ta-179 cells above.

Single-precision details that decide integer indices are reproduced: ``i = int(Exm/dEx)`` with
dEx = 0.1 is evaluated in float32, as TALYS evaluates it, so a matching energy that lands on a
0.1 MeV boundary picks the same table interval.
"""

from __future__ import annotations

import math
from dataclasses import replace
from pathlib import Path

import numpy as np
import torch
from torch import Tensor

from physics.hf.core.constants import talys_constants
from physics.hf.core.numerics import locate, pol1, rtbis, zbrak
from physics.hf.core.tensors import DTYPE
from physics.hf.density.parameters import (
    NUMLEV2,
    SENTINEL,
    LDNucleus,
    _fv,
    _t,
    colenhance,
    ignatyuk,
    spincut,
    spindis,
)
from physics.hf.structure.files import talys_structure_dir

__all__ = ["densitymatch", "match_ctm", "matching", "match", "aldmatch", "densitycum"]

_DEX = np.float32(0.1)


def _idx(x) -> int:
    """int(x / dEx) in single precision (densitymatch.f90, match.f90)."""
    return int(np.float32(_fv(x)) / _DEX)


_NUMMATCHT = 4000  # A0_talys_mod.f90:56, `nummatchT`: TALYS dimensions logrho/temprho to this, zero-filled


def _pad_match_table(x: Tensor) -> Tensor:
    """Zero-pad a matching table to TALYS's fixed length (indices 0..nummatchT).

    TALYS declares `logrho(nummatchT)` and `temprho(nummatchT)` and zeroes all of them
    (densitymatch.f90:134-137) before filling 1..nEx, so a matching energy above the grid end
    (light nuclei: Exmemp = 2.67 + 253/A + P is ~25 MeV at A = 11) reads 0. The port sized the
    tables to nEx + 2 and raised IndexError there (chart run 2026-09-20: 35 targets, Z 8-11).
    Values inside 0..nEx+1 are untouched, so every nuclide that ran before is bit-identical.
    """
    n = _NUMMATCHT + 1 - int(x.shape[0])
    if n <= 0:
        return x
    return torch.cat([x, torch.zeros(n, dtype=x.dtype)])


def _fermi_tables(ld: LDNucleus, ibar: int) -> tuple[Tensor, Tensor, int, int]:
    """`_fermi_tables_core`, with both tables zero-padded to TALYS's fixed length."""
    logrho, temprho, Nstart, nEx = _fermi_tables_core(ld, ibar)
    return _pad_match_table(logrho), _pad_match_table(temprho), Nstart, nEx


def _fermi_tables_core(ld: LDNucleus, ibar: int) -> tuple[Tensor, Tensor, int, int]:
    """logrho(i), temprho(i) for i = 0..nEx+1 on the 0.1 MeV grid, Nstart and nEx
    (densitymatch.f90:118-160)."""
    from physics.hf.density.models import fermi

    A = ld.A
    P = ld.pair_mev
    Exend = 20.0 + 300.0 / A
    nEx = int(np.float32(Exend) / _DEX)
    dEx = _fv(_DEX)
    from physics.hf.density.ld_nx2 import fermi_tables as _nx2_tables

    got = _nx2_tables(ld, ibar, nEx, dEx)  # NX2 ld: the whole table in C, off the graph
    if got is not None:
        return got[0], got[1], got[2], nEx
    i = torch.arange(1, nEx + 1, dtype=DTYPE)
    cols = []
    for j in (-1, 0, 1):
        eex = dEx * (i + 0.5 * j)
        U = eex - P
        ald = ignatyuk(ld, eex, ibar)
        _, _, Kcoll = colenhance(ld, eex, ald, ibar)
        val = torch.log(Kcoll * fermi(ld, ald, eex, P, ibar))
        cols.append(torch.where(U > 0.0, val, torch.zeros_like(val)))
    lm, l0, lp = cols
    logrho = torch.zeros(nEx + 2, dtype=DTYPE)
    logrho[1 : nEx + 1] = l0
    raw = torch.where(lp != lm, dEx / torch.where(lp != lm, lp - lm, torch.ones_like(lp)), 0.0)
    if not raw.requires_grad:  # SETB: the same fill and search on Python floats
        from physics.hf.density.matching_fast import temprho_fill

        temprho, Nstart = temprho_fill(raw, nEx)
        return logrho, temprho, Nstart, nEx
    temprho = [None] * (nEx + 2)
    temprho[nEx + 1] = _t(0.0)
    for k in range(nEx, 0, -1):  # descending fill: a non-positive or <= 0.1 value takes i+1
        v = raw[k - 1]
        temprho[k] = temprho[k + 1] if _fv(v) <= 0.1 else v
    temprho[0] = _t(0.0)
    temprho = torch.stack(temprho)
    Nstart = 1
    for k in range(nEx, 0, -1):
        if k < nEx and _fv(temprho[k]) >= _fv(temprho[k + 1]):
            Nstart = k + 1
            break
    return logrho, temprho, Nstart, nEx


def match(
    ld: LDNucleus, eex_mev: Tensor, logrho: Tensor, temprho: Tensor, E0save: float, ibar: int = 0
) -> Tensor:
    """Matching condition, batched over eex: with E0 free, the CTM count of levels between Nlow and
    Ntop minus (Ntop - Nlow); with E0 given, Eex - T log(T rho) - E0. 0 where T <= 0.

    TALYS: match.f90:1 (match)
    Test: A-ld
    """
    eex = _t(eex_mev)
    flat = eex.reshape(-1)
    NLo, NP = ld.Nlow[ibar], ld.Ntop[ibar]
    EL, EP = _level_window(ld, ibar)
    if not (eex.requires_grad or logrho.requires_grad or temprho.requires_grad):
        # SETB: every energy at once, bit-identical (density/matching_fast.py)
        from physics.hf.density.matching_fast import match_vec

        return match_vec(eex, logrho, temprho, E0save, NLo, NP, EL, EP, SENTINEL)
    dEx = _fv(_DEX)
    out = []
    for x in flat:
        i = max(_idx(x), 1)
        temp = pol1(_t(i * dEx), _t((i + 1) * dEx), temprho[i], temprho[i + 1], x)
        if _fv(temp) > 0.0:
            logrhof = pol1(_t(i * dEx), _t((i + 1) * dEx), logrho[i], logrho[i + 1], x)
            rhof = torch.exp(logrhof)
            if E0save == SENTINEL:
                factor1 = torch.exp(-x / temp)
                factor2 = torch.exp(EP / temp)
                if EL != 0.0:
                    factor2 = factor2 - torch.exp(EL / temp)
                term = torch.clamp(temp * rhof * factor1 * factor2, max=1.0e30)
                out.append(term + NLo - NP)
            else:
                out.append(x - temp * torch.log(temp * rhof) - E0save)
        else:
            out.append(_t(0.0))
    return torch.stack(out).reshape(eex.shape)


def _level_window(ld: LDNucleus, ibar: int) -> tuple[float, float]:
    """(EL, EP), the matching window's level energies [MeV] (densitymatch.f90:110-118)."""
    NLo, NP = ld.Nlow[ibar], ld.Ntop[ibar]
    if ibar == 0:
        return _fv(ld.edis_mev[NLo]), _fv(ld.edis_mev[NP])
    ef = ld.barriers.efistrrot_mev[ibar]
    return _fv(ef[NLo]), _fv(ef[NP])


def degenerate_window(ld: LDNucleus, ibar: int = 0) -> bool:
    """True when the CTM has no window of discrete levels to match against.

    `Nlow == Ntop` with a non-zero level energy makes `match.f90`'s `factor2` analytically zero,
    so the matching condition vanishes identically and every energy in the bracket is a root.
    `Ntop == Nlow == 0` is NOT this case: match.f90:57 guards `if (EL /= 0.)`, so `factor2` is 1
    and the condition is a real function (Eu-148 is the example).

    TALYS: match.f90:56-58
    Test: tests/hf/test_density.py::test_nb91_degenerate_matching_window
    """
    if int(ld.Nlow[ibar]) != int(ld.Ntop[ibar]):
        return False
    EL, EP = _level_window(ld, ibar)
    return EL != 0.0 and EL == EP


#: `rtbis`'s tolerance in matching.f90:96. TALYS's own value, and the default everywhere.
_XACC = 1.0e-4
#: zbrak's segment count in matching.f90:95.
_NSEG = 100


def matching(
    ld: LDNucleus, logrho: Tensor, temprho: Tensor, Exmemp: float, E0save: float, ibar: int = 0,
    xacc: float = _XACC,
) -> float:
    """Matching energy [MeV] between the CTM and the Fermi gas, 0 when no root: zbrak on
    [2.25/a + pair + 0.11, 19 + 300/A] in 100 steps, rtbis to `xacc` (TALYS's 1e-4), and of two
    roots the one nearer the empirical Exmemp.

    With a degenerate level window (`degenerate_window`) the condition is identically zero and
    every energy in the bracket is a root; the first point of zbrak's scan comes back instead of
    0. That value is a leaf: g == 0 there, so there is no implicit derivative to take and
    `_exmatch_implicit` hands back a plain constant. See the module docstring.

    `xacc` is TALYS's own 1e-4 MeV unless a caller asks otherwise, and the only caller that does
    is the DIFFPARAM gradient gate. The reason is worth stating: a bisection stopped at 1e-4 MeV
    makes Exmatch, and therefore every cross section below it, a **staircase** in the
    level-density parameters, with steps of order 1e-4 MeV. That is invisible to a cross section
    and fatal to a central finite difference -- d Exmatch/d Pshift measured across h = 1e-4 came
    out as -0.54, -0.16 and -0.13 MeV at three neighbouring step sizes, all of them the
    staircase rather than the slope. The analytic gradient describes the exact root, so the gate
    refines the root and says so; nothing that reproduces TALYS uses anything but 1e-4.

    TALYS: matching.f90:1 (matching)
    Test: A-ld / G0.4
    """
    A = ld.A
    ald = _fv(ignatyuk(ld, _t(Exmemp), ibar))
    x1 = _fv(np.float32(max(2.25 / ald + _fv(ld.pair_mev), 0.0) + 0.11))
    x2 = _fv(np.float32(19.0 + 300.0 / A))

    dx = _fv(np.float32((np.float32(x2) - np.float32(x1)) / np.float32(_NSEG)))

    # A degenerate window has no root to find and no root to miss: the condition is identically
    # zero, so zbrak on it can only report TALYS's own float32 rounding (module docstring).
    # Return the first point of zbrak's scan -- a definite energy, one `dx` from where all three
    # of TALYS's noise roots landed -- rather than 0, which sends densitymatch.f90:227 to the
    # empirical temperature and moves the residual's level density by a factor of 2 to 19.
    if E0save == SENTINEL and degenerate_window(ld, ibar):
        return _fv(np.float32(np.float32(x1) + np.float32(dx)))

    from physics.hf.density.ld_nx2 import match_roots

    EL, EP = _level_window(ld, ibar)
    # NX2 ld: zbrak's scan and rtbis's bisection on floats in C (None: the torch loop below)
    roots = match_roots(logrho, temprho, x1, x2, _NSEG, E0save, ld.Nlow[ibar], ld.Ntop[ibar],
                        EL, EP, SENTINEL, xacc)
    if roots is None:
        def f(x):
            return match(ld, x, logrho, temprho, E0save, ibar).detach()

        xb1, xb2 = zbrak(f, x1, x2, _NSEG, 2)
        roots = [_fv(rtbis(f, xb1[k], xb2[k], xacc)) for k in range(int(xb1.numel()))]
    nb = len(roots)
    if nb == 0:
        return 0.0
    if nb == 1:
        Exm = roots[0]
    else:
        Exm = roots[1] if abs(roots[0] - Exmemp) > abs(roots[1] - Exmemp) else roots[0]
    if Exm < x1 or Exm > x2:
        Exm = 0.0
    return Exm


def _ctm_light(Z: int, A: int) -> dict[str, float]:
    p = talys_structure_dir() / "density" / "ground" / "ctm" / "ctm.light"
    out: dict[str, float] = {}
    if not Path(p).is_file():
        return out
    for line in Path(p).read_text(encoding="latin-1").splitlines():
        parts = line.split()
        if len(parts) >= 4 and int(parts[1]) == Z and int(parts[2]) == A:
            out[parts[0]] = _fv(np.float32(_fv(parts[3])))
    return out


def _exmatch_implicit(
    ld: LDNucleus, Exm: float, logrho: Tensor, temprho: Tensor, E0save: float, ibar: int
) -> Tensor:
    """`Exm` as a tensor whose gradient is the implicit derivative of the matching root.

    `matching` finds Exmatch by bisecting `match(E, theta) = 0`; the bisection itself is a hard
    branch and `rtbis` returns a leaf. That made **every** level-density parameter's gradient
    wrong, not just imprecise: on Fe-57 the autograd d(sum log10 xs)/d(aadjust) was 2.27 against
    a central finite difference of 0.97, and the whole 1.3 was the missing dExmatch/dtheta
    (Exmatch = 11.84 MeV there and moves at -16.5 MeV per unit aadjust).

    The fix is the implicit function theorem, not a differentiable bisection. At the root
    g(E*, theta) = 0, so dE*/dtheta = -(dg/dtheta) / (dg/dE), and one Newton step written as a
    straight-through correction

        E = E* - (g - g.detach()) / (dg/dE)

    has E* as its forward value **to the bit** and that derivative as its gradient. dg/dE is
    taken by autograd on a fresh local leaf, so the E-derivative of the interpolation is exact
    inside the 0.1 MeV table interval the root lands in and nothing of it escapes into theta.

    Returns a plain constant tensor when nothing upstream carries a gradient.

    TALYS: matching.f90:1 (matching), rtbis.f90:1 (rtbis)
    Test: A-ld / G0.4
    """
    if not (logrho.requires_grad or temprho.requires_grad):
        return _t(Exm)  # NX2 ld: `g` below reads theta only through the two tables
    g = match(ld, _t(Exm), logrho, temprho, E0save, ibar)  # E constant: this is dg/dtheta only
    if not g.requires_grad:
        return _t(Exm)  # nothing upstream carries a gradient; stay a plain constant
    with torch.enable_grad():
        E = torch.tensor(float(Exm), dtype=DTYPE, requires_grad=True)
        (dg_dE,) = torch.autograd.grad(
            match(ld, E, logrho, temprho, E0save, ibar), E, allow_unused=True)
    if dg_dE is None or float(dg_dE) == 0.0 or not np.isfinite(float(dg_dE)):
        return _t(Exm)  # a flat or undefined condition: no implicit derivative to take
    return _t(Exm) - (g - g.detach()) / float(dg_dE)


def _straight_through(value: float, t: Tensor) -> Tensor:
    """`value` (TALYS's own float32-rounded number) carrying the gradient of `t`.

    Used for the empirical Tmemp / Exmatch fallbacks, whose formulas TALYS evaluates in single
    precision: the rounding derivative is 1 almost everywhere, so the forward stays exactly the
    number densitymatch.f90 produces while d/d(pair), d/d(gammald), d/d(deltaW) reach it.
    """
    return _t(value) + (t - t.detach())


def densitymatch(ld: LDNucleus, flagldglobal: bool = False, flagctmglob: bool = False,
                 xacc: float = _XACC) -> LDNucleus:
    """`ld` with T [MeV], E0 [MeV] and Exmatch [MeV] resolved for every barrier as
    densitymatch.f90 (CTM models only: skipped for ldmodel 2, 3 and for tabulated barriers),
    including the Tadjust/E0adjust second passes and the empirical fallbacks.

    TALYS: densitymatch.f90:1 (densitymatch)
    Test: A-ld
    """
    from physics.hf.density.ld_ceng import densitymatch_fast

    got = densitymatch_fast(ld, flagldglobal, flagctmglob, xacc)  # CENGLD: barrier 0 in one C call
    if got is not None:
        return got
    Ts, E0s, Exs = [], [], []
    A = ld.A
    P = _fv(ld.pair_mev)
    dEx = _fv(_DEX)
    for ib in range(ld.nfisbar + 1):
        T_in, E0_in, Ex_in = ld.T_mev[ib], ld.E0_mev[ib], ld.Exmatch_mev[ib]
        if ld.ldmodel in (2, 3) or ld.has_table(ib):
            Ts.append(T_in)
            E0s.append(E0_in)
            Exs.append(Ex_in)
            continue
        logrho, temprho, Nstart, nEx = _fermi_tables(ld, ib)
        T_cur, E0_cur, Ex_cur = T_in, E0_in, Ex_in
        if A <= 18:  # densitymatch.f90:167-183
            light = _ctm_light(ld.Z, A)
            if "T" in light and ib == 0:
                T_cur = _t(light["T"])
            if "E0" in light and ib == 0:
                E0_cur = _t(light["E0"])
            if "Exmatch" in light and ib == 0:
                Ex_cur = _t(light["Exmatch"])
        gdw_t = ld.gammald * ld.deltaW_mev[0]
        gdw = _fv(gdw_t)
        c0, c1, c2 = (-0.22, 9.4, 2.67) if ld.flagcol else (-0.25, 10.2, 2.33)
        Tmemp = c0 + c1 / np.sqrt(max(A * (1.0 + gdw), 1.0))
        Exmemp = c2 + 253.0 / A + P
        # DIFFPARAM: the same two numbers as tensors. TALYS forms them in single precision and
        # clamps at 0.1, so the forward value stays exactly `_fv(np.float32(max(., 0.1)))` and
        # only the derivative (1 a.e. through the clamp and the rounding) is attached.
        Tmemp_t = _straight_through(
            _fv(np.float32(max(Tmemp, 0.1))),
            c0 + c1 / torch.sqrt(torch.clamp(A * (1.0 + gdw_t), min=1.0))
            if Tmemp > 0.1 else _t(0.1))
        Exmemp_t = _straight_through(
            _fv(np.float32(max(Exmemp, 0.1))),
            c2 + 253.0 / A + ld.pair_mev if Exmemp > 0.1 else _t(0.1))
        Tmemp = _fv(Tmemp_t)
        Exmemp = _fv(Exmemp_t)

        def lower_limit(Exm):
            ald = _fv(ignatyuk(ld, _t(Exm), ib))
            return max(2.25 / ald + P, 0.0) + 0.11

        def t_from_ex(Exm):
            i = _idx(Exm)  # the table index is a branch: taken on the detached value
            return pol1(_t(i * dEx), _t((i + 1) * dEx), temprho[i], temprho[i + 1], _t(Exm))

        def ex_from_t(Tm, ib_=Nstart):
            # `temprho` is declared 1-based (A0_talys_mod.f90:1251, `dimension(nummatchT)`) but
            # locate.f90's dummy argument is `xx(0:ie)`, so inside locate xx(k) aliases
            # temprho(k+1) and the index that comes back is one BELOW the interval that
            # brackets Tm; the pol1 on the next line then extrapolates from the interval below
            # instead of interpolating. Passing `temprho[1:]` reproduces that aliasing exactly.
            # This is TALYS's own off-by-one and the port keeps it (contract §1: faithful
            # first). Measured on Y-89 in a Zr-90 run: with the shift Exmatch = 3.2044 MeV,
            # TALYS's own value; without it 2.9624, and rho(J) then misses by up to 35%.
            # It bites only the three locate(temprho, ...) calls of densitymatch.f90
            # (:222, :230, :246) -- `edens` is declared 0:numdens, so the tabulated-density
            # lookups in density/models.py are unaffected.
            i = int(locate(temprho[1:], _t(_fv(Tm)), ib_, nEx - 1))
            # DIFFPARAM: the *index* comes from the detached value (locate is a branch), the
            # interpolated value from the tensors, so Exmatch carries d/d(level-density
            # parameter) through `temprho` and through Tm. Bit-identical forward.
            return i, (
                pol1(temprho[i], temprho[i + 1], _t(i * dEx), _t((i + 1) * dEx), _t(Tm))
                if i > 0
                else None
            )

        # DIFFPARAM: every branch below is still decided on the FLOAT `Exm`, exactly as before;
        # `Exm_t` carries the same number as a tensor so that the two places the value enters a
        # *formula* -- `t_from_ex` and the E0 expression -- see the gradient. Keeping the two
        # side by side is what makes the change provably forward-identical.
        for _pass in range(3):
            Tm = T_cur
            Exm_t = ld.Exmatchadjust[ib] * _t(Ex_cur)
            Exm = _fv(Exm_t)
            E0m = E0_cur
            E0save = _fv(E0m)
            if flagldglobal:
                Tm = Tmemp_t
                Exm, Exm_t = Exmemp, Exmemp_t
            if _fv(Tm) == 0.0 and Exm == 0.0:
                if ld.ldparexist and not flagctmglob:
                    Exm = matching(ld, logrho, temprho, Exmemp, E0save, ib, xacc)
                    Exm_t = _exmatch_implicit(ld, Exm, logrho, temprho, E0save, ib)
                    if Exm > 0.0:
                        Tm = t_from_ex(Exm_t)
                    else:
                        Tm = Tmemp_t
                        i, e = ex_from_t(Tm)
                        if 0 < i <= nEx - 1 and e is not None:
                            Exm, Exm_t = _fv(e), e
                else:
                    Tm = Tmemp_t
                    i, e = ex_from_t(Tm)
                    if i > 0 and e is not None:
                        Exm, Exm_t = _fv(e), e
                if Exm <= lower_limit(Exm):
                    Exm, Exm_t = 0.0, _t(0.0)
                if Exm > 3.0 * Exmemp:
                    Exm, Exm_t = 0.0, _t(0.0)
            if Exm == 0.0:
                if _fv(Tm) == 0.0:
                    Tm = Tmemp_t
                i, e = ex_from_t(Tm)
                if i > 0 and e is not None:
                    Exm, Exm_t = _fv(e), e
                if Exm <= lower_limit(Exm):
                    Exm, Exm_t = Exmemp, Exmemp_t
                if Exm == 0.0:
                    Exm, Exm_t = Exmemp, Exmemp_t
                if Exm > 3.0 * Exmemp:
                    Exm, Exm_t = Exmemp, Exmemp_t
            if _fv(Tm) == 0.0:
                if Exm <= lower_limit(Exm):
                    Exm, Exm_t = Exmemp, Exmemp_t
                if Exm > 3.0 * Exmemp:
                    Exm, Exm_t = Exmemp, Exmemp_t
                if _idx(Exm) > 0:
                    Tm = t_from_ex(Exm_t)
            if _fv(E0m) == SENTINEL:
                i = _idx(Exm)
                if i > 0:
                    logrhomatch = pol1(
                        _t(i * dEx), _t((i + 1) * dEx), logrho[i], logrho[i + 1], Exm_t
                    )
                    rhomatch = torch.exp(logrhomatch)
                    E0m = Exm_t - Tm * torch.log(Tm * rhomatch)
            if _fv(Tm) == 0.0:
                Tm = Tmemp_t
            if _fv(T_cur) == 0.0 and _fv(ld.Tadjust[ib]) != 1.0:
                T_cur = ld.Tadjust[ib] * Tm
                continue
            T_cur = _t(Tm)
            if _fv(E0_cur) == SENTINEL and _fv(ld.E0adjust[ib]) != 1.0:
                E0_cur = ld.E0adjust[ib] * E0m
                continue
            E0_cur = _t(E0m)
            Ex_cur = Exm_t
            break
        Ts.append(_t(T_cur))
        E0s.append(_t(E0_cur))
        Exs.append(_t(Ex_cur))
    return replace(
        ld,
        T_mev=torch.stack(Ts),
        E0_mev=torch.stack(E0s),
        Exmatch_mev=torch.stack(Exs),
        matched=True,
    )


def match_ctm(ld: LDNucleus, levels=None, options=None) -> dict[str, Tensor]:
    """Temperature [MeV], E0 [MeV], matching energy [MeV] (ld*.gs header) as densitymatch.f90.
    `levels` and `options` are accepted for the contract signature; `ld` already carries them.

    TALYS: densitymatch.f90:1 (densitymatch), matching.f90:1 (matching)
    Test: A-ld
    """
    m = densitymatch(
        ld,
        flagldglobal=bool(getattr(options, "flagldglobal", False)),
        flagctmglob=bool(getattr(options, "flagctmglob", False)),
    )
    return {"T_mev": m.T_mev, "E0_mev": m.E0_mev, "Exmatch_mev": m.Exmatch_mev}


def aldmatch(ld: LDNucleus, eex_mev: float, ibar: int) -> Tensor:
    """Effective level density parameter [MeV^-1] on a barrier: the a for which a Fermi gas without
    collective enhancement reproduces the enhanced density at Eex (bisection, 40 steps, 0.001).

    TALYS: aldmatch.f90:1 (aldmatch)
    Test: A-ld
    """
    from physics.hf.density.models import fermi

    sqrttwopi = talys_constants()["sqrttwopi"]
    eex = _t(eex_mev)
    A = ld.A
    rj = 0.5 * (A % 2) - 1.0
    rhosum = _t(0.0)
    aldref = ignatyuk(ld, eex, ibar)
    while True:
        rj += 1.0
        sc = spincut(ld, aldref, eex, ibar)
        factor = (2.0 * rj + 1.0) * fermi(ld, aldref, eex, ld.pair_mev, ibar) * spindis(sc, _t(rj))
        rhosum = rhosum + factor
        if _fv(factor) < 0.00001:
            break
    _, _, Kcoll = colenhance(ld, eex, aldref, ibar)
    rhoref = Kcoll * rhosum

    def diff(a):
        sigma = torch.sqrt(spincut(ld, a, eex, ibar))
        return fermi(ld, a, eex, ld.pair_mev, ibar) * sigma * sqrttwopi - rhoref

    ald1, ald2 = 0.5 * aldref, 2.0 * aldref
    if _fv(diff(ald1)) < 0.0:
        out, dald = ald1, ald2 - ald1
    else:
        out, dald = ald2, ald1 - ald2
    for _ in range(40):
        dald = dald * 0.5
        mid = out + dald
        fmid = diff(mid)
        if _fv(fmid) <= 0.0:
            out = mid
        if abs(_fv(dald)) < 0.001 or _fv(fmid) == 0.0:
            break
    return out


def densitycum(ld: LDNucleus) -> dict[str, Tensor]:
    """The discrete-level bookkeeping of densitycum.f90 for ibar 0: the cumulative number of
    levels Ncum(i) integrated from the total level density at the level midpoints (with
    Ncum(Nlow) = Nlow by definition), the experimental level density rhoexp(i) from a 10-level
    window, and the four goodness-of-fit numbers TALYS prints in the ld*.gs header -- Chi-2,
    Frms, Erms and the average deviation per level, all over Nlow <= i <= Ntop.

    TALYS: densitycum.f90:1 (densitycum)
    Test: A-ld
    """
    from physics.hf.density.models import densitytot

    n = ld.nlevmax2
    edis = ld.edis_mev
    NL, NT = ld.Nlow[0], ld.Ntop[0]
    ncum = [_t(0.0)] * (n + 1)
    mids = 0.5 * (edis[1 : n + 1] + edis[0:n])
    dexs = edis[1 : n + 1] - edis[0:n]
    dens = densitytot(ld, mids, 0)
    for i in range(1, n + 1):
        if _fv(edis[i]) == 0.0:  # densitycum.f90:140 cycles: Ncum stays at its initialised zero
            continue
        ncum[i] = ncum[i - 1] + dens[i - 1] * dexs[i - 1]
        if i == NL:
            ncum[i] = _t(float(NL))
    rhoexp = torch.zeros(n + 1, dtype=DTYPE)
    chi2 = frms_sum = erms_sum = avdev = _t(0.0)
    for i in range(1, n + 1):  # densitycum.f90:200-215
        ibeg, iend = max(i - 5, 0), min(i + 5, n)
        nav = iend - ibeg + 1
        erange = _fv(edis[iend] - edis[ibeg])
        if erange > 0.0:
            rhoexp[i] = nav / erange
        if NL <= i <= NT:
            chi2 = chi2 + (ncum[i] - i) ** 2 / math.sqrt(i) / max(NT - NL, 1)
            R = ncum[i] / i
            frms_sum = frms_sum + torch.log(R) ** 2
            erms_sum = erms_sum + torch.log(R)
            avdev = avdev + (ncum[i] - i).abs()
    denom = float(NT - NL)
    zero = _t(0.0)
    return {
        "Ncum": torch.stack(ncum),
        "rhoexp": rhoexp,
        "chi2lev": chi2,
        "Frmslev": torch.exp(torch.sqrt(frms_sum / denom)) if denom > 0.0 else zero,
        "Ermslev": torch.exp(erms_sum / denom) if denom > 0.0 else zero,
        "avdevlev": avdev / denom if denom > 0.0 else zero,
    }
