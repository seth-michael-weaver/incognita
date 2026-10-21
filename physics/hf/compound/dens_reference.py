"""Build `DensPrepareInputs` for a reference case from the ported components, and score the four
arrays `densprepare` produces against the instrumented TALYS dump.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: E2E (physics/hf/CONTRACT.md §7). Acceptance test: A-cn1 / A-trans / A-ld / A-psf (§6).

What is *computed* here is exactly what `densprepare` consumes and nothing else:

* `rhogrid` -- T6 (`density.parameters.densitypar` -> `tables.attach_tables` ->
  `matching.densitymatch`, then `models.density` at the bin's bottom, centre and top and
  `core.grids.integrated_density`), exgrid.f90:241-285.
* `Tjl`, `Tl`, `lmax` on the emission grid -- T5 (`omp.inverse.inverse_channels`), plus
  `core.grids` for `egrid`, `ebegin` and `eend`.
* `f_XL` -- T7 (`gamma.parameters.gamma_parameters` -> `gamma.strength.fstrength`).

What is *injected* is the grid densprepare is handed, not the physics it computes on it:
`Exinc`/`dExinc` and `Fnorm` (compnorm.f90, the CN normalisation), `Ex`/`deltaEx`/`maxJ`
(exgrid, gate A-grid), `parlev`/`jdis`/`Nlast`/`S` (structure, gate A-struct, exact as printed)
and `lmaxinc`/`gammax`/`k0`. Each of those has its own passing component gate; taking them from
the dump is what makes this a gate on densprepare rather than on all of T2-T7 at once.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
import os
from functools import lru_cache
from pathlib import Path

import numpy as np
import torch

from physics.hf.compound.prepare import (
    NUMJ,
    CompoundInputs,
    DensPrepareInputs,
    DensResidual,
    DensTrans,
    densprepare,
)
from physics.hf.core.constants import PARSYM
from physics.hf.projectile import compound_of
from physics.hf.core.constants import talys_constants
from physics.hf.core.grids import (
    charged_particle_begin,
    egrid_values,
    emission_bins,
    emission_end,
    emission_limit,
    incident_kinematics,
    integrated_density,
    total_energy,
)
from physics.hf.core.tensors import DTYPE
from physics.hf.input.defaults import default_options, default_params, default_params_shared
from physics.hf.input.nuclides import coulomb_barriers
from physics.hf.structure.levels import discrete_levels
from physics.hf.structure.masses import masses
from physics.hf import stagetime
from physics.hf.projectile import target_mass_index  # ENGPROJ3 TARMASSFIX

NUMEN = int(__import__("os").environ.get("INCOGNITA_NUMEN", "250"))  # INCOGNITA_NUMEN (PECOLLAPSE): reference runs only
NUML = 60  # A0_talys_mod.f90 numl
TRANSEPS = 1.0e-8  # input_numerics.f90:80


# ------------------------------------------------------------------------------------------------
# T6: rhogrid on the excitation grid of one residual
# ------------------------------------------------------------------------------------------------


@lru_cache(maxsize=32)
@stagetime.timed("setup.structure")
def _structure_of(Zt: int, At: int):
    """`default_options`, `default_params` and `masses` of one run, built once: every helper
    below needs the same three for the same target, and `masses` is the expensive one."""
    o = default_options(Zt, At)
    p = default_params_shared(Zt, At, o)
    return o, p, masses(o, p)


def structure_of(Zt: int, At: int, overrides: dict | None = None):
    """`_structure_of` with DIFFPARAM's keyword overrides applied to `Params`.

    `masses` is taken from the unperturbed build: `density.overrides` rejects every keyword
    `structure.masses` reads, so it cannot move, and rebuilding it per finite-difference step
    would dominate the cost of the whole gradient (it is the expensive part of the run set-up).

    TALYS: talysinput.f90:1 (talysinput)
    Test: G0.4 / tests/hf/test_capture_fast.py
    """
    o, p, m = _structure_of(Zt, At)
    if not overrides:
        return o, p, m
    return o, default_params(Zt, At, o, overrides), m


@lru_cache(maxsize=128)
def _ld_of_cached(Z: int, A: int, Zt: int, At: int, aadjust: float | None = None):
    # PARAMWIRE: `aadjust` is the parameter set's value at (Z, A) (`density.overrides.ld_token`),
    # part of the key; the defaults are called with four arguments, as before
    if aadjust is None:
        return _ld_build(Z, A, Zt, At, None)
    return _ld_build(Z, A, Zt, At, None, aadjust=aadjust)


@stagetime.timed("setup.ld")
def _ld_build(Z: int, A: int, Zt: int, At: int, overrides: dict | None,
              matching_xacc: float | None = None, aadjust: float | None = None):
    from physics.hf.density.matching import _XACC
    from physics.hf.density.overrides import with_aadjust

    o, p, m = structure_of(Zt, At, overrides)
    if aadjust is not None:
        p = with_aadjust(p, o, ((Z, A, aadjust),))
    lv = discrete_levels(Z, A, o, m, p)
    if not overrides and not torch.is_grad_enabled():
        from physics.hf.density import ld_nx2
        from physics.hf.density.ctwindow import enabled as _ctw
        from physics.hf.density.ctwindow2 import mode as _ctw2

        k = ld_nx2.densitypar_key(Z, A, o, p, m, lv) if ld_nx2._xt_on() else None
        if k is not None:
            # CENGLD2: the matched record, Ntop, Nlast and Ncum(NL) of equal inputs are shared
            # across targets (`ld_nx2.densitypar_key` plus what matching reads besides the record)
            xacc = _XACC if matching_xacc is None else matching_xacc
            return ld_nx2.shared_record(
                ("ld", k, bool(o.flagldglobal), bool(o.flagctmglob), float(xacc))
                + ((("ctwindow2",) + (("cont",) if _ctw2(o) == "cont" else ())) if _ctw2(o) else (("ctwindow",) if _ctw(o) else ())),
                o.Zinit - Z, o.Ninit - (A - Z), lambda: _ld_match(Z, A, o, p, m, lv, xacc))
    return _ld_match(Z, A, o, p, m, lv, _XACC if matching_xacc is None else matching_xacc)


def _ld_match(Z: int, A: int, o, p, m, lv, xacc: float):
    """`_ld_build`'s record from its structure: densitypar, tables, densitymatch, Ntop/Nlast/Ncum."""
    from physics.hf.density.ctwindow import enabled as _ctw
    from physics.hf.density.ctwindow2 import mode as _ctw2
    from physics.hf.density.matching import densitycum, densitymatch
    from physics.hf.density.parameters import densitypar
    from physics.hf.density.tables import attach_tables

    from physics.hf.density import spinquench as _sq

    _sq.note_ecut(Z, A, o, lv)  # SPINQUENCH qd: the continuum start E(Nlast) (OFF: records nothing)
    ld = densitymatch(attach_tables(densitypar(Z, A, o, p, m, lv)), o.flagldglobal,
                      o.flagctmglob, xacc, ctwindow=_ctw(o), ctwindow2=_ctw2(o))
    nl = int(ld.Nlast[0])
    # `Ncum(NL)` looks like a count of discrete levels and is not: densitycum.f90 *integrates the
    # level density* between the level energies, so it moves with every level-density parameter,
    # and densprepare's `discfactor` divides the discrete rows above Ntop by it. Detaching it
    # cost 7% of d(sum log10 capture)/d(aadjust) on Fe-56 -- the single largest term left after
    # the implicit Exmatch derivative. It stays a tensor when it carries a gradient and becomes
    # a float when it does not, so the default path is the float it always was.
    try:
        ncum = _ncum_no_grad(ld, nl)  # SETB: None when the level density carries a gradient
        if ncum is None:
            v = densitycum(ld)["Ncum"][min(nl, ld.nlevmax2)]
            ncum = v if v.requires_grad else float(v)
    except Exception:
        ncum = float(nl)
    return ld, int(ld.Ntop[0]), nl, ncum


