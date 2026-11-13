# Every TALYS-2.25 keyword and observable in `physics/hf`: details per batch

Goal (after A. Koning: "the challenge is to cover all the same observables and keyword
combinations"): the engine reads every TALYS keyword and produces every TALYS observable, or says in the coverage
matrices why not. Inventory: `KEYWORD_COVERAGE.md` (446 keywords) and `OBSERVABLE_COVERAGE.md` (58 output families).
Regenerate both after every batch:

    # the engine venv (has torch); <talys-src> = a TALYS-2.25 source tree, talys.out = a stock echo run
    PY=.venv/bin/python
    $PY scripts/kwcov/inventory.py --talys <talys-src> --echo <work>/echo/talys.out
    $PY scripts/kwcov/observables.py && $PY scripts/kwcov/render.py

## Starting point (before the batches)

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
* **Test first, against stock TALYS-2.25** (`<talys-src>/bin/talys`). A stock run of one target at three
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
* **Resources**: one python or TALYS process at a time, with >= 8 GB memory available. Native build in a
  Windows worktree: the build scripts have CRLF endings and WSL has no
  `make`/`cc`; strip `\r` into a temp copy inside `scripts/` and run it with
  `CC=<conda env>/bin/gcc` (see B1 notes below).
* After the batch: rerun the inventory, update the batch's rows (status, `evidence = test:<file>`), commit.

## Batches, in order of value

Effort is the estimated porting time. "Anchors" are the TALYS routines to port (`source/<file>:<line of the subroutine>`); the
keyword's own parse line is in `keyword_coverage.csv` (`talys_line`).

| # | batch | keywords | observables | effort |
|---|---|---|---|---|
| B1 | channel observables (DONE) | -- | prod/multiplicity (gas production), binary.tot, xs*.tot gamma column, xs*.LMM isomeric channels, xs*.fis, discrete/continuum split | 0.5 d |
| B2 | deck wiring of what exists (DONE) | best, bestend, bestbranch, bestfile, fit, ngfit, nnfit, nffit, nafit, ndfit, pnfit, gnfit, dnfit, anfit, macsfit, gamgamfit, ejectiles, maxlevelsbin, maxlevelsres, nlevels, estop, liso, isomer (check), per-nucleus forms of ldmodel/colenhance, `energy E1 E2 dE` | CHANOBS default decision | 1-1.5 d |
| B3 | angular distributions on TALYS keywords | outangle, outlegendre, fileelastic, fileangle, angles, anglescont, cpang | elastic/inelastic ang + leg, Rutherford ratio (charged), compound ang. for charged particles | 1.5-2 d |
| B4 | spectra, DDX, gamma lines on TALYS keywords (DONE; exclusive channel spectra: B4b DONE, with `components y`) | outspectra, filespectrum, fileddxe, fileddxa, ddxmode, outgamdis, filegamdis, channelenergy, adddiscrete, addelastic, equispec (check) | emission spectra, DDX, discrete gamma lines, exclusive channel spectra, (n,gn) column xsngn | 1.5-2 d |
| B5 | model keyword sweep: compound, gamma, levels, LD (DONE) | tjadjust, rgamma, cknock, esurf, pshiftadjust, pshiftconstant (check), spradjust, popmev, emaxpseudores, pseudoreswidth, pseudoresfade, ntop, nlow, densfile, e1file, m1file, skipcn, maxzrp, maxnrp, rpevap, branch, levelfile, deformfile, massdir, sfth, sfexp, ldmodelracap | -- | 1.5-2 d |
| B6 | model keyword sweep: optical model, direct (DONE) | optmodall, vinfadjust, incadjust, rvadjustf ... awsoadjustf (12), riplomp, optmod, optmodfilen, optmodfilep, ompenergyfile, coulomb, ecisstep, eciscompound, statepot (check), rotational, sysreaction | -- | 1.5 d |
| B7 | unported model branches (DONE; gnorm y and MSD stay refused) | gnorm y, gshell y, twocomponent n, preeqspin 3, preeqmode 3, onestep, emsdmin, msdbins (MSD) | -- | 2 d |
| B7b | JLM and folding alpha OMP (DONE; JLM with preeqmode 3 / racap / optmodall / alphaomp 3-5 refused) | jlmomp, jlmmode, radialmodel, radialfile, lvadjust, lwadjust, lv1adjust, lw1adjust, lvsoadjust, lwsoadjust, alphaomp 3-5, adepthcor, aradialcor | -- | 2-3 d |
| B8 | fission extras (DONE; fisfeed J-parity columns and fragment-based nubar/PFNS -> B14) | fisfeed, rfiseps, axtype, class2file, hbtransfile, cnubar1, cnubar2, tmadjust, fsadjust, pfnsmodel 1 | rpZZZAAA.fis, nubar (Wahl), PFNS (Iwamoto), fission info | 2 d |
| B9 | astrophysics (DONE; astro + racap, fissile astrogs n refused) | astro, astrogs, astroex, astroe, astrot, nonthermlev | astrorate.*, MACS | 1-1.5 d |
| B10 | URR (DONE; widthmode 2/3 refused) | urr (check), lurr, urrnjoy, rprime | urr*.dat, urrtalys.tot | 1.5 d |
| B10b | thermal, natural targets, resonance range (DONE; resonance y refused) | xscaptherm, xsptherm, xsalphatherm, mass 0, abundance, resonance, group, integral, reslib, tres | thermal xs, natural sums, resonance/group/integral | 1.5 d |
| B11 | medical isotope production (DONE) | production, ebeam, eback, ibeam, tirrad, tcool, area, rho, radiounit, yieldunit | Y*.tot yields/activities | 1 d |
| B12 | recoils and LAB frame (DONE) | recoil, recoilaverage, maxenrec, anglesrec, labddx | recoil spectra, LAB DDX | 2 d |
| B13 | ingredient outputs (DONE) | outlevels, blocklevels, outbasic, outtransenergy, blockomp, outdensity, filedensity, outgamma, filepsf, outinverse, outomp, outkd, partable | ld/psf tables, T and inverse xs, OMP parameters, parameters.dat | 1 d |
| B14 | fission yields and fragment evaporation (part 1 Brosa DONE; part 2 GEF DONE; part 3 FF evaporation: fymodel 4 + 5, isomer split, per-ejectile nu DONE; pfnsmodel 2 spectra and fymodel 3 open) | massdis, fymodel, ffmodel, gefran, outfy, ffevaporation, ffspin, yieldfile, pfnsmodel 2 | yieldA/ZA, nu(A), P(nu), PFNS/PFGS from FF decay | 4+ d (split: Brosa; GEF; FF evaporation) |
| B15 | low value (DONE; components y (B4b: ported since), densfile/e1file/m1file/massdir, rescuefile/strucpath/bestpath refused; endf.cs ECIS files not given; transpower ported; U-239 E1 fix behind INCOGNITA_FIDFIX=psfsgl) | endf, endfdetail, sacs, legacy, components, micro, transpower | tefal.inf, gamma*.tot, sacs.dat | 1 d |
| GAP | isomeric (excited) targets (DONE; design `ISOMERIC_TARGETS.md`; n only, channel / level / total xs; ltarget + liso, Ltarget > 40 (Hf-178m2, as stock) and the angular / spectra / recoil / astro / urr / endf / components / racap / production / massdis outputs refused) | ltarget | everything for an excited target | 3+ d |

NA keywords (71: `out*`, `file*`, `block*`, paths, labels, ECIS plumbing) stay NA; the observables they switch are
batches above.

### B1 -- channel observables (done)

* What: `Results.extras` (new field, empty by default) carries TALYS's names for numbers the engine already computed:
  `<p>prod.tot` (+ `:multiplicity`), `binary.tot:<p>`, `<k0><p>.tot:discrete|continuum`, `xsNNNNNN.tot:gamma`,
  `xsNNNNNN.LMM` (+ `:branch`), `xsNNNNNN.fis`. Module `physics/hf/emission/chanobs.py`; switch
  `INCOGNITA_CHANOBS=1`. On the C driver the switch takes the Python channels on the C cascade's result (the
  existing fallback), because `ce_channels` returns only channel cross sections.
* Found on the way: particle production was wrong for neutrons by default (aprod Co-59 14 MeV 21 vs 38 mb) because
  the cascade gets only the compound part of `xsbinary` unless `INCOGNITA_TRITFID` is on. CHANOBS adds the missing direct,
  pre-equilibrium, giant-resonance and direct-capture emission (`multiple.binary_adds`, exact because xsparticle is
  a sum over xsfeed). `INCOGNITA_TRITFID` itself is untouched (still off for neutrons).
* Acceptance (`tests/hf/test_chanobs.py`, `scripts/kwcov/b1_compare.py`): switch on vs off, every other array
  identical (Fe-56 611, Co-59 660 arrays bitwise; U-238 one array 1.7e-16, the fission path's known run-to-run
  noise); Co-59 isomer files sum to the channel; Co-59 vs stock: <= 0.5 % at 1 and 5 MeV, <= 12 % at 14 MeV
  (measured worst 7 %, tracking the engine's own (n,p)/(n,a) differences). Fe-56 and U-238 checked by the script,
  same picture (14 MeV pprod +10 %, aprod +11 % = the engine's (n,p)/(n,a) at 14 MeV; xs*.fis within 10 % = its
  (n,f)).
* Left for later: the (n,gn) column `xsngn` of `.con`/`.tot` files (B4: done, `Results.spectra[".tot:ngn"]`); CHANOBS default ON (B2 decides after
  timing it on a chart sample: it costs the Python channels per energy).

### B2 -- deck wiring of what exists (done)

* **What a deck is now.** A talys.inp (`physics/hf/input/deck.py`: `read_deck`, `run_deck`) or deck lines in
  `INCOGNITA_TALYS_FIT_LINES`. The lines now act without an `INCOGNITA_TALYS_FIT` arm (before, they were dropped
  silently unless an arm was named). A deck line the port cannot apply (energy-dependent table form,
  unknown index / particle) is refused; the same line coming from a best file or a fitted library is left out with
  a warning naming it (it was silent). A multi-word form of an Options keyword TALYS does not have is refused (it was
  skipped).
* **Wired** (all default-off; default runs bit-identical, `test_engine_c.py`):
  `best` / `bestend` / `bestfile` (fitlib `_deck_best`: deck `best y` gives the same deck lines as
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

### B3 -- angular distributions (done)

* What: `physics/hf/angout.py` (output only). The deck keywords `outangle`, `fileelastic` (angleout runs when either is
  y, output.f90:65), `fileangle`, `outlegendre`, `blockangle`, `angles`, `cpang` (new Options fields `flagang`,
  `fileelastic`, `fileangle`, `flagblockangle`; `endf y` sets them as TALYS does) or the port switch
  `INCOGNITA_ANGOUT=1` turn the `specout` recorders on for the run and fill `Results.angular` (new field, empty by
  default) under TALYS's names: `<k0><t>ang.LNN` (+ `:direct`, `:compound`, charged elastic `:ruth`, `:nucint`) on the
  `angles` grid, `<k0><t>leg.LNN` (+ `:direct`, `:compound`, `:normalized`, `:endf6`), `angle`.
  `INCOGNITA_ANGOUT_DIR=<dir>` also writes the YANDF files with TALYS's names (`nn0014.000ang.L01`, `nnang.L01` with
  `blockangle y`); headers and the file set equal stock's (Fe-56 run: same 666 names).
* Physics: shape elastic and direct levels from specang (engine OMP / DWBA deck / coupled channels); discrete
  pre-equilibrium x Kalbach (preeqang.f90); compound cleg of EVERY residual (`compound/ceang_types.py`, the generalised
  `ceang` with each particle's own spin and TALYS's phase), normalised to the engine's level populations; isotropic
  without flagcompang ((k0 = 1 or cpang) and outangle and E <= 50). Charged projectiles: Coulomb amplitude and phases on
  the engine's S-matrix (`angout.charged_elastic`), ratio to Rutherford and nuclear+interference as angdis.f90.
* Found on the way: the photon exit channel's Moldauer factor is 1 in TALYS (comptarget.f90:510 sends every photon to
  channel tnum+1, whose `tav` molprepare never fills); with the particle formula (n,g) level shapes were off by up to
  6 % (Fe-56 1 MeV) and Legendre terms by 30 % (Pb-208 1 MeV); with it they agree to 1e-6.
