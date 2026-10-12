"""ENGPHYS: four consistency guards for TALYS behaviour far from stability. All OFF by default.

ENGPHYS (2026-09-27) found that stock TALYS-2.25 and the port share three defect classes on the far chart:

* **DWBA unitarity** -- first-order DWBA to a strongly collective default 2+ level in a weakly absorbing OMP
  gives a direct cross section larger than the reaction cross section (n+Am-308 at 0.336 MeV: 3.1e5 mb vs
  1411 mb; n+U-248 at 1.38 MeV: 3948 vs 3870). The excess flows into (n,n') or, for an unbound level, (n,2n).
* **Soukhovitskii Fermi energy** -- `soukhovitskii.f90` takes `Ef = -(S_n(A) + S_n(A+1))/2` from the mass
  table. At the neutron drip line Ef -> 0, so its (E - Ef)^2 imaginary terms vanish and the potential is
  almost real (Am-308: Wd 0.04 MeV at 0.34 MeV). Only Z >= 90 uses it, which is why every x6-x313 case is Z >= 91.
* **Pre-equilibrium spin spread** -- binary.f90:236-257 spreads each continuum bin's pre-equilibrium
  population over (J, parity) with the compound spin distribution where that cell holds compound flux and
  with the Wigner distribution elsewhere, cell by cell; the mixture sums to more than 1 per bin when the
  compound population has holes (low-Sn heavy nuclei), which puts 1-2.5 % more flux into the residuals than
  the reaction cross section holds.

Switches (each `=1` to enable; `INCOGNITA_ENGPHYS=all` enables all four, or a comma list of the short names):

  INCOGNITA_DIRCAP          (dircap)  non-coupled direct (DWBA discrete + giant resonances + collective continuum)
                                    scaled so it never exceeds the flux the coupled channels leave,
                                    sigma_R - sum(coupled) (strict unitarity, no free constant).
  INCOGNITA_SOUKHO_EFCLAMP  (efermi)  Soukhovitskii Fermi energy no higher than the Koning-Delaroche (2003) global
                                    systematics for the same A: Ef = min(Ef_mass, -11.2814 + 0.02646 A) (n),
                                    min(Ef_mass, -8.4075 + 0.01378 A) (p). Leaves stable actinides unchanged.
  INCOGNITA_DEF_EVENEVEN    (oddodd)  the vibrational 2+/3-/4+ deformation systematics of deformpar.f90 (and its
                                    0.02 default for other natural-parity levels) apply to even-even nuclei only;
                                    odd-odd nuclei are treated as TALYS treats odd-A ones (no default collectivity).
  INCOGNITA_PESPIN_NORM     (pespin)  the pre-equilibrium (J, parity) spread of each continuum bin is renormalised to
                                    sum to 1, so the bin receives exactly its pre-equilibrium population.
"""
from __future__ import annotations

import os

SWITCHES = {"dircap": "INCOGNITA_DIRCAP", "efermi": "INCOGNITA_SOUKHO_EFCLAMP",
            "oddodd": "INCOGNITA_DEF_EVENEVEN", "pespin": "INCOGNITA_PESPIN_NORM"}


def on(name: str) -> bool:
    """True when switch `name` (a key of SWITCHES) is enabled in the environment."""
    if os.environ.get(SWITCHES[name], "0") == "1":
        return True
    v = os.environ.get("INCOGNITA_ENGPHYS", "").strip().lower()
    if v in ("", "0", "off", "none"):
        return False
    s = {x.strip() for x in v.split(",") if x.strip()}
    bad = s - set(SWITCHES) - {"all"}
    if bad:
        raise ValueError(f"INCOGNITA_ENGPHYS: unknown switch(es) {sorted(bad)}; known {sorted(SWITCHES)}")
    return "all" in s or name in s


def active() -> tuple[str, ...]:
    return tuple(k for k in SWITCHES if on(k))


def kd03_fermi(k: int, A: int) -> float:
    """Koning-Delaroche (2003) global Fermi energy [MeV], k = 1 neutron, 2 proton."""
    return -11.2814 + 0.02646 * A if k == 1 else -8.4075 + 0.01378 * A


def soukho_fermi(k: int, A: int, eferm: float) -> float:
    """The Fermi energy the Soukhovitskii potential uses: TALYS's mass-table value, clamped under `efermi`."""
    if not on("efermi"):
        return eferm
    return min(float(eferm), kd03_fermi(k, A))


def spread_norm_np(pop_before, pop_after, rows, ppx):
    """`pespin`: rescale what the pre-equilibrium step added to rows `rows` of pop (N, J, 2) so each row's addition
    sums to ppx[row]. numpy, in place on pop_after."""
    import numpy as np
    for r in rows:
        add = pop_after[r] - pop_before[r]
        s = add.sum()
        if s > 0.0 and ppx[r] > 0.0:
            pop_after[r] = pop_before[r] + add * (ppx[r] / s)
    return pop_after


def spread_norm_torch(spread, ppx_rows):
    """`pespin`: normalise a (rows, J, 2)-shaped spread over (J, parity) per row (torch); rows with no weight stay."""
    import torch
    s = spread.sum(dim=tuple(range(1, spread.dim())), keepdim=True)
    return torch.where(s > 0, spread / torch.where(s > 0, s, torch.ones_like(s)), spread)
