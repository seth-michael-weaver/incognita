"""BESTFIT: TENDL's own per-nuclide knobs -- `best y` and the fitted parameter libraries
(`fit y` / `ngfit y` / `macsfit y` / `gamgamfit y`) -- read from TALYS's own structure database
and applied to the run, exactly as TALYS applies them.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T3 (physics/hf/CONTRACT.md §7, the input layer this extends). Acceptance test: A-omppar
(§6) plus the BESTFIT gates in docs/results/bestfit.md.

TALYS routines ported here (file:line of the subroutine statement):
    initial_best.f90:1 (initial_best)   the `best/<El><AAA>/<p>-<El><AAA>.talys` file and where
                                        its lines go in the input (before the user's, so the
                                        user's win, unless `bestend y`)
    input_fit.f90:1 (input_fit)         which fitted library each `*fit` flag selects
    xsfit.f90:1 (xsfit)                 `best/fits/<reaction>.par`: pick the entry matching
                                        (projectile, element, mass, Ltarget, ldmodel,
                                        colenhance, strength / alphaomp / fismodel) and apply
                                        its keyword lines ON TOP of everything else

Why this module exists
----------------------
TENDL-2025's capture recipe for a nuclide with data is: `best y` (which sets `ldmodel`, usually
7, and asks for `fit y`) plus the one fitted E1 width `wtable Z A+1 <value> e1` that `ng.par`
holds for that nuclide and model combination. The port parsed `best` into a flag and never read
either file, so every "stock TALYS" comparison of 2026-09-19 ran without TENDL's knobs.

Default OFF. `INCOGNITA_TALYS_FIT` selects the arm, as a comma/plus separated list of:

    best      read `structure/best/<Nuc>/n-<Nuc>.talys` and apply its keywords; if that file
              itself says `fit y` / `ngfit y` (TENDL's own recipe), the matching `ng.par` entry
              is applied too
    ng        force `ngfit y`   (`best/fits/ng.par`)
    macs      force `macsfit y` (`best/fits/macs.par`)
    gamgam    force `gamgamfit y` (`best/fits/gamgam.par`)
    s8        `strength 8` (Gogny D1M+QRPA), which is what TENDL-2025 was built with: 221 of
              the 240 `wtable` values in TENDL-2025's own MF1 blocks (Z 26-92) are the
              strength-8 entry of `ng.par` at that nuclide's `ldmodel`, and only 1 is the
              strength-9 one. TALYS-2.2 defaults to `strength 9` (input_densitymodel.f90:89)
    tendl     TENDL-2025's recipe: `best` + `s8`, and `ng.par` only where the best file
              itself asks for it (`fit y` / `ngfit y`), which is what TENDL ran
    nodata    TENDL's no-data recipe: no best file, no fitted entry, but `strength 8` and
              `globalwtable y` (TALYS's chart-wide constant) -- what TENDL ships for a nuclide
              it never fitted

Unset (or `0`/`off`/`none`) leaves every number exactly as it was: CHART1 stays 0.99750.

How it reaches the four paths
-----------------------------
One run has one target, and TALYS's keywords are in ABSOLUTE nuclide coordinates
(`wtable 26 57 ...` is the compound nucleus of n + Fe-56). `activate(Z, A)` records the run's
target; `default_options` then resolves the run's switches with the best file's global keywords
underneath the caller's, and `default_params` writes the per-nucleus cells into the `Params` of
whatever nucleus of that run is being built. Every path -- Python, C, fast, GPU -- builds its
level densities and photon strengths from those two objects, so all four see the same knobs.

Test: tests/hf/test_fitlib.py
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

PARSYM = ("g", "n", "p", "d", "t", "h", "a")  # constants.f90:89

ENV = "INCOGNITA_TALYS_FIT"
#: ad-hoc keyword lines, ';' separated, applied as if they were the target's best file
ENV_LINES = "INCOGNITA_TALYS_FIT_LINES"
#: CHUNKFIX: a chart-wide recipe table (one keyword line per line, or ';' separated). Each run takes the table's
#: global lines plus the per-nucleus lines of every nucleus in ITS OWN box, so a residual nucleus gets the same
#: recipe value whichever targets share the process. ENV_LINES, if also set, goes on top (later line wins).
ENV_LINES_FILE = "INCOGNITA_TALYS_FIT_LINES_FILE"
#: TENDL-2025's own "Adjusted TALYS input parameters" block, parsed by NGFIT
ENV_MF1 = "INCOGNITA_TALYS_FIT_MF1"
#: v1 (n,a) recipe (BLIND_LOOKS 09-22 NA-PICKUP / NA-V1b / HEPROD): the emission-fitted alpha
#: OMP of Avrigeanu, Hodgson & Avrigeanu (1994) and a Kalbach alpha PICKUP strength that depends
#: on the target's parity -- proton-pair pickup from an even-even target is ~3.6x stronger.
#: Confirmed on fresh EXFOR helium production: -23 % rms vs the TALYS default, -33 % for A > 70.
ENV_NA_V1 = "INCOGNITA_NA_V1"
NA_V1_ALPHAOMP = 8
NA_V1_CSTRIP = {True: 1.85, False: 0.52}  # even-even target -> cstrip a
_MF1_CSV = "<lab>/docs/shared/tendl2025_adjusted_params.csv"

#: xsfit.f90:80-101 -- fit flag -> parameter file, and the extra key each file is matched on
_FILES = {
    "nn": ("nn.par", None), "ng": ("ng.par", "strength"), "na": ("na.par", "alphaomp"),
    "nf": ("nf.par", "fismodel"), "an": ("an.par", "alphaomp"), "dn": ("dn.par", None),
    "pn": ("pn.par", None), "gn": ("gn.par", "strength"), "gamgam": ("gamgam.par", "strength"),
    "macs": ("macs.par", "strength"), "nd": ("nd.par", None),
}

#: the `*fit` switches themselves (input_fit.f90), as opposed to the values they produce
_FIT_FLAGS = frozenset({"fit", "ngfit", "nnfit", "nffit", "nafit", "ndfit", "pnfit", "gnfit",
                        "dnfit", "anfit", "macsfit", "gamgamfit"})

#: keyword lines this module knows it does NOT apply, with the reason (BESTFIT report)
_SKIP = {
    "optmod": "external OMP file", "optmodfilen": "external OMP file",
    "deformfile": "external deformation file", "levelfile": "external level file",
    "branch": "discrete branching ratios (per level)", "ntop": "not in PARAM_SPECS",
    "rescuefile": "output renormalisation, not a model parameter",
    "bestfile": "handled by activate()", "best": "flag", "bestend": "flag",
}


# ------------------------------------------------------------------------------------- the arm


def modes() -> frozenset[str]:
    """The arms `INCOGNITA_TALYS_FIT` asks for; empty when the lever is off (the default).

    TALYS: input_fit.f90:1 (input_fit) -- which fitted libraries a run reads
    Test: tests/hf/test_fitlib.py
    """
    raw = os.environ.get(ENV, "").strip().lower()
    if _na_v1_on():
        raw = (raw + ",nav1") if raw and raw not in ("0", "off", "none", "n", "no") else "nav1"
    if not raw or raw in ("0", "off", "none", "n", "no"):
        return frozenset()
    toks = {t for t in raw.replace("+", ",").replace(" ", ",").split(",") if t}
    unknown = toks - {"best", "ng", "macs", "gamgam", "nodata", "fit", "s8", "tendl", "mf1",
                      "lines", "nav1"}
    if unknown:
        raise ValueError(f"{ENV}: unknown arm(s) {sorted(unknown)}")
    if "tendl" in toks:  # TENDL's own recipe: the best file decides whether ng.par is read
        toks |= {"best", "s8"}
        toks.discard("tendl")
    if "nodata" in toks:
        toks = {"nodata", "s8"}
    if os.environ.get(ENV_LINES) or os.environ.get(ENV_LINES_FILE):
        toks = set(toks) | {"lines"}
    return frozenset(toks)


def _na_v1_on() -> bool:
    return os.environ.get(ENV_NA_V1, "").strip().lower() in ("1", "y", "yes", "on")


def na_v1_lines(Z: int, A: int) -> tuple[str, ...]:
    """The v1 (n,a) recipe as TALYS keyword lines for target (Z, A).

    TALYS: input_ompmodel.f90:1 (input_ompmodel) -- reads `alphaomp`; `cstrip` is read in input_preeqpar.f90
    Test: tests/hf/test_na_v1.py
    """
    ee = Z % 2 == 0 and (A - Z) % 2 == 0
    return (f"alphaomp {NA_V1_ALPHAOMP}", f"cstrip a {NA_V1_CSTRIP[ee]}")


def enabled() -> bool:
    """True when any arm is on, i.e. when this module may change a number.

    TALYS: input_best.f90:1 (input_best) -- `best`/`bestend`, the flags this stands in for
    Test: tests/hf/test_fitlib.py
    """
    return bool(modes())


# --------------------------------------------------------------------------------- file access


def structure_best() -> Path:
    """TALYS's `structure/best` directory (the `best` tree of the structure database).

    TALYS: initial_best.f90:1 (initial_best)
    Test: tests/hf/test_fitlib.py
    """
    from physics.hf.gamma.parameters import structure_dir

    return structure_dir() / "best"


def best_file(Z: int, A: int, projectile: str = "n", Ltarget: int = 0) -> Path:
    """`best/<El><AAA>[m]/<p>-<El><AAA>.talys`, the path initial_best.f90:70-99 builds.

    TALYS: initial_best.f90:1 (initial_best)
    Test: tests/hf/test_fitlib.py
    """
    from physics.hf.core.constants import nuclide_symbol

    sym = nuclide_symbol(int(Z))
    d = f"{sym}{int(A):03d}" + ("m" if Ltarget else "")
    return structure_best() / d / f"{projectile}-{sym}{int(A):03d}.talys"


@lru_cache(maxsize=512)
def best_lines(Z: int, A: int, projectile: str = "n", Ltarget: int = 0) -> tuple[str, ...]:
    """The best file's keyword lines, lowercased as `convert` does, comments dropped.

    TALYS: initial_best.f90:1 (initial_best)
    Test: tests/hf/test_fitlib.py
    """
    p = best_file(Z, A, projectile, Ltarget)
    if not p.is_file():
        return ()
    out = []
    for line in p.read_text(errors="replace").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        out.append(s.lower())
    return tuple(out)


@lru_cache(maxsize=16)
def _par_entries(name: str) -> dict:
    """`best/fits/<name>`, parsed once: {(element, mass, ldmodel, colenhance, extra): lines}.

    `extra` is the value of the file's own extra key (`strength`, `alphaomp` or `fismodel`);
    the first entry with a given key wins, as xsfit.f90 takes the first match and exits.
    """
    p = structure_best() / "fits" / name
    out: dict = {}
    if not p.is_file():
        return out
    cur: dict = {}
    npar = 0
    lines: list[str] = []
    it = iter(p.read_text(errors="replace").splitlines())
    for line in it:
        s = line.strip()
        if not s:
            continue
        if s.startswith("#####"):
            key = (str(cur.get("element", "")).lower(), int(cur.get("mass", -1)),
                   int(cur.get("ldmodel", -1)), str(cur.get("colenhance", "n"))[:1].lower(),
                   int(cur.get("strength", -1)), int(cur.get("alphaomp", -1)),
                   int(cur.get("fismodel", -1)), str(cur.get("projectile", "n")).strip().lower())
            out.setdefault(key, tuple(lines))
            cur, npar, lines = {}, 0, []
            continue
        if s.startswith("##parameters"):
            npar = int(s.split()[1])
            lines = [next(it).strip().lower() for _ in range(npar)]
            continue
        if s.startswith("##"):
            continue
        w = s.split()
        if len(w) >= 2 and w[0] in ("projectile", "element", "mass", "ldmodel", "colenhance",
                                    "strength", "fismodel", "alphaomp"):
            cur[w[0]] = w[1]
    return out


def par_lines(kind: str, Z: int, A: int, *, ldmodel: int, flagcol: bool, strength: int,
              alphaomp: int = 6, fismodel: int = 5, projectile: str = "n",
              Ltarget: int = 0) -> tuple[str, ...]:
    """The keyword lines of the `best/fits/<kind>.par` entry that matches this run (xsfit.f90).

    Match: element, mass, Ltarget == 0, ldmodel, colenhance (every file but `nf`), and the
    file's extra key -- `strength` for ng/gn/gamgam/macs, `alphaomp` for na/an, `fismodel` for
    nf. No match (or no file) is an empty tuple: TALYS then simply runs on its defaults.

    TALYS: xsfit.f90:1 (xsfit)
    Test: tests/hf/test_fitlib.py
    """
    from physics.hf.core.constants import nuclide_symbol

    name, extra = _FILES[kind]
    if Ltarget != 0:  # xsfit.f90:143 -- `Lt` is 0 there, so only ground-state targets match
        return ()
    ent = _par_entries(name)
    el = nuclide_symbol(int(Z)).lower()
    co = "y" if flagcol else "n"
    for key, lines in ent.items():
        if key[0] != el or key[1] != int(A) or key[2] != int(ldmodel):
            continue
        if key[7] != projectile:
            continue
        if kind != "nf" and key[3] != co:
            continue
        if extra == "strength" and key[4] != int(strength):
            continue
        if extra == "alphaomp" and key[5] != int(alphaomp):
            continue
        if extra == "fismodel" and key[6] != int(fismodel):
            continue
        return lines
    return ()


# ------------------------------------------------------------------ keyword lines -> the engine


@dataclass(frozen=True)
class Cards:
    """One run's resolved keywords: global switches, per-nucleus cells, and what was skipped."""

    Z: int
    A: int
    projectile: str
    options: tuple[tuple[str, object], ...] = ()          # for default_options(overrides=...)
    cells: tuple[tuple[str, int, int, float, tuple], ...] = ()  # (keyword, Z, A, value, idx)
    globals_: tuple[tuple[str, float], ...] = ()          # dims == () parameters
    particles: tuple[tuple[str, int, float], ...] = ()    # (keyword, particle type, value)
    skipped: tuple[tuple[str, str], ...] = ()             # (line, reason)
    source: tuple[str, ...] = ()                          # which files it came from
    eadj: tuple = ()                                      # ENGADJ energy-local bumps (physics/hf/eadj.py)

    @property
    def option_overrides(self) -> dict:
        return dict(self.options)

    def empty(self) -> bool:
        return not (self.options or self.cells or self.globals_ or self.particles or self.eadj)


