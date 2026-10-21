"""KEVLEAK2 (Incognita extension, default OFF): `INCOGNITA_KEVLEAK2` = 1/y (both parts), `dup` or `pe` (one part).

`dup`: cascade.f90:63-72 adds every branch of a discrete level to the populations (`xspop`, `xspopex`, `xspartial`,
`xsgamdistot` all `+ intens`) but ASSIGNS the exclusive record `mcontrib(0, nex, k) = intens`, which multiple.f90:681 copies
into `feedexcl` for channels.f90. A daughter named twice in a level's branch list (115 levels in 49 nuclides of the final level
library, e.g. Hg-197 L16 -> L5 twice, La-125 L7 -> L0 twice) therefore reaches the residual production but only its LAST branch
reaches the exclusive channels: sigma_nonel exceeds the channel sum (Hg-196 keV 5.8e-4 sigma_R, Ce-125 3e-2). With the part on,
the record accumulates (`mcontrib += intens`), so the exclusive books carry what the populations carry. Populations unchanged.

`pe`: KEVLEAK's sentinel guard (exciton.kevleak_on, an earlier engine version): the projectile's continuum pre-equilibrium is zero where
its last discrete level is closed (energies.f90 nendisc = 1 sentinel under `preequilibrium y`), which held the Fe-56/Co-59/Ni-58
keV leak.

`dup2` (KEVLEAK3): `dup` plus the C engine's `cascade_only` (engine_decay.c: a nucleus whose whole population sits in its
discrete levels, e.g. Sb-108 from Sb-109(n,2n) at 14.5-15.25 MeV), which still kept the last duplicate only. `dup` stays as it
was for --reproduce.

`pe2` (KEVLEAK3): `pe` only where the sentinel flux is booked nowhere. With FLUXCLOSE C on, an incident channel whose last
level is closed (Elast(k0) <= 0, so no continuum bin) has its PE placed on its open discrete levels 1..NL (fluxclose.
place_unplaced), i.e. booked into residual production; only when no level above the target's is open (eoutdis(k0, 1) <= 0,
target in its ground state) or FLUXCLOSE C is off does the flux leave every book. `pe2` zeroes it there and only there, so
wherever `off` already books it `pe2` == `off` bit for bit.

Values: 1/y/yes/on/all = dup + pe (KEVLEAK2); 2 = dup2 + pe2 (KEVLEAK3); else a comma list of parts; 0/n = OFF.

Default (KEVLEAK3 gate candidate): `2` ON. Deck keyword `kevleak2 y|n` (an explicit keyword wins; y = `2`, n = OFF = the
previous production), else env INCOGNITA_KEVLEAK2, else `2`. The C kernels and the option-less Python sites read the resolved
value from INCOGNITA_KEVLEAK2_EFF, which `sync(options)` writes once per run (Cascade, preequilibrium, binquad_sync).

Test: tests/hf/test_kevleak2.py, tests/hf/test_kevleak3.py
"""
from __future__ import annotations

import os


DEFAULT = "2"


def resolve(options=None) -> str:
    """The run's value: explicit deck keyword `kevleak2`, else env INCOGNITA_KEVLEAK2, else DEFAULT."""
    if options is not None and hasattr(options, "is_explicit") and options.is_explicit("kevleak2"):
        k = str(getattr(options, "kevleak2", "y")).strip().lower()
        return DEFAULT if k in ("y", "yes", "1", "true", "on") else ("0" if k in ("n", "no", "0", "false", "off") else k)
    v = os.environ.get("INCOGNITA_KEVLEAK2", "").strip().lower()
    return v if v else DEFAULT


def sync(options=None) -> None:
    """Write the run's resolved value for the C kernels and the option-less Python sites."""
    os.environ["INCOGNITA_KEVLEAK2_EFF"] = resolve(options)


def on(part: str) -> bool:
    v = os.environ.get("INCOGNITA_KEVLEAK2_EFF")
    v = (v if v is not None else os.environ.get("INCOGNITA_KEVLEAK2", "")).strip().lower() or DEFAULT
    if v in ("1", "y", "yes", "on", "all"):
        return part in ("dup", "pe")
    ps = {"dup2", "pe2"} if v == "2" else {p.strip() for p in v.split(",") if p.strip()}
    if part == "dup":  # dup2 contains dup
        return "dup" in ps or "dup2" in ps
    return part in ps
