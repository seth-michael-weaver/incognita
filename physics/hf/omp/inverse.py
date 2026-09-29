"""Inverse-channel transmission coefficients and reaction cross sections for every emitted particle
on every residual, with TALYS's normalisation (basicxs.f90, inverse.f90, inversenorm.f90).

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T5 (physics/hf/CONTRACT.md §7). Acceptance test: A-trans (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    basicxs.f90:1 (basicxs)
    inverse.f90:1 (inverse)
    inversenorm.f90:1 (inversenorm)
    inverseread.f90:1 (inverseread)

Injection (contract §5): the OMP parameters on the emission grid come from T4
(`physics.hf.omp.parameters`); until that lands, callers pass them in (`omp=`), e.g. from
`physics.hf.reference.omp_parameters`. Spherical targets only: deformed residuals and actinides
take their T_lj from `physics.hf.ecis.bridge` until the ECIS coupled-channels port (T13).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import torch
from torch import Tensor

from physics.hf.core.tensors import DTYPE
from physics.hf.omp.schrodinger import (
    NJ,
    PARA,
    PARMASS_AMU,
    PARZ,
    Transmission,
    nucleus_mass_amu,
    _requires_grad,
    solve_spherical,
    solve_spherical_many,
)

if TYPE_CHECKING:
    from physics.hf.core.grids import EmissionGrid
    from physics.hf.core.tensors import CaseBatch
    from physics.hf.input.defaults import Options, Params
    from physics.hf.omp.parameters import OMPParameters

TRANSLIMIT_DEFAULT = 1.0e-5  # grid.f90:256 translimit = 1/10**transpower, transpower 5
TRANSEPS_DEFAULT = 1.0e-8  # input_numerics.f90:80


def process_tjl(
    tjl: Tensor, particle: int, translimit: float = TRANSLIMIT_DEFAULT,
    transeps: float = TRANSEPS_DEFAULT,
) -> tuple[Tensor, Tensor, Tensor]:
    """TALYS's processing of the T_lj read from ECIS: fill in the (l+s) value ECIS omits at the
    highest l with the (l-s) one (and vice versa for l > 0), spin-average to T_l, and find lmax,
    the last l before every T_lj falls below max(T_0 * translimit / (2l+1), transeps).

    tjl: (..., L, 3) in the contract's j order. Returns (tjl, t_l (..., L), lmax (...)).

    TALYS: inverseread.f90:1 (inverseread)
    Test: A-trans
    """
    t = tjl.clone()
    nj = NJ[particle]
    L = torch.arange(t.shape[-2], dtype=DTYPE)
    lpos = (L > 0)[..., :]
    if nj == 2:
        m, p = t[..., 0], t[..., 1]
        p = torch.where((m != 0) & (p == 0), m, p)
        m = torch.where((m == 0) & (p != 0) & lpos, p, m)
        t = torch.stack([m, p, t[..., 2]], -1)
        tl = ((L + 1) * p + L * m) / (2 * L + 1)
    elif nj == 3:
        m, z, p = t[..., 0], t[..., 1], t[..., 2]
        z = torch.where((m != 0) & (z == 0), m, z)
        p = torch.where((m != 0) & (p == 0), m, p)
        m = torch.where((m == 0) & (p != 0) & lpos, p, m)
        t = torch.stack([m, z, p], -1)
        tl = ((2 * L + 3) * p + (2 * L + 1) * z + (2 * L - 1) * m) / (3 * (2 * L + 1))
    else:
        tl = t[..., 0]
    teps = torch.clamp_min(tl[..., :1].detach() * translimit / (2 * L + 1), transeps)
    small = (t[..., :nj].detach() < teps[..., None]).all(-1)
    nl = t.shape[-2]
    first = torch.where(
        small.any(-1), small.to(torch.int64).argmax(-1), torch.full(small.shape[:-1], nl)
    )
    return t, tl, first - 1


def _clip_to_njmax(tjl: Tensor, A_res: int, particle: int, e_lab_mev: Tensor) -> Tensor:
    """Zero every l above the highest one ECIS writes at that emission energy.

    `inverseecis` recomputes `njmax` inside its energy loop and asks ECIS for exactly that many
    total-J values, so TALYS's `Tjl(type, nen, ., l)` is a hard zero above the resulting l cap
    however large the true coefficient is -- the alpha's top written coefficient on Ca-37 is
    3.8e-5, three orders above `translimit`, and the next l is simply absent. A solver that fills
    those cells hands `densprepare`'s second-order interpolation three numbers TALYS does not
    have, and one that clips a cap lower than ECIS's takes away a partial wave TALYS does have.
    The cap is `schrodinger.lmax_ecis_grid`: njmax for n/p/d/t/h, njmax - 1 for the alpha.

    TALYS: inverseecis.f90:1 (inverseecis)
    Test: A-trans
    """
    from physics.hf.omp.schrodinger import lmax_ecis_grid

    lcap = lmax_ecis_grid(A_res, particle, e_lab_mev)
    ll = torch.arange(tjl.shape[-2], device=tjl.device)
    keep = ll[None, :] <= lcap.to(tjl.device)[:, None]  # (E, L)
    return tjl * keep.reshape((1,) * (tjl.dim() - 3) + keep.shape + (1,)).to(tjl.dtype)


def inversenorm(
    trans: Transmission, norm: Tensor | None = None
) -> Transmission:
    """Normalisation of inverse reaction cross sections to systematics (Tripathi) when
    `flagsys` is set for the particle; the default (flagsys n, input_directmodel.f90:106) leaves
    the optical-model values untouched. `norm` (C, particle, E) multiplies sigma_R and T_lj.

    TALYS: inversenorm.f90:1 (inversenorm)
    Test: A-trans
    """
    if norm is None:
        return trans
    return Transmission(
        tjl=trans.tjl * norm[..., None, None],
        nj=trans.nj,
        sigma_reac_mb=trans.sigma_reac_mb * norm,
        sigma_tot_mb=trans.sigma_tot_mb,
        sigma_shape_el_mb=trans.sigma_shape_el_mb,
        lmax=trans.lmax,
    )


def inverse_particle(
    Z_res: int,
    A_res: int,
    particle: int,
    e_lab_mev: Tensor,
    omp: OMPParameters,
    *,
    m_res_amu: float | None = None,
    lmax: int | None = None,
    integrator: str = "ecis",
) -> Transmission:
    """T_lj on the emission grid for one particle on the residual it leaves behind, processed as
    TALYS reads it (fill-in, lmax). `e_lab_mev` is the energy TALYS hands ECIS,
    egrid/specmass(Zix, Nix, type); `omp` holds the parameters on that axis.

    TALYS: inverseecis.f90:1 (inverseecis), inverseread.f90:1 (inverseread)
    Test: A-trans
    """
    tr = solve_spherical(
        omp, Z_res, A_res, particle, e_lab_mev, m_targ_amu=m_res_amu, lmax=lmax,
        integrator=integrator,
    )
    return _processed(tr, A_res, particle, e_lab_mev)


def _processed(tr: Transmission, A_res: int, particle: int, e_lab_mev: Tensor) -> Transmission:
    """`inverse_particle`'s reading of a raw solve: the ECIS l cap, fill-in and lmax."""
    tjl = _clip_to_njmax(tr.tjl, A_res, particle, e_lab_mev)
    tjl, _, lm = process_tjl(tjl, particle)
    return Transmission(
        tjl=tjl, nj=tr.nj, sigma_reac_mb=tr.sigma_reac_mb, sigma_tot_mb=tr.sigma_tot_mb,
        sigma_shape_el_mb=tr.sigma_shape_el_mb, lmax=lm,
    )


