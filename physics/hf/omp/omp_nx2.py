"""NATIVEX2 lever `omp`: the inverse-channel and incident-channel optical-model solves and the
optical-model parameters without per-element torch dispatch.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.
ECIS-06 (`ecist.f`) is by J. Raynal and ships inside the TALYS repository under its MIT license.

Task: NATIVEX2 (the speed work; no physics of its own). Acceptance test: `tests/hf/test_nx2_omp.py`
(against the torch paths with the lever off) and the G-NATIVEX2 closeness gate.

What it replaces (the physics is that code's, statement for statement):

* **One compiled solve per (nucleus, particle).** `schrodinger.solve_spherical` -- card rounding,
  ECIS kinematics, `ecis_grid`, `optical_potential`, the modified Numerov, `coulomb_functions`,
  `_match_ecis`, `cross_sections` -- is `nx2_omp_job` (`native/nx2_omp.c`). Every Coulomb call keeps
  the call-wide quantities of the torch call (continued-fraction starting order, inward Numerov
  step count), so batching the particles of a target changes nothing.
* **Only what `_transmission_build` reads.** `inverse_kept` solves an emission energy only inside
  `[ebegin(type), eendmax(type)]` (outside it the caller zeroes `Tjl`, and `preeq.chain` zeroes
  `xsreac`) and writes `T_lj` only up to ECIS's per-energy l cap (`inverse._clip_to_njmax`); the
  partial waves above the cap are still solved for the reaction cross section unless the capped
  one is already below 1e-14 of the sum.
* **The OMP parameters on floats.** `parameters.omp_parameters` for the configurations a chart
  run uses (KD03 or a local parameter file, Soukhovitskii, the Watanabe composites, the
  Avrigeanu 2014 alpha) is `omp_columns`: the energy-independent `omppar` once per nucleus (per
  `Options` object), the `optical*` formulas in numpy (or Python floats for one energy). Anything
  else -- a tabulated or RIPL potential, the 1 GeV join, `ompadjustE` ranges, alternative
  deuteron or McFadden-Satchler/Nolte alphas, a parameter on the autograd graph -- returns None
  and the torch path runs.
* **The pieces other stages call.** `card`, `grid`, `coulomb`: `ecis_card_value` /
  `ecis_card_energy`, `ecis_grid`, `coulomb_functions` on the no-grad path.

Held to closeness with the torch path (libm's exp/log/pow instead of torch's, sums in loop order,
each energy's own radial step count), not to bits.

Selection, per call: `nx2.kernel(..., lever="omp")` is None (no build, `HF_NX2=0`,
`HF_NX2_OMP=0`) or an input carries `requires_grad` -> the torch path.

TALYS: inverseecis.f90:1 (inverseecis), incidentecis.f90:1 (incidentecis), optical.f90:1 (optical),
omppar.f90:1 (omppar)
Test: tests/hf/test_nx2_omp.py
"""

from __future__ import annotations

import math
from functools import lru_cache

import numpy as np
import torch
from torch import Tensor

from physics.hf.core.tensors import DTYPE
from physics.hf.native import nx2, setup_c

__all__ = ["card", "grid", "coulomb", "solve", "inverse_kept", "omp_columns", "omp_parameters"]

_COLUMNS = (
    "v_mev", "rv_fm", "av_fm", "w_mev", "rw_fm", "aw_fm", "vd_mev", "rvd_fm", "avd_fm",
    "wd_mev", "rwd_fm", "awd_fm", "vso_mev", "rvso_fm", "avso_fm", "wso_mev", "rwso_fm",
    "awso_fm", "rc_fm",
)  # fmt: skip


def _kernel(name: str):
    sig = {
        "nx2_omp_card": ([nx2.I64, nx2.I64, nx2.P, nx2.P], None),
        "nx2_omp_grid": ([nx2.I64, nx2.I64, nx2.P, nx2.DBL, nx2.P, nx2.P, nx2.P, nx2.P, nx2.P],
                         None),
        "nx2_omp_coulomb": ([nx2.I64, nx2.I64] + [nx2.P] * 6, nx2.INT),
        "nx2_omp_job": ([nx2.I64, nx2.I64, nx2.I64, nx2.DBL, nx2.DBL, nx2.DBL, nx2.DBL, nx2.I64]
                        + [nx2.P] * 4 + [nx2.I64, nx2.P, nx2.P], nx2.INT),
    }[name]
    fn = setup_c.swap(name, nx2.kernel(name, sig[0], sig[1], lever="omp"))
    if fn is not None and not _HANDED[0]:
        _hand_over()
    return fn


_HANDED = [False]


