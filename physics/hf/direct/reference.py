"""Readers for the `directE*.out` dumps, which T0's loader leaves as raw text.

T0's parser keeps `direct` in `FAMILIES` (talys_reference.py:336) but the family has no
`direct.parquet`: its discrete block mixes numbers with two character columns -- `J/P` is
written as `f10.1, 1x, a1` (two whitespace-separated tokens for one column) and `def. type` is
a single letter (directout.f90:169) -- so every row fails the numeric split and the block lands
with `n_numeric_rows = 0`. The rows survive verbatim in `raw_rows.parquet` and the block headers
in `block_index.parquet`, so this module reads those two and types the columns itself.

A proposed loader patch is on `<lab-run>/requests.md` (T12 -> T0); nothing here depends on
it landing.

Two sources are supported:

* T0's published archives (`features/hf_reference/`), through the two parquets;
* T12's own `t12spec` / `t12racap` runs (`features/hf_direct_reference/`), read straight out of
  the tarballs, because those carry the `Giant resonance spectra` datablock (`outspectra y`)
  and `racap.tot`, which T0's runs do not.
"""

from __future__ import annotations

import tarfile
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import numpy as np

from physics.hf import reference as ref

ROOT = Path(__file__).resolve().parents[3]
T12_DIR = ROOT / "features" / "hf_direct_reference"

GR_LABELS = ("GMR", "GQR", "LEOR", "HEOR")


def t12_dir() -> Path:
    import os

    return Path(os.environ.get("INCOGNITA_HF_DIRECT_REFERENCE", T12_DIR))


def direct_file(e_inc_mev: float) -> str:
    """`directE0014.000.out` for 14.0 MeV (directout.f90:139-141)."""
    return f"directE{e_inc_mev:08.3f}.out"


@dataclass(frozen=True)
class DirectDump:
    """One `directE*.out`: the discrete rows, the giant-resonance block, and the two totals."""

    e_inc_mev: float
    level: np.ndarray  # (n,) int, TALYS level number
    e_mev: np.ndarray  # (n,) edis
    eout_mev: np.ndarray  # (n,) eoutdis
    spin: np.ndarray  # (n,)
    parity: np.ndarray  # (n,) +-1
    xs_mb: np.ndarray  # (n,) xsdirdisc
    deftype: str  # 'B' or 'D'
    defpar: np.ndarray  # (n,) deform
    xsdirdisctot_mb: float
    xscollconttot_mb: float
    # giant-resonance block, GMR/GQR/LEOR/HEOR order; absent below the pre-equilibrium onset
    has_giant: bool
    xsgrcoll_mb: np.ndarray  # (4,)
    egrcoll_mev: np.ndarray  # (4,)
    eoutgr_mev: np.ndarray  # (4,)
    ggrcoll_mev: np.ndarray  # (4,)
    betagr: np.ndarray  # (4,)
    xsgrtot_mb: float  # header "total GR cross section" = xsgrtot - xscollconttot
    # spectra block, only when the run had `outspectra y` (T12's t12spec variant)
    has_spectra: bool
    spec_eout_mev: np.ndarray
    spec_total_mb: np.ndarray
    spec_state_mb: np.ndarray  # (4, E)
    spec_collective_mb: np.ndarray


def _f(meta: dict, key: str, default: float = 0.0) -> float:
    v = meta.get(key, default)
    try:
        return float(str(v).split()[0])
    except (ValueError, IndexError):
        return float(default)


def parse_discrete_row(line: str) -> tuple:
    """(level, energy, E-out, spin, parity, cross section, def. type, def. par.) from one row.

    directout.f90:169 writes `(3x, i6, 6x, 2es15.6, f10.1, 1x, a1, 4x, es15.6, 6x, a1, 8x,
    es15.6)`. Every numeric field here is positive (a level is only written when `eoutdis > 0`),
    so the fields cannot abut and a whitespace split is exact; the fixed columns are used as the
    fallback if a run ever writes a negative one.
    """
    p = line.split()
    if len(p) == 8:
        return (
            int(p[0]),
            float(p[1]),
            float(p[2]),
            float(p[3]),
            1 if p[4] == "+" else -1,
            float(p[5]),
            p[6],
            float(p[7]),
        )
    return (
        int(line[3:9]),
        float(line[15:30]),
        float(line[30:45]),
        float(line[45:55]),
        1 if line[56:57] == "+" else -1,
        float(line[61:76]),
        line[82:83],
        float(line[91:106]),
    )


