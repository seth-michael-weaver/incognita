"""Nuclide-level physics features for the chart encoder (BLUEPRINT §5.2).

Every function is pure numpy over integer arrays Z, N so it works for one
nuclide or the whole chart. `feature_table(Z, N)` returns a dict of named
columns; `FEATURE_NAMES` fixes the column order used by models.
"""

from __future__ import annotations

import numpy as np

MAGIC = np.array([2, 8, 20, 28, 50, 82, 126, 184], dtype=np.int64)
# Shell boundaries used for valence counts: the magic numbers, with 184 as
# the predicted next neutron closure (§5.2).

# Liquid-drop (Weizsäcker) coefficients in MeV; Wang et al. 2014-style set.
LDM = {"a_v": 15.56, "a_s": 17.23, "a_c": 0.697, "a_a": 23.285, "a_p": 12.0}


def _nearest_magic_distance(x: np.ndarray) -> np.ndarray:
    return np.min(np.abs(x[:, None] - MAGIC[None, :]), axis=1)


def _valence(x: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (particles above lower closure, holes to upper closure, min of the two)."""
    idx = np.searchsorted(MAGIC, x, side="right")  # index of first magic > x
    lower = np.where(idx > 0, MAGIC[np.clip(idx - 1, 0, len(MAGIC) - 1)], 0)
    upper = MAGIC[np.clip(idx, 0, len(MAGIC) - 1)]
    upper = np.where(idx >= len(MAGIC), x + 1, upper)  # beyond 184: no closure
    particles = x - lower
    holes = upper - x
    return particles, holes, np.minimum(particles, holes)


def casten_p(Np: np.ndarray, Nn: np.ndarray) -> np.ndarray:
    """Casten's P factor Np*Nn/(Np+Nn); 0 where both vanish."""
    denom = Np + Nn
    with np.errstate(divide="ignore", invalid="ignore"):
        p = np.where(denom > 0, Np * Nn / np.where(denom > 0, denom, 1), 0.0)
    return p.astype(np.float64)


def liquid_drop_binding(Z: np.ndarray, N: np.ndarray) -> dict[str, np.ndarray]:
    """Semi-empirical mass formula terms (MeV) and their sum."""
    Z = Z.astype(np.float64)
    N = N.astype(np.float64)
    A = Z + N
    vol = LDM["a_v"] * A
    surf = -LDM["a_s"] * A ** (2 / 3)
    coul = -LDM["a_c"] * Z * (Z - 1) / np.cbrt(A)
    asym = -LDM["a_a"] * (N - Z) ** 2 / A
    even_z = (Z % 2 == 0)
    even_n = (N % 2 == 0)
    delta = np.where(even_z & even_n, 1.0, np.where(~even_z & ~even_n, -1.0, 0.0))
    pair = LDM["a_p"] * delta / np.sqrt(A)
    return {
        "ld_volume": vol,
        "ld_surface": surf,
        "ld_coulomb": coul,
        "ld_asymmetry": asym,
        "ld_pairing": pair,
        "ld_binding": vol + surf + coul + asym + pair,
    }


def feature_table(Z, N) -> dict[str, np.ndarray]:
    Z = np.atleast_1d(np.asarray(Z, dtype=np.int64))
    N = np.atleast_1d(np.asarray(N, dtype=np.int64))
    A = Z + N
    zp, zh, zv = _valence(Z)
    np_, nh, nv = _valence(N)
    feats: dict[str, np.ndarray] = {
        "Z": Z,
        "N": N,
        "A": A,
        "Z_even": (Z % 2 == 0).astype(np.int64),
        "N_even": (N % 2 == 0).astype(np.int64),
        "isospin": (N - Z).astype(np.float64),
        "isospin_frac": ((N - Z) / A).astype(np.float64),
        "dZ_magic": _nearest_magic_distance(Z),
        "dN_magic": _nearest_magic_distance(N),
        "Z_is_magic": np.isin(Z, MAGIC).astype(np.int64),
        "N_is_magic": np.isin(N, MAGIC).astype(np.int64),
        "Z_particles": zp,
        "Z_holes": zh,
        "Z_valence": zv,
        "N_particles": np_,
        "N_holes": nh,
        "N_valence": nv,
        "casten_P": casten_p(zv.astype(float), nv.astype(float)),
        "A_cbrt": np.cbrt(A.astype(np.float64)),
    }
    feats.update(liquid_drop_binding(Z, N))
    return feats


FEATURE_NAMES: list[str] = list(feature_table(np.array([82]), np.array([126])).keys())


def feature_matrix(Z, N) -> np.ndarray:
    """(n, len(FEATURE_NAMES)) float64 matrix in FEATURE_NAMES order."""
    t = feature_table(Z, N)
    return np.stack([t[k].astype(np.float64) for k in FEATURE_NAMES], axis=1)
