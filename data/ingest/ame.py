"""AME2020 fixed-width parsers: ``mass_1.mas20`` (masses) and ``rct1`` / ``rct2_1`` (reaction
and separation energies). Blueprint §4.2.

Conventions
-----------
* Energies in keV, uncertainties in keV (1 sigma), exactly as AME quotes them.
* ``#`` in place of the decimal point marks an AME extrapolation ("estimated from trends of
  the mass surface"); it is kept as ``<quantity>_extrapolated`` so those rows can be held out
  of training (§4.2). ``*`` means "not calculable" and becomes NaN.
* Column positions come from the Fortran formats printed in the file headers and are
  asserted against 208Pb and 56Fe at parse time, because AME columns shift between releases.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd

__all__ = [
    "AME_DIR",
    "ME_H_KEV",
    "ME_N_KEV",
    "derived_separation_energies",
    "load_ame",
    "parse_mass_table",
    "parse_rct_table",
]

REPO = Path(__file__).resolve().parents[2]
AME_DIR = REPO / "raw" / "ame2020"
MASS_FILE = AME_DIR / "mass_1.mas20.txt"
RCT1_FILE = AME_DIR / "rct1.mas20.txt"
RCT2_FILE = AME_DIR / "rct2_1.mas20.txt"

# AME2020 mass excesses of 1H and the neutron (keV): used to derive separation energies.
ME_H_KEV = 7288.971064
ME_N_KEV = 8071.31806

# mass_1.mas20 Fortran format:
#   a1,i3,i5,i5,i5,1x,a3,a4,1x,f14.6,f12.6,f13.5,1x,f10.5,1x,a2,f13.5,f11.5,1x,i3,1x,f13.6,f12.6
_MASS_SLICES = {
    "NZ": (1, 4),
    "N": (4, 9),
    "Z": (9, 14),
    "A": (14, 19),
    "symbol": (20, 23),
    "origin": (23, 27),
    "mass_excess": (28, 42),
    "mass_excess_unc": (42, 54),
    "binding_per_a": (54, 67),
    "binding_per_a_unc": (68, 78),
    "beta_kind": (79, 81),
    "q_beta_minus": (81, 94),
    "q_beta_minus_unc": (94, 105),
    "atomic_mass_int": (106, 109),
    "atomic_mass_frac": (110, 123),
    "atomic_mass_unc": (123, 135),
}

# rct1 / rct2:  a1,i3,1x,a3,i3,1x,6(f12.4,f10.4)
_RCT_A = (1, 4)
_RCT_EL = (5, 8)
_RCT_Z = (8, 11)
_RCT_FIRST = 12
_RCT_VALUE_W = 12
_RCT_UNC_W = 10

RCT1_QUANTITIES = ("s2n", "s2p", "q_alpha", "q_2beta_minus", "q_ep", "q_beta_minus_n")
RCT2_QUANTITIES = ("sn", "sp", "q_4beta_minus", "q_d_alpha", "q_p_alpha", "q_n_alpha")

# Known rows used to assert column positions (AME2020 values).
_CHECKS = {
    (82, 208): {"mass_excess": (-21748.519, 1.148), "binding_per_a": (7867.4530, 0.0055)},
    (26, 56): {"mass_excess": (-60607.163, 0.268), "binding_per_a": (8790.3563, 0.0048)},
}
_RCT_CHECKS = {
    "sn": {(82, 208): 7367.8686, (92, 235): 5297.4952},
    "s2n": {(92, 235): 12142.9649},
}


def _num(field: str) -> tuple[float, bool]:
    """Parse one AME numeric field -> (value, extrapolated). ``*``/blank -> NaN."""
    s = field.strip()
    if not s or s == "*":
        return math.nan, False
    if "#" in s:
        return float(s.replace("#", ".")), True
    return float(s), False


def _is_mass_row(line: str) -> bool:
    try:
        int(line[4:9]), int(line[9:14]), int(line[14:19])
    except ValueError:
        return False
    return line[20:23].strip().isalpha()


def parse_mass_table(path: Path = MASS_FILE) -> pd.DataFrame:
    """Parse ``mass_1.mas20`` into one row per (Z, A) ground state."""
    rows = []
    with path.open() as fh:
        for line in fh:
            line = line.rstrip("\n")
            if len(line) < 110 or not _is_mass_row(line):
                continue
            s = _MASS_SLICES
            rec: dict[str, object] = {
                "N": int(line[slice(*s["N"])]),
                "Z": int(line[slice(*s["Z"])]),
                "A": int(line[slice(*s["A"])]),
                "symbol": line[slice(*s["symbol"])].strip(),
                "origin": line[slice(*s["origin"])].strip() or None,
            }
            for q in ("mass_excess", "binding_per_a", "q_beta_minus"):
                v, ex = _num(line[slice(*s[q])])
                u, _ = _num(line[slice(*s[q + "_unc"])])
                rec[f"{q}_kev"] = v
                rec[f"{q}_unc_kev"] = u
                rec[f"{q}_extrapolated"] = ex
            ai = line[slice(*s["atomic_mass_int"])].strip()
            af, aex = _num(line[slice(*s["atomic_mass_frac"])])
            au, _ = _num(line[slice(*s["atomic_mass_unc"])])
            rec["atomic_mass_u"] = (int(ai) + af * 1e-6) if ai and not math.isnan(af) else math.nan
            rec["atomic_mass_unc_u"] = au * 1e-6
            rec["atomic_mass_extrapolated"] = aex
            rows.append(rec)
    df = pd.DataFrame(rows)
    if df.empty:
        raise ValueError(f"{path}: no data rows recognised")
    if df["A"].ne(df["Z"] + df["N"]).any():
        raise ValueError(f"{path}: A != Z + N on some rows; column positions are wrong")
    if df.duplicated(["Z", "N"]).any():
        raise ValueError(f"{path}: duplicate (Z, N) rows")
    _assert_mass_columns(df, path)
    return df.sort_values(["Z", "N"]).reset_index(drop=True)


def _assert_mass_columns(df: pd.DataFrame, path: Path) -> None:
    idx = df.set_index(["Z", "A"])
    for key, checks in _CHECKS.items():
        if key not in idx.index:
            raise ValueError(f"{path}: reference nuclide Z={key[0]} A={key[1]} missing")
        row = idx.loc[key]
        for q, (val, unc) in checks.items():
            got, got_u = row[f"{q}_kev"], row[f"{q}_unc_kev"]
            if abs(got - val) > 0.01 or abs(got_u - unc) > 0.01:
                raise ValueError(
                    f"{path}: {q} for Z={key[0]} A={key[1]} parsed as {got} +/- {got_u}, "
                    f"expected {val} +/- {unc}; AME column positions have shifted"
                )


def _is_rct_row(line: str) -> bool:
    try:
        int(line[slice(*_RCT_A)]), int(line[slice(*_RCT_Z)])
    except ValueError:
        return False
    return line[slice(*_RCT_EL)].strip().isalpha()


def parse_rct_table(path: Path, quantities: tuple[str, ...]) -> pd.DataFrame:
    """Parse one of the two reaction-energy files into ``Z, A, N`` + six quantities."""
    if len(quantities) != 6:
        raise ValueError("rct files carry exactly six quantities")
    rows = []
    with path.open() as fh:
        for line in fh:
            line = line.rstrip("\n")
            if len(line) < _RCT_FIRST + 22 or not _is_rct_row(line):
                continue
            line = line.ljust(_RCT_FIRST + 6 * (_RCT_VALUE_W + _RCT_UNC_W))
            rec: dict[str, object] = {
                "A": int(line[slice(*_RCT_A)]),
                "Z": int(line[slice(*_RCT_Z)]),
                "symbol": line[slice(*_RCT_EL)].strip(),
            }
            pos = _RCT_FIRST
            for q in quantities:
                v, ex = _num(line[pos : pos + _RCT_VALUE_W])
                pos += _RCT_VALUE_W
                u, _ = _num(line[pos : pos + _RCT_UNC_W])
                pos += _RCT_UNC_W
                rec[f"{q}_kev"] = v
                rec[f"{q}_unc_kev"] = u
                rec[f"{q}_extrapolated"] = ex
            rows.append(rec)
    df = pd.DataFrame(rows)
    if df.empty:
        raise ValueError(f"{path}: no data rows recognised")
    df["N"] = df["A"] - df["Z"]
    if df.duplicated(["Z", "N"]).any():
        raise ValueError(f"{path}: duplicate (Z, N) rows")
    idx = df.set_index(["Z", "A"])
    for q, checks in _RCT_CHECKS.items():
        if f"{q}_kev" not in df.columns:
            continue
        for key, val in checks.items():
            got = idx.loc[key, f"{q}_kev"]
            if abs(got - val) > 0.01:
                raise ValueError(
                    f"{path}: {q} for Z={key[0]} A={key[1]} parsed as {got}, expected {val}"
                )
    return df.drop(columns=["symbol"]).sort_values(["Z", "N"]).reset_index(drop=True)


def load_ame(ame_dir: Path = AME_DIR) -> pd.DataFrame:
    """Masses joined with both reaction-energy files on (Z, N). One row per ground state."""
    mass = parse_mass_table(ame_dir / MASS_FILE.name)
    rct1 = parse_rct_table(ame_dir / RCT1_FILE.name, RCT1_QUANTITIES)
    rct2 = parse_rct_table(ame_dir / RCT2_FILE.name, RCT2_QUANTITIES)
    df = mass.merge(rct1.drop(columns=["A"]), on=["Z", "N"], how="left").merge(
        rct2.drop(columns=["A"]), on=["Z", "N"], how="left"
    )
    for c in df.columns:
        if c.endswith("_extrapolated"):
            df[c] = df[c].fillna(False).astype(bool)
    df.attrs["source_version"] = "AME2020"
    return df


def derived_separation_energies(df: pd.DataFrame) -> pd.DataFrame:
    """S_n, S_p, S_2n, S_2p (keV) recomputed from the mass-excess column by neighbour lookup.

    Used to check the parser: they must agree with AME's own rct columns to rounding.
    """
    me = {(z, n): m for z, n, m in zip(df["Z"], df["N"], df["mass_excess_kev"], strict=True)}

    def get(z: int, n: int) -> float:
        return me.get((z, n), math.nan)

    out = pd.DataFrame({"Z": df["Z"], "N": df["N"]})
    Z = df["Z"].to_numpy()
    N = df["N"].to_numpy()
    M = df["mass_excess_kev"].to_numpy()
    out["sn_calc_kev"] = [get(z, n - 1) + ME_N_KEV - m for z, n, m in zip(Z, N, M, strict=True)]
    out["sp_calc_kev"] = [get(z - 1, n) + ME_H_KEV - m for z, n, m in zip(Z, N, M, strict=True)]
    out["s2n_calc_kev"] = [
        get(z, n - 2) + 2 * ME_N_KEV - m for z, n, m in zip(Z, N, M, strict=True)
    ]
    out["s2p_calc_kev"] = [
        get(z - 2, n) + 2 * ME_H_KEV - m for z, n, m in zip(Z, N, M, strict=True)
    ]
    return out.replace([np.inf, -np.inf], np.nan)
