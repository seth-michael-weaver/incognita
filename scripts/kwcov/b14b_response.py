#!/usr/bin/env python3
"""KWCOV B14 part 2 acceptance: GEF (`massdis y`, fymodel 2 = TALYS's default) yields and prompt neutrons vs stock.

    PY=~/fastgate_data/eng/16606b356d6e/.venv/bin/python   # WSL; the engine venv has torch
    $PY scripts/kwcov/b14b_response.py --target u235 [--kw "gefran 1000"] [--stream talys|lanes] [--seed k] [--mode talys]
    $PY scripts/kwcov/b14b_response.py --all                 # the table of COVERAGE_PLAN.md B14 part 2

Every deck is `massdis y` plus `--kw` lines (';'-separated) at the target's energies (U-235: 1, 5 MeV; U-238: 1, 5,
14 MeV). Stock runs keep only yieldA / yieldZA / nubarn.tot / Pnun / nunA files in ~/kwcov/stock/b14b/<target>_<hash>/
(scratch deleted); engine runs (engine_c.run, `--mode talys` = fidelity.py's TALYS_DECK / TALYS_ENV, as part 1) keep
the same tables in ~/kwcov/eng/b14b_<target>_<hash>_<mode>_<stream><seed>.npz.
Two kinds of comparison:
  exact      `--stream talys` (INCOGNITA_GEF_STREAM=talys: the stock generator stream, event by event) with a small
             gefran: the sampled numbers are stock's when the excitation bins and their fission cross sections agree.
  statistical `--stream lanes` (the engine's default) with several `--seed`s: ours vs stock against the sampling noise
             (spread of our seeds); acceptance |ln(ours/stock)| <= 2 % at the mass-yield peaks.
Metrics, |ln(ours/stock)| in %, worst over the energies (as b14_response.py): ffpk / fppk (bins >= 50 % of the max),
ff / fp (>= 1 %), za (isotopic FF >= 1 %), xs (FF cross section), nubar, pnu (P(nu) rows >= 1 % of max), nua (nu(A)
where the FF yield >= 1 % of its max).
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

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts" / "kwcov"))
from b14_response import TALYS_DECK, TALYS_ENV, _ln, read  # noqa: E402

STOCK = Path(os.path.expanduser("~/kwcov/stock/b14b"))
ENG = Path(os.path.expanduser("~/kwcov/eng"))
TALYS = os.path.expanduser("~/opt/talys-src/bin/talys")
LOCK = "/tmp/incognita_heavy.lock"
TARGETS = {"u235": ("u", 235, 92, (1.0, 5.0)), "u238": ("u", 238, 92, (1.0, 5.0, 14.0))}
BASE = "massdis y"
KEEP = ("yieldA", "yieldZA", "nubarn.tot", "Pnun", "nunA")


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
    tmp = Path(tempfile.mkdtemp(prefix="b14btmp_", dir=str(STOCK)))
    try:
        (tmp / "talys.inp").write_text(_deck(target, kw))
        (tmp / "energies").write_text("".join(f"{e:g}\n" for e in TARGETS[target][3]))
        with open(tmp / "talys.inp") as fi, open(tmp / "talys.full", "w") as fo:
            subprocess.run(["flock", LOCK, "nice", "-n", "10", TALYS], stdin=fi, stdout=fo, cwd=tmp, check=True)
        d.mkdir(parents=True, exist_ok=True)
        for f in tmp.iterdir():
            if f.name.startswith(KEEP) or f.name in ("talys.inp", "energies"):
                shutil.copy(f, d / f.name)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return d


def ours(target: str, kw: str, mode: str = "talys", stream: str = "lanes", seed: int = 0) -> dict:
    f = ENG / f"b14b_{_tag(target, kw)}_{mode}_{stream}{seed}.npz"
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
    env = dict(TALYS_ENV) if mode == "talys" else {}
    env.update(INCOGNITA_GEF_STREAM=stream, INCOGNITA_GEF_SEED=str(seed), INCOGNITA_TALYS_FIT="lines",
               INCOGNITA_TALYS_FIT_LINES=";".join(lines))
    old = {k: os.environ.get(k) for k in env}
    try:
        os.environ.update(env)
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
        if name.startswith(KEEP):
            for c, v in cols.items():
                out[f"{name}/{c}"] = np.asarray(v)
    ENG.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(f, **out)
    return out


def _estr(e: float) -> str:
    from physics.hf.fisyield import estring

    return estring(e)


def compare(target: str, kw: str, mode: str = "talys", stream: str = "lanes", seed: int = 0) -> dict:
    d = stock(target, kw)
    us = ours(target, kw, mode, stream, seed)
    worst: dict = {}

    def note(fam, v, where):
        if v > worst.get(fam, (-1.0, ""))[0]:
            worst[fam] = (v, where)

    nb, _ = read(d / "nubarn.tot") if (d / "nubarn.tot").is_file() else (np.zeros((0, 2)), [])
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
            note("xs", _ln(float(us[f"{key}/Tot"][3]), tot[3]), f"E={e:g}")
        z, _ = read(d / f"yieldZA{es}.fis")
        kz = f"yieldZA{es}.fis"
        if z.size and f"{kz}/Z" in us:
            oz = {(int(a_), int(b_)): v for a_, b_, v in zip(us[f"{kz}/Z"], us[f"{kz}/A"], us[f"{kz}/FF_yield"])}
            mx = z[:, 4].max()
            for row in z:
                if row[4] >= 1e-2 * mx:
                    note("za", _ln(oz.get((int(row[0]), int(row[1])), 0.0), row[4]), f"E={e:g} Z={int(row[0])} A={int(row[1])}")
        if nb.size:
            sv = nb[np.isclose(nb[:, 0], e), 1]
            ov = us["nubarn.tot/nubar"][np.isclose(us["nubarn.tot/E"], e)] if "nubarn.tot/E" in us else []
            if len(sv):
                note("nubar", _ln(float(ov[0]) if len(ov) else 0.0, float(sv[0])), f"E={e:g}")
        pf = d / f"Pnun{es}.fis"
        if pf.is_file() and f"Pnun{es}.fis/nu" in us:
            p, _ = read(pf)
            op = dict(zip(us[f"Pnun{es}.fis/number"].astype(int), us[f"Pnun{es}.fis/nu"]))
            mx = p[:, 1].max()
            for row in p:
                if row[1] >= 1e-2 * mx:
                    note("pnu", _ln(op.get(int(row[0]), 0.0), row[1]), f"E={e:g} nu={int(row[0])}")
        nf = d / f"nunA{es}.fis"
        if nf.is_file() and f"nunA{es}.fis/nu" in us:
            n, _ = read(nf)
            on = us[f"nunA{es}.fis/nu"]
            ffm = a[:, 2].max()
            for i in range(n.shape[0]):
                if a[i, 2] >= 1e-2 * ffm and n[i, 1] > 0:
                    note("nua", _ln(on[i], n[i, 1]), f"E={e:g} A={int(n[i, 0])}")
    return worst


def stat(target: str, kw: str, seeds: int, mode: str = "talys", stock_kw: str | None = None) -> dict:
    """Ours (lanes, `seeds` substreams) vs stock: per quantity the mean over seeds, the seed spread s, and z = (mean -
    stock) / sqrt(s^2 (1 + 1/n)) (stock carries one draw of the same sampling noise). Returns the worst |ln| of each
    seed and the worst z at the peaks. `stock_kw` compares with a stock deck of its own (e.g. "gefran 1000000": stock's
    sampling noise 4.5x smaller)."""
    d = stock(target, kw if stock_kw is None else stock_kw)
    runs = [ours(target, kw, mode, "lanes", k) for k in range(seeds)]
    res: dict = {}
    for e in TARGETS[target][3]:
        es = _estr(e)
        a, _ = read(d / f"yieldA{es}.fis")
        for fam, col, j in (("ffpk", "FF_yield", 2), ("fppk", "FP_yield", 1)):
            mx = a[:, j].max()
            sel = a[:, j] >= 0.5 * mx
            ys = np.array([r[f"yieldA{es}.fis/{col}"][sel] for r in runs])
            m, s = ys.mean(0), ys.std(0, ddof=1) if seeds > 1 else np.zeros(sel.sum())
            st = a[sel, j]
            lnm = np.abs(np.log(m / st)) * 100
            rel_s = s / m * 100
            z = (m - st) / np.maximum(s * math.sqrt(1 + 1 / seeds), 1e-30)
            k = int(np.argmax(lnm))
            # Poisson chi2 over every A with stock >= 1 % of the max: var(y) = y / N on each side
            ns = _gefran(stock_kw if stock_kw is not None else kw)
            no = _gefran(kw) * seeds
            allm = np.array([r[f"yieldA{es}.fis/{col}"] for r in runs]).mean(0)
            w = a[:, j] >= 1e-2 * mx
            c2 = (allm[w] - a[w, j]) ** 2 / (a[w, j] / ns + np.maximum(allm[w], 1e-12) / no)
            res[f"{fam} E={e:g}"] = {"worst_ln_mean_%": round(float(lnm[k]), 3), "A": int(a[sel, 0][k]),
                                     "seed_sd_%": round(float(rel_s[k]), 3), "max|z|": round(float(np.abs(z).max()), 2),
                                     "worst_ln_single_seed_%": round(float(np.abs(np.log(ys / st)).max() * 100), 3),
                                     "chi2/dof (A >= 1 % of max, Poisson)": round(float(c2.mean()), 2),
                                     "expected sd at the peak %": round(100 * math.sqrt(1 / (st[k] * ns) + 1 / (m[k] * no)), 2)}
        nb, _ = read(d / "nubarn.tot")
        sv = float(nb[np.isclose(nb[:, 0], e), 1][0])
        ov = np.array([float(r["nubarn.tot/nubar"][np.isclose(r["nubarn.tot/E"], e)][0]) for r in runs])
        res[f"nubar E={e:g}"] = {"stock": sv, "ours_mean": round(float(ov.mean()), 5),
                                 "seed_sd": round(float(ov.std(ddof=1)) if seeds > 1 else 0.0, 5),
                                 "ln_%": round(abs(math.log(ov.mean() / sv)) * 100, 3)}
    return res


def _gefran(kw: str) -> int:
    for ln in _lines(kw):
        t = ln.split()
        if t[0].lower() == "gefran":
            return int(t[1])
    return 50000


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default="u235")
    ap.add_argument("--kw", default="")
    ap.add_argument("--mode", default="talys")
    ap.add_argument("--stream", default="lanes")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--stat", type=int, default=0, help="statistical comparison over this many lane seeds")
    ap.add_argument("--stock-only", action="store_true")
    ap.add_argument("--stock-kw", default=None, help="--stat: stock deck lines of their own (e.g. 'gefran 1000000')")
    a = ap.parse_args()
    if a.stock_only:
        print(stock(a.target, a.kw))
        return
    if a.stat:
        print(json.dumps(stat(a.target, a.kw, a.stat, a.mode, a.stock_kw), indent=1))
        return
    w = compare(a.target, a.kw, a.mode, a.stream, a.seed)
    print(json.dumps({k: (round(v[0], 4), v[1]) for k, v in sorted(w.items())}, indent=1))


if __name__ == "__main__":
    main()
