"""Statistical resonance ladders: GOE spacings, Porter-Thomas widths, SLBW cross sections.

Below the resolved-resonance bound a capture cross section is a sum of individual resonances
whose positions and widths nobody can predict for an unmeasured nuclide. What *is* predictable
is their statistics, from four average parameters:

    D0      mean s-wave spacing (all compound spins together)   eV
    S0, S1  s- and p-wave neutron strength functions              dimensionless (~1e-4)
    <Gg>    average radiation width                               eV

and the spin-cutoff parameter sigma^2 that splits D0 among compound spins. A ladder is one
random realisation; an ensemble of ladders is the prediction, and the spread of an observable
over the ensemble (thermal capture, resonance integral) is its irreducible uncertainty.

Conventions (chosen to match ENDF-102 so NJOY reconstructs exactly what this computes):

* spin groups: for orbital l, channel spins s = |I-1/2|, I+1/2 and J = |s-l| .. s+l; a J reached
  by two channel spins has nu_J = 2 neutron channels (Porter-Thomas with 2 dof).
* level density per (J, parity) is proportional to (2J+1) exp(-(J+1/2)^2 / 2 sigma^2), with
  parity equipartition, so 1/D_{l,J} = f(J) / sum_{J' in s-wave} f(J') * 1/D0.
* the strength function is J independent per channel: <Gn^l>_J = S_l * D_{l,J} * nu_J, so that
  S0 = <g Gn0> / D0 over the s-wave ladder (the definition `data.ingest.endf.ladder_stats` uses).
* reduced width Gn^l is at 1 eV: Gn(E) = Gn^l sqrt(E) V_l(E), V_0 = 1, V_1 = rho^2 / (1 + rho^2).
* SLBW (ENDF-102 D.1.1, NAPS=1 so the channel radius AP is used for penetrability and phase).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
from scipy.linalg import eigvalsh_tridiagonal
from scipy.special import roots_genlaguerre

#: k = K_CONST * awri / (awri + 1) * sqrt(E[eV]) in units of 1/(1e-12 cm); pi/k^2 is then barns
K_CONST = 2.196807e-3
THERMAL_EV = 0.0253

#: Above this mean s-wave spacing a statistical ladder says nothing useful. With D0 of tens of
#: keV the nearest resonance to 0.0253 eV is typically many kV away, so the SLBW sum collapses to
#: ~1e-30 b while the real thermal capture of such a nuclide is direct capture into bound states
#: plus the tails of bound levels -- physics a compound-nucleus ladder does not contain. v0 scored
#: 29 such targets (light nuclei and Pb-208, predicted D0 0.1-100 MeV) and they alone took the G3
#: thermal RMS from 0.85 to 5.26. Refusing to answer there is the correct behaviour.
D0_MAX_EV = 1.0e4


class LadderDomainError(ValueError):
    """Average parameters outside the domain where a statistical ladder is meaningful."""


def check_domain(p: AverageParams, *, d0_max: float = D0_MAX_EV) -> None:
    """Raise :class:`LadderDomainError` unless ``p`` is inside the ladder's domain."""
    if not np.isfinite(p.d0_ev) or not p.d0_ev > 0.0:
        raise LadderDomainError(f"D0 = {p.d0_ev!r} eV is not a positive number")
    if p.d0_ev > d0_max:
        raise LadderDomainError(
            f"D0 = {p.d0_ev:.4g} eV > {d0_max:g} eV: no resonance within reach, capture here is "
            "direct, not compound -- the statistical ladder is refused"
        )


def channel_radius(awri: float) -> float:
    """ENDF-102 default channel radius a = 0.123 AWRI^(1/3) + 0.08, in 1e-12 cm."""
    return 0.123 * awri ** (1.0 / 3.0) + 0.08


def wavenumber(e_ev, awri: float):
    return K_CONST * awri / (awri + 1.0) * np.sqrt(np.abs(e_ev))


def penetrability(l: int, rho):
    rho = np.asarray(rho, float)
    if l == 0:
        return rho
    if l == 1:
        return rho**3 / (1.0 + rho**2)
    raise ValueError("only l = 0, 1")


def shift(l: int, rho):
    rho = np.asarray(rho, float)
    return np.zeros_like(rho) if l == 0 else -1.0 / (1.0 + rho**2)


def phase(l: int, rho):
    rho = np.asarray(rho, float)
    return rho if l == 0 else rho - np.arctan(rho)


def spin_weight(j, sigma2: float):
    j = np.asarray(j, float)
    return (2 * j + 1) * np.exp(-((j + 0.5) ** 2) / (2.0 * sigma2))


