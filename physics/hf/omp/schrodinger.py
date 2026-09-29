"""Spherical optical-model solver: integrates the radial Schrodinger equation per (l, j) and
returns transmission coefficients, S-matrix, reaction, total and shape-elastic cross sections.
It replaces ECIS for spherical targets; the numerics (radial step, matching radius, Coulomb wave
functions for charged particles) must reproduce ECIS's T_lj to the A-trans tolerance.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.
ECIS-06 (`ecist.f`) is by J. Raynal and ships inside the TALYS repository under its MIT license;
what is taken from it here is the input convention (card formats, reduced radii scaled by the
target mass in amu), the relativistic kinematics (subroutines lecl and khco) and the potential
form factors (wosa, stdp). The integrator is not a port of ECIS's modified-Numerov/iteration
machinery: a spherical single-channel problem has an exact solution that any converged
integrator reproduces, so this module uses a vectorised Numerov scheme on a finer step and
Coulomb functions from continued fractions (Steed's method) with a Wronskian normalisation.

Task: T5 (physics/hf/CONTRACT.md §7). Acceptance test: A-trans (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    inverseecis.f90:1 (inverseecis)
    incidentecis.f90:1 (incidentecis)
    ecisinput.f90:1 (ecisinput)
    ecist.f:1 (ecist)
    ecist.f:3332 (lecl)
    ecist.f:5464 (khco)
    ecist.f:12950 (wosa)
    ecist.f:14445 (tlnc)
    ecist.f:5775 (fcou)

Line numbers of anchors follow Python's `str.splitlines()` (what tests/hf/test_contract.py
counts); ecist.f contains form feeds, so `grep -n` gives numbers about 30 lower. Line numbers
quoted in prose below are `grep -n` numbers.

Conventions established against the reference dumps (tests/hf/test_optical.py):
  * potential  U(r) = -(V f_V + i W f_W) - 4 (Vd g_Vd + i Wd g_Wd)
                      + (Vso + i Wso) (2 l.s) (1/r) df_so/dr + V_C(r)
    with f = 1/(1+exp((r-R)/a)), g = -a df/dr, R = r0 * M_target^(1/3), M in amu as written on
    the ECIS card (lect: `am3=wv(2,ij)**.33333333333333d0`, ecist.f:3866), and a homogeneously
    charged sphere of radius rc * M^(1/3) for the Coulomb term.
  * ECIS input cards are fixed format (ecisinput.f90: energy f10.5 or es10.3, masses and potential
    parameters f10.5), so ECIS computes with rounded numbers. `ecis_rounding=True` reproduces
    that with a straight-through estimator: the forward value is the rounded one, the gradient
    is that of the unrounded parameter.
"""

from __future__ import annotations

import math
from contextlib import contextmanager
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import torch
from torch import Tensor

from physics.hf.core.constants import PARA as _PARA
from physics.hf.core.constants import PARTICLE_INDEX, nuclide_symbol, talys_constants, talys_structure_path
from physics.hf.core.constants import PARZ as _PARZ
from physics.hf.core.tensors import DTYPE
from physics.hf.core.units import MB_PER_FM2
from physics.hf import native as _native
from physics.hf.omp import omp_nx2 as _nx2omp

if TYPE_CHECKING:
    from physics.hf.input.defaults import Options
    from physics.hf.omp.parameters import OMPParameters

# ECIS-06's own constants (ecist.f:40-42 inside ecist). Deliberately not TALYS's amu: ECIS
# computes kinematics with these, and the port reproduces ECIS.
ECIS_CM_MEV = 931.494043  # atomic mass unit [MeV]
ECIS_CHB_MEV_FM = 197.326968  # hbar c [MeV fm]
ECIS_CZ = 137.03599911  # 1/alpha
ECIS_CCZ_MEV_FM = ECIS_CHB_MEV_FM / ECIS_CZ  # e^2 [MeV fm] (calc: ccz=chb/cz)
ECIS_CK = 2.0 * ECIS_CM_MEV / ECIS_CHB_MEV_FM**2  # (calc: ck=2*cm/chb**2) [fm^-2 MeV^-1 amu^-1]
# ECIS card 5 as TALYS writes it (ecisinput.f90:102): aconv = 1e-10 in columns 41-50
ECIS_ACONV = 1.0e-10

# TALYS particle numbering (1 = n ... 6 = alpha) and constants.f90 tables, from physics.hf.core
_C = talys_constants()
PARSPIN = dict(enumerate(_C["parspin"]))
PARZ = dict(enumerate(_PARZ))
PARA = dict(enumerate(_PARA))
PARMASS_AMU = dict(enumerate(_C["parmass"]))  # as TALYS holds them (single-precision literals)
# columns of the padded j axis (contract §5): number of valid j per particle
NJ = {1: 2, 2: 2, 3: 3, 4: 2, 5: 2, 6: 1}


@dataclass(frozen=True)
class Transmission:
    # (C, particle, E, L, 3) T_lj, dimensionless, padded to 3 j-values: spin-1/2 particles use
    # [T(l-1/2,l), T(l+1/2,l), 0], d uses [T(l-1,l), T(l,l), T(l+1,l)], alpha [T(l), 0, 0]
    tjl: Tensor
    nj: Tensor  # (particle,) int64 number of valid j entries: n,p,t,h 2; d 3; a 1
    sigma_reac_mb: Tensor  # (C, particle, E)
    sigma_tot_mb: Tensor  # (C, particle, E) neutrons only, else NaN
    sigma_shape_el_mb: Tensor  # (C, particle, E) neutrons only, else NaN
    lmax: Tensor  # (C, particle, E) int64


@dataclass(frozen=True)
class EcisKinematics:
    """Relativistic ECIS kinematics for one channel over an energy axis (E,)."""

    ecm_mev: Tensor  # centre-of-mass kinetic energy
    k_fm: Tensor  # wave number [fm^-1]
    eta: Tensor  # Coulomb parameter
    mu_coef: Tensor  # coefficient of U(r) in the radial equation [fm^-2 MeV^-1]


@dataclass(frozen=True)
class RadialSolution:
    """Per (E, L, J) results of the single-channel problem. J index follows `jvalues`."""

    smat: Tensor  # (E, L, J) complex S-matrix (nuclear, relative to Coulomb)
    tlj: Tensor  # (E, L, J) 1 - |S|^2, zero where the (l, j) combination is invalid
    valid: Tensor  # (L, J) bool
    jvalues: Tensor  # (L, J) total j
    kin: EcisKinematics
    rmatch_fm: float
    step_fm: float


# ----------------------------------------------------------------------------- inputs to ECIS
def _straight_through(x: Tensor, y: Tensor) -> Tensor:
    """forward value y, gradient of x (rounding done on ECIS input cards)."""
    return x + (y - x).detach()


#: ECIS reads its parameters off fixed-format input cards, so the port quantises them the same
#: way (`ecis_card_value`). It is a forward-only quantisation -- the gradient is the identity, by
#: the straight-through above -- and that is exactly why DIFFPARAM's finite-difference check has
#: to be able to switch it off: with it on, an f10.5 card resolves `rv` to 1e-5 fm, and a central
#: difference over a step of 1e-3 fm therefore carries a 0.3% quantisation error that has nothing
#: to do with the gradient being checked (measured: `rvadjust` 3.3e-3 relative with, 1e-6
#: without; `v1adjust`, on a 50 MeV depth, is 1.6e-5 either way). Never switch it off to compute
#: a cross section: `test_speed_golden.py` and every A-* gate run with it on, as TALYS does.
CARD_ROUNDING = True


@contextmanager
def card_rounding(enabled: bool):
    """Turn ECIS's input-card quantisation on or off for the duration of the block.

    `True` (the default state, and the only one any reproduction of TALYS uses) is
    `ecis_card_value`/`ecis_card_energy` as `ecisinput.f90` writes the cards. `False` is for
    DIFFPARAM's gradient gate only, where the f10.5 resolution of a radius would otherwise
    dominate a finite difference; see `CARD_ROUNDING` above and `docs/results/hf-diffparam.md`.

    TALYS: ecisinput.f90:1 (ecisinput)
    Test: G0.4 / tests/hf/test_optical.py
    """
    global CARD_ROUNDING
    prev = CARD_ROUNDING
    CARD_ROUNDING = bool(enabled)
    try:
        yield
    finally:
        CARD_ROUNDING = prev


def _round_f10_5(x: Tensor) -> Tensor:
    return torch.round(x * 1.0e5) / 1.0e5


def _round_es10_3(x: Tensor) -> Tensor:
    ax = torch.where(x == 0, torch.ones_like(x), x.abs())
    e = torch.floor(torch.log10(ax))
    m = torch.round(x / 10.0**e * 1.0e3) / 1.0e3
    return torch.where(x == 0, x, m * 10.0**e)


def ecis_card_energy(e_mev: Tensor) -> Tensor:
    """Energy as ECIS reads it from the first level card.

    TALYS: ecisinput.f90:1 (ecisinput) — `f10.5` when e >= 0.01 MeV, `es10.3` below.
    Test: A-trans
    """
    if not CARD_ROUNDING:
        return e_mev
    fast = _nx2omp.card(e_mev, True)  # NATIVEX2 `omp`: no gradient, compiled
    if fast is not None:
        return fast
    y = torch.where(e_mev >= 0.01, _round_f10_5(e_mev), _round_es10_3(e_mev))
    return _straight_through(e_mev, y)


