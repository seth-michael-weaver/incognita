"""SLINPUT (Incognita extension, default OFF; env INCOGNITA_SFUNC = u1 | u01): measured neutron strength functions S0 / S1
as the low-energy neutron transmission input, one uniform rule for every nucleus.

For a neutron channel on a nucleus (Z, A) with a measured S_l in the table (`INCOGNITA_SFUNC_TABLE`, csv Z,A,S0,S1 in
units of 1e-4; empty = not measured):

    T_lj(E) -> min(1, T_lj(E) * [S_l,meas / S_l,model]^w(E)),   l = 0 (u01 only) and l = 1 (u1 and u01),

    w(E) = 1 for E_lab <= 0.1 MeV, -log10(E_lab / MeV) for 0.1 < E_lab < 1 MeV (linear in log10 E), 0 above.

S_l,model is the channel's OWN strength function at E_lab = 1 keV (spr.f90 form: S0 = T0 / (2 pi sqrt(E[eV])),
S1 = T1 (1 + (kR)^2) / (kR)^2 / (2 pi sqrt(E[eV])), R = 1.35 A^(1/3)), so after the rule each channel reproduces the
measured S_l at 1 keV:
- incident channel (spherical or coupled-channels Tjlinc, `emission.feeding.Cascade.incident`): S_model from the
  incident channel solved at 1 keV; sigma_reac / sigma_tot move by the change of the compound-formation part.
- inverse (emission-grid) neutron channel (`compound.dens_reference._transmission`, ONE set per cascade = the
  target's, flagompall n): S_model log-interpolated from the grid's own T_l at 1 keV; the inverse sigma_reac
  (pre-equilibrium emission) scales with sum (2l+1) T_l.
Every Py/C/fast/GPU path reads T_lj through those two functions, so they agree by construction. lmax and the
shape-elastic cross section are left as solved. Nuclei without a measured S_l, l >= 2, charged particles and
E_lab >= 1 MeV are untouched (bitwise).
"""

from __future__ import annotations

import csv
import math
import os
from functools import lru_cache

import numpy as np

E_REF_MEV = 1.0e-3
E_FULL_MEV = 0.1
E_ZERO_MEV = 1.0
LAST: dict = {}  # diagnostics: {(Z, A, "inc"|"inv"): {"model": {l: S}, "meas": {l: S}}}


def mode() -> str | None:
    m = os.environ.get("INCOGNITA_SFUNC", "").strip().lower()
    return m if m in ("u1", "u01") else None


def scope() -> str:
    """SLFIRST (env INCOGNITA_SFUNC_SCOPE, default `all` = SLINPUT U1 bitwise): with `first` the inverse-channel
    factor acts only on neutron exits of the FIRST compound nucleus (residual = the measured target, the
    channel the measured S_l describes by reciprocity); every later compound nucleus emits neutrons through
    the unmodified model T_l (`Cascade.trans_of`). The incident channel is unchanged."""
    s = os.environ.get("INCOGNITA_SFUNC_SCOPE", "all").strip().lower() or "all"
    if s not in ("all", "first"):
        raise ValueError(f"INCOGNITA_SFUNC_SCOPE={s!r}: use all | first")
    return s


def _ls(m: str) -> tuple[int, ...]:
    return (0, 1) if m == "u01" else (1,)


@lru_cache(maxsize=4)
def _table(path: str) -> dict:
    out = {}
    with open(path) as f:
        for r in csv.DictReader(f):
            v = {}
            for l, key in ((0, "S0"), (1, "S1")):
                s = (r.get(key) or "").strip()
                if s and float(s) > 0:
                    v[l] = float(s) * 1.0e-4
            if v:
                out[(int(r["Z"]), int(r["A"]))] = v
    return out


def measured(Z: int, A: int) -> dict:
    """{l: S_l,meas (absolute)} for the active mode's l values; {} when the rule is off or nothing is measured."""
    m = mode()
    if m is None:
        return {}
    path = os.environ.get("INCOGNITA_SFUNC_TABLE", "")
    if not path:
        raise RuntimeError("INCOGNITA_SFUNC set without INCOGNITA_SFUNC_TABLE")
    v = _table(path).get((int(Z), int(A)), {})
    return {l: s for l, s in v.items() if l in _ls(m)}


def weight(e_lab_mev) -> np.ndarray:
    e = np.asarray(e_lab_mev, dtype=float)
    w = np.where(e <= E_FULL_MEV, 1.0, -np.log10(np.clip(e, 1e-300, None)))
    return np.where(e >= E_ZERO_MEV, 0.0, np.clip(w, 0.0, 1.0))


def penetrability_ratio(A: int, wavenum_fm) -> np.ndarray:
    """v_1 = (kR)^2 / (1 + (kR)^2) with spr.f90's R = 1.35 A^(1/3)."""
    x = (1.35 * float(A) ** (1.0 / 3.0)) ** 2 * np.asarray(wavenum_fm, dtype=float) ** 2
    return x / (1.0 + x)


def strength(t_l: np.ndarray, e_lab_mev, A: int, wavenum_fm, l: int) -> np.ndarray:
    efac = 1.0 / (np.sqrt(1.0e6 * np.asarray(e_lab_mev, dtype=float)) * 2.0 * math.pi)
    s = np.asarray(t_l, dtype=float) * efac
    return s if l == 0 else s / penetrability_ratio(A, wavenum_fm)


def factors(meas: dict, model: dict, e_lab_mev) -> dict:
    """{l: F_l(E)} = (S_meas / S_model)^w(E) on the energies given."""
    w = weight(e_lab_mev)
    out = {}
    for l, s in meas.items():
        sm = model.get(l)
        if sm is None or not (sm > 0) or not math.isfinite(sm):
            continue
        out[l] = np.power(s / sm, w)
    return out


def interp_ref(e_lab_mev: np.ndarray, s_model: np.ndarray) -> float:
    """log-log interpolation of a model strength function at E_REF on a grid (flat outside the valid points)."""
    e = np.asarray(e_lab_mev, dtype=float)
    s = np.asarray(s_model, dtype=float)
    ok = np.isfinite(s) & (s > 0) & (e > 0)
    if not ok.any():
        return float("nan")
    e, s = e[ok], s[ok]
    o = np.argsort(e)
    return float(np.exp(np.interp(math.log(E_REF_MEV), np.log(e[o]), np.log(s[o]))))
