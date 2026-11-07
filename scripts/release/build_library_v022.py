"""Build library v0.2.2 from library v0.2: the production engine's own capture below 1 keV, and the reduced mass.

v0.2.1 (2026-11-06) fixed the frame of v0.2's Maxwellian averages and extended every curve below its first grid point
(E_lab = 1 keV) as 1/v. Two issues remained, both fixed here:

1. Below 1 keV the engine's own cross section is not 1/v. Run below 1 keV, the production engine's capture falls as
   E^-0.5 to E^-1 (local slope -0.5 .. -0.97 between 2 eV and 1 keV), so the 1/v extension was low there: rates at
   T9 = 0.01 were 0.79-0.85 of what the engine's own curve gives (Au-197, Fe-56, Dy-164), 0.93-0.96 at T9 = 0.03, and the
   MACS at 5 keV 0.97-0.98 of it.
   v0.2.2 uses the engine below 1 keV: the production engine engine-20261022-3 (nucleus 16606b356d6e) was run with the v0.2
   environment, deck, runner and inputs on its 134-point production grid plus 15 points from 2 eV to 0.66 keV, composed with v0.2's rule for that nucleus
   (scripts/release/collect_below1keV_v022.py, which writes below1keV_engine_v022.parquet). Below 1 keV:
       sigma(E_lab) = sigma_v0.2(1 keV) * engine(E_lab) / engine(1 keV)
   i.e. the engine's own values (the run reproduces v0.2 at and above 1 keV, so the factor is 1 to < 1e-9; ANCHORED curves keep
   their scale factor), log-log interpolated between the 16 points, and 1/v below 2 eV (< 1e-4 of any MACS or rate here).
   Nuclei without a usable engine run (no production input in v0.2, or a failed run) keep the v0.2.1 rule, 1/v from 1 keV,
   and say so in `below1keV_source`.
2. The rate used mu = A/(A+1) u for the reduced mass. It is mu = m_n M / (m_n + M), with m_n = 1.00866491590 u and M the
   target's atomic mass (AME2020; the mass number A in u where AME2020 has no value). With M ~ A u, mu was too small by a
   factor ~1/1.0087, so every v_T = sqrt(2 kT / mu), and every rate, was 0.42-0.43 % too high. The same masses now set the
   centre-of-mass energy: E = E_lab M / (M + m_n) (was A/(A+1); a change of < 0.1 % in any MACS).

Everything else is v0.2.1's method: MACS(kT) = 2/sqrt(pi) kT^-2 int_0^inf sigma(E_lab) E exp(-E/kT) dE with E the
centre-of-mass energy; exact for the piecewise power law (48-point Gauss-Legendre per interval in ln E, closed form for the 1/v
part); N_A<sigma v> = N_A MACS v_T; REACLIB 7-parameter fit as in v0.2; ANCHORED (21): the curve (now including its part
below 1 keV) times one factor so that the MACS30 equals the measured anchor (= the v0.2 macs30_mb); alt_macs30_mb = the v0.2
value times the shipped curve's own v0.2.2/v0.2 MACS30 ratio (the alternative curves are not kept).
Above 1 keV the curves of the other 6,147 nuclei, the bands, the channels and the (n,p) grid are v0.2's, byte for byte where a
file is copied. No band is given below 1 keV.

usage (pandas, pyarrow, scipy):
    python scripts/release/build_library_v022.py
"""
import hashlib, json, os, re, shutil

import numpy as np
import pandas as pd
from scipy.special import gammainc, gamma as gfun

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "library", "v0.2")
V21 = os.path.join(ROOT, "library", "v0.2.1")
OUT = os.path.join(ROOT, "library", "v0.2.2")
KTS = np.array([5, 8, 10, 15, 20, 25, 30, 40, 50, 60, 80, 100], float)  # keV
T9 = np.array([0.01, 0.015, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.7,
               0.8, 0.9, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0])
