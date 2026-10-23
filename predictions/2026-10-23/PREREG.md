# Scoring rule for the predictions registered on 2026-10-23

This rule was fixed before any measurement of any target was looked at. It does not change after data appear.

## 1. What is registered
- For every target in `targets.csv`: the full predicted curve of every model (`curves.csv.gz`; 1 keV–20 MeV on the engine grid,
  or Maxwellian-averaged cross sections at kT = 5–100 keV), headline values (`cells.csv`), and a table over the expected
  measurement range (`predictions/<target>.csv`). All values in millibarn.
- INCOGNITA: engine version 2026-10-22, run with its production settings. Its 68 % and 95 % bands are given per point
  (`INCOGNITA_lo68`, `INCOGNITA_hi68`, `INCOGNITA_lo95`, `INCOGNITA_hi95`; `INCOGNITA_band_calibrated` says whether the band of
  that channel was calibrated on past data).
- TERRA_TUNED: our evaluated product, adjusted per nucleus to the EXFOR data available before 2026-10-23, where it exists. Its
  `sd_fit` is the fit uncertainty only; it is not scored as a predictive band.
- Model rivals, all frozen in the same files: TALYS-2 at default input (our port of the TALYS-2 default recipe;
  `TALYS2_default_via_port`), the TALYS-2.24 program at default input where a stored run exists (`TALYS-2.24_program`), the TENDL
  no-data recipe (`TENDL_nodata_recipe_via_port`, R_T), CoH3 and YAHFC at default input where available, NON-SMOKER (capture), and
  BRUSLIB (Maxwellian averages; a stellar rate, flagged).
- Evaluated libraries (ENDF/B-VIII.1, JENDL-5, JEFF-4.0, TENDL-2025) are shown for context. They were adjusted to data, so they
  are never used to decide a win or a loss.

## 2. Which measurements count
- The registration time is the time of the public git commit that added this directory.
- A measurement counts for a target if its first public appearance with numbers (journal online date, arXiv v1, EXFOR release,
  thesis, or a public talk or proceedings showing values) is after the registration time.
- Every target has a class (`class` in `targets.csv`), set by an independent check of public sources on 2026-10-23, before
  publication and before any measured value was looked at:
  - `BLIND`: measured or under analysis, no values public. **Only these targets enter the headline (section 5).**
  - `PRELIM` (PRELIM-PUBLIC): preliminary values or first results were shown in public before registration (we did not look at
    them). Scored by the same rule, reported in a separate table, never in the headline.
  - `CONTROL`: the quantity is already well measured, or first results were published before registration. The frozen
    predictions stay on record and are scored as controls in a separate table; not a blind test.
  - `PLANNED`: the measurement is only planned. Long shots: scored in a separate table if the data appear.
  A class never changes after the data of that target appear; the only later change allowed is VOID (cancelled experiment).
- Every qualifying measurement of a registered nucleus and reaction counts, not only the experiment named in `targets.csv`.
- We use the authors' final values (EXFOR when compiled, else the paper's tables). Ratio measurements are converted with the IAEA
  neutron standards at the same energy, identically for every model.
- A spectrum-averaged measurement (quasi-Maxwellian activation) is compared with the Maxwellian average of each model's registered
  curve at the authors' kT, or with its average over the authors' stated spectrum; the same integral for every model.
- Indirect capture results (beta-Oslo, surrogate) are scored like direct ones but reported in their own column.
- Points outside the registered energy range are dropped. The headline also drops points below the resolved-resonance limit
  (`rrr_upper_ev`; models give resonance averages there) unless the measurement is averaged over bins at least 20 % wide, and
  capture points above 10 MeV.

## 3. Statistic
- For each point and model: e = log10(predicted / measured). The prediction is read off the registered curve by linear
  interpolation in ln E (ln kT) of log10 σ, with no extrapolation. A point a model does not cover is "not covered", never imputed.
- Each dataset has total weight 1 within its target. For a target, S(model) = weighted root-mean-square of e over the points both
  INCOGNITA and the rival cover.

## 4. Per-target result (for each rival)
- d = S(INCOGNITA) − S(rival). Tolerance τ = max(0.02, log10(1 + u)), where u is the dataset's stated normalisation or systematic
  relative uncertainty (5 % if none is stated).
- WIN if d < −τ, LOSS if d > +τ, otherwise TIE. Also reported against the best-scoring model rival for that target.

## 5. Overall result (the headline)
- For each rival, over all scored `BLIND` targets it covers (each target weight 1): Δ = rms(INCOGNITA) − rms(rival), with a paired
  bootstrap over nuclei (2,000 draws, seed 20261023). WIN if the upper end of the 95 % interval is below 0, LOSS if the lower end
  is above 0, otherwise TIE.
- No overall verdict until at least 5 `BLIND` targets on at least 5 nuclei are scored; before that, results are descriptive. The verdict
  is taken at the first read that meets this bar; later reads are added with their date and never replace it.
- Also reported: the count of per-target wins and losses (sign test), and the fraction of measured points inside the INCOGNITA
  68 % and 95 % bands (aim: 68 ± 5 % and 95 %).
- `PRELIM`, `CONTROL` and `PLANNED` targets get the same per-target results (section 4) and the same pooled statistic, each class in
  its own table; these pooled lines are descriptive and never replace or join the headline.

## 6. What we will not do
- Edit these files; drop a target after its data appear (a cancelled experiment is marked void, with the date, before any of its
  values are known); choose rivals, energy windows or weights after seeing data; or rerun a model after the data are public and
  call that a prediction. A newer engine gets a new dated directory; this one stays.
