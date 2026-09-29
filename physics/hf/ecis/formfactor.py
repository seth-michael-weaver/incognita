"""Deformed form factors of the symmetric rotational model: the multipole expansion of a
Woods-Saxon potential whose radius is deformed, computed exactly as ECIS-06 computes it -- by a
20-point Gauss-Legendre integration over cos(theta), folded to 10 nodes by the theta -> pi-theta
symmetry of an even-multipole deformation.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.
ECIS-06 (`ecist.f`) is by J. Raynal and ships inside the TALYS repository under its MIT license;
this module ports its `rotd`/`rotp` symmetric-rotational branch and reuses T5's Woods-Saxon and
ECIS-card conventions from `physics/hf/omp/schrodinger.py`.

Task: T13 (physics/hf/CONTRACT.md §7). Acceptance test: A-inc (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    ecist.f:12262 (rotd)
    ecist.f:11889 (rotp)
    ecist.f:12950 (wosa)

Line numbers of anchors follow Python's `str.splitlines()` (what tests/hf/test_contract.py
counts); ecist.f contains form feeds, so `grep -n` gives numbers 30 lower. Line numbers quoted
in prose are `grep -n` numbers.

Two traps, both read off the Fortran and both easy to get wrong:

  * ECIS does **not** Taylor-expand in beta. `rotp-215` accumulates the potential *itself*
    (`iv = 1`, `b = 1` for the rotational model, `rotp-129`) at the shifted argument
    r - R(theta_j), so the expansion is exact to the quadrature order. Truncating at
    O(beta^2) is a different model.
  * "In the rotational models, the optical potentials (for elastic scattering) are always
    deformed" (ecist.f inpa, ecis-088). `lo(13) = F` below `soswitch` removes the spin-orbit
    *coupling* terms in `quan`, not the deformation of the diagonal spin-orbit: the lambda = 0
    form factor is still the angle-average of the deformed spin-orbit potential.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import torch
from torch import Tensor

from physics.hf.core.angmom import plegendre
from physics.hf.core.tensors import DTYPE
from physics.hf.omp.schrodinger import ECIS_CCZ_MEV_FM, SPIN_ORBIT_FACTOR, ecis_card_value

# ECIS's 20-point Gauss-Legendre rule folded to the 10 positive nodes (ecist.f:11336-11345,
# inside `pote`). `PGN` sums to 1, so sum_j PGN(j) f(x_j) = (1/2) int_-1^1 f dx for even f.
XGN: tuple[float, ...] = (
    7.65265211334973e-02, 2.27785851141645e-01, 3.73706088715420e-01, 5.10867001950827e-01,
    6.36053680726515e-01, 7.46331906460151e-01, 8.39116971822219e-01, 9.12234428251326e-01,
    9.63971927277914e-01, 9.93128599185095e-01,
)  # fmt: skip
PGN: tuple[float, ...] = (
    1.52753387130726e-01, 1.49172986472604e-01, 1.42096109318382e-01, 1.31688638449177e-01,
    1.18194531961518e-01, 1.01930119817240e-01, 8.32767415767047e-02, 6.26720483341091e-02,
    4.06014298003869e-02, 1.76140071391521e-02,
)  # fmt: skip

IQMAX = 8  # incidentecis.f90:302 / inverseecis.f90:380: maximum multipole of the expansion
LAMBDAS: tuple[int, ...] = tuple(range(0, IQMAX + 1, 2))  # 0, 2, 4, 6, 8

# (depth, reduced radius, diffuseness) field names of the six Woods-Saxon potentials, in ECIS's
# own order 1..6 (real/imaginary volume, real/imaginary surface, real/imaginary spin-orbit).
_POTENTIALS: tuple[tuple[str, str, str], ...] = (
    ("v_mev", "rv_fm", "av_fm"),
    ("w_mev", "rw_fm", "aw_fm"),
    ("vd_mev", "rvd_fm", "avd_fm"),
    ("wd_mev", "rwd_fm", "awd_fm"),
    ("vso_mev", "rvso_fm", "avso_fm"),
    ("wso_mev", "rwso_fm", "awso_fm"),
)


@dataclass(frozen=True)
class FormFactors:
    """Multipole form factors on the radial grid, in MeV, for every energy.

    `central` and `spin_orbit` are (E, NLAM, R) complex; `NLAM = len(LAMBDAS)` with `lambdas[i]`
    the multipole of slice i. `spin_orbit` is the factor that multiplies 2 l.s (T5's
    `SPIN_ORBIT_FACTOR` already folded in). `coulomb` is (E, R) real and carries no multipole
    structure: TALYS leaves `lo(11)` false for a neutron projectile, so the Coulomb potential is
    not deformed (and for a neutron it is zero).

    `so_grad` and `so_r2` are ECIS's TWO deformed spin-orbit *transition* form factors, the
    (1/r) dV/dr one and its r**-2 partner (pote-069/070, built at rotp-199/200 and stored at
    rotp-306/307). They exist only when `lo(13) = T`, i.e. E > `soswitch`, and are then addressed
    as `ity(7)+l` and `ity(7)+insl+l`. Both are (E, NLAM, R) and REAL, because TALYS never
    sets `ecis1(14:14)`, so `quan` leaves `nat(2,it) = 0` on every spin-orbit coupling and only
    the REAL spin-orbit depth enters them. They are `None` below the switch and for the
    vibrational and DWBA decks, where ECIS never builds them.
    """

    central: Tensor
    spin_orbit: Tensor
    coulomb: Tensor
    lambdas: tuple[int, ...]
    so_grad: Tensor | None = None
    so_r2: Tensor | None = None


def _ws(x: Tensor) -> tuple[Tensor, Tensor]:
    """Woods-Saxon f = 1/(1+exp(x)) and g = -a df/dr = f (1-f) at x = (r - R)/a (wosa)."""
    f = torch.sigmoid(-x)
    return f, f * (1.0 - f)


def deformed_radii(
    radius_fm: Tensor, rotbeta: Tensor, deformation_length: bool, iqm: int
) -> Tensor:
    """R_i(x_j) at ECIS's 10 angular nodes (rotd-403..431):

        R_i(x_j) = R_i ( 1 + sum_{lambda=2,4,..,iqm} s_i beta_lambda sqrt((2 lambda+1)/4 pi)
                                                        P_lambda(x_j) )

    with `s_i = 1 / R_i` when the input holds deformation *lengths* (ECIS `lo(6)`, TALYS
    `deftype == 'D'`), so the shift is the same absolute number of fermis for every potential,
    and `s_i = 1` when it holds dimensionless deformation parameters (`deftype == 'B'`).

    `radius_fm` is (E, P) with P potentials; `rotbeta` is (NROT,) with entry k the multipole
    lambda = 2(k+1). Returns (E, P, 10) in fm.

    TALYS: ecist.f:12262 (rotd)
    Test: A-inc
    """
    x = torch.tensor(XGN, dtype=DTYPE)
    pl = plegendre(iqm, x).transpose(0, 1)  # (iqm+1, 10): P_0..P_iqm at the 10 nodes
    n_rot = min(rotbeta.numel(), iqm // 2)
    shape = torch.ones(radius_fm.shape + (len(XGN),), dtype=DTYPE)
    for k in range(n_rot):
        lam = 2 * (k + 1)
        ylam = (torch.tensor(2.0 * lam + 1.0, dtype=DTYPE) / (4.0 * torch.pi)).sqrt()
        s = 1.0 / radius_fm if deformation_length else torch.ones_like(radius_fm)
        shape = shape + (s * rotbeta[k])[..., None] * ylam * pl[lam][None, None, :]
    return radius_fm[..., None] * shape


def rotational_form_factors(
    p,
    m_targ_amu: float,
    r_fm: Tensor,
    rotbeta: Tensor,
    deformation_length: bool,
    iqm: int,
    z_prod: float = 0.0,
    deformed_spin_orbit: bool = False,
) -> FormFactors:
    """The lambda = 0, 2, ..., 8 multipole form factors of the deformed optical potential
    (rotp-212..216 with the rotational-model weights of rotd-466):

        V_lambda(r) = sqrt(2 lambda + 1) sum_j PGN(j) P_lambda(x_j) V( r - R(x_j) )

    `p` carries T4's OMP parameters over an energy axis (E,); `r_fm` is (R,) or (E, R) in fm.
    The potential is T5's (`omp.schrodinger.optical_potential`): central
    -(V f_V + i W f_W) - 4 (Vd g_Vd + i Wd g_Wd) and spin-orbit (Vso + i Wso)(1/r) df_so/dr times
    ECIS's factor 2, all evaluated at the deformed argument.

    `deformed_spin_orbit` is ECIS's `lo(13)` (E > `soswitch`): it fills `so_grad` and `so_r2`,
    the two spin-orbit TRANSITION form factors. Below the switch ECIS still deforms the
    spin-orbit RADIUS -- `rotd` knows nothing about `lo(13)` -- but `redm` gives the multipoles
    no spin-orbit partner (`rotm-056`, `nsp = 0`), so the deformation survives only in the
    lambda = 0 slice of `spin_orbit`.

    TALYS: ecist.f:11889 (rotp)
    Test: A-inc
    """
    n_e = torch.as_tensor(p.v_mev).reshape(-1).numel()
    q = {}
    for d, r0, a in _POTENTIALS:
        for name in (d, r0, a):
            v = torch.as_tensor(getattr(p, name), dtype=DTYPE).reshape(-1)
            q[name] = ecis_card_value(v.expand(n_e) if v.numel() == 1 else v)
    am3 = m_targ_amu ** (1.0 / 3.0)
    radius = torch.stack([q[r0] * am3 for _, r0, _ in _POTENTIALS], dim=1)  # (E, 6)
    diffuse = torch.stack(
        [q[a].clamp_min(1.0e-6) for _, _, a in _POTENTIALS], dim=1
    )  # (E, 6)
    rdef = deformed_radii(radius, rotbeta, deformation_length, iqm)  # (E, 6, 10)

    r = r_fm[None, :] if r_fm.dim() == 1 else r_fm  # (E, R) or (1, R)
    x = torch.tensor(XGN, dtype=DTYPE)
    w = torch.tensor(PGN, dtype=DTYPE)
    pl = plegendre(IQMAX, x).transpose(0, 1)  # (IQMAX+1, 10)

    # f and g of every potential at every angular node: (E, 6, 10, R)
    arg = (r[:, None, None, :] - rdef[..., None]) / diffuse[:, :, None, None]
    f, g = _ws(arg)
    real = -q["v_mev"][:, None, None] * f[:, 0] - 4.0 * q["vd_mev"][:, None, None] * g[:, 2]
    imag = -q["w_mev"][:, None, None] * f[:, 1] - 4.0 * q["wd_mev"][:, None, None] * g[:, 3]
    central_ang = torch.complex(real, imag)  # (E, 10, R)
    dso_r = -g[:, 4] / diffuse[:, 4, None, None] / r[:, None, :]
    dso_i = -g[:, 5] / diffuse[:, 5, None, None] / r[:, None, :]
    so_ang = SPIN_ORBIT_FACTOR * torch.complex(
        q["vso_mev"][:, None, None] * dso_r, q["wso_mev"][:, None, None] * dso_i
    )

    lams = torch.tensor(LAMBDAS)
    wl = w[None, :] * pl[lams] * (2.0 * lams.to(DTYPE) + 1.0).sqrt()[:, None]  # (NLAM, 10)
    central = torch.einsum("lj,ejr->elr", wl.to(central_ang.dtype), central_ang)
    spin_orbit = torch.einsum("lj,ejr->elr", wl.to(so_ang.dtype), so_ang)

    rc = (ecis_card_value(torch.as_tensor(p.rc_fm, dtype=DTYPE).reshape(-1).expand(n_e)) * am3)[
        :, None
    ]
    if z_prod == 0.0:
        coul = torch.zeros_like(r).expand(n_e, r.shape[-1]).contiguous()
    else:
        e2z = ECIS_CCZ_MEV_FM * z_prod
        rcs = rc.clamp_min(1.0e-6)
        coul = torch.where(r < rc, e2z / (2.0 * rcs) * (3.0 - (r / rcs) ** 2), e2z / r)
    so_grad = so_r2 = None
    if deformed_spin_orbit:
        # rotp-199/200, the two lines that make potential 5 into potentials 5 and 9:
        #     vr(k,i+4) = vr(k,i) / r**2        (the r**-2 partner, stored NEGATED at rotp-307)
        #     vr(k,i)   = vr(k+1,i) / r         ((1/r) dV/dr, wosa's v(2) = -f')
        # Both carry ECIS's spin-orbit factor 2 (quan-267/303 `at(2,it) = 2*a*a2`), which the
        # port keeps inside the form factor as `SPIN_ORBIT_FACTOR`, and both are REAL: TALYS
        # leaves `ecis1(14:14)` false, so `quan` never fills `nat(2,it)` for a spin-orbit term.
        # The sign of `so_r2` is ECIS's `-p(25,k)` composed with the port's opposite sign
        # convention for the potential itself, i.e. `+` here.
        vso = q["vso_mev"][:, None, None]
        g1 = SPIN_ORBIT_FACTOR * vso * (-g[:, 4] / diffuse[:, 4, None, None]) / r[:, None, :]
        g2 = SPIN_ORBIT_FACTOR * vso * f[:, 4] / r[:, None, :] ** 2
        so_grad = torch.einsum("lj,ejr->elr", wl, g1)
        so_r2 = torch.einsum("lj,ejr->elr", wl, g2)
    return FormFactors(
        central=central, spin_orbit=spin_orbit, coulomb=coul, lambdas=LAMBDAS,
        so_grad=so_grad, so_r2=so_r2,
    )


# The eight potentials ECIS holds, in `val(*,i)` order, and the `ldl` map of rotp-082 from
# potential i to the `lo` flag that says whether it is deformed:
#     ldl / 7, 12, 7, 12, 13, 14, 11, 19 /,  lq(i,5) = .not. lo(ldl(i))  except lo(7), which is
# used straight (rotp-087/088).  lo(7) ("form factors read") is always false, so the two REAL
# central potentials are always deformed; the two imaginary ones only when `lo(12)`.
#   * `incidentecis.f90:257` sets ecis1(12:12) = 'T'  -> stage a1 deforms the imaginary potential.
#   * `directecis.f90:133` leaves it 'F'              -> the DWBA transition form factor is REAL.
DWBA_PARTS: tuple[str, ...] = ("v", "vd")  # real volume, real surface
ALL_CENTRAL_PARTS: tuple[str, ...] = ("v", "w", "vd", "wd")


def derivative_form_factor(
    p,
    m_targ_amu: float,
    r_fm: Tensor,
    deformation_length: bool,
    parts: tuple[str, ...] = DWBA_PARTS,
) -> Tensor:
    """The vibrational (one-phonon) transition form factor of `rotp-127..133`, divided by the
    deformation itself, i.e. the per-unit-deformation shape

        W(r) = sum_m s_m dU_m/dr,     s_m = 1 (deformation length, `lo(6)`) or R_m (beta),

    so that the ECIS form factor of a one-phonon level with deformation `d` is

        F(r) = (d / sqrt(4 pi)) W(r)          (`b(j,i) = sr**k * 0.282095 * beta / srd(k+1)`
                                               with k = 1, srd(2) = 1, sr = 1 or R_m)

    `parts` selects which Woods-Saxon terms are deformed; the DWBA default is the two REAL ones
    (see `DWBA_PARTS`). Returns (E, R) complex in MeV/fm.

    This is exactly the first-order term of `rotational_form_factors`: expanding
    V_lambda(r) = sqrt(2 lambda+1) sum_j PGN_j P_lambda(x_j) V(r - R(x_j)) to first order in the
    deformation and using sum_j PGN_j P_lambda(x_j)^2 = 1/(2 lambda+1) gives
    -(delta_lambda / sqrt(4 pi)) dV/dr, with no lambda left in it. `tests/hf/test_ecis.py`
    pins the two against each other.

    TALYS: ecist.f:11889 (rotp), directecis.f90:1 (directecis)
    Test: A-direct
    """
    n_e = torch.as_tensor(p.v_mev).reshape(-1).numel()
    q = {}
    for d, r0, a in _POTENTIALS:
        for name in (d, r0, a):
            v = torch.as_tensor(getattr(p, name), dtype=DTYPE).reshape(-1)
            q[name] = ecis_card_value(v.expand(n_e) if v.numel() == 1 else v)
    am3 = m_targ_amu ** (1.0 / 3.0)
    r = r_fm[None, :] if r_fm.dim() == 1 else r_fm
    idx = {"v": 0, "w": 1, "vd": 2, "wd": 3}
    out_re = torch.zeros(r.expand(n_e, r.shape[-1]).shape, dtype=DTYPE)
    out_im = torch.zeros_like(out_re)
    for name in parts:
        depth, r0, a = _POTENTIALS[idx[name]]
        R = (q[r0] * am3)[:, None]
        aa = q[a].clamp_min(1.0e-6)[:, None]
        f, g = _ws((r - R) / aa)
        s = torch.ones_like(R) if deformation_length else R
        if name in ("v", "w"):  # volume: U = -V f, dU/dr = V g / a
            d = s * q[depth][:, None] * g / aa
        else:  # surface: U = -4 Vd g, dg/dr = -g(1-2f)/a, so dU/dr = +4 Vd g (1 - 2f) / a.
            # The sign RELATIVE to the volume term matters: it is the only thing that tells the
            # two apart in W(r), and ECIS builds it the same way (`vr(k,i) = 4 vr(k+1,i) val(3,i)`,
            # rotp-195, one derivative further along the same Woods-Saxon).
            d = 4.0 * s * q[depth][:, None] * g * (1.0 - 2.0 * f) / aa
        if name in ("v", "vd"):
            out_re = out_re + d
        else:
            out_im = out_im + d
    return torch.complex(out_re, out_im)


def second_derivative_form_factor(
    p,
    m_targ_amu: float,
    r_fm: Tensor,
    deformation_length: bool,
    parts: tuple[str, ...] = ALL_CENTRAL_PARTS,
) -> Tensor:
    """The SECOND-order vibrational form factor of `rotp-119..125`, divided by the deformations:

        W2(r) = sum_m s_m^2 d2U_m/dr2,     s_m = 1 (deformation length) or R_m (beta),

    so that ECIS's second-order form factor for the phonon pair (i, j) is

        F_ij(r) = (1/2) (beta_i / sqrt(4 pi)) (beta_j / sqrt(4 pi)) W2(r)

    -- `b(j,i) = 0.0397887 * beta(j,k1) * beta(j,k2) * sr * sr` with `iv(i) = 3`, i.e. the second
    derivative, and `0.0397887 = 1/(8 pi) = (1/sqrt(4 pi))^2 / 2` (rotp-119..125). This is the
    exact partner of `derivative_form_factor`, which is the same sum with one derivative and one
    factor of `1/sqrt(4 pi)`.

    It is the form factor ECIS's `lo(2)` branch needs, which TALYS switches on
    (`ecis1(2:2) = 'T'`, incidentecis.f90:244) as soon as a level has two phonons. Nothing calls
    it yet: `ecis.incident` still raises on such a target and the rest of the two-phonon port is
    specified in `docs/results/hf-ecis-twophonon.md`. It is here, and tested against a numerical
    second derivative of `omp.schrodinger.optical_potential`, because it is the one piece of that
    port that can be written and checked with nothing else in place.

    In the port's `_ws` variables (`f = sigmoid(-(r-R)/a)`, `g = f (1-f)`):

        volume   U = -V f    ->  d2U/dr2 = -V (1 - 2f) g / a^2
        surface  U = -4 Vd g ->  d2U/dr2 = 4 Vd g (2 g - (1 - 2f)^2) / a^2

    Returns (E, R) complex in MeV/fm^2.

    TALYS: ecist.f:11889 (rotp), ecist.f:12950 (wosa)
    Test: tests/hf/test_ecis.py
    """
    n_e = torch.as_tensor(p.v_mev).reshape(-1).numel()
    q = {}
    for d, r0, a in _POTENTIALS:
        for name in (d, r0, a):
            v = torch.as_tensor(getattr(p, name), dtype=DTYPE).reshape(-1)
            q[name] = ecis_card_value(v.expand(n_e) if v.numel() == 1 else v)
    am3 = m_targ_amu ** (1.0 / 3.0)
    r = r_fm[None, :] if r_fm.dim() == 1 else r_fm
    idx = {"v": 0, "w": 1, "vd": 2, "wd": 3}
    out_re = torch.zeros(r.expand(n_e, r.shape[-1]).shape, dtype=DTYPE)
    out_im = torch.zeros_like(out_re)
    for name in parts:
        depth, r0, a = _POTENTIALS[idx[name]]
        R = (q[r0] * am3)[:, None]
        aa = q[a].clamp_min(1.0e-6)[:, None]
        f, g = _ws((r - R) / aa)
        s = torch.ones_like(R) if deformation_length else R
        if name in ("v", "w"):
            d = -(s * s) * q[depth][:, None] * (1.0 - 2.0 * f) * g / (aa * aa)
        else:
            d = 4.0 * (s * s) * q[depth][:, None] * g * (2.0 * g - (1.0 - 2.0 * f) ** 2) / (aa * aa)
        if name in ("v", "vd"):
            out_re = out_re + d
        else:
            out_im = out_im + d
    return torch.complex(out_re, out_im)


def vibrational_form_factors(
    p,
    m_targ_amu: float,
    r_fm: Tensor,
    vib_beta: Tensor,
    deformation_length: bool,
    z_prod: float = 0.0,
) -> FormFactors:
    """Form factors of the harmonic one-phonon vibrational model (`colltype V`), as
    `incidentecis.f90:261-268` asks for them: slice 0 is the undeformed potential and slice k is
    the transition form factor of band k,

        F_k(r) = (delta_k / sqrt(4 pi)) sum_m s_m dU_m/dr        (rotp-127..133 with `iv = 2`)

    `vib_beta` is (NB,) -- TALYS's `defpar` per band, a deformation length when
    `deformation_length`. The incident deck sets `ecis1(12:12) = 'T'` (incidentecis.f90:257), so
    unlike the DWBA deck ALL FOUR central terms are deformed; it never sets `ecis1(13:13)` for a
    vibrational target, so the spin-orbit is not, and only slice 0 of `spin_orbit` is non-zero.

    `lambdas` here is a placeholder `(0, 1, 2, ...)`: for the vibrational model a slice is a BAND,
    not a multipole, and its multipole lives in the coupling matrix (`coupling.vibrational_channels`).

    TALYS: ecist.f:11889 (rotp), incidentecis.f90:1 (incidentecis)
    Test: A-inc
    """
    n_e = torch.as_tensor(p.v_mev).reshape(-1).numel()
    r = r_fm[None, :] if r_fm.dim() == 1 else r_fm
    n_r = r.shape[-1]
    plain = rotational_form_factors(
        p, m_targ_amu, r_fm, torch.zeros(0, dtype=DTYPE), deformation_length, 0, z_prod
    )
    w = derivative_form_factor(p, m_targ_amu, r_fm, deformation_length, ALL_CENTRAL_PARTS)
    nb = int(vib_beta.numel())
    central = torch.zeros((n_e, nb + 1, n_r), dtype=plain.central.dtype)
    central[:, 0] = plain.central[:, 0]
    for k in range(nb):
        central[:, k + 1] = (vib_beta[k] / math.sqrt(4.0 * torch.pi)) * w
    so = torch.zeros((n_e, nb + 1, n_r), dtype=plain.spin_orbit.dtype)
    so[:, 0] = plain.spin_orbit[:, 0]
    return FormFactors(
        central=central, spin_orbit=so, coulomb=plain.coulomb, lambdas=tuple(range(nb + 1))
    )


def anharmonic_vibrational_form_factors(
    p,
    m_targ_amu: float,
    r_fm: Tensor,
    band_beta: Tensor,
    codes: tuple[int, ...],
    nbt1: int,
    deformation_length: bool,
    z_prod: float = 0.0,
) -> FormFactors:
    """Form factors of the SECOND-order vibrational model (`ecis1(2:2) = 'T'`,
    incidentecis.f90:244): slice 0 is the undeformed potential and slice `1 + q` is the form
    factor `vibm` addresses as `codes[q]`,

        code <= nbt1 :  F(r)  = -(beta_code / sqrt(4 pi)) sum_m s_m dU_m/dr        (rotp `iv = 2`)
        code >  nbt1 :  F(r)  = +(beta_k1 beta_k2 / (8 pi)) sum_m s_m^2 d2U_m/dr2  (rotp `iv = 3`)

    with `(k1, k2) = (code mod (nbt1+1), code / (nbt1+1))` (rotp-119..120), `s_m = 1` for
    deformation lengths and `R_m` otherwise (rotp-116/124), and `U` the port's optical potential
    -- the NEGATIVE of the quantity ECIS accumulates.

    **The two signs are the whole trap, so here is where they come from.** `wosa` returns
    `v(k) = (-1)^(k-1) d^(k-1) f / dr^(k-1)` of a Woods-Saxon `f` (wosa-021..028: `c = exp(x)`,
    `b = 1/(1+c) = f`, `v(2) = f^2 c / a = g/a = -f'`), and `rotp-190/195` scales it into
    `vr(k,m) = (-1)^(k-1) d^(k-1)(-U_m)/dr^(k-1)`. `rotp-215` then accumulates `b(m,l) vr(iv(l),m)`
    with `b > 0` for both orders, so in terms of the port's own `U`:

        ECIS form factor 1     = -U                       (the plain potential, negated)
        ECIS first order       = +0.282095 beta  sum s dU/dr
        ECIS second order      = -0.0397887 b_i b_j sum s^2 d2U/dr2

    The port's slice 0 is `+U`, i.e. the whole stack is ECIS's times -1 -- which is why the two
    transition slices here carry the signs they do. Flipping the first-order sign relative to
    `vibrational_form_factors` is not a change of physics: the harmonic port takes ECIS's
    `t = -1` (vibm-161) as `+1` and pays for it with the opposite form-factor sign, and
    `tests/hf/test_ecis.py` pins the two products against each other. The second-order sign is
    the one that cannot be absorbed, and it is checked against the closed form of the
    angle-averaged deformed potential: `<U(r - delta)> - U(r) = (1/2)<delta^2> U''`, with
    `<delta^2> = s^2 beta^2 / (4 pi)`, is exactly the ground-state diagonal that `vibm`'s case 1
    (`t = 1`, `lambda = 0`) plus `quan`'s `1/sqrt(2I+1)` builds out of this slice.

    `band_beta` is 1-based, entry 0 unused: `band_beta[b]` is the `vibbeta` of phonon b.
    `incidentecis.f90:257` sets `ecis1(12:12) = 'T'`, so all four central terms are deformed at
    both orders and the spin-orbit at neither.

    TALYS: ecist.f:11889 (rotp), incidentecis.f90:1 (incidentecis)
    Test: G-2PH
    """
    from physics.hf.ecis.vibm import decode_code

    n_e = torch.as_tensor(p.v_mev).reshape(-1).numel()
    r = r_fm[None, :] if r_fm.dim() == 1 else r_fm
    n_r = r.shape[-1]
    plain = rotational_form_factors(
        p, m_targ_amu, r_fm, torch.zeros(0, dtype=DTYPE), deformation_length, 0, z_prod
    )
    first = second = None
    central = torch.zeros((n_e, len(codes) + 1, n_r), dtype=plain.central.dtype)
    central[:, 0] = plain.central[:, 0]
    for q, code in enumerate(codes):
        ks = decode_code(int(code), nbt1)
        if len(ks) == 1:
            if first is None:
                first = derivative_form_factor(
                    p, m_targ_amu, r_fm, deformation_length, ALL_CENTRAL_PARTS
                )
            central[:, q + 1] = -(band_beta[ks[0]] / math.sqrt(4.0 * torch.pi)) * first
        else:
            if second is None:
                second = second_derivative_form_factor(
                    p, m_targ_amu, r_fm, deformation_length, ALL_CENTRAL_PARTS
                )
            scale = band_beta[ks[0]] * band_beta[ks[1]] / (8.0 * torch.pi)
            central[:, q + 1] = scale * second
    so = torch.zeros((n_e, len(codes) + 1, n_r), dtype=plain.spin_orbit.dtype)
    so[:, 0] = plain.spin_orbit[:, 0]
    return FormFactors(
        central=central, spin_orbit=so, coulomb=plain.coulomb,
        lambdas=tuple(range(len(codes) + 1)),
    )
