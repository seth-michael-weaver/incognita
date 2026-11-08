"""KWCOV B3 (output only): compound Legendre coefficients cleg(type, nexout, L) of the binary compound decay into the
discrete levels of EVERY residual (photons and every particle type), the generalisation of `compound.ceang` (which does
the projectile's own residual, i.e. compound elastic and compound inelastic).

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

For one incident energy, (J2, parity) block, incident channel a = (l, j) and exit channel b = (l', j') of type t to the
discrete level n of its residual, the pair weight is ceang's

    M_n[a, b] = CNfactor (2J+1) / denomhf(J, pi) * T_a * rho * T_b(n) * W(a, b)       (W: Moldauer, 1 without WFC)

and comptarget.f90:665-688 adds  phase angfac clin ra1in ra2in clout ra1out ra2out M / (2L+1)  to cleg(t, n, L), with
ra2 = W(j j l l; L s) taken with the particle's OWN spin s on each side (parspin(k0) incident, parspin(type) exit; photons
s = 0, j' = l') and phase = (-1)^int(|I_n - s_type - I_0 + s_k0| + 0.1).

Every photon exit channel is widthfluc's channel tnum+1 (comptarget.f90:510 tnumo = tnum + 1); molprepare.f90 fills
tav(1..numtjl) only, so tav(tnum+1) = 0 and the photon's Moldauer exit factor is 1 (f_b = 0).
The coefficients are normalised to the engine's own level population by the caller.

TALYS: comptarget.f90:1 (comptarget), angdis.f90:1 (angdis)
Test: tests/hf/test_angout.py
"""

from __future__ import annotations

import math

import numpy as np
import torch

from physics.hf.core.tensors import DTYPE


def pair_blocks(inp, types, nlev: dict, device=None) -> dict:
    """{type: {"blocks": [...], "sums": {n: sum M_n}}} for the exit types `types` (each != k0) and their discrete levels
    n <= nlev[type]; the block layout is ceang.pair_blocks' ("J2", "l_in", "j2_in", "levels": {n: {"l_out", "j2_out", "M"}}).

    TALYS: comptarget.f90:1 (comptarget)
    Test: tests/hf/test_angout.py
    """
    from physics.hf.compound import wfc
    from physics.hf.compound.prepare import exit_channel_sums, incident_channels
    from physics.hf.compound.target import NUMHILL, _exact_incident_channel

    inp = _exact_incident_channel(inp)
    k0 = inp.k0
    types = [t for t in types if t != k0 and t in inp.residuals]
    out = {t: {"blocks": [], "sums": {}} for t in types}
    use_wfc = inp.flagwidth and inp.wmode >= 1
    if (use_wfc and inp.wmode != 1) or not types:
        return out
    x, wts = wfc.gauss_laguerre(device)
    cn = torch.as_tensor(inp.cnfactor_mb, dtype=DTYPE, device=device)
    if float(cn) == 0.0:
        return out
    sp0 = inp.residuals[k0].spin2
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
            if use_wfc:  # ceang.pair_blocks, verbatim
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
                da = 1.0 + x[:, None] * fa[None, :]
            pref = cn * (J2 + 1.0) / st
            l_in = [c[0] for c in chans]
            j2_in = [2 * c[0] + c[1] * sp0 for c in chans]
            for t in types:
                b = blocks.get(t)
                if b is None:
                    continue
                r = inp.residuals[t]
                blk = {"J2": J2, "parity": parity, "l_in": l_in, "j2_in": j2_in, "levels": {}}
                for n in range(min(int(nlev.get(t, -1)), b.weight.shape[0] - 1) + 1):
                    w = b.weight[n]
                    if not bool((w > 0).any()):
                        continue
                    idx = torch.nonzero(w > 0).tolist()
                    if t == 0:  # (Ir, P', L, irad): j' = l' (parspin 0)
                        ex_l = [q[2] for q in idx]
                        ex_j2 = [2 * q[2] for q in idx]
                        tb = [float(b.t[n, q[2], q[3]]) for q in idx]
                    else:  # (Ir, P', L, updown)
                        ex_l = [q[2] for q in idx]
                        ex_j2 = [2 * q[2] + (q[3] - 1) * r.spin2 for q in idx]
                        tb = [float(b.t[n, q[2], q[3]]) for q in idx]
                    wb = torch.tensor([float(w[tuple(q)]) for q in idx], dtype=DTYPE, device=device)
                    tb_t = torch.tensor(tb, dtype=DTYPE, device=device)
                    if use_wfc:
                        tt = torch.where(tb_t > 1.0e-30, tb_t, 0.0)
                        if t == 0:  # every photon exit is widthfluc's channel tnum+1, whose tav molprepare leaves at 0
                            fb = torch.zeros_like(tt)
                        else:
                            nu_b = wfc.degrees_of_freedom(tt, st, inp.wfcfactor)
                            fb = 2.0 * tt / (st * nu_b)
                        db = 1.0 + x[:, None] * fb[None, :]
                        W = torch.einsum("m,ma,mb->ab", prod, 1.0 / da, 1.0 / db)
                        M = pref * tinc[:, None] * (wb * tt)[None, :] * W
                    else:
                        M = pref * tinc[:, None] * (wb * tb_t)[None, :]
                    Mn = M.numpy().copy()
                    out[t]["sums"][n] = out[t]["sums"].get(n, 0.0) + float(Mn.sum())
                    blk["levels"][n] = {"l_out": ex_l, "j2_out": ex_j2, "M": Mn}
                if blk["levels"]:
                    out[t]["blocks"].append(blk)
    return out


