"""Assemble `comptarget`'s `CompoundInputs` from the ported components, with no compound-nucleus
dump behind it.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T9, continued by EXCL (physics/hf/CONTRACT.md §7). Acceptance test: A-cn1 / E2E (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    talysreaction.f90:1 (talysreaction)  -- the order incident -> exgrid -> compnorm -> densprepare

`compound.dens_reference.chained_compound_inputs` (E2E) already replaced the four `densprepare`
arrays of a *dumped* `CompoundInputs` with built ones. It still needed the dump for two separate
reasons: the compound nucleus's normalisation (`CNfactor`, `xsflux`, `J2beg`/`J2end`, `Tjlinc`),
and the residuals' structure records (`Zix`, `maxex`, `Nlast`, `Ex`, `deltaEx`, `maxJ`, `parlev`,
`jdis`, `S`) that `densprepare` needs as a grid. `compnorm` is now chained
(`compound.norm_reference`) and the grids are now built per cascade nucleus
(`emission.feeding.Cascade.spec`), so neither reason survives -- which is what lets the chained
binary stage run on all 14 spherical targets instead of the 9 that have a `cndump` reference run.

The per-energy switches come from the RESOLVED onsets, not from `default_options`'s raw record:
`ewfc` keeps input_compoundmodel.f90:84's -1 sentinel there, and `Einc <= -1.` is false at every
energy, so reading it raw turns the width-fluctuation correction off for the whole chained arm
without any array going red (`Cascade.ewfc_mev`, nuclides.f90:251). That was worth 8% on the
1 keV Fe-56 capture cross section. `Fnorm` is the same shape of mistake: it is `1 / fiso` of the
INITIAL COMPOUND NUCLEUS for the primary decay (comptarget.f90:281, :338), not 1, and densprepare
multiplies every `Tgam` and `Tjlnex` by it (`Cascade.fiso`).

`Exinc = Etotal` and `dExinc = 0` for the primary decay (reacinitial.f90:370, comptarget.f90:275),
and `nexmax(type) = maxex(Zix, Nix)` (exgrid.f90:180) -- the primary compound nucleus can reach
every bin of every binary residual, unlike a continuum mother bin.
"""

from __future__ import annotations

import numpy as np

from physics.hf.compound.prepare import (
    CompoundInputs,
    DensPrepareInputs,
    DensResidual,
    densprepare,
)

PARZ = (0, 0, 1, 1, 1, 2, 2)
PARN = (0, 1, 0, 1, 2, 1, 2)


def primary_dens_inputs(cas, st, etotal_mev: float, *, gammax: int,
                        flagfullhf: bool = False) -> DensPrepareInputs:
    """`DensPrepareInputs` of the primary decay: the whole compound nucleus at `Etotal`.

    TALYS: densprepare.f90:1 (densprepare)
    Test: A-cn1
    """
    from physics.hf.compound.dens_reference import DensTrans, _eendmax

    sp = cas.spec(st, 0, 0)
    eend = _eendmax(cas.Zt, cas.At, cas.enincmax)
    residuals, trans = {}, {}
    for t in range(7):
        d = cas.spec(st, PARZ[t], PARN[t])
        residuals[t] = DensResidual(
            type=t, zix=d.zix, nix=d.nix, A=d.A, nlast=d.nlast, ntop=d.ntop,
            nexmax=d.maxex, sep_mev=sp.sep_mev[t], ex_mev=d.ex_mev, dex_mev=d.dex_mev,
            maxj=d.maxj, parlev=d.parlev, jdis=d.jdis, rhogrid=d.rhogrid, ncum_nl=d.ncum_nl)
        if t >= 1:
            tjl, tl, lmax = cas.trans[t]
            trans[t] = DensTrans(
                egrid_mev=cas.rg.egrid, ebegin=cas.rg.ebegin[t],
                eend=min(int(eend[t]), cas.rg.maxen), maxen=cas.rg.maxen,
                tjl=tjl, tl=tl, lmax=lmax)
    return DensPrepareInputs(
        exinc_mev=float(etotal_mev), dexinc_mev=0.0, s_n_mev=sp.sep_mev[1], gammax=gammax,
        lmaxinc=st.lmaxinc, k0=cas.k0, fnorm=cas.fiso(), residuals=residuals, trans=trans,
        gamma_strength=cas.gamma_strength(cas.Zt, cas.At), primary=True,
        flagfullhf=flagfullhf, transeps=cas.transeps,
        gamma_params=cas.gamma_params(cas.Zt, cas.At))  # PARAMWIRE: the run's parameter set


