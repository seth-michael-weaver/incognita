#!/usr/bin/env python3
"""GAP isomeric targets (`ltarget`): engine vs stock TALYS-2.25, in TALYS mode (docs/hf/ISOMERIC_TARGETS.md).

    PY=~/fastgate_data/eng/16606b356d6e/.venv/bin/python   # WSL; the engine venv has torch
    bash scripts/kwcov/biso_stock.sh                         # stock runs, trimmed, in ~/kwcov/stock/biso/<case>
    $PY scripts/kwcov/biso_compare.py --case fe56_l1 [--case am242_m ...] [--mode talys] [--json out.json]

The engine side is `engine_c.run(ChainedFull(Z, A, declared_energies))` in a fresh process under `nice -n 10` and
`flock /tmp/incognita_heavy.lock`, with the case's deck lines (plus, in TALYS mode, fidelity.TALYS_DECK / TALYS_ENV)
in INCOGNITA_TALYS_FIT_LINES and INCOGNITA_CHANOBS=1 (output only). Engine results are cached in ~/kwcov/biso_eng
by (case, mode, deck, energies, HEAD); `--fresh` reruns.

Metric: per channel and energy where stock > `--floor` mb, ours/stock - 1. "main" channels: total, elastic,
nonelastic, capture, inelastic, (n,2n), (n,p), (n,a), fission; plus every discrete inelastic `nn.Lnn`.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fidelity as F  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
STOCK = Path(os.path.expanduser("~/kwcov/stock/biso"))
CACHE = Path(os.path.expanduser("~/kwcov/biso_eng"))
LOCK = "/tmp/incognita_heavy.lock"

#: case -> (Z, A, deck lines); the stock deck of the same name is in biso_stock.sh
CASES = {
    "fe56_gs": (26, 56, []), "fe56_l1": (26, 56, ["ltarget 1"]), "fe56_l2": (26, 56, ["ltarget 2"]),
    "am242_gs": (95, 242, []), "am242_m": (95, 242, ["ltarget 2"]),
}
MAIN = {"total": ("total.tot", "totals_mb/total"), "elastic": ("elastic.tot", "totals_mb/elastic"),
        "nonelastic": ("nonelastic.tot", "totals_mb/nonelastic"), "capture": ("xs000000.tot", "channels_mb/xs000000"),
        "inelastic": ("xs100000.tot", "channels_mb/xs100000"), "n2n": ("xs200000.tot", "channels_mb/xs200000"),
        "np": ("xs010000.tot", "channels_mb/xs010000"), "na": ("xs000001.tot", "channels_mb/xs000001"),
        "fission": ("fission.tot", "totals_mb/fission")}


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


def stock(case: str) -> dict:
    d = STOCK / case
    if not (d / "DONE").is_file():
        raise SystemExit(f"no stock run {d}: run scripts/kwcov/biso_stock.sh")
    out: dict = {}
    for ch, (fn, _) in MAIN.items():
        if (d / fn).is_file():
            r = _rows(d / fn)
            out["E"] = [x[0] for x in r]
            out[ch] = [x[1] for x in r]
    for p in sorted(d.glob("nn.L[0-9][0-9]")):
        out[p.name] = [x[1] for x in _rows(p)]
    out["errors"] = (d / "errors.txt").read_text(errors="replace").strip()
    return out


def _head() -> str:
    """The engine source's identity: size and mtime of every physics/**/*.py (git does not work on a Windows worktree
    from WSL, so a commit hash would be empty there and a stale result would be reused)."""
    h = hashlib.sha1()
    for p in sorted((ROOT / "physics").rglob("*.py")):
        st = p.stat()
        h.update(f"{p.relative_to(ROOT)}|{st.st_size}|{st.st_mtime_ns}".encode())
    return h.hexdigest()[:12]


def engine(case: str, mode: str, energies, fresh: bool = False) -> dict:
    z, a, lines = CASES[case]
    kw, env_m = F.mode_args(mode)
    kw = ";".join(x for x in (";".join(lines), kw) if x)
    tag = hashlib.sha1(f"{case}|{mode}|{kw}|{energies}|{_head()}".encode()).hexdigest()[:12]
    f = CACHE / f"{case}_{mode}_{tag}.json"
    if f.is_file() and not fresh:
        return json.loads(f.read_text())
    CACHE.mkdir(parents=True, exist_ok=True)
    env = {k: v for k, v in os.environ.items() if not k.startswith(("INCOGNITA_", "NUCLIDO_"))}
    if kw:
        env["INCOGNITA_TALYS_FIT_LINES"] = kw
    env.update(env_m)
    env.setdefault("OMP_NUM_THREADS", "1")
    env["INCOGNITA_CHANOBS"] = "1"
    p = subprocess.run(["flock", LOCK, "nice", "-n", "10", sys.executable, __file__, "_child", str(z), str(a),
                        ",".join(map(str, energies))], env=env, cwd=ROOT, capture_output=True, text=True)
    line = [x for x in p.stdout.splitlines() if x.startswith("{")]
    if p.returncode != 0 or not line:
        return {"error": (p.stderr or p.stdout)[-2500:]}
    res = json.loads(line[-1])
    f.write_text(json.dumps(res))
    return res


def _child(z: int, a: int, energies: str) -> None:
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
    for ch, (_, key) in MAIN.items():
        if key in arr:
            out[ch] = [float(x) for x in np.asarray(arr[key]).ravel()]
    for k, v in arr.items():
        if k.startswith("levels_mb/nn.L"):
            out[k.split("/", 1)[1]] = [float(x) for x in np.asarray(v).ravel()]
    print(json.dumps(out))


def compare(case: str, mode: str, energies, floor: float, fresh: bool) -> dict:
    s, e = stock(case), engine(case, mode, energies, fresh)
    if "error" in e:
        return {"case": case, "mode": mode, "error": e["error"]}
    rows, worst_main, worst_lev = [], (0.0, ""), (0.0, "")
    for ch in list(MAIN) + sorted(k for k in s if k.startswith("nn.L")):
        if ch not in s:
            continue
        for i, en in enumerate(s["E"]):
            b = s[ch][i] if i < len(s[ch]) else 0.0
            v = e.get(ch, [0.0] * len(s["E"]))
            a = v[i] if i < len(v) else 0.0
            if b <= floor:
                continue
            d = a / b - 1.0
            rows.append({"ch": ch, "E": en, "ours": a, "stock": b, "rel": d})
            w = worst_main if ch in MAIN else worst_lev
            if abs(d) > w[0]:
                w = (abs(d), f"{ch} {en:g} MeV")
            if ch in MAIN:
                worst_main = w
            else:
                worst_lev = w
    return {"case": case, "mode": mode, "rows": rows, "worst_main": worst_main, "worst_levels": worst_lev,
            "wall_s": e.get("wall_s"), "stock_errors": s["errors"]}


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "_child":
        _child(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
        return
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", action="append", required=True)
    ap.add_argument("--mode", default="talys")
    ap.add_argument("--energies", default="1,5,14")
    ap.add_argument("--floor", type=float, default=1.0)
    ap.add_argument("--fresh", action="store_true")
    ap.add_argument("--json")
    a = ap.parse_args()
    es = tuple(float(x) for x in a.energies.split(","))
    allr = []
    for c in a.case:
        r = compare(c, a.mode, es, a.floor, a.fresh)
        allr.append(r)
        if "error" in r:
            print(f"{c} [{a.mode}]: ERROR\n{r['error']}")
            continue
        print(f"{c} [{a.mode}] wall {r['wall_s']} s; worst main {100 * r['worst_main'][0]:.2f} % ({r['worst_main'][1]}),"
              f" worst level {100 * r['worst_levels'][0]:.2f} % ({r['worst_levels'][1]})")
        for x in r["rows"]:
            print(f"  {x['ch']:<11} {x['E']:6g} ours {x['ours']:11.4f} stock {x['stock']:11.4f} {100 * x['rel']:+7.2f} %")
    if a.json:
        Path(a.json).write_text(json.dumps(allr, indent=1))


if __name__ == "__main__":
    main()