def _hand_over() -> None:
    """Give `nx2_omp_job` the inward-Numerov kernel `schrodinger` already runs
    (`native.numerov_inward`, hf_numerov_inward), so the two paths share its arithmetic; without
    that library the job uses its own copy of the recurrence."""
    import ctypes

    from physics.hf import native

    _HANDED[0] = True
    lib = native._load() if native.available() else None
    base = nx2.kernel("nx2_omp_set_numerov", [nx2.P], None, lever="omp")
    if base is None or lib is None:
        return
    hf = ctypes.cast(lib.hf_numerov_inward, ctypes.c_void_p).value
    base(hf)
    # CENGSETUP: libsetup's copy of the job gets `cs_numerov_inward`, the bits of
    # hf_numerov_inward on the job's equal-count columns, eight lanes at a time
    fast = setup_c.swap("nx2_omp_set_numerov", base)
    if fast is not base:
        addr = setup_c.numerov_inward_address()
        fast(addr if addr is not None else hf)


def enabled() -> bool:
    """Whether the lever runs (a `libnx2` build with the omp kernels, `HF_NX2_OMP` not 0)."""
    return _kernel("nx2_omp_job") is not None


def _np(x) -> np.ndarray:
    return np.ascontiguousarray(np.asarray(x, dtype=np.float64))


def _grad(*xs) -> bool:
    return any(isinstance(x, Tensor) and x.requires_grad for x in xs)


# ------------------------------------------------------------------------------ small pieces
def card(x: Tensor, energy: bool) -> Tensor | None:
    """`ecis_card_energy(x)` (energy) or `ecis_card_value(x)` with card rounding on, or None.

    TALYS: ecisinput.f90:1 (ecisinput)
    Test: tests/hf/test_nx2_omp.py
    """
    if not isinstance(x, Tensor) or x.requires_grad or x.dtype != DTYPE or x.device.type != "cpu":
        return None
    fn = _kernel("nx2_omp_card")
    if fn is None:
        return None
    a = np.ascontiguousarray(x.numpy())
    out = np.empty_like(a)
    fn(a.size, 1 if energy else 0, nx2.ptr(a), nx2.ptr(out))
    return torch.from_numpy(out).reshape(x.shape)


def _param_cols(p, n_e: int) -> np.ndarray | None:
    """The 19 OMP fields of `p` as a (19, n_e) float64 array (scalars broadcast), or None when one
    is on the autograd graph."""
    cols = np.empty((19, n_e), dtype=np.float64)
    for i, f in enumerate(_COLUMNS):
        v = getattr(p, f)
        if isinstance(v, Tensor):
            if v.requires_grad:
                return None
            v = v.detach().numpy()
        cols[i] = np.asarray(v, dtype=np.float64).reshape(-1)
    return cols


def grid(p, m_targ_amu: float, kin, rounding: bool):
    """`ecis_grid(p, m_targ_amu, kin)`: (h, ism, rm), or None.

    TALYS: ecist.f:3627 (lect)
    Test: tests/hf/test_nx2_omp.py
    """
    fn = _kernel("nx2_omp_grid")
    if fn is None or _grad(kin.k_fm, kin.ecm_mev):
        return None
    k, ecm = _np(kin.k_fm.detach()), _np(kin.ecm_mev.detach())
    n_e = k.shape[0]
    cols = _param_cols(p, n_e)
    if cols is None:
        return None
    h, rm = np.empty(n_e), np.empty(n_e)
    ism = np.empty(n_e, dtype=np.int64)
    fn(n_e, int(rounding), nx2.ptr(cols), float(m_targ_amu), nx2.ptr(k), nx2.ptr(ecm), nx2.ptr(h),
       nx2.ptr(ism), nx2.ptr(rm))
    return torch.from_numpy(h), torch.from_numpy(ism), torch.from_numpy(rm)


def coulomb(eta: Tensor, rho: Tensor, lmax: int):
    """`coulomb_functions(eta, rho, lmax)`: F, F', G, G' (E, lmax + 1), or None.

    TALYS: ecist.f:5775 (fcou)
    Test: tests/hf/test_nx2_omp.py
    """
    fn = _kernel("nx2_omp_coulomb")
    if fn is None or rho.device.type != "cpu":
        return None
    e = _np(eta.detach().reshape(-1))
    r = _np(rho.detach().reshape(-1))
    L1 = int(lmax) + 1
    out = np.zeros((4, r.shape[0], L1))
    if fn(r.shape[0], L1, nx2.ptr(e), nx2.ptr(r), *(nx2.ptr(out[i]) for i in range(4))):
        raise MemoryError("nx2_omp_coulomb")
    return tuple(torch.from_numpy(out[i]) for i in range(4))


