"""SPECOUT angular distributions and DDX (OUTPUT ONLY; switch INCOGNITA_SPECOUT, see physics/hf/specout.py).

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Every angular distribution is stored as Legendre coefficients c_L in TALYS's convention
    dsigma/dOmega(theta) = sum_L (2L+1) c_L P_L(cos theta)   [mb/sr, centre of mass],   sigma = 4 pi c_0.

* Shape elastic: from the incident S-matrix, |A|^2 + |B|^2 for a spin-1/2 projectile (spherical targets: the engine's own
  OMP re-solved on `omp.schrodinger.solve_radial`, the reference twin of the solve the engine ran; coupled targets: the
  coupled-channels S-matrix, `ecis.angular.coupled_angular` (ELDA), which also gives the direct DA of every coupled level).
  Checked against the engine's sigma_shape_el / sigma_direct (so_*_chk arrays).
* Compound elastic and compound inelastic to the target's discrete levels 0..NLEV: TALYS comptarget.f90 cleg from the exact
  per-(J, pi) Hauser-Feshbach pair weights with Moldauer WFC (`compound.ceang`, CEANG), normalised to the engine's own level
  population (the ratio is kept as a diagnostic: it is 1 unless an engine option changed the compound weights).
* Direct DWBA levels (not coupled): `ecis.dwba_angular` coherent DWBA amplitude normalised to the engine's xsdirdisc.
* Continuum DDX: TALYS's Kalbach systematics (kalbach.f90 + kalbachsep.f90): compound part isotropic, pre-equilibrium and
  multiple pre-equilibrium parts x K(a, theta) = a / (4 pi sinh a) exp(a cos theta); the slope a(type, Einc, Eout) is
  stored, so DDX at any angle (or its Legendre series, c_L = (a / sinh a) i_L(a) / (4 pi) per mb/MeV) is exact.

Test: tests/hf/test_specout.py
"""

from __future__ import annotations

import math
import os

import numpy as np

NLEV = 10  # compound Legendre for the target's levels 0..NLEV (CEANG's NLEV_MAX)
LCOMP = 24  # compound Legendre order kept (TALYS cleg runs to 2 min(l, l', J); terms above ~20 are ~0)


def _np(x):
    if hasattr(x, "detach"):
        x = x.detach().cpu().numpy()
    return np.asarray(x, float)


# --------------------------------------------------------------------------------------------- C comptarget sink
import ctypes as _ct

_TG_T = _ct.CFUNCTYPE(None, _ct.POINTER(_ct.c_int64), _ct.POINTER(_ct.c_double), _ct.POINTER(_ct.c_uint64))


def _arr(addr, n, dt=_ct.c_double):
    if not addr or n <= 0:
        return np.zeros(max(n, 0), dtype=np.int64 if dt is _ct.c_int64 else float)
    return np.ctypeslib.as_array(_ct.cast(addr, _ct.POINTER(dt)), shape=(n,)).copy()


def _tg_sink(iv, dv, pv):
    from physics.hf import specout

    cur = specout._CUR
    if cur is None:
        return
    try:
        na, nb, nn = int(iv[3]), int(iv[4]), int(iv[5])
        wfc = bool(iv[2])
        I = _ct.c_int64
        cell = dict(J2=int(iv[0]), parity=int(iv[1]), wfc=wfc, elastic=bool(iv[6]), lt=int(iv[7]), pref=float(dv[0]),
                    st=float(dv[1]), l_in=_arr(pv[0], na, I), j2_in=_arr(pv[1], na, I), tinc=_arr(pv[2], na),
                    fa=_arr(pv[3], na) if wfc else None, ea=_arr(pv[4], na) if (wfc and pv[4]) else None,
                    prod=_arr(pv[5], nn) if wfc else None, x=_arr(pv[6], nn) if wfc else None,
                    n=_arr(pv[7], nb, I), l=_arr(pv[8], nb, I), j2=_arr(pv[9], nb, I), T=_arr(pv[10], nb),
                    c=_arr(pv[11], nb), rho=_arr(pv[12], nb))
        cur.setdefault("tcells", []).append(cell)
    except Exception as exc:  # noqa: BLE001 -- output only
        cur.setdefault("errors", []).append(f"tg_sink {type(exc).__name__}: {exc}")


_TG = _TG_T(_tg_sink)


def sync_target(on: bool) -> None:
    """(Un)register the comptarget sink on libnativex (called per recorded energy by specout)."""
    try:
        from physics.hf.native import nativex

        so = nativex.lib()
    except Exception:  # noqa: BLE001
        return
    if so is None or not hasattr(so, "nx_set_targetsink"):
        return
    so.nx_set_targetsink.argtypes = [_ct.c_void_p, _ct.c_int64]
    so.nx_set_targetsink.restype = None
    so.nx_set_targetsink(_ct.cast(_TG, _ct.c_void_p) if on else None, NLEV)


