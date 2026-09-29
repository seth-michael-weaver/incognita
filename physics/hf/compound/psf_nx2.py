"""NATIVEX2: the photon transmission rows of the decay widths and of densprepare, from the strength
function evaluated in C (`native/nx2_psf.c`).

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: NATIVEX2 (the speed work; no physics of its own). Acceptance test: `tests/hf/test_nx2.py`
(against `psf_fast.fstrength_np`) and the G-NATIVEX2 closeness gate.

TALYS routines this evaluates:
    fstrength.f90:1 (fstrength)      -- as `psf_fast.fstrength_np` covers it
    densprepare.f90:1 (densprepare)  -- Tgam = 2 pi Egamma^(2l+1) fnorm f_XL(Efs, Egamma)

`psf_fast` spends its time in ~40 numpy calls per (l, irad) per call, four calls per cascade
nucleus per incident energy; the kernel does the same arithmetic point by point. The parameter set
is packed once per `GammaParameters` object. Covered: whatever `psf_fast._supported` accepts;
anything else (or no build, `HF_NX2_PSF=0`) returns None and the caller keeps `psf_fast`.
"""

from __future__ import annotations

import numpy as np

from physics.hf.native import nx2

_PACKS: dict = {}


def _f(x) -> float:
    return float(x.detach()) if hasattr(x, "detach") else float(x)


def _pack(gp):
    """(ip, dp, par, etab, ftab, log10 ftab, tq) for one parameter set, cached by identity; None if
    the set is outside `psf_fast`'s coverage."""
    got = _PACKS.get(id(gp))
    if got is not None and got[0] is gp:
        return got[1]
    from physics.hf.compound.psf_fast import _supported
    from physics.hf.gamma.parameters import NUMGAMQRPA, PI2H2C2, table_arrays

    pack = None
    if _supported(gp):
        L = gp.gammax + 1
        par = np.zeros(16 * 2 * L)
        for irad in (0, 1):
            for l in range(1, L):  # noqa: E741
                q = 16 * (irad * L + l)
                par[q] = gp.ngr[irad][l]
                for i in (1, 2):
                    if i <= gp.ngr[irad][l]:
                        par[q + 3 * i - 2: q + 3 * i + 1] = (
                            _f(gp.sgr_mb[irad, l, i]), _f(gp.egr_mev[irad, l, i]),
                            _f(gp.ggr_mev[irad, l, i]))
                    par[q + 3 * i + 4: q + 3 * i + 7] = (
                        _f(gp.tpr_mb[irad, l, i]), _f(gp.epr_mev[irad, l, i]),
                        _f(gp.gpr_mev[irad, l, i]))
                if gp.flagupbend:
                    par[q + 13: q + 16] = (_f(gp.upbend[irad, l, 1]), _f(gp.upbend[irad, l, 2]),
                                           _f(gp.upbend[irad, l, 3]))
        qrpa = gp.qrpaexist(1, 1)
        if qrpa:
            e_tab, f_tab = table_arrays(gp, 1, 1)
            etab = np.ascontiguousarray(e_tab.detach().numpy(), dtype=np.float64)
            ftab = np.ascontiguousarray(f_tab.detach().numpy(), dtype=np.float64)
            if ftab.ndim == 1:
                ftab = ftab[:, None].copy()
        else:
            etab = np.zeros(NUMGAMQRPA + 2)
            ftab = np.zeros((NUMGAMQRPA + 2, 1))
        n_t = gp.n_tqrpa if qrpa else 1
        tq = (np.ascontiguousarray(gp.tqrpa_mev.detach().numpy(), dtype=np.float64)
              if gp.tqrpa_mev is not None else np.zeros(1))
        if n_t > 1 and tq.size < n_t:
            pack = None
        else:
            ip = np.array([L, int(qrpa), int(bool(gp.flagupbend)), gp.strengthM1, gp.zix + gp.nix,
                           n_t, etab.size - 1, NUMGAMQRPA, ftab.shape[1]], dtype=np.int64)
            dp = np.array([_f(gp.S_k0_mev), _f(gp.delta_mev), _f(gp.alev_per_mev), _f(gp.beta2),
                           PI2H2C2])
            with np.errstate(divide="ignore", invalid="ignore"):
                lftab = np.where(ftab > 0.0, np.log10(np.where(ftab > 0.0, ftab, 1.0)), 0.0)
            pack = (ip, dp, par, etab, ftab, np.ascontiguousarray(lftab), tq)
    if len(_PACKS) > 512:
        _PACKS.clear()
    _PACKS[id(gp)] = (gp, pack)
    return pack


def _args():
    return [nx2.P] * 7


def photon_rows(gp, gammax: int, exinc: np.ndarray, ex0: np.ndarray, nexmax0: np.ndarray, n: int,
                s_n: float, twopi: float, fn1: float):
    """`widths_native.NativeWidths._photon`'s tg[b, row, l, irad], or None (use `psf_fast`).

    TALYS: fstrength.f90:1 (fstrength), densprepare.f90:1 (densprepare)
    Test: tests/hf/test_nx2.py
    """
    fn = nx2.kernel("nx2_psf_photon", _args() + [nx2.I64, nx2.P, nx2.I64, nx2.P, nx2.P, nx2.DBL,
                                                 nx2.DBL, nx2.P], lever="psf")
    if fn is None or gp is None or gp.gammax != gammax:
        return None
    pack = _pack(gp)
    if pack is None:
        return None
    ip, dp, par, etab, ftab, lftab, tq = pack
    m = exinc.size
    exinc = np.ascontiguousarray(exinc, dtype=np.float64)
    ex0 = np.ascontiguousarray(ex0[:n], dtype=np.float64)
    nexmax0 = np.ascontiguousarray(nexmax0, dtype=np.int64)
    tg = np.empty((m, n, gammax + 1, 2))
    fn(nx2.ptr(ip), nx2.ptr(dp), nx2.ptr(par), nx2.ptr(etab), nx2.ptr(ftab), nx2.ptr(lftab),
       nx2.ptr(tq), m, nx2.ptr(exinc), n, nx2.ptr(ex0), nx2.ptr(nexmax0), float(s_n),
       twopi * fn1, nx2.ptr(tg))
    return tg


def tgam_points(gp, gammax: int, efs, eg: np.ndarray, twopi: float, fn1: float):
    """(len(eg), gammax+1, 2) Tgam at each Egamma > 0 (`prepare._tgam_rows`), or None.

    TALYS: fstrength.f90:1 (fstrength), densprepare.f90:1 (densprepare)
    Test: tests/hf/test_nx2.py
    """
    fn = nx2.kernel("nx2_psf_points", _args() + [nx2.I64, nx2.P, nx2.P, nx2.DBL, nx2.P],
                    lever="psf")
    if fn is None or gp is None or gp.gammax != gammax:
        return None
    pack = _pack(gp)
    if pack is None:
        return None
    ip, dp, par, etab, ftab, lftab, tq = pack
    eg = np.ascontiguousarray(eg, dtype=np.float64)
    efs_a = np.ascontiguousarray(np.broadcast_to(np.asarray(efs, dtype=np.float64), eg.shape))
    out = np.zeros((eg.size, gammax + 1, 2))
    fn(nx2.ptr(ip), nx2.ptr(dp), nx2.ptr(par), nx2.ptr(etab), nx2.ptr(ftab), nx2.ptr(lftab),
       nx2.ptr(tq), eg.size, nx2.ptr(efs_a), nx2.ptr(eg), twopi * fn1, nx2.ptr(out))
    return out