def _split(lines, want_options: bool) -> tuple[list, list, list, list, list]:
    """Classify TALYS keyword lines into option / per-nucleus / global / per-particle / skipped.

    The form is read off `PARAM_SPECS[keyword].dims`, which are the Fortran bounds of the
    variable: `(Z, N)` leading axes take `keyword Z A value [extra...]` (getvalues classes 1-5),
    a single particle axis takes `keyword <p> value` (class 6), no axis takes `keyword value`.
    """
    from physics.hf.input.defaults import OPTION_KEYWORDS, PARAM_SPECS

    opts, cells, globs, parts, skipped = [], [], [], [], []
    for line in lines:
        w = line.split()
        if not w:
            continue
        k = w[0].lower()
        if k in _SKIP:
            skipped.append((line, _SKIP[k]))
            continue
        if k in OPTION_KEYWORDS:
            if len(w) == 2:
                if want_options:
                    opts.append((k, w[1]))
                continue
            skipped.append((line, "per-nucleus form of an option keyword"))
            continue
        if k in UPBEND_KEYS:  # LEESHELL fidelity fix: `upbendc Z A value [m1|e1]` (class 5, input_gammapar.f90:392-425)
            try:
                z, a, v = int(w[1]), int(w[2]), float(w[3])
                rad = (w[4] if len(w) > 4 else "e1").lower()  # getvalues.f90:179-191: no type -> irad 1, l 1
                irad = 0 if rad[:1] == "m" else 1
                lval = int(rad[1:]) if rad[:1] in "em" and len(rad) > 1 and rad[1:].isdigit() else 1
                cells.append((k, z, a, v, (irad, lval)))
            except (ValueError, IndexError):
                skipped.append((line, "could not be parsed"))
            continue
        spec = PARAM_SPECS.get(k)
        if spec is None:
            skipped.append((line, "not a TALYS keyword the port knows"))
            continue
        dims = spec.dims
        try:
            if not dims:
                globs.append((k, float(w[1])))
            elif dims[0] == (0, 14) and len(dims) >= 2:  # (Zix, Nix) leading -- class 1/2/3/5
                z, a, v = int(w[1]), int(w[2]), float(w[3])
                idx = _extra_index(k, dims, w[4:])
                if idx is None:
                    skipped.append((line, "index form not understood"))
                    continue
                cells.append((k, z, a, v, idx))
            elif len(dims) == 1 and dims[0] in ((0, 6), (-1, 6)):
                p = w[1].lower()
                if p not in PARSYM:
                    skipped.append((line, "particle symbol not understood"))
                    continue
                if len(w) > 3:  # `awdadjust n 1. awdadjust-n.table` -- an energy-dependent table
                    skipped.append((line, "energy-dependent table form"))
                    continue
                parts.append((k, PARSYM.index(p), float(w[2])))
            else:
                skipped.append((line, f"unsupported index form dims={dims}"))
        except (ValueError, IndexError):
            skipped.append((line, "could not be parsed"))
    return opts, cells, globs, parts, skipped


