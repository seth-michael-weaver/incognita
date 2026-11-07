# Benchmark tracks: data cards

Every track is a fixed list of measured points. `rows/<track>.csv` is the public row table (row, Z, A, energy_ev,
quantity, spectrum, label = log10 of the measured value in barns, plus subset flags). `MANIFEST.json` holds, per track,
the sha256 of that table, the frozen source files it is cut from (with their sha256), the reference entry, the weighting,
the bootstrap seed and whether the track is retired from our own model selection. `python -m incognita.bench.score tracks`
rebuilds every table from the frozen sources and refuses to run if a source hash differs.

Scoring rule (all tracks): e = log10(prediction / measurement); rms over covered rows (prediction finite and > 0);
95 % CI by nucleus bootstrap; Δ = paired difference against the reference entry on the rows both cover. A submission
that covers fewer rows is scored on what it covers and the coverage is printed next to the score: compare entries on
the paired Δ or on full-coverage rows, not on rms alone.

**Licences.** Every label is derived from EXFOR (IAEA Nuclear Data Section and the NRDC network; open access, cite the
EXFOR entries and Otuka et al., Nucl. Data Sheets 120 (2014) 272), except 9 points of `na-post2021` that were
hand-compiled from an open-access paper (Jiang et al., Chin. Phys. C 46 (2022) 024001). No evaluated-library value is in
any track; libraries are scored from the user's own copies. MACS labels (KADoNiS, ASTRAL) are NOT published: their
redistribution terms were not verified, so the MACS comparisons in the README stay "reported, not reproducible here".

**Status of every track: RETIRED from our internal selection when published (2026-09-27).** Publishing a label spends
it: from then on no INCOGNITA model may be chosen, tuned or gated on these rows. Our new held-out data are the
prospective registries (`docs/registry/`) and EXFOR entries added after the 2026-09-09 snapshot.

| track | rows / nuclei | what | source (frozen) | reference | blind for us? | blind for libraries? |
|---|---|---|---|---|---|---|
| `capture-heldout` | 3477 / 184 | capture σ(E), keV-MeV, one value per (nucleus, energy bin): the trust-weighted, curation-audited (rule P) EXFOR mean. Z ≤ 82, cells where all four of our frozen predictors exist | `docs/release/exam/capture_blind_cells.parquet` | default TALYS (TENDL no-data recipe, our engine), D0 withheld | yes: the nucleus was held out of our fit (8 contiguous folds) | **no**: evaluators fitted these data |
| `capture-nostructure` | 1962 / 125 | same cells, DEV folds 0-5, original (pre-audit) targets; model given no structure data | same | default TALYS, no structure data | yes | no |
| `capture-retro` | 286 / 16 | capture σ measured after year Y (Y = 2015-2023); rule-P datasets removed | `docs/release/exam/retro_rows.parquet` | default TALYS | yes (trained on data up to Y) | only releases dated ≤ Y (ENDF/B-VII.0 2006, JENDL-4.0 2010, ENDF/B-VII.1 2011, and the dated TENDL-Y entry) |
| `dated-2006` … `dated-2024` (9 tracks) | 4480 / 218 … 214 / 12 | all 7 channels, EXFOR rows published AND compiled after Y (Y = 2006, 2010, 2011, 2016, 2017, 2019, 2020, 2021, 2024); library-free row cuts; register v2 | `docs/release/exam/dated_rows.parquet` (DATEDEXAM) | default TALYS | yes (our arms trained on data up to Y) | yes for libraries released ≤ Y (DATED_Y in score.py). **Compare libraries on the `E >= 100 keV` subset**: below it, pointwise library resonances vs binned data cost every library 0.1-0.3 dex (docs/release/dated/DATED.md) |
| `na-pickup` | 920 / 57 | (n,α) isomer, ground-state and total production; registered before read (BLIND_LOOKS 2026-09-22) | `docs/release/exam/na_v1_rows.parquet` | default TALYS | yes | no (only the 55 total rows are scorable from a library file) |
| `na-heprod` | 197 / 52 | He-4 production (n,xα), incl. natural targets | same | default TALYS | yes | no |
| `na-neverread` | 51 / 8 | (n,α) to isomers, targets never read before the recipe froze | same | default TALYS | yes | not scorable from standard files (isomers) |
| `na-post2021` | 116 / 12 | (n,α) total published 2021 or later; nucleus-weighted; an uncovered row counts as a 1 dex miss | `incognita/bench/data/na_fresh.parquet` (NA-FRESH, sha256 0e08a83a…) | JENDL-5 | yes (v2 frozen before the set was read) | yes for JENDL-5 and older; not for 2022+ releases |
| `ch-na`, `ch-n2n`, `ch-np`, `ch-capture` | 1062 / 124, 2334 / 148, 1525 / 65, 5872 / 124 | EXFOR points (binned for (n,2n)/(n,p)), all years, 1 keV-20 MeV | `incognita/bench/data/exam_rows/*.parquet` | TENDL-2025 | **no** (our v5 was fitted to them and is retracted as library-derived; no independent INCOGNITA entry yet) | no |
| `ch-sacs` | 395 / 86 | spectrum-averaged σ (U-235 Watt / Cf-252 Maxwellian), non-suspect | `incognita/bench/data/exam_rows/sacs_rows.parquet` | TENDL-2025 | no | no |

