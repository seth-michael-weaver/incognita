"""Discrete levels: energies, spins, parities, half-lives, gamma branching ratios and conversion
coefficients, including TALYS's rules for missing spins and the number of levels kept.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T2 (physics/hf/CONTRACT.md §7). Acceptance test: A-struct (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    levels.f90:1 (levels)
    levelsout.f90:1 (levelsout)
    gammadecay.f90:1 (gammadecay)
    branching.f90:1 (branching)

Rules reproduced from levels.f90 (line numbers of the Fortran)
--------------------------------------------------------------
* Defaults before the file is read (:95-117): level 0 = ground state with the spin/parity of the
  theoretical mass table; level 1 at ``min(26/A, 10)`` MeV with J+2 and the same parity, one
  branch to level 0 with ratio 1. If the level file does not exist TALYS returns right there,
  leaving ``nlev`` untouched (so a nucleus without a level file keeps nlev = 30 slots, all but two
  zero) -- reproduced.
* ``nlev2 = min(nnn, numlev=40)`` levels are read with branches, ``nlevmax2 = min(nnn,
  numlev2=300)`` in total (:163, :212). Spins are capped at numJ = 40.
* Branches: zero ratios are dropped (:185-194), except for a level whose `nbranch` is already set
  -- level 1, from the defaults -- which keeps its default branch to level 0 with ratio 1 and only
  takes the conversion coefficient and assignment flag from the file (:179-183). The read buffers
  `br`, `con`, `bas` are NOT cleared between levels (:155-157), which that path can expose.
* Half-lives below ``isomer`` (1 s) are zeroed for levels 0..nlev2 (:206); `tauripl` keeps the
  file value for output.
* ``nlev = max(min(nlev, nlev2), 1)``; ``nlevmax2 = max(min(nnn, 300), 1)``.
* Isomers are levels 1..nlevmax2 with ``tau >= isomer`` (:252-258). Isomers beyond nlev are then
  copied, from the top down, into the last slots of the nlev list (:282-305): energy, spin,
  parity, half-life and `levnum = min(i, 99)` move, the assignment flags are blanked, and the
  branches and ENSDF string of the overwritten slot stay. Note the strict ``tau > isomer`` there.
* `Risomer` rescaling of feeding branches (:307-340) when Risomer /= 1.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import cache, lru_cache
from typing import TYPE_CHECKING

import numpy as np
import torch
from torch import Tensor

from physics.hf.core.tensors import DTYPE
from physics.hf.structure.files import fortran_reader, level_records

if TYPE_CHECKING:
    from physics.hf.input.defaults import Options, Params
    from physics.hf.structure.masses import Masses

__all__ = ["Levels", "discrete_levels", "gamma_cascade", "NUMLEV", "NUMLEV2"]

NUMLEV = 40  # A0_talys_mod.f90:43
NUMLEV2 = 300  # A0_talys_mod.f90:48
NUMJ = 40  # A0_talys_mod.f90:68
NUMISOM = 10  # A0_talys_mod.f90:44

_LEVEL_FMT = "(4x, f11.6, f6.1, 3x, i2, i3, 18x, e10.3, 3a1, a18)"  # levels.f90:172
_LEVEL_FMT2 = "(4x, f11.6, f6.1, 3x, i2, i3, 18x, e10.3, 3a1)"  # levels.f90:215
_BRANCH_FMT = "(29x, i3, f10.6, e10.3, 5x, a1)"  # levels.f90:176


def _f32(x: float) -> float:
    return float(np.float32(x))


@dataclass(frozen=True)
class Levels:
    """The discrete levels of one nucleus as TALYS holds them after levels.f90.

    Levels 0..nlev are the ones TALYS uses in the reaction (and prints in levels*.out); the
    ``all_*`` arrays run to nlevmax2 (used by level-density matching and deformation).
    Units: energies MeV, half-lives seconds (0 = below the isomer cut; ``half_life_ripl_s``
    keeps the file value, 0 = not given). Branch ratios are fractions (levels*.out prints %).
    """

    Z: int
    A: int
    nlev: int
    nlevmax2: int
    e_mev: Tensor  # (nlev+1,) edis
    spin: Tensor  # (nlev+1,) jdis
    parity: Tensor  # (nlev+1,) +-1
    half_life_s: Tensor  # (nlev+1,) tau
    half_life_ripl_s: Tensor  # (nlev+1,) tauripl
    levnum: Tensor  # (nlev+1,) int64
    nbranch: Tensor  # (nlev+1,) int64
    branch_to: Tensor  # (nlev+1, Kmax) int64, -1 padded
    branch_ratio: Tensor  # (nlev+1, Kmax) fraction
    conversion: Tensor  # (nlev+1, Kmax)
    branch_assign: tuple  # per level, tuple of 1-char flags per branch
    assign: tuple  # per level, 3-char string eassign+jassign+passign
    ensdf: tuple  # per level, the a18 ENSDF string
    all_e_mev: Tensor  # (nlevmax2+1,)
    all_spin: Tensor
    all_parity: Tensor
    all_half_life_s: Tensor
    Nisomer: int
    Lisomer: tuple[int, ...]
    file_found: bool
    notes: tuple[str, ...] = field(default=())


# SPEEDP. `discrete_levels` re-parses `levels/z<ZZZ>` from disk on every call, and the chain asks
# for the same nucleus over and over: the emission cascade's `_levels`, T6's level-density build,
# T7's gamma parameters, T8's residual pairing energies and T12's direct levels each ask
# independently, 75 times per target in the dump-free harness for ~20 distinct nuclei. The result
# is a frozen dataclass nothing writes into, so it can be shared.
#
# Keyed on the IDENTITY of `options`/`masses`/`params` rather than their value: `Params` holds
# tensors and is not hashable, and DIFFPARAM hands out a fresh one per override set, which must
# not collide with the default run's. The key objects are kept alive by the cache, so an id can
# never be reused while its entry lives.
_LEVELS_CACHE: dict[tuple, tuple] = {}
_LEVELS_CACHE_MAX = 512


def discrete_levels(
    Z: int,
    A: int,
    options: Options,
    masses: Masses | None = None,
    params: Params | None = None,
    nlev: int | None = None,
    prior_call: bool = False,
) -> Levels:
    """The levels TALYS uses for this nucleus, exactly as listed in levels*.out (including assigned
    spins marked in the Assignment column). Branch ratios converted from percent to fractions
    with core.units-free arithmetic (x / 100).

    `masses` supplies the ground-state spin/parity used when the file lacks the nucleus (computed
    from `options` if None). `nlev` overrides the initial `nlev(Zix, Nix)` (default
    ``options.nlev_of``). `params` supplies `risomer`. `prior_call` reproduces a nucleus whose
    levels TALYS had already read once before this call (see :func:`levels_call_history`): the
    branch lists are those of the first read, the conversion coefficients and assignment flags
    are re-taken by file branch index, which misaligns them wherever a zero-ratio branch was
    dropped.

    TALYS: levels.f90:1 (levels)
    Test: A-struct
    """
    key = (int(Z), int(A), id(options), id(masses), id(params), nlev, bool(prior_call))
    hit = _LEVELS_CACHE.get(key)
    if hit is not None:
        return hit[0]
    lv = _discrete_levels(Z, A, options, masses, params, nlev, prior_call)
    if len(_LEVELS_CACHE) >= _LEVELS_CACHE_MAX:
        _LEVELS_CACHE.pop(next(iter(_LEVELS_CACHE)))
    _LEVELS_CACHE[key] = (lv, options, masses, params)  # the refs pin the ids in the key
    return lv


def _discrete_levels(Z, A, options, masses, params, nlev, prior_call) -> Levels:
    if options.flagpseudores:
        raise NotImplementedError("pseudoresonances y (levels.f90:347) is not ported")
    if options.Ltarget != 0:
        raise NotImplementedError("excited/isomeric targets (Ltarget /= 0) are not ported")
    Zix, Nix = options.Zinit - Z, options.Ninit - (A - Z)
    if masses is None:
        from physics.hf.structure.masses import masses as _masses

        masses = _masses(options, params)
    if 0 <= Zix < masses.gsspin.shape[0] and 0 <= Nix < masses.gsspin.shape[1]:
        gs_j, gs_p = float(masses.gsspin[Zix, Nix]), int(masses.gsparity[Zix, Nix])
    else:  # strucinitial.f90 defaults
        gs_j, gs_p = (0.0 if A % 2 == 0 else 0.5), 1
    nlev0 = options.nlev_of(Zix, Nix) if nlev is None else int(nlev)
    risomer = 1.0
    if params is not None and "risomer" in params:
        risomer = float(params.at("risomer", Zix, Nix))
    # COREX: everything below reads only these values and the level file, so the result is a
    # pure function of them (no target in the key: Zix/Nix only chose gs_j, gs_p, nlev0, risomer)
    return _levels_of_values(int(Z), int(A), gs_j, gs_p, int(nlev0), risomer,
                             int(options.disctable), float(options.isomer_s),
                             int(options.massmodel), bool(prior_call))


@lru_cache(maxsize=2048)
def _levels_of_values(Z: int, A: int, gs_j: float, gs_p: int, nlev0: int, risomer: float,
                      disctable: int, isomer_s: float, massmodel: int,
                      prior_call: bool) -> Levels:
    """COREX: `_discrete_levels` by value, shared across targets (`chartrun.KEEP`). `Levels` is
    frozen and nothing writes into its tensors: the id-keyed `_LEVELS_CACHE` already hands one
    object to every caller of a run."""
    size = NUMLEV2 + 1
    edis = np.zeros(size)
    jdis = np.zeros(size)
    parlev = np.ones(size, dtype=np.int64)
    tau = np.zeros(size)
    tauripl = np.zeros(size)
    levnum = np.zeros(size, dtype=np.int64)
    eas = [" "] * size
    jas = [" "] * size
    pas = [" "] * size
    ensdf = [" " * 18] * (NUMLEV + 1)
    nbranch = np.zeros(NUMLEV + 1, dtype=np.int64)
    branchlevel = np.zeros((NUMLEV + 1, NUMLEV + 1), dtype=np.int64)
    branchratio = np.zeros((NUMLEV + 1, NUMLEV + 1))
    conv = np.zeros((NUMLEV + 1, NUMLEV + 1))
    bassign = [[" "] * (NUMLEV + 1) for _ in range(NUMLEV + 1)]

    notes: list[str] = []
    # levels() runs again for a nucleus whose levels were already read -- dtheory.f90:80 calls it
    # for (Zix, Nix+1) from every densitymatch -- and the second call keeps the branch lists of
    # the first but re-assigns conv/bassign by FILE branch index (levels.f90:179-183)
    for _pass in range(2 if prior_call else 1):
        # defaults (levels.f90:95-117)
        edis[0] = 0.0
        jdis[0] = gs_j
        parlev[0] = gs_p
        levnum[1] = 1
        edis[1] = _f32(min(np.float32(26.0) / np.float32(A), np.float32(10.0)))
        jdis[1] = _f32(np.float32(jdis[0]) + np.float32(2.0))
        parlev[1] = parlev[0]
        jas[1], eas[1], pas[1] = "J", "E", "P"
        branchratio[1, 1] = 1.0
        nbranch[1] = 1
        bassign[1][0] = "B"
        conv[1, 0] = 0.0
        tau[1] = 0.0

        block = _level_block(int(Z), int(A), int(disctable))
        if block is None:
            notes.append("no level file: TALYS returns before nlev is adjusted (levels.f90:140)")
            return _pack(
                Z,
                A,
                nlev0,
                0,
                edis,
                jdis,
                parlev,
                tau,
                tauripl,
                levnum,
                nbranch,
                branchlevel,
                branchratio,
                conv,
                bassign,
                eas,
                jas,
                pas,
                ensdf,
                0,
                (),
                False,
                notes,
            )
        nnn, has_records, main, rest = block
        nlev2 = 0
        con = [0.0] * (NUMLEV + 1)
        br = [0.0] * (NUMLEV + 1)
        bas = ["B"] * (NUMLEV + 1)
        klev = [0] * (NUMLEV + 1)
        nlevmax2 = 0
        if nnn or has_records:
            nlev2 = min(nnn, NUMLEV)
            n1 = nlev2 + 1
            # NATIVEX2 `struct`: the per-level scalar stores of the loop below as slice stores
            # (the loop reads each level's own row only)
            cols = tuple(zip(*main[:n1]))
            edis[:n1], jdis[:n1], parlev[:n1], tau[:n1] = cols[0], cols[1], cols[2], cols[3]
            eas[:n1], jas[:n1], pas[:n1], ensdf[:n1] = cols[4], cols[5], cols[6], cols[7]
            nbr_now = nbranch[:n1].tolist()
            for i in range(n1):
                branches = cols[8][i]
                nb = len(branches)
                for jj, (kl, b, cv, ba) in enumerate(branches, 1):
                    klev[jj], br[jj], con[jj], bas[jj] = kl, b, cv, ba
                if nbr_now[i] > 0:
                    for jj in range(1, nbr_now[i] + 1):
                        conv[i, jj] = con[jj]
                        bassign[i][jj] = bas[jj]
                else:
                    ii = 0
                    for jj in range(1, nb + 1):
                        if br[jj] != 0.0:
                            ii += 1
                            branchlevel[i, ii] = klev[jj]
                            branchratio[i, ii] = br[jj]
                            conv[i, ii] = con[jj]
                            bassign[i][ii] = bas[jj]
                    nbranch[i] = ii
            jdis[:n1] = np.minimum(jdis[:n1], float(NUMJ))
            tauripl[:n1] = tau[:n1]
            tau[:n1] = np.where(tau[:n1] < isomer_s, 0.0, tau[:n1])
            levnum[:n1] = np.arange(n1)
            if massmodel <= 1:
                if jas[0] == "J" and pas[0] == "P":
                    jdis[0], parlev[0] = gs_j, gs_p
                if nlev2 == 0:
                    jdis[1] = _f32(np.float32(jdis[0]) + np.float32(2.0))
                    parlev[1] = parlev[0]
            nlevmax2 = min(nnn, NUMLEV2)
            if nlevmax2 > nlev2:
                re_, rj, rp, rt, ra1, ra2, ra3 = rest
                sl = slice(nlev2 + 1, nlevmax2 + 1)
                edis[sl], jdis[sl], parlev[sl], tau[sl] = re_, rj, rp, rt
                eas[sl], jas[sl], pas[sl] = ra1, ra2, ra3
        nlev_final = max(min(nlev0, nlev2), 1)
        nlevmax2 = max(min(nnn, NUMLEV2), 1)

        isomer = isomer_s
        # NATIVEX2 `struct`: the two scans over levels 1..nlevmax2 as array comparisons; the second
        # loop only writes slots N <= nlev_final and its own i, so the levels it acts on are the
        # ones above nlev_final with tau > isomer, read before it starts
        lisomer: list[int] = (np.flatnonzero(tau[1 : nlevmax2 + 1] >= isomer)[:NUMISOM]
                              + 1).tolist()
        nisomer = len(lisomer)

        lis = nisomer + 1
        hits = (np.flatnonzero(tau[nlev_final + 1 : nlevmax2 + 1] > isomer)[::-1]
                + (nlev_final + 1)).tolist() if isomer >= 0.1 else []
        for i in hits:
            lis -= 1
            N = nlev_final - nisomer + lis
            if lis >= 0 and N >= 0:
                levnum[N] = min(i, 99)
                edis[N], jdis[N], parlev[N], tau[N] = edis[i], jdis[i], parlev[i], tau[i]
                if N != i:
                    tau[i] = 0.0
                eas[N] = jas[N] = pas[N] = " "
        nlev0 = nlev_final

    if nisomer > 0 and risomer != 1.0:
        # levels.f90:307-340 (branchdone guard: one application per nucleus)
        for i in range(1, nlev2 + 1):
            if tau[i] >= isomer:
                brexist = [False] * (NUMLEV + 1)
                brexist[i] = True
                for j in range(i + 1, nlev2 + 1):
                    for k in range(1, int(nbranch[j]) + 1):
                        if brexist[branchlevel[j, k]]:
                            brexist[j] = True
                for j in range(i + 1, nlev2 + 1):
                    for k in range(1, int(nbranch[j]) + 1):
                        if brexist[branchlevel[j, k]]:
                            branchratio[j, k] = _f32(
                                np.float32(risomer) * np.float32(branchratio[j, k])
                            )
        for i in range(1, nlev2 + 1):
            s = np.float32(0.0)
            for k in range(1, int(nbranch[i]) + 1):
                s = s + np.float32(branchratio[i, k])
            if s > 0.0:
                for k in range(1, int(nbranch[i]) + 1):
                    branchratio[i, k] = _f32(np.float32(branchratio[i, k]) / s)

    return _pack(
        Z,
        A,
        nlev_final,
        nlevmax2,
        edis,
        jdis,
        parlev,
        tau,
        tauripl,
        levnum,
        nbranch,
        branchlevel,
        branchratio,
        conv,
        bassign,
        eas,
        jas,
        pas,
        ensdf,
        nisomer,
        tuple(lisomer),
        True,
        notes,
    )


@cache
def _level_block(Z: int, A: int, disctable: int):
    """COREX: `read_level_file`'s block for (Z, A) read with levels.f90's formats once per process
    (a pure function of the file; `chartrun.KEEP`): None without a level file, else (nnn, whether
    the block has records, levels 0..min(nnn, numlev) as (E, J, P, tau, 3 assignment flags, ENSDF,
    branches (klev, ratio, conv, flag)), levels up to min(nnn, numlev2) as columns). Real fields
    are rounded to real(sgl) and spins capped at numJ, as `_discrete_levels` did per read.

    NATIVEX2 `struct`: the records are indexed in the file's text (`files.level_records`) rather
    than copied out as a tuple, only the lines up to level numlev2 are touched, and the real(sgl)
    columns are gathered while reading; the same reads, the same float32 rounding per column."""
    block = level_records(Z, A, disctable)
    if block is None:
        return None
    nnn, records = block
    if not (nnn or records):
        return nnn, False, (), None
    got = _level_block_nx2(nnn, records)
    if got is not None:  # NATIVEX2 `struct`: the plain records read in C (native/nx2_struct.c)
        return got
    return _level_block_py(nnn, records)


def _level_block_py(nnn: int, records):
    """`_level_block`'s (nnn, True, main, rest) read with the Python format readers."""
    nlev2 = min(nnn, NUMLEV)
    pos = 0
    lev_rows, br_rows = [], []
    e_col, j_col, t_col, r_col, c_col = [], [], [], [], []
    read_lev, read_br, read_lev2 = (fortran_reader(_LEVEL_FMT), fortran_reader(_BRANCH_FMT),
                                    fortran_reader(_LEVEL_FMT2))
    for _i in range(nlev2 + 1):
        row = read_lev(records[pos])
        pos += 1
        nb = row[3]
        lev_rows.append(row)
        e_col.append(row[0])
        j_col.append(row[1])
        t_col.append(row[4])
        bs = [read_br(records[pos + jj]) for jj in range(nb)]
        for b in bs:
            r_col.append(b[1])
            c_col.append(b[2])
        br_rows.append(bs)
        pos += nb
    # the real(sgl) fields rounded to float32 in one conversion per column
    e32, j32, t32, r32, c32 = (np.array(c, dtype=np.float64).astype(np.float32)
                               .astype(np.float64).tolist()
                               for c in (e_col, j_col, t_col, r_col, c_col))
    main, k = [], 0
    for i, (r, bs) in enumerate(zip(lev_rows, br_rows, strict=True)):
        branches = []
        for b in bs:
            branches.append((b[0], r32[k], c32[k], b[3]))
            k += 1
        main.append((e32[i], j32[i], r[2], t32[i], r[5], r[6], r[7], r[8], tuple(branches)))
    nlevmax2 = min(nnn, NUMLEV2)
    e2, j2, p2, t2, a1, a2, a3 = [], [], [], [], [], [], []
    for _i in range(nlev2 + 1, nlevmax2 + 1):
        row = read_lev2(records[pos])
        pos += 1 + row[3]
        e2.append(row[0])
        j2.append(row[1])
        p2.append(row[2])
        t2.append(row[4])
        a1.append(row[5])
        a2.append(row[6])
        a3.append(row[7])
    e2a, j2a, t2a = (np.array(c, dtype=np.float64).astype(np.float32).astype(np.float64)
                     for c in (e2, j2, t2))
    rest = (e2a, np.minimum(j2a, float(NUMJ)), np.array(p2, dtype=np.int64), t2a, a1, a2, a3)
    return nnn, True, tuple(main), rest