def _extra_index(k: str, dims, rest) -> tuple | None:
    """The trailing indices of a `keyword Z A value ...` line, beyond (Zix, Nix)."""
    n = len(dims) - 2
    if n == 0:
        return ()
    if k in _CLASS5:
        # class 5: `wtable Z A value e1`, `egr Z A value e1 [igr]` -- radiation type, multipolarity
        # and (GDR / pygmy-scissors keywords) the resonance number (getvalues.f90:179-191)
        rad = (rest[0] if rest else "e1").lower()
        irad = 1 if rad[:1] == "e" else 0
        lval = int(rad[1:]) if len(rad) > 1 and rad[1:].isdigit() else 1
        igr = int(rest[1]) if len(rest) > 1 else 1
        return (irad, lval, igr)[:n]
    # class 3: one barrier index, 0 when absent (input_densitypar / input_fissionpar)
    ibar = int(float(rest[0])) if rest else (1 if dims[2][0] == 1 else 0)
    return (ibar,) + (0,) * (n - 1)


def _resolved(Z: int, A: int, projectile: str, opts: dict):
    from physics.hf.input.defaults import default_options

    return default_options(int(Z), int(A), projectile, overrides=opts or None, _fit=False)


@lru_cache(maxsize=4)
def _mf1_blocks() -> dict:
    """TENDL-2025's MF1 "Adjusted TALYS input parameters" block per nuclide, as keyword lines."""
    import csv

    out: dict = {}
    p = Path(os.environ.get(ENV_MF1, "") or os.path.expanduser(_MF1_CSV))
    if not p.is_file():
        return out
    with open(p, newline="") as fh:
        for r in csv.DictReader(fh):
            nid = r["nuclide_id"]
            z, n, m = int(nid[1:4]), int(nid[5:8]), int(nid[9:])
            out.setdefault((z, z + n, m), []).append(
                f"{r['keyword'].strip().lower()} {r['args'].strip().lower()}".strip())
    return {k: tuple(v) for k, v in out.items()}


