#!/usr/bin/env python3
"""KWCOV B4 acceptance: emission spectra, DDX, discrete gamma lines and xsngn of the engine (physics/hf/specobs.py) vs a
stock TALYS-2.25 run.

    python scripts/kwcov/b4_compare.py --z 26 --a 56 --stock ~/kwcov/stock/b4_fe56 [--proj n] [--floor 1.0]
                                       [--kw "outspectra y;ddxmode 3;..."] [--onoff] [--write DIR] [--json out.json]

The stock directory holds TALYS's own files for the same target and energies (`energies`, the deck in `talys.inp`
with `outspectra y`, `ddxmode 3`, `fileddxa`, `fileddxe`, `outgamdis y`, `filegamdis y`, `filechannels y`). Per
ejectile and energy: the energy integral of the spectrum (ours / stock), the largest |ours/stock - 1| per bin where stock
> --floor mb/MeV on the egrid part of espec (absolute and after normalising both to their integrals = shape), the same for
the DDX at each fileddxa angle (mb/MeV/sr, floor / 10) and the fileddxe angular distributions, Eaverage, the gamma lines
of the target nucleus, and the (n,gx) column xsngn of <k0><x>.tot. `--onoff` also runs the engine with the switches
off and checks every Results array is the same.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

KW_DEFAULT = ("outspectra y;ddxmode 3;fileddxa n,30,90,150,p,30,90,150;fileddxe n,3.0,p,6.0;outgamdis y")


def read_cols(path: Path) -> np.ndarray:
    rows = [ln.split() for ln in path.read_text().splitlines() if ln.strip() and not ln.lstrip().startswith("#")]
    return np.array([[float(x) for x in r] for r in rows]) if rows else np.zeros((0, 0))


def efile(e: float) -> str:
    e32 = float(np.float32(e))
    return f"{int(e32):04d}{f'{e32:8.3f}'[4:]}"


def engine_run(Z: int, A: int, energies, kw: str | None):
    import torch

    from physics.hf import engine_c, warmrun
    from physics.hf.chartrun import drop_target_caches
    from physics.hf.engine import ChainedFull
    from physics.hf.input import fitlib

    if kw:
        os.environ["INCOGNITA_TALYS_FIT"] = "lines"
        os.environ["INCOGNITA_TALYS_FIT_LINES"] = kw
    else:
        os.environ.pop("INCOGNITA_TALYS_FIT", None)
        os.environ.pop("INCOGNITA_TALYS_FIT_LINES", None)
    drop_target_caches()
    try:
        with torch.inference_mode():
            r = engine_c.run(ChainedFull(Z=Z, A=A, declared_energies=tuple(energies)))
    finally:
        os.environ.pop("INCOGNITA_TALYS_FIT", None)
        os.environ.pop("INCOGNITA_TALYS_FIT_LINES", None)
        fitlib.deactivate()
        drop_target_caches()
    return r, warmrun.result_arrays(r)


def _bins(ours_e, ours, st, floor):
    """(integral ratio, worst abs, worst shape) on the stock rows whose energy is on our grid."""
    m = np.isfinite(ours_e)
    oe, ov = ours_e[m], ours[m]
    idx = np.searchsorted(oe, st[:, 0])
    idx = np.clip(idx, 0, oe.size - 1)
    hit = np.abs(oe[idx] - st[:, 0]) <= 1e-4 * np.maximum(1.0, st[:, 0])
    o, s = ov[idx][hit], st[hit, 1]
    ok = s > floor
    if not ok.any():
        return None, None, None, 0
    r = o[ok] / s[ok]
    io = np.trapezoid(ov, oe) if oe.size > 1 else 0.0
    is_ = np.trapezoid(st[:, 1], st[:, 0]) if st.shape[0] > 1 else 0.0
    shape = r / (io / is_) if is_ > 0 and io > 0 else r
    return (io / is_ if is_ else None), float(np.abs(r - 1).max()), float(np.abs(shape - 1).max()), int(ok.sum())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--z", type=int, required=True)
    ap.add_argument("--a", type=int, required=True)
    ap.add_argument("--stock", required=True)
    ap.add_argument("--proj", default="n")
    ap.add_argument("--floor", type=float, default=1.0)
    ap.add_argument("--kw", default=KW_DEFAULT)
    ap.add_argument("--onoff", action="store_true")
    ap.add_argument("--write", default="")
    ap.add_argument("--json", default="")
    ap.add_argument("--save", default="", help="also save Results.spectra as an npz")
    a = ap.parse_args()
    if a.proj != "n":
        os.environ["INCOGNITA_CPINC"] = a.proj
    d = Path(os.path.expanduser(a.stock))
    energies = [float(np.float32(float(x))) for x in (d / "energies").read_text().split()]
    if a.write:
        os.environ["INCOGNITA_SPECOBS_DIR"] = a.write
    res, arr_on = engine_run(a.z, a.a, energies, a.kw)
    os.environ.pop("INCOGNITA_SPECOBS_DIR", None)
    sp = {k: v.numpy() for k, v in res.spectra.items()}
    if a.save:
        np.savez_compressed(a.save, **sp)
    from physics.hf import specobs

    report = {"approx": specobs.META.get("approx", []), "rows": []}
    if a.onoff:
        _, arr_off = engine_run(a.z, a.a, energies, None)
        bad = [k for k in arr_off if k not in arr_on or not np.array_equal(arr_off[k], arr_on[k])]
        report["onoff"] = {"arrays": len(arr_off), "differ": bad + [k for k in arr_on if k not in arr_off]}
        print(f"on/off: {len(arr_off)} arrays, differing: {report['onoff']['differ']}")
    k0 = a.proj
    worst = {}

    def note(kind, v):
        if v is not None:
            worst[kind] = max(worst.get(kind, 0.0), v)

    for i, e in enumerate(energies):
        for x in "gnpdtha":
            f = d / f"{x}spec{efile(e)}.tot"
            stem = f"{x}spec.tot"
            if not f.is_file():
                if stem in sp and np.isfinite(sp[stem][i]).any():
                    print(f"{stem} E={e:g}: engine has a spectrum, stock none")
                continue
            st = read_cols(f)
            if stem not in sp or not np.isfinite(sp[stem][i]).any():
                print(f"{stem} E={e:g}: missing in engine output")
                report["rows"].append({"name": stem, "e": e, "missing": True})
                continue
            oe = sp[stem + ":E"][i]
            row = {"name": stem, "e": e}
            row["integral"], row["abs"], row["shape"], row["n"] = _bins(oe, sp[stem][i], st, a.floor)
            for c, j in (("compound", 5), ("preeq", 3)):
                r_ = _bins(oe, sp[f"{stem}:{c}"][i], st[:, [0, j]], a.floor)
                row[c] = r_[1]
            row["rows"] = [int(st.shape[0]), int(np.isfinite(oe).sum())]
            row["egrid_match"] = bool(st.shape[0] == np.isfinite(oe).sum() and
                                      np.abs(st[:, 0] - oe[np.isfinite(oe)]).max() <= 1e-4 * max(1.0, st[-1, 0]))
            ea = sp.get(f"Eaverage_{x}.out")
            hdr = f.read_text()
            mm = re.search(r"E-average \[MeV\]:\s*(\S+)", hdr)
            if ea is not None and mm:
                row["Eaverage"] = [float(ea[i]), float(mm.group(1))]
            if x in "np" and row["integral"] is not None:
                note(f"{x} integral", abs(row["integral"] - 1))
            print(f"{stem:10s} E={e:6.2f} rows {row['rows']} grid {row['egrid_match']}  integral {row['integral']}  "
                  f"abs {row['abs']}  shape {row['shape']} (n={row['n']})  comp {row['compound']}  pe {row['preeq']}  "
                  f"Eav {row.get('Eaverage')}")
            report["rows"].append(row)
            # DDX at the fileddxa angles
            for g in sorted(d.glob(f"{x}ddxE{efile(e)}A*.deg")):
                name = f"{x}ddx{g.name[len(x) + 3 + 9:]}"
                if name not in sp:
                    print(f"{name} E={e:g}: missing")
                    continue
                sd = read_cols(g)
                r_ = _bins(oe, sp[name][i], sd, a.floor / 10)
                rr = {"name": name, "e": e, "integral": r_[0], "abs": r_[1], "shape": r_[2], "n": r_[3]}
                print(f"  {name:16s} integral {r_[0]}  abs {r_[1]}  shape {r_[2]} (n={r_[3]})")
                report["rows"].append(rr)
            for g in sorted(d.glob(f"{x}ddxE{efile(e)}E*.MeV")):
                name = f"{x}ddx{g.name[len(x) + 3 + 9:]}"
                if name not in sp:
                    print(f"{name} E={e:g}: missing")
                    continue
                sd = read_cols(g)
                ok = sd[:, 1] > a.floor / 100
                if ok.any():
                    r = sp[name][i][ok] / sd[ok, 1]
                    rr = {"name": name, "e": e, "abs": float(np.abs(r - 1).max()),
                          "shape": float(np.abs(r / np.median(r) - 1).max()), "n": int(ok.sum())}
                    print(f"  {name:16s} abs {rr['abs']:.4f}  shape {rr['shape']:.4f} (n={rr['n']})")
                    report["rows"].append(rr)
    # discrete gamma lines (target nucleus) and xsngn
    for g in sorted(d.glob("gam*.tot")):
        name = g.name
        st = read_cols(g)
        if name not in sp:
            if st[:, 1].max() > a.floor:
                print(f"{name}: missing (stock max {st[:, 1].max():.4g} mb)")
                report["rows"].append({"name": name, "missing": True, "stock_max": float(st[:, 1].max())})
            continue
        ours = sp[name]
        ok = st[:, 1] > a.floor
        if ok.any():
            r = ours[ok] / st[ok, 1]
            rr = {"name": name, "abs": float(np.abs(r - 1).max()), "ours": ours.tolist(), "stock": st[:, 1].tolist()}
            report["rows"].append(rr)
            if name.endswith("L01L00.tot") or rr["abs"] > 0.05:
                print(f"{name}: ours {np.round(ours, 4).tolist()} stock {np.round(st[:, 1], 4).tolist()}  abs {rr['abs']:.4f}")
            note("gamma lines > floor", rr["abs"])
    for x in "gnpdtha":
        g = d / f"{k0}{x}.tot"
        if not g.is_file():
            continue
        st = read_cols(g)
        if st.shape[1] < 5:
            continue
        name = f"{k0}{x}.tot:ngn"
        ours = sp.get(name, np.zeros(len(energies)))
        print(f"{name}: ours {np.round(ours, 5).tolist()} stock {np.round(st[:, 4], 5).tolist()}")
        report["rows"].append({"name": name, "ours": np.asarray(ours).tolist(), "stock": st[:, 4].tolist()})
    report["worst"] = worst
    print("worst:", json.dumps(worst))
    if report["approx"]:
        print("approximations:", *report["approx"][:20], sep="\n  ")
    if a.json:
        Path(a.json).write_text(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
