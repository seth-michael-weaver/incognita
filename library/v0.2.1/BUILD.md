# v0.2.1 library build (2026-11-06; from library v0.2)

6168 nuclei, the same nuclei, tiers, engine, bands and channels as v0.2 (`library/v0.2/BUILD.md`). This build
recomputes the Maxwellian averages, the rates and the REACLIB fits. It also rescales the 21 ANCHORED curves.

- Build: `scripts/release/build_library_v021.py`. It reads only the shipped v0.2 files and runs in about 30 s on a laptop.
- Checks: `scripts/release/verify_library_v021.py`, written to `VERIFY_V021.json`.

## The two errors in v0.2

1. **Lab frame.** v0.2 integrated σ(E)·E·exp(−E/kT) over the laboratory neutron energy. The MACS is defined over the
   centre-of-mass energy E, with σ taken at E_lab = E·(A+1)/A.
   - For a cross section falling as E^−α, the lab formula is too high by (1+1/A)^α: √(1+1/A) for 1/v.
   - For a rising cross section it is too low.
   - Code: nucleus `research/rl/libv02/code/build.py:33-35` (MACS30 and the ANCHORED scaling), `mform.py:25-27`
     (`alt_macs30_mb`), and nuc-local `scripts/release/make_rates.py` (`macs_kt`, rates and REACLIB fits). All three are
     the same lab-energy integral.
2. **Cut at 1 keV.** Every integral started at the grid's first point, E_lab = 1 keV, so the part below 1 keV was
   dropped.
   - This is small at 30 keV (0.7 % median) and large at low kT: 7.5 % median at 5 keV.
   - In the rates it is about half of the value at T9 = 0.01.
   - v0.2.1 extends σ below 1 keV as 1/v from the first grid point. We extended rather than flagged because a zero
     cross section below 1 keV is certainly wrong. A 1/v average is the usual s-wave form, and the size of the
     extension is published per nuclide (`share_below1keV_<kT>keV`).

The integral is exact for the piecewise power-law curve: 48-point Gauss-Legendre per grid interval in ln E, plus a closed
form for the 1/v part. With the v0.2 formula, the same script reproduces v0.2's `macs_kt` to 7e-13.

## MACS at 30 keV: v0.2 against v0.2.1, by mass number

Each entry is v0.2 / v0.2.1 − 1, with the ANCHORED nuclides left out. "Frame alone" compares v0.2 with a
centre-of-mass integral that is still cut at 1 keV. It isolates error 1.

| A | nuclei | √(1+1/A) − 1, median | frame alone, range | frame alone, median | v0.2 / v0.2.1 (both errors), median | range |
|---|---|---|---|---|---|---|
| 1-19 | 25 | +2.90 % | +1.33 .. +5.15 % | **+3.05 %** | +2.64 % | +0.97 .. +4.49 % |
| 20-39 | 172 | +1.60 % | −2.79 .. +4.17 % | **+1.66 %** | +0.75 % | −3.43 .. +3.21 % |
| 40-79 | 548 | +0.82 % | −7.29 .. +2.23 % | **+1.03 %** | +0.15 % | −7.30 .. +1.01 % |
| 80-149 | 1463 | +0.43 % | −5.89 .. +1.17 % | **+0.46 %** | −0.21 % | −5.90 .. +0.54 % |
| 150-299 | 3610 | +0.23 % | −1.98 .. +0.63 % | **+0.24 %** | −0.40 % | −2.23 .. +0.40 % |

Examples (MACS30, mb, v0.2 → v0.2.1):

| nuclide | v0.2 | v0.2.1 |
|---|---|---|
| O-16 | 0.05291 | 0.05100 |
| Na-23 | 3.609 | 3.525 |
| Mg-24 | 3.814 | 3.741 |
| Ca-40 | 6.778 | 6.739 |
| Fe-56 | 32.99 | 33.00 |
| Ni-62 | 23.21 | 23.18 |
| Zr-90 | 27.14 | 27.15 |
| Ba-138 | 4.971 | 4.989 |
| Au-197 | 623.2 | 627.7 |
| Pb-208 | 0.4153 | 0.4172 |
| U-238 | 376.6 | 377.4 |

The two errors partly cancel. Light nuclei come out lower in v0.2.1, by up to 4.5 %. Heavy nuclei come out slightly
higher: 1/v extension > frame correction.

## MACS(kT), all nuclides

