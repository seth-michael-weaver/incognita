"""KWCOV B10b: natural-element targets (`mass 0`): one run per isotope, abundance-weighted sums (natural.f90).

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

`mass 0` makes TALYS read structure/abundance/<El>.abun (or the deck's `abundance <file>`), normalise the abundances
to 1, run every isotope with the same deck and energy grid, and write each output file of the element as the row-by-row
abundance-weighted sum of the isotopes' files (a file an isotope does not have counts 0). Here the sum is taken over
the `Results` arrays of the isotope runs: channels, discrete levels, residual production (keyed by the residual, so
the union over isotopes), totals, CHANOBS extras, the thermal rows of B10b; ratios (`:branch`) and LOWEPOT's weight
are not summed (TALYS has no natural file for them). Spectra / DDX are not summed (natural.f90 interpolates every
isotope's spectrum onto one energy list); they stay per isotope in `Results.natural["isotopes"]`.

TALYS routines ported here (file:line of the subroutine statement):
    abundance.f90:1 (abundance)    the abundance file ('(4x, i4, f11.6)', percent), normalised to 1
    natural.f90:1 (natural)        the isotope loop and the weighted sums
Task: T10 (physics/hf/CONTRACT.md section 7; KWCOV batch B10b). Acceptance test: KWCOV-B10b
(tests/hf/test_kwcov_b10b.py, docs/hf/COVERAGE_PLAN.md).
"""

from __future__ import annotations

import os
from dataclasses import replace
from pathlib import Path

import numpy as np

__all__ = ["abundances", "combine"]

#: Results fields natural.f90 sums (dicts of per-energy arrays)
SUMMED = ("channels_mb", "levels_mb", "residual_production_mb", "totals_mb", "extras")


def abundances(Z: int, abfile: str | os.PathLike | None = None) -> dict[int, float]:
    """{A: abundance fraction} as abundance.f90 leaves them (normalised to a sum of 1, file order).

    TALYS: abundance.f90:1 (abundance)
    Test: tests/hf/test_kwcov_b10b.py
    """
    from physics.hf.core.constants import nuclide_symbol
    from physics.hf.structure.files import talys_structure_dir

    if abfile is None:
        p = talys_structure_dir() / "abundance" / f"{nuclide_symbol(Z).capitalize()}.abun"
        if not p.is_file():
            raise ValueError("TALYS-error: No natural isotopes for this element, the mass keyword must be different "
                             "from 0")
    else:
        p = Path(abfile)
        if not p.is_file():
            raise ValueError(f"TALYS-error: abundance file {p} not found")
    out: dict[int, float] = {}
    for line in p.read_text(errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            a, ab = int(line[4:8]), float(line[8:19])
        except ValueError as e:
            raise ValueError(f"TALYS-error: read error in {p}: {line!r}") from e
        out[a] = out.get(a, 0.0) + 0.01 * ab
    tot = sum(out.values())
    return {a: v / tot for a, v in out.items()}


def _skip(key: str) -> bool:
    return key.endswith(":branch") or key.startswith("lowepot_")


def combine(runs: dict[int, object], abun: dict[int, float]):
    """The element's Results: the first isotope's Results with every summed field replaced by the weighted sum over
    isotopes (union of keys, missing = 0), `natural` = {"abundance", "isotopes"}. Every isotope must have the same
    incident energies (TALYS runs them on one grid).

    TALYS: natural.f90:1 (natural)
    Test: tests/hf/test_kwcov_b10b.py
    """
    import torch

    iso = list(runs)
    first = runs[iso[0]]
    e0 = first.e_inc_mev.detach().cpu().numpy()
    for a in iso[1:]:
        if not np.array_equal(runs[a].e_inc_mev.detach().cpu().numpy(), e0):
            raise ValueError(f"natural target: isotope A={a} ran on other energies than A={iso[0]}")
    new: dict = {}
    for part in SUMMED:
        keys = sorted({k for a in iso for k in getattr(runs[a], part, {}) if not _skip(k)})
        d = {}
        for k in keys:
            acc = None
            for a in iso:
                v = getattr(runs[a], part, {}).get(k)
                if v is None:
                    continue
                t = (v if isinstance(v, torch.Tensor) else torch.as_tensor(v)).to(torch.float64) * abun[a]
                acc = t if acc is None else acc + t
            d[k] = acc
        new[part] = d
    th = [getattr(runs[a], "thermal", {}) for a in iso]
    if all(th) and all(np.array_equal(t["E"], th[0]["E"]) for t in th):
        keys = sorted({k for t in th for k in t if k not in ("E", "eninclow", "E1v", "eref") and not _skip(k)
                       and "therm" not in k})
        thermal = {"E": th[0]["E"], "eninclow": th[0]["eninclow"], "E1v": th[0]["E1v"], "eref": th[0]["eref"]}
        for k in keys:
            thermal[k] = sum(abun[a] * np.asarray(t.get(k, np.zeros_like(th[0]["E"]))) for a, t in zip(iso, th))
        new["thermal"] = thermal
    elif any(th):
        raise NotImplementedError("natural target: the isotopes' energies below eninclow differ (endf y resolves "
                                  "eninclow per isotope): their thermal rows cannot be summed row by row")
    return replace(first, **new, spectra={}, angular={}, urr={}, astro={}, integral={},
                   natural={"abundance": dict(abun), "isotopes": dict(runs)})
