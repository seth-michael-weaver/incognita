"""LOGTINT (Incognita extension, not TALYS; default OFF): log-T Lagrange interpolation of charged-particle T_lj.

Numerics. densprepare.f90:341-388 puts the emission-grid transmission Tjl(type, nen, updown, l) onto each residual row's
Eout by pol2 = second-order Lagrange in LINEAR T over three grid nodes. Below the Coulomb barrier a charged particle's T is a
tunnelling exponential, T ~ exp(-2 G(E)), and changes x10-x1000 between nodes 0.2-0.5 MeV apart; a parabola through three
points of an exponential lies ABOVE it between the nodes, so pol2 overstates sub-barrier T (ALPHACE diagnostic). The same
Lagrange weights applied to ln T are exact for a pure exponential and second order in the WKB exponent:

    T(Eout) = exp(w1 ln Ta + w2 ln Tb + w3 ln Tc) = Ta^w1 Tb^w2 Tc^w3      (w_i the pol2 weights, sum w_i = 1)

Rule (no parameter): ejectile types 2..6 (p, d, t, h, alpha), every (row, l, j) element whose three node values are all
> 0. Where any node is <= 0 (threshold edges, the hard zeros below ebegin / above eendmax) TALYS's linear pol2 stays.
The nodes, lmax(nen), the transeps cut and Fnorm are unchanged; neutrons (type 1) and photons are untouched.

Keyword `tlog n|c` (c = charged), else the environment INCOGNITA_TLOG. OFF = TALYS, bit-identical.

Reference (G0 only, not an arm): `tlogref y` / INCOGNITA_TLOGREF=y. The run's own inverse OMP solve (`omp_nx2.inverse_kept`,
the routine that fills the emission-grid table) is repeated on an 8x-refined energy grid (REFINE sub-steps per emission-grid
step, same [ebegin, eendmax] keep window), and charged T at every Eout is the log-Lagrange value on that fine table (linear
where a fine node is zero). Only the T values change (nodes for lmax are the coarse ones). Numpy paths only; the C paths
(ce_densprepare, nx_widths, glue) and the GPU refuse it, so a REF run is a Python/numpy run.

Wired (L): Python densprepare (numpy + DIFFPARAM torch), decay_batch._interp_tl (decay_batch, capture_fast_batch,
capture_gpu_setup), decay_fast._particles (numpy widths), C ce_densprepare (engine_decay.c, ce_set_tlog), C nx_widths
(nativex.c, nx_set_tlog). NATIVEX2 glue (nx2_glue_interp): falls back to the numpy body when tlog is on (same arithmetic).
GPU full path (gpu_full_setup): refuses (NotImplementedError).

TLOGIT (Incognita extension, default OFF; keyword `tlogit y`, else INCOGNITA_TLOGIT=y): the same Lagrange weights on the LOGIT
u = ln(T / (1 - T)) instead of ln T. In WKB T = 1 / (1 + exp(2K)), so logit T = -2K is smooth in E on BOTH sides of the barrier
top: = ln T (exact for the tunnelling exponential) where T << 1, = -ln(1 - T) where T -> 1 (the saturating side, where ln-T
Lagrange overshoots, LOGTINT G0). Rule (no parameter): types 2..6, every element whose three nodes satisfy 1e-300 < T < 1 - 1e-12;
else TALYS's linear pol2 (as `tlog c` falls back). Same sites as `tlog c` (kind "l"; C flag 2). `tlogit y` overrides `tlog c`.
"""

from __future__ import annotations

import os

import numpy as np

CHARGED = (2, 3, 4, 5, 6)
REFINE = 8
LOGIT_LO, LOGIT_HI = 1e-300, 1.0 - 1e-12  # TLOGIT: node window where the logit is taken (else linear pol2)


def mode(options) -> str:
    """'l' (TLOGIT: charged ejectiles on logit T), 'c' (charged ejectiles on log T) or 'n' (OFF): the `tlogit` keyword, else
    INCOGNITA_TLOGIT, then the `tlog` keyword, else INCOGNITA_TLOG."""
    if bool(getattr(options, "tlogit", False)) or os.environ.get("INCOGNITA_TLOGIT", "n").strip().lower()[:1] in ("y", "1"):
        return "l"
    v = str(getattr(options, "tlog", "n") or "n").strip().lower()[:1]
    if v == "c":
        return "c"
    e = os.environ.get("INCOGNITA_TLOG", "n").strip().lower()[:1]
    return "c" if e in ("c", "y", "1") else "n"


