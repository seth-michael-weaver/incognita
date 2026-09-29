"""PORTLEVER: the M1 scissors mode of deformed nuclei at Kopecky et al. (2017) strength, as an
engine default layered on the TALYS port's own.

TALYS's default M1 model (`strengthM1 3`, Goriely & Plujko's SMLO-2019) carries a scissors
Lorentzian at E = 5 A^-0.1 MeV, Gamma = 1.5 MeV, sigma = 0.01 |beta2| A^0.9 mb
(gammapar.f90:275-300). For U-239 (beta2 0.215) that integrates to B(M1)up ~ 1.8 mu_N^2. The Oslo
quasi-continuum measurements on the actinides (Guttormsen et al., PRL 109 162503 (2012);
PRC 89 014302 (2014)) put the scissors strength of 231-233Th, 232-233Pa and 237-239U at
roughly 6-11 mu_N^2. TALYS already ships a second systematics for the same resonance, Kopecky,
Goriely, Peru, Hilaire and Martini, PRC 95 054317 (2017), used by its `strengthM1 4`:
E = 80 |beta2| A^-1/3 MeV, Gamma = 1.5 MeV, sigma = 42.4 beta2^2 / Gamma mb. For U-239 that is
B(M1)up ~ 8.3 mu_N^2, inside the Oslo band.

`INCOGNITA_M1_SCISSORS=k17` swaps **only** that scissors term into the `strengthM1 3` model. The
spin-flip Lorentzian and the upbend keep SMLO-2019's values. The swap happens at the one place
every engine path reads a photon strength from, `gamma.parameters.gamma_parameters`: the Python
reference chain, the native `engine_c` chain (`psf_nx2`), the fast path (`psf_fast`) and the GPU
capture kernel (`capture_gpu_setup.gamma_pack`). It applies to every nucleus of the cascade and
is zero at beta2 = 0, so spherical nuclei do not move. A user `epr`/`gpr`/`spr` keyword still
wins, as it does for TALYS's own defaults (the `== 0.` tests of gammapar.f90).

It is **off by default** (`INCOGNITA_M1_SCISSORS` unset or `0`), so the port's fidelity harnesses
(CHART1, `talys_reference`, the A-* tests) keep measuring TALYS. The measured effect on the blind
capture regime is in `docs/results/portlever.md`.

SCISSORS2 adds `INCOGNITA_M1_SCISSORS=s2`: a deformation-scaled scissors on rotational nuclei only
(docs/results/scissors2-prereg.md). A nucleus is rotational when the measured E(4+)/E(2+) of its
even-even core is past the X(5) critical point, R4/2 >= 2.91 (Casten & Zamfir, PRL 87 052503
(2001)); every other nucleus keeps TALYS's term unchanged. On a rotational nucleus, with the
FRDM2012 static deformation delta = 0.946 |beta2| (RIPL-4 `mass-frdm12.dat`):
    E = 66 delta A^-1/3 MeV (Lo Iudice & Richter; Heyde, von Neumann-Cosel & Richter RMP 82 2365),
    B(M1)up = KAPPA A^4/3 delta^2 mu_N^2 (B ~ delta^2: Ziegler et al., PRL 65 2515 (1990)),
    Gamma = GAMMA_MEV,
KAPPA and GAMMA_MEV fitted to Oslo quasi-continuum gamma-strength data of 25 rotational nuclei
(no cross section enters; `scripts/scissors2/oslo_fit.py`, docs/results/scissors2/oslo_fit.json).
The structure inputs are `scissors2_table.csv` (`scripts/scissors2/build_table.py`).
"""

from __future__ import annotations

import csv
import os
from functools import cache
from pathlib import Path

import numpy as np

MODES = ("", "k17", "s2")
_MODE = os.environ.get("INCOGNITA_M1_SCISSORS", "").strip().lower()
if _MODE == "0":
    _MODE = ""
if _MODE not in MODES:
    raise ValueError(f"INCOGNITA_M1_SCISSORS={_MODE!r}: expected one of {MODES} (or 0)")


