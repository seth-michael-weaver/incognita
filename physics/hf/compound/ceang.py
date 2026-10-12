"""CEANG (Incognita extension; an OUTPUT, no effect on any existing number): the Hauser-Feshbach channel-pair weights of the
target's binary compound decay into its OWN discrete levels (compound elastic at Ltarget and compound inelastic to the
lowest levels), exactly as comptarget.f90 / `target._case` weights them, so the angular builder can distribute each level's
compound cross section in angle with the per-(J, pi) denominator and the Moldauer width-fluctuation factor instead of a
J-independent constant (angular.compound_elastic_legendre, COVANG/ELDA).

For one incident energy, (J2, parity) block, incident channel a = (l, j) and exit channel b = (l', j') to discrete level n
of the target nucleus (type k0):

    M_n[a, b] = CNfactor (2J+1) / denomhf(J, pi) * T_a * T_b(n) * W(a, b)
    W(a, b)   = sum_m P_m / ((1 + x_m f_a)(1 + x_m f_b))   [+ E_a if n = Ltarget and b = a]   (Moldauer, wmode 1)
              = 1                                                                              (no WFC: Einc > ewfc)

with P_m, f, E_a from wfc.moldauer_product / moldauer_sums (their incident-summed G_b = sum_a T_a W(a, b) is the same
number), and the exit channels/weights from prepare.exit_channel_sums. sum_ab M_n equals the engine's population of level
n (n = Ltarget: compound elastic). Only wmode 0/1 (the product's) are supported; HRTW/GOE raise.

record(...) is called from engine_c.cases / engine (one call per incident energy) when INCOGNITA_CEANG is set; it rebuilds
the CompoundInputs with chain.compound_inputs if the C front was used (the C kernel exports no per-pair numbers; the Python
reference is the C path's tested twin) and keeps, per energy, the pair matrices of levels 0..NLEV_MAX. Nothing returned by
the engine changes.

TALYS: comptarget.f90:1 (comptarget), moldauer.f90:1, molprepare.f90:1
Test: tests/hf/test_ceang.py
"""

from __future__ import annotations

import os

import numpy as np
import torch

from physics.hf.core.tensors import DTYPE

ENV = "INCOGNITA_CEANG"
NLEV_MAX = 10
RECORD: list[dict] = []


def mode() -> str:
    v = os.environ.get(ENV, "").strip().lower()
    return "" if v in ("", "0", "n", "no", "off") else v


def enabled() -> bool:
    return mode() != ""


