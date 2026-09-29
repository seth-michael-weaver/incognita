#!/usr/bin/env python3
"""WP-11: evaluated libraries (ENDF-6) → ``EvaluatedXS`` on the common grid.

Tool path (see ``docs/evaluated-ingest.md`` for the full story):

* **NJOY2016 RECONR** (``$INCOGNITA_NJOY``, default ``~/micromamba/envs/incognita-phys/bin/njoy``)
  reconstructs the resonance region at 0 K and linearises every MF3 section to
  a relative tolerance ``error`` (default 0.1 %). It is the only tool on this
  box that handles every formalism present in the libraries (MLBW, Reich-Moore,
  R-matrix-limited) *and* computes the unresolved-region average cross sections
  for the 258 materials with ``LSSF=0`` (openmc's Python reconstruction is not
  built in the conda package and ignores LSSF=0 anyway). Optional BROADR
  temperatures give Doppler-broadened companions of the same records.
* **endf-parserpy** (IAEA, C++ parser) reads MF1/MF2/MF33 of the *original*
  evaluation for the resonance-region bounds, the resolved/unresolved
  parameter ladders and the MF33 relative covariance blocks.
* A small stdlib/numpy TAB1 reader (:func:`read_pendf_mf3`) pulls the requested
  MTs out of the PENDF so a 100 MB actinide PENDF does not become a
  dict-of-dicts in memory.

Grid mapping: the PENDF is lin-lin and dense to ``error`` everywhere (RECONR
linearises smooth MF3 sections as well as the reconstructed resonances), so the
value at each common-grid energy is obtained by lin-lin interpolation of the
PENDF, which reproduces the reconstructed 0 K cross section *at that energy*
to within ``error``. In the resonance region this is point sampling — no
averaging over the resonance structure between grid points — which is what
blueprint §4.2 asks for (Doppler/self-shielded group averages are a later
transport concern). No log-log interpolation of the coarse MF3 grid is needed
because RECONR has already densified it.

Memory: one material at a time per worker; PENDF parsing is streamed line by
line and only the requested MTs are kept. Peak RSS per worker is ~250 MB for
U-238 (96 MB PENDF); NJOY itself uses < 50 MB.

Usage (see ``data/ingest/build_evaluated.py`` for the CLI)::

    uv run python -m data.ingest.build_evaluated --library endfb81 --subset capture --workers 3
"""

from __future__ import annotations

import glob
import io
import json
import math
import os
import re
import shutil
import subprocess
import tarfile
import time
import zipfile
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parents[2]
RAW = REPO / "raw" / "endf"
TENDL_ARCHIVE = REPO / "raw" / "tendl_archive"
TENDL_ARCHIVE_YEARS: tuple[int, ...] = (2015, 2017, 2019, 2021, 2023)
STAGING = REPO / "staging" / "evaluated"
EXTRACT = REPO / "staging" / "_extract"
NJOY_EXE = Path(os.environ.get("INCOGNITA_NJOY", os.environ.get(
    "INCOGNITA_NJOY", os.path.expanduser("~/micromamba/envs/incognita-phys/bin/njoy"))))
NJOY_TIMEOUT_S = 1800

# MTs (blueprint §2.2 Tier 3 / plan step 1). "capture" is priority (a) of WP-11.
CAPTURE_MTS: tuple[int, ...] = (1, 2, 102, 4, 16, 103, 107, 18)
ALL_MTS: tuple[int, ...] = (
    1, 2, 3, 4, 5, 11, 16, 17, 18, 22, 24, 28, 32, 33, 37, 41, 42, 44, 45,
    51, 52, 53, 54, 55, 91, 102, 103, 104, 105, 106, 107, 111, 112, 115, 116, 117,
    649, 699, 749, 799, 849,
)  # fmt: skip
# MTs whose MF33 self-covariance block is assembled and stored (capture first).
COV_MTS: tuple[int, ...] = (102, 18, 1, 2, 16, 103, 107)
CAPTURE_Z_RANGE: tuple[int, int] = (26, 92)

__all__ = [
    "ALL_MTS",
    "CAPTURE_MTS",
    "COV_MTS",
    "LIBRARIES",
    "LibrarySpec",
    "MaterialResult",
    "MaterialSource",
    "MaterialTask",
    "assemble_mf33",
    "endf_floats",
    "ladder_stats",
    "list_materials",
    "parse_mf2",
    "process_material",
    "read_header",
    "read_pendf_mf3",
    "run_njoy",
    "stage_material",
    "threshold_from_pointwise",
    "to_grid",
]


# --------------------------------------------------------------------------- #
# Library registry
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class LibrarySpec:
    key: str  # short key used in file names: endfb81, jeff33, ...
    name: str  # EvaluatedXS.library
    archive: Path
    kind: str  # "tar" | "zip-per-material" | "zip-concatenated" | "tar-unknown"
    member_pattern: str | None = None  # regex on archive member names (tar kinds)
    version_note: str = ""
    # Where a "tar" library is unpacked, when it must not go under staging/_extract
    # (the archived TENDL releases are unpacked beside their tarballs in raw/).
    extract_override: Path | None = None
    # Keep only MTs that the evaluation itself gives in MF3. RECONR writes summed redundant
    # sections (MT1, MT4, MT103, ...) from whatever partials exist; for a dosimetry library that
    # carries a handful of channels those sums are not the physical total, so they are dropped.
    mf3_original_only: bool = False

    @property
    def extract_dir(self) -> Path:
        return self.extract_override or (EXTRACT / self.key)


