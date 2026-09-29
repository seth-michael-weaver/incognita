"""Thin subprocess wrapper around the TALYS nuclear reaction code.

TALYS (https://github.com/arjankoning1/talys, MIT) is built from source into
``$TALYS_DIR``, default ``~/opt/talys-src`` (see ``docs/talys-install.md``).  This module
writes a TALYS input file, runs the binary in an isolated working directory,
and parses the YANDF-format ``*.tot`` cross-section tables back into numpy
arrays keyed by channel name.

Dependencies: stdlib + numpy only.

Environment overrides
---------------------
TALYS_BIN   path to the ``talys`` executable (default: ``TALYS_BIN`` below)
TALYS_DIR   TALYS install root containing ``structure/``.  If unset we derive
            it as the parent of the binary's ``bin/`` directory, which is what
            the stock installer produces.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------
# Locations
# ---------------------------------------------------------------------------

DEFAULT_TALYS_BIN = os.path.join(os.environ.get("TALYS_DIR", os.path.expanduser("~/opt/talys-src")), "bin", "talys")
TALYS_BIN = os.environ.get("TALYS_BIN", DEFAULT_TALYS_BIN)


def talys_binary() -> Path:
    """Resolve the TALYS executable.

    ``TALYS_BIN`` wins, then ``$TALYS_DIR/bin/talys``, then anything named ``talys`` on PATH,
    then the module default. The default is one machine's absolute Linux path, so on the Mac
    -- where the install root is ``~/opt/talys-src`` -- setting ``TALYS_DIR``
    alone left the sweep reporting "TALYS binary not available" with a working binary sitting
    next to the structure database it had just been pointed at.
    """
    env = os.environ.get("TALYS_BIN")
    if env:
        return Path(env)
    tdir = os.environ.get("TALYS_DIR")
    if tdir:
        cand = Path(tdir) / "bin" / "talys"
        if cand.is_file():
            return cand
    which = shutil.which("talys")
    if which:
        return Path(which)
    return Path(TALYS_BIN)


def talys_dir() -> Path:
    """Resolve the TALYS install root that holds ``structure/``."""
    env = os.environ.get("TALYS_DIR")
    if env:
        return Path(env)
    return talys_binary().resolve().parent.parent


def talys_available() -> bool:
    b = talys_binary()
    return b.is_file() and os.access(b, os.X_OK)


# ---------------------------------------------------------------------------
# Element symbols (Z = 1..118), needed for the ``element`` keyword.
# ---------------------------------------------------------------------------

_SYMBOLS = (
    "H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn "
    "Ga Ge As Se Br Kr Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce "
    "Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf Ta W Re Os Ir Pt Au Hg Tl Pb Bi Po At Rn "
    "Fr Ra Ac Th Pa U Np Pu Am Cm Bk Cf Es Fm Md No Lr Rf Db Sg Bh Hs Mt Ds Rg Cn Nh Fl "
    "Mc Lv Ts Og"
).split()


def element_symbol(Z: int) -> str:
    if not 1 <= Z <= len(_SYMBOLS):
        raise ValueError(f"Z={Z} out of range 1..{len(_SYMBOLS)}")
    return _SYMBOLS[Z - 1]


# ---------------------------------------------------------------------------
# Channel naming
#
# TALYS exclusive channel files are named ``xs<n><p><d><t><h><a>.tot`` where
# each digit is the multiplicity of that ejectile.  ``total.tot``,
# ``elastic.tot``, ``nonelastic.tot`` and ``reaction.tot`` are written when
# ``filetotal y`` / ``fileelastic y`` are set.
# ---------------------------------------------------------------------------

CHANNEL_FILES: dict[str, str] = {
    "total": "total.tot",
    "elastic": "elastic.tot",
    "nonelastic": "nonelastic.tot",
    "reaction": "reaction.tot",
    # WP-24 needs this and the Phase-1 sweeps never captured it: TALYS writes the fission
    # cross section to its own file, and it only appears when `fission y` is in the input.
    "fission": "fission.tot",  # (n,f)        MT 18
    "capture": "xs000000.tot",  # (n,g)      MT 102
    "inelastic": "xs100000.tot",  # (n,n')    MT 4
    "n2n": "xs200000.tot",  # (n,2n)         MT 16
    "n3n": "xs300000.tot",  # (n,3n)         MT 17
    "np": "xs010000.tot",  # (n,p)           MT 103
    "nd": "xs001000.tot",  # (n,d)           MT 104
    "nt": "xs000100.tot",  # (n,t)           MT 105
    "nh": "xs000010.tot",  # (n,3He)         MT 106
    "na": "xs000001.tot",  # (n,a)           MT 107
    "nnp": "xs110000.tot",  # (n,np)         MT 28
    "nna": "xs100001.tot",  # (n,na)         MT 22
    "n2np": "xs210000.tot",  # (n,2np)       MT 41
}

# Aliases accepted by ``result["channels"]`` lookups.
CHANNEL_ALIASES: dict[str, str] = {
    "(n,tot)": "total",
    "(n,el)": "elastic",
    "(n,non)": "nonelastic",
    "(n,g)": "capture",
    "(n,gamma)": "capture",
    "ng": "capture",
    "(n,n')": "inelastic",
    "nn'": "inelastic",
    "(n,2n)": "n2n",
    "(n,3n)": "n3n",
    "(n,p)": "np",
    "(n,d)": "nd",
    "(n,t)": "nt",
    "(n,h)": "nh",
    "(n,a)": "na",
    "(n,alpha)": "na",
}


class TalysError(RuntimeError):
    """Raised when the TALYS binary is missing, times out, or exits non-zero."""


# ---------------------------------------------------------------------------
# YANDF table parser
# ---------------------------------------------------------------------------


def parse_yandf(path: Path) -> dict:
    """Parse a TALYS YANDF-0.x ``*.tot`` file.

    Returns ``{"meta": {...}, "columns": [...], "units": [...],
    "data": ndarray(n, ncol)}``.  ``meta`` holds flattened header keys such as
    ``title``, ``type`` (reaction string), ``ENDF_MT``, ``Q-value [MeV]``,
    ``E-threshold [MeV]``.  ``data`` is empty (0, ncol) when the file has no
    numeric rows.
    """
    meta: dict[str, str] = {}
    columns: list[str] = []
    units: list[str] = []
    rows: list[list[float]] = []
    with open(path) as fh:
        for line in fh:
            s = line.rstrip("\n")
            if s.startswith("##"):
                toks = s[2:].split()
                if not toks:
                    continue
                if toks[0].startswith("["):
                    units = toks
                else:
                    columns = toks
            elif s.startswith("#"):
                body = s[1:].strip()
                if ":" in body:
                    k, _, v = body.partition(":")
                    k, v = k.strip(), v.strip()
                    if v and k not in meta:
                        meta[k] = v
            else:
                toks = s.split()
                if not toks:
                    continue
                try:
                    rows.append([float(t) for t in toks])
                except ValueError:
                    continue
    ncol = len(columns) if columns else (len(rows[0]) if rows else 2)
    data = np.array(rows, dtype=float) if rows else np.zeros((0, ncol))
    return {"meta": meta, "columns": columns, "units": units, "data": data}


def _channel_record(parsed: dict, filename: str) -> dict:
    d = parsed["data"]
    cols = parsed["columns"]
    E = d[:, 0] if d.size else np.zeros(0)
    # ``xs`` column is the second one for every TALYS xs table; ``all.tot``
    # style multi-column tables are handled by callers via ``columns``.
    xs = d[:, 1] if d.size and d.shape[1] > 1 else np.zeros(0)
    rec = {
        "E": E,  # MeV
        "xs": xs,  # mb
        "file": filename,
        "reaction": parsed["meta"].get("type"),
        "title": parsed["meta"].get("title"),
        "columns": cols,
        "data": d,
    }
    mt = parsed["meta"].get("ENDF_MT")
    if mt is not None:
        try:
            rec["MT"] = int(mt)
        except ValueError:
            rec["MT"] = mt
    for key in ("Q-value [MeV]", "E-threshold [MeV]"):
        if key in parsed["meta"]:
            try:
                rec[key.split()[0].replace("-", "_")] = float(parsed["meta"][key])
            except ValueError:
                pass
    return rec


# ---------------------------------------------------------------------------
# Input file writer
# ---------------------------------------------------------------------------

DEFAULT_KEYWORDS: dict[str, str] = {
    # write exclusive channel files (xs*.tot) and total/elastic tables
    "channels": "y",
    "filechannels": "y",
    "filetotal": "y",
    "fileelastic": "y",
    # keep the main output modest
    "outbasic": "n",
}


# (Z, A) a projectile adds to the target: the compound nucleus radwidtheory.f90 normalises
_PROJECTILE_ZA = {"g": (0, 0), "n": (0, 1), "p": (1, 1), "d": (1, 2), "t": (1, 3), "h": (2, 3),
                  "a": (2, 4)}


def resonance_gamgam_ev(Z: int, A: int) -> float:
    """Measured <Gamma_gamma> [eV] of (Z, A) from ``structure/resonances/<Sym>.res``, 0 if absent.

    The file's column is keV (header ``gamgam[keV]``; Au198 1.28e-4 = 0.128 eV), read with
    ``(4x, 2i4, 8es15.6, i4)`` as resonancepar.f90:79 does, L = 0 row.
    """
    path = talys_dir() / "structure" / "resonances" / f"{element_symbol(Z)}.res"
    if not path.is_file():
        return 0.0
    for line in path.read_text().splitlines():
        if line.lstrip().startswith("#") or len(line) < 16:
            continue
        try:
            ia, ell = int(line[4:8]), int(line[8:12])
            field = line[12 + 4 * 15:12 + 5 * 15].strip()
        except ValueError:
            continue
        if ia == A and ell == 0 and field:
            return float(field) * 1.0e3
    return 0.0


def _gnorm_gamgam_keyword(Z: int, A: int, kw: dict[str, str], projectile: str) -> str | None:
    """The ``gamgam Zc Ac <eV>`` line ``gnorm y`` needs, or None when TALYS gets it right anyway.

    TALYS-2.x bug (resonancepar.f90:96 / radwidtheory.f90:253-256, source banner TALYS-2.25):
    the resonance table gives Gamma_gamma in keV, resonancepar stores the number unconverted in
    ``gamgam`` (declared eV in A0_talys_mod.f90), and with ``gnorm y`` radwidtheory divides the
    E1 ftable by gamgamth/gamgam until the loop gives up -- a target 1000x too small. Output
    shows it as ``C/E Gamma_gamma: 1.546081E+03`` (I-130) / ``7.837621E+02`` (Os-187). A
    user ``gamgam`` is read in eV (input_gammapar.f90:378) and wins over the table, so giving
    the table value in eV is the workaround. ``gamgamadjust`` still multiplies it (:113).
    """
    if kw.get("gnorm", "n").strip().lower()[:1] != "y":
        return None
    dz, da = _PROJECTILE_ZA.get(projectile, (0, 1))
    Zc, Ac = Z + dz, A + da
    for k, v in kw.items():
        if k.split("#", 1)[0] == "gamgam":
            parts = v.split()
            if len(parts) >= 2 and (int(parts[0]), int(parts[1])) == (Zc, Ac):
                return None
    gg = resonance_gamgam_ev(Zc, Ac)
    return f"{Zc} {Ac} {gg:.6g}" if gg > 0.0 else None


def write_input(
    workdir: Path,
    Z: int,
    A: int,
    energies: list[float],
    extra_keywords: dict[str, str] | None = None,
    projectile: str = "n",
) -> Path:
    """Write ``talys.inp`` (and an ``energies`` file) into *workdir*.

    ``gnorm y`` without a ``gamgam`` for the compound nucleus gets one added, the tabulated
    Gamma_gamma converted from keV to eV (see `_gnorm_gamgam_keyword`: stock TALYS normalises to
    the keV number as if it were eV, 1000x too small).
    """
    energies = list(np.asarray(energies, dtype=float).ravel())   # an ndarray is falsy-ambiguous
    if not energies:
        raise ValueError("energies must be a non-empty list of MeV values")
    workdir = Path(workdir)
    workdir.mkdir(parents=True, exist_ok=True)

    kw = dict(DEFAULT_KEYWORDS)
    if extra_keywords:
        kw.update({str(k): str(v) for k, v in extra_keywords.items()})
    gg = _gnorm_gamgam_keyword(Z, A, kw, projectile)
    if gg is not None:
        kw["gamgam#gnormfix"] = gg

    lines = [
        f"projectile {projectile}",
        f"element {element_symbol(Z).lower()}",
        f"mass {A}",
    ]
    if len(energies) == 1:
        lines.append(f"energy {float(energies[0]):.6g}")
    else:
        # TALYS requires the energy file to ascend and truncates at the first descent -- with a
        # zero exit code and its usual success banner, so the run looks clean and the result is
        # short. Raise rather than sort: the caller indexes the returned arrays by the order it
        # passed in, so quietly reordering would swap a silent truncation for a silent
        # misalignment, which is worse because it survives a length check.
        e = [float(x) for x in energies]
        bad = next((i for i in range(1, len(e)) if e[i] <= e[i - 1]), None)
        if bad is not None:
            raise ValueError(
                f"TALYS energies must strictly ascend; e[{bad - 1}]={e[bad - 1]:.6g} >= "
                f"e[{bad}]={e[bad]:.6g}. TALYS would truncate here and still report success."
            )
        efile = workdir / "energies"
        efile.write_text("".join(f"{x:.6E}\n" for x in e))
        lines.append("energy energies")
    for k, v in kw.items():
        # ``key#tag`` lets callers repeat a keyword (e.g. ``aadjust`` for two
        # nuclei); the ``#tag`` suffix is dropped from the input file.
        lines.append(f"{k.split('#', 1)[0]} {v}")
    inp = workdir / "talys.inp"
    inp.write_text("\n".join(lines) + "\n")
    return inp


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------



def _fatal_talys_errors(out_text: str) -> list[str]:
    """The `TALYS-error` lines that actually stopped the calculation.

    TALYS prints `TALYS-error:` for recoverable problems too, and says so on the next lines.
    A proton on O-18 hits three of them, because the SMLO-2019 photon strength function tables
    have no O or F entry:

        TALYS-error: Error in .../structure/gamma/smlo2019/O.psf
                     IOSTAT =     -1
                     End of file
                     Continuing...

    TALYS then falls back, finishes, and writes `O18(p,n)F18` -- the exact reaction the
    medical-isotope sweep exists to compute. Treating the substring as fatal threw that run
    away and would have thrown away every light target silently, leaving a sweep that ran
    clean over a hole in its own nuclide list.

    A block is fatal unless TALYS says `Continuing...` within it.
    """
    lines = out_text.splitlines()
    fatal: list[str] = []
    for i, ln in enumerate(lines):
        if "TALYS-error" not in ln and "TALYS error" not in ln:
            continue
        window = lines[i:i + 6]
        if any("Continuing" in w for w in window):
            continue
        fatal.append(ln.strip())
    return fatal


def run_talys(
    Z: int,
    A: int,
    energies: list[float],
    extra_keywords: dict[str, str] | None = None,
    workdir: Path | None = None,
    *,
    projectile: str = "n",
    timeout: float = 600.0,
    keep_workdir: bool | None = None,
) -> dict:
    """Run TALYS for target (Z, A) at the given incident energies (MeV).

    Parameters
    ----------
    Z, A
        Target charge and mass number.
    energies
        Incident projectile energies in MeV (one or many).
    extra_keywords
        Extra ``keyword value`` pairs appended to (and overriding) the
        defaults in :data:`DEFAULT_KEYWORDS`.
    workdir
        Directory to run in.  If ``None`` a temporary directory is created
        and removed afterwards (unless ``keep_workdir=True``).
    projectile
        TALYS projectile symbol (``n``, ``p``, ``d``, ``t``, ``h``, ``a``,
        ``g``, ``0``).  Channel names below assume ``n``.
    timeout
        Seconds before the subprocess is killed (:class:`TalysError`).

    Returns
    -------
    dict with keys
        ``Z``, ``A``, ``projectile``, ``energies`` (ndarray, MeV),
        ``channels``: ``{name: {"E": ndarray, "xs": ndarray [mb], "MT": int,
        "reaction": str, "file": str, ...}}`` for every entry of
        :data:`CHANNEL_FILES` whose file was produced, plus every other
        ``xs*.tot`` file keyed by its reaction string (e.g. ``"(n,2np)"``);
        ``workdir`` (str), ``elapsed`` (s), ``returncode``, ``stdout`` (tail),
        ``talys_version`` (from the YANDF ``source:`` header).
    """
    binary = talys_binary()
    if not (binary.is_file() and os.access(binary, os.X_OK)):
        raise TalysError(f"TALYS binary not found or not executable: {binary}")

    tdir = talys_dir()
    if not (tdir / "structure" / "abundance" / "H.abun").is_file():
        raise TalysError(
            f"TALYS structure database not found under {tdir}/structure; set TALYS_DIR"
        )

    tmp_created = workdir is None
    if keep_workdir is None:
        keep_workdir = not tmp_created
    wd = Path(tempfile.mkdtemp(prefix="talys_")) if tmp_created else Path(workdir)
    wd.mkdir(parents=True, exist_ok=True)

    inp = write_input(wd, Z, A, energies, extra_keywords, projectile=projectile)

    env = dict(os.environ)
    env["TALYS_DIR"] = str(tdir)
    env.setdefault("TALYS_USER", "nucleus")

    t0 = time.perf_counter()
    try:
        with open(inp) as fin, open(wd / "talys.out", "w") as fout:
            proc = subprocess.run(
                [str(binary)],
                stdin=fin,
                stdout=fout,
                stderr=subprocess.STDOUT,
                cwd=str(wd),
                env=env,
                timeout=timeout,
                check=False,
            )
    except subprocess.TimeoutExpired as exc:
        raise TalysError(f"TALYS timed out after {timeout}s in {wd}") from exc
    elapsed = time.perf_counter() - t0

    out_text = (wd / "talys.out").read_text(errors="replace")
    fatal = _fatal_talys_errors(out_text)
    if proc.returncode != 0 or fatal:
        detail = ("\n".join(fatal) + "\n" if fatal else "") + out_text[-2000:]
        raise TalysError(f"TALYS failed (rc={proc.returncode}) in {wd}:\n{detail}")

    channels: dict[str, dict] = {}
    version = None
    for name, fname in CHANNEL_FILES.items():
        p = wd / fname
        if p.is_file():
            parsed = parse_yandf(p)
            channels[name] = _channel_record(parsed, fname)
            version = version or parsed["meta"].get("source")
    # Any additional exclusive channel files not in the friendly map.
    known = set(CHANNEL_FILES.values())
    for p in sorted(wd.glob("xs*.tot")):
        if p.name in known:
            continue
        parsed = parse_yandf(p)
        key = parsed["meta"].get("type") or p.stem
        channels[key] = _channel_record(parsed, p.name)

    result = {
        "Z": Z,
        "A": A,
        "projectile": projectile,
        "energies": np.asarray(energies, dtype=float),
        "channels": channels,
        "workdir": str(wd),
        "elapsed": elapsed,
        "returncode": proc.returncode,
        "stdout": out_text[-4000:],
        "talys_version": version,
    }

    if tmp_created and not keep_workdir:
        shutil.rmtree(wd, ignore_errors=True)
        result["workdir"] = None
    return result


def get_channel(result: dict, name: str) -> dict:
    """Look up a channel by friendly name, alias, or TALYS reaction string."""
    ch = result["channels"]
    key = CHANNEL_ALIASES.get(name, name)
    if key in ch:
        return ch[key]
    raise KeyError(f"channel {name!r} not in result; have {sorted(ch)}")


if __name__ == "__main__":  # pragma: no cover - manual smoke run
    import sys

    z, a = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (26, 56)
    es = [float(x) for x in sys.argv[3:]] or [1.0]
    r = run_talys(z, a, es)
    print(f"TALYS {r['talys_version']}  {r['elapsed']:.1f}s")
    for k, v in r["channels"].items():
        if v["xs"].size:
            print(f"{k:12s} MT={v.get('MT', '?'):>4}  xs(E0)={v['xs'][0]:.4g} mb")
