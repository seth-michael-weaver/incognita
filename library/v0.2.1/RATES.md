# Rates: MACS(kT), stellar rate, REACLIB fit (v0.2.1, 2026-11-06)

6168 nuclei. MACS at kT = 5, 8, 10, 15, 20, 25, 30, 40, 50, 60, 80, 100 keV. Rate on the REACLIB T9 grid (0.01-5.0 GK).
REACLIB 7-parameter fit, max residual over the grid: median 0.0035 dex, 99th percentile 0.122 dex.

Method (changed from v0.2, see BUILD.md):
- MACS(kT) = 2/sqrt(pi) kT^-2 int sigma(E (A+1)/A) E exp(-E/kT) dE, E the centre-of-mass energy (KADoNiS definition);
  ground-state target, no stellar enhancement;
- below E_lab = 1 keV (the grid's first point) sigma is extended as 1/v from that point; `share_below1keV_<kT>keV` in
  `macs_kt_v021.csv` is the part of each MACS that comes from it;
- N_A<sigma v> = N_A MACS(kT) v_T, v_T = sqrt(2 kT / mu), mu = A/(A+1) u, kT = 86.1733 keV x T9;
- the 68 % factors are v0.2's (the band at E_lab = kT; the bands did not change).

The low-temperature rates rest on the 1/v extension: it supplies a median 51 % of N_A<sigma v> at T9 = 0.01, 17 % at
0.03, 3.7 % at 0.1 and 0.8 % at 0.3. v0.2 left this part out (it cut at 1 keV), so its rates were about half the
v0.2.1 value at T9 = 0.01.

## Check against KADoNiS's own kT table (MEASURED tier, descriptive)
KADoNiS is a compilation of the same measurements. The curves are blind engine predictions.

| kT (keV) | nuclei | f_rms ours / KADoNiS | median bias (dex) | v0.2 f_rms (bias) |
|---|---|---|---|---|
| 5 | 194 | x1.651 | +0.014 | x1.629 (-0.024) |
| 10 | 211 | x1.440 | +0.013 | x1.432 (+0.002) |
| 30 | 211 | x1.344 | +0.018 | x1.344 (+0.017) |
| 100 | 211 | x1.401 | +0.011 | x1.403 (+0.012) |

Most of the gap comes from the resolved-resonance region. Use the rate products where `macs_flag` is empty; elsewhere,
prefer a measured MACS. Nothing outside Z 26-83 is validated.
