"""KWCOV B13: TALYS's ingredient output files on an engine run (output only).

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

The deck keywords `outlevels`, `outdensity`, `filedensity`, `outgamma`, `filepsf`, `outinverse`, `outtransenergy`,
`outomp`, `blockomp`, `outkd`, `partable` and the umbrella `outbasic` ask TALYS for the files that show what a run was
computed FROM: discrete levels and masses, level densities, photon strength functions, transmission coefficients and
inverse cross sections, optical-model parameters and potentials, and every model parameter (parameters.dat). This
module builds the same files from the engine's own ingredients, read off the run's `Cascade` after the run (cache
hits: the level densities, gamma parameters and transmission coefficients the reaction used; the optical-model
parameters and radial potentials are recomputed with the run's own functions, as output). Nothing here runs unless
the run's Options ask for it, and no Results array other than `Results.ingout` changes.

`Results.ingout` = {TALYS file name: {"header": {title, Z, A, nuclide, kind}, "blocks": [{"meta": {key: value},
"quantity": str, "columns": [...], "units": [...], "data": ndarray (rows, columns)}, ...]}} plus, for the two
non-YANDF outputs, "nld<ZZZAAA>.tab" (the same blocks; written in TALYS's fixed format), "parameters.dat"
({"rows": [(keyword, Z, A, value, qualifier)], "general": [(keyword, particle, value)], "text": str}) and
"kd03" (outkd: talys.out's KD03 lines as {particle: {column: ndarray}}). INCOGNITA_INGOUT_DIR=<dir> writes the files.

TALYS routines ported here (file:line of the subroutine statement):
    levelsout.f90:1 (levelsout)            levels<ZZZAAA>.out (outlevels)
    densityout.f90:1 (densityout)          ld<ZZZAAA>.gs[bNN], nld<ZZZAAA>.tab[_bNN] (outdensity / filedensity)
    densitycum.f90:1 (densitycum)          the filedensity D0 statistics (chi2D0, CED0, FrmsD0, ErmsD0, CGD0)
    gammaout.f90:1 (gammaout)              psf<ZZZAAA>.E1/M1/E2/M2 (filepsf), cross_g.tot (outgamma)
    inverseout.f90:1 (inverseout)          transmission_<p>.out, cross_<p>.tot (outinverse; outtransenergy layout)
    incidentout.f90:1 (incidentout)        transmission_inc.out (outinverse; the last incident energy)
    inverseecis.f90:1 (inverseecis)        omppar_<p>.out (outomp)
    incidentread.f90:1 (incidentread)      omp.out / ompE<EEEE.EEE>_<p>.tot (outomp; blockomp)
    spr.f90:1 (spr)                        spr.opt (outomp)
    opticalnp.f90:1 (opticalnp)            the KD03 lines of talys.out (outkd)
    partable.f90:1 (partable), finalout.f90:1 (finalout), nuclides.f90:1 (nuclides)   parameters.dat (partable)
    gammadecay.f90:1 (gammadecay)          gamma<ZZZAAA>.tot, cumulative discrete gamma decay (outbasic / endf y;
                                           KWCOV B15)
    endfinfo.f90:1 (endfinfo)              tefal.inf, energies.endf (endf y, more than one energy; KWCOV B15)
    sacs.f90:1 (sacs)                      sacs.dat: per exclusive channel threshold, peak energy, peak and FWHM
                                           (sacs y; KWCOV B15)
TALYS quirks kept: the psf .E2/.M2 files' f column is the l = 1 strength (gammaout.f90 calls fstrength with l = 1);
`filepsf y` without `outgamma y` writes nothing (gammaout is called only for outgamma); `outdensity y; filedensity n`
leaves the D0 statistics and the experimental level density of ld*.gs at 0 (densitycum fills them for filedensity
only); the psf header's experimental Gamma_gamma is TALYS's gamgam (keV, labelled eV) and C/E uses it.
Task: T10 (physics/hf/CONTRACT.md section 7; KWCOV batch B13). Acceptance test: KWCOV-B13 (tests/hf/test_kwcov_b13.py).
"""
from __future__ import annotations

import math
import os
from dataclasses import replace
from pathlib import Path

import numpy as np

ENV_DIR = "INCOGNITA_INGOUT_DIR"
PARSYM = "gnpdtha"
PARNAME = ("gamma", "neutron", "proton", "deuteron", "triton", "helium-3", "alpha")
PARZ = (0, 0, 1, 1, 1, 2, 2)
PARN = (0, 1, 0, 1, 2, 1, 2)
SOURCE = "INCOGNITA (TALYS-2.25 port)"
STATE: dict = {}

__all__ = ["active", "begin_run", "add_to_results", "build", "write_files", "ENV_DIR"]


def _yn(o, name: str) -> bool:
    return bool(getattr(o, name, False))


def active(options) -> dict:
    """Which ingredient outputs the run's Options ask for ({} = none, the default).

    TALYS: output switches of input_basicreac / input_levels / input_densitymodel / input_densitypar /
    input_gammamodel / input_ompmodel / input_output
    Test: tests/hf/test_kwcov_b13.py
    """
    o = options
    want = {
        "levels": _yn(o, "flaglevels") or _yn(o, "flagbasic") or _yn(o, "flagendf"),  # B15: structure.f90:75
        "density": _yn(o, "flagdensity") or _yn(o, "filedensity"),
        "gamma": _yn(o, "flaggamma"),
        "inverse": _yn(o, "flaginverse"),
        "omp": _yn(o, "flagoutomp"),
        "kd": _yn(o, "flagoutkd"),
        "partable": _yn(o, "flagpartable"),
        "endf": _yn(o, "flagendf"),  # KWCOV B15: endfinfo (tefal.inf, energies.endf)
        "sacs": _yn(o, "flagsacs"),  # KWCOV B15: sacs.dat
    }
    return {k: v for k, v in want.items() if v}


def begin_run(cas) -> None:
    """Remember the run's Cascade when it asks for ingredient output (nothing otherwise).

    TALYS: talysreaction.f90:1 (talysreaction)
    Test: tests/hf/test_kwcov_b13.py
    """
    STATE.clear()
    w = active(cas.options)
    if w:
        STATE.update(cas=cas, want=w)


def add_to_results(res, injection=None):
    """Results.ingout from the remembered Cascade (and the files with INCOGNITA_INGOUT_DIR); `res` unchanged when the
    run asked for no ingredient output.

    TALYS: output.f90:1 (output)
    Test: tests/hf/test_kwcov_b13.py
    """
    if not STATE:
        return res
    cas, want = STATE["cas"], STATE["want"]
    STATE.clear()
    e_inc = [float(x) for x in res.e_inc_mev.tolist()] if res.e_inc_mev is not None else []
    out = build(cas, want, e_inc, res)
    d = os.environ.get(ENV_DIR, "").strip()
    if d:
        write_files(out, d)
    return replace(res, ingout=out)


# --------------------------------------------------------------------------------------------- helpers
def _f(x) -> float:
    if hasattr(x, "detach"):
        return float(x.detach().reshape(-1)[0])
    return float(np.asarray(x, dtype=float).reshape(-1)[0])


def _a(x) -> np.ndarray:
    return np.asarray(x.detach().cpu().numpy() if hasattr(x, "detach") else x, dtype=np.float64)


def _f32(x: float) -> float:
    return float(np.float32(x))


def _nuc(Z: int, A: int) -> str:
    from physics.hf.core.constants import NUC

    return f"{NUC[Z - 1]}{A}"


def _za_str(Z: int, A: int) -> str:
    return f"{Z:03d}{A:03d}"


def _file(title: str, Z: int, A: int, kind: str = "residual", blocks=None) -> dict:
    return {"header": {"title": title, "Z": int(Z), "A": int(A), "nuclide": _nuc(Z, A), "kind": kind},
            "blocks": list(blocks or [])}


def _block(quantity: str, columns, units, data, meta=None, pre=None) -> dict:
    """One datablock; `pre` = the `parameters` keys printed before the quantity (per block)."""
    arr = np.asarray(data, dtype=np.float64)
    if arr.ndim == 1:
        arr = arr.reshape(-1, len(columns)) if arr.size else np.zeros((0, len(columns)))
    return {"meta": dict(meta or {}), "pre": dict(pre or {}), "quantity": quantity, "columns": list(columns),
            "units": list(units), "data": arr}


def _grid(cas) -> dict:
    """The run's emission grid: egrid, maxen, ebegin and eendmax per type (grid.f90, energies.f90)."""
    from physics.hf.compound.dens_reference import _eendmax, run_grid

    rg = run_grid(int(cas.Zt), int(cas.At), float(cas.enincmax))
    eend = _eendmax(int(cas.Zt), int(cas.At), float(cas.enincmax))
    return {"rg": rg, "egrid": np.asarray(rg.egrid, dtype=float), "maxen": int(rg.maxen),
            "ebegin": {t: int(rg.ebegin[t]) for t in range(7)}, "eend": {t: int(eend[t]) for t in range(7)}}


def _target_ix(cas) -> tuple[int, int]:
    return PARZ[int(cas.k0)], PARN[int(cas.k0)]


# --------------------------------------------------------------------------------------------- levels
def levels_file(cas, zix: int, nix: int, prior: bool = False) -> tuple[str, dict]:
    """levels<ZZZAAA>.out: mass, separation energies and the discrete levels with their branches.

    TALYS: levelsout.f90:1 (levelsout)
    Test: tests/hf/test_kwcov_b13.py
    """
    Z, A = (int(v) for v in cas.zn(zix, nix))
    lv = cas._levels(zix, nix)
    if prior:  # levels.f90:179-183: a second read keeps the first branch list, conv / flags by file index
        from physics.hf.structure.levels import discrete_levels

        lv = discrete_levels(Z, A, cas.options, cas.m, cas.params, prior_call=True)
    m = cas.m
    pre = {"nuclear mass [amu]": _f(m.mass_amu[zix, nix]),
           "neutron separation energy [MeV]": _f(m.s_mev[zix, nix, 1]),
           "proton separation energy [MeV]": _f(m.s_mev[zix, nix, 2]),
           "alpha separation energy [MeV]": _f(m.s_mev[zix, nix, 6]),
           "number of excited levels": int(lv.nlev)}
    n = int(lv.nlev) + 1
    rows = np.zeros((n, 6))
    rows[:, 0] = _a(lv.levnum)[:n]
    rows[:, 1] = _a(lv.e_mev)[:n]
    rows[:, 2] = _a(lv.spin)[:n]
    rows[:, 3] = _a(lv.parity)[:n]
    rows[:, 4] = _a(lv.nbranch)[:n]
    rows[:, 5] = _a(lv.half_life_ripl_s)[:n]
    br_to, br_r, br_c = _a(lv.branch_to), _a(lv.branch_ratio), _a(lv.conversion)
    branches = []
    for i in range(n):
        for k in range(int(rows[i, 4])):
            branches.append((i, int(br_to[i, k]), 100.0 * br_r[i, k], br_c[i, k]))
    b = _block("Nuclear masses and levels", ["Level", "Energy", "Spin", "Parity", "Num._Branches", "Half-life"],
               ["", "MeV", "", "", "", "sec"], rows, pre=pre)
    b["branches"] = np.asarray(branches, dtype=float).reshape(-1, 4)
    b["assign"] = [str(lv.assign[i]) if i < len(lv.assign) else "" for i in range(n)]
    b["ensdf"] = [str(lv.ensdf[i]) if i < len(lv.ensdf) else "" for i in range(n)]
    b["branch_assign"] = [tuple(lv.branch_assign[i]) if i < len(lv.branch_assign) else () for i in range(n)]
    f = _file(f"{_nuc(Z, A)} Nuclear masses and levels", Z, A, blocks=[b])
    return f"levels{_za_str(Z, A)}.out", f


