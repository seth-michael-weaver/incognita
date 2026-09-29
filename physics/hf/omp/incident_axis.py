"""SETB: the spherical incident channel of a run solved once for its whole declared energy grid,
instead of one `incident_channel` call per energy.

`incident_channel` already takes a batch of cases: `omp_parameters` and `solve_spherical` run on an
energy axis, the radial loop and the Coulomb recurrences once for all of them. The one
cross-energy quantity is `njmax` (incidentecis.f90), which `incident_channel` takes from the
batch's highest energy; energies are therefore grouped by their own `njmax`, so every energy is
solved with the l range its one-energy call uses (on CHART1's 20-point grid below 20 MeV that is
one group, `njmax = 20`, for every target).

Not differentiable by design: `Cascade.incident` takes this path only with autograd off (a chart
sweep's inference mode). tests/hf/test_setb.py holds every field to the per-energy call.

TALYS: incident.f90:1 (incident), incidentecis.f90:1 (incidentecis)
Test: tests/hf/test_setb.py
"""

from __future__ import annotations

import math

import torch

from physics.hf.core.tensors import DTYPE

__all__ = ["incident_axis", "njmax_incident_spherical"]


def njmax_incident_spherical(A: int, particle: int, e_mev: float) -> int:
    """`incident_channel`'s `njmax` for one energy (incidentecis.f90)."""
    from physics.hf.core.constants import talys_constants
    from physics.hf.omp.schrodinger import PARMASS_AMU

    x = 2.4 * 1.25 * A ** (1.0 / 3.0) * 0.22 * math.sqrt(PARMASS_AMU[particle] * e_mev)
    nj = max(20, int(x))
    return min(nj, int(talys_constants()["numl"]))


def incident_axis(Zt: int, At: int, energies: tuple[float, ...], options, params,
                  particle: int = 1) -> dict[float, object]:
    """`{e: incident_channel(one case at e)}` for every energy, solved in one batch per `njmax`.

    TALYS: incident.f90:1 (incident)
    Test: tests/hf/test_setb.py
    """
    from dataclasses import fields

    from physics.hf.core.constants import PARTICLE_INDEX
    from physics.hf.core.tensors import CaseBatch
    from physics.hf.omp.incident import IncidentChannel, incident_channel

    proj = next(k for k, v in PARTICLE_INDEX.items() if v == particle)
    groups: dict[int, list[float]] = {}
    for e in energies:
        groups.setdefault(njmax_incident_spherical(At, particle, float(e)), []).append(float(e))
    out: dict[float, object] = {}
    for es in groups.values():
        n = len(es)
        cases = CaseBatch(Z=torch.full((n,), Zt), A=torch.full((n,), At),
                          e_inc_mev=torch.tensor(es, dtype=DTYPE), projectile=proj)
        inc = incident_channel(cases, options, params)
        for i, e in enumerate(es):
            kw = {}
            for f in fields(IncidentChannel):
                v = getattr(inc, f.name)
                kw[f.name] = None if v is None else v[i:i + 1].clone()
            out[e] = IncidentChannel(**kw)
    return out
