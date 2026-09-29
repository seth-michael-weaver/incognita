"""BRUSLIB HFB mass tables (``raw/mass_models/bruslib/hfb{24,27,31}-dat``).

Whitespace-separated: ``Z A bet2 bet4 Rch Edef Sn Sp Qbet Mcal Mexp-Mcal Jexp Jth Pexp Pth``
with ``Mcal`` the calculated atomic mass excess in MeV; ``999.99`` marks a missing value.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from physics.massmodels.paths import BRUSLIB

__all__ = ["BRUSLIB_TABLES", "load_bruslib_table"]

BRUSLIB_TABLES: dict[str, tuple[str, str]] = {
    "hfb24": ("hfb24-dat", "Goriely, Chamel, Pearson, PRC 88 (2013) 024308 (HFB-24)"),
    "hfb27_bruslib": ("hfb27-dat", "Goriely, Chamel, Pearson, PRC 88 (2013) 061302 (HFB-27)"),
    "hfb31": ("hfb31-dat", "Goriely, Chamel, Pearson, PRC 93 (2016) 034337 (HFB-31)"),
}

_COLS = [
    "Z", "A", "bet2", "bet4", "Rch", "Edef", "Sn", "Sp", "Qbet", "Mcal", "Mexp_minus_Mcal",
    "Jexp", "Jth", "Pexp", "Pth",
]  # fmt: skip
_MISSING = 999.99


def load_bruslib_table(name: str, bruslib_dir: Path = BRUSLIB) -> pd.DataFrame:
    fname, _ = BRUSLIB_TABLES[name]
    path = bruslib_dir / fname
    rows = []
    with path.open() as fh:
        for line in fh:
            parts = line.split()
            if len(parts) != len(_COLS) or not parts[0].isdigit():
                continue
            rows.append([float(x) for x in parts])
    arr = np.array(rows, dtype=np.float64)
    df = pd.DataFrame(arr, columns=_COLS)
    df["Z"] = df["Z"].astype(np.int64)
    df["A"] = df["A"].astype(np.int64)
    df["N"] = df["A"] - df["Z"]
    df["mass_excess_kev"] = df["Mcal"] * 1000.0
    df["beta2"] = df["bet2"]
    for c in ("Sn", "Sp", "Qbet"):
        df.loc[np.isclose(df[c], _MISSING), c] = np.nan
    keep = ["Z", "N", "A", "mass_excess_kev", "beta2", "bet4", "Rch", "Edef", "Sn", "Sp", "Qbet"]
    return df[keep]
