#!/usr/bin/env python3
"""KWCOV B13 acceptance: ingredient output files (outlevels, outdensity, filedensity, outgamma, filepsf, outinverse,
outtransenergy, outomp, blockomp, outkd, partable, outbasic) vs stock TALYS-2.25.

    PY=~/fastgate_data/eng/16606b356d6e/.venv/bin/python   # WSL; the engine venv has torch
    $PY scripts/kwcov/b13_response.py --target fe56 --kw "outtransenergy n"   # one deck, per-file table
    $PY scripts/kwcov/b13_response.py --all                                    # the table of COVERAGE_PLAN.md B13

Every deck is the target's base (`projectile n`, the energies, every B13 output switch) plus `--kw` lines (';'
separated). Stock runs keep only the B13 files (+ talys.out's KD03 lines) in ~/kwcov/stock/b13/<tag>/ (scratch
deleted); engine runs write Results.ingout with INCOGNITA_INGOUT_DIR to ~/kwcov/eng/b13/<tag>_<mode>/. Mode
`talys` = b10_response's TALYS_DECK / TALYS_ENV (the INCOGNITA defaults that are not TALYS switched off); `default`
= the engine as shipped. Metric per file: max |ln(ours/stock)| over every numeric datablock cell and every numeric
header value with |stock| > FLOOR x the column's largest |value| (cells below that: |ours - stock| <= FLOOR x the
largest, else counted); block / row count mismatches are listed. parameters.dat: per (keyword, Z, A, qualifier)
row present in both, and the keys only one side has.
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
STOCK = Path(os.path.expanduser("~/kwcov/stock/b13"))
ENG = Path(os.path.expanduser("~/kwcov/eng/b13"))
TALYS = os.path.expanduser("~/opt/talys-src/bin/talys")
LOCK = "/tmp/incognita_heavy.lock"
FLOOR = 1.0e-6
SWITCHES = ["outlevels y", "outdensity y", "filedensity y", "outgamma y", "filepsf y", "outinverse y", "outomp y",
            "outkd y", "partable y"]
TALYS_DECK = ["fluxclose n", "npwindow n", "chancap n", "nnleak n", "exactfis n", "alphatemp 0", "sfexit n",
              "kevleak2 n", "heavymacs2 n", "ftglobal n", "ccexitnbnf n", "tfold n", "ctwcont n", "alphaentr 0"]
TALYS_ENV = {"INCOGNITA_GRIDTOP": "n", "INCOGNITA_SPECCLOSE": "0", "INCOGNITA_LOWEPOT": "0",
             "INCOGNITA_TARMASSFIX": "0", "INCOGNITA_ISOROTPASS": "0"}
TARGETS = {"fe56": ("fe", 56, "1 14"), "u238": ("u", 238, "1 14"), "pb208": ("pb", 208, "14"),
           "co59": ("co", 59, "0.01 5")}
#: the --all table: (target, kw, mode)
TABLE = [
    ("fe56", "", "talys"), ("fe56", "", "default"), ("fe56", "outtransenergy n;blockomp n", "talys"),
    ("fe56", "ldmodel 2;colenhance y;strength 8", "talys"), ("fe56", "outdensity y;filedensity n", "talys"),
    ("co59", "", "talys"), ("pb208", "", "talys"), ("u238", "", "talys"), ("fe56", "outbasic y;blocklevels y", "talys"),
]


def _lines(kw: str) -> list[str]:
    return [x.strip() for x in kw.split(";") if x.strip()]


def deck(target: str, kw: str) -> list[str]:
    el, a, en = TARGETS[target]
    out, seen = [], {}
    for ln in ["projectile n", f"element {el}", f"mass {a}", "energy energies"] + SWITCHES + _lines(kw):
        k = ln.split()[0].lower()
        if k in seen:
            out[seen[k]] = ln
        else:
            seen[k] = len(out)
            out.append(ln)
    return out


def _tag(target: str, kw: str) -> str:
    return f"{target}_{hashlib.sha1(('|'.join(deck(target, kw)) + TARGETS[target][2]).encode()).hexdigest()[:10]}"


def _keep(name: str) -> bool:
    return (name.startswith(("levels", "ld0", "nld", "psf", "transmission_", "cross_", "omppar_", "ompE"))
            or name in ("omp.out", "spr.opt", "parameters.dat", "talys.inp"))


def stock(target: str, kw: str) -> Path:
    d = STOCK / _tag(target, kw)
    if (d / "talys.inp").is_file():
        return d
    STOCK.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="b13tmp_", dir=str(STOCK)))
    try:
        (tmp / "energies").write_text("\n".join(TARGETS[target][2].split()) + "\n")
        (tmp / "talys.inp").write_text("\n".join(deck(target, kw)) + "\n")
        with open(tmp / "talys.inp") as fi, open(tmp / "talys.full", "w") as fo:
            subprocess.run(["flock", LOCK, "nice", "-n", "10", TALYS], stdin=fi, stdout=fo, cwd=tmp, check=True)
        d.mkdir(parents=True, exist_ok=True)
        for p in tmp.iterdir():
            if _keep(p.name):
                shutil.copy(p, d / p.name)
        full = (tmp / "talys.full").read_text(errors="replace").splitlines()
        kd = [i for i, s in enumerate(full) if "KD03 OMP parameters" in s]
        (d / "kd03.out").write_text("\n".join(x for i in kd[:400] for x in full[i:i + 6]) + "\n")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return d


def engine(target: str, kw: str, mode: str) -> Path:
    d = ENG / f"{_tag(target, kw)}_{mode}"
    if (d / "done").is_file():
        return d
    shutil.rmtree(d, ignore_errors=True)
    d.mkdir(parents=True, exist_ok=True)
    env = {k: v for k, v in os.environ.items() if not k.startswith(("INCOGNITA_", "NUCLIDO_"))}
    lines = deck(target, kw) + (TALYS_DECK if mode == "talys" else [])
    if mode == "talys":
        env.update(TALYS_ENV)
    env.update(OMP_NUM_THREADS="1", INCOGNITA_INGOUT_DIR=str(d))
    (d / "energies").write_text("\n".join(TARGETS[target][2].split()) + "\n")
    (d / "talys.inp").write_text("\n".join(lines) + "\n")
    p = subprocess.run(["flock", LOCK, "nice", "-n", "10", sys.executable, "-c",
                        "import sys; sys.path.insert(0, '.'); from physics.hf.input.deck import run_deck; "
                        f"run_deck({str(d / 'talys.inp')!r})"], env=env, cwd=ROOT, capture_output=True, text=True)
    if p.returncode != 0:
        (d / "error").write_text((p.stderr or p.stdout)[-4000:])
        return d
    (d / "done").write_text("ok")
    return d


# ------------------------------------------------------------------------------------------------ comparison
def _cells(a: np.ndarray, b: np.ndarray) -> tuple[float, int, tuple]:
    """(max |ln(a/b)| over |b| > FLOOR*max|b|, count of small cells off by more than FLOOR*max|b|, worst index)."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    if a.size == 0 or b.size == 0:
        return 0.0, 0, ()
    big = np.nanmax(np.abs(b)) if np.isfinite(b).any() else 0.0
    if big == 0.0:
        return 0.0, int(np.sum(np.abs(a) > 1e-30)), ()
    m = np.abs(b) > FLOOR * big
    with np.errstate(divide="ignore", invalid="ignore"):
        r = np.where(m & (np.sign(a) == np.sign(b)), np.abs(np.log(np.abs(a) / np.where(m, np.abs(b), 1.0))), 0.0)
        r = np.where(m & (np.sign(a) != np.sign(b)) & (np.abs(a - b) > FLOOR * big), np.inf, r)
    bad = int(np.sum(~m & (np.abs(a - b) > FLOOR * big)))
    w = np.unravel_index(int(np.nanargmax(r)), r.shape) if r.size else ()
    return float(np.nanmax(r)) if r.size else 0.0, bad, w


