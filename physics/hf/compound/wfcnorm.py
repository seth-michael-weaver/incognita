"""Incognita extension (FIXENG F15; not TALYS): compound flux conservation in the binary step.

Env INCOGNITA_WFCNORM=1; default OFF, and OFF never changes a number.

Two leaks put flux into the reaction cross section that lands in no exclusive channel (nonelastic = sigma_R - compound
elastic, so the leak shows as nonelastic != sum of channels wherever compound elastic dwarfs the nonelastic: keV O-16
x0.04, Ca-52/Xe-140 x0.1):
* A. Width fluctuations (Moldauer, widthmode 1): the exact Moldauer integral conserves flux, the 32-point
  Gauss-Laguerre rule TALYS evaluates it with does not when one neutron channel dominates; the decays of a (J, parity)
  cell then sum to (1 - 2..3e-4) of its formation and the missing flux is mostly compound elastic. Fix: with width
  fluctuations on, the compound decays of each incident energy (every population cell, compound elastic included, and
  first-chance fission) are scaled to the compound formation cross section `xsflux` they were formed with.
* B. Coupled-channels targets (compnorm.f90:163-166): the flux is taken from pi/k^2 * sum T at the true energy while
  ECIS solved, and sigma_R was taken, at the card-rounded energy (`schrodinger.ecis_card_energy`, 3 significant digits
  below 10 keV): the compound flux is off by E_card/E (Cr-52 at 1.603 keV: +2.8e-4, nonelastic 3.5 % below the channels).
  Fix: k at the card energy in `chained_formation` for the coupled-channels branch.

Both act in one place each on every path (Py loop / batched / C kernel through `target._case`; the chart C engine
through `engine_c`; `chained_formation` is shared by all).
Test: tests/hf/test_wfcnorm.py
"""

from __future__ import annotations

import os

ENV = "INCOGNITA_WFCNORM"


def enabled() -> bool:
    return os.environ.get(ENV, "0").lower() in ("1", "y", "yes")


def factor(pop_sum: float, xs_fis: float, xsflux_mb: float) -> float:
    """xsflux / (sum of the compound decays), or 1 where there is nothing to scale."""
    d = float(pop_sum) + float(xs_fis)
    f = float(xsflux_mb)
    if not (d > 0.0 and f > 0.0):
        return 1.0
    return f / d
