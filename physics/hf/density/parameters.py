"""Level-density parameters: Ignatyuk energy-dependent a, shell correction and damping, pairing,
spin cutoff (all spincutmodels), spin and parity distributions, collective enhancement (Krot,
Kvib).

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T6 (physics/hf/CONTRACT.md §7). Acceptance test: A-ld (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    densitypar.f90:1 (densitypar)
    ignatyuk.f90:1 (ignatyuk)
    spincut.f90:1 (spincut)
    spindis.f90:1 (spindis)
    colenhance.f90:1 (colenhance)

How TALYS holds these, and how the port does
--------------------------------------------
TALYS keeps every level-density quantity in module arrays indexed ``(Zix, Nix[, ibar])`` and fills
them in structure.f90 in the order ``densitypar -> densitytable (ldmodel >= 4) -> densitymatch
-> densitycum``. The port gathers one nucleus's arrays into a frozen :class:`LDNucleus`
(contract §4.3: no module state) with the Fortran names, float64 tensors for the continuous
ones (so `aadjust`, `pshift`, `ctable`, `ptable`, `s2adjust`, `krotconstant` carry gradients),
and Python ints/bools for the switches. :func:`densitypar` fills what densitypar.f90 fills; the
constant-temperature matching (`T`, `E0`, `Exmatch`) is added by
:func:`physics.hf.density.matching.densitymatch` and the tables by
:func:`physics.hf.density.tables.density_table`.

Every function here is elementwise over the excitation energy tensor ``eex_mev``; TALYS's hard
branches (``U <= 0``, ``Eex <= Em``) are `torch.where` masks with safe denominators, so padded
or below-threshold entries give TALYS's value and no NaN gradient (contract §4.2).

Not ported: the energy-dependent parameter adjustment (`adjust` with `ldadjust y`, off by
default) and the BRC fission-model collective enhancement branch is ported but untested (it needs
`fismodel 1` with `colldamp y`). `rldm.f90`, the rotating-liquid-drop barrier, is a fission-barrier
routine and is left to T11.
"""

from __future__ import annotations

import math
import os
import weakref
from dataclasses import dataclass, field, replace
from functools import cache, lru_cache
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import torch
from torch import Tensor

from physics.hf.core.constants import nuclide_symbol, talys_constants
from physics.hf.core.tensors import DTYPE
from physics.hf.structure.files import fortran_read, talys_structure_dir

if TYPE_CHECKING:
    from physics.hf.input.defaults import Options, Params
    from physics.hf.structure.deformation import Deformation
    from physics.hf.structure.levels import Levels
    from physics.hf.structure.masses import Masses

__all__ = [
    "LDNucleus",
    "BarrierLevels",
    "densitypar",
    "ld_parameter_file",
    "ignatyuk",
    "spincut",
    "spindis",
    "colenhance",
    "PARDIS",
    "NUMJ",
    "NUMLEV2",
]

PARDIS = 0.5  # constants.f90:158
NUMJ = 40  # A0_talys_mod.f90:68
NUMLEV2 = 300  # A0_talys_mod.f90:48
SENTINEL = 1.0e-20  # TALYS's "not given" value for pair, Pshift, E0, ctable, ptable

_LD_DIRS = {  # densitypar.f90:229-235
    1: "ctm",
    2: "bfm",
    3: "gsm",
    4: "goriely",
    5: "hilaire",
    6: "hilaireD1M",
    7: "bskg3",
}


def _t(x) -> Tensor:
    if isinstance(x, Tensor):
        return x if x.dtype is DTYPE else x.to(DTYPE)
    return torch.as_tensor(float(x), dtype=DTYPE)  # `_fv` of a non-tensor, inlined


def _fv(x) -> float:
    """`x` as a Python float for one of TALYS's hard branches on a continuous value. Detaching is
    deliberate: the branch itself is not differentiated (contract §4.4), and going through
    `float()` on a `requires_grad` tensor would otherwise warn on every call."""
    if type(x) is float:
        return x
    if isinstance(x, Tensor):
        return float(x.detach()) if x.requires_grad else float(x)
    return float(x)


def _fast_ok(x) -> bool:
    """COREX: the float/numpy path of `ignatyuk`/`spincut` applies to `x`: nothing records a graph
    and `x` is a Python number or a CPU tensor."""
    if torch.is_grad_enabled():
        return False
    if isinstance(x, Tensor):
        return x.device.type == "cpu" and x.dtype in (DTYPE, torch.float32)
    return isinstance(x, (float, int))


def _as_np(x):
    """A float or a float64 ndarray (a view of a float64 tensor) for the fast paths."""
    if isinstance(x, Tensor):
        if x.dim() == 0:
            return float(x)
        return (x if x.dtype is DTYPE else x.to(DTYPE)).numpy()
    return float(x)


# COREX: the scalars of one LDNucleus the fast paths read, per object. Keyed by id with a weak
# reference that must still resolve to the same object (so a recycled id never hits), and dropped
# when the nucleus is freed. LDNucleus is frozen and nothing writes into its tensors in place.
_LD_FLOATS: dict[int, tuple] = {}


def _ld_memo(ld: LDNucleus) -> dict:
    key = id(ld)
    ent = _LD_FLOATS.get(key)
    if ent is None or ent[0]() is not ld:
        ent = (weakref.ref(ld, lambda _r, k=key: _LD_FLOATS.pop(k, None)), {})
        _LD_FLOATS[key] = ent
    return ent[1]


def _ign_floats(ld: LDNucleus, ibar: int) -> tuple:
    ent = _LD_FLOATS.get(id(ld))
    if ent is not None and ent[0]() is ld:
        b = ent[1].get(("ign", ibar))
        if b is not None:
            return b
    memo = _ld_memo(ld)
    b = memo.get(("ign", ibar))
    if b is None:
        b = memo[("ign", ibar)] = (
            float(ld.delta_mev[ibar]), float(ld.alimit), float(ld.gammald),
            float(ld.deltaW_mev[ibar]), bool(ld.flagcolldamp), ld.A / 13.0,
            float(ld.Ufermi_mev[0]), float(ld.cfermi_mev[0]))
    return b


