#!/usr/bin/env python3
"""KWCOV B10b acceptance: energies below eninclow (thermal.f90, xscaptherm / xsptherm / xsalphatherm, elow), natural
targets (mass 0, abundance) and integral y vs stock TALYS-2.25.

    PY=~/fastgate_data/eng/16606b356d6e/.venv/bin/python   # WSL; the engine venv has torch
    $PY scripts/kwcov/b10b_response.py thermal --target fe56 [--kw "xscaptherm 5000"] [--mode talys]
    $PY scripts/kwcov/b10b_response.py natural --element fe
    $PY scripts/kwcov/b10b_response.py integral --target fe56 [--mode talys]

thermal: (1) PORT: thermal.fill on stock's own eref row vs stock's rows below eninclow (every file stock writes for
them; float32 noise only); (2) ENGINE vs stock on those rows, |ln(ours/stock)| where stock > 1e-6 of the file maximum;
(3) with --kw the RESPONSE R = ours(kw)/ours(base), S = stock(kw)/stock(base) on those rows.
natural: the engine's sums = abundance-weighted sums of its own isotope runs (identity), stock's natural files = the
weighted sums of stock's isotope runs, engine vs stock per channel. integral: PORT (integral.effective_b on stock's own
xs files vs stock integral.dat) and ENGINE vs stock. Stock JSON (trimmed: E + xs of the compared files) in
~/kwcov/stock/b10b; TALYS scratch is deleted after every run. Mode `talys` = b10_response's TALYS_DECK / TALYS_ENV.
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

sys.path.insert(0, str(Path(__file__).resolve().parent))
import b2_response as B  # noqa: E402
import b10_response as B10  # noqa: E402

STOCK = Path(os.path.expanduser("~/kwcov/stock/b10b"))
ENG = Path(os.path.expanduser("~/kwcov/b10beng"))
LOW = (2.53e-8, 1.0e-7, 5.0e-7, 1.0e-3, 0.1, 1.0)
INTEG = (2.53e-8, 1.0e-6, 1.0e-5, 1.0e-4, 1.0e-3, 0.01, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0,
         9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0)
TARGETS = {"fe56": ("fe", 26, 56), "fe55": ("fe", 26, 55), "fe57": ("fe", 26, 57), "fe61": ("fe", 26, 61),
           "ag109": ("ag", 47, 109), "u238": ("u", 92, 238), "co59": ("co", 27, 59), "fenat": ("fe", 26, 0)}
_KEEP = re.compile(r"^(total|elastic|nonelastic|fission)\.tot$|^xs\d{6}\.(tot|L\d\d)$|^rp\d{6}\.(tot|L\d\d)$"
                   r"|^binary\.tot$|^integral\.dat$")
_BIN = "gnpdtha"


def _h(*a) -> str:
    return hashlib.sha1("|".join(map(str, a)).encode()).hexdigest()[:12]


def _key_of(fn: str) -> str | None:
    """Stock file -> engine result_arrays key."""
    if fn in ("total.tot", "elastic.tot", "nonelastic.tot", "fission.tot"):
        return "totals_mb/" + fn[:-4]
    m = re.match(r"^xs(\d{6})\.tot$", fn)
    if m:
        return f"channels_mb/xs{m.group(1)}"
    m = re.match(r"^xs(\d{6})\.(L\d\d)$", fn)
    if m:
        return f"extras/xs{m.group(1)}.{m.group(2)}"
    m = re.match(r"^rp(\d{6})\.tot$", fn)
    if m:
        return f"residual_production_mb/rp{m.group(1)}"
    m = re.match(r"^rp(\d{6})\.(L\d\d)$", fn)
    if m:
        return f"extras/rp{m.group(1)}.{m.group(2)}"
    return None


def stock(target: str, kw: str, energies) -> dict:
    """{"E": [...], key: [mb per E], "integral": [...], "errors": [...]} of a stock run (cached JSON)."""
    f = STOCK / f"b10b_{target}_{_h(target, kw, energies)}.json"
    if f.is_file():
        return json.loads(f.read_text())
    el, _, a = TARGETS[target]
    STOCK.mkdir(parents=True, exist_ok=True)
    d = Path(tempfile.mkdtemp(prefix=f"b10btmp_{target}_", dir=str(STOCK)))
    try:
        (d / "energies").write_text("".join(f"{e}\n" for e in energies))
        deck = ["projectile n", f"element {el}", f"mass {a}", "energy energies", "channels y", "filechannels y",
                "fileresidual y", "outdiscrete y"] + B._lines(kw)
        (d / "talys.inp").write_text("\n".join(deck) + "\n")
        with open(d / "talys.inp") as fi, open(d / "talys.out", "w") as fo:
            subprocess.run(["flock", B.LOCK, "nice", "-n", "10", B.TALYS], stdin=fi, stdout=fo, cwd=d, check=False)
        res: dict = {}
        for p in sorted(d.iterdir()):
            if not _KEEP.match(p.name):
                continue
            if p.name == "integral.dat":
                res["integral"] = [ln.split() for ln in p.read_text().splitlines() if ln.strip() and ln[0] != "#"]
                continue
            rows = B._rows(p)
            if p.name == "binary.tot":
                res["E"] = [r[0] for r in rows]
                for i, t in enumerate(_BIN):
                    res[f"extras/binary.tot:{t}"] = [r[i + 1] for r in rows]
                continue
            k = _key_of(p.name)
            res[k] = [r[1] for r in rows]
            res.setdefault("E", [r[0] for r in rows])
            res.setdefault("_E_" + k, [r[0] for r in rows])
        out = (d / "talys.out").read_text(errors="replace")
        res["errors"] = [ln.strip() for ln in out.splitlines() if "TALYS-error" in ln][:5]
        res["warnings"] = sorted({ln.strip() for ln in out.splitlines() if "TALYS-warning" in ln})[:20]
    finally:
        shutil.rmtree(d, ignore_errors=True)
    f.write_text(json.dumps(res))
    return res


def engine(target: str, kw: str, mode: str, energies) -> dict:
    f = ENG / f"eng_{target}_{_h(target, kw, mode, energies)}.json"
    if f.is_file():
        return json.loads(f.read_text())
    el, _, a = TARGETS[target]
    env = {k: v for k, v in os.environ.items() if not k.startswith(("INCOGNITA_", "NUCLIDO_"))}
    lines = B._lines(kw) + (B10.TALYS_DECK if mode == "talys" else [])
    if mode == "talys":
        env.update(B10.TALYS_ENV)
    env.update(OMP_NUM_THREADS="1", INCOGNITA_CHANOBS="1")  # CHANOBS: isomer / binary columns, output only
    ENG.mkdir(parents=True, exist_ok=True)
    d = Path(tempfile.mkdtemp(prefix="b10beng_", dir=str(ENG)))
    try:
        (d / "energies").write_text("".join(f"{e}\n" for e in energies))
        deck = ["projectile n", f"element {el}", f"mass {a}", "energy energies"] + lines
        (d / "talys.inp").write_text("\n".join(deck) + "\n")
        p = subprocess.run(["flock", B.LOCK, "nice", "-n", "10", sys.executable, __file__, "_engine_child",
                            str(d / "talys.inp")], env=env, cwd=B.ROOT, capture_output=True, text=True)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    line = [x for x in p.stdout.splitlines() if x.startswith("{")]
    if p.returncode != 0 or not line:
        return {"error": (p.stderr or p.stdout)[-2500:]}
    f.write_text(line[-1])
    return json.loads(line[-1])


def _engine_child(deck: str) -> None:
    sys.path.insert(0, str(B.ROOT))
    import time

    import numpy as np

    from physics.hf import warmrun
    from physics.hf.input.deck import run_deck

    t0 = time.time()
    r = run_deck(deck)

    def flat(res):
        arr = warmrun.result_arrays(res)
        return {k: [float(x) for x in np.asarray(v).ravel()] for k, v in arr.items()}

    out = {"arrays": flat(r), "wall_s": round(time.time() - t0, 1)}
    out["thermal"] = {k: [float(x) for x in np.asarray(v).ravel()] for k, v in r.thermal.items()}
    out["integral"] = {k: (list(v) if not hasattr(v, "tolist") else v.tolist())
                       for k, v in r.integral.get("integral.dat", {}).items()}
    if r.natural:
        out["abundance"] = {str(a): w for a, w in r.natural["abundance"].items()}
        out["isotopes"] = {str(a): flat(x) for a, x in r.natural["isotopes"].items()}
    print(json.dumps(out))


def _lowrows(st: dict, elow: float) -> dict:
    """{key: {E: value}} of stock's rows below eninclow (+ the eref row)."""
    out = {}
    for k, v in st.items():
        if "/" not in k or k.startswith("_E_"):
            continue
        es = st.get("_E_" + k, st["E"])
        out[k] = {round(e, 12): x for e, x in zip(es, v)}
    return out