# ------------------------------------------------------------------------- the channel solve
def _run_job(cols: np.ndarray, e_lab: np.ndarray, particle: int, Z_target: int, m_targ: float,
             L1: int, cap: np.ndarray, active: np.ndarray, tail: bool, rounding: int):
    from physics.hf.omp.schrodinger import PARMASS_AMU, PARSPIN, PARZ

    fn = _kernel("nx2_omp_job")
    n_e = e_lab.shape[0]
    spin = float(PARSPIN[particle])
    nj = int(round(2 * spin)) + 1
    tjl = np.zeros((n_e, L1, 3))
    sig = np.zeros((n_e, 3))
    cap = np.ascontiguousarray(cap, dtype=np.int64)
    active = np.ascontiguousarray(active, dtype=np.int64)
    if fn(n_e, L1, nj, spin, float(Z_target * PARZ[particle]), float(PARMASS_AMU[particle]),
          float(m_targ), rounding, nx2.ptr(e_lab), nx2.ptr(cols), nx2.ptr(cap), nx2.ptr(active),
          int(tail), nx2.ptr(tjl), nx2.ptr(sig)):
        raise MemoryError("nx2_omp_job")
    return tjl, sig


def _rounding(ecis_rounding: bool) -> int:
    from physics.hf.omp import schrodinger

    on = bool(schrodinger.CARD_ROUNDING)
    return (1 if (ecis_rounding and on) else 0) | (2 if on else 0)


def solve(p, Z_target: int, A_target: int, particle: int, e_mev, m_targ_amu: float | None,
          lmax: int | None, ecis_rounding: bool = True):
    """`solve_spherical(p, Z_target, A_target, particle, e_mev, m_targ_amu=, lmax=,
    ecis_rounding=)` with ECIS's integrator, or None (no kernel, or a gradient).

    TALYS: inverseecis.f90:1 (inverseecis), ecist.f:1 (ecist)
    Test: tests/hf/test_nx2_omp.py
    """
    from physics.hf.omp.schrodinger import (
        NJ, PARMASS_AMU, Transmission, _lmax_talys, njmax_ecis, nucleus_mass_amu)

    if _kernel("nx2_omp_job") is None or _grad(e_mev):
        return None
    e = torch.as_tensor(e_mev, dtype=DTYPE)
    e_np = _np(e.detach().reshape(-1))
    n_e = e_np.shape[0]
    cols = _param_cols(p, n_e)
    if cols is None:
        return None
    m_targ = m_targ_amu if m_targ_amu is not None else nucleus_mass_amu(Z_target, A_target)
    if lmax is None:
        lmax = njmax_ecis(A_target, PARMASS_AMU[particle], e)
    L1 = int(lmax) + 1
    tjl, sig = _run_job(cols, e_np, particle, Z_target, m_targ, L1,
                        np.full(n_e, L1 - 1), np.ones(n_e), False, _rounding(ecis_rounding))
    t = torch.from_numpy(tjl)
    nan = torch.full((n_e,), float("nan"), dtype=DTYPE)
    tot = torch.from_numpy(sig[:, 1].copy()) if particle == 1 else nan
    el = torch.from_numpy(sig[:, 2].copy()) if particle == 1 else nan
    return Transmission(
        tjl=t[None, None], nj=torch.tensor([NJ[particle]], dtype=torch.int64),
        sigma_reac_mb=torch.from_numpy(sig[:, 0].copy())[None, None], sigma_tot_mb=tot[None, None],
        sigma_shape_el_mb=el[None, None], lmax=_lmax_talys(t, particle)[None, None],
    )


def _fill_in(t: np.ndarray, nj: int) -> None:
    """`inverse.process_tjl`'s fill-in of the (l +- s) value ECIS omits, in place on (E, L, 3)."""
    lpos = (np.arange(t.shape[1]) > 0)[None, :]
    if nj == 2:
        m, p = t[..., 0], t[..., 1]
        p = np.where((m != 0) & (p == 0), m, p)
        m = np.where((m == 0) & (p != 0) & lpos, p, m)
        t[..., 0], t[..., 1] = m, p
    elif nj == 3:
        m, z, p = t[..., 0], t[..., 1], t[..., 2]
        z = np.where((m != 0) & (z == 0), m, z)
        p = np.where((m != 0) & (p == 0), m, p)
        m = np.where((m == 0) & (p != 0) & lpos, p, m)
        t[..., 0], t[..., 1], t[..., 2] = m, z, p


