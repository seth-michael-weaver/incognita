#!/usr/bin/env python3
"""FIDELITY1: engine vs stock TALYS-2.25 on DEFAULT decks, with INCOGNITA's deliberate defaults ON and switched to TALYS.

    PY=~/fastgate_data/eng/16606b356d6e/.venv/bin/python   # WSL; the engine venv has torch
    $PY scripts/kwcov/fidelity.py --target fe56 [--mode default,talys,talys+fix] [--json out.json]

Modes (deck lines go through INCOGNITA_TALYS_FIT_LINES like every kwcov run; env on top of a clean environment):
  default      the engine as the kwcov batches ran it (no switch, no deck line)
  talys        every deliberate INCOGNITA default that is ON switched to its TALYS value (TALYS_DECK + TALYS_ENV)
  talys+fix    `talys` plus the FIDELITY1 opt-in fixes (FIX_ENV); `default+fix` = default plus the fixes
Stock runs and engine runs are cached by b2_response (stock in ~/kwcov/b2, engine in ~/kwcov/fid).
docs/hf/FIDELITY_DEFAULTS.md records the results.
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

B.TARGETS.setdefault("au197", ("au", 79, 197))
B.TARGETS.setdefault("th232", ("th", 90, 232))
B.TARGETS.setdefault("u235", ("u", 92, 235))

#: deck keywords of INCOGNITA extensions whose default is ON (input/defaults.py, "Incognita extension ... not TALYS"),
#: each at its TALYS value. (ctwcont acts only under ctwindow2, alphaentr only for an alpha projectile: listed anyway.)
TALYS_DECK = ["fluxclose n", "npwindow n", "chancap n", "nnleak n", "exactfis n", "alphatemp 0", "sfexit n",
              "kevleak2 n", "heavymacs2 n", "ftglobal n", "ccexitnbnf n", "tfold n", "ctwcont n", "alphaentr 0"]
#: env switches of INCOGNITA extensions whose default is ON, at their TALYS value
TALYS_ENV = {"INCOGNITA_GRIDTOP": "n", "INCOGNITA_SPECCLOSE": "0", "INCOGNITA_LOWEPOT": "0",
             "INCOGNITA_TARMASSFIX": "0", "INCOGNITA_ISOROTPASS": "0"}
STOCK_CACHE = B.CACHE
ENGINE_CACHE = Path(os.path.expanduser("~/kwcov/fid"))
#: FIDELITY1 port fixes. ON by default in the engine since the KWCOV integration (INCOGNITA_FIDFIX=0 opts out), so
#: `default` = `default+fix` for engine runs made after it; engine runs cached in ENGINE_CACHE before the flip are the
#: pre-fix default. Named in full, so a cached `+fix` run never predates a fix.
FIX_ENV: dict = {"INCOGNITA_FIDFIX": "ldcn,besttables,fitrisomer,psfsgl"}


def mode_args(mode: str) -> tuple[str, dict]:
    deck, env = [], {}
    parts = mode.split("+")
    if parts[0] == "talys":
        deck += TALYS_DECK
        env.update(TALYS_ENV)
    for p in parts[1:]:
        if p == "fix":
            env.update(FIX_ENV)
        elif "=" in p:  # ad hoc: KEY=VAL (env) or deck:<line>
            k, v = p.split("=", 1)
            env[k] = v
        elif p.startswith("deck:"):
            deck.append(p[5:].replace("_", " "))
    return ";".join(deck), env


def run(target: str, modes, energies, base: str = "", files=()) -> dict:
    """`base`: ';'-separated deck lines on both sides (e.g. `best y`), before each mode's lines. `files`: input files
    the base names by full path; the engine reads that path, stock gets the file copied into its run directory and the
    deck names it by its basename (b6_response's stock runner, cached in ~/kwcov/b6)."""
    B.CACHE = STOCK_CACHE
    if files:
        import hashlib

        import b6_response as B6R

        sl = base
        for f in files:
            sl = sl.replace(f, os.path.basename(f))
        sl = "\n".join(x.strip() for x in sl.split(";") if x.strip())
        name = "fid_" + hashlib.sha1(f"{target}|{sl}|{energies}".encode()).hexdigest()[:12]
        out = {"target": target, "stock": B6R.stock(name, target, sl, [Path(f) for f in files], energies)}
    else:
        out = {"target": target, "stock": B.stock(target, base, energies)}
    B.CACHE = ENGINE_CACHE  # never the b2 engine cache: that engine is an older commit
    B.CACHE.mkdir(parents=True, exist_ok=True)
    for m in modes:
        kw, env = mode_args(m)
        kw = ";".join(x for x in (base, kw) if x)
        out[m] = B.engine(target, kw, energies, env or None)
    return out


def table(r: dict, modes, floor_mb=1.0) -> str:
    s = r["stock"]
    rows = []
    for ch in B.CHANNELS:
        if ch not in s:
            continue
        for i, e in enumerate(s["E"]):
            if s[ch][i] <= floor_mb:
                continue
            cells = []
            for m in modes:
                v = r[m].get(ch)
                if "error" in r[m] or v is None or i >= len(v):
                    cells.append("   n/a")
                    continue
                cells.append(f"{v[i]:9.2f} {100 * (v[i] / s[ch][i] - 1):+6.2f}%")
            rows.append(f"{ch:<10} {e:6g} {s[ch][i]:9.2f}  " + "  ".join(cells))
    return f"{r['target']}: channel E stock  " + "  ".join(modes) + "\n" + "\n".join(rows)


def response(target: str, kw: str, modes, energies, floor_mb: float = 1.0) -> dict:
    """b2_response's metric per mode: worst |ln(R/S)|, R = engine(mode + kw) / engine(mode), S = stock(kw) / stock()."""
    r0, r1 = run(target, modes, energies), run(target, modes, energies, kw)
    s0, s1 = r0["stock"], r1["stock"]
    out = {}
    for m in modes:
        e0, e1 = r0[m], r1[m]
        if "error" in e0 or "error" in e1:
            out[m] = ("error", (e1.get("error") or e0.get("error"))[-300:])
            continue
        worst = (0.0, "")
        for ch in B.CHANNELS:
            if not all(ch in x for x in (s0, s1, e0, e1)):
                continue
            for i, e in enumerate(s0["E"]):
                a0, a1, b0, b1 = e0[ch][i], e1[ch][i], s0[ch][i], s1[ch][i]
                if min(b0, b1) <= floor_mb or a0 <= 0 or a1 <= 0:
                    continue
                d = abs(math.log((a1 / a0) / (b1 / b0)))
                if d > worst[0]:
                    worst = (d, f"{ch} {e:g} MeV")
        out[m] = worst
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default="fe56")
    ap.add_argument("--mode", default="default,talys")
    ap.add_argument("--energies", default="1,5,14")
    ap.add_argument("--base", default="", help="deck lines on both sides, ';'-separated")
    ap.add_argument("--files", default="", help="comma list of input files the base names by full path")
    ap.add_argument("--response", action="append", default=[], help="deck lines: print the response metric per mode")
    ap.add_argument("--json")
    a = ap.parse_args()
    B.CACHE.mkdir(parents=True, exist_ok=True)
    es = tuple(float(x) for x in a.energies.split(","))
    modes = a.mode.split(",")
    if a.response:
        for kw in a.response:
            res = response(a.target, kw, modes, es)
            print(f"RESPONSE {a.target} [{kw}] " + "  ".join(
                f"{m}: " + (f"{100 * v[0]:.2f} % ({v[1]})" if v[0] != "error" else "ERROR " + v[1]) for m, v in res.items()))
        return
    r = run(a.target, modes, es, a.base, tuple(x for x in a.files.split(",") if x))
    for m in modes:
        if "error" in r[m]:
            print(m, "ERROR", r[m]["error"][-800:])
    print(table(r, modes))
    if a.json:
        Path(a.json).write_text(json.dumps(r, indent=1))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "_engine_child":
        B._engine_child(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
    else:
        main()