def parse_giant_row(line: str) -> tuple:
    """(label, xs, Egrcoll, eoutgr, Ggrcoll, betagr); `("     GMR       ", 5es15.6)`
    (directout.f90:212). `eoutgr` is negative below the resonance, so this one is read by
    column, not by split."""
    return (
        line[:15].strip(),
        float(line[15:30]),
        float(line[30:45]),
        float(line[45:60]),
        float(line[60:75]),
        float(line[75:90]),
    )


def _blank() -> dict:
    z4 = np.zeros(4)
    return dict(
        has_giant=False,
        xsgrcoll_mb=z4,
        egrcoll_mev=z4.copy(),
        eoutgr_mev=z4.copy(),
        ggrcoll_mev=z4.copy(),
        betagr=z4.copy(),
        xsgrtot_mb=0.0,
        has_spectra=False,
        spec_eout_mev=np.zeros(0),
        spec_total_mb=np.zeros(0),
        spec_state_mb=np.zeros((4, 0)),
        spec_collective_mb=np.zeros(0),
    )


def _from_text(e_inc_mev: float, text: str) -> DirectDump:
    """Parse a whole `directE*.out` file, header meta included."""
    rows: list[tuple] = []
    gr: list[tuple] = []
    spec: list[list[float]] = []
    meta: dict[str, str] = {}
    quantity = ""
    for raw in text.splitlines():
        if raw.startswith("#"):
            s = raw.lstrip("#").strip()
            if ":" in s:
                k, _, v = s.partition(":")
                meta[k.strip()] = v.strip()
                if k.strip() == "type":
                    quantity = v.strip()
            continue
        if not raw.strip():
            continue
        if quantity == "direct inelastic cross sections":
            rows.append(parse_discrete_row(raw))
        elif quantity == "giant resonance cross sections":
            gr.append(parse_giant_row(raw))
        elif quantity == "Giant resonance spectra":
            spec.append([float(raw[15 * k : 15 * (k + 1)]) for k in range(7)])
        # `average angular distributions` (flagddx) is not requested by any T12 run
    g = _blank()
    if gr:
        by = {r[0]: r for r in gr}
        g.update(
            has_giant=True,
            xsgrcoll_mb=np.array([by[k][1] for k in GR_LABELS]),
            egrcoll_mev=np.array([by[k][2] for k in GR_LABELS]),
            eoutgr_mev=np.array([by[k][3] for k in GR_LABELS]),
            ggrcoll_mev=np.array([by[k][4] for k in GR_LABELS]),
            betagr=np.array([by[k][5] for k in GR_LABELS]),
            xsgrtot_mb=_f(meta, "total GR cross section"),
        )
    if spec:
        a = np.array(spec)
        g.update(
            has_spectra=True,
            spec_eout_mev=a[:, 0],
            spec_total_mb=a[:, 1],
            spec_state_mb=a[:, 2:6].T.copy(),
            spec_collective_mb=a[:, 6],
        )
    cols = list(zip(*rows, strict=True)) if rows else [()] * 8
    return DirectDump(
        e_inc_mev=float(e_inc_mev),
        level=np.array(cols[0], np.int64),
        e_mev=np.array(cols[1], float),
        eout_mev=np.array(cols[2], float),
        spin=np.array(cols[3], float),
        parity=np.array(cols[4], np.int64),
        xs_mb=np.array(cols[5], float),
        deftype=(cols[6][0] if cols[6] else "B"),
        defpar=np.array(cols[7], float),
        xsdirdisctot_mb=_f(meta, "total discrete direct inelastic cross section [mb]"),
        xscollconttot_mb=_f(meta, "collective continuum inelastic cross section [mb]"),
        **g,
    )


# --- T0's published archives -----------------------------------------------------------------


@lru_cache(maxsize=8)
def _raw(target: str, variant: str):
    import pandas as pd

    df = pd.read_parquet(ref.reference_dir() / "raw_rows.parquet")
    df = df[
        (df["target"] == target) & (df["variant"] == variant) & df["file"].str.startswith("direct")
    ]
    return df


@lru_cache(maxsize=8)
def _meta(target: str, variant: str) -> dict:
    import json

    import pandas as pd

    idx = pd.read_parquet(ref.reference_dir() / "block_index.parquet")
    idx = idx[(idx.target == target) & (idx.variant == variant) & (idx.family == "direct")]
    return {(r["file"], int(r["block"])): json.loads(r["meta"]) for _, r in idx.iterrows()}


def energies_with_direct(target: str, variant: str = "default") -> list[float]:
    """Incident energies whose `directE*.out` this run wrote."""
    return sorted({float(f[7:-4]) for f, _b in _meta(target, variant)})


