# Curated EXFOR capture tables

EXFOR-derived (IAEA Nuclear Data Section and the NRDC network), CC BY 4.0. `SHA256SUMS` checks every data file.

A corrected version of these capture tables, capture set v2 (2026-11-06: number format, parser gaps, sums, uncertainty split, SPSDD/DEP duplicates, slips, EXFOR version), is in `../capture_v2/` with its own README and ADOPTION.md. The files here are unchanged.

| file | what |
|---|---|
| `exfor_capture_Z26-92_trust.parquet` | Z 26-92: one row per EXFOR capture dataset, with the WP-12 automatic curation (trust, inflation, decision keep / downweight / exclude / fix-unit and its reason) as run on 2026-09-12 |
| `exfor_cells.parquet` | Z 26-92: one row per dataset and 0.1-dex energy bin, joined to that decision |
| `exfor_capture_Z1-25_trust.parquet` | Z 1-25 (H..Mn): same schema, same curation (added 2026-11-06) |
| `exfor_cells_Z1-25.parquet` | Z 1-25: same schema as `exfor_cells.parquet` |
| `exfor_capture_Z1-25_provenance.json` | inputs (SHA256), gates and decision counts of the Z 1-25 run |
| `review_decisions_Z26-92.jsonl` | review lines for Z 26-92 capture datasets (same format, plus a `rekey` form), applied on top of the 2026-09-12 run by `scripts/apply_review_Z26-92.py` (added 2026-11-06; see below) |
| `review_decisions_Z1-25.jsonl` | review lines for light capture datasets (format of the research repository's `data/curate/review_decisions.jsonl`), applied by the Z 1-25 run |
| `exfor_threshold_Z1-25_rows.parquet` | Z 1-25 measured (n,2n), (n,p), (n,α): one row per EXFOR series and engine energy bin, columns of the benchmark `n2n_rows` / `np_rows` plus `reaction`, `first_author` and `review` (added 2026-11-06; version 1.2 of 2026-11-07, see below) |
| `exfor_threshold_Z1-25_provenance.json` | inputs (SHA256), rule counts and checks of that file |
| `review_decisions_threshold_Z1-25.jsonl` | review lines for those rows (18 lines, 2026-11-07), applied by `scripts/build_light_channels.py` |

## Z 26-92 review lines (2026-11-06)

A check of every REACTION code in the Z 26-92 set found 12 datasets whose code is a sum (`+`) of two reactions. Eleven
are not a single-isotope capture cross section and were still kept (one was already down-weighted to trust 1e-6): Pd-106
+ Pd-108 capture compiled as Pd-106 (22580006), Te-128 + Te-130 compiled as Te-128 (40336092), U-235 capture + fission
compiled as capture (40385003), and eight spectrum-averaged activation sums of a capture and an (n,2n) or (n,n') term
leading to the same product (30268015, 30400038, 30400045-052). They are excluded by `review_decisions_Z26-92.jsonl`
(reason with the EXFOR REACTION code on each line); in no case is the partner term negligible, so none was converted.
The twelfth, Pd-108 30567005 pointer 2, is ground state + isomer of one target, i.e. the total capture; the ingest read
only its first SF block and keyed it as the ground state `G`. It is re-keyed to the total (state `''`, group
`Z046N062M0|102||sig|`), decision and values unchanged. `scripts/apply_review_Z26-92.py` applies the lines (the data stay
in the tables; 12 datasets and 19 cells change). The 2026-09-12 consensus columns are not recomputed. Since these
tables were built, the capture exam files in `docs/release/exam` were frozen from them; none of the 12 datasets'
nuclide-bins changed a frozen exam label here (the exam files are not modified).

## The Z 1-25 extension (2026-11-06)

`scripts/build_light_curation.py` runs the same WP-12 curation code, unchanged, on the 2026-10-14 EXFOR snapshot. It runs
once on Z 1-92 together and keeps the Z 1-25 rows, so the metadata prior and the scatter model are learned as for Z 26-92.
The light rows have the same exclusion and down-weighting rules: upper limits, unconvertible units, EXFOR V-area
compilations and SF9 CALC/EVAL are excluded; offsets over x30 against two or more other datasets are excluded; the EXFOR
outdated flag and low posterior trust down-weight. Differences from the Z 26-92 set:

- No person has reviewed a light decision. All but three are automatic (`reviewer` = `auto:quality_model_v0.2`); the
  three in `review_decisions_Z1-25.jsonl` (reviewer `agent:claude-opus-5.5`, 2026-11-06) were checked against their EXFOR
  entries and excluded, each with a one-line reason: Ne-22 Winters 1988 (13139008, points digitised only on six peaks, so
  a cell mean is a peak value), Ne-22 and Ne-20 Almeida 1983 MACS (21808013, 21808011, superseded by the same group's 2014
  reanalysis of the same measurement, 21808022 / 21808020; 21808013 also does not follow from its pointwise data as
  compiled). The data stay in the tables with decision `exclude`. Checked and left automatic: Be-9 Marin-Lambarri 2020
  (31830002, EXFOR gives 9.7 B for the thermal spectrum average, a x1000 slip against the about 8 mb thermal capture of Be-9; decision
  `fix-unit`, trust 0) is a spectrum-averaged (SPA) value that the website does not plot; Ne-22 Almeida 1983 pointwise
  (21808010) keeps its automatic decision although its 2008 unit correction (MB -> MICRO-B) contradicts the MACS
  derived from it, because which unit is right cannot be decided from the entry. (The Z 26-92 file had one reviewed line in the 2026-09-12 run; 12 more are applied on top, see above.)
- The curation v2 register (`../curation_register_v2.*`, `docs/release/CURATION_RULE_v2.md`) covers Z 26-92 only.
- Z 26-92 stays the 2026-09-12 run. Run again today with the newer snapshot and review file, it would agree on 94 % of
  the Z 26-92 datasets' decisions; the resampling-stability gate fails in that newer run with or without the light data.
- Library v0.2 assigns tiers, and is validated, only from Z 26 (every lighter nuclide is EXTRAPOLATED there) and has no
  capture curve below Z 8. The website therefore shows its own label below Z 26: "measured (Z < 26)" when the nucleus has
  at least one curated capture cell that was kept or down-weighted, otherwise "not measured (Z < 26)". The library files
  are not changed.

## Light (n,2n), (n,p), (n,α) (2026-11-06)

`scripts/build_light_channels.py` stages EXFOR (n,2n), (n,p) and (n,α) for Z 1-25 from the same 2026-10-14 snapshot with
the ingest's own predicates (SF3 = 2N / P / A, SF6 = SIG, 20 MeV clip; the same procedure reproduces the Z 26-92 staging
exactly) and applies the rules of the benchmark rows in `incognita/bench/data/exam_rows` (research
`scripts/channels/score_channels.py --amend`): cross sections only, not EXFOR-outdated, one isotope in its ground state,
no SF5 / SF7 / SF8, no isomer product, no V-entry, points >= 1 mb between max(1 keV, the library resonance-range top) and
20 MeV, one row per series and engine energy bin. On Z 26-92 the same code reproduces every benchmark row with its value.
Light rows also pass the REACTION-code check that later corrected those rules (`score_channels_fixed.reaction_flags`): no
state or level suffix (-L included), no SF9 (DERIV ...), no sums with other reactions or targets (for example natural-
target activation sums `(22-TI-46(N,P)21-SC-46)+(22-TI-47(N,X)21-SC-46)`). Reaction identities stay exact: (n,α) is
SF3 = A only, so Li-6(n,t)He-4 is not in it; He-4 production (n,xα) is not (n,α) either, and the site no longer shows the
benchmark's He-production rows as (n,α) points. These rows are not curated by the WP-12 model (neither are the benchmark
rows). The site shows them next to the library v0.2 channel curves from Z 8; for Z 1-7 the measurements stand alone.