def _ncum_no_grad(ld, nl: int) -> float | None:
    """SETB: `densitycum(ld)["Ncum"][min(nl, nlevmax2)]` as a float, from the one level-density
    call `densitycum` makes and the cumulative sum up to that entry only; None when the density
    carries a gradient (the caller then keeps `densitycum` and its tensor).

    TALYS: densitycum.f90:1 (densitycum)
    Test: tests/hf/test_setb.py
    """
    from physics.hf.density.ld_nx2 import ncum as _nx2_ncum
    from physics.hf.density.matching_fast import ncum_at
    from physics.hf.density.models import densitytot

    n = ld.nlevmax2
    got = _nx2_ncum(ld, int(ld.Nlow[0]), min(nl, n))  # NX2 ld: C, off the graph (None: below)
    if got is not None:
        return got
    edis = ld.edis_mev
    dens = densitytot(ld, 0.5 * (edis[1 : n + 1] + edis[0:n]), 0)
    if dens.requires_grad:
        return None
    return ncum_at(edis, dens, int(ld.Nlow[0]), min(nl, n))


def _ld_of(Z: int, A: int, Zt: int, At: int, overrides: dict | None = None,
           matching_xacc: float | None = None, aadjust: float | None = None):
    """T6's `LDNucleus` for (Z, A), matched, with tables attached, plus Ntop and Ncum(NL).

    With DIFFPARAM level-density overrides the cache is bypassed -- an `lru_cache` keyed on
    (Z, A, Zt, At) would hand every finite-difference step the first step's tensors. A PARAMWIRE
    `aadjust` (a float, the parameter set's value at (Z, A)) is part of the cache key instead.
    """
    if not overrides and matching_xacc is None:
        if aadjust is None:
            return _ld_of_cached(Z, A, Zt, At)
        return _ld_of_cached(Z, A, Zt, At, aadjust)
    return _ld_build(Z, A, Zt, At, overrides, matching_xacc, aadjust)


def rhogrid_of(
    Z: int, A: int, Zt: int, At: int, ex_mev: np.ndarray, dex_mev: np.ndarray,
    maxj: np.ndarray, nlast: int, overrides: dict | None = None, differentiable: bool = False,
    matching_xacc: float | None = None, aadjust: float | None = None,
):
    """`rhogrid(nex, Ir, Pprime)`, the level density integrated over each continuum bin
    (exgrid.f90:241-285): rho at the bin bottom, centre and top, log-averaged. Parity axis
    (-1, +1); an equiprobable-parity model (`flagparity` false) fills both from +1, which
    `density` already does.

    numpy by default. `differentiable` returns the same numbers as a float64 tensor on the graph
    of `overrides` (DIFFPARAM): the loop that zeroes `Ir > maxJ` becomes a mask and the row
    scatter an `index_copy`, so nothing is written in place into a graph tensor. The two paths
    are compared at 1e-12 by `tests/hf/test_density.py::test_rhogrid_torch_path_matches_numpy`.

    TALYS: exgrid.f90:1 (exgrid)
    Test: A-ld / G0.4
    """
    from physics.hf.density.models import density

    ld, _, _, _ = _ld_of(Z, A, Zt, At, overrides, matching_xacc, aadjust)
    if not differentiable and not overrides:
        from physics.hf.density.ld_nx2 import rhogrid as _nx2_rhogrid

        got = _nx2_rhogrid(ld, A, ex_mev, dex_mev, maxj, nlast, NUMJ)  # NX2 ld: the bin set in C
        if got is None:
            from physics.hf.density.ld2_nx2 import table_rhogrid

            got = table_rhogrid(ld, ex_mev, dex_mev, maxj, nlast, NUMJ)  # NX2 ld2: a table's
        if got is not None:
            return got
    n = len(ex_mev)
    rodd = 0.5 * (A % 2)
    sel = [k for k in range(nlast + 1, n) if maxj[k] >= 0]
    if not sel:
        return (torch.zeros((n, NUMJ + 1, 2), dtype=DTYPE) if differentiable
                else np.zeros((n, NUMJ + 1, 2)))
    idx = torch.tensor(sel, dtype=torch.int64)
    ex = torch.as_tensor(ex_mev, dtype=DTYPE)[idx]
    dex = torch.as_tensor(dex_mev, dtype=DTYPE)[idx]
    spins = torch.arange(NUMJ + 1, dtype=DTYPE) + rodd
    e1 = (ex - 0.5 * dex)[:, None]
    e2 = ex[:, None]
    e3 = (ex + 0.5 * dex)[:, None]
    jj = spins[None, :]
    # the analytical models do not read the parity (density.f90's 1/2 pardis): one evaluation
    # (SPEED3), shared by both parity columns on the numpy and the differentiable path
    same = ld.ldmodel <= 3 or not ld.has_table(0)
    rows = [None, None]
    for ip, par in ((1, 1), (0, -1)) if same else ((0, -1), (1, 1)):
        if same and ip == 0:
            rows[0] = rows[1]
            continue
        if differentiable:
            r1 = density(ld, e1, jj, par)
            r2 = density(ld, e2, jj, par)
            r3 = density(ld, e3, jj, par)
        else:
            # NATIVEX: `density` is elementwise in the energy, so the bottom, centre and top of
            # every bin go through one call (a third of the Python work; values to rounding)
            k = e1.shape[0]
            r1, r2, r3 = density(ld, torch.cat([e1, e2, e3]), jj, par).split(k)
        rows[ip] = integrated_density(r1, r2, r3, dex[:, None])
    if not differentiable:
        out = np.zeros((n, NUMJ + 1, 2))
        for ip in (0, 1):
            # `.detach()` is belt and braces: nothing should reach the numpy path carrying a
            # graph (the two leaks that did -- `_exmatch_implicit`'s throwaway leaf and
            # `densitycum`'s Ncum -- are fixed at their source), but `.numpy()` raises rather
            # than degrading if one ever does, and this is the default path. A no-op.
            out[sel, :, ip] = rows[ip].detach().numpy()
        for k in sel:
            out[k, int(maxj[k]) + 1 :] = 0.0
        return out
    keep = (torch.arange(NUMJ + 1)[None, :]
            <= torch.as_tensor(np.asarray(maxj)[sel], dtype=torch.int64)[:, None])
    v = torch.stack(rows, dim=-1) * keep[:, :, None].to(DTYPE)
    return torch.zeros((n, NUMJ + 1, 2), dtype=DTYPE).index_copy(0, idx, v)