def dump(target: str, e_inc_mev: float, variant: str = "default") -> DirectDump:
    """One `directE*.out` from T0's archives, reassembled from `raw_rows` + `block_index`.

    The spectra block is never present here (T0's runs do not set `outspectra`); use
    :func:`t12_dump` for that.
    """
    name = direct_file(e_inc_mev)
    meta = _meta(target, variant)
    if (name, 0) not in meta:
        raise KeyError(f"{name} not in dumps for {target}/{variant}")
    df = _raw(target, variant)
    df = df[df["file"] == name]
    rows = [
        parse_discrete_row(r["line"])
        for _, r in df[df["block"].astype(int) == 0].sort_values("row").iterrows()
    ]
    gr = [
        parse_giant_row(r["line"])
        for _, r in df[df["block"].astype(int) == 1].sort_values("row").iterrows()
    ]
    g = _blank()
    if gr:
        by = {r[0]: r for r in gr}
        g.update(
            has_giant=True,
            xsgrcoll_mb=np.array([by[k][1] for k in GR_LABELS]),
            egrcoll_mev=np.array([by[k][2] for k in GR_LABELS]),
            eoutgr_mev=np.array([by[k][3] for k in GR_LABELS]),
            ggrcoll_mev=np.array([by[k][4] for k in GR_LABELS]),
            betagr=np.array([by[k][5] for k in GR_LABELS]),
            xsgrtot_mb=_f(meta[(name, 1)], "total GR cross section"),
        )
    cols = list(zip(*rows, strict=True)) if rows else [()] * 8
    return DirectDump(
        e_inc_mev=float(e_inc_mev),
        level=np.array(cols[0], np.int64),
        e_mev=np.array(cols[1], float),
        eout_mev=np.array(cols[2], float),
        spin=np.array(cols[3], float),
        parity=np.array(cols[4], np.int64),
        xs_mb=np.array(cols[5], float),
        deftype=(cols[6][0] if cols[6] else "B"),
        defpar=np.array(cols[7], float),
        xsdirdisctot_mb=_f(meta[(name, 0)], "total discrete direct inelastic cross section [mb]"),
        xscollconttot_mb=_f(meta[(name, 0)], "collective continuum inelastic cross section [mb]"),
        **g,
    )


# --- T12's own runs --------------------------------------------------------------------------


def t12_available(variant: str = "t12spec") -> list[str]:
    """Targets T12's own TALYS runs cover, for this variant."""
    d = t12_dir()
    if not d.is_dir():
        return []
    return sorted(p.name[len(variant) + 2 : -7] for p in d.glob(f"{variant}__*.tar.gz"))


@lru_cache(maxsize=16)
def _t12_files(target: str, variant: str) -> dict[str, str]:
    tar = t12_dir() / f"{variant}__{target}.tar.gz"
    if not tar.exists():
        raise KeyError(f"{tar} missing: run physics.hf.direct.reference_runs")
    out = {}
    with tarfile.open(tar) as tf:
        for m in tf.getmembers():
            if not m.isfile():
                continue
            f = tf.extractfile(m)
            if f is not None:
                out[Path(m.name).name] = f.read().decode("utf-8", "replace")
    return out


def t12_energies(target: str, variant: str = "t12spec") -> list[float]:
    return sorted(float(n[7:-4]) for n in _t12_files(target, variant) if n.startswith("directE"))


def t12_dump(target: str, e_inc_mev: float, variant: str = "t12spec") -> DirectDump:
    """One `directE*.out` from T12's own `outspectra y` run, spectra block included."""
    files = _t12_files(target, variant)
    name = direct_file(e_inc_mev)
    if name not in files:
        raise KeyError(f"{name} not in {variant}__{target}.tar.gz")
    return _from_text(e_inc_mev, files[name])


def t12_racap(target: str) -> np.ndarray:
    """`racap.tot`: (E-inc, xs, xs(E1), xs(E2), xs(M1), xs(tot)) per row, mb
    (racapout.f90:208)."""
    txt = _t12_files(target, "t12racap").get("racap.tot", "")
    rows = [
        [float(ln[15 * k : 15 * (k + 1)]) for k in range(6)]
        for ln in txt.splitlines()
        if ln.strip() and not ln.lstrip().startswith("#")
    ]
    return np.array(rows) if rows else np.zeros((0, 6))


