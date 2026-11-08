"""KWCOV B3 (ANGOUT): discrete-state angular distributions and Legendre coefficients on TALYS's keywords, OUTPUT ONLY.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

What it gives (TALYS's file names, without the energy, as Results.angular keys; arrays (C, ...) on the run's energies):

    <k0><t>ang.L<nn>              discad = directad + compad  [mb/sr] on TALYS's angle grid (angle(i) = i * 180 / nangle)
    <k0><t>ang.L<nn>:direct       directad: shape elastic / DWBA / coupled channels + discrete pre-equilibrium (Kalbach)
    <k0><t>ang.L<nn>:compound     compad: sum_L (2L+1) cleg_L P_L when flagcompang, else sigma_compound / (4 pi)
    <k0><k0>ang.L00:ruth          charged projectile: elastic / Rutherford (ECIS's ratio: direct over Rutherford)
    <k0><k0>ang.L00:nucint        charged projectile: nuclear + interference = discad (1 - 1/ruth)
    <k0><t>leg.L<nn>              tleg = dleg + cleg, L = 0..J2end (with outlegendre)
    <k0><t>leg.L<nn>:direct|:compound|:normalized|:endf6     dleg, cleg, tlegnor, cleg0
    angle                         (nangle+1,) degrees

The angle files follow angleout.f90: the elastic one always, the inelastic and other discrete ones for the levels in
`fileangle` (every level with `outangle y`) with a non-zero level cross section; the Legendre files with `outlegendre y`.
`write_files` writes them in TALYS's YANDF format and names (nn0014.000ang.L01, or nnang.L01 with all energies appended
under `blockangle y`).

Switches: the deck keywords (Options) `outangle`, `fileelastic` (angleout.f90 runs when either is y: output.f90:65),
`fileangle`, `outlegendre`, `blockangle`, `angles` (nangle), `cpang`; the port switch `INCOGNITA_ANGOUT=1` (= outangle y +
outlegendre y); `INCOGNITA_ANGOUT_DIR=<dir>` also writes the files. Default: none of them, nothing is computed and every
array of every gate is unchanged. Any of them turns the SPECOUT recorders on for the run (specout.enabled).

Where the numbers come from (none of it feeds back into the engine):
* shape elastic (neutron): `specang.shape_elastic_spherical` / `specang.coupled` (engine's own OMP / CC solve);
  charged projectile: `charged_elastic` below, the same S-matrix with the Coulomb amplitude and phases added;
* direct inelastic: `specang.dwba_levels` (DWBA deck the engine ran) or `specang.coupled` (coupled levels);
* discrete pre-equilibrium: xspreeqdisc(type, i) * kalbach(type, Einc, eoutdis(type, NL), angle) (preeqang.f90:88-103);
* compound: `specang.record_energy` (projectile's own residual, compound.ceang) and `compound.ceang_types` (every other
  residual), normalised to the engine's own level populations; isotropic xscompdisc / (4 pi) without flagcompang.

TALYS routines ported here (file:line of the subroutine statement):
    angdis.f90:1 (angdis)          compad, discad, elasni, tleg, tlegnor, cleg0, the cleg(2) <= cleg(0) clamp
    angleout.f90:1 (angleout)      file selection, names and columns
    preeqang.f90:1 (preeqang)      discrete pre-equilibrium Kalbach term
    write_block.f90:1              YANDF headers
Task: T10 (physics/hf/CONTRACT.md section 7; KWCOV batch B3, output only). Acceptance test: KWCOV-B3
(tests/hf/test_angout.py, scripts/kwcov/b3_compare.py, docs/hf/COVERAGE_PLAN.md).
"""

from __future__ import annotations

import datetime
import math
import os
from pathlib import Path

import numpy as np

ENV = "INCOGNITA_ANGOUT"
ENV_DIR = "INCOGNITA_ANGOUT_DIR"
PARSYM = "gnpdtha"
MT0 = (101, 50, 600, 650, 700, 750, 800)  # angleout.f90:85-91
NLEV_ALL = 199  # compound Legendre for every discrete level (comptarget.f90:521 NL = Nlast)
LMAXC = 60  # compound Legendre order kept for the other residuals (cleg above J2end is zero)

_SET: dict | None = None  # the current run's settings (begin_run); None = off
META: dict = {}  # last build: per-energy and per-level data `write_files` needs


