# Plan: every TALYS-2.25 keyword and observable in `physics/hf`

Goal (Seth, 2026-11-08, after A. Koning: "the challenge is to cover all the same observables and keyword
combinations"): the engine reads every TALYS keyword and produces every TALYS observable, or says in the coverage
matrices why not. Inventory: `KEYWORD_COVERAGE.md` (446 keywords) and `OBSERVABLE_COVERAGE.md` (58 output families).
Regenerate both after every batch:

    # WSL; the engine venv has torch
    PY=~/fastgate_data/eng/16606b356d6e/.venv/bin/python
    $PY scripts/kwcov/inventory.py --talys ~/opt/talys-src --echo ~/kwcov/echo/talys.out
    $PY scripts/kwcov/observables.py && $PY scripts/kwcov/render.py

## Where we start (2026-11-08, origin/main 05fa5f70 + B1)

| | SUPPORTED | READ_ONLY_DEFAULT | IGNORED | MISSING | NA | total |
|---|---|---|---|---|---|---|
| keywords | 225 (104 with a test, the rest code-path only) | 8 | 97 | 45 | 71 | 446 |

| | SUPPORTED | PARTIAL | INTERNAL | MISSING | NA | total |
|---|---|---|---|---|---|---|
| observables | 10 | 22 | 7 | 17 | 2 | 58 |

IGNORED is the dangerous class: a deck line is accepted and silently runs on the default. Every batch below either
makes such a keyword act, or makes it refuse (`defaults.UNPORTED`) until it can.

## Rules for every batch

* **Defaults stay bit-identical.** A new keyword, switch or output acts only when set. Check with
  `tests/hf/test_engine_c.py` (Fe-56 bitwise, U-238 to 1e-12) and, for output-only work, an on/off comparison of
  every `Results` array (`scripts/kwcov/b1_compare.py` does it).
* **Test first, against stock TALYS-2.25** (`~/opt/talys-src/bin/talys`, WSL). A stock run of one target at three
  energies takes 1-8 s (Fe-56 1 s, U-238 8 s); keep only the files you compare and delete the rest.
* **Two acceptance metrics.**
  1. *New observable*: engine vs stock, per name and energy where stock > 1 mb: `|ln(ours/stock)| <= 0.5 %` at
     energies where the parent channel already agrees (in practice <= 5 MeV), and no worse than the parent
     channel's own disagreement + 5 % above (B1 used 12 % at 14 MeV; E2E kill limit is 15 %).
  2. *Keyword that changes physics*: the RESPONSE must match, not the absolute value (the engine's defaults differ
     from stock by its known few %): `R = ours(kw)/ours(default)`, `S = stock(kw)/stock(default)` per channel and
     energy, `|ln(R/S)| <= 2 %` where stock > 1 mb, on every channel `engine_job.py` reports plus the channels the
     keyword targets.
* **Standard decks** (n incident unless stated, energies 1, 5, 14 MeV in an `energies` file):
  Fe-56 (spherical, no isomer), Co-59 (isomers in (n,g) and (n,2n)), U-238 (fission, coupled channels);
  add Pb-208 (angular), Au-197 (capture/astro, 1 keV-1 MeV), Nb-93 with `projectile p` (charged), Zr-90 (gas
  production) when a batch needs them. Stock recipe: `channels y`, `filechannels y`, `fileresidual y`,
  `outdiscrete y` + the batch's own output switches.
* **Laptop**: one python or TALYS process at a time, `nice -n 10`, `flock /tmp/incognita_heavy.lock`, `free -g`
  >= 8 GB available first. Native build in a Windows worktree: the build scripts have CRLF endings and WSL has no
  `make`/`cc`; strip `\r` into a temp copy inside `scripts/` and run it with
  `CC=~/micromamba/envs/nucleus-phys/bin/gcc` (see B1 notes below).
* After the batch: rerun the inventory, update the batch's rows (status, `evidence = test:<file>`), commit.

## Batches, in order of value

Effort is for one agent. "Anchors" are the TALYS routines to port (`source/<file>:<line of the subroutine>`); the
keyword's own parse line is in `keyword_coverage.csv` (`talys_line`).

| # | batch | keywords | observables | effort |
|---|---|---|---|---|
| B1 | channel observables (DONE, this branch) | -- | prod/multiplicity (gas production), binary.tot, xs*.tot gamma column, xs*.LMM isomeric channels, xs*.fis, discrete/continuum split | 0.5 d |
| B2 | deck wiring of what exists | best, bestend, bestbranch, bestfile, fit, ngfit, nnfit, nffit, nafit, ndfit, pnfit, gnfit, dnfit, anfit, macsfit, gamgamfit, ejectiles, maxlevelsbin, maxlevelsres, nlevels, estop, liso, isomer (check), per-nucleus forms of ldmodel/colenhance, `energy E1 E2 dE` | CHANOBS default decision | 1-1.5 d |
| B3 | angular distributions on TALYS keywords | outangle, outlegendre, fileelastic, fileangle, angles, anglescont, cpang | elastic/inelastic ang + leg, Rutherford ratio (charged), compound ang. for charged particles | 1.5-2 d |
| B4 | spectra, DDX, gamma lines on TALYS keywords | outspectra, filespectrum, fileddxe, fileddxa, ddxmode, outgamdis, filegamdis, channelenergy, adddiscrete, addelastic, equispec (check) | emission spectra, DDX, discrete gamma lines, exclusive channel spectra, (n,gn) column xsngn | 1.5-2 d |
| B5 | model keyword sweep: compound, gamma, levels, LD | tjadjust, rgamma, cknock, esurf, pshiftadjust, pshiftconstant (check), spradjust, popmev, emaxpseudores, pseudoreswidth, pseudoresfade, ntop, nlow, densfile, e1file, m1file, skipcn, maxzrp, maxnrp, rpevap, branch, levelfile, deformfile, massdir, sfth, sfexp, ldmodelracap | -- | 1.5-2 d |
| B6 | model keyword sweep: optical model, direct | vinfadjust, incadjust, rvadjustf ... awsoadjustf (12), riplomp, optmod, optmodfilen, optmodfilep, ompenergyfile, coulomb, ecisstep, eciscompound, statepot (check), rotational, sysreaction | -- | 1.5 d |
| B7 | unported model branches (now refused) | gnorm y, gshell y, twocomponent n, preeqspin 3, preeqmode 3, onestep, emsdmin, msdbins (MSD) | -- | 2 d |
| B7b | JLM and folding alpha OMP | jlmomp, jlmmode, radialmodel, radialfile, lvadjust, lwadjust, lv1adjust, lw1adjust, lvsoadjust, lwsoadjust, alphaomp 3-5, adepthcor, aradialcor | -- | 2-3 d |
| B8 | fission extras | fisfeed, rfiseps, axtype, class2file, hbtransfile, cnubar1, cnubar2, tmadjust, fsadjust, pfnsmodel 1 | rpZZZAAA.fis, nubar (Wahl), PFNS (Iwamoto), fission info | 2 d |
| B9 | astrophysics | astro, astrogs, astroex, astroe, astrot, nonthermlev | astrorate.*, MACS | 1-1.5 d |
| B10 | URR | urr (check), lurr, urrnjoy, rprime | urr*.dat, urrtalys.tot | 1.5 d |
| B10b | thermal, natural targets, resonance range | xscaptherm, xsptherm, xsalphatherm, mass 0, abundance, resonance, group, integral, reslib, tres | thermal xs, natural sums, resonance/group/integral | 1.5 d |
| B11 | medical isotope production | production, ebeam, eback, ibeam, tirrad, tcool, area, rho, radiounit, yieldunit | Y*.tot yields/activities | 1 d |
| B12 | recoils and LAB frame | recoil, recoilaverage, maxenrec, anglesrec, labddx | recoil spectra, LAB DDX | 2 d |
| B13 | ingredient outputs | outdensity, filedensity, outgamma, filepsf, outinverse, outomp, outkd, partable | ld/psf tables, T and inverse xs, OMP parameters, parameters.dat | 1 d |
| B14 | fission yields and fragment evaporation | massdis, fymodel, ffmodel, gefran, outfy, ffevaporation, ffspin, yieldfile, pfnsmodel 2 | yieldA/ZA, nu(A), P(nu), PFNS/PFGS from FF decay | 4+ d (split: Brosa; GEF; FF evaporation) |
| B15 | low value | endf, endfdetail, sacs, legacy, components | endf.cs helpers, sacs.dat, component split | 1 d |
| GAP | isomeric (excited) targets | ltarget | everything for an excited target | 3+ d; separate design (the engine refuses `Ltarget /= 0`, structure/levels.py:171; astro/stellar.py already builds excited entrance channels and is the starting point) |

NA keywords (71: `out*`, `file*`, `block*`, paths, labels, ECIS plumbing) stay NA; the observables they gate are
batches above.

### B1 -- channel observables (done on branch `kwcov1`)

* What: `Results.extras` (new field, empty by default) carries TALYS's names for numbers the engine already computed:
  `<p>prod.tot` (+ `:multiplicity`), `binary.tot:<p>`, `<k0><p>.tot:discrete|continuum`, `xsNNNNNN.tot:gamma`,
  `xsNNNNNN.LMM` (+ `:branch`), `xsNNNNNN.fis`. Module `physics/hf/emission/chanobs.py`; switch
  `INCOGNITA_CHANOBS=1`. On the C driver the switch takes the Python channels on the C cascade's result (the
  existing fallback), because `ce_channels` returns only channel cross sections.
