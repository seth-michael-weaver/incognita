"""The incident channel for a deformed (coupled-channels) target: what `incidentecis.f90` +
`incidentread.f90` + `spr.f90` produce, with ECIS replaced by the port.

Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.

Task: T13 (physics/hf/CONTRACT.md §7). Acceptance test: A-inc (§6).

TALYS routines ported here (file:line of the subroutine/function statement):
    incidentecis.f90:1 (incidentecis)
    incidentread.f90:1 (incidentread)

Returns T5's `omp.incident.IncidentChannel`, so switching the engine over for a deformed target
is a one-line change (contract §5: the same shapes `ecis.bridge` serves today).
"""

from __future__ import annotations

import math
import os
from collections import OrderedDict
from typing import TYPE_CHECKING

import torch
from torch import Tensor

from physics.hf.core.tensors import DTYPE
from physics.hf.ecis import ccdisk
from physics.hf.ecis.solver import CoupledResult, solve_rotational, solve_vibrational
from physics.hf.omp.incident import IncidentChannel, strength_functions
from physics.hf.omp.inverse import process_tjl
from physics.hf.omp.schrodinger import PARMASS_AMU, PARZ, nucleus_mass_amu

if TYPE_CHECKING:
    from physics.hf.input.defaults import Options

SOSWITCH_DEFAULT_MEV = 10.0  # input_directpar.f90:64

# FISSC2: the radial step of the incident coupled-channels solve at low incident energy.
#
# ECIS integrates its own grid (`omp.schrodinger.ecis_grid`, h = min(a/2, 0.5/k) ~ 0.27 fm) with
# the MODIFIED Numerov (`ecist.f` inpa, ecis-116); the port integrates the same grid with a plain
# matrix Numerov, whose truncation error has the opposite sign and does not cancel
# (docs/results/hf-ecis-port.md "The integration step").  `refine = 1` was chosen there because
# the *injected* f6.2/f6.3 OMP parameters carried an error of the same size and opposite sign, so
# refining was not uniformly better.  Every live path now passes `omp=None` and builds T4's exact
# RIPL/KD03 parameters instead (T4RIPL, 7eb846a9), so that cancellation is gone and what is left
# is the port's own truncation error -- 1.0-1.9e-3 on sigma_tot of a deformed actinide at 1 keV,
# which is CHART1's whole fissioning-29 deficit (docs/results/hf-fissc2.md).
#
# **Halving the step is enough.**  The plain Numerov is O(h**4): measured on 23 coupled targets,
# `|x(refine)/x(8) - 1|` at 1 keV is 5.6e-4 / 3.4e-5 / 2.0e-6 for refine 1 / 2 / 4 on sigma_tot
# and 8.4e-4 / 5.0e-5 / 3.0e-6 on sigma_reac -- a factor 16 per halving.  `refine = 2` therefore
# already leaves 1/16 of the truncation error, well under every other floor, at half the cost of
# `refine = 4`.
#
# **Only below `INCIDENT_REFINE_EMAX_MEV`.**  Two reasons, both measured (hf-fissc2.md):
#   * cost -- the number of total-J blocks grows with the incident energy, so the sub-MeV end is a
#     small share of a target's coupled-channels cost and the 20 MeV end is most of it;
#   * accuracy -- above ~0.2 MeV the port's truncation error is already below 2e-4 and is partly
#     CANCELLING the other floors (the f6.2 print format of the injected parameters, ECIS's own
#     `1p,d12.5` write-back), so converging it there makes the residual worse, not better.  That
#     is the same non-monotonicity docs/results/hf-ecis-port.md reported.
#
# The threshold is the measured crossover, not a round number.  On the whole chart (482 x 20,
# CHART1 cells against stock TALYS) `refine = 2` applied at E <= 38.4 keV moves 299 cells INTO
# 1e-3 and 48 out; extending it to the next two grid points (64.7 and 109 keV) adds only 16 more
# in against 24 more out, and those two are also the expensive ones, because the number of
# total-J blocks grows with the incident energy.  0.05 MeV sits between the two.
#
# `HF_INC_REFINE=1` turns it off (the A/B lever); an explicit `refine != 1` from a caller (the
# A-inc score tools, which gate the port on ECIS's own grid) always wins.
#
# ---------------------------------------------------------------------------------------------
# CCNUMEROV: **the default is back to 1, because the cause above is now fixed at its source.**
# `solver.modified_numerov` steps ECIS's own modified Numerov (`ecist.f::inch`), so the port is
# on ECIS's discretisation instead of the plain Numerov's opposite-signed one, and refining the
# step now moves the answer AWAY from ECIS rather than towards it.  Measured, whole chart
# 482 x 20 against stock TALYS, three arms interleaved on one Mac (docs/results/hf-ccnumerov.md):
#
#   CHART1 within-1e-3 | fissc2 head | modified + this refinement | modified, refinement off
#   all 482            |     0.99544 |                    0.99658 |                  0.99750
#   fissioning 29      |     0.97861 |                    0.98404 |                  0.98645
#   two-phonon 37      |     0.97794 |                    0.98462 |                  0.99536
#   colltype R cells   |     0.99060 |                    0.99490 |                  0.99597
#   chart CPU-s        |       286.6 |                      269.0 |                    261.0
#
# The third column beats the second on every slice and costs less, so the workaround is off by
# default.  It is kept, not deleted: `HF_INC_REFINE=2` restores it, which is how the table above
# was measured, and it is still the right lever if a future change puts the port back on a
# discretisation of its own.
INCIDENT_REFINE = int(os.environ.get("HF_INC_REFINE", "1"))
INCIDENT_REFINE_EMAX_MEV = float(os.environ.get("HF_INC_REFINE_EMAX", "0.05"))


