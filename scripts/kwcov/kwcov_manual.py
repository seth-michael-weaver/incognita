"""KWCOV hand-checked keyword rows: they override inventory.py's automatic class.

keyword -> (status, where, notes[, evidence]). Checked 2026-11-08 against origin/main 05fa5f70 by reading the code
named in `where`; "env" means the feature exists behind an INCOGNITA_* switch rather than the TALYS keyword.
"""
NA_PREFIXES = ("out", "file", "block")
NA_WORDS = frozenset({
    "user", "source", "format", "nulldev", "strucpath", "bestpath", "partable", "sacs", "ecissave", "eciscalc",
    "inccalc", "endfecis", "ecisdwba", "legacy", "reaction", "rescuefile", "components", "integral",
})

_F = "input/fitlib.py "
_T = "test:test_kwcov_b2.py"
_FITLOSS = ("fit y Fe-56 14 MeV: (n,p) 4.0 %, (n,a) 3.3 %, (n,d) 2.8 % off, traced to two engine responses: "
            "gadjust on the compound nucleus ((n,p) 2.7 %, (n,d) 2.7 %) and cstrip a ((n,a) 2.2 %). B5 traced both "
            "to the engine's DEFAULT 14 MeV (n,p)/(n,a) excess, not to the keywords: cstrip a moves (n,a) by the same "
            "mb as stock (9.59 vs 9.63 mb, 0.4 %; the % differs because the engine's (n,a) is 11 % higher); gadjust "
            "acts only through pre-equilibrium (with `preequilibrium 20` neither side moves) and the flux it hands "
            "back to the compound nucleus decays into protons more in the engine (compound-only (n,p) 151.5 vs 131.5 "
            "mb). Fixing that changes defaults: a fidelity task, not a keyword batch")
