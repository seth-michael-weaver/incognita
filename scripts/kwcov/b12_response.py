#!/usr/bin/env python3
"""KWCOV B12 acceptance: recoils and the LAB frame (recoil, labddx, recoilaverage, maxenrec, anglesrec, channelenergy)
vs stock TALYS-2.25.

    PY=~/fastgate_data/eng/16606b356d6e/.venv/bin/python   # WSL; the engine venv has torch
    $PY scripts/kwcov/b12_response.py --target fe56 --kw "labddx y" [--mode talys]
    $PY scripts/kwcov/b12_response.py --all                 # the table of COVERAGE_PLAN.md B12

Every deck is the target's base deck (recoil y, energies 1 5 14 MeV) plus `--kw` lines (';'-separated). Stock runs keep
the recoil, LAB, spectrum and exclusive-recoil files in ~/kwcov/stock/b12/<target>_<hash>/ (scratch deleted); engine runs
(engine_c.run on the deck lines; `--mode talys` adds fidelity.py's TALYS_DECK / TALYS_ENV: every deliberate INCOGNITA
default at its TALYS value) keep Results.recoil / Results.spectra as .npz in ~/kwcov/eng/b12_<target>_<hash>.npz.
Metrics, |ln(ours/stock)| in %, worst over the files of the deck and the three energies:
  rec    recoil spectra rec<ZZZ><AAA>spec*.tot of residuals with stock integral > 1 mb, per bin where stock > 1e-2 of the
         file's maximum (+ the integral)
  lab    LAB ejectile spectra <x>spec*.lab with integral > 1 mb, bins where stock > 1e-2 of the maximum
  ddx    LAB DDX files (<x>ddxE*.lab, <x>ddxA*.lab) where stock > 1e-2 of the maximum
  excl   exclusive recoil spectra sp*.rec of channels > 1 mb (same bins)
  cm     with channelenergy: the CM spectra <x>spec*.tot (espec grid and xs) where stock > 1 mb/MeV
  resp   |ln(R/S)|, R = ours(kw)/ours(base), S = stock(kw)/stock(base), per bin of every file both decks write on the
         same grid (recoil and LAB spectra), where stock > 1e-2 of the maximum
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
STOCK = Path(os.path.expanduser("~/kwcov/stock/b12"))
ENG = Path(os.path.expanduser("~/kwcov/eng"))
TALYS = os.path.expanduser("~/opt/talys-src/bin/talys")
LOCK = "/tmp/incognita_heavy.lock"
ENERGIES = (1.0, 5.0, 14.0)
TARGETS = {"fe56": ("n", "fe", 56, 26), "co59": ("n", "co", 59, 27), "u238": ("n", "u", 238, 92),
           "nb93p": ("p", "nb", 93, 41)}
BASE = "recoil y;filerecoil y;channels y;filechannels y"
LABKW = "labddx y;ddxmode 3;fileddxa n,30,150;fileddxa p,30;fileddxe n,3.0;fileddxe p,6.0"
#: fidelity.py (branch fidelity1): every deliberate INCOGNITA default at its TALYS value
TALYS_DECK = ["fluxclose n", "npwindow n", "chancap n", "nnleak n", "exactfis n", "alphatemp 0", "sfexit n",
              "kevleak2 n", "heavymacs2 n", "ftglobal n", "ccexitnbnf n", "tfold n", "ctwcont n", "alphaentr 0"]
TALYS_ENV = {"INCOGNITA_GRIDTOP": "n", "INCOGNITA_SPECCLOSE": "0", "INCOGNITA_LOWEPOT": "0",
             "INCOGNITA_TARMASSFIX": "0", "INCOGNITA_ISOROTPASS": "0"}
#: the --all table: (target, kw, base kw for the response or None)
TABLE = [
    ("fe56", "", None),
    ("fe56", LABKW, ""),
    ("fe56", LABKW + ";recoilaverage y", LABKW),
    ("fe56", "maxenrec 10", None),
    ("fe56", LABKW + ";anglesrec 4", LABKW),
    ("fe56", "channelenergy y", ""),
    ("co59", "", None),
    ("u238", "", None),
]


def _lines(kw: str) -> list[str]:
    out = []
    for x in kw.split(";"):
        x = x.strip()
        if not x:
            continue
        w = x.split(None, 1)
        if w[0].lower() in ("fileddxa", "fileddxe") and "," in x:  # stock: one deck line per value
            sym = None
            for v in w[1].replace(",", " ").split():
                if v[:1].isalpha():
                    sym = v
                else:
                    out.append(f"{w[0]} {sym} {v}")
        else:
            out.append(x)
    return out


def _deck(target: str, kw: str) -> str:
    p, el, a, _ = TARGETS[target]
    return "\n".join([f"projectile {p}", f"element {el}", f"mass {a}", "energy energies"] + _lines(BASE + ";" + kw)) + "\n"


def _tag(target: str, kw: str) -> str:
    return f"{target}_{hashlib.sha1(_deck(target, kw).encode()).hexdigest()[:10]}"


def stock(target: str, kw: str) -> Path:
    d = STOCK / _tag(target, kw)
    if (d / "talys.inp").is_file():
        return d
    STOCK.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="b12tmp_", dir=str(STOCK)))
    try:
        (tmp / "talys.inp").write_text(_deck(target, kw))
        (tmp / "energies").write_text("".join(f"{e:g}\n" for e in ENERGIES))
        with open(tmp / "talys.inp") as fi, open(tmp / "talys.full", "w") as fo:
            subprocess.run(["flock", LOCK, "nice", "-n", "10", TALYS], stdin=fi, stdout=fo, cwd=tmp, check=True)
        d.mkdir(parents=True, exist_ok=True)
        for f in tmp.iterdir():
            n = f.name
            if (n.startswith("rec") or n.endswith((".lab", ".rec")) or re.fullmatch(r"[gnpdtha]spec\d{4}\.\d{3}\.tot", n)
                    or n in ("talys.inp", "energies")):
                shutil.copy(f, d / n)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return d


def ours(target: str, kw: str, mode: str = "talys") -> dict:
    f = ENG / f"b12_{_tag(target, kw)}_{mode}.npz"
    if f.is_file():
        z = np.load(f)
        return {k: z[k] for k in z.files}
    import torch

    from physics.hf import engine_c
    from physics.hf.chartrun import drop_target_caches
    from physics.hf.engine import ChainedFull
    from physics.hf.input import fitlib

    p, _, A, Z = TARGETS[target]
    lines = _lines(BASE + ";" + kw) + (TALYS_DECK if mode == "talys" else [])
    lines = [x for x in lines if x.split()[0].lower() not in ("filerecoil", "channels", "filechannels")]
    merged: dict = {}  # the engine reads one fileddxa / fileddxe line (`fileddxa n,30,150,p,30`)
    for x in [x for x in lines if x.split()[0].lower() in ("fileddxa", "fileddxe")]:
        k, v = x.split(None, 1)
        merged.setdefault(k.lower(), []).append(v.replace(" ", ","))
    lines = [x for x in lines if x.split()[0].lower() not in merged] + [f"{k} {','.join(v)}" for k, v in merged.items()]
    old = {k: os.environ.get(k) for k in list(TALYS_ENV) + ["INCOGNITA_TALYS_FIT", "INCOGNITA_TALYS_FIT_LINES",
                                                            "INCOGNITA_CPINC"]}
    try:
        if mode == "talys":
            os.environ.update(TALYS_ENV)
        if p != "n":
            os.environ["INCOGNITA_CPINC"] = p
        os.environ["INCOGNITA_TALYS_FIT"] = "lines"
        os.environ["INCOGNITA_TALYS_FIT_LINES"] = ";".join(lines)
        drop_target_caches()
        import fcntl

        with open(LOCK, "a") as lk:
            fcntl.flock(lk, fcntl.LOCK_EX)
            with torch.inference_mode():
                r = engine_c.run(ChainedFull(Z=Z, A=A, declared_energies=ENERGIES))
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        fitlib.deactivate()
        drop_target_caches()
    out = {f"recoil/{k}": v.numpy() for k, v in r.recoil.items()}
    out.update({f"spectra/{k}": v.numpy() for k, v in r.spectra.items() if k.endswith(("spec.tot", "spec.tot:E"))})
    ENG.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(f, **out)
    return out


def read(p: Path):
    rows = [ln.split() for ln in p.read_text().splitlines() if ln.strip() and not ln.lstrip().startswith("#")]
    hdr = {}
    for ln in p.read_text().splitlines():
        if ln.startswith("#") and ":" in ln:
            k, _, v = ln[1:].partition(":")
            hdr[k.strip()] = v.strip()
    return np.array([[float(x) for x in r] for r in rows]) if rows else np.zeros((0, 2)), hdr


def stock_files(d: Path) -> dict:
    """{(our Results.recoil / spectra name, energy index): (x, y, header)} of a stock directory."""
    out = {}
    for p in sorted(d.iterdir()):
        n = p.name
        m = re.fullmatch(r"rec(\d{6})spec(\d{4}\.\d{3})\.tot", n)
        if m:
            key = f"recoil/rec{m.group(1)}spec.tot"
        elif re.fullmatch(r"sp(\d{6})E(\d{4}\.\d{3})\.rec", n):
            m = re.fullmatch(r"sp(\d{6})E(\d{4}\.\d{3})\.rec", n)
            key = f"recoil/sp{m.group(1)}.rec"
        elif re.fullmatch(r"([gnpdtha])spec(\d{4}\.\d{3})\.lab", n):
            m = re.fullmatch(r"([gnpdtha])spec(\d{4}\.\d{3})\.lab", n)
            key = f"recoil/{m.group(1)}spec.lab"
        elif re.fullmatch(r"([gnpdtha])ddxE(\d{4}\.\d{3})([AE]\d+\.\d)\.lab", n):
            m = re.fullmatch(r"([gnpdtha])ddxE(\d{4}\.\d{3})([AE]\d+\.\d)\.lab", n)
            key = f"recoil/{m.group(1)}ddx{m.group(3)}.lab"
        elif re.fullmatch(r"([gnpdtha])spec(\d{4}\.\d{3})\.tot", n):
            m = re.fullmatch(r"([gnpdtha])spec(\d{4}\.\d{3})\.tot", n)
            key = f"spectra/{m.group(1)}spec.tot"
        else:
            continue
        e = float(re.search(r"(\d{4}\.\d{3})", n).group(1))
        i = min(range(len(ENERGIES)), key=lambda j: abs(ENERGIES[j] - e))
        a, h = read(p)
        out[(key, i)] = (a, h)
    return out


def _ln(a, b):
    return abs(math.log(a / b)) * 100.0 if a > 0 and b > 0 else (0.0 if a == b else float("inf"))


def compare(target: str, kw: str, mode: str = "talys") -> dict:
    """Worst |ln(ours/stock)| per metric family: {family: (value %, where)}."""
    st = stock_files(stock(target, kw))
    us = ours(target, kw, mode)
    worst: dict = {}

    def note(fam, v, where):
        if v > worst.get(fam, (-1.0, ""))[0]:
            worst[fam] = (v, where)

    for (key, i), (a, h) in st.items():
        if a.size == 0:
            continue
        where = f"{key.split('/')[1]} E={ENERGIES[i]:g}"
        if key not in us:
            if a[:, 1].max() > 1.0:
                note("missing", float("inf"), where)
            continue
        y = us[key][i]
        if key.startswith("spectra/"):
            if "channelenergy" not in kw:
                continue
            x = us[key + ":E"][i]
            n = min(a.shape[0], int(np.sum(~np.isnan(y))))
            for j in range(n):
                if a[j, 1] > 1.0:
                    note("cm", max(_ln(y[j], a[j, 1]), abs(x[j] / a[j, 0] - 1) * 100), f"{where} E'={a[j, 0]:.3g}")
            continue
        fam = ("rec" if "/rec" in key else "excl" if key.endswith(".rec") else "lab" if "spec.lab" in key else "ddx")
        if fam == "rec":
            si = float(h.get("Integrated recoil spectrum [mb]", "0"))
            if si <= 1.0:
                continue
            note(fam, _ln(float(us[key + ":integral"][i]), si), where + " integral")
        if fam == "lab":
            si = float(h.get("Energy-integrated cross section [mb]", "0"))
            if si <= 1.0:
                continue
            note(fam, _ln(float(us[key + ":integral"][i]), si), where + " integral")
        if fam == "excl" and float(np.sum(a[:, 1])) * (a[1, 0] - a[0, 0] if a.shape[0] > 1 else 1.0) <= 1.0:
            continue
        yv = np.asarray(y, float)
        n = min(a.shape[0], int(np.sum(~np.isnan(yv))))
        mx = float(np.max(a[:n, 1])) if n else 0.0
        for j in range(n):
            if a[j, 1] > 1e-2 * mx and mx > 0:
                note(fam, _ln(yv[j], a[j, 1]), f"{where} x={a[j, 0]:.4g}")
    return worst


def response(target: str, kw: str, base: str, mode: str = "talys") -> tuple[float, str]:
    sk, sb = stock_files(stock(target, kw)), stock_files(stock(target, base))
    uk, ub = ours(target, kw, mode), ours(target, base, mode)
    w, where = 0.0, ""
    for (key, i), (a, _) in sk.items():
        if (key, i) not in sb or key not in uk or key not in ub or key.startswith("spectra/"):
            continue
        b = sb[(key, i)][0]
        if a.shape != b.shape or not np.allclose(a[:, 0], b[:, 0], rtol=1e-5):
            continue
        yk, yb = np.asarray(uk[key][i], float), np.asarray(ub[key][i], float)
        n = min(a.shape[0], int(np.sum(~np.isnan(yk))), int(np.sum(~np.isnan(yb))))
        mx = float(np.max(a[:n, 1])) if n else 0.0
        for j in range(n):
            if a[j, 1] > 1e-2 * mx and b[j, 1] > 0 and yb[j] > 0 and yk[j] > 0 and mx > 1e-3:
                v = abs(math.log((yk[j] / yb[j]) / (a[j, 1] / b[j, 1]))) * 100
                if v > w:
                    w, where = v, f"{key.split('/')[1]} E={ENERGIES[i]:g} x={a[j, 0]:.4g}"
    return w, where


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default="fe56")
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
        print(f"{target} [{kw or 'base'}] {a.mode}: {txt}" + (f"  resp {r[0]:.3f}% ({r[1]})" if r else ""), flush=True)
    if a.json:
        Path(a.json).write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
