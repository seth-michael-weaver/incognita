"""Residual recoil spectra and LAB-frame emission spectra / DDX on TALYS's keywords, OUTPUT ONLY.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

What it gives (Results.recoil, TALYS's file names without the incident energy; arrays (C, ...) on the run's energies, NaN
where TALYS writes no row at that energy):

    rec<ZZZ><AAA>spec.tot          specrecoil (C, maxenrec+1) mb/MeV of residual Z, A (+ :E recoil energy MeV, :integral
                                   recoilint mb, :production = xspopnuc (+ xselasinc for the target))   recoilout.f90
    sp<nnnnnn>.rec                 exclusive recoil spectrum = specrecoil x xschannel / xspopnuc (+ :E)  channelsout.f90
    with `labddx y`:
    <x>spec.lab                    xsejlab (C, iejlab) mb/MeV, the ejectile spectrum in the LAB (+ :E, :integral)
    <x>ddx.lab                     ddxejlab (C, iejlab, nanglecont+1) mb/MeV/sr (+ :E)      ddxout.f90 talys.out tables
    <x>ddxE<eeee.e>.lab            fileddxe: LAB angular distribution at one LAB energy (C, nanglecont+1), ddxmode 1/3
    <x>ddxA<aaa.a>.lab             fileddxa: LAB spectrum at one angle (C, iejlab) (+ :E), ddxmode 2/3

Switches: `recoil y` (Options.flagrecoil; TALYS then sets outspectra y), `labddx y` (flaglabddx; anglesrec defaults to
9 with it), `recoilaverage y` (flagrecoilav: the compound recoil of a decaying bin is one average velocity),
`maxenrec`, `anglesrec`; `fileddxa` / `fileddxe` / `ddxmode` name the LAB DDX files as for the CM ones (specobs.py).
`INCOGNITA_RECOIL_DIR=<dir>` also writes the files (rec026056spec0014.000.tot, nspec0014.000.lab,
nddxE0014.000E0003.0.lab, nddxE0014.000A030.0.lab, sp100000E0014.000.rec). Default: nothing is computed and every array
engine array is unchanged (`recoil n`).

How (none of it feeds back into the engine): TALYS's recoil module on the run's `specout` records (specout.py: the binary
spectra, every cascade nucleus' mcontrib / mpecontrib with its excitation grid) and angout's discrete angular
distributions (discad of every level, angdis.f90):
    recoilinit.f90:1 (recoilinit)      angle bins, the LAB ejectile grid, the classical maximum recoil energy per
                                       residual (the 50-bin kinematic sweep), recoil grids and areas, the initial CN
    binaryrecoil.f90:1 (binaryrecoil)  binary continuum (xsbinemisad) into the LAB, normalised to binemissum
    angdisrecoil.f90:1 (angdisrecoil)  discrete levels (discad, incl. the elastic) into the LAB
    comprecoil.f90:1 (comprecoil)      every compound-emission cell of compemission.f90:1 (mother recoil distribution
                                       fracCMloc x the CM DDX compspect/(4 pi) + preeqspect Kalbach)
    cm2lab.f90, labsurface.f90, binsurface.f90   physics/hf/native/recoil.c (the same in Python: scatter_py)
    totalrecoil.f90:1, recoilout.f90:1, channelsout.f90:811-890, spectraout.f90:165-197, ddxout.f90:200-245, :338-380
TALYS quirks kept: the CN recoil is along the beam (angcm = 0) whatever its direction; the 0-degree discrete bin alone
gets the elastic renormalisation (angnorm); the extension of the last recoil bin does not touch the mirrored angle
areas; the LAB DDX at an energy interpolates with the CM grid's deltaE; the LAB elastic DDX counts the compound elastic
twice (xsCMlev = xselastot + xsdisc). Precision: double (TALYS: single).
Approximation (META["approx"]): the binary giant-resonance / collective part of the CM DDX is isotropic (as B4);
binsurface is ported as written, intri's equality test on sideline's values included.

Task: T10 (physics/hf/CONTRACT.md section 7; output only). Acceptance test:
(tests/hf/test_kwcov_b12.py, scripts/kwcov/b12_response.py, docs/hf/COVERAGE_PLAN.md).
"""

from __future__ import annotations

import ctypes
import datetime
import math
import os
from pathlib import Path

import numpy as np

ENV_DIR = "INCOGNITA_RECOIL_DIR"
ENV_EXACT = "INCOGNITA_RECOIL_EXACT"  # 1: the initial CN recoil energy in double precision (TALYS: single, see _recoil_kinematics)
PARSYM = "gnpdtha"
PARZ = (0, 0, 1, 1, 1, 2, 2)
PARN = (0, 1, 0, 1, 2, 1, 2)
NBBINS = 50  # recoilinit.f90: bins for the maximum recoil energy
NUMENDISC = 400  # A0_talys_mod.f90:71
TWOPI = 2.0 * math.pi
FOURPI = 4.0 * math.pi
DEG = math.pi / 180.0

_SET: dict | None = None
_DISCAD: dict = {}
META: dict = {}


def _on(v) -> bool:
    v = str(v).strip().lower()
    return v[:1] in ("1", "y", "t") or v == "on"


def settings(options=None) -> dict | None:
    """The recoil switches of a run, or None when `recoil n` (talysreaction.f90: every recoil call is `if (flagrecoil)`).

    TALYS: input_basicreac.f90:163-183, input_numerics.f90:64-78
    Test: tests/hf/test_kwcov_b12.py
    """
    if options is None:
        from physics.hf.input import fitlib

        ov = {str(k).lower(): v for k, v in fitlib.option_overrides().items()}
        if not _on(ov.get("recoil", "n")):
            return None
        return dict(recoil=True)
    if not bool(getattr(options, "flagrecoil", False)):
        return None
    o = options
    return dict(recoil=True, labddx=bool(o.flaglabddx), recoilav=bool(o.flagrecoilav), maxenrec=int(o.maxenrec),
                nanglerec=int(o.nanglerec), nanglecont=int(o.nanglecont), nangle=int(o.nangle), k0=int(o.k0),
                flagspec=bool(o.flagspec), ddxmode=int(o.ddxmode), fileddxa=tuple(o.fileddxa), fileddxe=tuple(o.fileddxe),
                maxZ=int(o.maxZ), maxN=int(o.maxN), xseps=float(o.xseps_mb), maxchannel=int(getattr(o, "maxchannel", 4)),
                blockspectra=bool(o.flagblockspectra), blockddx=bool(o.flagblockddx))


def wanted() -> bool:
    """The run being set up asks for recoils (the `specout` recorders and every level's discad must be on).

    TALYS: (none -- a port switch)
    Test: tests/hf/test_kwcov_b12.py
    """
    return _SET is not None or settings() is not None


def wanted_for(options) -> bool:
    """`recoil y` on these Options (angout records every level's discad then: angdis.f90:161).

    TALYS: talysreaction.f90:159 (angdis with flagrecoil)
    Test: tests/hf/test_kwcov_b12.py
    """
    return options is not None and bool(getattr(options, "flagrecoil", False))


def active() -> bool:
    """A run with recoils is in progress (begin_run saw `recoil y`).

    TALYS: (none -- a port switch)
    Test: tests/hf/test_kwcov_b12.py
    """
    return _SET is not None


def begin_run(cas) -> bool:
    """Called by specout.begin_run: fix the run's settings, masses and separation energies; check the input.

    TALYS: checkvalue.f90:483-484 (anglesrec 1..numangrec, maxenrec 1..numenrec)
    Test: tests/hf/test_kwcov_b12.py
    """
    global _SET
    _DISCAD.clear()
    s = settings(cas.options)
    if s is not None:
        check(s)
        from physics.hf.core.constants import talys_constants
        from physics.hf.input.defaults import NUMENREC

        c = talys_constants()
        mass = cas.m.mass_amu
        sep = cas.m.s_mev
        s.update(Z=int(cas.Zt), A=int(cas.At), k0=int(cas.k0), Zinit=int(cas.Zt) + PARZ[int(cas.k0)],
                 Ninit=int(cas.At) - int(cas.Zt) + PARN[int(cas.k0)],
                 mass=np.asarray(mass.detach().cpu().numpy() if hasattr(mass, "detach") else mass, float),
                 sep=np.asarray(sep.detach().cpu().numpy() if hasattr(sep, "detach") else sep, float),
                 parmass=tuple(float(x) for x in c["parmass"]), amu=float(c["amu"]), numenrec=NUMENREC)
        try:
            s["elwidth"] = float(cas.params.at("elwidth"))
        except Exception:  # noqa: BLE001 -- Params without the key: TALYS's default
            s["elwidth"] = 0.5
    _SET = s
    return s is not None


def check(s: dict) -> None:
    """checkvalue.f90's ranges of the recoil numerics (the run is refused before it starts).

    TALYS: checkvalue.f90:483-484
    Test: tests/hf/test_kwcov_b12.py
    """
    from physics.hf.input.defaults import NUMANGREC, NUMENREC

    if not 1 <= int(s["nanglerec"]) <= NUMANGREC:
        raise ValueError(f"anglesrec {s['nanglerec']} out of range 1-{NUMANGREC} (TALYS checkvalue.f90:483)")
    if not 1 <= int(s["maxenrec"]) <= NUMENREC:
        raise ValueError(f"maxenrec {s['maxenrec']} out of range 1-{NUMENREC} (TALYS checkvalue.f90:484)")


def end_run() -> None:
    """The run is over.

    TALYS: (none -- a port switch)
    Test: tests/hf/test_kwcov_b12.py
    """
    global _SET
    _SET = None
    _DISCAD.clear()


