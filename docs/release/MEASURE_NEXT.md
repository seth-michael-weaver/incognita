# MEASURE_NEXT (2026-09-22): capture measurements that would teach the library the most

Candidates: Z 26-83 ground states with NO scored differential capture data and NO measured MACS (KADoNiS measured entries, ASTRAL), target makeable (stable or t1/2 >= 1 d).
Ranked by today's CALIBRATED uncertainty at 30 keV: the EXTRAPOLATED-tier 68 % interval (extrap_sigma.py: 8-model spread with floor, conformal q, D0 inflation; DEV coverage 66 / 94 %), shown as a factor. `after` = the ANCHORED-tier 68 % factor one measured MACS30 (10 %) would give. `model spread` = the old max/min ranking, for comparison.
Removed as already measured: KADoNiS measured entries, ASTRAL, newer measurements in anchored_targets_checked (Tl-204, n_TOF 2024), and any nucleus with an EXFOR Maxwellian-average entry (anchors/exfor_anchor_candidates.csv).
One vetted measurement pins a nucleus's level (anchored-tier validation: 28 % -> 14 % at 10 keV-1 MeV). Flag `s-branch` = known s-process branch point.
Not a use-weighted value of information (no astrophysics or applications weight yet). The calibrated factor ranks by the SD over models, the old one by max / min, so the order differs mainly where one model is an outlier. Full table: MEASURE_NEXT.csv

Candidates found: 188 (stable 2, long-lived 33, short-lived 153); s-process branch points among them: 9

## Stable targets (activation or TOF with an enriched sample)
| target | half-life | today's 68 % factor at 30 keV (calibrated) | after one MACS30 measurement | model spread (max/min) | median MACS-like value (mb) | neutrons to nearest measured isotope |
|---|---|---|---|---|---|---|
| In-113 | stable | x1.48 | x1.17 | x1.51 | 631 | 2 |
| Ru-98 | stable | x1.45 | x1.17 | x1.49 | 172 | 1 |

## Long-lived radioactive targets (>= 1 y)
| target | half-life | today's 68 % factor at 30 keV (calibrated) | after one MACS30 measurement | model spread (max/min) | median MACS-like value (mb) | neutrons to nearest measured isotope |
|---|---|---|---|---|---|---|
| La-137 | 6e+04 y | x3.63 | x1.17 | x4.42 | 519 | 2 |
| Pb-202 | 5.25e+04 y | x3.24 | x1.17 | x4.02 | 235 | 2 |
| Mo-93 | 4e+03 y | x3.04 | x1.17 | x3.33 | 256 | 1 |
| Os-194 | 6 y | x2.81 | x1.17 | x3.43 | 84.1 | 2 |
| Sb-125 | 2.76 y | x2.79 | x1.17 | x3.58 | 52.9 | 2 |
| Cs-134 (s-branch) | 2.06 y | x2.63 | x1.17 | x3.05 | 602 | 1 |
| Pb-210 | 22.2 y | x2.54 | x1.17 | x3.82 | 1.27 | 2 |
| Pt-193 | 50 y | x2.09 | x1.17 | x2.08 | 965 | 1 |
| Fe-55 | 2.76 y | x2.03 | x1.17 | x2.44 | 81.3 | 1 |
| Kr-85 (s-branch) | 10.7 y | x2.03 | x1.17 | x2.40 | 65.7 | 1 |
| Pm-145 | 17.7 y | x2.03 | x1.17 | x2.30 | 602 | 2 |
| Sm-146 | 6.8e+07 y | x1.85 | x1.17 | x2.14 | 169 | 1 |
| Nb-91 | 680 y | x1.78 | x1.17 | x2.00 | 134 | 2 |
| Bi-208 | 3.68e+05 y | x1.73 | x1.17 | x1.97 | 67.5 | 1 |
| Tb-157 | 71 y | x1.72 | x1.17 | x1.93 | 3.14e+03 | 2 |

## s-process branch points (any half-life >= 1 d)
| target | half-life | today's 68 % factor at 30 keV (calibrated) | after one MACS30 measurement | model spread (max/min) | median MACS-like value (mb) | neutrons to nearest measured isotope |
|---|---|---|---|---|---|---|
| Cs-134 (s-branch) | 2.06 y | x2.63 | x1.17 | x3.05 | 602 | 1 |
| Kr-85 (s-branch) | 10.7 y | x2.03 | x1.17 | x2.40 | 65.7 | 1 |
| Re-186 (s-branch) | 3.72 d | x1.68 | x1.17 | x1.73 | 1.4e+03 | 1 |
| Gd-153 (s-branch) | 241 d | x1.66 | x1.17 | x1.97 | 2.34e+03 | 1 |
| Hf-181 (s-branch) | 42.4 d | x1.51 | x1.17 | x1.51 | 193 | 1 |
| Tm-170 (s-branch) | 129 d | x1.43 | x1.17 | x1.43 | 1.56e+03 | 1 |
| Os-185 (s-branch) | 93 d | x1.41 | x1.17 | x1.48 | 1.12e+03 | 1 |
| Er-169 (s-branch) | 9.39 d | x1.40 | x1.17 | x1.41 | 582 | 1 |
| Nd-147 (s-branch) | 11 d | x1.30 | x1.17 | x1.18 | 737 | 1 |