def inverse_kept(Zt: int, At: int, e_grid: np.ndarray, maxen: int, options, params, lcap: int,
                 keep_e: dict):
    """`inverse.inverse_channels` for the neutron-induced run on (Zt, At) as
    `dens_reference._transmission_build` reads it: `Tjl` (1, 6, E, lcap + 1, 3) and `xsreac`
    (1, 6, E), solved only at the energies `keep_e[type]` marks (zeros elsewhere). None without
    the kernel.

    TALYS: basicxs.f90:1 (basicxs), inverse.f90:1 (inverse), inverseecis.f90:1 (inverseecis)
    Test: tests/hf/test_nx2_omp.py
    """
    from physics.hf.omp.inverse import NJ, _ported_omp
    from physics.hf.omp.schrodinger import (
        PARA, PARMASS_AMU, PARSPIN, PARZ, Transmission, nucleus_mass_amu)

    if _kernel("nx2_omp_job") is None:
        return None
    n_e = int(e_grid.shape[0])
    L1 = int(lcap) + 1
    out = np.zeros((1, 6, n_e, L1, 3))
    sig = np.zeros((1, 6, n_e))
    zc, ac = int(Zt), int(At) + 1  # neutron projectile
    e_all = np.asarray(e_grid, dtype=np.float64)
    nen = np.arange(n_e)
    sel = (nen >= 1) & (nen <= maxen) & (e_all > 0)
    idx = np.nonzero(sel)[0]
    rounding = _rounding(True)
    for k in range(1, 7):
        zr, ar = zc - PARZ[k], ac - PARA[k]
        if zr <= 0 or ar <= zr or idx.size == 0:
            continue
        m_res = nucleus_mass_amu(zr, ar)
        specmass = m_res / (m_res + PARMASS_AMU[k])
        e_lab = np.ascontiguousarray(e_all[idx] / specmass)
        cols = omp_columns(zr, ar - zr, k, e_lab, params, options)
        if cols is None:
            p = _ported_omp(Zt, At, zr, ar, k, torch.from_numpy(e_lab.copy()), options, params)
            cols = np.stack([np.broadcast_to(
                np.asarray(torch.as_tensor(getattr(p, f), dtype=DTYPE).detach().numpy(),
                           dtype=np.float64).reshape(-1), (e_lab.shape[0],)) for f in _COLUMNS])
            cols = np.ascontiguousarray(cols)
        # `schrodinger.lmax_ecis_grid`: njmax - 1 + ceil(parspin) per energy
        x = 2.4 * 1.25 * (ar ** (1.0 / 3.0)) * 0.22 * np.sqrt(PARMASS_AMU[k] * np.maximum(e_lab, 0.0))
        cap = np.clip(x.astype(np.int64), 20, 58) - 1 + int(math.ceil(PARSPIN[k]))
        active = np.asarray(keep_e[k], dtype=bool)[idx]
        tjl, s = _run_job(cols, e_lab, k, zr, m_res, L1, cap, active, True, rounding)
        _fill_in(tjl, NJ[k])
        out[0, k - 1, idx] = tjl
        sig[0, k - 1, idx] = s[:, 0]
    nan = torch.full((1, 6, n_e), float("nan"), dtype=DTYPE)
    return Transmission(
        tjl=torch.from_numpy(out), nj=torch.tensor([NJ[k] for k in range(1, 7)], dtype=torch.int64),
        sigma_reac_mb=torch.from_numpy(sig), sigma_tot_mb=nan, sigma_shape_el_mb=nan.clone(),
        lmax=torch.full((1, 6, n_e), -1, dtype=torch.int64),
    )


# ----------------------------------------------------------------------- OMP parameters
class _Id:
    """Identity key: an `Options` object is frozen, so one object means one set of switches."""

    __slots__ = ("obj",)

    def __init__(self, obj):
        self.obj = obj

    def __hash__(self):
        return id(self.obj)

    def __eq__(self, other):
        return isinstance(other, _Id) and other.obj is self.obj


@lru_cache(maxsize=256)
def _omppar(Z: int, A: int, opt: _Id, colltype, talys_dir):
    """`parameters.omppar(Z, A, options, colltype=)`, once per (nucleus, Options object)."""
    from physics.hf.omp.parameters import omppar

    return omppar(Z, A, opt.obj, colltype=colltype)


_ADJ_KEYS = (
    ("Fv1", "v1adjust"), ("Fv2", "v2adjust"), ("Fv3", "v3adjust"), ("Fv4", "v4adjust"),
    ("Frv", "rvadjust"), ("Fav", "avadjust"), ("Fw1", "w1adjust"), ("Fw2", "w2adjust"),
    ("Fw3", "w3adjust"), ("Fw4", "w4adjust"), ("Frw", "rwadjust"), ("Faw", "awadjust"),
    ("Frvd", "rvdadjust"), ("Favd", "avdadjust"), ("Fd1", "d1adjust"), ("Fd2", "d2adjust"),
    ("Fd3", "d3adjust"), ("Frwd", "rwdadjust"), ("Fawd", "awdadjust"), ("Fvso1", "vso1adjust"),
    ("Fvso2", "vso2adjust"), ("Frvso", "rvsoadjust"), ("Favso", "avsoadjust"),
    ("Fwso1", "wso1adjust"), ("Fwso2", "wso2adjust"), ("Frwso", "rwsoadjust"),
    ("Fawso", "awsoadjust"), ("Frc", "rcadjust"),
)  # fmt: skip
_FACTORS: dict = {}


def _version(t) -> int:
    """A tensor's in-place version counter (-1: absent; -2: an inference tensor, which keeps none,
    so only its identity is checked)."""
    if t is None:
        return -1
    return -2 if t.is_inference() else t._version


