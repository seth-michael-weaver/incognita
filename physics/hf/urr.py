"""KWCOV B10 (URR): unresolved resonance range parameters and cross sections on TALYS's keywords, OUTPUT ONLY.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md. The fluctuation integrals (gnrl.f) and the NJOY-style
cross sections (csunr2.f90, unfac.f90) are G. Noguere's code inside the TALYS repository, same license.

What it gives: `Results.urr` = urrout.f90's files as {file name: {column: ndarray over rows}}:

    urr.dat                   one block per URR energy: E, l, J, P, D(l), D(l,J), S(l), S(l,J), Gx, Gn, Gg, Gf, Gp, Ga
                              (eV; S in 1e-4), plus `S_n` and `xscaptherm` (the block parameters)
    urr<kind>.lLL             per l <= lurr, rows over the URR energies: `E` and, per J of the run's (l, J) range,
                              `J=<J>:nu` and `J=<J>:<width|spacing|strength>` (NaN where TALYS writes
                              "!!! not calculated" or a row is shorter); kinds: fiswidth (fission targets), gamwidth,
                              comwidth, spacinglj, neuwidth, neustrengthlj, prowidth (Q(n,p) > 0), alpwidth
                              (Q(n,a) > 0), spacingl and neustrengthl (one `spacing` / `strength` column)
    urrtalys.tot              E, xs, elastic, capture, fission [mb] from the Hauser-Feshbach (l <= min(2, lurr)) sums
    urrnjoy.tot, urrratio.tot with `urrnjoy y`: the same from the NJOY formalism (csunr2 + gnrl, potential scattering
                              radius `rprime`, default the R' of the first URR energy) and TALYS:NJOY

Switches: TALYS's own. `urr y` (onset eurr = S_n of the target), `urr <E>` (onset E), `endf y` (sets urr y for
A > 20, input_compoundpar.f90:69), `lurr`, `urrnjoy`, `rprime`. Default: none of them, nothing runs, every Results
array is unchanged. In TALYS too URR is output only: flagurr forces comptarget's full (j, l) loops, which give the
same cross sections as the lumped ones (W = 1 above ewfc).

How (comptarget.f90:501-510 and 721-745, the "advice of Gilles Noguere" blocks): per compound (J, parity) and incident
(l, j) with l <= lurr, the binary cross section into each exit type without compound elastic, sumIPE, and
Turrlj = sumIPE denomhf / (CNfactor (2J+1) Tinc Wab). `Wab` is the width-fluctuation factor of the LAST widthfluc call
before the end of that type's loops (the last exit channel visited, in TALYS's loop order; W(a, gamma) for photons;
the last fission hill with a non-zero ratio), not an average: a TALYS quirk kept as written. Per incident channel the
Moldauer sums are `wfc.moldauer_sums` with a one-hot incident vector (they are linear in it). Then urr.f90:
dtheory(0, 0, Einc) for D(l, J), strengthfunc for S(l, J), urrwidth = D(l, J) T(l, J) / 2 pi, the neutron width
D S 1e-4, the optional NJOY renormalisation loop, and urrout's files. The (l, J) range (lminU..lmaxU, JminU..JmaxU)
grows over the run's energies as TALYS's does (strucinitial resets it once per run).

Not given: `urr` with width fluctuations by HRTW or GOE (widthmode 2 / 3: the per-incident-channel factors of those
models are not separated here; refused), with INCOGNITA_EWFC on a coupled target, or with the KEVCOLD cell options
(refused); energies below `eninclow` (Ninclow > 0: TALYS's first-file rows for them are filled from the current
energy; the port has no Ninclow energies, B10b). The thermal capture cross section in urr.dat is thermalxs.f90's
xscaptherm(-1) (structure/thermal table, else Kopecky's systematics, a deck `xscaptherm` wins).

TALYS routines ported here (file:line of the subroutine statement):
    urr.f90:1 (urr)                    widths, strength functions, NJOY loop, final cross sections
    urrout.f90:1 (urrout)              the files
    csunr2.f90:1 (csunr2)              NJOY cross sections per (l, J)
    unfac.f90:1 (unfac)                penetrability and phase shift
    gnrl.f:1 (gnrl)                    NJOY fluctuation integrals
    strengthfunc.f90:1 (strengthfunc)  (l, j) neutron strength function
    dtheory.f90:1 (dtheory)            D(l) and D(l, J) of the initial compound nucleus at S_n + Einc
    thermalxs.f90:1 (thermalxs)        xscaptherm(-1) only
    comptarget.f90:1 (comptarget)      the URR extraction blocks
Task: T10 (physics/hf/CONTRACT.md section 7; KWCOV batch B10, output only). Acceptance test: KWCOV-B10
(tests/hf/test_kwcov_b10.py, scripts/kwcov/b10_response.py, docs/hf/COVERAGE_PLAN.md).
"""

from __future__ import annotations

import math
from dataclasses import replace

import numpy as np
import torch

from physics.hf.core.tensors import DTYPE

NUMJ = 40
NUML = 60
TWOPI = 2.0 * math.pi

# gnrl.f data: qw(10, 4), qp(10, 4), column-major as the Fortran DATA statements fill them
_QW = np.array([
    1.1120413E-01, 2.3546798E-01, 2.8440987E-01, 2.2419127E-01, .10967668, .030493789, .0042930874, 2.5827047E-04,
    4.9031965E-06, 1.4079206E-08, .033773418, .079932171, .12835937, .17652616, .21347043, .21154965, .13365186,
    .022630659, 1.6313638E-05, 2.745383E-31, 3.3376214E-04, .018506108, .12309946, .29918923, .33431475, .17766657,
    .042695894, 4.0760575E-03, 1.1766115E-04, 5.0989546E-07, 1.7623788E-03, .021517749, .080979849, .18797998,
    .30156335, .29616091, .10775649, 2.5171914E-03, 8.9630388E-10, 0.0], dtype=np.float32).reshape(4, 10).T
