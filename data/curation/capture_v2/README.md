# Curated EXFOR capture set v2.2 (CAPSET-v2.2), Z 1-92

**Version 2.2 (2026-11-07).** The tables here are v2.2: v2.1 plus the six Celenk 1991 total cross sections excluded,
step S10 (section "v2.2" at the end). v2.1 was v2 (below) plus the corrections of the 2026-11-07 data review, step S9
(section "v2.1"). File names are unchanged (`*_v2.parquet`); `provenance.json` and `counts_v2.json` carry
`"version": "2.2"`. The v2 and v2.1 results are still reproduced exactly by the same script (ladder steps S8 and S9,
0 of 12 432 decisions differ from the shipped v2 and v2.1) and are kept as the `S8_prelm_final` and `S9_v21` columns of
`ladder_v2.csv`.

EXFOR-derived (IAEA Nuclear Data Section and the NRDC network), CC BY 4.0. `SHA256SUMS` checks every data file.
Built 2026-11-06 by `scripts/build_capture_v2.py` from the 2026-10-14 EXFOR snapshot (`entry_2026-10-14.zip`).

This is a NEW version of the curated capture tables in `../inputs/` (Z 26-92 run 2026-09-12, Z 1-25 run 2026-11-06).
Those files are not changed. No shipped model, library or score reads this directory; `ADOPTION.md` says what would
change for a model or score that switches to it. ("v2" here is the capture set's version. The curation REGISTER v2,
`../curation_register_v2.*`, is a different product built from the v1 cells; see ADOPTION.md.)

| file | what |
|---|---|
| `exfor_capture_Z26-92_trust_v2.parquet` | one row per dataset, Z 26-92, the schema of `../inputs/exfor_capture_Z26-92_trust.parquet` |
| `exfor_cells_Z26-92_v2.parquet` | one row per dataset and 0.1-dex bin, the schema of `../inputs/exfor_cells.parquet` |
| `exfor_capture_Z1-25_trust_v2.parquet`, `exfor_cells_Z1-25_v2.parquet` | the same for Z 1-25 |
| `review_decisions_capture_v2.jsonl` | every decision this version adds (390 v2 lines + 15 v2.1 lines with `"version": "2.1"` + 6 v2.2 lines with `"version": "2.2"`), review-decision format, each with rule code, reason and EXFOR id |
| `ladder_v2.csv` | the decision of every dataset after each fix step S0-S10 (below), and the CAPSET-v2 rule that decided it |
| `counts_v2.json` | all counts quoted here, per defect and per step |
| `provenance.json` | inputs and their SHA256 (entry zip, staging, the three human-decision files), code, checks |

## How it was made

1. **Staging.** Every entry of the zip that holds `(N,G)` is parsed by this repository's `data/ingest/exfor.py` with the
   six CAPSET-v2 parser fixes switched on (`V2_FIXES`; they are opt-in, so the default ingest is byte-identical to before).
   Capture predicate and clip of `python -m data.ingest.exfor --subset capture` (SF2 N, SF3 G, SF6 SIG/RI, points
   <= 20 MeV), Z 1-92 together: 12 432 measurements. Check: the same code with only the number fix reproduces an
   earlier staging of the same snapshot with the number fix applied (`exfor_capture_Z26-92_2026-10-14_x4fix1`) exactly,
   10 706 of 10 706 rows.
2. **Curation.** The automatic quality model (`data/curate/quality_model.py`, `review_log.py`, unchanged) runs once
   on Z 1-92, as for the light run. Human-decision file = the Z 26-92 `review_decisions.jsonl` (sha in provenance) +
   `../inputs/review_decisions_Z1-25.jsonl` + `review_decisions_capture_v2.jsonl` (later lines override). The consensus
   fit leaves out the 300 datasets that a CAPSET-v2 line excludes (as it already leaves out compilations), and re-bases
   absolute-unit uncertainties (fix D4).
