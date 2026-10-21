"""FLUXCLOSE parts A and C (FLUXPROMO / FLUXPROMO2): two flux-book leaks of the stock TALYS bookkeeping (ENGAUDIT
cause C12), default ON.

* **A -- residual window.** nuclides.f90:140-141 caps the cascade at `maxZ = Zinit - 3`, `maxN = Ninit - 3`. The
  compound decay widths still include every particle exit, so a light target's flux into a residual past the cap
  (O-11 at 1 MeV: alpha and triton exits of O-12* to C-8 / N-10, 528 of 1,248 mb; Be-9: every alpha-ejectile channel
  and rp002006, He-6) leaves the nucleus and lands nowhere. Part A lowers the cap to `Zinit - 1`, `Ninit - 1`
  (`input.defaults`); the nuclei past the stock cap are terminal residuals (TALYS `skipCN`: booked whole, every bin to
  the ground state for the channels, never decayed); `numZ - 2` / `numN - 2` still apply.
* **C -- binary exit without a continuum.** population.f90:274 renormalises a binary exit's pre-equilibrium +
  giant-resonance column only if it is non-zero; where the exit has no continuum bin (Nlast = maxex: the residual's
  discrete levels reach every excitation the exit can feed, Pd-93 at 7.79 MeV, Be-9 alpha/He-5 exits at 17-20 MeV)
  `xscheck = 0`, `norm = 1`, and `xspreeqtot + xsgrtot` is taken from the compound flux but placed nowhere. Part C
  adds it to the exit's direct-discrete feeding, in equal shares over its levels 1..NL (the target's own level
  excluded on the incident channel; the ground state of an outgoing exit with no excited level) --
  compound.f90:404-419's convention for flux with nowhere else to go -- so it gamma-decays through the levels.
  Ported from the FLUXCLOSE branch unchanged.

Switch: deck keyword `fluxclose cn|y|n` (default cn = parts A, C and N; y = A and C; n = the stock bookkeeping,
production bit for bit). `INCOGNITA_FLUXCLOSE` overrides the keyword: `0` / `n` / `off` = stock, `1` / `y` / `all` /
`on` = A and C, `cn` = A, C and N, or a comma list of the parts `A`, `C`, `N` (`A` alone = the FLUXPROMO candidate
6a7598acd). Part B (dead-end discrete levels) is not in this engine; naming it is an error, not a silent no-op.

* **N -- capture-neutral sentinel (FLUXCN).** KEVLEAK3's `pe2` zeroes the incident channel's Elast(k0) <= 0 sentinel
  pre-equilibrium (energies.f90 nendisc = 1: a continuum bin that does not exist) only where "no level above the
  ground state is open or C is off". With C on and N off (`fluxclose y`), once the target's first
  excited level opens the sentinel PE is kept: it is taken out of the compound flux, its projectile part is placed on
  the levels by C, and because the PE sum is then no longer photons-only, preeqtotal.f90:92-102 keeps the PE photons,
  which book straight into capture (Ti-47 179 keV-2.6 MeV capture +0.08..0.9 %, FLUXPROMO2's FASTGATE E harm). That
  flux is booked in production already (zeroed sentinel = compound flux), so keeping it is not a closure. Part N
  evaluates the pe2 sink as if C were off, i.e. the sentinel is zeroed as in production; A and C are unchanged
  (C still places PE/GR of exits that production books nowhere).

Switch values: `fluxclose cn` (default: A, C, N), `y` (A and C, the FLUXPROMO2 candidate), `n` (stock).
`INCOGNITA_FLUXCLOSE` also takes `cn` and part lists with `N`.

`on(part)` is run-scoped: `sync(options)` (default_options, Cascade) writes the run's resolved parts to
`INCOGNITA_FLUXCLOSE_EFF`, so option-less sites (KEVLEAK3 pe2's `on("C")` / `on("N")`, the engine binary hooks) see the
deck keyword too.

Test: tests/hf/test_fluxclose.py
"""

from __future__ import annotations

import os


PARTS = ("A", "C")  # `y`
ALL = ("A", "C", "N")  # `cn`
DEFAULT = "cn"