_QP = np.array([
    3.0013465E-03, 7.8592886E-02, 4.3282415E-01, 1.3345267, 3.0481846, 5.8263198, 9.9452656, 1.5782128E+01, 23.996824,
    36.216208, 1.3219203E-02, 7.2349624E-02, .19089473, .39528842, .74083443, 1.3498293, 2.5297983, 5.2384894,
    13.821772, 75.647525, 1.0004488E-03, .026197629, .14427472, .44484223, 1.0160615, 1.9421066, 3.3150885, 5.2607092,
    7.9989414, 12.072069, .013219203, .072349624, .19089473, .39528842, .74083443, 1.3498293, 2.5297983, 5.2384894,
    13.821772, 75.647525], dtype=np.float32).reshape(4, 10).T

# urrout.f90 file names per `type` (-1..6) and the l-only files (7, 8)
_LFILE = {-1: ("urrfiswidth", "width"), 0: ("urrgamwidth", "width"), 1: ("urrcomwidth", "width"),
          2: ("urrspacinglj", "spacing"), 3: ("urrneuwidth", "width"), 4: ("urrneustrengthlj", "strength"),
          5: ("urrprowidth", "width"), 6: ("urralpwidth", "width")}

STATE: dict = {}


# ------------------------------------------------------------------------------------------------ switches


def active(options) -> bool:
    """True when the run asks for URR output (`urr y`, `urr <E>`, `endf y` for A > 20; input_compoundpar.f90:68-121).

    TALYS: urr.f90:1 (urr)
    Test: tests/hf/test_kwcov_b10.py
    """
    return bool(getattr(options, "flagurr", False))


def check(options) -> None:
    """checkvalue.f90:760-776 for the URR keywords, and the port's refusals.

    TALYS: urr.f90:1 (urr)
    Test: tests/hf/test_kwcov_b10.py
    """
    lurr = int(getattr(options, "lurr", 2))
    if not 0 <= lurr <= NUML:
        raise ValueError(f"TALYS-error: lurr {lurr} out of range 0-{NUML}")
    if not active(options):
        return
    if int(getattr(options, "k0", 1)) != 1:
        raise ValueError("TALYS-error: URR calculation only possible for incident neutrons")
    if not getattr(options, "flagcomp", True):
        raise ValueError("TALYS-error: URR calculation only possible if compound nucleus model enabled")


def eurr_mev(cas) -> float:
    """The URR onset: `urr <E>`, else S(parZ(k0), parN(k0), k0) = S_n of the target (nuclides.f90:252).

    TALYS: urr.f90:1 (urr)
    Test: tests/hf/test_kwcov_b10.py
    """
    e = float(cas.options.eurr_mev)
    if e != -1.0:
        return e
    return float(cas.ld_of(int(cas.Zt), int(cas.At))[0].S_mev)


def begin_run(cas) -> None:
    """strucinitial.f90:337-370 for the URR arrays: the (l, J) range and the file-existence flags, once per run.

    TALYS: urr.f90:1 (urr)
    Test: tests/hf/test_kwcov_b10.py
    """
    STATE.clear()
    if not active(cas.options):
        return
    check(cas.options)
    rp = _rprime_deck(cas)
    if not 0.0 <= rp <= 10.0:  # checkvalue.f90:883
        raise ValueError(f"TALYS-error: rprime {rp} out of range 0-10")
    STATE.update(lmin=NUML, lmax=0, Jmin=np.full(NUML + 1, NUMJ, dtype=int), Jmax=np.zeros(NUML + 1, dtype=int),
                 exist=set(), files={}, urrdat=[], RprimeU=rp, energies=[], records=[],
                 eurr=eurr_mev(cas), ewarn=[])


def _rprime_deck(cas) -> float:
    p = getattr(cas, "params", None)
    try:
        if p is not None and "rprime" in p:
            return float(np.asarray(p["rprime"].detach() if hasattr(p["rprime"], "detach") else p["rprime"]).ravel()[0])
    except (KeyError, TypeError, ValueError):
        pass
    return 0.0


# ------------------------------------------------------------------------------------------------ comptarget blocks


def _last_visit(w: torch.Tensor, spin2: int, photon: bool):
    """Index (nex, l', ud) of the last exit channel comptarget visits in a type's loops (nexout, P', Ir, j', l'
    ascending; a channel is visited when rho >= 1e-20 and its l' passes the parity/range tests, i.e. weight > 0)."""
    vis = w > 0  # (Nex, Ir, 2, L, 3|2)
    if not bool(vis.any()):
        return None
    idx = vis.nonzero()
    nex, ir, pp, lp, u = (idx[:, k] for k in range(5))
    if photon:
        key = ((nex * 2 + pp) * (NUMJ + 1) + ir) * 1000 + 2 * lp
    else:
        jj = 2 * lp + (u - 1) * spin2
        key = (((nex * 2 + pp) * (NUMJ + 1) + ir) * 1000 + jj) * 1000 + 2 * lp
    k = int(torch.argmax(key))
    return int(nex[k]), int(lp[k]), int(u[k])


