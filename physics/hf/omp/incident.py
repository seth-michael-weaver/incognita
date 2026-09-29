"""The incident channel: T_lj at the incident energy, total/reaction/shape-elastic cross sections,
S0/S1/R' (incident.f90, incidentnorm.f90, spr.f90).

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T5 (physics/hf/CONTRACT.md §7). Acceptance test: A-inc (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    incident.f90:1 (incident)
    incidentread.f90:1 (incidentread)
    incidentnorm.f90:1 (incidentnorm)
    spr.f90:1 (spr)

Injection (contract §5): the OMP parameters at each incident energy come from T4; until that
lands, pass `omp=` (fields shaped (C,)). Spherical targets only (deformed: ecis.bridge).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

import torch
from torch import Tensor

from physics.hf.core.constants import PARTICLE_INDEX, talys_constants
from physics.hf.core.tensors import DTYPE
from physics.hf.core.units import B_PER_MB, EV_PER_MEV
from physics.hf.omp.inverse import process_tjl
from physics.hf.omp.schrodinger import (
    PARMASS_AMU,
    PARZ,
    nucleus_mass_amu,
    solve_spherical,
)

if TYPE_CHECKING:
    from physics.hf.core.tensors import CaseBatch
    from physics.hf.input.defaults import Options, Params
    from physics.hf.omp.parameters import OMPParameters

FM2_PER_B = 100.0  # 1 b = 100 fm^2 (spr.f90: Rprime = 10*sqrt(0.001*xs/fourpi))


@dataclass(frozen=True)
class IncidentChannel:
    tjl_inc: Tensor  # (C, L, 3) contract j order (spin-1/2: [T(l-1/2), T(l+1/2), 0])
    sigma_tot_mb: Tensor  # (C,)
    sigma_reac_mb: Tensor  # (C,)
    sigma_shape_el_mb: Tensor  # (C,)
    s0: Tensor  # (C,) absolute (talys.out prints units of 1e-4)
    s1: Tensor  # (C,)
    r_prime_fm: Tensor  # (C,)
    t_l: Tensor | None = None  # (C, L) spin-averaged Tlinc
    lmax: Tensor | None = None  # (C,) lmaxinc


def strength_functions(
    t_l: Tensor, e_inc_mev: Tensor, sigma_shape_el_mb: Tensor, A: Tensor, wavenum_fm: Tensor
) -> tuple[Tensor, Tensor, Tensor]:
    """S0, S1 and R' from the incident T_l (spr.f90):
    S0 = T_0 / (2 pi sqrt(E[eV])), S1 = T_1 (1 + (kR)^2)/(kR)^2 / (2 pi sqrt(E[eV])),
    R = 1.35 A^(1/3), R' = sqrt(sigma_shape_el / 4 pi).

    TALYS: spr.f90:1 (spr)
    Test: A-inc
    """
    efac = 1.0 / (torch.sqrt(EV_PER_MEV * e_inc_mev) * 2.0 * math.pi)
    rpo = 1.35 * A.to(DTYPE) ** (1.0 / 3.0)
    r2k2 = rpo * rpo * wavenum_fm * wavenum_fm
    s0 = t_l[:, 0] * efac
    s1 = t_l[:, 1] * efac * (1.0 + r2k2) / r2k2
    rprime = torch.sqrt(FM2_PER_B * B_PER_MB * sigma_shape_el_mb.clamp_min(0.0) / (4.0 * math.pi))
    return s0, s1, rprime


def incident_channel(
    cases: CaseBatch,
    options: Options | None,
    params: Params | None,
    *,
    omp: OMPParameters | None = None,
    integrator: str = "ecis",
) -> IncidentChannel:
    """Incident-channel quantities for each case (talys.out 'Optical model results' and 'S-wave and
    P-wave strength functions'; transmission_inc.out holds the LAST energy only).

    `omp` injects the parameters (contract §5); with `omp=None` they come from T4's
    `omp_parameters`. Spherical incident channel only: `incidentecis.f90:203` takes this branch
    for `colltype == 'S'`, and couples collective levels otherwise (T13 / `ecis.bridge`).

    TALYS: incident.f90:1 (incident), spr.f90:1 (spr)
    Test: A-inc
    """
    from physics.hf.core.grids import incident_kinematics
    from physics.hf.omp.inverse import _slice_omp

    k0 = PARTICLE_INDEX[cases.projectile]
    n_c = cases.n
    tjl = torch.zeros((n_c, 61, 3), dtype=DTYPE)
    out = {k: torch.zeros(n_c, dtype=DTYPE) for k in ("tot", "reac", "el", "wk")}
    groups: dict[tuple[int, int], list[int]] = {}
    for c in range(n_c):
        groups.setdefault((int(cases.Z[c]), int(cases.A[c])), []).append(c)
    numl = int(talys_constants()["numl"])
    for (Z, A), cs in groups.items():
        idx = torch.tensor(cs)
        m_t = nucleus_mass_amu(Z, A)
        e = cases.e_inc_mev[idx]
        # incidentecis.f90: njmax = max(20, int(2.4*1.25*A**(1/3)*0.22*sqrt(m*E))), min numl
        nj = max(20, int(2.4 * 1.25 * A ** (1.0 / 3.0) * 0.22 * math.sqrt(PARMASS_AMU[k0] * float(e.max()))))
        nj = min(nj, numl)
        if omp is None:
            from physics.hf.omp.inverse import _ported_omp

            p = _ported_omp(Z, A, Z, A, k0, e, options, params)
        else:
            p = _slice_omp(omp, 0, idx, n_c) if _is_per_case(omp, n_c) else omp
        tr = solve_spherical(
            p, Z, A, k0, e, m_targ_amu=m_t, lmax=nj, integrator=integrator,
        )
        tjl[idx, : nj + 1] = tr.tjl[0, 0]
        out["reac"][idx] = tr.sigma_reac_mb[0, 0]
        out["tot"][idx] = tr.sigma_tot_mb[0, 0]
        out["el"][idx] = tr.sigma_shape_el_mb[0, 0]
        for i, c in enumerate(cs):
            _, wk = incident_kinematics(float(e[i]), k0, m_t, 0.0, 0.0)
            out["wk"][c] = wk
    tjl, t_l, lm = process_tjl(tjl, k0)
    if PARZ[k0] != 0:
        out["tot"] = torch.full_like(out["tot"], float("nan"))
        out["el"] = torch.full_like(out["el"], float("nan"))
    if k0 == 1:
        s0, s1, rp = strength_functions(t_l, cases.e_inc_mev, out["el"], cases.A, out["wk"])
    else:
        s0 = s1 = rp = torch.full((n_c,), float("nan"), dtype=DTYPE)
    return IncidentChannel(
        tjl_inc=tjl, sigma_tot_mb=out["tot"], sigma_reac_mb=out["reac"],
        sigma_shape_el_mb=out["el"], s0=s0, s1=s1, r_prime_fm=rp, t_l=t_l, lmax=lm,
    )


def _is_per_case(omp, n_c: int) -> bool:
    v = torch.as_tensor(omp.v_mev)
    return v.dim() >= 1 and v.numel() == n_c and n_c > 1
