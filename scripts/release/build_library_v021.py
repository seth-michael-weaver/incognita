"""Build library v0.2.1 from library v0.2: the Maxwellian averages and rates recomputed in the centre-of-mass frame.

The bug (v0.2 and earlier): MACS(kT) was integrated over the LABORATORY neutron energy, sigma(E_lab) E_lab exp(-E_lab/kT),
with no A/(A+1) factor (the v0.2 build.py:33-35 and mform.py:25-27 for macs30 / ANCHORED scaling;
the v0.2 make_rates.py for macs_kt, the rates and the REACLIB fits). The MACS is defined (KADoNiS,
Beer, Voss & Winters 1992) with E the centre-of-mass energy and the cross section taken at E_lab = E (A+1)/A. Integrating
over E_lab overstates the MACS by about (1+1/A)^a (a ~ 1/2 for a 1/v cross section). v0.2 also cut every integral at the
grid's first point, E_lab = 1 keV, which drops the E < 1 keV part (several % at kT = 5 keV; most of the rate at T9 < 0.03).

v0.2.1 (this script):
  MACS(kT) = 2/sqrt(pi) kT^-2 int_0^inf sigma(E (A+1)/A) E exp(-E/kT) dE,  E = centre-of-mass energy,
  with sigma log-log interpolated on the 64-point grid (1 keV - 20 MeV, lab energy) and, below 1 keV, extended as 1/v
  from the first grid point: sigma(E_lab) = sigma(1 keV) (1 keV / E_lab)^(1/2). The share of each MACS that comes from
  that extension is a new column (share_below1keV_<kT>keV).
  The integral is exact for the piecewise power law: on each grid interval sigma = s_i (E_lab/E_i)^b_i, so the piece is
  an incomplete gamma function (computed by Gauss-Legendre quadrature in log E, 48 nodes per interval); the 1/v part is
  analytic (lower incomplete gamma, a = 3/2).
  N_A<sigma v>(T9) = N_A MACS(kT) v_T, v_T = sqrt(2 kT / mu), mu = A/(A+1) u, kT = T9 * 86.1733 keV; REACLIB 7-parameter
  fit as in v0.2.
  ANCHORED (21 nuclides): the v0.2 curve times one factor so that the centre-of-mass MACS30 equals the measured anchor.
  The anchor is the v0.2 macs30_mb of these nuclides (v0.2 set it equal to the anchor to 7e-16).
  Nothing else changes: the curves of the other 6,147 nuclides, the bands, channels and the (n,p) grid are v0.2's,
  byte for byte where a file is copied.
  alt_macs30_mb (model-form alternative, 1,131 nuclides): the alternative curves are not shipped and their engine runs
  are no longer kept, so it is the v0.2 value times the shipped curve's own v0.2.1/v0.2 MACS30 ratio (labelled).

usage:  uv run --no-project --with pandas --with pyarrow --with scipy python scripts/release/build_library_v021.py
"""
import hashlib, json, os, re, shutil

import numpy as np
import pandas as pd
from scipy.special import gammainc, gamma as gfun

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "library", "v0.2")
OUT = os.path.join(ROOT, "library", "v0.2.1")
KTS = np.array([5, 8, 10, 15, 20, 25, 30, 40, 50, 60, 80, 100], float)  # keV
T9 = np.array([0.01, 0.015, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.7,
               0.8, 0.9, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0])
KB_EV_PER_GK = 86173.3          # as v0.2 (make_rates.py)
U_EV = 931.4941024e6
C_CM_S = 2.99792458e10
NA = 6.02214076e23
XG, WG = np.polynomial.legendre.leggauss(48)