def _on(v) -> bool:
    return str(v).strip().lower()[:1] in ("1", "y", "t") or str(v).strip().lower() == "on"


def settings(options=None) -> dict | None:
    """angleout's switches for a run, or None when angleout.f90 would not run (outangle n and fileelastic n).

    TALYS: output.f90:1 (output) line 65, input_output.f90:1, input_outfiles.f90:1
    Test: tests/hf/test_angout.py
    """
    env = _on(os.environ.get(ENV, "0"))
    if options is not None:
        flagang, fe = bool(getattr(options, "flagang", False)), bool(getattr(options, "fileelastic", False))
        leg, block = bool(options.flaglegendre), bool(getattr(options, "flagblockangle", False))
        fa, nangle, cpang = set(getattr(options, "fileangle", ())), int(options.nangle), bool(options.flagcpang)
        k0 = int(options.k0)
    else:  # before a Cascade exists: the active deck lines (fitlib) carry the same keywords
        from physics.hf.input import fitlib

        ov = {str(k).lower(): v for k, v in fitlib.option_overrides().items()}
        endf = _on(ov.get("endf", "n"))
        flagang, fe = _on(ov.get("outangle", endf)), _on(ov.get("fileelastic", endf))
        leg, block = _on(ov.get("outlegendre", endf)), _on(ov.get("blockangle", endf))
        fa = {int(x) for x in str(ov.get("fileangle", "")).replace(",", " ").split()}
        nangle, cpang, k0 = int(ov.get("angles", 90)), _on(ov.get("cpang", "n")), None
    if env:
        flagang, leg = True, True
    from physics.hf import specobs

    from physics.hf import recoil

    # KWCOV B4 / B12: the DDX and the recoils (angdisrecoil.f90) need discad of every level
    ddx = options is not None and (specobs.ddx_wanted(options) or recoil.wanted_for(options))
    if not (flagang or fe or ddx):
        return None
    return dict(flagang=flagang, fileelastic=fe, fileangle_all=flagang, fileangle=fa, legendre=leg, block=block,
                nangle=nangle, cpang=cpang, k0=k0, ddx=ddx, internal=not (flagang or fe))


def wanted() -> bool:
    """The run being set up asks for angular output (the SPECOUT recorders must be on).

    TALYS: (none -- a port switch)
    Test: tests/hf/test_angout.py
    """
    return _SET is not None or settings() is not None


def active() -> bool:
    """A run with angular output is in progress (begin_run saw the switch).

    TALYS: (none -- a port switch)
    Test: tests/hf/test_angout.py
    """
    return _SET is not None


def begin_run(cas) -> bool:
    """Called by specout.begin_run: fix the run's settings from its Options. Returns whether the run wants angles.

    TALYS: (none -- a port switch)
    Test: tests/hf/test_angout.py
    """
    global _SET
    _SET = settings(cas.options)
    return _SET is not None


def end_run() -> None:
    """The run is over: the switch is read again for the next one.

    TALYS: (none -- a port switch)
    Test: tests/hf/test_angout.py
    """
    global _SET
    _SET = None


def nlev_target(default: int) -> int:
    """Discrete levels of the projectile's residual that get compound Legendre coefficients (all of them with angles on).

    TALYS: comptarget.f90:1 (comptarget) line 521, NL = Nlast
    Test: tests/hf/test_angout.py
    """
    return NLEV_ALL if _SET is not None else default


def angles(nangle: int) -> np.ndarray:
    """angle(iang) = iang * (180 / nangle), single precision (grid.f90:262-265).

    TALYS: grid.f90:1 (grid)
    Test: tests/hf/test_angout.py
    """
    f32 = np.float32
    dang = f32(180.0) / f32(nangle)
    return np.array([f32(i) * dang for i in range(nangle + 1)], dtype=np.float32).astype(float)


def flagcompang(e_inc_mev: float, s: dict | None = None) -> bool:
    """energies.f90: flagcompang = (k0 == 1 or cpang) and outangle and Einc <= 50 MeV.

    TALYS: energies.f90:1 (energies) line 136
    Test: tests/hf/test_angout.py
    """
    s = _SET if s is None else s
    return bool(s and (s["k0"] == 1 or s["cpang"]) and s["flagang"] and np.float32(e_inc_mev) <= np.float32(50.0))


