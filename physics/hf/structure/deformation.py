"""Deformation parameters and collective-level assignments (deformation/*.def).

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T2 (physics/hf/CONTRACT.md §7). Acceptance test: A-struct (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    deformpar.f90:1 (deformpar)
    weakcoupling.f90:1 (weakcoupling)
    bdef.f90:1 (bdef)

Single-precision transcendental functions (exp, x**y) are evaluated in float64 and rounded to
float32, i.e. correctly rounded, which is what glibc's expf/powf return for these arguments;
numpy's own float32 kernels can differ in the last bit (seen once, Ba138 4+ deformation).

What deformpar.f90 does (reproduced branch by branch)
-----------------------------------------------------
1. Reads the nucleus block of `deformation/<Sym>.def` (unless `disctable 3`): collectivity type
   (S spherical, V vibrational, R rotational, A axially-deformed-but-spherical-OMP), deformation
   type (B = beta, D = deformation length), and per level its type and deformation parameters.
   Rotational band parameters go to `rotpar`, vibrational ones to `defpar`; for spherical
   nuclei (and levels demoted to 'D') a level's `deform` is the file value only for natural
   parity, ``parity = (-1)**J``.
2. Automatic rotational model for A > 150 nuclei at least 8 nucleons from a magic number when
   `autorot y` (default off).
3. Defaults for even-even-like nuclei (odd A skips): the first 2+, 3-, 4+ levels of a spherical
   nucleus get the systematics ``0.3 * {0.40 exp(-0.012 A) + 0.025 min(d, 5), 0.35 exp(-0.008 A),
   0.20 exp(-0.006 A)}``; every other natural-parity level without a value gets 0.02, and 0.02
   also replaces a systematic value when the level lies below 0.1 MeV. Deformation lengths
   (deftype D) multiply by ``1.24 A^(1/3)``. The loop runs over levels 0..numlev (40), not nlev.
4. Rigid-body moments of inertia for the ground state and the fission barriers.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from functools import cache
from typing import TYPE_CHECKING

import numpy as np

from physics.hf.core.constants import MAGIC, talys_constants
from physics.hf.structure.files import read_deformation_file

if TYPE_CHECKING:
    from physics.hf.input.defaults import Options, Params
    from physics.hf.structure.levels import Levels
    from physics.hf.structure.masses import Masses

__all__ = ["Deformation", "deformation", "weak_coupling", "bdef"]

NUMLEV = 40
NUMLEV2 = 300
NUMROTCC = 4
NUMBAR = 3
_F = np.float32


def _exp32(x) -> np.float32:
    return _F(math.exp(float(x)))


def _pow32(a, b) -> np.float32:
    return _F(math.pow(float(a), float(b)))


@dataclass(frozen=True)
class Deformation:
    """Deformation data of one nucleus (dimensionless; `irigid0`, `irigid` in TALYS's units of
    MeV^-1, from 0.4 m R^2 A / hbarc^2 with m in MeV and R in fm).

    `deform[k]` is the deformation parameter of level k (0..numlev2); `leveltype[k]` its type
    (R/V/D); `indexlevel`, `indexcc`, `vibband`, `iphonon` are indexed by the row of the .def
    block (1-based, as TALYS). `lband`, `Kband`, `defpar` are indexed by vibrational band.
    """

    Z: int
    A: int
    colltype: str
    deftype: str
    deform: np.ndarray  # (numlev2+1,)
    leveltype: tuple[str, ...]  # (numlev2+1,)
    rotpar: tuple[float, ...]  # (numrotcc+1,), index 1..4
    nrot: int
    defpar: np.ndarray  # (numlev2+1,) by band
    lband: np.ndarray
    Kband: np.ndarray
    indexlevel: np.ndarray
    indexcc: np.ndarray
    vibband: np.ndarray
    iphonon: np.ndarray
    ndef: int
    irigid0: float
    irigid: tuple[float, ...]  # (numbar+1,)


def _natpar(j: float) -> int:
    # natpar = int(sgn(int(jdis))): sgn(even) = 1, sgn(odd) = -1
    return 1 if int(j) % 2 == 0 else -1


def deformation(
    Z: int,
    A: int,
    options: Options,
    levels: Levels,
    masses: Masses,
    params: Params | None = None,
    flagautorot: bool | None = None,
) -> Deformation:
    """Deformation parameters per level as TALYS reads them (the `def. type`/`def. par.` columns of
    directE*.out). Dimensionless.

    `levels` must be the full `discrete_levels` result for this nucleus (its ``all_*`` arrays
    cover levels up to nlevmax2); `masses` supplies beta2/beta4 of the ground state; `params`
    supplies the barrier `beta2` (defaults 0.6, 0.8, 1.0). `flagautorot` overrides the option
    (levels.f90:163 switches it off for a nucleus with fewer than 2 file levels).

    TALYS: deformpar.f90:1 (deformpar)
    Test: A-struct
    """
    c = talys_constants()
    Zix, Nix = options.Zinit - Z, options.Ninit - (A - Z)
    N = A - Z
    autorot = options.flagautorot if flagautorot is None else flagautorot
    flagspher = options.flagspher
    k0 = options.k0
    maxrot, maxband = options.maxrot, options.maxband

    n_all = levels.nlevmax2
    jdis = np.zeros(NUMLEV2 + 1)
    parlev = np.ones(NUMLEV2 + 1, dtype=np.int64)
    edis = np.zeros(NUMLEV2 + 1)
    jdis[: n_all + 1] = levels.all_spin.numpy()
    parlev[: n_all + 1] = levels.all_parity.numpy().astype(np.int64)
    edis[: n_all + 1] = levels.all_e_mev.numpy()
    b2_gs = (
        float(masses.beta2[Zix, Nix])
        if Zix < masses.beta2.shape[0] and Nix < masses.beta2.shape[1]
        else 0.0
    )
    b4_gs = (
        float(masses.beta4[Zix, Nix])
        if Zix < masses.beta4.shape[0] and Nix < masses.beta4.shape[1]
        else 0.0
    )

    colltype = "S"
    deftype = "B"  # strucinitial.f90
    leveltype = ["D"] * (NUMLEV2 + 1)
    deform = np.zeros(NUMLEV2 + 1)
    defpar = np.zeros(NUMLEV2 + 1)
    lband = np.zeros(NUMLEV2 + 1, dtype=np.int64)
    Kband = np.zeros(NUMLEV2 + 1, dtype=np.int64)
    indexlevel = np.zeros(NUMLEV2 + 1, dtype=np.int64)
    indexcc = np.zeros(NUMLEV2 + 1, dtype=np.int64)
    vibband = np.zeros(NUMLEV2 + 1, dtype=np.int64)
    iphonon = np.zeros(NUMLEV2 + 1, dtype=np.int64)
    rotpar = [0.0] * (NUMROTCC + 1)
    nrot = 0
    ndef = 0

    block = read_deformation_file(Z, A) if options.disctable != 3 else None
    if block is not None:
        colltype1, deftype1, rows = block
        if colltype1 not in ("R", "A", "V"):
            colltype1 = "S"
        iirot = 1 if (flagspher and colltype1 == "A") else NUMROTCC
        if flagspher:
            colltype1 = "S"
        colltype = colltype1
        deftype = deftype1
        idef = irot = ii = 0
        deform1 = [0.0] * (NUMROTCC + 1)  # reset once per nucleus (deformpar.f90:140-142)
        for i, (nex, leveltype1, vibband1, lband1, kmag1, iphonon1, dvals) in enumerate(rows, 1):
            for k in range(1, iirot + 1):  # only iirot values are read; the rest persist
                deform1[k] = float(_F(dvals[k - 1]))
            if nex > NUMLEV2:
                continue
            idef += 1
            indexlevel[i] = nex
            if leveltype1 == "R":
                irot += 1
                if irot > maxrot + 1:
                    leveltype1 = "D"
            leveltype[nex] = leveltype1
            vibband[i] = vibband1
            if colltype == "R" and vibband1 > maxband:
                leveltype1 = "D"
            iphonon[i] = max(iphonon1, 1)
            goto130 = False
            if leveltype1 == "R" and rotpar[1] == 0.0:
                if nex == 0 and deform1[1] == 0.0:
                    deform1[1] = b2_gs
                    deform1[2] = b4_gs
                for k in range(1, NUMROTCC + 1):
                    rotpar[k] = deform1[k]
                    if deform1[k] == 0.0:
                        nrot = k - 1
                        goto130 = True
                        break
            if not goto130 and leveltype1 == "V" and defpar[vibband1] == 0.0:
                lband[vibband1] = lband1
                Kband[vibband1] = kmag1
                defpar[vibband1] = deform1[1]
            # label 130
            if colltype == "S" or leveltype1 == "D":
                if parlev[nex] == _natpar(jdis[nex]):
                    deform[nex] = deform1[1]
                if 1 < i <= NUMROTCC + 1 and leveltype1 == "R":
                    deform[nex] = rotpar[i - 1]
            else:
                ii += 1
                indexcc[ii] = nex
        ndef = idef

    distance = 1000
    for m in MAGIC:
        distance = min(abs(N - m), distance)
        distance = min(abs(Z - m), distance)
    odd = A % 2
    skip_to_400 = False
    if colltype == "S" and not flagspher and A > 150 and distance >= 8 and autorot:
        indexlevel[1] = 0
        indexcc[1] = 0
        leveltype[0] = "R"
        dspin = 2.0 if odd == 0 else 1.0
        ndef = maxrot + 1
        for i in range(2, ndef + 1):
            spin = jdis[0] + dspin * (i - 1)
            for nex in range(1, NUMLEV2 + 1):
                if spin == jdis[nex] and parlev[nex] == parlev[0]:
                    indexlevel[i] = nex
                    indexcc[i] = nex
                    leveltype[nex] = "R"
                    break
        if indexcc[ndef] != 0:
            colltype = "R"
        nrot = 2
        rotpar[1] = b2_gs
        rotpar[2] = b4_gs
        deftype = "B"
        if odd == 0:
            skip_to_400 = True

    if not skip_to_400:
        nrotlev = 0
        for nex in range(1, NUMLEV2 + 1):
            if leveltype[nex] == "R":
                nrotlev += 1
                if nrotlev > maxrot:
                    leveltype[nex] = "D"
        if odd == 0:
            first = colltype == "S"
            first2 = first3 = first4 = first
            typ = 2 * Zix + Nix
            betafactor = _F(0.3)
            a13 = _pow32(_F(A), _F(c["onethird"]))

            def _dl(x):
                # deform * 1.24 * (A**onethird), evaluated left to right in single precision
                return (_F(x) * _F(1.24)) * a13 if deftype == "D" else _F(x)

            for k in range(0, NUMLEV + 1):
                if k == 0 and typ == k0:
                    continue
                if colltype != "S" and leveltype[k] == "V":
                    continue
                if colltype == "A" and leveltype[k] == "R":
                    continue
                if colltype == "R" and leveltype[k] == "R":
                    continue
                if jdis[k] == 0.0:
                    continue
                if first2 and jdis[k] == 2.0 and parlev[k] == 1:
                    if leveltype[k] != "R" and deform[k] == 0.0:
                        v = betafactor * _F(0.40) * _exp32(_F(-0.012) * _F(A)) + _F(0.025) * _F(
                            min(distance, 5)
                        )
                        if edis[k] <= 0.1:
                            v = _F(0.02)
                        deform[k] = float(_F(_dl(v)))
                    first2 = False
                    continue
                if first3 and jdis[k] == 3.0 and parlev[k] == -1:
                    if leveltype[k] != "R" and deform[k] == 0.0:
                        v = betafactor * _F(0.35) * _exp32(_F(-0.008) * _F(A))
                        if edis[k] <= 0.1:
                            v = _F(0.02)
                        deform[k] = float(_F(_dl(v)))
                    first3 = False
                    continue
                if first4 and jdis[k] == 4.0 and parlev[k] == 1:
                    if leveltype[k] != "R" and deform[k] == 0.0:
                        v = betafactor * _F(0.20) * _exp32(_F(-0.006) * _F(A))
                        if edis[k] <= 0.1:
                            v = _F(0.02)
                        deform[k] = float(_F(_dl(v)))
                    first4 = False
                    continue
                if deform[k] != 0.0:
                    continue
                if parlev[k] == _natpar(jdis[k]):
                    deform[k] = 0.02
                deform[k] = float(_dl(deform[k]))

    # label 400
    irigid0, irigid = _rigid(A, Zix, Nix, b2_gs, params)
    return Deformation(
        Z=Z,
        A=A,
        colltype=colltype,
        deftype=deftype,
        deform=deform,
        leveltype=tuple(leveltype),
        rotpar=tuple(rotpar),
        nrot=nrot,
        defpar=defpar,
        lband=lband,
        Kband=Kband,
        indexlevel=indexlevel,
        indexcc=indexcc,
        vibband=vibband,
        iphonon=iphonon,
        ndef=ndef,
        irigid0=irigid0,
        irigid=irigid,
    )


@cache
def _irigid0(A: int) -> float:
    """deformpar.f90's label 400: `Irigid0`, a function of A alone."""
    c = talys_constants()
    R = _F(1.2) * _pow32(_F(A), _F(c["onethird"]))
    # ((0.4 R R A) in sgl) * parmass(1) * amu in dbl / (hbarc**2 in sgl), stored in sgl
    sgl_part = _F(0.4) * R * R * _F(A)
    hbarc2 = _F(c["hbarc"]) * _F(c["hbarc"])
    return float(_F(float(sgl_part) * c["parmass"][1] * c["amu"] / float(hbarc2)))


