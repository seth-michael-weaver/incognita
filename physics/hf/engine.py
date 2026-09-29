"""The reaction driver: the port of talysreaction.f90, wiring every subsystem for C cases.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T10 (physics/hf/CONTRACT.md §7). Acceptance test: E2E (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    talysreaction.f90:1 (talysreaction)

Order of operations follows talysreaction.f90 for a neutron-induced run: basicxs (inverse
channels) -> preeqinit -> compoundinit -> per incident energy: incident -> exgrid -> direct ->
preeq -> population/compnorm -> comptarget -> binary -> multiple -> channels -> totalxs ->
residual. Output, recoil, astro, URR and production branches are out of scope (§8).

**What runs today.** The last three stages -- binary, multiple+channels, totalxs+residual -- are
ported (T10) and `run` executes them.

The `densprepare.f90` seam T10 named is now closed: `compound.prepare.densprepare` builds
`Tjlnex`/`Tlnex` (T5's emission-grid transmission interpolated onto each residual level and bin),
`Tgam` (T7's photon strength times `Fnorm(0)`) and `rho0` (T6's level density integrated over
each bin's edges and centre), and `ChainedCompound` below runs `comptarget` on those instead of
on the dump's. What that buys is measured as a chained A-cn gate
(`compound.dens_reference.score_xspop`), not asserted.

Two seams are still open and are the reason `run` is not yet end-to-end, both bigger than
densprepare:

* `compnorm.f90` + `population.f90`: `CNfactor`, `xsflux`, `J2beg`/`J2end` and `Tjlinc` are the
  compound nucleus's own normalisation and initial (J, parity) population. Nothing ports them,
  so `ChainedCompound` injects them.
* `multiple.f90`'s feeding chain: `channels.f90`/`totalxs.f90`/`residual.f90` are ported, but the
  `feedexcl` array they consume comes from `compound.continuum` run over every bin of every
  residual -- which needs `densprepare` with `primary=False` per mother bin, and the
  excitation-energy re-gridding of `excitation.f90`. That is the next task, not this one.

`run` therefore still takes an `Injection`: a source for the families that are not chainable yet.
`DumpInjection` reads all of them from an instrumented TALYS run
(`emission/talys_instrument/chdump.f90`), which is what the A-mult gate uses; `ChainedCompound`
reads the same run but *builds* the compound-nucleus populations. Every injected family is named
in `Results.injected`, so no result can silently claim to be end-to-end.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

import numpy as np
import torch

from physics.hf.core.tensors import DTYPE
from physics.hf.emission.binary import BinaryInputs, BinaryState, binary
from physics.hf.emission.channels import ExclusiveState, exclusive_channels
from physics.hf.emission.dumps import ChannelInputs, load_binary_dump, load_channel_dump
from physics.hf.results import Results, level_key, residual_key

PARSYM = "gnpdtha"


class Injection(Protocol):
    """A source of the upstream families the port cannot chain yet (CONTRACT §5 injection rule)."""

    families: tuple[str, ...]

    def cases(self) -> list[tuple[BinaryInputs, ChannelInputs]]: ...


@dataclass(frozen=True)
class DumpInjection:
    """Every upstream family, from one instrumented TALYS run directory."""

    run_dir: Path
    families: tuple[str, ...] = (
        "optical", "level_density", "gamma", "preequilibrium", "direct", "compound",
        "multiple_emission", "fission",
    )

    def cases(self) -> list[tuple[BinaryInputs, ChannelInputs]]:
        b = load_binary_dump(Path(self.run_dir) / "bin_inputs.txt")
        c = load_channel_dump(Path(self.run_dir) / "ch_inputs.txt")
        by_e = {round(x.e_inc_mev, 6): x for x in c}
        return [(x, by_e[round(x.e_inc_mev, 6)]) for x in b if round(x.e_inc_mev, 6) in by_e]


@dataclass(frozen=True)
class ChainedCompound:
    """`DumpInjection`, except that the binary compound populations are BUILT, not injected.

    `densprepare` makes rho0/Tjlnex/Tlnex/Tgam from T5, T6 and T7; `comptarget` runs on them; the
    resulting `xspop`, `xspopex`, `xspopnuc` and `xsbinary` replace the dump's before `binary`
    sees them. `cn_dir` is a T9 instrumented run (`cn_inputs.txt`) and supplies only what nothing
    ports yet: CNfactor, xsflux, Tjlinc, J2beg/J2end and the fission transmission.

    TALYS: talysreaction.f90:1 (talysreaction)
    Test: E2E
    """

    run_dir: Path
    cn_dir: Path
    Z: int
    A: int
    families: tuple[str, ...] = (
        "compound_normalisation", "incident_channel", "preequilibrium", "direct",
        "multiple_emission", "fission",
    )

    def cases(self) -> list[tuple[BinaryInputs, ChannelInputs]]:
        from dataclasses import replace

        from physics.hf.compound.dens_reference import chained_compound_inputs
        from physics.hf.compound.prepare import load_cn_dump
        from physics.hf.compound.target import binary_cross_sections, compound_target_inputs

        pairs = DumpInjection(self.run_dir).cases()
        cn = {round(c.e_inc_mev, 6): c for c in load_cn_dump(Path(self.cn_dir) / "cn_inputs.txt")}
        enincmax = max(cn) if cn else 0.0
        out = []
        for binp, cinp in pairs:
            key = round(binp.e_inc_mev, 6)
            if key not in cn:
                out.append((binp, cinp))
                continue
            built = chained_compound_inputs(cn[key], self.Z, self.A, enincmax)
            pop = compound_target_inputs(built)
            xsb = binary_cross_sections(pop, [built])[0]
            p = pop.pop_mb[0]
            xspop, xspopex, xspopnuc = {}, {}, {}
            for t, g in binp.grids.items():
                n = g.ex_mev.shape[0]
                xspop[t] = p[t, :n].clone()
                xspopex[t] = xspop[t].sum((-2, -1))
                xspopnuc[t] = float(xspop[t].sum())
            xsbinary = binp.xsbinary_mb.clone() if binp.xsbinary_mb is not None else None
            if xsbinary is not None:
                for t in range(7):
                    xsbinary[t + 1] = xsb[t]
            out.append((replace(
                binp, xspop_mb=xspop, xspopex_mb=xspopex, xspopnuc_mb=xspopnuc,
                xsbinary_mb=xsbinary), cinp))
        return out


@dataclass(frozen=True)
class ChainedFull:
    """Everything the port has: `ChainedCompound` plus a ported `compnorm`, a ported
    `population.f90` and a COMPUTED `feedexcl`, so no exclusive channel is TALYS's bookkeeping.

    What each stage comes from:

    * incident channel, `lmaxinc`, `Tjlinc`, sigma_reac -- T5 (`omp.incident.incident_channel`)
    * `CNfactor`/`xsflux`/`J2beg`/`J2end` -- `compound.normalization` on T5, T8 and T12
      (`compound.norm_reference.chained_formation`)
    * `rho0`/`Tjlnex`/`Tlnex`/`Tgam` -- `compound.prepare.densprepare` on T5, T6 and T7
    * the binary compound populations -- `compound.target.comptarget`
    * `preeqpopex` -- `compound.population.population` on T8 and T12
    * `feedexcl`/`popexcl` -- `emission.feeding.Cascade` + `compound.continuum.compound_decay`
      driven by `emission.multiple.multiple_emission`

    What is still injected, in full, and why:

    * **T8's `xsreac` and T12's DWBA cross sections.** Those tasks inject them from the reference
      dumps themselves; they are inside the pre-equilibrium and direct families, not this seam.
    * **The discrete direct cross sections per level** (`xsdirdisc`), for the same reason.
    * **The structure and grid scalars** `Ltarget`, the target spin and parity, `popeps`, `xseps`
      and the reaction bookkeeping flags -- gates A-grid and A-struct cover them and no physics
      module produces them.
    * `multipreeq2.f90` -- `preeq.multi.multiple_preequilibrium`, driven per mother bin by
      `emission.feeding.Cascade.mpe` (gate A-mpe). It is live only at `Einc >= emulpre`
      (20 MeV, the last reference energy), where `population.f90` fills `xspopph2` at all.
    * **ECIS above `soswitch` and for `colltype V`** (Ca-40) -- ECIS2's seam, not this one.

    TALYS: talysreaction.f90:1 (talysreaction)
    Test: E2E
    """

    run_dir: Path | None = None
    Z: int = 0
    A: int = 0
    # A subset of the run's incident energies to compute (None = all). The run-scoped quantities
    # (`enincmax`, and with it the emission grid) still come from the whole run, so a subset
    # reproduces the same numbers the full run gives at those energies (hf_speed_bench).
    energies: tuple[float, ...] | None = None
    # Which of the three families is taken from the reference dumps instead of computed. The
    # default is NOTHING: every one of them is now built (NODUMP), and `inject=` exists so the
    # old arm stays testable and so the A/B that gates each family can be run.
    inject: tuple[str, ...] = ()
    # The run's declared incident energy grid. Required when `run_dir` is None (there is no dump
    # to read it off); `talys_reference.ENERGIES_MEV` is the reference set's.
    declared_energies: tuple[float, ...] | None = None
    # SPEEDW. With `energies` a subset, SPEEDP re-batches the two grid-batched set-ups -- the
    # exciton model and a coupled target's incident deck -- over that subset, which moves them in
    # the last bits (8 MeV alpha `preeqpopex` of Fe-56: 4.3e-16). `trim_batches=False` keeps both
    # on the whole declared grid, so a subset returns the serial full-grid run's bits at its
    # energies; `physics.hf.pool` builds those two once, before it forks the energy children.
    trim_batches: bool = True
    # SPEEDW. The run's `Cascade`, built by the caller on this run's (Z, A, enincmax, declared
    # grid), instead of a fresh one; `physics.hf.pool` hands every energy child the one its
    # parent warmed. None (the default) builds it here.
    cascade: object = field(default=None, compare=False, repr=False)
    # PARAMWIRE (ROUTE100 WP3). The run's fit parameters as TALYS keywords in absolute form,
    # `(("aadjust", Z, A, 1.1), ("ftable", Z, A + 1, 0.8), ...)` -- `density.overrides.FIT_KEYS`.
    # Plain floats: the numpy and NATIVEX paths stay on, and every level-density / photon-strength
    # cache is keyed by the entries it reads, so a run on a warmed `cascade` at a new point
    # recomputes only what the change reaches. Empty is TALYS's defaults, bit for bit.
    params: tuple = ()

    @property
    def families(self) -> tuple[str, ...]:
        """CONTRACT §5's report of what was injected. Empty is the point of this class."""
        return tuple(self.inject)

    def cases(self) -> list[tuple[BinaryInputs, ChannelInputs]]:
        from dataclasses import replace

        from physics.hf.compound.chain import compound_inputs
        from physics.hf.compound.norm_reference import addends
        from physics.hf.compound.population import population
        from physics.hf.compound.target import binary_cross_sections, compound_target_inputs
        from physics.hf.emission.feed_reference import etotal_of, pop_inputs_of
        from physics.hf.emission.feeding import Cascade
        from physics.hf.emission.multiple import multiple_emission
        from physics.hf.fission.chain import fission_chain
        from physics.hf.preeq.chain import lend_cascade, set_energy_subset, target_tag

        dumped = bool(self.inject)
        if dumped:
            if self.run_dir is None:
                raise ValueError("inject=%r needs a reference run_dir" % (self.inject,))
            pairs = DumpInjection(self.run_dir).cases()
            if not pairs:
                return []
            target = Path(self.run_dir).name.split("__")[-1]
            declared = tuple(b.e_inc_mev for b, _ in pairs)
        else:
            target = target_tag(self.Z, self.A)
            declared = self.declared_energies
            if declared is None and self.run_dir is not None:
                # convenience for the A/B: the same run the injected arm reads, energy grid only
                declared = tuple(b.e_inc_mev for b, _ in DumpInjection(self.run_dir).cases())
            if not declared:
                raise ValueError(
                    "ChainedFull with nothing injected needs `declared_energies`: the run's "
                    "incident energy grid is an input of the run, and there is no dump to read "
                    "it off. `talys_reference.ENERGIES_MEV` is the reference set's grid.")
            # TALYS holds `Einc` in real(sgl) (`capture_fast._f32` says the same), so the
            # declared grid is rounded the way TALYS stores it. Without this the dump-free arm
            # and the dumped one -- whose energies come from the dump, i.e. already float32 --
            # run on axes that differ by 5e-8 relative, and the SPEED0 golden sees it.
            declared = tuple(float(np.float32(e)) for e in declared)
            pairs = [(None, None)] * len(declared)
        enincmax = max(declared)
        want = None if self.energies is None else {round(e, 6) for e in self.energies}
        # OPEN4. binary.f90's `sfactor` lives for the whole energy loop (`BinaryState`), and the
        # multiple emission below is seeded from it, so a subset still has to walk every declared
        # energy before its last wanted one: those run as far as `binary` (`keep` False) and
        # return nothing. On the whole declared grid every energy is kept and nothing changes.
        run_axis = [b.e_inc_mev for b, _ in pairs] if dumped else list(declared)
        keep = [want is None or round(e, 6) in want for e in run_axis]
        n_run = max((i + 1 for i, k in enumerate(keep) if k), default=0)
        run_axis, keep = run_axis[:n_run], keep[:n_run]
        pairs = pairs[:n_run] if dumped else [(None, None)] * n_run
        # `energies` is the run's DECLARED grid (every energy of the run), not the subset this
        # call computes: `fisom`'s one-nucleus sentinel belongs to the run's first energy, so a
        # subset has to know it is a subset (`Cascade.is_first_energy`).
        cas = self.cascade
        if cas is None:
            cas = Cascade(self.Z, self.A, enincmax, energies=declared)
        elif (int(cas.Zt), int(cas.At), float(cas.enincmax), tuple(cas.energies)) != (
                self.Z, self.A, float(enincmax), tuple(declared)):
            raise ValueError("ChainedFull(cascade=...) was built for another run")
        if self.params and dumped:
            raise ValueError("ChainedFull(params=...) needs the dump-free chain (inject=())")
        cas.set_fit_params(self.params)
        trim = self.trim_batches
        # TWOPH: T11's fission transmission, wired in. Before this `compound_inputs` was passed
        # `tfis=None` and `Cascade.decay` `flagfission=False`, so a chained actinide ran and
        # returned (n,f) = 0 (`docs/results/hf-nodump.md`). `fission_chain` is None unless the
        # TARGET has `flagfission` (A > 215, input_fissionmodel.f90:78-80); every residual then
        # gets barriers of its own or `nfisbar = 0`.
        # MERGE4: built off `cas.options`, so a caller-supplied Cascade (SPEEDW's pool) gives the
        # same chain as a locally built one.
        fis = None if dumped else fission_chain(self.Z, self.A, cas.options,
                                                fit=cas.fit + cas.fission_fit)
        if not dumped:
            # SPEEDP. Two scheduling facts the chained families cannot work out for themselves:
            # this run computes `run_axis` out of the declared grid (so the exciton model does not
            # need the rows in between, and the DWBA does not need the energies in between), and
            # `cas` is the run's Cascade (so `preeq.chain` need not solve the incident channel a
            # second time on one of its own). Neither changes a number -- `check` against
            # `features/hf_speed_golden_speedp/` is bit-identical -- and on the full declared grid
            # the first is a no-op.
            set_energy_subset(self.Z, self.A, declared, run_axis if trim else None)
            lend_cascade(cas)
        try:
            add = addends(target, self.Z, self.A, run_axis, None if dumped else declared,
                          fit=cas.fit)
            built = None if dumped else _BuiltInputs(cas, target, declared, add)
            out = []
            bstate = BinaryState()
            for nin, (binp, cinp) in enumerate(pairs, start=1):
                if not dumped:
                    binp, cinp = built.shell(nin, run_axis[nin - 1])
                etot = etotal_of(self.Z, self.A, enincmax, binp.e_inc_mev, binp.k0)
                inc = cas.incident(binp.e_inc_mev)
                st = cas.new_energy(etot, lmaxinc=int(inc.lmax[0]), e_inc_mev=binp.e_inc_mev)
                cas.propagate_exmax(st, 0, 0)
                fkw = {}
                if fis is not None and cinp.flagfission:
                    cn = cas.spec(st, 0, 0)
                    fkw = fis.compound_target(int(cn.Z), int(cn.A), etot,
                                              fnorm=float(cas.fiso()[0]))
                ci = compound_inputs(cas, st, binp, cinp, etot,
                                     add[round(binp.e_inc_mev, 6)], **fkw)
                pop = compound_target_inputs(ci)
                xsb = binary_cross_sections(pop, [ci])[0]
                p = pop.pop_mb[0]
                xspop, xspopex, xspopnuc = {}, {}, {}
                for t, g in binp.grids.items():
                    n = g.ex_mev.shape[0]
                    xspop[t] = p[t, :n].clone()
                    xspopex[t] = xspop[t].sum((-2, -1))
                    xspopnuc[t] = float(xspop[t].sum())
                xsbinary = binp.xsbinary_mb.clone() if binp.xsbinary_mb is not None else None
                if xsbinary is not None:
                    for t in range(7):
                        xsbinary[t + 1] = xsb[t]
                    # TWOPH: index 0 is TALYS's `xsbinary(-1)`, the FIRST-CHANCE fission of the
                    # primary compound nucleus (comptarget.f90). `binary_cross_sections` returns
                    # types 0..6 only and the chained arm's shell starts at zeros, so before this
                    # the top bin of the compound nucleus contributed nothing to (n,f) --
                    # `multiple._binary_feed` seeds `fisfeedex[top]` from exactly this number.
                    if fis is not None and cinp.flagfission:
                        xsbinary[0] = pop.xs_fission_mb[0]
                # an energy walked only for `sfactor` needs no pre-equilibrium population:
                # binary.f90 overwrites `sfactor` from the compound population alone
                prq = (population(pop_inputs_of(cas, binp, target, etot, add,
                                                None if dumped else declared))
                       if keep[nin - 1] else None)
                pex = {}
                for t, g in binp.grids.items():
                    n = g.ex_mev.shape[0]
                    col = prq.preeqpopex_mb.get(t) if prq is not None else None
                    v = torch.zeros(n, dtype=DTYPE)
                    if col is not None:
                        k = min(n, len(col))
                        v[:k] = torch.as_tensor(col[:k], dtype=DTYPE)
                    pex[t] = v
                extra = {}
                if not dumped:
                    # comptarget.f90:398 -- the continuum part of the binary compound population,
                    # which binary.f90:311 keeps only above `xseps`. The dumped arm reads it from
                    # the TYPE record; here it is the population above the last discrete level.
                    extra["xscompcont_mb"] = {
                        t: float(xspop[t][binp.grids[t].nlast + 1:].sum()) for t in xspop}
                b2 = replace(binp, xspop_mb=xspop, xspopex_mb=xspopex, xspopnuc_mb=xspopnuc,
                             xsbinary_mb=xsbinary, preeqpopex_mb=pex, **extra,
                             xsreacinc_mb=float(inc.sigma_reac_mb[0]),
                             xsdirdiscsum_mb=add[round(binp.e_inc_mev, 6)]["xsdirdiscsum_mb"],
                             xspreeqsum_mb=add[round(binp.e_inc_mev, 6)]["xspreeqsum_mb"],
                             xsgrsum_mb=add[round(binp.e_inc_mev, 6)]["xsgrsum_mb"])
                b = binary(b2, bstate)
                if not keep[nin - 1]:
                    continue
                seed = {t: (b.xspop_mb[t].detach().numpy(), b.xspopex_mb[t].detach().numpy(),
                            float(b.xspop_mb[t].sum())) for t in b.xspop_mb}
                nuclei = cas.populations(st, cinp.maxz, cinp.maxn, seed)
                for zc in range(cinp.maxz + 1):
                    for nc in range(cinp.maxn + 1):
                        if (zc, nc) in nuclei:
                            cas.propagate_exmax(st, zc, nc)
                nuclei = cas.populations(st, cinp.maxz, cinp.maxn, seed)
                _seed_mulpre(nuclei, prq)
                xsb_by_type = ({t - 1: float(v) for t, v in enumerate(xsbinary)}
                               if xsbinary is not None else {})
                decay = _bin_decay(cas, st, nuclei, binp.popeps_mb,
                                   fis if cinp.flagfission else None)
                mpe_cb = None
                if any(n.mulpre for n in nuclei.values()):
                    def mpe_cb(zc, nc, nex, cas=cas, st=st, nuclei=nuclei, etot=etot):
                        return cas.mpe(st, nuclei, zc, nc, nex, etotal_mev=etot)

                    # NATIVEX: what `emission.multiple_native` needs to run multipreeq2 in C
                    mpe_cb.context = (cas, st, nuclei, etot)
                mres = multiple_emission(
                    nuclei, decay,
                    popeps_mb=binp.popeps_mb, maxz=cinp.maxz, maxn=cinp.maxn, k0=binp.k0,
                    xsreacinc_mb=float(inc.sigma_reac_mb[0]), xsbinary_mb=xsb_by_type,
                    feedbinary_mb=b.feedbinary_mb, flagfission=cinp.flagfission,
                    mpe=mpe_cb)
                if dumped:
                    out.append((b2, _with_computed_feeding(cinp, mres)))
                else:
                    ch_in = built.channels(cinp, st, mres, b, xsbinary)
                    if os.environ.get("INCOGNITA_RP_ISOMERS") == "1":
                        # multiple.f90 leaves an isomer's flux in its xspopex (the cascade skips
                        # tau != 0 levels); residual.f90's xsbranch reads it from there
                        for key, n in ch_in.nuclei.items():
                            pn = nuclei.get(key)
                            if pn is not None and n.nlast:
                                v = pn.xspopex_mb.tolist()
                                n.xspopex_mb = {k: float(v[k]) for k in range(min(len(v), n.nlast + 1))}
                    out.append((b2, ch_in))
            return out
        finally:
            if not dumped:
                # The subset is this RUN's, not this target's: a later caller that asks
                # `pop_reference._preeq` for the whole declared grid must not be served a
                # narrowed answer out of the cache (`set_energy_subset` drops it).
                set_energy_subset(self.Z, self.A, declared, None)