# ------------------------------------------------------------------------------------------------
# T5: Tjl, Tl, lmax on the emission grid
# ------------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class _RunGrid:
    egrid: np.ndarray
    maxen: int
    ebegin: dict
    s0: list
    options: object
    params: object
    m: object


@lru_cache(maxsize=32)
def run_grid(Zt: int, At: int, enincmax_mev: float) -> _RunGrid:
    """The outgoing-energy grid, `ebegin` and the separation energies of the compound nucleus.

    TALYS: grid.f90:1 (grid)
    Test: A-grid
    """
    o, p, m = _structure_of(Zt, At)
    s0 = [float(m.s_mev[0, 0, t]) for t in range(7)]
    eg, maxen = egrid_values(
        emission_limit(enincmax_mev, s0[o.k0], 0.0), o.segment, NUMEN, o.flagequispec, None)
    cb = coulomb_barriers(o)
    ebegin, _ = charged_particle_begin(
        eg, maxen, At, {t: cb[t] for t in range(7)}, {t: False for t in range(7)})
    return _RunGrid(eg, maxen, ebegin, s0, o, p, m)


@lru_cache(maxsize=32)
def _transmission_cached(Zt: int, At: int, enincmax_mev: float) -> dict:
    from physics.hf import stagedisk

    if not stagedisk.enabled():
        return _transmission_build(Zt, At, enincmax_mev, None, False)
    # STAGECACHE: the same build, from disk when its optical-model inputs were seen before
    from physics.hf.direct import dwbaunit

    o, p, m = _structure_of(Zt, At)
    return stagedisk.cached(
        "inverse", (int(Zt), int(At), float(enincmax_mev)),
        lambda: _transmission_build(Zt, At, enincmax_mev, None, False),
        options=(o,), params=(p,), values=(m, dwbaunit.state(*dwbaunit.target_of(o))))


def _transmission(Zt: int, At: int, enincmax_mev: float, overrides: dict | None = None,
                  differentiable: bool = False) -> dict:
    """T5's `Tjl` on the whole emission grid for particles 1..6, plus the spin-averaged `Tl` and
    `lmax` of inverseread.f90.

    With DIFFPARAM optical overrides the (Zt, At, enincmax) cache is bypassed, and with
    `differentiable` the `Tjl`/`Tl` of each type come back as float64 tensors on the graph of
    those overrides instead of numpy. `lmax` stays an integer array either way: it is
    inverseread.f90's *count* of partial waves above a threshold, a branch, not a value.

    TALYS: inverse.f90:1 (inverse), inverseread.f90:1 (inverseread)
    Test: A-trans / G0.4
    """
    from physics.hf.omp import sfunc

    if not overrides and not differentiable:
        if sfunc.mode() is not None:  # SLINPUT (default OFF): measured-S_l rule on the neutron row
            return _transmission_sfunc(Zt, At, enincmax_mev, sfunc.mode(),
                                       os.environ.get("INCOGNITA_SFUNC_TABLE", ""))
        return _transmission_cached(Zt, At, enincmax_mev)
    return _transmission_build(Zt, At, enincmax_mev, overrides, differentiable)


@lru_cache(maxsize=32)
def _transmission_sfunc(Zt: int, At: int, enincmax_mev: float, mode: str, table: str, div: tuple = ()) -> dict:
    """SLINPUT (`omp.sfunc`): the emission-grid neutron Tjl/Tl x F_l(E_lab) = [S_l,meas / S_l,model(1 keV)]^w,
    clipped at 1, with S_l,model log-interpolated at 1 keV from this grid's own Tl; the neutron inverse
    sigma_reac scales with sum (2l+1) Tl. Keyed on the mode and table, so a warm worker never mixes arms.
    `flagompall n`: this is the ONE neutron set of the cascade, i.e. the target's (Zt, At).
    `div` (ROTEXIT1CN3 `sfexit ccf`, default ()): ((l, f_l), ...) -- S_l,meas / f_l replaces S_l,meas."""
    from physics.hf.omp import sfunc

    d = _transmission_cached(Zt, At, enincmax_mev)
    meas = sfunc.measured(Zt, At)
    if not meas or 1 not in d:
        return d
    ud, tl, lm = d[1]
    e_lab, model = _sfunc_inv_model(Zt, At, enincmax_mev, tuple(sorted(meas)))
    if not div:
        sfunc.LAST[(int(Zt), int(At), "inv")] = {"model": dict(model), "meas": dict(meas)}
    else:
        dv = dict(div)
        meas = {l: s / dv.get(l, 1.0) for l, s in meas.items()}
        sfunc.LAST[(int(Zt), int(At), "ccf")] = {"model": dict(model), "meas": dict(meas), "f": dict(dv)}
    F = sfunc.factors(meas, model, e_lab)
    if not F:
        return d
    ud2, tl2 = ud.copy(), tl.copy()
    for l, f in F.items():
        ud2[:, l, :] = np.minimum(ud[:, l, :] * f[:, None], 1.0)
        tl2[:, l] = np.minimum(tl[:, l] * f, 1.0)
    g = 2.0 * np.arange(tl.shape[1]) + 1.0
    den = (tl * g).sum(-1)
    r = np.where(den > 0, (tl2 * g).sum(-1) / np.where(den > 0, den, 1.0), 1.0)
    out = dict(d)
    out[1] = (ud2, tl2, lm)
    sig = d["sigma_reac_mb"].clone()
    n_e = tl.shape[0]
    sig[0, : n_e] = sig[0, : n_e] * torch.as_tensor(r, dtype=sig.dtype)
    out["sigma_reac_mb"] = sig
    return out


@lru_cache(maxsize=32)
def _sfunc_inv_model(Zt: int, At: int, enincmax_mev: float, ls: tuple) -> tuple:
    """(E_lab grid, {l: S_l,model(1 keV)}) of the target's emission-grid neutron Tl (SLINPUT's inverse-channel
    reference strength functions; spr.f90 form, log-log interpolated at 1 keV)."""
    from physics.hf.core.grids import incident_kinematics
    from physics.hf.omp import sfunc
    from physics.hf.omp.schrodinger import PARMASS_AMU, nucleus_mass_amu

    d = _transmission_cached(Zt, At, enincmax_mev)
    tl = d[1][1]
    rg = run_grid(Zt, At, enincmax_mev)
    n_e = tl.shape[0]
    m_res = nucleus_mass_amu(Zt, At)
    e_lab = np.asarray(rg.egrid[:n_e], dtype=float) / (m_res / (m_res + PARMASS_AMU[1]))
    pos = e_lab > 0
    wk = np.zeros(n_e)
    wk[pos] = [incident_kinematics(float(e), 1, m_res, 0.0, 0.0)[1] for e in e_lab[pos]]
    model = {}
    for l in ls:
        if l >= tl.shape[1]:
            continue
        ok = pos & (tl[:, l] > 0) & (e_lab <= sfunc.E_FULL_MEV)
        s = np.full(n_e, np.nan)
        s[ok] = sfunc.strength(tl[ok, l], e_lab[ok], At, wk[ok], l)
        model[l] = sfunc.interp_ref(e_lab[ok], s[ok])
    return e_lab, model


