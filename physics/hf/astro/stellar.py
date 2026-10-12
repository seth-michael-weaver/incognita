"""STELLARSEF: capture on thermally populated target states (TALYS `astro y`, default `astrogs n`).

Env `INCOGNITA_STELLAR=y` (default OFF; OFF never calls anything here, so every run is bit-identical).

Method = TALYS astrotarget.f90 / astroprepare.f90 / partfunc.f90 / stellarrate.f90 (the NON-SMOKER / BRUSLIB thermalised
target). At each incident energy E of the ordinary ground-state run, the compound nucleus at E_tot = S_n + E_cm decays through
the same exit channels whatever level mu of the target formed it. Level mu (E_mu < E_cm) forms it through the neutron channel
the ground-state run already holds as its exit to mu: Tjlnex(l, j, k0, mu) at E'_cm = E_cm - E_mu. `record` re-enters the
engine's own comptarget (`compound.target._case`, width fluctuations included, the incident channel of entrance mu exactly
TALYS's Tjlnex) with that entrance: target spin/parity J_mu/pi_mu, Ltarget = mu, CNfactor = pi/k_mu^2 /((2s+1)(2J_mu+1)) with
k_mu at E'_cm, formation flux = pi/k_mu^2 sum T (no direct/PE depletion: TALYS direct.f90:33 runs no direct reaction from
an excited target). The exit row of the ground state gets the ground-state run's exact Tjlinc (comptarget.f90:358), so
sigma(0 -> mu) of the ground-state run and sigma(mu -> 0) of entrance mu use one transmission set: detailed balance
(2I_0+1) k_0^2 sigma(0->mu) / c_0 = (2J_mu+1) k_mu^2 sigma(mu->0) / c_mu is an identity of the port (STELLARSEF Step 0a).
This is the full non-lumped HF+WFC version of TALYS's lumped astrotarget loop; TALYS's own Ltarget = mu run would use the
exactly computed spherical T at E'_cm instead of the interpolated Tjlnex (densprepare pol2, <= 2.4 % on spherical targets).

Partition function (partfunc.f90): G(T) = sum_discrete (2J+1) exp(-E/kT) + int_{E_NL} sum_{J,pi} (2J+1) rho(E,J,pi) exp(-E/kT) dE.
Stellar rate (stellarrate.f90, astrogs n): N_A<sigma v>* = sum_mu (2J_mu+1) exp(-E_mu/kT) int E' sigma_mu(E') exp(-E'/kT) dE' x
const / G(T); SEF = that / the same with the ground state only and G = 2I_0+1.

Wired on the C chart path (`engine_c.cases`, the production path) only; every other path keeps the old `Ltarget /= 0`
refusal and never calls `record`.
"""
from __future__ import annotations

import copy
import math
import os
from dataclasses import replace

import numpy as np

ENV = "INCOGNITA_STELLAR"
KT12_KEV = (5.0, 8.0, 10.0, 15.0, 20.0, 25.0, 30.0, 40.0, 50.0, 60.0, 80.0, 100.0)  # RATEPACK kT grid
T9_GRID = (0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0, 3.0, 5.0, 7.0, 10.0)
KT_PER_T9_MEV = 0.0861733  # k_B x 1e9 K in MeV
LOG: list[dict] = []  # per incident energy, filled by `record` during one run; the runner writes and clears it
STATE: dict = {}


def enabled() -> bool:
    return os.environ.get(ENV, "n").strip().lower() in ("y", "1", "yes")


def emax_level_mev() -> float:
    """highest target level used as an entrance: 30 kT_max, kT_max = 100 keV (brief); env INCOGNITA_STELLAR_EMAX."""
    return float(os.environ.get("INCOGNITA_STELLAR_EMAX", "3.0"))


def einc_max_mev() -> float:
    """record only incident energies up to this (the Maxwellian never needs more); env INCOGNITA_STELLAR_EINC_MAX."""
    return float(os.environ.get("INCOGNITA_STELLAR_EINC_MAX", "8.0"))


