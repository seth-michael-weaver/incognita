"""NATIVEX2 lever `dwba`: `ecis.dwba.dwba_case` -- the discrete levels and the giant resonances of
one incident energy -- with the distorted waves, their normalisation, the overlap integrals and
the level sums in one compiled call (`native/nx2_dwba.c`, `nx2_dwba_levels`).

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.
ECIS-06 (`ecist.f`) is by J. Raynal and ships inside the TALYS repository under its MIT license.

Task: NATIVEX2 (the speed work; no physics of its own). Acceptance test: `tests/hf/test_nx2_dwba.py`
(against `dwba_case` with the lever off) and the G-NATIVEX2 closeness gate.

What changes against `dwba_cross_sections` (the physics is that function's, statement for
statement; see its module docstring):

* **One deck.** `dwba_case` made two calls with the same potential and grid, one for the levels
  and one for the giant resonances, and each integrated the entrance channel again. The grid
  (`ecis_grid`) reads only the entrance channel, `njmax` only the incident energy, and the
  channels beyond `njmax + lambda + 1` carry no Clebsch-Gordan weight, so both lists are one
  solve with `lmax = njmax + (largest solved lambda) + 1`. A call with nothing to solve returns
  its zeros before the grid is built.
* **No (levels, channels, radii) arrays.** Only the entrance channels and exit channels a
  non-zero weight reads are integrated, each exit level's waves are folded into its sum as soon
  as they are normalised.
* **Coulomb functions.** For neutral channels (every incident neutron) `H+` at the matching radius
  is computed in the kernel by `coulomb_functions`' own eta = 0 recurrences; a charged row takes
  `dwba_setb.exit_waves` from Python.
* **Scalars in numpy.** The card quantisation (`ecis_card_value`/`ecis_card_energy`), the
  channel kinematics (`solver.channel_kinematics`), the grid (`ecis_grid`), the potential
  (`optical_potential`) and the form factor (`formfactor.derivative_form_factor`) of this one
  energy are the same formulas on floats and one radial numpy row instead of torch calls on
  one-element tensors; `tests/hf/test_nx2_dwba.py` pins each against its torch function.

The kernel is held to closeness with the torch path (sums in loop order, the Numerov coefficients
divided first, libm instead of torch transcendentals, one larger `lmax` in the continued
fraction's starting order), not to bits.

Selection, per call: `nx2.kernel(..., lever="dwba")` is None (no build, `HF_NX2=0`,
`HF_NX2_DWBA=0`) or autograd is on -> `dwba_case`'s torch path.

TALYS: directecis.f90:1 (directecis), directread.f90:1 (directread), ecist.f:18285 (inri)
Test: tests/hf/test_nx2_dwba.py
"""

from __future__ import annotations

import math
from functools import lru_cache

import numpy as np
import torch
from torch import Tensor

from physics.hf.core.tensors import DTYPE
from physics.hf.core.units import MB_PER_FM2
from physics.hf.ecis.formfactor import DWBA_PARTS
from physics.hf.native import nx2, setup_c
from physics.hf.omp import schrodinger as _s

__all__ = ["case_cross_sections"]

SQRT4PI = math.sqrt(4.0 * math.pi)
_FIELDS = _s._FIELDS  # the 19 OMP columns in `optical_potential`'s order
_PART_COLS = {"v": ("v_mev", "rv_fm", "av_fm"), "w": ("w_mev", "rw_fm", "aw_fm"),
              "vd": ("vd_mev", "rvd_fm", "avd_fm"), "wd": ("wd_mev", "rwd_fm", "awd_fm")}


def _kernel():
    # CENGSETUP: libsetup's `cs_dwba_levels` when built (native/setup.c, the same bits)
    return setup_c.swap("nx2_dwba_levels", nx2.kernel(
        "nx2_dwba_levels",
        [nx2.I64, nx2.I64, nx2.DBL, nx2.P, nx2.P, nx2.P, nx2.I64, nx2.P, nx2.P, nx2.P, nx2.DBL,
         nx2.P, nx2.I64, nx2.P, nx2.P, nx2.P],
        nx2.INT, lever="dwba"))


def _es10_3(x):
    """`schrodinger._round_es10_3` on floats or a numpy array."""
    x = np.asarray(x, dtype=np.float64)
    ax = np.where(x == 0, 1.0, np.abs(x))
    e = np.floor(np.log10(ax))
    m = np.round(x / 10.0 ** e * 1.0e3) / 1.0e3
    return np.where(x == 0, x, m * 10.0 ** e)