def take_discad(arr: dict, nangle: int) -> None:
    """angout hands over the run's discrete angular distributions (discad of every level, `angles` grid).

    TALYS: angdis.f90:1 (angdis) -- discad
    Test: tests/hf/test_kwcov_b12.py
    """
    if _SET is None:
        return
    _DISCAD.clear()
    _DISCAD.update({k: np.asarray(v, float) for k, v in arr.items() if "ang.L" in k and ":" not in k})
    _DISCAD["_nangle"] = int(nangle)


# ------------------------------------------------------------------------------------------------ the LAB scatter
_LIB = None


def _lib():
    """physics/hf/native/lib/librecoil.so (scripts/build_recoil_native.sh) or None; RECOIL_PY=1 forces Python."""
    global _LIB
    if os.environ.get("RECOIL_PY", "0") == "1":
        return None
    if _LIB is None:
        p = Path(__file__).resolve().parent / "native" / "lib" / "librecoil.so"
        try:
            so = ctypes.CDLL(str(p))
            if so.rc_version() != 1:
                raise OSError("version")
            so.rc_batch.argtypes = [ctypes.c_void_p] * 3
            so.rc_batch.restype = ctypes.c_int
            _LIB = so
        except OSError:
            _LIB = False
    return _LIB or None


def _belongs(x, x1, x2) -> bool:
    x1x, x1x2 = x - x1, x2 - x1
    eps = abs(x1x2) / 1.0e14
    return not (x1x * x1x2 < -eps or abs(x1x) - abs(x1x2) > eps)


def _sideline(x, y, xs, ys, xe, ye) -> float:
    """sideline.f90: -1 / 0 / 1 for a sloped segment, but the signed distance for a vertical / horizontal one."""
    xdlim, ydlim = min(abs(xs), abs(xe)) / 1.0e14, min(abs(ys), abs(ye)) / 1.0e14
    if abs(xs - xe) <= xdlim:
        v = x - xs
        return 0.0 if abs(v) <= xdlim else v
    if abs(ys - ye) <= ydlim:
        v = y - ys
        return 0.0 if abs(v) <= ydlim else v
    a = (ys - ye) / (xs - xe)
    v = y - (a * x + (ys - a * xs))
    return 0.0 if abs(v) <= 1.0e-12 else (-1.0 if v < 0.0 else 1.0)


def _intri(x, y, x1, y1, x2, y2, x3, y3) -> bool:
    """intri.f90 (sideline.f90's values compared for equality)."""
    xg, yg = (x1 + x2 + x3) / 3.0, (y1 + y2 + y3) / 3.0
    for ax, ay, bx, by in ((x1, y1, x2, y2), (x2, y2, x3, y3), (x3, y3, x1, y1)):
        sv = _sideline(x, y, ax, ay, bx, by)
        if not (sv == _sideline(xg, yg, ax, ay, bx, by) or sv == 0.0):
            return False
    return True


def _invect(x, y, x1, y1, x2, y2) -> bool:
    """invect.f90."""
    x1x, y1x, x12, y12 = x - x1, y - y1, x2 - x1, y2 - y1
    n2 = x12 * x12 + y12 * y12
    eps = n2 / 1.0e14
    return not (x12 * x1x + y12 * y1x < -eps or (x1x * x1x + y1x * y1x) - n2 > eps)


def _intersection(xs, ys, xe, ye, xl, yl, xu, yu) -> list:
    """intersection.f90: the line through the segment with the four sides of the bin."""
    xdlim, ydlim = min(abs(xs), abs(xe)) / 1.0e14, min(abs(ys), abs(ye)) / 1.0e14
    if abs(xs - xe) <= xdlim:
        return [(xs, yu), (xs, yl)] if _belongs(xs, xu, xl) else []
    if abs(ys - ye) <= ydlim:
        return [(xu, ys), (xl, ys)] if _belongs(ys, yu, yl) else []
    a = (ys - ye) / (xs - xe)
    b = ys - a * xs
    ya, yb, xc, xd = a * xl + b, a * xu + b, (yl - b) / a, (yu - b) / a
    out = []
    if _belongs(ya, yu, yl):
        out.append((xl, ya))
    if _belongs(yb, yu, yl):
        out.append((xu, yb))
    if _belongs(xc, xu, xl):
        out.append((xc, yl))
    if _belongs(xd, xu, xl):
        out.append((xd, yu))
    return out


def binsurface(x1, y1, x2, y2, x3, y3, xl, xu, yl, yu, surfbin, epsx=None, epsy=None) -> float:
    """Area of the triangle inside the bin [xl, xu] x [yl, yu] as binsurface.f90 computes it: the polygon of bin
    corners inside the triangle (intri), side intersections (intersection, invect) and summits inside the bin, merged
    within epsx / epsy, sorted by angle around its centre of gravity, fan area; surfbin when all four corners are
    inside. intri's vertical / horizontal-side quirk (sideline.f90) is kept, so this is not always the exact overlap
    (labsurface renormalises the bins of a triangle to its area).

    TALYS: binsurface.f90:1 (binsurface), intri.f90:1, invect.f90:1, intersection.f90:1, sideline.f90:1
    Test: tests/hf/test_kwcov_b12.py
    """
    epsx = (xu - xl) / 100000.0 if epsx is None else epsx
    epsy = abs(yu - yl) / 100000.0 if epsy is None else epsy
    surf = [(cx, cy) for cx, cy in ((xl, yl), (xl, yu), (xu, yl), (xu, yu)) if _intri(cx, cy, x1, y1, x2, y2, x3, y3)]
    if len(surf) == 4:
        return surfbin
    sx, sy = (x1, x2, x3), (y1, y2, y3)
    pts = []
    for e in range(3):
        ax, ay, bx, by = sx[e], sy[e], sx[(e + 1) % 3], sy[(e + 1) % 3]
        pts += [p for p in _intersection(ax, ay, bx, by, xl, yl, xu, yu) if _invect(p[0], p[1], ax, ay, bx, by)]
    pts += [(sx[k], sy[k]) for k in range(3) if _belongs(sx[k], xu, xl) and _belongs(sy[k], yu, yl)]
    if not surf and pts:
        surf = [pts[0]]
    for p in pts:
        if not any(abs(p[0] - q[0]) <= epsx and abs(p[1] - q[1]) <= epsy for q in surf):
            surf.append(p)
    n = len(surf)
    if n <= 2:
        return 0.0
    if n == 3:
        (a1, b1), (a2, b2), (a3, b3) = surf
        return abs(0.5 * ((a3 - a2) * (b1 - b2) - (a1 - a2) * (b3 - b2)))
    xg, yg = sum(p[0] for p in surf) / n, sum(p[1] for p in surf) / n
    r1x, r1y = surf[0][0] - xg, surf[0][1] - yg
    n1 = r1x * r1x + r1y * r1y
    ang = [0.0]
    for p in surf[1:]:
        r2x, r2y = p[0] - xg, p[1] - yg
        n12 = n1 * (r2x * r2x + r2y * r2y)
        c = 1.0 if n12 == 0.0 else (r1x * r2x + r1y * r2y) / math.sqrt(n12)
        a = math.pi if c <= -1.0 else (0.0 if c >= 1.0 else math.acos(c))
        if r1x * r2y - r2x * r1y < 0.0:
            a = 2.0 * math.pi - a
        ang.append(a)
    for i in range(n - 1):
        for j in range(i + 1, n):
            if ang[j] > ang[i]:
                continue
            surf[i], surf[j], ang[i], ang[j] = surf[j], surf[i], ang[j], ang[i]
    tot = abs(0.5 * ((xg - surf[-1][0]) * (surf[0][1] - surf[-1][1]) - (surf[0][0] - surf[-1][0]) * (yg - surf[-1][1])))
    for i in range(n - 1):
        (a1, b1), (a2, b2) = surf[i], surf[i + 1]
        tot += abs(0.5 * ((xg - a2) * (b1 - b2) - (a1 - a2) * (yg - b2)))
    return tot


def labsurface(g: dict, pts, scov: np.ndarray):
    """labsurface.f90 on grid g (ix0, ixmax, nang, ej, xmin, xmax, area, cmin, cmax): (totsurf, limx, limy); fills scov.

    TALYS: labsurface.f90:1 (labsurface)
    Test: tests/hf/test_kwcov_b12.py
    """
    nang = g["nang"]
    iymax = 2 * nang + 1
    xs, yc, nt = [], [], []
    for x, c, s in pts:
        c = min(max(c, -1.0), 1.0)
        ang = math.acos(c)
        if s < 0.0:
            ang = 2.0 * math.pi - ang
        is_ = int(ang / math.pi)
        nt.append(int(ang / (2.0 * math.pi)))
        yc.append(-2.0 * is_ + (-1.0 if is_ % 2 else 1.0) * math.cos(ang))
        xs.append(x)
    ts = abs(0.5 * ((xs[0] - xs[2]) * (yc[1] - yc[2]) - (xs[1] - xs[2]) * (yc[0] - yc[2])))
    mode2 = ts < 1.0e-14
    if mode2:
        ts = 1.0e-14
    xmin, xmax, area, cmin, cmax = g["xmin"], g["xmax"], g["area"], g["cmin"], g["cmax"]
    ixk, iyk = [1, 1, 1], [0, 0, 0]
    for k in range(3):
        if xs[k] > xmax[g["ixmax"]]:
            xmax[g["ixmax"]] = xs[k]
            ixk[k] = g["ixmax"]
        else:
            for ix in range(g["ix0"], g["ixmax"] + 1):
                if _belongs(xs[k], xmin[ix], xmax[ix]):
                    ixk[k] = ix
                    break
    for k in range(3):
        for iy in range(iymax + 1):
            yl = yu = -4.0 * nt[k]
            if iy <= nang:
                yl, yu = yl + cmin[iy], yu + cmax[iy]
            else:
                yl, yu = yl - cmin[iy] - 2.0, yu - cmax[iy] - 2.0
            if _belongs(yc[k], yl, yu):
                iyk[k] = iy + nt[k] * (iymax + 1)
                break
    limx, limy = (min(ixk), max(ixk)), (min(iyk), max(iyk))

    def ixs(ix):
        return max(ix, 1) if g["ej"] else ix

    if limx[0] == limx[1] and limy[0] == limy[1]:
        scov[ixs(limx[0]), limy[0] % (iymax + 1)] = ts
        return ts, limx, limy
    nb = (limx[1] - limx[0] + 1) * (limy[1] - limy[0] + 1)
    cells = [(ix, iy) for ix in range(limx[0], limx[1] + 1) for iy in range(limy[0], limy[1] + 1)]
    if mode2:
        for ix, iy in cells:
            scov[ixs(ix), iy % (iymax + 1)] = ts * (1.0 / nb)
        return ts, limx, limy
    tot = 0.0
    for ix, iy in cells:
        ist, nturn = iy % (iymax + 1), iy // (2 * nang + 2)
        yl = yu = -4.0 * nturn
        if ist <= nang:
            yl, yu = yl + cmin[ist], yu + cmax[ist]
        else:
            yl, yu = yl - cmin[ist] - 2.0, yu - cmax[ist] - 2.0
        v = binsurface(xs[0], yc[0], xs[1], yc[1], xs[2], yc[2], xmin[ix], xmax[ix], yl, yu, area[ix, ist],
                       (xmax[ix] - xmin[ix]) / 100000.0, abs(yu - yl) / 100000.0)
        scov[ixs(ix), ist] = v
        tot += v
    if ts != tot:
        for ix, iy in cells:
            scov[ixs(ix), iy % (iymax + 1)] = scov[ixs(ix), iy % (iymax + 1)] * (ts / tot) if tot != 0.0 else ts / nb
    return ts, limx, limy


