"""MACSCLOSED: few-resonance capture where Hauser-Feshbach is not valid (`INCOGNITA_FEWRES`, default OFF).

Mechanism. The HF capture cross section is the ENSEMBLE AVERAGE over resonance ladders (positions with
GOE/Wigner spacings, Porter-Thomas widths) at the model's level spacing D_J, <Gamma_n> and <Gamma_gamma>.
Where the compound level density at S_n is low (closed shells, light nuclei) only a few s-wave
resonances lie in the Maxwellian window, and a real nucleus is ONE draw from that ensemble. The draw
distribution of the window sum is strongly skewed (most draws hold fewer / weaker resonances than the
mean), so the typical capture is below the HF mean (Rauscher, Thielemann & Kratz, PRC 56 (1997) 1613,
Sec. IV.B and Fig. 6: "applying the statistical model ... for a level density which is not
sufficiently large results in an overestimation of the actual cross section").

Region (fixed before scoring, the same for every nucleus): RTK97's criterion, fewer than NTHR = 10
s-wave resonances in the s-wave effective window at kT = 30 keV, Delta = 0.194 T9 (l + 1/2)^(1/2) MeV
(RTK97 eq. 25), i.e. N30 = Delta(30 keV) / D0theo < 10 with D0theo the engine's own theoretical s-wave
spacing (dtheory). Outside the region nothing changes.

Modes (only inside the region):
* ``mean``: the brief's expected value. The PT/Wigner ensemble mean IS the width-fluctuation-corrected
  HF average, so the HF curve is kept and direct capture into the experimental levels
  (`racapcalc.direct_capture_mb(..., "disc")`) is added at every energy.
* ``logmean``: the typical value for a log-scored observable, exp(E[ln(window sum)]):
  sigma(E) = sigma_HF(E) * G(E), G(E) = exp(<ln(r + delta)>) over ladders, with r = M_draw / M_mean the
  Maxwellian (kT = E) window sum of one draw over the ensemble mean (E[r] = 1 by construction) and
  delta = DC(E) / sigma_HF(E) the direct-capture floor. E <= 0.5 MeV: G as computed; 0.5-1 MeV: ln G
  blended linearly in ln E to ln(1 + delta); E >= 1 MeV: G = 1 + delta (= ``mean``). As the window
  fills, r -> 1 and G -> 1 + delta, so the two modes meet wherever HF is valid.
* ``typical`` (FEWTYP): ``logmean`` with NO direct-capture floor (delta = 0, racap not called): sigma = sigma_HF * G,
  G = exp(<ln r>) <= 1 (Jensen), G = 1 at E >= 1 MeV. Replaces the ensemble-mean (HF) capture by the typical (log-mean)
  value of one ladder draw inside the region; users who need the ensemble mean keep FEWRES off (or use G = fewres_G
  in the totals to undo it).

Ensemble model (all inputs read off the run's own Cascade): partial waves l = 0..4; J sequences from
target spin I and j = l +- 1/2, parity = target parity x (-1)^l; D_J = 1 / rho(S_n, J, parity) from the
compound nucleus's own level density (the one HF uses); per channel <Gamma_n>/D_J = -ln(1 - T_l(E)) / (2 pi)
with T_l the run's spin-averaged incident transmission; Gamma_n ~ chi2(nu)/nu, nu = number of j channels
for (l, J); Gamma_gamma fixed (many channels) = the engine's <Gamma_gamma> (radwidtheory: s-wave parity
gamgam_th, opposite parity gamgam_th_p). Narrow-resonance area for levels inside [0, 12 kT]; Breit-Wigner
wings of the 3 nearest bound (E_r < 0) levels and the first level above 12 kT by quadrature. Wigner-surmise
unit ladders and widths use common random numbers (seed from Z, A, sequence, block), Ns = 2000 draws, so G(E) is smooth and
reproducible. Above NMC_MAX expected levels in the window the second-order (Poisson-variance) delta method
is used. Inelastic competition is not in the ensemble (the ratio r, not the HF level, is taken from it).

Wiring: `add_to_results(res, injection)` is called by `engine.run` and `engine_c.run` right after
DIRECTCAP's hook, on the same Results, so the Py and C paths apply the identical function.
Diagnostics land in `res.totals_mb` as fewres_* (per energy): G, dc_mb, hf_mb, n30, mean_over_hf.
Refuses to run together with INCOGNITA_DIRECT_CAPTURE (DC would be counted twice).
Test: tests/hf/test_fewres.py
"""

from __future__ import annotations

import math
import os

import numpy as np

__all__ = ["mode", "n30", "ensemble_G", "add_to_results", "DELTA30_EV", "NTHR"]

