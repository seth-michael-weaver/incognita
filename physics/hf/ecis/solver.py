"""Coupled-channels radial solver: integrates the N coupled radial equations of the symmetric
rotational model, matches to the asymptotic solutions and returns the S-matrix, the transmission
coefficients and the reaction, total, shape-elastic and direct inelastic cross sections.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.
ECIS-06 (`ecist.f`) is by J. Raynal and ships inside the TALYS repository under its MIT license.
What is taken from it here is the channel kinematics (`lecl`, `khco`), the integration grid
(`lect`, through T5's `ecis_grid`) and the definitions of the S-matrix and the cross sections
(`scam`, `resu`). The integrator is NOT a port of ECIS's sequential-iteration/Pade machinery
(`cora`, 1,370 lines): as T5 argued for the single-channel problem, the coupled system has one
solution and any converged integrator finds it, so this is a matrix Numerov with N independent
solutions and an exact asymptotic match.

Task: T13 (physics/hf/CONTRACT.md §7). Acceptance test: A-inc (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    ecist.f:3332 (lecl)
    ecist.f:5464 (khco)
    ecist.f:15232 (mtch)
    ecist.f:18859 (scam)
    ecist.f:20513 (resu)

Line numbers of anchors follow Python's `str.splitlines()`; `grep -n` gives numbers 30 lower.

Closed channels (every excited member of the band, at every incident energy below its excitation
energy -- i.e. most of the reference grid) are matched to the exponentially decaying Riccati-Bessel
function of imaginary argument and their outgoing normalisation is divided out, so the matching
matrix stays conditioned while the decay boundary condition is exact.
"""

from __future__ import annotations

import math
import os
from collections import OrderedDict
from dataclasses import dataclass

import torch
from torch import Tensor

from physics.hf import native as _native
from physics.hf.ecis import ccnative as _ccnative
from physics.hf.core.tensors import DTYPE
from physics.hf.core.units import MB_PER_FM2
from physics.hf.ecis.coupling import ChannelSet
from physics.hf.ecis.formfactor import FormFactors
from physics.hf.omp.schrodinger import (
    ECIS_CCZ_MEV_FM,
    ECIS_CHB_MEV_FM,
    ECIS_CK,
    ECIS_CM_MEV,
    coulomb_functions,
    coulomb_functions_many,
)

CDTYPE = torch.complex128


@dataclass(frozen=True)
class ChannelKinematics:
    """Per-level channel kinematics at one incident energy axis (E,). `ecm_mev` and `k_fm` are
    (E, NLEV); `open_` marks ecm > 0. `mu_coef` is (E,) and channel-independent, because ECIS
    computes `amr` once from the *incident* channel (khco-057) and `lo(95)` sets amrm = amrd.
    """

    ecm_mev: Tensor
    k_fm: Tensor
    kappa2: Tensor  # k^2 with its sign: negative for a closed channel
    eta: Tensor
    open_: Tensor
    mu_coef: Tensor


def channel_kinematics(
    e_lab_mev: Tensor, m_proj_amu: float, m_targ_amu: float, z_prod: float, e_level_mev: Tensor
) -> ChannelKinematics:
    """ECIS's channel kinematics for a coupled set: the c.m. energy of level b is the incident
    c.m. energy minus its excitation energy (lecl-146, `wv(3,iv) = wv(3,1) - e`), while the
    relativistic `amr` and therefore the reduced mass are taken once from the incident channel
    (khco-057), so the coefficient of the potential is the same in every channel.

    TALYS: ecist.f:5464 (khco)
    Test: A-inc
    """
    cm = ECIS_CM_MEV
    m1, m2 = float(m_proj_amu), float(m_targ_amu)
    e = e_lab_mev.to(DTYPE)
    ecm1 = cm * (torch.sqrt((m1 + m2) ** 2 + 2.0 * m2 * e / cm) - m1 - m2)
    amr = ecm1 / cm + m1 + m2  # (E,)
    ecm = ecm1[:, None] - e_level_mev[None, :].to(DTYPE)  # (E, NLEV)
    x = ecm / cm
    k2 = (
        0.125
        * ECIS_CK
        * ecm
        * (x + 2.0 * m1 + 2.0 * m2)
        * (x + 2.0 * m1)
        * (x + 2.0 * m2)
        / amr[:, None] ** 2
    )
    amrd = (amr**4 - (m1**2 - m2**2) ** 2) / (4.0 * amr**3)
    k = torch.sqrt(k2.abs())
    eta = cm * ECIS_CCZ_MEV_FM * amrd[:, None] * z_prod / k.clamp_min(1.0e-30) / ECIS_CHB_MEV_FM**2
    return ChannelKinematics(
        ecm_mev=ecm, k_fm=k, kappa2=k2, eta=eta, open_=ecm > 0.0, mu_coef=ECIS_CK * amrd
    )


def _riccati_k(lmax: int, x: Tensor) -> tuple[Tensor, Tensor]:
    """The decaying Riccati-Bessel function of imaginary argument, khat_l(x) = x k_l(x), and
    d khat_l / dx, for l = 0..lmax. khat_0 = e^-x, khat_1 = e^-x (1 + 1/x),
    khat_{l+1} = khat_{l-1} + (2l+1) khat_l / x, and khat_l' = (l+1) khat_l / x - khat_{l+1}.
    Used as the outgoing solution of a closed channel (u'' = (kappa^2 + l(l+1)/r^2) u).
    """
    x = x.clamp_min(1.0e-30)
    f = [torch.exp(-x), torch.exp(-x) * (1.0 + 1.0 / x)]
    for l in range(1, lmax + 1):  # noqa: E741
        f.append(f[l - 1] + (2 * l + 1) * f[l] / x)
    ff = torch.stack(f[: lmax + 2], dim=-1)  # (..., lmax+2)
    lv = torch.arange(lmax + 1, dtype=DTYPE, device=x.device)
    d = (lv + 1.0) * ff[..., : lmax + 1] / x[..., None] - ff[..., 1 : lmax + 2]
    return ff[..., : lmax + 1], d


def _asymptotic(kin: ChannelKinematics, ch: ChannelSet, rmatch_fm: Tensor,
                coulomb=None) -> tuple[Tensor, ...]:
    """H^+ = G + iF and H^- = G - iF at the matching radius for every channel, with d/dr, plus the
    per-channel scale that was divided out. A closed channel gets H^+ = the decaying Riccati-Bessel
    function and H^- = 0, which is the statement that it carries no incoming flux and no growing
    component.
    """
    lev, l = ch.level, ch.l  # noqa: E741
    k = kin.k_fm[:, lev]  # (E, N)
    op = kin.open_[:, lev]
    eta = kin.eta[:, lev]
    rm = rmatch_fm[:, None].expand_as(k)
    lmax = int(l.max())
    rho = (k * rm).reshape(-1)
    F, dF, G, dG = coulomb if coulomb is not None else coulomb_functions(
        eta.reshape(-1).detach(), rho.detach(), lmax)
    idx = l[None, :].expand_as(k).reshape(-1, 1)
    Fv = F.gather(1, idx).reshape(k.shape)
    Gv = G.gather(1, idx).reshape(k.shape)
    dFv = dF.gather(1, idx).reshape(k.shape) * k  # d/dr
    dGv = dG.gather(1, idx).reshape(k.shape) * k
    hp = torch.complex(Gv, Fv)
    hm = torch.complex(Gv, -Fv)
    dhp = torch.complex(dGv, dFv)
    dhm = torch.complex(dGv, -dFv)
    if bool(op.all()):
        # SPEEDT3: every `where` below then selects its first argument element by element and
        # `scale` is 1, so the closed-channel branch -- `_riccati_k`'s lmax-long Python recurrence,
        # run once per (J, parity) block -- is not needed. Exactly the values the `where`s give.
        return hp, dhp, hm, dhm, torch.ones_like(Gv), op
    kk, dkk = _riccati_k(lmax, (k * rm).reshape(-1))
    kv = kk.gather(1, idx).reshape(k.shape)
    dkv = dkk.gather(1, idx).reshape(k.shape) * k
    scale = torch.where(op, torch.ones_like(kv), kv.abs().clamp_min(1.0e-300))
    hp = torch.where(op, hp, torch.complex(kv, torch.zeros_like(kv)) / scale)
    dhp = torch.where(op, dhp, torch.complex(dkv, torch.zeros_like(dkv)) / scale)
    hm = torch.where(op, hm, torch.zeros_like(hm))
    dhm = torch.where(op, dhm, torch.zeros_like(dhm))
    return hp, dhp, hm, dhm, scale, op


STABILISE_EVERY = 10  # radial steps between two stabilisations of the solution matrix

