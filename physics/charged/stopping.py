"""Electronic stopping of protons and alphas in elemental targets.

Bethe with the Barkas-Berger shell correction (ICRU Report 37 (1984); Leo, *Techniques for
Nuclear and Particle Physics Experiments*, 2nd ed., eq. 2.33) and the ICRU 37/49 mean
excitation energies. No density-effect term: below 100 MeV/u it is negligible for a
stopping medium this light in beta-gamma. No Barkas (z^3) or Bloch (z^4) term, and no
effective-charge reduction for alphas: those matter below ~1 MeV/u, which is below every
production threshold this module is used for except the bottom MeV of a few (p,n) routes --
and there the yield integrand is weighted by a cross section that is itself near zero.

The shell correction formula is valid for beta*gamma >= 0.13 (protons above ~8 MeV) and
diverges below it; there it is held at its eta = 0.13 value. The resulting accuracy is measured,
not assumed: ``scripts/wp25_medical_yields.py`` recomputes the IAEA's tabulated physical yields
from the IAEA's own cross sections, which isolates this module (docs/results/wp25-medical-model.md).

All functions return the stopping CROSS SECTION per atom, epsilon = (1/n) dE/dx, in
MeV cm^2. Per atom rather than per gram because a thick-target yield per incident charge is
integral sigma / epsilon dE -- the isotopic mass of an enriched target cancels, which it
would not if a natural-element S/rho were used for a 100%-enriched isotope.
"""
from __future__ import annotations

import numpy as np

ME_C2 = 0.51099895  # MeV
K = 0.307075  # 4 pi N_A r_e^2 m_e c^2, MeV cm^2 / mol
N_A = 6.02214076e23
AMU = 931.49410242  # MeV
ETA_SHELL_MIN = 0.13
PROJECTILES = {"p": (1, 1.007276466621), "d": (1, 2.013553212745), "a": (2, 4.001506179127)}

# Mean excitation energies, eV. ICRU 37 values for elements (as tabulated by NIST ESTAR/PSTAR);
# where ICRU 37 gives none, I = 9.76 Z + 58.8 Z^-0.19 (Sternheimer), marked None below.
_I_EV = {
    1: 19.2, 2: 41.8, 3: 40.0, 4: 63.7, 5: 76.0, 6: 78.0, 7: 82.0, 8: 95.0, 9: 115.0,
    10: 137.0, 11: 149.0, 12: 156.0, 13: 166.0, 14: 173.0, 15: 173.0, 16: 180.0, 17: 174.0,
    18: 188.0, 19: 190.0, 20: 191.0, 21: 216.0, 22: 233.0, 23: 245.0, 24: 257.0, 25: 272.0,
    26: 286.0, 27: 297.0, 28: 311.0, 29: 322.0, 30: 330.0, 31: 334.0, 32: 350.0, 33: 347.0,
    34: 348.0, 35: 343.0, 36: 352.0, 37: 363.0, 38: 366.0, 39: 379.0, 40: 393.0, 41: 417.0,
    42: 424.0, 43: 428.0, 44: 441.0, 45: 449.0, 46: 470.0, 47: 470.0, 48: 469.0, 49: 488.0,
    50: 488.0, 51: 487.0, 52: 485.0, 53: 491.0, 54: 482.0, 55: 488.0, 56: 491.0, 57: 501.0,
    58: 523.0, 59: 535.0, 60: 546.0, 61: 560.0, 62: 574.0, 63: 580.0, 64: 591.0, 65: 614.0,
    66: 628.0, 67: 650.0, 68: 658.0, 69: 674.0, 70: 684.0, 71: 694.0, 72: 705.0, 73: 718.0,
    74: 727.0, 75: 736.0, 76: 746.0, 77: 757.0, 78: 790.0, 79: 790.0, 80: 800.0, 81: 810.0,
    82: 823.0, 83: 823.0, 84: 830.0, 85: 825.0, 86: 794.0, 87: 827.0, 88: 826.0, 89: 841.0,
    90: 847.0, 91: 878.0, 92: 890.0,
}


def mean_excitation_ev(Z: int) -> float:
    if Z in _I_EV:
        return _I_EV[Z]
    return 9.76 * Z + 58.8 * Z ** -0.19


def shell_correction(eta: np.ndarray, I_ev: float) -> np.ndarray:
    """Barkas-Berger C (to be divided by Z); eta = beta*gamma, I in eV."""
    e2 = eta ** -2
    return ((0.422377 * e2 + 0.0304043 * e2 ** 2 - 0.00038106 * e2 ** 3) * 1e-6 * I_ev ** 2
            + (3.858019 * e2 - 0.1667989 * e2 ** 2 + 0.00157955 * e2 ** 3) * 1e-9 * I_ev ** 3)


def stopping_cross_section(E_mev, Z_target: int, projectile: str = "p",
                           shell: bool = True) -> np.ndarray:
    """epsilon(E) in MeV cm^2 per target atom, E = projectile kinetic energy in MeV."""
    z, m_u = PROJECTILES[projectile]
    M = m_u * AMU
    E = np.asarray(E_mev, dtype=float)
    gamma = 1.0 + E / M
    beta2 = 1.0 - 1.0 / gamma ** 2
    eta = np.sqrt(beta2) * gamma
    I = mean_excitation_ev(Z_target) * 1e-6  # MeV
    r = ME_C2 / M
    wmax = 2 * ME_C2 * beta2 * gamma ** 2 / (1 + 2 * gamma * r + r ** 2)
    L = 0.5 * np.log(2 * ME_C2 * beta2 * gamma ** 2 * wmax / I ** 2) - beta2
    if shell:
        # The Barkas-Berger fit is valid for eta >= 0.13 and diverges below it (as eta^-6):
        # continued naively it made gold stop a 5 MeV proton LESS than a 10 MeV one. Below
        # the validity limit the correction is held at its eta = 0.13 value, and the error
        # that leaves is measured against the IAEA recommended yields, not assumed.
        L = L - shell_correction(np.maximum(eta, ETA_SHELL_MIN), I * 1e6) / Z_target
    # K is per mole of target; divide by N_A for per atom
    eps = K / N_A * z ** 2 * Z_target / beta2 * L
    return eps


def mass_stopping_power(E_mev, Z_target: int, A_molar: float, projectile: str = "p",
                        shell: bool = True) -> np.ndarray:
    """S/rho in MeV cm^2/g (for comparison with PSTAR/ASTAR tables)."""
    return stopping_cross_section(E_mev, Z_target, projectile, shell) * N_A / A_molar