def scatter_py(cells: np.ndarray, t: int, em: float, rm: float, nuc: dict, renorm_rec: bool, ej: dict | None,
               renorm_ej: bool) -> None:
    """The LAB scatter of a batch of CM cells (rows E1 E2 cos1 cos2 sin1 sin2 vcm flux divide iexlo iexhi), in order:
    cm2lab, the last-bin renormalisations (binary / discrete), the two labsurface triangles, the deposits. Python twin
    of native/recoil.c rc_batch.

    TALYS: cm2lab.f90:1, binaryrecoil.f90:1, angdisrecoil.f90:1, comprecoil.f90:1 (the per-cell bodies)
    Test: tests/hf/test_kwcov_b12.py
    """
    maxenrec, nr = nuc["maxenrec"], nuc["nr"]
    gr = dict(ix0=0, ixmax=maxenrec, nang=nr, ej=False, xmin=nuc["Erecmin"], xmax=nuc["Erecmax"], area=nuc["area"],
              cmin=nuc["cmin"], cmax=nuc["cmax"])
    ddxrec, ddxrectot = nuc["ddxrec"], nuc["ddxrectot"]
    nexrows = ddxrec.shape[0]
    rcols = 2 * nr + 2
    sr1, sr2 = np.zeros((maxenrec + 2, rcols)), np.zeros((maxenrec + 2, rcols))
    if ej is not None:
        nc, iej = ej["nang"], ej["ixmax"]
        ecols = 2 * nc + 2
        se1, se2 = np.zeros((iej + 2, ecols)), np.zeros((iej + 2, ecols))
    ratio = rm / (em * (em + rm)) if t != 0 else 0.0
    for q in cells:
        E1, E2, c1, c2, s1, s2, vcm, flux, divide = (float(v) for v in q[:9])
        iexlo, iexhi = int(q[9]), int(q[10])
        if flux == 0.0:
            continue
        if t != 0:
            p1, p2 = em * math.sqrt(2.0 * ratio * E1), em * math.sqrt(2.0 * ratio * E2)
            vej = (p1 / em, p1 / em, p2 / em, p2 / em)
        else:
            p1, p2 = E1, E2
            vej = (0.0,) * 4
        vrr = (p1 / rm, p1 / rm, p2 / rm, p2 / rm)
        cc, sc, ecm = (c1, c2, c1, c2), (s1, s2, s1, s2), (E1, E1, E2, E2)
        pe, pr = [], []
        for k in range(4):
            if t == 0:
                pe.append((ecm[k], cc[k], sc[k]))
            else:
                vx, vy = vcm + vej[k] * cc[k], vej[k] * sc[k]
                v2 = vx * vx + vy * vy
                v = max(math.sqrt(v2), 1e-20)
                pe.append((0.5 * em * v2, vx / v, vy / v))
            vx, vy = vcm - vrr[k] * cc[k], -vrr[k] * sc[k]
            v2 = vx * vx + vy * vy
            v = max(math.sqrt(v2), 1e-20)
            pr.append((0.5 * rm * v2, vx / v, -sc[k]))
        if ej is not None:
            if renorm_ej:
                emaxi = ej["xmax"][iej]
                deori = emaxi - ej["xmin"][iej]
                big = max(p[0] for p in pe)
                if big > emaxi:
                    ej["xmax"][iej] = big
                    denew = big - ej["xmin"][iej]
                    ej["dE"][iej] = denew
                    rn = deori / denew
                    ej["area"][iej, : nc + 1] /= rn
                    ej["ren"][iej, : nc + 1] *= rn
            t1, lx1, ly1 = labsurface(ej, (pe[0], pe[1], pe[2]), se1)
            t2, lx2, ly2 = labsurface(ej, (pe[2], pe[3], pe[1]), se2)
            ls = t1 + t2
            if ls == 0.0:
                continue
            ddxlab = flux / ls
            for lx, ly, sc_ in ((lx1, ly1, se1), (lx2, ly2, se2)):
                for ix in range(lx[0], lx[1] + 1):
                    for iy in range(ly[0], ly[1] + 1):
                        im = iy % ecols
                        iys = im if im <= nc else 2 * nc + 1 - im
                        a = ej["area"][ix, im]
                        if a > 0.0:
                            ej["dep"][ix, iys] += ddxlab / a * sc_[max(ix, 1), im]
        if renorm_rec:
            emaxi = gr["xmax"][maxenrec]
            deori = emaxi - gr["xmin"][maxenrec]
            big = max(p[0] for p in pr)
            if big > emaxi:
                gr["xmax"][maxenrec] = big
                rn = deori / (big - gr["xmin"][maxenrec])
                gr["area"][maxenrec, : nr + 1] /= rn
                ddxrec[:, maxenrec, : nr + 1] *= rn
        t1, lx1, ly1 = labsurface(gr, (pr[0], pr[1], pr[2]), sr1)
        t2, lx2, ly2 = labsurface(gr, (pr[2], pr[3], pr[1]), sr2)
        ls = t1 + t2
        if ls == 0.0:
            continue
        ddxlab = flux / ls / divide
        for lx, ly, sc_ in ((lx1, ly1, sr1), (lx2, ly2, sr2)):
            for ix in range(lx[0], lx[1] + 1):
                for iy in range(ly[0], ly[1] + 1):
                    im = iy % rcols
                    a = gr["area"][ix, im]
                    if a == 0.0:
                        continue
                    fa = ddxlab * sc_[ix, im]
                    iys = im if im <= nr else 2 * nr + 1 - im
                    for ie in range(max(iexlo, 0), min(iexhi, nexrows - 1) + 1):
                        ddxrec[ie, ix, iys] += fa / a
                        ddxrectot[ie] += fa


def scatter(cells, t: int, em: float, rm: float, nuc: dict, renorm_rec: bool, ej: dict | None = None,
            renorm_ej: bool = False) -> None:
    """The LAB scatter (native/recoil.c when built, else scatter_py); the state arrays are updated in place.

    TALYS: cm2lab.f90:1, labsurface.f90:1, binsurface.f90:1 (via native/recoil.c)
    Test: tests/hf/test_kwcov_b12.py
    """
    cells = np.ascontiguousarray(cells, dtype=np.float64).reshape(-1, 11)
    if cells.shape[0] == 0:
        return
    so = _lib()
    if so is None:
        return scatter_py(cells, t, em, rm, nuc, renorm_rec, ej, renorm_ej)
    for k in ("Erecmin", "Erecmax", "area", "cmin", "cmax", "ddxrec", "ddxrectot"):
        assert nuc[k].dtype == np.float64 and nuc[k].flags.c_contiguous, k
    iv = np.zeros(10, np.int64)
    iv[:6] = (cells.shape[0], t, nuc["maxenrec"], nuc["nr"], nuc["ddxrec"].shape[0], int(renorm_rec))
    dv = np.array([em, rm], float)
    pv = np.zeros(16, np.uint64)
    pv[0] = cells.ctypes.data
    for i, k in enumerate(("Erecmin", "Erecmax", "area", "cmin", "cmax", "ddxrec", "ddxrectot"), start=1):
        pv[i] = nuc[k].ctypes.data
    if ej is not None:
        iv[6:10] = (1, ej["ixmax"], ej["nang"], int(renorm_ej))
        for i, k in enumerate(("xmin", "xmax", "dE", "area", "cmin", "cmax", "dep", "ren"), start=8):
            a = ej[k]
            assert a.dtype == np.float64 and a.flags.c_contiguous, k
            pv[i] = a.ctypes.data
    rc = so.rc_batch(iv.ctypes.data, dv.ctypes.data, pv.ctypes.data)
    if rc != 0:
        raise MemoryError("rc_batch")


