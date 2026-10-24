# v0.2 library build (2026-10-23; production engine engine-20261022-3)

6168 nuclei: EXTRAPOLATED 5611, INTERPOLATED 316, MEASURED 220, ANCHORED 21 (the same nuclei and the same tiers as v0.1)

| tier | nuclei | median 68 % factor at 30 keV | median 95 % factor at 30 keV | v0.1: 68 % / 95 % |
|---|---|---|---|---|
| ANCHORED | 21 | x1.32 | x2.17 | x1.16 / x1.48 |
| EXTRAPOLATED | 5611 | x1.60 | x2.49 | x1.58 / x2.42 |
| INTERPOLATED | 316 | x1.39 | x2.17 | x1.34 / x1.80 |
| MEASURED | 220 | x1.32 | x2.17 | x1.24 / x1.65 |

No ENDF-6 transport files. Floor-leak check: 0 shipped curves carry an engine floor/dropout point.

## What v0.2 is

v0.2 is v0.1 rebuilt on the engine the scoreboard scores. The files, the nuclei and the tiers are the same as in v0.1.
What changed is where the numbers come from:

- **Every capture curve is the production engine's prediction.** The engine is engine-20261022-3 (nucleus commit
  16606b356, production since 2026-10-22 22:05), run with its production settings and inputs.
  - For the 250 nuclei of the engine's reference set, the curves are the reference product itself, the same numbers
    the scoreboard compares with measurements.
  - The other 5,900 nuclei were run the same way: same engine, same settings, same input tables, same rules for
    combining the engine's two capture variants. A control nucleus (Nb-94) rerun this way matched the reference product
    to 7e-13 (relative).
  - 18 nuclei near the drip lines have no production input file. They keep their v0.1 values, and `value_source`
    says so.
- **Tiers now describe the data, not the method.** In v0.1 the tier decided the method: a model trained on the
  measurements for MEASURED and INTERPOLATED, and the old engine recipe for EXTRAPOLATED. In v0.2 all of them are the
  engine's blind prediction, so a MEASURED curve was not fitted to the measurements next to it.
- **ANCHORED** keeps v0.1's rule: the engine curve is scaled by one factor so that its 30 keV MACS equals the measured
  value.
- **Uncertainty bands**: at each energy, the wider of two bands, taken separately for 68 % and 95 %:
  - the engine's own band (UNCCAL v2, the spread of the production engine against held-out measurements; for capture it
    is labelled "not calibrated" because it is too wide), and
  - that nucleus's v0.1 interval.
  So no v0.2 band is narrower than in v0.1. No new band was calibrated (see Known limits).
- **(n,p), (n,2n), (n,α)** (`channels_v02.parquet`) come from the same engine runs.
  - `grid_np_v02.parquet` gives (n,p) at v0.1's 361 targets and energies. Values are interpolated (log-log) from the
    engine's 134-point grid, which is spaced 0.25 MeV above 5 MeV, and carry the engine's (n,p) band (calibrated in
    UNCCAL v2).
  - v0.1's learned (n,p) correction is dropped: it was fitted on top of an older engine and does not apply to this one.
    Its flag columns (`tendl_fitted_other_data`, `outside_training_*`, `e1_constant_*`) and `recipe_mb` are therefore gone.
- **Engine output floor**: points where the engine returns its output floor or drops out are repaired by v0.1's rule
  (log-log interpolation between neighbours). 275 curves had such points, 1,982 points in all, mostly on nuclei far from
  stability.

## Checks

- Every capture value is finite and positive (smallest 1.0e-10 b). Every band is finite with 0 <= 68 % <= 95 %. Every
  MACS is finite and positive. Every channel value is finite and non-negative. Every (n,p) row has
  lo95 <= lo68 <= value <= hi68 <= hi95.
- 0 floor leaks. Each ANCHORED MACS equals its anchor to 7e-16.
- The universe (6,168 nuclei) and every tier match v0.1.
- MACS against KADoNiS on the MEASURED tier. This is descriptive: KADoNiS compiles the same measurements, and nothing
  was fitted to it. f_rms is the rms ratio; the last column keeps only nuclei whose resolved resonances stay below 3 keV.

  | kT (keV) | nuclei | v0.2 f_rms (bias) | v0.1 f_rms | v0.2, resonances < 3 keV | v0.1, same |
  |---|---|---|---|---|---|
  | 5 | 194 | x1.629 (-0.024 dex) | x1.614 | x1.318 | x1.204 |
  | 30 | 211 | x1.344 (+0.017 dex) | x1.297 | x1.232 | x1.127 |
  | 100 | 211 | x1.403 (+0.012 dex) | x1.325 | x1.265 | x1.133 |

  v0.1's MEASURED curves were trained on these measurements. v0.2's are blind, so they are a little further away
  (x1.34 against x1.30 at 30 keV). The bias is small (+0.017 dex).

