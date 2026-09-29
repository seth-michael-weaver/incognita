"""Pre-equilibrium spectra folded onto the excitation-energy grids of the residual nuclei, so that
the residuals can decay further.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T9, continued by EXCL (physics/hf/CONTRACT.md §7). Acceptance test: A-cn1 / E2E (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    population.f90:1 (population)

What it does, and why the E2E gate needs it. `preeq` computes its spectra on the *emission*
energy grid `egrid(nen)`; `binary.f90` and `multiple.f90` need them on each residual's
*excitation* grid `Ex(Zix, Nix, nexout)`. `population` bridges the two: for every continuum bin of
every binary residual it integrates the pre-equilibrium (plus, with `flaggiant`, the giant
resonance) spectrum over the bin, by evaluating the spectrum at the bin's bottom and top with
`pol1` and trapezoidally averaging (population.f90:156-166) -- then renormalises the whole column
so the summed population equals `xspreeqtot + xsgrtot` exactly, because the interpolation does not
conserve flux (population.f90:246-268).

Three branches are reproduced but dormant at TALYS's defaults for an incident neutron, and each
is guarded by the flag that switches it on rather than dropped:

* `preeqpop(Zix, Nix, nexout, J, parity)`, the (J, parity)-resolved population, needs
  `pespinmodel >= 3`; `input_preeqmodel.f90:76-80` gives `pespinmodel = 1` for `k0 <= 1`, so an
  incident-neutron run never fills it. Pass `xspreeqjp`/`xscollcontjp`/`xsgrstate` to get it.
* `xspopph`/`xspopph2`, the particle-hole populations multiple pre-equilibrium decays, need
  `mulpreZN`, which `population` itself sets for neutrons and protons when `flagmulpre`. That flag
  is `not (Einc < emulpre)` with `emulpre = 20 MeV` (input_preeqmodel.f90:83), so of the 23
  reference energies only the last, 20.0 MeV exactly, turns it on.
* the `flaggiant` addend, which *is* live for `k0 in (1, 2)` (input_directmodel.f90:93-98) and is
  the reason this module takes `xsgr`/`xsgrtot` at all.

Units: every cross section in and out is mb, every energy MeV. Float64 throughout, with the one
`real(sgl)` truncation TALYS's `1.e-30` cut implies kept as a plain comparison.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from physics.hf.compound import pop_nx2
from physics.hf.core.grids import locate_scalar
from physics.hf.core.tensors import DTYPE  # noqa: F401  (documents the dtype contract)

XS_MIN_MB = 1.0e-30  # population.f90:168 "if (xs < 1.e-30) xs = 0."


@dataclass(frozen=True)
class PopResidual:
    """One binary residual's excitation grid, as `exgrid` left it."""

    type: int
    nlast: int  # Nlast(Zix, Nix, 0)
    maxex: int  # maxex(Zix, Nix)
    sep_mev: float  # S(0, 0, type)
    ex_mev: np.ndarray  # (maxex+1,) Ex(Zix, Nix, nex)
    dex_mev: np.ndarray  # (maxex+1,) deltaEx


@dataclass(frozen=True)
class PopulationInputs:
    """Everything `population` reads, per incident energy."""

    etotal_mev: float  # Etotal, the compound system's total energy
    egrid_mev: np.ndarray  # (maxen+1,) Fortran indexing, egrid[0] = 0
    ebegin: dict[int, int]  # type -> ebegin(type)
    eend: dict[int, int]  # type -> eend(type)
    residuals: dict[int, PopResidual]  # type -> grid
    xspreeq_mb: dict[int, np.ndarray]  # type -> (maxen+1,) xspreeq(type, nen)
    xspreeqtot_mb: dict[int, float]  # type -> xspreeqtot(type)
    flaggiant: bool = False
    xsgr_mb: dict[int, np.ndarray] = field(default_factory=dict)  # type -> (maxen+1,)
    xsgrtot_mb: dict[int, float] = field(default_factory=dict)
    # pespinmodel >= 3 only
    pespinmodel: int = 1
    maxjph: int = 0
    xspreeqjp_mb: dict[int, np.ndarray] = field(default_factory=dict)  # (maxen+1, maxJph+1, 2)
    xscollcontjp_mb: dict[int, np.ndarray] = field(default_factory=dict)
    xsgrstate_mb: dict[int, np.ndarray] = field(default_factory=dict)  # (maxen+1, 4, 2)
    # multiple pre-equilibrium only
    flagmulpre: bool = False
    flag2comp: bool = True
    p0: int = 1
    ppi0: int = 0
    pnu0: int = 1
    maxpar: int = 6  # preeqinit.f90:64-65, maxexc / 2 = numexc / 2
    xsstep_mb: dict[int, np.ndarray] = field(default_factory=dict)  # (maxpar+1, maxen+1)
    xsstep2_mb: dict[int, np.ndarray] = field(default_factory=dict)  # (maxpar+1, maxpar+1, E)
    flagomponly: bool = False