#: projectile -> (Z, N) it adds to the target, to find the compound nucleus (constants.f90 parZ / parN)
_PARZN = {"g": (0, 0), "n": (0, 1), "p": (1, 0), "d": (1, 1), "t": (1, 2), "h": (2, 1), "a": (2, 2)}


@lru_cache(maxsize=8)
def _lines_table(path: str, mtime_ns: int, size: int):
    """CHUNKFIX: the recipe table `ENV_LINES_FILE`, parsed once per (path, mtime, size):
    (global lines, {(Z, A): per-nucleus lines}, sha256). A per-nucleus line is one whose keyword has the (Zix, Nix)
    leading axes, i.e. the `keyword Z A value ...` form `_split` reads as a cell."""
    import hashlib

    from physics.hf.input.defaults import PARAM_SPECS

    raw = Path(path).read_bytes()
    glob: list[str] = []
    per: dict = {}
    for x in raw.decode(errors="replace").replace(";", "\n").splitlines():
        s = x.strip().lower()
        if not s or s.startswith("#"):
            continue
        w = s.split()
        spec = PARAM_SPECS.get(w[0])
        if spec is not None and spec.dims and spec.dims[0] == (0, 14) and len(spec.dims) >= 2 and len(w) >= 4:
            try:
                per.setdefault((int(w[1]), int(w[2])), []).append(s)
                continue
            except ValueError:
                pass
        glob.append(s)
    return tuple(glob), {k: tuple(v) for k, v in per.items()}, hashlib.sha256(raw).hexdigest()


