#!/usr/bin/env python3
"""KWCOV B14 part 3 acceptance: fission fragment evaporation (`massdis y; fymodel 4`, ffevap.f90) vs stock TALYS-2.25.

    PY=~/fastgate_data/eng/16606b356d6e/.venv/bin/python   # WSL; the engine venv has torch
    $PY scripts/kwcov/b14c_response.py --target u235 [--kw "..."] [--mode talys|default]

Every deck is `massdis y; fymodel 4` plus `--kw` lines (';'-separated) at the target's energies. A stock run takes
~12 min per energy (one full TALYS run per fragment, ~410 for U-236*); it keeps only the yield / nubar / P(nu) / nu(A)
/ nu(Z,A) / Eav files, the isomer files of two nuclides, three ff*.ex population files and frag_summary.json (talys.out's
reaction summary per fragment: initial population, multiplicities, residual production with isomers) in
~/kwcov/stock/b14c/<target>_<hash>/ (scratch deleted). Engine runs (engine_c.run; `--mode talys` = fidelity.py's
TALYS_DECK / TALYS_ENV, as parts 1-2) keep the same tables in ~/kwcov/eng/b14c_<target>_<hash>_<mode>.npz.
Metrics, |ln(ours/stock)| in % (worst):
  ff / fp            FF (pre) / FP (post-neutron) mass yield, A with stock >= 1 % of the max; ffpk / fppk >= 50 %
  za / zapost        isotopic FF / FP yield, rows >= 1 % of the max
  iso                isomeric ratio (yieldZA isomer rows), nuclides with FP yield >= 1 % of the max
  nubar_<x>          nubar per ejectile (n, g; p and alpha are 1e-6 and reported apart)
  nuA                nu_n(A), A with FF yield >= 1 % of the max
  frag_n / frag_g    per-fragment neutron / gamma multiplicity (talys.out), fragments with initial population
                     >= 1e-3 of the largest (neutron: multiplicity >= 0.05)
"""
from __future__ import annotations

import argparse
import hashlib
import json
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

STOCK = Path(os.path.expanduser("~/kwcov/stock/b14c"))
ENG = Path(os.path.expanduser("~/kwcov/eng"))
TALYS = os.path.expanduser("~/opt/talys-src/bin/talys")
LOCK = "/tmp/incognita_heavy.lock"
TARGETS = {"u235": ("u", 235, 92, (1.0,)), "u238": ("u", 238, 92, (5.0,))}
BASE = "massdis y;fymodel 4"
KEEP = ("yieldA", "yieldZA", "nubar", "Pnu", "nunA", "nugA", "nunZA", "nugZA", "EavA", "EavZA", "ff_fragments")
TRIM = ("yieldA", "yieldZA", "nubar", "Pnu", "nunA", "nugA", "nupA", "nuaA", "nunZA", "nugZA", "EavA", "EavZA",
        "fp030077", "fp031074", "ff029073.ex", "ff031075.ex", "ff030077.ex")


FY5 = ((36, 92), (56, 144), (38, 96), (54, 140))  # fymodel 5: two fragment pairs of U-236 with own populations


def ff5_files(d: Path) -> None:
    """fymodel 5 population files ff<ZZZ><AAA>.ex (npopE 20 energies 0.5-10 MeV, 12 spins, two parities): a Gaussian
    in E around 4-7 MeV times a spin distribution of cutoff 5-8, ~25-100 mb per fragment, printed es12.5."""
    d.mkdir(parents=True, exist_ok=True)
    for k, (z, a) in enumerate(FY5):
        e = np.linspace(0.5, 10.0, 20)
        ec, w, sig2, scale = 4.0 + k, 1.5 + 0.2 * k, 5.0 + k, 25.0 * (k + 1)
        rows = []
        for par in (0, 1):
            for x in e:
                j = np.arange(12) + 0.5 * (a % 2)
                pj = (2 * j + 1) * np.exp(-((j + 0.5) ** 2) / (2 * sig2))
                p = scale * np.exp(-((x - ec) ** 2) / (2 * w * w)) * pj / pj.sum() * (0.6 if par else 0.4) / 20 * 2
                rows.append(f"{x:10.5f}" + "".join(f"{v:12.5E}" for v in p))
        (d / f"ff{z:03d}{a:03d}.ex").write_text(f"{20:6d}{12:4d}{2:4d}\n" + "\n".join(rows) + "\n")


