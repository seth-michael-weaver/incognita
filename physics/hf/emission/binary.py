"""Binary reaction bookkeeping: direct + pre-equilibrium + compound feeding of the first residual
nuclei, binary emission spectra.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T10 (physics/hf/CONTRACT.md §7). Acceptance test: A-mult (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    binary.f90:1 (binary)
    spindis.f90:1 (spindis)

CONTRACT §5 deviation, for the record (same shape as T9's): `binary` takes one bundled
`BinaryInputs` rather than `(CaseBatch, BinaryPopulation, preeq, direct, Options)`. binary.f90
reads twenty-odd module globals that belong to five different owners, and the honest interface
is the bundle; `from_compound` builds it from T9's `BinaryPopulation` plus the grids, so nothing
downstream changes when the addends come from ported T8/T12 instead of the dumps.

What binary.f90 does, and the quirks this reproduces:
* The direct addend goes into ONE (J, parity) cell of a discrete level -- `int(jdis)` truncates
  the level spin, so a 2.5 level feeds J index 2 (binary.f90:200-203).
* The pre-equilibrium addend is spread over spin with `sfactor`, the compound population's own
  normalised (J, parity) shape, but only where the compound bin holds more than
  `popeps / max(5*maxex, 1)`. Where it does not -- ~14% of the live cells above 5 MeV, T9's
  `ungated_cells` -- binary.f90:236 falls back to `spindis(sc, J) * pardis`, the Wigner
  distribution at the bin's own spin cutoff. That fallback is why this module needs T6's
  `ignatyuk`/`spincut`.
* `xspopex0` is filled for the discrete levels BEFORE the pre-equilibrium loop, so the `.Lnn`
  files carry no continuum feeding, only direct + compound discrete.
* **`sfactor` is run-scoped, not energy-scoped.** `strucinitial.f90:484` zeroes it once per run,
  and binary.f90 only overwrites a bin's entry when that bin holds enough flux, so a bin that
  falls below the cut at a high incident energy keeps the spin shape computed at a LOWER one --
  at a different excitation energy, because the bins are re-gridded per energy. `BinaryState`
  carries that array; without it the gamma channel's high-energy continuum takes the Wigner
  fallback where TALYS does not (Nb-93 at 20 MeV: 6x on the smallest cells).
* Compound elastic is removed from the target's own level LAST (binary.f90:496-499), after
  `feedbinary` has been set to zero there, so `xspopnuc` still contains it.

Deliberately not ported: `normalization.f90:425-445` rescales `xsdirdisc`, `xsdirdisctot`,
`xsdircont` and `xsdirect` by the rescue-file ratio for MT 4 and 103-107. That is the
fitting/rescue path, which CONTRACT §8 puts out of scope, and it is off unless the user supplies a
rescue file; T12's direct outputs are the pre-normalisation values TALYS holds at binary.f90.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import torch
from torch import Tensor

from physics.hf.core.tensors import DTYPE

NUMJ = 40  # A0_talys_mod.f90:  numJ = 40
NUMEX = 80  # A0_talys_mod.f90:67, numex = numlev + numbins
MAXJPH = 30  # preeqinit.f90: maxJph, the pre-equilibrium spin ceiling
PARDIS = 0.5  # constants.f90:158


def _pi(parity: int) -> int:
    """Index of TALYS's parity -1/+1 on the contract's (-1, +1) axis."""
    return 0 if parity == -1 else 1


@dataclass(frozen=True)
class ResidualGrid:
    """Excitation-energy grid and level data of one binary residual nucleus (one ejectile)."""

    type: int
    zix: int
    nix: int
    maxex: int
    nlast: int
    ex_mev: Tensor  # (Nex,)
    dex_mev: Tensor  # (Nex,)
    maxj: Tensor  # (Nex,) int, maxJ(Zix, Nix, nex)
    parlev: Tensor  # (Nex,) int, discrete levels only
    jdis: Tensor  # (Nex,) float spin, discrete levels only
    ald: Tensor  # (Nex,) ignatyuk(Zix, Nix, Ex, 0); continuum bins only
    spincut: Tensor  # (Nex,) spincut(Zix, Nix, ald, Ex, 0, 0); continuum bins only


@dataclass
class BinaryState:
    """The one binary.f90 array that lives longer than an incident energy (strucinitial.f90:484).

    Pass the same object through an ascending energy loop, as TALYS does.
    """

    sfactor: dict[tuple[int, int], Tensor] = field(default_factory=dict)

    def get(self, zix: int, nix: int, numj: int, device=None) -> Tensor:
        key = (zix, nix)
        if key not in self.sfactor:
            self.sfactor[key] = torch.zeros((NUMEX + 1, numj + 1, 2), dtype=DTYPE, device=device)
        return self.sfactor[key]


@dataclass(frozen=True)
class BinaryInputs:
    """Everything binary.f90 reads, for one case (one target at one incident energy)."""

    e_inc_mev: float
    k0: int
    ltarget: int
    targetspin2: int
    target_parity: int
    pespinmodel: int
    maxjph: int
    numj: int
    popeps_mb: float
    xseps_mb: float
    xsreacinc_mb: float
    xselasinc_mb: float
    xsdirdiscsum_mb: float
    xspreeqsum_mb: float
    xsgrsum_mb: float
    xsracape_mb: float
    flagpreeq: bool
    grids: dict[int, ResidualGrid] = field(default_factory=dict)
    xspop_mb: dict[int, Tensor] = field(default_factory=dict)  # (Nex, numJ+1, 2), compound only
    xspopex_mb: dict[int, Tensor] = field(default_factory=dict)  # (Nex,), compound only
    xspopnuc_mb: dict[int, float] = field(default_factory=dict)  # compound only
    xsdirdisc_mb: dict[int, Tensor] = field(default_factory=dict)  # (Nex,)
    preeqpopex_mb: dict[int, Tensor] = field(default_factory=dict)  # (Nex,)
    xsdirdisctot_mb: dict[int, float] = field(default_factory=dict)
    xspreeqtot_mb: dict[int, float] = field(default_factory=dict)
    xsgrtot_mb: dict[int, float] = field(default_factory=dict)
    xscompcont_mb: dict[int, float] = field(default_factory=dict)
    xsbinary_mb: Tensor | None = None  # (8,) types -1..6, compound only
    # reference outputs carried by the same dump (not inputs; used only by tests)
    ref_xsdisc_mb: dict[int, Tensor] = field(default_factory=dict)


@dataclass(frozen=True)
class BinaryResult:
    """Populations and binary cross sections after binary.f90, all mb."""

    xspop_mb: dict[int, Tensor]  # (Nex, numJ+1, 2) per ejectile, compound elastic removed
    xspopex_mb: dict[int, Tensor]  # (Nex,)
    xspop_bine_mb: dict[int, Tensor]  # the same BEFORE the removal -- what binE*.out prints
    xspopex_bine_mb: dict[int, Tensor]
    xspopex0_mb: dict[int, Tensor]  # (NL+1,), discrete levels before the pre-equilibrium loop
    xspopnuc_mb: dict[int, Tensor]
    xspopdir_mb: dict[int, Tensor]
    preeqpopex_mb: dict[int, Tensor]  # after the target level has been zeroed
    xsdisc_mb: dict[int, Tensor]  # (NL+1,) -> the `.Lnn` files
    xsdirdisc_mb: dict[int, Tensor]  # (NL+1,)
    xscompdisc_mb: dict[int, Tensor]  # (NL+1,)
    feedbinary_mb: dict[int, Tensor]  # (Nex,)
    sfactor: dict[int, Tensor]  # (Nex, numJ+1, 2), the spin factor actually used
    xsdisctot_mb: Tensor  # (7,)
    xscompdisctot_mb: Tensor
    xsdircont_mb: Tensor
    xsdirect_mb: Tensor
    xsconttot_mb: Tensor
    xscompound_mb: Tensor
    xsbinary_mb: Tensor  # (8,) types -1..6
    xscompel_mb: Tensor
    xselastot_mb: Tensor
    xsnonel_mb: Tensor
    xscompnonel_mb: Tensor


def spindis(sc: Tensor, rspin: Tensor) -> Tensor:
    """Wigner spin distribution (2J+1)/(2 sigma^2) exp(-(J+1/2)^2 / (2 sigma^2)).

    TALYS: spindis.f90:1 (spindis)
    Test: A-mult
    """
    sigma22 = 2.0 * sc
    return (2.0 * rspin + 1.0) / sigma22 * torch.exp(-((rspin + 0.5) ** 2) / sigma22)


def bin_spin_cutoff(ld, ex_mev: Tensor) -> tuple[Tensor, Tensor]:
    """a(Ex) and the spin cutoff sigma^2(Ex) of the continuum bins, from T6's `LDNucleus`.

    This is binary.f90:229-230 -- the two lines that make the pre-equilibrium spin spread work
    where `sfactor` is zero. Split out so the engine can feed a ported level density in and the
    gate can feed TALYS's own dumped values in, with the same `binary` below.

    TALYS: ignatyuk.f90:1 (ignatyuk), spincut.f90:1 (spincut)
    Test: A-mult
    """
    from physics.hf.density.parameters import ignatyuk, spincut

    ald = ignatyuk(ld, ex_mev, 0)
    return ald, spincut(ld, ald, ex_mev, 0, 0)


def binary(inp: BinaryInputs, state: BinaryState | None = None, device=None) -> BinaryResult:
    """Populations of the first residual nuclei [mb] per bin/level, J, parity, and every binary
    cross section, compared with binE*.out and the `.Lnn` files.

    TALYS: binary.f90:1 (binary)
    Test: A-mult
    """
    from physics.hf.emission import emit_nx2

    fast = emit_nx2.binary(inp, state, device)  # NATIVEX2: off the graph, numpy + C per type
    if fast is not None:
        return fast
    types = sorted(inp.grids)
    st = state if state is not None else BinaryState()
    nj = inp.numj
    xspop, xspopex, xspopex0 = {}, {}, {}
    xspopnuc, xspopdir, sfac_out, preeqpopex = {}, {}, {}, {}
    xsdisc, xsdirdisc, xscompdisc, feedbinary = {}, {}, {}, {}
    z = torch.zeros((), dtype=DTYPE, device=device)
    xsdisctot = torch.zeros(7, dtype=DTYPE, device=device)
    xscompdisctot = torch.zeros(7, dtype=DTYPE, device=device)
    xsdircont = torch.zeros(7, dtype=DTYPE, device=device)
    xsdirect = torch.zeros(7, dtype=DTYPE, device=device)
    xsconttot = torch.zeros(7, dtype=DTYPE, device=device)
    xscompound = torch.zeros(7, dtype=DTYPE, device=device)
    xsbin = (inp.xsbinary_mb.clone() if inp.xsbinary_mb is not None
             else torch.zeros(8, dtype=DTYPE, device=device)).to(DTYPE)

    for t in types:
        g = inp.grids[t]
        nmax = g.maxex
        # Nlast can exceed maxex at low incident energy: the levels above the highest
        # attainable bin are simply closed, and TALYS's `do nex = 0, NL` reads zeros there.
        nl = min(g.nlast, nmax)
        pop = inp.xspop_mb[t].clone()
        pex = inp.xspopex_mb[t].clone()
        dd = inp.xsdirdisc_mb[t]
        nuc = torch.as_tensor(inp.xspopnuc_mb.get(t, 0.0), dtype=DTYPE, device=device)

        # --- direct discrete addend (binary.f90:194-216) -----------------------------------
        # One (J, parity) cell per level; J is int(jdis), the TRUNCATED level spin.
        lv = torch.arange(nl + 1, device=device)
        jidx = g.jdis[: nl + 1].to(torch.int64)  # int(jdis): truncation, not rounding
        pidx = torch.where(g.parlev[: nl + 1] == -1, 0, 1).to(torch.int64)
        term = dd[: nl + 1]
        live = term != 0.0
        pop.index_put_((lv[live], jidx[live], pidx[live]), term[live], accumulate=True)
        pex[: nl + 1] = pex[: nl + 1] + torch.where(live, term, z)
        x0 = pex[: nl + 1].clone()  # xspopex0, frozen before the pre-equilibrium loop

        ddtot = torch.as_tensor(inp.xsdirdisctot_mb.get(t, 0.0), dtype=DTYPE, device=device)
        xspopdir[t] = ddtot
        xsbin[t + 1] = xsbin[t + 1] + ddtot
        nuc = nuc + ddtot

        # --- pre-equilibrium addend (binary.f90:222-257) -----------------------------------
        sfglobal = st.get(g.zix, g.nix, nj, device)
        sfac = sfglobal[: nmax + 1].clone()
        ppx = inp.preeqpopex_mb[t].clone()
        if inp.flagpreeq:
            ncont = nmax - nl
            if ncont > 0 and inp.pespinmodel <= 2:
                popepsA = inp.popeps_mb / max(5 * nmax, 1)
                sl = slice(nl + 1, nmax + 1)
                mj = inp.maxjph + 1
                jj = torch.arange(mj, dtype=DTYPE, device=device)
                # sfactor is only overwritten where the bin holds enough flux; elsewhere TALYS
                # keeps whatever this bin index held at a PREVIOUS incident energy (zero on the
                # first), which is what selects the spindis fallback.
                has = (pex[sl] > popepsA)[:, None, None]
                new = torch.where(
                    has,
                    pop[sl, :mj, :]
                    / torch.where(pex[sl] > 0, pex[sl], torch.ones_like(pex[sl]))[:, None, None],
                    sfac[sl, :mj, :],
                )
                sfac[sl, :mj, :] = new
                sfglobal[nl + 1: nmax + 1, :mj, :] = new
                wig = spindis(g.spincut[sl][:, None], jj[None, :]) * PARDIS
                use_sf = (inp.pespinmodel == 1) & (new > 0.0)
                spread = torch.where(use_sf, new, wig[:, :, None])
                add = spread * ppx[sl][:, None, None]
                pop[sl, :mj, :] = pop[sl, :mj, :] + add
                pex[sl] = pex[sl] + ppx[sl]
            pt = torch.as_tensor(inp.xspreeqtot_mb.get(t, 0.0), dtype=DTYPE, device=device)
            gt = torch.as_tensor(inp.xsgrtot_mb.get(t, 0.0), dtype=DTYPE, device=device)
            nuc = nuc + pt + gt
            xsbin[t + 1] = xsbin[t + 1] + pt + gt

        # --- other total binary cross sections (binary.f90:263-313) ------------------------
        disc = x0.clone()
        if t == inp.k0 and inp.ltarget <= nl:
            disc[inp.ltarget] = z  # the target's own level is not a `.Lnn` channel
        cdisc = disc - dd[: nl + 1]
        if t == inp.k0 and inp.ltarget <= nl:
            cdisc[inp.ltarget] = z
        xscompdisctot[t] = cdisc.sum()
        xsdisctot[t] = ddtot + xscompdisctot[t]
        pt = torch.as_tensor(inp.xspreeqtot_mb.get(t, 0.0), dtype=DTYPE, device=device)
        gt = torch.as_tensor(inp.xsgrtot_mb.get(t, 0.0), dtype=DTYPE, device=device)
        cc = torch.as_tensor(inp.xscompcont_mb.get(t, 0.0), dtype=DTYPE, device=device)
        cc = torch.where(cc < inp.xseps_mb, z, cc)  # binary.f90:311
        xsdircont[t] = pt + gt
        xsdirect[t] = ddtot + xsdircont[t]
        xsconttot[t] = cc + xsdircont[t]
        xscompound[t] = xscompdisctot[t] + cc

        # --- binary feeding channels (binary.f90:329-340) ----------------------------------
        feed = pex.clone()
        xspop[t], xspopex[t], xspopex0[t] = pop, pex, x0
        xspopnuc[t], preeqpopex[t], sfac_out[t] = nuc, ppx, sfac
        xsdisc[t], xsdirdisc[t], xscompdisc[t] = disc, dd[: nl + 1], cdisc
        feedbinary[t] = feed

    # --- totals over the initial compound nucleus (binary.f90:317-326) ----------------------
    k0, lt = inp.k0, inp.ltarget
    ltok = k0 in xspopex0 and lt < xspopex0[k0].shape[0]
    xscompel = xspopex0[k0][lt] if ltok else z.clone()
    xselastot = inp.xselasinc_mb + xscompel
    xsnonel = torch.clamp(inp.xsreacinc_mb - xscompel, min=0.0)
    xscompall = torch.clamp(
        torch.as_tensor(
            inp.xsreacinc_mb - inp.xsdirdiscsum_mb - inp.xspreeqsum_mb - inp.xsgrsum_mb
            - inp.xsracape_mb, dtype=DTYPE, device=device),
        min=0.0,
    )
    xscompnonel = torch.clamp(xscompall - xscompel, min=0.0)

    # binary.f90 writes binE*.out at line 380, BEFORE it removes compound elastic at line 496,
    # so the printed population still holds it in the target's own (J, parity) cell.
    xspop_bine = {t: v.clone() for t, v in xspop.items()}
    xspopex_bine = {t: v.clone() for t, v in xspopex.items()}
    if ltok:
        feedbinary[k0] = feedbinary[k0].clone()
        feedbinary[k0][lt] = z
        # Remove compound elastic from the target state (binary.f90:496-499).
        xspopex[k0] = xspopex[k0].clone()
        xspopex[k0][lt] = z
        xspop[k0] = xspop[k0].clone()
        xspop[k0][lt, inp.targetspin2 // 2, _pi(inp.target_parity)] = z
        preeqpopex[k0] = preeqpopex[k0].clone()
        preeqpopex[k0][lt] = z

    return BinaryResult(
        xspop_mb=xspop, xspopex_mb=xspopex, xspop_bine_mb=xspop_bine,
        xspopex_bine_mb=xspopex_bine, xspopex0_mb=xspopex0, xspopnuc_mb=xspopnuc,
        xspopdir_mb=xspopdir, preeqpopex_mb=preeqpopex, xsdisc_mb=xsdisc,
        xsdirdisc_mb=xsdirdisc, xscompdisc_mb=xscompdisc, feedbinary_mb=feedbinary,
        sfactor=sfac_out, xsdisctot_mb=xsdisctot, xscompdisctot_mb=xscompdisctot,
        xsdircont_mb=xsdircont, xsdirect_mb=xsdirect, xsconttot_mb=xsconttot,
        xscompound_mb=xscompound, xsbinary_mb=xsbin, xscompel_mb=xscompel,
        xselastot_mb=xselastot, xsnonel_mb=xsnonel, xscompnonel_mb=xscompnonel,
    )