def ecis_card_value(x: Tensor) -> Tensor:
    """Masses and OMP parameters as ECIS reads them (`f10.5`, or `es10.3` when |x| >= 1000).

    TALYS: ecisinput.f90:1 (ecisinput)
    Test: A-trans
    """
    if not CARD_ROUNDING:
        return x
    fast = _nx2omp.card(x, False)  # NATIVEX2 `omp`: no gradient, compiled
    if fast is not None:
        return fast
    y = torch.where(x.abs() >= 1000.0, _round_es10_3(x), _round_f10_5(x))
    return _straight_through(x, y)


@cache
def _ame2020_table(symbol: str, structure: str) -> dict[int, float]:
    # TODO(T2): switch to physics.hf.structure.masses when it lands. Read exactly as
    # masses.f90 does: `read(1, '(4x, i4, 2f12.6)') ia, expmass1, expmexc1`.
    path = Path(structure) / "masses" / "ame2020" / f"{symbol}.mass"
    out: dict[int, float] = {}
    for line in path.read_text().splitlines():
        if len(line) < 20:
            continue
        out[int(line[4:8])] = float(line[8:20])
    return out


def nucleus_mass_amu(Z: int, A: int, code_dir: str | None = None) -> float:
    """nucmass(Zix, Nix) [amu] as TALYS sets it by default: the AME2020 atomic mass from the
    structure database (masses.f90, flagexpmass). Falls back to A when the nuclide is absent.

    TALYS: masses.f90:1 (masses)
    Test: A-trans
    """
    table = _ame2020_table(nuclide_symbol(Z), str(talys_structure_path(code_dir)))
    return table.get(A, float(A))


# ------------------------------------------------------------------------------ kinematics
def ecis_kinematics(
    e_lab_mev: Tensor, m_proj_amu: float, m_targ_amu: float, z_prod: float
) -> EcisKinematics:
    """Wave number, Coulomb parameter and potential coefficient exactly as ECIS computes them
    with TALYS's flags: relativistic kinematics (lo(8), flagrel default y) and the "reduced
    energy" for the non-Coulomb interaction (lo(95), set in ecis2 by TALYS).

    TALYS: ecist.f:3332 (lecl), ecist.f:5464 (khco)
    Test: A-trans
    """
    cm = ECIS_CM_MEV
    m1, m2 = float(m_proj_amu), float(m_targ_amu)
    e = e_lab_mev.to(DTYPE)
    # lecl: relativistic c.m. energy ecm = sqrt((m1+m2)**2+2*m2*elab) - m1 - m2 (in cm units)
    ecm = cm * (torch.sqrt((m1 + m2) ** 2 + 2.0 * m2 * e / cm) - m1 - m2)
    x = ecm / cm
    amr = x + m1 + m2
    # khco: wsk2 = k**2
    k2 = 0.125 * ECIS_CK * ecm * (x + 2.0 * m1 + 2.0 * m2) * (x + 2.0 * m1) * (x + 2.0 * m2) / amr**2
    k = torch.sqrt(k2.abs())
    amrd = (amr**4 - (m1**2 - m2**2) ** 2) / (4.0 * amr**3)
    amre = amrd  # lo(96) false
    amrm = amre  # lo(95) true: amrm = amre
    eta = cm * ECIS_CCZ_MEV_FM * amre * z_prod / k / ECIS_CHB_MEV_FM**2
    return EcisKinematics(ecm_mev=ecm, k_fm=k, eta=eta, mu_coef=ECIS_CK * amrm)


# ------------------------------------------------------------------------------- potentials
_FIELDS = (
    "v_mev", "rv_fm", "av_fm", "w_mev", "rw_fm", "aw_fm",
    "vd_mev", "rvd_fm", "avd_fm", "wd_mev", "rwd_fm", "awd_fm",
    "vso_mev", "rvso_fm", "avso_fm", "wso_mev", "rwso_fm", "awso_fm", "rc_fm",
)  # fmt: skip


def _param(p, name: str, n_e: int) -> Tensor:
    v = torch.as_tensor(getattr(p, name), dtype=DTYPE)
    return v.reshape(-1).expand(n_e) if v.numel() == 1 else v.reshape(n_e)


def _ws(r: Tensor, R: Tensor, a: Tensor) -> tuple[Tensor, Tensor]:
    """Woods-Saxon f and g = -a df/dr on r (wosa: v(1)=b, v(2)=b*c*v(1)/a)."""
    x = (r - R) / a
    f = torch.sigmoid(-x)
    g = f * (1.0 - f)
    return f, g


def optical_potential(
    p, m_targ_amu: Tensor, r_fm: Tensor, z_prod: float
) -> tuple[Tensor, Tensor, Tensor]:
    """Central nuclear potential, spin-orbit radial factor and Coulomb potential on r_fm.

    Shapes: parameters (E,), r (R,) or (E, R) -> central (E, R) complex [MeV]; spin-orbit
    (E, R) complex [MeV], the radial factor that multiplies 2 l.s (with ECIS's (hbar/m_pi c)^2 =
    2 fm^2 included: tlnc `cso=2*vpr*cls`, ecist.f:14415); Coulomb (E, R) real [MeV].

    TALYS: ecist.f:12950 (wosa)
    Test: A-trans
    """
    n_e = torch.as_tensor(p.v_mev).numel()
    # SPEEDT3: the 19 card quantisations of a potential in one call instead of one per column.
    # `ecis_card_value` is element-wise, and the two transcendentals it runs (log10, 10**e) see
    # the same arguments in either shape -- checked bitwise on all 798 columns of the speed
    # harness, inverse and incident.
    flat = ecis_card_value(torch.cat([_param(p, f, n_e) for f in _FIELDS]))
    q = {f: flat[i * n_e:(i + 1) * n_e] for i, f in enumerate(_FIELDS)}
    am3 = m_targ_amu ** (1.0 / 3.0)
    r = r_fm[None, :] if r_fm.dim() == 1 else r_fm

    def ws(depth, r0, a):
        return _ws(r, (r0 * am3)[:, None], a[:, None].clamp_min(1.0e-6))

    fv, _ = ws(q["v_mev"], q["rv_fm"], q["av_fm"])
    fw, _ = ws(q["w_mev"], q["rw_fm"], q["aw_fm"])
    _, gvd = ws(q["vd_mev"], q["rvd_fm"], q["avd_fm"])
    _, gwd = ws(q["wd_mev"], q["rwd_fm"], q["awd_fm"])
    real = -q["v_mev"][:, None] * fv - 4.0 * q["vd_mev"][:, None] * gvd
    imag = -q["w_mev"][:, None] * fw - 4.0 * q["wd_mev"][:, None] * gwd
    central = torch.complex(real, imag)
    # spin-orbit: (1/r) df/dr = -(g/a)/r
    _, gvso = ws(q["vso_mev"], q["rvso_fm"], q["avso_fm"])
    _, gwso = ws(q["wso_mev"], q["rwso_fm"], q["awso_fm"])
    dvso = -gvso / q["avso_fm"][:, None].clamp_min(1.0e-6) / r
    dwso = -gwso / q["awso_fm"][:, None].clamp_min(1.0e-6) / r
    so = torch.complex(q["vso_mev"][:, None] * dvso, q["wso_mev"][:, None] * dwso)
    so = SPIN_ORBIT_FACTOR * so
    # homogeneously charged sphere
    rc = (q["rc_fm"] * am3)[:, None]
    e2z = ECIS_CCZ_MEV_FM * z_prod
    inside = e2z / (2.0 * rc.clamp_min(1.0e-6)) * (3.0 - (r / rc.clamp_min(1.0e-6)) ** 2)
    coul = torch.where(r < rc, inside, e2z / r)
    if z_prod == 0:
        coul = torch.zeros_like(coul)
    return central, so, coul


# ECIS multiplies (Vso + i Wso) (1/r) df/dr (2 l.s) by 2 (tlnc: `cso=2.d0*vpr*cls`, with cls = 2 l.s):
# the (hbar/m_pi c)^2 = 2 fm^2 of the Thomas form. Confirmed by the T(l-1/2)/T(l+1/2) splitting.
SPIN_ORBIT_FACTOR = 2.0


# ---------------------------------------------------------------------- Coulomb functions
def _cf1(
    eta: np.ndarray, rho: np.ndarray, lmax: int, n_extra: int
) -> tuple[np.ndarray, np.ndarray]:
    """f_L = F'_L/F_L (d/drho) for L = 0..lmax by the backward recurrence of the continued
    fraction, and sign(F_0/F_{Ltop}) (F_L > 0 for L well beyond rho).

    In numpy (float64 arrays) for speed: a torch op on a small CPU tensor costs a few µs and
    this loop runs rho + 60 times. Each operation is the one the torch version performed, in
    the same order (`L / rho` in torch is `L * rho.reciprocal()`), so the result is
    bit-identical."""
    ltop = lmax + n_extra
    L = ltop + 1
    with np.errstate(all="ignore"):
        inv_rho = 1.0 / rho
        f = L * inv_rho + eta / L  # asymptotic F'_L/F_L at large L
        sign = np.ones_like(rho)
        out = np.empty(rho.shape + (lmax + 1,), dtype=np.float64)
        for L in range(ltop, 0, -1):
            # f_{L-1} = S_L - R_L^2/(S_L + f_L)
            S = L * inv_rho + eta / L
            q = eta / L
            R2 = 1.0 + q * q
            d = S + f
            d = np.where(np.abs(d) < 1.0e-290, 1.0e-290, d)
            sign = sign * np.sign(d)
            f = S - R2 / d
            if L - 1 <= lmax:
                out[..., L - 1] = f
        if lmax >= 0 and ltop == lmax:
            out[..., lmax] = (lmax + 1) * inv_rho + eta / (lmax + 1)
    return out, sign


