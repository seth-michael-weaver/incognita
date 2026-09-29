"""The capture cross section from the chained port, without dumps and without the cascade.

Task: SPEED0 gate G0.2 (the speed plan's capture fast path). No physics of its own: every number
comes from the same modules `engine.ChainedFull` runs, in the same order.

**Why the capture channel needs only one nucleus.** TALYS's (n,gamma) exclusive cross section
`xs000000` is the flux that never leaves the initial compound nucleus, and nothing can flow back
into that nucleus once it has left. So it is exactly the compound nucleus's final population
`xspopnuc(0, 0)` after `multiple.f90` has decayed it (checked on the SPEED0 golden record: equal to
the last bit on 24 of 24 cases, 1.5e-16 on the 25th). That needs the binary photon population
(`comptarget`) and the decay of the compound nucleus's own bins -- not the residual nuclei, not
`channels.f90`.

**Where it is exact, and why there.** `ChainedFull` still injects, per incident energy, the
direct-discrete, pre-equilibrium and giant-resonance sums compnorm subtracts (T8/T12 read them
from the reference dumps), and the structure scalars (`popeps`, the target's spin and parity).
Below the target's first excited level (`E_inc < E_1`, lab frame, so the CM energy is lower
still) no inelastic channel is open: the direct-discrete sum is zero (no level to excite),
there is no pre-equilibrium flux (`flagpreeq` is false in every reference dump there) and no
giant-resonance flux, and the scalars are the target's ground-state spin/parity and TALYS's
defaults. That is the fast path's domain; outside it `capture_xs` returns NaN rather than a
number with an injected family silently set to zero. Also outside: fissile compound nuclei
(T11's fission transmission is not built here).

Identity with the full chain is gated by `tests/hf/test_capture_fast.py` against the golden
record's `xs000000` at every in-domain harness energy.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace

import numpy as np

ZERO_ADDENDS = {"xsdirdiscsum_mb": 0.0, "xspreeqsum_mb": 0.0, "xsgrsum_mb": 0.0}


def _f32(x: float) -> float:
    """TALYS holds `Einc`, `popeps` and `xseps` in real(sgl); the chain reads them that way."""
    return float(np.float32(x))


@dataclass
class CaptureTarget:
    """Run-scoped state for one target: the Cascade and the ground-state scalars."""

    Z: int
    A: int
    enincmax: float
    cas: object
    e1_mev: float
    targetspin2: int
    target_parity: int
    popeps_mb: float
    fissile: bool


def target(Z: int, A: int, enincmax_mev: float = 20.0,
           gamma_overrides: dict | None = None,
           energies: tuple[float, ...] | None = None,
           density_overrides: dict | None = None,
           optical_overrides: dict | None = None,
           matching_xacc: float | None = None) -> CaptureTarget:
    """Build the run-scoped part (optical model, grids, level densities load lazily).

    Three families of parameter can be put on the autograd graph, and `capture_xs(...,
    differentiable=True)` then returns a tensor carrying all of them at once:

    * `gamma_overrides` -- T7's `gamma_parameters` fields for the compound nucleus (`ftable`,
      `wtable`, `sgr_mb`, ... as requires_grad tensors). SPEED0's G0.3.
    * `density_overrides` -- level-density TALYS keywords (`aadjust`, `pshift`, `s2adjust`,
      `ctable`, `ptable`, `tadjust`, ...): `physics.hf.density.overrides.DENSITY_KEYS`.
    * `optical_overrides` -- optical-model TALYS keywords (`v1adjust`, `w1adjust`, `d1adjust`,
      `rvadjust`, `avadjust`, ...): `physics.hf.density.overrides.OPTICAL_KEYS`. Per-particle
      keywords take TALYS's own `{"n": value}` form as well as a full tensor.

    The last two are keyword overrides rather than resolved-object overrides, and they go
    through `input.defaults.default_params`, so TALYS's post-resolution links still run
    (`rwadjust` follows `rvadjust`, `ctable`/`ptable` follow `cglobal`/`pglobal`). An unknown
    keyword raises rather than being dropped -- a dropped override is a zero gradient that looks
    like a converged one. DIFFPARAM, gate G0.4.

    `matching_xacc` overrides `rtbis`'s tolerance in the CTM matching (`density.matching`);
    `None` is TALYS's 1e-4 MeV and is what every reproduction of TALYS uses. The gradient gate
    passes 1e-10, because at 1e-4 Exmatch is a staircase in the level-density parameters and a
    finite difference measures the step rather than the slope. See `density.matching.matching`.

    `energies` is the incident energy grid of the TALYS *run* being reproduced, and it matters
    for one reason: `isotrans`'s `fisom` divides the initial compound nucleus's gamma
    transmission by its isospin factor at the run's FIRST energy and nowhere else
    (`emission.feeding.Cascade.fisom`). A Ca-40-type target (compound nucleus with |Z - N| = 1)
    therefore has a different (n,gamma) at 1 keV in a 23-energy run than in a run that starts at
    1 keV and stops. `None` means a one-energy run, which is what a chart sweep is; pass the
    reference grid (`talys_reference.ENERGIES_MEV`) to reproduce a reference run.

    TALYS: talysreaction.f90:1 (talysreaction)
    Test: G0.2 / tests/hf/test_capture_fast.py
    """
    from physics.hf.emission.feeding import Cascade

    cas = Cascade(Z, A, _f32(enincmax_mev), energies=energies)
    cas.gamma_overrides = gamma_overrides
    if density_overrides or optical_overrides or matching_xacc is not None:
        cas.set_param_overrides(density_overrides, optical_overrides, matching_xacc)
    # below E_1 every bin of the compound nucleus under Etotal is fed by the primary photons,
    # so build the decay widths for all of them in one go rather than 24 at a time
    cas.DECAY_CHUNK = 256
    lv = cas._levels(0, 1)  # the target: zn(0, 1) = (Z, A)
    e = lv.all_e_mev.detach().numpy()
    e1 = float(e[1]) if len(e) > 1 else float("inf")
    fissile = bool(getattr(cas.options, "flagfission", False))
    return CaptureTarget(
        Z=Z, A=A, enincmax=_f32(enincmax_mev), cas=cas, e1_mev=e1,
        targetspin2=int(2.0 * float(lv.all_spin[0])), target_parity=int(lv.all_parity[0]),
        popeps_mb=_f32(float(cas.options.popeps_mb)), fissile=fissile)


def in_domain(tg: CaptureTarget, e_inc_mev: float) -> bool:
    return (not tg.fissile) and _f32(e_inc_mev) < tg.e1_mev


def capture_xs(tg: CaptureTarget, e_inc_mev: float, differentiable: bool = False):
    """`xs000000` [mb] at one incident energy, NaN outside the fast path's domain. With
    `differentiable` the result is a 0-d tensor on the graph of the target's gamma overrides.

    TALYS: comptarget.f90:1 (comptarget), multiple.f90:1 (multiple) for (Zcomp, Ncomp) = (0, 0)
    Test: G0.2 / tests/hf/test_capture_fast.py
    """
    from physics.hf.compound.chain import compound_inputs
    from physics.hf.compound.target import compound_target_inputs
    from physics.hf.emission.feed_reference import etotal_of
    from physics.hf.emission.multiple import multiple_emission

    if not in_domain(tg, e_inc_mev):
        return float("nan")
    cas = tg.cas
    e = _f32(e_inc_mev)
    k0 = cas.k0
    etot = etotal_of(tg.Z, tg.A, tg.enincmax, e, k0)
    inc = cas.incident(e)
    st = cas.new_energy(etot, lmaxinc=int(inc.lmax[0]), e_inc_mev=e)
    cas.propagate_exmax(st, 0, 0)
    binp = SimpleNamespace(e_inc_mev=e, k0=k0, targetspin2=tg.targetspin2,
                           target_parity=tg.target_parity, ltarget=0, popeps_mb=tg.popeps_mb,
                           flagpreeq=False)
    ci = compound_inputs(cas, st, binp, SimpleNamespace(flagfission=False), etot, ZERO_ADDENDS)
    pop = compound_target_inputs(ci).pop_mb[0, 0]  # photon residual = the compound nucleus
    n = cas.spec(st, 0, 0).maxex + 1
    xspop = pop[:n].clone()
    xd = xspop.detach()
    seed = {0: (xd.numpy(), xd.sum((-2, -1)).numpy(), float(xd.sum()))}
    nuclei = cas.populations(st, 0, 0, seed)
    if differentiable:
        cn = nuclei[(0, 0)]
        cn.xspop_mb = xspop.clone()
        cn.xspopex_mb = xspop.sum((-2, -1))

    def decay(zc: int, nc: int, nex: int):
        return cas.decay(st, nuclei, zc, nc, nex, popeps_mb=tg.popeps_mb, flagfission=False)

    res = multiple_emission(nuclei, decay, popeps_mb=tg.popeps_mb, maxz=0, maxn=0, k0=k0,
                            xsreacinc_mb=float(inc.sigma_reac_mb[0]))
    # DIRECTCAP: direct radiative capture (racap), off unless INCOGNITA_DIRECT_CAPTURE is set; a
    # constant in the photon-strength / level-density / OMP knobs of this path
    from physics.hf.direct.racapcalc import direct_capture_mb

    dc = float(direct_capture_mb(tg.Z, tg.A, [e])[0])
    if differentiable:
        # multiple.f90:643-646 on the tensors: the ground state plus the isomers
        cn = nuclei[(0, 0)]
        pop = cn.xspopex_mb[0]
        for nex in range(1, cn.nlast + 1):
            if float(cn.tau_s[nex]) != 0.0:
                pop = pop + cn.xspopex_mb[nex]
        return pop + dc
    return float(res.xspopnuc_mb[(0, 0)]) + dc


def capture_curve(Z: int, A: int, energies_mev, enincmax_mev: float = 20.0,
                  declared_energies: tuple[float, ...] | None = None) -> np.ndarray:
    """`capture_xs` over an energy grid for one target (NaN where out of domain).

    `declared_energies` is the run grid `target` needs for `fisom`; `None` treats each point as
    its own one-energy run, which is what a chart sweep is.
    """
    tg = target(Z, A, enincmax_mev, energies=declared_energies)
    return np.array([capture_xs(tg, float(e)) for e in energies_mev], dtype=np.float64)

