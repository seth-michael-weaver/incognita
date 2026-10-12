"""EWCC (Incognita extension, default OFF): the Engelbrecht-Weidenmueller transformation of the Moldauer
width-fluctuation correction for coupled-channels targets.

Hauser-Feshbach with width fluctuations assumes the penetration matrix P = 1 - <S><S>^dagger is
diagonal in channel space. For a target whose collective levels are coupled (ECIS rotor or
vibrator, `colltype R|V`), the incident coupled-channels <S> connects the ground-state channels
with the channels on the coupled levels, and P is not diagonal at a fixed (J, parity).
Engelbrecht & Weidenmueller (PRC 8 (1973) 859) diagonalise P,

    P = U^dagger diag(p) U,         S~ = U S U^T  (time-reversal symmetric, <S~> diagonal),

apply the statistical theory (here Moldauer, the engine's widthmode 1) in the eigen-channel space
with transmissions p_alpha, and transform the fluctuation cross section back
(Kawano, Capote, Hilaire, Chau, PRC 94 (2016) 014612, eqs. 13-16):

    <|S^fl_ab|^2> = sum_alpha |U_alpha a|^2 |U_alpha b|^2 X_alpha alpha
                  + sum_{alpha != beta} ( |U_alpha a|^2 |U_beta b|^2
                                          + U*_alpha a U_alpha b U*_beta b U_beta a ) X_alpha beta,
    X_alpha beta = p_alpha p_beta W_alpha beta / st     (Moldauer, W with the elastic factor on alpha = beta).

A channel outside the coupled set is its own eigen-channel, so for an exit b outside it the sum
collapses to sum_alpha |U_alpha a|^2 X_alpha b: the incident sum H_m = sum_a T_a / (1 + x_m f_a)
that `wfc.moldauer_sums` factorises is replaced by sum_alpha w_alpha p_alpha / (1 + x_m f_alpha),
w_alpha = sum_{a incident} |U_alpha a|^2. Every channel enters Moldauer's product once, the coupled
ones as eigen-channels.

P on the coupled channels (registered in development notes) is the CC solve's own, as in ECIS's compound
routine (scam, Satchler P, lo(83) = F) and Kawano et al.: the excited coupled levels' transmissions
become the CC P_cc at the incident energy instead of TALYS's ground-state Tjl at E - E_level. The
ground-state diagonal stays the engine's Tjlinc (the same CC quantity from the cached solve; equal to
P_aa to ~1e-5), via P' = D P D, D = sqrt(Tjlinc / P_aa) on ground-state channels and 1 elsewhere.
st moves by the change of the coupled diagonal. (Keeping the engine's diagonal everywhere and taking
only the correlation from the CC solve was tried first: it gives eigen-transmissions up to 1.58 on
W-184, i.e. it breaks unitarity, so it is not used.) A target without coupling, or a block with a
single coupled cell, is not routed through this module, so the default paths stay bit-identical.

Scope: neutron incident, widthmode 1 (Moldauer) where comptarget applies WFC (E_inc <= ewfc) and plain
Hauser-Feshbach (W = 1) in the eigen space above it, Python compound path only. `engine_c.front` and the batch kernels refuse when the switch is on and
the target is coupled; the GPU capture/full paths raise.

Keyword `ewtransform y` (lines/cards) or env INCOGNITA_EWFC = y|1 (keyword `ewfc` is not usable: TALYS's own `ewfc`
keyword is the WFC energy cut and is left alone).
"""

from __future__ import annotations

import math
import os
from dataclasses import dataclass

import numpy as np
import torch
from torch import Tensor

from physics.hf.core.tensors import DTYPE

ENV = "INCOGNITA_EWFC"
STATS: dict = {"blocks": 0, "ew_blocks": 0, "pmax": 0.0, "pclip": 0, "diag_check": 0.0, "offdiag_max": 0.0}


