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
| `uq/PREREG_FINAL674.md` | the pre-registration of the sealed coverage test |

These documents were written during development and keep its vocabulary: upper-case names (SHIPEXAMS, FINAL-674,
INDEP_FIX, ...) are internal test and work-package names, "RC" is the release candidate that preceded the shipped
model, and references to `BLIND_LOOKS.md`, `docs/results/...` or the development tree point to the project's internal
log of registered reads and working notes, which are not part of this preview.