def _meta_num(meta: dict) -> dict:
    out = {}
    for k, v in meta.items():
        try:
            out[k] = float(str(v).split()[0])
        except (ValueError, IndexError):
            continue
    return out


SKIP_META = {"Z", "A", "columns", "entries", "date"}


def compare_yandf(ours: Path, theirs: Path) -> dict:
    from physics.hf.yandf import parse_blocks

    A, B = parse_blocks(ours), parse_blocks(theirs)
    res = {"blocks": (len(A), len(B)), "data": 0.0, "meta": 0.0, "bad": 0, "rows": [], "worst": ""}
    for i, (a, b) in enumerate(zip(A, B)):
        if a.data.shape != b.data.shape:
            res["rows"].append((i, a.data.shape, b.data.shape))
            n = min(a.data.shape[0], b.data.shape[0])
            if a.data.shape[1:] != b.data.shape[1:] or n == 0:
                continue
            da, db = a.data[:n], b.data[:n]
        else:
            da, db = a.data, b.data
        for j in range(db.shape[1] if db.ndim == 2 else 0):
            r, bad, w = _cells(da[:, j], db[:, j])
            res["bad"] += bad
            if r > res["data"]:
                res["data"] = r
                res["worst"] = f"block {i} col {b.columns[j]} row {w[0] if w else '-'}"
        ma, mb = _meta_num(a.meta), _meta_num(b.meta)
        for k in mb:
            if k in SKIP_META or k not in ma:
                continue
            r, bad, _w = _cells(np.array([ma[k]]), np.array([mb[k]]))
            if mb[k] == 0.0 and ma[k] != 0.0:
                r = math.inf
            if r > res["meta"]:
                res["meta"] = r
                res["worst_meta"] = f"block {i} {k}: ours {ma[k]:.6g} stock {mb[k]:.6g}"
        missing = [k for k in mb if k not in ma and k not in SKIP_META]
        if missing:
            res.setdefault("missing_meta", set()).update(missing)
    if "missing_meta" in res:
        res["missing_meta"] = sorted(res["missing_meta"])
    return res


