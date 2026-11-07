"""Independent checks of library v0.2.3 against v0.2.2 (writes library/v0.2.3/VERIFY_V023.json).

1. Nothing else changed. Every file is compared with its v0.2.2 counterpart:
   - parquet: every column (arrays included) equal as Arrow data, the schema equal;
   - CSV: every cell equal as text, column by column, in the v0.2.2 columns;
   - the other files byte for byte.
   Only the fields the errata names may differ (BUGTIER3 items A, B, F); the counts of changed cells are recorded.
2. No value changed. 1. shows that every curve, band, MACS and rate is v0.2.2's, bit for bit. In addition, the 21
   ANCHORED curves (above and below 1 keV), their MACS at every kT and their rates at every T9 are recomputed from v0.2
   with build_library_v022.py's own functions and the full-precision factor bookkeeping. They agree with the shipped
   numbers to < 1e-14 (relative). They are not all bit-identical: the same recompute of non-ANCHORED nuclides on this
   machine differs from v0.2.2 by up to 5.6e-16 too (numpy 1.26 and 2.5 alike), so the last-ulp differences come from the
   floating-point platform of the v0.2.2 build, not from the factor.
3. A: v02_factor is the full-precision `anchored_v02_factor`; v022_factor = v02_factor x v022_extra_factor equals the
   curve's own factor sigma(1 keV) / engine(1 keV) (rel. < 1e-12); every ANCHORED "blind curve x f" is that factor
   rounded to 3 decimals, in capture and macs30 alike.
4. B: model_form_max_dex_sub1MeV >= |log10(alt_value_30keV_b / sigma(31.8 keV))| for every model-form flagged nuclide.
5. F: macs_flag_<kT>keV is resolved_upper_ev > kT/10 exactly; macs_flag is set where any is; rate_flag_below_T9 is
   10 resolved_upper_ev / 86173.3 eV where that exceeds T9 = 0.01; macs30_flag is v0.2.2's.

usage (pandas, pyarrow, scipy):  python scripts/release/verify_library_v023.py
"""
import csv, hashlib, importlib.util, io, json, math, os, re

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
V2, V22, V23 = (os.path.join(ROOT, "library", v) for v in ("v0.2", "v0.2.2", "v0.2.3"))
KTS = [5, 8, 10, 15, 20, 25, 30, 40, 50, 60, 80, 100]
ALLOWED = {  # file -> columns that may differ from v0.2.2 (new columns are listed separately)
    "capture": {"value_source", "model_form_max_dex_sub1MeV"},
    "anchored_rescale": {"v02_factor", "v022_factor"},
    "macs30": {"value_source"},
    "macs_kt": {"macs_flag"},
    "rates": set(),
}
NEW_COLS = {"macs_kt": [f"macs_flag_{k}keV" for k in KTS], "rates": ["rate_flag_below_T9"]}
COPIES = ["below1keV_engine_v02x.parquet", "masses_v02x.csv", "compound_smin_v02x.csv", "grid_dependent_v02x.csv",
          "channels_v02x.parquet", "grid_np_v02x.parquet", "reaclib_v02x.dat"]


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def csv_text(p):
    rows = list(csv.reader(io.StringIO(open(p, "rb").read().decode("utf-8"), newline="")))
    return rows[0], rows[1:]