def _factors(params):
    """Per particle type 0..6: the `ompadjust` factors, `ejoin`, `vinfadjust` as floats; None when
    a parameter is on the autograd graph or an `ompadjustE` range is set. Memoised per `Params`
    object, re-read when any of its tensors was replaced or modified in place."""
    if params is None:
        return None
    vals = params.values
    keys = [k for _, k in _ADJ_KEYS] + ["ejoin", "vinfadjust", "ompadjuste1", "ompadjuste2"]
    tens = [vals.get(k) for k in keys]
    stamp = tuple((id(t), _version(t)) for t in tens)
    hit = _FACTORS.get(id(params))
    if hit is not None and hit[0] is params and hit[1] == stamp:
        return hit[2]
    res = None
    if not any(t is not None and t.requires_grad for t in tens) and all(
            t is not None for t in tens[:-2]):
        e1, e2 = tens[-2], tens[-1]
        if e1 is None or e2 is None or not bool((e2 > e1).any()):
            rows = [t.detach().reshape(-1).tolist() for t in tens[:-2]]
            res = []
            for k in range(7):
                F = {f: rows[i][k] for i, (f, _) in enumerate(_ADJ_KEYS)}
                res.append((F, rows[-2][k], rows[-1][k]))
    if len(_FACTORS) > 64:
        _FACTORS.clear()
    _FACTORS[id(params)] = (params, stamp, res)
    return res


class _Vec:
    where = staticmethod(np.where)
    exp = staticmethod(np.exp)
    log = staticmethod(np.log)
    maximum = staticmethod(np.maximum)
    minimum = staticmethod(np.minimum)
    sqrt = staticmethod(np.sqrt)

    @staticmethod
    def full(e, v):
        return np.full(e.shape, v, dtype=np.float64)


class _Scal:
    exp = staticmethod(math.exp)
    log = staticmethod(math.log)
    sqrt = staticmethod(math.sqrt)

    @staticmethod
    def where(c, a, b):
        return a if c else b

    @staticmethod
    def maximum(a, b):
        return a if (a != a or not (b > a)) else b

    @staticmethod
    def minimum(a, b):
        return a if (a != a or not (b < a)) else b

    @staticmethod
    def full(e, v):
        return v


def _opticalnp(xp, nuc, k: int, Z: int, A: int, e, fac, options, soukho: float | None):
    """`parameters.opticalnp` without a table or a join, on floats (xp: _Vec or _Scal)."""
    from physics.hf.omp.parameters import soukhovitskii_fermi

    e = xp.maximum(e, 0.0)
    F, ejoin, vinfadjust = fac[k]
    onethird = 1.0 / 3.0
    if options.flagsoukhoinp or (options.flagsoukho and Z >= 90 and nuc.ompglobal):
        eferm = soukho if soukho is not None else soukhovitskii_fermi(options)[k]
        return _soukhovitskii(xp, k, Z, A, e, eferm, F)
    f = e - nuc.ef_mev
    f2 = f * f
    rc = F["Frc"] * nuc.rc0_fm
    v1, v2 = F["Fv1"] * nuc.v1_mev, F["Fv2"] * nuc.v2_per_mev
    v3, v4 = F["Fv3"] * nuc.v3_per_mev2, F["Fv4"] * nuc.v4_per_mev3
    if k == 2 and nuc.ompglobal:
        vc = 1.73 / rc * Z / (A**onethird)
        vcoul = vc * v1 * (v2 - 2.0 * v3 * f + 3.0 * v4 * f2)
    else:
        vcoul = xp.full(e, 0.0)
    fjoin = ejoin - nuc.ef_mev
    v_low = v1 * (1.0 - v2 * f + v3 * f2 - v4 * (f2 * f)) + vcoul
    vinf = -vinfadjust * 30.0
    v0term = 0.0 - vinf
    vterm = (0.0 - vinf) / v0term if v0term > 0 else -1.0
    if v0term > 0 and vterm > 0:
        v_high = vinf + v0term * xp.exp(f / fjoin * math.log(vterm))
    else:
        v_high = xp.full(e, vinf)
    w1, w2 = F["Fw1"] * nuc.w1_mev, F["Fw2"] * nuc.w2_mev
    w3, w4 = F["Fw3"] * nuc.w3_mev, F["Fw4"] * nuc.w4_mev
    f4 = f**4
    w_low = w1 * f2 / (f2 + w2 * w2)
    w_high = 0.0 - w3 * fjoin**4 / (fjoin**4 + w4**4) + w3 * f4 / (f4 + w4**4)
    d1, d2, d3 = F["Fd1"] * nuc.d1_mev, F["Fd2"] * nuc.d2_per_mev, F["Fd3"] * nuc.d3_mev
    vso1, vso2 = F["Fvso1"] * nuc.vso1_mev, F["Fvso2"] * nuc.vso2_per_mev
    wso1, wso2 = F["Fwso1"] * nuc.wso1_mev, F["Fwso2"] * nuc.wso2_mev
    low = e <= ejoin
    return {
        "v_mev": xp.where(low, v_low, v_high),
        "rv_fm": F["Frv"] * nuc.rv0_fm,
        "av_fm": F["Fav"] * nuc.av0_fm,
        "w_mev": xp.where(low, w_low, w_high),
        "rw_fm": F["Frw"] * nuc.rv0_fm,
        "aw_fm": F["Faw"] * nuc.av0_fm,
        "vd_mev": 0.0,
        "rvd_fm": F["Frvd"] * nuc.rvd0_fm,
        "avd_fm": F["Favd"] * nuc.avd0_fm,
        "wd_mev": d1 * f2 * xp.exp(-d2 * f) / (f2 + d3 * d3),
        "rwd_fm": F["Frwd"] * nuc.rvd0_fm,
        "awd_fm": F["Fawd"] * nuc.avd0_fm,
        "vso_mev": vso1 * xp.exp(-vso2 * f),
        "rvso_fm": F["Frvso"] * nuc.rvso0_fm,
        "avso_fm": F["Favso"] * nuc.avso0_fm,
        "wso_mev": wso1 * f2 / (f2 + wso2 * wso2),
        "rwso_fm": F["Frwso"] * nuc.rvso0_fm,
        "awso_fm": F["Fawso"] * nuc.avso0_fm,
        "rc_fm": rc,
    }


