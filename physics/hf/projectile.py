"""CPINC: the run's projectile (proton / alpha incident), off unless INCOGNITA_CPINC is set.

TALYS reads `projectile` once (input_main.f90:214-219) and every routine after that works off
`k0`. The port carries the k0 branches already (defaults, exciton, stripping/knockout, feeding,
incident OMP), but its call sites ask for `default_options(Z, A)` and build `Cascade(Z, A, ...)`
with the neutron defaults. This module is the one switch those defaults read:

* unset / "" / "n" -> k0 = 1, the neutron port bit for bit (nothing below changes a number);
* "p" -> k0 = 2, "a" -> k0 = 6; ENGPROJ: "d", "t", "h" -> k0 = 3, 4, 5 (breakup ported) and "g" -> k0 = 0
  (photon entrance, incidentgamma.f90).

The value is read per call, so a process must not change it between building a Cascade and
running it: every in-memory cache keyed by (Z, A) assumes ONE projectile per process. The
stage-disk cache (`INCOGNITA_STAGEDISK`) must be off for k0 != 1 runs (its keys predate CPINC).
"""

from __future__ import annotations

import os

from physics.hf.core.constants import PARN, PARSYM, PARZ

ENV = "INCOGNITA_CPINC"


def symbol() -> str:
    v = os.environ.get(ENV, "").strip().lower()
    if v in ("", "0", "n", "no", "off"):
        return "n"
    v = {"alpha": "a", "proton": "p"}.get(v, v)
    v = {"gamma": "g", "photon": "g", "deuteron": "d", "triton": "t", "helion": "h", "he3": "h"}.get(v, v)
    if v not in PARSYM:
        raise ValueError(f"{ENV}={v!r}: one of n, p, d, t, h, a, g")
    return v


def k0() -> int:
    return PARSYM.index(symbol())


def compound_of(Z: int, A: int) -> tuple[int, int]:
    """The initial compound nucleus for target (Z, A) and the run's projectile."""
    k = k0()
    return Z + PARZ[k], A + PARZ[k] + PARN[k]


def cpinc2() -> bool:
    """PORTSTACK: CPINC2's alpha fixes (stripping Kap + compound Z in stripping, spin-0 DWBA) behind
    INCOGNITA_CPINC2, so the flag switches CPINC2 alone. charged-projectile fidelity: default ON (unset = on; INCOGNITA_CPINC2=0
    restores CPINC 5d4350d1), since OFF is not TALYS. Neutron runs never reach them."""
    return os.environ.get("INCOGNITA_CPINC2", "") != "0"


def residual_nucleus(Z: int, A: int):
    """ENGPROJ GPRESFIX: the nucleus (Z, A) a residual-side photon-strength lookup must use, or None for the legacy
    pseudo-target form `(Z, A - 1)` -> `compound_of(Z, A - 1)`, which is (Z, A) only for a neutron projectile.
    For any other projectile the legacy form returns the photon strength of a NEIGHBOUR nucleus (proton: (Z+1, A),
    deuteron: (Z+1, A+1), photon: (Z, A-1)) for every residual of the cascade. Active for the ENGPROJ projectiles
    (g, d, t, h) and, since GPRESFIX (2026-10-17), p and alpha by default (INCOGNITA_GPRESFIX=0 restores the legacy
    neighbour-nucleus numbers); a neutron run is identical either way (returns None)."""
    k = k0()
    if k == 1 or not gpres_active():
        return None
    return (int(Z), int(A))


def gpres_active() -> bool:
    """ENGPROJ GPRESFIX on: the ENGPROJ projectiles (g, d, t, h) always; p / alpha by default (GPRESFIX 2026-10-17:
    TALYS calls fstrength(Zcomp, Ncomp, ...) with the decaying nucleus's own indices, densprepare.f90:310/320,
    tgamma.f90:64); INCOGNITA_GPRESFIX=0 restores the legacy p/alpha numbers. Also switches the photon-strength
    `S(Zcomp, Ncomp, k0)` (fstrength.f90:192) from the neutron's to k0's (a no-op for a neutron)."""
    return k0() in (0, 3, 4, 5) or os.environ.get("INCOGNITA_GPRESFIX", "") != "0"


def pseudo_target(Z: int, A: int) -> tuple[int, int]:
    """The (Zt, At) whose `compound_of` is (Z, A) for the run's projectile (neutron: (Z, A - 1))."""
    k = k0()
    return int(Z) - PARZ[k], int(A) - PARZ[k] - PARN[k]


def target_mass_index() -> tuple[int, int]:
    """ENGPROJ3 TARMASSFIX: the (Zix, Nix) of the TARGET in the compound-relative mass table, for the incident
    kinematics. TALYS: tarmass = nucmass(parZ(k0), parN(k0)) (nuclides.f90:239), used by energies.f90:67-77
    (eninccm, wavenum). The legacy call sites read mass_amu[0, 1] (compound minus a neutron), the target only for
    a neutron projectile: 1 amu too heavy for d, 2 for t and h, 3 for alpha (t + Fe-56 at 20 MeV: Ecm 19.007 vs
    18.973 MeV, which moves eend(k0) one bin up at 20 and 40 MeV and Etotal by +34 keV), the A-1 nucleus for a
    photon. Active for g/d/t/h; p and alpha too by default (TARMASSFIX_PROMO; proton: an isobar,
    ~1e-6 relative); INCOGNITA_TARMASSFIX=0 restores the legacy [0, 1] for p/alpha. A neutron run is identical either way."""
    k = k0()
    if k in (0, 3, 4, 5) or (k in (2, 6) and os.environ.get("INCOGNITA_TARMASSFIX", "1").strip() != "0"):
        return PARZ[k], PARN[k]
    return 0, 1


def dwba_ecis_numerics(particle: int) -> bool:
    """ENGPROJ4 DWECIS: the DWBA distorted waves and overlap with ECIS's OWN numerics (ecist.f insh / insi): the
    modified Numerov (lo(27) = F) on ECIS's grid h = min(a/2, 0.5/k), u = (z_{n-1} + 10 z_n + z_{n+1})/12, tlnc's
    matching, and the plain node sum of the first-order amplitude. The legacy port integrates the plain Numerov on
    h/4 (converged); stock is not converged where q = h^2 k_local^2 is large -- deep folded t/3He wells (V ~ 150 MeV,
    q ~ 2 inside): t + Fe-56 at 20 MeV, sum over levels, stock 30.52247, legacy 30.04253, ECIS numerics 30.52244 mb.
    On for the ENGPROJ projectiles d/t/h (`particle` = TALYS k0 3, 4, 5); n/p/alpha keep the legacy numbers (brief:
    n/p/alpha bitwise) unless INCOGNITA_DWECIS=1. Photons have no DWBA."""
    return int(particle) in (3, 4, 5) or os.environ.get("INCOGNITA_DWECIS", "") == "1"
