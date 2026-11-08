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
| B2 | deck wiring of what exists (DONE, branch `kwcov2`) | best, bestend, bestbranch, bestfile, fit, ngfit, nnfit, nffit, nafit, ndfit, pnfit, gnfit, dnfit, anfit, macsfit, gamgamfit, ejectiles, maxlevelsbin, maxlevelsres, nlevels, estop, liso, isomer (check), per-nucleus forms of ldmodel/colenhance, `energy E1 E2 dE` | CHANOBS default decision | 1-1.5 d |
| B3 | angular distributions on TALYS keywords | outangle, outlegendre, fileelastic, fileangle, angles, anglescont, cpang | elastic/inelastic ang + leg, Rutherford ratio (charged), compound ang. for charged particles | 1.5-2 d |
| B4 | spectra, DDX, gamma lines on TALYS keywords (DONE, branch `kwcov4`; exclusive channel spectra -> B4b) | outspectra, filespectrum, fileddxe, fileddxa, ddxmode, outgamdis, filegamdis, channelenergy, adddiscrete, addelastic, equispec (check) | emission spectra, DDX, discrete gamma lines, exclusive channel spectra, (n,gn) column xsngn | 1.5-2 d |
| B5 | model keyword sweep: compound, gamma, levels, LD (DONE, branch `kwcov5`) | tjadjust, rgamma, cknock, esurf, pshiftadjust, pshiftconstant (check), spradjust, popmev, emaxpseudores, pseudoreswidth, pseudoresfade, ntop, nlow, densfile, e1file, m1file, skipcn, maxzrp, maxnrp, rpevap, branch, levelfile, deformfile, massdir, sfth, sfexp, ldmodelracap | -- | 1.5-2 d |
| B6 | model keyword sweep: optical model, direct (DONE, branch `kwcov6`) | optmodall, vinfadjust, incadjust, rvadjustf ... awsoadjustf (12), riplomp, optmod, optmodfilen, optmodfilep, ompenergyfile, coulomb, ecisstep, eciscompound, statepot (check), rotational, sysreaction | -- | 1.5 d |
| B7 | unported model branches (DONE, branch `kwcov7`; gnorm y and MSD stay refused) | gnorm y, gshell y, twocomponent n, preeqspin 3, preeqmode 3, onestep, emsdmin, msdbins (MSD) | -- | 2 d |
| B7b | JLM and folding alpha OMP | jlmomp, jlmmode, radialmodel, radialfile, lvadjust, lwadjust, lv1adjust, lw1adjust, lvsoadjust, lwsoadjust, alphaomp 3-5, adepthcor, aradialcor | -- | 2-3 d |
| B8 | fission extras (DONE, branch `kwcov8`; fisfeed J-parity columns and fragment-based nubar/PFNS -> B14) | fisfeed, rfiseps, axtype, class2file, hbtransfile, cnubar1, cnubar2, tmadjust, fsadjust, pfnsmodel 1 | rpZZZAAA.fis, nubar (Wahl), PFNS (Iwamoto), fission info | 2 d |
| B9 | astrophysics (DONE, branch `kwcov9`; astro + racap, fissile astrogs n refused) | astro, astrogs, astroex, astroe, astrot, nonthermlev | astrorate.*, MACS | 1-1.5 d |
| B10 | URR (DONE, branch `kwcov10`; widthmode 2/3 refused) | urr (check), lurr, urrnjoy, rprime | urr*.dat, urrtalys.tot | 1.5 d |
| B10b | thermal, natural targets, resonance range | xscaptherm, xsptherm, xsalphatherm, mass 0, abundance, resonance, group, integral, reslib, tres | thermal xs, natural sums, resonance/group/integral | 1.5 d |
| B11 | medical isotope production (DONE, branch `kwcov11`) | production, ebeam, eback, ibeam, tirrad, tcool, area, rho, radiounit, yieldunit | Y*.tot yields/activities | 1 d |
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

### B2 -- deck wiring of what exists (done on branch `kwcov2`)

* **What a deck is now.** A talys.inp (`physics/hf/input/deck.py`: `read_deck`, `run_deck`) or deck lines in
  `INCOGNITA_TALYS_FIT_LINES`. The lines now act without an `INCOGNITA_TALYS_FIT` arm (before, they were dropped
  silently unless an arm was named: POPEPS2 (a)). A deck line the port cannot apply (energy-dependent table form,
  unknown index / particle) is refused; the same line coming from a best file or a fitted library is left out with
  a warning naming it (it was silent). A multi-word form of an Options keyword TALYS does not have is refused (it was
  skipped).
