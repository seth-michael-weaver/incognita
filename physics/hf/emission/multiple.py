"""The multi-chance cascade: for each residual nucleus in TALYS's order, decay every populated bin
(compound_decay), add multiple pre-equilibrium, and run the gamma cascade through the discrete
levels.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T10 (physics/hf/CONTRACT.md §7). Acceptance test: A-mult (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    multiple.f90:1 (multiple)
    cascade.f90:1 (cascade)

The loop over nuclei (decreasing Z and N) and the loop over mother bins (downward, because the
gamma cascade empties the bin it is standing in) stay Python loops, as CONTRACT §1 allows;
everything inside a bin is a tensor expression, supplied by T9's `compound.continuum.compound_decay`
through the `decay` callback so this module can be exercised with the decay injected.

Quirks this reproduces:
* A discrete level below the neutron separation energy never particle-decays: it only gamma-
  cascades, and only if it is not an isomer (`tau == 0`, multiple.f90:499-503).
* `popexcl` is snapshotted BEFORE the bin decays, and it is what channels.f90 divides by. The
  gamma cascade then subtracts the same flux from `xspopex`, so the two differ by construction.
* `xspopnuc` after the cascade is the ground state plus the isomers only -- everything else has
  decayed away (multiple.f90:643-646).
* Compound decay subtracts `sumIP` from the mother bin's `xspopex` but NOT from its `xspop`, so
  the (J, parity) array still holds the pre-decay population when the next bin is reached.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

import numpy as np
import torch
from torch import Tensor

from physics.hf.core.tensors import DTYPE
from physics.hf.emission.channels import NUMNCHAN, NUMZCHAN, PARN, PARZ
from physics.hf.emission.feed_table import FeedTable

NUMJ = 40


def _pi(parity: int) -> int:
    return 0 if parity == -1 else 1


@dataclass
class NucleusPopulation:
    """One residual nucleus while it is being de-excited: the arrays multiple.f90 mutates."""

    zcomp: int
    ncomp: int
    Z: int
    A: int
    maxex: int
    nlast: int
    ex_mev: Tensor  # (Nex,)
    dex_mev: Tensor  # (Nex,)
    maxj: Tensor  # (Nex,) int
    jdis: Tensor  # (Nex,) float level spin, discrete levels only
    parlev: Tensor  # (Nex,) int
    tau_s: Tensor  # (Nex,)
    sep_mev: dict[int, float]  # type -> S(Zcomp, Ncomp, type)
    branch: dict[int, list[tuple[int, float]]]  # level -> [(daughter level, branching ratio)]
    xspop_mb: Tensor  # (Nex, numJ+1, 2)
    xspopex_mb: Tensor  # (Nex,)
    xspopnuc_mb: float = 0.0
    skipcn: bool = False
    # multiple pre-equilibrium, live only at `Einc >= emulpre`: `mulpreZN(Zcomp, Ncomp)` and the
    # particle-hole population `xspopph2(Zcomp, Ncomp, nex, ipp, ihp, ipn, ihn)`, kept sparse in
    # `nex` because only the bins `population.f90` or `multipreeq2.f90` reached carry any.
    mulpre: bool = False
    xspopph2_mb: dict = field(default_factory=dict)  # nex -> (P+1, P+1, P+1, P+1)


@dataclass(frozen=True)
class BinFeeding:
    """What one mother bin hands to its daughters: T9's `ContinuumFeeding`, or a dump of it."""

    dpop_mb: dict[int, Tensor]  # type -> (Nex_daughter, numJ+1, 2)
    mcontrib_mb: dict[int, Tensor]  # type -> (Nex_daughter,)
    fisfeed_mb: float = 0.0
    # compound.f90:404-419: the flux of a (J, parity) cell with no open exit, which iloop 1
    # spreads equally over the mother nucleus's OWN discrete levels 0..Nlast. It is already in
    # `dpop_mb[0]`; it is NOT in `mcontrib_mb[0]`, because iloop 2 runs that cell with `feed = 0`.
    # `_apply_leftover` puts it in `xspopex` and `mcontrib`/`feedexcl` as compound.f90 does, and
    # leaves `xsfeed`, `xspopnuc` and the mother's own `xspopex` alone, as compound.f90 does.
    leftover_mb: float = 0.0


