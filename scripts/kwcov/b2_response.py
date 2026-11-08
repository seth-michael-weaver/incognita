#!/usr/bin/env python3
"""KWCOV B2 acceptance: the RESPONSE of the engine to a deck keyword vs stock TALYS-2.25's.

    PY=~/fastgate_data/eng/16606b356d6e/.venv/bin/python   # WSL; the engine venv has torch
    $PY scripts/kwcov/b2_response.py --target fe56 --kw "maxlevelsres 10" [--kw2 ...] [--json out.json]

For each deck line set `kw` (';'-separated TALYS lines) and target, R = ours(kw)/ours(default) and
S = stock(kw)/stock(default) per channel and energy; the plan's metric is |ln(R/S)| <= 2 % where stock > 1 mb.
Every run is a fresh process (the engine's per-target caches never see two decks), under `nice -n 10` and
`flock /tmp/incognita_heavy.lock`. Results are cached as JSON in ~/kwcov/b2/ (one file per target, deck, side), so
the default runs are made once. TALYS scratch directories are deleted after each run.

The engine side runs `engine_c.run(ChainedFull(Z, A, declared_energies))` with the deck lines in
INCOGNITA_TALYS_FIT_LINES (the engine's deck-line entry, fitlib's `lines` arm) and no other switch.
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
CACHE = Path(os.path.expanduser("~/kwcov/b2"))
TALYS = os.path.expanduser("~/opt/talys-src/bin/talys")
LOCK = "/tmp/incognita_heavy.lock"

TARGETS = {  # standard decks of COVERAGE_PLAN.md
    "fe56": ("fe", 26, 56), "co59": ("co", 27, 59), "u238": ("u", 92, 238), "zr90": ("zr", 40, 90),
}
ENERGIES = (1.0, 5.0, 14.0)
#: channel -> (stock file, engine Results key); the channels engine_job.py reports
CHANNELS = {
    "total": ("total.tot", "totals_mb/total"), "elastic": ("elastic.tot", "totals_mb/elastic"),
    "nonelastic": ("nonelastic.tot", "totals_mb/nonelastic"), "capture": ("xs000000.tot", "channels_mb/xs000000"),
    "np": ("xs010000.tot", "channels_mb/xs010000"), "na": ("xs000001.tot", "channels_mb/xs000001"),
    "n2n": ("xs200000.tot", "channels_mb/xs200000"), "inelastic": ("xs100000.tot", "channels_mb/xs100000"),
    "nd": ("xs001000.tot", "channels_mb/xs001000"), "npn": ("xs110000.tot", "channels_mb/xs110000"),
    "fission": ("fission.tot", "totals_mb/fission"),
    # isomeric channels (B1 CHANOBS names; the engine children run with INCOGNITA_CHANOBS=1, output only)
    "ng_L00": ("xs000000.L00", "extras/xs000000.L00"), "ng_L01": ("xs000000.L01", "extras/xs000000.L01"),
    "n2n_L00": ("xs200000.L00", "extras/xs200000.L00"), "n2n_L01": ("xs200000.L01", "extras/xs200000.L01"),
}


def _tag(target: str, kw: str, side: str, energies) -> Path:
    h = hashlib.sha1(f"{target}|{kw}|{','.join(map(str, energies))}".encode()).hexdigest()[:12]
    return CACHE / f"{side}_{target}_{h}.json"


def _lines(kw: str) -> list[str]:
    return [x.strip() for x in kw.split(";") if x.strip()]


def _rows(path: Path) -> list[list[float]]:
    out = []
    for ln in path.read_text(errors="replace").splitlines():
        s = ln.strip()
        if s and not s.startswith("#"):
            try:
                out.append([float(x) for x in s.split()])
            except ValueError:
                pass
    return out


def stock(target: str, kw: str, energies=ENERGIES, extra_files=()) -> dict:
    """{channel: [mb per energy]} of a stock TALYS run (cached)."""
    f = _tag(target, kw, "stock", energies)
    if f.is_file() and not extra_files:
        return json.loads(f.read_text())
    el, _, a = TARGETS[target]
    d = Path(tempfile.mkdtemp(prefix=f"b2_{target}_", dir=str(CACHE)))
    try:
        (d / "energies").write_text("".join(f"{e}\n" for e in energies))
        deck = [f"projectile n", f"element {el}", f"mass {a}", "energy energies", "channels y",
                "filechannels y", "fileresidual y", "outdiscrete y"] + _lines(kw)
        (d / "talys.inp").write_text("\n".join(deck) + "\n")
        if any(x.split()[:2] == ["best", "y"] for x in _lines(kw)):  # a best file's adjustment tables (Fe-56)
            from glob import glob

            sym = el[:1].upper() + el[1:]
            bd = os.path.expanduser(f"~/opt/talys-src/structure/best/{sym}{a:03d}")
            for t in glob(bd + "/tables/*.table") + [x for x in glob(bd + "/*") if os.path.isfile(x)]:
                shutil.copy(t, d)  # the files a best file names (tables, n-U238.omp, ...) are read from the cwd
        with open(d / "talys.inp") as fi, open(d / "talys.out", "w") as fo:
            subprocess.run(["flock", LOCK, "nice", "-n", "10", TALYS], stdin=fi, stdout=fo, cwd=d, check=True)
        res: dict = {"E": None}
        for ch, (fn, _) in CHANNELS.items():
            p = d / fn
            if not p.is_file():
                continue
            r = _rows(p)
            if res["E"] is None:
                res["E"] = [x[0] for x in r]
            res[ch] = [x[1] for x in r]
        for fn in extra_files:  # caller-named files, raw rows
            if (d / fn).is_file():
                res["file:" + fn] = _rows(d / fn)
        tail = (d / "talys.out").read_text(errors="replace")
        res["warnings"] = [ln.strip() for ln in tail.splitlines() if "TALYS-warning" in ln or "TALYS-error" in ln][:20]
    finally:
        shutil.rmtree(d, ignore_errors=True)
    if not extra_files:
        f.write_text(json.dumps(res))
    return res


def engine(target: str, kw: str, energies=ENERGIES, env_extra: dict | None = None) -> dict:
    """{channel: [mb per energy]} of the engine with deck lines `kw` (fresh process, cached)."""
    f = _tag(target, kw + (json.dumps(env_extra, sort_keys=True) if env_extra else ""), "engine", energies)
    if f.is_file():
        return json.loads(f.read_text())
    _, z, a = TARGETS[target]
    env = {k: v for k, v in os.environ.items() if not k.startswith(("INCOGNITA_", "NUCLIDO_"))}
    if kw.strip():
        env["INCOGNITA_TALYS_FIT_LINES"] = kw
    env.update(env_extra or {})
    env.setdefault("OMP_NUM_THREADS", "1")
    env.setdefault("INCOGNITA_CHANOBS", "1")  # output only (B1): the isomeric channels under TALYS names
    p = subprocess.run(["flock", LOCK, "nice", "-n", "10", sys.executable, __file__, "_engine_child", str(z), str(a),
                        ",".join(map(str, energies))], env=env, cwd=ROOT, capture_output=True, text=True)
    line = [x for x in p.stdout.splitlines() if x.startswith("{")]
    if p.returncode != 0 or not line:
        return {"error": (p.stderr or p.stdout)[-1500:]}
    res = json.loads(line[-1])
    f.write_text(json.dumps(res))
    return res


def _engine_child(z: int, a: int, energies: str) -> None:
    sys.path.insert(0, str(ROOT))
    import time

    import numpy as np
    import torch

    from physics.hf import engine_c, warmrun
    from physics.hf.engine import ChainedFull

    t0 = time.time()
    es = tuple(float(x) for x in energies.split(","))
    with torch.inference_mode():
        r = engine_c.run(ChainedFull(Z=z, A=a, declared_energies=es), {})
    arr = warmrun.result_arrays(r)
    out = {"E": [float(x) for x in arr["e_inc_mev"]], "wall_s": round(time.time() - t0, 1)}
    for ch, (_, key) in CHANNELS.items():
        if key in arr:
            out[ch] = [float(x) for x in np.asarray(arr[key]).ravel()]
    print(json.dumps(out))


def response(target: str, kw: str, energies=ENERGIES, floor_mb: float = 1.0, env_extra=None) -> dict:
    """Per channel and energy: R, S and |ln(R/S)|; plus the worst over cells where stock > floor."""
    s0, s1 = stock(target, "", energies), stock(target, kw, energies)
    e0, e1 = engine(target, "", energies), engine(target, kw, energies, env_extra)
    if "error" in e1 or "error" in e0:
        return {"error": e1.get("error") or e0.get("error")}
    rows, worst = [], 0.0
    for ch in CHANNELS:
        if ch not in s0 or ch not in s1 or ch not in e0 or ch not in e1:
            continue
        for i, e in enumerate(s0["E"]):
            if i >= len(e0[ch]) or i >= len(s1[ch]):
                continue
            a0, a1, b0, b1 = e0[ch][i], e1[ch][i], s0[ch][i], s1[ch][i]
            if min(b0, b1) <= floor_mb or a0 <= 0 or a1 <= 0:
                continue
            R, S = a1 / a0, b1 / b0
            d = abs(math.log(R / S))
            rows.append(dict(ch=ch, E=e, R=R, S=S, dlog=d))
            worst = max(worst, d)
    moved = max((abs(math.log(r["S"])) for r in rows), default=0.0)
    return {"target": target, "kw": kw, "rows": rows, "worst_dlog": worst, "stock_moved": moved,
            "stock_warnings": s1.get("warnings", [])}


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "_engine_child":
        _engine_child(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
        return
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default="fe56")
    ap.add_argument("--kw", action="append", required=True, help="';'-separated deck lines (repeatable)")
    ap.add_argument("--energies", default=",".join(map(str, ENERGIES)))
    ap.add_argument("--json")
    a = ap.parse_args()
    CACHE.mkdir(parents=True, exist_ok=True)
    es = tuple(float(x) for x in a.energies.split(","))
    allr = []
    for kw in a.kw:
        r = response(a.target, kw, es)
        allr.append(r)
        if "error" in r:
            print(f"{a.target} [{kw}] ERROR {r['error'][-600:]}")
            continue
        print(f"{a.target} [{kw}] worst |ln(R/S)| = {100 * r['worst_dlog']:.2f} %  (stock moved up to "
              f"{100 * r['stock_moved']:.1f} %)  {'PASS' if r['worst_dlog'] <= 0.02 else 'FAIL'}")
        for x in sorted(r["rows"], key=lambda x: -x["dlog"])[:6]:
            print(f"    {x['ch']:<10} E={x['E']:<6g} R={x['R']:.4f} S={x['S']:.4f} d={100 * x['dlog']:.2f} %")
        for w in r["stock_warnings"][:3]:
            print("    stock:", w)
    if a.json:
        Path(a.json).write_text(json.dumps(allr, indent=1))


if __name__ == "__main__":
    main()
