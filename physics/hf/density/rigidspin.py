"""RIGIDSPIN (Incognita extension, ISORATIO 2026-10-01): ground-state spin cut-off from the engine's own rigid-body moment of inertia.

Physics: in the continuum the spin cut-off of a (residual or compound) nucleus is sigma^2 = I * T / hbar^2. The rigid-body value
uses TALYS's own deformed moment `Irigid(0) = (1 + |beta2| / 3) * 0.01389 A^(5/3)` (deformpar.f90 label 400; beta2 = the mass
table's ground-state deformation) and the engine's own temperature at the neutron separation energy S of that nucleus:
    ldmodel 1-3:  T = sqrt(U / a(S)), U = S - delta   (the Fermi-gas T the spin cut-off formula itself uses)
    ldmodel >= 4: T = the table's T column at S        (BSkG3 / HFB combinatorial tables)
The engine's current sigma^2(S) is read off its own spin distribution, sigma^2 = <(J + 1/2)^2> / 2 over the level density rho(S, J)
(both parities). The switch scales each nucleus's ground-state spin cut-off by R = sigma^2_rig(S) / sigma^2_eng(S) through TALYS's
existing `s2adjust Z A R 0` keyword, so every path that already honours s2adjust (Py / C / fast / GPU; tables by the exponential
squeeze of densitytable.f90:160-195; ldmodel 1-3 through scutconst and the s2adjust-interpolated ld parameter files) carries it.
Zero new parameters; no per-nuclide input beyond the engine's own structure. Barriers (ibar > 0) are untouched.

Default OFF (env INCOGNITA_RIGIDSPIN unset / 'n'); OFF never enters this module, so OFF is bit-identical.
`chain_lines(cas)` builds the lines from a run's OFF cascade; runners append them to INCOGNITA_TALYS_FIT_LINES and rebuild the cascade.
"""

from __future__ import annotations

import math
import os

import numpy as np

ENV = "INCOGNITA_RIGIDSPIN"


def mode() -> str:
    v = os.environ.get(ENV, "n").strip().lower()
    return "y" if v in ("y", "1", "yes", "on") else "n"


def _f(x) -> float:
    return float(x.detach().reshape(-1)[0]) if hasattr(x, "detach") else float(x)


def sigma2_engine(ld, E_mev: float) -> float:
    """<(J+1/2)^2>/2 of the engine's level density rho(E, J) summed over parity (levels, not states)."""
    import torch

    from physics.hf.density.models import density
    from physics.hf.density.tables import NUMJ

    odd = (int(ld.A) % 2) == 1
    J = torch.arange(NUMJ + 1, dtype=torch.float64) + 0.5 * odd
    E = torch.tensor([[float(E_mev)]], dtype=torch.float64)
    w = torch.zeros(NUMJ + 1, dtype=torch.float64)
    for parity in (1, -1):
        w = w + density(ld, E, J.unsqueeze(0), parity, 0).reshape(-1)
    w = w.detach().numpy()
    s = w.sum()
    if not s > 0.0:
        return float("nan")
    x = J.numpy() + 0.5
    return float((w * x * x).sum() / s / 2.0)


def temperature(ld, E_mev: float) -> float:
    """The engine's own nuclear temperature at E: FG sqrt(U/a) for ldmodel <= 3, the table T column (parity-averaged) otherwise."""
    if int(ld.ldmodel) <= 3:
        from physics.hf.density.parameters import ignatyuk

        U = float(E_mev) - _f(ld.delta_mev[0])
        a = _f(ignatyuk(ld, float(E_mev), 0))
        return math.sqrt(U / a) if U > 0.0 and a > 0.0 else float("nan")
    if not ld.has_table(0):
        return float("nan")
    from physics.hf.density.models import edens_grid  # noqa: F401  (same grid the table uses)
    from physics.hf.density.tables import edens_grid as eg, nendens_of

    tab = ld.tables[0]
    n = nendens_of(int(ld.ldmodel))[0]
    e = eg()[1:n + 1].numpy()
    shift = _f(ld.ptable_mev[0])
    T = 0.5 * (tab.ldtableT_mev[1:n + 1, 0].numpy() + tab.ldtableT_mev[1:n + 1, 1].numpy())
    return float(np.interp(float(E_mev) - shift, e, T))


def ratio(ld) -> dict:
    """R = Irigid(0) T(S) / sigma^2_eng(S) for one nucleus, with its parts (for the record)."""
    S = _f(ld.S_mev)
    s2 = sigma2_engine(ld, S)
    T = temperature(ld, S)
    irig = _f(ld.Irigid[0])
    s2r = irig * T
    R = s2r / s2 if (s2 > 0.0 and s2r > 0.0 and math.isfinite(s2r)) else 1.0
    return dict(Z=int(ld.Z), A=int(ld.A), ldmodel=int(ld.ldmodel), S=S, T=T, irigid=irig, beta2=_f(ld.beta2[0]),
                sigma2_eng=s2, sigma2_rig=s2r, R=float(R))


#: the populated corner of the decay box up to 20-30 MeV (n,4n / n,2a reach Nix 5, Zix 3); nuclei beyond it keep s2adjust 1
ZIX_MAX, NIX_MAX = 3, 5


def chain_nuclei(cas) -> list[tuple[int, int]]:
    """The nuclei (Z, A) of the run's decay box with Zix <= 3 and Nix <= 5 (and inside maxZ/maxN)."""
    o = cas.options
    out = []
    for zix in range(0, min(int(getattr(o, "maxZ", 0)), ZIX_MAX) + 1):
        for nix in range(0, min(int(getattr(o, "maxN", 0)), NIX_MAX) + 1):
            Z = int(o.Zinit) - zix
            A = int(o.Zinit + o.Ninit) - zix - nix
            if Z > 0 and A > Z:
                out.append((Z, A))
    return out


def chain_lines(cas, nuclei=None) -> tuple[list[str], list[dict]]:
    """`s2adjust Z A R 0` for every nucleus of the box whose LD the cascade can build; (lines, records)."""
    lines, recs = [], []
    for Z, A in (nuclei or chain_nuclei(cas)):
        try:
            ld = cas.ld_of(Z, A)[0]
        except Exception as e:  # a nucleus outside the run's structure: leave it alone
            recs.append(dict(Z=Z, A=A, error=repr(e)[:200]))
            continue
        r = ratio(ld)
        recs.append(r)
        if r["R"] != 1.0:
            lines.append(f"s2adjust {Z} {A} {r['R']:.5f} 0")
    return lines, recs


__all__ = ["ZIX_MAX", "NIX_MAX", "ENV", "mode", "sigma2_engine", "temperature", "ratio", "chain_nuclei", "chain_lines"]