@dataclass(frozen=True)
class MpeFeeding:
    """What `multipreeq2` takes out of one mother bin and gives its two nucleon daughters.

    `dmulti` is the depletion factor `compound.f90:402` applies to the compound decay of the same
    bin; `term_mb`, `xspop_add_mb` and `sumtype_mb` are per ejectile type (1, 2); `ph_add` maps
    (type, ipp, ihp, ipn, ihn) -> (Nex_daughter,) for the daughter's own `xspopph2`.
    """

    dmulti: float
    summpe_mb: float
    term_mb: dict[int, Tensor]
    xspop_add_mb: dict[int, Tensor]
    sumtype_mb: dict[int, float]
    ph_add: dict
    ph_mother_mb: Tensor | None = None


@dataclass
class MultipleResult:
    """multiple.f90's outputs: what channels.f90 then consumes."""

    popexcl_mb: dict[tuple[int, int], dict[int, float]]
    feedexcl_mb: dict[tuple[int, int], dict[int, dict[tuple[int, int], float]]]
    fisfeedex_mb: dict[tuple[int, int], dict[int, float]] = field(default_factory=dict)
    xsfeed_mb: dict[tuple[int, int], dict[int, float]] = field(default_factory=dict)
    xspartial_mb: dict[tuple[int, int], dict[int, dict[int, float]]] = field(default_factory=dict)
    xsgamdistot_mb: dict[tuple[int, int], float] = field(default_factory=dict)
    xspopnuc_mb: dict[tuple[int, int], float] = field(default_factory=dict)


def _records_feedexcl(zcomp: int, ncomp: int, t: int) -> bool:
    """Whether `multiple.f90` stores `feedexcl` for this (nucleus, ejectile).

    multiple.f90:678 skips it for the INITIAL compound nucleus and any particle:
    `if (Zcomp == 0 .and. Ncomp == 0 .and. type > 0 .and. .not. flaginitpop) cycle`. Its particle
    emission is the binary step, already recorded as the `nex = maxex + 1` row
    (multiple.f90:961), so recording the continuum bins too would double-count every exclusive
    channel. `xsfeed` and `xspartial` are outside that guard and ARE accumulated -- only the
    exclusive-channel feeding array is skipped. The second guard is the size of the exclusive
    bookkeeping itself (multiple.f90:677, `numZchan` = 6, `numNchan` = 10).

    TALYS: multiple.f90:1 (multiple)
    Test: A-mult
    """
    if zcomp > NUMZCHAN or ncomp > NUMNCHAN:
        return False
    return not (zcomp == 0 and ncomp == 0 and t > 0)


def gamma_cascade(nuc: NucleusPopulation, nex: int) -> dict[int, float]:
    """Gamma-ray cascade out of one discrete level into the levels it branches to [mb].

    Returns `mcontrib(0, nex, k)` per daughter level and mutates `nuc` in place, exactly as
    cascade.f90 does: the intensity is taken from the level's single (J, parity) cell, added to
    the daughter's cell and to `xspopex(k)`, and subtracted from `xspopex(nex)`.

    TALYS: cascade.f90:1 (cascade)
    Test: A-mult
    """
    J = int(nuc.jdis[nex].item())
    parity = int(nuc.parlev[nex].item())
    xsjp = nuc.xspop_mb[nex, J, _pi(parity)].clone()
    out: dict[int, float] = {}
    for k, ratio in nuc.branch.get(nex, []):
        jres = int(nuc.jdis[k].item())
        pres = int(nuc.parlev[k].item())
        intens = xsjp * ratio
        nuc.xspop_mb[k, jres, _pi(pres)] += intens
        nuc.xspopex_mb[k] += intens
        nuc.xspopex_mb[nex] -= intens
        out[k] = float(intens)
    return out


def emission_limits(
    mother: NucleusPopulation, daughters: dict[int, NucleusPopulation], nex: int,
    egrid_begin_mev: dict[int, float],
) -> dict[int, int]:
    """Highest daughter bin `nexmax(type)` reachable from mother bin `nex` (multiple.f90:512-533).

    The reference energy is the TOP of the mother bin; for composite ejectiles TALYS also removes
    the first point of the emission grid, so the limit is one bin tighter than the kinematics.

    TALYS: multiple.f90:1 (multiple)
    Test: A-mult
    """
    exinc = float(mother.ex_mev[nex])
    dex = float(mother.dex_mev[nex])
    out: dict[int, int] = {0: nex - 1}
    for t, d in daughters.items():
        if t == 0:
            continue
        exm = exinc + 0.5 * dex - mother.sep_mev.get(t, 0.0)
        if t > 1:
            exm -= egrid_begin_mev.get(t, 0.0)
        out[t] = -1
        for nexout in range(d.maxex, -1, -1):
            if float(d.ex_mev[nexout]) - 0.5 * float(d.dex_mev[nexout]) < exm:
                out[t] = nexout
                break
    return out