3. **Cells.** `discrepancy.cells_from_parquet` on the v2 staging, joined to the trust table; split at Z 25/26.

## The fixes, with counts before and after

"v1" = the shipped tables in `../inputs/`. Dataset counts exclude the 12 STD2017 anchor rows.

**D1. Fortran numbers with a blank exponent** (`"5.     -07"`, `"7.     -03"` read as NaN; `_NUM_FIX` at
exfor.py:214; an earlier correction patched staged files but not the parser). Fixed regex
`^([+-]?(?:\d+\.?\d*|\.\d+))([+-]\d+)$`.
Z 26-92: 87 datasets recovered (e.g. 11407012 Zr-96, 11658002/005 resonance integrals), 148 more datasets gain points
or uncertainties, 142 points and 241 uncertainty values recovered. Z 1-25: 15 datasets, 50, 70 points, 101 values.
(An earlier count of 87 / 55 points / ~99 uncertainties used Z 26-92 data only.)

**D2. Parser gaps.**
- Data heading `RATIO` (and `RATIO-ERR`): 4 datasets now staged (20942004, 21181002 ptr 1, 21181004, 21216002); 2 are
  excluded automatically (ratio to a non-standard, not convertible to barns), 2 kept.
- `EN-MIN-APX` / `EN-MAX-APX`: 15 resonance-integral datasets of entry 10637 now staged (9 in Z 26-92); 13 keep, 2 downweight.
- `KT-K` in `DEG-C`: kT = k_B (T + 273.15); 3 datasets (10013010, 31756002, 31756003), all keep.
- `(X(N,ABS),,SIG)=(X(N,G)...)` equivalences filed under the (N,G) leaf (the REACTION string is kept): 7 datasets,
  160 points (21178003, 21278005/008/011/013, 21322007/008), all keep.

**D3. Sums kept as single-isotope capture.** `incognita.bench.reaction_check.reaction_flags` (the REACTION-code rule of the
benchmark fix) is applied to every capture dataset; COMBO_SUM / COMBO_DIFF / COMBO_PROD -> exclude (rule
`D3_SUM_REACTION`). 12 datasets: 22580006 (Pd-106 + Pd-108), 40336092 (Te-128 + Te-130), 40385003 (U-235 (n,g) +
(n,f)), 30567005 ptr 2 (Pd-109 G + 1.006 x M, FCT, was keyed state G), 30268015 and 30400038/045/046/048/050/051/052
(fission-spectrum sums). v1 used all 12 (11 keep, 1 downweight). Ratios and `=` equivalences are not excluded. The benchmark threshold rows
(n,2n)/(n,p)/(n,alpha) are not in this product; the benchmark row checks handle them
(`incognita/bench/reaction_check.py`).

**D4. Uncertainties.** New split (exfor.py `_split_uncertainty`): stat = ERR-S; sys = ERR-SYS, else
sqrt(ERR-T^2 - ERR-S^2) when both are given (568 datasets, `split_sys_derived`; v1 dropped ERR-T there); ERR-T with
ERR-SYS but no ERR-S: stat = sqrt(T^2 - SYS^2) (62, `total_minus_sys`; v1 counted the systematic part twice). An unsplit
total (ERR-T / DATA-ERR alone, 9 503 datasets, `total_unsplit`) stays stat_sigma as in v1, reduced by sqrt(n) in a
cell mean: on dense time-of-flight scans it is mostly counting statistics, and the correlated normalisation belongs
to the scatter model's per-dataset bias term (tau 3 %, 1 % floor). (Treating it as fully correlated sys_sigma
instead inflates dense cells, e.g. 1 583 usable Z 26-92 cells of >= 10 points at a median sys/sem of 2.2, 13742004
Sr-88 capped at 100 %, and double-counts the bias term.)
Others: split 348, stat only 330, sys only 27, none 1 594. Effect on the Z 26-92 cells' relative uncertainty (24 286
cells with an uncertainty in v1 and v2): median ratio 1.00, 8.1 % larger by > 5 %, 0.5 % smaller by > 5 %. Usable cells
of >= 10 points with a sys-only uncertainty: 23 (as v1).
Peelle's puzzle (rule: no data uncertainty proportional to the observed value): the cells' relative
uncertainties are already relative to the cell mean, not to each point; inside the consensus fit the 16 915 cells of
the 9 257 datasets whose uncertainty columns are in absolute units are re-based on the expected value of a first fit,
sigma / exp(mu + bias), instead of sigma / observed mean (factor clipped to [1/3, 3]; median |ln factor| 0.002).
Uncertainties given in per cent are already independent of the observed value. The shipped cells carry the reported
uncertainties; the re-basing is inside the fit only.

