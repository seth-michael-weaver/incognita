"""Library v0.2.2, step 1: collect the production engine's capture below 1 keV, and the target masses.

Runs where the engine runs are (WSL / Linux, the production engine's own venv), not in the plain library build:
    ~/fastgate_data/eng/16606b356d6e/.venv/bin/python scripts/release/collect_below1keV_v022.py RUNS_DIR [FULL_RUNS_DIR]

Engine runs (made for v0.2.2, 2026-11-06/07, Mac mini): engine-20261022-3 = nucleus 16606b356d6e, the environment, deck,
runner (FASTGATE worker -> prodrun, `fewres off`, `pewindow g`) and inputs of the v0.2 runs (nucleus research/rl/libv02/code/run.sh,
inputs = ~/libv02/inputs), with ONE change: the energy grid (inputs/grid134.json) gets 15 more points below 1 keV (the 16
log-spaced points np.geomspace(2, 1000, 16), 2 eV - 1 keV; RUNS_DIR: these 16 alone). Arms per nucleus as v0.2 composed it (P; A for
JS(P,A) and A(rotor); AJ = arm A with the actinide lines for ACTJS A(rotor)). RUNS_DIR/{P,A,AJ}/ZZZ_AAA.npz.
FULL_RUNS_DIR: the same runs on the 134-point production grid plus the 15 points below 1 keV (149 points, top 20.5 MeV).
Only these are used. On the short grid alone, 2,320 nuclei did not reproduce v0.2's 1 keV value (by up to a factor ~30):
the engine's outgoing-energy grid ends at E + S_n + 1 MeV, so where the compound nucleus is unbound to alpha or proton
emission, a run whose top energy is low drops the fastest alphas/protons and (with pre-equilibrium on) inflates capture
(found on branch gridfix, 2bac71aa; see BUILD.md). The short-grid values are kept only for the comparison columns
short_vs_full_maxrel_le1keV and short_grid_1keV_vs_v02_reldiff. A nucleus without a long-grid run is "engine run failed".

Composition = the v0.2 build rule (nucleus research/rl/libv02/code/build.py product()): P | A | AJ alone, or
physics.hf.jointcap.combine(P, A) for JS(P,A), from the same engine install. The composition label is read from the v0.2
value_source. Floor repair = v0.1's rule (nucleus research/docs/release/indep_fix2/repair.py), applied to the 15 low points
joined to the v0.2 curve; only low points are changed.

Writes library/v0.2.2/below1keV_engine_v022.parquet (per nucleus: composition, status, the 15 engine values in mb before any
ANCHORED scaling, the engine value at 1 keV and its relative difference from the v0.2 curve) and library/v0.2.2/masses_v022.csv
(AME2020 atomic masses, u; W.J. Huang et al., Chin. Phys. C 45 (2021) 030002, M. Wang et al., ibid. 030003).
"""
import json, os, re, sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "library", "v0.2.2")
H = os.path.expanduser("~")
ENG = f"{H}/fastgate_data/eng/16606b356d6e"
assert open(f"{ENG}/ENGINE_COMMIT").read().strip().startswith("16606b356d6e")
sys.path.insert(0, ENG); sys.path.insert(0, f"{H}/nucleus/research/docs/release/indep_fix2")
from physics.hf import jointcap as J        # noqa: E402
from repair import repair_mb                 # noqa: E402
AME = f"{H}/nucleus/raw/ame2020/mass_1.mas20.txt"
LOW = np.geomspace(2.0, 1000.0, 16); LOW[-1] = 1000.0


def cap(q):
    return np.asarray(q["capture_mb"] if "capture_mb" in q.files else q["ch_xs000000"], float)


def compose(runs, z, A, comp):
    f = f"{z:03d}_{A:03d}.npz"; base = comp.replace(" [FEW->mean]", "")
    ld = lambda k: np.load(f"{runs}/{k}/{f}", allow_pickle=True)  # noqa: E731
    if base == "P": q = ld("P"); return np.asarray(q["e_ev"], float), cap(q)
    if base == "A(rotor)": q = ld("A"); return np.asarray(q["e_ev"], float), cap(q)
    if base == "ACTJS A(rotor)": q = ld("AJ"); return np.asarray(q["e_ev"], float), cap(q)
    if base in ("JS(P,A)", "ACTJS JS(P,A)"):
        qP = ld("P"); qA = ld("A" if base == "JS(P,A)" else "AJ"); c = J.combine(qP, qA)
        return np.asarray(qP["e_ev"], float), np.asarray(c["capture_mb"], float)
    raise ValueError(comp)


