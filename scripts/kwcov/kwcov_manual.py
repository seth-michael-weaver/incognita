"""KWCOV hand-checked keyword rows: they override inventory.py's automatic class.

keyword -> (status, where, notes[, evidence]). Checked 2026-11-08 against origin/main 05fa5f70 by reading the code
named in `where`; "env" means the feature exists behind an INCOGNITA_* switch rather than the TALYS keyword.
"""
NA_PREFIXES = ("out", "file", "block")
NA_WORDS = frozenset({
    "user", "source", "format", "nulldev", "strucpath", "bestpath", "partable", "sacs", "ecissave", "eciscalc",
    "inccalc", "endfecis", "ecisdwba", "legacy", "reaction", "rescuefile", "components", "ddxmode", "integral",
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
    "astro": ("IGNORED", "astro/stellar.py (INCOGNITA_STELLAR)",
              "keyword ignored; thermalised-target stellar rate/SEF exists behind INCOGNITA_STELLAR on the C path. "
              "astro y also resets numerics (transpower 15, xseps 1e-17): that cascade IS honoured in default_options"),
    # --- KWCOV B2 (2026-11-08): deck wiring; response vs stock = scripts/kwcov/b2_response.py, |ln(R/S)| max ---
    **B2,
    **B5,
    "channels": ("SUPPORTED", "structure/scalars.py:144", "exclusive channels are always computed (flagchannels "
                 "hard-wired on); `channels n` has no effect, which is harmless", "manual"),
    "endf": ("IGNORED", "input/defaults.py", "defaults cascade honoured (eninclow 0, urr y, channels y, adddiscrete "
             "30 MeV); ENDF-6 output files (endf.cs, MF6 data) not written"),
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
}