def multiple_emission(
    nuclei: dict[tuple[int, int], NucleusPopulation],
    decay: Callable[[int, int, int], BinFeeding | None],
    *,
    popeps_mb: float,
    maxz: int,
    maxn: int,
    k0: int = 1,
    xsreacinc_mb: float = 0.0,
    xsbinary_mb: dict[int, float] | None = None,
    feedbinary_mb: dict[int, Tensor] | None = None,
    flagfission: bool = False,
    flagcomp: bool = True,
    mpe: Callable[[int, int, int], "MpeFeeding | None"] | None = None,
) -> MultipleResult:
    """Residual populations and emission for all nuclei (multiple.f90). The loop over nuclei stays
    a Python loop in TALYS's order; everything per nucleus is tensor code.

    `decay(zcomp, ncomp, nex)` supplies the compound decay of one mother bin -- T9's
    `compound.continuum.compound_decay`, or the same quantity injected from a dump. Returning
    `None` means the bin was skipped.

    `mpe(zcomp, ncomp, nex)` supplies `multipreeq2.f90` for the same bin, and is called where
    multiple.f90:549-554 calls it: after `densprepare` and BEFORE the compound decay, so the
    decay sees the `Dmulti` it produced (`decay` is then given a `dmulti=` keyword). It is
    `None` below `emulpre` (20 MeV), where no nucleus has `mulpreZN` set.

    TALYS: multiple.f90:1 (multiple), cascade.f90:1 (cascade)
    Test: A-mult
    """
    xsbinary_mb = xsbinary_mb or {}
    res = MultipleResult(popexcl_mb={}, feedexcl_mb={})
    for zc in range(maxz + 1):
        for nc in range(maxn + 1):
            key = (zc, nc)
            nuc = nuclei.get(key)
            if nuc is None or nuc.skipcn:
                continue
            popexcl: dict[int, float] = {}
            feedexcl: dict[int, dict[tuple[int, int], float]] = {}
            fisfeed: dict[int, float] = {}
            xsfeed: dict[int, float] = {}
            xspartial: dict[int, dict[int, float]] = {}
            gamdis = 0.0
            res.popexcl_mb[key] = popexcl
            res.feedexcl_mb[key] = feedexcl
            res.fisfeedex_mb[key] = fisfeed
            res.xsfeed_mb[key] = xsfeed
            res.xspartial_mb[key] = xspartial
            if nuc.xspopnuc_mb < popeps_mb:
                nuc.xspopnuc_mb = 0.0
                res.xspopnuc_mb[key] = 0.0
                res.xsgamdistot_mb[key] = 0.0
                _binary_feed(res, key, zc, nc, k0, xsreacinc_mb, xsbinary_mb, feedbinary_mb,
                             nuc, flagfission)
                continue
            popepsA = popeps_mb / max(5 * nuc.maxex, 1)
            smin = nuc.sep_mev.get(1, 0.0)
            daughters = {t: nuclei[(zc + PARZ[t], nc + PARN[t])]
                         for t in range(7) if (zc + PARZ[t], nc + PARN[t]) in nuclei}
            nograd = not any(d.xspop_mb.requires_grad or d.xspopex_mb.requires_grad
                             for d in (nuc, *daughters.values()))
            native = None
            if flagcomp and nograd:
                # NATIVEX: the whole walk in one compiled call, multiple pre-equilibrium included
                from physics.hf.emission.multiple_native import decay_nucleus

                native = decay_nucleus(nuc, daughters, decay, zc, nc, popepsA, smin, popexcl,
                                       feedexcl, xsfeed, xspartial, fisfeed, mpe=mpe)
            if native is not None:
                gamdis = native
            fast = native is None and mpe is None and flagcomp and nograd
            if fast:
                try:
                    gamdis = _decay_nucleus_numpy(nuc, daughters, decay, zc, nc, popepsA, smin,
                                                  popexcl, feedexcl, xsfeed, xspartial, fisfeed)
                except _GraphFeeding:
                    fast = False
            if not fast and native is None:
                for nex in range(nuc.maxex, 0, -1):
                    popexcl[nex] = float(nuc.xspopex_mb[nex])
                    exinc = float(nuc.ex_mev[nex])
                    if nex <= nuc.nlast and exinc <= smin:
                        if float(nuc.tau_s[nex]) == 0.0:
                            contrib = gamma_cascade(nuc, nex)
                            if contrib and _records_feedexcl(zc, nc, 0):
                                fe = feedexcl.setdefault(0, {})
                                part = xspartial.setdefault(0, {})
                                for k, v in contrib.items():
                                    fe[(nex, k)] = fe.get((nex, k), 0.0) + v
                                    part[nex] = part.get(nex, 0.0) + v
                                    gamdis += v
                        continue
                    if float(nuc.xspopex_mb[nex]) < popepsA:
                        continue
                    # multiple.f90:549-554. Not guarded by flagcomp, and it runs before the
                    # compound decay because it is what depletes the bin the decay then shares out.
                    dmulti = 0.0
                    if mpe is not None and nuc.mulpre:
                        m = mpe(zc, nc, nex)
                        if m is not None:
                            dmulti = m.dmulti
                            _apply_mpe(nuc, daughters, nex, m, feedexcl, xspartial, xsfeed, zc, nc)
                    if not flagcomp:
                        continue
                    feeding = (decay(zc, nc, nex) if mpe is None
                               else decay(zc, nc, nex, dmulti=dmulti))
                    if feeding is None:
                        continue
                    if feeding.leftover_mb:
                        _apply_leftover(
                            nuc, nex, feeding.leftover_mb,
                            feedexcl.setdefault(0, {}) if _records_feedexcl(zc, nc, 0) else None,
                            xspartial, nuc.xspopex_mb)
                    for t, dp in feeding.dpop_mb.items():
                        d = daughters.get(t)
                        if d is None:
                            continue
                        sumip = feeding.mcontrib_mb[t]
                        if dp is None:  # compound.decay_fast's closed exit: all zeros
                            dp, sumip = torch.zeros((1, 1, 2), dtype=DTYPE), torch.zeros(1, dtype=DTYPE)
                        elif isinstance(dp, np.ndarray):  # compound.decay_fast's numpy
                            dp, sumip = torch.from_numpy(dp), torch.from_numpy(sumip)
                        n = min(dp.shape[0], d.xspop_mb.shape[0])
                        d.xspop_mb[:n, : dp.shape[1]] += dp[:n]
                        sumip = sumip[:n]
                        d.xspopex_mb[:n] += sumip
                        tot = float(sumip.sum())
                        nuc.xspopex_mb[nex] -= tot
                        d.xspopnuc_mb += tot
                        xspartial.setdefault(t, {})[nex] = (
                            xspartial.setdefault(t, {}).get(nex, 0.0) + tot)
                        xsfeed[t] = xsfeed.get(t, 0.0) + tot
                        if not _records_feedexcl(zc, nc, t):
                            continue
                        fe = feedexcl.setdefault(t, {})
                        for nexout in range(n):
                            v = float(sumip[nexout])
                            if v != 0.0:
                                fe[(nex, nexout)] = fe.get((nex, nexout), 0.0) + v
                    if feeding.fisfeed_mb:
                        fisfeed[nex] = fisfeed.get(nex, 0.0) + feeding.fisfeed_mb
                        xsfeed[-1] = xsfeed.get(-1, 0.0) + feeding.fisfeed_mb
                        nuc.xspopex_mb[nex] -= feeding.fisfeed_mb
            # multiple.f90:643-646: what survives is the ground state and the isomers
            pop = float(nuc.xspopex_mb[0])
            for nex in range(1, nuc.nlast + 1):
                if float(nuc.tau_s[nex]) != 0.0:
                    pop += float(nuc.xspopex_mb[nex])
            nuc.xspopnuc_mb = pop
            res.xspopnuc_mb[key] = pop
            res.xsgamdistot_mb[key] = gamdis
            _binary_feed(res, key, zc, nc, k0, xsreacinc_mb, xsbinary_mb, feedbinary_mb, nuc,
                         flagfission)
    return res


