# Incognita v0.1 library (preview)

Predicted neutron-capture cross sections, Maxwellian averages, reaction rates and three threshold channels for 6,168
nuclides. `sha256sum -c SHA256SUMS` checks the files; `uv run python -m incognita.library summary` prints the counts
below from the files themselves. BUILD.md records the build (tier counts, interval medians, the registered vault read).

| file | content |
|---|---|
| `capture_v01_indep.parquet` | σ(n,γ)(E) on a 64-point grid from 1 keV to 20 MeV, one row per nuclide (array columns), with regime tier, value source and uncertainty components (`unc68_log10`, `unc95_log10`: multiplicative half-widths in log10) |
| `macs30_v01_indep.csv`, `macs_kt_v01_indep.csv` | Maxwellian-averaged cross sections at 30 keV and at kT = 5–100 keV, with 68 % factors |
| `rates_v01_indep.csv`, `reaclib_v01_indep.dat` | stellar reaction rates on the REACLIB T9 grid and their 7-parameter REACLIB fits (RATES.md) |
| `channels_recipe_v01_indep.parquet` | (n,p), (n,2n), (n,α) from the engine's no-data recipe |
| `grid_np_v01_indep.parquet` | (n,p) for 361 targets (Z 26–92) with a learned correction and 68 / 95 % intervals |

## Regime tiers

| tier | meaning |
|---|---|
| MEASURED | the nucleus has capture data; the value is the learned model trained on all EXFOR data |
| ANCHORED | no capture cross-section data, but a measured MACS at 30 keV; the blind curve is scaled to it |
| INTERPOLATED | unmeasured, with structure data, within two neutrons or protons of measured nuclei |
| EXTRAPOLATED | everything else: the engine's no-data recipe (default TALYS-2 physics with this project's E1-width constant) with a calibrated interval |

Only Z 26–83 is covered by the validation described in the top-level README (`in_validated_range`). `macs30_flag` marks
nuclei whose resolved resonances reach into the MACS window; there a measured MACS should be preferred.

## Provenance

- No evaluated-library value (ENDF/B, JENDL, JEFF, TENDL, CENDL, BROND, FENDL, IRDFF, BRUSLIB) enters these files.
- The no-data recipe uses the E1-width constant 1.0425, fitted to EXFOR capture data on the development folds
  (`physics/hf/gamma/e1_width.py`, applied by `scripts/bestfit/engine_curves.py --arm nodata`), in place of TALYS's
  default `globalwtable` value.
- The (n,p) correction in `grid_np_v01_indep.parquet` was frozen on engine curves computed with TALYS's stock E1 table
  and is applied with a per-point E1 factor (`e1_constant_factor`). `tendl_fitted_other_data` is a yes/no flag (whether
  TALYS's own parameter tables carry a fit for the nucleus), not a value.
- Structure inputs of the engine: RIPL (levels, level densities, resonance spacings), AME2020 masses, HFB tables
  distributed through RIPL, the TALYS structure database (downloaded by the user, not redistributed).
- The training and build scripts of this library ran in the development tree and are not part of this distribution;
  the recipe is summarised in the top-level README and the frozen evaluation tables are in `docs/release/`.
- Difference from the frozen build: the columns `anchor_macs30_mb` / `anchor_rel_unc` (compiled measured MACS values used
  as anchors) were removed from `capture_v01_indep.parquet` and `macs30_v01_indep.csv` because the compilation they come
  from states no redistribution licence. All other values are unchanged; the capture file's hash therefore differs from
  the one recorded in `docs/registry/capture-v01-2026-09-24/PROTOCOL.md`. The 21 ANCHORED nuclides are scaled to those
  measured values by construction.
