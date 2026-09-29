# Reproducing the README numbers

`bash scripts/reproduce.sh` regenerates each table below from frozen inputs and compares it byte for byte with
`docs/release/expected/<step>/`. It writes `out/reproduce/SUMMARY.md` with one line per table: IDENTICAL, DIFFERS (with
the diff) or SKIPPED (the missing input and the command that fetches it). A single step runs with
`bash scripts/reproduce.sh <step>`. Every exam input is hashed in `docs/release/exam/SHA256SUMS`, and a step refuses to
run if a file changed.

| README section | step | input shipped here | status without external data |
|---|---|---|---|
| Capture on held-out nuclei (DEV rows) | `capblind` | `exam/capture_blind_cells.parquet` | regenerated |
| Capture on held-out nuclei (vault rows), vault interval coverage | `vault` | `exam/vault_rows.parquet` | regenerated |
| Retrodiction | `retro` | `exam/retro_rows.parquet` | regenerated |
| Sealed 674-bin coverage test | `final674` | `uq/final674_rows.parquet` | regenerated |
| Measured-tier coverage after the cutoff | `retromeasured` | `uq/retro_measured_rows.parquet` | regenerated |
| No-structure interval, nuclide counts | `nostruct` | `exam/capture_blind_cells.parquet`, `exam/structure_flags.parquet` | regenerated |
| (n,α) recipe vs default TALYS | `na` | `exam/na_v1_rows.parquet` | regenerated |
| (n,p) correction and its intervals | `np` | `exam/np_fresh_rows.parquet`, `exam/np_interval_rows.parquet` | regenerated |
| Engine vs stock TALYS | `stock` | `exam/stock_rows.parquet` (library columns removed) | regenerated |
| Measure-next ranking | `measure` | `exam/measure_next_inputs.parquet`, `exam/sigma_extrap.json` | regenerated |
| Blind-tier coverage on its own fitting rows (in-sample; not quoted as calibration evidence) | `tiers` | `exam/tier_rows.parquet` | regenerated |
| Interval by chart distance | `interp` | `exam/interp_interval_rows.parquet` | regenerated |
| Release-candidate retrain check | `cleanretrain` | `exam/clean_retrain_rows.parquet` | regenerated |
| Speed report from the recorded timings | `speed` | `incognita/bench/speed/results/` | regenerated (re-timing needs stock TALYS) |
| Registries unchanged since their timestamps; frozen (n,p) model | `verify` | `docs/registry/`, `incognita/terra/data/` | checked (sha256) |
| (n,p) correction on three check targets | `terra`, `npfix` | frozen models | SKIPPED unless `--with-engine` (needs the TALYS structure database) |
| Curation register v2 | `curation` | `data/curation/inputs/` | SKIPPED unless `--download` (EXFOR master file, RIPL-4) |
| Registry scores against the current EXFOR | `registry` | `docs/registry/` | SKIPPED unless `--download`; produces a new report each time |
| Library tier counts | (none) | `library/v0.1/` | `uv run python -m incognita.library summary` |

Exam targets are derived from EXFOR (CC BY 4.0; cite the EXFOR library). Half-lives come from NUBASE2020.

**Exam folds.** `capture_blind_cells.parquet` contains every fold of the held-out exam, including folds 6–7 (the
vault), which were read once for the shipped model. Publishing the file makes them public, so they can no longer serve
as a private confirmation set; future confirmation has to come from the prospective registries or a newly drawn set.

**Not part of v0.1.** Earlier development drafts also reported an evaluation for measured nuclei, ENDF-6 files,
covariances, and criticality and shielding tests. Those products were built on evaluated-library values and were
withdrawn under the project's independence policy; neither they nor their numbers are part of this release.