def blocks_from_cells(cells: list[dict], nlev: int) -> dict:
    """CEANG's pair_blocks layout rebuilt from nx_target's cells: M_n[a, b] = pref tinc_a T_b W_ab rho_n
    (W_ab = sum_m prod_m / ((1 + x_m fa_a)(1 + x_m c_b)) with Moldauer, 1 without), plus the elastic enhancement
    pref T_b tinc_a ea_a rho_lt on the diagonal channel of level Ltarget (nx_target's `elas`)."""
    out, sums = [], {n: 0.0 for n in range(nlev + 1)}
    for c in cells:
        blk = {"J2": c["J2"], "parity": c["parity"], "l_in": c["l_in"].tolist(), "j2_in": c["j2_in"].tolist(),
               "t_in": c["tinc"], "levels": {}}
        if c["wfc"]:
            da = 1.0 + c["x"][:, None] * c["fa"][None, :]  # (M, A)
        for n in sorted(set(c["n"].tolist())):
            if n > nlev:
                continue
            m = c["n"] == n
            T, cb, rho = c["T"][m], c["c"][m], c["rho"][m]
            if c["wfc"]:
                db = 1.0 + c["x"][:, None] * cb[None, :]
                W = np.einsum("m,ma,mb->ab", c["prod"], 1.0 / da, 1.0 / db)
            else:
                W = np.ones((len(c["tinc"]), int(m.sum())))
            M = c["pref"] * c["tinc"][:, None] * (T * rho)[None, :] * W
            if c["wfc"] and c["elastic"] and n == c["lt"] and c["ea"] is not None:
                lb, jb = c["l"][m], c["j2"][m]
                for a in range(len(c["tinc"])):
                    hit = np.flatnonzero((lb == c["l_in"][a]) & (jb == c["j2_in"][a]))
                    for bq in hit[:1]:
                        M[a, bq] += c["pref"] * T[bq] * c["tinc"][a] * c["ea"][a] * rho[bq]
            blk["levels"][n] = {"l_out": c["l"][m].tolist(), "j2_out": c["j2"][m].tolist(), "M": M}
            sums[n] += float(M.sum())
        out.append(blk)
    return {"blocks": out, "sums": sums, "nmax": nlev}


_SIDE: dict = {}


def _sides(J2: int, ls: tuple, j2s: tuple, two_i: int, lmax: int) -> np.ndarray:
    """ceang._side for every channel and every even L <= lmax: (L+1, n) (odd L rows 0), cached."""
    key = (J2, ls, j2s, two_i, lmax)
    got = _SIDE.get(key)
    if got is None:
        from physics.hf.compound.ceang import _side

        got = np.zeros((lmax + 1, len(ls)))
        for L in range(0, lmax + 1, 2):
            got[L] = [_side(J2, l, j2, two_i, L) for l, j2 in zip(ls, j2s)]  # noqa: B905
        if len(_SIDE) > 20000:  # angular momenta only: kept across targets, bounded
            _SIDE.clear()
        _SIDE[key] = got
    return got


