"""FTGLOBAL (card FTPROMO): the E1/M1 `ftable` of every nucleus is the ONE global form
f(Z, A) = 10^(W clip(k3 + k4 |beta2|, -1, 1)) (CTREFIT k3, k4; W = B18 out-of-range shrink weight of the B13 features),
tabulated in ftglobal_table.csv (development notes, 6 decimals as the deck lines were written).

It replaces every nonzero E1/M1 (l = 1) `ftable` override of a nucleus in the table: the per-nucleus <Gamma_gamma> anchors
(JS / ISOROTPASS / ACTJS), the PATTERN delta and the stale-base residual lines stop reaching the prediction. Other cells,
`ftableadjust`, the TMC factor and every nucleus outside the table are untouched. Default ON (`ftglobal y`); `ftglobal n`
or INCOGNITA_FTGLOBAL=0 = the previous behaviour (deck lines verbatim). Tensors that require grad are never rewritten (fits).

HEAVYMACS2 (rebuild of HEAVYMACS rule R1, default ON since the HEAVYMACS2 gate commit; `heavymacs2 n` / INCOGNITA_HEAVYMACS2=0 = previous production): `heavymacs2 y` or INCOGNITA_HEAVYMACS2=1 sets the global value to 1 (no rotor
dipole boost) for every nucleus with 60 <= Z <= 83 and |beta2| >= 0.2 (same beta2 table as f_glob; heavymacs2_domain.csv). Only acts where
FTGLOBAL acts (nonzero l=1 override, nucleus tabulated, ftglobal on)."""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import numpy as np

_TABLE = Path(__file__).with_name("ftglobal_table.csv")
_HM2 = Path(__file__).with_name("heavymacs2_domain.csv")


@lru_cache(maxsize=1)
def table() -> dict:
    out = {}
    with open(_TABLE) as f:
        next(f)
        for line in f:
            z, a, v = line.split(",")
            out[(int(z), int(a))] = float(v)
    return out


@lru_cache(maxsize=1)
def hm2_domain() -> frozenset:
    with open(_HM2) as f:
        next(f)
        return frozenset((int(z), int(a)) for z, a, _ in (line.split(",") for line in f))


def hm2_enabled(options) -> bool:
    env = os.environ.get("INCOGNITA_HEAVYMACS2", "").strip().lower()
    if env:
        return env not in ("0", "n", "no", "off", "false")
    return str(getattr(options, "heavymacs2", "y")).strip().lower() in ("y", "yes", "1", "true")


def enabled(options) -> bool:
    env = os.environ.get("INCOGNITA_FTGLOBAL", "").strip().lower()
    if env:
        return env not in ("0", "n", "no", "off", "false")
    return str(getattr(options, "ftglobal", "y")).strip().lower() in ("y", "yes", "1", "true")


def apply(options, Z: int, A: int, ov: dict) -> dict:
    """`ov` (gamma_parameters overrides) with the E1/M1 l=1 ftable cells set to f_glob(Z, A); `ov` itself when nothing applies."""
    v = ov.get("ftable")
    if v is None or not enabled(options):
        return ov
    g = table().get((int(Z), int(A)))
    if g is None:
        return ov
    if (int(Z), int(A)) in hm2_domain() and hm2_enabled(options):
        g = 1.0  # HEAVYMACS2 R1
    if getattr(v, "requires_grad", False):
        return ov
    a = np.array(v.detach().cpu().numpy() if hasattr(v, "detach") else v, dtype=float)
    if a.ndim != 2 or a.shape[1] < 2:
        return ov
    for irad in (0, 1):
        if a[irad, 1] != 0.0:
            a[irad, 1] = g
    out = dict(ov)
    out["ftable"] = a
    return out