# ------------------------------------------------------------------------------------------------ one incident energy
def _angle_grids(s: dict) -> dict:
    """recoilinit.f90's bin edges in real(sgl): discrete (nangle), continuum (nanglecont, mirrored to 2 nanglecont + 1),
    recoil (nanglerec). Single precision as TALYS (the LAB binning of a CM cell whose edges meet a bin edge depends on
    the last bit)."""
    from physics.hf import angout, specobs

    f32 = np.float32
    d2r = f32(f32(math.pi) / f32(180.0))
    nangle, nc, nr = s["nangle"], s["nanglecont"], s["nanglerec"]

    def edges(ang, n):
        d = f32(180.0) / f32(n)
        lo = np.maximum(f32(0.0), ang - f32(0.5) * d).astype(f32)
        hi = np.minimum(f32(180.0), ang + f32(0.5) * d).astype(f32)
        return lo, hi

    g = {}
    amin, amax = edges(angout.angles(nangle).astype(f32), nangle)
    g["cosangmin"], g["cosangmax"] = np.cos(amin * d2r).astype(float), np.cos(amax * d2r).astype(float)
    g["sinangmin"], g["sinangmax"] = np.sin(amin * d2r).astype(float), np.sin(amax * d2r).astype(float)
    g["dcosang"] = np.abs(g["cosangmin"] - g["cosangmax"]).astype(f32).astype(float)
    g["sinangmin"][0] = float(f32(1.0e-6))
    g["sinangmax"][nangle] = float(f32(1.0e-6))
    th = specobs.anglecont(nc)
    cmin, cmax = edges(th.astype(f32), nc)
    g["anglecont"], g["angmid"] = th, (f32(0.5) * (cmin + cmax)).astype(float)
    cc = {k: np.zeros(2 * nc + 2) for k in ("cmin", "cmax", "smin", "smax", "dcos")}
    cc["cmin"][: nc + 1], cc["cmax"][: nc + 1] = np.cos(cmin * d2r), np.cos(cmax * d2r)
    cc["smin"][: nc + 1], cc["smax"][: nc + 1] = np.sin(cmin * d2r), np.sin(cmax * d2r)
    cc["dcos"][: nc + 1] = np.abs(cc["cmin"][: nc + 1].astype(f32) - cc["cmax"][: nc + 1].astype(f32))
    for i in range(nc + 1, 2 * nc + 2):
        j = i - nc - 1
        cc["cmax"][i], cc["cmin"][i] = -cc["cmax"][j], -cc["cmin"][j]
        cc["smin"][i], cc["smax"][i] = -cc["smin"][j], -cc["smax"][j]
        cc["dcos"][i] = cc["dcos"][2 * nc + 1 - i]
    tiny = float(f32(1.0e-6))
    cc["smin"][0] = tiny
    cc["smax"][nc] = tiny
    cc["smax"][2 * nc + 1] = -tiny
    cc["smin"][nc + 1] = -tiny
    g["cont"] = cc
    d = f32(180.0) / f32(nr)
    rmin, rmax = edges((d * np.arange(nr + 1, dtype=f32)).astype(f32), nr)
    rc = {k: np.zeros(2 * nr + 2) for k in ("cmin", "cmax", "dcos")}
    rc["cmin"][: nr + 1], rc["cmax"][: nr + 1] = np.cos(rmin * d2r), np.cos(rmax * d2r)
    for i in range(nr + 1, 2 * nr + 2):
        rc["cmax"][i], rc["cmin"][i] = -rc["cmax"][i - nr - 1], -rc["cmin"][i - nr - 1]
    rc["dcos"] = np.abs(rc["cmin"].astype(f32) - rc["cmax"].astype(f32)).astype(float)
    g["rec"] = rc
    return g


def _ejectile_grid(s, g, t, e_inc, eg, nl_eout) -> dict | None:
    """recoilinit.f90's LAB ejectile energy grid of type t: Eejlab, bin edges and areas (None: no LAB grid)."""
    f32 = np.float32
    # Emaxinc = Einc + S(0,0,k0) + targetE and Emaxlab = Emaxinc - S(0,0,type): real(sgl) of double sums (S is real(dbl))
    emaxinc = f32(float(f32(e_inc)) + float(s["sep"][0, 0, s["k0"]]))
    emaxlab32 = f32(float(emaxinc) - float(s["sep"][0, 0, t]))
    emaxlab = float(emaxlab32)
    if emaxlab < 0.0:
        return None
    maxen = len(eg) - 1
    eg32 = eg.astype(np.float32)
    maxentype = 0
    for iej in range(maxen + 1):
        if eg32[iej] >= emaxlab32:
            maxentype = iej
            break
    if maxen > 0 and eg32[maxen] < emaxlab32:
        maxentype = maxen
    if maxentype > 0:
        maxentype = max(maxentype, 3)
    elast = max(nl_eout - s["elwidth"], 0.0)
    from physics.hf.specout import _locate

    nend = maxentype if elast > eg[maxentype] else _locate(eg, 0, maxentype, elast)
    E = np.zeros(nend + NUMENDISC + 3)
    E[1: nend + 1] = eg[1: nend + 1]
    nhigh = min(int(math.floor(10.0 * (eg[maxentype] - eg[nend]) + 0.5)), NUMENDISC)  # nint
    iejlab = nend + nhigh
    for iej in range(nend + 1, nend + nhigh + 1):
        E[iej] = float(eg32[nend] + f32(0.1) * f32(iej - nend))
        if f32(E[iej]) > emaxlab32:
            iejlab = min(iejlab, iej)
    n = iejlab
    if n < 2:
        return None
    dE, emax_, emin_ = np.zeros(E.size), np.zeros(E.size), np.zeros(E.size)
    for iej in range(2, n):
        dE[iej] = 0.5 * (E[iej + 1] - E[iej - 1])
        emax_[iej] = 0.5 * (E[iej] + E[iej + 1])
        emin_[iej] = 0.5 * (E[iej] + E[iej - 1])
    dE[1] = E[1] + 0.5 * (E[2] - E[1])
    emin_[1], emax_[1] = 0.0, dE[1]
    emin_[n] = emax_[max(0, n - 1)]
    emax_[n] = emaxlab
    dE[n] = emax_[n] - emin_[n]
    E[n] = 0.5 * (emaxlab + emin_[n])
    nc = s["nanglecont"]
    area = np.zeros((n + 1, 2 * nc + 2))
    area[1: n + 1] = dE[1: n + 1, None] * g["cont"]["dcos"][None, :]
    return dict(ix0=1, ixmax=n, nang=nc, ej=True, E=E[: n + 2].copy(), xmin=np.ascontiguousarray(emin_[: n + 2]),
                xmax=np.ascontiguousarray(emax_[: n + 2]), dE=np.ascontiguousarray(dE[: n + 2]), area=area,
                cmin=g["cont"]["cmin"], cmax=g["cont"]["cmax"], ddx=np.zeros((n + 2, nc + 1)))


def _recoil_kinematics(s: dict, e_inc: float, etotal: float):
    """recoilinit.f90:220-415: Erecinit and the classical maximum recoil energy Erecmaxmax(Zix, Nix) of every residual
    the emission of n p d t h a can reach (50-bin sweep of the CM excitation, momentum carried by the fastest frame)."""
    k0, amu = s["k0"], s["amu"]
    parmass, S, M = s["parmass"], s["sep"], s["mass"]
    f32 = np.float32
    if os.environ.get(ENV_EXACT, "0") == "1":  # port switch: the CN recoil energy in double precision
        projectmass = parmass[k0] * amu
        ptot = math.sqrt(e_inc * (e_inc + 2.0 * projectmass))
        compmass = M[0, 0] * amu
        erecinit = math.sqrt(ptot ** 2 + compmass ** 2) - compmass
    else:  # recoilinit.f90:207-211 in real(sgl): sqrt(P^2 + M^2) - M cancels to the float32 spacing of M (~4 keV)
        projectmass = f32(parmass[k0] * amu)
        ekin = f32(e_inc)
        ptot32 = np.sqrt(ekin * (ekin + f32(2.0) * projectmass))
        compmass32 = f32(M[0, 0] * amu)
        erecinit = float(np.sqrt(ptot32 * ptot32 + compmass32 * compmass32) - compmass32)
        ptot = float(ptot32)
    zmax, nmax, zinit, ninit = s["maxZ"] + 2, s["maxN"] + 2, s["Zinit"], s["Ninit"]

    def zn(c):
        return c[2] + c[3] + c[4] + 2 * (c[5] + c[6]), c[1] + c[3] + c[5] + 2 * (c[4] + c[6])

    combos = [[0] * 7]
    eexmax = [etotal]
    while True:
        npass = len(combos)
        iloop = 1
        for ires in range(npass):
            iloop = 0 if ires == len(combos) - 1 else 1
            zc, nc = zn(combos[ires])
            for t in range(1, 7):
                zr, nr = zc + PARZ[t], nc + PARN[t]
                if zr > zmax or zr > zinit or nr > nmax or nr > ninit:
                    continue
                eloc = eexmax[ires] - float(S[zc, nc, t])
                if eloc <= 0.0:
                    continue
                for k in range(len(combos)):
                    if zn(combos[k]) == (zr, nr):
                        eexmax[k] = max(eexmax[k], eloc)
                        break
                else:
                    f = list(combos[ires])
                    f[t] += 1
                    combos.append(f)
                    eexmax.append(eloc)
                    iloop = 1
        if iloop != 1:
            break
    nres = len(combos)
    eex = np.array([np.arange(NBBINS + 1) * (eexmax[i] / NBBINS) for i in range(nres)])
    pcm = np.zeros((nres, NBBINS + 1))
    pcm[0, NBBINS] = ptot
    index = {tuple(c): i for i, c in enumerate(combos)}
    for ires in range(nres):
        zc, nc = zn(combos[ires])
        cmass = M[zc, nc] * amu
        for iex in range(NBBINS, -1, -1):
            ecm = eex[ires, iex]
            vcm = pcm[ires, iex] / (cmass + ecm)
            for t in range(7):
                em = parmass[t] * amu
                f = list(combos[ires])
                if t:
                    f[t] += 1
                k = index.get(tuple(f))
                if k is None:
                    continue
                zr, nr = zn(combos[k])
                rmass = M[zr, nr] * amu + eex[k]
                eej = ecm - eex[k] - float(S[zc, nc, t])
                eej = np.where(np.abs(eej) <= 1.0e-10, 0.0, eej)
                ok = eej > 0.0
                if not np.any(ok):
                    continue
                if t:
                    ratio = rmass / (em * (em + rmass))
                    prec = em * np.sqrt(2.0 * ratio * np.where(ok, eej, 0.0))
                else:
                    prec = eej
                plab = rmass * (vcm + prec / rmass)
                pcm[k] = np.where(ok, np.maximum(pcm[k], plab), pcm[k])
    erecmax = {}
    for ires in range(nres):
        zr, nr = zn(combos[ires])
        rmass = M[zr, nr] * amu + eex[ires]
        erecmax[(zr, nr)] = float(np.max(pcm[ires] ** 2 / (2.0 * rmass)))
    return erecinit, erecmax


