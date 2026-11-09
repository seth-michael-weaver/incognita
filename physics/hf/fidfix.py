"""FIDELITY1: port-fidelity fixes, ON by default since KWCOV integration (docs/hf/FIDELITY_DEFAULTS.md).

Each fix here corrects a place where the port departs from stock TALYS-2.25 on a deck TALYS accepts. They were opt-in
(default OFF) while the decision was open; Seth approved fixing port bugs in the default engine (2026-11-08), so every
fix is now ON unless switched off. The deliberate INCOGNITA defaults (NPWINDOW, EXACTFIS, CCEXITNB2, LOWEPOT, ...)
are not port bugs and are not touched here.

Switch: `INCOGNITA_FIDFIX` unset / `all` / `y` / `1` = every fix (the default); a comma list = only those fixes;
`0` / `n` / `off` / `none` = OFF (opt-out: the engine is then bit-identical to the pre-fix port, every hook asks
`on(name)` first). Being an INCOGNITA_* variable, it is part of the stage-cache key (stagedisk.ENV_PREFIXES), and the
stage cache's source hash covers this module, so entries computed before the default flip are not reused.

Default-number change of the flip (only `psfsgl` acts on default decks; ldcn / besttables / fitrisomer act only on
decks with ldmodelCN, best-file tables or fitted risomer): U-238 capture 0.5 MeV 81.32 -> 81.23 mb (-0.11 %, towards
stock 81.26 in TALYS mode), other cells of nuclei with a tabulated E1 at the ~1e-7 relative level (section 6 of
FIDELITY_DEFAULTS.md).

Fixes:
  ldcn   `ldmodelCN` belongs to the run's INITIAL compound nucleus only (input_densitymodel.f90:245-249 sets ldmodel(0,0)
         of the one run). The port builds options for pseudo-targets -- one per compound nucleus of the chained cascade
         (dens_reference._structure_of, gamma parameters, chained pre-equilibrium) -- and in each of those the chain
         nucleus is (Zix, Nix) = (0, 0), so `Options.ldmodel_of` handed it `ldmodelCN` too. With the fix, (0, 0) of an
         options set whose target is not the run's target (fitlib.active()) takes the TALYS value of that nucleus in the
         real run: its per-nucleus `ldmodel` card, else `ldmodelall`. Only decks with an explicit `ldmodelCN` that
         differs from `ldmodel` are affected (e.g. structure/best/Fe056: `ldmodel 2` + `ldmodelCN 1`).
  besttables  a table a best file names (`awdadjust n 1. awdadjust-n.table`) is looked up in the best file's own
         `tables/` directory before its `misc/tables` (fitlib, the `dirs` of ompdeck.resolve). TALYS opens the name in the
         working directory only (getvalues.f90), so the user supplies the file; the one TENDL ships next to
         best/Fe056/n-Fe056.talys is best/Fe056/tables/awdadjust-n.table (the kwcov stock harness copies it). The port
         skipped `tables/` and read best/Fe056/misc/tables/awdadjust-n.table, a different table (0.80 vs 0.81 at 5 MeV).
         Only Fe-56 has a `tables/` directory in structure/best.
  fitrisomer  a `risomer` that a fit file (`ngfit y` / `fit y` ... -> best/fits/*.par, xsfit.f90:318) gives for the
         INITIAL compound nucleus does not act, as in TALYS-2.25: structure.f90:74 reads that nucleus's levels, and
         levels.f90:313 applies Risomer to its branching ratios there, before structure.f90:80 calls xsfit. The port
         applied it (Co-59 `ngfit y`: ng.par `risomer 27 60 2.95161`, Co-60 g.s./isomer capture at 1 MeV -7.9 / +6.1 %
         against stock). Arguably a TALYS ordering bug that the port "corrected"; the fix restores stock. A `risomer` on
         the deck or in a best file (read with the input) and fitted values for other nuclei are untouched.

  psfsgl  tabulated photon strength functions (strength 3-13, the E1 table and a tabulated M1) with TALYS's
         single-precision energies: qrpa%e = ee + etable and the wtable stretch `Emid + (Eq - Emid) * wt`
         (gammapar.f90:268, :574-578) are real(sgl), so even at wt = 1 the stretch moves a table energy by a few 1e-7
         (U-239 smlo2019: 0.4 -> 0.39999962, 0.6 -> 0.60000038), and Tqrpa is the single-precision sum of 0.2 steps
         (gammapar.f90:311-321). The port did both in double (0.40000000000000036 > Tqrpa 0.4), so at a gamma energy on
         a table point that equals a Tqrpa temperature, locate and the `eb <= et` / `ee <= et` choice between the
         T-dependent column and the photoabsorption column (fstrength.f90:401-411) went the other way: U-239 f_E1 at
         0.4 / 0.6 MeV 9.08e-10 / 1.54e-9 vs stock 2.12e-9 / 1.01e-9 (psf*.E1 89 %, cross_g.tot 19.7 %, and the
         engine's photon transmission there). With the fix the port has TALYS's numbers (values straight-through, so
         the etable / wtable gradients are kept). KWCOV B15 (docs/hf/FIDELITY_DEFAULTS.md section 4).

TALYS: (none -- Incognita switch module; each fix names the TALYS lines it restores)
Test: tests/hf/test_fidfix.py
"""
from __future__ import annotations

