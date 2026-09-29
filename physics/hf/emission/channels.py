"""Exclusive channel cross sections, per-level partials, totals and residual production
(channels.f90, totalxs.f90, residual.f90).

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T10 (physics/hf/CONTRACT.md §7). Acceptance test: A-mult (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    channels.f90:1 (channels)
    totalxs.f90:1 (totalxs)
    residual.f90:1 (residual)

channels.f90 is exclusive-flux bookkeeping, not physics: it walks every reachable exit channel
in TALYS's own order and propagates the inclusive cross section per excitation energy `xsexcl`
down the decay chain with the ratio `feedexcl / popexcl`. It is a chain of scalar recurrences
over (channel, bin), so the vectorised axis is the excitation bin, and the loops over channel
and over mother bin stay loops (CONTRACT §1, "loops inherent to the physics").

Quirks this reproduces, each of which changes a number:
* The six particle loops are nested h, t, d, a, p, n and the channel index `idnum` is assigned
  in exactly that order; a channel whose cross section falls below `xseps` gives its index BACK
  (channels.f90:634), so the index is a function of the whole energy history, not of the code.
* `chanopen` and `idnumfull` persist across incident energies (`strucinitial`), so a channel that
  opened at 20 MeV is still evaluated at 1 keV on the next run of the energy loop.
* For gamma emission the "previous channel" is the channel itself (identorg(0) == idnum), which
  is what makes the downward `nexout` loop accumulate the gamma cascade.
* `xsexcl` is divided by `popexcl`, the population of the mother bin BEFORE it decayed, which
  multiple.f90 stores separately from `xspopex` precisely because the gamma cascade mutates the
  latter while the bin is being emptied.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache

import numpy as np
from scipy.linalg import solve_triangular

from physics.hf.emission.dumps import ChannelInputs
from physics.hf.emission.feed_table import dense_feed

PARZ = (0, 0, 1, 1, 1, 2, 2)  # constants.f90: parZ, types 0..6 = g n p d t h a
PARN = (0, 1, 0, 1, 2, 1, 2)  # constants.f90: parN
NUMZCHAN, NUMNCHAN = 6, 10  # A0_talys_mod.f90: numZchan, numNchan
NUMIN, NUMIP, NUMID, NUMIT, NUMIH, NUMIA = 8, 4, 2, 1, 1, 3
NUMCHANTOT = 35 * 7  # A0_talys_mod.f90:92, memorypar = 8 at the default `memory` setting


@dataclass
class ExclusiveState:
    """`chanopen` / `idnumfull` / `opennum`, which channels.f90 carries across incident energies."""

    chanopen: set[tuple[int, int, int, int, int, int]] = field(default_factory=set)
    idnumfull: bool = False

    @property
    def opennum(self) -> int:
        return len(self.chanopen)


@dataclass(frozen=True)
class ChannelResult:
    """Exclusive channels and everything derived from them, all mb."""

    idchannel: list[int]  # idnum -> the six-digit channel code
    xschannel_mb: dict[int, float]  # channel code -> xs*.tot
    xsgamchannel_mb: dict[int, float]
    xsfischannel_mb: dict[int, float]
    xschaniso_mb: dict[int, dict[int, float]]  # code -> level -> isomeric/ground xs
    exclbranch: dict[int, dict[int, float]]
    qexcl_mev: dict[int, float]
    channelsum_mb: float
    xsabs_mb: float
    xsexclusive_mb: dict[int, float]  # type -> the (n,x) exclusive total
    xsexclcont_mb: dict[int, float]
    xsparticle_mb: dict[int, float]  # type -> nn.tot / np.tot / ...
    multiplicity: dict[int, float]
    xsfistot_mb: float
    residual_mb: dict[tuple[int, int], float]  # (Z, A) -> rpZZZAAA.tot
    xsbranch: dict[tuple[int, int], dict[int, float]]
    xsresprod_mb: float


def _limits(zix: int, nix: int, parinclude: list[bool], maxchannel: int) -> tuple[int, ...]:
    """channels.f90:204-225: the largest number of each ejectile that can reach (Zix, Nix)."""
    aix = zix + nix
    lim = [0] * 6
    if aix != 0:
        cand = (min(nix, maxchannel), min(zix, maxchannel), min(2 * zix * nix // aix, maxchannel),
                min(3 * zix * nix // (2 * aix), maxchannel),
                min(3 * zix * nix // (2 * aix), maxchannel), min(zix * nix // aix, maxchannel))
        for i, c in enumerate(cand):
            if parinclude[i + 2]:  # parinclude index 0 is type -1
                lim[i] = c
    caps = (NUMIN, NUMIP, NUMID, NUMIT, NUMIH, NUMIA)
    return tuple(min(a, b) for a, b in zip(lim, caps))  # noqa: B905 (py3.9 boxes)


@lru_cache(maxsize=4096)
def _limits_of(zix: int, nix: int, parinclude: tuple, maxchannel: int) -> tuple[int, ...]:
    """NATIVEX: `_limits`, memoised (a pure function of its arguments)."""
    return _limits(zix, nix, list(parinclude), maxchannel)


@lru_cache(maxsize=4096)
def _channel_keys(zix: int, nix: int, lim: tuple[int, ...], maxchannel: int) -> tuple:
    """(i_n, ip, id, it, ih, ia) in channels.f90's loop order with ztot == Zix, ntot == Nix and
    at most `maxchannel` particles: for fixed (h, t, d, a) the proton and neutron counts are
    determined, so the two inner loops hold at most one survivor."""
    inend, ipend, idend, itend, ihend, iaend = lim
    out = []
    for ih in range(ihend + 1):
        for it in range(itend + 1):
            for idd_ in range(idend + 1):
                for ia in range(iaend + 1):
                    ip = zix - idd_ - it - 2 * ih - 2 * ia
                    i_n = nix - idd_ - 2 * it - ih - 2 * ia
                    if not (0 <= ip <= ipend and 0 <= i_n <= inend):
                        continue
                    if i_n + ip + idd_ + it + ih + ia > maxchannel:
                        continue
                    out.append((i_n, ip, idd_, it, ih, ia))
    return tuple(out)


class _SourceTables:
    """Per (mother nucleus, ejectile): the binary row `feedexcl(top0, nexout)` of the initial
    compound nucleus, and `feedexcl(nex, nexout) / popexcl(nex)` for nex = 1..maxex(mother)
    with 0 wherever either is 0 (channels.f90:370-383), cut to the daughter's `nr` bins."""

    def __init__(self, nuc: dict, top0: int):
        self.nuc, self.top0, self.cache = nuc, top0, {}

    def of(self, zc: int, nc: int, t: int, nr: int):
        key = (zc, nc, t, nr)
        got = self.cache.get(key)
        if got is None:
            mother = self.nuc[(zc, nc)]
            feed = mother.feedexcl_mb.get(t)
            top = ratio = None
            if feed:
                mx = mother.maxex
                F = dense_feed(feed, max(mx + 1, self.top0 + 1) if (zc, nc) == (0, 0) else mx + 1,
                               nr)
                if (zc, nc) == (0, 0):
                    top = F[self.top0]
                    if not top.any():
                        top = None
                if mx >= 1:
                    pop = np.array([mother.popexcl_mb.get(nex, 0.0) for nex in range(1, mx + 1)])
                    f = F[1 : mx + 1]
                    ok = (f != 0.0) & (pop != 0.0)[:, None]
                    if ok.any():
                        ratio = np.where(ok, f / np.where(pop != 0.0, pop, 1.0)[:, None], 0.0)
            got = self.cache[key] = (top, ratio)
        return got

    def gamma_system(self, zix: int, nix: int, ug: np.ndarray, nr: int) -> np.ndarray:
        """I - U with U[nexout, nex] = feedexcl(0, nex, nexout) / popexcl(nex) for nex > nexout:
        the photon source's recurrence, walked from the top bin down (channels.f90:330,
        `nexout = maxex, 0, -1`), as one unit upper triangular system."""
        key = ("g", zix, nix, nr)
        got = self.cache.get(key)
        if got is None:
            k = min(ug.shape[0], nr - 1)  # mother bins 1..k feed the bins below them
            U = np.zeros((nr, nr))
            U[:, 1 : k + 1] = ug[:k, :nr].T
            U = np.triu(U, 1)
            got = self.cache[key] = (np.eye(nr) - U, U)
        return got