def _levels_rows(p: Path) -> tuple[dict, list]:
    meta, rows = {}, []
    for ln in p.read_text().splitlines():
        if ln.startswith("#"):
            m = re.match(r"#\s+(.+?):\s+(\S+)\s*$", ln)
            if m:
                try:
                    meta[m.group(1)] = float(m.group(2))
                except ValueError:
                    pass
            continue
        t = ln.split()
        if not t:
            continue
        if t[0] == "--->":
            rows.append(("b", int(t[1]), float(t[2]), float(t[3])))
        else:
            tau = float(ln[90:105]) if ln[90:105].strip() else 0.0
            rows.append(("l", int(t[0]), float(t[1]), float(t[2]), t[3], int(t[4]), tau))
    return meta, rows


def compare_levels(ours: Path, theirs: Path) -> dict:
    ma, ra = _levels_rows(ours)
    mb, rb = _levels_rows(theirs)
    meta = max((abs(math.log(ma[k] / mb[k])) if mb[k] and ma.get(k) else (0.0 if ma.get(k) == mb[k] else math.inf))
               for k in mb if k in ma)
    diff = sum(1 for x, y in zip(ra, rb) if x[0] != y[0] or any(
        (abs(u - v) > 1e-5 * max(abs(v), 1e-30) if isinstance(v, float) else u != v) for u, v in zip(x[1:], y[1:])))
    return {"rows": (len(ra), len(rb)), "meta": meta, "data": 0.0 if diff == 0 else float(diff), "bad": diff,
            "blocks": (1, 1)}


def _nld_numbers(p: Path) -> np.ndarray:
    vals = []
    for ln in p.read_text().splitlines():
        t = ln.split()
        if t and re.match(r"^-?\d", t[0]):
            vals.append([float(x) for x in t])
    return vals


def compare_nld(ours: Path, theirs: Path) -> dict:
    A, B = _nld_numbers(ours), _nld_numbers(theirs)
    worst, bad = 0.0, 0
    for a, b in zip(A, B):
        n = min(len(a), len(b))
        for u, v in zip(a[:n], b[:n]):
            if v == 0.0:
                bad += abs(u) > 1e-30
                continue
            worst = max(worst, abs(math.log(abs(u) / abs(v))) if u * v > 0 else math.inf)
    return {"rows": (len(A), len(B)), "data": worst, "meta": 0.0, "bad": bad, "blocks": (1, 1)}


def compare_partable(ours: Path, theirs: Path) -> dict:
    from physics.hf.input.defaults import parse_partable, parse_partable_general

    a = {(k, z, aa, q.strip()): v for k, z, aa, v, q in parse_partable(ours.read_text())}
    b = {(k, z, aa, q.strip()): v for k, z, aa, v, q in parse_partable(theirs.read_text())}
    worst, wk, nbad = 0.0, None, 0
    for k, v in b.items():
        if k not in a:
            continue
        u = a[k]
        tol = 6e-6 + 1e-5 * abs(v)
        if abs(u - v) > tol:
            nbad += 1
            r = abs(math.log(abs(u) / abs(v))) if u * v > 0 else math.inf
            if r > worst:
                worst, wk = r, (k, u, v)
    ga = {(k, p): v for k, p, v in parse_partable_general(ours.read_text())}
    gb = {(k, p): v for k, p, v in parse_partable_general(theirs.read_text())}
    gbad = [(k, ga.get(k), v) for k, v in gb.items() if k in ga and not _same(ga[k], v)]
    return {"rows": (len(a), len(b)), "only_stock": sorted({k[0] for k in b if k not in a}),
            "only_ours": sorted({k[0] for k in a if k not in b}),
            "nuclei": (len({(k[1], k[2]) for k in a}), len({(k[1], k[2]) for k in b})),
            "data": worst, "worst": wk, "bad": nbad, "general_bad": gbad, "meta": 0.0, "blocks": (1, 1)}


