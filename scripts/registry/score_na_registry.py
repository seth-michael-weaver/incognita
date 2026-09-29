#!/usr/bin/env python3
"""Score the prospective (n,a) registry against NEW EXFOR measurements.

    score_na_registry.py --registry docs/registry/na-2026-09-22-v1 --watch DIR [--zip entry.zip] [--no-download]

Downloads the current IAEA EXFOR Entry File into DIR (only when the server copy changed), keeps
the entries that report a neutron (n,a) or (n,x)He-4 cross section on a registry target, parses
them with data.ingest.exfor, and scores every point in 5-20 MeV against the stamped predictions
(log-log interpolation on the registry grid) by the rule fixed in the registry README:
log10(model/data) for v1, hybrid and default TALYS, and whether v1 lies inside its 68/95 % bands.

Append-only: DIR/scores.csv gets one row per new point (deduplicated by subentry + energy);
DIR/REPORT.md is rewritten from all rows. Exit status 0 always; prints how many new points arrived.
"""
from __future__ import annotations

import argparse
import datetime as dt
import email.utils
import os
import re
import sys
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from data.ingest.download import UA  # noqa: E402  (IAEA answers 403 to the default urllib client string)
from data.ingest.exfor import build_measurements, iter_entry_texts, parse_entry  # noqa: E402

URL = "https://nds.iaea.org/nrdc/exfor-master/entry/entry.zip"
RX = re.compile(r"\(\s*(\d+)-([A-Z]+)-(\d+)\s*\(N,(A|X)\)")   # target Z-SYM-A (N,A...) or (N,X...)


def fetch(watch: Path) -> Path:
    """The entry file in `watch`, re-downloaded only when the server's Last-Modified is newer."""
    dst = watch / "entry.zip"
    req = urllib.request.Request(URL, method="HEAD", headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=120) as r:
        lm = r.headers.get("Last-Modified")
    remote = email.utils.parsedate_to_datetime(lm).timestamp() if lm else None
    if dst.exists() and remote is not None and dst.stat().st_mtime >= remote:
        return dst
    tmp = dst.with_suffix(".part")
    with urllib.request.urlopen(urllib.request.Request(URL, headers={"User-Agent": UA, "Accept": "*/*"}), timeout=600) as r, tmp.open("wb") as f:
        while chunk := r.read(1 << 20):
            f.write(chunk)
    os.replace(tmp, dst)
    if remote is not None:
        os.utime(dst, (remote, remote))
    return dst


def predictions(reg: Path) -> pd.DataFrame:
    p = pd.read_csv(reg / "predictions.csv")
    if (reg / "rivals.csv").exists():   # evaluated libraries on the same targets and grid: the head-to-head
        r = pd.read_csv(reg / "rivals.csv")
        p = p.merge(r.drop(columns=["nuclide_id", "nuclide"]), on=["Z", "A", "e_mev"], how="left")
    return p


def rivals(p: pd.DataFrame) -> list[str]:
    return sorted({c.split("_mb_", 1)[1] for c in p.columns if c.startswith("sigma_na_mb_")} - {"v1", "hybrid", "default_talys"})


def model_at(p: pd.DataFrame, e_mev: float, col: str) -> float:
    x, y = p.e_mev.to_numpy(float), p[col].to_numpy(float)
    ok = y > 0
    if ok.sum() < 2 or not (x[ok].min() <= e_mev <= x[ok].max()):
        return float("nan")
    return float(10 ** np.interp(e_mev, x[ok], np.log10(y[ok])))


def scan(zip_path: Path, targets: set[tuple[int, int]]):
    """Measurements on registry targets: (n,a) total or state-resolved, or (n,x)He-4, SIG."""
    for name, text in iter_entry_texts(zip_path):
        hits = {(int(z), int(a)) for z, _, a, _ in RX.findall(text)}
        if not hits & targets:
            continue
        try:
            entry = parse_entry(text)
            ms = build_measurements(entry)
        except Exception:  # noqa: BLE001 - one bad entry must not stop the watch
            continue
        for m in ms:
            d = m.model_dump() if hasattr(m, "model_dump") else vars(m)
            if str(d.get("projectile", "")).lower() != "n" or d.get("quantity") != "cross_section":
                continue
            if (int(d["target_z"]), int(d["target_a"])) not in targets:
                continue
            rx = str(d.get("reaction", "")).strip()
            if re.search(r"\(N,X\)2-HE-4,,SIG\)$", rx):
                kind = "nxa"
            elif re.search(r"\(N,A\)(\d+-[A-Z]+-\d+)?,,SIG\)$", rx):
                kind = "na"                      # total (n,a): no SF5 modifier, no isomer suffix on the product
            elif re.search(r"\(N,A\)\d+-[A-Z]+-\d+-(G|M\d?)", rx):
                kind = "na_state"                # state-resolved: the registry has no isomer split; logged, not scored
            else:
                continue
            vals = (d.get("renormalized") or {}).get("values") or (d.get("original") or {}).get("values")
            if vals is None:
                continue
            for e, v in zip(np.atleast_1d(d["energy_ev"]), np.atleast_1d(vals)):
                if 5e6 <= e <= 20e6 and v and v > 0:
                    yield dict(entry=d.get("entry"), subentry=d.get("subentry"), reaction=rx, kind=kind,
                               Z=int(d["target_z"]), A=int(d["target_a"]), e_mev=float(e) / 1e6,
                               data_mb=float(v) * 1e3, year=d.get("year"))


