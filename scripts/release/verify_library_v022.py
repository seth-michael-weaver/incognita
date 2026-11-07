"""Independent checks of library v0.2.2 (writes library/v0.2.2/VERIFY_V022.json).

1. MACS and rates recomputed for 12 nuclides by a different method from the build: the integral over the CENTRE-OF-MASS
   energy (the build integrates over lab energy and converts), a 400,000-point trapezoid in ln E from 1e-6 eV, sigma looked
   up at E_lab = E (M + m_n)/M on the joined curve (the 15 shipped points below 1 keV + the 64-point grid; 1/v below 2 eV);
   the reduced mass recomputed from the shipped target mass. Must agree with macs_kt_v022.csv / rates_v022.csv to < 1e-6.
2. Closed forms through the build's macs_cm on the joined grid (2 eV - 20 MeV): a 1/v cross section gives
   MACS = sigma(E_lab = kT (M+m_n)/M); a constant one gives the incomplete-gamma expression.
3. Reduced mass: every rate equals N_A MACS sqrt(2 kT / mu) with mu = m_n M/(m_n+M) (< 1e-12); the v0.2.1 formula
   mu = A/(A+1) u is smaller by 1.00866 (A+1)/(A+1.00866) for M = A u, the size of the v0.2.1 error.
4. Below 1 keV: where the source is the engine, the shipped values equal the collected engine values (scaled to the 1 keV
   value of the curve; ANCHORED keep their factor) and join the curve at 1 keV; where it is 1/v, sigma = sigma(1 keV)
   sqrt(1 keV/E). The long-grid engine reruns reproduce v0.2 above 1 keV.
5. Files: same nuclides and tiers as v0.2; non-ANCHORED curves (1 keV - 20 MeV) and all bands identical to v0.2; channels and
   (n,p) grid byte-identical to v0.2; ANCHORED MACS30 equals the v0.2 anchor; every MACS, rate and share finite and in range.
6. Against KADoNiS on the MEASURED tier (descriptive; read from KADONIS_TSV when present).

usage (pandas, pyarrow, scipy):  python scripts/release/verify_library_v022.py
"""
import hashlib, importlib.util, json, os

import numpy as np
import pandas as pd
from scipy.special import gammainc, gamma as gfun

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
V2, V21, V22 = (os.path.join(ROOT, "library", v) for v in ("v0.2", "v0.2.1", "v0.2.2"))
KTS = [5, 8, 10, 15, 20, 25, 30, 40, 50, 60, 80, 100]
PICK = ["Z008N008M0", "Z011N012M0", "Z012N012M0", "Z020N020M0", "Z026N030M0", "Z028N034M0", "Z040N050M0", "Z056N082M0",
        "Z079N118M0", "Z082N126M0", "Z092N146M0", "Z055N080M0"]  # O-16 Na-23 Mg-24 Ca-40 Fe-56 Ni-62 Zr-90 Ba-138 Au-197 Pb-208 U-238 Cs-135 (ANCHORED)
MN = 1.00866491590