def inverse_channels(
    cases: CaseBatch,
    grid: EmissionGrid,
    options: Options | None,
    params: Params | None,
    *,
    omp: dict[int, OMPParameters] | None = None,
    parskip: dict[int, bool] | None = None,
    lmax: int = 30,
    edetach: dict[int, Tensor] | None = None,
) -> Transmission:
    """Emission-grid T_lj for particles 1..6 on the residuals they leave behind
    (transmission_{n,p,d,t,h,a}.out).

    For case c with compound nucleus (Zc, Ac) = target + projectile, particle k leaves
    (Zc - parZ(k), Ac - parA(k)); ECIS is given e = egrid / specmass with
    specmass = M_res / (M_res + m_k) (masses.f90:238). `omp[k]` holds OMP parameters with fields
    shaped (C, E) or (E,) on the grid positions. Grid positions outside `grid.mask` get T = 0.
    Output: (C, 6, E, lmax+1, 3).

    `edetach[k]` is an optional per-particle boolean over the grid marking the positions the
    caller **keeps**; the OMP parameters at every other position are detached before the solve.
    The forward value is untouched -- `torch.where(keep, x, x.detach())` is the identity -- and
    the reverse pass gains the one thing DIFFPARAM needs from it. `inverse` fills `Tjl` only over
    `[ebegin(type), eend(type)]` (inverseecis.f90:402) and the caller zeroes the rest, but the
    port still *solves* the rest, and at 1 keV the alpha channel is hundreds of orders of
    magnitude under its barrier: the value is a harmless underflowed zero, the local derivative
    there is infinite, and the discarded cells' zero incoming gradient then turns `0 * inf` into
    a NaN that poisons the entire backward pass. `where`'s backward is a *select*, so detaching
    at the parameters stops that NaN at the only point where it can be stopped without changing
    a number. Energies do not mix in the solver, so no live row loses anything.

    TALYS: basicxs.f90:1 (basicxs), inverse.f90:1 (inverse)
    Test: A-trans
    """
    from physics.hf.core.constants import PARTICLE_INDEX

    projectile = PARTICLE_INDEX[cases.projectile]
    n_c, n_e = grid.e_mev.shape
    out = torch.zeros((n_c, 6, n_e, lmax + 1, 3), dtype=DTYPE)
    sig = torch.zeros((n_c, 6, n_e), dtype=DTYPE)
    nan = torch.full((n_c, 6, n_e), float("nan"), dtype=DTYPE)
    tot, el = nan.clone(), nan.clone()
    lm = torch.full((n_c, 6, n_e), -1, dtype=torch.int64)
    for c in range(n_c):
        zc = int(cases.Z[c]) + PARZ[projectile]
        ac = int(cases.A[c]) + PARA[projectile]
        todo = []
        for k in range(1, 7):
            if parskip is not None and parskip.get(k, False):
                continue
            zr, ar = zc - PARZ[k], ac - PARA[k]
            if zr <= 0 or ar <= zr:
                continue
            m_res = nucleus_mass_amu(zr, ar)
            specmass = m_res / (m_res + PARMASS_AMU[k])
            sel = grid.mask[c] & (grid.e_mev[c] > 0)
            idx = torch.nonzero(sel).flatten()
            if idx.numel() == 0:
                continue
            e_lab = grid.e_mev[c, idx] / specmass
            if omp is not None:
                p = _slice_omp(omp[k], c, idx, n_c)
            else:
                p = _ported_omp(int(cases.Z[c]), int(cases.A[c]), zr, ar, k, e_lab,
                                options, params)
            if edetach is not None and k in edetach:
                p = _detach_outside(p, edetach[k].to(idx.device)[idx])
            todo.append((k, zr, ar, idx, e_lab, p, m_res))
        # SPEEDT: without a gradient the six particles share one radial loop and one pass of the
        # Coulomb recurrences (`schrodinger.solve_spherical_many`), bit-identical per particle
        if todo and not any(_requires_grad(item[5]) for item in todo):
            many = solve_spherical_many([(p, zr, ar, k, e_lab, m_res, lmax)
                                         for k, zr, ar, idx, e_lab, p, m_res in todo])
        else:
            many = [solve_spherical(p, zr, ar, k, e_lab, m_targ_amu=m_res, lmax=lmax)
                    for k, zr, ar, idx, e_lab, p, m_res in todo]
        for (k, zr, ar, idx, e_lab, _p, _m), raw in zip(todo, many, strict=True):
            tr = _processed(raw, ar, k, e_lab)
            out[c, k - 1, idx] = tr.tjl[0, 0]
            sig[c, k - 1, idx] = tr.sigma_reac_mb[0, 0]
            lm[c, k - 1, idx] = tr.lmax[0, 0]
            if k == 1:
                tot[c, 0, idx] = tr.sigma_tot_mb[0, 0]
                el[c, 0, idx] = tr.sigma_shape_el_mb[0, 0]
    return Transmission(
        tjl=out, nj=torch.tensor([NJ[k] for k in range(1, 7)], dtype=torch.int64),
        sigma_reac_mb=sig, sigma_tot_mb=tot, sigma_shape_el_mb=el, lmax=lm,
    )