def score(rows: pd.DataFrame, preds: pd.DataFrame) -> pd.DataFrame:
    out = []
    for r in rows.itertuples():
        p = preds[(preds.Z == r.Z) & (preds.A == r.A)].sort_values("e_mev")
        if p.empty:
            continue
        if r.kind == "na_state":
            out.append({**r._asdict(), "lr_v1": np.nan, "lr_hybrid": np.nan, "lr_default": np.nan, "in68_v1": np.nan, "in95_v1": np.nan})
            continue
        v1col = "sigma_nxa_mb_v1" if r.kind == "nxa" else "sigma_na_mb_v1"
        v1 = model_at(p, r.e_mev, v1col)
        hy = model_at(p, r.e_mev, "sigma_na_mb_hybrid") * (v1 / model_at(p, r.e_mev, "sigma_na_mb_v1") if r.kind == "nxa" else 1.0)
        de = model_at(p, r.e_mev, "sigma_na_mb_default_talys")
        h68, h95 = float(p.log10_halfwidth68_v1.iloc[0]), float(p.log10_halfwidth95_v1.iloc[0])
        lv = np.log10(v1 / r.data_mb)
        riv = {f"lr_{nm}": np.log10(model_at(p, r.e_mev, f"sigma_{r.kind}_mb_{nm}") / r.data_mb) for nm in rivals(preds)}
        out.append({**r._asdict(), "lr_v1": lv, "lr_hybrid": np.log10(hy / r.data_mb), "lr_default": np.log10(de / r.data_mb),
                    "in68_v1": abs(lv) <= h68, "in95_v1": abs(lv) <= h95, **riv})
    return pd.DataFrame(out).drop(columns=["Index"], errors="ignore")


def report(s: pd.DataFrame, path: Path, reg: str) -> None:
    rms = lambda x: float(np.sqrt(np.mean(np.square(x))))
    L = [f"# (n,a) registry {reg}: prospective scores", "", f"Updated {dt.date.today()}. Points: {len(s)}, targets: {s.groupby(['Z', 'A']).ngroups if len(s) else 0}.", ""]
    st = s[s.kind == "na_state"] if len(s) else s
    if len(st):
        L.append(f"State-resolved (n,a) points logged but not scored (no isomer split in this registry): {len(st)}")
    s = s[s.kind != "na_state"] if len(s) else s
    if len(s):
        L += ["| model | rms log10(m/d) | median |", "|---|---|---|"]
        for c in ["v1", "hybrid", "default"] + [k[3:] for k in s.columns if k.startswith("lr_") and k[3:] not in ("v1", "hybrid", "default")]:
            x = s["lr_" + c].dropna()
            if len(x):
                L.append(f"| {c} | {rms(x):.4f} (n={len(x)}) | {np.median(x):+.3f} |")
        L += ["", f"v1 inside 68 % band: {s.in68_v1.mean():.0%}; inside 95 %: {s.in95_v1.mean():.0%}", "", s.to_string(index=False)]
    else:
        L.append("No measurement on a registry target yet.")
    path.write_text("\n".join(L) + "\n")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--registry", type=Path, required=True)
    ap.add_argument("--watch", type=Path, required=True)
    ap.add_argument("--zip", type=Path, default=None, help="use this entry file instead of downloading")
    ap.add_argument("--no-download", action="store_true")
    a = ap.parse_args(argv)
    a.watch.mkdir(parents=True, exist_ok=True)
    z = a.zip or (a.watch / "entry.zip" if a.no_download else fetch(a.watch))
    preds = predictions(a.registry)
    rows = pd.DataFrame(list(scan(z, set(zip(preds.Z, preds.A)))))
    new = score(rows, preds) if len(rows) else pd.DataFrame()
    log = a.watch / "scores.csv"
    old = pd.read_csv(log) if log.exists() else pd.DataFrame()
    if len(new):
        new["found"] = str(dt.date.today())
        if len(old):
            key = set(zip(old.subentry.astype(str), old.e_mev.round(4)))
            new = new[[(str(s), round(e, 4)) not in key for s, e in zip(new.subentry, new.e_mev)]]
        allrows = pd.concat([old, new], ignore_index=True)
        allrows.to_csv(log, index=False)
    else:
        allrows = old
    report(allrows, a.watch / "REPORT.md", a.registry.name)
    print(f"{dt.datetime.now().isoformat(timespec='seconds')} entry file {z} ({dt.datetime.fromtimestamp(z.stat().st_mtime).date()}): "
          f"{len(new)} new point(s) on registry targets; {len(allrows)} total")
    return 0


if __name__ == "__main__":
    sys.exit(main())