_SIDE: dict = {}


def side(J2: int, l: int, j2: int, two_i: int, L: int, two_s: int) -> float:
    """(2j+1)(2l+1) <l 0 l 0 | L 0> W(J j J j; I L) W(j j l l; L s): one side of comptarget's Ablatt with the particle's
    own spin s (ceang._side is the s = 1/2 case).

    TALYS: comptarget.f90:1 (comptarget) lines 667-686
    Test: tests/hf/test_angout.py
    """
    key = (J2, l, j2, two_i, L, two_s)
    v = _SIDE.get(key)
    if v is None:
        from physics.hf.ecis.angular import cg2, racah2

        v = ((j2 + 1) * (2 * l + 1) * cg2(2 * l, 0, 2 * l, 0, 2 * L, 0) * racah2(J2, j2, J2, j2, two_i, 2 * L)
             * racah2(j2, j2, 2 * l, 2 * l, 2 * L, two_s))
        if len(_SIDE) > 400000:
            _SIDE.clear()
        _SIDE[key] = v
    return v


def legendre(rec: dict, n: int, two_i0: int, two_s0: int, two_in: int, two_s: int, lmax: int) -> np.ndarray:
    """cleg(type, n, L), L = 0..lmax (odd L = 0), f(mu) = sum (2L+1) cleg_L P_L, 4 pi cleg_0 = sum M_n.

    TALYS: comptarget.f90:1 (comptarget) lines 665-688
    Test: tests/hf/test_angout.py
    """
    out = np.zeros(lmax + 1)
    iphase = int(abs((two_in - two_s - two_i0 + two_s0) / 2.0) + 0.1)
    phase = -1.0 if iphase % 2 else 1.0
    for blk in rec["blocks"]:
        lv = blk["levels"].get(n)
        if lv is None:
            continue
        J2 = blk["J2"]
        for L in range(0, lmax + 1, 2):
            a_in = np.array([side(J2, l, j2, two_i0, L, two_s0) for l, j2 in zip(blk["l_in"], blk["j2_in"])])  # noqa: B905
            if not a_in.any():
                continue
            a_out = np.array([side(J2, l, j2, two_in, L, two_s) for l, j2 in zip(lv["l_out"], lv["j2_out"])])  # noqa: B905
            out[L] += phase * (J2 + 1) / (4 * math.pi) * float(a_in @ lv["M"] @ a_out) / (2 * L + 1)
    return out


__all__ = ["legendre", "pair_blocks", "side"]
