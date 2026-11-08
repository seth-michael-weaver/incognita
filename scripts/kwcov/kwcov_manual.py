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
    "best": ("IGNORED", _F + "(INCOGNITA_TALYS_FIT=best)", "deck line ignored; the best-file recipe runs via "
             "INCOGNITA_TALYS_FIT=best|tendl"),
    "fit": ("IGNORED", _F + "(INCOGNITA_TALYS_FIT=fit)", "deck line ignored; fitted libraries via INCOGNITA_TALYS_FIT"),
    **{k: ("IGNORED", _F + "(INCOGNITA_TALYS_FIT=ng|macs|gamgam)", "deck flag ignored; ng/macs/gamgam .par entries "
           "applied via INCOGNITA_TALYS_FIT; nn/nf/na/nd/pn/gn/dn/an only when a best file asks")
       for k in ("ngfit", "nnfit", "nffit", "nafit", "ndfit", "pnfit", "gnfit", "dnfit", "anfit", "macsfit", "gamgamfit")},
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
    "colenhance": ("SUPPORTED", "input/defaults.py Options.flagcol() -> density/*", "read through the Options.flagcol "
                   "property (automatic grep missed it); global form only", "test:test_defaults.py"),
    "maxlevelsbin": ("MISSING", "", "per-ejectile nlevbin; only maxlevelstar is read"),
    "ejectiles": ("MISSING", "", "all 7 ejectiles always on; `ejectiles g n` (parskip) not read"),
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