def _decay_nucleus_numpy(nuc: NucleusPopulation, daughters: dict, decay, zc: int, nc: int,
                         popepsA: float, smin: float, popexcl: dict, feedexcl: dict,
                         xsfeed: dict, xspartial: dict, fisfeed: dict) -> float:
    """`multiple_emission`'s loop over the mother bins of one nucleus, on numpy views of the
    population tensors (no graph, no multiple pre-equilibrium). Returns `xsgamdistot`.

    Same operations as the tensor loop, in the same order on every array element, with one
    rearrangement: a particle exit (t >= 1) feeds a DIFFERENT nucleus, which is not read until
    that nucleus is decayed, so its feeding is applied after the walk down this nucleus, bin by
    bin in the same order. Only the photon exit, which feeds this nucleus's own lower bins, is
    applied while walking. That lets `decay` contract the particle exits of all bins at once
    (`compound.decay_fast`), and it leaves each daughter's sums, this nucleus's `xspopex` and the
    `xsfeed`/`xspartial`/`feedexcl` records with the terms they had, added in the order they had.

    TALYS: multiple.f90:1 (multiple), cascade.f90:1 (cascade)
    Test: A-mult / speed-wave golden
    """
    X = nuc.xspop_mb.numpy()
    XE = nuc.xspopex_mb.numpy()
    ex = nuc.ex_mev.tolist()
    tau = nuc.tau_s.tolist()
    jdis = nuc.jdis.tolist()
    parlev = nuc.parlev.tolist()
    rec0 = _records_feedexcl(zc, nc, 0)
    dviews = {t: (d, d.xspop_mb.numpy(), d.xspopex_mb.numpy()) for t, d in daughters.items()}
    gamdis = 0.0
    pending = []
    photon = []
    # compound.f90:404-419 per mother bin. `xspopex` has to move while the walk is still above
    # the discrete levels (the next bin down reads it, and `popexcl` is snapshotted per bin), but
    # the `feedexcl` row cannot: the photon rows are written with `set_row_nonzero` after the
    # walk, which overwrites. So the row is added afterwards, where `add` accumulates.
    leftovers: list[tuple[int, float]] = []
    for nex in range(nuc.maxex, 0, -1):
        popexcl[nex] = float(XE[nex])
        if nex <= nuc.nlast and ex[nex] <= smin:
            if tau[nex] == 0.0:
                # gamma_cascade on the views
                xsjp = float(X[nex, int(jdis[nex]), _pi(int(parlev[nex]))])
                contrib = {}
                for k, ratio in nuc.branch.get(nex, []):
                    intens = xsjp * ratio
                    X[k, int(jdis[k]), _pi(int(parlev[k]))] += intens
                    XE[k] += intens
                    XE[nex] -= intens
                    contrib[k] = intens
                if contrib and rec0:
                    fe = _table(feedexcl, 0, nuc.maxex + 2, X.shape[0])
                    part = xspartial.setdefault(0, {})
                    for k, v in contrib.items():
                        fe.add(nex, k, v)
                        part[nex] = part.get(nex, 0.0) + v
                        gamdis += v
            continue
        if XE[nex] < popepsA:
            continue
        feeding = decay(zc, nc, nex)
        if feeding is None:
            continue
        if not pending and _carries_graph(feeding):
            raise _GraphFeeding  # nothing has been fed yet: the tensor loop starts over
        if feeding.leftover_mb:
            _apply_leftover(nuc, nex, feeding.leftover_mb, None, xspartial, XE)
            leftovers.append((nex, feeding.leftover_mb))
        if 0 in dviews and getattr(feeding.dpop_mb, "nw", None) is not None:
            # compound.decay_fast's photon exit: the four array updates now (the next bin reads
            # them), the records after the walk (their rows are this bin's alone)
            dp0 = feeding.dpop_mb.dp0
            if dp0 is None:
                photon.append((nex, None, 0.0))
            else:
                n = min(dp0.shape[0], X.shape[0])
                sumip = feeding.dpop_mb.mc0[:n]
                X[:n, : dp0.shape[1]] += dp0[:n]
                XE[:n] += sumip
                tot = float(sumip.sum())
                XE[nex] -= tot
                photon.append((nex, sumip, tot))
        elif 0 in feeding.dpop_mb and 0 in dviews:
            _apply_numpy(nuc, XE, dviews[0], 0, nex, feeding.dpop_mb[0], feeding.mcontrib_mb[0],
                         xsfeed, xspartial, feedexcl, _records_feedexcl(zc, nc, 0))
        pending.append((nex, feeding))
    if photon:
        part = xspartial.setdefault(0, {})
        acc_nuc, acc_feed = nuc.xspopnuc_mb, xsfeed.get(0, 0.0)
        for x, _, tot in photon:
            acc_nuc += tot
            part[x] = part.get(x, 0.0) + tot
            acc_feed += tot
        nuc.xspopnuc_mb, xsfeed[0] = acc_nuc, acc_feed
        if rec0:
            fe = _table(feedexcl, 0, nuc.maxex + 2, X.shape[0])
            for x, sumip, _ in photon:
                if sumip is not None:
                    fe.set_row_nonzero(x, sumip)
    if leftovers and rec0:
        fe = _table(feedexcl, 0, nuc.maxex + 2, X.shape[0])
        nl = nuc.nlast
        for x, v in leftovers:
            share = v / (nl + 1.0)
            for nexout in range(min(nl, X.shape[0] - 1) + 1):
                fe.add(x, nexout, share)
    if pending and _apply_particle_batch(nuc, XE, dviews, pending, zc, nc, xsfeed, xspartial,
                                         feedexcl, fisfeed):
        return gamdis
    for nex, feeding in pending:
        for t in feeding.dpop_mb:
            if t == 0 or t not in dviews:
                continue
            _apply_numpy(nuc, XE, dviews[t], t, nex, feeding.dpop_mb[t],
                         feeding.mcontrib_mb[t], xsfeed, xspartial, feedexcl,
                         _records_feedexcl(zc, nc, t))
        if feeding.fisfeed_mb:
            fisfeed[nex] = fisfeed.get(nex, 0.0) + feeding.fisfeed_mb
            xsfeed[-1] = xsfeed.get(-1, 0.0) + feeding.fisfeed_mb
            XE[nex] -= feeding.fisfeed_mb
    return gamdis