def _soukhovitskii(xp, k: int, Z: int, A: int, e, eferm: float, F):
    """`parameters.soukhovitskii` on floats."""
    asym = (A - 2.0 * Z) / A
    f = xp.maximum(e - eferm, -20.0)
    f2 = f * f
    cviso, v0r, var, vrdisp, v1r, v2r, lam = 10.5, -41.45, -0.06667, 92.44, 0.03, 2.05e-4, 3.9075e-3
    viso = 1.0 + ((-1.0) ** k) * cviso * asym / (v0r + var * (A - 232.0) + vrdisp)
    ex = xp.exp(-lam * f)
    v = (v0r + var * (A - 232.0) + v1r * f + v2r * f2 + vrdisp * ex) * viso
    if k == 2:
        phicoul = (lam * vrdisp * ex - v1r - 2.0 * v2r * f) * viso
        v = v + 0.9 * Z / A ** (1.0 / 3.0) * phicoul
    w1, w2 = F["Fw1"] * 14.74, F["Fw2"] * 81.63
    d1 = F["Fd1"] * (17.38 + 0.03833 * (A - 232.0) + ((-1.0) ** k) * 24.0 * asym)
    d2, d3 = F["Fd2"] * 0.01759, F["Fd3"] * 11.79
    vso1, vso2 = F["Fvso1"] * 5.86, F["Fvso2"] * 0.0050
    wso1, wso2 = -3.1 * F["Fwso1"], F["Fwso2"] * 160.0
    return {
        "v_mev": F["Fv1"] * v,
        "rv_fm": F["Frv"] * 1.245 * (1.0 - 0.05 * f2 / (f2 + 100.0**2)),
        "av_fm": F["Fav"] * (0.660 + 2.53e-4 * e),
        "w_mev": w1 * f2 / (f2 + w2 * w2),
        "rw_fm": F["Frw"] * 1.2476,
        "aw_fm": F["Faw"] * 0.594,
        "vd_mev": 0.0,
        "rvd_fm": F["Frvd"] * 1.2080,
        "avd_fm": F["Favd"] * 0.614,
        "wd_mev": d1 * f2 * xp.exp(-d2 * f) / (f2 + d3 * d3),
        "rwd_fm": F["Frwd"] * 1.2080,
        "awd_fm": F["Fawd"] * 0.614,
        "vso_mev": vso1 * xp.exp(-vso2 * f),
        "rvso_fm": F["Frvso"] * 1.1213,
        "avso_fm": F["Favso"] * 0.59,
        "wso_mev": wso1 * f2 / (f2 + wso2 * wso2),
        "rwso_fm": F["Frwso"] * 1.1213,
        "awso_fm": F["Fawso"] * 0.59,
        "rc_fm": 0.0 if k == 1 else F["Frc"] * 1.2643,
    }


_FINAL = ("Fv1", "Frv", "Fav", "Fw1", "Frw", "Faw", "Fd1", "Frvd", "Favd", "Fd1", "Frwd", "Fawd",
          "Fvso1", "Frvso", "Favso", "Fwso1", "Frwso", "Fawso", "Frc")