* Acceptance (`tests/hf/test_angout.py`, `scripts/kwcov/b3_compare.py`, stock runs in `<work>/stock/b3_*`): switch on
  vs off, every Results array identical (Fe-56 three energies, U-238 692 arrays). Per angle where stock > 1 mb/sr:
  Fe-56 elastic + levels 1-2 at 1, 5, 14 MeV worst 0.39 %; Pb-208 0.25 %; U-238 (coupled) levels 0-3 at 1, 14 MeV
  0.48 %. p + Nb-93 5, 14 MeV ratio to Rutherford 1e-5, elastic 2e-5; cpang y compound distributions 1e-5. Other
  residuals' discrete distributions (n,p) (n,a) (n,d) (n,g): shapes 1e-5 of stock; their absolute level cross sections
  are the engine's (14 MeV: compound +15 %, the known level-population difference; (n,t) (n,h) < 1e-5 mb off by x3-70).
* Left: the charged-particle elastic Legendre Direct column (ECIS's Coulomb-subtracted expansion), HRTW/GOE pair weights
  (isotropic then), charged projectiles on coupled targets (no shape elastic), repeated `fileangle` deck lines (one
  value per key until B2 merges them; `fileangle 1,2` works), `Results.angular` through `pool.py` (not carried),
  `anglescont` (continuum DDX grid) belongs to B4.

### B4 -- spectra, DDX, discrete gamma lines (done)

* What: `physics/hf/specobs.py` (output only). The deck keywords `outspectra`, `ddxmode` (> 0 implies outspectra),
  `fileddxa`, `fileddxe`, `anglescont`, `outgamdis`, `filespectrum`, `filegamdis`, `blockspectra`, `blockddx`,
  `adddiscrete`, `addelastic`, `channelenergy` (spectra.f90's espec conversion), `elwidth`, `segment` (new Options
  fields `flagspec`, `ddxmode`, `flaggamdis`, `filegamdis`, `filespectrum`, `fileddxa`, `fileddxe`, `flagblockspectra`,
  `flagblockddx`; `endf y` / `recoil y` set them as TALYS does) or the port switch `INCOGNITA_SPECOBS=1` (= outspectra y,
  ddxmode 3, outgamdis y) turn the `specout` recorders on and fill `Results.spectra` (new field, empty by default) under
  TALYS's names: `<x>spec.tot` (+ `:E` espec, `:direct`, `:preeq`, `:multiple_preeq`, `:compound`, `:preeq_ratio`, and
  for d t h a / charged projectiles `:breakup_ratio`, `:stripping`, `:knockout`, `:breakup`), `Eaverage_<x>.out`,
  `<x>ddx` (C, M, nanglecont+1) + columns, `<x>ddxAaaa.a.deg`, `<x>ddxEeeee.e.MeV`, `anglecont`,
  `gamZZZAAALiiLjj.tot` (+ `:E`), `<k0><x>.tot:ngn` (xsngn, the B1 gap). `INCOGNITA_SPECOBS_DIR=<dir>` writes the files
  with TALYS's names (`nspec0014.000.tot`, `nddxE0014.000A030.0.deg`, `nddxE0014.000E0003.0.MeV`, `gam026056L01L00.tot`,
  `Eaverage_n.out`; `blockspectra`/`blockddx` names).
* Physics: spectra.f90 on the recorded parts taken as TALYS has them (`INCOGNITA_SPECCLOSE`'s closing undone: raw
  binary parts,
  compemission without the discrete-parent addition): espec = egrid up to eoutdis(NL) - elwidth, then the 1/(segment
  fine) grid with Gaussian discrete peaks (elastic with addelastic); Eaverage from Eaveragebin / Eaveragemul / xsfeed;
  DDX = Kalbach (pre-equilibrium, multiple pre-equilibrium) + isotropic compound + discad (angout, run internally for
  every level when only the DDX asks) for the peaks; gamma lines = the cascade's discrete transitions / (1 + conv)
  (cascade.f90:78, electronconv y); xsngn = the initial compound nucleus' own emission (multiple.f90:945).
* Found on the way: gamma lines need the conversion coefficient (Mn-56 26 keV line x2.5 without it); the engine's
  `specout` spectra are `INCOGNITA_SPECCLOSE`-closed by default (not TALYS), so TALYS names use the raw parts; deck
  values with two
  words (`fileddxa n 30`) were refused by `default_options` -- `ejectiles` / `ddxpoints` kinds now pass. Not fixed
  (outside B4): with `equispec y` the engine builds the equidistant grid with numen 250 (`preeq/prepare.py`,
  `compound/dens_reference.py`: the reference build) where stock 2.25 has 260, so above 12.5 MeV its step is 0.108
  instead of 0.1 MeV (Fe-56 at 14 MeV); below that the spectra agree as without equispec (5 MeV 2e-4).
* Acceptance (`tests/hf/test_specobs.py`, `scripts/kwcov/b4_compare.py`, `scripts/kwcov/b4_onoff.py`, stock run
  `<work>/stock/b4_fe56`): switches on vs off, every Results array identical (Fe-56 611, U-238 692 arrays bitwise).
  Fe-56 vs stock, espec grids identical; per bin where stock > 1 mb/MeV: 1 MeV 1e-5, 5 MeV 2e-4 (n, g); DDX 30/90/150
  degrees 1.4e-3 at 5 MeV; Eaverage 1e-4; xsngn 1e-4 at 1, 5 MeV; 846.8 keV line 1e-5 at 1, 5 MeV and 1.2 % at 14 MeV.
  14 MeV: n spectrum 5.5 % (integral -1.1 %), p 15 % (integral +9.8 %), DDX n 9 % (150 deg), p 15 % -- the compound
  column carries the engine's own channel differences ((n,2n)/(n,np) composition, (n,p) +10 %); the pre-equilibrium
  column agrees to 4e-5 at every energy; shapes normalised to the integral: n 6.7 %, p 10 %. TALYS's own spectrum
  integral minus elastic equals nprod to 0.25 % at 5 and 14 MeV; ours is the same construction. U-238
  (`<work>/stock/b4_u238`): spectra 1 MeV 1e-3, 5 MeV 2.5 %, 14 MeV 3 % (its compound column); DDX 1 MeV 1.5e-3, but
  14 MeV up to 28 % at 150 deg in the 8-13 MeV band: the collective continuum of the deformed levels above Nlast and
  the giant resonances are isotropic here (their discrete levels' discad agree with stock to 0.5 %); 14 MeV alpha
  espec breaks from egrid to the fine grid 2 MeV later than stock (eoutdis(a, Nlast) of Th-235, sub-mb channel).
* Left: exclusive channel spectra `spNNNNNN*.tot` (B4b: specexcl through the channel loop, specemission.f90);
  the giant-resonance / collective-continuum DDX is isotropic (TALYS: grcollad / directad, DWBA shapes; Fe-56 14 MeV
  <= 0.05 mb/MeV/sr of a few mb/MeV/sr); break-up (kalbachBU, xspreeqbu) is zero (only d/alpha projectiles have it);
  LAB-frame spectra/DDX (B12); repeated `fileddxa`/`fileddxe`/`filespectrum` deck lines need B2's merge (one line per
  key until then: `fileddxa n,30,90,p,150`); `channelenergy y` follows spectra.f90 but is not checked against stock.

### B4b -- exclusive channel spectra and `components y` (done)