@dataclass(frozen=True)
class SpinGroup:
    l: int
    j: float
    g: float  # (2J+1) / (2(2I+1))
    nu: int  # number of neutron channels (channel spins) reaching this J
    d_ev: float  # mean spacing of this (l, J) sequence
    gn_red_mean: float  # <Gn^l> reduced width at 1 eV, summed over channels


@dataclass(frozen=True)
class AverageParams:
    """Average resonance parameters of one target."""

    awri: float
    target_spin: float
    d0_ev: float
    s0: float
    gg_ev: float
    s1: float = 0.0
    sigma2: float = 10.0
    ap: float | None = None  # channel radius, 1e-12 cm
    gg_dof: int = 100

    @property
    def radius(self) -> float:
        return self.ap if self.ap is not None else channel_radius(self.awri)

    def spin_groups(self, lmax: int = 1) -> list[SpinGroup]:
        I = abs(self.target_spin)
        s_vals = sorted({abs(I - 0.5), I + 0.5})
        denom_s = 2.0 * (2.0 * I + 1.0)

        def js(l):
            count: dict[float, int] = {}
            for s in s_vals:
                j = abs(s - l)
                while j <= s + l + 1e-9:
                    count[round(j, 1)] = count.get(round(j, 1), 0) + 1
                    j += 1.0
            return count

        f_s = sum(float(spin_weight(j, self.sigma2)) for j in js(0))
        out = []
        for l in range(lmax + 1):
            strength = self.s0 if l == 0 else self.s1
            if l > 0 and not strength > 0:
                continue
            for j, nu in sorted(js(l).items()):
                d = self.d0_ev * f_s / float(spin_weight(j, self.sigma2))
                out.append(SpinGroup(l, j, (2 * j + 1) / denom_s, nu, d, strength * d * nu))
        return out


# --------------------------------------------------------------------------------------------
# sampling
# --------------------------------------------------------------------------------------------


def goe_unit_levels(n: int, rng: np.random.Generator, block: int = 600) -> np.ndarray:
    """``n`` unit-mean-spacing GOE levels, stitched from independent tridiagonal blocks.

    Dumitriu-Edelman beta=1 ensemble; the middle 60% of each block's spectrum is unfolded with
    the Wigner semicircle (radius sqrt(2 beta m)), which leaves spacings with the GOE nearest-
    neighbour law and spectral rigidity inside a block. Blocks are independent, so rigidity is
    lost only beyond ~0.6 * block levels.
    """
    out: list[np.ndarray] = []
    total = 0
    start = 0.0
    while total < n:
        m = block
        diag = rng.normal(0.0, math.sqrt(2.0), m)
        off = np.sqrt(rng.chisquare(np.arange(m - 1, 0, -1) * 1.0))
        ev = eigvalsh_tridiagonal(diag / math.sqrt(2.0), off / math.sqrt(2.0))
        R = math.sqrt(2.0 * m)
        x = np.clip(ev / R, -1, 1)
        # semicircle CDF times m: expected number of levels below x
        cdf = m * (0.5 + (x * np.sqrt(1 - x**2) + np.arcsin(x)) / math.pi)
        lo, hi = 0.2 * m, 0.8 * m
        u = cdf[(cdf > lo) & (cdf < hi)]
        u = u - u[0]
        seg = start + u
        out.append(seg)
        total += seg.size
        # next block starts one Wigner-distributed spacing later
        start = seg[-1] + math.sqrt(-4.0 / math.pi * math.log(1.0 - rng.random()))
    return np.concatenate(out)[:n]


@dataclass
class Ladder:
    awri: float
    target_spin: float
    radius: float
    l: np.ndarray
    j: np.ndarray
    g: np.ndarray
    er: np.ndarray  # eV (may be negative: bound levels)
    gn_red: np.ndarray  # reduced neutron width at 1 eV
    gg: np.ndarray  # eV
    e_min: float = 0.0
    e_max: float = 0.0
    meta: dict = field(default_factory=dict)

    def __len__(self) -> int:
        return int(self.er.size)

    def gn_at(self, e_ev) -> np.ndarray:
        """Neutron width of every resonance at energy e (broadcast: resonances x energies)."""
        e = np.abs(np.atleast_1d(np.asarray(e_ev, float)))
        rho = wavenumber(e, self.awri)[None, :] * self.radius
        base = self.gn_red[:, None] * np.sqrt(e)[None, :]
        v1 = rho**2 / (1.0 + rho**2)
        return np.where(self.l[:, None] == 1, base * v1, base)

    def gn_at_resonance(self) -> np.ndarray:
        """Gn(|Er|): what ENDF MF2 stores in the GN field."""
        e = np.abs(self.er)
        rho = wavenumber(e, self.awri) * self.radius
        v1 = rho**2 / (1.0 + rho**2)
        return self.gn_red * np.sqrt(e) * np.where(self.l == 1, v1, 1.0)


