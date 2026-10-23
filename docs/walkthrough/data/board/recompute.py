#!/usr/bin/env python3
"""Recompute the class-A engine scoreboard from the files in this folder and compare with cells.csv.

    python3 recompute.py            # gaps + bootstrap 95 % CIs from d_pernuc.csv / k_pernuc.csv
    python3 recompute.py --rows     # also rebuild d_pernuc.csv from the per-measurement residuals in d_rows.csv.gz
    python3 recompute.py --labels   # also compare capture labels with a trust-weighted mean of their EXFOR datasets (approximate)
    python3 recompute.py --table    # print every engine cell

Standard library only, plus numpy if it is installed. With numpy (numpy.random.default_rng, PCG64) the bootstrap
draws are the same as the census's, so the CIs are reproduced to rounding. Without numpy the gaps are still exact,
but the CIs come from Python's own random generator: they will differ slightly from cells.csv and a verdict whose
interval end sits near zero can differ.

Verdict: WIN if the interval's upper end < 0, LOSS if its lower end > 0, TIE otherwise; N/A (not counted) when the rival gives
no value, when 5 or fewer nuclei are scored, or when the rival's error exceeds 1 dex (a failed rival run). cells.csv keeps the
gap, interval and scores of such cells and says why in `na_reason`. A stellar-capture band with no scored nuclide at all
(Z < 20 and Z >= 84: no compiled value there is a measurement) is not a comparison: `na_reason` "empty band", not counted.
"""
import csv, gzip, math, os, random, sys
from collections import OrderedDict, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
try:
    import numpy as np
except ImportError:  # stdlib fallback
    np = None

NB = 2000                 # bootstrap replicates
SEED_D = 20261001         # D cells (data views): paired nucleus bootstrap
SEED_K = 20261004         # K cells (MACS bands): nucleus bootstrap
TOL = 1e-8                # agreement required with cells.csv (dex); the files carry 10-12 significant digits
RIVALS = ["TALYS-2.24", "TALYS-port", "R_T", "CoH3", "YAHFC"]   # order of d_pernuc.csv


def fnum(s):
    return float(s) if s not in ("", None) else float("nan")