def enabled(options=None) -> bool:
    """The keyword `ewtransform y|n` if set to y, else the environment INCOGNITA_EWFC (y|n)."""
    k = str(getattr(options, "ewtransform", "n") or "n").strip().lower()
    if k in ("y", "yes", "1"):
        return True
    if k not in ("n", "no", "0", ""):
        raise ValueError(f"ewtransform {k!r}: use y or n")
    v = os.environ.get(ENV, "").strip().lower()
    if v in ("", "0", "n", "no", "off"):
        return False
    if v in ("y", "1", "yes", "on"):
        return True
    raise ValueError(f"{ENV}={v!r}: use y or n")


@dataclass
class CCBlock:
    """One (J, parity) block of the incident CC solve at one energy, open channels only."""

    two_j: int
    parity: int
    level: np.ndarray  # band level index (0 = ground state)
    l: np.ndarray  # noqa: E741
    ud: np.ndarray  # j = l + ud/2
    pmat: np.ndarray  # complex (n, n), 1 - S S^dagger


@dataclass
class CCBlocks:
    e_mev: float
    band_e_mev: np.ndarray
    band_two_spin: np.ndarray
    blocks: dict  # (two_j, parity) -> CCBlock


# ------------------------------------------------------------------------------------------------- the CC S-matrix
_MEMO: dict = {}


def cc_blocks(Z: int, A: int, e_mev: float, band: dict, options, two_j_max: int) -> CCBlocks:
    """Solve the incident coupled channels at one energy on the reference Python path and keep P per
    (J, parity), J up to `two_j_max` (both parities). Same OMP (T4, incl. fit cards through
    `options`), channel sets, form factors, radial grid and refinement as `incident_coupled`."""
    key = (Z, A, float(e_mev), int(two_j_max), id(options))
    if key in _MEMO:
        return _MEMO[key]
    from physics.hf.ecis import solver as S
    from physics.hf.ecis.angular import _setup
    from physics.hf.ecis.incident import SOSWITCH_DEFAULT_MEV, _refine_axis, _t4_parameters, njmax_incident
    from physics.hf.omp.schrodinger import PARMASS_AMU, nucleus_mass_amu

    e = torch.tensor([float(e_mev)], dtype=DTYPE)
    omp = _t4_parameters(Z, A, 1, e, options)
    scheme = band_beta = None
    if band["colltype"] == "V" and int(band["iphonon"].max()) > 1:
        from physics.hf.ecis.vibm import scheme_from_band

        scheme, band_beta = scheme_from_band(band)
    soswitch = SOSWITCH_DEFAULT_MEV if options is None else float(options.soswitch_mev)
    deformed_so = bool(band["colltype"] == "R" and float(e_mev) > soswitch)
    nj = njmax_incident(A, PARMASS_AMU[1], float(e_mev))
    ref = int(_refine_axis(e, 1)[0])
    m_t = nucleus_mass_amu(Z, A)
    maker, ff, kin, h, nmatch, r = _setup(omp, PARMASS_AMU[1], m_t, 0.0, e, band, nj, ref, deformed_so, scheme, band_beta)
    two_i0 = int(round(2 * float(band["spin"][0])))
    blocks = {}
    for two_j in range((two_i0 + 1) % 2, int(two_j_max) + 1, 2):
        for par in (-1, 1):
            ch = maker(two_j, par)
            if ch.level.numel() == 0 or not bool(ch.elastic.any()):
                continue
            d, op = S.smatrix(ch, ff, kin, h, nmatch, r, minus_identity=True)
            o = op[0].numpy().astype(bool)
            if not o.any():
                continue
            dd = d[0].numpy()[np.ix_(o, o)]
            # P = 1 - S S^+ with S = 1 + D, written without the cancelling 1 (accumulate's form)
            pm = -dd - dd.conj().T - dd @ dd.conj().T
            lv = ch.level.numpy()[o]
            ll = ch.l.numpy()[o]
            jj = ch.j.numpy()[o]
            ud = np.rint(2.0 * (jj - ll)).astype(int)
            blocks[(two_j, par)] = CCBlock(two_j, par, lv, ll, ud, pm)
    out = CCBlocks(float(e_mev), band["e_mev"].numpy().copy(),
                   np.rint(2 * band["spin"].numpy()).astype(int), blocks)
    if len(_MEMO) > 64:
        _MEMO.clear()
    _MEMO[key] = out
    return out