def _apply_particle_batch(nuc, XE, dviews: dict, pending: list, zc: int, nc: int, xsfeed: dict,
                          xspartial: dict, feedexcl: dict, fisfeed: dict) -> bool:
    """The particle half of the loop below for a nucleus whose bins all came from one
    `compound.decay_fast.NucleusWidths` batch: per exit, every bin's feeding added to the daughter
    in bin order (`np.add.accumulate`, the same left-to-right sums), the mother bins' `xspopex`
    reduced exit by exit, and the records written as whole rows. False if it does not apply.
    A fissioning nucleus's `fisfeed` (FISSB) comes out of each bin after its particle exits, in
    bin order, as the loop below takes it."""
    first = pending[0][1].dpop_mb
    nw = getattr(first, "nw", None)
    if nw is None or any(getattr(f.dpop_mb, "nw", None) is not nw for _, f in pending):
        return False
    nexs = [x for x, _ in pending]
    batch = nw.particle_batch(nexs)
    if batch is None:
        return False
    rows = np.asarray(nexs)
    for t in range(1, 7):
        if t not in dviews or t not in batch:
            continue
        d, DX, DXE = dviews[t]
        v = batch[t]
        record = _records_feedexcl(zc, nc, t)
        part = xspartial.setdefault(t, {})
        if v is None:  # closed: every tot is 0.0
            for x in nexs:
                part[x] = part.get(x, 0.0) + 0.0
            d.xspopnuc_mb += 0.0
            xsfeed[t] = xsfeed.get(t, 0.0) + 0.0
            if record:
                _table(feedexcl, t, nuc.maxex + 2, DX.shape[0])
            continue
        dp, mc, nrows = v
        n = min(dp.shape[1], DX.shape[0])
        jx = dp.shape[2]
        # a bin's rows past its own nexmax are zero in the batch: adding them changes nothing
        DX[:n, :jx] = np.add.accumulate(np.concatenate([DX[None, :n, :jx], dp[:, :n]]), 0)[-1]
        sumip = mc[:, :n]
        DXE[:n] = np.add.accumulate(np.concatenate([DXE[None, :n], sumip]), 0)[-1]
        tots = [float(sumip[b, : min(int(nrows[b]), n)].sum()) for b in range(len(nexs))]
        XE[rows] -= np.asarray(tots)
        acc_nuc = d.xspopnuc_mb
        acc_feed = xsfeed.get(t, 0.0)
        for x, tot in zip(nexs, tots):  # noqa: B905
            acc_nuc += tot
            part[x] = part.get(x, 0.0) + tot
            acc_feed += tot
        d.xspopnuc_mb = acc_nuc
        xsfeed[t] = acc_feed
        if record:
            fe = _table(feedexcl, t, nuc.maxex + 2, DX.shape[0])
            nz = sumip != 0.0
            fe.val[rows, :n] = np.where(nz, sumip, fe.val[rows, :n])
            fe.present[rows, :n] |= nz
    for x, f in pending:
        if f.fisfeed_mb:
            fisfeed[x] = fisfeed.get(x, 0.0) + f.fisfeed_mb
            xsfeed[-1] = xsfeed.get(-1, 0.0) + f.fisfeed_mb
            XE[x] -= f.fisfeed_mb
    return True


