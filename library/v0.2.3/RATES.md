# Rates: MACS(kT), stellar rate, REACLIB fit (v0.2.3, 2026-11-07)

v0.2.3 is an errata release: every MACS, rate and REACLIB fit is v0.2.2's, bit for bit. What changed here is the
resonance flag ("Flags" below).

6168 nuclei.
- MACS at kT = 5, 8, 10, 15, 20, 25, 30, 40, 50, 60, 80 and 100 keV.
- Rate on the REACLIB T9 grid (0.01-5.0 GK).
- REACLIB 7-parameter fit. The max residual over the grid has a median of 0.0035 dex and a 99th percentile of 0.122 dex.

Method (v0.2.2's; changed from v0.2.1, see BUILD.md):
- MACS(kT) = 2/sqrt(pi) kT^-2 ∫ σ(E_lab) E exp(−E/kT) dE.
  - E is the centre-of-mass energy, E = E_lab·M/(M+m_n), as KADoNiS defines it.
  - Ground-state target, no stellar enhancement.
- Below E_lab = 1 keV, σ is the production engine's own capture at 15 points from 2 eV to 0.66 keV
  (`sigma_below1keV_b` in `capture_v023.parquet`), with 1/v below 2 eV.
  - For 55 nuclides it is v0.2.1's 1/v extension from 1 keV instead; `below1keV_source` says why.
  - `share_below1keV_<kT>keV` in `macs_kt_v023.csv` is the part of each MACS that comes from E_lab < 1 keV.
- N_A⟨σv⟩ = N_A·MACS(kT)·v_T, with v_T = √(2kT/μ), μ = m_n·M/(m_n+M), m_n = 1.00866 u, and M the AME2020 atomic mass
  (`target_mass_u`, `reduced_mass_u` in `rates_v023.csv`). kT = 86.1733 keV × T9.
- The 68 % factors are v0.2's: the band at E_lab = kT. No band is given below 1 keV.

How much of the rate comes from E_lab < 1 keV (median): 55 % at T9 = 0.01, 19 % at 0.03, 4.3 % at 0.1, 1.0 % at 0.3.
So below T9 ≈ 0.05 the rates rest mainly on the engine's statistical-model curve below 1 keV, which averages over resolved
resonances it does not describe.

Against v0.2.1 (median v0.2.2 / v0.2.1 − 1):

| T9 | change |
|---|---|
| 0.01 | +8.8 % |
| 0.03 | +2.1 % |
| 0.1 | +0.1 % |
| 0.3 | −0.3 % |
| 1 | −0.41 % |
| ≥ 3 | −0.43 % |

The −0.43 % is the reduced-mass fix.

Known issue: for 2,364 nuclides whose compound nucleus is unbound to alpha or proton emission (`engine_grid_dependent`),
the engine's value depends on the top of the run's energy grid. The library's wide-grid values are right to about 1.5 % at
keV energies (BUILD.md, "Known issue").

## Check against KADoNiS's own kT table (MEASURED tier, descriptive)
KADoNiS is a compilation of the same measurements. The curves are blind engine predictions.

| kT (keV) | nuclei | f_rms ours / KADoNiS | median bias (dex) | v0.2.1 f_rms (bias) |
|---|---|---|---|---|
| 5 | 194 | x1.660 | +0.022 | x1.651 (+0.014) |
| 10 | 211 | x1.443 | +0.017 | x1.440 (+0.013) |
| 30 | 211 | x1.345 | +0.019 | x1.344 (+0.018) |
| 100 | 211 | x1.402 | +0.011 | x1.401 (+0.011) |

Most of the gap comes from the resolved-resonance region.

## Flags (changed in v0.2.3)

A MACS at kT integrates σ mostly over E ≲ 10 kT. Where the measured resolved resonances reach above kT/10
(`resolved_upper_ev` > kT/10), the smooth curve stands in for resonances it does not describe there. At kT = 30 keV this
is v0.2's `macs30_flag` (> 3 keV).
- `macs_flag_<kT>keV` (`macs_kt_v023.csv`, True/False): that criterion at each kT, from 0.5 keV at kT = 5 keV to 10 keV
  at kT = 100 keV. Flagged: 879 nuclides at 5 keV, 772 at 8, 727 at 10, 660 at 15, 621 at 20, 567 at 25, 545 at 30,
  523 at 40, 509 at 50, 493 at 60, 453 at 80, 439 at 100.
- `macs_flag`: set where any kT is flagged (879 nuclides); the text names the kT range. In v0.2.2 it repeated the
  30 keV flag at every kT (545), which missed the 334 nuclides with resolved resonances between 0.5 and 3 keV at low kT.
- `rate_flag_below_T9` (`rates_v023.csv`): the rate at T9 below this value is flagged by the same criterion
  (kT = 86.1733 keV × T9). It is set for 1,061 nuclides. Empty means no grid T9 (≥ 0.01) is flagged.
- Where `resolved_upper_ev` is unknown (4,929 of 6,168 nuclides, including 284 of the 449 with Z < 26), an empty flag
  means "unknown", not "clear".

Use a MACS where its `macs_flag_<kT>keV` is False and a rate above its `rate_flag_below_T9`; elsewhere prefer a measured
MACS. Outside Z 26-83 nothing is validated, and inside it `in_validated_range` is a Z cut, not a per-nuclide validation
(README.md).
