"""ELDA (Incognita extension; an OUTPUT, no effect on any existing number): neutron elastic and coupled-level inelastic
angular distributions from the incident coupled-channels S-matrix, plus TALYS's compound-elastic Legendre route.

Shape elastic and CC inelastic (ECIS `scam`/`resu` angular part, TALYS `directecis` -> `nn*ang.L00`). The S-matrix is the
one `solver.sum_blocks` sums: the same channel sets (`_ChannelMaker`), form factors, kinematics, radial grid, soswitch split
and per-energy total-J convergence (QUIET_J, j_tol), solved here on the reference Python path (`solver.smatrix`,
minus_identity, D = S - 1) so every block's matrix is kept. The amplitude for a spin-1/2 projectile on a target of spin I
(beam along z, phi = 0), final level of spin I':

    f_{M'v', Mv}(theta) = -(i / 2k) sum_{J pi} sum_{c=(l j) in g.s.} sum_{c'=(l' j') in I'}
        sqrt(4 pi (2l+1)) <l 0 1/2 v | j v> <j v I M | J M_J>  D^{J pi}_{c'c}
        <j' m' I' M' | J M_J> <l' m'-v' 1/2 v' | j' m'> Y_{l' m'-v'}(theta, 0)

with no i^(l-l') factor: the port's channel basis is ECIS's i^l [(l 1/2) j, I] J (checked against the textbook reduced
matrix element: coupling_matrix = (-1)^((l-l')/2) x standard x a level-pair constant, development notes phase_check), so the plane
wave's i^l and the outgoing H+'s i^-l' cancel against the basis phase. dsigma/dOmega = sum |f|^2 / (2 (2I+1)) (centre of
mass, flux-normalised D so the k'/k factor is already in). Checks: the integral equals accumulate's `el` / `direct` sums.

Compound elastic (comptarget.f90:665-688 + angdis.f90:97-101): the Blatt-Biedenharn Legendre coefficients
    cleg(L) += phase angfac clebsch(l l L;000) W(J j J j; I L) W(j j l l; L s) clebsch(l' l' L) W(J j' J j'; I L) W(j' j' l' l'; L s)
               x compterm / (2L+1),   compterm = CNfactor (2J+1) T_lj T_l'j' / denom_J
with T = the incident Tjlinc. The per-(J, pi) Hauser-Feshbach denominator (all exit channels, WFC) is NOT exported by the
compound kernels; here it is taken J-independent (one constant per energy) and the result is normalised to the engine's own
compound-elastic cross section, so the integral is exact and only the L > 0 shape carries the approximation. The isotropic
alternative (TALYS without flagcompang, angdis.f90:103-108) is returned as well.

Test: tests/hf/test_angular.py
"""

from __future__ import annotations

import math
import os
from functools import lru_cache

import numpy as np
import torch

from physics.hf.core.tensors import DTYPE

ENV = "INCOGNITA_ELDA"
RECORD: list[dict] = []  # incident_coupled's calls, filled only when ENV is set (record())


def record(**kw) -> None:
    """Keep the arguments of one incident coupled-channels solve (no copy of the numbers; nothing is changed)."""
    if os.environ.get(ENV, "").strip() not in ("", "0", "n", "no"):
        RECORD.append(kw)


# ----------------------------------------------------------------------------------------------- angular-momentum algebra
@lru_cache(maxsize=None)
def _lf(n: int) -> float:
    return math.lgamma(n + 1.0)


