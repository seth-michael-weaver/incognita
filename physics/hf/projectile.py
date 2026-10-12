"""CPINC: the run's projectile (proton / alpha incident), off unless INCOGNITA_CPINC is set.

TALYS reads `projectile` once (input_main.f90:214-219) and every routine after that works off
`k0`. The port carries the k0 branches already (defaults, exciton, stripping/knockout, feeding,
incident OMP), but its call sites ask for `default_options(Z, A)` and build `Cascade(Z, A, ...)`
with the neutron defaults. This module is the one switch those defaults read:

* unset / "" / "n" -> k0 = 1, the neutron port bit for bit (nothing below changes a number);
* "p" -> k0 = 2, "a" -> k0 = 6 (also "d", "t", "h" are accepted by the switch, but only p and
  alpha are in scope of CPINC: deuteron breakup, `preeq.complex` k0 = 3, is not ported).

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
    if v not in PARSYM or v == "g":
        raise ValueError(f"{ENV}={v!r}: one of p, a (d, t, h untested)")
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
