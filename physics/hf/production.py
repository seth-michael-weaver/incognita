"""KWCOV B11: medical isotope production (TALYS `production y`): yields, activities and numbers of produced isotopes.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

`production y` (with `Ebeam`, optional `Eback`, `Ibeam`, `Area`, `rho`, `Tirrad`, `Tcool`, `radiounit`, `yieldunit`)
makes TALYS fold the residual production cross sections of the run over a thick target that slows the beam from
Ebeam to Eback (Bethe-Bloch stopping power), turn them into production rates per target atom, and solve the
irradiation/cooling equations (target depletion, decay, one generation of beta feeding) on a 100-point time grid
(prodyield). It writes `Y<ZZZ><AAA>.tot|.L<NN>` per produced nuclide and a summary in talys.out (prodout). This
module is that bookkeeping on an engine run: the residual production (`Results.residual_production_mb`, rpZZZAAA and
the RESISO isomer keys rpZZZAAA.LNN) and the non-elastic cross section, rounded to the es15.6 of TALYS's rp files,
which prodres.f90 reads back. Nothing here runs unless the run's Options say `production y`.

TALYS routines ported here (file:line of the subroutine statement):
    input_medical.f90:1 (input_medical)  defaults and the Tirrad/Tcool value-unit pairs
    checkvalue.f90:1 (checkvalue)        lines 497-552: the medical checks (neutrons/photons refused as in TALYS)
    prodinitial.f90:1 (prodinitial)      density table, irradiation and cooling times
    decaydata.f90:1 (decaydata)          half-lives and decay types from structure/decay (JEFF-3.1.1, ENDF-6 MF8)
    prodres.f90:1 (prodres)              residual production and the non-elastic (minus the target's own) on file
    stoppingpower.f90:1 (stoppingpower)  Bethe-Bloch
    prodrates.f90:1 (prodrates)          production rates (100-point midpoint rule over Eback..Ebeam)
    prodyield.f90:1 (prodyield)          numbers of isotopes, activities, yields, isotopic fractions
    prodout.f90:1 (prodout)              summary rows and the Y files
    locate.f90:1 (locate), pol1.f90:1 (pol1)
TALYS quirks kept (ported as written): beta feeding is one generation and keeps the daughter's isomer index for the
parent; during cooling a beta- parent (Zix + 1) is processed after its daughter, so it feeds nothing (its Niso is
still 0); a nuclide counts as produced only if its rp file has xs > 0 on a grid point inside [Eback, Ebeam]; the
target's L00 file (if any) is subtracted from the non-elastic as well as its total; `Tcool 0` leaves the cooling
part of the time grid at 0 (TALYS then prints growing "cooling" numbers); a value/unit pair with a unit TALYS does
not know is refused (checkvalue), a pair with no unit counts zero seconds.
Task: T10 (physics/hf/CONTRACT.md section 7; KWCOV batch B11). Acceptance test: KWCOV-B11 (tests/hf/test_kwcov_b11.py).
"""
from __future__ import annotations

import math
import os
import warnings
from bisect import bisect_right
from pathlib import Path

import numpy as np