* Found on the way: particle production was wrong for neutrons by default (aprod Co-59 14 MeV 21 vs 38 mb) because
  the cascade gets only the compound part of `xsbinary` unless TRITFID is on. CHANOBS adds the missing direct,
  pre-equilibrium, giant-resonance and direct-capture emission (`multiple.binary_adds`, exact because xsparticle is
  a sum over xsfeed). TRITFID itself is untouched (still off for neutrons).
* Acceptance (`tests/hf/test_chanobs.py`, `scripts/kwcov/b1_compare.py`): switch on vs off, every other array
  identical (Fe-56 611, Co-59 660 arrays bitwise; U-238 one array 1.7e-16, the fission path's known run-to-run
  noise); Co-59 isomer files sum to the channel; Co-59 vs stock: <= 0.5 % at 1 and 5 MeV, <= 12 % at 14 MeV
  (measured worst 7 %, tracking the engine's own (n,p)/(n,a) differences). Fe-56 and U-238 checked by the script,
  same picture (14 MeV pprod +10 %, aprod +11 % = the engine's (n,p)/(n,a) at 14 MeV; xs*.fis within 10 % = its
  (n,f)).
* Left for later: the (n,gn) column `xsngn` of `.con`/`.tot` files (B4); CHANOBS default ON (B2 decides after
  timing it on a chart sample: it costs the Python channels per energy).

### B2 -- deck wiring of what exists

* `best y` / `bestend` / `bestbranch` / `bestfile` and the `*fit` flags: today they work only through
  `INCOGNITA_TALYS_FIT`; a deck line is ignored. Route them to `fitlib.modes()` when they come in deck lines
  (`initial_best.f90:1`, `input_fit.f90:1`, `xsfit.f90:1`). `bestbranch` needs `branch` lines (B5).
* `ejectiles` (parskip, `input_basicpar.f90:98`), `maxlevelsbin` (`nlevbin`, `nuclides.f90`), `maxlevelsres`
  (`nlevmaxres`, `nuclides.f90`), `nlevels`, `estop` (`read_energies.f90`), `liso` (`levels.f90`).
* Per-nucleus forms of Options keywords: `ldmodel Z A n`, `colenhance Z A y` (getvalues class 14/13); today
  `default_options` raises.
* `energy E1 E2 dE` range form and energy files with TALYS's own grid (`read_energies.f90`).
* Accept: response metric on Fe-56 and U-238 for each switch; `best y` on Fe-56 and U-238 equals
  `INCOGNITA_TALYS_FIT=best` bitwise.

### B3 -- angular distributions

* Exists: `specang.py` behind `INCOGNITA_SPECOUT` (shape + compound elastic, discrete inelastic, Legendre).
* Do: `outangle`/`outlegendre`/`fileelastic`/`fileangle` switch it on; `angles`, `anglescont` set the grid
  (already in `core/grids.py`); put the distributions in `Results` under TALYS names (`nnang.L00`, `nnleg.L00`,
  `elastic.ang`); add the Coulomb amplitude for charged projectiles (ratio to Rutherford) and `cpang`
  (`angdis.f90:1`, `angleout.f90:1`).
* Accept: Fe-56 and Pb-208 elastic + first two inelastic levels at 1, 5, 14 MeV vs stock, 2 % per angle where
  dsigma/dOmega > 1 mb/sr; Nb-93 (p,p) ratio to Rutherford 2 %.

### B4 -- spectra, DDX, discrete gamma lines

* Exists: `specout.py` (spectra, gamma lines, C path), `specang.py` (Kalbach DDX), behind `INCOGNITA_SPECOUT`.
* Do: TALYS keywords drive them; TALYS names; `adddiscrete`/`addelastic` peaks (`spectra.f90:1`);
  `channelenergy` exclusive spectra (`channelsout.f90:641`); `xsngn`.
  Anchors: `spectra.f90:1`, `spectraout.f90:1`, `ddxout.f90:1`, `gamdisout.f90:1`, `kalbach.f90:1`,
  `kalbachsep.f90:1`.
* Accept: Fe-56 14 MeV n and p spectra (energy-integrated within 2 % of `nprod`, shape 5 % per bin above 1 mb/MeV),
  DDX at 30/90/150 degrees, the 846.8 keV Fe-56 line vs stock 2 %.

### B5 -- model keywords: compound, gamma, levels, level densities

Read in `defaults.py` today but nothing uses them. Where TALYS consumes each: `tjadjust` comptarget.f90 and
multiple.f90; `rgamma` emissionrate.f90; `cknock` knockout.f90; `esurf` preeq.f90; `pshiftadjust` densitypar.f90;
`spradjust` fstrength.f90; `popmev` excitation.f90; `emaxpseudores`/`pseudores*` pseudo_resonance.f90;
`ntop`/`nlow` densitymatch.f90; `densfile` densitytable.f90; `e1file`/`m1file` (convert.f90 + fstrength);
`skipcn`, `maxzrp`, `maxnrp`, `rpevap` multiple.f90; `branch` branching.f90; `levelfile` levels.f90;
`deformfile` deformpar.f90; `sfth`, `sfexp`, `ldmodelracap` racapinit.f90.
Accept: response metric, one deck per keyword family (Fe-56 for CN/LD/gamma, Au-197 for racap at 1 keV-1 MeV).
Anything not done by the end of the batch goes to `defaults.UNPORTED` so it refuses instead of being ignored.

### B6 -- model keywords: optical model, direct

`vinfadjust` opticalnp.f90; `incadjust` ompadjust.f90; the 12 `*adjustf` keywords (`ompadjustF`, opticalcomp.f90,
opticalnp.f90, `adjustf.f90:1`); `riplomp` omppar.f90 + riplomp_mod.f90; `optmod*`/`ompenergyfile` external OMP
files (omppar.f90, `convert.f90`); `coulomb`, `ecisstep` incidentecis.f90; `eciscompound` comptarget.f90
(ECIS compound); `rotational`, `sysreaction` (directmodel). Accept: response metric on Fe-56 (spherical) and
U-238 (coupled), reaction and total cross section 1 %.

### B7 / B7b -- unported model branches

Refused today (`defaults.UNPORTED`): `gnorm y` (`radwidtheory.f90:1`; `gamma.transmission.radwidtheory` has the
iteration, nothing calls it), `gshell y` (damping in the exciton model), `twocomponent n` (one-component exciton,
`exciton.f90`), `preeqspin 3` (J-dependent PE population), `preeqmode 3` (`bonetti.f90:1`), MSD (`onestep`,
`emsdmin`, `msdbins`: `msd.f90:1`, `msdinit.f90:1`, `msdcalc.f90:1`, `onestepA.f90:1`).
B7b: JLM (`mom.f90:1` and the radial-density tables; `lv*`/`lw*` adjust, `jlmmode`, `radialmodel`, `radialfile`)
and folding alpha OMPs 3-5 (`foldalpha.f90:1`, `adepthcor`, `aradialcor`).
Accept: response metric on Fe-56 and Zr-90 at 14 MeV (PE-sensitive channels (n,p), (n,a), nprod).

### B8 -- fission extras

Per-fissioning-nucleus fission (`rpZZZAAA.fis`, `finalout.f90:396`), `fisfeed`, `rfiseps`, `axtype`
(`colenhance.f90`, densitypar), `class2file`, `hbtransfile` (`fissionpar.f90`), `cnubar1/2` + `nubarWahl.f90:1`,
PFNS Iwamoto (`iwamoto.f90:1`, `pfnsout.f90:1`, `tmadjust`, `fsadjust`). Accept: U-238 and Th-232 at 1, 5, 14 MeV:
per-chance fission vs stock within the engine's own (n,f) band; nubar 0.5 %; PFNS mean energy 1 %, shape 3 %.

### B9 -- astrophysics

Exists: `astro/stellar.py` (thermalised target, SEF; `INCOGNITA_STELLAR`). Do: `astro y` and the `astro*` keywords
drive it; reaction rate files and MACS as TALYS writes them (`astroout.f90:1`, `stellarrate.f90:1`,
`partfunc.f90:1`), `nonthermlev`. Accept: Au-197 and Ge-74 rates at T9 = 0.1-10 and MACS at 30 keV vs stock 2 %.

### B10 / B10b -- low energy

URR: `urr.f90:1`, `urrout.f90:1` (`urr`, `lurr`, `urrnjoy`, `rprime`). Thermal: `thermal.f90:1`,
`thermalxs.f90:1`. Natural targets: `natural.f90:1` (loop over isotopes, `abundance`). Resonance range:
`resonance.f90:1`, `integral.f90:1` (needs external resonance libraries, lowest priority).
Accept: U-238 and Fe-56 URR parameters vs stock 1 %; natural Fe = abundance-weighted sum 1e-6.

### B11 -- medical isotope production

`prodinitial.f90:1`, `prodrates.f90:1`, `prodyield.f90:1`, `prodout.f90:1`, decay data `decaydata.f90:1`.
Post-processing of residual (and isomer) production -- needs B1-style isomer output and RESISO on.
Accept: p + Ni-nat or Zn-68 (p,x) yields/activities vs stock 1 % given the same residual production.

### B12 -- recoils and LAB frame

`recoilinit.f90:1` (576 l.), `angdisrecoil.f90:1`, `recoilout.f90:1`, LAB DDX in `ddxout.f90`. Accept: Fe-56
14 MeV residual recoil spectra vs stock 3 %.

### B13 -- ingredient outputs

`ingredients.py` already writes D0, Gg, S0. Add ld/psf tables, transmission and inverse cross sections, OMP
parameters under TALYS names, and `partable y` = `parameters.dat` (every parameter value the run used; what a
TASMAN-style sampler needs). Accept: Fe-56 parameters.dat identical keys, values 1e-5.

### B14 -- fission yields, fragment evaporation

`massdis.f90:1` (Brosa, 779 l.), GEF (7,264 l., `fymodel 2` default), `ffevap.f90:1`, `massdisout.f90:1`,
`nudisout.f90:1`. Split into three sub-batches (Brosa; GEF or an external-yield-file path via `ffmodel 0` /
`yieldfile`; FF evaporation for nu(A), P(nu), PFNS model 2). Accept: U-235 thermal and U-238 14 MeV Y(A) vs stock
5 % at the peaks.

### B15 -- low value

ENDF helper outputs (`endf y`: `endfinfo.f90:1`), `sacs` (`sacs.f90:1`), `legacy`, `components`. Do only after
everything above.

## Known gap: isomeric targets

`ltarget /= 0` is refused (`structure/levels.py:171`). TALYS runs an excited target as an ordinary run with the
entrance channel on level `ltarget` (`Ltarget` in comptarget.f90, direct.f90 skips direct reactions). The pieces
exist in `astro/stellar.py` (excited entrance channels through the engine's own comptarget). Needs its own design
note before a batch: grids, binary, level removal, the isomer as residual vs target, and the best files of `m`
targets (`best/<El><AAA>m`).