def exclusive_channels(inp: ChannelInputs, state: ExclusiveState | None = None) -> ChannelResult:
    """xsNNNNNN.tot, `.Lnn` isomeric branches, rp*.tot and the particle production totals [mb].

    `state` carries `chanopen`/`idnumfull` from the previous incident energy; pass the same object
    through an ascending energy loop, as TALYS does. With `state=None` the dump's own `chanopen`
    set is used, which is what the injected gate wants.

    TALYS: channels.f90:1 (channels), totalxs.f90:1 (totalxs), residual.f90:1 (residual)
    Test: A-mult
    """
    from physics.hf.emission import emit_nx2

    fast = emit_nx2.exclusive_channels(inp, state)  # NATIVEX2: the same body, less re-reading
    if fast is not None:
        return fast
    st = state if state is not None else ExclusiveState(set(inp.chanopen), inp.idnumfull)
    nuc = inp.nuclei
    xseps = inp.xseps_mb
    root = nuc[(0, 0)]

    # xsexcl / gamexcl per channel index: {nexout -> mb}. Index maxex(0,0)+1 is the initial
    # compound state, which holds all of the flux before any emission (channels.f90:176-181).
    # xsexcl / gamexcl per channel index, over the channel nucleus's bins 0..maxex
    xsexcl: dict[int, np.ndarray] = {}
    gamexcl: dict[int, np.ndarray] = {}
    idchannel: dict[int, int] = {}
    xschannel: dict[int, float] = {}
    xsgamchannel: dict[int, float] = {}
    xsfischannel: dict[int, float] = {}
    xschaniso: dict[int, dict[int, float]] = {}
    qexcl: dict[int, dict[int, float]] = {}
    npart_of: dict[int, int] = {}
    in_of: dict[int, int] = {}
    top0 = root.maxex + 1
    slots: dict[int, list[int]] = {}
    tables = _SourceTables(nuc, top0)

    channelsum = 0.0
    xsabs = 0.0
    idnum = -1
    zend = min(NUMZCHAN, inp.maxz, inp.zinit)
    nend = min(NUMNCHAN, inp.maxn, inp.ninit)
    for zix in range(zend + 1):
        for nix in range(nend + 1):
            if (zix, nix) not in nuc:
                continue
            res = nuc[(zix, nix)]
            inend, ipend, idend, itend, ihend, iaend = _limits_of(
                zix, nix, tuple(inp.parinclude), inp.maxchannel)
            # the six particle loops, nested h, t, d, a, p, n, keep only the tuples that reach
            # (Zix, Nix); the others fall through every test below without a side effect
            for key in _channel_keys(zix, nix, (inend, ipend, idend, itend, ihend, iaend),
                                     inp.maxchannel):
                    i_n, ip, idd_, it, ih, ia = key
                    if key not in st.chanopen and st.idnumfull:
                        continue
                    if idnum == NUMCHANTOT:
                        continue
                    npart = i_n + ip + idd_ + it + ih + ia
                    ident = (100000 * i_n + 10000 * ip + 1000 * idd_ + 100 * it + 10 * ih + ia)
                    idnum += 1
                    idchannel[idnum] = ident
                    slots.setdefault(ident, []).append(idnum)
                    xschannel[idnum] = 0.0
                    xsgamchannel[idnum] = 0.0
                    xsfischannel[idnum] = 0.0
                    xschaniso[idnum] = {}
                    npart_of[idnum], in_of[idnum] = npart, i_n
                    q = {0: 0.0}
                    qexcl[idnum] = q
                    # Qexcl(0, 0) is re-assigned inside the loop at every idnum (channels.f90:256)
                    qexcl.setdefault(0, {})[0] = root.sep_mev.get(inp.k0, 0.0) + inp.targete_mev
                    if idnum == 0:
                        q[0] = qexcl[0][0]

                    # --- source paths (channels.f90:283-318) --------------------------------
                    identorg: dict[int, int] = {}
                    for t in range(7):
                        if inp.parskip[t]:
                            continue
                        idd = ident if t == 0 else ident - 10 ** (6 - t)
                        if idd < 0:
                            continue
                        # the last idorg <= idnum whose channel is idd (an index given back is
                        # reassigned, so the candidate must still hold idd)
                        for idorg in reversed(slots.get(idd, ())):
                            if idorg <= idnum and idchannel.get(idorg) == idd:
                                break
                        else:
                            continue
                        identorg[t] = idorg
                        zc, nc = zix - PARZ[t], nix - PARN[t]
                        if q[0] == 0.0 and (zc, nc) in nuc:
                            q[0] = qexcl[idorg][0] - nuc[(zc, nc)].sep_mev.get(t, 0.0)
                        # channels.f90 fills Qexcl(idnum, nex) for every discrete level; only
                        # nex = 0 is ever read, and it is re-formed at nex = 0 of that loop
                        if min(res.nlast, len(res.edis_mev) - 1) >= 0:
                            q[0] = q[0] - res.edis_mev.get(0, 0.0)

                    if inp.flagfission and zix == 0 and nix == 0:
                        xsfischannel[idnum] += root.fisfeedex_mb.get(top0, 0.0)

                    # --- exclusive cross section per excitation energy (channels.f90:330-391) -
                    # xsexcl(idnum, nexout) = sum over sources of feedexcl / popexcl times the
                    # source channel's xsexcl at the mother bin. The photon source is this
                    # channel itself one bin higher, so that part is a back substitution down
                    # the (strictly upper triangular) gamma-feeding matrix.
                    nr = res.maxex + 1
                    xe = np.zeros(nr)
                    ge = np.zeros(nr)
                    ug = None
                    for t in range(7):
                        if inp.parskip[t] or t not in identorg:
                            continue
                        zc, nc = zix - PARZ[t], nix - PARN[t]
                        if (zc, nc) not in nuc:
                            continue
                        top, ratio = tables.of(zc, nc, t, nr)
                        if top is not None:
                            xe += top
                            if t == 0:
                                ge += top
                        if ratio is None:
                            continue
                        if t == 0:
                            ug = ratio  # (nex, nexout), nex = 1..maxex(mother) = res
                            continue
                        idorg = identorg[t]
                        xe += xsexcl[idorg][1 : ratio.shape[0] + 1] @ ratio
                        ge += gamexcl[idorg][1 : ratio.shape[0] + 1] @ ratio
                    if ug is not None:
                        A, U = tables.gamma_system(zix, nix, ug, nr)
                        xe = solve_triangular(A, xe, lower=False, unit_diagonal=True,
                                              check_finite=False)
                        # gamexcl: the photon term is xsexcl's own (term2) plus gamexcl's
                        ge = solve_triangular(A, ge + U @ xe, lower=False, unit_diagonal=True,
                                              check_finite=False)
                    xsexcl[idnum], gamexcl[idnum] = xe, ge
                    # --- total and per isomer (channels.f90:398-425) -------------------------
                    for nexout in range(min(res.maxex, res.nlast), -1, -1):
                        if res.tau_s.get(nexout, 0.0) != 0.0 or nexout == 0:
                            xschaniso[idnum][nexout] = float(xe[nexout])
                            xschannel[idnum] += float(xe[nexout])
                            xsgamchannel[idnum] += float(ge[nexout])

                    channelsum += xschannel[idnum]
                    if i_n == 0:
                        xsabs += xschannel[idnum]

                    # non-threshold floor (channels.f90:435-445)
                    if q[0] > 0.0 and xschannel[idnum] <= xseps:
                        xschannel[idnum] = xseps
                        xsgamchannel[idnum] = xseps
                        xschaniso[idnum][0] = xseps
                        for i in range(1, res.nlast + 1):
                            if res.tau_s.get(i, 0.0) != 0.0:
                                xschaniso[idnum][0] = 0.5 * xseps
                                xschaniso[idnum][i] = 0.5 * xseps

                    # exclusive fission (channels.f90:459-475)
                    if inp.flagfission:
                        for nex in range(res.maxex, 0, -1):
                            pop = res.popexcl_mb.get(nex, 0.0)
                            if pop != 0.0:
                                term = res.fisfeedex_mb.get(nex, 0.0) / pop
                                xsfischannel[idnum] += term * float(xe[nex])
                        channelsum += xsfischannel[idnum]
                        xsabs += xsfischannel[idnum]

                    # --- idnum give-back (channels.f90:630-637) -----------------------------
                    if (xschannel[idnum] >= xseps and not st.idnumfull) or npart == 0:
                        st.chanopen.add(key)
                    if xschannel[idnum] < xseps and npart > 1 and key not in st.chanopen:
                        idnum -= 1
                    if st.opennum == NUMCHANTOT - 10:
                        st.idnumfull = True
                    if idnum < 0:
                        continue
                    if xschannel[idnum] < 0.0:
                        xschannel[idnum] = xseps

    return _channel_result(inp, nuc, xseps, idnum, idchannel, xschannel, xsgamchannel,
                           xsfischannel, xschaniso, qexcl, channelsum, xsabs)