class _BuiltInputs:
    """`BinaryInputs` and `ChannelInputs` from the ported modules, with no dump behind them.

    This is the last mile of NODUMP. `ChainedFull` already computed every *physics* array it
    hands to `binary` and `channels`; what it still took from `bin_inputs.txt` / `ch_inputs.txt`
    was the shell around them -- the residual grids, the per-level direct cross sections, the
    T8/T12 per-type totals and the structure scalars. All four are built here:

    * **grids** -- `emission.feeding.Cascade.spec` (exgrid.f90, gate A-grid) plus
      `binary.bin_spin_cutoff` for the `ald`/`spincut` columns the pre-equilibrium spin spread
      needs (binary.f90:229-230).
    * **`xsdirdisc`, `xsdirdisctot`, `xsgrtot`** -- `direct.chain` (T12 + T13's ECIS).
      `giant.f90:113-174` fills type `k0` only, so every other type is zero and not merely
      unread.
    * **`xspreeqtot`** -- T8's exciton model on T5's inverse channels (`preeq.chain`).
    * **the scalars** -- `structure.scalars.structure_scalars`.

    `ChannelInputs.nuclei` is built AFTER the cascade has run, from `ChainState.spec`: that is
    exactly the set of nuclei TALYS called `structure` for (`exgrid` reaches every daughter of
    every mother it processes), so a nucleus the cascade never reached keeps the zeros
    `strucinitial` left it with, as it does in the dump.

    TALYS: talysreaction.f90:1 (talysreaction), exgrid.f90:1 (exgrid), multiple.f90:1 (multiple)
    Test: E2E
    """

    def __init__(self, cas, target: str, declared: tuple[float, ...], add: dict):
        from physics.hf.preeq.chain import chained_direct
        from physics.hf.structure.scalars import structure_scalars

        self.cas = cas
        self.target = target
        self.declared = declared
        self.add = add
        self.sc = structure_scalars(cas.Zt, cas.At, declared, cas.k0)
        self.direct = chained_direct(cas.Zt, cas.At, declared)
        self._preeqtot = None

    def preeq_at(self, e_inc_mev: float):
        """T8's per-type totals and per-level discrete cross sections at one energy.

        `(xspreeqtot(type), xspreeqdisctot(type), xspreeqdisc(type, i))`, all zero below `epreeq`
        where `preeq` never runs.
        """
        from physics.hf.compound.pop_reference import preeq_fit
        from physics.hf.emission.feed_reference import _preeq_of

        if self._preeqtot is None:
            pfit = preeq_fit(self.cas.fit, self.cas.Zt, self.cas.At)
            pe, pres, _o = (_preeq_of(self.target, self.declared, pfit) if pfit
                            else _preeq_of(self.target, self.declared))
            self._preeqtot = (pe, pres)
        pe, pres = self._preeqtot
        i = pe.get(round(float(e_inc_mev), 6))
        if i is None:
            return {t: 0.0 for t in range(7)}, {t: 0.0 for t in range(7)}, None
        return ({t: float(pres["xspreeqtot"][i][t]) for t in range(7)},
                {t: float(pres["xspreeqdisctot"][i][t]) for t in range(7)},
                pres["xspreeqdisc"][i])

    def shell(self, nin: int, e_inc_mev: float):
        """The `(BinaryInputs, ChannelInputs)` pair for one energy, before the chain runs on it."""
        from physics.hf.emission.binary import ResidualGrid, bin_spin_cutoff
        from physics.hf.emission.feed_reference import etotal_of
        from physics.hf.emission.feeding import PARN, PARZ

        sc = self.sc
        cas = self.cas
        e = float(e_inc_mev)
        etot = etotal_of(cas.Zt, cas.At, cas.enincmax, e, cas.k0)
        st = cas.new_energy(etot, e_inc_mev=e)
        cas.propagate_exmax(st, 0, 0)
        d, _flaggiant = self.direct[round(e, 6)]
        petot, pedisctot, pedisc = self.preeq_at(e)
        # `xsdirdisc` at binary.f90's entry is NOT only the DWBA: preeqtotal.f90:186-192 adds
        # `xspreeqdisc(type, i)` to it for EVERY ejectile, and `xsdirdisctot` with it. That is
        # why the dump carries a non-zero `xsdirdisctot` for the proton, deuteron and alpha
        # channels of a neutron-induced run, where `direct.f90` writes nothing at all -- and why
        # leaving it out costs Fe-56's (n,alpha) 10% above 8 MeV (3.4 mb of 35).
        dd_all = d.xsdirdisc_mb.detach().to(DTYPE)
        grids, xsdirdisc = {}, {}
        for t in range(7):
            if sc.parskip[t]:
                continue
            sp = cas.spec(st, PARZ[t], PARN[t])
            n = sp.maxex + 1
            ex = torch.as_tensor(sp.ex_mev[:n], dtype=DTYPE)
            ald = torch.zeros(n, dtype=DTYPE)
            spc = torch.ones(n, dtype=DTYPE)
            ng = min(sp.nlast, sp.maxex)
            if sp.maxex > ng:
                # PARAMWIRE: the run's level density of this residual (it was the defaults' even
                # under an override), for the pre-equilibrium spin spread's ald / spincut
                ld, _ntop, _nl, _nc = cas.ld_of(sp.Z, sp.A)
                a, sg = bin_spin_cutoff(ld, ex[ng + 1:])
                ald[ng + 1:], spc[ng + 1:] = a, sg
            grids[t] = ResidualGrid(
                type=t, zix=sp.zix, nix=sp.nix, maxex=sp.maxex, nlast=sp.nlast,
                ex_mev=ex, dex_mev=torch.as_tensor(sp.dex_mev[:n], dtype=DTYPE),
                maxj=torch.as_tensor(sp.maxj[:n]),
                parlev=torch.as_tensor(sp.parlev[:n]),
                jdis=torch.as_tensor(sp.jdis[:n], dtype=DTYPE), ald=ald, spincut=spc)
            v = torch.zeros(n, dtype=DTYPE)
            if t == cas.k0:
                k = min(n, dd_all.shape[0])
                v[:k] = dd_all[:k]
            if pedisc is not None:
                row = torch.as_tensor(pedisc[t], dtype=DTYPE)
                k = min(n, row.shape[0])
                v[:k] = v[:k] + row[:k]
            xsdirdisc[t] = v
        inc = cas.incident(e)
        binp = BinaryInputs(
            e_inc_mev=e, k0=cas.k0, ltarget=sc.ltarget, targetspin2=sc.targetspin2,
            target_parity=sc.target_parity, pespinmodel=sc.pespinmodel,
            # `maxJph` is `preeqinit`'s, and `preeqinit` runs only where `preeq` does: the dump
            # carries 0 at every energy below `epreeq` and 30 above it. `binary` reads it only
            # inside its own `flagpreeq` branch, so the two agree either way -- it is carried
            # this way because the dump is the record and a silent 30 below the onset is a lie.
            maxjph=(sc.maxjph if sc.flags(e)["flagpreeq"] else 0),
            numj=sc.numj, popeps_mb=sc.popeps_mb, xseps_mb=sc.xseps_mb,
            xsreacinc_mb=float(inc.sigma_reac_mb[0]),
            xselasinc_mb=float(inc.sigma_shape_el_mb[0]),
            xsdirdiscsum_mb=self.add[round(e, 6)]["xsdirdiscsum_mb"],
            xspreeqsum_mb=self.add[round(e, 6)]["xspreeqsum_mb"],
            xsgrsum_mb=self.add[round(e, 6)]["xsgrsum_mb"],
            # `racape` needs `racap y`, which is off by default (input_basicreaction.f90); the
            # reference dumps carry 0 at every energy of every target.
            xsracape_mb=0.0,
            flagpreeq=bool(sc.flags(e)["flagpreeq"]), grids=grids, xsdirdisc_mb=xsdirdisc,
            xsdirdisctot_mb={t: (float(d.xsdirdisctot_mb) if t == cas.k0 else 0.0)
                                + pedisctot[t] for t in range(7)},
            xspreeqtot_mb=petot,
            xsgrtot_mb={cas.k0: float(d.xsgrtot_mb)},
            xsbinary_mb=torch.zeros(8, dtype=DTYPE))
        cinp = ChannelInputs(
            nin=nin, e_inc_mev=e, k0=cas.k0, ltarget=sc.ltarget, maxz=sc.maxz, maxn=sc.maxn,
            zinit=sc.zinit, ninit=sc.ninit, maxchannel=sc.maxchannel, ninclow=sc.ninclow,
            xseps_mb=sc.xseps_mb, targete_mev=sc.targete_mev, specmass=sc.specmass,
            xsreacinc_mb=float(inc.sigma_reac_mb[0]), xsnonel_mb=0.0,
            flagfission=sc.flagfission, flaginitpop=sc.flaginitpop,
            flagchannels=sc.flagchannels, parinclude=list(sc.parinclude),
            parskip=list(sc.parskip), xsbinary_mb=[0.0] * 8)
        return binp, cinp

    def channels(self, cinp: ChannelInputs, st, mres, b, xsbinary):
        """`cinp` with every nucleus record built from the cascade's own state.

        `Qres(Zix, Nix, 0) = S(0, 0, k0) + targetE + (Exmax0 - Etotal)` (exgrid.f90:167-170),
        which is `S(0, 0, k0)` minus the separation energies along the path to that nucleus and
        is therefore the same at every incident energy -- a nucleus the cascade has not reached
        keeps `Exmax0 = 0`, and TALYS keeps `Qres = 0` there too.

        TALYS: exgrid.f90:1 (exgrid), multiple.f90:1 (multiple)
        Test: E2E
        """
        from copy import copy

        from physics.hf.emission.dumps import NucleusState
        from physics.hf.emission.feeding import PARN, PARZ
        from physics.hf.structure.levels import NUMLEV2

        sc = self.sc
        cas = self.cas
        out = copy(cinp)
        out.xsnonel_mb = float(b.xsnonel_mb)
        out.xsbinary_mb = [float(x) for x in xsbinary]
        out.nuclei = {}
        etot = float(st.exmax0[0, 0])
        s_k0 = float(cas.m.s_mev[0, 0, cas.k0])
        from physics.hf.emission import emit_nx2

        if emit_nx2.glue_enabled():
            # NATIVEX2 (glue): the same records, the level columns read with one `tolist` each
            # and the per-type fields from lists made once
            live_t = [t for t in range(7) if not sc.parskip[t]]
            spec = st.spec
            Zc, Ac = cas.Zc, cas.Ac  # `Cascade.zn`
            unreached = self.__dict__.setdefault("_unreached_nuclei", {})
            get = (mres.xspopnuc_mb.get, mres.xsgamdistot_mb.get, mres.popexcl_mb.get,
                   mres.feedexcl_mb.get, mres.fisfeedex_mb.get, mres.xsfeed_mb.get)
            for zc in range(cinp.maxz + 1):
                for nc in range(cinp.maxn + 1):
                    key = (zc, nc)
                    sp = spec.get(key)
                    if sp is None:
                        # a nucleus this energy's cascade never reached: the same all-zero record
                        # at every energy of the target, built once (every reader only reads it)
                        rec = unreached.get(key)
                        if rec is None:
                            Z, A = Zc - zc, Ac - zc - nc
                            rec = unreached[key] = NucleusState(
                                zcomp=zc, ncomp=nc, Z=Z, N=A - Z, A=A, maxex=0, nlast=0,
                                xspopnuc_mb=0.0, qres_mev=0.0, xsgamdistot_mb=0.0, skipcn=0.0)
                        out.nuclei[key] = rec
                        continue
                    exmax0 = float(st.exmax0[zc, nc])
                    n = NucleusState(
                        zcomp=zc, ncomp=nc, Z=sp.Z, N=sp.A - sp.Z, A=sp.A, maxex=sp.maxex,
                        nlast=sp.nlast, xspopnuc_mb=get[0](key, 0.0),
                        qres_mev=((s_k0 + sc.targete_mev + (exmax0 - etot)) if exmax0 != 0.0
                                  else 0.0),
                        xsgamdistot_mb=get[1](key, 0.0),
                        skipcn=0.0)
                    k = min(sp.nlast, NUMLEV2, len(sp.ex_mev) - 1) + 1
                    if k > 0:
                        lv = range(k)
                        n.edis_mev = dict(zip(lv, sp.ex_mev[:k].tolist()))  # noqa: B905
                        n.tau_s = dict(zip(lv, sp.tau_s[:k].tolist()))  # noqa: B905
                    sep = sp.sep_mev
                    for t in live_t:
                        n.sep_mev[t] = sep[t]
                        n.index[t] = (zc + PARZ[t], nc + PARN[t])
                    n.popexcl_mb = get[2](key, {})
                    n.feedexcl_mb = get[3](key, {})
                    n.fisfeedex_mb = get[4](key, {})
                    n.xsfeed_mb = get[5](key, {})
                    out.nuclei[key] = n
            return out
        for zc in range(cinp.maxz + 1):
            for nc in range(cinp.maxn + 1):
                Z, A = cas.zn(zc, nc)
                if (zc, nc) not in st.spec:
                    out.nuclei[(zc, nc)] = NucleusState(
                        zcomp=zc, ncomp=nc, Z=Z, N=A - Z, A=A, maxex=0, nlast=0,
                        xspopnuc_mb=0.0, qres_mev=0.0, xsgamdistot_mb=0.0, skipcn=0.0)
                    continue
                sp = st.spec[(zc, nc)]
                exmax0 = float(st.exmax0[zc, nc])
                n = NucleusState(
                    zcomp=zc, ncomp=nc, Z=sp.Z, N=sp.A - sp.Z, A=sp.A, maxex=sp.maxex,
                    nlast=sp.nlast, xspopnuc_mb=mres.xspopnuc_mb.get((zc, nc), 0.0),
                    qres_mev=(s_k0 + sc.targete_mev + (exmax0 - etot)) if exmax0 != 0.0 else 0.0,
                    xsgamdistot_mb=mres.xsgamdistot_mb.get((zc, nc), 0.0),
                    skipcn=0.0)
                for nex in range(min(sp.nlast, NUMLEV2, len(sp.ex_mev) - 1) + 1):
                    n.edis_mev[nex] = float(sp.ex_mev[nex])
                    n.tau_s[nex] = float(sp.tau_s[nex])
                for t in range(7):
                    if sc.parskip[t]:
                        continue
                    n.sep_mev[t] = sp.sep_mev[t]
                    n.index[t] = (zc + PARZ[t], nc + PARN[t])
                n.popexcl_mb = mres.popexcl_mb.get((zc, nc), {})
                n.feedexcl_mb = mres.feedexcl_mb.get((zc, nc), {})
                n.fisfeedex_mb = mres.fisfeedex_mb.get((zc, nc), {})
                n.xsfeed_mb = mres.xsfeed_mb.get((zc, nc), {})
                out.nuclei[(zc, nc)] = n
        return out


