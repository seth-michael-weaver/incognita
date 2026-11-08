#!/usr/bin/env python3
"""KWCOV: TALYS-2.25 output observables -> docs/hf/observable_coverage.csv (hand-curated, regenerable).

Status for observables (OBSERVABLE_COVERAGE.md explains them):
  SUPPORTED  in `Results` on the production (C) path with default inputs, compared with stock TALYS by a gate/test
  PARTIAL    produced only behind an INCOGNITA_* switch, on one driver, or for a subset (named in notes)
  INTERNAL   the engine computes it, but `Results` does not carry it out
  MISSING    not computed
  NA         TALYS diagnostics/plumbing with no meaning for us
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COLS = ("observable", "talys_files", "talys_writer", "gating_keywords", "status", "where", "batch", "notes")

ROWS = [
    # --- integral cross sections ---
    ("total cross section", "total.tot", "totalout.f90:1", "outexcitation", "SUPPORTED", "Results.totals_mb['total']", "",
     "identity sigma_el + sigma_nonel (binary.f90); TALYSworld channel"),
    ("elastic cross section (shape + compound)", "elastic.tot", "totalout.f90:1", "", "SUPPORTED",
     "Results.totals_mb['elastic'], ['compound_elastic']", "", "TALYSworld channel"),
    ("nonelastic cross section", "nonelastic.tot", "totalout.f90:1", "", "SUPPORTED", "Results.totals_mb['nonelastic']", "", ""),
    ("reaction cross section (OMP)", "reaction.tot", "totalout.f90:1", "", "SUPPORTED", "Results.totals_mb['reaction']", "", ""),
    ("binary non-elastic per ejectile", "binary.tot", "finalout.f90:351", "", "PARTIAL",
     "Results.extras['binary.tot:<p>'] (INCOGNITA_CHANOBS)", "B1", "verified vs stock (Fe-56, Co-59, U-238)"),
    ("exclusive channel cross sections", "xsNNNNNN.tot (col 2)", "channelsout.f90:1", "channels, filechannels, maxchannel",
     "SUPPORTED", "Results.channels_mb['xsNNNNNN']", "", "(n,g) (n,p) (n,a) (n,2n) (n,n') are TALYSworld channels"),
    ("exclusive channel gamma production", "xsNNNNNN.tot (col 3)", "channelsout.f90:315", "channels", "PARTIAL",
     "Results.extras['xsNNNNNN.tot:gamma'] (INCOGNITA_CHANOBS)", "B1", "verified vs stock; switch routes the C driver through the Python channels"),
    ("exclusive channel isomeric cross sections + branching", "xsNNNNNN.L01..", "channelsout.f90:354", "channels",
     "PARTIAL", "Results.extras['xsNNNNNN.LMM', ':branch'] (INCOGNITA_CHANOBS)", "B1", "verified vs stock Co-59 (n,g) (n,2n)"),
    ("exclusive channel fission", "xsNNNNNN.fis", "channelsout.f90:552", "channels", "PARTIAL",
     "Results.extras['xsNNNNNN.fis'] (INCOGNITA_CHANOBS)", "B1", "multi-chance fission; vs stock U-238 within the engine's own (n,f) difference (<= 10 %)"),
    ("exclusive (n,x) totals per ejectile", "nn.tot np.tot ...", "totalout.f90:1", "", "SUPPORTED",
     "Results.totals_mb['np'] ...", "", "one-particle channel of each ejectile"),
    ("total particle production + multiplicity (gas production)", "gprod.tot nprod.tot pprod.tot ... aprod.tot", "finalout.f90:359",
     "outexcitation", "PARTIAL", "Results.extras['<p>prod.tot', ':multiplicity'] (INCOGNITA_CHANOBS)", "B1",
     "H/He gas production; completed with the non-compound binary emission (TRITFID off) -- verified vs stock"),
    ("residual production", "rpZZZAAA.tot", "residualout.f90:1", "fileresidual", "SUPPORTED",
     "Results.residual_production_mb['rpZZZAAA']", "", ""),
    ("residual isomer production", "rpZZZAAA.L02 ...", "residualout.f90:1", "isomer, fileresidual", "PARTIAL",
     "Results.residual_production_mb['rpZZZAAA.LNN'] (INCOGNITA_RESISO)", "B1", "off by default; isomeric ratios derive from it"),
    ("total residual production", "(talys.out)", "residualout.f90:1", "", "SUPPORTED", "Results.totals_mb['residual_production']", "", ""),
    ("discrete level cross sections (binary)", "nn.L01 np.L00 ...", "discreteout.f90:1", "outdiscrete, filediscrete",
     "SUPPORTED", "Results.levels_mb['nn.L01']", "", "inelastic per level incl. direct + compound"),
    ("exclusive discrete / continuum split", "nn.tot np.tot cols 3-5, nn.con", "discreteout.f90:1", "outdiscrete", "PARTIAL",
     "Results.extras['<k0><p>.tot:discrete', ':continuum'] (INCOGNITA_CHANOBS); Results.spectra['<k0><p>.tot:ngn'] "
     "(xsngn, any B4 switch)", "B1, B4", "xsngn vs stock Fe-56: 1e-4 at 1, 5 MeV; 14 MeV +4 to +24 % (engine's own CN "
     "decay difference)"),
    ("direct / DWBA / giant-resonance / collective components", "direct.tot, talys.out", "directout.f90:1", "outdirect, components",
     "INTERNAL", "direct/chain.py xsdirdisctot, xsgrcoll, xscollconttot", "B4", "r52pool dir-log hook captures them"),
    ("compound / pre-equilibrium components", "talys.out, components", "totalout.f90:1", "components", "INTERNAL",
     "binary / preeq", "B4", ""),
    # --- fission ---
    ("fission cross section", "fission.tot", "fissionout.f90:1", "fission", "SUPPORTED", "Results.totals_mb['fission']", "",
     "TALYSworld channel"),
    ("fission per fissioning nuclide", "rpZZZAAA.fis", "fissionout.f90:1", "filefission, fisfeed, outfission",
     "SUPPORTED", "fisobs.py Results.extras['rpZZZAAA.fis'] (INCOGNITA_FISOBS)", "B8",
     "xsfeed(Z, N, -1); U-238 / U-235 / Pu-239 / Th-232 vs stock within the engine's own (n,f) difference; sums to fission.tot"),
    ("fission per excitation bin", "fisZZZAAAEeeee.eee.feed", "multiple.f90:884", "fisfeed", "PARTIAL",
     "fisobs.py Results.spectra['fisZZZAAA.feed', ':Ex']", "B8",
     "Ex and Population columns (same rows as stock); the J-parity columns (fisfeedJP) are not given"),
    ("fission transmission / barrier info", "talys.out, tfis*", "tfissionout.f90:1", "outfission", "PARTIAL", "ingredients.py", "B5", ""),
    ("fission fragment / product yields", "yieldA*.fis yieldZA*.fis", "massdisout.f90:1", "massdis, fymodel, ffmodel, outfy",
     "MISSING", "", "B14", "GEF/Brosa (massdis.f90 779 l.) or FF files"),
    ("prompt nubar (Wahl systematics)", "(not written by TALYS-2.25)", "nubarWahl.f90:1, totalxs.f90:124", "cnubar1, cnubar2",
     "SUPPORTED", "fisobs.py Results.extras['nubarn.tot:wahl']", "B8",
     "TALYS computes it and never writes it (massdis.f90:252 resets nubar before nubarout); transcription checked by hand"),
    ("prompt nubar, nu(A), P(nu) from fragments", "nubar*.tot nuA*.fis", "nubarout.f90:1, nudisout.f90:1",
     "massdis, ffevaporation", "MISSING", "", "B14", "requires FF evaporation"),
    ("prompt fission neutron spectrum (Iwamoto)", "pfnsEEEE.EEE.fis", "pfnsout.f90:1, iwamoto.f90:1",
     "pfnsmodel 1, tmadjust, fsadjust", "SUPPORTED",
     "fisobs.py Results.spectra['pfns.fis', ':E', ':Maxwell_ratio', ':CM'], extras['pfns.fis:E-average']", "B8",
     "U-238 / U-235 / Pu-239 / Th-232 at 1/5/14 MeV vs stock: same 293-point grid, E-average 1e-5, every column 2e-5"),
    ("prompt fission gamma spectra / PFNS from fragment decay", "pfgs*, pfns (pfnsmodel 2)", "ffevap.f90:1",
     "pfnsmodel 2, massdis", "MISSING", "", "B14", "pfnsmodel 2 without massdis writes no PFNS in TALYS either"),
    # --- gamma ---
    ("discrete gamma-ray production lines", "gamZZZAAALnnLmm.tot", "gamdisout.f90:1", "outgamdis, filegamdis", "SUPPORTED",
     "specobs.py Results.spectra['gamZZZAAALiiLjj.tot'] (+ files, INCOGNITA_SPECOBS_DIR)", "B4",
     "conversion-corrected (cascade.f90:78); Fe-56 846.8 keV vs stock 1e-5 at 1, 5 MeV, 1.2 % at 14 MeV; other "
     "residuals' lines track the engine's channel xs (14 MeV (n,p) lines +12-17 %)"),
    ("photon production spectrum", "gspec*.tot", "spectraout.f90:1", "outspectra", "SUPPORTED",
     "specobs.py Results.spectra['gspec.tot'] (+ columns)", "B4", "Fe-56 5 MeV 5e-5 per bin, 14 MeV 2 %"),
    # --- angular ---
    ("elastic angular distribution", "nn0014.000ang.L00 / nnang.L00", "angleout.f90:1", "outangle, fileelastic, angles",
     "SUPPORTED", "angout.py Results.angular['nnang.L00'] (+ TALYS files, INCOGNITA_ANGOUT_DIR)", "B3",
     "shape + compound; vs stock Fe-56, Pb-208, U-238 at 1-14 MeV <= 0.5 % per angle (test:test_angout.py, b3_compare.py)"),
    ("inelastic discrete angular distributions", "nn0014.000ang.L01 ...", "angleout.f90:1", "outangle, fileangle",
     "SUPPORTED", "angout.py Results.angular['nnang.LNN'] (DWBA / coupled channels + compound + discrete PE Kalbach)", "B3",
     "first levels vs stock Fe-56, Pb-208, U-238 <= 0.5 % per angle; compound part tracks the engine's own level xs"),
    ("other discrete angular distributions", "np0014.000ang.L00, ng..., na...", "angleout.f90:1, angdis.f90:1",
     "outangle, fileangle", "SUPPORTED", "angout.py + compound/ceang_types.py (cleg of every residual)", "B3",
     "Fe-56/Pb-208 (n,p) (n,a) (n,d) (n,g) levels: shape 1e-5 of stock; absolute = the engine's level xs (14 MeV +15 %)"),
    ("Legendre coefficients", "nn0014.000leg.L00 ...", "angleout.f90:1", "outlegendre", "PARTIAL",
     "angout.py Results.angular['<k0><t>leg.LNN'] (Total, Direct, Compound, Normalized, ENDF-6)", "B3",
     "L0-L4 to 1e-4; small high-L direct coefficients 1-5 %; charged-particle elastic Direct column (ECIS's "
     "Coulomb-subtracted expansion) MISSING"),
    ("charged-particle elastic ratio to Rutherford", "pp0014.000ang.L00 (xs/Rutherford, Nuc+interfer.)",
     "angleout.f90:1, incidentread.f90:1", "outangle", "SUPPORTED",
     "angout.charged_elastic (Coulomb amplitude + phases on the engine's S-matrix)", "B3",
     "p + Nb-93 5, 14 MeV: ratio to 1e-4 of stock; spherical targets only (coupled charged targets: no shape elastic); "
     "0 degrees written as ratio 1, xs 0"),
    ("compound angular distributions for charged particles", "pp*ang.L*, pn*ang.L* Compound column", "angdis.f90:1",
     "cpang", "SUPPORTED", "angout.py (flagcompang = (k0 = 1 or cpang) and outangle and E <= 50)", "B3",
     "p + Nb-93 14 MeV cpang y: 1e-5 of stock; HRTW/GOE widthmode: isotropic (CEANG is Moldauer-only)"),
    # --- spectra / DDX ---
    ("emission spectra (angle-integrated)", "nspec0014.000.tot ...", "spectraout.f90:1, spectra.f90:1",
     "outspectra, filespectrum, adddiscrete, addelastic, channelenergy, elwidth", "SUPPORTED",
     "specobs.py Results.spectra['<x>spec.tot'] (+ E, Direct, Preeq, Mult. preeq, Compound, ratios; Eaverage_<x>.out)",
     "B4", "TALYS's espec grid exactly; Fe-56 vs stock per bin > 1 mb/MeV: 1e-5 (1 MeV), 2e-4 (5 MeV); 14 MeV n 5.5 %, "
     "p 15 % = the engine's own compound / (n,p) differences (pre-equilibrium column 4e-5)"),
    ("double-differential cross sections", "nddxE0014.000A030.0.deg, nddxE0014.000E0003.0.MeV", "ddxout.f90:1",
     "ddxmode, fileddxe, fileddxa, anglescont, blockddx", "SUPPORTED",
     "specobs.py Results.spectra['<x>ddx', '<x>ddxAaaa.a.deg', '<x>ddxEeeee.e.MeV']", "B4",
     "Kalbach PE / MPE, isotropic compound, discad peaks; Fe-56 30/90/150 deg: 1.4e-3 at 5 MeV, 14 MeV n 9 % p 15 % "
     "(engine's compound and level xs); giant-resonance / collective-continuum part isotropic (TALYS: DWBA shape)"),
    ("DDX in LAB frame", "*.lab", "ddxout.f90:1", "labddx", "MISSING", "", "B7", "needs recoil kinematics"),
    ("exclusive channel spectra", "sp100000E0014.000.tot ...", "channelsout.f90:641, channels.f90:330-420, "
     "specemission.f90:1", "outspectra + channels, filechannels", "MISSING", "", "B4b",
     "needs specexcl carried through the channel loop (binemis per daughter bin + specemission, 306 l.); "
     "only the sp000000 (n,gx) columns exist (xsngnspec = specout per-nucleus emission of the CN). "
     "`channelenergy` is NOT this: it is spectra.f90's flagEchannel energy conversion (B4, supported)"),
    ("emission spectrum per excitation bin", "", "binaryout.f90:1", "outbinspectra", "NA", "", "", "debug output"),
    # --- recoil ---
    ("recoil spectra of residuals", "recZZZAAAspec*.tot", "recoilout.f90:1", "recoil, filerecoil, maxenrec, anglesrec",
     "MISSING", "", "B7", "recoilinit.f90 576 l. + angdisrecoil 491 l."),
    # --- low energy / resonances ---
    ("unresolved resonance parameters", "urr.dat urr*.lLL urrtalys.tot urrnjoy.tot urrratio.tot", "urrout.f90:1, urr.f90:1",
     "urr, lurr, urrnjoy, rprime", "SUPPORTED", "urr.py (Results.urr, urr.write_files)", "B10",
     "test:test_kwcov_b10.py; every number vs stock: Fe-56 5e-5, Co-59 1e-4, U-238 0.11 % and Au-197 2e-4 in TALYS mode "
     "(default mode: U-238 Gf 22 % = EXACTFIS, Au-197 Gx/capture = CCEXITNB2); keyword responses <= 3e-4. "
     "Not: Ninclow energies, widthmode 2/3"),
    ("resonance-range pointwise / groupwise data", "total.tot elastic.tot xs*.tot rp*.tot below the URR, *.point, *.group",
     "resonance.f90:1", "resonance, group, reslib, tres", "MISSING", "input/fitlib.py RESONANCE_REFUSAL", "B10b",
     "resonance y REFUSED: needs Cullen's PREPRO (prepro.f, 29,688 lines) on the ENDF-6 resonance files; group / reslib / "
     "tres act only inside it"),
    ("effective cross sections in integral spectra", "integral.dat", "integral.f90:1", "integral", "SUPPORTED",
     "integral.py (run_deck -> Results.integral)", "B10b",
     "test:test_kwcov_b10b.py; port on stock's xs files 1e-6, engine vs stock 3e-5 (TALYS mode, Fe-56 / Co-59 sacs rows). "
     "Deck triples give no row (TALYS-2.25 bug, kept)"),
    ("cross sections below eninclow (thermal / 1/v region)", "every .tot file's rows below eninclow",
     "thermal.f90:1, thermalxs.f90:1", "xscaptherm, xsptherm, xsalphatherm, elow", "SUPPORTED",
     "thermal.py (Results.thermal, output only)", "B10b",
     "test:test_kwcov_b10b.py; port on stock's eref row 2e-6; engine vs stock (TALYS mode) Fe-55/56/61, Ag-109 (isomer "
     "branches), U-238 <= 6e-6; default mode the elastic/total rows carry LOWEPOT's elastic (x274 lower for Fe-56). "
     "Not: rp*.Lnn rows (no engine residual-isomer output)"),
    ("S0, S1, R', D0, <Gamma_gamma> (resonance parameters)", "spr.opt, ld*.gs, psf*.E1 headers",
     "spr.f90, densityout.f90, gammaout.f90", "outomp, outdensity, filepsf", "SUPPORTED",
     "ingredients.py (D0, Gg, S0) + ingout.py (the files)", "B13", "test:test_kwcov_b13.py"),
    # --- astro / medical ---
    ("astrophysical reaction rates", "astrorate.g/p/a/f, astrorate.tot, astrorateZZZAAA.tot, .LNN", "astroout.f90:1",
     "astro, astrogs, astroex, astroT, astroE, nonthermlev", "SUPPORTED",
     "astro/rates.py, astro/thermal.py (run_deck -> Results.astro, rates.write_files)", "B9",
     "test:test_kwcov_b9.py; Fe-56 (n,g) rate 1.27 % vs stock over T9 1e-4..10, G(T) 1.35 %; Au-197 limited by the "
     "engine's default (n,n')/(n,g) above 0.1 MeV (plan B9)"),
    ("MACS", "macs.g", "astroout.f90:1", "astro, astroE", "SUPPORTED", "astro/rates.py (MACS column + macs.g)", "B9",
     "test:test_kwcov_b9.py; Au-197 30 keV 929.9 vs stock 934.4 mb. The published library's MACS are NOT this path "
     "(scripts/release, ground-state curve, exact log-log integral)"),
    ("isotope production yields / activities (medical)", "Y*.tot", "prodout.f90:1, prodyield.f90:1",
     "production, ebeam, eback, ibeam, tirrad, tcool, area, rho, radiounit, yieldunit", "SUPPORTED",
     "production.py (Results.production, write_files; charged projectiles)", "B11",
     "test:test_kwcov_b11.py; port on stock rp = stock Y to 1e-6; engine vs stock = the production-rate difference "
     "(Ga-68 0.001 %, Tc-99m 0.07 %, F-18 0.49 %, At-211 0.77 %); natural targets (mass 0) refused"),
    # --- ingredients / diagnostics ---
    ("level densities", "ld*.gs ld*.bNN nld*.tab", "densityout.f90:1", "outdensity, filedensity", "SUPPORTED",
     "ingout.py (Results.ingout, write_files)", "B13", "test:test_kwcov_b13.py; tables <= 0.012 %, nld (es9.2) <= 1 % "
     "in TALYS mode; fission barriers included"),
    ("photon strength functions", "psf*.E1 psf*.M1 psf*.E2 psf*.M2 cross_g.tot", "gammaout.f90:1", "outgamma, filepsf",
     "SUPPORTED", "ingout.py (Results.ingout)", "B13", "test:test_kwcov_b13.py; Fe-57 <= 0.0034 %; U-239 E1 85-89 % "
     "at 0.4/0.6 MeV (T-dependent table, port difference recorded)"),
    ("transmission coefficients / inverse cross sections", "transmission_*.out cross_*.tot transmission_inc.out",
     "inverseout.f90:1, incidentout.f90:1", "outinverse, outtransenergy", "SUPPORTED", "ingout.py (Results.ingout)",
     "B13", "test:test_kwcov_b13.py; <= 0.0008 % (TALYS mode)"),
    ("optical-model parameters", "omppar_*.out omp.out ompE*.tot spr.opt, talys.out KD03", "inverseecis.f90, "
     "incidentread.f90, spr.f90, opticalnp.f90", "outomp, outkd, blockomp", "SUPPORTED", "ingout.py (Results.ingout)",
     "B13", "test:test_kwcov_b13.py; omppar <= 0.0004 %, omp.out <= 0.044 %"),
    ("populations / decay per bin", "population*.out", "multiple.f90", "outpopulation, outdecay", "INTERNAL", "emission/*", "", ""),
    ("pre-equilibrium output", "talys.out", "preeqout.f90:1", "outpreequilibrium", "INTERNAL", "preeq/*", "", ""),
    ("discrete level / structure tables", "levels*.out levels.out", "levelsout.f90:1", "outlevels, blocklevels, outbasic",
     "SUPPORTED", "ingout.py (Results.ingout)", "B13", "test:test_kwcov_b13.py; identical to stock"),
    ("model parameter table (TASMAN/covariance input)", "parameters.dat", "partable.f90, finalout.f90, nuclides.f90",
     "partable", "SUPPORTED", "ingout.py (Results.ingout['parameters.dat'])", "B13",
     "test:test_kwcov_b13.py; identical keys, values to f10.5 except the CT matching energies (<= 1.3e-4)"),
    ("ENDF-6 helper outputs", "endf.cs, *.ang for ENDF", "endfinfo.f90", "endf, endfdetail", "MISSING", "", "B12",
     "TEFAL input; low value for us"),
    ("statistical analysis of cross sections", "sacs.dat", "sacs.f90:1", "sacs", "MISSING", "", "B12", ""),
    # --- projectiles ---
    ("charged-particle induced reactions (p d t h a)", "all", "", "projectile", "PARTIAL", "projectile.py (INCOGNITA_CPINC)", "",
     "ported, behind env switch"),
    ("photonuclear reactions", "all", "", "projectile g", "PARTIAL", "projectile.py (engine.run only)", "", ""),
    ("natural-element targets", "all + natural sums", "natural.f90:1", "mass 0, abundance", "SUPPORTED",
     "natural.py (run_deck mass 0 -> weighted Results + Results.natural)", "B10b",
     "test:test_kwcov_b10b.py; sums = weighted isotope runs to 2e-16; stock natural = stock isotope sums 4e-7. Spectra / "
     "angular not summed (natural.f90 interpolates them); binary.tot and xs*.Lnn ARE summed here (TALYS leaves the last "
     "isotope's)"),
    ("isomeric (excited) targets", "all", "", "ltarget", "MISSING", "structure/levels.py:171 refuses", "KNOWN GAP",
     "engine refuses Ltarget /= 0"),
]


def main() -> None:
    out = ROOT / "docs/hf/observable_coverage.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(COLS)
        w.writerows(ROWS)
    from collections import Counter
    print(len(ROWS), dict(Counter(r[4] for r in ROWS)), file=sys.stderr)


if __name__ == "__main__":
    main()
