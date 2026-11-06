# Curated EXFOR capture tables

EXFOR-derived (IAEA Nuclear Data Section and the NRDC network), CC BY 4.0. `SHA256SUMS` checks every data file.

| file | what |
|---|---|
| `exfor_capture_Z26-92_trust.parquet` | Z 26-92: one row per EXFOR capture dataset, with the WP-12 automatic curation (trust, inflation, decision keep / downweight / exclude / fix-unit and its reason) as run on 2026-09-12 |
| `exfor_cells.parquet` | Z 26-92: one row per dataset and 0.1-dex energy bin, joined to that decision |
| `exfor_capture_Z1-25_trust.parquet` | Z 1-25 (H..Mn): same schema, same curation (added 2026-11-06) |
| `exfor_cells_Z1-25.parquet` | Z 1-25: same schema as `exfor_cells.parquet` |
| `exfor_capture_Z1-25_provenance.json` | inputs (SHA256), gates and decision counts of the Z 1-25 run |

## The Z 1-25 extension (2026-11-06)

`scripts/build_light_curation.py` runs the same WP-12 curation code, unchanged, on the 2026-10-14 EXFOR snapshot. It runs
once on Z 1-92 together and keeps the Z 1-25 rows, so the metadata prior and the scatter model are learned as for Z 26-92.
The light rows have the same exclusion and down-weighting rules: upper limits, unconvertible units, EXFOR V-area
compilations and SF9 CALC/EVAL are excluded; offsets over x30 against two or more other datasets are excluded; the EXFOR
outdated flag and low posterior trust down-weight. Differences from the Z 26-92 set:

- No person has reviewed a light decision: they are all automatic (`reviewer` = `auto:quality_model_v0.2`). (The Z 26-92
  file has one reviewed line.)
- The curation v2 register (`../curation_register_v2.*`, `docs/release/CURATION_RULE_v2.md`) covers Z 26-92 only.
- Z 26-92 stays the 2026-09-12 run. Run again today with the newer snapshot and review file, it would agree on 94 % of
  the Z 26-92 datasets' decisions; the resampling-stability gate fails in that newer run with or without the light data.
- Library v0.2 assigns tiers, and is validated, only from Z 26 (every lighter nuclide is EXTRAPOLATED there) and has no
  capture curve below Z 8. The website therefore shows its own label below Z 26: "measured (Z < 26)" when the nucleus has
  at least one curated capture cell that was kept or down-weighted, otherwise "not measured (Z < 26)". The library files
  are not changed. (n,2n), (n,p) and (n,α) points on the site still come only from the benchmark rows (Z 24-92).
