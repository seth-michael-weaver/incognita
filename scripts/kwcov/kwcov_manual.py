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
}
