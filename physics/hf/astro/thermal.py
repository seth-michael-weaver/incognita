"""KWCOV B9: TALYS's thermalised target (`astro y`, `astrogs n`) inside the compound-nucleus step.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

With `astro y` and `astrogs n` TALYS adds, at every incident energy, the compound nucleus formed from every excited
target state below E_cm (discrete levels and continuum bins of the target as a residual of the neutron channel,
weighted with rho0, its own exit transmission Tjlnex at E_cm - E_mu) to the populations, the binary cross sections
and the residual production of the ordinary ground-state run, with the ground state's CNfactor. Folded with
exp(-E/kT) on the ground-state energy axis and divided by the partition function, that is the stellar rate
(a detailed-balance identity: (2J_mu+1) E' sigma_mu(E') = (2I_0+1) E [CNfactor sum (2J+1) T_mu ...]).

Two branches, as TALYS has them:
* width fluctuations on (Einc <= ewfc): astrotarget.f90 + astroprepare.f90 -- per target state (nexastro, J, pi)
  one LUMPED incident channel (rho = number of open (l, j) channels times rho0, T = their mean) and one lumped exit
  channel per (type, nexout, Ir, P'); Moldauer W between them (molprepare / moldauer on that list); the "elastic"
  exit (the state itself) gets (W_el + (rho - 1) W_inel) / rho, and its sumIPE adds `suminl` WITHOUT the
  CNfactor (2J+1) (astrotarget.f90:265, kept);
* width fluctuations off: compprepare.f90:377-384 adds sum rho0 T of every excited target cell to the incident
  `feed` (only for J2 <= J2maxastro), comptarget.f90:644/718 subtracts the self-return term
  CNfactor (2J+1) enumhf^2 / denomhf from sumIPE of every type-k0 exit (the target's ground state too).
* comptarget.f90:800-804: after the first energy that ran with width fluctuations and has more than 3 target bins
  open, ewfc = Einc -- every later energy runs WITHOUT width fluctuations, the ground-state part included.
  `Cascade.astro_ewfc_mev` carries that (None = never set, the default).

Not ported (refused): a fissile target (astrotarget.f90:68 calls tfission with the TARGET level index as the
compound-nucleus bin; the port does not reproduce that), widthmode 2/3 (HRTW / GOE on the lumped list).

TALYS routines ported here (file:line of the subroutine statement):
    astrotarget.f90:1 (astrotarget)
    astroprepare.f90:1 (astroprepare)
    compprepare.f90:1 (compprepare)    lines 300-303, 377-384 (astro feed)
    comptarget.f90:1 (comptarget)      lines 554, 644, 718 (sumIPas), 800-804 (astrotarget call, ewfc)
    compnorm.f90:1 (compnorm)          lines 97-98 (J2end = 2 numJ)
Task: T10 (physics/hf/CONTRACT.md section 7; KWCOV batch B9). Acceptance test: KWCOV-B9 (tests/hf/test_kwcov_b9.py).
"""
from __future__ import annotations

import numpy as np
import torch

from physics.hf.core.tensors import DTYPE

NUMJ = 40  # A0_talys_mod.f90:68
LOG: list[dict] = []  # per incident energy of the current run (mode, states, feed, sumIPas, dxsb); run_deck clears it


def active(options) -> bool:
    """`astro y` with `astrogs n` (the thermalised target).

    TALYS: comptarget.f90:1 (comptarget) line 800, `flagastro .and. .not. flagastrogs`
    Test: tests/hf/test_kwcov_b9.py
    """
    return bool(getattr(options, "flagastro", False)) and not bool(getattr(options, "flagastrogs", False))


def check(options) -> None:
    """Refuse what this port of the thermalised target does not cover.

    TALYS: (none -- a port guard)
    Test: tests/hf/test_kwcov_b9.py
    """
    if not active(options):
        return
    if getattr(options, "flagfission", False):
        raise NotImplementedError(
            "not ported: astro y with astrogs n on a fissile target (astrotarget.f90:68 calls tfission with the "
            "target level index as the compound-nucleus bin; use astrogs y)")
    if int(getattr(options, "wmode", 1)) not in (0, 1):
        raise NotImplementedError("not ported: astro y with astrogs n and widthmode 2/3 (HRTW / GOE on "
                                  "astroprepare's lumped channel list); use widthmode 1 or astrogs y")


