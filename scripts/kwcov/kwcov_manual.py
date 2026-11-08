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
            "gadjust on the compound nucleus ((n,p) 2.7 %, (n,d) 2.7 %) and cstrip a ((n,a) 2.2 %); B5/B7")
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
                "3.1 % (a 51 % move), capture 1.1 %", "test:test_defaults.py,test_density.py,test_kwcov_b2.py"),
    "colenhance": ("SUPPORTED", "input/defaults.py Options.flagcol_of (global + `colenhance y Z A`) -> density/*",
                   "per-nucleus form since B2: Fe-56 `colenhance y 26 57` 0.31 %", "test:test_defaults.py,test_kwcov_b2.py"),
    "energy": ("SUPPORTED", "input/energies.py read_energies, input/deck.py read_deck/run_deck",
               "single, `E1 E2 dE` range (dE 0 = 10 points), file, and pre-defined `n0-20.grid` grids, equal to "
               "TALYS's own `energies` files", _T),
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
    "channels": ("SUPPORTED", "structure/scalars.py:144", "exclusive channels are always computed (flagchannels "
                 "hard-wired on); `channels n` has no effect, which is harmless", "manual"),
    "racap": ("SUPPORTED", "direct/capture.py, direct/racapcalc.py (INCOGNITA_DIRECT_CAPTURE)",
              "direct capture added to (n,g) when INCOGNITA_DIRECT_CAPTURE is set; verify keyword-alone path", "test:test_directcap.py"),
    "endf": ("IGNORED", "input/defaults.py", "defaults cascade honoured (eninclow 0, urr y, channels y, adddiscrete "
             "30 MeV); ENDF-6 output files (endf.cs, MF6 data) not written"),
    "micro": ("IGNORED", "input/defaults.py", "cascade honoured (ldmodel 7, jlmomp y -> refused, autorot y)"),
    "massdis": ("IGNORED", "input/defaults.py", "cascade honoured (transeps, popeps, pfnsmodel 2); fission yields "
                "not computed (MISSING observable)"),
    "riplomp": ("MISSING", "", "per-particle RIPL OMP index; the actinide RIPL 2408 default is applied automatically "
                "(defaults.py omppar stage) but the keyword is not read"),
    "preequilibrium": ("SUPPORTED", "input/defaults.py Options.epreeq_mev -> preeq/*", "onset energy honoured "
                       "(automatic grep missed: variable is consumed under its resolved name)", "manual"),
}
