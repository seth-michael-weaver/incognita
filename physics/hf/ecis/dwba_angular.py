"""VIBLEN: angular distributions of the one-step (DWBA) inelastic excitation of a 0+ target, for scoring only.

`directecis.f90` asks ECIS for `ecis.dirang` (the DWBA level angular distributions) but the port only ever needed the
angle-integrated `xsdirdisc`, so `ecis.dwba` sums the partial waves incoherently. This module rebuilds the coherent
amplitude from the SAME distorted waves and radial integrals (`dwba_cross_sections`'s `integral`), so its angle integral
is `dwba_cross_sections`'s cross section (checked in tests/hf/test_viblen.py), and it inherits the `parts` choice
(real-only TALYS form factor, or the complex one of `dwbaimag y`).

Amplitude (m-scheme, incident beam along z, target 0+ -> lambda M, central coupling V = F(r) Y*_{lambda M}(r^), spin-1/2
projectile with spin-orbit distortion; chi^(-)* is built from the same outgoing-wave radial functions, which is why the
radial integral carries no complex conjugate):

    T_{s' M, s}(theta) ~ sum_{l j l' j'} i^(l - l') I_{l'j', l j}
        sum_{s1} Y_l^0(z) <l 0 1/2 s|j s> <l m 1/2 s1|j s> G(l' m'; lambda M; l m) <l' m' 1/2 s1|j' mu'>
                 <l' m'' 1/2 s'|j' mu'> Y_{l'}^{m''}(theta, 0),
        m = s - s1,  m' = m - M,  mu' = m' + s1,  m'' = mu' - s',
    G = int Y_{l'}^{m'*} Y_{lambda}^{M*} Y_l^m dOmega,

    dsigma/dOmega = C sum_{s s' M} |T|^2 / 2 ,

with C fixed by requiring the angle integral to equal the incoherent sum (`sigma_mb`); `check_norm` reports the constant
computed independently from the partial-wave algebra, so the two can be compared.

Test: tests/hf/test_viblen.py (angle integral == dwba_cross_sections; plane-wave limit == Born |int j_lambda(qr) F r^2 dr|^2)
"""

from __future__ import annotations

import math
from functools import lru_cache

import numpy as np
import torch

from physics.hf.core.tensors import DTYPE
from physics.hf.core.units import MB_PER_FM2
from physics.hf.ecis import dwba as _D
from physics.hf.ecis.formfactor import DWBA_PARTS, derivative_form_factor
from physics.hf.ecis.solver import CDTYPE, channel_kinematics
from physics.hf.omp.schrodinger import (
    PARMASS_AMU, PARSPIN, PARZ, EcisKinematics, ecis_card_energy, ecis_card_value, ecis_grid, nucleus_mass_amu,
    optical_potential,
)


@lru_cache(maxsize=None)
def _fact(n: int) -> float:
    return math.lgamma(n + 1)


@lru_cache(maxsize=None)
def cg(j1: float, m1: float, j2: float, m2: float, j: float, m: float) -> float:
    """Clebsch-Gordan <j1 m1 j2 m2 | j m> (Racah), half-integers as floats."""
    if abs(m1 + m2 - m) > 1e-9 or abs(m1) > j1 + 1e-9 or abs(m2) > j2 + 1e-9 or abs(m) > j + 1e-9:
        return 0.0
    if j < abs(j1 - j2) - 1e-9 or j > j1 + j2 + 1e-9:
        return 0.0
    a = [round(x) for x in (j1 + j2 - j, j1 - j2 + j, -j1 + j2 + j, j1 + j2 + j + 1, j1 + m1, j1 - m1, j2 + m2, j2 - m2,
                            j + m, j - m)]
    if min(a) < 0:
        return 0.0
    pre = 0.5 * (math.log(2 * j + 1) + _fact(a[0]) + _fact(a[1]) + _fact(a[2]) - _fact(a[3])) + 0.5 * (
        _fact(a[4]) + _fact(a[5]) + _fact(a[6]) + _fact(a[7]) + _fact(a[8]) + _fact(a[9]))
    s = 0.0
    kmin = max(0, round(j2 - j - m1), round(j1 + m2 - j))
    kmax = min(round(j1 + j2 - j), round(j1 - m1), round(j2 + m2))
    for k in range(kmin, kmax + 1):
        d = (_fact(k) + _fact(round(j1 + j2 - j) - k) + _fact(round(j1 - m1) - k) + _fact(round(j2 + m2) - k)
             + _fact(round(j - j2 + m1) + k) + _fact(round(j - j1 - m2) + k))
        s += (-1) ** k * math.exp(pre - d)
    return s