def gamma_decay_file(cas, zix: int, nix: int, prior: bool = False) -> tuple[str, dict]:
    """gamma<ZZZAAA>.tot: per discrete level, every gamma of its cumulative decay to the ground state (branching flux
    followed down the level scheme, isomers stop it), sorted by gamma energy, with the total gamma yield.

    TALYS: gammadecay.f90:1 (gammadecay)
    Test: tests/hf/test_kwcov_b15.py
    """
    Z, A = (int(v) for v in cas.zn(zix, nix))
    lv = cas._levels(zix, nix)
    if prior:  # levels.f90:179-183: the nucleus's levels were read before structure() (conversion by file index)
        from physics.hf.structure.levels import discrete_levels

        lv = discrete_levels(Z, A, cas.options, cas.m, cas.params, prior_call=True)
    nlev = int(lv.nlev)
    edis, tau = _a(lv.e_mev), _a(lv.half_life_s)
    nbr, bto = _a(lv.nbranch).astype(int), _a(lv.branch_to).astype(int)
    brr, conv = _a(lv.branch_ratio), _a(lv.conversion)
    electron = bool(getattr(cas.options, "flagelectron", True))
    rows, gams = [], []
    for i in range(1, nlev + 1):
        flux = np.zeros(nlev + 1)
        flux[i] = 1.0
        g, total, totalg = [], 0.0, 0.0
        for j in range(i, 0, -1):
            if tau[j] != 0.0:
                continue
            for k in range(int(nbr[j])):
                lto = int(bto[j, k])
                if flux[j] == 0.0:
                    continue
                b = float(brr[j, k]) * flux[j]
                g.append([j, lto, edis[j] - edis[lto], b, edis[j], edis[lto]])
                flux[lto] += b
                total += b
                totalg = totalg + b / (1.0 + float(conv[j, k])) if electron else total
        if total != 0.0:
            for r in g:
                r[3] /= total
            for jj in range(len(g)):  # gammadecay.f90's exchange sort (descending gamma energy), kept literally
                for kk in range(jj + 1):
                    if g[jj][2] > g[kk][2]:
                        g[jj], g[kk] = g[kk], g[jj]
        rows.append([i, edis[i], len(g), totalg])
        gams.append(np.asarray(g, dtype=float).reshape(-1, 6))
    b = _block("Cumulative discrete gamma decay",
               ["Level", "Energy", "Num._branch", "Total_yield", "Parent_level", "Daughter_level", "Gamma_energy",
                "Branch._ratio", "Parent_energy", "Daughter_energy"],
               ["", "MeV", "", "", "", "", "MeV", "", "MeV", "MeV"], np.zeros((0, 10)))
    b["data"] = np.asarray(rows, dtype=float).reshape(-1, 4)
    b["gammas"] = gams
    tZ, tA = (int(v) for v in cas.zn(*_target_ix(cas)))
    f = _file(f"{_nuc(tZ, tA)} Cumulative discrete gamma decay", tZ, tA, kind="target", blocks=[b])
    return f"gamma{_za_str(Z, A)}.tot", f


def _gammadecay_text(f: dict) -> str:
    b = f["blocks"][0]
    lines = _header_lines(f["header"])
    n = int(b["data"].shape[0]) + sum(int(x.shape[0]) for x in b["gammas"])
    lines += ["# quantity: ", f"#   type: {b['quantity']}", "# datablock: ", f"#   columns: {len(b['columns'])}",
              f"#   entries: {n}"]
    lines.append("##" + "".join(f"{c:^15}" for c in b["columns"]))
    lines.append("##" + "".join(f"{('[' + u + ']'):^15}" for u in b["units"]))
    for r, gs in zip(b["data"], b["gammas"]):
        lines.append(f"{int(r[0]):6d}{'':9s}{r[1]:15.6E}{int(r[2]):6d}{'':9s}{r[3]:15.6E}")
        for x in gs:
            lines.append(f"{'':60s}{int(x[0]):6d}{'':9s}{int(x[1]):6d}{'':9s}" + "".join(f"{v:15.6E}" for v in x[2:]))
    return "\n".join(lines) + "\n"


def endf_info(cas, energies, res=None) -> dict:
    """tefal.inf (the run's facts for TEFAL) and energies.endf (the incident energies), `endf y` with Ninc > 1.

    TALYS: endfinfo.f90:1 (endfinfo)
    Test: tests/hf/test_kwcov_b15.py
    """
    o = cas.options
    tz, tn = _target_ix(cas)
    lv = cas._levels(tz, tn)

    def yn(b) -> str:
        return "y" if b else "n"

    urr = bool(res is not None and getattr(res, "urr", None))
    lines = [f"{int(cas.k0):3d}       : projectile type", f"{int(o.Ztarget):3d}       : Z of target",
             f"{int(o.Atarget):3d}       : A of target",
             f"{_f(cas.m.mass_amu[tz, tn]):10.6f}: mass of target in a.m.u.",
             f"{_f(lv.spin[0]):4.1f}      : spin of target", f"{0.0:10.6f}: energy of target",
             f"{int(o.Ltarget):4d}{int(getattr(o, 'Liso', 0) or 0):4d}  : level and isomeric number of target",
             f"{len(energies):4d}      : number of incident energies",
             f"{int(o.nlevmax):4d}      : number of discrete levels", "energies.endf : file with incident energies",
             f"{yn(o.flagendfdet)}         : detailed ENDF-6 information per channel",
             "y         : keep elastic cross section in normalization",
             f"{yn(o.flagrecoil)}         : recoils", f"{yn(urr)}         : urr", "y         : block"]
    return {"tefal.inf": {"text": "\n".join(lines) + "\n"},
            "energies.endf": {"text": "".join(f"{_es(e)}\n" for e in energies)}}


def _channel_q(cas, code: str) -> float:
    """Qexcl(idc, 0) of an exclusive channel (channels.f90:283-318): S(0, 0, k0) + targetE minus the separation energy
    of every particle on the way down (n, p, d, t, h, a removed in that order; the sum is path independent)."""
    m = cas.m
    q = _f(m.s_mev[0, 0, int(cas.k0)])
    zix = nix = 0
    for t, cnt in zip(range(1, 7), (int(c) for c in code)):
        for _ in range(cnt):
            q -= _f(m.s_mev[zix, nix, t])
            zix, nix = zix + PARZ[t], nix + PARN[t]
    return q


def sacs_table(cas, res) -> dict:
    """sacs.dat: for every exclusive channel the run has (xs<code>.tot), its threshold Ethrexcl(idc, 0), the energy
    and value of the largest cross section on the incident grid and its full width at half maximum (pol1 on the
    two crossings, 0 without both). Rows in sacs.f90's loop order (number of particles, then a h t d p n).

    TALYS: sacs.f90:1 (sacs), channels.f90:306-312 / :656-661 (Ethrexcl; (n,n') takes its first excited level)
    Test: tests/hf/test_kwcov_b15.py
    """
    e = np.asarray(res.e_inc_mev.tolist(), dtype=float)
    o = cas.options
    tz, tn = _target_ix(cas)
    mt, mp = _f(cas.m.mass_amu[tz, tn]), _parmass(int(cas.k0))
    specmass = mt / (mt + mp)
    rows = []
    codes = sorted((k[2:] for k in res.channels_mb if k.startswith("xs") and len(k) == 8 and k[2:].isdigit()),
                   key=lambda c: (sum(int(x) for x in c), c[5], c[4], c[3], c[2], c[1], c[0]))
    # sacs.f90 reads the xs<code>.tot files the run wrote: channelsout writes them only with channels y and filechannels
    # (input_outfiles.f90: filechannels follows flagexc = more than one energy, or endf y + endfdetail); without them
    # sacs.dat is the two header lines (stock Fe-56 `sacs y` alone)
    if not (bool(getattr(o, "flagchannels", False))
            and (len(e) > 1 or (bool(o.flagendf) and bool(o.flagendfdet)))):
        codes = []
    for code in codes:
        xs = np.asarray(res.channels_mb["xs" + code].tolist(), dtype=float)
        q = _channel_q(cas, code)
        if int(cas.k0) == 1 and code == "100000":  # channels.f90:656-661: (n,n') threshold = its first excited level
            lv = cas._levels(*_cas_ix(code))
            q -= _f(lv.e_mev[1]) if int(lv.nlev) >= 1 else 0.0
        ethr = 0.0 if q >= 0.0 else -q / specmass
        ex = np.concatenate([[0.0], e])
        xv = np.concatenate([[0.0], xs])
        imax, xsmax = 0, 0.0
        for n in range(1, len(ex)):
            if xv[n] > xsmax:
                imax, xsmax = n, xv[n]
        emax = ex[imax] if imax else 0.0
        half = 0.5 * xsmax
        eh1 = eh2 = 0.0
        for n in range(1, len(ex)):
            if xv[n - 1] < half <= xv[n]:
                eh1 = _pol1(xv[n - 1], xv[n], ex[n - 1], ex[n], half)
            if xv[n - 1] > half >= xv[n]:
                eh2 = _pol1(xv[n - 1], xv[n], ex[n - 1], ex[n], half)
                break
        width = eh2 - eh1 if (eh1 > 0.0 and eh2 > 0.0) else 0.0
        rows.append((int(o.Ztarget), int(o.Atarget), f"xs{code}.tot", ethr, emax, xsmax, width))
    head = (f"# {PARSYM[int(cas.k0)]} + {_nuc(int(o.Ztarget), int(o.Atarget))}: Statistical analysis of cross "
            "sections\n# Z   A     channel    E-thresh.   Emax     xsmax    width \n")
    text = head + "".join(f"{z:4d}{a:4d} {f:15s}{t:8.3f}{em:8.3f}{_es(x)}{w:10.3f}\n" for z, a, f, t, em, x, w in rows)
    return {"rows": rows, "text": text}


def _cas_ix(code: str) -> tuple[int, int]:
    """(Zix, Nix) of the residual of exclusive channel `code` (relative to the compound nucleus)."""
    zix = sum(int(c) * PARZ[t] for t, c in zip(range(1, 7), code))
    nix = sum(int(c) * PARN[t] for t, c in zip(range(1, 7), code))
    return zix, nix


def _pol1(x1: float, x2: float, y1: float, y2: float, x: float) -> float:
    """pol1.f90: linear interpolation of y at x between (x1, y1) and (x2, y2)."""
    return y1 if x2 == x1 else y1 + (x - x1) * (y2 - y1) / (x2 - x1)


def _parmass(k: int) -> float:
    from physics.hf.omp.schrodinger import PARMASS_AMU

    return float(PARMASS_AMU[k])


def _es(x: float) -> str:
    """Fortran es12.5."""
    m, ex = f"{x:.5E}".split("E")
    return f"{m}E{int(ex):+03d}".rjust(12)


# --------------------------------------------------------------------------------------------- level density
def _d0_stats(dtheo: float, dexp: float, ddexp: float, dglob: float) -> dict:
    """densitycum.f90:148-185 (filedensity): chi2D0, CED0, FrmsD0, ErmsD0, CGD0."""
    chi2 = 0.0 if ddexp <= 1.0e-30 else (abs(dtheo - dexp) / ddexp) ** 2
    frms = erms = ced0 = 0.0
    if dexp > 1.0e-30:
        ced0 = dtheo / dexp
        if dtheo > 0.0 and dexp > 0.0:
            if ddexp > 0.0:
                x = (dtheo - dexp) / (ddexp * math.sqrt(2.0))
                pp = math.erf(x) if dtheo > dexp else -math.erf(x)
                ri = 1.0 + (ced0 - 1.0) * pp
            else:
                ri = ced0
            frms = ri if ri >= 1.0 else 1.0 / ri
            erms = ri
    cg = dtheo / dglob if dglob > 1.0e-30 else 0.0
    return {"Chi-2 D0": chi2, "C/E D0": ced0, "Frms D0": frms, "Erms D0": erms, "C/G D0": cg}


