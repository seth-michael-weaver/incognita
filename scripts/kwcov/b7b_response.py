#!/usr/bin/env python3
"""KWCOV B7b: response of the JLM / folding-alpha keywords vs stock TALYS-2.25 (b2_response's metric through fidelity.py).

    PY=~/fastgate_data/eng/16606b356d6e/.venv/bin/python   # WSL
    $PY scripts/kwcov/b7b_response.py --target fe56 --response "jlmomp y" [--mode default,talys]

Stock runs are cached (trimmed: channel totals only) in ~/kwcov/stock/b7b, engine runs in ~/kwcov/b7b_eng (delete that
directory after a code change: the engine cache key is the deck, not the commit).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import b2_response as B  # noqa: E402
import fidelity as F  # noqa: E402

B.TARGETS.setdefault("pb208", ("pb", 82, 208))
F.STOCK_CACHE = Path(os.path.expanduser("~/kwcov/stock/b7b"))
F.ENGINE_CACHE = Path(os.path.expanduser("~/kwcov/b7b_eng"))
B.CACHE = F.STOCK_CACHE

def response(target: str, kw: str, modes, energies, base: str = "", floor_mb: float = 1.0) -> dict:
    """fidelity.response with `base` deck lines on both sides: R = ours(base + kw) / ours(base), S likewise for stock.
    Returns {mode: (worst |ln(R/S)|, where, largest |ln S| = how much stock moved)}."""
    import math

    r0 = F.run(target, modes, energies, base)
    r1 = F.run(target, modes, energies, ";".join(x for x in (base, kw) if x))
    s0, s1 = r0["stock"], r1["stock"]
    out = {}
    for m in modes:
        e0, e1 = r0[m], r1[m]
        if "error" in e0 or "error" in e1:
            out[m] = ("error", (e1.get("error") or e0.get("error"))[-300:], 0.0)
            continue
        worst, moved = (0.0, ""), 0.0
        for ch in B.CHANNELS:
            if not all(ch in x for x in (s0, s1, e0, e1)):
                continue
            for i, e in enumerate(s0["E"]):
                a0, a1, b0, b1 = e0[ch][i], e1[ch][i], s0[ch][i], s1[ch][i]
                if min(b0, b1) <= floor_mb or a0 <= 0 or a1 <= 0:
                    continue
                moved = max(moved, abs(math.log(b1 / b0)))
                d = abs(math.log((a1 / a0) / (b1 / b0)))
                if d > worst[0]:
                    worst = (d, f"{ch} {e:g} MeV")
        out[m] = (*worst, moved)
    return out


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default="fe56")
    ap.add_argument("--mode", default="default,talys")
    ap.add_argument("--energies", default="1,5,14")
    ap.add_argument("--base", default="")
    ap.add_argument("--response", action="append", default=[])
    a = ap.parse_args()
    es = tuple(float(x) for x in a.energies.split(","))
    modes = a.mode.split(",")
    for kw in a.response:
        res = response(a.target, kw, modes, es, a.base)
        print(f"RESPONSE {a.target} [{a.base} | {kw}] " + "  ".join(
            f"{m}: " + (f"{100 * v[0]:.2f} % ({v[1]}; stock moved {100 * v[2]:.1f} %)" if v[0] != "error"
                        else "ERROR " + v[1]) for m, v in res.items()), flush=True)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "_engine_child":
        B._engine_child(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
    else:
        F.STOCK_CACHE.mkdir(parents=True, exist_ok=True)
        F.ENGINE_CACHE.mkdir(parents=True, exist_ok=True)
        main()
