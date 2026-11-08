#!/usr/bin/env python3
"""KWCOV B8 acceptance: fission extras (per-nucleus fission, PFNS, fisfeed) and the fission model keywords, vs stock.

    PY=~/fastgate_data/eng/16606b356d6e/.venv/bin/python   # WSL; the engine venv has torch
    $PY scripts/kwcov/b8_response.py --target u238 --kw ""                 # observables of the default deck
    $PY scripts/kwcov/b8_response.py --target u238 --kw "tmadjust 1.2"     # + the response to a keyword

Channels: the method of b2_response.py (R = ours(kw)/ours(default), S = stock(kw)/stock(default), |ln(R/S)| <= 2 %
where stock > 1 mb) over b2's channels plus the fission per fissioning nuclide (rpZZZAAA.fis, FISOBS names, output
only); every row also carries the millibarns each side moved (the B5-B7 comparison where the engine's default
fission differs from stock). Observables (absolute, engine vs stock): per-nucleus fission, the Iwamoto PFNS (mean
energy, shape where the spectrum is above 1e-3 of its peak, Maxwell ratio, CM column) and the fisfeed populations
(sum over bins = rpZZZAAA.fis). Stock runs keep only those files, as JSON, in ~/kwcov/stock/b8/b8_<target>_<hash>.json;
TALYS scratch is deleted after every run.
"""
from __future__ import annotations

import argparse
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

STOCK = Path(os.path.expanduser("~/kwcov/stock"))
B.CACHE = STOCK / "b8"
B.__file__ = __file__
B.TARGETS.update({"u235": ("u", 92, 235), "pu239": ("pu", 94, 239), "th232": ("th", 90, 232)})
for _el, _z, _a in list(B.TARGETS.values()):
    if _z < 90:
        continue
    for _dz in range(0, 3):
        for _da in range(0, 6):
            _k = f"rp{_z - _dz:03d}{_a + 1 - _da:03d}.fis"
            B.CHANNELS[f"fis{_z - _dz}_{_a + 1 - _da}"] = (_k, f"extras/{_k}")


def _rows(p: Path) -> list[list[float]]:
    return B._rows(p)


def stock(target: str, kw: str, energies=B.ENERGIES) -> dict:
    """Channels (b2 names), rp*.fis, pfns*.fis (4 columns), fis*.feed (Ex, Population) of a stock run (cached)."""
    f = B._tag(target, "B8|" + kw, "stock", energies).with_name(
        f"b8_{target}_{B._tag(target, kw, 'x', energies).stem.split('_')[-1]}.json")
    if f.is_file():
        return json.loads(f.read_text())
    el, _, a = B.TARGETS[target]
    STOCK.mkdir(parents=True, exist_ok=True)
    d = Path(tempfile.mkdtemp(prefix=f"b8tmp_{target}_", dir=str(STOCK)))
    try:
        (d / "energies").write_text("".join(f"{e}\n" for e in energies))
        lines = []
        for w in B._lines(kw):  # a file a deck line names is copied next to talys.inp, as TALYS reads it from the cwd
            p = os.path.expanduser(w.split()[-1])
            if os.path.isfile(p):
                shutil.copy(p, d)
                w = " ".join(w.split()[:-1] + [os.path.basename(p)])
            lines.append(w)
        deck = ["projectile n", f"element {el}", f"mass {a}", "energy energies", "channels y", "filechannels y",
                "fileresidual y", "outdiscrete y", "fisfeed y"] + lines
        (d / "talys.inp").write_text("\n".join(deck) + "\n")
        with open(d / "talys.inp") as fi, open(d / "talys.out", "w") as fo:
            subprocess.run(["flock", B.LOCK, "nice", "-n", "10", B.TALYS], stdin=fi, stdout=fo, cwd=d, check=True)
        res: dict = {"E": None}
        for ch, (fn, _) in B.CHANNELS.items():
            p = d / fn
            if not p.is_file():
                continue
            r = _rows(p)
            if res["E"] is None and fn == "fission.tot":
                res["E"] = [x[0] for x in r]
            res[ch] = [x[1] for x in r]
        if res["E"] is None:
            res["E"] = list(energies)
        res["pfns"] = {}
        for p in sorted(d.glob("pfns*.fis")):
            e = float(p.name[4:12])
            head = p.read_text(errors="replace")
            eav = [float(x.split(":")[1]) for x in head.splitlines() if "E-average [MeV]" in x]
            res["pfns"][str(e)] = {"eav": eav[0] if eav else None, "rows": _rows(p)}
        res["feed"] = {}
        for p in sorted(d.glob("fis*.feed")):
            res["feed"][p.name] = [[x[0], x[1]] for x in _rows(p)]
        tail = (d / "talys.out").read_text(errors="replace")
        res["warnings"] = [ln.strip() for ln in tail.splitlines() if "TALYS-warning" in ln or "TALYS-error" in ln][:20]
    finally:
        shutil.rmtree(d, ignore_errors=True)
    f.write_text(json.dumps(res))
    return res


