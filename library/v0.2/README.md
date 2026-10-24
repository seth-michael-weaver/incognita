# Incognita v0.2 library (preview)

Predicted neutron-capture cross sections, Maxwellian averages, reaction rates and three threshold channels for 6,168
nuclides, computed with the production engine **engine-20261022-3** (the engine the scoreboard scores). `sha256sum -c
SHA256SUMS` checks the files. BUILD.md records the build: what changed against v0.1, the checks, and the known limits.

| file | content |
|---|---|
| `capture_v02.parquet` | σ(n,γ)(E) on a 64-point grid from 1 keV to 20 MeV, one row per nuclide (array columns), with regime tier, value source and uncertainty (`unc68_log10`, `unc95_log10`: multiplicative half-widths in log10) |
| `macs30_v02.csv`, `macs_kt_v02.csv` | Maxwellian-averaged cross sections at 30 keV and at kT = 5–100 keV, with 68 % factors |
| `rates_v02.csv`, `reaclib_v02.dat` | stellar reaction rates on the REACLIB T9 grid and their 7-parameter REACLIB fits (RATES.md) |
| `channels_v02.parquet` | (n,p), (n,2n), (n,α) from the production engine, same grid |
| `grid_np_v02.parquet` | (n,p) for the same 361 targets as v0.1, at 1–20 MeV, with 68 / 95 % bands |
| `VERIFY_V02.json` | the build's checks and the per-tier comparison with v0.1 |

## Regime tiers

The tier of every nuclide is the same as in v0.1. It describes the data situation of the nucleus. In v0.2 it no longer
decides where the number comes from: every curve is the production engine's blind prediction.

| tier | meaning in v0.2 |
|---|---|
| MEASURED | the nucleus has capture data. The curve is still the engine's blind prediction: it was not fitted to this nucleus's data (v0.1's MEASURED curves were). The engine's global parameters were set on data from many nuclei, these included, so agreement is a check of the global model, not an independent test |
| ANCHORED | no capture cross-section data, but a measured MACS at 30 keV; the engine curve is scaled by one factor to it |
| INTERPOLATED | unmeasured, with structure data, within two neutrons or protons of measured nuclei |
| EXTRAPOLATED | everything else |

`v01_mover_note` is set on the 318 nuclides whose 30 keV MACS moved by more than 10x since v0.1, with the
engine setting that causes the move (BUILD.md, "Why the large movers move"); treat those values as very uncertain.

`model_form_flag` marks 1,131 nuclides where one engine setting changes keV capture by more than a factor 2:
1,108 by pre-equilibrium emission at keV energies (production runs it at every energy; TALYS and TENDL start it near
1 MeV) and 23 actinides by fission transmission. There, `alt_value_30keV_b` and `alt_macs30_mb` give the other choice,
and the bands below 1 MeV are widened to contain it. No measurement can decide between the two. See BUILD.md,
"Model-form uncertainty far from stability".

Only Z 26–83 is covered by the validation described in the top-level README (`in_validated_range`). `macs30_flag` marks
nuclei whose resolved resonances reach into the MACS window; there a measured MACS should be preferred.

## Provenance

- Central values: the INCOGNITA production engine engine-20261022-3 (nucleus commit 16606b356), with its production deck
  and inputs. For the 250 nuclei of the engine's reference set the values are the reference product itself; the other
  nuclei were run the same way. 18 nuclei close to the drip lines have no production input file; they keep their v0.1
  value, and `value_source` says so.
- No evaluated-library value (ENDF/B, JENDL, JEFF, TENDL, CENDL, BROND, FENDL, IRDFF, BRUSLIB) enters these files. No
  nucleus has its own measured cross sections fitted. The engine's parameters are global: one rule for every nucleus.
  The one per-nucleus use of data is the 21 measured 30 keV MACS anchors of the ANCHORED tier.
- Uncertainty: at each energy, the larger of the engine's own band (UNCCAL v2, the spread of the production engine
  against held-out measurements) and the v0.1 interval of that nucleus. For capture the engine band is labelled not
  calibrated (it over-covers), so the bands are on the wide side.
- Coverage caveat: a later pre-registered coverage check of the engine bands (2026-10-24) found that the threshold
  channels ((n,p), (n,α), (n,2n)) and the total under-cover, while capture, fission and elastic cover as stated. Treat
  the 68 / 95 % bands of the threshold channels as possibly too narrow.
- The ANCHORED tier is scaled to compiled measured MACS values; those values are not redistributed (as in v0.1).
- Structure inputs of the engine: RIPL (levels, level densities, resonance spacings), AME2020 masses, HFB tables
  distributed through RIPL, the TALYS structure database (downloaded by the user, not redistributed).
- The build scripts ran in the development tree and are not part of this distribution.
- v0.1 (`library/v0.1`) stays in the repository unchanged.
