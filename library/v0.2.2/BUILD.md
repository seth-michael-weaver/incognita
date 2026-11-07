# v0.2.2 library build (2026-11-07; from library v0.2 and new engine runs below 1 keV)

6168 nuclei, with the same nuclei, tiers, engine, bands and channels as v0.2 (`library/v0.2/BUILD.md`). Above 1 keV the
capture curves are v0.2's, except the 21 ANCHORED curves, which are rescaled. This build adds the engine's own capture
below 1 keV and fixes the reduced mass. It then recomputes the Maxwellian averages, the rates and the REACLIB fits.

- Engine runs: Mac mini, 2026-11-06 18:27 to 11-07 09:41, 3 workers.
- Collect (on the machine with the runs): `scripts/release/collect_below1keV_v022.py`, which writes
  `below1keV_engine_v022.parquet` and `masses_v022.csv`.
- Build: `scripts/release/build_library_v022.py`. It reads the shipped v0.2 files and those two files, and runs in about
  1 min.
- Checks: `scripts/release/verify_library_v022.py`, written to `VERIFY_V022.json`.

## The v0.2.1 issue and the two fixes

1. **1/v below 1 keV (v0.2.1).** v0.2 cut every integral at E_lab = 1 keV. v0.2.1 replaced that cut with a 1/v
   extension from the 1 keV point. The production engine, run below 1 keV, is not 1/v:
   - between 2 eV and 1 keV its capture falls as E^s, with s at a median of −0.71 (5-95 %: −0.93 .. −0.43; range
     −1.00 .. +0.84; 6,113 nuclei);
   - so v0.2.1 was too low below 1 keV for most nuclei, and too high for some.

   **Fix:** the engine's own values from 2 eV to 1 keV, as below.