* **Wired** (all default-off; default runs bit-identical, `test_engine_c.py`):
  `best` / `bestend` / `bestfile` (fitlib `_deck_best`: deck `best y` gives the same cards as
  `INCOGNITA_TALYS_FIT=best` for Fe-56, Co-59, U-238 and the same Fe-56 engine arrays bitwise); `fit` and every
  `*fit` flag (`fitflag` kind: sets `flagfit`, `macsfit`/`gamgamfit` turn `ngfit` off; an/dn/pn/gn libraries in
  xsfit.f90 order, matched without the projectile as TALYS does); `bestbranch` (levels/branch file ->
  `structure/levels.py`); per-nucleus `ldmodel v Z A`, `colenhance y Z A` (the TALYS form is value first, not
  `ldmodel Z A v`), `nlevels Z A n`, `maxlevelsbin p n` (`Options.pernuc`, `nlev_of`/`ldmodel_of`/`flagcol_of`;
  out-of-box nuclei ignored with TALYS's warning); `maxlevelsres` (was read but called IGNORED: `nlev_of` uses it);
  `estop` (energies above it are not computed, the grid keeps `enincmax`, `input/energies.estop_subset` in both
  drivers); `energy E1 E2 [dE]`, energy files and `n0-20.grid`-style grids (`input/energies.py`, equal to the
  `energies` files TALYS-2.25 writes); `liso` (labels only, in TALYS too).
* **Refused:** `ejectiles <subset>` (`defaults.UNPORTED`): parskip reaches only the channel bookkeeping in the
  engine, not the compound or pre-equilibrium decay; Fe-56 `ejectiles g n p` at 14 MeV moved stock (n,2n) +3.4 %,
  (n,p) +3.1 % and the engine 0.0 %.
* **TALYS-2.25 bug found:** `branch` lines never act: strucinitial.f90:312-325 resets `branchratio`/`nbranch` after
  the input is read (stock Co-59 `branch 27 58 2 1 0 1.0`: no cross section moves; `bestbranch y`, read after the
  reset, does act). The port reproduces it, with a warning. Co-59's best file carries four such lines.
* **Response vs stock** (`scripts/kwcov/b2_response.py`, n + target at 1/5/14 MeV, `|ln(R/S)|` max over channels
  with stock > 1 mb; limit 2 %):

  | deck lines | target | worst | | deck lines | target | worst |
  |---|---|---|---|---|---|---|
  | maxlevelsres 10 | Fe-56 / Co-59 / U-238 | 0.03 / 0.02 / 0.01 % | | ngfit y | Fe-56 | 0.23 % |
  | maxlevelsbin p 5 | Fe-56 | 0.19 % | | macsfit y | Fe-56 | 0.38 % |
  | nlevels 25 56 5 | Fe-56 | 0.19 % | | gamgamfit y | Fe-56 | 0.15 % |
  | ldmodel 2 26 57 | Fe-56 | 0.99 % | | bestbranch y | Co-59 ((n,2n) isomers) | 0.02 % |
  | colenhance y 26 57 | Fe-56 | 0.31 % | | branch 27 58 2 1 0 1.0 | Co-59 | 0.00 % (both 0) |
  | estop 6 | Fe-56 | 0.00 % | | liso 1, isomer 0.001 | Fe-56 | 0.00 % (both 0) |
  | **ldmodel 1 92 238** | U-238 | **3.1 %** (n,2n) 14 MeV, a 51 % move | | **fit y** | Fe-56 | **4.0 %** (n,p) 14 MeV |
  | **best y** | Co-59 | **8.2 %** (n,g) isomer 1 MeV | | **best y** (no table / table) | Fe-56 | **6.8 / 11 %** |
  | **best y** | U-238 | **8.1 %** fission 5 MeV | | | | |

  Losses, traced: `fit y` = two engine responses, `gadjust 26 57` (CN g of the exciton model; (n,p) 2.7 %,
  (n,d) 2.7 %) and `cstrip a` ((n,a) 2.2 %); `rvadjust p/a/d`, `cstrip d`, `gadjust` of the residuals pass
  (<= 0.8 %). These are pre-equilibrium port issues for B5/B7, not wiring. `best y` carries the same knobs
  (cknock/cstrip, m2constant, g*adjust) plus, for Fe-56, an energy-dependent `awdadjust` table and, for U-238, an
  external OMP file (`optmod`), which the port does not read (B6; warned). U-238 `ldmodel 1` on the target: an
  actinide level-density response, open.
* **CHANOBS default decision: stays OFF.** Turning it on by default would change `Results` for every caller (new
  `extras`) and cost the Python channels per energy on the C path, against the rule that defaults stay
  bit-identical. The TALYS output keywords that ask for those files (`filechannels`, `fileresidual`, ...) are NA rows;
  wiring them to CHANOBS belongs with the output batches (B4/B13).
* Tests: `tests/hf/test_kwcov_b2.py` (parsing, precedence, refusals, energies vs TALYS's own files, deck `best y`
  = best arm bitwise through the engine).

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

### B5 -- model keywords: compound, gamma, levels, level densities (done on branch `kwcov5`)

* **Wired** (default-off; Fe-56 611 and U-238 692 `Results` arrays bitwise with nothing set, `test_engine_c.py`):
  `nlow`/`ntop Z A n [ibar]` (`Options.nlow_of`/`ntop_of` -> `density/parameters.py`, `ld_nx2.py`; they were
  skipped); `skipcn Z A` (`Options.skipcn_of`: the Python walk does not decay the nucleus, multiple.f90:262; the C
  cascade hands such a run to it); `levelfile Z <file>`, `deformfile Z <file>` (deck lines keep the file name's case,
  relative to the deck's directory; a missing level file stops the run as TALYS does; a best file's own lines,
  Mo-95/97, Hf-174..180, are still left out with a warning); the global form of `pshiftconstant`; `sfth v [Z A]`,
  `sfexp v [Z A ilev]` (class 15, value first) now reach the direct-capture structure, which took the defaults;
  `racap y|n` on a deck (it was read and ignored; it now wins over `INCOGNITA_DIRECT_CAPTURE`).
* **Already acting, now tested:** `rgamma`, `esurf`, `cknock`, `pshiftadjust`, `spradjust` (the inventory's grep missed
  them: they are read under their keyword names through `Params.at`).
* **TALYS-2.25 behaviour reproduced, with a warning:** a constant `tjadjust Z A <p> v` never acts (comptarget.f90:331
  and multiple.f90:429 use `adjust`'s factor, which has no entry for a constant line; `TJadjust` is read nowhere;
  stock Fe-56 0.0 %); `racap y` without `optmodall y` gives exactly 0 mb (the final-state well is never built,
  structure.f90:85; stock Au-197 capture 0.0 %).
* **Inert, as in TALYS:** `maxzrp`/`maxnrp` (only with `rpevap y`), `popmev` (only with a population input,
  projectile 0), `emaxpseudores`/`pseudoreswidth`/`pseudoresfade` (only with `pseudoresonances y`, refused).
* **Refused:** `rpevap y`, `optmodall y` (`defaults.UNPORTED`); `ldmodelracap` 1/2 with direct capture on; the
  `Ea Eb Em D` / file forms of `tjadjust`; `densfile`, `e1file`, `m1file`, `massdir` (external files, refused on a
  deck line). **Deck lines with a keyword the port does not know are now refused**; before B5 they were skipped
  without a word (every MISSING row, 36 keywords, was silently accepted on a deck). Output switches, paths and
  labels (the NA rows: `out*`, `file*`, `block*`, `partable`, ...) stay accepted and change nothing.
* **Bug found (B6):** `optmodall y` was SUPPORTED in the matrix (the grep hit comments) but no engine code reads
  `flagompall`: stock Au-197 1 MeV capture +93 %, inelastic -38 %, engine 0.0 %. Refused until B6 ports it.
* **Response vs stock** (`scripts/kwcov/b5_response.py`, n + target at 1/5/14 MeV; `racap` subcommand: racap.tot
  `xs(dir. cap.)` of stock `racap y optmodall y` vs `racapcalc.direct_capture_mb`; limit 2 %):

  | deck lines | target | worst (stock moved) | | deck lines | target | worst (stock moved) |
  |---|---|---|---|---|---|---|
  | rgamma 4 | Fe-56 | 0.82 % (63 %) | | ntop 26 56 6 | Fe-56 | 0.77 % (29 %) |
  | esurf 20 | Fe-56 | 0.28 % (4.0 %) | | ntop 26 57 8 | Fe-56 | 0.92 % (38 %) |
  | pshiftadjust 26 57 0.5 | Fe-56 | 0.01 % (0.4 %) | | nlow 26 56 3 | Fe-56 | 0.05 % (1.5 %) |
  | spradjust 26 57 2.0 m1 | Fe-56 | 0.00 % (4.6 %) | | levelfile 26 (2+ at 0.95 MeV) | Fe-56 | 0.02 % (38 %) |
  | cknock a 2, cknock n 2 | Fe-56 | 0.00 % (0 %) | | deformfile 26 (beta2 0.30) | Fe-56 | 0.06 % (2.6 %) |
  | tjadjust 26 57 p 1.5 | Fe-56 | 0.00 % (0 %) | | racap y | Au-197 | 0.00 % (0 %) |
  | ldmodel 2; pshiftconstant 1.5 | Fe-56 | = ldmodel 2 (0 %) | | sfexp 0.5 (racap.tot) | Au-197 | 0.00 % (1.6 %) |
  | **skipcn 26 56** | Fe-56 | **9.4 %** (n,np) 14 MeV (105 %) | | sfth 0.5 / 0.01 (racap.tot) | Fe-56, Zr-90, Au-197 | 0.00 % (0 %) |

  Loss, traced: with Fe-56 skipped, what is left of (n,np) is the Mn-56 path, i.e. the engine's default (n,p) excess at
  14 MeV (139.9 vs 124.8 mb); every other channel 0.0 %.
* **B2's open losses, traced (not keyword bugs, so not fixable here without moving defaults):**
  `cstrip a` moves (n,a) by the same millibarns as stock (9.59 vs 9.63 mb, 0.4 %); the 2.2 % is the engine's default
  (n,a) being 11 % higher at 14 MeV. `gadjust 26 57` acts only through pre-equilibrium (with `preequilibrium 20` both
  sides are unmoved); the flux it returns to the compound nucleus decays to protons more in the engine (compound-only
  (n,p) 151.5 vs 131.5 mb): the same default excess. `ldmodel 1 92 238`: with the keyword the engine's (n,2n) at 14 MeV
  is 1537.6 vs stock 1540.8 mb (0.2 %); the 3.1 % is the default run's own (n,2n) -3.3 % / fission +4 %. Global
  `ldmodel 2` on Fe-56: 2.85 % ((n,a) 14 MeV), same cause. All four go to a default-fidelity task (14 MeV
  compound proton/alpha emission, U-238 default level density / fission), which B6/B7 should not mistake for theirs.
* Tests: `tests/hf/test_kwcov_b5.py` (forms, refusals, inert keywords, racap deck logic, a level file through
  `discrete_levels`, global vs per-nucleus precedence).

### B6 -- model keywords: optical model, direct

`optmodall` first (refused since B5: no engine code read it; stock Au-197 1 MeV capture +93 %). Once it acts, the deck
`racap y; optmodall y` reaches TALYS's own direct-capture path and `racap` can be checked end to end.
`vinfadjust` opticalnp.f90; `incadjust` ompadjust.f90; the 12 `*adjustf` keywords (`ompadjustF`, opticalcomp.f90,
opticalnp.f90, `adjustf.f90:1`); `riplomp` omppar.f90 + riplomp_mod.f90; `optmod*`/`ompenergyfile` external OMP
files (omppar.f90, `convert.f90`); `coulomb`, `ecisstep` incidentecis.f90; `eciscompound` comptarget.f90
(ECIS compound); `rotational`, `sysreaction` (directmodel). Accept: response metric on Fe-56 (spherical) and
U-238 (coupled), reaction and total cross section 1 %.

**Done on branch `kwcov6`** (kwcov4 + kwcov2 + kwcov5 merged). New modules `physics/hf/omp/ompdeck.py` (files, ranges,
energy-local adjustments) and `physics/hf/compound/ompall.py` (`optmodall`); small hooks in fitlib, defaults,
omp/parameters, omp_nx2, dens_reference, feeding, compound/chain, engine_c, stagedisk, record/caches.

* **Now acting:**
  * `optmodall y`: every compound nucleus of the cascade decays through transmission coefficients on its own residuals
    (`dens_reference._transmission_build(cn=...)`), and the PRIMARY decay of the initial compound nucleus at the 2nd and
    later incident energies uses the set TALYS reads at the top of the energy loop, before `energies`: Tl and lmax are
    filled only up to the PREVIOUS energy's eend (inverseread.f90), lmax = 0 above it. **TALYS-2.25 behaviour, found with
    a debug build of stock TALYS** (print of lmax(1, :) after `energies`: Au-197 at 1 MeV after 0.1 MeV has lmax 0 above
    node 7 = eend(0.1 MeV)). A one-energy run is unchanged by `optmodall y` (stock Au-197 at 1 MeV alone: capture
    145.65 mb both ways); the same 1 MeV after a 0.1 MeV energy: 144 -> 277 mb. The engine reproduces it; the C cascade
    has one stack, so `optmodall y` runs the Python cascade (slower).
  * `optmod Z A file [p]` (table read as omppar.f90:243-277, header Ef honoured, explicit table wins over the RIPL
    default), `optmodfilen Z file`, `optmodfilep Z file` (element files, also for elements without a database file).
  * the 12 `*adjustF p E1 E2 D s` ranges (s required, as TALYS), written into `Params.ompadjustE1/E2/D/s`.
  * the energy-local forms of the 28 ompadjust keywords: `v1adjust n 1. Ea Eb Em D` and `awdadjust n 1. <table>`
    (adjust.f90 shape / linear table, depth = value x D, last covering line wins), applied by TALYS's ktype rule: the
    bump of particle k acts on the incident channel (with `incadjust y`) and on outgoing particles OTHER than the
    projectile (the projectile leaving takes type 0, flagompejec). Files: cwd, then the best file's directory and its
    `misc/tables`, case-insensitive. A word with `/` is a file too (TALYS would read it as a number and drop the bump).
  * `incadjust n` (projectile's ompadjust factors and bumps act nowhere), `riplomp n` / `riplomp <p> <iref>`.
  * `vinfadjust` (already consumed; acts above Ejoin = 200 MeV only), `coulomb n` (no Coulomb excitation, which the
    port's ECIS never had), `eciscompound` (reference-only ECIS run in TALYS: NA), `ompenergyfile` (accepted; read by
    TALYS only with `endf y`).
* **Refused (`defaults.UNPORTED`):** `statepot y`, `rotational <particles>`, `sysreaction <particles>`, `ecisstep` != 0,
  `ompenergyfile` with `endf y`.
* **Merge fix:** deck lines with several words for an Options keyword (`fileddxa n 30`, B4) were refused by B2's
  fitlib after the merge; `_MULTIWORD` lets the multi-word kinds through.
* **Response vs stock** (`scripts/kwcov/b6_response.py`; stock runs trimmed in `~/kwcov/stock/b6_*`):
  | deck lines | target | worst (stock moved) | | deck lines | target | worst (stock moved) |
  |---|---|---|---|---|---|---|
  | awdadjustF n 2 20 10 0 | Fe-56 | 0.10 % (4.0 %) | | optmod 26 56 (Wd x1.15 table) | Fe-56 | 0.15 % (8.2 %) |
  | rvadjustF n 1 20 3 0 | Fe-56 | 0.04 % (5.7 %) | | optmodfilen 26 (v1 +2, d1 x1.1) | Fe-56 | 0.17 % (13 %) |
  | rvadjustF p 1 20 5 0 | Fe-56 | 0.12 % (3.8 %) | | optmodfilep 25 (Mn file) | Fe-56 | 0.86 % (8.2 %) |
  | v1adjust n 1. 3 16 10 1.03 | Fe-56 | 0.00 % (1.0 %) | | coulomb n / vinfadjust n 1.2 / eciscompound y | Fe-56 | 0.00 % (0 %) |
  | d1adjust p 1. 1 15 8 1.2 | Fe-56 | 0.01 % (0.4 %) | | optmod 92 238 n-U238.omp | U-238 | 0.09 % (4.6 %) |
  | awdadjust n 1. awdadjust-n.table | Fe-56 | 0.25 % (11 %) | | riplomp n | U-238 | 0.38 % (48 %) |
  | incadjust n; v1adjust n 1.02; d1adjust p 1.1 | Fe-56 | 0.09 % (3.1 %) | | awdadjustF n 2 20 10 0 | U-238 | 0.14 % (5.8 %) |
  | **optmodall y** | Fe-56 | **6.9 %** (n,a) 14 MeV (106 %) | | optmodall y | U-238 | 1.1 % (25 %) |
  | **optmodall y** (0.01/0.1/1/5 MeV) | Au-197 | **51 %** capture 1 MeV (66 %) | | racap y; optmodall y | Au-197 | direct capture = stock (133.6 mb at 1 MeV) |
  | **best y** | Fe-56 | **6.7 %** (n,np) 14 MeV | | **best y** | U-238 | **9.2 %** fission 5 MeV |

  Losses, traced. `best y`: the B6 lines in the best files now act (Fe-56 awdadjust table, U-238 n-U238.omp), and
  the same deck WITHOUT them misses by the same amount (Fe-56 6.8 %, U-238 9.2 %): what is left is outside B6 (B5's
  default-fidelity task: 14 MeV (n,p)/(n,a) excess; U-238 level density / fission). `optmodall y` Fe-56: stock moves
  (n,a) at 14 MeV to 0.35x, the engine to 0.32x; the miss is on the charged-particle channels the engine already
  over-predicts at 14 MeV. Au-197: the engine's DEFAULT 1 MeV run is far from stock (capture 104 vs 144 mb,
  inelastic 2004 vs 1734 mb) and most of its inelastic does not go through the first compound nucleus's neutron exits
  (with every one of them zeroed the engine still has 1877 mb inelastic), so the exits TALYS's stale set cuts carry
  less flux in the engine: capture x1.16 vs stock x1.93. A default-fidelity item (Au-197 1 MeV channel composition),
  not the keyword. Also found: with `racap y` the isomer split `xs000000.L00` (CHANOBS extras) does not get the
  direct-capture addend (racapcalc.add_to_results adds it to xs000000 only).
* Tests: `tests/hf/test_kwcov_b6.py` (forms, refusals, adjust.f90 shape, ktype/incadjust, ranges, optmod, optmodfile,
  riplomp, multi-word deck lines, optmodall cut/eend/Python cascade).

### B7 / B7b -- unported model branches (B7 done on branch `kwcov7`; B7b open)

* **Ported** (all default-off: a run without them never enters the new code; Fe-56 611 and U-238 692 `Results` arrays
  as before, `test_engine_c.py`). `physics/hf/preeq/exciton_b7.py` transcribes, one exciton state at a time (numpy
  over the emission grid and the `nexcbins` points), the branches the vectorised `preeq/exciton.py` does not carry;
  `exciton_model` hands a run to it when one of the three switches below is set (`PreeqInputs.b7`, built in
  `preeq/prepare.py`). With all switches off it reproduces the vectorised emission and transition rates to 1e-16
  (preeqmode 1 and 2; `test_kwcov_b7.py`), the check that it is the same physics.
  * `twocomponent n`: one-component exciton model (exciton.f90, emissionrate.f90 with `Qfactor`, lambdaplus.f90,
    lifetime.f90, matrix.f90's 0.5, phdens.f90).
  * `gshell y`: g damped by ignatyuk(E)/alev in the emission and transition rates of both models, with TALYS's
    quirks (each numerical rate damps all four collision densities with g of its FIRST channel's energy;
    lambdanupi damps its residual with g(uu), not g(U - uu); the Pauli tables keep the undamped g).
  * `preeqmode 3`: optical-model transition rates; bonetti.f90's `wvol` (the target's W + surface Wd averaged over
    the Woods-Saxon volume, n and p, -8 MeV .. emax) through `omp.parameters.omp_parameters`.
  * `preeqspin 3` (= `preeqspin y`) and `preeqspin 4` (Wigner, newspin.f90, now in `preeq/spin.py`): the exciton
    model's J shares (`exciton.spin_fraction`: xspreeqJP = xs 0.5 (2J+1) RnJ/RnJsum, scaled as xspreeq through
    preeqcomplex/preeqcorrect/preeqtotal) go to population.f90 (`feed_reference._spin_inputs`: xspreeqJP, the
    collective continuum's xscollcontJP, the giant resonances' xsgrstate by multipolarity) and its `preeqpop` is
    added by binary.f90 (`BinaryInputs.preeqpop_mb`, `binary.py`; the C binary kernels hand such a run to it).
    `preeqspin y/n` is read as TALYS does (y = 3, n = 1).
