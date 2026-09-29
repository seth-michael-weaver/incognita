"""TALYS reference quantities as contract-shaped arrays, for acceptance tests and injection.

Contract §5 ("injection rule") and §6. Every component is tested against what TALYS computed
for the same case, and every consumer can be fed TALYS's own upstream values before the
upstream port exists. This module is the one place that knows how the dumps written by
`physics.hf.talys_reference` are laid out; tests and components call these getters instead of
reading parquet themselves.

    from physics.hf import reference as ref
    if not ref.available():
        pytest.skip("reference dumps not parsed")
    T = ref.transmission("Fe056", particle="n")              # e_mev (E,), tjl (E, L, 2)
    omp = ref.omp_parameters("Fe056", particle="n")           # DataFrame, 19 columns + E
    pop = ref.binary_population("Fe056", e_inc_mev=1.0)       # per ejectile block

Units are exactly TALYS's (mb, MeV, MeV^-1, MeV^-3); names carry the suffix (contract §4.1).
"""

from __future__ import annotations

import json
import os
from functools import cache
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DIR = ROOT / "features" / "hf_reference"

PARTICLE_FILE = {"n": "n", "p": "p", "d": "d", "t": "t", "h": "h", "a": "a"}
PARTICLE_NAME = {
    "n": "neutron",
    "p": "proton",
    "d": "deuteron",
    "t": "triton",
    "h": "helium-3",
    "a": "alpha",
}


def reference_dir() -> Path:
    return Path(os.environ.get("INCOGNITA_HF_REFERENCE", DEFAULT_DIR))


def available(family: str = "manifest") -> bool:
    return (reference_dir() / f"{family}.parquet").exists()


@cache
def _family(family: str):
    import pandas as pd

    p = reference_dir() / f"{family}.parquet"
    if not p.exists():
        raise FileNotFoundError(
            f"{p} missing: run `python -m physics.hf.talys_reference parse` first"
        )
    return pd.read_parquet(p)


def _select(family: str, target: str, variant: str, file: str | None = None):
    df = _family(family)
    m = (df["target"] == target) & (df["variant"] == variant)
    if file is not None:
        m &= df["file"] == file
    return df[m]


def manifest():
    return _family("manifest")


def _wide_blocks(df):
    """long -> {block: (meta dict, wide DataFrame indexed by row)}"""
    out = {}
    for b, g in df.groupby("block", observed=True):
        w = g.pivot_table(
            index="row", columns="column", values="value", observed=True, aggfunc="first"
        )
        # pivot sorts columns alphabetically ('rho(J)= 10.5' before 'rho(J)=  2.5'); restore
        # TALYS's column order, which melt preserved as order of first appearance
        order = [c for c in dict.fromkeys(g["column"].astype(str)) if c in w.columns]
        w.columns = w.columns.astype(str)
        out[int(b)] = (json.loads(g["meta"].iloc[0]), w[order].sort_index())
    return out


def transmission(target: str, particle: str = "n", variant: str = "default") -> dict:
    """Emission-grid transmission coefficients for `particle` on the residual it leaves.

    Returns ``{"e_mev": (E,), "tjl": (E, Lmax+1, nj), "t_l": (E, Lmax+1), "j_columns": [...],
    "open": (E,) bool}``. The last axis of ``tjl`` has one entry per total j for the particle's
    spin, in TALYS's column order: nj = 2 for n, p, t, h (``T(L-1/2,L)``, ``T(L+1/2,L)``),
    3 for d (``T(L-1,L)``, ``T(L,L)``, ``T(L+1,L)``), and for the spin-0 alpha the file has only
    ``T(L))``, so ``tjl`` is (E, L, 1) holding T(l). Energies whose block TALYS wrote empty
    (``entries: -1``, a closed channel) are included with all-zero T and ``open`` False.
    Source: ``transmission_<p>.out``.
    """
    import pandas as pd

    fname = f"transmission_{PARTICLE_FILE[particle]}.out"
    idx = pd.read_parquet(reference_dir() / "block_index.parquet")
    idx = idx[(idx.target == target) & (idx.variant == variant) & (idx.file == fname)]
    if idx.empty:
        raise KeyError(f"{fname} not in dumps for {target}/{variant}")
    filled = _wide_blocks(_select("transmission", target, variant, fname))
    cols = json.loads(idx.iloc[0]["columns"])
    jcols = [c for c in cols if c.startswith("T(") and c != "T(L))"] or ["T(L))"]
    energies, tables = [], []
    for _, r in idx.sort_values("block").iterrows():
        energies.append(float(json.loads(r["meta"])["energy [MeV]"]))
        tables.append(filled.get(int(r["block"]), (None, None))[1])
    lmax = max((int(w["L"].max()) for w in tables if w is not None), default=-1)
    tjl = np.zeros((len(tables), lmax + 1, len(jcols)))
    tl = np.zeros((len(tables), lmax + 1))
    for i, w in enumerate(tables):
        if w is None:
            continue
        L = w["L"].to_numpy().astype(int)
        for k, c in enumerate(jcols):
            tjl[i, L, k] = w[c].to_numpy()
        tl[i, L] = w["T(L))"].to_numpy()
    return {
        "e_mev": np.array(energies),
        "tjl": tjl,
        "t_l": tl,
        "j_columns": jcols,
        "open": np.array([w is not None for w in tables]),
    }