def continuum_on() -> bool:
    """continuum-bin entrances (TALYS astrotarget nexastro > NL); env INCOGNITA_STELLAR_CONT (default y)."""
    return os.environ.get("INCOGNITA_STELLAR_CONT", "y").strip().lower() in ("y", "1", "yes")


def reset() -> None:
    LOG.clear()
    STATE.clear()


class _NoWfcnorm:
    """raw comptarget populations (INCOGNITA_WFCNORM is one uniform factor per case; it is recorded, not applied)"""

    def __enter__(self):
        self.v = os.environ.pop("INCOGNITA_WFCNORM", None)

    def __exit__(self, *a):
        if self.v is not None:
            os.environ["INCOGNITA_WFCNORM"] = self.v


def _sums(pop, k0: int, lt: int) -> dict:
    """per exit type: population summed over states (compound elastic at (k0, lt) split off), per discrete level for k0."""
    p = pop.detach().numpy()
    per = p.sum((2, 3))  # (7, Nex)
    out = {"type": [float(x) for x in per.sum(1)], "el": float(per[k0, lt])}
    out["type"][k0] -= out["el"]
    out["k0_lev"] = [float(x) for x in per[k0]]
    return out


def _levels(r) -> dict:
    n = int(min(r.nlast, r.maxex))
    return dict(nlast=int(r.nlast), n=n, ex_mev=[float(x) for x in r.ex_mev[: n + 1]],
                j2=[int(x) for x in r.jdis2[: n + 1]], par=[int(x) for x in r.parlev[: n + 1]])


