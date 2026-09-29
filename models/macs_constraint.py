"""KADoNiS Maxwellian-averaged cross sections as a training constraint.

The MACS table has scored this project since WP-16 and never trained it. That is the wrong
way round for our failure mode. Against TENDL our error on odd-A targets is a per-nuclide
*normalisation* error -- the spread of per-nuclide bias is 0.1115 against their 0.0665,
while our shape is better than theirs (docs/results/beat-tendl.json). A MACS is an integral
of the cross section against a Maxwellian, so it constrains magnitude and almost nothing
else. It is the measurement shaped like the thing we get wrong.

What it buys, over the 225 modelled nuclides:

  213 nuclides covered (95%), 2,340 points across kT = 5 to 100 keV
  2,340 constraints against Stage C's 4,875 differential training bins -- 48% more
  26 nuclides have *zero* differential training bins; 21 of those have MACS
  30 more have between one and five bins, and 308 MACS points between them
  967 of the points are odd-A, the class the whole TENDL deficit lives in

Two honesties about "data they are not using". KADoNiS is derived from differential
measurements, many of which are in our EXFOR curation already, so this is not disjoint
information -- it is the same physics entering as an integral constraint rather than as a
scatter of points, which is a different and much stronger regulariser of normalisation.
Where it *is* close to new information is the quarter of the chart carrying almost no
differential bins, where the model currently trains on the surrogate and the features alone.

kT of 5-100 keV puts the Maxwellian's weight around E = 2kT, i.e. 10-200 keV, inside the
fast window every reported number lives on and above the resolved region.

CORRECTION (2026-09-12). This used to end "KADoNiS v1.0 predates the 2012 reporting cutoff, so
training on it cannot leak the test split." That is false. v1.0 is the compilation's fourth
update, published in 2014 -- Dillmann et al., Nucl. Data Sheets 120 (2014) 171,
arXiv:1408.3688 -- so it can fold in measurements made between 2012 and 2014. Any run with a
cutoff below 2014 and macs_weight > 0 was training on a table that may carry post-cutoff
information, which is the leak the cutoff exists to prevent. capture-2026 trains at cutoff 2026
and has no test split to leak into; the retrodiction models (v19, v20) do.

`load_macs` now takes `year_cutoff` and honours it: KADoNiS is dropped whole below
KADONIS_PUBLISHED, because a compilation carries no per-value year to filter on, and the EXFOR
Maxwellian rows are read from the dataset-level table, which does carry one.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import torch
from torch import Tensor

KADONIS_TSV = "raw/kadonis/kadonis1.0_macs.tsv"
# the band in which a Maxwellian average is both quoted and integrable on Stage C's own grid,
# which starts at 1 keV
KT_MIN_EV, KT_MAX_EV = 3.0e3, 2.0e5
# KADoNiS v1.0 is the fourth update of the compilation, published 2014. A time-split run whose
# cutoff is earlier cannot use it: one recommended value per (nuclide, kT), no year attached.
KADONIS_PUBLISHED = 2014
_EXFOR_MACS_CACHE: dict = {}
KT_COLUMNS = ("5", "10", "15", "20", "25", "30", "40", "50", "60", "80", "100(keV)")


def _kt_ev(col: str) -> float:
    return float(col.replace("(keV)", "")) * 1e3


def _exfor_macs(kt_ev: list[float], year_cutoff: int | None = None
                ) -> dict[tuple[int, int], list[tuple[float, float, float]]]:
    """Maxwellian-averaged capture measurements from this project's own EXFOR curation.

    KADoNiS v1.0 is 368 rows published in 2014, and it is the only MACS this project has ever
    used. The curated consensus carries a `mxw` kind -- the same quantity, measured, binned by
    kT -- for 342 nuclides, and 46 of the ones on our chart are absent from KADoNiS. 39 of
    those have no differential capture data at all, which is exactly the population the model
    cannot otherwise reach: a nuclide with a MACS reaches 0.1510 held-out against 0.2035 with
    nothing (docs/results/out-of-sample.md).

    KADoNiS wins wherever both have a nuclide. It is a compilation with renormalisations and
    corrections applied across experiments; these rows are the consensus of whatever EXFOR
    holds. Taking EXFOR only where KADoNiS is silent adds coverage without relitigating any
    nuclide the compilation already judged.

    Returns raw (kT, value, sigma) rather than snapping to the KADoNiS columns. Snapping to
    within 15% looked reasonable and kept only 5 of the 46 new nuclides: the ones the
    compilation lacks are, unsurprisingly, exactly the ones measured at a kT it does not carry.
    The loss integrates a Maxwellian at whatever kT it is handed, so the grid is extended
    instead.
    """
    import polars as pl

    from validation import cache as _vc

    # Cached per (cutoff, kT grid): train_ensemble calls train_stage_c once per member, so
    # without this the dataset-level table is re-read five times a fold and a cross-validation
    # run goes from fifty seconds a fold to seven minutes.
    ck = (year_cutoff, tuple(kt_ev))
    if ck in _EXFOR_MACS_CACHE:
        return _EXFOR_MACS_CACHE[ck]
    out: dict[tuple[int, int], list[tuple[float, float, float]]] = {}
    if year_cutoff is not None:
        # the consensus table carries no year, so a time-split run reads the dataset-level rows
        from validation.differential import core as _C
        try:
            pts = _C.load_exfor_points(mode="datasets", year_cutoff=None, mts=(102,),
                                       channel="capture", kinds=("mxw",))
        except Exception:                                    # noqa: BLE001
            _EXFOR_MACS_CACHE[ck] = out
            return out
        fr = pts.frame
        fr = pl.from_pandas(fr.to_pandas()) if hasattr(fr, "to_pandas") else fr
        idc = "nuclide_id" if "nuclide_id" in fr.columns else "nuclide"
        d = fr.filter(pl.col("year").is_not_null() & (pl.col("year") <= year_cutoff))
        ren = {idc: "nuclide", "meas_b": "consensus_b"}
        if "sigma_log10" in d.columns:
            ren["sigma_log10"] = "sigma_log"
        d = d.rename({k: v for k, v in ren.items() if k in d.columns})
    else:
        try:
            d = pl.read_parquet(_vc.channel_consensus("capture"))
        except Exception:                                    # noqa: BLE001
            return out
        if "kind" not in d.columns:
            return out
        d = d.filter(pl.col("mt") == 102, pl.col("kind") == "mxw")
    for r in d.iter_rows(named=True):
        nid, e, v = r.get("nuclide"), r.get("e_mid_ev"), r.get("consensus_b")
        if not (isinstance(nid, str) and nid.startswith("Z") and "NAT" not in nid):
            continue
        if e is None or v is None or not np.isfinite(e) or not np.isfinite(v) or e <= 0 or v <= 0:
            continue
        # kT below the model's own grid start cannot be integrated honestly -- the Maxwellian
        # at kT = 25 meV draws almost all its weight from the resonance region, which Stage C
        # does not speak in -- and above ~200 keV nothing quotes a MACS.
        if not (KT_MIN_EV <= e <= KT_MAX_EV):
            continue
        try:
            z, n = int(nid[1:4]), int(nid[5:8])
        except ValueError:
            continue
        sig = r.get("sigma_log") or 0.10
        out.setdefault((z, z + n), []).append((float(e), float(v), float(sig)))
    _EXFOR_MACS_CACHE[ck] = out
    return out


def _kadonis_keep() -> dict | None:
    """{(Z, A): 'all' | '30'}: which KADoNiS entries are measured (page procedure 'e' -> every kT; 'e+t' -> 30 keV only;
    theory 't'/'s', starred or missing values -> dropped), from models/data/kadonis_keep.csv (built by
    docs/release/indep_fix/classify.py from the KADoNiS pages; flags only, no values). INCOGNITA_KADONIS_KEEP = another
    table, or 'all' to use every entry (the pre-v0.1 behaviour)."""
    import os
    p = os.environ.get("INCOGNITA_KADONIS_KEEP", "") or str(Path(__file__).resolve().parent / "data" / "kadonis_keep.csv")
    if p == "all":
        return None
    import pandas as pd
    d = pd.read_csv(p)
    m = {"measured": "all", "measured_30keV_only": "30"}
    return {(int(z), int(a)): m[c] for z, a, c in zip(d.Z, d.A, d.cls) if c in m}


def load_macs(nuclide_ids: list[str], path: Path, exfor: bool = True,
              year_cutoff: int | None = None) -> tuple[Tensor, Tensor, Tensor]:
    """(macs_b, weight, kT_ev) with macs_b shaped (n_nuclides, n_kT), zero weight where absent.

    KADoNiS quotes millibarns and a single error at 30 keV; that error is used as a relative
    uncertainty for every kT of the nuclide, which is the compilation's own convention for
    the points it does not separately qualify.
    """
    import polars as pl

    d = pl.read_csv(path, separator="\t", truncate_ragged_lines=True, ignore_errors=True)
    cols = [c for c in KT_COLUMNS if c in d.columns]
    err_col = next((c for c in d.columns if "error" in c.lower()), None)
    table: dict[tuple[int, int], tuple[list[float], float]] = {}
    for row in d.iter_rows(named=True):
        try:
            z, a = int(row["Z"]), int(row["A"])
        except (TypeError, ValueError):
            continue
        if str(row.get("Isomer") or "").strip():        # ground states only
            continue
        vals = []
        for c in cols:
            v = row.get(c)
            try:
                vals.append(float(v))
            except (TypeError, ValueError):
                vals.append(math.nan)
        try:
            err = float(row.get(err_col)) if err_col else math.nan
        except (TypeError, ValueError):
            err = math.nan
        table[(z, a)] = (vals, err)

    keep = _kadonis_keep()
    if keep is not None:   # REDTEAM M8 / INDEP_FIX item 3: KADoNiS entries with experimental data only
        for key in list(table):
            k_ = keep.get(key)
            if k_ is None:
                del table[key]
            elif k_ == "30":
                vals, err = table[key]
                table[key] = ([v if c == "30" else math.nan for v, c in zip(vals, cols)], err)
    n, k = len(nuclide_ids), len(cols)
    macs = np.zeros((n, k), np.float64)
    weight = np.zeros((n, k), np.float64)
    if year_cutoff is not None and year_cutoff < KADONIS_PUBLISHED:
        print(f"[macs] KADoNiS v1.0 was published in {KADONIS_PUBLISHED} and this run's cutoff "
              f"is {year_cutoff}; dropping it whole so the time split stays honest. Only the "
              f"year-filtered EXFOR Maxwellian rows are used.", flush=True)
        table = {}
    for i, nid in enumerate(nuclide_ids):
        z, nn = int(nid[1:4]), int(nid[5:8])
        rec = table.get((z, z + nn))
        if rec is None:
            continue
        vals, err = rec
        for j, v in enumerate(vals):
            if not np.isfinite(v) or v <= 0:
                continue
            macs[i, j] = v * 1e-3                        # mb -> barn
            # relative error at 30 keV, floored so a quoted 0 does not become infinite weight
            rel = (err * 1e-3 / macs[i, j]) if (np.isfinite(err) and macs[i, j] > 0) else 0.10
            weight[i, j] = 1.0 / max(rel, 0.02) ** 2
    kt_ev = [_kt_ev(c) for c in cols]
    if exfor:
        extra = _exfor_macs(kt_ev, year_cutoff=year_cutoff)
        # KADoNiS wins where it actually speaks. Being LISTED there is not the same as being
        # usable: a row whose columns are all blank leaves weight at zero, and skipping on
        # membership rather than on coverage threw away most of what EXFOR adds.
        need = {nid: extra[(int(nid[1:4]), int(nid[1:4]) + int(nid[5:8]))]
                for i, nid in enumerate(nuclide_ids)
                if weight[i].sum() <= 0
                and (int(nid[1:4]), int(nid[1:4]) + int(nid[5:8])) in extra}
        if need:
            # extend the kT axis with whatever these nuclides were measured at, rather than
            # forcing their measurements onto columns the compilation happens to use
            want = sorted({round(float(e), 3) for rs in need.values() for e, _v, _s in rs})
            lg = np.log10(np.asarray(kt_ev, float))
            new_kt = [e for e in want
                      if np.min(np.abs(lg - np.log10(e))) > np.log10(1.05)]
            if new_kt:
                kt_ev = kt_ev + new_kt
                pad = np.zeros((n, len(new_kt)), np.float64)
                macs = np.concatenate([macs, pad], axis=1)
                weight = np.concatenate([weight, pad.copy()], axis=1)
            pos = {round(v, 3): j for j, v in enumerate(kt_ev)}
            lg = np.log10(np.asarray(kt_ev, float))
            for i, nid in enumerate(nuclide_ids):
                rs = need.get(nid)
                if not rs:
                    continue
                for e, v, sig in rs:
                    j = pos.get(round(e, 3))
                    if j is None:
                        j = int(np.argmin(np.abs(lg - np.log10(e))))
                    macs[i, j] = v
                    # sigma_log is the consensus fit's log10 scatter; a relative error is
                    # 10**sigma - 1, floored as the KADoNiS branch floors its quoted one
                    weight[i, j] = 1.0 / max(10.0 ** sig - 1.0, 0.02) ** 2
            print(f"[macs] {len(need)} nuclides carry an EXFOR Maxwellian average and no "
                  f"usable KADoNiS entry; kT axis {len(cols)} -> {len(kt_ev)} points",
                  flush=True)
    weight /= max(weight.max(), 1e-12)                   # O(1), so the loss weight means something
    return (torch.tensor(macs, dtype=torch.float32),
            torch.tensor(weight, dtype=torch.float32),
            torch.tensor(kt_ev, dtype=torch.float32))


def maxwellian_average_torch(grid_ev: Tensor, sigma_b: Tensor, kT_ev: Tensor,
                             mass_a: Tensor) -> Tensor:
    """Differentiable MACS(kT) = 2/sqrt(pi) * integral sigma x^2 e^-x dlnx, x = E_cm/kT.

    Trapezoids in ln x, matching validation.differential.core.maxwellian_average so the
    number trained against is the number reported. Returns (n_nuclides, n_kT) in barns.
    """
    # centre-of-mass energy, the frame KADoNiS quotes
    e_cm = grid_ev.unsqueeze(0) * (mass_a / (mass_a + 1.0)).unsqueeze(1)   # (N, E)
    x = e_cm.unsqueeze(-1) / kT_ev.view(1, 1, -1)                          # (N, E, K)
    lnx = torch.log(x.clamp_min(1e-30))
    kernel = x * x * torch.exp(-x)
    f = sigma_b.unsqueeze(-1) * kernel                                     # (N, E, K)
    dlnx = lnx[:, 1:, :] - lnx[:, :-1, :]
    integral = ((f[:, 1:, :] + f[:, :-1, :]) * 0.5 * dlnx).sum(dim=1)
    return (2.0 / math.sqrt(math.pi)) * integral


def macs_loss(pred_b: Tensor, grid_ev: Tensor, macs_b: Tensor, weight: Tensor,
              kT_ev: Tensor, mass_a: Tensor) -> Tensor:
    """Weighted mean square error in log10 MACS. Zero when nothing is covered."""
    if weight.sum() <= 0:
        return pred_b.sum() * 0.0
    pred = maxwellian_average_torch(grid_ev, pred_b, kT_ev, mass_a)
    d = torch.log10(pred.clamp_min(1e-12)) - torch.log10(macs_b.clamp_min(1e-12))
    return (weight * d.pow(2)).sum() / weight.sum().clamp_min(1e-9)
