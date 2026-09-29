"""WP-24: fission observables read straight from ENDF-6 files -- ν̄ (MF1), PFNS (MF5), FPY (MF8).

The WP-11 build carries MF3 only, so these readers open the evaluated files directly: the
extracted trees under `staging/_extract/<lib>` where they exist, the per-material zips under
`raw/endf/<lib>/n` otherwise, and the ENDF/B-VIII.1 `nfy` sublibrary inside its tarball.

Only what the WP-24 scorers need is implemented, and each reader refuses the representations
it does not handle rather than guessing:

* `nubar(text, mt)`   MF1 MT452/455/456, LNU=1 (polynomial) or LNU=2 (tabulated) -> (E, ν)
* `pfns(text)`        MF5 MT18, LF=1 tabulated distributions -> {E_in: (E_out, p)}, and the
                      analytic LF=7 (Maxwell) / LF=11 (Watt) / LF=12 (Madland-Nix) forms
* `fpy(text, mt)`     MF8 MT454 (independent) / MT459 (cumulative) -> {E_in: {(Z,A,I): (Y, dY)}}
"""
from __future__ import annotations

import glob
import os
import io
import re
import tarfile
import zipfile
from functools import lru_cache
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
MAIN = Path(os.environ.get("INCOGNITA_MAIN", Path.home() / "nucleus"))


def _p(rel: str) -> Path:
    here = ROOT / rel
    return here if here.exists() else MAIN / rel


# ----------------------------------------------------------------------------- ENDF records
def _f(s: str) -> float:
    s = s.strip()
    if not s:
        return 0.0
    s = s.replace("D", "E").replace("d", "e")
    for i in range(1, len(s)):
        if s[i] in "+-" and s[i - 1] not in "eE ":
            s = s[:i] + "e" + s[i:]
            break
    return float(s)


def _i(s: str) -> int:
    s = s.strip()
    return int(s) if s else 0


def section(text: str, mf: int, mt: int) -> list[str]:
    out = []
    for line in text.splitlines():
        if len(line) < 75:
            continue
        if _i(line[70:72]) == mf and _i(line[72:75]) == mt:
            out.append(line)
    return out


class _Reader:
    def __init__(self, lines: list[str]):
        self.lines, self.k = lines, 0

    def cont(self):
        ln = self.lines[self.k]
        self.k += 1
        return (_f(ln[0:11]), _f(ln[11:22]), _i(ln[22:33]), _i(ln[33:44]), _i(ln[44:55]),
                _i(ln[55:66]))

    def values(self, n: int) -> np.ndarray:
        vals: list[float] = []
        while len(vals) < n:
            ln = self.lines[self.k]
            self.k += 1
            for j in range(6):
                if len(vals) < n:
                    vals.append(_f(ln[11 * j:11 * (j + 1)]))
        return np.asarray(vals)

    def list_(self):
        c1, c2, l1, l2, npl, n2 = self.cont()
        return (c1, c2, l1, l2, n2), self.values(npl)

    def tab1(self):
        c1, c2, l1, l2, nr, np_ = self.cont()
        _interp = self.values(2 * nr)
        xy = self.values(2 * np_)
        return (c1, c2, l1, l2), xy[0::2], xy[1::2]

    def tab2(self):
        c1, c2, l1, l2, nr, nz = self.cont()
        self.values(2 * nr)
        return (c1, c2, l1, l2), nz


# ----------------------------------------------------------------------------- locating files
ELEM = ("n H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn Ga "
        "Ge As Se Br Kr Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce Pr Nd Pm "
        "Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf Ta W Re Os Ir Pt Au Hg Tl Pb Bi Po At Rn Fr Ra Ac Th Pa "
        "U Np Pu Am Cm Bk Cf Es Fm").split()


