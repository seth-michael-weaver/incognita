# BUGSCORE2: scoring audit, round 2 (2026-11-07)

Round 1 (BUGSCORE, 2026-11-07) reported eight scoring defects without fixing them, because a fix could move a
published number. Round 2 wrote a regression test for each (`tests/test_bugscore2.py`, synthetic inputs only),
computed the exact effect of each fix on every published number it touches, and applied the fixes that change no
published verdict (ranking or significance). The others are amendment drafts below; they need a registered decision
before they are applied.

How the effects were computed: the old and the new scorer on the frozen track rows, for every library grid available
(staged ENDF/B-VIII.1, JENDL-5, JEFF-4.0, TENDL-2025; ENDF/B-VII.0 and -VII.1 from the official-file grids built on
2026-11-06; JEFF-3.3, CENDL-3.2, JENDL-4.0 and TENDL-2015 to -2023 from their cached MT subsets). The old scorer
reproduces every published number checked (JENDL-4.0 capture-heldout 0.133 / 1795 rows, capture-retro 0.149,
He production 0.174, ch-na 0.277, ch-np 0.182; ch-na JEFF-4.0 0.281, JENDL-5 0.283, ENDF/B-VII.0 0.307; ch-np
CENDL-3.2 0.172; ch-n2n ENDF/B-VII.0 0.113, JEFF-3.3 0.115, JENDL-5 0.117; ch-sacs CENDL-3.2 0.230, JENDL-4.0 0.251,
JENDL-5 0.255; TENDL-Y 0.193 and ours − TENDL-Y −0.056 [−0.106, −0.020]).

| # | finding | published numbers touched | status |
|---|---|---|---|
| 1 | consensus mode ignored the 1e-5 b floor and weighted orphan bins 1.0 | none | applied |
| 2 | fix-unit cells (trust 0, value ×1000) in the unweighted rows | none (frozen predictions) | applied |
| 3 | `interp_loglog` holds the first positive value below a threshold | ch-n2n, ch-na, ch-np, He production: changes the ch-na ranking | draft E |
| 4 | SACS integrals from 100 keV | ch-sacs, all libraries; ranking unchanged | applied |
| 5 | R11 (MACSCHECK) series MACS in the lab frame | curation register v2 evidence; no decision | draft D |
| 6 | `gatecalib/thresholds.py` says Šidák, computes Bonferroni | research-tree verdict relabel; no verdict | draft F (outside this repository) |
| 7 | binavg vs score.py MT 5 rules (round-1 amendments B, C) | none | applied |
| 8 | capture-retro TENDL-Y chose releases by name (round-1 amendment A) | capture-retro TENDL-Y; win stands | applied |

## Applied

**1. Consensus mode** (`validation/differential/core.py`, `load_exfor_points`). The cell cache marks cells below
`CHANNEL_FLOOR_B` excluded, but the consensus table is fitted upstream and keeps those bins; a bin with no usable cell
behind it got weight 1.0 at `min_trust = 0` (the comment said there were none). Now the floor is applied to
`consensus_b` and orphan bins are dropped at every `min_trust`, both counted. Rows (kinds sig/av, state and branch
empty): (n,α) 493 → 469 (23 below the floor down to 3.8e-12 b, 1 orphan above it), (n,p) 399 → 391 (8 below the floor,
7 of them orphans), capture 11,013 → 11,012 (1 orphan), (n,2n) 409 unchanged. Over all kinds the orphans are 33 (n,α)
and 14 (n,p), as round 1 found. No published number of this repository is computed in consensus mode (the bench tracks
are frozen row files; consensus mode is used only by tests here). The research tree's copy of `core.py` has the same
code and scripts there use consensus mode; they are not re-run here.

**2. Fix-unit cells** (same function, both modes). The 13 fix-unit capture cells carry trust 0 and the value as
compiled. Trust only silences them in trust-weighted sums; `models/macs_constraint.py` reads the datasets-mode `mxw`
rows without the weight when a year cutoff is set, so the nine 14797006 Mo-95 MACS cells (2022, 346-1018 b instead of
mb) entered the MACS constraint of any time-split run with cutoff ≥ 2022. They are now removed and counted
(`dropped_fix_unit`). Published numbers come from frozen predictions and do not move. The capture-retro Mo-95 rows are
Y = 2015 and 2017 only, so Mo-95's own retrodiction never saw them; whether the Y = 2023 arm (17 rows: Se-78, Se-79,
I-129, Tm-169, Re-187) ran with EXFOR MACS rows, and so saw them through shared parameters, was not checked: that needs
the development run logs.

**4. SACS grid** (`incognita/eval/spectra.py`). 1.3 % of the U-235 Watt and of the Cf-252 Maxwellian spectrum lies
below 100 keV. Old grid: capture SACS 0.024 dex low (a 1/v test case: −0.0247 dex), threshold SACS 0.006 dex high (the
normalisation). New grid: 1e-5 eV to 20 MeV, same point density. ch-sacs rms, old → new (rows):

