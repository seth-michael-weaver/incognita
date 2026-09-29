"""ECIS-06 coupled channels and DWBA (J. Raynal), used by TALYS for every optical-model calculation
and, by default, coupled channels for actinides (RIPL OMP 2408).

Stages a1, a2 and b have landed: `formfactor` + `coupling` + `solver` + `incident` are the
coupled-channels **incident** channel for every reference target TALYS runs that way -- the eleven
symmetric-rotational ones (the five actinides, the five deformed rare earths and Au197) and Ca040,
the one harmonic-vibrational one -- at **every** incident energy, across `soswitch`, where ECIS
deforms the spin-orbit potential too (`lo(13) = T`). See `docs/results/hf-ecis-port.md`.

Stage b has landed too: `dwba` + `weakcore` + `formfactor.derivative_form_factor` are
`directecis.f90`'s one-phonon DWBA, which is where T12's `xsdirdisc` and `xsgrcoll` come from.
A-direct passes on all 24 reference targets.

`ecis.bridge` is no longer needed for any incident channel or any row of `directE*.out` at TALYS's
defaults. What is still unported is unreachable there: the asymmetric rotor (`colltype A`, which no
reference target has), `flagrot y` (false by default, so the emission-grid transmission coefficients
are spherical and come from T5) and the deformed Coulomb potential (neutrons only, so `lo(11)` is
never set).

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T13 (physics/hf/CONTRACT.md §7). Acceptance test: A-trans (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    ecist.f:1 (ecist)
    ecisinput.f90:1 (ecisinput)
    ecisdwbamac.f90:1 (ecisdwbamac)
    eciscompound.f90:1 (eciscompound)
    incidentecis.f90:1 (incidentecis)
    inverseecis.f90:1 (inverseecis)
    directecis.f90:1 (directecis)
    dwbaecis.f90:1 (dwbaecis)

"""

from __future__ import annotations