def _barrier_ld(cas, Z: int, A: int):
    """(Z, A)'s level density with its fission-barrier arrays, as the fission chain builds it (None: no barrier)."""
    try:
        from physics.hf.density.ctwindow import enabled as _ctw
        from physics.hf.density.ctwindow2 import mode as _ctw2
        from physics.hf.density.matching import densitymatch
        from physics.hf.density.parameters import densitypar
        from physics.hf.density.tables import attach_tables
        from physics.hf.fission.parameters import barrier_levels, fission_parameters
        from physics.hf.structure.levels import discrete_levels

        o, p, ms = cas.options, cas.params, cas.m
        fp = fission_parameters(Z, A, o, p, masses=ms)
        if int(fp.nfisbar) <= 0:
            return None
        lv = discrete_levels(Z, A, o, ms, p)
        return densitymatch(attach_tables(densitypar(Z, A, o, p, ms, lv, barriers=barrier_levels(fp))),
                            ctwindow=_ctw(o), ctwindow2=_ctw2(o))
    except Exception:  # noqa: BLE001 - a nucleus fissionpar declines has no barrier files
        return None


def density_files(cas, zix: int, nix: int) -> dict:
    """ld<ZZZAAA>.gs (+ b<NN> per fission barrier) and the matching nld<ZZZAAA>.tab blocks for one nucleus.

    TALYS: densityout.f90:1 (densityout), densitycum.f90:1 (densitycum)
    Test: tests/hf/test_kwcov_b13.py
    """
    import torch

    from physics.hf.density.matching import densitycum
    from physics.hf.density.models import densityout, densitytot, dtheory
    from physics.hf.density.parameters import colenhance, ignatyuk
    from physics.hf.structure.resonances import resonance_parameters

    o = cas.options
    filedensity = bool(getattr(o, "filedensity", False))
    Z, A = (int(v) for v in cas.zn(zix, nix))
    ld = cas.ld_of(Z, A)[0]
    out: dict = {}
    cum = densitycum(ld)
    rd = resonance_parameters(Z, A, o, cas.params)
    tl = cas._levels(zix, min(nix + 1, 33))
    D = dtheory(ld, float(_a(tl.spin)[0]), int(_a(tl.parity)[0]), 0.0, 0)
    d0theo, d1theo = float(D[0]), float(D[1])
    ldb = _barrier_ld(cas, Z, A) if bool(o.flagfission) else None
    nfis = int(ldb.nfisbar) if ldb is not None else 0
    odd = A % 2
    for ibar in range(0, nfis + 1):
        if ibar > 0:  # the fission chain's own level density with the barrier arrays (fission/chain.py)
            ld = ldb
        # densitycum.f90:93-139 fills Ncum always; rhoexp (and the statistics) only for filedensity
        dout = densityout(ld, cum["Ncum"], ibar, cum["rhoexp"] if filedensity else torch.zeros_like(cum["rhoexp"]))
        pre = {}
        for k, v in dout["parameters"].items():
            pre[k] = v
        if ibar == 0:
            dglob = float(rd.d0global_ev)
            pre.update({"experimental D0 [eV]": float(rd.d0_ev), "experimental D0 unc. [eV]": float(rd.dd0_ev),
                        "global D0 [eV]": dglob, "global D0 unc. [eV]": dglob, "theoretical D0 [eV]": d0theo})
            st = _d0_stats(d0theo, float(rd.d0_ev), float(rd.dd0_ev), dglob) if filedensity else \
                {"Chi-2 D0": 0.0, "C/E D0": 0.0, "Frms D0": 0.0, "Erms D0": 0.0, "C/G D0": 0.0}
            pre.update(st)
            pre.update({"experimental D1 [eV]": float(rd.d1_ev), "experimental D1 unc. [eV]": float(rd.dd1_ev),
                        "theoretical D1 [eV]": d1theo})
            if filedensity:
                pre.update({"Chi-2 per level": _f(cum["chi2lev"]), "Frms per level": _f(cum["Frmslev"]),
                            "Erms per level": _f(cum["Ermslev"]), "average deviation per level": _f(cum["avdevlev"])})
            else:
                pre.update({"Chi-2 per level": 0.0, "Frms per level": 0.0, "Erms per level": 0.0,
                            "average deviation per level": 0.0})
        blocks = []
        col_enh = ld.ldmodel <= 3 and bool(ld.flagcol) and not ld.has_table(ibar)
        if ibar == 0 and "levels" in dout:
            L = dout["levels"]
            cols = ["E", "Level", "N_cumulative", "Total_LD", "Exp_LD"]
            units = ["MeV", "", "", "MeV^-1", "MeV^-1"]
            data = [L["E"], L["Level"], L["N_cumulative"], L["Total_LD"], L["Exp_LD"]]
            if ld.ldmodel <= 3:
                cols += ["a", "Sigma"]
                units += ["MeV^-1", ""]
                data += [L["a"], L["Sigma"]]
                if col_enh:
                    kr, kv, kc = [], [], []
                    for e, a in zip(L["E"], L["a"]):
                        r = colenhance(ld, torch.tensor(float(e), dtype=torch.float64),
                                       torch.tensor(float(a), dtype=torch.float64), ibar)
                        kr.append(_f(r[0])); kv.append(_f(r[1])); kc.append(_f(r[2]))  # noqa: E702
                    cols += ["Krot", "Kvib", "Kcoll"]
                    units += ["", "", ""]
                    data += [kr, kv, kc]
            blocks.append(_block("total level density", cols, units, np.stack([np.asarray(x, float) for x in data], 1)))
        pb = dout["parity_blocks"]
        J = np.arange(_a(pb[1]["rho_J"]).shape[-1]) + 0.5 * odd
        cols = ["E", "T", "N_cumulative", "rho_observed", "rho_total"] + [f"rho(J)={j:4.1f}" for j in J]
        units = ["MeV", "MeV", ""] + ["MeV^-1"] * (len(cols) - 3)
        for parity in (1, -1):
            b = pb[parity]
            data = np.concatenate([np.stack([_a(b["E"]), _a(b["T"]), _a(b["N_cumulative"]), _a(b["rho_observed"]),
                                             _a(b["rho_total"])], 1), _a(b["rho_J"])], 1)
            blocks.append(_block("level density", cols, units, data, meta={"Parity": parity}))
        E = _a(pb[1]["E"])
        rdist = {}
        for parity in (-1, 1):
            rj, tot = _a(pb[parity]["rho_J"]), _a(pb[parity]["rho_observed"])
            with np.errstate(divide="ignore", invalid="ignore"):
                r = rj / tot[:, None]
            rdist[parity] = np.where(np.isfinite(r) & (r > 1.0e-20), r, 0.0)
        for i, e in enumerate(E):
            data = np.stack([J, rdist[-1][i], rdist[1][i]], 1)
            blocks.append(_block("spin distribution", ["Spin", "R (parity -)", "R (parity +)"], ["", "", ""], data,
                                 meta={"Excitation energy [MeV]": float(e)}))
        name = f"ld{_za_str(Z, A)}." + (f"b{ibar:02d}" if ibar > 0 else "gs")  # densityout.f90:181-182
        f = _file(f"{_nuc(Z, A)} level density", Z, A, blocks=blocks)
        f["header"]["pre"] = pre
        out[name] = f
        nld = f"nld{_za_str(Z, A)}.tab" + (f"_b{ibar:02d}" if ibar > 0 else "")
        out[nld] = {"header": {"Z": Z, "A": A, "nuclide": _nuc(Z, A), "ldmodel": int(ld.ldmodel), "kind": "nld"},
                    "blocks": [blk for blk in blocks if blk["quantity"] == "level density"]}
    _ = densitytot, ignatyuk
    return out


# --------------------------------------------------------------------------------------------- gamma
_MODEL_E1 = {1: "Kopecky-Uhl", 2: "Brink-Axel", 3: "Goriely HFbcs tables", 4: "Goriely HFB tables",
             5: "Goriely Hybrid model", 6: "Goriely T-dep. HFB Tables", 7: "Goriely T-dep. RMF Tables",
             8: "Gogny D1M HFB+QRPA Tables", 9: "IAEA-CRP SMLO 2019 Tables", 10: "BSk27+QRPA 2018 Tables",
             11: "D1M-Intra-E1", 12: "Shellmodel-E1", 13: "RQFAMz"}
_MODEL_M1 = {1: "RIPL-1", 2: "RIPL-2", 3: "IAEA GSF CRP (2018)", 4: "RIPL-2+Scissors Kawano",
             8: "Gogny D1M HFB+QRPA Tables", 10: "BSk27+QRPA 2018 Tables", 11: "D1M-Intra-M1", 12: "Shellmodel-M1"}


