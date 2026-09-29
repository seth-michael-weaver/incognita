#!/usr/bin/env python3
"""WP-26 M1: a differentiable Hauser-Feshbach capture layer, in torch.

The surrogate emulates TALYS; this computes the same quantity from the physics, so gradients
flow to parameters that mean something. Compact by design -- s-wave and p-wave only, no width
fluctuation, no pre-equilibrium -- because the point of M1 is a working differentiable path
from (level density, gamma strength, strength function) to a capture cross section, not a
TALYS replacement.

The statistical model in the energy range Stage C is scored on:

    sigma(n,gamma) = (pi / k^2) * sum_l (2l+1) * T_l * T_gamma / (T_l + T_gamma)

with

    T_l      neutron transmission from the measured strength function, T_l = 2 pi S_l sqrt(E) P_l
    T_gamma  gamma transmission, 2 pi <Gamma_gamma> / D, from the measured average radiation
             width and mean level spacing -- both of which RIPL-4 tabulates

Every input is a measured quantity with an uncertainty, which is the difference from a fitted
emulator: the parameters here are the ones evaluators already argue about.

Validated against the TALYS runs in the sweep rather than against itself.
"""
from __future__ import annotations

import numpy as np
import torch
from torch import Tensor

HBAR_C_FM_MEV = 197.3269804
M_N_MEV = 939.565420
R0_FM = 1.35


# WP-26 M2 calibration, fitted on pre-2012 curated capture only. See capture_xs().
CAL_SLOPE = 0.485
CAL_INTERCEPT = 0.995


def wave_number(e_mev: Tensor, a_mass: Tensor) -> Tensor:
    """Neutron wave number in the CM frame, fm^-1. Non-relativistic; fine below 20 MeV."""
    mu = M_N_MEV * a_mass / (a_mass + 1.0)
    return torch.sqrt(2.0 * mu * e_mev.clamp_min(1e-12)) / HBAR_C_FM_MEV


def penetrability(k: Tensor, a_mass: Tensor, ell: int) -> Tensor:
    """Hard-sphere penetrability for l = 0, 1. Analytic, so it differentiates cleanly."""
    rho = k * (R0_FM * a_mass ** (1.0 / 3.0))
    if ell == 0:
        return torch.ones_like(rho)
    if ell == 1:
        return rho ** 2 / (1.0 + rho ** 2)
    raise ValueError("only s- and p-wave are implemented in M1")


def capture_xs(
    e_mev: Tensor,          # (E,) incident neutron energy
    a_mass: Tensor,         # () target mass number
    s0: Tensor,             # () s-wave strength function, ABSOLUTE (e.g. 2.3e-4)
    s1: Tensor,             # () p-wave strength function, absolute
    d0_ev: Tensor,          # () s-wave mean level spacing, eV
    gg_mev: Tensor,         # () average radiation width, MeV
                            # NOTE staging/structure_params.parquet calls its column
                            # `gamma_gamma_mev` and stores milli-eV: Al-27 reads 1600 and
                            # Gamma_gamma there is 1.6 eV. Convert with *1e-9 before calling.
    calibrated: bool = False,   # apply the measured T_gamma response correction (WP-26 M2)
) -> Tensor:
    """(E,) capture cross section in barns. Differentiable in every parameter."""
    k = wave_number(e_mev, a_mass)                       # fm^-1
    # T_gamma = 2 pi <Gamma_gamma> / D, both in the same units
    d0_mev = d0_ev * 1e-6
    t_gamma = 2.0 * np.pi * gg_mev / d0_mev.clamp_min(1e-12)

    total = torch.zeros_like(e_mev)
    for ell, s_ell in ((0, s0), (1, s1)):
        # T_l = 2 pi S_l sqrt(E/1eV) P_l. S_l is ABSOLUTE here (Al-27: 2.3e-4), NOT in the
        # units of 1e-4 that RIPL *prints* -- this comment used to say the opposite of the
        # signature two lines up, and reading it instead of the signature inflates T_l by 1e4.
        p_l = penetrability(k, a_mass, ell)
        t_l = 2.0 * np.pi * s_ell * torch.sqrt(e_mev * 1e6) * p_l
        # sigma_l = (pi/k^2)(2l+1) T_l T_gamma / (T_l + T_gamma)
        frac = t_l * t_gamma / (t_l + t_gamma).clamp_min(1e-30)
        total = total + (2 * ell + 1) * frac
    # pi/k^2 in fm^2, then fm^2 -> barns (1 b = 100 fm^2)
    sigma = (np.pi / k ** 2) * total / 100.0
    if not calibrated:
        return sigma
    # WP-26 M2. Against measurement this layer does not have a normalisation error, it has a
    # RESPONSE error: log10(sigma_HF / sigma_meas) regresses on log10(T_gamma) with slope
    # +0.485, so the computed cross section scales as T_gamma while the measured one scales
    # roughly as its square root. Across T_gamma quartiles the ratio runs 0.25 to 5.3 -- a
    # factor of 21 -- and a single global factor removes almost none of it (0.758 -> 0.731).
    #
    # Fitted on pre-2012 measurements only (4,854 curated cells). Held out:
    #   post-2012 datasets (266 cells)   RMS log10 0.806 -> 0.545   (-32%)
    #   25% nuclide holdout              RMS log10 0.697 -> 0.510   (-27%)
    # It generalises better than it fits (+23% in sample), which is what an effect that is
    # real rather than absorbed noise looks like.
    #
    # This is a calibration, not new physics: it is off by default, because `capture_xs` is
    # meant to be the ab-initio layer and mixing a fit into it silently would make every later
    # comparison uninterpretable. What the exponent is *telling* us is a physics question --
    # a sub-linear response to T_gamma is what width fluctuation and channel competition both
    # produce -- and neither is implemented here yet.
    log_tg = torch.log10(t_gamma.clamp_min(1e-30))
    return sigma / 10.0 ** (CAL_SLOPE * log_tg + CAL_INTERCEPT)


def capture_xs_np(e_mev, a_mass, s0, s1, d0_ev, gg_mev, calibrated: bool = False) -> np.ndarray:
    def t(x):
        return torch.as_tensor(x, dtype=torch.float64)

    with torch.no_grad():
        return capture_xs(t(e_mev), t(a_mass), t(s0), t(s1), t(d0_ev), t(gg_mev),
                          calibrated=calibrated).numpy()