def _alpha6(xp, Z: int, A: int, e, prev: dict, F) -> dict:
    """`parameters.opticalalpha` with alphaomp 6 (Avrigeanu 2014), then `_final_adjust`."""
    a13 = A ** (1.0 / 3.0)
    rb = 2.66 + 1.36 * a13
    e2 = (2.59 + 10.4 / A) * Z / rb
    e1 = -3.03 - 0.76 * a13 + 1.24 * e2
    e3 = 22.2 + 0.181 * Z / a13
    e4 = 29.1 - 0.22 * Z / a13
    v = xp.where(e <= e3, 165.0 + 0.733 * Z / a13 - 2.64 * e, 116.5 + 0.337 * Z / a13 - 0.453 * e)
    v = xp.maximum(v, -100.0)
    rv = xp.where(e <= 25.0, 1.18 + 0.012 * e, xp.full(e, 1.48))
    av = xp.where(
        e <= e2,
        xp.full(e, 0.631 + (0.016 - 0.001 * e2) * Z / a13),
        xp.where(e <= e4, 0.631 + (0.016 - 0.001 * e) * Z / a13,
                 0.684 - 0.016 * Z / a13 - (0.0026 - 0.00026 * Z / a13) * e),
    )  # fmt: skip
    av = xp.maximum(av, 0.1)
    w = xp.maximum(2.73 - 2.88 * a13 + 1.11 * e, 0.0)
    wd = xp.where(e <= e1, xp.full(e, 4.0),
                  xp.where(e <= e2, 22.2 + 4.57 * a13 - 7.446 * e2 + 6.0 * e,
                           22.2 + 4.57 * a13 - 1.446 * e))
    wd = xp.maximum(wd, 0.0)
    rwd = 1.52 if (A <= 152 or A >= 190) else xp.maximum(1.74 - 0.01 * e, 1.52)
    o = dict(prev)
    o.update(v_mev=v, rv_fm=rv, av_fm=av, w_mev=w, rw_fm=1.34, aw_fm=0.50, vd_mev=0.0, wd_mev=wd,
             rwd_fm=rwd, awd_fm=0.729 - 0.074 * a13, vso_mev=0.0, wso_mev=0.0, rc_fm=1.3)
    return {c: F[f] * o[c] for c, f in zip(_COLUMNS, _FINAL, strict=True)}


def _opticalcomp(xp, k: int, Z: int, A: int, e, nucleon, options, fac, soukho) -> dict | None:
    """`parameters.opticalcomp` without tables, joins or ranges, on floats."""
    from physics.hf.core.constants import PARA, PARN, PARZ

    e = xp.maximum(e, 0.0)
    alt = bool(options.altomp[k])
    if alt and (k == 3 and options.deuteronomp >= 2):
        return None
    if alt and k == 6 and (options.alphaomp == 2 or options.alphaomp >= 7):
        return None
    if alt and k == 6 and 3 <= options.alphaomp <= 5:
        return None

    def np_(kk, en):
        return _opticalnp(xp, nucleon[kk], kk, Z, A, en, fac, options, soukho.get(kk))

    ea = e / PARA[k]
    n, p = np_(1, ea), np_(2, ea)
    n_e, p_e = np_(1, e), np_(2, e)
    F = fac[k][0]
    iz, in_, ia = PARZ[k], PARN[k], PARA[k]
    o = {
        "v_mev": F["Fv1"] * (in_ * n["v_mev"] + iz * p["v_mev"]),
        "rv_fm": F["Frv"] * (in_ * n["rv_fm"] + iz * p["rv_fm"]) / ia,
        "av_fm": F["Fav"] * (in_ * n["av_fm"] + iz * p["av_fm"]) / ia,
        "w_mev": F["Fw1"] * (in_ * n["w_mev"] + iz * p["w_mev"]),
        "rw_fm": F["Frw"] * (in_ * n["rw_fm"] + iz * p["rw_fm"]) / ia,
        "aw_fm": F["Faw"] * (in_ * n["aw_fm"] + iz * p["aw_fm"]) / ia,
        "vd_mev": F["Fd1"] * (in_ * n["vd_mev"] + iz * p["vd_mev"]),
        "rvd_fm": F["Frvd"] * (in_ * n["rvd_fm"] + iz * p["rvd_fm"]) / ia,
        "avd_fm": F["Favd"] * (in_ * n["avd_fm"] + iz * p["avd_fm"]) / ia,
        "wd_mev": F["Fd1"] * (in_ * n["wd_mev"] + iz * p["wd_mev"]),
        "rwd_fm": F["Frwd"] * (in_ * n["rvd_fm"] + iz * p["rvd_fm"]) / ia,
        "awd_fm": F["Fawd"] * (in_ * n["avd_fm"] + iz * p["avd_fm"]) / ia,
        "rvso_fm": F["Frvso"] * (in_ * n_e["rvso_fm"] + iz * p_e["rvso_fm"]) / ia,
        "avso_fm": F["Favso"] * (in_ * n_e["avso_fm"] + iz * p_e["avso_fm"]) / ia,
        "rwso_fm": F["Frwso"] * (in_ * n_e["rvso_fm"] + iz * p_e["rvso_fm"]) / ia,
        "awso_fm": F["Fawso"] * (in_ * n_e["avso_fm"] + iz * p_e["avso_fm"]) / ia,
        "rc_fm": F["Frc"] * p_e["rc_fm"],
    }
    if k == 3:
        o["vso_mev"] = F["Fvso1"] * (n_e["vso_mev"] + p_e["vso_mev"]) / 2.0
        o["wso_mev"] = F["Fwso1"] * (n_e["wso_mev"] + p_e["wso_mev"]) / 2.0
    elif k in (4, 5):
        o["vso_mev"] = F["Fvso1"] * (n_e["vso_mev"] + p_e["vso_mev"]) / 6.0
        o["wso_mev"] = F["Fwso1"] * (n_e["wso_mev"] + p_e["wso_mev"]) / 6.0
    else:
        o["vso_mev"] = 0.0
        o["wso_mev"] = 0.0
    if alt:
        from physics.hf.omp.parameters import _alt_window

        kd = dict(o)
        i = 1
        new = o
        if k == 6 and options.alphaomp == 6:
            new = _alpha6(xp, Z, A, e, o, F)
            i = 6
        b0, b1, e1, e0 = _alt_window(k, i)
        efrac = xp.full(e, 1.0)
        if b1 > b0:
            efrac = xp.where((e > b0) & (e <= b1), (e - b0) / (b1 - b0), efrac)
        if e0 > e1:
            efrac = xp.where((e > e1) & (e <= e0), 1.0 - (e - e1) / (e0 - e1), efrac)
        efrac = xp.where(e <= b0, 0.0, efrac)
        efrac = xp.where(e > e0, 0.0, efrac)
        o = {c: efrac * new[c] + (1.0 - efrac) * kd[c] for c in _COLUMNS}
    return o


