"""The multiple-emission feeding chain: build `multiple.f90`'s per-nucleus grids and run T9's
continuum decay over every populated bin, so that `channels.f90` consumes a COMPUTED `feedexcl`
instead of TALYS's own.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T10, continued by EXCL (physics/hf/CONTRACT.md §7). Acceptance test: A-mult / E2E (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    exgrid.f90:1 (exgrid)        -- driven per cascade nucleus, with TALYS's latching order
    isotrans.f90:1 (isotrans)    -- the `fisom` factor `Fnorm` divides by
    multiple.f90:1 (multiple)    -- only the set-up this module owns; the bookkeeping is
                                    `emission.multiple.multiple_emission` (T10)

`emission.multiple.multiple_emission` (T10) and `compound.continuum.compound_decay` (T9) were both
already ported, but nothing joined them: `multiple_emission` takes a `decay(zcomp, ncomp, nex)`
callback and the only caller passed a dump. This module is that callback. For each mother bin it
builds a `densprepare(primary=False)` input set out of T5's transmission, T6's level densities and
T7's photon strength, runs `densprepare`, and hands the result to `compound_decay`.

Three things about TALYS's book-keeping that a naive assembly gets wrong, each reproduced here:

* **`flagompall` is false by default** (input_basicreaction.f90), so `basicxs` runs exactly once,
  for the initial compound nucleus (talysreaction.f90:88). Every nucleus in the cascade therefore
  decays through the *same* `Tjl(type, nen, updown, l)` -- the one computed for the daughters of
  (0, 0). Recomputing the optical model per residual is not more faithful, it is a different
  calculation.
* **`exgrid`'s grids latch.** `if (maxex(Zix, Nix) /= 0) cycle` (exgrid.f90:163) and the identical
  guard on `Exmax`: a nucleus's excitation grid is built by the *first* mother that reaches it, in
  the loop order `Zcomp = 0..maxZ, Ncomp = 0..maxN`, and later mothers reuse it. `reacinitial`
  clears the latch once per incident energy (reacinitial.f90:503-508), so it is energy-scoped.
* **`isotrans`'s `fisom` is spent on exactly one (nucleus, incident energy) of a run.**
  `fiso`/`fisom` are set to -1 in `input_gammapar.f90:102-103`, i.e. at input parsing, and
  `isotrans` only overwrites an entry that is still -1 (isotrans.f90:63-82) -- but
  multiple.f90:458-460 resets `fisom(0:6)` to 1 immediately after :437 has formed `Fnorm` from it.
  So the initial compound nucleus at the run's FIRST incident energy decays with
  `Fnorm = 1 / ff`, over all of its excitation bins, and every other nucleus at every other
  energy decays with `Fnorm = 1`. For an incident neutron the only affected entry is `fisom(0)`,
  which is 2 when that nucleus has Z == N and 1.5 when |Z - N| == 1 -- e.g. Ca-41, the initial
  compound nucleus of the Ca-40 run. `Cascade.fisom` is a pure function of (zix, nix) and
  `ChainState.first_energy`, so which energy is first comes from the run's DECLARED grid
  (`Cascade(..., energies=...)`) and not from the order a caller walks it in; an energy subset,
  a batched width build and a sharded run therefore all give the full run's number.

What is still injected, and named rather than hidden: the mother populations come from `binary`
(T10) fed by `comptarget` (T9), i.e. they are as chained as `engine.ChainedCompound` makes them;
`multipreeq2.f90` is ported (`preeq.multi`, gate A-mpe) and driven from here by `Cascade.mpe`,
so at `Einc >= emulpre` (20 MeV, the last reference energy only) each mother bin is depleted by
multiple pre-equilibrium exactly as TALYS depletes it; and the fission transmission is T11's,
injected per (J, parity) for the actinides.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache

import numpy as np
import torch

from physics.hf.compound.prepare import (
    NUMJ,
    DensPrepareInputs,
    DensResidual,
    densprepare,
)
from physics.hf.core.tensors import DTYPE
from physics.hf.emission.multiple import BinFeeding, NucleusPopulation

PARZ = (0, 0, 1, 1, 1, 2, 2)
PARN = (0, 1, 0, 1, 2, 1, 2)
PARA = (0, 1, 1, 2, 3, 3, 4)
# A0_talys_mod.f90:23-33 with memorypar = 6 gives numZ = 14, numN = 34; T2's mass tables are
# built to (15, 31), so the cascade tree is carried as far as they reach and no further -- a
# nucleus outside them has Exmax = 0 and `populations` drops it, which is also what TALYS's
# `skipCN` does to a nucleus with no flux.
NUMZ = 14
NUMN = 30


def _pad(v, n: int):
    """`v` cut or zero-extended to length `n`, the way TALYS's fixed-size arrays behave."""
    out = torch.zeros(n, dtype=DTYPE)
    k = min(n, v.shape[0])
    out[:k] = v[:k]
    return out


_SPINCUT_PARTS: dict = {}


def _spincut_parts(ld) -> tuple:
    """The Eex-independent half of `density.parameters.spincut(ld, ald, Eex, ibar=0, ipop=0)`,
    computed by its own torch expressions once per level-density record and kept as floats."""
    got = _SPINCUT_PARTS.get(id(ld))
    if got is not None and got[0] is ld:
        return got[1]
    from physics.hf.density.parameters import _fv, ignatyuk

    ibar = 0
    Rs, s2, ldmod = ld.Rspincut, ld.s2adjust[ibar], ld.ldmodel
    scutconst = (Rs * s2 * ld.Irigid0 / ld.alimit if ld.spincutmodel == 1
                 else Rs * s2 * ld.Irigid0)
    Em = ld.Exmatch_mev[ibar]
    if ldmod == 2 or ldmod >= 4:
        Em = ld.S_mev
    if ldmod == 3:
        Em = ld.Ucrit_mev[ibar] - ld.pair_mev - ld.Pshift_mev[ibar]
    sdisc = ld.scutoffdisc[ibar]
    aldm = ignatyuk(ld, Em, ibar)
    Umatch = Em - ld.pair_mev - ld.Pshift_mev[ibar]
    okm = Umatch > 0.0
    Um = torch.where(okm, Umatch, torch.ones_like(Umatch))
    if ld.spincutmodel == 1:
        s2m = (scutconst * ld.aldcrit[ibar] * ld.Tcrit_mev if ldmod == 3
               else scutconst * torch.sqrt(aldm * Um))
    else:
        s2m = scutconst * ld.Tcrit_mev if ldmod == 3 else scutconst * torch.sqrt(Um / aldm)
    s2m = torch.where(okm, s2m, sdisc)
    Ed = ld.Ediscrete_mev[ibar]
    interp = _fv(Em) != _fv(Ed)
    denom = float(Em - Ed) if interp else 1.0
    parts = (float(scutconst), float(Em), float(sdisc), float(s2m), float(Ed), denom, interp,
             float(ld.delta_mev[ibar]), int(ld.spincutmodel))
    _SPINCUT_PARTS[id(ld)] = (ld, parts)
    return parts


def _spincut_np(ld, ald: float, eex: np.ndarray) -> np.ndarray:
    """`density.parameters.spincut(ld, ald, eex, 0, 0)` for a scalar `ald`, on numpy. The per-bin
    half is +, -, *, / (numpy) and one torch sqrt in the torch function's order: the same double
    arithmetic, bit for bit."""
    scutconst, Em, sdisc, s2m, Ed, denom, interp, delta, model = _spincut_parts(ld)
    below = np.where(interp & (eex > Ed), sdisc + (eex - Ed) / denom * (s2m - sdisc), sdisc)
    U = eex - delta
    okU = U > 0.0
    Us = np.where(okU, U, 1.0)
    # torch's sqrt, not numpy's: on x86 the two differ in the last bit now and then
    root = torch.sqrt(torch.from_numpy(ald * Us if model == 1 else Us / ald)).numpy()
    above = scutconst * root
    above = np.where(okU, above, sdisc)
    return np.maximum(sdisc, np.where(eex <= Em, below, above))