def pair_blocks(inp, nlev: int = NLEV_MAX, device=None) -> dict:
    """Per (J2, parity): incident channels, and for every target-nucleus discrete level n <= min(nlev, Nlast) the exit
    channels (l', 2j') and the pair matrix M_n (mb). Returns {"blocks": [...], "sums": {n: sum M_n}, "two_i": [...]}."""
    from physics.hf.compound import wfc
    from physics.hf.compound.prepare import exit_channel_sums, incident_channels
    from physics.hf.compound.target import NUMHILL, _exact_incident_channel

    inp = _exact_incident_channel(inp)
    k0, lt = inp.k0, inp.ltarget
    r0 = inp.residuals[k0]
    use_wfc = inp.flagwidth and inp.wmode >= 1
    if use_wfc and inp.wmode != 1:
        raise NotImplementedError("CEANG: only Moldauer (wmode 1) width fluctuations")
    nmax = min(nlev, int(r0.maxex))
    x, wts = wfc.gauss_laguerre(device)
    cn = torch.as_tensor(inp.cnfactor_mb, dtype=DTYPE, device=device)
    spin2 = r0.spin2
    out, sums = [], {n: 0.0 for n in range(nmax + 1)}
    if float(cn) == 0.0:
        return {"blocks": out, "sums": sums, "nmax": nmax}
    for parity in (-1, 1):
        for J2 in range(inp.j2beg, inp.j2end + 1, 2):
            s = exit_channel_sums(inp, J2, parity, device)
            st = s["denom"]
            if float(st) == 0.0:
                continue
            chans, tinc_np = incident_channels(inp, J2, parity)
            if not chans:
                continue
            tinc = torch.as_tensor(tinc_np, dtype=DTYPE, device=device)
            blocks = s["blocks"]
            b0 = blocks[k0]
            if use_wfc:
                nu_inc = wfc.degrees_of_freedom(tinc, st, inp.wfcfactor)
                t_list, r_list = [], []
                for t, b in blocks.items():
                    if t == 0:
                        continue
                    tt = torch.where(b.t > 1.0e-30, b.t, 0.0)
                    t_list.append(tt.reshape(-1))
                    r_list.append(b.weight.sum((1, 2)).reshape(-1))
                if inp.flagfission and inp.nfisbar != 0:
                    ta = torch.as_tensor(inp.tfisA.get((J2, parity), [0.0] * (NUMHILL + 1)), dtype=DTYPE, device=device)
                    ra = torch.as_tensor(inp.rhofisA.get((J2, parity), [0.0] * (NUMHILL + 1)), dtype=DTYPE, device=device)
                    ratio_h = torch.where(ta[0] > 0, ta[1:] / torch.where(ta[0] > 0, ta[0], 1.0), 0.0)
                    tfh = ratio_h * s["fiswidth"]
                    rho_h = torch.clamp(ra[1:], min=1.0)
                    t_list.append(torch.where(tfh > 1.0e-30, tfh / rho_h, 0.0))
                    r_list.append(rho_h)
                t_exit, r_exit = torch.cat(t_list), torch.cat(r_list)
                nu_exit = wfc.degrees_of_freedom(t_exit, st, inp.wfcfactor)
                prod = wfc.moldauer_product(x, wts, st, t_exit, r_exit, nu_exit, s["gamwidth"])
                fa = 2.0 * tinc / (st * nu_inc)
                da = 1.0 + x[:, None] * fa[None, :]  # (M, A)
                _, _, ea = wfc.moldauer_sums(x, prod, st, tinc, nu_inc, tinc[:1], nu_inc[:1])
            pref = cn * (J2 + 1.0) / st
            blk = {"J2": J2, "parity": parity, "l_in": [c[0] for c in chans],
                   "j2_in": [2 * c[0] + c[1] * spin2 for c in chans], "t_in": tinc.numpy().copy(), "denom": float(st),
                   "levels": {}}
            L = b0.t.shape[1]
            for n in range(nmax + 1):
                w = b0.weight[n]  # (Jx, 2, L, 3)
                if not bool((w > 0).any()):
                    continue
                idx = torch.nonzero(w > 0)
                ex_l, ex_j2, tb, wb, ir2 = [], [], [], [], []
                for (ir, pp, lp, ud) in idx.tolist():
                    ex_l.append(lp)
                    ex_j2.append(2 * lp + (ud - 1) * spin2)
                    tb.append(float(b0.t[n, lp, ud]))
                    wb.append(float(w[ir, pp, lp, ud]))
                    ir2.append(ir)
                tb_t = torch.tensor(tb, dtype=DTYPE, device=device)
                wb_t = torch.tensor(wb, dtype=DTYPE, device=device)
                if use_wfc:
                    tt = torch.where(tb_t > 1.0e-30, tb_t, 0.0)
                    nu_b = wfc.degrees_of_freedom(tt, st, inp.wfcfactor)
                    fb = 2.0 * tt / (st * nu_b)
                    db = 1.0 + x[:, None] * fb[None, :]  # (M, B)
                    W = torch.einsum("m,ma,mb->ab", prod, 1.0 / da, 1.0 / db)
                    teff = tt
                else:
                    W = torch.ones((len(chans), len(tb)), dtype=DTYPE, device=device)
                    teff = tb_t
                M = pref * tinc[:, None] * (wb_t * teff)[None, :] * W
                if use_wfc and n == lt:
                    # elastic diagonal (ielas = 1): exit (l', j') identical to incident (l, j) at Ltarget
                    for ia, (l, ud) in enumerate(chans):
                        if l >= L:
                            continue
                        for ib in range(len(tb)):
                            if ex_l[ib] == l and ex_j2[ib] == 2 * l + ud * spin2:
                                M[ia, ib] = M[ia, ib] + pref * wb_t[ib] * b0.t[n, l, ud + 1] * tinc[ia] * ea[ia]
                Mn = M.numpy().copy()
                # diagnostic: the same pair weights without width fluctuations (W = 1, per-(J, pi) denominator kept)
                Mhf = (pref * tinc[:, None] * (wb_t * tb_t)[None, :]).numpy().copy()
                sums[n] += float(Mn.sum())
                blk["levels"][n] = {"l_out": ex_l, "j2_out": ex_j2, "two_ir": ir2, "M": Mn, "M_nowfc": Mhf, "t_out": np.asarray(tb)}
            out.append(blk)
    return {"blocks": out, "sums": sums, "nmax": nmax}