LIBRARIES: dict[str, LibrarySpec] = {
    "endfb81": LibrarySpec(
        "endfb81", "ENDF/B-VIII.1", RAW / "endfb81" / "ENDF-B-VIII.1.tar.gz", "tar",
        r"(^|/)n-\d{3}_[A-Za-z]+_\d{3}(m\d)?\.endf$",
        "ENDF/B-VIII.1 release tarball (neutrons sublibrary)",
    ),
    "jeff33": LibrarySpec(
        "jeff33", "JEFF-3.3", RAW / "jeff33" / "JEFF33-n.tgz", "tar",
        r"(^|/)\d+-[A-Za-z]+-\d+[gmn]\.jeff33$", "JEFF-3.3 neutron sublibrary (JEFF33-n.tgz)",
    ),
    "jendl5": LibrarySpec(
        "jendl5", "JENDL-5", RAW / "jendl5" / "jendl5-n.tar.gz", "tar",
        r"(?i)(^|/)[^/]*\.(dat|endf|jendl5|txt)$", "JENDL-5 neutron sublibrary",
    ),
    "tendl2025": LibrarySpec(
        "tendl2025", "TENDL-2025", RAW / "tendl2025" / "n", "zip-per-material", None,
        "TENDL-2025 IAEA mirror, one zip per nuclide (E4-util retrieval)",
    ),
    "endfb71": LibrarySpec(
        "endfb71", "ENDF/B-VII.1", RAW / "endfb71" / "n", "zip-per-material", None,
        "ENDF/B-VII.1 (December 2011) from the IAEA-NDS mirror: the information-fair "
        "comparator for a model with a 2012 training cutoff",
    ),
    # Two more libraries old enough to be honest against a 2012 cutoff. Ensembling priors has
    # beaten choosing one three times over; these are not independent of each other (all fit
    # the same pre-2012 measurements) but they carry different evaluators' judgement, and that
    # is the part an average removes.
    "jendl40": LibrarySpec(
        "jendl40", "JENDL-4.0", RAW / "jendl40" / "n", "zip-per-material", None,
        "JENDL-4.0 (2010) from the IAEA-NDS mirror, one zip per nuclide",
    ),
    "endfb70": LibrarySpec(
        "endfb70", "ENDF/B-VII.0", RAW / "endfb70" / "n", "zip-per-material", None,
        "ENDF/B-VII.0 (2006) from the IAEA-NDS mirror, one zip per nuclide",
    ),
    "cendl32": LibrarySpec(
        "cendl32", "CENDL-3.2", RAW / "cendl32" / "cendl-3-2_n.sublib.zip", "zip-concatenated",
        None, "CENDL-3.2 neutron sublibrary, single concatenated tape",
    ),
    # --- Archived TENDL releases (RETRO, the retrodiction exam) --------------------------- #
    # A TENDL release of year Y has not seen a measurement published after Y, so TENDL-Y is as
    # blind as a model trained with year_cutoff = Y on those cells. One tarball per release
    # (tendl.imperial.ac.uk), flat, one ENDF-6 file per material: n-<Sym><A>[m].tendl. They are
    # unpacked beside the tarballs (raw/tendl_archive/<year>/), never into the 2025 raw tree.
    **{
        f"tendl{_y}": LibrarySpec(
            f"tendl{_y}", f"TENDL-{_y}", TENDL_ARCHIVE / f"TENDL-n-{_y}.tgz", "tar",
            # 2017-2023 name their files n-<Sym><A>[m].tendl; TENDL-2015 puts the projectile
            # last, <Sym><A>[m]-n.tendl, under <Sym>/<A>/lib/endf/ instead of <Sym><A>/lib/endf/
            r"(^|/)(n-[A-Za-z]{1,2}\d{1,3}[mn]?|[A-Za-z]{1,2}\d{1,3}[mn]?-n)\.tendl$",
            f"TENDL-{_y} neutron sublibrary (archived release tarball), RETRO exam arm",
            TENDL_ARCHIVE / str(_y),
        )
        for _y in TENDL_ARCHIVE_YEARS
    },
    # More evaluated libraries to score next to JENDL-5 / TENDL-2025 / ENDF/B-VIII.1, all from
    # the IAEA-NDS per-material mirror (data/ingest/download.py: jeff40_n ... irdff2_n).
    "jeff40": LibrarySpec(
        "jeff40", "JEFF-4.0", RAW / "jeff40" / "n", "zip-per-material", None,
        "JEFF-4.0 (OECD/NEA, June 2025) neutron sublibrary, IAEA-NDS mirror",
    ),
    "fendl32": LibrarySpec(
        "fendl32", "FENDL-3.2", RAW / "fendl32" / "n", "zip-per-material", None,
        "FENDL-3.2c (IAEA, current fix release of FENDL-3.2) neutron sublibrary, IAEA-NDS mirror",
    ),
    "brond31": LibrarySpec(
        "brond31", "BROND-3.1", RAW / "brond31" / "n", "zip-per-material", None,
        "BROND-3.1 (IPPE, 2016) neutron sublibrary, IAEA-NDS mirror",
    ),
    "irdff2": LibrarySpec(
        "irdff2", "IRDFF-II", RAW / "irdff2" / "n", "zip-per-material", None,
        "IRDFF-II dosimetry library, IAEA-NDS mirror: MF3 dosimetry channels only; MF10 "
        "isomer-production sections and elemental (A=0) materials are not staged",
        mf3_original_only=True,
    ),
}  # fmt: skip


@dataclass(frozen=True)
class MaterialSource:
    """Where one material's ENDF-6 text lives: a plain file, or a member of a zip."""

    library: str
    name: str  # stable per-material id used for resume/skip logs
    path: Path
    zip_member: str | None = None

    def read_text(self) -> str:
        if self.zip_member is None:
            data = self.path.read_bytes()
        else:
            with zipfile.ZipFile(self.path) as zf:
                data = zf.read(self.zip_member)
        return data.decode("latin-1").replace("\r\n", "\n").replace("\r", "\n")

    def iter_lines(self) -> Iterator[bytes]:
        """Stream the material line by line (LF-terminated, CR stripped) without loading it."""
        if self.zip_member is None:
            with open(self.path, "rb") as fh:
                for line in fh:
                    yield line.rstrip(b"\r\n") + b"\n"
        else:
            with zipfile.ZipFile(self.path) as zf, zf.open(self.zip_member) as fh:
                for line in fh:
                    yield line.rstrip(b"\r\n") + b"\n"

    def head_text(self, n_lines: int = 12) -> str:
        out = []
        for i, line in enumerate(self.iter_lines()):
            out.append(line.decode("latin-1"))
            if i + 1 >= n_lines:
                break
        return "".join(out)


# --------------------------------------------------------------------------- #
# ENDF-6 text helpers
# --------------------------------------------------------------------------- #
_FLOAT_FIX = re.compile(rb"(\d)([+-])")
_FLOAT_FIX_S = re.compile(r"(\d)([+-])")


def endf_float(s: str) -> float:
    # Some IPPE-made files (IRDFF-II Mn-55/Tm-169, BROND-3.1 O-18/P-31) write "2.50550+ 4":
    # a blank inside the exponent, which Fortran reads as-is. No field has a legitimate blank.
    s = s.replace(" ", "")
    if not s:
        return 0.0
    try:
        return float(s)
    except ValueError:
        return float(_FLOAT_FIX_S.sub(r"\1e\2", s))


def endf_floats(lines: Iterable[bytes], nvalues: int | None = None) -> np.ndarray:
    """All 11-column fields of the given 66-char data lines as float64.

    Fields are sliced by column (a negative number fills all 11 columns, so a
    whitespace split would merge it with its neighbour). ``nvalues`` truncates
    the trailing padding of the last line.
    """
    fields = []
    for ln in lines:
        ln = ln[:66].ljust(66)
        fields.extend(ln[i : i + 11] for i in range(0, 66, 11))
    if nvalues is not None:
        fields = fields[:nvalues]
    fields = [f.replace(b" ", b"") for f in fields]  # "2.50550+ 4" (see endf_float)
    txt = _FLOAT_FIX.sub(rb"\1e\2", b" ".join(f if f else b"0" for f in fields))
    return np.array(txt.split(), dtype=np.float64)