* **Bugs found.** `preeqmode 4` (MSD) was accepted and ran the exciton model with the analytic rates, without MSD
  (stock Fe-56 14 MeV: (n,p) +32 %, engine -2.5 %): now refused. `preeqspin 4` ran with NO pre-equilibrium flux in
  the binary population (binary.py adds it only for pespinmodel <= 2): now ported. The inventory had `onestep`,
  `emsdmin`, `msdbins` as IGNORED: they act only inside MSD in TALYS too (inert, SUPPORTED with that note).
* **Refused, with what is left:**
  * `preeqmode 4` (MSD/MSC): msd.f90, msdinit, the continuum DWBA of dwbaecis.f90 (ECIS per outgoing-energy pair),
    onestepA/B, onecontinuumA/B, multistepA/B, msdcalc/msdtotal/msdplusmsc, cmsd; several days with the ECIS port.
  * `gnorm y`: TALYS-2.25 compares its theoretical <Gamma_gamma> (eV) with the resonance table's number in keV
    (resonancepar.f90:96), so radwidtheory.f90's iteration drives the compound nucleus's E1 `ftable` to 0 (stock
    Fe-57: 1.30 eV vs 9.2e-4, E1 ftable printed 0, C/E 120 from M1/E2; capture 1 MeV -70 %, 14 MeV -99 %; Zr-91
    capture 1 MeV -54 %). Left: call `gamma.transmission.radwidtheory(flaggnorm=True)` with TALYS's gamgam (past its
    GAMGAM_MIN_EV guard) before the run, again per incident energy as incident.f90:90 does, and feed the final
    ftable(E1) of the compound nucleus to every strength user (PARAMWIRE's ftable path). Reproducing it means
    reproducing the unit bug; `ftable Z A f` is the physical alternative.
  * `twocomponent n` or `gshell y` with multiple pre-equilibrium (Einc >= `multipreeq` onset, 20 MeV):
    multipreeq.f90 (one-component chain) is not ported, and the shell damping is not wired into multipreeq2's
    cascade (`MultiPreeqInputs.damp` exists, `Cascade.mpe_inputs` does not fill it); refused in
    `feed_reference.pop_inputs_of` with the reason. `preeqspin 4` with multiple pre-equilibrium likewise.
  * `preeqspin 3` on the GPU path (`gpu_full_setup`): refused (engine_c has it).
  * B7b (`alphaomp 3-5`, JLM) untouched.
* **Response vs stock** (`scripts/kwcov/b7_response.py`, n + target at 1/5/14 MeV, channels of b2_response plus
  nprod/pprod/aprod; `--pe` compares the binary pre-equilibrium totals with stock `preeq*.out`; stock JSON in
  `~/kwcov/stock/b7`):

  | deck lines | Fe-56 worst (stock moved) | Zr-90 worst (stock moved) |
  |---|---|---|
  | twocomponent n | 0.49 % (16.9 %) | 0.39 % (16.5 %) |
  | gshell y | 0.39 % (17.9 %) | 0.50 % (14.9 %) |
  | preeqspin 3 (= y) | 0.44 % (4.4 %) | 0.88 % (11.6 %) |
  | preeqspin 4 | 0.35 % (3.5 %) | -- |
  | **preeqmode 3** | **4.81 %** (n,d) 14 MeV (46 %) | **5.98 %** (n,p) 14 MeV (58 %) |
  | twocomponent n; preeqspin 3 | 0.49 % (17.1 %) | -- |
  | twocomponent n; preeqmode 3; gshell y | 0.61 % (8.6 %) | -- |
  | twocomponent n; preeqmode 1 | 0.71 % (7.4 %) | -- |
  | preeqmode 1 (already ported, check) | 0.25 % (16.2 %) | -- |

  preeqmode 3, traced: the transition rates equal stock's exciton0014.000.out to 1e-6 and the binary
  pre-equilibrium totals to 1e-4 (Fe-56 14 MeV n 77.029 vs 77.027 mb, p 5.8168 vs 5.8167), and the channels move by
  the same millibarns: Fe-56 (n,d) -1.01 vs -1.04 mb, Zr-90 (n,p) -12.60 vs -12.86 mb (2 %). The relative gap is the
  engine's default 14 MeV (n,p)/(n,d) excess (B5): preeqmode 3 moves ~200 mb of Fe-56 pre-equilibrium flux back to
  the compound nucleus, which the engine decays into protons ~15 % more than stock (Fe-56 (n,p) +5.21 vs +1.98 mb
  for -17.5 mb of PE protons on both sides). Same cause, smaller, in the other rows' (n,p) mb.
  The pre-equilibrium totals of twocomponent n and gshell y also equal stock's preeq file to 1e-4 (test_kwcov_b7.py).
* Tests: `tests/hf/test_kwcov_b7.py` (transcription = vectorised path, preeqmode 3 rates and PE totals = stock,
  parsing, refusals, the giant-resonance J map); `test_unported_options.py` updated.

### B8 -- fission extras

Per-fissioning-nucleus fission (`rpZZZAAA.fis`, `finalout.f90:396`), `fisfeed`, `rfiseps`, `axtype`
(`colenhance.f90`, densitypar), `class2file`, `hbtransfile` (`fissionpar.f90`), `cnubar1/2` + `nubarWahl.f90:1`,
PFNS Iwamoto (`iwamoto.f90:1`, `pfnsout.f90:1`, `tmadjust`, `fsadjust`). Accept: U-238 and Th-232 at 1, 5, 14 MeV:
per-chance fission vs stock within the engine's own (n,f) band; nubar 0.5 %; PFNS mean energy 1 %, shape 3 %.

**Done on branch `kwcov8`** (kwcov7 + kwcov6 merged). New module `physics/hf/fisobs.py` (output only); small hooks in
engine_c (`cases`: `fisobs.begin_run` / `record` per kept energy off the cascade result, the arena read with
`_Packed.result()` on the C path; `run`: `fisobs.add_to_results`), input/defaults (Options `filefission`,
`flagfisout`, `axtype_of`, `fisstates_file_of`; per-nucleus forms `axtype`, `hbtransfile`, `class2file`), fitlib
(deck forms) and fission/parameters (the states files). With none of the switches set nothing is recorded:
U-238 1/5/14 MeV, all 692 `Results` arrays bitwise equal to the merge commit; `test_engine_c.py` passes.

* **Now acting:**
  * Switches: `filefission y`, `fisfeed y`, `outfission y`, an explicit `pfnsmodel`, `cnubar1/2`, `tmadjust`,
    `fsadjust` != 1, or the port switch `INCOGNITA_FISOBS=1`, on a fission run. TALYS writes the PFNS of every fission
    run and the per-nucleus files with `channels y`; the port keeps defaults unchanged and asks for a switch (decision,
    as CHANOBS / SPECOBS). `endf y` sets filefission and outfission as TALYS does.
  * `Results.extras['rpZZZAAA.fis']` (fissionout.f90, xsfeed(Z, N, -1); sums to fission.tot to 1e-12),
    `Results.spectra['fisZZZAAA.feed', ':Ex']` (fisfeed, multiple.f90:884: the Ex and Population columns, the
    initial compound nucleus with the binary fission as its top row), `Results.spectra['pfns.fis', ':E',
    ':Maxwell_ratio', ':CM']` + `extras['pfns.fis:E-average']` (iwamoto.f90 in single precision, strucinitial's 293-point
    grid), `extras['nubarn.tot:wahl']` (nubarWahl.f90).
  * `axtype Z A type [ibar]` (class 4, ibar 1 when absent; range 1-4), `hbtransfile Z A <file>`,
    `class2file Z A <file>` (class 11; read with `hbstate y` / `class2 y` as TALYS; a missing file stops the run).
  * `tmadjust`, `fsadjust`, `cnubar1`, `cnubar2` (range 0.1-10), `pfnsmodel` (1-2), `rfiseps` (0-1) checked as
    checkvalue.f90. `rfiseps` acts only in massdis/ffevap (B14): inert, as stock (U-238 `rfiseps 0.01`: nothing moves).
    `pfnsmodel 2` gives no Iwamoto spectrum, as stock without massdis.
* **TALYS-2.25 finding:** the Wahl nubar is computed (totalxs.f90:124) and never written: massdis.f90:252 resets
  `nubar` before nubarout, and nubarout runs only from massdis (fymodel 2) and ffevap. So `cnubar1/2` change no stock
  output; the port's `nubarn.tot:wahl` is their only reader (transcription checked by hand in the test).
* **Before B8:** `cnubar1/2`, `tmadjust`, `fsadjust`, `rfiseps`, `fisfeed` were read and ignored; `axtype`,
  `hbtransfile`, `class2file` deck lines were refused as unknown per-nucleus forms; `filefission`/`outfission` NA.
* **Not given (PARTIAL):** the J-parity columns of the fisfeed file (fisfeedJP; the decay kernels sum the fission feed
  over J and parity); the talys.out barrier / transmission tables of `outfission` (ingredients.py, as before);
  fragment-based nubar, nu(A), P(nu), PFGS, `pfnsmodel 2` with massdis (B14).
* **Observables vs stock** (`scripts/kwcov/b8_response.py`; stock JSON trimmed in `~/kwcov/stock/b8/b8_*.json`, states
  files in `~/kwcov/stock/b8_files`): PFNS of U-238, U-235, Pu-239, Th-232 at 1/5/14 MeV, also with `tmadjust 1.3`,
  `fsadjust 3`, `tmadjust 0.8; fsadjust 2`: same grid, E-average to 1e-5, spectrum / Maxwell ratio / CM to 2e-5 where
  above 1e-3 of the peak. Per-nucleus fission within the engine's own (n,f) difference: U-238 (fission -6.0 / +9.2 /
  +4.2 % at 1/5/14 MeV) U-239 -6.0 / +9.8 / +7.5 %, U-238 +6.1 / +4.7 %, U-237 -0.5 %; U-235 (+0.2 / +2.1 / +0.6 %)
  U-236 -0.1 / -0.3 %, U-235 +17.6 % (5 MeV, 173 vs 145 mb) / +1.6 %, U-234 -3.5 %; Pu-239 (-1.0 / -0.3 / -0.4 %)
  all nuclides within 1.3 % but Pu-239 at 5 MeV (3.9 vs 3.8 mb); Th-232 (+1.9 / +20 / +10 %) Th-233 +27 % at 14 MeV.
  fisfeed: same files and rows as stock; each population sums to its rpZZZAAA.fis; the top row (binary fission)
  follows the per-nucleus number.