**D5. Duplicates and preliminary data.** A dataset whose EXFOR STATUS (subentry or SUBENT 001) says `(SPSDD,X)` or
`(DEP,X)` is excluded when X is in the set, is a measurement (not a V-entry compilation, not SF9 CALC/EVAL) and has the
same comparable quantity (group key: nuclide, MT, branch, kind, state); it is also left out of the consensus fit. Within
and across entries alike (v1 only shared weight within an entry). A dataset an earlier human line already decides keeps
that line (339, all of them excludes). In a mutual reference one member is kept (11).
- SPSDD: 96 excluded, DEP: 189 excluded (42 of the 285 cross-entry). Rule codes `D5_SPSDD`, `D5_DEP`, field `superseded_by`.
- Two excluded datasets point to an original that is itself superseded (C-14: 22254002 and 22895003 -> 22995002 ->
  22995004 ptr 2); the chain ends at a kept dataset.
- PRELM (STATUS PRELM): down-weighted (trust x0.25, the review `downweight`) wherever the automatic layer kept or
  down-weighted the dataset and no earlier human line decides it: 90 datasets (`D5_PRELM`). v1 used 115
  PRELM datasets (79 at full keep) in v1; the rest are excluded by D5/D3 or by earlier lines.

**D6. x1000-type slips** (hand lines, machine-checked against the EXFOR record):
- 14657002 Y-89(n,g)Y-90m thermal MXW, Krane 2020: 1.02 B vs 1 mb in 11870002, 23488032, 23266090/91 -> `fix-unit` 0.001.
- 13947004 Ni-60 partial gamma lines (PAR), Raman 2004: sum 3 693 B vs 2 744 MB for the same quantity in 30150003 ->
  `fix-unit` 0.001.
- 41639002 Sb-124 SPA, Murin 1957: 2000 B, DATA-APRX, no uncertainty, energy supposed by the compiler -> `exclude`
  on the record. It is NOT shown to be a unit slip: Elgart 1971 (10728004, MXW) gives 2990 B, Courtemanche 1966
  (11990002, SPA) 6.5 B. Sb-124 is left open for a human reviewer (10728004 and 11990002 keep their automatic decisions).

**D7. EXFOR version.** `exfor_version` of every staged row is the snapshot read, 2026-10-14 (`exfor_version_of(zip)`),
not the hard-coded 2026-08-27. The default ingest keeps the constant (reproducibility of v1); CAPSET-v2 runs and
`INCOGNITA_X4_V2` runs use the zip's date.

## Before / after

| | Z 26-92 v1 | Z 26-92 v2 | Z 1-25 v1 | Z 1-25 v2 |
|---|---|---|---|---|
| datasets | 10 619 | 10 728 | 1 695 | 1 704 |
| points | 688 818 | 689 138 | 266 299 | 266 308 |
| cells | 33 659 | 33 830 | 4 040 | 4 049 |
| keep / downweight / exclude / fix-unit (datasets) | 6 819 / 1 326 / 2 469 / 5 | 6 645 / 974 / 3 104 / 5 | 1 148 / 158 / 388 / 1 | 1 137 / 118 / 448 / 1 |
| cells keep / downweight / exclude / fix-unit | 23 866 / 8 341 / 1 439 / 13 | 23 259 / 6 919 / 3 647 / 5 | 3 115 / 675 / 249 / 1 | 2 992 / 625 / 431 / 1 |