def _int(s: str) -> int:
    s = s.strip()
    return int(s) if s else 0


@dataclass
class Header:
    mat: int
    za: float
    awr: float
    lrp: int
    nlib: int
    nmod: int
    lis: int
    liso: int
    nfor: int
    lrel: int
    nsub: int
    nver: int
    tpid: str
    text: str  # first descriptive line of MF1/MT451

    @property
    def Z(self) -> int:
        return int(self.za) // 1000

    @property
    def A(self) -> int:
        return int(self.za) % 1000

    @property
    def N(self) -> int:
        return self.A - self.Z


def read_header(text: str) -> Header:
    """MF1/MT451 HEAD + the next three CONT records, straight from the first lines."""
    lines = text.split("\n", 8)
    if len(lines) < 5:
        raise ValueError("file too short to be an ENDF-6 material")
    # Locate the first line with MF=1 MT=451 (the TPID line comes first).
    idx = next((i for i, ln in enumerate(lines[:4]) if ln[70:75] == " 1451"), None)
    if idx is None:
        raise ValueError("no MF1/MT451 record in the first lines")
    tpid = lines[0][:66].strip() if idx > 0 else ""
    l1, l2, l3, l5 = lines[idx], lines[idx + 1], lines[idx + 2], lines[idx + 4]
    return Header(
        mat=_int(l1[66:70]),
        za=endf_float(l1[0:11]),
        awr=endf_float(l1[11:22]),
        lrp=_int(l1[22:33]),
        nlib=_int(l1[44:55]),
        nmod=_int(l1[55:66]),
        lis=_int(l2[22:33]),
        liso=_int(l2[33:44]),
        nfor=_int(l2[55:66]),
        lrel=_int(l3[22:33]),
        nsub=_int(l3[44:55]),
        nver=_int(l3[55:66]),
        tpid=tpid,
        text=l5[:66].strip(),
    )


# --------------------------------------------------------------------------- #
# Material discovery / extraction
# --------------------------------------------------------------------------- #
def _extract_tar(spec: LibrarySpec) -> list[Path]:
    out = spec.extract_dir
    pat = re.compile(spec.member_pattern or r".*")
    marker = out / ".extracted"

    def _listing() -> list[Path]:
        # rglob, not iterdir: this function also lists trees unpacked outside the pipeline, and
        # the TENDL 2015/2017 tarballs nest their materials (neutron_file/<Sym>/<Sym><A>/lib/endf/).
        return sorted(p for p in out.rglob("*") if p.is_file() and pat.search(p.name))

    if marker.exists():
        return _listing()
    out.mkdir(parents=True, exist_ok=True)
    with tarfile.open(spec.archive, "r:*") as tf:
        for m in tf:
            if not m.isfile() or not pat.search(m.name):
                continue
            src = tf.extractfile(m)
            if src is None:
                continue
            with open(out / Path(m.name).name, "wb") as dst:
                shutil.copyfileobj(src, dst)
    marker.write_text(time.strftime("%Y-%m-%dT%H:%M:%S"))
    return _listing()


def _split_concatenated(spec: LibrarySpec) -> list[Path]:
    """Split a single multi-material tape into one file per MAT (TPID + material + MEND/TEND)."""
    out = spec.extract_dir / "mats"
    marker = out / ".split"
    if marker.exists():
        return sorted(out.glob("*.endf"))
    out.mkdir(parents=True, exist_ok=True)
    mend = f"{'':66}   0 0  0    0\n".encode()
    tend = f"{'':66}  -1 0  0    0\n".encode()
    with zipfile.ZipFile(spec.archive) as zf:
        members = [n for n in zf.namelist() if not n.endswith("/")]
        if len(members) != 1:
            raise ValueError(f"{spec.key}: expected one tape in the zip, got {members}")
        # Stream the tape (CENDL-3.2 is ~390 MB of text): never hold it in memory.
        with zf.open(members[0]) as fh:
            tpid = next(fh).rstrip(b"\r\n") + b"\n"
            dst = None
            cur_mat: int | None = None
            for raw in fh:
                ln = raw.rstrip(b"\r\n")
                if len(ln) < 70:
                    continue
                mat = _int(ln[66:70].decode("latin-1"))
                if mat <= 0:  # MEND / TEND: close the current material
                    if dst is not None:
                        dst.write(mend + tend)
                        dst.close()
                        dst = None
                    cur_mat = None
                    continue
                if dst is None:
                    cur_mat = mat
                    dst = open(out / f"mat{cur_mat:04d}.endf", "wb")
                    dst.write(tpid)
                dst.write(ln + b"\n")
            if dst is not None:
                dst.write(mend + tend)
                dst.close()
    marker.write_text(time.strftime("%Y-%m-%dT%H:%M:%S"))
    return sorted(out.glob("*.endf"))


def list_materials(library: str) -> list[MaterialSource]:
    """Every material of a library as a :class:`MaterialSource` (extracting if needed)."""
    spec = LIBRARIES[library]
    if not spec.archive.exists():
        raise FileNotFoundError(f"{library}: {spec.archive} is not on disk")
    if spec.kind == "tar":
        return [MaterialSource(library, p.name, p) for p in _extract_tar(spec)]
    if spec.kind == "zip-concatenated":
        return [MaterialSource(library, p.name, p) for p in _split_concatenated(spec)]
    if spec.kind == "zip-per-material":
        out = []
        for zp in sorted(glob.glob(str(spec.archive / "*.zip"))):
            zp = Path(zp)
            with zipfile.ZipFile(zp) as zf:
                members = [n for n in zf.namelist() if not n.endswith("/")]
            if members:
                out.append(MaterialSource(library, zp.stem, zp, members[0]))
        return out
    raise ValueError(f"unknown archive kind {spec.kind!r}")


# --------------------------------------------------------------------------- #
# NJOY
# --------------------------------------------------------------------------- #
def njoy_deck(mat: int, error: float, temperatures: Iterable[float]) -> str:
    """RECONR (0 K → tape21) then one BROADR per temperature (tape22, tape23, ...)."""
    lines = ["reconr", "20 21", "'pendf'/", f"{mat} 0/", f"{error:g}/", "0/"]
    for i, t in enumerate(temperatures):
        lines += ["broadr", f"20 21 {22 + i}", f"{mat} 1 0 0 0/", f"{error:g}/", f"{t:g}/", "0/"]
    lines.append("stop")
    return "\n".join(lines) + "\n"