### Version 1.1 of the light threshold rows (2026-11-07)

`scripts/build_light_channels.py` (`--v1` rebuilds 1.0) now corrects the staged series before the rules:

- **Review lines** (`review_decisions_threshold_Z1-25.jsonl`, reviewer `agent:claude-opus-5.5`, reasons quote the EXFOR
  record). Cr-52 and Cr-53(n,p) at 14.8 MeV, Chittenden 1961 (11132004 / 11132005): compiled in B after the 2023 revision
  "published numbers in mb adopted" (82.7 B, 37.3 B) -> `fix-unit` 0.001, now 82.7 and 37.3 mb (rows marked
  `review = "fix-unit x0.001"`). Duplicates, original kept: Ti-47(n,p) Gonzalez 1962 compiled twice (31165002 = 30219002,
  12 points) -> 31165002 excluded; Firkin 1983 (AERE-M-3350, entry 21941) repeats the Swinhoe+Uttley 1979 AERE points
  (entry 20986) -> Ti-48(n,p) 21941005 and Al-27(n,α) 21941006 excluded (their 14.1 MeV Al-27 value is Swinhoe's 122 mb
  monitor), and the three Ti-47(n,p) points of 21941002 at 5.47-9.8 MeV excluded (its 11.8 MeV point is kept).