@stagetime.timed("setup.omp_inverse")
def _transmission_build(Zt: int, At: int, enincmax_mev: float, overrides: dict | None,
                        differentiable: bool) -> dict:
    from physics.hf.core.grids import EmissionGrid
    from physics.hf.omp.inverse import NJ, inverse_channels
    from physics.hf.core.tensors import CaseBatch

    from physics.hf.omp.parameters import ejectile_params

    rg = run_grid(Zt, At, enincmax_mev)
    _o, rg_params, _m = structure_of(Zt, At, overrides)
    # Every channel here is an OUTGOING one: the PROJECTILE's type leaving takes TALYS's type-0
    # factors (flagompejec, opticalnp.f90:175 `k == k0`), not the incident channel's `rvadjust n`
    # & co.; every other ejectile keeps its own per-particle factors. charged-projectile fidelity: was hard-wired to
    # the neutron (1), so a proton/alpha run dropped `rvadjust n` on outgoing neutrons and kept
    # the incident `rvadjust p` on outgoing protons. k0 = 1 is unchanged.
    rg_params = ejectile_params(rg_params, int(rg.options.k0))
    E = rg.maxen + 1
    de, _, _ = emission_bins(rg.egrid, rg.maxen)
    e_t = torch.tensor(rg.egrid[:E], dtype=DTYPE)[None]
    mask = (torch.arange(E) >= 1) & (torch.arange(E) <= rg.maxen)
    grid = EmissionGrid(e_t, torch.tensor(de[:E], dtype=DTYPE)[None], mask[None],
                        maxen=torch.tensor([rg.maxen]))
    cases = CaseBatch(Z=torch.tensor([Zt]), A=torch.tensor([At]),
                      e_inc_mev=torch.tensor([enincmax_mev], dtype=DTYPE),
                      projectile=PARSYM[rg.options.k0])  # CPINC: was "n"
    njm = {t: _njmax(Zt, At, t, rg.egrid[:E]) for t in range(1, 7)}
    lcap = int(max(int(v.max()) for v in njm.values()))
    eendmax = _eendmax(Zt, At, enincmax_mev)
    nen_ax = torch.arange(E)
    keep_e = {t: (nen_ax >= rg.ebegin[t]) & (nen_ax <= eendmax[t]) for t in range(1, 7)}
    tr = None
    if not differentiable:  # NATIVEX2 `omp`: compiled, only the energies and l kept below
        from physics.hf.omp.omp_nx2 import inverse_kept

        tr = inverse_kept(Zt, At, np.asarray(rg.egrid[:E], dtype=float), rg.maxen, rg.options,
                          rg_params, lcap, {t: keep_e[t].numpy() for t in range(1, 7)})
    if tr is None:
        tr = inverse_channels(cases, grid, rg.options, rg_params, lmax=lcap,
                              edetach=keep_e if differentiable else None)
    out = {}
    L = tr.tjl.shape[-2]
    ll = torch.arange(L, dtype=DTYPE)
    for t in range(1, 7):
        tjl = tr.tjl[0, t - 1]  # (E, L, 3) in the contract's padded j order
        # The per-energy njmax cap is `omp.inverse._clip_to_njmax`'s job now (T5LOW). It used to
        # be repeated here as `l < njmax(nen)`, one l short: ECIS's J loop ends at J = njmax - 1/2,
        # whose partial waves are l = njmax - 1 AND l = njmax, so the cap is inclusive. That
        # off-by-one is the `l = lmax` cell the end-to-end run found the port zeroing.
        keep = torch.ones((tjl.shape[0], L), dtype=torch.bool)
        # `inverse` fills Tjl only over [ebegin(type), eendmax(type)] (inverseecis.f90:402); a
        # grid point above eendmax is a hard zero TALYS then interpolates through, and pol2 can
        # take the result negative, which densprepare clips to 0. Filling it instead -- which a
        # port naturally does -- put Pb-208's alpha channel out by 2.6x at 18-20 MeV, because
        # S(alpha) of Pb-209 is NEGATIVE (-2.25 MeV) so Eout runs past the top of the grid.
        keep = keep & keep_e[t][: tjl.shape[0], None]
        tjl = torch.where(keep[:, :, None], tjl, torch.zeros(()))
        nj = NJ[t]
        if nj == 2:
            tl = ((ll + 1) * tjl[..., 1] + ll * tjl[..., 0]) / (2 * ll + 1)
        elif nj == 3:
            tl = ((2 * ll + 3) * tjl[..., 2] + (2 * ll + 1) * tjl[..., 1]
                  + (2 * ll - 1) * tjl[..., 0]) / (3 * (2 * ll + 1))
        else:
            tl = tjl[..., 0]
        lm = _lmax_inverseread(tjl, tl, t)
        # outside [ebegin, eend] TALYS never computes lmax; the array keeps reacinitial's 0, and
        # densprepare copies it into lmaxhf whenever Eout falls below egrid(ebegin) (nen = 0).
        lm[: rg.ebegin[t]] = 0
        lm[rg.maxen + 1 :] = 0
        ud = _to_updown_axis(tjl, t)
        out[t] = ((ud.to(DTYPE), tl.to(DTYPE), lm) if differentiable
                  else (ud.detach().numpy().astype(float), tl.detach().numpy().astype(float), lm))
    # SPEEDP: the same `inverse_channels` solve also produces `xsreac(type, nen)`, which
    # `preeq.chain.inverse_reaction_xs` (NODUMP's replacement for `cross_<p>.tot`) used to get by
    # repeating the whole solve on an identical grid. Every other key of this dict is an int
    # type, so the string key is invisible to the six consumers that index it.
    out["sigma_reac_mb"] = tr.sigma_reac_mb[0]
    # LOGTINT (default OFF; compound/tlog.py): log-T Lagrange of charged T in densprepare; REF = 8x-refined table (G0)
    from physics.hf.compound import tlog

    if tlog.mode(rg.options) in ("c", "l"):  # TLOGIT: "l" = logit-T Lagrange
        out["tlog"] = True if tlog.mode(rg.options) == "c" else "l"
    if tlog.ref(rg.options) and not differentiable:
        out["tlogref"] = _tlogref_tables(Zt, At, rg, rg_params, lcap, eendmax)
    # ALPHATEMP (default OFF; omp/alphatemp.py): the alpha ABSORPTION potential (alphaomp 6) on the same grid and keep window,
    # for the cold residual states. The hot table is the run's own (out[6]); lmax stays the run's.
    from physics.hf.omp import alphatemp

    ts = alphatemp.tstar(rg.options)
    if ts > 0.0 and not differentiable:
        import dataclasses

        from physics.hf.omp.omp_nx2 import inverse_kept

        o6 = dataclasses.replace(rg.options, alphaomp=6)
        k6 = {t: (keep_e[t].numpy() if t == 6 else np.zeros_like(keep_e[t].numpy())) for t in range(1, 7)}
        tc = inverse_kept(Zt, At, np.asarray(rg.egrid[:E], dtype=float), rg.maxen, o6, rg_params, lcap, k6)
        if tc is None:
            tc = inverse_channels(cases, grid, o6, rg_params, lmax=lcap)
        t6 = torch.as_tensor(tc.tjl, dtype=DTYPE)[0, 5]
        t6 = torch.where(keep_e[6][: t6.shape[0], None, None], t6, torch.zeros((), dtype=DTYPE))
        out["alpha_cold"] = (_to_updown_axis(t6, 6).detach().numpy().astype(float),
                             t6[..., 0].detach().numpy().astype(float), out[6][2])
        out["alphatemp_ustar"] = alphatemp.ustar(At + 1 - 4, ts)
        out["alphatemp_tstar"] = ts
        out["alphatemp_dom"] = alphatemp.domain(rg.options)  # KEVCOLD (n = everywhere)
    return out