def table_lines(Z: int, A: int, projectile: str = "n") -> tuple[tuple[str, ...], str]:
    """CHUNKFIX: the lines of the recipe table (`ENV_LINES_FILE`) that a run on target (Z, A) uses: the global lines
    and the per-nucleus lines of every nucleus of its box, Zix = Zc - z in 0..14 and Nix = Nc - n in 0..34 below the
    compound nucleus (Zc, Nc) (the (Zix, Nix) bounds of every per-nucleus keyword; `apply_params` would skip the
    rest anyway). Returns (lines, "lines table <path> sha256 <hex>"); ((), "") when no table is set.

    TALYS: getvalues (input_*par.f90) -- keywords in absolute coordinates, Zix = Zinit - Z
    Test: tests/hf/test_chunkfix.py
    """
    p = os.environ.get(ENV_LINES_FILE, "").strip()
    if not p:
        return (), ""
    st = os.stat(p)
    glob, per, sha = _lines_table(os.path.abspath(p), st.st_mtime_ns, st.st_size)
    dz, dn = _PARZN.get(projectile, (0, 1))
    zc, nc = int(Z) + dz, int(A) - int(Z) + dn
    out = list(glob)
    for (z, a), ls in sorted(per.items()):
        if 0 <= zc - z <= 14 and 0 <= nc - (a - z) <= 34:
            out.extend(ls)
    return tuple(out), f"lines table {os.path.abspath(p)} sha256 {sha}"


def _lines_key() -> tuple:
    """What the `lines` arm reads from the environment, so `cards` is never served from a stale cache entry."""
    p = os.environ.get(ENV_LINES_FILE, "").strip()
    st = os.stat(p) if p and os.path.exists(p) else None
    return (os.environ.get(ENV_LINES, ""), p, st.st_mtime_ns if st else 0, st.st_size if st else 0,
            os.environ.get("INCOGNITA_OMPROTOR", ""), os.environ.get("INCOGNITA_ENGADJ", ""))


def cards(Z: int, A: int, projectile: str = "n", Ltarget: int = 0,
          arms: frozenset = frozenset()) -> Cards:
    """Everything `best y` and the fitted libraries put on a run for this target (cached per environment).

    TALYS: initial_best.f90:1 (initial_best), input_fit.f90:1 (input_fit), xsfit.f90:1 (xsfit)
    Test: tests/hf/test_fitlib.py, tests/hf/test_chunkfix.py
    """
    return _cards(int(Z), int(A), projectile, Ltarget, arms or modes(), _lines_key())