- **Centre-of-mass energies** (`data/ingest/exfor.py` fix `encm`, E_lab = E_cm (A+1)/A): 6 light series (86 points) give
  their energy as EN-CM (He-3(n,p) Pizzone 2020; Be-7(n,p) / (n,α) Kawabata 2017, Hayakawa 2021, Lamia 2019). They are
  converted, but none of them passes the rules (DERIV / SF5 / SF8), so no row changes.

Rows: 2 881 -> 2 865 (16 rows of excluded series or points removed, 2 rows rescaled); (n,2n) 405, (n,p) 1 374, (n,α)
1 086. The Z 26-92 check against the benchmark rows is unchanged (100 % reproduced). The v1 light capture tables
(`exfor_capture_Z1-25_trust.parquet`, `exfor_cells_Z1-25.parquet`, `build_light_curation.py`) are not rebuilt: none of
their inputs changed; the capture corrections of 2026-11-07 are in capture set v2.1 (`../capture_v2/`).

### Version 1.2 of the light threshold rows (2026-11-07, BUGLIGHT5)

No code change; 12 more review lines (reviewer `agent:claude-opus-5.5`, each reason quotes the EXFOR record):

- **Below the reaction threshold** (the page draws the threshold from `docs/walkthrough/data/q.json`): C-12(n,2n) Ashby
  1958 (11097006, 6 +- 6 mb at 14.1 MeV; threshold 20.28 MeV) and Ca-40(n,2n) Braun 1968 (22611002, 8 mb at 14.69 MeV;
  threshold 16.03 MeV) excluded. C-12 has no (n,2n) row left.
- **One measurement compiled twice** (the later copy excluded): Si-28(n,p) Klochkova 41118005 = 41036002; the 8.5 MeV
  point of Ti-46(n,p) Lu Hanlin 30523004 = 30733004; Ti-46 and Cr-50(n,2n) Pansare 1993 pointer 1 (33001007, 33001006)
  = Dighe/Pansare 1991 (30962002, 30962003).
- **An average shown next to its runs** (EXFOR STATUS DEP, both in the rows; as capture rule D5 the average goes and the
  runs stay): Schantl 1970 O-16 (21846006), F-19 (21846009), K-41 (21846026) (n,p); Al-27(n,p) 40676002; Al-27(n,alpha)
  41051004. For Ca-40(n,p) Schantl the average 21846027 also holds a run that is not in the rows (a ratio to F-19), so
  the average stays and the run 21846055 goes.

Rows: 2 865 -> 2 853; (n,2n) 401, (n,p) 1 367, (n,alpha) 1 085. Z 26-92 check unchanged (100 %).