# CCNUMEROV.  ECIS integrates the coupled radial equations with its *modified* Numerov, not the
# plain one.  For u'' = M u and T = h**2 M the exact second difference of a constant-potential
# solution is 2(cosh kh - 1) u = (T + T**2/12 + T**3/360 + ...) u, and `ecist.f::inch` keeps the
# first two terms explicitly (inch-133..147 builds V - V*V/12 with V = -T, inch-155..162 steps
#     u_{i+1} = 2 u_i - u_{i-1} + (T_i + T_i**2/12) u_i,
# i.e. 12 c M u + 12 c**2 M (M u) with c = h**2/12).  The plain Numerov the port used instead is
# the implicit (1 - T/12) u_{i+1} = (2 + 5T/6) u_i - (1 - T/12) u_{i-1}, whose h**6 truncation is
# -v**3/240 against the modified scheme's +v**3/360 (ecis-113/ecis-114): opposite signs, so at
# ECIS's own step the two answers differ by ~T**3/144 per step and the port could not sit on
# ECIS's.  That is FISSC2's diagnosis and the reason it had to halve the step below 50 keV.
#
# The modified step has no implicit matrix: two products replace a factorise-and-solve, and the
# single-channel kernels of the port already use it (`native/hfnative.c:647`).  ECIS's lo(26)
# stabilisation (the further +T**3/360 on the real diagonal, inch-146) is OFF for the incident
# calculation (`incidentecis.f90:197`), so this is the two-term scheme.
#
# `HF_CC_MODNUM=0` restores the plain Numerov: the A/B lever, and what every pre-CCNUMEROV
# measurement in docs/results was taken with.
def modified_numerov() -> bool:
    """Whether the radial loops step ECIS's modified Numerov (the default) or the plain one.

    TALYS: ecist.f:18604 (inch)
    Test: tests/hf/test_ccnumerov.py
    """
    return os.environ.get("HF_CC_MODNUM", "1") != "0"


_KEEP_SOLUTIONS = ("umm1", "um", "ump1", "sp1", "sm1")


def _stabilise(u_cur, u_prev, keep, hist):
    """Re-orthogonalise the N independent solutions, ECIS's `lo(42)` ("Schmidt's orthogonalisation
    of solutions", calx-036, applied every `jsx` points at inch-170).

    Integrated outward through the centrifugal barrier, every solution is eventually dominated by
    the same fastest-growing mode, so the columns of U go numerically parallel and `U' U^-1` at the
    matching radius is noise. The remedy is exact rather than approximate: the Numerov recursion
    never mixes COLUMNS, so replacing U by U C for any invertible C -- here C = R^-1 from the QR of
    the current U, which makes the columns orthonormal -- is the same set of solutions, and
    U' U^-1 is invariant under it. Every stored matrix of solutions gets the same C.

    Without it the port is fine on ECIS's own step but falls apart on a refined one, where the
    barrier has more points to grow through: at `refine = 4` the weakest coupled level of Er166
    came back 1e9 times too large, with sigma_tot still right to 4e-3.

    TALYS: ecist.f:18604 (inch)
    Test: A-inc
    """
    q, r = torch.linalg.qr(u_cur)
    if not bool(torch.isfinite(r).all()):
        return u_cur, u_prev, keep, hist
    d = torch.diagonal(r, dim1=-2, dim2=-1).abs()
    if float(d.min()) <= 0.0:
        return u_cur, u_prev, keep, hist

    def t(x):
        return torch.linalg.solve_triangular(r, x, upper=True, left=False)

    keep = {k: (t(v) if k in _KEEP_SOLUTIONS else v) for k, v in keep.items()}
    return q, t(u_prev), keep, [t(x) for x in hist]


_FD_CACHE: dict[int, Tensor] = {}


def _fd_weights(npts: int) -> tuple[Tensor, Tensor, Tensor]:
    """Weights of h du/dr at r_{i+1}, r_i and r_{i-1} from the `npts` nodes
    r_{i+1}, r_i, ..., r_{i+2-npts}, i.e. from the points an outward Numerov integration already
    has plus the one it is about to produce.

    ECIS uses a CENTRED 7-point formula for the same derivative (insi-245) because it iterates
    over the whole solution; the port integrates once, so it uses the one-sided stencil of the
    same 7 points. Both are O(h**6) in `h du/dr`, and the derivative enters the Numerov step
    multiplied by h**2/12, so the difference between them is O(h**8) -- below Numerov's own
    O(h**6) truncation, which is the error the port is deliberately sharing with ECIS.
    """
    if npts in _FD_CACHE:
        return _FD_CACHE[npts]
    import numpy as np

    nodes = np.arange(0.0, -float(npts), -1.0)
    vand = np.vander(nodes, npts, increasing=True).T
    out = []
    for x0 in (0.0, -1.0, -2.0):
        rhs = np.array([0.0] + [q * x0 ** (q - 1) for q in range(1, npts)])
        out.append(np.linalg.solve(vand, rhs))
    _FD_CACHE[npts] = torch.tensor(np.stack(out), dtype=DTYPE).to(CDTYPE)
    return _FD_CACHE[npts]


def _block_operators(ch: ChannelSet, ff: FormFactors, kin: ChannelKinematics, r_fm: Tensor):
    """M(r) of one (J, parity) block at every grid point, (E, R, N, N), and the matrix of the
    derivative coupling (the same shape) or None below `soswitch`; `smatrix`'s set-up, shared with
    `smatrix_blocks`.

    TALYS: ecist.f:14643 (quan)
    Test: A-inc
    """
    lev = ch.level
    k2 = kin.kappa2[:, lev]  # (E, N)
    mu = kin.mu_coef[:, None]  # (E, 1)
    cent = (ch.l.to(DTYPE) * (ch.l.to(DTYPE) + 1.0))[None, :]  # (1, N)
    cpl = ch.coupling.to(CDTYPE)  # (NLAM, N, N); the lambda = 0 slice is the identity
    ls2 = ch.ls2.to(CDTYPE)[None, :]
    muc = mu.to(CDTYPE)
    mu4 = muc[:, :, None, None]
    deformed_so = ch.so_deriv_coef is not None and ff.so_r2 is not None
    # M(r) at every grid point in one batched contraction, (E, R, N, N): the radial loop is
    # Python-bound, not flop-bound, so building it per step costs more than holding it.
    diag = (
        cent[:, None, :] / r_fm[:, :, None] ** 2
        - k2[:, None, :]
        + (mu * ff.coulomb)[:, :, None]
    ).to(CDTYPE) + (muc * ls2)[:, None, :] * ff.spin_orbit[:, 0, :][:, :, None]
    # SPEEDT3: the same expressions, written so that the (E, R, N, N) result is allocated once and
    # every later term lands in it (`mul_` / `add_` on the whole array, `add_` on its diagonal
    # view instead of a full-size add of `diag_embed`'s mostly-zero array). Bit-identical --
    # checked element by element on 509 real blocks of Hf-179 and Ca-40, signed zeros included --
    # and it is worth a quarter of a deformed target's coupled channels, where this function held
    # five arrays of that size at once.
    mmat = torch.einsum("elr,lij->erij", ff.central.to(CDTYPE), cpl)
    mmat.mul_(mu4)
    nmat = None
    if deformed_so:
        so1c, so2c = ch.so_grad_coef.to(CDTYPE), ch.so_r2_coef.to(CDTYPE)
        sodc = ch.so_deriv_coef.to(CDTYPE)
        so_grad, so_r2 = ff.so_grad.to(CDTYPE), ff.so_r2.to(CDTYPE)
        extra = torch.einsum("elr,lij->erij", so_grad, so1c)
        extra.add_(torch.einsum("elr,lij->erij", so_r2, so2c))
        extra.mul_(mu4)
        mmat.add_(extra)
        del extra
        nmat = torch.einsum("elr,lij->erij", so_r2, sodc)
        nmat.mul_(mu4)
    mmat.diagonal(dim1=-2, dim2=-1).add_(diag)
    return mmat, nmat