def gamma_files(cas, g: dict, e_first: float, ing: dict) -> dict:
    """psf<ZZZAAA>.<XL> (filepsf) and cross_g.tot of the initial compound nucleus, at the run's first energy.

    TALYS: gammaout.f90:1 (gammaout), gamma.f90:1 (gamma)
    Test: tests/hf/test_kwcov_b13.py
    """
    import torch

    from physics.hf.compound.psf_fast import fstrength_np
    from physics.hf.gamma.strength import fstrength_gp
    from physics.hf.gamma.transmission import gammaxs, tgamma
    from physics.hf.structure.resonances import resonance_parameters

    o = cas.options
    Zt, At = int(cas.Zt), int(cas.At)
    Z, A = int(cas.Zc), int(cas.Ac)
    gp = cas.gamma_params(Zt, At)
    out: dict = {}
    if gp is None:
        return out
    eg = g["egrid"]
    nb, ne = g["ebegin"][0], _eend_at(cas, g, e_first)[0]
    epsf = [float(eg[n]) for n in range(nb, ne + 1)]
    if bool(getattr(o, "filepsf", False)) and epsf and epsf[-1] < 30.0:
        epsf += [0.5 * n for n in range(int(2.0 * (_f32(epsf[-1]) + 0.5)), 61)]
    egt = torch.as_tensor(eg, dtype=torch.float64)
    tj = tgamma(gp, egt, float(e_first), Zt, At)
    tjl = _a(tj.tjl)  # (E, irad, l)
    if bool(getattr(o, "filepsf", False)):
        rd = resonance_parameters(Z, A, o, cas.params)
        gg, dgg = float(rd.gamgam_talys), float(rd.dgamgam_talys)
        th = float(ing.get("ing_gamgam_th_ev", float("nan")))
        ce = th / gg if gg > 0.0 else 0.0
        e_arr = np.asarray(epsf, dtype=float)
        for l in range(1, int(gp.gammax) + 1):  # noqa: E741
            for irad in (0, 1):
                rad = ("M" if irad == 0 else "E") + str(l)
                mm = int(gp.strengthM1 if irad == 0 else gp.strength)
                model = (_MODEL_M1 if irad == 0 else _MODEL_E1).get(mm, "")
                pre: dict = {"strength keyword": mm, "PSF model": model}
                if (irad == 0 and gp.strengthM1 <= 4) or (irad == 1 and (gp.strength <= 2 or gp.strength == 5)) \
                        or l >= 2:
                    pre["sigma0 (sgr) [mb]"] = _f(gp.sgr_mb[irad, l, 1])
                    pre["E (egr) [MeV]"] = _f(gp.egr_mev[irad, l, 1])
                    pre["gamma (ggr) [MeV]"] = _f(gp.ggr_mev[irad, l, 1])
                    if gp.ngr[irad][l] == 2:
                        pre["sigma0_2 (sgr) [mb]"] = _f(gp.sgr_mb[irad, l, 2])
                        pre["E_2 (egr) [MeV]"] = _f(gp.egr_mev[irad, l, 2])
                        pre["gamma_2 (ggr) [MeV]"] = _f(gp.ggr_mev[irad, l, 2])
                if gp.flagupbend and l == 1:
                    if irad == 0:
                        pre["M1 upbend C"] = _f(gp.upbend[0, 1, 1])
                        pre["M1 upbend eta"] = _f(gp.upbend[0, 1, 2])
                        pre["M1 upbend F"] = _f(gp.upbend[0, 1, 3])
                    else:
                        pre["E1 upbend C"] = _f(gp.upbend[1, 1, 1])
                        pre["E1 upbend eta"] = _f(gp.upbend[1, 1, 2])
                if l == 1:
                    if irad == 0 or _f(gp.tpr_mb[1, 1, 1]) > 0.0:
                        pre["pygmy tpr [mb]"] = _f(gp.tpr_mb[irad, 1, 1])
                        pre["pygmy epr [MeV]"] = _f(gp.epr_mev[irad, 1, 1])
                        pre["pygmy gpr [MeV]"] = _f(gp.gpr_mev[irad, 1, 1])
                pre["ftable"] = _f(gp.ftable[irad, l])
                pre["etable"] = _f(gp.etable_mev[irad, l])
                pre["wtable"] = _f(gp.wtable[irad, l])
                pre2 = {"experimental Gamma_gamma [eV]": gg, "experimental Gamma_gamma unc. [eV]": dgg,
                        "theoretical Gamma_gamma [eV]": th, "C/E Gamma_gamma": ce,
                        "average resonance energy [eV]": float(ing.get("ing_eavres_mev", 0.01)) * 1.0e6,
                        "theoretical S-wave strength function [e-4]": float(ing.get("ing_swaveth_e4", float("nan")))}
                fv = fstrength_np(gp, 0.0, e_arr, irad, 1)  # gammaout.f90: l = 1 in every file (quirk kept)
                if fv is None:
                    fv = _a(fstrength_gp(gp, 0.0, torch.as_tensor(e_arr, dtype=torch.float64), irad, 1))
                tcol = np.zeros(len(e_arr))
                for i in range(len(e_arr)):  # Tjl(0, nen, irad, l) indexed by the row number nen (quirk kept)
                    nen = i + 1
                    if nb <= nen <= ne and nen < tjl.shape[0]:
                        tcol[i] = tjl[nen, irad, l]
                data = np.stack([e_arr, np.asarray(fv, float), tcol], 1)
                b = _block(f"{rad} photon strength function", ["E", f"f({rad})", f"T({rad})"], ["MeV", "MeV^-3", ""],
                           data)
                f = _file(f"{_nuc(Z, A)} {rad} photon strength function", Z, A, blocks=[b])
                f["header"]["pre"] = pre
                f["header"]["pre2"] = pre2
                out[f"psf{_za_str(Z, A)}.{rad}"] = f
    ec = np.asarray([eg[n] for n in range(nb, ne + 1)], dtype=float)
    # fstrength.f90:150 tests Egamma > 0.001 in single precision: egrid(1) = 0.001 is not above it there; the port's
    # double compare of float32(0.001) is (a 1 keV E2/M2 / pygmy term TALYS drops; engine untouched, output fixed here)
    ecx = np.where(np.float32(ec) == np.float32(0.001), 0.001, ec)
    xs, xg, xq = gammaxs(gp, torch.as_tensor(ecx, dtype=torch.float64), float(e_first), Zt, At)
    b = _block("photo absorption cross sections", ["E", "cross section", "GDR", "Quasi-deuteron"],
               ["MeV", "mb", "mb", "mb"], np.stack([ec, _a(xs), _a(xg), _a(xq)], 1))
    f = _file(f"{_nuc(Z, A)} photo absorption cross sections", Z, A, blocks=[b])
    f["header"]["pre"] = {"particle": "gamma"}
    out["cross_g.tot"] = f
    return out


def _eend_at(cas, g: dict, e_inc: float) -> dict:
    """eend(type) at one incident energy (energies.f90 / grid.f90 emission_end on the run's grid)."""
    from physics.hf.compound.dens_reference import emission_end, incident_kinematics, target_mass_index, total_energy
    from physics.hf.core.constants import talys_constants

    c = talys_constants()
    rg = g["rg"]
    k0 = int(rg.options.k0)
    eninccm, _ = incident_kinematics(
        float(e_inc), k0, float(rg.m.mass_amu[target_mass_index()]),
        float(rg.m.specmass[c["parZ"][k0], c["parN"][k0], k0]),
        float(rg.m.redumass_amu[c["parZ"][k0], c["parN"][k0], k0]), rg.options.flagrel)
    ecomp = total_energy(eninccm, rg.s0[k0], rg.target_e)
    eend, _ = emission_end(rg.egrid, rg.maxen, ecomp, {t: rg.s0[t] for t in range(7)}, rg.ebegin,
                           {t: False for t in range(7)})
    return {t: int(eend[t]) for t in range(7)}


# --------------------------------------------------------------------------------------------- inverse / OMP
def _specmass(Zr: int, Ar: int, k: int) -> float:
    from physics.hf.omp.schrodinger import PARMASS_AMU, nucleus_mass_amu

    m = nucleus_mass_amu(Zr, Ar)
    return m / (m + PARMASS_AMU[k])


def _omp_rows(cas, Zr: int, Ar: int, k: int, e_lab: np.ndarray):
    """The run's outgoing-channel OMP parameters (omppar_<p>.out columns) on the residual (Zr, Ar)."""
    import torch

    from physics.hf.compound.dens_reference import _structure_of
    from physics.hf.omp.inverse import _ported_omp
    from physics.hf.omp.parameters import ejectile_params

    _o, p, _m = _structure_of(int(cas.Zt), int(cas.At))
    p = ejectile_params(p, int(cas.k0))
    return _ported_omp(int(cas.Zt), int(cas.At), Zr, Ar, k, torch.as_tensor(e_lab, dtype=torch.float64),
                       cas.options, p)


_OMPCOLS = ("E", "V", "rv", "av", "W", "rw", "aw", "Vd", "rvd", "avd", "Wd", "rwd", "awd",
            "Vso", "rvso", "avso", "Wso", "rwso", "awso", "rc")
_OMPF = ("v_mev", "rv_fm", "av_fm", "w_mev", "rw_fm", "aw_fm", "vd_mev", "rvd_fm", "avd_fm", "wd_mev", "rwd_fm",
         "awd_fm", "vso_mev", "rvso_fm", "avso_fm", "wso_mev", "rwso_fm", "awso_fm", "rc_fm")


def inverse_files(cas, g: dict, want_inverse: bool, want_omp: bool) -> dict:
    """transmission_<p>.out and cross_<p>.tot (outinverse), omppar_<p>.out (outomp) on the run's emission grid.

    TALYS: inverseout.f90:1 (inverseout), inverseecis.f90:1 (inverseecis)
    Test: tests/hf/test_kwcov_b13.py
    """
    import torch

    from physics.hf.core.grids import EmissionGrid
    from physics.hf.core.tensors import CaseBatch
    from physics.hf.omp.inverse import inverse_channels

    out: dict = {}
    o = cas.options
    trans = cas.trans_of(0, 0)
    eg = g["egrid"]
    zc, ac = int(cas.Zc), int(cas.Ac)
    transen = bool(getattr(o, "flagtransen", True))
    raw = None
    if want_inverse:  # xsopt (and the neutron total / elastic): the raw OMP solve on the same grid
        from physics.hf.compound.dens_reference import _structure_of
        from physics.hf.omp.parameters import ejectile_params

        _o, rgp, _m = _structure_of(int(cas.Zt), int(cas.At))
        rgp = ejectile_params(rgp, int(cas.k0))
        E = g["maxen"] + 1
        mask = (torch.arange(E) >= 1) & (torch.arange(E) <= g["maxen"])
        de = torch.zeros(E, dtype=torch.float64)
        grid = EmissionGrid(torch.tensor(eg[:E], dtype=torch.float64)[None], de[None], mask[None],
                            maxen=torch.tensor([g["maxen"]]))
        cases = CaseBatch(Z=torch.tensor([int(cas.Zt)]), A=torch.tensor([int(cas.At)]),
                          e_inc_mev=torch.tensor([float(cas.enincmax)], dtype=torch.float64),
                          projectile=PARSYM[int(cas.k0)])
        raw = inverse_channels(cases, grid, o, rgp, lmax=60)
    for k in range(1, 7):
        if not _included(o, k):
            continue
        nb, ne = g["ebegin"][k], g["eend"][k]
        if nb >= ne:
            continue
        Zr, Ar = zc - PARZ[k], ac - PARZ[k] - PARN[k]
        if Zr < 1 or Ar <= Zr:
            continue
        sm = _specmass(Zr, Ar, k)
        e_lab = np.asarray([_f32(eg[n] / sm) for n in range(nb, ne + 1)], dtype=float)
        nuc = _nuc(Zr, Ar)
        if want_inverse and k in trans:
            ud, tl, lm = trans[k]
            ud, tl, lm = np.asarray(ud), np.asarray(tl), np.asarray(lm)
            if k == 3:
                cols, units = ["L", "T(L-1,L)", "T(L,L)", "T(L+1,L)", "T(L))"], [""] * 5
            elif k == 6:
                cols, units = ["L", "T(L))"], [""] * 2
            else:
                cols, units = ["L", "T(L-1/2,L)", "T(L+1/2,L)", "T(L))"], [""] * 4

            def row(nen, l):  # noqa: E741
                if k == 3:
                    return [l, ud[nen, l, 0], ud[nen, l, 1], ud[nen, l, 2], tl[nen, l]]
                if k == 6:
                    return [l, ud[nen, l, 1]]
                return [l, ud[nen, l, 0], ud[nen, l, 2], tl[nen, l]]

            blocks = []
            quantity = f"{PARNAME[k]} transmission coefficients"
            if transen:
                for i, nen in enumerate(range(nb, ne + 1)):
                    L = int(lm[nen])
                    data = [row(nen, l) for l in range(0, L + 1)] if L >= 0 else []
                    blk = _block(quantity, cols, units, np.asarray(data, float).reshape(-1, len(cols)),
                                 pre={"energy [MeV]": float(e_lab[i])})
                    blk["entries"] = L
                    blocks.append(blk)
                head = {"particle": PARNAME[k], "number of energies": ne - nb + 1}
            else:
                Lmax = int(lm[ne])
                cols_e = ["E"] + cols[1:]
                units_e = ["MeV"] + units[1:]
                for l in range(0, Lmax + 1):  # noqa: E741
                    data = [[e_lab[i]] + row(nen, l)[1:] for i, nen in enumerate(range(nb, ne + 1))]
                    blocks.append(_block(quantity, cols_e, units_e, data, pre={"L-value": l}))
                head = {"particle": PARNAME[k], "number of angular L-values": Lmax + 1}
            f = _file(f"{nuc} {quantity}", Zr, Ar, blocks=blocks)
            f["header"]["pre"] = head
            f["header"]["pre_indent"] = 0
            f["header"]["transen"] = transen
            out[f"transmission_{PARSYM[k]}.out"] = f
            sig = _a(trans["sigma_reac_mb"])[k - 1] if "sigma_reac_mb" in trans else np.zeros(len(eg))
            sopt = _a(raw.sigma_reac_mb)[0, k - 1]
            idx = list(range(nb, ne + 1))
            if k == 1:
                tot, el = _a(raw.sigma_tot_mb)[0, 0], _a(raw.sigma_shape_el_mb)[0, 0]
                # inversenorm.f90:91: xselas = OMP elastic + xsopt - xsreac (0 without a normalisation)
                data = [[e_lab[i], tot[n], el[n] + sopt[n] - sig[n], sig[n], sopt[n]] for i, n in enumerate(idx)]
                cols, units = ["E", "total", "elastic", "reaction", "OMP reaction"], ["MeV", "mb", "mb", "mb", "mb"]
            else:
                data = [[e_lab[i], sig[n], sopt[n]] for i, n in enumerate(idx)]
                cols, units = ["E", "reaction", "OMP reaction"], ["MeV", "mb", "mb"]
            qx = f"{PARNAME[k]} inverse reaction cross sections"
            f = _file(f"{nuc} {qx}", Zr, Ar, blocks=[_block(qx, cols, units, data)])
            f["header"]["pre"] = {"particle": PARNAME[k]}
            out[f"cross_{PARSYM[k]}.tot"] = f
        if want_omp and not (getattr(o, "flagjlm", False) and k <= 2):
            p = _omp_rows(cas, Zr, Ar, k, e_lab)
            data = [e_lab] + [np.broadcast_to(_a(getattr(p, c)).reshape(-1), e_lab.shape) for c in _OMPF]
            units = ["MeV"] + ["MeV" if c.endswith("_mev") else "fm" for c in _OMPF]
            qo = "optical model parameters"
            f = _file(f"{nuc} {PARNAME[k]} {qo}", Zr, Ar, blocks=[_block(qo, list(_OMPCOLS), units,
                                                                           np.stack(data, 1))])
            pre = {"particle": PARNAME[k]}
            if k <= 2:
                pre["Fermi energy [MeV]"] = _fermi(cas, Zr, Ar, k)
            f["header"]["pre"] = pre
            out[f"omppar_{PARSYM[k]}.out"] = f
    return out