def _np(x):
    if hasattr(x, "detach"):
        x = x.detach().cpu().numpy()
    return np.asarray(x, float)


def _clamp2(c: np.ndarray) -> np.ndarray:
    """angdis.f90:76: cleg(L=2) = min(cleg(2), cleg(0))."""
    if c.size > 2:
        c = c.copy()
        c[2] = min(c[2], c[0])
    return c


# ------------------------------------------------------------------------------------------------ per incident energy
def record(rec: dict, cas, st, binp, cinp, etot, a_e, fkw, ci, pop, b2, b) -> None:
    """specang.record_energy's extra for the angle files: every residual's level data, J2end, and (flagcompang) the
    compound Legendre coefficients of the other residuals' levels, into rec["angx"].

    TALYS: comptarget.f90:1, angdis.f90:1 (angdis)
    Test: tests/hf/test_angout.py
    """
    s = _SET
    if s is None:
        return
    k0, e = int(binp.k0), float(binp.e_inc_mev)
    x = {"types": {}, "flagcompang": flagcompang(e)}
    if ci is None or not hasattr(ci, "residuals"):
        from physics.hf.compound.chain import compound_inputs

        ci = compound_inputs(cas, st, binp, cinp, etot, a_e, **fkw)
    x["j2end"] = int(ci.j2end)
    p = pop.pop_mb[0]
    xd = {t: _np(v) for t, v in b.xsdisc_mb.items()}
    for t, disc in xd.items():
        g = binp.grids.get(t)
        if g is None:
            continue
        nl = len(disc) - 1
        dd = _np(b2.xsdirdisc_mb[t])[: nl + 1] if t in b2.xsdirdisc_mb else np.zeros(nl + 1)
        dd = np.pad(dd, (0, nl + 1 - dd.size))
        cd = getattr(b, "xscompdisc_mb", {}).get(t) if hasattr(b, "xscompdisc_mb") else None
        cd = _np(cd)[: nl + 1] if cd is not None else np.maximum(disc - dd, 0.0)
        p0 = getattr(b, "xspopex0_mb", {}).get(t) if hasattr(b, "xspopex0_mb") else None
        p0 = _np(p0)[: nl + 1] if p0 is not None else disc.copy()
        ex = _np(g.ex_mev)[: nl + 1]
        S_t = float(_np(cas.m.s_mev)[0, 0, t])
        d = dict(xsdisc=disc, xsdirdisc=dd, xscompdisc=cd, xspopex0=np.pad(p0, (0, nl + 1 - p0.size)), e=ex,
                 j=_np(g.jdis)[: nl + 1], p=_np(g.parlev)[: nl + 1].astype(int), eout_nl=float(etot) - S_t - float(ex[nl]),
                 pop=np.array([float(p[t, n].sum()) if n < p.shape[1] else 0.0 for n in range(nl + 1)]))
        x["types"][t] = d
    if x["flagcompang"]:
        others = [t for t in x["types"] if t != k0 and t in ci.residuals]
        if others and ci.flagwidth and ci.wmode > 1:  # HRTW / GOE pair weights are not ported (ceang: Moldauer only)
            x["note"] = f"wmode {ci.wmode}: compound angular distributions isotropic"
            others = []
        if others:
            import torch

            from physics.hf.compound import ceang_types

            nlev = {t: len(x["types"][t]["xsdisc"]) - 1 for t in others}
            with torch.inference_mode():
                got = ceang_types.pair_blocks(ci, others, nlev)
            two_i0, two_s0 = int(binp.targetspin2), int(ci.residuals[k0].parspin2)
            lmax = min(x["j2end"], LMAXC)
            for t in others:
                d, r = x["types"][t], ci.residuals[t]
                leg = np.zeros((len(d["xsdisc"]), lmax + 1))
                for n in range(len(d["xsdisc"])):
                    if n not in got[t]["sums"]:
                        continue
                    two_in = int(r.jdis2[n])
                    c = ceang_types.legendre(got[t], n, two_i0, two_s0, two_in, int(r.parspin2), lmax)
                    eng = float(d["pop"][n])
                    if c[0] > 0 and eng > 0:
                        c = c * eng / (4 * math.pi * c[0])
                    elif eng > 0:
                        c = np.zeros(lmax + 1)
                        c[0] = eng / (4 * math.pi)
                    leg[n] = c
                d["comp_leg"] = leg
    rec["angx"] = x