def engine(target: str, kw: str, energies=B.ENERGIES) -> dict:
    f = B._tag(target, "B8|" + kw, "engine", energies)
    if f.is_file():
        return json.loads(f.read_text())
    _, z, a = B.TARGETS[target]
    env = {k: v for k, v in os.environ.items() if not k.startswith(("INCOGNITA_", "NUCLIDO_"))}
    if kw.strip():
        env["INCOGNITA_TALYS_FIT_LINES"] = kw
    env.update(OMP_NUM_THREADS="1", INCOGNITA_FISOBS="1")
    p = subprocess.run(["flock", B.LOCK, "nice", "-n", "10", sys.executable, __file__, "_engine_child", str(z), str(a),
                        ",".join(map(str, energies))], env=env, cwd=B.ROOT, capture_output=True, text=True)
    line = [x for x in p.stdout.splitlines() if x.startswith("{")]
    if p.returncode != 0 or not line:
        return {"error": (p.stderr or p.stdout)[-1500:]}
    res = json.loads(line[-1])
    B.CACHE.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(res))
    return res


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
    for ch, (_, key) in B.CHANNELS.items():
        if key in arr:
            out[ch] = [float(x) for x in np.asarray(arr[key]).ravel()]
    for k in ("nubarn.tot:wahl", "pfns.fis:E-average"):
        if k in r.extras:
            out[k] = r.extras[k].tolist()
    out["spectra"] = {k: np.nan_to_num(v.numpy(), nan=-1.0).tolist() for k, v in r.spectra.items()
                      if k.startswith(("pfns.fis", "fis"))}
    print(json.dumps(out))


def channels(target: str, kw: str, energies, base: str = "") -> dict:
    """The response to `kw` from the deck `base` (default: the plain deck)."""
    full = f"{base}; {kw}" if base.strip() else kw
    s0, s1 = stock(target, base, energies), stock(target, full, energies)
    e0, e1 = engine(target, base, energies), engine(target, full, energies)
    if "error" in e0 or "error" in e1:
        return {"error": e1.get("error") or e0.get("error")}
    rows, worst = [], 0.0
    for ch in B.CHANNELS:
        if not all(ch in x for x in (s0, s1, e0, e1)):
            continue
        for i, e in enumerate(s0["E"]):
            a0, a1, b0, b1 = e0[ch][i], e1[ch][i], s0[ch][i], s1[ch][i]
            if min(b0, b1) <= 1.0 or a0 <= 0 or a1 <= 0:
                continue
            d = abs(math.log((a1 / a0) / (b1 / b0)))
            rows.append(dict(ch=ch, E=e, R=a1 / a0, S=b1 / b0, dlog=d, dmb_ours=a1 - a0, dmb_stock=b1 - b0,
                             abs_ours=a1, abs_stock=b1))
            worst = max(worst, d)
    return {"rows": rows, "worst": worst, "moved": max((abs(math.log(r["S"])) for r in rows), default=0.0)}


def observables(target: str, kw: str, energies) -> dict:
    """Engine vs stock, absolute: per-nucleus fission, PFNS, fisfeed."""
    s, e = stock(target, kw, energies), engine(target, kw, energies)
    if "error" in e:
        return {"error": e["error"]}
    out = {"fis": [], "pfns": [], "feed": []}
    for ch in B.CHANNELS:
        if ch.startswith("fis") and ch in s and ch in e:
            for i, en in enumerate(s["E"]):
                if s[ch][i] > 1.0:
                    out["fis"].append((ch, en, e[ch][i], s[ch][i], math.log(e[ch][i] / s[ch][i])))
    sp = e.get("spectra", {})
    for i, en in enumerate(e["E"]):
        st = s["pfns"].get(str(float(en)))
        if st is None or "pfns.fis" not in sp:
            continue
        rows = st["rows"]
        es, ps, ms, cs = ([r[j] for r in rows] for j in range(4))
        eo, po, mo, co = sp["pfns.fis:E"][i], sp["pfns.fis"][i], sp["pfns.fis:Maxwell_ratio"][i], sp["pfns.fis:CM"][i]
        grid = max(abs(x - y) for x, y in zip(es, eo)) if len(es) == len(eo) else float("inf")
        peak = max(ps)
        shape = max((abs(math.log(po[j] / ps[j])) for j in range(len(ps)) if ps[j] > 1e-3 * peak and po[j] > 0),
                    default=float("inf"))
        mrat = max((abs(math.log(mo[j] / ms[j])) for j in range(len(ms)) if ps[j] > 1e-3 * peak and mo[j] > 0),
                   default=float("inf"))
        cmr = max((abs(math.log(co[j] / cs[j])) for j in range(len(cs)) if cs[j] > 1e-3 * max(cs) and co[j] > 0),
                  default=float("inf"))
        eav_o = e["pfns.fis:E-average"][i]
        out["pfns"].append(dict(E=en, n=(len(eo), len(es)), grid=grid, eav=(eav_o, st["eav"]),
                                eav_d=math.log(eav_o / st["eav"]), shape=shape, maxwell=mrat, cm=cmr))
    for name, rows in s.get("feed", {}).items():
        zA, en = name[3:9], float(name[10:18])
        key = f"fis{zA}.feed"
        if key not in sp or en not in e["E"]:
            continue
        i = e["E"].index(en)
        pop_o = [x for x in sp[key][i] if x >= 0]
        tot_s, tot_o = sum(r[1] for r in rows), sum(pop_o)
        top_s, top_o = rows[-1][1], (pop_o[-1] if pop_o else 0.0)
        out["feed"].append(dict(name=name, n=(len(pop_o), len(rows)), sum=(tot_o, tot_s), top=(top_o, top_s)))
    return out


