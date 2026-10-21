"""ALPHAENTR: entrance-only alpha optical potential for alpha-INDUCED runs (INCOGNITA_ALPHAENTR; default "6" since E1PROMO 2026-10-19, hw:0.77 from HWA770PROMO 10-18 to 10-19,
deck keyword `alphaentr 0` = OFF = previous production).

The deck's `alphaomp 8` (Avrigeanu 1994, far-out volume W) is chosen for alpha EMISSION ((n,a), ALPHAINV). On alpha-induced
data it over-absorbs below the Coulomb barrier (CPALPHA). This switch changes only the INCIDENT alpha channel of an alpha
projectile run (`Cascade.incident`: T_lj, lmaxinc, sigma_reac, xscoupled); every inverse / emission channel keeps the deck's
`alphaomp`. Neutron and proton projectile runs never reach it (k0 != 6), so they are bitwise unchanged.

* "" / "0" / "off" -> off; unset -> DEFAULT ("6"; deck `alphaentr hw:0.77` = previous production).
* "6"   -> E1: the incident alpha channel is solved with alphaomp 6 (Avrigeanu 2014, TALYS default).
* "mix:<x>" -> ALPHAMIX2: T_inc = T6^x T_deck^(1-x) per (l, j) with one constant x in [0, 1] (same blend code as "bar";
           x = 1 is "6" up to the blend arithmetic, x = 0 is the deck).
* "hw" / "hw:<a>" -> ALPHABAR2: ao6 share confined to the tunnelling region, s(E) = a (1 - T_HW(E)),
           T_HW = 1 / (1 + exp(2 pi (V_B - E_cm) / hbar omega)) (Hill-Wheeler l = 0 transmission of the same engine barrier as
           "bar"; hbar omega = hbar sqrt(|V''(r_B)| / mu) from its curvature at the top). T_inc = T6^s T_deck^(1-s) (blend as
           "bar"). a = 1 by default (no knob); "hw:<a>" only for the A0-LTO amplitude refit allowed by the ALPHABAR2 prereg.
* "bar" -> E2: T_inc = T6^(1-w) T_deck^w per (l, j), w = logistic((E_cm - V_B) / (0.1 V_B)), V_B = the top of the engine's
           own l = 0 alpha + target barrier (real alphaomp-6 potential + uniform-sphere Coulomb, `optical_potential`) at the
           incident energy. sigma_reac = sigma_deck * sum(2l+1) T_l(blend) / sum(2l+1) T_l(deck); xscoupled blended in log.

Consequence by construction: `compound.target._exact_incident_channel` puts the incident T on the target ground-state alpha
exit row, so compound-elastic alpha re-emission to the ground state follows the entrance potential (reciprocity); every other
alpha exit state keeps the deck potential. The DWBA direct alpha' to collective levels keeps the deck potential (not switched).
"""

from __future__ import annotations

import math
import os
from dataclasses import replace

import torch

ENV = "INCOGNITA_ALPHAENTR"
WIDTH = 0.1  # logistic width in units of V_B (fixed in the brief before any run)
_RGRID = torch.arange(2.0, 30.0, 0.01, dtype=torch.float64)


DEFAULT = "6"  # E1PROMO: ALPHAREOPEN arm E1 replaces HWA770 (hw:0.77)


def mode(options=None) -> str | None:
    """Resolved mode: explicit deck keyword `alphaentr`, else env INCOGNITA_ALPHAENTR (set to "" / "0" / "off" = OFF), else DEFAULT."""
    if options is not None and hasattr(options, "is_explicit") and options.is_explicit("alphaentr"):
        v = str(getattr(options, "alphaentr", DEFAULT))
    else:
        v = os.environ.get(ENV, DEFAULT)
    v = v.strip().lower()
    if v in ("", "0", "n", "no", "off"):
        return None
    if v.startswith(("mix:", "hw:")):
        x = float(v.split(":", 1)[1])
        if not 0.0 <= x <= 1.0:
            raise ValueError(f"{ENV}={v!r}: mix weight outside [0, 1]")
        return v
    if v not in ("6", "bar", "hw"):
        raise ValueError(f"{ENV}={v!r}: one of 6, bar, hw, hw:<a>, mix:<x>")
    return v


def active(k0: int, options=None) -> bool:
    return int(k0) == 6 and mode(options) is not None


def options6(options):
    return replace(options, alphaomp=6)


def barrier_mev(Zt: int, At: int, e_lab_mev: float, options, params) -> float:
    """Top of the l = 0 alpha + (Zt, At) barrier [MeV, c.m.] from the alphaomp-6 real potential + Coulomb, as the
    incident solver builds them (`schrodinger.optical_potential`, radii x m_target^(1/3))."""
    return barrier_top(Zt, At, e_lab_mev, options, params)[0]


def barrier_top(Zt: int, At: int, e_lab_mev: float, options, params) -> tuple[float, float]:
    """(V_B [MeV], V''(r_B) [MeV/fm^2]) of the l = 0 barrier of `barrier_mev`; curvature by the central difference on _RGRID."""
    from physics.hf.omp.inverse import _ported_omp
    from physics.hf.omp.schrodinger import nucleus_mass_amu, optical_potential

    o6 = options6(options)
    p = _ported_omp(Zt, At, Zt, At, 6, torch.tensor([float(e_lab_mev)], dtype=torch.float64), o6, params)
    m_t = torch.tensor([nucleus_mass_amu(Zt, At)], dtype=torch.float64)
    central, _, coul = optical_potential(p, m_t, _RGRID, float(2 * Zt))
    v = (central.real + coul)[0]
    i = int(torch.argmax(torch.where(_RGRID > 4.0, v, torch.full_like(v, -1e30))))
    dr = float(_RGRID[1] - _RGRID[0])
    return float(v[i]), float((v[i + 1] - 2.0 * v[i] + v[i - 1]) / dr**2)