No v1 dataset is missing from v2. The ladder (`ladder_v2.csv`, `counts_v2.json` "ladder") attributes every change:

| step (Z 26-92) | keep | downweight | exclude | fix-unit | changed vs previous step |
|---|---|---|---|---|---|
| S0 shipped v1 (2026-09-12, with the 12 review lines of 2026-11-06) | 6 819 | 1 326 | 2 469 | 5 | |
| S1 same parser, 2026-10-14 snapshot, current review files | 6 743 | 1 011 | 2 861 | 4 | 610 |
| S2 + D1 number fix | 6 702 | 1 135 | 2 865 | 4 | 375 |
| S3 + D2 parser gaps | 6 817 | 1 040 | 2 867 | 4 | 290 |
| S4 + D4 uncertainty split | 6 847 | 1 011 | 2 866 | 4 | 200 |
| S5 + D4 Peelle re-basing | 6 898 | 960 | 2 866 | 4 | 277 |
| S6 + D3 sums, D6 slips | 6 912 | 931 | 2 879 | 6 | 136 |
| S7 + D5 SPSDD / DEP | 6 724 | 895 | 3 104 | 5 | 423 |
| S8 + D5 PRELM = v2 | 6 645 | 974 | 3 104 | 5 | 79 |

Read this honestly: S1 alone (no fix, only the newer snapshot and review files) changes 610 decisions, and S2-S5 each
move a few hundred datasets across the keep / downweight boundary (trust 0.5) because the metadata prior and the
posterior trust are re-learned on every run. The resampling-stability check fails in every run on the 2026-10-14
snapshot (it failed for the light run too); the standards and spot-list checks pass. The fit stops at its 300-iteration
cap as every run of the quality model has (converged = false, rms step 9e-5). Decision changes that come from a rule are the S6-S8
steps (rule lines); the rest is the automatic layer's sensitivity, which v2 does not claim to fix. (S0 is read from the `../inputs/` tables as they ship, with the 12 Z 26-92 review lines
(11 more excludes).)

## v2.1 (2026-11-07)

Step S9 of `scripts/build_capture_v2.py`: re-staged with `V21_ALL` (the six v2 fixes + `encm`) and the energy fixes of
the D10 lines, the 15 v2.1 lines appended to the human-decision file, one more quality-model run. Lines: machine-checked
against their EXFOR records (the reasons quote them).

**D8. Centre-of-mass energies** (`data/ingest/exfor.py` fix `encm`, opt-in and NOT in `V2_ALL`, so v2 stays
reproducible). EN-CM, EN-RES-CM and EN-CM-MIN/-MAX were stored as `energy_ev`, which is the lab energy everywhere else.
Now E_lab = E_cm (A + a) / A (mass numbers; for a neutron E_lab = E_cm (A+1)/A, +14 % for Li-7, +7 % for C-14, +1.6 %
for Ni-63; a natural target uses its standard atomic weight). In the capture set: 11 datasets, 451 points (Z 1-25: 3
datasets, 47 points: C-14 Nakamura 2009 14224002 and Jiang 2025 14859002, Li-7 Izsak 2013 14378002, all DERIV from
Coulomb dissociation; Z 26-92: Ni-63 Weigand 2015 14446002, 207 points, and 7 V0012 evaluation datasets, excluded as
compilations anyway). One decision changes with the energies: 14224002 C-14 keep -> downweight.
In all of EXFOR 2026-10-14, 3 803 datasets take their incident energy from such a column; 437 (31 431 points) have a
neutron projectile, 307 of them (7 818 points) on Z 1-25 targets, 288 of these on P-31 (the V0016 evaluation file, mostly
DA/DE). Among the measured capture, (n,2n), (n,p), (n,alpha) products only the 11 datasets above and 6 light threshold
series (He-3(n,p), Be-7(n,p)/(n,alpha), all removed by the threshold rules before the rows; see
`../inputs/README.md`) are affected. Other staged products (elastic, inelastic, DE spectra) were not rebuilt.