def run_njoy(
    endf_path: Path, mat: int, workdir: Path, *, error: float = 1e-3,
    temperatures: Iterable[float] = (), timeout: int = NJOY_TIMEOUT_S,
) -> dict[float, Path]:  # fmt: skip
    """Run NJOY in ``workdir``; returns {temperature_K: pendf_path} (0.0 → RECONR output)."""
    workdir.mkdir(parents=True, exist_ok=True)
    tape20 = workdir / "tape20"
    if tape20.resolve() != endf_path.resolve():
        shutil.copyfile(endf_path, tape20)
    temps = list(temperatures)
    deck = njoy_deck(mat, error, temps)
    (workdir / "input").write_text(deck)
    with open(workdir / "njoy.out", "w") as out:
        proc = subprocess.run(
            [str(NJOY_EXE)], input=deck, cwd=workdir, stdout=out, stderr=subprocess.STDOUT,
            text=True, timeout=timeout,
        )
    tapes = {0.0: workdir / "tape21"}
    for i, t in enumerate(temps):
        tapes[float(t)] = workdir / f"tape{22 + i}"
    missing = [str(p) for p in tapes.values() if not p.exists() or p.stat().st_size < 1000]
    if proc.returncode != 0 or missing:
        tail = (workdir / "njoy.out").read_text(errors="replace")[-1500:]
        raise RuntimeError(f"njoy rc={proc.returncode} missing={missing}\n{tail}")
    return tapes


# --------------------------------------------------------------------------- #
# PENDF MF3 reader
# --------------------------------------------------------------------------- #
@dataclass
class PointwiseXS:
    mt: int
    energy_ev: np.ndarray
    xs_b: np.ndarray
    qm: float
    qi: float
    lr: int
    interpolation: tuple[int, ...]


def _parse_mf3_section(lines: list[bytes], mt: int) -> PointwiseXS:
    head = lines[1]  # TAB1 header: QM QI 0 LR NR NP
    qm = endf_float(head[0:11].decode())
    qi = endf_float(head[11:22].decode())
    lr = _int(head[33:44].decode())
    nr = _int(head[44:55].decode())
    np_ = _int(head[55:66].decode())
    n_int_lines = math.ceil(nr / 3)
    ints = endf_floats(lines[2 : 2 + n_int_lines], 2 * nr).astype(np.int64)
    interp = tuple(int(v) for v in ints[1::2])
    n_data_lines = math.ceil(np_ / 3)
    data = endf_floats(lines[2 + n_int_lines : 2 + n_int_lines + n_data_lines], 2 * np_)
    return PointwiseXS(mt, data[0::2], data[1::2], qm, qi, lr, interp)


def read_pendf_mf3(path: Path, mts: Iterable[int] | None = None) -> dict[int, PointwiseXS]:
    """Stream a PENDF (or ENDF) tape and return the MF3 sections for ``mts`` (all if None)."""
    want = None if mts is None else set(int(m) for m in mts)
    out: dict[int, PointwiseXS] = {}
    buf: list[bytes] = []
    cur_mt: int | None = None
    with open(path, "rb") as fh:
        for line in fh:
            if line[70:72] != b" 3":
                if cur_mt is not None:
                    out[cur_mt] = _parse_mf3_section(buf, cur_mt)
                    buf, cur_mt = [], None
                continue
            mt = _int(line[72:75].decode())
            if mt == 0:  # SEND
                if cur_mt is not None:
                    out[cur_mt] = _parse_mf3_section(buf, cur_mt)
                buf, cur_mt = [], None
                continue
            if want is not None and mt not in want:
                continue
            if cur_mt != mt:
                if cur_mt is not None:
                    out[cur_mt] = _parse_mf3_section(buf, cur_mt)
                buf, cur_mt = [], mt
            buf.append(line)
    if cur_mt is not None and buf:
        out[cur_mt] = _parse_mf3_section(buf, cur_mt)
    return out


# --------------------------------------------------------------------------- #
# Grid mapping and thresholds
# --------------------------------------------------------------------------- #
def to_grid(energy_ev: np.ndarray, xs_b: np.ndarray, grid: np.ndarray | None = None) -> np.ndarray:
    """Lin-lin sample of a linearised (PENDF) cross section at the common-grid energies.

    Outside the tabulated range the value is 0 (correct for thresholds and for
    evaluations that stop below 20 MeV). Non-negative by construction.
    """
    from physics.grid import ENERGY_GRID_EV

    g = ENERGY_GRID_EV if grid is None else grid
    x = np.asarray(energy_ev, dtype=np.float64)
    y = np.asarray(xs_b, dtype=np.float64)
    if x.size == 0:
        return np.zeros_like(g)
    out = np.interp(g, x, y, left=0.0, right=0.0)
    # A grid point sitting exactly at the tabulated lower/upper end is inside the range.
    return np.clip(out, 0.0, None)


def threshold_from_pointwise(
    energy_ev: np.ndarray, xs_b: np.ndarray, qi: float, awr: float
) -> float | None:
    """Threshold energy (eV) from the first non-zero point, falling back to Q.

    NJOY writes the threshold as a zero-valued point immediately before the
    first positive value; sections that are non-zero from the first point and
    start at (or below) 1e-5 eV are non-threshold and return ``None``.
    """
    x = np.asarray(energy_ev, dtype=np.float64)
    y = np.asarray(xs_b, dtype=np.float64)
    nz = np.flatnonzero(y > 0.0)
    if nz.size == 0:
        return None
    first = int(nz[0])
    if first > 0:
        return float(x[first - 1])
    if x[0] > 1.5e-5:
        return float(x[0])
    if qi < 0.0 and awr > 0.0:
        return float(-qi * (awr + 1.0) / awr)
    return None


# --------------------------------------------------------------------------- #
# MF2 (resonance parameters) and MF33 (covariances) via endf-parserpy
# --------------------------------------------------------------------------- #
def _vals(d: Any) -> np.ndarray:
    """endf-parserpy 1-based dict {1: v1, 2: v2, ...} (or list) → float array."""
    if isinstance(d, dict):
        return np.array([float(d[k]) for k in sorted(d)], dtype=np.float64)
    return np.asarray(d, dtype=np.float64)


def _param_arrays(group: dict[str, Any]) -> tuple[list[str], list[list[float]], list[list[int]]]:
    """All numeric-array entries of a parameter group, flattened row-major with shapes."""
    names, values, shapes = [], [], []
    for key, v in group.items():
        if isinstance(v, dict) and v:
            first = v[next(iter(v))]
            if isinstance(first, dict):  # 2-D block (e.g. RML GAM[channel][resonance])
                rows = [_vals(v[k]) for k in sorted(v)]
                ncol = min(len(r) for r in rows)
                block = np.array([r[:ncol] for r in rows])
                names.append(key)
                values.append(block.ravel().tolist())
                shapes.append(list(block.shape))
            elif isinstance(first, int | float):
                arr = _vals(v)
                names.append(key)
                values.append(arr.tolist())
                shapes.append([int(arr.size)])
        elif isinstance(v, list) and v and isinstance(v[0], int | float):
            arr = np.asarray(v, dtype=np.float64)
            names.append(key)
            values.append(arr.tolist())
            shapes.append([int(arr.size)])
    return names, values, shapes