@lru_cache(maxsize=None)
def _cendl_index() -> dict[tuple[int, int], Path]:
    out = {}
    for f in sorted(glob.glob(str(_p("staging/_extract/cendl32/mats") / "*.endf"))):
        with open(f, errors="replace") as fh:
            fh.readline()
            ln = fh.readline()
        za = int(_f(ln[0:11]))
        out.setdefault((za // 1000, za % 1000), Path(f))
    return out


def endf_text(lib: str, z: int, a: int) -> str | None:
    """The ground-state neutron sublibrary file of (Z, A) in `lib`, or None."""
    sym = ELEM[z]
    try:
        if lib == "endfb81":
            f = _p("staging/_extract/endfb81") / f"n-{z:03d}_{sym}_{a:03d}.endf"
            return f.read_text(errors="replace") if f.exists() else None
        if lib == "jeff33":
            f = _p("staging/_extract/jeff33") / f"{z}-{sym}-{a}g.jeff33"
            return f.read_text(errors="replace") if f.exists() else None
        if lib == "jendl5":
            f = _p("staging/_extract/jendl5") / f"n_{z:03d}-{sym}-{a:03d}.dat"
            return f.read_text(errors="replace") if f.exists() else None
        if lib == "cendl32":
            f = _cendl_index().get((z, a))
            return f.read_text(errors="replace") if f else None
        if lib == "tendl2025":
            fs = glob.glob(str(_p("raw/endf/tendl2025/n") / f"n_{z:03d}-{sym}-{a}_*.zip"))
        elif lib == "endfb71":
            fs = glob.glob(str(_p("raw/endf/endfb71/n") / f"n_*_{z}-{sym}-{a}.zip"))
        else:
            raise KeyError(lib)
        if not fs:
            return None
        with zipfile.ZipFile(fs[0]) as zf:
            name = [n for n in zf.namelist() if not n.endswith("/")][0]
            return zf.read(name).decode("latin-1")
    except (OSError, KeyError, zipfile.BadZipFile):
        return None


# ----------------------------------------------------------------------------- ν̄
def nubar(text: str, mt: int = 456) -> tuple[np.ndarray, np.ndarray] | None:
    lines = section(text, 1, mt)
    if not lines:
        return None
    r = _Reader(lines)
    _za, _awr, ldg, lnu, _, _ = r.cont()
    if mt == 455:
        if ldg == 0:
            r.list_()                          # decay constants
        else:
            return None                        # energy-dependent group constants: not needed
    if lnu == 1:
        _h, c = r.list_()
        e = np.logspace(-5, np.log10(2e7), 400)
        return e, np.polyval(c[::-1], e)
    if lnu == 2:
        _h, e, v = r.tab1()
        return e, v
    return None


# ----------------------------------------------------------------------------- PFNS
def pfns(text: str) -> dict[float, tuple[np.ndarray, np.ndarray]] | None:
    """MF5 MT18 as normalised spectra per incident energy (probability per eV)."""
    lines = section(text, 5, 18)
    if not lines:
        return None
    r = _Reader(lines)
    _za, _awr, _, _, nk, _ = r.cont()
    out: dict[float, tuple[np.ndarray, np.ndarray]] = {}
    for _k in range(nk):
        (_u, _0, _l, lf), pe, pv = r.tab1()
        if lf == 1:
            (_c1, _c2, _l1, _l2), ne = r.tab2()
            for _j in range(ne):
                (_t, ein, _a, _b), eo, p = r.tab1()
                out[float(ein)] = (eo, p)
        elif lf in (7, 9, 11, 12):
            return {"_analytic_lf": lf}  # type: ignore[dict-item]
        else:
            return None
        if nk > 1:
            return None                          # several partial distributions: not needed
    return out


# ----------------------------------------------------------------------------- FPY
@lru_cache(maxsize=None)
def _nfy_members() -> dict[str, str]:
    """name -> text of every nfy file, read in ONE pass over the 1 GB tarball (a gzip tar has
    no index, so opening it per system re-decompresses everything before the member)."""
    tf = _p("raw/endf/endfb81/ENDF-B-VIII.1.tar.gz")
    out = {}
    with tarfile.open(tf, "r|gz") as t:
        for m in t:
            if "/nfy-" in m.name and m.isfile():
                out[Path(m.name).name] = t.extractfile(m).read().decode("latin-1")
    return out


def nfy_text(z: int, a: int) -> str | None:
    sym = ELEM[z]
    pat = re.compile(rf"nfy-0*{z}_{sym}_0*{a}\.endf$", re.I)
    for base, text in _nfy_members().items():
        if pat.search(base):
            return text
    return None


def nfy_systems() -> list[tuple[int, int]]:
    out = []
    for base in _nfy_members():
        m = re.search(r"nfy-0*(\d+)_([A-Za-z]+)_0*(\d+)(m\d)?\.endf$", base)
        if m and not m.group(4):
            out.append((int(m.group(1)), int(m.group(3))))
    return sorted(out)


def fpy(text: str, mt: int = 459) -> dict[float, dict[tuple[int, int, int], tuple[float, float]]]:
    lines = section(text, 8, mt)
    if not lines:
        return {}
    r = _Reader(lines)
    _za, _awr, le1, _, _, _ = r.cont()
    out = {}
    for _ in range(le1):
        (ein, _c2, _i1, _l2, nfp), v = r.list_()
        d = {}
        for j in range(nfp):
            zafp, fps, y, dy = v[4 * j:4 * j + 4]
            zafp = int(round(zafp))
            d[(zafp // 1000, zafp % 1000, int(round(fps)))] = (float(y), float(dy))
        out[float(ein)] = d
    return out


def mass_yield(d: dict[tuple[int, int, int], tuple[float, float]]) -> dict[int, float]:
    m: dict[int, float] = {}
    for (_z, a, _i), (y, _dy) in d.items():
        m[a] = m.get(a, 0.0) + y
    return m


__all__ = ["endf_text", "fpy", "mass_yield", "nfy_systems", "nfy_text", "nubar", "pfns",
           "section", "io"]