#: KWCOV B2 rows (docs/hf/COVERAGE_PLAN.md B2 has the full table)
B2: dict = {
    "best": ("SUPPORTED", _F + "_deck_best (= INCOGNITA_TALYS_FIT=best, cards identical; Fe-56 engine bitwise)",
             "deck `best y` reads structure/best/<Nuc>/<p>-<Nuc>.talys before the deck (initial_best.f90). Lines the "
             "port cannot apply (adjustment tables, optmod/levelfile/deformfile files) are left out WITH A WARNING. "
             "Wiring exact; the RESPONSE has LOSSES from the physics knobs the files hold: Co-59 8.2 % ((n,g) isomer "
             "1 MeV), 7.3 % ((n,np) 14 MeV); Fe-56 without its awdadjust table 6.8 % ((n,np) 14 MeV), with it 11 % "
             "(nonelastic 5 MeV); U-238 8.1 % (fission 5 MeV: its n-U238.omp optmod file is not read, B6). "
             "Same family as the fit y loss (gadjust, cstrip/cknock)", _T),
    "bestend": ("SUPPORTED", _F + "_deck_best", "best lines after the deck's (initial_best.f90:113-124)", _T),
    "bestfile": ("SUPPORTED", _F + "_deck_best", "explicit best file path; missing file = TALYS's warning", _T),
    "bestbranch": ("SUPPORTED", "input/defaults.py _bestbranch -> structure/levels.py",
                   "levels/branch/<Nuc>.branch (branching.f90); Co-59 (n,2n) isomers vs stock 0.02 %", _T),
    "branch": ("SUPPORTED", "input/defaults.py _apply_forms (parsed, checked, dropped with a warning)",
               "TALYS-2.25 BUG: strucinitial.f90:325 resets nbranch after the input, so `branch` lines never act "
               "(stock Co-59: 0.0 % change). The port reproduces that and warns", _T),
    "fit": ("SUPPORTED", _F + "_cards (o.flagfit -> nn/ng/na/nf/nd .par)", "works as a deck line; LOSS: " + _FITLOSS, _T),
    "ngfit": ("SUPPORTED", _F + "_cards", "Fe-56 response 0.23 % (capture)", _T),
    "macsfit": ("SUPPORTED", _F + "_cards", "turns ngfit off (input_fit.f90); Fe-56 response 0.38 %", _T),
    "gamgamfit": ("SUPPORTED", _F + "_cards", "turns ngfit off; Fe-56 response 0.15 %", _T),
    **{k: ("SUPPORTED", _F + "_cards", "wired (xsfit.f90 order); its .par lines carry the gadjust / cstrip "
           "responses of the fit y loss: " + _FITLOSS, _T) for k in ("nnfit", "nafit", "ndfit")},
    "nffit": ("SUPPORTED", _F + "_cards", "wired (nf.par matched on fismodel); not response-tested (U-238 fit run "
              "not made)", _T),
    **{k: ("SUPPORTED", _F + "_cards (" + k[0] + "n.par)", "wired; xsfit.f90 does not match the projectile, so the "
           "library applies on any run; response untested (charged/photon projectiles behind INCOGNITA_CPINC)", _T)
       for k in ("pnfit", "gnfit", "dnfit", "anfit")},
    "ejectiles": ("READ_ONLY_DEFAULT", "input/defaults.py Options.parinclude + UNPORTED",
                  "a subset is REFUSED: parskip reaches only the channel bookkeeping, not the decay (Fe-56 `ejectiles "
                  "g n p` 14 MeV: stock (n,2n) +3.4 %, engine 0.0 %)", _T),
    "maxlevelsbin": ("SUPPORTED", "input/defaults.py Options.nlevbin -> nlev_of -> structure/levels.py",
                     "`maxlevelsbin p 5` Fe-56 response 0.19 %", _T),
    "maxlevelsres": ("SUPPORTED", "input/defaults.py Options.nlevmaxres -> nlev_of -> structure/levels.py",
                     "Fe-56 0.03 %, Co-59 0.02 %, U-238 0.01 %", _T),
    "nlevels": ("SUPPORTED", "input/defaults.py Options.pernuc -> nlev_of", "`nlevels 25 56 5` Fe-56 0.19 %", _T),
    "estop": ("SUPPORTED", "input/energies.py estop_subset -> engine.py / engine_c.py",
              "energies above estop not computed, grid (enincmax) kept as read_energies.f90; Fe-56 0.00 %", _T),
    "liso": ("SUPPORTED", "input/defaults.py Options.Lisoinp (output label only in TALYS too)",
             "no cross section moves in stock TALYS (Fe-56 0.0 %) nor in the engine", _T),
    "isomer": ("SUPPORTED", "input/defaults.py Options.isomer_s -> structure/levels.py",
               "Fe-56 `isomer 0.001` 0.0 % both sides", "test:test_chanobs.py,test_resiso.py,test_kwcov_b2.py"),
    "ldmodel": ("SUPPORTED", "input/defaults.py Options.ldmodel_of (global + `ldmodel v Z A`) -> density/*, gamma/*",
                "per-nucleus form since B2: Fe-56 `ldmodel 2 26 57` 0.99 %; U-238 `ldmodel 1 92 238` LOSS (n,2n) 14 MeV "
                "3.1 % (a 51 % move), capture 1.1 %. B5: the keyword is exact (with it, (n,2n) 14 MeV engine 1537.6 vs "
                "stock 1540.8 mb, 0.2 %); the loss is the DEFAULT run's own 14 MeV disagreement ((n,2n) -3.3 %, fission "
                "+4 %). Global `ldmodel 2` on Fe-56: 2.85 % ((n,a) 14 MeV, the same default (n,a) excess)",
                "test:test_defaults.py,test_density.py,test_kwcov_b2.py"),
    "colenhance": ("SUPPORTED", "input/defaults.py Options.flagcol_of (global + `colenhance y Z A`) -> density/*",
                   "per-nucleus form since B2: Fe-56 `colenhance y 26 57` 0.31 %", "test:test_defaults.py,test_kwcov_b2.py"),
    "energy": ("SUPPORTED", "input/energies.py read_energies, input/deck.py read_deck/run_deck",
               "single, `E1 E2 dE` range (dE 0 = 10 points), file, and pre-defined `n0-20.grid` grids, equal to "
               "TALYS's own `energies` files", _T),
}
_T5 = "test:test_kwcov_b5.py"
_R5 = "scripts/kwcov/b5_response.py"
#: KWCOV B5 rows (docs/hf/COVERAGE_PLAN.md B5 has the full table); response = |ln(R/S)| max, stock > 1 mb, 1/5/14 MeV
B5: dict = {
    "tjadjust": ("SUPPORTED", "input/fitlib.py _split (class 12 `tjadjust Z A <p> v`) -> Params.TJadjust",
                 "TALYS-2.25 BUG: a constant tjadjust never acts (comptarget.f90:331 / multiple.f90:429 scale by "
                 "`adjust`'s factor, which has no entry for it; TJadjust is read nowhere; stock Fe-56 `tjadjust 26 57 p "
                 "1.5`: 0.0 %). Read, warned, inert, as stock. The `Ea Eb Em D` / file forms (which act: stock (n,p) "
                 "+24 %) are REFUSED", _T5),
    "rgamma": ("SUPPORTED", "input/defaults.py Params.Rgamma -> preeq/exciton.py:318",
               "Fe-56 `rgamma 4` 0.82 % (stock capture 14 MeV +63 %)", _T5),
    "cknock": ("SUPPORTED", "input/defaults.py Params.Cknock -> preeq/complex.py:354 (knockout.f90:158)",
               "Fe-56 n `cknock a 2`, `cknock n 2`: stock and engine 0.0 % (no knockout cross section survives for an "
               "incident neutron)", _T5),
    "esurf": ("SUPPORTED", "input/defaults.py Params.Esurf0 -> preeq/exciton.py:231", "Fe-56 `esurf 20` 0.28 % "
              "(stock (n,d) -3.9 %)", _T5),
    "pshiftadjust": ("SUPPORTED", "input/defaults.py Params.Pshiftadjust -> density/parameters.py, density/ld_nx2.py",
                     "Fe-56 `pshiftadjust 26 57 0.5` 0.01 % (stock moved 0.4 %)", _T5),
    "pshiftconstant": ("SUPPORTED", "input/fitlib.py (global form, input_densitypar.f90:444) -> density/*",
                       "global form now read (was refused as unparsable); acts only where Pshift is not in the ld "
                       "parameter file: Fe-56 `ldmodel 2; pshiftconstant 1.5` 0.0 % on both sides. A per-nucleus card "
                       "beats the global form here, while TALYS's global form overwrites every cell", _T5),
    "spradjust": ("SUPPORTED", "input/fitlib.py GAMMA_FIELDS -> gamma/parameters.py:914",
                  "Fe-56 `spradjust 26 57 2.0 m1` 0.00 % (stock moved 4.6 %)", _T5),
    "popmev": ("SUPPORTED", "input/defaults.py Options.flagpopMeV (inert)", "acts only on a population input "
               "(excitation.f90, projectile 0), which the port does not run: inert in TALYS too", _T5),
    **{k: ("SUPPORTED", "input/defaults.py Params." + v + " (inert)", "acts only with `pseudoresonances y` "
           "(levels.f90:348), which is refused (structure/levels.py)", _T5)
       for k, v in (("emaxpseudores", "Emaxpseudores"), ("pseudoreswidth", "pseudoreswidth"),
                    ("pseudoresfade", "pseudoresfade"))},
    "ntop": ("SUPPORTED", "input/defaults.py Options.ntop_of (`ntop Z A n [ibar]`) -> density/parameters.py, ld_nx2.py",
             "Fe-56 `ntop 26 56 6` 0.77 % (stock moved 29 %), `ntop 26 57 8` 0.92 % (38 %)", _T5),
    "nlow": ("SUPPORTED", "input/defaults.py Options.nlow_of (`nlow Z A n [ibar]`) -> density/parameters.py, ld_nx2.py",
             "Fe-56 `nlow 26 56 3` 0.05 % (stock moved 1.5 %)", _T5),
    "skipcn": ("SUPPORTED", "input/defaults.py Options.skipcn_of -> emission/feeding.py, multiple.py (C cascade -> "
               "Python walk)", "multiple.f90:262: the nucleus keeps what it is fed, never decays. Fe-56 `skipcn 26 56` "
               "LOSS 9.4 % on (n,np) 14 MeV (stock moved 105 %; every other channel 0.0 %): what is left of (n,np) "
               "goes through Mn-56, i.e. the engine's default (n,p) excess at 14 MeV (+12 %)", _T5),
    "maxzrp": ("SUPPORTED", "input/defaults.py Options.maxZrp (inert)", "acts only with `rpevap y` (multiple.f90:270), "
               "which is refused", _T5),
    "maxnrp": ("SUPPORTED", "input/defaults.py Options.maxNrp (inert)", "acts only with `rpevap y` (multiple.f90:270), "
               "which is refused", _T5),
    "rpevap": ("READ_ONLY_DEFAULT", "input/defaults.py UNPORTED", "rpevap y REFUSED: residual-product evaporation "
               "(rpevap.f90) is not ported", _T5),
    "levelfile": ("SUPPORTED", "input/defaults.py Options.levelfile_of -> structure/levels.py, files.level_records",
                  "deck `levelfile Z <file>` (path keeps its case; relative to the deck's directory): Fe-56 with the "
                  "2+ level moved to 0.95 MeV 0.02 % (stock moved 38 %); a missing file stops the run, as TALYS. A "
                  "best file's own levelfile line (Mo-95/97) is still left out with a warning", _T5),
    "deformfile": ("SUPPORTED", "input/defaults.py Options.deformfile_of -> structure/deformation.py",
                   "Fe-56 beta2(2+) 0.239 -> 0.30: 0.06 % (stock moved 2.6 %). Best-file lines (Hf-174..180) still "
                   "left out with a warning", _T5),
    **{k: ("MISSING", "input/fitlib.py _SKIP (refused on a deck line)", "external " + w + " file not read: a deck "
           "line with it is REFUSED (was skipped silently)", _T5)
       for k, w in (("densfile", "level-density table"), ("e1file", "E1 strength"), ("m1file", "M1 strength"),
                    ("massdir", "mass-table directory"))},
    "sfth": ("SUPPORTED", "input/fitlib.py (class 15, value first) -> direct/capture.py spectroscopic_factors",
             "reaches the racap structure since B5 (it took the defaults); Au-197 / Fe-56 / Zr-90 racap.tot: 0.0 % on "
             "both sides (the continuum factor does not move xs(dir. cap.))", _T5),
    "sfexp": ("SUPPORTED", "input/fitlib.py (class 15, value first) -> direct/capture.py spectroscopic_factors",
              "Au-197 racap.tot `sfexp 0.5` and `sfexp 0.5 79 198 0`: 0.00 % (stock -1.6 % at 1 keV)", _T5),
    "ldmodelracap": ("READ_ONLY_DEFAULT", "direct/racapcalc.py mode", "3 only (the port's racap level density); 1/2 "
                     "REFUSED when direct capture is on, inert otherwise (as TALYS)", _T5),
    "racap": ("SUPPORTED", "direct/racapcalc.py mode (deck `racap y|n` wins over INCOGNITA_DIRECT_CAPTURE)",
              "a deck `racap y` was read and ignored; now it is TALYS-2.25's: exactly 0 mb without `optmodall y` "
              "(stock Au-197: capture 0.0 %; structure.f90:85 defect, warned), and `optmodall y` is refused, so the "
              "racapcalc model runs only through INCOGNITA_DIRECT_CAPTURE (the KD03 well stock builds under "
              "optmodall y)", "test:test_directcap.py,test_kwcov_b5.py"),
    "optmodall": ("READ_ONLY_DEFAULT", "input/defaults.py UNPORTED", "WAS SILENTLY IGNORED (no engine code reads "
                  "flagompall; the old SUPPORTED came from comments): stock Au-197 1 MeV `optmodall y` capture +93 %, "
                  "inelastic -38 %, engine 0.0 %. Now REFUSED; port in B6", _T5),
}