@lru_cache(maxsize=32)
def _eendmax(Zt: int, At: int, enincmax_mev: float) -> dict:
    """`eendmax(type)`, the highest emission-grid point `inverse` ever fills: `eend(type)` at the
    run's highest incident energy (inverseecis.f90:402 loops to it once, before the energy loop).
    Note `eend` defaults to maxen - 1, so the grid's very last point is never filled.

    TALYS: energies.f90:1 (energies), basicxs.f90:1 (basicxs)
    Test: A-trans
    """
    c = talys_constants()
    rg = run_grid(Zt, At, enincmax_mev)
    eninccm, _ = incident_kinematics(
        enincmax_mev, rg.options.k0, float(rg.m.mass_amu[target_mass_index()]),
        float(rg.m.specmass[c["parZ"][rg.options.k0], c["parN"][rg.options.k0], rg.options.k0]),
        float(rg.m.redumass_amu[c["parZ"][rg.options.k0], c["parN"][rg.options.k0],
                                rg.options.k0]),
        rg.options.flagrel)
    ecomp = total_energy(eninccm, rg.s0[rg.options.k0], 0.0)
    eend, _ = emission_end(rg.egrid, rg.maxen, ecomp, {t: rg.s0[t] for t in range(7)},
                           rg.ebegin, {t: False for t in range(7)})
    return eend


def _tlogref_tables(Zt: int, At: int, rg, rg_params, lcap: int, eendmax) -> dict:
    """LOGTINT G0 reference: the run's inverse OMP solve (`omp_nx2.inverse_kept`, else `inverse.inverse_channels`) on
    the emission grid refined `tlog.REFINE`x, kept over the same [egrid(ebegin), egrid(eendmax)] window per type.
    {type: (efine, Tjl (Ef, L, 3) updown axis, Tl (Ef, L))} for the charged types 2..6."""
    from physics.hf.compound import tlog
    from physics.hf.core.grids import EmissionGrid
    from physics.hf.core.tensors import CaseBatch
    from physics.hf.omp.inverse import NJ, inverse_channels
    from physics.hf.omp.omp_nx2 import inverse_kept

    ef, _left = tlog.fine_grid(rg.egrid, rg.maxen)
    nf = ef.shape[0]
    keep = {}
    for t in range(1, 7):
        lo = float(rg.egrid[rg.ebegin[t]]) if rg.ebegin[t] >= 1 else float("inf")
        hi = float(rg.egrid[min(int(eendmax[t]), rg.maxen)])
        keep[t] = (np.arange(nf) >= 1) & (ef >= lo) & (ef <= hi) & (t >= 2)
    tr = inverse_kept(Zt, At, ef, nf - 1, rg.options, rg_params, lcap, keep)
    if tr is None:
        de = np.diff(ef, prepend=0.0)
        grid = EmissionGrid(torch.tensor(ef, dtype=DTYPE)[None], torch.tensor(de, dtype=DTYPE)[None],
                            torch.tensor(np.arange(nf) >= 1)[None], maxen=torch.tensor([nf - 1]))
        cases = CaseBatch(Z=torch.tensor([Zt]), A=torch.tensor([At]),
                          e_inc_mev=torch.tensor([float(rg.egrid[rg.maxen])], dtype=DTYPE),
                          projectile=PARSYM[rg.options.k0])  # charged-projectile fidelity: was "n"
        tr = inverse_channels(cases, grid, rg.options, rg_params, lmax=lcap)
    out = {}
    tj_all = torch.as_tensor(tr.tjl, dtype=DTYPE)
    L = tj_all.shape[-2]
    ll = torch.arange(L, dtype=DTYPE)
    for t in range(2, 7):
        tjl = torch.where(torch.as_tensor(keep[t])[:, None, None], tj_all[0, t - 1], torch.zeros((), dtype=DTYPE))
        nj = NJ[t]
        if nj == 2:
            tl = ((ll + 1) * tjl[..., 1] + ll * tjl[..., 0]) / (2 * ll + 1)
        elif nj == 3:
            tl = ((2 * ll + 3) * tjl[..., 2] + (2 * ll + 1) * tjl[..., 1]
                  + (2 * ll - 1) * tjl[..., 0]) / (3 * (2 * ll + 1))
        else:
            tl = tjl[..., 0]
        out[t] = (ef, _to_updown_axis(tjl, t).detach().numpy().astype(float), tl.detach().numpy().astype(float))
    return out


def _njmax(Zt: int, At: int, particle: int, egrid: np.ndarray) -> np.ndarray:
    """`njmax`, the number of j-values TALYS asks ECIS for at each emission energy
    (inverseecis.f90:409-411): int(2.4 * 1.25 * A^(1/3) * 0.22 * sqrt(m_proj E)), at least 20 and
    at most numl - 2. The port would otherwise solve more partial waves than TALYS has, and
    every extra l is a transmission coefficient TALYS reports as zero.

    TALYS: inverseecis.f90:1 (inverseecis)
    Test: A-trans
    """
    from physics.hf.core.constants import talys_constants
    from physics.hf.omp.schrodinger import nucleus_mass_amu

    c = talys_constants()
    Zc, Ac = compound_of(Zt, At)  # CPINC
    Zr = Zc - c["parZ"][particle]
    Ar = Ac - c["parA"][particle]
    m_res = nucleus_mass_amu(Zr, Ar)
    specmass = m_res / (m_res + c["parmass"][particle])
    e = np.maximum(np.asarray(egrid, float), 0.0) / specmass
    nj = (2.4 * 1.25 * float(Ar) ** (1.0 / 3.0) * 0.22 * np.sqrt(
        float(c["parmass"][particle]) * e)).astype(np.int64)
    return np.clip(nj, 20, NUML - 2)


def _lmax_inverseread(tjl: torch.Tensor, tl: torch.Tensor, particle: int) -> np.ndarray:
    """`lmax(type, nen)`, the last l before every T_lj falls under
    max(T_l(0) translimit / (2l+1), transeps) (inverseread.f90:163-215). -1 when even l = 0 is
    under it; 0 outside [ebegin, eend], where TALYS never computes it and the array keeps its
    reacinitial value -- which densprepare then copies into lmaxhf.

    TALYS: inverseread.f90:1 (inverseread)
    Test: A-trans
    """
    from physics.hf.omp.inverse import NJ, TRANSEPS_DEFAULT, TRANSLIMIT_DEFAULT

    nj = NJ[particle]
    L = tjl.shape[-2]
    ll = torch.arange(L, dtype=DTYPE)
    teps = torch.clamp_min(tl[:, :1] * TRANSLIMIT_DEFAULT / (2 * ll + 1), TRANSEPS_DEFAULT)
    small = (tjl[..., :nj] < teps[..., None]).all(-1)
    first = torch.where(small.any(-1), small.to(torch.int64).argmax(-1),
                        torch.full(small.shape[:-1], L))
    return (first - 1).detach().numpy().astype(np.int64).clip(min=-1)


