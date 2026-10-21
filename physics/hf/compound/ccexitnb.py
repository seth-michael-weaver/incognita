"""CCEXITNB (Incognita extension, default OFF; deck `ccexitnb y` or env INCOGNITA_CCEXITNB=1): for a `colltype R` target
(rotor coupled channels on the incident channel) the FIRST compound nucleus's neutron exit to a discrete level of the
target that is NOT in the coupled band takes the ground-state channel's coupled-channels compound-formation T_lj
(`Cascade.incident`'s Tjlinc, SLINPUT rule included -- the same object comptarget.f90:358 puts on the elastic exit) at
that exit energy, instead of densprepare's interpolation of the spherical inverse table.

Why: the non-band (intrinsic) levels of a deformed target belong to the same deformed nucleus as its ground state, so
by reciprocity their inverse channel should be the deformed one. TALYS uses the exact CC Tjlinc only for the elastic
exit (ltarget) and a spherical solve of the target's potential for every other exit (INVCC, development notes).
INVCC swapped the WHOLE inverse table (continuum and every compound nucleus) and failed on the continuum first-neutron
spectrum ((n,2n)); this switch touches only the discrete non-band rows of the first compound nucleus.

Untouched: band levels (EWCC: their exit needs P_cc, not the g.s. T), the elastic exit, continuum bins, every later
compound nucleus, charged particles, spherical and vibrational targets, non-neutron projectiles.

Rows: the k0 residual's discrete rows i <= min(Nlast, maxex), i != Ltarget, whose energy matches no coupled-band level
(1 eV). Value: Tjlinc at the emission-grid nodes (E_lab = egrid / specmass, specmass = M_t / (M_t + m_n)), combined with
densprepare.f90:341-360's own locate + three-node Lagrange rule at Eout = Exinc - Ex(i) - S_n (below egrid(ebegin):
nen = 0, nodes 0..2 with the zero row at egrid(0), lmaxhf 0, as TALYS), cut at transeps, times Fnorm(k0), limited to
the row's l range; lmaxhf(i) = the last l with T > 0. One shared builder (`rows`) feeds every path (Python compound_inputs, C front, GPU), so they
agree by construction.

Test: tests/hf/test_ccexitnb.py
"""

from __future__ import annotations

import os

import numpy as np

ENV = "INCOGNITA_CCEXITNB"
ENV2 = "INCOGNITA_CCEXITNB2"  # CCEXITNB2: the same rows only for targets without a fission channel
BAND_TOL_MEV = 1.0e-6


def _env_on(name: str) -> bool:
    v = os.environ.get(name, "").strip().lower()
    if v in ("", "0", "n", "no", "off"):
        return False
    if v in ("1", "y", "yes", "on"):
        return True
    raise ValueError(f"{name}={v!r} (expected 1/y or 0/n)")


def enabled(options=None) -> bool:
    """Deck keyword `ccexitnb y` (Options.ccexitnb) or env INCOGNITA_CCEXITNB in (1, y, yes, on); or the CCEXITNB2 class
    rule: deck `ccexitnbnf y` (Options.ccexitnbnf) or env INCOGNITA_CCEXITNB2, which applies only when the engine opens no
    fission channel for this target (Options.flagfission False; default A <= FISLIM = 215, input_fissionmodel.f90:78-80).
    Why: in fissioning systems the barrier / fission-width parameters were set against spherical exit widths, so a
    deformed exit width there double-counts the n' vs f competition (CCEXITNB: Cm-243/244/247 fission -1.4..-4.5 %)."""
    if options is not None and bool(getattr(options, "ccexitnb", False)):
        return True
    if _env_on(ENV):
        return True
    if (options is not None and bool(getattr(options, "ccexitnbnf", False))) or _env_on(ENV2):
        return options is not None and not bool(getattr(options, "flagfission", False))
    return False


def _active(cas) -> dict | None:
    """The coupled band when the rule applies to this cascade, else None."""
    if not enabled(getattr(cas, "options", None)):
        return None
    if int(cas.k0) != 1 or getattr(cas, "omp_overrides", None) or getattr(cas, "diff_params", False):
        return None
    band = cas._coupled_band()
    if band is None or band.get("colltype") != "R":
        return None
    return band


def _specmass(cas) -> float:
    m = cas.__dict__.get("_ccx_specmass")
    if m is None:
        from physics.hf.omp.schrodinger import PARMASS_AMU, nucleus_mass_amu

        mt = nucleus_mass_amu(int(cas.Zt), int(cas.At))
        m = mt / (mt + PARMASS_AMU[1])
        cas.__dict__["_ccx_specmass"] = m
    return m


def _node_tjl(cas, nen: int) -> np.ndarray:
    """Tjlinc (updown axis, (L, 3)) at emission-grid node nen, memoised per cascade."""
    memo = cas.__dict__.setdefault("_ccx_nodes", {})
    v = memo.get(nen)
    if v is None:
        from physics.hf.compound.dens_reference import _to_updown_axis

        e_lab = float(cas.rg.egrid[nen]) / _specmass(cas)
        inc = cas.incident(e_lab)
        t = _to_updown_axis(inc.tjl_inc[0], 1)
        v = np.asarray(t.detach().numpy() if hasattr(t, "detach") else t, dtype=np.float64).copy()
        memo[nen] = v
    return v


