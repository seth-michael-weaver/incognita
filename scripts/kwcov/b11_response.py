#!/usr/bin/env python3
"""KWCOV B11 acceptance: medical isotope production (production, Ebeam, Eback, Ibeam, Area, rho, Tirrad, Tcool,
radiounit, yieldunit, blockyield) vs stock TALYS-2.25.

    PY=~/fastgate_data/eng/16606b356d6e/.venv/bin/python   # WSL; the engine venv has torch
    $PY scripts/kwcov/b11_response.py --target zn68 --kw "Ibeam 0.5"     # three metrics for one deck
    $PY scripts/kwcov/b11_response.py --all                               # the table of COVERAGE_PLAN.md B11

Every deck is the target's base deck (`BASE`) plus `--kw` lines (';'-separated). Stock runs keep the Y files, the
rp files, nonelastic.tot and the talys.out production table in ~/kwcov/stock/b11_<target>_<hash>/ (scratch deleted);
engine runs (input.deck.run_deck, INCOGNITA_CPINC = the deck's projectile) keep Results.production as JSON in
~/kwcov/eng/b11_<target>_<hash>.json. Metrics, all |ln(a/b)| in %:
  book   the port (physics/hf/production.py) on STOCK's own rp files vs stock's Y files: every column and time where
         stock > 1e-30 (Yield where stock > 1e-3 of its maximum: stock's yield is a float32 difference of two
         activities and is noise near saturation); the bookkeeping alone.
  abs    engine run vs stock: activity (radioactive) or number of isotopes (stable) at the end of irradiation per Y
         file, next to the production-rate ratio (= the engine's residual production over Eback..Ebeam vs stock's).
         Acceptance: within 2 % where the production rates agree to 0.5 %.
  resp   R = ours(kw)/ours(base), S = stock(kw)/stock(base) per Y file, activity and isotopes at end of irradiation
         and at the last cooling time; worst over files with stock > 1e-6 of the deck's largest value.
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
sys.path.insert(0, str(ROOT))
STOCK = Path(os.path.expanduser("~/kwcov/stock"))
ENG = Path(os.path.expanduser("~/kwcov/eng"))
TALYS = os.path.expanduser("~/opt/talys-src/bin/talys")
LOCK = "/tmp/incognita_heavy.lock"
#: target -> (projectile, element, A, energy line, base production lines)
TARGETS = {
    "zn68": ("p", "zn", 68, "energy 8 20 1", "production y;Ebeam 18;Eback 10"),
    "mo100": ("p", "mo", 100, "energy 10 26 1", "production y;Ebeam 24;Eback 15;Tirrad 6 h;Tcool 2 h"),
    "o18": ("p", "o", 18, "energy 3 15 1", "production y;Ebeam 14;Eback 4;Tirrad 2 h;Tcool 1 h"),
    "bi209a": ("a", "bi", 209, "energy 20 30 1", "production y;Ebeam 29;Eback 21;Tirrad 4 h;Tcool 1 h"),
}
#: the --all table: (target, kw, base kw or None)
TABLE = [
    ("zn68", "", None),
    ("zn68", "Ibeam 0.5", ""),
    ("zn68", "Area 2.5", ""),
    ("zn68", "rho 5", ""),
    ("zn68", "Tirrad 2 h 30 m", ""),
    ("zn68", "Tcool 3 h", ""),
    ("zn68", "Tirrad 3 d;Tcool 2 d", ""),
    ("zn68", "Tcool 0", ""),
    ("zn68", "radiounit mbq", ""),
    ("zn68", "radiounit ci", ""),
    ("zn68", "yieldunit mg", ""),
    ("zn68", "Eback -1", ""),
    ("zn68", "Ebeam 15;Eback 12", ""),
    ("zn68", "blockyield y", ""),
    ("mo100", "", None),
    ("mo100", "radiounit mci;yieldunit mug;Ibeam 0.1", ""),
    ("mo100", "Tcool 1 d;radiounit kbq;yieldunit g", ""),
    ("o18", "", None),
    ("bi209a", "", None),
]


def _deck(target: str, kw: str) -> str:
    p, el, a, en, base = TARGETS[target]
    lines = [f"projectile {p}", f"element {el}", f"mass {a}", en] + base.split(";")
    lines += [x.strip() for x in kw.split(";") if x.strip()]
    out, seen = [], {}
    for ln in lines:  # a kw line replaces the base line of the same keyword (TALYS keeps the last one anyway)
        k = ln.split()[0].lower()
        if k in seen:
            out[seen[k]] = ln
        else:
            seen[k] = len(out)
            out.append(ln)
    return "\n".join(x for x in out if x.lower() != "eback -1") + "\n"


def _tag(target: str, kw: str) -> str:
    return f"b11_{target}_{hashlib.sha1(_deck(target, kw).encode()).hexdigest()[:10]}"


def stock(target: str, kw: str) -> Path:
    d = STOCK / _tag(target, kw)
    if (d / "talys.out").is_file():
        return d
    tmp = Path(tempfile.mkdtemp(prefix="b11tmp_", dir=str(STOCK)))
    try:
        (tmp / "talys.inp").write_text(_deck(target, kw))
        with open(tmp / "talys.inp") as fi, open(tmp / "talys.full", "w") as fo:
            subprocess.run(["flock", LOCK, "nice", "-n", "10", TALYS], stdin=fi, stdout=fo, cwd=tmp, check=True)
        d.mkdir(parents=True, exist_ok=True)
        for p in tmp.iterdir():
            if p.name.startswith(("Y", "rp")) or p.name in ("nonelastic.tot", "talys.inp"):
                shutil.copy(p, d / p.name)
        full = (tmp / "talys.full").read_text(errors="replace").splitlines()
        i0 = next((i for i, s in enumerate(full) if "Summary of isotope production" in s), len(full))
        (d / "talys.out").write_text("\n".join(full[i0:i0 + 120]) + "\n")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return d


def ours(target: str, kw: str) -> dict:
    f = ENG / f"{_tag(target, kw)}.json"
    if f.is_file():
        return json.loads(f.read_text())
    os.environ["INCOGNITA_CPINC"] = TARGETS[target][0]
    from physics.hf.input.deck import run_deck

    ENG.mkdir(parents=True, exist_ok=True)
    d = Path(tempfile.mkdtemp(prefix=f"b11eng_{target}_"))
    try:
        (d / "talys.inp").write_text(_deck(target, kw))
        import fcntl

        with open(LOCK, "a") as lk:
            fcntl.flock(lk, fcntl.LOCK_EX)
            r = run_deck(d / "talys.inp")
        pr = r.production
        res = {"deck": _deck(target, kw),
               "files": {k: {c: [float(x) for x in v] for c, v in cols.items()} for k, cols in pr["files"].items()},
               "params": pr["params"], "meta": {k: (list(v) if isinstance(v, tuple) else v) for k, v in pr["meta"].items()}}
    finally:
        shutil.rmtree(d, ignore_errors=True)
    f.write_text(json.dumps(res))
    return res


def stock_files(d: Path) -> dict:
    from physics.hf.production import read_yfile

    out = {}
    for p in sorted(d.glob("Y*")):
        if p.name == "Y.tot":  # blockyield y: every nuclide in one file, prodout's loop order
            text = p.read_text()
            seen: dict = {}
            for chunk in text.split("# header:")[1:]:
                tmp = d / "_chunk.tmp"
                tmp.write_text("# header:" + chunk)
                par, cols = read_yfile(tmp)
                tmp.unlink()
                ln = [s for s in chunk.splitlines() if s.startswith("#     Z:") or s.startswith("#     A:")]
                z, a = int(ln[0].split(":")[1]), int(ln[1].split(":")[1])  # the residual's (the target's: 3 blanks)
                k = seen[(z, a)] = seen.get((z, a), -2) + 1
                name = f"Y{z:03d}{a:03d}." + ("tot" if k == -1 else "L00" if k == 0 else f"is{k}")
                out[name] = {"params": par, "cols": {c: [float(x) for x in v] for c, v in cols.items()}}
            continue
        par, cols = read_yfile(p)
        out[p.name] = {"params": par, "cols": {k: [float(x) for x in v] for k, v in cols.items()}}
    return out


def _medical(deck: str) -> dict:
    """The deck's medical input as production.settings() returns it (TALYS's defaults otherwise)."""
    from physics.hf.production import parse_time

    m = dict(Area=1.0, Eback=-1.0, Ebeam=-1.0, Ibeam=1.0, radiounit="gbq", yieldunit="num", rhotarget=-1.0,
             Tirrad=(1, 0, 0, 0, 0), unitTirrad=("d", " ", " ", " ", " "), Tcool=(1, 0, 0, 0, 0),
             unitTcool=("d", " ", " ", " ", " "))
    names = {"area": "Area", "eback": "Eback", "ebeam": "Ebeam", "ibeam": "Ibeam", "rho": "rhotarget"}
    for ln in deck.lower().splitlines():
        w = ln.split()
        if not w:
            continue
        if w[0] in names:
            m[names[w[0]]] = float(w[1])
        elif w[0] in ("radiounit", "yieldunit"):
            m[w[0]] = w[1][:3]
        elif w[0] in ("tirrad", "tcool"):
            n = "Tirrad" if w[0] == "tirrad" else "Tcool"
            m[n], m["unit" + n] = parse_time(" ".join(w[1:]))
    return m


def book(target: str, kw: str) -> tuple[float, str, int]:
    """The port on stock's rp files vs stock's Y files: (worst |ln|, where, number of files)."""
    import numpy as np

    from physics.hf import production as P

    d = stock(target, kw)
    p, _, A, _, _ = TARGETS[target]
    k0 = P.PARSYM.index(p)
    Z = next(z for z in range(1, 120) if _sym(z).lower() == TARGETS[target][1])
    Zi, Ai = Z + P.PARZ[k0], A + P.PARZ[k0] + P.PARN[k0]
    rp, non = P.read_rp_dir(d, Zi, Ai - Zi)
    out = P.production(rp=rp, nonel=non, m=_medical(_deck(target, kw)), k0=k0, Ztarget=Z, Atarget=A, maxZ=12,
                       maxN=32, eninc=tuple(non[0]))
    sf = stock_files(d)
    worst, where = 0.0, ""
    if set(sf) != set(out["files"]):
        return math.inf, f"file sets differ: {sorted(set(sf) ^ set(out['files']))}", len(sf)
    for n, s in sf.items():
        for c, vs in s["cols"].items():
            vs = np.asarray(vs)
            vo = np.asarray(out["files"][n][c], dtype=float)
            if (np.isnan(vs) != np.isnan(vo)).any():  # `Tcool 0`: TALYS's 0 * exp(overflow) = NaN, both sides
                return math.inf, f"{n} {c}: NaN in one side only", len(sf)
            vs, vo = np.nan_to_num(vs, nan=0.0), np.nan_to_num(vo, nan=0.0)
            floor = 1e-3 * vs.max() if c == "Yield" else 1e-30
            m = vs > max(floor, 1e-30)
            if not m.any():
                continue
            r = np.abs(np.log(np.where(vo[m] > 0, vo[m], 1e-300) / vs[m]))
            i = int(np.argmax(r))
            if r[i] > worst:
                worst, where = float(r[i]), f"{n} {c} t={np.asarray(s['cols']['Time'])[m][i]:.4g} h"
    return worst, where, len(sf)


def _sym(z: int) -> str:
    from physics.hf.core.constants import nuclide_symbol

    return nuclide_symbol(z)


def _eoi(cols: dict, ntime: int, col: str) -> float:
    return float(cols[col][ntime - 1])


def absolute(target: str, kw: str) -> list[tuple]:
    """[(file, quantity, |ln(ours/stock)|, |ln(prate ratio)|, ours, stock)] at the end of irradiation."""
    o = ours(target, kw)
    sf = stock_files(stock(target, kw))
    nt = int(o["meta"]["Ntime"])
    rows = []
    for n, s in sf.items():
        if n not in o["files"]:
            rows.append((n, "(missing in ours)", math.inf, math.inf, 0.0, 0.0))
            continue
        lam = float(s["params"].get("Decay rate [s^-1]", "0"))
        col = "Activity" if lam > 0 else "Isotopes"
        x, y = _eoi(o["files"][n], nt, col), _eoi(s["cols"], nt, col)
        po = float(o["params"][n]["Initial production rate [s^-1]"])
        ps = float(s["params"].get("Initial production rate [s^-1]", "0"))
        dp = abs(math.log(po / ps)) if po > 0 and ps > 0 else (0.0 if po == ps else math.inf)
        d = abs(math.log(x / y)) if x > 0 and y > 0 else (0.0 if x == y else math.inf)
        rows.append((n, col, d, dp, x, y))
    for n in o["files"]:
        if n not in sf:
            rows.append((n, "(not in stock)", math.inf, math.inf, 0.0, 0.0))
    return rows


def response(target: str, kw: str, base: str, floor: float = 1e-6) -> list[tuple]:
    """[(file, quantity@time, |ln(R/S)|, R, S)] per Y file."""
    o, ob = ours(target, kw), ours(target, base)
    s, sb = stock_files(stock(target, kw)), stock_files(stock(target, base))
    nt, ntb = int(o["meta"]["Ntime"]), int(ob["meta"]["Ntime"])
    top = max((max(v["cols"]["Activity"]) for v in s.values()), default=0.0)
    rows = []
    for n in sorted(set(s) & set(sb) & set(o["files"]) & set(ob["files"])):
        if not all(_agree(oo["params"][n], ss[n]["params"]) for oo, ss in ((o, s), (ob, sb))):
            continue  # the engine's own residual production differs from stock's: not the keyword's response
        for col in ("Activity", "Isotopes"):
            for lab, i, ib in (("EOI", nt - 1, ntb - 1), ("end", -1, -1)):
                vs, vsb = s[n]["cols"][col][i], sb[n]["cols"][col][ib]
                vo, vob = o["files"][n][col][i], ob["files"][n][col][ib]
                if col == "Activity" and vs <= floor * top:
                    continue
                if not all(x > 0 for x in (vs, vsb, vo, vob)):
                    continue
                R, S = vo / vob, vs / vsb
                rows.append((n, f"{col}@{lab}", abs(math.log(R / S)), R, S))
    return rows


def _agree(po: dict, ps: dict, tol: float = 0.005) -> bool:
    """The engine's production rate is stock's to `tol` (and not zero): the residual production agrees."""
    a = float(po["Initial production rate [s^-1]"])
    b = float(ps.get("Initial production rate [s^-1]", "0"))
    return a > 0 and b > 0 and abs(math.log(a / b)) <= tol


def _prate(target: str, kw: str, name: str) -> float:
    return float(ours(target, kw)["params"].get(name, {}).get("Initial production rate [s^-1]", 0.0))


def report(target: str, kw: str, base: str | None) -> dict:
    b, where, nf = book(target, kw)
    ab = absolute(target, kw)
    agree = [r for r in ab if r[3] <= 0.005 and r[1] in ("Activity", "Isotopes") and _prate(target, kw, r[0]) > 0]
    wa = max(agree, key=lambda r: r[2]) if agree else None
    out = {"target": target, "kw": kw, "files": nf, "book": b, "book_where": where,
           "abs_agree": (wa[0], wa[2], wa[3]) if wa else None,
           "abs_all": [(r[0], r[1], r[2], r[3]) for r in sorted(ab, key=lambda r: -r[2])[:6]]}
    if base is not None:
        rs = response(target, kw, base)
        w = max(rs, key=lambda r: r[2]) if rs else None
        out["resp"] = (w[0], w[1], w[2], w[3], w[4]) if w else None
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default="zn68")
    ap.add_argument("--kw", default="")
    ap.add_argument("--base", default=None)
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    todo = TABLE if a.all else [(a.target, a.kw, a.base)]
    for t, kw, base in todo:
        r = report(t, kw, base)
        print(f"# {t} [{kw or 'base'}]  files {r['files']}  book {100 * r['book']:.2e} % ({r['book_where']})")
        if r["abs_agree"]:
            print(f"    abs (prate within 0.5 %): worst {r['abs_agree'][0]} {100 * r['abs_agree'][1]:.3f} % "
                  f"(prate {100 * r['abs_agree'][2]:.3f} %)")
        for n, c, d, dp in r["abs_all"]:
            print(f"    abs {n:14s} {c:18s} {100 * d:9.3f} %  prate {100 * dp:9.3f} %")
        if "resp" in r and r["resp"]:
            n, q, d, R, S = r["resp"]
            print(f"    resp worst {n} {q} {100 * d:.4f} %  R={R:.6g} S={S:.6g}")


if __name__ == "__main__":
    main()