@dataclass
class PopulationResult:
    """population.f90's outputs."""

    preeqpopex_mb: dict[int, np.ndarray]  # type -> (maxex+1,)
    xscheck_mb: dict[int, float]  # type -> the pre-normalisation sum (the POPULATION CHECK table)
    norm: dict[int, float]  # type -> the renormalisation factor actually applied
    mulpre: dict[int, bool]  # type -> mulpreZN(Zix, Nix)
    preeqpop_mb: dict[int, np.ndarray] = field(default_factory=dict)  # (maxex+1, maxJph+1, 2)
    xspopph_mb: dict[int, np.ndarray] = field(default_factory=dict)  # (maxex+1, p+1, h+1)
    xspopph2_mb: dict[int, np.ndarray] = field(default_factory=dict)


PARA = (0, 1, 1, 2, 3, 3, 4)  # parA
PARZ = (0, 0, 1, 1, 1, 2, 2)  # parZ
PARN = (0, 1, 0, 1, 2, 1, 2)  # parN


def _bin_nodes(
    egrid: np.ndarray, ib: int, ie: int, etop_mev: float, e_mev: float
) -> tuple[int, int, float, float]:
    """`locate` plus the two interpolation abscissae of one bin edge (population.f90:139-152).

    The upper node is clipped to `Etotal - S`, which is what makes the topmost bin of a residual
    interpolate over a shortened interval instead of past the end of the spectrum.

    TALYS: population.f90:1 (population)
    Test: A-cn1
    """
    nen = locate_scalar(egrid, ib, ie, e_mev)
    na = nen
    nb = nen + 1
    return na, nb, float(egrid[na]), float(min(egrid[nb], etop_mev))


def _bin_nodes_many(eg: np.ndarray, ib: int, ie: int, etop: float, emax: float, r,
                    lo: int, hi: int) -> dict | None:
    """COREX: `_bin_nodes` at both edges of bins lo..hi-1 at once, {nexout: (na1, nb1, ea1, eb1,
    na2, nb2, ea2, eb2)} with the bin edges computed as the loop computes them. `locate` is a
    bisection; on a strictly increasing egrid[ib..ie] (checked) its answer is a sorted search with
    locate's ties at ib and ie, so the values are `_bin_nodes`' own. None (use the scalar calls)
    for any other grid, or when a node would fall off the array."""
    if hi <= lo or ib > ie:
        return None
    f32 = np.float32
    xs = np.asarray(eg, dtype=f32)
    seg = xs[ib : ie + 1]
    if seg.size > 1 and not bool(np.all(seg[1:] > seg[:-1])):
        return None
    ex = np.asarray(r.ex_mev, dtype=float)[lo:hi]
    dex = np.asarray(r.dex_mev, dtype=float)[lo:hi]
    eout = emax - ex
    edges = np.stack([eout - 0.5 * dex, eout + 0.5 * dex]).astype(f32)
    jl = ib - 1 + np.searchsorted(seg, edges, side="right")
    jl = np.where(np.isnan(edges), ib - 1, jl)
    jl = np.where(edges == xs[ie], ie - 1, jl)
    na = np.where(edges == xs[ib], ib, jl)
    nb = na + 1
    if int(nb.max()) >= len(eg):
        return None
    egf = np.asarray(eg, dtype=float)
    ea = egf[na]
    ebn = egf[nb]
    eb = np.where(etop < ebn, etop, ebn)
    out = {}
    for k in range(hi - lo):
        out[lo + k] = (int(na[0, k]), int(nb[0, k]), float(ea[0, k]), float(eb[0, k]),
                       int(na[1, k]), int(nb[1, k]), float(ea[1, k]), float(eb[1, k]))
    return out