| kT (keV) | frame alone, median | v0.2 / v0.2.1 − 1, median | 5-95 % | share from E_lab < 1 keV (1/v), median |
|---|---|---|---|---|
| 5 | +0.28 % | −7.17 % | −10.4 .. −3.5 % | 7.5 % (max 13.0 %) |
| 8 | +0.29 % | −3.70 % | −6.0 .. −1.4 % | 4.1 % (max 7.9 %) |
| 10 | +0.30 % | −2.63 % | −4.6 .. −0.8 % | 3.1 % (max 6.3 %) |
| 15 | +0.30 % | −1.33 % | −2.7 .. −0.3 % | 1.8 % (max 4.2 %) |
| 20 | +0.29 % | −0.76 % | −1.8 .. −0.0 % | 1.2 % (max 3.3 %) |
| 25 | +0.29 % | −0.46 % | −1.3 .. +0.2 % | 0.9 % (max 2.7 %) |
| 30 | +0.28 % | −0.29 % | −1.0 .. +0.4 % | 0.7 % (max 2.3 %) |
| 40 | +0.27 % | −0.12 % | −0.6 .. +0.6 % | 0.4 % (max 1.9 %) |
| 50 | +0.27 % | −0.04 % | −0.4 .. +0.7 % | 0.3 % (max 1.5 %) |
| 60 | +0.26 % | +0.02 % | −0.3 .. +0.8 % | 0.2 % (max 1.3 %) |
| 80 | +0.26 % | +0.10 % | −0.2 .. +0.9 % | 0.2 % (max 1.0 %) |
| 100 | +0.27 % | +0.14 % | −0.1 .. +0.9 % | 0.1 % (max 0.9 %) |

The 68 % factors in `macs_kt` are v0.2's: the band at E_lab = kT. The bands did not change.

## Rates

| T9 | v0.2 / v0.2.1 − 1, median | 5-95 % | share from E_lab < 1 keV, median |
|---|---|---|---|
| 0.01 | −51.3 % | −55.2 .. −46.0 % | 51.2 % (max 56.1 %) |
| 0.03 | −16.5 % | −21.0 .. −10.8 % | 16.7 % (max 23.8 %) |
| 0.1 | −3.3 % | −5.5 .. −1.2 % | 3.7 % (max 7.3 %) |
| 0.3 | −0.4 % | −1.3 .. +0.2 % | 0.8 % (max 2.7 %) |
| 1 | +0.1 % | −0.1 .. +0.9 % | 0.1 % (max 1.0 %) |
| 3 | +0.3 % | −0.1 .. +1.0 % | 0.0 % (max 0.6 %) |

REACLIB 7-parameter fit, max residual over the grid: median 0.0035 dex, 99th percentile 0.122 dex (v0.2: 0.0034 /
0.121).

## ANCHORED: new scale factors

The anchor is the measured 30 keV MACS. It is not redistributed, but it equals the shipped `macs30_mb`, in v0.2 and in
v0.2.1. v0.2 scaled each curve so that its lab-frame, cut-at-1-keV MACS30 equalled the anchor. v0.2.1 applies one more
factor so that the centre-of-mass MACS30 equals it (to 6e-16). The full list is in `anchored_rescale_v021.csv`.