def sample_ladder(
    p: AverageParams,
    e_max: float,
    rng: np.random.Generator,
    *,
    e_min: float | None = None,
    lmax: int = 1,
    spacing: str = "goe",
) -> Ladder:
    """One ladder over [e_min, e_max]; e_min defaults to -e_max/2 bounded by 50 s-wave spacings,
    because negative-energy (bound) levels carry much of a thermal cross section."""
    if e_min is None:
        e_min = -min(0.5 * e_max, 50.0 * p.d0_ev)
    cols = {k: [] for k in ("l", "j", "g", "er", "gn", "gg")}
    for sg in p.spin_groups(lmax):
        n = int(math.ceil((e_max - e_min) / sg.d_ev)) + 2
        if spacing == "goe":
            unit = goe_unit_levels(n, rng)
        elif spacing == "wigner":
            unit = np.cumsum(np.sqrt(-4.0 / math.pi * np.log(1.0 - rng.random(n))))
        elif spacing == "poisson":
            unit = np.cumsum(rng.exponential(1.0, n))
        else:
            raise ValueError(spacing)
        er = e_min + (unit - rng.random()) * sg.d_ev
        er = er[(er >= e_min) & (er <= e_max)]
        k = er.size
        gn = sg.gn_red_mean / sg.nu * rng.chisquare(sg.nu, k)
        gg = p.gg_ev / p.gg_dof * rng.chisquare(p.gg_dof, k)
        for key, val in (("l", np.full(k, sg.l)), ("j", np.full(k, sg.j)), ("g", np.full(k, sg.g)),
                         ("er", er), ("gn", gn), ("gg", gg)):
            cols[key].append(val)
    cat = {k: np.concatenate(v) if v else np.empty(0) for k, v in cols.items()}
    order = np.argsort(cat["er"])
    return Ladder(p.awri, p.target_spin, p.radius, cat["l"][order].astype(int), cat["j"][order],
                  cat["g"][order], cat["er"][order], cat["gn"][order], cat["gg"][order],
                  e_min=e_min, e_max=e_max)


# --------------------------------------------------------------------------------------------
# SLBW cross sections
# --------------------------------------------------------------------------------------------


def _slbw_terms(lad: Ladder, e: np.ndarray, sel: np.ndarray | None = None):
    idx = np.arange(len(lad)) if sel is None else np.flatnonzero(sel)
    l = lad.l[idx][:, None]
    er = lad.er[idx][:, None]
    ae = np.abs(er)
    k = wavenumber(e, lad.awri)[None, :]
    rho = k * lad.radius
    rho_r = wavenumber(ae, lad.awri) * lad.radius
    gn_r = lad.gn_at_resonance()[idx][:, None]
    p_e = np.where(l == 1, rho**3 / (1 + rho**2), rho)
    p_r = np.where(l == 1, rho_r**3 / (1 + rho_r**2), rho_r)
    s_e = np.where(l == 1, -1.0 / (1 + rho**2), 0.0)
    s_r = np.where(l == 1, -1.0 / (1 + rho_r**2), 0.0)
    gn = p_e * gn_r / p_r
    er_p = er + (s_r - s_e) / (2 * p_r) * gn_r
    gg = lad.gg[idx][:, None]
    gam = gn + gg
    den = (e[None, :] - er_p) ** 2 + 0.25 * gam**2
    pk = math.pi / k**2
    g = lad.g[idx][:, None]
    return idx, l, rho, pk, g, gn, gg, gam, den, e[None, :] - er_p