def _bin_decay(cas, st, nuclei, popeps_mb: float, fis=None):
    """`multiple_emission`'s `decay(zcomp, ncomp, nex)` callback, bound to one incident energy.

    `fis` is a `fission.chain.FissionChain` when the target fissions. Each mother bin then gets
    the `(tfisdown, tfis, tfisup)` triple `compound.f90:120-147` integrates over it, built at the
    nucleus's own `densprepare` grid -- `Ex(maxex)`, not `Exinc` (densprepare.f90:408-412).
    A nucleus with no barrier (`A <= 150`, or `fissionpar` finds none) decays with
    `flagfission=False` exactly as before, which keeps every non-fissile residual -- and every
    non-actinide target -- on `decay_fast`'s batched path.
    """

    def fission_kw(zc: int, nc: int) -> dict:
        if fis is None:
            return {}
        sp = cas.spec(st, zc, nc)
        nb = fis.nfisbar(int(sp.Z), int(sp.A))
        if not nb:
            return {}
        from physics.hf.compound.fission_batch_decay import FissionLadder

        return {"flagfission": True, "nfisbar": nb,
                "fission": FissionLadder(fis, int(sp.Z), int(sp.A), float(cas.fiso()[0]))}

    def widths(zc: int, nc: int, nex: int):
        # NATIVEX: the `compound.decay_fast.NucleusWidths` `decay` would use for this bin, or None
        kw = fission_kw(zc, nc)
        return cas.fast_widths(st, nuclei, zc, nc, nex, flagfission=kw.get("flagfission", False),
                               fission=kw.get("fission"))

    def decay(zc: int, nc: int, nex: int, *, dmulti: float = 0.0):
        # FISSB: the triple is built by `Cascade.decay` only where the per-bin path runs;
        # `decay_fast` takes the whole ladder's fission widths from the same object
        kw = fission_kw(zc, nc)
        return cas.decay(st, nuclei, zc, nc, nex, popeps_mb=popeps_mb,
                         flagfission=kw.get("flagfission", False),
                         nfisbar=kw.get("nfisbar", 0), fission=kw.get("fission"),
                         dmulti=dmulti)

    decay.widths = widths
    return decay