def thermal_check(target: str, kw: str, mode: str, base: str = "") -> dict:
    """PORT, ENGINE and (with base != kw) RESPONSE numbers for one thermal deck."""
    import numpy as np

    sys.path.insert(0, str(B.ROOT))
    from physics.hf import thermal

    _, Z, A = TARGETS[target]
    st = stock(target, kw, LOW)
    elow = 1.0e-6
    for ln in B._lines(kw):
        if ln.split()[0] == "elow":
            elow = float(ln.split()[1])
    g = thermal.low_grid(LOW, elow)
    n = g["Ninclow"]
    low_e = [round(float(np.float32(e)), 12) for e in g["eninc"][:n]]
    eref = g["eref"]
    rows = _lowrows(st, elow)
    sE = [round(e, 12) for e in st["E"]]

    def at(k, e):
        d = rows[k]
        for kk, v in d.items():
            if math.isclose(kk, e, rel_tol=1e-5):
                return v
        return None

    deck = {}
    for ln in B._lines(kw):
        w = ln.split()
        if w[0] in ("xscaptherm", "xsptherm", "xsalphatherm"):
            deck[{"xscaptherm": "cap", "xsptherm": "p", "xsalphatherm": "alpha"}[w[0]]] = float(w[1])
    th = thermal.thermal_xs(Z, A, deck, None)
    ref = {k: at(k, eref) for k in rows if at(k, eref) is not None}
    filled = thermal.fill(ref, g, th, Z, A)
    port = []
    for k, v in filled.items():
        if k == "E" or k not in rows:
            continue
        mx = max(abs(x) for x in rows[k].values()) or 1.0
        for e, x in zip(filled["E"], v):
            s = at(k, round(float(np.float32(e)), 12))
            if s is None or abs(s) < 1e-6 * mx:
                continue
            port.append((abs(math.log(max(x, 1e-300) / s)), k, e, x, s))
    port.sort(reverse=True)
    eng = engine(target, kw, mode, LOW)
    out = {"target": target, "kw": kw, "mode": mode, "eninclow": g["eninclow"], "E1v": g["E1v"], "eref": eref,
           "stock_errors": st.get("errors"), "therm": {k: th[k][-1] for k in th},
           "port_worst": port[:3], "port_n": len(port)}
    if "error" in eng:
        out["engine_error"] = eng["error"][-800:]
        return out
    T = eng["thermal"]
    cmp_ = []
    for k, v in T.items():
        if k not in rows or k in ("E",):
            continue
        mx = max(abs(x) for x in rows[k].values()) or 1.0
        for e, x in zip(T["E"], v):
            s = at(k, round(float(np.float32(e)), 12))
            if s is None or abs(s) < 1e-6 * mx or s <= 0:
                continue
            cmp_.append((abs(math.log(max(x, 1e-300) / s)), k, e, x, s))
    cmp_.sort(reverse=True)
    out["engine_worst"] = cmp_[:4]
    out["engine_n"] = len(cmp_)
    missing = sorted(k for k in rows if k not in T and any(at(k, e) for e in low_e))
    out["stock_keys_not_in_engine"] = missing[:10]
    out["engine_wall_s"] = eng.get("wall_s")
    if base != kw:
        st0 = stock(target, base, LOW)
        rows0 = _lowrows(st0, elow)
        e0 = engine(target, base, mode, LOW)
        T0 = e0.get("thermal", {})
        resp = []
        for k in T:
            if k == "E" or k not in T0 or k not in rows or k not in rows0:
                continue
            for i, e in enumerate(T["E"]):
                ek = round(float(np.float32(e)), 12)
                s1, s0 = at(k, ek), rows0[k].get(ek)
                if s0 is None:
                    s0 = next((v for kk, v in rows0[k].items() if math.isclose(kk, ek, rel_tol=1e-5)), None)
                o1 = T[k][i]
                o0 = next((v for e0, v in zip(T0.get("E", []), T0[k]) if math.isclose(e0, e, rel_tol=1e-5)), None)
                if not s1 or not s0 or not o1 or not o0 or s1 < 1e-6 or s0 < 1e-6:
                    continue
                resp.append((abs(math.log((o1 / o0) / (s1 / s0))), k, e, o1 / o0, s1 / s0))
        resp.sort(reverse=True)
        out["response_worst"] = resp[:4]
        out["response_n"] = len(resp)
    return out


