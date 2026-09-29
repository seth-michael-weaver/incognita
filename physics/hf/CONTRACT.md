# `physics.hf` — the Python port of TALYS: architecture and interface contract

Status: **foundation (phase 1)**. Nothing here computes a cross section yet except the legacy
toy `capture.py`, which stays untouched until the port replaces it. This document is what
parallel components build against; change it only by a commit that says so in its title.

## 1. What this is, and the order of priorities

A **faithful port of TALYS-2.x** (MIT, © A.J. Koning; `~/opt/talys-src`, 386 files, 146,909
lines) to Python, so the physics can be optimised, differentiated and extended by us. It is
not a reimplementation from papers. The priorities are strictly ordered:

1. **Faithful.** Same inputs (TALYS's own `structure/` database, read directly), same defaults,
   same grids, interpolation and quadrature, same model branches. It must reproduce TALYS
   output (§6 gates) before anyone "improves" anything. Every disagreement must be traceable to
   one routine, which is why every ported function names the Fortran it ports.
2. **Fast.** Vectorised over (case, energy, spin, parity, bin) in `torch.float64`, CPU and
   GPU. A literal DO-loop-for-for-loop translation into Python is **not acceptable** in the hot
   path — it would be orders of magnitude slower than TALYS. Loops that are inherent to the
   physics (the multi-chance cascade over residual nuclei in order, the γ cascade from the top
   bin down) stay loops *over nuclei or bins*; everything inside them is tensor code.
3. **Differentiable** with respect to continuous model parameters (§4.4). Discrete structure
   (which levels, grid positions, model switches) is prepared once and is not differentiated.

Improvements (learned ingredients, new physics) come after the E2E gate, behind a flag whose
default reproduces TALYS.

## 2. Package layout — one subpackage per TALYS subsystem

The layout mirrors the subsystem grouping in `docs/results/talys-inventory.md`
(`scripts/talys_inventory.py`), so the inventory's line counts are also the size of each task.

```
physics/hf/
  CONTRACT.md            this file
  NOTICE-TALYS.md        MIT notice for TALYS; required by every ported module
  capture.py             legacy WP-26 toy — do not edit, do not import from the port
  yandf.py               parser for TALYS YANDF output (reference dumps)           [T0]
  talys_reference.py     runs TALYS, writes/parses the reference dumps              [T0]
  reference.py           dump loader: TALYS quantities as contract-shaped tensors  [T0]
  core/        constants.py numerics.py angmom.py grids.py units.py tensors.py      [T0: units, tensors; T1: rest]
  input/       defaults.py nuclides.py                                              [T3, T2]
  structure/   files.py masses.py levels.py deformation.py resonances.py             [T2]
  omp/         parameters.py potential.py schrodinger.py inverse.py incident.py      [T4: parameters, potential; T5: rest]
  ecis/        bridge.py (reads TALYS T_lj / DWBA from dumps) + the port, later       [T0 bridge; T13 port]
  density/     parameters.py models.py tables.py matching.py particle_hole.py        [T6; particle_hole T8]
  gamma/       parameters.py strength.py transmission.py                            [T7]
  preeq/       exciton.py complex.py spin.py multi.py                               [T8]
  compound/    prepare.py wfc.py target.py continuum.py normalization.py            [T9]
  emission/    binary.py multiple.py channels.py                                    [T10]
  fission/     parameters.py barriers.py transmission.py                            [T11]
  direct/      dwba.py capture.py                                                   [T12]
  engine.py    the talysreaction.f90 driver: run(...) -> Results                    [T10]
  results.py   result schema, names and units matching TALYS output files            [T10]
```

Each stub module lists, in its docstring, the TALYS files it ports with `file:line` anchors
(line = the `subroutine`/`function` statement) and the acceptance test id from §6. The
anchors are checked by `tests/hf/test_contract.py` against the TALYS source when it is present.

## 3. Attribution

Every module that ports TALYS code carries, as the first lines of its docstring:

```
Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License,
Copyright (c) A.J. Koning. See physics/hf/NOTICE-TALYS.md.
```

ECIS-06 (`ecist.f`, J. Raynal) and the RIPL retrieval code (`om_retrieve.f`) are distributed
inside the TALYS repository under its MIT license but have different authors; T13 records the
provenance of each before porting them.

## 4. Conventions every component follows

### 4.1 Numbers and units

* dtype `torch.float64` everywhere (`core.tensors.DTYPE`). No float32, no Python floats in
  tensor paths, no `.item()` / `.numpy()` inside a function that must stay differentiable.
* TALYS itself computes much of its physics in single precision (`real(sgl)`). A float64 port
  will therefore differ from TALYS at ~1e-6 relative even when it is exactly right. Differences
  larger than the §6 tolerances are port bugs until T14 (the double-precision TALYS build)
  shows they are TALYS's own rounding.
* **Units are part of the name.** Public arguments and fields carry a unit suffix:
  `_mev`, `_ev`, `_kev`, `_mb`, `_b`, `_fm`, `_per_mev` (level density), `_mev3` (photon
  strength, MeV⁻³), `_amu`; dimensionless quantities (transmission coefficients, spins,
  branching ratios) carry none. `core.units` defines the constants for every conversion; a
  literal `1000.` or `1e-3` for a unit conversion anywhere else fails review.
* Cross sections are **millibarns** internally and in `Results`, because every TALYS output
  file is in mb. The project has lost a full analysis to "the sweep stores mb" before; the
  suffix is the defence.
* Known unit traps (add to this list when you find one):
  - RIPL `s0` in `staging/structure_params.parquet` is the absolute strength function, not
    units of 1e-4; `gamma_gamma_mev` there holds meV (WP-26 doc). The port reads TALYS's
    `structure/`, not that parquet, but anyone comparing against it must convert.
  - TALYS prints S0/S1 in talys.out as `5.6558 .e-4`: the value is 5.6558e-4.
  - `binE*.out` column units row is shifted by TALYS itself: `bin` is labelled `[mb]` and `Ex`
    `[]`; the population columns are mb and `Ex` is MeV.
  - `ld*.gs` tables are per MeV (`[MeV^-1]`); `nld*.tab` columns are per MeV too but the file
    is fixed-format text, not YANDF.
  - psf files (`psfZZZAAA.E1`) are in MeV⁻³.
  - Closed channels are written as datablocks with `entries: -1` and no rows (α below the
    Coulomb barrier). Their energies are still grid points; `reference.transmission` returns
    them with T = 0 and `open` False.
  - `transmission_inc.out` is overwritten at every incident energy: only the last energy
    survives. Incident-channel T at other energies must come from the port or `talys.out`.

### 4.2 Batching and ragged dimensions

* The leading axis of every per-reaction tensor is the **case** axis `C`: one (target, incident
  energy) pair. `core.tensors.CaseBatch` holds `Z`, `A`, `e_inc_mev` of shape `(C,)`.
* Per-nuclide structure is gathered into padded tensors with an explicit boolean mask
  (`core.tensors.Ragged(values, mask)`): discrete levels `(C, Lmax)`, continuum bins
  `(C, Bmax)`, spins `(Jmax,)` on the shared grid `J = 0, 1/2, ..., numJ` exactly as TALYS
  indexes them (`J2 = 2J`), parity `(2,)` ordered `(-1, +1)` as in TALYS's `do parity = -1, 1, 2`.
* Padded entries must contribute exactly zero to every sum and must not produce NaN in the
  backward pass (use `torch.where` before `log`/`sqrt`/division, not after).
* Residual nuclei are addressed by TALYS's `(Zix, Nix)` index (number of protons/neutrons
  removed from the compound nucleus), never by (Z, A), so ported index arithmetic stays
  line-comparable with the Fortran.

