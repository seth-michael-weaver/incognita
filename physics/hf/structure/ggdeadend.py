"""Incognita extension (FIXENG F14; not TALYS): no radiative dead end at the neutron-capture entry.

Env INCOGNITA_GGDEADEND=1; default OFF, and OFF never changes a `Levels` object.

Defect: TALYS keeps levels 0..Nlast of the discrete file in the decay and starts the continuum at E(Nlast). For a few
nuclei the file lists, beyond the complete part of the scheme, a high-spin (yrast) band that runs past the nucleus's
own S_n, and the level-density fill of the file starts above that. Then there is no continuum anywhere below S_n, and
the s-wave capture state (J = |I-1/2|..I+1/2, I = the (Z, A-1) ground-state spin of its level list) finds no dipole partner among the
listed levels below S_n: its gamma decay is reduced to M2/E3 transitions, <Gamma_gamma> -> 0 (Xe-141: 0 eV, Rh-106:
2.6e-7 eV, against the usual 0.01-1 eV) and keV capture collapses. A real nucleus at S_n always has dipole-connected
states below; a list that offers none is incomplete by construction.

Rule (structure only, no fitted number, the same for every nucleus): if E(Nlast) > S_n AND no level 0..Nlast with
E < S_n has |J - Ir| <= 1 (not 0 -> 0) for an s-wave entry spin J, the discrete list is cut at the complete scheme:
Nlast = max(1, last level with E <= Umax), Umax = the upper end of the complete scheme in RIPL-4
levels/levels-param.data (0 when RIPL-4 gives none), applied only when the new E(Nlast) < S_n (the cut opens a
continuum below S_n; where even the first excited level is above S_n the list is not cut). The continuum then starts
at E(Nlast). The level-density matching
keeps the uncut list (`Levels.nlev_ld` feeds the Ntop default), so D0 and the LD are unchanged.

Everything downstream (Py / C / fast / GPU chains) reads `Levels.nlev`, so the switch acts in one place.
Test: tests/hf/test_ggdeadend.py
"""

from __future__ import annotations

import os

__all__ = ["enabled", "entry_spins", "is_dead_end", "cut_index", "new_nlev"]

ENV = "INCOGNITA_GGDEADEND"
LAST: dict = {}  # (Z, A) -> record of the last cut (diagnostics only)


def enabled() -> bool:
    return os.environ.get(ENV, "0").lower() in ("1", "y", "yes")


def entry_spins(parent_spin: float) -> list[float]:
    """s-wave neutron-capture entry spins on a target of spin I."""
    I = float(parent_spin)  # noqa: E741
    return [abs(I - 0.5)] if I < 0.25 else [I - 0.5, I + 0.5]


def is_dead_end(e_mev, spin, nlev: int, sn_mev: float, parent_spin: float) -> bool:
    """True when levels 0..nlev reach past S_n and none below S_n is dipole-connected to an s-wave entry spin."""
    sn = float(sn_mev)
    if not sn > 0.0 or nlev < 1 or not float(e_mev[nlev]) > sn:
        return False
    for J in entry_spins(parent_spin):
        for i in range(nlev + 1):
            e, ir = float(e_mev[i]), float(spin[i])
            if e < sn and abs(J - ir) <= 1.0 and not (J == 0.0 and ir == 0.0):
                return False
    return True


def cut_index(Z: int, A: int, e_mev, nlev: int) -> int:
    """max(1, last level index <= nlev with E <= RIPL-4 Umax)."""
    from physics.hf.density.ctwindow import ripl_umax

    _nmax, umax = ripl_umax(Z, A)
    idx = [i for i in range(nlev + 1) if float(e_mev[i]) <= umax + 1e-6]
    return max(1, max(idx) if idx else 0)


def new_nlev(Z: int, A: int, e_mev, spin, nlev: int, sn_mev: float, parent_spin: float) -> int:
    """The decay list length under the rule: `nlev` unless a dead end that the cut opens below S_n."""
    if not is_dead_end(e_mev, spin, nlev, sn_mev, parent_spin):
        return nlev
    n = cut_index(Z, A, e_mev, nlev)
    return n if n < nlev and float(e_mev[n]) < float(sn_mev) else nlev
