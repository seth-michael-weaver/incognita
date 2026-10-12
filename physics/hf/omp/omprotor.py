"""OMPROTOR (Incognita extension, not TALYS): coupled-channels smearing un-fold of the KD03 neutron surface diffuseness.

TALYS couples every `colltype R` target (A >= 140, Z < 90: the rare-earth rotors; the actinides get RIPL 2408) in rigid-rotor CC with
the global SPHERICAL KD03 potential deformed explicitly, R(theta) = R0 (1 + beta2 Y20 + beta4 Y40). KD03's diffuseness is already
an orientation-averaged "equivalent spherical" one, so the explicit deformation smears the surface a second time. The orientation
average of a Woods-Saxon of radius R(theta) is the spherical profile convolved with a Gaussian of variance R0^2 sum(beta^2)/(4 pi); the
WS derivative has variance pi^2 a^2 / 3. The intrinsic diffuseness the deformed potential should carry is therefore

    a0^2 = a_KD^2 - 3 R^2 (beta2^2 + beta4^2) / (4 pi^3)        (no fitted parameter)

with R = r A^(1/3) and a of each KD03 geometry, beta2/beta4 from the HFB mass table (what deformpar.f90 hands ECIS as rotbeta).

Modes (keyword `omprotor <mode>` or env INCOGNITA_OMPROTOR when the keyword is absent/`n`):
  n    = OFF (TALYS; the default, bit-identical)
  unf1 = volume (avadjust n) and surface (awdadjust n, avdadjust n) un-folded   (OMPROTOR arm UNF1)
  unfv = volume only (avadjust n)                                              (OMPROTOR diagnostic UNFV)
Each factor f = sqrt(1 - c R^2 s / a^2), floored at 0.3, written as the per-particle cards `avadjust n f` ... rounded to 5 decimals,
exactly the lines OMPROTOR's runs carried (development notes), and put on the run through the fitted-lines
route (`fitlib`) AFTER the run's own lines, like those runs' extra lines. Incident channel only, as every `Xadjust n` (TALYS
flagompejec n). Note what the cards do on that route: they are written after TALYS's post-loop links, so `awadjust` does NOT follow
`avadjust` (the volume imaginary diffuseness stays KD03's); that is what OMPROTOR measured and what is reproduced here.
Test: tests/hf/test_omprotor.py
"""

from __future__ import annotations

import math
import os
from functools import lru_cache

ENV_OMPROTOR = "INCOGNITA_OMPROTOR"
CPHYS = 3.0 / (4.0 * math.pi ** 3)
FLOOR = 0.3
MODES = {"n": None, "unf1": "vs", "unfv": "v"}


def mode(options=None) -> str:
    """The run's mode: the keyword if set (not `n`), else the environment, else `n`."""
    v = str(getattr(options, "omprotor", "n") or "n").strip().lower()
    if v in ("", "n", "no", "0"):
        v = os.environ.get(ENV_OMPROTOR, "").strip().lower() or "n"
        if v in ("no", "0", "off"):
            v = "n"
    if v not in MODES:
        raise ValueError(f"omprotor: unknown mode {v!r} (one of {sorted(MODES)})")
    return v


def env_mode() -> str:
    return os.environ.get(ENV_OMPROTOR, "").strip().lower()


def factors(A: int, beta2: float, beta4: float, c: float = CPHYS) -> tuple[float, float, bool]:
    """(f_volume, f_surface, floored) for the KD03 neutron geometry of target mass A (omppar.f90:240-249)."""
    A = float(A)
    a13 = A ** (1 / 3)
    s = beta2 * beta2 + beta4 * beta4
    rv, av = 1.3039 - 0.4054 / a13, 0.6778 - 1.487e-4 * A
    rd, ad = 1.3424 - 0.01585 * a13, 0.5446 - 1.656e-4 * A
    out, fl = [], False
    for r, a in ((rv, av), (rd, ad)):
        R = r * a13
        x = 1.0 - c * R * R * s / (a * a)
        f = math.sqrt(x) if x > FLOOR ** 2 else FLOOR
        fl |= x <= FLOOR ** 2
        out.append(f)
    return out[0], out[1], fl


@lru_cache(maxsize=512)
def hfb_beta(Z: int, A: int) -> tuple[float, float]:
    from physics.hf.structure.files import read_mass_file

    row = read_mass_file(int(Z), "hfb").get(int(A))
    return (0.0, 0.0) if row is None else (float(row[2]), float(row[3]))


def lines(Z: int, A: int, m: str) -> tuple[str, ...]:
    """The keyword cards mode `m` puts on a run with target (Z, A); () for OFF and for non-members."""
    kind = MODES[m]
    if kind is None:
        return ()
    from physics.hf.omp.regional import deformed_member

    if not deformed_member(int(Z), int(A)):
        return ()
    b2, b4 = hfb_beta(int(Z), int(A))
    fv, fd, _ = factors(int(A), b2, b4)
    out = [f"avadjust n {fv:.5f}"]
    if "s" in kind:
        out += [f"awdadjust n {fd:.5f}", f"avdadjust n {fd:.5f}"]
    return tuple(out)