def _to_updown_axis(tjl: torch.Tensor, particle: int) -> torch.Tensor:
    """The contract's padded j order -> TALYS's `Tjl(type, nen, updown, l)` axis (-1, 0, +1).

    They are the same array only for the deuteron. A spin-1/2 ejectile has updown = +-1, so
    T(l+1/2) belongs at index 2, not index 1; the alpha has parspin 0, so compprepare's
    `updown = (jj2 - l2)/spin2` is always 0 and its single T belongs at index 1. Reading the
    contract order as an updown axis silently moves every nucleon's j = l + 1/2 transmission
    onto the unused updown = 0 slot, which zeroes half the exit channels.

    TALYS: inverseread.f90:1 (inverseread), compprepare.f90:1 (compprepare)
    Test: A-trans
    """
    out = torch.zeros_like(tjl)
    if particle == 3:  # deuteron: spin 1, updown = -1, 0, +1 already
        return tjl
    if particle == 0:  # ENGPROJ: incident photon, Tjlinc(irad, l) is stored at index irad + 1 already (incident_gamma)
        return tjl
    if particle == 6:  # alpha: spin 0, only updown = 0
        out[..., 1] = tjl[..., 0]
        return out
    out[..., 0] = tjl[..., 0]  # j = l - 1/2
    out[..., 2] = tjl[..., 1]  # j = l + 1/2
    return out


# ------------------------------------------------------------------------------------------------
# T7: f_XL of the compound nucleus
# ------------------------------------------------------------------------------------------------


@lru_cache(maxsize=32)
def _gamma_parameters(Zt: int, At: int, fit: tuple | None = None):
    """T7's `GammaParameters` for the compound nucleus (Zt, At + 1).

    `fit` (PARAMWIRE) is `density.overrides.gamma_token` of that nucleus -- its `aadjust`, E1
    `ftable` and E1 `wtable` from a parameter set -- and part of the key; the defaults are called
    with two arguments, as before.

    TALYS: gammapar.f90:1 (gammapar)
    Test: A-psf
    """
    if fit is None:
        return _build_gamma_parameters(Zt, At, None)
    return _build_gamma_parameters(Zt, At, None, fit)


@lru_cache(maxsize=64)
def _gamma_parameters_nuc(Z: int, A: int, fit: tuple | None = None):
    """ENGPROJ GPRESFIX: `_gamma_parameters` of the nucleus (Z, A) itself (not of a pseudo-target's compound).

    TALYS: gammapar.f90:1 (gammapar)
    Test: tests/hf/test_engproj_gamma.py
    """
    return _build_gamma_parameters(Z, A, None, fit, nucleus=(Z, A))


@stagetime.timed("setup.psf")
def _build_gamma_parameters(Zt: int, At: int, overrides: dict | None, fit: tuple | None = None,
                            nucleus: tuple | None = None):
    """`_gamma_parameters` with T7's `overrides` (requires_grad tensors keep their graph).

    PARAMWIRE: `fit`'s `aadjust` reaches `alev` (densitypar with the adjusted `Params`, as TALYS's
    fstrength reads `alev(Zcomp, Ncomp)`), its `ftable`/`wtable` reach the E1 table. An explicit
    `overrides` entry wins over the parameter set's for the same field.
    """
    from physics.hf.density.overrides import gamma_fit_overrides, with_aadjust
    from physics.hf.density.parameters import densitypar
    from physics.hf.gamma.parameters import gamma_parameters

    from physics.hf.projectile import gpres_active, k0 as _k0, pseudo_target

    if nucleus is not None:  # ENGPROJ GPRESFIX: the run whose initial compound nucleus IS this nucleus
        Zt, At = pseudo_target(int(nucleus[0]), int(nucleus[1]))
    o, p, m = _structure_of(Zt, At)
    Zc, Ac = compound_of(Zt, At)  # CPINC: (Zt, At + 1) for a neutron
    s_type = _k0() if gpres_active() else 1  # GPRESFIX: S(Zcomp, Ncomp, k0) (fstrength.f90:192); legacy S_n
    lv = discrete_levels(Zc, Ac, o, m, p)
    if fit is not None and fit[0] is not None:
        p = with_aadjust(p, o, ((Zc, Ac, fit[0]),))
    ld = densitypar(Zc, Ac, o, p, m, lv)
    fov = gamma_fit_overrides(fit, int(o.gammax))
    if fov:
        overrides = {**fov, **(overrides or {})}
    # BESTFIT: `wtable`/`ftable` from `best`/`ng.par` belong to this nucleus and are owned by
    # `gamma_parameters` (it builds its own defaults), so they come in through `overrides` too
    from physics.hf.input import fitlib

    gov = fitlib.gamma_overrides(Zc, Ac, int(o.gammax))
    if gov:
        overrides = {**gov, **(overrides or {})}
    return gamma_parameters(
        Zc, Ac, o, zix=0, nix=0, S_k0_mev=float(m.s_mev[0, 0, s_type]),
        delta_mev=float(ld.delta_mev[0]), alev_per_mev=float(ld.alev),
        beta2=float(ld.beta2[0]), projectile_k0=o.k0, flagcol=bool(ld.flagcol),
        overrides=overrides,
    ), o


@stagetime.timed("setup.psf")
def strength_fn(Zt: int, At: int, e_inc_mev: float, overrides: dict | None = None,
                fit: tuple | None = None, nucleus: tuple | None = None):
    """`fstrength(Efs, Egamma, irad, l)` for the compound nucleus, T7's port.

    With `overrides` (T7's `gamma_parameters` overrides: `ftable`, `wtable`, `sgr_mb`, ... as
    requires_grad tensors) the parameters are built for them and `f.batch` returns tensors that
    carry the graph; `f.differentiable` says which one the caller got.

    TALYS: fstrength.f90:1 (fstrength)
    Test: A-psf
    """
    from physics.hf.density.overrides import torch_path
    from physics.hf.gamma.strength import fstrength

    if overrides:
        gp, o = _build_gamma_parameters(Zt, At, overrides, fit, nucleus=nucleus)
    elif nucleus is not None:  # ENGPROJ GPRESFIX
        gp, o = _gamma_parameters_nuc(int(nucleus[0]), int(nucleus[1]), fit)
    else:
        gp, o = _gamma_parameters(Zt, At) if fit is None else _gamma_parameters(Zt, At, fit)
    # PARAMWIRE: only a TENSOR override is on a graph; float overrides and parameter sets return
    # numpy like the defaults, so the numpy / NATIVEX paths can take them
    diff = torch_path(overrides)

    def f(efs_mev: float, egamma_mev: float, irad: int, l: int) -> float:  # noqa: E741
        return float(fstrength(0, 0, efs_mev, torch.tensor(egamma_mev, dtype=DTYPE),
                               irad, l, gp, o, e_inc_mev))

    def batch(efs_mev: float, egamma_mev, irad: int, l: int) -> np.ndarray:  # noqa: E741
        """`f` on a whole list of Egamma in one call (fstrength is elementwise in Egamma)."""
        v = fstrength(0, 0, efs_mev, torch.tensor(egamma_mev, dtype=DTYPE),
                      irad, l, gp, o, e_inc_mev)
        return v if diff else v.detach().numpy()

    f.batch = batch
    f.differentiable = diff
    f.gp = gp  # what psf_fast.fstrength_np evaluates on the numpy path
    return f