def _ignatyuk_f(ld: LDNucleus, eex: float, ibar: int) -> float:
    """COREX: `ignatyuk` at one energy in Python floats, the same operations in the same order
    (math.exp for torch.exp: agreement to the last bits, not bit-identity)."""
    delta, aldlim, gam, dW, colldamp, aldlow, uf, cf = _ign_floats(ld, ibar)
    U = eex - delta
    if U > 0.0:
        expo = gam * U
        fU = 1.0 - math.exp(-expo) if abs(expo) <= 80.0 else 1.0
        damp = 1.0 + fU * dW / U
    else:
        damp = 1.0 + dW * gam
    if colldamp:  # ignatyuk.f90:71-79
        e = (U - uf) / cf
        qfermi = 1.0 / (1.0 + math.exp(-max(e, -80.0))) if e > -80.0 else 0.0
        aldlim = aldlow * qfermi + aldlim * (1.0 - qfermi)
    v = aldlim * damp
    return v if not v < 1.0 else 1.0


def _ignatyuk_fast(ld: LDNucleus, eex_mev, ibar: int) -> Tensor:
    """COREX: `ignatyuk` off the graph, in floats (one energy) or numpy (an array of them)."""
    if isinstance(eex_mev, Tensor) and eex_mev.ndim and eex_mev.dtype is DTYPE:
        eex = eex_mev.numpy()
    else:
        eex = _as_np(eex_mev)
    if isinstance(eex, float):
        return torch.tensor(_ignatyuk_f(ld, eex, ibar), dtype=DTYPE)
    from physics.hf.density.ld_ceng import ignatyuk as _ceng_ignatyuk

    got = _ceng_ignatyuk(ld, eex, ibar)  # CENGLD: the same loop in C
    if got is not None:
        return got
    delta, aldlim, gam, dW, colldamp, aldlow, uf, cf = _ign_floats(ld, ibar)
    with np.errstate(all="ignore"):
        U = eex - delta
        pos = U > 0.0
        Us = np.where(pos, U, 1.0)
        expo = gam * Us
        small = np.abs(expo) <= 80.0
        fU = np.where(small, 1.0 - np.exp(-np.where(small, expo, 1.0)), 1.0)
        damp = np.where(pos, 1.0 + fU * dW / Us, 1.0 + dW * gam)
        if colldamp:
            e = (U - uf) / cf
            qfermi = np.where(e > -80.0, 1.0 / (1.0 + np.exp(-np.maximum(e, -80.0))), 0.0)
            aldlim = aldlow * qfermi + aldlim * (1.0 - qfermi)
        return torch.from_numpy(np.asarray(np.maximum(aldlim * damp, 1.0), dtype=np.float64))


def _sc_floats(ld: LDNucleus, ibar: int, ipop: int, rspincutff: float) -> tuple:
    """spincut's energy-independent scalars: (scutconst, Em, Ed, sdisc, s2m, colld, delta)."""
    key = ("sc", ibar, ipop, float(rspincutff))
    ent = _LD_FLOATS.get(id(ld))
    if ent is not None and ent[0]() is ld:
        b = ent[1].get(key)
        if b is not None:
            return b
    memo = _ld_memo(ld)
    Rs = float(rspincutff) if ipop == 1 else float(ld.Rspincut)
    s2 = float(ld.s2adjust[ibar])
    ldmod = ld.ldmodel
    Irigid0 = float(ld.Irigid0)
    scutconst = Rs * s2 * Irigid0 / float(ld.alimit) if ld.spincutmodel == 1 else Rs * s2 * Irigid0
    pair = float(ld.pair_mev)
    Em = float(ld.Exmatch_mev[ibar])
    if ldmod == 2 or ldmod >= 4:
        Em = float(ld.S_mev)
    if ldmod == 3:
        Em = float(ld.Ucrit_mev[ibar]) - pair - float(ld.Pshift_mev[ibar])
    sdisc = float(ld.scutoffdisc[ibar])
    colld = 1.0 + float(ld.beta2[ibar]) / 3.0 if (ld.flagcolldamp and ibar != 0) else None
    aldm = _ignatyuk_f(ld, Em, ibar)
    Umatch = Em - pair - float(ld.Pshift_mev[ibar])
    if Umatch > 0.0:
        if ld.spincutmodel == 1:
            s2m = (scutconst * float(ld.aldcrit[ibar]) * float(ld.Tcrit_mev) if ldmod == 3
                   else scutconst * math.sqrt(aldm * Umatch))
        else:
            s2m = (scutconst * float(ld.Tcrit_mev) if ldmod == 3
                   else scutconst * math.sqrt(Umatch / aldm))
    else:
        s2m = sdisc
    if colld is not None:
        s2m = colld * s2m
    b = memo[key] = (scutconst, Em, float(ld.Ediscrete_mev[ibar]), sdisc, s2m, colld,
                     float(ld.delta_mev[ibar]))
    return b


def _spincut_fast(ld: LDNucleus, ald, eex_mev, ibar: int, ipop: int, rspincutff: float) -> Tensor:
    """COREX: `spincut` off the graph, in floats (one energy) or numpy; the same operations in the
    same order as the tensor path."""
    scutconst, Em, Ed, sdisc, s2m, colld, delta = _sc_floats(ld, ibar, ipop, rspincutff)
    model1 = ld.spincutmodel == 1
    eex = (eex_mev.numpy() if isinstance(eex_mev, Tensor) and eex_mev.ndim
           and eex_mev.dtype is DTYPE else _as_np(eex_mev))
    a = ald.numpy() if isinstance(ald, Tensor) and ald.ndim and ald.dtype is DTYPE else _as_np(ald)
    if isinstance(eex, float) and isinstance(a, float):
        if Em != Ed and eex > Ed:
            below = sdisc + (eex - Ed) / (Em - Ed) * (s2m - sdisc)
        else:
            below = sdisc
        U = eex - delta
        if U > 0.0:
            above = scutconst * math.sqrt(a * U) if model1 else scutconst * math.sqrt(U / a)
        else:
            above = sdisc
        sc = below if eex <= Em else above
        if colld is not None:
            sc = colld * sc
        return torch.tensor(sc if not sc < sdisc else sdisc, dtype=DTYPE)
    from physics.hf.density.ld_ceng import spincut as _ceng_spincut

    got = _ceng_spincut(ld, a, eex, ibar, ipop, rspincutff)  # CENGLD: the same loop in C
    if got is not None:
        return got
    with np.errstate(all="ignore"):
        eex = np.asarray(eex, dtype=np.float64)
        interp = (Em != Ed) & (eex > Ed)
        denom = Em - Ed if Em != Ed else 1.0
        below = np.where(interp, sdisc + (eex - Ed) / denom * (s2m - sdisc), sdisc)
        U = eex - delta
        okU = U > 0.0
        Us = np.where(okU, U, 1.0)
        above = scutconst * np.sqrt(a * Us) if model1 else scutconst * np.sqrt(Us / a)
        above = np.where(okU, above, sdisc)
        sc = np.where(eex <= Em, below, above)
        if colld is not None:
            sc = colld * sc
        return torch.from_numpy(np.asarray(np.maximum(sdisc, sc), dtype=np.float64))