_T7 = "test:test_kwcov_b7.py"
#: KWCOV B7 rows (docs/hf/COVERAGE_PLAN.md B7); response = |ln(R/S)| max, stock > 1 mb, Fe-56 and Zr-90, 1/5/14 MeV
B7: dict = {
    "twocomponent": ("SUPPORTED", "input/defaults.py Options.flag2comp -> preeq/exciton_b7.py one_component",
                     "`twocomponent n`: one-component exciton model (exciton.f90, emissionrate.f90, lambdaplus.f90, "
                     "lifetime.f90, Qfactor). Binary PE totals = stock to 1e-4; response Fe-56 0.49 %, Zr-90 0.39 % "
                     "(stock moved 17 %). REFUSED with multiple pre-equilibrium (Einc >= multipreeq onset, 20 MeV): "
                     "multipreeq.f90 not ported", _T7),
    "gshell": ("SUPPORTED", "input/defaults.py Options.flaggshell -> preeq/exciton_b7.py (_Damp: ignatyuk/alev)",
               "shell-damped g in the exciton emission and transition rates, TALYS's quirks kept (first-channel damping, "
               "lambdanupi's g(uu)). PE totals = stock to 1e-4; response Fe-56 0.39 %, Zr-90 0.50 %. REFUSED with "
               "multiple pre-equilibrium (the damping is not wired into multipreeq2); racap y path needs optmodall "
               "(refused)", _T7),
    "preeqmode": ("SUPPORTED", "input/defaults.py Options.preeqmode -> preeq/exciton.py (1, 2), preeq/exciton_b7.py (3)",
                  "1 analytic, 2 numerical (default), 3 optical-model rates (bonetti.f90 wvol: transition rates = stock "
                  "to 1e-6, PE totals to 1e-4; response 4.8 % Fe-56 (n,d) and 6.0 % Zr-90 (n,p) relative but the SAME "
                  "millibarns (-1.01 vs -1.04, -12.60 vs -12.86 mb): the engine's default 14 MeV (n,p)/(n,d) excess). "
                  "4 (MSD/MSC) REFUSED: msd.f90 + continuum DWBA not ported (stock Fe-56 (n,p) +32 %)", _T7),
    "preeqspin": ("SUPPORTED", "input/defaults.py Options.pespinmodel -> preeq/exciton.py spin_fraction, "
                  "emission/feed_reference._spin_inputs, emission/binary.py",
                  "1/2 as before; 3 (= y) J-dependent PE population (xspreeqJP -> population.f90 preeqpop -> binary): "
                  "response Fe-56 0.44 %, Zr-90 0.88 %; 4 Wigner (newspin.f90) Fe-56 0.35 %. Before B7, 4 dropped the "
                  "PE flux silently (binary added nothing for pespinmodel > 2). preeqspin 4 with multiple PE refused",
                  _T7),
    "onestep": ("SUPPORTED", "input/defaults.py Options.flagonestep (inert)", "acts only inside MSD (preeqmode 4, "
                "refused); inert otherwise, as in TALYS", _T7),
    "msdbins": ("SUPPORTED", "input/defaults.py Options.msdbins (inert)", "acts only inside MSD (preeqmode 4, refused); "
                "inert otherwise, as in TALYS", _T7),
    "emsdmin": ("SUPPORTED", "input/defaults.py Params.Emsdmin (inert)", "acts only inside MSD (preeqmode 4, refused); "
                "inert otherwise, as in TALYS", _T7),
    "gnorm": ("READ_ONLY_DEFAULT", "input/defaults.py Options.flaggnorm (refused when y)",
              "REFUSED: TALYS-2.25 normalises to the resonance table's keV number read as eV (resonancepar.f90:96), so "
              "radwidtheory's iteration drives the compound nucleus's E1 ftable to 0 (stock Fe-57 1.30 eV vs 9.2e-4; "
              "capture 1 MeV -70 %, 14 MeV -99 %; Zr-91 capture 1 MeV -54 %). Left: call "
              "gamma.transmission.radwidtheory(flaggnorm) with TALYS's gamgam before the run and feed the final "
              "ftable(E1) of the compound nucleus to every strength user", _T7),
}
_T8 = "test:test_kwcov_b8.py"
_FO = "fisobs.py (output only; Results.extras / Results.spectra) "
#: KWCOV B8 rows (docs/hf/COVERAGE_PLAN.md B8); stock TALYS-2.25 n + U-238 / U-235 / Pu-239 / Th-232 at 1/5/14 MeV,
#: scripts/kwcov/b8_response.py; response = |ln(R/S)| max, stock > 1 mb, over b2's channels + rpZZZAAA.fis
B8: dict = {
    "filefission": ("SUPPORTED", _FO + "rpZZZAAA.fis", "turns FISOBS on: fission per fissioning nuclide (fissionout.f90), "
                    "the Iwamoto PFNS and the Wahl nubar; vs stock within the engine's own (n,f) difference. y with "
                    "endf y; TALYS's `channels y` default for it is not modelled", _T8),
    "outfission": ("SUPPORTED", _FO + "(as filefission)", "turns FISOBS on; the talys.out barrier / transmission "
                   "tables stay PARTIAL (ingredients.py)", _T8),
    "fisfeed": ("SUPPORTED", _FO + "fisZZZAAA.feed", "fission per excitation bin (multiple.f90:884): Ex and Population "
                "columns, same rows as stock, sums = rpZZZAAA.fis; the J-parity columns (fisfeedJP) are NOT given "
                "(the decay kernels sum the fission feed over J and parity)", _T8),
    "pfnsmodel": ("SUPPORTED", _FO + "iwamoto",
                  "1: Iwamoto PFNS (iwamoto.f90, single precision as TALYS): grid, E-average and every column = stock "
                  "to 2e-5 (U-238, U-235, Pu-239, Th-232). 2: no Iwamoto spectrum, as stock without massdis; the "
                  "fragment-decay PFNS (ffevap.f90) is B14", _T8),
    "tmadjust": ("SUPPORTED", _FO + "iwamoto (Tm0 x tmadjust)", "PFNS E-average = stock 1e-5 (U-238 1.3; U-235, "
                 "Pu-239 0.8 with fsadjust 2); no cross section moves on either side", _T8),
    "fsadjust": ("SUPPORTED", _FO + "iwamoto (scission fraction x fsadjust)", "PFNS E-average = stock 1e-5 (U-238 3; "
                 "U-235, Pu-239 2); no cross section moves on either side", _T8),
    "cnubar1": ("SUPPORTED", _FO + "nubar_wahl -> extras['nubarn.tot:wahl']", "TALYS-2.25 computes nubarWahl "
                "(totalxs.f90:124) and never writes it (massdis.f90:252 resets nubar before nubarout); the port's "
                "extras give it; transcription checked by hand", _T8),
    "cnubar2": ("SUPPORTED", _FO + "nubar_wahl -> extras['nubarn.tot:wahl']", "slope term of the Wahl nubar; as cnubar1",
                _T8),
    "rfiseps": ("SUPPORTED", "input/defaults.py Options.Rfiseps (inert)", "acts only in massdis.f90 / ffevap.f90 "
                "(fission yields, B14); stock U-238 `rfiseps 0.01`: nothing moves. Range 0..1 checked", _T8),
    "axtype": ("SUPPORTED", "input/defaults.py Options.axtype_of (`axtype Z A type [ibar]`) -> density/parameters.py",
               "barrier axiality per nucleus and barrier. U-238 response: 92 239 2 1 0.42 %, 92 238 3 1 1.24 %; "
               "92 239 3 2 4.7 % relative for a x2.5 move, the same millibarns (+886 vs +867 mb fission 5 MeV, 2.2 %); "
               "Th-232 90 233 3 2: 12 % relative, +1081 vs +1032 mb (4.8 %): the engine's default Th-232 fission is "
               "+20 % at 5 MeV (a default-fidelity item)", _T8),
    "hbtransfile": ("SUPPORTED", "input/defaults.py Options.fisstates_file_of -> fission/parameters.py "
                    "read_headband_states", "`hbtransfile Z A <file>` (read with hbstate y, as TALYS): U-238 response "
                    "from `hbstate y` 1.93 % (fission 1 MeV -36.3 vs -39.3 mb); `hbstate y` itself 0.73 %. A missing "
                    "file stops the run, as TALYS", _T8),
    "class2file": ("SUPPORTED", "input/defaults.py Options.fisstates_file_of -> fission/parameters.py "
                   "read_class2_states", "`class2file Z A <file>` (read with class2 y): U-238 response from `class2 y` "
                   "0.67 %. `class2 y` itself: 6.2 % relative (U-238 rp092238.fis 5 MeV x4), +291 vs +297 mb (2.2 %)",
                   _T8),
}
_T9 = "test:test_kwcov_b9.py"
_AR = "astro/rates.py + astro/thermal.py (input/deck.py run_deck -> Results.astro) "
#: KWCOV B9 rows (docs/hf/COVERAGE_PLAN.md B9); stock TALYS-2.25 n + Au-197 / Fe-56 / Ge-74, scripts/kwcov/b9_response.py
B9: dict = {
    "astro": ("SUPPORTED", _AR + "egridastro grid, partfunc, stellarrate, astroout files",
              "astro y: TALYS's incident grid (= stock, 110 energies for Au-197), the T9 grid, rates/MACS/G(T) and the "
              "files astrorate.g/p/a(/f), astrorate.tot, astrorateZZZAAA.tot; with astrogs n (TALYS's default) the "
              "thermalised target inside the run (astrotarget lumped WFC + compprepare astro feed + ewfc = Einc "
              "switch-off). Fe-56: (n,g) rate 1.27 %, stellar enhancement response 1.25 %; see the plan for Au-197 "
              "(engine default (n,n')/(n,g) above 0.1 MeV) and Ge-74. Runs on the C driver (run_deck); "
              "engine.run refuses astrogs n; fissile targets with astrogs n and astro + racap refused", _T9),
    "astrogs": ("SUPPORTED", _AR + "(G = 1, no thermal add-on)", "Fe-56 rates = stock to 0.06 % ((n,g)), 0.04 % "
                "((n,n)); Au-197 (n,g) MACS = stock to 1e-5 at T9 <= 0.1 (the capture agrees there)", _T9),
    "astroex": ("SUPPORTED", _AR + "(isomer populations from CHANOBS xsNNNNNN.LMM)",
                "astrorate.<g|p|a>.LNN and astrorateZZZAAA.LNN (rate, MACS, branching); turns CHANOBS on for the run",
                _T9),
    "astroe": ("SUPPORTED", "input/defaults.py Options.astroE (kind astroe) + " + _AR,
               "one temperature T9 = astroE/kT, sets astro y and astrogs y, grid to 50 kT, macs.g for 0.029-0.031 "
               "(with structure/gamma/macs Exp column): Au-197 30 keV MACS 929.9 vs stock 934.4 mb (0.48 %)", _T9),
    "astrot": ("SUPPORTED", "input/defaults.py Options.astroT9 (kind astrot) + " + _AR,
               "one temperature, sets astro y (astrogs stays n); range 1e-4..10 and astroE/astroT exclusion checked",
               _T9),
    "nonthermlev": ("SUPPORTED", "astro/rates.py partition_function", "the level left out of the partition function "
                    "(partfunc.f90:101; TALYS-2.25 uses it nowhere else)", _T9),
}
_T10 = "test:test_kwcov_b10.py"
_UR = "urr.py (engine_c/engine cases -> urr.record per Einc <= eurr -> Results.urr) "
#: KWCOV B10 rows (docs/hf/COVERAGE_PLAN.md B10); stock TALYS-2.25 n + Fe-56 / U-238 / Co-59 / Au-197 at 0.01-5 MeV,
#: scripts/kwcov/b10_response.py
B10: dict = {
    "urr": ("SUPPORTED", "input/defaults.py Options.flagurr/eurr_mev -> " + _UR,
            "urr y / urr <E> / urr n: urr.dat, urr<gam|com|fis|neu|pro|alp>width.lLL, urrspacingl(j), urrneustrengthl(j), "
            "urrtalys.tot (comptarget's (l,J) blocks incl. the last-Wab quirk, dtheory D(l,J), strengthfunc, thermalxs). "
            "Every number vs stock: Fe-56 5e-5, Co-59 1e-4, U-238 0.11 % in TALYS mode (Gg 1 MeV = the engine's capture; "
            "default mode Gf 22 % = EXACTFIS), Au-197 2e-4 in TALYS mode (default Gx x2 / capture -30 % = CCEXITNB2). "
            "Output only: Fe-56 552 / U-238 600 Results arrays bitwise with and without urr y. Refused: widthmode 2/3, "
            "INCOGNITA_EWFC coupled targets, KEVCOLD cells", _T10),
    "lurr": ("SUPPORTED", "input/defaults.py Options.lurr -> " + _UR,
             "l range of the URR blocks and files (0-60 checked); response vs stock lurr 0/1/3: Fe-56 1e-5, U-238 8e-5 "
             "(l03 files = stock to 3e-5)", _T10),
    "urrnjoy": ("SUPPORTED", "input/defaults.py Options.flagurrnjoy -> urr.py (csunr2, unfac, gnrl)",
                "NJOY-formalism cross sections and the Gx/Gf renormalisation loop: urrnjoy.tot, urrratio.tot; response "
                "Fe-56 7e-5, U-238 2.8e-4 (Gx)", _T10),
    "rprime": ("SUPPORTED", "input/defaults.py Params.RprimeU -> urr.py (NJOY potential scattering radius)",
               "acts only with urrnjoy y, as TALYS (default: R' of the first URR energy); range 0-10 checked; response "
               "rprime 7: Fe-56 6e-7, U-238 6e-6", _T10),
    "xscaptherm": ("IGNORED", "urr.py thermal_capture_mb (thermalxs.f90 port, urr.dat column only)",
                   "only urr.dat's `thermal capture cross section` reads it (B10; table/Kopecky = stock for Fe-56 "
                   "2590, U-238 2670 mb); thermal.f90's normalisation of the low-energy capture is B10b"),
}
MANUAL: dict = {
    # --- the four main keywords: the run's arguments, not deck lines ---
    "projectile": ("SUPPORTED", "projectile.py (INCOGNITA_CPINC: n default; p d t h a g)",
                   "n is production; p/d/t/h/a/g ported behind INCOGNITA_CPINC (g runs engine.run only)", "test:test_charged_fidelity.py"),
    "element": ("SUPPORTED", "engine run(Z, A) arguments", "target is a run argument (TALYSworld: target)", "manual"),
    "mass": ("SUPPORTED", "engine run(Z, A) arguments", "mass 0 (natural element) is MISSING: no abundance loop "
             "(natural.f90)", "manual"),
    "energy": ("SUPPORTED", "ChainedFull(declared_energies=...)", "single energy, list or grid file; TALYS "
               "`energy E1 E2 dE` range form must be expanded by the caller", "manual"),
    "ltarget": ("READ_ONLY_DEFAULT", "structure/levels.py:171",
                "KNOWN GAP: excited/isomeric targets refused (NotImplementedError); only astro/stellar.py uses "
                "excited entrance states internally", "manual"),
    "abundance": ("MISSING", "", "natural targets (mass 0 / abundance file): natural.f90 loop over isotopes"),
    # --- per-nucleus gamma cards that fitlib reads under its own table ---
    **{k: ("SUPPORTED", _F + "UPBEND_KEYS -> gamma/parameters.py:762", "upbend C/e/f cards (LEESHELL fix)", "grep")
       for k in ("upbendc", "upbende", "upbendf", "upbendcadjust", "upbendeadjust", "upbendfadjust")},
    # --- switches that only exist as INCOGNITA_* env levers today ---
    # --- KWCOV B2 (2026-11-08): deck wiring; response vs stock = scripts/kwcov/b2_response.py, |ln(R/S)| max ---
    **B2,
    **B5,
    **B7,
    **B8,
    **B9,
    **B10,
    "transeps": ("SUPPORTED", "input/defaults.py Options.transeps -> emission/feeding.py Cascade.transeps",
                 "KWCOV B9 fix: the deck value (and astro y's / massdis y's) did not reach the chain, which kept the "
                 "Cascade constructor's 1e-8; now it does unless a caller passes its own", _T9),
    "channels": ("SUPPORTED", "structure/scalars.py:144", "exclusive channels are always computed (flagchannels "
                 "hard-wired on); `channels n` has no effect, which is harmless", "manual"),
    "endf": ("IGNORED", "input/defaults.py", "defaults cascade honoured (eninclow 0, urr y -> the B10 URR files, "
             "channels y, adddiscrete 30 MeV); ENDF-6 output files (endf.cs, MF6 data) not written"),
    "micro": ("IGNORED", "input/defaults.py", "cascade honoured (ldmodel 7, jlmomp y -> refused, autorot y)"),
    "massdis": ("IGNORED", "input/defaults.py", "cascade honoured (transeps, popeps, pfnsmodel 2); fission yields "
                "not computed (MISSING observable)"),
    "riplomp": ("MISSING", "", "per-particle RIPL OMP index; the actinide RIPL 2408 default is applied automatically "
                "(defaults.py omppar stage) but the keyword is not read"),
    "preequilibrium": ("SUPPORTED", "input/defaults.py Options.epreeq_mev -> preeq/*", "onset energy honoured "
                       "(automatic grep missed: variable is consumed under its resolved name)", "manual"),
    # --- KWCOV B3: angular distributions (physics/hf/angout.py) ---
    "outangle": ("SUPPORTED", "input/defaults.py Options.flagang -> angout.py", "angleout + compound angular "
                 "distributions (flagcompang); INCOGNITA_ANGOUT=1 is the port switch", "test:test_angout.py"),
    "fileelastic": ("SUPPORTED", "input/defaults.py Options.fileelastic -> angout.py", "elastic angle file without "
                    "outangle (isotropic compound, as TALYS)", "test:test_angout.py"),
    "fileangle": ("SUPPORTED", "input/defaults.py Options.fileangle -> angout.py", "one level per line (TALYS); "
                  "`fileangle 1,2` also accepted; repeated deck lines need B2's plumbing to merge", "test:test_angout.py"),
    "outlegendre": ("SUPPORTED", "input/defaults.py Options.flaglegendre -> angout.py", "leg files (Total, Direct, "
                    "Compound, Normalized, ENDF-6)", "test:test_angout.py"),
    "blockangle": ("SUPPORTED", "input/defaults.py Options.flagblockangle -> angout.write_files", "nnang.L01 names, "
                   "energies appended", "test:test_angout.py"),
    "angles": ("SUPPORTED", "input/defaults.py Options.nangle -> angout.angles", "discrete angle grid "
               "180/nangle", "test:test_angout.py"),
    "cpang": ("SUPPORTED", "input/defaults.py Options.flagcpang -> angout.flagcompang", "compound angular "
              "distributions for charged projectiles", "test:test_angout.py"),
    # --- KWCOV B4: spectra, DDX, gamma lines (physics/hf/specobs.py) ---
    "outspectra": ("SUPPORTED", "input/defaults.py Options.flagspec -> specobs.py", "spectraout: <x>spec.tot columns, "
                   "Eaverage; INCOGNITA_SPECOBS=1 is the port switch", "test:test_specobs.py"),
    "ddxmode": ("SUPPORTED", "input/defaults.py Options.ddxmode -> specobs.py", "full DDX arrays + fileddxa/fileddxe; "
                "giant-resonance part isotropic", "test:test_specobs.py"),
    "fileddxa": ("SUPPORTED", "input/defaults.py Options.fileddxa -> specobs.py", "`fileddxa n 30`; deck line form "
                 "`fileddxa n,30,90,p,150` until B2 merges repeated lines", "test:test_specobs.py"),
    "fileddxe": ("SUPPORTED", "input/defaults.py Options.fileddxe -> specobs.py", "`fileddxe n 3.0` (same deck-line "
                 "note as fileddxa)", "test:test_specobs.py"),
    "filespectrum": ("SUPPORTED", "input/defaults.py Options.filespectrum -> specobs.write_files", "which ejectiles get "
                     "a file (Results carries all)", "test:test_specobs.py"),
    "outgamdis": ("SUPPORTED", "input/defaults.py Options.flaggamdis -> specobs.py", "gamZZZAAALiiLjj.tot (conversion "
                  "corrected with electronconv y)", "test:test_specobs.py"),
    "filegamdis": ("SUPPORTED", "input/defaults.py Options.filegamdis", "files follow INCOGNITA_SPECOBS_DIR",
                   "test:test_specobs.py"),
    "blockspectra": ("SUPPORTED", "input/defaults.py Options.flagblockspectra -> specobs.write_files", "nspec.tot names",
                     "test:test_specobs.py"),
    "blockddx": ("SUPPORTED", "input/defaults.py Options.flagblockddx -> specobs.write_files", "nddx.deg / nddx.MeV names",
                 "test:test_specobs.py"),
    "adddiscrete": ("SUPPORTED", "input/defaults.py Options.eadd_mev -> specobs.energy_spectra", "discrete peaks + fine "
                    "grid in the spectra (spectra.f90 flagadd)", "test:test_specobs.py"),
    "addelastic": ("SUPPORTED", "input/defaults.py Options.eaddel_mev -> specobs.energy_spectra", "elastic peak in the "
                   "spectra (flagaddel)", "test:test_specobs.py"),
    "channelenergy": ("SUPPORTED", "input/defaults.py Options.flagEchannel -> specobs.energy_spectra", "espec conversion "
                      "of spectra.f90:152-158 (not checked against stock)", "code"),
    "anglescont": ("SUPPORTED", "input/defaults.py Options.nanglecont -> specobs.anglecont", "continuum DDX angle grid",
                   "test:test_specobs.py"),
}

