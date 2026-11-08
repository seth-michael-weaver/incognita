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
    ("exclusive discrete / continuum split", "nn.tot np.tot cols 3-4, nn.con", "discreteout.f90:1", "outdiscrete", "PARTIAL",
     "Results.extras['<k0><p>.tot:discrete', ':continuum'] (INCOGNITA_CHANOBS)", "B1", "the (n,gn) column xsngn is MISSING"),
    ("direct / DWBA / giant-resonance / collective components", "direct.tot, talys.out", "directout.f90:1", "outdirect, components",
     "INTERNAL", "direct/chain.py xsdirdisctot, xsgrcoll, xscollconttot", "B4", "r52pool dir-log hook captures them"),
    ("compound / pre-equilibrium components", "talys.out, components", "totalout.f90:1", "components", "INTERNAL",
     "binary / preeq", "B4", ""),
    # --- fission ---
    ("fission cross section", "fission.tot", "fissionout.f90:1", "fission", "SUPPORTED", "Results.totals_mb['fission']", "",
     "TALYSworld channel"),
    ("fission per fissioning nuclide", "rpZZZAAA.fis", "finalout.f90:396", "fission", "INTERNAL", "fission/chain.py", "B5", ""),
    ("fission transmission / barrier info", "talys.out, tfis*", "tfissionout.f90:1", "outfission", "PARTIAL", "ingredients.py", "B5", ""),
    ("fission fragment / product yields", "yieldA*.fis yieldZA*.fis", "massdisout.f90:1", "massdis, fymodel, ffmodel, outfy",
     "MISSING", "", "B8", "GEF/Brosa (massdis.f90 779 l.) or FF files"),
    ("prompt nubar, nu(A), P(nu)", "nubar*.tot nuA*.fis", "nubarout.f90:1, nudisout.f90:1", "massdis, ffevaporation",
     "MISSING", "", "B8", "requires FF evaporation"),
    ("prompt fission neutron/gamma spectra (PFNS/PFGS)", "pfns*.fis pfgs*", "pfnsout.f90:1, iwamoto.f90:1", "pfnsmodel",
     "MISSING", "", "B8", "pfnsmodel 1 (Iwamoto, 387 l.) is the cheap first step"),
    # --- gamma ---
    ("discrete gamma-ray production lines", "gamZZZAAALnnLmm.tot", "gamdisout.f90:1", "outgamdis, filegamdis", "PARTIAL",
     "specout.py (INCOGNITA_SPECOUT)", "B3", "lines collected; TALYS file naming/units not checked"),
    ("photon production spectrum", "gspec*.tot", "spectraout.f90:1", "outspectra", "PARTIAL", "specout.py", "B3", ""),
    # --- angular ---
    ("elastic angular distribution", "nnang.L00 / elastic angle files", "angleout.f90:1", "outangle, fileelastic, angles",
     "PARTIAL", "specang.py (INCOGNITA_SPECOUT)", "B2", "shape + compound elastic; Legendre form"),
    ("inelastic discrete angular distributions", "nnang.L01 ...", "angleout.f90:1", "outangle, fileangle", "PARTIAL",
     "specang.py", "B2", ""),
    ("Legendre coefficients", "nnleg.L00 ...", "angleout.f90:1", "outlegendre", "PARTIAL", "specang.py c_L", "B2", ""),
    ("charged-particle elastic ratio to Rutherford", "ppang.L00", "angleout.f90:1", "outangle", "MISSING", "", "B2",
     "needs Coulomb amplitude for p/d/t/h/a incident"),
    ("compound angular distributions for charged particles", "", "angdis.f90:1", "cpang", "MISSING", "", "B2", ""),
    # --- spectra / DDX ---
    ("emission spectra (angle-integrated)", "nspec010.000.tot ...", "spectraout.f90:1", "outspectra, filespectrum", "PARTIAL",
     "specout.py (INCOGNITA_SPECOUT)", "B3", "C path only"),
    ("double-differential cross sections", "nddx*.deg nddxE*.mev", "ddxout.f90:1", "outspectra, fileddxe, fileddxa, ddxmode",
     "PARTIAL", "specang.py Kalbach", "B3", ""),
    ("DDX in LAB frame", "*.lab", "ddxout.f90:1", "labddx", "MISSING", "", "B7", "needs recoil kinematics"),
    ("exclusive channel spectra", "spNNNNNN*.tot", "channelsout.f90:641", "channelenergy, filechannels", "MISSING", "", "B3", ""),
    ("emission spectrum per excitation bin", "", "binaryout.f90:1", "outbinspectra", "NA", "", "", "debug output"),
    # --- recoil ---
    ("recoil spectra of residuals", "recZZZAAAspec*.tot", "recoilout.f90:1", "recoil, filerecoil, maxenrec, anglesrec",
     "MISSING", "", "B7", "recoilinit.f90 576 l. + angdisrecoil 491 l."),
    # --- low energy / resonances ---
    ("unresolved resonance parameters", "urr*.dat urrtalys.tot", "urrout.f90:1, urr.f90:1", "urr, lurr, urrnjoy", "MISSING",
     "", "B6", ""),
    ("resonance-range / groupwise / integral data", "resonance.tot group*.tot integral.dat", "resonance.f90:1, integral.f90:1",
     "resonance, group, integral, reslib, tres", "MISSING", "", "B6", "uses external resonance libraries"),
    ("thermal cross sections", "talys.out", "thermal.f90:1, thermalxs.f90:1", "xscaptherm, xsptherm, xsalphatherm", "MISSING", "", "B6", ""),
    ("S0, S1, R', D0, <Gamma_gamma> (resonance parameters)", "talys.out", "incidentout.f90, densityout.f90", "",
     "PARTIAL", "ingredients.py (D0, Gg, S0)", "B4", ""),
    # --- astro / medical ---
    ("astrophysical reaction rates", "astrorate.g ...", "astroout.f90:1", "astro, astrogs, astroex, astroT, astroE", "PARTIAL",
     "astro/stellar.py (INCOGNITA_STELLAR)", "B9", "rate + SEF; keyword not wired, file format not matched"),
    ("MACS", "macs.g", "astroout.f90:1", "astro", "PARTIAL", "fewres.py / chart scripts", "B9", "post-processed from capture"),
    ("isotope production yields / activities (medical)", "Y*.tot", "prodout.f90:1, prodyield.f90:1",
     "production, ebeam, eback, ibeam, tirrad, tcool, area, rho, radiounit, yieldunit", "MISSING", "", "B10",
     "post-processing of residual production + decay data"),
    # --- ingredients / diagnostics ---
    ("level densities", "ld*.tot nld*.tab", "densityout.f90:1", "outdensity, filedensity", "PARTIAL", "ingredients.py", "B11", ""),
    ("photon strength functions", "psf*.E1", "gammaout.f90:1", "outgamma, filepsf", "PARTIAL", "ingredients.py", "B11", ""),
    ("transmission coefficients / inverse cross sections", "talys.out", "inverseout.f90:1", "outinverse, outtransenergy",
     "INTERNAL", "omp/*", "B11", ""),
    ("optical-model parameters", "talys.out", "incidentout.f90", "outomp, outkd", "INTERNAL", "omp/parameters.py", "B11", ""),
    ("populations / decay per bin", "population*.out", "multiple.f90", "outpopulation, outdecay", "INTERNAL", "emission/*", "", ""),
    ("pre-equilibrium output", "talys.out", "preeqout.f90:1", "outpreequilibrium", "INTERNAL", "preeq/*", "", ""),
    ("discrete level / structure tables", "talys.out", "levelsout.f90:1", "outlevels", "NA", "", "", ""),
    ("model parameter table (TASMAN/covariance input)", "parameters.dat", "nuclides.f90 (partable block)", "partable", "MISSING", "", "B11",
     "covariances are TASMAN's (we have tmc.py); parameters.dat lets TASMAN-style sampling see every value used"),
    ("ENDF-6 helper outputs", "endf.cs, *.ang for ENDF", "endfinfo.f90", "endf, endfdetail", "MISSING", "", "B12",
     "TEFAL input; low value for us"),
    ("statistical analysis of cross sections", "sacs.dat", "sacs.f90:1", "sacs", "MISSING", "", "B12", ""),
    # --- projectiles ---
    ("charged-particle induced reactions (p d t h a)", "all", "", "projectile", "PARTIAL", "projectile.py (INCOGNITA_CPINC)", "",
     "ported, behind env switch"),
    ("photonuclear reactions", "all", "", "projectile g", "PARTIAL", "projectile.py (engine.run only)", "", ""),
    ("natural-element targets", "all + natural sums", "natural.f90", "mass 0, abundance", "MISSING", "", "B6", ""),
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
