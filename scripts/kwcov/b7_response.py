#!/usr/bin/env python3
"""KWCOV B7 acceptance: response of the engine to the pre-equilibrium / gamma model branches B7 ports, vs stock.

    PY=~/fastgate_data/eng/16606b356d6e/.venv/bin/python   # WSL; the engine venv has torch
    $PY scripts/kwcov/b7_response.py --target fe56 --kw "twocomponent n" [--kw ...]
    $PY scripts/kwcov/b7_response.py --stock-only --target zr90 --kw "gshell y"

Same method as b2_response.py / b5_response.py (R = ours(kw)/ours(default), S = stock(kw)/stock(default),
|ln(R/S)| <= 2 % where stock > 1 mb) on the plan's B7 decks (Fe-56 and Zr-90, n at 1/5/14 MeV), plus the particle
production cross sections the plan names for B7 (nprod, pprod, aprod: B1's CHANOBS names, output only). Every row
also carries the millibarns each side moved (ours(kw) - ours(default) vs stock(kw) - stock(default)), the comparison
B5 used where the engine's default (n,p)/(n,a) excess at 14 MeV scales a relative response. Cache:
~/kwcov/stock/b7 (JSON only; TALYS scratch is deleted after every run).
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import b2_response as B  # noqa: E402

B.CACHE = Path(os.path.expanduser("~/kwcov/stock/b7"))
B.__file__ = __file__  # the engine child runs this script, so it reports the production channels too
B.TARGETS.update({"au197": ("au", 79, 197), "pb208": ("pb", 82, 208)})
B.CHANNELS.update({
    "nprod": ("nprod.tot", "extras/nprod.tot"), "pprod": ("pprod.tot", "extras/pprod.tot"),
    "aprod": ("aprod.tot", "extras/aprod.tot"),
})


def report(target: str, kw: str, energies, stock_only: bool = False) -> dict:
    if stock_only:
        s0, s1 = B.stock(target, "", energies), B.stock(target, kw, energies)
        moved = []
        for ch in B.CHANNELS:
            if ch in s0 and ch in s1:
                for i, e in enumerate(s0["E"]):
                    b0, b1 = s0[ch][i], s1[ch][i]
                    if min(b0, b1) > 1.0:
                        moved.append((abs(math.log(b1 / b0)), ch, e, b0, b1))
        moved.sort(reverse=True)
        print(f"{target} [{kw}] stock only; warnings: {s1.get('warnings', [])[:3]}")
        for d, ch, e, b0, b1 in moved[:8]:
            print(f"    {ch:<10} E={e:<6g} {b0:10.3f} -> {b1:10.3f} mb ({100 * d:.2f} %)")
        return {"moved": moved}
    r = B.response(target, kw, energies)
    if "error" in r:
        print(f"{target} [{kw}] ERROR {r['error'][-900:]}")
        return r
    e0, e1 = B.engine(target, "", energies), B.engine(target, kw, energies)
    s0, s1 = B.stock(target, "", energies), B.stock(target, kw, energies)
    idx = {e: i for i, e in enumerate(s0["E"])}
    for x in r["rows"]:
        i = idx[x["E"]]
        x["dmb_ours"] = e1[x["ch"]][i] - e0[x["ch"]][i]
        x["dmb_stock"] = s1[x["ch"]][i] - s0[x["ch"]][i]
    print(f"{target} [{kw}] worst |ln(R/S)| = {100 * r['worst_dlog']:.2f} %  (stock moved up to "
          f"{100 * r['stock_moved']:.1f} %)  {'PASS' if r['worst_dlog'] <= 0.02 else 'FAIL'}")
    for x in sorted(r["rows"], key=lambda x: -x["dlog"])[:8]:
        print(f"    {x['ch']:<10} E={x['E']:<6g} R={x['R']:.4f} S={x['S']:.4f} d={100 * x['dlog']:.2f} %   "
              f"moved ours {x['dmb_ours']:+.2f} mb, stock {x['dmb_stock']:+.2f} mb")
    for w in r["stock_warnings"][:3]:
        print("    stock:", w)
    return r


PARTICLES = ("gamma", "neutron", "proton", "deuteron", "triton", "helium-3", "alpha")


def pe_stock(target: str, kw: str, energies) -> dict:
    """{E: [Total of preeqEEEE.EEE.out per particle g n p d t h a]} of a stock `outpreequilibrium y` run (cached)."""
    import shutil
    import subprocess
    import tempfile

    f = B._tag(target, "PE|" + kw, "stock", energies)
    if f.is_file():
        return {float(k): v for k, v in json.loads(f.read_text()).items()}
    el, _, a = B.TARGETS[target]
    d = Path(tempfile.mkdtemp(prefix=f"b7pe_{target}_", dir=str(B.CACHE)))
    out = {}
    try:
        (d / "energies").write_text("".join(f"{e}\n" for e in energies))
        deck = ["projectile n", f"element {el}", f"mass {a}", "energy energies", "outpreequilibrium y"] + B._lines(kw)
        (d / "talys.inp").write_text("\n".join(deck) + "\n")
        with open(d / "talys.inp") as fi, open(d / "talys.out", "w") as fo:
            subprocess.run(["flock", B.LOCK, "nice", "-n", "10", B.TALYS], stdin=fi, stdout=fo, cwd=d, check=True)
        for e in energies:
            p = d / f"preeq{e:08.3f}.out"
            if not p.is_file():
                continue
            rows = {}
            for ln in p.read_text().splitlines():
                w = ln.split()
                if len(w) > 2 and w[0] in PARTICLES and w[0] not in rows:
                    rows[w[0]] = float(w[1])
            out[e] = [rows.get(x, 0.0) for x in PARTICLES]
    finally:
        shutil.rmtree(d, ignore_errors=True)
    f.write_text(json.dumps(out))
    return out


def _pe_child(z: int, a: int, energies: str) -> None:
    sys.path.insert(0, str(B.ROOT))
    import torch

    from physics.hf.compound.pop_reference import _preeq
    from physics.hf.input import fitlib
    from physics.hf.preeq.chain import target_tag

    es = tuple(float(x) for x in energies.split(","))
    fitlib.activate(z, a)
    with torch.inference_mode():
        got, res, _ = _preeq(target_tag(z, a), declared=es)
    print(json.dumps({str(e): [float(x) for x in res["xspreeqtot"][i]] for i, e in enumerate(got)}))


def pe_engine(target: str, kw: str, energies) -> dict:
    import subprocess

    _, z, a = B.TARGETS[target]
    env = {k: v for k, v in os.environ.items() if not k.startswith(("INCOGNITA_", "NUCLIDO_"))}
    if kw.strip():
        env["INCOGNITA_TALYS_FIT_LINES"] = kw
    env.setdefault("OMP_NUM_THREADS", "1")
    p = subprocess.run(["flock", B.LOCK, "nice", "-n", "10", sys.executable, __file__, "_pe_child", str(z), str(a),
                        ",".join(map(str, energies))], env=env, cwd=B.ROOT, capture_output=True, text=True)
    line = [x for x in p.stdout.splitlines() if x.startswith("{")]
    if p.returncode != 0 or not line:
        raise RuntimeError((p.stderr or p.stdout)[-1500:])
    return {float(k): v for k, v in json.loads(line[-1]).items()}


def pe_report(target: str, kw: str, energies) -> None:
    """Binary pre-equilibrium totals (xspreeqtot per particle) of the engine vs stock's preeq*.out, with and without
    `kw`: the PE part of a keyword's response, free of the compound-nucleus default differences."""
    s0, s1 = pe_stock(target, "", energies), pe_stock(target, kw, energies)
    e0, e1 = pe_engine(target, "", energies), pe_engine(target, kw, energies)
    print(f"{target} [{kw}] binary pre-equilibrium totals [mb]: ours (default -> kw) | stock (default -> kw)")
    for e in energies:
        if e not in s1 or e not in e1:
            continue
        for i, x in enumerate(PARTICLES):
            if max(s1[e][i], s0[e][i], e1[e][i]) < 0.01:
                continue
            print(f"    E={e:<5g} {x:<9} {e0[e][i]:10.4f} -> {e1[e][i]:10.4f} | {s0[e][i]:10.4f} -> {s1[e][i]:10.4f}"
                  f"   kw ratio ours/stock {e1[e][i] / s1[e][i] if s1[e][i] else float('nan'):.4f}")


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "_engine_child":
        B._engine_child(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
        return
    if len(sys.argv) > 1 and sys.argv[1] == "_pe_child":
        _pe_child(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
        return
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default="fe56")
    ap.add_argument("--kw", action="append", required=True)
    ap.add_argument("--energies", default="1.0,5.0,14.0")
    ap.add_argument("--stock-only", action="store_true")
    ap.add_argument("--pe", action="store_true", help="binary pre-equilibrium totals vs stock preeq*.out")
    ap.add_argument("--json")
    a = ap.parse_args()
    B.CACHE.mkdir(parents=True, exist_ok=True)
    es = tuple(float(x) for x in a.energies.split(","))
    if a.pe:
        for kw in a.kw:
            pe_report(a.target, kw, es)
        return
    out = [report(a.target, kw, es, a.stock_only) for kw in a.kw]
    if a.json:
        Path(a.json).write_text(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