def _lines(kw: str) -> list[str]:
    return [x.strip() for x in kw.split(";") if x.strip()]


def _deck(target: str, kw: str) -> str:
    el, a, _, _ = TARGETS[target]
    return "\n".join(["projectile n", f"element {el}", f"mass {a}", "energy energies"] + _lines(BASE + ";" + kw)) + "\n"


def _tag(target: str, kw: str) -> str:
    return f"{target}_{hashlib.sha1(_deck(target, kw).encode()).hexdigest()[:10]}"


def frag_summary(talys_out: Path) -> list[dict]:
    """talys.out's reaction summary of every fragment run: E, initial population, multiplicities, residuals (Z, A,
    total, level, isomeric xs, ratio)."""
    import re

    out, cur, mode, last_e = [], None, None, None
    for line in open(talys_out, errors="replace"):
        if "Total population of input excitation energy grid" in line:
            cur = {"initpop_in": float(line.split(":")[1]), "mult": {}, "res": [], "E": last_e}
            mode = None
        elif "RESULTS FOR E=" in line and "REACTION SUMMARY" not in line:
            last_e = float(line.split("E=")[1].split()[0])
        elif cur is None:
            continue
        elif "1. Initial population cross section" in line:
            cur["initpop"] = float(line.split("=")[1])
        elif "Multiplicity=" in line:
            cur["mult"][line.split("=")[0].strip()] = float(line.split("Multiplicity=")[1])
        elif "a. Per isotope" in line:
            mode = "iso"
        elif "b. Per mass" in line:
            mode = None
        elif mode == "iso":
            t = line.split()
            if len(t) >= 3 and t[0].isdigit():
                m = re.match(r"\s*(\d+)\s+(\d+)\s+\([^)]*\)\s+(\S+)\s+(\d+)\s+(\S+)\s+(\S+)", line)
                if m:
                    cur["res"].append([int(m.group(1)), int(m.group(2)), float(m.group(3)), int(m.group(4)),
                                       float(m.group(5)), float(m.group(6))])
                elif cur["res"]:
                    cur["res"].append([cur["res"][-1][0], cur["res"][-1][1], None, int(t[0]), float(t[1]),
                                       float(t[2])])
        elif "End of calculation for" in line:
            cur["nuc"] = line.split("for")[1].strip()
            out.append(cur)
            cur, mode = None, None
    return out


def stock(target: str, kw: str) -> Path:
    d = STOCK / _tag(target, kw)
    if (d / "frag_summary.json").is_file():
        return d
    STOCK.mkdir(parents=True, exist_ok=True)
    # scratch in RAM (/dev/shm) when there is one: a fragment run writes ~70 MB of per-fragment files, and the WSL disk
    # lives on a nearly full C: (DISKGUARD kills the largest talys / python while C: falls)
    shm = Path("/dev/shm")
    tmp = Path(tempfile.mkdtemp(prefix="b14ctmp_", dir=str(shm if shm.is_dir() else STOCK)))
    try:
        (tmp / "talys.inp").write_text(_deck(target, kw))
        (tmp / "energies").write_text("".join(f"{e:g}\n" for e in TARGETS[target][3]))
        if "fymodel 5" in BASE:
            ff5_files(tmp)
        with open(tmp / "talys.inp") as fi, open(tmp / "talys.out", "w") as fo:
            subprocess.run(["flock", LOCK, "nice", "-n", "10", TALYS], stdin=fi, stdout=fo, cwd=tmp, check=True)
        d.mkdir(parents=True, exist_ok=True)
        json.dump(frag_summary(tmp / "talys.out"), open(d / "frag_summary.json", "w"))
        for f in tmp.iterdir():
            if f.name.startswith(TRIM) or f.name in ("talys.inp", "energies"):
                shutil.copy(f, d / f.name)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return d