def _maxj_of(ld, ald: float, eex: np.ndarray) -> np.ndarray:
    """`max_spin_index(spincut(ld, ald, eex))`: exgrid.f90's maxJ with a = A/8, the float32 cast
    and truncation as torch does them."""
    s = _spincut_np(ld, ald, eex).astype(np.float32)
    root = torch.sqrt(torch.from_numpy(s)).numpy()
    return np.minimum((np.float32(4.0) + np.float32(3.0) * root).astype(np.int64), NUMJ)


@dataclass
class NucleusSpec:
    """One cascade nucleus after `exgrid` and `structure`: what the decay of its bins reads."""

    zix: int
    nix: int
    Z: int
    A: int
    nlast: int  # Nlast(Zix, Nix, 0), UNCLAMPED: densprepare's discfactor divides by NL - Ntop
    nlast_grid: int  # min(Nlast, maxex): the last discrete level the grid actually holds
    ntop: int
    ncum_nl: float | torch.Tensor  # Tensor under a DIFFPARAM level-density override
    maxex: int
    exmax_mev: float
    ex_mev: np.ndarray  # (maxex+1,)
    dex_mev: np.ndarray
    maxj: np.ndarray  # (maxex+1,) int
    parlev: np.ndarray  # (maxex+1,) int, discrete levels only
    jdis: np.ndarray  # (maxex+1,) float, discrete levels only
    tau_s: np.ndarray  # (maxex+1,)
    branch: dict[int, list[tuple[int, float]]]
    sep_mev: dict[int, float]  # type -> S(zix, nix, type)
    rhogrid: np.ndarray  # (maxex+1, numJ+1, 2)
    nfisbar: int = 0


@dataclass
class ChainState:
    """`reacinitial`'s per-energy latches (reacinitial.f90:503-508)."""

    exmax0: np.ndarray
    exmax: np.ndarray
    lmaxinc: int = 0  # densprepare.f90:397 overwrites lmaxhf(k0, 0) with it at EVERY call
    maxex: dict[tuple[int, int], int] = field(default_factory=dict)
    spec: dict[tuple[int, int], NucleusSpec] = field(default_factory=dict)
    e_inc_mev: float | None = None
    # `fisom`'s -1 sentinel is live for the whole of ONE (nucleus, incident energy) of a run,
    # and this says whether THIS energy is that one (`Cascade.fisom`). It is set from the run's
    # declared energy grid, never from the order in which energies happen to be computed.
    first_energy: bool = True