@dataclass(frozen=True)
class RacapOut:
    """One `racap.out` (racapout.f90): the header block and one record per incident energy."""

    nlevexpracap: int
    spectfac: np.ndarray  # (n,) in the order racapout.f90:126 prints them
    spect_e_mev: np.ndarray
    spect_spin: np.ndarray
    spect_parity: np.ndarray
    energies_mev: np.ndarray
    xsracape_mb: np.ndarray
    xsracapedisc_mb: np.ndarray
    xsracapecont_mb: np.ndarray
    xspopnuc_mb: np.ndarray  # "Total radiative capture xs", i.e. xspopnuc(0,0) after racap
    xshfpreeq_mb: np.ndarray  # "HF+Preeq radiative capture xs" = xspopnuc(0,0) - xsracape
    popex_mb: list  # per energy, (nex,) xsracappopex
    level_sp: list  # per energy, (nex,) the spectfac column of the table


def _parse_racap_out(txt: str) -> RacapOut:
    """Parse the text of a `racap.out`.

    Column formats are racapout.f90:126 (spectroscopic factors), :145-149 (the per-energy
    summary) and :1225/:1226 (the per-level table, whose `Sp` column repeats `spectfac` and
    whose `J/p=tot` column is `xsracappopex`).
    """
    import re

    nexp = 0
    m = re.search(r"experimental levels:\s*(\d+)", txt)
    if m:
        nexp = int(m.group(1))
    sp_e, sp_j, sp_p, sp_f = [], [], [], []
    lines = txt.splitlines()
    i = 0
    while i < len(lines) and "Spectroscopic factors" not in lines[i]:
        i += 1
    i += 1
    while i < len(lines):
        p = lines[i].split()
        if len(p) == 4 and p[2] in ("+", "-"):
            sp_e.append(float(p[0]))
            sp_j.append(float(p[1]))
            sp_p.append(1 if p[2] == "+" else -1)
            sp_f.append(float(p[3]))
        elif sp_e:
            break
        i += 1
    es, tot, disc, cont, popex, lsp = [], [], [], [], [], []
    hf, tn = [], []
    cur: list[tuple[float, float]] = []
    for ln in lines:
        m = re.search(r"Direct capture at Elab=\s*(\S+)", ln)
        if m:
            if es:
                popex.append(np.array([c[1] for c in cur]))
                lsp.append(np.array([c[0] for c in cur]))
            cur = []
            es.append(float(m.group(1)))
            continue
        m = re.search(
            r"Direct\s+radiative capture xs =\s*(\S+)\s*mb\s*"
            r"\(Discrete=\s*(\S+)\s*-\s*Continuum=\s*(\S+)\)",
            ln,
        )
        if m:
            tot.append(float(m.group(1)))
            disc.append(float(m.group(2)))
            cont.append(float(m.group(3)))
            continue
        m = re.search(r"HF\+Preeq radiative capture xs =\s*(\S+)", ln)
        if m:
            hf.append(float(m.group(1)))
            continue
        m = re.search(r"Total\s+radiative capture xs =\s*(\S+)", ln)
        if m:
            tn.append(float(m.group(1)))
            continue
        p = ln.split()
        if es and len(p) >= 6 and re.fullmatch(r"\d+", p[0]) and "." in p[1]:
            try:
                cur.append((float(p[4]), float(p[5])))
            except ValueError:
                pass
    if es:
        popex.append(np.array([c[1] for c in cur]))
        lsp.append(np.array([c[0] for c in cur]))
    return RacapOut(
        nlevexpracap=nexp,
        spectfac=np.array(sp_f),
        spect_e_mev=np.array(sp_e),
        spect_spin=np.array(sp_j),
        spect_parity=np.array(sp_p),
        energies_mev=np.array(es),
        xsracape_mb=np.array(tot),
        xsracapedisc_mb=np.array(disc),
        xsracapecont_mb=np.array(cont),
        xspopnuc_mb=np.array(tn),
        xshfpreeq_mb=np.array(hf),
        popex_mb=popex,
        level_sp=lsp,
    )


def t12_racap_out(target: str) -> RacapOut:
    """`racap.out` from T12's own `t12racap` run."""
    return _parse_racap_out(_t12_files(target, "t12racap").get("racap.out", ""))


def sample_racap_out(name: str = "n-Y089-dircap") -> RacapOut:
    """`racap.out` from a TALYS sample shipped with the source (`samples/<name>/org/`).

    `n-Y089-dircap` is TALYS's own direct-capture example, so it is a reference that needs no
    run and moves only when the TALYS version does.
    """
    import os

    root = Path(os.environ.get("TALYS_DIR", Path.home() / "opt/talys-src"))
    p = root / "samples" / name / "org" / "racap.out"
    if not p.is_file():
        raise KeyError(f"{p} missing")
    return _parse_racap_out(p.read_text(errors="replace"))