def population(inp: PopulationInputs) -> PopulationResult:
    """`preeqpopex` (and, when the flags ask for them, `preeqpop`, `xspopph`, `xspopph2`) for every
    binary residual of the initial compound nucleus.

    TALYS: population.f90:1 (population)
    Test: A-cn1 / E2E
    """
    res = PopulationResult({}, {}, {}, {})
    if inp.flagomponly:
        return res
    eg = np.asarray(inp.egrid_mev, float)
    # GLUEFINISH: the bin loop below, for every residual, in one C call per type. It fills `res`
    # with the same bits and returns True, or leaves it untouched for the body here.
    if not pop_nx2.bin_loop(inp, res, eg, PARA, PARZ, PARN):
        _bin_loop(inp, res, eg)
    return _renormalise(inp, res)


def _bin_loop(inp: PopulationInputs, res: PopulationResult, eg: np.ndarray) -> None:
    """population.f90:129-244 -- every binary residual's bins, the reference body.

    TALYS: population.f90:1 (population)
    Test: A-cn1 / E2E
    """
    for t, r in sorted(inp.residuals.items()):
        n = r.maxex + 1
        res.preeqpopex_mb[t] = np.zeros(n)
        res.mulpre[t] = False
        res.norm[t] = 1.0
        res.xscheck_mb[t] = 0.0
        if inp.pespinmodel >= 3:
            res.preeqpop_mb[t] = np.zeros((n, inp.maxjph + 1, 2))
        ib, ie = inp.ebegin.get(t, 0), inp.eend.get(t, -1)
        if ib >= ie:
            continue
        # population.f90:129 -- multiple pre-equilibrium is neutrons and protons only
        if inp.flagmulpre and t in (1, 2):
            res.mulpre[t] = True
        if res.mulpre[t]:
            if inp.flag2comp:
                res.xspopph2_mb[t] = np.zeros(
                    (n, inp.maxpar + 1, inp.maxpar + 1, inp.maxpar + 1, inp.maxpar + 1))
            else:
                res.xspopph_mb[t] = np.zeros((n, inp.maxpar + 1, inp.maxpar + 1))
        etop = inp.etotal_mev - r.sep_mev
        xspreeq = np.asarray(inp.xspreeq_mb[t], float)
        xsgr = np.asarray(inp.xsgr_mb.get(t, np.zeros_like(xspreeq)), float)
        spec = xspreeq + xsgr if inp.flaggiant else xspreeq
        nodes = _bin_nodes_many(eg, ib, ie, etop, inp.etotal_mev - r.sep_mev, r, r.nlast + 1,
                                r.maxex + 1)
        for nexout in range(r.nlast + 1, r.maxex + 1):
            eout = inp.etotal_mev - r.sep_mev - float(r.ex_mev[nexout])
            if eout < eg[ib]:
                continue
            dex = float(r.dex_mev[nexout])
            elow = eout - 0.5 * dex
            ehigh = eout + 0.5 * dex
            if nodes is not None:
                na1, nb1, ea1, eb1, na2, nb2, ea2, eb2 = nodes[nexout]
            else:
                na1, nb1, ea1, eb1 = _bin_nodes(eg, ib, ie, etop, elow)
                na2, nb2, ea2, eb2 = _bin_nodes(eg, ib, ie, etop, ehigh)
            na1 = max(na1, 0)
            xslow = _p1(ea1, eb1, spec[na1], spec[nb1], elow)
            xshigh = _p1(ea2, eb2, spec[na2], spec[nb2], ehigh)
            res.preeqpopex_mb[t][nexout] = _cut(0.5 * (xslow + xshigh) * dex)
            if inp.pespinmodel >= 3:
                jp = np.asarray(inp.xspreeqjp_mb[t], float)
                cc = np.asarray(inp.xscollcontjp_mb.get(t, np.zeros_like(jp)), float)
                gs = inp.xsgrstate_mb.get(t)
                a = jp + cc
                if inp.flaggiant and gs is not None:
                    g = np.asarray(gs, float)  # (E, 4, 2) -> J <= 3, the two GR branches
                    a[:, :4] = a[:, :4] + g.sum(-1)[:, :, None]
                lo = _p1(ea1, eb1, a[na1], a[nb1], elow)
                hi = _p1(ea2, eb2, a[na2], a[nb2], ehigh)
                res.preeqpop_mb[t][nexout] = _cut(0.5 * (lo + hi) * dex)
            if res.mulpre[t]:
                _mulpre_bin(inp, res, t, nexout, dex,
                            (na1, nb1, ea1, eb1, elow), (na2, nb2, ea2, eb2, ehigh))


