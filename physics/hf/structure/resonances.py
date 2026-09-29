"""Average resonance data TALYS reads for normalisation: D0, Gamma_gamma, S0
(structure/resonances/*.res).

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T2 (physics/hf/CONTRACT.md §7). Acceptance test: A-struct (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    resonancepar.f90:1 (resonancepar)

Two quirks of resonancepar.f90 that are reproduced, not fixed
-------------------------------------------------------------
* **Γγ units.** The `.res` column is keV (its header says so; Au198 1.28e-4 keV = 0.128 eV),
  and TALYS stores it unconverted in `gamgam`, which A0_talys_mod.f90 documents as eV and
  gammaout.f90 prints as ``experimental Gamma_gamma [eV]``. With the default ``gnorm n`` the
  value only reaches output; with ``gnorm y`` (radwidtheory.f90:253) TALYS normalises E1 to a
  width 1000x too small (GNORMFIX, 2026-09-17: C/E Gamma_gamma 1546 I-130, 784 Os-187, 1277
  Au-198 in stock output). Returned as ``gamgam_talys`` (TALYS's number, for matching its
  output only) and ``gamgam_ev`` (physical, what `radwidtheory` must be given; it refuses a keV
  number). `physics.talys.runner.write_input` adds ``gamgam Z A <eV>`` to stock-TALYS inputs
  with ``gnorm y`` so they do not inherit the bug.
* **Nrr is read from the wrong columns.** The format "(4x, 2i4, 8es15.6, i4)" ends at column
  136, but the files right-align the resonance count in columns 133-137 ("   61"), so TALYS reads
  the first digit(s) only (Ni059: 6, not 61). And `Eavres` is reset to 0.01 MeV at the top of
  every call (:74), so only the value from the LAST resonancepar call survives, which is not the
  compound nucleus in a normal run.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np

from physics.hf.structure.files import read_d0global, read_resonance_file

if TYPE_CHECKING:
    from physics.hf.input.defaults import Options, Params

__all__ = ["ResonanceData", "resonance_parameters", "d0_extension"]

EV_PER_KEV = 1.0e3


@dataclass(frozen=True)
class ResonanceData:
    """Average resonance parameters of one nucleus as TALYS holds them.

    Units: `d0_ev`, `dd0_ev`, `d1_ev` (TALYS `D1r`), `d0global_ev` in eV; `s0`, `s1` in units of
    1e-4 (as tabulated); `r_scat_fm` in fm; `gamgam_talys` is TALYS's `gamgam` (numerically keV,
    labelled eV by TALYS), `gamgam_ev` the physical width in eV. Zero means "not tabulated".
    `eavres_mev` is what this call sets `Eavres` to (0.01 unless this nucleus is the compound
    nucleus with D0 and Nrr).
    """

    Z: int
    A: int
    d0_ev: float
    dd0_ev: float
    s0: float
    ds0: float
    gamgam_talys: float
    dgamgam_talys: float
    r_scat_fm: float
    dr_scat_fm: float
    nrr: int
    d1_ev: float
    dd1_ev: float
    s1: float
    ds1: float
    d0global_ev: float
    eavres_mev: float

    @property
    def gamgam_ev(self) -> float:
        return self.gamgam_talys * EV_PER_KEV


def _f32(x: float) -> float:
    return float(np.float32(x))


def d0_extension(ldmodel: int, flagcol: bool) -> str | None:
    """File extension of the global D0 table for a level-density model (resonancepar.f90:114-122).

    TALYS: resonancepar.f90:1 (resonancepar)
    Test: A-struct
    """
    if ldmodel in (1, 2, 3):
        return f"ld{ldmodel}{'y' if flagcol else 'n'}"
    if ldmodel in (4, 5, 6, 7):
        return f"ld{ldmodel}"
    return None


def resonance_parameters(
    Z: int, A: int, options: Options | None = None, params: Params | None = None
) -> ResonanceData:
    """Experimental D0 [eV], D0 uncertainty, Gamma_gamma and S0 as TALYS reads them
    (cross-check: ld*.gs 'experimental D0 [eV]', psf* 'experimental Gamma_gamma [eV]').

    `options` selects the D0global table (ldmodel, flagcol of this nucleus) and whether this is
    the compound nucleus (for Eavres); `params` supplies `gamgamadjust` (default 1). User keywords
    that TALYS lets override the file (D0, gamgam, S0, ...) are not applied here.

    TALYS: resonancepar.f90:1 (resonancepar)
    Test: A-struct
    """
    D0 = dD0 = S0 = dS0 = gg = dgg = R = dR = D1 = dD1 = S1 = dS1 = 0.0
    nrr = 0
    eavres = _f32(0.01)
    is_cn = options is not None and (options.Zinit, options.Ninit) == (Z, A - Z)
    for ia, L, Df, dDf, Sf, dSf, ggf, dggf, Rf, dRf, nrrf in read_resonance_file(Z):
        if ia != A:
            continue
        Df, dDf, Sf, dSf = _f32(Df), _f32(dDf), _f32(Sf), _f32(dSf)
        ggf, dggf, Rf, dRf = _f32(ggf), _f32(dggf), _f32(Rf), _f32(dRf)
        if L == 0:
            if dSf != 0.0 and S0 == 0.0:
                dS0 = dSf
            if Sf != 0.0 and S0 == 0.0:
                S0 = Sf
            if dDf != 0.0 and D0 == 0.0:
                dD0 = dDf
            if Df != 0.0 and D0 == 0.0:
                D0 = Df
            if dggf != 0.0 and gg == 0.0:
                dgg = dggf
            if ggf != 0.0 and gg == 0.0:
                gg = ggf
            if dRf != 0.0 and R == 0.0:
                dR = dRf
            if Rf != 0.0 and R == 0.0:
                R = Rf
            if nrrf != 0:
                nrr = nrrf
            if is_cn and nrrf > 0 and D0 > 0.0:
                eavres = _f32(
                    np.float32(0.5) * (np.float32(nrrf - 1) * np.float32(D0)) * np.float32(1.0e-6)
                )
        else:
            if dDf != 0.0 and D1 == 0.0:
                dD1 = dDf
            if Df != 0.0 and D1 == 0.0:
                D1 = Df
            if dSf != 0.0 and S1 == 0.0:
                dS1 = dSf
            if Sf != 0.0 and S1 == 0.0:
                S1 = Sf
    adjust = 1.0
    if params is not None and options is not None and "gamgamadjust" in params:
        adjust = float(params.at("gamgamadjust", options.Zinit - Z, options.Ninit - (A - Z)))
    gg = _f32(np.float32(adjust) * np.float32(gg))
    d0g = 0.0
    if options is not None:
        Zix, Nix = options.Zinit - Z, options.Ninit - (A - Z)
        ext = d0_extension(options.ldmodel_of(Zix, Nix), options.flagcol_of(Zix, Nix))
        if ext is not None:
            v = read_d0global(ext, Z, A)
            d0g = _f32(v) if v is not None else 0.0
    return ResonanceData(
        Z=Z,
        A=A,
        d0_ev=D0,
        dd0_ev=dD0,
        s0=S0,
        ds0=dS0,
        gamgam_talys=gg,
        dgamgam_talys=dgg,
        r_scat_fm=R,
        dr_scat_fm=dR,
        nrr=nrr,
        d1_ev=D1,
        dd1_ev=dD1,
        s1=S1,
        ds1=dS1,
        d0global_ev=d0g,
        eavres_mev=eavres,
    )
