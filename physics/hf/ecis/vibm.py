"""Reduced nuclear matrix elements of the vibrational model, including the second-order
(`lo(2)`) terms a two-phonon level needs: a line-by-line port of ECIS-06's `vibm`.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.
ECIS-06 (`ecist.f`) is by J. Raynal and ships inside the TALYS repository under its MIT license.

Task: T13 (physics/hf/CONTRACT.md §7), the ECIS task, extended by TWOPH with ECIS's second-order
(`lo(2)`) branch. Acceptance test: G-2PH (docs/results/hf-ecis-twophonon.md §5).

Line numbers of anchors follow Python's `str.splitlines()`; `grep -n` gives numbers 30 lower.
Line numbers quoted in prose are the `vibm-NNN` tags in the right margin of `ecist.f`.

What `vibm` produces
--------------------
One list of `(iq1, lambda, t)` per *ordered* level pair (i1 <= i2), where `t` is the reduced
nuclear matrix element and `iq1` addresses ECIS's table of form factors:

    iq1 <= nbt1                      first order in beta_iq1        (rotp `iv = 2`)
    iq1 = max(i,j)*(nbt1+1)+min(i,j) second order in beta_i beta_j  (rotp `iv = 3`)

with the diagonal pair (l, l) written `l*(nbt1+2)` at vibm-144/177/288, which is the same
number. `quan` then turns each triple into the geometrical coefficient of that form factor
(`coupling.anharmonic_vibrational_coupling_matrix`).

Six cases, by the phonon counts of the pair (vibm-137's computed GOTO):

    1  0-0  guarded by lo(2)  the ground-state second-order monopole, sum over beta_l^2
    2  0-1  always            the one-phonon coupling (the harmonic model's only term)
    3  1-1  guarded by lo(2)  one-phonon reorientation
    4  1-2  always            one-phonon to two-phonon -- FIRST order, and the term that moves
                              a cross section
    5  2-2  guarded by lo(2)  two-phonon to two-phonon
    6  0-2  guarded by lo(2)  ground state to two-phonon, second order

`lo(2)` is `ecis1(2:2)`, which `incidentecis.f90:244` sets as soon as one level has two phonons
-- so on a two-phonon target every one of the six is live, not only cases 4 and 6. Cases 1, 3
and 5 are there even between levels that are not two-phonon states.

The 37 `colltype V` sweep nuclides (Zn-64 ... Ce-136) are ONE configuration and it is simpler
than `docs/results/hf-ecis-twophonon.md` §1 guessed: five coupled levels but a SINGLE band.
`deformpar.f90:198-201` keys `lband`/`Kband`/`defpar` on the band number, and every V level of
e.g. `Zn.def` carries `vibband = 1`, so `incidentecis.f90:246-250` writes `Nband = 1` and one
phonon card (lambda = 2, K = 0, beta = 0.242). `ecisinput.f90:117`'s `iph(i), iband(i), 1` then
gives `lecl` (lecl-204..208) `npa(1,na) = 1` and `npa(2,na) = 1`: **the two phonons of a
two-phonon level are the same phonon**, so case 4 takes the identical-phonon branch
(vibm-223..228, label 16), not the `lib(2)` one, and `nbt1 = 1` leaves exactly two transition
form factors -- first order in beta and second order in beta^2.

TALYS routines ported here (file:line of the subroutine/function statement):
    ecist.f:8043 (vibm)
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from functools import lru_cache

from physics.hf.core.angmom import clebsch, racah

__all__ = ["Phonons", "VibLevel", "VibmScheme", "decode_code", "reduced_matrix_elements"]

_DROP = 1.0e-12  # vibm-359: ECIS drops a merged element at or below this


@lru_cache(maxsize=65536)  # NATIVEX2: a pure function of three integers (chartrun.KEEP)
def _cg0(two_j1: int, two_j2: int, two_j3: int) -> float:
    """`djcg(j1, j2, j3, 0, 0)` -- the Clebsch-Gordan <j1 0; j2 0 | j3 0> on doubled arguments.

    TALYS: ecist.f:8821 (djcg)
    Test: G-2PH
    """
    import torch

    v = clebsch(*(torch.tensor(0.5 * x, dtype=torch.float64)
                  for x in (two_j1, two_j2, two_j3, 0, 0, 0)))
    return float(v) if math.isfinite(float(v)) else 0.0


@lru_cache(maxsize=65536)  # NATIVEX2: a pure function of six integers (chartrun.KEEP)
def _sixj(a: int, b: int, c: int, d: int, e: int, f: int) -> float:
    """`dj6j(j1..j6)` -- the 6j symbol {a b c; d e f} on doubled arguments, through T1's Racah W.

    TALYS: ecist.f:8972 (dj6j)
    Test: G-2PH
    """
    import torch

    t = [torch.tensor(0.5 * x, dtype=torch.float64) for x in (a, b, c, d, e, f)]
    v = racah(t[0], t[1], t[4], t[3], t[2], t[5]) * math.cos(
        math.pi * float(t[0] + t[1] + t[3] + t[4])
    )
    return float(v) if math.isfinite(float(v)) else 0.0


@dataclass(frozen=True)
class Phonons:
    """ECIS's phonon table, one entry per band: `lam[b]` is `nbeta(17,b)` (the multipolarity,
    TALYS's `Jband`) and `kmag[b]` is `nbeta(18,b)` (`Kmag`). Both are 1-based, entry 0 unused.
    """

    lam: tuple[int, ...]
    kmag: tuple[int, ...]

    @property
    def nbt1(self) -> int:
        """ECIS's `nbt1`, the number of phonons (calx-502, `nbt1 = nbet`)."""
        return len(self.lam) - 1


