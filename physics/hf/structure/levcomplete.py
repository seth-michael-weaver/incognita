"""Incognita extension (HFGAMMA; not TALYS): the continuum starts where the discrete level scheme stops being complete.

Env INCOGNITA_LEVCOMPLETE=1 (or `all`); `tgt` restricts the cut to the target nucleus's list (the (n,n') residual).
Default OFF, and OFF never changes a `Levels` object.

Defect: TALYS keeps levels 0..Nlast (maxlevelstar 30 for the target, nlevbin / maxlevelsres elsewhere) of the discrete
file in the decay and starts the continuum at E(Nlast) (exgrid.f90). Past the upper end of the complete scheme the files
list only the levels someone saw -- often a yrast band -- so between Umax and E(Nlast) the nucleus has a handful of
high-spin states and NO continuum. Hf-182 lists 30 levels to 3.869 MeV, complete only to 1.988 MeV (RIPL-4, 22 levels):
levels 23-30 are the 5-/4- ... 14+, 16+ yrast members. A Hf-183 compound fed by 3-4.5 MeV neutrons then finds almost no
neutron exit into Hf-182 at 2-3.9 MeV, gamma emission (T_gamma ~ 10 at 9 MeV excitation) wins 15-20 % of the flux
(B55: capture 197 mb at 3.55 MeV, gamma-fed (n,gamma X) 409 mb at 4 MeV), where the real neutron exit is open.

Rule (structure only, no fitted number, the same for every nucleus): where RIPL-4 levels/levels-param.data gives the
complete scheme's upper end Umax > 0 and E(Nlast) > Umax, the decay list is cut at Nlast = max(1, last level with
E <= Umax) (`ggdeadend.cut_index`); the continuum then starts at E(Nlast) and the level density (CT window already
anchored there by ctwindow/ctwindow2 where on) covers the incomplete region. Where RIPL-4 gives no Umax the list is
kept. Levels above the cut leave the decay list; collective ones keep their direct strength through TALYS's own
collective-continuum path (xscollcont). The level-density matching keeps the uncut list (`Levels.nlev_ld` feeds the
Ntop default), so D0 and the LD parameters are unchanged. Isomers beyond the cut are re-slotted by levels.f90's own rule.

Everything downstream (Py / C / fast / GPU chains) reads `Levels.nlev`, so the switch acts in one place.
Test: tests/hf/test_levcomplete.py
"""

from __future__ import annotations

import os

__all__ = ["ENV", "mode", "applies", "new_nlev"]

ENV = "INCOGNITA_LEVCOMPLETE"
LAST: dict = {}  # (Z, A) -> record of the last cut (diagnostics only)


def mode() -> str:
    """'' (OFF), 'all' (every nucleus) or 'tgt' (target nucleus only)."""
    v = os.environ.get(ENV, "0").strip().lower()
    if v in ("1", "y", "yes", "all"):
        return "all"
    if v in ("tgt", "t", "target"):
        return "tgt"
    return ""


def applies(is_target: bool) -> bool:
    m = mode()
    return m == "all" or (m == "tgt" and is_target)


def new_nlev(Z: int, A: int, e_mev, nlev: int) -> int:
    """The decay list length under the rule: last level <= RIPL-4 Umax when the list runs past it, else `nlev`."""
    from physics.hf.density.ctwindow import ripl_umax
    from physics.hf.structure.ggdeadend import cut_index

    _nmax, umax = ripl_umax(Z, A)
    if not umax > 0.0 or nlev < 2 or not float(e_mev[nlev]) > umax + 1e-6:
        return nlev
    return min(nlev, cut_index(Z, A, e_mev, nlev))