_FORMALISM = {(1, 1): "SLBW", (1, 2): "MLBW", (1, 3): "RM", (1, 4): "AA", (1, 7): "RML",
              (2, 1): "URR-A", (2, 2): "URR-B"}  # fmt: skip


def parse_mf2(
    mf2: dict[str, Any] | None,
) -> tuple[float | None, float | None, list[dict[str, Any]]]:
    """(resolved_upper_ev, unresolved_upper_ev, resonance rows) from an endf-parserpy MF2/151 dict.

    One row per (isotope, range, l-group[, j-group]) for LRF 1-3 and the URR,
    one per (isotope, range, spin group) for RML (LRF=7). ``param_names`` /
    ``param_values`` / ``param_shape`` carry the raw ENDF-6 arrays with their
    manual names (ER, AJ, GN, GG, GF, GFA, GFB, GT; URR: ES, D, GX, GN0, GG,
    GF; RML: PPI, L, SCH, BND, APE, APT, ER, GAM[nch, nres]).
    """
    if not mf2:
        return None, None, []
    resolved_upper: float | None = None
    unresolved_upper: float | None = None
    rows: list[dict[str, Any]] = []
    for iso_idx, iso in sorted(mf2.get("isotope", {}).items()):
        for rng_idx, rng in sorted(iso.get("range", {}).items()):
            lru, lrf = int(rng.get("LRU", 0)), int(rng.get("LRF", 0))
            el, eh = float(rng.get("EL", 0.0)), float(rng.get("EH", 0.0))
            if lru == 1:
                resolved_upper = eh if resolved_upper is None else max(resolved_upper, eh)
            elif lru == 2:
                unresolved_upper = eh if unresolved_upper is None else max(unresolved_upper, eh)
            else:
                continue  # LRU=0: scattering radius only
            base = {
                "isotope_index": int(iso_idx), "zai": float(iso.get("ZAI", 0.0)),
                "abundance": float(iso.get("ABN", 1.0)), "range_index": int(rng_idx),
                "lru": lru, "lrf": lrf,
                "formalism": _FORMALISM.get((lru, lrf), f"LRU{lru}LRF{lrf}"),
                "el_ev": el, "eh_ev": eh, "spi": float(rng.get("SPI", math.nan)),
                "ap": float(rng.get("AP", math.nan)), "lssf": int(rng.get("LSSF", -1)),
                "nro": int(rng.get("NRO", 0)), "naps": int(rng.get("NAPS", 0)),
            }  # fmt: skip
            if lrf == 7 and lru == 1:
                for jg_idx, jg in sorted(rng.get("j_group", {}).items()):
                    names, values, shapes = _param_arrays(jg)
                    rows.append({**base, "group_index": int(jg_idx), "l": None,
                                 "j": float(jg.get("AJ", math.nan)), "awri": math.nan,
                                 "n_res": int(jg.get("NRS", 0)), "param_names": names,
                                 "param_values": values, "param_shape": shapes})  # fmt: skip
                continue
            gi = 0
            for _, lg in sorted(rng.get("l_group", {}).items()):
                l_val = int(lg.get("L", -1))
                awri = float(lg.get("AWRI", math.nan))
                if "j_group" in lg:  # URR: parameters per (l, J)
                    for _, jg in sorted(lg["j_group"].items()):
                        gi += 1
                        names, values, shapes = _param_arrays(jg)
                        scal = {k: float(v) for k, v in jg.items() if isinstance(v, int | float)}
                        for k in ("D", "GN0", "GG", "GF", "GX", "AMUN", "AMUG", "AMUF", "AMUX"):
                            if k in scal and k not in names:  # energy-independent URR-A
                                names.append(k)
                                values.append([scal[k]])
                                shapes.append([1])
                        rows.append({**base, "group_index": gi, "l": l_val,
                                     "j": float(jg.get("AJ", math.nan)), "awri": awri,
                                     "n_res": int(jg.get("NE", 0)), "param_names": names,
                                     "param_values": values, "param_shape": shapes})  # fmt: skip
                else:
                    gi += 1
                    names, values, shapes = _param_arrays(lg)
                    rows.append({**base, "group_index": gi, "l": l_val, "j": None, "awri": awri,
                                 "n_res": int(lg.get("NRS", 0)), "param_names": names,
                                 "param_values": values, "param_shape": shapes})  # fmt: skip
    return resolved_upper, unresolved_upper, rows


def assemble_mf33(
    section: dict[str, Any], mt: int
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]] | None:
    """Self-covariance of ``mt`` (MT1 == mt) as a relative covariance matrix on a union bin grid.

    Handled NI sub-subsection flavours: LB=5 (matrix, symmetric if LS=1),
    LB=1/LB=8 (diagonal variances per bin), LB=2 (fully correlated, F_k F_l).
    LB=0 (absolute), 3, 4, 6 and LT>0 blocks are counted in ``meta['skipped']``
    and not added; NC-type (derived) sub-subsections are flagged. Returns
    ``(energy_bounds_ev [n+1], rel_cov [n, n], meta)`` or ``None`` if nothing usable.
    """
    comps: list[tuple[np.ndarray, np.ndarray]] = []
    meta: dict[str, Any] = {"n_ni": 0, "nc": 0, "skipped": [], "lb": []}
    mat = int(section.get("MAT", 0))
    for _, sub in sorted(section.get("subsection", {}).items()):
        if int(sub.get("MT1", -1)) != mt or int(sub.get("MAT1", 0)) not in (0, mat):
            continue
        meta["nc"] += int(sub.get("NC", 0) or 0)
        for _, ni in sorted(sub.get("ni_subsection", {}).items()):
            lb = int(ni.get("LB", -1))
            lt = int(ni.get("LT", 0) or 0)
            meta["n_ni"] += 1
            meta["lb"].append(lb)
            if lb == 5:
                e = _vals(ni["E"])
                n = e.size - 1
                m = np.zeros((n, n))
                for k, row in ni["F"].items():
                    for col, v in row.items():
                        m[int(k) - 1, int(col) - 1] = float(v)
                if int(ni.get("LS", 0)) == 1:
                    m = m + m.T - np.diag(np.diag(m))
                comps.append((e, m))
            elif lb in (1, 8) and lt == 0:
                # endf-parserpy names the LB=1/2/8 pairs E/F (ENDF-102 calls them E_k/F_k).
                ek = _vals(ni["E"] if "E" in ni else ni["Ek"])
                fk = _vals(ni["F"] if "F" in ni else ni["Fk"])
                comps.append((ek, np.diag(fk[: ek.size - 1])))
            elif lb == 2 and lt == 0:
                ek = _vals(ni["E"] if "E" in ni else ni["Ek"])
                fk = _vals(ni["F"] if "F" in ni else ni["Fk"])[: ek.size - 1]
                comps.append((ek, np.outer(fk, fk)))
            else:
                meta["skipped"].append(f"LB{lb}LT{lt}")
    if not comps:
        return None
    bounds = np.unique(np.concatenate([e for e, _ in comps]))
    n = bounds.size - 1
    cov = np.zeros((n, n))
    mid = 0.5 * (bounds[:-1] + bounds[1:])
    for e, m in comps:
        idx = np.searchsorted(e, mid, side="right") - 1
        inside = (idx >= 0) & (idx < m.shape[0])
        sel = np.flatnonzero(inside)
        sub = m[np.ix_(idx[sel], idx[sel])]
        cov[np.ix_(sel, sel)] += sub
    meta["n_bins"] = int(n)
    return bounds, cov, meta