# ------------------------------------------------------------------------------------------------ charged elastic
def charged_elastic(cas, energies: list[float]) -> dict:
    """Elastic scattering of a charged projectile (spin 1/2 or 0, spherical target) on TALYS's angle grid: the engine's
    OMP S-matrix (Coulomb-relative, as ECIS's) with the point-Coulomb amplitude and Coulomb phases,

        A = f_C + 1/(2ik) sum_l e^{2i sigma_l} [(l+1)(S_l+ - 1) + l (S_l- - 1)] P_l,  B = 1/(2ik) sum_l e^{2i sigma_l}
        (S_l+ - S_l-) P_l^1,  f_C = -eta / (2k sin^2(theta/2)) exp(-i eta ln sin^2(theta/2) + 2i sigma_0),

    dsigma/dOmega = |A|^2 + |B|^2 (mb/sr) and the ratio to Rutherford |f_C|^2 (ECIS's kinematics: relativistic k, eta).
    At 0 degrees the Rutherford cross section is infinite: the row has ratio 1 and cross section 0.

    TALYS: incidentread.f90:1 (incidentread) lines 355-363 (ECIS's elastic angular file), ecist.f:1 (ecist)
    Test: tests/hf/test_angout.py
    """
    import torch
    from scipy.special import loggamma, lpmv

    from physics.hf.core.tensors import DTYPE
    from physics.hf.omp.incident import talys_constants
    from physics.hf.omp.inverse import _ported_omp
    from physics.hf.omp.schrodinger import PARMASS_AMU, PARSPIN, PARZ, nucleus_mass_amu, solve_radial

    s = _SET or {}
    Z, A, k0 = int(cas.Zt), int(cas.At), int(cas.k0)
    if k0 <= 1 or cas._coupled_band() is not None:
        return {}
    th = angles(int(s.get("nangle", cas.options.nangle)))
    x = np.cos(np.radians(th))
    sin2 = np.sin(np.radians(th) / 2.0) ** 2
    m_t = nucleus_mass_amu(Z, A)
    numl = int(talys_constants()["numl"])
    out_d = np.zeros((len(energies), th.size))
    out_r = np.zeros((len(energies), th.size))
    for i, e0 in enumerate(energies):
        nj = min(max(20, int(2.4 * 1.25 * A ** (1.0 / 3.0) * 0.22 * math.sqrt(PARMASS_AMU[k0] * e0))), numl)
        e = torch.tensor([e0], dtype=DTYPE)
        p = _ported_omp(Z, A, Z, A, k0, e, cas.options, cas.params)
        sol = solve_radial(p, e, PARMASS_AMU[k0], m_t, float(Z * PARZ[k0]), PARSPIN[k0], nj)
        S, jv, valid = sol.smat.numpy()[0], sol.jvalues.numpy(), sol.valid.numpy()
        k = float(sol.kin.k_fm.numpy().reshape(-1)[0])
        eta = float(sol.kin.eta.numpy().reshape(-1)[0])
        L = S.shape[0]
        ll = np.arange(L)
        sig = np.array([loggamma(l + 1 + 1j * eta).imag for l in ll])
        ph = np.exp(2j * sig)
        sp = np.ones(L, complex)
        sm = np.ones(L, complex)
        spin = PARSPIN[k0]
        for l in range(L):  # noqa: E741
            for jj in range(S.shape[1]):
                if not valid[l, jj]:
                    continue
                if abs(jv[l, jj] - (l + spin)) < 1e-6:
                    sp[l] = S[l, jj]
                elif abs(jv[l, jj] - (l - spin)) < 1e-6:
                    sm[l] = S[l, jj]
        P0 = np.array([lpmv(0, l, x) for l in ll])
        if spin == 0.0:
            a_n = ((2 * ll + 1) * ph * (sp - 1.0)) @ P0 / (2j * k)
            b_n = np.zeros_like(a_n)
        else:
            P1 = np.array([lpmv(1, l, x) for l in ll])
            sm[0] = 1.0
            a_n = (ph * ((ll + 1) * (sp - 1.0) + ll * (sm - 1.0))) @ P0 / (2j * k)
            b_n = (ph * (sp - sm)) @ P1 / (2j * k)
        with np.errstate(divide="ignore", invalid="ignore"):
            fc = -eta / (2 * k * sin2) * np.exp(-1j * eta * np.log(sin2) + 2j * sig[0])
            ruth_xs = (eta / (2 * k * sin2)) ** 2 * 10.0
            xs = (np.abs(fc + a_n) ** 2 + np.abs(b_n) ** 2) * 10.0  # fm^2/sr -> mb/sr
            ratio = xs / ruth_xs
        zero = sin2 <= 0.0
        xs[zero], ratio[zero] = 0.0, 1.0
        out_d[i], out_r[i] = xs, ratio
    return {"el_direct": out_d, "el_ruth": out_r, "el_angle": th}