@torch.no_grad()
def _cf2(eta: Tensor, rho: Tensor, maxit: int = 20000, acc: float = 1.0e-15) -> tuple[Tensor, Tensor]:
    """p + i q = H+'/H+ at L = 0 (Steed's CF2, Barnett's COUL90 recurrences)."""
    xi = 1.0 / rho
    wi = 2.0 * eta
    p = torch.zeros_like(rho)
    q = 1.0 - eta * xi
    ar = -(eta**2)
    ai = eta.clone()
    br = 2.0 * (rho - eta)
    bi = torch.full_like(rho, 2.0)
    dr = br / (br * br + bi * bi)
    di = -bi / (br * br + bi * bi)
    dp = -xi * (ar * di + ai * dr)
    dq = xi * (ar * dr - ai * di)
    pk = torch.zeros_like(rho)
    done = torch.zeros_like(rho, dtype=torch.bool)
    for _ in range(maxit):
        p = torch.where(done, p, p + dp)
        q = torch.where(done, q, q + dq)
        pk = pk + 2.0
        ar = ar + pk
        ai = ai + wi
        bi = bi + 2.0
        d = ar * dr - ai * di + br
        di = ai * dr + ar * di + bi
        c = 1.0 / (d * d + di * di)
        dr = c * d
        di = -c * di
        a = br * dr - bi * di - 1.0
        b = bi * dr + br * di
        c = dp * a - dq * b
        dq = dp * b + dq * a
        dp = c
        done = done | ((dp.abs() + dq.abs()) < (p.abs() + q.abs()) * acc)
        if bool(done.all()):
            break
    return p, q


@torch.no_grad()
def _steed_g0(eta: Tensor, rho: Tensor) -> tuple[Tensor, Tensor]:
    """G_0 and dG_0/drho at rho (beyond the L=0 turning point) by Steed's method."""
    f, sign = _cf1(eta.numpy(), rho.numpy(), 0, int(float(rho.max())) + 60)
    f0, sign = torch.from_numpy(f[..., 0]), torch.from_numpy(sign)
    p, q = _cf2(eta, rho)
    gam = (f0 - p) / q
    w = 1.0 / torch.sqrt((f0 - p) * gam + q)
    F0 = sign * w
    return gam * F0, (p * gam - q) * F0


@torch.no_grad()
def _numerov_inward(ee: np.ndarray, ra: np.ndarray, rb: np.ndarray, gb: np.ndarray, gb1: np.ndarray,
                    n: int, block: int = 2048):
    """Numerov for u'' = -(1 - 2 eta/x) u from x = rb inward in n steps of h = (rb - ra)/n, one
    column per energy, given u(rb) = gb and u(rb - h) = gb1.

    Returns u(ra), u(ra - h), u(ra + h), h, c = h^2/12 and 2 eta. The step coefficients are
    evaluated for a block of steps at once; the recurrence itself is sequential over steps and
    vectorised over energies. Every floating-point operation is the one the former scalar-step
    loop made, in the same order, so the result is bit-identical to it."""
    h = (rb - ra) / n
    c = h * h / 12.0
    c5 = 5.0 * c
    e2 = 2.0 * ee
    u2, u1 = gb.copy(), gb1.copy()  # u at x + h, x
    t = np.empty_like(u1)
    prev = None
    with np.errstate(all="ignore"):
        for s in range(2, n + 2, block):
            i = np.arange(s, min(s + block, n + 2), dtype=np.float64)[:, None]
            x0 = rb - i * h  # new point
            x1 = rb - (i - 1.0) * h
            if s == 2:
                x1[0] = rb - h
            A = 2.0 * (1.0 - c5 * (1.0 - e2 / x1))
            B = 1.0 + c * (1.0 - e2 / (x1 + h))
            C = 1.0 + c * (1.0 - e2 / x0)
            kprev = n - 1 - s if s <= n - 1 < s + block else -1
            for k, (a, b, cc) in enumerate(zip(A, B, C, strict=True)):
                # u(x0) = (A u(x1) - B u(x1 + h)) / C
                np.multiply(a, u1, out=t)
                np.multiply(b, u2, out=u2)
                np.subtract(t, u2, out=t)
                np.divide(t, cc, out=u2)
                u1, u2 = u2, u1
                if k == kprev:
                    prev = u1.copy()  # value at ra + h
    # u1 is at ra - h, u2 at ra, prev at ra + h
    return u2, u1, prev, h, c, e2


def _g_recurrence(eta: Tensor, rho: Tensor, G0: Tensor, dG0: Tensor, lmax: int
                  ) -> tuple[Tensor, Tensor]:
    """SETB: the upward recurrence of `coulomb_functions` for G_L, dG_L, L = 1..lmax, on numpy
    arrays: `+ - * /`, `x ** 2` (= x * x in both libraries) and `sqrt` are exact per element, and
    torch's scalar-over-tensor `L / rho` is `rho.reciprocal() * L`, written so here; so the columns
    are the torch loop's bits without its ~6 dispatches per order.

    TALYS: ecist.f:5775 (fcou)
    Test: tests/hf/test_setb.py (bitwise against the torch loop)
    """
    e = eta.numpy()
    r = rho.numpy()
    G = np.empty(r.shape + (lmax + 1,), dtype=np.float64)
    dG = np.empty_like(G)
    G[..., 0], dG[..., 0] = G0.numpy(), dG0.numpy()
    with np.errstate(all="ignore"):
        for L in range(1, lmax + 1):
            S = (1.0 / r) * L + e / L  # torch's `L / rho` is `rho.reciprocal() * L`
            R = np.sqrt(1.0 + (e / L) ** 2)
            G[..., L] = (S * G[..., L - 1] - dG[..., L - 1]) / R
            dG[..., L] = R * G[..., L - 1] - S * G[..., L]
    return torch.from_numpy(G), torch.from_numpy(dG)


@torch.no_grad()
def coulomb_functions(eta: Tensor, rho: Tensor, lmax: int) -> tuple[Tensor, Tensor, Tensor, Tensor]:
    """Regular and irregular Coulomb functions F_L, G_L and their rho-derivatives for
    L = 0..lmax at one rho per energy: shapes (E, lmax+1). eta = 0 gives Riccati-Bessel
    functions (F_0 = sin rho, G_0 = cos rho).

    ECIS computes these with Bardin's algorithm (fcou/fcz0, "at least 8 significant figures");
    this is not a line port of it but reproduces those functions to <= 1e-9 relative (tested
    against mpmath), which is below anything ECIS's 8 figures can distinguish in T_lj.

    G_0 comes from Steed's method at rho_far = max(rho, 2 eta + 20) and, when rho lies under
    the barrier, an inward Numerov integration (stable for the growing G); G_L by upward
    recurrence (stable); F_L from the continued fraction for F'_L/F_L and the Wronskian
    F'G - FG' = 1, which is exact to rounding wherever G is.

    The two long loops (the inward Numerov, up to 40,000 steps, and the continued fraction) run
    in numpy on the CPU with the same floating-point operations as the original torch loops, so
    the outputs are bit-identical to them (SPEED1, tests/hf/test_optical.py fixture).

    TALYS: ecist.f:5775 (fcou)
    Test: A-trans
    """
    device = rho.device
    eta = eta.detach().to(device="cpu", dtype=DTYPE)
    rho = rho.detach().to(device="cpu", dtype=DTYPE)
    fast = _nx2omp.coulomb(eta, rho, lmax)  # NATIVEX2 `omp`: the same call, compiled
    if fast is not None:
        return tuple(t.to(device) for t in fast)
    neutral = eta == 0
    G0 = torch.cos(rho)
    dG0 = -torch.sin(rho)
    if bool((~neutral).any()):
        e_c = eta[~neutral]
        r_c = rho[~neutral]
        r_far = torch.maximum(r_c, 2.0 * e_c + 20.0)
        need = r_far > r_c
        g_far, dg_far = _steed_g0(e_c, r_far)
        g_c, dg_c = g_far.clone(), dg_far.clone()
        if bool(need.any()):
            ee, ra, rb = e_c[need], r_c[need], r_far[need]
            n = int(min(40000, max(200, math.ceil(float((rb - ra).max()) / 0.004))))
            h = (rb - ra) / n
            gb, _ = _steed_g0(ee, rb)
            gb1, _ = _steed_g0(ee, rb - h)
            ra_np = ra.numpy()
            ga, u1, prev, h_np, c, e2 = _numerov_inward(
                ee.numpy(), ra_np, rb.numpy(), gb.numpy(), gb1.numpy(), n
            )
            with np.errstate(all="ignore"):
                dga = (
                    (1.0 + 2.0 * c * (1.0 - e2 / (ra_np + h_np))) * prev
                    - (1.0 + 2.0 * c * (1.0 - e2 / (ra_np - h_np))) * u1
                ) / (2.0 * h_np)
            g_c[need] = torch.from_numpy(ga)
            dg_c[need] = torch.from_numpy(dga)
        G0 = G0.clone()
        dG0 = dG0.clone()
        G0[~neutral] = g_c
        dG0[~neutral] = dg_c
    # upward recurrence for G_L
    G, dG = _g_recurrence(eta, rho, G0, dG0, lmax)
    f = torch.from_numpy(_cf1(eta.numpy(), rho.numpy(), lmax, int(float(rho.max())) + 60)[0])
    F = 1.0 / (f * G - dG)
    dF = f * F
    return F.to(device), dF.to(device), G.to(device), dG.to(device)