2. **Reduced mass (v0.2, v0.2.1).** v_T = √(2kT/μ) used μ = A/(A+1) u. The reduced mass of a neutron and a target of
   mass M is μ = m_n·M/(m_n+M), with m_n = 1.00866491590 u.
   - With M = A u the old μ is low by the factor (A+1.00866)/(1.00866·(A+1)).
   - Every v_T, and every rate, was therefore 0.40-0.43 % too high (median 0.430 %).

   **Fix:** μ from AME2020 atomic masses (`masses_v022.csv`). That covers 2,460 measured and 862 estimated (#) masses;
   the other 2,846 nuclides take the mass number A in u, which changes μ by less than 1e-5. The same masses set the
   centre-of-mass energy E = E_lab·M/(M+m_n), where v0.2.1 used A/(A+1). That moves any MACS by less than 0.1 %.

## Engine runs below 1 keV

- **Engine and setup:** engine-20261022-3 = nucleus 16606b356d6e, the engine of v0.2. It used the v0.2 environment,
  deck, runner and inputs (nucleus `research/rl/libv02/code/run.sh` with the FASTGATE worker → prodrun, `fewres off`,
  `pewindow g`; inputs `~/libv02/inputs`).
- **The one change:** the energy grid is the 134-point production grid (1 keV - 20.5 MeV) plus 15 points
  np.geomspace(2, 1000, 16)[:-1] eV, 149 points in all. The coupled-channels cache was a private copy of the production
  cache.
- **Arms and composition:** for each nucleus, the arms v0.2 composed it from, combined with v0.2's rule (the composition
  label is read from v0.2's `value_source`):

  | composition | nuclei |
  |---|---|
  | P | 5,845 (10 of them with the FEW → mean label) |
  | JS(P,A) | 211 (29 FEW → mean) |
  | A(rotor) | 56 |
  | ACTJS A(rotor) | 38 |

  There were 6,361 runs and none failed. 18 nuclides have no production input; they keep their v0.1 values in v0.2.
- **Floor repair:** v0.1's rule, applied to the 15 low points joined to the curve. 8 nuclei had output-floor points
  below 1 keV; they take 1/v instead (see the table below).
- **First pass discarded.** A first pass ran the 16 points 2 eV - 1 keV alone. For 2,323 nuclei its 1 keV value missed
  v0.2's (by more than 10 % for 184). Branch `gridfix` (2bac71aa) found why:
  - The engine's outgoing-energy grid ends at E + S_n + 1 MeV, with E the run's top energy.
  - Where the compound nucleus is unbound to alpha or proton emission, a grid with a low top energy drops the fastest
    alphas and protons, which inflates capture.

  The short-grid values are wrong. Only the wide-grid values are used; the short ones survive only as comparison
  columns. See "Known issue".

**Reproduction of v0.2 above 1 keV**

The same runs give v0.2's 64 points, so every nucleus checks itself.

| result at the 64 points ≥ 1 keV | nuclei |
|---|---|
| all equal to v0.2 within 1e-9 | 5,692 |
| control nuclei (O-16, Fe-56, Ni-62, Nb-94, Mo-86, Sn-116, Cs-135, Eu-151, Dy-164, Ta-181, Au-197, Pb-208, Th-229, U-238; every composition, ANCHORED included) | 14, within ≤ 5e-13 |
| differ by 1e-9 .. 2.1e-8 at a few points (numerical) | 28 |
| differ at the 1 keV point (the next 63 points equal) | 153 |
| differ where v0.2 repaired engine floor points | 275 |
| differ everywhere (Pa-245, Pa-248) | 2 |

**What is used below 1 keV**

σ(E_lab) = σ_v0.2(1 keV)·engine(E_lab)/engine(1 keV). It is log-log interpolated between the 16 points, with 1/v below
2 eV (under 1e-4 of any MACS or rate). ANCHORED curves keep their factor.

| `below1keV_source` | nuclei |
|---|---|
| engine: the run's 1 keV value equals v0.2's within 1e-9, so these are the raw engine values | 5,980 |
| engine, scaled to join the curve: 1 keV value off by 1e-9 .. 1 % (largest 0.94 %) | 133 |
| 1/v from 1 keV (v0.2.1's rule): no production input, v0.1 values | 18 |
| 1/v: the run's 1 keV value is off by more than 1 % (including Pa-245, Pa-248) | 29 |
| 1/v: engine output floor at 8-15 of the 15 points below 1 keV | 8 |

## MACS(kT): v0.2.2 against v0.2.1

Each entry is v0.2.2 / v0.2.1 − 1: the median, the 5-95 % range in brackets, then the full range. "Engine below 1 keV"
counts that change alone, over the 6,113 engine nuclei; "masses" counts the mass change alone. "Share" is the median
part of the MACS that comes from E_lab < 1 keV.

| kT (keV) | v0.2.2 / v0.2.1 − 1 | engine below 1 keV | masses | share (v0.2.2) | share (v0.2.1, 1/v) |
|---|---|---|---|---|---|
| 5 | +1.08 % (−0.24 .. +4.36; −6.3 .. +6.4) | +1.09 % | −0.003 % | 8.6 % (max 17.6 %) | 7.5 % |
| 8 | +0.57 % (−0.10 .. +2.47) | +0.58 % | −0.003 % | 4.7 % | 4.1 % |
| 10 | +0.42 % (−0.07 .. +1.87) | +0.43 % | −0.003 % | 3.6 % | 3.1 % |
| 15 | +0.24 % (−0.03 .. +1.12) | +0.25 % | −0.003 % | 2.1 % | 1.8 % |
| 20 | +0.16 % (−0.02 .. +0.78) | +0.17 % | −0.003 % | 1.4 % | 1.2 % |
| 30 | +0.09 % (−0.01 .. +0.46; −0.4 .. +1.0) | +0.09 % | −0.003 % | 0.8 % (max 3.0 %) | 0.7 % |
| 50 | +0.04 % (−0.01 .. +0.23) | +0.04 % | −0.003 % | 0.4 % | 0.3 % |
| 100 | +0.01 % (−0.01 .. +0.09) | +0.02 % | −0.002 % | 0.1 % | 0.1 % |

## Rates: v0.2.2 against v0.2.1

| T9 | v0.2.2 / v0.2.1 − 1 | engine below 1 keV alone | masses alone | share from E_lab < 1 keV |
|---|---|---|---|---|
| 0.01 | +8.83 % (−3.89 .. +31.0; −44.8 .. +40.0) | +9.43 % | −0.43 % | 55.5 % (max 68 %) |
| 0.015 | +5.43 % (−2.49 .. +19.9) | +5.94 % | −0.43 % | 39.1 % |
| 0.02 | +3.69 % (−1.79 .. +14.3) | +4.21 % | −0.43 % | 29.4 % |
| 0.03 | +2.06 % (−1.14 .. +8.94) | +2.54 % | −0.43 % | 18.9 % |
| 0.05 | +0.86 % (−0.73 .. +4.76) | +1.33 % | −0.43 % | 10.3 % |
| 0.1 | +0.09 % (−0.51 .. +1.81) | +0.53 % | −0.43 % | 4.3 % |
| 0.3 | −0.32 % (−0.44 .. +0.13) | +0.12 % | −0.43 % | 1.0 % |
| 1 | −0.41 % (−0.43 .. −0.32) | +0.02 % | −0.43 % | 0.2 % |
| 3 | −0.43 % (−0.43 .. −0.40) | +0.00 % | −0.43 % | 0.0 % |
| 5 | −0.43 % (−0.43 .. −0.41) | +0.00 % | −0.43 % | 0.0 % |

REACLIB 7-parameter fit, max residual over the grid: median 0.0035 dex, 99th percentile 0.122 dex (v0.2.1: 0.0035 /
0.122).

Examples (v0.2.1 → v0.2.2; rate columns are v0.2.2 / v0.2.1):

| nuclide | MACS 5 keV (mb) | MACS 30 keV (mb) | rate T9 0.01 | T9 0.03 | T9 0.1 |
|---|---|---|---|---|---|
| O-16 | 0.2284 → 0.2324 | 0.05100 → 0.05109 | 1.110 | 1.033 | 1.005 |
| Na-23 | 14.37 → 14.50 | 3.525 → 3.528 | 1.077 | 1.017 | 1.001 |
| Fe-56 | 88.22 → 91.87 | 33.00 → 33.11 | 1.308 | 1.088 | 1.016 |
| Ni-62 | 56.98 → 58.70 | 23.18 → 23.23 | 1.260 | 1.067 | 1.010 |
| Zr-90 | 93.46 → 93.33 | 27.15 → 27.15 | 0.990 | 0.993 | 0.995 |
| Ba-138 | 12.00 → 12.18 | 4.989 → 4.994 | 1.113 | 1.029 | 1.003 |
| Eu-151 | 6783 → 6826 | 2055 → 2056 | 1.048 | 1.010 | 0.999 |
| Dy-164 | 637.3 → 653.3 | 243.5 → 244.0 | 1.218 | 1.056 | 1.007 |
| Au-197 | 2054 → 2115 | 627.7 → 629.5 | 1.204 | 1.059 | 1.011 |
| Pb-208 | 1.090 → 1.099 | 0.4172 → 0.4175 | 1.070 | 1.016 | 1.000 |
| U-238 | 923.8 → 932.9 | 377.4 → 377.6 | 1.104 | 1.021 | 1.000 |
| Cs-135 (ANCHORED) | 604.9 → 619.2 | 160 → 160 | 1.198 | 1.051 | 1.006 |

## ANCHORED: new scale factors

The anchor is the measured 30 keV MACS, which equals the shipped `macs30_mb` in v0.2, v0.2.1 and v0.2.2. One more
factor makes the MACS30 equal it again (to 6e-16), now that the curve includes the engine below 1 keV and the new masses.
The full list is in `anchored_rescale_v022.csv`. The extra factor ranges from 0.9887 (Eu-155) to 1.0006 (Pd-102), so the
curves change by −1.13 % to +0.06 %. Examples:

| nuclide | v0.2 factor | v0.2.2 extra factor | v0.2.2 factor |
|---|---|---|---|
| Fe-60 | 0.817 | 1.00028 | 0.8172 |
| Cs-135 | 1.767 | 0.99206 | 1.7530 |
| Pm-147 | 0.936 | 0.98987 | 0.9265 |
| Eu-155 | 0.973 | 0.98873 | 0.9620 |
| Tl-204 | 1.332 | 0.99125 | 1.3203 |

## `alt_macs30_mb`

As in v0.2.1, the alternative curves are not kept. `alt_macs30_mb` is therefore the v0.2 value times the shipped curve's
own v0.2.2 / v0.2 MACS30 ratio.

## Checks (`VERIFY_V022.json`)

- **Independent recompute** for 12 nuclides (O-16, Na-23, Mg-24, Ca-40, Fe-56, Ni-62, Zr-90, Ba-138, Au-197, Pb-208,
  U-238, Cs-135).
  - Method: a 400,000-point trapezoid over the centre-of-mass energy from 1e-6 eV, with σ looked up at
    E_lab = E(M+m_n)/M on the joined curve, and μ recomputed from the shipped target mass.
  - Every kT, and the rate at T9 = 0.01, 0.03, 0.1, 0.3, 1 and 5, agree to 1.1e-9 or better (limit 1e-6).
- **Closed forms** on the joined 2 eV - 20 MeV grid, through the build's integrator: a 1/v cross section gives
  σ(E_lab = kT(M+m_n)/M), and a constant one gives the incomplete-gamma expression. Both agree to < 1e-9.
- **Reduced mass**
  - Every `reduced_mass_u` equals m_n·M/(m_n+M) (2e-16).
  - For 200 random nuclides the rate equals N_A·MACS·√(2kT/μ) (4e-16).
- **Old rule reproduces v0.2.1.** With v0.2.1's rule (1/v from 1 keV, A/(A+1)), the build reproduces every v0.2.1 MACS
  to 5e-13 and every rate to 4e-15.
- **Below 1 keV**
  - The shipped values are the collected engine values (4e-16).
  - Unscaled, non-ANCHORED, they are the raw engine values (8e-10).
  - The 1/v nuclides follow σ(1 keV)·√(1 keV/E) exactly.
- **Files**
  - The nuclides and tiers are v0.2's.
  - The 6,147 non-ANCHORED curves above 1 keV and all bands are identical to v0.2.
  - The channels and (n,p) grid are byte-identical copies of v0.2's.
  - Every MACS, rate and value below 1 keV is finite and positive, and every share is in [0, 1).
- **Against KADoNiS, MEASURED tier (descriptive).** KADoNiS compiles the same measurements, so this is not a test.

  | kT (keV) | nuclei | v0.2 f_rms (bias) | v0.2.1 | v0.2.2 |
  |---|---|---|---|---|
  | 5 | 194 | x1.629 (−0.024 dex) | x1.651 (+0.014) | x1.660 (+0.022) |
  | 10 | 211 | x1.432 (+0.002 dex) | x1.440 (+0.013) | x1.443 (+0.017) |
  | 30 | 211 | x1.344 (+0.017 dex) | x1.344 (+0.018) | x1.345 (+0.019) |
  | 100 | 211 | x1.403 (+0.012 dex) | x1.401 (+0.011) | x1.402 (+0.011) |

  The correction follows the engine's own curve. It does not move the MACS closer to KADoNiS: the spread at low kT comes
  from resolved resonances, which the smooth curve does not hold (`macs_flag`).

## Known issue: grid-dependent engine values

The engine's value at one energy can depend on the other energies in its run (branch `gridfix`, 2bac71aa; the check is
on branch `talysworld`, `scripts/talysworld/CHECK.md` with `check_points.csv`).

**Cause**

- The outgoing-energy grid ends at E + S_n + 1 MeV, with E the run's highest incident energy.
- When the compound nucleus is unbound to alpha or proton emission (S < 0), a run with a low top energy drops the fastest
  alphas or protons. With pre-equilibrium on, that inflates capture by up to ×62 across 1 keV - 1 MeV (I-109, Pa-200,
  Ra-215, Fr-190, Bi-178, Tl-174, Te-104).
- Grids whose top is ≥ ~5 MeV converge.

**Effect on this library**

- v0.2 and v0.2.2 use the production grid (top 20.5 MeV), so for these nuclei they are right to about 1.5 % at keV
  energies. A second, smaller mechanism, sfactor carry-over, remains.
- Above about 21 MeV + S_min the emission is still cut.
- The values are not changed here. The real fix is the engine's GRIDTOP setting, which the next engine release turns on.
- It is short-grid and one-energy runs that disagree with the library, not the other way round. That is why v0.2.2
  discarded its first, short-grid pass.

**Affected nuclides**

- 2,364 nuclides whose compound nucleus has S_min < −1 MeV: 2,309 via alpha, 55 via proton.
- They are flagged `engine_grid_dependent` in `capture_v022.parquet` and `macs_kt_v022.csv` and listed in
  `grid_dependent_v022.csv`. That file has S_min, the particle, and how far the discarded short-grid run was from v0.2.
- `compound_smin_v022.csv` gives S_min for every nuclide.
- 892 are in Z 26-83. By tier: 2,209 EXTRAPOLATED, 100 INTERPOLATED, 6 ANCHORED (Pm-147, Hf-174, Hf-182, Os-184, Pt-190,
  Hg-196) and 49 MEASURED:
  - Nd-143, Nd-144, Nd-145, Nd-146, Sm-144, Sm-147, Sm-148, Sm-149, Sm-150, Eu-151;
  - Gd-152, Dy-156, Er-162, Er-164, Yb-168, Yb-170, Yb-171, Lu-175, Lu-176;
  - Hf-176, Hf-177, Hf-178, Hf-179, Hf-180, Ta-181, W-180, W-182, W-183, W-184;
  - Re-185, Re-187, Os-186, Os-187, Os-188, Os-189, Os-190, Ir-191, Pt-192, Pt-194;
  - Pb-204, Pb-208, Bi-209, Th-232, Pa-233, U-233, U-234, U-235, U-236, U-238.

## Not changed

The bands (no band is given below 1 keV), the channels, the tiers and flags, and `value_source` (except for ANCHORED).
v0.2 and v0.2.1 stay unchanged in their directories.
