"""KWCOV B6: the optical-model deck keywords that are files, energy ranges or energy tables.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T4 (physics/hf/CONTRACT.md §7). Acceptance test: KWCOV-B6 (tests/hf/test_kwcov_b6.py).

TALYS routines ported here (file:line of the subroutine statement):
    input_ompmodel.f90:1 (input_ompmodel)   optmod, optmodfilen, optmodfilep, the 12 `*adjustF` range keywords
    getvalues.f90:1 (getvalues)             lines 303-365: the energy-local form of an adjustment keyword
                                            (`key p value Ea Eb Em D` or `key p value <file>`)
    adjust.f90:1 (adjust)                   the energy-local factor (adjustment table or Ea/Eb/Em/D bump)
    ompadjust.f90:1 (ompadjust)             `Fv1 = factor * v1adjust(k)` ... applied at the potential's energy
    omppar.f90:1 (omppar)                   lines 243-277: reading an `optmod` table (header `Z A nlines [Ef]`, then
                                            `E` + the 19 OMP columns per line)

What it does. `fitlib._cards` hands the run's keyword lines to `extract` before its own classification; the lines it
understands come back as one `OMPDeck` on the run's `Cards` (`Cards.omp`), and every engine path reaches it through
`active()`:

* `optmod Z A file [p]` -> `tables(Z, A)`, merged into `omp.parameters.omp_parameters` before the RIPL default (an
  explicit table wins, as `optmod(Zix, Nix, k) == ' '` gates the RIPL retrieval, omppar.f90:191).
* `optmodfilen Z file`, `optmodfilep Z file` -> `local_file(Z, k)`, read by `omp.parameters.read_local_omp` in place of
  `structure/optical/{neutron,proton}/<p>-<El>.omp`.
* `rvadjustF p E1 E2 D s` ... `awsoadjustF` -> the `ompadjustE1/E2/D/s` cells of `Params` (written by
  `fitlib.apply_params`), which `omp.parameters.adjustF` already applies.
* `v1adjust p value Ea Eb Em D` and `v1adjust p value <table>` for the 28 `ompadjust` keywords -> `TBump`s, applied by
  `factors` on the F* factors with TALYS's rules: the bump of particle k acts where `ompadjust(E, ktype)` runs with
  ktype = k, i.e. the incident channel (only with `incadjust y`, ompadjust.f90:92) and the OUTGOING channels of every
  particle but the projectile (the projectile leaving takes type 0, flagompejec, opticalnp.f90:175); several lines of
  one keyword: the last one whose range holds E wins (adjust.f90 assigns); a table's depth is `value * D(E)`
  (getvalues.f90:353) and outside the table the factor is 1.

A relative file name is looked up as TALYS does, in the working directory, then (the port's addition, because a best
file names its files relative to the run directory TALYS's user copies them into) in the directory of the best file the
line came from and its `misc/tables`; a name that differs only in case is accepted (TALYS keeps the case of `optmod`
file names, convert.f90, but `fitlib` lowercases deck lines). A file that is not found stops the run, as in TALYS.

Default OFF: a run without these lines has `Cards.omp == ()`; `active()` is None and no hook changes anything.
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from pathlib import Path

import numpy as np

PARSYM = ("g", "n", "p", "d", "t", "h", "a")

#: input_ompmodel.f90:249-262 -- the 12 range keywords and their `omptype`
ADJUSTF = {
    "rvadjustf": 1, "avadjustf": 2, "rwadjustf": 3, "awadjustf": 4, "rvdadjustf": 5, "avdadjustf": 6,
    "rwdadjustf": 7, "awdadjustf": 8, "rvsoadjustf": 9, "avsoadjustf": 10, "rwsoadjustf": 11, "awsoadjustf": 12,
}  # fmt: skip
#: ompadjust.f90 -- the 28 keywords with an F* factor (same set as omp.parameters._ADJ)
OMPADJ = frozenset({
    "v1adjust", "v2adjust", "v3adjust", "v4adjust", "rvadjust", "avadjust",
    "w1adjust", "w2adjust", "w3adjust", "w4adjust", "rwadjust", "awadjust",
    "rvdadjust", "avdadjust", "d1adjust", "d2adjust", "d3adjust", "rwdadjust", "awdadjust",
    "vso1adjust", "vso2adjust", "rvsoadjust", "avsoadjust", "wso1adjust", "wso2adjust",
    "rwsoadjust", "awsoadjust", "rcadjust",
})  # fmt: skip
NUMRANGE = 10  # A0_talys_mod.f90:40
NUMOMP = 500  # A0_talys_mod.f90:52
NUMENADJ = 1000  # A0_talys_mod.f90:42


@dataclass(frozen=True)
class TBump:
    """One energy-local adjustment line of an `ompadjust` keyword (getvalues.f90:303-365)."""

    key: str
    k: int                 # particle type 0..6 (the `ktype` it acts on)
    kind: str              # "tal": (Ea, Eb, Em, D); "tab": (energies, depths), depths already x value
    args: tuple


@dataclass(frozen=True)
class Table:
    """An `optmod` file: the nucleus and particle it is for, and its rows (sha256 for the cache keys)."""

    Z: int
    A: int
    k: int
    path: str
    sha: str
    ef: float              # header Ef (0: keep omppar's)
    e: tuple               # energies (MeV)
    rows: tuple            # 19 columns per energy


@dataclass(frozen=True)
class OMPDeck:
    tables: tuple = ()     # Table
    files: tuple = ()      # (Z, k, path) optmodfilen / optmodfilep
    ranges: tuple = ()     # (k, omptype, E1, E2, D, s) in input order
    bumps: tuple = ()      # TBump in input order


def _sgl(x: float) -> float:
    return float(np.float32(x))


def _num(s: str) -> float:
    return float(s.lower().replace("d", "e"))


def _is_name(w: str) -> bool:
    """getvalues.f90:310: a word that starts with a letter is a file name, otherwise a number. The port also takes a
    word with a `/` (an absolute or relative path, which TALYS would try to read as a number and drop the adjustment)."""
    return bool(w) and (w[0].isalpha() or "/" in w)


def resolve(name: str, dirs) -> Path:
    """The file a deck line names: as given (absolute, or relative to the working directory), then in `dirs`; an
    exact name first, then one that differs only in case. FileNotFoundError when there is none (TALYS stops too).

    TALYS: getvalues.f90:1 (getvalues) -- `inquire (file = adfile, exist = lexist)`
    Test: tests/hf/test_kwcov_b6.py
    """
    p = Path(os.path.expanduser(name))
    cands = [p] if p.is_absolute() else [Path.cwd() / p] + [Path(d) / p for d in dirs]
    for c in cands:
        if c.is_file():
            return c
    for c in cands:
        par = c.parent
        if par.is_dir():
            low = c.name.lower()
            for x in sorted(par.iterdir()):
                if x.name.lower() == low and x.is_file():
                    return x
    raise FileNotFoundError(f"TALYS-error: file {name!r} does not exist (looked in the working directory"
                            + (", " + ", ".join(str(d) for d in dirs) if dirs else "") + ")")


def read_table(path: Path, Z: int, A: int, k: int) -> Table:
    """An `optmod` file as omppar.f90:243-277 reads it.

    TALYS: omppar.f90:1 (omppar) lines 243-277
    Test: tests/hf/test_kwcov_b6.py
    """
    raw = path.read_bytes()
    lines = raw.decode(errors="replace").splitlines()
    if not lines:
        raise ValueError(f"TALYS-error: {path}: empty optmod file")
    head = lines[0].split()
    try:
        nlines = int(head[2])
        ef = _num(head[3]) if len(head) > 3 else 0.0
    except (IndexError, ValueError) as exc:
        raise ValueError(f"TALYS-error: {path}: header must be `Z A nlines [Ef]`") from exc
    if nlines > NUMOMP:
        raise ValueError(f"TALYS-error: number of lines in OMP file > {NUMOMP}")
    toks = " ".join(lines[1:]).split()
    e, rows = [], []
    for n in range(nlines):  # list-directed reads: 20 numbers per record, wherever the line breaks fall
        rec = toks[20 * n: 20 * n + 20]
        if len(rec) < 20:
            break  # end of file (istat == -1): the lines read so far
        vals = [_sgl(_num(x)) for x in rec]
        e.append(vals[0])
        rows.append(tuple(vals[1:]))
    if len(e) == 1:  # omppar.f90:268-274
        e, rows = e * 2, rows * 2
    if not e:
        raise ValueError(f"TALYS-error: {path}: no OMP lines")
    return Table(int(Z), int(A), int(k), str(path), hashlib.sha256(raw).hexdigest()[:16], _sgl(ef), tuple(e),
                 tuple(rows))


def read_adjust_table(path: Path, value: float) -> tuple[tuple, tuple]:
    """An adjustment table (`E D` per line), as getvalues.f90:310-320 reads it; depths are `value * D`.

    TALYS: getvalues.f90:1 (getvalues) lines 303-365
    Test: tests/hf/test_kwcov_b6.py
    """
    es: list[float] = []
    ds: list[float] = []
    prev = 0.0
    for ln in path.read_text(errors="replace").splitlines():
        w = ln.replace(",", " ").split()
        if not w:
            continue
        try:
            ee, dd = _sgl(_num(w[0])), _sgl(_num(w[1]))
        except (ValueError, IndexError) as exc:
            raise ValueError(f"TALYS-error: parameter file {path} has wrong format") from exc
        if ee == prev:
            continue
        if ee < prev:
            raise ValueError(f"TALYS-error: parameter file {path} must have energies in increasing order")
        es.append(ee)
        ds.append(_sgl(value * dd))
        prev = ee
        if len(es) >= NUMENADJ:
            raise ValueError(f"TALYS-error: parameter file {path} has more than {NUMENADJ} energies")
    return tuple(es), tuple(ds)


def _particle(w: str, line: str) -> int:
    c = w[:1].lower()
    if c == "e":
        c = "g"
    if c not in PARSYM:
        raise ValueError(f"TALYS-error: wrong particle symbol for: {line!r}")
    return PARSYM.index(c)


def extract(lines, Z: int, A: int, dirs=()) -> tuple[tuple, OMPDeck | tuple]:
    """Split the run's keyword lines into (the lines `fitlib._split` still classifies, the `OMPDeck` of the lines
    handled here, or () when there are none). An energy-local adjustment line goes back as its plain form
    (`v1adjust n 1.02`), because TALYS assigns the value as well (getvalues.f90:356 `flagassign`).

    `Z, A` is the target; `optmod` and `optmodfile*` name absolute nuclides, kept as such (a nucleus outside the run's
    box is never asked for, TALYS's own warning case).

    TALYS: input_ompmodel.f90:1 (input_ompmodel), getvalues.f90:1 (getvalues)
    Test: tests/hf/test_kwcov_b6.py
    """
    keep: list[str] = []
    tables: dict = {}
    files: dict = {}
    ranges: list = []
    bumps: list = []
    nrange: dict = {}
    for line in lines:
        w = line.split()
        if not w:
            continue
        k = w[0].lower()
        if k == "optmod":  # input_ompmodel.f90:168-188: `optmod Z A file [particle]`
            if len(w) < 4:
                raise ValueError(f"deck line {line!r}: expected `optmod Z A file [particle]`")
            iz, ia = int(w[1]), int(w[2])
            kk = _particle(w[4], line) if len(w) > 4 else 1
            if kk == 0:
                raise ValueError(f"deck line {line!r}: no optical model for photons")
            tables[(iz, ia, kk)] = read_table(resolve(w[3], dirs), iz, ia, kk)
            continue
        if k in ("optmodfilen", "optmodfilep"):  # getvalues class 10: `optmodfilen Z file`
            if len(w) < 3:
                raise ValueError(f"deck line {line!r}: expected `{k} Z file`")
            kk = 1 if k.endswith("n") else 2
            files[(int(w[1]), kk)] = str(resolve(w[2], dirs))
            continue
        if k in ADJUSTF:  # input_ompmodel.f90:249-283: `rvadjustF p E1 E2 D s`
            if len(w) < 6:
                raise ValueError(f"deck line {line!r}: TALYS reads `{k} <particle> E1 E2 D s` (read_error "
                                 "without s)")
            kk = _particle(w[1], line)
            if kk == 0:  # parsym(1..6) only: a photon line is TALYS's read_error
                raise ValueError(f"deck line {line!r}: wrong particle")
            n = nrange.get((kk, ADJUSTF[k]), 0) + 1
            if n > NUMRANGE:
                raise ValueError(f"deck line {line!r}: more than {NUMRANGE} ranges for {k} {PARSYM[kk]}")
            nrange[(kk, ADJUSTF[k])] = n
            ranges.append((kk, ADJUSTF[k], _sgl(_num(w[2])), _sgl(_num(w[3])), _sgl(_num(w[4])), _sgl(_num(w[5]))))
            continue
        if k in OMPADJ and len(w) > 3:  # getvalues class 6 + the energy-local tail
            kk = _particle(w[1], line)
            val = _num(w[2])
            if _is_name(w[3]):
                es, ds = read_adjust_table(resolve(w[3], dirs), val)
                if es:
                    bumps.append(TBump(k, kk, "tab", (es, ds)))
            else:
                try:
                    ea, eb, em, d = (_sgl(_num(x)) for x in w[3:7])
                    bumps.append(TBump(k, kk, "tal", (ea, eb, em, d)))
                except ValueError:
                    pass  # getvalues.f90:322-325 `err = 10, end = 10`: the value only, no local adjustment
            keep.append(" ".join(w[:3]))
            continue
        keep.append(line)
    if not (tables or files or ranges or bumps):
        return tuple(keep), ()
    return tuple(keep), OMPDeck(tuple(tables.values()), tuple((z, kk, p) for (z, kk), p in files.items()),
                                tuple(ranges), tuple(bumps))


def drop_bumps(deck, k: int):
    """`deck` without the energy-local lines of particle `k` (incadjust n for the projectile: ompadjust.f90:92 never
    evaluates them -- the incident channel skips every factor and the projectile leaving takes type 0).

    TALYS: ompadjust.f90:1 (ompadjust)
    Test: tests/hf/test_kwcov_b6.py
    """
    if not deck or not any(b.k == k for b in deck.bumps):
        return deck
    nd = OMPDeck(deck.tables, deck.files, deck.ranges, tuple(b for b in deck.bumps if b.k != k))
    return nd if (nd.tables or nd.files or nd.ranges or nd.bumps) else ()


def range_cells(deck) -> tuple:
    """The `ompadjustE1/E2/D/s` cells the range lines write: ((keyword, (type, omptype-1, nr-1), value), ...).

    TALYS: input_ompmodel.f90:1 (input_ompmodel)
    Test: tests/hf/test_kwcov_b6.py
    """
    if not deck:
        return ()
    out, n = [], {}
    for kk, ot, e1, e2, d, s in deck.ranges:
        nr = n.get((kk, ot), 0)
        n[(kk, ot)] = nr + 1
        for key, v in (("ompadjuste1", e1), ("ompadjuste2", e2), ("ompadjustd", d), ("ompadjusts", s)):
            out.append((key, (kk, ot - 1, nr), v))
    return tuple(out)


# ------------------------------------------------------------------------------------------- the run's active set
def active() -> OMPDeck | None:
    """The active run's OMPDeck, None when it has none (the default).

    TALYS: (none -- the run's state, as fitlib.active)
    Test: tests/hf/test_kwcov_b6.py
    """
    from physics.hf.input import fitlib

    c = fitlib.active()
    d = getattr(c, "omp", ()) if c is not None else ()
    return d or None


def on() -> bool:
    """True when any B6 file / table / energy-local line is active: the native OMP fast path (omp_nx2) stands aside.

    TALYS: (none -- a port guard)
    Test: tests/hf/test_kwcov_b6.py
    """
    d = active()
    return d is not None and bool(d.tables or d.files or d.bumps)


def tables(Z: int, A: int) -> dict:
    """{particle: (OMPTable, Ef)} of the `optmod` files for nucleus (Z, A); {} when none.

    TALYS: omppar.f90:1 (omppar)
    Test: tests/hf/test_kwcov_b6.py
    """
    d = active()
    if d is None or not d.tables:
        return {}
    import torch

    from physics.hf.core.tensors import DTYPE
    from physics.hf.omp.parameters import OMPTable

    out = {}
    for t in d.tables:
        if (t.Z, t.A) == (int(Z), int(A)):
            out[t.k] = (OMPTable(torch.tensor(t.e, dtype=DTYPE), torch.tensor(t.rows, dtype=DTYPE)), t.ef)
    return out


def local_file(Z: int, k: int) -> str | None:
    """The `optmodfilen` / `optmodfilep` file for element Z (k = 1, 2), or None (omppar.f90:52-63).

    TALYS: omppar.f90:1 (omppar)
    Test: tests/hf/test_kwcov_b6.py
    """
    d = active()
    if d is None or not d.files:
        return None
    for z, kk, p in d.files:
        if (z, kk) == (int(Z), int(k)):
            return p
    return None


def has_bumps(k: int) -> bool:
    """Any energy-local adjustment line for particle type k in the active run.

    TALYS: ompadjust.f90:1 (ompadjust)
    Test: tests/hf/test_kwcov_b6.py
    """
    d = active()
    return d is not None and any(b.k == k for b in d.bumps)


def _factor(bumps, e: np.ndarray) -> np.ndarray:
    """adjust.f90 over the lines of one keyword and particle, in input order: the last one that covers E wins.

    TALYS: ompadjust.f90:1 (ompadjust)
    Test: tests/hf/test_kwcov_b6.py
    """
    f = np.ones_like(e)
    for b in bumps:
        if b.kind == "tab":
            es, ds = (np.asarray(x, dtype=np.float64) for x in b.args)
            inside = (e >= es[0]) & (e <= es[-1])
            if len(es) == 1:
                val = np.full_like(e, ds[0])
            else:
                # locate(Eadj, 1, N, E, nen) then pol1 between nen and nen+1 (E == Eadj(N) -> the last segment)
                j = np.clip(np.searchsorted(es, e, side="right") - 1, 0, len(es) - 2)
                val = ds[j] + (ds[j + 1] - ds[j]) * (e - es[j]) / (es[j + 1] - es[j])
            f = np.where(inside, val, f)
        else:
            ea, eb, em, d = b.args
            npow = 4
            db = (d - 1.0) * (1.0 + 0.5**npow)
            inside = (e > ea) & (e < eb)
            c1 = ea + 0.5 * (em - ea)
            c2 = em + 0.5 * (eb - em)
            with np.errstate(all="ignore"):
                x1 = (e - ea) ** npow
                lo = 1.0 + db * x1 / (x1 + (c1 - ea) ** npow)
                x2 = (eb - e) ** npow
                hi = 1.0 + db * x2 / (x2 + (c2 - eb) ** npow)
            f = np.where(inside, np.where(e <= em, lo, hi), f)
    return f


def factors(F: dict, ktype: int, e) -> dict:
    """`F` with the energy-local factors of particle type `ktype` at the potential's energies `e`
    (`Fv1 = factor * v1adjust(k)`); `F` itself when there are none.

    TALYS: ompadjust.f90:1 (ompadjust), adjust.f90:1 (adjust)
    Test: tests/hf/test_kwcov_b6.py
    """
    d = active()
    if d is None or not d.bumps:
        return F
    mine = [b for b in d.bumps if b.k == ktype]
    if not mine:
        return F
    import torch

    from physics.hf.core.tensors import DTYPE
    from physics.hf.omp.parameters import _ADJ

    et = torch.as_tensor(e, dtype=DTYPE)
    en = et.detach().reshape(-1).numpy().astype(np.float64)
    out = dict(F)
    for f, key in _ADJ.items():
        bs = [b for b in mine if b.key == key]
        if bs:
            fac = torch.as_tensor(_factor(bs, en).reshape(tuple(et.shape)), dtype=DTYPE)
            out[f] = F[f] * fac
    return out


# --------------------------------------------------------------------------- the projectile as an ejectile
_EJECTILE_ATTR = "_kwcov_b6_ejectile"


def mark_ejectile(params, k0: int):
    """Tag a `Params` built by `ejectile_params` (the outgoing channels' view), so `ktype` can tell the projectile
    leaving (type 0) from the incident channel.

    TALYS: opticalnp.f90:1 (opticalnp) -- flagompejec
    Test: tests/hf/test_kwcov_b6.py
    """
    setattr(params, _EJECTILE_ATTR, int(k0))
    return params


def ktype(params, k: int, options) -> int:
    """The particle type whose factors the potential of particle k takes (opticalnp.f90:175, opticalcomp.f90:162).

    TALYS: opticalnp.f90:1 (opticalnp)
    Test: tests/hf/test_kwcov_b6.py
    """
    k0 = getattr(params, _EJECTILE_ATTR, None)
    return 0 if (k0 is not None and k == k0) else k


def token() -> tuple:
    """TALYS: (none -- cache keys)

    Test: tests/hf/test_kwcov_b6.py
    """
    d = active()
    return (d,) if d is not None else ()


__all__ = ["ADJUSTF", "OMPADJ", "OMPDeck", "TBump", "Table", "active", "drop_bumps", "extract", "factors", "has_bumps",
           "ktype", "local_file", "mark_ejectile", "on", "range_cells", "read_adjust_table", "read_table", "resolve",
           "tables", "token"]