def _refine_axis(e: Tensor, refine: int) -> Tensor:
    """The per-energy radial refinement of `incident_coupled` (one int per incident energy)."""
    if int(refine) != 1 or INCIDENT_REFINE <= 1:
        return torch.full(e.shape, int(refine), dtype=torch.int64)
    return torch.where(e <= INCIDENT_REFINE_EMAX_MEV,
                       torch.tensor(int(INCIDENT_REFINE), dtype=torch.int64),
                       torch.tensor(1, dtype=torch.int64))
# the OMP fields the solver reads, in ECIS's card order (schrodinger._FIELDS without `ef`)
_OMP_FIELDS: tuple[str, ...] = (
    "v_mev", "rv_fm", "av_fm", "w_mev", "rw_fm", "aw_fm",
    "vd_mev", "rvd_fm", "avd_fm", "wd_mev", "rwd_fm", "awd_fm",
    "vso_mev", "rvso_fm", "avso_fm", "wso_mev", "rwso_fm", "awso_fm", "rc_fm",
)  # fmt: skip


class _Sliced:
    def __init__(self, **kw):
        self.__dict__.update(kw)


def _slice_energies(omp, mask: Tensor):
    return _Sliced(
        **{
            f: torch.as_tensor(getattr(omp, f), dtype=DTYPE).reshape(-1)[mask].contiguous()
            for f in _OMP_FIELDS
        }
    )


def njmax_incident(A: int, m_proj_amu: float, e_max_mev: float, numl: int = 60) -> int:
    """TALYS's estimate of the number of j values requested from ECIS for the incident channel:
    `njmax = max(20, int(2.4*1.25*A**(1/3)*0.22*sqrt(m E)))`, capped at `numl`
    (incidentecis.f90:178-180 -- note it caps at `numl`, while `inverseecis.f90` caps at
    `numl - 2`).

    TALYS: incidentecis.f90:1 (incidentecis)
    Test: A-inc
    """
    x = 2.4 * 1.25 * (A ** (1.0 / 3.0)) * 0.22 * math.sqrt(m_proj_amu * e_max_mev)
    return min(max(20, int(x)), numl)


def _t4_parameters(Z: int, A: int, particle: int, e: Tensor, options):
    """T4's own OMP parameters on the incident energy axis -- the chained path, which since
    T4RIPL's `om_retrieve` covers the five actinides (RIPL OMP 2408) as well.

    TALYS: incidentecis.f90:1 (incidentecis)
    Test: A-inc
    """
    from physics.hf.input.defaults import default_options, default_params
    from physics.hf.omp.parameters import omp_parameters

    o = options if options is not None else default_options(Z, A)
    # SPEEDT: `default_params` is ~16 ms and depends only on (Z, A, options); a caller walking an
    # energy grid one energy at a time (`Cascade.incident`) hands the same `Options` every time
    hit = _PARAMS_CACHE.get((Z, A))
    if hit is None or hit[0] is not o:
        hit = (o, default_params(Z, A, o))
        _PARAMS_CACHE[(Z, A)] = hit
    return omp_parameters(Z, A - Z, particle, e, hit[1], o)


_PARAMS_CACHE: dict[tuple[int, int], tuple] = {}  # (Z, A) -> (options, its default Params)


