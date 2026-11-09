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
            if k in ("levelfile", "deformfile") and len(w) == 3 and not os.path.isabs(w[2]):
                w = w[:2] + [str(Path(cwd) / w[2])]  # KWCOV B5: TALYS opens it in its working directory
            rest.append(s.lower() if k not in ("bestfile", "levelfile", "deformfile") else " ".join([k] + w[1:]))
    for k, v in (("projectile", proj), ("element", elem), ("mass", mass), ("energy", energy)):
        if v is None:
            raise ValueError(f"TALYS-error: {k} must be given")
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

    KWCOV B10b: `mass 0` runs every isotope and returns the abundance-weighted sums (`Results.natural`), `integral y`
    adds `Results.integral`, `resonance y` is refused.

    TALYS: talysreaction.f90:1 (talysreaction) -- the run the deck asks for
    Test: tests/hf/test_kwcov_b2.py, tests/hf/test_kwcov_b10b.py
    """
    from physics.hf import projectile
    from physics.hf.input import fitlib

    p = Path(path)
    d = read_deck(p.read_text(errors="replace"), p.parent)
    if d.projectile != projectile.symbol():
        raise ValueError(f"deck projectile {d.projectile!r}, engine projectile {projectile.symbol()!r} "
                         "(set INCOGNITA_CPINC for charged particles / photons)")
    from physics.hf import integral as integ_mod

    if any(ln.split()[:1] == ["resonance"] and ln.split()[1:2] and ln.split()[1][:1] == "y" for ln in d.lines):
        raise NotImplementedError(fitlib.RESONANCE_REFUSAL)  # KWCOV B10b: refused before any run
    integ = integ_mod.parse_deck(d.lines)  # KWCOV B10b: integral y / integral <file> <spectrum> <value>
    if d.A == 0:  # KWCOV B10b: natural element (natural.f90)
        lt = [ln.split()[1] for ln in d.lines if ln.split()[:1] == ["ltarget"] and len(ln.split()) > 1]
        if lt and int(lt[-1]) > 0:  # KWCOV GAP (isomeric targets): checkvalue.f90:429-432
            raise ValueError("TALYS-error: Excited level for target not possible for natural targets")
        return _run_natural(d, p.parent, stats, integ)
    res = _run_one(d, d.A, stats, chanobs=integ is not None)
    if integ is not None:
        from dataclasses import replace

        res = replace(res, integral=integ_mod.integral_table(res, d.Z, d.A, integ["triples"]))
    return res


def _run_natural(d: Deck, cwd: Path, stats, integ):
    """mass 0: every isotope of the abundance file with the same deck, then the weighted sums (natural.f90).

    TALYS: input_main.f90:197-205, abundance.f90:1 (abundance), natural.f90:1 (natural)
    Test: tests/hf/test_kwcov_b10b.py
    """
    from physics.hf import natural

    bad = [k for k in ("astro", "astroe", "astrot", "urr", "integral")
           if any(ln.split()[:1] == [k] and ln.split()[1:2] != ["n"] for ln in d.lines)]
    if bad or integ is not None:
        raise NotImplementedError(f"not ported: mass 0 with {', '.join(sorted(set(bad)))} (natural.f90 sums no "
                                  "astro / urr / integral file; TALYS leaves the last isotope's)")
    abf = None
    for ln in d.lines:
        w = ln.split()
        if w[:1] == ["abundance"] and len(w) > 1:
            abf = w[1] if os.path.isabs(w[1]) else str(cwd / w[1])
    ab = natural.abundances(d.Z, abf)
    lw = [ln.split()[:2] for ln in d.lines]
    if ["massdis", "y"] in lw and ["fission", "n"] not in lw and any(a > 215 for a in ab):  # flagfission: A > 215
        raise ValueError("TALYS-error: Fission yield calculation not possible for natural targets "
                         "(checkvalue.f90:1075; KWCOV B14)")
    runs = {a: _run_one(d, a, stats) for a in ab}
    return natural.combine(runs, ab)


def _run_one(d: Deck, A: int, stats, chanobs: bool = False):
    """One engine run of the deck on target (d.Z, A)."""
    import torch

    from physics.hf import engine_c
    from physics.hf.engine import ChainedFull
    from physics.hf.input import fitlib

    ast = astro_of(d.lines)
    old = os.environ.get(fitlib.ENV_LINES)
    old_ch = os.environ.get("INCOGNITA_CHANOBS")
    try:
        if chanobs:
            os.environ["INCOGNITA_CHANOBS"] = "1"  # KWCOV B10b integral: the isomer files (xsNNNNNN.Lnn), output only
        if d.lines:
            os.environ[fitlib.ENV_LINES] = d.lines_env
        else:
            os.environ.pop(fitlib.ENV_LINES, None)
        declared, energies = d.declared_mev, (None if d.energies_mev == d.declared_mev else d.energies_mev)
        if ast is not None:  # KWCOV B9: egridastro.f90 replaces the deck's energies
            declared, energies = _astro_energies(d, ast)
            if ast["astroex"]:
                os.environ["INCOGNITA_CHANOBS"] = "1"  # the isomer populations (xsNNNNNN.LMM) astroex folds
        with torch.inference_mode():
            res = engine_c.run(ChainedFull(Z=d.Z, A=A, declared_energies=declared, energies=energies), stats)
        if ast is not None:
            res = _astro_results(res, d, ast)
        return res
    finally:
        if old is None:
            os.environ.pop(fitlib.ENV_LINES, None)
        else:
            os.environ[fitlib.ENV_LINES] = old
        if old_ch is None:
            os.environ.pop("INCOGNITA_CHANOBS", None)
        else:
            os.environ["INCOGNITA_CHANOBS"] = old_ch


def astro_of(lines) -> dict | None:
    """The astro keywords of a deck (input_main.f90:158-159, input_astro.f90:79-110), None without `astro y`,
    `astroE` or `astroT`. Ranges and the astroE/astroT exclusion: checkvalue.f90:425-495.

    TALYS: input_astro.f90:1 (input_astro), checkvalue.f90:1 (checkvalue)
    Test: tests/hf/test_kwcov_b9.py
    """
    from physics.hf.astro.rates import check_astro_input

    a = dict(astro=False, astrogs=False, astroex=False, nonthermlev=-1, astroE=0.0, astroT9=0.0, segment=1,
             racap=False)
    for s in lines:
        w = s.split()
        k, v = w[0].lower(), (w[1].lower() if len(w) > 1 else "")
        if k == "astro":
            a["astro"] = v[:1] == "y"
        elif k in ("astrogs", "astroex", "racap"):
            a[k] = v[:1] == "y"
        elif k == "nonthermlev":
            a["nonthermlev"] = int(v)
        elif k == "astroe":
            a["astroE"], a["astro"], a["astrogs"] = float(v), True, True
        elif k == "astrot":
            a["astroT9"], a["astro"] = float(v), True
        elif k == "segment":
            a["segment"] = int(v)
    if not a["astro"]:
        return None
    if a["racap"]:
        raise NotImplementedError("not ported: astro y with racap y (stellarrate.f90's separate direct-capture rate, "
                                  "iloop 3, and its astrorate column)")
    a["astroE"], a["astroT9"] = check_astro_input(a["astroE"], a["astroT9"], a["segment"])
    a["nTmax"] = 1 if a["astroT9"] != 0.0 else 30
    return a


def _astro_energies(d: Deck, ast: dict):
    """egridastro.f90's incident grid for this target (masses of the run), cut at estop like any grid.

    TALYS: egridastro.f90:1 (egridastro)
    Test: tests/hf/test_kwcov_b9.py
    """
    from physics.hf import projectile
    from physics.hf.astro.rates import energy_grid
    from physics.hf.compound.dens_reference import structure_of

    from physics.hf.input import fitlib

    k0 = projectile.k0()
    fitlib.activate(d.Z, d.A)  # the deck's cards first: structure_of caches the run's options per target
    _, _, m = structure_of(d.Z, d.A)
    pz, pn = (0, 0, 1, 1, 1, 2, 2)[k0], (0, 1, 0, 1, 2, 1, 2)[k0]
    e = energy_grid(k0, float(m.specmass[pz, pn, k0]), float(m.redumass_amu[pz, pn, k0]),
                    {t: float(m.s_mev[0, 0, t]) for t in range(7)}, d.Z, ast["astroT9"], ast["nTmax"])
    declared = tuple(float(x) for x in e)
    estop = next((float(s.split()[1]) for s in d.lines if s.split()[0] == "estop"), 1000.0)
    kept = tuple(x for x in declared if x <= estop)
    return declared, (None if kept == declared else kept)


def _astro_results(res, d: Deck, ast: dict):
    """Results + astroout.f90's files (`Results.astro`), from the run's residual production.

    TALYS: stellarrate.f90:1 (stellarrate), astroout.f90:1 (astroout), residual.f90:76-82 (xsastro)
    Test: tests/hf/test_kwcov_b9.py
    """
    from dataclasses import replace

    import numpy as np

    from physics.hf import projectile
    from physics.hf.astro import rates as R
    from physics.hf.astro import thermal
    from physics.hf.emission.chanobs import residual_of

    k0 = projectile.k0()
    Zcn, Acn = d.Z + R.PARZ[k0], d.A + R.PARZ[k0] + R.PARN[k0]
    e = res.e_inc_mev.detach().numpy().astype(np.float64)
    rp = {}
    for zc in range(R.NUMZASTRO + 1):
        for nc in range(R.NUMNASTRO + 1):
            key = f"rp{Zcn - zc:03d}{Acn - zc - nc:03d}"
            if key in res.residual_production_mb:
                rp[(zc, nc)] = res.residual_production_mb[key].detach().numpy().astype(np.float64)
    iso = {}
    if ast["astroex"]:
        for k, v in res.extras.items():
            if not (k.startswith("xs") and ".L" in k) or ":" in k:
                continue
            code, lev = k[2:8], int(k.split(".L")[1])
            z, a = residual_of(int(code), Zcn, Acn)
            kk = (Zcn - z, (Acn - a) - (Zcn - z), lev)
            iso[kk] = iso.get(kk, 0.0) + v.detach().numpy().astype(np.float64)
    fis = res.totals_mb.get("fission")
    st = R.STATE
    t9, et9 = R.t9_grid(ast["astroT9"], ast["nTmax"])
    out = R.astro_outputs(
        Z=d.Z, A=d.A, k0=k0, e_lab=e, rp_mb=rp, fis_mb=None if fis is None else fis.detach().numpy(),
        specmass=st["masses"]["specmass"], redumass=st["masses"]["redumass"], t9=t9, et9=et9,
        partf=st["partf"], astrogs=ast["astrogs"], iso_mb=iso, flagastroex=ast["astroex"], astroE=ast["astroE"],
        macs_exp=R.macs_experimental(d.Z, d.A), flagfission=bool(fis is not None and float(fis.abs().sum()) > 0))
    out["_meta"].update(thermal=list(thermal.LOG), nonthermlev=ast["nonthermlev"])
    thermal.LOG.clear()
    return replace(res, astro=out)
