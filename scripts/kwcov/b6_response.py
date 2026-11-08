#!/usr/bin/env python3
"""KWCOV B6 acceptance: the RESPONSE of the engine to the optical-model / direct deck keywords vs stock TALYS-2.25's.

    PY=~/fastgate_data/eng/16606b356d6e/.venv/bin/python   # WSL; the engine venv has torch
    $PY scripts/kwcov/b6_response.py [--only NAME ...] [--json out.json]

The metric and the engine side are B2's (`b2_response.py`: R = ours(kw)/ours(default), S = stock(kw)/stock(default),
|ln(R/S)| <= 2 % where stock > 1 mb, n + target at 1/5/14 MeV, one fresh process per run under `nice -n 10` and
`flock /tmp/incognita_heavy.lock`). What B6 adds: decks that read files. The files (`optmod` tables, `optmodfilen`
element files, adjustment tables) are written to ~/kwcov/b6/files/ and named by absolute path in the engine's deck
lines; the stock run copies them into its run directory and names them by basename, as a TALYS user would. A trimmed
copy of every stock run (talys.inp + the channel files) is kept in ~/kwcov/stock/b6_<name>/.

JSON caches: ~/kwcov/b6/ (the defaults are copied from B2's cache: the default runs are bit-identical).
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

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import b2_response as B2  # noqa: E402

ROOT = HERE.parents[1]
B6 = Path(os.path.expanduser("~/kwcov/b6"))
FILES = B6 / "files"
KEEP = Path(os.path.expanduser("~/kwcov/stock"))
TS = Path(os.path.expanduser("~/opt/talys-src/structure"))


# ------------------------------------------------------------------------------------------------ the input files
def make_files() -> None:
    """The files the decks read: a modified Fe local OMP file, a Fe-56 neutron `optmod` table, the best tables."""
    FILES.mkdir(parents=True, exist_ok=True)
    # optmodfilen: structure/optical/neutron/n-Fe.omp with Fe-56's real depth v1 +2 MeV and d1 x1.1
    src = (TS / "optical/neutron/n-Fe.omp").read_text().splitlines()
    out, i = [], 0
    while i < len(src):
        head = src[i]
        out.append(head)
        ia, nomp = int(head[4:8]), int(head[8:12])
        for j in range(nomp):
            l1, l2, l3, l4 = src[i + 1 + 4 * j: i + 5 + 4 * j]
            if ia == 56:
                v1 = float(l2[16:22]) + 2.0
                l2 = l2[:16] + f"{v1:6.1f}" + l2[22:]
                d1 = float(l3[16:22]) * 1.1
                l3 = l3[:16] + f"{d1:6.1f}" + l3[22:]
            out += [l1, l2, l3, l4]
        i += 1 + 4 * nomp
    (FILES / "n-fe-b6.omp").write_text("\n".join(out) + "\n")
    # optmodfilep: a Mn file (TALYS has none) whose A=56 entry is p-Fe.omp's Fe-56 set with v1 -3 MeV: the
    # protons leaving Mn-56 (n + Fe-56 -> (n,p)) take it instead of the global KD03 potential
    src = (TS / "optical/proton/p-Fe.omp").read_text().splitlines()
    i = next(j for j, x in enumerate(src) if x[4:8].strip() == "56")
    l1, l2, l3, l4 = src[i + 1: i + 5]
    l2 = l2[:16] + f"{float(l2[16:22]) - 3.0:6.1f}" + l2[22:]
    (FILES / "p-mn-b6.omp").write_text("\n".join(["  25  56   1", l1, l2, l3, l4]) + "\n")
    # optmod: a Fe-56 neutron table, the engine's own KD03 values (= TALYS's, A-omppar) with Wd x1.15, rv x1.01
    if not (FILES / "fe56-n-b6.omp").is_file():
        sys.path.insert(0, str(ROOT))
        import torch

        from physics.hf.core.tensors import DTYPE
        from physics.hf.input.defaults import default_options, default_params
        from physics.hf.omp.parameters import COLUMNS, omp_parameters

        es = [0.001, 0.01, 0.1, 0.5] + [float(x) for x in range(1, 31)]
        o = default_options(26, 56)
        p = omp_parameters(26, 30, 1, torch.tensor(es, dtype=DTYPE), default_params(26, 56, o), o)
        rows = []
        for i, e in enumerate(es):
            v = [float(getattr(p, c)[i]) for c in COLUMNS]
            v[1] *= 1.01   # rv
            v[9] *= 1.15   # Wd
            rows.append(f"{e:8.3f} " + " ".join(f"{x:8.4f}" for x in v))
        (FILES / "fe56-n-b6.omp").write_text(f"  26  56 {len(es)}\n" + "\n".join(rows) + "\n")
    for f in ("Fe056/misc/tables/awdadjust-n.table", "U238/n-U238.omp"):
        shutil.copy(TS / "best" / f, FILES / Path(f).name)


FE_REST = ("ldmodel 2", "rvadjust p 0.99", "avadjust p 0.99", "gnadjust 26 57 0.90", "gpadjust 26 57 0.90",
           "aadjust 25 56 1.12", "pshiftadjust 26 56 -0.2", "pshiftadjust 25 56 0.1", "cknock a 1.1", "cstrip a 1.1",
           "ldmodelcn 1", "ngfit y")


B2.TARGETS.setdefault("au197", ("au", 79, 197))
AU_E = (0.01, 0.1, 1.0, 5.0)


def _best_rest(rel: str) -> tuple:
    """A best file's keyword lines (lowercased, comments dropped) without `optmod`."""
    out = []
    for ln in (TS / "best" / rel).read_text().splitlines():
        s = ln.strip().lower()
        if s and not s.startswith("#") and not s.startswith("optmod"):
            out.append(" ".join(s.split()))
    return tuple(out)


