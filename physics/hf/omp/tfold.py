"""TFOLD (Incognita extension, not TALYS; default ON): finite-size fold of the triton / helion optical potentials.

Physics. TALYS builds the t / 3He optical potential by Watanabe folding of the nucleon potentials but keeps the point-nucleon
geometry. Folding a Woods-Saxon form factor with the projectile's matter density (rms radius r_m = 1.74 fm for 3H and 3He, from
the measured charge radii and mirror symmetry) adds variances in quadrature to the diffuseness (TRITON3 T2):

    a' = sqrt(a^2 + (r_m / pi)^2)

on the real-volume, imaginary-volume, real-surface and imaginary-surface diffuseness (av, aw, avd, awd) of k = 4, 5; radii
unchanged. The Kalbach stripping / pickup constant `cstrip` of t and 3He is x0.99 (TRITON2's 14 MeV fit, = 1 within its CI).
No fitted number enters the fold.

Before TFOLD the same fold was carried as per-target deck lines (`avadjust/awadjust/avdadjust/awdadjust t|h f`,
`cstrip t|h 0.99`; f = sqrt(1 + (r_m / (pi a))^2) with the stock-TALYS a at that A), so a target outside the lines tables ran
WITHOUT it. The keyword reproduces those lines from the engine's own composite-particle diffuseness (energy-independent for
the KD nucleon potentials). The Fav/Faw/Favd/Fawd adjust factors multiply the folded value, as they multiplied the point value.

Keyword `tfold y|n` (default y; `n` or env INCOGNITA_TFOLD=0 = TALYS point geometry). Do not combine with the old deck lines
(double fold).

TALYS: opticalcomp.f90:1 (opticalcomp), input_preeqpar.f90:93 (cstrip)
Test: tests/hf/test_tfold.py
"""

from __future__ import annotations

import math
import os

RM_FM = 1.74  # rms matter radius of 3H and 3He
C2_FM2 = (RM_FM / math.pi) ** 2
CSTRIP_FACTOR = 0.99
KS = (4, 5)  # t, 3He
COLS = (("av_fm", "Fav"), ("aw_fm", "Faw"), ("avd_fm", "Favd"), ("awd_fm", "Fawd"))


def enabled(options) -> bool:
    if not bool(getattr(options, "tfold", True)):
        return False
    return os.environ.get("INCOGNITA_TFOLD", "").strip().lower() not in ("0", "n", "off")


def fold(a):
    """a' = sqrt(a^2 + (r_m/pi)^2) (float, numpy or torch)."""
    return (a * a + C2_FM2) ** 0.5