* **Response vs stock** (from the plain deck unless noted; U-238 at 1/5/14 MeV):

  | deck lines | worst |ln(R/S)| (stock moved) | millibarns |
  |---|---|---|
  | axtype 92 239 2 1 | 0.42 % (8.2 %) | |
  | axtype 92 238 3 1 | 1.24 % (10.4 %) | |
  | **axtype 92 239 3 2** | **4.66 %** rp092239.fis 5 MeV (x2.6) | +886 vs +867 mb (2.2 %) |
  | **axtype 90 233 3 2** (Th-232) | **12.1 %** rp090233.fis 14 MeV (x2.8) | fission 5 MeV +1081 vs +1032 mb (4.8 %) |
  | hbstate y (existing) | 0.73 % (56 %) | |
  | hbtransfile 92 239 hb_u239.eo, from `hbstate y` | 1.93 % (61 %) | fission 1 MeV -36.3 vs -39.3 mb |
  | **class2 y** (existing) | **6.2 %** rp092238.fis 5 MeV (x4) | +291 vs +297 mb (2.2 %) |
  | class2file 92 239 c2_u239.eo, from `class2 y` | 0.67 % (5.9 %) | |
  | tmadjust 1.3, fsadjust 3, rfiseps 0.01, pfnsmodel 2 | 0.00 % (0 %) | |

  Losses, traced: the relative misses are large moves on top of the engine's default fission, which is high where the
  big axtype / class2 moves act (U-238 +9 % at 5 MeV, Th-232 +20 %): fission and inelastic share a fixed nonelastic,
  so a fission that starts high gains less relatively. In millibarns the moves agree to 2-5 %. Th-232 is the worst
  case because its default is the furthest off (default-fidelity, the separate fission task).
