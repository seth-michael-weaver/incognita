#!/usr/bin/env python3
"""README "Measure these next": regenerate MEASURE_NEXT.csv from the frozen inputs (docs/release/exam/measure_next_inputs.parquet,
sigma_extrap.json). Candidates: Z 26-83 ground states with no scored capture data and no measured MACS, a makeable target
(stable or t1/2 >= 1 d), all 8 engine models > 1e-3 mb at 30 keV, no EXFOR Maxwellian-average entry; ranked by the calibrated
EXTRAPOLATED-tier 68 % half-width at 30 keV. Ported from the development tree: scripts/release/measure_next.py (same arithmetic).
    python scripts/release/measure_next.py docs/release/exam OUT.csv"""
import json, sys
import numpy as np, pandas as pd
D = sys.argv[1]; X = pd.read_parquet(D + "/measure_next_inputs.parquet"); par = json.load(open(D + "/sigma_extrap.json"))
MODELS = ["s8l1", "s8l2", "s8l5", "s8l7", "s9l1", "s9l2", "s9l5", "s9l7"]; ANCH_H68 = 0.054
BRANCH = {(28, 63), (34, 79), (36, 85), (40, 93), (40, 95), (41, 94), (43, 99), (55, 134), (55, 135), (61, 147), (62, 151), (63, 154), (63, 155),
          (64, 153), (67, 163), (69, 170), (69, 171), (72, 181), (74, 185), (75, 186), (76, 185), (77, 192), (81, 204), (82, 205), (48, 113), (60, 147), (68, 169)}
SYM = ("H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn Ga Ge As Se Br Kr Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe "
       "Cs Ba La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf Ta W Re Os Ir Pt Au Hg Tl Pb Bi").split()


def h68(sp, e):   # extrap_sigma.half_width, EXTRAPOLATED tier with D0 inflation
    s = np.sqrt(np.asarray(sp) ** 2 + par["s0"] ** 2); q = np.where(np.asarray(e) < 1e5, par["q_lt100keV"][0], par["q_ge100keV"][0])
    return par["d0_inflation"] * q * s


measured = set(zip(X.Z[X.measured], X.A[X.measured]))
rows = []
for r in X.itertuples():
    z, a = int(r.Z), int(r.A); v = np.array([getattr(r, f"c30_{m}") for m in MODELS])
    if not (26 <= z <= 83) or not np.all(np.isfinite(v)) or r.measured: continue
    if np.any(v <= 1e-3): continue
    t = r.halflife_s
    if not np.isfinite(t) and not np.isinf(t): continue
    if t < 86400 or r.exfor_mxw: continue
    iso = [aa for (zz, aa) in measured if zz == z]; dn = min(abs(a - aa) for aa in iso) if iso else 99
    rows.append(dict(target=f"{SYM[z - 1]}-{a}", Z=z, A=a, half_life="stable" if np.isinf(t) else (f"{t / 3.156e7:.3g} y" if t >= 3.156e7 else f"{t / 86400:.3g} d"),
                     access="stable" if np.isinf(t) else ("long-lived (>= 1 y)" if t >= 3.156e7 else "short-lived (1 d - 1 y)"),
                     spread_30keV=float(v.max() / v.min()), h68_30keV=float(h68(np.array([np.std(np.log10(v))]), [3e4])[0]), median_macs_mb=float(np.median(v)),
                     n_to_measured=dn, s_branch=(z, a) in BRANCH))
R = pd.DataFrame(rows); R["unc68_factor"] = 10 ** R.h68_30keV; R["anchored_factor"] = 10 ** np.sqrt(ANCH_H68 ** 2 + np.log10(1.1) ** 2)
R["gain"] = R.h68_30keV - np.log10(R.anchored_factor); R = R.sort_values("h68_30keV", ascending=False)
R.to_csv(sys.argv[2], index=False); print(len(R), "candidates ->", sys.argv[2])