def ours(target: str, kw: str, mode: str = "talys") -> dict:
    f = ENG / f"b14c_{_tag(target, kw)}_{mode}.npz"
    if f.is_file():
        z = np.load(f)
        return {k: z[k] for k in z.files}
    import time

    import torch

    from physics.hf import engine_c
    from physics.hf.chartrun import drop_target_caches
    from physics.hf.engine import ChainedFull
    from physics.hf.input import fitlib

    _, A, Z, energies = TARGETS[target]
    lines = _lines(BASE + ";" + kw) + (TALYS_DECK if mode == "talys" else [])
    env = dict(TALYS_ENV) if mode == "talys" else {}
    env.update(INCOGNITA_TALYS_FIT="lines", INCOGNITA_TALYS_FIT_LINES=";".join(lines))
    if "fymodel 5" in BASE:
        ff5_files(ENG / "b14c_ff5")
        env["INCOGNITA_FFDIR"] = str(ENG / "b14c_ff5")
    old = {k: os.environ.get(k) for k in env}
    t0 = time.time()
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
    out = {"seconds": np.array([time.time() - t0])}
    for name, cols in r.fission_yields.items():
        if name.startswith(KEEP) or name.startswith(("fp", "rp")) and ".i0" in name:
            for c, v in cols.items():
                out[f"{name}/{c}"] = np.asarray(v)
    ENG.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(f, **out)
    return out


def read_za(p: Path) -> np.ndarray:
    """yieldZA<E>.fis of a fymodel >= 3 run: Z, A, isomer, FP_yield, FF_yield, FP_xs, FF_xs, ratio (NaN where TALYS
    leaves the column blank: FF columns of isomer rows, ratio of the -1 rows)."""
    nan = float("nan")
    rows = []
    for ln in p.read_text().splitlines():
        t = ln.split()
        if not t or ln.lstrip().startswith("#"):
            continue
        v = [float(x) for x in t]
        rows.append(v + [nan] if len(v) == 7 else [v[0], v[1], v[2], v[3], nan, v[4], nan, v[5]])
    return np.array(rows, dtype=float).reshape(-1, 8)


def _estr(e: float) -> str:
    from physics.hf.fisyield import estring

    return estring(e)