@lru_cache(maxsize=256)
def _cards(Z: int, A: int, projectile: str, Ltarget: int, arms: frozenset, _key: tuple) -> Cards:
    """Everything `best y` and the fitted libraries put on a run for this target.

    TALYS: initial_best.f90:1 (initial_best), input_fit.f90:1 (input_fit), xsfit.f90:1 (xsfit)
    Test: tests/hf/test_fitlib.py
    """
    src: list[str] = []
    bl: tuple[str, ...] = ()
    if "best" in arms:
        bl = best_lines(Z, A, projectile, Ltarget)
        if bl:
            src.append(str(best_file(Z, A, projectile, Ltarget)))
    if "mf1" in arms:
        # TENDL-2025's own block already contains the VALUES its `fit y` produced (its
        # adjust.dat is echoed into MF1), so the fit switches are dropped: keeping them would
        # let today's ng.par overwrite the values TENDL actually shipped. `mf1,ng` keeps both.
        blk = tuple(l for l in _mf1_blocks().get((Z, A, Ltarget), ())
                    if l.split()[0] not in _FIT_FLAGS)
        if blk:
            bl = bl + blk
            src.append(f"MF1[{Z},{A}]")
    if "nav1" in arms:  # before the ad-hoc lines, so an explicit line still wins (last one does)
        bl = bl + na_v1_lines(Z, A)
        src.append("NA_V1")
    if "lines" in arms:
        tl, tsrc = table_lines(Z, A, projectile)
        if tl:
            bl = bl + tl
            src.append(tsrc)
        extra = tuple(x.strip().lower() for x in os.environ.get(ENV_LINES, "").split(";")
                      if x.strip())
        if extra:
            bl = bl + extra
            src.append("ENV lines")
    ead: list = []
    if any(x.split()[:1] == ["eadj"] for x in bl):  # ENGADJ: `eadj ...` lines are the engine's own, not TALYS keywords
        from physics.hf import eadj as _eadj

        keep = []
        for x in bl:
            if x.split()[:1] != ["eadj"]:
                keep.append(x)
            elif not _eadj.disabled():
                ead.append(_eadj.parse_line(x))  # a malformed eadj line raises: a dial must not be dropped silently
        bl = tuple(keep)
    opts, cells, globs, parts, skipped = _split(bl, want_options=True)
    if "s8" in arms and not any(k == "strength" for k, _ in opts):
        opts = [("strength", 8)] + opts
    o = _resolved(Z, A, projectile, dict(opts))
    # OMPROTOR (COMBINE4, Incognita extension): the rotor CC diffuseness un-fold's per-particle cards, after the run's own lines
    # (where OMPROTOR's runs carried them as extra lines); none for OFF or a non-member target (omp/omprotor.py)
    from physics.hf.omp import omprotor

    if projectile == "n":
        rot = omprotor.lines(Z, A, omprotor.mode(o))
        if rot:
            _, c3, g3, p3, s3 = _split(rot, want_options=False)
            cells, globs, parts, skipped = cells + c3, globs + g3, parts + p3, skipped + s3
            src.append("omprotor " + omprotor.mode(o))
    # input_fit.f90:54-63: `fit y` turns on EVERY (n,x) fitted library, not only (n,g); xsfit.f90
    # then walks them in this order, so a later file's value wins. `ngfit y` on its own leaves
    # the others off (their defaults are read before the keyword loop, when flagfit is still n).
    flags = {"nn": o.flagnnfit, "ng": o.flagngfit, "na": o.flagnafit, "nf": o.flagnffit,
             "nd": o.flagndfit, "gamgam": o.flaggamgamfit, "macs": o.flagmacsfit}
    if not ("best" in arms or "mf1" in arms or "lines" in arms):
        flags = dict.fromkeys(flags, False)   # nothing asked for the fits; the arms below do
    for arm_kind in ("ng", "macs", "gamgam"):
        if arm_kind in arms:
            flags[arm_kind] = True
            if arm_kind != "ng":     # macsfit y / gamgamfit y turn ngfit off (input_fit.f90:175)
                flags["ng"] = False
    if "fit" in arms:
        flags.update({"nn": True, "ng": True, "na": True, "nf": True, "nd": True})
    kinds = [k for k in ("nn", "ng", "na", "nf", "gamgam", "macs", "nd") if flags.get(k)]
    for kind in kinds:
        # xsfit.f90:145 matches on `ldmodel(0, 0)`, the INITIAL COMPOUND NUCLEUS's level density
        # model -- `ldmodelCN` when the input sets it (input_densitymodel.f90:245-252), which is
        # not `ldmodelall`: Fe-56's best file says `ldmodel 2` and `ldmodelCN 1`, and TENDL's own
        # adjust.dat then carries the ldmodel-1 entry of ng.par.
        lines = par_lines(kind, Z, A, ldmodel=o.ldmodelCN, flagcol=o.flagcolall,
                          strength=o.strength, alphaomp=o.alphaomp, fismodel=o.fismodel,
                          projectile=projectile, Ltarget=Ltarget)
        if not lines:
            continue
        src.append(f"{_FILES[kind][0]}[ldmodel {o.ldmodelCN} colenhance "
                   f"{'y' if o.flagcolall else 'n'} strength {o.strength}]")
        # xsfit runs after the input is read, so its values overwrite the best file's
        _, c2, g2, p2, s2 = _split(lines, want_options=False)
        cells, globs, parts = cells + c2, globs + g2, parts + p2
        skipped = skipped + s2
    return Cards(Z, A, projectile, tuple(opts), tuple(cells), tuple(globs), tuple(parts),
                 tuple(skipped), tuple(src), tuple(ead))


# ------------------------------------------------------------------------- the run's active set

_ACTIVE: Cards | None = None


def active() -> Cards | None:
    """The cards of the run in front of us, or None when the lever is off.

    TALYS: xsfit.f90:1 (xsfit) -- one run, one target, keywords in absolute coordinates
    Test: tests/hf/test_fitlib.py
    """
    return _ACTIVE