def smatrix(
    ch: ChannelSet,
    ff: FormFactors,
    kin: ChannelKinematics,
    h_fm: Tensor,
    nmatch: Tensor,
    r_fm: Tensor,
    minus_identity: bool = False,
) -> tuple[Tensor, Tensor]:
    """The S-matrix of one (J, parity) block, (E, N, N), flux-normalised so that it is symmetric
    and sum_c |S_{c c0}|^2 <= 1, plus the open-channel mask (S - 1 with `minus_identity`, see
    `_match`).

    The coupled equations are u'' = M(r) u with
    M_{cc'} = delta_{cc'} (l_c(l_c+1)/r^2 - k_c^2 + mu (V_C + 2 l.s_c V^so_0))
              + mu sum_lambda A^lambda_{cc'} V^central_lambda(r)
    integrated by the matrix Numerov from N independent solutions regular at the origin
    (u_c^(m)(h) = delta_{cm} h^(l_c+1)) and matched at r = nmatch * h.

    Above `soswitch` (`lo(13) = T`) the spin-orbit is deformed too and three terms join, all of
    them on the SAME geometrical coefficient as the central multipole (`quan`):

        M_{cc'} += mu sum_lambda [ so_grad^lambda_{cc'} V^so-grad_lambda(r)
                                 + so_r2^lambda_{cc'}   V^so-r2_lambda(r) ]
        u''_c   += mu sum_lambda so_deriv^lambda_{cc'} V^so-r2_lambda(r) * r du_{c'}/dr

    The last one is ECIS's "derivative coupling", and it is why ECIS switches from the direct
    solution of the coupled equations to its own iteration above the switch
    (`incidentecis.f90:280-287` sets `ecis1(21:21) = 'F'` there). The port keeps one outward pass
    and makes the step implicit instead: `r du/dr` at the three points the Numerov step needs is
    written on the nodes the integration already has plus the unknown one, so the u_{i+1} part
    joins the matrix that is inverted anyway and nothing is iterated.

    TALYS: ecist.f:15232 (mtch)
    Test: A-inc
    """
    n_e, n = r_fm.shape[0], ch.level.numel()
    mmat, nmat = _block_operators(ch, ff, kin, r_fm)
    deformed_so = nmat is not None
    eye = torch.eye(n, dtype=CDTYPE)

    def m_at(i: int) -> Tensor:
        """M(r_i) of u'' = M u + (derivative couplings), (E, N, N)."""
        return mmat[:, i]

    def nhat_at(i: int) -> Tensor:
        """The matrix that multiplies `r du/dr` at r_i (quan-352 on the r**-2 form factor)."""
        return nmat[:, i]

    nmax = int(nmatch.max()) + 2
    c = (h_fm**2 / 12.0)[:, None, None].to(CDTYPE)
    u_prev = torch.zeros((n_e, n, n), dtype=CDTYPE)
    u_cur = torch.diag_embed(h_fm[:, None] ** (ch.l.to(DTYPE) + 1.0)[None, :]).to(CDTYPE)
    m_prev, m_cur = None, m_at(0)
    nh_prev, nh_cur = None, nhat_at(0) if deformed_so else None
    hist: list[Tensor] = [u_cur]  # hist[k] is u at index i-k, most recent first
    zero = torch.zeros((n_e, n, n), dtype=CDTYPE)
    keep = {
        k: zero.clone()
        for k in ("umm1", "um", "ump1", "mmm1", "mmp1", "sp1", "sm1")
    }
    modnum = modified_numerov() and not deformed_so
    c12, c144 = 12.0 * c, 12.0 * c * c
    for i in range(nmax):
        m_next = m_at(i + 1)
        if modnum:  # CCNUMEROV: ECIS's explicit modified step, nothing to invert
            mu_c = torch.matmul(m_cur, u_cur)
            u_next = (2.0 * u_cur - u_prev) + c12 * mu_c + c144 * torch.matmul(m_cur, mu_c)
        if not modnum:
            rhs = 2.0 * (u_cur + 5.0 * c * torch.matmul(m_cur, u_cur))
            if m_prev is not None:
                rhs = rhs - (u_prev - c * torch.matmul(m_prev, u_prev))
            lhs = eye - c * m_next
        if deformed_so:
            nh_next = nhat_at(i + 1)
            wt = _fd_weights(min(7, i + 3))  # (3, npts): rows are r_{i+1}, r_i, r_{i-1}
            top = min(wt.shape[1] - 1, len(hist))
            use_m1 = nh_prev is not None and i != 0
            fac = torch.tensor(
                [i + 2.0, 10.0 * (i + 1.0), float(i) if use_m1 else 0.0], dtype=DTYPE
            )
            nh3 = torch.stack((nh_next, nh_cur, nh_prev if use_m1 else nh_cur))
            fac4 = fac[:, None, None, None].to(CDTYPE)
            if top:
                v3 = torch.tensordot(wt[:, 1 : top + 1], torch.stack(hist[:top]), dims=1)
                prod = torch.matmul(nh3, v3)
                rhs = rhs + c * (fac4 * prod).sum(0)
            imp = (fac4 * wt[:, 0, None, None, None] * nh3).sum(0)
            lhs = lhs - c * imp
        if not modnum:
            u_next = torch.linalg.solve(lhs, rhs)
        hit = nmatch == i
        if bool(hit.any()):
            at = hit[:, None, None]
            keep["um"] = torch.where(at, u_cur, keep["um"])
            keep["umm1"] = torch.where(at, u_prev, keep["umm1"])
            keep["ump1"] = torch.where(at, u_next, keep["ump1"])
            keep["mmm1"] = torch.where(at, m_prev if m_prev is not None else m_cur, keep["mmm1"])
            keep["mmp1"] = torch.where(at, m_next, keep["mmp1"])
            if deformed_so:
                # the derivative-coupling part of u'' at the two matching neighbours, which the
                # Numerov-consistent derivative below needs as much as M u
                s3 = torch.matmul(nh3, u_next) * wt[:, 0, None, None, None]
                if top:
                    s3 = s3 + prod
                s3 = fac4 * s3
                keep["sp1"] = torch.where(at, s3[0], keep["sp1"])
                keep["sm1"] = torch.where(at, s3[2], keep["sm1"])
        if deformed_so:
            nh_prev, nh_cur = nh_cur, nh_next
            hist.insert(0, u_next)
            del hist[6:]
        u_prev, u_cur, m_prev, m_cur = u_cur, u_next, m_cur, m_next
        if i % STABILISE_EVERY == STABILISE_EVERY - 1:
            u_cur, u_prev, keep, hist = _stabilise(u_cur, u_prev, keep, hist)
    return _match(ch, kin, h_fm, nmatch, c, keep, minus_identity=minus_identity)


def _match(ch: ChannelSet, kin: ChannelKinematics, h_fm: Tensor, nmatch: Tensor, c: Tensor,
           keep: dict, coulomb=None, minus_identity: bool = False) -> tuple[Tensor, Tensor]:
    """`smatrix`'s matching of the solutions kept around the matching radius to the asymptotic
    ones, shared with `smatrix_blocks`. `coulomb` optionally carries `_asymptotic`'s Coulomb
    functions, computed for many blocks at once (`coulomb_functions_many`, bit-identical).

    `minus_identity=True` returns D = S - 1 on the open channels instead of S (CCFAST2). It is
    solved as its own linear system, (L H+ - H+') D = L (H- - H+) - (H- - H+)', whose right-hand
    side is -2i (L F - F') on an open channel: H- - H+ is exact in floating point (the real parts
    are the same number), so nothing cancels. S = 1 + D formed afterwards would lose every digit
    of a nearly unitary S that `1 - sum |S|^2` needs; see `accumulate`.

    TALYS: ecist.f:15232 (mtch), ecist.f:18859 (scam)
    Test: A-inc
    """
    lev = ch.level
    rm = h_fm * (nmatch.to(DTYPE) + 1.0)
    um, ump1, umm1 = keep["um"], keep["ump1"], keep["umm1"]
    ddp1 = torch.matmul(keep["mmp1"], ump1) + keep["sp1"]
    ddm1 = torch.matmul(keep["mmm1"], umm1) + keep["sm1"]
    du = ((ump1 - 2.0 * c * ddp1) - (umm1 - 2.0 * c * ddm1)) / (2.0 * h_fm[:, None, None].to(CDTYPE))
    # one more column normalisation right at the matching radius: L = U' U^-1 is invariant under
    # it and the condition number is not
    cn = um.abs().amax(dim=1, keepdim=True).clamp_min(1.0e-300)
    um, du = um / cn, du / cn
    hp, dhp, hm, dhm, scale, op = _asymptotic(kin, ch, rm, coulomb)
    # L = U' U^-1, then (L H+ - H+') S~ = L H- - H-'
    L = torch.linalg.solve(um.transpose(1, 2), du.transpose(1, 2)).transpose(1, 2)
    A = L * hp[:, None, :] - torch.diag_embed(dhp)
    if minus_identity:
        B = L * (hm - hp)[:, None, :] - torch.diag_embed(dhm - dhp)
    else:
        B = L * hm[:, None, :] - torch.diag_embed(dhm)
    st = torch.linalg.solve(A, B) / scale[:, :, None]
    k = kin.k_fm[:, lev]
    w = torch.sqrt(k[:, :, None] / k[:, None, :].clamp_min(1.0e-30))
    mask = (op[:, :, None] & op[:, None, :]).to(CDTYPE)
    return st * w.to(CDTYPE) * mask, op