# ------------------------------------------------------------------------------------------------ run level
def _series(c: np.ndarray, x: np.ndarray) -> np.ndarray:
    from numpy.polynomial.legendre import legval

    c = np.asarray(c, float)
    return legval(x, (2 * np.arange(c.size) + 1) * c) if c.size else np.zeros_like(x)


def _direct_level_leg(ang: dict, i: int, n: int, level_e: float) -> np.ndarray | None:
    """Direct (DWBA or coupled-channels) Legendre coefficients of the projectile's level n at energy index i."""
    if "cc_leg" in ang and "cc_level_e" in ang:
        ce = np.asarray(ang["cc_level_e"], float)
        hit = np.flatnonzero(np.abs(ce - level_e) < 1e-4)
        if hit.size and hit[0] > 0:
            return np.asarray(ang["cc_leg"][i, hit[0]], float)
    if "dwba_leg" in ang:
        d = np.asarray(ang["dwba_leg"])
        if n < d.shape[1] and np.any(d[i, n]):
            return np.asarray(d[i, n], float)
    return None


def build() -> dict[str, np.ndarray]:
    """The Results.angular arrays of the recorded run (see module doc); fills META for `write_files`.

    TALYS: angdis.f90:1 (angdis), angleout.f90:1 (angleout), preeqang.f90:1 (preeqang)
    Test: tests/hf/test_angout.py
    """
    from physics.hf import specang, specout

    s = _SET
    META.clear()
    if s is None or not specout.ENERGIES:
        return {}
    run = specout.RUN or {}
    ang = run.get("ang", {})
    k0 = int(s["k0"])
    th = angles(s["nangle"])
    xc = np.cos(np.radians(th))
    sm = specang.smyers(int(run.get("Zc", 0)), int(run.get("Ac", 0))) if run else np.zeros(7)
    ne = len(specout.ENERGIES)
    rows: dict[str, dict[int, np.ndarray]] = {}
    lev: dict[tuple, tuple] = {}
    j2e = np.zeros(ne, int)
    e_inc = np.array([float(r["e_inc_mev"]) for r in specout.ENERGIES])
    approx: list[str] = []

    def put(name, i, v):
        rows.setdefault(name, {})[i] = np.asarray(v, float)

    for i, r in enumerate(specout.ENERGIES):
        approx += [f"E={e_inc[i]:g}: {m}" for m in r.get("errors", []) if m.startswith(("specang", "angout", "tg_sink"))
                   and not ("CEANG: only Moldauer" in m and not flagcompang(e_inc[i]))]  # the target cleg is not used
        a = r.get("ang") or {}
        x = a.get("angx")
        if not x:
            continue
        e = e_inc[i]
        fc = bool(x["flagcompang"])
        j2end = int(x["j2end"])
        j2e[i] = j2end
        if x.get("note"):
            approx.append(f"E={e:g}: {x['note']}")
        lt = int(a.get("ltarget", 0))
        for t, d in sorted(x["types"].items()):
            nl = len(d["xsdisc"]) - 1
            for n in range(nl + 1):
                elastic = t == k0 and n == lt
                if not elastic:
                    if d["xsdisc"][n] == 0.0 or not (s["fileangle_all"] or n in s["fileangle"] or s.get("ddx")):
                        continue
                # compound (angdis.f90:68-87): cleg with flagcompang, else isotropic
                cl = None
                if fc:
                    if t == k0 and "comp_leg" in a and n < len(a["comp_leg"]):
                        cl = np.asarray(a["comp_leg"][n], float)
                    elif t != k0 and "comp_leg" in d and np.any(d["comp_leg"][n]):
                        cl = np.asarray(d["comp_leg"][n], float)
                    elif t == k0:
                        approx.append(f"E={e:g} {PARSYM[k0]}{PARSYM[t]}.L{n:02d}: compound isotropic (no cleg recorded)")
                    if cl is not None and not elastic:
                        cl = _clamp2(cl)
                if cl is not None:
                    compad = _series(cl, xc)
                else:
                    xs_c = float(a.get("xscompel", 0.0)) if elastic else float(d["xscompdisc"][n])
                    compad = np.full(th.size, xs_c / (4 * math.pi))
                # direct
                dl, directad = None, np.zeros(th.size)
                if elastic:
                    if k0 == 1 and "shape_leg" in ang:
                        dl = np.asarray(ang["shape_leg"][i], float)
                        directad = _series(dl, xc)
                    elif k0 > 1 and "el_direct" in ang:
                        directad = np.asarray(ang["el_direct"][i], float)
                    else:
                        approx.append(f"E={e:g} elastic: no shape-elastic angular distribution")
                elif t == k0:
                    dl = _direct_level_leg(ang, i, n, float(d["e"][n]))
                    if dl is not None:
                        directad = _series(dl, xc)
                # discrete pre-equilibrium (preeqang.f90:88-103); for the projectile's levels it is what xsdirdisc holds
                # beyond the direct-model cross section
                pe = float(d["xsdirdisc"][n]) if not elastic else 0.0
                if t == k0 and not elastic:
                    # a level without a DWBA / coupled deck got only the discrete pre-equilibrium (preeqcorrect.f90)
                    sig_dir = 4 * math.pi * float(dl[0]) if dl is not None else 0.0
                    if dl is None and pe > 0 and not ("dwba_leg" in ang or "cc_leg" in ang):
                        approx.append(f"E={e:g} {PARSYM[k0]}{PARSYM[t]}.L{n:02d}: no direct deck recorded, Kalbach shape")
                    pe = pe - sig_dir
                    pe = pe if pe > 1e-9 * max(abs(float(d["xsdirdisc"][n])), 1e-30) else 0.0
                if pe > 0:
                    akal = specang.kalbach_a(k0, t, e, np.array([d["eout_nl"]]), sm)
                    directad = directad + pe * specang.kalbach_shape(akal, th)[0]
                discad = directad + compad
                stem = f"{PARSYM[k0]}{PARSYM[t]}"
                name = f"{stem}ang.L{n:02d}"
                if elastic and k0 > 1:
                    put(name, i, np.maximum(discad, directad))
                    ruth = np.asarray(ang["el_ruth"][i], float) if "el_ruth" in ang else np.zeros(th.size)
                    with np.errstate(divide="ignore", invalid="ignore"):
                        ni = np.where(ruth > 0, discad * (1.0 - 1.0 / np.where(ruth > 0, ruth, 1.0)), 0.0)
                    put(name + ":ruth", i, ruth)
                    put(name + ":nucint", i, ni)
                else:
                    put(name, i, discad)
                put(name + ":direct", i, directad)
                put(name + ":compound", i, compad)
                if not elastic:
                    lev[(t, n)] = (float(d["e"][n]), float(d["j"][n]), int(d["p"][n]))
                if s["legendre"]:
                    nL = j2end + 1
                    dleg = np.zeros(nL)
                    cleg = np.zeros(nL)
                    if dl is not None:
                        dleg[: min(nL, dl.size)] = dl[:nL]
                    if cl is not None:
                        cleg[: min(nL, cl.size)] = cl[:nL]
                    tleg = dleg + cleg
                    if k0 == 1 and elastic:
                        el = float(a.get("xselastot", 0.0))
                        tnor = tleg / el if el else np.zeros(nL)
                    else:
                        p0 = float(d["xspopex0"][n])
                        tnor = tleg / p0 if p0 >= 1e-20 else np.zeros(nL)
                    c0 = tnor / tnor[0] if tnor[0] != 0 else np.zeros(nL)
                    ln = f"{stem}leg.L{n:02d}"
                    put(ln, i, tleg)
                    put(ln + ":direct", i, dleg)
                    put(ln + ":compound", i, cleg)
                    put(ln + ":normalized", i, tnor)
                    put(ln + ":endf6", i, c0)
    out: dict[str, np.ndarray] = {"angle": th}
    present: dict[str, np.ndarray] = {}
    for name, per in rows.items():
        w = max(v.size for v in per.values())
        arr = np.zeros((ne, w))
        for i, v in per.items():
            arr[i, : v.size] = v
        out[name] = arr
        if ":" not in name:
            present[name] = np.array([i in per for i in range(ne)])
    META.update(Z=int(run.get("Z", 0)), A=int(run.get("A", 0)), k0=k0, e_inc_mev=e_inc, j2end=j2e, levels=lev,
                present=present, block=bool(s["block"]), approx=approx)
    return out