* Tests: `tests/hf/test_kwcov_b8.py` (Iwamoto and grid vs stock numbers, Wahl by hand, switches, deck forms, ranges,
  states files, output-only on/off at U-238 5 MeV with the sums).

### B9 -- astrophysics

Exists: `astro/stellar.py` (thermalised target, SEF; `INCOGNITA_STELLAR`). Do: `astro y` and the `astro*` keywords
drive it; reaction rate files and MACS as TALYS writes them (`astroout.f90:1`, `stellarrate.f90:1`,
`partfunc.f90:1`), `nonthermlev`. Accept: Au-197 and Ge-74 rates at T9 = 0.1-10 and MACS at 30 keV vs stock 2 %.

**Done (branch `kwcov9`).**

* **What.** A deck with `astro y`, `astroE` or `astroT` (`input/deck.py run_deck`, C driver) runs on TALYS's own
  incident grid (egridastro: = stock, 110 energies 2 eV - 50 MeV for n + Au-197; `astroE`/`astroT`: one temperature,
  grid to 50 kT) and returns `Results.astro` = astroout's files as {file: {column: array}}: `astrorate.g/p/a(/f)`,
  `astrorate.tot`, `astrorateZZZAAA.tot`, with `astroex y` the `.LNN` level files (isomer populations from CHANOBS),
  with `astroE 0.029-0.031` `macs.g` (Exp column from structure/gamma/macs). `astro/rates.py` = egridastro (T9 and
  energy grids), partfunc (G(T), `nonthermlev`), stellarrate (rates, MACS: centre-of-mass Maxwellian, TALYS's
  half-interval sum), astroout; `rates.write_files` writes them. `astro/thermal.py` = the thermalised target of
  `astrogs n` (TALYS's default with astro y) INSIDE the run: astrotarget/astroprepare (lumped incident and exit
  channels, Moldauer W, the "elastic" (W_el + (rho-1) W_inel)/rho) while width fluctuations are on;
  compprepare's astro feed + comptarget's sumIPas subtraction (J2end = 2 numJ) when they are off; and
  comptarget.f90:803 (after the first WFC energy with more than 3 target bins open, ewfc = Einc: WFC off for every
  later energy, ground state included; `Cascade.astro_ewfc_mev`). Keywords: `astroe`/`astrot` are new Options
  (`astroE`, `astroT9`; they set astro y, astroE also astrogs y), ranges and `astroE` OR `astroT` and `segment 1`
  checked as checkvalue.f90.
