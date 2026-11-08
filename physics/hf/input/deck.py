"""KWCOV B2: a TALYS input deck (`talys.inp`) as an engine run.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T3 (physics/hf/CONTRACT.md §7). Acceptance test: KWCOV-B2 (tests/hf/test_kwcov_b2.py).

TALYS routines ported here (file:line of the subroutine statement):
    readinput.f90:1 (readinput)     lines lowercased (`convert`), comments (`#` first) and blank lines dropped
    input_main.f90:1 (input_main)   the four main keywords: projectile, element, mass, energy (+ estop)

The four main keywords become the run's arguments (target, projectile, incident energies); every other line
is a deck line and goes to the engine the way every deck line does, through `INCOGNITA_TALYS_FIT_LINES`
(`input.fitlib`'s `lines` arm). `energy` takes TALYS's three forms (`input.energies.read_energies`).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from physics.hf.input.energies import read_energies

MAIN = ("projectile", "element", "mass", "energy")


@dataclass(frozen=True)
class Deck:
    projectile: str
    Z: int
    A: int
    declared_mev: tuple[float, ...]   # the run's grid (enincmax comes from it)
    energies_mev: tuple[float, ...]   # the energies computed (estop cut)
    lines: tuple[str, ...]            # every other keyword line, lowercased

    @property
    def lines_env(self) -> str:
        """The deck lines as the engine reads them (`INCOGNITA_TALYS_FIT_LINES`)."""
        return ";".join(self.lines)


def read_deck(text: str, cwd: str | os.PathLike = ".") -> Deck:
    """Parse a talys.inp. `cwd` is where an `energy <file>` is looked up (TALYS's working directory).

    TALYS: readinput.f90:1 (readinput), input_main.f90:1 (input_main)
    Test: tests/hf/test_kwcov_b2.py
    """
    from physics.hf.core.constants import nuclide_symbol

    proj = elem = None
    mass = None
    energy = None
    estop = 1000.0
    rest: list[str] = []
    for raw in text.splitlines():
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        w = s.split()
        k = w[0].lower()
        if k == "projectile":
            proj = w[1].lower()
        elif k == "element":
            elem = w[1]
        elif k == "mass":
            mass = int(w[1])
        elif k == "energy":
            energy = w[1:]
        else:
            if k == "estop":
                estop = float(w[1])
            rest.append(s.lower() if k not in ("bestfile",) else " ".join([k] + w[1:]))
    for k, v in (("projectile", proj), ("element", elem), ("mass", mass), ("energy", energy)):
        if v is None:
            raise ValueError(f"TALYS-error: {k} must be given")
    if mass == 0:
        raise NotImplementedError("mass 0 (natural element, natural.f90) is not ported")
    if elem.isdigit():
        Z = int(elem)
    else:
        Z = next((z for z in range(1, 125) if nuclide_symbol(z).lower() == elem.lower()), 0)
        if not Z:
            raise ValueError(f"element {elem!r} not known")
    declared, kept = read_energies(energy, estop, cwd)
    return Deck(proj, Z, int(mass), declared, kept, tuple(rest))


def run_deck(path: str | os.PathLike, stats: dict | None = None):
    """Run a talys.inp through the engine's C driver: `engine_c.run(ChainedFull(...))` with the deck lines
    in `INCOGNITA_TALYS_FIT_LINES` (restored afterwards). The run's projectile must be the engine's
    (`physics.hf.projectile`, neutron unless INCOGNITA_CPINC says otherwise).

    TALYS: talysreaction.f90:1 (talysreaction) -- the run the deck asks for
    Test: tests/hf/test_kwcov_b2.py
    """
    import torch

    from physics.hf import engine_c, projectile
    from physics.hf.engine import ChainedFull
    from physics.hf.input import fitlib

    p = Path(path)
    d = read_deck(p.read_text(errors="replace"), p.parent)
    if d.projectile != projectile.symbol():
        raise ValueError(f"deck projectile {d.projectile!r}, engine projectile {projectile.symbol()!r} "
                         "(set INCOGNITA_CPINC for charged particles / photons)")
    old = os.environ.get(fitlib.ENV_LINES)
    try:
        if d.lines:
            os.environ[fitlib.ENV_LINES] = d.lines_env
        else:
            os.environ.pop(fitlib.ENV_LINES, None)
        with torch.inference_mode():
            return engine_c.run(ChainedFull(Z=d.Z, A=d.A, declared_energies=d.declared_mev,
                                            energies=None if d.energies_mev == d.declared_mev else d.energies_mev),
                                stats)
    finally:
        if old is None:
            os.environ.pop(fitlib.ENV_LINES, None)
        else:
            os.environ[fitlib.ENV_LINES] = old