def table(family: str, target: str, file: str, variant: str = "default"):
    """A single-block YANDF table as a wide DataFrame (columns as TALYS names them) + meta."""
    blocks = _wide_blocks(_select(family, target, variant, file))
    if len(blocks) != 1:
        raise ValueError(f"{file}: {len(blocks)} blocks; use blocks()")
    meta, w = next(iter(blocks.values()))
    return meta, w


def blocks(family: str, target: str, file: str, variant: str = "default") -> dict:
    """All blocks of a file: {block index: (meta, wide DataFrame)}."""
    return _wide_blocks(_select(family, target, variant, file))


def omp_parameters(target: str, particle: str = "n", variant: str = "default"):
    """omppar_<p>.out: E [MeV] and the 19 OMP columns (V, rv, av, W, ..., rc)."""
    return table("omp_parameters", target, f"omppar_{PARTICLE_FILE[particle]}.out", variant)[1]


def inverse_xs(target: str, particle: str = "n", variant: str = "default"):
    """cross_<p>.tot: E [MeV], total/elastic/reaction/OMP reaction [mb] on the emission grid."""
    return table("inverse_xs", target, f"cross_{PARTICLE_FILE[particle]}.tot", variant)[1]


def cross_section(target: str, file: str, variant: str = "default"):
    """Any single-table cross-section file (ng.tot, xs000000.tot, nn.L01, total.tot, ...)."""
    for fam in ("xs_totals", "xs_channels", "xs_levels", "xs_continuum", "residual_production"):
        df = _select(fam, target, variant, file)
        if len(df):
            return table(fam, target, file, variant)
    raise KeyError(f"{file} not found for {target}/{variant}")


def level_density(target_residual_file: str, target: str, variant: str = "default") -> dict:
    """ld<ZZZ><AAA>.gs: header parameters (meta of block 0) and every table block."""
    return blocks("level_density", target, target_residual_file, variant)


def binary_population(target: str, e_inc_mev: float, variant: str = "default") -> dict:
    """binE<E>.out: {block: (meta, wide table)} with bin, Ex [MeV], population [mb], JP= columns.

    TALYS labels the first two unit fields wrongly (`bin` [mb], `Ex` []); population columns
    are mb and Ex is MeV (contract §4.1 traps).
    """
    name = "binE" + f"{e_inc_mev:08.3f}".replace(" ", "0") + ".out"
    return blocks("binary_population", target, name, variant)


def psf(target: str, file: str, variant: str = "default"):
    """psf<ZZZ><AAA>.<E1|M1|E2|M2>: photon strength function table [MeV^-3] + Γγ header."""
    return table("psf", target, file, variant)


def incident_scalars(target: str, variant: str = "default"):
    """Per incident energy, from talys.out: OMP sigma_tot/reac/el [mb], S0 and S1 (absolute,
    not units of 1e-4), R' [fm], and the normalisation block (reaction, sum over T(j,l),
    compound formation) [mb]. The incident channel's T_lj survive only for the last energy.
    """
    df = _family("incident_scalars")
    return df[(df["target"] == target) & (df["variant"] == variant)].sort_values("e_inc_mev")


def _float_meta(meta: dict) -> dict:
    out = {}
    for k, v in meta.items():
        try:
            out[k] = float(str(v).split()[0])
        except (ValueError, IndexError):
            out[k] = v
    return out


def _meta_or_none(meta: dict, key: str) -> float | None:
    v = meta.get(key)
    return None if v is None else float(str(v).split()[0])


