"""Multiple pre-equilibrium emission from the continuum bins of a cascade nucleus.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T8, rewritten by EXCL3 (physics/hf/CONTRACT.md §7). Acceptance test: A-mpe (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    multipreeq2.f90:1 (multipreeq2)

`multipreeq2` runs inside the multi-chance cascade: `multiple.f90:549-554` calls it for every
excited bin `nex` of every residual `(Zcomp, Ncomp)` for which `mulpreZN` is set, after
`densprepare` and *before* the compound decay of that bin, and it does two things --
it feeds the two nucleon daughters directly (bypassing Hauser-Feshbach), and it hands
`compound.f90:402` the depletion factor `Dmulti(nex)` that the compound decay of the same bin is
then reduced by. It is live only at `Einc >= emulpre` (20 MeV, `input_preeqmodel.f90:83`), because
that is the only condition under which `population.f90` fills `xspopph2` at all.

This module keeps the routine a pure function (contract §4.3): the mother's particle-hole
population goes in, the daughters' additions come out, and `emission.feeding` threads them.

**Five things a vectorised transcription gets wrong, all reproduced here.**

* The loop over particle-hole pairs is **sequential, and it writes into the array it is
  iterating over**: multipreeq2.f90:297-305 moves the flux a pair did not emit into
  `(ipp+1, ihp+1, ipn, ihn)` and `(ipp, ihp, ipn+1, ihn+1)`, both of which come *later* in
  TALYS's loop order, so they are reached with the augmented population. Computing every pair
  from the entry-state array drops the whole multiple-pre-equilibrium cascade above the first
  stage.
* **`gsp`/`gsn` leak across pairs.** They are set from the mother at multipreeq2.f90:161-168 and
  then overwritten *inside* the outgoing-bin loop with the daughter's `gp(Zix, Nix)`/`gn(Zix, Nix)`
  (:226-232) and never restored, so every pair after the first live one computes its
  `omegaph` (:180) with the **last daughter's** single-particle densities, not the mother's.
  `gsp_state`/`gsn_state` below carry exactly that state.
* The `Apauli2` correction `phdens2` subtracts is TALYS's **precomputed table**, built once in
  `preeqinit.f90:99-117` from `gp(0, 0)`/`gn(0, 0)` -- the *initial* compound nucleus, not the
  nucleus being decayed and not the leaked `gsp`. Passed through as `ap2`.
* The normalisation block (:171-186) indexes `Nlast(Zix, Nix, 0)` with the `Zix`/`Nix` **left
  over from the last iteration of the preceding type loop** -- the proton daughter's, for both
  types. `last` below is that latch.
* `omegaph <= 0` does not skip the pair, it only makes every `term` zero; the pair then
  transfers its *whole* `feedph` to the next stage.

`mpreeqmode 1` (multipreeq2.f90:93-107, a full two-component exciton restart from an arbitrary
`(ppi, hpi, pnu, hnu)`) is not ported; TALYS's default is 2 (`input_preeqmodel.f90:74`).
`flag2comp` false routes TALYS to the one-component `multipreeq.f90` instead, which is also not
ported; `flag2comp` is true for every reference run.

Units: cross sections mb, energies MeV. float64 (§4.1); `term` is `real(sgl)` in TALYS and the
gate shows that costs ~1e-7 relative, well inside A-mpe's tolerance, so it is not emulated.
Differentiable in `gp`/`gn` and in the transmission coefficients; the two hard branches
(`feedph <= 1e-10`, `sumterm > feedph`) are §4.4 branches, taken on detached scalars.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import torch
from torch import Tensor

from physics.hf.core.tensors import DTYPE
from physics.hf.density.particle_hole import EFERMI_MEV, apauli2, phdens2

NUMZPH = 4  # A0_talys_mod.f90:34
NUMNPH = 8  # A0_talys_mod.f90:35
NUMPARX = 6  # A0_talys_mod.f90:1407, numexc/2
PARZ = (0, 0, 1)  # parZ(type) for type 1, 2
PARN = (0, 1, 0)
FEED_MIN_MB = 1.0e-10  # multipreeq2.f90:66, :176


@dataclass(frozen=True)
class MpeDaughter:
    """One nucleon daughter `(Zix, Nix) = Zindex/Nindex(Zcomp, Ncomp, type)` of the mother bin.

    `ex_mev`, `dex_mev`, `tswave`, `damp`, `maxj` are indexed by the daughter's own `nexout`,
    from 0; only `nlast + 1 .. nexmax` are read (multipreeq2.f90:216).
    """

    type: int  # 1 = neutron, 2 = proton
    zix: int
    nix: int
    nlast: int  # Nlast(Zix, Nix, 0)
    nexmax: int  # nexmax(type), -1 when no bin is reachable
    parskip: bool
    s_mev: float  # S(Zcomp, Ncomp, type)
    gp: Tensor  # gp(Zix, Nix)
    gn: Tensor  # gn(Zix, Nix)
    ex_mev: Tensor  # (B,)
    dex_mev: Tensor  # (B,)
    tswave: Tensor  # (B,) Tjl(type, nen, 1, 0) at Eo = Exinc - Eex - S
    maxj: tuple  # (B,) int, maxJ(Zix, Nix, nexout)
    damp: Tensor | None = None  # (B,) ignatyuk(Zix, Nix, Eex, 0) / alev(Zix, Nix); flaggshell only

    @property
    def live(self) -> bool:
        """multipreeq2.f90:199-201: parskip, and outside the `xspopph2` box there is no array."""
        return not self.parskip and self.zix <= NUMZPH and self.nix <= NUMNPH


@dataclass(frozen=True)
class MultiPreeqInputs:
    """One mother bin `(Zcomp, Ncomp, nex)`, with everything multipreeq2 reads off a global."""

    zcomp: int
    ncomp: int
    nex: int
    exinc_mev: Tensor  # scalar, Exinc
    dexinc_mev: Tensor  # scalar, dExinc
    xspopex_mother_mb: Tensor  # scalar, xspopex(Zcomp, Ncomp, nex) before the depletion
    xspopph2_mb: Tensor  # (P+1, P+1, P+1, P+1), indexed (ipp, ihp, ipn, ihn)
    gp_comp: Tensor  # gp(Zcomp, Ncomp)
    gn_comp: Tensor
    gp_cn0: Tensor  # gp(0, 0) -- the Apauli2 table's own densities (preeqinit.f90:99)
    gn_cn0: Tensor
    daughters: tuple  # (MpeDaughter, MpeDaughter) for type 1, 2
    rnj: Tensor  # (numJ+1,) RnJ(2, J)
    rnjsum: Tensor  # scalar, RnJsum(2)
    maxpar: int = NUMPARX
    flaggshell: bool = False  # input_preeqmodel.f90:62
    damp_comp: Tensor | None = None  # ignatyuk(Zcomp, Ncomp, Exinc, 0) / alev(Zcomp, Ncomp)
    efermi_mev: float = EFERMI_MEV
    mpreeqmode: int = 2  # input_preeqmodel.f90:74
    flag2comp: bool = True


@dataclass
class MultiPreeqResult:
    """multipreeq2.f90's outputs for one mother bin.

    `term_mb` is `mpecontrib(type, nex, nexout)` = `mcontrib`'s multiple-pre-equilibrium addend
    and the flux each daughter bin receives; `sumtype_mb` is `xsmpe(type, nex)`; `dmulti` is
    `Dmulti(nex)`, which `compound.f90:402` multiplies `(1 - Dmulti)` into.
    """

    dmulti: Tensor  # scalar
    summpe_mb: Tensor  # scalar
    term_mb: Tensor  # (2, B)
    sumtype_mb: Tensor  # (2,)
    xspop_add_mb: Tensor  # (2, B, numJ+1) per parity half, the `Jterm` of :272-277
    xspopph2_mother_mb: Tensor  # (P+1,)*4, after the leftover-flux transfers
    # (type, ipp, ihp, ipn, ihn) -> (B,): what each daughter's `xspopph2` row gains
    xspopph2_daughter_mb: dict = field(default_factory=dict)
    mulpre: tuple = (False, False)  # mulpreZN(Zix, Nix) for type 1, 2


def _zero(inp: MultiPreeqInputs, numj: int) -> MultiPreeqResult:
    dev = inp.exinc_mev.device
    b = inp.daughters[0].ex_mev.shape[0]
    p = inp.maxpar
    z = torch.zeros((), dtype=DTYPE, device=dev)
    return MultiPreeqResult(
        dmulti=z, summpe_mb=z, term_mb=torch.zeros(2, b, dtype=DTYPE, device=dev),
        sumtype_mb=torch.zeros(2, dtype=DTYPE, device=dev),
        xspop_add_mb=torch.zeros(2, b, numj + 1, dtype=DTYPE, device=dev),
        xspopph2_mother_mb=inp.xspopph2_mb.clone(),
        xspopph2_daughter_mb={}, mulpre=(False, False))


def multiple_preequilibrium(inp: MultiPreeqInputs, numj: int = 40) -> MultiPreeqResult:
    """Two-component multiple pre-equilibrium emission out of one mother bin.

    TALYS: multipreeq2.f90:1 (multipreeq2)
    Test: A-mpe
    """
    if inp.mpreeqmode != 2:
        raise NotImplementedError(
            "EXCL3: mpreeqmode 1 (a full exciton restart per particle-hole pair, "
            "multipreeq2.f90:93-107) is not ported; TALYS's default is 2")
    if not inp.flag2comp:
        raise NotImplementedError(
            "EXCL3: flag2comp false routes multiple.f90:553 to the one-component "
            "multipreeq.f90, which is not ported; TALYS's default is two-component")
    # multipreeq2.f90:139 -- the initial compound nucleus has no particle-hole population of
    # its own; `population.f90` seeds only its daughters.
    if inp.zcomp == 0 and inp.ncomp == 0:
        return _zero(inp, numj)
    if float(inp.xspopph2_mb.sum()) <= FEED_MIN_MB:  # :140-151
        return _zero(inp, numj)

    dev = inp.exinc_mev.device
    p = inp.maxpar
    b = inp.daughters[0].ex_mev.shape[0]
    ef = torch.full((), inp.efermi_mev, dtype=DTYPE, device=inp.exinc_mev.device)

    # :161-168. surfwell is .false. throughout multipreeq2.
    gsp_state, gsn_state = inp.gp_comp, inp.gn_comp
    if inp.flaggshell:
        gsp_state = gsp_state * inp.damp_comp
        gsn_state = gsn_state * inp.damp_comp

    mother = {}
    pop0 = inp.xspopph2_mb
    for ipp in range(p + 1):
        for ihp in range(p + 1):
            for ipn in range(p + 1):
                for ihn in range(p + 1):
                    v = pop0[ipp, ihp, ipn, ihn]
                    if float(v) != 0.0:
                        mother[(ipp, ihp, ipn, ihn)] = v
    zero = torch.zeros((), dtype=DTYPE, device=dev)
    summpe = zero
    term_tot = torch.zeros(2, b, dtype=DTYPE, device=dev)
    sumtype_tot = torch.zeros(2, dtype=DTYPE, device=dev)
    xspop_add = torch.zeros(2, b, numj + 1, dtype=DTYPE, device=dev)
    dpop: dict = {}
    mulpre = [False, False]
    last = inp.daughters[0]  # the stale (Zix, Nix) of the normalisation block (:173)
    # :272-277, hoisted: `Jterm` is `0.5 (2J+1) RnJ(2, J) / RnJsum(2)` times `term`, cut at
    # `maxJ(Zix, Nix, nexout)`, and neither factor depends on the particle-hole pair.
    jj = torch.arange(numj + 1, dtype=DTYPE, device=dev)
    jw = torch.zeros(2, b, numj + 1, dtype=DTYPE, device=dev)
    for d in inp.daughters:
        w = 0.5 * (2.0 * jj + 1.0) * inp.rnj / inp.rnjsum
        for nexout in range(b):
            jw[d.type - 1, nexout, : min(int(d.maxj[nexout]), numj) + 1] = (
                w[: min(int(d.maxj[nexout]), numj) + 1])

    # :174-306, in TALYS's loop order, because :297-305 writes into `mother` ahead of the cursor.
    for ipp in range(p + 1):
        for ihp in range(p + 1):
            for ipn in range(p + 1):
                ip = ipp + ipn
                if ip == 0 or ip > p:  # :177
                    continue
                for ihn in range(p + 1):
                    ih = ihp + ihn
                    if ih == 0 or ih > p:  # :180
                        continue
                    feedph = mother.get((ipp, ihp, ipn, ihn), zero)
                    if float(feedph) <= FEED_MIN_MB:  # :183
                        continue
                    ap = apauli2(
                        torch.tensor(ipp, device=dev), torch.tensor(ihp, device=dev),
                        torch.tensor(ipn, device=dev), torch.tensor(ihn, device=dev),
                        inp.gp_cn0, inp.gn_cn0)
                    omegaph = phdens2(  # :186
                        torch.tensor(ipp, device=dev), torch.tensor(ihp, device=dev),
                        torch.tensor(ipn, device=dev), torch.tensor(ihn, device=dev),
                        gsp_state, gsn_state, inp.exinc_mev, ef, False, ap2=ap)
                    live_om = float(omegaph) > 0.0  # :224

                    term = torch.zeros(2, b, dtype=DTYPE, device=dev)
                    sumtype = [zero, zero]
                    sumterm = zero
                    for d in inp.daughters:  # :194
                        ti = d.type - 1
                        if d.parskip:  # :196
                            continue
                        last = d  # Zix/Nix are assigned before the numZph cut (:197-199)
                        if d.zix > NUMZPH or d.nix > NUMNPH:  # :201
                            continue
                        zej, nej = PARZ[d.type], PARN[d.type]
                        if ipp - zej < 0 or ipn - nej < 0:  # :205-207
                            continue
                        lo, hi = d.nlast + 1, d.nexmax
                        if hi < lo:
                            continue
                        if live_om:
                            # :226-232. Assigned inside the outgoing-bin loop and never
                            # restored, so what leaks to the next pair's `omegaph` is the value
                            # the LAST bin left behind.
                            gsp_o, gsn_o = d.gp, d.gn
                            if inp.flaggshell:
                                gsp_o = gsp_o * d.damp[lo:hi + 1]
                                gsn_o = gsn_o * d.damp[lo:hi + 1]
                                gsp_state, gsn_state = gsp_o[-1], gsn_o[-1]
                            else:
                                gsp_state, gsn_state = gsp_o, gsn_o
                            eex = d.ex_mev[lo:hi + 1]
                            dex = d.dex_mev[lo:hi + 1].clone()
                            ap1 = apauli2(
                                torch.tensor(ipp - zej, device=dev),
                                torch.tensor(ihp, device=dev),
                                torch.tensor(ipn - nej, device=dev),
                                torch.tensor(ihn, device=dev), inp.gp_cn0, inp.gn_cn0)
                            omegap1h = phdens2(  # :233
                                torch.tensor(ipp - zej, device=dev),
                                torch.tensor(ihp, device=dev),
                                torch.tensor(ipn - nej, device=dev),
                                torch.tensor(ihn, device=dev),
                                gsp_o, gsn_o, eex, ef, False, ap2=ap1)
                            ap1p = apauli2(
                                torch.tensor(zej, device=dev), torch.tensor(0, device=dev),
                                torch.tensor(nej, device=dev), torch.tensor(0, device=dev),
                                inp.gp_cn0, inp.gn_cn0)
                            omega1p = phdens2(  # :235
                                torch.tensor(zej, device=dev), torch.tensor(0, device=dev),
                                torch.tensor(nej, device=dev), torch.tensor(0, device=dev),
                                gsp_o, gsn_o, inp.exinc_mev - eex, ef, False, ap2=ap1p)
                            proba = omega1p * omegap1h / omegaph / float(ipp + ipn)  # :236
                            pescape = proba * d.tswave[lo:hi + 1]  # :237-238
                            if hi == d.nexmax:  # :239-243, the top bin runs to the kinematic max
                                exm = inp.exinc_mev + 0.5 * inp.dexinc_mev - d.s_mev
                                exmin = d.ex_mev[hi] - 0.5 * d.dex_mev[hi]
                                dex = torch.cat([dex[:-1], (exm - exmin).reshape(1)])
                            row = feedph * pescape * dex  # :244
                            term[ti, lo:hi + 1] = row
                            sumterm = sumterm + row.sum()  # :245
                        sumtype[ti] = sumtype[ti] + term[ti, lo:hi + 1].sum()  # :259

                    if float(sumterm) > float(feedph):  # :265-280
                        scale = feedph / sumterm
                        for d in inp.daughters:
                            ti = d.type - 1
                            lo, hi = last.nlast + 1, d.nexmax  # the stale Zix/Nix, :268
                            if hi >= lo:
                                term[ti, lo:hi + 1] = term[ti, lo:hi + 1] * scale
                            sumtype[ti] = sumtype[ti] * scale

                    sumph = zero  # :286-296
                    for d in inp.daughters:
                        ti = d.type - 1
                        if not d.live:
                            continue
                        zej, nej = PARZ[d.type], PARN[d.type]
                        if ipp - zej < 0 or ipn - nej < 0:
                            continue
                        lo, hi = d.nlast + 1, d.nexmax
                        if hi >= lo:
                            row = term[ti, lo:hi + 1]
                            key = (d.type, ipp - zej, ihp, ipn - nej, ihn)  # :253-254
                            cur = dpop.get(key)
                            add = torch.zeros(b, dtype=DTYPE, device=dev)
                            add[lo:hi + 1] = row
                            dpop[key] = add if cur is None else cur + add
                            term_tot[ti, lo:hi + 1] = term_tot[ti, lo:hi + 1] + row  # :266-269
                            # :272-277, the same spin distribution for both parities
                            xspop_add[ti, lo:hi + 1] = (
                                xspop_add[ti, lo:hi + 1]
                                + row.unsqueeze(-1) * jw[ti, lo:hi + 1])
                        sumph = sumph + sumtype[ti]  # :281-282
                        summpe = summpe + sumtype[ti]
                        sumtype_tot[ti] = sumtype_tot[ti] + sumtype[ti]
                        if float(sumtype[ti]) != 0.0:  # :292
                            mulpre[ti] = True

                    if ip <= p - 1 and ih <= p - 1:  # :297-305
                        rest = 0.5 * (feedph - sumph)
                        if ipp <= p - 1 and ihp <= p - 1:
                            k = (ipp + 1, ihp + 1, ipn, ihn)
                            mother[k] = mother.get(k, zero) + rest
                        if ipn <= p - 1 and ihn <= p - 1:
                            k = (ipp, ihp, ipn + 1, ihn + 1)
                            mother[k] = mother.get(k, zero) + rest

    out = torch.zeros_like(inp.xspopph2_mb)
    for (a, bb, c, dd), v in mother.items():
        out[a, bb, c, dd] = v
    dmulti = summpe / inp.xspopex_mother_mb  # :374
    return MultiPreeqResult(
        dmulti=dmulti, summpe_mb=summpe, term_mb=term_tot, sumtype_mb=sumtype_tot,
        xspop_add_mb=xspop_add, xspopph2_mother_mb=out, xspopph2_daughter_mb=dpop,
        mulpre=(mulpre[0], mulpre[1]))
