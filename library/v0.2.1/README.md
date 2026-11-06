# Incognita v0.2.1 library (preview)

v0.2.1 corrects how library v0.2 averaged its curves over a Maxwellian. Nothing else changes. The engine, the
nuclides, the tiers, the uncertainty bands and the threshold channels are v0.2's. The capture curves are v0.2's too,
except the 21 ANCHORED curves, which are rescaled. What changed is the Maxwellian-averaged cross sections (MACS), the
stellar rates and the REACLIB fits. CHANGELOG.md names the bug and BUILD.md gives the numbers. `sha256sum -c SHA256SUMS`
checks the files.

| file | content |
|---|---|
| `capture_v021.parquet` | σ(n,γ)(E) on a 64-point grid from 1 keV to 20 MeV (lab neutron energy), one row per nuclide, with tier, value source and bands (`unc68_log10`, `unc95_log10`). Same as v0.2 except `macs30_mb` and `alt_macs30_mb`, plus `sigma_b` and `value_source` for the 21 ANCHORED nuclides |
| `macs30_v021.csv`, `macs_kt_v021.csv` | MACS at 30 keV and at kT = 5–100 keV, centre-of-mass definition, with 68 % factors. New in `macs_kt`: `share_below1keV_<kT>keV` |
| `rates_v021.csv`, `reaclib_v021.dat` | N_A⟨σv⟩ on the REACLIB T9 grid and the 7-parameter REACLIB fits (RATES.md) |
| `channels_v021.parquet`, `grid_np_v021.parquet` | (n,p), (n,2n), (n,α): byte-identical copies of the v0.2 files |
| `anchored_rescale_v021.csv` | the 21 ANCHORED nuclides: the v0.2 factor, the extra v0.2.1 factor and the total |
| `VERIFY_V021.json`, `build_summary_v021.json` | the checks (independent recompute, closed forms, file identity) and the v0.2 → v0.2.1 changes |

## The MACS definition used

MACS(kT) = 2/√π · kT⁻² · ∫₀^∞ σ(E_lab) · E · exp(−E/kT) dE

Here E is the centre-of-mass energy and E_lab = E·(A+1)/A. This is the definition used by KADoNiS and by Beer, Voss
and Winters (1992). The rate is N_A⟨σv⟩ = N_A · MACS(kT) · v_T, with v_T = √(2kT/μ) and μ = A/(A+1) u.

Below the grid's first point (E_lab = 1 keV) the cross section is extended as 1/v from that point:
σ(E_lab) = σ(1 keV) · (1 keV / E_lab)^½.
- At kT = 5 keV the extension supplies a median 7.5 % of the MACS (at most 13 %). At 30 keV it supplies 0.7 % (at most
  2.3 %). The column `share_below1keV_<kT>keV` gives it for every nuclide and kT.
- In the rates it supplies about half of N_A⟨σv⟩ at T9 = 0.01 and 17 % at T9 = 0.03. Rates below T9 ≈ 0.05 therefore
  rest mainly on the 1/v assumption (RATES.md).
- v0.2 instead stopped every integral at 1 keV, so its low-kT MACS and low-T rates were too low.

## Tiers, flags, provenance

All as in v0.2 (`library/v0.2/README.md`, `library/v0.2/BUILD.md`).
- The engine is engine-20261022-3. The 18 drip-line nuclides keep their v0.1 values.
- `model_form_flag` and the widened bands are unchanged. `macs30_flag` and `in_validated_range` are unchanged.
- Only Z 26–83 is validated. Where `macs30_flag` is set, prefer a measured MACS.
- The ANCHORED tier is scaled to compiled measured 30 keV MACS values. Those values are not redistributed.
- v0.2.1 was built from the shipped v0.2 files by `scripts/release/build_library_v021.py`, and checked by
  `scripts/release/verify_library_v021.py`. Both are in this repository.
- v0.2 stays unchanged in `library/v0.2`.