def ref(options) -> bool:
    """`tlogref y` / INCOGNITA_TLOGREF=y: the 8x-refined reference table (G0 only)."""
    if bool(getattr(options, "tlogref", False)):
        return True
    return os.environ.get("INCOGNITA_TLOGREF", "n").strip().lower()[:1] in ("y", "1")


def kind(v) -> str | bool:
    """The rule a run's trans["tlog"] value names: "l" (logit), "c" (log; also a bare True), else False (OFF)."""
    if v is True or v == "c":
        return "c"
    return "l" if v == "l" else False


def on(trans, t: int) -> str | bool:
    """The rule ("c" log / "l" logit) type t of a run's transmission dict takes, else False."""
    return kind(trans.get("tlog", False)) if t in CHARGED and isinstance(trans, dict) else False


def lagr_logit(w1, w2, w3, ta, tb, tc):
    """TLOGIT: Lagrange on u = ln(T/(1-T)) where all three nodes are in (1e-300, 1-1e-12), TALYS's linear pol2 (same term order)
    elsewhere. numpy. T = e^u/(1+e^u) for u < 0 (exact down to the denormals), 1/(1+e^-u) for u >= 0."""
    lin = w1 * ta + w2 * tb + w3 * tc
    pos = ((ta > LOGIT_LO) & (ta < LOGIT_HI) & (tb > LOGIT_LO) & (tb < LOGIT_HI) & (tc > LOGIT_LO) & (tc < LOGIT_HI))
    if not np.any(pos):
        return lin

    def lg(x):
        x = np.where(pos, x, 0.5)
        return np.log(x) - np.log1p(-x)
    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        u = w1 * lg(ta) + w2 * lg(tb) + w3 * lg(tc)
        eu = np.exp(-np.abs(u))
        t = np.where(u < 0.0, eu / (1.0 + eu), 1.0 / (1.0 + eu))
    return np.where(pos, t, lin)


def lagr_log(w1, w2, w3, ta, tb, tc, kind: str = "c"):
    """Lagrange on ln T where all three nodes are > 0, TALYS's linear pol2 (same term order) elsewhere. numpy.
    kind "l" = TLOGIT (lagr_logit)."""
    if kind == "l":
        return lagr_logit(w1, w2, w3, ta, tb, tc)
    lin = w1 * ta + w2 * tb + w3 * tc
    pos = (ta > 0.0) & (tb > 0.0) & (tc > 0.0)
    if not np.any(pos):
        return lin
    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        lg = np.exp(w1 * np.log(np.where(pos, ta, 1.0)) + w2 * np.log(np.where(pos, tb, 1.0))
                    + w3 * np.log(np.where(pos, tc, 1.0)))
    return np.where(pos, lg, lin)


def lagr_log_torch(w1, w2, w3, ta, tb, tc, kind: str = "c"):
    """DIFFPARAM: the same rule on the graph (gradients flow through both branches' selected values). kind "l" = TLOGIT."""
    import torch

    lin = w1 * ta + w2 * tb + w3 * tc
    if kind == "l":
        pos = ((ta > LOGIT_LO) & (ta < LOGIT_HI) & (tb > LOGIT_LO) & (tb < LOGIT_HI) & (tc > LOGIT_LO) & (tc < LOGIT_HI))
        half = torch.full((), 0.5, dtype=ta.dtype)
        lg = lambda x: torch.logit(torch.where(pos, x, half))  # noqa: E731
        return torch.where(pos, torch.sigmoid(w1 * lg(ta) + w2 * lg(tb) + w3 * lg(tc)), lin)
    pos = (ta > 0.0) & (tb > 0.0) & (tc > 0.0)
    one = torch.ones((), dtype=ta.dtype)
    lg = torch.exp(w1 * torch.log(torch.where(pos, ta, one)) + w2 * torch.log(torch.where(pos, tb, one))
                   + w3 * torch.log(torch.where(pos, tc, one)))
    return torch.where(pos, lg, lin)


