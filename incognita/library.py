"""Read the shipped libraries (library/v0.1/, library/v0.2/, library/v0.2.1/, library/v0.2.2/, library/v0.2.3/) without any other tooling.

    uv run python -m incognita.library summary            # nuclei per regime tier, energy grid
    uv run python -m incognita.library show Fe-56          # capture curve with 68 / 95 % intervals, MACS at 30 keV
    uv run python -m incognita.library show Fe-56 --version v0.2   # the same from library v0.2
    uv run python -m incognita.library show Fe-56 --version v0.2.1 # v0.2 with centre-of-mass MACS (library/v0.2.1/CHANGELOG.md)
    uv run python -m incognita.library show Fe-56 --version v0.2.2 # + the engine below 1 keV, reduced mass (library/v0.2.2/CHANGELOG.md)
    uv run python -m incognita.library show Fe-56 --version v0.2.3 # v0.2.2 values; errata of flags and factors (library/v0.2.3/CHANGELOG.md)
    uv run python -m incognita.library show Z026N030M0 --every 4

`--version` (or `version=` in Python) picks the library; the default stays v0.1.

The capture table holds one row per nuclide; `energy_ev`, `sigma_b`, `unc68_log10` and `unc95_log10` are arrays on a
common grid (1 keV to 20 MeV). An interval is multiplicative: sigma * 10**(+-unc68_log10) is the 68 % band.
v0.2.2 adds `energy_below1keV_ev` / `sigma_below1keV_b` (15 points, 2 eV - 0.66 keV, no band) and `below1keV_source`.
v0.2.3 has the same values as v0.2.2, with corrected ANCHORED factor text, model-form column and per-kT MACS flags.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import numpy as np
import pandas as pd

LIBRARY = Path(__file__).resolve().parents[1] / "library" / "v0.1"
CAPTURE = "capture_v01_indep.parquet"
VERSIONS = {"v0.1": CAPTURE, "v0.2": "capture_v02.parquet", "v0.2.1": "capture_v021.parquet",
            "v0.2.2": "capture_v022.parquet", "v0.2.3": "capture_v023.parquet"}  # library/<version>/<capture file>
TIERS = ("MEASURED", "ANCHORED", "INTERPOLATED", "EXTRAPOLATED")

_SYMBOLS = (
    "n H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn Ga Ge As Se Br Kr Rb Sr Y Zr "
    "Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf Ta W Re Os Ir Pt "
    "Au Hg Tl Pb Bi Po At Rn Fr Ra Ac Th Pa U Np Pu Am Cm Bk Cf Es Fm Md No Lr Rf Db Sg Bh Hs Mt Ds Rg Cn Nh Fl Mc Lv "
    "Ts Og"
).split()


def nuclide_id(name: str) -> str:
    """'Fe-56', 'fe56', '56Fe' or 'Z026N030M0' -> 'Z026N030M0' (ground state)."""
    s = name.strip()
    if re.fullmatch(r"Z\d{3}N\d{3}M\d", s):
        return s
    m = re.fullmatch(r"([A-Za-z]{1,2})-?(\d{1,3})", s) or None
    if m:
        sym, a = m.group(1), int(m.group(2))
    else:
        m = re.fullmatch(r"(\d{1,3})([A-Za-z]{1,2})", s)
        if not m:
            raise ValueError(f"cannot parse nuclide {name!r}; use e.g. Fe-56 or Z026N030M0")
        a, sym = int(m.group(1)), m.group(2)
    sym = sym.capitalize()
    if sym not in _SYMBOLS:
        raise ValueError(f"unknown element symbol {sym!r}")
    z = _SYMBOLS.index(sym)
    return f"Z{z:03d}N{a - z:03d}M0"


def load_capture(root: Path | str = LIBRARY, version: str | None = None) -> pd.DataFrame:
    """The capture table of library `version` ("v0.1", "v0.2", "v0.2.1", "v0.2.2" or "v0.2.3"); without a version, CAPTURE under `root`."""
    if version is None:
        return pd.read_parquet(Path(root) / CAPTURE)
    if version not in VERSIONS:
        raise ValueError(f"unknown library version {version!r}; use one of {sorted(VERSIONS)}")
    return pd.read_parquet(LIBRARY.parent / version / VERSIONS[version])


def capture_curve(nid: str, table: pd.DataFrame | None = None, version: str | None = None) -> pd.DataFrame:
    """One nuclide's capture curve as a flat table with its 68 / 95 % bands (barns)."""
    t = load_capture(version=version) if table is None else table
    rows = t[t.nuclide_id == nuclide_id(nid)]
    if rows.empty:
        raise KeyError(f"{nid} is not in the library")
    r = rows.iloc[0]
    e, s = np.asarray(r.energy_ev, float), np.asarray(r.sigma_b, float)
    u68, u95 = np.asarray(r.unc68_log10, float), np.asarray(r.unc95_log10, float)
    return pd.DataFrame({
        "energy_ev": e, "sigma_b": s,
        "lo68_b": s / 10 ** u68, "hi68_b": s * 10 ** u68,
        "lo95_b": s / 10 ** u95, "hi95_b": s * 10 ** u95,
    }).assign(tier=r.tier)


def summary(table: pd.DataFrame | None = None) -> str:
    t = load_capture() if table is None else table
    e = np.asarray(t.energy_ev.iloc[0], float)
    counts = t.tier.value_counts()
    lines = [f"nuclides: {len(t)} (Z {t.Z.min()}-{t.Z.max()})",
             f"capture grid: {len(e)} energies, {e.min():.4g} eV to {e.max():.4g} eV"]
    lines += [f"  {k:<13} {int(counts.get(k, 0))}" for k in TIERS]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m incognita.library", description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sm = sub.add_parser("summary")
    sh = sub.add_parser("show")
    sh.add_argument("nuclide")
    sh.add_argument("--every", type=int, default=1, help="print every n-th energy")
    for p in (sm, sh):
        p.add_argument("--version", choices=sorted(VERSIONS), default="v0.1", help="library version (default v0.1)")
    a = ap.parse_args(argv)
    t = load_capture(version=a.version)
    if a.cmd == "summary":
        print(summary(t))
        return 0
    cur = capture_curve(a.nuclide, t)
    r = t[t.nuclide_id == nuclide_id(a.nuclide)].iloc[0]
    print(f"{r.nuclide_id}  tier {r.tier}  MACS(30 keV) {r.macs30_mb:.4g} mb (68 % factor x{r.unc68_factor_30keV:.2f})"
          + (f"  flag: {r.macs30_flag}" if isinstance(r.macs30_flag, str) and r.macs30_flag else ""))
    if "sigma_below1keV_b" in t.columns:  # v0.2.2, v0.2.3: the curve below 1 keV (no band)
        el, sl = np.asarray(r.energy_below1keV_ev, float), np.asarray(r.sigma_below1keV_b, float)
        print(f"below 1 keV ({r.below1keV_source}): " + ", ".join(f"{x:.4g} eV {y:.4g} b" for x, y in list(zip(el, sl))[:: max(1, a.every)]))
    with pd.option_context("display.float_format", "{:.4g}".format, "display.width", 120):
        print(cur.drop(columns="tier").iloc[:: max(1, a.every)].to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