def _nuclei(r: dict) -> dict:
    """(Zix, Nix) -> excitation grid of every nucleus the run's records touch (own walk first, then as a daughter)."""
    out = {}
    walks = r.get("walks", {})
    for key, rec in walks.items():
        if rec.get("lines_only"):
            continue
        out[key] = dict(ex=np.asarray(rec["ex"], float), dex=np.asarray(rec["dex"], float), maxex=int(rec["maxex"]),
                        nlast=int(rec["nlast"]))
    for key, rec in walks.items():
        if rec.get("lines_only"):
            continue
        for t, e in rec["types"].items():
            d = (key[0] + PARZ[t], key[1] + PARN[t])
            if d not in out:
                out[d] = dict(ex=np.asarray(e["ex"], float), dex=np.asarray(e["dex"], float), maxex=int(e["maxex"]),
                              nlast=int(e["nlast"]))
    return out


def energy_recoil(r: dict, s: dict, row: int) -> dict:
    """The recoil module of TALYS for one recorded incident energy `r` (a specout.ENERGIES entry).

    TALYS: recoilinit.f90:1, binaryrecoil.f90:1, angdisrecoil.f90:1, compemission.f90:1 + comprecoil.f90:1,
    totalrecoil.f90:1
    Test: tests/hf/test_kwcov_b12.py
    """
    from physics.hf import specang
    from physics.hf.specout import _locate

    approx = []
    k0, amu = s["k0"], s["amu"]
    e_inc = float(r["e_inc_mev"])
    b = r["binary"]
    etotal = float(b["etotal_mev"])
    eg, eb, et, de = (np.asarray(r[k], float) for k in ("egrid", "ebottom", "etop", "deltae"))
    E = len(eg)
    S, M, parmass = s["sep"], s["mass"], s["parmass"]
    maxenrec, nr, nc, numenrec = s["maxenrec"], s["nanglerec"], s["nanglecont"], s["numenrec"]
    labddx = s["labddx"]
    g = _angle_grids(s)
    cont, rgrid = g["cont"], g["rec"]
    ang = r.get("ang") or {}
    xselastot = float(ang.get("xselastot", 0.0))
    xscompel = float(ang.get("xscompel", b.get("xscompel_mb", 0.0)))
    if not math.isfinite(xselastot) or k0 > 1:  # charged projectile: no total / shape elastic (incidentread.f90:234)
        xselastot = xscompel
    xselasinc = xselastot - xscompel
    xstotinc = float(b.get("xsreacinc_mb", 0.0)) + xselasinc
    btypes = b["types"]
    sm = specang.smyers(s["Zinit"], s["Zinit"] + s["Ninit"])
    # --- recoilinit: LAB ejectile grids
    ejg = {}
    if labddx:
        for t, ent in btypes.items():
            nl = int(ent["nlast"])
            le = list(ent.get("lines_e") or [])
            nl_eout = float(le[nl]) if nl < len(le) else -1.0
            e = _ejectile_grid(s, g, t, e_inc, eg, nl_eout)
            if e is not None:
                ejg[t] = e
    # --- recoilinit: recoil grids of every residual
    erecinit, erecmaxmax = _recoil_kinematics(s, e_inc, etotal)
    grids = _nuclei(r)
    for t, ent in btypes.items():  # binary residuals: their grid as the CN walk saw it (or the binary record's size)
        key = (PARZ[t], PARN[t])
        if key not in grids and (np.any(np.asarray(ent.get("xsbinemis", []), float) != 0.0)
                                 or np.any(np.asarray(ent.get("lines_xs", []), float) != 0.0)):
            approx.append(f"E={e_inc:g}: binary residual {key} has no excitation grid, skipped")
    nuc = {}
    for key, gd in grids.items():
        em_ = erecmaxmax.get(key, 0.0)
        rows = max(gd["maxex"] + 1, len(gd["ex"]))
        n = dict(maxenrec=maxenrec, nr=nr, cmin=rgrid["cmin"], cmax=rgrid["cmax"], Erecmin=np.zeros(numenrec + 2),
                 Erecmax=np.zeros(numenrec + 2), Erec=np.zeros(numenrec + 2), area=np.zeros((maxenrec + 2, 2 * nr + 2)),
                 ddxrec=np.zeros((rows, maxenrec + 1, nr + 1)), ddxrectot=np.zeros(rows), **gd)
        if em_ > 0.0:
            d = em_ / (maxenrec + 1)
            i = np.arange(numenrec + 1)
            n["Erecmin"][: numenrec + 1], n["Erecmax"][: numenrec + 1] = i * d, (i + 1) * d
            n["Erec"][: numenrec + 1] = i * d + 0.5 * d
            n["area"][: maxenrec + 1] = (n["Erecmax"][: maxenrec + 1] - n["Erecmin"][: maxenrec + 1])[:, None] \
                * rgrid["dcos"][None, :]
        nuc[key] = n
    cn = nuc.get((0, 0))
    if cn is None:
        return dict(approx=approx + [f"E={e_inc:g}: no compound-nucleus record"], nuclei={}, ej={})
    d00 = erecmaxmax.get((0, 0), 0.0) / (maxenrec + 1)
    irecinit = min(int(erecinit / d00), numenrec, maxenrec) if d00 > 0 else 0
    mx0 = cn["maxex"]
    if cn["area"][irecinit, 0] != 0.0:
        cn["ddxrec"][mx0, irecinit, 0] = xstotinc / TWOPI / cn["area"][irecinit, 0]
    cn["ddxrectot"][mx0] = xstotinc / TWOPI
    compmass = M[0, 0] * amu
    vcm0 = math.sqrt(2.0 * erecinit / compmass)

    def ejd(t, dep_key="ddx"):
        e = ejg.get(t)
        if e is None:
            return None
        return dict(e, dep=e[dep_key], ren=e["ddx"])

    def cellrows(E1, E2, cs, ss, vcm, flux, divide, lo, hi):
        n_ = len(flux)
        out = np.empty((n_, 11))
        out[:, 0], out[:, 1] = E1, E2
        out[:, 2], out[:, 3], out[:, 4], out[:, 5] = cs[0], cs[1], ss[0], ss[1]
        out[:, 6], out[:, 7], out[:, 8], out[:, 9], out[:, 10] = vcm, flux, divide, lo, hi
        return out

    # --- binaryrecoil (binary.f90:514, inside `if (flagspec)`)
    if s["flagspec"]:
        sums = {}
        for t in sorted(btypes):
            ent = btypes[t]
            key = (PARZ[t], PARN[t])
            n = nuc.get(key)
            if n is None:
                continue
            raw = ent.get("raw") or ent
            vec = lambda v: np.pad(np.asarray(v, float)[:E], (0, max(0, E - len(v))))  # noqa: E731
            xc, pe, gr_ = vec(raw["xsemis"]), vec(raw["xspreeq"]), vec(raw["xsgr"])
            ib, ie = int(ent["ebegin"]), int(ent["eend"])
            xsb = xc + pe + gr_
            K = specang.kalbach_shape(specang.kalbach_a(k0, t, e_inc, eg, sm), g["anglecont"])
            ad = (xc + gr_)[:, None] / FOURPI + np.where((pe != 0.0)[:, None], pe[:, None] * K, 0.0)
            SS = float(S[0, 0, t])
            em, rm = parmass[t] * amu, M[key] * amu
            exg = n["ex"][: n["maxex"] + 1]
            blocks = []
            for nen in range(max(ib, 0), ie + 1):
                if xsb[nen] == 0.0:
                    continue
                E1 = eb[nen] if eb[nen] != 0.0 else 0.5 * eg[1]
                if E1 > etotal - SS:
                    continue
                E2 = et[nen]
                x1, x2 = etotal - SS - E1, etotal - SS - E2
                i1 = int(np.flatnonzero(exg <= x1)[-1]) if np.any(exg <= x1) else 0
                i2 = int(np.flatnonzero(exg <= x2)[-1]) if np.any(exg <= x2) else 0
                lo, hi = min(i1, i2), max(i1, i2)
                flux = ad[nen, : nc + 1] * (E2 - E1) * cont["dcos"][: nc + 1]
                blocks.append(cellrows(E1, E2, (cont["cmin"][: nc + 1], cont["cmax"][: nc + 1]),
                                       (cont["smin"][: nc + 1], cont["smax"][: nc + 1]), vcm0, flux, hi - lo + 1, lo, hi))
            ej = ejd(t)
            if blocks:
                scatter(np.vstack(blocks), t, em, rm, n, True, ej, True)
            sumej = 0.0
            if ej is not None:
                e = ejg[t]
                k = e["ixmax"]
                sumej = float(np.sum((e["ddx"][1: k + 1] * cont["dcos"][None, : nc + 1]).sum(axis=1) * TWOPI
                                     * e["dE"][1: k + 1]))
            rows = n["maxex"] + 1
            sumrec = float(np.sum(n["ddxrec"][:rows] * n["area"][None, : maxenrec + 1, : nr + 1]) * TWOPI)
            if key == (0, 0):
                sumrec -= xstotinc
            # binemissum (binary.f90:349-363)
            nd = int(ent.get("nendisc", ie))
            bsum = float(np.sum(xsb[ib:nd + 1] * de[ib:nd + 1])) if ie >= ib else 0.0
            nl = int(ent["nlast"])
            le = list(ent.get("lines_e") or [])
            if nl < len(le) and float(le[nl]) > 0.0 and nd < E:
                bsum -= xsb[nd] * (et[nd] - float(le[nl]))
            sums[t] = (bsum, sumej, sumrec)
        for t, (bsum, sumej, sumrec) in sums.items():
            key = (PARZ[t], PARN[t])
            n = nuc[key]
            if t in ejg:
                rn = 1.0 if sumej <= 1.0e-14 else bsum / sumej
                k = ejg[t]["ixmax"]
                ejg[t]["ddx"][1: k + 1] *= rn
            rn = 1.0 if sumrec <= 1.0e-14 else bsum / sumrec
            rows = n["maxex"] + 1
            keep = None
            if t == 0:
                keep = (n["ddxrec"][mx0, irecinit, 0], n["ddxrectot"][mx0])
            n["ddxrectot"][:rows] *= rn
            n["ddxrec"][:rows] *= rn
            if keep is not None:
                n["ddxrec"][mx0, irecinit, 0], n["ddxrectot"][mx0] = keep
    # --- angdisrecoil (angdis.f90:161)
    nangle = int(_DISCAD.get("_nangle", s["nangle"]))
    if nangle != s["nangle"]:
        approx.append(f"E={e_inc:g}: discad on {nangle} angles, recoil grids on {s['nangle']}")
    for t in sorted(btypes):
        ent = btypes[t]
        key = (PARZ[t], PARN[t])
        n = nuc.get(key)
        if n is None:
            continue
        SS = float(S[0, 0, t])
        em, rm = parmass[t] * amu, M[key] * amu
        exg, mxx = n["ex"], n["maxex"]
        xsdisc = list(ent.get("lines_xs") or [])
        nl = int(ent["nlast"])
        xscm0 = xselastot if t == k0 else 0.0
        e = ejg.get(t)
        for nex in range(nl + 1):
            if nex != 0:
                xscm0 = 0.0
            xscmlev = xscm0 + (float(xsdisc[nex]) if nex < len(xsdisc) else 0.0)
            if nex > mxx:
                continue
            if nex == 0:
                # Ex(1) of a residual whose grid stops at its ground state is the first level (edis) when known
                le = list(ent.get("lines_e") or [])
                ex_1 = exg[1] if len(exg) > 1 else (etotal - SS - float(le[1]) if len(le) > 1 else 0.0)
                ex1, ex2 = exg[0], 0.5 * (ex_1 + exg[0])
            elif nex == mxx:
                # Exmax = real(sgl)(Etotal - S): Etotal - S - Exmax is the float32 rounding of Etotal - S, whose sign
                # decides whether TALYS keeps the residual's last level (Fe-56 at 1 MeV: level 1 dropped)
                ex2 = float(np.float32(float(np.float32(etotal)) - SS))
                ex1 = 0.5 * (ex2 + exg[nex - 1])
            else:
                ex1, ex2 = 0.5 * (exg[nex] + exg[nex - 1]), 0.5 * (exg[nex] + exg[nex + 1])
            et32 = float(np.float32(etotal))
            E1, E2 = et32 - SS - ex1, et32 - SS - ex2
            if E1 < 0.0 or E2 < 0.0:
                continue
            da = _DISCAD.get(f"{PARSYM[k0]}{PARSYM[t]}ang.L{nex:02d}")
            if da is None or row >= da.shape[0]:
                continue
            dad = np.asarray(da[row][: nangle + 1], float)
            if dad.size < nangle + 1:
                continue
            sumang = float(np.sum(dad * np.abs(g["cosangmin"] - g["cosangmax"]) * TWOPI))
            norm = np.ones(nangle + 1)
            xd = float(xsdisc[nex]) if nex < len(xsdisc) else 0.0
            if sumang > 1.0e-14:
                norm[0] = (xd + xselasinc) / sumang if (t == k0 and nex == 0) else xd / sumang
            flux = dad * g["dcosang"] * norm
            dis = None
            ej = None
            if e is not None:
                dis = np.zeros_like(e["ddx"])
                ej = dict(e, dep=dis, ren=e["ddx"])
            cells = cellrows(E1, E2, (g["cosangmin"], g["cosangmax"]), (g["sinangmin"], g["sinangmax"]), vcm0, flux,
                             1.0, nex, nex)
            scatter(cells, t, em, rm, n, True, ej, True)
            if dis is not None:
                rn = xscmlev / sumang if (sumang != xscmlev and sumang >= 1.0e-30) else 1.0
                k = e["ixmax"]
                e["ddx"][1: k + 1] += rn * dis[1: k + 1]
    # --- multiple: compemission.f90 with comprecoil.f90 per cell
    if s["flagspec"]:
        speceps = float(r.get("speceps", 0.0))
        ebegin = {t: int(v) for t, v in r["ebegin"].items()}
        eend = {t: int(v) for t, v in r["eend"].items()}
        Kmid = {t: specang.kalbach_shape(specang.kalbach_a(k0, t, e_inc, eg, sm), g["angmid"]) for t in range(7)}
        for key in sorted(r.get("walks", {})):
            rec = r["walks"][key]
            if rec.get("lines_only"):
                continue
            _comprecoil_nucleus(rec, key, nuc, ejg, s, g, eg, eb, et, de, ebegin, eend, speceps, Kmid, approx)
    # --- totalrecoil
    out_nuc = {}
    for key, n in nuc.items():
        top = max(n["nlast"], 1)
        rows = min(top + 1, n["ddxrec"].shape[0])
        dE = np.abs(n["Erecmax"][: maxenrec + 1] - n["Erecmin"][: maxenrec + 1])
        dE = np.where(dE <= 1.0e-14, 1.0, dE)
        sm_ = (n["ddxrec"][:rows] * n["area"][None, : maxenrec + 1, : nr + 1]).sum(axis=(0, 2)) * TWOPI
        out_nuc[key] = dict(E=n["Erec"][: maxenrec + 1].copy(), spec=sm_ / dE, integral=float(sm_.sum()))
    out_ej = {}
    for t, e in ejg.items():
        k = e["ixmax"]
        xs = (e["ddx"][1: k + 1] * cont["dcos"][None, : nc + 1]).sum(axis=1) * TWOPI
        out_ej[t] = dict(E=e["E"][1: k + 1].copy(), spec=xs, integral=float(np.sum(xs * e["dE"][1: k + 1])),
                         ddx=e["ddx"][1: k + 1].copy())
    return dict(approx=approx, nuclei=out_nuc, ej=out_ej, xselasinc=xselasinc, xselastot=xselastot, deltae=de)


