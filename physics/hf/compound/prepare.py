"""Preparation of the compound-nucleus decay: the exit-channel transmission sums per (J, parity),
the channel lists the WFC needs, and the injected inputs they are built from.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T9 (physics/hf/CONTRACT.md §7). Acceptance test: A-cn1 (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    compoundinit.f90:1 (compoundinit)
    compprepare.f90:1 (compprepare)
    widthprepare.f90:1 (widthprepare)
    densprepare.f90:1 (densprepare)  -- consumed, not recomputed: see below

Inputs. `compprepare` reads four arrays that `densprepare` fills: the bin-integrated level density
`rho0(Ir, P, type, nexout)`, the transmission coefficients interpolated onto each residual level or
bin `Tjlnex(l, updown, type, nexout)` (with the incident channel's exact `Tjlinc` put in place of
the target ground state), the gamma transmission `Tgam(l, nexout, irad, J, P)` and, for fissile
compound nuclei, `tfis`/`tfisA`/`rhofisA`. Computing those is T5/T6/T7/T11 work; per the
contract's injection rule this module takes them as data. `CompoundInputs` is that data for one
case, and `load_cn_dump` reads it from the instrumented TALYS run (compound/cn_reference.py).
When the upstream ports land, an adapter that builds `CompoundInputs` from `Transmission`,
`LevelDensity` and `GammaTransmission` replaces the loader; nothing downstream changes.

Contract deviation (reported, CONTRACT.md is not T9's file): §5 lists
`exit_channel_sums(Zcomp, Ncomp, J2, parity, trans, rho, tgam, tfis, bins, options)`. Here the
upstream objects are bundled in `CompoundInputs`, because densprepare's interpolated arrays are
the true interface and none of the upstream objects exist yet.

Selection rules, exactly as the Fortran loops enumerate them (compprepare.f90, comptarget.f90):

* incident (j, l): jj2 in |J2 - 2I|..J2 + 2I step 2; l2 in |jj2 - s2|..min(jj2 + s2, 2 lmaxinc)
  step 2; l parity = |P_target - P|/2; updown = (jj2 - l2)/spin2.
* residual spin: discrete level -> Irspin2 = int(2 jdis), Ir = Irspin2/2; continuum ->
  Irspin2 = mod(J2 + s2', 2) .. min(J2 + s2' + 2 lmaxhf, 2 maxJ) step 2 (so for half-integer
  residuals the last index maxJ is never reached -- a TALYS quirk kept on purpose).
* exit (j', l'): jj2' in |J2 - Irspin2|..J2 + Irspin2 step 2; l2' in |jj2' - s2'|..min(jj2' + s2',
  2 lmaxhf) step 2, l2' >= 2 for photons; particles need mod(l', 2) = |P - P'|/2; photons are E
  (irad = 1) when mod(l', 2) = |P - P'|/2, else M.
* channels with rho0 < 1e-20 are skipped.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import re

import numpy as np
import torch
from torch import Tensor

from physics.hf.core.tensors import DTYPE

NUMJ = 40
PARTICLES = ("gamma", "neutron", "proton", "deuteron", "triton", "helium-3", "alpha")


@dataclass
class ResidualChannels:
    """Everything compprepare needs about one exit type (0 = gamma, 1..6 = n p d t h a)."""

    type: int
    zix: int
    nix: int
    maxex: int
    nlast: int  # Nlast(Zix, Nix, 0): last discrete level
    spin2: int  # spin2(type): 1 for photons and alphas (constants.f90:171)
    parspin2: int  # int(2 parspin(type))
    lmaxhf: np.ndarray  # (Nex,) int
    maxj: np.ndarray  # (Nex,) int
    ex_mev: np.ndarray  # (Nex,)
    parlev: np.ndarray  # (Nex,) int, 0 for continuum bins
    jdis2: np.ndarray  # (Nex,) int(2 jdis) for discrete levels, -1 for continuum
    rho: np.ndarray  # (Nex, numJ+1, 2) rho0, parity axis (-1, +1)
    tjl: np.ndarray | None = None  # (Nex, L, 3) Tjlnex, updown axis (-1, 0, +1); particles
    tgam: np.ndarray | None = None  # (Nex, gammax+1, 2, numJ+1, 2) Tgam[l, irad, J, P]; photons
    tl: np.ndarray | None = None  # (Nex, L) Tlnex, the spin-averaged T (flagfullhf off; continuum)
    dex_mev: np.ndarray | None = None  # (Nex,) deltaEx
    sep_mev: float = 0.0  # S(Zcomp, Ncomp, type)


@dataclass
class CompoundInputs:
    """Injected inputs of comptarget.f90 for one case (one target at one incident energy)."""

    e_inc_mev: float
    cnfactor_mb: float  # CNfactor after compnorm (pi/k^2 /(2s+1)(2I+1) * cfratio/norm) [mb]
    xsflux_mb: float
    xsreacinc_mb: float
    j2beg: int
    j2end: int
    targetspin2: int
    target_parity: int
    lmaxinc: int
    k0: int
    ltarget: int
    wmode: int
    wfcfactor: int
    gammax: int
    nfisbar: int
    flagwidth: bool
    flagfission: bool
    tjlinc: np.ndarray  # (lmaxinc+1, 3)
    exinc_mev: float = 0.0  # Exinc, the mother bin densprepare builds its grid around
    dexinc_mev: float = 0.0  # dExinc
    fnorm: np.ndarray = field(default_factory=lambda: np.ones(8))  # Fnorm(-1..6), index type+1
    residuals: dict[int, ResidualChannels] = field(default_factory=dict)
    tfis: dict[tuple[int, int], float] = field(default_factory=dict)  # (J2, P) -> tfis
    tfisA: dict[tuple[int, int], np.ndarray] = field(default_factory=dict)  # -> (numhill+1,)
    rhofisA: dict[tuple[int, int], np.ndarray] = field(default_factory=dict)
    # reference outputs carried by the same dump (not inputs; used only by tests)
    denomhf: dict[tuple[int, int], float] = field(default_factory=dict)
    ref_pop_mb: dict[int, np.ndarray] = field(default_factory=dict)  # type -> (Nex, numJ+1, 2)
    ref_xsbinary_mb: np.ndarray | None = None  # (8,) types -1..6
    # what binary.f90 adds to the compound population before writing binE*.out (for scoring only)
    xsdirdisc_mb: dict[tuple[int, int], float] = field(default_factory=dict)  # (type, level)
    preeqpopex_mb: dict[tuple[int, int], float] = field(default_factory=dict)  # (type, bin)
    popeps_mb: float = 0.0
    flagpreeq: bool = False


def _pidx(p: int) -> int:
    return 0 if p == -1 else 1


def _split_dump_fields(rest: str) -> list[str]:
    """Split one cndump record's payload into fields.

    `es17.9e3` is exactly 17 characters wide for a NEGATIVE value (sign + 1 + '.' + 9 digits +
    'E' + sign + 3 digits) and 16 plus a leading blank for a positive one, so two adjacent fields
    run together the moment the second is negative: Pb-208's TYPE line prints
    `0.000000000E+000-2.248526176E+000` with no separator. Whitespace splitting then loses a
    whole column. A `-` that directly follows a digit can only be the sign of the next field --
    an exponent's sign always follows `E` -- so re-introduce the separator there.
    """
    return re.sub(r"(?<=[0-9])-", " -", rest).split()


def load_cn_dump(path: str | Path) -> list[CompoundInputs]:
    """Parse cn_inputs.txt written by talys_instrument/cndump.f90 into one CompoundInputs per
    incident energy at which comptarget ran.

    TALYS: comptarget.f90:1 (comptarget) -- the arrays it holds after densprepare
    Test: A-cn1
    """
    cases: list[CompoundInputs] = []
    cur: CompoundInputs | None = None
    nexinfo: dict[int, list] = {}
    rows: dict[str, list] = {}

    def finish():
        if cur is None:
            return
        for t, info in nexinfo.items():
            meta = info[0]
            nex = meta["maxex"] + 1
            r = ResidualChannels(
                type=t, zix=meta["zix"], nix=meta["nix"], maxex=meta["maxex"],
                nlast=meta["nl"], spin2=meta["spin2"], parspin2=meta["parspin2"],
                lmaxhf=np.zeros(nex, int), maxj=np.zeros(nex, int), ex_mev=np.zeros(nex),
                parlev=np.zeros(nex, int), jdis2=-np.ones(nex, int),
                rho=np.zeros((nex, NUMJ + 1, 2)),
                dex_mev=np.zeros(nex), sep_mev=meta["sep"],
            )
            for n, lmh, mj, ex, jd, dex in info[1]:
                r.lmaxhf[n], r.maxj[n], r.ex_mev[n], r.dex_mev[n] = lmh, mj, ex, dex
                if n <= r.nlast:
                    r.jdis2[n] = int(2.0 * np.float32(jd))
            cur.residuals[t] = r
        for tt, n, p in rows.get("LEV", []):
            cur.residuals[tt].parlev[n] = p
        for tt, n, ir, p, v in rows.get("RHO", []):
            cur.residuals[tt].rho[n, ir, _pidx(p)] = v
        lmax_all = {t: max(1, int(r.lmaxhf.max()) + 1) for t, r in cur.residuals.items()}
        for t, r in cur.residuals.items():
            if t == 0:
                r.tgam = np.zeros((r.maxex + 1, cur.gammax + 1, 2, NUMJ + 1, 2))
            else:
                r.tjl = np.zeros((r.maxex + 1, lmax_all[t], 3))
        for tt, n, l, irad, vals in rows.get("TGAM", []):
            cur.residuals[tt].tgam[n, l, irad] = np.asarray(vals).reshape(2, NUMJ + 1).T
        for tt, n, l, vals in rows.get("TJL", []):
            r = cur.residuals[tt]
            if l >= r.tjl.shape[1]:
                r.tjl = np.concatenate([r.tjl, np.zeros((r.tjl.shape[0], l + 1 - r.tjl.shape[1], 3))], 1)
            r.tjl[n, l] = vals
        for tt, n, ir, p, v in rows.get("POP", []):
            if tt not in cur.ref_pop_mb:
                cur.ref_pop_mb[tt] = np.zeros((cur.residuals[tt].maxex + 1, NUMJ + 1, 2))
            cur.ref_pop_mb[tt][n, ir, _pidx(p)] = v
        cases.append(cur)

    with open(path) as f:
        for line in f:
            tag, rest = line[:5].strip(), _split_dump_fields(line[5:])
            if tag == "EINC":
                finish()
                cur, nexinfo, rows = None, {}, {}
                e = float(rest[0])
                cur = CompoundInputs(
                    e_inc_mev=e, cnfactor_mb=0, xsflux_mb=0, xsreacinc_mb=0, j2beg=0, j2end=0,
                    targetspin2=0, target_parity=1, lmaxinc=0, k0=1, ltarget=0, wmode=0,
                    wfcfactor=1, gammax=2, nfisbar=0, flagwidth=False, flagfission=False,
                    tjlinc=np.zeros((0, 3)),
                )
            elif tag == "SCAL":
                cur.cnfactor_mb, cur.xsflux_mb, cur.xsreacinc_mb = map(float, rest[:3])
                cur.exinc_mev, cur.dexinc_mev = float(rest[3]), float(rest[4])
            elif tag == "INTS":
                v = list(map(int, rest))
                (cur.j2beg, cur.j2end, cur.targetspin2, cur.target_parity, cur.lmaxinc, cur.k0,
                 cur.ltarget, cur.wmode, cur.wfcfactor, cur.gammax, _nmold, cur.nfisbar) = v
                cur.tjlinc = np.zeros((cur.lmaxinc + 1, 3))
            elif tag == "SCL2":
                cur.popeps_mb, cur.flagpreeq = float(rest[0]), rest[1] == "T"
            elif tag == "XSDD":
                cur.xsdirdisc_mb[(int(rest[0]), int(rest[1]))] = float(rest[2])
            elif tag == "PEPX":
                cur.preeqpopex_mb[(int(rest[0]), int(rest[1]))] = float(rest[2])
            elif tag == "FLAG":
                cur.flagwidth, cur.flagfission = rest[0] == "T", rest[1] == "T"
            elif tag == "FNRM":
                cur.fnorm = np.asarray(list(map(float, rest[:8])))
            elif tag == "TINC":
                cur.tjlinc[int(rest[0])] = list(map(float, rest[1:4]))
            elif tag == "TYPE":
                t = int(rest[0])
                nexinfo[t] = [dict(zix=int(rest[1]), nix=int(rest[2]), maxex=int(rest[3]),
                                   nl=int(rest[4]), spin2=int(rest[5]),
                                   parspin2=int(2.0 * float(rest[6])),
                                   sep=float(rest[7])), []]
            elif tag == "NEX":
                t, n, lmh, mj = map(int, rest[:4])
                nexinfo[t][1].append(
                    (n, lmh, mj, float(rest[4]), float(rest[6]), float(rest[5])))
            elif tag == "LEV":
                rows.setdefault("LEV", []).append(tuple(map(int, rest)))
            elif tag == "RHO":
                rows.setdefault("RHO", []).append((*map(int, rest[:4]), float(rest[4])))
            elif tag == "TGAM":
                rows.setdefault("TGAM", []).append((*map(int, rest[:4]), list(map(float, rest[4:]))))
            elif tag == "TJL":
                rows.setdefault("TJL", []).append((*map(int, rest[:3]), list(map(float, rest[3:6]))))
            elif tag == "JP":
                cur.denomhf[(int(rest[0]), int(rest[1]))] = float(rest[3])
            elif tag == "TFIS":
                cur.tfis[(int(rest[0]), int(rest[1]))] = float(rest[2])
            elif tag == "TFHA":
                key = (int(rest[0]), int(rest[1]))
                cur.tfisA.setdefault(key, np.zeros(21))[int(rest[2])] = float(rest[3])
                cur.rhofisA.setdefault(key, np.zeros(21))[int(rest[2])] = float(rest[4])
            elif tag == "XSBI":
                cur.ref_xsbinary_mb = np.array(list(map(float, rest)))
            elif tag == "POP":
                rows.setdefault("POP", []).append((*map(int, rest[:4]), float(rest[4])))
    finish()
    return cases


# ------------------------------------------------------------------------------------------------
# selection rules as tensors
# ------------------------------------------------------------------------------------------------


@dataclass
class ExitBlock:
    """One exit type's contribution to a (J2, P) block, grouped by (nexout, l', updown)."""

    type: int
    t: Tensor  # (Nex, L, 3) transmission per group (photons: (Nex, L, 2) per irad)
    weight: Tensor  # (Nex, Ir, 2, L, 3|2) rho0 * allowed(Ir, P', l', updown|irad)
    width: Tensor  # (Nex,) sum over the bin/level of rho * T  -> part of denomhf


def _residual_spin2(r: ResidualChannels, J2: int, device) -> tuple[Tensor, Tensor]:
    """Irspin2 of shape (Nex, numJ+1) and `valid` of shape (Nex, numJ+1, 2): the residual
    (spin, parity) cells the loops visit.

    Discrete levels also carry exactly one PARITY, `parlev` (compound.f90:243-246 sets
    `Pprimebeg = Pprimeend = parlev`). That matters: `rho0` is a scratch array TALYS refills per
    residual without clearing, so a level's own `Ir` row can still hold a stale non-zero value at
    the opposite parity from an earlier nucleus or bin. TALYS never reads it; a mask on `Ir`
    alone does, and then adds a whole phantom exit channel.

    The `comptarget` dumps show no such collision (rho0 is freshly built for the target's own
    residuals), so this guard is dormant on A-cn1/A-cn2 -- but it is what compound.f90 does, and
    the same mask in `continuum._residual_spins` is load-bearing for A-mult.

    TALYS: compprepare.f90:1 (compprepare)
    Test: A-cn1
    """
    nex = r.maxex + 1
    ir = torch.arange(NUMJ + 1, device=device)
    j2res = J2 + r.parspin2
    base = j2res % 2
    irs2 = (2 * ir + base)[None, :].expand(nex, -1).clone()
    lmaxhf = torch.as_tensor(r.lmaxhf, device=device)
    maxj = torch.as_tensor(r.maxj, device=device)
    top = torch.minimum(j2res + 2 * lmaxhf, 2 * maxj)[:, None]
    valid = irs2 <= top
    disc = torch.as_tensor(np.arange(nex) <= r.nlast, device=device)
    jd2 = torch.as_tensor(r.jdis2, device=device)
    # discrete levels: exactly one residual spin, Irspin2 = int(2 jdis), stored at Ir = Irspin2/2
    ir_disc = torch.div(jd2, 2, rounding_mode="floor")
    irs2 = torch.where(disc[:, None], jd2[:, None].expand(-1, NUMJ + 1), irs2)
    par_disc = torch.as_tensor((r.parlev > 0).astype(int), device=device)  # -1 -> 0, +1 -> 1
    disc_ok = (ir[None, :, None] == ir_disc[:, None, None]) & (
        torch.arange(2, device=device)[None, None, :] == par_disc[:, None, None])
    valid = torch.where(disc[:, None, None], disc_ok, valid[:, :, None].expand(-1, -1, 2))
    return irs2, valid


def anomalous_exit_mask(lo: Tensor, hi: Tensor, anom: Tensor, parspin2: int, spin2: int, L: int,
                        photon: bool) -> Tensor:
    """The exit (l', updown) channels compprepare/comptarget enumerate for |J2 - Irspin2| = `lo`,
    J2 + Irspin2 = `hi` and `anom = (lo + parspin2) % 2`, before the lmaxhf cap. Bool
    `lo.shape + (L, 3)`; photons fill the updown = 0 slot only.

    TALYS gives some discrete levels a 2J parity their mass number forbids: an ENSDF spin range
    such as Nb-95's (5/2:13/2)+ comes out as J = 3.0. Then `jj2'` runs over the wrong parity,
    `l2' = |jj2' - s2'| ..` is odd, and compprepare.f90 / comptarget.f90:595 read
    `lprime = l2prime / 2`, TRUNCATED, and `updown2 = (jj2' - l2') / spin2`. Reproduced here
    because the reference is TALYS: `l2' = 2 l' + anom` and `jj2' = l2' + updown * spin2`, with
    every other rule unchanged. The caller caps with `2 l' + anom <= 2 lmaxhf` (l2maxhf).
    For anom = 0 this is exactly the plain rule.

    TALYS: compprepare.f90:1 (compprepare), comptarget.f90:1 (comptarget)
    Test: tests/hf/test_open3m.py
    """
    dev = lo.device
    lp = torch.arange(L, device=dev)
    lo_, hi_, an = lo[..., None, None], hi[..., None, None], anom[..., None, None]
    l2p = 2 * lp[:, None] + an  # (..., L, 1)
    if photon:
        jj = l2p
        ok = (jj >= lo_) & (jj <= hi_) & ((jj - lo_) % 2 == 0) & (l2p >= 2)
        out = torch.zeros(ok.shape[:-1] + (3,), dtype=torch.bool, device=dev)
        out[..., 1] = ok[..., 0]
        return out
    dj = torch.tensor([-1, 0, 1], device=dev) * spin2  # (3,)
    jj2p = l2p + dj
    ok_s = ((dj.abs() <= parspin2) & ((dj - parspin2) % 2 == 0))
    ok_s = ok_s & (jj2p >= 0) & (l2p >= (jj2p - parspin2).abs())
    ok_j = (jj2p >= lo_) & (jj2p <= hi_) & ((jj2p - lo_) % 2 == 0)
    return ok_s & ok_j


def exit_channel_sums(inp: CompoundInputs, J2: int, parity: int, device=None) -> dict:
    """denomhf for (J2, parity) and the grouped exit channels of every type.

    Returns {"denom": Tensor scalar, "fiswidth": Tensor, "gamwidth": Tensor,
             "blocks": {type: ExitBlock}}.

    TALYS: compprepare.f90:1 (compprepare), widthprepare.f90:1 (widthprepare)
    Test: A-cn1
    """
    blocks: dict[int, ExitBlock] = {}
    denom = torch.zeros((), dtype=DTYPE, device=device)
    gamwidth = torch.zeros((), dtype=DTYPE, device=device)
    J = J2 // 2
    for t, r in inp.residuals.items():
        rho = torch.as_tensor(r.rho, dtype=DTYPE, device=device)  # (Nex, Jx, 2)
        irs2, valid = _residual_spin2(r, J2, device)
        rho = torch.where(valid & (rho >= 1.0e-20), rho, 0.0)
        pprime = torch.tensor([-1, 1], device=device)
        pardif2 = (parity - pprime).abs() // 2  # (2,)
        lmaxhf = torch.as_tensor(r.lmaxhf, device=device)
        # OPEN3M: TALYS's truncation into a discrete level of impossible 2J parity
        anom = (J2 + irs2 + r.parspin2) % 2  # (Nex, Jx); 0 on continuum rows
        anomalous = bool((anom * valid.any(-1)).any())
        if t == 0:
            L = inp.gammax + 1
            lp = torch.arange(L, device=device)
            jj2p = 2 * lp  # photons: parspin2 = 0 -> l2' = jj2'
            lo = (J2 - irs2).abs()  # (Nex, Jx)
            ok_j = (jj2p[None, None, :] >= lo[..., None]) & (jj2p[None, None, :] <= (J2 + irs2)[..., None]) \
                & ((jj2p[None, None, :] - lo[..., None]) % 2 == 0)
            ok_l = (lp >= 1)[None, None, :] & (2 * lp[None, None, :] <= 2 * lmaxhf[:, None, None])
            if anomalous:
                ok_j = anomalous_exit_mask(lo, J2 + irs2, anom, 0, 1, L, True)[..., 1]
                ok_l = 2 * lp[None, None, :] + anom[..., None] <= 2 * lmaxhf[:, None, None]
            ok = ok_j & ok_l  # (Nex, Jx, L)
            irad = (pardif2[:, None] == (lp % 2)[None, :]).long()  # (2, L): 1 = E, 0 = M
            tg = torch.as_tensor(r.tgam, dtype=DTYPE, device=device)  # (Nex, L, 2, Jx, 2)
            tgJ = tg[:, :, :, J, 0 if parity == -1 else 1]  # (Nex, L, 2)  Tgam(l, nex, irad, J, P)
            # weight per (Nex, Ir, P', L, irad)
            sel = torch.nn.functional.one_hot(irad, 2).to(DTYPE)  # (2, L, 2)
            w = rho[:, :, :, None, None] * ok[:, :, None, :, None].to(DTYPE) * sel[None, None, :, :, :]
            width = (w * tgJ[:, None, None, :, :]).sum((1, 2, 3, 4))
            blocks[t] = ExitBlock(t, tgJ, w, width)
            gamwidth = gamwidth + width.sum()
        else:
            L = r.tjl.shape[1]
            lp = torch.arange(L, device=device)
            ud = torch.tensor([-1, 0, 1], device=device)
            jj2p = 2 * lp[:, None] + ud[None, :] * r.spin2  # (L, 3)
            dj = jj2p - 2 * lp[:, None]
            ok_s = (dj.abs() <= r.parspin2) & ((dj - r.parspin2) % 2 == 0) & (jj2p >= 0)
            ok_s = ok_s & (2 * lp[:, None] >= (jj2p - r.parspin2).abs())
            lo = (J2 - irs2).abs()
            ok_j = (jj2p[None, None] >= lo[..., None, None]) & (jj2p[None, None] <= (J2 + irs2)[..., None, None]) \
                & ((jj2p[None, None] - lo[..., None, None]) % 2 == 0)  # (Nex, Jx, L, 3)
            ok_l = (2 * lp[None, :] <= 2 * lmaxhf[:, None])  # (Nex, L)
            ok = ok_j & ok_s[None, None] & ok_l[:, None, :, None]
            if anomalous:
                ok = anomalous_exit_mask(lo, J2 + irs2, anom, r.parspin2, r.spin2, L, False) & (
                    2 * lp[None, None, :] + anom[..., None] <= 2 * lmaxhf[:, None, None])[..., None]
            okp = (lp[None, :] % 2 == pardif2[:, None])  # (P', L)
            allowed = ok[:, :, None, :, :] & okp[None, None, :, :, None]  # (Nex, Jx, 2, L, 3)
            w = rho[:, :, :, None, None] * allowed.to(DTYPE)
            tt = torch.as_tensor(r.tjl, dtype=DTYPE, device=device)  # (Nex, L, 3)
            width = (w * tt[:, None, None]).sum((1, 2, 3, 4))
            blocks[t] = ExitBlock(t, tt, w, width)
        denom = denom + blocks[t].width.sum()
    fiswidth = torch.zeros((), dtype=DTYPE, device=device)
    if inp.flagfission and inp.nfisbar != 0:
        fiswidth = torch.as_tensor(inp.tfis.get((J2, parity), 0.0), dtype=DTYPE, device=device)
        denom = denom + fiswidth
    return {"denom": denom, "fiswidth": fiswidth, "gamwidth": gamwidth, "blocks": blocks}


def incident_channels(inp: CompoundInputs, J2: int, parity: int) -> tuple[list[tuple[int, int]], np.ndarray]:
    """[(l, updown)] and T for the incident (j, l) channels of (J2, parity), in TALYS's order.

    TALYS: comptarget.f90:1 (loops 130), compprepare.f90:1 (incident block)
    Test: A-cn1
    """
    s2 = inp.residuals[inp.k0].parspin2
    spin2 = inp.residuals[inp.k0].spin2
    pardif = abs(inp.target_parity - parity) // 2
    chans, t = [], []
    for jj2 in range(abs(J2 - inp.targetspin2), J2 + inp.targetspin2 + 1, 2):
        for l2 in range(abs(jj2 - s2), min(jj2 + s2, 2 * inp.lmaxinc) + 1, 2):
            l = l2 // 2
            if l % 2 != pardif:
                continue
            ud = (jj2 - l2) // spin2
            chans.append((l, ud))
            t.append(inp.tjlinc[l, ud + 1])
    if isinstance(inp.tjlinc, Tensor):  # DIFFPARAM: an optical override on the incident channel
        return chans, (torch.stack(t) if t else torch.zeros(0, dtype=DTYPE))
    return chans, np.asarray(t, dtype=float)


# ================================================================================================
# densprepare.f90 -- the adapter that BUILDS rho0 / Tjlnex / Tlnex / Tgam from T5, T6 and T7
# ================================================================================================
#
# Until now this module only *read* those four arrays from the instrumented dump (`load_cn_dump`).
# `densprepare` below computes them, which was the last seam between the component ports and a
# chained engine (T10's blocker). Faithful to densprepare.f90:
#
#   densprepare.f90:154-169   the mother bin Ex0plus/Ex0min and Efs
#   densprepare.f90:170-177   discfactor from Ncum/Ntop (missing-level correction above Ntop)
#   densprepare.f90:196-254   the four decay types and their Eout / Rboundary
#   densprepare.f90:264-281   rho0 for discrete levels (a weight) and for continuum bins
#   densprepare.f90:288-322   Tgam = 2 pi Egamma^(2l+1) f_XL(Egamma) Fnorm(0)
#   densprepare.f90:329-388   Tjlnex / Tlnex by pol2 interpolation of Tjl / Tl onto Eout
#   densprepare.f90:389-396   lmaxhf, its top-bin copy and lmaxhf(k0, 0) = lmaxinc
#
# Deviations, stated rather than silent:
#   * float64 throughout (contract §4.1); TALYS holds Eout, Rboundary, Egamma and the
#     interpolated T in `real(sgl)`. Measured against the dumps this is worth <= 6e-7 in |ln|,
#     orders under the tolerance of every quantity it feeds.
#   * TALYS never clears `rho0`, so a cell the loops do not fill keeps whatever an earlier
#     nucleus, bin or parity left there. This port returns a freshly zeroed array. Both
#     consumers (`_residual_spin2` here, `continuum._residual_spins`) mask to the cells TALYS
#     actually reads, so they agree everywhere it matters; `score_densprepare` compares exactly
#     those cells and counts the others as `stale_cells`.
#   * `strength 11` + `flagstrengthjp` (the (J, P)-dependent psf of densprepare.f90:310-318)
#     is not reachable: T7 does not port strength 11 and raises.

SPIN2 = (1, 1, 1, 2, 1, 1, 1)  # constants.f90:171 spin2(type) = max(1, int(2 * parspin(type)))
PARSPIN2 = (0, 1, 1, 2, 1, 1, 0)  # int(2 * parspin(type)); alpha and photon are 0


@dataclass
class DensResidual:
    """One exit type's residual nucleus, as densprepare.f90 sees it (T2 + T6 + core.grids)."""

    type: int
    zix: int
    nix: int
    A: int
    nlast: int  # Nlast(Zix, Nix, 0)
    ntop: int  # Ntop(Zix, Nix, 0)
    nexmax: int  # nexmax(type); = maxex(Zix, Nix) for the primary compound nucleus
    sep_mev: float  # S(Zcomp, Ncomp, type)
    ex_mev: np.ndarray  # (nexmax+1,) Ex
    dex_mev: np.ndarray  # (nexmax+1,) deltaEx
    maxj: np.ndarray  # (nexmax+1,) int maxJ
    parlev: np.ndarray  # (nexmax+1,) int, discrete levels only
    jdis: np.ndarray  # (nexmax+1,) float, discrete levels only
    rhogrid: np.ndarray  # (nexmax+1, numJ+1, 2) exgrid's bin-integrated rho, parity (-1, +1)
    # Ncum(Zix, Nix, NL) from densitycum (T6); read only when NL > Ntop. A Tensor under a
    # DIFFPARAM level-density override: densitycum integrates the level density, so it moves.
    ncum_nl: float | Tensor = 0.0


@dataclass
class DensTrans:
    """One particle type's emission-grid transmission coefficients (T5)."""

    egrid_mev: np.ndarray  # (maxen+1,) Fortran indexing, egrid[0] = 0
    ebegin: int
    eend: int
    maxen: int
    tjl: np.ndarray  # (maxen+1, L, 3) Tjl(type, nen, updown, l), updown axis (-1, 0, +1)
    tl: np.ndarray  # (maxen+1, L) Tl(type, nen, l)
    lmax: np.ndarray  # (maxen+1,) int lmax(type, nen)


@dataclass
class DensPrepareInputs:
    """Everything densprepare.f90 reads for one mother bin of compound nucleus (Zcomp, Ncomp)."""

    exinc_mev: float  # Exinc, the centre of the mother bin
    dexinc_mev: float  # dExinc
    s_n_mev: float  # S(Zcomp, Ncomp, 1); Efs = Exinc - S(.,.,1)
    gammax: int
    lmaxinc: int
    k0: int
    fnorm: np.ndarray  # (8,) Fnorm(-1..6); index type + 1
    residuals: dict[int, DensResidual]
    trans: dict[int, DensTrans]  # types 1..6
    gamma_strength: object = None  # f(efs_mev, egamma_mev, irad, l) -> float (T7's fstrength)
    primary: bool = True
    flagfullhf: bool = False
    transeps: float = 1.0e-8
    # SPEEDD: the gamma parameters behind `gamma_strength` when they are TALYS's defaults (no
    # override, nothing on a graph); `_tgam_rows` then evaluates the same fstrength through
    # compound.psf_fast, bit for bit
    gamma_params: object = None


def _eout_and_rboundary(
    inp: DensPrepareInputs, r: DensResidual, nexout: int
) -> tuple[float, float, float]:
    """`Eout`, `Rboundary` and the (possibly shifted) `Exout` of one residual bin or level.

    densprepare.f90 distinguishes four decays: primary -> discrete and primary -> continuum (no
    correction), continuum -> continuum (boundary-corrected, and with the top bin's centre moved
    to 0.5 (Ex0plus - S + Ex1min)), and continuum -> discrete, where the lowest mother bin that
    can reach the level can only partly do so -- that fraction is Rboundary.

    TALYS: densprepare.f90:1 (densprepare)
    Test: A-cn1
    """
    ex0plus = inp.exinc_mev + 0.5 * inp.dexinc_mev
    ex0min = inp.exinc_mev - 0.5 * inp.dexinc_mev
    ss = r.sep_mev
    dexhalf = 0.5 * float(r.dex_mev[nexout])
    exout = float(r.ex_mev[nexout])
    if inp.primary:
        return inp.exinc_mev - exout - ss, 1.0, exout
    if nexout > r.nlast:
        ex1min = exout - dexhalf
        if nexout == r.nexmax and r.type >= 1:
            ex1plus = ex0plus - ss
            exout = 0.5 * (ex1plus + ex1min)
        else:
            ex1plus = exout + dexhalf
        emax = ex0plus - ss - ex1min
        emin = ex0min - ss - ex1plus
        eout = 0.5 * (emin + emax)
        rboundary = 1.0
        if emin < 0.0:
            if eout > 0.0:
                rboundary = 1.0 - 0.5 * (emin / (0.5 * (emax - emin))) ** 2
            else:
                rboundary = 0.5 * (emax / (0.5 * (emax - emin))) ** 2
            emin = 0.0
        return 0.5 * (emin + emax), rboundary, exout
    exm = exout + ss
    if ex0min < exm <= ex0plus:
        return (0.5 * (ex0plus + exm) - ss - exout,
                (ex0plus - exm) / inp.dexinc_mev, exout)
    return inp.exinc_mev - ss - exout, 1.0, exout


def _eout_and_rboundary_rows(
    inp: DensPrepareInputs, r: DensResidual, nex: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """`_eout_and_rboundary` for residual rows 0..nex-1 at once: (Eout, Rboundary, Exout).

    Elementwise the same float64 arithmetic as the scalar function, branch by branch.

    TALYS: densprepare.f90:1 (densprepare)
    Test: A-cn1 / SPEED0 golden
    """
    ex = np.asarray(r.ex_mev[:nex], dtype=np.float64)
    if inp.primary:
        return inp.exinc_mev - ex - r.sep_mev, np.ones(nex), ex.copy()
    ex0plus = inp.exinc_mev + 0.5 * inp.dexinc_mev
    ex0min = inp.exinc_mev - 0.5 * inp.dexinc_mev
    ss = r.sep_mev
    n = np.arange(nex)
    dexhalf = 0.5 * np.asarray(r.dex_mev[:nex], dtype=np.float64)
    # continuum -> continuum (nexout > NL)
    ex1min = ex - dexhalf
    top = (n == r.nexmax) & (r.type >= 1)
    ex1plus = np.where(top, ex0plus - ss, ex + dexhalf)
    exout_c = np.where(top, 0.5 * (ex1plus + ex1min), ex)
    emax = ex0plus - ss - ex1min
    emin = ex0min - ss - ex1plus
    eout_mid = 0.5 * (emin + emax)
    below = emin < 0.0
    half = 0.5 * (emax - emin)
    with np.errstate(divide="ignore", invalid="ignore"):
        rb_c = np.where(below, np.where(eout_mid > 0.0, 1.0 - 0.5 * (emin / half) ** 2,
                                        0.5 * (emax / half) ** 2), 1.0)
    eout_c = 0.5 * (np.where(below, 0.0, emin) + emax)
    # continuum -> discrete (nexout <= NL)
    exm = ex + ss
    part = (ex0min < exm) & (exm <= ex0plus)
    with np.errstate(divide="ignore", invalid="ignore"):
        rb_d = np.where(part, (ex0plus - exm) / inp.dexinc_mev, 1.0)
    eout_d = np.where(part, 0.5 * (ex0plus + exm) - ss - ex, inp.exinc_mev - ss - ex)
    cont = n > r.nlast
    return (np.where(cont, eout_c, eout_d), np.where(cont, rb_c, rb_d),
            np.where(cont, exout_c, ex))


def _discfactor(r: DensResidual):
    """densprepare.f90's missing-level correction for the discrete rows above Ntop.

    A tensor when `Ncum(NL)` carries a gradient (DIFFPARAM): `torch.clamp`'s derivative is
    `np.clip`'s, i.e. zero outside [0.5, 2], which is what a finite difference measures there.
    """
    if r.nlast <= r.ntop:
        return 1.0
    ratio = (r.ncum_nl - r.ntop) / (r.nlast - r.ntop)
    if isinstance(ratio, Tensor):
        return torch.clamp(ratio, 0.5, 2.0)
    return min(max(ratio, 0.5), 2.0)


def _rho0_rows(r: DensResidual, nex: int, rboundary: np.ndarray, discfactor,
               glue: bool = False) -> np.ndarray:
    """`_rho0` for residual rows 0..nex-1 at once, (Nex, numJ+1, 2).

    TALYS: densprepare.f90:1 (densprepare)
    Test: A-ld / SPEED0 golden
    """
    grad = isinstance(r.rhogrid, Tensor)
    out = np.zeros((nex, NUMJ + 1, 2))
    n = np.arange(nex)
    cont = n > r.nlast
    cont_rows = None
    if cont.any():
        mj = np.asarray(r.maxj[:nex], dtype=np.int64)
        keep = (np.arange(NUMJ + 1)[None, :] <= mj[:, None]) & cont[:, None]
        if grad:
            # DIFFPARAM: the continuum rows are the only ones a level-density parameter reaches
            # (a discrete level's weight is Rboundary, a grid quantity), so they carry the graph
            # and the discrete cells below stay the constants they are.
            rows = (torch.as_tensor(rboundary, dtype=DTYPE)[:, None, None]
                    * r.rhogrid[:nex].to(DTYPE))
            k_t = torch.as_tensor(keep)[:, :, None]
            cont_rows = torch.where(k_t, rows, torch.zeros((), dtype=DTYPE))
        else:
            rows = rboundary[:, None, None] * np.asarray(r.rhogrid[:nex], dtype=np.float64)
            out = np.where(keep[:, :, None], rows, 0.0)
    df_t = discfactor if isinstance(discfactor, Tensor) else None
    scaled = np.zeros_like(out) if df_t is not None else None  # cells that carry `discfactor`
    kd = min(r.nlast, nex - 1) + 1
    if glue and df_t is None and not grad and kd > 0:
        # NATIVEX2 (glue): the loop below as one scatter -- one cell per level, so no index
        # repeats; int() truncation is astype's for the finite spins it is taken on
        jd = np.asarray(r.jdis[:kd], dtype=np.float64)
        if np.isfinite(jd).all():
            ir = jd.astype(np.int64)
            k = np.flatnonzero((ir >= 0) & (ir <= NUMJ))
            if k.size:
                rbk = np.asarray(rboundary[k], dtype=np.float64)
                vals = np.where(k > r.ntop, rbk * discfactor, rbk)
                pidx = np.where(np.asarray(r.parlev[:kd])[k].astype(np.int64) == -1, 0, 1)
                out[k, ir[k], pidx] = vals
            return out
    for k in range(kd):  # discrete levels: one (Ir, parity) cell each
        ir = int(r.jdis[k])
        if 0 <= ir <= NUMJ:
            if k > r.ntop and df_t is not None:
                scaled[k, ir, _pidx(int(r.parlev[k]))] = float(rboundary[k])
            else:
                out[k, ir, _pidx(int(r.parlev[k]))] = (
                    float(rboundary[k]) * discfactor if k > r.ntop else float(rboundary[k]))
    total = torch.as_tensor(out, dtype=DTYPE) if (grad or df_t is not None) else out
    if df_t is not None:
        total = total + df_t * torch.as_tensor(scaled, dtype=DTYPE)
    if cont_rows is None:
        return total
    return cont_rows + total


def _rho0(r: DensResidual, nexout: int, rboundary: float, discfactor: float) -> np.ndarray:
    """`rho0(Ir, Pprime)` of one residual bin: a weight for a discrete level (Rboundary, times
    the missing-level `discfactor` above Ntop), and Rboundary * rhogrid for a continuum bin.

    TALYS: densprepare.f90:1 (densprepare)
    Test: A-ld
    """
    out = np.zeros((NUMJ + 1, 2))
    if nexout <= r.nlast:
        ir = int(r.jdis[nexout])
        if 0 <= ir <= NUMJ:
            out[ir, _pidx(int(r.parlev[nexout]))] = (
                rboundary * discfactor if nexout > r.ntop else rboundary
            )
        return out
    mj = int(r.maxj[nexout])
    out[: mj + 1] = rboundary * r.rhogrid[nexout, : mj + 1]
    return out


def _tgam_row(inp: DensPrepareInputs, egamma: float) -> np.ndarray:
    """`Tgam(l, irad)` = 2 pi Egamma^(2l+1) f_XL(Efs, Egamma) Fnorm(0), spin independent.

    densprepare.f90:305 calls fstrength with (Ir, iP) = (0, 0); only `strength 11` with
    `flagstrengthjp` makes it spin dependent, and that branch is unreachable here.

    TALYS: densprepare.f90:1 (densprepare)
    Test: A-psf
    """
    from physics.hf.core.constants import talys_constants

    out = np.zeros((inp.gammax + 1, 2))
    if egamma <= 0.0 or inp.gamma_strength is None:
        return out
    twopi = float(talys_constants()["twopi"])
    efs = inp.exinc_mev - inp.s_n_mev
    for l in range(1, inp.gammax + 1):  # noqa: E741 -- TALYS's loop variable
        fac = twopi * egamma ** (2 * l + 1) * float(inp.fnorm[1])
        for irad in (0, 1):
            out[l, irad] = fac * float(inp.gamma_strength(efs, egamma, irad, l))
    return out


def _tgam_rows(inp: DensPrepareInputs, egamma: np.ndarray) -> np.ndarray:
    """`_tgam_row` for every residual bin at once, (Nex, gammax+1, 2).

    The same numbers as calling `_tgam_row` per bin: the prefactor is still formed per bin in
    Python floats, and the strength function -- which is vectorised over Egamma -- is called
    once per (l, irad) on all positive Egamma instead of once per bin. A `gamma_strength`
    without a `batch` attribute falls back to the per-bin loop.

    TALYS: densprepare.f90:1 (densprepare)
    Test: A-psf / SPEED0 golden
    """
    from physics.hf.core.constants import talys_constants

    n = len(egamma)
    out = np.zeros((n, inp.gammax + 1, 2))
    batch = getattr(inp.gamma_strength, "batch", None)
    if inp.gamma_strength is None:
        return out
    if batch is None:
        for k in range(n):
            out[k] = _tgam_row(inp, float(egamma[k]))
        return out
    egamma = np.asarray(egamma, dtype=np.float64)
    idx = np.flatnonzero(egamma > 0.0)
    if not idx.size:
        return out
    eg = egamma[idx]
    twopi = float(talys_constants()["twopi"])
    efs = inp.exinc_mev - inp.s_n_mev
    fn1 = float(inp.fnorm[1])
    if getattr(inp.gamma_strength, "differentiable", False):
        out = torch.zeros((n, inp.gammax + 1, 2), dtype=DTYPE)
    elif inp.gamma_params is not None:
        # NATIVEX2: every (Egamma, l, irad) in one C call (compound/psf_nx2.py)
        from physics.hf.compound.psf_nx2 import tgam_points

        got = tgam_points(inp.gamma_params, inp.gammax, efs, eg, twopi, fn1)
        if got is not None:
            out[idx, 1:, :] = got[:, 1:, :]
            return out
    for l in range(1, inp.gammax + 1):  # noqa: E741 -- TALYS's loop variable
        fac = twopi * eg ** (2 * l + 1) * fn1  # numpy's float64 ** int is libm pow, as Python's
        for irad in (0, 1):
            v = None
            if inp.gamma_params is not None:
                from physics.hf.compound.psf_fast import fstrength_np

                v = fstrength_np(inp.gamma_params, efs, eg, irad, l)
            if v is None:
                v = batch(efs, eg, irad, l)
            if isinstance(v, Tensor):
                out[idx, l, irad] = torch.as_tensor(fac, dtype=DTYPE) * v
            else:
                out[idx, l, irad] = fac * v
    return out


def _locate_nen(tr: DensTrans, eout: np.ndarray) -> np.ndarray:
    """`nen`, the emission-grid index densprepare.f90:341-345 locates each Eout in (0 below
    egrid(ebegin)).

    TALYS: locate.f90:1 (locate)
    Test: A-trans
    """
    from physics.hf.core.grids import locate_scalar

    lo = float(tr.egrid_mev[tr.ebegin])
    ib, ie = tr.ebegin, tr.eend
    xs = np.asarray(tr.egrid_mev, dtype=np.float32)
    if ib <= ie and bool(np.all(np.diff(xs[ib : ie + 1]) > 0)):
        # locate_scalar's bisection on a strictly ascending float32 table is searchsorted
        x = np.asarray(eout, dtype=np.float64).astype(np.float32)
        jl = np.searchsorted(xs[ib : ie + 1], x, side="right") - 1 + ib
        jl = np.where(x == xs[ib], ib, np.where(x == xs[ie], ie - 1, jl))
        return np.where(np.asarray(eout) < lo, 0, jl).astype(np.int64)
    return np.array(
        [0 if e < lo else locate_scalar(tr.egrid_mev, tr.ebegin, tr.eend, float(e))
         for e in eout],
        dtype=np.int64,
    )


def _interp_nodes(tr: DensTrans, nen: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """densprepare.f90:346-352's three interpolation nodes. The triple is centred on `nen` only
    away from the start of the grid (or at its very end); otherwise it *starts* at `nen`.
    TALYS's own asymmetry, kept.

    TALYS: densprepare.f90:1 (densprepare)
    Test: A-trans
    """
    centred = (nen > tr.ebegin + 1) | (nen >= tr.maxen - 1)
    na = np.where(centred, nen - 1, nen)
    return na, na + 1, na + 2


def _interpolate(inp, tr, ch, grad_t: bool, fn: float, na, nb, nc, w1, w2, w3, keep) -> None:
    """densprepare.f90:341-360's Lagrange interpolation of Tjl and Tl onto the residual rows, on
    the graph (DIFFPARAM) or in numpy, into `ch.tjl` / `ch.tl`.

    TALYS: densprepare.f90:1 (densprepare)
    Test: A-cn1 / SPEED0 golden
    """
    if grad_t:
        # DIFFPARAM: the same Lagrange interpolation on the graph. The three nodes,
        # `lmax` and the transeps cut are index/branch decisions taken on the
        # unperturbed grid, exactly as in the numpy path.
        w1, w2, w3 = (torch.as_tensor(w, dtype=DTYPE) for w in (w1, w2, w3))
        keep_t = torch.as_tensor(keep)
        z = torch.zeros((), dtype=DTYPE)
        v = (w1[:, :, None] * tr.tjl[na] + w2[:, :, None] * tr.tjl[nb]
             + w3[:, :, None] * tr.tjl[nc])
        v = torch.where(keep_t[:, :, None], v, z)
        ch.tjl = torch.where(v < inp.transeps, z, v) * fn
        if not inp.flagfullhf:
            u = w1 * tr.tl[na] + w2 * tr.tl[nb] + w3 * tr.tl[nc]
            u = torch.where(keep_t, u, z)
            ch.tl = torch.where(u < inp.transeps, z, u) * fn
        return
    v = (w1[:, :, None] * tr.tjl[na] + w2[:, :, None] * tr.tjl[nb]
         + w3[:, :, None] * tr.tjl[nc])
    v = np.where(keep[:, :, None], v, 0.0)
    ch.tjl = np.where(v < inp.transeps, 0.0, v) * fn
    if not inp.flagfullhf:
        u = w1 * tr.tl[na] + w2 * tr.tl[nb] + w3 * tr.tl[nc]
        u = np.where(keep, u, 0.0)
        ch.tl = np.where(u < inp.transeps, 0.0, u) * fn


def _interp_c(tr: DensTrans, nex: int, L: int, eout, ea, eb, ec, na, nb, nc, lm, transeps: float,
              fn: float, ch: ResidualChannels, with_tl: bool) -> bool:
    """NATIVEX2 (glue): `densprepare`'s numpy Lagrange interpolation of Tjl (and Tl) onto the
    residual rows, in C (`nx2_glue_interp`), written into `ch.tjl` / `ch.tl`; False (nothing
    written) without the build (the caller checks the `glue` lever).

    TALYS: densprepare.f90:1 (densprepare)
    Test: tests/hf/test_nx2_glue.py
    """
    from physics.hf.native import nx2

    I, D, P = nx2.I64, nx2.DBL, nx2.P
    fn_c = nx2.kernel("nx2_glue_interp", [I, I] + [P] * 10 + [D, D, P, P], nx2.INT, lever="glue")
    if fn_c is None:
        return False
    tjl = np.ascontiguousarray(tr.tjl, dtype=np.float64)
    tl = np.ascontiguousarray(tr.tl, dtype=np.float64) if with_tl else None
    if tjl.ndim != 3 or tjl.shape[1:] != (L, 3) or (tl is not None and tl.shape[1:] != (L,)):
        return False
    c = [np.ascontiguousarray(x, dtype=d) for x, d in (
        (eout, np.float64), (ea, np.float64), (eb, np.float64), (ec, np.float64), (na, np.int64),
        (nb, np.int64), (nc, np.int64), (lm, np.int64))]
    # the nodes are (na, na + 1, na + 2) (`_interp_nodes`): na >= 0 and nc in range bound all
    if any(x.shape != (nex,) for x in c) or not (
            int(c[4].min()) >= 0 and int(c[6].max()) < tjl.shape[0]
            and (tl is None or tl.shape[0] == tjl.shape[0])):
        return False  # the numpy body raises (or wraps) as it always did
    ptr = nx2.ptr
    fn_c(nex, L, *(ptr(x) for x in c), ptr(tjl), ptr(tl), float(transeps), float(fn),
         ptr(ch.tjl), ptr(ch.tl))
    return True


def densprepare(inp: DensPrepareInputs) -> dict[int, ResidualChannels]:
    """Build the four arrays `compprepare`/`compound` read -- `rho0`, `Tjlnex`, `Tlnex` and
    `Tgam` -- plus `lmaxhf`, from T5's emission-grid transmission, T6's level densities and T7's
    photon strength. This is the adapter `load_cn_dump` stands in for; one `ResidualChannels`
    per exit type, ready for `exit_channel_sums`.

    TALYS: densprepare.f90:1 (densprepare)
    Test: A-cn1
    """
    out: dict[int, ResidualChannels] = {}
    from physics.hf.emission.emit_nx2 import glue_enabled

    glue = glue_enabled()  # NATIVEX2 (glue), read once per call
    for t, r in sorted(inp.residuals.items()):
        nex = r.nexmax + 1
        discfactor = _discfactor(r)
        lmaxhf = np.zeros(nex, dtype=np.int64)
        eout, rb, exout = _eout_and_rboundary_rows(inp, r, nex)
        rho = _rho0_rows(r, nex, rb, discfactor, glue)
        ch = ResidualChannels(
            type=t, zix=r.zix, nix=r.nix, maxex=r.nexmax, nlast=r.nlast,
            spin2=SPIN2[t], parspin2=PARSPIN2[t],
            lmaxhf=lmaxhf, maxj=np.asarray(r.maxj[:nex], dtype=np.int64),
            ex_mev=np.asarray(r.ex_mev[:nex], dtype=float),
            parlev=np.asarray(r.parlev[:nex], dtype=np.int64),
            jdis2=np.where(np.arange(nex) <= r.nlast,
                           (2.0 * np.float32(r.jdis[:nex])).astype(np.int64), -1),
            rho=rho,
        )
        if t == 0:
            lmaxhf[:] = inp.gammax
            if getattr(inp.gamma_strength, "differentiable", False):
                rows = _tgam_rows(inp, inp.exinc_mev - exout)  # a tensor on the graph
                ch.tgam = rows[:, :, :, None, None].expand(nex, inp.gammax + 1, 2, NUMJ + 1, 2)
            else:
                tg = np.zeros((nex, inp.gammax + 1, 2, NUMJ + 1, 2))
                tg[:] = _tgam_rows(inp, inp.exinc_mev - exout)[:, :, :, None, None]
                ch.tgam = tg
        else:
            tr = inp.trans[t]
            L = tr.tjl.shape[1]
            grad_t = isinstance(tr.tjl, Tensor)
            ch.tjl = (torch.zeros((nex, L, 3), dtype=DTYPE) if grad_t
                      else np.zeros((nex, L, 3)))
            ch.tl = torch.zeros((nex, L), dtype=DTYPE) if grad_t else np.zeros((nex, L))
            if tr.ebegin < tr.eend:
                nen = _locate_nen(tr, eout)
                na, nb, nc = _interp_nodes(tr, nen)
                ea, eb, ec = tr.egrid_mev[na], tr.egrid_mev[nb], tr.egrid_mev[nc]
                lm = tr.lmax[np.minimum(np.maximum(nen, 0), tr.maxen)]  # np.clip's values
                fn = float(inp.fnorm[t + 1])
                if glue and not grad_t and _interp_c(tr, nex, L, eout, ea, eb, ec, na, nb, nc,
                                                     lm, inp.transeps, fn, ch,
                                                     not inp.flagfullhf):
                    pass  # NATIVEX2 (glue): the numpy interpolation below in C, into ch.tjl/tl
                else:
                    w1 = ((eout - eb) * (eout - ec) / ((ea - eb) * (ea - ec)))[:, None]
                    w2 = ((eout - ea) * (eout - ec) / ((eb - ea) * (eb - ec)))[:, None]
                    w3 = ((eout - ea) * (eout - eb) / ((ec - ea) * (ec - eb)))[:, None]
                    keep = np.arange(L)[None, :] <= lm[:, None]
                    _interpolate(inp, tr, ch, grad_t, fn, na, nb, nc, w1, w2, w3, keep)
                lmaxhf[:] = lm
        if r.nexmax > 0:
            lmaxhf[r.nexmax] = lmaxhf[r.nexmax - 1]
        out[t] = ch
    if inp.k0 in out:
        out[inp.k0].lmaxhf[0] = inp.lmaxinc
    return out