* **Defaults untouched**: nothing runs unless the deck asks for astro (`Results.astro` empty; the thermal hook,
  the ewfc override and the partition-function record are all behind `options.flagastro`).
* **Refused:** `astro y` + `racap y` (stellarrate's separate direct-capture rate, iloop 3); `astrogs n` on a
  fissile target (astrotarget.f90:68 calls tfission with the TARGET level index as the compound-nucleus bin, a
  TALYS bug not reproduced; astrogs y works); `astrogs n` with widthmode 2/3; `astrogs n` on the Python driver
  (`engine.run`).
* **TALYS quirks kept** (ported as written): astrotarget's elastic sumIPE adds `suminl` without CNfactor (2J+1);
  without WFC sumIPas = CNfactor (2J+1) enumhf^2/denomhf is subtracted from sumIPE of every type-k0 exit including
  the ground state (whose compound elastic is already left out); J2cnend = 2 (lmaxhf + 1/2 + Ir) with the integer
  Ir (one J short for odd-A targets), capped at numJ = 40; partfunc's continuum trapezoid starts from the last
  discrete level's term; the elastic/last-cell test of astrotarget uses the last (P', Ir) visited.
* **Bug fixed on the way:** the deck keyword `transeps` (and astro y's 1e-18, massdis y's 1e-12) reached `Options`
  but never the chain: `Cascade.transeps` was the constructor default 1e-8. Now taken from Options unless a caller
  passes its own (`emission/feeding.py`); default runs unchanged (both 1e-8).
* **Vs stock** (`scripts/kwcov/b9_response.py`, `b9_table.py`; |ln(ours/stock)| max over T9 1e-4..10 where stock
  > 1e-6 of its column maximum; response = (astro y) / (astro y; astrogs y), the stellar enhancement):

  | deck | (n,g) rate / MACS | G(T) | (n,n) | (n,p) | (n,a) | response (n,g) | response other |
  |---|---|---|---|---|---|---|---|
  | Fe-56 astro y astrogs y | 0.06 % | 1 | 0.04 % | 2.3 % | 2.8 % | | |
  | Fe-56 astro y | 1.27 % | 1.35 % (T9 10) | 0.9 % | 0.6 % | 0.4 % | **1.25 %** | (n,n) 0.9, (n,p) 1.7, (n,a) 2.25 % |
  | Ge-74 astro y astrogs y | 0.13 % | 1 | 0.10 % | 0.01 % | 2.8 % | | |
  | Ge-74 astro y | 1.17 % | 0.00 % | 1.5 % | 0.01 % | 0.4 % | **1.04 %** | (n,n) 2.6, (n,a) 2.4 % (rate ~1 cm3/mol/s) |
  | Au-197 astroE 0.03 (macs.g) | **0.48 %** (929.9 vs 934.4 mb) | 1 | 79 % | = | floor | | |
  | Au-197 astroT 0.348 (30 keV, thermal) | **0.24 %** | 0.00 % | 122 % | = | floor | | |
  | Au-197 + nonthermlev 1 | 0.24 % | 0.00 % | | | | **0.00 %** (x1.038) | all 0.00 % |
  | Au-197 + astroex y | g.L00 0.24 %, g.L30 (Au-198m) 3.6 % | | | | | | |
  | Au-197 astro y astrogs y | 1e-5 at T9 <= 0.1; 0.3 % at 0.3; 2.8 % at 1; 24 % at 10 | 1 | 90 % | 27 % | floor | | |
  | Au-197 astro y | 0.15 % at T9 0.3; 2.3 % at 1; 8.7 % at 3 | 0.00 % to T9 3, 10 % at T9 >= 7 | 129 % | 10 % | 160 % | **21 % (T9 4)**, 0.6 % at 30 keV | |

  Residual products of astrorate.tot (Fe55, Mn54, Pt195 ...) with rates of 1e-12 - 1 cm3/mol/s follow the engine's
  multi-particle channels at high T and are not part of the acceptance.
* **Losses, traced.** (1) Au-197 above T9 ~ 0.5: the ENGINE's default n + Au-197 differs from stock above 0.1 MeV,
  not the astro port: in a plain deck at 0.1-0.3 MeV the engine's (n,n') (rp079197) is ~2x stock (388 vs 157-242
  mb), its (n,g) at 1 MeV 104 vs 144 mb (-27 %). The rate arithmetic is exact where the capture agrees (MACS 1e-5 at
  T9 <= 0.1) and G(T) is exact to T9 = 3; the stellar response follows the excited-state neutron widths, which
  carry the same excess (a default-fidelity item for the fidelity task, not B9). (2) G(T) at T9 >= 5 (Au-197 +10 %,
  Fe-56 1.35 %): the continuum part of the partition function = the engine's level density 10-50 MeV and its
  last-energy bins. (3) (n,a)/(n,p) "floor" rows: the engine's keV-energy (n,a) on Au-197 is 0 (rate = xseps
  floor 1.7e-12) where stock has 4e-7; 1e-15 of the capture rate.
* **INCOGNITA vs TALYS astro (deliberate, recorded):** the published library's MACS and rates (scripts/release
  v0.2.1-v0.2.3) do NOT come from this path and are unchanged by it: they integrate the ground-state capture curve
  (= TALYS `astrogs y`, no partition function, no stellar enhancement), with the same centre-of-mass definition as
  stellarrate (sigma at E_lab, E = E_lab M/(M + m_n)), but exactly (log-log between the grid points, Gauss-Legendre)
  on the 64/134-point production grid with the engine's own capture below 1 keV (v0.2.2) and the AME2020 reduced
  mass, where TALYS sums half-interval rectangles on its astro grid from 2 eV with its own redumass. The library's
  capture runs keep width fluctuations up to S_n; TALYS's astro y (astrogs n) switches them off above 3 open target
  levels (Au-197 above 0.30 MeV, Fe-56 above 2.7 MeV), a TALYS quirk the library does not take. `astro/stellar.py`
  (INCOGNITA_STELLAR, the SEF study) stays a separate, non-lumped method (full HF+WFC per entrance level, partition
  function cut at 3 MeV) and is not what `astro y` runs.
