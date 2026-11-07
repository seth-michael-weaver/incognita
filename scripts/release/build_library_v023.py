"""Build library v0.2.3 from library v0.2.2: a corrections-only errata release (BUGTIER3 items A, B, D, F).

No cross section, band, MACS, rate or REACLIB fit changes. Every file is v0.2.2's, byte for byte where nothing in it
changes, and cell for cell otherwise, except these fields (docs/release/amendments/BUGTIER3.md):

A. ANCHORED factor bookkeeping. build_library_v022.py read the v0.2 factor of the 21 ANCHORED nuclides back from the
   3-decimal text of v0.2's `value_source` ("blind curve x 0.817"). The curve itself carries the exact factor. v0.2.3
   takes the v0.2 factor at full precision from `below1keV_engine_v022.parquet` (`anchored_v02_factor`), keeping the
   text as a cross-check (to 5e-4):
   - `anchored_rescale_v023.csv`: `v02_factor` and `v022_factor` (= v02_factor x v022_extra_factor) at full precision;
   - `value_source` of the 21 ANCHORED rows (`capture_v023.parquet`, `macs30_v023.csv`): "blind curve x <total>" now
     rounds the true total factor (the text changes for 5 of them).
B. `model_form_max_dex_sub1MeV` (`capture_v023.parquet`) was 0.0 for the 3 `gg_deadend` nuclides (Mo-86, Tc-87, Rh-105),
   the "not widened" convention. It is now |log10(alt_value_30keV_b / sigma)| at the grid point nearest 30 keV
   (31.8 keV), the one energy where their alternative is kept: a lower bound on the difference below 1 MeV.
F. Per-kT MACS resonance flag. `macs_flag` in `macs_kt_v022.csv` repeated `macs30_flag` (resolved resonances above
   3 keV, the criterion for kT = 30 keV) at every kT. v0.2.3 applies each kT's own criterion, resolved range above kT/10:
   - new columns `macs_flag_<kT>keV` (True/False) in `macs_kt_v023.csv`;
   - `macs_flag` is set where any of them is, and its text names the kT range;
   - new column `rate_flag_below_T9` in `rates_v023.csv`: rates at T9 below it integrate the resolved range
     (10 x resolved_upper_ev / (86173.3 eV x T9) > 1), empty where no grid T9 is flagged or the bound is unknown.
   `macs30_flag` (capture, macs30) is unchanged: its criterion is the 30 keV one.
D is a documentation change (README.md, BUILD.md). C and E are not applied (README.md, "Known issues").

usage (pandas, pyarrow):
    python scripts/release/build_library_v023.py          # writes library/v0.2.3 (data files, build_summary_v023.json)
    python scripts/release/build_library_v023.py --sums   # (re)writes library/v0.2.3/SHA256SUMS, after the docs and VERIFY
"""
import csv, hashlib, io, json, math, os, re, shutil, sys

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
V2 = os.path.join(ROOT, "library", "v0.2")
SRC = os.path.join(ROOT, "library", "v0.2.2")
OUT = os.path.join(ROOT, "library", "v0.2.3")
KTS = [5, 8, 10, 15, 20, 25, 30, 40, 50, 60, 80, 100]  # keV
KB_EV_PER_GK = 86173.3                                    # as v0.2 / v0.2.2
T9_MIN = 0.01                                             # lowest T9 of the rate grid
TEXT_TOL = 5e-4                                           # the 3-decimal text vs the exact factor
ANCH_RE = re.compile(r"blind curve x ([0-9.]+) \(measured MACS30 anchor")
COPIES = ["below1keV_engine", "masses", "compound_smin", "grid_dependent", "channels", "grid_np", "reaclib"]
EXT = {"below1keV_engine": "parquet", "channels": "parquet", "grid_np": "parquet", "reaclib": "dat"}


def name(stem, tag):
    return f"{stem}_{tag}.{EXT.get(stem, 'csv')}"


def read_csv_text(path):
    raw = open(path, "rb").read()
    rows = list(csv.reader(io.StringIO(raw.decode("utf-8"), newline="")))
    assert write_csv_text(rows) == raw, f"{path}: csv round trip is not byte-identical"
    return rows


def write_csv_text(rows):
    s = io.StringIO(newline="")
    csv.writer(s, lineterminator="\n").writerows(rows)
    return s.getvalue().encode("utf-8")


def flag_kts(ru):
    """kT values (keV) of the MACS table whose window reaches the resolved range: resolved_upper_ev > kT/10."""
    if ru is None or not math.isfinite(ru):
        return []
    return [k for k in KTS if ru > k * 1e3 / 10]


def macs_flag_text(ru, kts):
    if not kts:
        return ""
    rng = "every kT in this file (5-100 keV)" if len(kts) == len(KTS) else f"kT <= {kts[-1]} keV"
    return (f"resolved resonances above kT/10 for {rng} (measured-resonance bound {ru / 1e3:.3g} keV): these MACS "
            f"integrate a region the curve makes no claim in; use a measured value")


