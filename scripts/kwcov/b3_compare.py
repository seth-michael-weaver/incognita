#!/usr/bin/env python3
"""KWCOV B3 acceptance: discrete angular distributions of the engine (INCOGNITA_ANGOUT) vs a stock TALYS-2.25 run.

    python scripts/kwcov/b3_compare.py --z 26 --a 56 --stock ~/kwcov/stock/b3_fe56 [--proj p] [--levels 0,1,2]
                                       [--kw "cpang y"] [--rel 1e-3] [--onoff] [--write DIR] [--json out.json]

The stock directory holds TALYS's own files for the same target and energies (`energies` file, `outangle y`,
`outlegendre y`). For every (ejectile, level, energy) file both have: the largest |ours/stock - 1| of the total, direct
and compound columns over the angles where stock > --floor mb/sr (plan: 1 mb/sr), and of the xs/Rutherford column
(charged elastic). `--onoff` also runs the engine with the switch off and checks every Results array is the same.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def read_cols(path: Path) -> np.ndarray:
    rows = [ln.split() for ln in path.read_text().splitlines() if ln.strip() and not ln.lstrip().startswith("#")]
    return np.array([[float(x) for x in r] for r in rows]) if rows else np.zeros((0, 0))


def stock_files(d: Path, k0: str):
    """{(stem, kind, level, E): array} of the per-energy angle/Legendre files."""
    out = {}
    for f in d.iterdir():
        m = re.fullmatch(rf"({k0}[gnpdtha])(\d{{4}}\.\d{{3}})(ang|leg)\.L(\d\d)", f.name)
        if m:
            out[(m.group(1), m.group(3), int(m.group(4)), float(m.group(2)))] = read_cols(f)
    return out


def engine_run(Z: int, A: int, energies, on: bool):
    import torch

    from physics.hf import engine_c, warmrun
    from physics.hf.chartrun import drop_target_caches
    from physics.hf.engine import ChainedFull

    os.environ["INCOGNITA_ANGOUT"] = "1" if on else "0"
    drop_target_caches()
    with torch.inference_mode():
        r = engine_c.run(ChainedFull(Z=Z, A=A, declared_energies=tuple(energies)))
    return r, warmrun.result_arrays(r)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--z", type=int, required=True)
    ap.add_argument("--a", type=int, required=True)
    ap.add_argument("--stock", required=True)
    ap.add_argument("--proj", default="n")
    ap.add_argument("--levels", default="0,1,2")
    ap.add_argument("--floor", type=float, default=1.0)
    ap.add_argument("--rel", type=float, default=0.0, help="floor relative to the file's maximum instead of --floor")
    ap.add_argument("--onoff", action="store_true")
    ap.add_argument("--write", default="")
    ap.add_argument("--json", default="")
    ap.add_argument("--kw", default="", help="extra deck lines, ';'-joined (fitlib's lines arm), e.g. 'cpang y'")
    a = ap.parse_args()
    if a.kw:
        os.environ["INCOGNITA_TALYS_FIT"] = "lines"
        os.environ["INCOGNITA_TALYS_FIT_LINES"] = a.kw
    if a.proj != "n":
        os.environ["INCOGNITA_CPINC"] = a.proj
    d = Path(os.path.expanduser(a.stock))
    energies = [float(np.float32(float(x))) for x in (d / "energies").read_text().split()]
    if a.write:
        os.environ["INCOGNITA_ANGOUT_DIR"] = a.write
    res, arr_on = engine_run(a.z, a.a, energies, True)
    os.environ.pop("INCOGNITA_ANGOUT_DIR", None)
    ang = {k: v.numpy() for k, v in res.angular.items()}
    from physics.hf import angout

    report = {"approx": angout.META.get("approx", []), "rows": []}
    if a.onoff:
        _, arr_off = engine_run(a.z, a.a, energies, False)
        bad = [k for k in arr_off if k not in arr_on or not np.array_equal(arr_off[k], arr_on[k])]
        report["onoff"] = {"arrays": len(arr_off), "differ": bad + [k for k in arr_on if k not in arr_off]}
        print(f"on/off: {len(arr_off)} arrays, differing: {report['onoff']['differ']}")
    st = stock_files(d, a.proj)
    th = ang["angle"]
    levels = [int(x) for x in a.levels.split(",")]
    worst = 0.0
    for (stem, kind, n, e), s in sorted(st.items()):
        if kind != "ang" or n not in levels:
            continue
        i = int(np.argmin(np.abs(np.asarray(energies) - e)))
        name = f"{stem}ang.L{n:02d}"
        if name not in ang or abs(energies[i] - e) > 1e-3:
            print(f"{name} E={e:g}: missing in engine output")
            report["rows"].append({"name": name, "e": e, "missing": True})
            continue
        if s.shape[0] != th.size or np.abs(s[:, 0] - th).max() > 1e-4:
            print(f"{name} E={e:g}: angle grids differ")
            continue
        m = (s[:, 1] > (a.floor if a.rel <= 0 else a.rel * s[:, 1].max())) & (th > 0)
        row = {"name": name, "e": e, "n_ang": int(m.sum()), "stock_max": float(s[:, 1].max())}
        cols = {"xs": 1, "direct": 2, "compound": 3}
        for c, j in cols.items():
            ours = ang[name][i] if c == "xs" else ang[f"{name}:{c}"][i]
            mm = m & (s[:, j] > 1e-3 * s[:, 1].max()) if c != "xs" else m
            row[c] = float(np.abs(ours[mm] / s[mm, j] - 1).max()) if mm.any() else None
        if m.any():  # shape: the ratio's spread around its median (an overall factor = the parent channel's difference)
            rr = ang[name][i][m] / s[m, 1]
            row["shape"] = float(np.abs(rr / np.median(rr) - 1).max())
            row["scale"] = float(np.median(rr))
        lg = st.get((stem, "leg", n, e))
        if lg is not None and f"{stem}leg.L{n:02d}" in ang:
            ours = ang[f"{stem}leg.L{n:02d}"][i]
            k = min(lg.shape[0], ours.size)
            mk = np.abs(lg[:k, 1]) > 1e-3 * abs(lg[0, 1]) if lg[0, 1] else np.zeros(k, bool)
            row["leg_rows"] = [int(lg.shape[0]), int(ours.size)]
            row["leg"] = float(np.abs(ours[:k][mk] / lg[:k, 1][mk] - 1).max()) if mk.any() else None
            if mk.any():
                ra = ours[:k][mk] / lg[:k, 1][mk]
                row["leg_shape"] = float(np.abs(ra / ra[0] - 1).max())
        if s.shape[1] >= 6 and f"{name}:ruth" in ang:
            mm = th > 0
            row["ruth"] = float(np.abs(ang[f"{name}:ruth"][i][mm] / s[mm, 4] - 1).max())
            row["ruth_lt60"] = float(np.abs(ang[f"{name}:ruth"][i][mm & (th <= 60)] / s[mm & (th <= 60), 4] - 1).max())
        if row["xs"] is not None:
            worst = max(worst, row["xs"])
        report["rows"].append(row)
        print(f"{name:12s} E={e:6.2f} n={row['n_ang']:3d} stock_max={row['stock_max']:10.4g}  xs {row['xs']}  "
              f"dir {row['direct']}  comp {row['compound']}  shape {row.get('shape')}  leg {row.get('leg')} "
              f"leg_shape {row.get('leg_shape')} rows {row.get('leg_rows')}" + (f"  ruth {row['ruth']:.4f} (<=60deg {row['ruth_lt60']:.4f})"
                                                                 if "ruth" in row else ""))
    report["worst_xs"] = worst
    print(f"worst |ours/stock-1| (xs, stock > {a.floor} mb/sr): {worst:.4f}")
    if report["approx"]:
        print("approximations:", *report["approx"][:20], sep="\n  ")
    if a.json:
        Path(a.json).write_text(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
