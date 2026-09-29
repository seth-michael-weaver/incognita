#!/usr/bin/env python3
"""Calibration report for prediction intervals: does a 68 % (95 %) interval contain the measurement 68 % (95 %) of the time,
where does it, and does its width tell you anything?

Input: one table (parquet or csv) with one row per scored point, in log10 units (dex). The report needs, per row, the signed
error ``err = pred - y`` (or ``pred`` and ``y``, and it computes the difference) and ONE interval description:

  * ``h68`` and ``h95``: symmetric half-widths of the 68 % and 95 % intervals (what INCOGNITA ships), or
  * ``sigma`` (+ optional ``nu``): a Gaussian or Student-t predictive scale.

Output, for the whole table and for every stratum (``--by`` columns, and energy bands when ``energy_ev`` is present):

  * coverage at 68 % and 95 % with a percentile bootstrap CI that resamples GROUPS (``--group``, default ``nuclide_id``):
    rows of one nucleus are not independent, so a row bootstrap would give CIs that are far too narrow;
  * the PIT histogram (10 bins; flat = calibrated, U = too narrow, hump = too wide, slope = biased);
  * ECE: the mean |observed - nominal| coverage of central intervals at 5 %, 10 %, ..., 95 %, in percentage points;
  * sharpness ratio: rms error in the widest quarter of intervals / rms error in the narrowest quarter. 1 = the width does not
    rank the errors (the interval is right only on average); >= 1.5 is the project's target for a useful per-point width;
  * the median 68 % half-width (dex) and the rms error (dex), so calibration is never read without the width it costs.

PIT from an interval (``h68``/``h95``): the report assumes a symmetric Student-t through both quantiles, i.e. nu is solved per row
so that t_nu(0.975) / t_nu(0.84) = h95 / h68 (Gaussian when the ratio is <= 1.96 / 0.994), scale = h68 / t_nu(0.84). The 68 and
95 % coverages never depend on this assumption; the PIT histogram and ECE do, and the report says so.

Presets regenerate the release tables from the shipped exam files (``docs/release/exam``):

  python -m incognita.uq.calibration_report --preset tiers    [--exam DIR] [--out OUT.md]
  python -m incognita.uq.calibration_report --preset nostruct [--exam DIR] [--out OUT.md]
  python -m incognita.uq.calibration_report TABLE.parquet --by tier --out OUT.md       # any table with err + h68/h95

Folds 6-7 of the capture exam were the project's internal confirmation reserve. Presets stratify on DEV folds 0-5 only; the
all-fold row of ``tiers`` is printed once, because it is the already-published number, and never stratified.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

REPO = Path(__file__).resolve().parents[2]
BANDS = [(0, 1e4, "< 10 keV"), (1e4, 1e5, "10-100 keV"), (1e5, 1e6, "0.1-1 MeV"), (1e6, 1e7, "1-10 MeV"), (1e7, np.inf, "> 10 MeV")]
BANDS5 = [(0, 5e6, "< 5 MeV"), (5e6, np.inf, ">= 5 MeV")]
LEVELS = np.round(np.arange(0.05, 0.951, 0.05), 2)
Z68 = stats.norm.ppf(0.84)                      # 0.9945; the "68 %" interval is +-1 sigma = 68.27 %, we use 68 % exactly
NU_GRID = np.concatenate([np.geomspace(0.6, 200, 400), [np.inf]])
RATIO_GRID = np.array([stats.t.ppf(0.975, n) / stats.t.ppf(0.84, n) if np.isfinite(n) else stats.norm.ppf(0.975) / Z68
                       for n in NU_GRID])      # decreasing in nu


def _nu_from_ratio(r):
    """Student-t nu whose 97.5 / 84 % quantile ratio equals r (vectorised); inf when r is at or below the Gaussian ratio."""
    r = np.asarray(r, float)
    nu = np.interp(-r, -RATIO_GRID[:-1], NU_GRID[:-1])            # interp needs increasing x
    return np.where(r <= RATIO_GRID[-1] * 1.0005, np.inf, np.where(r >= RATIO_GRID[0], NU_GRID[0], nu))


def _cdf(z, nu):
    z, nu = np.asarray(z, float), np.broadcast_to(np.asarray(nu, float), np.shape(z))
    out = stats.norm.cdf(z)
    fin = np.isfinite(nu)
    if fin.any():
        out = out.copy(); out[fin] = stats.t.cdf(z[fin], nu[fin])
    return out


def _ppf(p, nu):
    nu = np.asarray(nu, float)
    return np.where(np.isfinite(nu), stats.t.ppf(p, np.where(np.isfinite(nu), nu, 1.0)), stats.norm.ppf(p))


def prepare(df: pd.DataFrame) -> pd.DataFrame:
    """Normalise a table to columns err, h68, h95, pit, halfwidth(level) inputs (scale, nu)."""
    d = df.copy()
    if "err" not in d:
        if not {"pred", "y"} <= set(d):
            raise SystemExit("need an 'err' column (pred - y) or both 'pred' and 'y'")
        d["err"] = d["pred"] - d["y"]
    if {"h68", "h95"} <= set(d):
        r = d["h95"] / d["h68"]
        d["nu"] = _nu_from_ratio(r)
        d["scale"] = d["h68"] / _ppf(0.84, d["nu"])
    elif "sigma" in d:
        d["scale"] = d["sigma"]
        if "nu" not in d:
            d["nu"] = np.inf
        d["h68"] = d["scale"] * _ppf(0.84, d["nu"]); d["h95"] = d["scale"] * _ppf(0.975, d["nu"])
    else:
        raise SystemExit("need interval columns: h68 and h95 (half-widths, dex), or sigma [+ nu]")
    ok = np.isfinite(d["err"]) & np.isfinite(d["h68"]) & np.isfinite(d["h95"]) & (d["h68"] > 0)
    d = d[ok].copy()
    d["pit"] = _cdf(d["err"].to_numpy() / d["scale"].to_numpy(), d["nu"].to_numpy())
    return d


def _stat(e, h68, h95, pit):
    a = np.abs(e)
    return 100 * np.mean(a <= h68), 100 * np.mean(a <= h95), _ece(pit)


def _ece(pit):
    """Mean |observed - nominal| central-interval coverage over 5 %..95 %, percentage points."""
    c = np.abs(np.asarray(pit) - 0.5) * 2                     # the central level at which the point is just covered
    return float(100 * np.mean([abs(np.mean(c <= L) - L) for L in LEVELS]))


def sharpness(err, h68):
    """rms error in the widest quarter of intervals / rms error in the narrowest quarter (ties at the cut go to both)."""
    e, h = np.asarray(err), np.asarray(h68)
    if len(e) < 8:
        return np.nan
    lo, hi = np.quantile(h, [0.25, 0.75])
    if hi <= lo:                                              # all widths (nearly) equal: the width cannot rank anything
        return np.nan
    return float(np.sqrt(np.mean(e[h >= hi] ** 2)) / np.sqrt(np.mean(e[h <= lo] ** 2)))


def bootstrap(d: pd.DataFrame, group: str, n_boot: int = 2000, seed: int = 20260923):
    """Group (nucleus) percentile bootstrap of coverage 68 / 95 and ECE: returns [(lo, hi)] x 3."""
    g = d[group].to_numpy() if group in d else np.arange(len(d))
    codes, uniq = pd.factorize(g)
    k = len(uniq)
    if k < 2:
        return [(np.nan, np.nan)] * 3
    a, h68, h95 = np.abs(d["err"].to_numpy()), d["h68"].to_numpy(), d["h95"].to_numpy()
    c = np.abs(d["pit"].to_numpy() - 0.5) * 2
    # per-group sums so each replicate is a weighted sum, not a row copy
    n = np.bincount(codes, minlength=k).astype(float)
    s68 = np.bincount(codes, weights=(a <= h68), minlength=k)
    s95 = np.bincount(codes, weights=(a <= h95), minlength=k)
    sL = np.stack([np.bincount(codes, weights=(c <= L), minlength=k) for L in LEVELS])
    rng = np.random.default_rng(seed)
    W = np.stack([np.bincount(rng.integers(0, k, k), minlength=k) for _ in range(n_boot)]).astype(float)
    N = W @ n
    cov68, cov95 = 100 * (W @ s68) / N, 100 * (W @ s95) / N
    ece = 100 * np.mean(np.abs((W @ sL.T) / N[:, None] - LEVELS[None, :]), axis=1)
    return [tuple(np.percentile(x, [2.5, 97.5])) for x in (cov68, cov95, ece)]


def summarise(d: pd.DataFrame, group: str, n_boot: int) -> dict:
    e, h68, h95, pit = d["err"].to_numpy(), d["h68"].to_numpy(), d["h95"].to_numpy(), d["pit"].to_numpy()
    c68, c95, ece = _stat(e, h68, h95, pit)
    ci = bootstrap(d, group, n_boot)
    hist = np.histogram(pit, bins=10, range=(0, 1))[0]
    return dict(rows=int(len(d)), groups=int(d[group].nunique()) if group in d else int(len(d)),
                cov68=c68, cov68_ci=ci[0], cov95=c95, cov95_ci=ci[1], ece=ece, ece_ci=ci[2],
                sharpness=sharpness(e, h68), median_h68=float(np.median(h68)), rms_err=float(np.sqrt(np.mean(e ** 2))),
                bias=float(np.mean(e)), pit_hist=[int(x) for x in hist])


def strata(d: pd.DataFrame, by: list[str], bands: bool) -> list[tuple[str, pd.DataFrame]]:
    out = [("all", d)]
    for col in by:
        for v, g in d.groupby(col, sort=True):
            out.append((f"{col} = {v}", g))
    if bands and "energy_ev" in d:
        for spec in (BANDS, BANDS5):
            for lo, hi, name in spec:
                g = d[(d.energy_ev >= lo) & (d.energy_ev < hi)]
                if len(g):
                    out.append((name, g))
    return out


def _pct(x, ci):
    return f"{x:.1f} [{ci[0]:.1f}, {ci[1]:.1f}]" if np.isfinite(ci[0]) else f"{x:.1f}"


def pit_bar(h):
    h = np.asarray(h, float); t = h.sum()
    if t == 0:
        return ""
    blocks = " ▁▂▃▄▅▆▇█"
    f = h / t * 10                                           # 1.0 = flat
    return "".join(blocks[min(8, int(round(x / 2 * 8)))] for x in f)   # full block = 2x the flat height


def report(d: pd.DataFrame, title: str, by: list[str], group: str, n_boot: int, bands: bool = True, min_rows: int = 30,
           note: str = "") -> tuple[str, list[dict]]:
    rows, lines = [], [f"## {title}", ""]
    if note:
        lines += [note, ""]
    lines += ["| stratum | rows (groups) | 68 % coverage [95 % CI] | 95 % coverage [95 % CI] | ECE, pp [CI] | sharpness | "
              "median h68 (dex) | rms err (dex) | bias (dex) | PIT (10 bins; flat = calibrated) |",
              "|---|---|---|---|---|---|---|---|---|---|"]
    for name, g in strata(d, by, bands):
        if len(g) < min_rows:
            lines.append(f"| {name} | {len(g)} ({g[group].nunique() if group in g else len(g)}) | too few rows (< {min_rows}) "
                         f"| | | | | | | |")
            continue
        s = summarise(g, group, n_boot); s["stratum"] = name; rows.append(s)
        sh = f"{s['sharpness']:.2f}" if np.isfinite(s["sharpness"]) else "n/a"
        lines.append(f"| {name} | {s['rows']} ({s['groups']}) | {_pct(s['cov68'], s['cov68_ci'])} | {_pct(s['cov95'], s['cov95_ci'])} | "
                     f"{_pct(s['ece'], s['ece_ci'])} | {sh} | {s['median_h68']:.3f} | {s['rms_err']:.3f} | {s['bias']:+.3f} | "
                     f"`{pit_bar(s['pit_hist'])}` {s['pit_hist']} |")
    return "\n".join(lines) + "\n", rows


HEADER = """# Calibration report (regenerated by `python -m incognita.uq.calibration_report`)

