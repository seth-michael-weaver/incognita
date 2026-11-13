# Isomeric (excited) targets: TALYS `ltarget` in `physics/hf`

How the engine handles an excited target state (`ltarget > 0`), the design decisions, and the comparison with
stock TALYS-2.25 (section 6). This closes the last structural gap of `COVERAGE_PLAN.md`.

## 1. What TALYS-2.25 does for `ltarget > 0`

`ltarget L` names discrete level `L` of the target (index in TALYS's own level list, 0 = ground state). TALYS runs
an ordinary calculation with the entrance channel on that level. Every place the source reads `Ltarget`
(`grep -n Ltarget source/*.f90`, 115 lines in 34 files) falls in one of the groups below.

### 1.1 Input and level list

* `input_main.f90:131` reads it; `input_levels.f90:106` sets `maxlevelstar = max(30, Ltarget)` (and `:255` after an
  explicit `maxlevelstar`), so the target keeps at least `Ltarget` discrete levels; `nlevbin(k0)` follows.
* `checkvalue.f90:467`: `0 <= Ltarget <= numlev` (= 40) unless `liso` is given; `checkvalue.f90:429`: no excited
  level for a natural target (`mass 0`); `levels.f90:252`: "excited level of target does not exist" when
  `Ltarget > nlev(target)`.
* `levels.f90:270-307`: the target's isomer number `Liso` (the `m`/`n` suffix of the target name, `Hf178n`) and the
  continuum-isomer renumbering (an isomer above the last discrete level is moved onto the last slot; with `liso` set
  this can move `Ltarget` itself).
* Consequence for the choice of test case: **Hf-178m2 is level 109 of Hf-178**, so stock TALYS-2.25 stops
  (`maxlevelstar = 109, Range: 0 <= maxlevelstar <= 40`). It runs only with `ltarget 109` + `liso 2`, which skips the
  range checks and keeps `nlevbin(k0) = 109` past the `numlev` bound of the arrays while the renumbering moves the
  target to level 40. That is not a reference to port against.

### 1.2 Target spin, parity and energy (nuclides.f90:231-234)

`targetspin = jdis(target, Ltarget)`, `targetP = parlev(target, Ltarget)`, `targetE = edis(target, Ltarget)`.

### 1.3 Excitation energy in the compound nucleus and the Q-values

* `energies.f90:131`: `Etotal = eninccm + S(0,0,k0) + targetE`: every exit energy, every residual's `Exmax`, the
  fission and gamma channels see the extra energy.
* `grid.f90:123`: `Elimit = enincmax + S(0,0,k0) + targetE + 1` (top of the emission grid).
* `exgrid.f90:167-171`: `Qres(Zix,Nix,0) = S(0,0,k0) + targetE + Exmax0 - Etotal`, and `Qres(target) = targetE`
  (which the general formula already gives, since `Exmax0(target) = Etotal - S(0,0,k0)`); `Ethresh` follows, so the
  inelastic thresholds of the levels below `Ltarget` are negative (exothermic, superelastic).
* `channels.f90:263`: `Qexcl(0,0) = S(0,0,k0) + targetE`; `recoilinit.f90:281` likewise.

### 1.4 Incident-channel spin coupling

The incident transmission coefficients `Tjlinc` are the same optical-model (or ground-band coupled-channels) ones as
for the ground state at the same incident energy: `incidentecis` never reads the target state. Only the coupling to
the compound states changes, through `targetspin2` / `targetP`:

* `compnorm.f90:92-118`: `CNfactor = pi/k^2 / (2s+1) / (2 I_L + 1)`, `J2` from `|2(I_L + s)| mod 2` to
  `2(lmaxinc + s + I_L)`, `jj2` between `|J2 - 2I_L|` and `J2 + 2I_L`, parity selection on `targetP`;
* `compprepare.f90:163, 217-235` (the same for the lumped sum `enumhf(I_L, pi_L, k0, Ltarget)`);
* `comptarget.f90:360`: `Tjlnex(l, updown, k0, Ltarget) = Tjlinc(updown, l)` (the exit channel back to the
  target state takes the exact incident coefficients), `:379, :431` the parity/spin ranges, `:530`
  `elastic = (type == k0 .and. nexout == Ltarget)` (the WFC elastic enhancement), `:676-681` the Racah algebra of the
  compound angular distribution.

### 1.5 Coupled channels and DWBA

* `direct.f90:33`: `if (Ltarget /= 0) return` -- no `directecis`, `directread`, `giant`: no DWBA level, no giant
  resonance, `xsgrsum = 0`.
* But `incidentread.f90:381-394` still reads the incident coupled-channels inelastic of a deformed target
  (`colltype /= 'S'`): `xsdirdisc(k0, ii)` for the coupled levels of the **ground** band, `xsdirdiscsum`. TALYS keeps
  that direct inelastic for the excited target (for Am-242m: levels 3 and 4 of the 0/3/4 band), even though it was
  computed from the ground state. The port follows TALYS (decision: faithful first; flagged in section 5).
* `directread.f90:96` skips `i == Ltarget` (dead code after `direct.f90:33`).

### 1.6 Discrete levels, inelastic and superelastic

* `binary.f90:266, 315, 338, 368, 504-506`: level `Ltarget` of the k0 residual is the elastic channel:
  `xscompel = xspopex0(k0, Ltarget)`, it is left out of `xsdisc`, `xscompdisc`, the binary feeding and the average
  emission energy, and its population is removed before the cascade (`xspopex`, `xspop(.., int(targetspin),
  targetP)`, `preeqpopex`).
* Every other level is an ordinary inelastic exit, the levels **below** `Ltarget` included: down-scattering to the
  ground state and the lower levels (superelastic) needs no code of its own, because the exit energy
  `Etotal - S - E_x` is simply larger than the incident one. `nn.L00` exists; `nn.L<Ltarget>` does not
  (`discreteout.f90:152, 177`, `finalout.f90:437`).
* `preeqcorrect.f90:90`: no collapse of the pre-equilibrium continuum onto the discrete levels (`goto 100`); the
  part of the spectrum above `nendisc` is still zeroed.
* `spectra.f90:139, 226-227`, `angdis.f90:104`, `angleout.f90`: the elastic line and angular distribution are at
  `Ltarget`.

### 1.7 Fission

No fission routine reads `Ltarget`. The excited target enters fission only through `Etotal` (and the incident spin
coupling): the compound nucleus is `targetE` higher.

### 1.8 Outputs

`mainout.f90:93` (the excited level line), `endfinfo.f90:60`, `astroout.f90:450` (non-thermalised target),
`partfunc.f90:103-137` (partition function relative to the target level), `initial_best.f90:85-93` (best files of
`<El><AAA>m`), `xsfit.f90:173` (fitted libraries are ground-state only), the elastic/angle files of `angleout.f90`
(`nn.L<Ltarget>` angle and Legendre files).

## 2. Plan by engine routine

What exists already: `structure/scalars.py` (`targetspin2`, `target_parity`, `targete_mev` read off level
`Ltarget`), `core/grids.py` and `structure/scalars.target_energy_mev` (ENGFIX4: `targetE` in `Etotal` and `Elimit`),
`emission/channels.py` (`Qexcl(0,0)`), `engine.py` (`Qres` by the general formula), and every compound / binary
routine is written with `inp.ltarget` (`compound/target.py`, `target_batch.py`, `ewfc.py`, `ceang.py`,
`dens_reference.py` rows, `emission/binary.py:317-367`, `engine_c.py:1243`). Only the refusal stood in front.

| # | TALYS | engine routine | change |
|---|---|---|---|
| 1 | levels.f90:252, checkvalue.f90:429, :467 | `structure/levels.py` (`_discrete_levels`), `input/defaults.check_values`, `input/deck.run_deck` | lift the `Ltarget /= 0` refusal; TALYS's three errors instead; `ltarget` + `liso` refused (renumbering path) |
| 2 | nuclides.f90:231-234, energies.f90:131, grid.f90:123 | `structure/scalars.py`, `core/grids.py` | none (ENGFIX4) |
| 3 | direct.f90:33, incidentread.f90:381-394 | `direct/chain.computed_cross_sections`, `direct/chain._direct_result` | no DWBA, `flaggiant = False`; the coupled-channels inelastic stays |
| 4 | preeqcorrect.f90:90 | `preeq/exciton.preeq_correct`, `preeq/preeq_nx2.preeq_correct`, `preeq/prepare.py` | `DiscreteInputs.ltarget`; no collapse onto levels |
| 5 | compnorm.f90, compprepare.f90, comptarget.f90 | `compound/*`, native comptarget | none (already on `targetspin2` / `ltarget`); checked by the runs |
| 6 | binary.f90 | `emission/binary.py`, `engine_c.binary_lean` | none (already on `ltarget`); checked by the runs |
| 7 | exgrid.f90:171 | `engine.channels` | none: the general `Qres` equals `targetE` for the target |
| 8 | outputs (1.8) | `input/defaults.reject_unported` (`LTARGET_UNPORTED`) | refused with `ltarget > 0`: angular (outangle, outlegendre, fileelastic, fileangle), spectra / DDX / gamma lines (outspectra, filespectrum, fileddxe, fileddxa, outgamdis), recoil / labddx, astro, urr, endf, components, eciscompound, racap, production, massdis, channelenergy, and any projectile but n |

## 3. Test decks

Stock TALYS-2.25, `scripts/kwcov/biso_stock.sh` (trimmed runs in `<work>/stock/biso/<case>`), incident neutron at
1, 5, 14 MeV, `channels y`, `filechannels y`, `fileresidual y`, `outdiscrete y`:

| case | target | why |
|---|---|---|
| `fe56_gs`, `fe56_l1`, `fe56_l2` | Fe-56, levels 0 / 1 (0.847 MeV 2+) / 2 (2.085 MeV 4+) | spherical (no coupled channels), cheap (1 s stock); `ltarget 2` has two levels below it (superelastic to 2+ and 0+) |
| `am242_gs`, `am242_m` | Am-242, level 0 (1-) / level 2 (48.6 keV 5-, Am-242m, 141 y) | the real isomer: deformed (incident coupled channels on the 0/3/4 band), fission, high target spin |

**Choice of the isomer case: Am-242m, not Hf-178m2.** Hf-178m2 is level 109 and stock TALYS-2.25 refuses it
(1.1); there is no clean stock reference. Am-242m is level 2, inside every limit, and adds the fission and
coupled-channels paths that a spherical case cannot test. The engine follows stock on Hf-178m2: `ltarget 109`
stops with TALYS's range error.

Engine side: `scripts/kwcov/biso_compare.py` (fresh process per run, TALYS mode = `fidelity.TALYS_DECK` /
`TALYS_ENV`, i.e. the deliberate defaults off, `docs/hf/FIDELITY_DEFAULTS.md`). Acceptance: `|ours/stock - 1| <= 2 %`
on total, elastic, nonelastic, capture, inelastic, (n,2n), (n,p), (n,a), fission where stock > 1 mb, at the energies
where the ground-state run of the same target agrees (the ground-state gap is the engine's own and is reported
beside it). Unit tests: `tests/hf/test_kwcov_biso.py` (checks, refusals, the direct / pre-equilibrium conditions, the
stock numbers transcribed). Defaults stay bit-identical: `tests/hf/test_engine_c.py`.

## 4. Order of work

1. This note.
2. Item 1 (checks, lift the refusal) and the stock decks; run `fe56_l1` to see what the existing `ltarget` plumbing
   gives.
3. Items 3 and 4 (direct and pre-equilibrium conditions); `fe56_l1`, `fe56_l2` against stock.
4. `am242_m` against stock (coupled channels, fission).
5. Item 8 refusals, the test file, the coverage rows (`scripts/kwcov/inventory.py`, `observables.py`, `render.py`),
   the checks.

## 5. Left out (refused, with the reason in the error)

* `ltarget` with `liso` (the renumbering path of 1.1), and so every isomer above level 40 (Hf-178m2). Isomers
  inside the first 40 levels (Am-242m = 2, and the usual low-lying ones) run.
* The outputs of item 8 (they read level 0 as the elastic level or were not checked with an excited target).
* Projectiles other than the neutron.
* Physics question, not a port item: TALYS's incident coupled channels for an excited deformed target are the ground
  band's (1.4, 1.5). A coupled-channels calculation built on the isomer's own band would differ; the port keeps
  TALYS.

## 6. Results

Done as planned (items 1, 3, 4, 8), plus one port bug the first run found:

* **Bug: complex-particle pre-equilibrium at the wrong energy.** `preeq/complex.py` (knockout, stripping, breakup)
  rebuilt eninccm as `Etotal - S(0,0,k0)`, which is eninccm + targetE for an excited target (TALYS uses eninccm
  itself, knockout.f90 / stripping.f90). Fe-56 `ltarget 1` 14 MeV: (n,a) -1.63 % vs stock, (n,2n) / (n,p) /
  inelastic +0.04-0.06 %. Fixed: `PreeqInputs.targete_mev` and `complex._eninccm`; 0 for a ground-state target.
* Small one: an explicit `maxlevelstar` did not keep `max(value, Ltarget)` (input_levels.f90:255); fixed in
  `input/defaults.py`.
* Items 5-7 needed nothing: the compound, binary and Q-value code was already written on `ltarget`.

TALYS mode vs stock TALYS-2.25 (`scripts/kwcov/biso_compare.py`, 1 / 5 / 14 MeV, channels > 1 mb), worst
`|ours/stock - 1|`, on the production C driver (`engine_c`; the Python driver, which the run takes when the native
libraries are not built, gives the same numbers to the digits shown):

| case | main channels (total, elastic, nonelastic, capture, inelastic, n2n, np, na, fission) | discrete inelastic nn.Lnn | ground state of the same target |
|---|---|---|---|
| Fe-56 `ltarget 1` (2+, 0.847 MeV) | 0.001 % | 0.001 % (nn.L00 at 1 MeV = the whole inelastic, 343.69 mb: superelastic) | main 0.003 %, levels 0.06 % |
| Fe-56 `ltarget 2` (4+, 2.085 MeV) | 0.001 % | 0.001 % (nn.L00 57.91, nn.L01 511.99 mb at 1 MeV) | as above |
| Am-242m `ltarget 2` (5-, 48.6 keV) | 0.02 %, except (n,p) 14 MeV +1.30 % (2.71 mb) | 0.02 % (nn.L03 / nn.L04: the ground band's CC inelastic, 119.21 / 244.78 mb at 1 MeV; nn.L00 / L01 superelastic) | 0.03 %, (n,p) 14 MeV +0.47 %, levels 0.25 % |

Fission of Am-242m: 2376.48 / 2319.57 / 2538.50 mb vs stock 2376.45 / 2319.55 / 2538.38 (the ground state:
2003.17 / 2124.74 / 2456.91 stock; the isomer raises it by 19 % at 1 MeV). Capture 1 MeV: 50.62 vs 50.61 mb (ground
state 70.70). Engine wall time per run (three energies, TALYS mode, after import): Fe-56 9-11 s, Am-242m 6 s.
The Am-242m (n,p) at 14 MeV is the one cell above 0.1 %: 2.7 mb, 0.08 % of the nonelastic, and the ground state
has the same sign (+0.47 %); not chased further.

Default mode (the deliberate defaults on) runs too and differs from stock by the same deliberate defaults as the
ground state (`FIDELITY_DEFAULTS.md`): Fe-56 `ltarget 1` 14 MeV (n,p) +11.2 %, (n,a) +10.7 % (`npwindow`; ground state
+12.1 / +11.0 %), Am-242m 1 MeV fission -2.4 %, capture +13.6 % (exactfis and the other actinide defaults).

Tests: `tests/hf/test_kwcov_biso.py` (checks, refusals, target state, the direct and pre-equilibrium conditions, Fe-56
`ltarget 1` at 1 and 14 MeV and Am-242m at 1 MeV against the transcribed stock numbers). `test_engfix4.py`: the
Hf-178m2 test (`ltarget 109`) now stops on TALYS's range check, as stock does.