def _merge(parts: list[tuple[Tensor, CoupledResult]], n_e: int) -> CoupledResult:
    """Reassemble the per-side results of the `soswitch` split back onto one energy axis."""
    first = parts[0][1]
    out = {
        "sigma_tot_mb": torch.zeros(n_e, dtype=DTYPE),
        "sigma_reac_mb": torch.zeros(n_e, dtype=DTYPE),
        "sigma_abs_mb": torch.zeros(n_e, dtype=DTYPE),
        "sigma_shape_el_mb": torch.zeros(n_e, dtype=DTYPE),
        "sigma_direct_mb": torch.zeros((n_e,) + first.sigma_direct_mb.shape[1:], dtype=DTYPE),
        "tjl": torch.zeros((n_e,) + first.tjl.shape[1:], dtype=DTYPE),
    }
    for idx, res in parts:
        for k in out:
            out[k][idx] = getattr(res, k)
    return CoupledResult(
        **out,
        n_j=max(r.n_j for _, r in parts),
        last_j_fraction=max(r.last_j_fraction for _, r in parts),
    )


# CCFAST2: one incident coupled-channels solve per (target, energy) per process. The direct deck
# (`direct.chain._coupled_cached`, the whole declared grid at once) and `Cascade.incident` (one
# energy at a time) used to solve the same blocks twice -- a third of a deformed target's run.
# `solver.sum_blocks` converges each energy on its own, so a row does not depend on which other
# energies shared its call and the second caller can read the first one's. The key carries every
# input the solve reads: the target, projectile, band, lmax, refine, the soswitch choice and the
# 19 OMP parameters AT THAT ENERGY, so an override of the potential is a different key rather
# than a stale hit. Nothing is kept when the parameters are on an autograd graph.
_SOLVED: OrderedDict = OrderedDict()
_SOLVED_MAX = 4096


def _band_key(band: dict) -> tuple:
    out = []
    for k in sorted(band):
        if k == "options":
            continue
        v = band[k]
        if isinstance(v, Tensor):
            v = (str(v.dtype), tuple(v.reshape(-1).tolist()))
        elif hasattr(v, "tolist"):
            v = (str(getattr(v, "dtype", "")), repr(v.tolist()))
        elif isinstance(v, list | tuple):
            v = repr(v)
        out.append((k, v))
    return tuple(out)


def _energy_keys(omp, e: Tensor, base: tuple) -> list[tuple] | None:
    cols = [torch.as_tensor(getattr(omp, f), dtype=DTYPE).reshape(-1) for f in _OMP_FIELDS]
    if any(c.requires_grad for c in cols) or e.requires_grad:
        return None
    n_e = e.shape[0]
    if any(c.numel() != n_e for c in cols):
        return None
    table = torch.stack(cols, 1).tolist()
    return [base + (float(e[i]),) + tuple(table[i]) for i in range(n_e)]


def _row(res: CoupledResult, j: int) -> tuple:
    return (res.sigma_tot_mb[j].clone(), res.sigma_reac_mb[j].clone(), res.sigma_abs_mb[j].clone(),
            res.sigma_shape_el_mb[j].clone(), res.sigma_direct_mb[j].clone(), res.tjl[j].clone(),
            res.n_j, res.last_j_fraction)


def _stack_rows(rows: list[tuple]) -> CoupledResult:
    col = list(zip(*rows, strict=True))
    return CoupledResult(
        sigma_tot_mb=torch.stack(col[0]), sigma_reac_mb=torch.stack(col[1]),
        sigma_abs_mb=torch.stack(col[2]), sigma_shape_el_mb=torch.stack(col[3]),
        sigma_direct_mb=torch.stack(col[4]), tjl=torch.stack(col[5]),
        n_j=max(col[6]), last_j_fraction=max(col[7]),
    )


