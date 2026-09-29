"""Hauser-Feshbach decay of a populated continuum state (Zcomp, Ncomp, bin, J, parity) without
width fluctuations (compound.f90), used by the multiple-emission cascade.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T9 (physics/hf/CONTRACT.md §7). Acceptance test: A-mult (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    compound.f90:1 (compound)
    multiple.f90:1 (multiple)     -- only the per-bin loop order it imposes, not its bookkeeping
    compemission.f90:1 (compemission)  -- consumer of `mcontrib`, returned but not ported here

How this differs from `target.py`, which ports comptarget.f90 for the first (binary) decay:

* no width fluctuations at all (`compound.f90` has no W); the feeding of every daughter state is
  `feed * enumhf` with the single scalar `feed = (1 - Dmulti) * xspop(mother) / denomhf`.
* the **averaged** transmission coefficients are the default here. `comptarget.f90` always sums
  `Tjlnex(l', updown)` over j'; `compound.f90` does that only when `fullhf y`, and at the default
  `flagfullhf = .false.` (input_compoundmodel.f90:73) it uses `(2s+1) * Tlnex(l', type, nexout)`
  summed over l' of the right parity. The two differ when the spin-orbit term is large.
* fission is a **logarithmic integration** of `tfisdown/tfis/tfisup` over the mother bin
  (compound.f90:120-147), not the single `tfis` comptarget uses.
* when `denomhf == 0` the mother's flux is not trapped: it is spread equally over the compound
  nucleus's own discrete levels (compound.f90:404-419).

Inputs are injected exactly as in `prepare.py`: `rho0`, `Tlnex`/`Tjlnex`, `Tgam` and the fission
transmission are what `densprepare` left in memory, dumped by `talys_instrument/cndump.f90`
(the `cnmulti_*` hooks) and loaded by `load_cn_multi_dump`. `MultiInputs` is one mother bin
(Zcomp, Ncomp, nex) at one incident energy.

Vectorisation. The loops over (J, parity) stay Python loops; inside a block everything is a tensor
expression over (nexout, Ir, P', l', updown), the same shapes `prepare.exit_channel_sums` builds.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import numpy as np
import torch
from torch import Tensor

from physics.hf.compound.prepare import NUMJ, ResidualChannels, _split_dump_fields
from physics.hf.core.tensors import DTYPE

TRANSEPS = 1.0e-8  # input_numerics.f90:80


@dataclass
class MultiInputs:
    """Injected inputs of compound.f90 for one mother bin (Zcomp, Ncomp, nex) at one energy."""

    zcomp: int
    ncomp: int
    nex: int
    odd: int
    e_inc_mev: float
    ex_inc_mev: float  # Exinc, centre of the mother bin
    dex_inc_mev: float  # dExinc
    exmax_mev: float  # Exmax(Zcomp, Ncomp)
    popeps_mb: float
    dmulti: float
    flagfullhf: bool
    maxj_mother: int
    gammax: int
    nlast_mother: int
    nfisbar: int
    numj: int
    flagfission: bool
    # mother population per (J, parity): xspop(Zcomp, Ncomp, nex, J, P)
    xspop_mother_mb: np.ndarray  # (numJ+1, 2), parity axis (-1, +1)
    residuals: dict[int, ResidualChannels] = field(default_factory=dict)
    # fission transmission per (J2, parity): (tfisdown, tfis, tfisup)
    tfis: dict[tuple[int, int], tuple[float, float, float]] = field(default_factory=dict)
    # reference outputs carried by the same dump (not inputs; tests only)
    denomhf: dict[tuple[int, int], float] = field(default_factory=dict)
    ref_dpop_mb: dict[int, np.ndarray] = field(default_factory=dict)  # type -> (Nex, numJ+1, 2)
    # discrete-level spins/parities of the COMPOUND nucleus, for the leftover branch
    mother_levels: list[tuple[int, int]] = field(default_factory=list)  # (Ir, parity) per level


@dataclass(frozen=True)
class ContinuumFeeding:
    """What one mother bin hands to its daughters."""

    dpop_mb: dict[int, Tensor]  # type -> (Nex, numJ+1, 2) added to xspop of the residual
    fisfeed_mb: Tensor  # scalar, added to xsfeed(Zcomp, Ncomp, -1)
    mcontrib_mb: dict[int, Tensor]  # type -> (Nex,) sumIP, what compemission.f90 interpolates
    leftover_mb: Tensor  # scalar, flux spread over the mother's own discrete levels
    denom: dict[tuple[int, int], Tensor]  # (J2, parity) -> denomhf, for diagnosis


def _pidx(p: int) -> int:
    return 0 if p == -1 else 1


def load_cn_multi_dump(path: str | Path) -> list[MultiInputs]:
    """Parse cn_multi.txt written by talys_instrument/cndump.f90 (`cnmulti_*`) into one
    MultiInputs per (incident energy, mother bin) at which compound() ran.

    TALYS: compound.f90:1 (compound) -- the arrays it holds after densprepare
    Test: A-mult
    """
    cases: list[MultiInputs] = []
    cur: MultiInputs | None = None
    nexinfo: dict[int, list] = {}
    rows: dict[str, list] = {}

    def finish():
        if cur is None:
            return
        for t, (meta, per_nex) in nexinfo.items():
            if meta["nexmax"] < 0:
                # compound.f90:224 `do nexout = 0, nexmax(type)`: nexmax = -1 is a channel with no
                # open bin at this mother excitation, so it contributes to neither enumhf nor the
                # daughter population. multiple.f90 still dumps its TYPE line, but no NEX rows.
                continue
            n = meta["nexmax"] + 1
            r = ResidualChannels(
                type=t, zix=meta["zix"], nix=meta["nix"], maxex=meta["nexmax"],
                nlast=meta["nl"], spin2=meta["spin2"], parspin2=meta["parspin2"],
                lmaxhf=np.zeros(n, int), maxj=np.zeros(n, int), ex_mev=np.zeros(n),
                parlev=np.zeros(n, int), jdis2=-np.ones(n, int),
                rho=np.zeros((n, NUMJ + 1, 2)),
            )
            for nex, lmh, mj, ex, jd in per_nex:
                r.lmaxhf[nex], r.maxj[nex], r.ex_mev[nex] = lmh, mj, ex
                if nex <= r.nlast:
                    r.jdis2[nex] = int(2.0 * np.float32(jd))
            cur.residuals[t] = r
        for tt, nex, p in rows.get("LEV", []):
            cur.residuals[tt].parlev[nex] = p
        for tt, nex, ir, p, v in rows.get("RHO", []):
            cur.residuals[tt].rho[nex, ir, _pidx(p)] = v
        for t, r in cur.residuals.items():
            n = r.maxex + 1
            if t == 0:
                r.tgam = np.zeros((n, cur.gammax + 1, 2, NUMJ + 1, 2))
            else:
                lmax = max(1, int(r.lmaxhf.max()) + 1) if r.lmaxhf.size else 1
                r.tl = np.zeros((n, lmax))
                r.tjl = np.zeros((n, lmax, 3))
        for tt, nex, l, irad, vals in rows.get("TGAM", []):
            cur.residuals[tt].tgam[nex, l, irad] = np.asarray(vals).reshape(2, NUMJ + 1).T
        for tt, nex, l, tl, tjl in rows.get("TL", []):
            r = cur.residuals[tt]
            if l >= r.tl.shape[1]:
                pad = l + 1 - r.tl.shape[1]
                r.tl = np.concatenate([r.tl, np.zeros((r.tl.shape[0], pad))], 1)
                r.tjl = np.concatenate([r.tjl, np.zeros((r.tjl.shape[0], pad, 3))], 1)
            r.tl[nex, l] = tl
            r.tjl[nex, l] = tjl
        for tt, nex, ir, p, v in rows.get("DPOP", []):
            if tt not in cur.ref_dpop_mb:
                cur.ref_dpop_mb[tt] = np.zeros((cur.residuals[tt].maxex + 1, NUMJ + 1, 2))
            cur.ref_dpop_mb[tt][nex, ir, _pidx(p)] = v
        cases.append(cur)

    with open(path) as f:
        for line in f:
            tag, rest = line[:5].strip(), _split_dump_fields(line[5:])
            if tag == "MBIN":
                finish()
                cur, nexinfo, rows = None, {}, {}
                z, n, nex, odd = map(int, rest[:4])
                cur = MultiInputs(
                    zcomp=z, ncomp=n, nex=nex, odd=odd,
                    e_inc_mev=float(rest[4]), ex_inc_mev=float(rest[5]),
                    dex_inc_mev=float(rest[6]), exmax_mev=float(rest[7]),
                    popeps_mb=float(rest[8]), dmulti=float(rest[9]),
                    flagfullhf=rest[10] == "T",
                    maxj_mother=0, gammax=2, nlast_mother=0, nfisbar=0, numj=NUMJ,
                    flagfission=False, xspop_mother_mb=np.zeros((NUMJ + 1, 2)),
                )
            elif tag == "MINT":
                (cur.maxj_mother, cur.gammax, cur.nlast_mother, cur.nfisbar,
                 cur.numj) = map(int, rest[:5])
                cur.flagfission = rest[5] == "T"
            elif tag == "MPOP":
                cur.xspop_mother_mb[int(rest[0]), _pidx(int(rest[1]))] = float(rest[2])
            elif tag == "TYPE":
                t = int(rest[0])
                nexinfo[t] = [dict(zix=int(rest[1]), nix=int(rest[2]), nexmax=int(rest[3]),
                                   nl=int(rest[4]), spin2=int(rest[5]),
                                   parspin2=int(2.0 * float(rest[6]))), []]
            elif tag == "NEX":
                t, nex, lmh, mj = map(int, rest[:4])
                nexinfo[t][1].append((nex, lmh, mj, float(rest[4]), float(rest[6])))
            elif tag == "LEV":
                rows.setdefault("LEV", []).append(tuple(map(int, rest)))
            elif tag == "RHO":
                rows.setdefault("RHO", []).append((*map(int, rest[:4]), float(rest[4])))
            elif tag == "TGAM":
                rows.setdefault("TGAM", []).append(
                    (*map(int, rest[:4]), list(map(float, rest[4:]))))
            elif tag == "TL":
                rows.setdefault("TL", []).append(
                    (*map(int, rest[:3]), float(rest[3]), list(map(float, rest[4:7]))))
            elif tag == "MJP":
                cur.denomhf[(int(rest[0]), int(rest[1]))] = float(rest[2])
            elif tag == "MFIS":
                cur.tfis[(int(rest[0]), int(rest[1]))] = tuple(map(float, rest[2:5]))
            elif tag == "DPOP":
                rows.setdefault("DPOP", []).append((*map(int, rest[:4]), float(rest[4])))
    finish()
    return cases


def fission_width(mi: MultiInputs, J2: int, parity: int, device=None) -> Tensor:
    """The logarithmically integrated fission transmission of the mother bin (`fiscontr`).

    TALYS: compound.f90:120-147 (inside compound, iloop = 1)
    Test: A-mult
    """
    z = torch.zeros((), dtype=DTYPE, device=device)
    if not (mi.flagfission and mi.nfisbar != 0):
        return z
    tri = mi.tfis.get((J2, parity))
    if tri is None:
        return z
    tfd, tf, tfu = (torch.as_tensor(max(v, TRANSEPS), dtype=DTYPE, device=device) for v in tri)
    explus = min(mi.exmax_mev, mi.ex_inc_mev + 0.5 * mi.dex_inc_mev)
    exmin = max(mi.ex_inc_mev - 0.5 * mi.dex_inc_mev, 0.0)
    de1, de2 = mi.ex_inc_mev - exmin, explus - mi.ex_inc_mev
    logd, logu = torch.log(tf) - torch.log(tfd), torch.log(tfu) - torch.log(tf)
    c1 = torch.where(logd == 0, tf * de1, (tf - tfd) / torch.where(logd == 0, 1.0, logd) * de1)
    c2 = torch.where(logu == 0, tf * de2, (tfu - tf) / torch.where(logu == 0, 1.0, logu) * de2)
    if explus <= exmin:
        return z
    fis = (c1 + c2) / (explus - exmin)
    return torch.where(fis <= 10.0 * TRANSEPS, z, fis)


def _residual_spins(r: ResidualChannels, J2: int, device) -> tuple[Tensor, Tensor]:
    """Irspin2 of shape (Nex, numJ+1) and `valid` of shape (Nex, numJ+1, 2): the residual
    (spin, parity) cells compound.f90 visits.

    Continuum: Irspin2 = mod(J2 + parspin2, 2) .. 2 maxJ step 2, both parities. Discrete levels:
    the single level spin int(2 jdis), stored at Ir = Irspin2/2.

    Discrete levels also carry exactly one PARITY, `parlev` (compound.f90:243-246 sets
    `Pprimebeg = Pprimeend = parlev`). That matters: `rho0` is a scratch array TALYS refills per
    residual without clearing, so a level's own `Ir` row can still hold a stale non-zero value at
    the opposite parity from an earlier nucleus or bin. TALYS never reads it; a mask on `Ir`
    alone does, and then adds a whole phantom exit channel.

    TALYS: compound.f90:1 (compound)  -- the Pprimebeg/Pprimeend block at 241-256
    Test: A-mult
    """
    nex = r.maxex + 1
    ir = torch.arange(NUMJ + 1, device=device)
    base = (J2 + r.parspin2) % 2
    irs2 = (2 * ir + base)[None, :].expand(nex, -1).clone()
    maxj = torch.as_tensor(r.maxj, device=device)
    valid = (irs2 <= (2 * maxj)[:, None])[:, :, None].expand(-1, -1, 2)
    disc = torch.as_tensor(np.arange(nex) <= r.nlast, device=device)
    jd2 = torch.as_tensor(r.jdis2, device=device)
    ir_disc = torch.div(jd2, 2, rounding_mode="floor")
    irs2 = torch.where(disc[:, None], jd2[:, None].expand(-1, NUMJ + 1), irs2)
    par_disc = torch.as_tensor((r.parlev > 0).astype(int), device=device)  # -1 -> 0, +1 -> 1
    disc_ok = (ir[None, :, None] == ir_disc[:, None, None]) & (
        torch.arange(2, device=device)[None, None, :] == par_disc[:, None, None])
    valid = torch.where(disc[:, None, None], disc_ok, valid)
    return irs2, valid


def partial_widths(mi: MultiInputs, J2: int, parity: int, device=None) -> dict[int, Tensor]:
    """`enumhf(Ir, P', type, nexout)` = rho0 * total for every exit type of one (J2, parity).

    TALYS: compound.f90:1 (compound)   -- iloop = 1
    Test: A-mult
    """
    J = J2 // 2
    out: dict[int, Tensor] = {}
    pprime = torch.tensor([-1, 1], device=device)
    pardif2 = (parity - pprime).abs() // 2  # (2,)
    for t, r in sorted(mi.residuals.items()):
        rho = torch.as_tensor(r.rho, dtype=DTYPE, device=device)  # (Nex, Jx, 2)
        irs2, valid = _residual_spins(r, J2, device)
        rho = torch.where(valid & (rho >= 1.0e-20), rho, 0.0)
        if r.nlast == 0:
            rho = rho.clone()
            rho[0] = 0.0  # compound.f90:236 `if (nexout == 0 .and. NL == 0) cycle`
        lmaxhf = torch.as_tensor(r.lmaxhf, device=device)
        j2min = (J2 - irs2).abs()  # (Nex, Jx)
        j2plus = J2 + irs2
        lbeg = torch.div((j2min - r.parspin2).abs(), 2, rounding_mode="floor")
        lend = torch.minimum(torch.div(j2plus + r.parspin2, 2, rounding_mode="floor"),
                             lmaxhf[:, None])
        if t == 0:
            L = mi.gammax + 1
            lp = torch.arange(L, device=device)
            inrange = (lp[None, None, :] >= lbeg[..., None]) & (lp[None, None, :] <= lend[..., None])
            tg = torch.as_tensor(r.tgam, dtype=DTYPE, device=device)  # (Nex, L, 2, Jx, 2)
            tgJ = tg[:, :L, :, J, _pidx(parity)]  # (Nex, L, irad)
            # irad = 1 - |mod(l', 2) - pardif2|  (compound.f90:270)
            irad = 1 - ((lp % 2)[None, :] - pardif2[:, None]).abs()  # (2, L)
            sel = torch.nn.functional.one_hot(irad.clamp(min=0), 2).to(DTYPE)  # (2, L, 2)
            tl_p = (tgJ[:, None, :, :] * sel[None, :, :, :]).sum(-1)  # (Nex, P', L)
            total = (tl_p[:, None, :, :] * inrange[:, :, None, :].to(DTYPE)).sum(-1)
        else:
            L = r.tjl.shape[1]
            lp = torch.arange(L, device=device)
            okp = (lp[None, :] % 2 == pardif2[:, None])  # (P', L)
            inrange = (lp[None, None, :] >= lbeg[..., None]) & (lp[None, None, :] <= lend[..., None])
            allowed = inrange[:, :, None, :] & okp[None, None, :, :]  # (Nex, Jx, P', L)
            if mi.flagfullhf:
                # jj2' in max(J2minI2, |l2'-2s|) .. min(J2plusI2, l2'+2s) step 2, as in prepare.py
                ud = torch.tensor([-1, 0, 1], device=device)
                jj2p = 2 * lp[:, None] + ud[None, :] * r.spin2  # (L, 3)
                dj = jj2p - 2 * lp[:, None]
                ok_s = (dj.abs() <= r.parspin2) & ((dj - r.parspin2) % 2 == 0) & (jj2p >= 0)
                ok_s = ok_s & (2 * lp[:, None] >= (jj2p - r.parspin2).abs())
                ok_j = (jj2p[None, None] >= j2min[..., None, None]) & (
                    jj2p[None, None] <= j2plus[..., None, None])  # (Nex, Jx, L, 3)
                tt = torch.as_tensor(r.tjl, dtype=DTYPE, device=device)  # (Nex, L, 3)
                w = allowed[..., None] & ok_j[:, :, None] & ok_s[None, None, None]
                total = (w.to(DTYPE) * tt[:, None, None, :, :]).sum((-1, -2))
            else:
                tl = torch.as_tensor(r.tl, dtype=DTYPE, device=device)  # (Nex, L)
                s2plus1 = float(r.parspin2 + 1)
                total = s2plus1 * (allowed.to(DTYPE) * tl[:, None, None, :]).sum(-1)
        out[t] = rho * total
    return out


def _lrange_sums(tl: Tensor, L: int) -> Tensor:
    """`G[c, nexout, a, b]` = sum of `tl[nexout, l]` over a <= l <= b with l % 2 == c, summed
    upward from l = a (0 where b < a). (2, Nex, L, L).

    Every (J, parity) cell of a mother bin reads `sum_{l = lbeg..lend, parity} Tlnex(l)` for each
    (nexout, Ir, P'); tabulating those range sums once per residual turns the per-cell sum over
    l' into a gather.

    TALYS: compound.f90:1 (compound)
    Test: A-mult / SPEED0 golden
    """
    lp = torch.arange(L, device=tl.device)
    out = []
    for c in (0, 1):
        m = torch.where((lp % 2 == c)[None, :], tl, torch.zeros((), dtype=tl.dtype,
                                                                 device=tl.device))  # (Nex, L)
        upper = lp[None, :] >= lp[:, None]  # (a, b): b >= a
        out.append(torch.cumsum(torch.where(upper[None], m[:, None, :], 0.0), dim=-1))
    return torch.stack(out)


def partial_widths_cells(mi: MultiInputs, cells: list[tuple[int, int]],
                         device=None) -> dict[int, Tensor]:
    """`partial_widths` for many (J2, parity) cells of one mother bin at once: type ->
    (K, Nex, numJ+1, 2), row k equal to `partial_widths(mi, *cells[k])` up to the order of the
    sum over l' (all terms non-negative). Not for `flagfullhf`.

    `_residual_spins` depends on J2 only through `(J2 + parspin2) % 2`, and J2 = 2J + odd, so
    the residual spin grid and the masked rho0 are the same for every cell.

    TALYS: compound.f90:1 (compound)   -- iloop = 1
    Test: A-mult / SPEED0 golden
    """
    K = len(cells)
    j2 = torch.tensor([c[0] for c in cells], device=device)
    par = torch.tensor([c[1] for c in cells], device=device)
    jidx = torch.div(j2, 2, rounding_mode="floor")
    pidx = (par > 0).to(torch.int64)
    pprime = torch.tensor([-1, 1], device=device)
    pardif2 = (par[:, None] - pprime[None, :]).abs() // 2  # (K, 2)
    out: dict[int, Tensor] = {}
    for t, r in sorted(mi.residuals.items()):
        rho = torch.as_tensor(r.rho, dtype=DTYPE, device=device)  # (Nex, Jx, 2)
        irs2, valid = _residual_spins(r, cells[0][0] if K else mi.odd, device)
        rho = torch.where(valid & (rho >= 1.0e-20), rho, 0.0)
        if r.nlast == 0:
            rho = rho.clone()
            rho[0] = 0.0  # compound.f90:236 `if (nexout == 0 .and. NL == 0) cycle`
        nex = rho.shape[0]
        lmaxhf = torch.as_tensor(r.lmaxhf, device=device)
        j2min = (j2[:, None, None] - irs2[None]).abs()  # (K, Nex, Jx)
        j2plus = j2[:, None, None] + irs2[None]
        lbeg = torch.div((j2min - r.parspin2).abs(), 2, rounding_mode="floor")
        lend = torch.minimum(torch.div(j2plus + r.parspin2, 2, rounding_mode="floor"),
                             lmaxhf[None, :, None])
        if t == 0:
            L = mi.gammax + 1
            lp = torch.arange(L, device=device)
            inrange = (lp >= lbeg[..., None]) & (lp <= lend[..., None])  # (K, Nex, Jx, L)
            tg = torch.as_tensor(r.tgam, dtype=DTYPE, device=device)  # (Nex, L, 2, Jx, 2)
            tgk = tg[:, :L, :, jidx, pidx].permute(3, 0, 1, 2)  # (K, Nex, L, irad)
            irad = 1 - ((lp % 2)[None, None, :] - pardif2[:, :, None]).abs()  # (K, 2, L)
            sel = torch.nn.functional.one_hot(irad.clamp(min=0), 2).to(DTYPE)  # (K, 2, L, 2)
            tl_p = (tgk[:, :, None, :, :] * sel[:, None]).sum(-1)  # (K, Nex, P', L)
            total = (tl_p[:, :, None, :, :] * inrange[:, :, :, None, :].to(DTYPE)).sum(-1)
        else:
            L = r.tl.shape[1]
            G = _lrange_sums(torch.as_tensor(r.tl, dtype=DTYPE, device=device), L)
            ok = (lend >= lbeg) & (lbeg <= L - 1)
            a = lbeg.clamp(0, L - 1)
            b = lend.clamp(0, L - 1)
            n_ax = torch.arange(nex, device=device)[None, :, None]
            total = torch.zeros(K, nex, rho.shape[1], 2, dtype=DTYPE, device=device)
            for q in (0, 1):
                c = pardif2[:, q][:, None, None].expand_as(a)
                g = G[c, n_ax.expand_as(a), a, b]
                total[..., q] = torch.where(ok, g, 0.0)
            total = float(r.parspin2 + 1) * total
        out[t] = rho[None] * total
    return out


def _compound_decay_cells(mi: MultiInputs, device=None) -> ContinuumFeeding:
    """`compound_decay` with every (J, parity) cell of the mother bin decayed in one tensor call.

    Same selection, special cases and bookkeeping as the per-cell loop; the per-cell feedings are
    summed over cells with one tensor sum instead of one addition per cell.

    TALYS: compound.f90:1 (compound)
    Test: A-mult / SPEED0 golden
    """
    dpop = {t: torch.zeros((r.maxex + 1, NUMJ + 1, 2), dtype=DTYPE, device=device)
            for t, r in mi.residuals.items()}
    mcontrib = {t: torch.zeros(r.maxex + 1, dtype=DTYPE, device=device)
                for t, r in mi.residuals.items()}
    fisfeed = torch.zeros((), dtype=DTYPE, device=device)
    leftover = torch.zeros((), dtype=DTYPE, device=device)
    denoms: dict[tuple[int, int], Tensor] = {}
    xspop = torch.as_tensor(mi.xspop_mother_mb, dtype=DTYPE, device=device)
    popeps_b = mi.popeps_mb / (5 * max(mi.maxj_mother, 1)) * 0.5
    cells, pops, fis = [], [], []
    for parity in (-1, 1):
        for J in range(0, mi.maxj_mother + 1):
            J2 = 2 * J + mi.odd
            pop = xspop[J, _pidx(parity)]
            if float(pop.detach()) < popeps_b:
                continue
            cells.append((J2, parity))
            pops.append(pop)
            fis.append(fission_width(mi, J2, parity, device))
    if not cells:
        return ContinuumFeeding(dpop, fisfeed, mcontrib, leftover, denoms)
    enum = partial_widths_cells(mi, cells, device)
    fis_t = torch.stack(fis)
    sums = {t: v.sum((1, 2, 3)) for t, v in enum.items()}
    if 6 in enum:  # compound.f90:222
        others = [s == 0.0 for k, s in sums.items() if k != 6]
        dead = fis_t == 0.0
        for o in others:
            dead = dead & o
        if bool(dead.any()):
            enum[6] = torch.where(dead[:, None, None, None], 0.0, enum[6])
            sums[6] = enum[6].sum((1, 2, 3))
    denom = fis_t + sum(sums.values())
    pop_t = torch.stack(pops)
    for k, c in enumerate(cells):
        denoms[c] = denom[k]
    live = (pop_t != 0.0) & (denom != 0.0)
    feed = torch.where(live, (1.0 - mi.dmulti) * pop_t / torch.where(live, denom, 1.0), 0.0)
    for t, v in enum.items():
        fv = feed[:, None, None, None] * v
        dpop[t] = dpop[t] + fv.sum(0)
        mcontrib[t] = mcontrib[t] + fv.sum((0, 2, 3))
    fisfeed = fisfeed + (feed * fis_t).sum()
    trapped = (pop_t != 0.0) & (denom == 0.0)
    if bool(trapped.any()):
        # compound.f90:404-419, exactly as in the per-cell loop
        nl = mi.nlast_mother
        r0 = mi.residuals.get(0)
        for k in torch.nonzero(trapped).flatten().tolist():
            pop = pop_t[k]
            leftover = leftover + pop
            if r0 is not None and nl >= 0:
                share = pop / (nl + 1.0)
                mask = torch.zeros_like(dpop[0])
                for nexout in range(min(nl, r0.maxex) + 1):
                    mask[nexout, int(r0.jdis2[nexout]) // 2, _pidx(int(r0.parlev[nexout]))] = 1.0
                dpop[0] = dpop[0] + mask * share
    return ContinuumFeeding(dpop, fisfeed, mcontrib, leftover, denoms)


@lru_cache(maxsize=256)
def _spin_l_mask(odd: int, parspin2: int, nj: int, L: int, device=None) -> Tensor:
    """`lbeg <= l' <= lend` before the `lmaxhf` cap, for every mother J (0..nj-1, J2 = 2J + odd),
    continuum residual spin index Ir (Irspin2 = 2 Ir + (J2 + parspin2) % 2) and l'. Bool
    (nj, numJ+1, L). Everything else in the selection rules is the residual bin's.

    TALYS: compound.f90:1 (compound)
    Test: A-mult / SPEED0 golden
    """
    j2 = 2 * torch.arange(nj, device=device) + odd
    irs2 = 2 * torch.arange(NUMJ + 1, device=device) + (odd + parspin2) % 2
    j2min = (j2[:, None] - irs2[None, :]).abs()
    lbeg = torch.div((j2min - parspin2).abs(), 2, rounding_mode="floor")
    lend = torch.div(j2[:, None] + irs2[None, :] + parspin2, 2, rounding_mode="floor")
    lp = torch.arange(L, device=device)
    return (lp >= lbeg[..., None]) & (lp <= lend[..., None])


def _compound_decay_factored(mi: MultiInputs, device=None) -> ContinuumFeeding | None:
    """`compound_decay` with the sum over the mother's (J, parity) cells moved inside the sum
    over l'. Returns None when the inputs do not have the structure this relies on (a photon
    transmission that depends on the mother's J or parity, or flagfullhf), and the caller then
    takes the per-cell path.

    Per exit type, a cell (J, P) reaches residual state (nexout, Ir, P') through
    `sum_l' [lbeg(J, Ir) <= l' <= lend(J, Ir)] [l' <= lmaxhf(nexout)] T_c(nexout, l')`, with
    c = |P - P'| / 2 selecting the l' parity (particles) or the E/M radiation (photons). The
    first bracket is `_spin_l_mask`, independent of the bin; the rest is independent of the
    cell. So the denominators are `mask . R` with `R = sum_nexout rho0 * T`, and the feeding is
    `rho0 * sum_l' T * (mask . feed)`. Discrete residual levels carry their own spin and are
    summed the same way over their few rows. Every term is non-negative, so reordering the sums
    moves results by rounding only.

    TALYS: compound.f90:1 (compound)
    Test: A-mult / SPEED0 golden
    """
    if mi.flagfullhf:
        return None
    nj = mi.maxj_mother + 1
    xspop = torch.as_tensor(mi.xspop_mother_mb, dtype=DTYPE, device=device)
    popeps_b = mi.popeps_mb / (5 * max(mi.maxj_mother, 1)) * 0.5
    cells, pops, fis = [], [], []
    for parity in (-1, 1):
        for J in range(0, nj):
            J2 = 2 * J + mi.odd
            pop = xspop[J, _pidx(parity)]
            if float(pop.detach()) < popeps_b:
                continue
            cells.append((J, _pidx(parity)))
            pops.append(pop)
            fis.append(fission_width(mi, J2, parity, device))
    dpop = {t: torch.zeros((r.maxex + 1, NUMJ + 1, 2), dtype=DTYPE, device=device)
            for t, r in mi.residuals.items()}
    mcontrib = {t: torch.zeros(r.maxex + 1, dtype=DTYPE, device=device)
                for t, r in mi.residuals.items()}
    zero = torch.zeros((), dtype=DTYPE, device=device)
    if not cells:
        return ContinuumFeeding(dpop, zero.clone(), mcontrib, zero.clone(), {})
    ir = torch.arange(NUMJ + 1, device=device)
    prep = {}
    for t, r in sorted(mi.residuals.items()):
        nex = r.maxex + 1
        if t == 0:
            L = mi.gammax + 1
            tg = torch.as_tensor(r.tgam, dtype=DTYPE, device=device)[:, :L]  # (Nex, L, 2, Jx, 2)
            if not bool((tg == tg[..., :1, :1]).all()):
                return None
            tg = tg[..., 0, 0]  # (Nex, L, irad)
            lp = torch.arange(L, device=device)
            # irad = 1 - |mod(l', 2) - c| (compound.f90:270)
            T = torch.stack([tg[:, lp, 1 - (lp % 2)], tg[:, lp, lp % 2]])  # (c, Nex, L)
            sfac = 1.0
        else:
            tl = torch.as_tensor(r.tl, dtype=DTYPE, device=device)  # (Nex, L)
            L = tl.shape[1]
            lp = torch.arange(L, device=device)
            T = torch.stack([torch.where(lp % 2 == c, tl, 0.0) for c in (0, 1)])
            sfac = float(r.parspin2 + 1)
        lmaxhf = torch.as_tensor(r.lmaxhf, device=device)
        T = torch.where(lp[None, None, :] <= lmaxhf[None, :, None], T, 0.0)
        rho = torch.as_tensor(r.rho, dtype=DTYPE, device=device)  # (Nex, Jx, 2)
        irs2, valid = _residual_spins(r, 2 * cells[0][0] + mi.odd, device)
        rho = torch.where(valid & (rho >= 1.0e-20), rho, 0.0)
        if r.nlast == 0:
            rho = rho.clone()
            rho[0] = 0.0  # compound.f90:236
        disc = torch.arange(nex, device=device) <= r.nlast
        rho_c = torch.where(disc[:, None, None], 0.0, rho)
        M = _spin_l_mask(mi.odd, r.parspin2, nj, L, device).to(DTYPE)  # (nj, Jx, L)
        R = torch.einsum("nip,cnl->cipl", rho_c, T)  # (c, Jx, P', L)
        # D[J, P] = sfac * sum_P' sum_{Ir, l} M R[c = (P != P')]
        MR = torch.einsum("jil,cipl->jcp", M, R)  # (nj, c, P')
        D = torch.stack([MR[:, 0, 0] + MR[:, 1, 1], MR[:, 1, 0] + MR[:, 0, 1]], dim=1) * sfac
        nd = min(r.nlast, r.maxex) + 1
        dd = None
        if nd > 0:
            jd2 = torch.as_tensor(r.jdis2[:nd], device=device)
            j2 = 2 * torch.arange(nj, device=device) + mi.odd
            lbeg = torch.div(((j2[:, None] - jd2[None, :]).abs() - r.parspin2).abs(), 2,
                             rounding_mode="floor")
            lend = torch.div(j2[:, None] + jd2[None, :] + r.parspin2, 2, rounding_mode="floor")
            lpd = torch.arange(L, device=device)
            Md = ((lpd >= lbeg[..., None]) & (lpd <= lend[..., None])).to(DTYPE)  # (nj, nd, L)
            tot_d = torch.einsum("jnl,cnl->jcn", Md, T[:, :nd])  # (nj, c, nd)
            ird = torch.div(jd2, 2, rounding_mode="floor").clamp(0, NUMJ)
            pd = torch.as_tensor((r.parlev[:nd] > 0).astype(int), device=device)
            rho_d = rho[:nd][torch.arange(nd, device=device), ird, pd]  # (nd,)
            # c = (P != P'_n): for mother parity index p, c = (p != pd)
            cmat = (torch.arange(2, device=device)[:, None] != pd[None, :]).to(torch.int64)
            tot_dp = torch.stack([tot_d[:, cmat[p], torch.arange(nd, device=device)]
                                  for p in (0, 1)], dim=1)  # (nj, P, nd)
            D = D + sfac * torch.einsum("jpn,n->jp", tot_dp, rho_d)
            dd = (ird, pd, rho_d, tot_dp)
        prep[t] = (T, rho_c, M, D, dd, sfac)
    jj = torch.tensor([c[0] for c in cells], device=device)
    pp = torch.tensor([c[1] for c in cells], device=device)
    fis_t = torch.stack(fis)
    pop_t = torch.stack(pops)
    sums = {t: v[3][jj, pp] for t, v in prep.items()}
    if 6 in sums:  # compound.f90:222
        dead = fis_t == 0.0
        for k, sv in sums.items():
            if k != 6:
                dead = dead & (sv == 0.0)
        if bool(dead.any()):
            sums[6] = torch.where(dead, 0.0, sums[6])
    else:
        dead = torch.zeros_like(fis_t, dtype=torch.bool)
    denom = fis_t + sum(sums.values())
    denoms = {(2 * c[0] + mi.odd, 2 * c[1] - 1): denom[k] for k, c in enumerate(cells)}
    live = (pop_t != 0.0) & (denom != 0.0)
    feed_c = torch.where(live, (1.0 - mi.dmulti) * pop_t / torch.where(live, denom, 1.0), 0.0)
    feed = torch.zeros((nj, 2), dtype=DTYPE, device=device)
    feed[jj, pp] = feed_c
    for t, (T, rho_c, M, D, dd, sfac) in prep.items():
        f = feed
        if t == 6 and bool(dead.any()):
            f = feed.clone()
            f[jj[dead], pp[dead]] = 0.0
        # V_c(Ir, P', l) = sum_J M(J, Ir, l) feed(J, P) with c = (P != P')
        V0 = torch.einsum("jil,jq->iql", M, f)  # P = P'
        V1 = torch.einsum("jil,jq->iql", M, f.flip(1))  # P = -P'
        TV = (torch.einsum("nl,iql->niq", T[0], V0) + torch.einsum("nl,iql->niq", T[1], V1))
        dp = sfac * rho_c * TV
        if dd is not None:
            ird, pd, rho_d, tot_dp = dd
            nd = rho_d.shape[0]
            fd = torch.einsum("jpn,jp->n", tot_dp, f)
            dp = dp.index_put((torch.arange(nd, device=device), ird, pd),
                              sfac * rho_d * fd, accumulate=True)
        dpop[t] = dp
        mcontrib[t] = dp.sum((1, 2))
    fisfeed = (feed_c * fis_t).sum()
    leftover = zero.clone()
    trapped = (pop_t != 0.0) & (denom == 0.0)
    if bool(trapped.any()):
        nl = mi.nlast_mother
        r0 = mi.residuals.get(0)
        for k in torch.nonzero(trapped).flatten().tolist():
            pop = pop_t[k]
            leftover = leftover + pop
            if r0 is not None and nl >= 0:
                share = pop / (nl + 1.0)
                mask = torch.zeros_like(dpop[0])
                for nexout in range(min(nl, r0.maxex) + 1):
                    mask[nexout, int(r0.jdis2[nexout]) // 2, _pidx(int(r0.parlev[nexout]))] = 1.0
                dpop[0] = dpop[0] + mask * share
    return ContinuumFeeding(dpop, fisfeed, mcontrib, leftover, denoms)


def compound_decay(mi: MultiInputs, device=None) -> ContinuumFeeding:
    """Feeding of every daughter state [mb] from the population of one mother bin, summed over the
    compound (J, parity) and vectorised over its exit energies, spins and parities.

    Contract deviation (reported; CONTRACT.md is T0's file): §5 gives
    `compound_decay(state) -> feeding`; `state` here is `MultiInputs`, the injected arrays
    compound.f90 reads, exactly as `compound_target` takes `CompoundInputs`.

    TALYS: compound.f90:1 (compound)
    Test: A-mult
    """
    if not mi.flagfullhf:
        f = _compound_decay_factored(mi, device)
        return f if f is not None else _compound_decay_cells(mi, device)
    dpop = {t: torch.zeros((r.maxex + 1, NUMJ + 1, 2), dtype=DTYPE, device=device)
            for t, r in mi.residuals.items()}
    mcontrib = {t: torch.zeros(r.maxex + 1, dtype=DTYPE, device=device)
                for t, r in mi.residuals.items()}
    fisfeed = torch.zeros((), dtype=DTYPE, device=device)
    leftover = torch.zeros((), dtype=DTYPE, device=device)
    denoms: dict[tuple[int, int], Tensor] = {}
    xspop = torch.as_tensor(mi.xspop_mother_mb, dtype=DTYPE, device=device)
    # multiple.f90:560 popepsB, the flux cut below which a (bin, J, parity) is not decayed at all
    popeps_b = mi.popeps_mb / (5 * max(mi.maxj_mother, 1)) * 0.5
    for parity in (-1, 1):
        for J in range(0, mi.maxj_mother + 1):
            J2 = 2 * J + mi.odd  # multiple.f90:576
            pop = xspop[J, _pidx(parity)]
            if float(pop.detach()) < popeps_b:
                continue
            fis = fission_width(mi, J2, parity, device)
            enum = partial_widths(mi, J2, parity, device)
            if 6 in enum and float(fis.detach()) == 0.0 and all(
                float(v.sum().detach()) == 0.0 for k, v in enum.items() if k != 6
            ):
                enum[6] = torch.zeros_like(enum[6])  # compound.f90:222
            denom = fis + sum(v.sum() for v in enum.values())
            denoms[(J2, parity)] = denom
            if float(pop.detach()) == 0.0:
                continue
            if float(denom.detach()) == 0.0:
                # compound.f90:404-419: nothing is open, so the flux is not trapped in the bin --
                # it is spread equally over the compound nucleus's OWN discrete levels. Those are
                # the type-0 residual (Zix, Nix) == (Zcomp, Ncomp), so they land in dpop[0].
                leftover = leftover + pop
                nl = mi.nlast_mother
                r0 = mi.residuals.get(0)
                if r0 is not None and nl >= 0:
                    share = pop / (nl + 1.0)
                    mask = torch.zeros_like(dpop[0])
                    for nexout in range(min(nl, r0.maxex) + 1):
                        mask[nexout, int(r0.jdis2[nexout]) // 2,
                             _pidx(int(r0.parlev[nexout]))] = 1.0
                    dpop[0] = dpop[0] + mask * share
                continue
            feed = (1.0 - mi.dmulti) * pop / denom
            for t, v in enum.items():
                dpop[t] = dpop[t] + feed * v
                mcontrib[t] = mcontrib[t] + (feed * v).sum((1, 2))
            fisfeed = fisfeed + feed * fis
    return ContinuumFeeding(dpop, fisfeed, mcontrib, leftover, denoms)
