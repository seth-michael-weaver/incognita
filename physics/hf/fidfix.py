"""FIDELITY1: opt-in port-fidelity fixes (default OFF; docs/hf/FIDELITY_DEFAULTS.md).

Each fix here corrects a place where the port departs from stock TALYS-2.25 on a deck TALYS accepts. They are OFF by
default because the published library and the scoring were calibrated on the engine as it is; turning one on by default
is Seth's decision (the doc estimates what would move).

Switch: `INCOGNITA_FIDFIX` = comma list of fix names, or `all` / `y` / `1` for every fix; unset / `0` / `n` = OFF (the
engine is then bit-identical to before: every hook asks `on(name)` first). Being an INCOGNITA_* variable, it is part of
the stage-cache key (stagedisk.ENV_PREFIXES).

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

TALYS: (none -- Incognita switch module; each fix names the TALYS lines it restores)
Test: tests/hf/test_fidfix.py
"""
from __future__ import annotations

import os

ENV = "INCOGNITA_FIDFIX"
FIXES = ("ldcn", "besttables", "fitrisomer")


def on(name: str) -> bool:
    """True when fix `name` is switched on in INCOGNITA_FIDFIX."""
    v = os.environ.get(ENV, "").strip().lower()
    if not v or v in ("0", "n", "no", "off"):
        return False
    if v in ("1", "y", "yes", "on", "all"):
        return True
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