#: NX2 ld: (storage keyword, Fortran bounds, storage offsets) per `Params` keyword `densitypar`
#: reads; a pure function of the static `PARAM_SPECS` table.
_AT_PLAN: dict[str, tuple] = {}


def _f32(x: float) -> float:
    """TALYS's single-precision literal as float64 (contract §4.1)."""
    import numpy as np

    return _fv(np.float32(x))


@dataclass(frozen=True)
class BarrierLevels:
    """Fission-barrier inputs densitypar/densitymatch read (fissionpar.f90, T11): the number of
    barriers, the rotational band on each barrier (`efistrrot` [MeV], `jfistrrot`), axiality and
    barrier height. Index 0 of each per-barrier tuple is unused (ground state), as in TALYS."""

    nfisbar: int = 0
    nfistrrot: tuple[int, ...] = (0, 0, 0, 0)
    efistrrot_mev: tuple[Tensor | None, ...] = (None, None, None, None)  # (n+1,) per barrier
    jfistrrot: tuple[Tensor | None, ...] = (None, None, None, None)
    axtype: tuple[int, ...] = (1, 1, 1, 1)
    fbarrier_mev: tuple[float, ...] = (0.0, 0.0, 0.0, 0.0)


@dataclass(frozen=True)
class LDNucleus:
    """The level-density arrays of one nucleus ``(Zix, Nix)`` after densitypar.f90 (and, once
    filled, densitytable/densitymatch/densitycum). Per-barrier tensors have shape (nfisbar+1,).
    Units in the names; `alev`, `alimit`, `aldcrit` are MeV^-1; spin cutoffs, `gammald`,
    `Krotconstant`, `Irigid*` [MeV^-1] as TALYS uses them."""

    Z: int
    A: int
    Zix: int
    Nix: int
    ldmodel: int
    flagcol: bool
    nfisbar: int
    # switches read from Options
    spincutmodel: int
    kvibmodel: int
    flagcolldamp: bool
    fismodel: int
    flagparity: bool
    # densitypar.f90
    ldparexist: bool
    alev: Tensor
    alimit: Tensor
    gammald: Tensor
    deltaW_mev: Tensor  # (nbar+1,)
    pair_mev: Tensor
    delta0_mev: Tensor
    Pshift_mev: Tensor  # (nbar+1,)
    delta_mev: Tensor  # (nbar+1,)
    scutoffdisc: Tensor  # (nbar+1,)
    Ediscrete_mev: Tensor  # (nbar+1,)
    Nlow: tuple[int, ...]
    Ntop: tuple[int, ...]
    Nlast: tuple[int, ...]
    ctable: Tensor  # (nbar+1,)
    ptable_mev: Tensor  # (nbar+1,)
    s2adjust: Tensor  # (nbar+1,)
    Rspincut: Tensor
    Krotconstant: Tensor  # (nbar+1,)
    Ufermi_mev: Tensor  # (nbar+1,)
    cfermi_mev: Tensor  # (nbar+1,)
    Irigid0: Tensor
    Irigid: Tensor  # (nbar+1,)
    beta2: Tensor  # (nbar+1,)
    axtype: tuple[int, ...]
    S_mev: Tensor  # S(Zix, Nix, 1), neutron separation energy of this nucleus
    # generalised superfluid model (ldmodel 3)
    Tcrit_mev: Tensor
    aldcrit: Tensor  # (nbar+1,)
    Econd_mev: Tensor  # (nbar+1,)
    Ucrit_mev: Tensor  # (nbar+1,)
    Scrit: Tensor  # (nbar+1,)
    Dcrit: Tensor  # (nbar+1,)
    # constant-temperature matching: inputs (T/E0/Exmatch keywords) until densitymatch fills them
    T_mev: Tensor  # (nbar+1,)
    E0_mev: Tensor  # (nbar+1,)
    Exmatch_mev: Tensor  # (nbar+1,)
    Tadjust: Tensor
    E0adjust: Tensor
    Exmatchadjust: Tensor
    # exciton-model single-particle densities (densitypar.f90:525-532)
    g: Tensor
    gn: Tensor
    gp: Tensor
    # discrete levels, padded to numlev2 as TALYS's edis/jdis
    edis_mev: Tensor  # (numlev2+1,)
    jdis: Tensor  # (numlev2+1,)
    nlev: int
    nlevmax2: int
    barriers: BarrierLevels
    # filled by later stages
    ldexist: tuple[bool, ...] = ()
    tables: tuple = ()  # per ibar: physics.hf.density.tables.DensityTable or None
    matched: bool = False
    extra: dict = field(default_factory=dict)

    @property
    def N(self) -> int:
        return self.A - self.Z

    def has_table(self, ibar: int) -> bool:
        return bool(self.ldexist) and ibar < len(self.ldexist) and self.ldexist[ibar]


@cache
def _ld_file_rows(path: str, collective: bool) -> dict[int, tuple[int, int, float, float]]:
    fmt = "(4x,i4,32x,2i4,2f12.5)" if collective else "(4x,3i4,2f12.5)"  # densitypar.f90:241-245
    out: dict[int, tuple[int, int, float, float]] = {}
    p = Path(path)
    if not p.is_file():
        return out
    for line in p.read_text(encoding="latin-1").splitlines():
        if not line.strip():
            continue
        ia, nlow0, ntop0, ald0, pshift0 = fortran_read(line, fmt)
        out.setdefault(int(ia), (int(nlow0), int(ntop0), _f32(ald0), _f32(pshift0)))
    return out