def macs_indep(el, sl, M, kt):
    """CM-energy trapezoid; sigma(E_lab) log-log on the joined grid, 1/v below its first point."""
    g = np.exp(np.linspace(np.log(1e-6), np.log(el[-1] * M / (M + MN)), 400_001))
    e = g * (M + MN) / M
    ls = np.where(e < el[0], np.log(sl[0]) + 0.5 * (np.log(el[0]) - np.log(e)), np.interp(np.log(e), np.log(el), np.log(sl)))
    f = np.exp(ls) * g * np.exp(-g / kt) * g
    return 2 / np.sqrt(np.pi) * np.trapezoid(f, np.log(g)) / kt ** 2


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    spec = importlib.util.spec_from_file_location("b", os.path.join(ROOT, "scripts", "release", "build_library_v022.py"))
    B = importlib.util.module_from_spec(spec); spec.loader.exec_module(B)
    C2 = pd.read_parquet(os.path.join(V2, "capture_v02.parquet")).set_index("nuclide_id")
    C = pd.read_parquet(os.path.join(V22, "capture_v022.parquet")).set_index("nuclide_id")
    K = pd.read_csv(os.path.join(V22, "macs_kt_v022.csv")).set_index("nuclide_id")
    M1 = pd.read_csv(os.path.join(V22, "macs30_v022.csv")).set_index("nuclide_id")
    M2 = pd.read_csv(os.path.join(V2, "macs30_v02.csv")).set_index("nuclide_id")
    R = pd.read_csv(os.path.join(V22, "rates_v022.csv")).set_index("nuclide_id")
    R21 = pd.read_csv(os.path.join(V21, "rates_v021.csv")).set_index("nuclide_id")
    K21 = pd.read_csv(os.path.join(V21, "macs_kt_v021.csv")).set_index("nuclide_id")
    E = pd.read_parquet(os.path.join(V22, "below1keV_engine_v022.parquet")).set_index("nuclide_id")
    MS = pd.read_csv(os.path.join(V22, "masses_v022.csv")).set_index("nuclide_id")
    out = {"independent_recompute": []}
    worst = 0.0
    joined = lambda n: (np.r_[np.asarray(C.at[n, "energy_below1keV_ev"], float), np.asarray(C.at[n, "energy_ev"], float)],  # noqa: E731
                        np.r_[np.asarray(C.at[n, "sigma_below1keV_b"], float), np.asarray(C.at[n, "sigma_b"], float)])
    for n in PICK:
        el, sl = joined(n); M = float(R.at[n, "target_mass_u"]); A = int(C.at[n, "A"])
        row = dict(nuclide_id=n, A=A, tier=C.at[n, "tier"], below1keV_source=C.at[n, "below1keV_source"])
        for k in KTS:
            m = macs_indep(el, sl, M, k * 1e3) * 1e3; d = abs(K.at[n, f"macs{k}_mb"] / m - 1); worst = max(worst, d); row[f"macs{k}_relerr"] = d
        mu = MN * M / (MN + M)
        for t in (0.01, 0.03, 0.1, 0.3, 1.0, 5.0):
            kt = t * B.KB_EV_PER_GK
            rt = B.NA * macs_indep(el, sl, M, kt) * 1e-24 * B.C_CM_S * np.sqrt(2 * kt / (mu * B.U_EV))
            d = abs(R.at[n, f"rate_T9_{t:g}"] / rt - 1); worst = max(worst, d); row[f"rate_T9_{t:g}_relerr"] = d
        for k in (5, 30):
            row[f"macs{k}_v021_mb"] = float(K21.at[n, f"macs{k}_mb"]); row[f"macs{k}_v022_mb"] = float(K.at[n, f"macs{k}_mb"])
        for t in (0.01, 0.03, 0.1):
            row[f"rate_T9_{t:g}_v022_over_v021"] = float(R.at[n, f"rate_T9_{t:g}"] / R21.at[n, f"rate_T9_{t:g}"])
        out["independent_recompute"].append(row)
    out["independent_recompute_max_relerr"] = worst
    out["independent_recompute_ok_lt_1e-6"] = bool(worst < 1e-6)
    # closed forms on the joined grid
    el0, _ = joined(PICK[0]); cf = []
    for M in (15.9949, 55.9349, 196.9666):
        r = M / (M + MN)
        for kt in (5e3, 30e3, 100e3):
            s1v = 2.0 * np.sqrt(1e3 / el0); m1 = B.macs_cm(el0, s1v, r, kt)[0][0]; want = 2.0 * np.sqrt(1e3 / (kt / r))
            th = kt / r; x = el0[0] / th
            mc = B.macs_cm(el0, np.full(len(el0), 2.0), r, kt)[0][0]
            wc = 2 / np.sqrt(np.pi) / kt ** 2 * r ** 2 * 2.0 * (th ** 2 * (1 + x) * np.exp(-x) + np.sqrt(el0[0]) * th ** 1.5 * gfun(1.5) * gammainc(1.5, x))
            cf.append(dict(M_u=M, kT_keV=kt / 1e3, one_over_v_relerr=abs(m1 / want - 1), const_relerr=abs(mc / wc - 1)))
    out["closed_forms"] = cf
    out["closed_forms_ok_lt_1e-9"] = bool(max(max(c["const_relerr"], c["one_over_v_relerr"]) for c in cf) < 1e-9)
    # reduced mass, every nuclide: rate = N_A MACS(kT) v_T, needs the MACS at the rate's kT -> check the T9 where kT is a MACS kT
    # point is not on the grid, so check mu itself and the rate/MACS relation through the build's macs_cm on 200 nuclides
    mu = MN * R.target_mass_u / (MN + R.target_mass_u)
    mu_ok = float(np.max(np.abs(R.reduced_mass_u / mu - 1)))
    old = R.A / (R.A + 1.0)
    rng = np.random.default_rng(22); samp = rng.choice(R.index.to_numpy(), 200, replace=False); wr = 0.0
    for n in samp:
        el, sl = joined(n); M = float(R.at[n, "target_mass_u"])
        kt = np.array([0.01, 0.1, 1.0]) * B.KB_EV_PER_GK
        m = B.macs_cm(el, sl, M / (M + MN), kt)[0]
        rt = B.NA * m * 1e-24 * B.C_CM_S * np.sqrt(2 * kt / (float(R.at[n, "reduced_mass_u"]) * B.U_EV))
        wr = max(wr, float(np.max(np.abs(rt / R.loc[n, ["rate_T9_0.01", "rate_T9_0.1", "rate_T9_1"]].to_numpy(float) - 1))))
    out["reduced_mass"] = dict(mu_eq_mn_M_over_mn_plus_M_maxrel=mu_ok, rate_eq_NA_macs_vT_maxrel_200_nuclides=wr,
                               old_over_new_v_T_if_M_eq_A_median=float(np.median(np.sqrt((MN * R.A / (MN + R.A)) / old))),
                               old_over_new_v_T_min=float(np.min(np.sqrt((MN * R.A / (MN + R.A)) / old))),
                               old_over_new_v_T_max=float(np.max(np.sqrt((MN * R.A / (MN + R.A)) / old))),
                               mass_sources=MS.mass_source.value_counts().to_dict())
    # below 1 keV
    eng = C.below1keV_source.str.startswith("engine")
    dmax, jmax, onev = 0.0, 0.0, 0.0
    for n in C.index:
        s = np.asarray(C.at[n, "sigma_b"], float); sl = np.asarray(C.at[n, "sigma_below1keV_b"], float)
        el = np.asarray(C.at[n, "energy_below1keV_ev"], float)
        if eng[n]:
            em = np.asarray(E.at[n, "engine_mb"], float); want = s[0] * em / E.at[n, "engine_1keV_mb"]
            dmax = max(dmax, float(np.max(np.abs(sl / want - 1))))
            if C.at[n, "tier"] != "ANCHORED" and "scaled by" not in C.at[n, "below1keV_source"]:  # the shipped values ARE the engine values
                jmax = max(jmax, float(np.max(np.abs(sl / (em / 1e3) - 1))))
        else:
            onev = max(onev, float(np.max(np.abs(sl / (s[0] * np.sqrt(1e3 / el)) - 1))))
    F = E[E.grid.str.startswith("134")].join(C2[["engine_points_repaired"]])
    rep02 = F.engine_points_repaired > 0
    only1k = (F.full_vs_v02_points_gt1e9 == 1) & (F.junction_reldiff.abs() > 1e-9)
    exact = F.full_vs_v02_points_gt1e9 == 0
    out["below1keV"] = dict(engine=int(eng.sum()), one_over_v=int((~eng).sum()),
                            one_over_v_list=C.loc[~eng, "below1keV_source"].to_dict(),
                            engine_scaled_to_join_1keV=int(C.below1keV_source.str.contains("scaled by").sum()),
                            engine_values_shipped_as_collected_maxrel=dmax, engine_values_vs_raw_engine_maxrel_non_anchored=jmax,
                            one_over_v_rule_maxrel=onev,
                            long_grid_runs=int(len(F)),
                            long_grid_reproduce_all_64_v02_points_lt_1e9=int(exact.sum()),
                            long_grid_differ_only_at_1keV=int((only1k & ~rep02).sum()),
                            long_grid_differ_only_at_1keV_maxrel=float(F.junction_reldiff[only1k & ~rep02].abs().max()),
                            long_grid_differ_v02_repaired_floor_points=int((~exact & rep02).sum()),
                            long_grid_differ_other=F.index[~exact & ~rep02 & ~only1k].tolist(),
                            short_vs_long_below1keV_maxrel_median=float(F.short_vs_full_maxrel_le1keV.median()))
    # files
    an = C.tier == "ANCHORED"
    same = [np.array_equal(np.asarray(C.at[n, "sigma_b"]), np.asarray(C2.at[n, "sigma_b"])) for n in C.index[~an]]
    bands = all(np.array_equal(np.asarray(C.at[n, c]), np.asarray(C2.at[n, c])) for n in C.index for c in ("unc68_log10", "unc95_log10"))
    shares = K.filter(like="share_below1keV").to_numpy()
    out.update(
        nuclides=int(len(C)), same_nuclides_and_tiers_as_v02=bool(C.index.equals(C2.index) and (C.tier == C2.tier).all()),
        non_anchored_curves_identical_to_v02=bool(all(same)), non_anchored_curves=int(len(same)),
        bands_identical_to_v02=bool(bands),
        anchored_macs30_eq_v02_anchor_maxrel=float(np.max(np.abs(M1.macs30_mb[M1.tier == "ANCHORED"] / M2.macs30_mb[M2.tier == "ANCHORED"] - 1))),
        macs30_csv_eq_capture_column=bool(np.allclose(M1.macs30_mb, C.macs30_mb.reindex(M1.index), rtol=1e-12)),
        macs30_eq_macs_kt_30=bool(np.allclose(M1.macs30_mb, K.macs30_mb.reindex(M1.index), rtol=1e-12)),
        channels_byte_identical_to_v02=sha(os.path.join(V2, "channels_v02.parquet")) == sha(os.path.join(V22, "channels_v022.parquet")),
        grid_np_byte_identical_to_v02=sha(os.path.join(V2, "grid_np_v02.parquet")) == sha(os.path.join(V22, "grid_np_v022.parquet")),
        macs_finite_positive=bool((K[[f"macs{k}_mb" for k in KTS]].to_numpy() > 0).all() and np.isfinite(K[[f"macs{k}_mb" for k in KTS]].to_numpy()).all()),
        shares_in_0_1=bool(((shares >= 0) & (shares < 1)).all()),
        below1keV_finite_positive=bool(all(np.all(np.isfinite(x)) and np.all(np.asarray(x) > 0) for x in C.sigma_below1keV_b)),
        rates_finite_positive=bool((R.filter(like="rate_T9").to_numpy() > 0).all() and np.isfinite(R.filter(like="rate_T9").to_numpy()).all()),
    )
    kp = os.environ.get("KADONIS_TSV", os.path.expanduser("~/nucleus/raw/kadonis/kadonis1.0_macs.tsv"))
    if os.path.exists(kp):
        kd = pd.read_csv(kp, sep="\t", index_col=False); kd = kd[kd.Isomer.isna()]
        K2 = pd.read_csv(os.path.join(V2, "macs_kt_v02.csv")).set_index("nuclide_id")
        res = []
        for k in (5, 10, 30, 100):
            col = str(k) if k != 100 else "100(keV)"
            kv = {(int(z), int(a)): pd.to_numeric(v, errors="coerce") for z, a, v in zip(kd.Z, kd.A, kd[col])}
            for tag, T in (("v0.2", K2), ("v0.2.1", K21), ("v0.2.2", K)):
                t = T[T.tier == "MEASURED"]
                z = np.array([np.log10(m / kv[(int(Z), int(A))]) for Z, A, m in zip(t.Z, t.A, t[f"macs{k}_mb"])
                              if (int(Z), int(A)) in kv and kv[(int(Z), int(A))] > 0])
                z = z[np.isfinite(z)]
                res.append(dict(kT_keV=k, library=tag, nuclei=int(len(z)), f_rms=float(10 ** np.sqrt(np.mean(z ** 2))), median_bias_dex=float(np.median(z))))
        out["kadonis_measured_tier_descriptive"] = res
        print(pd.DataFrame(res).to_string())
    out["build_summary"] = json.load(open(os.path.join(V22, "build_summary_v022.json")))
    with open(os.path.join(V22, "VERIFY_V022.json"), "w", newline="\n") as f:
        json.dump(out, f, indent=1, default=float)
    print(json.dumps({k: v for k, v in out.items() if k not in ("independent_recompute", "closed_forms", "build_summary")}, indent=1, default=float))
    cols = ["nuclide_id", "A", "tier", "macs5_v021_mb", "macs5_v022_mb", "macs30_v021_mb", "macs30_v022_mb", "rate_T9_0.01_v022_over_v021",
            "rate_T9_0.03_v022_over_v021", "rate_T9_0.1_v022_over_v021", "macs5_relerr", "rate_T9_0.01_relerr"]
    print(pd.DataFrame(out["independent_recompute"])[cols].to_string())
    print(pd.DataFrame(cf).to_string())


if __name__ == "__main__":
    main()