def _rigid(A: int, Zix: int, Nix: int, b2_gs: float, params,
           nbar: int = NUMBAR) -> tuple[float, tuple[float, ...]]:
    """deformpar.f90's label 400: `Irigid0` and `Irigid(0..nbar)` (numbar by default)."""
    irigid0 = _irigid0(A)
    barrier_beta2 = [b2_gs, 0.6, 0.8, 1.0]
    if nbar > 0 and params is not None and "beta2" in params:
        barrier_beta2 = [float(params.at("beta2", Zix, Nix, ib)) for ib in range(NUMBAR + 1)]
        barrier_beta2[0] = b2_gs
    irigid = tuple(
        float(_F((_F(1.0) + abs(_F(barrier_beta2[ib])) / _F(3.0)) * _F(irigid0)))
        for ib in range(nbar + 1)
    )
    return irigid0, irigid


def rigid_moments(Z: int, A: int, options: Options, masses: Masses, params: Params | None = None,
                  nbar: int = NUMBAR) -> tuple[float, tuple[float, ...]]:
    """`deformation(Z, A, ...).irigid0` and `.irigid` without the rest of deformpar: the rigid-body
    moments of inertia read nothing but A, the ground-state beta2 of the mass table and the
    barrier `beta2` parameters, so `densitypar` (which needs only these two) skips the
    deformation file and the level loops. The same numbers, bit for bit; `nbar` limits `irigid` to
    barriers 0..nbar (the ones `densitypar` stores).

    TALYS: deformpar.f90:1 (deformpar)
    Test: tests/hf/test_nx2_ld.py
    """
    Zix, Nix = options.Zinit - Z, options.Ninit - (A - Z)
    b2_gs = (
        float(masses.beta2[Zix, Nix])
        if Zix < masses.beta2.shape[0] and Nix < masses.beta2.shape[1]
        else 0.0
    )
    return _rigid(A, Zix, Nix, b2_gs, params, nbar)