def _seed_mulpre(nuclei: dict, prq) -> None:
    """`population.f90:136` sets `mulpreZN` for the neutron and proton binary residuals, and
    :249 fills their `xspopph2`; everything deeper is set by `multipreeq2` itself. Below
    `emulpre` `population` returns neither, and the whole chain stays dormant.

    TALYS: population.f90:1 (population)
    Test: E2E
    """
    from physics.hf.emission.feeding import PARN, PARZ

    for t, on in prq.mulpre.items():
        nuc = nuclei.get((PARZ[t], PARN[t]))
        if nuc is None or not on:
            continue
        nuc.mulpre = True
        arr = prq.xspopph2_mb.get(t)
        if arr is None:
            continue
        for nex in range(min(arr.shape[0], nuc.xspopex_mb.shape[0])):
            row = arr[nex]
            if float(row.sum()) != 0.0:
                nuc.xspopph2_mb[nex] = torch.as_tensor(row, dtype=DTYPE)


def _with_computed_feeding(cinp: ChannelInputs, mres) -> ChannelInputs:
    """`cinp` with every nucleus's `popexcl`, `feedexcl`, `fisfeedex`, `xsfeed` and `xspopnuc`
    replaced by the computed ones. Everything else is structure and configuration.

    TALYS: multiple.f90:1 (multiple)
    Test: E2E
    """
    from copy import copy

    out = copy(cinp)
    out.nuclei = {}
    for k, ns in cinp.nuclei.items():
        n = copy(ns)
        n.popexcl_mb = mres.popexcl_mb.get(k, {})
        n.feedexcl_mb = mres.feedexcl_mb.get(k, {})
        n.fisfeedex_mb = mres.fisfeedex_mb.get(k, {})
        n.xsfeed_mb = mres.xsfeed_mb.get(k, {})
        if k in mres.xspopnuc_mb:
            n.xspopnuc_mb = mres.xspopnuc_mb[k]
        out.nuclei[k] = n
    return out