def natural_check(element: str, mode: str, energies=(1.0, 5.0, 14.0)) -> dict:
    """Engine natural sums vs its isotope runs (identity) and vs stock natural; stock natural vs stock isotopes."""
    sys.path.insert(0, str(B.ROOT))
    from physics.hf import natural as N

    Z = {"fe": 26, "ni": 28}[element]
    ab = N.abundances(Z)
    TARGETS.setdefault(f"{element}nat", (element, Z, 0))
    stn = stock(f"{element}nat", "", energies)
    isos = {}
    for a in ab:
        TARGETS.setdefault(f"{element}{a}", (element, Z, a))
        isos[a] = stock(f"{element}{a}", "", energies)
    worst_stock = []
    for k, v in stn.items():
        if "/" not in k or k.startswith("_E_"):
            continue
        for i, x in enumerate(v):
            s = sum(ab[a] * (isos[a].get(k, [0.0] * len(v))[i] if len(isos[a].get(k, [])) == len(v) else 0.0)
                    for a in ab)
            if x > 1e-3:
                worst_stock.append((abs(s / x - 1.0), k, i, x, s))
    worst_stock.sort(reverse=True)
    eng = engine(f"{element}nat", "", mode, energies)
    out = {"element": element, "abundance": ab, "stock_natural_vs_isotope_sum": worst_stock[:3]}
    if "error" in eng:
        out["engine_error"] = eng["error"][-800:]
        return out
    arr, iso = eng["arrays"], eng["isotopes"]
    ident = 0.0
    for k, v in arr.items():
        if k == "e_inc_mev":
            continue
        for i, x in enumerate(v):
            s = sum(ab[int(a)] * (iso[a].get(k, [0.0] * len(v))[i]) for a in iso)
            ident = max(ident, abs(x - s) / max(abs(x), 1e-30) if x else abs(s))
    out["engine_natural_vs_isotope_sum"] = ident
    cmp_ = []
    for ch, (fn, key) in B.CHANNELS.items():
        if key in arr and key in stn:
            for i, (x, s) in enumerate(zip(arr[key], stn[key])):
                if s > 1.0:
                    cmp_.append((abs(math.log(x / s)) if x > 0 else 99.0, key, energies[i], x, s))
    for k in [k for k in stn if k.startswith("residual_production_mb/")]:
        if k in arr:
            for i, (x, s) in enumerate(zip(arr[k], stn[k])):
                if s > 1.0:
                    cmp_.append((abs(math.log(x / s)) if x > 0 else 99.0, k, energies[i], x, s))
    cmp_.sort(reverse=True)
    out["engine_vs_stock_worst"] = cmp_[:5]
    out["engine_wall_s"] = eng.get("wall_s")
    return out


