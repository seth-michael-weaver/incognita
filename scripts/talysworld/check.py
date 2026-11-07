#!/usr/bin/env python3
"""Check: one engine job per energy (talysworld service, library-default settings) against library v0.2.1, point by point.

usage (service running, laptop WSL python3 with pandas):
    python3 scripts/talysworld/check.py run       # submit the sample, wait (results land in the service cache)
    python3 scripts/talysworld/check.py analyze   # write check_points.csv + check_summary.json (+ tables for CHECK.md)
    python3 scripts/talysworld/check.py gridtop   # the 7 grid-dependent nuclides again, GRIDTOP-padded jobs, 15 energies
                                                  # (service started with the default TW_GRIDTOP=1) -> check_gridtop_*.{csv,json}

Sample: 20 nuclides spread over Z and A, including the six named ones and six heavy/proton-rich nuclei from the v0.2.2
short-grid mismatch list (library/v0.2.2/below1keV_engine_v022.parquet in the libv022 worktree: |junction_reldiff| > 0.5).
Energies: the library's own 64-point grid (1 keV - 20 MeV) plus three of v0.2.2's points below 1 keV (10.49, 126.0, 660.8 eV).
Library v0.2.1 = v0.2 above 1 keV (capture; ANCHORED curves divided by their anchor factor to get the engine's own value),
channels (n,p), (n,2n), (n,alpha) from channels_v021.parquet.
"""
import json, os, sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import client  # noqa: E402

SAMPLE = [(8, 16), (11, 23), (20, 40), (26, 56), (28, 62), (40, 90), (50, 120), (52, 104), (53, 109), (56, 138), (64, 158),
          (79, 197), (81, 174), (82, 208), (83, 178), (87, 190), (88, 215), (90, 232), (91, 200), (92, 238)]
SYM = {8: "O", 11: "Na", 20: "Ca", 26: "Fe", 28: "Ni", 40: "Zr", 50: "Sn", 52: "Te", 53: "I", 56: "Ba", 64: "Gd", 79: "Au", 81: "Tl",
       82: "Pb", 83: "Bi", 87: "Fr", 88: "Ra", 90: "Th", 91: "Pa", 92: "U"}
LOW = np.geomspace(2.0, 1000.0, 16); LOWPICK = [4, 10, 14]          # 10.49, 126.0, 660.8 eV
V022 = os.environ.get("TW_V022", "/mnt/c/Users/smw57/Documents/projects/incognita_libv022/library/v0.2.2/below1keV_engine_v022.parquet")
OUT = HERE
FLOOR = 1.0000001e-7   # the engine's output floor in mb (values at or below = zero)


def lib():
    C = pd.read_parquet(os.path.join(ROOT, "library/v0.2.1/capture_v021.parquet"))
    X = pd.read_parquet(os.path.join(ROOT, "library/v0.2.1/channels_v021.parquet")).set_index("nuclide_id")
    return C, X


def energies():
    C, _ = lib(); G = [float(x) for x in C.energy_ev.iloc[0]]
    return [float(LOW[i]) for i in LOWPICK] + G


def run():
    E = energies()
    import urllib.request
    ids = []
    for z, a in SAMPLE:
        body = json.dumps(dict(z=z, a=a, energies_ev=E, comp="library", kw={}, extra="")).encode()
        r = json.load(urllib.request.urlopen(urllib.request.Request("http://localhost:8765/api/run", body, {"Content-Type": "application/json"})))
        ids.append(((z, a), r)); print(z, a, r, flush=True)
    import time
    while True:
        tot = 0; left = []
        for (z, a), r in ids:
            s = json.load(urllib.request.urlopen(f"http://localhost:8765/api/run?run={r['run']}"))
            tot += len(s["points"])
            if not s["done"]: left.append(f"{SYM[z]}{a}:{len(s['points'])}/{s['n']}")
        print(time.strftime("%H:%M:%S"), "points", tot, "of", len(E) * len(SAMPLE), " ".join(left[:6]), flush=True)
        if not left: break
        time.sleep(60)
    json.dump([dict(z=z, a=a, **r) for (z, a), r in ids], open(os.path.join(OUT, "check_runs.json"), "w"), indent=0)


