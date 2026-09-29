# Are INCOGNITA's uncertainty intervals calibrated? The claim and the evidence

*UQWEEK, 2026-09-23/24. Every number is quoted from a logged, pre-registered read (lab log `BLIND_LOOKS.md`) or regenerated
by `python -m incognita.uq.calibration_report` from files shipped in `docs/release/exam/`. Each number is tagged
**VERIFIED** (regenerated here from shipped files, or read once under a registration) or **REPORTED** (quoted from a lab
write-up and not regenerated here). An inference is labelled as one.*

## The claim, in one paragraph

For **neutron capture below 1 MeV**, INCOGNITA's intervals **contain measurements the model never saw at or above their nominal
rate**, pooled over the two sealed tests. At 95 % they are close to nominal on those pooled tests, **but not on the shipped model's own sealed read: on the vault (folds 6–7, D0 withheld) the 95 % interval covered 88.1 %** (INDEP_FIX2, registered; the release candidate 91.6 %), and at 1–10 MeV 90 % (REDTEAM M1). At 68 % they are conservative: on the two sealed tests, the 68 % interval covered 75.5 %
(674 post-2012 measurements of 51 nuclei the model was blind to; registered PASS, at the top of its band) and 79.7 % (286 post-cutoff
measurements of 16 measured nuclei; registered FAIL for being too wide).
- For a nucleus with no structure data, our interval covers 66 / 95 % on held-out DEV nuclei, where the field's usual model-spread
  band covers only 47 / 74 %.
- The intervals are **not sharp**: their width barely ranks the errors (sharpness 1.08 on the sealed set; target ≥ 1.5).
- Coverage holds pooled over the chart, not per nucleus or per region.
- At 1–10 MeV the 68 % interval under-covers on the sealed set (52 %).
- Above 5 MeV, for (n,2n), for (n,α), and for the evaluation covariances, we make no calibration claim.

**Wording we can defend:** "On data never used to fit or select them, INCOGNITA's capture intervals cover at least their nominal
rate below 1 MeV (68 %: 75–80 % observed; 95 %: 95–98 %). They are conservative and not sharp."

## 1. Failures and limits first