def compare(target: str, kw: str, mode: str = "talys") -> dict:
    d = stock(target, kw)
    us = ours(target, kw, mode)
    worst: dict = {}

    def note(fam, v, where):
        if v > worst.get(fam, (-1.0, ""))[0]:
            worst[fam] = (v, where)

    summ = json.load(open(d / "frag_summary.json"))
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
            note("xspost", _ln(float(us[f"{key}/Tot"][2]), tot[2]), f"E={e:g}")
        z = read_za(d / f"yieldZA{es}.fis")
        kz = f"yieldZA{es}.fis"
        oz = {(int(a_), int(b_), int(c_)): (v, w, q) for a_, b_, c_, v, w, q in zip(
            us[f"{kz}/Z"], us[f"{kz}/A"], us[f"{kz}/isomer"], us[f"{kz}/FF_yield"], us[f"{kz}/FP_yield"],
            us[f"{kz}/Isomeric_ratio"])}
        rows = [r for r in z if int(r[2]) == -1]
        mxf = max(r[4] for r in rows)
        mxp = max(r[3] for r in rows)
        big = set()
        for row in rows:
            k = (int(row[0]), int(row[1]), -1)
            o = oz.get(k, (0.0, 0.0, 0.0))
            if row[4] >= 1e-2 * mxf:
                note("za", _ln(o[0], row[4]), f"E={e:g} Z={k[0]} A={k[1]}")
            if row[3] >= 1e-2 * mxp:
                note("zapost", _ln(o[1], row[3]), f"E={e:g} Z={k[0]} A={k[1]}")
                big.add(k[:2])
        nst = nus = 0
        for row in z:
            if int(row[2]) < 0:
                continue
            nst += 1
            k = (int(row[0]), int(row[1]), int(row[2]))
            o = oz.get(k)
            if o is None:
                note("iso_missing", 1.0, f"E={e:g} Z={k[0]} A={k[1]} i{k[2]}")
                continue
            nus += 1
            if k[:2] in big and row[-1] >= 0.05:
                note("iso", _ln(o[2], row[-1]), f"E={e:g} Z={k[0]} A={k[1]} i{k[2]}")
        note("iso_rows", abs(nst - sum(1 for k in oz if k[2] >= 0)), f"stock {nst} ours {sum(1 for k in oz if k[2] >= 0)}")
        for x in "ng":
            nb, _ = read(d / f"nubar{x}.tot")
            ov = us.get(f"nubar{x}.tot/nubar")
            sv = float(nb[np.isclose(nb[:, 0], e), 1][0])
            note(f"nubar_{x}", _ln(float(ov[np.isclose(us[f'nubar{x}.tot/E'], e)][0]) if ov is not None else 0.0, sv),
                 f"E={e:g} stock {sv:.6g} ours {float(ov[0]) if ov is not None else 0:.6g}")
        n, _ = read(d / f"nunA{es}.fis")
        on = us[f"nunA{es}.fis/nu"]
        ffm = a[:, 2].max()
        for i in range(n.shape[0]):
            if a[i, 2] >= 1e-2 * ffm and n[i, 1] > 0:
                note("nuA", _ln(on[i], n[i, 1]), f"E={e:g} A={int(n[i, 0])}")
        fk = f"ff_fragments{es}"
        if f"{fk}/Z" in us:
            of = {(int(zz), int(aa)): (p, mn, mg) for zz, aa, p, mn, mg in zip(
                us[f"{fk}/Z"], us[f"{fk}/A"], us[f"{fk}/xsinitpop"], us[f"{fk}/mult_n"], us[f"{fk}/mult_g"])}
            from physics.hf.core.constants import NUC

            sym = {s.lower(): i + 1 for i, s in enumerate(NUC)}
            pmax = max(x["initpop"] for x in summ)
            note("frag_count", abs(len(of) - len(summ)), f"stock {len(summ)} ours {len(of)}")
            for x in summ:
                nuc = x["nuc"]
                el = nuc.rstrip("0123456789")
                k = (sym[el.lower()], int(nuc[len(el):]))
                o = of.get(k)
                if o is None:
                    note("frag_missing", 1.0, nuc)
                    continue
                note("frag_pop", _ln(o[0], x["initpop"]), nuc)
                if x["initpop"] >= 1e-3 * pmax:
                    if x["mult"]["neutron"] >= 0.05:
                        note("frag_n", _ln(o[1], x["mult"]["neutron"]), nuc)
                    note("frag_g", _ln(o[2], x["mult"]["gamma"]), nuc)
    return worst


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default="u235")
    ap.add_argument("--kw", default="")
    ap.add_argument("--mode", default="talys")
    ap.add_argument("--stock-only", action="store_true")
    ap.add_argument("--fy", type=int, default=4, help="4: fragment files (gef); 5: own populations (FY5)")
    a = ap.parse_args()
    global BASE
    BASE = f"massdis y;fymodel {a.fy}"
    if a.stock_only:
        print(stock(a.target, a.kw))
        return
    w = compare(a.target, a.kw, a.mode)
    print(json.dumps({k: (round(v[0], 4), v[1]) for k, v in sorted(w.items())}, indent=1))


if __name__ == "__main__":
    main()