def _fermi(cas, Zr: int, Ar: int, k: int) -> float:
    from physics.hf.omp.parameters import omppar

    try:
        return float(omppar(Zr, Ar, cas.options)[k].ef_mev)
    except Exception:  # noqa: BLE001 - a nucleus without a nucleon OMP entry prints nothing better
        return float("nan")


def _included(o, k: int) -> bool:
    try:
        from physics.hf.input.nuclides import _included_types

        return k in _included_types(o)
    except Exception:  # noqa: BLE001
        return True


def incident_files(cas, energies: list[float], want_inverse: bool, want_omp: bool, ing: dict) -> dict:
    """transmission_inc.out (last energy), omp.out / ompE*.tot (radial potential per energy), spr.opt.

    TALYS: incidentout.f90:1 (incidentout), incidentread.f90:1 (incidentread), spr.f90:1 (spr)
    Test: tests/hf/test_kwcov_b13.py
    """
    import torch

    out: dict = {}
    o = cas.options
    k0 = int(cas.k0)
    Zt, At = int(cas.Zt), int(cas.At)
    if not energies or k0 == 0:
        return out
    tnuc = _nuc(Zt, At)
    if want_inverse:
        e = float(energies[-1])
        inc = cas.incident(e)
        tj = _a(inc.tjl_inc)[0]
        tl = _a(inc.t_l)[0] if inc.t_l is not None else tj[:, 0]
        lmx = int(_f(inc.lmax)) if inc.lmax is not None else tj.shape[0] - 1
        rows = []
        for l in range(0, lmx + 1):  # noqa: E741
            if k0 == 3:
                rows.append([l, tj[l, 0], tj[l, 1], tj[l, 2], tl[l]])
            elif k0 == 6:
                rows.append([l, tj[l, 0]])
            else:
                rows.append([l, tj[l, 0], tj[l, 1], tl[l]])
        cols = {3: ["L", "T(L-1,L)", "T(L,L)", "T(L+1,L)", "T(L))"], 6: ["L", "T(L))"]}.get(
            k0, ["L", "T(L-1/2,L)", "T(L+1/2,L)", "T(L))"])
        b = _block("transmission coefficients", cols, [""] * len(cols), np.asarray(rows, float).reshape(-1, len(cols)))
        f = _file(f"{tnuc}({PARSYM[k0]},tot) transmission coefficients at {e:12.6E} MeV", Zt, At, "target", [b])
        f["header"]["pre"] = {"E-incident [MeV]": e}
        out["transmission_inc.out"] = f
    if want_omp:
        first = float(energies[0])
        sel = [e for e in energies if e <= 0.1 or e == first]
        if k0 == 1 and sel:
            e = sel[-1]
            inc = cas.incident(e)
            from physics.hf.structure.resonances import resonance_parameters

            rd = resonance_parameters(int(cas.Zc), int(cas.Ac), o, cas.params)
            s0, s1, rp = _f(inc.s0) * 1.0e4, _f(inc.s1) * 1.0e4, _f(inc.r_prime_fm)
            pre = {"S0": s0}
            if rd.s0 > 0.0:
                pre.update({"experimental S0": float(rd.s0), "experimental S0 unc.": float(rd.ds0),
                            "C/E S0": s0 / float(rd.s0)})
            pre["S1"] = s1
            if rd.s1 > 0.0:
                pre.update({"experimental S1": float(rd.s1), "experimental S1 unc.": float(rd.ds1),
                            "C/E S1": s1 / float(rd.s1)})
            pre["Rprime [fm]"] = rp
            if rd.r_scat_fm > 0.0:
                pre.update({"experimental Rprime [fm]": float(rd.r_scat_fm),
                            "experimental Rprime unc. [fm]": float(rd.dr_scat_fm),
                            "C/E Rprime": rp / float(rd.r_scat_fm)})
            f = _file(f"{tnuc} basic OMP quantities", Zt, At, "target", [])
            f["header"]["pre"] = pre
            f["header"]["E-incident [MeV]"] = e
            out["spr.opt"] = f
        blocks = []
        for e in energies:
            try:
                blocks.append((e, _potential_block(cas, e)))
            except Exception as exc:  # noqa: BLE001 - a coupled target the port cannot print is recorded
                blocks.append((e, {"error": f"{type(exc).__name__}: {exc}"}))
        if bool(getattr(o, "flagblockomp", True)):
            f = _file(f"{tnuc} {PARNAME[k0]} optical potential", Zt, At, "target",
                      [b for _e, b in blocks if "error" not in b])
            f["header"]["energies"] = [e for e, b in blocks if "error" not in b]
            out["omp.out"] = f
        else:
            for e, b in blocks:
                if "error" in b:
                    continue
                s = f"{e:8.3f}"
                name = f"ompE{int(e):04d}{s[4:]}_{PARSYM[k0]}.tot"
                f = _file(f"{tnuc} {PARNAME[k0]} optical potential at {e:12.6E} MeV", Zt, At, "target", [b])
                out[name] = f
    _ = torch, ing
    return out