# ------------------------------------------------------------------------------------------------
# assembly
# ------------------------------------------------------------------------------------------------


def dens_inputs(inp: CompoundInputs, Zt: int, At: int, enincmax_mev: float) -> DensPrepareInputs:
    """The `DensPrepareInputs` of one incident energy: ported rhogrid / Tjl / f_XL on the grid
    the dump carries.

    TALYS: densprepare.f90:1 (densprepare)
    Test: A-cn1
    """
    c = talys_constants()
    rg = run_grid(Zt, At, enincmax_mev)
    tr_all = _transmission(Zt, At, enincmax_mev)
    Zc, Ac = compound_of(Zt, At)  # CPINC: (Zt, At + 1) for a neutron
    eninccm, _ = incident_kinematics(
        inp.e_inc_mev, inp.k0, float(rg.m.mass_amu[target_mass_index()]),
        float(rg.m.specmass[c["parZ"][inp.k0], c["parN"][inp.k0], inp.k0]),
        float(rg.m.redumass_amu[c["parZ"][inp.k0], c["parN"][inp.k0], inp.k0]),
        rg.options.flagrel)
    ecomp = total_energy(eninccm, rg.s0[inp.k0], 0.0)
    eend, _ = emission_end(rg.egrid, rg.maxen, ecomp, {t: rg.s0[t] for t in range(7)},
                           rg.ebegin, {t: False for t in range(7)})
    residuals, trans = {}, {}
    for t, r in sorted(inp.residuals.items()):
        n = r.maxex + 1
        Zr, Ar = Zc - c["parZ"][t], Ac - c["parA"][t]
        _, ntop, _, ncum = _ld_of(Zr, Ar, Zt, At)
        residuals[t] = DensResidual(
            type=t, zix=r.zix, nix=r.nix, A=Ar, nlast=min(r.nlast, r.maxex), ntop=ntop,
            nexmax=r.maxex, sep_mev=r.sep_mev,
            ex_mev=np.asarray(r.ex_mev, float), dex_mev=np.asarray(r.dex_mev, float),
            maxj=np.asarray(r.maxj, np.int64), parlev=np.asarray(r.parlev, np.int64),
            jdis=np.where(r.jdis2 >= 0, r.jdis2 / 2.0, 0.0),
            rhogrid=rhogrid_of(Zr, Ar, Zt, At, np.asarray(r.ex_mev, float),
                               np.asarray(r.dex_mev, float), np.asarray(r.maxj, np.int64),
                               min(r.nlast, r.maxex)),
            ncum_nl=ncum,
        )
        del n
        if t >= 1:
            tjl, tl, lmax = tr_all[t]
            trans[t] = DensTrans(egrid_mev=rg.egrid, ebegin=rg.ebegin[t],
                                 eend=min(eend[t], rg.maxen), maxen=rg.maxen,
                                 tjl=tjl, tl=tl, lmax=lmax)
    return DensPrepareInputs(
        exinc_mev=inp.exinc_mev, dexinc_mev=inp.dexinc_mev,
        s_n_mev=rg.s0[1], gammax=inp.gammax, lmaxinc=inp.lmaxinc, k0=inp.k0,
        fnorm=np.asarray(inp.fnorm, float), residuals=residuals, trans=trans,
        gamma_strength=strength_fn(Zt, At, inp.e_inc_mev), primary=True,
        flagfullhf=False, transeps=TRANSEPS,
    )


# ------------------------------------------------------------------------------------------------
# gate
# ------------------------------------------------------------------------------------------------


def _r(p: np.ndarray, t: np.ndarray, floor: float) -> np.ndarray:
    """|ln(p/t)| over the points where |t| > floor; inf where TALYS has nothing and the port
    does (gates doc §2)."""
    live = np.abs(t) > floor
    out = np.full(t.shape, np.nan)
    both = live & (np.abs(p) > 0)
    out[both] = np.abs(np.log(np.abs(p[both] / t[both])))
    out[live & ~both] = np.inf
    born = ~live & (np.abs(p) > floor)
    out[born] = np.inf
    return out[live | born]


def _stats(vals: list[np.ndarray], tol: float) -> dict:
    v = np.concatenate(vals) if vals else np.array([])
    if v.size == 0:
        return {"n": 0}
    fin = v[np.isfinite(v)]
    return {
        "n": int(v.size), "n_inf": int((~np.isfinite(v)).sum()),
        "p95": float(np.percentile(fin, 95)) if fin.size else None,
        "median": float(np.median(fin)) if fin.size else None,
        "max": float(fin.max()) if fin.size else None,
        "tolerance": tol,
        "pass": bool(fin.size and np.percentile(fin, 95) <= tol and not (~np.isfinite(v)).any()),
    }


def score_case(inp: CompoundInputs, got: dict) -> dict:
    """Compare the four densprepare arrays against the dump, cell by cell, at the tolerance of
    the component each comes from: Tjlnex/Tlnex A-trans (1e-2), rho0 A-ld tables (2e-2),
    Tgam A-psf (1e-2). `lmaxhf` is exact.
    """
    rho_r, tjl_r, tgam_r = [], [], []
    lmax_ok = lmax_n = 0
    stale = 0
    overwritten = 0
    for t, ref in sorted(inp.residuals.items()):
        g = got[t]
        n = ref.maxex + 1
        lmax_n += n
        lmax_ok += int((g.lmaxhf[:n] == ref.lmaxhf[:n]).sum())
        # rho0: only the cells TALYS's own consumers read (see the stale-scratch note)
        mask = np.zeros((n, NUMJ + 1, 2), dtype=bool)
        nl = min(ref.nlast, ref.maxex)
        for k in range(n):
            if k <= nl:
                ir = int(ref.jdis2[k]) // 2 if ref.jdis2[k] >= 0 else -1
                if 0 <= ir <= NUMJ:
                    mask[k, ir, 0 if ref.parlev[k] < 0 else 1] = True
            else:
                mask[k, : int(ref.maxj[k]) + 1, :] = True
        stale += int(((ref.rho != 0) & ~mask).sum())
        rho_r.append(_r(g.rho[mask], ref.rho[mask], 1.0e-10))
        if t == 0:
            if ref.tgam is not None and g.tgam is not None:
                a, b = g.tgam, ref.tgam
                k = min(a.shape[0], b.shape[0])
                # densprepare writes Tgam only for Ir = 0..maxJ(nexout); above that the cell keeps
                # whatever an earlier nucleus/energy left, and comptarget.f90:610 indexes it with
                # the COMPOUND J, so TALYS can read a stale cell. Gate the written cells.
                m = np.zeros(a.shape[:1] + (1, 1, NUMJ + 1, 1), dtype=bool)
                for q in range(k):
                    m[q, :, :, : int(ref.maxj[q]) + 1] = True
                m = np.broadcast_to(m, a[:k].shape)
                stale += int(((b[:k] != 0) & ~m).sum())
                tgam_r.append(_r(a[:k][m], b[:k][m], 1.0e-12))
        elif ref.tjl is not None and g.tjl is not None:
            L = min(g.tjl.shape[1], ref.tjl.shape[1])
            rows = np.ones(n, dtype=bool)
            if t == inp.k0 and 0 <= inp.ltarget < n:
                # The dump is written inside comptarget, AFTER comptarget.f90:358-362 replaces
                # the incident channel's interpolated Tjlnex by the exact Tjlinc, so this one row
                # is not densprepare's output and scoring it here measured an overwrite that had
                # not happened yet. It is counted, and gated end to end by score_xspop, which
                # runs `compound.target` and therefore does apply the overwrite.
                rows[inp.ltarget] = False
                overwritten += int((ref.tjl[inp.ltarget, :L] != 0).sum())
            tjl_r.append(_r(g.tjl[:n, :L][rows].ravel(), ref.tjl[:n, :L][rows].ravel(), 1.0e-6))
    return {"rho0": rho_r, "tjlnex": tjl_r, "tgam": tgam_r, "lmaxhf": (lmax_ok, lmax_n),
            "stale_cells": stale, "tjlinc_cells": overwritten}