def omp_columns(Z: int, N: int, particle: int, e_mev, params, options, *, colltype=None,
                soukho_eferm_mev=None, enincmax_mev: float = 0.0):
    """`parameters.omp_parameters(Z, N, particle, e_mev, params, options)` as a (19, E) float64
    array in `COLUMNS` order (a tuple of 19 floats for a Python-float energy), or None when the
    configuration is outside the fast path (see the module docstring).

    TALYS: optical.f90:1 (optical), omppar.f90:1 (omppar)
    Test: tests/hf/test_nx2_omp.py
    """
    import os

    from physics.hf.core.constants import PARA, PARZ

    if options is None or not enabled():
        return None
    fac = _factors(params)
    if fac is None:
        return None
    A = Z + N
    if options.flagriplomp:
        for k in range(1, 7):
            if options.riplomp[k] > 0 and (Z, A) == (options.Zinit - PARZ[k],
                                                     options.Ainit - PARA[k]):
                return None
    for k in (1, 2):
        if enincmax_mev > fac[k][1]:
            return None
    if not (1 <= particle <= 6):
        return None
    nucleon = _omppar(Z, A, _Id(options), colltype, os.environ.get("TALYS_DIR"))
    scalar = isinstance(e_mev, float)
    xp = _Scal if scalar else _Vec
    e = e_mev if scalar else np.ascontiguousarray(np.asarray(e_mev, dtype=np.float64))
    soukho = dict(soukho_eferm_mev or {})
    try:
        with np.errstate(all="ignore"):
            if particle <= 2:
                o = _opticalnp(xp, nucleon[particle], particle, Z, A, e, fac, options,
                               soukho.get(particle))
            else:
                o = _opticalcomp(xp, particle, Z, A, e, nucleon, options, fac, soukho)
    except (OverflowError, ValueError, ZeroDivisionError):
        return None
    if o is None:
        return None
    if scalar:
        return tuple(float(o[c]) for c in _COLUMNS)
    out = np.empty((19, e.shape[0]), dtype=np.float64)
    for i, c in enumerate(_COLUMNS):
        out[i] = o[c]
    return out


def omp_parameters(Z: int, N: int, particle: int, e_mev, params, options, *, colltype=None,
                   tables=None, enincmax_mev: float = 0.0, soukho_eferm_mev=None,
                   sep_energy_mev=None, structure=None):
    """`parameters.omp_parameters` (same arguments) through `omp_columns`, or None.

    TALYS: optical.f90:1 (optical), omppar.f90:1 (omppar)
    Test: tests/hf/test_nx2_omp.py
    """
    from physics.hf.omp.parameters import OMPParameters

    if tables or sep_energy_mev is not None or structure is not None or options is None:
        return None
    e = torch.as_tensor(e_mev, dtype=DTYPE)
    if e.requires_grad or e.device.type != "cpu":
        return None
    en = e.detach().numpy().reshape(-1)
    kw = dict(colltype=colltype, soukho_eferm_mev=soukho_eferm_mev, enincmax_mev=enincmax_mev)
    if en.shape[0] == 1:  # one energy (`direct.chain._omp_at`): Python floats
        vals = omp_columns(Z, N, particle, float(en[0]), params, options, **kw)
        cols = None if vals is None else np.array(vals, dtype=np.float64)
    else:
        cols = omp_columns(Z, N, particle, en, params, options, **kw)
    if cols is None:
        return None
    t = torch.from_numpy(cols.reshape((19,) + tuple(e.shape)))
    return OMPParameters(**{c: t[i] for i, c in enumerate(_COLUMNS)})