def _comprecoil_nucleus(rec, key, nuc, ejg, s, g, eg, eb, et, de, ebegin, eend, speceps, Kmid, approx) -> None:
    """compemission.f90 for one cascade nucleus (the same cells as specout.compemission_py) with comprecoil.f90 on
    every (nex, type, nexout) cell."""
    from physics.hf.specout import _locate

    zc, ncc = key
    par = nuc.get(key)
    if par is None:
        return
    E = len(eg)
    amu, M, parmass = s["amu"], s["mass"], s["parmass"]
    maxenrec, nr, nc = s["maxenrec"], s["nanglerec"], s["nanglecont"]
    cont = g["cont"]
    ex, dex, sep = rec["ex"], rec["dex"], rec["sep"]
    maxex, nl0 = int(rec["maxex"]), int(rec["nlast"])
    T = rec["types"]
    compmass = M[zc, ncc] * amu
    vcmloc = np.sqrt(2.0 * np.maximum(par["Erec"][: maxenrec + 1], 0.0) / compmass)
    mcx = {t: np.asarray(e["mc"], float) + np.asarray(e["mpe"], float) for t, e in T.items()}

    def mcv(t, a, b_):
        m = mcx[t]
        if a < 0 or b_ < 0 or a >= m.shape[0] or b_ >= m.shape[1]:
            return 0.0
        return float(m[a, b_])

    for nex in range(maxex, nl0, -1):
        exinc, dexinc = float(ex[nex]), float(dex[nex])
        ex0plus, ex0min = exinc + 0.5 * dexinc, exinc - 0.5 * dexinc
        nexmax = {}
        for t, e in T.items():
            if t == 0:
                continue
            exm = ex0plus - float(sep[t])
            if t > 1:
                exm -= float(eg[ebegin[t]])
            nexmax[t] = -1
            for nexout in range(int(e["maxex"]), -1, -1):
                if nexout >= len(e["ex"]):
                    continue
                if float(e["ex"][nexout]) - 0.5 * float(e["dex"][nexout]) < exm:
                    nexmax[t] = nexout
                    break
        nexmax[0] = nex - 1
        # the mother's recoil distribution (comprecoil.f90:194-221), the same for every daughter cell
        tot = par["ddxrectot"][nex] if nex < par["ddxrectot"].size else 0.0
        if tot > 0.0:
            frac = (par["ddxrec"][nex] * par["area"][: maxenrec + 1, : nr + 1]).sum(axis=1) / tot
        else:
            frac = np.zeros(maxenrec + 1)
        for t in sorted(T):
            e = T[t]
            nxm = nexmax.get(t, -1)
            if nxm < 0 or ebegin[t] >= eend[t]:
                continue
            dkey = (zc + PARZ[t], ncc + PARN[t])
            dn = nuc.get(dkey)
            if dn is None:
                continue
            NL = int(e["nlast"])
            SS = float(sep[t])
            exd, dexd = e["ex"], e["dex"]
            em, rm = parmass[t] * amu, M[dkey] * amu
            if s["recoilav"] and t > 0:
                vlist, flist = [float(np.sum(frac * vcmloc))], [1.0]
            else:
                vlist, flist = list(vcmloc), list(frac)
            ej = None
            if t in ejg:
                ej = dict(ejg[t], dep=ejg[t]["ddx"], ren=ejg[t]["ddx"])
            for nexout in range(0, nxm + 1):
                if nexout == 0 and NL == 0:
                    continue
                xso00 = mcv(t, nex, nexout)
                if xso00 <= speceps:
                    continue
                exout, dEx = float(exd[nexout]), float(dexd[nexout])
                if nexout > NL:
                    ex1min, ex1plus = exout - 0.5 * dEx, exout + 0.5 * dEx
                    if nexout == nxm and t >= 1:
                        ex1plus = ex0plus - SS
                        exout = 0.5 * (ex1plus + ex1min)
                    emin = max(ex0min - SS - ex1plus, 0.0)
                    emax = ex0plus - SS - ex1min
                    eout = 0.5 * (emin + emax)
                    exm = 0.0
                else:
                    exm = exout + SS
                    if ex0min < exm <= ex0plus:
                        eout = 0.5 * (ex0plus + exm) - SS - exout
                        emin = 0.0
                    else:
                        eout = exinc - SS - exout
                        emin = ex0min - SS - exout
                    emax = ex0plus - SS - exout
                nenbeg = max(_locate(eb, ebegin[t], eend[t], emin), 1)
                nenend = _locate(eb, ebegin[t], eend[t], emax)
                if nenend < nenbeg:
                    continue
                dE = emax - emin
                dEhalf = 0.5 * dE
                xsom0, xsop0 = mcv(t, nex - 1, nexout), mcv(t, nex + 1, nexout)
                weight = np.zeros(E)
                if nexout > NL:
                    xso0m, xsopm = mcv(t, nex, nexout - 1), mcv(t, nex + 1, nexout - 1)
                    xsomp, xso0p = mcv(t, nex - 1, nexout + 1), mcv(t, nex, nexout + 1)
                    for nen in range(nenbeg, nenend + 1):
                        if eg[nen] <= eout:
                            edist = eout - eg[nen]
                            if emin <= 0.0001:
                                term = xso00 * (1.0 - edist / dEhalf)
                            else:
                                term1 = xso00 + 0.5 * edist / dE * (xsom0 - xso00)
                                term2 = xso0p + 0.5 * edist / dE * (xsomp - xso0p)
                                term = term1 + 0.5 * edist / dE * (term2 - term1)
                        else:
                            edist = eg[nen] - eout
                            if xsop0 == 0.0:
                                term1, term2 = xso00 * (1.0 - 0.5 * edist / dEhalf), 0.0
                            else:
                                term1 = xso00 + 0.5 * edist / dE * (xsop0 - xso00)
                                term2 = xso0m + 0.5 * edist / dE * (xsopm - xso0m)
                            term = term1 + 0.5 * edist / dE * (term2 - term1)
                        weight[nen] = max(term, 0.0) * de[nen]
                else:
                    inside = ex0min < exm <= ex0plus
                    for nen in range(nenbeg, nenend + 1):
                        if eg[nen] <= eout:
                            edist = eout - eg[nen]
                            term = xso00 * (1.0 - edist / dEhalf) if inside else xso00 + edist / dE * (xsom0 - xso00)
                        else:
                            edist = eg[nen] - eout
                            term = (xso00 * (1.0 - edist / dEhalf) if xsop0 == 0.0
                                    else xso00 + edist / dexinc * (xsop0 - xso00))
                        weight[nen] = max(term, 0.0) * de[nen]
                fracbot = (emin - eb[nenbeg]) / de[nenbeg]
                fractop = (et[nenend] - emax) / de[nenend]
                if nexout == NL + 1:
                    fractop = 0.0
                if nenend == nenbeg:
                    weight[nenbeg] *= 1.0 - fracbot - fractop
                else:
                    weight[nenbeg] *= 1.0 - fracbot
                    weight[nenend] *= 1.0 - fractop
                sumweight = float(np.sum(weight[nenbeg:nenend + 1]))
                if sumweight == 0.0:
                    continue
                mpe = np.asarray(e["mpe"], float)
                fracmpe = float(mpe[nex, nexout]) / xso00 if nexout < mpe.shape[1] and nex < mpe.shape[0] else 0.0
                sl = slice(nenbeg, nenend + 1)
                emisfac = (xso00 / sumweight) * weight[sl] / de[sl]
                comp, pre = (1.0 - fracmpe) * emisfac, fracmpe * emisfac
                # comprecoil.f90: the CM DDX of the cell and its LAB scatter
                gad = comp[:, None] / FOURPI + pre[:, None] * Kmid[t][sl]
                nens = np.arange(nenbeg, nenend + 1)
                keepn = (comp + pre) != 0.0
                E1 = np.where(eb[sl] == 0.0, 0.5 * eg[1], eb[sl])
                E2 = et[sl]
                blocks = []
                for vcm, fr in zip(vlist, flist):
                    if fr == 0.0:
                        continue
                    for j in np.flatnonzero(keepn):
                        flux = gad[j, : nc + 1] * (E2[j] - E1[j]) * cont["dcos"][: nc + 1] * fr
                        if not np.any(flux):
                            continue
                        blk = np.empty((nc + 1, 11))
                        blk[:, 0], blk[:, 1] = E1[j], E2[j]
                        blk[:, 2], blk[:, 3] = cont["cmin"][: nc + 1], cont["cmax"][: nc + 1]
                        blk[:, 4], blk[:, 5] = cont["smin"][: nc + 1], cont["smax"][: nc + 1]
                        blk[:, 6], blk[:, 7], blk[:, 8], blk[:, 9], blk[:, 10] = vcm, flux, 1.0, nexout, nexout
                        blocks.append(blk)
                del nens
                if blocks:
                    scatter(np.vstack(blocks), t, em, rm, dn, False, ej, False)