def macs_cm(e, s, A, kt_ev, frame_only=False):
    """MACS [same unit as s] at each kt_ev, centre-of-mass definition; and the share from E_lab < e[0] (1/v extension).

    Integration variable: lab energy. With E = E_lab A/(A+1) (CM) the integrand sigma E exp(-E/kT) dE becomes
    (A/(A+1))^2 sigma(E_lab) E_lab exp(-E_lab/theta) dE_lab, theta = kT (A+1)/A."""
    kt = np.atleast_1d(np.asarray(kt_ev, float)); r = A / (A + 1.0); th = kt / r
    le, ls = np.log(e), np.log(s)
    # grid pieces: Gauss-Legendre in u = ln E_lab, integrand sigma E^2 exp(-E/theta) du
    a, b = le[:-1], le[1:]
    u = 0.5 * (b - a)[:, None] * XG[None, :] + 0.5 * (a + b)[:, None]          # (n-1, 48)
    lsig = ls[:-1, None] + (ls[1:] - ls[:-1])[:, None] / (b - a)[:, None] * (u - a[:, None])
    E = np.exp(u)
    f = np.exp(lsig + 2 * u)[None] * np.exp(-E[None] / th[:, None, None])      # (nkt, n-1, 48)
    hi = (0.5 * (b - a)[None, :, None] * WG[None, None, :] * f).sum(axis=(1, 2))
    # 1/v below e[0]: sigma = s0 sqrt(e0/E): int_0^e0 s0 sqrt(e0) E^(1/2) exp(-E/theta) dE
    lo = s[0] * np.sqrt(e[0]) * th ** 1.5 * gfun(1.5) * gammainc(1.5, e[0] / th)
    I = r ** 2 * (hi + lo)
    if frame_only:  # centre-of-mass, but cut at E_lab = e[0] like v0.2 (no 1/v extension): isolates the frame correction
        return 2 / np.sqrt(np.pi) * r ** 2 * hi / kt ** 2
    return 2 / np.sqrt(np.pi) * I / kt ** 2, lo / (hi + lo)


def macs_lab_v02(e, s, kt_ev):
    """v0.2's formula (make_rates.py): lab energy, from e[0] up, 6000-point trapezoid -- to check this script reproduces v0.2."""
    g = np.logspace(np.log10(e[0]), np.log10(e[-1]), 6000)
    sg = 10 ** np.interp(np.log10(g), np.log10(e), np.log10(np.clip(s, 1e-30, None)))
    return np.array([2 / np.sqrt(np.pi) * np.trapezoid(sg * g * np.exp(-g / k), g) / k ** 2 for k in np.atleast_1d(kt_ev)])


