"""ACTPHYS: actinide-only photon-strength corrections for the keV capture deficit, off by default.

TALYS-2.x's default photon strength (SMLO-2019 E1 + its M1) gives U-239 a theoretical s-wave
<Gamma_gamma> of 11.2 meV against 23.6 meV measured (RIPL-3), and U-238 capture sits 0.12-0.22 dex
low from 10 keV to 1 MeV (ACTSC, ACTFOLD). `INCOGNITA_ACTPHYS` switches on, for nuclei with
Z >= ZMIN (88) only:

* ``gg``   -- the E1 ftable default of each nucleus with a RIPL-3 s-wave <Gamma_gamma> is set to
  the factor that makes TALYS's theoretical <Gamma_gamma> equal it (what `gnorm y` would do
  without its keV/eV bug, GNORMFIX). Nuclei with no RIPL-3 width keep ftable 1.
* ``sc``   -- the Kopecky-2017 M1 scissors (PORTLEVER's `gamma/scissors.py` term) replaces
  SMLO-2019's scissors, Z >= ZMIN only.
* ``both`` -- ``sc`` plus the ``gg`` factors re-derived WITH the Kopecky scissors in place, so
  <Gamma_gamma> is again the RIPL-3 value and the scissors only reshapes the spectrum.

Factors: `scripts/actphys/gamgam.py` (stock TALYS, `docs/results/actphys/gamgam.json`), keyed by
the nucleus whose PSF they scale (the compound nucleus of target A-1). Unlike TALYS's `gnorm`,
which normalises only the initial compound nucleus, the factor applies wherever that nucleus's
strength is built, so all engine paths agree whatever (zix, nix) they pass. A user/PARAMWIRE
`ftable` still replaces the default, as a TALYS keyword does. Z < ZMIN is never touched, so
non-actinide output is bit-identical with the switch on or off.

The width source is the `Gg(RIPL-3)` column of RIPL-4's resonances_L0.dat (Capote et al., NDS
110 (2009) 3107; Mughabghab 2006), which predates every scored (post-2012) EXFOR bin.
"""

from __future__ import annotations

import os

ZMIN = 88
MODES = ("", "gg", "sc", "both")

# (Z, A of the nucleus): (factor at SMLO-2019 scissors, factor at Kopecky-2017 scissors)
GG_FACTOR: dict[tuple[int, int], tuple[float, float]] = {
    (88, 227): (1.7687952912620353, 0.4253785132868003),  # RIPL-3 26.0 meV; TALYS 18.58 / k17 31.55
    (90, 231): (1.2899066109083852, 0.36324854146195085),  # 26.0 meV; 22.47 / 33.74
    (90, 233): (1.780644842317693, 0.9398631163668196),  # 24.0 meV; 17.05 / 24.54
    (91, 232): (1.135848922634371, 0.37639558271387885),  # 40.0 meV; 37.09 / 53.35
    (91, 234): (2.136804245881725, 1.4630602441414773),  # 47.0 meV; 28.64 / 39.52
    (92, 234): (1.5407079902418108, 0.8472196146330948),  # 40.0 meV; 30.67 / 42.64
    (92, 235): (0.5766975510245096, 0.1763879537605556),  # 26.0 meV; 36.11 / 45.67
    (92, 236): (2.0869445644326934, 1.4608982761790452),  # 38.0 meV; 23.46 / 31.83
    (92, 237): (1.1581495404459312, 0.6017326692124441),  # 23.0 meV; 21.17 / 27.62
    (92, 239): (3.2215738995205436, 2.6316048142634205),  # 23.6 meV; 11.21 / 14.50
}

_MODE = os.environ.get("INCOGNITA_ACTPHYS", "").strip().lower()
if _MODE == "0":
    _MODE = ""
if _MODE not in MODES:
    raise ValueError(f"INCOGNITA_ACTPHYS={_MODE!r}: expected one of {MODES} (or 0)")


def mode() -> str:
    return _MODE


def scissors_k17(Z: int) -> bool:
    """Use the Kopecky-2017 scissors for this nucleus."""
    return _MODE in ("sc", "both") and Z >= ZMIN


def e1_factor(Z: int, A: int) -> float:
    """Default E1 ftable of nucleus (Z, A): 1 unless ``gg``/``both`` and RIPL-3 has its width."""
    if _MODE not in ("gg", "both") or Z < ZMIN:
        return 1.0
    f = GG_FACTOR.get((Z, A))
    if f is None:
        return 1.0
    return f[1] if _MODE == "both" else f[0]


def set_mode(m: str) -> str:
    """Switch in-process and drop every per-target cache. Returns the previous mode."""
    global _MODE
    m = "" if m in ("0", None) else str(m).lower()
    if m not in MODES:
        raise ValueError(f"actphys mode {m!r}: expected one of {MODES}")
    prev, _MODE = _MODE, m
    if prev != _MODE:
        from physics.hf.chartrun import drop_target_caches

        drop_target_caches(frozenset())
    return prev


__all__ = ["GG_FACTOR", "MODES", "ZMIN", "e1_factor", "mode", "scissors_k17", "set_mode"]