| library | all rows | capture rows | ranking rows (no (n,α) for the three partial grids) |
|---|---|---|---|
| CENDL-3.2 | 0.2362 → 0.2351 (356) | 0.2066 → 0.1950 | 0.2300 → 0.2284 (307) |
| JENDL-4.0 | 0.2612 → 0.2595 (295) | 0.2082 → 0.1979 | 0.2508 → 0.2487 (239) |
| JENDL-5 | 0.2552 → 0.2538 (395) | 0.2328 → 0.2207 | |
| TENDL-2025 | 0.2657 → 0.2642 (395) | 0.2382 → 0.2231 | |
| ENDF/B-VII.1 | 0.2659 → 0.2652 (393) | 0.1952 → 0.1840 | |
| ENDF/B-VIII.1 | 0.2670 → 0.2659 (385) | 0.2090 → 0.1967 | |
| JEFF-3.3 | 0.2752 → 0.2742 (395) | 0.2325 → 0.2191 | |
| JEFF-4.0 | 0.2836 → 0.2824 (388) | 0.2445 → 0.2309 | |
| ENDF/B-VII.0 | 0.3019 → 0.3014 (341) | 0.1910 → 0.1805 | |

The order of every entry is unchanged. BROND-3.1, FENDL-3.2 and IRDFF-II (published values on the old rows) were not
re-scored; no grid of them is on our machines.

**7. Amendments B and C** (`incognita/bench/binavg.py`). B: `binavg` blanked the (n,α) curve wherever σ(MT 5) > 0 when
the MT 5 products were not read; the point scorer counts a row incomplete only where σ(MT 5) can exceed 1 % of the
value. C: `binavg` dropped an (n,α) that a file gives only inside MT 5 (no MT 107 / 800-849); the point scorer keeps it
when it reaches 1 mb. Both now follow the point scorer. The only published bin-average (n,α) numbers are ENDF/B-VII.1's
on the dated tracks (rebuilt 2026-11-06 from the official files). Its official-file grid has no nucleus with (n,α) only
inside MT 5 and none with σ(MT 5) > 0 and unread products, so none of the 1,845 dated (n,α) rows changes. (The
ENDF/B-VIII.1 staged grid on the laptop lacks the MT 5 product parts, so 306 dated (n,α) rows would be blanked under
the old rule B if that grid were used; the published placement read the official files.)

**8. Amendment A, TENDL-Y release year** (`incognita/bench/score.py`, `tendl_y`). The capture-retro TENDL-Y entry took
the newest release whose NAME year ≤ Y. `DATED_Y` (the dated tracks' table) gives TENDL-2015 → 2016 and TENDL-2023 →
2024. With release years: TENDL-Y 0.1930 (286 rows) → 0.1731 [0.128, 0.253] (193 rows; the 93 Y = 2015 rows have no
release here); ours on the same rows 0.1322; ours − TENDL-Y −0.0557 [−0.1056, −0.0197] → −0.0409 [−0.0698, −0.0130]
(seed 20260910, 5,000 draws). Round 1's narrower amendment A (only TENDL-2023 → TENDL-2021 at Y = 2023, TENDL-2021 grid
from the validation cache) gives 0.1957 on 286 rows and −0.0584 [−0.1077, −0.0224]. Either way the win stands; the
rule applied is the one the code already uses for the dated tracks.

## Amendment drafts (not applied)

### D. R11 (MACSCHECK) in the centre-of-mass frame (item 5)

Finding: `Engine.macs_over` (`incognita/curation/rules.py`) Maxwellian-averages the series curve with lab energies;
MACS is defined with the centre-of-mass energy E = E_lab A/(A+1). For a 1/v curve the lab value is high by
0.5 log10(1 + 1/A) (0.004 dex at A = 56). Library v0.2.1 fixed the same bug in the library
(`scripts/release/build_library_v021.py`).

Proposed change: integrate with θ = kT (A+1)/A (weight E_lab² e^(−E_lab/θ) d ln E_lab, coverage normalised by θ²); the
patch is 16 lines, test `test_r11_series_macs_is_centre_of_mass` (strict xfail until adopted; it passes with the patch).

Impact (recomputed on the shipped curation cells; the lab-frame run reproduces the shipped
`curation_r11_series_v2.csv`, 261 testable series, 5 flagged, exactly): R = series MACS / IM shifts by −0.0014 dex
(median; range −0.0080 to +0.0001) over the 725 IM comparisons. Flags and grades: unchanged (5 flagged: 4 R11d, 1 R11x),
so no curation decision changes. Testable series 261 → 262 (Br-81 series 57 becomes testable, 1 group, not flagged);
Ba-137 series 424 goes from 3 groups (1 against) to 1 (1 against), not flagged either way. Why not applied: the
published register files (`curation_r11_series_v2.csv`, `curation_summary_v2.json` r11_testable 261 → 262, the R11
evidence in `curation_register_v2.*`) must be regenerated with the change, and the build needs the EXFOR master
(`raw/exfor/entry.zip`), which is not on the machines used here. Adopt by applying the patch and rerunning
`bash scripts/reproduce.sh --download curation`, then replacing the shipped files.