# --------------------------------------------------------------------------- #
# s-wave statistics from the ladders (plan step 2: D0, S0, <Γγ> for WP-14)
# --------------------------------------------------------------------------- #
def _g_factor(j: np.ndarray | float, spi: float | None) -> np.ndarray | float:
    """Spin statistical factor g = (2J+1) / (2(2I+1)); NaN without a target spin."""
    if spi is None or (isinstance(spi, float) and math.isnan(spi)):
        return np.nan if np.isscalar(j) else np.full(np.shape(j), np.nan)
    return (2.0 * np.abs(j) + 1.0) / (2.0 * (2.0 * spi + 1.0))


def ladder_stats(rows: list[dict[str, Any]], target_spin: float | None = None) -> dict[str, Any]:
    """s-wave statistics of one nuclide from its MF2 ladder rows (:func:`parse_mf2` output).

    Resolved region (LRU=1): every l=0 resonance with ``0 < ER <= EH`` of its
    range counts. ``d0_ev`` is the mean spacing ``(E_last - E_first) / (n - 1)``,
    ``s0`` the s-wave strength function ``Σ g Γn⁰ / (n · D0)`` with the reduced
    width ``Γn⁰ = Γn / sqrt(ER [eV])`` (so ``s0`` is dimensionless, ~1e-4), and
    ``gamma_gamma_ev`` the mean radiation width over resonances with Γγ > 0.
    For R-matrix-limited ladders (LRF=7) the neutron channel is taken as
    particle pair 2 with L=0 and the eliminated capture width as particle pair
    1 (ENDF-102 ordering for KRM=3); ``rml_pair_assumed`` flags such nuclides.
    Unresolved region (LRU=2, l=0): the averages at the lowest tabulated energy
    give ``d0_urr_ev = 1/Σ_J(1/D_J)``, ``s0_urr = Σ_J g_J <Γn⁰>_J / D_J`` and the
    spacing-weighted ``gamma_gamma_urr_ev``. Missing quantities are NaN.
    """
    out: dict[str, Any] = {
        "n_res_rrr_total": 0, "n_res_l0": 0, "e_first_l0_ev": math.nan, "e_last_l0_ev": math.nan,
        "d0_ev": math.nan, "s0": math.nan, "g_gn0_mean_ev": math.nan,
        "gamma_gamma_ev": math.nan, "gamma_gamma_median_ev": math.nan, "n_gamma_gamma": 0,
        "d0_urr_ev": math.nan, "s0_urr": math.nan, "gamma_gamma_urr_ev": math.nan,
        "urr_lower_ev": math.nan, "rml_pair_assumed": False, "formalisms": [],
    }  # fmt: skip
    er_all: list[np.ndarray] = []
    ggn0_all: list[np.ndarray] = []
    gg_all: list[np.ndarray] = []
    inv_d = s0_urr = gg_w = 0.0
    urr_lower = math.inf
    forms: set[str] = set()
    for r in rows:
        names = list(r.get("param_names") or [])
        d = dict(zip(names, r.get("param_values") or [], strict=False))
        shapes = dict(zip(names, r.get("param_shape") or [], strict=False))
        lru, lrf = int(r.get("lru", 0)), int(r.get("lrf", 0))
        forms.add(str(r.get("formalism", "")))
        spi = r.get("spi")
        if spi is None or (isinstance(spi, float) and math.isnan(spi)):
            spi = target_spin
        if lru == 1:
            out["n_res_rrr_total"] += int(r.get("n_res", 0) or 0)
            eh = float(r.get("eh_ev", math.inf) or math.inf)
            if lrf == 7:
                if "GAM" not in d or "PPI" not in d or "ER" not in d:
                    continue
                gam = np.asarray(d["GAM"], dtype=np.float64).reshape(shapes["GAM"])
                ppi = np.asarray(d["PPI"], dtype=np.int64)
                lch = np.asarray(d.get("L", np.zeros_like(ppi)), dtype=np.int64)
                n_idx = np.flatnonzero((ppi == 2) & (lch == 0))
                if n_idx.size == 0:
                    continue
                out["rml_pair_assumed"] = True
                er = np.asarray(d["ER"], dtype=np.float64)
                gn = gam[n_idx].sum(axis=0)
                g_idx = np.flatnonzero(ppi == 1)
                gg = gam[g_idx[0]] if g_idx.size else np.full(er.size, np.nan)
                aj = np.full(er.size, abs(float(r.get("j") or 0.0)))
            else:
                if r.get("l") != 0 or "ER" not in d or "GN" not in d:
                    continue
                er = np.asarray(d["ER"], dtype=np.float64)
                gn = np.asarray(d["GN"], dtype=np.float64)
                gg = np.asarray(d.get("GG", np.full(er.size, np.nan)), dtype=np.float64)
                aj = np.abs(np.asarray(d.get("AJ", np.zeros(er.size)), dtype=np.float64))
            n = min(er.size, gn.size, gg.size, aj.size)
            er, gn, gg, aj = er[:n], gn[:n], gg[:n], aj[:n]
            mask = (er > 0.0) & (er <= eh)
            if not mask.any():
                continue
            er_all.append(er[mask])
            ggn0_all.append(_g_factor(aj[mask], spi) * gn[mask] / np.sqrt(er[mask]))
            gg_all.append(gg[mask])
        elif lru == 2 and r.get("l") == 0:
            if "D" not in d or "GN0" not in d:
                continue
            dj = float(np.asarray(d["D"], dtype=np.float64).ravel()[0])
            if not dj > 0.0:
                continue
            gn0 = float(np.asarray(d["GN0"], dtype=np.float64).ravel()[0])
            ggj = float(np.asarray(d.get("GG", [math.nan]), dtype=np.float64).ravel()[0])
            j = r.get("j")
            if j is None and "AJ" in d:
                j = float(np.asarray(d["AJ"]).ravel()[0])
            g = _g_factor(abs(float(j)), spi) if j is not None else math.nan
            inv_d += 1.0 / dj
            s0_urr += g * gn0 / dj
            gg_w += ggj / dj if not math.isnan(ggj) else 0.0
            es = np.asarray(d.get("ES", [r.get("el_ev", math.nan)]), dtype=np.float64).ravel()
            urr_lower = min(urr_lower, float(es[0]))
    out["formalisms"] = sorted(f for f in forms if f)
    if er_all:
        er = np.concatenate(er_all)
        ggn0 = np.concatenate(ggn0_all)
        gg = np.concatenate(gg_all)
        order = np.argsort(er)
        er, ggn0, gg = er[order], ggn0[order], gg[order]
        n = int(er.size)
        out["n_res_l0"] = n
        out["e_first_l0_ev"], out["e_last_l0_ev"] = float(er[0]), float(er[-1])
        if n >= 2 and er[-1] > er[0]:
            d0 = float((er[-1] - er[0]) / (n - 1))
            out["d0_ev"] = d0
            out["g_gn0_mean_ev"] = float(np.mean(ggn0))  # NaN without a target spin
            out["s0"] = float(np.sum(ggn0) / (n * d0))
        pos = gg[np.isfinite(gg) & (gg > 0)]
        out["n_gamma_gamma"] = int(pos.size)
        if pos.size:
            out["gamma_gamma_ev"] = float(pos.mean())
            out["gamma_gamma_median_ev"] = float(np.median(pos))
    if inv_d > 0.0:
        out["d0_urr_ev"] = 1.0 / inv_d
        out["s0_urr"] = float(s0_urr)
        out["gamma_gamma_urr_ev"] = gg_w / inv_d if gg_w > 0 else math.nan
        out["urr_lower_ev"] = urr_lower
    return out


