"""DWBAUNIT: flux conservation for the incident channel of a spherical target whose first-order
(DWBA) direct inelastic exceeds the reaction cross section. Default OFF (`INCOGNITA_DWBAUNIT=1`).

The defect (FIXREL3 / FIXDWBA): a target with no `deformation/<Sym>.def` block is `colltype S`,
so its collective levels go through DWBA on the spherical optical potential. `deformpar.f90:310`
gives the first 2+ of an even-A nucleus ``0.3 * 0.40 exp(-0.012 A) + 0.025 min(d, 5)`` -- the
2026-03-26 `betafactor` safety factor multiplies only the first term, so a heavy nucleus five or
more nucleons from a magic number gets beta = 0.125-0.13 -- and odd-A targets inherit it through
weak coupling. Far on the neutron-rich side the KD03 surface absorption is nearly zero
(W_D ~ 0.2-0.3 MeV below 1 MeV), and the DWBA to that one level reaches x10-x70 sigma_R
(Bk-300: 34 b against 2.7 b at 0.54 MeV). DWBA is first-order perturbation theory on the elastic
wave; it is not unitary, and once it exceeds the flux it perturbs it is outside its validity.
The compound nucleus is then left with nothing (ENGDEFECT), and (n,n') > sigma_nonel.

The rule, chart-wide, decided once per target from the target's own spherical calculation:

1. TRIGGER. Only a `colltype S` target is examined (R/V/A targets are already coupled-channels
   and unitary). On the fixed grid `TRIGGER_GRID_MEV` (the release grid, 1 keV-20 MeV, 64 log
   points) compute the direct cross sections the run would subtract from the flux
   (`xsdirdisctot + xscollconttot + xsgrcoll`, preeq.f90:108) and the spherical sigma_R. The
   target is triggered when the ratio exceeds `FRACTION` (1.0: the direct part alone takes more
   than all the flux) at any grid energy.
2. COUPLED CHANNELS (preferred). A triggered target that TALYS's own automatic rotational model
   accepts (`deformpar.f90` `autorot`: A > 150, at least 8 nucleons from every magic number, a
   ground-state band J0 + dJ (i - 1) of ground-state parity found in the level list) is solved as
   that rotor: band coupled in ECIS-type CC with the mass-table beta2/beta4 (`rotpar`), the
   incident channel (sigma_R, T_lj) from the CC solution, and the KD03 surface absorption x0.85
   (omppar.f90:267) exactly as for a `.def` rotor. For an odd-A target the weak-coupling core is
   given the same rotor treatment, so the core's systematics 2+ beta is not copied onto the
   target's levels a second time (that quadrupole strength IS the rotational band). The coupled
   solution is unitary: the direct inelastic to the band is part of sigma_R by construction.
3. CAP (fallback, labelled). A triggered target the rotor rule cannot take (near a magic number
   or no band in the level list) keeps the spherical model, and at each energy where the direct
   sum exceeds sigma_R every direct quantity (per level, collective continuum, giant resonances)
   is scaled by sigma_R / sum. This is a plain cap, not physics: it only restores
   sigma_direct <= sigma_R.

Everything here is structure-level (Python), so the C, fast and GPU engines see the same
deformation, band, OMP and direct cross sections as the Python engine.

TALYS: deformpar.f90:216-260 (autorot), deformpar.f90:301-330 (systematics), preeq.f90:108,
       omppar.f90:267, weakcoupling.f90:1
Test: scripts/fixdwba (FIXDWBA report)
"""

from __future__ import annotations

import os
from contextlib import contextmanager

import numpy as np

ENV_VAR = "INCOGNITA_DWBAUNIT"
#: trigger: direct / sigma_R above this at any grid energy
FRACTION = 1.0
#: the release grid (engine_curves.py: geomspace(1 keV, 20 MeV, 64), float32-rounded MeV)
TRIGGER_GRID_MEV: tuple[float, ...] = tuple(
    float(np.float32(e)) for e in np.geomspace(1e3, 2e7, 64) / 1e6)

_DECISION: dict[tuple[int, int], str] = {}
_RATIO: dict[tuple[int, int], float] = {}
_EVALUATING: list[bool] = [False]


def enabled() -> bool:
    """Read per call (workers set the environment after import)."""
    return os.environ.get(ENV_VAR, "0") == "1"


def target_of(options) -> tuple[int, int]:
    """(Z, A) of the run's target: the k0 residual of the initial compound."""
    from physics.hf.core.constants import talys_constants

    c = talys_constants()
    k0 = options.k0
    Z = int(options.Zinit) - int(c["parZ"][k0])
    N = int(options.Ninit) - int(c["parN"][k0])
    return Z, Z + N


@contextmanager
def _stock():
    """Stock structure, and the run's lent cascades hidden: the evaluation must not memoise its
    spherical answers (`Cascade._coupled_band`) on the cascade the run itself will use."""
    from physics.hf.preeq import chain

    lent = dict(chain._LENT)
    chain._LENT.clear()
    _EVALUATING[0] = True
    try:
        yield
    finally:
        _EVALUATING[0] = False
        chain._LENT.clear()
        chain._LENT.update(lent)


def evaluating() -> bool:
    return _EVALUATING[0]


def _direct_ratio(Z: int, A: int) -> float:
    """max over TRIGGER_GRID_MEV of (xsdirdisctot + xscollconttot + sum xsgrcoll) / sigma_R,
    spherical target, stock structure."""
    from physics.hf.preeq.chain import chained_direct, incident_reaction_xs

    e = TRIGGER_GRID_MEV
    reac = incident_reaction_xs(Z, A, e)
    dirs = chained_direct(Z, A, e)
    best = 0.0
    for x in e:
        k = round(float(x), 6)
        d, _g = dirs[k]
        s = (float(d.xsdirdisctot_mb) + float(d.xscollconttot_mb) + float(d.xsgrcoll_mb.sum()))
        r = float(reac[k])
        if s <= 0.0:
            continue
        best = max(best, s / r if r > 0.0 else float("inf"))
    return best