def rate_flag_t9(ru):
    """T9 below which the rate's kT window reaches the resolved range (kT/10 < resolved_upper_ev); None if no grid T9."""
    if ru is None or not math.isfinite(ru):
        return None
    t = 10 * ru / KB_EV_PER_GK
    return t if t > T9_MIN else None


def main():
    os.makedirs(OUT, exist_ok=True)
    diff = {}  # file -> {column: changed cells}
    # ---- byte-identical copies
    for stem in COPIES:
        shutil.copyfile(os.path.join(SRC, name(stem, "v022")), os.path.join(OUT, name(stem, "v023")))
    # ---- capture: value_source (A, 21 ANCHORED), model_form_max_dex_sub1MeV (B, 3 gg_deadend)
    T = pq.read_table(os.path.join(SRC, "capture_v022.parquet"))
    C = T.to_pylist()
    LOWE = {r["nuclide_id"]: r for r in pq.read_table(os.path.join(SRC, "below1keV_engine_v022.parquet")).to_pylist()}
    V02 = {r["nuclide_id"]: r["value_source"] for r in pq.read_table(os.path.join(V2, "capture_v02.parquet"),
                                                                      columns=["nuclide_id", "value_source"]).to_pylist()}
    AR = read_csv_text(os.path.join(SRC, "anchored_rescale_v022.csv"))
    ah = AR[0]; ai = {c: i for i, c in enumerate(ah)}
    extra = {r[ai["nuclide_id"]]: float(r[ai["v022_extra_factor"]]) for r in AR[1:]}
    e = np.asarray(C[0]["energy_ev"], float); k31 = int(np.argmin(np.abs(np.log(e / 3e4))))
    new_vs, new_mf, anch = [], [], {}
    for r in C:
        n, vs, mf = r["nuclide_id"], r["value_source"], r["model_form_max_dex_sub1MeV"]
        if r["tier"] == "ANCHORED":
            f02 = float(LOWE[n]["anchored_v02_factor"])
            f02_text = float(ANCH_RE.search(V02[n]).group(1))
            assert abs(f02 - f02_text) <= TEXT_TOL, (n, f02, f02_text)
            tot = f02 * extra[n]
            curve = r["sigma_b"][0] / (LOWE[n]["engine_1keV_mb"] / 1e3)       # the factor the shipped curve carries
            assert abs(tot / curve - 1) < 1e-12, (n, tot, curve)
            old_tot = float(ANCH_RE.search(vs).group(1))
            assert abs(old_tot - tot) <= 2 * TEXT_TOL, (n, old_tot, tot)
            vs = ANCH_RE.sub(f"blind curve x {tot:.3f} (measured MACS30 anchor", vs, count=1)
            anch[n] = dict(v02_factor=f02, v02_factor_text=f02_text, v022_factor=tot, v022_factor_listed_v022=None,
                           value_source_factor_v022=old_tot, value_source_factor_v023=float(f"{tot:.3f}"))
        if r["model_form_flag"] == "gg_deadend":
            assert mf == 0.0, (n, mf)
            mf = abs(math.log10(r["alt_value_30keV_b"] / r["sigma_b"][k31]))
        new_vs.append(vs); new_mf.append(mf)
    old_vs = T.column("value_source").to_pylist(); old_mf = T.column("model_form_max_dex_sub1MeV").to_pylist()
    T1 = T.set_column(T.schema.get_field_index("value_source"), T.schema.field("value_source"),
                      pa.array(new_vs, type=T.schema.field("value_source").type))
    T1 = T1.set_column(T1.schema.get_field_index("model_form_max_dex_sub1MeV"), T1.schema.field("model_form_max_dex_sub1MeV"),
                       pa.array(new_mf, type=T.schema.field("model_form_max_dex_sub1MeV").type))
    pq.write_table(T1, os.path.join(OUT, "capture_v023.parquet"), compression="snappy")
    diff["capture_v023.parquet"] = {"value_source": sum(a != b for a, b in zip(old_vs, new_vs)),
                                    "model_form_max_dex_sub1MeV": sum(a != b for a, b in zip(old_mf, new_mf))}
    vs_new = dict(zip((r["nuclide_id"] for r in C), new_vs))
    ru = {r["nuclide_id"]: r["resolved_upper_ev"] for r in C}
    # ---- anchored_rescale: v02_factor, v022_factor at full precision (A)
    rows = [ah]; ch = {"v02_factor": 0, "v022_factor": 0}
    for r in AR[1:]:
        r = list(r); n = r[ai["nuclide_id"]]
        anch[n]["v022_factor_listed_v022"] = float(r[ai["v022_factor"]])
        for c, v in (("v02_factor", anch[n]["v02_factor"]), ("v022_factor", anch[n]["v022_factor"])):
            s = repr(float(v))
            ch[c] += s != r[ai[c]]; r[ai[c]] = s
        rows.append(r)
    open(os.path.join(OUT, "anchored_rescale_v023.csv"), "wb").write(write_csv_text(rows))
    diff["anchored_rescale_v023.csv"] = ch
    # ---- macs30: value_source (A)
    M = read_csv_text(os.path.join(SRC, "macs30_v022.csv")); mi = {c: i for i, c in enumerate(M[0])}
    n_vs = 0
    for r in M[1:]:
        v = vs_new[r[mi["nuclide_id"]]]
        n_vs += v != r[mi["value_source"]]; r[mi["value_source"]] = v
    open(os.path.join(OUT, "macs30_v023.csv"), "wb").write(write_csv_text(M))
    diff["macs30_v023.csv"] = {"value_source": n_vs}
    # ---- macs_kt: macs_flag per kT (F)
    K = read_csv_text(os.path.join(SRC, "macs_kt_v022.csv")); ki = {c: i for i, c in enumerate(K[0])}
    K[0] = K[0] + [f"macs_flag_{k}keV" for k in KTS]
    n_flag, newly, cleared_at = 0, [], {k: 0 for k in KTS}
    per_kt = {k: 0 for k in KTS}
    for r in K[1:]:
        n = r[ki["nuclide_id"]]; kts = flag_kts(ru[n]); old = r[ki["macs_flag"]]
        new = macs_flag_text(ru[n], kts)
        n_flag += new != old
        if new and not old:
            newly.append(n)
        assert not (old and not new), n  # every old flag (> 3 keV) stays flagged at kT <= 30 keV
        for k in KTS:
            per_kt[k] += k in kts
            cleared_at[k] += bool(old) and k not in kts
        r[ki["macs_flag"]] = new
        r.extend("True" if k in kts else "False" for k in KTS)
    open(os.path.join(OUT, "macs_kt_v023.csv"), "wb").write(write_csv_text(K))
    diff["macs_kt_v023.csv"] = {"macs_flag": n_flag, **{f"macs_flag_{k}keV (new)": len(K) - 1 for k in KTS}}
    # ---- rates: rate_flag_below_T9 (F)
    R = read_csv_text(os.path.join(SRC, "rates_v022.csv")); ri = {c: i for i, c in enumerate(R[0])}
    R[0] = R[0] + ["rate_flag_below_T9"]; n_rf = 0
    for r in R[1:]:
        t = rate_flag_t9(ru[r[ri["nuclide_id"]]])
        r.append("" if t is None else repr(float(t))); n_rf += t is not None
    open(os.path.join(OUT, "rates_v023.csv"), "wb").write(write_csv_text(R))
    diff["rates_v023.csv"] = {"rate_flag_below_T9 (new)": len(R) - 1}
    for stem in COPIES:
        diff[name(stem, "v023")] = "byte-identical copy of " + name(stem, "v022")
    # ---- summary
    tiers = {r["nuclide_id"]: r["tier"] for r in C}
    by_tier = {}
    for n in newly:
        by_tier[tiers[n]] = by_tier.get(tiers[n], 0) + 1
    known = sum(1 for v in ru.values() if v is not None and math.isfinite(v))
    summ = dict(
        release="v0.2.3", base="v0.2.2", nuclides=len(C), changed_fields=diff,
        A_anchored=dict(nuclides=len(anch), value_source_text_changed=diff["capture_v023.parquet"]["value_source"],
                        max_rel_listed_v022_total_vs_curve=max(abs(a["v022_factor_listed_v022"] / a["v022_factor"] - 1) for a in anch.values()),
                        max_abs_v02_text_vs_exact=max(abs(a["v02_factor_text"] - a["v02_factor"]) for a in anch.values()),
                        rows={n: a for n, a in anch.items()}),
        B_gg_deadend={r["nuclide_id"]: dict(v022=0.0, v023=m) for r, m in zip(C, new_mf) if r["model_form_flag"] == "gg_deadend"},
        F_macs_flag=dict(resolved_upper_known=known, flagged_at_any_kT=sum(1 for v in ru.values() if flag_kts(v)),
                         newly_flagged=len(newly), newly_flagged_by_tier=by_tier,
                         flagged_per_kT={f"{k}keV": per_kt[k] for k in KTS},
                         v022_flag_now_clear_per_kT={f"{k}keV": cleared_at[k] for k in KTS},
                         rate_flag_below_T9_set=n_rf),
    )
    with open(os.path.join(OUT, "build_summary_v023.json"), "w", newline="\n") as f:
        json.dump(summ, f, indent=1)
    print(json.dumps({k: v for k, v in summ.items() if k != "A_anchored"}, indent=1))
    for n, a in anch.items():
        print(n, {k: (round(v, 6) if isinstance(v, float) else v) for k, v in a.items()})


def write_sums():
    names = sorted(f for f in os.listdir(OUT) if f != "SHA256SUMS")
    lines = [f"{hashlib.sha256(open(os.path.join(OUT, f), 'rb').read()).hexdigest()}  {f}" for f in names]
    with open(os.path.join(OUT, "SHA256SUMS"), "w", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    for f_ in names:
        assert b"\r\n" not in open(os.path.join(OUT, f_), "rb").read() or f_.endswith(".parquet"), f"{f_}: CRLF"
    print("\n".join(lines))


if __name__ == "__main__":
    write_sums() if "--sums" in sys.argv else main()