# --------------------------------------------------------------------------- #
# Per-material processing (runs inside a worker process)
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class MaterialTask:
    source: MaterialSource
    mts: tuple[int, ...] = CAPTURE_MTS
    cov_mts: tuple[int, ...] = COV_MTS
    temperatures: tuple[float, ...] = ()
    error: float = 1e-3
    workroot: Path = EXTRACT / "njoy"
    keep_workdir: bool = False


@dataclass
class MaterialResult:
    name: str
    library: str
    status: str  # "ok" | "skip" | "error"
    message: str = ""
    seconds: float = 0.0
    Z: int | None = None
    N: int | None = None
    iso: int = 0
    nuclide_id: str | None = None
    library_version: str | None = None
    mat: int | None = None
    resolved_upper_ev: float | None = None
    unresolved_upper_ev: float | None = None
    lssf: int | None = None
    formalisms: list[str] = field(default_factory=list)
    n_resonances: int = 0
    mf33_mts: list[int] = field(default_factory=list)
    mf32: bool = False
    # (mt, temperature_k) → values on the common grid
    xs: dict[tuple[int, float], np.ndarray] = field(default_factory=dict)
    thresholds: dict[int, float | None] = field(default_factory=dict)
    resonance_rows: list[dict[str, Any]] = field(default_factory=list)
    # mt → (bounds, cov, meta)
    covariances: dict[int, tuple[np.ndarray, np.ndarray, dict[str, Any]]] = field(
        default_factory=dict
    )
    peak_rss_mb: float = 0.0


def _rss_mb() -> float:
    try:
        import resource

        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
    except Exception:  # pragma: no cover
        return 0.0


def stage_material(
    src: MaterialSource, workdir: Path, cov_mts: Iterable[int]
) -> tuple[Path, Path, set[tuple[int, int]]]:
    """One streaming pass over the material: write the full tape for NJOY (``tape20``)
    and a reduced tape for endf-parserpy (``tape_parse``: MF1/451, MF2, MF33 of
    ``cov_mts``) with correct SEND/FEND/MEND/TEND, and record every (MF, MT)
    section present. Keeps the parser's memory bounded for GB-scale JENDL-5
    actinides whose MF6/MF32/MF34 would otherwise be parsed for nothing.
    """
    want_cov = {int(m) for m in cov_mts}
    tape20 = workdir / "tape20"
    tape_parse = workdir / "tape_parse"
    present: set[tuple[int, int]] = set()
    sec_kept = mf_kept = False
    lines = src.iter_lines()
    with open(tape20, "wb") as full, open(tape_parse, "wb") as small:
        try:
            first = next(lines)
        except StopIteration:
            return tape20, tape_parse, present
        full.write(first)
        if first[70:75] == b" 1451":  # no TPID line: synthesise one so both tapes are tapes
            small.write(f"{'':66}   1 0  0    0\n".encode())
            lines = iter([first, *lines])
        else:
            small.write(first)
        for line in lines:
            full.write(line)
            if len(line) < 75:
                continue
            mat = _int(line[66:70].decode())
            mf, mt = _int(line[70:72].decode()), _int(line[72:75].decode())
            if mat <= 0:  # MEND / TEND
                small.write(line)
                continue
            if mf == 0:  # FEND
                if mf_kept:
                    small.write(line)
                mf_kept = False
                continue
            if mt == 0:  # SEND
                if sec_kept:
                    small.write(line)
                sec_kept = False
                continue
            present.add((mf, mt))
            if (mf == 1 and mt == 451) or mf == 2 or (mf == 33 and mt in want_cov):
                small.write(line)
                sec_kept = mf_kept = True
    return tape20, tape_parse, present


