"""Bin-average placement of an evaluated library on binned EXFOR rows (DATEDEXAM2).

Why: the staged library grids (3000 log points, `score.G`) SAMPLE the 0 K RECONR cross section. Below ~100 keV that is a
point inside a resonance ladder, while an EXFOR row of the dated tracks is the MEAN of a series' points in a 0.1-wide ln E bin.
DATEDEXAM compared the two and every library lost 0.1-0.3 dex below 100 keV, including libraries that had fitted those rows.

Rule (docs/release/dated/PREREG2.md, fixed before any library value was compared with a label):
- pointwise curve = NJOY2016 RECONR at 0 K, tolerance 0.1 % (the staging deck, `data.ingest.endf.njoy_deck`), lin-lin;
- channel -> MT: capture 102, total 1, elastic 2, n2n 16; inelastic 4, else the sum of MT 51-91; (n,p) 103, else the sum of
  MT 600-649; (n,a) 107, else the sum of MT 800-849. "present" means present in MF3 of the ORIGINAL evaluation (RECONR's
  redundant sums are not trusted for libraries that carry only a few channels, e.g. IRDFF-II);
- the row's bin is the data's: b = floor(ln(E_row) / 0.1), [e^{0.1 b}, e^{0.1 (b+1)}], clipped to [max(1 keV, emin_ev), 20 MeV]
  (emin_ev = the row's resonance cut, max(1 keV, 100 D0), below which the data points were dropped);
- the averaging window inside that bin: below 100 keV the whole bin (resonance structure; filtered-beam, activation and TOF
  resolution are all comparable to or wider than the level spacing there); from 100 keV up, the span of the row's own
  points [E_lo, E_hi] (`dated_row_spans.parquet`), widened symmetrically in ln E to at least 2 % (the energy spread of
  monoenergetic and D-T sources), then clipped to the bin.  A single 14.5 MeV activation point is not a mean over
  13.4-14.8 MeV of a steep excitation function (a full-bin average moved such rows by up to 0.18 dex; label-free audit);
- value = lethargy (1/E-weighted) average of the lin-lin curve over the bin, integrated exactly segment by segment:
  <sigma> = int sigma dE/E / int dE/E;
- threshold channels (inelastic, n2n, np, na): the data kept only points >= 1 mb, so the library average runs over the
  PENDF segments whose both ends are >= 1 mb (same rule on the library curve); no such segment -> not covered.
"""
from __future__ import annotations

import numpy as np

BIN = 0.1
EMIN, EMAX = 1e3, 2e7
THRESHOLD_Q = ('inelastic', 'n2n', 'np', 'na')
FLOOR_B = 1e-3
MAIN_MT = {'capture': 102, 'total': 1, 'elastic': 2, 'n2n': 16, 'inelastic': 4, 'np': 103, 'na': 107}
PARTIALS = {'inelastic': range(51, 92), 'np': range(600, 650), 'na': range(800, 850)}
WANT_MTS = sorted(set(MAIN_MT.values()) | {m for r in PARTIALS.values() for m in r})


def _sum_on_union(curves):
    """Sum lin-lin curves [(x, y)] on the union of their grids (0 outside each curve's table)."""
    x = np.unique(np.concatenate([c[0] for c in curves]))
    y = np.zeros_like(x)
    for cx, cy in curves:
        y += np.interp(x, cx, cy, left=0.0, right=0.0)
    return x, y


def channel_curves(pendf_mf3: dict, original_mts) -> dict:
    """pendf_mf3: {mt: (x, y)} from the RECONR tape; original_mts: MF3 MTs of the evaluation itself.
    -> {quantity: (x, y, source)} with source 'MT<n>' or 'sum MT<a>-<b> (k sections)'."""
    orig = set(int(m) for m in original_mts)
    out = {}
    for q, mt in MAIN_MT.items():
        if mt in orig and mt in pendf_mf3:
            x, y = pendf_mf3[mt]
            out[q] = (np.asarray(x, float), np.asarray(y, float), f'MT{mt}')
        elif q in PARTIALS:
            parts = [m for m in PARTIALS[q] if m in orig and m in pendf_mf3]
            if parts:
                x, y = _sum_on_union([tuple(map(np.asarray, pendf_mf3[m])) for m in parts])
                out[q] = (x, y, f'sum MT{PARTIALS[q].start}-{PARTIALS[q].stop - 1} ({len(parts)} sections)')
    return out