## What changed against v0.1 (MACS at 30 keV, log10 v0.2/v0.1)

| tier | nuclei | median | middle 50 % | middle 90 % | rms | share > 0.3 dex | share > 1 dex | inside v0.1's 68 % band |
|---|---|---|---|---|---|---|---|---|
| MEASURED | 220 | -0.018 | -0.077 .. +0.032 | -0.155 .. +0.137 | 0.100 | 0.9 % | 0 % | 68 % |
| ANCHORED | 21 | 0 (by construction) | | | | | | |
| INTERPOLATED | 316 | -0.158 | -0.264 .. -0.079 | -0.502 .. +0.039 | 0.270 | 19.6 % | 0.9 % | 37 % |
| EXTRAPOLATED | 5611 | +0.049 | -0.002 .. +0.128 | -0.132 .. +1.109 | 0.507 | 13.9 % | 5.6 % | 83 % |

- **MEASURED**: going from the trained model to the blind engine moves most nuclei by less than 0.15 dex, in both
  directions (94 up, 126 down). The biggest change is U-234 (-0.58 dex, 709 -> 186 mb). Next come Pb-208 (-0.36),
  Eu-151, Bi-209 and Ce-142 (about -0.25 each).
- **ANCHORED**: the MACS is unchanged by construction. Only the shape of the curve changes (-0.06 dex median at 1 MeV).
- **INTERPOLATED**: the blind engine is lower than v0.1's trained model for 280 of 316 nuclei (median -0.16 dex). The
  largest drops are on the proton-rich side of measured nuclei: Zn-60, Cu-58 and Ga-64 fall by about -1.1 to -1.2 dex,
  and Br-74, Rb-78 and Tc-92 by -0.8 to -0.9. v0.1's model carried its neighbours' level of capture to these nuclei; the
  engine does not.
- **EXTRAPOLATED**: the typical change is small (+0.05 dex median; +0.05 in Z 26-83 for N >= Z). The tail comes from
  very proton-rich nuclei (N < Z, 284 nuclei; median +1.5 dex).
  - v0.1's old recipe gave many of them a MACS of about 0.001-0.005 mb. The production engine gives a few mb (for
    example Co-46, Cr-42 and Fe-45 up by about +3.3 to +3.5 dex).
  - 308 nuclei rose by more than 1 dex; 178 of them have N < Z.
  - Mo-86 rose most (0.049 -> 704 mb, +4.2 dex).
  - A few proton-unbound targets fell to essentially zero capture: F-13 (-4.6 dex, after 28 of 64 points hit the
    engine floor and were repaired), I-103 (-4.2), Na-17 and Cs-107 (about -3.4 to -3.5).
  - These far-from-stability values are outside the validated range and should be read as very uncertain.
- Full lists: VERIFY_V02.json (per-tier numbers). The development record holds the movers table with reasons.

## Why the large movers move (review 2026-10-23)

318 nuclei moved by more than 1 dex in their 30 keV MACS: 315 EXTRAPOLATED and 3 INTERPOLATED. 308 went up and 10 down;
183 of them have N < Z. Each carries the cause in the `v01_mover_note` column of `capture_v02.parquet` and
`macs30_v02.csv`.

**Not a build error.** The run set-up reproduces the scored product: the control nucleus matches to 7e-13, and Mo-86
rerun on the laptop matches the Mac mini run exactly. The movers were diagnosed by rerunning each one with a single
production setting switched off:

| cause | movers |
|---|---|
| production deck runs pre-equilibrium emission at all incident energies (`preequilibrium y`). This matters only where compound capture is almost shut off (very proton-rich and some heavy nuclei); switched off, the curve returns to within 0.5 dex of v0.1 | 276, plus 2 partly |
| production's fix for the radiative dead end (GGDEADEND). Without it the old level lists leave the capture state almost no gamma decay (Γγ: Rh-106 2.7e-7 eV, Mo-87 0 eV, against a normal 0.01-1 eV); TALYS-based TENDL keeps that defect | 2 alone, 1 partly, 8 together with pre-equilibrium |
| production fission transmission (`fists2`, actinides) | 22, plus 1 partly |
| none of these switches moves it by more than 0.3 dex (includes the 3 INTERPOLATED nuclei Zn-60, Cu-58, Ga-64, where v0.2 now agrees with TENDL-2025) | 6 |