KB_MEV_PER_GK = 0.08617333262
T9_30 = 0.030 / KB_MEV_PER_GK
DELTA30_EV = 0.194 * T9_30 * math.sqrt(0.5) * 1.0e6   # RTK97 eq. 25, l = 0, kT = 30 keV (47.76 keV)
NTHR = 10.0
NS = 2000
XMAX = 12.0            # window [0, XMAX kT]
NMC_MAX = 20000        # expected in-window levels (all sequences) above which the delta method is used
E_FULL, E_OFF = 0.5e6, 1.0e6


def mode() -> str:
    v = os.environ.get("INCOGNITA_FEWRES", "off").strip().lower()
    if v in ("", "0", "n", "no", "off", "false"):
        return "off"
    if v in ("mean", "logmean", "typical"):
        return v
    raise ValueError(f"INCOGNITA_FEWRES={v!r}: off | mean | logmean | typical")


def n30(d0_ev: float) -> float:
    return DELTA30_EV / d0_ev if d0_ev > 0 and np.isfinite(d0_ev) else float("inf")


LMAX = 4


def _sequences(I: float, pt: int, rho, gg_same: float, gg_opp: float, lmax: int = LMAX):
    """(l, J, nu, D_J, g_J, Gg) for l = 0..lmax: D_J = 1 / rho(S_n, J, pt (-1)^l) from the run's own
    compound level density `rho(J, parity)` [MeV^-1], nu = number of j = l +- 1/2 channels reaching J,
    Gg = <Gamma_gamma> of the s-wave parity (gg_same) or the opposite parity (gg_opp)."""
    out = []
    for l in range(lmax + 1):
        par = pt * (-1) ** l
        gg = gg_same if l % 2 == 0 else gg_opp
        if not (gg > 0 and np.isfinite(gg)):
            continue
        Jn: dict[float, int] = {}
        for j in (l - 0.5, l + 0.5):
            if j <= 0:
                continue
            J = abs(I - j)
            while J <= I + j + 1e-9:
                Jn[round(J, 1)] = Jn.get(round(J, 1), 0) + 1
                J += 1.0
        for J, nu in sorted(Jn.items()):
            r = float(rho(J, par))
            if r > 1e-10:
                out.append((l, J, nu, 1.0e6 / r, (2 * J + 1) / (2.0 * (2 * I + 1)), gg))
    return out


class _Tl:
    """Spin-averaged incident T_l(E) (E in eV) on the run's grid, log-log interpolation; below the grid
    T_l ~ E^(l + 1/2), above it held flat."""

    def __init__(self, e_ev, tl):
        self.le = np.log(np.asarray(e_ev, float))
        self.lt = np.log(np.maximum(np.asarray(tl, float), 1e-300))   # (n_e, L)

    def tau(self, l: int, E):
        """per-channel <Gamma_n>/D = -ln(1 - T_l) / (2 pi)"""
        if l >= self.lt.shape[1]:
            return np.zeros_like(np.asarray(E, float))
        lE = np.log(np.maximum(np.asarray(E, float), 1e-6))
        lt = np.interp(lE, self.le, self.lt[:, l])
        lt = np.where(lE < self.le[0], self.lt[0, l] + (l + 0.5) * (lE - self.le[0]), lt)
        T = np.clip(np.exp(lt), 0.0, 1.0 - 1e-12)
        return -np.log1p(-T) / (2 * math.pi)


def _chi2_q(nu: int, n: int = 64):
    from scipy.stats import chi2
    return chi2.ppf((np.arange(n) + 0.5) / n, nu) / nu


def _mean_var(seqs, tl, kT):
    """Expected window sum (narrow areas, constant factors dropped) and its Poisson-position variance."""
    E = np.linspace(0.0, XMAX * kT, 801)[1:]
    dE = E[1] - E[0]
    mu = var = 0.0
    for l, J, nu, D, g, gg in seqs:
        x = _chi2_q(nu)[:, None]
        gn = nu * D * tl.tau(l, E)[None, :] * x
        a = 2 * math.pi * g * gn * gg / (gn + gg)
        w = np.exp(-E / kT)
        mu += float(np.sum(a.mean(0) * w) * dE / D)
        var += float(np.sum((a ** 2).mean(0) * w * w) * dE / D)
    return mu, var


BLOCK = 256


