# Incognita v0.2.2 library (preview)

v0.2.2 corrects two remaining issues in how library v0.2.1 turned the capture curves into Maxwellian averages (MACS) and
stellar rates. The engine, the nuclides, the tiers, the uncertainty bands, the threshold channels and the capture curves
from 1 keV to 20 MeV are v0.2's (the 21 ANCHORED curves are rescaled again). CHANGELOG.md names the fixes and BUILD.md
gives the numbers. `sha256sum -c SHA256SUMS` checks the files.

1. **Below 1 keV the curve is now the engine's own.** v0.2.1 extended every curve below its first grid point (1 keV) as
   1/v. Run below 1 keV, the production engine falls more steeply than 1/v for most nuclei, so v0.2.1's rates at low
   temperature were mostly too low: at T9 = 0.01 by a median 9 %, and by 31 % at the 95th percentile. v0.2.2 ran the
   production engine on its production grid plus 15 points from 2 eV to 0.66 keV for every nuclide, and uses those values.
2. **Reduced mass.** v0.2.1 (and v0.2) used μ = A/(A+1) u in the rate. The reduced mass is μ = m_n·M/(m_n+M), with
   m_n = 1.00866 u and M the target's mass (AME2020). The old μ was too small, so every rate was 0.40-0.43 % too high.

| file | content |
|---|---|
| `capture_v022.parquet` | σ(n,γ)(E) on a 64-point grid from 1 keV to 20 MeV (lab neutron energy), one row per nuclide, with tier, value source and bands (`unc68_log10`, `unc95_log10`). New: `energy_below1keV_ev`, `sigma_below1keV_b` (15 points, 2 eV to 0.66 keV, no band) and `below1keV_source`. Same as v0.2 above 1 keV except the 21 ANCHORED curves; `macs30_mb` and `alt_macs30_mb` recomputed |
| `macs30_v022.csv`, `macs_kt_v022.csv` | MACS at 30 keV and at kT = 5–100 keV, centre-of-mass definition, with 68 % factors; `share_below1keV_<kT>keV` (the part from E_lab < 1 keV) and `below1keV_source` |
| `rates_v022.csv`, `reaclib_v022.dat` | N_A⟨σv⟩ on the REACLIB T9 grid (with `target_mass_u`, `reduced_mass_u`) and the 7-parameter REACLIB fits (RATES.md) |
| `channels_v022.parquet`, `grid_np_v022.parquet` | (n,p), (n,2n), (n,α): byte-identical copies of the v0.2 files |
| `below1keV_engine_v022.parquet` | the engine runs below 1 keV, per nuclide: composition, grid, status, the 15 engine values (mb, before any ANCHORED scaling), the engine value at 1 keV and its difference from the v0.2 curve |
| `masses_v022.csv` | the target masses used (AME2020 atomic masses, u; the mass number where AME2020 has none) |
| `grid_dependent_v022.csv`, `compound_smin_v022.csv` | the known issue below: the 2,364 flagged nuclides, and the compound nucleus's lowest alpha/proton separation energy S_min for every nuclide |
| `anchored_rescale_v022.csv` | the 21 ANCHORED nuclides: the v0.2 factor, the extra v0.2.2 factor and the total |
| `VERIFY_V022.json`, `build_summary_v022.json` | the checks and the v0.2.1 → v0.2.2 changes |

## The MACS and rate used

MACS(kT) = 2/√π · kT⁻² · ∫₀^∞ σ(E_lab) · E · exp(−E/kT) dE

E is the centre-of-mass energy, E = E_lab · M/(M + m_n) (KADoNiS; Beer, Voss and Winters 1992). σ is log-log
interpolated between the points of the curve: the 15 engine points below 1 keV and the 64-point grid above. Below 2 eV it
is extended as 1/v, which is below 1e-4 of any MACS or rate in the files. The rate is N_A⟨σv⟩ = N_A · MACS(kT) · v_T,
v_T = √(2kT/μ), μ = m_n·M/(m_n+M).

Where the engine gave no usable values below 1 keV (`below1keV_source` says why), the curve below 1 keV is v0.2.1's 1/v
extension from 1 keV.

## Known issue: grid-dependent engine values

For 2,364 nuclides (`engine_grid_dependent`), the compound nucleus is unbound to alpha or proton emission by more than
1 MeV. For these, the engine's value at one energy depends on the other energies in its run.
- The engine's outgoing-energy grid ends at E + S_n + 1 MeV. A run whose top energy is low drops the fastest alphas or
  protons, and that can inflate capture by up to ×62.
- This library comes from the wide production grid (top 20.5 MeV), so its values for these nuclides are right to about
  1.5 % at keV energies. Above about 21 MeV + S_min the emission is still cut.
- The values are not changed here. The fix is the engine's GRIDTOP setting, in the next engine release.
- Details, and the 49 MEASURED nuclides among them, are in BUILD.md. The cause was found on branch `gridfix`
  (2bac71aa); the check is `scripts/talysworld/CHECK.md` on branch `talysworld`.

## Tiers, flags, provenance

All as in v0.2 (`library/v0.2/README.md`, `library/v0.2/BUILD.md`).
- The engine is engine-20261022-3 (nucleus 16606b356d6e). The 18 drip-line nuclides keep their v0.1 values above 1 keV
  and 1/v below it.
- `model_form_flag` and the widened bands are unchanged. `macs30_flag` and `in_validated_range` are unchanged.
- Only Z 26–83 is validated. Where `macs30_flag` is set, prefer a measured MACS. Below 1 keV the smooth curve is an
  average over resolved resonances, as it is above.
- The ANCHORED tier is scaled to compiled measured 30 keV MACS values. Those values are not redistributed.
- Built from the shipped v0.2 files and the engine runs below 1 keV by `scripts/release/collect_below1keV_v022.py` and
  `scripts/release/build_library_v022.py`, checked by `scripts/release/verify_library_v022.py`.
- v0.2 and v0.2.1 stay unchanged in `library/v0.2` and `library/v0.2.1`.