def _level_block_nx2(nnn: int, records):
    """NATIVEX2 `struct`: `_level_block`'s (nnn, True, main, rest) with the records read by
    `nx2_struct_levels`, or None when there is no build (`HF_NX2_STRUCT=0`), the file is not held
    as one text, or any field of the block is not in the plain form the kernel converts (the
    Python readers then read the block, and raise where they raised).

    TALYS: levels.f90:1 (levels)
    Test: tests/hf/test_nx2_struct.py
    """
    from physics.hf.native import nx2

    fn = nx2.kernel("nx2_struct_levels", [nx2.P, nx2.P, nx2.P, nx2.I64, nx2.I64, nx2.I64,
                                          nx2.P, nx2.P, nx2.P, nx2.P, nx2.P, nx2.P],
                    nx2.I64, lever="struct")
    if fn is None:
        return None
    buf = records.buffer()
    if buf is None:
        return None
    data, ls, le = buf
    nrec = len(records)
    nlev2 = min(nnn, NUMLEV)
    nlevmax2 = min(nnn, NUMLEV2)
    nrest = max(nlevmax2 - nlev2, 0)
    raw = np.frombuffer(data, dtype=np.uint8)
    lev = np.empty((nlev2 + 1, 5))
    lchr = np.empty((nlev2 + 1) * 21, dtype=np.uint8)
    br = np.empty((max(nrec, 1), 3))
    bchr = np.empty(max(nrec, 1), dtype=np.uint8)
    rest = np.empty((max(nrest, 1), 4))
    rchr = np.empty(max(nrest, 1) * 3, dtype=np.uint8)
    nbr = fn(nx2.ptr(raw), nx2.ptr(ls), nx2.ptr(le), nrec, nlev2, nlevmax2, nx2.ptr(lev),
             nx2.ptr(lchr), nx2.ptr(br), nx2.ptr(bchr), nx2.ptr(rest), nx2.ptr(rchr))
    if nbr < 0:
        return None
    # the real(sgl) fields rounded to float32 in one conversion per column, as `_level_block`
    lev32 = lev[:, (0, 1, 4)].astype(np.float32).astype(np.float64)
    e32, j32, t32 = (lev32[:, c].tolist() for c in range(3))
    br32 = br[:nbr, 1:].astype(np.float32).astype(np.float64)
    r32, c32 = br32[:, 0].tolist(), br32[:, 1].tolist()
    klev = br[:nbr, 0].astype(np.int64).tolist()
    par = lev[:, 2].astype(np.int64).tolist()
    nbs = lev[:, 3].astype(np.int64).tolist()
    ls_ = lchr.tobytes().decode("latin-1")
    bs_ = bchr[:nbr].tobytes().decode("latin-1")
    main, k = [], 0
    for i in range(nlev2 + 1):
        o = 21 * i
        branches = []
        for _ in range(nbs[i]):
            branches.append((klev[k], r32[k], c32[k], bs_[k]))
            k += 1
        main.append((e32[i], j32[i], par[i], t32[i], ls_[o], ls_[o + 1], ls_[o + 2],
                     ls_[o + 3:o + 21], tuple(branches)))
    rest = rest[:nrest]
    ejt = rest[:, (0, 1, 3)].astype(np.float32).astype(np.float64)
    rs_ = rchr[: 3 * nrest].tobytes().decode("latin-1")
    rest_out = (ejt[:, 0].copy(), np.minimum(ejt[:, 1], float(NUMJ)),
                rest[:, 2].astype(np.int64), ejt[:, 2].copy(),
                list(rs_[0::3]), list(rs_[1::3]), list(rs_[2::3]))
    return nnn, True, tuple(main), rest_out