def add_to_results(res, injection):
    """End of engine.run / engine_c.run: Results.angular from the recorded run (and the TALYS files with
    INCOGNITA_ANGOUT_DIR); the recorders the switch turned on are cleared. Unchanged when the switch is off.

    TALYS: angleout.f90:1 (angleout)
    Test: tests/hf/test_angout.py
    """
    if _SET is None:
        return res
    from dataclasses import replace

    import torch

    from physics.hf import specout

    from physics.hf import specobs

    s = _SET
    try:
        arr = build()
        specobs.take_discad(arr, s["nangle"])  # KWCOV B4: discrete-peak angular distributions for the DDX
        from physics.hf import recoil

        recoil.take_discad(arr, s["nangle"])  # KWCOV B12: angdisrecoil.f90
        if s.get("ddx") and not s["fileangle_all"]:  # the DDX made build visit every level: keep angleout's selection
            arr = {k: v for k, v in arr.items() if _selected(k, s)}
            META["present"] = {k: v for k, v in META.get("present", {}).items() if _selected(k, s)}
            META["levels"] = {k: v for k, v in META.get("levels", {}).items() if k[1] in s["fileangle"]}
        if not s.get("internal"):
            out_dir = os.environ.get(ENV_DIR, "").strip()
            if out_dir and arr:
                write_files(arr, META, out_dir)
            ang = {k: torch.as_tensor(v, dtype=torch.float64) for k, v in arr.items()}
            res = replace(res, angular=ang)
    finally:
        from physics.hf import recoil

        if not specout.env_enabled() and not specobs.active() and not recoil.active():  # KWCOV B4/B12: cleared later
            specout.clear_run()
        end_run()
    return res