def legendre_fast(rec: dict, n: int, two_i0: int, two_in: int, lmax_out: int) -> np.ndarray:
    """ceang.legendre(rec, n, two_i0, two_in, lmax_out) (key "M"), vectorised over L with the side vectors cached:
    cleg(L) = sum_blocks phase (J2+1)/(4 pi) a_in(L) . M . a_out(L) / (2L+1)."""
    out = np.zeros(lmax_out + 1)
    phase = -1.0 if (abs(two_in - two_i0) // 2) % 2 else 1.0
    L = np.arange(lmax_out + 1)
    for blk in rec["blocks"]:
        lv = blk["levels"].get(n)
        if lv is None:
            continue
        J2 = blk["J2"]
        ai = _sides(J2, tuple(blk["l_in"]), tuple(blk["j2_in"]), two_i0, lmax_out)
        ao = _sides(J2, tuple(lv["l_out"]), tuple(lv["j2_out"]), two_in, lmax_out)
        out += phase * (J2 + 1) / (4 * np.pi) * np.einsum("La,ab,Lb->L", ai, lv["M"], ao) / (2 * L + 1)
    return out


# --------------------------------------------------------------------------------------------- per incident energy
def record_energy(cas, st, binp, cinp, etot, a_e, fkw, ci, pop, b2, b) -> None:
    """Compound Legendre of the target's discrete levels + the engine's elastic/level numbers, for the energy being built."""
    from physics.hf import specout

    cur = specout._CUR
    if cur is None:
        return
    rec = {"k0": int(binp.k0), "ltarget": int(binp.ltarget), "targetspin2": int(binp.targetspin2)}
    try:
        k0 = rec["k0"]
        rec["xselastot"] = float(_np(b.xselastot_mb))
        rec["xscompel"] = float(_np(b.xscompel_mb))
        rec["xsreac"] = float(b2.xsreacinc_mb)
        disc = _np(b.xsdisc_mb[k0]) if k0 in b.xsdisc_mb else np.zeros(0)
        dd = _np(b2.xsdirdisc_mb[k0]) if k0 in b2.xsdirdisc_mb else np.zeros(0)
        rec["xsdisc"] = disc  # binary level cross sections (compound + direct), engine's
        rec["xsdirdisc"] = dd
        g = binp.grids[k0]
        rec["level_e"] = _np(g.ex_mev)[: len(disc)]
        p = pop.pop_mb[0]
        nl = min(NLEV, len(disc) - 1)
        rec["comp_pop"] = np.array([float(p[k0, n].sum()) for n in range(nl + 1)]) if nl >= 0 else np.zeros(0)
        rec["comp_pop"][rec["ltarget"]] = float(_np(pop.xs_comp_el_mb[0])) if nl >= rec["ltarget"] else 0.0
        from physics.hf.compound import ceang
        from physics.hf.compound.chain import compound_inputs

        import torch

        cells = cur.pop("tcells", None)
        if cells:  # the C front's own cells (nx_target sink)
            got = blocks_from_cells(cells, nl)
            jd = _np(g.jdis)[: nl + 1] if hasattr(g, "jdis") else None
            two = [int(2.0 * np.float32(v)) for v in jd] if jd is not None else None
            rec["ceang_route"] = "c"
        else:
            got = None
        if got is None or two is None:
            if ci is None or not hasattr(ci, "residuals"):
                ci = compound_inputs(cas, st, binp, cinp, etot, a_e, **fkw)
            if got is None:
                with torch.inference_mode():
                    got = ceang.pair_blocks(ci, nlev=nl)
                rec["ceang_route"] = "py"
            r0 = ci.residuals[k0]
            two = [int(r0.jdis2[n]) for n in range(got["nmax"] + 1)]
        leg = np.zeros((nl + 1, LCOMP + 1))
        ratio = np.full(nl + 1, np.nan)
        for n in range(min(nl, got["nmax"]) + 1):
            c = (ceang.legendre(got, n, rec["targetspin2"], two[n], LCOMP) if os.environ.get("SPECOUT_LEG_REF", "0") == "1"
                 else legendre_fast(got, n, rec["targetspin2"], two[n], LCOMP))
            s = float(got["sums"].get(n, 0.0))
            eng = float(rec["comp_pop"][n])
            if c[0] > 0 and eng > 0:
                ratio[n] = 4 * math.pi * c[0] / eng
                c = c * eng / (4 * math.pi * c[0])
            elif eng > 0:  # no pair recorded: isotropic
                c = np.zeros(LCOMP + 1)
                c[0] = eng / (4 * math.pi)
            leg[n] = c
            del s
        rec["comp_leg"] = leg
        rec["comp_ratio"] = ratio
        rec["level_two_spin"] = np.array(two[: nl + 1])
    except Exception as exc:  # noqa: BLE001 -- output only
        rec["error"] = f"{type(exc).__name__}: {exc}"
        cur.setdefault("errors", []).append(f"specang.record_energy {rec['error']}")
    cur["ang"] = rec


# --------------------------------------------------------------------------------------------- DWBA decks
_DWBA: dict = {}  # (Z, A, round(e, 6)) -> (omp, case, parts, refine, xs_by_level); filled only with the switch on


def record_dwba(Z, A, e_inc_mev, omp, case, parts, refine, xs_by_level) -> None:
    """direct/chain.computed_cross_sections' DWBA deck of one energy (references only; nothing is changed)."""
    from physics.hf import specout

    if not specout.enabled():
        return
    _DWBA[(int(Z), int(A), round(float(e_inc_mev), 6))] = (omp, case, parts, refine, xs_by_level)


_GEOM: dict = {}


def _dwba_geom(lam: int, parity: int, l: np.ndarray, j: np.ndarray, njmax: int):
    """Energy-independent part of dwba_angular.angular_distribution's amplitude for one multipole: the sparse map
    from the radial integrals I[cp, c] (flattened pair index) to the coefficients of Y_{l'}^{m''} in each final
    amplitude (s, s', M). Returns (keys (K, 5) = s2, sp2, M, lp, mpp; pairs (P, 2) = cp, c; coef (K, P) sparse)."""
    key = (lam, parity, tuple(l.tolist()), tuple(np.round(2 * j).astype(int).tolist()), njmax)
    got = _GEOM.get(key)
    if got is not None:
        return got
    import scipy.sparse as sp_

    from physics.hf.ecis.dwba_angular import cg, gaunt_conj

    nlj = len(l)
    ent = [c for c in range(nlj) if j[c] <= njmax + 0.5 + 1e-9]
    halves = (-0.5, 0.5)
    kidx, pidx, rows, cols, vals = {}, {}, [], [], []
    for c in ent:
        lc, jc = int(l[c]), float(j[c])
        y0 = math.sqrt((2 * lc + 1) / (4 * math.pi))
        for cp in range(nlj):
            lp, jp = int(l[cp]), float(j[cp])
            if (lc + lp + lam) % 2 or ((-1) ** lam != parity):
                continue
            if abs(lc - lp) > lam or lc + lp < lam:
                continue
            ph = (1j) ** (lc - lp)
            for s in halves:
                a1 = cg(lc, 0, 0.5, s, jc, s)
                if a1 == 0:
                    continue
                for s1 in halves:
                    m = round(s - s1)
                    a2 = cg(lc, m, 0.5, s1, jc, s)
                    if a2 == 0:
                        continue
                    for M in range(-lam, lam + 1):
                        mp = m - M
                        g = gaunt_conj(lp, mp, lam, M, lc, m)
                        if g == 0:
                            continue
                        mup = mp + s1
                        a3 = cg(lp, mp, 0.5, s1, jp, mup)
                        if a3 == 0:
                            continue
                        for spn in halves:
                            mpp = round(mup - spn)
                            if abs(mpp) > lp:
                                continue
                            a4 = cg(lp, mpp, 0.5, spn, jp, mup)
                            if a4 == 0:
                                continue
                            kk = kidx.setdefault((int(2 * s), int(2 * spn), M, lp, mpp), len(kidx))
                            pp = pidx.setdefault((cp, c), len(pidx))
                            rows.append(kk); cols.append(pp); vals.append(ph * y0 * a1 * a2 * g * a3 * a4)
    keys = np.array(sorted(kidx, key=kidx.get), dtype=np.int64).reshape(-1, 5)
    pairs = np.array(sorted(pidx, key=pidx.get), dtype=np.int64).reshape(-1, 2)
    coef = sp_.csr_matrix((np.asarray(vals, complex), (rows, cols)), shape=(len(kidx), len(pidx)))
    _GEOM[key] = (keys, pairs, coef)
    return _GEOM[key]


def dwba_da_fast(ri: dict, b: int, lam: int, parity: int, theta_deg: np.ndarray) -> np.ndarray:
    """dwba_angular.angular_distribution's dsigma/dOmega (same normalisation, same terms) with the geometry cached:
    the coherent amplitude per final (s, s', M) is sum_k [coef @ I]_k Y_{l'_k}^{m''_k}(theta)."""
    from physics.hf.ecis.dwba_angular import sph_harm

    keys, pairs, coef = _dwba_geom(lam, parity, ri["l"], ri["j"], int(ri["njmax"]))
    th = np.radians(np.asarray(theta_deg, float))
    if keys.shape[0] == 0:
        return np.zeros(th.size)
    Iv = ri["I"][b][pairs[:, 0], pairs[:, 1]]
    amp = coef @ Iv  # (K,)
    ylm = {}
    Y = np.empty((keys.shape[0], th.size), complex)
    for q, (_, _, _, lp, mpp) in enumerate(keys.tolist()):
        y = ylm.get((lp, mpp))
        if y is None:
            y = ylm[(lp, mpp)] = sph_harm(lp, mpp, th)
        Y[q] = y
    grp = {}
    gi = np.array([grp.setdefault((s2, sp2, M), len(grp)) for s2, sp2, M, _, _ in keys.tolist()])
    A = np.zeros((len(grp), th.size), complex)
    np.add.at(A, gi, amp[:, None] * Y)
    return (np.abs(A) ** 2).sum(axis=0) / 2.0


_SIGW: dict = {}


def dwba_sigma(ri: dict, b: int, lam: int, vibbeta_b: float) -> float:
    """angular_distribution's incoherent (port) sigma of level b, its pair weights cached per (lam, l/j table)."""
    from physics.hf.ecis import dwba as _D
    from physics.hf.ecis.dwba_angular import MB_PER_FM2, cg

    l, j, njmax = ri["l"], ri["j"], int(ri["njmax"])
    key = (lam, tuple(l.tolist()), tuple(np.round(2 * j).astype(int).tolist()), njmax)
    W = _SIGW.get(key)
    if W is None:
        nlj = len(l)
        W = np.zeros((nlj, nlj))  # [cp, c]
        for c in range(nlj):
            if j[c] > njmax + 0.5 + 1e-9:
                continue
            for cp in range(nlj):
                if (int(l[c]) + int(l[cp]) + lam) % 2:
                    continue
                W[cp, c] = (2 * j[c] + 1) / 2.0 * cg(j[c], -0.5, lam, 0, j[cp], -0.5) ** 2
        _SIGW[key] = W
    k = ri["k"]
    d = vibbeta_b / _D.SQRT4PI
    fac = math.pi / float(k[0]) ** 2 * MB_PER_FM2
    pre = (ri["mu"] * d) ** 2 / (4.0 * float(k[b + 1]) * float(k[0]))
    return float((W * np.abs(ri["I"][b]) ** 2).sum()) * fac * pre


def dwba_levels(Z: int, A: int, energies: list[float], nlev: int) -> dict:
    """Direct DWBA level DA per energy as Legendre coefficients (E, nlev+1, L+1), each normalised to the engine's own
    DWBA cross section of that level; so_dwba_chk = (engine sigma, the deck's own sigma / engine sigma)."""
    from physics.hf.ecis import dwba_angular as DA

    out_leg, chk, lmax_all = {}, {}, 0
    for i, e in enumerate(energies):
        rec = _DWBA.get((Z, A, round(float(e), 6)))
        if rec is None:
            continue
        omp, case, parts, refine, xs = rec
        lev = case.level_index.tolist()
        if not lev:
            continue
        ri = DA.radial_integrals(omp, Z, A, float(case.e_inc_mev), case.e_mev, case.spin, case.parity, case.vibbeta,
                                 case.deformation_length, refine=refine, parts=parts)
        lout = 2 * int(ri["njmax"]) + 2 * int(max(case.spin.tolist())) + 4
        x, w = _gauss(lout + 4)
        th = np.degrees(np.arccos(x))
        for b, n in enumerate(lev):
            if n > nlev:
                continue
            sig_e = float(xs[b])
            if sig_e <= 0:
                continue
            if os.environ.get("SPECOUT_DWBA_REF", "0") == "1":
                raw, sig = DA.angular_distribution(ri, b, int(case.spin[b]), int(case.parity[b]), float(case.vibbeta[b]), th)
            else:
                raw = dwba_da_fast(ri, b, int(case.spin[b]), int(case.parity[b]), th)
                sig = dwba_sigma(ri, b, int(case.spin[b]), float(case.vibbeta[b]))
            c = _project(np.asarray(raw, float), x, w, lout)
            ratio = float(sig) / sig_e  # the coherent deck's own incoherent sigma vs the engine's (1 = same deck)
            if c[0] > 0:
                c = c * sig_e / (4 * math.pi * c[0])
            out_leg[(i, n)] = c
            chk[(i, n)] = (sig_e, ratio)
            lmax_all = max(lmax_all, c.size - 1)
    if not out_leg:
        return {}
    leg = np.zeros((len(energies), nlev + 1, lmax_all + 1))
    ck = np.full((len(energies), nlev + 1, 2), np.nan)
    for (i, n), c in out_leg.items():
        leg[i, n, : c.size] = c
        ck[i, n] = chk[(i, n)]
    return {"dwba_leg": leg, "dwba_chk": ck}


# --------------------------------------------------------------------------------------------- run level
def _gauss(n: int):
    x, w = np.polynomial.legendre.leggauss(n)
    return x, w


def _project(f: np.ndarray, x: np.ndarray, w: np.ndarray, lmax: int) -> np.ndarray:
    """c_L with f(x) = sum (2L+1) c_L P_L(x): c_L = 1/2 int f P_L dx (exact for polynomial f of degree < 2 n)."""
    from numpy.polynomial.legendre import legvander

    V = legvander(x, lmax)  # (n, L+1)
    return 0.5 * (f * w) @ V if f.ndim == 1 else 0.5 * (f * w[None, :]) @ V


def shape_elastic_spherical(cas, energies: list[float]) -> dict:
    """Shape-elastic Legendre per energy for a spherical (colltype S) target from the engine's own OMP: (E, L+1) + the
    integral vs the solve's sigma_shape_el (check)."""
    import torch

    from physics.hf.core.tensors import DTYPE
    from physics.hf.omp.inverse import _ported_omp
    from physics.hf.omp.schrodinger import (PARMASS_AMU, PARSPIN, PARZ, cross_sections, nucleus_mass_amu,
                                            solve_radial)
    from physics.hf.omp.incident import talys_constants

    Z, A, k0 = int(cas.Zt), int(cas.At), int(cas.k0)
    if k0 != 1:
        return {}
    m_t = nucleus_mass_amu(Z, A)
    numl = int(talys_constants()["numl"])
    groups: dict[int, list[int]] = {}
    for i, e in enumerate(energies):
        nj = min(max(20, int(2.4 * 1.25 * A ** (1.0 / 3.0) * 0.22 * math.sqrt(PARMASS_AMU[k0] * e))), numl)
        groups.setdefault(nj, []).append(i)
    lout = 2 * max(groups) + 2
    leg = np.zeros((len(energies), lout + 1))
    chk = np.zeros((len(energies), 2))
    x, w = _gauss(lout + 4)
    from scipy.special import lpmv

    for nj, idx in groups.items():
        e = torch.tensor([energies[i] for i in idx], dtype=DTYPE)
        p = _ported_omp(Z, A, Z, A, k0, e, cas.options, cas.params)
        sol = solve_radial(p, e, PARMASS_AMU[k0], m_t, float(Z * PARZ[k0]), PARSPIN[k0], nj)
        S = sol.smat.numpy()  # (E, L, J)
        jv = sol.jvalues.numpy()
        valid = sol.valid.numpy()
        k = sol.kin.k_fm.numpy().reshape(len(idx), -1)[:, 0]
        xs = cross_sections(sol, PARSPIN[k0])["sigma_shape_el_mb"].numpy()
        L = S.shape[1]
        P0 = np.array([lpmv(0, l, x) for l in range(L)])  # (L, n)
        P1 = np.array([lpmv(1, l, x) for l in range(L)])
        for q, i in enumerate(idx):
            sp = np.zeros(L, complex); sm = np.zeros(L, complex)
            for l in range(L):  # noqa: E741
                for jj in range(S.shape[2]):
                    if not valid[l, jj]:
                        continue
                    if abs(jv[l, jj] - (l + 0.5)) < 1e-6:
                        sp[l] = S[q, l, jj]
                    elif abs(jv[l, jj] - (l - 0.5)) < 1e-6:
                        sm[l] = S[q, l, jj]
            ll = np.arange(L)
            sm[0] = 1.0  # no j = -1/2
            a = ((ll + 1) * (sp - 1.0) + ll * (sm - 1.0)) @ P0 / (2j * k[q])
            bb = (sp - sm) @ P1 / (2j * k[q])
            f = (np.abs(a) ** 2 + np.abs(bb) ** 2) * 10.0  # fm^2/sr -> mb/sr
            leg[i] = _project(f, x, w, lout)
            chk[i] = (4 * math.pi * leg[i, 0], float(xs[q]))
    return {"shape_leg": leg, "shape_chk": chk}


def coupled(cas, energies: list[float]) -> dict:
    """Coupled targets: shape elastic + direct DA of every coupled level per energy (ELDA's coupled_angular, one energy at a
    time as the engine solves it), as Legendre coefficients; plus the integral checks."""
    import torch

    from physics.hf.core.tensors import DTYPE
    from physics.hf.ecis import angular
    from physics.hf.ecis.incident import _t4_parameters, njmax_incident
    from physics.hf.omp.schrodinger import PARMASS_AMU

    band = cas._coupled_band()
    if band is None or int(cas.k0) != 1:
        return {}
    nlev = int(band["spin"].numel())
    shp, drc, chk = None, None, []
    njs = [njmax_incident(int(cas.At), PARMASS_AMU[1], float(v)) for v in energies]
    lout = 2 * max(njs) + 4  # one angle grid for the run, so the per-block geometry is reused across energies
    x, w = _gauss(lout + 4)
    th = np.degrees(np.arccos(x))
    for i, e0 in enumerate(energies):
        e = torch.tensor([e0], dtype=DTYPE)
        nj = njs[i]
        omp = _t4_parameters(int(cas.Zt), int(cas.At), 1, e, cas.options)
        rec = dict(omp=omp, Z=int(cas.Zt), A=int(cas.At), e=e, band=band, options=cas.options, particle=1, lmax=nj, refine=1)
        r = angular.coupled_angular(rec, th)
        if shp is None:
            shp = np.zeros((len(energies), 2 * max(njmax_incident(int(cas.At), PARMASS_AMU[1], float(v)) for v in energies) + 5))
            drc = np.zeros((len(energies), nlev, shp.shape[1]))
        c = _project(r["el_shape"][0], x, w, lout)
        shp[i, : c.size] = c
        for q, bidx in enumerate(r["levels_out"].tolist()):
            if bidx == 0:
                continue
            c = _project(r["direct"][0, q], x, w, lout)
            drc[i, bidx, : c.size] = c
        chk.append([4 * math.pi * shp[i, 0], float(r["sigma_shape_el"][0])]
                   + [4 * math.pi * drc[i, b, 0] for b in range(1, nlev)] + [float(v) for v in r["sigma_direct"][0, 1:]])
    return {"shape_leg": shp, "cc_leg": drc, "cc_level_e": band["e_mev"].numpy().copy(), "cc_chk": np.asarray(chk),
            "cc_nlev": np.array(nlev)}


# --------------------------------------------------------------------------------------------- Kalbach
def smyers(Zc: int, Ac: int) -> np.ndarray:
    """kalbachsep.f90: Myers-Swiatecki separation energies of types 1..6 from the compound (Zinit, Ainit); index 0 unused."""
    pz = (0, 0, 1, 1, 1, 2, 2)
    pa = (0, 1, 1, 2, 3, 3, 4)
    ib = (0.0, 0.0, 0.0, 2.225, 8.482, 7.718, 28.296)
    out = np.zeros(7)
    tt, ot = 2.0 / 3.0, 1.0 / 3.0
    for t in range(1, 7):
        ac, zc = float(Ac), float(Zc)
        ab, zb = float(Ac - pa[t]), float(Zc - pz[t])
        nc, nb = ac - zc, ab - zb
        out[t] = (15.68 * (ac - ab) - 28.07 * ((nc - zc) ** 2 / ac - (nb - zb) ** 2 / ab)
                  - 18.56 * (ac ** tt - ab ** tt) + 33.22 * ((nc - zc) ** 2 / ac ** (2 * tt) - (nb - zb) ** 2 / ab ** (2 * tt))
                  - 0.717 * (zc ** 2 / ac ** ot - zb ** 2 / ab ** ot) + 1.211 * (zc ** 2 / ac - zb ** 2 / ab) - ib[t])
    return out


def kalbach_a(k0: int, t: int, ein: float, eout: np.ndarray, sm: np.ndarray) -> np.ndarray:
    """kalbach.f90's slope a (0 for photons: isotropic)."""
    if t == 0 or k0 == 0:
        return np.zeros_like(eout)
    cmin = (1.0, 1.0, 1.0, 1.0, 1.0, 0.0)
    cmout = (0.5, 1.0, 1.0, 1.0, 1.0, 2.0)
    ea = ein + sm[k0]
    ek1, ek3 = min(ea, 130.0), min(ea, 41.0)
    eb = eout + sm[t]
    x1, x3 = ek1 * eb / ea, ek3 * eb / ea
    return 0.04 * x1 + 1.8e-6 * x1 ** 3 + 6.7e-7 * cmin[k0 - 1] * cmout[t - 1] * x3 ** 4


def kalbach_shape(a: np.ndarray, theta_deg) -> np.ndarray:
    """K(a, theta) = a / (4 pi sinh a) exp(a cos theta) (1/(4 pi) at a = 0; 0 where |a| > 80, as kalbach.f90)."""
    a = np.asarray(a, float)[..., None]
    c = np.cos(np.radians(np.asarray(theta_deg, float)))
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        k = np.where(np.abs(a) < 1e-12, 1.0, a / np.sinh(np.where(np.abs(a) < 1e-12, 1.0, a))) * np.exp(a * c) / (4 * math.pi)
    return np.where(np.abs(a) <= 80.0, k, 0.0)


def ddx(so: dict, x: str, i: int, theta_deg) -> np.ndarray:
    """Continuum DDX (mb/MeV/sr, (E, T)) of ejectile x at incident-energy index i of a specout pack, TALYS's ddxmode-2
    arrangement: compound/(4 pi) + (pe + mpe) K(a, theta) + gr/(4 pi). Discrete lines are not included."""
    a = so[f"so_{x}_kal_a"][i]
    k = kalbach_shape(a, theta_deg)
    iso = (so[f"so_{x}_comp"][i] + so[f"so_{x}_gr"][i])[:, None] / (4 * math.pi)
    return iso + (so[f"so_{x}_pe"][i] + so[f"so_{x}_mpe"][i])[:, None] * k


def run_level(cas, energies: list[float]) -> None:
    """End of an engine run (cascade still alive): the shape-elastic / coupled-level angular distributions of every
    recorded energy, into specout.RUN["ang"]. INCOGNITA_SPECOUT_DA=0 skips them."""
    from physics.hf import specout

    if specout.RUN is None or not energies or os.environ.get("INCOGNITA_SPECOUT_DA", "1") == "0":
        return
    try:
        import time

        t0 = time.process_time()
        if cas._coupled_band() is None:
            r = shape_elastic_spherical(cas, energies)
        else:
            r = coupled(cas, energies)
        r["da_cpu_s"] = np.array(time.process_time() - t0)
        t1 = time.process_time()
        r.update(dwba_levels(int(cas.Zt), int(cas.At), energies, NLEV))
        r["dwba_cpu_s"] = np.array(time.process_time() - t1)
        specout.RUN["ang"] = r
    except Exception as exc:  # noqa: BLE001 -- output only
        specout.RUN.setdefault("ang_errors", []).append(f"run_level {type(exc).__name__}: {exc}")


def nubar_wahl(Zc: int, Ac: int, ein: float, bn: float, c1: float = 1.0, c2: float = 1.0) -> float:
    """nubarWahl.f90: Wahl's prompt nubar systematics for the compound (Zinit, Ainit), Bn = S(0, 0, 1)."""
    fz = 1.0 if Zc % 2 == 0 else -1.0
    nc = Ac - Zc
    fn = 1.0 if nc % 2 == 0 else -1.0
    term1 = 2.286 + 0.147 * (Zc - 92) + 0.054 * (Ac - 236) + 0.040 * (2.0 - fz - fn)
    term2 = 0.0
    if ein > 0.0:
        th = 11.47 - 0.166 * Zc * Zc / float(Ac) + 0.093 * (2.0 - fz - fn) - bn
        term2 = (0.145 - 0.0043 * (Ac - 236)) * (ein - th)
    return c1 * term1 + c2 * term2


# --------------------------------------------------------------------------------------------- pack
def pack(energies: list[dict], spectra: dict) -> dict:
    """Angular/DDX arrays for the run (see module doc)."""
    out = {}
    if not energies or "so_egrid" not in spectra:
        return out
    from physics.hf import specout

    ctx = specout.RUN
    eg = spectra["so_egrid"]
    e_inc = spectra["so_e_inc_mev"]
    errs = []
    # Kalbach slopes
    if ctx is not None:
        sm = smyers(int(ctx["Zc"]), int(ctx["Ac"]))
        k0 = int(ctx["k0"])
        for t, x in enumerate(specout.PARNAME):
            out[f"so_{x}_kal_a"] = np.stack([kalbach_a(k0, t, float(e), eg, sm) for e in e_inc])
        out["so_smyers"] = sm
    # prompt nubar: TALYS's default-run value (totalxs.f90:124, nubarWahl.f90; first chance, Wahl systematics)
    if ctx is not None and ctx.get("flagfission"):
        out["so_nubar_wahl"] = np.array([nubar_wahl(ctx["Zc"], ctx["Ac"], float(r["e_inc_mev"]), r.get("S_n_cn", np.nan),
                                                    *ctx.get("cnubar", (1.0, 1.0))) for r in energies])
    # per-energy compound Legendre + engine level numbers
    recs = [r.get("ang") for r in energies]
    nlev = max((len(r["comp_leg"]) for r in recs if r and "comp_leg" in r), default=0)
    if nlev:
        ne = len(recs)
        cl = np.zeros((ne, nlev, LCOMP + 1)); cr = np.full((ne, nlev), np.nan); ls = np.full((ne, nlev), -1)
        le = np.full((ne, nlev), np.nan); xd = np.zeros((ne, nlev)); xdd = np.zeros((ne, nlev)); el = np.zeros((ne, 3))
        for i, r in enumerate(recs):
            if not r or "comp_leg" not in r:
                continue
            n = len(r["comp_leg"])
            cl[i, :n] = r["comp_leg"]; cr[i, :n] = r["comp_ratio"]; ls[i, :n] = r["level_two_spin"]
            m = min(n, len(r["level_e"])); le[i, :m] = r["level_e"][:m]
            m = min(n, len(r["xsdisc"])); xd[i, :m] = r["xsdisc"][:m]
            m = min(n, len(r["xsdirdisc"])); xdd[i, :m] = r["xsdirdisc"][:m]
            el[i] = (r["xselastot"], r["xscompel"], r["xsreac"])
        out.update(so_comp_leg=cl, so_comp_ratio=cr, so_level_two_spin=ls, so_level_e=le, so_level_xs=xd,
                   so_level_xsdir=xdd, so_elastic_xs=el, so_ltarget=np.array(recs[0]["ltarget"] if recs[0] else 0))
    # shape elastic / coupled levels (computed by run_level at the end of the engine run)
    if ctx is not None:
        for k, v in ctx.get("ang", {}).items():
            out["so_" + k] = np.asarray(v)
        errs += ctx.get("ang_errors", [])
    if errs:
        out["so_ang_errors"] = np.array("\n".join(errs))
    return out