def process_material(task: MaterialTask) -> MaterialResult:
    """ENDF-6 material → reconstructed grid values, MF2 ladders, MF33 blocks."""
    from data.schema.keys import nuclide_id as make_nuclide_id

    t0 = time.time()
    src = task.source
    spec = LIBRARIES[src.library]
    res = MaterialResult(name=src.name, library=spec.name, status="error")
    safe_name = re.sub(r"[^A-Za-z0-9_.-]", "_", src.name)
    workdir = task.workroot / src.library / f"{os.getpid()}-{safe_name}"
    try:
        try:
            hdr = read_header(src.head_text(12))
        except ValueError as exc:  # README/LICENSE/index files inside library archives
            res.status, res.message = "skip", f"not an ENDF-6 material: {exc}"
            return res
        res.mat = hdr.mat
        if hdr.Z <= 0 or hdr.A <= 0 or hdr.N < 0:
            res.status, res.message = "skip", f"not a nuclide target (ZA={hdr.za:g})"
            return res
        if hdr.nsub not in (10, 0):
            res.status, res.message = "skip", f"NSUB={hdr.nsub} is not incident-neutron"
            return res
        res.Z, res.N, res.iso = hdr.Z, hdr.N, hdr.liso
        res.nuclide_id = make_nuclide_id(hdr.Z, hdr.N, hdr.liso)
        res.library_version = (
            f"{spec.name} NLIB={hdr.nlib} NVER={hdr.nver} LREL={hdr.lrel} "
            f"NMOD={hdr.nmod} MAT={hdr.mat}"
        )
        if workdir.exists():
            shutil.rmtree(workdir)
        workdir.mkdir(parents=True, exist_ok=True)
        tape20, tape_parse, present = stage_material(src, workdir, task.cov_mts)
        res.mf32 = any(mf == 32 for mf, _ in present)
        res.mf33_mts = sorted(mt for mf, mt in present if mf == 33)
        if not any(mf == 3 for mf, _ in present):
            res.status, res.message = "skip", "no MF3 cross sections in this material"
            return res

        # MF2 + MF33 of the original evaluation (from the reduced tape).
        from endf_parserpy import EndfParserCpp

        parser = EndfParserCpp()
        try:
            parsed = parser.parsefile(str(tape_parse), include=[2, 33])
        except Exception as exc:  # keep going without ladders/covariances
            parsed = {}
            res.message += f"endf-parserpy MF2/33 failed: {exc!r:.200}; "
        mf2 = parsed.get(2, {}).get(151) if isinstance(parsed.get(2), dict) else None
        try:
            res.resolved_upper_ev, res.unresolved_upper_ev, rows = parse_mf2(mf2)
        except Exception as exc:
            rows = []
            res.message += f"MF2 ladder extraction failed: {exc!r:.200}; "
        for r in rows:
            r.update({"library": spec.name, "nuclide_id": res.nuclide_id,
                      "Z": hdr.Z, "N": hdr.N, "iso": hdr.liso})  # fmt: skip
            if r["lru"] == 2 and r["lssf"] >= 0:
                res.lssf = r["lssf"]
        res.resonance_rows = rows
        res.formalisms = sorted({r["formalism"] for r in rows})
        res.n_resonances = sum(r["n_res"] for r in rows if r["lru"] == 1)
        mf33 = parsed.get(33, {}) if isinstance(parsed.get(33), dict) else {}
        for mt in task.cov_mts:
            if mt in mf33:
                try:
                    block = assemble_mf33(mf33[mt], mt)
                except Exception as exc:
                    res.message += f"MF33/{mt} assembly failed: {exc!r:.120}; "
                    continue
                if block is not None:
                    res.covariances[mt] = block
        del parsed, mf33
        tape_parse.unlink(missing_ok=True)

        # NJOY: RECONR (+ BROADR).
        tapes = run_njoy(tape20, hdr.mat, workdir, error=task.error, temperatures=task.temperatures)
        for temp, pendf in tapes.items():
            sections = read_pendf_mf3(pendf, task.mts)
            if spec.mf3_original_only:
                sections = {mt: v for mt, v in sections.items() if (3, mt) in present}
            for mt, sec in sections.items():
                if sec.energy_ev.size == 0 or not np.any(sec.xs_b > 0):
                    continue
                res.xs[(mt, temp)] = to_grid(sec.energy_ev, sec.xs_b)
                if temp == 0.0:
                    res.thresholds[mt] = threshold_from_pointwise(
                        sec.energy_ev, sec.xs_b, sec.qi, hdr.awr
                    )
            del sections
        res.status = "ok"
    except subprocess.TimeoutExpired:
        res.status, res.message = "error", f"njoy timeout after {NJOY_TIMEOUT_S}s"
    except Exception as exc:
        res.status, res.message = "error", f"{type(exc).__name__}: {exc}"[:2000]
    finally:
        res.seconds = time.time() - t0
        res.peak_rss_mb = _rss_mb()
        if not task.keep_workdir:
            shutil.rmtree(workdir, ignore_errors=True)
    return res


# --------------------------------------------------------------------------- #
# Record building (main process)
# --------------------------------------------------------------------------- #
def result_to_records(result: MaterialResult, spec: LibrarySpec) -> list[Any]:
    """``MaterialResult`` → validated ``EvaluatedXS`` records."""
    from data.schema.evaluated import EvaluatedXS

    if result.status != "ok" or result.Z is None or result.N is None:
        return []
    res_ref = (
        f"staging/evaluated/{spec.key}_resonances.parquet#{result.nuclide_id}"
        if result.resonance_rows
        else None
    )
    out = []
    for (mt, temp), values in sorted(result.xs.items()):
        cov_ref = (
            f"staging/evaluated/{spec.key}_cov.zarr#{result.nuclide_id}/mt{mt}"
            if mt in result.covariances
            else None
        )
        out.append(
            EvaluatedXS(
                library=spec.name,
                library_version=result.library_version,
                Z=result.Z,
                N=result.N,
                iso=result.iso,
                mt=mt,
                temperature_k=float(temp),
                values_b=values,
                threshold_ev=result.thresholds.get(mt),
                resolved_upper_ev=result.resolved_upper_ev,
                unresolved_upper_ev=result.unresolved_upper_ev,
                resonance_ref=res_ref,
                covariance_ref=cov_ref,
            )
        )
    return out


def result_summary_row(result: MaterialResult) -> dict[str, Any]:
    """The per-material line written to ``<lib>_done.jsonl`` (resume + summary input)."""
    return {
        "name": result.name,
        "status": result.status,
        "message": result.message,
        "seconds": round(result.seconds, 2),
        "peak_rss_mb": round(result.peak_rss_mb, 1),
        "Z": result.Z,
        "N": result.N,
        "iso": result.iso,
        "nuclide_id": result.nuclide_id,
        "mat": result.mat,
        "mts": sorted({mt for mt, _ in result.xs}),
        "temperatures": sorted({t for _, t in result.xs}),
        "resolved_upper_ev": result.resolved_upper_ev,
        "unresolved_upper_ev": result.unresolved_upper_ev,
        "lssf": result.lssf,
        "formalisms": result.formalisms,
        "n_resonances": result.n_resonances,
        "mf33_mts": result.mf33_mts,
        "cov_mts": sorted(result.covariances),
        "mf32": result.mf32,
    }


def iter_done(path: Path) -> Iterator[dict[str, Any]]:
    if not path.exists():
        return
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if line:
                yield json.loads(line)


def dump_json(obj: Any) -> str:
    return json.dumps(obj, default=lambda o: o.tolist() if isinstance(o, np.ndarray) else str(o))


def _self_test() -> None:  # pragma: no cover - manual smoke check
    buf = io.StringIO()
    print(njoy_deck(7925, 1e-3, (293.6,)), file=buf)
    print(buf.getvalue())


if __name__ == "__main__":  # pragma: no cover
    _self_test()