# ------------------------------------------------------------------------------------------------ the run
def _lab_name(x: str, kind: str, v: float) -> str:
    v32 = float(np.float32(v))
    if kind == "A":
        return f"{x}ddxA{int(v32):03d}{f'{v32:5.1f}'[3:]}.lab"
    return f"{x}ddxE{int(v32):04d}{f'{v32:6.1f}'[4:]}.lab"


def build(res=None) -> dict[str, np.ndarray]:
    """The Results.recoil arrays of the recorded run (see module doc); fills META for `write_files`.

    TALYS: totalrecoil.f90:1, recoilout.f90:1, channelsout.f90:811-890, spectraout.f90:165-197, ddxout.f90:200-245, :338-380
    Test: tests/hf/test_kwcov_b12.py
    """
    from physics.hf import specobs, specout

    s = _SET
    META.clear()
    if s is None or not specout.ENERGIES:
        return {}
    ens = specout.ENERGIES
    C = len(ens)
    k0 = s["k0"]
    e_inc = np.array([float(r["e_inc_mev"]) for r in ens])
    per, approx = [], []
    for i, r in enumerate(ens):
        if "egrid" not in r or not r.get("binary"):
            per.append(None)
            continue
        try:
            p = energy_recoil(r, s, i)
        except Exception as exc:  # noqa: BLE001 -- output only
            approx.append(f"E={e_inc[i]:g}: recoil {type(exc).__name__}: {exc}")
            p = None
        per.append(p)
        if p:
            approx += p["approx"]

    def _np(v):
        return np.asarray(v.detach().cpu().numpy() if hasattr(v, "detach") else v, float)

    rp = {k: _np(v) for k, v in (getattr(res, "residual_production_mb", {}) or {}).items()} if res is not None else {}
    ch = {k: _np(v) for k, v in (getattr(res, "channels_mb", {}) or {}).items()} if res is not None else {}
    Zc, Ac = s["Zinit"], s["Zinit"] + s["Ninit"]
    out: dict[str, np.ndarray] = {}
    present: dict[str, np.ndarray] = {}
    M = s["maxenrec"] + 1
    xseps = s["xseps"]
    pop = {}  # (zix, nix) -> xspopnuc (C,)
    for zix in range(s["maxZ"] + 1):
        for nix in range(s["maxN"] + 1):
            Z, A = Zc - zix, Ac - zix - nix
            v = rp.get(f"rp{Z:03d}{A:03d}")
            if v is not None:
                pop[(zix, nix)] = v
    targ = (PARZ[k0], PARN[k0])
    if targ not in pop:  # a charged projectile's run books no rp file for the target itself: its xspopnuc is the
        # inelastic population, which the recoil of the target's own levels carries (recoilout.f90 prints the file when
        # xspopnuc >= xseps; here when the target got any recoil)
        inel = np.zeros(C)
        for i, p in enumerate(per):
            q = p["nuclei"].get(targ) if p else None
            if q is not None and q["integral"] > 0.0:
                inel[i] = max(q["integral"] - p["xselastot"], xseps)
        pop[targ] = inel
    for (zix, nix), v in sorted(pop.items()):
        Z, A = Zc - zix, Ac - zix - nix
        name = f"rec{Z:03d}{A:03d}spec.tot"
        spec, En = np.full((C, M), np.nan), np.full((C, M), np.nan)
        integ, prod = np.full(C, np.nan), np.full(C, np.nan)
        for i, p in enumerate(per):
            if p is None or i >= v.size or v[i] < xseps:
                continue
            q = p["nuclei"].get((zix, nix))
            if q is None:
                q = dict(E=np.zeros(M), spec=np.zeros(M), integral=0.0)
            spec[i], En[i], integ[i] = q["spec"], q["E"], q["integral"]
            prod[i] = v[i] + (p["xselasinc"] if (zix, nix) == targ else 0.0)
        if np.all(np.isnan(integ)):
            continue
        out[name], out[name + ":E"], out[name + ":integral"], out[name + ":production"] = spec, En, integ, prod
        present[name] = ~np.isnan(integ)
    # exclusive recoil spectra (channelsout.f90:811-890): specrecoil x xschannel / xspopnuc
    import re

    for key, xs in sorted(ch.items()):
        m = re.fullmatch(r"xs(\d)(\d)(\d)(\d)(\d)(\d)", key)
        if not m:
            continue
        nn, npp, nd, nt, nh, na = (int(x) for x in m.groups())
        if nn + npp + nd + nt + nh + na > s["maxchannel"]:
            continue
        zix, nix = npp + nd + nt + 2 * nh + 2 * na, nn + nd + 2 * nt + nh + 2 * na
        v = pop.get((zix, nix))
        name = f"sp{key[2:]}.rec"
        spec, En = np.full((C, M), np.nan), np.full((C, M), np.nan)
        for i, p in enumerate(per):
            if p is None or i >= xs.size or xs[i] < xseps:
                continue
            q = p["nuclei"].get((zix, nix))
            ratio = xs[i] / v[i] if (v is not None and i < v.size and v[i] > 0.0) else 0.0
            spec[i] = (q["spec"] if q is not None else np.zeros(M)) * ratio
            En[i] = q["E"] if q is not None else np.zeros(M)
        if np.all(np.isnan(spec)):
            continue
        out[name], out[name + ":E"] = spec, En
        present[name] = ~np.isnan(spec[:, 0])
    # LAB spectra and DDX (labddx y)
    if s["labddx"]:
        nc = s["nanglecont"]
        th = specobs.anglecont(nc)
        for t in range(7):
            x = PARSYM[t]
            rows = [p["ej"].get(t) if p else None for p in per]
            if not any(rows):
                continue
            W = max(q["E"].size for q in rows if q)
            spec, En = np.full((C, W), np.nan), np.full((C, W), np.nan)
            dd = np.full((C, W, nc + 1), np.nan)
            integ = np.full(C, np.nan)
            for i, q in enumerate(rows):
                if q is None:
                    continue
                n_ = q["E"].size
                spec[i, :n_], En[i, :n_], dd[i, :n_], integ[i] = q["spec"], q["E"], q["ddx"], q["integral"]
            stem = f"{x}spec.lab"
            out[stem], out[stem + ":E"], out[stem + ":integral"] = spec, En, integ
            present[stem] = ~np.isnan(integ)
            out[f"{x}ddx.lab"], out[f"{x}ddx.lab:E"] = dd, En
            if t == 0:
                continue
            if s["ddxmode"] in (1, 3):
                for sym, enf in specobs._points(s["fileddxe"]):
                    if sym != x:
                        continue
                    name = _lab_name(x, "E", enf)
                    v = np.full((C, nc + 1), np.nan)
                    for i, q in enumerate(rows):
                        if q is None:
                            continue
                        Eo = q["E"]
                        k = Eo.size
                        # locate(Eo, 1, iejlab, enf) (1-based), fac with the CM grid's deltaE(nen) (ddxout.f90:212)
                        Eo1 = np.concatenate(([0.0], Eo))
                        from physics.hf.specout import _locate

                        nen = _locate(Eo1, 1, k, enf)
                        nen = min(max(nen, 0), k)
                        dEc = per[i]["deltae"]
                        fac = (enf - Eo1[nen]) / dEc[nen] if nen < dEc.size and dEc[nen] != 0.0 else 0.0
                        a = q["ddx"][nen - 1] if nen >= 1 else np.zeros(nc + 1)
                        b_ = q["ddx"][nen] if nen < k else np.zeros(nc + 1)
                        v[i] = a + fac * (b_ - a)
                    out[name] = v
                    present[name] = present[stem]
            if s["ddxmode"] in (2, 3):
                anginc = 180.0 / nc
                for sym, angf in specobs._points(s["fileddxa"]):
                    if sym != x:
                        continue
                    from physics.hf.specout import _locate

                    iang = _locate(th, 0, nc, angf)
                    iang = min(max(iang, 0), nc - 1)
                    fac = (angf - th[iang]) / anginc
                    name = _lab_name(x, "A", angf)
                    out[name] = dd[:, :, iang] + fac * (dd[:, :, iang + 1] - dd[:, :, iang])
                    out[name + ":E"] = En
                    present[name] = present[stem]
        out["anglecont"] = th
    META.update(Z=int(s["Z"]), A=int(s["A"]), k0=k0, e_inc_mev=e_inc, present=present, approx=sorted(set(approx)),
                settings={k: v for k, v in s.items() if k not in ("mass", "sep")})
    return out