# ------------------------------------------------- Coulomb functions of many calls in one pass
# SPEEDT. `coulomb_functions` derives three things from its whole batch rather than per column:
# the continued fraction's starting order (`int(rho.max()) + 60`), the inward Numerov's step count
# (from the largest `rb - ra`) and the set of columns under the barrier. So concatenating two
# calls' columns into one call changes their last bits. The functions below give every column its
# own call's starting order and step count and run the recurrences for all of them at once, which
# is where the time goes (up to 40,000 Numerov steps and ~3,000 continued-fraction terms per call,
# each a handful of numpy ufuncs whose cost is per call, not per column). Only the per-element
# operations of the single call are performed, in its order; floating-point +, -, *, / and sqrt
# are exact per element whatever the array layout, so every column is bit-identical to its call.


def _cf1_many(eta: np.ndarray, rho: np.ndarray, lmax: int, ltop: np.ndarray,
              lmax_col: np.ndarray | None = None):
    """`_cf1(eta[c], rho[c], lmax_col[c], ltop[c] - lmax_col[c])` for every column c, to the bit,
    in its first `lmax_col[c] + 1` orders (`lmax_col` defaults to `lmax`, the width of the output):
    the backward recurrence runs once from the largest `ltop` down, and a column joins it at its
    own `ltop` (sorted so that the running columns are always a prefix). `ltop[c] > lmax_col[c]`
    is required (every caller adds 60)."""
    m = rho.shape[0]
    out = np.empty((m, lmax + 1), dtype=np.float64)
    sign = np.ones(m, dtype=np.float64)
    if m == 0:
        return out, sign
    assert bool((ltop > (lmax if lmax_col is None else lmax_col)).all())
    if _native.available():  # SPEEDT3: the same recurrence per column, compiled
        return _native.cf1(eta, rho, lmax, ltop)
    order = np.argsort(-ltop, kind="stable")
    eta_s, rho_s, top_s = eta[order], rho[order], ltop[order]
    ost = np.empty_like(out)
    sgn = np.empty(m, dtype=np.float64)
    f = np.empty(m, dtype=np.float64)
    # number of columns running at order L: those with ltop >= L (top_s is non-increasing)
    neg = -top_s
    with np.errstate(all="ignore"):
        inv_rho = 1.0 / rho_s
        k = 0
        for L in range(int(top_s[0]), 0, -1):
            k_new = int(np.searchsorted(neg, -L, side="right"))
            if k_new > k:
                Li = L + 1
                f[k:k_new] = Li * inv_rho[k:k_new] + eta_s[k:k_new] / Li
                sgn[k:k_new] = 1.0
                k = k_new
            ir, et = inv_rho[:k], eta_s[:k]
            S = L * ir + et / L
            q = et / L
            R2 = 1.0 + q * q
            d = S + f[:k]
            d = np.where(np.abs(d) < 1.0e-290, 1.0e-290, d)
            sgn[:k] = sgn[:k] * np.sign(d)
            f[:k] = S - R2 / d
            if L - 1 <= lmax:
                ost[:k, L - 1] = f[:k]
    out[order] = ost
    sign[order] = sgn
    return out, sign


def _numerov_inward_many(ee: np.ndarray, ra: np.ndarray, rb: np.ndarray, gb: np.ndarray,
                         gb1: np.ndarray, n: np.ndarray, block: int = 128):
    """`_numerov_inward` for columns that each carry their own step count `n[c]`, to the bit.

    A column with n steps runs its steps 2..n+1 as the global steps N-n+2..N+1 (N = max n), so
    every column ends on the same step and the columns running at any step are a prefix once
    they are sorted by n. Returns u(ra), u(ra - h), u(ra + h), h, c and 2 eta per column."""
    if _native.available():  # SPEEDT3: the same steps per column, compiled
        return _native.numerov_inward(ee, ra, rb, gb, gb1, n)
    m = ee.shape[0]
    order = np.argsort(-n, kind="stable")
    ee_s, ra_s, rb_s, n_s = ee[order], ra[order], rb[order], n[order]
    h = (rb_s - ra_s) / n_s.astype(np.float64)
    c = h * h / 12.0
    c5 = 5.0 * c
    e2 = 2.0 * ee_s
    big = int(n_s[0])
    off = (big - n_s).astype(np.float64)  # global step = local step + off
    start = big - n_s + 2  # global step at which a column starts (non-decreasing)
    gb_s, gb1_s = gb[order], gb1[order]
    # columns starting at each global step take their boundary values just before it; until
    # then their slots hold values that are never read (computed, then overwritten)
    events = {}
    for v in np.unique(start):
        sel = np.nonzero(start == v)[0]
        events[int(v)] = slice(int(sel[0]), int(sel[-1]) + 1)
    u2 = np.zeros(m, dtype=np.float64)
    u1 = np.zeros(m, dtype=np.float64)
    t = np.empty(m, dtype=np.float64)
    prev = None
    mul, sub, div = np.multiply, np.subtract, np.divide
    with np.errstate(all="ignore"):
        for s in range(2, big + 2, block):
            stop = min(s + block, big + 2)
            # each column's own step index j = i - 1 .. i (garbage before the column starts).
            # The scalar loop's x1 = rb - (i - 1.0) h is bit-for-bit x0 one step earlier
            # (i - 1.0 is exact; at i = 2 it is its special case rb - h), so 1 - 2 eta / x is
            # evaluated once per node and shared by C at i and A at i + 1.
            gj = np.arange(s - 1, stop, dtype=np.float64)[:, None]
            x = rb_s - (gj - off[None, :]) * h
            q = 1.0 - e2 / x
            A = 2.0 * (1.0 - c5 * q[:-1])
            B = 1.0 + c * (1.0 - e2 / (x[:-1] + h))
            C = 1.0 + c * q[1:]
            g = s
            for ar, br, cr in zip(A, B, C):
                ev = events.get(g)
                if ev is not None:
                    u2[ev] = gb_s[ev]
                    u1[ev] = gb1_s[ev]
                # u(x0) = (A u(x1) - B u(x1 + h)) / C
                mul(ar, u1, t)
                mul(br, u2, u2)
                sub(t, u2, t)
                div(t, cr, u2)
                u1, u2 = u2, u1
                if g == big - 1:
                    prev = u1.copy()  # value at ra + h
                g += 1
    res = np.empty(m), np.empty(m), np.empty(m)
    res[0][order], res[1][order], res[2][order] = u2, u1, prev
    back = np.empty(m, dtype=np.intp)
    back[order] = np.arange(m)
    return res[0], res[1], res[2], h[back], c[back], e2[back]


