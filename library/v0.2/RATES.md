# Rates: MACS(kT), stellar rate, REACLIB fit (v0.2, 2026-10-23)

6168 nuclei. MACS at kT = 5, 8, 10, 15, 20, 25, 30, 40, 50, 60, 80, 100 keV. Rate on the REACLIB T9 grid (0.01-5.0 GK).
REACLIB 7-parameter fit, max residual over the grid: median 0.0034 dex, 99th percentile 0.121 dex.

The method is the same as v0.1:
- laboratory MACS, ground-state target, no stellar enhancement;
- the rate is the direct Maxwellian integral of the capture curve in `capture_v02.parquet`;
- the 68 % factors are interpolated from that file's band.

## Check against KADoNiS's own kT table (MEASURED tier, descriptive)
KADoNiS is a compilation of the same measurements. v0.2's MEASURED curves are blind engine predictions; v0.1's were
trained on these measurements.

| kT (keV) | nuclei | f_rms ours / KADoNiS | median bias (dex) | same, only nuclei whose resonance region stays below 3 keV | v0.1 f_rms (all / below 3 keV) |
|---|---|---|---|---|---|
| 5 | 194 | x1.629 | -0.024 | x1.318 (87 nuclei) | x1.614 / x1.204 |
| 10 | 211 | x1.432 | +0.002 | x1.257 (99 nuclei) | x1.423 / x1.156 |
| 20 | 211 | x1.352 | +0.014 | x1.234 (99 nuclei) | x1.325 / x1.132 |
| 30 | 211 | x1.344 | +0.017 | x1.232 (99 nuclei) | x1.297 / x1.127 |
| 50 | 211 | x1.352 | +0.016 | x1.239 (99 nuclei) | x1.289 / x1.125 |
| 100 | 211 | x1.403 | +0.012 | x1.265 (99 nuclei) | x1.325 / x1.133 |

How to read it:
- Most of the gap comes from the resolved-resonance region, not from the temperature.
- On nuclei whose resonances stay below 3 keV, the blind curves hold at x1.23-1.32 at every kT.
- Use the rate products where `macs_flag` is empty. Elsewhere, prefer a measured MACS.

The same caveat applies as in v0.1. For a nucleus whose resolved resonances reach into the MACS window, the integral
covers energies the curve makes no claim for (`macs30_flag` in the library). For those, use a measured MACS. Nothing
outside Z 26-83 is validated.
