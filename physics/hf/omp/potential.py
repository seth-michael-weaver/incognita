"""Radial form factors V(r), W(r), Vso(r), Wso(r) built from OMPParameters (Woods-Saxon, derivative
WS, Thomas spin-orbit) on the radial grid ECIS integrates on.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T4 (physics/hf/CONTRACT.md §7). Acceptance test: A-omppot (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    optical.f90:1 (optical)
    radialtable.f90:1 (radialtable)
    ecisinput.f90:1 (ecisinput)
    incidentread.f90:1 (incidentread)

What omp.out holds. TALYS does not compute the radial potential itself: `ecisinput` writes the
19 parameters on fixed-format cards (f10.5, or es10.3 above 1000 MeV), ECIS builds the form
factors with reduced radii multiplied by M^(1/3), M the target mass on the card in amu (ECIS
`lect`: `am3 = wv(2,ij)**.333`, `val = am3*ro`), and `incidentread` copies ECIS's printed
potential (unit 11, `ecis.pot`) to omp.out with the radius rebuilt as `iR * step`, where `step`
is ECIS's integration step as printed with f8.5. The columns are

    V   = V f(r; rv, av) + 4 Vd g(r; rvd, avd)
    W   = W f(r; rw, aw) + 4 Wd g(r; rwd, awd)
    Vso = Vso (1/r) (-df/dr)(r; rvso, avso)
    Wso = Wso (1/r) (-df/dr)(r; rwso, awso)

with f = 1/(1+exp((r-R)/a)) and g = -a df/dr = f(1-f). The overall signs, the (hbar/m_pi c)^2
factor of the Thomas term and the Coulomb potential are ECIS's business and live in the solver
(T5, omp/schrodinger.py); this module reproduces the printed columns. The fixed-format rounding
of the card values is applied with a straight-through estimator (`ecis_card=True`), so the
forward value is what ECIS computed with and gradients are those of the unrounded parameters.

`radialtable` (JLM radial matter densities) is listed for completeness of the stub contract: the
JLM/folding potentials are out of scope (contract §8) and `jlm_radial_table` raises.

Reconstructing the true radii of omp.out needs ECIS's step before the f8.5 rounding; the dump
does not carry it, so tests fit it in the one-digit window the rounding allows (see
tests/hf/test_omp_parameters.py); it is one number for all four columns, so it is fitted once
against all four together and all four are then gated with it.

`radial_potential` is the SPHERICAL form factor, which is what ECIS prints for a `colltype S`
target and -- because the vibrational model deforms only the transition form factors -- for a
`colltype V` one too. A `colltype R` target needs `rotational_radial_potential`, ECIS's
lambda = 0 multipole of the deformed potential.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import torch
from torch import Tensor

from physics.hf.core.tensors import DTYPE

if TYPE_CHECKING:
    from physics.hf.omp.parameters import OMPParameters


_FIELDS = (
    "v_mev", "rv_fm", "av_fm", "w_mev", "rw_fm", "aw_fm", "vd_mev", "rvd_fm", "avd_fm",
    "wd_mev", "rwd_fm", "awd_fm", "vso_mev", "rvso_fm", "avso_fm", "wso_mev", "rwso_fm",
    "awso_fm", "rc_fm",
)  # fmt: skip


def _straight_through(x: Tensor, y: Tensor) -> Tensor:
    return x + (y - x).detach()


def ecis_card_value(x: Tensor) -> Tensor:
    """A potential parameter as `ecisinput` writes it: f10.5, or es10.3 when |x| >= 1000.

    TALYS: ecisinput.f90:1 (ecisinput)
    Test: A-omppot
    """
    x = torch.as_tensor(x, dtype=DTYPE)
    f10 = torch.round(x * 1.0e5) / 1.0e5
    big = x.abs() >= 1000.0
    ax = torch.where(big, x.abs(), torch.ones_like(x))
    ex = torch.floor(torch.log10(ax))
    mant = torch.round(x / 10.0**ex * 1.0e3) / 1.0e3
    es = mant * 10.0**ex
    return _straight_through(x, torch.where(big, es, f10))


def _fermi(r: Tensor, R: Tensor, a: Tensor) -> tuple[Tensor, Tensor]:
    """f = 1/(1+exp((r-R)/a)) and -df/dr = f(1-f)/a, stable for any sign of the exponent."""
    x = (r - R) / a
    f = torch.sigmoid(-x)
    return f, f * (1.0 - f) / a


def radial_potential(
    p: OMPParameters,
    a_mass: Tensor,
    r_fm: Tensor,
    *,
    ecis_card: bool = True,
) -> dict[str, Tensor]:
    """Complex central and spin-orbit potentials on r_fm (fm), MeV; compare with omp.out.

    `p` fields are shaped (...,) (one value per case/energy); `a_mass` is the target mass in amu
    as written on the ECIS card (f10.5), broadcastable to the parameter shape; `r_fm` is (R,).
    Returns the omp.out columns "V", "W", "Vso", "Wso" shaped (..., R).

    TALYS: optical.f90:1 (optical)
    Test: A-omppot
    """
    card = ecis_card_value if ecis_card else (lambda t: torch.as_tensor(t, dtype=DTYPE))
    q = {name: card(getattr(p, name)) for name in _FIELDS[:18]}
    mass = card(torch.as_tensor(a_mass, dtype=DTYPE))
    shape = torch.broadcast_shapes(q["v_mev"].shape, mass.shape)
    am3 = (mass ** (1.0 / 3.0)).expand(shape)[..., None]
    r = torch.as_tensor(r_fm, dtype=DTYPE)

    def ff(radius: str, diff: str) -> tuple[Tensor, Tensor]:
        a = q[diff].expand(shape)[..., None]
        a = torch.where(a > 0, a, torch.ones_like(a))  # zero depth pairs with zero geometry
        return _fermi(r, q[radius].expand(shape)[..., None] * am3, a)

    def depth(name: str) -> Tensor:
        return q[name].expand(shape)[..., None]

    fv, _ = ff("rv_fm", "av_fm")
    fw, _ = ff("rw_fm", "aw_fm")
    fvd, dvd = ff("rvd_fm", "avd_fm")
    fwd, dwd = ff("rwd_fm", "awd_fm")
    _, dvso = ff("rvso_fm", "avso_fm")
    _, dwso = ff("rwso_fm", "awso_fm")
    avd = q["avd_fm"].expand(shape)[..., None]
    awd = q["awd_fm"].expand(shape)[..., None]
    return {
        "V": depth("v_mev") * fv + 4.0 * depth("vd_mev") * avd * dvd,
        "W": depth("w_mev") * fw + 4.0 * depth("wd_mev") * awd * dwd,
        "Vso": depth("vso_mev") * dvso / r,
        "Wso": depth("wso_mev") * dwso / r,
    }


def rotational_radial_potential(
    p: OMPParameters,
    a_mass: Tensor,
    r_fm: Tensor,
    rotbeta: Tensor,
    deformation_length: bool,
    *,
    iqm: int | None = None,
) -> dict[str, Tensor]:
    """omp.out for a `colltype R` target, where ECIS's printed potential is NOT the spherical
    Woods-Saxon.

    "In the rotational models, the optical potentials (for elastic scattering) are always
    deformed" (ECIS `inpa`): `incidentecis.f90` writes one deformed deck, ECIS expands the
    potential in multipoles over its 10-node Gauss-Legendre rule, and the block `incidentread`
    copies is the **lambda = 0** form factor, i.e. the angle average of W-S evaluated at the
    deformed radius R(theta). That is larger than the spherical potential in the tail by
    exp(<delta R>/a) -- 10% at the last printed point of Au-197 and a factor 1.5 for U-238 --
    so the spherical `radial_potential` is the wrong object for these eleven targets, not a
    slightly-off one.

    The multipole expansion itself is T13's (`physics.hf.ecis.formfactor`, gated by A-inc); this
    function only unpacks the lambda = 0 slice into omp.out's sign and column convention:
    V = -Re(central), W = -Im(central), Vso = -Re(spin_orbit)/2, Wso = -Im(spin_orbit)/2, the 2
    being ECIS's spin-orbit factor which the form factor carries and omp.out does not.

    `rotbeta` and `deformation_length` are `ecis.reference.coupled_band(Z, A)`'s; `iqm` defaults
    to `2 * len(rotbeta)`, as `solver.solve_rotational` sets it.

    TALYS: incidentread.f90:1 (incidentread), incidentecis.f90:1 (incidentecis)
    Test: A-omppot
    """
    from dataclasses import replace as _replace

    from physics.hf.ecis.formfactor import SPIN_ORBIT_FACTOR, rotational_form_factors

    r = torch.as_tensor(r_fm, dtype=DTYPE)
    n_e = torch.as_tensor(p.v_mev).reshape(-1).numel()
    if r.dim() == 2 and r.shape[0] != n_e:
        # one energy, many trial radial grids (the f8.5 step fit): give the form factor one
        # parameter row per grid, which is what its (E, R) contract wants.
        if n_e != 1:
            raise ValueError(f"r_fm has {r.shape[0]} rows but the parameters have {n_e}")
        p = _replace(p, **{c: getattr(p, c).reshape(1).expand(r.shape[0]) for c in _FIELDS})
    ff = rotational_form_factors(
        p,
        float(torch.as_tensor(a_mass, dtype=DTYPE)),
        r,
        torch.as_tensor(rotbeta, dtype=DTYPE),
        deformation_length,
        2 * int(torch.as_tensor(rotbeta).numel()) if iqm is None else int(iqm),
    )
    central, so = ff.central[:, 0], ff.spin_orbit[:, 0]
    return {
        "V": -central.real,
        "W": -central.imag,
        "Vso": -so.real / SPIN_ORBIT_FACTOR,
        "Wso": -so.imag / SPIN_ORBIT_FACTOR,
    }


def omp_out_radii(step_fm: float, n: int) -> Tensor:
    """The radius column of omp.out: `iR * step` for iR = 1..n, with ECIS's integration step.

    TALYS: incidentread.f90:1 (incidentread)
    Test: A-omppot
    """
    return torch.arange(1, n + 1, dtype=DTYPE) * float(step_fm)


def jlm_radial_table(*args, **kwargs):
    """JLM radial matter densities (flagjlm, alphaomp 3-5): out of scope for the port.

    TALYS: radialtable.f90:1 (radialtable)
    Test: A-omppot
    """
    raise NotImplementedError("JLM/folding radial densities are out of scope (contract §8)")