def add_to_results(res, injection=None):
    """End of engine.run / engine_c.run (called by specobs.add_to_results before the recorders are cleared):
    Results.recoil from the recorded run (and the TALYS files with INCOGNITA_RECOIL_DIR). Unchanged with `recoil n`.

    TALYS: recoilout.f90:1, channelsout.f90:811-890, spectraout.f90:165-197, ddxout.f90:200-245, :338-380
    Test: tests/hf/test_kwcov_b12.py
    """
    if _SET is None:
        return res
    from dataclasses import replace

    import torch

    try:
        arr = build(res)
        out_dir = os.environ.get(ENV_DIR, "").strip()
        if out_dir and arr:
            write_files(arr, META, out_dir)
        res = replace(res, recoil={k: torch.as_tensor(v, dtype=torch.float64) for k, v in arr.items()})
    finally:
        end_run()
    return res


# ------------------------------------------------------------------------------------------------ TALYS files
def _efile(e: float) -> str:
    e32 = float(np.float32(e))
    return f"{int(e32):04d}{f'{e32:8.3f}'[4:]}"


def _write(path: Path, title: str, meta: dict, params: list, cols: tuple, units: tuple, rows: np.ndarray) -> None:
    from physics.hf.specobs import _header

    with open(path, "w") as f:
        _header(f, title, meta["Z"], meta["A"], meta["reaction"], 6, 5, params)
        f.write(f"#   datablock: \n#     columns: {len(cols)}\n#     entries: {rows.shape[0]}\n")
        f.write("##" + "".join(f"{c:>15s}" for c in cols)[2:] + "\n")
        f.write("##" + "".join(f"{'[' + u + ']':>15s}" for u in units)[2:] + "\n")
        for r in rows:
            f.write("".join(f"{v:15.6E}" for v in r) + "\n")


def write_files(arr: dict, meta: dict, out_dir) -> list[str]:
    """The recoil / LAB files with TALYS's names (one per energy; blockspectra / blockddx are not merged here).

    TALYS: recoilout.f90:1, channelsout.f90:845-885, spectraout.f90:165-197, ddxout.f90:200-245, :338-380
    Test: tests/hf/test_kwcov_b12.py
    """
    d = Path(out_dir)
    d.mkdir(parents=True, exist_ok=True)
    k0 = meta["k0"]
    written = []
    for i, e in enumerate(meta["e_inc_mev"]):
        ef = _efile(e)
        for name, pr in meta["present"].items():
            if not pr[i]:
                continue
            base = dict(Z=meta["Z"], A=meta["A"])
            if name.startswith("rec"):
                fn = f"{name[:9]}spec{ef}.tot"
                rows = np.column_stack([arr[name + ":E"][i], arr[name][i]])
                params = [("E-incident [MeV]", e), ("Integrated recoil spectrum [mb]", arr[name + ":integral"][i]),
                          ("Residual production cross section [mb]", arr[name + ":production"][i])]
                title = f"recoil emission spectrum at {e:12.6E} MeV"
                base["reaction"] = f"({PARSYM[k0]},x)"
            elif name.startswith("sp"):
                fn = f"{name[:8]}E{ef}.rec"
                rows = np.column_stack([arr[name + ":E"][i], arr[name][i]])
                params = [("E-incident [MeV]", e)]
                title = f"recoil spectrum - exclusive at {e:12.6E} MeV"
                base["reaction"] = name[:8]
            elif name.endswith("spec.lab"):
                x = name[0]
                v, En = arr[name][i], arr[name + ":E"][i]
                ok = ~np.isnan(v)
                fn = f"{x}spec{ef}.lab"
                rows = np.column_stack([En[ok], v[ok]])
                params = [("E-incident [MeV]", e), ("Energy-integrated cross section [mb]", arr[name + ":integral"][i])]
                title = f"emission spectrum in LAB frame at {e:12.6E} MeV"
                base["reaction"] = f"({PARSYM[k0]},x{x})"
            elif ".lab" in name and "ddxE" in name:
                x = name[0]
                fn = f"{x}ddxE{ef}{name[4:]}"
                rows = np.column_stack([arr["anglecont"], arr[name][i]])
                params = [("E-incident [MeV]", e)]
                title = f"double-differential cross section in LAB frame at {e:12.6E} MeV"
                base["reaction"] = f"({PARSYM[k0]},x{x})"
            elif ".lab" in name and "ddxA" in name:
                x = name[0]
                v, En = arr[name][i], arr[name + ":E"][i]
                ok = ~np.isnan(v)
                fn = f"{x}ddxE{ef}{name[4:]}"
                rows = np.column_stack([En[ok], v[ok]])
                params = [("E-incident [MeV]", e)]
                title = f"double-differential cross section in LAB frame at {e:12.6E} MeV"
                base["reaction"] = f"({PARSYM[k0]},x{x})"
            else:
                continue
            title = f"{base['reaction']} {title}"
            cols = ("Angle", "xs") if "ddxE" in name else ("E-out", "xs")
            units = ("deg", "mb/MeV/sr") if "ddxE" in name else ("MeV", "mb/MeV/sr" if "ddx" in name else "mb/MeV")
            _write(d / fn, title, base, params, cols, units, rows)
            written.append(fn)
    return written