# --- KWCOV B6 (2026-11-08): optical model and direct reactions (physics/hf/omp/ompdeck.py); response vs stock =
# scripts/kwcov/b6_response.py, n + Fe-56 / U-238 at 1, 5, 14 MeV, |ln(R/S)| max over channels with stock > 1 mb ---
_T6 = "test:test_kwcov_b6.py"
_OD = "omp/ompdeck.py "
B6: dict = {
    "optmod": ("SUPPORTED", _OD + "tables -> omp/parameters.omp_parameters (tables=, before the RIPL default)",
               "`optmod Z A file [p]` (omppar.f90:243-277, header Ef honoured). U-238 best n-U238.omp: 0.09 %; Fe-56 "
               "table (Wd x1.15): 0.15 %. Files: cwd, then the best file's dir and its misc/tables", _T6),
    "optmodfilen": ("SUPPORTED", _OD + "local_file -> omp/parameters.omppar/read_local_omp",
                    "element OMP file instead of optical/neutron (omppar.f90:52-63); Fe-56 (v1 +2, d1 x1.1): 0.17 %", _T6),
    "optmodfilep": ("SUPPORTED", _OD + "local_file -> omp/parameters.omppar/read_local_omp",
                    "element OMP file instead of optical/proton; Fe-56 with a Mn file (outgoing protons): 0.86 % "
                    "((n,np) 14 MeV)", _T6),
    **{k: ("SUPPORTED", _OD + "range_cells -> Params ompadjustE1/E2/D/s -> omp/parameters.adjustF",
           "`<key> p E1 E2 D s` (s required, as TALYS); Fe-56 awdadjustF n 0.10 %, rvadjustF n 0.04 %, rvadjustF p "
           "0.12 %; U-238 awdadjustF n 0.14 %", _T6)
       for k in ("rvadjustf", "avadjustf", "rwadjustf", "awadjustf", "rvdadjustf", "avdadjustf", "rwdadjustf",
                 "awdadjustf", "rvsoadjustf", "avsoadjustf", "rwsoadjustf", "awsoadjustf")},
    "incadjust": ("SUPPORTED", "input/defaults.py default_params/_incadjust + " + _OD + "drop_bumps",
                  "`incadjust n`: the projectile's ompadjust factors act on no channel (ompadjust.f90:92 + flagompejec); "
                  "Fe-56 `incadjust n; v1adjust n 1.02; d1adjust p 1.1`: 0.09 %", _T6),
    "riplomp": ("SUPPORTED", "input/defaults.py Options.riplomp (kind riplomp) -> omp/parameters.omp_parameters",
                "`riplomp n` (no RIPL potential) / `riplomp <p> <iref>`; U-238 `riplomp n` (KD03 instead of RIPL 2408, "
                "stock moves 48 %): 0.38 %", _T6),
    "vinfadjust": ("SUPPORTED", "input/defaults.py Params.Vinfadjust -> omp/parameters.opticalnp, omp_nx2._opticalnp",
                   "acts above Ejoin (200 MeV) only, as in TALYS; Fe-56 at 1-14 MeV moves neither side (0.00 %); the "
                   "high-energy value itself not compared with stock", _T6),
    "coulomb": ("SUPPORTED", "none needed", "`coulomb n` = the port's ECIS (no Coulomb excitation, lo(11)); acts in "
                "TALYS only for charged projectiles on deformed targets, where the DEFAULT `coulomb y` is not "
                "reproduced (known gap, charged projectiles behind INCOGNITA_CPINC); Fe-56: 0.00 %", _T6),
    "eciscompound": ("NA", "", "ECIS compound-nucleus run for reference only (comptarget.f90:814-820: not used by "
                     "TALYS); no cross section moves in stock (Fe-56 0.00 %)", _T6),
    "statepot": ("READ_ONLY_DEFAULT", "input/defaults.py UNPORTED",
                 "`statepot y` REFUSED: a potential per excited state (incidentecis.f90:252); the port's ECIS uses the "
                 "incident-energy potential for every state", _T6),
    "rotational": ("READ_ONLY_DEFAULT", "input/defaults.py Options.flagrot + UNPORTED",
                   "`rotational <particles>` REFUSED: coupled-channels inverse transmission coefficients on deformed "
                   "residuals (inverseecis.f90:301) are not ported", _T6),
    "sysreaction": ("READ_ONLY_DEFAULT", "input/defaults.py Options.flagsys + UNPORTED",
                    "`sysreaction <particles>` REFUSED: Tripathi normalisation (tripathi.f90) not ported", _T6),
    "ecisstep": ("READ_ONLY_DEFAULT", "input/defaults.py UNPORTED", "non-zero REFUSED: the port's radial solvers take "
                 "ECIS's own step (hint 0)", _T6),
    "ompenergyfile": ("SUPPORTED", "input/defaults.py Options.ompenergyfile + reject_unported",
                      "read by endfenergies.f90 under `endf y` only: accepted without effect otherwise (as TALYS), "
                      "REFUSED with endf y (ENDF-6 incident grid not ported)", _T6),
    "best": ("SUPPORTED", _F + "_deck_best (= INCOGNITA_TALYS_FIT=best, cards identical; Fe-56 engine bitwise)",
             "deck `best y` reads structure/best/<Nuc>/<p>-<Nuc>.talys before the deck (initial_best.f90). Since B6 its "
             "OMP files act (Fe-56 awdadjust table, U-238 n-U238.omp optmod). RESPONSE LOSSES remain and are outside "
             "B6: Fe-56 6.7 % ((n,np) 14 MeV; 6.8 % for the same deck without its B6 line), U-238 9.2 % (fission 5 MeV; "
             "9.2 % without optmod), Co-59 8.2 % (B2): the 14 MeV (n,p)/(n,a) and U-238 LD/fission default-fidelity "
             "task of B5", _T6),
    "optmodall": ("SUPPORTED", "compound/ompall.py -> emission/feeding.Cascade.trans_of/front_trans, compound/chain.py",
                  "a set per compound nucleus (multiple.f90:323) + TALYS-2.25's stale-eend primary set at the 2nd and "
                  "later energies (talysreaction.f90:102 before `energies`); Python cascade. RESPONSE: U-238 1.1 %, Fe-56 6.9 % ((n,a) 14 MeV, a 65 % move), Au-197 LOSS 51 % (capture 1 MeV; the engine default Au-197 1 MeV composition differs, see COVERAGE_PLAN B6)", _T6),
    "racap": ("SUPPORTED", "direct/racapcalc.py mode (deck `racap y|n` wins over INCOGNITA_DIRECT_CAPTURE)",
              "0 mb without `optmodall y` as TALYS-2.25 (warned); with `optmodall y` (B6) the racapcalc model runs from "
              "a deck: Au-197 `racap y; optmodall y` direct capture = stock (133.6 mb at 1 MeV); the L00 isomer extra lacks it", "test:test_directcap.py,test_kwcov_b5.py"),
}
MANUAL.update(B6)