KB_EV_PER_GK = 86173.3          # as v0.2 (make_rates.py)
U_EV = 931.4941024e6            # atomic mass unit (eV), AME2020 / CODATA 2018
M_N_U = 1.00866491590           # neutron mass (u), AME2020
C_CM_S = 2.99792458e10
NA = 6.02214076e23
XG, WG = np.polynomial.legendre.leggauss(48)
JUNCTION_TOL = 1e-2             # engine(1 keV) in the 149-point run vs the v0.2 curve's 1 keV value; above this: 1/v, flagged


def macs_cm(e, s, r, kt_ev, e_split=1e3):
    """MACS at each kt_ev (unit of s), centre-of-mass definition; and the share from E_lab < e_split.

    e, s: lab energy grid and sigma (piecewise power law between points); 1/v below e[0]. r = M/(M+m_n): E = r E_lab.
    Integration over lab energy: sigma E exp(-E/kT) dE = r^2 sigma(E_lab) E_lab exp(-E_lab/theta) dE_lab, theta = kT/r."""
    kt = np.atleast_1d(np.asarray(kt_ev, float)); th = kt / r
    le, ls = np.log(e), np.log(s)
    a, b = le[:-1], le[1:]
    u = 0.5 * (b - a)[:, None] * XG[None, :] + 0.5 * (a + b)[:, None]          # (n-1, 48)
    lsig = ls[:-1, None] + (ls[1:] - ls[:-1])[:, None] / (b - a)[:, None] * (u - a[:, None])
    E = np.exp(u)
    f = np.exp(lsig + 2 * u)[None] * np.exp(-E[None] / th[:, None, None])      # (nkt, n-1, 48)
    piece = (0.5 * (b - a)[None, :, None] * WG[None, None, :] * f).sum(axis=2)  # (nkt, n-1)
    lo = s[0] * np.sqrt(e[0]) * th ** 1.5 * gfun(1.5) * gammainc(1.5, e[0] / th)  # 1/v below e[0]
    below = lo + piece[:, e[1:] <= e_split * (1 + 1e-12)].sum(axis=1)
    tot = lo + piece.sum(axis=1)
    return 2 / np.sqrt(np.pi) * r ** 2 * tot / kt ** 2, below / tot


def rate(macs_b, kt_ev, mu_u):
    """N_A <sigma v> (cm^3 mol^-1 s^-1) from MACS (b) at kt_ev, reduced mass mu_u (u)."""
    return NA * macs_b * 1e-24 * C_CM_S * np.sqrt(2 * kt_ev / (mu_u * U_EV))


def reaclib_fit(t9, r):  # identical to v0.2 (make_rates.py)
    ok = r > 0
    X = np.stack([np.ones(ok.sum()), 1 / t9[ok], t9[ok] ** (-1 / 3), t9[ok] ** (1 / 3), t9[ok], t9[ok] ** (5 / 3), np.log(t9[ok])], 1)
    a, *_ = np.linalg.lstsq(X, np.log(r[ok]), rcond=None)
    return a, float(np.max(np.abs(np.log10(np.exp(X @ a) / r[ok]))))


def low_part(row, s1kev):
    """(energies, sigma_b, source) below 1 keV for one nucleus; s1kev = its curve's value at 1 keV (b).

    Engine values are used when the run has no output-floor point below 1 keV and its 1 keV value is v0.2's to JUNCTION_TOL;
    they are scaled to join the curve at 1 keV (the factor is 1 to < 1e-9 for 5,986 of 6,150 runs; BUILD.md)."""
    e = np.asarray(row.energy_ev, float); m = np.asarray(row.engine_mb, float); jd = row.junction_reldiff
    if row.status == "engine" and row.points_repaired == 0 and np.isfinite(jd) and abs(jd) <= JUNCTION_TOL             and np.all(np.isfinite(m)) and np.all(m > 0):
        src = f"engine ({row.grid})"
        if abs(jd) > 1e-9:
            src += f"; scaled by {1 / (1 + jd):.6f} to join the v0.2 curve at 1 keV (the run's 1 keV value differs by {jd:+.1e})"
        return e, s1kev * m / row.engine_1keV_mb, src
    if row.status != "engine":
        why = row.status
    elif row.points_repaired > 0:
        why = f"the engine is at its output floor at {int(row.points_repaired)} of the 15 points below 1 keV"
    else:
        why = f"the run's 1 keV value differs from the v0.2 curve by {jd:+.1e} (more than {JUNCTION_TOL:g})"
    if row.message:
        why += f": {row.message}"
    return e, s1kev * np.sqrt(1e3 / e), f"1/v from 1 keV (as v0.2.1); {why}"