def ld_parameter_file(
    Z: int, A: int, ldmodel: int, collective: bool, s2adjust: float = 1.0
) -> tuple[bool, int, int, float, float]:
    """(found, Nlow0, Ntop0, ald0, pshift0) from TALYS's fitted level-density parameter files
    ``density/ground/<model>/<Sym>.ld_<s2adjust>``, with the s2adjust interpolation between the
    two bracketing files. For ldmodel >= 4, ald0/pshift0 are ctable/ptable.

    TALYS: densitypar.f90:1 (densitypar)
    Test: A-ld
    """
    return _ld_parameter_file(int(Z), int(A), int(ldmodel), bool(collective), _fv(s2adjust),
                              talys_structure_dir())


@cache
def _ld_parameter_file(Z: int, A: int, ldmodel: int, collective: bool, s2a: float, root: Path):
    """`ld_parameter_file`, memoised (NX2 ld): a pure function of its arguments and the files."""
    ext1, ext2, frac = 0.0, 0.0, 0.0
    if s2a == 1.0:  # densitypar.f90:209-212
        ext1 = 1.0
    else:
        for k in range(1, 11):
            x = _f32(k * 0.2)
            if x < s2a <= _f32(x + 0.2):
                ext1, ext2 = x, _f32(x + 0.2)
                break
        if ext2 > ext1:
            frac = (s2a - ext1) / (ext2 - ext1)
        if s2a <= 0.2:
            ext1 = 0.2
        if s2a >= 2.0:
            ext2 = 2.0
    base = root / "density" / "ground" / _LD_DIRS[ldmodel]
    sym = nuclide_symbol(Z)

    def look(ext: float):
        return _ld_file_rows(str(base / f"{sym}.ld_{ext:3.1f}"), collective).get(int(A))

    r1 = look(ext1)
    r2 = look(ext2) if ext2 > 0.0 else None
    if r1 and r2:  # densitypar.f90:291-306
        nlow0, ntop0 = (r1[0], r1[1]) if abs(ext1 - 1.0) <= abs(ext2 - 1.0) else (r2[0], r2[1])
        return True, nlow0, ntop0, r1[2] + frac * (r2[2] - r1[2]), r1[3] + frac * (r2[3] - r1[3])
    if r1:
        return True, *r1
    if r2:
        return True, *r2
    return False, 0, 0, 0.0, 0.0


class _SameObjects:
    """CENGLD: `densitypar`'s arguments as a cache key by identity (Z and A by value). The key
    holds the objects, so no id is recycled while it is cached; a new `Params` (a fit's parameter
    point, PARAMWIRE's `with_aadjust`) is a new key."""

    __slots__ = ("args", "_h")

    def __init__(self, Z, A, *objs) -> None:
        self.args = (Z, A, *objs)
        self._h = hash((Z, A, *map(id, objs)))

    def __hash__(self) -> int:
        return self._h

    def __eq__(self, other) -> bool:
        a, b = self.args, other.args
        return (a[0] == b[0] and a[1] == b[1] and len(a) == len(b)
                and all(x is y for x, y in zip(a[2:], b[2:])))


@lru_cache(maxsize=256)
def _densitypar_shared(key: _SameObjects):
    """`ld_nx2.densitypar_floats` of `key`'s arguments (dropped with the target's caches)."""
    from physics.hf.density import ld_nx2

    args = key.args
    k = ld_nx2.densitypar_key(*args) if ld_nx2._xt_on() else None
    if k is None:
        return ld_nx2.densitypar_floats(*args)
    # CENGLD2: the same record across targets (`ld_nx2.densitypar_key`)
    Z, A, options = args[0], args[1], args[2]
    return ld_nx2.shared_record(("dp", k), options.Zinit - Z, options.Ninit - (A - Z),
                                lambda: ld_nx2.densitypar_floats(*args))