**D9. Duplicates** (the same measurement compiled twice; the later copy excluded, the original kept), 12 datasets:
- Ba-132 MACS Dillmann 2010, 22939040 pointer 3 (JENDL-3.3 shape) = pointer 2 (JEFF) in all 11 values; pointer 3 excluded.
- Cl-35 Pavetich 2019, entry 31796 (002, 003, 004) = entry 23468 (compiled first, author-approved); 31796 excluded.
- P-31, I-127 (two), In-115 thermal activation Jozefowicz 1963, entry 31472 (002-005 pointer 2) = entry 31099; 31472 excluded.
- Te-122 / Te-124 isomer cross sections and resonance integrals Alpatov, journal 1995 (41168002-005) = report 1990
  (41039002-005), same samples and values; 41168 excluded.
Checked and NOT duplicates (left as they are): F-19 Uberseder 2007 22968005 / 22968008 (two different samples, C-F2 no. 1
and Na-F-1, whose 2007 values were both 3.46 mb, renormalised to 3.67 mb; their ratios to gold differ) and Pb-208 Ratzel
2004 22883012 / 22883013 (samples Pb2 and Pb3, both 0.292 mb in 2004, different uncertainties). The test of identical
datasets covers two or more equal cells; single-cell equalities (about 100 pairs, mostly thermal values equal to three
digits) were not reviewed.

**D10. Unit and energy slips**, 3 datasets:
- Mo-95 MACS Koehler 2022 14797006: 1018 ... 346 B at kT 5-30 keV are mb -> `fix-unit` 0.001 (v2: downweight, trust 6e-5).
- Te-120 Eastman 2008 14165012: a resonance integral (paper table 3, EN-MIN 0.5 eV) coded as a Maxwellian average at
  kT = 0.5 eV -> `exclude`.
- W-186 MACS Marganiec 2009 14248005: kT 5-100 compiled in EV, really keV -> energies x1000 at staging (line with
  `energy_fix`, no decision); the decision stays automatic (keep).

**Result.** Z 26-92: 10 728 datasets, 689 138 points, 33 823 cells (v2: 33 830; corrected energies fall into
different 0.1-dex bins); keep / downweight / exclude / fix-unit 6 664 / 945 / 3 113 / 6 (v2: 6 645 / 974 / 3 104 / 5); cells
23 527 / 6 625 / 3 657 / 14. Z 1-25: 1 704 datasets, 4 048 cells; 1 141 / 110 / 452 / 1 (v2: 1 137 / 118 / 448 / 1); cells
3 073 / 539 / 435 / 1. 138 decisions change from v2 (`ladder_v2.csv` S8 -> S9): 14 by the lines (13 keep -> exclude, 1
downweight -> fix-unit), 1 by the D8 energies (14224002), and 123 by the automatic layer re-learning its prior and trust
(80 downweight -> keep, 43 keep -> downweight, none to or from exclude), the same sensitivity as steps S1-S5 above. Checks
as v2: standards and spot list pass, resampling stability fails.

| step | Z 26-92 keep / dw / excl / fix | changed | Z 1-25 keep / dw / excl / fix | changed |
|---|---|---|---|---|
| S8 = v2 | 6 645 / 974 / 3 104 / 5 | | 1 137 / 118 / 448 / 1 | |
| S9 = v2.1 | 6 664 / 945 / 3 113 / 6 | 122 | 1 141 / 110 / 452 / 1 | 16 |

## v2.2 (2026-11-07)

Step S10 of `scripts/build_capture_v2.py`: the v2.1 staging (unchanged), the 6 v2.2 lines appended to the human-decision
file, one more quality-model run. Lines: rule `D11_TOTAL_XS`, each machine-checked against
the EXFOR record of the 2026-10-14 zip (the reasons quote it).

