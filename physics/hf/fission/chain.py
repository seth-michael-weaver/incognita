"""Fission transmission for the dump-free chain: T11's `tfission` wired to `engine.ChainedFull`.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T11 (physics/hf/CONTRACT.md §7), the fission port, wired into the chain by TWOPH.
Acceptance test: A-fis (§6) / E2E §5.

T11 ported `fissionpar`, the WKB barrier machinery and `tfission`, and A-fis passes on all five
actinides. What was missing was one wiring step, not a port: `engine.ChainedFull` passed
`tfis=None` to `compound.chain.compound_inputs` and `flagfission=False` to `Cascade.decay`, so a
chained U-238 ran but returned **(n,f) = 0** and the whole actinide group failed to score
(`docs/results/hf-nodump.md`, `hf-e2e.md` §7). This module is what the chain calls instead.

What the compound nucleus needs, and where TALYS builds it
---------------------------------------------------------
`densprepare.f90:399-441` builds the barrier integration grid `eintfis`/`rhofis` ONCE per
fissioning nucleus -- at `Exinc` for the primary compound nucleus and at `Ex(maxex)` for every
later one -- and `tfission.f90` then evaluates `Tfis(J, pi)` at the bin being decayed.
`comptarget.f90` takes the single value at `Exinc`; `compound.f90:120-147` integrates the triple
`(tfisdown, tfis, tfisup)` logarithmically over the mother bin. Both consumers already exist in
the port (`compound.prepare.exit_channel_sums`, `compound.continuum.compound_decay`); they were
simply never given anything.

Index convention. `fission.transmission` returns `(maxj + 1, 2)` tensors indexed by the integer
`J` of `fis*.trans` -- physical spin `J + odd/2`, `odd = A % 2` -- with the parity axis ordered
`(-1, +1)` (contract §4.2). The compound side keys its dictionaries on `(J2, parity)` with
`J2 = 2 * spin` and `parity` in `(-1, +1)`, so the map is `J2 = 2 * J + odd`.

T14's warning (`docs/results/hf-sgl-floor.md`, result 4) is why nothing here is gated per
barrier: a single `T(J, -)` of U-238 moves 5.7x between TALYS's own single- and double-precision
builds on a discrete branch flip. The gate is on the cross sections.

TALYS routines ported here (file:line of the subroutine/function statement):
    densprepare.f90:1 (densprepare)
    tfission.f90:1 (tfission)
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from physics.hf.fission.barriers import NUMJ

__all__ = ["FissionChain", "fission_chain"]

FISLIM = 150  # checkvalue.f90: "Fission not allowed for A <= 150"


@dataclass
class _Nucleus:
    fp: object
    ld: object
    odd: int
    grids: dict  # rounded exfis_top -> FissionLevelDensities


class FissionChain:
    """Per-nucleus fission transmission for one run, built once and cached.

    One instance serves every incident energy and every residual nucleus of a chained run: the
    barrier parameters (`fissionpar`) and the barrier level densities (T6 with `ibar > 0`) depend
    only on the nucleus, and `densprepare`'s integration grid only on the nucleus and the top of
    its bin ladder.

    TALYS: densprepare.f90:1 (densprepare)
    Test: A-fis / E2E
    """

    def __init__(self, Z: int, A: int, options, params=None, maxj: int = NUMJ,
                 fit: tuple = ()) -> None:
        from dataclasses import replace

        from physics.hf.density.overrides import fit_value

        self.Z, self.A = int(Z), int(A)
        self._p = params
        # PARAMWIRE: the run's parameter set; its `aadjust` reaches the barrier level densities,
        # and (FISBARWIRE) its `fismodel` / `fisbaradjust` / `fishwadjust` the barriers themselves
        self.fit = tuple(fit or ())
        fm = fit_value(self.fit, "fismodel", 0, 0)
        if fm is not None and int(fm) != int(options.fismodel):
            # TALYS's `fismodel` is global, but outside `fissionpar` / `t1barrier` it is read only
            # by `axtype` and the `vfiscor` default (both fission-only here) and by `colenhance`
            # under `colldamp y` (off by default), so the chain's own options carry it
            options = replace(options, fismodel=int(fm))
        self.o = options
        self.maxj = int(maxj)
        self._nuc: dict[tuple[int, int], _Nucleus | None] = {}
        self._masses = None

    # ---- lazily built per-nucleus pieces -----------------------------------------------------

    def params(self):
        if self._p is None:
            from physics.hf.density.overrides import (
                aadjust_entries,
                with_aadjust,
                with_fission_adjust,
            )
            from physics.hf.input.defaults import default_params

            self._p = with_fission_adjust(
                with_aadjust(default_params(self.Z, self.A, self.o), self.o,
                             aadjust_entries(self.fit)), self.o, self.fit)
        return self._p

    def masses(self):
        if self._masses is None:
            from physics.hf.structure.masses import masses as _m

            self._masses = _m(self.o, self.params())
        return self._masses

    def nucleus(self, Z: int, A: int) -> _Nucleus | None:
        """Barrier parameters and barrier level densities of one nucleus, or `None` if it does
        not fission (`A <= 150`, or `fissionpar` finds no barrier)."""
        key = (Z, A)
        if key in self._nuc:
            return self._nuc[key]
        got = None
        if A > FISLIM:
            from physics.hf.density.matching import densitymatch
            from physics.hf.density.parameters import densitypar
            from physics.hf.density.tables import attach_tables
            from physics.hf.fission.parameters import barrier_levels, fission_parameters
            from physics.hf.structure.levels import discrete_levels

            # masses from `params()` too: no parameter-set keyword reaches structure.masses
            p, ms = self.params(), self.masses()
            fp = fission_parameters(Z, A, self.o, p, masses=ms)
            if int(fp.nfisbar) > 0:
                lv = discrete_levels(Z, A, self.o, ms, p)
                ld = densitymatch(attach_tables(densitypar(
                    Z, A, self.o, p, ms, lv, barriers=barrier_levels(fp))))
                got = _Nucleus(fp=fp, ld=ld, odd=A % 2, grids={})
        self._nuc[key] = got
        return got

    def nfisbar(self, Z: int, A: int) -> int:
        n = self.nucleus(Z, A)
        return 0 if n is None else int(n.fp.nfisbar)

    def _grid(self, n: _Nucleus, exfis_top_mev: float):
        from physics.hf.fission.transmission import fission_level_densities

        key = round(float(exfis_top_mev), 9)
        if key not in n.grids:
            n.grids[key] = fission_level_densities(
                n.fp, n.ld, key, odd=n.odd, maxj=self.maxj)
        return n.grids[key]

    # ---- what the two compound consumers ask for ---------------------------------------------

    def transmission(self, Z: int, A: int, exinc_mev: float, dexinc_mev: float,
                     exfis_top_mev: float, *, exmax_mev: float | None = None,
                     primary: bool = False, fnorm: float = 1.0):
        """`FissionTransmission` for one mother bin, or `None` if the nucleus does not fission.

        TALYS: tfission.f90:1 (tfission)
        Test: A-fis / E2E
        """
        from physics.hf.fission.transmission import fission_transmission

        n = self.nucleus(Z, A)
        if n is None:
            return None
        return fission_transmission(
            n.fp, self._grid(n, exfis_top_mev), n.ld, float(exinc_mev), float(dexinc_mev),
            self.o, exmax_mev=exmax_mev, odd=n.odd, maxj=self.maxj, primary=primary,
            fnorm=fnorm,
        )

    def compound_target(self, Z: int, A: int, exinc_mev: float, fnorm: float = 1.0) -> dict:
        """`tfis`/`tfisA`/`rhofisA`/`nfisbar` for `compound.chain.compound_inputs`, i.e. the
        PRIMARY compound nucleus at the incident energy.

        `comptarget.f90` reads the single value at `Exinc` (and, when the width-fluctuation
        correction is on, the per-hump `tfisA`/`rhofisA` of `compprepare.f90:407`), so this is
        `tfission` with `dExinc = 0` and `primary = .true.` -- which is also what makes
        `tfisA`/`rhofisA` be filled at all (tfission.f90's `collect` branch).

        TALYS: tfission.f90:1 (tfission)
        Test: A-fis / E2E
        """
        n = self.nucleus(Z, A)
        got = None
        if n is not None:
            from physics.hf.fission.fis_ceng import target_transmission

            got = target_transmission(self, n, float(exinc_mev), fnorm)  # CENGFIS: C, once
        if got is not None:
            m, a, rho = got
        else:
            ft = self.transmission(Z, A, exinc_mev, 0.0, exinc_mev, exmax_mev=exinc_mev,
                                   primary=True, fnorm=fnorm)
            if ft is None:
                return {"tfis": {}, "tfisA": {}, "rhofisA": {}, "nfisbar": 0}
            m = ft.tfis.detach().cpu().numpy()
            a = ft.tfisA.detach().cpu().numpy()
            rho = ft.rhofisA.detach().cpu().numpy()
        odd = n.odd
        tfis = _by_jp(m, odd)
        tfisA, rhofisA = {}, {}
        for (j2, par), _v in tfis.items():
            j = (j2 - odd) // 2
            tfisA[(j2, par)] = a[j, 0 if par < 0 else 1]
            rhofisA[(j2, par)] = rho[j, 0 if par < 0 else 1]
        return {"tfis": tfis, "tfisA": tfisA, "rhofisA": rhofisA,
                "nfisbar": self.nfisbar(Z, A)}

    def bin_triples(self, Z: int, A: int, ex_mev: float, dex_mev: float, exmax_mev: float,
                    exfis_top_mev: float, fnorm: float = 1.0) -> dict:
        """`{(J2, parity): (tfisdown, tfis, tfisup)}` for `compound.continuum.compound_decay`,
        i.e. one mother bin of one residual nucleus.

        `compound.f90:120-147` integrates those three logarithmically over the bin, which is why
        `tfission` is evaluated at `Ex - dEx/2`, `Ex` and `Ex + dEx/2` (clipped at `Exmax`).

        TALYS: compound.f90:1 (compound), tfission.f90:1 (tfission)
        Test: A-fis / E2E
        """
        ft = self.transmission(Z, A, ex_mev, dex_mev, exfis_top_mev, exmax_mev=exmax_mev,
                               primary=False, fnorm=fnorm)
        if ft is None:
            return {}
        odd = self.nucleus(Z, A).odd
        d = ft.tfisdown.detach().cpu().numpy()
        m = ft.tfis.detach().cpu().numpy()
        u = ft.tfisup.detach().cpu().numpy()
        out = {}
        for j in range(m.shape[0]):
            for k, par in ((0, -1), (1, 1)):
                if d[j, k] == 0.0 and m[j, k] == 0.0 and u[j, k] == 0.0:
                    continue
                out[(2 * j + odd, par)] = (float(d[j, k]), float(m[j, k]), float(u[j, k]))
        return out


def _by_jp(arr: np.ndarray, odd: int) -> dict:
    """A `(maxj+1, 2)` array as `{(J2, parity): value}`, dropping exact zeros the way a dump
    does -- `exit_channel_sums` defaults a missing key to 0.0."""
    out = {}
    for j in range(arr.shape[0]):
        for k, par in ((0, -1), (1, 1)):
            if arr[j, k] != 0.0:
                out[(2 * j + odd, par)] = float(arr[j, k])
    return out


def fission_chain(Z: int, A: int, options=None, params=None, fit: tuple = ()
                  ) -> FissionChain | None:
    """A `FissionChain` for a target that fissions at its defaults, else `None`.

    `input_fissionmodel.f90:78-80` sets `flagfission` from `A > 215` for the TARGET; the
    compound nucleus and every residual heavier than `A = 150` then get barriers of their own.

    TALYS: fissionpar.f90:1 (fissionpar)
    Test: E2E
    """
    from physics.hf.input.defaults import default_options

    o = options if options is not None else default_options(Z, A)
    if not bool(o.flagfission):
        return None
    return FissionChain(Z, A, o, params, fit=fit)