def _pack(
    Z,
    A,
    nlev,
    nlevmax2,
    edis,
    jdis,
    parlev,
    tau,
    tauripl,
    levnum,
    nbranch,
    branchlevel,
    branchratio,
    conv,
    bassign,
    eas,
    jas,
    pas,
    ensdf,
    nisomer,
    lisomer,
    found,
    notes,
):
    n = nlev + 1
    kmax = max(int(nbranch[: min(n, NUMLEV + 1)].max(initial=0)), 1)
    bto = np.full((n, kmax), -1, dtype=np.int64)
    brat = np.zeros((n, kmax))
    bconv = np.zeros((n, kmax))
    bas = []
    nb_out = np.zeros(n, dtype=np.int64)
    for i in range(n):
        if i > NUMLEV:
            bas.append(())
            continue
        k = int(nbranch[i])
        nb_out[i] = k
        bto[i, :k] = branchlevel[i, 1 : k + 1]
        brat[i, :k] = branchratio[i, 1 : k + 1]
        bconv[i, :k] = conv[i, 1 : k + 1]
        bas.append(tuple(bassign[i][1 : k + 1]))
    m = nlevmax2 + 1

    def t(x):
        return torch.as_tensor(np.asarray(x), dtype=DTYPE)

    return Levels(
        Z=Z,
        A=A,
        nlev=nlev,
        nlevmax2=nlevmax2,
        e_mev=t(edis[:n]),
        spin=t(jdis[:n]),
        parity=t(parlev[:n]),
        half_life_s=t(tau[:n]),
        half_life_ripl_s=t(tauripl[:n]),
        levnum=torch.as_tensor(levnum[:n]),
        nbranch=torch.as_tensor(nb_out),
        branch_to=torch.as_tensor(bto),
        branch_ratio=t(brat),
        conversion=t(bconv),
        branch_assign=tuple(bas),
        assign=tuple(eas[i] + jas[i] + pas[i] for i in range(n)),
        ensdf=tuple(ensdf[i] if i <= NUMLEV else " " * 18 for i in range(n)),
        all_e_mev=t(edis[:m]),
        all_spin=t(jdis[:m]),
        all_parity=t(parlev[:m]),
        all_half_life_s=t(tau[:m]),
        Nisomer=nisomer,
        Lisomer=lisomer,
        file_found=found,
        notes=tuple(notes),
    )