**D11. Total cross sections compiled as capture.** Celenk, Demirel, Ozmen 1991 (J. Radioanal. Nucl. Chem. 148, 393),
EXFOR 22234. The title says "macroscopic and microscopic thermal neutron cross sections ... using neutron self
absorption", and the ANALYSIS of subentry 001 (common to all six data subentries) says the photopeak areas against foil
thickness "were model fitted to yield the total thermal neutron macroscopic cross section", divided by the number of
nuclei per cm3. All six values are compiled as `(N,G) SIG` at EN-DUMMY 0.0253 eV with no uncertainty, and all six are
the total (removal) cross section of the natural-element foil, so all six are excluded:

| subentry | REACTION as compiled | value | capture (set consensus / known) | total | v2.1 -> v2.2 |
|---|---|---|---|---|---|
| 22234002 | V-51(n,g)V-52 | 10.13 b | 5.1 b | V: 10.5 b (EXFOR (N,TOT) thermal median) | downweight -> exclude |
| 22234003 | Co-59(n,g)Co-60m | 46.94 b | total capture 37.8 b (a partial to the isomer cannot exceed it) | 46.0 b | keep -> exclude |
| 22234004 | Cu-63(n,g)Cu-64 | 11.24 b | 4.4 b | natural Cu about 11.8 b | downweight -> exclude |
| 22234005 | In-115(n,g)In-116m1+m2 | 191.78 b | partial about 160-170 b | natural In about 196 b | keep -> exclude |
| 22234006 | Dy-164(n,g)Dy-165 (g, M+) | 1056 b | 2720 b | natural Dy about 1080 b (absorption 994 + scattering 90) | keep -> exclude |
| 22234007 | Au-197(n,g)Au-198 | 107.55 b | 98.7 b | about 106.6 b | keep -> exclude |

(V-51 had been only down-weighted by the automatic layer: its value is 2x the consensus but has no uncertainty.)

**Scan of the whole set for the same class of defect** (scan script not shipped; the thresholds are a search
aid, not a rule). (a) Values: the 2 031 datasets with a 2200 m/s (n,g) SIG point (0.02-0.03 eV, no SF8) were compared
with the capture consensus of their target (median of the kept / down-weighted total-capture values) and with the
target's thermal total and elastic cross sections from EXFOR itself ((N,TOT) / (N,EL) SIG medians at 0.02-0.03 eV, 202
and 294 targets). Flagged: value above the capture consensus by > max(2 sigma, 10 %) AND equal to the total (within
max(2 sigma, 5 %), scattering > 10 % of capture) or to the elastic cross section. 18 datasets; besides Celenk 002/003
none is a total on its record: Sims 1970 Yb-174 10608015, Friesenhahn 1966 W-182 12167011, Koehler 1994 Ir-193 14027003,
Widder 1975 Lu-175 20437010, Auclair 1955 U-236 21397003, Efimov 1956 U-236 40370002, Pavlenko 1976 Hf-176 40464005,
Danelyan 1964 / Vertebnyy 1970 Dy-161 40681002 / 41280039, Yoon 2005 I-127 30840002 are activation or capture-detector
measurements; Leinweber 2006 Gd-152 14110039 is computed from resonance parameters (its scattering is a separate
REACTION); Knopf 1997 Er-170 22450044 is a 1/v extrapolation of a capture value; Baston 1960 Lu-175 21322007 is an
absorption cross section (total minus 5.5 b potential scattering, compiled `(N,ABS)=(N,G)`, which for Lu-175 at thermal
is capture); Vertebny 1979 Cd-114 40122020 is a capture value derived from the 1/v part of the total (6.9 b, about the
Cd-114 scattering and 20 x the accepted 0.34 b capture, but labelled capture by the authors; left to the automatic
layer, which keeps it); V1002384 and V1002547 are evaluations, excluded anyway. (b) Text: 963 thermal datasets whose
BIB (subentry + 001) mentions total / absorption / transmission / scattering / macroscopic; of the 187 with a strong
term and a value off the consensus (or no consensus), all but Celenk are absorption = capture derived from transmission
(total minus scattering: Pattenden 1958, Vertebnyi 1975, Anufriev 1983, Doilnitsyn 1965/69, Kropff, Koester, Knopf,
...), activation values, or evaluations. Not excluded, left for a human reviewer: Gorshkov 1957 Sm-147 40363004 (1000 b
"absorption" from a fission-product yield analysis, 13 x the capture; not a total), Grishanin 1967 Gd-156 41244003
(13 b, PRELM, DEP). (c) REACTION codes: 19 staged datasets name (N,ABS) (none names (N,TOT), (N,NON), (N,EL) or
(N,X)): 12 ratios to a B-10 / B / U-235 / U-233 absorption standard and 7 compiler equivalences `(N,ABS)=(N,G)` (D2
eqroute); none is a total mislabelled as capture.

