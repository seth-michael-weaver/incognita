"""WS4 mass tables from the authors' site (``raw/mass_models/ws4/``).

``WS4.txt``: ``A Z Beta2 Beta4 Beta6 Esh Edef Eexp Eth Mexp Mth`` (energies in MeV);
``WS4_RBF.txt``: ``A Z WS4 WS4+RBF`` mass excesses in MeV.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from physics.massmodels.paths import WS4_DIR

__all__ = ["load_ws4", "load_ws4_rbf"]

WS4_CITATION = "Wang, Liu, Wu, Meng, PLB 734 (2014) 215 (WS4)"
WS4_RBF_CITATION = "Wang, Liu, Wu, Meng, PLB 734 (2014) 215 (WS4+RBF)"


def _numeric_rows(path: Path, ncol: int) -> np.ndarray:
    rows = []
    with path.open(encoding="latin-1") as fh:
        for line in fh:
            parts = line.replace(",", " ").split()
            if len(parts) != ncol or not parts[0].isdigit():
                continue
            try:
                rows.append([float(x) for x in parts])
            except ValueError:
                continue
    return np.array(rows, dtype=np.float64)


def load_ws4(ws4_dir: Path = WS4_DIR) -> pd.DataFrame:
    arr = _numeric_rows(ws4_dir / "WS4.txt", 11)
    cols = ["A", "Z", "Beta2", "Beta4", "Beta6", "Esh", "Edef", "Eexp", "Eth", "Mexp", "Mth"]
    df = pd.DataFrame(arr, columns=cols)
    df["Z"] = df["Z"].astype(np.int64)
    df["A"] = df["A"].astype(np.int64)
    df["N"] = df["A"] - df["Z"]
    df["mass_excess_kev"] = df["Mth"] * 1000.0
    df["beta2"] = df["Beta2"]
    return df[["Z", "N", "A", "mass_excess_kev", "beta2", "Beta4", "Beta6", "Esh", "Edef"]]


def load_ws4_rbf(ws4_dir: Path = WS4_DIR) -> pd.DataFrame:
    """WS4+RBF (radial-basis-function corrected) mass excesses; ``mass_excess_ws4_kev`` kept
    alongside for a self-consistency check against ``WS4.txt``."""
    arr = _numeric_rows(ws4_dir / "WS4_RBF.txt", 4)
    df = pd.DataFrame(arr, columns=["A", "Z", "ws4", "ws4_rbf"])
    df["Z"] = df["Z"].astype(np.int64)
    df["A"] = df["A"].astype(np.int64)
    df["N"] = df["A"] - df["Z"]
    df["mass_excess_kev"] = df["ws4_rbf"] * 1000.0
    df["mass_excess_ws4_kev"] = df["ws4"] * 1000.0
    return df[["Z", "N", "A", "mass_excess_kev", "mass_excess_ws4_kev"]]