* Tests: `tests/hf/test_kwcov_b9.py` (grids vs stock, constant-sigma MACS, partition function by hand, macs file,
  file round trip, keyword parsing and refusals, the transeps fix, the ewfc override default, Au-197 astroE 0.03 run
  vs stock macs.g).

### B10 / B10b -- low energy

URR: `urr.f90:1`, `urrout.f90:1` (`urr`, `lurr`, `urrnjoy`, `rprime`). Thermal: `thermal.f90:1`,
`thermalxs.f90:1`. Natural targets: `natural.f90:1` (loop over isotopes, `abundance`). Resonance range:
`resonance.f90:1`, `integral.f90:1` (needs external resonance libraries, lowest priority).
Accept: U-238 and Fe-56 URR parameters vs stock 1 %; natural Fe = abundance-weighted sum 1e-6.

**B10 done (branch `kwcov10`, from kwcov9).** B10b (thermal, natural targets, resonance range) stays open.

* **What.** New module `physics/hf/urr.py` (output only): comptarget.f90's two "Gilles Noguere" blocks (per compound
  (J, parity) and incident (l, j) with l <= lurr: sumIPE per exit type without compound elastic, Turrlj = sumIPE
  denomhf / (CNfactor (2J+1) Tinc Wab), xsbinarylj, nulj, Turrljinc, Purrlj, the (l, J) range that grows over the
  run's energies), dtheory's D(l, J), strengthfunc, urr.f90 (widths D T / 2 pi, Gn = D S 1e-4, the NJOY Gx/Gf
  renormalisation loop with csunr2 + unfac + gnrl, the TALYS and NJOY sums), urrout.f90's files and thermalxs.f90's
  xscaptherm(-1) (the urr.dat header). `Results.urr` = {file: {column: array}} with TALYS's file names: `urr.dat`,
  `urr<fis|gam|com|neu|pro|alp>width.lLL`, `urrspacingl(j).lLL`, `urrneustrengthl(j).lLL`, `urrtalys.tot`, with
  `urrnjoy y` also `urrnjoy.tot`, `urrratio.tot`; `urr.write_files` writes them. Hooks: `engine_c.cases` and the
  Python driver's `ChainedFull.cases` call `urr.record` at Einc <= eurr (a fresh `compound_inputs`, as B9's astro
  hook), `run` adds `Results.urr`. Per incident channel the Moldauer sums are `wfc.moldauer_sums` with a one-hot
  incident vector (they are linear in it).
* **TALYS quirk kept:** `Wab` in Turrlj is the factor of the LAST widthfluc call before a type's loop ends (the last
  exit channel visited in TALYS's loop order, including the elastic level; W(a, gamma) for photons; the last fission
  hill with a non-zero ratio), not a channel average. Without it Gg/Gx/Gf are off by the WFC factor of that channel.
* **Defaults bit-identical**: nothing runs unless `urr y` / `urr <E>` / `endf y` (A > 20); `test_engine_c.py` passes. In
  TALYS too URR is output only: with and without `urr y`, Fe-56 552 and U-238 600 engine `Results` arrays are bitwise
  equal and stock's channels identical (`b10_response.py --unmoved`).
* **Refused:** `urr` with widthmode 2 / 3 at an energy with width fluctuations (HRTW/GOE per-incident-channel factors
  not separated here), with INCOGNITA_EWFC on a coupled target, with the KEVCOLD cell options. checkvalue's `lurr`
  0-60, `rprime` 0-10, incident neutrons only, compound model on.
* **Vs stock** (`scripts/kwcov/b10_response.py`, energies 0.01 0.1 1 5 MeV, stock JSON in `~/kwcov/stock/b10`; every
  number of every urr file where stock > 1e-6 of its column maximum, same files and rows):

  | deck | default mode | TALYS mode | worst (TALYS mode) |
  |---|---|---|---|
  | Fe-56 `urr y` (+ `urrnjoy y`) | 5e-5 (7e-5) | same | capture 5 MeV (Gx 5 MeV) |
  | Co-59 `urr y; urrnjoy y` | 1.0e-4 | 1.0e-4 | Gx 5 MeV |
  | U-238 `urr y` (+ `urrnjoy y`) | **22 %** Gf (EXACTFIS), Ga 9e-10 vs 0 eV | **0.11 %** | Gg 1 MeV = the engine's own (n,g) at 1 MeV (65.28 vs 65.21 mb) |
  | Au-197 `urr y; urrnjoy y` | **x2.0** Gx, capture **-30 %** (CCEXITNB2) | **2e-4** | Gx 1 MeV |
  | `urr 0.5` (onset): Fe-56 / U-238 | | 4e-6 / 8e-5 | |

  Keyword responses (TALYS mode, |ln(R/S)| or the same absolute change): `urrnjoy y` Fe-56 7e-5, U-238 2.8e-4 (Gx);
  `lurr 0` / `1` Fe-56 1e-5 / 7e-6, U-238 8e-5 / 1.5e-5; `lurr 3` the l03 files = stock to 3e-5; `rprime 7` (with
  urrnjoy) Fe-56 6e-7, U-238 6e-6. Default mode differs only through EXACTFIS (U-238 Gf, fission sums) and CCEXITNB2
  (Au-197 competitive width and capture), FIDELITY_DEFAULTS.md's deliberate defaults.
* **INCOGNITA vs TALYS URR (recorded, not touched).** The published/reactor library's URR is not this path: the
  research repo's REACTORLIB `urr_build.py` (URRPROD) writes ENDF MF2 LRU=2 LRF=2 LSSF=1 from engine ingredients, with
  D(l,J) from an Ericson spin distribution and an analytic energy dependence (TALYS: the full level density at S_n +
  Einc per (J, parity)), <Gn> from the OMP S0/S1 with R = 1.35 A^(1/3) and S2 := S0 (TALYS: Tjlinc per (l, j) with the
  ENDF radius 1.23 A^(1/3) + 0.8), <Gg> = the engine's energy-independent gamgam_th s/p (TALYS: D Turrlj(0) / 2 pi from
  the capture sums, energy dependent and divided by the last Wab), <Gf> = the T_f(J) shape scaled to the engine's
  sigma_f (TALYS: D Turrlj(-1) / 2 pi), Gx fitted to the inelastic with AMUX 4 (TALYS: nu = 1), AP = R'(1 keV) (TALYS
  NJOY: R' of the first URR energy). The LSSF <Gamma_gamma> closure work stays in the research repo. B10's files
  change none of it.
* **Not given:** energies below eninclow (Ninclow > 0; urrout fills their rows from the current energy; the port has
  no Ninclow energies: B10b); thermal.f90 (B10b). Observed: a second `run_deck` with a different deck in the same
  process needs `chartrun.drop_target_caches()` first (the cached Cascade keeps the first deck's Options; the test
  does it; not chased).
* Tests: `tests/hf/test_kwcov_b10.py` (gnrl / unfac / strengthfunc by hand, keyword parsing, refusals, defaults record
  nothing, thermal capture table, Fe-56 run vs stock numbers with every cross section bitwise unchanged).

### B11 -- medical isotope production

`prodinitial.f90:1`, `prodrates.f90:1`, `prodyield.f90:1`, `prodout.f90:1`, decay data `decaydata.f90:1`.
Post-processing of residual (and isomer) production -- needs B1-style isomer output and RESISO on.
Accept: p + Ni-nat or Zn-68 (p,x) yields/activities vs stock 1 % given the same residual production.

