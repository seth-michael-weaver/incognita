"""Thick-target yields: what a producer plans an irradiation with.

For a beam entering a thick target at energy ``E_in`` and leaving at ``E_out`` (0 for a
target thick enough to stop it), the production rate per incident particle is

    R/N = integral_{E_out}^{E_in} sigma(E) / epsilon(E) dE

with epsilon the stopping cross section per target atom (``physics.charged.stopping``). Per
electrical microampere the particle rate is 1e-6 / (z e). The three numbers the IAEA
recommended tables quote, and this module returns:

* physical yield, MBq/uAh -- the activity slope at the start of bombardment per unit charge,
  lambda * (3.6e-3 C / (z e)) * integral: the yield of an infinitely short irradiation;
* EOB activity after 1 h at 1 uA, MBq/uA -- R (1 - exp(-lambda 3600 s));
* saturation activity, MBq/uA -- R.

The target is taken as 100% the named isotope, which is what the IAEA tables assume.
"""
from __future__ import annotations

import numpy as np

from physics.charged.stopping import PROJECTILES, stopping_cross_section

E_CHARGE = 1.602176634e-19  # C
MB_TO_CM2 = 1e-27
LN2 = np.log(2.0)


def integral_sigma_over_eps(E_mev, xs_mb, Z_target: int, projectile: str,
                            n_sub: int = 20) -> np.ndarray:
    """Cumulative integral from the lowest energy up to each E, per incident particle.

    The cross section is interpolated LINEARLY in sigma between grid points (a log
    interpolation is undefined through the zeros below threshold, and turns a 1-MeV grid step
    across a threshold into a spurious tail) and epsilon is evaluated on a sub-grid, so a
    coarse model grid does not integrate as coarsely as it is tabulated.
    """
    E = np.asarray(E_mev, float)
    s = np.clip(np.nan_to_num(np.asarray(xs_mb, float)), 0.0, None) * MB_TO_CM2
    out = np.zeros_like(E)
    for i in range(1, len(E)):
        e = np.linspace(E[i - 1], E[i], n_sub + 1)
        sig = np.interp(e, E, s)
        eps = stopping_cross_section(np.maximum(e, 1e-3), Z_target, projectile)
        out[i] = out[i - 1] + np.trapezoid(sig / eps, e)
    return out


def thick_target_yields(E_mev, xs_mb, Z_target: int, projectile: str,
                        half_life_s: float, t_irr_s: float = 3600.0) -> dict[str, np.ndarray]:
    """Yields for a beam entering at each grid energy and stopping in the target."""
    z = PROJECTILES[projectile][0]
    lam = LN2 / half_life_s
    integ = integral_sigma_over_eps(E_mev, xs_mb, Z_target, projectile)
    per_uah = 3.6e-3 / (z * E_CHARGE)  # particles per uAh
    per_ua_s = 1e-6 / (z * E_CHARGE)  # particles per second per uA
    phys = lam * per_uah * integ / 1e6  # MBq / uAh
    sat = per_ua_s * integ / 1e6  # MBq / uA
    return {
        "phys_yield_mbq_uah": phys,
        "a1h_mbq_ua": sat * (1.0 - np.exp(-lam * t_irr_s)),
        "asat_mbq_ua": sat,
    }


def window_yield(E_mev, xs_mb, Z_target: int, projectile: str, half_life_s: float,
                 e_in: float, e_out: float) -> float:
    """Physical yield (MBq/uAh) for a target that degrades the beam from e_in to e_out."""
    E = np.asarray(E_mev, float)
    grid = np.unique(np.r_[E[(E > e_out) & (E < e_in)], e_out, e_in])
    xs = np.interp(grid, E, np.nan_to_num(np.asarray(xs_mb, float)))
    y = thick_target_yields(grid, xs, Z_target, projectile, half_life_s)["phys_yield_mbq_uah"]
    return float(y[-1] - y[0])