### 4.3 Purity and state

TALYS keeps all state in module globals (`A0_talys_mod.f90`, 2,310 lines). The port does not.
Each subsystem exposes **pure functions** of (structure data, parameters, grids) returning
frozen dataclasses of tensors. The engine threads those objects through explicitly; there is
no module-level mutable state. A function that needs something TALYS reads from a global
takes it as an argument, named after the Fortran variable (`ald`, `Tjl`, `rhogrid`, ...), so
the port can be read side by side with the source.

### 4.4 What must be differentiable

Every continuous quantity TALYS lets a user adjust with a keyword is a `Params` tensor with
the TALYS keyword name and `requires_grad`-able: level density `a` (`aadjust`), pairing shift
(`pshift`), spin cutoff (`spincutmodel` stays a switch; `s2adjust` is a tensor), photon strength
normalisation (`gnorm`, `etable`, `ftable`, `wtable`), OMP geometry and depth factors
(`rvadjust`, `avadjust`, `v1adjust`, ...), barrier heights and widths (`fisbar`, `fishw`),
pre-equilibrium `M2constant`, `Rpinu`. `input.defaults` owns the list and the default values.
Model switches (`ldmodel`, `strength`, `widthmode`, `preeqmode`) are Python ints, not tensors.

Hard branches TALYS takes on continuous values (matching energy root-finding in the CTM,
`locate` into energy tables) are allowed; they must not break autograd, and T6 documents what
gradient flows through the matching energy.