def activate(Z: int, A: int, projectile: str | None = None, Ltarget: int = 0) -> Cards | None:
    """Make (Z, A) the target whose `best`/fit keywords every `default_options` /
    `default_params` of this process applies. A no-op when the lever is off.

    A change of target drops the per-target caches (`chartrun.drop_target_caches`): the run's
    switches are part of what they hold.

    TALYS: initial_best.f90:1 (initial_best)
    Test: tests/hf/test_fitlib.py
    """
    global _ACTIVE
    if not enabled():
        return None
    if projectile is None:  # CPINC: the run's projectile (neutron unless INCOGNITA_CPINC)
        from physics.hf import projectile as _proj

        projectile = _proj.symbol()
    c = cards(int(Z), int(A), projectile, Ltarget, modes())
    if _ACTIVE is not None and (_ACTIVE.Z, _ACTIVE.A, _ACTIVE.projectile) == (
            int(Z), int(A), projectile) and (_ACTIVE is c or _ACTIVE == c):
        return _ACTIVE
    if _ACTIVE is not None:
        from physics.hf import chartrun

        chartrun.drop_target_caches()
    _ACTIVE = c
    return c


def current(Z: int, A: int, projectile: str | None = None, Ltarget: int = 0) -> Cards | None:
    """The cards the environment asks for NOW for (Z, A), or None when the lever is off.

    SPEEDFIX (warmrun trap): a `Cascade` records `active()` when it is built; a run on it is
    refused unless `active()` and `current(...)` are still those cards (`Cascade.check_cards`).

    TALYS: initial_best.f90:1 (initial_best)
    Test: tests/hf/test_warmguard.py
    """
    if not enabled():
        return None
    if projectile is None:  # CPINC
        from physics.hf import projectile as _proj

        projectile = _proj.symbol()
    return cards(int(Z), int(A), projectile, Ltarget, modes())


def deactivate() -> None:
    """Forget the active run's cards (and drop the caches that hold them).

    TALYS: initial_best.f90:1 (initial_best)
    Test: tests/hf/test_fitlib.py
    """
    global _ACTIVE
    if _ACTIVE is not None:
        from physics.hf import chartrun

        chartrun.drop_target_caches()
    _ACTIVE = None


def option_overrides() -> dict:
    """The active run's global keywords, to go UNDERNEATH a caller's own (initial_best.f90:113-124
    puts the best file's lines before the user's, and the later line wins).

    TALYS: initial_best.f90:1 (initial_best)
    Test: tests/hf/test_fitlib.py
    """
    c = _ACTIVE
    return c.option_overrides if c is not None else {}


#: keywords `gamma.parameters.gamma_parameters` owns (it builds them from the options, not from
#: `Params`), so they reach it through its `overrides` dict instead -- see `gamma_overrides`.
#: Value -> the `GammaParameters` field it fills (ETABLEFIX: `etable` used to arrive under its
#: keyword name, which `gamma_parameters` never reads, and the GDR / pygmy-scissors keywords and
#: every `*adjust` were not passed at all); the `*adjust` keys keep their keyword names and
#: `gamma_parameters` applies them the way gammapar/fstrength do.
GAMMA_FIELDS = {
    "etable": "etable_mev", "ftable": "ftable", "wtable": "wtable",
    "egr": "egr_mev", "ggr": "ggr_mev", "sgr": "sgr_mb",
    "epr": "epr_mev", "gpr": "gpr_mev", "spr": "tpr_mb",
    "etableadjust": "etableadjust", "ftableadjust": "ftableadjust", "wtableadjust": "wtableadjust",
    "egradjust": "egradjust", "ggradjust": "ggradjust", "sgradjust": "sgradjust",
    "epradjust": "epradjust", "gpradjust": "gpradjust", "spradjust": "spradjust",
}
#: LEESHELL fidelity fix: the per-nucleus upbend keywords (input_gammapar.f90:392-425) -> (field, last-axis slot).
#: Before, they were not PARAM_SPECS keys and landed in `Cards.skipped` ("not a TALYS keyword the port knows").
#: TALYS assigns them AFTER its defaults (a user 0 is kept), so they travel as NaN-masked arrays.
UPBEND_KEYS = {
    "upbendc": ("upbend_cards", 1), "upbende": ("upbend_cards", 2), "upbendf": ("upbend_cards", 3),
    "upbendcadjust": ("upbendadjust_cards", 1), "upbendeadjust": ("upbendadjust_cards", 2),
    "upbendfadjust": ("upbendadjust_cards", 3),
    "m1kappa": ("m1kappa_cards", 0),  # M1SHARE (Incognita extension): `m1kappa Z A k`, read only by gamma_parameters
}
GAMMA_KEYS = tuple(GAMMA_FIELDS) + tuple(UPBEND_KEYS)
#: the getvalues class-5 keywords among them: (irad, l) and, for the resonance ones, igr
_CLASS5 = frozenset(GAMMA_FIELDS)