HBARC = 197.3269804  # MeV fm
AMU = 931.49410242  # MeV


def hw_share(Zt: int, At: int, e_lab_mev: float, options, params, amp: float = 1.0) -> tuple[float, float, float, float]:
    """(deck weight w = 1 - amp (1 - T_HW), E_cm, V_B, hbar omega): the ao6 share is the l = 0 tunnelling (non-transmission)
    probability of the engine's own barrier; -> 0 above V_B, -> amp deep below."""
    from physics.hf.omp.schrodinger import PARMASS_AMU, nucleus_mass_amu

    m_t = nucleus_mass_amu(Zt, At)
    e_cm = float(e_lab_mev) * m_t / (m_t + PARMASS_AMU[6])
    vb, d2 = barrier_top(Zt, At, e_lab_mev, options, params)
    mu = m_t * PARMASS_AMU[6] / (m_t + PARMASS_AMU[6]) * AMU
    hw = HBARC * math.sqrt(abs(d2) / mu)
    x = 2.0 * math.pi * (vb - e_cm) / hw
    t_hw = 1.0 / (1.0 + math.exp(max(min(x, 700.0), -700.0)))
    return 1.0 - amp * (1.0 - t_hw), e_cm, vb, hw


def weight(Zt: int, At: int, e_lab_mev: float, options, params) -> tuple[float, float, float]:
    """(w, E_cm, V_B): w -> 1 (deck potential) above the barrier, -> 0 (alphaomp 6) below."""
    from physics.hf.omp.schrodinger import PARMASS_AMU, nucleus_mass_amu

    m_t = nucleus_mass_amu(Zt, At)
    e_cm = float(e_lab_mev) * m_t / (m_t + PARMASS_AMU[6])
    vb = barrier_mev(Zt, At, e_lab_mev, options, params)
    x = (e_cm - vb) / (WIDTH * vb)
    return 1.0 / (1.0 + math.exp(-max(min(x, 700.0), -700.0))), e_cm, vb


def _geo(a: torch.Tensor, b: torch.Tensor, w: float) -> torch.Tensor:
    pos = (a > 0) & (b > 0)
    la = torch.log(torch.where(pos, a, torch.ones_like(a)))
    lb = torch.log(torch.where(pos, b, torch.ones_like(b)))
    return torch.where(pos, torch.exp((1.0 - w) * la + w * lb), (1.0 - w) * a + w * b)


LOG: list[dict] = []  # per-energy record (mode, E, w, E_cm, V_B, sigma_reac arms) for the run's capture


def incident(cas, e_inc_mev: float):
    """The switched incident channel for `cas` (a `feeding.Cascade` with k0 = 6)."""
    m = mode(cas.options)
    o6 = options6(cas.options)
    inc6 = cas._incident_with(e_inc_mev, o6, tag="_ae6")
    x6 = cas.__dict__.get("_xscoupled_ae6", {}).get(float(e_inc_mev))
    rec = dict(mode=m, e=float(e_inc_mev), alphaomp_deck=int(cas.options.alphaomp), sr6=float(inc6.sigma_reac_mb[0]))
    if m == "6":
        out, xs = inc6, x6
    else:
        inc8 = cas._incident_with(e_inc_mev, cas.options, tag="_ae8")
        x8 = cas.__dict__.get("_xscoupled_ae8", {}).get(float(e_inc_mev))
        if m.startswith("mix:"):  # ALPHAMIX2: constant ao6 share x -> deck weight w = 1 - x
            w, ecm, vb = 1.0 - float(m[4:]), float("nan"), float("nan")
        elif m.startswith("hw"):  # ALPHABAR2: ao6 share = amp (1 - T_HW)
            w, ecm, vb, hw = hw_share(cas.Zt, cas.At, e_inc_mev, cas.options, cas.params, float(m[3:]) if ":" in m else 1.0)
            rec["hbar_omega"] = hw
        else:
            w, ecm, vb = weight(cas.Zt, cas.At, e_inc_mev, cas.options, cas.params)
        t_l = _geo(inc6.t_l, inc8.t_l, w)
        tjl = _geo(inc6.tjl_inc, inc8.tjl_inc, w)
        lw = (2.0 * torch.arange(t_l.shape[-1], dtype=t_l.dtype) + 1.0)
        s8 = (lw * inc8.t_l).sum(-1)
        ratio = torch.where(s8 > 0, (lw * t_l).sum(-1) / torch.where(s8 > 0, s8, torch.ones_like(s8)), torch.ones_like(s8))
        lm = torch.maximum(torch.as_tensor(inc6.lmax), torch.as_tensor(inc8.lmax)) if inc6.lmax is not None else inc8.lmax
        out = replace(inc8, tjl_inc=tjl, t_l=t_l, sigma_reac_mb=inc8.sigma_reac_mb * ratio, lmax=lm)
        xs = None
        if x6 is not None and x8 is not None:
            xs = _geo(torch.as_tensor(x6, dtype=torch.float64), torch.as_tensor(x8, dtype=torch.float64), w)
        rec.update(w=w, e_cm=ecm, v_b=vb, sr8=float(inc8.sigma_reac_mb[0]))
    rec["sr"] = float(out.sigma_reac_mb[0])
    if xs is not None:
        cas.__dict__.setdefault("_xscoupled", {})[float(e_inc_mev)] = xs
    LOG.append(rec)
    return out
