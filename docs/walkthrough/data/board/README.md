# Scoreboard data

The numbers behind the [scoreboard](../../scoreboard.html), so that anyone can check them. Section 1 of the board (the
INCOGNITA engine against other reaction codes) can be recomputed from the files in this folder, down to the
95 % intervals. Section 2 (the TERRA data product against evaluated libraries) is listed cell by cell, but cannot be
recomputed from this folder (see [What is not here](#what-is-not-here)).

- Engine board: census `BOARDREFRESH`, production engine `engine-20261022-3`, 23 October 2026.
- TERRA board: product R072w, 11 October 2026.

These are **development comparisons**. The engine's global rules were chosen while watching these same comparisons,
and TERRA is scored in-sample except where a row says otherwise. Neither board is a blind test.

## Files

| File | Size | What it is |
|---|---|---|
| `cells.csv` | 61 kB | Every comparison: 112 engine cells (64 data views + 48 MACS bands; 88 of them counted on the board) and 354 TERRA cells. One row per (view, rival). |
| `d_pernuc.csv` | 150 kB | Data views: for each view, rival and nucleus, the weighted sums each score is built from. Enough to recompute every gap and interval. |
| `d_rows.csv.gz` | 370 kB | Data views: every measurement row (6,425), with our residual, each rival's residual, the weight, and whether the row is scored. `d_pernuc.csv` is built from these. |
| `k_pernuc.csv` | 20 kB | MACS bands: for each of 185 nuclides, our error and each rival's (dex), its Z band, and whether it is scored. |
| `measurements.csv.gz` | 119 kB | The EXFOR measurements each scored row rests on, by EXFOR entry and subentry, with energy, value, uncertainty and the curation decision. |
| `recompute.py` | 11 kB | Recomputes every engine cell from these files and checks the result against `cells.csv`. |

The `.gz` files are gzip-compressed CSV; Python, R and spreadsheet tools read them directly, or run `gunzip`.

## Check it yourself

```bash
python3 recompute.py              # gaps and 95 % intervals from d_pernuc.csv and k_pernuc.csv
python3 recompute.py --rows       # first rebuild d_pernuc.csv from the per-row residuals in d_rows.csv.gz
python3 recompute.py --table      # print every engine cell
```

It needs Python 3 and nothing else; with numpy installed the intervals come out the same as the board's. Our run
(Python 3.12, numpy 1.26) prints:

```
--rows: d_pernuc.csv rebuilt from d_rows.csv.gz: 1405 nucleus entries, same nuclei and order, max relative difference 8.7e-12
engine cells recomputed: 112; counted on the board: WIN 54, TIE 17, LOSS 0, N/A 17
max |difference| vs cells.csv over gap, scores, CI ends: 4.6e-10 dex (tolerance 1e-08)
REPRODUCED
```

Every verdict, nucleus count, score, gap and interval end in `cells.csv` is reproduced within 1e-8 dex. The
remaining differences come from the files being written to 10–12 significant digits.

Without numpy the gaps are still exact, but the bootstrap uses Python's own random generator, so the interval ends
move slightly. In our run one verdict then differs (`macs_Zge20` against stock, whose interval ends at −0.0014),
which shows how close to zero that interval is.

## The statistic

**Residual.** For a measurement row, a code's residual is `r = log10(code / measured)`, in dex. 0.01 dex is about 2.3 %.

**Weight.** Each row has weight `w = 1 / (0.1² + u²)`, where `u` is the row's measurement uncertainty in dex.

**Score of a code on a data view.** For each nucleus *i*, add up `S_i = Σ w r²` and `W_i = Σ w` over its scored
rows. The view's `agg` column then says how nuclei are combined:

- `rows`: `score = sqrt(Σ_i S_i / Σ_i W_i)`. Every row counts by its weight, so nuclei with many points weigh more.
- `nucw` (fission, MACS): `score = sqrt(mean_i (S_i / W_i))`. Every nucleus counts equally.

A row counts for a comparison only when both codes have a finite residual there, so both codes are always scored on
the same rows and nuclei.

**Score on a MACS band** (block K). For each nuclide, `err = log10(MACS_code(30 keV) / MACS_compiled)`. The score
is `sqrt(mean err²)` over the band's scored nuclides.

**Gap.** `gap = score_ours − score_rival`. Negative means we are closer to the data.

**95 % interval.** This is a paired nucleus bootstrap. Resample the nuclei with replacement (2,000 times), recompute
both scores on each resample, and take the 2.5th and 97.5th percentiles of the gap. "Paired" means both codes are
scored on the same resample. The random seeds are 20261001 (data views) and 20261004 (MACS bands), using
numpy's `default_rng`, with nuclei in the order they appear in `d_pernuc.csv` (`order` column) and `k_pernuc.csv`.

**Verdict.**

- **WIN** if the interval's upper end is below 0.
- **LOSS** if its lower end is above 0.
- **TIE** otherwise.
- **N/A** when fewer than 3 nuclei can be scored, or the rival has no values for the view.

A tie is not a win. The counts on the board apply no correction for multiple comparisons, and several views overlap.

## The rivals (engine board)

All are class A: model calculations compared on equal terms. The engine is not scored against evaluated libraries,
which are fitted to the same measurements.

- **stock**: TALYS-2 default input, computed with this project's port of TALYS-2. It is not the TALYS program itself.
- **R_T** ("recipe R"): this project's reproduction, in its own engine, of the recipe TENDL uses for nuclei without
  fitted inputs. It is not the TENDL library.
- **CoH3** (3.6.1) and **YAHFC** (3.67): independent Hauser–Feshbach codes that we ran at their default input. Their
  authors did not tune them. By default YAHFC emits no alpha particles, so it has no (n,α) comparisons.

## Columns

### `cells.csv`

| Column | Meaning |
|---|---|
| `section` | `engine` (board section 1) or `terra` (section 2) |
| `block` | Engine: `D` = data view, `K` = MACS band. TERRA: the family of the cell (accuracy, series-aware, uncertainty coverage, …) |
| `view` | The data view or band. For engine views, `SURR <view>` is the same view scored on rows from surrogate-reaction measurements |
| `rival` | The rival code or library |
| `n_nuclei`, `n_rows` | Nuclei and measurement rows scored in the cell |
| `score_ours`, `score_rival` | The two scores (dex; engine cells only) |
| `gap`, `ci_lo`, `ci_hi` | The gap and its 95 % interval |
| `verdict` | WIN / TIE / LOSS / N/A |
| `counted_on_board` | Engine: the K126 bands are a second label set with the same verdicts as K185, so they are listed but not counted. TERRA: N/A cells are not counted |
| `scoring` | in-sample, or leave-one-series-out (TERRA refitted without the series being judged; libraries stay in-sample) |

TERRA cells hold the gap and interval exactly as the TERRA board recorded them. What the gap measures depends on the
family:

| Family | Statistic | Unit |
|---|---|---|
| accuracy | RMS of log10 residuals | dex |
| `SA` (series-aware) | Nucleus-mean χ² with extra per-series scatter | — |
| `COV-IS` | Interval score of the uncertainty bands | — |
| `COV-CE` | Coverage error of the bands against their nominal 68 % / 95 % | — |

In every family, lower is better for TERRA, and the verdict rule is the same.

### `d_rows.csv.gz`

| Column | Meaning |
|---|---|
| `view` | The data view |
| `nucleus` | The target nucleus |
| `row` | The row's id in the view |
| `e_ev` | Incident neutron energy (eV). For `macs_Zge20`, the Maxwellian temperature kT (eV) |
| `agg` | How the view combines nuclei (see above) |
| `capture_bin` | Energy bin of a capture row (links to `measurements.csv.gz`) |
| `exfor_subentries` | The EXFOR subentry or subentries the row comes from (point views) |
| `label_log10` | The measured value the row is scored against: log10 of the cross section, in barns (`unit` = `b`, capture views) or millibarns (`mb`, others). Empty for `macs_Zge20` (see below) |
| `u_dex` | The row's uncertainty, in dex |
| `weight` | The row's weight, `1 / (0.1² + u_dex²)` |
| `status` | `scored` (counts in the view); `scored_surrogate` (counts in the `SURR` view); `excluded_curation` (excluded by the project's EXFOR curation register, `data/curation/` in the repository); `excluded_data_defect` (removed for a documented defect in the measurement); `excluded_estimated_label` (MACS label that is an estimate, not a measurement) |
| `r_ours`, `r_stock`, `r_R_T`, `r_CoH3`, `r_YAHFC` | The residuals, in dex. Empty where a code has no value |

### `d_pernuc.csv`

| Column | Meaning |
|---|---|
| `view`, `rival`, `nucleus` | Which comparison and nucleus |
| `order` | The nucleus's position in the bootstrap |
| `agg` | How the view combines nuclei |
| `rows` | Rows counted for this nucleus |
| `W` | `Σ w` over those rows |
| `S_ours`, `S_rival` | `Σ w r²` for ours and for the rival |
| `rms_ours`, `rms_rival` | The per-nucleus errors, `sqrt(S/W)`, in dex |

### `k_pernuc.csv`

| Column | Meaning |
|---|---|
| `nucleus`, `Z`, `A` | The nuclide |
| `z_band` | Its Z band |
| `in_K126` | Whether it is in the 126-nuclide label set |
| `in_scope` | Whether it is scored. It is not when its compiled value is an estimate or has a documented defect |
| `err_ours`, `err_stock`, `err_R_T`, `err_CoH3`, `err_YAHFC` | `log10(code MACS / compiled MACS)` at kT = 30 keV, in dex |

### `measurements.csv.gz`

One line per EXFOR source of each scored row.

**Point views** ((n,2n), (n,p), (n,α), fission). Each row is one EXFOR point:

- `exfor_subentry`: where the point comes from.
- `value`: the measured cross section, in `unit`.
- `unc_dex`: its uncertainty, in dex.
- `decision`: `kept`.

**Capture views.** Each row is a consensus over every EXFOR dataset with data in that energy bin. The bin has one
line per dataset:

- `e_lo_ev`, `e_hi_ev`: the dataset's energy range in the bin.
- `n_points`: how many of its points fall in the bin.
- `value`: their mean cross section, in barns.
- `trust`: the curation weight, from 0 to 1.
- `decision`: one of the following.
  - `kept`.
  - `down-weighted`: the curation register lowered its trust.
  - `excluded`: removed for a documented defect. The consensus was recomputed without it.

The consensus weights each dataset by its trust and its uncertainty, with extra scatter added where datasets
disagree. The per-dataset uncertainties are not in this package, so `recompute.py --labels` can only compare each
label with a trust-weighted mean of its datasets. It reports how far apart the two are: they agree within 1e-6 dex
for 924 of 1,495 capture rows, and differ by up to 0.2 dex elsewhere.

EXFOR entries can be looked up at <https://www-nds.iaea.org/exfor/> by entry (5 characters) and subentry
(8 characters).

## What is not here

- **TERRA per-nucleus data.** Recomputing TERRA's cells would need per-point values derived from the evaluated
  libraries (ENDF/B-VIII.1, JEFF-4.0, JENDL-5, TENDL-2025). This repository does not redistribute evaluated-library
  values, so only the cells are given.
- **The compiled MACS values** that the `macs_Zge20` view and the K bands are scored against. They are not
  redistributed, as elsewhere in this repository. Their residuals and errors are given, and each nuclide's
  compiled source can be looked up by name. The `macs_Zge20` rows have no EXFOR identifier for the same reason.
- **The engine's sensitivity variants.** The census also scores two variants of how documented data defects are
  applied. Only the headline view, the one on the board, is published here.
- **No held-out or sealed measurements** are in this package. Every row is from the development set the board is
  scored on.

## Licence

Data files (`*.csv`, `*.csv.gz`, this README) are licensed under CC BY 4.0; `recompute.py` is under Apache-2.0. See
`LICENSE-DATA` and `LICENSE` at the repository root. The measurement values and identifiers in
`measurements.csv.gz` and `d_rows.csv.gz` come from the EXFOR library (IAEA Nuclear Data Section and the NRDC
network), which the IAEA distributes under CC BY 4.0. Cite N. Otuka et al., Nucl. Data Sheets 120 (2014) 272,
alongside Incognita (`CITATION.cff`).