def _enumhf(b) -> torch.Tensor:
    """(Nex, Ir, 2) sum over (l', j' | irad) of rho0 T: compprepare's enumhf of one exit block."""
    return (b.weight * b.t[:, None, None]).sum((3, 4))


def _count(b) -> torch.Tensor:
    """(Nex, Ir, 2) sum of rho0 over the channels with T > 0: astroprepare's Tastroout(0, ...)."""
    return (b.weight * (b.t[:, None, None] > 0).to(DTYPE)).sum((3, 4))


def addon(ci, xseps_mb: float, transeps: float, nexmax: int) -> dict:
    """Thermalised-target additions at one incident energy: dpop (7, nexmax, NUMJ+1, 2) to add to the compound
    population, dxsb (7,) to add to xsbinary / xspopnuc (TALYS's sumIPE), and diagnostics.

    TALYS: astrotarget.f90:1, astroprepare.f90:1, compprepare.f90:377-384, comptarget.f90:644,718,800
    Test: tests/hf/test_kwcov_b9.py
    """
    from physics.hf.compound.prepare import exit_channel_sums, incident_channels

    k0, lt = int(ci.k0), int(ci.ltarget)
    r = ci.residuals[k0]
    dpop = torch.zeros((7, nexmax, NUMJ + 1, 2), dtype=DTYPE)
    dxsb = np.zeros(7)
    info = {"mode": "wfc" if ci.flagwidth else "hf", "states": 0, "feed": 0.0, "sumipas": 0.0}
    if int(r.maxex) < 1 or r.tjl is None:
        return dict(dpop=dpop, dxsb=dxsb, info=info)
    cn = float(ci.cnfactor_mb)
    cache: dict = {}

    def sums(J2, parity):
        key = (J2, parity)
        if key not in cache:
            s = exit_channel_sums(ci, J2, parity)
            d = float(s["denom"])
            cache[key] = None if d == 0.0 else dict(
                denom=d, gam=s["gamwidth"], en={t: _enumhf(b) for t, b in s["blocks"].items()},
                cnt={t: _count(b) for t, b in s["blocks"].items()})
        return cache[key]

    if not ci.flagwidth:
        _hf(ci, r, k0, lt, cn, xseps_mb, sums, incident_channels, dpop, dxsb, info)
    else:
        _wfc(ci, r, k0, lt, cn, transeps, sums, dpop, dxsb, info)
    return dict(dpop=dpop, dxsb=dxsb, info=info)


def _hf(ci, r, k0, lt, cn, xseps, sums, incident_channels, dpop, dxsb, info) -> None:
    """No width fluctuations: compprepare.f90:377-384 feed, comptarget.f90:644/718 sumIPas (J2end = 2 numJ)."""
    nexk = int(r.maxex) + 1
    lmaxhf = np.asarray(r.lmaxhf[:nexk], dtype=np.int64)
    ir = np.arange(NUMJ + 1)
    # J2maxastro(nexout, Ir) = min(int(2 (lmaxhf + parspin + Ir)), numJ)
    j2max = np.minimum(2 * lmaxhf[:, None] + int(r.parspin2) + 2 * ir[None, :], NUMJ)
    notlt = torch.ones(nexk, dtype=DTYPE)
    if 0 <= lt < nexk:
        notlt[lt] = 0.0
    # J2end = 2 numJ (compnorm.f90:97); above max(numJ, the ground state's J2end) both feeds are 0 and the
    # sumIPas condition (sumIP - sumIPas > xseps with sumIP = 0) is false, so the loop stops there
    for parity in (-1, 1):
        for J2 in range(int(ci.j2beg), max(NUMJ, int(ci.j2end)) + 1, 2):
            s = sums(J2, parity)
            if s is None:
                continue
            en0 = s["en"][k0][:nexk]
            ok = torch.as_tensor(J2 <= j2max, dtype=DTYPE)[:, :, None]
            feed_a = float((en0 * ok * notlt[:, None, None]).sum())
            _, tinc = incident_channels(ci, J2, parity)
            feed_g = float(np.sum(np.asarray(tinc, dtype=float))) if len(tinc) else 0.0
            pref = cn * (J2 + 1.0) / s["denom"]
            if feed_a > 0.0:
                info["feed"] += feed_a
                for t, en in s["en"].items():
                    n = min(en.shape[0], dpop.shape[1])
                    add = pref * feed_a * en[:n]
                    dpop[t, :n] += add
                    tot = add.sum((1, 2))
                    if t == k0 and 0 <= lt < n:
                        tot = tot.clone()
                        tot[lt] = 0.0  # `elastic` (k0, Ltarget) is never in sumIPE
                    dxsb[t] += float(tot.sum())
            # sumIPas: subtracted wherever sumIP - sumIPas > xseps (every nexout of type k0, Ltarget too)
            sip = pref * (feed_g + feed_a) * en0.sum((1, 2))
            sas = pref * (en0 * en0).sum((1, 2))
            cond = (sip - sas) > xseps
            sub = float(sas[cond].sum())
            dxsb[k0] -= sub
            info["sumipas"] += sub


