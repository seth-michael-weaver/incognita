#!/usr/bin/env python3
"""Score the frozen capture registry (blind-2026-09-13-v0) and the evaluated libraries against NEW EXFOR capture data.

    score_capture_registry.py --registry DIR_WITH_capture_ng_grid [--rivals DIR] --watch DIR [--no-download]

--rivals: a directory holding capture_rivals.csv.gz built by build_capture_rivals.py from libraries YOU staged. We do not ship
library values (licences; INCOGNITA's independence rule). Without --rivals only the registry prediction is scored.

Scored nuclides: status_at_freeze in {never_measured, macs_only, thermal_or_integral_only} (no keV-MeV differential data at
freeze). Scored points: (n,g) SIG, 1 keV - 20 MeV, above the nuclide's resonance bound (registry `resolved_upper_ev` and every
library's resolved/unresolved upper limit), log-log on the 64-point grid. Metric: log10(model/data) for the registry
prediction and each library; v0 68 % band = registry log10_halfwidth. Append-only scores.csv, REPORT.md rewritten.
"""
from __future__ import annotations

import argparse, datetime as dt, re, sys
from pathlib import Path

import numpy as np, pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import score_na_registry as NA  # noqa: E402  (fetch, EXFOR parsing helpers)

RX = re.compile(r"\(\s*(\d+)-([A-Z]+)-(\d+)\s*\(N,G\)")


def scan(zip_path: Path, targets: set[tuple[int, int]]):
    for name, text in NA.iter_entry_texts(zip_path):
        if not {(int(z), int(a)) for z, _, a in RX.findall(text)} & targets:
            continue
        try:
            ms = NA.build_measurements(NA.parse_entry(text))
        except Exception:  # noqa: BLE001
            continue
        for m in ms:
            d = m.model_dump() if hasattr(m, "model_dump") else vars(m)
            if str(d.get("projectile", "")).lower() != "n" or d.get("quantity") != "cross_section":
                continue
            if (int(d["target_z"]), int(d["target_a"])) not in targets or not re.search(r"\(N,G\)[^,]*,,SIG\)$", str(d.get("reaction", ""))):
                continue
            vals = (d.get("renormalized") or {}).get("values") or (d.get("original") or {}).get("values")
            if vals is None:
                continue
            for e, v in zip(np.atleast_1d(d["energy_ev"]), np.atleast_1d(vals)):
                if 1e3 <= e <= 2e7 and v and v > 0:
                    yield dict(entry=d.get("entry"), subentry=d.get("subentry"), Z=int(d["target_z"]), A=int(d["target_a"]),
                               e_ev=float(e), data_b=float(v), year=d.get("year"))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--registry", type=Path, required=True); ap.add_argument("--rivals", type=Path, default=None)
    ap.add_argument("--watch", type=Path, required=True); ap.add_argument("--no-download", action="store_true")
    a = ap.parse_args(argv); a.watch.mkdir(parents=True, exist_ok=True)
    z = (a.watch / "entry.zip") if a.no_download else NA.fetch(a.watch)
    nuc = pd.read_csv(a.registry / "capture_nuclides.csv")
    nuc = nuc[nuc.status_at_freeze.isin(["never_measured", "macs_only", "thermal_or_integral_only"])]
    bound = {(int(r.Z), int(r.A)): float(r.resolved_upper_ev or 0) for r in nuc.itertuples()}
    grid = pd.read_csv(a.registry / "capture_ng_grid.csv.gz"); libs = []
    if a.rivals is not None and (a.rivals / "capture_rivals.csv.gz").exists():
        riv = pd.read_csv(a.rivals / "capture_rivals.csv.gz")
        grid = grid.merge(riv.drop(columns=["nuclide"]), on=["Z", "A", "energy_eV"], how="left")
        libs = [c[len("sigma_b_"):] for c in riv.columns if c.startswith("sigma_b_")]
    rows = pd.DataFrame(list(scan(z, set(bound))))
    out = []
    for r in rows.itertuples() if len(rows) else []:
        g = grid[(grid.Z == r.Z) & (grid.A == r.A)].sort_values("energy_eV")
        lo = max([bound[(r.Z, r.A)]] + [float(np.nanmax(g[f"resonance_upper_ev_{l}"])) for l in libs if g[f"resonance_upper_ev_{l}"].notna().any()])
        if r.e_ev <= lo:
            continue
        le = np.log(g.energy_eV.to_numpy())
        f = lambda col: float(10 ** np.interp(np.log(r.e_ev), le, np.log10(np.clip(g[col].to_numpy(float), 1e-30, None)))) if g[col].notna().all() else np.nan
        lv = np.log10(f("sigma_b") / r.data_b); hw = float(np.interp(np.log(r.e_ev), le, g.log10_halfwidth.to_numpy()))
        out.append({**r._asdict(), "lr_v0": lv, "in68_v0": abs(lv) <= hw, **{f"lr_{l}": np.log10(f(f"sigma_b_{l}") / r.data_b) for l in libs}})
    new = pd.DataFrame(out).drop(columns=["Index"], errors="ignore")
    log = a.watch / "scores.csv"; old = pd.read_csv(log) if log.exists() else pd.DataFrame()
    if len(new):
        new["found"] = str(dt.date.today())
        if len(old):
            k = set(zip(old.subentry.astype(str), old.e_ev.round(1))); new = new[[(str(s), round(e, 1)) not in k for s, e in zip(new.subentry, new.e_ev)]]
        old = pd.concat([old, new], ignore_index=True); old.to_csv(log, index=False)
    rms = lambda x: float(np.sqrt(np.mean(np.square(x))))
    L = [f"# capture registry blind-2026-09-13-v0 + libraries: prospective scores", "", f"Updated {dt.date.today()}. Points: {len(old)}.", ""]
    if len(old):
        L += ["| model | rms log10(m/d) (n) |", "|---|---|"] + [f"| {c[3:]} | {rms(old[c].dropna()):.4f} ({old[c].notna().sum()}) |" for c in old.columns if c.startswith("lr_")]
        L += ["", f"v0 inside 68 % band: {old.in68_v0.mean():.0%}"]
    else:
        L.append("No new keV-MeV capture measurement on a nuclide that had none at freeze.")
    (a.watch / "REPORT.md").write_text("\n".join(L) + "\n")
    print(f"{dt.datetime.now().isoformat(timespec='seconds')} capture registry: {len(new)} new point(s); {len(old)} total")
    return 0


if __name__ == "__main__":
    sys.exit(main())
