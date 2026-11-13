# docs/release

Evaluation material for the v0.1 preview.

| path | content |
|---|---|
| `exam/`, `uq/` | frozen exam inputs (hashed in `exam/SHA256SUMS`); each file holds EXFOR-derived targets and the predictions being scored, never evaluated-library values |
| `expected/<step>/` | the tables `scripts/reproduce.sh` must regenerate byte for byte |
| `REPRODUCE.md` | which claim comes from which step, and which claims cannot be regenerated here (and why) |
| `INPUTS.md` | external inputs (EXFOR master file, TALYS structure database, optional evaluated libraries for baselines) and how to fetch them |
| `BENCHMARK.md` | the open benchmark: tracks, metric, how to score a model |
| `UQ_EVIDENCE.md` | the evidence behind the uncertainty claims, including where they fail |
| `CURATION_RULE_v2.md`, `CURATION_REGISTER.md` | the library-free EXFOR curation rules and the published register |
| `MEASURE_NEXT.csv`, `MEASURE_NEXT.md` | unmeasured capture targets ranked by current uncertainty |
| `uq/PREREG_FINAL674.md` | the protocol of the 674-bin coverage test (bins, interval rule, pass band), fixed before it was run |
| `amendments/` | scoring-audit records: fixes applied with their before/after numbers, and proposed changes not yet applied |

Some names in these documents are labels of individual tests (for example FINAL-674, the 674-bin coverage test);
"RC" is the release candidate that preceded the shipped model. References to `docs/results/...` point to working
notes that are not part of this preview.