#: name -> (target, engine deck lines, stock deck lines, stock input files)
def decks() -> dict:
    f = FILES
    return {
        "fe_awdadjustf": ("fe56", "awdadjustf n 2 20 10 0", "awdadjustf n 2 20 10 0", ()),
        "fe_rvadjustf": ("fe56", "rvadjustf n 1 20 3 0", "rvadjustf n 1 20 3 0", ()),
        "fe_rvadjustf_p": ("fe56", "rvadjustf p 1 20 5 0", "rvadjustf p 1 20 5 0", ()),
        "fe_v1adjust_tal": ("fe56", "v1adjust n 1.0 3 16 10 1.03", "v1adjust n 1.0 3 16 10 1.03", ()),
        "fe_d1adjust_p_tal": ("fe56", "d1adjust p 1.0 1 15 8 1.2", "d1adjust p 1.0 1 15 8 1.2", ()),
        "fe_awdadjust_table": ("fe56", f"awdadjust n 1. {f}/awdadjust-n.table", "awdadjust n 1. awdadjust-n.table",
                               (f / "awdadjust-n.table",)),
        "fe_incadjust": ("fe56", "incadjust n;v1adjust n 1.02;d1adjust p 1.1", "incadjust n\nv1adjust n 1.02\nd1adjust p 1.1",
                         ()),
        "fe_v1adjust_ref": ("fe56", "v1adjust n 1.02;d1adjust p 1.1", "v1adjust n 1.02\nd1adjust p 1.1", ()),
        "fe_optmodfilen": ("fe56", f"optmodfilen 26 {f}/n-fe-b6.omp", "optmodfilen 26 n-fe-b6.omp",
                           (f / "n-fe-b6.omp",)),
        "fe_optmodfilep": ("fe56", f"optmodfilep 25 {f}/p-mn-b6.omp", "optmodfilep 25 p-mn-b6.omp",
                           (f / "p-mn-b6.omp",)),
        "fe_optmod": ("fe56", f"optmod 26 56 {f}/fe56-n-b6.omp", "optmod 26 56 fe56-n-b6.omp", (f / "fe56-n-b6.omp",)),
        "fe_coulomb": ("fe56", "coulomb n", "coulomb n", ()),
        "fe_vinfadjust": ("fe56", "vinfadjust n 1.2", "vinfadjust n 1.2", ()),
        "fe_eciscompound": ("fe56", "eciscompound y", "eciscompound y", ()),
        "fe_best": ("fe56", "best y", "best y", (f / "awdadjust-n.table",)),
        # Fe-56's best file without its B6 line (the awdadjust table): what is left of `best y` is outside B6
        "fe_best_rest": ("fe56", ";".join(FE_REST), "\n".join(FE_REST), ()),
        # optmodall y (B5 refused it): a set per compound nucleus + TALYS reading the initial one before `energies`
        "au_optmodall": ("au197", "optmodall y", "optmodall y", (), AU_E),
        "au_racap_optmodall": ("au197", "racap y;optmodall y", "racap y\noptmodall y", (), AU_E),
        "fe_optmodall": ("fe56", "optmodall y", "optmodall y", ()),
        "u_optmodall": ("u238", "optmodall y", "optmodall y", ()),
        "u_riplomp_n": ("u238", "riplomp n", "riplomp n", ()),
        "u_optmod": ("u238", f"optmod 92 238 {f}/n-U238.omp", "optmod 92 238 n-U238.omp", (f / "n-U238.omp",)),
        "u_awdadjustf": ("u238", "awdadjustf n 2 20 10 0", "awdadjustf n 2 20 10 0", ()),
        "u_best": ("u238", "best y", "best y", (f / "n-U238.omp",)),
        # U-238's best file without its B6 line (optmod): what is left of `best y` is outside B6
        "u_best_rest": ("u238", ";".join(_best_rest("U238/n-U238.talys")), "\n".join(_best_rest("U238/n-U238.talys")),
                        ()),
    }