def slbw(lad: Ladder, e_ev, chunk: int = 2_000_000) -> dict[str, np.ndarray]:
    """0 K SLBW capture, elastic and total [b] on ``e_ev`` (positive energies)."""
    e = np.atleast_1d(np.asarray(e_ev, float))
    cap = np.zeros(e.size)
    el_res = np.zeros(e.size)
    step = max(1, chunk // max(len(lad), 1))
    for a in range(0, e.size, step):
        ee = e[a:a + step]
        _, l, rho, pk, g, gn, gg, gam, den, de = _slbw_terms(lad, ee)
        phi = np.where(l == 1, rho - np.arctan(rho), rho)
        sin2 = np.sin(phi) ** 2
        cap[a:a + step] = (pk * g * gn * gg / den).sum(axis=0)
        el_res[a:a + step] = (pk * g * (gn**2 - 2 * gam * gn * sin2 + 2 * de * gn * np.sin(2 * phi))
                              / den).sum(axis=0)
    k = wavenumber(e, lad.awri)
    rho = k * lad.radius
    lset = sorted(set(lad.l.tolist())) or [0]
    pot = sum(4 * math.pi / k**2 * (2 * l + 1) * np.sin(phase(l, rho)) ** 2 for l in lset)
    el = pot + el_res
    return {"capture": cap, "elastic": el, "total": cap + el}


def thermal_capture(lad: Ladder, e_ev: float = THERMAL_EV) -> float:
    return float(slbw(lad, [e_ev])["capture"][0])


def resonance_integral(lad: Ladder, e_cut: float = 0.5, e_top: float | None = None) -> float:
    """integral_{e_cut}^{e_top} sigma_gamma(E) dE / E over the ladder's resonances (SLBW capture has
    no interference, so it is a sum of per-resonance integrals). Narrow resonances well above the
    cutoff use the closed form 2 pi^2 lambdabar^2 g Gn Gg / (Gamma E0); the rest are integrated
    numerically."""
    e_top = lad.e_max if e_top is None else e_top
    er = lad.er
    gn_r = lad.gn_at_resonance()
    gam = gn_r + lad.gg
    narrow = (er > 200 * gam) & (er - e_cut > 50 * gam) & (e_top - er > 50 * gam)
    total = 0.0
    if narrow.any():
        k2 = wavenumber(er[narrow], lad.awri) ** 2
        total += float(np.sum(2 * math.pi**2 / k2 * lad.g[narrow] * gn_r[narrow] * lad.gg[narrow]
                              / (gam[narrow] * er[narrow])))
    # positive resonances far below the range contribute Lorentzian tails ~ (Gamma/distance)^2 and
    # are dropped below e_cut / 3; bound levels are all kept (cheap: one coarse shared grid).
    # A cutoff in units of the mean spacing was tried first and was wrong: the spacing of the
    # MERGED ladder is D0 / (number of spin groups), so it silently dropped the bound levels that
    # carry ~5% of a resonance integral at D0 = 0.4 eV.
    wide = ~narrow & (er < e_top) & ((er <= 0) | (er > e_cut / 3.0))
    # bound levels: a smooth 1/E-weighted tail above the cutoff, one coarse shared log grid
    neg = wide & (er <= 0)
    if neg.any():
        grid = np.geomspace(e_cut, e_top, 400)
        _, _, _, pk, g, gn, gg, _, den, _ = _slbw_terms(lad, grid, neg)
        total += float(np.trapezoid((pk * g * gn * gg / den).sum(axis=0) / grid, grid))
    # positive wide resonances: capture is additive, so each is integrated on its OWN grid --
    # a shared log grid plus a Lorentzian-mapped cluster (E0 + Gamma/2 tan u) around itself.
    # (One union grid for all of them costs n_res^2 clusters: 10 s per ladder at D0 = 0.4 eV.)
    idx = np.flatnonzero(wide & (er > 0))
    if idx.size:
        base = np.geomspace(e_cut, e_top, 1500)
        u = np.tan(np.linspace(-1.565, 1.565, 401))
        for c in range(0, idx.size, 200):
            ii = idx[c:c + 200]
            eg = np.sort(np.concatenate([np.broadcast_to(base, (ii.size, base.size)),
                                         er[ii, None] + 0.5 * gam[ii, None] * u[None, :]], axis=1),
                         axis=1)
            eg = np.clip(eg, e_cut, e_top)
            l = lad.l[ii][:, None]
            k = wavenumber(eg, lad.awri)
            rho = k * lad.radius
            ae = np.abs(er[ii])[:, None]
            rho_r = wavenumber(ae, lad.awri) * lad.radius
            gn_r = gn_r_all = lad.gn_at_resonance()[ii][:, None]
            p_e = np.where(l == 1, rho**3 / (1 + rho**2), rho)
            p_r = np.where(l == 1, rho_r**3 / (1 + rho_r**2), rho_r)
            s_e = np.where(l == 1, -1.0 / (1 + rho**2), 0.0)
            s_r = np.where(l == 1, -1.0 / (1 + rho_r**2), 0.0)
            gn = p_e * gn_r / p_r
            er_p = er[ii][:, None] + (s_r - s_e) / (2 * p_r) * gn_r_all
            gg_ = lad.gg[ii][:, None]
            cap = math.pi / k**2 * lad.g[ii][:, None] * gn * gg_ / ((eg - er_p) ** 2
                                                                     + 0.25 * (gn + gg_) ** 2)
            total += float(np.trapezoid(cap / eg, eg, axis=1).sum())
    return total


# --------------------------------------------------------------------------------------------
# averages (URR)
# --------------------------------------------------------------------------------------------

def _chi2_quadrature(nu: int, n: int = 48) -> tuple[np.ndarray, np.ndarray]:
    """Nodes x and weights w with sum w f(x) = E[f(chi^2_nu / nu)] (generalised Gauss-Laguerre)."""
    y, w = roots_genlaguerre(n, nu / 2.0 - 1.0)
    return 2.0 * y / nu, w / math.gamma(nu / 2.0)


_CHI = {nu: _chi2_quadrature(nu) for nu in (1, 2, 3, 4)}


def average_capture(p: AverageParams, e_ev, lmax: int = 1) -> np.ndarray:
    """Ensemble-average SLBW capture <sigma_gamma>(E) = sum (2 pi^2/k^2) g <Gn Gg / Gamma> / D, with
    the Porter-Thomas width-fluctuation average done by Gauss-Laguerre quadrature over chi^2_nu
    (Gg taken as its mean: 100 dof). No competing inelastic channel."""
    e = np.atleast_1d(np.asarray(e_ev, float))
    k = wavenumber(e, p.awri)
    rho = k * p.radius
    out = np.zeros(e.size)
    for sg in p.spin_groups(lmax):
        v = rho**2 / (1 + rho**2) if sg.l == 1 else np.ones_like(rho)
        gn_mean = sg.gn_red_mean * np.sqrt(e) * v
        x, w = _CHI[sg.nu]
        gn = gn_mean[:, None] * x[None, :]
        fluct = (gn * p.gg_ev / (gn + p.gg_ev)) @ w
        out += 2 * math.pi**2 / k**2 * sg.g * fluct / sg.d_ev
    return out


def average_integral(p: AverageParams, lo: float, hi: float, n: int = 400) -> float:
    """integral <sigma_gamma> dE / E over [lo, hi] (log-spaced trapezoid)."""
    if hi <= lo:
        return 0.0
    e = np.geomspace(lo, hi, n)
    return float(np.trapezoid(average_capture(p, e), np.log(e)))


def ensemble_observables(
    p: AverageParams,
    n_ladders: int,
    rng: np.random.Generator,
    *,
    e_cut: float = 0.5,
    n_res_target: int = 300,
    e_top_max: float = 1e5,
    spacing: str = "goe",
    windows: tuple[tuple[float, float], ...] = (),
    d0_max: float = D0_MAX_EV,
    allow_out_of_domain: bool = False,
) -> dict[str, np.ndarray]:
    """Thermal capture and resonance integral over an ensemble of ladders.

    The explicit ladder runs to e_top = min(e_top_max, max(100 eV, n_res_target * D0)); above it
    the resonance integral uses the ensemble-average capture up to 20 MeV (no inelastic
    competition, so that tail is an upper bound -- it is a few percent of the RI for
    heavy nuclei and reported separately as ``ri_tail``).

    Raises :class:`LadderDomainError` when ``p.d0_ev`` exceeds ``d0_max`` (see :data:`D0_MAX_EV`)
    unless ``allow_out_of_domain``; a caller sampling D0 inside an ensemble passes that flag for
    the individual draws and checks the central value once."""
    if not allow_out_of_domain:
        check_domain(p, d0_max=d0_max)
    # at least 100 eV, but never more than ~3000 s-wave spacings (a D0 drawn at 0.02 eV)
    e_top = min(e_top_max, max(n_res_target * p.d0_ev, min(100.0, 3000.0 * p.d0_ev)))
    tail = average_integral(p, e_top, 2e7)
    th, ri = np.empty(n_ladders), np.empty(n_ladders)
    win = {w: np.full(n_ladders, np.nan) for w in windows}
    for i in range(n_ladders):
        lad = sample_ladder(p, e_top * 1.02, rng, spacing=spacing)
        th[i] = thermal_capture(lad)
        ri[i] = resonance_integral(lad, e_cut, e_top) + tail
        for lo, hi in windows:
            # lethargy-averaged capture over a window; above e_top the ensemble average
            inside = resonance_integral(lad, lo, min(hi, e_top)) if lo < e_top else 0.0
            win[(lo, hi)][i] = (inside + average_integral(p, max(lo, e_top), hi)) / math.log(hi / lo)
    out = {"thermal": th, "ri": ri, "ri_tail": np.full(n_ladders, tail), "e_top": e_top}
    out.update({f"mean_{lo:g}_{hi:g}": v for (lo, hi), v in win.items()})
    return out
