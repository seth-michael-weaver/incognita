"""Measured thermal capture and capture resonance integrals from EXFOR, one consensus per target.

These are the two capture observables the resolved-resonance region controls and that a
statistical ladder can be scored on without matching individual resonances:

* ``thermal``  sigma(n,gamma) at 2200 m/s (0.0253 eV), pointwise ``SIG`` with no SF8 modifier.
  Maxwellian-averaged values (SF8 ``MXW``) are NOT merged in: they carry the Westcott g factor,
  which is exactly the quantity a low-lying resonance moves.
* ``ri``       the capture resonance integral ``integral_{Ec}^{inf} sigma(E) dE / E`` (SF6 ``RI``,
  no SF8 modifier), with the cadmium cutoff Ec in the dataset's energy field restricted to
  0.4-0.6 eV so one model cutoff (0.5 eV) is comparable with every dataset kept.

Only total capture counts: partials to an isomer or ground state (SF4 ending ``-M``/``-G``, SF5
``PAR``/``M+``/...) are dropped, as are outdated subentries and non-ground-state targets. The
consensus is the median of the per-subentry log10 values; ``spread_log10`` is 1.4826 x MAD over
subentries (NaN with one), the disagreement between experiments.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
EXFOR_ALL = ROOT / "staging" / "exfor_all.parquet"

THERMAL_EV = 0.0253
RI_CUTOFF_EV = 0.5
_UNIT = {"b": 1.0, "B": 1.0, "MB": 1e-3, "mb": 1e-3, "MICRO-B": 1e-6, "KB": 1e3}


def _values_b(rec) -> np.ndarray:
    for key in ("renormalized", "original"):
        r = rec.get(key) if isinstance(rec, dict) else None
        if r is None or r.get("values") is None:
            continue
        f = _UNIT.get(str(r.get("units")))
        if f is None:
            continue
        v = np.asarray(r["values"], dtype=float) * f
        v = v[np.isfinite(v) & (v > 0)]
        if v.size:
            return v
    return np.empty(0)


def load_measurements(path: Path = EXFOR_ALL) -> pd.DataFrame:
    """One row per usable subentry: target, observable, value [b], year, entry."""
    cols = ["subentry", "entry", "target_id", "target_iso", "projectile", "mt", "quantity",
            "sf", "energy_ev", "original", "renormalized", "year", "outdated"]
    d = pd.read_parquet(path, columns=cols)
    d = d[(d.projectile == "n") & (d.mt == 102) & (d.target_iso == 0) & ~d.outdated]
    sf = pd.DataFrame(list(d.sf.map(lambda v: v or {})), index=d.index)
    for k in ("sf4", "sf5", "sf6", "sf7", "sf8"):
        d[k] = sf.get(k)
    partial = d.sf4.fillna("").str.contains(r"-[MG]\d?$") | d.sf5.notna() | d.sf7.notna()
    d = d[~partial & d.sf8.isna()]
    e0 = d.energy_ev.map(lambda a: float(a[0]) if a is not None and len(a) else np.nan)
    is_th = (d.sf6 == "SIG") & (d.quantity == "cross_section") & (np.abs(e0 / THERMAL_EV - 1) < 0.1)
    is_ri = (d.sf6 == "RI") & e0.between(0.4, 0.6)
    rows = []
    for obs, mask in (("thermal", is_th), ("ri", is_ri)):
        for idx, r in d[mask].iterrows():
            v = _values_b({"renormalized": r.renormalized, "original": r.original})
            if not v.size:
                continue
            rows.append({"target_id": r.target_id, "observable": obs,
                         "value_b": float(np.median(v)), "year": int(r.year),
                         "entry": r.entry, "subentry": r.subentry, "cutoff_ev": float(e0[idx])})
    return pd.DataFrame(rows)


def consensus(meas: pd.DataFrame, *, before_year: int | None = None) -> pd.DataFrame:
    """Median log10 over subentries per (target, observable)."""
    m = meas if before_year is None else meas[meas.year < before_year]
    m = m.assign(log10=np.log10(m.value_b))

    def agg(g: pd.DataFrame) -> pd.Series:
        lv = g.log10.to_numpy()
        med = float(np.median(lv))
        spread = float(1.4826 * np.median(np.abs(lv - med))) if lv.size > 1 else np.nan
        return pd.Series({"log10_b": med, "value_b": 10 ** med, "spread_log10": spread,
                          "n_subentries": int(lv.size), "n_entries": int(g.entry.nunique()),
                          "first_year": int(g.year.min()), "last_year": int(g.year.max())})

    out = m.groupby(["target_id", "observable"]).apply(agg, include_groups=False).reset_index()
    ids = out.target_id.str.extract(r"Z(\d+)N(\d+)M(\d+)").astype(int)
    out["Z"], out["N"] = ids[0], ids[1]
    out["A"] = out.Z + out.N
    return out