@torch.no_grad()
def coulomb_functions_many(etas: list[Tensor], rhos: list[Tensor], lmax: int | list[int]):
    """`[coulomb_functions(eta, rho, lmax) for eta, rho in zip(etas, rhos)]`, bit-identical, with
    the continued fractions and the inward Numerov of all calls run together (see above). `lmax`
    may be one value per call.

    TALYS: ecist.f:5775 (fcou)
    Test: A-trans / tests/hf/test_optical.py (bitwise against `coulomb_functions`)
    """
    devices = [r.device for r in rhos]
    etas = [e.detach().to(device="cpu", dtype=DTYPE).reshape(-1) for e in etas]
    rhos = [r.detach().to(device="cpu", dtype=DTYPE).reshape(-1) for r in rhos]
    lmaxs = [int(lmax)] * len(rhos) if isinstance(lmax, int) else [int(x) for x in lmax]
    lmax = max(lmaxs, default=0)
    sizes = [int(r.numel()) for r in rhos]
    eta_all, rho_all = torch.cat(etas), torch.cat(rhos)
    # continued-fraction columns: [final (every call, all columns), steed columns]
    cf_eta, cf_rho, cf_top, cf_lmax = [eta_all.numpy()], [rho_all.numpy()], [], []
    for r, lm in zip(rhos, lmaxs, strict=True):
        cf_top.append(np.full(r.numel(), lm + (int(float(r.max())) + 60 if r.numel() else 60)))
        cf_lmax.append(np.full(r.numel(), lm))
    steed = []  # (call, kind, columns) with kind 0: g_far at r_far, 1: gb at rb, 2: gb1 at rb - h
    num = []  # per call: None or (need mask, ee, ra, rb, n)
    for i, (e, r) in enumerate(zip(etas, rhos, strict=True)):
        charged = e != 0
        if not bool(charged.any()):
            num.append(None)
            continue
        e_c, r_c = e[charged], r[charged]
        r_far = torch.maximum(r_c, 2.0 * e_c + 20.0)
        need = r_far > r_c
        pts = [(e_c, r_far)]
        info = None
        if bool(need.any()):
            ee, ra, rb = e_c[need], r_c[need], r_far[need]
            nn = int(min(40000, max(200, math.ceil(float((rb - ra).max()) / 0.004))))
            h = (rb - ra) / nn
            pts += [(ee, rb), (ee, rb - h)]
            info = (need, ee, ra, rb, nn)
        num.append((charged, r_far, info))
        for kind, (pe, pr) in enumerate(pts):
            steed.append((i, kind, int(pe.numel())))
            cf_eta.append(pe.numpy())
            cf_rho.append(pr.numpy())
            cf_top.append(np.full(pe.numel(), int(float(pr.max())) + 60))
            cf_lmax.append(np.zeros(pe.numel(), dtype=np.int64))
    f_all, s_all = _cf1_many(np.concatenate(cf_eta), np.concatenate(cf_rho), lmax,
                             np.concatenate(cf_top), np.concatenate(cf_lmax))
    n_final = int(rho_all.numel())
    G = torch.empty((n_final, lmax + 1), dtype=DTYPE)
    dG = torch.empty_like(G)
    G[:, 0] = torch.cos(rho_all)
    dG[:, 0] = -torch.sin(rho_all)
    if steed:
        # Steed's G_0 for every steed column at once (CF2 is per-element; it only runs longer)
        se = torch.from_numpy(np.concatenate(cf_eta[1:]))
        sr = torch.from_numpy(np.concatenate(cf_rho[1:]))
        f0 = torch.from_numpy(f_all[n_final:, 0].copy())
        sign = torch.from_numpy(s_all[n_final:].copy())
        p, q = _cf2(se, sr)
        gam = (f0 - p) / q
        w = 1.0 / torch.sqrt((f0 - p) * gam + q)
        F0 = sign * w
        g_st, dg_st = gam * F0, (p * gam - q) * F0
        pos, cols = 0, {}
        for i, kind, cnt in steed:
            cols[(i, kind)] = (g_st[pos : pos + cnt], dg_st[pos : pos + cnt])
            pos += cnt
        # the inward Numerov of every call under the barrier, at once
        nee, nra, nrb, ngb, ngb1, nn_col, owners = [], [], [], [], [], [], []
        for i, item in enumerate(num):
            if item is None or item[2] is None:
                continue
            need, ee, ra, rb, nn = item[2]
            nee.append(ee.numpy())
            nra.append(ra.numpy())
            nrb.append(rb.numpy())
            ngb.append(cols[(i, 1)][0].numpy())
            ngb1.append(cols[(i, 2)][0].numpy())
            nn_col.append(np.full(ee.numel(), nn))
            owners.append((i, int(ee.numel())))
        if owners:
            ga, u1, prev, h_np, c, e2 = _numerov_inward_many(
                np.concatenate(nee), np.concatenate(nra), np.concatenate(nrb),
                np.concatenate(ngb), np.concatenate(ngb1), np.concatenate(nn_col))
            ra_np = np.concatenate(nra)
            with np.errstate(all="ignore"):
                dga = (
                    (1.0 + 2.0 * c * (1.0 - e2 / (ra_np + h_np))) * prev
                    - (1.0 + 2.0 * c * (1.0 - e2 / (ra_np - h_np))) * u1
                ) / (2.0 * h_np)
            pos, inward = 0, {}
            for i, cnt in owners:
                inward[i] = (torch.from_numpy(ga[pos : pos + cnt].copy()),
                             torch.from_numpy(dga[pos : pos + cnt].copy()))
                pos += cnt
        start = 0
        for i, item in enumerate(num):
            size = sizes[i]
            if item is not None:
                charged, _r_far, info = item
                g_far, dg_far = cols[(i, 0)]
                g_c, dg_c = g_far.clone(), dg_far.clone()
                if info is not None:
                    g_c[info[0]] = inward[i][0]
                    dg_c[info[0]] = inward[i][1]
                G0 = G[start : start + size, 0].clone()
                dG0 = dG[start : start + size, 0].clone()
                G0[charged] = g_c
                dG0[charged] = dg_c
                G[start : start + size, 0] = G0
                dG[start : start + size, 0] = dG0
            start += size
    # upward recurrence for G_L (per element)
    G, dG = _g_recurrence(eta_all, rho_all, G[:, 0], dG[:, 0], lmax)
    f = torch.from_numpy(f_all[:n_final])
    F = 1.0 / (f * G - dG)
    dF = f * F
    out, start = [], 0
    for size, dev, lm in zip(sizes, devices, lmaxs, strict=True):
        sl = slice(start, start + size)
        out.append(tuple(t[sl, : lm + 1].to(dev) for t in (F, dF, G, dG)))
        start += size
    return out


# ------------------------------------------------------------------------------ the solver
_POTS = (
    ("v_mev", "rv_fm", "av_fm"),
    ("w_mev", "rw_fm", "aw_fm"),
    ("vd_mev", "rvd_fm", "avd_fm"),
    ("wd_mev", "rwd_fm", "awd_fm"),
    ("vso_mev", "rvso_fm", "avso_fm"),
    ("wso_mev", "rwso_fm", "awso_fm"),
)


@torch.no_grad()
def ecis_grid(p, m_targ_amu: float, kin: EcisKinematics) -> tuple[Tensor, Tensor, Tensor]:
    """ECIS's default integration grid per energy: matching radius
    rm = max over non-zero potentials of R + a*log(|V| k/(aconv ecm)) and Rc + 10*a_c (lect,
    ecist.f:3874 and 3909, `w1`); step h = min(min(a)/2, 0.5/k) (`if (h.le.0) h=dmin1(w2/2,
    0.5/wv(4,1))`); ism = idint(rm/h + 0.5); h = rm/ism; rm = h*ism.

    TALYS hands ECIS hint = rmatch = 0 for a spherical non-JLM target (inverseecis.f90:189-190,
    incidentecis.f90:170-171), so these ECIS defaults are what is used; the rmatch = 18 branch
    at inverseecis.f90:318 is JLM only and out of scope (contract §8).

    Returns (h_fm, ism, rm_fm), each (E,).

    TALYS: ecist.f:3627 (lect)
    Test: A-trans
    """
    fast = _nx2omp.grid(p, m_targ_amu, kin, CARD_ROUNDING)  # NATIVEX2 `omp`
    if fast is not None:
        return fast
    n_e = kin.k_fm.shape[0]
    am3 = m_targ_amu ** (1.0 / 3.0)
    w3 = kin.k_fm / (ECIS_ACONV * kin.ecm_mev)
    rm = torch.zeros(n_e, dtype=DTYPE)
    w2 = torch.full((n_e,), 1.0e21, dtype=DTYPE)
    # SPEEDT3: one card quantisation for the 22 columns this reads, as in `optical_potential`
    names = [n for pot in _POTS for n in pot] + ["rc_fm"]
    flat = ecis_card_value(torch.cat([_param(p, n, n_e) for n in names]))
    card = [flat[i * n_e:(i + 1) * n_e] for i in range(len(names))]
    for k in range(len(_POTS)):
        dep = card[3 * k].abs()
        R = card[3 * k + 1] * am3
        aa = card[3 * k + 2]
        on = dep != 0
        val = R + torch.log(w3 * torch.where(on, dep, torch.ones_like(dep))) * aa
        rm = torch.where(on, torch.maximum(rm, val), rm)
        w2 = torch.where(on, torch.minimum(w2, aa), w2)
    rc = card[-1] * am3
    rm = torch.maximum(rm, rc)
    h = torch.minimum(w2 / 2.0, 0.5 / kin.k_fm)
    ism = torch.floor(rm / h + 0.5).to(torch.int64).clamp_min(4)
    h = rm / ism.to(DTYPE)
    return h, ism, h * ism.to(DTYPE)


def matching_radius(p, m_targ_amu: float, kin: EcisKinematics) -> float:
    """Largest ECIS matching radius over the energy axis (see `ecis_grid`).

    TALYS: ecist.f:3627 (lect)
    Test: A-trans
    """
    return float(ecis_grid(p, m_targ_amu, kin)[2].max())


def _lj_grid(lmax: int, spin: float):
    two_s = int(round(2 * spin))
    L = torch.arange(lmax + 1, dtype=DTYPE)
    joff = torch.arange(two_s + 1, dtype=DTYPE) - spin  # j = l - s ... l + s
    jv = L[:, None] + joff[None, :]
    valid = jv >= (L[:, None] - spin).abs() - 1.0e-9
    ls2 = jv * (jv + 1) - L[:, None] * (L[:, None] + 1) - spin * (spin + 1)  # 2 l.s
    return L, jv, valid, ls2