def main():
    B = load(os.path.join(ROOT, "scripts", "release", "build_library_v022.py"), "b22")
    out, ok = {}, True
    # ---------------------------------------------------------------- 1. nothing else changed
    diff = {}
    T22 = pq.read_table(os.path.join(V22, "capture_v022.parquet")); T23 = pq.read_table(os.path.join(V23, "capture_v023.parquet"))
    assert T22.schema.remove_metadata().equals(T23.schema.remove_metadata())
    d = {}
    for c in T22.column_names:
        if not T22.column(c).equals(T23.column(c)):
            a, b = T22.column(c).to_pylist(), T23.column(c).to_pylist()
            d[c] = sum(x != y for x, y in zip(a, b))
    diff["capture_v023.parquet"] = d
    for stem in ("anchored_rescale", "macs30", "macs_kt", "rates"):
        h2, r2 = csv_text(os.path.join(V22, f"{stem}_v022.csv")); h3, r3 = csv_text(os.path.join(V23, f"{stem}_v023.csv"))
        assert h3 == h2 + NEW_COLS.get(stem, []), stem
        assert [r[0] for r in r2] == [r[0] for r in r3], stem
        d = {}
        for j, c in enumerate(h2):
            n = sum(a[j] != b[j] for a, b in zip(r2, r3))
            if n:
                d[c] = n
        for c in NEW_COLS.get(stem, []):
            d[c + " (new)"] = len(r3)
        diff[f"{stem}_v023.csv"] = d
    for f in COPIES:
        same = sha(os.path.join(V22, f.replace("v02x", "v022"))) == sha(os.path.join(V23, f.replace("v02x", "v023")))
        diff[f.replace("v02x", "v023")] = "byte-identical to v0.2.2" if same else "DIFFERS"
        ok &= same
    for k, v in diff.items():
        stem = k.split("_v023")[0]
        if isinstance(v, dict):
            extra = {c for c in v if not c.endswith("(new)")} - ALLOWED[stem]
            ok &= not extra
            if extra:
                print("unexpected change", k, extra)
    out["changed_cells_vs_v022"] = diff
    out["only_named_fields_changed"] = bool(ok)
    # ---------------------------------------------------------------- 2. values unchanged: ANCHORED recomputed bit for bit
    C2 = pd.read_parquet(os.path.join(V2, "capture_v02.parquet")).set_index("nuclide_id")
    M2 = pd.read_csv(os.path.join(V2, "macs30_v02.csv")).set_index("nuclide_id")
    C = pd.read_parquet(os.path.join(V23, "capture_v023.parquet")).set_index("nuclide_id")
    LOWE = pd.read_parquet(os.path.join(V23, "below1keV_engine_v023.parquet")).set_index("nuclide_id")
    MS = pd.read_csv(os.path.join(V23, "masses_v023.csv")).set_index("nuclide_id")
    K = pd.read_csv(os.path.join(V23, "macs_kt_v023.csv"), float_precision="round_trip").set_index("nuclide_id")
    R = pd.read_csv(os.path.join(V23, "rates_v023.csv"), float_precision="round_trip").set_index("nuclide_id")
    AR = pd.read_csv(os.path.join(V23, "anchored_rescale_v023.csv"), float_precision="round_trip").set_index("nuclide_id")
    M30 = pd.read_csv(os.path.join(V23, "macs30_v023.csv"), float_precision="round_trip").set_index("nuclide_id")
    kt_rate = B.T9 * B.KB_EV_PER_GK
    bit, worst, anch = 0, 0.0, []
    for n in C.index[C.tier == "ANCHORED"]:
        e = np.asarray(C2.at[n, "energy_ev"], float); s = np.asarray(C2.at[n, "sigma_b"], float)
        M = float(MS.at[n, "mass_u"]); r_ = M / (M + B.M_N_U); mu = B.M_N_U * M / (B.M_N_U + M)
        el, sl, _ = B.low_part(LOWE.loc[n], s[0])
        ea, sa = np.r_[el, e], np.r_[sl, s]
        f = float(M2.at[n, "macs30_mb"]) / (B.macs_cm(ea, sa, r_, 3e4)[0][0] * 1e3)
        s, sl, sa = s * f, sl * f, sa * f
        m = B.macs_cm(ea, sa, r_, np.array(KTS, float) * 1e3)[0] * 1e3
        rt = B.rate(B.macs_cm(ea, sa, r_, kt_rate)[0], kt_rate, mu)
        got = [np.asarray(C.at[n, "sigma_b"], float), np.asarray(C.at[n, "sigma_below1keV_b"], float),
               K.loc[n, [f"macs{k}_mb" for k in KTS]].to_numpy(float), R.loc[n, [f"rate_T9_{t:g}" for t in B.T9]].to_numpy(float)]
        want = [s, sl, m, rt]
        same = all(np.array_equal(g, w) for g, w in zip(got, want))
        bit += same
        worst = max(worst, max(float(np.max(np.abs(g / w - 1))) for g, w in zip(got, want)))
        # 3. A
        tot = float(LOWE.at[n, "anchored_v02_factor"]) * float(AR.at[n, "v022_extra_factor"])
        curve = float(C.at[n, "sigma_b"][0] / (LOWE.at[n, "engine_1keV_mb"] / 1e3))
        fs = [float(re.search(r"blind curve x ([0-9.]+) \(measured", v).group(1)) for v in (C.at[n, "value_source"], M30.at[n, "value_source"])]
        anch.append(dict(nuclide_id=n, extra_factor_recomputed_eq_listed=bool(f == float(AR.at[n, "v022_extra_factor"])),
                         v02_factor_eq_anchored_v02_factor=bool(AR.at[n, "v02_factor"] == LOWE.at[n, "anchored_v02_factor"]),
                         v022_factor_vs_curve_rel=abs(float(AR.at[n, "v022_factor"]) / curve - 1), total_vs_curve_rel=abs(tot / curve - 1),
                         value_source_factor=fs[0], value_source_eq_round3=bool(fs[0] == round(curve, 3) and fs[1] == fs[0]),
                         capture_eq_macs30_value_source=bool(C.at[n, "value_source"] == M30.at[n, "value_source"]),
                         curves_macs_rates_bit_identical=bool(same)))
    A = pd.DataFrame(anch)
    out["values_unchanged"] = dict(anchored_recomputed=int(len(A)), bit_identical=int(bit), max_rel_diff=worst,
                                   note="sigma_b and sigma_below1keV_b (capture), macs<kT>_mb (macs_kt) and rate_T9_* (rates) of the 21 "
                                        "ANCHORED nuclides, recomputed from v0.2 with build_library_v022.py's functions")
    out["values_unchanged"].update({"numpy": np.__version__, "recompute_ok_lt_1e-14": bool(worst < 1e-14)})
    ok &= worst < 1e-14
    out["A_anchored"] = dict(rows=anch, all_v02_factor_full_precision=bool(A.v02_factor_eq_anchored_v02_factor.all()),
                             max_v022_factor_vs_curve_rel=float(A.v022_factor_vs_curve_rel.max()),
                             all_value_source_eq_round3=bool(A.value_source_eq_round3.all()),
                             all_capture_eq_macs30_value_source=bool(A.capture_eq_macs30_value_source.all()))
    ok &= bool(A.v02_factor_eq_anchored_v02_factor.all() and A.v022_factor_vs_curve_rel.max() < 1e-12
               and A.value_source_eq_round3.all() and A.capture_eq_macs30_value_source.all())
    vs22 = pd.read_parquet(os.path.join(V22, "capture_v022.parquet"), columns=["nuclide_id", "value_source"]).set_index("nuclide_id").value_source
    out["A_anchored"]["value_source_changed"] = {n: [re.search(r"x ([0-9.]+)", vs22[n]).group(1), re.search(r"x ([0-9.]+)", C.at[n, "value_source"]).group(1)]
                                                 for n in C.index if vs22[n] != C.at[n, "value_source"]}
    # ---------------------------------------------------------------- 4. B
    e = np.asarray(C.energy_ev.iloc[0], float); k31 = int(np.argmin(np.abs(np.log(e / 3e4))))
    F = C[C.model_form_flag != "none"]
    dex = np.array([abs(math.log10(a / np.asarray(s, float)[k31])) for a, s in zip(F.alt_value_30keV_b, F.sigma_b)])
    out["B_model_form"] = dict(flagged=int(len(F)), grid_point_eV=float(e[k31]),
                               max_dex_ge_alt_at_31_8keV=bool((F.model_form_max_dex_sub1MeV.to_numpy() >= dex - 1e-12).all()),
                               gg_deadend=C.loc[C.model_form_flag == "gg_deadend", "model_form_max_dex_sub1MeV"].to_dict())
    ok &= out["B_model_form"]["max_dex_ge_alt_at_31_8keV"]
    # ---------------------------------------------------------------- 5. F
    ru = C.resolved_upper_ev.reindex(K.index)
    per = {}
    for k in KTS:
        want = (ru > k * 100.0).fillna(False).to_numpy()
        got = K[f"macs_flag_{k}keV"].astype(str).eq("True").to_numpy()
        per[f"{k}keV"] = dict(flagged=int(got.sum()), eq_criterion=bool(np.array_equal(got, want)))
        ok &= per[f"{k}keV"]["eq_criterion"]
    anyf = K[[f"macs_flag_{k}keV" for k in KTS]].astype(str).eq("True").any(axis=1)
    K22 = pd.read_csv(os.path.join(V22, "macs_kt_v022.csv")).set_index("nuclide_id")
    newly = anyf & K22.macs_flag.isna()
    rf = R.rate_flag_below_T9; want_rf = 10 * C.resolved_upper_ev.reindex(R.index) / 86173.3
    want_rf = want_rf.where(want_rf > 0.01)
    M22 = pd.read_csv(os.path.join(V22, "macs30_v022.csv")).set_index("nuclide_id")
    out["F_macs_flag"] = dict(
        per_kT=per, macs_flag_set_iff_any=bool((K.macs_flag.notna() == anyf).all()), macs_flag_set=int(anyf.sum()),
        newly_flagged=int(newly.sum()), newly_flagged_by_tier=K.tier[newly].value_counts().to_dict(),
        newly_flagged_resolved_upper_eV_range=[float(ru[newly].min()), float(ru[newly].max())],
        rate_flag_below_T9_eq=bool(np.allclose(rf.fillna(-1), want_rf.fillna(-1), rtol=0, atol=0)), rate_flag_below_T9_set=int(rf.notna().sum()),
        macs30_flag_unchanged=bool(M22.macs30_flag.fillna("").equals(M30.macs30_flag.fillna("")) and
                                   (pd.read_parquet(os.path.join(V22, "capture_v022.parquet"), columns=["macs30_flag"]).macs30_flag.fillna("").to_numpy()
                                    == C.macs30_flag.fillna("").to_numpy()).all()))
    ok &= out["F_macs_flag"]["macs_flag_set_iff_any"] and out["F_macs_flag"]["rate_flag_below_T9_eq"] and out["F_macs_flag"]["macs30_flag_unchanged"]
    ok &= out["F_macs_flag"]["newly_flagged"] == 334
    out["all_checks_pass"] = bool(ok)
    with open(os.path.join(V23, "VERIFY_V023.json"), "w", newline="\n") as f:
        json.dump(out, f, indent=1, default=float)
    print(json.dumps({k: v for k, v in out.items() if k not in ("A_anchored",)}, indent=1, default=float))
    print(json.dumps({k: v for k, v in out["A_anchored"].items() if k != "rows"}, indent=1, default=float))
    print(A.drop(columns=["extra_factor_recomputed_eq_listed"]).to_string())
    print("extra factor recomputed == listed:", int(A.extra_factor_recomputed_eq_listed.sum()), "of", len(A))
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