| where | what we measured | status |
|---|---|---|
| capture above 5 MeV, no-structure interval | 46 % / 67 % (39 cells, DEV, cross-fitted); the field's band 18 % / 31 % | **not calibrated**; nobody is |
| capture above 10 MeV, EXTRAPOLATED interval | 31 % / 69 % (67 rows) | **not calibrated**, stated in the library |
| capture ≥ 5 MeV, shipped TIERS rule on held-out rows (DEV) | 60.7 % / 85.4 % (89 rows, 32 nuclei), bias −0.21 dex | **under-covers** (VERIFIED; in-sample for the interval) |
| per region, not pooled | EXTRAPOLATED fold 4: 39 % / 86 %; ANCHORED fold 0: 50 % at 68; no-structure fold 5: 57 % at 68; TIERS rule Z ≤ 50 vs Z 51–82: PIT slopes of opposite sign (biases −0.03 / +0.03 dex) | **calibrated on average only**: a nucleus in a region where the engine level is off gets a too-narrow interval |
| sharpness | the no-structure interval's rms error is ×1.10 higher in its widest quarter than in its narrowest (target ≥ 1.5); the field's 8-model sd scores 1.01. The TIERS rule scores 1.96 pooled but only 1.08–1.16 within the 10–100 keV and 1–10 MeV bands | **not sharp within a band**: INFERRED, the pooled 1.96 comes mostly from the rule widening with energy, not from ranking nuclei |
| distance from data | HOLE exam at distance 2: 55 % [26, 81] / 85 % (7 nuclei); HOLE-2 neutron-poor side, D0 withheld, d3–4 / d5–6: 61 % / 49 % at 68 | **INTERPOLATED tier is capped at distance ≤ 2** for this reason; the d2 cell is underpowered |
| FINAL-674 (sealed), 1–10 MeV | 52.1 % [36, 68] / 89.6 % (96 bins, 20 nuclei) | **under-covers at 68 %** |
| FINAL-674 (sealed), by fold | fold 2: 57 % / 81 % (10 nuclei); fold 6: 51 % / 87 % (6 nuclei); fold 5: 100 % / 100 % (5 nuclei) | **pooled pass hides fold failures** |
| INTERPOLATED, D0 withheld, vault folds 6–7 (INDEP_FIX2's registered read) | 95 % coverage 88.1 % (RC 91.6 %) | **fails its 95 % clause** (REPORTED, INDEP_FIX2) |
| (n,p), fresh post-cutoff records | shipped frozen interval: 63.5 % / 90.1 % (203 records / 49 nuclei, one registered read, PASS at 68). Only 37.9 % on the 9 cleanest nuclei and 53.3 % on the 19 never seen by the correction | **passes pooled; fails on the nuclei that matter most** |
| (n,p) unmeasured, vault | 59.0 % / 92.9 % (239 rows / 27 nuclei), gate 60–76 | **fail by 1 point** |
| unseen far-field capture (Oslo-method labels) | ours covers 2 of 5 labels at 68 %, 5 of 5 at 95 %; the field's sd band covers 3 of 5 and 4 of 5 | **underpowered (4 nuclei); does not support "ours beats the field" off DEV** |
| evaluation covariances (MF33) | shipped recipe 40–56 % / 63–81 % held out; a recalibration passed (67–69 / 94–95) but is **retracted** (its widths start from the library spread; v0.1 ships no ENDF-6) | no claim |
| (n,2n), (n,α) | no (n,2n) interval ships. The (n,α) registry interval (0.300 / 0.697 dex) is an in-sample quantile and has never been validated | no claim |
| MEASURED tier (the full-data curve of the ~225 measured nuclei), time split (RETRO-MEASURED, sealed for intervals, read once) | 79.7 % [66, 88] / 97.6 % on 286 post-cutoff rows / 16 nuclei; < 10 keV 22 % / 72 % (18 rows, 3 nuclei); 0.1–1 MeV 94 % / 100 %. With the 79 rows from flagged defect datasets included (365 rows): 70.4 / 94.0 | **FAIL, too wide at 68 %** on clean data (the rule was fitted on rows that include defective data); under-covers below 10 keV |
| ANCHORED tier as built (shape width ⊕ the anchor's MACS uncertainty) | validated only with a perfect anchor (u = 0): 68.1 % / 94.5 %, and the band split was chosen post hoc on the same rows | **untested as shipped** |

## 2. The one sealed test: FINAL-674 (pre-registered 2026-09-21, amended before reading on 2026-09-23)

**Design.** The data are 674 capture measurements published after 2012, on 51 nuclei. Every prediction comes from the INDEP recipe
(v0.1's library-value-free model) in the blind protocol: the nucleus's contiguous chart fold is held out entirely (8 folds;
3 seeds × 5 members; D0 used, MACS masked). The interval is the shipped INTERPOLATED rule (v3 sigma × v4 multipliers), with
features computed exactly as the model computes them. The pass band stayed as registered on 09-21: 68 % coverage within 60–76 %
and 95 % within 91–99 %.

**Why it was amended.** The v0.1 curves for measured nuclei are trained on all data up to 2026. On the shipped library these bins
are training points, so the literal 09-21 test would have measured interval width on fitted data. That version is retired, and
the amendment was committed before any prediction was made on these bins (`docs/release/uq/PREREG_FINAL674.md`). Two caveats:
- This set was used for about 34 accuracy (rms) looks in earlier weeks, so it is not pristine for accuracy.
- It has never been used to fit or choose any interval.

**Power.** A synthetic twin of this exam shows that a truly calibrated interval passes 78–91 % of the time, while one 15 % too
narrow still passes 44 %. A PASS here is therefore consistent with calibration, not proof of it.

**Result (read once 2026-09-23 17:11; VERIFIED: `python -m incognita.uq.calibration_report docs/release/uq/final674_rows.parquet --by region fold`
regenerates it from the shipped per-bin rows).** The model is INDEP_FIX2 (`INDEP_FINAL.flag`, library capture sha256 69f956ea…).

| stratum | bins (nuclei) | 68 % [95 % CI] | 95 % [95 % CI] | ECE, pp | sharpness | median h68 / rms error (dex) | bias |
|---|---|---|---|---|---|---|---|
| **all (PRIMARY, INTERPOLATED rule)** | 674 (51) | **75.5** [66.0, 83.7] | **95.3** [90.8, 98.4] | 5.1 | 1.08 | 0.165 / 0.171 | +0.001 |
| Z ≤ 82 (the rule's domain) | 536 (48) | 72.8 [62.0, 82.4] | 94.4 [89.4, 98.1] | 4.2 | 1.03 | 0.158 / 0.175 | +0.017 |
| actinides (U-236, U-238, Th-232) | 138 (3) | 86.2 | 98.6 | 9.1 | 1.50 | 0.190 / 0.153 | −0.059 |
| < 10 keV | 62 (15) | 74.2 [50.8, 97.3] | 91.9 | 11.2 | 1.03 | 0.155 / 0.140 | +0.025 |
| 10–100 keV | 279 (34) | 86.4 [76.6, 94.1] | 98.6 | 9.4 | 0.62 | 0.158 / 0.145 | −0.007 |
| 0.1–1 MeV | 217 (32) | 70.5 [57.0, 82.7] | 94.5 | 3.2 | 0.58 | 0.162 / 0.147 | +0.003 |
| 1–10 MeV | 96 (20) | **52.1** [36.4, 67.8] | 89.6 | 10.0 | 0.83 | 0.216 / 0.262 | +0.017 |
| ≥ 5 MeV | 43 (16) | 76.7 | 95.3 | 13.2 | 0.66 | 0.340 / 0.267 | −0.005 |
| Z ≤ 50 / Z 51–82 | 236 (24) / 300 (24) | 75.8 / 70.3 | 92.8 / 95.7 | – | 1.56 / 0.82 | – | −0.044 / +0.065 |
| SECONDARY: MEASURED rule (v3 × v3 q) | 674 (51) | 70.6 [60.9, 79.8] | 96.1 [92.4, 99.1] | 1.7 | 1.33 | 0.149 / 0.171 | +0.001 |

**Reading.** The registered verdict is PASS. Beyond the verdict:
1. Pooled calibration holds at 95 %, while 68 % over-covers by about 7 points. The interval is roughly 20 % wider than it needs to
   be at 68 % on this set (INFERRED from the PIT hump; not re-tuned, since this was a single read).
2. The width does not rank the errors: within every energy band sharpness is ≤ 1, which means the widest quarter of intervals is
   no worse on average than the narrowest.
3. The biases by region have opposite signs (Z ≤ 50 under-predicted, Z 51–82 over-predicted), so pooling hides region-level
   miscalibration. Fold 2 (57 / 81) and fold 6 (51 / 87) fail on their own.
4. At 1–10 MeV the 68 % interval under-covers.
5. The actinides (3 nuclei, 138 bins) lie outside the rule's domain. They over-cover and pull the pooled 68 % up; the Z ≤ 82 figure
   is 72.8 %.

## 3. Evidence table (capture), by what the data had seen

Set types: CROSS-FITTED = each row is scored by an interval fitted without it (DEV folds 0–5). IN-SAMPLE = the interval was fitted
on these rows. SEALED = read once, never used for fitting or selection.

| tier / interval (ships?) | rows / nuclei | set type | 68 % | 95 % | sharpness | tag |
|---|---|---|---|---|---|---|
| **No structure data** (CAPFAR; ships for 4,602 nuclei) | 1,966 / 126 | CROSS-FITTED (leave-one-DEV-fold-out) | 66.4 [59.6, 73.1] | 95.0 [92.6, 97.0] | 1.10 | VERIFIED (`--preset nostruct`) |

*Two numbers for the same cells:* `reproduce.sh nostruct` (the shipped value, `score_nostruct.py`) gives **65.8 / 95.3 %**, which the README quotes; the CAPFAR preset above gives 66.4 / 95.0 %. The cells are the same; the two scripts differ in the prediction they score (shipped value vs CAPFAR's arm). Likewise above 5 MeV the README's 46 / 64 % and this file's 46 / 67 % come from the two computations; the difference has not been traced.

| ... by band < 10 keV / 10–100 keV / 0.1–1 MeV / 1–10 MeV | 130 / 770 / 765 / 274 | same | 66.9 / 65.7 / 69.5 / 61.7 | 98.5 / 95.2 / 96.3 / 92.3 | 0.77–1.09 | VERIFIED |
| ... ≥ 5 MeV | 39 / 28 | same | **46.2** [27.0, 63.5] | **66.7** [50.0, 81.0] | – | VERIFIED |
| **EXTRAPOLATED** with structure (ships) | 4,858 / 141 | CROSS-FITTED | 65.8 | 93.9 | 1.35 | REPORTED (`extrap_sigma_validation.md`) |
| **INTERPOLATED**, D0 withheld, distance 1 / 2 (ships, d ≤ 2) | 1,445 / 81; 1,763 / 94 | CROSS-FITTED rows, but these nuclei's rows were in the v3 fit | 69 / 71 | 93 / 93 | – | REPORTED (TERRA-SCATTER) |
| INTERPOLATED, INDEP model, DEV | 1,937 / 122 | as above | D0 withheld 77.9, D0 used 81.6 | 94.5 / 97.2 | – | REPORTED (INDEP_FIX; **over-covers at 68**) |
| INTERPOLATED on the TERRA reserve (one read) | 2,472 / 31 | SEALED (weakened: read in aggregate before) | 70 | **90** | – | REPORTED |
| TIERS rule on leave-nucleus-out rows (the README headline 68.4 / 95.2) | 8,662 / 196 | **IN-SAMPLE** for the interval (v3 deploy fit) | 68.4 | 95.2 | 2.08 | VERIFIED (`--preset tiers`) |
| **RETRO-MEASURED, MEASURED rule, INDEP_FIX2 retrained per cutoff year** | 286 / 16 | **SEALED** for intervals (time split) | **79.7** | 97.6 | 1.63 | VERIFIED (`retro_measured_rows.parquet`) |
| **FINAL-674, INTERPOLATED rule, INDEP_FIX2 blind predictions** | 674 / 51 | **SEALED** (never used for any interval) | 75.5 | 95.3 | 1.08 | VERIFIED |
| same rule, honestly cross-fitted (v3 / v3b) | 8,765 | CROSS-FITTED over 8 folds | 68 / 67 | 94 / 94 | 1.49 / 1.36 | REPORTED (OFFLINE D3) |
| ANCHORED (perfect-anchor check) | 4,352 / 95 | CROSS-FITTED, band split post hoc | 68.1 | 94.5 (< 10 keV: 87) | – | REPORTED |

The README's "68.4 / 95.2 % on 8,662 held-out rows" is true of the *predictions*: they are held out. The *interval* was fitted on
those same rows, so the number cannot evidence calibration. The cross-fitted equivalent is 68 / 94. We recommend the README
quote that row, or FINAL-674, instead.

## 4. Against the field's model-spread band

The usual uncertainty for a nucleus without data is the spread across model choices. TENDL-astro, for example, publishes the
spread over its level-density and γ-strength options. We rebuilt the two ingredients TENDL-astro names as dominant (E1 strength
8/9 × level density 1/2/5/7 = 8 TALYS model sets) and scored them against ours on the same 1,966 no-structure DEV cells
(`--preset nostruct`, VERIFIED):

| band | 68 % coverage | 95 % coverage | sharpness |
|---|---|---|---|
| ours (CAPFAR, cross-fitted) | 66.4 [59.6, 73.1] | 95.0 [92.6, 97.0] | 1.10 |
| field: 8-model mean ± 1 / 1.96 sd | **47.2** [39.2, 55.3] | **73.9** [66.5, 80.5] | 1.01 |
| field: min–max of the 8 models | – | **59.1** [51.2, 67.1] | – |

On these cells ours is closer to nominal by 19 points at 68 % [+8.7, +25.9] and 21 points at 95 % [+13.4, +27.2] (nucleus
bootstrap; REPORTED from SPREAD_COVERAGE). Three limits apply:
1. This is a calibration win, not an information win. Our interval is the same spread with a floor and a conformal rescale, and
   neither band ranks the errors (sharpness about 1.0–1.1).
2. It is measured on DEV nuclei with their structure files stripped, not on nuclei far from stability.
3. On the only unseen far-field labels (4 Oslo-method nuclei) the field's band did as well as ours. That set is underpowered, and
   it neither confirms nor refutes the DEV result.

**Wording we can defend:** "On held-out nuclei treated as having no structure data, the conventional model-spread band covers
47 % / 74 % at nominal 68 / 95 %; ours covers 66 / 95 %." We cannot defend: "ours is sharper", or "ours is calibrated far from
stability".

## 5. What is not claimed, and what would close the gaps

- **Per-nucleus calibration.** Coverage is pooled. Fold-to-fold (region) coverage ranges from 39 % to 81 % at 68 %.
- **Above 5 MeV** (all tiers), **(n,2n)**, **(n,α)** and **evaluation covariances.**
- **The MEASURED tier on unseen data** was tested once (RETRO-MEASURED, `docs/release/uq/RETRO_MEASURED.md`, rows
  `retro_measured_rows.parquet`) and **failed by over-covering**: 79.7 % at 68 %. Caveats:
  - The retrodiction models use 3 seeds where the library uses 10, and their median 68 % half-width (0.137 dex) is wider than the
    shipped MEASURED tier's (0.103 dex at 10 keV–1 MeV).
  - The shipped width may therefore cover less than 79.7 % (INFERRED, not tested).
  - 16 nuclei is a small sample.
  So what we can say is "not shown to be calibrated; conservative on this test", not "calibrated".
- **The prospective registries** (capture v0: 2,524 targets; (n,α) v1: 171 targets) hold 0 scored points today. They are the
  held-out set from release on, because the internal vault (folds 6–7) is published with the exam files and retired.

## 6. Regenerating the tables

```bash
python -m incognita.uq.calibration_report --preset tiers    --out tiers.md      # TIERS rule by region / fold / band (in-sample, labelled)
python -m incognita.uq.calibration_report --preset nostruct --out nostruct.md   # no-structure interval vs the field's 8-model band
python -m incognita.uq.calibration_report ROWS.parquet --by region --out my.md   # any table with err (= pred - y, log10) and h68/h95
```

For each stratum the report gives:
- coverage at 68 / 95 % with a nucleus-bootstrap 95 % CI (rows of one nucleus are not independent);
- the PIT histogram;
- ECE, the mean |observed − nominal| coverage over central levels 5–95 %;
- sharpness, the rms error in the widest vs the narrowest quarter of intervals;
- the median half-width and the rms error, so calibration is never read without the width it costs.

The PIT and ECE assume a Student-t through the two quantiles; the coverages do not. Presets never stratify folds 6–7. The
FINAL-674 per-bin rows (`final674_rows.parquet`) run through the same tool.
