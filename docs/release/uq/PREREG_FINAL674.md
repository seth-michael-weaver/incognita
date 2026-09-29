# FINAL-674 coverage test: pre-registration (amended 2026-09-23, before any prediction on these bins is computed or read)

**What is tested.** The shipped interval rule's coverage on 674 post-2012 measurements of 51 nuclei. The predictions come from a
model that never saw those nuclei: the INDEP recipe of v0.1 in the blind protocol, i.e. leave-contiguous-fold-out over 8 folds.
In each fold the held nucleus gets trust 0, a bare Stage B, its MACS masked and its D0 used, with 3 seed offsets x 5 members.

**Why amended.** The test was registered on 2026-09-21 (TIERS.md "FINAL TEST") against "the release model". v0.1's measured-nucleus
curves are trained on all data up to 2026, so on the shipped library these 674 bins are training points. That version is
retired as evidence: it would measure the interval width on fitted points, not calibration. The owner changed to UQWEEK when
the shipping model changed under the independence policy (INDEP_FIX).

**Inputs, hashed.**

| file | sha256 |
|---|---|
| 674-bin set (frozen keys of 2026-09-19, today's measured values) `674_bins.parquet` | 80c0f6e060f298eb59be4102c37bcb9f631764a33322a5dea5d664ae9491128d |
| frozen key list `blind_keys.json` (674 keys) | c69b1f1bfcbf3521d1a6a6cc7ee108c56c4658b9f10a2dc767e0d3b0cd20e1e9 |
| exporter `export_674_bins.py` | ed21d4dea8f9b7acaf988e8fd60e3aa7ebc3716369f179b6ba2378b286f77f3b |
| folds 6-7 runner `final674_vault_folds.py` (INDEP exam copy; only the fold guard changes, and no DEV-cell rows are written) | 6ce1bd896791fa80ab8d99477c0bfa24411233d2ddabdd137feb926fafc7f0b0 |
| INDEP exam (folds 0-5 predictions, stored) `indep_exam.py` | 4bb052144938aa7de211e763246d2ac96fc019cf0b01d8dcdf0195026622a9c2 |
| scorer `final674_score.py` (runs once, refuses a second run) | 4e32653a3d04c8d656e0fcaa370f4893e48d4751bd3d29b104bf6c216f1b1f69 |

Reconstructing the set today gives 683 bins. The 9 keys outside the frozen list are dropped, and no frozen key is missing.
There are 541 bins in folds 0-5 and 133 in folds 6-7; 138 bins are actinides (Z > 82: U-238, Th-232, U-236).

**Interval.** The shipped rule, with v3 sigma features computed exactly as the INDEP exam computes them.
- PRIMARY = the INTERPOLATED-tier rule (v3 sigma x v4 multipliers): what v0.1 attaches to a blind model prediction.
- SECONDARY = the MEASURED rule (v3 x q68 / q95): the README headline rule on leave-nucleus-out rows.

**Pass rule (unchanged from 2026-09-21).** PRIMARY, all 674 bins: 68 % coverage within 60-76 % AND 95 % coverage within 91-99 %.

**Reported, not gated.**
- the Z <= 82 subset (the rule's domain is Z 26-83)
- region, fold, energy band (< 10 keV, 10-100 keV, 0.1-1 MeV, 1-10 MeV, > 10 MeV; < / >= 5 MeV) and per nucleus
- nucleus-bootstrap CIs, PIT, ECE and sharpness, from the same single read, via `incognita/uq/calibration_report.py`

Nothing is tuned or rerun after the read. A FAIL is reported as it is. The log row is in the lab's BLIND_LOOKS.md (2026-09-23,
"UQWEEK FINAL-674 — AMENDMENT").

## Amendment 2 (2026-09-23 16:30, before any prediction on these bins)
The target recipe becomes the library named in the lab's `INDEP_FINAL.flag` (INDEP_FIX2), replacing INDEP_FIX, whose library had
known defects. INDEP_FIX's stored fold 0-5 predictions are therefore not used: all 8 folds are run with INDEP_FIX2's own exam code
and flags. The bins, the interval rule, the pass band and the outputs are unchanged. An earlier folds 6-7 attempt on the INDEP_FIX
recipe died within a minute and wrote no predictions. Nothing has been computed on the bins.

## Companion read: RETRO-MEASURED (registered 2026-09-23 16:40, before any interval is computed on these rows)
This tests the MEASURED-tier interval, the one v0.1 ships for the ~225 measured nuclei (v3 sigma × v3 q68 / q95, as
`library_uncertainty` builds it), on post-cutoff measurements. The rows are retrodiction rows: the model is trained on data up
to year Y and scored on measurements published after Y, for Y = 2015 / 2017 / 2019 / 2021 / 2023. PRIMARY = the 286 rule-P-clean
rows (16 nuclei); SECONDARY = all 365. The model is the final library's retrodiction recipe (3 × 5 members), rerun to save the
per-member curves and head outputs. The features follow the library's chart run; the one stated difference is 3 seeds here
instead of 10. The pass band is 60-76 / 91-99. The point errors of these rows have been read before; no interval has been fitted
or chosen on them. With 16 nuclei, a PASS is weak evidence and a FAIL is informative. One read.
