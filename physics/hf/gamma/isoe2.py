"""ISOE2: collective low-energy E2 strength of the quasi-continuum (stretched Delta J = 2 band transitions), added to the E2
photon strength as one Lorentzian in TALYS's E2 SLO form (the `epr/gpr/tpr` E2 slot, irad = 1, l = 2, i = 1), so every engine
path that evaluates fstrength (Py torch, numpy psf_fast, NATIVEX2 C) carries it; the GPU capture setup refuses it (Unsupported).

Keyword: env INCOGNITA_ISOE2 = e (default unset = OFF: this module is never consulted, OFF bit-identical); INCOGNITA_ISOE2_K = global
scale k (default 1.0 = arm E0, the B(E2) sum).

Rule (one for every nucleus; nothing fitted per nuclide):
  core values  E2 = E(2+_1) [MeV], Bd = B(E2; 2+_1 -> 0+) [e^2 fm^4] from data/isoe2/e2coll_v1.json (ENSDF adopted, Raman
               systematics where B(E2) is unmeasured). Even-even nucleus: itself; odd Z / odd N: the mean of its even-even cores
               ((Z, A-+1) for odd N, (Z-+1, A-+1) for odd Z, (Z-1, A-2) and (Z+1, A) for odd-odd), cores present in the table only.
               No core in the table -> no term.
  band energy  sigma = 0.83 A^0.26 (low-energy spin cutoff), Jbar = 1.25 sigma - 0.5 (mean spin of (2J+1) exp(-(J+1/2)^2/2sigma^2)),
               E0 = (4 Jbar - 2) E2 / 6 (stretched rotational E2, E(J) - E(J-2) = (4J-2) E2/6), Gamma = E0.
  strength     Bbar = (15/8) Bd (Alaga high-J limit B(E2; J -> J-2)/B(E2; 2 -> 0) = 5 <J 0 2 0|J-2 0>^2 -> 15/8),
               peak area int f dE = k C Bbar with C = 8 pi (L+1) / (L ((2L+1)!!)^2) e^2 / (hbar c)^5 (L = 2) [MeV^-4 per e^2 fm^4]
               (Gamma_E2 = C B Egamma^5, the Weisskopf/BM single-transition width); with the SLO near-peak area
               int f = kgr(2) tpr pi Gamma / (2 E0^3):  tpr = 2 E0^3 k C Bbar / (pi Gamma kgr(2)).
"""
from __future__ import annotations

import json
import math
import os
from functools import lru_cache
from pathlib import Path

E2SQ = 1.439964  # e^2, MeV fm
HBARC = 197.3269804  # MeV fm
C_E2 = 8.0 * math.pi * 3.0 / (2.0 * 225.0) * E2SQ / HBARC**5  # MeV^-4 per (e^2 fm^4)


def mode() -> str:
    return os.environ.get("INCOGNITA_ISOE2", "").strip().lower()


def scale() -> float:
    return float(os.environ.get("INCOGNITA_ISOE2_K", "1.0"))


@lru_cache(maxsize=1)
def _table() -> dict:
    p = Path(__file__).resolve().parents[3] / "data" / "isoe2" / "e2coll_v1.json"
    return {tuple(int(x) for x in k.split(",")): v for k, v in json.load(open(p)).items()}


def cores(Z: int, A: int) -> list[tuple[int, int]]:
    N = A - Z
    if Z % 2 == 0 and N % 2 == 0:
        return [(Z, A)]
    if Z % 2 == 0:
        return [(Z, A - 1), (Z, A + 1)]
    if N % 2 == 0:
        return [(Z - 1, A - 1), (Z + 1, A + 1)]
    return [(Z - 1, A - 2), (Z + 1, A)]


def core_values(Z: int, A: int):
    t = _table()
    cs = [t[c] for c in cores(Z, A) if c in t]
    if not cs:
        return None
    return sum(c[0] for c in cs) / len(cs), sum(c[1] for c in cs) / len(cs)


def lorentzian(Z: int, A: int, kgr2: float, k: float | None = None):
    """(tpr [mb], epr [MeV], gpr [MeV]) of the collective E2 term for nucleus (Z, A), or None (no core data / k <= 0)."""
    k = scale() if k is None else k
    cv = core_values(Z, A)
    if cv is None or k <= 0.0:
        return None
    e2, bd = cv
    sig = 0.83 * A**0.26
    jbar = 1.25 * sig - 0.5
    e0 = (4.0 * jbar - 2.0) * e2 / 6.0
    gam = e0
    area = k * C_E2 * (15.0 / 8.0) * bd
    tpr = 2.0 * e0**3 * area / (math.pi * gam * kgr2)
    return tpr, e0, gam