| nuclide | A | anchor (mb) | v0.2 factor | extra factor | v0.2.1 factor | curve change |
|---|---|---|---|---|---|---|
| Fe-60 | 60 | 5.15 | 0.817 | 1.00199 | 0.8186 | +0.20 % |
| Zn-70 | 70 | 9.34 | 0.875 | 1.00165 | 0.8764 | +0.17 % |
| Ge-76 | 76 | 21.5 | 0.631 | 1.00114 | 0.6317 | +0.11 % |
| Se-76 | 76 | 164 | 0.974 | 1.00087 | 0.9749 | +0.09 % |
| Pd-102 | 102 | 369 | 1.267 | 1.00122 | 1.2685 | +0.12 % |
| Te-120 | 120 | 519 | 1.172 | 0.99838 | 1.1701 | −0.16 % |
| Xe-126 | 126 | 359 | 0.963 | 0.99796 | 0.9610 | −0.20 % |
| Cs-135 | 135 | 160 | 1.767 | 0.99492 | 1.7580 | −0.51 % |
| Ba-132 | 132 | 397 | 1.672 | 0.99727 | 1.6674 | −0.27 % |
| Ce-136 | 136 | 300 | 0.971 | 0.99644 | 0.9675 | −0.36 % |
| Ce-138 | 138 | 179 | 0.845 | 0.99825 | 0.8435 | −0.18 % |
| Pm-147 | 147 | 709 | 0.936 | 0.99324 | 0.9297 | −0.68 % |
| Eu-154 | 154 | 4420 | 1.016 | 0.99435 | 1.0103 | −0.56 % |
| Eu-155 | 155 | 1320 | 0.973 | 0.99208 | 0.9653 | −0.79 % |
| Ho-163 | 163 | 2125 | 0.532 | 0.99268 | 0.5281 | −0.73 % |
| Hf-174 | 174 | 983 | 1.144 | 0.99542 | 1.1388 | −0.46 % |
| Hf-182 | 182 | 141 | 0.876 | 0.99792 | 0.8742 | −0.21 % |
| Os-184 | 184 | 590 | 0.616 | 0.99475 | 0.6128 | −0.53 % |
| Pt-190 | 190 | 508 | 0.858 | 0.99435 | 0.8532 | −0.56 % |
| Hg-196 | 196 | 204 | 0.639 | 0.99495 | 0.6358 | −0.50 % |
| Tl-204 | 204 | 260 | 1.332 | 0.99352 | 1.3234 | −0.65 % |

## `alt_macs30_mb`

This is the model-form alternative's MACS30, for the 1,131 flagged nuclides. The alternative curves are not shipped,
and the engine runs that made them are not kept. So `alt_macs30_mb` is the v0.2 value times the shipped curve's own
v0.2.1 / v0.2 MACS30 ratio: an approximation, good to the extent that the two curves have the same shape below
~100 keV. `alt_value_30keV_b` (a cross section, not an average) is unchanged.

## Checks (`VERIFY_V021.json`)

- **Independent recompute** for 12 nuclides (O-16, Na-23, Mg-24, Ca-40, Fe-56, Ni-62, Zr-90, Ba-138, Au-197, Pb-208,
  U-238, Cs-135). The method differs from the build: a 400,000-point trapezoid over the centre-of-mass energy from
  1e-6 eV, with σ looked up at E_lab = E(A+1)/A. Every kT, and the rate at T9 = 0.01, 0.1, 0.3, 1 and 5, agree to
  1.2e-9 or better (limit 1e-6).
- **Closed forms** through the build's integrator, at A = 1, 16, 56, 197 and kT = 5, 30, 100 keV: agree to < 1e-9.
  - A 1/v cross section gives MACS = σ(E_lab = kT(A+1)/A). Since σv is constant, the MACS is σ at the thermal relative
    velocity, which is the KADoNiS convention. The v0.2 formula gives 1.026 times that at A = 16 and 30 keV.
  - A constant cross section with the 1/v extension below 1 keV gives the incomplete-gamma expression.
- **Files**
  - The nuclides and tiers are v0.2's.
  - The 6,147 non-ANCHORED curves and all bands are identical to v0.2.
  - The channels and (n,p) grid are byte-identical copies.
  - Every MACS and rate is finite and positive, and every share is in [0, 1).
- **Against KADoNiS, MEASURED tier (descriptive).** KADoNiS compiles the same measurements, so this is not a test.
  The v0.2 numbers reproduce RATES.md of v0.2.

  | kT (keV) | nuclei | v0.2 f_rms (bias) | v0.2.1 f_rms (bias) |
  |---|---|---|---|
  | 5 | 194 | x1.629 (−0.024 dex) | x1.651 (+0.014 dex) |
  | 10 | 211 | x1.432 (+0.002 dex) | x1.440 (+0.013 dex) |
  | 30 | 211 | x1.344 (+0.017 dex) | x1.344 (+0.018 dex) |
  | 100 | 211 | x1.403 (+0.012 dex) | x1.401 (+0.011 dex) |

  The correction does not move the curves closer to KADoNiS. It fixes the definition. At 5 keV the 1/v extension
  shifts the median from −0.024 to +0.014 dex. The spread there comes from resolved resonances, which the smooth
  curve does not hold (`macs_flag`).

## Not changed

The research scorer and other research code (fr_compute.py, r9_cv.py, vc_compute.py) have the same lab-frame formula.
They are fixed separately, not here. The nucleus build code was not edited. This entry records the fix, and the
corrected computation is the script above.