def arms(comp):
    base = comp.replace(" [FEW->mean]", "")
    return {"P": ["P"], "A(rotor)": ["A"], "ACTJS A(rotor)": ["AJ"], "JS(P,A)": ["P", "A"], "ACTJS JS(P,A)": ["P", "AJ"]}[base]


def errtext(runs, z, A, comp):
    t = []
    for k in arms(comp):
        p = f"{runs}/{k}/{z:03d}_{A:03d}"
        if os.path.exists(p + ".err"): t.append(f"{k}: " + open(p + ".err").read().strip().splitlines()[-1][:200])
        elif not os.path.exists(p + ".npz"): t.append(f"{k}: no output")
    return "; ".join(t)


def ame_masses():
    m = {}
    for ln in open(AME):
        if len(ln) < 120 or not re.match(r"^[0 ]", ln[:1]): continue
        try:
            N, Z, A = int(ln[4:9]), int(ln[9:14]), int(ln[14:19])
        except ValueError:
            continue
        t = ln[106:].split()
        if len(t) < 2: continue
        est = "#" in t[1]
        m[(Z, A)] = (int(t[0]) + float(t[1].replace("#", ".")) * 1e-6, "AME2020 estimate (#)" if est else "AME2020")
    return m


def main():
    runs = sys.argv[1]; full = sys.argv[2] if len(sys.argv) > 2 else ""
    os.makedirs(OUT, exist_ok=True)
    L = pd.read_parquet(os.path.join(ROOT, "library", "v0.2", "capture_v02.parquet"),
                        columns=["nuclide_id", "Z", "A", "tier", "value_source", "energy_ev", "sigma_b"])
    rows = []
    for r in L.itertuples(index=False):
        z, A = int(r.Z), int(r.A); vs = r.value_source
        G = np.asarray(r.energy_ev, float); sb = np.asarray(r.sigma_b, float)
        row = dict(nuclide_id=r.nuclide_id, Z=z, A=A, tier=r.tier)
        if "v0.1 value carried" in vs:
            rows.append(dict(row, composition="", grid="", status="no engine run (v0.1 value carried in v0.2)", message="",
                             energy_ev=list(LOW[:-1]), engine_mb=[np.nan] * 15, engine_1keV_mb=np.nan, points_repaired=0,
                             v02_1keV_unscaled_mb=np.nan, junction_reldiff=np.nan)); continue
        comp = re.search(r"composed (.+?);", vs).group(1).strip()
        fA = 1.0
        if r.tier == "ANCHORED":
            fA = float(re.search(r"blind curve x ([0-9.]+) \(measured MACS30 anchor\)", vs).group(1))  # 3 digits; refined below
        src, grid = runs, "2 eV - 1 keV, 16 points"
        if full:  # the long grid only: short-grid values are wrong where the compound nucleus is alpha/proton-unbound (BUILD.md)
            src, grid = full, "134-point production grid + 15 points below 1 keV"
        try:
            e, c = compose(src, z, A, comp)
        except (FileNotFoundError, OSError, KeyError, ValueError) as ex:
            rows.append(dict(row, composition=comp, grid=grid, status="engine run failed", message=errtext(src, z, A, comp) or repr(ex)[:200],
                             energy_ev=list(LOW[:-1]), engine_mb=[np.nan] * 15, engine_1keV_mb=np.nan, points_repaired=0,
                             v02_1keV_unscaled_mb=np.nan, junction_reldiff=np.nan)); continue
        idx = np.array([int(np.argmin(np.abs(np.log(e / x)))) for x in LOW])
        assert np.max(np.abs(e[idx] / LOW - 1)) < 1e-9, r.nuclide_id
        c16 = c[idx]
        v02 = sb * 1e3                       # mb, v0.2 curve (ANCHORED: scaled)
        if r.tier == "ANCHORED" and np.isfinite(c16[-1]) and c16[-1] > 0:
            fA = v02[0] / c16[-1]            # the exact v0.2 factor (engine 1 keV value -> shipped)
        jd = float(c16[-1] / (v02[0] / fA) - 1) if c16[-1] > 0 else np.nan
        # floor repair on the low points joined to the (unscaled) v0.2 curve; keep v0.2's points as they are
        x = np.r_[LOW[:-1], G]; y = np.r_[c16[:-1], v02 / fA]
        rep, nbad, ok = repair_mb(y, x)
        nlow = int(np.sum(np.abs(rep[:15] - np.where(np.isfinite(c16[:-1]), c16[:-1], -1)) > 0))
        status = "engine" if ok and np.all(np.isfinite(rep[:15])) and np.all(rep[:15] > 0) else "engine values unusable"
        extra = {}
        if src == full:  # the long-grid run also reproduces v0.2 above 1 keV: check every grid point (repaired points show up)
            ig = np.array([int(np.argmin(np.abs(np.log(e / x)))) for x in G]); assert np.max(np.abs(e[ig] / G - 1)) < 1e-9
            d = np.abs(c[ig] / (v02 / fA) - 1)
            extra = dict(full_vs_v02_maxrel_ge1keV=float(np.max(d)), full_vs_v02_points_gt1e9=int(np.sum(d > 1e-9)))
            try:
                es, cs = compose(runs, z, A, comp)
                js = np.array([int(np.argmin(np.abs(np.log(es / x)))) for x in LOW]); extra["short_vs_full_maxrel_le1keV"] = float(np.max(np.abs(cs[js] / c16 - 1)))
                # the short-grid run's 1 keV value against v0.2 (> 1e-9: the engine value depends on the other energies in the run)
                extra["short_grid_1keV_vs_v02_reldiff"] = float(cs[js[-1]] / (v02[0] / fA) - 1)
            except (FileNotFoundError, OSError, KeyError, ValueError):
                extra["short_vs_full_maxrel_le1keV"] = np.nan; extra["short_grid_1keV_vs_v02_reldiff"] = np.nan
        rows.append(dict(row, composition=comp, grid=grid, status=status, message="", energy_ev=list(LOW[:-1]),
                         engine_mb=list(rep[:15]), engine_1keV_mb=float(c16[-1]), points_repaired=nlow,
                         v02_1keV_unscaled_mb=float(v02[0] / fA), junction_reldiff=jd, anchored_v02_factor=fA if r.tier == "ANCHORED" else np.nan,
                         **extra))
    D = pd.DataFrame(rows)
    D.to_parquet(os.path.join(OUT, "below1keV_engine_v022.parquet"), index=False)
    M = ame_masses(); mm = []
    for r in L.itertuples(index=False):
        v = M.get((int(r.Z), int(r.A)))
        mm.append(dict(nuclide_id=r.nuclide_id, Z=int(r.Z), A=int(r.A), mass_u=v[0] if v else float(r.A),
                       mass_source=v[1] if v else "not in AME2020: mass number A (u)"))
    pd.DataFrame(mm).to_csv(os.path.join(OUT, "masses_v022.csv"), index=False, float_format="%.9f")
    print(D.status.value_counts().to_string()); print(D.grid.value_counts().to_string())
    j = D.junction_reldiff.abs()
    print("junction |rel diff|: n", int(j.notna().sum()), "max", j.max(), ">1e-9:", int((j > 1e-9).sum()), ">1e-6:", int((j > 1e-6).sum()))
    print(D.loc[j > 1e-9, ["nuclide_id", "composition", "grid", "junction_reldiff"]].sort_values("junction_reldiff").to_string())
    print("points repaired", int(D.points_repaired.sum()), "nuclei", int((D.points_repaired > 0).sum()))
    if "full_vs_v02_maxrel_ge1keV" in D:
        F = D[D.full_vs_v02_maxrel_ge1keV.notna()]
        print("long-grid reruns", len(F), "reproduce v0.2 >= 1 keV: max", F.full_vs_v02_maxrel_ge1keV.max(), "nuclei with points > 1e-9:",
              int((F.full_vs_v02_points_gt1e9 > 0).sum()), "short vs long below 1 keV: median", F.short_vs_full_maxrel_le1keV.median(),
              "max", F.short_vs_full_maxrel_le1keV.max())
        print(F.loc[F.full_vs_v02_points_gt1e9 > 0, ["nuclide_id", "composition", "full_vs_v02_maxrel_ge1keV", "full_vs_v02_points_gt1e9"]].to_string())
    print(pd.DataFrame(mm).mass_source.value_counts().to_string())


if __name__ == "__main__":
    main()