Examples:
- Rh-105: 896 mb at 30 keV; with the dead-end fix off, 3.3 mb (v0.1 2.9 mb, TENDL 2.3 mb).
- Co-46: 3.5 mb; with pre-equilibrium off, 0.0013 mb (v0.1 0.0010 mb).
- Fm-255: 917 mb; with fission transmission off, 104 mb (v0.1 30 mb).

**Comparison with evaluated libraries at 30 keV** (comparators only; nothing is fitted to them). 2,251 nuclei have a
value, almost all from TENDL-2025:

| tier | nuclei | median abs(log10 v0.1/library) | v0.2 |
|---|---|---|---|
| MEASURED | 220 | 0.033 | 0.067 |
| ANCHORED | 21 | 0.034 | 0.033 |
| INTERPOLATED | 315 | 0.085 | 0.100 |
| EXTRAPOLATED | 1695 | 0.065 | 0.113 |

Only 15 of the movers have a library value. On those, the median distance grows from 0.79 dex (v0.1) to 1.48 dex (v0.2).
TENDL is made with TALYS, so it shares v0.1's old recipe, including the dead-end defect. Agreement with it is therefore
not evidence either way. The pre-equilibrium-at-keV behaviour is a property of the production engine (it was seen
before in the project's own records). Whether to keep it for these nuclei is a decision about the engine, not about
this build.

## Model-form uncertainty far from stability

Two settings of the production engine change keV capture a lot on some nuclei, and no measurement can say which choice
is right there.

- **Pre-equilibrium at keV energies.** The production engine runs pre-equilibrium emission at every incident energy
  (`preequilibrium y`). This was a deliberate, gated choice (PEONSET, 2026-10-09). Its effect on keV capture was logged
  then as unmeasured and untestable. TALYS and TENDL switch pre-equilibrium on only from about 1 MeV.
  - For most nuclei the two choices give the same keV capture. They differ where compound-nucleus capture is almost
    shut off: very proton-rich nuclei, some neutron-rich ones, and fissile heavy nuclei.
  - Above 1 MeV the choice changes nothing that matters (PEONSET found ≤ 3.4e-6 dex).
- **Fission transmission (`fists2`)** changes keV capture on some actinides.

**What we did.**
- We reran every nucleus with pre-equilibrium switched off, which below 1 MeV is the same as the TALYS default onset.
  We reran the 23 actinides whose v0.1→v0.2 change comes from fission transmission with `fists2` off. Nothing else in
  the engine changed.
- A nucleus is flagged when, at some energy below 1 MeV, the two choices differ by more than a factor 2 (0.3 dex).
- The central value stays the production value. Below 1 MeV the 95 % band is widened, symmetrically in log, until it
  also contains the alternative value. The 68 % band is widened by the same factor. Above 1 MeV the bands are
  unchanged.
- The full alternative curve was available for every flagged nucleus, so no band was widened from a 30 keV value alone.
- New columns in `capture_v02.parquet`, `macs30_v02.csv` and `macs_kt_v02.csv`:
  - `model_form_flag`: `pe_kev`, `fists2`, `gg_deadend` or `none`;
  - `alt_model`;
  - `alt_value_30keV_b`;
  - `alt_macs30_mb`.
  `capture_v02.parquet` also has `model_form_max_dex_sub1MeV`.

**Counts.**

| `model_form_flag` | nuclides | what it means |
|---|---|---|
| `pe_kev` | 1,108 | pre-equilibrium choice matters below 1 MeV; band widened |
| `fists2` | 23 | fission-transmission choice matters; band widened |
| `gg_deadend` | 3 | Mo-86, Tc-87, Rh-105. The move from v0.1 comes from production's fix of a known defect (the radiative dead end, which leaves the capture state almost no gamma decay). Noted only; not widened, because the old value is a defect, not a model choice |
| `none` | 5,034 | |

- All flagged nuclides are EXTRAPOLATED.
- 270 have N < Z, 109 have Z < 20, 381 have Z ≥ 88, and 573 lie in Z 26-83.
- The 30 keV value alone differs by more than 0.3 dex for 552 of them.
- Where the two choices differ, the alternative is usually lower: median -0.26 dex at 30 keV, lower in 78 % of cases.

**Band width at 30 keV, flagged nuclides (multiplicative 95 % factor).**

| | before | after |
|---|---|---|
| median | x2.7 | x4.3 |
| 90th percentile | x14 | x82 |
| largest | | x7.3e4 |

The median 68 % factor goes from x1.66 to x2.11. Over the whole EXTRAPOLATED tier, the median 30 keV factors go from
x1.58 / x2.45 to x1.60 / x2.49.

**Against TENDL-2025** (a comparator only). The central values did not change, so the median |log10(v0.2 / TENDL)| at
30 keV is the same as before:

| tier | nuclei | median |
|---|---|---|
| MEASURED | 219 | 0.067 |
| ANCHORED | 21 | 0.033 |
| INTERPOLATED | 315 | 0.100 |
| EXTRAPOLATED | 1,694 | 0.113 |

72 flagged nuclides have a TENDL value. TENDL is inside their 95 % band for 28 of them, up from 27 before the widening.
The widening only spans our own two choices, and TENDL also differs in other ways (for example, it keeps the radiative
dead end). So it is no surprise that the widened bands rarely reach TENDL.

## Band coverage of the curated measurements (descriptive)

These are not new data, so this is descriptive, not a calibration test: the curated EXFOR capture points shown in the
site's data explorer were used, together with many others, to set the engine's global parameters and v0.1's bands.
Count: points of MEASURED and ANCHORED nuclides that the curation kept (excluded points left out), with the curve and
band interpolated log-log to the point's energy; points inside the resolved-resonance region (where the curve is an
average) and outside 1 keV - 20 MeV are left out. 12,358 points on 214 nuclei (211 MEASURED, 3 ANCHORED); the same
points for v0.1 and v0.2.