### 4.5 Reading TALYS's database

`structure.files` resolves `$TALYS_DIR/structure/...` (default `~/opt/talys-src/structure`,
3.8 GB density tables, 2.2 GB gamma tables) and parses TALYS's fixed-format files with the
same column positions the Fortran `read` statements use (anchor each reader to its `read`
line). Readers cache per nuclide. No other data source is allowed in the faithful port — not
RIPL files from `raw/`, not our staging tables — because "same inputs" is what makes a
disagreement a port bug.

## 5. Interfaces (the seams between tasks)

Signatures are in the stub modules; this is the dependency spine. Shapes use `C` cases, `E`
emission energies, `L` orbital l, `Jx` spin index, `B` bins, `Lv` discrete levels, `P`=2 parities.

| producer | object | consumed by |
|---|---|---|
| `core.grids` (T1) | `EmissionGrid(e_mev (C,E), de_mev)`, `ExcitationBins(ex_mev (C,B), dex_mev, nlev)` — TALYS `egrid`, `Ex`, `deltaEx`, `maxex` | everyone |
| `structure` (T2) | `Masses`, `Levels(e_mev, spin, parity, branch...)`, `Deformation`, `ResonanceData(d0_ev, gamgam_ev, s0)` | omp, density, gamma, compound, direct |
| `input.defaults` (T3) | `Options` (model switches, ints/bools) and `Params` (adjustable tensors, §4.4) | everyone |
| `omp` (T4/T5) | `Transmission(tjl (C,particle,E,L,3), nj, sigma_reac_mb (C,particle,E))` for emission (j axis padded to 3: n/p/t/h use 2, d 3, α 1 — TALYS writes `T(L-1,L) T(L,L) T(L+1,L)` for d and only `T(L)` for α); `IncidentChannel(tjl_inc (C,L,2), sigma_tot_mb, sigma_reac_mb, sigma_shape_el_mb, s0, s1, r_prime_fm)` | compound, preeq, emission |
| `ecis.bridge` (T0) | the same `Transmission`/`IncidentChannel`/direct cross sections, loaded from dumps for deformed and actinide targets until T13 | compound, direct |
| `density` (T6) | `LevelDensity`: `rho_per_mev(ex_mev, J, parity)` for any residual and fission barrier, plus the `ld*.gs` parameter set | gamma, compound, fission |
| `gamma` (T7) | `GammaTransmission(tgamma (C,B,Jx,P,multipolarity))`, `psf_mev3(e_gamma_mev)`, Γγ normalisation | compound |
| `preeq` (T8) | `PreequilibriumPopulation(xs_mb (C,particle,E), spin distribution)` | emission |
| `fission` (T11) | `FissionTransmission(tfis (C,B,Jx,P))` | compound |
| `compound` (T9) | `compound_target(...) -> BinaryPopulation(pop_mb (C,particle,B+Lv,Jx,P))`, `compound_decay(state) -> feeding` | emission |
| `emission` (T10) | `Results` (exclusive channels, per-level, residual production, totals, all mb) | engine, Stage B |