Coverage = share of points whose |pred - y| is within the interval half-width. CIs: percentile bootstrap over {group}s
({n_boot} replicates, fixed seed). ECE = mean |observed - nominal| coverage of central intervals 5-95 %, percentage points
(0 = perfect; it and the PIT histogram assume a Student-t through the 68 and 95 % half-widths; the coverages do not).
Sharpness = rms error in the widest quarter of intervals / rms error in the narrowest quarter (1 = the width does not rank
the errors; target >= 1.5). Strata with fewer than {min_rows} rows are not scored.
"""


# ---------------------------------------------------------------------------------------------------------------- presets
def preset_tiers(exam: Path, n_boot: int, min_rows: int):
    """The shipped capture interval (TIERS release rule) on the leave-nucleus-out rows it was built from."""
    r = pd.read_parquet(exam / "tier_rows.parquet")
    r = r[r.scored & ~r.ruleP_flagged]
    d = prepare(r)
    allfold = summarise(d, "nuclide_id", n_boot)
    dev = d[d.fold.isin(range(6))].copy()
    dev["region"] = pd.cut(dev.nuclide_id.str.slice(1, 4).astype(int), [0, 50, 82, 200], labels=["Z <= 50", "Z 51-82", "Z > 82"])
    note = ("Rows: leave-nucleus-out predictions of the capture model with the shipped 68 / 95 % half-widths "
            "(`tier_rows.parquet`, rule-P flagged rows removed). **The interval rule was fitted on these same rows "
            "(all folds), so this table is IN-SAMPLE for the interval: it shows the rule is internally consistent by "
            "stratum, not that it holds on new data.** Stratified on DEV folds 0-5 only.")
    txt, rows = report(dev, "Capture, shipped interval (TIERS rule), DEV folds 0-5", ["region", "fold"], "nuclide_id", n_boot,
                       min_rows=min_rows, note=note)
    top = (f"All folds 0-7 (the published README row; not stratified): {allfold['rows']} rows, "
           f"68 % {allfold['cov68']:.1f} / 95 % {allfold['cov95']:.1f}.\n\n")
    return top + txt, dict(all_folds=allfold, dev=rows)


def preset_nostruct(exam: Path, n_boot: int, min_rows: int):
    """No-structure-data interval (CAPFAR, out-of-fold) vs the field's 8-model spread band, same DEV cells."""
    X = pd.read_parquet(exam / "capture_blind_cells.parquet")
    M = ["s8l1", "s8l2", "s8l5", "s8l7", "s9l1", "s9l2", "s9l5", "s9l7"]
    L = np.stack([X[f"pred_strip_{m}"].to_numpy() for m in M])
    e = X.pred_recipe_strip.to_numpy() - X.target_log10.to_numpy()
    m = ((X.Z.to_numpy() <= 82) & np.isin(X.fold, range(6)) & np.isfinite(e) & np.isfinite(X.pred_ours_strip.to_numpy())
         & np.all(np.isfinite(L), 0))
    ev, sp, Ev, fv = e[m], np.std(L[:, m], 0), X.energy_ev.to_numpy()[m], X.fold.to_numpy()[m]
    lo = Ev < 1e5
    h68, h95 = np.zeros(len(ev)), np.zeros(len(ev))
    for k in range(6):                                    # same leave-one-DEV-fold-out fit as scripts/release/score_nostruct.py
        te = fv == k
        par = _nostruct_fit(ev[~te], sp[~te], lo[~te])
        h68[te], h95[te] = _nostruct_half_width(par, sp[te], Ev[te])
    base = pd.DataFrame(dict(nuclide_id=X.nuclide_id.to_numpy()[m], fold=fv, energy_ev=Ev, Z=X.Z.to_numpy()[m]))
    ours = prepare(base.assign(err=ev, h68=h68, h95=h95))
    # the field's band: sd of the 8 models around THEIR MEAN, used as a Gaussian 1-sigma (TENDL-astro practice, SPREAD_COVERAGE)
    field = prepare(base.assign(err=L[:, m].mean(0) - X.target_log10.to_numpy()[m], h68=sp, h95=1.96 * sp))   # +-1 / 1.96 sd, as published
    note1 = ("Rows: DEV folds 0-5, Z <= 82, the TENDL-style no-data recipe run with all structure data stripped (STRIP), "
             "i.e. what v0.1 ships for the 4,602 nuclei with no structure data. Interval = CAPFAR rule, fitted "
             "leave-one-DEV-fold-out (each fold's rows scored with parameters fitted on the other five folds).")
    note2 = ("Same cells. The field's band = standard deviation of the 8 strength x level-density TALYS models used as a "
             "+-1 sd (68 %) and +-1.96 sd (95 %) band around the 8-model mean (the model-spread uncertainty the field publishes, e.g. TENDL-astro).")
    t1, r1 = report(ours, "No structure data: shipped interval (CAPFAR), out-of-fold", [], "nuclide_id", n_boot, min_rows=min_rows,
                    note=note1)
    t2, r2 = report(field, "No structure data: the field's 8-model spread band, same cells", [], "nuclide_id", n_boot,
                    min_rows=min_rows, note=note2)
    return t1 + "\n" + t2, dict(ours=r1, field=r2)