def cc_blocks_batch(Z: int, A: int, energies, band: dict, options, chunk: int = 8, j_tol: float = 1.0e-12) -> dict:
    """`cc_blocks` for many incident energies at once (the same per-energy grid, split, as `incident_coupled`, by
    soswitch side and radial refinement, in chunks of `chunk` energies). The total-J loop stops for an energy after two
    consecutive J whose ground-state penetrability trace is below `j_tol` x the largest so far (`sum_blocks`' rule);
    a block not kept is Moldauer in `_case` (its population is <= j_tol of the energy's). Returns {e: CCBlocks}."""
    from physics.hf.ecis import solver as S
    from physics.hf.ecis.angular import _setup
    from physics.hf.ecis.incident import SOSWITCH_DEFAULT_MEV, _refine_axis, _t4_parameters, _slice_energies, njmax_incident
    from physics.hf.omp.schrodinger import PARMASS_AMU, nucleus_mass_amu

    e_all = torch.tensor(sorted({float(x) for x in energies}), dtype=DTYPE)
    omp = _t4_parameters(Z, A, 1, e_all, options)
    scheme = band_beta = None
    if band["colltype"] == "V" and int(band["iphonon"].max()) > 1:
        from physics.hf.ecis.vibm import scheme_from_band

        scheme, band_beta = scheme_from_band(band)
    soswitch = SOSWITCH_DEFAULT_MEV if options is None else float(options.soswitch_mev)
    above = (e_all > soswitch) if band["colltype"] == "R" else torch.zeros(e_all.shape, dtype=torch.bool)
    ref_ax = _refine_axis(e_all, 1)
    m_t = nucleus_mass_amu(Z, A)
    two_i0 = int(round(2 * float(band["spin"][0])))
    band_e = band["e_mev"].numpy().copy()
    band_s = np.rint(2 * band["spin"].numpy()).astype(int)
    out = {float(e): CCBlocks(float(e), band_e, band_s, {}) for e in e_all.tolist()}
    groups = []
    for dso in (False, True):
        for rf in sorted({int(v) for v in ref_ax.tolist()}):
            idx = torch.nonzero((above == dso) & (ref_ax == rf)).reshape(-1)
            for lo in range(0, idx.numel(), chunk):
                groups.append((dso, rf, idx[lo:lo + chunk]))
    for dso, rf, idx in groups:
        sub = omp.select(idx) if hasattr(omp, "select") else _slice_energies(omp, idx)
        e = e_all[idx]
        nj = njmax_incident(A, PARMASS_AMU[1], float(e.max()))
        maker, ff, kin, h, nmatch, r = _setup(sub, PARMASS_AMU[1], m_t, 0.0, e, band, nj, rf, dso, scheme, band_beta)
        n_e = idx.numel()
        best = np.zeros(n_e)
        quiet = np.zeros(n_e, dtype=int)
        two_j = (two_i0 + 1) % 2
        while True:
            tr = np.zeros(n_e)
            for par in (-1, 1):
                ch = maker(two_j, par)
                if ch.level.numel() == 0 or not bool(ch.elastic.any()):
                    continue
                d, op = S.smatrix(ch, ff, kin, h, nmatch, r, minus_identity=True)
                dn, opn = d.numpy(), op.numpy().astype(bool)
                lv_all, l_all, j_all = ch.level.numpy(), ch.l.numpy(), ch.j.numpy()
                for k in range(n_e):
                    if quiet[k] >= 2:
                        continue
                    o = opn[k]
                    if not o.any():
                        continue
                    dd = dn[k][np.ix_(o, o)]
                    pm = -dd - dd.conj().T - dd @ dd.conj().T
                    lv = lv_all[o]
                    tr[k] += float(np.real(np.trace(pm[np.ix_(lv == 0, lv == 0)])))
                    ll = l_all[o]
                    ud = np.rint(2.0 * (j_all[o] - ll)).astype(int)
                    out[float(e[k])].blocks[(two_j, par)] = CCBlock(two_j, par, lv, ll, ud, pm)
            best = np.maximum(best, tr)
            quiet = np.where((best > 0) & (tr < j_tol * best), quiet + 1, np.where(quiet >= 2, quiet, 0))
            two_j += 2
            if bool((quiet >= 2).all()) or two_j > 2 * (2 * nj + 2) + two_i0:
                break
    return out