def _ported_omp(
    Z_target: int, A_target: int, Z_res: int, A_res: int, particle: int, e_lab_mev: Tensor,
    options: Options | None, params: Params | None,
):
    """T4's OMP parameters for `particle` on (Z_res, A_res) at `e_lab_mev`, with the defaults of
    the target that defines the run. T4 indexes the nuclide by (Z, N), not (Z, A).

    TALYS: optical.f90:1 (optical)
    Test: A-trans
    """
    from physics.hf.input.defaults import default_options, default_params
    from physics.hf.omp.parameters import omp_parameters

    o = options if options is not None else default_options(Z_target, A_target)
    pa = params if params is not None else default_params(Z_target, A_target, o)
    return omp_parameters(Z_res, A_res - Z_res, particle, e_lab_mev, pa, o)


class _Sliced:
    def __init__(self, **kw):
        self.__dict__.update(kw)


def _detach_outside(p, keep: Tensor):
    """`p` with every field detached at the energies `keep` is False (DIFFPARAM; see `edetach`).

    The forward value is unchanged by construction. A field that is a single number carries no
    energy axis and cannot be masked per energy, so it is broadcast first -- which is also
    exactly what `schrodinger._param` would have done to it.
    """
    from physics.hf.omp.schrodinger import _FIELDS

    n_e = int(keep.numel())
    kw = {}
    for f in _FIELDS:
        v = torch.as_tensor(getattr(p, f), dtype=DTYPE).reshape(-1)
        v = v.expand(n_e) if v.numel() == 1 else v
        kw[f] = torch.where(keep, v, v.detach())
    return _Sliced(**kw)


def _slice_omp(p, c: int, idx: Tensor, n_c: int):
    from physics.hf.omp.schrodinger import _FIELDS

    kw = {}
    for f in _FIELDS:
        v = torch.as_tensor(getattr(p, f), dtype=DTYPE)
        if v.dim() == 2:
            v = v[c]
        kw[f] = v[idx] if v.dim() == 1 and v.numel() > 1 else v
    return _Sliced(**kw)