def gamma_overrides(Z: int, A: int, gammax: int) -> dict | None:
    """The active run's `ftable` / `etable` / `wtable` cells at nucleus (Z, A), in the (2, gammax+1)
    form `gamma_parameters(overrides=...)` takes (zero = keep the default).

    TALYS: input_gammapar.f90:313-326 (the keyword writes wtable(Zix, Nix, irad, l)), gammapar.f90
    Test: tests/hf/test_fitlib.py
    """
    c = _ACTIVE
    if c is None:
        return None
    import numpy as np

    from physics.hf.input.defaults import PARAM_SPECS

    out: dict = {}
    for k, z, a, v, idx in c.cells:
        if k not in GAMMA_KEYS or (int(z), int(a)) != (int(Z), int(A)):
            continue
        irad, lval, igr = (tuple(idx) + (1, 1, 1))[:3]
        if not (0 <= irad <= 1 and 1 <= lval <= int(gammax)):
            continue
        if k in UPBEND_KEYS:
            fld, slot = UPBEND_KEYS[k]
            arr = out.setdefault(fld, np.full((2, int(gammax) + 1, 4), np.nan))
            arr[irad, lval, slot] = float(v)
            continue
        if len(PARAM_SPECS[k].dims) == 5:  # egr/ggr/sgr/epr/gpr/spr (+adjust): (2, gammax+1, 3)
            if not 1 <= igr <= 2:
                continue
            arr = out.setdefault(GAMMA_FIELDS[k], np.zeros((2, int(gammax) + 1, 3)))
            arr[irad, lval, igr] = float(v)
        else:
            arr = out.setdefault(GAMMA_FIELDS[k], np.zeros((2, int(gammax) + 1)))
            arr[irad, lval] = float(v)
    return out or None


_PLANS: dict = {}


def _write_plan(c: Cards, zinit: int, ninit: int):
    """SPEEDFIX lever 3: `apply_params`'s writes for cards `c` on a run with target (Zinit, Ninit), resolved once (it was
    re-derived from all ~1,300 cells on each of ~20 calls per run). Cells: per keyword, the storage positions that land
    in the run's box as index tensors and their values, a position written twice keeping its LAST value (the serial
    loop's result); then the globals and the per-particle cells, in card order, as before.

    TALYS: xsfit.f90:1 (xsfit)
    Test: tests/hf/test_fitlib.py
    """
    import torch

    from physics.hf.input.defaults import PARAM_SPECS

    key = (id(c), zinit, ninit)
    got = _PLANS.get(key)
    if got is not None and got[0] is c:
        return got[1]
    per: dict[str, dict] = {}
    for k, z, a, v, idx in c.cells:
        if k in UPBEND_KEYS:  # LEESHELL: reach gamma_parameters only (gamma_overrides)
            continue
        spec = PARAM_SPECS[k]
        offs = spec.offsets
        zix, nix = zinit - int(z), ninit - (int(a) - int(z))
        (zlo, zhi), (nlo, nhi) = spec.dims[0], spec.dims[1]
        if not (zlo <= zix <= zhi and nlo <= nix <= nhi):
            continue
        pos = [zix + offs[0], nix + offs[1]]
        ok = True
        for i, (lo, hi), off in zip(idx, spec.dims[2:], offs[2:], strict=True):
            if not lo <= i <= hi:
                ok = False
                break
            pos.append(i + off)
        if ok:
            per.setdefault(k, {})[tuple(pos)] = float(v)
    cells = []
    for k, d in per.items():
        cols = tuple(torch.tensor(ax, dtype=torch.long) for ax in zip(*d.keys()))
        cells.append((k, cols, list(d.values())))
    globs = [(k, float(v)) for k, v in c.globals_]
    parts = []
    for k, p, v in c.particles:
        spec = PARAM_SPECS[k]
        lo, hi = spec.dims[0]
        if lo <= p <= hi:
            parts.append((k, p + spec.offsets[0], float(v)))
    plan = (cells, globs, parts)
    if len(_PLANS) > 64:
        _PLANS.clear()
    _PLANS[key] = (c, plan)
    return plan


def apply_params(Z: int, A: int, options, params):
    """`params` with the active run's per-nucleus / per-particle / global cells written in.

    The cells are in absolute nuclide coordinates, converted to this run's (Zix, Nix) the way
    `getvalues` does (`Zix = Zinit - Z`); a nucleus outside the run's box is skipped, as TALYS
    skips it. Returns `params` itself when nothing lands, so the default path keeps its object;
    otherwise a shallow copy that shares every tensor it does not write.

    TALYS: xsfit.f90:1 (xsfit)
    Test: tests/hf/test_fitlib.py
    """
    c = _ACTIVE
    if c is None or c.empty():
        return params
    import torch

    from physics.hf.input.defaults import Params

    new: dict = {}

    def _t(k):
        t = new.get(k)
        if t is None:
            t = new[k] = params.values[k].clone()
        return t

    cells, globs, parts = _write_plan(c, int(options.Zinit), int(options.Ninit))
    for k, pos, vals in cells:
        t = _t(k)
        t[pos] = torch.tensor(vals, dtype=t.dtype)
    for k, v in globs:
        _t(k)[...] = v
    for k, i, v in parts:
        _t(k)[i] = v
    return Params({**params.values, **new}) if new else params


__all__ = ["ENV", "ENV_LINES", "ENV_LINES_FILE", "Cards", "activate", "active", "apply_params", "best_file", "best_lines",
           "cards", "current", "deactivate", "enabled", "modes", "option_overrides", "par_lines", "table_lines"]
