"""Independent checks of library v0.2.1 (writes library/v0.2.1/VERIFY_V021.json).

1. MACS recomputed for 12 nuclides with a different method from the build: the integral is done over the CENTRE-OF-MASS
   energy (the build integrates over lab energy and converts), by a 400,000-point trapezoid in ln E from 1e-6 eV, with
   sigma looked up at E_lab = E (A+1)/A and the 1/v extension evaluated pointwise. Must agree with macs_kt_v021.csv to
   < 1e-6 (relative) at every kT, and the rate with N_A MACS v_T to < 1e-6.
2. Closed forms through the build's macs_cm: sigma constant above 1 keV with the 1/v extension below (incomplete gamma
   functions); 1/v sigma ->
   MACS = sigma_lab(E_lab = kT (A+1)/A) (sigma v constant, so the MACS is the cross section at the thermal relative
   velocity; this is the KADoNiS/Beer-Voss-Winters convention and fails by sqrt((A+1)/A) under the lab-frame formula).
3. Files: same nuclides and tiers as v0.2; non-ANCHORED curves and all bands identical to v0.2; channels and (n,p) grid
   byte-identical; ANCHORED MACS30 equals the v0.2 anchor; every MACS, rate and share finite and in range.

usage:  uv run --no-project --with pandas --with pyarrow --with scipy python scripts/release/verify_library_v021.py
"""
import hashlib, importlib.util, json, os

import numpy as np
import pandas as pd
from scipy.special import gammainc, gamma as gfun

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
V2, V21 = os.path.join(ROOT, "library", "v0.2"), os.path.join(ROOT, "library", "v0.2.1")
KTS = [5, 8, 10, 15, 20, 25, 30, 40, 50, 60, 80, 100]
PICK = ["Z008N008M0", "Z011N012M0", "Z012N012M0", "Z020N020M0", "Z026N030M0", "Z028N034M0", "Z040N050M0", "Z056N082M0",
        "Z079N118M0", "Z082N126M0", "Z092N146M0", "Z055N080M0"]  # O-16 Na-23 Mg-24 Ca-40 Fe-56 Ni-62 Zr-90 Ba-138 Au-197 Pb-208 U-238 Cs-135 (ANCHORED)