def comptarget_lj(ci, lurr: int) -> dict:
    """comptarget.f90:501-510, 721-745: per (l, J) with l <= lurr the URR transmissions Turrlj(type), binary cross
    sections xsbinarylj(type) (compound elastic left out), degrees of freedom nulj, incident Turrljinc and parity
    Purrlj, for one incident energy. `ci` = CompoundInputs after the exact incident channel.

    TALYS: comptarget.f90:1 (comptarget)
    Test: tests/hf/test_kwcov_b10.py
    """
    from physics.hf.compound import wfc
    from physics.hf.compound.prepare import exit_channel_sums, incident_channels

    if getattr(ci, "alphadom", None) is not None or getattr(ci, "cellsel", None) is not None:
        raise NotImplementedError("urr with the KEVCOLD cell options is not ported")
    if getattr(ci, "ew", None) is not None:
        raise NotImplementedError("urr with INCOGNITA_EWFC on a coupled target is not ported")
    use_wfc = bool(ci.flagwidth and ci.wmode >= 1)
    if use_wfc and ci.wmode != 1:
        raise NotImplementedError(f"urr with widthmode {ci.wmode} (HRTW/GOE) is not ported; widthmode 1 or 0 only")
    k0 = int(ci.k0)
    cn = float(ci.cnfactor_mb)
    x, wts = wfc.gauss_laguerre()
    fis_on = bool(ci.flagfission and ci.nfisbar != 0)
    T = {}  # (type, l, J) -> Turrlj
    XS = {}  # (type, l, J) -> xsbinarylj
    NU = {}  # (type, l, J) -> nulj
    TINC, PAR = {}, {}
    rng = []
    W_state = [1.0]  # comptarget.f90:265 Wab = 1, then whatever widthfluc set last
    for parity in (-1, 1):
        for J2 in range(ci.j2beg, ci.j2end + 1, 2):
            s = exit_channel_sums(ci, J2, parity)
            st = s["denom"]
            if float(st) == 0.0:
                continue
            chans, tinc_np = incident_channels(ci, J2, parity)
            tinc = torch.as_tensor(np.asarray(tinc_np, dtype=float), dtype=DTYPE)
            if not chans:
                continue
            J = J2 // 2
            blocks = s["blocks"]
            spin2 = {t: (ci.residuals[t].spin2 if t in ci.residuals else 1) for t in blocks}
            last = {t: _last_visit(b.weight, spin2[t], t == 0) for t, b in blocks.items()}
            ratio_h = th = nu_h = None
            if use_wfc:
                nu_inc = wfc.degrees_of_freedom(tinc, st, ci.wfcfactor)
                t_list, r_list = [], []
                for t, b in blocks.items():
                    if t == 0:
                        continue
                    tt = torch.where(b.t > 1.0e-30, b.t, 0.0)
                    t_list.append(tt.reshape(-1))
                    r_list.append(b.weight.sum((1, 2)).reshape(-1))
                if fis_on:
                    ta = torch.as_tensor(ci.tfisA.get((J2, parity), [0.0] * 21), dtype=DTYPE)
                    ra = torch.as_tensor(ci.rhofisA.get((J2, parity), [0.0] * 21), dtype=DTYPE)
                    ratio_h = torch.where(ta[0] > 0, ta[1:] / torch.where(ta[0] > 0, ta[0], 1.0), 0.0)
                    tfh = ratio_h * s["fiswidth"]
                    rho_h = torch.clamp(ra[1:], min=1.0)
                    th = torch.where(tfh > 1.0e-30, tfh / rho_h, 0.0)
                    t_list.append(th)
                    r_list.append(rho_h)
                    nu_h = wfc.degrees_of_freedom(th, st, ci.wfcfactor)
                t_exit, r_exit = torch.cat(t_list), torch.cat(r_list)
                nu_exit = wfc.degrees_of_freedom(t_exit, st, ci.wfcfactor)
                prod = wfc.moldauer_product(x, wts, st, t_exit, r_exit, nu_exit, s["gamwidth"])
            pref = cn * (J2 + 1.0) / st
            for ia, (l, ud) in enumerate(chans):
                if l > lurr:
                    continue
                ta_ = float(tinc[ia])
                one = torch.zeros_like(tinc)
                one[ia] = tinc[ia]
                if fis_on:
                    tf = s["fiswidth"]
                    if use_wfc:
                        factor1 = 0.0
                        if float(torch.as_tensor(ci.tfisA.get((J2, parity), [0.0])[0])) > 0:
                            gh, _, _ = wfc.moldauer_sums(x, prod, st, one, nu_inc, th, nu_h)
                            live = (ratio_h != 0).nonzero().ravel()
                            factor1 = float((gh * ratio_h).sum() * tf / st)
                            if live.numel():
                                W_state[0] = float(gh[int(live[-1])]) / ta_ if ta_ > 0 else W_state[0]
                    else:
                        factor1 = ta_ * float(tf) / float(st)
                    wab = W_state[0]
                    T[(-1, l, J)] = factor1 * float(st) / (ta_ * wab) if ta_ * wab != 0 else 0.0
                    XS[(-1, l, J)] = XS.get((-1, l, J), 0.0) + cn * (J2 + 1.0) * factor1
                    NU[(-1, l, J)] = 1
                for t in range(7):
                    b = blocks.get(t)
                    sumipe = 0.0
                    if b is not None:
                        if t == 0:
                            if use_wfc:
                                _, gg, _ = wfc.moldauer_sums(x, prod, st, one, nu_inc, b.t[:1, :1, :1],
                                                             torch.ones(1, dtype=DTYPE))
                                gg = float(gg)
                            else:
                                gg = ta_
                            contrib = (b.weight * b.t[:, None, None, :, :]).sum((3, 4)) * gg
                            if use_wfc and last[t] is not None and ta_ > 0:
                                W_state[0] = gg / ta_
                        else:
                            tt = torch.where(b.t > 1.0e-30, b.t, 0.0)
                            if use_wfc:
                                nu_b = wfc.degrees_of_freedom(tt, st, ci.wfcfactor)
                                gb, _, _ = wfc.moldauer_sums(x, prod, st, one, nu_inc, tt, nu_b)
                                if last[t] is not None and ta_ > 0:
                                    n_, lp_, u_ = last[t]
                                    W_state[0] = float(gb[n_, lp_, u_]) / ta_
                            else:
                                gb = ta_
                            contrib = (b.weight * (b.t * gb)[:, None, None, :, :]).sum((3, 4))
                            if t == k0 and 0 <= ci.ltarget < contrib.shape[0]:
                                contrib = contrib.clone()
                                contrib[ci.ltarget] = 0.0  # compound elastic: not in sumIPE
                        sumipe = float(pref * contrib.sum())
                    wab = W_state[0]
                    den = cn * (J2 + 1.0) * ta_ * wab
                    T[(t, l, J)] = sumipe * float(st) / den if den != 0 else 0.0
                    XS[(t, l, J)] = XS.get((t, l, J), 0.0) + sumipe
                    NU[(t, l, J)] = NU.get((t, l, J), 0) + 1 if t == 0 else 1
                TINC[(l, J)] = TINC.get((l, J), 0.0) + ta_
                PAR[(l, J)] = parity
                rng.append((l, J))
    return dict(T=T, XS=XS, NU=NU, TINC=TINC, PAR=PAR, rng=rng)