### E. Point scorer below a library's threshold (item 3)

Finding: `interp_loglog` (`incognita/bench/score.py`) interpolates over the positive points only, so a row below the
first positive grid point gets that point's value (np.interp holds it flat). Proposed rule: below the first positive
point, interpolate the curve's own points lin-lin (a ramp from the last zero point; zero, i.e. not covered, below it).
The top end must keep the hold: the staged grids end at 2e7 eV and many tables end there with a zero last grid point;
ramping to it moved 20 MeV rows by up to 13 dex in a first trial.

Rows that change (old → new log10 b; "—" = not covered):

| row | library | old | new | label |
|---|---|---|---|---|
| ch-n2n Ga-71 9.44 MeV | ENDF/B-VII.0, -VII.1, -VIII.1 | −3.126 | −3.423 | −1.936 |
| | JENDL-5 | −2.309 | — | |
| | JEFF-3.3 / JEFF-4.0 / CENDL-3.2 | −2.645 / −3.033 / −3.110 | −2.942 / −3.329 / −3.407 | |
| ch-n2n Mo-92 12.92 MeV | ENDF/B-VII.0, -VII.1, -VIII.1 | −2.554 | −2.673 | −2.022 |
| | JENDL-5 / JEFF-3.3 | −2.025 / −2.025 | — / — | |
| ch-na Fe-54 2.23 MeV | ENDF/B-VII.0, -VII.1 | −6.005 | — | −2.185 |
| ch-na and He production, Cr-50 5.1 MeV | CENDL-3.2 | −3.781 | — | −2.836 |
| ch-np Cu-65 2.22 MeV | CENDL-3.2 | −5.165 | — | −2.508 |

Track rms, old → new (rows): ch-n2n ENDF/B-VII.0 0.1134 → 0.1154 (2073), JEFF-3.3 0.1155 → 0.1164 (2296 → 2295),
JENDL-5 0.1170 → 0.1168 (2334 → 2332), TENDL-2025 0.1178 → 0.1191, ENDF/B-VIII.1 0.1289 → 0.1304, ENDF/B-VII.1
0.1259 → 0.1275, JEFF-4.0 0.1458 → 0.1469, CENDL-3.2 0.1729 → 0.1742 (ranking unchanged); ch-na ENDF/B-VII.0
0.3074 → 0.2816 (952 → 951), ENDF/B-VII.1 0.3109 → 0.2870, CENDL-3.2 0.2844 → 0.2829; ch-np CENDL-3.2 0.1723 → 0.1571
(1402 → 1401); He production CENDL-3.2 0.2545 → 0.2427 (142 → 141). Capture tracks, na-pickup, na-post2021 and every
INCOGNITA entry: unchanged.

Why not applied: it changes a published ranking. ch-na top three, JEFF-4.0 0.281, JENDL-5 0.283, ENDF/B-VII.0 0.307,
becomes JEFF-4.0 0.2808, ENDF/B-VII.0 0.2816, JENDL-5 0.2830. And it does so for a reason worth deciding explicitly:
under the scorer's convention a zero prediction is "not covered", so the fix removes a library's worst rows (Fe-54
(n,α) at 2.23 MeV, where ENDF/B-VII.0 is effectively zero against 6.5 mb measured) instead of scoring them. Options for
the registered decision: (a) the rule above (zero → not covered, as now for every other zero); (b) the rule above, but a
row where the library is zero and the measurement is positive counts as a miss of a fixed size (e.g. the 1 dex that
na-post2021 uses), on every threshold track; (c) keep the flat hold and document it. (b) is the fairest to the
measurements; its numbers are not computed here. Test: `test_interp_loglog_does_not_hold_the_threshold_value_flat`
(strict xfail).

### F. `scripts/gatecalib/thresholds.py` (item 6; research tree, not part of this repository)

The "Šidák-widened" CIs use z(1 − 0.025/k), which is Bonferroni; Šidák is z(1 − (1 − 0.95^(1/k))/2). (Its per-nuclide
harm limit, Φ⁻¹(0.95^(1/n)), is correctly Šidák.) Factor at k = 8: 1.3951 (Bonferroni) vs 1.3914 (Šidák); at k = 20:
1.5425 vs 1.5388. Corrected lower bounds quoted in `VERDICT_RELABEL_2026-11-06.md`, Bonferroni → Šidák: BANDTAIL T1 ZB
IS68 −0.00373 → −0.00367, T2 ZB IS95 −0.02196 → −0.02161, BANDCAL ZB IS95 +0.07406 → +0.07426 (k = 20: +0.06624 →
+0.06644), BANDCAL ZB CRPS −0.00020 → −0.00019, BANDCAL EB na IS68 −0.00568 → −0.00559. No sign changes, so no verdict
moves (BANDTAIL stays INCONCLUSIVE, BANDCAL STANDS). Bonferroni is the more conservative of the two and valid as such;
the minimal fix is to call it Bonferroni (or switch the formula to Šidák). Not applied here: the file is in the
research tree, outside this repository.
