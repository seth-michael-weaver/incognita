"""Channels and coupling coefficients of the symmetric rotational model: which (level, l, j) make
up the coupled set at each (J, parity), and the matrix of geometrical coefficients that multiplies
each multipole form factor.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.
ECIS-06 (`ecist.f`) is by J. Raynal and ships inside the TALYS repository under its MIT license.

Task: T13 (physics/hf/CONTRACT.md §7). Acceptance test: A-inc (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    ecist.f:8429 (rotm)
    ecist.f:14643 (quan)
    ecist.f:9889 (dcgs)

Line numbers of anchors follow Python's `str.splitlines()`; `grep -n` gives numbers 30 lower.

The coupling of channel c = (level I, l, j) to c' = (level I', l', j') at total J, for multipole
lambda, is the product of a reduced nuclear matrix element (`rotm`, the rotor) and a geometrical
coefficient (`quan`, the projectile). `dcgs` and `dj6j` were checked against ECIS's own compiled
routines: see `docs/results/hf-ecis-plan.md` §4 and `tests/hf/fixtures/ecis_angmom.json`.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from functools import lru_cache

import torch
from torch import Tensor

from physics.hf.core.angmom import clebsch, racah
from physics.hf.core.tensors import DTYPE
from physics.hf.ecis import ccnative as _ccnative
from physics.hf.ecis.formfactor import LAMBDAS


def _t(x) -> Tensor:
    return torch.as_tensor(x, dtype=DTYPE)


def sixj(j1, j2, j3, j4, j5, j6) -> Tensor:
    """The 6j symbol {j1 j2 j3; j4 j5 j6} from T1's Racah W,
    {j1 j2 j3; j4 j5 j6} = (-1)^(j1+j2+j4+j5) W(j1 j2 j5 j4; j3 j6).

    Verified against ECIS's own `dj6j` (extracted and compiled; 2,000 random arguments, max
    relative difference 3.3e-14).

    TALYS: ecist.f:8972 (dj6j)
    Test: A-inc
    """
    a, b, c, d, e, f = (_t(v) for v in (j1, j2, j3, j4, j5, j6))
    phase = torch.cos(torch.pi * (a + b + d + e))  # (-1)^(a+b+d+e) for integer exponent
    return racah(a, b, e, d, c, f) * phase


def _sixj_many(items) -> list[Tensor]:
    """`[sixj(*args) for args in items]` in one element-wise evaluation over the concatenated
    arguments (SPEEDT3). `racah`'s operations are element-wise and torch's lgamma, exp and cos are
    position-independent, so every value is the one its own call gives; one call instead of one
    per (J, parity) block and multipole saves the per-call op overhead."""
    if not items:
        return []
    shapes, flat = [], [[] for _ in range(6)]
    for args in items:
        full = torch.broadcast_tensors(*(_t(v) for v in args))
        shapes.append(full[0].shape)
        for k in range(6):
            flat[k].append(full[k].reshape(-1))
    args = [torch.cat(f) for f in flat]
    # CCGLUE: the same element-wise evaluation in C (`ccnative.sixj`) when the library is loaded
    out = _ccnative.sixj(args)
    if out is None:
        out = sixj(*args)
    res, pos = [], 0
    for sh in shapes:
        cnt = math.prod(sh)
        res.append(out[pos : pos + cnt].reshape(sh))
        pos += cnt
    return res


def dcgs(lam, jp, j) -> Tensor:
    """ECIS's "singular" Clebsch-Gordan for a half-integer pair,

        dcgs(lambda, j', j) = (-1)^(j+j'-lambda) sqrt(2j+1) <j -1/2; lambda 0 | j' -1/2>

    The overall sign was pinned against ECIS's own compiled `dcgs` on all 567 non-zero values in
    the range the port uses; the sign of the docstring in `ecist.f` (dcgs-009) is the opposite.

    TALYS: ecist.f:9889 (dcgs)
    Test: A-inc
    """
    lam, jp, j = (_t(v) for v in (lam, jp, j))
    cg = clebsch(j, lam, jp, -0.5 * torch.ones_like(j), torch.zeros_like(j), -0.5 * torch.ones_like(j))
    return torch.cos(torch.pi * (j + jp - lam)) * (2.0 * j + 1.0).sqrt() * cg


def reduced_matrix_element(lam, spin_lo, spin_hi, kband) -> Tensor:
    """Reduced nuclear matrix element of the symmetric rotor (rotm-109),

        t_lambda(I -> I') = (-1)^(lambda/2) sqrt(2 I + 1) <I K; lambda 0 | I' K>

    with `spin_lo` = I the spin of the lower-index level and `spin_hi` = I' the higher-index one,
    and K the projection of the rotational band (ECIS `nspin/2`, TALYS the target ground-state
    spin). Zero outside max(2, |I-I'|) <= lambda <= min(8, I+I').

    TALYS: ecist.f:8429 (rotm)
    Test: A-inc
    """
    lam, lo, hi, k = (_t(v) for v in (lam, spin_lo, spin_hi, kband))
    ok = (lam >= torch.maximum(_t(2.0), (lo - hi).abs())) & (lam <= lo + hi)
    cg = clebsch(lo, lam, hi, k, torch.zeros_like(k), k)
    val = torch.cos(torch.pi * lam / 2.0) * (2.0 * lo + 1.0).sqrt() * cg
    return torch.where(ok, val, torch.zeros_like(val))


# SPEEDT: the two factors of the coupling that do not depend on the total J -- the reduced matrix
# element (a function of the level pair) and `dcgs` (of the j pair) -- are evaluated once per
# multipole on the distinct values and gathered, instead of on every (row, column) pair of every
# (J, parity) block. Element by element the same operations on the same arguments (clebsch is
# element-wise, its Horner series freezes finished elements), so the matrices are unchanged.


@lru_cache(maxsize=256)
def _rme_table(lam: float, spins: tuple[float, ...], kband: float) -> Tensor:
    """`reduced_matrix_element(lam, spin[b], spin[a], kband)` as a (level a, level b) table: the
    `t` of `coupling_matrix` for row level a and column level b."""
    sp = torch.tensor(spins, dtype=DTYPE)
    m = sp.numel()
    return reduced_matrix_element(_t(lam).expand(m, m), sp[None, :].expand(m, m),
                                  sp[:, None].expand(m, m), _t(kband).expand(m, m))


@lru_cache(maxsize=256)
def _dcgs_table(lam: float, jvals: tuple[float, ...]) -> Tensor:
    """`dcgs(lam, j_p, j_q)` for every pair of the distinct j values, (p, q)."""
    jv = torch.tensor(jvals, dtype=DTYPE)
    m = jv.numel()
    return dcgs(_t(lam).expand(m, m), jv[:, None].expand(m, m), jv[None, :].expand(m, m))


def _dcgs_lookup(lam: float, j: Tensor) -> Tensor:
    """`dcgs(lam, j[:, None], j[None, :])` through `_dcgs_table`.

    SPEEDT3: for half-integer j (a nucleon projectile) one table per multipole over every
    j = 1/2, 3/2, ... up to the largest seen, instead of one per distinct j set of each (J, parity)
    block; the entries are the same element-wise evaluations (torch's lgamma, exp, cos and sqrt
    are position-independent), gathered by 2j."""
    idx = j - 0.5
    if j.numel() and bool((idx == torch.round(idx)).all()) and float(j.min()) >= 0.5:
        k = torch.round(idx).to(torch.int64)
        m = 16 * ((int(k.max()) + 16) // 16)
        return _dcgs_table(lam, tuple(0.5 + q for q in range(m)))[k[:, None], k[None, :]]
    jvals, inv = torch.unique(j, sorted=True, return_inverse=True)
    return _dcgs_table(lam, tuple(jvals.tolist()))[inv[:, None], inv[None, :]]


@dataclass(frozen=True)
class ChannelSet:
    """The coupled channels at one (J, parity), in ECIS's own order: level index, then l, then j.

    `level`, `l` are int64 (N,); `spin`, `j` are float64 (N,); `ls2` is 2 l.s = j(j+1) - l(l+1)
    - s(s+1). `elastic` is the boolean mask of channels built on the ground state, which are the
    entrance channels. `coupling` is (NLAM, N, N): the geometrical coefficient of each multipole
    form factor, with the lambda = 0 slice the identity (`rotp-286`: form factor 1 is the
    angle-averaged potential and multiplies every diagonal).

    `so_grad_coef`, `so_r2_coef` and `so_deriv_coef` are the three extra (NLAM, N, N) tables
    `quan` builds when the spin-orbit is deformed (`lo(13) = T`, E > `soswitch`), and are `None`
    otherwise. See `deformed_spin_orbit_coupling`.
    """

    twoJ: int
    parity: int
    level: Tensor
    l: Tensor  # noqa: E741
    j: Tensor
    spin: Tensor
    ls2: Tensor
    elastic: Tensor
    coupling: Tensor
    lambdas: tuple[int, ...]
    so_grad_coef: Tensor | None = None
    so_r2_coef: Tensor | None = None
    so_deriv_coef: Tensor | None = None


def channel_list(
    twoJ: int, parity: int, level_spin: Tensor, level_parity: Tensor, lmax: int, s: float = 0.5
) -> tuple[Tensor, Tensor, Tensor]:
    """(level, l, j) of every channel at total J = twoJ/2 and the given parity: parity
    conservation `parlev(level) * (-1)**l == parity` and the triangle |I - j| <= J <= I + j
    (quan-160..182 enumerates the same set from ECIS's `mc` table).

    TALYS: ecist.f:14643 (quan)
    Test: A-inc
    """
    J = 0.5 * twoJ
    lev, ls, js = [], [], []
    n_lev = level_spin.numel()
    for b in range(n_lev):
        I = float(level_spin[b])  # noqa: E741
        pb = int(level_parity[b])
        for orb in range(lmax + 1):
            if pb * (-1) ** orb != parity:
                continue
            for jj in (orb - s, orb + s):
                if jj < 0:
                    continue
                if abs(I - jj) - 1.0e-9 <= J <= I + jj + 1.0e-9:
                    lev.append(b)
                    ls.append(orb)
                    js.append(jj)
    return (
        torch.tensor(lev, dtype=torch.int64),
        torch.tensor(ls, dtype=torch.int64),
        torch.tensor(js, dtype=DTYPE),
    )


def _rot_sixj_args(twoJ: int, level: Tensor, j: Tensor, spin: Tensor) -> tuple:
    """The arguments of `coupling_matrix`'s 6j symbols, every multipole at once: (NLAM-1, N, N)."""
    n = level.numel()
    lam = _t(LAMBDAS)
    return (j[None, :], lam[1:, None, None].expand(-1, n, n), j[:, None], spin[level][:, None],
            _t(0.5 * twoJ).expand(n, n), spin[level][None, :])


def coupling_matrix(
    twoJ: int, level: Tensor, l: Tensor, j: Tensor, spin: Tensor, kband: float,  # noqa: E741
    w6_all: Tensor | None = None,
) -> Tensor:
    """The (NLAM, N, N) geometrical coupling of the symmetric rotational model with an undeformed
    spin-orbit (ECIS `lo(13) = F`, i.e. E <= `soswitch`), from quan-183..238 with `is = 1`
    (spin-1/2 projectile) and `iis = 0` (no spin transfer):

        A^lambda_{row,col} = (-1)^((l+l'+lambda)/2 + J + I' + l - j') sqrt(2 lambda + 1)
                             {j lambda j'; I' J I}_6j dcgs(lambda, j', j) t_lambda(I -> I')

    with unprimed = column (ECIS `i2`), primed = row (`i1`), and `t_lambda` from `rotm` taken with
    the lower-index level first. The lambda = 0 slice is the identity: ECIS's form factor 1 is the
    angle-averaged deformed potential and multiplies the diagonal of every channel.

    TALYS: ecist.f:14643 (quan)
    Test: A-inc
    """
    J = 0.5 * twoJ
    n = level.numel()
    lam = _t(LAMBDAS)
    lr, lc = l[:, None].to(DTYPE), l[None, :].to(DTYPE)
    jr = j[:, None]
    ir = spin[level][:, None]
    out = torch.zeros((lam.numel(), n, n), dtype=DTYPE)
    out[0] = torch.eye(n, dtype=DTYPE)
    # SPEEDT3: the 6j symbols of every multipole in one element-wise call (see `_sixj_many`);
    # `w6_all` may come from a call over many blocks
    if w6_all is None:
        w6_all = sixj(*_rot_sixj_args(twoJ, level, j, spin))
    for k in range(1, lam.numel()):
        L = float(lam[k])
        # rotm's own doc (rotm-035) reads (ip||q||i) = sqrt(2i+1) cg(i, iq, ip, k, 0, k): the
        # sqrt(2I+1) belongs to the INITIAL state, i.e. the column. ECIS stores one value per
        # level pair (the lower index first, rotm-058..071) and the transposed triangle differs
        # from it by (-1)^(I_row - I_col); taking the column spin here is what makes the matrix
        # symmetric, which it must be for the S-matrix to be. For a K = 0 even-even band the two
        # readings agree (Delta I is even); for the odd-A K = 3/2, 1/2, 5/2, 7/2 bands of Au197,
        # Gd157, Pu239, Am241 and U235 they differ in sign on every Delta I = odd block.
        t = _rme_table(L, tuple(spin.tolist()), float(kband))[level[:, None], level[None, :]]
        w6 = w6_all[k - 1]
        cgs = _dcgs_lookup(L, j)
        ph = torch.cos(torch.pi * ((lr + lc + L) / 2.0 + J + ir + lc - jr))
        val = ph * (2.0 * L + 1.0) ** 0.5 * w6 * cgs * t
        # parity/triangle violations come back as exact zeros from clebsch/racah
        out[k] = torch.where(torch.isfinite(val), val, torch.zeros_like(val))
    return out


def deformed_spin_orbit_coupling(
    central: Tensor, l: Tensor, ls2: Tensor  # noqa: E741
) -> tuple[Tensor, Tensor, Tensor]:
    """The three extra coupling tables of `quan` when ECIS deforms the spin-orbit potential
    (`lo(13) = T`, i.e. E > `soswitch`), quan-257..305 and quan-341..362, with
    `az = (0, 1, 1, 0, 1, 1)` -- ECIS's defaults, which TALYS leaves alone because it never sets
    `ecis1(4:4)` (lect-355..361).

    Each is (NLAM, N, N) and rides on the SAME geometrical coefficient `central` (ECIS's `cx`) as
    the central multipole, with row = the equation, column = the source channel, and the
    lambda = 0 slice zero: `redm`'s multipole table starts at lambda = 2 (rotm-100), so the
    lambda = 0 potential has no spin-orbit transition partner.

        so_grad[lam]  = cx[lam] * (2 l.s)_col                                        (quan-261)
        so_r2[lam]    = cx[lam] * ( s (lam(lam+1) - l_row(l_row+1) - l_col(l_col+1))
                                    + (2 l.s)_row (1 + (2 l.s)_col / 2s) )           (quan-280)
        so_deriv[lam] = cx[lam] * ((2 l.s)_col - (2 l.s)_row)                        (quan-352)

    with s = 1/2 and `2s = is = 1` for a nucleon, so the two divisions above are by 1 and the
    prefactor `0.5 (ipi(2,j1)-1)` is 1/2. `so_grad` multiplies ECIS's first spin-orbit transition
    form factor and `so_r2` its r**-2 partner; `so_deriv` multiplies the SAME r**-2 partner but
    against `r du/dr` instead of `u` -- ECIS's "derivative coupling", whose second member is
    built from `pd`, and `pd` is r (d/dr) of the solution (insi-233..246), not d/dr.

    ECIS computes only the i2 <= i1 triangle and then copies it (quan-379..417), adding
    `-at` on the `so_grad` address and `+at` on the `so_r2` one for every derivative term so that
    the interaction stays hermitian. That correction is exactly the difference between the two
    orientations of the formulas above -- `so_grad` with the columns swapped differs by
    `2 cx ((2 l.s)_row - (2 l.s)_col)` and `so_r2` by `cx ((2 l.s)_col - (2 l.s)_row)` -- so the
    port writes the formula for every (row, column) pair and needs no triangle at all.
    `tests/hf/test_ecis.py` pins that identity.

    TALYS: ecist.f:14643 (quan)
    Test: A-inc
    """
    n = l.numel()
    lam = _t(LAMBDAS)
    lr, lc = l[:, None].to(DTYPE), l[None, :].to(DTYPE)
    sr, sc = ls2[:, None], ls2[None, :]
    so_grad = central * sc[None]
    so_deriv = central * (sc - sr)[None]
    so_r2 = torch.zeros_like(central)
    for k in range(1, lam.numel()):
        L = float(lam[k])
        smatel = 0.5 * (L * (L + 1.0) - lr * (lr + 1.0) - lc * (lc + 1.0)) + sr * (1.0 + sc)
        so_r2[k] = central[k] * smatel
    zero = torch.zeros((n, n), dtype=DTYPE)
    so_grad[0], so_deriv[0] = zero, zero
    return so_grad, so_r2, so_deriv


def channels(
    twoJ: int,
    parity: int,
    level_spin: Tensor,
    level_parity: Tensor,
    lmax: int,
    kband: float,
    s: float = 0.5,
    deformed_spin_orbit: bool = False,
    _pieces: tuple | None = None,
) -> ChannelSet:
    """Build the coupled set and its coupling matrix at one (J, parity).

    `deformed_spin_orbit` is ECIS's `lo(13)`: above `soswitch` it adds the three tables of
    `deformed_spin_orbit_coupling`.

    TALYS: ecist.f:14643 (quan)
    Test: A-inc
    """
    lev, orb, jj, w6_all = _pieces or (
        *channel_list(twoJ, parity, level_spin, level_parity, lmax, s), None)
    ls2 = jj * (jj + 1.0) - orb.to(DTYPE) * (orb.to(DTYPE) + 1.0) - s * (s + 1.0)
    cpl = coupling_matrix(twoJ, lev, orb, jj, level_spin, kband, w6_all)
    g1 = g2 = gd = None
    if deformed_spin_orbit and lev.numel():
        g1, g2, gd = deformed_spin_orbit_coupling(cpl, orb, ls2)
    return ChannelSet(
        twoJ=twoJ, parity=parity, level=lev, l=orb, j=jj, spin=level_spin[lev], ls2=ls2,
        elastic=lev == 0, coupling=cpl, lambdas=LAMBDAS,
        so_grad_coef=g1, so_r2_coef=g2, so_deriv_coef=gd,
    )


def _vib_bands(level: Tensor, vib_lambda: Tensor) -> list:
    """(band, lambda, pair mask) of every band `vibrational_coupling_matrix` fills."""
    gnd_r, gnd_c = (level == 0)[:, None], (level == 0)[None, :]
    bands = []
    for b in range(1, int(vib_lambda.numel())):
        L = float(vib_lambda[b])
        if L == 0.0:
            continue
        pair = ((level == b)[:, None] & gnd_c) | (gnd_r & (level == b)[None, :])
        if bool(pair.any()):
            bands.append((b, L, pair))
    return bands


def _vib_sixj_args(twoJ: int, level: Tensor, j: Tensor, spin: Tensor, bands: list) -> tuple:
    """The arguments of `vibrational_coupling_matrix`'s 6j symbols, every band at once."""
    n = level.numel()
    return (j[None, :], _t([L for _, L, _ in bands])[:, None, None].expand(-1, n, n), j[:, None],
            spin[level][:, None], _t(0.5 * twoJ).expand(n, n), spin[level][None, :])


def vibrational_coupling_matrix(
    twoJ: int,
    level: Tensor,
    l: Tensor,  # noqa: E741
    j: Tensor,
    spin: Tensor,
    vib_lambda: Tensor,
    _bands_w6: tuple | None = None,
) -> Tensor:
    """The (1 + NB, N, N) coupling of the harmonic one-phonon vibrational model.

    Slice 0 is the identity (the undeformed potential on every diagonal); slice k couples the
    ground state to the one-phonon level of band k, through the SAME `quan` coefficient as the
    rotational model (quan-183..238, `is = 1`, `iis = 0`) with the one-phonon reduced matrix
    element of `vibm-152..163` in place of `rotm`'s:

        A^lambda_{c'c} = (-1)^((l+l'+lambda)/2 + J + I' + l - j') sqrt(2 lambda+1)
                         {j lambda j'; I' J I}_6j dcgs(lambda, j', j) t_lambda ,   t_lambda = +/- 1.

    `vibm` gives `t(3,it) = ay` with a sign that only depends on lambda; a cross section never
    sees it, and neither does an all-orders coupled-channels one, because with no level-to-level
    coupling every path in or out of a one-phonon level uses the pair (A_{b0}, A_{0b}) an even
    number of times. Taking t = +1 in BOTH directions makes the matrix exactly symmetric, which
    it must be for the S-matrix to be -- checked on every (lambda, J, channel) pair the port
    reaches, not assumed (`tests/hf/test_ecis.py`).

    Harmonicity is why there is nothing else in the matrix: `alpha_lambda` connects n to n +/- 1,
    so one-phonon levels do not couple to each other and carry no reorientation term. TALYS sets
    `ecis1(2:2) = 'T'` only when some `iphonon == 2` (incidentecis.f90:244), which no reference
    target does.

    TALYS: ecist.f:14643 (quan), ecist.f:8043 (vibm)
    Test: A-inc
    """
    J = 0.5 * twoJ
    n = level.numel()
    nb = int(vib_lambda.numel()) - 1
    out = torch.zeros((nb + 1, n, n), dtype=DTYPE)
    out[0] = torch.eye(n, dtype=DTYPE)
    lr, lc = l[:, None].to(DTYPE), l[None, :].to(DTYPE)
    jr = j[:, None]
    ir = spin[level][:, None]
    # SPEEDT3: the 6j symbols of every band in one element-wise call (see `_sixj_many`);
    # `_bands_w6` may come from a call over many blocks
    if _bands_w6 is None:
        bands = _vib_bands(level, vib_lambda)
        w6_all = sixj(*_vib_sixj_args(twoJ, level, j, spin, bands)) if bands else None
    else:
        bands, w6_all = _bands_w6
    for q, (b, L, pair) in enumerate(bands):
        w6 = w6_all[q]
        cgs = _dcgs_lookup(L, j)
        ph = torch.cos(torch.pi * ((lr + lc + L) / 2.0 + J + ir + lc - jr))
        val = ph * (2.0 * L + 1.0) ** 0.5 * w6 * cgs
        val = torch.where(torch.isfinite(val), val, torch.zeros_like(val))
        out[b] = torch.where(pair, val, torch.zeros_like(val))
    return out


def vibrational_channels(
    twoJ: int,
    parity: int,
    level_spin: Tensor,
    level_parity: Tensor,
    vib_lambda: Tensor,
    lmax: int,
    s: float = 0.5,
    _pieces: tuple | None = None,
) -> ChannelSet:
    """The coupled set and its coupling at one (J, parity) for `colltype V`.

    `vib_lambda[b]` is the multipolarity of the phonon that builds level b (TALYS's `lband` of
    band `vibband(b)`), zero for the ground state. It is the level's spin for a one-phonon state,
    but TALYS keeps the two apart and so does this.

    TALYS: ecist.f:14643 (quan)
    Test: A-inc
    """
    lev, orb, jj, bands_w6 = _pieces or (
        *channel_list(twoJ, parity, level_spin, level_parity, lmax, s), None)
    ls2 = jj * (jj + 1.0) - orb.to(DTYPE) * (orb.to(DTYPE) + 1.0) - s * (s + 1.0)
    cpl = vibrational_coupling_matrix(twoJ, lev, orb, jj, level_spin, vib_lambda, bands_w6)
    return ChannelSet(
        twoJ=twoJ, parity=parity, level=lev, l=orb, j=jj, spin=level_spin[lev], ls2=ls2,
        elastic=lev == 0, coupling=cpl, lambdas=tuple(range(int(vib_lambda.numel()))),
    )


def _channels_many(kind: str, pairs, level_spin: Tensor, level_parity: Tensor, lmax: int, s: float,
                   extra) -> list[ChannelSet]:
    """`channels` (kind "rot", extra = (kband, deformed_spin_orbit)) or `vibrational_channels`
    (kind "vib", extra = vib_lambda) for several (twoJ, parity) pairs, with the 6j symbols of all
    of them in one `_sixj_many` evaluation. Same values as one call per pair."""
    lists = [channel_list(tj, par, level_spin, level_parity, lmax, s) for tj, par in pairs]
    if kind == "rot":
        kband, dso = extra
        w6 = _sixj_many([_rot_sixj_args(tj, lev, jj, level_spin)
                         for (tj, _), (lev, _o, jj) in zip(pairs, lists, strict=True)])
        return [channels(tj, par, level_spin, level_parity, lmax, kband, s, dso, (*lst, w))
                for (tj, par), lst, w in zip(pairs, lists, w6, strict=True)]
    if kind == "vib2":
        table, codes = extra
        mults = table.multipoles
        w6 = _sixj_many([_anh_sixj_args(tj, lev, jj, level_spin, mults)
                         for (tj, _), (lev, _o, jj) in zip(pairs, lists, strict=True)]) if mults \
            else [None] * len(pairs)
        return [anharmonic_vibrational_channels(tj, par, level_spin, level_parity, table, codes,
                                                lmax, s, (*lst, (mults, w)))
                for (tj, par), lst, w in zip(pairs, lists, w6, strict=True)]
    vib_lambda = extra
    bands = [_vib_bands(lev, vib_lambda) for lev, _o, _j in lists]
    todo = [k for k, b in enumerate(bands) if b]
    w6 = dict(zip(todo, _sixj_many([_vib_sixj_args(pairs[k][0], lists[k][0], lists[k][2],
                                                   level_spin, bands[k]) for k in todo]),
                  strict=True))
    return [vibrational_channels(tj, par, level_spin, level_parity, vib_lambda, lmax, s,
                                 (*lists[k], (bands[k], w6.get(k))))
            for k, (tj, par) in enumerate(pairs)]


def _anh_sixj_args(twoJ: int, level: Tensor, j: Tensor, spin: Tensor, lams: tuple) -> tuple:
    """The arguments of `anharmonic_vibrational_coupling_matrix`'s 6j symbols, every multipole of
    the scheme at once: (NMULT, N, N)."""
    n = level.numel()
    return (j[None, :], _t(list(lams))[:, None, None].expand(-1, n, n), j[:, None],
            spin[level][:, None], _t(0.5 * twoJ).expand(n, n), spin[level][None, :])


def anharmonic_vibrational_coupling_matrix(
    twoJ: int,
    level: Tensor,
    l: Tensor,  # noqa: E741
    j: Tensor,
    spin: Tensor,
    table,
    codes: tuple[int, ...],
    _mult_w6: tuple | None = None,
) -> Tensor:
    """The `(1 + len(codes), N, N)` coupling of the SECOND-order vibrational model.

    Slice 0 is the identity (ECIS's form factor 1, the undeformed potential on every diagonal);
    slice `1 + q` carries the coefficient of the form factor `codes[q]`. Every element goes
    through the SAME `quan` expression as the rotational and harmonic-vibrational models
    (quan-183..238, `is = 1`, `iis = 0`),

        A^lambda_{c'c} = (-1)^((l+l'+lambda)/2 + J + I' + l - j') sqrt(2 lambda + 1)
                         {j lambda j'; I' J I}_6j dcgs(lambda, j', j) t ,

    with `t` now `vibm`'s reduced matrix element rather than the harmonic `+/- 1` -- and `lambda`
    read off the same `(iq1, lambda, t)` triple, so one level pair can contribute to several
    slices and several multipoles at once. `table` is
    `vibm.reduced_matrix_elements(...)`, keyed by the ordered pair `(i1, i2)` with `i1 <= i2`.

    **This is where the harmonic `t = +1` shortcut has to die.** `vibrational_coupling_matrix`
    justifies it by "every path in or out of a one-phonon level uses the pair (A_b0, A_0b) an
    even number of times", which is exactly what a 0 -> 1 -> 2 path breaks. Signs come from
    `vibm` here; the form factors carry the matching sign convention
    (`formfactor.anharmonic_vibrational_form_factors`).

    ECIS fills only the `i2 <= i1` triangle of `nat/at` and copies it (quan-379..417), and with
    an undeformed spin-orbit the geometrical factor above is invariant under swapping row and
    column, so the port writes `t` at both (a, b) and (b, a) and the matrix is symmetric -- which
    it must be for the S-matrix to be. `tests/hf/test_ecis.py` pins that.

    TALYS: ecist.f:14643 (quan), ecist.f:8043 (vibm)
    Test: G-2PH
    """
    J = 0.5 * twoJ
    n = level.numel()
    out = torch.zeros((len(codes) + 1, n, n), dtype=DTYPE)
    out[0] = torch.eye(n, dtype=DTYPE)
    if n == 0:
        return out
    lr, lc = l[:, None].to(DTYPE), l[None, :].to(DTYPE)
    jr = j[:, None]
    ir = spin[level][:, None]
    if _mult_w6 is None:
        mults = table.multipoles
        w6_all = sixj(*_anh_sixj_args(twoJ, level, j, spin, mults)) if mults else None
    else:
        mults, w6_all = _mult_w6
    geo: dict[int, Tensor] = {}
    for q, L in enumerate(mults):
        w6 = w6_all[q]
        cgs = _dcgs_lookup(float(L), j)
        ph = torch.cos(torch.pi * ((lr + lc + L) / 2.0 + J + ir + lc - jr))
        val = ph * (2.0 * L + 1.0) ** 0.5 * w6 * cgs
        geo[L] = torch.where(torch.isfinite(val), val, torch.zeros_like(val))
    slot = {c: q + 1 for q, c in enumerate(codes)}
    zero = torch.zeros((n, n), dtype=DTYPE)
    for a, b, items in table.pairs:
        ra, rb = level == a, level == b
        pair = (ra[:, None] & rb[None, :]) | (rb[:, None] & ra[None, :])
        if not bool(pair.any()):
            continue
        for code, mult, t in items:
            out[slot[code]] += torch.where(pair, float(t) * geo[mult], zero)
    return out


def anharmonic_vibrational_channels(
    twoJ: int,
    parity: int,
    level_spin: Tensor,
    level_parity: Tensor,
    table,
    codes: tuple[int, ...],
    lmax: int,
    s: float = 0.5,
    _pieces: tuple | None = None,
) -> ChannelSet:
    """The coupled set and its coupling at one (J, parity) for a `colltype V` target with a
    two-phonon level (`ecis1(2:2) = 'T'`, incidentecis.f90:244).

    `lambdas` is a placeholder `(0, 1, 2, ...)` as for the harmonic model: a slice is a FORM
    FACTOR here, not a multipole, and the multipole lives inside the coupling.

    TALYS: ecist.f:14643 (quan)
    Test: G-2PH
    """
    lev, orb, jj, mult_w6 = _pieces or (
        *channel_list(twoJ, parity, level_spin, level_parity, lmax, s), None)
    ls2 = jj * (jj + 1.0) - orb.to(DTYPE) * (orb.to(DTYPE) + 1.0) - s * (s + 1.0)
    cpl = anharmonic_vibrational_coupling_matrix(
        twoJ, lev, orb, jj, level_spin, table, codes, mult_w6
    )
    return ChannelSet(
        twoJ=twoJ, parity=parity, level=lev, l=orb, j=jj, spin=level_spin[lev], ls2=ls2,
        elastic=lev == 0, coupling=cpl, lambdas=tuple(range(len(codes) + 1)),
    )
