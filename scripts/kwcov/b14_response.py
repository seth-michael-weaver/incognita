#!/usr/bin/env python3
"""KWCOV B14 part 1 acceptance: fission yields with `massdis y` + `fymodel 1` (Brosa) vs stock TALYS-2.25.

    PY=~/fastgate_data/eng/16606b356d6e/.venv/bin/python   # WSL; the engine venv has torch
    $PY scripts/kwcov/b14_response.py --target u235 --kw "ffevaporation n" [--base ""] [--mode talys]
    $PY scripts/kwcov/b14_response.py --all                 # the table of COVERAGE_PLAN.md B14

Every deck is the target's base deck (massdis y, fymodel 1) plus `--kw` lines (';'-separated), at the target's energies
(U-235: 1 and 5 MeV; U-238: 1, 5, 14 MeV). Stock runs keep only yieldA*.fis / yieldZA*.fis in
~/kwcov/stock/b14/<target>_<hash>/ (scratch deleted); engine runs (engine_c.run on the deck lines; `--mode talys` adds
fidelity.py's TALYS_DECK / TALYS_ENV, every deliberate INCOGNITA default at its TALYS value: EXACTFIS and NPWINDOW change
the default fission, so the fragment yields are compared there) keep Results.fission_yields' yieldA / yieldZA tables in
~/kwcov/eng/b14_<target>_<hash>_<mode>.npz.
Metrics, |ln(ours/stock)| in %, worst over the energies:
  ffpk / fppk   FF (pre-neutron) / FP (post-neutron) mass yield, bins where stock >= 50 % of its maximum (the peaks)
  ff / fp       the same, bins where stock >= 1 % of its maximum
  za            isotopic FF yield of yieldZA, rows where stock >= 1 % of its maximum
  xs            total FF cross section (the `Tot` line, = the fission cross section the yields carry)
  resp          |ln(R/S)|, R = ours(kw)/ours(base), S = stock(kw)/stock(base), FF and FP mass yields where stock >= 10 % of
                the maximum (an output that is zero in both counts as matched)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
STOCK = Path(os.path.expanduser("~/kwcov/stock/b14"))
ENG = Path(os.path.expanduser("~/kwcov/eng"))
TALYS = os.path.expanduser("~/opt/talys-src/bin/talys")
LOCK = "/tmp/incognita_heavy.lock"
TARGETS = {"u235": ("u", 235, 92, (1.0, 5.0)), "u238": ("u", 238, 92, (1.0, 5.0, 14.0))}
BASE = "massdis y;fymodel 1"
#: fidelity.py (branch fidelity1): every deliberate INCOGNITA default at its TALYS value
TALYS_DECK = ["fluxclose n", "npwindow n", "chancap n", "nnleak n", "exactfis n", "alphatemp 0", "sfexit n",
              "kevleak2 n", "heavymacs2 n", "ftglobal n", "ccexitnbnf n", "tfold n", "ctwcont n", "alphaentr 0"]
TALYS_ENV = {"INCOGNITA_GRIDTOP": "n", "INCOGNITA_SPECCLOSE": "0", "INCOGNITA_LOWEPOT": "0",
             "INCOGNITA_TARMASSFIX": "0", "INCOGNITA_ISOROTPASS": "0"}
#: the --all table: (target, kw, base kw for the response or None)
TABLE = [
    ("u235", "", None),
    ("u238", "", None),
    ("u235", "ffevaporation n", ""),
    ("u235", "rfiseps 1e-3", ""),
    ("u238", "rfiseps 0.12", ""),
    ("u235", "outfy y;gefran 1000", ""),
]


def _lines(kw: str) -> list[str]:
    return [x.strip() for x in kw.split(";") if x.strip()]


def _deck(target: str, kw: str) -> str:
    el, a, _, _ = TARGETS[target]
    return "\n".join(["projectile n", f"element {el}", f"mass {a}", "energy energies"] + _lines(BASE + ";" + kw)) + "\n"


def _tag(target: str, kw: str) -> str:
    return f"{target}_{hashlib.sha1(_deck(target, kw).encode()).hexdigest()[:10]}"


def stock(target: str, kw: str) -> Path:
    d = STOCK / _tag(target, kw)
    if (d / "talys.inp").is_file():
        return d
    STOCK.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="b14tmp_", dir=str(STOCK)))
    try:
        (tmp / "talys.inp").write_text(_deck(target, kw))
        (tmp / "energies").write_text("".join(f"{e:g}\n" for e in TARGETS[target][3]))
        with open(tmp / "talys.inp") as fi, open(tmp / "talys.full", "w") as fo:
            subprocess.run(["flock", LOCK, "nice", "-n", "10", TALYS], stdin=fi, stdout=fo, cwd=tmp, check=True)
        d.mkdir(parents=True, exist_ok=True)
        for f in tmp.iterdir():
            if f.name.startswith(("yieldA", "yieldZA")) or f.name in ("talys.inp", "energies"):
                shutil.copy(f, d / f.name)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return d


def ours(target: str, kw: str, mode: str = "talys") -> dict:
    f = ENG / f"b14_{_tag(target, kw)}_{mode}.npz"
    if f.is_file():
        z = np.load(f)
        return {k: z[k] for k in z.files}
    import torch

    from physics.hf import engine_c
    from physics.hf.chartrun import drop_target_caches
    from physics.hf.engine import ChainedFull
    from physics.hf.input import fitlib

    _, A, Z, energies = TARGETS[target]
    lines = _lines(BASE + ";" + kw) + (TALYS_DECK if mode == "talys" else [])
    old = {k: os.environ.get(k) for k in list(TALYS_ENV) + ["INCOGNITA_TALYS_FIT", "INCOGNITA_TALYS_FIT_LINES"]}
    try:
        if mode == "talys":
            os.environ.update(TALYS_ENV)
        os.environ["INCOGNITA_TALYS_FIT"] = "lines"
        os.environ["INCOGNITA_TALYS_FIT_LINES"] = ";".join(lines)
        drop_target_caches()
        import fcntl

        with open(LOCK, "a") as lk:
            fcntl.flock(lk, fcntl.LOCK_EX)
            with torch.inference_mode():
                r = engine_c.run(ChainedFull(Z=Z, A=A, declared_energies=energies))
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        fitlib.deactivate()
        drop_target_caches()
    out = {}
    for name, cols in r.fission_yields.items():
        if name.startswith(("yieldA", "yieldZA")):
            for c, v in cols.items():
                out[f"{name}/{c}"] = np.asarray(v)
    out["fission"] = np.asarray(r.totals_mb["fission"].numpy()) if "fission" in r.totals_mb else np.zeros(0)
    ENG.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(f, **out)
    return out


def read(p: Path) -> tuple[np.ndarray, list]:
    rows, tot = [], []
    for ln in p.read_text().splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#Tot"):
            tot = [float(x) for x in s.split()[1:]]
        elif not s.startswith("#"):
            rows.append([float(x) for x in s.split()])
    return np.array(rows), tot


def _estr(e: float) -> str:
    from physics.hf.fisyield import estring

    return estring(e)


def _ln(a, b):
    return abs(math.log(a / b)) * 100.0 if a > 0 and b > 0 else (0.0 if a == b else float("inf"))


def compare(target: str, kw: str, mode: str = "talys") -> dict:
    d = stock(target, kw)
    us = ours(target, kw, mode)
    worst: dict = {}

    def note(fam, v, where):
        if v > worst.get(fam, (-1.0, ""))[0]:
            worst[fam] = (v, where)

    for e in TARGETS[target][3]:
        es = _estr(e)
        a, tot = read(d / f"yieldA{es}.fis")
        key = f"yieldA{es}.fis"
        if f"{key}/A" not in us:
            note("missing", float("inf"), key)
            continue
        for fam, col, j in (("ff", "FF_yield", 2), ("fp", "FP_yield", 1)):
            y = us[f"{key}/{col}"]
            mx = a[:, j].max()
            for i in range(a.shape[0]):
                if a[i, j] >= 1e-2 * mx and mx > 0:
                    note(fam, _ln(y[i], a[i, j]), f"E={e:g} A={int(a[i, 0])}")
                if a[i, j] >= 0.5 * mx and mx > 0:
                    note(fam + "pk", _ln(y[i], a[i, j]), f"E={e:g} A={int(a[i, 0])}")
        if tot:
            note("xs", _ln(float(us[f"{key}/Tot"][3]), tot[3]), f"E={e:g} FF_xs {us[f'{key}/Tot'][3]:.1f} vs {tot[3]:.1f}")
        z, _ = read(d / f"yieldZA{es}.fis")
        kz = f"yieldZA{es}.fis"
        if z.size and f"{kz}/Z" in us:
            ours_za = {(int(a_), int(b_)): v for a_, b_, v in zip(us[f"{kz}/Z"], us[f"{kz}/A"], us[f"{kz}/FF_yield"])}
            mx = z[:, 4].max()
            for row in z:
                if row[4] >= 1e-2 * mx:
                    note("za", _ln(ours_za.get((int(row[0]), int(row[1])), 0.0), row[4]),
                         f"E={e:g} Z={int(row[0])} A={int(row[1])}")
    return worst


def response(target: str, kw: str, base: str, mode: str = "talys") -> tuple[float, str, float]:
    dk, db = stock(target, kw), stock(target, base)
    uk, ub = ours(target, kw, mode), ours(target, base, mode)
    w, where, moved = 0.0, "", 0.0
    for e in TARGETS[target][3]:
        es = _estr(e)
        ak, _ = read(dk / f"yieldA{es}.fis")
        ab, _ = read(db / f"yieldA{es}.fis")
        key = f"yieldA{es}.fis"
        for col, j in (("FF_yield", 2), ("FP_yield", 1)):
            mx = max(ab[:, j].max(), ak[:, j].max())
            for i in range(ak.shape[0]):
                sk, sb, yk, yb = ak[i, j], ab[i, j], uk[f"{key}/{col}"][i], ub[f"{key}/{col}"][i]
                if max(sk, sb) < 0.1 * mx or mx <= 0:
                    continue
                if sk == 0 and yk == 0:  # both switched the output off
                    continue
                if min(sk, sb, yk, yb) <= 0:
                    v = float("inf")
                else:
                    v = abs(math.log((yk / yb) / (sk / sb))) * 100
                    moved = max(moved, abs(math.log(sk / sb)) * 100)
                if v > w:
                    w, where = v, f"{col} E={e:g} A={int(ak[i, 0])}"
    return w, where, moved


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default="u235")
    ap.add_argument("--kw", default="")
    ap.add_argument("--base", default=None)
    ap.add_argument("--mode", default="talys", choices=("talys", "default"))
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--json", default=None)
    a = ap.parse_args()
    rows = TABLE if a.all else [(a.target, a.kw, a.base)]
    res = []
    for target, kw, base in rows:
        w = compare(target, kw, a.mode)
        r = response(target, kw, base, a.mode) if base is not None else None
        res.append(dict(target=target, kw=kw, mode=a.mode, worst={k: list(v) for k, v in w.items()},
                        resp=list(r) if r else None))
        txt = "  ".join(f"{k} {v[0]:.3f}% ({v[1]})" for k, v in sorted(w.items()))
        rt = f"  resp {r[0]:.3f}% ({r[1]}; stock moved {r[2]:.1f}%)" if r else ""
        print(f"{target} [{kw or 'base'}] {a.mode}: {txt}{rt}", flush=True)
    if a.json:
        Path(a.json).write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
