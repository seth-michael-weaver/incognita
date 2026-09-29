"""Optical-model parameters for every particle type: Koning-Delaroche 2003 (n, p), the global
potentials TALYS uses for d, t, h, alpha, Soukhovitskii for actinides, the Coulomb radius.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T4 (physics/hf/CONTRACT.md §7). Acceptance test: A-omppar (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    omppar.f90:1 (omppar)
    kd03.f90:1 (kd03)
    kd03.f90:129 (jsonline)
    optical.f90:1 (optical)
    opticalnp.f90:1 (opticalnp)
    opticalalpha.f90:1 (opticalalpha)
    opticaldeut.f90:1 (opticaldeut)
    opticalcomp.f90:1 (opticalcomp)
    soukhovitskii.f90:1 (soukhovitskii)
    ompadjust.f90:1 (ompadjust)
    adjustf.f90:1 (adjustF)
    radius.f90:1 (radius)

Structure of the port. TALYS splits the work in two: `omppar` runs once per nucleus and stores
the energy-independent coefficients (v1..v4, w1..w4, d1..d3, geometry, Fermi energy) in module
globals; `optical` is then called at every energy and fills the 19 globals v, rv, av, ... that
ECIS reads. Here `omppar` returns a frozen `NucleonOMP` per nucleon type and the `optical*`
functions are pure functions of it, vectorised over an energy tensor. Every energy branch TALYS
takes with an `if` on `eopt` (the 1 GeV extension above Ejoin, the tabulated-file range, the
alternative-OMP blending windows) is a `torch.where`, so one call covers a whole grid.

Faithfulness notes (each is TALYS's behaviour, reproduced on purpose):

* `omppar` reduces the surface-absorption coefficient d1 by 0.85 for a non-spherical
  (`colltype /= 'S'`) nucleus both inside the local-file loop and again after the global block
  (omppar.f90:217, :267). A nucleus with a local parameter file and a deformed collective type is
  therefore reduced twice (0.85**2). The file header's `omptype` would suppress this for 'C'
  entries, but no file in `structure/optical/{neutron,proton}` carries one.
* The proton Coulomb radius is always the KD03 formula, even when a local file supplies rc0
  (omppar.f90:269-270 overwrite it after the loop).
* Composite particles (d, t, h, alpha) are built by `opticalcomp` from the neutron and proton
  potentials of the same residual at E/A (Watanabe). The spin-orbit geometry of the composite
  uses the nucleon *surface real* radius for rwd and the nucleon spin-orbit radius for rwso,
  and rc is the proton rc at the full energy, as in opticalcomp.f90:272-289.
* With TALYS's defaults the alpha potential is Avrigeanu 2014 (alphaomp 6, altomp(6) true), but
  opticalalpha only overwrites the variables it sets: rvd, avd, rvso, avso, rwso, awso keep the
  Watanabe composite values (times the adjust factors a second time).
* Adjustment factors (`v1adjust` ...) come from `Params` and are always applied. TALYS applies
  them only when `ompadjustp(k)` is set, which every one of those keywords sets
  (input_omppar.f90:243ff.), so at the defaults (all 1) the two agree and away from them the port
  is differentiable. The energy-dependent `adjust` ranges (adjust.f90) are not ported; the
  geometry ranges of `adjustF` are.

Not ported (contract §8): JLM and folding potentials (alphaomp 3-5, jlmomp).

The RIPL retrieval (`om_retrieve`, `riplomp_mod`) *is* ported, in :mod:`physics.hf.omp.ripl`:
the actinide default `riplomp(1) = 2408` (targets Z 90-97, A 228-249) is retrieved here by
`riplomp_table` and interpolated by `opticalnp`, exactly as omppar.f90:271-387 does. A user
`optmod` file, or any other already-retrieved table, still goes in through `tables=`.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass, replace
from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import torch
from torch import Tensor

from physics.hf.core.constants import MAGIC, PARA, PARN, PARZ, nuclide_symbol, talys_structure_path
from physics.hf.core.tensors import DTYPE

if TYPE_CHECKING:
    from physics.hf.input.defaults import Options, Params

# the 19 OMP columns in the order TALYS writes them (inverseecis.f90:361-365)
COLUMNS = (
    "v_mev", "rv_fm", "av_fm", "w_mev", "rw_fm", "aw_fm", "vd_mev", "rvd_fm", "avd_fm",
    "wd_mev", "rwd_fm", "awd_fm", "vso_mev", "rvso_fm", "avso_fm", "wso_mev", "rwso_fm",
    "awso_fm", "rc_fm",
)  # fmt: skip
# the column names in omppar_<k>.out, same order
TALYS_COLUMNS = (
    "V", "rv", "av", "W", "rw", "aw", "Vd", "rvd", "avd", "Wd", "rwd", "awd", "Vso", "rvso",
    "avso", "Wso", "rwso", "awso", "rc",
)  # fmt: skip

_ONETHIRD = 1.0 / 3.0


def _sgl(x: float) -> float:
    """A Fortran default `real` literal or list-directed read, as TALYS holds it."""
    return float(np.float32(x))


@dataclass(frozen=True)
class OMPParameters:
    # (C, particle, E) each; the 19 columns of omppar_*.out
    v_mev: Tensor
    rv_fm: Tensor
    av_fm: Tensor
    w_mev: Tensor
    rw_fm: Tensor
    aw_fm: Tensor
    vd_mev: Tensor
    rvd_fm: Tensor
    avd_fm: Tensor
    wd_mev: Tensor
    rwd_fm: Tensor
    awd_fm: Tensor
    vso_mev: Tensor
    rvso_fm: Tensor
    avso_fm: Tensor
    wso_mev: Tensor
    rwso_fm: Tensor
    awso_fm: Tensor
    rc_fm: Tensor

    def stack(self) -> Tensor:
        """All 19 columns along a new last axis, in omppar_*.out order."""
        return torch.stack([getattr(self, c) for c in COLUMNS], dim=-1)


@dataclass(frozen=True)
class NucleonOMP:
    """What `omppar` stores for one nucleus and one nucleon type (k = 1 neutron, 2 proton)."""

    ef_mev: float
    rc0_fm: float
    rv0_fm: float
    av0_fm: float
    v1_mev: float
    v2_per_mev: float
    v3_per_mev2: float
    v4_per_mev3: float
    w1_mev: float
    w2_mev: float
    w3_mev: float
    w4_mev: float
    rvd0_fm: float
    avd0_fm: float
    d1_mev: float
    d2_per_mev: float
    d3_mev: float
    rvso0_fm: float
    avso0_fm: float
    vso1_mev: float
    vso2_per_mev: float
    wso1_mev: float
    wso2_mev: float
    ompglobal: bool
    disp: bool


@dataclass(frozen=True)
class OMPTable:
    """A tabulated OMP (RIPL retrieval output or a user `optmod` file): energies (MeV) and the
    19 columns per energy, as vomp(Zix, Nix, k, nen, 1:19) (omppar.f90:352-387)."""

    e_mev: Tensor  # (L,)
    values: Tensor  # (L, 19)


# ------------------------------------------------------------------------------ database readers
def jsonline(line: str) -> float:
    """The value of one `"key": value,` line, read the way TALYS reads it (text between the colon
    and the first comma, list-directed into a default real).

    TALYS: kd03.f90:129 (jsonline)
    Test: A-omppar
    """
    col = line.index(":")
    comma = line.find(",")
    end = comma if comma >= 0 else len(line)
    return _sgl(float(line[col + 1 : end]))


@cache
def _kd03_file(path: str) -> tuple[str, ...]:
    return tuple(Path(path).read_text().splitlines())


def kd03(
    k: int, pruitt: str = "n", pruittset: int = 0, disp: bool = False, structure: Path | None = None
) -> dict[str, float]:
    """Global KD03 (or Pruitt et al.) nucleon OMP coefficients for particle k, read line by line
    in TALYS's fixed order. `disp` selects parameters_disp.json (flagdisp and flagglobaldisp,
    neutrons only).

    TALYS: kd03.f90:1 (kd03)
    Test: A-omppar
    """
    par, setn = "kd03", 0
    if pruitt in ("f", "y"):
        par = "pruitt_federal"
    if pruitt == "d":
        par = "pruitt_democratic"
    if pruitt != "n":
        setn = pruittset
    dispstring = "_disp" if (k == 1 and disp) else ""
    base = structure if structure is not None else talys_structure_path()
    f = base / "optical" / "global" / par / str(setn) / f"parameters{dispstring}.json"
    return dict(_kd03_values(str(f), k))


@cache
def _kd03_values(path: str, k: int) -> tuple[tuple[str, float], ...]:
    """NATIVEX2 `omp`: `kd03`'s reading of one parameter file for particle k, parsed once (a pure
    function of the file; `kd03` hands out a fresh dict)."""
    lines = iter(_kd03_file(path)[2:])
    out: dict[str, float] = {}

    def rd(name: str | None = None, only_k: int | None = None) -> None:
        x = jsonline(next(lines))
        if name is not None and (only_k is None or only_k == k):
            out[name] = x

    def skip2() -> None:
        next(lines)
        next(lines)

    rd("v1_0"), rd("v1_asymm"), rd("v1_A")
    rd("v2_0", 1), rd("v2_A", 1), rd("v3_0", 1), rd("v3_A", 1)
    rd("v2_0", 2), rd("v2_A", 2), rd("v3_0", 2), rd("v3_A", 2)
    rd("v4_0"), rd("rv_0"), rd("rv_A"), rd("av_0"), rd("av_A")
    skip2()
    rd("rc_0"), rd("rc_A"), rd("rc_A2")
    skip2()
    rd("vso1_0"), rd("vso1_A"), rd("vso2_0"), rd("rso_0"), rd("rso_A"), rd("aso_0")
    skip2()
    rd("wso1_0"), rd("wso2_0")
    skip2()
    rd("w1_0", 1), rd("w1_A", 1), rd("w1_0", 2), rd("w1_A", 2), rd("w2_0"), rd("w2_A")
    skip2()
    rd("d1_0"), rd("d1_asymm"), rd("d2_0"), rd("d2_A"), rd("d2_A2"), rd("d2_A3"), rd("d3_0")
    rd("rd_0"), rd("rd_A")
    rd("ad_0", 1), rd("ad_A", 1), rd("ad_0", 2), rd("ad_A", 2)
    return tuple(out.items())


@cache
def _local_omp_file(path: str) -> tuple[str, ...] | None:
    p = Path(path)
    return tuple(p.read_text().splitlines()) if p.is_file() else None


def _ff(s: str, widths: tuple[int, ...]) -> list[float]:
    """Fortran fixed-width real fields; blank reads as 0."""
    out, pos = [], 0
    for w in widths:
        field = s[pos : pos + w].strip()
        out.append(_sgl(float(field)) if field else 0.0)
        pos += w
    return out


def read_local_omp(
    Z: int,
    A: int,
    k: int,
    flagdisp: bool = False,
    flagjlm: bool = False,
    structure: Path | None = None,
) -> tuple[dict[str, float], bool] | None:
    """Nucleus-specific KD03 parameters from optical/{neutron,proton}/<p>-<El>.omp, or None when
    the element file or the isotope is absent. Returns (coefficients, disp). Without `flagdisp`
    TALYS stops after the first parameter set; with it the last set read wins.

    TALYS: omppar.f90:1 (omppar)
    Test: A-omppar
    """
    base = structure if structure is not None else talys_structure_path()
    sub, sym = ("neutron", "n") if k == 1 else ("proton", "p")
    lines = _local_omp_file(str(base / "optical" / sub / f"{sym}-{nuclide_symbol(Z)}.omp"))
    if lines is None:
        return None
    i = 0
    while i < len(lines):
        head = lines[i]
        if not head.strip():
            i += 1
            continue
        ia, nomp = int(head[4:8]), int(head[8:12])  # (4x, 2i4, 3x, a1)
        i += 1
        if ia != A:
            i += 4 * nomp
            continue
        rec: dict[str, float] = {}
        disp = False
        for _ in range(nomp):
            ef, rc0 = _ff(lines[i][4:], (7, 8))  # (4x, f7.2, f8.3)
            rv0, av0, v1, v2, v3, w1, w2 = _ff(lines[i + 1], (8, 8, 6, 10, 9, 6, 7))
            rvd0, avd0, d1, d2, d3 = _ff(lines[i + 2], (8, 8, 6, 10, 7))
            rvso0, avso0, vso1, vso2, wso1, wso2 = _ff(lines[i + 3], (8, 8, 6, 10, 6, 7))
            i += 4
            rec = dict(
                ef=ef,
                rc0=rc0,
                rv0=rv0,
                av0=av0,
                v1=v1,
                v2=v2,
                v3=v3,
                v4=_sgl(7.0e-9),
                w1=w1,
                w2=w2,
                rvd0=rvd0,
                avd0=avd0,
                d1=d1,
                d2=d2,
                d3=d3,
                rvso0=rvso0,
                avso0=avso0,
                vso1=vso1,
                vso2=vso2,
                wso1=wso1,
                wso2=wso2,
            )
            if not flagdisp:
                break
            disp = not (nomp == 1 or flagjlm)
        return rec, disp
    return None


def riplomp_table(
    Z: int,
    A: int,
    k: int,
    iref: int,
    enincmax_mev: float,
    structure: Path | None = None,
) -> tuple[OMPTable, float]:
    """The RIPL optical potential `iref` retrieved for particle k on (Z, A), as the `omp-table.dat`
    that `omppar` writes and reads back, plus the `Ef` of its header. This is the actinide default
    (`riplomp(1) = 2408`): see :mod:`physics.hf.omp.ripl` for the port of `om_retrieve` itself.

    `enincmax_mev` is the maximum incident energy of the run, which fixes where TALYS's table
    stops (`enincmax + 12`). The node positions below that do not depend on it, so a table built
    with a larger `enincmax` interpolates identically inside TALYS's range.

    TALYS: omppar.f90:271-387
    Test: A-omppar
    """
    from physics.hf.omp import ripl

    e, vals, ef = ripl.omp_table(Z, A, iref, enincmax_mev, structure=structure)
    index = ripl.read_om_index(str(ripl._ripl_dir(structure)))
    if ripl._PARSYM.get((PARZ[k], PARA[k])) != index[iref][0]:
        raise ValueError(f"RIPL OMP {iref} is not a particle-{k} potential")
    return OMPTable(torch.tensor(e, dtype=DTYPE), torch.tensor(vals, dtype=DTYPE)), ef


def _colltype(Z: int, A: int, options: Options, structure: Path | None = None) -> str:
    """Collective type of (Z, A) as deformpar reads it: the `.def` header letter (R, A, V; anything
    else and a missing entry give S), forced to S by `spherical y`. The automatic rotational
    assignment (flagautorot, off by default) needs discrete levels and raises.
    TODO(T2): replace with structure.deformation once it lands (deformpar.f90:115-263)."""
    if options.flagautorot:
        raise NotImplementedError("flagautorot needs discrete levels: pass colltype= (TODO(T2))")
    if options.flagspher or options.disctable == 3:
        return "S"
    base = structure if structure is not None else talys_structure_path()
    f = base / "deformation" / f"{nuclide_symbol(Z)}.def"
    lines = _local_omp_file(str(f))
    if lines is None:
        return "S"
    i = 0
    while i < len(lines):
        head = lines[i]
        if not head.strip():
            i += 1
            continue
        ia, ndisc = int(head[4:8]), int(head[8:12])  # (4x, 2i4, 2(3x, a1))
        ct = head[15:16]
        if ia == A:
            return ct if ct in ("R", "A", "V") else "S"
        i += 1 + ndisc
    return "S"


def omppar(
    Z: int,
    A: int,
    options: Options,
    *,
    colltype: str | None = None,  # TODO(T2): deformpar.f90 colltype; None reads the .def file
    sep_energy_mev: Mapping[int, tuple[float, float]] | None = None,  # TODO(T2)
    structure: Path | None = None,
) -> dict[int, NucleonOMP]:
    """Energy-independent neutron and proton OMP coefficients of nucleus (Z, A): local file if
    TALYS finds one (flaglocalomp), otherwise the KD03 global formulas; Fermi energy from the
    global fit (flagglobalfermi) or, otherwise, from separation energies
    `sep_energy_mev[k] = (S_k(this nucleus), S_k(the neighbour with one fewer k))`; the 1 GeV
    extension coefficients w3, w4.

    TALYS: omppar.f90:1 (omppar)
    Test: A-omppar
    """
    N = A - Z
    if structure is None:  # NATIVEX2 `omp`: resolved once, not per helper (a stat() each)
        structure = talys_structure_path()
    if colltype is None:
        colltype = _colltype(Z, A, options, structure)
    rec: dict[int, dict[str, float]] = {1: {}, 2: {}}
    disp = {1: False, 2: False}
    omptype = " "  # no local file in the TALYS database carries 'C'
    if options.flaglocalomp:
        for k in (1, 2):
            base = structure
            sub, sym = ("neutron", "n") if k == 1 else ("proton", "p")
            path = base / "optical" / sub / f"{sym}-{nuclide_symbol(Z)}.omp"
            exists = _local_omp_file(str(path)) is not None  # cached; the file's is_file()
            if not exists:
                continue
            got = read_local_omp(Z, A, k, options.flagdisp, options.flagjlm, structure)
            if got is not None:
                rec[k], disp[k] = got
            if colltype != "S" and omptype != "C":  # omppar.f90:217
                rec[k]["d1"] = 0.85 * rec[k].get("d1", 0.0)
    eta = {1: -1.0, 2: 1.0}
    ompglobal = {1: False, 2: False}
    kd = None
    for k in (1, 2):
        if rec[k].get("rv0", 0.0) == 0.0:
            if options.flagdisp:
                disp[k] = k == 1 and options.flagglobaldisp
            ompglobal[k] = True
            if options.flagglobalfermi:
                ef = -11.2814 + 0.02646 * A if k == 1 else -8.4075 + 0.01378 * A
            else:
                if sep_energy_mev is None:
                    raise ValueError("flagglobalfermi n needs sep_energy_mev (TODO(T2))")
                s_here, s_prev = sep_energy_mev[k]
                ef = -0.5 * (s_here + s_prev)
            kd = kd03(
                k,
                options.pruitt,
                options.pruittset,
                k == 1 and options.flagdisp and options.flagglobaldisp,
                structure,
            )
            rec[k] = dict(
                ef=ef,
                rc0=rec[k].get("rc0", 0.0),
                rv0=kd["rv_0"] - kd["rv_A"] * A ** (-_ONETHIRD),
                av0=kd["av_0"] - kd["av_A"] * A,
                v1=kd["v1_0"] + eta[k] * kd["v1_asymm"] * (N - Z) / A - kd["v1_A"] * A,
                v2=kd["v2_0"] + eta[k] * kd["v2_A"] * A,
                v3=kd["v3_0"] + eta[k] * kd["v3_A"] * A,
                v4=kd["v4_0"],
                w1=kd["w1_0"] + kd["w1_A"] * A,
                w2=kd["w2_0"] + kd["w2_A"] * A,
                rvd0=kd["rd_0"] - kd["rd_A"] * A**_ONETHIRD,
                avd0=kd["ad_0"] + eta[k] * kd["ad_A"] * A,
                d1=kd["d1_0"] + eta[k] * kd["d1_asymm"] * (N - Z) / A,
                d2=kd["d2_0"] + kd["d2_A"] / (1.0 + math.exp((A - kd["d2_A3"]) / kd["d2_A2"])),
                d3=kd["d3_0"],
                rvso0=kd["rso_0"] - kd["rso_A"] * A ** (-_ONETHIRD),
                avso0=kd["aso_0"],
                vso1=kd["vso1_0"] + kd["vso1_A"] * A,
                vso2=kd["vso2_0"],
                wso1=kd["wso1_0"],
                wso2=kd["wso2_0"],
            )
        if colltype != "S" and omptype != "C":  # omppar.f90:267
            rec[k]["d1"] = 0.85 * rec[k]["d1"]
    # omppar.f90:269-270: the Coulomb radius is KD03's for protons, zero for neutrons. The rc_*
    # coefficients are module globals set by any kd03 call; they do not depend on k.
    if kd is None:
        kd = kd03(2, options.pruitt, options.pruittset, False, structure)
    rc0 = {1: 0.0, 2: kd["rc_0"] + kd["rc_A"] * A ** (-2.0 / 3.0) + kd["rc_A2"] * A ** (-5.0 / 3.0)}
    out = {}
    for k in (1, 2):
        r = rec[k]
        out[k] = NucleonOMP(
            ef_mev=r["ef"], rc0_fm=rc0[k], rv0_fm=r["rv0"], av0_fm=r["av0"], v1_mev=r["v1"],
            v2_per_mev=r["v2"], v3_per_mev2=r["v3"], v4_per_mev3=r["v4"], w1_mev=r["w1"],
            w2_mev=r["w2"], w3_mev=25.0 - 0.0417 * A, w4_mev=250.0, rvd0_fm=r["rvd0"],
            avd0_fm=r["avd0"], d1_mev=r["d1"], d2_per_mev=r["d2"], d3_mev=r["d3"],
            rvso0_fm=r["rvso0"], avso0_fm=r["avso0"], vso1_mev=r["vso1"], vso2_per_mev=r["vso2"],
            wso1_mev=r["wso1"], wso2_mev=r["wso2"], ompglobal=ompglobal[k], disp=disp[k],
        )  # fmt: skip
    return out


# ------------------------------------------------------------------------------ adjustment factors
_ADJ = {  # opticalnp's F* variables -> Params keyword (ompadjust.f90)
    "Fv1": "v1adjust", "Fv2": "v2adjust", "Fv3": "v3adjust", "Fv4": "v4adjust",
    "Frv": "rvadjust", "Fav": "avadjust", "Fw1": "w1adjust", "Fw2": "w2adjust",
    "Fw3": "w3adjust", "Fw4": "w4adjust", "Frw": "rwadjust", "Faw": "awadjust",
    "Frvd": "rvdadjust", "Favd": "avdadjust", "Fd1": "d1adjust", "Fd2": "d2adjust",
    "Fd3": "d3adjust", "Frwd": "rwdadjust", "Fawd": "awdadjust", "Fvso1": "vso1adjust",
    "Fvso2": "vso2adjust", "Frvso": "rvsoadjust", "Favso": "avsoadjust", "Fwso1": "wso1adjust",
    "Fwso2": "wso2adjust", "Frwso": "rwsoadjust", "Fawso": "awsoadjust", "Frc": "rcadjust",
}  # fmt: skip


def ompadjust(params: Params | None, k: int) -> dict[str, Tensor | float]:
    """The multiplicative OMP adjustment factors F* for particle type k (0 = the projectile when
    it is also the ejectile, flagompejec).

    TALYS: ompadjust.f90:1 (ompadjust)
    Test: A-omppar
    """
    if params is None:
        return dict.fromkeys(_ADJ, 1.0)
    return {f: params[key][k] for f, key in _ADJ.items()}


def ejectile_params(params: Params | None, projectile: int = 1) -> Params | None:
    """`params` as TALYS's inverse channels see them: the projectile's type, leaving as an
    ejectile, takes the type-0 `ompadjust` factors (flagompejec), so `rvadjust n 0.96` moves the
    incident channel only and every outgoing neutron keeps the unadjusted potential. Type 0 is
    the photon slot, which nothing sets, so its factors are 1. The `ompadjustF` energy ranges
    stay keyed on the particle itself (opticalnp.f90:311 uses k, not ktype). Returns `params`
    itself -- no copy, so every cache keyed on it is untouched -- when the two rows already agree,
    which is every run at TALYS defaults.

    OMPDEF found the port applied the projectile's factors to its outgoing channels too
    (PORTLEVER's 0.041 dex W-182 departure from TALYS at 0.3-1 MeV under `INCOGNITA_OMP_REGION`).

    TALYS: inverseecis.f90 (flagompejec, line 220), opticalnp.f90:175, opticalcomp.f90:162
    Test: tests/hf/test_ompdef.py
    """
    if params is None:
        return None
    keys = list(_ADJ.values())
    if all(bool(torch.equal(params[k][projectile], params[k][0])) for k in keys):
        return params
    vals = dict(params.values)
    for k in keys:
        t = vals[k].clone()
        t[projectile] = t[0]
        vals[k] = t
    return type(params)(values=vals)


def adjustF(e_mev: Tensor, params: Params | None, k: int, omptype: int) -> Tensor | float:
    """Energy-dependent geometry factor from the `ompadjustE1/E2/D/s` ranges (1.0 outside them).

    TALYS: adjustf.f90:1 (adjustF)
    Test: A-omppar
    """
    if params is None or "ompadjuste1" not in params:
        return 1.0
    e1 = params["ompadjuste1"][k, omptype - 1]
    e2 = params["ompadjuste2"][k, omptype - 1]
    dr = params["ompadjustd"][k, omptype - 1]
    sr = params["ompadjusts"][k, omptype - 1]
    if not bool((e2 > e1).any()):
        return 1.0
    factor = torch.ones_like(e_mev)
    done = torch.zeros_like(e_mev, dtype=torch.bool)
    for nr in range(e1.numel()):
        elow, eup = e1[nr], e2[nr]
        if not bool(eup > elow):
            break  # ranges are filled in order; nrange = number assigned
        inside = (e_mev > elow) & (e_mev < eup) & ~done
        emid = 0.5 * (elow + eup)
        d = 0.01 * dr[nr]
        sigma = torch.where(sr[nr] == 0.0, (eup - emid) / 2.0, sr[nr])
        expo0 = (eup - emid) ** 2 / (2.0 * sigma**2)
        offset = torch.where(expo0 <= 80.0, -d * torch.exp(-expo0), torch.zeros_like(d))
        expo = (e_mev - emid) ** 2 / (2.0 * sigma**2)
        f = torch.where(
            expo <= 80.0, 1.0 + d * torch.exp(-expo.clamp(max=80.0)) + offset, 1.0 + offset
        )
        factor = torch.where(inside, f, factor)
        done = done | inside
    return factor


def _apply_geometry_ranges(
    out: dict[str, Tensor], e: Tensor, params: Params | None, k: int
) -> None:
    """opticalnp.f90:313-338 / opticalcomp.f90:354-379: the `ompadjustF(k)` block."""
    names = (
        "rv_fm",
        "av_fm",
        "rw_fm",
        "aw_fm",
        "rvd_fm",
        "avd_fm",
        "rwd_fm",
        "awd_fm",
        "rvso_fm",
        "avso_fm",
        "rwso_fm",
        "awso_fm",
        "rc_fm",
    )
    for omptype, name in enumerate(names, start=1):
        f = adjustF(e, params, k, omptype)
        if not isinstance(f, float):
            out[name] = f * out[name]


# ------------------------------------------------------------------------------ potentials
def _t(x, like: Tensor) -> Tensor:
    return torch.as_tensor(x, dtype=DTYPE, device=like.device).expand_as(like)


def _interp_table(table: OMPTable, e: Tensor, F: Mapping[str, Tensor | float]):
    """opticalnp.f90:190-224: linear interpolation in a tabulated OMP; returns (inside, 19 cols)."""
    te = table.e_mev.to(dtype=DTYPE, device=e.device)
    tv = table.values.to(dtype=DTYPE, device=e.device)
    inside = (e >= te[0]) & (e <= te[-1])
    # the first segment with elow <= e <= eup, as the Fortran loop finds it
    seg = torch.searchsorted(te, e.clamp(te[0], te[-1]), right=False).clamp(1, len(te) - 1)
    elow, eup = te[seg - 1], te[seg]
    eint = (e - elow) / torch.where(eup > elow, eup - elow, torch.ones_like(eup))
    vloc = tv[seg - 1] + eint[..., None] * (tv[seg] - tv[seg - 1])
    fac = (
        "Fv1",
        "Frv",
        "Fav",
        "Fw1",
        "Frw",
        "Faw",
        "Fd1",
        "Frvd",
        "Favd",
        "Fd1",
        "Frwd",
        "Fawd",
        "Fvso1",
        "Frvso",
        "Favso",
        "Fwso1",
        "Frwso",
        "Fawso",
        "Frc",
    )
    cols = {c: F[f] * vloc[..., i] for i, (c, f) in enumerate(zip(COLUMNS, fac, strict=True))}
    return inside, cols


@cache
def soukhovitskii_fermi(options: "Options") -> dict[int, float]:
    """`eferm` of soukhovitskii.f90:103-107, per particle: `-(S(0,1,1) + S(0,0,1))/2` for a
    neutron and `-(S(1,0,2) + S(0,0,2))/2` for a proton.

    Those three indices are ABSOLUTE, not relative to the nucleus the potential is for, so the
    Fermi energy is a property of the run: (0, 0) is the initial compound nucleus, (0, 1) the
    nucleus one neutron below it and (1, 0) the one one proton below it. One value per run
    therefore serves every residual, which is what TALYS does -- `soukhovitskii` reads the same
    three separation energies whatever `(Zix, Nix)` it was called for.

    This closes the TODO(T2) gap that made Th-227 the one crash of CHART1's 482 nuclides: the
    RIPL actinide table `riplomp(1) = 2408` covers A 228-249, so a Z >= 90 nucleus below A 228
    falls to the global potential, where `flagsoukho` sends it to Soukhovitskii and there was
    nothing to read the Fermi energy off. `S` comes from `structure.masses` at the run's mass
    model; a `massnucleus`/`massexcess` override is not applied here, and a caller that wants one
    passes `soukho_eferm_mev=` explicitly, which still wins.

    TALYS: soukhovitskii.f90:1 (soukhovitskii), separation.f90:1 (separation)
    Test: A-omppar / CHARTFIX
    """
    from physics.hf.structure.masses import masses

    m = masses(options)
    return {1: -0.5 * (float(m.s_mev[0, 1, 1]) + float(m.s_mev[0, 0, 1])),
            2: -0.5 * (float(m.s_mev[1, 0, 2]) + float(m.s_mev[0, 0, 2]))}


def soukhovitskii(
    k: int, Z: int, A: int, e_mev: Tensor, eferm_mev: float, F: Mapping[str, Tensor | float]
) -> dict[str, Tensor]:
    """Soukhovitskii et al., J. Phys. G30, 905 (2004) dispersive CC potential for actinides, for
    k = 1 (n) or 2 (p). `eferm_mev` = -(S(0,1,k) + S(0,0,k))/2 of the compound-nucleus indexed
    nuclei, as TALYS computes it.

    TALYS: soukhovitskii.f90:1 (soukhovitskii)
    Test: A-omppar
    """
    e = e_mev
    asym = (A - 2.0 * Z) / A
    f = torch.clamp(e - eferm_mev, min=-20.0)
    cviso, v0r, var, vrdisp, v1r, v2r, lam = 10.5, -41.45, -0.06667, 92.44, 0.03, 2.05e-4, 3.9075e-3
    viso = 1.0 + ((-1.0) ** k) * cviso * asym / (v0r + var * (A - 232.0) + vrdisp)
    v = (v0r + var * (A - 232.0) + v1r * f + v2r * f**2 + vrdisp * torch.exp(-lam * f)) * viso
    if k == 2:
        phicoul = (lam * vrdisp * torch.exp(-lam * f) - v1r - 2.0 * v2r * f) * viso
        v = v + 0.9 * Z / A**_ONETHIRD * phicoul
    out = {"v_mev": F["Fv1"] * v}
    out["rv_fm"] = F["Frv"] * 1.245 * (1.0 - 0.05 * f**2 / (f**2 + 100.0**2))
    out["av_fm"] = F["Fav"] * (0.660 + 2.53e-4 * e)
    w1, w2 = F["Fw1"] * 14.74, F["Fw2"] * 81.63
    out["w_mev"] = w1 * f**2 / (f**2 + w2**2)
    out["rw_fm"] = _t(F["Frw"] * 1.2476, e)
    out["aw_fm"] = _t(F["Faw"] * 0.594, e)
    out["vd_mev"] = torch.zeros_like(e)
    out["rvd_fm"] = _t(F["Frvd"] * 1.2080, e)
    out["avd_fm"] = _t(F["Favd"] * 0.614, e)
    d1 = F["Fd1"] * (17.38 + 0.03833 * (A - 232.0) + ((-1.0) ** k) * 24.0 * asym)
    d2, d3 = F["Fd2"] * 0.01759, F["Fd3"] * 11.79
    out["wd_mev"] = d1 * f**2 * torch.exp(-d2 * f) / (f**2 + d3**2)
    out["rwd_fm"] = _t(F["Frwd"] * 1.2080, e)
    out["awd_fm"] = _t(F["Fawd"] * 0.614, e)
    vso1, vso2 = F["Fvso1"] * 5.86, F["Fvso2"] * 0.0050
    out["vso_mev"] = vso1 * torch.exp(-vso2 * f)
    out["rvso_fm"] = _t(F["Frvso"] * 1.1213, e)
    out["avso_fm"] = _t(F["Favso"] * 0.59, e)
    wso1, wso2 = -3.1 * F["Fwso1"], F["Fwso2"] * 160.0
    out["wso_mev"] = wso1 * f**2 / (f**2 + wso2**2)
    out["rwso_fm"] = _t(F["Frwso"] * 1.1213, e)
    out["awso_fm"] = _t(F["Fawso"] * 0.59, e)
    out["rc_fm"] = _t(0.0 if k == 1 else F["Frc"] * 1.2643, e)
    return out


@dataclass(frozen=True)
class JoinValues:
    """V0(k), Vjoin(k), Wjoin(k): the potential of the k-residual at 0 and at Ejoin, computed in
    omppar for the 1 GeV extension (omppar.f90:425-435). Zero when enincmax <= Ejoin."""

    v0_mev: float = 0.0
    vjoin_mev: float = 0.0
    wjoin_mev: float = 0.0


def opticalnp(
    nuc: NucleonOMP,
    k: int,
    Z: int,
    A: int,
    e_mev: Tensor,
    params: Params | None = None,
    *,
    adjust_type: int | None = None,
    options: Options | None = None,
    table: OMPTable | None = None,
    join: JoinValues | None = None,
    soukho_eferm_mev: float | None = None,
) -> dict[str, Tensor]:
    """The 19 OMP quantities for a neutron (k = 1) or proton (k = 2) on nucleus (Z, A) at
    energies e_mev: interpolated from `table` where it covers the energy, else Soukhovitskii for
    actinides with a global OMP (flagsoukho, Z >= 90), else the KD03 energy dependence with the
    Coulomb correction for global proton potentials and the 1 GeV extension above Ejoin.
    `adjust_type` is the particle index whose adjust factors apply (0 for the projectile as
    ejectile, flagompejec); default k.

    TALYS: opticalnp.f90:1 (opticalnp)
    Test: A-omppar
    """
    e = torch.clamp(torch.as_tensor(e_mev, dtype=DTYPE), min=0.0)  # optical.f90:24
    F = ompadjust(params, k if adjust_type is None else adjust_type)
    ejoin = 200.0 if params is None else params["ejoin"][k]
    vinfadjust = 1.0 if params is None else params["vinfadjust"][k]
    flagsoukho = options.flagsoukho if options is not None else True
    flagsoukhoinp = options.flagsoukhoinp if options is not None else False

    if flagsoukhoinp or (flagsoukho and Z >= 90 and nuc.ompglobal):
        if soukho_eferm_mev is None:
            if options is None:
                raise ValueError(
                    "Soukhovitskii OMP needs soukho_eferm_mev or `options` to read it off"
                )
            soukho_eferm_mev = soukhovitskii_fermi(options)[k]
        out = soukhovitskii(k, Z, A, e, soukho_eferm_mev, F)
    else:
        f = e - nuc.ef_mev
        rc = F["Frc"] * nuc.rc0_fm
        v1, v2 = F["Fv1"] * nuc.v1_mev, F["Fv2"] * nuc.v2_per_mev
        v3, v4 = F["Fv3"] * nuc.v3_per_mev2, F["Fv4"] * nuc.v4_per_mev3
        if k == 2 and nuc.ompglobal:
            vc = 1.73 / rc * Z / (A**_ONETHIRD)
            vcoul = vc * v1 * (v2 - 2.0 * v3 * f + 3.0 * v4 * f**2)
        else:
            vcoul = torch.zeros_like(e)
        low = e <= ejoin
        fjoin = ejoin - nuc.ef_mev
        v_low = v1 * (1.0 - v2 * f + v3 * f**2 - v4 * f**3) + vcoul
        jv = join if join is not None else JoinValues()
        vinf = -vinfadjust * 30.0
        v0term = jv.v0_mev - vinf
        vterm = (jv.vjoin_mev - vinf) / v0term if v0term > 0 else torch.as_tensor(-1.0)
        vterm_t = torch.as_tensor(vterm, dtype=DTYPE)
        safe_log = torch.log(torch.where(vterm_t > 0, vterm_t, torch.ones_like(vterm_t)))
        v_high = torch.where(
            (torch.as_tensor(v0term) > 0) & (vterm_t > 0),
            vinf + v0term * torch.exp(f / fjoin * safe_log),
            _t(vinf, e),
        )
        w1, w2 = F["Fw1"] * nuc.w1_mev, F["Fw2"] * nuc.w2_mev
        w3, w4 = F["Fw3"] * nuc.w3_mev, F["Fw4"] * nuc.w4_mev
        w_low = w1 * f**2 / (f**2 + w2**2)
        w_high = jv.wjoin_mev - w3 * fjoin**4 / (fjoin**4 + w4**4) + w3 * f**4 / (f**4 + w4**4)
        d1, d2, d3 = F["Fd1"] * nuc.d1_mev, F["Fd2"] * nuc.d2_per_mev, F["Fd3"] * nuc.d3_mev
        vso1, vso2 = F["Fvso1"] * nuc.vso1_mev, F["Fvso2"] * nuc.vso2_per_mev
        wso1, wso2 = F["Fwso1"] * nuc.wso1_mev, F["Fwso2"] * nuc.wso2_mev
        out = {
            "v_mev": torch.where(low, v_low, v_high),
            "rv_fm": _t(F["Frv"] * nuc.rv0_fm, e),
            "av_fm": _t(F["Fav"] * nuc.av0_fm, e),
            "w_mev": torch.where(low, w_low, w_high),
            "rw_fm": _t(F["Frw"] * nuc.rv0_fm, e),
            "aw_fm": _t(F["Faw"] * nuc.av0_fm, e),
            "vd_mev": torch.zeros_like(e),
            "rvd_fm": _t(F["Frvd"] * nuc.rvd0_fm, e),
            "avd_fm": _t(F["Favd"] * nuc.avd0_fm, e),
            "wd_mev": d1 * f**2 * torch.exp(-d2 * f) / (f**2 + d3**2),
            "rwd_fm": _t(F["Frwd"] * nuc.rvd0_fm, e),
            "awd_fm": _t(F["Fawd"] * nuc.avd0_fm, e),
            "vso_mev": vso1 * torch.exp(-vso2 * f),
            "rvso_fm": _t(F["Frvso"] * nuc.rvso0_fm, e),
            "avso_fm": _t(F["Favso"] * nuc.avso0_fm, e),
            "wso_mev": wso1 * f**2 / (f**2 + wso2**2),
            "rwso_fm": _t(F["Frwso"] * nuc.rvso0_fm, e),
            "awso_fm": _t(F["Fawso"] * nuc.avso0_fm, e),
            "rc_fm": _t(rc, e),
        }
    if table is not None:
        inside, tab = _interp_table(table, e, F)
        out = {c: torch.where(inside, _t(tab[c], e), _t(out[c], e)) for c in COLUMNS}
    _apply_geometry_ranges(out, e, params, k if adjust_type is None else adjust_type)
    return out


def opticaldeut(
    Z: int,
    A: int,
    e_mev: Tensor,
    deuteronomp: int,
    F: Mapping[str, Tensor | float],
    prev: Mapping[str, Tensor],
) -> dict[str, Tensor]:
    """Alternative deuteron potentials (deuteronomp 2 Daehnick, 3 Bojowald, 4 Han, 5 An & Cai);
    variables a model does not set keep their `prev` (Watanabe) values, as the Fortran globals do.

    TALYS: opticaldeut.f90:1 (opticaldeut)
    Test: A-omppar
    """
    e = e_mev
    N = A - Z
    a13 = A**_ONETHIRD
    asym = (N - Z) / A
    o = dict(prev)
    z = torch.zeros_like(e)
    if deuteronomp == 2:
        beta = -((0.01 * e) ** 2)
        summu = sum(math.exp(-((0.5 * (m - N)) ** 2)) for m in MAGIC)
        o.update(
            v_mev=88.0 + 0.88 * Z / a13 - 0.283 * e,
            rv_fm=_t(1.17, e),
            av_fm=0.717 + 0.0012 * e,
            w_mev=(12 + 0.031 * e) * (1.0 - torch.exp(beta)),
            rw_fm=1.376 - 0.01 * torch.sqrt(e),
            aw_fm=_t(0.52 + 0.07 * a13 - 0.04 * summu, e),
            vd_mev=z,
        )
        o.update(rvd_fm=o["rw_fm"], avd_fm=o["aw_fm"], wd_mev=(12.0 + 0.031 * e) * torch.exp(beta))
        o.update(
            rwd_fm=o["rvd_fm"],
            awd_fm=o["avd_fm"],
            vso_mev=_t(5.0, e),
            rvso_fm=_t(1.04, e),
            avso_fm=_t(0.60, e),
            wso_mev=0.37 * a13 - 0.03 * e,
            rwso_fm=_t(0.80, e),
            awso_fm=_t(0.25, e),
            rc_fm=_t(1.30, e),
        )
    elif deuteronomp == 3:
        w = torch.clamp(0.132 * (e - 45.0), min=0.0)
        o.update(
            v_mev=81.32 - 0.24 * e + 1.43 * Z / a13,
            rv_fm=_t(1.18, e),
            av_fm=_t(0.636 + 0.035 * a13, e),
            w_mev=w,
            rw_fm=_t(1.27, e),
            aw_fm=_t(0.768 + 0.021 * a13, e),
            vd_mev=z,
        )
        o.update(
            rvd_fm=o["rw_fm"],
            avd_fm=o["aw_fm"],
            wd_mev=torch.clamp(7.80 + 1.04 * a13 - 0.712 * w, min=0.0),
        )
        rvso = _t(0.78 + 0.038 * a13, e)
        o.update(
            rwd_fm=o["rvd_fm"],
            awd_fm=o["avd_fm"],
            vso_mev=_t(6.0, e),
            rvso_fm=rvso,
            avso_fm=rvso,
            wso_mev=z,
            rwso_fm=rvso,
            awso_fm=rvso,
            rc_fm=_t(1.30, e),
        )
    elif deuteronomp == 4:
        o.update(
            v_mev=82.18 - 0.148 * e - 0.000886 * e * e - 34.811 * asym + 1.058 * Z / a13,
            rv_fm=_t(1.174, e),
            av_fm=_t(0.809, e),
            w_mev=torch.clamp(-4.916 + 0.0555 * e + 4.42e-5 * e * e + 35.0 * asym, min=0.0),
            rw_fm=_t(1.563, e),
            aw_fm=_t(0.700 + 0.045 * a13, e),
            vd_mev=z,
            rvd_fm=_t(1.328, e),
            avd_fm=_t(0.465 + 0.045 * a13, e),
            wd_mev=20.968 - 0.0794 * e - 43.398 * asym,
            vso_mev=_t(3.703, e),
            rvso_fm=_t(1.234, e),
            avso_fm=_t(0.813, e),
            wso_mev=_t(-0.206, e),
            rc_fm=_t(1.698, e),
        )
        o.update(rwd_fm=o["rvd_fm"], awd_fm=o["avd_fm"], rwso_fm=o["rvso_fm"], awso_fm=o["avso_fm"])
    elif deuteronomp == 5:
        o.update(
            v_mev=91.85 - 0.249 * e - 0.000116 * e * e + 0.642 * Z / a13,
            rv_fm=_t(1.152 - 0.00776 / a13, e),
            av_fm=_t(0.719 + 0.0126 * a13, e),
            w_mev=1.104 + 0.0622 * e,
            rw_fm=_t(1.305 + 0.0997 / a13, e),
            aw_fm=_t(0.855 - 0.100 * a13, e),
            vd_mev=z,
            rvd_fm=_t(1.334 + 0.152 / a13, e),
            avd_fm=_t(0.531 + 0.062 * a13, e),
            wd_mev=10.83 - 0.0306 * e,
            vso_mev=_t(3.557, e),
            rvso_fm=_t(0.972, e),
            avso_fm=_t(1.011, e),
            wso_mev=z,
            rc_fm=_t(1.303, e),
        )
        o.update(rwd_fm=o["rvd_fm"], awd_fm=o["avd_fm"], rwso_fm=o["rvso_fm"], awso_fm=o["avso_fm"])
    return _final_adjust(o, F)


def _final_adjust(o: dict[str, Tensor], F: Mapping[str, Tensor | float]) -> dict[str, Tensor]:
    """opticaldeut.f90:198-216 / opticalalpha.f90:186-204: `v = Fv1 * v` ... on every variable."""
    fac = (
        "Fv1",
        "Frv",
        "Fav",
        "Fw1",
        "Frw",
        "Faw",
        "Fd1",
        "Frvd",
        "Favd",
        "Fd1",
        "Frwd",
        "Fawd",
        "Fvso1",
        "Frvso",
        "Favso",
        "Fwso1",
        "Frwso",
        "Fawso",
        "Frc",
    )
    return {c: F[f] * o[c] for c, f in zip(COLUMNS, fac, strict=True)}


def opticalalpha(
    Z: int,
    A: int,
    e_mev: Tensor,
    alphaomp: int,
    F: Mapping[str, Tensor | float],
    prev: Mapping[str, Tensor],
) -> dict[str, Tensor]:
    """Alternative alpha potentials (alphaomp 2 McFadden-Satchler, 6 Avrigeanu 2014, 7 Nolte,
    8 Avrigeanu 1994); unset variables keep their `prev` (Watanabe) values.

    TALYS: opticalalpha.f90:1 (opticalalpha)
    Test: A-omppar
    """
    if 3 <= alphaomp <= 5:
        raise NotImplementedError(
            "alphaomp 3-5 (folding potentials) are out of scope (contract §8)"
        )
    e = e_mev
    a13 = A**_ONETHIRD
    o = dict(prev)
    z = torch.zeros_like(e)
    if alphaomp == 2:
        o.update(v_mev=_t(185.0, e), rv_fm=_t(1.40, e), av_fm=_t(0.52, e), w_mev=_t(25.0, e))
        o.update(
            rw_fm=o["rv_fm"],
            aw_fm=o["av_fm"],
            vd_mev=z,
            wd_mev=z,
            vso_mev=z,
            wso_mev=z,
            rc_fm=_t(1.3, e),
        )
    elif alphaomp == 6:
        rb = 2.66 + 1.36 * a13
        e2 = (2.59 + 10.4 / A) * Z / rb
        e1 = -3.03 - 0.76 * a13 + 1.24 * e2
        e3 = 22.2 + 0.181 * Z / a13
        e4 = 29.1 - 0.22 * Z / a13
        v = torch.where(
            e <= e3, 165.0 + 0.733 * Z / a13 - 2.64 * e, 116.5 + 0.337 * Z / a13 - 0.453 * e
        )
        v = torch.clamp(v, min=-100.0)
        rv = torch.where(e <= 25.0, 1.18 + 0.012 * e, _t(1.48, e))
        av = torch.where(
            e <= e2,
            _t(0.631 + (0.016 - 0.001 * e2) * Z / a13, e),
            torch.where(e <= e4, 0.631 + (0.016 - 0.001 * e) * Z / a13,
                        0.684 - 0.016 * Z / a13 - (0.0026 - 0.00026 * Z / a13) * e),
        )  # fmt: skip
        av = torch.clamp(av, min=0.1)
        w = torch.clamp(2.73 - 2.88 * a13 + 1.11 * e, min=0.0)
        wd = torch.where(
            e <= e1,
            _t(4.0, e),
            torch.where(
                e <= e2, 22.2 + 4.57 * a13 - 7.446 * e2 + 6.0 * e, 22.2 + 4.57 * a13 - 1.446 * e
            ),
        )
        wd = torch.clamp(wd, min=0.0)
        if A <= 152 or A >= 190:
            rwd = _t(1.52, e)
        else:
            rwd = torch.clamp(1.74 - 0.01 * e, min=1.52)
        o.update(
            v_mev=v,
            rv_fm=rv,
            av_fm=av,
            w_mev=w,
            rw_fm=_t(1.34, e),
            aw_fm=_t(0.50, e),
            vd_mev=z,
            wd_mev=wd,
            rwd_fm=rwd,
            awd_fm=_t(0.729 - 0.074 * a13, e),
            vso_mev=z,
            wso_mev=z,
            rc_fm=_t(1.3, e),
        )
    elif alphaomp in (7, 8):
        v = 101.1 + 6.051 * Z / a13 - 0.248 * e
        if alphaomp == 7:
            w = 26.82 - 1.706 * a13 + 0.006 * e
        else:
            w = torch.where(
                e <= 73.0, 12.64 - 1.706 * a13 + 0.20 * e, 26.82 - 1.706 * a13 + 0.006 * e
            )
        o.update(
            v_mev=v,
            rv_fm=_t(1.245, e),
            av_fm=_t(0.817 - 0.0085 * a13, e),
            w_mev=w,
            rw_fm=_t(1.57, e),
            aw_fm=_t(0.692 - 0.02 * a13, e),
            vd_mev=z,
            wd_mev=z,
            vso_mev=z,
            wso_mev=z,
            rc_fm=_t(1.3, e),
        )
    return _final_adjust(o, F)


def _alt_window(k: int, i: int) -> tuple[float, float, float, float]:
    """(Eompbeg0, Eompbeg1, Eompend1, Eompend0) of alternative OMP i for particle k
    (omppar.f90:443-465; zero for anything omppar does not set)."""
    if k == 3 and 2 <= i <= 5:
        return {2: (0.0, 0.0, 90.0, 150.0), 3: (0.0, 0.0, 100.0, 150.0)}.get(
            i, (0.0, 0.0, 200.0, 300.0)
        )
    if k == 6 and 2 <= i <= 8:
        return (0.0, 0.0, 25.0, 50.0) if i == 2 else (0.0, 0.0, 200.0, 300.0)
    return (0.0, 0.0, 0.0, 0.0)


def opticalcomp(
    k: int,
    Z: int,
    A: int,
    e_mev: Tensor,
    nucleon: Mapping[int, NucleonOMP],
    options: Options,
    params: Params | None = None,
    *,
    tables: Mapping[int, OMPTable] | None = None,
    joins: Mapping[int, JoinValues] | None = None,
    soukho_eferm_mev: Mapping[int, float] | None = None,
) -> dict[str, Tensor]:
    """OMP for a composite particle k = 3..6 on (Z, A): the Watanabe combination of the neutron
    and proton potentials at E/A_k (spin-orbit at E), then, where `altomp(k)` is set, the
    alternative global potential blended in over its energy window.

    TALYS: opticalcomp.f90:1 (opticalcomp)
    Test: A-omppar
    """
    e = torch.clamp(torch.as_tensor(e_mev, dtype=DTYPE), min=0.0)
    tables = tables or {}
    joins = joins or {}
    se = soukho_eferm_mev or {}
    if k in tables:
        F = ompadjust(params, k)
        inside, tab = _interp_table(tables[k], e, F)
    else:
        inside, tab = None, None

    def np_(kk: int, en: Tensor) -> dict[str, Tensor]:
        return opticalnp(
            nucleon[kk],
            kk,
            Z,
            A,
            en,
            params,
            options=options,
            table=tables.get(kk),
            join=joins.get(kk),
            soukho_eferm_mev=se.get(kk),
        )

    ea = e / PARA[k]
    n, p = np_(1, ea), np_(2, ea)
    n_e, p_e = np_(1, e), np_(2, e)
    F = ompadjust(params, k)
    iz, in_, ia = PARZ[k], PARN[k], PARA[k]
    o = {
        "v_mev": F["Fv1"] * (in_ * n["v_mev"] + iz * p["v_mev"]),
        "rv_fm": F["Frv"] * (in_ * n["rv_fm"] + iz * p["rv_fm"]) / ia,
        "av_fm": F["Fav"] * (in_ * n["av_fm"] + iz * p["av_fm"]) / ia,
        "w_mev": F["Fw1"] * (in_ * n["w_mev"] + iz * p["w_mev"]),
        "rw_fm": F["Frw"] * (in_ * n["rw_fm"] + iz * p["rw_fm"]) / ia,
        "aw_fm": F["Faw"] * (in_ * n["aw_fm"] + iz * p["aw_fm"]) / ia,
        "vd_mev": F["Fd1"] * (in_ * n["vd_mev"] + iz * p["vd_mev"]),
        "rvd_fm": F["Frvd"] * (in_ * n["rvd_fm"] + iz * p["rvd_fm"]) / ia,
        "avd_fm": F["Favd"] * (in_ * n["avd_fm"] + iz * p["avd_fm"]) / ia,
        "wd_mev": F["Fd1"] * (in_ * n["wd_mev"] + iz * p["wd_mev"]),
        "rwd_fm": F["Frwd"] * (in_ * n["rvd_fm"] + iz * p["rvd_fm"]) / ia,
        "awd_fm": F["Fawd"] * (in_ * n["avd_fm"] + iz * p["avd_fm"]) / ia,
        "rvso_fm": F["Frvso"] * (in_ * n_e["rvso_fm"] + iz * p_e["rvso_fm"]) / ia,
        "avso_fm": F["Favso"] * (in_ * n_e["avso_fm"] + iz * p_e["avso_fm"]) / ia,
        "rwso_fm": F["Frwso"] * (in_ * n_e["rvso_fm"] + iz * p_e["rvso_fm"]) / ia,
        "awso_fm": F["Fawso"] * (in_ * n_e["avso_fm"] + iz * p_e["avso_fm"]) / ia,
        "rc_fm": F["Frc"] * p_e["rc_fm"],
    }
    if k == 3:
        o["vso_mev"] = F["Fvso1"] * (n_e["vso_mev"] + p_e["vso_mev"]) / 2.0
        o["wso_mev"] = F["Fwso1"] * (n_e["wso_mev"] + p_e["wso_mev"]) / 2.0
    elif k in (4, 5):
        o["vso_mev"] = F["Fvso1"] * (n_e["vso_mev"] + p_e["vso_mev"]) / 6.0
        o["wso_mev"] = F["Fwso1"] * (n_e["wso_mev"] + p_e["wso_mev"]) / 6.0
    else:
        o["vso_mev"] = torch.zeros_like(e)
        o["wso_mev"] = torch.zeros_like(e)
    o = {
        c: _t(o[c], e) if not isinstance(o[c], Tensor) or o[c].shape != e.shape else o[c]
        for c in COLUMNS
    }
    if options.altomp[k]:
        kd = dict(o)
        i = 1
        alt = o
        if k == 3 and options.deuteronomp >= 2:
            alt = opticaldeut(Z, A, e, options.deuteronomp, F, o)
            i = options.deuteronomp
        if k == 6 and (options.alphaomp == 2 or options.alphaomp >= 6):
            alt = opticalalpha(Z, A, e, options.alphaomp, F, o)
            i = options.alphaomp
        b0, b1, e1, e0 = _alt_window(k, i)
        efrac = torch.ones_like(e)
        if b1 > b0:
            efrac = torch.where((e > b0) & (e <= b1), (e - b0) / (b1 - b0), efrac)
        if e0 > e1:
            efrac = torch.where((e > e1) & (e <= e0), 1.0 - (e - e1) / (e0 - e1), efrac)
        efrac = torch.where(e <= b0, torch.zeros_like(e), efrac)
        efrac = torch.where(e > e0, torch.zeros_like(e), efrac)
        o = {c: efrac * alt[c] + (1.0 - efrac) * kd[c] for c in COLUMNS}
    if tab is not None:
        o = {c: torch.where(inside, _t(tab[c], e), o[c]) for c in COLUMNS}
    _apply_geometry_ranges(o, e, params, k)
    return o


def optical(
    k: int,
    Z: int,
    A: int,
    e_mev: Tensor,
    nucleon: Mapping[int, NucleonOMP],
    options: Options,
    params: Params | None = None,
    **kw,
) -> dict[str, Tensor]:
    """Dispatch: nucleons to `opticalnp`, composite particles to `opticalcomp`.

    TALYS: optical.f90:1 (optical)
    Test: A-omppar
    """
    if k <= 2:
        return opticalnp(
            nucleon[k],
            k,
            Z,
            A,
            e_mev,
            params,
            options=options,
            table=(kw.get("tables") or {}).get(k),
            join=(kw.get("joins") or {}).get(k),
            soukho_eferm_mev=(kw.get("soukho_eferm_mev") or {}).get(k),
        )
    return opticalcomp(k, Z, A, e_mev, nucleon, options, params, **kw)


def radius(a: float) -> float:
    """Radius function for the Tripathi reaction cross section: sqrt(5/3) times a tabulated rms
    charge radius for light nuclei (A <= 26), otherwise 0.84 A^(1/3) + 0.55.

    TALYS: radius.f90:1 (radius)
    Test: A-omppar
    """
    na = (1, 2, 3, 4, 6, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 22, 23, 24, 25, 26)
    rms = (
        0.85,
        2.095,
        1.976,
        1.671,
        2.57,
        2.41,
        2.519,
        2.45,
        2.42,
        2.471,
        2.440,
        2.58,
        2.611,
        2.730,
        2.662,
        2.727,
        2.900,
        3.040,
        2.969,
        2.94,
        3.075,
        3.11,
        3.06,
    )
    fact = math.sqrt(5.0 / 3.0)
    ia = int(a + 0.4)
    r = fact * (0.84 * a**_ONETHIRD + 0.55)
    for n_, s in zip(na, rms, strict=True):
        if ia == n_:
            r = fact * s
    return r


# ------------------------------------------------------------------------------ public entry point
def omp_parameters(
    Z: int,
    N: int,
    particle: int,
    e_mev: Tensor,
    params: Params,
    options: Options,
    *,
    colltype: str | None = None,  # TODO(T2): None reads structure/deformation
    tables: Mapping[int, OMPTable] | None = None,
    enincmax_mev: float = 0.0,
    soukho_eferm_mev: Mapping[int, float] | None = None,
    sep_energy_mev: Mapping[int, tuple[float, float]] | None = None,  # TODO(T2)
    structure: Path | None = None,
) -> OMPParameters:
    """OMP depths and geometry at energies e_mev (MeV) for particle type k (TALYS numbering 1=n ...
    6=alpha) on residual (Z, N), reproducing omppar_{n,p,d,t,h,a}.out column for column.

    Structure inputs TALYS reads elsewhere are arguments until T2 lands: `colltype` (deformpar;
    None reads the `.def` header directly),
    `sep_energy_mev` (only when `globalfermi n`), `soukho_eferm_mev` (only for Soukhovitskii
    actinides). `tables` supplies an already-retrieved OMP table per particle, standing in for a
    user `optmod` file; the actinide RIPL default (`flagriplomp`) is retrieved here instead, by
    `riplomp_table`.

    `enincmax_mev` is the run's maximum incident energy. It enables the 1 GeV extension exactly
    when TALYS would (enincmax > Ejoin) and fixes where the RIPL table stops (enincmax + 12,
    omppar.f90:304). Left at 0 it defaults to `max(e_mev)`, which is what the incident grid gives
    and, for any other call, only extends the table past where TALYS stops interpolating; the
    node positions inside are the same either way, so the interpolation is unchanged.

    TALYS: optical.f90:1 (optical), kd03.f90:1 (kd03)
    Test: A-omppar
    """
    from physics.hf.omp import omp_nx2

    fast = omp_nx2.omp_parameters(  # NATIVEX2 `omp`: on floats, no gradient
        Z, N, particle, e_mev, params, options, colltype=colltype, tables=tables,
        enincmax_mev=enincmax_mev, soukho_eferm_mev=soukho_eferm_mev,
        sep_energy_mev=sep_energy_mev, structure=structure)
    if fast is not None:
        return fast
    A = Z + N
    e = torch.as_tensor(e_mev, dtype=DTYPE)
    nucleon = omppar(
        Z, A, options, colltype=colltype, sep_energy_mev=sep_energy_mev, structure=structure
    )
    # omppar.f90:317: `riplomp(k)` attaches a retrieved table to the ONE nucleus that is the
    # k-particle's own residual, (Zix, Nix) = (parZ(k), parN(k)); it is a property of the nucleus,
    # so a composite particle on the same nucleus sees it too through opticalcomp.
    tables = dict(tables or {})
    nucleon = dict(nucleon)
    if options.flagriplomp:
        for k in range(1, 7):
            if options.riplomp[k] <= 0 or k in tables:  # an explicit table wins, as `optmod` does
                continue
            if (Z, A) != (options.Zinit - PARZ[k], options.Ainit - PARA[k]):
                continue
            tables[k], ef_ripl = riplomp_table(
                Z, A, k, options.riplomp[k], enincmax_mev or float(e.max()), structure=structure
            )
            if k in nucleon:  # omppar.f90:363-366: `Ef =` in the table header overwrites ef
                nucleon[k] = replace(nucleon[k], ef_mev=ef_ripl)
    joins: dict[int, JoinValues] = {}
    for k in (1, 2):
        ejoin = float(params["ejoin"][k])
        zr, ar = options.Zinit - PARZ[k], options.Ainit - PARA[k]
        if enincmax_mev > ejoin:
            src = nucleon if (zr, ar) == (Z, A) else omppar(zr, ar, options, structure=structure)
            args = dict(
                params=params, options=options, soukho_eferm_mev=(soukho_eferm_mev or {}).get(k)
            )
            e0 = opticalnp(src[k], k, zr, ar, torch.zeros(1, dtype=DTYPE), **args)
            ej = opticalnp(src[k], k, zr, ar, torch.full((1,), ejoin, dtype=DTYPE), **args)
            joins[k] = JoinValues(
                float(e0["v_mev"][0]), float(ej["v_mev"][0]), float(ej["w_mev"][0])
            )
    out = optical(
        particle,
        Z,
        A,
        e,
        nucleon,
        options,
        params,
        tables=tables,
        joins=joins,
        soukho_eferm_mev=soukho_eferm_mev,
    )
    return OMPParameters(**{c: _t(out[c], e) for c in COLUMNS})


def omp_parameter_grid(
    residuals: list[tuple[int, int]],
    particles: tuple[int, ...],
    e_mev: Tensor,
    params: Params,
    options: Options,
    **kw,
) -> OMPParameters:
    """`omp_parameters` batched over (case, particle, energy): residuals[c] = (Z, N) per case,
    one shared energy grid (C, E) or (E,). Returns fields shaped (C, P, E).

    TALYS: optical.f90:1 (optical)
    Test: A-omppar
    """
    e = torch.as_tensor(e_mev, dtype=DTYPE)
    rows = []
    for c, (z, n) in enumerate(residuals):
        ec = e[c] if e.dim() == 2 else e
        rows.append([omp_parameters(z, n, k, ec, params, options, **kw).stack() for k in particles])
    t = torch.stack([torch.stack(r) for r in rows])  # (C, P, E, 19)
    return OMPParameters(**{c: t[..., i] for i, c in enumerate(COLUMNS)})


__all__ = [
    "COLUMNS", "TALYS_COLUMNS", "OMPParameters", "NucleonOMP", "OMPTable", "JoinValues",
    "omppar", "kd03", "read_local_omp", "opticalnp", "opticalcomp", "opticaldeut",
    "opticalalpha", "soukhovitskii", "optical", "ompadjust", "adjustF", "radius",
    "omp_parameters", "omp_parameter_grid", "jsonline",
]  # fmt: skip