def main():
    os.makedirs(OUT, exist_ok=True)
    L = pd.read_parquet(os.path.join(SRC, "capture_v02.parquet"))
    M2 = pd.read_csv(os.path.join(SRC, "macs30_v02.csv")).set_index("nuclide_id")
    K2 = pd.read_csv(os.path.join(SRC, "macs_kt_v02.csv")).set_index("nuclide_id")
    K21 = pd.read_csv(os.path.join(V21, "macs_kt_v021.csv")).set_index("nuclide_id")
    R21 = pd.read_csv(os.path.join(V21, "rates_v021.csv")).set_index("nuclide_id")
    LOWE = pd.read_parquet(os.path.join(OUT, "below1keV_engine_v022.parquet")).set_index("nuclide_id")
    MS = pd.read_csv(os.path.join(OUT, "masses_v022.csv")).set_index("nuclide_id")
    assert LOWE.index.equals(pd.Index(L.nuclide_id)) and MS.index.equals(pd.Index(L.nuclide_id))
    kt_rate = T9 * KB_EV_PER_GK
    new_sig, new_m30, new_vs, lo_e, lo_s, lo_src, mk, rr, dat, anch, sh_t9, parts = ([] for _ in range(12))
    for r in L.itertuples(index=False):
        n = r.nuclide_id; e = np.asarray(r.energy_ev, float); s = np.asarray(r.sigma_b, float); A = int(r.A); vs = r.value_source
        M = float(MS.at[n, "mass_u"]); rr_ = M / (M + M_N_U); mu = M_N_U * M / (M_N_U + M)
        el, sl, src = low_part(LOWE.loc[n], s[0])
        ea, sa = np.r_[el, e], np.r_[sl, s]
        if r.tier == "ANCHORED":
            anchor = float(M2.at[n, "macs30_mb"])
            f = anchor / (macs_cm(ea, sa, rr_, 3e4)[0][0] * 1e3); s = s * f; sl = sl * f; sa = sa * f
            m_old = re.search(r"blind curve x ([0-9.]+) \(measured MACS30 anchor\)", vs)
            f_old = float(m_old.group(1)) if m_old else float("nan")
            vs = re.sub(r"blind curve x [0-9.]+ \(measured MACS30 anchor\)",
                        f"blind curve x {f_old * f:.3f} (measured MACS30 anchor; centre-of-mass MACS including the engine below 1 keV, v0.2.2)", vs)
            anch.append(dict(nuclide_id=n, Z=int(r.Z), A=A, anchor_equals_v02_macs30_mb=anchor, v02_factor=f_old,
                             v022_extra_factor=float(f), v022_factor=f_old * f, curve_change_pct=100 * (f - 1)))
        m, sh = macs_cm(ea, sa, rr_, KTS * 1e3); m = m * 1e3
        new_sig.append(list(s)); new_m30.append(float(m[list(KTS).index(30)])); new_vs.append(vs)
        lo_e.append(list(el)); lo_s.append(list(sl)); lo_src.append(src)
        mk.append(dict(nuclide_id=n, **{f"macs{int(k)}_mb": v for k, v in zip(KTS, m)},
                       **{f"share_below1keV_{int(k)}keV": v for k, v in zip(KTS, sh)}, below1keV_source=src))
        mr, shr = macs_cm(ea, sa, rr_, kt_rate)
        rt = rate(mr, kt_rate, mu)
        a, res = reaclib_fit(T9, rt)
        rr.append(dict(nuclide_id=n, Z=int(r.Z), A=A, tier=r.tier, target_mass_u=M, reduced_mass_u=mu, reaclib_max_resid_dex=res,
                       **{f"rate_T9_{t:g}": v for t, v in zip(T9, rt)}))
        sh_t9.append(shr)
        dat.append(f"{n} {int(r.Z):3d} {A:3d} n,g " + " ".join(f"{x:+.6e}" for x in a)
                   + f"  # v022, {r.tier}, fit residual {res:.3f} dex")
        # decomposition of the v0.2.1 -> v0.2.2 change (non-ANCHORED): (a) engine below 1 keV, (b) masses
        if r.tier != "ANCHORED":
            r21 = A / (A + 1.0); mu21 = A / (A + 1.0)
            m_a = macs_cm(ea, sa, r21, KTS * 1e3)[0] * 1e3                 # engine below 1 keV, v0.2.1 masses
            m_v21 = macs_cm(e, s, r21, KTS * 1e3)[0] * 1e3                  # = v0.2.1
            ra = rate(macs_cm(ea, sa, r21, kt_rate)[0], kt_rate, mu21)
            rv21 = rate(macs_cm(e, s, r21, kt_rate)[0], kt_rate, mu21)
            parts.append(dict(nuclide_id=n, A=A, **{f"lowE_macs{int(k)}": x for k, x in zip(KTS, m_a / m_v21)},
                              **{f"lowE_rate{t:g}": x for t, x in zip(T9, ra / rv21)},
                              **{f"mass_macs{int(k)}": x for k, x in zip(KTS, m / m_a)},
                              **{f"mass_rate{t:g}": x for t, x in zip(T9, rt / ra)},
                              v021_reproduced_macs=float(np.max(np.abs(m_v21 / K21.loc[n, [f"macs{int(k)}_mb" for k in KTS]].to_numpy(float) - 1))),
                              v021_reproduced_rate=float(np.max(np.abs(rv21 / R21.loc[n, [f"rate_T9_{t:g}" for t in T9]].to_numpy(float) - 1)))))
    # ---- capture: v0.2 columns; sigma_b / value_source new for ANCHORED; macs30_mb and alt_macs30_mb new for all; 3 new columns
    L1 = L.copy()
    L1["sigma_b"] = new_sig; L1["macs30_mb"] = new_m30; L1["value_source"] = new_vs
    ratio30 = L1.set_index("nuclide_id").macs30_mb / M2.macs30_mb.reindex(L1.nuclide_id).values
    L1["alt_macs30_mb"] = L1["alt_macs30_mb"].to_numpy(float) * ratio30.to_numpy()
    L1["energy_below1keV_ev"] = lo_e; L1["sigma_below1keV_b"] = lo_s; L1["below1keV_source"] = lo_src
    # known issue (not a value change): where the compound nucleus is unbound to alpha or proton emission by more than 1 MeV
    # (S_min < -1 MeV), the engine's value depends on the top of the run's energy grid (BUILD.md, "Known issue")
    SM = pd.read_csv(os.path.join(OUT, "compound_smin_v022.csv")).set_index("nuclide_id").reindex(L1.nuclide_id)
    gd = LOWE.get("short_grid_1keV_vs_v02_reldiff", pd.Series(np.nan, index=LOWE.index)).reindex(L1.nuclide_id)
    L1["engine_grid_dependent"] = (SM.smin_MeV < -1.0).to_numpy()
    L1.to_parquet(os.path.join(OUT, "capture_v022.parquet"))
    unchanged = sum(1 for a_, b_ in zip(L.sigma_b, L1.sigma_b) if np.array_equal(np.asarray(a_), np.asarray(b_)))
    M1 = M2.copy()
    M1["macs30_mb"] = L1.set_index("nuclide_id").macs30_mb.reindex(M1.index)
    M1["alt_macs30_mb"] = L1.set_index("nuclide_id").alt_macs30_mb.reindex(M1.index)
    M1.reset_index().to_csv(os.path.join(OUT, "macs30_v022.csv"), index=False)
    MK = pd.DataFrame(mk).set_index("nuclide_id")
    K1 = K2.copy()
    for k in KTS:
        K1[f"macs{int(k)}_mb"] = MK[f"macs{int(k)}_mb"].reindex(K1.index)
    K1["alt_macs30_mb"] = M1.alt_macs30_mb.reindex(K1.index)
    for k in KTS:
        K1[f"share_below1keV_{int(k)}keV"] = MK[f"share_below1keV_{int(k)}keV"].reindex(K1.index)
    K1["below1keV_source"] = MK.below1keV_source.reindex(K1.index)
    K1["engine_grid_dependent"] = L1.set_index("nuclide_id").engine_grid_dependent.reindex(K1.index)
    K1.reset_index().to_csv(os.path.join(OUT, "macs_kt_v022.csv"), index=False)
    R1 = pd.DataFrame(rr); R1.to_csv(os.path.join(OUT, "rates_v022.csv"), index=False)
    with open(os.path.join(OUT, "reaclib_v022.dat"), "w", newline="\n") as f:
        f.write("\n".join(dat) + "\n")
    for a_, b_ in (("channels_v02.parquet", "channels_v022.parquet"), ("grid_np_v02.parquet", "grid_np_v022.parquet")):
        shutil.copyfile(os.path.join(SRC, a_), os.path.join(OUT, b_))
    AN = pd.DataFrame(anch); AN.to_csv(os.path.join(OUT, "anchored_rescale_v022.csv"), index=False)
    GD = LOWE.reindex(L1.nuclide_id)[["Z", "A", "tier", "composition"]].assign(
        smin_MeV=SM.smin_MeV.to_numpy(), smin_particle=SM.smin_particle.to_numpy(),
        short_grid_1keV_vs_v02_reldiff=gd.to_numpy(), short_vs_long_grid_maxrel_below1keV=LOWE.get("short_vs_full_maxrel_le1keV").reindex(L1.nuclide_id).to_numpy())
    GD = GD[L1.engine_grid_dependent.to_numpy()].reset_index()
    GD.to_csv(os.path.join(OUT, "grid_dependent_v022.csv"), index=False)
    # ---- summary
    P = pd.DataFrame(parts).set_index("nuclide_id")
    eng = MK.below1keV_source.str.startswith("engine")
    q = lambda x: dict(median_pct=100 * float(np.median(x)), p05_pct=100 * float(np.quantile(x, 0.05)),  # noqa: E731
                       p95_pct=100 * float(np.quantile(x, 0.95)), min_pct=100 * float(np.min(x)), max_pct=100 * float(np.max(x)))
    Pe = P[eng.reindex(P.index).to_numpy()]
    kt_tab = []
    for k in KTS:
        x = (K1[f"macs{int(k)}_mb"] / K21[f"macs{int(k)}_mb"]).to_numpy() - 1
        kt_tab.append(dict(kT_keV=int(k), v022_over_v021=q(x), lowE_alone=q(Pe[f"lowE_macs{int(k)}"].to_numpy() - 1),
                           masses_alone=q(P[f"mass_macs{int(k)}"].to_numpy() - 1),
                           share_below1keV_median_pct=100 * float(K1[f"share_below1keV_{int(k)}keV"].median()),
                           share_below1keV_max_pct=100 * float(K1[f"share_below1keV_{int(k)}keV"].max()),
                           v021_share_below1keV_median_pct=100 * float(K21[f"share_below1keV_{int(k)}keV"].median())))
    shr = np.array(sh_t9); R1i = R1.set_index("nuclide_id")
    rt_tab = []
    for t in T9:
        x = (R1i[f"rate_T9_{t:g}"] / R21[f"rate_T9_{t:g}"].reindex(R1i.index)).to_numpy() - 1
        rt_tab.append(dict(T9=float(t), v022_over_v021=q(x), lowE_alone=q(Pe[f"lowE_rate{t:g}"].to_numpy() - 1),
                           masses_alone=q(P[f"mass_rate{t:g}"].to_numpy() - 1),
                           share_below1keV_median_pct=100 * float(np.median(shr[:, list(T9).index(t)])),
                           share_below1keV_max_pct=100 * float(shr[:, list(T9).index(t)].max())))
    LO = LOWE.reindex(L1.nuclide_id)
    slope = []
    for el_, sl_, s_ in zip(lo_e, lo_s, L1.sigma_b):
        slope.append(float(np.log(s_[0] / sl_[0]) / np.log(1e3 / el_[0])))
    slope = np.array(slope)
    summ = dict(nuclides=len(L1), curves_above_1keV_unchanged=unchanged, curves_rescaled_anchored=len(AN),
                engine_grid_dependent=dict(nuclei=int(len(GD)), by_tier=GD.tier.value_counts().to_dict(), by_particle=GD.smin_particle.value_counts().to_dict(),
                                           short_grid_mismatch_gt_1e9_all=int((gd.abs() > 1e-9).sum()),
                                           short_grid_mismatch_gt_1e9_in_list=int((GD.short_grid_1keV_vs_v02_reldiff.abs() > 1e-9).sum()),
                                           abs_reldiff_1keV_gt_1pct=int((GD.short_grid_1keV_vs_v02_reldiff.abs() > 0.01).sum()),
                                           abs_reldiff_1keV_gt_10pct=int((GD.short_grid_1keV_vs_v02_reldiff.abs() > 0.1).sum()),
                                           in_Z26_83=int(((GD.Z >= 26) & (GD.Z <= 83)).sum())),
                below1keV_source=dict(engine=int(eng.sum()), one_over_v=int((~eng).sum()),
                                      one_over_v_reasons=MK.below1keV_source[~eng].str.replace(r" \(rel\. diff.*", "", regex=True)
                                      .str.replace(r": .*", "", regex=True).value_counts().to_dict(),
                                      grids=LO.grid[eng.reindex(LO.index).to_numpy()].value_counts().to_dict(),
                                      engine_points_repaired=int(LO.points_repaired.sum()),
                                      nuclei_with_repaired_points=int((LO.points_repaired > 0).sum())),
                engine_slope_2eV_1keV=dict(median=float(np.median(slope[eng.to_numpy()])), p05=float(np.quantile(slope[eng.to_numpy()], 0.05)),
                                           p95=float(np.quantile(slope[eng.to_numpy()], 0.95)), min=float(slope[eng.to_numpy()].min()),
                                           max=float(slope[eng.to_numpy()].max())),
                junction_reldiff_max_used=float(LO.junction_reldiff[eng.reindex(LO.index).to_numpy()].abs().max()),
                reproduce_v021_with_v021_rule=dict(macs_maxrel=float(P.v021_reproduced_macs.max()), rate_maxrel=float(P.v021_reproduced_rate.max())),
                anchored_macs30_eq_anchor_maxrel=float(np.max(np.abs(L1[L1.tier == "ANCHORED"].macs30_mb.to_numpy()
                                                                      / M2.loc[L1[L1.tier == "ANCHORED"].nuclide_id, "macs30_mb"].to_numpy() - 1))),
                masses=MS.mass_source.value_counts().to_dict(),
                macs_by_kT=kt_tab, rates_by_T9=rt_tab,
                reaclib_resid_median_dex=float(R1.reaclib_max_resid_dex.median()), reaclib_resid_p99_dex=float(R1.reaclib_max_resid_dex.quantile(0.99)),
                reaclib_resid_max_dex=float(R1.reaclib_max_resid_dex.max()),
                macs_all_finite_positive=bool(np.isfinite(K1[[f"macs{int(k)}_mb" for k in KTS]].to_numpy()).all()
                                              and (K1[[f"macs{int(k)}_mb" for k in KTS]].to_numpy() > 0).all()),
                rates_all_finite_positive=bool(np.isfinite(R1.filter(like="rate_T9").to_numpy()).all() and (R1.filter(like="rate_T9").to_numpy() > 0).all()),
                anchored=AN.to_dict("records"))
    with open(os.path.join(OUT, "build_summary_v022.json"), "w", newline="\n") as f:
        json.dump(summ, f, indent=1)
    print(json.dumps({k: v for k, v in summ.items() if k not in ("anchored", "macs_by_kT", "rates_by_T9")}, indent=1))
    for t in kt_tab:
        print(t["kT_keV"], {k: round(v["median_pct"], 3) for k, v in t.items() if isinstance(v, dict)}, round(t["share_below1keV_median_pct"], 2))
    for t in rt_tab:
        print(t["T9"], {k: (round(v["median_pct"], 3), round(v["p05_pct"], 2), round(v["p95_pct"], 2)) for k, v in t.items() if isinstance(v, dict)})
    print(AN.to_string())


if __name__ == "__main__":
    main()