def incident_coupled(
    omp,
    Z: int,
    A: int,
    e_inc_mev: Tensor,
    band: dict,
    *,
    particle: int = 1,
    options: Options | None = None,
    refine: int = 1,
    lmax: int | None = None,
    energy_mask: Tensor | None = None,
    allow_undeformed_spin_orbit: bool = False,
) -> tuple[IncidentChannel, CoupledResult]:
    """The incident channel of a `colltype R` or `colltype V` target: coupled-channels
    sigma_tot / sigma_reac / sigma_shape-el, the direct cross section to each coupled level,
    T_lj and S0 / S1 / R'.

    `omp` carries the OMP parameters at each incident energy. **Pass `None` and T4 builds them**
    -- including the actinides, whose RIPL-2408 retrieval T4RIPL ported exactly, so nothing here
    needs `ecis.reference.incident_omp` any more. That reader stays as the *injected* arm of the
    A-inc A/B (`score --chained` against the default), where it is bounded by the `f6.2/f6.3`
    print format of `incidentecis.f90:347` rather than by the port.
    `band` is `ecis.reference.coupled_band(Z, A)`. `energy_mask` cuts both `e_inc_mev` and `omp`
    to a subset of the energy axis, so a caller holding a reference target's full 23 energies can
    ask for a subset without rebuilding the parameters.

    `refine` is the radial step divisor.  Left at 1 (every live path) the module's own policy
    applies instead: the step is halved below `INCIDENT_REFINE_EMAX_MEV`, where the port's plain
    Numerov carries a truncation error ECIS's modified one does not (FISSC2, see the constants
    above).  Any other value is taken literally on the whole axis.

    `soswitch` is handled here, not by the caller: `incidentecis.f90:280-287` chooses
    `ecis1(13:13)` per INCIDENT ENERGY, so a rotational target whose axis straddles 10 MeV is
    solved twice -- spherical spin-orbit below, deformed above -- and the two halves are stitched
    back together. `allow_undeformed_spin_orbit=True` forces the lower branch everywhere, which
    is NOT what TALYS does above the switch and exists only to measure what the deformation is
    worth (`physics.hf.ecis.score --above-soswitch --undeformed-so`).

    `Tjlinc(ispin, l) = sum_J (2J+1)/((2j+1)(2I_0+1)) T^J_(0,l,j)` is incidentread.f90:186's own
    coupled-channels weight; `spr.f90` then gives S0, S1 and R' from the spin-averaged T_l and the
    shape-elastic cross section, exactly as for a spherical target (T5's `strength_functions`).

    TALYS: incidentecis.f90:1 (incidentecis), incidentread.f90:1 (incidentread)
    Test: A-inc
    """
    if band["colltype"] not in ("R", "V"):
        raise NotImplementedError(
            f"colltype {band['colltype']!r}: only the symmetric rotational (stage a1) and the "
            "harmonic vibrational (stage a2) models are ported, not the asymmetric rotor "
            "(docs/results/hf-ecis-plan.md)"
        )
    e = torch.as_tensor(e_inc_mev, dtype=DTYPE)
    if energy_mask is not None:
        # `omp` may be T4's OMPParameters or `ecis.reference.InjectedOMP`; both need the same cut.
        if omp is not None:
            omp = omp.select(energy_mask) if hasattr(omp, "select") else _slice_energies(
                omp, energy_mask
            )
        e = e[energy_mask]
    if omp is None:
        omp = _t4_parameters(Z, A, particle, e, options)
    # ECIS's `lo(2)` branch: as soon as one coupled level has two phonons
    # (`ecis1(2:2) = 'T'`, incidentecis.f90:244) EVERY second-order term is on, including the
    # ground-state diagonal and the one-phonon reorientation -- so the whole `vibm` table is
    # rebuilt, not only the couplings of the new levels. A one-phonon target keeps the harmonic
    # path untouched.
    scheme = band_beta = None
    if band["colltype"] == "V" and int(band["iphonon"].max()) > 1:
        from physics.hf.ecis.vibm import scheme_from_band

        scheme, band_beta = scheme_from_band(band)
    soswitch = SOSWITCH_DEFAULT_MEV if options is None else float(options.soswitch_mev)
    m_t = nucleus_mass_amu(Z, A)
    nj = njmax_incident(A, PARMASS_AMU[particle], float(e.max())) if lmax is None else int(lmax)
    n_e = e.shape[0]

    ref_ax = _refine_axis(e, refine)

    def solve(idx: Tensor, deformed_so: bool, ref: int) -> CoupledResult:
        sub = omp.select(idx) if hasattr(omp, "select") else _slice_energies(omp, idx)
        common = (sub, PARMASS_AMU[particle], m_t, float(PARZ[particle] * Z), e[idx],
                  band["e_mev"], band["spin"], band["parity"])
        if band["colltype"] == "R":
            return solve_rotational(
                *common, band["rotbeta"], band["deformation_length"], band["kband"],
                lmax=nj, refine=ref, deformed_spin_orbit=deformed_so,
            )
        return solve_vibrational(
            *common, band["vib_lambda"], band["vib_beta"], band["deformation_length"],
            lmax=nj, refine=ref, scheme=scheme, band_beta=band_beta,
        )

    # `incidentecis.f90:279-287` only touches ecis1(13:13) inside the rotational branch, so a
    # vibrational target never deforms its spin-orbit and has no soswitch.
    above = (
        (e > soswitch)
        if (band["colltype"] == "R" and particle == 1 and not allow_undeformed_spin_orbit)
        else torch.zeros(n_e, dtype=torch.bool)
    )

    def solve_axis(sel: Tensor) -> CoupledResult:
        """The energies `sel` (a mask over `e`), split at `soswitch` and by radial refinement.

        `solver.sum_blocks` converges each energy on its own and `lmax` is fixed on the whole
        axis before the split, so which energies share a call changes no value -- only the radial
        extent the batch carries, which is why the refined low-energy rows are solved apart from
        the unrefined ones (FISSC2) exactly as the two `soswitch` sides already are.
        """
        n_sel = int(sel.sum())
        parts = []
        for deformed_so in (False, True):
            side = sel & (above if deformed_so else ~above)
            if not bool(side.any()):
                continue
            for ref in sorted({int(v) for v in ref_ax[side].tolist()}):
                m = side & (ref_ax == ref)
                if bool(m.any()):
                    parts.append((m, deformed_so, ref))
        if len(parts) == 1:
            m, deformed_so, ref = parts[0]
            return solve(sel, deformed_so, ref)
        return _merge([(m[sel], solve(m, so, ref)) for m, so, ref in parts], n_sel)

    keys = _energy_keys(omp, e, (Z, A, particle, _band_key(band), nj,
                                 bool(allow_undeformed_spin_orbit), soswitch))
    if keys is not None:  # FISSC2: the refinement is per energy, so the key must be too
        keys = [k + (int(ref_ax[i]),) for i, k in enumerate(keys)]
    from physics.hf.ecis import solver as _solver

    if keys is None:
        res = solve_axis(torch.ones(n_e, dtype=torch.bool))
        if _solver._PLAN is not None:  # SPEED50 CCGPU planning pass: nothing was solved
            raise _solver.Planned()
    else:
        miss = torch.tensor([k not in _SOLVED for k in keys], dtype=torch.bool)
        # CCCACHE: the same rows, from disk, across processes and runs. `ccdisk.load` returns
        # None for anything but an exact key match on a readable file, so a hit is the row this
        # process would have solved and a corrupt file is simply a miss.
        if bool(miss.any()) and ccdisk.enabled():
            for i in torch.nonzero(miss).reshape(-1).tolist():
                got = ccdisk.load(keys[i])
                if got is not None:
                    _SOLVED[keys[i]] = got
                    miss[i] = False
        if bool(miss.any()):
            got = solve_axis(miss)
            if _solver._PLAN is not None:  # SPEED50 CCGPU planning pass: nothing was solved
                raise _solver.Planned()
            for j, i in enumerate(torch.nonzero(miss).reshape(-1).tolist()):
                _SOLVED[keys[i]] = _row(got, j)
                ccdisk.store(keys[i], _SOLVED[keys[i]])
            while len(_SOLVED) > _SOLVED_MAX:
                _SOLVED.popitem(last=False)
        rows = []
        for k in keys:
            _SOLVED.move_to_end(k)
            rows.append(_SOLVED[k])
        res = _stack_rows(rows)
    tjl = torch.zeros((n_e, nj + 1, 3), dtype=DTYPE)
    tjl[:, :, :2] = res.tjl
    tjl, t_l, lm = process_tjl(tjl, particle)
    from physics.hf.core.grids import incident_kinematics

    wk = torch.tensor(
        [incident_kinematics(float(e[i]), particle, m_t, 0.0, 0.0)[1] for i in range(n_e)],
        dtype=DTYPE,
    )
    if particle == 1:
        s0, s1, rp = strength_functions(
            t_l, e, res.sigma_shape_el_mb, torch.full((n_e,), float(A), dtype=DTYPE), wk
        )
    else:
        s0 = s1 = rp = torch.full((n_e,), float("nan"), dtype=DTYPE)
    tot = res.sigma_tot_mb if PARZ[particle] == 0 else torch.full((n_e,), float("nan"), dtype=DTYPE)
    el = (
        res.sigma_shape_el_mb
        if PARZ[particle] == 0
        else torch.full((n_e,), float("nan"), dtype=DTYPE)
    )
    return (
        IncidentChannel(
            tjl_inc=tjl,
            sigma_tot_mb=tot,
            sigma_reac_mb=res.sigma_reac_mb,
            sigma_shape_el_mb=el,
            s0=s0,
            s1=s1,
            r_prime_fm=rp,
            t_l=t_l,
            lmax=lm,
        ),
        res,
    )


__all__ = ["SOSWITCH_DEFAULT_MEV", "incident_coupled", "njmax_incident"]