def _channel_result(inp, nuc, xseps, idnum, idchannel, xschannel, xsgamchannel, xsfischannel,
                    xschaniso, qexcl, channelsum, xsabs) -> ChannelResult:
    """The channels up to `idnum`, `totalxs.f90` and `residual.f90` (the tail of
    `exclusive_channels`, shared with `emission.emit_nx2.exclusive_channels`)."""
    live = list(range(idnum + 1))
    codes = {i: idchannel[i] for i in live}
    xsch = {codes[i]: xschannel[i] for i in live}
    xsgam = {codes[i]: xsgamchannel[i] for i in live}
    xsfis = {codes[i]: xsfischannel[i] for i in live}
    iso = {codes[i]: xschaniso[i] for i in live}
    branch = {codes[i]: ({k: v / xschannel[i] for k, v in xschaniso[i].items()}
                         if xschannel[i] != 0.0 else {}) for i in live}

    # --- totalxs.f90 --------------------------------------------------------------------------
    xsexclusive, xsexclcont = {}, {}
    for t in range(7):
        if inp.parskip[t]:
            continue
        code = 0 if t == 0 else 10 ** (6 - t)
        xsexclusive[t] = xsch.get(code, 0.0)
    xsparticle, mult = {}, {}
    # NATIVEX: only the nuclei with feeding records (an empty record adds exactly 0.0)
    fed = [n.xsfeed_mb for n in nuc.values() if n.xsfeed_mb]
    for t in range(7):
        if inp.parskip[t]:
            continue
        s = sum(f.get(t, 0.0) for f in fed)
        xsparticle[t] = s
        mult[t] = s / inp.xsnonel_mb if inp.xsnonel_mb != 0 else 0.0
    xsfistot = sum(f.get(-1, 0.0) for f in fed) if inp.flagfission else 0.0

    # --- residual.f90 -------------------------------------------------------------------------
    residual_mb, xsbranch = {}, {}
    xsresprod = 0.0
    for (zc, nc), n in nuc.items():
        pop = n.xspopnuc_mb
        if pop != 0.0:
            xsresprod += pop
            xsbranch[(n.Z, n.A)] = {
                nex: n.xspopex_mb.get(nex, 0.0) / pop
                for nex in range(n.nlast + 1)
                if nex == 0 or n.tau_s.get(nex, 0.0) != 0.0
            }
        if n.qres_mev > 0.0 and pop <= xseps:
            pop = xseps
        residual_mb[(n.Z, n.A)] = pop

    return ChannelResult(
        idchannel=[idchannel[i] for i in live], xschannel_mb=xsch, xsgamchannel_mb=xsgam,
        xsfischannel_mb=xsfis, xschaniso_mb=iso, exclbranch=branch,
        qexcl_mev={codes[i]: qexcl[i][0] for i in live}, channelsum_mb=channelsum, xsabs_mb=xsabs,
        xsexclusive_mb=xsexclusive, xsexclcont_mb=xsexclcont, xsparticle_mb=xsparticle,
        multiplicity=mult, xsfistot_mb=xsfistot, residual_mb=residual_mb, xsbranch=xsbranch,
        xsresprod_mb=xsresprod,
    )