def _card_value(x):
    """`ecis_card_value` (f10.5, es10.3 at |x| >= 1000) on a float or numpy array, the forward
    value of its straight-through form `x + (y - x)`.

    TALYS: ecisinput.f90:1 (ecisinput)
    Test: tests/hf/test_nx2_dwba.py
    """
    x = np.asarray(x, dtype=np.float64)
    if not _s.CARD_ROUNDING:
        return x
    big = np.abs(x) >= 1000.0
    y = np.round(x * 1.0e5) / 1.0e5
    if big.any():
        y = np.where(big, _es10_3(x), y)
    return x + (y - x)


def _card_energy(e: float) -> float:
    """`ecis_card_energy` on one float.

    TALYS: ecisinput.f90:1 (ecisinput)
    Test: tests/hf/test_nx2_dwba.py
    """
    if not _s.CARD_ROUNDING:
        return e
    y = float(np.round(e * 1.0e5) / 1.0e5) if e >= 0.01 else float(_es10_3(e))
    return e + (y - e)


@lru_cache(maxsize=16)
def _masses(Z: int, A: int, particle: int, rounding: bool) -> tuple[float, float]:
    m_proj, m_targ = float(_s.PARMASS_AMU[particle]), _s.nucleus_mass_amu(Z, A)
    if rounding:
        m_proj, m_targ = float(_card_value(m_proj)), float(_card_value(m_targ))
    return m_proj, m_targ


def _kinematics(e: float, m1: float, m2: float, z_prod: float, e_lev: np.ndarray):
    """`solver.channel_kinematics` for one incident energy: (k, kappa2, eta) per channel
    (entrance first) and mu_coef, the same operations in the same order on floats.

    TALYS: ecist.f:5464 (khco)
    Test: tests/hf/test_nx2_dwba.py
    """
    cm = _s.ECIS_CM_MEV
    ecm1 = cm * (math.sqrt((m1 + m2) ** 2 + 2.0 * m2 * e / cm) - m1 - m2)
    amr = ecm1 / cm + m1 + m2
    ecm = ecm1 - np.concatenate([[0.0], e_lev])
    x = ecm / cm
    k2 = (0.125 * _s.ECIS_CK * ecm * (x + 2.0 * m1 + 2.0 * m2) * (x + 2.0 * m1)
          * (x + 2.0 * m2) / (amr * amr))
    amrd = (amr ** 4 - (m1 ** 2 - m2 ** 2) ** 2) / (4.0 * (amr * amr * amr))
    k = np.sqrt(np.abs(k2))
    eta = (cm * _s.ECIS_CCZ_MEV_FM * amrd * z_prod / np.maximum(k, 1.0e-30)
           / _s.ECIS_CHB_MEV_FM ** 2)
    return k, k2, eta, _s.ECIS_CK * amrd, ecm1


def _omp_row(omp) -> dict[str, float]:
    """The 19 OMP columns of the single-row `omp`, card-quantised."""
    raw = [float(torch.as_tensor(getattr(omp, f), dtype=DTYPE).reshape(-1)[0]) for f in _FIELDS]
    q = _card_value(np.asarray(raw)).tolist()
    return dict(zip(_FIELDS, q, strict=True))


def _grid(q: dict[str, float], m_targ: float, k0: float, ecm0: float) -> tuple[float, int]:
    """`ecis_grid` for the entrance channel: (h, ism).

    TALYS: ecist.f:3627 (lect)
    Test: tests/hf/test_nx2_dwba.py
    """
    am3 = m_targ ** (1.0 / 3.0)
    w3 = k0 / (_s.ECIS_ACONV * ecm0)
    rm, w2 = 0.0, 1.0e21
    for d, r0, a in _s._POTS:
        dep = abs(q[d])
        if dep != 0:
            rm = max(rm, q[r0] * am3 + math.log(w3 * dep) * q[a])
            w2 = min(w2, q[a])
    rm = max(rm, q["rc_fm"] * am3)
    h = min(w2 / 2.0, 0.5 / k0)
    ism = max(int(math.floor(rm / h + 0.5)), 4)
    return rm / ism, ism


def _ws(r: np.ndarray, R: float, a: float) -> tuple[np.ndarray, np.ndarray]:
    f = 1.0 / (1.0 + np.exp((r - R) / a))  # sigmoid(-x)
    return f, f * (1.0 - f)