* **What.** `physics/hf/exclspec.py` (output only): channels.f90's exclusive-channel loop walked again on the energy's
  channel inputs with `specexcl` (binemission.f90's `binemis` per binary residual bin from the raw binary parts
  `specout` recorded; the first term = source channel spectrum x feedexcl / popexcl; specemission.f90's smearing of the
  last emitted particle over mother and residual bins; the photon source walked down the channel's own bins); final
  spectra = ground state + isomer bins, fission spectra = fisfeedex-weighted bins. `Results.spectra`:
  `spNNNNNN.tot:E` / `:g` ... `:a` (C, M) on egrid(ebegin(0)..eendhigh), `spNNNNNN.fis:*` for fissile targets;
  `sp000000.tot` particle columns = xsngnspec (zero unless `endf y`, as TALYS). A channel is present when TALYS writes
  its file (chanopen, xs >= xseps incl. the non-threshold xseps floor; xsfis > xseps). `INCOGNITA_SPECOBS_DIR` writes
  `spNNNNNNE0014.000.tot` / `.fis` (YANDF headers). Switch: `outspectra y` (or ddxmode > 0, endf y, recoil y,
  INCOGNITA_SPECOBS=1) AND `channels y`; with it the C driver takes the Python channels (as CHANOBS: same numbers).
* **`components y`** (refused since B15) is ported: `physics/hf/compoobs.py`, multiple.f90:649-668 on the `specout`
  records (binary xsdirdisctot; binary preeqpopex with the target level zeroed + received - emitted multiple
  pre-equilibrium up to Smax; quirk kept: xspopcomp = pop - (preeq - dir)). `Results.extras`:
  `xsNNNNNN.tot:direct|:preeq|:compound` (F x xschannel) and `rpZZZAAA.tot:direct|:preeq|:compound`. `components y`
  turns the `specout` recorders on (specout.enabled). binaryout.f90's talys.out-only split is not given.
* **Defaults** bitwise: nothing runs without the keywords; with them every other Results array is bitwise the same
  (Fe-56 14 MeV TALYS mode, test). Python driver (engine.run) wired too (smoke: Fe-56 5 MeV, the stock channel set).
* **Vs stock** (`scripts/kwcov/b4b_compare.py`, TALYS mode, stock `<work>/stock/b4b/{fe56,co59,u238,fe56_endf,
  fe56_maxch2}` from `scripts/kwcov/b4b_stock.sh`; worst |ours/stock - 1| on the main bins = stock >= 1 % of the
  column peak): Fe-56 5/14 MeV 0.15 % (gamma column of (n,g)), every particle column <= 0.06 %, channel set identical;
  Co-59 14 MeV 0.62 % ((n,n') gamma), particles <= 0.02 %; `endf y` (xsngnspec columns of sp000000: n 3e-5) and
  `maxchannel 2` respond as stock (Fe-56 14 MeV has no 3-particle channel: no change on either side). U-238 5/14 MeV:
  particle columns <= 1.6 % ((n,n') 14 MeV, the channel's own -0.25 %), every .fis file 1e-4 WITH
  `INCOGNITA_FIDFIX=psfsgl` (without: fission gamma columns 17 % = B15's U-239 E1 table bug). Components: Fe-56,
  Co-59 <= 0.1 %; U-238 14 MeV 3.4 % (U-239 compound, 1.1 mb), tiny channels (< 0.01 mb) up to 10 %.
* **Losses (recorded).** (1) U-238 14 MeV gamma columns: (n,p) up to 59 % low at E-gamma < 0.6 MeV (integral -8 %),
  (n,g) 14 %, (n,n') 4 %: the engine's own Pa-238 / U-239 gamma cascade (xs010000 gamma production 1.217 vs stock
  1.293 mb, xs000000 5.98 vs 5.83 mb), not the spectrum port (Fe-56 / Co-59 gamma columns agree to 0.6 %). (2) U-238:
  the engine keeps 9 sub-xseps floor channels stock does not open (sp001102, sp002002, sp010102, sp011002, sp020002,
  sp100012, sp100102, sp101002, sp110002: Q > 0, 1e-7 mb, zero spectra) -- the engine's channel set (xs files too),
  not B4b. (3) `block y` names (sp100000.tot, appended) are not written (non-block names only; `endf y` implies block in
  TALYS); the arrays are the same.
* **Bugs.** No new engine bug: the U-238 differences are the engine's gamma cascade (above) and B15's known U-239 E1
  table bug (`INCOGNITA_FIDFIX=psfsgl`, default ON since the KWCOV integration).
* Tests: `tests/hf/test_kwcov_b4b.py` (switches, reaction strings, specemission flux conservation, the components
  quirks, Fe-56 14 MeV TALYS mode vs stock integrals 0.5 % and components 1 %, bitwise on/off, the files).

### B5 -- model keywords: compound, gamma, levels, level densities (done)

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

**Done.** New modules `physics/hf/omp/ompdeck.py` (files, ranges,
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
* **Response vs stock** (`scripts/kwcov/b6_response.py`; stock runs trimmed in `<work>/stock/b6_*`):
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

### B7 / B7b -- unported model branches (both done, B7b below)

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
    ftable(E1) of the compound nucleus to every strength user (the fit-parameter wiring's ftable path). Reproducing it means
    reproducing the unit bug; `ftable Z A f` is the physical alternative.
  * `twocomponent n` or `gshell y` with multiple pre-equilibrium (Einc >= `multipreeq` onset, 20 MeV):
    multipreeq.f90 (one-component chain) is not ported, and the shell damping is not wired into multipreeq2's
    cascade (`MultiPreeqInputs.damp` exists, `Cascade.mpe_inputs` does not fill it); refused in
    `feed_reference.pop_inputs_of` with the reason. `preeqspin 4` with multiple pre-equilibrium likewise.
  * `preeqspin 3` on the GPU path (`gpu_full_setup`): refused (engine_c has it).
  * B7b (`alphaomp 3-5`, JLM): done, see the B7b section below.
* **Response vs stock** (`scripts/kwcov/b7_response.py`, n + target at 1/5/14 MeV, channels of b2_response plus
  nprod/pprod/aprod; `--pe` compares the binary pre-equilibrium totals with stock `preeq*.out`; stock JSON in
  `<work>/stock/b7`):

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

### B7b -- JLM and folding alpha OMP (done)

New modules `physics/hf/omp/jlm.py` (radialtable.f90, mom.f90, momjlmecis.f, and
ECIS's tabulated-potential channel) and `physics/hf/omp/foldalpha.py` (foldalpha.f90, afold.f, mahaux); hooks in
`omp/inverse.inverse_channels`, `omp/incident.incident_channel`, `compound/dens_reference._transmission_build` (the
native inverse path stands aside under JLM / alphaomp 3-5), `omp/parameters` (alphaomp 3-5 keep the base potential, as
opticalcomp.f90:323), `omp/ompdeck.extract` (`radialfile`), `input/fitlib` (energy-local l*adjust refused). Stock refs
in `<work>/stock/b7b`; responses by `scripts/kwcov/b7b_response.py` (n decks, `--base`) and
`scripts/kwcov/b7b_alpha.py` (alpha projectile, run_deck with INCOGNITA_CPINC=a).

* **What TALYS does, reproduced.** `jlmomp y` (also `micro y`) sets flagspher, so the incident channel is spherical;
  every nucleus with a mass in `structure/optical/jlm/<d1m|bskg3>/<Sym>.rad` (or `radialfile Z file`) gets
  jlmexist(n) = jlmexist(p) and runs ECIS on mom's tabulated potential (hint 0.1, rmatch 18, njmax 1600 = no l cap);
  nuclei without a density keep the phenomenological OMP. `alphaomp 3-5` likewise for the alpha (jlmexist(6)): the
  double-folded real part (afold, normalised to its volume integral; adepthcor / aradialcor and the beta2 radius
  stretch), the WS volume (+surface) imaginary part, dispersion for 5. ECIS's tabulated form factors are read at the
  integration nodes r = 0.1 n (the table's own points), U = -(s fext) with the strength s and the es20.6 values as
  written; spin-orbit `-0.5 potjlm` times 2 (2 l.s) as for Woods-Saxon.
* **Checks against stock** (tests/hf/test_kwcov_b7b.py): Fe-56 JLM potentials = omp.out to its 6 printed digits at
  1/5/14 MeV (V, W, Vso, Wso); incident total / reaction / elastic and T_lj (all 56 inverse energies) to 7 digits;
  alpha + Fe-56 alphaomp 3/4/5: V (Coulomb removed) and W = omp.out to 1e-5, reaction xs to 1e-4.
* **Response** (|ln(R/S)| worst, channels > 1 mb, 1/5/14 MeV n, 10/15/20 MeV alpha; "stock moved" = largest |ln S|):

  | deck lines | target | TALYS mode | default | stock moved |
  |---|---|---|---|---|
  | jlmomp y | Fe-56 | 0.04 % (n,d) 14 | 0.94 % (n,np) 14 | 69.7 % |
  | jlmomp y | Pb-208 | 0.01 % | 0.01 % | 11.5 % |
  | micro y | Fe-56 | 0.04 % | **80 %** (n,p) 14: `npwindow` on ldmodel 7, deliberate default (B15) | 69.6 % |
  | jlmomp y + jlmmode 1 / 2 / 3 | Fe-56 | 0.00 / 0.00 / 0.00 % | 0.03 / 0.08 / 0.46 % | 2.4 / 5.3 / 29.3 % |
  | jlmomp y + radialmodel 1 | Fe-56 | 0.00 % | 0.35 % | 16.1 % |
  | jlmomp y + lvadjust 1.05 / lwadjust 1.3 | Fe-56 | 0.00 / 0.00 % | 0.90 / 0.23 % | 44.0 / 14.8 % |
  | jlmomp y + lv1adjust 1.3 / lw1adjust 1.3 | Fe-56 | 0.00 / 0.00 % | 0.10 / 0.07 % | 6.0 / 3.3 % |
  | jlmomp y + lvsoadjust 1.5 / lwsoadjust 2 | Fe-56 | 0.00 / 0.00 % | 0.55 / 0.00 % | 15.8 / 0.0 % |
  | alphaomp 3 / 4 / 5 (n,a) | Fe-56 | 0.00 % each | 0.03 / 0.02 / 0.07 % | 5.2 / 2.0 / 7.4 % |
  | alphaomp 4 + adepthcor 1.1 / aradialcor 1.05 | Fe-56 | 0.00 / 0.00 % | 0.03 / 0.21 % | 7.4 / 36.2 % |
  | alphaomp 4 | Pb-208 | 0.00 % | 0.00 % | 0.0 % |
  | alpha + Fe-56: alphaomp 3 / 4 / 5 | Fe-56 | 0.42 / 0.43 / 0.40 % (a,a') 20 | -- | 9.3 / 11.2 / 12.2 % |
  | alpha + Fe-56: alphaomp 4 + adepthcor 1.1 / aradialcor 1.05 | Fe-56 | 0.43 / 0.49 % (a,a') 20 | -- | 9.1 / 64.3 % |

  The alpha-projectile worst cell is the inelastic (a,a') at 20 MeV, where the engine's own default (a,a') differs from
  stock by ~0.3 %; nonelastic moves identically (0.00 %).
* **Refused (`defaults.reject_unported`), with what is left:** `jlmomp y` with `preeqmode 3` (bonetti.f90 normalises
  the exciton W to the JLM imaginary volume integral, one mom call per emission energy: port `bonetti` B), with
  `racap y` (racapinit.f90:375 / racap.f90:138 JLMB direct-capture states: port racopt 3), with `optmodall y` (wire
  `_transmission_build(cn=...)`'s set to the JLM solve and test), with `alphaomp 3-5` (TALYS writes the folded alpha
  with normjlm(Zix, Nix, 1:2), which foldalpha never sets: the alpha strengths are whatever the last JLM n/p call on
  that nucleus left there; reproducing that means tracking mom's call order); `alphaomp 3-5` with `optmodall y`; the
  energy-local forms of lvadjust ... lwsoadjust, aradialcor, adepthcor (`<key> v Ea Eb Em D`, adjust.f90 inside mom /
  foldalpha): the line is refused, the plain value acts.
* **Quirks kept / found.** radial.out (outomp y) prints the COMPOUND nucleus's density under the target's title
  (inverseecis.f90:213; not given by the port, NA). afold's alpha density takes r^2 of the previous grid point, its
  target exp(-beta rho) factor takes 4 pi r^2 rho, and ftrans's Filon branch writes the end node of its last panel to
  bcof(npoint) and never sets bcof(npoint-1) (stale in TALYS, 0 here; the integrands vanish there).
* **Bug fixed on the way:** `omp_parameters` raised for alphaomp 3-5 on every alpha channel, including nuclei without
  a density, where TALYS keeps the base (alphaomp 1-like) potential.
* **Not given:** radial.out; the JLM path is Python only (no native / GPU kernel), so a JLM run's inverse solve is
  slower than the default's. The differentiable path is not differentiable through JLM.
* Tests: `tests/hf/test_kwcov_b7b.py`; `test_unported_options.py`, `test_kwcov_b15.py::test_micro_cascade`,
  `test_charged_fidelity.py` updated.

### B8 -- fission extras

Per-fissioning-nucleus fission (`rpZZZAAA.fis`, `finalout.f90:396`), `fisfeed`, `rfiseps`, `axtype`
(`colenhance.f90`, densitypar), `class2file`, `hbtransfile` (`fissionpar.f90`), `cnubar1/2` + `nubarWahl.f90:1`,
PFNS Iwamoto (`iwamoto.f90:1`, `pfnsout.f90:1`, `tmadjust`, `fsadjust`). Accept: U-238 and Th-232 at 1, 5, 14 MeV:
per-chance fission vs stock within the engine's own (n,f) band; nubar 0.5 %; PFNS mean energy 1 %, shape 3 %.

**Done.** New module `physics/hf/fisobs.py` (output only); small hooks in
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
* **Observables vs stock** (`scripts/kwcov/b8_response.py`; stock JSON trimmed in `<work>/stock/b8/b8_*.json`, states
  files in `<work>/stock/b8_files`): PFNS of U-238, U-235, Pu-239, Th-232 at 1/5/14 MeV, also with `tmadjust 1.3`,
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

**Done.**

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

**B10 done.** B10b: below, after B10.

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
  not separated here), with INCOGNITA_EWFC on a coupled target, with the keV cold-pass alpha-table cell options.
  checkvalue's `lurr`
  0-60, `rprime` 0-10, incident neutrons only, compound model on.
* **Vs stock** (`scripts/kwcov/b10_response.py`, energies 0.01 0.1 1 5 MeV, stock JSON in `<work>/stock/b10`; every
  number of every urr file where stock > 1e-6 of its column maximum, same files and rows):

  | deck | default mode | TALYS mode | worst (TALYS mode) |
  |---|---|---|---|
  | Fe-56 `urr y` (+ `urrnjoy y`) | 5e-5 (7e-5) | same | capture 5 MeV (Gx 5 MeV) |
  | Co-59 `urr y; urrnjoy y` | 1.0e-4 | 1.0e-4 | Gx 5 MeV |
  | U-238 `urr y` (+ `urrnjoy y`) | **22 %** Gf (`exactfis`), Ga 9e-10 vs 0 eV | **0.11 %** | Gg 1 MeV = the engine's own (n,g) at 1 MeV (65.28 vs 65.21 mb) |
  | Au-197 `urr y; urrnjoy y` | **x2.0** Gx, capture **-30 %** (`ccexitnbnf`) | **2e-4** | Gx 1 MeV |
  | `urr 0.5` (onset): Fe-56 / U-238 | | 4e-6 / 8e-5 | |

  Keyword responses (TALYS mode, |ln(R/S)| or the same absolute change): `urrnjoy y` Fe-56 7e-5, U-238 2.8e-4 (Gx);
  `lurr 0` / `1` Fe-56 1e-5 / 7e-6, U-238 8e-5 / 1.5e-5; `lurr 3` the l03 files = stock to 3e-5; `rprime 7` (with
  urrnjoy) Fe-56 6e-7, U-238 6e-6. Default mode differs only through `exactfis` (U-238 Gf, fission sums) and `ccexitnbnf`
  (Au-197 competitive width and capture), FIDELITY_DEFAULTS.md's deliberate defaults.
* **INCOGNITA vs TALYS URR (recorded, not touched).** The published/reactor library's URR is not this path: the
  reactor-library build (`urr_build.py`, not in this repository) writes ENDF MF2 LRU=2 LRF=2 LSSF=1 from engine
  ingredients, with
  D(l,J) from an Ericson spin distribution and an analytic energy dependence (TALYS: the full level density at S_n +
  Einc per (J, parity)), <Gn> from the OMP S0/S1 with R = 1.35 A^(1/3) and S2 := S0 (TALYS: Tjlinc per (l, j) with the
  ENDF radius 1.23 A^(1/3) + 0.8), <Gg> = the engine's energy-independent gamgam_th s/p (TALYS: D Turrlj(0) / 2 pi from
  the capture sums, energy dependent and divided by the last Wab), <Gf> = the T_f(J) shape scaled to the engine's
  sigma_f (TALYS: D Turrlj(-1) / 2 pi), Gx fitted to the inelastic with AMUX 4 (TALYS: nu = 1), AP = R'(1 keV) (TALYS
  NJOY: R' of the first URR energy). The LSSF <Gamma_gamma> closure is part of that build. B10's files
  change none of it.
* **Not given:** energies below eninclow (Ninclow > 0; urrout fills their rows from the current energy; the port has
  no Ninclow energies: B10b gives thermal.f90's rows, not urrout's); thermal.f90 (done in B10b). Observed: a second
  `run_deck` with a different deck in the same process reused the first deck's Options (traced and fixed in B10b:
  stale `fitlib._ACTIVE` + (Z, A)-keyed caches).
* Tests: `tests/hf/test_kwcov_b10.py` (gnrl / unfac / strengthfunc by hand, keyword parsing, refusals, defaults record
  nothing, thermal capture table, Fe-56 run vs stock numbers with every cross section bitwise unchanged).

**B10b done.**

* **Energies below eninclow** (new module `physics/hf/thermal.py`, output only). TALYS computes nothing below
  `eninclow` (`elow`, default 1e-6 MeV): grid.f90 inserts E1v = 0.2 eninclow and eninclow when the grid starts below
  E1v, and at the first computed energy eref (talysreaction.f90:201) thermal.f90 fills every lower energy from eref's
  numbers: 1/v through the thermal value below E1v (R = xstherm / xs1), log-log between (E1v, xs(eref) Rres) and eref
  above it; capture's ratio for every channel, the (n,p) / (n,a) ones when xsptherm / xsalphatherm are set; elastic and
  compound elastic constant at eref's; non-elastic = the filled channels; inelastic, the projectile's own levels and
  binary column and fission 0; below E1v a capture / (n,p) / (n,a) isomer gets the table's branching. thermalxs.f90
  (structure/thermal, deck, Kopecky) is ported in full. `Results.thermal` = TALYS's rows ({"E", result_arrays key: rows,
  eninclow, E1v, eref, xscaptherm/xsptherm/xsalphatherm(-1..10)}); when eninclow is not one of the run's energies (it
  was inserted), eref is a one-energy engine run at it, as TALYS's first energy. Hooked at the end of `engine_c.run` and
  `engine.run`; a run with no energy below eninclow returns `res` itself (no Cascade built).
* **Natural targets** (`physics/hf/natural.py`, `run_deck`): `mass 0` reads structure/abundance/<El>.abun or the deck's
  `abundance <file>` (normalised, abundance.f90), runs every isotope with the same deck and grid and returns the first
  isotope's Results with channels, levels, residual production, totals, CHANOBS extras and the thermal rows replaced by
  abundance-weighted sums (union of keys, missing = 0; `:branch` ratios and `lowepot`'s weight not summed), plus
  `Results.natural` = {abundance, isotopes}. Refused with astro / urr / integral (natural.f90 sums none of their files).
* **integral y** (`physics/hf/integral.py`, `run_deck`, `Results.integral` = integral.dat): the target's
  structure/integral/sacs triples, the group spectra of structure/integral/spectra, xs linear on the file rows with a
  (0, 0) point in front (thermal rows included), groups above the last row left out; `m` = the first L01.. file, `g` =
  L00 (CHANOBS is switched on for the run, output only).
* **Refused / accepted.** `resonance y` refused at deck parse and in `run_deck` before any run: resonance.f90 runs
  Cullen's PREPRO (prepro.f, 29,688 lines: RECENT, SIGMA1 Doppler to `tres`, GROUPIE for `group y`) on the ENDF-6 file
  of `reslib` and splices the pointwise MF3 into the .tot files; not ported. `resonance n`, `group`, `reslib`, `tres`
  are accepted and change no number, as in TALYS without resonance y (flaggroup / Tres / reslib are read only by
  resonance.f90). checkvalue ranges ported for `elow` (1e-11-1), `tres` (0-1e12), `xscaptherm` (1e-20-1e10). `endf y`
  (eninclow from D0) with energies below eninclow refused (B15).
* **Bugs found and fixed (port).** (1) `xscaptherm` / `xsptherm` / `xsalphatherm` deck lines were DROPPED silently:
  the isomer axis of their Params made `_split` file them as "unsupported index form", which is not a loud reason (B10's
  "a deck xscaptherm wins" was never exercised). (2) The run_deck cache bug B10 observed, traced: `fitlib.activate` is
  a no-op when no deck lines are set, so after a deck WITH lines a deck WITHOUT them still ran on the old lines
  (`_ACTIVE` stale), and the per-target caches (`dens_reference._structure_of` keyed on (Z, A) only, and every
  lru_cache under it) are never dropped on the way from no deck lines to deck lines. Fixed: `activate` deactivates
  stale lines,
  and `Cascade.__init__` calls `fitlib.drop_caches_on_new_deck()`, which drops the per-target caches when the deck key
  (INCOGNITA_TALYS_FIT + the lines key) differs from the one they were built under (a process that never changes its
  deck drops nothing). Fe-56 1 MeV capture default / `ldmodel 2` / default in one process: 3.0452 / 2.1757 / 3.0452 mb
  (before: 3.0452 / 3.0452 / 3.0452). B10's test keeps its explicit drop; it is no longer needed.
* **TALYS-2.25 quirks / bugs kept.** (1) thermalxs.f90 reads the table after the input: a table row of the target's
  mass overwrites a deck `xscaptherm` / `xsptherm` / `xsalphatherm` (stock Fe-56 `xscaptherm 5000`: no number moves;
  the deck acts only on targets with no row, e.g. Fe-61, or on a column the row leaves empty, e.g. Fe-55 (n,p)). B10's
  urr.dat header now follows it too (output only). (2) The table is matched on A only, the last row of that mass wins.
  (3) A deck `integral <file> <spectrum> <value>` never gives a row: integral.f90:111-143 rebuilds the file name from
  reacstr, which only the sacs reader fills (stock: "cross section file .tot does not exist"); kept, with the warning.
  (4) natural.f90 sums all/total/elastic/nonelastic/reaction, <p>prod, rp*.tot/.Lnn, xs*.tot, fission, spectra
  (interpolated), the elastic angular file, recoils and yields; binary.tot, xs*.Lnn and the discrete-level files of a
  TALYS natural run are the LAST isotope's. The port sums every Results array (binary, isomer channels and levels
  included) and does not sum spectra / angular (left per isotope).
* **Vs stock** (`scripts/kwcov/b10b_response.py`; energies 2.53e-8 1e-7 5e-7 1e-3 0.1 1 MeV, TALYS adds 2e-7 and 1e-6;
  stock JSON in <work>/stock/b10b; every file stock writes for the rows below eninclow, stock > 1e-6 of its maximum):

  | deck | port (fill on stock's eref row) | engine vs stock, TALYS mode | default mode |
  |---|---|---|---|
  | Fe-56 | 2e-6 | 2.5e-6 | elastic / total rows x274 low (`lowepot` elastic at 1 eV); every other row 2e-6 |
  | Fe-56 `xscaptherm 5000` | 2e-6 | 2e-6, response 0 (stock 0: table quirk) | |
  | Fe-56 `elow 1e-4` | 0 | 5e-6, response 4e-6 | |
  | Fe-55 `xsptherm 2000` / `xsalphatherm 500` | 2e-6 | 5e-6 / 3e-6; response 2e-6 / 5e-6 (x70 / x76 moves) | |
  | Fe-61 (Kopecky) / `xscaptherm 5000` | -- / 2e-6 | 1e-6 / 2e-6, response 0.0 | |
  | Ag-109 (capture isomer branches) | 1e-6 | 4e-6 | elastic / total x9 low (`lowepot`); every other row 3e-6, isomer L00 / L02 included |
  | U-238 | 2e-6 | 6e-6 | elastic / total x3.7 low (`lowepot`); capture 0.22 % (the default-mode 1 eV capture) |

  Natural Fe (1 / 5 / 14 MeV, abundances 5.845 / 91.754 / 2.119 / 0.282 %): engine sums = weighted sums of its isotope
  runs to 2.2e-16; stock's natural files = weighted sums of stock's isotope runs to 3.8e-7 (binary.tot and xs*.Lnn
  excepted, see quirk 4); engine vs stock natural worst 15 % (rp025054 14 MeV), the engine's own Fe-56 14 MeV (n,p) /
  (n,a) excess (B1), nothing from the sum. integral y: port (integral.effective_b on stock's own xs files) <= 1.3e-6;
  engine vs stock in TALYS mode 3e-5 (Fe-56, five (n,p) rows; Co-59 (n,2n) L01 and total, (n,g) FNG-eurofer with the
  thermal rows, (n,a)); default mode Fe-56 (n,p) +10.5-10.8 % (the engine's default 14 MeV (n,p) excess, B1), Co-59 (n,a) 4.3 %, (n,2n) 0.9 %, (n,g) 0.0 %.
* **INCOGNITA vs TALYS below eninclow (recorded, not touched).** TALYS computes no model below eninclow (1 eV): its
  rows there are thermal.f90's 1/v extrapolation through the thermal value and a log-log join to the 1 eV
  Hauser-Feshbach number (Fe-56: capture 2.59 b at 0.0253 eV, 148 b at 1 eV, elastic 2399 b constant). The engine
  runs Hauser-Feshbach at every energy it is given (Fe-56 0.0253 eV capture 3,703 b, elastic ~8.8 b after `lowepot`,
  which removes the compound elastic below the resonance region; TALYS keeps it, 2399 b). The published library
  takes neither below 1 keV: resonance-fill curves (capture / elastic / total from resonance parameters, the v0.2.2 engine
  above the 1 keV join). B10b's rows are output only (`Results.thermal`); no default number moved
  (`test_engine_c.py`, B10b tests).
* **Not given:** rp*.Lnn rows below eninclow (the engine has no residual-isomer production output at any energy);
  thresholds between a low energy and eref (thermal.f90's Ethresh / Ethrexcl checks; a channel open at eref is open
  below it in practice); the URR files' rows below eninclow (urrout); resonance y, group y (PREPRO).
* Tests: `tests/hf/test_kwcov_b10b.py` (thermalxs table quirks and Kopecky, the grid insertion, the fill on stock's
  Fe-56 row, keyword parsing / ranges / refusals, Fe-56 run vs stock rows, Fe-55 xsptherm thermal point, the
  deck-change cache drop, natural Fe sums and `abundance`, the integral fold, sacs / spectrum readers and the deck
  triple bug).


### B11 -- medical isotope production

`prodinitial.f90:1`, `prodrates.f90:1`, `prodyield.f90:1`, `prodout.f90:1`, decay data `decaydata.f90:1`.
Post-processing of residual (and isomer) production -- needs B1-style isomer output and RESISO on.
Accept: p + Ni-nat or Zn-68 (p,x) yields/activities vs stock 1 % given the same residual production.

**Done.**

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
* **Vs stock** (`scripts/kwcov/b11_response.py --all`; stock runs `<work>/stock/b11_*`, trimmed to Y/rp files and
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

### B12 -- recoils and LAB frame (done)

`recoilinit.f90:1` (576 l.), `angdisrecoil.f90:1`, `recoilout.f90:1`, LAB DDX in `ddxout.f90`. Accept: Fe-56
14 MeV residual recoil spectra vs stock 3 %.

**Done.**

* **What.** `physics/hf/recoil.py` + `physics/hf/native/recoil.c` (`scripts/build_recoil_native.sh` ->
  `native/lib/librecoil.so`; Python twin `recoil.scatter_py` when the library is missing). TALYS's recoil module on the
  run's `specout` records (binary spectra, every cascade nucleus' mcontrib / mpecontrib with its grid) and angout's
  discad of every level: recoilinit (angle bins, LAB ejectile grid, the 50-bin kinematic sweep for Erecmaxmax, recoil
  grids, the initial CN bin), binaryrecoil, angdisrecoil (incl. the elastic), comprecoil inside a re-run of
  compemission, cm2lab, labsurface, binsurface (as written, with intri/sideline's quirk), totalrecoil, recoilout,
  the exclusive `sp*.rec` of channelsout, the LAB parts of spectraout / ddxout. New `Results.recoil`:
  `rec<ZZZ><AAA>spec.tot` (+ `:E`, `:integral`, `:production`), `sp<nnnnnn>.rec`, and with `labddx y`
  `<x>spec.lab`, `<x>ddx.lab`, `<x>ddxE<eeee.e>.lab`, `<x>ddxA<aaa.a>.lab`. `INCOGNITA_RECOIL_DIR` writes the files
  under TALYS's names. Keywords: `recoil`, `labddx`, `recoilaverage`, `maxenrec`, `anglesrec` (ranges refused as
  checkvalue.f90:483-484), `channelenergy` checked against stock; `filerecoil` stays NA (the arrays are always there).
* **Defaults untouched**: nothing runs without `recoil y`; with it, every other Results array is bitwise the same
  (test). Hooks: specout.begin_run / enabled, binspec.enabled, angout (discad of every level when recoil y),
  specobs.add_to_results.
* **TALYS quirks kept (all checked against stock):** the initial CN recoil energy is `sqrt(P^2+M^2)-M` in real(sgl),
  i.e. a multiple of the float32 spacing of M (1/256 MeV for Fe-57: Fe-57 recoil at 1 MeV centred 1.3 bins low;
  `INCOGNITA_RECOIL_EXACT=1` = double); `Emaxlab` and the residual's `Exmax` in real(sgl) (Fe-56 1 MeV: the LAB grid
  gets an 11th point, and level 1, the last one below Exmax, is DROPPED from the recoils because
  `Etotal - S - Exmax` rounds negative: stock's Fe-56 recoil integral is the elastic alone, 3199 mb, not
  3199 + 584 inelastic); the CN moves along the beam (angcm = 0); only the 0-degree discrete bin is renormalised
  (angnorm); the last recoil bin's extension leaves the mirrored areas; the LAB DDX at an energy interpolates with
  the CM grid's deltaE; binsurface's intri compares sideline's distances for equality (vertical/horizontal sides);
  the LAB gamma spectrum depends on the last bit of the angle/energy edges, so the kernel computes in single
  precision as TALYS (double: 25 % per bin on Fe-56 1 MeV gamma, single: 0.2 %).
* **Vs stock** (`scripts/kwcov/b12_response.py --all`, TALYS mode = fidelity.py's TALYS_DECK/TALYS_ENV; stock in
  `<work>/stock/b12/`, worst |ln| over 1/5/14 MeV and bins > 1 % of the file's peak):

  | deck | rec | excl | LAB spectra | LAB DDX | response |
  |---|---|---|---|---|---|
  | Fe-56 recoil y | **1.70 %** (14 MeV, 0.72 MeV tail) | 1.70 % | | | |
  | Fe-56 + labddx y, ddxmode 3, fileddxa/e | 0.89 % | 0.89 % | 0.83 % | **3.92 %** (n 150 deg, 8.6 MeV, 14 MeV) | 0.80 % |
  | + recoilaverage y | 0.89 % | 0.89 % | 0.83 % | 3.92 % | 0.04 % |
  | + anglesrec 4 | 0.89 % | 0.89 % | 0.83 % | 3.92 % | 0.02 % |
  | Fe-56 maxenrec 10 | 1.62 % | 1.62 % | | | |
  | Fe-56 channelenergy y | 1.70 % | | CM espec + xs 0.05 % | | |
  | Co-59 recoil y | **5.67 %** (14 MeV, 0.69 MeV) | 5.67 % | | | |
  | U-238 recoil y | **4.47 %** (5 MeV, 0.05 MeV) | 4.47 % | | | |
  | p + Nb-93 recoil y | 0.03 % | 0.03 % | | | |

  Fe-56 at 1 and 5 MeV: every recoil and LAB file to 1e-3 (gamma LAB 1 MeV 0.2 %). The engine-default run (no TALYS
  mode) differs at 14 MeV by the channels' own `npwindow` offset ((n,p) residual +12 %), not by the recoils.
* **Losses.** Co-59 / U-238: integrals and residual production agree to 0.3 % / 0.01 %, the worst bins are the
  high-recoil tail (1-5 % of the peak: backward-angle elastic / inelastic, i.e. the B3 discrete angular distributions
  at large angles), within 0.2 % above 10 % of the peak. LAB DDX 3.9 %: the CM DDX's isotropic giant-resonance /
  collective part (B4 approximation). Sub-mb ejectiles (h, t LAB spectra at 14 MeV, 1e-7 mb) follow the engine's own
  tiny channels. `blockspectra` / `blockddx` merged files are not written (one file per energy).
* **Bugs found:** in the port: none outside B12 (a charged projectile's `xselastot` is NaN in the angout record; the
  recoil code now takes TALYS's xselasinc = 0). In TALYS: the float32 cancellation of Erecinit and the dropped last
  level above (both reproduced, documented).
* Tests: `tests/hf/test_kwcov_b12.py` (binsurface incl. the quirk, labsurface area, C kernel vs Python twin,
  recoil grids = stock's 14 MeV grids, Erecinit quirk, Options / deck lines / refusals, one Fe-56 1 MeV engine run vs
  stock's recoil, LAB and LAB-DDX files to 0.5 %, `recoil y; outspectra n` = stock's discrete-only recoils, files
  written, every Results array unchanged).

### B13 -- ingredient outputs

`ingredients.py` already writes D0, Gg, S0. Add ld/psf tables, transmission and inverse cross sections, OMP
parameters under TALYS names, and `partable y` = `parameters.dat` (every parameter value the run used; what a
TASMAN-style sampler needs). Accept: Fe-56 parameters.dat identical keys, values 1e-5.

**Done.**

* **What.** New module `physics/hf/ingout.py` (output only). The deck keywords `outlevels`, `blocklevels`, `outdensity`,
  `filedensity`, `outgamma`, `filepsf`, `outinverse`, `outtransenergy`, `outomp`, `blockomp`, `outkd`, `partable` and
  the umbrella `outbasic` are Options now (`flaglevels`, `flagblocklevels`, `flagdensity`, `filedensity`,
  `flaggamma`, `filepsf`, `flaginverse`, `flagtransen`, `flagoutomp`, `flagblockomp`, `flagoutkd`, `flagpartable`,
  `flagbasic`; TALYS's cascade: outbasic sets outlevels / outdensity / outgamma / outomp / outinverse / outfission,
  filedensity follows outdensity). Before B13 every one was an NA line that changed nothing. Both drivers remember the
  run's Cascade at the start (`ingout.begin_run`) and fill `Results.ingout` (new field, empty by default) at the end with
  TALYS's files as {name: {header, blocks}}: `levels<ZZZAAA>.out` (levels.out with blocklevels), `ld<ZZZAAA>.gs` + `.bNN`
  per fission barrier, `nld<ZZZAAA>.tab[_bNN]`, `psf<ZZZAAA>.E1/M1/E2/M2`, `cross_g.tot`, `transmission_<p>.out`,
  `cross_<p>.tot`, `transmission_inc.out`, `omppar_<p>.out`, `omp.out` / `ompE<E>_<p>.tot`, `spr.opt`,
  `parameters.dat`, and `kd03` (talys.out's KD03 lines as a table). `INCOGNITA_INGOUT_DIR=<dir>` writes them with
  TALYS's names and layouts. Every number is read off the run's own ingredients (level densities, gamma parameters,
  transmission coefficients: cache hits) or recomputed with the run's functions (OMP parameters, ECIS mesh potential,
  the raw OMP solve for xsopt / total / elastic).
* **Defaults untouched**: nothing runs without one of the switches (`test_engine_c.py`); the Fe-56 run with every
  switch on has every other Results array bitwise equal to the run without (`test_kwcov_b13.py`).
* **Vs stock** (`scripts/kwcov/b13_response.py --all`; n + target at the energies listed, every B13 switch on; stock in
  `<work>/stock/b13`, trimmed to the B13 files; worst |ln(ours/stock)| per file over cells with stock > 1e-6 of the
  column's maximum; TALYS mode = the INCOGNITA defaults that are not TALYS switched off):

  | file family | Fe-56 (1, 14 MeV) | Co-59 (0.01, 5) | Pb-208 (14) | U-238 (1, 14) | tolerance used |
  |---|---|---|---|---|---|
  | levels*.out, levels.out (outbasic + blocklevels: 3151 rows) | identical | identical | identical | identical | exact |
  | ld*.gs tables / header | 0.001 % / 0.007 % | 0.001 % / 0.06 % | <= 0.001 % | 0.0002 % / 0.07 % (b01-b03 incl.) | 0.1 % (header Chi-2 D0: see below) |
  | nld*.tab (es9.2 print) | 0.63 % | 0.74 % | 0.69 % | 0.37 % | 1 % (3-digit print) |
  | psf*.XL | 0.0034 % | 0.0034 % | < 0.001 % | M1/M2 0.04 %; **E1/E2 89 %** | 0.01 % |
  | cross_g.tot | 1e-6 | < 1e-5 | < 1e-5 | **19.7 %** | 0.01 % |
  | transmission_*.out, cross_*.tot, transmission_inc.out | 0.0008 % | < 0.001 % | < 0.001 % | 0.035 % (incident) | 0.1 % |
  | omppar_*.out | 0.0004 % | < 0.001 % | < 0.001 % | < 0.001 % | 0.01 % |
  | omp.out (ECIS mesh, f8.5 step) | 0.023 % | 0.044 % | 0.016 % | 0.034 % | 0.1 % |
  | spr.opt | print | print | -- | print | print |
  | parameters.dat | keys identical (1499); 14 rows > print, worst Exmatch 5.2e-5 | 1160; 10 rows | 1345; 9 rows, worst 1.3e-4 | 2896; all to print | f10.5 / 1e-4 |
  | KD03 (outkd) | 0.05 % | 0.05 % | 0.04 % | **45 %** | print |

  Fe-56 other decks: `outtransenergy n; blockomp n` (per-L layout, ompE*.tot) <= 0.0006 % (alpha L = 19, T ~ 1e-8:
  0.72 %); `ldmodel 2; colenhance y; strength 8` (Krot / Kvib / Kcoll columns, D1M tables) ld <= 0.0004 %, header
  0.29 %; `outdensity y; filedensity n` identical (zeroed statistics); `outbasic y; blocklevels y` levels.out identical,
  ld / nld of every populated compound nucleus (Fe-55, Mn-56, Cr-52/53 ...) <= 0.012 % / 0.96 %.
  Default mode (Fe-56): ld026056.gs 18.7 % (`npwindow`, the target's continuum density by design), cross_h/t.tot and
  transmission_h/t.out up to x5 at a few near-threshold energies and omppar_h/t `avd` 36 % at the first energy (an
  INCOGNITA default of the composite-particle OMP; closed in TALYS mode, not isolated to one switch); the rest as TALYS mode.
* **Losses, traced.** (1) U-239 E1 (strength 9, temperature-dependent SMLO table) at Egamma = 0.4 and 0.6 MeV on the
  run's grid: port 9.08e-10 / 1.54e-9 vs stock 2.12e-9 / 1.01e-9 MeV^-3; every other energy to 1e-6. It moves psf E1/E2
  (the f column of E2 is f_E1, quirk) and cross_g.tot at those two rows, and the engine's photon transmission there
  (Tjl(E1) at 0.4 / 0.6 MeV): a port difference in the T-dependent table interpolation, **not fixed** in B13 (B15: cause = the double-precision table energies; fixed behind `INCOGNITA_FIDFIX=psfsgl`) (engine numbers;
  the U-238 capture was 0.00 % vs stock in FIDELITY1's TALYS mode). (2) KD03 for U-238: talys.out's first neutron
  block is global KD03 (Ef -5.01), the port's `omppar(92, 238)` returns a local entry (Ef -5.48, rv 1.244); the
  run's neutron OMP is RIPL 2408 either way (omppar_n.out agrees to 1e-5), so only the outkd table differs. (3) The CT
  matching energy Exmatch (and E0) of a few residuals, 2e-5..1.3e-4: TALYS's single-precision root; inside A-ld's 1e-4.
  (4) ld*.gs `Chi-2 D0` up to 8 % relative: the squared 1e-5 difference of D0theo. (5) nld*.tab: es9.2 rounding.
* **Bugs found.** (a) Port: `gamma/strength.fstrength_gp` tests `Egamma > 0.001` in double on the float32 grid point
  0.001 (TALYS: single, false), so the 1 keV E2/M2/pygmy terms TALYS drops are kept: cross_g.tot 1 keV row +27 % before
  the output-side fix (`ingout` evaluates that row at 0.001 exactly); the engine keeps it (T(E2) at 1 keV ~1e-24, no
  visible number), recorded. (b) Port: `strength 1` (and the other legacy strengths) is accepted; TALYS-2.25 refuses it
  without `legacy y` ("strength = 8, 9, 10, 11, 12 or 13 are recommended") -- checkvalue gap, not B13, left for B15
  (`legacy`). (c) The B10b/B11 notes hold: no second-run cache issue seen (each b13_response engine run is its own process).
* **TALYS quirks kept.** psf .E2/.M2 f column = f(l=1) (gammaout.f90 calls fstrength with l = 1); `filepsf y` without
  `outgamma y` writes nothing; psf header "experimental Gamma_gamma [eV]" is TALYS's gamgam in keV and C/E uses it
  (Fe-57: C/E 1417); `outdensity y; filedensity n` zeroes the D0 statistics and Exp_LD; the T column of psf files is
  indexed by the row number (rows past eend(0) are 0); levels*.out written after a second `levels` read keeps the first
  branch list with the conversion coefficients by file index (Co-59 level 11: conv 2.381e-3 on the branch to level 2);
  with outbasic, structure.f90 writes levels for every nucleus it builds (even with outlevels n) and multiple.f90 the
  densities / levels of every populated compound nucleus (flagpop); spr.opt only at the first energy or Einc <= 0.1;
  transmission_inc.out holds the last energy.
* **Not given (NA rows / later).** outbasic's gamma*.tot decay schemes (gammadecay), population / check / direct
  output; JLM `radial.out` (B7b: JLM ported, radial.out not given); `endf y`'s levelsout (B15: done). The parameters.dat nucleus list uses the
  run's residual production >= 1e-3 mb for TALYS's population test (keys identical on all four decks).
* Tests: `tests/hf/test_kwcov_b13.py` (keyword cascade and deck lines, the D0 statistics, one Fe-56 engine run vs
  stock numbers, every other Results array bitwise unchanged, the file round trip, filepsf without outgamma).

### B14 -- fission yields, fragment evaporation

`massdis.f90:1` (Brosa, 779 l.), GEF (7,264 l., `fymodel 2` default), `ffevap.f90:1`, `massdisout.f90:1`,
`nudisout.f90:1`. Accept: Y(A) vs stock 2 % at the peaks (TALYS mode), keyword responses 2 % on the change.

**Split (decided in part 1).** TALYS-2.25 runs, with `massdis y` on a fission run: `massdis` (yields per fissioning
nucleus and excitation bin), `massdisout` (yield files) for fymodel <= 2, `nubarout` + `nudisout` for fymodel 2, and
`ffevap` (fragment decay: nu(A), P(nu), PFNS/PFGS, isomer split, then massdisout/nubarout/nudisout/pfnsout) for
fymodel >= 3. The three parts follow those paths:

| part | models / keywords | TALYS routines | output |
|---|---|---|---|
| **1 (done)** | massdis, fymodel 1 (Brosa), ffevaporation (Brosa's step sizes and FP estimate), rfiseps (fpeps), outfy / gefran / ffmodel / yieldfile / ffspin read (inert with fymodel 1, as stock) | massdis (fymodel 1 branch, normalisation), brosafy, neck, trans/trapzd/funcfismode, fmin/fidi, shape helpers, massdisout | yieldA / yieldZA / fpZZZAAA / fpAAA / rpZZZAAA (FP xs) |
| 2 | fymodel 2 (GEF, TALYS's default once massdis is on), gefran, outfy (gefwrite), the GEF nubar / nu(A) / P(nu) (nubarout, nudisout for fymodel 2); fymodel 4 file path (ffmodel 0-4, yieldfile, structure/fission/ff tables) | geftalys.f / gefsub.f / geffunctions.f (7,264 l., Monte Carlo with gefran events: compare statistically or port the RNG), nubarout, nudisout | yields + nubar*.tot, nuA, Pnu |
| 3 | fymodel 3 / 4 / 5 with ffevap (fragment evaporation by TALYS's own decay), ffspin, pfnsmodel 2 (PFNS / PFGS from fragment decay), the isomer split (yieldfpex / fpratio, `fpZZZAAA.tot` i00/i01 files) | ffevap.f90, ffgammaspec.f90, the per-fragment population files (ff*.ex) | nu(A), P(nu), PFNS/PFGS, isomeric FP yields |

Since part 2, `massdis y` alone runs GEF (fymodel 2); fymodel 3-5 were REFUSED (`NotImplementedError` naming part 3; since part 3 only fymodel 3 is);
before B14 `massdis y` ran the cascade with its defaults and gave no yields.

**Part 1 done.** New module `physics/hf/fisyield.py` (output only);
hooks in engine_c (`cases`: `fisyield.begin_run`, `fisyield.record` next to fisobs's on the same cascade result;
`run`: `fisyield.add_to_results`), `Results.fission_yields` (new field, empty by default), `Options.yieldfile` (read),
deck.py (natural targets with massdis refused, checkvalue.f90:1075). Without `massdis y` nothing is computed:
`test_engine_c.py` passes unchanged.

* **What it gives:** `Results.fission_yields` = {TALYS file name: {column: ndarray}}: `yieldA<E>.fis` (A, FP_yield,
  FF_yield, FP_xs, FF_xs, `Tot`), `yieldZA<E>.fis` (the rows TALYS writes), `fpZZZAAA.tot` / `fpAAA.tot` over the run's
  energies, `rpZZZAAA.tot` (TALYS's name for the fission-product cross section; kept in this dict, apart from residual
  production). Brosa in TALYS's single precision (np.float32), double where TALYS has dbl (mode transmissions, level
  density through the engine's `ignatyuk` / `density(..., ldmodel 1)` of each fissioning nucleus).
* **TALYS quirks kept:** trapzd.f90 resets `snew` at entry (no running trapezoid: each refinement is half the midpoint
  sum); fidi.f90 sets the neck globals as a side effect, so neck.f90 continues from the LAST simplex evaluation, not the
  best vertex; fmin returns the value of the last ranking; massdis skips the bins nex = 0-2 (`nex - istep + 1 < 0`);
  every bin above 30 MeV is merged by four. Zeroed where TALYS reads stale static arrays (neck's zdis / wgt for
  skipped charge steps; never reached for actinides).
* **Vs stock** (`scripts/kwcov/b14_response.py`, TALYS mode = fidelity.py's TALYS_DECK / TALYS_ENV; stock files
  trimmed to yieldA / yieldZA in `<work>/stock/b14/`), worst |ln(ours/stock)| over the energies:

  | target, energies | FF peaks (>= 50 % max) | FF (>= 1 %) | FP peaks | FP (>= 1 %) | isotopic FF (>= 1 %) | FF cross section |
  |---|---|---|---|---|---|---|
  | U-235 1, 5 MeV | 0.011 % | 0.029 % | 0.17 % | 0.35 % | 0.23 % | 0.01 % |
  | U-238 1, 5, 14 MeV | 0.061 % | 0.22 % | 0.68 % | 1.15 % | **2.6 %** (Br-87, 1 MeV) | 1.0 % (14 MeV) |
  | U-235, default mode | 2.1 % | 2.1 % | 2.3 % | 2.3 % | 2.6 % | 2.1 % |
  | U-238, default mode | 0.34 % | 1.4 % | 0.68 % | 1.5 % | 2.6 % | 9.1 % (5 MeV: the engine's default fission, `exactfis`) |

  Default mode differs by the deliberate fission defaults (`exactfis` changes the per-chance fission and so the mix of
  fissioning nuclei and excitation energies; `npwindow` the densities); that is why acceptance is in TALYS mode.
  The isotopic 2.6 % is a charge-wing row (yield 1-2 % of the max) and follows the float32 neck sums.
* **Responses** (|ln(R/S)|, FF and FP mass yields where stock >= 10 % of the max):

  | deck line (from `massdis y; fymodel 1`) | worst | stock moved |
  |---|---|---|
  | ffevaporation n (U-235) | 0.005 % (FP: 0 on both sides) | 6.0 % |
  | rfiseps 1e-3 (U-235) | 0.001 % | 0.0 % |
  | rfiseps 0.12 (U-238: drops U-239 below fpeps) | 0.16 % | 10.4 % |
  | outfy y; gefran 1000 (U-235) | 0.000 % | 0.0 % |

* **Loss, traced (bug found):** the FF cross section at U-238 14 MeV is 1270.7 vs 1257.5 mb (1.0 %): `massdis y` sets
  `transpower 10` (input_numerics.f90:83-88) and the engine never reads `transpower` (translimit stays 1e-5 in
  core/grids.py / omp/inverse.py). Stock `transpower 10` alone moves U-238 14 MeV fission -0.75 %, ours 0 (1270.682 mb both; the rest is
  transeps / xseps / popeps). Yields are normalised and do not see it. `transpower` is now IGNORED in the keyword table
  (was SUPPORTED by grep); wiring it touches the OMP / inverse lmax cut and is left for a numerics batch.
* **Not given:** GEF and fymodel 3-5 (parts 2/3, refused); the isomer split of fission products (only ffevap fills it:
  with fymodel 1 TALYS writes none either); nubar / nu(A) / P(nu) (nubarout / nudisout run for fymodel 2 only); the
  engine.py (Python) driver computes no yields (as fisobs, engine_c only).
* Tests: `tests/hf/test_kwcov_b14.py` (shape helpers, spline / bisection, file names, refusals and ranges, deck lines,
  Brosa modes on a model level density, U-235 1 MeV engine run vs stock numbers, no yields without massdis, natural
  targets refused).

**Part 2 done.** New module `physics/hf/gef.py` (geftalys.f, 3,160 lines, with
the geffunctions.f functions it calls: LyMass, ECOUL, TEgidy, Getyield, BFTFB/BFTF/LDMass/AME2012, Gaussintegral);
`fisyield.py` gains massdis.f90's GEF branch (bins per fissioning nucleus, `xsApre += 0.5 ysum`, nubar / nu(A) / P(nu)
with Fmulti), nubarout / nudisout's files (`nubarn.tot`, `Pnun<E>.fis`, `nunA<E>.fis`, `nunZA<E>.fis`) and the fymodel 4
reader (`ff_files`, `ff_pairs`). gefsub.f (fymodel 3) is part 3 (it only feeds ffevap). Output only: without
`massdis y` nothing runs and `test_engine_c.py` is unchanged.

* **Random numbers, decided:** GEF's generator is the MCNP 48-bit LCG of geftalys.f (`ran2`, reseeded 5^19 at every
  geftalys call; `rndm = sngl(ran2)`), ported exactly; PGauss's cached Gaussian is a SAVE variable (DATA ISet 1, GSet
  0.5) that carries across nuclides and incident energies, also ported. Two layouts of the same event code:
  `INCOGNITA_GEF_STREAM=talys` runs stock's single stream event by event (python speed: 2.8 s per 1000 events, for
  checks); the default `lanes` runs all events of a bin in lockstep, one lane each (0.55 s per bin at 50,000 events,
  60 MB), lane i on its own hashed odd 48-bit start (`gef.lane_seeds`, splitmix64; `INCOGNITA_GEF_SEED` shifts them).
  Each lane draws exactly stock's per-event sequence, so the default agrees with stock statistically and is
  deterministic.
* **Exact match (stock stream):** stock `massdis y; outfy y; gefran 1000` prints geftalys's per-bin tables (yields per
  mode, N and A yields pre/post, nu per A pre/post, P(nu), mean). U-235 1 MeV, all 30 bins of U-236 (30,000 events, 1.8M
  draws) and 5 MeV, all 53 bins of U-236 + U-235: **every printed number equal** (5-9 digits). Engine end to end, TALYS
  mode, U-235 gefran 1000: 1 MeV every yieldA / nunA / Pnun entry 1e-5 relative (the bin cross sections differ at that
  level), nubar 0.001 %; 5 MeV FF yields 0.02 % (worst, 1 % of max), nubar 0.001 %, P(nu) 0.03 %, FP *cross sections*
  1e-4, but FP *yields* per A up to 2 % (A = 94, 95) and stock-only rows at A = 110-121: see the loss below.
* **Statistical match (default lanes, 4 seeds x 50,000 events vs stock gefran 1,000,000, TALYS mode):**

  | target, E | mass-yield chi2/dof (FF, FP; A >= 1 % of max, Poisson) | worst peak bin (expected sd) | nubar ours / stock |
  |---|---|---|---|
  | U-235 1 MeV | 0.73, 0.89 | 1.7 %, 2.5 % (1.0, 1.2 %) | 3.0088 / 3.0099 (0.04 %) |
  | U-235 5 MeV | 1.11, 0.78 | 2.9 %, 2.3 % (1.3, 1.1 %) | 3.5337 / 3.5341 (0.01 %) |
  | U-238 1 MeV | 0.61, 0.77 | 1.7 %, 1.9 % (1.0, 0.9 %) | 2.7617 / 2.7606 (0.04 %) |
  | U-238 5 MeV | 0.80, 0.90 | 1.7 %, 1.9 % (1.4, 1.2 %) | 3.4663 / 3.4671 (0.02 %) |
  | U-238 14 MeV | 0.06, 0.07 (many bins: Poisson var overstated) | 0.56 %, 0.54 % (seed sd 0.13 %) | 4.6639 / 4.6624 (0.03 %) |

  U-238 14 MeV keeps a ~0.5 % peak residual beyond its 4-seed spread: the fission cross section there is 1.0 % off
  (part 1's transpower loss), which moves the chance mix; yields are normalised, so it shows only at this level.
  Lanes vs the stock stream inside the port (one bin, 40,000 events, 4 seeds): chi2/dof 0.77-1.14 pre- and post-neutron.
  The plan's "2 % at the peaks" is not testable bin by bin against stock's default 50,000 events: a peak mass bin
  carries 1.8 % sampling noise on each side (worst of ~20 peak bins 4-6 %, as found first); hence the 1e6 stock runs.
* **Bug found and fixed (ours):** the first lane layout jumped the stock stream by 2^26 per lane; for this LCG
  G^(2^k) = 1 mod 2^(k+2), so the lanes were shifted copies of each other in their top bits and biased the Box-Muller /
  rejection draws (peaks 3-5 %, z up to 8 vs stock). Hashed starts fixed it (chi2/dof ~1 above).
* **Loss, traced (engine, not GEF):** stock lists fission in deeper sub-barrier bins than the engine (U-236 at 5 MeV:
  34 bins down to Ex 3.11 MeV vs ours 31 down to 3.89; U-235 second chance 19 bins vs 12): their cross sections are
  <= 0.03 mb (the engine's fisfeedex is 0 there). They matter only through two TALYS conditions: (1) massdis counts a (Z,A)
  FP yield only where that nuclide's FF cross section is non-zero, so rare (Z,A) seeded by those bins add FP yield in
  stock (A = 94/95/120 at 5 MeV, up to 2 % of a peak bin; FP cross sections agree 1e-4); (2) nu(A) and P(nu) add
  Fmulti/xsfistot (= Ncomp xsfeed / xsfistot, 0.11 for U-235 5 MeV) wherever a nucleus has any event, so rare masses
  / multiplicities jump by 0.1 (nu(A) A = 110-120, P(nu > 8)). The same conditions make these rows sampling-noise driven in
  the statistical comparison (P(nu = 11) at U-238 14 MeV differs by the Fmulti step).
* **TALYS / GEF quirks kept:** P(nu) counts only events with >= 1 neutron and nubar is the mean of that conditional
  distribution (U-235 1 MeV: 3.01; evaluated about 2.5); Pdisnu normalised over nu = 1..numin (8), nu > 8 left raw plus
  Fmulti; nu(A) per pre-neutron mass over fragments with 1..20 neutrons; the stale `A1` in the heavy-fragment spin and
  the Fermi-gas energy split; mode 3's yield uses PShellS3 (not RShellS3eff) in TEgidy; mode 4's light width uses
  beta(2,2,Z); mode 2's discarded PGauss before PBox; Ivenodd clamps the even-odd table in place; PEgammahigh never
  fills sigma(N); `Erf` is Numerical Recipes in geftalys but the gfortran intrinsic in Gaussintegral (ERF typed, not
  EXTERNAL). Diagnostic arrays (Edefo2d, Eintr2d, ...) dropped; stock indexes some out of bounds (Eintr2d with E < 0),
  harmless in its static layout (the exact match holds).
* **Keywords:** `gefran` acts (events per bin, range checked); `outfy` prints only, as stock (the tables are
  `geftalys(detail=True)`); `ffmodel` / `yieldfile` feed the fymodel 4 reader, whose run stays refused (ffevap, part 3);
  fymodel 3/4/5 refused naming part 3.
* **fymodel 4 reader:** `ff_files` (database file at the two tabulated energies around Etotal, or `yieldfile`) and `ff_pairs` (filters, linear interpolation incl. TALYS's light-then-heavy overwrite of Y0 / TKE / TXE): U-235 1 MeV (U-236, Etotal 7.541 MeV, gef files at 7 and 8 MeV) all 207 pairs equal to stock's printed table (11 columns, <= 4.8e-6 relative = es12.5). The run itself stays refused (ffevap, part 3).
* **Not given (part 3):** fymodel 3 (gefsub.f), 4 and 5 runs (ffevap), ffspin, pfnsmodel 2, isomer split, nuZA rows
  (only ffevap fills nuZA / Pdisnuav). The engine.py driver computes no yields (engine_c only).
* Tests: `tests/hf/test_kwcov_b14b.py` (generator = ran2, PGauss SAVE state, float32 helpers, BFTFB / mode yields of
  U-236 bin 1, the bin-1 tables vs stock's printout on the stock stream, lanes statistics and determinism, settings and
  refusals, the numin quirk, nubarout's zero rows, fymodel 4 files, U-235 1 MeV engine run vs stock); part 1's
  test_kwcov_b14.py updated (fymodel 2 accepted). `scripts/kwcov/b14b_response.py` (exact `--stream talys`,
  statistical `--stat N [--stock-kw "gefran 1000000"]`). Stock refs `<work>/stock/b14b/` (trimmed).

**Part 3 (slices 1, 3 and 5 done).** New module `physics/hf/ffevap.py` (ffevap.f90,
excitation.f90, read_energies.f90's projectile-0 branch); fisyield gains massdis.f90's fymodel 4 / 5 branches
(`_fymodel4`, `_fymodel5`), the isomer rows / files and the per-ejectile nu files (`build_nu_ff`). Output only: the
fragment loop runs in `fisyield.add_to_results` after the energy loop (TALYS runs it after each energy's output and
re-initialises the target, so the main run cannot see it). Without `massdis y` nothing runs; `test_engine_c.py` is
unchanged.

* **How a fragment is evaporated (decided):** TALYS runs a whole TALYS calculation per fragment (evaptalys.f90): the
  fragment is the target, `projectile 0` with the population file ff<ZZZ><AAA>.ex, fission off, the deck's other
  lines. The port does the same through the engine's own C cascade (`engine_c.cascade`) on a `Cascade(Zff, Aff,
  k0 = 0)`: `INCOGNITA_CPINC=g` for the loop (the photon projectile's defaults are projectile 0's), deck + `fission n`
  + `nnleak n` (`nnleak`'s premise -- a top bin fed by primary photons -- does not hold for an input population),
  Etotal = Einc (energies.f90:130), lmaxhf(0, 0) = gammax, maxJ with ipop = 1 (Rspincutff, exgrid.f90:250; new
  `Cascade.ffruns_rspincut`, None on every other run), the (0, 0) population from excitation.f90 as the cascade's
  type-0 seed, multiplicity = (sum of xsfeed + the discrete gammas over 1 + conversion) / xsinitpop, residual.f90's
  xseps floor. Speed: U-235 1 MeV, 411 fragments, 167 s for the whole run (stock 12.5 min).
* **fymodel 4 vs stock** (TALYS mode, `scripts/kwcov/b14c_response.py --target u235|u238`, |ln(ours/stock)|, worst):

  | quantity | U-235 1 MeV | U-238 5 MeV |
  |---|---|---|
  | fragments evaporated / their initial population | 411 = 411 / 0.005 % | 432 = 432 / 0.096 % (the run's fission xs) |
  | FF yields (A, Z-A) | 0.000 % | 0.000 % |
  | FP (post-neutron) yields, peaks / >= 1 % of max | 0.51 % (A 91) / 2.0 % (A 153) | 0.20 % (A 104) / 0.84 % (A 153) |
  | FP isotopic >= 1 % of max | 3.5 % (Nd-153) | 4.7 % (Nd-152) |
  | isomer rows / isomeric ratios (FP >= 1 % of max) | 126 = 126 / 0.054 % (Y-97) | 106 = 106 / 0.072 % (Y-97) |
  | nubar_n | 0.012 % (2.48133 vs 2.48162) | 0.018 % (3.06189 vs 3.06243) |
  | nu_n(A), FF yield >= 1 % of max | 0.36 % (A 154) | 0.29 % (A 92) |
  | per-fragment neutron multiplicity (>= 0.05) | 0.61 % (Nd-154) | 0.81 % (Ga-82) |
  | nubar_g | 0.71 % (7.8373 vs 7.7821) | 0.60 % (7.9157 vs 7.8684) |
  | per-fragment gamma multiplicity | 5.6 % (Sb-130; Zr-100 +1.3 %, Sr-96 +1.0 %) | 5.0 % (I-134) |
  | P(nu) | 0 = 0 (channels n) | 0 = 0 |

* **fymodel 5 vs stock** (own spin-dependent populations of Kr-92, Ba-144, Sr-96, Xe-140 at U-235 1 MeV,
  `--fy 5`): every number equal to print precision (nubar_n, nubar_g 0.0000 %, per-fragment multiplicities <= 3e-6).
* **Bug found and fixed (ours): transpower / transeps never reached the outgoing channels' lmax** (part 1 found
  transpower ignored). `compound/dens_reference._lmax_inverseread` took the defaults 1e-5 / 1e-8 whatever the deck
  said; `massdis y` sets 10 / 1e-12 (input_numerics.f90:83-88). Near-threshold neutron emission of high-spin fragment
  states needs those extra partial waves: Sb-134 neutron multiplicity stock 1.00455, ours 0.8836 before, 1.00438
  after (standalone population run; `transpower 10` alone 0.90413 / 0.90392). Now `_trans_cut(options)`; the
  defaults return the old constants (bit-identical default runs). The incident channel's lmax (incidentread.f90:287)
  still takes 1e-5 (left; it is the main run's).
* **TALYS quirk kept: misaligned conversion coefficients.** levels.f90:177-183: a nucleus whose levels are read a second
  time (dtheory of its (Z, N-1) neighbour reads (Z, N)) keeps its first branch list but re-takes the conversion
  coefficients by FILE branch index, misaligned where a zero-ratio branch was dropped. Zr-99 level 7 (two zero
  branches with alpha = 2780, 18250 first): its lines in stock are 2,800 and 18,000 times smaller than the cascade
  intensity. The gamma multiplicity counts them that way; the port uses `discrete_levels(prior_call=True)` for every
  nucleus whose (Z, N-1) neighbour is in the cascade (nubar_g 0.88 % -> 0.71 %).
* **Loss, partly traced: gamma multiplicity of spin-less (fymodel 4) populations.** With spins given (fymodel 5) the
  gammas are exact; with fymodel 4's Wigner spins (sc = spincut(ipop = 1) at the population maximum, ~4x the normal
  cutoff) and maxJ(ipop = 1) truncation ours is +0.7 % on nubar_g. Sr-96 (largest fragment): the discrete lines per
  nucleus agree 0.0-0.3 % (outgamdis), the continuum gammas are +2.5 % while its neutron multiplicity agrees 0.06 %:
  more photons per cascade at the same neutron count, i.e. a slightly higher spin population; the J tail at maxJ ~ 30
  (~1-3 % of the Wigner distribution) is the suspect. Neutron observables and yields are not affected at that level.
* **Not given (open slices):** pfnsmodel 2 spectra (ffevap.f90:322-341 lab transform, ffgammaspec.f90, pfnsout.f90;
  `outspectra y` with fymodel >= 3 is refused -- they need the fragment runs' emission spectra xssumout and Eaverage,
  and EavZA / EavA stay zero as stock without spectra); fymodel 3 (gefsub.f, 2,057 lines: GEF per fission event with
  excitation and spin per fragment, then the same ffevap; refused); P(nu) from the fragment runs' exclusive channels
  (`channels y` refused with fymodel >= 3; TALYS's default channels n gives zero P(nu), as here); `popmev y` and
  one-bin populations (refused in excitation). ffspin acts only with fymodel 3: inert, as stock.
* Tests: `tests/hf/test_kwcov_b14c.py` (fymodel 4 population rows = stock's file, spindis / Edistmax, excitation
  spin-less and with spins, the run directory of fymodel 5, pairs to fragments, settings and refusals, the new files,
  three fragment runs vs stock's talys.out incl. the Ga-74m / Zn-77m isomer split); part 2's refusal test now fymodel 3
  only. Stock refs `<work>/stock/b14c/` (trimmed: yield / nu / Eav files, frag_summary.json = talys.out's per-fragment
  reaction summary).

### B15 -- low value (done)

Builds on B1-B13 and the port fixes (`INCOGNITA_FIDFIX`, `FIDELITY_DEFAULTS.md`). Stock TALYS-2.25 references:
`<work>/stock/b15/` (n + Fe-56: `endf y` at
1/5/14 MeV, `sacs y` at 2-20 MeV with and without channel files, `components y`, and the refused decks' TALYS-error
lines). Responses by `scripts/kwcov/fidelity.py --response` (`|ln(R/S)|`, worst over channels > 1 mb at 1/5/14 MeV).
Tests: `tests/hf/test_kwcov_b15.py`.

**Decisions (no questions, recorded).**

| keyword | now | how / why |
|---|---|---|
| legacy | SUPPORTED | `defaults.check_values` (called by `reject_unported` at the start of a calculation): without `legacy y`, strength <= 7, strengthM1 not 3/8/10/11/12, ldmodelCN or any (per-nucleus) ldmodel 3/4/6 stop the run with TALYS's own message (checkvalue.f90:803-813, :953-966; stock Fe-56 `strength 1` / `strengthm1 2` / `ldmodel 3` print the same lines). They ran silently before. `legacy y` runs them: Fe-56 `legacy y; strength 1` response 0.60 % default / 0.66 % TALYS mode ((n,np) 14 MeV), `legacy y; ldmodel 3` 1.62 % default / 0.00 % TALYS mode |
| transpower | SUPPORTED (follow-up from B14) | was parsed and never reached the cut. Now `translimit = 1/10**transpower` and `transeps` go to every lmax cut of a transmission read (`omp/inverse.set_eps` from `default_options`; `process_tjl`, `schrodinger._lmax_talys`, `dens_reference._lmax_inverseread`), and a non-default pair adds a token to the stage-cache key. Range 2-20 checked (checkvalue.f90:475). Defaults bitwise (1e-5 / 1e-8, key unchanged). U-238 `transpower 10`: stock fission 14 MeV 1270.62 -> 1261.01 mb (-0.76 %), engine TALYS mode 1270.68 -> 1261.07; worst response 0.44 % default / 0.43 % TALYS mode (capture 14 MeV, 1.12 -> 1.11 mb). Fe-56 `transpower 10` / `transeps 1e-12` 0.00 %, `transpower 2` 0.29 % / 0.00 %. `massdis y` (transpower 10, transeps 1e-12) and `astro y` (15, 1e-18) now act through it too |
| transeps | SUPPORTED | B9 took it to the chain's T cut; B15 adds the lmax cut (above) |
| endf | SUPPORTED | cascade as before (eninclow from D0, urr y, channels y, adddiscrete 30 MeV, output switches) + structure.f90:75's levelsout and gammadecay for every nucleus structure builds (`ingout.gamma_decay_file`, gamma<ZZZAAA>.tot) + endfinfo.f90's tefal.inf / energies.endf (Ninc > 1). Stock Fe-56 `endf y`: the same 46 files; levels*.out identical, gamma*.tot <= 1e-6 (print), tefal.inf / energies.endf identical. Response Fe-56 0.00 % (both modes), U-238 0.00 % (TALYS mode). **Not given:** endfenergies / endfecis / endfread (ECIS on the ENDF incident grid: endf.cs, endf.tot, endftot.tot, endfel.tot, endfnon.tot) and channelsout's discrete-gamma xs*.gam -- TEFAL inputs, recorded in the observable row (PARTIAL) |
| endfdetail | SUPPORTED | cascade only (gamdis / channels / filechannels defaults with endf y, tefal.inf's line); Fe-56 `endf y; endfdetail n` response 0.00 % |
| sacs | SUPPORTED | `ingout.sacs_table` (sacs.dat): on stock's own Fe-56 xs files it is stock's sacs.dat; engine Fe-56 2-20 MeV: channel list, order and thresholds identical, xsmax / FWHM are the engine's default cross sections. Quirk kept: TALYS reads the xs*.tot it wrote, so without channel files (`sacs y` alone) sacs.dat is the header only |
| components | READ_ONLY_DEFAULT (refused) in B15; **SUPPORTED since B4b** (compoobs.py, see B4b; this row is the B15 state) | `components y`: Fdir / Fpreeq / Fcomp per residual (multiple.f90:649) and the extra xs*.tot / rp*.tot columns are not carried by the port's cascade; refused with a clear message (`defaults.UNPORTED`) |
| micro | SUPPORTED | B7b: `micro y` now runs (JLM ported; Fe-56 response 0.04 % TALYS mode); before B7b it was refused through jlmomp y; `micro y; jlmomp n` runs ldmodel 7 + autorot: response 0.00 % TALYS mode, **78 % default** ((n,p) 14 MeV: `npwindow` acts on the ldmodel-7 Fe-56 density; deliberate default, as FIDELITY1) |
| densfile, e1file, m1file, massdir | READ_ONLY_DEFAULT (refused) | external user tables; kept refused (decision): each needs its own reader path (densitytable.f90:113, gammapar.f90:521 incl. the forced wtable 1 and the strength 1/2/5 table branch, masses.f90:139) |
| rescuefile, strucpath, bestpath | READ_ONLY_DEFAULT (refused) | were NA and skipped silently; rescuefile renormalises returned cross sections (normalization.f90), the two paths name another database. Deck line refused, best-file line warned |

**Port bug fixed (`INCOGNITA_FIDFIX=psfsgl`, opt-in in B15, default ON since the KWCOV integration): U-239 E1 at 0.4 / 0.6 MeV (B13 loss (1)).** Cause:
TALYS holds the tabulated PSF energies in single precision: `qrpa%e = ee + etable` and the wtable stretch
`Emid + (Eq - Emid) * wt` (gammapar.f90:268, :574-578) are real(sgl), so even at wt = 1 the stretch moves a table
energy by a few 1e-7 (U-239 smlo2019 Emid 13.1: 0.4 -> 0.39999962, 0.6 -> 0.60000038), and Tqrpa is the
single-precision running sum of 0.2 steps (gammapar.f90:311-321). The port did both in double (0.40000000000000036 >
Tqrpa 0.4). At a gamma energy on a table point that equals a Tqrpa temperature, `locate` and fstrength.f90:401-411's
`eb <= et` / `ee <= et` choice between the temperature column jt and the photoabsorption column went the other way.
Fix (`gamma/parameters.py` table_arrays + Tqrpa, `fidfix.py`): the energies are TALYS's single-precision values
(straight-through, the etable / wtable gradients are kept); the GPU capture path refuses under the fix and the CPU
paths (strength.py, psf_fast.py, nx2 C) read table_arrays. U-239 f_E1: 0.4 MeV 9.08e-10 -> 2.1185e-9 (stock
2.1185e-9), 0.6 MeV 1.536e-9 -> 1.0096e-9 (stock 1.0096e-9); every other energy moves ~5e-7 relative. Impact (engine,
U-238, 0.1/0.5/1/5/14 MeV): capture 0.5 MeV 81.32 -> 81.23 mb (-0.11 %) at default, TALYS mode 81.36 (+0.12 % vs
stock) -> 81.26 (0.00 %); every other cell <= 0.01 % (default fission 5 MeV -0.01 %). More targets in
FIDELITY_DEFAULTS.md section 6. Turning it on by default is the integration step's call.

**Owners of what is left** (status IGNORED / MISSING after B15): massdis, fymodel, ffmodel, gefran, ffevaporation,
ffspin (IGNORED), yieldfile (MISSING) -> B14; jlmmode, radialmodel, radialfile -> B7b (done). Every other
keyword is SUPPORTED, NA, or refused with a message (READ_ONLY_DEFAULT). `ltarget`: the isomeric-target gap, done
(below).

## Isomeric targets (done)

Design and results: `ISOMERIC_TARGETS.md`. `ltarget L` runs the target on its level `L` as TALYS does: the level's
spin, parity and energy (`structure/scalars.py`; targetE in Etotal and the grid top since ENGFIX4), no DWBA level and
no giant resonance (direct.f90:33, `direct/chain.py`) while the incident coupled-channels inelastic of a deformed
target is kept (incidentread.f90:381-394), no collapse of the pre-equilibrium continuum onto the levels
(preeqcorrect.f90:90), level `L` as the elastic channel (the binary / compound code was already written on
`ltarget`). Port bug found on the way: the complex-particle pre-equilibrium (knockout / stripping / breakup) took
eninccm = Etotal - S(0,0,k0), i.e. eninccm + targetE (Fe-56 `ltarget 1` 14 MeV (n,a) -1.6 %); fixed
(`preeq/complex._eninccm`). TALYS mode vs stock TALYS-2.25 (1/5/14 MeV): Fe-56 levels 1 and 2 <= 0.01 % on every
main channel and level; Am-242m (level 2, 5-, fission, coupled channels) <= 0.03 %, (n,p) 14 MeV +1.3 % (2.7 mb;
ground state +0.47 %). TALYS's checks (Ltarget <= 40, the level must exist, no natural target) are made. Refused:
ltarget with liso, projectiles other than n, the outputs of `defaults.LTARGET_UNPORTED`. Test:
`tests/hf/test_kwcov_biso.py`; comparison `scripts/kwcov/biso_compare.py` / `biso_stock.sh`.