# -------------------------------------------------------------------------------------------------------- runs
def stock(name: str, target: str, lines: str, files, energies=B2.ENERGIES) -> dict:
    """B2's stock run, with input files copied into the run directory; a trimmed copy kept in ~/kwcov/stock/b6_<name>."""
    tag = B6 / f"stock_{name}.json"
    if not lines:
        return B2.stock(target, "", energies)
    if tag.is_file():
        return json.loads(tag.read_text())
    el, _, a = B2.TARGETS[target]
    d = Path(tempfile.mkdtemp(prefix=f"b6_{name}_", dir=str(B6)))
    try:
        (d / "energies").write_text("".join(f"{e}\n" for e in energies))
        deck = ["projectile n", f"element {el}", f"mass {a}", "energy energies", "channels y", "filechannels y",
                "fileresidual y", "outdiscrete y"] + [x for x in lines.split("\n") if x.strip()]
        (d / "talys.inp").write_text("\n".join(deck) + "\n")
        for x in files:
            shutil.copy(x, d)
        with open(d / "talys.inp") as fi, open(d / "talys.out", "w") as fo:
            subprocess.run(["flock", B2.LOCK, "nice", "-n", "10", B2.TALYS], stdin=fi, stdout=fo, cwd=d, check=True)
        res: dict = {"E": None}
        keep = KEEP / f"b6_{name}"
        keep.mkdir(parents=True, exist_ok=True)
        shutil.copy(d / "talys.inp", keep)
        for ch, (fn, _) in B2.CHANNELS.items():
            p = d / fn
            if not p.is_file():
                continue
            shutil.copy(p, keep)
            r = B2._rows(p)
            if res["E"] is None:
                res["E"] = [x[0] for x in r]
            res[ch] = [x[1] for x in r]
        tail = (d / "talys.out").read_text(errors="replace")
        res["warnings"] = [ln.strip() for ln in tail.splitlines() if "TALYS-warning" in ln or "TALYS-error" in ln][:20]
    finally:
        shutil.rmtree(d, ignore_errors=True)
    tag.write_text(json.dumps(res))
    return res