def _ecis_setup(p, kin, m_targ, z_prod, spin, lmax, native: bool = False):
    """ECIS's grid and the modified-Numerov coefficient x = q - q**2/12 per (E, L, J, R).

    With `native` (SPEEDT3, no autograd) x is not built: its place holds the pieces the compiled
    kernel builds it from, element by element in the same operations (`native.ecis_job`)."""
    L, jv, valid, ls2 = _lj_grid(lmax, spin)
    h, ism, rm = ecis_grid(p, m_targ, kin)
    n_e = h.shape[0]
    nmax = int(ism.max()) + 1
    n_idx = torch.arange(1, nmax + 1, dtype=DTYPE)
    r = h[:, None] * n_idx[None, :]  # (E, R): r_n = n h, n = 1..nmax
    central, so, coul = optical_potential(p, torch.tensor(m_targ, dtype=DTYPE), r, z_prod)
    k2 = kin.k_fm**2
    mu = kin.mu_coef
    # q_n = h^2 g(r_n) per (E, L, J, R); ECIS: x = wv(12) - cll/is**2 + vpr*v
    if native:
        x = (so, central, coul, ls2, L, k2 * h * h, mu * h * h)
    elif _requires_grad(p) or any(t.requires_grad for t in (h, k2, mu)):
        U = central[:, None, None, :] + so[:, None, None, :] * ls2[None, :, :, None].to(so.dtype)
        g = (k2 * h * h)[:, None, None, None] - (L * (L + 1))[None, :, None, None] / (
            n_idx[None, None, None, :] ** 2
        ) - (mu * h * h)[:, None, None, None] * (U + coul[:, None, None, :])
        x = g - g * g / 12.0  # modified Numerov: q - q**2/12 (complex)
    else:
        # SPEEDT: the same expression on (E, L, J, R) with two allocations instead of eight. The
        # sums, differences and products by real-valued factors are exact to the element in any
        # order of evaluation; the one complex square, g * g, runs on a fresh array of the same
        # shape as before (its SIMD kernel's result depends on the element's position).
        g = so[:, None, None, :] * ls2[None, :, :, None].to(so.dtype)
        g.add_(central[:, None, None, :]).add_(coul[:, None, None, :])
        g.mul_((mu * h * h)[:, None, None, None])
        ab = (k2 * h * h)[:, None, None, None] - (L * (L + 1))[None, :, None, None] / (
            n_idx[None, None, None, :] ** 2)
        torch.sub(ab, g, out=g)
        gg = g * g
        x = torch.sub(g, gg.div_(12.0), out=gg)

    shape = (n_e, lmax + 1, jv.shape[1])
    return L, jv, valid, h, ism, rm, nmax, shape, x


def _integrate_ecis(p, kin, m_targ, z_prod, spin, lmax):
    """ECIS's modified Numerov on ECIS's own grid, matched with ECIS's Numerov-consistent
    transformation of the Coulomb functions (tlnc, ecist.f:14415)."""
    L, jv, valid, h, ism, rm, nmax, shape, x = _ecis_setup(p, kin, m_targ, z_prod, spin, lmax)
    u_prev = torch.zeros(shape, dtype=torch.complex128)  # u(0)
    u_cur = torch.ones(shape, dtype=torch.complex128)  # u(h) (ECIS: 1e-15, scale-free)
    ism_m1 = (ism - 1)[:, None, None]
    ism_p1 = (ism + 1)[:, None, None]
    u_am = torch.zeros(shape, dtype=torch.complex128)
    u_ap = torch.zeros(shape, dtype=torch.complex128)
    for n in range(1, nmax + 1):
        # u_cur is u at node n (r = n h); step to n+1 using x at node n
        u_next = 2.0 * u_cur - u_prev - x[..., n - 1] * u_cur
        u_am = torch.where(ism_m1 == n, u_cur, u_am)
        u_ap = torch.where(ism_p1 == n + 1, u_next, u_ap)
        u_prev, u_cur = u_cur, u_next
        if n % 25 == 0:
            s = u_cur.abs().detach().clamp_min(1.0e-300)
            u_prev, u_cur = u_prev / s, u_cur / s
            u_am = torch.where(ism_m1 <= n, u_am / s, u_am)
            u_ap = torch.where(ism_p1 <= n + 1, u_ap / s, u_ap)

    # Coulomb functions at rho = k rm, then tlnc's transformation to the matching nodes
    F, dF, G, dG = coulomb_functions(kin.eta.detach(), (kin.k_fm * rm).detach(), lmax)
    return _match_ecis(u_am, u_ap, F, dF, G, dG, L, jv, valid, h, ism, rm, kin)


@torch.no_grad()
def _integrate_ecis_many(jobs):
    """`[_integrate_ecis(*job) for job in jobs]`, bit-identical, with the Coulomb functions of all
    jobs in one pass (`coulomb_functions_many`).

    The radial loop steps each job on its own tensors, exactly as `_integrate_ecis` does (the
    products and `abs` there take SIMD kernels whose result depends on an element's position in
    its array, so the jobs are not concatenated); it only replaces the two per-step `where`
    captures of the matching neighbours by index copies at the steps where they happen.
    Autograd is not supported: the differentiable path keeps `_integrate_ecis`.

    TALYS: ecist.f:14445 (tlnc)
    Test: A-trans / tests/hf/test_optical.py (bitwise against `_integrate_ecis`)
    """
    prep = []
    native = _native.vhypot()
    for p, kin, m_targ, z_prod, spin, lmax in jobs:
        L, jv, valid, h, ism, rm, nmax, shape, x = _ecis_setup(p, kin, m_targ, z_prod, spin, lmax,
                                                              native)
        prep.append((L, jv, valid, h, ism, rm, nmax, shape, x, kin, lmax))
    # SPEEDT3: with the compiled kernels, the loop below runs in C per job (bitwise,
    # tests/hf/test_native.py) and `state` holds only its two outputs
    prep_loop = [] if native else prep
    state = [[None, None, *_native.ecis_job(item[8], item[4], item[6])] for item in prep] \
        if native else []
    # per job: capture schedule (the energies whose matching neighbours are reached at a step)
    for L, _jv, _v, _h, ism, _rm, nmax, shape, x, _k, _l in prep_loop:
        cap_m = {int(v) - 1: torch.nonzero(ism == v).flatten() for v in torch.unique(ism)}
        cap_p = {int(v) + 1: torch.nonzero(ism == v).flatten() for v in torch.unique(ism)}
        state.append([torch.zeros(shape, dtype=torch.complex128),
                      torch.ones(shape, dtype=torch.complex128),
                      torch.zeros(shape, dtype=torch.complex128),
                      torch.zeros(shape, dtype=torch.complex128), cap_m, cap_p,
                      (ism - 1)[:, None, None], (ism + 1)[:, None, None]])
    for n in range(1, max((item[6] for item in prep_loop), default=0) + 1):
        for st, item in zip(state, prep_loop, strict=True):
            if n > item[6]:
                continue
            u_prev, u_cur, u_am, u_ap, cap_m, cap_p, ism_m1, ism_p1 = st
            u_next = 2.0 * u_cur - u_prev - item[8][..., n - 1] * u_cur
            idx = cap_m.get(n)
            if idx is not None:  # `where(ism - 1 == n, u_cur, u_am)`
                u_am[idx] = u_cur[idx]
            idx = cap_p.get(n + 1)
            if idx is not None:  # `where(ism + 1 == n + 1, u_next, u_ap)`
                u_ap[idx] = u_next[idx]
            u_prev, u_cur = u_cur, u_next
            if n % 25 == 0:
                s = u_cur.abs().clamp_min(1.0e-300)
                u_prev, u_cur = u_prev / s, u_cur / s
                u_am = torch.where(ism_m1 <= n, u_am / s, u_am)
                u_ap = torch.where(ism_p1 <= n + 1, u_ap / s, u_ap)
            st[:4] = u_prev, u_cur, u_am, u_ap
    etas = [item[9].eta.detach() for item in prep]
    rhos = [(item[9].k_fm * item[5]).detach() for item in prep]
    coul_all = coulomb_functions_many(etas, rhos, max(item[10] for item in prep)) if len(
        {item[10] for item in prep}) == 1 else [
        coulomb_functions(e, r, item[10]) for e, r, item in zip(etas, rhos, prep, strict=True)]
    out = []
    for st, item, fgs in zip(state, prep, coul_all, strict=True):
        L, jv, valid, h, ism, rm, _nmax, _shape, _x, kin, _lmax = item
        out.append(_match_ecis(st[2], st[3], *fgs, L, jv, valid, h, ism, rm, kin))
    return out