def run(cases=None, options=None, params=None, *, injection: Injection | None = None) -> Results:
    """Cross sections for every case, TALYS defaults unless `options`/`params` say otherwise.

    TALYS: talysreaction.f90:1 (talysreaction)
    Test: E2E
    """
    if injection is None:
        raise NotImplementedError(
            "engine.run without injection is still two seams short, both named in this module's "
            "docstring: compnorm.f90 + population.f90 (CNfactor, xsflux, J2beg/J2end, Tjlinc) "
            "and multiple.f90's feeding chain (compound.continuum over every residual bin, with "
            "densprepare(primary=False) and excitation.f90's re-gridding). densprepare itself is "
            "ported -- pass `injection=ChainedCompound(run_dir, cn_dir, Z, A)` to build the "
            "binary compound populations from T5/T6/T7, or `DumpInjection(run_dir)` to inject "
            "everything. Either way the families supplied are reported in Results.injected."
        )
    per_case = injection.cases()
    e_inc, chans, levels, resid, totals = [], [], [], [], []
    bstate = BinaryState()  # binary.f90's sfactor is run-scoped, not energy-scoped
    # `chanopen`/`idnumfull` are run-scoped too (strucinitial.f90), and a dumped case carries
    # TALYS's own set, which is what the injected gate scores. With nothing injected there is no
    # set to carry, so the engine keeps its own across the ascending energy loop, as TALYS does.
    cstate = ExclusiveState() if not injection.families else None
    for binp, cinp in per_case:
        e_inc.append(binp.e_inc_mev)
        b = binary(binp, bstate)
        ch = exclusive_channels(cinp, cstate)
        chans.append({f"xs{code:06d}": v for code, v in ch.xschannel_mb.items()})
        levels.append({
            level_key(binp.k0, t, nex): float(v[nex])
            for t, v in b.xsdisc_mb.items() for nex in range(v.shape[0])
        })
        resid.append({residual_key(Z, A): v for (Z, A), v in ch.residual_mb.items()})
        if os.environ.get("INCOGNITA_RP_ISOMERS") == "1":
            # residual.f90's isomeric production (rpZZZAAA.L00 ground, .Lnn each isomer), from
            # the Python channel path only: the C engine does not carry xsbranch
            for (Z, A), br in ch.xsbranch.items():
                pop = ch.residual_mb.get((Z, A), 0.0)
                for nex, f in br.items():
                    resid[-1][f"{residual_key(Z, A)}.L{nex:02d}"] = pop * f
        totals.append({
            "elastic": float(b.xselastot_mb), "nonelastic": float(b.xsnonel_mb),
            # sigma_tot is the incident channel's (T5/A-inc); binary.f90 only forms it itself for
            # a photon projectile, so this is the identity sigma_tot = sigma_el + sigma_nonel.
            "total": float(b.xselastot_mb + b.xsnonel_mb),
            "reaction": cinp.xsreacinc_mb, "compound_elastic": float(b.xscompel_mb),
            "fission": ch.xsfistot_mb, "residual_production": ch.xsresprod_mb,
            **{f"{PARSYM[binp.k0]}{PARSYM[t]}": v for t, v in ch.xsexclusive_mb.items()},
        })
    res = Results(
        e_inc_mev=torch.tensor(e_inc, dtype=DTYPE),
        channels_mb=_stack(chans), levels_mb=_stack(levels),
        residual_production_mb=_stack(resid), totals_mb=_stack(totals),
        injected=injection.families,
    )
    # DIRECTCAP: direct radiative capture (racap), off unless INCOGNITA_DIRECT_CAPTURE is set
    from physics.hf.direct.racapcalc import add_to_results

    return add_to_results(res, injection)


def _stack(per_case: list[dict[str, float]]) -> dict[str, torch.Tensor]:
    keys = sorted({k for d in per_case for k in d})
    return {k: torch.tensor([d.get(k, 0.0) for d in per_case], dtype=DTYPE) for k in keys}