def engine(name: str, target: str, kw: str, energies=B2.ENERGIES) -> dict:
    if not kw:
        return B2.engine(target, "", energies)  # B2's cache (bit-identical defaults)
    tag = B6 / f"engine_{name}.json"
    if tag.is_file():
        return json.loads(tag.read_text())
    old = B2.CACHE
    try:
        B2.CACHE = B6 / "engine_tmp"
        B2.CACHE.mkdir(parents=True, exist_ok=True)
        r = B2.engine(target, kw, energies)
    finally:
        B2.CACHE = old
    if "error" not in r:
        tag.write_text(json.dumps(r))
    return r


def response(name: str) -> dict:
    target, kw, st, files, *rest = decks()[name]
    es = rest[0] if rest else B2.ENERGIES
    s0, s1 = stock("", target, "", (), es), stock(name, target, st, files, es)
    e0, e1 = engine("", target, "", es), engine(name, target, kw, es)
    if "error" in e1 or "error" in e0:
        return {"name": name, "error": e1.get("error") or e0.get("error")}
    rows, worst = [], 0.0
    for ch in B2.CHANNELS:
        if not all(ch in x for x in (s0, s1, e0, e1)):
            continue
        for i, e in enumerate(s0["E"]):
            if i >= len(e0[ch]) or i >= len(s1[ch]) or i >= len(e1[ch]):
                continue
            a0, a1, b0, b1 = e0[ch][i], e1[ch][i], s0[ch][i], s1[ch][i]
            if min(b0, b1) <= 1.0 or a0 <= 0 or a1 <= 0:
                continue
            R, S = a1 / a0, b1 / b0
            dl = abs(math.log(R / S))
            rows.append(dict(ch=ch, E=e, R=R, S=S, dlog=dl))
            worst = max(worst, dl)
    moved = max((abs(math.log(r["S"])) for r in rows), default=0.0)
    absd = []  # ours(kw) vs stock(kw) on total / nonelastic (the plan's 1 % on reaction and total)
    for ch in ("total", "nonelastic"):
        for i, e in enumerate(s1.get("E") or []):
            if ch in e1 and ch in s1 and i < len(e1[ch]) and s1[ch][i] > 0:
                absd.append((ch, e, e1[ch][i] / s1[ch][i] - 1.0))
    return {"name": name, "target": target, "kw": kw, "rows": rows, "worst_dlog": worst, "stock_moved": moved,
            "abs": absd, "stock_warnings": s1.get("warnings", [])}


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "_engine_child":
        B2._engine_child(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
        return
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", action="append")
    ap.add_argument("--json")
    a = ap.parse_args()
    B6.mkdir(parents=True, exist_ok=True)
    for t in ("fe56", "u238"):  # the defaults, from B2's cache when it has them
        B2.stock(t, "")
    make_files()
    out = []
    for name in a.only or list(decks()):
        r = response(name)
        out.append(r)
        if "error" in r:
            print(f"{name}: ERROR {r['error'][-800:]}")
            continue
        print(f"{name} [{r['kw']}] worst |ln(R/S)| = {100 * r['worst_dlog']:.2f} %  (stock moved up to "
              f"{100 * r['stock_moved']:.1f} %)  {'PASS' if r['worst_dlog'] <= 0.02 else 'FAIL'}")
        for x in sorted(r["rows"], key=lambda x: -x["dlog"])[:4]:
            print(f"    {x['ch']:<10} E={x['E']:<6g} R={x['R']:.4f} S={x['S']:.4f} d={100 * x['dlog']:.2f} %")
        for w in r["stock_warnings"][:3]:
            print("    stock:", w)
        sys.stdout.flush()
    if a.json:
        Path(a.json).write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
