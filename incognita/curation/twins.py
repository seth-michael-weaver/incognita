"""R3: EXFOR twin datasets (one measurement compiled twice). The rule of scripts/twins.py, unchanged.

A candidate pair comes from a BIB cross-reference (STATUS SPSDD, or "renormalized / revised gold / new gold"
naming Subent X) or from the data alone (same nuclide/kind/state/branch, same cells, constant ratio). It is
confirmed by the numbers: factor in [0.8, 1.25], sd(log10 ratio) < 0.01 dex (x) or < 0.004 dex (d); a
single-cell data pair needs an exact copy AND the same entry or the same first author and year. The documented
renormalised copy is kept; otherwise the higher-trust copy, then the earlier accession.
"""
from __future__ import annotations

import re
from collections import defaultdict

import numpy as np
import polars as pl

from . import exfor_text, paths

BAND = (0.8, 1.25)
SD_X, SD_D = 0.01, 0.004
EXACT = 3e-5
RENORM_TXT = re.compile(r"renormali[sz]ed|revised gold|new gold", re.I)
SUBENT = re.compile(r"Subent(?:ry|ries)?\.?\s+(\d{5})[.\s]?(\d{3})", re.I)
SPSDD = re.compile(r"SPSDD\s*,\s*(\d{8})")


def _bib_refs(sub) -> tuple[list[str], list[str]]:
    sup, ren = [], []
    for kw, items in sub.bib.items():
        for it in items:
            code, text = it.code or "", it.text or ""
            for m in SPSDD.finditer(code + " " + text):
                sup.append(m.group(1))
            if kw in ("STATUS", "ANALYSIS", "COMMENT", "CORRECTION", "ADD-RES") and RENORM_TXT.search(text):
                for m in SUBENT.finditer(text):
                    ren.append(m.group(1) + m.group(2))
    return sup, ren


def _ratio(A: dict, B: dict):
    com = [e for e in A if e in B and A[e] > 0 and B[e] > 0]
    if not com:
        return None
    lr = np.array([np.log10(A[e] / B[e]) for e in com])
    return len(com), float(lr.mean()), float(lr.std())


def find_twins() -> pl.DataFrame:
    """One row per superseded dataset: superseded, kept, how, ref, n_common, factor (kept/superseded), sd_dex."""
    from data.ingest.exfor import parse_entry  # the repository's EXFOR parser

    c = pl.read_parquet(paths.CELLS).filter(pl.col("mt") == 102)
    tr = pl.read_parquet(paths.TRUST, columns=["dataset_key", "first_author", "year", "trust"])
    who = {r["dataset_key"]: ((r["first_author"] or "").strip().upper(), r["year"]) for r in tr.iter_rows(named=True)}
    trust = dict(zip(tr["dataset_key"], tr["trust"]))
    ds, meta = defaultdict(dict), {}
    for r in c.select("dataset_key", "e_lo_ev", "e_hi_ev", "mean_b", "nuclide", "kind", "state", "branch",
                      "usable").iter_rows(named=True):
        ds[r["dataset_key"]][(round(r["e_lo_ev"], 3), round(r["e_hi_ev"], 3))] = r["mean_b"]
        meta[r["dataset_key"]] = (r["nuclide"], r["kind"], r["state"], r["branch"])
    z, names = exfor_text._zip()
    by_sub = defaultdict(list)
    for k in ds:
        by_sub[k.split("/")[1]].append(k)
    pairs: dict[frozenset, dict] = {}

    def add(orig, kept, how, ref, n, mlr, sd):
        key = frozenset((orig, kept))
        if key in pairs and pairs[key]["how"].startswith("x"):
            return
        pairs[key] = dict(superseded=orig, kept=kept, how=how, ref=ref, n_common=n,
                          factor=round(10 ** -mlr, 5), sd_dex=round(sd, 5))

    for e in sorted({k.split("/")[0] for k in ds}):
        if e not in names:
            continue
        E = parse_entry(z.read(names[e]).decode("latin-1"))
        for sub in E.subentries:
            mine = by_sub.get(sub.accession, [])
            if not mine:
                continue
            sup, ren = _bib_refs(sub)
            for role, refs in (("SPSDD", sup), ("renorm", ren)):
                for x in refs:
                    if x == sub.accession:
                        continue
                    for a in mine:
                        best = None
                        for b in by_sub.get(x, []):
                            if meta[a] != meta[b]:
                                continue
                            st = _ratio(ds[a], ds[b])
                            if st is None:
                                continue
                            n, mlr, sd = st
                            if not BAND[0] <= 10 ** abs(mlr) <= BAND[1] or (n >= 2 and sd >= SD_X):
                                continue
                            if best is None or (sd, abs(mlr)) < best[0]:
                                best = ((sd, abs(mlr)), b, n, mlr, sd)
                        if best:
                            _, b, n, mlr, sd = best
                            if role == "SPSDD":
                                add(a, b, "x:SPSDD", x, n, mlr, sd)
                            else:
                                add(b, a, "x:renorm", x, n, -mlr, sd)
    grp = defaultdict(list)
    for k, m in meta.items():
        grp[m].append(k)
    for ks in grp.values():
        for i, a in enumerate(ks):
            for b in ks[i + 1:]:
                if frozenset((a, b)) in pairs:
                    continue
                A, B = ds[a], ds[b]
                if len(set(A) & set(B)) < 0.99 * max(len(A), len(B)):
                    continue
                st = _ratio(A, B)
                if st is None:
                    continue
                n, mlr, sd = st
                wa, wb = who.get(a, ("", None)), who.get(b, ("", None))
                same_src = a.split("/")[0] == b.split("/")[0] or (wa[0] and wa == wb)
                ok = (n >= 2 and sd < SD_D and BAND[0] <= 10 ** abs(mlr) <= BAND[1]) or (
                    n == 1 and abs(mlr) < EXACT and same_src)
                if not ok:
                    continue
                ta, tb = trust.get(a) or 0, trust.get(b) or 0
                keep, orig = (a, b) if (ta > tb or (ta == tb and a < b)) else (b, a)
                add(orig, keep, "d:exact" if abs(mlr) < 1e-4 else "d:ratio", "", n, mlr if orig == a else -mlr, sd)
    T = pl.DataFrame(list(pairs.values())).sort("superseded")
    T = T.unique(subset=["superseded"], keep="first", maintain_order=True)
    return T.filter(~pl.col("superseded").is_in(T["kept"].to_list()))


def series_ids(twin_pairs: list[tuple[str, str]]) -> dict[str, int]:
    """FLOOR's series (same entry, or same first author + facility + detector) plus twin edges (union-find)."""
    t = pl.read_parquet(paths.TRUST, columns=["dataset_key", "entry", "first_author", "facility", "detector"])
    keys = t["dataset_key"].to_list()
    parent = {k: k for k in keys}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(g):
        r0 = find(g[0])
        for k in g[1:]:
            r = find(k)
            if r != r0:
                parent[r] = r0

    by = defaultdict(list)
    for r in t.iter_rows(named=True):
        by[("e", r["entry"] or r["dataset_key"].split("/")[0])].append(r["dataset_key"])
        au, fa, de = r["first_author"], r["facility"], r["detector"]
        if au and fa and de:
            by[("a", au.strip().upper(), fa, de)].append(r["dataset_key"])
    for g in by.values():
        union(g)
    known = set(keys)
    for a, b in twin_pairs:
        if a in known and b in known:
            union([a, b])
    roots: dict[str, int] = {}
    return {k: roots.setdefault(find(k), len(roots)) for k in keys}