def _word(v, src: str) -> frozenset:
    """A keyword / env value as a part set: bool (True = y), y|n|cn, or a comma list of A, C, N."""
    if isinstance(v, bool):
        return frozenset(PARTS) if v else frozenset()
    s = str(v).strip()
    if s.lower() in ("", "0", "n", "no", "off"):
        return frozenset()
    if s.lower() in ("1", "y", "yes", "all", "on"):
        return frozenset(PARTS)
    if s.lower() == "cn":
        return frozenset(ALL)
    ps = {p.strip().upper() for p in s.split(",") if p.strip()}
    if ps - set(ALL):
        raise ValueError(f"{src}={v!r}: only parts A (residual window), C (PE+GR of an exit with no continuum bin) and N "
                         "(capture-neutral sentinel) are in this engine; part B lives on the FLUXCLOSE branch")
    return frozenset(ps)


def _env_parts() -> frozenset | None:
    """`INCOGNITA_FLUXCLOSE` as a part set, None when unset."""
    v = os.environ.get("INCOGNITA_FLUXCLOSE", "").strip()
    return None if v == "" else _word(v, "INCOGNITA_FLUXCLOSE")


def parts(keyword=DEFAULT) -> frozenset:
    """The run's parts: `INCOGNITA_FLUXCLOSE` when set, else the deck keyword `fluxclose` (y|n|cn, default cn)."""
    e = _env_parts()
    return e if e is not None else _word(keyword, "fluxclose")


def canon(ps) -> str:
    """A part set as the `INCOGNITA_FLUXCLOSE_EFF` / Options value: "A,C,N", "A,C", ..., "0" = none."""
    return ",".join(sorted(ps)) or "0"


def window_on(keyword=DEFAULT) -> bool:
    """Part A on? `keyword` = the deck's `fluxclose` value; `INCOGNITA_FLUXCLOSE`, when set, wins."""
    return "A" in parts(keyword)


def sync(options) -> None:
    """Write the run's resolved parts for the option-less sites (`options.fluxclose` = the resolved keyword)."""
    os.environ["INCOGNITA_FLUXCLOSE_EFF"] = canon(parts(getattr(options, "fluxclose", DEFAULT)))


def on(part: str) -> bool:
    """Is `part` on for this run? `INCOGNITA_FLUXCLOSE_EFF` (sync) when written, else env / default (keyword cn)."""
    v = os.environ.get("INCOGNITA_FLUXCLOSE_EFF")
    ps = (frozenset() if v.strip() in ("", "0") else frozenset(v.split(","))) if v is not None else parts(DEFAULT)
    return part.upper() in ps


def place_unplaced(b2):
    """Part C on a `BinaryInputs` about to go into `binary`: the exits whose continuum column is empty but which
    carry pre-equilibrium + giant-resonance flux get it as direct-discrete feeding. Returns the new inputs (or
    `b2` unchanged), and the amounts moved {type: mb} for the record. FLUXCLOSE branch verbatim."""
    import torch
    from dataclasses import replace

    moved = {}
    dd_new = dict(b2.xsdirdisc_mb)
    for t, g in b2.grids.items():
        nmax = int(g.maxex)
        nl = min(int(g.nlast), nmax)
        tot = float(b2.xspreeqtot_mb.get(t, 0.0)) if b2.flagpreeq else 0.0
        tot += float(b2.xsgrtot_mb.get(t, 0.0))
        if tot <= 0.0:
            continue
        pex = b2.preeqpopex_mb.get(t)
        check = float(pex[nl + 1: nmax + 1].sum()) if pex is not None and nmax > nl else 0.0
        if check != 0.0:
            continue
        dd = b2.xsdirdisc_mb.get(t)
        if dd is None:
            continue
        levels = [i for i in range(1, min(nl, dd.shape[0] - 1) + 1)
                  if not (t == b2.k0 and i == b2.ltarget)]
        if not levels:
            if t == b2.k0:
                continue  # an incident channel with no excited level: nothing inelastic to feed
            levels = [0]
        add = torch.zeros_like(dd)
        share = tot / len(levels)
        for i in levels:
            add[i] = share
        dd_new[t] = dd + add
        moved[t] = tot
    if not moved:
        return b2, moved
    return replace(b2, xsdirdisc_mb=dd_new), moved