def reaclib_fit(t9, r):  # identical to v0.2 (make_rates.py)
    ok = r > 0
    X = np.stack([np.ones(ok.sum()), 1 / t9[ok], t9[ok] ** (-1 / 3), t9[ok] ** (1 / 3), t9[ok], t9[ok] ** (5 / 3), np.log(t9[ok])], 1)
    a, *_ = np.linalg.lstsq(X, np.log(r[ok]), rcond=None)
    return a, float(np.max(np.abs(np.log10(np.exp(X @ a) / r[ok]))))


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    os.makedirs(OUT, exist_ok=True)
    L = pd.read_parquet(os.path.join(SRC, "capture_v02.parquet"))
    M2 = pd.read_csv(os.path.join(SRC, "macs30_v02.csv")).set_index("nuclide_id")
    K2 = pd.read_csv(os.path.join(SRC, "macs_kt_v02.csv")).set_index("nuclide_id")
    R2 = pd.read_csv(os.path.join(SRC, "rates_v02.csv")).set_index("nuclide_id")
    kt_rate = T9 * KB_EV_PER_GK
    new_sig, new_m30, new_vs, mk, rr, dat, anch, chk, fo, shares_t9 = [], [], [], [], [], [], [], [], {}, []
    for r in L.itertuples(index=False):
        e = np.asarray(r.energy_ev, float); s = np.asarray(r.sigma_b, float); A = int(r.A); vs = r.value_source
        lab_m = macs_lab_v02(e, s, KTS * 1e3) * 1e3
        fo[r.nuclide_id] = macs_cm(e, s, A, KTS * 1e3, frame_only=True) * 1e3 / lab_m  # frame correction alone, v0.2 curve
        chk.append(float(np.max(np.abs(lab_m / K2.loc[r.nuclide_id, [f"macs{int(k)}_mb" for k in KTS]].to_numpy(float) - 1))))
        if r.tier == "ANCHORED":
            anchor = float(M2.at[r.nuclide_id, "macs30_mb"])
            m30 = macs_cm(e, s, A, 3e4)[0][0] * 1e3
            f = anchor / m30; s = s * f
            m_old = re.search(r"blind curve x ([0-9.]+) \(measured MACS30 anchor\)", vs)
            f_old = float(m_old.group(1)) if m_old else float("nan")
            vs = re.sub(r"blind curve x [0-9.]+ \(measured MACS30 anchor\)",
                        f"blind curve x {f_old * f:.3f} (measured MACS30 anchor; centre-of-mass MACS, v0.2.1)", vs)
            anch.append(dict(nuclide_id=r.nuclide_id, Z=int(r.Z), A=A, anchor_equals_v02_macs30_mb=anchor, v02_factor=f_old,
                             v021_extra_factor=float(f), v021_factor=f_old * f, curve_change_pct=100 * (f - 1)))
        m, sh = macs_cm(e, s, A, KTS * 1e3); m = m * 1e3
        new_sig.append(list(s)); new_m30.append(float(m[list(KTS).index(30)])); new_vs.append(vs)
        mk.append(dict(nuclide_id=r.nuclide_id, **{f"macs{int(k)}_mb": v for k, v in zip(KTS, m)},
                       **{f"share_below1keV_{int(k)}keV": v for k, v in zip(KTS, sh)}))
        mr, shr = macs_cm(e, s, A, kt_rate)                                              # b
        mu = A / (A + 1.0) * U_EV
        rate = NA * mr * 1e-24 * C_CM_S * np.sqrt(2 * kt_rate / mu)
        a, res = reaclib_fit(T9, rate)
        rr.append(dict(nuclide_id=r.nuclide_id, Z=int(r.Z), A=A, tier=r.tier, reaclib_max_resid_dex=res,
                       **{f"rate_T9_{t:g}": v for t, v in zip(T9, rate)}))
        shares_t9.append(shr)
        dat.append(f"{r.nuclide_id} {int(r.Z):3d} {A:3d} n,g " + " ".join(f"{x:+.6e}" for x in a)
                   + f"  # v021, {r.tier}, fit residual {res:.3f} dex")
    # ---- capture: new sigma for ANCHORED only, macs30_mb (CM) for all, value_source for ANCHORED
    L1 = L.copy()
    L1["sigma_b"] = new_sig; L1["macs30_mb"] = new_m30; L1["value_source"] = new_vs
    ratio30 = L1.set_index("nuclide_id").macs30_mb / M2.macs30_mb.reindex(L1.nuclide_id).values
    alt = L1["alt_macs30_mb"].to_numpy(float) * ratio30.to_numpy()
    L1["alt_macs30_mb"] = alt
    L1.to_parquet(os.path.join(OUT, "capture_v021.parquet"))
    unchanged = sum(1 for a_, b_ in zip(L.sigma_b, L1.sigma_b) if np.array_equal(np.asarray(a_), np.asarray(b_)))
    # ---- macs30 csv: same columns as v0.2, macs30_mb and alt_macs30_mb replaced
    M1 = M2.copy()
    M1["macs30_mb"] = L1.set_index("nuclide_id").macs30_mb.reindex(M1.index)
    M1["alt_macs30_mb"] = L1.set_index("nuclide_id").alt_macs30_mb.reindex(M1.index)
    M1.reset_index().to_csv(os.path.join(OUT, "macs30_v021.csv"), index=False)
    # ---- macs_kt: macs<kT>_mb replaced, share columns added; unc factors and flags as v0.2
    MK = pd.DataFrame(mk).set_index("nuclide_id")
    K1 = K2.copy()
    for k in KTS:
        K1[f"macs{int(k)}_mb"] = MK[f"macs{int(k)}_mb"].reindex(K1.index)
    K1["alt_macs30_mb"] = M1.alt_macs30_mb.reindex(K1.index)
    for k in KTS:
        K1[f"share_below1keV_{int(k)}keV"] = MK[f"share_below1keV_{int(k)}keV"].reindex(K1.index)
    K1.reset_index().to_csv(os.path.join(OUT, "macs_kt_v021.csv"), index=False)
    R1 = pd.DataFrame(rr); R1.to_csv(os.path.join(OUT, "rates_v021.csv"), index=False)
    with open(os.path.join(OUT, "reaclib_v021.dat"), "w") as f:
        f.write("\n".join(dat) + "\n")
    for a_, b_ in (("channels_v02.parquet", "channels_v021.parquet"), ("grid_np_v02.parquet", "grid_np_v021.parquet")):
        shutil.copyfile(os.path.join(SRC, a_), os.path.join(OUT, b_))
    AN = pd.DataFrame(anch); AN.to_csv(os.path.join(OUT, "anchored_rescale_v021.csv"), index=False)
    # ---- summary numbers
    d30 = (M1.macs30_mb / M2.macs30_mb).to_numpy(); Aarr = M1.A.to_numpy()
    tiers = M1.tier.to_numpy()
    bands = []
    for lo, hi in ((1, 20), (20, 40), (40, 80), (80, 150), (150, 300)):
        k = (Aarr >= lo) & (Aarr < hi) & (tiers != "ANCHORED")
        x = 1 / d30[k] - 1  # v0.2 over v0.2.1
        y = np.array([1 / fo[n][list(KTS).index(30)] - 1 for n in M1.index[k]])  # v0.2 over CM-cut-at-1-keV: the frame bias alone
        bands.append(dict(A=f"{lo}-{hi - 1}", n=int(k.sum()), v02_over_v021_median_pct=100 * float(np.median(x)),
                          min_pct=100 * float(x.min()), max_pct=100 * float(x.max()),
                          frame_bias_alone_median_pct=100 * float(np.median(y)), frame_bias_alone_min_pct=100 * float(y.min()),
                          frame_bias_alone_max_pct=100 * float(y.max()),
                          frame_only_formula_pct=100 * float(np.median(np.sqrt(1 + 1 / Aarr[k]) - 1))))
    kt_tab = []
    for k in KTS:
        x = K2[f"macs{int(k)}_mb"] / K1[f"macs{int(k)}_mb"] - 1
        sh = K1[f"share_below1keV_{int(k)}keV"]
        y = pd.Series({n: 1 / v[list(KTS).index(k)] - 1 for n, v in fo.items()})
        kt_tab.append(dict(kT_keV=int(k), frame_bias_alone_median_pct=100 * float(y.median()), v02_over_v021_median_pct=100 * float(x.median()), p05_pct=100 * float(x.quantile(0.05)),
                           p95_pct=100 * float(x.quantile(0.95)), share_below1keV_median_pct=100 * float(sh.median()),
                           share_below1keV_max_pct=100 * float(sh.max())))
    rt = []
    for t in (0.01, 0.03, 0.1, 0.3, 1.0, 3.0):
        x = R2[f"rate_T9_{t:g}"] / R1.set_index("nuclide_id")[f"rate_T9_{t:g}"].reindex(R2.index) - 1
        sh = np.array(shares_t9)[:, list(T9).index(t)]
        rt.append(dict(T9=t, v02_over_v021_median_pct=100 * float(x.median()), p05_pct=100 * float(x.quantile(0.05)),
                       p95_pct=100 * float(x.quantile(0.95)), share_below1keV_median_pct=100 * float(np.median(sh)),
                       share_below1keV_max_pct=100 * float(sh.max())))
    summ = dict(nuclides=len(L1), curves_unchanged=unchanged, curves_rescaled_anchored=len(AN),
                reproduce_v02_macs_kt_with_v02_formula_maxrel=max(chk),
                anchored_cm_macs30_eq_anchor_maxrel=float(np.max(np.abs(L1[L1.tier == "ANCHORED"].macs30_mb.to_numpy()
                                                                          / M2.loc[L1[L1.tier == "ANCHORED"].nuclide_id, "macs30_mb"].to_numpy() - 1))),
                macs30_by_A=bands, macs_by_kT=kt_tab, rates_by_T9=rt,
                reaclib_resid_median_dex=float(R1.reaclib_max_resid_dex.median()), reaclib_resid_p99_dex=float(R1.reaclib_max_resid_dex.quantile(0.99)),
                macs_all_finite_positive=bool(np.isfinite(K1[[f"macs{int(k)}_mb" for k in KTS]].to_numpy()).all()
                                              and (K1[[f"macs{int(k)}_mb" for k in KTS]].to_numpy() > 0).all()),
                rates_all_finite_positive=bool(np.isfinite(R1.filter(like="rate_T9").to_numpy()).all() and (R1.filter(like="rate_T9").to_numpy() > 0).all()),
                anchored=AN.to_dict("records"))
    with open(os.path.join(OUT, "build_summary_v021.json"), "w") as f:
        json.dump(summ, f, indent=1)
    print(json.dumps({k: v for k, v in summ.items() if k != "anchored"}, indent=1))
    print(AN.to_string())


if __name__ == "__main__":
    main()
