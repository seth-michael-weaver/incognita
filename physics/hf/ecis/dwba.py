"""Stage b of the ECIS port: the DWBA that `directecis.f90` runs for every collective level with
a non-zero deformation, which is where T12's `xsdirdisc` and `xsgrcoll` come from.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.
ECIS-06 (`ecist.f`) is by J. Raynal and ships inside the TALYS repository under its MIT license.

Task: T13 (physics/hf/CONTRACT.md §7). Acceptance test: A-direct (the `xsdirdisc` column of
`directE*.out`, which is T12's A-mult input).

TALYS routines ported here (file:line of the subroutine/function statement):
    directecis.f90:1 (directecis)
    directread.f90:1 (directread)
    ecist.f:8043 (vibm)
    ecist.f:18285 (inri)

Line numbers of anchors follow Python's `str.splitlines()`; `grep -n` gives numbers 30 lower.

What `directecis.f90` actually asks ECIS for, read off its deck
(`ecis1 = 'FFFFFTFFFFFFFFFFFFFFFFFFFFFTFTFF...'`, `ecis2 = 'FFFFFFFFTFFFFTTFTTTFTTTFTFFF...'`):

  * `ncoll = 2`, `vibrational`, `iph(2) = 1`, `Nband = 1`, `tarspin = 0`, `tarparity = '+'`.
    Every level is its own two-channel problem, a one-phonon excitation of a 0+ "ground state" --
    for an odd-A target the excited spin is the CORE spin `jcore`, not `jdis` (directecis.f90:207).
  * `lo(30) = T` (ecis1(30)): pure DWBA -- the transition is first order in the deformation, and
    `iterm` is forced to 1 (calx-357).
  * `lo(12) = F`: unlike the incident coupled-channels deck (`incidentecis.f90:257` sets it to
    'T'), the DWBA deck does NOT deform the imaginary potential, so the transition form factor is
    purely REAL -- the derivative of the real volume plus the real surface term (`rotp-082`'s
    `ldl` map; see `formfactor.DWBA_PARTS`).
  * `lo(13) = F`, `lo(11) = F`: the spin-orbit and the Coulomb potential are not deformed.
  * `flagstate` is false by default, so `npp = 1`: both channels see the SAME optical potential,
    the one at the incident energy.

With a 0+ entrance state the whole angular-momentum algebra collapses. The entrance channel at
total J is unique per parity (I = 0 forces j = J, l = J -/+ 1/2), and `quan`'s coefficient
(`coupling.coupling_matrix`) reduces, through {j lambda j'; lambda J 0} = (-1)^(j+lambda+j')
/ sqrt((2j+1)(2 lambda+1)), to

    |A^lambda_{c'c}|^2 = <j -1/2; lambda 0 | j' -1/2>^2 ,      j = J,

whose sum over j' is 1. The one-phonon reduced matrix element of `vibm-152..163` is +/- 1 and
only its sign is lost, which a cross section does not see.

First order then gives the S-matrix in closed form. With the radial equations written as
u'' = M u exactly as in `solver.smatrix`, and u_c normalised the way that solver normalises them
(u -> H^- delta - H^+ S~), the Green's function of the exit channel gives

    S~_{c'c} = (i / (2 k_c')) mu A^lambda_{c'c} int_0^rmatch u_c'(r) F(r) u_c(r) dr

with u_c, u_c' the ELASTIC (uncoupled) distorted waves of the entrance and exit channels, and
then S = S~ sqrt(k_c'/k_c) as usual. The cross section is `resu`'s

    sigma = (pi / k_0^2) sum_{J,pi} (2J+1) / ((2 I_0 + 1)(2 s + 1)) sum_{c'} |S_{c'c}|^2 .
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import torch
from torch import Tensor

from physics.hf.core.angmom import clebsch
from physics.hf.core.tensors import DTYPE
from physics.hf.core.units import MB_PER_FM2
from physics.hf.ecis.formfactor import DWBA_PARTS, derivative_form_factor
from physics.hf.ecis.solver import CDTYPE, channel_kinematics
from physics.hf.omp.schrodinger import (
    PARMASS_AMU,
    PARSPIN,
    PARZ,
    EcisKinematics,
    coulomb_functions,
    ecis_card_energy,
    ecis_card_value,
    ecis_grid,
    nucleus_mass_amu,
    optical_potential,
)

SQRT4PI = math.sqrt(4.0 * math.pi)


@dataclass(frozen=True)
class DwbaResult:
    """DWBA cross sections for one incident energy, one entry per level asked about."""

    xs_mb: Tensor  # (n,)
    n_j: int  # number of total-J blocks summed
    lmax: int  # njmax actually used
    n_r: int  # radial points integrated
    h_fm: float


def _lj_table(lmax: int) -> tuple[Tensor, Tensor, Tensor]:
    """(l, j, 2 l.s) of every channel with l <= lmax and j = l +/- 1/2, l = 0 having only j=1/2."""
    ls, js = [], []
    for orb in range(lmax + 1):
        for jj in (orb - 0.5, orb + 0.5):
            if jj < 0:
                continue
            ls.append(orb)
            js.append(jj)
    l = torch.tensor(ls, dtype=torch.int64)
    j = torch.tensor(js, dtype=DTYPE)
    ls2 = j * (j + 1.0) - l.to(DTYPE) * (l.to(DTYPE) + 1.0) - 0.75
    return l, j, ls2


def distorted_waves(
    f_lj: Tensor, kappa2: Tensor, l: Tensor, h: float, n: int
) -> Tensor:
    """Numerov on the uncoupled radial equation u'' = (f_lj(r) - k^2) u for every (channel, k),
    from u(0) = 0 and u(h) = h^(l+1). Returns (NK, NLJ, n+1) with column i at r = i h.

    `f_lj` is (NLJ, n+1) -- the r-dependent part, i.e. l(l+1)/r^2 + mu (V_central + V_Coulomb
    + 2 l.s V_so) -- and `kappa2` is (NK,), the signed k^2 of each channel energy. Column 0 of
    `f_lj` is never used (it multiplies u(0) = 0) and may hold anything finite.

    The same integrator as `solver.smatrix`, reduced to one channel; T5's argument applies
    unchanged (`omp/schrodinger.py`).

    TALYS: ecist.f:18285 (inri)
    Test: A-direct
    """
    from physics.hf.native import speedw

    if (speedw.available() and torch.get_num_threads() == 1 and f_lj.device.type == "cpu"
            and not (torch.is_grad_enabled() and (f_lj.requires_grad or kappa2.requires_grad))):
        return speedw.dwba_numerov(f_lj, kappa2, l, h, n)  # SPEEDW: this loop, compiled, same bits
    nk = kappa2.shape[0]
    nlj = l.shape[0]
    c = h * h / 12.0
    y = torch.zeros((nk, nlj, n + 1), dtype=CDTYPE)
    y[:, :, 1] = torch.as_tensor(h, dtype=DTYPE) ** (l.to(DTYPE) + 1.0)
    k2 = kappa2.to(CDTYPE)[:, None]

    def fval(i: int) -> Tensor:
        return f_lj[None, :, i] - k2

    fm1, f0 = fval(1), fval(1)
    for i in range(1, n):
        fp1 = fval(i + 1)
        y[:, :, i + 1] = (
            2.0 * y[:, :, i] * (1.0 + 5.0 * c * f0) - y[:, :, i - 1] * (1.0 - c * fm1)
        ) / (1.0 - c * fp1)
        fm1, f0 = f0, fp1
    return y


def _normalise(
    y: Tensor, f_lj: Tensor, kappa2: Tensor, eta: Tensor, l: Tensor, h: float
) -> Tensor:
    """Rescale each raw solution so that it is the physical `H^- - S H^+` of `solver.smatrix`.

    Matching at r = (n-1) h with the Numerov-consistent derivative. The scale is NOT taken as
    `y / (H^- - S H^+)` with `S` from the usual ratio: for a barely-open high-l channel (rho = k r
    of order 1, l of order 7) F_l is some 1e-7 of G_l, so `S` comes out as 1 + O(1e-7) and
    `H^- - S H^+` is the difference of two numbers that agree to that many digits. Eliminating S
    analytically leaves the Wronskian,

        H^- - S H^+ = -2 i k y / (y' H^+ - y H^+') ,    so    C = (y H^+' - y' H^+) / (2 i k),

    which has no cancellation in it: the denominator is exactly C times the constant Wronskian
    W[H^-, H^+] = 2 i k. Ca-40's level 40 at 8 MeV (c.m. exit energy 0.126 MeV, lambda = 6) is
    98x wrong with the first form and right with the second.
    """
    nk, nlj, np1 = y.shape
    n = np1 - 1
    y = y / y.abs().amax(dim=2, keepdim=True).clamp_min(1.0e-300)
    c = h * h / 12.0
    k2 = kappa2.to(CDTYPE)[:, None]
    fp, fm = f_lj[None, :, n] - k2, f_lj[None, :, n - 2] - k2
    um = y[:, :, n - 1]
    dy = (
        y[:, :, n] * (1.0 - 2.0 * c * fp) - y[:, :, n - 2] * (1.0 - 2.0 * c * fm)
    ) / (2.0 * h)
    k = kappa2.abs().sqrt()
    rm = h * (n - 1)
    if not (torch.is_grad_enabled() and (kappa2.requires_grad or eta.requires_grad)):
        # SETB: one Coulomb row per level, the same bits (ecis/dwba_setb.py)
        from physics.hf.ecis.dwba_setb import exit_waves

        hp, dhp = exit_waves(kappa2, eta, l, rm, nk, nlj)
        kk = k[:, None].expand(nk, nlj)
    else:
        lmax = int(l.max())
        rho = (k * rm)[:, None].expand(nk, nlj).reshape(-1)
        et = eta[:, None].expand(nk, nlj).reshape(-1)
        F, dF, G, dG = coulomb_functions(et.detach(), rho.detach(), lmax)
        idx = l[None, :].expand(nk, nlj).reshape(-1, 1)
        kk = k[:, None].expand(nk, nlj)
        hp = torch.complex(G.gather(1, idx).reshape(nk, nlj), F.gather(1, idx).reshape(nk, nlj))
        dhp = torch.complex(
            dG.gather(1, idx).reshape(nk, nlj) * kk, dF.gather(1, idx).reshape(nk, nlj) * kk
        )
    cnorm = (um * dhp - dy * hp) / (2.0j * kk.to(CDTYPE))
    return y / cnorm[:, :, None]


def _simpson_weights(n: int, h: float) -> Tensor:
    """Composite Simpson on r_i = i h, i = 0..n, falling back to the trapezoid on the last
    interval when n is odd."""
    w = torch.zeros(n + 1, dtype=DTYPE)
    m = n if n % 2 == 0 else n - 1
    w[0] += 1.0
    w[m] += 1.0
    w[1:m:2] += 4.0
    w[2:m:2] += 2.0
    w *= h / 3.0
    if m != n:
        w[n - 1] += h / 2.0
        w[n] += h / 2.0
    return w


def dwba_cross_sections(
    omp,
    Z: int,
    A: int,
    e_inc_mev: float,
    level_e_mev: Tensor,
    level_spin: Tensor,
    level_parity: Tensor,
    vibbeta: Tensor,
    deformation_length: bool,
    *,
    particle: int = 1,
    refine: int = 1,
    njmax: int | None = None,
    numl: int = 60,
    parts: tuple[str, ...] = DWBA_PARTS,
    ecis_rounding: bool = True,
) -> DwbaResult:
    """`directecis` + `directread` for one incident energy: the DWBA cross section of every level
    in the list, in mb and in the order given.

    `omp` holds the optical-model parameters at this ONE incident energy (a single-row
    `ecis.reference.InjectedOMP` or T4's `OMPParameters`); `level_*` and `vibbeta` are T12's
    `direct.dwba.direct_levels` output, except that `level_spin`/`level_parity` must already be
    the CORE spin for an odd-A target (`ecis.weakcore.dwba_level_spins`).

    TALYS: directecis.f90:1 (directecis)
    Test: A-direct
    """
    n_lev = int(level_e_mev.numel())
    e_lab = torch.as_tensor([float(e_inc_mev)], dtype=DTYPE)
    m_proj, m_targ = float(PARMASS_AMU[particle]), nucleus_mass_amu(Z, A)
    e_lev = torch.as_tensor(level_e_mev, dtype=DTYPE).reshape(-1)
    if ecis_rounding:
        e_lab = ecis_card_energy(e_lab)
        m_proj = float(ecis_card_value(torch.tensor(m_proj, dtype=DTYPE)))
        m_targ = float(ecis_card_value(torch.tensor(m_targ, dtype=DTYPE)))
        e_lev = ecis_card_value(e_lev)
    z_prod = float(PARZ[particle] * Z)
    spin = float(PARSPIN[particle])
    kin = channel_kinematics(
        e_lab, m_proj, m_targ, z_prod, torch.cat([torch.zeros(1, dtype=DTYPE), e_lev])
    )
    k = kin.k_fm[0]  # (n_lev+1,)
    kappa2 = kin.kappa2[0]
    eta = kin.eta[0]
    mu = float(kin.mu_coef[0])
    grid_kin = EcisKinematics(
        ecm_mev=kin.ecm_mev[:, 0], k_fm=k[:1], eta=eta[:1], mu_coef=kin.mu_coef
    )
    h_t, ism, _ = ecis_grid(omp, m_targ, grid_kin)
    h = float(h_t[0]) / refine
    n = int(ism[0]) * refine
    r = h * torch.arange(0, n + 1, dtype=DTYPE)
    r_safe = r.clone()
    r_safe[0] = h  # column 0 multiplies u(0) = 0
    if njmax is None:
        x = 2.4 * 1.25 * (A ** (1.0 / 3.0)) * 0.22 * math.sqrt(m_proj * float(e_lab))
        njmax = min(max(20, int(x)), numl)
    lam_max = int(torch.as_tensor(level_spin).max()) if n_lev else 0
    lmax = njmax + lam_max + 1
    # SETB: with autograd off, the distorted waves are solved only for the entrance channel and the
    # levels the sum below reads; a call with none of them returns its zeros without solving
    # (ecis/dwba_setb.py). `row[b]` is level b's row of `u`.
    rows_of = None
    if not torch.is_grad_enabled():
        from physics.hf.ecis.dwba_setb import live_levels

        live = live_levels(level_spin, level_parity, vibbeta, kappa2, n_lev)
        if not live:
            return DwbaResult(xs_mb=torch.zeros(n_lev, dtype=DTYPE), n_j=int(njmax) + 1,
                              lmax=njmax, n_r=n, h_fm=h)
        rows_of = {b: i + 1 for i, b in enumerate(live)}
        sel = torch.tensor([0] + [b + 1 for b in live])
    l, j, ls2 = _lj_table(lmax)

    central, so, coul = optical_potential(omp, m_targ, r_safe, z_prod)
    diag = central[0] + coul[0].to(CDTYPE)  # (n+1,)
    f_lj = (
        (l.to(DTYPE) * (l.to(DTYPE) + 1.0))[:, None] / r_safe[None, :] ** 2
    ).to(CDTYPE) + mu * (diag[None, :] + ls2.to(CDTYPE)[:, None] * so[0][None, :])

    if rows_of is None:
        u = distorted_waves(f_lj, kappa2, l, h, n)
        u = _normalise(u, f_lj, kappa2, eta, l, h)
    else:
        u = distorted_waves(f_lj, kappa2[sel], l, h, n)
        u = _normalise(u, f_lj, kappa2[sel], eta[sel], l, h)
    w = derivative_form_factor(omp, m_targ, r_safe, deformation_length, parts)[0]
    w[0] = 0.0  # r = 0 carries no weight; u(0) = 0 anyway
    wt = _simpson_weights(n, h)
    # I[b, c', c] = int u^(b)_c'(r) W(r) u^(0)_c(r) dr
    lhs = u * (w * wt.to(CDTYPE))[None, None, :]
    integral = torch.einsum("bpr,qr->bpq", lhs, u[0])

    xs = torch.zeros(n_lev, dtype=DTYPE)
    fac = math.pi / float(k[0]) ** 2 * MB_PER_FM2
    # The entrance channel of a 0+ target at total J is (l = J -/+ 1/2, j = J), so the total-J sum
    # is a sum over entrance channels with J = j_c, and quan's coefficient squared is the single
    # Clebsch-Gordan <j_c -1/2; lambda 0 | j_c' -1/2>^2 (see the module docstring). The weight
    # therefore depends on the level only through (lambda, parity), so it is cached.
    jc, jp = j[None, :], j[:, None]
    par = ((-1.0) ** (l.to(DTYPE)[:, None] + l.to(DTYPE)[None, :]))
    open_j = (jc <= njmax + 0.5 + 1.0e-9).to(DTYPE)
    weights: dict[tuple[int, int], Tensor] = {}
    n_j = int(njmax) + 1
    for b in range(n_lev):
        lam = int(round(float(level_spin[b])))
        pb = int(level_parity[b])
        d = float(vibbeta[b]) / SQRT4PI
        if pb != (-1) ** lam or d == 0.0 or float(kappa2[b + 1]) <= 0.0:
            continue  # a lambda-pole form factor cannot reach unnatural parity
        key = (lam, pb)
        if key not in weights and not torch.is_grad_enabled():
            # SETB: the same table, cached for the worker (ecis/dwba_setb.py)
            from physics.hf.ecis.dwba_setb import cg_weights

            weights[key] = cg_weights(lam, pb, int(lmax), int(njmax), float(spin))
        if key not in weights:
            lm = torch.full_like(jp.expand(jp.shape[0], jc.shape[1]), float(lam))
            cg = clebsch(
                jc.expand_as(lm), lm, jp.expand_as(lm),
                torch.full_like(lm, -0.5), torch.zeros_like(lm), torch.full_like(lm, -0.5),
            )
            keep = (pb * par > 0).to(DTYPE) * open_j
            weights[key] = (2.0 * jc + 1.0) / (2.0 * spin + 1.0) * cg * cg * keep
        pre = (mu * d) ** 2 / (4.0 * float(k[b + 1]) * float(k[0]))
        row = b + 1 if rows_of is None else rows_of[b]
        xs[b] = fac * pre * (weights[key] * integral[row].abs() ** 2).sum()
    return DwbaResult(xs_mb=xs, n_j=n_j, lmax=njmax, n_r=n, h_fm=h)




@dataclass(frozen=True)
class DwbaCase:
    """Everything `directecis.f90` asks ECIS at one (target, incident energy): the level list in
    file order with the spin/parity ECIS is actually given, and the four giant resonances."""

    target: str
    Z: int
    A: int
    e_inc_mev: float
    level_index: Tensor  # (n,) TALYS level numbers
    e_mev: Tensor
    spin: Tensor  # jcore for an odd-A target
    parity: Tensor
    vibbeta: Tensor
    deformation_length: bool
    gr_which: Tensor  # (m,) indices into direct.dwba.GR_LABELS
    gr_e_mev: Tensor
    gr_spin: Tensor
    gr_parity: Tensor
    gr_vibbeta: Tensor


_CORE_LAST: list = []  # NATIVEX2: [struct, options, params, (jcore, pcore)] of the last odd-A case


def _core_spins_of(cs, Z: int, A: int):
    """`weakcore.core_spins` of an odd-A `DirectCase`'s target: (jcore, pcore) per level.

    NATIVEX2: a function of the target's structure only, which `prepare_case` rebuilt at every
    incident energy (masses, both level schemes and deformations, the core assignment: 2.7 ms a
    call). Remembered for the last case, matched on the identity of its `struct`, `options` and
    `params` (one set per target and declared grid, `direct.prepare._base`); autograd on
    recomputes.

    TALYS: weakcoupling.f90:1 (weakcoupling)
    Test: A-direct
    """
    from physics.hf.ecis.weakcore import core_spins
    from physics.hf.input.nuclides import weak_coupling_core
    from physics.hf.structure.deformation import deformation
    from physics.hf.structure.levels import discrete_levels
    from physics.hf.structure.masses import masses as get_masses

    o = cs.options
    memo = not torch.is_grad_enabled()
    if (memo and _CORE_LAST and _CORE_LAST[0] is cs.struct and _CORE_LAST[1] is o
            and _CORE_LAST[2] is cs.params):
        return _CORE_LAST[3]
    m = get_masses(o, cs.params)
    Ar = A  # the k0 residual of an incident neutron is the target itself
    lev = discrete_levels(Z, Ar, o, m, cs.params)
    dfm = deformation(Z, Ar, o, lev, m, cs.params)
    zc, nc = weak_coupling_core(o)
    cz = o.Zinit - zc
    ca = cz + o.Ninit - nc
    clev = discrete_levels(cz, ca, o, m, cs.params)
    out = core_spins(dfm, lev, deformation(cz, ca, o, clev, m, cs.params), clev)
    if memo:
        _CORE_LAST[:] = [cs.struct, o, cs.params, out]
    return out


def prepare_case(omp, target: str, e_inc_mev: float, *, direct_case=None,
                 levels=None) -> DwbaCase:
    """Build the DWBA question for one incident energy from T2's structure and T12's
    `direct.prepare` / `direct.dwba`, plus `ecis.weakcore` for an odd-A target's core spins.

    `omp` is the single-row OMP at this energy; only `rv_fm` is read, for the `deftype == 'D'`
    conversion of the giant-resonance beta (directecis.f90:239).

    `direct_case` is a prebuilt `direct.prepare.DirectCase`. Pass one when the caller already
    has it, or when it was built for an energy grid this function cannot discover -- the default
    path calls `direct.prepare.case(target, e)`, which asks the reference dump which energies
    have a direct block (NODUMP's chained arm has no dump to ask).

    `levels` is `direct.dwba.direct_levels` of that case at this energy when the caller already
    holds it (NATIVEX2: `direct.chain.computed_cross_sections` does); otherwise it is built here.

    TALYS: directecis.f90:1 (directecis)
    Test: A-direct
    """
    import numpy as np

    from physics.hf.direct.dwba import GR_LI, direct_levels, giant_levels
    from physics.hf.direct.dwba import giant_resonance_parameters_of as giant_resonance_parameters
    from physics.hf.direct.prepare import case as _direct_case
    from physics.hf.direct.prepare import parse_target
    from physics.hf.ecis.weakcore import dwba_level_spins

    Z, A = parse_target(target)
    cs = direct_case if direct_case is not None else _direct_case(target, e_inc_mev)
    k0 = cs.options.k0
    lv = (levels if levels is not None
          else direct_levels(cs.struct, cs.eninccm_mev, cs.eoutdis_mev, e_inc_mev, k0))
    jcore = pcore = np.zeros(cs.struct.jdis.shape)
    if cs.struct.Atarget % 2 == 1:
        jcore, pcore = _core_spins_of(cs, Z, A)
    spin, par = dwba_level_spins(cs.struct, lv.index, jcore, pcore, cs.struct.nlast)
    gr = giant_resonance_parameters(cs.struct, cs.params)
    which = giant_levels(gr, cs.eninccm_mev, k0) if cs.flaggiant else np.zeros(0, np.int64)
    gb = gr.beta.detach()[which].clone()
    if cs.struct.deftype == "D":  # directecis.f90:239
        rv = torch.as_tensor(omp.rv_fm, dtype=DTYPE).reshape(-1)[0]
        gb = gb * ecis_card_value(rv) * A ** (1.0 / 3.0)
    lsp = torch.tensor([float(GR_LI[k][0]) for k in which.tolist()], dtype=DTYPE)
    return DwbaCase(
        target=target, Z=Z, A=A, e_inc_mev=float(e_inc_mev),
        level_index=torch.as_tensor(lv.index),
        e_mev=torch.as_tensor(lv.e_mev, dtype=DTYPE),
        spin=torch.as_tensor(spin, dtype=DTYPE),
        parity=torch.as_tensor(par, dtype=torch.int64),
        vibbeta=torch.as_tensor(lv.vibbeta, dtype=DTYPE),
        deformation_length=cs.struct.deftype == "D",
        gr_which=torch.as_tensor(which),
        gr_e_mev=gr.e_mev.detach()[which].clone(),
        gr_spin=lsp,
        gr_parity=torch.tensor([int((-1) ** int(x)) for x in lsp.tolist()], dtype=torch.int64),
        gr_vibbeta=gb,
    )


def dwba_case(omp, case: DwbaCase, *, refine: int = 4, **kw) -> tuple[Tensor, Tensor]:
    """(discrete cross sections, giant-resonance cross sections) in mb for one `DwbaCase`.

    ECIS is fed the discrete levels and the giant resonances in one deck (directecis.f90:224-243),
    so they share a solve; here they share the distorted waves through two calls with the same
    grid, which is the same statement.

    TALYS: directecis.f90:1 (directecis), directread.f90:1 (directread)
    Test: A-direct
    """
    from physics.hf.ecis.dwba_nx2 import case_cross_sections

    got = case_cross_sections(omp, case, refine=refine, **kw)
    if got is not None:  # NATIVEX2: both lists in one compiled deck (ecis/dwba_nx2.py)
        return got
    a = dwba_cross_sections(
        omp, case.Z, case.A, case.e_inc_mev, case.e_mev, case.spin, case.parity,
        case.vibbeta, case.deformation_length, refine=refine, **kw,
    )
    if case.gr_which.numel() == 0:
        return a.xs_mb, torch.zeros(0, dtype=DTYPE)
    b = dwba_cross_sections(
        omp, case.Z, case.A, case.e_inc_mev, case.gr_e_mev, case.gr_spin, case.gr_parity,
        case.gr_vibbeta, case.deformation_length, refine=refine, **kw,
    )
    return a.xs_mb, b.xs_mb


__all__ = [
    "DwbaCase", "DwbaResult", "distorted_waves", "dwba_case", "dwba_cross_sections",
    "prepare_case",
]