# ------------------------------------------------------------- many (J, parity) blocks at once
# SPEEDT. `sum_blocks` spends its time in the radial loop of one block after another: ~90 steps
# of two products and one solve on (E, N, N) matrices, and most blocks of a target share the same
# channel count N (every total J above the band's largest spin couples the same N channels).
# `smatrix_blocks` stacks the blocks of one N on a leading axis and runs their loops together.
# Bit-identical to `smatrix` block by block, because
#   * at one thread MKL's batched matmul / solve / qr / solve_triangular are the same kernel per
#     matrix whatever the batch (checked; zero-padding a matrix to a larger N is NOT, so blocks of
#     different N never share a batch), and
#   * every element-wise operation of the step is exact to the element whatever the array layout:
#     complex add/sub, and products by the real-valued complex factors c = h**2/12, 2, 5 and the
#     finite-difference weights (the imaginary part of the factor is exactly 0, so a fused and an
#     unfused multiply agree).
# It also drops work whose result is never read: M_{i-1} u_{i-1} is the product of the previous
# step unless a stabilisation replaced u in between, and before any energy has reached its
# matching point the kept solutions are zeros that the capture overwrites whole, so the
# stabilisation does not transform them. The set-up (`_block_operators`) and the matching
# (`_match`) run per block, exactly as `smatrix` runs them.

_BLOCK_BATCH_BYTES = 256 * 2**20  # stacked operators per batch


def _stabilise_blocks(u_cur, u_prev, keep, hist, captured: bool):
    """`_stabilise` for a (B, E, N, N) stack of blocks: each block keeps its own decision."""
    q, r = torch.linalg.qr(u_cur)
    n_b = u_cur.shape[0]
    d = torch.diagonal(r, dim1=-2, dim2=-1).abs()
    ok = torch.isfinite(r).reshape(n_b, -1).all(1) & (d.reshape(n_b, -1).amin(1) > 0.0)
    every = bool(ok.all())
    if not every and not bool(ok.any()):
        return u_cur, u_prev, keep, hist
    ok4 = ok[:, None, None, None]

    def t(x):
        y = torch.linalg.solve_triangular(r, x, upper=True, left=False)
        return y if every else torch.where(ok4, y, x)

    names = _KEEP_SOLUTIONS if captured else ()
    keep = {k: (t(v) if k in names else v) for k, v in keep.items()}
    return (q if every else torch.where(ok4, q, u_cur)), t(u_prev), keep, [t(x) for x in hist]


def _numerov_blocks(mm: Tensor, nm: Tensor | None, u_cur: Tensor, h_fm: Tensor,
                    nmatch: Tensor) -> dict:
    """`smatrix`'s radial loop for a stack of blocks: `mm` (and `nm`) are (R, B, E, N, N), `u_cur`
    the (B, E, N, N) solutions at r_1. Returns `keep` with a leading block axis."""
    n = u_cur.shape[-1]
    deformed_so = nm is not None
    nmax = int(nmatch.max()) + 2
    c = (h_fm**2 / 12.0)[:, None, None].to(CDTYPE)
    eye = torch.eye(n, dtype=CDTYPE)
    u_prev = torch.zeros_like(u_cur)
    m_prev, m_cur = None, mm[0]
    nh_prev, nh_cur = None, nm[0] if deformed_so else None
    hist: list[Tensor] = [u_cur]
    zero = torch.zeros_like(u_cur)
    keep = {k: zero.clone() for k in ("umm1", "um", "ump1", "mmm1", "mmp1", "sp1", "sm1")}
    hits = {int(v) for v in nmatch.tolist()}
    captured = False
    mu_prev = None
    modnum = modified_numerov() and not deformed_so
    c12, c144 = 12.0 * c, 12.0 * c * c
    for i in range(nmax):
        m_next = mm[i + 1]
        mu_cur = torch.matmul(m_cur, u_cur)
        if modnum:  # CCNUMEROV
            u_next = (2.0 * u_cur - u_prev) + c12 * mu_cur + c144 * torch.matmul(m_cur, mu_cur)
        if not modnum:
            rhs = 2.0 * (u_cur + 5.0 * c * mu_cur)
            if m_prev is not None:
                if mu_prev is None:
                    mu_prev = torch.matmul(m_prev, u_prev)
                rhs = rhs - (u_prev - c * mu_prev)
            lhs = eye - c * m_next
        if deformed_so:
            nh_next = nm[i + 1]
            wt = _fd_weights(min(7, i + 3))
            top = min(wt.shape[1] - 1, len(hist))
            use_m1 = nh_prev is not None and i != 0
            fac = torch.tensor(
                [i + 2.0, 10.0 * (i + 1.0), float(i) if use_m1 else 0.0], dtype=DTYPE
            )
            nh3 = torch.stack((nh_next, nh_cur, nh_prev if use_m1 else nh_cur))
            fac4 = fac[:, None, None, None, None].to(CDTYPE)
            if top:
                v3 = torch.stack([torch.tensordot(wt[:, 1 : top + 1], torch.stack([x[b] for x in hist[:top]]), dims=1)
                                  for b in range(u_cur.shape[0])], 1)
                prod = torch.matmul(nh3, v3)
                rhs = rhs + c * (fac4 * prod).sum(0)
            imp = (fac4 * wt[:, 0, None, None, None, None] * nh3).sum(0)
            lhs = lhs - c * imp
        if not modnum:
            u_next = torch.linalg.solve(lhs, rhs)
        if i in hits:
            captured = True
            at = (nmatch == i)[None, :, None, None]
            keep["um"] = torch.where(at, u_cur, keep["um"])
            keep["umm1"] = torch.where(at, u_prev, keep["umm1"])
            keep["ump1"] = torch.where(at, u_next, keep["ump1"])
            keep["mmm1"] = torch.where(at, m_prev if m_prev is not None else m_cur, keep["mmm1"])
            keep["mmp1"] = torch.where(at, m_next, keep["mmp1"])
            if deformed_so:
                s3 = torch.matmul(nh3, u_next) * wt[:, 0, None, None, None, None]
                if top:
                    s3 = s3 + prod
                s3 = fac4 * s3
                keep["sp1"] = torch.where(at, s3[0], keep["sp1"])
                keep["sm1"] = torch.where(at, s3[2], keep["sm1"])
        if deformed_so:
            nh_prev, nh_cur = nh_cur, nh_next
            hist.insert(0, u_next)
            del hist[6:]
        u_prev, u_cur, m_prev, m_cur = u_cur, u_next, m_cur, m_next
        mu_prev = mu_cur
        if i % STABILISE_EVERY == STABILISE_EVERY - 1:
            u_cur, u_prev, keep, hist = _stabilise_blocks(u_cur, u_prev, keep, hist, captured)
            mu_prev = None
    return keep