def _potential_block(cas, e: float) -> dict:
    """omp.out at one incident energy: the radial potential on ECIS's integration mesh (spherical targets; the
    deformed potential of the coupled band for rotational ones).

    TALYS: incidentread.f90:1 (incidentread), optical.f90:1 (optical)
    Test: tests/hf/test_kwcov_b13.py
    """
    import torch

    from physics.hf.omp import parameters as P
    from physics.hf.omp.potential import radial_potential, rotational_radial_potential
    from physics.hf.omp.schrodinger import PARMASS_AMU, ecis_grid, ecis_kinematics, nucleus_mass_amu

    Zt, At, k0 = int(cas.Zt), int(cas.At), int(cas.k0)
    et = torch.tensor([float(e)], dtype=torch.float64)
    par = P.omp_parameters(Zt, At - Zt, k0, et, cas.params, cas.options, enincmax_mev=float(cas.enincmax))
    mt = nucleus_mass_amu(Zt, At)
    kin = ecis_kinematics(et, PARMASS_AMU[k0], mt, float(Zt * PARZ[k0]))
    h, ism, _rm = ecis_grid(par, mt, kin)
    n = int(ism[0])
    n = 3 * ((n + 2) // 3)
    step = float(f"{float(h[0]):8.5f}")  # incidentread.f90:413 reads ECIS's step as f8.5
    r = torch.arange(1, n + 1, dtype=torch.float64) * step
    band = None
    if P._colltype(Zt, At, cas.options) == "R":
        try:
            from physics.hf.ecis.reference import coupled_band

            b = coupled_band(Zt, At)
            band = (b["rotbeta"], bool(b["deformation_length"]))
        except Exception:  # noqa: BLE001
            band = None
    pot = radial_potential(par, torch.tensor(mt, dtype=torch.float64), r) if band is None else \
        rotational_radial_potential(par, torch.tensor(mt, dtype=torch.float64), r, band[0], band[1])
    data = np.stack([_a(r)] + [_a(pot[c]).reshape(-1) for c in ("V", "W", "Vso", "Wso")], 1)
    blk = _block("optical potential", ["radius", "V", "W", "Vso", "Wso"], ["fm", "MeV", "MeV", "MeV", "MeV"], data)
    blk["title"] = f"{_nuc(Zt, At)} {PARNAME[k0]} optical potential at {float(e):12.6E} MeV"
    return blk


def kd03_table(cas, g: dict) -> dict:
    """outkd: the KD03 lines opticalnp.f90 prints for the nucleon residuals of the run (one row per emission energy
    of the residual's nucleon channel), {particle: {column: ndarray}}.

    TALYS: opticalnp.f90:1 (opticalnp)
    Test: tests/hf/test_kwcov_b13.py
    """
    import torch

    from physics.hf.compound.dens_reference import _structure_of
    from physics.hf.omp.parameters import ejectile_params, ompadjust, omppar

    _o, p, _m = _structure_of(int(cas.Zt), int(cas.At))
    p = ejectile_params(p, int(cas.k0))
    out: dict = {}
    zc, ac = int(cas.Zc), int(cas.Ac)
    for k in (1, 2):
        Zr, Ar = zc - PARZ[k], ac - PARZ[k] - PARN[k]
        try:
            nuc = omppar(Zr, Ar, cas.options)[k]
        except Exception:  # noqa: BLE001
            continue
        F = ompadjust(p, k)

        def fac(name):
            v = F.get(name, 1.0)
            return _f(v) if hasattr(v, "detach") else float(v)

        row = {"Ef": float(nuc.ef_mev)}
        # opticalnp.f90:250-293: name -> (NucleonOMP field, F factor); rw/aw take the real geometry, rwso/awso the so one
        spec = {"rv": ("rv0_fm", "Frv"), "av": ("av0_fm", "Fav"), "v1": ("v1_mev", "Fv1"), "v2": ("v2_per_mev", "Fv2"),
                "v3": ("v3_per_mev2", "Fv3"), "v4": ("v4_per_mev3", "Fv4"), "rw": ("rv0_fm", "Frw"),
                "aw": ("av0_fm", "Faw"), "w1": ("w1_mev", "Fw1"), "w2": ("w2_mev", "Fw2"), "w3": ("w3_mev", "Fw3"),
                "w4": ("w4_mev", "Fw4"), "rwd": ("rvd0_fm", "Frwd"), "awd": ("avd0_fm", "Fawd"),
                "d1": ("d1_mev", "Fd1"), "d2": ("d2_per_mev", "Fd2"), "d3": ("d3_mev", "Fd3"),
                "rvso": ("rvso0_fm", "Frvso"), "avso": ("avso0_fm", "Favso"), "vso1": ("vso1_mev", "Fvso1"),
                "vso2": ("vso2_per_mev", "Fvso2"), "rwso": ("rvso0_fm", "Frwso"), "awso": ("avso0_fm", "Fawso"),
                "wso1": ("wso1_mev", "Fwso1"), "wso2": ("wso2_mev", "Fwso2")}
        for name, (field, fk) in spec.items():
            row[name] = float(getattr(nuc, field)) * fac(fk)
        out[PARSYM[k]] = row
    _ = torch, g
    return out


# --------------------------------------------------------------------------------------------- parameters.dat
def _p(p, key: str, *idx) -> float:
    try:
        return _f(p.at(key, *idx))
    except Exception:  # noqa: BLE001 - a keyword the port does not hold prints as NaN (recorded by the test)
        return float("nan")


def partable_rows(cas, zix: int, nix: int) -> list:
    """partable.f90's rows for one nucleus: (keyword, Z, A, value, qualifier, kind) with kind f (f10.5), e (es12.5),
    g (f8.3), i (i4), d (D0, es12.5).

    TALYS: partable.f90:1 (partable)
    Test: tests/hf/test_kwcov_b13.py
    """
    from physics.hf.structure.resonances import resonance_parameters

    o, p = cas.options, cas.params
    Z, A = (int(v) for v in cas.zn(zix, nix))
    rows: list = []

    def add(key, val, qual="", kind="f"):
        rows.append((key, Z, A, float(val), qual, kind))

    ld0 = cas.ld_of(Z, A)[0]
    ldb = _barrier_ld(cas, Z, A) if bool(o.flagfission) else None
    ld = ldb if ldb is not None else ld0  # the fission chain's density carries the barrier arrays (ibar 0 the same)
    add("a", _f(ld.alev))
    add("aadjust", _p(p, "aadjust", zix, nix))
    add("gammald", _f(ld.gammald))
    add("pair", _f(ld.pair_mev))
    nfis = int(ldb.nfisbar) if ldb is not None else 0
    ldm = int(ld.ldmodel)
    for ibar in range(0, nfis + 1):
        q = f"{ibar:4d}"
        add("Pshift", _f(ld.Pshift_mev[ibar]), q)
        add("Pshiftadjust", _p(p, "pshiftadjust", zix, nix, ibar), q)
        add("deltaW", _f(ld.deltaW_mev[ibar]), q)
        if ldm == 1:
            add("T", _f(ld.T_mev[ibar]), q)
            add("E0", _f(ld.E0_mev[ibar]), q)
            add("Exmatch", _f(ld.Exmatch_mev[ibar]), q)
            add("Tadjust", _p(p, "tadjust", zix, nix, ibar), q)
            add("E0adjust", _p(p, "e0adjust", zix, nix, ibar), q)
            add("Exmatchadjust", _p(p, "exmatchadjust", zix, nix, ibar), q)
        add("Ntop", int(ld.Ntop[ibar]), q, "i")
        add("Nlow", int(ld.Nlow[ibar]), q, "i")
        add("s2adjust", _f(ld.s2adjust[ibar]), q)
        add("ctable", _f(ld.ctable[ibar]), q)
        add("ptable", _f(ld.ptable_mev[ibar]), q)
        add("ctableadjust", _p(p, "ctableadjust", zix, nix, ibar), q)
        add("ptableadjust", _p(p, "ptableadjust", zix, nix, ibar), q)
        add("Ufermi", _f(ld.Ufermi_mev[ibar]), q)
        add("cfermi", _f(ld.cfermi_mev[ibar]), q)
        if bool(o.flagcolall):
            add("Krotconstant", _f(ld.Krotconstant[ibar]), q)
    rd = resonance_parameters(Z, A, o, p)
    if float(rd.d0_ev) != 0.0:
        add("D0", float(np.float32(rd.d0_ev)) * 0.001, "", "e")
    if int(o.phmodel) == 1:
        for key in ("g", "gp", "gn"):
            add(key, _p(p, key, zix, nix) if not _resolved(key) else _preeq_g(cas, Z, A, key))
        add("gnadjust", _p(p, "gnadjust", zix, nix))
        add("gpadjust", _p(p, "gpadjust", zix, nix))
        add("gadjust", _p(p, "gadjust", zix, nix))
    add("Risomer", _p(p, "risomer", zix, nix))
    rows.append(("##psf", Z, A, 0.0, "", "h"))
    gp = cas.gamma_params(Z, A - 1, nucleus=(Z, A)) if A > 1 else None
    add("gamgam", float(rd.gamgam_talys))
    add("gamgamadjust", _p(p, "gamgamadjust", zix, nix))
    gx = int(o.gammax) if hasattr(o, "gammax") else 2
    s, sm1 = int(o.strength), int(o.strengthM1)
    for l in range(1, gx + 1):  # noqa: E741
        if gp is None:
            break
        if s <= 2 or s == 5:
            for key, arr in (("sgr", gp.sgr_mb), ("egr", gp.egr_mev), ("ggr", gp.ggr_mev)):
                add(key, _f(arr[1, l, 1]), f"E{l}", "g")
            for key in ("sgradjust", "egradjust", "ggradjust"):
                add(key, _p(p, key, zix, nix, 1, l, 1), f"E{l}", "g")
        else:
            add("etable", _f(gp.etable_mev[1, l]), f"E{l}")
            add("ftable", _f(gp.ftable[1, l]), f"E{l}")
            add("wtable", _f(gp.wtable[1, l]), f"E{l}")
            for key in ("etableadjust", "ftableadjust", "wtableadjust"):
                add(key, _p(p, key, zix, nix, 1, l), f"E{l}")
        if sm1 in (8, 10):
            add("etable", _f(gp.etable_mev[0, l]), f"M{l}")
            add("ftable", _f(gp.ftable[0, l]), f"M{l}")
            add("wtable", _f(gp.wtable[0, l]), f"M{l}")
            for key in ("etableadjust", "ftableadjust", "wtableadjust"):
                add(key, _p(p, key, zix, nix, 0, l), f"M{l}")
        if sm1 >= 3:
            for c, key in ((1, "upbendc"), (2, "upbende"), (3, "upbendf")):
                add(key, _p(p, "upbend", zix, nix, 0, l, c), f"M{l}", "e")
            for c, key in ((1, "upbendcadjust"), (2, "upbendeadjust"), (3, "upbendfadjust")):
                add(key, _p(p, "upbendadjust", zix, nix, 0, l, c), f"M{l}", "e")
        if gp.ngr[1][l] == 2:
            for key, arr in (("sgr", gp.sgr_mb), ("egr", gp.egr_mev), ("ggr", gp.ggr_mev)):
                add(key, _f(arr[1, l, 2]), f"E{l} 2", "g")
            for key in ("sgradjust", "egradjust", "ggradjust"):
                add(key, _p(p, key, zix, nix, 1, l, 2), f"E{l} 2", "g")
        for key, arr in (("sgr", gp.sgr_mb), ("egr", gp.egr_mev), ("ggr", gp.ggr_mev)):
            add(key, _f(arr[0, l, 1]), f"M{l}", "g")
        for key in ("sgradjust", "egradjust", "ggradjust"):
            add(key, _p(p, key, zix, nix, 0, l, 1), f"M{l}", "g")
    if bool(o.flagfission) and nfis > 0:
        rows.append(("##fission", Z, A, 0.0, "", "h"))
        try:
            from physics.hf.fission.parameters import fission_parameters

            fp = fission_parameters(Z, A, o, p, masses=cas.m)
        except Exception:  # noqa: BLE001
            fp = None
        if fp is not None:
            for ibar in range(1, int(fp.nfisbar) + 1):
                q = f"{ibar:3d}"
                if int(fp.fismodelx) >= 5:  # partable.f90: the WKB (fismodel 5/6) parameters
                    if ibar == 1:
                        add("betafiscor", _p(p, "betafiscor", zix, nix))
                        for key in ("vfiscor", "rmiufiscor"):  # checkvalue.f90:1143-1144: -1 -> 1 without sffactor
                            v = _p(p, key, zix, nix)
                            add(key, 1.0 if (v == -1.0 and not bool(getattr(o, "flagsffactor", False))) else v)
                        if bool(getattr(o, "flagsffactor", False)):
                            add("sffactor", _p(p, "sffactor", zix, nix))
                        add("betafiscoradjust", _p(p, "betafiscoradjust", zix, nix))
                        add("vfiscoradjust", _p(p, "vfiscoradjust", zix, nix))
                        add("rmiufiscoradjust", _p(p, "rmiufiscoradjust", zix, nix))
                    add("bdamp", _p(p, "bdamp", zix, nix, ibar), q)
                    add("bdampadjust", _p(p, "bdampadjust", zix, nix, ibar), q)
                else:
                    add("fisbar", _f(_a(fp.fbarrier_mev)[ibar]), q)
                    add("fishw", _f(_a(fp.fwidth_mev)[ibar]), q)
                    add("fisbaradjust", _p(p, "fisbaradjust", zix, nix, ibar), q)
                    add("fishwadjust", _p(p, "fishwadjust", zix, nix, ibar), q)
                if ibar < int(fp.nfisbar):
                    add("class2width", _p(p, "class2width", zix, nix, ibar), q)
                add("Rtransmom", _p(p, "rtransmom", zix, nix, ibar), q)
                add("Rclass2mom", _p(p, "rclass2mom", zix, nix, ibar), q)
    return rows


def _resolved(key: str) -> bool:
    from physics.hf.input.defaults import PARAM_SPECS

    spec = PARAM_SPECS.get(key)
    return spec is None or bool(spec.resolved_by)


def _preeq_g(cas, Z: int, A: int, key: str) -> float:
    """The single-particle state densities g, gp, gn (A/15, Z/15, N/15 times Kph-scaled; resolved by preeq)."""
    p = cas.params
    zix, nix = cas.options.Zinit - Z, cas.options.Ninit - (A - Z)
    try:
        v = _f(p.at(key, zix, nix))
        if v > 0.0:
            return v
    except Exception:  # noqa: BLE001
        pass
    kph = _f(p["kph"]) if "kph" in p else 15.0
    n = A - Z
    return {"g": A / kph, "gp": Z / kph, "gn": n / kph}[key]


def partable_general(cas, ing: dict, energies=()) -> list:
    """finalout.f90's `## General parameters` rows: (keyword, particle, value, kind).

    TALYS: finalout.f90:1 (finalout)
    Test: tests/hf/test_kwcov_b13.py
    """
    o, p = cas.options, cas.params
    rows: list = []

    def add(key, val, part=None, kind="f"):
        rows.append((key, part, val, kind))

    rows.append(("##level density", None, None, "h"))
    add("ldmodel", int(o.ldmodel_of(0, 0)) if hasattr(o, "ldmodel_of") else int(o.ldmodelCN), kind="i1")
    add("colenhance", "y" if o.flagcolall else "n", kind="a")
    if int(o.ldmodel_of(0, 0) if hasattr(o, "ldmodel_of") else o.ldmodelCN) <= 3:
        add("alphald", _p(p, "alphald", 0, 0))
        add("betald", _p(p, "betald", 0, 0))
        add("gammashell1", _p(p, "gammashell1", 0, 0))
        add("gammashell2", _f(p["gammashell2"]))
        add("pairconstant", _f(p["pairconstant"]))
        add("pshiftconstant", _p(p, "pshiftconstant", 0, 0))
        add("Rspincut", _f(p["rspincut"]))
    add("Rspincutff", _f(p["rspincutff"]))
    add("cglobal", _f(p["cglobal"]), kind="e")
    add("pglobal", _f(p["pglobal"]), kind="e")
    if int(o.phmodel) == 1:
        add("Kph", _f(p["kph"]))
    rows.append(("##photon strength function", None, None, "h"))
    add("strength", int(o.strength), kind="i2")
    add("strengthM1", int(o.strengthM1), kind="i2")
    add("xscaptherm", _xscaptherm(cas), kind="e")
    add("levinger", _f(p["levinger"]), kind="e")
    rows.append(("##pre-equilibrium", None, None, "h"))
    for key in ("M2constant", "M2limit", "M2shift", "Rpipi", "Rnunu", "Rpinu", "Rnupi", "Rgamma", "Rspincutpreeq",
                "Esurf"):
        add(key, _esurf(cas, energies) if key == "Esurf" else (_f(p[key.lower()]) if key.lower() in p else float("nan")))
    for t in range(1, 7):
        for key in ("Cstrip", "Cknock", "Cbreak"):
            add(key, _p(p, key.lower(), t), PARSYM[t])
    for key in ("GMRadjustE", "GMRadjustG", "GMRadjustD", "GQRadjustE", "GQRadjustG", "GQRadjustD", "LEORadjustE",
                "LEORadjustG", "LEORadjustD", "HEORadjustE", "HEORadjustG", "HEORadjustD"):
        add(key, _f(p[key.lower()]) if key.lower() in p else float("nan"))
    rows.append(("##fission", None, None, "h"))
    add("fismodel", int(o.fismodel), kind="i1")
    for key in ("Cnubar1", "Cnubar2", "Tmadjust", "Fsadjust", "Cbarrier"):
        add(key, _f(p[key.lower()]) if key.lower() in p else float("nan"))
    rows.append(("##optical model", None, None, "h"))
    if bool(getattr(o, "flagjlm", False)):
        for key in ("lvadjust", "lwadjust", "lv1adjust", "lw1adjust", "lvsoadjust", "lwsoadjust"):
            add(key, _f(p[key]) if key in p else float("nan"))
    add("deuteronomp", int(o.deuteronomp), kind="i1")
    add("alphaomp", int(o.alphaomp), kind="i1")
    if 3 <= int(o.alphaomp) <= 5:
        add("aradialcor", _f(p["aradialcor"]))
        add("adepthcor", _f(p["adepthcor"]))
    for i in range(1, 8):
        t = 0 if i == 7 else i
        if bool(getattr(o, "flagjlm", False)) and t <= 2:
            continue
        for key in ("v1adjust", "v2adjust", "v3adjust", "v4adjust", "rvadjust", "avadjust", "w1adjust", "w2adjust",
                    "w3adjust", "w4adjust", "rwadjust", "awadjust", "rvdadjust", "avdadjust", "d1adjust", "d2adjust",
                    "d3adjust", "rwdadjust", "awdadjust", "rvsoadjust", "avsoadjust", "vso1adjust", "vso2adjust",
                    "rwsoadjust", "awsoadjust", "wso1adjust", "wso2adjust", "rcadjust"):
            add(key, _p(p, key, t), "e" if t == 0 else PARSYM[t])
    if int(cas.k0) == 1 and ing:
        rows.append(("##resonance parameters", None, None, "h"))
        add("resonance", (int(cas.Zt), int(cas.At), float(ing.get("ing_s0_e4_first", float("nan"))),
                          float(ing.get("ing_rprime_fm_first", float("nan"))), _xscaptherm(cas),
                          float(ing.get("ing_d0theo_ev", float("nan"))), float(ing.get("ing_alev_mev1", float("nan"))),
                          float(ing.get("ing_pair_mev", float("nan"))), float(ing.get("ing_sn_mev", float("nan")))),
            kind="res")
    return rows


def _xscaptherm(cas) -> float:
    """xscaptherm(-1) after thermalxs.f90 (the table row of the target's mass, else the deck, else Kopecky)."""
    try:
        from physics.hf.thermal import therm_of_run

        return float(therm_of_run(cas)["cap"][-1])
    except Exception:  # noqa: BLE001
        return _p(cas.params, "xscaptherm", -1)


def _esurf(cas, energies) -> float:
    """Esurf as finalout prints it: preeq.f90:80-89's value at the last energy pre-equilibrium ran (the input value,
    -1 by default, when it never ran)."""
    import torch

    from physics.hf.preeq.exciton import esurf

    if not energies:
        return _p(cas.params, "esurf")
    e = torch.tensor([float(max(energies))], dtype=torch.float64)
    return _f(esurf(cas.options, cas.params, int(cas.k0), e, int(cas.Ac)))


def _populated_compounds(cas, energies, res) -> list:
    """The compound nuclei multiple emission processes (population >= popeps; the run's residual production)."""
    return list(_history(cas, energies, res).compounds)


def partable_order(cas, energies, res=None) -> list:
    """(Z, A) order of parameters.dat: `structure`'s call order.

    TALYS: nuclides.f90:1 (nuclides)
    Test: tests/hf/test_kwcov_b13.py
    """
    return list(_history(cas, energies, res).order)


def _history(cas, energies, res=None):
    """The nuclei in the order TALYS's `structure` builds them (nuclides.f90 binary residuals, then multiple
    emission's residuals per energy; populations by the energy test of input.nuclides).

    TALYS: nuclides.f90:1 (nuclides), multiple.f90:1 (multiple)
    Test: tests/hf/test_kwcov_b13.py
    """
    from physics.hf.input.nuclides import _energetic_population, structure_history

    populated = None
    if res is not None and res.residual_production_mb:
        # multiple.f90:76: a compound nucleus is processed when its population >= popeps (TALYS 1e-3 mb); the run's
        # own residual production of that nucleus at that energy stands in for its population (output only)
        en = _energetic_population(cas.options, cas.m)
        e_run = [float(x) for x in res.e_inc_mev.tolist()]
        Zi, Ni = int(cas.options.Zinit), int(cas.options.Ninit)
        rp = {}
        for k, v in res.residual_production_mb.items():
            if k.startswith("rp") and ".L" not in k:
                Z, A = int(k[2:5]), int(k[5:8])
                rp[(Zi - Z, Ni - (A - Z))] = [float(x) for x in v.tolist()]

        def populated(zc, nc, e):
            if (zc, nc) == (0, 0):
                return en(zc, nc, e)
            i = min(range(len(e_run)), key=lambda j: abs(e_run[j] - e)) if e_run else None
            return i is not None and rp.get((zc, nc), [0.0] * len(e_run))[i] >= 1.0e-3

    h = structure_history(cas.options, list(energies) or [float(cas.enincmax)], populated=populated, masses=cas.m)
    h_pop = populated if populated is not None else _energetic_population(cas.options, cas.m)
    _POP[id(h)] = h_pop
    return h


_POP: dict = {}


def _levels_sequence(cas, energies, res, h, nuclei, struct: list | None = None) -> list:
    """levelsout's calls in TALYS's order: structure.f90:75 per built nucleus (outbasic / endf), mainout.f90:154-161
    for target and compound nucleus (outlevels), then per incident energy multiple.f90:76-140 (new residuals' structure
    first, then the compound nucleus with flagpop = outbasic). (zix, nix) list, repeats included.

    TALYS: structure.f90:1 (structure), mainout.f90:1 (mainout), multiple.f90:1 (multiple)
    Test: tests/hf/test_kwcov_b13.py
    """
    from physics.hf.input.nuclides import _included_types

    o = cas.options
    on_struct = bool(o.flagbasic) or bool(o.flagendf)
    flagpop = bool(o.flagbasic)
    populated = _POP.get(id(h))
    inc = _included_types(o)
    seq, built, written = [], set(), set()

    def structure(zn):
        built.add(zn)
        if on_struct:
            seq.append(zn)
            if struct is not None:  # KWCOV B15: structure.f90:75-78 also calls gammadecay for this nucleus
                struct.append(zn)

    for typ in range(0, 7):
        if typ != 0 and typ not in inc:
            continue
        structure((PARZ[typ], PARN[typ]))
    if bool(o.flaglevels):
        for zn in nuclei[:2]:
            seq.append(zn)
            written.add(zn)
    for e in sorted(float(x) for x in (energies or [float(cas.enincmax)])):
        for zc in range(0, int(o.maxZ) + 1):
            for nc in range(0, int(o.maxN) + 1):
                if populated is None or not populated(zc, nc, e):
                    continue
                for typ in inc:
                    zn = (zc + PARZ[typ], nc + PARN[typ])
                    if zn not in built:
                        structure(zn)
                if flagpop and bool(o.flaglevels) and (zc, nc) not in written:
                    seq.append((zc, nc))
                    written.add((zc, nc))
    return seq


# --------------------------------------------------------------------------------------------- the whole set
def build(cas, want: dict, energies: list[float], res=None) -> dict:
    """Every ingredient file the Options ask for, {file name: content}.

    TALYS: talysreaction.f90:1 (talysreaction), mainout.f90:1 (mainout)
    Test: tests/hf/test_kwcov_b13.py
    """
    import torch

    from physics.hf.ingredients import ingredients

    out: dict = {}
    g = _grid(cas)
    tix = _target_ix(cas)
    nuclei = [tix] + ([(0, 0)] if int(cas.k0) != 0 else [])
    if bool(getattr(cas.options, "flagbasic", False)) and (want.get("levels") or want.get("density")):
        # outbasic sets flagpop: multiple.f90:330-337 writes levels / densities of every populated compound nucleus
        try:
            for zn in _populated_compounds(cas, energies, res):
                if zn not in nuclei:
                    nuclei.append(zn)
        except Exception:  # noqa: BLE001
            pass
    ing = {}
    with torch.no_grad():
        if want.get("gamma") or want.get("partable"):
            try:
                ing = ingredients(cas)
            except Exception:  # noqa: BLE001 - only the psf / parameters.dat header numbers need it
                ing = {}
        if want.get("levels"):
            o = cas.options
            try:
                h = _history(cas, energies, res)
                prior, prior_s, order = h.prior_call, h.prior_call_at_structure, list(h.order)
            except Exception:  # noqa: BLE001
                prior, prior_s, order = frozenset(), frozenset(), []
            struct: list = []
            try:
                seq = [(z, n, (z, n) in prior) for z, n in _levels_sequence(cas, energies, res, h, nuclei, struct)]
            except Exception:  # noqa: BLE001
                seq = [(z, n, (z, n) in prior) for z, n in nuclei] if bool(o.flaglevels) else []
            for zix, nix in struct:  # KWCOV B15: gamma<ZZZAAA>.tot of every nucleus structure builds (outbasic / endf)
                Z, A = (int(v) for v in cas.zn(zix, nix))
                if Z < 1 or A <= Z:
                    continue
                name, f = gamma_decay_file(cas, zix, nix, (zix, nix) in prior_s)
                out[name] = f
            block = bool(getattr(o, "flagblocklevels", False))
            names = []
            for zix, nix, pr in seq:
                Z, A = (int(v) for v in cas.zn(zix, nix))
                if Z < 1 or A <= Z:
                    continue
                name, f = levels_file(cas, zix, nix, pr)
                out[name] = f  # a later write replaces the file (status = 'replace'), as TALYS
                names.append(name)
            if block:  # blocklevels y: every write appended to one levels.out (levelsout.f90:85-92)
                out["levels.out"] = {"sequence": names}
        if want.get("density"):
            for zix, nix in nuclei:
                out.update(density_files(cas, zix, nix))
        if want.get("gamma") and energies:
            out.update(gamma_files(cas, g, float(energies[0]), ing))
        if want.get("inverse") or want.get("omp"):
            out.update(inverse_files(cas, g, bool(want.get("inverse")), bool(want.get("omp"))))
            out.update(incident_files(cas, energies, bool(want.get("inverse")), bool(want.get("omp")), ing))
        if want.get("kd"):
            out["kd03"] = kd03_table(cas, g)
        if want.get("endf") and len(energies) > 1:  # endf.f90: `if (Ninc == 1) return`
            out.update(endf_info(cas, energies, res))
        if want.get("sacs") and res is not None:
            out["sacs.dat"] = sacs_table(cas, res)
        if want.get("partable"):
            rows = []
            for zix, nix in partable_order(cas, energies, res):
                Z, A = (int(v) for v in cas.zn(zix, nix))
                if Z < 1 or A <= Z:
                    continue
                try:
                    rows.append(((Z, A), partable_rows(cas, zix, nix)))
                except Exception as exc:  # noqa: BLE001 - a nucleus the port cannot build is named, not hidden
                    rows.append(((Z, A), [("##error", Z, A, 0.0, f"{type(exc).__name__}: {exc}", "h")]))
            gen = partable_general(cas, ing, energies)
            pd = {"nuclei": rows, "general": gen, "Zt": int(cas.Zt), "At": int(cas.At), "k0": int(cas.k0)}
            pd["text"] = partable_text(pd)
            out["parameters.dat"] = pd
    return out


# --------------------------------------------------------------------------------------------- writers
def _num(v) -> str:
    if isinstance(v, (int, np.integer)) or (isinstance(v, float) and False):
        return str(v)
    return f"{float(v):13.6E}"


def _kv(indent: int, key: str, v) -> str:
    if isinstance(v, str):
        return f"#{' ' * indent}{key}: {v}"
    if isinstance(v, (bool, np.bool_)):
        return f"#{' ' * indent}{key}: {'y' if v else 'n'}"
    if isinstance(v, (int, np.integer)):
        return f"#{' ' * indent}{key}: {int(v)}"
    return f"#{' ' * indent}{key}: {float(v):13.6E}"


def _header_lines(h: dict) -> list[str]:
    from datetime import date

    lines = ["# header: ", f"#   title: {h.get('title', '')}", f"#   source: {SOURCE}", "#   user: INCOGNITA",
             f"#   date: {date.today().isoformat()}", "#   format: YANDF-0.4"]
    kind = h.get("kind", "residual")
    lines += [f"# {'target' if kind == 'target' else 'residual'}: ", f"#   Z: {h['Z']}", f"#   A: {h['A']}",
              f"#   nuclide: {h['nuclide']}"]
    return lines


def _fmt_row(vals, kinds) -> str:
    s = ""
    for v, k in zip(vals, kinds):
        if k == "i":
            s += f"{int(round(v)):6d}" + " " * 9
        elif k == "I":
            s += f"{int(round(v)):9d}" + " " * 6
        else:
            s += f"{float(v):15.6E}"
    return s


def _block_lines(b: dict, kinds=None, indent: int = 2) -> list[str]:
    pad = " " * indent
    lines = []
    if b.get("pre"):
        lines.append(f"#{pad}parameters: ")
        lines += [_kv(indent + 2, k, v) for k, v in b["pre"].items()]
    lines += [f"#{pad}quantity: ", f"#{pad}  type: {b['quantity']}"]
    lines += [_kv(indent + 2, k, v) for k, v in b.get("meta", {}).items()]
    n = int(b["data"].shape[0]) if "entries" not in b else int(b["entries"])
    lines += [f"#{pad}datablock: ", f"#{pad}  columns: {len(b['columns'])}", f"#{pad}  entries: {n}"]
    lines.append("##" + "".join(f"{c:^15}" for c in b["columns"]))
    lines.append("##" + "".join(f"{('[' + u + ']'):^15}" for u in b["units"]))
    kinds = kinds or ["e"] * len(b["columns"])
    for r in b["data"]:
        lines.append(_fmt_row(r, kinds))
    return lines


def _yandf_text(name: str, f: dict) -> str:
    h = f["header"]
    lines = _header_lines(h)
    if name.startswith("levels"):
        return _levels_text(f)
    if h.get("pre"):
        ind = int(h.get("pre_indent", 2))
        lines.append(f"#{' ' * (ind + 1)}parameters: ")
        lines += [_kv(ind + 2, k, v) for k, v in h["pre"].items()]
    if h.get("pre2"):
        lines.append("#   parameters: ")
        lines += [_kv(4, k, v) for k, v in h["pre2"].items()]
    for b in f["blocks"]:
        kinds = None
        if b["columns"][:2] == ["E", "Level"]:
            kinds = ["e", "i"] + ["e"] * (len(b["columns"]) - 2)
        elif b["columns"][0] == "L":
            kinds = ["i"] + ["e"] * (len(b["columns"]) - 1)
        lines += _block_lines(b, kinds)
    return "\n".join(lines) + "\n"


def _levels_text(f: dict) -> str:
    b = f["blocks"][0]
    lines = _header_lines(f["header"])
    lines.append("#   parameters: ")
    lines += [_kv(4, k, v) for k, v in b["pre"].items()]
    br = b["branches"]
    n = b["data"].shape[0] + br.shape[0]
    lines += ["#   quantity: ", "#     type: Nuclear masses and levels", "#   datablock: ", "#     columns: 11",
              f"#     entries: {n}"]
    cols = ["Level", "Energy", "Spin", "Parity", "Num._Branches", "Branch._level", "Branch._ratio", "Intern._conv",
            "Half-life", "Assignment", "ENSDF"]
    un = ["", "MeV", "", "", "", "", "%", "", "sec", "", ""]
    lines.append("##" + "".join(f"{c:^15}" for c in cols))
    lines.append("##" + "".join(f"{('[' + u + ']'):^15}" for u in un))
    for i, r in enumerate(b["data"]):
        tau = f"{r[5]:15.6E}" if r[5] != 0.0 else " " * 15
        par = "+" if r[3] > 0 else "-"
        a = (b["assign"][i] + "   ")[:3]
        lines.append(f"{int(r[0]):6d}{'':9s}{r[1]:15.6E}{'':7s}{r[2]:4.1f}{'':13s}{par}{'':9s}{int(r[4]):6d}{'':51s}"
                     f"{tau}{'':6s}{a} {b['ensdf'][i][:18]:18s}".rstrip())
        for j, row in enumerate(x for x in br if int(x[0]) == i):
            ba = b["branch_assign"][i][j] if j < len(b["branch_assign"][i]) else " "
            lines.append(f"{'':75s}--->{int(row[1]):6d}{'':9s}{row[2]:8.4f}{'':4s}{row[3]:15.6E}{'':26s}{ba}".rstrip())
    return "\n".join(lines) + "\n"


def _nld_text(f: dict) -> str:
    h = f["header"]
    Z, A = h["Z"], h["A"]
    sym = h["nuclide"].rstrip("0123456789")
    out = []
    for b in f["blocks"]:
        par = int(b["meta"]["Parity"])
        word = "Positive" if par == 1 else "Negative"
        out.append(" " * 20 + "*" * 96)
        out.append(" " * 20 + f"*  Z={Z:3d} A={A:3d}: {word:>8s}-Parity Spin-dependent Level Density [MeV-1] for "
                   f"{sym:2s}{A:3d} and ldmodel={h['ldmodel']:2d}  *")
        out.append(" " * 20 + "*" * 96)
        if A % 2 == 0:
            out.append(" U[MeV]  T[MeV]  NCUMUL   RHOOBS   RHOTOT  " + "".join(f"   J={j:02d}  " for j in range(30)))
        else:
            out.append(" U[MeV]  T[MeV]  NCUMUL   RHOOBS   RHOTOT  " + "".join(f"  J={j:02d}/2 " for j in range(1, 60, 2)))
        for r in b["data"]:
            out.append(f" {r[0]:6.2f}{r[1]:7.3f} " + "".join(f"{v:9.2E}" for v in list(r[2:5]) + list(r[5:35])))
        out.append("")
    return "\n".join(out) + "\n"


def partable_text(pd: dict) -> str:
    """parameters.dat as partable.f90 / finalout.f90 write it.

    TALYS: partable.f90:1 (partable), finalout.f90:1 (finalout), nuclides.f90:1 (nuclides)
    Test: tests/hf/test_kwcov_b13.py
    """
    from datetime import date

    Zt, At, k0 = pd["Zt"], pd["At"], pd["k0"]
    L = ["## header:", f"##   title: {_nuc(Zt, At)}({PARSYM[k0]},x) nuclear model parameters", f"##   source: {SOURCE}",
         "##   user: INCOGNITA", f"##   date: {date.today().isoformat()}", "##   format: YANDF-0.4", "## target:",
         f"##   Z: {Zt}", f"##   A: {At}", f"##   nuclide: {_nuc(Zt, At)}"]
    for (Z, A), rows in pd["nuclei"]:
        L += ["## residual:", f"##   Z: {Z}", f"##   A: {A}", f"##   nuclide: {_nuc(Z, A)}", "## parameters: ",
              "##   level density"]
        for key, z, a, v, q, kind in rows:
            if kind == "h":
                if key == "##psf":
                    L += ["## parameters: ", "##   photon strength function"]
                elif key == "##fission":
                    L += ["##", "## parameters: ", "##   fission", "##"]
                else:
                    L.append(f"## {key} {q}")
                continue
            k = f"{key:15s}"
            if kind == "i":
                L.append(f"{k}{z:4d}{a:4d}{int(v):4d}{q}")
            elif kind == "e":
                L.append(f"{k}{z:4d}{a:4d}{v:12.5E}{(' ' + q) if q else ''}")
            elif kind == "g":
                L.append(f"{k}{z:4d}{a:4d}{v:8.3f} {q}")
            else:
                qq = q if (not q or q.startswith(" ")) else " " + q
                L.append(f"{k}{z:4d}{a:4d}{v:10.5f}{qq}")
    for key, part, v, kind in pd["general"]:
        if kind == "h":
            L += ["## General parameters:", f"##   {key[2:]}"]
            continue
        if kind == "res":
            L.append("## Z   A     S0        R      xs(therm)    D0         a         P        Sn")
            L.append("##" + f"{v[0]:4d}{v[1]:4d}" + "".join(f"{x:10.3E}" for x in v[2:]))
            continue
        k = f"{key:15s}" if part is None else f"{key:14s}{part}"
        if kind == "a":
            L.append(f"{k}{v}")
        elif kind in ("i1", "i2"):
            L.append(f"{k}{int(v):{kind[1]}d}")
        elif kind == "e":
            L.append(f"{k}{float(v):12.5E}")
        else:
            L.append(f"{k}{float(v):10.5f}")
    return "\n".join(L) + "\n"


def write_files(ingout: dict, outdir) -> list[str]:
    """Write Results.ingout with TALYS's file names (YANDF headers; nld*.tab and parameters.dat in their own
    formats; kd03 as kd03.out, a plain table).

    TALYS: the writers listed in the module docstring
    Test: tests/hf/test_kwcov_b13.py
    """
    p = Path(outdir)
    p.mkdir(parents=True, exist_ok=True)
    done = []
    for name, f in ingout.items():
        if name == "levels.out":  # blocklevels y
            text = "".join(_levels_text(ingout[n]) for n in f["sequence"])
        elif name.startswith("levels") and "levels.out" in ingout:
            continue
        elif name in ("parameters.dat", "tefal.inf", "energies.endf", "sacs.dat"):
            text = f["text"]
        elif name.startswith("gamma") and name.endswith(".tot"):
            text = _gammadecay_text(f)
        elif name.startswith("nld"):
            text = _nld_text(f)
        elif name == "kd03":
            text = "".join(f"# {k} " + " ".join(f"{c}={v:.6E}" for c, v in row.items()) + "\n" for k, row in f.items())
            name = "kd03.out"
        elif name == "omp.out" or name.startswith("ompE"):
            text = "".join(_yandf_text(name, {"header": {**f["header"], "title": b.get("title", f["header"]["title"])},
                                               "blocks": [b]}) for b in f["blocks"])
        else:
            text = _yandf_text(name, f)
        (p / name).write_text(text)
        done.append(name)
    return done