def _conformal(r, lev):
    n = len(r)
    return float(np.quantile(r, min(1.0, np.ceil((n + 1) * lev) / n)))


def _nostruct_fit(e, sp, lo, s0_grid=np.arange(0.0, 0.205, 0.01)):
    best = None
    for s0 in s0_grid:
        s = np.sqrt(sp ** 2 + s0 ** 2); w = 0
        for b in (lo, ~lo):
            w += np.median(_conformal(np.abs(e[b]) / s[b], 0.68) * s[b]) * b.sum()
        if best is None or w < best[0]:
            best = (w, s0)
    s0 = best[1]; s = np.sqrt(sp ** 2 + s0 ** 2)
    return dict(s0=float(s0), **{k: [_conformal(np.abs(e[b]) / s[b], 0.68), _conformal(np.abs(e[b]) / s[b], 0.95)]
                                 for k, b in (("q_lt100keV", lo), ("q_ge100keV", ~lo))})


def _nostruct_half_width(par, sp, energy_ev):
    s = np.sqrt(np.asarray(sp) ** 2 + par["s0"] ** 2); lo = np.asarray(energy_ev) < 1e5
    return (np.where(lo, par["q_lt100keV"][0], par["q_ge100keV"][0]) * s,
            np.where(lo, par["q_lt100keV"][1], par["q_ge100keV"][1]) * s)


