#!/usr/bin/env python3
"""KWCOV B5 acceptance: response of the engine to compound / gamma / level / level-density deck keywords vs stock.

    PY=~/fastgate_data/eng/16606b356d6e/.venv/bin/python   # WSL; the engine venv has torch
    $PY scripts/kwcov/b5_response.py --target fe56 --kw "tjadjust 26 57 p 1.5" [--kw ...]

Same method as b2_response.py (R = ours(kw)/ours(default), S = stock(kw)/stock(default), |ln(R/S)| <= 2 % where
stock > 1 mb), with its cache in ~/kwcov/stock/b5 (JSON only; TALYS scratch is deleted after every run) and two
more standard decks: Au-197 (capture, racap at 1 keV - 1 MeV) and Zr-90.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import b2_response as B  # noqa: E402

B.CACHE = Path(os.path.expanduser("~/kwcov/stock/b5"))
B.TARGETS.update({"au197": ("au", 79, 197)})


def racap_stock(target: str, kw: str, energies) -> list[float]:
    """racap.tot `xs(dir. cap.)` of stock `racap y` + `optmodall y` (TALYS-2.25 gives 0 without it) + `kw`."""
    lines = "racap y;optmodall y" + (";" + kw if kw else "")
    r = B.stock(target, lines, energies, extra_files=("racap.tot",))
    return [row[1] for row in r.get("file:racap.tot", [])]


def racap_engine(target: str, kw: str, energies) -> list[float]:
    """`racapcalc.direct_capture_mb` (INCOGNITA_DIRECT_CAPTURE=all: the KD03 well stock builds under optmodall y)
    with deck lines `kw`, in a fresh process."""
    import json
    import subprocess

    _, z, a = B.TARGETS[target]
    env = {k: v for k, v in os.environ.items() if not k.startswith(("INCOGNITA_", "NUCLIDO_"))}
    env["INCOGNITA_DIRECT_CAPTURE"] = "all"
    if kw:
        env["INCOGNITA_TALYS_FIT_LINES"] = kw
    code = ("import sys,json; sys.path.insert(0, '.'); from physics.hf.direct.racapcalc import direct_capture_mb; "
            f"print(json.dumps([float(x) for x in direct_capture_mb({z}, {a}, {list(energies)!r})]))")
    p = subprocess.run(["flock", B.LOCK, "nice", "-n", "10", sys.executable, "-c", code], env=env, cwd=B.ROOT,
                       capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(p.stderr[-1500:])
    return json.loads(p.stdout.strip().splitlines()[-1])


def racap_response(target: str, kw: str, energies) -> list[tuple]:
    """(E, R, S, |ln(R/S)|) of the direct-capture cross section for deck lines `kw`."""
    import math

    s0, s1 = racap_stock(target, "", energies), racap_stock(target, kw, energies)
    e0, e1 = racap_engine(target, "", energies), racap_engine(target, kw, energies)
    out = []
    for e, a0, a1, b0, b1 in zip(energies, e0, e1, s0, s1):
        if min(a0, a1, b0, b1) > 0:
            R, S = a1 / a0, b1 / b0
            out.append((e, R, S, abs(math.log(R / S))))
    return out


if __name__ == "__main__":
    B.CACHE.mkdir(parents=True, exist_ok=True)
    if len(sys.argv) > 1 and sys.argv[1] == "_engine_child":
        B._engine_child(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
    elif len(sys.argv) > 1 and sys.argv[1] == "racap":  # racap <target> <E1,E2,..> <kw> [<kw> ...]
        es = tuple(float(x) for x in sys.argv[3].split(","))
        for kw in sys.argv[4:]:
            rows = racap_response(sys.argv[2], kw, es)
            w = max((r[3] for r in rows), default=0.0)
            print(f"{sys.argv[2]} racap [{kw}] worst {100 * w:.2f} %  " + "  ".join(
                f"E={e:g} R={R:.4f} S={S:.4f}" for e, R, S, _ in rows))
    else:
        B.main()
