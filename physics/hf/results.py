"""Result schema of the port: names and units match the TALYS output files they replace.

Task: T10 (physics/hf/CONTRACT.md §7). Acceptance test: E2E (§6).

Every cross section is millibarns (contract §4.1), keyed the way TALYS names its files so the
E2E test is a join on the name: exclusive channels by TALYS's six-digit channel code
(`xs000000` = (n,g), `xs100000` = (n,n'), `xs200000` = (n,2n), `xs010000` = (n,p),
`xs000001` = (n,a); code digits = number of n, p, d, t, h, a emitted), per-level partials by
`<ejectile><residual-level>` (`nn.L01`), residual production by `rpZZZAAA`, totals by
`total`, `elastic`, `nonelastic`, `reaction`, fission by `fission`.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import torch
from torch import Tensor

PARSYM = "gnpdtha"  # constants.f90: parsym, types 0..6


@dataclass(frozen=True)
class Results:
    e_inc_mev: Tensor  # (C,)
    channels_mb: dict[str, Tensor] = field(default_factory=dict)  # "xs000000" -> (C,)
    levels_mb: dict[str, Tensor] = field(default_factory=dict)  # "nn.L01" -> (C,)
    residual_production_mb: dict[str, Tensor] = field(default_factory=dict)  # "rp026056" -> (C,)
    totals_mb: dict[str, Tensor] = field(default_factory=dict)  # "total", "elastic", ...
    # what the engine injected rather than computed, per family: "fission", "direct", "ecis", ...
    injected: tuple[str, ...] = ()
    # CHANOBS (INCOGNITA_CHANOBS, default off = empty): TALYS file/column names -> (C,), mb unless the name ends in
    # ":multiplicity" or ":branch" (physics/hf/emission/chanobs.py lists them)
    extras: dict[str, Tensor] = field(default_factory=dict)
    # ANGOUT (KWCOV B3: outangle / fileelastic / INCOGNITA_ANGOUT, default empty): discrete angular distributions and
    # Legendre coefficients under TALYS's file names, (C, nangle+1) mb/sr or (C, J2end+1); physics/hf/angout.py
    angular: dict[str, Tensor] = field(default_factory=dict)
    # SPECOBS (KWCOV B4: outspectra / ddxmode / outgamdis / INCOGNITA_SPECOBS, default empty): emission spectra, DDX,
    # discrete gamma lines and the (k0,g<p>) column under TALYS's file names; physics/hf/specobs.py lists them
    spectra: dict[str, Tensor] = field(default_factory=dict)
    # ASTRO (KWCOV B9: astro / astroE / astroT in a deck, default empty): astroout.f90's files as
    # {file name: {column: ndarray over T9}} (astrorate.g, astrorate.tot, astrorateZZZAAA.tot, macs.g, ...);
    # physics/hf/astro/rates.py
    astro: dict = field(default_factory=dict)
    # PRODUCTION (KWCOV B11: `production y` with a charged projectile, default empty): prodout.f90's isotope production
    # as {"files": {Y file name: {column: ndarray over time}}, "params": {Y file name: {...}}, "summary": [...],
    # "meta": {...}}; physics/hf/production.py
    production: dict = field(default_factory=dict)
    # URR (KWCOV B10: `urr y` / `urr <E>` / `endf y` on an incident-neutron run, default empty): urr.f90 / urrout.f90's
    # files as {file name: {column: ndarray over rows}} (urr.dat, urrgamwidth.l00, urrtalys.tot, urrnjoy.tot, ...);
    # physics/hf/urr.py
    urr: dict = field(default_factory=dict)
    # RECOIL (KWCOV B12: `recoil y` (+ `labddx y`) in a deck, default empty): residual recoil spectra
    # (rec<ZZZ><AAA>spec.tot, sp<nnnnnn>.rec) and LAB-frame spectra / DDX (<x>spec.lab, <x>ddx.lab, <x>ddxE....lab,
    # <x>ddxA....lab) under TALYS's file names, (C, ...); physics/hf/recoil.py lists them
    recoil: dict[str, Tensor] = field(default_factory=dict)
    # THERMAL (KWCOV B10b: an incident-neutron run with energies below eninclow, default empty): TALYS's rows for those
    # energies (thermal.f90), {"E": ndarray, "<result_arrays key>": ndarray over E, "eninclow", "E1v", "eref",
    # "xscaptherm"/"xsptherm"/"xsalphatherm" (isomer -1..10)}; the engine's own arrays at those energies are untouched.
    # physics/hf/thermal.py
    thermal: dict = field(default_factory=dict)
    # NATURAL (KWCOV B10b: `mass 0` in a deck, default empty): {"abundance": {A: fraction}, "isotopes": {A: Results}};
    # the Results' own arrays are then the abundance-weighted sums (natural.f90). physics/hf/natural.py
    natural: dict = field(default_factory=dict)
    # INTEGRAL (KWCOV B10b: `integral y` in a deck, default empty): integral.f90's effective cross sections,
    # {"integral.dat": {"file", "spectrum": list, "xseff_b", "xsexp_b", "ratio": ndarray}}. physics/hf/integral.py
    integral: dict = field(default_factory=dict)

    @property
    def n(self) -> int:
        return int(self.e_inc_mev.shape[0])


def channel_code(counts: tuple[int, int, int, int, int, int]) -> str:
    """TALYS's exclusive-channel file name from (n, p, d, t, h, a) emitted."""
    return "xs" + "".join(str(min(c, 9)) for c in counts)


def level_key(k0: int, ejectile: int, level: int) -> str:
    """The `.Lnn` file name of a discrete-level partial (discreteout.f90:179-181)."""
    return f"{PARSYM[k0]}{PARSYM[ejectile]}.L{level:02d}"


def residual_key(Z: int, A: int) -> str:
    """The `rpZZZAAA.tot` file name of a residual production cross section (finalout.f90:379)."""
    return f"rp{Z:03d}{A:03d}"


def stack(per_case: list[dict[str, float]], device=None) -> dict[str, Tensor]:
    """Turn one dict per case into the contract's name -> (C,) tensors, zero-filled where a case
    does not have that key (a channel that is closed at that energy)."""
    keys = sorted({k for d in per_case for k in d})
    return {k: torch.tensor([d.get(k, 0.0) for d in per_case], dtype=torch.float64, device=device)
            for k in keys}