F32 = np.float32
NUMTIME = 100  # A0_talys_mod.f90:100
NUMENRP = 200  # A0_talys_mod.f90:104
NUMELEM = 124
# constants.f90:93, :118-125
PARMASS = (0.0, 1.00866491574, 1.00782495281, 2.01410195518, 3.01604916211, 3.01602879487, 4.00260293529)
PARZ = (0, 0, 1, 1, 1, 2, 2)
PARN = (0, 1, 0, 1, 2, 1, 2)
PARSYM = "gnpdtha"
AMU = 931.49410242
EMASS = 0.510998950
AVOGADRO = 6.02214076e23
QELEM = 1.602176634e-19
ISOCHAR = (" ", "g", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v")  # constants.f90:107, index is + 1
# decaydata.f90: time units (single precision)
MINUTESEC = float(F32(60.0))
HOURSEC = float(F32(3600.0))
DAYSEC = float(F32(86400.0))
YEARSEC = float(F32(365.25 * 86400.0))
RADIOUNITS = ("bq", "kbq", "mbq", "gbq", "mci", "ci", "kci")
YIELDUNITS = ("num", "mug", "mg", "g", "kg")
TIMEUNITS = (" ", "y", "d", "h", "m", "s")
# prodinitial.f90: default material densities by Z (g/cm^3)
RHOTABLE = (8.99e-5, 1.79e-4, 0.534, 1.85, 2.34, 2.267, 1.25e-3, 1.43e-3, 1.70e-3, 9.0e-3,
            0.97, 1.74, 2.7, 2.33, 1.82, 2.07, 3.21e-3, 1.78e-3, 0.86, 1.55, 2.99, 4.54, 6.11, 7.19, 7.43, 7.87, 8.9,
            8.9, 8.96, 7.13, 5.91, 5.32, 5.72, 4.79, 3.12, 3.75e-3, 1.53, 2.64, 4.47, 6.51,
            8.57, 10.22, 11.5, 12.37, 12.41, 12.02, 10.5, 8.65, 7.31, 7.31,
            6.68, 6.24, 4.93, 5.9e-3, 1.87, 3.59, 6.15, 6.77, 6.77, 7.01, 7.3, 7.52, 5.24, 7.9, 8.23, 8.55, 8.8, 9.07,
            9.32, 6.9, 9.84, 13.31, 16.65, 19.35, 21.04, 22.6, 22.4, 21.45, 19.32, 13.55,
            11.85, 11.35, 9.75, 9.3, 7.0, 9.73e-3, 1.87, 5.5, 10.07, 11.72,
            15.4, 18.95, 20.2, 19.84, 13.67, 13.5, 14.78, 15.1, 13.5, 13.5) + (13.5,) * 24


# ----------------------------------------------------------------------------------------------------------------------
# input


def parse_time(value) -> tuple[tuple, tuple]:
    """`tirrad 2 d 6 h` / `tcool 1 d`: up to five (integer, unit) pairs (input_medical.f90:127-150). The first pair
    is reset to (0, ' '); a non-integer value is skipped (TALYS's `istat > 0 cycle`); a missing unit is ' '.

    TALYS: input_medical.f90:1 (input_medical)
    Test: tests/hf/test_kwcov_b11.py
    """
    w = str(value).split() if not isinstance(value, (tuple, list)) else [str(x) for x in value]
    vals, units = [0, 0, 0, 0, 0], [" ", " ", " ", " ", " "]
    for k in range(5):
        a = w[2 * k] if 2 * k < len(w) else ""
        try:
            v = int(a) if a else 0
        except ValueError:
            continue
        if len(a) > 9:
            continue
        vals[k] = v
        u = w[2 * k + 1] if 2 * k + 1 < len(w) else ""
        units[k] = u[:1].lower() if u else " "
    return tuple(vals), tuple(units)


def settings(o) -> dict | None:
    """The run's medical input from its Options, None without `production y`.

    TALYS: input_medical.f90:1 (input_medical)
    Test: tests/hf/test_kwcov_b11.py
    """
    if not getattr(o, "flagprod", False):
        return None
    return dict(Area=float(o.Area), Eback=float(o.Eback), Ebeam=float(o.Ebeam), Ibeam=float(o.Ibeam),
                radiounit=str(o.radiounit), yieldunit=str(o.yieldunit), rhotarget=float(o.rhotarget),
                Tirrad=tuple(int(x) for x in o.Tirrad), unitTirrad=tuple(o.unitTirrad),
                Tcool=tuple(int(x) for x in o.Tcool), unitTcool=tuple(o.unitTcool))


def _range(name: str, v: float, lo: float, hi: float, unit: str = "") -> None:
    if v < lo or v > hi:
        raise ValueError(f"TALYS-error: {lo} <= {name} <= {hi}{' ' + unit if unit else ''}, {name} = {v}")


def check(m: dict, k0: int, eninc: tuple, emaxtalys: float = 1.0e6) -> dict:
    """checkvalue.f90:497-552 on the medical input; returns it with the Eback default filled in.

    TALYS: checkvalue.f90:1 (checkvalue)
    Test: tests/hf/test_kwcov_b11.py
    """
    m = dict(m)
    if k0 <= 1:
        raise NotImplementedError("TALYS-error: isotope production not yet enabled for incident photons or neutrons "
                                  "(checkvalue.f90:498; `production y` needs a charged projectile)")
    if m["Ebeam"] == -1.0:
        raise ValueError("TALYS-error: accelerator energy Ebeam must be given for isotope production (production y)")
    _range("Ebeam", m["Ebeam"], 0.0, emaxtalys, "MeV")
    if m["Eback"] == -1.0:
        m["Eback"] = float(F32(max(m["Ebeam"] - 5.0, 0.1)))
    else:
        _range("Eback", m["Eback"], 0.0, emaxtalys, "MeV")
    _range("Ebeam", m["Ebeam"], m["Eback"], emaxtalys, "MeV")
    if m["Ebeam"] > max(eninc) + 1.0e-4:
        raise ValueError(f"TALYS-error: Ebeam is not in the energy range with TALYS results, Ebeam = {m['Ebeam']:.5f}"
                         f" Ein(max) = {max(eninc):.5f}. Rerun with wider energy grid")
    if m["Eback"] < min(eninc) - 1.0e-4:
        raise ValueError(f"TALYS-error: Eback is not in the energy range with TALYS results, Eback = {m['Eback']:.5f}"
                         f" Ein(1) = {min(eninc):.5f}. Rerun with wider energy grid")
    if m["radiounit"] not in RADIOUNITS:
        raise ValueError("TALYS-error: radiounit should be equal to Bq, kBq, MBq, Gbq, mCi, Ci or kCi")
    if m["yieldunit"] not in YIELDUNITS:
        raise ValueError("TALYS-error: yieldunit should be equal to num (number), mug (micro-gram), mg, g, or kg")
    _range("Ibeam", m["Ibeam"], 0.0, 10000.0, "mA")
    _range("Area", m["Area"], 0.0, 10000.0, "cm^2")
    for k in range(5):
        _range("Tirrad", m["Tirrad"][k], 0, 1000000)
        _range("Tcool", m["Tcool"][k], 0, 1000000)
    for k in range(5):
        if m["unitTirrad"][k] not in TIMEUNITS:
            raise ValueError(f"TALYS-error: wrong unit for Tirrad = {m['Tirrad'][k]}")
        if m["unitTcool"][k] not in TIMEUNITS:
            raise ValueError(f"TALYS-error: wrong unit for Tcool = {m['Tcool'][k]}")
    if m["rhotarget"] != -1.0:
        _range("rhotarget", m["rhotarget"], 0.0, 100.0)
    return m


def _seconds(vals, units) -> float:
    t = F32(0.0)
    for v, u in zip(vals, units):  # noqa: B905
        f = {"y": YEARSEC, "d": DAYSEC, "h": HOURSEC, "m": MINUTESEC, "s": 1.0}.get(u)
        if f is not None:
            t = F32(t + F32(f) * F32(v))
    return float(t)


def _split(t: float) -> tuple[int, int, int, int, int]:
    """Seconds as (years, days, hours, minutes, seconds), TALYS's int() cascade."""
    tt = float(F32(t))
    out = []
    for f in (YEARSEC, DAYSEC, HOURSEC, MINUTESEC):
        n = int(tt / f)
        out.append(n)
        tt = tt - n * f
    out.append(int(tt))
    return tuple(out)


def prodinitial(m: dict, Ztarget: int) -> dict:
    """Target density (table by Z when rho is not given), Tir / Tco in seconds and their (y, d, h, m, s) form.

    TALYS: prodinitial.f90:1 (prodinitial)
    Test: tests/hf/test_kwcov_b11.py
    """
    rho = m["rhotarget"] if m["rhotarget"] != -1.0 else RHOTABLE[Ztarget - 1]
    tir = _seconds(m["Tirrad"], m["unitTirrad"])
    tco = _seconds(m["Tcool"], m["unitTcool"])
    return dict(rho=float(F32(rho)), Tir=tir, Tco=tco, Tirrad=_split(tir), Tcool=_split(tco))


# ----------------------------------------------------------------------------------------------------------------------
# decay data


def _endf_float(s: str) -> float:
    s = s.strip()
    if not s:
        return 0.0
    try:
        return float(s)
    except ValueError:
        pass
    for i in range(len(s) - 1, 0, -1):
        if s[i] in "+-" and s[i - 1] not in "eEdD":
            return float(s[:i] + "e" + s[i:])
    return float(s.replace("d", "e").replace("D", "e"))


def decay_data(Zinit: int, Ninit: int, maxZ: int, maxN: int, structure: str | Path | None = None) -> dict:
    """{(Zix, Nix, is): (Thalf s, lambda 1/s, rtyp)} for Zix 0..maxZ, A in Z + Ninit - maxN .. Z + Ninit, from
    structure/decay/<El>.decay; absent = (1e30, 0, 0) (strucinitial.f90:506-510). is = -1 total/ground, 0 ground
    (copied), 1 'M', 2 'N'; an isomer without decay data takes the ground state's (decaydata.f90's second loop).

    TALYS: decaydata.f90:1 (decaydata)
    Test: tests/hf/test_kwcov_b11.py
    """
    from physics.hf.core.constants import nuclide_symbol

    if structure is None:
        from physics.hf.structure.files import talys_structure_dir

        structure = talys_structure_dir()
    out: dict = {}
    for Zix in range(0, maxZ + 1):
        Z = min(Zinit - Zix, NUMELEM)
        Abegin, Aend = Z + Ninit - maxN, Z + Ninit
        f = Path(structure) / "decay" / f"{nuclide_symbol(Z)}.decay"
        if not f.is_file():
            continue
        lines = f.read_text(errors="replace").splitlines()
        i, n = 0, len(lines)
        while i < n:
            s = lines[i].ljust(80)
            i += 1
            if s[71:80] != "1451    5":
                continue
            ia = int(s[7:10])
            if ia < Abegin:
                continue
            if ia > Aend:
                break
            Nix = Ninit - (ia - Z)
            iso = 1 if s[10] == "M" else 2 if s[10] == "N" else -1
            while i < n:
                s = lines[i].ljust(80)
                i += 1
                if s[71:80] == "8457    2":
                    break
            th = float(F32(_endf_float(s[0:11])))
            nc = int(s[44:55])
            i += 1 + (nc - 1) // 6 + 2  # the NC list lines, the decay-mode CONT line, then RTYP's line
            if i > n:
                break
            rt = int(_endf_float(lines[i - 1].ljust(80)[0:11]))
            if th == 0.0:
                th = 1.0e30
            lam = 0.0 if th > 1.0e17 else float(F32(math.log(F32(2.0)) / F32(th)))
            out[(Zix, Nix, iso)] = (th, lam, rt)
            if iso == -1:
                out[(Zix, Nix, 0)] = (th, lam, rt)
        for ia in range(Abegin, Aend + 1):
            Nix = Ninit - (ia - Z)
            if out.get((Zix, Nix, 1), (1.0e30,))[0] > 1.0e17:
                g = out.get((Zix, Nix, -1))
                if g is not None:
                    out[(Zix, Nix, 1)] = g
    return out


# ----------------------------------------------------------------------------------------------------------------------
# cross sections, rates


def _es156(x: float) -> float:
    """A value as TALYS's es15.6 writes it (prodres.f90 reads the rp files back)."""
    return float(f"{float(x):.6E}")


def residuals_from_results(res, Zinit: int, Ninit: int) -> tuple[dict, tuple]:
    """The rp files prodres.f90 reads, from an engine Results: {(Zix, Nix, lev): (E, xs)} with lev None for
    rpZZZAAA.tot and the file level number for rpZZZAAA.LNN (RESISO), plus the non-elastic (E, xs).

    TALYS: prodres.f90:1 (prodres) -- the files residual.f90 / residualout.f90 write
    Test: tests/hf/test_kwcov_b11.py
    """
    e = [_es156(x) for x in res.e_inc_mev.detach().cpu().numpy()]
    out = {}
    for k, v in res.residual_production_mb.items():
        if not k.startswith("rp"):
            continue
        Z, A = int(k[2:5]), int(k[5:8])
        lev = int(k.split(".L")[1]) if ".L" in k else None
        out[(Zinit - Z, Ninit - (A - Z), lev)] = (e, [_es156(x) for x in v.detach().cpu().numpy()])
    non = res.totals_mb["nonelastic"].detach().cpu().numpy()
    return out, (e, [_es156(x) for x in non])


def read_rp_dir(d: str | Path, Zinit: int, Ninit: int) -> tuple[dict, tuple]:
    """The same from a TALYS output directory (rpZZZAAA.tot / .LNN, nonelastic.tot): the port on stock's own
    cross sections.

    TALYS: prodres.f90:1 (prodres)
    Test: tests/hf/test_kwcov_b11.py
    """
    def table(p):
        e, x = [], []
        for ln in Path(p).read_text().splitlines():
            if not ln.strip() or ln.lstrip().startswith("#"):
                continue
            w = ln.split()
            e.append(float(w[0]))
            x.append(float(w[1]))
        return e, x

    d = Path(d)
    out = {}
    for p in sorted(d.glob("rp[0-9][0-9][0-9][0-9][0-9][0-9].*")):
        suf = p.name[9:]
        if suf == "tot":
            lev = None
        elif suf.startswith("L") and suf[1:].isdigit():
            lev = int(suf[1:])
        else:
            continue
        Z, A = int(p.name[2:5]), int(p.name[5:8])
        out[(Zinit - Z, Ninit - (A - Z), lev)] = table(p)
    return out, table(d / "nonelastic.tot")


def prodres(rp: dict, nonel: tuple, Zinit: int, Ninit: int, Ztarget: int, Atarget: int, Eback: float,
            Ebeam: float) -> tuple[dict, dict, dict, dict]:
    """(xsrp {(Zix, Nix, is): (E, xs) float32}, prodexist, Nisomer {(Zix, Nix): n}, Lisomer {(Zix, Nix, is): lev}).
    is = -1 the total, 0 L00, 1.. the isomers in level order. (-1, -1, -1) = non-elastic minus the target's own rp
    (tot and L00).

    TALYS: prodres.f90:1 (prodres)
    Test: tests/hf/test_kwcov_b11.py
    """
    def clip(e, x, name):
        if len(e) > NUMENRP:
            warnings.warn(f"TALYS-warning: number of energy points exceeds {NUMENRP}, incomplete integration ({name})",
                          stacklevel=3)
        return np.asarray(e[:NUMENRP], dtype=F32), np.asarray(x[:NUMENRP], dtype=F32)

    xsrp, exist, nis, lis = {}, {}, {}, {}
    e0, x0 = clip(*nonel, "nonelastic.tot")
    x0 = x0.copy()
    xsrp[(-1, -1, -1)] = (e0, x0)
    exist[(-1, -1, -1)] = True
    levs: dict = {}
    for (zix, nix, lev) in rp:
        levs.setdefault((zix, nix), set()).add(lev)
    for (zix, nix) in sorted(levs):
        iso = sorted(v for v in levs[(zix, nix)] if v is not None and v > 0)
        nis[(zix, nix)] = len(iso)
        Z = Zinit - zix
        A = Z + Ninit - nix
        for i_s in range(-1, len(iso) + 1):
            lev = None if i_s == -1 else 0 if i_s == 0 else iso[i_s - 1]
            if i_s > 0:
                lis[(zix, nix, i_s)] = lev
            if lev not in levs[(zix, nix)]:
                continue
            e, x = clip(*rp[(zix, nix, lev)], f"rp{Z:03d}{A:03d}")
            pos = bool(np.any((e >= F32(Eback)) & (e <= F32(Ebeam)) & (x > 0)))
            xsrp[(zix, nix, i_s)] = (e, x)
            exist[(zix, nix, i_s)] = pos
            if Z == Ztarget and A == Atarget and i_s <= 0:
                m = min(len(x), len(x0))
                x0[:m] = (x0[:m] - x[:m]).astype(F32)
    return xsrp, exist, nis, lis


def stopping_power(E: np.ndarray, k0: int, Ztarget: int, Atarget: int, rho: float) -> np.ndarray:
    """Bethe-Bloch dE/dx (MeV/cm) of the projectile in the target material (Leo 1994, p. 24).

    TALYS: stoppingpower.f90:1 (stoppingpower)
    Test: tests/hf/test_kwcov_b11.py
    """
    E = np.asarray(E, dtype=np.float64)
    pmass = PARMASS[k0] * AMU
    beta = np.sqrt(E * (E + 2.0 * pmass) / (E + pmass) ** 2)
    imean = Ztarget * (9.76 + 58.8 * Ztarget ** (-1.19)) * 1.0e-6
    gam = 1.0 / np.sqrt(1.0 - beta ** 2)
    eta = beta * gam
    wmax = 2.0 * EMASS * eta ** 2
    term1 = 0.1535 * rho * Ztarget / float(Atarget) * PARZ[k0] ** 2 / beta ** 2
    term2 = np.log(2.0 * EMASS * eta ** 2 * wmax / imean ** 2) - 2.0 * beta ** 2
    return (term1 * term2).astype(F32)


def prodrates(xsrp: dict, exist: dict, m: dict, k0: int, Ztarget: int, Atarget: int, rho: float) -> tuple[dict, dict]:
    """Production rates prate {(Zix, Nix, is): 1/s per target atom} and the target numbers (thickness, volume, mass,
    heat, projectiles per second).

    TALYS: prodrates.f90:1 (prodrates), locate.f90:1 (locate), pol1.f90:1 (pol1)
    Test: tests/hf/test_kwcov_b11.py
    """
    ninte = 100
    eb, ek = F32(m["Ebeam"]), F32(m["Eback"])
    dE = F32((eb - ek) / F32(ninte))
    eint = (ek + (np.arange(ninte, dtype=F32) + F32(0.5)) * dE).astype(F32)
    dxde = (F32(1.0) / stopping_power(eint, k0, Ztarget, Atarget, rho)).astype(F32)
    s = F32(0.0)
    for v in dxde:
        s = F32(s + v)
    targetdx = F32(s * dE)
    vtar = F32(F32(m["Area"]) * targetdx)
    info = dict(targetdx=float(targetdx), Vtar=float(vtar), Mtar=float(F32(F32(rho) * vtar)),
                heat=float(F32(F32(m["Ibeam"]) * (eb - ek))))
    projnum = F32(F32(m["Ibeam"]) / (F32(1000.0) * F32(PARZ[k0]) * F32(QELEM)))
    info["projnum"] = float(projnum)
    prate = {}
    for key, (e, x) in xsrp.items():
        prate[key] = 0.0
        if not exist.get(key) or len(e) == 0:
            continue
        n = len(e)
        el = e.tolist()
        rs = F32(0.0)
        for j in range(ninte):
            E = eint[j]
            if E < e[0]:
                continue
            if E > e[n - 1]:
                break
            nen = 1 if E == e[0] else n - 1 if E == e[n - 1] else bisect_right(el, float(E))
            ea, ebb, xa, xb = e[nen - 1], e[nen], x[nen - 1], x[nen]
            xs = xa if ebb == ea else F32(xa + (xb - xa) * (E - ea) / (ebb - ea))
            rs = F32(rs + dxde[j] * xs)
        prate[key] = float(F32(projnum / vtar * rs * dE * F32(1.0e-27)))
    return prate, info


# ----------------------------------------------------------------------------------------------------------------------
# yields


def time_grid(tir: float, tco: float) -> tuple[np.ndarray, int]:
    """Tgrid(0:numtime) in hours and Ntime (the end of irradiation).

    TALYS: prodyield.f90:1 (prodyield) lines 'Set time grid'
    Test: tests/hf/test_kwcov_b11.py
    """
    tg = np.zeros(NUMTIME + 1, dtype=F32)
    ntime = NUMTIME // 2
    th = float(F32(F32(tir) / F32(HOURSEC)))
    dT = th / ntime
    if dT <= 0.1:
        dT = 0.1
    if 0.1 < dT <= 0.2:
        dT = 0.2
    if 0.2 < dT <= 0.5:
        dT = 0.5
    if 0.5 < dT <= 1.0:
        dT = 1.0
    for it in range(0, ntime + 1):
        tg[it] = F32(it * dT)
        if abs(float(tg[it]) - th) < 1.0 / HOURSEC or float(tg[it]) > th:
            tg[it] = F32(th)
            ntime = it
            break
    if tco > 0.0:
        tc = float(F32(F32(tco) / F32(HOURSEC)))
        ncool = NUMTIME - ntime
        dT = math.log(tc + 1.0) / ncool
        for it in range(ntime + 1, NUMTIME + 1):
            tg[it] = F32(th + math.exp((it - ntime) * dT) - 1.0)
    return tg, ntime


def prodyield(prate: dict, decay: dict, nis: dict, m: dict, init: dict, info: dict, *, Zinit: int, Ninit: int,
              Ztarget: int, Atarget: int, maxZ: int, maxN: int) -> dict:
    """Numbers of isotopes, activities (MBq, then radiounit), yields (per mAh) and isotopic fractions on the time
    grid for every nuclide Zix 0..maxZ, Nix 0..maxN (is -1 always, isomers when produced).

    TALYS: prodyield.f90:1 (prodyield)
    Test: tests/hf/test_kwcov_b11.py
    """
    nt = NUMTIME + 1
    ntar0 = float(F32(F32(AVOGADRO) / F32(Atarget) * F32(init["rho"]) * F32(info["Vtar"])))
    tg, ntime = time_grid(init["Tir"], init["Tco"])
    TT = (tg * F32(HOURSEC)).astype(F32).astype(np.float64)
    tir = init["Tir"]
    irr = np.arange(nt) <= ntime
    irr[0] = False
    cool = np.arange(nt) > ntime
    prate0 = prate.get((-1, -1, -1), 0.0)
    lam = {k: v[1] for k, v in decay.items()}
    rtyp = {k: v[2] for k, v in decay.items()}
    Niso, act, yld, rel, nisotot = {}, {}, {}, {}, {}
    yexist, tmax, tp = {}, {}, {}
    ib = float(F32(m["Ibeam"]))
    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        for zix in range(0, maxZ + 1):
            Z = Zinit - zix
            tot = np.zeros(nt, dtype=F32)
            for nix in range(0, maxN + 1):
                A = Z + Ninit - nix
                for i_s in range(-1, nis.get((zix, nix), 0) + 1):
                    key = (zix, nix, i_s)
                    pratei = prate.get(key, 0.0)
                    if i_s >= 0 and pratei == 0.0:
                        continue
                    n = np.zeros(nt, dtype=F32)
                    a = np.zeros(nt, dtype=F32)
                    y = np.zeros(nt, dtype=F32)
                    is_target = Z == Ztarget and A == Atarget and i_s == -1
                    lamD = lam.get(key, 0.0)
                    if is_target:
                        n[0] = F32(ntar0)
                        tot[0] = F32(tot[0] + n[0])
                        n[irr] = (ntar0 * np.exp(-prate0 * TT[irr])).astype(F32)
                        n[cool] = n[ntime]
                    else:
                        denomD = lamD - prate0
                        C1 = ntar0 * pratei
                        expo1 = np.exp(-prate0 * TT)
                        expo2 = np.exp(-lamD * TT)
                        exp1 = expo1 / denomD - expo2 / denomD
                        n[irr] = (C1 * exp1[irr]).astype(F32)
                        parents = []
                        for isob in (-1, 1):
                            zp, np_ = zix - isob, nix + isob
                            if zp < 0 or np_ < 0:
                                continue
                            rt = rtyp.get((zp, np_, -1), 0)
                            if (isob == -1 and rt == 1) or (isob == 1 and rt == 2):
                                parents.append((zp, np_))
                        for zp, np_ in parents:  # irradiation
                            lamPD = lam.get((zp, np_, i_s), 0.0)
                            prateP = prate.get((zp, np_, i_s), 0.0)
                            if prateP > 0.0 and lamPD > 0.0:
                                CP1 = ntar0 * prateP
                                denom = lamD - lamPD
                                exp2 = np.exp(-lamPD * TT) / denom - expo2 / denom
                                term = lamPD * CP1 / (lamPD - prate0) * (exp1 - exp2)
                                n[irr] = (n[irr].astype(np.float64) + term[irr]).astype(F32)
                        dt = TT - tir
                        n[cool] = (float(n[ntime]) * np.exp(-lamD * dt[cool])).astype(F32)
                        for zp, np_ in parents:  # cooling only
                            lamPD = lam.get((zp, np_, i_s), 0.0)
                            N0 = float(Niso.get((zp, np_, i_s), np.zeros(nt, dtype=F32))[ntime])
                            denom = lamD - lamPD
                            if denom != 0.0:
                                term = N0 * lamPD / denom * (np.exp(-lamPD * dt) - np.exp(-lamD * dt))
                                n[cool] = (n[cool].astype(np.float64) + term[cool]).astype(F32)
                        a[1:] = (lamD * n[1:].astype(np.float64) * 1.0e-6).astype(F32)
                        for it in range(1, ntime + 1):
                            v = (float(a[it]) - float(a[it - 1])) / (ib * HOURSEC * float(F32(tg[it] - tg[it - 1])))
                            y[it] = F32(max(v, 0.0))
                    if np.any(n[1:] > 0):
                        yexist[key] = True
                    tot[1:] = (tot[1:] + n[1:]).astype(F32)
                    Niso[key], act[key], yld[key] = n, a, y
                    if not yexist.get(key):
                        continue
                    if lamD > 0.0 and prate0 > 0.0:
                        tm = float(F32(math.log(lamD / prate0) / (lamD - prate0)))
                    else:
                        tm = 1.0e30
                    tmax[key] = tm
                    tp[key] = _split(tm) if tm <= 1.0e17 else (0, 0, 0, 0, 0)
            nisotot[zix] = tot
            for key in [k for k in yexist if k[0] == zix]:
                rel[key] = np.where(tot != 0, Niso[key] / np.where(tot != 0, tot, 1), 0).astype(F32)
    rfac = {"bq": 1.0e6, "kbq": 1.0e3, "gbq": 1.0e-3, "ci": 1.0 / 3.7e4, "kci": 1.0 / 3.7e7,
            "mci": 1.0 / 3.7e1}.get(m["radiounit"], 1.0)
    tmaxact = {}
    for key in Niso:
        Z = Zinit - key[0]
        A = Z + Ninit - key[1]
        yfac = {"g": A / AVOGADRO, "mug": A / AVOGADRO * 1.0e6, "mg": A / AVOGADRO * 1.0e3,
                "kg": A / AVOGADRO * 1.0e-3}.get(m["yieldunit"], 1.0)
        rf, yf = F32(rfac), F32(yfac)
        act[key][1:] = (rf * act[key][1:]).astype(F32)
        yld[key][1:] = (rf * yld[key][1:]).astype(F32)
        Niso[key][1:] = (yf * Niso[key][1:]).astype(F32)
        best, acmax = 0, 0.0
        for it in range(1, NUMTIME + 1):
            if act[key][it] > acmax:
                best, acmax = it, float(act[key][it])
        tmaxact[key] = best
    return dict(Ntar0=ntar0, Tgrid=tg, Ntime=ntime, Niso=Niso, activity=act, yield_=yld, Nisorel=rel,
                Nisotot=nisotot, Yexist=yexist, Tmax=tmax, Tp=tp, Tmaxactivity=tmaxact, prate0=prate0)


# ----------------------------------------------------------------------------------------------------------------------
# output


def _tstring(t5) -> str:
    return " {:6d} years {:3d} days{:3d} hours{:3d} minutes{:3d} seconds ".format(*t5)


def prodout(y: dict, prate: dict, decay: dict, lis: dict, m: dict, init: dict, *, Zinit: int, Ninit: int,
            maxZ: int, maxN: int, nis: dict) -> dict:
    """Summary rows (talys.out) and the Y files: {"files": {name: {column: array}}, "params": {name: {...}},
    "summary": [...]}. Names Y<ZZZ><AAA>.tot (is -1), .L00 (is 0), .L<NN> (isomer level NN).

    TALYS: prodout.f90:1 (prodout)
    Test: tests/hf/test_kwcov_b11.py
    """
    from physics.hf.core.constants import nuclide_symbol

    rstr = {"bq": "Bq", "kbq": "KBq", "gbq": "GBq", "ci": "Ci", "kci": "KCi", "mci": "mCi"}.get(m["radiounit"], "MBq")
    ystr = {"g": "g", "mug": "mug", "mg": "mg", "kg": "kg"}.get(m["yieldunit"], "")
    files, params, summary = {}, {}, []
    for zix in range(0, maxZ + 1):
        Z = Zinit - zix
        for nix in range(0, maxN + 1):
            A = Z + Ninit - nix
            for i_s in range(-1, nis.get((zix, nix), 0) + 1):
                key = (zix, nix, i_s)
                if not y["Yexist"].get(key):
                    continue
                th, lam, _ = decay.get(key, (1.0e30, 0.0, 0))
                it = y["Tmaxactivity"][key]
                name = f"Y{Z:03d}{A:03d}." + ("tot" if i_s < 0 else "L00" if i_s == 0 else f"L{lis[key]:02d}")
                nuc = f"{nuclide_symbol(Z)}{A}{ISOCHAR[min(i_s, 10) + 1]}".strip()
                files[name] = {"Time": y["Tgrid"][1:].astype(np.float64), "Activity": y["activity"][key][1:].copy(),
                               "Isotopes": y["Niso"][key][1:].copy(), "Yield": y["yield_"][key][1:].copy(),
                               "Isotopic_fract.": y["Nisorel"][key][1:].copy()}
                params[name] = {
                    "nuclide": nuc, "Z": Z, "A": A, "isomer": i_s if i_s > 0 else None,
                    "Beam current [mA]": float(F32(m["Ibeam"])), "E-Beam [MeV]": float(F32(m["Ebeam"])),
                    "E-Back [MeV]": float(F32(m["Eback"])), "Initial production rate [s^-1]": prate.get(key, 0.0),
                    "Decay rate [s^-1]": lam, f"Initial production yield [{rstr}/mAh]": float(y["yield_"][key][1]),
                    f"Total activity at EOI [{rstr}]": float(y["activity"][key][y["Ntime"]]),
                    "Irradiation time": _tstring(init["Tirrad"]), "Cooling time": _tstring(init["Tcool"]),
                    "Half-life": "stable" if th > 1.0e17 else _tstring(_split(th)),
                    "Maximum production at": "infinity" if y["Tmax"][key] > 1.0e17 else _tstring(y["Tp"][key]),
                }
                summary.append({"nuclide": nuc, "Z": Z, "A": A, "is": i_s, "Production rate": prate.get(key, 0.0),
                                "Decay rate": lam, "Activity": float(y["activity"][key][it]),
                                "#isotopes": float(y["Niso"][key][it]), "Yield": float(y["yield_"][key][it]),
                                "Isotopic fraction": float(y["Nisorel"][key][it]), "Half-life s": th,
                                "Tmax s": y["Tmax"][key], "file": name})
    return dict(files=files, params=params, summary=summary, units=dict(activity=rstr, isotopes=ystr))


# ----------------------------------------------------------------------------------------------------------------------
# driver


def production(*, rp: dict, nonel: tuple, m: dict, k0: int, Ztarget: int, Atarget: int, maxZ: int, maxN: int,
               eninc: tuple, decay: dict | None = None, structure=None) -> dict:
    """isoprod.f90 on given residual production (rp / nonel as `residuals_from_results` / `read_rp_dir` return).

    TALYS: isoprod.f90:1 (isoprod)
    Test: tests/hf/test_kwcov_b11.py
    """
    m = check(m, k0, eninc)
    Zinit, Ainit = Ztarget + PARZ[k0], Atarget + PARZ[k0] + PARN[k0]
    Ninit = Ainit - Zinit
    maxZ, maxN = min(maxZ, Zinit - 3), min(maxN, Ninit - 3)
    init = prodinitial(m, Ztarget)
    if decay is None:
        decay = decay_data(Zinit, Ninit, maxZ, maxN, structure)
    xsrp, exist, nis, lis = prodres(rp, nonel, Zinit, Ninit, Ztarget, Atarget, m["Eback"], m["Ebeam"])
    prate, info = prodrates(xsrp, exist, m, k0, Ztarget, Atarget, init["rho"])
    y = prodyield(prate, decay, nis, m, init, info, Zinit=Zinit, Ninit=Ninit, Ztarget=Ztarget, Atarget=Atarget,
                  maxZ=maxZ, maxN=maxN)
    out = prodout(y, prate, decay, lis, m, init, Zinit=Zinit, Ninit=Ninit, maxZ=maxZ, maxN=maxN, nis=nis)
    out["meta"] = dict(info, Ntar0=y["Ntar0"], prate0=y["prate0"], Ntime=y["Ntime"], Tir=init["Tir"],
                       Tco=init["Tco"], rho=init["rho"], Eback=m["Eback"], Ebeam=m["Ebeam"], k0=k0,
                       target=(Ztarget, Atarget), radiounit=m["radiounit"], yieldunit=m["yieldunit"])
    return out


_SET: dict | None = None


def begin_run(cas, declared) -> bool:
    """Fix the run's medical input from its Options (engine_c.cases / engine.ChainedFull.cases, before the energy
    loop); the medical checks run here, before the cross sections are computed, as checkvalue does.

    TALYS: checkvalue.f90:1 (checkvalue)
    Test: tests/hf/test_kwcov_b11.py
    """
    global _SET
    _SET = None
    s = settings(cas.options)
    if s is None:
        return False
    k0 = int(cas.k0)
    check(s, k0, tuple(float(x) for x in declared))
    o = cas.options
    _SET = dict(m=s, k0=k0, Z=int(cas.Zt), A=int(cas.At), maxZ=int(o.maxZ), maxN=int(o.maxN),
                eninc=tuple(float(x) for x in declared),
                blockyield=os.environ.get("INCOGNITA_PRODUCTION_BLOCK", "") == "1")
    return True


def add_to_results(res, injection=None):
    """End of engine_c.run / engine.run: Results.production from the run's residual production (and the Y files
    with INCOGNITA_PRODUCTION_DIR). Unchanged without `production y`.

    TALYS: isoprod.f90:1 (isoprod)
    Test: tests/hf/test_kwcov_b11.py
    """
    global _SET
    if _SET is None:
        return res
    from dataclasses import replace

    s = _SET
    _SET = None
    k0 = s["k0"]
    Zinit, Ainit = s["Z"] + PARZ[k0], s["A"] + PARZ[k0] + PARN[k0]
    rp, nonel = residuals_from_results(res, Zinit, Ainit - Zinit)
    out = production(rp=rp, nonel=nonel, m=s["m"], k0=k0, Ztarget=s["Z"], Atarget=s["A"], maxZ=s["maxZ"],
                     maxN=s["maxN"], eninc=s["eninc"])
    d = os.environ.get("INCOGNITA_PRODUCTION_DIR", "").strip()
    if d:
        write_files(out, d, block=s["blockyield"])
    return replace(res, production=out)


def write_files(out: dict, directory: str | Path, block: bool = False) -> list[str]:
    """The Y files (YANDF header with prodout's parameters + the 5-column datablock); `block` = blockyield y: one
    file Y.tot with every nuclide appended.

    TALYS: prodout.f90:1 (prodout)
    Test: tests/hf/test_kwcov_b11.py
    """
    d = Path(directory)
    d.mkdir(parents=True, exist_ok=True)
    u = out["units"]
    written, chunks = [], []
    for name, cols in out["files"].items():
        p = out["params"][name]
        lines = ["# header:", f"#   title: ({p['nuclide']}) isotope production", "#   source: INCOGNITA (TALYS-2.x port)",
                 "# reaction:", "#   residual:", f"#     Z: {p['Z']}", f"#     A: {p['A']}",
                 f"#     nuclide: {p['nuclide']}"]
        if p["isomer"]:
            lines.append(f"#     isomer: {p['isomer']}")
        lines.append("#   parameters:")
        for k, v in p.items():
            if k in ("nuclide", "Z", "A", "isomer"):
                continue
            lines.append(f"#     {k}: {v:14.6E}" if isinstance(v, float) else f"#     {k}: {v}")
        lines += ["#   quantity:", "#     type: isotope production", "#   datablock:", "#     columns: 5",
                  f"#     entries: {NUMTIME}",
                  "##     Time         Activity       Isotopes         Yield     Isotopic_fract.",
                  f"##      [h]           [{u['activity']}]           [{u['isotopes']}]            "
                  f"[{u['activity']}]           []"]
        for i in range(NUMTIME):
            lines.append("".join(f"{float(cols[c][i]):15.6E}" for c in
                                 ("Time", "Activity", "Isotopes", "Yield", "Isotopic_fract.")))
        text = "\n".join(lines) + "\n"
        if block:
            chunks.append(text)
        else:
            (d / name).write_text(text)
            written.append(name)
    if block and chunks:
        (d / "Y.tot").write_text("".join(chunks))
        written.append("Y.tot")
    return written


def read_yfile(path: str | Path) -> tuple[dict, dict]:
    """A TALYS Y file: (parameters {name: str}, columns {Time, Activity, Isotopes, Yield, Isotopic_fract.}).

    TALYS: prodout.f90:1 (prodout)
    Test: tests/hf/test_kwcov_b11.py
    """
    par, rows = {}, []
    inpar = False
    for ln in Path(path).read_text().splitlines():
        if ln.startswith("#"):
            s = ln[1:].strip()
            if s.startswith("parameters:"):
                inpar = True
                continue
            if s.startswith("quantity:"):
                inpar = False
            if inpar and ":" in s:
                k, v = s.split(":", 1)
                par[k.strip()] = v.strip()
            continue
        if ln.strip():
            rows.append([float(x) for x in ln.split()])
    a = np.asarray(rows, dtype=np.float64).reshape(-1, 5)
    cols = dict(zip(("Time", "Activity", "Isotopes", "Yield", "Isotopic_fract."), a.T))  # noqa: B905
    return par, cols


def read_summary(talys_out: str | Path) -> dict:
    """The talys.out production table: {(symbol, A, isochar): {column: float}}.

    TALYS: prodout.f90:1 (prodout)
    Test: tests/hf/test_kwcov_b11.py
    """
    out = {}
    lines = Path(talys_out).read_text(errors="replace").splitlines()
    try:
        i0 = next(i for i, s in enumerate(lines) if "(Maximum) production and decay rates per isotope" in s)
    except StopIteration:
        return out
    for s in lines[i0 + 4:]:
        if not s.strip() or s.startswith("Medical") or s.lstrip().startswith("#"):
            if s.startswith("Medical"):
                break
            continue
        sym, a, iso = s[1:3].strip(), int(s[3:7]), s[8:9].strip()
        v = [float(s[9 + 15 * j:9 + 15 * (j + 1)]) for j in range(5)]
        out[(sym, a, iso)] = dict(zip(("Production rate", "Decay rate", "Activity", "#isotopes", "Yield"), v),  # noqa: B905
                                  **{"Isotopic fraction": float(s[84:92])})
    return out