def _potential(q, m_targ: float, r: np.ndarray, z_prod: float, deformation_length: bool,
               parts: tuple[str, ...]):
    """`optical_potential` (central, spin-orbit factor, Coulomb) and
    `derivative_form_factor` on one radial row, as (re, im) numpy pairs.

    TALYS: ecist.f:12950 (wosa), ecist.f:11889 (rotp)
    Test: tests/hf/test_nx2_dwba.py
    """
    am3 = m_targ ** (1.0 / 3.0)

    def ws(d, r0, a):
        return _ws(r, q[r0] * am3, max(q[a], 1.0e-6))

    fv, _ = ws("v_mev", "rv_fm", "av_fm")
    fw, _ = ws("w_mev", "rw_fm", "aw_fm")
    _, gvd = ws("vd_mev", "rvd_fm", "avd_fm")
    _, gwd = ws("wd_mev", "rwd_fm", "awd_fm")
    c_re = -q["v_mev"] * fv - 4.0 * q["vd_mev"] * gvd
    c_im = -q["w_mev"] * fw - 4.0 * q["wd_mev"] * gwd
    _, gvso = ws("vso_mev", "rvso_fm", "avso_fm")
    _, gwso = ws("wso_mev", "rwso_fm", "awso_fm")
    so_re = _s.SPIN_ORBIT_FACTOR * (q["vso_mev"] * (-gvso / max(q["avso_fm"], 1.0e-6) / r))
    so_im = _s.SPIN_ORBIT_FACTOR * (q["wso_mev"] * (-gwso / max(q["awso_fm"], 1.0e-6) / r))
    if z_prod == 0:
        coul = np.zeros_like(r)
    else:
        rc = q["rc_fm"] * am3
        e2z = _s.ECIS_CCZ_MEV_FM * z_prod
        rcs = max(rc, 1.0e-6)
        coul = np.where(r < rc, e2z / (2.0 * rcs) * (3.0 - (r / rcs) ** 2), e2z / r)
    w_re = np.zeros_like(r)
    w_im = np.zeros_like(r)
    for name in parts:
        d, r0, a = _PART_COLS[name]
        R = q[r0] * am3
        aa = max(q[a], 1.0e-6)
        f, g = _ws(r, R, aa)
        s = 1.0 if deformation_length else R
        if name in ("v", "w"):
            t = s * q[d] * g / aa
        else:
            t = 4.0 * s * q[d] * g * (1.0 - 2.0 * f) / aa
        if name in ("v", "vd"):
            w_re = w_re + t
        else:
            w_im = w_im + t
    return (c_re + coul, c_im), (so_re, so_im), (w_re, w_im)


def _simpson(n: int, h: float) -> np.ndarray:
    """`dwba._simpson_weights` in numpy."""
    w = np.zeros(n + 1)
    m = n if n % 2 == 0 else n - 1
    w[0] += 1.0
    w[m] += 1.0
    w[1:m:2] += 4.0
    w[2:m:2] += 2.0
    w *= h / 3.0
    if m != n:
        w[n - 1] += h / 2.0
        w[n] += h / 2.0
    return w