@dataclass(frozen=True)
class VibLevel:
    """One coupled level as `lecl` leaves it for `vibm`.

    `n_phonon` is `iph(1,iv)`; `bands` is the empty tuple for the ground state, `(b,)` for a
    one-phonon level of band b, and `(lb1, lb2)` for a two-phonon level -- `lecl`'s
    `npa(1,na), npa(2,na)` (lecl-204..208). `two_spin` is 2I (ECIS's `ipi(3,iv) - 1`) and
    `parity_index` is `ipi(1,iv)`, 0 for the target's own parity and 1 for the other one
    (lecl-162..163).
    """

    n_phonon: int
    bands: tuple[int, ...]
    two_spin: int
    parity_index: int


def _pair_code(i: int, j: int, nbt1: int) -> int:
    """`max(i,j)*(nbt1+1) + min(i,j)`, ECIS's address of the second-order form factor in
    `beta_i beta_j` (vibm-035..039, vibm-192/258..261/322). The diagonal `i = j` is
    `i*(nbt1+2)`, which is how vibm-144/177/288 writes the monopole terms."""
    return max(i, j) * (nbt1 + 1) + min(i, j)


def decode_code(code: int, nbt1: int) -> tuple[int, ...]:
    """The phonons a form-factor code stands for: `(k,)` for first order in `beta_k`,
    `(k1, k2)` for second order in `beta_k1 beta_k2` (rotp-119..120).

    TALYS: ecist.f:11889 (rotp)
    Test: G-2PH
    """
    if code <= nbt1:
        return (code,)
    return (code % (nbt1 + 1), code // (nbt1 + 1))


@dataclass(frozen=True)
class VibmScheme:
    """`vibm`'s output for one coupling scheme, in a hashable form so that `solver` can memoise
    the channel sets on it.

    `pairs` holds `(i1, i2, ((iq1, lambda, t), ...))` for every level pair with `i1 <= i2`,
    0-based; `codes` is the ascending list of distinct `iq(1)` form-factor addresses, which is
    the slice order of `formfactor.anharmonic_vibrational_form_factors` (slice 0 there is
    ECIS's own form factor 1 and is not in `codes`).
    """

    pairs: tuple[tuple[int, int, tuple[tuple[int, int, float], ...]], ...]
    codes: tuple[int, ...]
    nbt1: int

    @property
    def multipoles(self) -> tuple[int, ...]:
        """The distinct multipoles the scheme uses, ascending."""
        return tuple(sorted({m for _a, _b, it in self.pairs for _c, m, _t in it}))

    def as_dict(self) -> dict[tuple[int, int], list[tuple[int, int, float]]]:
        return {(a, b): list(it) for a, b, it in self.pairs}


def reduced_matrix_elements(
    levels: list[VibLevel], phonons: Phonons, second_order: bool
) -> VibmScheme:
    """`vibm`'s `(iq(1,k), iq(2,k), t(3,k))` for every level pair `(i1, i2)` with `i1 <= i2`,
    0-based in the level index, including the duplicate merge and the `1e-12` drop.

    `second_order` is ECIS's `lo(2)`. The mixing amplitudes `aa` of vibm-095..116 are the
    identity here: they are read only for `iph(1) > 2` (a 1-and-2-phonon mixture), which
    `ecisinput.f90:117` never writes.

    TALYS: ecist.f:8043 (vibm)
    Test: G-2PH
    """
    return _reduced_matrix_elements(tuple(levels), phonons, bool(second_order))


@lru_cache(maxsize=256)
def _reduced_matrix_elements(levels: tuple, phonons: Phonons, second_order: bool) -> VibmScheme:
    """NATIVEX2: `reduced_matrix_elements` by value (a pure function of the band, which
    `incident_coupled` rebuilt at every incident energy; `chartrun.KEEP`)."""
    if any(lv.n_phonon > 2 for lv in levels):
        raise NotImplementedError(
            "iph(1) > 2 is ECIS's 1-and-2-phonon mixture (vibm-097): it needs the `var` mixing "
            "angles, and ecisinput.f90:117 never writes one"
        )
    nbt1 = phonons.nbt1
    pairs = []
    for i1 in range(len(levels)):
        for i2 in range(i1, len(levels)):
            items = _compact(_pair(levels, phonons, nbt1, second_order, i1, i2))
            if items:
                pairs.append((i1, i2, tuple(items)))
    codes = tuple(sorted({c for _a, _b, it in pairs for c, _m, _t in it}))
    return VibmScheme(pairs=tuple(pairs), codes=codes, nbt1=nbt1)


def _pair(levels, phonons, nbt1, lo2, i1, i2) -> list[tuple[int, int, float]]:
    """The raw (un-merged) elements of one pair: vibm-117..327."""
    lam, kmag = phonons.lam, phonons.kmag
    l1, l2 = levels[i1].n_phonon, levels[i2].n_phonon
    ay = 1.0
    case = l1 + l2 + 1
    if case == 3 and l1 != l2:
        case = 6  # vibm-127
    if l1 <= l2:
        j1, j2 = i1, i2
    else:  # vibm-132..136, the transposition phase
        j1, j2 = i2, i1
        ay *= float(
            1
            - (levels[i1].two_spin + levels[i2].two_spin
               + 2 * (levels[i1].parity_index + levels[i2].parity_index + 1)) % 4
        )
    a, b = levels[j1], levels[j2]
    p_ab = a.parity_index - b.parity_index
    items: list[tuple[int, int, float]] = []

    if case == 1:  # (0||q||0), vibm-139..149
        if not lo2:
            return items
        for l in range(1, nbt1 + 1):
            if kmag[l] == 0:
                items.append((l * (nbt1 + 2), 0, ay))
    elif case == 2:  # (ip||q||0), vibm-152..162: the harmonic one-phonon coupling
        (n2,) = b.bands
        t = ay
        if abs(lam[n2] + p_ab) % 4 != 0:
            t = -t
        items.append((n2, lam[n2], t))
    elif case == 3:  # (ip||q||i), vibm-165..197: one-phonon reorientation
        if not lo2:
            return items
        (n1,), (n2,) = a.bands, b.bands
        if n1 == n2:
            aq = math.sqrt(2 * lam[n1] + 1)
            for l in range(1, nbt1 + 1):
                if kmag[l] == 0:
                    items.append((l * (nbt1 + 2), 0, aq * ay))
        k1 = abs(lam[n2] - lam[n1]) + 1
        k2 = lam[n2] + lam[n1] + 1
        fs = float(2 * (1 - 2 * ((lam[n1] + abs(p_ab + k1 - 1) // 2) % 2)))
        for k in range(k1, k2 + 1, 2):
            j = k - 1
            aq = fs * _cg0(a.two_spin, b.two_spin, 2 * j)
            items.append((_pair_code(n1, n2, nbt1), j, aq * ay))
            fs = -fs
    elif case == 4:  # (l1,l2,ip||q||i), vibm-200..229: one-phonon to two-phonon, FIRST order
        lb1, lb2 = b.bands
        (n1,) = a.bands
        lib1, lib2 = lb1 == n1, lb2 == n1
        if lib1 and lib2:  # vibm-223..228, label 16: the two phonons are the same phonon
            if (b.two_spin + 1) % 4 != 1:
                return items
            code, mult = n1, lam[n1]
            t = math.sqrt(2.0) * ay * float(1 - abs(p_ab + mult) % 4)
        elif lib2:  # vibm-217..221, label 15
            code, mult = lb1, lam[lb1]
            t = ay * float(1 - abs(a.two_spin + b.two_spin + p_ab - mult) % 4)
        elif lib1:  # vibm-212..215
            code, mult = lb2, lam[lb2]
            t = ay * float(1 - 2 * ((abs(p_ab + mult) // 2) % 2))
        else:
            return items
        items.append((code, mult, t * math.sqrt((b.two_spin + 1) / (2.0 * mult + 1.0))))
    elif case == 5:  # (l3,l4,ip||q||l1,l2,i), vibm-232..313
        if not lo2:
            return items
        items = _case5(levels[i1], levels[i2], a, b, lam, kmag, nbt1, ay, p_ab)
    elif case == 6:  # (l1,l2,ip||q||0), vibm-316..327
        if not lo2:
            return items
        k3 = b.two_spin // 2
        k1, k2 = b.bands
        w1 = math.sqrt(2.0) if k1 == k2 else 2.0
        t = (ay * _cg0(2 * lam[k1], 2 * lam[k2], b.two_spin)
             * float(1 - abs(p_ab + k3) % 4) * w1)
        items.append((_pair_code(k1, k2, nbt1), k3, t))
    return items


def _case5(lev1, lev2, a, b, lam, kmag, nbt1, ay, p_ab) -> list[tuple[int, int, float]]:
    """vibm-232..313. The band pair comes from `i1`/`i2` (vibm-233..238), the spins from
    `j1`/`j2`; with two two-phonon levels there is no transposition, so they coincide."""
    lb1, lb2 = lev1.bands
    lb3, lb4 = lev2.bands
    lib = (lb1 != lb3, lb2 != lb4, lb1 != lb4, lb2 != lb3)
    if all(lib):
        return []
    ja1, ja2 = a.two_spin // 2, b.two_spin // 2
    ia1 = (lam[lb2], lam[lb1], lam[lb2], lam[lb1])
    ia2 = (lam[lb4], lam[lb3], lam[lb3], lam[lb4])
    ia3 = (ia1[1], ia1[0], ia1[1], ia1[0])
    ia6 = (_pair_code(lb2, lb4, nbt1), _pair_code(lb1, lb3, nbt1),
           _pair_code(lb2, lb3, nbt1), _pair_code(lb1, lb4, nbt1))
    imin, imax = 1000, 0
    ia4 = [0] * 4
    ia5 = [0] * 4
    for k in range(4):
        if lib[k]:
            continue
        ia4[k] = abs(ia1[k] - ia2[k])
        ia5[k] = ia1[k] + ia2[k]
        imin, imax = min(imin, ia4[k]), max(imax, ia5[k])
    bk = (
        float(1 - 2 * ((ja2 + ia1[1]) % 2)),
        float(1 - 2 * ((ia1[1] + ia2[1] + ia2[0] + ja1) % 2)),
        float(1 - 2 * (ia2[1] % 2)),
        float(1 - 2 * ((ja2 + ja1 + ia1[1]) % 2)),
    )
    t0 = math.sqrt(float((2 * ja1 + 1) * (2 * ja2 + 1))) * 2.0
    if lb1 == lb2:
        t0 *= math.sqrt(0.5)
    if lb3 == lb4:
        t0 *= math.sqrt(0.5)
    items: list[tuple[int, int, float]] = []
    if ja1 == ja2:  # vibm-278..293, the second-order monopole of a two-phonon level
        tkq = 0.0
        if lb1 == lb3 and lb2 == lb4:
            tkq = 1.0
        if lb1 == lb4 and lb2 == lb3:
            tkq += float(1 - 2 * ((ja1 + ia1[0] + ia1[1]) % 2))
        if tkq != 0.0:
            if lb1 == lb2:
                tkq *= 0.5
            for l in range(1, nbt1 + 1):
                if kmag[l] == 0:
                    items.append((l * (nbt1 + 2), 0, tkq * math.sqrt(2.0 * ja1 + 1.0) * ay))
    imin = max(imin, abs(ja1 - ja2))
    imax = min(imax, ja1 + ja2)
    for j in range(imin, imax + 1):
        for k in range(4):
            if lib[k] or j < ia4[k] or j > ia5[k] or (j + ia5[k]) % 2 != 0:
                continue
            t3 = (bk[k]
                  * _sixj(2 * ia1[k], 2 * ia2[k], 2 * j, 2 * ja2, 2 * ja1, 2 * ia3[k])
                  * _cg0(2 * ia1[k], 2 * ia2[k], 2 * j)
                  * float(1 - abs(p_ab + j) % 4))
            if abs(t3) < 1.0e-6:  # vibm-306
                continue
            items.append((ia6[k], j, t3 * t0 * ay))
    return items


def _compact(items: list[tuple[int, int, float]]) -> list[tuple[int, int, float]]:
    """vibm-337..368: merge duplicate `(iq1, iq2, iq3)` triples by summing `t`, keeping the
    first occurrence's position, then drop every element with `|t| <= 1e-12`. A port that skips
    the merge has the same physics and a different form-factor table, which would not line up
    with `quan`'s `niv` slices."""
    merged: list[list] = []
    index: dict[tuple[int, int], int] = {}
    for code, mult, t in items:
        hit = index.get((code, mult))
        if hit is None:
            index[(code, mult)] = len(merged)
            merged.append([code, mult, t])
        else:
            merged[hit][2] += t
    return [(c, m, t) for c, m, t in merged if abs(t) > _DROP]


def scheme_from_band(band: dict) -> tuple[VibmScheme, "object"]:
    """`(VibmScheme, band_beta)` for a `colltype V` target, from `reference.coupled_band`.

    The level and phonon cards are `ecisinput.f90:110-125`: the ground state's phonon card is a
    BLANK line for a vibrational target (`if (vibrational) write(9, '()')`), so `lecl` reads
    `iph(1,1) = 0`; every other level gets `iph(i), iband(i), 1`, which `lecl` stores as
    `npa(1,na) = iband(i)` and `npa(2,na) = 1` for a two-phonon state (lecl-204..208). The
    literal `1` in TALYS's format is the SECOND phonon's band index, not a flag -- and because
    `deformpar.f90` puts every V level of a two-phonon `.def` block in band 1, both phonons are
    band 1, so the pair is identical and `nbt1 = 1`.

    `ipi(1,iv)` is 1 for a negative-parity level and 0 otherwise (lecl-162..163, on the parity
    CHARACTER of the card, not relative to the target).

    TALYS: ecisinput.f90:1 (ecisinput)
    Test: G-2PH
    """
    iph = [int(x) for x in band["iphonon"]]
    vb = [int(x) for x in band["vibband"]]
    spin = [float(x) for x in band["spin"]]
    par = [int(x) for x in band["parity"]]
    levels = []
    for i in range(len(iph)):
        if i == 0:
            n, bands = 0, ()
        elif iph[i] <= 1:
            n, bands = 1, (vb[i],)
        else:
            n, bands = 2, (vb[i], 1)
        levels.append(VibLevel(n, bands, int(round(2 * spin[i])), 0 if par[i] > 0 else 1))
    phonons = Phonons(
        lam=tuple(int(x) for x in band["jband"]), kmag=tuple(int(x) for x in band["kmag"])
    )
    lo2 = any(x > 1 for x in iph)
    return reduced_matrix_elements(levels, phonons, lo2), band["band_beta"]
