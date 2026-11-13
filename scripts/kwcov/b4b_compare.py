#!/usr/bin/env python3
"""KWCOV B4b acceptance: exclusive channel spectra sp<nnnnnn>.tot / .fis of the engine (physics/hf/exclspec.py) vs a
stock TALYS-2.25 run (scripts/kwcov/b4b_stock.sh, ~/kwcov/stock/b4b/<deck>).

    python scripts/kwcov/b4b_compare.py --z 26 --a 56 --stock ~/kwcov/stock/b4b/fe56 [--mode talys|default]
                                        [--kw "endf y"] [--frac 0.01] [--json out.json] [--write DIR] [--onoff]

Engine in TALYS mode by default (fidelity.py's TALYS_DECK / TALYS_ENV: `INCOGNITA_NPWINDOW` etc. change the 14 MeV channels) with
`outspectra y; channels y` + --kw. Per channel file and energy and ejectile column: the integral ratio (ours / stock),
the worst |ours/stock - 1| over the MAIN bins (stock >= --frac x the column's peak), the same after normalising both to
their integrals (shape), and the channel cross section ratio (xs*.tot) the spectrum carries. `--onoff` also runs the
engine without the keywords and checks every Results array other than the spectra is bitwise the same.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts" / "kwcov"))

PARSYM = "gnpdtha"


def read_cols(path: Path) -> np.ndarray:
    rows = [ln.split() for ln in path.read_text().splitlines() if ln.strip() and not ln.lstrip().startswith("#")]
    return np.array([[float(x) for x in r] for r in rows]) if rows else np.zeros((0, 0))


def read_blocks(path: Path) -> dict:
    """{E-incident: rows} of a TALYS file with one block per energy (block names, endf y) or a single block."""
    out, cur, e = {}, [], None
    for ln in path.read_text().splitlines():
        if "E-incident [MeV]" in ln:
            if e is not None and cur:
                out[e] = np.array(cur)
            e, cur = float(ln.split(":")[1]), []
        elif ln.strip() and not ln.lstrip().startswith("#"):
            cur.append([float(x) for x in ln.split()])
    if e is not None and cur:
        out[e] = np.array(cur)
    return out


def efile(e: float) -> str:
    e32 = float(np.float32(e))
    return f"{int(e32):04d}{f'{e32:8.3f}'[4:]}"


def stock_spectra(d: Path) -> dict:
    """{(name, E): rows} for sp*.tot / sp*.fis of a stock directory (E-named or block files)."""
    out = {}
    for p in sorted(d.glob("sp??????*")):
        nm = p.name
        kind = nm.rsplit(".", 1)[1]
        if kind not in ("tot", "fis"):
            continue
        for e, rows in read_blocks(p).items():
            out[(f"{nm[:8]}.{kind}", round(e, 4))] = rows
    return out


def stock_xs(d: Path) -> dict:
    out = {}
    for p in d.glob("xs??????.tot"):
        r = read_cols(p)
        for row in r:
            out[(p.name[2:8], round(row[0], 4))] = row[1]
    return out


def engine_run(Z: int, A: int, energies, kw: str, env: dict):
    import torch

    from physics.hf import engine_c, warmrun
    from physics.hf.chartrun import drop_target_caches
    from physics.hf.engine import ChainedFull
    from physics.hf.input import fitlib

    saved = {k: os.environ.get(k) for k in env}
    os.environ.update(env)
    if kw:
        os.environ["INCOGNITA_TALYS_FIT"] = "lines"
        os.environ["INCOGNITA_TALYS_FIT_LINES"] = kw
    drop_target_caches()
    try:
        with torch.inference_mode():
            r = engine_c.run(ChainedFull(Z=Z, A=A, declared_energies=tuple(energies)))
    finally:
        os.environ.pop("INCOGNITA_TALYS_FIT", None)
        os.environ.pop("INCOGNITA_TALYS_FIT_LINES", None)
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        fitlib.deactivate()
        drop_target_caches()
    return r, warmrun.result_arrays(r)


def compare(res, stock: dict, sxs: dict, frac: float) -> list[dict]:
    sp = {k: v.numpy() for k, v in (res.spectra or {}).items()}
    E = res.e_inc_mev.numpy()
    xs = {k[2:]: v.numpy() for k, v in res.channels_mb.items()}
    rows = []
    names = sorted({n for n, _ in stock} | {k.rsplit(":", 1)[0] for k in sp if k.startswith("sp")})
    for name in names:
        for i, e in enumerate(E):
            st = stock.get((name, round(float(e), 4)))
            ours_e = sp.get(name + ":E")
            have = ours_e is not None and np.isfinite(ours_e[i]).any()
            if st is None and not have:
                continue
            row = dict(file=name, E=float(e), stock=st is not None, ours=bool(have))
            code = name[2:8]
            row["xs_ratio"] = (float(xs[code][i]) / sxs[(code, round(float(e), 4))]
                               if (code in xs and (code, round(float(e), 4)) in sxs and sxs[(code, round(float(e), 4))])
                               else None)
            if st is None or not have:
                rows.append(row)
                continue
            m = np.isfinite(ours_e[i])
            oe = ours_e[i][m]
            row["grid"] = bool(len(oe) == len(st) and np.allclose(oe, st[:, 0], rtol=2e-6, atol=1e-7))
            cols = {}
            for t, x in enumerate(PARSYM):
                o = sp[f"{name}:{x}"][i][m]
                s = st[:, t + 1]
                if len(o) != len(s) or s.max() <= 0:
                    if s.max() > 0 or (len(o) and np.nanmax(o) > 0):
                        cols[x] = dict(note="grid/len mismatch" if len(o) != len(s) else "stock zero",
                                       ours_max=float(np.nanmax(o)) if len(o) else 0.0)
                    continue
                de = np.gradient(st[:, 0])
                si, oi = float((s * de).sum()), float((o * de).sum())
                main = s >= frac * s.max()
                r = o[main] / s[main]
                sh = (o[main] / oi) / (s[main] / si) if oi > 0 else r * np.nan
                k = int(np.argmax(np.abs(r - 1)))
                cols[x] = dict(integral=oi / si, worst=float(np.max(np.abs(r - 1))),
                               worst_E=float(st[main, 0][k]), shape=float(np.max(np.abs(sh - 1))),
                               stock_int=si, nmain=int(main.sum()))
            row["cols"] = cols
            rows.append(row)
    return rows


def compare_components(res, d: Path) -> list[dict]:
    """components y: xs*.tot columns 5-7 and rp*.tot columns 3-5 (stock) vs Results.extras (mb); |ours/stock - 1| on
    entries > 1e-3 x the file's column-2 value (and > 1e-6 mb)."""
    ex = {k: v.numpy() for k, v in (res.extras or {}).items()}
    E = res.e_inc_mev.numpy()
    out = []
    for p in sorted(list(d.glob("xs??????.tot")) + list(d.glob("rp??????.tot"))):
        r = read_cols(p)
        if r.size == 0 or r.shape[1] < 5:
            continue
        stem = p.name[:8]
        c0 = 4 if stem.startswith("xs") else 2
        for row in r:
            i = np.flatnonzero(np.abs(E - row[0]) < 1e-6)
            if i.size == 0:
                continue
            i = int(i[0])
            for j, name in enumerate(("direct", "preeq", "compound")):
                sv = row[c0 + j]
                ov = ex.get(f"{stem}.tot:{name}")
                ov = float(ov[i]) if ov is not None else float("nan")
                if sv > max(1e-3 * row[1], 1e-6) or ov > max(1e-3 * row[1], 1e-6):
                    out.append(dict(file=stem, E=float(row[0]), col=name, stock=float(sv), ours=ov,
                                    ratio=ov / sv if sv else float("inf"), total=float(row[1])))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--z", type=int, required=True)
    ap.add_argument("--a", type=int, required=True)
    ap.add_argument("--stock", required=True)
    ap.add_argument("--mode", default="talys")
    ap.add_argument("--kw", default="")
    ap.add_argument("--frac", type=float, default=0.01)
    ap.add_argument("--json")
    ap.add_argument("--write")
    ap.add_argument("--onoff", action="store_true")
    a = ap.parse_args()
    from fidelity import mode_args

    deck, env = mode_args(a.mode)
    sdir = Path(os.path.expanduser(a.stock))
    ef = sdir / "energies"
    if ef.exists():
        energies = [float(x) for x in ef.read_text().split()]
    else:
        energies = [float(ln.split()[1]) for ln in (sdir / "talys.inp").read_text().splitlines()
                    if ln.startswith("energy ")]
    kw = ";".join(x for x in [deck, "outspectra y;channels y", a.kw] if x)
    if a.write:
        env = {**env, "INCOGNITA_SPECOBS_DIR": a.write}
    res, arrs = engine_run(a.z, a.a, energies, kw, env)
    rows = compare(res, stock_spectra(sdir), stock_xs(sdir), a.frac)
    comp = compare_components(res, sdir) if "components y" in (sdir / "talys.inp").read_text() else []
    meta = __import__("physics.hf.specobs", fromlist=["META"]).META.get("exclspec", {})
    out = dict(target=f"{a.z}-{a.a}", stock=str(sdir), kw=kw, mode=a.mode, rows=rows,
               errors=meta.get("errors", []) if isinstance(meta, dict) else [])
    if a.onoff:
        base = ";".join(x for x in [deck, a.kw.replace("outspectra y", "")] if x)
        _, arr0 = engine_run(a.z, a.a, energies, base, {k: v for k, v in env.items() if k != "INCOGNITA_SPECOBS_DIR"})
        diff = [k for k in arr0 if k in arrs and not np.array_equal(np.asarray(arr0[k]), np.asarray(arrs[k]),
                                                                       equal_nan=True)]
        missing = [k for k in arr0 if k not in arrs]
        out["onoff"] = dict(n=len(arr0), differ=diff[:20], ndiff=len(diff), missing=missing[:20])
    worst = []
    for r in rows:
        for x, c in (r.get("cols") or {}).items():
            if "worst" in c and c["stock_int"] > 0.01:
                worst.append((c["worst"], r["file"], r["E"], x, c["integral"], c["shape"], r.get("xs_ratio")))
            elif "note" in c:
                print(f"  {r['file']} E={r['E']:g} {x}: {c}")
        if not (r["stock"] and r["ours"]):
            print(f"  {r['file']} E={r['E']:g}: stock={r['stock']} ours={r['ours']} xs_ratio={r.get('xs_ratio')}")
    worst.sort(reverse=True)
    print(f"{out['target']} {a.mode} kw={a.kw!r}: {len(rows)} file-energies, errors={out['errors']}")
    for w in worst[:25]:
        print(f"  worst {w[0]:.4f} {w[1]} E={w[2]:g} {w[3]} integral={w[4]:.4f} shape={w[5]:.4f} xs_ratio={w[6]}")
    out["components"] = comp
    if comp:
        bad = sorted(comp, key=lambda c: -abs(c["ratio"] - 1) if np.isfinite(c["ratio"]) else -1e9)
        print(f"  components: {len(comp)} entries, worst:")
        for c in bad[:12]:
            print(f"    {c['file']} E={c['E']:g} {c['col']}: ours {c['ours']:.6g} stock {c['stock']:.6g} "
                  f"ratio {c['ratio']:.4f} (total {c['total']:.4g})")
    if "onoff" in out:
        print("  onoff:", out["onoff"])
    if a.json:
        Path(a.json).write_text(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
