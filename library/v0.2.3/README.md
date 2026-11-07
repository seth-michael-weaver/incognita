# Incognita v0.2.3 library (preview)

v0.2.3 is a corrections-only errata release of library v0.2.2. **No cross section, band, MACS, rate or REACLIB fit
changes**: every number is v0.2.2's, bit for bit. What changes is bookkeeping, two flag columns and the documentation
(items A, B, D and F of `docs/release/amendments/BUGTIER3.md`). CHANGELOG.md lists the fixes, BUILD.md gives the
numbers, and `sha256sum -c SHA256SUMS` checks the files.

1. **ANCHORED factors (A).** v0.2.2 listed the 21 ANCHORED scale factors from a v0.2 factor rounded to 3 decimals.
   The curves carried the exact factor. `anchored_rescale_v023.csv` now lists the exact factors. The `value_source`
   text "blind curve x f" now rounds the true factor, and capture and `macs30_v023.csv` say the same thing.
2. **Model-form columns (B).** `model_form_max_dex_sub1MeV` was 0.0 for the 3 `gg_deadend` nuclides, whose alternative
   differs by 1.1-3.6 dex. It is now that difference. `alt_value_30keV_b` is the alternative at the grid point nearest
   30 keV (31.8 keV), and its description now says so.
3. **Per-kT MACS flag (F).** `macs_flag` in `macs_kt_v022.csv` used the 30 keV criterion at every kT. v0.2.3 flags
   each kT by its own criterion, so 334 more nuclides are flagged at low kT. A new rate column says below which T9 a
   rate is flagged.
4. **Definitions (D).** The tier and validated-range definitions below now state the full rule.

## What changed against v0.2.2 (changed cells, per file)

| file | changed fields (rows) |
|---|---|
| `capture_v023.parquet` | `value_source` (5 ANCHORED rows: Fe-60, Se-76, Te-120, Ba-132, Hf-182), `model_form_max_dex_sub1MeV` (3: Mo-86, Tc-87, Rh-105). All other columns of all 6,168 rows equal v0.2.2's |
| `macs30_v023.csv` | `value_source` (21 ANCHORED rows: v0.2.2 still carried v0.2's text and factor here; it now equals the capture file's) |
| `anchored_rescale_v023.csv` | `v02_factor`, `v022_factor` (21 rows, full precision) |
| `macs_kt_v023.csv` | `macs_flag` (879 rows: 545 reworded, 334 newly set); new columns `macs_flag_5keV` ... `macs_flag_100keV` |
| `rates_v023.csv` | new column `rate_flag_below_T9` (set for 1,061 nuclides); every rate unchanged |
| `channels_v023.parquet`, `grid_np_v023.parquet`, `reaclib_v023.dat`, `below1keV_engine_v023.parquet`, `masses_v023.csv`, `compound_smin_v023.csv`, `grid_dependent_v023.csv` | none: byte-identical copies of the v0.2.2 files (the REACLIB comments still say `v022`) |
| `README.md`, `CHANGELOG.md`, `BUILD.md`, `RATES.md`, `VERIFY_V023.json`, `build_summary_v023.json`, `SHA256SUMS` | new for v0.2.3 |

`VERIFY_V023.json` compares every column of every file with v0.2.2.

## Files