def _selected(name: str, s: dict) -> bool:
    """KWCOV B4: is an angle/Legendre array one angleout.f90 writes (elastic, or a level in `fileangle`)?"""
    if ".L" not in name or name[2:5] not in ("ang", "leg"):
        return True
    n = int(name.split(".L")[1][:2])
    k0 = int(s["k0"])
    return (name[0] == PARSYM[k0] and name[1] == PARSYM[k0] and n == 0) or n in s["fileangle"]  # Ltarget = 0


# ------------------------------------------------------------------------------------------------ TALYS files
def _w_char(f, ind, key, val=""):
    f.write("# " + " " * ind + f"{key}: {val}\n")


def _w_real(f, ind, key, x):
    f.write("# " + " " * ind + f"{key}: {float(np.float32(x)):13.6E}\n")


def _datablock(f, ind, cols, units, n):
    _w_char(f, ind, "datablock")
    _w_char(f, ind + 2, "columns", len(cols))
    _w_char(f, ind + 2, "entries", n)
    for names, bracket in ((cols, False), (units, True)):
        line = "##"
        for c in names:
            w = [" "] * 15
            L = len(c.strip())
            b0 = max(15 // 2 - L // 2, 0)
            w[b0: b0 + L] = c.strip()
            if bracket:
                w[b0 - 1] = "["
                w[b0 + L] = "]"
            line += "".join(w)
        f.write(line.rstrip() + "\n")


def _fname(stem: str, kind: str, n: int, e: float, block: bool) -> str:
    if block:
        return f"{stem}{kind}.L{n:02d}"
    e32 = float(np.float32(e))
    return f"{stem}{int(e32):04d}{f'{e32:8.3f}'[4:]}{kind}.L{n:02d}"


def write_files(arr: dict, meta: dict, out_dir) -> list[str]:
    """TALYS's angle (and Legendre) files of the run in `out_dir`, YANDF-0.4 as angleout.f90 writes them.

    TALYS: angleout.f90:1 (angleout), write_block.f90:1
    Test: tests/hf/test_angout.py
    """
    from physics.hf.core.constants import nuclide_symbol

    d = Path(out_dir)
    d.mkdir(parents=True, exist_ok=True)
    Z, A, k0, block = meta["Z"], meta["A"], meta["k0"], meta["block"]
    nuc = f"{nuclide_symbol(Z)}{A}"
    th = arr["angle"]
    today = datetime.date.today().isoformat()
    opened: set[str] = set()
    written = []
    for name in sorted(k for k in meta["present"]):
        stem, rest = name[:2], name[2:]
        kind, n = rest[:3], int(rest.split(".L")[1])
        t = PARSYM.index(stem[1])
        elastic = t == k0 and (t, n) not in meta["levels"]
        for i, e in enumerate(meta["e_inc_mev"]):
            if not meta["present"][name][i]:
                continue
            fn = _fname(stem, kind, n, e, block)
            mode = "a" if (block and fn in opened) else "w"
            opened.add(fn)
            if elastic:
                reaction, mt = f"({PARSYM[k0]},el)", 2
            else:
                reaction, mt = f"({PARSYM[k0]},{PARSYM[t]}_{n})", MT0[t] + n
            quantity = "angular distribution" if kind == "ang" else "Legendre coefficients"
            with open(d / fn, mode) as f:
                _w_char(f, 0, "header")
                _w_char(f, 2, "title", f"{nuc}{reaction} {quantity} at {float(np.float32(e)):12.6E} MeV")
                _w_char(f, 2, "source", "INCOGNITA (TALYS-2.x port)")
                _w_char(f, 2, "user", "Unknown User")
                _w_char(f, 2, "date", today)
                _w_char(f, 2, "format", "YANDF-0.4")
                _w_char(f, 0, "target")
                _w_char(f, 2, "Z", Z)
                _w_char(f, 2, "A", A)
                _w_char(f, 2, "nuclide", nuc)
                _w_char(f, 0, "reaction")
                _w_char(f, 2, "type", reaction)
                _w_char(f, 2, "ENDF_MF", 4)
                _w_char(f, 2, "ENDF_MT", mt)
                _w_real(f, 2, "E-incident [MeV]", e)
                if not elastic:
                    le, lj, lp = meta["levels"][(t, n)]
                    _w_char(f, 2, "level")
                    _w_char(f, 4, "number", n)
                    _w_real(f, 4, "energy [MeV]", le)
                    if lj >= 0:
                        _w_real(f, 4, "spin", lj)
                        _w_char(f, 4, "parity", lp)
                _w_char(f, 2, "quantity")
                _w_char(f, 4, "type", quantity)
                if kind == "ang":
                    cols = ["Angle", "xs", "Direct", "Compound"]
                    un = ["deg", "mb/sr", "mb/sr", "mb/sr"]
                    data = [th, arr[name][i], arr[name + ":direct"][i], arr[name + ":compound"][i]]
                    if elastic and k0 > 1:
                        cols += ["xs/Rutherford", "Nuc+interfer."]
                        un += ["", ""]
                        data += [arr[name + ":ruth"][i], arr[name + ":nucint"][i]]
                    _datablock(f, 2, cols, un, th.size)
                    for row in zip(*data):  # noqa: B905
                        f.write("".join(f"{float(np.float32(v)):15.6E}" for v in row) + "\n")
                else:
                    nL = int(meta["j2end"][i]) + 1
                    _datablock(f, 2, ["L", "Total", "Direct", "Compound", "Normalized", "ENDF-6"], [""] * 6, nL)
                    cols = [arr[name + s][i] for s in ("", ":direct", ":compound", ":normalized", ":endf6")]
                    for L in range(nL):
                        f.write(f"{L:6d}" + " " * 9 + "".join(f"{float(np.float32(c[L] if L < c.size else 0.0)):15.6E}"
                                                            for c in cols) + "\n")
            written.append(fn)
    return sorted(set(written))


__all__ = ["ENV", "ENV_DIR", "META", "active", "add_to_results", "angles", "begin_run", "build", "charged_elastic",
           "flagcompang", "nlev_target", "record", "settings", "wanted", "write_files"]