def threej(j1, j2, j3, m1, m2, m3) -> float:
    return (-1) ** round(j1 - j2 - m3) / math.sqrt(2 * j3 + 1) * cg(j1, m1, j2, m2, j3, -m3)


@lru_cache(maxsize=None)
def gaunt_conj(lp: int, mp: int, lam: int, M: int, l: int, m: int) -> float:
    """int Y_{l'}^{m'*} Y_{lam}^{M*} Y_l^m dOmega."""
    if m - M != mp:
        return 0.0
    ph = (-1) ** (mp + M)
    return ph * math.sqrt((2 * lp + 1) * (2 * lam + 1) * (2 * l + 1) / (4 * math.pi)) * threej(lp, lam, l, 0, 0, 0) * \
        threej(lp, lam, l, -mp, -M, m)


def sph_harm(l: int, m: int, theta: np.ndarray) -> np.ndarray:
    """Y_l^m(theta, phi = 0), Condon-Shortley phase."""
    from scipy.special import lpmv
    am = abs(m)
    norm = math.sqrt((2 * l + 1) / (4 * math.pi) * math.exp(_fact(l - am) - _fact(l + am)))
    y = norm * lpmv(am, l, np.cos(theta))  # lpmv includes (-1)^m (Condon-Shortley)
    if m < 0:
        y = (-1) ** am * y
    return y


def radial_integrals(omp, Z, A, e_inc_mev, level_e_mev, level_spin, level_parity, vibbeta, deformation_length, *,
                     particle=1, refine=4, njmax=None, numl=60, parts=DWBA_PARTS, ecis_rounding=True, free_waves=False):
    """`dwba_cross_sections` up to its radial integral: (l, j, integral (n_lev, NLJ, NLJ), k (n_lev+1,), mu, njmax, sigma_mb).
    `free_waves=True` replaces the distorted waves by plane waves (optical and Coulomb potentials zero in the wave equation,
    form factor unchanged): the plane-wave Born limit used by the test."""
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
    kin = channel_kinematics(e_lab, m_proj, m_targ, z_prod, torch.cat([torch.zeros(1, dtype=DTYPE), e_lev]))
    k, kappa2, eta, mu = kin.k_fm[0], kin.kappa2[0], kin.eta[0], float(kin.mu_coef[0])
    grid_kin = EcisKinematics(ecm_mev=kin.ecm_mev[:, 0], k_fm=k[:1], eta=eta[:1], mu_coef=kin.mu_coef)
    h_t, ism, _ = ecis_grid(omp, m_targ, grid_kin)
    h = float(h_t[0]) / refine
    n = int(ism[0]) * refine
    r = h * torch.arange(0, n + 1, dtype=DTYPE)
    r_safe = r.clone(); r_safe[0] = h
    if njmax is None:
        x = 2.4 * 1.25 * (A ** (1.0 / 3.0)) * 0.22 * math.sqrt(m_proj * float(e_lab))
        njmax = min(max(20, int(x)), numl)
    lam_max = int(torch.as_tensor(level_spin).max()) if n_lev else 0
    lmax = njmax + lam_max + 1
    l, j, ls2 = _D._lj_table(lmax)
    central, so, coul = optical_potential(omp, m_targ, r_safe, z_prod)
    if free_waves:
        central, so, coul = central * 0, so * 0, coul * 0
    diag = central[0] + coul[0].to(CDTYPE)
    f_lj = ((l.to(DTYPE) * (l.to(DTYPE) + 1.0))[:, None] / r_safe[None, :] ** 2).to(CDTYPE) + mu * (
        diag[None, :] + ls2.to(CDTYPE)[:, None] * so[0][None, :])
    u = _D.distorted_waves(f_lj, kappa2, l, h, n)
    u = _D._normalise(u, f_lj, kappa2, eta, l, h)
    w = derivative_form_factor(omp, m_targ, r_safe, deformation_length, parts)[0]
    w[0] = 0.0
    wt = _D._simpson_weights(n, h)
    lhs = u * (w * wt.to(CDTYPE))[None, None, :]
    integral = torch.einsum("bpr,qr->bpq", lhs, u[0])[1:]
    return dict(l=l.numpy(), j=j.numpy(), I=integral.numpy(), k=k.numpy(), mu=mu, njmax=int(njmax), r=r_safe.numpy(),
                w=w.numpy(), u=u.numpy())