| file | content |
|---|---|
| `capture_v023.parquet` | σ(n,γ)(E) on a 64-point grid from 1 keV to 20 MeV (lab neutron energy), one row per nuclide, with tier, value source and bands (`unc68_log10`, `unc95_log10`). Below 1 keV: `energy_below1keV_ev`, `sigma_below1keV_b` (15 points, 2 eV to 0.66 keV, no band) and `below1keV_source` |
| `macs30_v023.csv`, `macs_kt_v023.csv` | MACS at 30 keV and at kT = 5–100 keV, centre-of-mass definition, with 68 % factors, `share_below1keV_<kT>keV`, `below1keV_source` and the MACS flags (below) |
| `rates_v023.csv`, `reaclib_v023.dat` | N_A⟨σv⟩ on the REACLIB T9 grid (with `target_mass_u`, `reduced_mass_u`, `rate_flag_below_T9`) and the 7-parameter REACLIB fits (RATES.md) |
| `channels_v023.parquet`, `grid_np_v023.parquet` | (n,p), (n,2n), (n,α): byte-identical copies of the v0.2 files |
| `below1keV_engine_v023.parquet` | the engine runs below 1 keV, per nuclide (v0.2.2's) |
| `masses_v023.csv` | the target masses used (AME2020 atomic masses, u; the mass number where AME2020 has none) |
| `grid_dependent_v023.csv`, `compound_smin_v023.csv` | the grid-dependence known issue: the 2,364 flagged nuclides, and S_min for every nuclide |
| `anchored_rescale_v023.csv` | the 21 ANCHORED nuclides: the v0.2 factor, the extra v0.2.2 factor and the total, at full precision |
| `VERIFY_V023.json`, `build_summary_v023.json` | the checks and the v0.2.2 → v0.2.3 changes |

Columns that this release corrects or adds:
- `alt_value_30keV_b` (`model_form_flag` set): the alternative engine choice's capture cross section at the grid point
  nearest 30 keV, E_lab = 31.8 keV, in b. Compare it with `sigma_b` at that grid point, not with the curve interpolated
  to 30 keV. `alt_macs30_mb` is the alternative's MACS at kT = 30 keV.
- `model_form_max_dex_sub1MeV`: the largest |log10(alternative / curve)| below 1 MeV. For `pe_kev` and `fists2` it is
  taken over the full alternative curve. For `gg_deadend` (Mo-86 3.59, Tc-87 1.11, Rh-105 2.43) only the 31.8 keV value
  of the alternative is kept, so it is the difference there: a lower bound. Their bands stay unwidened (the
  alternative is a known defect, not a model choice).
- `macs30_flag` (capture, macs30): resolved resonances above 3 keV (`resolved_upper_ev` > kT/10 at kT = 30 keV).
  Unchanged.
- `macs_flag_<kT>keV` (macs_kt, True/False): `resolved_upper_ev` > kT/10. That is the 30 keV criterion scaled to each
  kT: 0.5 keV at kT = 5 keV, 10 keV at kT = 100 keV. Flagged nuclides per kT: 879 at 5 keV, 727 at 10, 545 at 30, 439 at
  100 (BUILD.md).
- `macs_flag` (macs_kt): set where any `macs_flag_<kT>keV` is True (879 nuclides). Its text names the kT range. v0.2.2
  set it where `macs30_flag` was set (545), at every kT.
- `rate_flag_below_T9` (rates): the rate at T9 below this value integrates the resolved range (kT/10 <
  `resolved_upper_ev`, kT = 86.1733 keV × T9). Empty where no grid T9 (≥ 0.01) is flagged.
- **An empty flag is not a clear flag** where `resolved_upper_ev` is unknown: it is known for 1,239 of 6,168 nuclides
  (165 of the 449 with Z < 26).

## The MACS and rate used

Unchanged from v0.2.2:

MACS(kT) = 2/√π · kT⁻² · ∫₀^∞ σ(E_lab) · E · exp(−E/kT) dE

E is the centre-of-mass energy, E = E_lab · M/(M + m_n) (KADoNiS; Beer, Voss and Winters 1992). σ is log-log
interpolated between the points of the curve: the 15 engine points below 1 keV and the 64-point grid above. Below 2 eV it
is extended as 1/v, which is below 1e-4 of any MACS or rate in the files. The rate is N_A⟨σv⟩ = N_A · MACS(kT) · v_T,
v_T = √(2kT/μ), μ = m_n·M/(m_n+M). Where the engine gave no usable values below 1 keV (`below1keV_source` says why),
the curve below 1 keV is v0.2.1's 1/v extension from 1 keV.

## Tiers and the validated range

The tiers are v0.1's, as in v0.2 and v0.2.2. They describe the data situation of a nucleus. Every curve is the engine's
blind prediction, except that ANCHORED curves are scaled by one factor.

| tier | rule (as the files show it) |
|---|---|
| MEASURED | the nucleus has capture data in v0.1's measured set (220) |
| ANCHORED | no capture cross-section data in that set, but a measured 30 keV MACS; the curve is scaled by one factor to it (21) |
| INTERPOLATED | unmeasured, with structure data, Z 26–83, at most \|ΔZ\| + \|ΔN\| = 2 from a MEASURED nucleus, and not on the "rich side" of it (v0.1 build rule) (316) |
| EXTRAPOLATED | everything else (5,611) |

- The INTERPOLATED distance is |ΔZ| + |ΔN| to the nearest MEASURED nucleus (`chart_distance`). 58 INTERPOLATED
  nuclides have a measured neighbour only diagonally (one proton and one neutron away).
- The Z 26–83 condition: below Z 26 and above Z 83 every unmeasured nucleus is EXTRAPOLATED.
- The "rich side" exclusion: v0.1's build left 256 nuclides of its chart run EXTRAPOLATED for being on the rich side
  of their measured neighbours (`library/v0.1/BUILD.md`). The exact v0.1 threshold is not documented.
- So 205 EXTRAPOLATED nuclides in Z 26–83 with structure data lie within |ΔZ| + |ΔN| ≤ 2 of a MEASURED nucleus.
  171 of them are at least as neutron-rich (N − Z) as every measured neighbour within that distance.

**Validated range.** `in_validated_range` marks Z 26–83, the proton range the validation covered. It is a Z cut only
and does not say that a nuclide's value was validated. Of the 3,707 nuclides it marks:
- 2,451 have no structure data;
- 195 moved by more than 1 dex since v0.1 (`v01_mover_note`);
- 576 are model-form flagged (`model_form_flag`);
- 892 are `engine_grid_dependent`.

Far from stability, read those columns before the value. Outside Z 26–83 nothing is validated.

## Known issues (not changed in v0.2.3)

- **Tiers against the curated capture set (BUGTIER3 item C).** 57 INTERPOLATED or EXTRAPOLATED nuclides with Z ≥ 26
  have kept keV capture cross sections or measured MACS in the curated capture set (v1 and v2 agree). Zn-70, Ge-76 and
  Te-120 are ANCHORED with kept keV cross sections. By the tier definition they would be MEASURED. Reclassifying them
  (up to 60 nuclides) would change their tier and the bands that take a tier interval. That is a separate decision and
  not part of this errata. The website's Data explorer already shows such nuclides as measured.
- **TERRA coverage cells (BUGTIER3 item E).** On the Scoreboard, 4 TERRA coverage cells are N/A by a "<5 nuclei" label
  while `n_nuclei` is 5 or 6. Whether they should be scored needs the TERRA ledger. It does not touch this library.
- **Grid-dependent engine values** (as in v0.2.2). For 2,364 nuclides (`engine_grid_dependent`), the compound nucleus is
  unbound to alpha or proton emission by more than 1 MeV, and the engine's value at one energy depends on the other
  energies in its run. The library comes from the wide production grid, so its values for these nuclides are right to
  about 1.5 % at keV energies. Above about 21 MeV + S_min the emission is still cut. The fix is the engine's GRIDTOP
  setting, in the next engine release (BUILD.md).
- **Resolved resonances.** The curve below and above 1 keV is a smooth average over resolved resonances. Where a MACS
  flag is set, prefer a measured MACS. Below T9 ≈ 0.05 every rate rests mainly on the curve below 1 keV (RATES.md).

## Provenance

- The engine is engine-20261022-3 (nucleus 16606b356d6e). The 18 drip-line nuclides keep their v0.1 values above 1 keV
  and 1/v below it.
- `model_form_flag`, the widened bands and `in_validated_range` are unchanged.
- The ANCHORED tier is scaled to compiled measured 30 keV MACS values. Those values are not redistributed.
- Built from the shipped v0.2.2 files by `scripts/release/build_library_v023.py`, checked by
  `scripts/release/verify_library_v023.py`. v0.2.2 itself was built by `scripts/release/build_library_v022.py`.
- v0.2, v0.2.1 and v0.2.2 stay unchanged in `library/v0.2`, `library/v0.2.1` and `library/v0.2.2`.
- Reader: `python -m incognita.library show <nuclide> --version v0.2.3`.