@torch.no_grad()
def smatrix_blocks(chs: list[ChannelSet], ff: FormFactors, kin: ChannelKinematics, h_fm: Tensor,
                   nmatch: Tensor, r_fm: Tensor, minus_identity: bool = False,
                   exact_bits: bool = True) -> list[tuple[Tensor, Tensor]]:
    """`[smatrix(ch, ff, kin, h_fm, nmatch, r_fm) for ch in chs]`, bit-identical, with the radial
    loops of all blocks of one channel count run together (see above). Not differentiable:
    `sum_blocks` keeps `smatrix` whenever the form factors or the kinematics are on a graph.

    `exact_bits=False` (CCFAST2, `sum_blocks`) lets a block below `soswitch` run on
    `ccnative.cc_block_w`: the same discretised equations in fewer operations, so the same numbers
    to rounding, not to the bit (tests/hf/test_ccfast.py).

    TALYS: ecist.f:15232 (mtch)
    Test: A-inc / tests/hf/test_ecis.py (bitwise against `smatrix`)
    """
    out: list = [None] * len(chs)
    if not chs:
        return out
    n_e = r_fm.shape[0]
    c = (h_fm**2 / 12.0)[:, None, None].to(CDTYPE)
    # `_asymptotic`'s Coulomb functions of every block in one pass
    rm = h_fm * (nmatch.to(DTYPE) + 1.0)
    etas, rhos = [], []
    for ch in chs:
        k = kin.k_fm[:, ch.level]
        etas.append(kin.eta[:, ch.level].reshape(-1))
        rhos.append((k * rm[:, None].expand_as(k)).reshape(-1))
    coul = coulomb_functions_many(etas, rhos, [int(ch.l.max()) for ch in chs])
    groups: dict[int, list[int]] = {}
    for k, ch in enumerate(chs):
        groups.setdefault(int(ch.level.numel()), []).append(k)
    native = _native.lapack()
    fast = not exact_bits and _ccnative.available()
    for n, members in groups.items():
        deformed = chs[members[0]].so_deriv_coef is not None and ff.so_r2 is not None
        if fast:
            for k in members:
                keep = _ccnative.cc_block_w(chs[k], ff, kin, h_fm, nmatch, r_fm)
                out[k] = _match(chs[k], kin, h_fm, nmatch, c, keep, coul[k], minus_identity)
            continue
        if native:
            # SPEEDT3: `_numerov_blocks` compiled, one block at a time, with torch's own MKL
            # routines (tests/hf/test_native.py, bitwise)
            for k in members:
                mmat, nmat = _block_operators(chs[k], ff, kin, r_fm)
                pw = (chs[k].l.to(DTYPE) + 1.0)[None, :]
                u1 = torch.diag_embed(h_fm[:, None] ** pw).to(CDTYPE)
                keep = _native.cc_block(mmat, nmat, u1, h_fm, nmatch, _fd_weights)
                del mmat, nmat
                out[k] = _match(chs[k], kin, h_fm, nmatch, c, keep, coul[k], minus_identity)
            continue
        per = r_fm.shape[1] * n_e * n * n * 16 * (2 if deformed else 1)
        size = max(1, _BLOCK_BATCH_BYTES // max(per, 1))
        if torch.get_num_threads() > 1:
            # MKL's batch invariance holds at one thread only: with more, a batch of blocks is
            # threaded across the batch and a lone block inside its kernels, and the bits differ
            # (Au-197's Tjlinc by 3e-6 relative at 2 threads). One block per loop keeps every
            # thread count bit-identical to `smatrix`.
            size = 1
        for s in range(0, len(members), size):
            part = members[s : s + size]
            ops = [_block_operators(chs[k], ff, kin, r_fm) for k in part]
            mm = torch.stack([m.transpose(0, 1) for m, _ in ops], 1)
            nm = torch.stack([x.transpose(0, 1) for _, x in ops], 1) if deformed else None
            del ops
            u1 = torch.stack([
                torch.diag_embed(h_fm[:, None] ** (chs[k].l.to(DTYPE) + 1.0)[None, :]).to(CDTYPE)
                for k in part])
            keep = _numerov_blocks(mm, nm, u1, h_fm, nmatch)
            del mm, nm
            for b, k in enumerate(part):
                kb = {name: v[b].clone() for name, v in keep.items()}
                out[k] = _match(chs[k], kin, h_fm, nmatch, c, kb, coul[k], minus_identity)
    return out


@dataclass(frozen=True)
class CoupledResult:
    """Coupled-channels results on the incident energy axis (E,). Cross sections in mb."""

    sigma_tot_mb: Tensor
    sigma_reac_mb: Tensor  # TALYS xsreacinc = sigma_tot - sigma_el = absorption + direct
    sigma_abs_mb: Tensor  # sum over entrance channels of 1 - sum_c |S|^2
    sigma_shape_el_mb: Tensor
    sigma_direct_mb: Tensor  # (E, NLEV) direct cross section to each coupled level
    tjl: Tensor  # (E, L+1, 2) elastic T_lj in the contract j order [T(l-1/2), T(l+1/2)]
    n_j: int
    last_j_fraction: float  # the last total J's share of sigma_reac, a convergence witness


def accumulate(
    ch: ChannelSet, s: Tensor, op: Tensor, kin: ChannelKinematics, target_spin: float,
    proj_spin: float, n_lev: int, lmax: int, minus_identity: bool = False,
) -> dict[str, Tensor]:
    """One (J, parity) block's contribution to the cross sections and to T_lj, in units of
    pi/k_1^2 (resu/scam). The statistical weight is (2J+1)/((2I_0+1)(2s+1)); the elastic entrance
    channels are those built on the ground state.

    `Tjlinc(ispin, l) += (2J+1)/((2j+1)(2I_0+1)) T^J_{(0,l,j)}` is incidentread.f90:186's own
    formula for a coupled-channels incident channel, not a choice made here.

    With `minus_identity` (CCFAST2) `s` is D = S - 1 (`_match`) and every quantity is written
    without the leading 1 that cancels: with S_00 = 1 + D_00,
        1 - sum_c |S_c0|^2 = -2 Re D_00 - sum_c |D_c0|^2,    1 - Re S_00 = -Re D_00,
        |1 - S|^2 = |D|^2  (elastic),                          S_b0 = D_b0 (b != 0).
    This is ECIS's own form: `scam` holds the amplitude T = (far, fai) with S = 1 + 2iT and
    takes the transmission as 4 Im T_cc - 4 sum_c' |T_c'c|^2 (scam-160/170), i.e. -2 Re D - |D|^2
    with D = 2iT. From S itself `1 - sum |S|^2` is the difference of two numbers equal to ~1, so a
    T_lj of 1e-12 keeps ~4 digits and one below 1e-16 none; from D what cancels is only the
    squared phase shift (4 delta^2 against T), which is small exactly where T is (high l).

    TALYS: ecist.f:18859 (scam), ecist.f:20513 (resu)
    Test: A-inc
    """
    J = 0.5 * ch.twoJ
    gw = (2.0 * J + 1.0) / ((2.0 * target_spin + 1.0) * (2.0 * proj_spin + 1.0))
    ent = ch.elastic  # openness of the ground-state channel is energy-independent (ecm > 0)
    idx = torch.nonzero(ent).reshape(-1)
    out = {}
    diag = torch.diagonal(s, dim1=1, dim2=2)[:, idx]
    sub = s[:, idx][:, :, idx]
    if minus_identity:
        col2 = (s.real**2 + s.imag**2).sum(dim=1)[:, idx]  # (E, Nent) sum over exit channels
        tcoef = (-2.0 * diag.real - col2).clamp_min(0.0)
        out["reac"] = gw * tcoef.sum(dim=1)
        out["tot"] = 2.0 * gw * (-diag.real).sum(dim=1)
        out["el"] = gw * (sub.real**2 + sub.imag**2).sum(dim=(1, 2))
    else:
        sabs2 = (s.abs() ** 2).sum(dim=1)  # (E, N) sum over exit channels
        tcoef = (1.0 - sabs2)[:, idx].clamp_min(0.0)  # (E, Nent)
        out["reac"] = gw * tcoef.sum(dim=1)
        out["tot"] = 2.0 * gw * (1.0 - diag.real).sum(dim=1)
        delta = torch.eye(idx.numel(), dtype=CDTYPE)[None]
        out["el"] = gw * ((delta - sub).abs() ** 2).sum(dim=(1, 2))
    direct = torch.zeros((s.shape[0], n_lev), dtype=DTYPE)
    for b in range(1, n_lev):
        ex = torch.nonzero(ch.level == b).reshape(-1)
        if ex.numel() == 0:
            continue
        direct[:, b] = gw * (s[:, ex][:, :, idx].abs() ** 2).sum(dim=(1, 2))
    out["direct"] = direct
    tjl = torch.zeros((s.shape[0], lmax + 1, 2), dtype=DTYPE)
    for m, cc in enumerate(idx.tolist()):
        orb = int(ch.l[cc])
        if orb > lmax:
            continue
        jj = float(ch.j[cc])
        col = 1 if jj > orb else 0
        fac = (2.0 * J + 1.0) / ((2.0 * jj + 1.0) * (2.0 * target_spin + 1.0))
        tjl[:, orb, col] = tjl[:, orb, col] + fac * tcoef[:, m]
    out["tjl"] = tjl
    return out


def _rounded_mass(m_amu: float, ecis_rounding: bool) -> float:
    """The target mass as it reaches ECIS's card (`f10.5`), or unrounded."""
    from physics.hf.omp.schrodinger import ecis_card_value

    if not ecis_rounding:
        return float(m_amu)
    return float(ecis_card_value(torch.tensor(m_amu, dtype=DTYPE)))


def _grid_and_kinematics(
    p, m_proj_amu: float, m_targ_amu: float, z_prod: float, e_lab_mev: Tensor,
    level_e_mev: Tensor, refine: int, ecis_rounding: bool,
):
    """(channel kinematics, step, matching index, radial grid) of a coupled set -- ECIS's own grid
    (`lect`, through T5's `ecis_grid`) taken from the INCIDENT channel and optionally refined.

    TALYS: ecist.f:3627 (lect)
    Test: A-inc
    """
    from physics.hf.omp.schrodinger import EcisKinematics, ecis_card_energy, ecis_grid

    e_lab = e_lab_mev.to(DTYPE)
    m_proj = _rounded_mass(m_proj_amu, ecis_rounding)
    m_targ = _rounded_mass(m_targ_amu, ecis_rounding)
    e_lev = level_e_mev.to(DTYPE)
    if ecis_rounding:
        from physics.hf.omp.schrodinger import ecis_card_value

        e_lab = ecis_card_energy(e_lab)
        e_lev = ecis_card_value(e_lev)
    kin = channel_kinematics(e_lab, m_proj, m_targ, z_prod, e_lev)
    grid_kin = EcisKinematics(
        ecm_mev=kin.ecm_mev[:, 0], k_fm=kin.k_fm[:, 0], eta=kin.eta[:, 0], mu_coef=kin.mu_coef
    )
    h, ism, _ = ecis_grid(p, m_targ, grid_kin)
    h = h / refine
    nmatch = (ism * refine - 1).clamp_min(8)
    nmax = int(nmatch.max()) + 3
    r = h[:, None] * torch.arange(1, nmax + 1, dtype=DTYPE)[None, :]
    return kin, h, nmatch, r


BLOCK_AHEAD = 1  # total-J values solved per `smatrix_blocks` call of `sum_blocks` (CCFAST2: 2;
# NATIVEX2: 1, so an energy that leaves the loop has no block solved ahead of it)
QUIET_J = 1  # quiet total-J values an energy needs to leave `sum_blocks` (CCFAST2: 3; NATIVEX2)


def _energy_subset(ff: FormFactors, kin: ChannelKinematics, h: Tensor, nmatch: Tensor, r: Tensor,
                   idx: Tensor):
    """(ff, kin, h, nmatch, r) cut to the energies `idx`, and the radial axis cut to what the
    slowest of them integrates (`_grid_and_kinematics` sizes it `max(nmatch) + 3`). Every field is
    per energy and per radial point, so this changes no value, only which rows are carried."""
    n_r = int(nmatch[idx].max()) + 3

    def cut(t: Tensor | None) -> Tensor | None:
        return None if t is None else t[idx][..., :n_r]

    ff2 = FormFactors(central=cut(ff.central), spin_orbit=cut(ff.spin_orbit),
                      coulomb=cut(ff.coulomb), lambdas=ff.lambdas, so_grad=cut(ff.so_grad),
                      so_r2=cut(ff.so_r2))
    kin2 = ChannelKinematics(ecm_mev=kin.ecm_mev[idx], k_fm=kin.k_fm[idx],
                             kappa2=kin.kappa2[idx], eta=kin.eta[idx], open_=kin.open_[idx],
                             mu_coef=kin.mu_coef[idx])
    return ff2, kin2, h[idx], nmatch[idx], r[idx][:, :n_r]


def sum_blocks(
    make_channels,
    ff: FormFactors,
    kin: ChannelKinematics,
    h: Tensor,
    nmatch: Tensor,
    r: Tensor,
    n_lev: int,
    lmax: int,
    target_spin: float,
    proj_spin: float,
    j_tol: float = 1.0e-10,
) -> CoupledResult:
    """Loop over total J and parity until the reaction cross section converges, summing the
    blocks; shared by the rotational and the vibrational models, which differ only in the channel
    set and the form factors. `make_channels(twoJ, parity)` returns the `ChannelSet`.

    The total J runs over every value of the right integer/half-integer character starting at 0
    (or 1/2), NOT at |I_0 - s|: a channel with j = I_0 reaches J = 0. Starting at |I_0 - s| costs
    Au197's S1 5.8%, because Tjlinc(l=1, j=3/2) is missing its J = 0 term.

    **Convergence is per energy (CCFAST2).** Each energy leaves the loop after `QUIET_J` quiet
    total-J values of its own (`block < j_tol * sigma_reac`), and the blocks of the next J are
    solved only for the energies still in it. ECIS itself runs every J to njmax (TALYS gives it
    conj = 1e-30, ecisinput.f90:105), so any stop is a truncation; NATIVEX2 leaves at the first
    quiet J instead of the third: the blocks it drops are each below 1e-10 of sigma_reac and fall
    with J (Er-166, Lu-175, U-238, Pd-106: every chart channel within 2e-11 of the three-J stop;
    whole nuclides 13-19 % less CPU for the first three). The loop used to run every energy to the
    J the highest one needed: on the chart grid a 1 keV neutron on Nd-150 converges by 2J = 7 and
    was integrated to 2J = 35. A single-energy call and the same energy inside a batch now sum the
    same blocks, so `Cascade.incident` and the direct deck can share one solve
    (`incident._SOLVED`). Blocks are matched as S - 1 (`accumulate`).

    TALYS: ecist.f:20513 (resu)
    Test: A-inc
    """
    n_e = h.shape[0]
    acc = {
        "reac": torch.zeros(n_e, dtype=DTYPE),
        "tot": torch.zeros(n_e, dtype=DTYPE),
        "el": torch.zeros(n_e, dtype=DTYPE),
        "direct": torch.zeros((n_e, n_lev), dtype=DTYPE),
        "tjl": torch.zeros((n_e, lmax + 1, 2), dtype=DTYPE),
    }
    two_j0 = (int(round(2 * target_spin)) + int(round(2 * proj_spin))) % 2
    j_cap = 4 * (lmax + 2) + 1  # the loop below never runs more total-J values than this
    batched = not (torch.is_grad_enabled() and any(
        isinstance(t, Tensor) and t.requires_grad
        for t in (ff.central, ff.spin_orbit, ff.coulomb, ff.so_grad, ff.so_r2, kin.kappa2,
                  kin.k_fm, kin.mu_coef, h, r)))
    if batched and _ccnative.glue_available():
        return _sum_blocks_tasks(make_channels, ff, kin, h, nmatch, r, n_lev, lmax, target_spin,
                                 proj_spin, j_tol, acc, two_j0, j_cap)
    # (twoJ, parity) -> (S - 1, open mask, the energy rows it was solved on) or None
    solved: dict[tuple[int, int], tuple[Tensor, Tensor, Tensor] | None] = {}

    def solve_from(twoJ: int, count: int, rows: Tensor) -> None:
        """Solve the blocks of `count` total-J values from `twoJ` on the energy rows `rows` in one
        `smatrix_blocks` call (SPEEDT). Each block's numbers do not depend on which other blocks
        or energies share its call."""
        keys, chs = [], []
        if hasattr(make_channels, "prefill"):
            make_channels.prefill([(twoJ + 2 * q, par) for q in range(count)
                                   if (twoJ + 2 * q - two_j0) // 2 < j_cap for par in (-1, 1)])
        for q in range(count):
            tj = twoJ + 2 * q
            if (tj - two_j0) // 2 >= j_cap:
                break
            for par in (-1, 1):
                ch = make_channels(tj, par)
                if ch.level.numel() == 0 or not bool(ch.elastic.any()):
                    solved[(tj, par)] = None
                    continue
                keys.append((tj, par))
                chs.append(ch)
        if not chs:
            return
        sub = (ff, kin, h, nmatch, r) if rows.numel() == n_e else _energy_subset(
            ff, kin, h, nmatch, r, rows)
        if batched:
            got = smatrix_blocks(chs, *sub, minus_identity=True, exact_bits=False)
        else:
            got = [smatrix(ch, *sub, minus_identity=True) for ch in chs]
        for key, (s_mat, op) in zip(keys, got, strict=True):
            solved[key] = (s_mat, op, rows)

    active = torch.arange(n_e)
    quiet = torch.zeros(n_e, dtype=torch.int64)
    frac = torch.zeros(n_e, dtype=DTYPE)
    n_j, twoJ = 0, two_j0
    while active.numel():
        block = torch.zeros(active.numel(), dtype=DTYPE)
        for par in (-1, 1):
            if (twoJ, par) not in solved:
                solve_from(twoJ, BLOCK_AHEAD, active)
            got_s = solved.pop((twoJ, par))
            if got_s is None:
                continue
            s_mat, op, rows = got_s
            if rows.numel() != active.numel():
                pos = torch.searchsorted(rows, active)
                s_mat, op = s_mat[pos], op[pos]
            ch = make_channels(twoJ, par)
            got = accumulate(ch, s_mat, op, kin, target_spin, proj_spin, n_lev, lmax,
                             minus_identity=True)
            for key in ("reac", "tot", "el", "direct", "tjl"):
                acc[key] = acc[key].index_add(0, active, got[key])
            block = torch.maximum(block, got["reac"].detach().abs())
        n_j += 1
        ref = acc["reac"].detach()[active].abs()
        q = torch.where((ref > 0) & (block < j_tol * ref), quiet[active] + 1, 0)
        quiet[active] = q
        frac[active] = block / ref.clamp_min(1.0e-300)
        if n_j > 4 * (lmax + 2):
            break
        active = active[q < QUIET_J]
        twoJ += 2
    return _coupled_result(kin, acc, n_j, frac)


# ------------------------------------------------ CCGLUE: the J loop as a (block, energy) task list
# `sum_blocks` with the compiled kernels: every total J asks for an explicit list of `CCTask`s, one
# per (J, parity) block and incident energy still in the loop, and `run_cc_tasks` executes it. A
# task's numbers do not depend on which other tasks share its kernel call (each energy of
# `cc_block_w` / `cc_block_d` integrates, stabilises and matches on its own), so a scheduler may
# split or regroup the list freely -- by block here, one kernel call per block on all its energies;
# by (block, energy) or by thread elsewhere -- and the driver adds the returned contributions in
# task order, which keeps the sums independent of the schedule. Matching and accumulation run in
# C (`ccnative.cc_block_acc`), not as `_match` + `accumulate`'s ~60 torch operations per block.


@dataclass(frozen=True)
class CCTask:
    """One (J, parity) block of `sum_blocks` at one incident-energy row."""

    two_j: int
    parity: int
    energy: int


def cc_tasks(two_j: int, rows: list[int]) -> list[CCTask]:
    """The tasks of total J = two_j/2 on the energy rows still in the loop, parity -1 first (the
    order `sum_blocks` adds the blocks in).

    TALYS: none (scheduling only, no Fortran counterpart)
    Test: tests/hf/test_ccglue.py
    """
    return [CCTask(two_j, par, e) for par in (-1, 1) for e in rows]


def _ccgpu_lookup():
    """SPEED50 CCGPU: `ccgpu.lookup` when the GPU store holds anything, else None (no import)."""
    import sys

    mod = sys.modules.get("physics.hf.ecis.ccgpu")
    return None if mod is None or not mod.active() else mod.lookup


def run_cc_tasks(tasks: list[CCTask], make_channels, ff: FormFactors, kin: ChannelKinematics,
                 h: Tensor, nmatch: Tensor, r: Tensor, n_lev: int, lmax: int, target_spin: float,
                 proj_spin: float, subsets: dict | None = None) -> list[tuple[int, int, Tensor, dict]]:
    """Execute `tasks`, one kernel call per (J, parity) block on the energies its tasks name.
    Returns `(two_j, parity, rows, contributions)` per block that has channels, in the order the
    blocks first appear; `contributions` is `accumulate`'s dict on `rows`. `subsets` memoises
    `_energy_subset` by row tuple across calls.

    TALYS: none (scheduling only, no Fortran counterpart)
    Test: tests/hf/test_ccglue.py
    """
    n_e = h.shape[0]
    groups: dict[tuple[int, int], list[int]] = {}
    for t in tasks:
        groups.setdefault((t.two_j, t.parity), []).append(t.energy)
    if hasattr(make_channels, "prefill"):
        make_channels.prefill(list(groups))
    blocks = []
    for (tj, par), es in groups.items():
        ch = make_channels(tj, par)
        if ch.level.numel() == 0 or not bool(ch.elastic.any()):
            continue
        key = tuple(es)
        sub = None if subsets is None else subsets.get(key)
        if sub is None:
            rows = torch.tensor(es, dtype=torch.int64)
            full = len(es) == n_e and es == list(range(n_e))
            sub = (rows, (ff, kin, h, nmatch, r) if full else _energy_subset(ff, kin, h, nmatch, r,
                                                                             rows))
            if subsets is not None:
                subsets.clear()  # the loop's rows only shrink: one entry is all it re-reads
                subsets[key] = sub
        blocks.append((tj, par, ch, sub))
    if not blocks:
        return []
    etas, rhos = [], []
    for _tj, _par, ch, (_rows, (_ff, kn, hh, nm, _r)) in blocks:
        k = kn.k_fm[:, ch.level]
        rm = hh * (nm.to(DTYPE) + 1.0)
        etas.append(kn.eta[:, ch.level].reshape(-1))
        rhos.append((k * rm[:, None].expand_as(k)).reshape(-1))
    coul = coulomb_functions_many(etas, rhos, [int(b[2].l.max()) for b in blocks])
    out = []
    gpu = _ccgpu_lookup()
    for (tj, par, ch, (rows, sub)), cf in zip(blocks, coul, strict=True):
        # SPEED50 CCGPU: the block's radial loop may already have been integrated on the GPU
        # (`ccgpu.plan`); a miss on any row runs the C kernel as before
        keep = None if gpu is None else gpu(ch, sub)
        got = _ccnative.cc_block_acc(ch, *sub, cf, n_lev, lmax, target_spin, proj_spin, keep=keep)
        out.append((tj, par, rows, got))
    return out


# SPEED50 CCGPU: while `ccgpu.plan` runs, a callable that records each `_sum_blocks_tasks` side
# (its blocks are then integrated on the GPU ahead of the real run); None otherwise.
_PLAN = None


class Planned(Exception):
    """SPEED50 CCGPU: raised by `incident_coupled` once a planning pass has recorded its sides."""


def _sum_blocks_tasks(make_channels, ff, kin, h, nmatch, r, n_lev, lmax, target_spin, proj_spin,
                      j_tol, acc, two_j0, j_cap) -> CoupledResult:
    """`sum_blocks`'s loop on `cc_tasks` / `run_cc_tasks`: the same blocks, the same per-energy
    convergence (`QUIET_J`), the same J cap and the same order of addition.

    TALYS: ecist.f:20513 (resu)
    Test: tests/hf/test_ccglue.py
    """
    n_e = h.shape[0]
    if _PLAN is not None:  # SPEED50 CCGPU: record the side for the GPU, solve nothing
        _PLAN(make_channels, ff, kin, h, nmatch, r, target_spin, two_j0, j_cap)
        return _coupled_result(kin, acc, 0, torch.zeros(n_e, dtype=DTYPE))
    active = torch.arange(n_e)
    quiet = torch.zeros(n_e, dtype=torch.int64)
    frac = torch.zeros(n_e, dtype=DTYPE)
    subsets: dict = {}
    n_j, twoJ = 0, two_j0
    while active.numel():
        rows_l = active.tolist()
        tasks = cc_tasks(twoJ, rows_l) if (twoJ - two_j0) // 2 < j_cap else []
        bmax = torch.zeros(n_e, dtype=DTYPE)
        for _tj, _par, rows, got in run_cc_tasks(tasks, make_channels, ff, kin, h, nmatch, r,
                                                 n_lev, lmax, target_spin, proj_spin, subsets):
            for key in ("reac", "tot", "el", "direct", "tjl"):
                acc[key] = acc[key].index_add(0, rows, got[key])
            bmax[rows] = torch.maximum(bmax[rows], got["reac"].abs())
        block = bmax[active]
        n_j += 1
        ref = acc["reac"][active].abs()
        q = torch.where((ref > 0) & (block < j_tol * ref), quiet[active] + 1, 0)
        quiet[active] = q
        frac[active] = block / ref.clamp_min(1.0e-300)
        if n_j > 4 * (lmax + 2):
            break
        active = active[q < QUIET_J]
        twoJ += 2
    return _coupled_result(kin, acc, n_j, frac)


def _coupled_result(kin: ChannelKinematics, acc: dict, n_j: int, frac: Tensor) -> CoupledResult:
    """`sum_blocks`'s summed blocks in mb."""
    k1 = kin.k_fm[:, 0]
    fac = math.pi / k1**2 * MB_PER_FM2
    direct = fac[:, None] * acc["direct"]
    absorb = fac * acc["reac"]
    return CoupledResult(
        sigma_tot_mb=fac * acc["tot"],
        # ECIS's second `ecis.inccs` number, which incidentread.f90:140 calls xsreacinc, is the
        # total reaction cross section: the flux that leaves the elastic channel, so the direct
        # inelastic to the coupled band counts. Checked against unitarity: sigma_tot - sigma_el -
        # (absorption + direct) is < 5e-12 mb on the whole U238 grid.
        sigma_reac_mb=absorb + direct.sum(dim=1),
        sigma_abs_mb=absorb,
        sigma_shape_el_mb=fac * acc["el"],
        sigma_direct_mb=direct,
        tjl=acc["tjl"],
        n_j=n_j,
        last_j_fraction=float(frac.max()),
    )


_CHANNELS: OrderedDict = OrderedDict()  # memo of `_channels_cached`, least recently used first
_CHANNELS_MAX = 512


def _channels_cached(kind: str, twoJ: int, parity: int, spins: tuple, spin_dtype, parities: tuple,
                     parity_dtype, extra: tuple, lmax: int, proj_spin: float, ahead=()):
    """`coupling.channels` / `coupling.vibrational_channels` for one (J, parity), memoised.

    The channel set and its geometrical coupling (6j, Clebsch-Gordan, reduced matrix elements)
    depend on the band and on lmax, never on the incident energy, and they were half the wall of
    an energy loop over a deformed target. Rebuilt from the same values, so identical.

    `ahead` lists more (twoJ, parity) pairs the caller is about to ask for: the missing ones are
    built together with this one (SPEEDT3, `coupling._channels_many`: one 6j evaluation for all).

    TALYS: ecist.f:14643 (quan)
    Test: A-inc / SPEED0 golden
    """
    from dataclasses import replace

    from physics.hf.ecis.coupling import _channels_many

    base = (kind, spins, spin_dtype, parities, parity_dtype, extra, lmax, proj_spin)
    key = (twoJ, parity, base)
    got = _CHANNELS.get(key)
    if got is not None:
        _CHANNELS.move_to_end(key)
        return got
    if kind == "rot" and not extra[1]:
        # CCFAST2: the set below `soswitch` is the set above it without the three deformed
        # spin-orbit tables (same levels, l, j, 2 l.s and coupling, checked field by field on
        # Nd-150, Hf-179 and U-238), so a run whose grid straddles the switch builds the 6j
        # tables once. Building the spin-orbit tables too costs ~8% of a set.
        full = _channels_cached(kind, twoJ, parity, spins, spin_dtype, parities, parity_dtype,
                                (extra[0], True), lmax, proj_spin, ahead)
        got = replace(full, so_grad_coef=None, so_r2_coef=None, so_deriv_coef=None)
        _CHANNELS[key] = got
        return got
    want = [(twoJ, parity)] + [q for q in ahead if (q[0], q[1], base) not in _CHANNELS
                               and q != (twoJ, parity)]
    ls = torch.tensor(spins, dtype=spin_dtype)
    lp = torch.tensor(parities, dtype=parity_dtype)
    if kind == "rot":
        built = _channels_many("rot", want, ls, lp, lmax, proj_spin, extra)
    elif kind == "vib2":
        built = _channels_many("vib2", want, ls, lp, lmax, proj_spin, extra)
    else:
        lam_vals, lam_dtype = extra
        built = _channels_many("vib", want, ls, lp, lmax, proj_spin,
                               torch.tensor(lam_vals, dtype=lam_dtype))
    for q, ch in zip(want, built, strict=True):
        _CHANNELS[(q[0], q[1], base)] = ch
    while len(_CHANNELS) > _CHANNELS_MAX:
        _CHANNELS.popitem(last=False)
    return built[0]


class _ChannelMaker:
    """`make_channels(twoJ, parity)` for `sum_blocks`, with `prefill` for a batch of pairs."""

    def __init__(self, kind: str, *args):
        self.kind, self.args = kind, args

    def __call__(self, twoJ: int, parity: int):
        return _channels_cached(self.kind, twoJ, parity, *self.args)

    def prefill(self, pairs) -> None:
        if pairs:
            _channels_cached(self.kind, pairs[0][0], pairs[0][1], *self.args, ahead=tuple(pairs))


def solve_rotational(
    p,
    m_proj_amu: float,
    m_targ_amu: float,
    z_prod: float,
    e_lab_mev: Tensor,
    level_e_mev: Tensor,
    level_spin: Tensor,
    level_parity: Tensor,
    rotbeta: Tensor,
    deformation_length: bool,
    kband: float,
    lmax: int,
    proj_spin: float = 0.5,
    refine: int = 1,
    j_tol: float = 1.0e-10,
    ecis_rounding: bool = True,
    deformed_spin_orbit: bool = False,
) -> CoupledResult:
    """Symmetric rotational coupled channels for the incident channel: loops over total J and
    parity until the reaction cross section converges, and sums the blocks.

    `p` holds T4's OMP parameters on the (E,) energy axis; `level_*` the coupled band (level 0 is
    the ground state); `rotbeta` TALYS's `rotpar`; `deformation_length` is `deftype == 'D'`
    (ECIS `lo(6)`). `deformed_spin_orbit` is ECIS's `lo(13)`, which `incidentecis.f90:280-287`
    switches on above `soswitch`; the whole energy axis handed to one call must be on one side of
    the switch, which is what `incident.incident_coupled` arranges.

    TALYS: incidentecis.f90:1 (incidentecis)
    Test: A-inc
    """
    from physics.hf.ecis.formfactor import rotational_form_factors

    kin, h, nmatch, r = _grid_and_kinematics(
        p, m_proj_amu, m_targ_amu, z_prod, e_lab_mev, level_e_mev, refine, ecis_rounding
    )
    ff = rotational_form_factors(
        p, _rounded_mass(m_targ_amu, ecis_rounding), r, rotbeta, deformation_length,
        2 * int(rotbeta.numel()), z_prod, deformed_spin_orbit,
    )
    key = (tuple(level_spin.tolist()), level_spin.dtype, tuple(level_parity.tolist()),
           level_parity.dtype)
    return sum_blocks(
        _ChannelMaker("rot", key[0], key[1], key[2], key[3],
                      (float(kband), bool(deformed_spin_orbit)), int(lmax), float(proj_spin)),
        ff, kin, h, nmatch, r, int(level_spin.numel()), lmax, float(level_spin[0]),
        proj_spin, j_tol,
    )


def solve_vibrational(
    p,
    m_proj_amu: float,
    m_targ_amu: float,
    z_prod: float,
    e_lab_mev: Tensor,
    level_e_mev: Tensor,
    level_spin: Tensor,
    level_parity: Tensor,
    vib_lambda: Tensor,
    vib_beta: Tensor,
    deformation_length: bool,
    lmax: int,
    proj_spin: float = 0.5,
    refine: int = 1,
    j_tol: float = 1.0e-10,
    ecis_rounding: bool = True,
    scheme=None,
    band_beta: Tensor | None = None,
) -> CoupledResult:
    """Vibrational coupled channels for the incident channel (`colltype V`), which is what TALYS
    runs for Ca-40 (incidentecis.f90:261-268) and for the 37 two-phonon sweep nuclides.

    Same machinery as `solve_rotational`; what changes is that the transition form factor is a
    derivative of the potential scaled by the band's `defpar` (`formfactor`), and that the
    coupling matrix has one slice per FORM FACTOR rather than per multipole (`coupling`). ECIS
    never deforms the spin-orbit for a vibrational target -- `incidentecis.f90` only touches
    `ecis1(13:13)` inside the rotational branch -- so there is no `soswitch` in this path and all
    23 reference energies are in scope.

    `scheme` is `vibm.reduced_matrix_elements(...)`: pass it (with `band_beta`, the per-phonon
    `vibbeta`) for a target that has a two-phonon level, i.e. ECIS's `lo(2)` second-order branch
    (`ecis1(2:2) = 'T'`, incidentecis.f90:244). Leave it `None` and the harmonic one-phonon path
    runs untouched, bit for bit.

    TALYS: incidentecis.f90:1 (incidentecis)
    Test: A-inc / G-2PH
    """
    kin, h, nmatch, r = _grid_and_kinematics(
        p, m_proj_amu, m_targ_amu, z_prod, e_lab_mev, level_e_mev, refine, ecis_rounding
    )
    key = (tuple(level_spin.tolist()), level_spin.dtype, tuple(level_parity.tolist()),
           level_parity.dtype)
    if scheme is not None:
        from physics.hf.ecis.formfactor import anharmonic_vibrational_form_factors

        ff = anharmonic_vibrational_form_factors(
            p, _rounded_mass(m_targ_amu, ecis_rounding), r, band_beta, scheme.codes,
            scheme.nbt1, deformation_length, z_prod,
        )
        maker = _ChannelMaker("vib2", key[0], key[1], key[2], key[3], (scheme, scheme.codes),
                              int(lmax), float(proj_spin))
    else:
        from physics.hf.ecis.formfactor import vibrational_form_factors

        ff = vibrational_form_factors(
            p, _rounded_mass(m_targ_amu, ecis_rounding), r, vib_beta, deformation_length, z_prod
        )
        maker = _ChannelMaker("vib", key[0], key[1], key[2], key[3],
                              (tuple(vib_lambda.tolist()), vib_lambda.dtype),
                              int(lmax), float(proj_spin))
    return sum_blocks(
        maker, ff, kin, h, nmatch, r, int(level_spin.numel()), lmax, float(level_spin[0]),
        proj_spin, j_tol,
    )
