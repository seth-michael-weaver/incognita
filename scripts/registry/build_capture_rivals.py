#!/usr/bin/env python3
"""Build the capture registry's rival table from libraries YOU stage (we do not redistribute library values: licences and the
INCOGNITA independence rule; libraries are scoring rivals only).

    build_capture_rivals.py --registry docs/registry/blind-2026-09-13-v0 --out DIR [--evaluated $INCOGNITA_EVALUATED]

Reads $INCOGNITA_EVALUATED/<stem>.parquet (JENDL-5, TENDL-2025, ENDF/B-VIII.1, JEFF-3.3, CENDL-3.2; staged by
data/ingest/build_evaluated.py, docs/release/INPUTS.md section 2), MT 102, ground state, and puts each library's capture on the
frozen registry grid (capture_ng_grid.csv.gz energies, log-log). resonance_upper_ev_<lib> = the library's resonance-region upper
bound (max of resolved and unresolved), which the scorer uses to skip points inside any resonance region.
Writes DIR/capture_rivals.csv.gz in the schema score_capture_registry.py reads. Missing libraries are skipped with a message."""
from __future__ import annotations
import argparse, os, sys
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT))
from physics.grid import ENERGY_GRID_EV  # noqa: E402
LIBS = [("JENDL-5", "jendl5"), ("TENDL-2025", "tendl2025"), ("ENDF/B-VIII.1", "endfb81"), ("JEFF-3.3", "jeff33"), ("CENDL-3.2", "cendl32")]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--registry", type=Path, required=True); ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--evaluated", type=Path, default=Path(os.environ.get("INCOGNITA_EVALUATED", Path.home() / "nucleus" / "staging" / "evaluated")))
    a = ap.parse_args(argv); a.out.mkdir(parents=True, exist_ok=True)
    grid = pd.read_csv(a.registry / "capture_ng_grid.csv.gz")[["nuclide", "Z", "A", "energy_eV"]]
    out = grid.copy(); lg = np.log(np.asarray(ENERGY_GRID_EV, float)); n = 0
    for nm, stem in LIBS:
        p = a.evaluated / f"{stem}.parquet"
        if not p.exists():
            print(f"skip {nm}: {p} not staged"); continue
        x = pd.read_parquet(p, columns=["Z", "N", "iso", "mt", "values_b", "resolved_upper_ev", "unresolved_upper_ev"])
        x = x[(x.iso == 0) & (x.mt == 102)]
        tab = {(int(r.Z), int(r.Z + r.N)): r for r in x.itertuples()}
        sig, res = np.full(len(out), np.nan), np.full(len(out), np.nan)
        for (z, aa), idx in out.groupby(["Z", "A"]).groups.items():
            r = tab.get((int(z), int(aa)))
            if r is None: continue
            v = np.asarray(r.values_b, float); ok = v > 0
            if ok.sum() < 2: continue
            e = out.loc[idx, "energy_eV"].to_numpy(float)
            sig[np.asarray(idx)] = np.exp(np.interp(np.log(e), lg[ok], np.log(v[ok])))
            res[np.asarray(idx)] = max(np.nan_to_num(float(r.resolved_upper_ev), nan=0.0), np.nan_to_num(float(r.unresolved_upper_ev), nan=0.0))  # 0 = no resonance region
        out[f"sigma_b_{nm}"] = sig; out[f"resonance_upper_ev_{nm}"] = res; n += 1
    out.to_csv(a.out / "capture_rivals.csv.gz", index=False); print(f"{n} libraries -> {a.out / 'capture_rivals.csv.gz'}"); return 0


if __name__ == "__main__":
    sys.exit(main())