# ---------------------------------------------------------------------------------------------- reference (G0 only)

def fine_grid(egrid: np.ndarray, maxen: int, refine: int = REFINE) -> tuple[np.ndarray, np.ndarray]:
    """REFINE sub-steps per emission-grid step over egrid[0..maxen]; returns (efine, coarse index of each fine node's
    left grid point). efine[k * refine] == egrid[k]."""
    eg = np.asarray(egrid[: maxen + 1], dtype=float)
    out, left = [], []
    for k in range(maxen):
        for j in range(refine):
            out.append(eg[k] + (eg[k + 1] - eg[k]) * j / refine)
            left.append(k)
    out.append(eg[maxen]); left.append(maxen)
    return np.asarray(out), np.asarray(left, dtype=np.int64)


def interp_ref(eout: np.ndarray, efine: np.ndarray, tfine: np.ndarray) -> np.ndarray:
    """T at every eout from the fine table (Ef, ...): 3-node Lagrange on the nearest centred fine nodes, in ln T where all
    three are > 0, linear otherwise. eout outside [efine[1], efine[-2]] clamps to the end triples."""
    e = np.asarray(eout, dtype=float)
    nf = efine.shape[0]
    j = np.clip(np.searchsorted(efine, e, side="right") - 1, 0, nf - 1)
    na = np.clip(j - 1, 0, nf - 3)
    nb, nc = na + 1, na + 2
    ea, eb, ec = efine[na], efine[nb], efine[nc]
    sh = (slice(None),) + (None,) * (tfine.ndim - 1)
    w1 = ((e - eb) * (e - ec) / ((ea - eb) * (ea - ec)))[sh]
    w2 = ((e - ea) * (e - ec) / ((eb - ea) * (eb - ec)))[sh]
    w3 = ((e - ea) * (e - eb) / ((ec - ea) * (ec - eb)))[sh]
    return lagr_log(w1, w2, w3, tfine[na], tfine[nb], tfine[nc])


# ---------------------------------------------------------------------------------------------- G0 recorder

HBINS = np.concatenate([[0.0], np.logspace(-12, 3, 1501)])  # |ln(T/T_ref)| histogram edges (0 = exact)
_AGG: dict = {}
_RNG = np.random.default_rng(12345)
NSAMPLE = 4000  # raw rows kept per type and call batch (subsample)


