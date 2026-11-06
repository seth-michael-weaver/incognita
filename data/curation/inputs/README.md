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
| `review_decisions_Z1-25.jsonl` | review lines for light capture datasets (format of the research repository's `data/curate/review_decisions.jsonl`), applied by the Z 1-25 run |
| `exfor_threshold_Z1-25_rows.parquet` | Z 1-25 measured (n,2n), (n,p), (n,α): one row per EXFOR series and engine energy bin, columns of the benchmark `n2n_rows` / `np_rows` plus `reaction` and `first_author` (added 2026-11-06) |
| `exfor_threshold_Z1-25_provenance.json` | inputs (SHA256), rule counts and checks of that file |

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
  derived from it, because which unit is right cannot be decided from the entry. (The Z 26-92 file has one reviewed line.)
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