def integral_check(target: str, mode: str) -> dict:
    """integral.dat: PORT on stock's own xs files, ENGINE vs stock."""
    import numpy as np

    sys.path.insert(0, str(B.ROOT))
    from physics.hf import integral as I

    _, Z, A = TARGETS[target]
    st = stock(target, "integral y", INTEG)
    rows = st.get("integral", [])
    port = []
    for r in rows:
        fn, flux, eff = r[0], r[1], float(r[2])
        k = _key_of(fn)
        if k not in st:
            continue
        sp = I.spectrum(flux)
        mine = I.effective_b(st.get("_E_" + k, st["E"]), st[k], sp[0], sp[1])
        port.append((abs(mine / eff - 1.0) if eff else abs(mine), fn, flux, mine, eff))
    out = {"target": target, "stock_rows": rows, "port": port, "stock_warnings": st.get("warnings")}
    eng = engine(target, "integral y", mode, INTEG)
    if "error" in eng:
        out["engine_error"] = eng["error"][-800:]
        return out
    E = eng["integral"]
    out["engine_rows"] = list(zip(E.get("file", []), E.get("spectrum", []), E.get("xseff_b", [])))
    cmp_ = []
    for (fn, fl, x), r in zip(out["engine_rows"], rows):
        if fn == r[0] and fl == r[1]:
            cmp_.append((abs(math.log(x / float(r[2]))) if x > 0 and float(r[2]) > 0 else None, fn, fl, x,
                         float(r[2])))
    out["engine_vs_stock"] = cmp_
    out["engine_wall_s"] = eng.get("wall_s")
    _ = np
    return out


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "_engine_child":
        _engine_child(sys.argv[2])
        return
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=("thermal", "natural", "integral", "stock"))
    ap.add_argument("--target", default="fe56")
    ap.add_argument("--element", default="fe")
    ap.add_argument("--kw", default="")
    ap.add_argument("--base", default="")
    ap.add_argument("--mode", default="default", choices=("default", "talys"))
    a = ap.parse_args()
    if a.what == "thermal":
        r = thermal_check(a.target, a.kw, a.mode, a.base if a.kw else "")
    elif a.what == "natural":
        r = natural_check(a.element, a.mode)
    elif a.what == "integral":
        r = integral_check(a.target, a.mode)
    else:
        r = {k: (v if not isinstance(v, list) or len(v) < 12 else v[:12]) for k, v in
             stock(a.target, a.kw, LOW).items() if not k.startswith("_E_")}
    print(json.dumps(r, indent=1, default=str))


if __name__ == "__main__":
    main()