def densitypar(
    Z: int,
    A: int,
    options: Options,
    params: Params,
    masses: Masses,
    levels: Levels,
    deformation: Deformation | None = None,
    barriers: BarrierLevels | None = None,
) -> LDNucleus:
    """Level-density parameters of nucleus (Z, A) exactly as densitypar.f90: Nlow/Ntop and the
    fitted a/Pshift (or ctable/ptable) from the parameter files, the discrete spin cutoff,
    shell correction from the liquid-drop mass, asymptotic a, damping gamma, pairing, the GSM
    critical quantities, a(Sn) and the exciton-model g, gn, gp.

    `levels` is T2's `discrete_levels` for this nucleus; `deformation` T2's `deformation` (computed
    if None, for Irigid); `barriers` the fission-barrier data (none by default).

    TALYS: densitypar.f90:1 (densitypar)
    Test: A-ld
    """
    from physics.hf.density.ld_nx2 import densitypar_floats

    if not torch.is_grad_enabled() and os.environ.get("HF_NX2_CENGLD", "1") != "0":
        # CENGLD: one nucleus's record is asked for by its level density, its photon strength's
        # `alev` and the pre-equilibrium pairing, on the same objects: built once per target. Only
        # where no graph can be recorded (the chart runs in inference mode), so a tensor turned
        # `requires_grad` in place never meets a record built before it was
        got = _densitypar_shared(_SameObjects(Z, A, options, params, masses, levels, deformation,
                                              barriers))
    else:
        got = densitypar_floats(Z, A, options, params, masses, levels, deformation, barriers)
    if got is not None:  # NX2 ld: the same numbers on Python floats (None: a parameter's gradient)
        return got
    c = talys_constants()
    amu = c["amu"]
    twothird, onethird, pi, pi2 = c["twothird"], c["onethird"], c["pi"], c["pi2"]
    N = A - Z
    Zix, Nix = options.Zinit - Z, options.Ninit - N
    ldmod = options.ldmodel_of(Zix, Nix)
    flagcol = options.flagcol_of(Zix, Nix)
    bar = barriers or BarrierLevels()
    nbar = bar.nfisbar if options.flagfission else 0
    bars = range(nbar + 1)

    vals = params.values

    def p(k, *extra):
        # NX2 ld: `params.at` without re-deriving the spec's offsets per call; any index outside
        # the Fortran bounds goes through `params.at`, which raises as before
        plan = _AT_PLAN.get(k)
        if plan is None:
            from physics.hf.input.defaults import PARAM_SPECS

            spec = PARAM_SPECS[k]
            plan = _AT_PLAN[k] = (spec.keyword, spec.dims, spec.offsets)
        kw, dims, offs = plan
        idx = (Zix, Nix, *extra)
        if len(idx) == len(dims) and all(lo <= i <= hi for i, (lo, hi) in zip(idx, dims)):
            return _t(vals[kw][tuple(i + o for i, o in zip(idx, offs))])
        return _t(params.at(k, *idx))

    def pb(k):
        return torch.stack([p(k, ib) for ib in bars])

    # --- parameter files (densitypar.f90:203-339)
    s2a0 = p("s2adjust", 0)
    found, nlow0, ntop0, ald0, pshift0 = ld_parameter_file(
        Z, A, ldmod, flagcol and ldmod <= 3, _fv(s2a0)
    )
    alev = p("a")
    Pshift = pb("pshift").clone()
    ctable = pb("ctable").clone()
    ptable = pb("ptable").clone()
    Nlow = [options.nlow_default for _ in bars]
    Ntop = [options.ntop_default for _ in bars]
    ldparexist = False
    if found:
        ldparexist = True
        if Nlow[0] == -1:
            Nlow[0] = nlow0
        if Ntop[0] == -1:
            Ntop[0] = min(ntop0, 50)
        if not options.flagasys and not options.flagldglobal:
            if ldmod <= 3:
                if _fv(alev) == 0.0:
                    alev = p("aadjust") * _t(ald0)
                for ib in bars:
                    if _fv(Pshift[ib]) == SENTINEL:
                        Pshift[ib] = _t(pshift0) + p("pshiftadjust", ib)
            else:
                if _fv(ctable[0]) == SENTINEL:
                    ctable[0] = _t(ald0)
                if _fv(ptable[0]) == SENTINEL:
                    ptable[0] = _t(pshift0)
            ctable[0] = ctable[0] + p("ctableadjust", 0)
            ptable[0] = ptable[0] + p("ptableadjust", 0)

    # --- discrete levels padded as TALYS's edis/jdis (0 beyond nlevmax2)
    edis = torch.zeros(NUMLEV2 + 1, dtype=DTYPE)
    jdis = torch.zeros(NUMLEV2 + 1, dtype=DTYPE)
    n2 = min(int(levels.nlevmax2), NUMLEV2)
    edis[: n2 + 1] = levels.all_e_mev[: n2 + 1].to(DTYPE)
    jdis[: n2 + 1] = levels.all_spin[: n2 + 1].to(DTYPE)

    # --- Nlast/Ntop/Nlow (densitypar.f90:344-355)
    Nlast = []
    for ib in bars:
        Nlast.append(int(levels.nlev) if ib == 0 else max(int(bar.nfistrrot[ib]), 1))
        if Ntop[ib] == -1:
            Ntop[ib] = Nlast[ib]
        if Nlow[ib] == -1:
            Nlow[ib] = 2
        if Ntop[ib] <= 2:
            Nlow[ib] = 0

    # --- discrete spin cutoff (densitypar.f90:363-389)
    scutoffsys = (_f32(0.83) * (A ** _f32(0.26))) ** 2
    scut = []
    ediscrete = []
    for ib in bars:
        s = _t(scutoffsys)
        ed = _t(0.0)
        if ldparexist:
            imax = Ntop[ib]
            if ib == 0:
                imin = Nlow[0]
                ed = 0.5 * (edis[imin] + edis[imax])
                rj = jdis[imin : imax + 1]
            else:
                imin = 1
                ef = bar.efistrrot_mev[ib]
                jf = bar.jfistrrot[ib]
                ed = 0.5 * (_t(ef[imin]) + _t(ef[imax]))
                rj = _t(jf[imin : imax + 1])
            sigsum = (rj * (rj + 1) * (2 * rj + 1)).sum()
            denom = (2 * rj + 1).sum()
            sd = sigsum / (3.0 * denom) if _fv(denom) != 0.0 else _t(0.0)
            if scutoffsys / 3.0 < _fv(sd) < scutoffsys * 3.0:
                s = sd
        scut.append(s)
        ediscrete.append(ed)
    scutoffdisc = torch.stack(scut)
    Ediscrete = torch.stack(ediscrete)

    # --- a, deltaW, alimit, gammald (densitypar.f90:398-431)
    alimit = p("alimit")
    inpalev = _fv(alev) != 0.0
    if inpalev and ldmod == 3 and _fv(alimit) == 0.0:
        alimit = alev
    deltaW = pb("deltaw").clone()
    inpdeltaW = True
    if _fv(deltaW[0]) == 0.0:
        inpdeltaW = False
        from physics.hf.structure.masses import mliquid1, mliquid2

        mldm = mliquid1(Z, A) if options.shellmodel == 1 else mliquid2(Z, A)
        deltaW[0] = _t((_fv(masses.mass_amu[Zix, Nix]) - mldm) * amu)
    inpalimit = True
    if _fv(alimit) == 0.0:
        inpalimit = False
        alimit = p("alphald") * A + p("betald") * (A**twothird)
    gammald = p("gammald")
    inpgammald = True
    if _fv(gammald) == -1.0:
        inpgammald = False
        gammald = p("gammashell1") / (A**onethird) + _t(params["gammashell2"])
    if inpalev and inpdeltaW and inpalimit and inpgammald:
        inpalev = False
        alev = _t(0.0)

    # --- pairing (densitypar.f90:437-453)
    oddZ, oddN = Z % 2, N % 2
    delta0 = _t(params["pairconstant"]) / math.sqrt(_fv(A))
    pair = p("pair")
    if _fv(pair) == SENTINEL:
        if ldmod == 3:
            pair = (oddZ + oddN) * delta0
        elif ldmod == 2:
            pair = (1 - oddZ - oddN) * delta0
        else:
            pair = (2 - oddZ - oddN) * delta0
    for ib in bars:
        if _fv(Pshift[ib]) == SENTINEL:
            Pshift[ib] = p("pshiftconstant") + p("pshiftadjust", ib)

    # --- fission barrier shell corrections (densitypar.f90:458-477)
    axtype = tuple(options.axtype_of(Zix, Nix, ib) if ib > 0 else 1 for ib in bars)
    if options.flagfission:
        for ib in range(1, nbar + 1):
            if _fv(deltaW[ib]) == 0.0:
                if options.flagcolldamp:
                    deltaW[ib] = deltaW[0].abs() * twothird
                elif ib == 1:
                    deltaW[ib] = _t(1.5 if axtype[1] == 1 else 2.5)
                else:
                    deltaW[ib] = _t(0.6)
        if nbar == 1 and bar.fbarrier_mev[1] == 0.0:  # :477 reads the unset slot 2
            deltaW[1] = p("deltaw", 2)

    # --- generalised superfluid critical quantities, and delta (densitypar.f90:485-520)
    S = _t(masses.s_mev[Zix, Nix, 1])
    Tcrit = _t(0.0)
    zeros = torch.zeros(nbar + 1, dtype=DTYPE)
    aldcrit, Econd, Ucrit, Scrit, Dcrit = (zeros.clone() for _ in range(5))
    if ldmod == 3:
        Tcrit = _f32(0.567) * delta0
        ald = alimit
        difprev = 0.0
        acrit = []
        for ib in bars:
            iloop = 0
            while True:
                factor = (1.0 - torch.exp(-gammald * ald * Tcrit**2)) / (ald * (Tcrit**2))
                ac = alimit * (1.0 + deltaW[ib] * factor)
                d = abs(_fv(ac) - _fv(ald))
                if d > 0.001 and d != difprev and iloop <= 1000:
                    difprev = d
                    ald = ac
                    iloop += 1
                    if _fv(ald) <= 1.0:
                        break
                else:
                    break
            if _fv(ac) < _fv(alimit) / 3.0:
                expo = torch.clamp(-gammald * S, max=80.0)
                fU = 1.0 - torch.exp(expo)
                factor = 1.0 + fU * deltaW[ib] / S
                ac = torch.clamp(alimit * factor, min=1.0)
            acrit.append(ac)
        aldcrit = torch.stack(acrit)
        Econd = 1.5 / pi2 * aldcrit * delta0**2
        Ucrit = aldcrit * Tcrit**2 + Econd
        Scrit = 2.0 * aldcrit * Tcrit
        Dcrit = 144.0 / pi * (aldcrit**3) * (Tcrit**5)
        delta = Econd - pair - Pshift
    else:
        delta = pair + Pshift

    # --- a(Sn) or the parameter it leaves free (densitypar.f90:524-556)
    Spair = torch.clamp(S - delta[0], min=1.0)
    if not inpalev:
        fU = 1.0 - torch.exp(-gammald * Spair)
        factor = 1.0 + fU * deltaW[0] / Spair
        alev = torch.clamp(p("aadjust") * alimit * factor, min=1.0)
    elif ldmod != 3:
        fU = 1.0 - torch.exp(-gammald * Spair)
        if not inpalimit:
            factor = 1.0 + fU * deltaW[0] / Spair
            alimit = alev / factor
        elif not inpdeltaW:
            factor = alev / alimit - 1.0
            deltaW[0] = Spair * factor / fU
        else:
            argum = 1.0 - Spair / deltaW[0] * (alev / alimit - 1.0)
            if 0.0 < _fv(argum) < 1.0:
                gammald = -1.0 / Spair * torch.log(argum)
            else:
                factor = alev / alimit - 1.0
                deltaW[0] = Spair * factor / fU

    # --- exciton single-particle densities (densitypar.f90:560-567)
    kph = _t(params["kph"])
    g = p("g")
    if _fv(g) == 0.0:
        g = A / kph
    g = p("gadjust") * g
    gp = p("gp")
    if _fv(gp) == 0.0:
        gp = Z / kph
    gn = p("gn")
    if _fv(gn) == 0.0:
        gn = N / kph
    gn = p("gadjust") * p("gnadjust") * gn
    gp = p("gadjust") * p("gpadjust") * gp

    # --- moments of inertia (deformpar.f90, T2) and barrier beta2
    if deformation is None:
        # NX2 ld: only Irigid0/Irigid are read, and they need neither the .def file nor the levels
        from physics.hf.structure.deformation import rigid_moments

        irigid0, irigid = rigid_moments(Z, A, options, masses, params, nbar)
    else:
        irigid0, irigid = deformation.irigid0, deformation.irigid
    Irigid0 = _t(irigid0)
    Irigid = torch.stack([_t(irigid[ib]) for ib in bars])
    beta2 = torch.stack(
        [_t(masses.beta2[Zix, Nix]) if ib == 0 else p("beta2", ib) for ib in bars]
    )

    return LDNucleus(
        Z=Z,
        A=A,
        Zix=Zix,
        Nix=Nix,
        ldmodel=ldmod,
        flagcol=flagcol,
        nfisbar=nbar,
        spincutmodel=options.spincutmodel,
        kvibmodel=options.kvibmodel,
        flagcolldamp=options.flagcolldamp,
        fismodel=options.fismodel,
        flagparity=options.flagparity,
        ldparexist=ldparexist,
        alev=_t(alev),
        alimit=_t(alimit),
        gammald=_t(gammald),
        deltaW_mev=deltaW,
        pair_mev=_t(pair),
        delta0_mev=_t(delta0),
        Pshift_mev=Pshift,
        delta_mev=delta,
        scutoffdisc=scutoffdisc,
        Ediscrete_mev=Ediscrete,
        Nlow=tuple(Nlow),
        Ntop=tuple(Ntop),
        Nlast=tuple(Nlast),
        ctable=ctable,
        ptable_mev=ptable,
        s2adjust=pb("s2adjust"),
        Rspincut=_t(params["rspincut"]),
        Krotconstant=pb("krotconstant"),
        Ufermi_mev=pb("ufermi"),
        cfermi_mev=pb("cfermi"),
        Irigid0=Irigid0,
        Irigid=Irigid,
        beta2=beta2,
        axtype=axtype,
        S_mev=S,
        Tcrit_mev=_t(Tcrit),
        aldcrit=aldcrit,
        Econd_mev=Econd,
        Ucrit_mev=Ucrit,
        Scrit=Scrit,
        Dcrit=Dcrit,
        T_mev=pb("t"),
        E0_mev=pb("e0"),
        Exmatch_mev=pb("exmatch"),
        Tadjust=pb("tadjust"),
        E0adjust=pb("e0adjust"),
        Exmatchadjust=pb("exmatchadjust"),
        g=_t(g),
        gn=_t(gn),
        gp=_t(gp),
        edis_mev=edis,
        jdis=jdis,
        nlev=int(levels.nlev),
        nlevmax2=int(levels.nlevmax2),
        barriers=bar,
        ldexist=tuple(False for _ in bars),
        tables=tuple(None for _ in bars),
    )


