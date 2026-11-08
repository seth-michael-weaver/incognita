#!/usr/bin/env python3
"""KWCOV B7b: alpha-projectile response of `alphaomp 3|4|5` vs stock TALYS-2.25 (R = ours(kw)/ours(base),
S = stock(kw)/stock(base), worst |ln(R/S)| over the channels > 1 mb).

    PY=~/fastgate_data/eng/16606b356d6e/.venv/bin/python   # WSL
    $PY scripts/kwcov/b7b_alpha.py --target fe56 --energies 10,15,20 --kw "alphaomp 3" --kw "alphaomp 4" [--mode talys]

Stock: alpha + target with `channels y; filechannels y`, trimmed to the channel totals (JSON in ~/kwcov/stock/b7b);
engine: input.deck.run_deck in a fresh process with INCOGNITA_CPINC=a (JSON in ~/kwcov/b7b_eng). Both under
`flock /tmp/incognita_heavy.lock` and `nice -n 10`.
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

sys.path.insert(0, str(Path(__file__).resolve().parent))
import b2_response as B  # noqa: E402
import fidelity as F  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
STOCK = Path(os.path.expanduser("~/kwcov/stock/b7b"))
ENG = Path(os.path.expanduser("~/kwcov/b7b_eng"))
TARGETS = {"fe56": ("fe", 56), "pb208": ("pb", 208), "ni58": ("ni", 58)}
FILES = {"nonelastic": "nonelastic.tot", "an": "xs100000.tot", "ap": "xs010000.tot", "ag": "xs000000.tot",
         "a2n": "xs200000.tot", "anp": "xs110000.tot", "aa": "xs000001.tot", "inelastic": "xs000001.tot"}
KEYS = {"nonelastic": "totals_mb/nonelastic", "an": "channels_mb/xs100000", "ap": "channels_mb/xs010000",
        "ag": "channels_mb/xs000000", "a2n": "channels_mb/xs200000", "anp": "channels_mb/xs110000",
        "aa": "channels_mb/xs000001"}


def _deck(target: str, kw: str, energies) -> str:
    el, a = TARGETS[target]
    lines = ["projectile a", f"element {el}", f"mass {a}", "energy energies", "channels y", "filechannels y"]
    lines += [x.strip() for x in kw.split(";") if x.strip()]
    return "\n".join(lines) + "\n"


def _tag(side: str, target: str, kw: str, energies, env=None) -> Path:
    h = hashlib.sha1(f"{_deck(target, kw, energies)}|{energies}|{json.dumps(env or {}, sort_keys=True)}".encode())
    return (STOCK if side == "stock" else ENG) / f"alpha_{side}_{target}_{h.hexdigest()[:12]}.json"


def stock(target: str, kw: str, energies) -> dict:
    f = _tag("stock", target, kw, energies)
    if f.is_file():
        return json.loads(f.read_text())
    STOCK.mkdir(parents=True, exist_ok=True)
    d = Path(tempfile.mkdtemp(prefix="b7ba_", dir=str(STOCK)))
    try:
        (d / "energies").write_text("".join(f"{e}\n" for e in energies))
        (d / "talys.inp").write_text(_deck(target, kw, energies))
        with open(d / "talys.inp") as fi, open(d / "talys.out", "w") as fo:
            subprocess.run(["flock", B.LOCK, "nice", "-n", "10", B.TALYS], stdin=fi, stdout=fo, cwd=d, check=True)
        res: dict = {}
        for ch, fn in FILES.items():
            if (d / fn).is_file():
                rows = B._rows(d / fn)
                res["E"] = [x[0] for x in rows]
                res[ch] = [x[1] for x in rows]
    finally:
        shutil.rmtree(d, ignore_errors=True)
    f.write_text(json.dumps(res))
    return res


def engine(target: str, kw: str, energies, env_extra=None) -> dict:
    f = _tag("engine", target, kw, energies, env_extra)
    if f.is_file():
        return json.loads(f.read_text())
    ENG.mkdir(parents=True, exist_ok=True)
    env = {k: v for k, v in os.environ.items() if not k.startswith(("INCOGNITA_", "NUCLIDO_"))}
    env.update(env_extra or {})
    env["INCOGNITA_CPINC"] = "a"
    env.setdefault("OMP_NUM_THREADS", "1")
    d = Path(tempfile.mkdtemp(prefix="b7baeng_"))
    try:
        (d / "energies").write_text("".join(f"{e}\n" for e in energies))
        (d / "talys.inp").write_text(_deck(target, kw, energies))
        p = subprocess.run(["flock", B.LOCK, "nice", "-n", "10", sys.executable, __file__, "_child", str(d / "talys.inp")],
                           env=env, cwd=ROOT, capture_output=True, text=True)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    line = [x for x in p.stdout.splitlines() if x.startswith("{")]
    if p.returncode != 0 or not line:
        return {"error": (p.stderr or p.stdout)[-1500:]}
    f.write_text(line[-1])
    return json.loads(line[-1])


def _child(deck: str) -> None:
    sys.path.insert(0, str(ROOT))
    import numpy as np
    import torch

    from physics.hf import warmrun
    from physics.hf.input.deck import run_deck

    with torch.inference_mode():
        r = run_deck(deck)
    arr = warmrun.result_arrays(r)
    out = {"E": [float(x) for x in arr["e_inc_mev"]]}
    for ch, key in KEYS.items():
        if key in arr:
            out[ch] = [float(x) for x in np.asarray(arr[key]).ravel()]
    print(json.dumps(out))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default="fe56")
    ap.add_argument("--energies", default="10,15,20")
    ap.add_argument("--mode", default="talys")
    ap.add_argument("--base", default="")
    ap.add_argument("--kw", action="append", default=[])
    a = ap.parse_args()
    es = tuple(float(x) for x in a.energies.split(","))
    for m in a.mode.split(","):
        mdeck, menv = F.mode_args(m)
        for kw in a.kw:
            k0 = ";".join(x for x in (a.base, mdeck) if x)
            k1 = ";".join(x for x in (a.base, kw, mdeck) if x)
            s0, s1 = stock(a.target, a.base, es), stock(a.target, ";".join(x for x in (a.base, kw) if x), es)
            e0, e1 = engine(a.target, k0, es, menv), engine(a.target, k1, es, menv)
            if "error" in e0 or "error" in e1:
                print(f"ALPHA {a.target} [{kw}] {m}: ERROR {(e1.get('error') or e0.get('error'))[-600:]}")
                continue
            worst, moved = (0.0, ""), 0.0
            for ch in KEYS:
                if not all(ch in x for x in (s0, s1, e0, e1)):
                    continue
                for i, e in enumerate(s0["E"]):
                    b0, b1, x0, x1 = s0[ch][i], s1[ch][i], e0[ch][i], e1[ch][i]
                    if min(b0, b1) <= 1.0 or x0 <= 0 or x1 <= 0:
                        continue
                    moved = max(moved, abs(math.log(b1 / b0)))
                    dd = abs(math.log((x1 / x0) / (b1 / b0)))
                    print(f"   {ch:10s} {e:5g} stock {b0:9.2f}->{b1:9.2f} ours {x0:9.2f}->{x1:9.2f} d {100 * dd:.2f} %")
                    if dd > worst[0]:
                        worst = (dd, f"{ch} {e:g} MeV")
            print(f"ALPHA {a.target} [{a.base} | {kw}] {m}: {100 * worst[0]:.2f} % ({worst[1]}; stock moved "
                  f"{100 * moved:.1f} %)", flush=True)


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "_child":
        _child(sys.argv[2])
    else:
        main()