class _GraphFeeding(Exception):
    """A decay callback returned tensors on a graph: `multiple_emission` uses its tensor loop."""


def _carries_graph(feeding: BinFeeding) -> bool:
    if not isinstance(feeding.dpop_mb, dict):
        return False
    return any(isinstance(v, torch.Tensor) and v.requires_grad
               for m in (feeding.dpop_mb, feeding.mcontrib_mb) for v in m.values())


def _apply_numpy(nuc, XE, dview, t: int, nex: int, dp, sumip, xsfeed: dict, xspartial: dict,
                 feedexcl: dict, record: bool) -> None:
    """One exit of one mother bin into its daughter: the tensor loop's body, on numpy views.
    `dp is None` is a closed exit (all zeros): only the records are touched."""
    d, DX, DXE = dview
    if dp is None:
        tot = 0.0
    else:
        n = min(dp.shape[0], DX.shape[0])
        if isinstance(dp, torch.Tensor):  # decay_batch's path: the same sum, on the tensor
            tot = float(sumip[:n].sum())
            dp, sumip = dp.numpy(), sumip.numpy()
        else:
            tot = None
        DX[:n, : dp.shape[1]] += dp[:n]
        sumip = sumip[:n]
        DXE[:n] += sumip
        if tot is None:
            tot = float(sumip.sum())
        XE[nex] -= tot
    d.xspopnuc_mb += tot
    part = xspartial.setdefault(t, {})
    part[nex] = part.get(nex, 0.0) + tot
    xsfeed[t] = xsfeed.get(t, 0.0) + tot
    if not record:
        return
    fe = _table(feedexcl, t, nuc.maxex + 2, DX.shape[0])
    if dp is None:
        return
    # each (nex, nexout) is fed once without multiple pre-equilibrium: 0.0 + v == v
    fe.set_row_nonzero(nex, sumip)