def angular_distribution(ri: dict, b: int, lam: int, parity: int, vibbeta_b: float, theta_deg: np.ndarray):
    """dsigma/dOmega (mb/sr, c.m.) of level b and its angle integral (mb), plus the incoherent (port) sigma for the check."""
    l, j, I, k = ri["l"], ri["j"], ri["I"][b], ri["k"]
    njmax = ri["njmax"]
    th = np.radians(np.asarray(theta_deg, float))
    nlj = len(l)
    ent = [c for c in range(nlj) if j[c] <= njmax + 0.5 + 1e-9]
    ex = [c for c in range(nlj)]
    halves = (-0.5, 0.5)
    amp = {}
    for s in halves:
        for sp in halves:
            for M in range(-lam, lam + 1):
                amp[(s, sp, M)] = np.zeros(len(th), dtype=complex)
    ylm_cache = {}

    def Y(lp, mpp):
        key = (lp, mpp)
        if key not in ylm_cache:
            ylm_cache[key] = sph_harm(lp, mpp, th)
        return ylm_cache[key]

    for c in ent:
        lc, jc = int(l[c]), float(j[c])
        y0 = math.sqrt((2 * lc + 1) / (4 * math.pi))
        for cp in ex:
            lp, jp = int(l[cp]), float(j[cp])
            if (lc + lp + lam) % 2 or ((-1) ** lam != parity):
                continue
            if abs(lc - lp) > lam or lc + lp < lam:
                continue
            Iv = I[cp, c]
            if Iv == 0:
                continue
            ph = (1j) ** (lc - lp)
            for s in halves:
                a1 = cg(lc, 0, 0.5, s, jc, s)
                if a1 == 0:
                    continue
                for s1 in halves:
                    m = round(s - s1)
                    a2 = cg(lc, m, 0.5, s1, jc, s)
                    if a2 == 0:
                        continue
                    for M in range(-lam, lam + 1):
                        mp = m - M
                        g = gaunt_conj(lp, mp, lam, M, lc, m)
                        if g == 0:
                            continue
                        mup = mp + s1
                        a3 = cg(lp, mp, 0.5, s1, jp, mup)
                        if a3 == 0:
                            continue
                        for sp in halves:
                            mpp = round(mup - sp)
                            if abs(mpp) > lp:
                                continue
                            a4 = cg(lp, mpp, 0.5, sp, jp, mup)
                            if a4 == 0:
                                continue
                            amp[(s, sp, M)] += ph * Iv * y0 * a1 * a2 * g * a3 * a4 * Y(lp, mpp)
    tot = sum(np.abs(a) ** 2 for a in amp.values()) / 2.0
    # incoherent (port) cross section of this level
    d = vibbeta_b / _D.SQRT4PI
    mu = ri["mu"]
    fac = math.pi / float(k[0]) ** 2 * MB_PER_FM2
    pre = (mu * d) ** 2 / (4.0 * float(k[b + 1]) * float(k[0]))
    sig = 0.0
    for c in ent:
        for cp in ex:
            if (int(l[c]) + int(l[cp]) + lam) % 2:
                continue
            w = (2 * j[c] + 1) / 2.0 * cg(j[c], -0.5, lam, 0, j[cp], -0.5) ** 2
            sig += w * abs(I[b][cp, c] if False else ri["I"][b][cp, c]) ** 2
    sig *= fac * pre
    return tot, sig


def normalised_da(ri, b, lam, parity, vibbeta_b, theta_deg, n_int=721):
    """(dsigma/dOmega mb/sr on theta_deg, sigma_port mb, raw/integral constant) normalised so int dOmega = sigma_port."""
    tg = np.linspace(0.0, 180.0, n_int)
    raw_g, sig = angular_distribution(ri, b, lam, parity, vibbeta_b, tg)
    integ = 2 * math.pi * np.trapezoid(raw_g * np.sin(np.radians(tg)), np.radians(tg))
    raw, _ = angular_distribution(ri, b, lam, parity, vibbeta_b, theta_deg)
    cst = sig / integ if integ > 0 else float("nan")
    return raw * cst, sig, cst