_BATCH: dict = {}


def attach(inp, cas, e_inc_mev: float) -> None:
    """Give a CompoundInputs its CC blocks (inp.ew) when the switch is on and the target is coupled."""
    if not enabled(cas.options):
        return
    band = cas._coupled_band()
    if band is None or int(getattr(cas, "k0", 1)) != 1:
        return
    if inp.flagwidth and inp.wmode not in (0, 1):
        raise NotImplementedError("INCOGNITA_EWFC: only widthmode 1 (Moldauer) is wired")
    # every incident energy: Moldauer in the eigen space where comptarget applies WFC (E <= ewfc), Hauser-Feshbach
    # (W = 1) in the eigen space above it -- the transform itself is not a width-fluctuation effect, and stopping it
    # at ewfc would put a step into the coupled-level exits there
    key = (int(cas.Zt), int(cas.At), id(cas.options), tuple(getattr(cas, "energies", ()) or ()))
    if key not in _BATCH and key[3]:
        _BATCH.clear()
        _BATCH[key] = cc_blocks_batch(key[0], key[1], key[3], band, cas.options)
    got = _BATCH.get(key, {}).get(float(e_inc_mev))
    if got is None:
        got = _BATCH.setdefault(key, {})[float(e_inc_mev)] = cc_blocks_batch(key[0], key[1], (float(e_inc_mev),), band,
                                                                              cas.options)[float(e_inc_mev)]
    inp.ew = got


# ------------------------------------------------------------------------------------------ channel bookkeeping
def level_map(inp, cc: CCBlocks) -> dict[int, int]:
    """band level index -> residual level index of the target (k0), matched on energy and 2*spin."""
    r = inp.residuals[inp.k0]
    ex = np.asarray(r.ex_mev, float)
    out = {}
    for b, (eb, sb) in enumerate(zip(cc.band_e_mev, cc.band_two_spin, strict=True)):
        hit = np.nonzero(np.abs(ex[: r.nlast + 1] - eb) < 1.0e-5)[0] if hasattr(r, "nlast") else np.nonzero(np.abs(ex - eb) < 1.0e-5)[0]
        if hit.size:
            out[b] = int(hit[0])
    return out