def case_cross_sections(
    omp,
    case,
    *,
    refine: int = 4,
    particle: int = 1,
    njmax: int | None = None,
    numl: int = 60,
    parts: tuple[str, ...] = DWBA_PARTS,
    ecis_rounding: bool = True,
) -> tuple[Tensor, Tensor] | None:
    """`dwba_case(omp, case, refine=refine, ...)`: (discrete, giant-resonance) cross sections in
    mb, or None when the kernel is unavailable or autograd is on.

    TALYS: directecis.f90:1 (directecis), directread.f90:1 (directread)
    Test: tests/hf/test_nx2_dwba.py
    """
    if torch.is_grad_enabled():
        return None
    fn = _kernel()
    if fn is None:
        return None
    from physics.hf.ecis.dwba_setb import cg_weights, exit_waves

    groups = [(case.e_mev, case.spin, case.parity, case.vibbeta)]
    has_gr = case.gr_which.numel() > 0
    if has_gr:
        groups.append((case.gr_e_mev, case.gr_spin, case.gr_parity, case.gr_vibbeta))

    def col(i, dtype=np.float64):
        return np.concatenate([np.asarray(torch.as_tensor(g[i]).reshape(-1), dtype=dtype)
                               for g in groups])

    e_lev, spins, pars, betas = col(0), col(1), col(2, np.int64), col(3)
    n_disc, n_tot = int(torch.as_tensor(case.e_mev).numel()), int(e_lev.shape[0])
    Z, A = case.Z, case.A
    rounding = bool(ecis_rounding and _s.CARD_ROUNDING)
    m_proj, m_targ = _masses(Z, A, particle, rounding)
    e_lab = float(case.e_inc_mev)
    if ecis_rounding:
        e_lab = _card_energy(e_lab)
        e_lev = _card_value(e_lev)
    z_prod = float(_s.PARZ[particle] * Z)
    spin = float(_s.PARSPIN[particle])
    k, kappa2, eta, mu, ecm0 = _kinematics(e_lab, m_proj, m_targ, z_prod, e_lev)

    # the level sum's `continue` test (dwba_setb.live_levels), over both lists
    live, lams = [], []
    for b in range(n_tot):
        lam = int(round(float(spins[b])))
        if int(pars[b]) != (-1) ** lam or betas[b] / SQRT4PI == 0.0 or kappa2[b + 1] <= 0.0:
            continue
        live.append(b)
        lams.append(lam)
    xs = np.zeros(n_tot)
    if live:
        if njmax is None:
            x = 2.4 * 1.25 * (A ** (1.0 / 3.0)) * 0.22 * math.sqrt(m_proj * e_lab)
            njmax = min(max(20, int(x)), numl)
        lmax = njmax + max(lams) + 1
        q = _omp_row(omp)
        h, ism = _grid(q, m_targ, float(k[0]), ecm0)
        h = h / refine
        n = ism * refine
        r = h * np.arange(0, n + 1, dtype=np.float64)
        r[0] = h  # column 0 multiplies u(0) = 0
        (d_re, d_im), (so_re, so_im), (w_re, w_im) = _potential(
            q, m_targ, r, z_prod, case.deformation_length, parts)
        ls, js = [], []
        for orb in range(lmax + 1):
            for jj in (orb - 0.5, orb + 0.5):
                if jj >= 0:
                    ls.append(orb)
                    js.append(jj)
        l_np = np.asarray(ls, dtype=np.int64)
        lf = l_np.astype(np.float64)
        jf = np.asarray(js)
        ls2 = jf * (jf + 1.0) - lf * (lf + 1.0) - 0.75
        nlj = int(l_np.shape[0])
        f_np = np.empty((nlj, n + 1, 2))
        f_np[:, :, 0] = (lf * (lf + 1.0))[:, None] / (r * r)[None, :] + mu * (
            d_re[None, :] + ls2[:, None] * so_re[None, :])
        f_np[:, :, 1] = mu * (d_im[None, :] + ls2[:, None] * so_im[None, :])
        y1 = np.ascontiguousarray(h ** (lf + 1.0))
        sel = [0] + [b + 1 for b in live]
        nk = len(sel)
        k2_np = np.ascontiguousarray(kappa2[sel])
        eta_np = np.ascontiguousarray(eta[sel])
        rm = h * (n - 1)
        hp_np = None
        if bool((eta_np != 0.0).any()):
            lt = torch.from_numpy(l_np)
            hp, dhp = exit_waves(torch.from_numpy(k2_np), torch.from_numpy(eta_np), lt, rm, nk,
                                 nlj)
            hp_np = np.ascontiguousarray(np.stack(
                [hp.real.numpy(), hp.imag.numpy(), dhp.real.numpy(), dhp.imag.numpy()], axis=-1))
        wt = _simpson(n, h)
        ww_np = np.empty((n + 1, 2))
        ww_np[:, 0] = w_re * wt
        ww_np[:, 1] = w_im * wt
        ww_np[0] = 0.0  # r = 0 carries no weight; u(0) = 0 anyway
        keys: dict[tuple[int, int], int] = {}
        tabs, tab_of = [], []
        for b, lam in zip(live, lams, strict=True):
            key = (lam, int(pars[b]))
            if key not in keys:
                keys[key] = len(tabs)
                tabs.append(cg_weights(lam, key[1], int(lmax), int(njmax), spin).numpy())
            tab_of.append(keys[key])
        tab_np = np.ascontiguousarray(np.stack(tabs))
        tab_of_np = np.asarray(tab_of, dtype=np.int64)
        out = np.zeros(nk - 1)
        rc = fn(nlj, n, h, nx2.ptr(f_np), nx2.ptr(y1), nx2.ptr(l_np), nk, nx2.ptr(k2_np),
                nx2.ptr(eta_np), nx2.ptr(hp_np), rm, nx2.ptr(ww_np), len(tabs), nx2.ptr(tab_np),
                nx2.ptr(tab_of_np), nx2.ptr(out))
        if rc != 0:
            return None
        k0 = float(k[0])
        fac = math.pi / k0 ** 2 * MB_PER_FM2
        for i, b in enumerate(live):
            d = float(betas[b]) / SQRT4PI
            pre = (mu * d) ** 2 / (4.0 * float(k[b + 1]) * k0)
            xs[b] = fac * pre * float(out[i])
    xs_t = torch.from_numpy(xs)
    if not has_gr:
        return xs_t, torch.zeros(0, dtype=DTYPE)
    return xs_t[:n_disc].clone(), xs_t[n_disc:].clone()