def read_csv(name):
    op = gzip.open if name.endswith(".gz") else open
    with op(os.path.join(HERE, name), "rt", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def percentile(xs, q):  # numpy's default (linear) percentile
    xs = sorted(xs); k = (len(xs) - 1) * q / 100.0; i = int(math.floor(k)); j = min(i + 1, len(xs) - 1)
    return xs[i] + (xs[j] - xs[i]) * (k - i)


def counts_iter(n, seed):
    """Yields NB vectors of resampling counts (how often each nucleus is drawn)."""
    if np is not None:
        rng = np.random.default_rng(seed)
        C = np.stack([np.bincount(rng.integers(0, n, n), minlength=n) for _ in range(NB)]).astype(float)
        for c in C: yield c
    else:
        rng = random.Random(seed)
        for _ in range(NB):
            c = [0.0] * n
            for _ in range(n): c[rng.randrange(n)] += 1.0
            yield c


# ---------------------------------------------------------------- D cells (data views)
def d_score(S, W, agg, c=None):
    """Error of one code over the nuclei: S_i = sum_rows w r^2, W_i = sum_rows w, per nucleus i; c = bootstrap counts.
    agg 'rows': sqrt(sum c S / sum c W)  (every measurement row counts, by its weight)
    agg 'nucw': sqrt(sum c (S/W) / sum c) (every nucleus counts equally)"""
    c = [1.0] * len(S) if c is None else c
    if agg == "rows":
        return math.sqrt(sum(ci * s for ci, s in zip(c, S)) / sum(ci * w for ci, w in zip(c, W)))
    m = [w > 0 for w in W]
    return math.sqrt(sum(ci * s / w for ci, s, w, mm in zip(c, S, W, m) if mm) / sum(ci for ci, mm in zip(c, m) if mm))


def d_cell(nucs):
    if len(nucs) < 3: return None
    agg = nucs[0]["agg"]; W = [float(r["W"]) for r in nucs]
    Sa = [float(r["S_ours"]) for r in nucs]; Sb = [float(r["S_rival"]) for r in nucs]
    a, b = d_score(Sa, W, agg), d_score(Sb, W, agg)
    d = [d_score(Sa, W, agg, c) - d_score(Sb, W, agg, c) for c in counts_iter(len(nucs), SEED_D)]
    return dict(n=len(nucs), ours=a, rival=b, gap=a - b, lo=percentile(d, 2.5), hi=percentile(d, 97.5))


def pernuc_from_rows(ours_col):
    """Rebuild d_pernuc.csv from d_rows.csv.gz: for each view (and its SURR variant) and rival, the rows with status
    'scored' ('scored_surrogate'), in file order; a row counts for a rival when both residuals are finite; nuclei in
    order of first appearance among the view's scored rows, nuclei with no counted row dropped.
    ours_col[(view, rival)] names our residual column for that cell (cells.csv, ours_residual): r_ours, except the
    (n,2n) views against TALYS-2.24, which use r_ours_talysgrid (see README)."""
    rows = read_csv("d_rows.csv.gz"); out = []
    views = sorted({r["view"] for r in rows})
    for v in views:
        for vn, st in ((v, "scored"), ("SURR " + v, "scored_surrogate")):
            g = [r for r in rows if r["view"] == v and r["status"] == st]
            if not g: continue
            for riv in RIVALS:
                acc = OrderedDict(); oc = ours_col.get((vn, riv), "r_ours")
                for r in g:
                    a, b, w = fnum(r[oc]), fnum(r["r_" + riv]), fnum(r["weight"])
                    e = acc.setdefault(r["nucleus"], [0, 0.0, 0.0, 0.0])
                    if math.isfinite(a) and math.isfinite(b) and math.isfinite(w):
                        e[0] += 1; e[1] += w; e[2] += w * a * a; e[3] += w * b * b
                i = 0
                for n, (k, W, Sa, Sb) in acc.items():
                    if k == 0: continue
                    out.append(dict(view=vn, rival=riv, order=i, nucleus=n, agg=g[0]["agg"], rows=k, W=W, S_ours=Sa, S_rival=Sb)); i += 1
    return out


# ---------------------------------------------------------------- K cells (MACS bands)
def k_cell(a, b):
    k = len(a)
    if k < 3: return None
    rms = lambda x: math.sqrt(sum(v * v for v in x) / len(x))
    d = []
    if np is not None:
        A, B = np.array(a), np.array(b); rng = np.random.default_rng(SEED_K)
        for _ in range(NB):
            i = rng.integers(0, k, k); d.append(float(np.sqrt(np.mean(A[i] ** 2)) - np.sqrt(np.mean(B[i] ** 2))))
    else:
        rng = random.Random(SEED_K)
        for _ in range(NB):
            i = [rng.randrange(k) for _ in range(k)]; d.append(rms([a[j] for j in i]) - rms([b[j] for j in i]))
    return dict(n=k, ours=rms(a), rival=rms(b), gap=rms(a) - rms(b), lo=percentile(d, 2.5), hi=percentile(d, 97.5))


def k_cells():
    """Returns ({(band, rival): cell or None}, {band: number of scored nuclides in it})."""
    K = read_csv("k_pernuc.csv"); out = {}; size = {}
    for lab in ("K185", "K126"):
        for band in ("all", "Z<20", "Z20-39", "Z40-59", "Z60-83", "Z>=84"):
            sel = [r for r in K if r["in_scope"] == "True" and (lab == "K185" or r["in_K126"] == "True") and (band == "all" or r["z_band"] == band)]
            size[f"{lab} {band}"] = len(sel)
            for riv in RIVALS:
                pr = [(fnum(r["err_ours"]), fnum(r["err_" + riv])) for r in sel]
                pr = [(x, y) for x, y in pr if math.isfinite(x) and math.isfinite(y)]
                out[(f"{lab} {band}", riv)] = k_cell([x for x, _ in pr], [y for _, y in pr]) if len(pr) >= 3 else None
    return out, size


MIN_NUCLEI = 6           # a comparison needs at least 6 nuclei ...
RIVAL_FAIL_DEX = 1.0     # ... and a rival error of at most 1 dex (above that the rival's run failed); otherwise N/A


def na_reason(c):
    """Why a cell is N/A ('' when it is scored). The rule is the same for every cell, whatever its verdict would be."""
    if c is None: return "rival gives no value or too few nuclei"
    if c["rival"] > RIVAL_FAIL_DEX: return "rival run failed"
    if c["n"] < MIN_NUCLEI: return "too few nuclei"
    return ""


def verdict(c):
    if na_reason(c): return "N/A"
    return "WIN" if c["hi"] < 0 else "LOSS" if c["lo"] > 0 else "TIE"


def main():
    args = set(sys.argv[1:])
    cells = [r for r in read_csv("cells.csv") if r["section"] == "engine"]
    pn = read_csv("d_pernuc.csv")
    if "--rows" in args:
        rb = pernuc_from_rows({(r["view"], r["rival"]): r["ours_residual"] for r in cells if r["block"] == "D"}); mx = 0.0
        assert len(rb) == len(pn), (len(rb), len(pn))
        for x, y in zip(rb, pn):
            assert (x["view"], x["rival"], x["nucleus"], int(x["order"]), int(x["rows"])) == (y["view"], y["rival"], y["nucleus"], int(y["order"]), int(y["rows"])), (x, y)
            for c in ("W", "S_ours", "S_rival"): mx = max(mx, abs(float(x[c]) - float(y[c])) / max(1.0, abs(float(y[c]))))
        print(f"--rows: d_pernuc.csv rebuilt from d_rows.csv.gz: {len(rb)} nucleus entries, same nuclei and order, max relative difference {mx:.1e}")
        pn = [{k: str(v) for k, v in r.items()} for r in rb]
    if "--labels" in args:
        check_labels()
    by = defaultdict(list)
    for r in pn: by[(r["view"], r["rival"])].append(r)
    for v in by.values(): v.sort(key=lambda r: int(r["order"]))
    K, ksize = k_cells()
    worst = 0.0; bad = []; table = []; tally = defaultdict(int)
    for r in cells:
        key = (r["view"], r["rival"])
        if r["block"] == "K" and ksize[r["view"]] == 0:   # empty band: not a comparison, never counted
            if (r["na_reason"], r["verdict"], r["counted_on_board"]) != ("empty band", "N/A", "False"): bad.append((key, "empty band", r["na_reason"], r["counted_on_board"]))
            table.append((r["block"], r["view"], r["rival"], None, "N/A", r["verdict"])); continue
        c = d_cell(by.get(key, [])) if r["block"] == "D" else K[key]
        v = verdict(c)
        if r["counted_on_board"] == "True": tally[v] += 1
        if v != r["verdict"]: bad.append((key, v, r["verdict"]))
        why = na_reason(c)
        if why and c is not None and why != r.get("na_reason"): bad.append((key, "na_reason", why, r.get("na_reason")))
        if c is not None:
            n_ref = int(r["n_nuclei"])
            if c["n"] != n_ref: bad.append((key, "n", c["n"], n_ref))
            for a, b in (("gap", "gap"), ("lo", "ci_lo"), ("hi", "ci_hi"), ("ours", "score_ours"), ("rival", "score_rival")):
                if np is None and a in ("lo", "hi"): continue
                worst = max(worst, abs(c[a] - float(r[b])))
        table.append((r["block"], r["view"], r["rival"], c, v, r["verdict"]))
    if "--table" in args or bad:
        print(f"{'blk':3} {'view':22} {'rival':10} {'n':>4} {'ours':>8} {'rival':>8} {'gap':>8} {'ci_lo':>8} {'ci_hi':>8}  verdict (cells.csv)")
        for blk, view, riv, c, v, ref in table:
            if c is None: print(f"{blk:3} {view:22} {riv:10} {'':>4} {'':>8} {'':>8} {'':>8} {'':>8} {'':>8}  {v:5} ({ref})"); continue
            print(f"{blk:3} {view:22} {riv:10} {c['n']:4d} {c['ours']:8.4f} {c['rival']:8.4f} {c['gap']:+8.4f} {c['lo']:+8.4f} {c['hi']:+8.4f}  {v:5} ({ref})")
    print(f"engine cells recomputed: {len(cells)} ({sum(r['na_reason'] == 'empty band' for r in cells)} of them empty MACS bands, not counted); counted on the board: " + ", ".join(f"{k} {tally[k]}" for k in ("WIN", "TIE", "LOSS", "N/A")))
    print(f"max |difference| vs cells.csv over gap, scores" + (", CI ends" if np is not None else " (CIs skipped: numpy not installed)") + f": {worst:.1e} dex (tolerance {TOL:.0e})")
    if np is None:
        print("note: without numpy the bootstrap uses Python's random module, so CI ends differ slightly from cells.csv")
    if bad:
        print("MISMATCHES:", *bad, sep="\n  ")
    ok = worst <= TOL and (not bad or np is None)
    print("REPRODUCED" if ok and not bad else "NOT REPRODUCED" if not ok else "gaps reproduced; verdict differences above come from the stdlib bootstrap")
    sys.exit(0 if ok else 1)


def check_labels():
    """Capture rows, approximate check. The scored label is a consensus over the EXFOR datasets in the energy bin, weighted by
    trust and by each dataset's uncertainty (with extra scatter added where datasets disagree); the per-dataset uncertainties
    are not in this package. This check uses trust weights only, excluded datasets left out:
    log10(exp(sum t ln x / sum t)). It agrees to rounding where the two weightings coincide and shows how far the
    uncertainty weighting moves the label elsewhere."""
    rows = {(r["view"], r["row"]): r for r in read_csv("d_rows.csv.gz") if r["view"].startswith("capture")}
    acc = defaultdict(lambda: [0.0, 0.0])
    for m in read_csv("measurements.csv.gz"):
        if not m["view"].startswith("capture") or m["decision"] == "excluded": continue
        t = float(m["trust"]); a = acc[(m["view"], m["row"])]; a[0] += t * math.log(float(m["value"])); a[1] += t
    d = sorted(abs(math.log10(math.exp(s / t)) - float(rows[k]["label_log10"])) for k, (s, t) in acc.items())
    same = sum(x < 1e-6 for x in d)
    print(f"--labels (approximate, trust weights only): {len(d)} capture rows; {same} agree within 1e-6 dex; "
          f"median |difference| {percentile(d, 50):.1e}, 95th percentile {percentile(d, 95):.1e}, max {d[-1]:.1e} dex")


if __name__ == "__main__":
    main()