| tier | energy | points | v0.1 inside 68 % | v0.1 inside 95 % | v0.2 inside 68 % | v0.2 inside 95 % |
|---|---|---|---|---|---|---|
| MEASURED | all | 12,326 | 75 % | 92 % | 67 % | 94 % |
| MEASURED | 1-10 keV | 1,577 | 76 % | 95 % | 62 % | 97 % |
| MEASURED | 10-100 keV | 5,286 | 77 % | 93 % | 70 % | 96 % |
| MEASURED | 0.1-1 MeV | 3,888 | 75 % | 90 % | 69 % | 93 % |
| MEASURED | 1-20 MeV | 1,575 | 65 % | 88 % | 60 % | 90 % |
| ANCHORED | all (0.1-20 MeV) | 32 | 25 % | 97 % | 50 % | 97 % |

Each nucleus counted once (mean of its own fractions), MEASURED: v0.1 73 % / 91 %, v0.2 63 % / 91 %.

How to read it: v0.1's MEASURED curves were trained on these points; v0.2's are blind, so the 68 % band holds fewer of
them (67 % against 75 %), while the wider 95 % band holds a few more (94 % against 92 %). Both are close to the nominal
68 % and 95 %, but because the points are not independent of the model, this does not show that the bands are
calibrated. The ANCHORED row has too few points to read.

## Known limits

- **No new coverage test.** v0.1 had one registered vault read (folds 6-7), which is spent. No held-out or vault read
  was made for v0.2. Its bands are the wider of the engine band and v0.1's band, not a newly calibrated interval.
- **Far-from-stability values changed by orders of magnitude** between engine versions (see EXTRAPOLATED above). That
  shows how weakly the model constrains them; the bands there may be too narrow.
- 18 drip-line nuclei carry v0.1 values (no production input).
- The (n,p) grid is interpolated from a 0.25-0.5 MeV engine grid. Close to threshold this can miss shape.
- Only Z 26-83 is covered by the project's validation. MACS where `macs30_flag` is set integrates energies the smooth
  curve makes no claim for; use a measured MACS there.

## Provenance (2026-10-23)

- Engine: engine-20261022-3 = nucleus 16606b356d6e (FASTGATE --full PASS), production settings.
  - The 250 reference nuclei are the stored reference product.
  - The other nuclei were run with the reference campaign's runner and environment, with structure-line inputs from
    the chart-wide production table.
  - Combination rules are the production composer's: 182 nuclei JS(P,A), 56 A(rotor), 38 actinide A(rotor), 39 with
    the FEW->mean rule, the rest P.
- Runs: 5,900 nuclei plus 114 second-variant runs. Laptop, Mac mini and MacBook Air, 1 h 46 min wall, 0 failed runs.
  The stock TALYS program was not used.
- No evaluated-library value enters. No TERRA value, no per-nucleus tuned correction and no trained model enters.
- v0.1 is unchanged in `library/v0.1`.
