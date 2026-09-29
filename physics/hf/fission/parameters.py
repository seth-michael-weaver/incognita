"""Fission barrier parameters: heights, curvatures, class-II states, barrier level densities
(fission/barrier, fission/states tables; Sierk systematics, RLDM).

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T11 (physics/hf/CONTRACT.md §7). Acceptance test: A-fis (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    fissionpar.f90:1 (fissionpar)
    rotband.f90:1 (rotband)
    rotclass2.f90:1 (rotclass2)

What the default run actually does
----------------------------------
`fismodel` defaults to 6 (input_fissionmodel.f90:85), so for every fissile nucleus TALYS reads
the BSkG3 deformation-energy path and runs the WKB machinery in :mod:`physics.hf.fission.wkb`;
`fbarrier`/`fwidth` are *outputs* of that fit, not table look-ups. `hbstate` and `class2` both
default to false (input_fissionmodel.f90:87-88), so the default run has **no** head-band
transition states, no rotational bands on the barriers and no class-II states: every barrier
is pure continuum from `fecont = 0`. The tabulated (`fismodel` 1-4) and state-file branches are
ported here too because they are what the `fisbar`/`hbstate`/`class2` keywords select, and they
are what supplies :class:`physics.hf.density.parameters.BarrierLevels` (T6's `ibar > 0` path).

`Cbarrier`, `fbaradjust`, `fwidthadjust`, `betafiscor`, `vfiscor` and `rmiufiscor` enter as
`Params` tensors (contract §4.4), so barrier heights and widths stay differentiable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING


import torch
from torch import Tensor

from physics.hf.core.constants import nuclide_symbol
from physics.hf.core.tensors import DTYPE
from physics.hf.fission.wkb import NUMBAR, FissionPath, WKBResult, read_hfbpath, wkb
from physics.hf.structure.files import fortran_read, talys_structure_dir

if TYPE_CHECKING:
    from physics.hf.input.defaults import Options, Params
    from physics.hf.structure.deformation import Deformation

NUMROT = 700  # A0_talys_mod.f90:55
NUMLEV = 40  # A0_talys_mod.f90:43


def _t(x, device=None) -> Tensor:
    return torch.as_tensor(x, dtype=DTYPE, device=device)


@dataclass(frozen=True)
class TransitionStates:
    """A band of transition (or class-II) states on one barrier: `n` states with energies [MeV],
    spins and parities, 1-based with a dummy element 0 as in TALYS."""

    n: int = 0
    e_mev: Tensor = field(default_factory=lambda: torch.zeros(1, dtype=DTYPE))
    spin: Tensor = field(default_factory=lambda: torch.zeros(1, dtype=DTYPE))
    parity: tuple[int, ...] = (0,)


@dataclass(frozen=True)
class FissionParameters:
    """Everything `fissionpar.f90` leaves for one compound nucleus `(Zix, Nix)`.

    Per-barrier tuples are 1-based with a dummy element 0. `fbarrier_mev`/`fwidth_mev` are the
    raw `fbarrier`/`fwidth` arrays (the shell correction and the `fisadjust` factors are applied
    in `t1barrier`, not here). `headband[i]` is `nfistrhb`/`efistrhb`/..., `rotational[i]` is the
    band `rotband` builds from it, `class2[i]`/`class2rot[i]` the same pair for class-II states.
    """

    Z: int
    A: int
    Zix: int
    Nix: int
    fismodelx: int
    nfisbar: int
    fbarrier_mev: Tensor  # (NUMBAR + 1,)
    fwidth_mev: Tensor
    fecont_mev: Tensor
    axtype: tuple[int, ...]
    minertia: Tensor
    minertc2: Tensor
    widthc2_mev: Tensor
    nclass2: int
    emaxclass2_mev: Tensor
    headband: tuple[TransitionStates, ...]
    rotational: tuple[TransitionStates, ...]
    class2: tuple[TransitionStates, ...]
    class2rot: tuple[TransitionStates, ...]
    path: FissionPath | None = None
    wkb: WKBResult | None = None
    # FISBARWIRE: `fbaradjust`/`fwidthadjust` per barrier, (NUMBAR + 1,), which `t1barrier`
    # multiplies into the height and curvature (t1barrier.f90:99-121). None where every factor is
    # 1, which leaves the default arithmetic exactly as it was.
    fbaradjust: Tensor | None = None
    fwidthadjust: Tensor | None = None


# ------------------------------------------------------------------ tabulated barrier files


def _bar_file(Z: int, sub: str) -> Path:
    return talys_structure_dir() / "fission" / sub / f"{nuclide_symbol(Z)}.bar"


def read_barrier_file(Z: int, A: int) -> tuple[float, float, float, float] | None:
    """RIPL/Maslov experimental barriers `(B1, hw1, B2, hw2)` [MeV] for `fismodel` 1.

    TALYS: fissionpar.f90:138-159 (fissionpar), ``read(2,'(4x,i4,4x,1x,2(f8.2),5x,2(f8.2))')``
    Test: A-fis
    """
    p = _bar_file(Z, "barrier")
    if not p.exists():
        return None
    for line in p.read_text().splitlines():
        ia, bar1, hw1, bar2, hw2 = fortran_read(line, "4x,i4,4x,1x,f8.2,f8.2,5x,f8.2,f8.2")
        if ia == A:
            return float(bar1), float(hw1), float(bar2), float(hw2)
    return None


def read_mamdouh_file(Z: int, A: int) -> tuple[float, float] | None:
    """Mamdouh barriers `(B1, B2)` [MeV] for `fismodel` 2.

    TALYS: fissionpar.f90:163-184 (fissionpar), ``read(2,'(4x,i4,2(24x,f8.2))')``
    Test: A-fis
    """
    p = _bar_file(Z, "mamdouh")
    if not p.exists():
        return None
    out = None
    for line in p.read_text().splitlines():
        ia, bar1, bar2 = fortran_read(line, "4x,i4,24x,f8.2,24x,f8.2")
        if ia == A:
            out = (float(bar1), float(bar2))  # TALYS keeps scanning; last match wins
    return out


def _states_file(Z: int, N: int, kind: str) -> Path:
    ext = ("ee", "eo", "oe", "oo")[2 * (Z % 2) + (N % 2)]
    return talys_structure_dir() / "fission" / "states" / f"{kind}.{ext}"


def read_headband_states(Z: int, N: int, nfisbar: int, path: str | None = None):
    """Head-band transition states per barrier from `structure/fission/states/hbstates.*`.

    Returns `(states, fecont)` where `fecont[i]` [MeV] is the start of the continuum on barrier
    `i`. Read only when `hbstate y` (off by default).

    TALYS: fissionpar.f90:346-363 (fissionpar), ``read(2,'(4x,i4,f8.3)')`` then
    ``read(2,'(4x,f11.6,f6.1,i5)')``
    Test: A-fis
    """
    p = Path(path) if path else _states_file(Z, N, "hbstates")
    lines = p.read_text().splitlines()
    out = [TransitionStates()]
    fecont = [0.0] * (NUMBAR + 1)
    k = 0
    for i in range(1, nfisbar + 1):
        n, ec = fortran_read(lines[k], "4x,i4,f8.3")
        k += 1
        n = min(int(n), NUMLEV)
        fecont[i] = float(ec)
        e, j, pi = [0.0], [0.0], [0]
        for _ in range(n):
            ee, jj, pp = fortran_read(lines[k], "4x,f11.6,f6.1,i5")
            k += 1
            e.append(float(ee))
            j.append(float(jj))
            pi.append(int(pp))
        out.append(TransitionStates(n, _t(e), _t(j), tuple(pi)))
    while len(out) <= NUMBAR:
        out.append(TransitionStates())
    return tuple(out), _t(fecont)


def read_class2_states(Z: int, N: int, nclass2: int, path: str | None = None):
    """Class-II head states per well from `structure/fission/states/class2states.*`.

    TALYS: fissionpar.f90:365-383 (fissionpar), ``read(2,'(4x,i4)')`` then
    ``read(2,'(4x,f11.6,f6.1,i5)')``
    Test: A-fis
    """
    p = Path(path) if path else _states_file(Z, N, "class2states")
    lines = p.read_text().splitlines()
    out = [TransitionStates()]
    k = 0
    for _ in range(nclass2):
        (n,) = fortran_read(lines[k], "4x,i4")
        k += 1
        n = min(int(n), NUMLEV)
        e, j, pi = [0.0], [0.0], [0]
        for _ in range(n):
            ee, jj, pp = fortran_read(lines[k], "4x,f11.6,f6.1,i5")
            k += 1
            e.append(float(ee))
            j.append(float(jj))
            pi.append(int(pp))
        out.append(TransitionStates(n, _t(e), _t(j), tuple(pi)))
    while len(out) <= NUMBAR:
        out.append(TransitionStates())
    return tuple(out)


# ------------------------------------------------------------------ rotational bands


def _build_band(
    head: TransitionStates, moment: Tensor, ecut: Tensor, nmax: int
) -> TransitionStates:
    """The rotational band on one set of head states, cut at `ecut` and sorted in energy.

    Each head state `K` generates ``E = E_head + [J(J+1) - K(K+1)] / 2I``; a `K = 0` head steps
    in 2 units of J, and a `0-` head starts at `J = 1` with the extra `1/I` shift between the
    `K = 0-` and `K = 1-` bands.
    """
    e_out: list[float] = []
    j_out: list[float] = []
    p_out: list[int] = []
    inertia = float(moment)
    cut = float(ecut)
    for i in range(1, head.n + 1):
        jstart = float(head.spin[i])
        jstep = 1.0
        erk10 = 0.0
        if jstart == 0.0:
            jstep = 2.0
            if head.parity[i] == -1:
                jstart = 1.0
                erk10 = 1.0 / inertia
        rj = jstart - jstep
        while True:
            rj += jstep
            erot = (rj * (rj + 1.0) - jstart * (jstart + 1.0)) / (2.0 * inertia)
            eband = float(head.e_mev[i]) + erot + erk10
            if eband > cut:
                break
            e_out.append(eband)
            j_out.append(rj)
            p_out.append(head.parity[i])
            if len(e_out) >= nmax:
                break
        if len(e_out) >= nmax:
            break
    order = sorted(range(len(e_out)), key=lambda k: e_out[k])
    return TransitionStates(
        n=len(e_out),
        e_mev=_t([0.0] + [e_out[k] for k in order]),
        spin=_t([0.0] + [j_out[k] for k in order]),
        parity=(0,) + tuple(p_out[k] for k in order),
    )


def rotband(
    headband: tuple[TransitionStates, ...], minertia: Tensor, fecont_mev: Tensor, nfisbar: int
) -> tuple[TransitionStates, ...]:
    """Build the rotational band on each barrier's head-band transition states.

    TALYS: rotband.f90:1 (rotband)
    Test: A-fis
    """
    out = [TransitionStates()]
    for nbi in range(1, nfisbar + 1):
        out.append(_build_band(headband[nbi], minertia[nbi], fecont_mev[nbi], NUMROT))
    while len(out) <= NUMBAR:
        out.append(TransitionStates())
    return tuple(out)


def rotclass2(
    class2: tuple[TransitionStates, ...],
    minertc2: Tensor,
    fbarrier_mev: Tensor,
    fbaradjust: Tensor,
    fecont_mev: Tensor,
    widthc2_mev: Tensor,
    nfisbar: int,
) -> tuple[tuple[TransitionStates, ...], Tensor]:
    """Build the rotational bands on the class-II head states, and `Emaxclass2`.

    The cut-off used while building is ``Emaxclass2 + 0.5 widthc2``; TALYS subtracts the half
    width again afterwards (rotclass2.f90:126-130), and that reduced value is what `tfission`
    compares against.

    TALYS: rotclass2.f90:1 (rotclass2)
    Test: A-fis
    """
    emax = [torch.zeros((), dtype=DTYPE)] * (NUMBAR + 1)
    nclass2 = nfisbar - 1 if nfisbar in (2, 3) else 0
    for i in range(1, nclass2 + 1):
        emax[i] = (
            fbaradjust[i] * fbarrier_mev[i] + fecont_mev[i] + 0.5 * widthc2_mev[i]
        )
    out = [TransitionStates()]
    for nbi in range(1, nclass2 + 1):
        out.append(_build_band(class2[nbi], minertc2[nbi], emax[nbi], NUMROT))
    while len(out) <= NUMBAR:
        out.append(TransitionStates())
    for i in range(1, nclass2 + 1):
        emax[i] = emax[i] - 0.5 * widthc2_mev[i]
    return tuple(out), torch.stack([e.reshape(()) for e in emax])


# ------------------------------------------------------------------ fissionpar


def fission_parameters(
    Z: int,
    A: int,
    options: Options,
    params: Params,
    deformation: Deformation | None = None,
    *,
    levels=None,
    masses=None,
    device=None,
) -> FissionParameters:
    """fbarrier [MeV], fwidth [MeV], class-II well data per barrier as fissionpar.f90.

    Follows TALYS's model cascade: the chosen `fismodel`, then `fismodelalt` when its tables
    have nothing for this nuclide. For `fismodel` 5/6 the barriers come out of the WKB fit of
    the HFB path; the `WKBResult` is kept on the returned object because `t1barrier` needs its
    penetrability table.

    TALYS: fissionpar.f90:1 (fissionpar)
    Test: A-fis
    """
    N = A - Z
    Zix, Nix = options.Zinit - Z, options.Ninit - N
    if deformation is None:
        from physics.hf.structure.deformation import deformation as deformation_of
        from physics.hf.structure.levels import discrete_levels
        from physics.hf.structure.masses import masses as _masses

        masses = _masses(options, params) if masses is None else masses
        levels = discrete_levels(Z, A, options, masses, params) if levels is None else levels
        deformation = deformation_of(Z, A, options, levels, masses, params)

    p = lambda k, *i: params.at(k, *i)  # noqa: E731
    cbar = float(p("cbarrier"))
    # checkvalue.f90:1143-1144 -- without `sffactor y`, the two -1 sentinels become 1.
    vfiscor = float(p("vfiscor", Zix, Nix))
    rmiufiscor = float(p("rmiufiscor", Zix, Nix))
    if not options.flagsffactor:
        vfiscor = 1.0 if vfiscor == -1.0 else vfiscor
        rmiufiscor = 1.0 if rmiufiscor == -1.0 else rmiufiscor

    def _zero(t: Tensor) -> bool:
        """`fbarrier(i) == 0.` -- read without tripping autograd on a `requires_grad` tensor."""
        return float(t.detach()) == 0.0

    fbar = [torch.zeros((), dtype=DTYPE, device=device) for _ in range(NUMBAR + 1)]
    fwid = [torch.zeros((), dtype=DTYPE, device=device) for _ in range(NUMBAR + 1)]
    # user-supplied fisbar/fishw seed the arrays and set nfisbar (fissionpar.f90:120-123)
    nfisbar = 0
    for i in range(1, NUMBAR + 1):
        fbar[i] = p("fisbar", Zix, Nix, i).to(device=device)
        fwid[i] = p("fishw", Zix, Nix, i).to(device=device)
        if not _zero(fbar[i]) or not _zero(fwid[i]):
            nfisbar += 1

    fismodelx = options.fismodelx_of(Zix, Nix)
    axtype = [0] + [options.axtype_of(Zix, Nix, i) for i in range(1, NUMBAR + 1)]
    path: FissionPath | None = None
    wkbres: WKBResult | None = None

    for _attempt in range(2):
        fislocal = fismodelx
        if fislocal == 1:
            tab = read_barrier_file(Z, A)
            if tab is not None:
                b1, hw1, b2, hw2 = tab
                if _zero(fbar[1]):
                    fbar[1] = _t(cbar * b1, device)
                if _zero(fwid[1]):
                    fwid[1] = _t(hw1, device)
                if _zero(fbar[2]):
                    fbar[2] = _t(cbar * b2, device)
                if _zero(fwid[2]):
                    fwid[2] = _t(hw2, device)
                if nfisbar != 3:
                    nfisbar = 2
            if nfisbar == 0:
                fislocal = 2
        if fislocal == 2:
            tab = read_mamdouh_file(Z, A)
            if tab is not None:
                b1, b2 = tab
                if _zero(fbar[1]):
                    fbar[1] = _t(cbar * b1, device)
                if _zero(fbar[2]):
                    fbar[2] = _t(cbar * b2, device)
                nfisbar = 1 if (_zero(fbar[1]) or _zero(fbar[2])) else 2
        if fismodelx <= 2 and nfisbar == 0:
            fislocal = options.fismodelalt
        if fislocal in (3, 4):
            from physics.hf.fission.systematics import barsierk, rldm

            nfisbar = 1
            if fislocal == 3:
                bar1, _egs, _lbar0 = barsierk(Z, A, 0)
            else:
                egs, esp = rldm(Z, A, 0)
                bar1 = esp - egs
            if _zero(fbar[1]):
                fbar[1] = _t(cbar, device) * bar1.to(device=device)
            if _zero(fwid[1]):
                fwid[1] = _t(0.24, device)
        if fislocal >= 5:
            path = read_hfbpath(
                Z,
                A,
                fislocal,
                betafiscor=float(p("betafiscor", Zix, Nix)),
                betafiscoradjust=float(p("betafiscoradjust", Zix, Nix)),
                vfiscor=vfiscor,
                vfiscoradjust=float(p("vfiscoradjust", Zix, Nix)),
                rmiufiscor=rmiufiscor,
                rmiufiscoradjust=float(p("rmiufiscoradjust", Zix, Nix)),
                Cbarrier=cbar,
                device=device,
            )
            if path is None:  # fissionpar.f90:307-316: fall back and retry
                fismodelx = options.fismodelalt
                axtype[2] = 2
                continue
            wkbres = wkb(
                Z,
                A,
                path,
                fismodel=fislocal,
                nbinswkb=30 if options.nbins0 == 0 else options.nbins0,
                rmiufiscor=rmiufiscor,
                bdamp=(
                    float(p("bdamp", Zix, Nix, 1) * p("bdampadjust", Zix, Nix, 1)),
                    float(p("bdamp", Zix, Nix, 2) * p("bdampadjust", Zix, Nix, 2)),
                ),
                flagfispartdamp=options.flagfispartdamp,
            )
            nfisbar = wkbres.nbar
            for i in range(1, NUMBAR + 1):
                if i <= nfisbar:
                    fbar[i] = wkbres.fbarrier_mev[i]
                    fwid[i] = wkbres.fwidth_mev[i]
        break

    # --- head band and class2 states (fissionpar.f90:319-383) -----------------------------
    fecont = torch.zeros(NUMBAR + 1, dtype=DTYPE, device=device)
    headband = tuple(TransitionStates() for _ in range(NUMBAR + 1))
    if options.flaghbstate:
        headband, fecont = read_headband_states(Z, N, nfisbar)
        fecont = fecont.to(device=device)
    nclass2 = nfisbar - 1 if options.flagclass2 else 0
    class2 = tuple(TransitionStates() for _ in range(NUMBAR + 1))
    if options.flagclass2:
        class2 = read_class2_states(Z, N, nclass2)

    # --- default widths and moments of inertia (fissionpar.f90:385-396) --------------------
    if _zero(fwid[1]):
        fwid[1] = _t(1.0, device)
    if _zero(fwid[2]):
        fwid[2] = _t(0.6, device)
    if nfisbar == 1 and _zero(fbar[1]):
        fbar[1], fwid[1] = fbar[2], fwid[2]
    irigid = deformation.irigid
    minertia = [torch.zeros((), dtype=DTYPE, device=device)]
    minertc2 = [torch.zeros((), dtype=DTYPE, device=device)]
    for i in range(1, NUMBAR + 1):
        minertia.append(p("rtransmom", Zix, Nix, i).to(device=device) * _t(irigid[i], device))
        minertc2.append(p("rclass2mom", Zix, Nix, i).to(device=device) * _t(irigid[i], device))

    fbarrier = torch.stack(fbar)
    fwidth = torch.stack(fwid)
    minertia_t = torch.stack(minertia)
    minertc2_t = torch.stack(minertc2)
    widthc2 = torch.stack(
        [torch.zeros((), dtype=DTYPE, device=device)]
        + [p("class2width", Zix, Nix, i).to(device=device) for i in range(1, NUMBAR + 1)]
    )
    fbaradjust = torch.stack(
        [torch.ones((), dtype=DTYPE, device=device)]
        + [p("fisbaradjust", Zix, Nix, i).to(device=device) for i in range(1, NUMBAR + 1)]
    )

    fwidthadjust = torch.stack(
        [torch.ones((), dtype=DTYPE, device=device)]
        + [p("fishwadjust", Zix, Nix, i).to(device=device) for i in range(1, NUMBAR + 1)]
    )

    rotational = rotband(headband, minertia_t, fecont, nfisbar)
    class2rot: tuple[TransitionStates, ...] = tuple(TransitionStates() for _ in range(NUMBAR + 1))
    emaxclass2 = torch.zeros(NUMBAR + 1, dtype=DTYPE, device=device)
    if options.flagclass2:
        class2rot, emaxclass2 = rotclass2(
            class2, minertc2_t, fbarrier, fbaradjust, fecont, widthc2, nfisbar
        )

    return FissionParameters(
        Z=Z,
        A=A,
        Zix=Zix,
        Nix=Nix,
        fismodelx=fismodelx,
        nfisbar=nfisbar,
        fbarrier_mev=fbarrier,
        fwidth_mev=fwidth,
        fecont_mev=fecont,
        axtype=tuple(axtype),
        minertia=minertia_t,
        minertc2=minertc2_t,
        widthc2_mev=widthc2,
        nclass2=nclass2,
        emaxclass2_mev=emaxclass2,
        headband=headband,
        rotational=rotational,
        class2=class2,
        class2rot=class2rot,
        path=path,
        wkb=wkbres,
        fbaradjust=_unless_ones(fbaradjust),
        fwidthadjust=_unless_ones(fwidthadjust),
    )


def _unless_ones(t: Tensor) -> Tensor | None:
    """`t`, or None when every factor is exactly 1 and nothing asks for its gradient."""
    if t.requires_grad or bool((t.detach() != 1.0).any()):
        return t
    return None


def barrier_levels(fp: FissionParameters):
    """Adapt `FissionParameters` to T6's `density.parameters.BarrierLevels`.

    This is the seam between the two tasks (CONTRACT.md §5, `fission` -> `density`): it packages
    exactly the `nfisbar`/`nfistrrot`/`efistrrot`/`jfistrrot`/`axtype`/`fbarrier` arrays that
    `densitypar` reads from TALYS's fission globals. Nothing here computes physics.

    TALYS: densitypar.f90:1 (densitypar)
    Test: A-fis
    """
    from physics.hf.density.parameters import BarrierLevels

    n = fp.nfisbar

    def _pad(x: Tensor) -> Tensor:
        # TALYS's efistrrot/jfistrrot are numrot-long and zero-initialised, and densitypar reads
        # element 1 even for an empty band (Nlast = max(nfistrrot, 1), densitypar.f90:306).
        return x if x.numel() > 1 else torch.zeros(2, dtype=DTYPE, device=x.device)

    return BarrierLevels(
        nfisbar=n,
        nfistrrot=tuple(fp.rotational[i].n for i in range(NUMBAR + 1)),
        efistrrot_mev=tuple(_pad(fp.rotational[i].e_mev) for i in range(NUMBAR + 1)),
        jfistrrot=tuple(_pad(fp.rotational[i].spin) for i in range(NUMBAR + 1)),
        axtype=fp.axtype,
        fbarrier_mev=tuple(float(x.detach()) for x in fp.fbarrier_mev),
    )


__all__ = [
    "FissionParameters",
    "TransitionStates",
    "barrier_levels",
    "fission_parameters",
    "read_barrier_file",
    "read_class2_states",
    "read_headband_states",
    "read_mamdouh_file",
    "rotband",
    "rotclass2",
]