Library values are placed on a row the way our lab did it (`incognita/eval/hydrate.py`): the evaluated file is
reconstructed with NJOY2016 RECONR (0.1 %), sampled lin-lin on a 3000-point log grid (1e-5 eV-20 MeV) and interpolated
log-log at the row energy; SACS folds the grid with `incognita/eval/spectra.py`. (n,α) and He-4 production are derived the
same way for every library (`incognita/bench/alpha.py`, since 2026-11-06): (n,α) = MT 107 (else the sum of MT 800-849)
plus the (n,α) residual that the file puts inside MT 5 (its MF6 / MF9 / MF10 product yields); He-4 = the sum of
multiplicity × σ over every alpha-emitting MT plus the alphas inside MT 5. A row where σ(MT 5) > 0 but the file's MT 5
products could not be read is "comparator incomplete" for that library (not covered) unless σ(MT 5) is below 1 % of the
value; `leaderboard` prints the count. Before, (n,α) was MT 107 alone and He-4 the sum of MT 107, 22, 24, 45, 112, 117,
so a file that lumps alpha emission into MT 5 was scored on a partial channel: ENDF/B-VIII.1 puts 91-96 % of the 14 MeV
(n,α) of Mn-55 and Fe-54/56/57 (and half of V-51's) in MT 5, ENDF/B-VII.1 does it for Mn-55, and JEFF-4.0 has σ(MT 5)
above 1 % of the (n,α) value on Cr, Mn, Fe, Ta and W rows. Known effect: inside resolved-resonance structure a point value is sensitive to the placement
rule (the dated TENDL-Y entry of `capture-retro` gives 0.193 here and 0.184 with the lab's older placement; the difference
sits on a few rows of a few nuclei, mostly 2 Gd-154 rows).

**Corrections of 2026-11-06.** (1) The REACTION code of every ch-n2n / ch-np / ch-na / ch-sacs / ch-capture row was
checked with the rule the light (Z 1-25) rows already follow (`incognita/bench/reaction_check.py`, applied by
`scripts/fix_bench_rows.py`): partial-state products (-G, -M, -L, M1+M2, G+M2, G+M1 where a second long-lived isomer
exists), sums with another target or process, SF9 DERIV / CALC and SF5 PAR rows are no longer scored as total cross
sections. 1,672 rows were dropped (n2n 143, np 68, na 89, sacs 5, capture 1,367), each listed with its flags and code in
`data/exam_rows/reaction_check_dropped.csv`. (2) Four capture-nostructure cells whose only dataset is a sum reaction
(Pd-106 + Pd-108, Te-128 + Te-130; curation review of 2026-11-06) were dropped (`score.CAPTURE_REVIEW_DROP`). (3) The
(n,α) / He-4 comparator above. (4) Capture tracks can be scored with bin averages (`place_tracks.py`, the DATEDEXAM2
rule) instead of point samples. Scores before and after: `docs/release/BENCHMARK.md`.

Known gaps: the capture tracks give one audited value per (nucleus, bin) without the list of contributing EXFOR entries;
the curation that built them (trust weights, rule P) is documented in docs/release but its code is not yet in the repository.
Natural-element targets (A = 0) are not folded over isotopes for library entries (not covered). Isomer rows are scorable
only from a submission CSV.