def _safe(x: Tensor, ok: Tensor, fill: float = 1.0) -> Tensor:
    return torch.where(ok, x, fill)


def ignatyuk(ld: LDNucleus, eex_mev: Tensor, ibar: int = 0) -> Tensor:
    """Energy-dependent level density parameter a(Eex) [MeV^-1] (Ignatyuk 1975), with the BRC
    Fermi-distribution damping when `colldamp y`. Elementwise over eex.

    TALYS: ignatyuk.f90:1 (ignatyuk)
    Test: A-ld
    """
    if _fast_ok(eex_mev):
        return _ignatyuk_fast(ld, eex_mev, ibar)
    eex = _t(eex_mev)
    U = eex - ld.delta_mev[ibar]
    aldlim = ld.alimit
    pos = U > 0.0
    Us = _safe(U, pos)
    expo = ld.gammald * Us
    fU = torch.where(expo.abs() <= 80.0, 1.0 - torch.exp(-_safe(expo, expo.abs() <= 80.0)), 1.0)
    damp = torch.where(pos, 1.0 + fU * ld.deltaW_mev[ibar] / Us, 1.0 + ld.deltaW_mev[ibar] * ld.gammald)
    if ld.flagcolldamp:  # ignatyuk.f90:71-79
        aldlow = ld.A / 13.0
        e = (U - ld.Ufermi_mev[0]) / ld.cfermi_mev[0]
        qfermi = torch.where(e > -80.0, 1.0 / (1.0 + torch.exp(-torch.clamp(e, min=-80.0))), 0.0)
        aldlim = aldlow * qfermi + aldlim * (1.0 - qfermi)
    return torch.clamp(aldlim * damp, min=1.0)