import os

ENV = "INCOGNITA_FIDFIX"
FIXES = ("ldcn", "besttables", "fitrisomer", "psfsgl")


def on(name: str) -> bool:
    """True when fix `name` is on: every fix by default (INCOGNITA_FIDFIX unset), none with `0`/`n`/`off`/`none`,
    only the named ones with a comma list."""
    v = os.environ.get(ENV, "").strip().lower()
    if not v or v in ("1", "y", "yes", "on", "all"):
        return True
    if v in ("0", "n", "no", "off", "none"):
        return False
    return name in {x.strip() for x in v.split(",")}


def ldcn_pseudo(options) -> bool:
    """`ldcn` fix: True when `options` (with an explicit `ldmodelCN`) was built for a target that is not the run's own
    target, i.e. its compound nucleus (0, 0) is a later nucleus of the run's chain, where TALYS never applies ldmodelCN."""
    if not on("ldcn"):
        return False
    from physics.hf.input import fitlib

    c = fitlib.active()
    if c is None:
        return False
    return (int(options.Ztarget), int(options.Atarget)) != (int(c.Z), int(c.A))


def f32(x):
    """Round to IEEE single precision and back (TALYS real(sgl) arithmetic, one operation at a time).

    TALYS: gammapar.f90:1 (gammapar) -- the real(sgl) it emulates
    Test: tests/hf/test_kwcov_b15.py
    """
    import torch

    if isinstance(x, torch.Tensor):
        return x.detach().to(torch.float32).to(x.dtype if x.dtype != torch.float32 else torch.float64)
    import numpy as np

    return float(np.float32(x))


def sgl_straight(value, sgl):
    """`sgl`'s numbers with `value`'s gradient (straight-through), in `value`'s dtype.

    TALYS: (none -- autograd helper)
    Test: tests/hf/test_kwcov_b15.py
    """
    return value + (sgl.to(value.dtype) - value).detach()


def tqrpa_sgl(n_t: int, dtemp: float):
    """gammapar.f90:311-321: Tqrpa(it) = the single-precision running sum -dtemp + it * dtemp, as float64.

    TALYS: gammapar.f90:1 (gammapar) lines 311-321
    Test: tests/hf/test_kwcov_b15.py
    """
    import numpy as np

    out = np.zeros(n_t)
    t = np.float32(-dtemp)
    for it in range(n_t):
        t = np.float32(t + np.float32(dtemp))
        out[it] = float(t)
    return out