def _renormalise(inp: PopulationInputs, res: PopulationResult) -> PopulationResult:
    """population.f90:246-268 -- the interpolation does not conserve flux, so renormalise the
    column. Stays in numpy on every path: the sum is `np.sum`'s pairwise one.

    TALYS: population.f90:1 (population)
    Test: A-cn1 / E2E
    """
    for t, r in sorted(inp.residuals.items()):
        col = res.preeqpopex_mb[t]
        sl = slice(r.nlast + 1, r.maxex + 1)
        check = float(col[sl].sum())
        res.xscheck_mb[t] = check
        tot = inp.xspreeqtot_mb.get(t, 0.0) + (
            inp.xsgrtot_mb.get(t, 0.0) if inp.flaggiant else 0.0)
        norm = 1.0 if check == 0.0 else tot / check
        res.norm[t] = norm
        col[sl] *= norm
        if inp.pespinmodel >= 3:
            res.preeqpop_mb[t][sl] *= norm
    return res


def _p1(x1: float, x2: float, y1, y2, x: float):
    """`pol1` on plain floats / arrays; TALYS has no x1 == x2 guard and neither does this."""
    return y1 + (x - x1) / (x2 - x1) * (y2 - y1)


def _cut(xs):
    """population.f90:168 -- anything under 1e-30 mb is stored as a hard zero.

    Signed, as TALYS's `if (xs < 1.e-30) xs = 0.` is (OPEN3M): `pol1` extrapolates past the end of
    the pre-equilibrium spectrum and can go negative, and TALYS zeroes that. Keeping it (an
    `abs` test) made Am-241's alpha column sum negative at 18 MeV, so population.f90:274's
    renormalisation flipped the sign of every bin (docs/results/hf-open3m.md section 2).
    """
    return np.where(xs < XS_MIN_MB, 0.0, xs) if np.ndim(xs) else (
        0.0 if xs < XS_MIN_MB else xs)


def _mulpre_bin(inp: PopulationInputs, res: PopulationResult, t: int, nexout: int, dex: float,
                lo: tuple, hi: tuple) -> None:
    """The same interpolation applied to the particle-hole spectra multiple pre-equilibrium
    decays (population.f90:180-236). Live only at `Einc >= emulpre` (20 MeV).

    TALYS: population.f90:1 (population)
    Test: E2E
    """
    na1, nb1, ea1, eb1, elow = lo
    na2, nb2, ea2, eb2, ehigh = hi

    def integ(arr: np.ndarray) -> float:
        a = _p1(ea1, eb1, arr[na1], arr[nb1], elow)
        b = _p1(ea2, eb2, arr[na2], arr[nb2], ehigh)
        return float(_cut(0.5 * (a + b) * dex))

    if not inp.flag2comp:
        step = np.asarray(inp.xsstep_mb[t], float)  # (pc, E)
        for pc in range(inp.p0, inp.maxpar + 1):
            p, h = pc - PARA[t], pc - inp.p0
            if p < 0 or h < 0:
                continue
            res.xspopph_mb[t][nexout, p, h] = integ(step[pc])
        return
    step2 = np.asarray(inp.xsstep2_mb[t], float)  # (pcpi, pcnu, E)
    for pcpi in range(inp.ppi0, inp.maxpar + 1):
        ppi, hpi = pcpi - PARZ[t], pcpi - inp.ppi0
        if ppi < 0 or hpi < 0:
            continue
        for pcnu in range(inp.pnu0, inp.maxpar + 1):
            pnu, hnu = pcnu - PARN[t], pcnu - inp.pnu0
            if pnu < 0 or hnu < 0:
                continue
            res.xspopph2_mb[t][nexout, ppi, hpi, pnu, hnu] = integ(step2[pcpi, pcnu])