def _match_ecis(u_am, u_ap, F, dF, G, dG, L, jv, valid, h, ism, rm, kin):
    """tlnc's Numerov-consistent matching of `_integrate_ecis`, shared by `_integrate_ecis_many`
    (the same operations on the same values)."""
    hh = h[:, None]
    wk = kin.k_fm[:, None]
    b1c = hh * hh / 48.0
    cll = (L * (L + 1))[None, :]
    av = []
    c1 = (ism - 1).to(DTYPE)[:, None] * hh
    for _ in range(5):
        av.append(b1c * (2.0 * wk * kin.eta[:, None] / c1 - wk * wk + cll / c1**2))
        c1 = c1 + 0.5 * hh
    a1 = (1 - av[1]) / (2 + 10 * av[1])
    b1 = (1 - av[3]) / (2 + 10 * av[3])
    a2 = a1 * (1 - av[0]) / (1 - 4 * av[0])
    b2 = b1 * (1 - av[4]) / (1 - 4 * av[4])
    c1 = (2 + 10 * av[2]) - (1 - av[2]) * (a1 + b1)
    a1 = (16 - 144 * av[1]) / (2 + 10 * av[1])
    b1 = (16 - 144 * av[3]) / (2 + 10 * av[3])
    c2 = (7 + a1 * (1 - av[0])) / (1 - 4 * av[0])
    d2 = (7 + b1 * (1 - av[4])) / (1 - 4 * av[4])
    d1 = (b1 - a1) * (1 - av[2])
    a1 = a2 * d2 + b2 * c2
    b1 = (c1 * d2 + d1 * b2) / a1
    b2 = 30.0 * hh * b2 * wk / a1
    fam1 = b1 * F - b2 * dF
    fam3 = b1 * G - b2 * dG
    b1 = (c2 * c1 - a2 * d1) / a1
    a2 = -30.0 * hh * a2 * wk / a1
    fam2 = b1 * F - a2 * dF
    fam4 = b1 * G - a2 * dG
    f1, f2, f3, f4 = (t[:, :, None] for t in (fam1, fam2, fam3, fam4))
    A = u_am * f4 - f3 * u_ap
    B = u_am * f2 - f1 * u_ap
    D = A + 1j * B
    ok = torch.isfinite(D.real) & torch.isfinite(D.imag) & (D.abs() > 0) & valid[None]
    C = torch.where(ok, -B / torch.where(ok, D, torch.ones_like(D)), torch.zeros_like(D))
    tlj = torch.where(ok, 4.0 * (C.imag - C.real**2 - C.imag**2), torch.zeros_like(C.real)).clamp_min(0.0)
    smat = 1.0 + 2.0j * C
    return smat, tlj, valid, jv, float(rm.max()), float(h.min())


def _integrate_converged(p, kin, m_targ, z_prod, spin, lmax, refine):
    """Standard Numerov on one fine grid for all energies, matched to exact Coulomb functions."""
    L, jv, valid, ls2 = _lj_grid(lmax, spin)
    n_e = kin.k_fm.shape[0]
    h_e, _, rm_e = ecis_grid(p, m_targ, kin)
    h = float(h_e.min()) / refine
    rm = float(rm_e.max())
    n = int(math.ceil(rm / h)) + 1
    r = torch.arange(1, n + 2, dtype=DTYPE) * h  # r_1 .. r_{n+1}; r_0 = 0
    central, so, coul = optical_potential(p, torch.tensor(m_targ, dtype=DTYPE), r, z_prod)
    k2 = (kin.k_fm**2)[:, None, None, None]
    mu = kin.mu_coef[:, None, None, None]
    U = central[:, None, None, :] + so[:, None, None, :] * ls2[None, :, :, None].to(so.dtype)
    Uc = coul[:, None, None, :]
    cent = (L * (L + 1))[None, :, None, None] / r[None, None, None, :] ** 2
    g = k2 - mu * (U + Uc) - cent  # (E, L, J, R) complex
    c = h * h / 12.0
    shape = (n_e, lmax + 1, jv.shape[1])
    u_prev = torch.zeros(shape, dtype=torch.complex128)
    u_cur = (h ** (L + 1.0))[None, :, None].expand(shape).to(torch.complex128)
    g_prev = None  # g at r_0 multiplies u_0 = 0
    nm = n - 1
    u_m = u_mm1 = u_mp1 = None
    for i in range(0, n):
        gi, gn = g[..., i], g[..., i + 1]
        t_prev = 0.0 if g_prev is None else (1.0 + c * g_prev) * u_prev
        u_next = (2.0 * (1.0 - 5.0 * c * gi) * u_cur - t_prev) / (1.0 + c * gn)
        if i == nm:
            u_m, u_mp1, u_mm1 = u_cur, u_next, u_prev
            break
        u_prev, u_cur, g_prev = u_cur, u_next, gi
        if i % 40 == 39:
            s = u_cur.abs().detach().clamp_min(1.0e-300)
            u_cur, u_prev = u_cur / s, u_prev / s
    rmatch = float(r[nm])
    gm1, gp1 = g[..., nm - 1], g[..., nm + 1]
    du_m = ((1.0 + 2.0 * c * gp1) * u_mp1 - (1.0 + 2.0 * c * gm1) * u_mm1) / (2.0 * h)
    k = kin.k_fm
    F, dF, G, dG = coulomb_functions(kin.eta.detach(), (k * rmatch).detach(), lmax)
    kk = k[:, None, None]
    Fm, Gm = F[:, :, None], G[:, :, None]
    dFm, dGm = dF[:, :, None] * kk, dG[:, :, None] * kk  # d/dr
    a = Gm * du_m - dGm * u_m
    b = Fm * du_m - dFm * u_m
    den = a + 1j * b
    ok = torch.isfinite(den.real) & torch.isfinite(den.imag) & (den.abs() > 0) & valid[None]
    den_safe = torch.where(ok, den, torch.ones_like(den))
    smat = torch.where(ok, (a - 1j * b) / den_safe, torch.ones_like(den))
    tlj = torch.where(ok, -4.0 * torch.imag(torch.conj(a) * b) / (den_safe.abs() ** 2), torch.zeros_like(a.real))
    return smat, tlj, valid, jv, rmatch, h


def solve_radial(
    p,
    e_lab_mev: Tensor,
    m_proj_amu: float,
    m_targ_amu: float,
    z_prod: float,
    spin: float,
    lmax: int,
    refine: int = 4,
    ecis_rounding: bool = True,
    integrator: str = "ecis",
) -> RadialSolution:
    """Single-channel optical-model S-matrix and T_lj for every (E, l, j), batched.

    integrator="ecis" (default) reproduces ECIS: its modified Numerov on its own per-energy grid
    (lect) and its matching (tlnc), so the result carries ECIS's truncation error, which reaches
    several percent for sub-barrier complex particles. integrator="converged" solves the same
    equation on a grid `refine` times finer with exact Coulomb matching: the physics answer.

    TALYS: ecist.f:1 (ecist), inverseecis.f90:1 (inverseecis), ecist.f:14445 (tlnc)
    Test: A-trans
    """
    e_lab = e_lab_mev.to(DTYPE)
    if ecis_rounding:
        e_lab = ecis_card_energy(e_lab)
        m_proj = float(ecis_card_value(torch.tensor(m_proj_amu, dtype=DTYPE)))
        m_targ = float(ecis_card_value(torch.tensor(m_targ_amu, dtype=DTYPE)))
    else:
        m_proj, m_targ = float(m_proj_amu), float(m_targ_amu)
    kin = ecis_kinematics(e_lab, m_proj, m_targ, z_prod)
    if integrator == "ecis":
        smat, tlj, valid, jv, rm, h = _integrate_ecis(p, kin, m_targ, z_prod, spin, lmax)
    elif integrator == "converged":
        smat, tlj, valid, jv, rm, h = _integrate_converged(p, kin, m_targ, z_prod, spin, lmax, refine)
    else:
        raise ValueError(f"integrator {integrator!r}")
    return RadialSolution(smat=smat, tlj=tlj, valid=valid, jvalues=jv, kin=kin, rmatch_fm=rm, step_fm=h)


def cross_sections(sol: RadialSolution, spin: float) -> dict[str, Tensor]:
    """Reaction, total and shape-elastic cross sections [mb] from the S-matrix
    (spherical target, spin 0): sum over (l, j) weighted by (2j+1)/(2s+1).

    TALYS: ecist.f:1 (ecist)
    Test: A-inc
    """
    w = torch.where(sol.valid, (2.0 * sol.jvalues + 1.0) / (2.0 * spin + 1.0), torch.zeros_like(sol.jvalues))
    fac = math.pi / sol.kin.k_fm**2 * MB_PER_FM2
    s = sol.smat
    sig_r = fac * (w[None] * sol.tlj).sum((1, 2))
    sig_tot = 2.0 * fac * (w[None] * (1.0 - s.real)).sum((1, 2))
    sig_el = fac * (w[None] * (1.0 - s).abs() ** 2).sum((1, 2))
    return {"sigma_reac_mb": sig_r, "sigma_tot_mb": sig_tot, "sigma_shape_el_mb": sig_el}


def njmax_ecis(A: int, m_proj_amu: float, e_lab_mev: Tensor, numl: int = 60) -> int:
    """TALYS's estimate of the number of j values requested from ECIS (inverseecis.f90):
    njmax = max(20, int(2.4*1.25*A**(1/3)*0.22*sqrt(m*E))), capped at numl-2.

    TALYS: inverseecis.f90:1 (inverseecis)
    Test: A-trans
    """
    return int(njmax_grid(A, m_proj_amu, e_lab_mev, numl).max())


def njmax_grid(A: int, m_proj_amu: float, e_lab_mev: Tensor, numl: int = 60) -> Tensor:
    """`njmax` per energy, as `inverseecis` recomputes it inside its `do nen` loop
    (inverseecis.f90:409-411) rather than once for the whole grid.

    TALYS: inverseecis.f90:1 (inverseecis)
    Test: A-trans
    """
    e = torch.as_tensor(e_lab_mev, dtype=DTYPE).detach().clamp_min(0.0)
    x = 2.4 * 1.25 * (A ** (1.0 / 3.0)) * 0.22 * torch.sqrt(m_proj_amu * e)
    return x.to(torch.int64).clamp(20, numl - 2)


