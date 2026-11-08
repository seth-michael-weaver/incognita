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
| B4 | spectra, DDX, gamma lines on TALYS keywords (DONE, branch `kwcov4`; exclusive channel spectra -> B4b) | outspectra, filespectrum, fileddxe, fileddxa, ddxmode, outgamdis, filegamdis, channelenergy, adddiscrete, addelastic, equispec (check) | emission spectra, DDX, discrete gamma lines, exclusive channel spectra, (n,gn) column xsngn | 1.5-2 d |
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
* Left for later: the (n,gn) column `xsngn` of `.con`/`.tot` files (B4: done, `Results.spectra[".tot:ngn"]`); CHANOBS default ON (B2 decides after
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

### B3 -- angular distributions (done on branch `kwcov3`)

* What: `physics/hf/angout.py` (output only). The deck keywords `outangle`, `fileelastic` (angleout runs when either is
  y, output.f90:65), `fileangle`, `outlegendre`, `blockangle`, `angles`, `cpang` (new Options fields `flagang`,
  `fileelastic`, `fileangle`, `flagblockangle`; `endf y` sets them as TALYS does) or the port switch
  `INCOGNITA_ANGOUT=1` turn the SPECOUT recorders on for the run and fill `Results.angular` (new field, empty by
  default) under TALYS's names: `<k0><t>ang.LNN` (+ `:direct`, `:compound`, charged elastic `:ruth`, `:nucint`) on the
  `angles` grid, `<k0><t>leg.LNN` (+ `:direct`, `:compound`, `:normalized`, `:endf6`), `angle`.
  `INCOGNITA_ANGOUT_DIR=<dir>` also writes the YANDF files with TALYS's names (`nn0014.000ang.L01`, `nnang.L01` with
  `blockangle y`); headers and the file set equal stock's (Fe-56 run: same 666 names).
* Physics: shape elastic and direct levels from specang (engine OMP / DWBA deck / coupled channels); discrete
  pre-equilibrium x Kalbach (preeqang.f90); compound cleg of EVERY residual (`compound/ceang_types.py`, the generalised
  CEANG with each particle's own spin and TALYS's phase), normalised to the engine's level populations; isotropic
  without flagcompang ((k0 = 1 or cpang) and outangle and E <= 50). Charged projectiles: Coulomb amplitude and phases on
  the engine's S-matrix (`angout.charged_elastic`), ratio to Rutherford and nuclear+interference as angdis.f90.
* Found on the way: the photon exit channel's Moldauer factor is 1 in TALYS (comptarget.f90:510 sends every photon to
  channel tnum+1, whose `tav` molprepare never fills); with the particle formula (n,g) level shapes were off by up to
  6 % (Fe-56 1 MeV) and Legendre terms by 30 % (Pb-208 1 MeV); with it they agree to 1e-6.
* Acceptance (`tests/hf/test_angout.py`, `scripts/kwcov/b3_compare.py`, stock runs in `~/kwcov/stock/b3_*`): switch on
  vs off, every Results array identical (Fe-56 three energies, U-238 692 arrays). Per angle where stock > 1 mb/sr:
  Fe-56 elastic + levels 1-2 at 1, 5, 14 MeV worst 0.39 %; Pb-208 0.25 %; U-238 (coupled) levels 0-3 at 1, 14 MeV
  0.48 %. p + Nb-93 5, 14 MeV ratio to Rutherford 1e-5, elastic 2e-5; cpang y compound distributions 1e-5. Other
  residuals' discrete distributions (n,p) (n,a) (n,d) (n,g): shapes 1e-5 of stock; their absolute level cross sections
  are the engine's (14 MeV: compound +15 %, the known level-population difference; (n,t) (n,h) < 1e-5 mb off by x3-70).
* Left: the charged-particle elastic Legendre Direct column (ECIS's Coulomb-subtracted expansion), HRTW/GOE pair weights
  (isotropic then), charged projectiles on coupled targets (no shape elastic), repeated `fileangle` deck lines (one
  value per key until B2 merges them; `fileangle 1,2` works), `Results.angular` through `pool.py` (not carried),
  `anglescont` (continuum DDX grid) belongs to B4.

### B4 -- spectra, DDX, discrete gamma lines (done on branch `kwcov4`)

* What: `physics/hf/specobs.py` (output only). The deck keywords `outspectra`, `ddxmode` (> 0 implies outspectra),
  `fileddxa`, `fileddxe`, `anglescont`, `outgamdis`, `filespectrum`, `filegamdis`, `blockspectra`, `blockddx`,
  `adddiscrete`, `addelastic`, `channelenergy` (spectra.f90's espec conversion), `elwidth`, `segment` (new Options
  fields `flagspec`, `ddxmode`, `flaggamdis`, `filegamdis`, `filespectrum`, `fileddxa`, `fileddxe`, `flagblockspectra`,
  `flagblockddx`; `endf y` / `recoil y` set them as TALYS does) or the port switch `INCOGNITA_SPECOBS=1` (= outspectra y,
  ddxmode 3, outgamdis y) turn the SPECOUT recorders on and fill `Results.spectra` (new field, empty by default) under
  TALYS's names: `<x>spec.tot` (+ `:E` espec, `:direct`, `:preeq`, `:multiple_preeq`, `:compound`, `:preeq_ratio`, and
  for d t h a / charged projectiles `:breakup_ratio`, `:stripping`, `:knockout`, `:breakup`), `Eaverage_<x>.out`,
  `<x>ddx` (C, M, nanglecont+1) + columns, `<x>ddxAaaa.a.deg`, `<x>ddxEeeee.e.MeV`, `anglecont`,
  `gamZZZAAALiiLjj.tot` (+ `:E`), `<k0><x>.tot:ngn` (xsngn, the B1 gap). `INCOGNITA_SPECOBS_DIR=<dir>` writes the files
  with TALYS's names (`nspec0014.000.tot`, `nddxE0014.000A030.0.deg`, `nddxE0014.000E0003.0.MeV`, `gam026056L01L00.tot`,
  `Eaverage_n.out`; `blockspectra`/`blockddx` names).
