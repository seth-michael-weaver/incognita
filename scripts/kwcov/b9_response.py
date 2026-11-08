#!/usr/bin/env python3
"""KWCOV B9 acceptance: astrophysical rates, MACS and partition functions (astro, astrogs, astroex, astroE, astroT,
nonthermlev) vs stock TALYS-2.25.

    PY=~/fastgate_data/eng/16606b356d6e/.venv/bin/python   # WSL; the engine venv has torch
    $PY scripts/kwcov/b9_response.py --target au197 --kw "astro y"                  # absolute: ours vs stock
    $PY scripts/kwcov/b9_response.py --target au197 --kw "astro y" --base "astro y;astrogs y"   # + response

Stock runs keep only the astro files (astrorate*, macs.g) as JSON in ~/kwcov/stock/b9_<target>_<hash>.json; engine
runs the same in ~/kwcov/eng/b9_<target>_<hash>.json (the engine's per-energy log of the thermalised target too).
TALYS scratch is deleted after every run. Metrics: per file and column, |ln(ours/stock)| over T9 (rows where stock
> `--floor` of its column maximum); the response R = ours(kw)/ours(base), S = stock(kw)/stock(base), |ln(R/S)|.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
STOCK = Path(os.path.expanduser("~/kwcov/stock"))
ENG = Path(os.path.expanduser("~/kwcov/eng"))
TALYS = os.path.expanduser("~/opt/talys-src/bin/talys")
LOCK = "/tmp/incognita_heavy.lock"
TARGETS = {"au197": ("au", 79, 197), "fe56": ("fe", 26, 56), "ge74": ("ge", 32, 74), "co59": ("co", 27, 59)}


def _deck(target: str, kw: str) -> str:
    el, _, a = TARGETS[target]
    lines = ["projectile n", f"element {el}", f"mass {a}", "energy 1."] + [x.strip() for x in kw.split(";") if x.strip()]
    return "\n".join(lines) + "\n"


def _tag(target: str, kw: str, side: str) -> Path:
    h = hashlib.sha1(_deck(target, kw).encode()).hexdigest()[:10]
    return (STOCK if side == "stock" else ENG) / f"b9_{target}_{h}.json"


def _astro_files(d: Path) -> dict:
    from physics.hf.astro.rates import read_stock

    out = {}
    for p in sorted(d.iterdir()):
        if p.name.startswith("astrorate") or p.name == "macs.g":
            if p.name == "macs.g":
                w = p.read_text().splitlines()[1].split()
                out[p.name] = {"Z": [float(w[0])], "A": [float(w[1])], "MACS(mb)": [float(w[2])],
                               "Exp(mb)": [float(w[3])], "dEXP(mb)": [float(w[4])], "MACS/Exp": [float(w[5])]}
            else:
                out[p.name] = {k: [float(x) for x in v] for k, v in read_stock(p).items()}
    return out


def stock(target: str, kw: str) -> dict:
    f = _tag(target, kw, "stock")
    if f.is_file():
        return json.loads(f.read_text())
    STOCK.mkdir(parents=True, exist_ok=True)
    d = Path(tempfile.mkdtemp(prefix=f"b9tmp_{target}_", dir=str(STOCK)))
    try:
        (d / "talys.inp").write_text(_deck(target, kw))
        with open(d / "talys.inp") as fi, open(d / "talys.out", "w") as fo:
            subprocess.run(["flock", LOCK, "nice", "-n", "10", TALYS], stdin=fi, stdout=fo, cwd=d, check=True)
        res = {"deck": _deck(target, kw), "files": _astro_files(d)}
    finally:
        shutil.rmtree(d, ignore_errors=True)
    f.write_text(json.dumps(res))
    return res


def ours(target: str, kw: str) -> dict:
    f = _tag(target, kw, "eng")
    if f.is_file():
        return json.loads(f.read_text())
    from physics.hf.input.deck import run_deck

    ENG.mkdir(parents=True, exist_ok=True)
    d = Path(tempfile.mkdtemp(prefix=f"b9eng_{target}_"))
    try:
        (d / "talys.inp").write_text(_deck(target, kw))
        import fcntl

        with open(LOCK, "a") as lk:  # one heavy process at a time (shared with the stock runs)
            fcntl.flock(lk, fcntl.LOCK_EX)
            r = run_deck(d / "talys.inp")
        files = {k: {c: [float(x) for x in v] for c, v in cols.items()} for k, cols in r.astro.items()
                 if not k.startswith("_")}
        meta = r.astro.get("_meta", {})
        res = {"deck": _deck(target, kw), "files": files, "thermal": meta.get("thermal", []),
               "e_inc_mev": [float(x) for x in r.e_inc_mev], "xs000000": [float(x) for x in r.channels_mb["xs000000"]]}
    finally:
        shutil.rmtree(d, ignore_errors=True)
    f.write_text(json.dumps(res))
    return res


def compare(a: dict, b: dict, floor: float = 1e-6, tmin: float = 0.0, tmax: float = 10.0) -> list[tuple]:
    """[(file, column, worst |ln(a/b)|, T9 at worst, a, b)] over the files and columns both have."""
    rows = []
    for f, cb in b["files"].items():
        ca = a["files"].get(f)
        if ca is None:
            rows.append((f, "(missing)", math.inf, 0, 0, 0))
            continue
        t = cb.get("T", [0.0] * len(next(iter(cb.values()))))
        for c, vb in cb.items():
            if c in ("T", "E-average", "Z", "A", "Exp(mb)", "dEXP(mb)") or c not in ca:
                continue
            va = ca[c]
            top = max(abs(x) for x in vb) if vb else 0.0
            worst = (0.0, 0.0, 0.0, 0.0)
            for i, (x, y) in enumerate(zip(va, vb)):
                if not (tmin <= t[i] <= tmax) or y <= floor * top or y <= 0:
                    continue
                d = abs(math.log(x / y)) if x > 0 else math.inf
                if d > worst[0]:
                    worst = (d, t[i], x, y)
            rows.append((f, c, *worst))
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default="au197")
    ap.add_argument("--kw", default="astro y")
    ap.add_argument("--base", default=None)
    ap.add_argument("--floor", type=float, default=1e-6)
    ap.add_argument("--tmin", type=float, default=0.0)
    ap.add_argument("--tmax", type=float, default=10.0)
    ap.add_argument("--files", default="astrorate.g,astrorate.p,astrorate.a,astrorate.tot,macs.g")
    a = ap.parse_args()
    keep = set(a.files.split(","))
    s, o = stock(a.target, a.kw), ours(a.target, a.kw)
    print(f"# {a.target} [{a.kw}] ours vs stock (|ln| %, T9 in [{a.tmin}, {a.tmax}])")
    for f, c, d, t, x, y in compare(o, s, a.floor, a.tmin, a.tmax):
        if f in keep or f.split(".L")[0] in keep:
            print(f"  {f:22s} {c:16s} {100 * d:8.2f} %  T9={t:<8.4g} ours={x:.5e} stock={y:.5e}")
    if a.base:
        sb, ob = stock(a.target, a.base), ours(a.target, a.base)
        print(f"# response [{a.kw}] / [{a.base}]: |ln(R/S)| %")
        for f in sorted(keep):
            if f not in s["files"] or f not in sb["files"] or f not in o["files"] or f not in ob["files"]:
                continue
            for c in s["files"][f]:
                if c in ("T", "E-average", "Z", "A", "Exp(mb)", "dEXP(mb)", "MACS/Exp"):
                    continue
                vs, vsb = s["files"][f][c], sb["files"][f].get(c)
                vo, vob = o["files"][f].get(c), ob["files"][f].get(c)
                if vsb is None or vo is None or vob is None:
                    continue
                t = s["files"][f].get("T", [0] * len(vs))
                top = max(vs) if vs else 0
                worst = (0.0, 0, 0, 0)
                for i in range(len(vs)):
                    if not (a.tmin <= t[i] <= a.tmax) or vs[i] <= a.floor * top or vsb[i] <= 0 or vob[i] <= 0 or vo[i] <= 0:
                        continue
                    R, S = vo[i] / vob[i], vs[i] / vsb[i]
                    d = abs(math.log(R / S))
                    if d > worst[0]:
                        worst = (d, t[i], R, S)
                print(f"  {f:22s} {c:16s} {100 * worst[0]:8.2f} %  T9={worst[1]:<8.4g} R={worst[2]:.5f} S={worst[3]:.5f}")


if __name__ == "__main__":
    main()