def level_density_arrays(target: str, ld_file: str, variant: str = "default") -> dict:
    """ld<ZZZ><AAA>.gs as arrays (T6/T7/T9 injection).

    Returns ``{"parameters": {name: float|str} (a(Sn) [MeV^-1], temperature [MeV], E0 [MeV],
    matching energy [MeV], ...), "levels": DataFrame (E, Level, N_cumulative, Total_LD, ...),
    "u_mev": (U,), "rho_total_per_mev": (U, 2), "rho_jp_per_mev": (U, J, 2), "j": (J,)}``
    with the parity axis ordered (-1, +1) (contract §4.2). Only blocks for fission barrier 0.

    Columns are returned as TALYS prints them, and their definitions are NOT established here:
    for Zr-91 the sum over J of the ``rho(J)=`` columns in a parity block is 0.05-0.13 of that
    block's ``rho_total`` column, falling with energy. T6 must pin the definitions down in
    densityout.f90 (per-parity or both parities, levels or states, (2J+1) weighting) before
    comparing anything against them.
    """
    bl = level_density(ld_file, target, variant)
    params = _float_meta(bl[0][0])
    levels = bl[0][1]
    by_parity = {}
    for _, (m, w) in bl.items():
        if m.get("type") == "level density" and m.get("fission barrier", "0") in ("0", 0):
            by_parity.setdefault(int(m["Parity"]), w)
    if set(by_parity) != {-1, 1}:
        raise KeyError(f"{ld_file}: parities {sorted(by_parity)} in dumps")
    neg, pos = by_parity[-1], by_parity[1]
    jcols = [c for c in neg.columns if c.startswith("rho(J)=")]
    j = np.array([float(c.split("=")[1]) for c in jcols])
    return {
        "parameters": params,
        "levels": levels,
        "u_mev": neg["E"].to_numpy(),
        "rho_total_per_mev": np.stack([neg["rho_total"], pos["rho_total"]], axis=-1),
        "rho_jp_per_mev": np.stack([neg[jcols].to_numpy(), pos[jcols].to_numpy()], axis=-1),
        "j": j,
    }


def binary_population_arrays(target: str, e_inc_mev: float, variant: str = "default") -> dict:
    """binE<E>.out as arrays (A-cn1/A-cn2): {ejectile: {"bin": (B,), "ex_mev": (B,),
    "pop_mb": (B,), "pop_jp_mb": (B, J, 2), "j": (J,), "meta": {...}}} with parity (-1, +1).
    Discrete levels come first in the bin list (TALYS nex numbering), then continuum bins.
    ``exmax_mev`` is TALYS's Exmax for the residual; ``elimit`` (the top of the discrete-level
    region) is not printed in any dump file, so it is not offered here.
    In the incident particle's block, bin 0 is the target ground state: its population is the
    compound-elastic cross section and is NOT part of the block's ``post-binary population``
    (Fe-56 at 1 MeV, wfc_off: bin 0 = 1343.8 mb, post-binary population = 890.75 mb = bin 1).
    """
    out = {}
    for _, (m, w) in binary_population(target, e_inc_mev, variant).items():
        jp = [c for c in w.columns if c.startswith("JP=")]
        spins = sorted({float(c[3:-1]) for c in jp})
        arr = np.zeros((len(w), len(spins), 2))
        for c in jp:
            arr[:, spins.index(float(c[3:-1])), 0 if c.endswith("-") else 1] = w[c].to_numpy()
        out[m.get("ejectile", str(len(out)))] = {
            "bin": w["bin"].to_numpy().astype(int),
            "ex_mev": w["Ex"].to_numpy(),
            "pop_mb": w["population"].to_numpy(),
            "pop_jp_mb": arr,
            "j": np.array(spins),
            # TALYS's own grid facts for this residual, printed per block (T1 injects them
            # until T2 lands separation energies). Absent keys are None, never inherited:
            # blocks with no continuum print neither the level count nor the bin count.
            "exmax_mev": _meta_or_none(m, "maximum excitation energy [MeV]"),
            "n_discrete_levels": _meta_or_none(m, "number of discrete levels"),
            "n_continuum_bins": _meta_or_none(m, "number of continuum bins"),
            "bin_size_mev": _meta_or_none(m, "continuum bin size [MeV]"),
            "meta": _float_meta(m),
        }
    return out