def _apply_leftover(nuc: NucleusPopulation, nex: int, leftover_mb: float, fe,
                    xspartial: dict, xe) -> None:
    """compound.f90:404-419: the flux of a mother cell with no open exit, spread equally over the
    mother nucleus's OWN discrete levels.

    `compound` does this in iloop 1, where it sets `feed = 0` for that cell, so iloop 2 adds
    nothing for it: the leftover reaches `xspopex(Zcomp, Ncomp, nexout)`, `xspop` and
    `mcontrib(0, nex, nexout)` -- and through `mcontrib`, `feedexcl` and the exclusive channels --
    but NOT `xsfeed`, NOT `xspopnuc`, and it is NOT taken out of the mother's own `xspopex(nex)`.
    `xspop` already has it (the decay put it in `dpop[0]`); this adds the other three.

    Dropping it cost the whole trapped bin out of the exclusive channels: Eu-147 `(n,g)` was
    0.734x TALYS from 1 keV to 1.5 MeV because 990 mb of the 3042 mb Eu-148 population sat in one
    trapped bin (CHARTFIX defect 3).

    TALYS: compound.f90:1 (compound)
    Test: tests/hf/test_trapped_leftover.py / E2E
    """
    nl = nuc.nlast
    if nl < 0 or leftover_mb == 0.0:
        return
    share = leftover_mb / (nl + 1.0)
    for nexout in range(min(nl, int(xe.shape[0]) - 1) + 1):
        xe[nexout] += share
        if fe is not None:
            fe[(nex, nexout)] = fe.get((nex, nexout), 0.0) + share
    part = xspartial.setdefault(0, {})
    part[nex] = part.get(nex, 0.0) + leftover_mb


def _table(feedexcl: dict, t: int, nrows: int, ncols: int) -> FeedTable:
    fe = feedexcl.get(t)
    if fe is None:
        fe = feedexcl[t] = FeedTable(nrows, ncols)
    return fe


