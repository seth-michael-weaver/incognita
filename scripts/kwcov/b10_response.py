#!/usr/bin/env python3
"""KWCOV B10 acceptance: unresolved resonance range outputs (urr, lurr, urrnjoy, rprime) vs stock TALYS-2.25.

    PY=~/fastgate_data/eng/16606b356d6e/.venv/bin/python   # WSL; the engine venv has torch
    $PY scripts/kwcov/b10_response.py --target fe56 --base "urr y"                     # observables vs stock
    $PY scripts/kwcov/b10_response.py --target u238 --base "urr y" --kw "urrnjoy y"    # + the response to a keyword
    $PY scripts/kwcov/b10_response.py --target u238 --base "urr y" --mode talys        # engine in TALYS mode

Observables (absolute, engine vs stock): every number of every urr* file stock writes (urr.dat per (E, l, J) row,
the urr*.lLL files per (E, J), urrtalys.tot / urrnjoy.tot / urrratio.tot per E), |ln(ours/stock)| where stock is above
1e-6 of its column's maximum; file names and row structure must agree. Response: R = ours(base; kw)/ours(base),
S = stock(base; kw)/stock(base) on the same numbers, |ln(R/S)| <= 2 % (or the same absolute change). Channels: the plain
deck's cross sections must not move when `urr y` is added (output only), in the engine bit for bit.
Mode `talys`: the engine with every deliberate INCOGNITA default switched to TALYS (FIDELITY_DEFAULTS.md: `INCOGNITA_NPWINDOW`,
`INCOGNITA_EXACTFIS`, `INCOGNITA_CCEXITNB2`, ...). Stock runs keep only the URR files and channels, as JSON, in
~/kwcov/stock/b10/b10_<target>_<hash>.json; TALYS scratch is deleted after every run.
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

STOCK = Path(os.path.expanduser("~/kwcov/stock/b10"))
ENG = Path(os.path.expanduser("~/kwcov/b10eng"))
ENERGIES = (0.01, 0.1, 1.0, 5.0)
B.TARGETS.update({"au197": ("au", 79, 197), "co59": ("co", 27, 59), "u235": ("u", 92, 235)})
CH = {k: B.CHANNELS[k] for k in ("total", "elastic", "nonelastic", "capture", "inelastic", "np", "na", "fission")}
#: FIDELITY_DEFAULTS.md (branch fidelity1, scripts/kwcov/fidelity.py): every deliberate INCOGNITA default at TALYS's
TALYS_DECK = ["fluxclose n", "npwindow n", "chancap n", "nnleak n", "exactfis n", "alphatemp 0", "sfexit n",
              "kevleak2 n", "heavymacs2 n", "ftglobal n", "ccexitnbnf n", "tfold n", "ctwcont n", "alphaentr 0"]
TALYS_ENV = {"INCOGNITA_GRIDTOP": "n", "INCOGNITA_SPECCLOSE": "0", "INCOGNITA_LOWEPOT": "0",
             "INCOGNITA_TARMASSFIX": "0", "INCOGNITA_ISOROTPASS": "0"}


def _h(*a) -> str:
    return hashlib.sha1("|".join(map(str, a)).encode()).hexdigest()[:12]


def _parse_urr(d: Path) -> dict:
    """Stock urr* files as {file: {column: [values]}} in Results.urr's layout (NaN = not calculated)."""
    out: dict = {}
    p = d / "urr.dat"
    if p.is_file():
        cols = ["E", "l", "J", "P", "D(l)", "D(l,J)", "S(l)", "S(l,J)", "Gx(l,J)", "Gn(l,J)", "Gg(l,J)", "Gf(l,J)",
                "Gp(l,J)", "Ga(l,J)"]
        t = {c: [] for c in cols}
        t.update(S_n=[], xscaptherm=[], rprime=[], block_E=[])
        e = None
        for ln in p.read_text(errors="replace").splitlines():
            s = ln.strip()
            if "E-incident [MeV]:" in s:
                e = float(s.split(":")[1])
                t["block_E"].append(e)
            elif "neutron separation energy" in s:
                t["S_n"].append(float(s.split(":")[1]))
            elif "thermal capture cross section" in s:
                t["xscaptherm"].append(float(s.split(":")[1]))
            elif "potential scattering radius" in s:
                t["rprime"].append(float(s.split(":")[1]))
            elif s and not s.startswith("#"):
                v = [float(x) for x in s.split()]
                for c, x in zip(cols, [e] + v):
                    t[c].append(x)
        out["urr.dat"] = t
    for p in sorted(d.glob("urr*.l[0-9][0-9]")):
        rows = []
        for ln in p.read_text(errors="replace").splitlines():
            s = ln.strip()
            if not s or s.startswith("#"):
                continue
            if "not calculated" in s:
                rows.append((float(s.split()[0]), None))
                continue
            v = [float(x) for x in s.split()]
            rows.append((v[0], v[1:]))
        col = "spacing" if p.name.startswith("urrspacingl.") else (
            "strength" if p.name.startswith("urrneustrengthl.") else None)
        t = {"E": [r[0] for r in rows]}
        if col:
            t[col] = [float("nan") if r[1] is None else r[1][0] for r in rows]
        else:
            kind = "spacing" if "spacinglj" in p.name else ("strength" if "strengthlj" in p.name else "width")
            js = []
            for _, v in rows:
                for i in range(0, len(v or []), 3):
                    if v[i] not in js:
                        js.append(v[i])
            for j in sorted(js):
                nu, w = [], []
                for _, v in rows:
                    m = {v[i]: (v[i + 1], v[i + 2]) for i in range(0, len(v or []), 3)} if v else {}
                    nu.append(m[j][0] if j in m else float("nan"))
                    w.append(m[j][1] if j in m else float("nan"))
                t[f"J={j:g}:nu"], t[f"J={j:g}:{kind}"] = nu, w
        out[p.name] = t
    for name in ("urrtalys.tot", "urrnjoy.tot", "urrratio.tot"):
        p = d / name
        if p.is_file():
            rows = [r for r in B._rows(p)]
            out[name] = {c: [r[i] for r in rows] for i, c in enumerate(["E", "xs", "elastic", "capture", "fission"])}
    return out