def compound_inputs(cas, st, binp, cinp, etotal_mev: float, add: dict,
                    *, tfis: dict | None = None, nfisbar: int = 0,
                    tfisA: dict | None = None, rhofisA: dict | None = None) -> CompoundInputs:
    """`CompoundInputs` for one incident energy, built rather than dumped.

    `binp`/`cinp` supply only the structure-and-configuration scalars that gates A-grid and
    A-struct cover and that no physics module produces (`Ltarget`, the target's spin and parity,
    `popeps`, `xseps`); `add` is `norm_reference.addends`' T8/T12 sums for this energy.

    TALYS: talysreaction.f90:1 (talysreaction)
    Test: A-cn1 / E2E
    """
    from physics.hf.compound.norm_reference import chained_formation

    o = cas.options
    cf, lmaxinc = chained_formation(cas, _NormView(binp), add)
    res = densprepare(primary_dens_inputs(cas, st, etotal_mev, gammax=o.gammax))
    inc = cas.incident(binp.e_inc_mev)
    from physics.hf.compound.dens_reference import _to_updown_axis

    # DIFFPARAM: with an optical override on the graph the incident channel is a tensor and
    # must stay one -- `cnfactor`, `Tjlinc` and sigma_reac are exactly where an OMP parameter
    # enters the compound cross section. Without one this is the byte-identical numpy of before.
    tjl_t = _to_updown_axis(inc.tjl_inc[0], cas.k0)[: lmaxinc + 1]
    grad = bool(getattr(cas, "diff_params", False))
    tjlinc = tjl_t if grad else tjl_t.detach().numpy()
    out = CompoundInputs(
        e_inc_mev=binp.e_inc_mev,
        cnfactor_mb=cf.cn_factor_mb if grad else float(cf.cn_factor_mb),
        xsflux_mb=float(cf.xs_flux_mb),
        xsreacinc_mb=inc.sigma_reac_mb[0] if grad else float(inc.sigma_reac_mb[0]),
        j2beg=cf.j2beg, j2end=cf.j2end, targetspin2=binp.targetspin2,
        target_parity=binp.target_parity, lmaxinc=lmaxinc, k0=binp.k0, ltarget=binp.ltarget,
        wmode=o.wmode, wfcfactor=o.WFCfactor, gammax=o.gammax, nfisbar=nfisbar,
        flagwidth=bool(binp.e_inc_mev <= cas.ewfc_mev), flagfission=bool(cinp.flagfission),
        tjlinc=tjlinc, exinc_mev=float(etotal_mev), dexinc_mev=0.0, fnorm=cas.fiso(),
        tfis=tfis or {}, popeps_mb=binp.popeps_mb, flagpreeq=binp.flagpreeq,
        # compprepare.f90:407 tests the per-hump Hill-Wheeler width, so `comptarget`'s
        # width-fluctuation branch needs `tfisA`/`rhofisA` as well as the combined `tfis`
        tfisA=tfisA or {}, rhofisA=rhofisA or {},
    )
    out.residuals = res
    return out


class _NormView:
    """`chained_formation` reads only these five fields off a `CompoundInputs`; a `BinaryInputs`
    carries all of them, so the chained path needs no compound dump at all."""

    def __init__(self, binp):
        self.e_inc_mev = binp.e_inc_mev
        self.k0 = binp.k0
        self.targetspin2 = binp.targetspin2
        self.target_parity = binp.target_parity
        self.lmaxinc = 0