def _lagrange(cas, eout: float) -> tuple[list[int], list[float], bool]:
    """densprepare.f90:341-352 (`prepare._locate_nen` / `_interp_nodes`): nodes (na, na+1, na+2) around Eout and the
    Lagrange weights. Below egrid(ebegin) TALYS sets nen = 0 (nodes 0, 1, 2; node 0 is the zero row at egrid(0) = 0)
    and lmaxhf = 0; `below` reports that case."""
    eg = np.asarray(cas.rg.egrid, dtype=np.float64)
    eb = int(cas.rg.ebegin[1])
    maxen = int(cas.rg.maxen)
    below = eout < float(eg[eb])
    if below:
        nen = 0
    else:
        nen = int(np.searchsorted(eg[eb: maxen + 1], eout, side="right") - 1 + eb)
        nen = min(max(nen, eb), maxen - 1)
    centred = (nen > eb + 1) or (nen >= maxen - 1)
    na = nen - 1 if centred else nen
    ns = [na, na + 1, na + 2]
    e = [float(eg[n]) for n in ns]
    w = []
    for k in range(3):
        a, b = [e[m] for m in range(3) if m != k]
        w.append((eout - a) * (eout - b) / ((e[k] - a) * (e[k] - b)))
    return ns, w, below


def rows(cas, ltarget: int, ex_mev, nlast: int, maxex: int, etot_mev: float, sep_mev: float, L: int,
         fn: float, node=None) -> dict[int, tuple[np.ndarray, int]]:
    """{row i: (T_lj row (L, 3) on the updown axis, lmax)} for the k0 = neutron residual (the target) of the first
    compound nucleus; {} when the rule does not apply. `node(nen)` replaces the CC node table (tests: the spherical
    table there must give densprepare's own rows back)."""
    band = _active(cas)
    if band is None:
        return {}
    node = node or (lambda n: _node_tjl(cas, n))
    be = np.asarray(band["e_mev"], dtype=np.float64)
    ex = np.asarray(ex_mev, dtype=np.float64)
    out = {}
    for i in range(0, min(int(nlast), int(maxex)) + 1):
        if i == int(ltarget) or i >= ex.shape[0]:
            continue
        if be.size and float(np.min(np.abs(be - ex[i]))) <= BAND_TOL_MEV:
            continue
        eout = float(etot_mev) - float(ex[i]) - float(sep_mev)
        if eout <= 0.0:
            continue
        ns, w, below = _lagrange(cas, eout)
        nodes = [node(n) if n >= int(cas.rg.ebegin[1]) else np.zeros((1, 3)) for n in ns]
        Lc = max(x.shape[0] for x in nodes)
        v = np.zeros((Lc, 3))
        for wk, x in zip(w, nodes, strict=True):
            v[: x.shape[0]] += wk * x
        v = np.where(v < cas.transeps, 0.0, v) * float(fn)
        if below:  # lmaxhf = 0 there (densprepare copies reacinitial's 0)
            v[1:] = 0.0
        row = np.zeros((int(L), 3))
        k = min(int(L), Lc)
        row[:k] = v[:k]
        nz = np.nonzero(row.max(axis=1) > 0.0)[0]
        out[i] = (row, int(nz[-1]) if nz.size else 0)
    return out


def fnorm_n(cas) -> float:
    """Fnorm(k0 = 1) of the primary decay, the factor densprepare puts on every neutron row."""
    return float(np.asarray(cas.fiso())[2])


def apply_residual(cas, r, ltarget: int, etot_mev: float, sep_mev: float):
    """Python paths: a copy of the k0 ResidualChannels `r` with the CCEXITNB rows written in (r itself when none).
    `sep_mev` = S_n of the compound nucleus (ResidualChannels.sep_mev is not filled by densprepare)."""
    from dataclasses import replace

    if r is None or r.tjl is None or not isinstance(r.tjl, np.ndarray):
        return r
    rw = rows(cas, ltarget, r.ex_mev, r.nlast, r.maxex, etot_mev, sep_mev, r.tjl.shape[1], fnorm_n(cas))
    if not rw:
        return r
    tjl = r.tjl.copy()
    lmaxhf = np.asarray(r.lmaxhf).copy()
    tl = None if r.tl is None else np.asarray(r.tl).copy()
    ll = np.arange(tjl.shape[1])
    for i, (row, lm) in rw.items():
        tjl[i] = row
        lmaxhf[i] = lm
        if tl is not None:
            tl[i, : tjl.shape[1]] = ((ll + 1) * row[:, 2] + ll * row[:, 0]) / (2 * ll + 1)
    LAST[(int(cas.Zt), int(cas.At))] = sorted(rw)
    return replace(r, tjl=tjl, lmaxhf=lmaxhf, tl=tl)


LAST: dict = {}  # diagnostics: {(Z, A): [rows replaced at the last call]}