def decision(Z: int, A: int) -> str:
    """'' (untouched), 'R' (rotor CC) or 'CAP' (fallback) for target (Z, A). Cached per process.

    Evaluated with the stock structure; every per-target cache it filled is dropped afterwards
    so the run itself is built from scratch on the decided model.
    """
    key = (int(Z), int(A))
    if key in _DECISION:
        return _DECISION[key]
    if _EVALUATING[0]:
        return ""
    from physics.hf import stagedisk
    from physics.hf.input.defaults import default_options

    o = default_options(*key)
    if not stagedisk.enabled():
        out, ratio = _evaluate(key, o)
    else:
        # STAGECACHE: the decision and its ratio from disk when the target's optical-model,
        # level and deformation inputs were seen before; a hit evaluates nothing, so it has no
        # evaluation caches to drop
        from physics.hf.compound.dens_reference import _structure_of

        so, sp, sm = _structure_of(*key)
        out, ratio = stagedisk.cached("dwbaunit", key, lambda: _evaluate(key, o),
                                      options=(o, so), params=(sp,), values=(sm,))
    _RATIO[key] = ratio
    _DECISION[key] = out
    return out


def _evaluate(key: tuple[int, int], o) -> tuple[str, float]:
    """`decision`'s stock evaluation: (decision, trigger ratio); every per-target cache it
    filled is dropped afterwards."""
    from physics.hf import chartrun
    from physics.hf.omp.parameters import _colltype

    out = ""
    with _stock():
        if _colltype(key[0], key[1], o) == "S" and not o.flagspher:
            ratio = _direct_ratio(*key)
            if ratio > FRACTION:
                out = "R" if _rotor_accepts(key[0], key[1], o) else "CAP"
        else:
            ratio = float("nan")
    chartrun.drop_target_caches()
    return out, float(ratio)


def state(Z: int, A: int) -> tuple:
    """STAGECACHE key part: (switch on, inside the stock evaluation, the decision for (Z, A)).
    Every optical-model / direct stage of the run's target depends on it (the rotor colltype and
    W_D, the autorot deformation, the cap); the stock evaluation's own calls see ''."""
    on = enabled()
    ev = bool(_EVALUATING[0])
    return (on, ev, decision(Z, A) if on and not ev else None)


def _rotor_accepts(Z: int, A: int, o) -> bool:
    from physics.hf.structure.deformation import deformation
    from physics.hf.structure.levels import discrete_levels
    from physics.hf.structure.masses import masses as get_masses

    ms = get_masses(o)
    return deformation(Z, A, o, discrete_levels(Z, A, o, ms), ms,
                       flagautorot=True).colltype == "R"


def info(Z: int, A: int) -> dict:
    """The decision and the trigger ratio, for run records."""
    return {"decision": _DECISION.get((int(Z), int(A))), "ratio": _RATIO.get((int(Z), int(A)))}


def autorot_for(Z: int, A: int, options) -> bool | None:
    """`flagautorot` override for `deformation(Z, A, options, ...)`: True for the run's target
    when it is decided 'R', else None (no override)."""
    if not enabled() or _EVALUATING[0]:
        return None
    t = target_of(options)
    if (int(Z), int(A)) != t:
        return None
    return True if decision(*t) == "R" else None


def core_autorot(options) -> bool | None:
    """`flagautorot` for the weak-coupling core of an odd-A target decided 'R'."""
    if not enabled() or _EVALUATING[0]:
        return None
    return True if decision(*target_of(options)) == "R" else None


def colltype_override(Z: int, A: int, options) -> str | None:
    """'R' for the run's target decided 'R' (the OMP's `.def` colltype), else None."""
    if not enabled() or _EVALUATING[0]:
        return None
    t = target_of(options)
    if (int(Z), int(A)) != t:
        return None
    return "R" if decision(*t) == "R" else None


def cap_direct(res, Z: int, A: int, e_inc_mev: float):
    """The fallback: every direct quantity of `res` scaled by sigma_R / sum where the sum of
    `xsdirdisctot + xscollconttot + xsgrcoll` exceeds the spherical sigma_R. `res` unchanged
    otherwise (and when the switch is off or the target is not decided 'CAP')."""
    if not enabled() or _EVALUATING[0] or decision(Z, A) != "CAP":
        return res
    import dataclasses

    from physics.hf.preeq.chain import _incident_cascade

    e = float(e_inc_mev)
    # `Cascade.incident` does not read the cascade's own grid: one cascade serves every energy
    r = float(_incident_cascade(int(Z), int(A), TRIGGER_GRID_MEV).incident(e).sigma_reac_mb[0])
    s = (float(res.xsdirdisctot_mb) + float(res.xscollconttot_mb) + float(res.xsgrcoll_mb.sum()))
    if s <= r or s <= 0.0:
        return res
    f = r / s
    names = ("xsdirdisc_mb", "xsdirdisctot_mb", "xscollconttot_mb", "xsgrcoll_mb", "xsgrtot_mb",
             "xsgrsum_mb", "xsgrstate_mb", "xscollcont_mb", "xscollcontjp_mb", "xsgr_mb")
    return dataclasses.replace(res, **{n: getattr(res, n) * f for n in names})


__all__ = ["ENV_VAR", "FRACTION", "TRIGGER_GRID_MEV", "autorot_for", "cap_direct",
           "colltype_override", "core_autorot", "decision", "enabled", "info", "target_of"]
