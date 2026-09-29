"""EXFOR residual-production cross sections for proton and alpha beams (WP-25 training data).

An activation experiment measures the production of one nuclide -- or of one long-lived state
of it -- summed over every channel that makes it. EXFOR spells that as a residual in SF4 with
an optional state suffix, and a reaction code in SF3 that is either X or a named channel. For
this table the SF3 code is carried but NOT used to select: ``42-MO-100(P,2N)43-TC-99-M`` and
``42-MO-100(P,X)43-TC-99-M`` are the same measured quantity whenever (p,2n) is the only way
to make Tc-99 from Mo-100, and they are compared against the same TALYS ``rp`` table.

What is kept, and why each exclusion exists (every one is counted in the summary):

* ``quantity_kind == "sig"`` -- a plain cross section. The S-factor (``sig/sfc``) and
  sigma*sqrt(E) (``sig/rte``) parse as numbers in barn-like units and once drove a Ge-76
  residual to RMS 4.18 (docs/results/wp25-proton-first-data.md).
* SF5 empty or ``IND`` -> independent formation; ``M+`` -> ground state *including* the
  isomer's decay, which for an isomer that decays by IT is the all-states production and is
  stored as state ``""`` with ``branch="M+"`` so it can be dropped in one line.
* ``CUM`` (cumulative, including feeding by the decay of a parent made in the same
  irradiation) is kept with ``kind="cum"`` and never scored against an independent
  prediction. ``PAR`` / ``EM`` / ``PRE`` / ``(M)`` / everything else is dropped.
* SF8 relative (``REL``), ratio (``SIG/RAT`` in SF6) and limit data are dropped.
* The product must parse as ``Z-SYM-A[-state]``; ``ELEM/MASS`` and light ejectile
  "products" (``0-NN-1``, ``2-HE-4``) are dropped.
* ``outdated`` subentries are dropped; renormalised values (monitor-corrected where the
  EXFOR renormalisation step could) are used, in barns.

Output: ``staging/exfor_charged_production.parquet`` -- one row per point.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import polars as pl

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from data.curate.discrepancy import quantity_kind  # noqa: E402

OUT = REPO / "staging" / "exfor_charged_production.parquet"
_PRODUCT = re.compile(r"^(\d+)-([A-Z]+)-(\d+)(?:-(G|M\d?|M1\+M2|L\d*))?$")
UNIT_TO_MB = {"b": 1e3, "mb": 1.0, "ub": 1e-3, "microb": 1e-3}
SYMBOLS = (
    "H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn "
    "Ga Ge As Se Br Kr Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce "
    "Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf Ta W Re Os Ir Pt Au Hg Tl Pb Bi Po At Rn "
    "Fr Ra Ac Th Pa U"
).split()


def parse_product(sf4: str | None) -> tuple[int, int, str] | None:
    """``'43-TC-99-M'`` -> (43, 99, 'M'); ``'41-NB-97'`` -> (41, 97, '')."""
    m = _PRODUCT.match((sf4 or "").strip().upper())
    if not m:
        return None
    z, a = int(m.group(1)), int(m.group(3))
    if a < 5:
        return None
    state = m.group(4) or ""
    if state == "M1":
        state = "M"
    return z, a, state


def classify(sf: dict) -> tuple[str | None, str]:
    """(kind, branch) or (None, reason-dropped)."""
    k = quantity_kind(sf.get("sf6"), sf.get("sf8"))
    if k != "sig":
        return None, f"kind={k}"
    b = (sf.get("sf5") or "").upper()
    if b in ("", "IND"):
        return "ind", ""
    if b in ("M+", "IND/M+"):
        return "ind", "M+"
    if b == "CUM":
        return "cum", ""
    return None, f"sf5={b}"


def build(targets: set[tuple[int, int, str]] | None = None,
          out: Path | None = None) -> pl.DataFrame:
    ex = pl.read_parquet(
        REPO / "staging/exfor_all.parquet",
        columns=["entry", "subentry", "target_z", "target_a", "projectile", "reaction", "sf",
                 "energy_ev", "energy_sigma_ev", "renormalized", "year", "first_author",
                 "monitor", "outdated", "renorm_factor"])
    # ``target_a == 0`` is EXFOR's natural element. Admitted only when *targets* names one,
    # so the default build is byte-for-byte what it was.
    nat_ok = bool(targets) and any(a == 0 for _, a, _ in targets)
    ex = ex.filter(pl.col("projectile").is_in(["p", "a"])
                   & (pl.col("target_a") >= 0 if nat_ok else pl.col("target_a") > 0))
    if targets is not None:
        keys = pl.DataFrame([{"target_z": z, "target_a": a, "projectile": p}
                             for z, a, p in targets],
                            schema={"target_z": pl.Int16, "target_a": pl.Int16,
                                    "projectile": pl.String})
        ex = ex.join(keys, on=["target_z", "target_a", "projectile"], how="inner")
    dropped: Counter = Counter()
    rows = []
    for r in ex.iter_rows(named=True):
        sf = r["sf"] or {}
        if r["outdated"]:
            dropped["outdated"] += 1
            continue
        prod = parse_product(sf.get("sf4"))
        if prod is None:
            dropped["product unparseable/light"] += 1
            continue
        kind, branch = classify(sf)
        if kind is None:
            dropped[branch] += 1
            continue
        ren = r["renormalized"] or {}
        unit = (ren.get("units") or "").strip().lower()
        if unit not in UNIT_TO_MB:
            dropped[f"units={unit or '(none)'}"] += 1
            continue
        es, vs = r["energy_ev"] or [], ren.get("values") or []
        stat = ren.get("stat_sigma") or [None] * len(vs)
        sysu = ren.get("sys_sigma") or [None] * len(vs)
        esig = r["energy_sigma_ev"] or [None] * len(es)
        state = prod[2] if branch != "M+" else ""
        n_ok = 0
        for i, (e, v) in enumerate(zip(es, vs, strict=False)):
            if e is None or v is None or not np.isfinite(v) or v <= 0 or e <= 0:
                continue
            du = [u for u in (stat[i] if i < len(stat) else None,
                              sysu[i] if i < len(sysu) else None) if u is not None]
            rows.append({
                "entry": r["entry"], "subentry": r["subentry"], "year": r["year"],
                "author": r["first_author"], "reaction": r["reaction"],
                "sf3": sf.get("sf3") or "", "monitor": r["monitor"] or "",
                "target_z": int(r["target_z"]), "target_a": int(r["target_a"]),
                "projectile": r["projectile"], "product_z": prod[0], "product_a": prod[1],
                "state": state, "branch": branch, "kind": kind,
                "e_mev": e * 1e-6,
                "de_mev": (esig[i] * 1e-6 if i < len(esig) and esig[i] is not None else None),
                "xs_mb": v * UNIT_TO_MB[unit],
                "dxs_mb": (float(np.sqrt(sum(u * u for u in du))) * UNIT_TO_MB[unit]
                           if du else None),
                "renorm_factor": r["renorm_factor"],
            })
            n_ok += 1
        if n_ok == 0:
            dropped["no usable points"] += 1
    df = pl.DataFrame(rows, infer_schema_length=None)
    dest = Path(out) if out else OUT
    dest.parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(dest)
    summary = {"points": len(df), "subentries": df["subentry"].n_unique(),
               "by_kind": dict(Counter(df["kind"].to_list())),
               "dropped_subentries": dict(dropped.most_common())}
    dest.with_suffix(".summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(f"[exfor_charged] {summary['points']} points, {summary['subentries']} subentries; "
          f"dropped {sum(dropped.values())}: {dict(dropped.most_common(8))}")
    return df


if __name__ == "__main__":
    import argparse

    from omegaconf import OmegaConf

    ap = argparse.ArgumentParser()
    ap.add_argument("--natural-config", default=None,
                    help="also ingest the natural targets this sweep config's `natural` names")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    cfg = OmegaConf.load(REPO / "configs" / "charged_medical_sweep.yaml")
    tg = {(int(z), int(a_), str(p)) for z, a_, p in cfg.targets}
    if a.natural_config:
        nat = OmegaConf.load(a.natural_config)
        sym = {s: i + 1 for i, s in enumerate(SYMBOLS)}
        for k in nat.natural:
            el, pr = k.rsplit("-", 1)
            tg.add((sym[el], 0, pr))
    build(tg, out=Path(a.out) if a.out else None)