def weak_coupling(
    target: Deformation,
    target_levels: Levels,
    core: Deformation,
    core_levels: Levels,
    options: Options,
) -> Deformation:
    """Deformation parameters of an odd-A target's levels from its even core (weak coupling):
    each deformed core level i spreads to the nearest unassigned 'D'-type target level with
    int(J) = j for every j in |J0 - Jc| .. J0 + Jc, searched outward from the first target level
    above the core level's energy, with ``factor = sqrt((2(j + 1/2) + 1) / ((2 Jc + 1)(2 J0 + 1)))``
    and a deformation-length conversion when the two deftypes differ. Returns the target with
    `deform` updated. Note that TALYS tests the TARGET's level type at the core level's index
    (weakcoupling.f90:112) -- reproduced.

    TALYS: weakcoupling.f90:1 (weakcoupling)
    Test: A-struct
    """
    c = talys_constants()
    A = target.A
    nmax2 = target_levels.nlevmax2
    te = np.zeros(NUMLEV2 + 1)
    tj = np.zeros(NUMLEV2 + 1)
    te[: nmax2 + 1] = target_levels.all_e_mev.numpy()
    tj[: nmax2 + 1] = target_levels.all_spin.numpy()
    ce = np.zeros(NUMLEV2 + 1)
    cj = np.zeros(NUMLEV2 + 1)
    cm = core_levels.nlevmax2
    ce[: cm + 1] = core_levels.all_e_mev.numpy()
    cj[: cm + 1] = core_levels.all_spin.numpy()
    deform = target.deform.copy()
    j0 = _F(tj[0])
    a13 = _pow32(_F(A), _F(c["onethird"]))
    for i in range(0, NUMLEV2 + 1):
        if i == 0:  # `i == 0 .and. type == k0`: nuclides.f90 always passes type = k0
            continue
        if target.leveltype[i] in ("R", "V"):
            continue
        if core.deform[i] == 0.0:
            continue
        middle = 0
        for i2 in range(1, NUMLEV2 + 1):
            if te[i2] > ce[i]:
                middle = i2 + 1
                break
        jc = _F(cj[i])
        spinbeg = abs(j0 - jc)
        spinend = j0 + jc
        for j in range(int(spinbeg), int(spinend) + 1):
            done = False
            for i3 in range(0, NUMLEV2 + 1):
                for i4 in (1, -1):
                    if i3 == 0 and i4 == -1:
                        break
                    i5 = middle + i4 * i3
                    if i5 < 1 or i5 > nmax2:
                        continue
                    if deform[i5] != 0.0:
                        continue
                    if target.leveltype[i5] != "D":
                        continue
                    if int(tj[i5]) == j:
                        factor = np.sqrt(
                            (_F(2.0) * (_F(j) + _F(0.5)) + _F(1.0))
                            / ((_F(2.0) * jc + _F(1.0)) * (_F(2.0) * j0 + _F(1.0)))
                        )
                        v = _F(factor) * _F(core.deform[i])
                        if target.deftype == "D" and core.deftype == "B":
                            v = (v * _F(1.24)) * a13
                        if target.deftype == "B" and core.deftype == "D":
                            v = v / (_F(1.24) * a13)
                        deform[i5] = float(_F(v))
                        done = True
                        break
                if done:
                    break
    from dataclasses import replace

    return replace(target, deform=deform)


def bdef(amass: float, zchar: float, epscloc: float) -> tuple[float, float, float]:
    """Liquid-drop deformation energy terms of the Brosa model: (cou, sym, b), single precision.
    Needs `fsurf` from the fission subsystem, so it is ported there (T11) and only anchored here.

    TALYS: bdef.f90:1 (bdef)
    Test: A-fis
    """
    raise NotImplementedError("bdef depends on fsurf (fission, T11)")
