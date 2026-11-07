# Rates: MACS(kT), stellar rate, REACLIB fit (v0.2.2, 2026-11-07)

6168 nuclei.
- MACS at kT = 5, 8, 10, 15, 20, 25, 30, 40, 50, 60, 80 and 100 keV.
- Rate on the REACLIB T9 grid (0.01-5.0 GK).
- REACLIB 7-parameter fit. The max residual over the grid has a median of 0.0035 dex and a 99th percentile of 0.122 dex.

Method (changed from v0.2.1, see BUILD.md):
- MACS(kT) = 2/sqrt(pi) kT^-2 ∫ σ(E_lab) E exp(−E/kT) dE.
  - E is the centre-of-mass energy, E = E_lab·M/(M+m_n), as KADoNiS defines it.
  - Ground-state target, no stellar enhancement.
- Below E_lab = 1 keV, σ is the production engine's own capture at 15 points from 2 eV to 0.66 keV
  (`sigma_below1keV_b` in `capture_v022.parquet`), with 1/v below 2 eV.
  - For 55 nuclides it is v0.2.1's 1/v extension from 1 keV instead; `below1keV_source` says why.
  - `share_below1keV_<kT>keV` in `macs_kt_v022.csv` is the part of each MACS that comes from E_lab < 1 keV.
- N_A⟨σv⟩ = N_A·MACS(kT)·v_T, with v_T = √(2kT/μ), μ = m_n·M/(m_n+M), m_n = 1.00866 u, and M the AME2020 atomic mass
  (`target_mass_u`, `reduced_mass_u` in `rates_v022.csv`). kT = 86.1733 keV × T9.
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

Most of the gap comes from the resolved-resonance region. Use the rate products where `macs_flag` is empty; elsewhere,
prefer a measured MACS. Nothing outside Z 26-83 is validated.
