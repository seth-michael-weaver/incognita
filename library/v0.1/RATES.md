# Rates: MACS(kT), stellar rate, REACLIB fit (2026-09-22)

6168 nuclei. MACS at kT = 5, 8, 10, 15, 20, 25, 30, 40, 50, 60, 80, 100 keV; rate on the REACLIB T9 grid (0.01-5.0 GK); REACLIB 7-parameter fit, max residual over the grid: median 0.0036 dex, 99th pct 0.084 dex.

## Check against KADoNiS's own kT table (MEASURED tier, descriptive; KADoNiS is a compilation of the same measurements)
| kT (keV) | nuclei | f_rms ours / KADoNiS | median bias (dex) | same, only nuclei whose resonance region stays below 3 keV |
|---|---|---|---|---|
| 5 | 194 | x1.614 | +0.004 | x1.204 (87 nuclei) |
| 10 | 211 | x1.423 | +0.023 | x1.156 (99 nuclei) |
| 20 | 211 | x1.325 | +0.028 | x1.132 (99 nuclei) |
| 30 | 211 | x1.297 | +0.028 | x1.127 (99 nuclei) |
| 50 | 211 | x1.289 | +0.024 | x1.125 (99 nuclei) |
| 100 | 211 | x1.325 | +0.023 | x1.133 (99 nuclei) |

Reading: the whole gap is the resolved-resonance region, not the temperature. On the 66 nuclei whose resonance region stays below 3 keV the smooth curves hold at x1.19 at EVERY kT, 5 to 100 keV; including the rest it degrades to x2.2 at 5 keV. So the rate products are usable wherever `macs_flag` is empty, at any kT, and a measured MACS should be preferred everywhere else.

Caveat that travels with these: for a nucleus whose resolved resonances reach into the MACS window the integral covers energies the curve makes no claim in (`macs30_flag` in the library); for those, use a measured MACS. Nothing outside Z 26-83 is validated.