**Done (branch `kwcov11`).**

* **What.** `physics/hf/production.py` = isoprod.f90 (prodinitial, decaydata, prodres, stoppingpower, prodrates,
  prodyield, prodout) on the run's residual production. `production y` and the medical keywords are Options
  (`Ebeam`, `Eback`, `Ibeam`, `Area`, `rhotarget`, `radiounit`, `yieldunit`, `Tirrad`/`unitTirrad`,
  `Tcool`/`unitTcool`; `tirrad 2 d 6 h` = kind `medtime`, up to five value/unit pairs); before B11 every one of them
  except `production` was refused on a deck line. Both drivers check the input at the start of the run
  (checkvalue.f90:497-552: Ebeam given and inside the run's grid, Eback default max(Ebeam - 5, 0.1), units, ranges)
  and fill `Results.production` at the end = {"files": Y<ZZZ><AAA>.tot/.L00/.L<NN> columns Time, Activity,
  Isotopes, Yield, Isotopic_fract.; "params": the Y-file header numbers; "summary": the talys.out table; "meta":
  target thickness/volume/mass, projectiles per second, heat, Ntar0, the total rate}. `INCOGNITA_PRODUCTION_DIR`
  writes the Y files (`INCOGNITA_PRODUCTION_BLOCK=1` = blockyield's one Y.tot; the deck keyword `blockyield` stays
  an NA output switch). The rp files TALYS reads back are the engine's `rpZZZAAA` and RESISO `rpZZZAAA.LNN` (on by
  default for charged projectiles) and the non-elastic, rounded to es15.6 as on file; half-lives and decay types
  from `structure/decay` (JEFF-3.1.1 ENDF-6 MF8, read as decaydata.f90 does).
* **Proton (and alpha) runs work**; nothing needed refusing. **Refused** as TALYS refuses: neutron and photon
  projectiles ("isotope production not yet enabled", checkvalue.f90:498), Ebeam missing or above the grid, Eback
  below it, unknown radiounit/yieldunit/time unit. Natural targets (`mass 0`, e.g. Ni-nat) stay refused by the deck
  reader (natural.f90 is B10b).
* **Defaults untouched**: nothing runs without `production y` (`begin_run` returns at once, `Results.production`
  empty).
* **TALYS quirks kept** (ported as written, checked against stock): one generation of beta feeding, with the
  daughter's isomer index for the parent; a beta- parent (Zix + 1) is processed after its daughter, so it feeds
  nothing during cooling; a nuclide counts as produced only with xs > 0 on a GRID point inside [Eback, Ebeam]; the
  target's L00 (if any) is subtracted from the non-elastic as well as its total; `Tcool 0` leaves the cooling grid at
  t = 0 and TALYS then prints Niso(EOI) exp(+lambda Tirr) and NaN isotopic fractions (0 x exp overflow) -- the port
  gives the same numbers and the same NaNs; a time value with no unit counts 0 s; `Area` does not change a
  thick-target yield (rate per atom ~ 1/Area, atoms ~ Area: stock 1.00015).
* **Vs stock** (`scripts/kwcov/b11_response.py --all`; stock runs `~/kwcov/stock/b11_*`, trimmed to Y/rp files and
  the talys.out table). *book* = the port on stock's OWN rp files vs stock's Y files (the bookkeeping alone);
  *abs* = engine run vs stock, activity (or isotopes if stable) at end of irradiation, worst over nuclides whose
  production rate agrees to 0.5 %; *resp* = |ln(R/S)| of activity/isotopes at end of irradiation and of cooling,
  over nuclides whose production rate agrees in both decks:

  | deck | book | abs | resp | | deck | book | abs | resp |
  |---|---|---|---|---|---|---|---|---|
  | p + Zn-68 E 18->10, 1 d / 1 d | 1.3e-4 * | 0.013 % | | | Zn-68 Tcool 0 | 1.3e-4 * | 0.013 % | 0.003 % |
  | Zn-68 Ibeam 0.5 | 3.3e-4 * | 0.013 % | 0.0000 % | | Zn-68 radiounit mbq / ci | 1.3e-4 * | 0.013 % | 0.0000 % |
  | Zn-68 Area 2.5 | 2.4e-4 * | 0.013 % | 0.0001 % | | Zn-68 yieldunit mg | 1.3e-4 * | 0.013 % | 0.0000 % |
  | Zn-68 rho 5 | 5e-6 | 0.013 % | 0.0001 % | | Zn-68 Eback default (13) | 4e-4 * | 0.015 % | 0.003 % |
  | Zn-68 Tirrad 2 h 30 m | 5e-6 | 0.013 % | 0.007 % | | Zn-68 Ebeam 15 Eback 12 | 1.4e-4 * | 0.050 % | **0.062 %** |
  | Zn-68 Tcool 3 h | 1.3e-4 * | 0.013 % | 0.0005 % | | Zn-68 blockyield y (Y.tot) | 1.3e-4 * | 0.013 % | 0.0000 % |
  | Zn-68 Tirrad 3 d Tcool 2 d | 8.5e-5 * | 0.013 % | 0.0007 % | | p + Mo-100 E 24->15, 6 h / 2 h | 9e-5 * | 0.25 % | |
  | Mo-100 mCi, mug, Ibeam 0.1 | 1.1e-4 * | 0.25 % | 0.0000 % | | Mo-100 Tcool 1 d, kBq, g | 9e-5 * | 0.25 % | 0.0001 % |
  | p + O-18 E 14->4, 2 h / 1 h | 4e-6 | 0.49 % | | | a + Bi-209 E 29->21, 4 h / 1 h | **1.7e-3** ** | 0.38 % | |

  \* the worst is a Yield entry near saturation, where stock's yield is a float32 difference of two activities
  (e.g. Ga-68 at 13 h: stock 6.233334e-4, port 6.238889e-4 GBq/mAh); activities, isotopes and fractions agree to 1e-6.
  \*\* Pb-207 at 0.1 h (15 atoms, a stable daughter of 31 y Bi-207): exp1 - exp2 cancels to the last bits in both
  codes (double; libm ulps), noise.
  Headline products, engine vs stock at end of irradiation = the production-rate difference each time: Ga-68
  0.001 %, Ga-67 0.007 %, Cu-64 0.013 %; Tc-99m (Y043099.L02) 0.074 %, Mo-99 0.017 %, Tc-100 0.046 %; F-18 0.49 %,
  F-17 0.57 %; At-211 0.77 %, At-210 1.24 %, Po-211 1.11 %, At-212 0.16 %.
* **Losses (all residual production, not B11).** Small channels where the engine's cross section differs: Zn-66
  from p + Zn-68 (0.3 mb, prate +75 %), Nb-98 from Mo-100 (+161 %), O-16 / C-12 from O-18 (+20 % / -98 %), Zr-93
  (436 %: fed only by Y-93 decay, whose 1e-18/s rate is 80x stock's). Nuclides with a tiny engine cross section where
  stock has none get Y files stock does not write (Co-61, Ni-61, Cu-66 from Zn-68; Y-92, Zr-92/94/95/96 from Mo-100;
  Bi-210 and its isomer from Bi-209). The O-18 deck (light target) agrees for F-18; the light-nucleus physics itself
  is outside B11.
* Tests: `tests/hf/test_kwcov_b11.py` (time units, density table, time grid = stock's, JEFF half-lives and decay
  types, the port on stock's p + Zn-68 cross sections vs stock's Y files and talys.out to 2e-6, units / Ibeam / Area,
  file round trip and blockyield, Options and deck-line parsing, every refusal, one p + Zn-68 engine run, neutron
  refusal through run_deck).

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