**Injection rule.** Every consumer accepts its upstream object as an argument, so it can be
tested with TALYS's own upstream values from `physics.hf.reference` before the upstream port
exists. `compound` must pass its gate with dump-injected T, ρ, Tγ *before* it is run on ported
inputs; that separates "compound is wrong" from "an input is wrong".

## 6. Acceptance tests (gates are pre-registered in `docs/results/hf-engine-gates.md`)

Metric for a ported quantity `p` against TALYS `t`, over all points with `t` above the stated
floor: `r = |ln(p/t)|`. Component gates bound the **95th percentile** of `r` and report the
median and max. Tests live in `tests/hf/`, one file per task, and skip (not fail) when the
reference parquet is absent.

| id | component | reference (family in `features/hf_reference/`) | tolerance (p95 of r) |
|---|---|---|---|
| A-grid | emission grid, excitation bins | `transmission` block energies; `binary_population` `Ex`, bin-size meta | exact to 1e-6 MeV |
| A-struct | masses, S_n/S_p/S_α, levels, spins, parities, branchings | `levels` meta + raw rows | 1e-5; discrete data exact |
| A-omppar | OMP parameters, all particles | `omp_parameters` (19 columns) | 1e-5 |
| A-omppot | radial potential | `omp_potential` | 1e-4 |
| A-trans | T(l±1/2) emission, inverse σ | `transmission`, `inverse_xs` (T > 1e-6) | 1% |
| A-inc | incident σ_tot/σ_R/σ_shape-el, S0, S1, R' | `talys.out` blocks, `xs_totals` | 1% |
| A-ld | ld parameters; ρ(U), ρ(U,J,π) | `level_density` | 1e-4 params; 2% tables |
| A-psf | f_E1/M1/E2/M2, theoretical Γγ | `psf` | 1% |
| A-pe | exciton matrix elements, emission rates, pre-equilibrium spectra | `exciton`, `preequilibrium` | 2% |
| A-cn1 | first-chance population per (ejectile, bin/level, J, π), inputs injected, `wfc_off` | `binary_population` | 1% |
| A-cn2 | same with WFC (Moldauer), inputs injected | `binary_population` (`default`) | 2% |
| A-mult | exclusive channels, residual production, per-level xs, inputs injected | `xs_channels`, `residual_production`, `xs_levels` | 5% |
| A-fis | (n,f), fission transmission | `fission` | 5% (actinides, bridge T) |
| E2E | every channel end to end on ported inputs | `xs_*` | §7 of the gates doc: median ≤ 5%, kill > 15% |

The reference set, energies and variants are fixed in `physics/hf/talys_reference.py`
(24 targets A 40–241; 23 energies 1 keV–20 MeV; `default`, `wfc_off`, `minimal`, on-demand
`population`). Adding targets is fine; changing an existing target's inputs invalidates gates.

## 7. What is explicitly out of scope for the port

PREPRO (29,688 lines), GEF (7,264), output writers (10,704), astro, breakup, recoil, angular
distributions and DDX, URR/thermal, ENDF-6 writing, fitting/adjust/best files, isotope
production and medical yields, MSD. Keyword *parsing* is out of scope; keyword *defaults* are
in (T3). All of these can be added later behind the same contract.