def coupled_set(inp, cc: CCBlocks, J2: int, parity: int, chans, tinc: Tensor, kblock, lmap: dict):
    """The channels of (J2, parity) that the transform acts on, as residual-k0 cells.

    Returns None when the block has nothing to mix, else a dict with
      cells:  list of (lev, l, ud) -- coupled channels with a live engine transmission, then every
              incident channel the CC block does not carry (its own eigen-channel)
      t:      engine transmission of each cell (Tensor)
      pprime: P' on the cells (complex numpy, Hermitian)
      inc:    index of each incident channel (in `chans` order) into `cells`
    """
    blk = cc.blocks.get((J2, parity))
    if blk is None:
        return None
    tt = kblock.t  # (Nex, L, 3)
    w = kblock.weight  # (Nex, Jx, 2, L, 3)
    L = tt.shape[1]
    keep, cells, tv = [], [], []
    for c in range(blk.level.size):
        b = int(blk.level[c])
        if b not in lmap:
            continue
        lev, l, ud = lmap[b], int(blk.l[c]), int(blk.ud[c])
        if l >= L or lev >= tt.shape[0]:
            continue
        tcell = float(tt[lev, l, ud + 1])
        wsum = float(w[lev, :, :, l, ud + 1].sum())
        if tcell <= 1.0e-30 or wsum <= 0.0:
            continue
        if abs(wsum - 1.0) > 1.0e-12:  # engine level weight not a single state (e.g. Ag-109 level 23): left to plain Moldauer
            STATS["skip_weight"] = STATS.get("skip_weight", 0) + 1
            continue
        keep.append(c)
        cells.append((lev, l, ud))
        tv.append(tcell)
    if len(keep) < 2:
        return None
    pm = blk.pmat[np.ix_(keep, keep)]
    dg = np.real(np.diag(pm)).copy()
    if np.any(dg <= 0.0):
        return None
    t = np.asarray(tv)
    gs = np.array([lev == inp.ltarget for lev, _, _ in cells])
    # Full CC penetration matrix (ECIS scam's Satchler P, lo(83) = F; Kawano 2016): the coupled channels'
    # transmissions are the CC P_cc at this energy. The ground-state diagonal is the engine's Tjlinc (the same
    # quantity from the cached solve, equal to P_aa to ~1e-5), so P' = D P D with D = sqrt(T/P) on the ground
    # state and 1 on the excited coupled levels.
    scale = np.where(gs, np.sqrt(t / dg), 1.0)
    mode = os.environ.get("INCOGNITA_EWFC_DIAG", "")
    if mode == "engine":  # test hook: engine diagonal, no correlations -> Moldauer exactly
        pp = np.diag(t).astype(complex)
    else:
        pp = scale[:, None] * pm * scale[None, :]
        pp = 0.5 * (pp + pp.conj().T)
        if mode in ("1", "cc"):  # diagnostic: CC diagonal, correlations dropped
            pp = np.diag(np.real(np.diag(pp))).astype(complex)
    t_new = np.real(np.diag(pp)).copy()
    if os.environ.get("INCOGNITA_EWFC_DEBUG", "") == "1":
        STATS.setdefault("debug", []).append((float(inp.e_inc_mev), J2, parity, list(cells), t.tolist(), t_new.tolist()))
    dst = float(t_new.sum() - t.sum())
    t = t_new
    corr = np.abs(pm) / np.sqrt(dg[:, None] * dg[None, :])
    np.fill_diagonal(corr, 0.0)
    STATS["offdiag_max"] = max(STATS["offdiag_max"], float(corr.max()))
    lt = inp.ltarget
    # diagnostic: the CC P on the ground-state channels vs the engine's incident T
    idx = {cell: i for i, cell in enumerate(cells)}
    inc = []
    extra = []
    for ia, (l, ud) in enumerate(chans):
        i = idx.get((lt, l, ud))
        if i is None:
            extra.append(ia)
            inc.append(len(cells) + len(extra) - 1)
        else:
            inc.append(i)
            STATS["diag_check"] = max(STATS["diag_check"], abs(dg[i] / float(tinc[ia]) - 1.0) if float(tinc[ia]) > 1e-12 else 0.0)
    n0 = len(cells)
    if extra:
        n = n0 + len(extra)
        big = np.zeros((n, n), dtype=complex)
        big[:n0, :n0] = pp
        for k, ia in enumerate(extra):
            l, ud = chans[ia]
            cells.append((lt, l, ud))
            big[n0 + k, n0 + k] = float(tinc[ia])
            t = np.append(t, float(tinc[ia]))
        pp = big
    return {"cells": cells, "t": torch.as_tensor(t, dtype=DTYPE), "pprime": pp, "inc": inc, "n_cc": n0, "dst": dst}


# --------------------------------------------------------------------------------------------- the transform
def eigen(pprime: np.ndarray, n_cc: int):
    """p (real, ascending) and V with P' = V diag(p) V^+ (U = V^+). The trailing plain cells are left alone."""
    n = pprime.shape[0]
    v = np.eye(n, dtype=complex)
    p = np.real(np.diag(pprime)).copy()
    pe, ve = np.linalg.eigh(pprime[:n_cc, :n_cc])
    p[:n_cc] = pe
    v[:n_cc, :n_cc] = ve
    STATS["pmax"] = max(STATS["pmax"], float(pe.max()))
    if pe.min() < -1.0e-9 * max(float(pe.max()), 1.0e-30):
        raise FloatingPointError(f"EWFC: P' not positive semi-definite (min eigenvalue {pe.min():.3e})")
    p = np.clip(p, 0.0, None)
    if p.max() > 1.0 + 1.0e-6:
        STATS["pclip"] += 1  # counted (unitarity check), not clipped
    return p, v