def stock(target: str, kw: str, energies=ENERGIES) -> dict:
    f = STOCK / f"b10_{target}_{_h(target, kw, energies)}.json"
    if f.is_file():
        return json.loads(f.read_text())
    el, _, a = B.TARGETS[target]
    STOCK.mkdir(parents=True, exist_ok=True)
    d = Path(tempfile.mkdtemp(prefix=f"b10tmp_{target}_", dir=str(STOCK)))
    try:
        (d / "energies").write_text("".join(f"{e}\n" for e in energies))
        deck = ["projectile n", f"element {el}", f"mass {a}", "energy energies", "channels y", "filechannels y",
                "fileresidual y", "outdiscrete y"] + B._lines(kw)
        (d / "talys.inp").write_text("\n".join(deck) + "\n")
        with open(d / "talys.inp") as fi, open(d / "talys.out", "w") as fo:
            subprocess.run(["flock", B.LOCK, "nice", "-n", "10", B.TALYS], stdin=fi, stdout=fo, cwd=d, check=False)
        res: dict = {"E": list(energies)}
        for ch, (fn, _) in CH.items():
            p = d / fn
            if p.is_file():
                res[ch] = [x[1] for x in B._rows(p)]
        res["urr"] = _parse_urr(d)
        tail = (d / "talys.out").read_text(errors="replace")
        res["errors"] = [ln.strip() for ln in tail.splitlines() if "TALYS-error" in ln][:5]
    finally:
        shutil.rmtree(d, ignore_errors=True)
    f.write_text(json.dumps(res))
    return res


def engine(target: str, kw: str, mode: str = "default", energies=ENERGIES) -> dict:
    f = ENG / f"eng_{target}_{_h(target, kw, mode, energies)}.json"
    if f.is_file():
        return json.loads(f.read_text())
    _, z, a = B.TARGETS[target]
    env = {k: v for k, v in os.environ.items() if not k.startswith(("INCOGNITA_", "NUCLIDO_"))}
    lines = B._lines(kw) + (TALYS_DECK if mode == "talys" else [])
    if lines:
        env["INCOGNITA_TALYS_FIT_LINES"] = "; ".join(lines)
    if mode == "talys":
        env.update(TALYS_ENV)
    env.update(OMP_NUM_THREADS="1")
    p = subprocess.run(["flock", B.LOCK, "nice", "-n", "10", sys.executable, __file__, "_engine_child", str(z), str(a),
                        ",".join(map(str, energies))], env=env, cwd=B.ROOT, capture_output=True, text=True)
    line = [x for x in p.stdout.splitlines() if x.startswith("{")]
    if p.returncode != 0 or not line:
        return {"error": (p.stderr or p.stdout)[-1500:]}
    ENG.mkdir(parents=True, exist_ok=True)
    f.write_text(line[-1])
    return json.loads(line[-1])


def _engine_child(z: int, a: int, energies: str) -> None:
    sys.path.insert(0, str(B.ROOT))
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
    for ch, (_, key) in CH.items():
        if key in arr:
            out[ch] = [float(x) for x in np.asarray(arr[key]).ravel()]
    out["arrays"] = {k: [float(x) for x in np.asarray(v).ravel()] for k, v in arr.items()}
    out["urr"] = {fn: {c: [float(x) for x in np.asarray(v).ravel()] for c, v in t.items()} for fn, t in r.urr.items()}
    print(json.dumps(out))


def _flat(u: dict, fn: str, keycols=("E",)) -> dict:
    """{(file, column, row key): value} for one urr table; urr.dat rows keyed by (E, l, J)."""
    t = u[fn]
    out = {}
    if fn == "urr.dat":
        keys = list(zip(t["E"], t["l"], t["J"]))
        for c, v in t.items():
            if c in ("E", "l", "J", "block_E", "S_n", "xscaptherm", "rprime"):
                continue
            for k, x in zip(keys, v):
                out[(fn, c, tuple(round(float(y), 6) for y in k))] = x
        for c in ("S_n", "xscaptherm", "rprime"):
            for e, x in zip(t["block_E"], t[c]):
                out[(fn, c, (round(float(e), 6),))] = x
        return out
    for c, v in t.items():
        if c == "E":
            continue
        for e, x in zip(t["E"], v):
            out[(fn, c, (round(float(e), 6),))] = x
    return out


