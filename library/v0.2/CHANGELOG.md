# Library changelog

## v0.2 (2026-10-23)

Same 6,168 nuclides, same files and same tiers as v0.1. What changed is where the numbers come from. BUILD.md has the
details and the checks.

- **Engine.** Every curve now comes from the production engine `engine-20261022-3`, the engine the scoreboard scores
  (release tag `engine-2026-10-22`). v0.1 was built with an older engine.
- **Curves are engine predictions.** In v0.1, MEASURED and INTERPOLATED curves came from a model trained on the
  measurements. In v0.2 every curve is the engine's blind prediction; none is fitted to its own nucleus's data. The one
  per-nucleus use of data is unchanged: ANCHORED curves (21) are scaled by one factor to a measured 30 keV MACS.
  The tier now only describes the data situation of a nucleus, not the method.
- **Learned (n,p) correction dropped.** It was fitted on top of the older engine and does not apply to this one. (n,p),
  (n,2n) and (n,α) come from the same engine runs as capture; `grid_np_v02.parquet` keeps v0.1's 361 (n,p) targets with
  the engine's (n,p) band. The columns `tendl_fitted_other_data`, `outside_training_*`, `e1_constant_*` and `recipe_mb`
  are gone.
- **Bands.** At each energy, the wider of the engine's own band and the nucleus's v0.1 band, so no band is narrower
  than in v0.1. No new band was calibrated.
- **Model-form flags and widened bands.** 1,134 nuclides carry `model_form_flag`: 1,108 `pe_kev` (keV capture depends
  on pre-equilibrium emission at low energies, which this engine includes and TALYS/TENDL start near 1 MeV), 23
  `fists2` (fission-transmission setting, actinides) and 3 `gg_deadend` (Mo-86, Tc-87, Rh-105: the value relies on the
  engine's fix of a missing gamma-decay width; noted, not widened). For `pe_kev` and `fists2` the 68 % and 95 % bands
  below 1 MeV are widened to contain the other choice (median 95 % factor at 30 keV on these nuclides x2.7 -> x4.3,
  largest x7.3e4). All flagged nuclides are EXTRAPOLATED. `alt_value_30keV_b` and `alt_macs30_mb` give the other choice.
- **Large movers.** 318 nuclides moved by more than 10x in their 30 keV MACS against v0.1, almost all far from
  stability; `v01_mover_note` names the cause. On the MEASURED tier the typical change is small (median -0.02 dex).
- **Counts.** 6,168 nuclides: 220 MEASURED, 21 ANCHORED, 316 INTERPOLATED, 5,611 EXTRAPOLATED. 18 drip-line nuclides
  without a production input keep their v0.1 values (`value_source` says so).
- **Reader.** `python -m incognita.library show <nuclide> --version v0.2` (or `capture_curve(..., version="v0.2")`)
  reads this library; without `--version` the reader still reads v0.1.

v0.1 stays unchanged in `library/v0.1`.

## v0.1 (2026-09)

First release. See `library/v0.1/README.md`.