def _ladders(seqs, seed: int, emax_ev):
    """Unit Wigner ladders (float32, positions in units of D_J) and chi2/nu widths per sequence. Each
    sequence draws its columns in blocks of BLOCK from its own generator (seed, sequence, block), so a
    ladder's first n levels do not depend on the grid's top energy (Py/C and any grid share draws)."""
    L = []
    for q, (l, J, nu, D, g, gg) in enumerate(seqs):
        nb = (int(math.ceil(emax_ev / D)) + 8 + BLOCK - 1) // BLOCK
        sp, xw = [], []
        for b in range(nb):
            r = np.random.default_rng([seed, q, b])
            sp.append(np.sqrt(-(4.0 / math.pi) * np.log(r.random((NS, BLOCK)))).astype(np.float32))
            xw.append((r.chisquare(nu, (NS, BLOCK)) / nu).astype(np.float32))
        off = np.random.default_rng([seed, q, 1_000_000]).random((NS, 1)).astype(np.float32)
        pos = np.cumsum(np.concatenate(sp, 1), axis=1) - (3.0 + off)
        L.append((pos, np.concatenate(xw, 1)))
    return L


def _draw_sums(seqs, L, tl, kT):
    """Window sum for each of the NS draws at Maxwellian scale kT (same constants as _mean_var)."""
    emax = XMAX * kT
    Eq = np.geomspace(1e-4 * kT, emax, 160)
    M = np.zeros(NS)
    for (l, J, nu, D, g, gg), (pos, xw) in zip(seqs, L):
        nc = min(pos.shape[1], int(math.ceil(emax / D)) + 8)
        pos, xw = pos[:, :nc], xw[:, :nc]
        Er = pos.astype(float) * D
        inw = (Er >= 0) & (Er <= emax)
        if inw.any():
            Ei = np.where(inw, Er, 0.0)
            gn = nu * D * tl.tau(l, Ei) * xw
            a = 2 * math.pi * g * gn * gg / (gn + gg) * np.exp(-Ei / kT)
            M += np.where(inw, a, 0.0).sum(1)
        # wings: 3 nearest bound levels and the first level above the window
        below = np.where(Er < 0, Er, -np.inf)
        idx_b = np.argsort(-below, axis=1)[:, :3]
        idx_a = np.argmax(Er > emax, axis=1)[:, None]
        for idx in (idx_b, idx_a):
            Erw = np.take_along_axis(Er, idx, 1)
            xr = np.take_along_axis(xw, idx, 1).astype(float)
            ok = np.isfinite(Erw) & ((Erw < 0) | (Erw > emax))
            Erw = np.where(ok, Erw, -1e30)
            tq = nu * D * tl.tau(l, Eq)                     # <Gamma_n>(E) on the quadrature grid
            gnq = tq[None, None, :] * xr[:, :, None]
            gtot = gnq + gg
            f = g * gg * gnq * np.exp(-Eq / kT)[None, None, :] / ((Eq[None, None, :] - Erw[:, :, None]) ** 2 + gtot ** 2 / 4)
            wsum = np.trapezoid(f, Eq, axis=2)
            M += np.where(ok, wsum, 0.0).sum(1)
    return M


def ensemble_G(seqs, tl, e_ev, delta, seed: int):
    """ln G(E) for logmean at each energy in e_ev (eV) with DC floor delta(E); also mean-check scalars."""
    e_ev = np.asarray(e_ev, float)
    lnG = np.log1p(np.maximum(delta, 0.0))
    act = e_ev < E_OFF
    if not act.any() or not seqs:
        return lnG
    L = _ladders(seqs, seed, XMAX * float(e_ev[act].max()))
    for i in np.flatnonzero(act):
        kT = float(e_ev[i])
        mu, var = _mean_var(seqs, tl, kT)
        if not (mu > 0):
            continue
        nexp = sum(XMAX * kT / s[3] for s in seqs)
        d = max(float(delta[i]), 0.0)
        if nexp > NMC_MAX:
            lg = math.log1p(d) - var / mu ** 2 / (2 * (1 + d) ** 2)
        else:
            r = _draw_sums(seqs, L, tl, kT) / mu
            lg = float(np.mean(np.log(np.maximum(r + d, 1e-300))))
        if kT > E_FULL:
            w = math.log(E_OFF / kT) / math.log(E_OFF / E_FULL)
            lg = w * lg + (1 - w) * math.log1p(d)
        lnG[i] = lg
    return lnG


def run_ingredients(cas) -> dict:
    """`physics.hf.ingredients.ingredients(cas)` with the `ing_` prefix stripped."""
    from physics.hf.ingredients import PREFIX, ingredients
    return {(k[len(PREFIX):] if k.startswith(PREFIX) else k): v for k, v in ingredients(cas).items()}