PRESETS = {"tiers": preset_tiers, "nostruct": preset_nostruct}


def _json_default(o):
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    raise TypeError(type(o))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("table", nargs="?", help="parquet/csv with err (or pred, y) and h68/h95 (or sigma [, nu])")
    ap.add_argument("--preset", choices=sorted(PRESETS), help="regenerate a release table from the shipped exam files")
    ap.add_argument("--exam", default=str(REPO / "docs" / "release" / "exam"), help="directory of the shipped exam files")
    ap.add_argument("--by", nargs="*", default=[], help="stratify by these columns (energy bands are added when energy_ev exists)")
    ap.add_argument("--group", default="nuclide_id", help="bootstrap resampling unit (default nuclide_id)")
    ap.add_argument("--n-boot", type=int, default=2000)
    ap.add_argument("--min-rows", type=int, default=30)
    ap.add_argument("--title", default="Calibration")
    ap.add_argument("--out", help="write markdown here (and the numbers to the same name with .json)")
    a = ap.parse_args(argv)
    head = HEADER.format(group=a.group, n_boot=a.n_boot, min_rows=a.min_rows)
    if a.preset:
        txt, data = PRESETS[a.preset](Path(a.exam), a.n_boot, a.min_rows)
    elif a.table:
        p = Path(a.table)
        df = pd.read_parquet(p) if p.suffix == ".parquet" else pd.read_csv(p)
        grp = a.group
        if grp not in df.columns:   # say so: resampling rows instead of nuclei gives CIs that are too narrow
            print(f"WARNING: no '{grp}' column: the bootstrap resamples ROWS; with several rows per nucleus the CIs are too narrow",
                  file=sys.stderr)
            df = df.assign(_row=np.arange(len(df))); grp = "_row"
            head = ("**Warning: the table has no nuclide column, so the bootstrap resamples rows; with several rows per nucleus the CIs "
                    "are too narrow.**\n\n" + HEADER.format(group="row", n_boot=a.n_boot, min_rows=a.min_rows))
        txt, data = report(prepare(df), a.title, a.by, grp, a.n_boot, min_rows=a.min_rows)
    else:
        ap.error("give a table or --preset")
    md = head + "\n" + txt
    print(md)
    if a.out:
        Path(a.out).write_text(md)
        Path(a.out).with_suffix(".json").write_text(json.dumps(data, indent=1, default=_json_default))


if __name__ == "__main__":
    main()