# ------------------------------------------------------------------------------------------------ urr.f90 helpers


def dtheory_lj(ld, tspin: float, tpar: int, e_mev: float, lmaxinc: int):
    """dtheory.f90 with its D(l, J): returns (Dl (NUML+1,), Dlj {(l, J): eV}) at S + E of the compound nucleus `ld`.

    TALYS: dtheory.f90:1 (dtheory)
    Test: tests/hf/test_kwcov_b10.py
    """
    from physics.hf.density.models import density

    tspin2 = int(2.0 * tspin)
    lmaxdth = max(int(lmaxinc), 5)
    J2b = int(2.0 * (tspin + 0.5)) % 2
    J2e = min(int(2 * (lmaxdth + 0.5 + tspin)), 2 * NUMJ)
    eex = torch.clamp(torch.as_tensor(ld.S_mev, dtype=DTYPE) + float(e_mev), min=0.0)
    cell = {}
    for parity in (-1, 1):
        pardif = abs(int(tpar) - parity) // 2
        for J2 in range(J2b, J2e + 1, 2):
            for jj2 in range(abs(J2 - tspin2), J2 + tspin2 + 1, 2):
                for l2 in range(abs(jj2 - 1), min(jj2 + 1, 2 * lmaxdth) + 1, 2):
                    l = l2 // 2
                    if l % 2 == pardif:
                        cell[(l, J2 // 2)] = (0.5 * J2, parity)
    rho = {}
    for parity in (-1, 1):
        js = sorted({v[0] for v in cell.values() if v[1] == parity})
        if js:
            vals = density(ld, eex, torch.tensor(js, dtype=DTYPE), parity, 0)
            for i, j in enumerate(js):
                rho[(j, parity)] = float(np.asarray(vals[i].detach()).ravel()[0])
    Dlj, Dl = {}, np.zeros(NUML + 1)
    rsum = {}
    for (l, J), key in cell.items():
        r = rho[key]
        Dlj[(l, J)] = float(np.float32(1.0e6 / r)) if r > 0 else 0.0
        rsum[l] = rsum.get(l, 0.0) + r
    for l, r in rsum.items():
        if r >= 1.0e-10:
            Dl[l] = float(np.float32(1.0e6 / r))
    return Dl, Dlj


def strengthfunc(tinc: float, l: int, e_mev: float, wavenum: float, tarmass: float) -> float:
    """(l, j) neutron strength function [1e-4]: Tinc / (2 pi v_l sqrt(Einc)), hard-sphere penetrability, ENDF radius.

    TALYS: strengthfunc.f90:1 (strengthfunc)
    Test: tests/hf/test_kwcov_b10.py
    """
    ac = 1.23 * tarmass ** (1.0 / 3.0) + 0.8
    P = [wavenum * ac]
    shift = [0.0]
    p0 = P[0]
    for i in range(1, l + 1):
        den = P[i - 1] ** 2 + (i - shift[i - 1]) ** 2
        P.append(P[i - 1] * p0 ** 2 / den)
        shift.append((i - shift[i - 1]) * p0 ** 2 / den - i)
    vl = P[l] / (p0 * 10.0)
    return tinc / (TWOPI * vl * math.sqrt(e_mev))


def unfac(l: int, rho: float, rhoc: float, amun: float) -> tuple[float, float]:
    """Penetrability (times nu) and phase shift for l = 0, 1, 2 (1, 1 above).

    TALYS: unfac.f90:1 (unfac)
    Test: tests/hf/test_kwcov_b10.py
    """
    r2 = rho * rho
    if l == 0:
        return amun, rhoc
    if l == 1:
        return amun * r2 / (1.0 + r2), rhoc - math.atan(rhoc)
    if l == 2:
        r4 = r2 * r2
        return amun * r4 / (9.0 + 3.0 * r2 + r4), rhoc - math.atan(3.0 * rhoc / (3.0 - rhoc * rhoc))
    return 1.0, 1.0


def gnrl(galpha: float, gbeta: float, gam: float, mu: int, nu: int, lamda: int, df: float, id_: int) -> float:
    """NJOY's fluctuation integrals (10-point quadratures per chi-squared degree 1-4).

    TALYS: gnrl.f:1 (gnrl)
    Test: tests/hf/test_kwcov_b10.py
    """
    if galpha <= 0.0 or gam <= 0.0 or gbeta < 0.0 or (gbeta > 0.0 and df < 0.0):
        return 0.0
    qpm, qwm = _QP[:, mu - 1].astype(float), _QW[:, mu - 1].astype(float)
    qpn, qwn = _QP[:, nu - 1].astype(float), _QW[:, nu - 1].astype(float)
    qpl, qwl = _QP[:, lamda - 1].astype(float), _QW[:, lamda - 1].astype(float)
    if gbeta == 0.0 and df == 0.0:
        if id_ == 1:
            return float((qwm * qpm * qpm / (galpha * qpm + gam)).sum())
        if id_ == 2:
            return float((qwm * qpm / (galpha * qpm + gam)).sum())
        return 0.0
    if gbeta == 0.0 and df > 0.0:
        den = galpha * qpm[:, None] + gam + df * qpl[None, :]
        w = qwm[:, None] * qwl[None, :]
        if id_ == 1:
            return float((w * qpm[:, None] ** 2 / den).sum())
        if id_ == 2:
            return float((w * qpm[:, None] / den).sum())
        return 0.0
    if gbeta > 0.0 and df == 0.0:
        den = galpha * qpm[:, None] + gbeta * qpn[None, :] + gam
        w = qwm[:, None] * qwn[None, :]
        if id_ == 1:
            return float((w * qpm[:, None] ** 2 / den).sum())
        if id_ == 2:
            return float((w * qpm[:, None] / den).sum())
        return float((w * qpm[:, None] * qpn[None, :] / den).sum())
    den = galpha * qpm[:, None, None] + gbeta * qpn[None, :, None] + gam + df * qpl[None, None, :]
    w = qwm[:, None, None] * qwn[None, :, None] * qwl[None, None, :]
    if id_ == 1:
        return float((w * qpm[:, None, None] ** 2 / den).sum())
    if id_ == 2:
        return float((w * qpm[:, None, None] / den).sum())
    return float((w * qpm[:, None, None] * qpn[None, :, None] / den).sum())


def csunr2(ay: float, l: int, J: int, w: dict, Dlj: dict, nulj: dict, e_mev: float, wavenum: float,
           tarmass: float, A: int, spi: float) -> tuple[float, float, float, float]:
    """NJOY-formalism (l, J) scattering, fission, capture cross sections [b] and potential scattering spot(l).
    `w` = urrwidth by type. Returns (sigs, sigf, sigc, spot); None for sig* when D(l, J) = 0 (TALYS returns early and
    keeps the previous values).

    TALYS: csunr2.f90:1 (csunr2)
    Test: tests/hf/test_kwcov_b10.py
    """
    gnox, gxx, ggx, gfx = w[(3, l, J)], w[(1, l, J)], w[(0, l, J)], w[(-1, l, J)]
    dx = Dlj.get((l, J), 0.0)
    if dx == 0.0:
        return None, None, None, 0.0
    n0 = nulj.get((0, l, J), 0)
    amun = float(n0)
    mu = min(max(n0, 1), 4)
    nu = min(max(nulj.get((-1, l, J), 0), 1), 4)
    lamda = min(max(nulj.get((1, l, J), 0), 1), 4)
    e = e_mev * 1.0e6
    sqrte = math.sqrt(e)
    k = wavenum * 10.0
    const = 2.0 * e * math.pi ** 2 / k ** 2
    odd = (A + 1) % 2
    aj = J + 0.5 * odd
    gj = (2.0 * aj + 1.0) / (4.0 * spi + 2.0)
    ac = 0.123 * tarmass ** (1.0 / 3.0) + 0.08
    rho = k * ac
    rhoc = k * ay
    vl, ps = unfac(l, rho, rhoc, amun)
    vl = vl * sqrte
    spot = 2.0 * TWOPI * (2.0 * l + 1.0) * (math.sin(ps) / k) ** 2
    gnx = gnox * vl
    temp = const * gj * gnx / (e * dx)
    gs = gnrl(gnx, gfx, ggx, mu, nu, lamda, gxx, 1) * temp * gnx
    gc = gnrl(gnx, gfx, ggx, mu, nu, lamda, gxx, 2) * temp * ggx
    gff = gnrl(gnx, gfx, ggx, mu, nu, lamda, gxx, 3) * temp * gfx
    gs = gs - const * gj * 2.0 * gnx * math.sin(ps) ** 2 / (e * dx)
    return gs, gff, gc, spot


def thermal_capture_mb(cas) -> float:
    """xscaptherm(-1) as urr.dat prints it: a deck `xscaptherm`, else the structure/thermal table of the target
    (isomer -1 row, or the sum over residual isomers), else Kopecky's 1.5e-3 (a (S_n - pair))^3.5 of the compound
    nucleus.

    TALYS: thermalxs.f90:1 (thermalxs)
    Test: tests/hf/test_kwcov_b10.py
    """
    from physics.hf.core.constants import nuclide_symbol
    from physics.hf.structure.files import talys_structure_dir

    p = getattr(cas, "params", None)
    try:
        if p is not None and "xscaptherm" in p:
            v = float(p.at("xscaptherm", -1))
            if v != 0.0:
                return v
    except (KeyError, TypeError, ValueError, IndexError):
        pass
    Z, A = int(cas.Zt), int(cas.At)
    f = talys_structure_dir() / "thermal" / f"{nuclide_symbol(Z).capitalize()}.ther"
    xs: dict[int, float] = {}
    if f.is_file():
        for line in f.read_text(errors="replace").splitlines()[1:]:
            try:
                ia, iso_r = int(line[4:8]), int(line[12:16])
                v = line[16:31].strip()
                val = float(v) if v else 0.0
            except ValueError:
                continue
            if ia == A and val != 0.0:
                xs[iso_r] = val
        if -1 in xs:
            return xs[-1]
        tot = sum(v for k, v in xs.items() if k >= 0)
        if tot != 0.0:
            return tot
    ld = cas.ld_of(Z, A + 1)[0]
    ald = float(np.asarray(ld.alev.detach() if hasattr(ld.alev, "detach") else ld.alev).ravel()[0])
    pair = float(np.asarray(ld.pair_mev.detach() if hasattr(ld.pair_mev, "detach") else ld.pair_mev).ravel()[0])
    sn = float(np.asarray(ld.S_mev.detach() if hasattr(ld.S_mev, "detach") else ld.S_mev).ravel()[0])
    sp = max(np.float32(sn - pair), 1.0)
    return float(np.float32(1.5e-3 * (ald * sp) ** 3.5))


# ------------------------------------------------------------------------------------------------ the energy hook


def wanted(cas, e_inc_mev: float) -> bool:
    """energies.f90:184-188: URR at this energy (Einc <= eurr) on a run that asks for it.

    TALYS: urr.f90:1 (urr)
    Test: tests/hf/test_kwcov_b10.py
    """
    return bool(STATE) and float(np.float32(e_inc_mev)) <= float(np.float32(STATE["eurr"]))


def record(cas, ci, e_inc_mev: float) -> None:
    """urr.f90 at one incident energy (output only): comptarget's (l, J) blocks, dtheory, widths, strength functions,
    the NJOY loop, the cross sections; urrout's rows go to STATE. `ci` = the CompoundInputs of this energy.

    TALYS: urr.f90:1 (urr), urrout.f90:1 (urrout)
    Test: tests/hf/test_kwcov_b10.py
    """
    from physics.hf.compound.target import _exact_incident_channel
    from physics.hf.core.constants import talys_constants
    from physics.hf.core.grids import incident_kinematics
    from physics.hf.projectile import target_mass_index

    o = cas.options
    lurr = int(o.lurr)
    ci = _exact_incident_channel(ci)
    cj = comptarget_lj(ci, lurr)
    S = STATE
    for l, J in cj["rng"]:
        S["lmin"] = min(S["lmin"], l)
        S["lmax"] = max(S["lmax"], l)
        S["Jmin"][l] = min(S["Jmin"][l], J)
        S["Jmax"][l] = max(S["Jmax"][l], J)
    c = talys_constants()
    tarmass = float(cas.m.mass_amu[target_mass_index()])
    _, wavenum = incident_kinematics(
        e_inc_mev, 1, tarmass, float(cas.m.specmass[c["parZ"][1], c["parN"][1], 1]),
        float(cas.m.redumass_amu[c["parZ"][1], c["parN"][1], 1]), o.flagrel)
    inc = cas.incident(e_inc_mev)
    rprime = float(np.asarray(inc.r_prime_fm.detach() if hasattr(inc.r_prime_fm, "detach") else inc.r_prime_fm)
                   .ravel()[0])
    ld_cn = cas.ld_of(int(cas.Zt), int(cas.At) + 1)[0]
    Dl, Dlj = dtheory_lj(ld_cn, 0.5 * ci.targetspin2, int(ci.target_parity), e_inc_mev, int(ci.lmaxinc))
    nulj, Tl, TINC = cj["NU"], cj["T"], dict(cj["TINC"])
    lo, hi = S["lmin"], min(S["lmax"], lurr)
    strlj, strl, width = {}, {}, {}
    for l in range(lo, hi + 1):
        s_, sg = 0.0, 0.0
        for J in range(S["Jmin"][l], S["Jmax"][l] + 1):
            ti = TINC.get((l, J), 0.0)
            n0 = nulj.get((0, l, J), 0)
            if n0 > 0:
                ti = ti / n0
            strlj[(l, J)] = strengthfunc(ti, l, e_inc_mev, wavenum, tarmass)
            gJ = (2 * J + 1.0) / (2.0 * (ci.targetspin2 + 1.0))
            sg += gJ
            s_ += gJ * strlj[(l, J)]
            for t in range(-1, 7):
                width[(t, l, J)] = Dlj.get((l, J), 0.0) * Tl.get((t, l, J), 0.0) / TWOPI
            width[(3, l, J)] = Dlj.get((l, J), 0.0) * strlj[(l, J)] * 1.0e-4
        if sg > 0:
            strl[l] = s_ / sg
    if S["RprimeU"] == 0.0:
        S["RprimeU"] = rprime
    XS = cj["XS"]
    xsN = [0.0] * 5
    xsT = [0.0] * 5
    spi = 0.5 * ci.targetspin2
    A = int(cas.At)
    njoy = bool(o.flagurrnjoy)
    sig = {}
    spot = {}
    for l in range(lo, hi + 1):
        for J in range(S["Jmin"][l], S["Jmax"][l] + 1):
            for t in (-1, 0, 1, 3):
                width.setdefault((t, l, J), 0.0)
    if njoy:
        r0 = 0.1 * S["RprimeU"]
        err = 0.005
        rsig, rsig0, rsig1 = 0.0, 1.0, 1.0
        istop = 0
        while rsig > 1.0 + err or rsig < 1.0 - err:
            istop += 1
            n3 = n4 = t1 = t3 = t4 = 0.0
            for l in range(lo, min(2, lurr) + 1):
                for J in range(S["Jmin"][l], S["Jmax"][l] + 1):
                    width[(1, l, J)] = width.get((1, l, J), 0.0) / rsig0
                    width[(-1, l, J)] = width.get((-1, l, J), 0.0) * rsig1
                    gs, gf, gc, sp = csunr2(r0, l, J, width, Dlj, nulj, e_inc_mev, wavenum, tarmass, A, spi)
                    spot[l] = sp
                    if gs is not None:
                        sig[(l, J)] = (gs, gf, gc)
                    gs, gf, gc = sig.get((l, J), (0.0, 0.0, 0.0))
                    n3 += gf * 1000.0
                    n4 += gc * 1000.0
                    t1 += XS.get((1, l, J), 0.0)
                    t3 += XS.get((-1, l, J), 0.0)
                    t4 += XS.get((0, l, J), 0.0)
            rsig0 = t4 / n4 if n4 > 0 else 1.0
            rsig1 = t3 / n3 if n3 > 0 else 1.0
            if t4 > t3:
                if t1 > 0:
                    rsig, rsig1 = rsig0, 1.0
                else:
                    rsig, rsig1 = 1.0, 1.0
            else:
                if rsig1 > 1.0 + err or rsig1 < 1.0 - err:
                    rsig, rsig0 = rsig1, 1.0
                elif t1 > 0:
                    rsig, rsig1 = rsig0, 1.0
                else:
                    rsig, rsig1 = 1.0, 1.0
            if istop > 100:
                rsig = 1.0
    for l in range(lo, min(2, lurr) + 1):
        for J in range(S["Jmin"][l], S["Jmax"][l] + 1):
            if njoy:
                gs, gf, gc, sp = csunr2(0.1 * S["RprimeU"], l, J, width, Dlj, nulj, e_inc_mev, wavenum, tarmass, A,
                                        spi)
                spot[l] = sp
                if gs is not None:
                    sig[(l, J)] = (gs, gf, gc)
                gs, gf, gc = sig.get((l, J), (0.0, 0.0, 0.0))
                xsN[1] += XS.get((1, l, J), 0.0)
                xsN[2] += gs * 1000.0
                xsN[3] += gf * 1000.0
                xsN[4] += gc * 1000.0
            xsT[1] += XS.get((1, l, J), 0.0)
            xsT[3] += XS.get((-1, l, J), 0.0)
            xsT[4] += XS.get((0, l, J), 0.0)
        if njoy:
            xsN[2] += spot.get(l, 0.0) * 1000.0
    if njoy:
        xsN[1] += xsN[2] + xsN[3] + xsN[4]
    # ---- urrout: urr.dat block, l files (the elastic column of urrtalys.tot is filled by add_to_results)
    sm = cas.m.s_mev  # S(Zix, Nix, type); Q(type) = S(0, 0, k0) - S(0, 0, type) (nuclides.f90:242)
    sep = {t: float(sm[0, 0, t]) for t in range(7)}
    q = {t: sep[1] - sep[t] for t in sep}
    odd = (A + 1) % 2
    nin = len(S["energies"])
    S["energies"].append(float(e_inc_mev))
    blk = []
    for l in range(0, lurr + 1):
        for J in range(S["Jmin"][l], S["Jmax"][l] + 1):
            blk.append([float(e_inc_mev), l, J + 0.5 * odd, cj["PAR"].get((l, J), 1), Dl[l], Dlj.get((l, J), 0.0),
                        strl.get(l, 0.0), strlj.get((l, J), 0.0), width.get((1, l, J), 0.0),
                        width.get((3, l, J), 0.0), width.get((0, l, J), 0.0), width.get((-1, l, J), 0.0),
                        width.get((2, l, J), 0.0), width.get((6, l, J), 0.0)])
    S["urrdat"].append(dict(E=float(e_inc_mev), S_n=sep[1], xscaptherm=S.setdefault(
        "xscaptherm", thermal_capture_mb(cas)), rprime=rprime, rows=blk))
    for t in range(-1, 7):
        if t == -1 and not bool(ci.flagfission):
            continue
        if t == 5 and q.get(2, -1.0) <= 0.0:
            continue
        if t == 6 and q.get(6, -1.0) <= 0.0:
            continue
        for l in range(lo, hi + 1):
            name, col = _LFILE[t]
            fname = f"{name}.l{l:02d}"
            row = {}
            for J in range(S["Jmin"][l], S["Jmax"][l] + 1):
                xv, yv = 0.0, width.get((t, l, J), 0.0)
                if t in (-1, 1):
                    xv = float(nulj.get((t, l, J), 0))
                if t == 2:
                    yv = Dlj.get((l, J), 0.0)
                if t == 3:
                    xv = float(nulj.get((0, l, J), 0))
                if t == 4:
                    yv = strlj.get((l, J), 0.0)
                if t == 5:
                    xv, yv = float(nulj.get((2, l, J), 0)), width.get((2, l, J), 0.0)
                if t == 6:
                    xv = float(nulj.get((6, l, J), 0))
                row[J + 0.5 * odd] = (xv, yv)
            _append(fname, col, row, nin)
    for t in (7, 8):
        for l in range(lo, hi + 1):
            fname = f"urrspacingl.l{l:02d}" if t == 7 else f"urrneustrengthl.l{l:02d}"
            _append(fname, "spacing" if t == 7 else "strength", {None: Dl[l] if t == 7 else strl.get(l, 0.0)}, nin)
    S["records"].append(dict(E=float(e_inc_mev), xsT=xsT, xsN=xsN, njoy=njoy, rprime=rprime,
                             RprimeU=S["RprimeU"]))


def _append(fname: str, col: str, row: dict, nin: int) -> None:
    """One row of an urrout l-file; a file first opened at a later energy gets "not calculated" rows before it."""
    f = STATE["files"].setdefault(fname, dict(col=col, rows=[]))
    if fname not in STATE["exist"]:
        STATE["exist"].add(fname)
        for e in STATE["energies"][:nin]:
            f["rows"].append((e, None))
    f["rows"].append((STATE["energies"][nin], row))


# ------------------------------------------------------------------------------------------------ Results


def tables(elastic_by_e: dict | None = None) -> dict:
    """STATE as {file: {column: ndarray}}; `elastic_by_e` {E: xselastot mb} fills urrtalys.tot's elastic column.

    TALYS: urrout.f90:1 (urrout)
    Test: tests/hf/test_kwcov_b10.py
    """
    if not STATE or not STATE.get("records"):
        return {}
    out: dict = {}
    cols = ["E", "l", "J", "P", "D(l)", "D(l,J)", "S(l)", "S(l,J)", "Gx(l,J)", "Gn(l,J)", "Gg(l,J)", "Gf(l,J)",
            "Gp(l,J)", "Ga(l,J)"]
    rows = [r for b in STATE["urrdat"] for r in b["rows"]]
    d = {c: np.array([r[i] for r in rows], dtype=float) for i, c in enumerate(cols)}
    d["S_n"] = np.array([b["S_n"] for b in STATE["urrdat"]])
    d["xscaptherm"] = np.array([b["xscaptherm"] for b in STATE["urrdat"]])
    d["rprime"] = np.array([b["rprime"] for b in STATE["urrdat"]])
    d["block_E"] = np.array([b["E"] for b in STATE["urrdat"]])
    out["urr.dat"] = d
    for fname, f in STATE["files"].items():
        js = []
        for _, row in f["rows"]:
            for j in (row or {}):
                if j not in js:
                    js.append(j)
        t = {"E": np.array([e for e, _ in f["rows"]], dtype=float)}
        if js == [None]:
            t[f["col"]] = np.array([np.nan if row is None else row[None] for _, row in f["rows"]], dtype=float)
        else:
            for j in sorted(js):
                t[f"J={j:g}:nu"] = np.array([np.nan if (row is None or j not in row) else row[j][0]
                                             for _, row in f["rows"]], dtype=float)
                t[f"J={j:g}:{f['col']}"] = np.array([np.nan if (row is None or j not in row) else row[j][1]
                                                     for _, row in f["rows"]], dtype=float)
        out[fname] = t
    recs = STATE["records"]
    E = np.array([r["E"] for r in recs])
    el = np.array([(elastic_by_e or {}).get(round(r["E"], 6), np.nan) for r in recs])
    xsT = np.array([r["xsT"] for r in recs])
    tot = xsT[:, 1] + el + xsT[:, 3] + xsT[:, 4]
    out["urrtalys.tot"] = {"E": E, "xs": tot, "elastic": el, "capture": xsT[:, 4], "fission": xsT[:, 3],
                           "rprime": np.array([r["rprime"] for r in recs])}
    if any(r["njoy"] for r in recs):
        xsN = np.array([r["xsN"] for r in recs])
        out["urrnjoy.tot"] = {"E": E, "xs": xsN[:, 1], "elastic": xsN[:, 2], "capture": xsN[:, 4],
                              "fission": xsN[:, 3], "rprime": np.array([r["RprimeU"] for r in recs])}
        tv = np.stack([tot, el, xsT[:, 4], xsT[:, 3]], 1)
        nv = np.stack([xsN[:, 1], xsN[:, 2], xsN[:, 4], xsN[:, 3]], 1)
        ratio = np.where(nv > 0, tv / np.where(nv > 0, nv, 1.0), 1.0)
        out["urrratio.tot"] = {"E": E, "xs": ratio[:, 0], "elastic": ratio[:, 1], "capture": ratio[:, 2],
                               "fission": ratio[:, 3]}
    return out


def add_to_results(res):
    """Results.urr from the recorded energies (empty and `res` unchanged when the run asked for no URR).

    TALYS: urrout.f90:1 (urrout)
    Test: tests/hf/test_kwcov_b10.py
    """
    if not STATE or not STATE.get("records"):
        return res
    el = {}
    if "elastic" in res.totals_mb:
        for e, v in zip(res.e_inc_mev.tolist(), res.totals_mb["elastic"].tolist()):
            el[round(float(np.float32(e)), 6)] = float(v)
    for r in STATE["records"]:
        r["E"] = float(r["E"])
    elastic = {round(float(np.float32(r["E"])), 6): el.get(round(float(np.float32(r["E"])), 6), np.nan)
               for r in STATE["records"]}
    t = tables({round(r["E"], 6): elastic[round(float(np.float32(r["E"])), 6)] for r in STATE["records"]})
    STATE.clear()  # one run's records go to one Results
    return replace(res, urr=t)


def write_files(urr: dict, outdir) -> list:
    """Write Results.urr as TALYS-named plain files (`#` header lines, columns as urrout.f90 orders them).

    TALYS: urrout.f90:1 (urrout)
    Test: tests/hf/test_kwcov_b10.py
    """
    from pathlib import Path

    p = Path(outdir)
    p.mkdir(parents=True, exist_ok=True)
    done = []
    for name, cols in urr.items():
        keys = [k for k in cols if k not in ("S_n", "xscaptherm", "rprime", "block_E")]
        n = len(cols[keys[0]])
        with open(p / name, "w") as f:
            f.write("# " + " ".join(keys) + "\n")
            for i in range(n):
                f.write("".join(f"{float(cols[k][i]):15.6E}" for k in keys) + "\n")
        done.append(name)
    return done