def rel(eng, lb):
    e = 0.0 if eng is None or eng <= FLOOR else eng; l = 0.0 if lb <= FLOOR else lb
    if e == 0 and l == 0: return 0.0
    if l == 0 or e == 0: return np.inf
    return e / l - 1


def analyze():
    C, X = lib(); E = energies(); G = E[3:]
    V = pd.read_parquet(V022).set_index("nuclide_id") if os.path.exists(V022) else None
    rows = []; per = []
    for z, a in SAMPLE:
        _, pts = client.run(z, a, E, quiet=True, poll=2)
        P = {round(p["e_ev"], 6): p for p in pts}
        r = C[(C.Z == z) & (C.A == a)].iloc[0]; n = r.nuclide_id; nm = f"{SYM[z]}-{a}"
        f = 1.0
        if r.tier == "ANCHORED":
            import re
            f = float(re.search(r"blind curve x ([0-9.]+) \(measured", r.value_source).group(1))
        lc = np.asarray(r.sigma_b, float) * 1e3 / f
        x = X.loc[n]
        libch = {"capture": lc, "np": np.asarray(x.sigma_np_mb, float), "n2n": np.asarray(x.sigma_n2n_mb, float),
                 "na": np.asarray(x.sigma_na_mb, float)}
        comp = pts[0].get("comp", "")
        errs = [p for p in pts if p.get("err")]
        for i, e in enumerate(G):
            p = P[round(e, 6)]; ch = p.get("channels") or {}
            for c, L in libch.items():
                v = ch.get(c); d = rel(v, float(L[i])) if v is not None else np.nan
                rows.append(dict(nuclide=nm, Z=z, A=a, tier=r.tier, comp=comp, channel=c, e_ev=e, library_mb=float(L[i]),
                                 onejob_mb=v, rel=d))
            for c in ("total", "elastic", "fission"):
                rows.append(dict(nuclide=nm, Z=z, A=a, tier=r.tier, comp=comp, channel=c, e_ev=e, library_mb=np.nan, onejob_mb=ch.get(c), rel=np.nan))
        # below 1 keV: one-energy jobs vs v0.2.2 engine values (16-point short grid, or long grid where rerun) and v0.2.1's 1/v
        for j in LOWPICK:
            e = float(LOW[j]); p = P[round(e, 6)]; v = (p.get("channels") or {}).get("capture")
            v22 = np.nan; g22 = ""
            if V is not None and n in V.index:
                vr = V.loc[n]; g22 = vr.grid
                if vr.status == "engine": v22 = float(np.asarray(vr.engine_mb, float)[j])
            rows.append(dict(nuclide=nm, Z=z, A=a, tier=r.tier, comp=comp, channel="capture<1keV vs v0.2.2 engine", e_ev=e,
                             library_mb=v22, onejob_mb=v, rel=rel(v, v22) if np.isfinite(v22) else np.nan))
            l11 = lc[0] * np.sqrt(1000.0 / e)
            rows.append(dict(nuclide=nm, Z=z, A=a, tier=r.tier, comp=comp, channel="capture<1keV vs v0.2.1 1/v", e_ev=e,
                             library_mb=l11, onejob_mb=v, rel=rel(v, l11)))
        jd = float(V.loc[n].junction_reldiff) if V is not None and n in V.index else np.nan
        p1 = P[round(G[0], 6)]; v1 = (p1.get("channels") or {}).get("capture")
        per.append(dict(nuclide=nm, Z=z, A=a, tier=r.tier, comp=comp, n_err=len(errs), err=errs[0]["err"][:120] if errs else "",
                        lib_1keV_mb=float(lc[0]), onejob_1keV_mb=v1, onejob_vs_lib_1keV=rel(v1, float(lc[0])),
                        shortgrid_vs_lib_1keV_v022=jd, points_repaired=int(r.engine_points_repaired or 0)))
    D = pd.DataFrame(rows); Pn = pd.DataFrame(per)
    # raw comparison, kept small: compared points only (total/elastic/fission have no library curve), per-nuclide columns in check_nuclides.csv
    D[D.rel.notna()][["nuclide", "channel", "e_ev", "library_mb", "onejob_mb", "rel"]].to_csv(
        os.path.join(OUT, "check_points.csv"), index=False, float_format="%.6g")
    Pn.to_csv(os.path.join(OUT, "check_nuclides.csv"), index=False, float_format="%.6g")
    S = {}
    for c, g in D[D.rel.notna()].groupby("channel"):
        fin = g[np.isfinite(g.rel)]; ar = fin.rel.abs()
        k = ar.idxmax() if len(ar) else None
        S[c] = dict(points=int(len(g)), zero_vs_nonzero=int((~np.isfinite(g.rel)).sum()), median_abs=float(ar.median()) if len(ar) else None,
                    max_abs=float(ar.max()) if len(ar) else None,
                    max_at=(f"{fin.loc[k, 'nuclide']} {fin.loc[k, 'e_ev']:.4g} eV" if k is not None else ""),
                    n_gt_1e6=int((ar > 1e-6).sum()), n_gt_1pct=int((ar > 0.01).sum()),
                    at_1keV_max_abs=float(fin[fin.e_ev == G[0]].rel.abs().max()) if (fin.e_ev == G[0]).any() else None,
                    above_1keV_max_abs=float(fin[fin.e_ev > G[0] * 1.0001].rel.abs().max()) if (fin.e_ev > G[0] * 1.0001).any() else None)
    # where in energy: per energy band, the max |rel| over all comparable channels on the library grid
    lg = D[D.channel.isin(["capture", "np", "n2n", "na"]) & D.rel.notna() & np.isfinite(D.rel)]
    bands = [(999, 1001, "1 keV (first grid point)"), (1001, 1e4, "1-10 keV"), (1e4, 1e5, "10-100 keV"), (1e5, 1e6, "0.1-1 MeV"),
             (1e6, 5e6, "1-5 MeV"), (5e6, 2.1e7, "5-20 MeV")]
    S["bands"] = []
    for lo, hi, lb in bands:
        b = lg[(lg.e_ev >= lo) & (lg.e_ev < hi)]
        S["bands"].append(dict(band=lb, points=int(len(b)), max_abs=float(b.rel.abs().max()) if len(b) else None,
                               n_gt_1e6=int((b.rel.abs() > 1e-6).sum()), nuclides_gt_1e6=sorted(set(b[b.rel.abs() > 1e-6].nuclide))))
    json.dump(dict(summary=S, nuclides=per), open(os.path.join(OUT, "check_summary.json"), "w"), indent=1, default=float)
    print(json.dumps(S, indent=1, default=float)); print(Pn.to_string())