def _apply_mpe(nuc: NucleusPopulation, daughters: dict, nex: int, m: "MpeFeeding",
               feedexcl: dict, xspartial: dict, xsfeed: dict, zc: int, nc: int) -> None:
    """multipreeq2.f90:246-296: move the mother bin's multiple-pre-equilibrium flux to the two
    nucleon daughters, and record it the way a compound decay would be.

    `mcontrib` is where it lands, and multiple.f90:681 copies `mcontrib` into `feedexcl`, so the
    flux is inside the exclusive channels rather than beside them. `xspopex` of the mother is
    reduced by `summpe` at :375 -- but `popexcl` was snapshotted at :498, before this ran.

    TALYS: multipreeq2.f90:1 (multipreeq2)
    Test: A-mpe / E2E
    """
    if m.ph_mother_mb is not None:
        nuc.xspopph2_mb[nex] = m.ph_mother_mb
    for t, term in m.term_mb.items():
        d = daughters.get(t)
        if d is None:
            continue
        n = min(term.shape[0], d.xspop_mb.shape[0])
        d.xspopex_mb[:n] += term[:n]
        d.xspop_mb[:n, :, 0] += m.xspop_add_mb[t][:n]
        d.xspop_mb[:n, :, 1] += m.xspop_add_mb[t][:n]
        tot = m.sumtype_mb.get(t, 0.0)
        d.xspopnuc_mb += tot
        xspartial.setdefault(t, {})[nex] = xspartial.setdefault(t, {}).get(nex, 0.0) + tot
        xsfeed[t] = xsfeed.get(t, 0.0) + tot
        if tot != 0.0:
            d.mulpre = True
        if _records_feedexcl(zc, nc, t):
            fe = feedexcl.setdefault(t, {})
            # SPEEDW: the nonzero bins of a detached row read through numpy -- the same float64
            # values in the same order as `float(term[nexout])` one element at a time
            tn = _np_row(term, n)
            if tn is None:
                for nexout in range(n):
                    v = float(term[nexout])
                    if v != 0.0:
                        fe[(nex, nexout)] = fe.get((nex, nexout), 0.0) + v
            else:
                for nexout in np.flatnonzero(tn).tolist():
                    v = float(tn[nexout])
                    fe[(nex, nexout)] = fe.get((nex, nexout), 0.0) + v
    for (t, ipp, ihp, ipn, ihn), col in m.ph_add.items():
        d = daughters.get(t)
        if d is None:
            continue
        n = min(col.shape[0], d.xspop_mb.shape[0])
        cn = _np_row(col, n)
        if cn is not None:
            for nexout in np.flatnonzero(cn).tolist():
                cur = d.xspopph2_mb.get(nexout)
                if cur is None:
                    p = m.ph_mother_mb.shape[0] - 1 if m.ph_mother_mb is not None else 6
                    cur = torch.zeros(p + 1, p + 1, p + 1, p + 1, dtype=DTYPE)
                    d.xspopph2_mb[nexout] = cur
                if cur.requires_grad:
                    cur[ipp, ihp, ipn, ihn] = cur[ipp, ihp, ipn, ihn] + float(cn[nexout])
                else:
                    a = cur.numpy()
                    a[ipp, ihp, ipn, ihn] = a[ipp, ihp, ipn, ihn] + cn[nexout]
            continue
        for nexout in range(n):
            v = col[nexout]
            if float(v) == 0.0:
                continue
            cur = d.xspopph2_mb.get(nexout)
            if cur is None:
                p = m.ph_mother_mb.shape[0] - 1 if m.ph_mother_mb is not None else 6
                cur = torch.zeros(p + 1, p + 1, p + 1, p + 1, dtype=DTYPE)
                d.xspopph2_mb[nexout] = cur
            cur[ipp, ihp, ipn, ihn] = cur[ipp, ihp, ipn, ihn] + v
    nuc.xspopex_mb[nex] -= m.summpe_mb


def _np_row(x, n: int):
    """`x[:n]` as a float64 numpy array when that reads the same values (a CPU tensor off the
    autograd graph, or an array already); None otherwise, and the caller walks the tensor."""
    if isinstance(x, np.ndarray):
        return x[:n] if x.dtype == np.float64 else None
    if isinstance(x, torch.Tensor) and x.dtype == torch.float64 and x.device.type == "cpu" \
            and not x.requires_grad:
        return x[:n].numpy()
    return None


def _binary_feed(res, key, zc, nc, k0, xsreacinc_mb, xsbinary_mb, feedbinary_mb, nuc, flagfission):
    """multiple.f90:936-961: the binary step is the initial compound nucleus's own `nex = maxex+1`
    row, so exclusive channels see the first emission the same way as every later one."""
    if (zc, nc) != (0, 0):
        return
    xsfeed = res.xsfeed_mb[key]
    # `dict.fromkeys`, not `list(xsfeed) + [-1]`: multiple.f90:936-961 adds `xsbinary(type)` to
    # `xsfeed(0,0,type)` ONCE per type, and `-1` is already a key of `xsfeed` whenever the
    # compound nucleus's own bins have fissioned -- which is every actinide as soon as
    # `engine.ChainedFull` passes a fission transmission (TWOPH). The duplicate cost U-238's
    # (n,f) exactly one extra first-chance term, +10% at 14 MeV; it was invisible before because
    # the injected arm reads `xsfeed` out of the dump and never calls this, and the chained arm
    # ran with `flagfission=False`.
    for t in dict.fromkeys(list(xsfeed) + [-1]):
        xsfeed[t] = xsfeed.get(t, 0.0) + xsbinary_mb.get(t, 0.0)
    for t, v in xsbinary_mb.items():
        if t not in xsfeed:
            xsfeed[t] = v
    top = nuc.maxex + 1
    res.popexcl_mb[key][top] = xsreacinc_mb
    if flagfission:
        res.fisfeedex_mb[key][top] = xsbinary_mb.get(-1, 0.0)
    if feedbinary_mb:
        for t, arr in feedbinary_mb.items():
            fe = res.feedexcl_mb[key].setdefault(t, {})
            for nexout in range(arr.shape[0]):
                v = float(arr[nexout])
                if v != 0.0:
                    fe[(top, nexout)] = v