def lmax_ecis_grid(A: int, particle: int, e_lab_mev: Tensor, numl: int = 60) -> Tensor:
    """The highest l ECIS actually writes at each emission energy: `njmax - 1 + ceil(parspin)`.

    `njmax` bounds ECIS's total-angular-momentum loop, not l. That loop runs `ipj = 1..njmax`
    with `naj = jmin + 2 ipj - 2` (ecist.f cal1-244) and stops once `ipj > njmax` (cal1-355), so
    it covers njmax consecutive J starting at the lowest one the channel allows -- 1/2 for a
    spin-1/2 ejectile on the spin-0 target `ecisinput` writes for the inverse channel, 0 for the
    deuteron and the alpha. The top l is then J_max + parspin:

        n, p, t, h  J = 1/2 .. njmax - 1/2   ->  l <= njmax
        d           J = 0    .. njmax - 1    ->  l <= njmax
        alpha       J = 0    .. njmax - 1    ->  l <= njmax - 1

    Read off ECIS's own `tr020041` for n + Ca-40 (TALYS rerun with `ecissave y`): a saturated
    nucleon block has nJ = 2 x njmax = 40 and a top l of exactly 20 = njmax, a deuteron block
    nJ = 39 and top l 20, and an alpha block nJ = njmax with top l = njmax - 1 -- 19 at the
    emission energies where njmax = 20 and 20 at the two where it is 21, with T(l = 19) = 3.8e-5
    left unwritten, far above `translimit`. So the alpha's cap really is one lower, and it is not
    a convergence effect.

    TALYS: inverseecis.f90:1 (inverseecis), ecist.f:1 (ecist)
    Test: A-trans
    """
    nj = njmax_grid(A, PARMASS_AMU[particle], e_lab_mev, numl)
    return nj - 1 + int(math.ceil(PARSPIN[particle]))


def to_talys_j_axis(sol: RadialSolution, particle: int) -> Tensor:
    """(E, L, 3) in the contract's padded j order: spin-1/2 [T(l-1/2), T(l+1/2), 0], deuteron
    [T(l-1), T(l), T(l+1)], alpha [T(l), 0, 0].

    TALYS: inverseread.f90:1 (inverseread)
    Test: A-trans
    """
    t = sol.tlj
    out = torch.zeros(t.shape[:2] + (3,), dtype=DTYPE)
    nj = t.shape[2]
    out[..., :nj] = t
    return out


def solve_spherical(
    p: OMPParameters,
    Z_target: int,
    A_target: int,
    particle: int,
    e_mev: Tensor,
    options: Options | None = None,
    *,
    m_targ_amu: float | None = None,
    lmax: int | None = None,
    refine: int = 4,
    ecis_rounding: bool = True,
    integrator: str = "ecis",
) -> Transmission:
    """T_lj and cross sections for one target and particle over e_mev, batched over energy and (l,
    j). Must match transmission_*.out and cross_*.tot (A-trans).

    `p` holds the OMP parameters on the energy axis (fields of OMPParameters, each broadcastable
    to (E,)); `Z_target, A_target` is the nucleus the particle interacts with (for emission, the
    residual it leaves behind); `e_mev` is the laboratory energy TALYS hands ECIS
    (egrid/specmass). Outputs carry leading (C=1, particle=1) axes.

    TALYS: inverseecis.f90:1 (inverseecis), ecist.f:1 (ecist)
    Test: A-trans
    """
    if integrator == "ecis" and not _requires_grad(p):  # NATIVEX2 `omp`: one compiled solve
        fast = _nx2omp.solve(p, Z_target, A_target, particle, e_mev, m_targ_amu, lmax,
                             ecis_rounding)
        if fast is not None:
            return fast
    m_proj = PARMASS_AMU[particle]
    m_targ = m_targ_amu if m_targ_amu is not None else nucleus_mass_amu(Z_target, A_target)
    spin = PARSPIN[particle]
    zp = float(Z_target * PARZ[particle])
    e = torch.as_tensor(e_mev, dtype=DTYPE)
    if lmax is None:
        lmax = njmax_ecis(A_target, m_proj, e)
    sol = solve_radial(
        p, e, m_proj, m_targ, zp, spin, lmax, refine=refine, ecis_rounding=ecis_rounding,
        integrator=integrator,
    )
    return _transmission_of(sol, particle, spin)


def _transmission_of(sol: RadialSolution, particle: int, spin: float) -> Transmission:
    xs = cross_sections(sol, spin)
    nan = torch.full_like(xs["sigma_reac_mb"], float("nan"))
    tot = xs["sigma_tot_mb"] if particle == 1 else nan
    el = xs["sigma_shape_el_mb"] if particle == 1 else nan
    tjl = to_talys_j_axis(sol, particle)
    lm = _lmax_talys(tjl, particle)
    return Transmission(
        tjl=tjl[None, None],
        nj=torch.tensor([NJ[particle]], dtype=torch.int64),
        sigma_reac_mb=xs["sigma_reac_mb"][None, None],
        sigma_tot_mb=tot[None, None],
        sigma_shape_el_mb=el[None, None],
        lmax=lm[None, None],
    )


def solve_spherical_many(specs) -> list[Transmission]:
    """`solve_spherical` for several (parameters, target, particle, energies) at once, with ECIS's
    integrator, card rounding and one radial loop for all of them (`_integrate_ecis_many`):
    `specs` holds `(p, Z_target, A_target, particle, e_mev, m_targ_amu, lmax)` tuples and every
    result is bit-identical to the corresponding `solve_spherical` call. Not differentiable; the
    caller keeps `solve_spherical` whenever a parameter requires a gradient.

    TALYS: inverseecis.f90:1 (inverseecis), ecist.f:1 (ecist)
    Test: A-trans / tests/hf/test_optical.py
    """
    fast = [_nx2omp.solve(p, Z_target, A_target, particle, e_mev, m_targ_amu, lmax)
            for p, Z_target, A_target, particle, e_mev, m_targ_amu, lmax in specs]
    if all(f is not None for f in fast):  # NATIVEX2 `omp`: one compiled solve per spec
        return fast
    jobs, meta = [], []
    for p, Z_target, A_target, particle, e_mev, m_targ_amu, lmax in specs:
        m_proj = PARMASS_AMU[particle]
        m_targ = m_targ_amu if m_targ_amu is not None else nucleus_mass_amu(Z_target, A_target)
        spin = PARSPIN[particle]
        zp = float(Z_target * PARZ[particle])
        e = torch.as_tensor(e_mev, dtype=DTYPE)
        if lmax is None:
            lmax = njmax_ecis(A_target, m_proj, e)
        # solve_radial with ecis_rounding=True, integrator="ecis"
        e_lab = ecis_card_energy(e.to(DTYPE))
        m_proj_r = float(ecis_card_value(torch.tensor(m_proj, dtype=DTYPE)))
        m_targ_r = float(ecis_card_value(torch.tensor(m_targ, dtype=DTYPE)))
        kin = ecis_kinematics(e_lab, m_proj_r, m_targ_r, zp)
        jobs.append((p, kin, m_targ_r, zp, spin, lmax))
        meta.append((particle, spin, kin))
    out = []
    for (smat, tlj, valid, jv, rm, h), (particle, spin, kin) in zip(
            _integrate_ecis_many(jobs), meta, strict=True):
        sol = RadialSolution(smat=smat, tlj=tlj, valid=valid, jvalues=jv, kin=kin, rmatch_fm=rm,
                             step_fm=h)
        out.append(_transmission_of(sol, particle, spin))
    return out


def _requires_grad(p) -> bool:
    """Whether any optical-model field of `p` is on an autograd graph."""
    return any(isinstance(v, Tensor) and v.requires_grad
               for v in (getattr(p, f, None) for f in _FIELDS))


def _lmax_talys(tjl: Tensor, particle: int, translimit: float = 1.0e-5, transeps: float = 1.0e-8) -> Tensor:
    # inverseread.f90 "Processing of transmission coefficients": first l where every T_lj of
    # that l is below max(T_l(0) * translimit / (2l+1), transeps), minus one.
    t = tjl.detach()
    nj = NJ[particle]
    L = torch.arange(t.shape[1], dtype=DTYPE)
    if nj == 2:
        tl = ((L + 1) * t[..., 1] + L * t[..., 0]) / (2 * L + 1)
    elif nj == 3:
        tl = ((2 * L + 3) * t[..., 2] + (2 * L + 1) * t[..., 1] + (2 * L - 1) * t[..., 0]) / (3 * (2 * L + 1))
    else:
        tl = t[..., 0]
    teps = torch.maximum(tl[:, :1] * translimit / (2 * L + 1), torch.tensor(transeps, dtype=DTYPE))
    small = (t[..., :nj] < teps[..., None]).all(-1)
    first = torch.where(small.any(1), small.to(torch.int64).argmax(1), torch.full((t.shape[0],), t.shape[1]))
    return first - 1