def lethargy_average(x, y, lo, hi, floor=None):
    """Exact 1/E-weighted average of the lin-lin curve (x, y) over [lo, hi]; with `floor`, only over segments whose both
    ends are >= floor.  Returns (value, lethargy fraction used)."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    if not (hi > lo) or hi <= x[0] or lo >= x[-1]:
        return np.nan, 0.0
    i0, i1 = np.searchsorted(x, lo, 'right'), np.searchsorted(x, hi, 'left')
    xs = np.concatenate([[lo], x[i0:i1], [hi]])
    ys = np.interp(xs, x, y, left=0.0, right=0.0)
    x1, x2, y1, y2 = xs[:-1], xs[1:], ys[:-1], ys[1:]
    ok = x2 > x1
    b = np.where(ok, (y2 - y1) / np.where(ok, x2 - x1, 1.0), 0.0)
    a = y1 - b * x1
    du = np.where(ok, np.log(np.where(ok, x2 / x1, 1.0)), 0.0)
    seg = a * du + b * (x2 - x1)
    if floor is not None:
        keep = ok & (y1 >= floor) & (y2 >= floor)
    else:
        keep = ok
    U = du[keep].sum()
    if U <= 0:
        return np.nan, 0.0
    return float(seg[keep].sum() / U), float(U / np.log(hi / lo))


SPAN_FROM = 1e5      # full bin below, points' span (>= MIN_SPAN in ln E) at and above
MIN_SPAN = 0.02


def row_bin(e_ev, emin_ev=None):
    b = np.floor(np.log(e_ev) / BIN)
    lo, hi = np.exp(BIN * b), np.exp(BIN * (b + 1))
    lo = max(lo, EMIN, emin_ev if emin_ev is not None and np.isfinite(emin_ev) else EMIN)
    return lo, min(hi, EMAX)


def row_window(e_ev, emin_ev=None, e_lo=None, e_hi=None):
    """The averaging window of one row (rule in the module docstring)."""
    lo, hi = row_bin(e_ev, emin_ev)
    if e_ev < SPAN_FROM or e_lo is None or e_hi is None or not (np.isfinite(e_lo) and np.isfinite(e_hi)):
        return lo, hi
    c, w = 0.5 * np.log(e_lo * e_hi), max(np.log(e_hi / e_lo), MIN_SPAN)
    return max(lo, np.exp(c - w / 2)), min(hi, np.exp(c + w / 2))


def place_rows(curves: dict, quantity, energy_ev, emin_ev, e_lo=None, e_hi=None):
    """-> (binavg_b, point_b, used_fraction, source) arrays for rows of one nucleus."""
    n = len(energy_ev)
    e_lo = np.full(n, np.nan) if e_lo is None else np.asarray(e_lo, float)
    e_hi = np.full(n, np.nan) if e_hi is None else np.asarray(e_hi, float)
    v = np.full(n, np.nan); p = np.full(n, np.nan); f = np.zeros(n); src = np.array([''] * n, dtype=object)
    for i, (q, e, em) in enumerate(zip(quantity, energy_ev, emin_ev)):
        c = curves.get(q)
        if c is None:
            continue
        x, y, s = c
        lo, hi = row_window(float(e), float(em), e_lo[i], e_hi[i])
        v[i], f[i] = lethargy_average(x, y, lo, hi, FLOOR_B if q in THRESHOLD_Q else None)
        p[i] = float(np.interp(e, x, y, left=np.nan, right=np.nan))
        src[i] = s
    return v, p, f, src