def flat_all(u: dict) -> dict:
    out = {}
    for fn in u:
        out.update(_flat(u, fn))
    return out


def _ok(x) -> bool:
    return x is not None and not (isinstance(x, float) and math.isnan(x))


def observables(target: str, base: str, mode: str = "default") -> dict:
    s, e = stock(target, base), engine(target, base, mode)
    if "error" in e:
        return {"error": e["error"]}
    su, eu = s["urr"], e["urr"]
    files = dict(missing=sorted(set(su) - set(eu)), extra=sorted(set(eu) - set(su)))
    fs, fe = flat_all(su), flat_all(eu)
    colmax: dict = {}
    for (fn, c, _), x in fs.items():
        if _ok(x):
            colmax[(fn, c)] = max(colmax.get((fn, c), 0.0), abs(x))
    per: dict = {}
    struct = 0
    for k, x in fs.items():
        y = fe.get(k)
        fn, c, _ = k
        if not _ok(x) or not _ok(y):
            if _ok(x) != _ok(y):
                struct += 1
            continue
        if abs(x) <= 1e-6 * colmax.get((fn, c), 0.0):
            if abs(y) > 1e-3 * colmax.get((fn, c), 0.0):
                per.setdefault(fn, []).append((c, k[2], y, x, float("inf")))
            continue
        if x * y <= 0:
            d = float("inf")
        else:
            d = abs(math.log(y / x))
        per.setdefault(fn, []).append((c, k[2], y, x, d))
    worst = {fn: max(v, key=lambda r: r[4]) for fn, v in per.items()}
    return dict(files=files, struct=struct, nkeys=(len(fs), len(fe)), worst=worst,
                chan_moved=None, wall=e.get("wall_s"))


def response(target: str, base: str, kw: str, mode: str = "default") -> dict:
    full = f"{base}; {kw}" if base.strip() else kw
    s0, s1 = stock(target, base), stock(target, full)
    e0, e1 = engine(target, base, mode), engine(target, full, mode)
    if "error" in e0 or "error" in e1:
        return {"error": e1.get("error") or e0.get("error")}
    a0, a1, b0, b1 = (flat_all(x["urr"]) for x in (e0, e1, s0, s1))
    rows, worst = [], (0.0, None)
    for k in sorted(set(b0) & set(b1), key=str):
        x0, x1, y0, y1 = b0[k], b1[k], a0.get(k), a1.get(k)
        if not all(_ok(v) for v in (x0, x1, y0, y1)):
            continue
        if min(abs(x0), abs(x1)) <= 0 or min(abs(y0), abs(y1)) <= 0:
            continue
        S, R = x1 / x0, y1 / y0
        if S <= 0 or R <= 0:
            continue
        d = abs(math.log(R / S))
        dabs = abs((y1 - y0) - (x1 - x0)) / max(abs(x1 - x0), 1e-30)
        rows.append((k, R, S, d, dabs))
        if min(d, dabs) > worst[0] and abs(math.log(S)) > 1e-4:
            worst = (min(d, dabs), (k, R, S, d, dabs))
    moved = max((abs(math.log(r[2])) for r in rows), default=0.0)
    new = dict(stock=sorted(set(map(lambda k: k[0], b1)) - set(map(lambda k: k[0], b0))),
               engine=sorted(set(map(lambda k: k[0], a1)) - set(map(lambda k: k[0], a0))))
    return dict(worst=worst, moved=moved, n=len(rows), newfiles=new)


def channels_unmoved(target: str, base: str = "urr y", mode: str = "default") -> dict:
    """The deck's cross sections with and without `base`: engine every Results array, stock the channels."""
    e0, e1 = engine(target, "", mode), engine(target, base, mode)
    s0, s1 = stock(target, ""), stock(target, base)
    ediff = max((abs(x - y) for k in e0.get("arrays", {}) for x, y in zip(e0["arrays"][k], e1["arrays"].get(k, []))),
                default=None)
    sdiff = max((abs(math.log(y / x)) for c in CH if c in s0 and c in s1 for x, y in zip(s0[c], s1[c]) if x > 0 and y > 0),
                default=None)
    return dict(engine_maxabs=ediff, narrays=len(e0.get("arrays", {})), stock_maxlog=sdiff)


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "_engine_child":
        _engine_child(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
        return
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", required=True)
    ap.add_argument("--base", default="urr y")
    ap.add_argument("--kw", default="")
    ap.add_argument("--mode", default="default")
    ap.add_argument("--unmoved", action="store_true")
    a = ap.parse_args()
    if a.unmoved:
        print(json.dumps(channels_unmoved(a.target, a.base, a.mode), default=str))
        return
    if a.kw:
        print(json.dumps(response(a.target, a.base, a.kw, a.mode), default=str))
    else:
        print(json.dumps(observables(a.target, a.base, a.mode), default=str))


if __name__ == "__main__":
    main()