def macs_indep(e, s, A, kt):
    """CM-energy trapezoid; sigma(E_lab) log-log on the grid, 1/v below e[0]."""
    g = np.exp(np.linspace(np.log(1e-6), np.log(e[-1] * A / (A + 1.0)), 400_001))
    el = g * (A + 1.0) / A
    ls = np.where(el < e[0], np.log(s[0]) + 0.5 * (np.log(e[0]) - np.log(el)), np.interp(np.log(el), np.log(e), np.log(s)))
    f = np.exp(ls) * g * np.exp(-g / kt) * g          # d E = E d(ln E)
    return 2 / np.sqrt(np.pi) * np.trapezoid(f, np.log(g)) / kt ** 2


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    spec = importlib.util.spec_from_file_location("b", os.path.join(ROOT, "scripts", "release", "build_library_v021.py"))
    B = importlib.util.module_from_spec(spec); spec.loader.exec_module(B)
    C2 = pd.read_parquet(os.path.join(V2, "capture_v02.parquet")).set_index("nuclide_id")
    C1 = pd.read_parquet(os.path.join(V21, "capture_v021.parquet")).set_index("nuclide_id")
    K1 = pd.read_csv(os.path.join(V21, "macs_kt_v021.csv")).set_index("nuclide_id")
    M1 = pd.read_csv(os.path.join(V21, "macs30_v021.csv")).set_index("nuclide_id")
    M2 = pd.read_csv(os.path.join(V2, "macs30_v02.csv")).set_index("nuclide_id")
    R1 = pd.read_csv(os.path.join(V21, "rates_v021.csv")).set_index("nuclide_id")
    out = {"independent_recompute": []}
    worst = 0.0
    for n in PICK:
        r = C1.loc[n]; e = np.asarray(r.energy_ev, float); s = np.asarray(r.sigma_b, float); A = int(r.A)
        row = dict(nuclide_id=n, A=A, tier=r.tier)
        for k in KTS:
            m = macs_indep(e, s, A, k * 1e3) * 1e3; p = K1.at[n, f"macs{k}_mb"]
            d = abs(p / m - 1); worst = max(worst, d); row[f"macs{k}_relerr"] = d
        row["macs30_v021_mb"] = float(M1.at[n, "macs30_mb"]); row["macs30_v02_mb"] = float(M2.at[n, "macs30_mb"])
        for t in (0.01, 0.1, 0.3, 1.0, 5.0):
            kt = t * B.KB_EV_PER_GK; mu = A / (A + 1.0) * B.U_EV
            rate = B.NA * macs_indep(e, s, A, kt) * 1e-24 * B.C_CM_S * np.sqrt(2 * kt / mu)
            d = abs(R1.at[n, f"rate_T9_{t:g}"] / rate - 1); worst = max(worst, d); row[f"rate_T9_{t:g}_relerr"] = d
        out["independent_recompute"].append(row)
    out["independent_recompute_max_relerr"] = worst
    out["independent_recompute_ok_lt_1e-6"] = bool(worst < 1e-6)
    # closed forms through the build's own macs_cm
    e = np.asarray(C1.iloc[0].energy_ev, float); cf = []
    for A in (1, 16, 56, 197):
        for kt in (5e3, 30e3, 100e3):
            mc = B.macs_cm(e, np.full(len(e), 2.0), A, kt)[0][0]
            s1v = 2.0 * np.sqrt(1e3 / e)
            m1 = B.macs_cm(e, s1v, A, kt)[0][0]; want = 2.0 * np.sqrt(1e3 / (kt * (A + 1.0) / A))
            ml = B.macs_lab_v02(e, s1v, kt)[0]
            # constant 2 b above the grid's first point e0, 1/v below it (the build's extension), in closed form:
            # MACS = 2/sqrt(pi) kT^-2 r^2 s0 [theta^2 (1+x) e^-x + sqrt(e0) theta^1.5 gamma(3/2, x)], theta = kT/r, x = e0/theta
            r = A / (A + 1.0); th = kt / r; x = e[0] / th
            wc = 2 / np.sqrt(np.pi) / kt ** 2 * r ** 2 * 2.0 * (th ** 2 * (1 + x) * np.exp(-x) + np.sqrt(e[0]) * th ** 1.5 * gfun(1.5) * gammainc(1.5, x))
            cf.append(dict(A=A, kT_keV=kt / 1e3, const_relerr=abs(mc / wc - 1), one_over_v_relerr=abs(m1 / want - 1),
                           lab_formula_one_over_v_ratio=ml / want))
    out["closed_forms"] = cf
    out["closed_forms_ok_lt_1e-9"] = bool(max(max(c["const_relerr"], c["one_over_v_relerr"]) for c in cf) < 1e-9)
    # files
    an = C1.tier == "ANCHORED"
    same = [np.array_equal(np.asarray(C1.at[n, "sigma_b"]), np.asarray(C2.at[n, "sigma_b"])) for n in C1.index[~an]]
    bands = all(np.array_equal(np.asarray(C1.at[n, c]), np.asarray(C2.at[n, c])) for n in C1.index for c in ("unc68_log10", "unc95_log10"))
    out.update(
        nuclides=int(len(C1)), same_nuclides_and_tiers_as_v02=bool(C1.index.equals(C2.index) and (C1.tier == C2.tier).all()),
        non_anchored_curves_identical_to_v02=bool(all(same)), non_anchored_curves=int(len(same)),
        bands_identical_to_v02=bool(bands),
        anchored_macs30_eq_v02_anchor_maxrel=float(np.max(np.abs(M1.macs30_mb[M1.tier == "ANCHORED"] / M2.macs30_mb[M2.tier == "ANCHORED"] - 1))),
        macs30_csv_eq_capture_column=bool(np.allclose(M1.macs30_mb, C1.macs30_mb.reindex(M1.index), rtol=1e-12)),
        macs30_eq_macs_kt_30=bool(np.allclose(M1.macs30_mb, K1.macs30_mb.reindex(M1.index), rtol=1e-12)),
        channels_byte_identical=sha(os.path.join(V2, "channels_v02.parquet")) == sha(os.path.join(V21, "channels_v021.parquet")),
        grid_np_byte_identical=sha(os.path.join(V2, "grid_np_v02.parquet")) == sha(os.path.join(V21, "grid_np_v021.parquet")),
        macs_finite_positive=bool((K1[[f"macs{k}_mb" for k in KTS]].to_numpy() > 0).all() and np.isfinite(K1[[f"macs{k}_mb" for k in KTS]].to_numpy()).all()),
        shares_in_0_1=bool(((K1.filter(like="share_below1keV").to_numpy() >= 0) & (K1.filter(like="share_below1keV").to_numpy() < 1)).all()),
        rates_finite_positive=bool((R1.filter(like="rate_T9").to_numpy() > 0).all() and np.isfinite(R1.filter(like="rate_T9").to_numpy()).all()),
    )
    # descriptive: MEASURED tier against KADoNiS v1.0 (a compilation of the same measurements, centre-of-mass MACS; not
    # redistributed, so read from KADONIS_TSV when it is there; skipped otherwise)
    kp = os.environ.get("KADONIS_TSV", os.path.expanduser("~/nucleus/raw/kadonis/kadonis1.0_macs.tsv"))
    if os.path.exists(kp):
        kd = pd.read_csv(kp, sep="	", index_col=False); kd = kd[kd.Isomer.isna()]
        K2 = pd.read_csv(os.path.join(V2, "macs_kt_v02.csv")).set_index("nuclide_id")
        res = []
        for k in (5, 10, 30, 100):
            col = str(k) if k != 100 else "100(keV)"
            kv = {(int(z), int(a)): pd.to_numeric(v, errors="coerce") for z, a, v in zip(kd.Z, kd.A, kd[col])}
            for tag, T in (("v0.2", K2), ("v0.2.1", K1)):
                t = T[T.tier == "MEASURED"]
                z = np.array([np.log10(m / kv[(int(Z), int(A))]) for Z, A, m in zip(t.Z, t.A, t[f"macs{k}_mb"])
                              if (int(Z), int(A)) in kv and kv[(int(Z), int(A))] > 0])
                z = z[np.isfinite(z)]
                res.append(dict(kT_keV=k, library=tag, nuclei=int(len(z)), f_rms=float(10 ** np.sqrt(np.mean(z ** 2))), median_bias_dex=float(np.median(z))))
        out["kadonis_measured_tier_descriptive"] = res
        print(pd.DataFrame(res).to_string())
    summ = json.load(open(os.path.join(V21, "build_summary_v021.json")))
    out["build_summary"] = summ
    json.dump(out, open(os.path.join(V21, "VERIFY_V021.json"), "w"), indent=1, default=float)
    print(json.dumps({k: v for k, v in out.items() if k not in ("independent_recompute", "closed_forms", "build_summary")}, indent=1, default=float))
    print(pd.DataFrame(out["independent_recompute"])[["nuclide_id", "A", "tier", "macs30_v02_mb", "macs30_v021_mb", "macs5_relerr", "macs30_relerr", "rate_T9_0.01_relerr"]].to_string())
    print(pd.DataFrame(cf).to_string())


if __name__ == "__main__":
    main()