def record(cas, st, binp, cinp, etot, a_e, fkw, ci, pop) -> None:
    """Keep the pair blocks of one incident energy (output only). `ci` is the Python CompoundInputs when the engine used
    it, else None (C front): then it is rebuilt here with chain.compound_inputs. `pop` = the engine's BinaryPopulation."""
    if not enabled():
        return
    from physics.hf.compound.chain import compound_inputs

    try:
        if ci is None or not hasattr(ci, "residuals"):
            ci = compound_inputs(cas, st, binp, cinp, etot, a_e, **fkw)
        with torch.inference_mode():
            got = pair_blocks(ci)
        k0, lt = int(binp.k0), int(binp.ltarget)
        p = pop.pop_mb[0]
        eng = {n: float(p[k0, n].sum()) for n in range(got["nmax"] + 1) if n < p.shape[1]}
        RECORD.append({"e_inc_mev": float(binp.e_inc_mev), "k0": k0, "ltarget": lt, "targetspin2": int(binp.targetspin2),
                       "target_parity": int(binp.target_parity), "engine_pop": eng, "engine_ce": float(pop.xs_comp_el_mb[0]),
                       "flagwidth": bool(ci.flagwidth), **got})
    except Exception as exc:  # an output: never break the run
        RECORD.append({"e_inc_mev": float(binp.e_inc_mev), "error": f"{type(exc).__name__}: {exc}"})


def _side(J2: int, l: int, j2: int, two_i: int, L: int) -> float:
    """(2j+1)(2l+1) <l 0 l 0 | L 0> W(J j J j; I L) W(j j l l; L 1/2): one side of TALYS's Ablatt (comptarget.f90:667-686)."""
    from physics.hf.ecis.angular import cg2, racah2

    return ((j2 + 1) * (2 * l + 1) * cg2(2 * l, 0, 2 * l, 0, 2 * L, 0) * racah2(J2, j2, J2, j2, two_i, 2 * L)
            * racah2(j2, j2, 2 * l, 2 * l, 2 * L, 1))


def legendre(rec: dict, n: int, two_i0: int, two_in: int, lmax_out: int, key: str = "M") -> np.ndarray:
    """TALYS cleg(type=k0, nexout=n, L), L = 0..lmax_out (odd L = 0), from the recorded pair matrices of one energy:
    cleg(L) = sum_{J pi} sum_{a b} phase angfac clin ra1in ra2in clout ra1out ra2out M_n[a, b] / (2L+1),
    phase = (-1)^|I_n - I_0| (comptarget.f90:676). f(mu) = sum (2L+1) cleg_L P_L; 4 pi cleg_0 = sum M_n."""
    from functools import lru_cache

    side = lru_cache(maxsize=None)(_side)
    out = np.zeros(lmax_out + 1)
    phase = -1.0 if (abs(two_in - two_i0) // 2) % 2 else 1.0
    for blk in rec["blocks"]:
        lv = blk["levels"].get(n)
        if lv is None:
            continue
        J2 = blk["J2"]
        M = lv[key] if key != "M_covang" else (J2 + 1) * np.outer(blk["t_in"], lv["t_out"])
        for L in range(0, lmax_out + 1, 2):
            a_in = np.array([side(J2, l, j2, two_i0, L) for l, j2 in zip(blk["l_in"], blk["j2_in"])])
            if not a_in.any():
                continue
            a_out = np.array([side(J2, l, j2, two_in, L) for l, j2 in zip(lv["l_out"], lv["j2_out"])])
            out[L] += phase * (J2 + 1) / (4 * np.pi) * float(a_in @ M @ a_out) / (2 * L + 1)
    return out


__all__ = ["ENV", "RECORD", "enabled", "legendre", "mode", "pair_blocks", "record"]