def mode() -> str:
    """The active scissors systematics: "" (TALYS's SMLO-2019), "k17" (Kopecky 2017) or "s2"
    (SCISSORS2, rotational nuclei only)."""
    return _MODE


def k17(A: int, beta2: float) -> tuple[float, float, float]:
    """(E [MeV], Gamma [MeV], sigma [mb]) of the scissors Lorentzian, Kopecky et al. 2017.

    TALYS: gammapar.f90:275-300 (the `strengthM1 == 4` scissors branch)
    Test: tests/hf/test_portlever_scissors.py
    """
    b2 = abs(float(beta2))
    gpr = 1.5
    return 80.0 * b2 / A ** (1.0 / 3.0), gpr, 42.4 * b2 * b2 / gpr


# SCISSORS2 constants (docs/results/scissors2/oslo_fit.json: medians over 25 Oslo nuclei)
KAPPA = 0.15219  # mu_N^2
GAMMA_MEV = 2.159
R42_ROTOR = 2.91  # X(5) critical point
_HBARC = 197.3269804  # MeV fm
_MUN2 = 1.43996448 * _HBARC**2 / (4 * 938.2720813**2)  # mu_N^2 in MeV fm^3
_K1 = 8.674e-8  # TALYS kgr(1), mb^-1 MeV^-2
_EG = np.linspace(1e-3, 20.0, 40001)


def slo_m1(e, omega: float, sigma_mb: float, gamma: float):
    """TALYS's standard-Lorentzian M1 strength [MeV^-3] (fstrength.f90:377-406)."""
    return _K1 * sigma_mb * e * gamma**2 / ((e**2 - omega**2) ** 2 + e**2 * gamma**2)


def b_m1(omega: float, sigma_mb: float, gamma: float) -> float:
    """B(M1)up [mu_N^2] of that Lorentzian, Oslo's definition 27 (hbar c)^3 / (16 pi) int f dE
    (Guttormsen et al., PRC 89 014302 (2014))."""
    f = slo_m1(_EG, omega, sigma_mb, gamma)
    return float(27 * _HBARC**3 / (16 * np.pi) * np.trapezoid(f, _EG) / _MUN2)


@cache
def _table() -> dict[tuple[int, int], tuple[float, float | None]]:
    out = {}
    with open(Path(__file__).with_name("scissors2_table.csv")) as fh:
        for r in csv.DictReader(fh):
            out[(int(r["Z"]), int(r["A"]))] = (
                float(r["beta2_frdm12"]), float(r["r42_core"]) if r["r42_core"] else None)
    return out


def is_rotor(Z: int, A: int) -> bool:
    b2, r42 = _table().get((int(Z), int(A)), (0.0, None))
    return r42 is not None and r42 >= R42_ROTOR and b2 != 0.0


@cache
def s2(Z: int, A: int) -> tuple[float, float, float] | None:
    """(E [MeV], Gamma [MeV], sigma [mb]) of the SCISSORS2 scissors of nucleus (Z, A), or None
    when (Z, A) is not rotational (TALYS's own term then stays).

    Test: tests/hf/test_scissors2.py
    """
    if not is_rotor(Z, A):
        return None
    b2 = _table()[(int(Z), int(A))][0]
    d = 0.946 * abs(b2)
    om = 66.0 * d / A ** (1.0 / 3.0)
    B = KAPPA * A ** (4.0 / 3.0) * d * d
    return om, GAMMA_MEV, B / b_m1(om, 1.0, GAMMA_MEV)


def set_mode(m: str) -> str:
    """Switch the systematics in-process and drop every per-target cache (the mode is in none of
    their keys). Returns the previous mode."""
    global _MODE
    m = "" if m in ("0", None) else str(m).lower()
    if m not in MODES:
        raise ValueError(f"scissors mode {m!r}: expected one of {MODES}")
    prev, _MODE = _MODE, m
    if prev != _MODE:
        from physics.hf.chartrun import drop_target_caches

        drop_target_caches(frozenset())
    return prev


__all__ = ["GAMMA_MEV", "KAPPA", "MODES", "b_m1", "is_rotor", "k17", "mode", "s2", "set_mode",
           "slo_m1"]