def _wfc(ci, r, k0, lt, cn, transeps, sums, dpop, dxsb, info) -> None:
    """Width fluctuations on: astrotarget.f90 with astroprepare.f90's lumped channels (Moldauer)."""
    from physics.hf.compound import wfc

    nexk = int(r.maxex) + 1
    NL = int(r.nlast)
    x, wts = wfc.gauss_laguerre()
    wfcf = int(ci.wfcfactor)
    lmaxinc = int(ci.lmaxinc)
    s2, sp2 = int(r.parspin2), int(r.spin2)
    tjl = np.asarray(r.tjl, dtype=float)
    # astrotarget is called only when the excited target states carry flux (comptarget.f90:801, Tastrotot)
    tastro = 0.0
    for parity in (-1, 1):
        for J2 in range(int(ci.j2beg), int(ci.j2end) + 1, 2):
            s = sums(J2, parity)
            if s is not None:
                e0 = s["en"][k0][:nexk].clone()
                if 0 <= lt < nexk:
                    e0[lt] = 0.0
                tastro += float(e0.sum())
    info["tastrotot"] = tastro
    if tastro < transeps:
        return
    spin2beg0 = int(r.jdis2[0]) % 2
    suminl = 0.0
    for nexastro in range(0, nexk):
        if nexastro == lt:
            continue
        if nexastro <= NL:
            states = [(int(r.parlev[nexastro]), int(r.jdis2[nexastro]))]
        else:
            states = [(p, s2t) for p in (-1, 1) for s2t in range(spin2beg0, 2 * int(r.maxj[nexastro]) + 1, 2)]
        for ptarget, spin2t in states:
            st_ir = spin2t // 2
            rhoinc = float(r.rho[nexastro, st_ir, 0 if ptarget == -1 else 1]) if st_ir <= NUMJ else 0.0
            if rhoinc == 0.0:
                continue
            j2cnend = min(int(2 * int(r.lmaxhf[nexastro]) + s2 + 2 * st_ir), NUMJ)
            for parity in (-1, 1):
                pardif = abs(ptarget - parity) // 2
                for J2 in range(int(ci.j2beg), j2cnend + 1, 2):
                    s = sums(J2, parity)
                    if s is None:
                        continue
                    # astroprepare: the lumped incident channel of this target state
                    n_inc, t_inc = 0, 0.0
                    for jj2 in range(abs(J2 - spin2t), J2 + spin2t + 1, 2):
                        for l2 in range(abs(jj2 - s2), min(jj2 + s2, 2 * lmaxinc) + 1, 2):
                            l = l2 // 2
                            if l % 2 != pardif:
                                continue
                            ud = (jj2 - l2) // sp2
                            tv = float(tjl[nexastro, l, ud + 1]) if l < tjl.shape[1] else 0.0
                            if tv > 0.0:
                                n_inc += 1
                                t_inc += tv
                    tinc1 = rhoinc * t_inc  # Tastroinc(1): sum rho T
                    if tinc1 < transeps:
                        continue
                    rho_a = rhoinc * n_inc
                    tav_a = tinc1 / rho_a
                    info["states"] += 1
                    st = torch.as_tensor(s["denom"], dtype=DTYPE)
                    # exit list: lumped (type >= 1, nexout, Ir, P') with rho >= 1e-20, in astroprepare's order
                    tl, rl, keys = [], [], []
                    for t in sorted(s["en"]):
                        if t == 0:
                            continue
                        c, e = s["cnt"][t], s["en"][t]
                        m = c >= 1.0e-20
                        idx = m.nonzero()
                        tav = (e[m] / c[m])
                        tl.append(torch.where(tav > 1.0e-30, tav, 0.0))
                        rl.append(c[m])
                        keys.append((t, idx))
                    t_exit = torch.cat(tl) if tl else torch.zeros(0, dtype=DTYPE)
                    r_exit = torch.cat(rl) if rl else torch.zeros(0, dtype=DTYPE)
                    nu_exit = wfc.degrees_of_freedom(t_exit, st, wfcf)
                    prod = wfc.moldauer_product(x, wts, st, t_exit, r_exit, nu_exit, s["gam"])
                    ta = torch.as_tensor(tav_a, dtype=DTYPE)
                    nu_a = wfc.degrees_of_freedom(ta, st, wfcf)
                    fa = 2.0 * ta / (st * nu_a)
                    da = 1.0 + x * fa  # (M,)
                    w_gam = float((prod / da).sum())
                    pref = cn * (J2 + 1.0)
                    # gamma: W(a, gamma) per cell
                    eg = s["en"][0]
                    n = min(eg.shape[0], dpop.shape[1])
                    add = pref * tinc1 * eg[:n] / s["denom"] * w_gam
                    dpop[0, :n] += add
                    dxsb[0] += float(add.sum())
                    off = 0
                    for (t, idx), tt, rr in zip(keys, tl, rl):
                        k = tt.shape[0]
                        nu_b = nu_exit[off: off + k]
                        off += k
                        fb = 2.0 * tt / (st * nu_b)
                        db = 1.0 + x[:, None] * fb[None, :]  # (M, K)
                        w_in = ((prod / da)[:, None] / db).sum(0)  # W(a, b), dab = 0
                        w_el = (((prod * (1.0 + 2.0 / nu_a)) / da)[:, None] / db).sum(0)
                        comp = pref * tinc1 * rr * tt / s["denom"] * w_in  # factor1 = Tinc rho Tout / denom W
                        nexo, iro, po = idx[:, 0], idx[:, 1], idx[:, 2]
                        el = None
                        if t == k0:
                            el = (nexo == nexastro) & (iro == st_ir) & (po == (0 if ptarget == -1 else 1))
                            if bool(el.any()):
                                fel = tinc1 * tt / s["denom"] * (w_el + (rr - 1.0) * w_in)
                                comp = torch.where(el, pref * fel, comp)
                                j = int(el.nonzero()[0, 0])
                                suminl = float((rr[j] - 1.0) * tinc1 * tt[j] / s["denom"] * w_in[j])
                        keep = nexo < dpop.shape[1]
                        dpop[t].index_put_((nexo[keep], iro[keep], po[keep]), comp[keep], accumulate=True)
                        tot = float(comp.sum())
                        if t == k0 and nexastro < nexk:
                            # sumIPE of nexout = nexastro: suminl if the LAST (P', Ir) cell visited is the
                            # target state itself, else the whole sumIP
                            at = nexo == nexastro
                            sip = float(comp[at].sum())
                            if nexastro <= NL:
                                last_el = True
                            else:
                                irend = min(J2 + s2 + 2 * int(r.lmaxhf[nexastro]), 2 * int(r.maxj[nexastro])) // 2
                                last_el = ptarget == 1 and st_ir == irend
                            if last_el:
                                tot = tot - sip + suminl
                        dxsb[t] += tot


def after_energy(cas, ci) -> None:
    """comptarget.f90:802-804: with width fluctuations on and more than 3 target bins open, ewfc = Einc.

    TALYS: comptarget.f90:1 (comptarget) lines 800-804
    Test: tests/hf/test_kwcov_b9.py
    """
    r = ci.residuals.get(int(ci.k0))
    if ci.flagwidth and r is not None and int(r.maxex) + 1 > 3:
        cas.astro_ewfc_mev = float(ci.e_inc_mev)