class Cascade:
    """The cascade of one target: run-scoped structure, per-energy grids, and the `decay` callback
    `multiple_emission` needs.

    TALYS: multiple.f90:1 (multiple), exgrid.f90:1 (exgrid), isotrans.f90:1 (isotrans)
    Test: A-mult / E2E
    """

    def __init__(self, Zt: int, At: int, enincmax_mev: float, *, k0: int = 1,
                 gammax: int = 2, flagfullhf: bool = False, transeps: float = 1.0e-8,
                 energies: tuple[float, ...] | None = None):
        from physics.hf.compound.dens_reference import run_grid
        from physics.hf.input import fitlib

        # BESTFIT: this is the run's target, and it is where every path (Python, C, fast, GPU)
        # starts. `activate` is a no-op unless INCOGNITA_TALYS_FIT asks for TENDL's knobs.
        fitlib.activate(int(Zt), int(At))
        self.Zt, self.At, self.enincmax = Zt, At, enincmax_mev
        # The run's DECLARED incident energy grid, in TALYS's own order. `fisom` needs it (and
        # only it) to know which energy is the run's first; a Cascade built without one is a
        # one-energy run, so every energy it is handed is that run's first.
        self.energies = tuple(float(e) for e in energies) if energies is not None else None
        self.Zc, self.Ac = Zt, At + 1  # the initial compound nucleus
        self.k0, self.gammax = k0, gammax
        self.flagfullhf, self.transeps = flagfullhf, transeps
        self.rg = run_grid(Zt, At, enincmax_mev)
        self.options, self.params, self.m = self.rg.options, self.rg.params, self.rg.m
        from physics.hf.input.defaults import reject_unported

        reject_unported(self.options)  # a calculation must not run on an unported keyword
        # SPEED0: decay all bins of a nucleus through compound.decay_batch (False: per bin)
        self.batched = True
        # SPEED0 G0.3: T7 overrides (requires_grad) for the INITIAL compound nucleus's photon
        # strength; None is TALYS's defaults
        self.gamma_overrides: dict | None = None
        self._gamma_override_fn = None
        # DIFFPARAM: TALYS-keyword overrides for the other two families (`density.overrides`).
        # `diff_params` is set when either carries a tensor, and it is what switches the level
        # density and the transmission coefficients from numpy to the graph; the caches below
        # replace the module-level `lru_cache`es those two bypass when overridden.
        self.density_overrides: dict | None = None
        self.omp_overrides: dict | None = None
        self.matching_xacc: float | None = None
        self.diff_params = False
        self._trans_cache: dict | None = None
        # PARAMWIRE: the run's fit parameter set (`density.overrides.fit_params`), plain floats in
        # absolute (keyword, Z, A, value) form. It keys the level-density and photon-strength
        # caches instead of bypassing them, and keeps the numpy / NATIVEX paths on. Set per run by
        # `engine.ChainedFull(params=...)`, so one Cascade serves successive parameter points.
        self.fit: tuple = ()
        self.fission_fit: tuple = ()
        self.ndens = 0  # densprepare calls, for the speed table

    @property
    def trans(self) -> dict:
        """T5's `Tjl`/`Tl`/`lmax` on the emission grid. `flagompall` is false, so there is exactly
        ONE set for the whole cascade -- the initial compound nucleus's (talysreaction.f90:88).
        Built on first use, because it is the expensive part of the set-up and the grid logic
        above does not need it.

        TALYS: inverse.f90:1 (inverse), basicxs.f90:1 (basicxs)
        Test: A-trans
        """
        from physics.hf.compound.dens_reference import _transmission

        if not self.omp_overrides and not self.diff_params:
            return _transmission(self.Zt, self.At, self.enincmax)
        if self._trans_cache is None:  # per-Cascade: `inverse_channels` is the expensive call
            self._trans_cache = _transmission(
                self.Zt, self.At, self.enincmax, self.omp_overrides, self.diff_params)
        return self._trans_cache

    def set_param_overrides(self, density: dict | None = None, optical: dict | None = None,
                            matching_xacc: float | None = None) -> None:
        """Install DIFFPARAM's level-density / optical-model keyword overrides on this run.

        Both are mappings of a lowercase TALYS keyword to a value `input.defaults.default_params`
        accepts (a scalar, a full tensor of the keyword's shape, or `{"n": ...}` per particle).
        A tensor in either switches the whole run onto the torch path -- level densities,
        emission-grid transmission, `Tjlinc` and `cnfactor` stop being numpy -- so that a loss
        built from `capture_fast.capture_xs(..., differentiable=True)` reaches them.

        The two families are resolved into `Params` together (`self.params`, which the incident
        channel reads) but handed to their own consumers separately, so a density-only fit never
        rebuilds `inverse_channels` and an optical-only fit never rebuilds `LDNucleus`.

        TALYS: talysinput.f90:1 (talysinput)
        Test: G0.4 / tests/hf/test_capture_fast.py
        """
        from physics.hf.compound.dens_reference import structure_of
        from physics.hf.density import overrides as ov

        self.matching_xacc = matching_xacc
        self.density_overrides = ov.check(density, "density")
        self.omp_overrides = ov.check(optical, "optical")
        merged = ov.merge(self.density_overrides, self.omp_overrides)
        self.diff_params = ov.torch_path(merged)
        self._trans_cache = None
        # `incident` and `_levels` are `lru_cache`d per instance and keyed on `self`, so a fresh
        # Cascade has no entries: call this before the first energy (as `capture_fast.target`
        # does) and there is nothing to invalidate. Clearing them here would empty the caches of
        # every OTHER live Cascade, which is what an `lru_cache` on a method does.
        self.options, self.params, self.m = structure_of(self.Zt, self.At, merged)

    def set_fit_params(self, fit) -> None:
        """Install a PARAMWIRE parameter set (`density.overrides.fit_params` form) on this run.

        Nothing is dropped: every cache that reads a parameter carries it in its key (the spec
        memo below, `dens_reference._ld_of_cached` / `_gamma_parameters`,
        `pop_reference._preeq`), so a new point misses exactly the entries it reaches.

        TALYS: talysinput.f90:1 (talysinput)
        Test: tests/hf/test_paramwire.py
        """
        from physics.hf.density import overrides as ov

        fit = ov.fit_params(fit)
        # FISBARWIRE: the fission keywords reach only the fission chain (`fission_fit`), so every
        # other cache keyed by `fit` is the same with or without them
        self.fit = ov.without_fission(fit)
        self.fission_fit = ov.fission_entries(fit)

    def ld_token(self, Z: int, A: int) -> float | None:
        from physics.hf.density.overrides import ld_token

        return ld_token(self.fit, Z, A) if self.fit else None

    def ld_of(self, Z: int, A: int):
        """`dens_reference._ld_of` for (Z, A) on this run: DIFFPARAM overrides and the parameter
        set's `aadjust` at (Z, A)."""
        from physics.hf.compound.dens_reference import _ld_of

        return _ld_of(Z, A, self.Zt, self.At, self.density_overrides, self.matching_xacc,
                      self.ld_token(Z, A))

    def gamma_strength(self, Zt: int, At: int):
        """`dens_reference.strength_fn` for the compound nucleus (Zt, At + 1), honouring
        `gamma_overrides` when that nucleus is this run's initial compound nucleus, and the
        parameter set's `aadjust`/`ftable`/`wtable` of (Zt, At + 1) (PARAMWIRE) for every nucleus.

        TALYS: fstrength.f90:1 (fstrength)
        Test: A-psf / G0.3
        """
        from physics.hf.compound.dens_reference import strength_fn
        from physics.hf.density.overrides import gamma_token

        tok = gamma_token(self.fit, Zt, At + 1) if self.fit else None
        if self.gamma_overrides and (Zt, At) == (self.Zt, self.At):
            got = self._gamma_override_fn
            if got is None or getattr(got, "fit_token", None) != tok:
                got = strength_fn(Zt, At, self.enincmax, self.gamma_overrides, tok)
                got.fit_token = tok
                self._gamma_override_fn = got
            return got
        return strength_fn(Zt, At, self.enincmax, fit=tok)

    def gamma_params(self, Zt: int, At: int):
        """The `GammaParameters` of (Zt, At + 1) that `psf_fast.fstrength_np` evaluates on the
        numpy paths (`decay_fast`, `widths_native`, the primary `densprepare`), or None where only
        the torch `fstrength` may run: a TENSOR photon-strength override on this run.

        TALYS: gammapar.f90:1 (gammapar)
        Test: tests/hf/test_paramwire.py
        """
        from physics.hf.density.overrides import torch_path

        if self.gamma_overrides:
            if torch_path(self.gamma_overrides):
                return None
            if (Zt, At) == (self.Zt, self.At):
                return self.gamma_strength(Zt, At).gp
        if not self.fit:
            from physics.hf.compound.dens_reference import _gamma_parameters

            return _gamma_parameters(Zt, At)[0]
        return self.gamma_strength(Zt, At).gp

    # ---------------------------------------------------------------- structure, run-scoped

    def zn(self, zix: int, nix: int) -> tuple[int, int]:
        """(Z, A) of cascade index (zix, nix), counted down from the initial compound nucleus."""
        return self.Zc - zix, self.Ac - zix - nix

    @lru_cache(maxsize=512)  # noqa: B019  (per-Cascade cache; the object is per target)
    def _levels(self, zix: int, nix: int):
        from physics.hf.structure.levels import discrete_levels

        Z, A = self.zn(zix, nix)
        return discrete_levels(Z, A, self.options, self.m, self.params)

    def sep_mev(self, zix: int, nix: int) -> dict[int, float]:
        """`S(Zix, Nix, type)` from T2's masses."""
        return dict(self._sep(zix, nix))

    @lru_cache(maxsize=512)  # noqa: B019  (per-Cascade cache; the object is per target)
    def _sep(self, zix: int, nix: int) -> tuple:
        return tuple((t, float(self.m.s_mev[zix, nix, t])) for t in range(7))

    @lru_cache(maxsize=512)  # noqa: B019  (per-Cascade cache; the object is per target)
    def _discrete(self, zix: int, nix: int, ng: int):
        """Parity, spin and half-life of discrete levels 0..ng, and their gamma branches: the
        run-scoped part of `spec` (the levels do not move with the incident energy).
        Read-only: `spec` copies the arrays and every consumer only reads `branch`."""
        lv = self._levels(zix, nix)
        p_all = lv.all_parity.detach().numpy()
        j_all = lv.all_spin.detach().numpy()
        t_all = lv.all_half_life_s.detach().numpy()
        k = min(ng, len(p_all) - 1) + 1
        parlev = np.array([int(v) for v in p_all[:k]], dtype=np.int64)
        jdis = np.array([float(v) for v in j_all[:k]])
        tau = np.array([float(v) for v in t_all[:k]])
        branch: dict[int, list[tuple[int, float]]] = {}
        bt = lv.branch_to.detach().numpy()
        br = lv.branch_ratio.detach().numpy()
        for k in range(1, min(ng, bt.shape[0] - 1) + 1):
            rows = [(int(bt[k, i]), float(br[k, i])) for i in range(bt.shape[1])
                    if int(bt[k, i]) >= 0 and br[k, i] != 0.0]
            if rows:
                branch[k] = rows
        return parlev, jdis, tau, branch

    @property
    def ewfc_mev(self) -> float:
        """`ewfc`, the width-fluctuation off-set energy, with its default resolved.

        `default_options` leaves input_compoundmodel.f90:84's `ewfc = -1` sentinel in place, and
        `Einc <= -1.` is false at every incident energy -- so a caller that reads it raw runs the
        whole chain with W = 1, silently. TALYS resolves it once in `nuclides`: for a particle
        projectile `ewfc = S(parZ(k0), parN(k0), k0)`, the projectile's separation energy from the
        TARGET (11.197 MeV for n + Fe-56), so width fluctuations are on below the separation
        energy and off above it.

        TALYS: nuclides.f90:251
        Test: E2E
        """
        e = float(self.options.ewfc_mev)
        if self.k0 >= 1 and e == -1.0:
            e = self.sep_mev(PARZ[self.k0], PARN[self.k0])[self.k0]
        return e

    def _isotrans_ff(self, zix: int, nix: int) -> np.ndarray:
        """isotrans.f90's `ff(-1..6)` for one nucleus, on the contract's index `type + 1`.

        TALYS: isotrans.f90:1 (isotrans)
        Test: A-mult
        """
        Z, A = self.zn(zix, nix)
        N = A - Z
        ff = np.ones(8)
        if Z == N or abs(Z - N) == 1:
            v = 2.0 if Z == N else 1.5
            if self.k0 == 0:
                ff[1 + 1] = ff[2 + 1] = v if Z == N else 1.5
                ff[6 + 1] = 5.0 if Z == N else 1.5
            elif self.k0 in (1, 2):
                ff[0 + 1] = v
            elif self.k0 == 6:
                ff[0 + 1] = 5.0 if Z == N else 1.5
        return ff

    def fiso(self) -> np.ndarray:
        """`Fnorm(-1..6)` = 1 / `fiso` for the PRIMARY decay (comptarget.f90:281, :338).

        isotrans keeps two latches, not one: `fiso` for the primary decay and `fisom` for multiple
        emission (isotrans.f90:63-81). comptarget calls it once, on `(Zinit, Ninit)` -- the initial
        compound nucleus -- so the primary decay's `Fnorm` is a property of the compound nucleus
        and of nothing else. For n + Ca-40 the compound nucleus is Ca-41, `Z = N - 1`, so
        `fiso(0) = 1.5` and every primary gamma transmission is divided by it (densprepare.f90:310,
        :320). Passing 1 here instead leaves Ca-40's chained `Tgam` a factor 1.5 too large --
        worth 3e-1 on its (n,gamma) and 2e-1 on its nonelastic; no other spherical reference target
        is isospin-forbidden, which is why Ca-40 was the only one that showed it.

        `adjustTJ` is off by default, so `factor` in comptarget.f90:332-337 is 1.

        TALYS: isotrans.f90:1 (isotrans), comptarget.f90:338
        Test: E2E
        """
        return 1.0 / self._isotrans_ff(0, 0)

    def is_first_energy(self, e_inc_mev: float | None) -> bool:
        """Whether `e_inc_mev` is the FIRST incident energy of the run's declared grid.

        `fisom`'s sentinel is consumed once per run, so which energy is "first" is a property of
        the run's input, not of the order a caller happens to compute energies in. A Cascade built
        without `energies` is a one-energy run and every energy it is handed is that run's first.

        TALYS: read_energies.f90:1 (read_energies) -- the `Einc` axis multiple.f90 is driven over
        Test: A-mult / E2E
        """
        if self.energies is None or e_inc_mev is None:
            return True
        return round(float(e_inc_mev), 6) == round(self.energies[0], 6)

    def fisom(self, zix: int, nix: int, st: ChainState | None = None) -> np.ndarray:
        """`Fnorm(-1..6)` = 1 / fisom for MULTIPLE emission (multiple.f90:429-438).

        `fisom` behaves NOTHING like `fiso`, even though `isotrans` fills them with the same `ff`
        and guards both with the same `== -1` test. **multiple.f90:458-460 resets
        `fisom(0:6) = fisominit(type) = 1` immediately after `Fnorm` has been formed from it**,
        for every cascade nucleus. So the `-1` sentinel is live for exactly ONE nucleus in a whole
        run: the first one past multiple.f90:262-265 (the `skipCN` / `popeps` cuts) at the run's
        FIRST incident energy, which for an incident particle is the initial compound nucleus
        (0, 0) -- `skipCN(0, 0)` is 0 and its population is the whole reaction cross section.

        Two things follow, and the port used to get both wrong:

        * **It is that nucleus's WHOLE decay, not its first bin.** `Fnorm` is formed once per
          (Zcomp, Ncomp), above the `do nex = maxex, 1, -1` loop (multiple.f90:429-438 vs :488),
          so every mother bin of (0, 0) at the first energy divides by `ff`. EXCL3 replaced a
          run-scoped latch with a latch on the first CALL, which gave it to one bin.
        * **Which energy is first is declared, not observed.** A latch on the first call makes the
          answer depend on how the caller walks the grid: `ChainedFull(energies=...)` over a
          subset, `compound.decay_batch` building widths on demand, or a lab network shard each latch
          a different energy, and the same target then gets three different cross sections. The
          rule here is a pure function of (zix, nix) and `st.first_energy`, which
          `Cascade.is_first_energy` derives from the run's declared grid -- so any subset, any
          order and any batching give the number the full run gives.

        For n + Ca-40 this is worth a factor 1.5 on the gamma transmission of the initial compound
        nucleus at 1 keV only: Ca-41 is `Z = N - 1`, so `ff(0) = 1.5`. Latching it for the run
        (EXCL's reading) divides EVERY cascade nucleus's `Tgam` by 1.5 -- A-mult's `feedexcl`
        p95 0.405 = |ln(1.5)|.

        `fisom(-1)`, the fission factor, is NOT in the reset loop (`do type = 0, 6`), so it does
        latch for the run -- but `isotrans` never sets `ff(-1)` to anything but 1, so it is 1
        either way. It is carried here rather than dropped, because the asymmetry is the point.

        `adjustTJ` is off by default, so `factor` in multiple.f90:431-436 is 1.

        TALYS: isotrans.f90:1 (isotrans), multiple.f90:437, multiple.f90:458-460
        Test: A-mult / E2E
        """
        first_energy = True if st is None else bool(st.first_energy)
        if (zix, nix) == (0, 0) and first_energy:
            return 1.0 / self._isotrans_ff(zix, nix)
        return np.ones(8)  # fisominit for 0..6; ff(-1) is 1 whenever isotrans can set it

    # ---------------------------------------------------------------- grids, per energy

    @lru_cache(maxsize=64)  # noqa: B019  (per-Cascade cache; the object is per target)
    def incident(self, e_inc_mev: float):
        """The incident channel at one energy -- `lmaxinc`, `Tjlinc`, sigma_reac and the wave
        number. `densprepare` needs `lmaxinc` at every call, not only the primary one
        (densprepare.f90:394-398 is outside the `primary` branch), and `compnorm` needs the rest.

        **Which solver is not a detail.** `incidentecis.f90:203` takes the spherical branch only
        for `colltype == 'S'`; a `colltype R` or `V` target couples its collective levels, and
        T5's spherical `incident_channel` is then a different calculation, not an approximation of
        the same one. Ca-40 is the one `colltype V` target in the spherical reference set, and
        reading it as spherical costs `sigma_reac` 40% at 1 keV and 5% at 20 MeV -- which is most
        of why Ca-40 was the worst target of every gate in this family. T13's
        `ecis.incident.incident_coupled` is used for R and V; it builds T4's parameters itself
        (including RIPL 2408, T4RIPL) when `omp` is None.

        TALYS: incident.f90:1 (incident), incidentecis.f90:1 (incidentecis)
        Test: A-inc
        """
        from physics.hf.core.tensors import CaseBatch
        from physics.hf.omp.incident import incident_channel

        band = self._coupled_band()
        if band is not None:
            from physics.hf.ecis.incident import incident_coupled

            inc, res = incident_coupled(
                None, self.Zt, self.At, torch.tensor([e_inc_mev], dtype=DTYPE), band,
                particle=self.k0, options=self.options)
            self.__dict__.setdefault("_xscoupled", {})[float(e_inc_mev)] = (
                res.sigma_direct_mb[0].sum())
            return inc
        if not torch.is_grad_enabled() and self.energies and float(e_inc_mev) in self.energies:
            # SETB: the whole declared grid in one batch per njmax (omp/incident_axis.py)
            tab = self.__dict__.get("_setb_incident")
            if tab is None:
                from physics.hf.omp.incident_axis import incident_axis

                tab = incident_axis(self.Zt, self.At, self.energies, self.options, self.params)
                self.__dict__["_setb_incident"] = tab
            return tab[float(e_inc_mev)]
        cases = CaseBatch(Z=torch.tensor([self.Zt]), A=torch.tensor([self.At]),
                          e_inc_mev=torch.tensor([e_inc_mev], dtype=DTYPE), projectile="n")
        return incident_channel(cases, self.options, self.params)

    def xscoupled(self, e_inc_mev: float):
        """`xscoupled` [mb]: the direct cross section to the coupled levels, or None when the
        incident channel is spherical. compnorm's coupled-channels branch adds it back to the flux,
        because the coupled `Tjlinc` are already depleted by it.

        TALYS: incidentread.f90:369-391 (incidentread)
        Test: tests/hf/test_open4.py
        """
        band = self._coupled_band()
        if band is None:
            return None
        memo = self.__dict__.setdefault("_xscoupled", {})
        if float(e_inc_mev) not in memo:
            # `incident` records it when it solves; a table installed over `incident`
            # (`capture_fast_batch.install_tables`) does not, so solve it here then
            from physics.hf.ecis.incident import incident_coupled

            _, res = incident_coupled(
                None, self.Zt, self.At, torch.tensor([e_inc_mev], dtype=DTYPE), band,
                particle=self.k0, options=self.options)
            memo[float(e_inc_mev)] = res.sigma_direct_mb[0].sum()
        return memo[float(e_inc_mev)]

    @lru_cache(maxsize=1)  # noqa: B019  (per-Cascade cache; the object is per target)
    def _coupled_band(self):
        """T13's coupled band for this target, or None when the incident channel is spherical.

        Returns None rather than raising if `ecis` cannot serve this target, so a target outside
        T13's two stages still runs on the spherical branch instead of failing -- the substitution
        is then recorded by `coupled_incident_channel` being False rather than hidden.

        TALYS: incidentecis.f90:1 (incidentecis)
        Test: A-inc
        """
        try:
            from physics.hf.ecis.reference import coupled_band

            band = coupled_band(self.Zt, self.At)
        except Exception:
            return None
        if band is None or band.get("colltype") not in ("R", "V"):
            return None
        return band

    @property
    def coupled_incident_channel(self) -> bool:
        """Whether this target's incident channel is solved coupled-channels (T13) or spherical."""
        return self._coupled_band() is not None

    def new_energy(self, etotal_mev: float, lmaxinc: int = 0, *,
                   e_inc_mev: float | None = None) -> ChainState:
        """`reacinitial`: clear the grid latches and seed Exmax(0, 0) = Etotal.

        `e_inc_mev` is the INCIDENT energy this state belongs to (`etotal_mev` is the compound
        nucleus's excitation energy, which is not on the declared grid). It decides
        `ChainState.first_energy`, and with it whether `fisom`'s sentinel is live here.

        TALYS: reacinitial.f90:1 (reacinitial)
        Test: A-grid
        """
        e0 = np.zeros((NUMZ + 1, NUMN + 1), np.float32)
        em = np.zeros((NUMZ + 1, NUMN + 1), np.float32)
        e0[0, 0] = em[0, 0] = np.float32(etotal_mev)
        return ChainState(e0, em, lmaxinc=int(lmaxinc), e_inc_mev=e_inc_mev,
                          first_energy=self.is_first_energy(e_inc_mev))

    def propagate_exmax(self, st: ChainState, zcomp: int, ncomp: int) -> None:
        """exgrid.f90:110-138 for one mother: fill the Exmax of every daughter still at 0."""
        from physics.hf.core.grids import residual_exmax

        if zcomp > NUMZ or ncomp > NUMN:
            return
        sep = self._sep_table()
        st.exmax0, st.exmax = residual_exmax(
            zcomp, ncomp, st.exmax0, st.exmax, sep, {t: False for t in range(7)})

    @lru_cache(maxsize=1)  # noqa: B019  (per-Cascade cache; the object is per target)
    def _sep_table(self) -> np.ndarray:
        """`S(Zix, Nix, type)` as the (numZ+1, numN+1, 7) single-precision array exgrid reads."""
        sep = np.zeros((NUMZ + 1, NUMN + 1, 7), np.float32)
        nz, nn = self.m.s_mev.shape[0], self.m.s_mev.shape[1]
        sep[: min(NUMZ + 1, nz), : min(NUMN + 1, nn)] = np.asarray(
            self.m.s_mev[: NUMZ + 1, : NUMN + 1], np.float32)
        return sep

    def spec(self, st: ChainState, zix: int, nix: int) -> NucleusSpec:
        """`exgrid`'s excitation grid, maxJ and rhogrid of one nucleus, built once and latched.

        TALYS: exgrid.f90:1 (exgrid)
        Test: A-grid / A-ld
        """
        key = (zix, nix)
        if key in st.spec:
            return st.spec[key]
        # MACSPEED. One energy builds three ChainStates (`engine._BuiltInputs.shell`, the chain
        # itself and `feed_reference.pop_inputs_of`), and each rebuilt the binary residuals' grids
        # and rhogrid. A spec is a function of this Cascade and of Exmax(zix, nix) alone (plus
        # Exmax0(0, 0) for the compound nucleus), so it is shared across the states of one Etotal.
        # Nothing writes into a NucleusSpec. Bypassed under DIFFPARAM overrides.
        memo = None
        Z, A = self.zn(zix, nix)
        # PARAMWIRE: a spec reads the level density of (Z, A) and nothing else a parameter set
        # holds, so that nucleus's `aadjust` joins the memo key
        aadj = self.ld_token(Z, A)
        if not self.density_overrides and not self.diff_params and self.matching_xacc is None:
            e_key = float(st.exmax0[0, 0])
            memo = getattr(self, "_spec_memo", None)
            if memo is None or memo[0] != e_key:
                memo = self._spec_memo = (e_key, {})
            mkey = ((zix, nix, float(st.exmax[zix, nix])) if aadj is None
                    else (zix, nix, float(st.exmax[zix, nix]), aadj))
            hit = memo[1].get(mkey)
            if hit is not None:
                st.spec[key] = hit
                return hit
        from physics.hf.compound.dens_reference import _ld_of, rhogrid_of
        from physics.hf.core.grids import excitation_energies, max_spin_index
        from physics.hf.density.parameters import spincut

        lv = self._levels(zix, nix)
        ld, ntop, nlast_ld, ncum = _ld_of(Z, A, self.Zt, self.At, self.density_overrides,
                                          self.matching_xacc, aadj)
        nl = nlast_ld  # TALYS's Nlast(Zix, Nix, 0); NOT clamped to maxex -- see NucleusSpec
        exmax = float(st.exmax[zix, nix])
        ex, dex, maxex = excitation_energies(
            lv.all_e_mev.detach().numpy(), nl, exmax,
            int(self.options.nbins0), zix + nix, self.options.flagequi,
            float(st.exmax0[0, 0]) if (zix, nix) == (0, 0) else None)
        n = maxex + 1
        ng = min(nl, maxex)
        # maxJ: spincut at the bin centre with ald = A/8 (exgrid.f90:239-256), NOT ignatyuk.
        # `reacinitial` leaves maxJ at numJ and exgrid writes only NL+1..maxex, so a nucleus whose
        # grid stops below NL keeps numJ everywhere -- hence the unclamped `nl` in this test.
        rows = None
        if not self.density_overrides and not self.diff_params:
            from physics.hf.density.ld_ceng import spec_rows

            # CENGLD2: maxJ and rhogrid in one C call on the record's floats
            rows = spec_rows(ld, A, ex, dex, n, nl, _spincut_parts, NUMJ)
        maxj = rows[0] if rows is not None else np.full(n, NUMJ, np.int64)
        if rows is None and maxex > nl:
            if self.density_overrides or self.diff_params:
                exc = torch.as_tensor(ex[nl + 1 : n], dtype=DTYPE)
                sc = spincut(ld, torch.full_like(exc, A / 8.0), exc, 0, 0)
                maxj[nl + 1 :] = max_spin_index(sc).numpy()
            else:
                maxj[nl + 1 :] = _maxj_of(ld, A / 8.0, np.asarray(ex[nl + 1 : n], np.float64))
        parlev = np.zeros(n, np.int64)
        jdis = np.zeros(n)
        tau = np.zeros(n)
        p_d, j_d, t_d, branch = self._discrete(zix, nix, ng)
        parlev[: p_d.size] = p_d[:n]
        jdis[: j_d.size] = j_d[:n]
        tau[: t_d.size] = t_d[:n]
        sp = NucleusSpec(
            zix=zix, nix=nix, Z=Z, A=A, nlast=nl, nlast_grid=ng, ntop=ntop, ncum_nl=ncum,
            maxex=maxex, exmax_mev=exmax, ex_mev=ex[:n], dex_mev=dex[:n], maxj=maxj,
            parlev=parlev, jdis=jdis, tau_s=tau, branch=branch, sep_mev=self.sep_mev(zix, nix),
            rhogrid=rows[1] if rows is not None else rhogrid_of(
                Z, A, self.Zt, self.At, ex[:n], dex[:n], maxj, nl, self.density_overrides,
                self.diff_params, self.matching_xacc, aadj))
        st.spec[key] = sp
        if memo is not None:
            memo[1][mkey] = sp
        return sp

    # ---------------------------------------------------------------- the decay of one bin

    def nexmax(self, st: ChainState, sp: NucleusSpec, nex: int) -> dict[int, int]:
        """`nexmax(type)` of one mother bin (multiple.f90:517-538): the highest daughter bin whose
        BOTTOM is still under the top of the mother bin, minus one emission-grid point for a
        composite ejectile.

        TALYS: multiple.f90:1 (multiple)
        Test: A-mult
        """
        out = {0: nex - 1}
        exinc, dex = float(sp.ex_mev[nex]), float(sp.dex_mev[nex])
        for t in range(1, 7):
            d = self.spec(st, sp.zix + PARZ[t], sp.nix + PARN[t])
            exm = exinc + 0.5 * dex - sp.sep_mev[t]
            if t > 1:
                exm -= float(self.rg.egrid[self.rg.ebegin[t]])
            bottom = (np.asarray(d.ex_mev[: d.maxex + 1], dtype=np.float64)
                      - 0.5 * np.asarray(d.dex_mev[: d.maxex + 1], dtype=np.float64))
            below = np.flatnonzero(bottom < exm)
            out[t] = int(below[-1]) if below.size else -1
        return out

    def dens_inputs(self, st: ChainState, sp: NucleusSpec, nex: int) -> DensPrepareInputs:
        """`DensPrepareInputs` for mother bin `nex` of nucleus `sp`, with `primary = False`.

        TALYS: densprepare.f90:1 (densprepare)
        Test: A-cn1
        """
        from physics.hf.compound.dens_reference import DensTrans

        nxm = self.nexmax(st, sp, nex)
        eend = self._eend(st, sp)
        residuals, trans = {}, {}
        for t in range(7):
            d = self.spec(st, sp.zix + PARZ[t], sp.nix + PARN[t])
            residuals[t] = DensResidual(
                type=t, zix=d.zix, nix=d.nix, A=d.A, nlast=d.nlast, ntop=d.ntop,
                nexmax=max(nxm[t], 0), sep_mev=sp.sep_mev[t], ex_mev=d.ex_mev,
                dex_mev=d.dex_mev, maxj=d.maxj, parlev=d.parlev, jdis=d.jdis,
                rhogrid=d.rhogrid, ncum_nl=d.ncum_nl)
            if t >= 1:
                tjl, tl, lmax = self.trans[t]
                trans[t] = DensTrans(
                    egrid_mev=self.rg.egrid, ebegin=self.rg.ebegin[t],
                    eend=min(eend[t], self.rg.maxen), maxen=self.rg.maxen,
                    tjl=tjl, tl=tl, lmax=lmax)
        self.ndens += 1
        return DensPrepareInputs(
            exinc_mev=float(sp.ex_mev[nex]), dexinc_mev=float(sp.dex_mev[nex]),
            s_n_mev=sp.sep_mev[1], gammax=self.gammax, lmaxinc=st.lmaxinc, k0=self.k0,
            fnorm=self.fisom(sp.zix, sp.nix, st), residuals=residuals, trans=trans,
            gamma_strength=self.gamma_strength(sp.Z, sp.A - 1),
            primary=False, flagfullhf=self.flagfullhf, transeps=self.transeps)

    def _eend(self, st: ChainState, sp: NucleusSpec) -> dict[int, int]:
        """`eend(type)` for this mother's total energy; `inverse` filled Tjl only up to
        `eendmax`, and densprepare must not interpolate past it (the Pb-208 alpha trap)."""
        from physics.hf.compound.dens_reference import _eendmax

        em = _eendmax(self.Zt, self.At, self.enincmax)
        return {t: int(em[t]) for t in range(7)}

    def mpe_inputs(self, st: ChainState, nuclei: dict[tuple[int, int], NucleusPopulation],
                   zcomp: int, ncomp: int, nex: int, *, etotal_mev: float):
        """`MultiPreeqInputs` for one mother bin, built from the cascade's own grids.

        The s-wave transmission `Tjl(type, nen, 1, 0)` is located on the SAME emission grid the
        rest of the cascade decays through (`flagompall` false, so there is one set for the whole
        run), at `Eo = Exinc - Eex - S(Zcomp, Ncomp, type)`, with `eend(type)` from
        `energies.f90` -- not `densprepare`'s `eendmax` cut, which is a different limit.

        TALYS: multipreeq2.f90:1 (multipreeq2)
        Test: A-mpe / E2E
        """
        from physics.hf.core.grids import emission_end, locate_scalar
        from physics.hf.preeq.multi import MpeDaughter, MultiPreeqInputs
        from physics.hf.preeq.prepare import single_particle_densities
        from physics.hf.preeq.spin import preeq_spin_distribution

        sp = self.spec(st, zcomp, ncomp)
        nuc = nuclei[(zcomp, ncomp)]
        pop = nuc.xspopph2_mb.get(nex)
        if pop is None:
            return None
        nxm = self.nexmax(st, sp, nex)
        eend, _ = emission_end(self.rg.egrid, self.rg.maxen, etotal_mev,
                               {t: self.rg.s0[t] for t in range(7)}, self.rg.ebegin,
                               {t: False for t in range(7)})
        kph = float(self.params.at("kph"))
        exinc, dexinc = float(sp.ex_mev[nex]), float(sp.dex_mev[nex])
        # The two daughters share one bin axis, padded to the longer of the two grids, because
        # `term(type, nexout)` is one `(2, numex)` array in TALYS.
        nb = max(self.spec(st, sp.zix + PARZ[t], sp.nix + PARN[t]).maxex for t in (1, 2)) + 1
        daughters = []
        for t in (1, 2):
            d = self.spec(st, sp.zix + PARZ[t], sp.nix + PARN[t])
            n = nb
            _, gp, gn = single_particle_densities(d.Z, d.A - d.Z, kph)
            tjl = self.trans[t][0]
            tsw = np.zeros(n)
            for nexout in range(min(d.nlast_grid + 1, d.maxex + 1), min(nxm[t] + 1, d.maxex + 1)):
                eo = exinc - float(d.ex_mev[nexout]) - sp.sep_mev[t]
                nen = locate_scalar(self.rg.egrid, self.rg.ebegin[t],
                                    min(eend[t], self.rg.maxen), eo)
                tsw[nexout] = float(tjl[nen, 0, 2])  # Tjl(type, nen, updown = +1, l = 0)
            daughters.append(MpeDaughter(
                type=t, zix=d.zix, nix=d.nix, nlast=d.nlast_grid, nexmax=min(nxm[t], d.maxex),
                parskip=False, s_mev=sp.sep_mev[t],
                gp=torch.as_tensor(gp, dtype=DTYPE), gn=torch.as_tensor(gn, dtype=DTYPE),
                ex_mev=_pad(torch.as_tensor(d.ex_mev, dtype=DTYPE), nb),
                dex_mev=_pad(torch.as_tensor(d.dex_mev, dtype=DTYPE), nb),
                tswave=torch.as_tensor(tsw, dtype=DTYPE),
                maxj=tuple(int(d.maxj[k]) if k <= d.maxex else 0 for k in range(nb))))
        # `RnJ(0:numexc, 0:numJ)` is only filled to `maxJph` (preeqspindis.f90:47); above it
        # TALYS reads the zeros it was initialised with, and `maxJ` does exceed `maxJph`.
        rnj = preeq_spin_distribution(self.options, self.params, self.At)
        _, gpc, gnc = single_particle_densities(sp.Z, sp.A - sp.Z, kph)
        c0 = self.spec(st, 0, 0)
        _, gp0, gn0 = single_particle_densities(c0.Z, c0.A - c0.Z, kph)
        nj = nuc.xspop_mb.shape[1] - 1
        return MultiPreeqInputs(
            zcomp=zcomp, ncomp=ncomp, nex=nex,
            exinc_mev=torch.as_tensor(exinc, dtype=DTYPE),
            dexinc_mev=torch.as_tensor(dexinc, dtype=DTYPE),
            xspopex_mother_mb=nuc.xspopex_mb[nex].clone(), xspopph2_mb=pop,
            gp_comp=torch.as_tensor(gpc, dtype=DTYPE), gn_comp=torch.as_tensor(gnc, dtype=DTYPE),
            gp_cn0=torch.as_tensor(gp0, dtype=DTYPE), gn_cn0=torch.as_tensor(gn0, dtype=DTYPE),
            daughters=tuple(daughters), rnj=_pad(rnj["RnJ"][2], nj + 1),
            rnjsum=rnj["RnJsum"][2].clone(),
            maxpar=pop.shape[0] - 1, flaggshell=bool(self.options.flaggshell))

    def mpe(self, st: ChainState, nuclei: dict[tuple[int, int], NucleusPopulation],
            zcomp: int, ncomp: int, nex: int, *, etotal_mev: float):
        """`multiple_emission`'s `mpe(zcomp, ncomp, nex)` callback: multipreeq2 for one bin.

        TALYS: multipreeq2.f90:1 (multipreeq2)
        Test: A-mpe / E2E
        """
        from physics.hf.emission.multiple import MpeFeeding
        # SPEEDW: the compiled loop where it applies; the torch loop otherwise (preeq.mpe_fast)
        from physics.hf.preeq.mpe_fast import multiple_preequilibrium_fast

        inp = self.mpe_inputs(st, nuclei, zcomp, ncomp, nex, etotal_mev=etotal_mev)
        if inp is None:
            return None
        nj = nuclei[(zcomp, ncomp)].xspop_mb.shape[1] - 1
        r = multiple_preequilibrium_fast(inp, numj=nj)
        if float(r.summpe_mb) == 0.0 and not r.xspopph2_daughter_mb:
            return None
        return MpeFeeding(
            dmulti=float(r.dmulti), summpe_mb=float(r.summpe_mb),
            term_mb={t: r.term_mb[t - 1] for t in (1, 2)},
            xspop_add_mb={t: r.xspop_add_mb[t - 1] for t in (1, 2)},
            sumtype_mb={t: float(r.sumtype_mb[t - 1]) for t in (1, 2)},
            ph_add=r.xspopph2_daughter_mb, ph_mother_mb=r.xspopph2_mother_mb)

    def decay(self, st: ChainState, nuclei: dict[tuple[int, int], NucleusPopulation],
              zcomp: int, ncomp: int, nex: int, *, popeps_mb: float,
              flagfission: bool = False, nfisbar: int = 0, dmulti: float = 0.0,
              tfis: dict | None = None, fission=None) -> BinFeeding | None:
        """One mother bin's compound decay, as `multiple_emission`'s `decay` callback expects.

        `fission` (FISSB) is a `compound.fission_batch_decay.FissionLadder`: a fissioning nucleus
        it covers stays on `decay_fast`, and the per-bin path takes its `tfis` from it.

        TALYS: compound.f90:1 (compound), densprepare.f90:1 (densprepare)
        Test: A-mult
        """
        pop = nuclei[(zcomp, ncomp)]
        ladder = fission if (flagfission and fission is not None and fission.covered()) else None
        if (self.batched and (not flagfission or ladder is not None) and not self.flagfullhf
                and self.DECAY_CHUNK is None and self._numpy_decay_ok(pop)):
            # SPEEDD: the whole nucleus's widths in numpy, particle exits contracted for all
            # bins at once (compound.decay_fast); the same numbers to rounding
            popeps_a = popeps_mb / max(5 * pop.maxex, 1)  # multiple.f90:467, see below
            nw = st.__dict__.get("_nucleus_widths", {}).get((zcomp, ncomp))
            if nw is None or nex not in nw.row or nw.X_src is not pop.xspop_mb:
                nw = self._nucleus_widths(st, self.spec(st, zcomp, ncomp), nex, ladder)
                nw.X_src, nw.X = pop.xspop_mb, pop.xspop_mb.numpy()
            dpop, mcontrib, fisfeed, leftover = nw.feeding(nex, nw.X[nex], popeps_a,
                                                          dmulti=dmulti)
            return BinFeeding(dpop_mb=dpop, mcontrib_mb=mcontrib, fisfeed_mb=fisfeed,
                              leftover_mb=leftover)
        from physics.hf.compound.continuum import MultiInputs, compound_decay

        sp = self.spec(st, zcomp, ncomp)
        if self.batched and not flagfission and not self.flagfullhf:
            popeps_a = popeps_mb / max(5 * pop.maxex, 1)  # multiple.f90:467, see below
            # SPEED0: widths of every bin of this nucleus in one call, then this bin's feeding;
            # the same numbers as the per-bin path below (compound.decay_batch)
            nd = self._nucleus_decay(st, sp, nex)
            popeps_a = popeps_mb / max(5 * pop.maxex, 1)  # multiple.f90:467, see below
            dpop, mcontrib, fisfeed, leftover = nd.feeding(nex, pop.xspop_mb[nex], popeps_a,
                                                           dmulti=dmulti)
            return BinFeeding(dpop_mb=dpop, mcontrib_mb=mcontrib, fisfeed_mb=fisfeed,
                              leftover_mb=leftover)
        if tfis is None and flagfission and fission is not None:
            tfis = fission.triples(sp, nex)
        got = densprepare(self.dens_inputs(st, sp, nex))
        # `MultiInputs.popeps_mb` is TALYS's **popepsA**, not `popeps`: cndump.f90:137-138 writes
        # popepsA into that field, and `compound_decay` divides it again to get multiple.f90:560's
        # popepsB. Handing it the raw `popeps` makes the per-(J, parity) flux cut a factor
        # `5 * maxex` (350 here) too coarse, which silently drops the whole decay of any mother bin
        # whose largest (J, parity) cell falls under it -- the top populated bin of each residual.
        popeps_a = popeps_mb / max(5 * pop.maxex, 1)  # multiple.f90:467
        mi = MultiInputs(
            zcomp=zcomp, ncomp=ncomp, nex=nex, odd=sp.A % 2, e_inc_mev=0.0,
            ex_inc_mev=float(sp.ex_mev[nex]), dex_inc_mev=float(sp.dex_mev[nex]),
            exmax_mev=sp.exmax_mev, popeps_mb=popeps_a,
            dmulti=dmulti,  # multipreeq2.f90:374, via `Cascade.mpe` (multiple.f90:549)
            flagfullhf=self.flagfullhf, maxj_mother=int(sp.maxj[nex]), gammax=self.gammax,
            nlast_mother=sp.nlast_grid, nfisbar=nfisbar, numj=NUMJ, flagfission=flagfission,
            xspop_mother_mb=pop.xspop_mb[nex].detach().numpy(), residuals=got,
            tfis=tfis or {},
            mother_levels=[(int(sp.jdis[k]), int(sp.parlev[k]))
                           for k in range(sp.nlast_grid + 1)],
        )
        f = compound_decay(mi)
        return BinFeeding(dpop_mb=f.dpop_mb, mcontrib_mb=f.mcontrib_mb,
                          fisfeed_mb=float(f.fisfeed_mb),
                          leftover_mb=float(f.leftover_mb))

    def fast_widths(self, st: ChainState, nuclei: dict[tuple[int, int], NucleusPopulation],
                    zcomp: int, ncomp: int, nex: int, *, flagfission: bool = False,
                    fission=None):
        """NATIVEX: the `compound.decay_fast.NucleusWidths` holding mother bin `nex`, built as
        `decay` builds it, where `decay` would take that path; None otherwise.

        TALYS: compound.f90:1 (compound), densprepare.f90:1 (densprepare)
        Test: tests/hf/test_nativex.py
        """
        pop = nuclei[(zcomp, ncomp)]
        ladder = fission if (flagfission and fission is not None and fission.covered()) else None
        if not (self.batched and (not flagfission or ladder is not None) and not self.flagfullhf
                and self.DECAY_CHUNK is None and self._numpy_decay_ok(pop)):
            return None
        cache = st.__dict__.setdefault("_native_widths", {})
        nw = cache.get((zcomp, ncomp))
        if nw is not None and nex in nw.row:
            return nw
        from physics.hf.native import nativex

        if nativex.available() and os.environ.get("HF_NATIVEX_WIDTHS", "1") != "0":
            from physics.hf.compound.widths_native import NativeWidths

            sp = self.spec(st, zcomp, ncomp)
            smin = sp.sep_mev.get(1, 0.0)
            bins = [b for b in range(nex, 0, -1)
                    if not (b <= sp.nlast_grid and float(sp.ex_mev[b]) <= smin)]
            try:
                nw = NativeWidths(self, st, sp, bins)
            except NotImplementedError:
                nw = None
            if nw is not None:
                if ladder is not None:
                    fis = ladder.widths(sp, np.asarray(nw.bins, dtype=np.int64))
                    if fis.shape[1] < nw.nj:
                        fis = np.concatenate(
                            [fis, np.zeros((fis.shape[0], nw.nj - fis.shape[1], 2))], axis=1)
                    nw.fis = np.ascontiguousarray(fis[:, : nw.nj])
                    nw.dsum6 = nw.dsum6 + nw.fis
                    nw.zero6 = nw.zero6 & (nw.fis == 0.0)
                cache[(zcomp, ncomp)] = nw
                return nw
        nw = st.__dict__.get("_nucleus_widths", {}).get((zcomp, ncomp))
        if nw is None or nex not in nw.row or nw.X_src is not pop.xspop_mb:
            nw = self._nucleus_widths(st, self.spec(st, zcomp, ncomp), nex, ladder)
            nw.X_src, nw.X = pop.xspop_mb, pop.xspop_mb.numpy()
        return nw

    # Mother bins per `decay_batch.NucleusDecay` width build. None (the default) decays through
    # `compound.decay_fast` instead -- whole nucleus, numpy -- wherever nothing is on a graph;
    # a caller that sets a chunk size (capture_fast: 256) keeps decay_batch's path and its bits.
    DECAY_CHUNK: int | None = None

    def _numpy_decay_ok(self, pop: NucleusPopulation) -> bool:
        """Whether this bin can take `compound.decay_fast`: nothing on a graph -- no TENSOR
        parameter or photon-strength override on the run, and a population that is not on a graph.

        PARAMWIRE: a parameter set and float photon-strength overrides keep it (their strength
        functions return numpy, `gamma_params` hands `psf_fast` the adjusted parameters)."""
        from physics.hf.density.overrides import torch_path

        return (not self.diff_params and not torch_path(self.gamma_overrides)
                and not pop.xspop_mb.requires_grad)

    def _nucleus_widths(self, st: ChainState, sp: NucleusSpec, nex: int, ladder=None):
        """The `compound.decay_fast.NucleusWidths` holding mother bin `nex` of `sp`: built on the
        first decayed bin, for it and every bin below it that can decay at all (not a discrete
        level under S_n, which cascade.f90 empties instead). With a fission `ladder` (FISSB),
        `compound.fission_batch_decay.FissionNucleusWidths`."""
        from physics.hf.compound.decay_fast import NucleusWidths

        cache = st.__dict__.setdefault("_nucleus_widths", {})
        key = (sp.zix, sp.nix)
        cur = cache.get(key)
        if cur is None or nex not in cur.row:
            smin = sp.sep_mev.get(1, 0.0)
            ex = sp.ex_mev
            bins = [b for b in range(nex, 0, -1)
                    if not (b <= sp.nlast_grid and float(ex[b]) <= smin)]
            cur = (NucleusWidths(self, st, sp, bins) if ladder is None
                   else ladder.nucleus_widths(self, st, sp, bins))
            cur.X_src = cur.X = None
            cache[key] = cur
        return cur

    def _nucleus_decay(self, st: ChainState, sp: NucleusSpec, nex: int):
        """The `compound.decay_batch.NucleusDecay` holding mother bin `nex` of `sp`.

        `multiple_emission` decays a nucleus's bins from the top down and skips empty ones, so
        widths are built on demand for `nex` and the next DECAY_CHUNK - 1 bins below it that it
        can decay at all -- not for a discrete level under S_n, which cascade.f90 empties instead
        (multiple.f90's `nex <= NL .and. Exinc <= smin` branch).
        """
        from physics.hf.compound.decay_batch import NucleusDecay

        cache = st.__dict__.setdefault("_nucleus_decay", {})
        key = (sp.zix, sp.nix)
        cur = cache.get(key)
        if cur is None or nex not in cur.row:
            smin = sp.sep_mev.get(1, 0.0)
            bins = [b for b in range(nex, 0, -1)
                    if not (b <= sp.nlast_grid and float(sp.ex_mev[b]) <= smin)][
                        : self.DECAY_CHUNK or 24]
            cur = NucleusDecay(self, st, sp, bins)
            cache[key] = cur
        return cur

    # ---------------------------------------------------------------- the nucleus set

    def populations(self, st: ChainState, maxz: int, maxn: int,
                    seed: dict[int, tuple[np.ndarray, np.ndarray, float]],
                    ) -> dict[tuple[int, int], NucleusPopulation]:
        """`NucleusPopulation` for every nucleus of the cascade tree, with the binary residuals
        seeded from `binary` (T10) and everything deeper starting at zero.

        `seed` maps ejectile type -> (xspop (Nex, numJ+1, 2), xspopex (Nex,), xspopnuc).

        TALYS: multiple.f90:1 (multiple)
        Test: A-mult
        """
        out: dict[tuple[int, int], NucleusPopulation] = {}
        for zc in range(maxz + 1):
            for nc in range(maxn + 1):
                if zc > NUMZ or nc > NUMN:
                    continue
                if float(st.exmax[zc, nc]) <= 0.0 and (zc, nc) != (0, 0):
                    continue
                sp = self.spec(st, zc, nc)
                n = sp.maxex + 1
                out[(zc, nc)] = NucleusPopulation(
                    zcomp=zc, ncomp=nc, Z=sp.Z, A=sp.A, maxex=sp.maxex, nlast=sp.nlast_grid,
                    ex_mev=torch.as_tensor(sp.ex_mev, dtype=DTYPE),
                    dex_mev=torch.as_tensor(sp.dex_mev, dtype=DTYPE),
                    maxj=torch.as_tensor(sp.maxj), jdis=torch.as_tensor(sp.jdis, dtype=DTYPE),
                    parlev=torch.as_tensor(sp.parlev),
                    tau_s=torch.as_tensor(sp.tau_s, dtype=DTYPE),
                    sep_mev=sp.sep_mev, branch=sp.branch,
                    xspop_mb=torch.zeros((n, NUMJ + 1, 2), dtype=DTYPE),
                    xspopex_mb=torch.zeros(n, dtype=DTYPE))
        for t, (xspop, xspopex, xspopnuc) in seed.items():
            key = (PARZ[t], PARN[t])
            p = out.get(key)
            if p is None:
                continue
            k = min(p.xspop_mb.shape[0], xspop.shape[0])
            p.xspop_mb[:k] = torch.as_tensor(np.asarray(xspop)[:k], dtype=DTYPE)
            p.xspopex_mb[:k] = torch.as_tensor(np.asarray(xspopex)[:k], dtype=DTYPE)
            p.xspopnuc_mb = float(xspopnuc)
        return out