def record(cas, st, binp, cinp, etot: float, a_e: dict, fkw: dict, pop_front) -> None:
    """one incident energy of the ground-state run: ground-state comptarget (raw) + one re-entrance per open target level."""
    import torch

    from physics.hf.compound.chain import compound_inputs
    from physics.hf.compound.normalization import compound_formation
    from physics.hf.compound.target import _case, _exact_incident_channel
    from physics.hf.compound.wfcnorm import factor as wn_factor
    from physics.hf.core.constants import talys_constants
    from physics.hf.core.grids import incident_kinematics
    from physics.hf.core.tensors import DTYPE

    e = float(binp.e_inc_mev)
    if e > einc_max_mev() or int(binp.k0) != 1 or int(binp.ltarget) != 0:
        return
    rec = dict(e_inc_mev=e)
    STATE["wfcnorm_env"] = os.environ.get("INCOGNITA_WFCNORM", "0").lower() in ("1", "y", "yes")
    try:
        c = talys_constants()
        k0 = 1
        pz, pn = c["parZ"][k0], c["parN"][k0]
        spm = float(cas.m.specmass[pz, pn, k0]); red = float(cas.m.redumass_amu[pz, pn, k0])
        tm = float(cas.m.mass_amu[0, 1]); rel = cas.options.flagrel
        ecm, _ = incident_kinematics(e, k0, tm, spm, red, rel)
        rec.update(e_cm_mev=float(ecm), specmass=spm)
        if "g" not in STATE:
            try:
                STATE["g"] = partition(cas)
            except Exception as exc:
                STATE["g"] = None
                STATE["g_err"] = f"{type(exc).__name__}: {exc}"
        with torch.inference_mode(), _NoWfcnorm():
            ci = _exact_incident_channel(compound_inputs(cas, st, binp, cinp, etot, a_e, **fkw))
            use_wfc = bool(ci.flagwidth and ci.wmode >= 1)
            pop0, fis0 = _case(ci)
            f0 = wn_factor(float(pop0.sum()), float(fis0), float(ci.xsflux_mb)) if (use_wfc and wn_on_env()) else 1.0
            rec["gs"] = dict(cn=float(ci.cnfactor_mb), xsflux=float(ci.xsflux_mb), fis=float(fis0), wfcnorm=f0,
                             targetspin2=int(ci.targetspin2), flagwidth=bool(ci.flagwidth), **_sums(pop0, k0, 0))
            pf = pop_front.pop_mb[0].detach().numpy().sum((1, 2, 3))
            rec["gs"]["front_type"] = [float(x) for x in pf]
            r = ci.residuals[k0]
            lv = _levels(r)
            rec["levels"] = lv
            def enter(nex, j2, par, epcm):
                """comptarget re-entered through target state (nex, J = j2/2, par) at E'_cm = epcm."""
                lmax = int(r.lmaxhf[nex])
                tinc = np.asarray(r.tjl[nex, : lmax + 1], float)
                if lmax < 0 or not np.any(tinc > 0):
                    return None
                elab = epcm / spm
                _, wn = incident_kinematics(elab, k0, tm, spm, red, rel)
                tt = torch.as_tensor(tinc, dtype=DTYPE)
                z = torch.zeros((), dtype=DTYPE)
                wt = torch.tensor(float(wn), dtype=DTYPE)
                cf = compound_formation(tt, wt, j2, par, lmax, k0, torch.ones((), dtype=DTYPE), z, z, z)
                cf = compound_formation(tt, wt, j2, par, lmax, k0, cf.xs_reacsum_mb, z, z, z)
                cim = copy.copy(ci)
                cim.e_inc_mev = elab
                cim.cnfactor_mb = float(cf.cn_factor_mb)
                cim.xsflux_mb = float(cf.xs_flux_mb)
                cim.xsreacinc_mb = float(cf.xs_reacsum_mb)
                cim.j2beg, cim.j2end = int(cf.j2beg), int(cf.j2end)
                cim.targetspin2, cim.target_parity, cim.lmaxinc, cim.ltarget = j2, par, lmax, nex
                cim.tjlinc = tinc
                cim.flagwidth = ci.flagwidth  # one width-fluctuation regime per CN energy (astrotarget.f90 uses the run's flagwidth)
                cim.residuals = dict(ci.residuals)
                pm, fm = _case(cim)
                extra = {}
                if os.environ.get("INCOGNITA_STELLAR_CHECK", "n") == "y":  # Step 0a: W = 1 twin of this entrance
                    cw = copy.copy(cim)
                    cw.flagwidth = False
                    pw, _ = _case(cw)
                    extra["cap_nowfc"] = float(pw[0].sum())
                fmu = (wn_factor(float(pm.sum()), float(fm), float(cim.xsflux_mb))
                       if (cim.flagwidth and cim.wmode >= 1 and wn_on_env()) else 1.0)
                return dict(e_cm_prime=epcm, e_lab_prime=elab, wavenum=float(wn), cn=float(cim.cnfactor_mb),
                            xsflux=float(cim.xsflux_mb), fis=float(fm), wfcnorm=fmu, flagwidth=cim.flagwidth, lmax=lmax,
                            **extra, **_sums(pm, k0, nex))

            lev = []
            for mu in range(1, lv["n"] + 1):
                emu = float(r.ex_mev[mu])
                if emu > emax_level_mev() or float(ecm) - emu <= 0.0:
                    break
                j2, par = int(r.jdis2[mu]), int(r.parlev[mu])
                x = enter(mu, j2, par, float(ecm) - emu)
                if x is None:
                    continue
                rho_w = float(r.rho[mu, min(j2 // 2, r.rho.shape[1] - 1), 0 if par == -1 else 1])
                lev.append(dict(mu=mu, e_mu=emu, j2=j2, par=par, rho_w=rho_w, **x))
            # continuum bins of the target (astrotarget.f90 nexastro > NL), every (J, parity) with rho0 > 0, weight rho0.
            # Hauser-Feshbach WITHOUT width fluctuations (W = 1): capture is then linear in the entrance feed, so one
            # branching B(J, P) = Gamma_gamma / denomhf per compound cell serves every entrance (`_hf_capture`); the full
            # comptarget per entrance would be ~2,400 calls per energy. Checked against `_case` (W = 1) on the discrete
            # entrances (rec["lev"][i]["cap_hf"]), and the WFC/no-WFC ratio there is recorded (Step 0a).
            cont = []
            if continuum_on():
                bcache: dict = {}
                odd = int(cas.At) % 2
                for x in lev:
                    x["cap_hf"] = _hf_capture(ci, r, x["mu"], x["j2"], x["par"], x["cn"], bcache)
                for nex in range(int(r.nlast) + 1, int(r.maxex) + 1):
                    ex = float(r.ex_mev[nex])
                    if ex > emax_level_mev() or float(ecm) - ex <= 0.0:
                        break
                    epcm = float(ecm) - ex
                    _, wn = incident_kinematics(epcm / spm, k0, tm, spm, red, rel)
                    pik2 = 10.0 * math.pi / float(wn) ** 2 / 2.0  # pi/k^2 [mb] / (2s+1)
                    nst, ysum = 0.0, 0.0
                    for pi_, par in ((0, -1), (1, 1)):
                        for ir in range(r.rho.shape[1]):
                            w = float(r.rho[nex, ir, pi_])
                            if w < 1.0e-20:
                                continue
                            j2t = 2 * ir + odd
                            cn_t = pik2 / (j2t + 1.0)
                            cap = _hf_capture(ci, r, nex, j2t, par, cn_t, bcache)
                            nst += w * (j2t + 1.0)
                            ysum += w * (j2t + 1.0) * cap
                    cont.append(dict(nex=nex, ex=ex, dex=float(r.dex_mev[nex]) if r.dex_mev is not None else float("nan"),
                                     e_cm_prime=epcm, states=nst, states_cap=ysum))
            rec["cont"] = cont
            rec["lev"] = lev
    except Exception as exc:  # recorded, never raised: the ground-state run must not depend on this
        import traceback

        rec["err"] = f"{type(exc).__name__}: {exc}"
        rec["tb"] = traceback.format_exc()[-2000:]
    LOG.append(rec)


def _hf_capture(ci, r, nex: int, j2t: int, par: int, cn: float, bcache: dict) -> float:
    """first-chance capture [mb] from target state (nex, J = j2t/2, par) without width fluctuations:
    cn sum_{J,P} (2J+1) [sum_{l,j} Tjlnex(l, j, k0, nex)] Gamma_gamma(J,P) / denomhf(J,P) (comptarget.f90, W = 1)."""
    import torch

    from physics.hf.compound.prepare import exit_channel_sums
    from physics.hf.compound.prepare import incident_channels
    from types import SimpleNamespace

    lmax = int(r.lmaxhf[nex])
    tinc = np.asarray(r.tjl[nex, : lmax + 1], float)
    if lmax < 0 or not np.any(tinc > 0):
        return 0.0
    view = SimpleNamespace(residuals=ci.residuals, k0=ci.k0, target_parity=par, targetspin2=j2t, lmaxinc=lmax, tjlinc=tinc)
    j2end = min(2 * lmax + r.parspin2 + j2t, 80)
    tot = 0.0
    for parity in (-1, 1):
        for J2 in range((j2t + r.parspin2) % 2, j2end + 1, 2):
            _, t = incident_channels(view, J2, parity)
            f = float(np.sum(t))
            if f <= 0.0:
                continue
            key = (J2, parity)
            if key not in bcache:
                sx = exit_channel_sums(ci, J2, parity)
                d = float(sx["denom"])
                b = sx["blocks"].get(0)
                g = float((b.weight * b.t[:, None, None, :, :]).sum()) if b is not None else 0.0
                bcache[key] = g / d if d > 0.0 else 0.0
            tot += (J2 + 1.0) * f * bcache[key]
    return cn * tot


def wn_on_env() -> bool:
    """INCOGNITA_WFCNORM as the production run sees it (record() hides it from _case while computing raw populations)."""
    return STATE.get("wfcnorm_env", False)


def partition(cas) -> dict:
    """partfunc.f90 on the engine's target levels and level density: G(T) on the kT12 and T9 grids, plus the discrete-only
    part and the continuum part separately (Step 0a convergence)."""
    import torch

    from physics.hf.density.models import density
    Z, A = int(cas.Zt), int(cas.At)
    lv = cas._levels(0, 1)  # the target, (parZ(k0), parN(k0)), exactly as the run reads it
    nl = int(lv.nlev)
    ed = np.asarray(lv.all_e_mev[: nl + 1], float)
    jd = np.asarray(lv.all_spin[: nl + 1], float)
    ld = cas.ld_of(Z, A)[0]  # (LDNucleus, Ntop, Ncum(NL))
    # continuum: E_NL .. E_NL + 25 MeV, 0.01 MeV trapezoid, J = I + (A mod 2)/2 for I = 0..39, both parities
    ex = np.arange(ed[-1], ed[-1] + 25.0 + 1e-9, 0.01)
    rho = np.zeros_like(ex)
    for ir in range(40):
        jj = ir + (A % 2) / 2.0
        for p in (-1, 1):
            d = density(ld, torch.as_tensor(ex, dtype=torch.float64), torch.tensor(jj, dtype=torch.float64), p)
            rho += (2 * jj + 1) * np.asarray(d.detach(), float).reshape(-1)
    rho[0] = 0.0  # TALYS starts the continuum sum above the last discrete level

    em = emax_level_mev()

    def g_at(kt):
        """(discrete, continuum to E_NL + 25 MeV, discrete <= E_max, continuum <= E_max): the last two are what the
        stellar sum covers (entrances up to E_max), so SEF uses them; the first two measure the truncation."""
        gd = float(np.sum((2 * jd + 1) * np.exp(-ed / kt)))
        w = rho * np.exp(-ex / kt)
        seg = 0.5 * (w[1:] + w[:-1]) * np.diff(ex)
        gc = float(np.sum(seg))
        gdt = float(np.sum(((2 * jd + 1) * np.exp(-ed / kt))[ed <= em]))
        gct = float(np.sum(seg[ex[1:] <= em]))
        return gd, gc, gdt, gct

    out = dict(Z=Z, A=A, nlev=nl, e_levels=ed.tolist(), j_levels=jd.tolist(), ldmodel=int(getattr(ld, "ldmodel", -1)),
               kT12={}, T9={})
    for kt in KT12_KEV:
        out["kT12"][str(kt)] = g_at(kt / 1000.0)
    for t9 in T9_GRID:
        out["T9"][str(t9)] = g_at(t9 * KT_PER_T9_MEV)
    return out


# ----------------------------------------------------------------------------------------------------------------------------
# rates from the records (pure arithmetic, no engine)
# ----------------------------------------------------------------------------------------------------------------------------
def _maxw(e: np.ndarray, s: np.ndarray, kt: float, nsub: int = 32) -> float:
    """int E sigma(E) exp(-E/kT) dE on the record points: E sigma log-log (power law) between points, the exponential
    exact on `nsub` geometric sub-points per segment (trapezoid); 1/v below the first point (E sigma ~ sqrt(E)).
    Accuracy, 1/v sigma on 25 points 1 keV..3 MeV: <= 2e-4 at kT 5..100 keV (tests/hf/test_stellar.py)."""
    o = np.argsort(e); e, s = e[o], s[o]
    ok = s > 0
    e, s = e[ok], s[ok]
    if e.size == 0:
        return 0.0
    es = e * s
    h = np.geomspace(1.0e-4 * e[0], e[0], nsub + 1)
    yh = es[0] * np.sqrt(h / e[0]) * np.exp(-h / kt)
    tot = (2.0 / 3.0) * h[0] * yh[0] + float(np.sum(0.5 * (yh[1:] + yh[:-1]) * np.diff(h)))
    for i in range(e.size - 1):
        a, b = e[i], e[i + 1]
        x = np.geomspace(a, b, nsub + 1)
        k = math.log(es[i + 1] / es[i]) / math.log(b / a)
        y = es[i] * (x / a) ** k * np.exp(-x / kt)
        tot += float(np.sum(0.5 * (y[1:] + y[:-1]) * np.diff(x)))
    return float(tot)


def capture_curves(log: list[dict], wfcnorm: bool = True) -> dict:
    """sigma_0(E_cm), sigma_mu(E'_cm) [mb] of first-chance capture (pop of type 0) and the continuum entrance sum
    Y(E_cm) = sum_bins E'_b sum_{J,P} rho0 (2J+1) sigma_b(E'_b) [mb MeV] from the records."""
    e0, s0, yc, lev = [], [], [], {}
    for r in log:
        if "gs" not in r:
            continue
        f = r["gs"]["wfcnorm"] if wfcnorm else 1.0
        e0.append(r["e_cm_mev"]); s0.append(r["gs"]["type"][0] * f)
        yc.append(sum(c["e_cm_prime"] * c["states_cap"] for c in r.get("cont", [])))
        for x in r.get("lev", []):
            d = lev.setdefault(x["mu"], dict(e_mu=x["e_mu"], j2=x["j2"], par=x["par"], e=[], s=[]))
            d["e"].append(x["e_cm_prime"]); d["s"].append(x["type"][0] * (x["wfcnorm"] if wfcnorm else 1.0))
    o = np.argsort(e0)
    return dict(e0=np.array(e0)[o], s0=np.array(s0)[o], yc=np.array(yc)[o], lev=lev)


def sef_table(log: list[dict], g: dict, i0_2: int, wfcnorm: bool = True) -> list[dict]:
    """SEF, G, X on the kT12 and T9 grids. num(kT) = (2I_0+1) M_0 + sum_mu (2J_mu+1) e^{-E_mu/kT} M_mu
    + int Y(E) e^{-E/kT} dE (continuum entrances, gs-energy axis, trapezoid), M = int E sigma e^{-E/kT} dE;
    rate*/rate_gs = (num / G_trunc) / M_0 with G_trunc = partition up to E_max (the same states as num).
    flag_trunc = 1 - G_trunc/G_full (states above E_max the sum leaves out)."""
    cc = capture_curves(log, wfcnorm)
    rows = []
    for gkey, grid in (("kT12", KT12_KEV), ("T9", T9_GRID)):
        for v in grid:
            kt = v / 1000.0 if gkey == "kT12" else v * KT_PER_T9_MEV
            gd, gc, gdt, gct = g[gkey][str(float(v))]
            m0 = _maxw(cc["e0"], cc["s0"], kt)
            gsum = (i0_2 + 1) * m0
            disc = 0.0
            for mu, d in sorted(cc["lev"].items()):
                disc += (d["j2"] + 1) * math.exp(-d["e_mu"] / kt) * _maxw(np.array(d["e"]), np.array(d["s"]), kt)
            yy = cc["yc"] * np.exp(-cc["e0"] / kt)
            cont = float(np.sum(0.5 * (yy[1:] + yy[:-1]) * np.diff(cc["e0"]))) if yy.size > 1 else 0.0
            num = gsum + disc + cont
            Gt = gdt + gct
            rows.append(dict(grid=gkey, value=v, kt_mev=kt, G_trunc=Gt, G_full=gd + gc, G_disc=gd, G_cont=gc,
                             flag_trunc=1.0 - Gt / (gd + gc), m0=m0, num_gs=gsum, num_disc=disc, num_cont=cont,
                             sef=(num / Gt) / m0 if m0 > 0 and Gt > 0 else float("nan"),
                             X=gsum / num if num > 0 else float("nan"), gs_pop=(i0_2 + 1) / Gt))
    return rows