def report(target: str, kw: str, energies, base: str = "") -> dict:
    full = f"{base}; {kw}" if base.strip() else kw
    o = observables(target, full, energies)
    if "error" in o:
        print(f"{target} [{kw}] ERROR {o['error'][-900:]}")
        return o
    print(f"== {target} [{kw or 'default'}]" + (f" from [{base}]" if base.strip() else ""))
    for ch, en, a, b, d in o["fis"]:
        print(f"    {ch:<12} E={en:<5g} ours {a:10.3f} stock {b:10.3f} mb  ({100 * d:+.2f} %)")
    for x in o["pfns"]:
        print(f"    PFNS E={x['E']:<5g} n={x['n']} grid {x['grid']:.1e}  Eav {x['eav'][0]:.4f} vs {x['eav'][1]:.4f} "
              f"({100 * x['eav_d']:+.3f} %)  shape {100 * x['shape']:.3f} %  Maxwell ratio {100 * x['maxwell']:.3f} %"
              f"  CM {100 * x['cm']:.3f} %")
    for x in o["feed"]:
        print(f"    {x['name']:<26} rows {x['n']}  sum {x['sum'][0]:.4g} vs {x['sum'][1]:.4g}  top {x['top'][0]:.4g} vs "
              f"{x['top'][1]:.4g}")
    if kw.strip():
        c = channels(target, kw, energies, base)
        if "error" in c:
            print(f"    channels ERROR {c['error'][-900:]}")
        else:
            print(f"    response worst |ln(R/S)| = {100 * c['worst']:.2f} % (stock moved up to {100 * c['moved']:.1f} %)"
                  f"  {'PASS' if c['worst'] <= 0.02 else 'FAIL'}")
            for x in sorted(c["rows"], key=lambda x: -x["dlog"])[:8]:
                print(f"      {x['ch']:<10} E={x['E']:<5g} R={x['R']:.4f} S={x['S']:.4f} d={100 * x['dlog']:.2f} %  "
                      f"moved ours {x['dmb_ours']:+.2f} mb, stock {x['dmb_stock']:+.2f} mb")
        o["channels"] = c
    return o


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "_engine_child":
        _engine_child(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
        return
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default="u238")
    ap.add_argument("--kw", action="append", required=True)
    ap.add_argument("--energies", default=",".join(map(str, B.ENERGIES)))
    ap.add_argument("--stock-only", action="store_true")
    ap.add_argument("--base", default="", help="deck lines the response is taken from (default: none)")
    ap.add_argument("--json")
    a = ap.parse_args()
    B.CACHE.mkdir(parents=True, exist_ok=True)
    es = tuple(float(x) for x in a.energies.split(","))
    allr = []
    for kw in a.kw:
        if a.stock_only:
            s0, s1 = stock(a.target, "", es), stock(a.target, kw, es)
            for ch in B.CHANNELS:
                if ch in s0 and ch in s1:
                    for i, en in enumerate(s0["E"]):
                        if max(s0[ch][i], s1[ch][i]) > 1.0:
                            d = math.log(max(s1[ch][i], 1e-30) / max(s0[ch][i], 1e-30))
                            if abs(d) > 1e-4:
                                print(f"    {ch:<10} E={en:<5g} {s0[ch][i]:10.3f} -> {s1[ch][i]:10.3f} ({100 * d:+.2f} %)")
            print(f"{a.target} [{kw}] stock warnings: {s1.get('warnings', [])[:3]}")
            continue
        allr.append(report(a.target, kw, es, a.base))
    if a.json:
        Path(a.json).write_text(json.dumps(allr, indent=1, default=str))


if __name__ == "__main__":
    main()