def _same(a: str, b: str) -> bool:
    try:
        return abs(float(a) - float(b)) <= 6e-6 + 1e-5 * abs(float(b))
    except ValueError:
        return a.strip() == b.strip()


def compare_kd(ours: Path, theirs: Path) -> dict:
    """The first KD03 block of each nucleon in talys.out vs Results.ingout['kd03'] (energy-independent geometry and
    depth coefficients; the energy column is not compared)."""
    txt = theirs.read_text()
    got = {}
    for ln in ours.read_text().splitlines():
        p = ln.split()[1]
        got[p] = {kv.split("=")[0]: float(kv.split("=")[1]) for kv in ln.split()[2:]}
    worst, n = 0.0, 0
    for part, name in (("n", "neutron"), ("p", "proton")):
        i = txt.find(f"KD03 OMP parameters for {name}")
        if i < 0 or part not in got:
            continue
        blk = txt[i:i + 900].splitlines()[1:6]
        for ln in blk:
            for key, val in re.findall(r"(\w+):\s*(-?[\d.Ee+-]+)", ln):
                if key in got[part]:
                    v = float(val)
                    n += 1
                    if v != 0.0:
                        worst = max(worst, abs(math.log(abs(got[part][key]) / abs(v))) if got[part][key] * v > 0
                                    else math.inf)
    return {"rows": (n, n), "data": worst, "meta": 0.0, "bad": 0, "blocks": (1, 1)}


def compare_dirs(eng: Path, st: Path) -> dict:
    out = {}
    names = sorted({p.name for p in st.iterdir()} | {p.name for p in eng.iterdir()})
    for name in names:
        if name in ("talys.inp", "energies", "done", "error"):
            continue
        a, b = eng / name, st / name
        if not a.is_file() or not b.is_file():
            out[name] = {"only": "ours" if a.is_file() else "stock"}
            continue
        try:
            if name.startswith("levels"):
                out[name] = compare_levels(a, b)
            elif name.startswith("nld"):
                out[name] = compare_nld(a, b)
            elif name == "parameters.dat":
                out[name] = compare_partable(a, b)
            elif name == "kd03.out":
                out[name] = compare_kd(a, b)
            else:
                out[name] = compare_yandf(a, b)
        except Exception as exc:  # noqa: BLE001
            out[name] = {"error": f"{type(exc).__name__}: {exc}"}
    return out


def run(target: str, kw: str, mode: str) -> dict:
    st = stock(target, kw)
    en = engine(target, kw, mode)
    if (en / "error").is_file():
        return {"error": (en / "error").read_text()[-1500:]}
    return compare_dirs(en, st)


def _pct(x) -> str:
    if x is None:
        return "-"
    if x == math.inf:
        return "inf"
    return f"{100.0 * x:.4f} %"


def show(res: dict) -> None:
    if "error" in res:
        print(res["error"])
        return
    for name, r in sorted(res.items()):
        if "only" in r:
            print(f"  {name:24s} only {r['only']}")
            continue
        if "error" in r:
            print(f"  {name:24s} ERROR {r['error']}")
            continue
        extra = ""
        if r.get("rows"):
            extra += f" rows {r['rows']}" if not isinstance(r["rows"], list) else f" shape-mismatch {r['rows'][:3]}"
        if r.get("missing_meta"):
            extra += f" missing-meta {r['missing_meta'][:6]}"
        if r.get("only_stock"):
            extra += f" only-stock {r['only_stock']}"
        if r.get("only_ours"):
            extra += f" only-ours {r['only_ours']}"
        if r.get("general_bad"):
            extra += f" general-bad {r['general_bad'][:5]}"
        w = r.get("worst", "")
        print(f"  {name:24s} data {_pct(r['data']):>12s} meta {_pct(r['meta']):>12s} bad {r['bad']:4d} "
              f"blocks {r['blocks']}{extra} {w} {r.get('worst_meta', '')}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default="fe56")
    ap.add_argument("--kw", default="")
    ap.add_argument("--mode", default="talys")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--json")
    a = ap.parse_args()
    todo = TABLE if a.all else [(a.target, a.kw, a.mode)]
    allres = {}
    for t, kw, mode in todo:
        print(f"== {t} [{kw}] {mode}", flush=True)
        r = run(t, kw, mode)
        show(r)
        allres[f"{t}|{kw}|{mode}"] = r
    if a.json:
        Path(a.json).write_text(json.dumps(allres, default=str, indent=1))


if __name__ == "__main__":
    main()