def gamma_cascade(levels: Levels, flagelectron: bool = True) -> list[dict]:
    """Cumulative discrete gamma decay of every level (gamma*.tot): for each level i >= 1 the
    gamma lines (parent, daughter, E_gamma [MeV], normalised intensity) sorted as TALYS sorts
    them, and the total gamma yield (conversion-corrected when `flagelectron`).

    TALYS: gammadecay.f90:1 (gammadecay)
    Test: A-struct
    """
    f = np.float32
    e = levels.e_mev.numpy()
    tau = levels.half_life_s.numpy()
    nb = levels.nbranch.numpy()
    bto = levels.branch_to.numpy()
    brat = levels.branch_ratio.numpy()
    conv = levels.conversion.numpy()
    out = []
    for i in range(1, levels.nlev + 1):
        flux = [f(0.0)] * (levels.nlev + 1)
        flux[i] = f(1.0)
        total = f(0.0)
        totalg = f(0.0)
        lines = []
        for j in range(i, 0, -1):
            if tau[j] != 0.0:
                continue
            for k in range(int(nb[j])):
                lvl = int(bto[j, k])
                if flux[j] == 0.0:
                    continue
                b = f(brat[j, k]) * flux[j]
                eg = f(e[j]) - f(e[lvl])
                lines.append([j, lvl, eg, b, f(e[j]), f(e[lvl])])
                flux[lvl] = flux[lvl] + b
                total = total + b
                if flagelectron:
                    totalg = totalg + b / (f(1.0) + f(conv[j, k]))
                else:
                    totalg = total
        if total != 0.0:  # gammadecay.f90: `if (total == 0.) cycle` skips normalise and sort
            for ln in lines:
                ln[3] = ln[3] / total
            ng = len(lines)
            for jj in range(ng):  # gammadecay.f90 exchange sort, reproduced as written
                for kk in range(jj + 1):
                    if lines[jj][2] > lines[kk][2]:
                        lines[jj], lines[kk] = lines[kk], lines[jj]
        out.append(
            {
                "level": i,
                "e_mev": float(e[i]),
                "yield": float(totalg),
                "lines": [
                    (a, b, float(c), float(d), float(pe), float(de)) for a, b, c, d, pe, de in lines
                ],
            }
        )
    return out
