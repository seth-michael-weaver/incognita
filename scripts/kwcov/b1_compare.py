#!/usr/bin/env python3
"""KWCOV B1 acceptance: CHANOBS names of the engine vs the files of a stock TALYS-2.25 run.

    INCOGNITA_CHANOBS=1 python scripts/kwcov/b1_compare.py --z 27 --a 59 --stock ~/kwcov/stock/co59 [--json out.json]

The stock run directory holds TALYS's own files of the same target and energies (`energies` file, `channels y`,
`filechannels y`, `outdiscrete y`). Prints one line per name: engine, TALYS, ratio; and the C-path arrays with the
switch on vs off (they must be the same: the switch is output only).
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
PARSYM = "gnpdtha"


def read_cols(path: Path) -> np.ndarray:
    rows = [ln.split() for ln in path.read_text().splitlines() if ln.strip() and not ln.lstrip().startswith("#")]
    return np.array([[float(x) for x in r] for r in rows]) if rows else np.zeros((0, 0))


def stock_values(d: Path, k0: str = "n") -> dict[str, np.ndarray]:
    """{CHANOBS name: values on the stock energy grid}, plus 'E'."""
    out: dict[str, np.ndarray] = {}
    for p in PARSYM:
        f = d / f"{p}prod.tot"
        if f.is_file():
            a = read_cols(f)
            out["E"] = a[:, 0]
            out[f"{p}prod.tot"], out[f"{p}prod.tot:multiplicity"] = a[:, 1], a[:, 2]
        f = d / f"{k0}{p}.tot"
        if f.is_file() and p != k0:
            a = read_cols(f)
            out[f"{k0}{p}.tot:discrete"], out[f"{k0}{p}.tot:continuum"] = a[:, 2], a[:, 3]
    f = d / "binary.tot"
    if f.is_file():
        a = read_cols(f)
        for t, p in enumerate(PARSYM):
            out[f"binary.tot:{p}"] = a[:, 1 + t]
    for f in sorted(d.glob("xs[0-9]*.*")):
        stem, ext = f.name.split(".", 1)
        a = read_cols(f)
        if a.size == 0:
            continue
        if ext == "tot" and a.shape[1] >= 3:
            out[f"{stem}.tot:gamma"] = a[:, 2]
            out[f"{stem}.tot"] = a[:, 1]
        elif re.fullmatch(r"L\d\d", ext):
            out[f"{stem}.{ext}"], out[f"{stem}.{ext}:branch"] = a[:, 1], a[:, 2]
        elif ext == "fis":
            out[f"{stem}.fis"] = a[:, 1]
    return out


def engine_values(Z: int, A: int, energies, chanobs: bool):
    import torch

    from physics.hf import engine_c, warmrun
    from physics.hf.chartrun import drop_target_caches
    from physics.hf.engine import ChainedFull

    os.environ["INCOGNITA_CHANOBS"] = "1" if chanobs else "0"
    drop_target_caches()
    stats: dict = {}
    with torch.inference_mode():
        r = engine_c.run(ChainedFull(Z=Z, A=A, declared_energies=tuple(energies)), stats)
    arr = warmrun.result_arrays(r)
    ex = {k.split("/", 1)[1]: v for k, v in arr.items() if k.startswith("extras/")}
    ex.update({k.split("/", 1)[1] + ".tot": v for k, v in arr.items() if k.startswith("channels_mb/")})
    return arr, ex, stats


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--z", type=int, required=True)
    ap.add_argument("--a", type=int, required=True)
    ap.add_argument("--stock", required=True)
    ap.add_argument("--floor", type=float, default=1.0, help="mb: below this the TALYS value is not scored")
    ap.add_argument("--json")
    a = ap.parse_args()
    st = stock_values(Path(os.path.expanduser(a.stock)))
    E = st.pop("E")
    off, _, _ = engine_values(a.z, a.a, E, False)
    on, ex, stats = engine_values(a.z, a.a, E, True)
    same = [k for k in off if not k.startswith("extras/") and k in on and np.array_equal(off[k], on[k])]
    diff = [k for k in off if not k.startswith("extras/") and (k not in on or not np.array_equal(off[k], on[k]))]
    rmax = max((float(np.max(np.abs(on[k] - off[k]) / np.maximum(np.abs(off[k]), 1e-30))) for k in diff if k in on),
               default=0.0)
    print(f"switch on vs off: {len(same)} arrays identical, {len(diff)} differ (max rel {rmax:.2e}); stats {stats}")
    rows = []
    for k in sorted(st):
        t = st[k]
        e = ex.get(k)
        if e is None:
            if np.any(t > a.floor):
                rows.append((k, None, t))
            continue
        rows.append((k, e, t))
    out = []
    for k, e, t in rows:
        if e is None:
            print(f"{k:28s} MISSING in engine; TALYS {np.array2string(t, precision=4)}")
            out.append(dict(name=k, engine=None, talys=t.tolist()))
            continue
        is_ratio = k.endswith(":multiplicity") or k.endswith(":branch")
        m = (t > (1e-3 if is_ratio else a.floor)) & (e > 0)
        r = np.where(m, e / np.where(t != 0, t, 1), np.nan)
        print(f"{k:28s} eng {np.array2string(e, precision=4)} talys {np.array2string(t, precision=4)} "
              f"ratio {np.array2string(r, precision=3)}")
        out.append(dict(name=k, engine=e.tolist(), talys=t.tolist(), ratio=[None if np.isnan(x) else float(x) for x in r]))
    if a.json:
        Path(a.json).write_text(json.dumps(dict(z=a.z, a=a.a, energies=E.tolist(), on_off_identical=len(diff) == 0,
                                                on_off_maxrel=rmax, rows=out), indent=1))


if __name__ == "__main__":
    main()