def ew_populations(x: Tensor, wts: Tensor, st: Tensor, prod_rest_log: Tensor, gamw: Tensor,
                   p: np.ndarray, v: np.ndarray, inc: list[int], tinc: Tensor, wfcfactor: int, use_wfc: bool = True):
    """Moldauer in the eigen-channel space and the transform back.

    prod_rest_log: (M,) sum over the NON-transformed exit channels of -nu rho/2 log(1 + x f).
    Returns (Pm, Hm, sigma_cells) with
      Pm (M,): Moldauer's node weights including the eigen-channels,
      Hm (M,): sum over incident a and eigen alpha of |U_alpha a|^2 p_alpha / (1 + x f_alpha)
               (replaces wfc.moldauer_sums' incident sum for every non-transformed exit),
      sigma_cells (n,): sum over incident a of <|S^fl_ab|^2> * st for every transformed cell b
               (multiply by the engine's pref = CNfactor (2J+1) / st).
    """
    from physics.hf.compound import wfc

    pt = torch.as_tensor(p, dtype=DTYPE)
    if not use_wfc:  # Hauser-Feshbach in the eigen space: one node x = 0, weight 1, no elastic factor
        x = torch.zeros(1, dtype=DTYPE)
        wts = torch.ones(1, dtype=DTYPE)
        prod_rest_log = torch.zeros(1, dtype=DTYPE)
    nu = wfc.degrees_of_freedom(pt, st, wfcfactor)
    f = 2.0 * pt / (st * nu)  # (n,)
    eps = x[:, None] * f[None, :]
    live = eps > 1.0e-30
    lg = torch.where(live, torch.log1p(torch.where(live, eps, 0.0)), 0.0)
    logp = prod_rest_log + (-nu * 0.5 * lg).sum(1)
    expo = gamw * x / st
    capt = torch.where(expo > 80.0, 0.0, torch.exp(-torch.clamp(expo, max=80.0)))
    pm = wts * wts * torch.exp(x) * torch.exp(logp) * capt  # (M,)
    a2 = np.abs(v) ** 2  # a2[c, alpha] = |U_alpha c|^2
    winc = torch.as_tensor(a2[inc, :].sum(0), dtype=DTYPE)  # (n_alpha,)
    den = 1.0 + x[:, None] * f[None, :]  # (M, n)
    hm = (winc * pt / den).sum(1)  # (M,)
    # Y_ab = p_a p_b W_ab * st ... W_ab = sum_m Pm (1 + 2 d_ab / nu_a) / (den_a den_b)
    wmat = torch.einsum("m,ma,mb->ab", pm, 1.0 / den, 1.0 / den)
    if use_wfc:
        wmat = wmat + torch.diag((pm[:, None] * (2.0 / nu)[None, :] / den**2).sum(0))
    y = (pt[:, None] * pt[None, :] * wmat).numpy()  # (n_alpha, n_alpha) real symmetric
    ydiag = np.diag(y).copy()
    # first term: sum_a sum_{alpha beta} A_alpha a A_beta b Y_alpha beta (alpha = beta once):
    # t1[b] = sum_beta |U_beta b|^2 sum_alpha Y_beta alpha w_alpha  (Y symmetric)
    t1 = a2 @ (y @ winc.numpy())
    # second term: sum_a [ R^ab^T Y conj(R^ab) - sum_alpha |R_alpha|^2 Y_alpha alpha ], R_alpha = U*_alpha a U_alpha b
    # U_alpha c = conj(v[c, alpha]) -> R_alpha = v[a, alpha] conj(v[b, alpha])
    t2 = np.zeros(v.shape[0])
    for a in inc:
        rab = v[a, :][None, :] * v.conj()  # (n_cells, n_alpha): row b
        q = np.real(np.einsum("ba,ac,bc->b", rab, y, rab.conj()))
        q -= (np.abs(rab) ** 2 * ydiag[None, :]).sum(1)
        t2 += q
    sig = torch.as_tensor(t1 + t2, dtype=DTYPE)
    return pm, hm, sig


__all__ = ["ENV", "STATS", "enabled", "cc_blocks", "attach", "coupled_set", "eigen", "ew_populations", "level_map"]
