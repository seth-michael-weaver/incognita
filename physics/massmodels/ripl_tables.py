"""Loaders for the RIPL-4 ``masses/mass-*.dat`` compilations (S. Goriely, 2024).

Every table shares the prefix ``Z, A, s, fl, Mexp, Err, Mth`` in Fortran format
``(2i4,1x,a2,1x,i1,4f10.3,...)``; ``Mth`` is the model's atomic mass excess in MeV
and is blank where the model has no entry. Column names after ``Mth`` differ per
model and are read from the ``#`` header line.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from physics.massmodels.paths import RIPL_MASSES

__all__ = ["RIPL_TABLES", "load_ripl_mass_table"]

# name -> (file, deformation column to expose as beta2, citation)
RIPL_TABLES: dict[str, tuple[str, str | None, str]] = {
    "frdm2012": (
        "mass-frdm12.dat",
        "beta2",
        "Moller, Sierk, Ichikawa, Sagawa, ADNDT 109-110 (2016) 1 (FRDM2012)",
    ),
    "hfb27": (
        "mass-hfb27.dat",
        "beta20",
        "Goriely, Chamel, Pearson, PRC 88 (2013) 061302 (HFB-27)",
    ),
    "ws4_ripl": (
        "mass-ws4.dat",
        "beta2",
        "Wang, Liu, Wu, Meng, PLB 734 (2014) 215 (WS4, RIPL copy)",
    ),
    "bskg3": (
        "mass-bskg3.dat",
        "beta20",
        "Grams, Ryssens, Scamps, Goriely, Chamel, EPJA 59 (2023) 270",
    ),
    "d1m": (
        "mass-d1m.dat",
        "beta20",
        "Goriely, Hilaire, Girod, Peru, PRL 102 (2009) 242501 (D1M)",
    ),
}

_PREFIX = ("Z", "A", "s", "fl", "Mexp", "Err", "Mth")


def _header_columns(path: Path) -> list[str]:
    with path.open() as fh:
        for line in fh:
            if line.startswith("#") and "Mth" in line:
                cols = line.lstrip("#").split()
                return cols
    raise ValueError(f"{path}: no '#  Z   A s fl ... Mth' header line")


def load_ripl_mass_table(name: str, ripl_masses: Path = RIPL_MASSES) -> pd.DataFrame:
    """Return ``Z, N, A, mass_excess_kev, beta2, <extra model columns>`` for one RIPL table.

    Rows without a theoretical mass (``Mth`` blank) are dropped, so the frame is the
    model's own domain of validity.
    """
    fname, beta_col, _ = RIPL_TABLES[name]
    path = ripl_masses / fname
    cols = _header_columns(path)
    if tuple(cols[:7]) != _PREFIX:
        raise ValueError(f"{path}: unexpected header {cols[:7]}")
    extra = cols[7:]
    # Fixed widths from (2i4,1x,a2,1x,i1,4f10.3,Nf8.3): everything after col 13 is
    # whitespace-separable because each f10.3/f8.3 field has at least one blank.
    z, a, mth, extras = [], [], [], []
    with path.open() as fh:
        for line in fh:
            if not line.strip() or line.startswith("#"):
                continue
            zi, ai = int(line[0:4]), int(line[4:8])
            body = line[13:].split()
            if len(body) < 3:  # no Mth
                continue
            z.append(zi)
            a.append(ai)
            mth.append(float(body[2]))
            vals = [float(x) for x in body[3 : 3 + len(extra)]]
            extras.append(vals + [np.nan] * (len(extra) - len(vals)))
    df = pd.DataFrame({"Z": np.array(z, dtype=np.int64), "A": np.array(a, dtype=np.int64)})
    df["N"] = df["A"] - df["Z"]
    df["mass_excess_kev"] = np.array(mth) * 1000.0
    ex = np.array(extras, dtype=np.float64)
    if ex.size:
        for j, c in enumerate(extra):
            if j < ex.shape[1]:
                df[c] = ex[:, j]
    if beta_col is not None and beta_col in df.columns:
        df["beta2"] = df[beta_col]
    first = ["Z", "N", "A", "mass_excess_kev"]
    return df[first + [c for c in df.columns if c not in first]]