def record(t: int, eout, na, w1, w2, w3, ta, tb, tc, keep, transeps: float, refv=None) -> None:
    """G0 recorder (INCOGNITA_TLOG_REC=<path.npz>, default off). Per type: histograms of |ln(T_lin/T_ref)| and
    |ln(T_log/T_ref)| over every kept (row, l[, j]) element with T_ref > 1e-12 (REF runs), signed sums, and a random
    subsample of raw (Eout, l, lin, log, ref, logit) rows. Without REF (L runs) only |ln(T_lin/T_log)| is histogrammed."""
    if not os.environ.get("INCOGNITA_TLOG_REC"):
        return
    lin = np.asarray(w1 * ta + w2 * tb + w3 * tc, dtype=float)
    lg = np.asarray(lagr_log(w1, w2, w3, ta, tb, tc), dtype=float)
    lgt = np.asarray(lagr_logit(w1, w2, w3, ta, tb, tc), dtype=float)  # TLOGIT column (recorded in every recorder run)
    kp = np.broadcast_to(np.asarray(keep, dtype=bool), lin.shape)
    e = np.broadcast_to(np.asarray(eout, dtype=float).reshape((-1,) + (1,) * (lin.ndim - 1)), lin.shape)
    ll = np.broadcast_to(np.arange(lin.shape[1]).reshape((1, -1) + (1,) * (lin.ndim - 2)), lin.shape)
    ref = np.asarray(refv, dtype=float) if refv is not None else lg
    sel = kp & (ref > 1e-12)
    if not np.any(sel):
        return
    lin, lg, lgt, ref, e, ll = lin[sel], lg[sel], lgt[sel], ref[sel], e[sel], ll[sel]
    a = _AGG.setdefault(int(t), dict(n=0, h_lin=np.zeros(len(HBINS) - 1), h_lg=np.zeros(len(HBINS) - 1),
                                     h_lgt=np.zeros(len(HBINS) - 1), nneg_lin=0, s_lin=0.0, s_lg=0.0, s_lgt=0.0, samp=[]))
    with np.errstate(divide="ignore", invalid="ignore"):
        dlin = np.where(lin > 0, np.log(lin / ref), -np.inf)
        dlg = np.where(lg > 0, np.log(lg / ref), -np.inf)
        dlgt = np.where(lgt > 0, np.log(lgt / ref), -np.inf)
    a["n"] += lin.size
    a["nneg_lin"] += int(np.sum(lin <= 0))
    a["h_lin"] += np.histogram(np.minimum(np.abs(dlin), 999.0), HBINS)[0]
    a["h_lg"] += np.histogram(np.minimum(np.abs(dlg), 999.0), HBINS)[0]
    a["h_lgt"] += np.histogram(np.minimum(np.abs(dlgt), 999.0), HBINS)[0]
    a["s_lin"] += float(np.sum(np.where(np.isfinite(dlin), dlin, 0.0)))
    a["s_lg"] += float(np.sum(np.where(np.isfinite(dlg), dlg, 0.0)))
    a["s_lgt"] += float(np.sum(np.where(np.isfinite(dlgt), dlgt, 0.0)))
    k = min(NSAMPLE, lin.size)
    pick = _RNG.choice(lin.size, k, replace=False) if lin.size > k else np.arange(lin.size)
    a["samp"].append(np.stack([e[pick], ll[pick], lin[pick], lg[pick], ref[pick], lgt[pick]], 1).astype(np.float64))
    if len(a["samp"]) > 64:  # keep memory flat: thin the sample
        x = np.concatenate(a["samp"]); a["samp"] = [x[_RNG.choice(x.shape[0], min(x.shape[0], 64 * NSAMPLE // 4), replace=False)]]


def flush(path: str | None = None) -> None:
    p = path or os.environ.get("INCOGNITA_TLOG_REC")
    if not p or not _AGG:
        return
    out = {"hbins": HBINS}
    for t, a in _AGG.items():
        for k in ("n", "nneg_lin", "s_lin", "s_lg", "s_lgt", "h_lin", "h_lg", "h_lgt"):
            out[f"t{t}_{k}"] = np.asarray(a[k])
        out[f"t{t}_samp"] = np.concatenate(a["samp"]) if a["samp"] else np.zeros((0, 6))
    np.savez_compressed(p, **out)
    _AGG.clear()


def native_arm(trans) -> None:
    """Switch the C kernels' log-T rule on/off for this run (nx_widths, ce_densprepare). REF refuses the C paths."""
    import ctypes

    k = kind(trans.get("tlog", False)) if isinstance(trans, dict) else False
    flag = 2 if k == "l" else 1 if k == "c" else 0  # TLOGIT = 2
    from physics.hf.native import nativex

    nx = nativex.lib()
    if nx is not None and hasattr(nx, "nx_set_tlog"):
        nx.nx_set_tlog.argtypes = [ctypes.c_int64]; nx.nx_set_tlog.restype = None
        nx.nx_set_tlog(flag)
    elif flag and nx is not None:
        raise NotImplementedError("TLOG: libnativex without nx_set_tlog (rebuild the native libraries)")
    from physics.hf import engine_c

    so = engine_c.lib()
    if so is not None and hasattr(so, "ce_set_tlog"):
        so.ce_set_tlog.argtypes = [ctypes.c_int64]; so.ce_set_tlog.restype = None
        so.ce_set_tlog(flag)
    elif flag and so is not None:
        raise NotImplementedError("TLOG: libengdecay without ce_set_tlog (rebuild the native libraries)")


def refuse_ref(trans, where: str) -> None:
    if isinstance(trans, dict) and "tlogref" in trans:
        raise NotImplementedError(f"TLOGREF (G0 reference) is numpy-only; not wired on {where}")