def spincut(
    ld: LDNucleus, ald: Tensor, eex_mev: Tensor, ibar: int = 0, ipop: int = 0,
    rspincutff: float = 4.0,
) -> Tensor:
    """Spin cutoff parameter sigma^2 (dimensionless): interpolated linearly between the discrete
    value at Ediscrete and the model value at the matching energy below it, the model value
    (spincutmodel 1: I0/alimit sqrt(aU); 2: I0 sqrt(U/a)) above it. `ipop` 1 uses Rspincutff
    (initial population) instead of Rspincut.

    TALYS: spincut.f90:1 (spincut)
    Test: A-ld
    """
    if _fast_ok(eex_mev) and _fast_ok(ald):
        return _spincut_fast(ld, ald, eex_mev, ibar, ipop, rspincutff)
    eex = _t(eex_mev)
    ald = _t(ald)
    Rs = _t(rspincutff) if ipop == 1 else ld.Rspincut
    s2 = ld.s2adjust[ibar]
    ldmod = ld.ldmodel
    if ld.spincutmodel == 1:
        scutconst = Rs * s2 * ld.Irigid0 / ld.alimit
    else:
        scutconst = Rs * s2 * ld.Irigid0
    Em = ld.Exmatch_mev[ibar]
    if ldmod == 2 or ldmod >= 4:
        Em = ld.S_mev
    if ldmod == 3:
        Em = ld.Ucrit_mev[ibar] - ld.pair_mev - ld.Pshift_mev[ibar]
    sdisc = ld.scutoffdisc[ibar]
    colld = 1.0 + ld.beta2[ibar] / 3.0 if (ld.flagcolldamp and ibar != 0) else None

    # 1. below the matching energy
    aldm = ignatyuk(ld, Em, ibar)
    Umatch = Em - ld.pair_mev - ld.Pshift_mev[ibar]
    okm = Umatch > 0.0
    Um = _safe(Umatch, okm)
    if ld.spincutmodel == 1:
        s2m = scutconst * ld.aldcrit[ibar] * ld.Tcrit_mev if ldmod == 3 else scutconst * torch.sqrt(aldm * Um)
    else:
        s2m = scutconst * ld.Tcrit_mev if ldmod == 3 else scutconst * torch.sqrt(Um / aldm)
    s2m = torch.where(okm, s2m, sdisc)
    if colld is not None:
        s2m = colld * s2m
    Ed = ld.Ediscrete_mev[ibar]
    interp = (_fv(Em) != _fv(Ed)) & (eex > Ed)
    denom = Em - Ed if _fv(Em) != _fv(Ed) else _t(1.0)
    below = torch.where(interp, sdisc + (eex - Ed) / denom * (s2m - sdisc), sdisc.expand_as(eex))

    # 2. above the matching energy
    U = eex - ld.delta_mev[ibar]
    okU = U > 0.0
    Us = _safe(U, okU)
    above = scutconst * torch.sqrt(ald * Us) if ld.spincutmodel == 1 else scutconst * torch.sqrt(Us / ald)
    above = torch.where(okU, above, sdisc)

    sc = torch.where(eex <= Em, below, above)
    if colld is not None:
        sc = colld * sc
    return torch.maximum(sdisc.expand_as(sc), sc)