def score_run(work: Path, Zt: int, At: int, limit: int | None = None) -> dict:
    """Gate `densprepare` over every incident energy of one instrumented run."""
    from physics.hf.compound.prepare import load_cn_dump

    cases = load_cn_dump(Path(work) / "cn_inputs.txt")
    if limit:
        cases = cases[:limit]
    enincmax = max(c.e_inc_mev for c in cases)
    acc: dict[str, list] = {"rho0": [], "tjlnex": [], "tgam": []}
    ok = tot = stale = over = 0
    for c in cases:
        got = densprepare(dens_inputs(c, Zt, At, enincmax))
        s = score_case(c, got)
        for k in acc:
            acc[k] += s[k]
        ok += s["lmaxhf"][0]
        tot += s["lmaxhf"][1]
        stale += s["stale_cells"]
        over += s["tjlinc_cells"]
    return {
        "run": Path(work).name, "energies": len(cases),
        "rho0": _stats(acc["rho0"], 0.02),
        "tjlnex": _stats(acc["tjlnex"], 0.01),
        "tgam": _stats(acc["tgam"], 0.01),
        "lmaxhf_exact": [ok, tot], "stale_cells": stale, "tjlinc_cells": over,
    }


# ------------------------------------------------------------------------------------------------
# chained A-cn: comptarget on BUILT densprepare arrays instead of injected ones
# ------------------------------------------------------------------------------------------------


def chained_compound_inputs(inp: CompoundInputs, Zt: int, At: int, enincmax_mev: float):
    """`inp` with its four densprepare arrays (and lmaxhf) replaced by the ported ones.

    Everything else comptarget reads stays injected: `CNfactor`/`xsflux` (compnorm.f90),
    `Tjlinc`/`lmaxinc` (the incident channel, T5/T13), `J2beg`/`J2end` (population.f90) and the
    fission transmission (T11). This isolates the densprepare seam inside A-cn.

    TALYS: comptarget.f90:1 (comptarget)
    Test: A-cn1
    """
    from copy import copy

    got = densprepare(dens_inputs(inp, Zt, At, enincmax_mev))
    out = copy(inp)
    out.residuals = {t: got[t] for t in sorted(inp.residuals)}
    return out


def score_xspop(work: Path, Zt: int, At: int, limit: int | None = None) -> dict:
    """A-cn on the built arrays: comptarget's `xspop(type, nex, J, P)` against TALYS's own, over
    every incident energy of one instrumented run. Tolerance 0.01 (`wfc_off`) / 0.02 (default),
    populations floor 1e-6 mb (gates doc §2).
    """
    from physics.hf.compound.prepare import load_cn_dump
    from physics.hf.compound.target import compound_target_inputs

    cases = load_cn_dump(Path(work) / "cn_inputs.txt")
    if limit:
        cases = cases[:limit]
    enincmax = max(c.e_inc_mev for c in cases)
    tol = 0.01 if "wfc_off" in Path(work).name else 0.02
    rs, el = [], []
    for c in cases:
        pop = compound_target_inputs(chained_compound_inputs(c, Zt, At, enincmax)).pop_mb[0]
        for t, ref in sorted(c.ref_pop_mb.items()):
            n = min(ref.shape[0], pop.shape[1])
            rs.append(_r(pop[t, :n].numpy().ravel(), ref[:n].ravel(), 1.0e-6))
        ref_el = c.ref_xsbinary_mb
        if ref_el is not None and abs(ref_el[0]) > 1.0e-3:
            got_el = float(pop[c.k0, c.ltarget].sum())
            el.append(_r(np.array([got_el]), np.array([float(ref_el[0])]), 1.0e-3))
    return {"run": Path(work).name, "energies": len(cases),
            "xspop": _stats(rs, tol), "compound_elastic": _stats(el, tol)}


def main(argv=None) -> None:
    import argparse
    import tarfile

    from physics.hf.talys_reference import REFERENCE_SET

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--runs", default=str(Path.home() / "hf_t10/runs"))
    ap.add_argument("--work", default=str(Path.home() / "e2e_work"))
    ap.add_argument("--out", default="docs/results/hf-densprepare-gate.json")
    ap.add_argument("--only", default="")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--xspop", action="store_true",
                    help="also run the chained A-cn gate on comptarget")
    a = ap.parse_args(argv)
    torch.set_num_threads(2)
    work = Path(a.work).expanduser()
    work.mkdir(parents=True, exist_ok=True)
    za = {t.tag: (t.Z, t.A) for t in REFERENCE_SET}
    recs = []
    for tar in sorted(Path(a.runs).expanduser().glob("*.tar.gz")):
        tag = tar.name[: -len(".tar.gz")]
        if a.only and a.only not in tag:
            continue
        d = work / tag
        if not (d / "cn_inputs.txt").is_file():
            with tarfile.open(tar) as tf:
                tf.extractall(work)
        if not (d / "cn_inputs.txt").is_file():
            continue
        Z, A = za[tag.split("__")[-1]]
        rec = score_run(d, Z, A, a.limit or None)
        if a.xspop:
            rec.update(score_xspop(d, Z, A, a.limit or None))
        recs.append(rec)
        print(json.dumps(rec), flush=True)
    pool = {k: _stats([np.array([r[k]["p95"]]) for r in recs if r[k]["n"]], r0)
            for k, r0 in (("rho0", 0.02), ("tjlnex", 0.01), ("tgam", 0.01))}
    out = {"runs": recs, "worst_p95": {k: max((r[k]["p95"] or 0.0) for r in recs) if recs else None
                                       for k in ("rho0", "tjlnex", "tgam")}}
    del pool
    Path(a.out).write_text(json.dumps(out, indent=1))
    print(json.dumps(out["worst_p95"], indent=1))


if __name__ == "__main__":
    main()