@lru_cache(maxsize=None)
def cg2(j1: int, m1: int, j2: int, m2: int, j: int, m: int) -> float:
    """<j1 m1 j2 m2 | j m> (Condon-Shortley) on DOUBLED arguments."""
    if m1 + m2 != m or abs(m1) > j1 or abs(m2) > j2 or abs(m) > j:
        return 0.0
    if j > j1 + j2 or j < abs(j1 - j2) or (j1 + j2 + j) % 2 or (j1 + m1) % 2 or (j2 + m2) % 2 or (j + m) % 2:
        return 0.0
    a = [(j1 + j2 - j) // 2, (j1 - j2 + j) // 2, (-j1 + j2 + j) // 2, (j1 + j2 + j) // 2 + 1]
    pre = 0.5 * (_lf(a[0]) + _lf(a[1]) + _lf(a[2]) - _lf(a[3]))
    pre += 0.5 * (_lf((j1 + m1) // 2) + _lf((j1 - m1) // 2) + _lf((j2 + m2) // 2) + _lf((j2 - m2) // 2)
                  + _lf((j + m) // 2) + _lf((j - m) // 2))
    s = 0.0
    for k in range(0, a[3] + 1):
        d = [k, (j1 + j2 - j) // 2 - k, (j1 - m1) // 2 - k, (j2 + m2) // 2 - k, (j - j2 + m1) // 2 + k,
             (j - j1 - m2) // 2 + k]
        if min(d) < 0:
            continue
        s += (-1) ** k * math.exp(pre - sum(_lf(x) for x in d))
    return s * math.sqrt(j + 1.0)


@lru_cache(maxsize=None)
def racah2(a: int, b: int, c: int, d: int, e: int, f: int) -> float:
    """Racah W(a b c d; e f) on doubled arguments (racah.f90 sign convention: W = (-1)^(a+b+c+d) {a b e; d c f})."""
    def tri(x, y, z):
        if (x + y + z) % 2 or z > x + y or z < abs(x - y):
            return None
        return 0.5 * (_lf((x + y - z) // 2) + _lf((x - y + z) // 2) + _lf((-x + y + z) // 2) - _lf((x + y + z) // 2 + 1))
    t = [tri(a, b, e), tri(c, d, e), tri(a, c, f), tri(b, d, f)]
    if any(x is None for x in t):
        return 0.0
    pre = sum(t)
    s1, s2, s3, s4 = (a + b + e) // 2, (c + d + e) // 2, (a + c + f) // 2, (b + d + f) // 2
    t1, t2, t3 = (a + b + c + d) // 2, (a + d + e + f) // 2, (b + c + e + f) // 2
    s = 0.0
    for k in range(max(s1, s2, s3, s4), min(t1, t2, t3) + 1):
        s += (-1) ** (k + t1) * math.exp(_lf(k + 1) - _lf(k - s1) - _lf(k - s2) - _lf(k - s3) - _lf(k - s4)
                                         - _lf(t1 - k) - _lf(t2 - k) - _lf(t3 - k) + pre)
    return s


_YLM: dict = {}


def ylm_table(lmax: int, theta_deg: np.ndarray) -> np.ndarray:
    """Y_{l m}(theta, 0) as (lmax+1, 2 lmax+1, n_theta), index m + lmax (Condon-Shortley). Cached per (lmax, grid)."""
    key = (int(lmax), np.asarray(theta_deg, float).tobytes())
    got = _YLM.get(key)
    if got is None:
        if len(_YLM) > 64:
            _YLM.clear()
        got = _YLM[key] = _ylm_table(lmax, theta_deg)
    return got


def _ylm_table(lmax: int, theta_deg: np.ndarray) -> np.ndarray:
    from scipy.special import sph_harm_y

    th = np.deg2rad(np.asarray(theta_deg, float))
    out = np.zeros((lmax + 1, 2 * lmax + 1, th.size))
    for l in range(lmax + 1):  # noqa: E741
        for m in range(-l, l + 1):
            out[l, m + lmax] = np.real(sph_harm_y(l, m, th, 0.0))
    return out


# ------------------------------------------------------------------------------------------------- amplitudes per block
def _initial_states(two_i: int) -> list[tuple[int, int]]:
    return [(mm, nu) for mm in range(-two_i, two_i + 1, 2) for nu in (-1, 1)]


_GEO: dict = {}  # SPECOUT: per-block geometric weights (energy-independent), cleared per run by specout.reset


def _block_geometry(two_j, lev, ls, js2, two_i0, level_two_spin, levels_out):
    """The Clebsch-Gordan part of block_amplitudes: ain (entrance, initial) and per exit level b the weights
    w (exc, final, initial) and the Y_{l m} row/column each term reads (l index, m + lmax offset left to the caller)."""
    key = (two_j, tuple(lev), tuple(ls), tuple(js2), two_i0, tuple(level_two_spin), tuple(levels_out))
    got = _GEO.get(key)
    if got is not None:
        return got
    ini = _initial_states(two_i0)
    ent = [c for c in range(len(lev)) if lev[c] == 0]
    ain = np.zeros((len(ent), len(ini)))
    for a, c in enumerate(ent):
        l2, j2 = 2 * ls[c], js2[c]
        for i, (mm, nu) in enumerate(ini):
            ain[a, i] = math.sqrt(4 * math.pi * (ls[c] * 2 + 1)) * cg2(l2, 0, 1, nu, j2, nu) * cg2(j2, nu, two_i0, mm, two_j, nu + mm)
    per = {}
    for b in levels_out:
        exc = [c for c in range(len(lev)) if lev[c] == b]
        if not exc:
            continue
        two_ib = level_two_spin[b]
        fin = _initial_states(two_ib)
        w = np.zeros((len(exc), len(fin), len(ini)))
        lix = np.zeros((len(exc), len(fin), len(ini)), dtype=np.int64)
        mix = np.zeros((len(exc), len(fin), len(ini)), dtype=np.int64)
        for a, c in enumerate(exc):
            l2, j2 = 2 * ls[c], js2[c]
            for f, (mp, nup) in enumerate(fin):
                for i, (mm, nu) in enumerate(ini):
                    mj = nu + mm
                    mjp = mj - mp
                    ml2 = mjp - nup
                    if abs(mjp) > j2 or abs(ml2) > l2:
                        continue
                    w[a, f, i] = cg2(j2, mjp, two_ib, mp, two_j, mj) * cg2(l2, ml2, 1, nup, j2, mjp)
                    lix[a, f, i] = ls[c]
                    mix[a, f, i] = ml2 // 2
        per[b] = (exc, w, lix, mix)
    _GEO[key] = (ent, ain, per)
    return _GEO[key]


def block_amplitudes(ch, d: np.ndarray, two_i0: int, level_two_spin: list[int], levels_out: list[int], ylm: np.ndarray,
                     lmax_y: int) -> dict[int, np.ndarray]:
    """Contribution of one (J, pi) block to f (without -i/2k): {level: (E, n_theta, n_final, n_initial) complex}.
    SPECOUT: the Clebsch-Gordan weights come from `_block_geometry` (cached across energies); the same terms."""
    if os.environ.get("SPECOUT_CC_REFAMP", "0") != "1":
        two_j = int(ch.twoJ)
        lev = ch.level.tolist()
        ls = ch.l.tolist()
        js2 = [int(round(2 * float(x))) for x in ch.j.tolist()]
        ent, ain, per = _block_geometry(two_j, lev, ls, js2, two_i0, level_two_spin, levels_out)
        g = np.einsum("eqc,ci->eqi", d[:, :, ent], ain)
        out = {}
        for b, (exc, w, lix, mix) in per.items():
            aout = w[..., None] * ylm[lix, mix + lmax_y]  # (a, f, i, T)
            out[b] = np.einsum("afit,eai->etfi", aout, g[:, exc, :])
        return out
    two_j = int(ch.twoJ)
    lev = ch.level.tolist()
    ls = ch.l.tolist()
    js2 = [int(round(2 * float(x))) for x in ch.j.tolist()]
    ini = _initial_states(two_i0)
    ent = [c for c in range(len(lev)) if lev[c] == 0]
    ain = np.zeros((len(ent), len(ini)))
    for a, c in enumerate(ent):
        l2, j2 = 2 * ls[c], js2[c]
        for i, (mm, nu) in enumerate(ini):
            ain[a, i] = math.sqrt(4 * math.pi * (ls[c] * 2 + 1)) * cg2(l2, 0, 1, nu, j2, nu) * cg2(j2, nu, two_i0, mm, two_j, nu + mm)
    g = np.einsum("eqc,ci->eqi", d[:, :, ent], ain)  # (E, N_out, n_initial)
    out = {}
    for b in levels_out:
        exc = [c for c in range(len(lev)) if lev[c] == b]
        if not exc:
            continue
        two_ib = level_two_spin[b]
        fin = _initial_states(two_ib)
        aout = np.zeros((len(exc), len(fin), len(ini), ylm.shape[2]))
        for a, c in enumerate(exc):
            l2, j2 = 2 * ls[c], js2[c]
            for f, (mp, nup) in enumerate(fin):
                for i, (mm, nu) in enumerate(ini):
                    mj = nu + mm  # doubled M_J
                    mjp = mj - mp  # doubled m_j'
                    ml2 = mjp - nup
                    if abs(mjp) > j2 or abs(ml2) > l2:
                        continue
                    w = cg2(j2, mjp, two_ib, mp, two_j, mj) * cg2(l2, ml2, 1, nup, j2, mjp)
                    if w != 0.0:
                        aout[a, f, i] = w * ylm[ls[c], ml2 // 2 + lmax_y]
        out[b] = np.einsum("afit,eai->etfi", aout, g[:, exc, :])
    return out


# --------------------------------------------------------------------------------------------- coupled-channels driver
def _setup(omp_sub, m_proj, m_targ, z_prod, e, band, nj, ref, deformed_so, scheme, band_beta):
    """(maker, ff, kin, h, nmatch, r) exactly as solver.solve_rotational / solve_vibrational build them."""
    from physics.hf.ecis import solver as S

    kin, h, nmatch, r = S._grid_and_kinematics(omp_sub, m_proj, m_targ, z_prod, e, band["e_mev"], ref, True)
    ls_, lp_ = band["spin"], band["parity"]
    key = (tuple(ls_.tolist()), ls_.dtype, tuple(lp_.tolist()), lp_.dtype)
    if band["colltype"] == "R":
        from physics.hf.ecis.formfactor import rotational_form_factors

        rb = band["rotbeta"]
        ff = rotational_form_factors(omp_sub, S._rounded_mass(m_targ, True), r, rb, band["deformation_length"],
                                     2 * int(rb.numel()), z_prod, deformed_so)
        maker = S._ChannelMaker("rot", key[0], key[1], key[2], key[3], (float(band["kband"]), bool(deformed_so)), int(nj), 0.5)
    elif scheme is not None:
        from physics.hf.ecis.formfactor import anharmonic_vibrational_form_factors

        ff = anharmonic_vibrational_form_factors(omp_sub, S._rounded_mass(m_targ, True), r, band_beta, scheme.codes, scheme.nbt1,
                                                 band["deformation_length"], z_prod)
        maker = S._ChannelMaker("vib2", key[0], key[1], key[2], key[3], (scheme, scheme.codes), int(nj), 0.5)
    else:
        from physics.hf.ecis.formfactor import vibrational_form_factors

        ff = vibrational_form_factors(omp_sub, S._rounded_mass(m_targ, True), r, band["vib_beta"], band["deformation_length"], z_prod)
        vl = band["vib_lambda"]
        maker = S._ChannelMaker("vib", key[0], key[1], key[2], key[3], (tuple(vl.tolist()), vl.dtype), int(nj), 0.5)
    return maker, ff, kin, h, nmatch, r


def _loop(maker, ff, kin, h, nmatch, r, n_lev, lmax, target_spin, two_spins, levels_out, ylm, lmax_y, j_tol=1.0e-10):
    """sum_blocks' Python loop (per-energy QUIET_J convergence, same J cap) keeping amplitudes."""
    from physics.hf.ecis import solver as S

    n_e = h.shape[0]
    two_i0 = two_spins[0]
    acc = {k: torch.zeros(n_e, dtype=DTYPE) for k in ("reac", "tot", "el")}
    acc["direct"] = torch.zeros((n_e, n_lev), dtype=DTYPE)
    acc["tjl"] = torch.zeros((n_e, lmax + 1, 2), dtype=DTYPE)
    amp = {}
    live = torch.ones(n_e, dtype=torch.bool)
    quiet = torch.zeros(n_e, dtype=torch.int64)
    two_j0 = (two_i0 + 1) % 2
    n_j, twoJ = 0, two_j0
    while bool(live.any()):
        block = torch.zeros(n_e, dtype=DTYPE)
        chs = []
        for par in (-1, 1):
            ch = maker(twoJ, par)
            if ch.level.numel() == 0 or not bool(ch.elastic.any()):
                continue
            chs.append(ch)
        # SPECOUT: the compiled block solves the engine's own sum_blocks uses (exact_bits=False = CCFAST2 below
        # soswitch, SPEEDT3 otherwise; same equations, rounding-level differences from the Python `smatrix`)
        sms = S.smatrix_blocks(chs, ff, kin, h, nmatch, r, minus_identity=True,
                               exact_bits=os.environ.get("SPECOUT_CC_EXACT", "0") == "1")
        for ch, (s_mat, _op) in zip(chs, sms):  # noqa: B905
            got = S.accumulate(ch, s_mat, _op, kin, target_spin, 0.5, n_lev, lmax, minus_identity=True)
            m = live.to(DTYPE)
            for k in ("reac", "tot", "el"):
                acc[k] = acc[k] + got[k] * m
            acc["direct"] = acc["direct"] + got["direct"] * m[:, None]
            acc["tjl"] = acc["tjl"] + got["tjl"] * m[:, None, None]
            block = torch.maximum(block, got["reac"].abs() * m)
            dm = (s_mat.numpy() * live.numpy()[:, None, None])
            for b, v in block_amplitudes(ch, dm, two_i0, two_spins, levels_out, ylm, lmax_y).items():
                amp[b] = v if b not in amp else amp[b] + v
        n_j += 1
        ref = acc["reac"].abs()
        q = torch.where((ref > 0) & (block < j_tol * ref), quiet + 1, torch.zeros_like(quiet))
        quiet = torch.where(live, q, quiet)
        if n_j > 4 * (lmax + 2):
            break
        live = live & (quiet < S.QUIET_J)
        twoJ += 2
    return acc, amp


def coupled_angular(rec: dict, theta_deg: np.ndarray, levels_out: list[int] | None = None) -> dict:
    """Angular distributions for one recorded incident_coupled call (`record`). Returns numpy arrays on the call's
    energy axis: e_mev, theta, el_shape (E, T) mb/sr, direct (E, nlev_out, T) mb/sr, and the integrated sums of this
    solve (sigma_shape_el, sigma_direct, sigma_reac, sigma_tot, tjl) for the integral checks."""
    from physics.hf.ecis import solver as S
    from physics.hf.ecis.incident import SOSWITCH_DEFAULT_MEV, _refine_axis, _slice_energies
    from physics.hf.omp.schrodinger import PARMASS_AMU, PARZ, nucleus_mass_amu

    omp, Z, A, e, band = rec["omp"], rec["Z"], rec["A"], rec["e"], rec["band"]
    particle, nj, options, refine = rec["particle"], rec["lmax"], rec["options"], rec.get("refine", 1)
    if particle != 1:
        raise NotImplementedError("ELDA: neutron incident only")
    scheme = band_beta = None
    if band["colltype"] == "V" and int(band["iphonon"].max()) > 1:
        from physics.hf.ecis.vibm import scheme_from_band

        scheme, band_beta = scheme_from_band(band)
    soswitch = SOSWITCH_DEFAULT_MEV if options is None else float(options.soswitch_mev)
    m_t = nucleus_mass_amu(Z, A)
    n_e = e.shape[0]
    n_lev = int(band["spin"].numel())
    two_spins = [int(round(2 * float(x))) for x in band["spin"].tolist()]
    if levels_out is None:
        levels_out = list(range(n_lev))
    ylm = ylm_table(nj + 1, theta_deg)
    ref_ax = _refine_axis(e, refine)
    above = (e > soswitch) if band["colltype"] == "R" else torch.zeros(n_e, dtype=torch.bool)
    th = np.asarray(theta_deg, float)
    el = np.zeros((n_e, th.size))
    dr = np.zeros((n_e, len(levels_out), th.size))
    sums = {k: np.zeros(n_e) for k in ("el", "reac", "tot")}
    sums["direct"] = np.zeros((n_e, n_lev))
    sums["tjl"] = np.zeros((n_e, nj + 1, 2))
    for deformed_so in (False, True):
        for rf in sorted({int(v) for v in ref_ax.tolist()}):
            m = (above if deformed_so else ~above) & (ref_ax == rf)
            if not bool(m.any()):
                continue
            idx = torch.nonzero(m).reshape(-1)
            sub = omp.select(idx) if hasattr(omp, "select") else _slice_energies(omp, idx)
            maker, ff, kin, h, nmatch, r = _setup(sub, PARMASS_AMU[particle], m_t, float(PARZ[particle] * Z), e[idx], band, nj, rf,
                                                  deformed_so, scheme, band_beta)
            acc, amp = _loop(maker, ff, kin, h, nmatch, r, n_lev, nj, float(band["spin"][0]), two_spins, levels_out, ylm, nj + 1)
            k1 = kin.k_fm[:, 0].numpy()
            pre = 1.0 / (4.0 * k1 ** 2) * 10.0 / (2.0 * (two_spins[0] + 1))  # |-i/2k|^2, fm^2 -> mb, spin average
            ii = idx.numpy()
            for q, b in enumerate(levels_out):
                if b not in amp:
                    continue
                x = (np.abs(amp[b]) ** 2).sum(axis=(2, 3)) * pre[:, None]
                if b == 0:
                    el[ii] = x
                dr[ii, q] = x
            fac = math.pi / k1 ** 2 * 10.0
            for k in ("el", "reac", "tot"):
                sums[k][ii] = fac * acc[k].numpy()
            sums["direct"][ii] = fac[:, None] * acc["direct"].numpy()
            sums["tjl"][ii] = acc["tjl"].numpy()
    sums["reac"] = sums["reac"] + sums["direct"].sum(axis=1)
    return {"e_mev": e.numpy().copy(), "theta": th, "el_shape": el, "direct": dr, "levels_out": np.asarray(levels_out),
            "level_e_mev": band["e_mev"].numpy().copy(), "level_two_spin": np.asarray(two_spins),
            "sigma_shape_el": sums["el"], "sigma_direct": sums["direct"], "sigma_reac": sums["reac"], "sigma_tot": sums["tot"],
            "tjl": sums["tjl"], "two_i0": two_spins[0]}


# ------------------------------------------------------------------------------------------------------ compound elastic
def compound_elastic_legendre(tjl: np.ndarray, two_i: int, target_parity: int = 1) -> np.ndarray:
    """TALYS's compound-elastic cleg(L) per energy with a J-independent denominator, UNNORMALISED: (E, Lmax+1) for even L.
    tjl: (E, l, 2) incident T_lj, column 0 = j = l-1/2, 1 = j = l+1/2 (contract order)."""
    n_e, nl, _ = tjl.shape
    lmax = nl - 1
    out = np.zeros((n_e, 2 * lmax + 2))
    two_jmax = 2 * lmax + 1 + two_i
    for two_j in range((two_i + 1) % 2, two_jmax + 1, 2):
        for par in (-1, 1):
            ch = []  # (l, two_jj, T(E))
            for l in range(lmax + 1):  # noqa: E741
                if target_parity * (-1) ** l != par:
                    continue
                for col, two_jj in ((0, 2 * l - 1), (1, 2 * l + 1)):
                    if two_jj < 0 or not (abs(two_j - two_i) <= two_jj <= two_j + two_i):
                        continue
                    ch.append((l, two_jj, tjl[:, l, col]))
            if not ch:
                continue
            tsum = sum(t for _, _, t in ch)
            for li, jin, tin in ch:
                for lo, jout, tout in ch:
                    angfac = (two_j + 1) * (jout + 1) * (jin + 1) * (2 * li + 1) * (2 * lo + 1) / (4 * math.pi)
                    llmax = min(2 * li, 2 * lo, two_j)
                    for ll in range(0, llmax + 1, 2):
                        a = (angfac * cg2(2 * li, 0, 2 * li, 0, 2 * ll, 0) * racah2(two_j, jin, two_j, jin, two_i, 2 * ll)
                             * racah2(jin, jin, 2 * li, 2 * li, 2 * ll, 1) * cg2(2 * lo, 0, 2 * lo, 0, 2 * ll, 0)
                             * racah2(two_j, jout, two_j, jout, two_i, 2 * ll) * racah2(jout, jout, 2 * lo, 2 * lo, 2 * ll, 1))
                        if a == 0.0:
                            continue
                        # elastic: Rspin = targetspin, parspin(type) = parspin(k0) -> phase +1
                        out[:, ll] += a * (two_j + 1) * tin * tout / (2 * ll + 1)
            del tsum
    return out


def legendre_da(cleg: np.ndarray, sigma: np.ndarray, theta_deg: np.ndarray) -> np.ndarray:
    """angdis.f90: compad = sum (2L+1) cleg_L P_L, rescaled so that its integral 4 pi cleg_0 = sigma. (E, T) mb/sr."""
    from numpy.polynomial.legendre import legval

    x = np.cos(np.deg2rad(np.asarray(theta_deg, float)))
    out = np.zeros((cleg.shape[0], x.size))
    for i in range(cleg.shape[0]):
        if cleg[i, 0] <= 0 or sigma[i] <= 0:
            out[i] = sigma[i] / (4 * math.pi)
            continue
        c = cleg[i] * (2 * np.arange(cleg.shape[1]) + 1) * (sigma[i] / (4 * math.pi * cleg[i, 0]))
        out[i] = legval(x, c)
    return out


def integrate(da: np.ndarray, theta_deg: np.ndarray) -> np.ndarray:
    """2 pi int da sin(theta) dtheta on the given grid (composite Simpson if odd points and uniform, else trapezoid)."""
    from scipy.integrate import simpson

    th = np.deg2rad(np.asarray(theta_deg, float))
    return 2 * math.pi * simpson(da * np.sin(th), x=th, axis=-1)


__all__ = ["ENV", "RECORD", "record", "coupled_angular", "compound_elastic_legendre", "legendre_da", "integrate", "ylm_table",
           "cg2", "racah2"]