# --- GRIDTOP re-check (2026-11-07): the 7 nuclides that were "grid-dependent" above, with the pad on (engine_job.py) ---
GT_SAMPLE = [(53, 109), (91, 200), (88, 215), (87, 190), (83, 178), (81, 174), (52, 104)]
GT_IDX = [0, 9, 15, 19, 25, 29, 34, 39, 44, 49, 53, 57, 59, 61, 63]   # 15 of the 64 library-grid points, 1 keV - 20 MeV


def gridtop():
    """Run (through the service, so cached points are reused) and compare with v0.2.1; the old unpadded one-point jobs are read
    from the service cache under their old key for the 'before' column."""
    import hashlib
    C, X = lib(); G = [float(x) for x in C.energy_ev.iloc[0]]; E = [G[i] for i in GT_IDX]
    data = os.environ.get("TW_DATA", os.path.expanduser("~/talysworld_data"))
    rows = []
    for z, a in GT_SAMPLE:
        info, pts = client.run(z, a, E, quiet=True, poll=10)
        assert any(p.get("gridtop") for p in pts), "service is not padding (start it with TW_GRIDTOP unset or 1)"
        P = {round(p["e_ev"], 6): p for p in pts}
        r = C[(C.Z == z) & (C.A == a)].iloc[0]; x = X.loc[r.nuclide_id]; nm = f"{SYM[z]}-{a}"
        okey = hashlib.sha256(json.dumps(["16606b356d6e", "libv02-inputs", z, a, info["comp"], ""]).encode()).hexdigest()[:16]
        libch = {"capture": np.asarray(r.sigma_b, float) * 1e3, "np": np.asarray(x.sigma_np_mb, float),
                 "n2n": np.asarray(x.sigma_n2n_mb, float), "na": np.asarray(x.sigma_na_mb, float)}
        smin = next((p["s_min_mev"] for p in pts if "s_min_mev" in p), np.nan)
        for i in GT_IDX:
            e = G[i]; p = P[round(e, 6)]; ch = p.get("channels") or {}
            of = os.path.join(data, "cache", okey, f"{e:.6e}.json")
            old = (json.load(open(of)).get("channels") or {}) if os.path.exists(of) else {}
            for c, L in libch.items():
                v = ch.get(c); lb = float(L[i]); o = old.get(c)
                rows.append(dict(nuclide=nm, s_min_mev=smin, e_cut_mev=21.0 + smin, channel=c, e_ev=e, library_mb=lb, padded_mb=v,
                                 rel=rel(v, lb) if v is not None else np.nan, onepoint_mb=o,
                                 rel_onepoint=rel(o, lb) if o is not None else np.nan, err=p.get("err", "")))
    D = pd.DataFrame(rows)
    D.to_csv(os.path.join(OUT, "check_gridtop_points.csv"), index=False, float_format="%.6g")
    S = {"energies_ev": E, "nuclides": {}, "channels": {}}

    def st(g, col):
        f = g[np.isfinite(g[col])]; ar = f[col].abs()
        return dict(n=int(len(g)), zero_vs_nonzero=int((~np.isfinite(g[col]) & g[col].notna()).sum()),
                    median_abs=float(ar.median()) if len(ar) else None, max_abs=float(ar.max()) if len(ar) else None,
                    max_at=(f"{f.loc[ar.idxmax(), 'nuclide']} {f.loc[ar.idxmax(), 'e_ev']:.4g} eV" if len(ar) else ""))
    for c, g in D.groupby("channel", sort=False):
        lo = g[g.e_ev < 1e5]; mid = g[(g.e_ev >= 1e5) & (g.e_ev <= g.e_cut_mev * 1e6)]; hi = g[g.e_ev > g.e_cut_mev * 1e6]
        S["channels"][c] = dict(all=st(g, "rel"), keV_below_100keV=st(lo, "rel"), from_100keV_to_cut=st(mid, "rel"),
                                above_cut=st(hi, "rel"), onepoint_all=st(g, "rel_onepoint"))
    for nm, g in D.groupby("nuclide", sort=False):
        cap = g[g.channel == "capture"]; npc = g[g.channel == "np"]
        S["nuclides"][nm] = dict(s_min_mev=float(g.s_min_mev.iloc[0]), e_cut_mev=float(g.e_cut_mev.iloc[0]),
                                 capture_max_abs_below_cut=float(cap[cap.e_ev <= cap.e_cut_mev * 1e6].rel.abs().max()),
                                 capture_max_abs_keV=float(cap[cap.e_ev < 1e5].rel.abs().max()),
                                 capture_max_abs_above_cut=(float(cap[cap.e_ev > cap.e_cut_mev * 1e6].rel.abs().max())
                                                            if (cap.e_ev > cap.e_cut_mev * 1e6).any() else None),
                                 capture_onepoint_max_abs=float(cap.rel_onepoint.abs().max()),
                                 np_max_abs_below_cut=float(npc[npc.e_ev <= npc.e_cut_mev * 1e6].rel.abs().max()),
                                 np_onepoint_max_abs=float(npc.rel_onepoint.abs().max()),
                                 n_err=int((g.err.fillna("") != "").sum()) // 4)
    json.dump(S, open(os.path.join(OUT, "check_gridtop_summary.json"), "w"), indent=1, default=float)
    print(json.dumps(S, indent=1, default=float))
    print(D[D.channel == "capture"][["nuclide", "e_ev", "library_mb", "padded_mb", "rel", "rel_onepoint"]].to_string())


if __name__ == "__main__":
    {"run": run, "analyze": analyze, "gridtop": gridtop}[sys.argv[1]]()