**Result.** Z 26-92: 10 728 datasets, 689 138 points, 33 823 cells (as v2.1); keep / downweight / exclude / fix-unit
6 673 / 931 / 3 118 / 6 (v2.1: 6 664 / 945 / 3 113 / 6); cells 23 426 / 6 721 / 3 662 / 14 (v2.1: 23 527 / 6 625 /
3 657 / 14). Z 1-25: 1 704 datasets, 4 048 cells; 1 140 / 110 / 453 / 1 (v2.1: 1 141 / 110 / 452 / 1); cells 3 103 /
508 / 436 / 1 (v2.1: 3 073 / 539 / 435 / 1). 116 decisions change from v2.1 (`ladder_v2.csv` S9 -> S10): **6 by the
review lines** (4 keep -> exclude and 1 downweight -> exclude in Z 26-92, 1 downweight -> exclude in Z 1-25) and **110
by the automatic layer re-learning its prior and trust** after six datasets leave the consensus fit (Z 26-92: 54
downweight -> keep, 41 keep -> downweight; Z 1-25: 7 downweight -> keep, 8 keep -> downweight; none to or from
exclude), the same sensitivity as steps S1-S5 and S9. Checks as v2.1: standards and spot list pass, resampling
stability fails.

| step | Z 26-92 keep / dw / excl / fix | changed | Z 1-25 keep / dw / excl / fix | changed |
|---|---|---|---|---|
| S9 = v2.1 | 6 664 / 945 / 3 113 / 6 | | 1 141 / 110 / 452 / 1 | |
| S10 = v2.2 | 6 673 / 931 / 3 118 / 6 | 100 (5 lines + 95 automatic) | 1 140 / 110 / 453 / 1 | 16 (1 line + 15 automatic) |

## Not done / open

- The parser fixes are opt-in (`V2_FIXES`, `INCOGNITA_X4_V2`), so the default ingest still reproduces v1; any staging
  can be rebuilt with them by the same script.
- Sb-124 (above); the fix-unit factors are logged, not applied (as in v1).
- The curation register v2 and its decisions were not re-run on these cells (its rules were fixed on the v1 cells;
  re-running it would be a new register version).
- No person has reviewed the 390 new lines; 387 are rule lines from the EXFOR record, 3 are machine-checked. The 15
  v2.1 lines are machine-checked, not reviewed by a person.
- v2.2: the 6 D11 lines are machine-checked, not reviewed by a person; the scan above did not read the 963 text hits
  one by one (only the 187 off the consensus or without one), and thermal values of targets without a capture
  consensus (mostly natural elements) were checked by text only.
- v2.1: the three pointers of each Dillmann DERIV MACS (22939, one SACS with three evaluated shapes) still count one
  measurement two or three times where their values differ; the v1 tables in `../inputs/` do not get the v2.1 lines.