* Physics: spectra.f90 on the recorded parts taken as TALYS has them (SPECCLOSE's closing undone: raw binary parts,
  compemission without the discrete-parent addition): espec = egrid up to eoutdis(NL) - elwidth, then the 1/(segment
  fine) grid with Gaussian discrete peaks (elastic with addelastic); Eaverage from Eaveragebin / Eaveragemul / xsfeed;
  DDX = Kalbach (pre-equilibrium, multiple pre-equilibrium) + isotropic compound + discad (angout, run internally for
  every level when only the DDX asks) for the peaks; gamma lines = the cascade's discrete transitions / (1 + conv)
  (cascade.f90:78, electronconv y); xsngn = the initial compound nucleus' own emission (multiple.f90:945).
* Found on the way: gamma lines need the conversion coefficient (Mn-56 26 keV line x2.5 without it); the engine's
  SPECOUT spectra are SPECCLOSE-closed by default (not TALYS), so TALYS names use the raw parts; deck values with two
  words (`fileddxa n 30`) were refused by `default_options` -- `ejectiles` / `ddxpoints` kinds now pass. Not fixed
  (outside B4): with `equispec y` the engine builds the equidistant grid with numen 250 (`preeq/prepare.py`,
  `compound/dens_reference.py`: the reference build) where stock 2.25 has 260, so above 12.5 MeV its step is 0.108
  instead of 0.1 MeV (Fe-56 at 14 MeV); below that the spectra agree as without equispec (5 MeV 2e-4).
* Acceptance (`tests/hf/test_specobs.py`, `scripts/kwcov/b4_compare.py`, `scripts/kwcov/b4_onoff.py`, stock run
  `~/kwcov/stock/b4_fe56`): switches on vs off, every Results array identical (Fe-56 611, U-238 692 arrays bitwise).
  Fe-56 vs stock, espec grids identical; per bin where stock > 1 mb/MeV: 1 MeV 1e-5, 5 MeV 2e-4 (n, g); DDX 30/90/150
  degrees 1.4e-3 at 5 MeV; Eaverage 1e-4; xsngn 1e-4 at 1, 5 MeV; 846.8 keV line 1e-5 at 1, 5 MeV and 1.2 % at 14 MeV.
  14 MeV: n spectrum 5.5 % (integral -1.1 %), p 15 % (integral +9.8 %), DDX n 9 % (150 deg), p 15 % -- the compound
  column carries the engine's own channel differences ((n,2n)/(n,np) composition, (n,p) +10 %); the pre-equilibrium
  column agrees to 4e-5 at every energy; shapes normalised to the integral: n 6.7 %, p 10 %. TALYS's own spectrum
  integral minus elastic equals nprod to 0.25 % at 5 and 14 MeV; ours is the same construction. U-238
  (`~/kwcov/stock/b4_u238`): spectra 1 MeV 1e-3, 5 MeV 2.5 %, 14 MeV 3 % (its compound column); DDX 1 MeV 1.5e-3, but
  14 MeV up to 28 % at 150 deg in the 8-13 MeV band: the collective continuum of the deformed levels above Nlast and
  the giant resonances are isotropic here (their discrete levels' discad agree with stock to 0.5 %); 14 MeV alpha
  espec breaks from egrid to the fine grid 2 MeV later than stock (eoutdis(a, Nlast) of Th-235, sub-mb channel).
* Left: exclusive channel spectra `spNNNNNN*.tot` (B4b: specexcl through the channel loop, specemission.f90);
  the giant-resonance / collective-continuum DDX is isotropic (TALYS: grcollad / directad, DWBA shapes; Fe-56 14 MeV
  <= 0.05 mb/MeV/sr of a few mb/MeV/sr); break-up (kalbachBU, xspreeqbu) is zero (only d/alpha projectiles have it);
  LAB-frame spectra/DDX (B12); repeated `fileddxa`/`fileddxe`/`filespectrum` deck lines need B2's merge (one line per
  key until then: `fileddxa n,30,90,p,150`); `channelenergy y` follows spectra.f90 but is not checked against stock.

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