def spindis(sc: Tensor, J: Tensor) -> Tensor:
    """Wigner spin distribution (2J+1)/(2 sigma^2) exp(-(J+1/2)^2 / (2 sigma^2)). Dimensionless.

    TALYS: spindis.f90:1 (spindis)
    Test: A-ld
    """
    sc, J = _t(sc), _t(J)
    sigma22 = 2.0 * sc
    return (2.0 * J + 1.0) / sigma22 * torch.exp(-((J + 0.5) ** 2) / sigma22)


def colenhance(
    ld: LDNucleus, eex_mev: Tensor, ald: Tensor, ibar: int = 0
) -> tuple[Tensor, Tensor, Tensor]:
    """Collective enhancement (Krot, Kvib, Kcoll), dimensionless, all 1 when `colenhance n`, below
    the CTM matching energy for ldmodel 1, or for U <= 0. Kvib from the liquid-drop (kvibmodel 1,
    damped) or Bose-gas (kvibmodel 2) formula; Krot from the rigid-body spin cutoff, damped by a
    Fermi function at Ufermi.

    TALYS: colenhance.f90:1 (colenhance)
    Test: A-ld
    """
    eex = _t(eex_mev)
    ald = _t(ald)
    one = torch.ones_like(eex)
    if not ld.flagcol:
        return one, one.clone(), one.clone()
    c = talys_constants()
    twothird, pi2, twopi = c["twothird"], c["pi2"], c["twopi"]
    A = ld.A
    U = eex - ld.delta_mev[ibar]
    active = U > 0.0
    if ld.ldmodel == 1:
        active = active & ~(eex < ld.Exmatch_mev[ibar])
    Us = _safe(U, U > 0.0)
    aldgs = ald if ibar == 0 else ignatyuk(ld, eex, 0)
    Temp = torch.sqrt(Us / aldgs)
    Kr = ld.Krotconstant[ibar]

    if ld.fismodel == 1 and ld.flagcolldamp:  # colenhance.f90:94-117
        if ibar == 0:
            return one, one.clone(), one.clone()
        if ld.axtype[ibar] == 2:
            aldint = ald * 8.0 / 13.5
            rotfactor = Kr * (Us / aldint) ** 0.25
        else:
            rotfactor = torch.clamp(Kr, min=1.0) * one
        damprot = 1.0 / (1.0 + torch.exp(-0.5 * (Us - 18.0)))
        Krot = rotfactor * (1.0 - damprot) + damprot
        Kvib = one.clone()
    else:
        avib = A / 13.0
        Pvib = ld.pair_mev
        posv = eex > Pvib
        Tvib = torch.where(posv, torch.sqrt(_safe(eex - Pvib, posv) / avib), torch.zeros_like(eex))
        okT = Tvib > 0.0
        Ts = _safe(Tvib, okT)
        if ld.kvibmodel == 1:
            expo = torch.clamp(0.0555 * (A**twothird) * (Ts ** (4.0 / 3.0)), max=80.0)
            Kvib0 = torch.where(okT, torch.exp(expo), one)
        else:
            deltaS = torch.zeros_like(eex)
            deltaU = torch.zeros_like(eex)
            Cvib = 0.0075 * (A ** c["onethird"])
            term = A ** (-5.0 / 6.0) / (1.0 + 0.05 * ld.deltaW_mev[ibar])
            omegavib = {2: 65.0 * term, 3: 100.0 * term}
            for l in (2, 3):
                gammavib = Cvib * (omegavib[l] ** 2 + 4.0 * pi2 * Ts**2)
                expo0 = gammavib / (2.0 * omegavib[l])
                expo = omegavib[l] / Ts
                ok = okT & (expo0 <= 80.0) & (expo > 0.0) & (expo <= 80.0)
                e0s = _safe(expo0, ok, 0.0)
                es = _safe(expo, ok, 1.0)
                nvib = torch.exp(-e0s) / (torch.exp(es) - 1.0)
                nvib = _safe(nvib, ok & (nvib > 0.0), 1.0)
                dS = (2 * l + 1) * ((1.0 + nvib) * torch.log(1.0 + nvib) - nvib * torch.log(nvib))
                dU = (2 * l + 1) * omegavib[l] * nvib
                deltaS = deltaS + torch.where(ok, dS, 0.0)
                deltaU = deltaU + torch.where(ok, dU, 0.0)
            Kvib0 = torch.where(okT, torch.exp(deltaS - deltaU / Ts), one)
        expo = (Us - ld.Ufermi_mev[ibar]) / ld.cfermi_mev[ibar]
        okd = expo <= 80.0
        damper = torch.where(okd, 1.0 / (1.0 + torch.exp(_safe(expo, okd, 0.0))), 0.0)
        if ibar == 0:
            Krot0 = torch.clamp(Kr * ld.Irigid[0] * Temp, min=1.0)
        else:
            spincutbf = ld.Krotconstant[ibar] * ld.Irigid[ibar] * Temp
            ax = ld.axtype[ibar]
            if ax == 1:
                Krot0 = spincutbf
            elif ax == 2:
                Krot0 = 2.0 * spincutbf
            else:
                aldf = ignatyuk(ld, eex, ibar)
                term = spincutbf * torch.sqrt(
                    spincut(ld, aldf, eex, ibar) * (1.0 - twothird * ld.beta2[ibar].abs())
                )
                Krot0 = {3: 0.5, 4: 1.0, 5: 2.0}[ax] * math.sqrt(twopi) * term
            Krot0 = torch.clamp(Krot0, min=1.0)
        Krot = 1.0 + (Krot0 - 1.0) * damper
        Kvib = 1.0 + (Kvib0 - 1.0) * damper if ld.kvibmodel == 1 else Kvib0
    Kcoll = torch.clamp(Krot * Kvib, min=1.0)
    return (
        torch.where(active, Krot, one),
        torch.where(active, Kvib, one),
        torch.where(active, Kcoll, one),
    )


def with_matching(ld: LDNucleus, T_mev: Tensor, E0_mev: Tensor, Exmatch_mev: Tensor) -> LDNucleus:
    """`ld` with the constant-temperature matching quantities replaced (densitymatch.f90 result).

    TALYS: densitymatch.f90:1 (densitymatch)
    Test: A-ld
    """
    return replace(ld, T_mev=T_mev, E0_mev=E0_mev, Exmatch_mev=Exmatch_mev, matched=True)