def model(cas, ing):
    """(seqs, tl) for the run's Cascade: compound level density, <Gamma_gamma> and incident T_l."""
    import torch

    from physics.hf.density.models import density

    ld = cas.ld_of(int(cas.Zc), int(cas.Ac))[0]
    sn = torch.as_tensor(float(ld.S_mev), dtype=torch.float64)

    def rho(J, par):
        return float(density(ld, sn, torch.as_tensor(float(J), dtype=torch.float64), int(par), 0))

    gg0 = float(ing["gamgam_th_ev"]); gg1 = float(ing["gamgam_th_p_ev"])
    gg1 = gg1 if np.isfinite(gg1) and gg1 > 0 else gg0
    seqs = _sequences(float(ing["target_spin"]), int(ing["target_parity"]), rho, gg0, gg1)
    es = list(cas.energies)
    T = np.zeros((len(es), LMAX + 1))
    for i, e in enumerate(es):
        t = cas.incident(float(e)).t_l
        if t is None:
            raise ValueError("fewres: incident channel without t_l")
        t = np.asarray(t.detach().cpu().numpy() if hasattr(t, "detach") else t, float).reshape(-1)
        n = min(len(t), LMAX + 1)
        T[i, :n] = t[:n]
    return seqs, _Tl(np.asarray(es, float) * 1e6, T)


def add_to_results(res, injection):
    """`engine.run` / `engine_c.run` Results with the MACSCLOSED change in capture (xs000000) and the
    compound nucleus's residual production, in place; off or outside the region -> untouched."""
    m = mode()
    if m == "off" or getattr(injection, "families", ()) or not hasattr(injection, "Z"):
        return res
    from physics.hf.direct import racapcalc
    if m != "typical" and racapcalc.mode() != "off":
        raise ValueError("INCOGNITA_FEWRES adds direct capture itself; unset INCOGNITA_DIRECT_CAPTURE")
    import torch

    Z, A = int(injection.Z), int(injection.A)
    cas = getattr(injection, "cascade", None)
    if cas is None:
        from physics.hf import warmrun
        cas = warmrun.new_cascade(Z, A, tuple(float(x) for x in res.e_inc_mev.detach().cpu().numpy()))
    ing = run_ingredients(cas)
    d0 = float(ing["d0theo_ev"])
    N = n30(d0)
    if not (N < NTHR) or "xs000000" not in res.channels_mb:
        return res
    e_mev = res.e_inc_mev.detach().cpu().numpy().astype(float)
    hf = res.channels_mb["xs000000"].detach().cpu().numpy().astype(float)
    dc = np.zeros_like(hf) if m == "typical" else racapcalc.direct_capture_mb(Z, A, e_mev, "disc")
    with np.errstate(divide="ignore", invalid="ignore"):
        delta = np.where(hf > 0, dc / hf, 0.0)
    e_ev = e_mev * 1e6
    seqs, tl = model(cas, ing)
    if m == "mean":
        new = hf + dc
        G = np.where(hf > 0, new / np.where(hf > 0, hf, 1.0), 1.0)
    else:
        lnG = ensemble_G(seqs, tl, e_ev, delta, seed=1000 * Z + A)
        G = np.exp(lnG)
        new = np.where(hf > 0, hf * G, dc)
    # validation diagnostic: ensemble-mean MACS-scale sum in absolute units / engine HF at kT = E (<= 1 MeV)
    mo = np.full(len(e_ev), np.nan)
    for i in np.flatnonzero(e_ev <= E_OFF):
        kT = float(e_ev[i]); mu, _ = _mean_var(seqs, tl, kT)
        # <sigma>(E) = (pi/k^2) * sum_seq 2 pi g <Gn Gg/G> / D_J ; pi/k^2 = 6.5136e8 ((A+1)/A)^2 / E[eV] mb
        K = 6.5136e8 * ((A + 1.0) / A) ** 2
        mac_ens = (2 / math.sqrt(math.pi)) * K * mu / kT ** 2
        Eg = np.linspace(0, XMAX * kT, 2001)[1:]
        hf_m = (2 / math.sqrt(math.pi)) * np.trapezoid(np.interp(Eg, e_ev, hf) * Eg * np.exp(-Eg / kT), Eg) / kT ** 2
        mo[i] = mac_ens / hf_m if hf_m > 0 else np.nan
    dt = res.e_inc_mev.dtype
    d = torch.as_tensor(new - hf, dtype=dt)
    res.channels_mb["xs000000"] = res.channels_mb["xs000000"] + d
    from physics.hf.results import residual_key
    k = residual_key(Z, A + 1)
    if k in res.residual_production_mb:
        res.residual_production_mb[k] = res.residual_production_mb[k] + d
    if isinstance(getattr(res, "totals_mb", None), dict):
        for key, v in (("fewres_G", G), ("fewres_dc_mb", dc), ("fewres_hf_mb", hf),
                       ("fewres_n30", np.full(len(e_ev), N)), ("fewres_mean_over_hf", mo)):
            res.totals_mb[key] = torch.as_tensor(np.asarray(v, float), dtype=dt)
    return res
