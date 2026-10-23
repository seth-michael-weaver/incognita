# Scoreboard data

The numbers behind the [scoreboard](../../scoreboard.html), so that anyone can check them. Section 1 of the board (the
INCOGNITA engine against other reaction codes) can be recomputed from the files in this folder, down to the
95 % intervals. Section 2 (the TERRA data product against evaluated libraries) is listed cell by cell, but cannot be
recomputed from this folder (see [What is not here](#what-is-not-here)).

- Engine board: production engine `engine-20261022-3`, 23 October 2026. Its TALYS rival is the TALYS-2.24 program
  at default input (stored runs, scored 23 October 2026); the project's port of TALYS-2, the TALYS rival before that
  date, is still listed as `TALYS-port` but not counted. Counted: 47 WIN / 19 TIE / 0 LOSS, 14 N/A.
- TERRA board: product R072w, 11 October 2026, on an older engine. Counted: 217 WIN / 108 TIE / 1 LOSS, 28 N/A.

These are **development comparisons**. The engine's global rules were chosen while watching these same comparisons,
and TERRA is scored in-sample except where a row says otherwise. Neither board is a blind test.

The measurements were curated by this project: of the 6,425 measurement rows in `d_rows.csv.gz`, 985 are not scored
(776 excluded by the project's curation register, 143 for documented defects, 66 MACS labels that are estimates), and
each capture row is a trust-weighted consensus of the EXFOR datasets in its energy bin (502 dataset entries
down-weighted, 221 excluded; see `measurements.csv.gz`).

## Files

| File | Size | What it is |
|---|---|---|
| `cells.csv` | 67 kB | Every comparison: 140 engine cells (80 data-view cells + 60 MACS-band cells, five rivals; 80 of them counted on the board, 14 of those as N/A; the 20 empty-band cells are listed but not counted) and 354 TERRA cells (326 counted, 28 N/A). One row per (view, rival). |
| `d_pernuc.csv` | 197 kB | Data views: for each view, rival and nucleus, the weighted sums each score is built from. Enough to recompute every gap and interval. |
| `d_rows.csv.gz` | 447 kB | Data views: every measurement row (6,425), with our residual, each rival's residual, the weight, and whether the row is scored. `d_pernuc.csv` is built from these. |
| `k_pernuc.csv` | 22 kB | MACS bands: for each of 185 nuclides, our error and each rival's (dex), its Z band, and whether it is scored. |
| `measurements.csv.gz` | 119 kB | The EXFOR measurements each scored row rests on, by EXFOR entry and subentry, with energy, value, uncertainty and the curation decision. |
| `recompute.py` | 12 kB | Recomputes every engine cell from these files and checks the result against `cells.csv`. |

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
--rows: d_pernuc.csv rebuilt from d_rows.csv.gz: 1808 nucleus entries, same nuclei and order, max relative difference 8.7e-12
engine cells recomputed: 140 (20 of them empty MACS bands, not counted); counted on the board: WIN 47, TIE 19, LOSS 0, N/A 14
max |difference| vs cells.csv over gap, scores, CI ends: 4.6e-10 dex (tolerance 1e-08)
REPRODUCED
```

Every verdict, N/A reason, nucleus count, score, gap and interval end in `cells.csv` is reproduced within 1e-8 dex.
The remaining differences come from the files being written to 10–12 significant digits. The counted totals,
47 WIN / 19 TIE / 0 LOSS / 14 N/A, are the board's.

Without numpy the gaps are still exact, but the bootstrap uses Python's own random generator, so the interval ends
move slightly. In our run (same files, numpy hidden) the counted totals are unchanged and one listed, uncounted
verdict differs: `macs_Zge20` against `TALYS-port`, whose interval ends at −0.0014, which shows how close to zero
that interval is.

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
is `sqrt(mean err²)` over the band's scored nuclides: the 104 whose compiled value is a measurement, not an estimate (97 against TALYS-2.24, which has no stored value for the other 7; Zr-95 is also left out, for a documented defect). The bands Z < 20 and Z ≥ 84 contain no such nuclide, so they are not comparisons: they are listed with `na_reason` = `empty band` and not counted (until 23 October 2026 they were counted as N/A).

**Gap.** `gap = score_ours − score_rival`. Negative means we are closer to the data.

**95 % interval.** This is a paired nucleus bootstrap. Resample the nuclei with replacement (2,000 times), recompute
both scores on each resample, and take the 2.5th and 97.5th percentiles of the gap. "Paired" means both codes are
scored on the same resample. The random seeds are 20261001 (data views) and 20261004 (MACS bands), using
numpy's `default_rng`, with nuclei in the order they appear in `d_pernuc.csv` (`order` column) and `k_pernuc.csv`.

**Verdict.**

- **WIN** if the interval's upper end is below 0.
- **LOSS** if its lower end is above 0.
- **TIE** otherwise.
- **N/A** (not counted), whatever the verdict above would be, when
  - the rival has no values for the view (`na_reason` = `rival gives no value`);
  - 5 or fewer nuclei can be scored (`too few nuclei`); or
  - the rival's score exceeds 1 dex, a factor of 10, which means its run failed rather than its physics
    (`rival run failed`).

  These cells keep their gap, interval and scores in `cells.csv`. The rule was tightened on 23 October 2026 (before:
  N/A only below 3 nuclei or without rival values); it moved five counted fission cells to N/A: `fission_SELECT`
  against CoH3 (WIN, 5 nuclei), TALYS-2.24 (TIE, 5) and YAHFC (TIE, 4); `SURR fission_SELECT` against CoH3 (WIN, 5)
  and YAHFC (WIN, 5 nuclei, YAHFC error 6.6 dex: rival run failed). The uncounted `fission_SELECT` against
  `TALYS-port` (TIE, 5) moved too.

The TERRA board keeps the rule it was scored with: N/A with 3 or fewer nuclei for the plain accuracy cells, fewer
than 5 for the series-aware and uncertainty-coverage cells (`na_reason` = `too few nuclei`).

A tie is not a win. Some comparisons reuse the same measurements (for example `n2n_step1` is a second scoring of the `thrA1_n2n` rows), so the 66 counted comparisons are not independent; no correction for multiple comparisons is applied.

## The rivals (engine board)

All are class A: model calculations compared on equal terms. The engine is not scored against evaluated libraries,
which are fitted to the same measurements.

- **TALYS-2.24**: the TALYS program, version 2.24, at default input, from runs we made and stored earlier (no new
  runs were made for the board). The program is MIT-licensed. Its results were stored only on its 64-point energy
  grid (steps of about 17 %), and are read between those points by log-log interpolation. That matters only for
  (n,2n), which rises steeply above its threshold: there the four cells against TALYS-2.24 compare our own curves put
  through the same 64-point grid (`r_ours_talysgrid`), so both codes carry the same grid error. On the census grid
  instead (`r_ours` against the interpolated program) those four cells would be WINs (gaps −0.046 to −0.053), and
  most of that would be the program's grid, not physics; they are not counted that way. Capture, MACS and fission
  rows sit on grid points (no grid effect); for (n,p) and (n,α) the grid effect is 0.008–0.013 dex rms and moves
  no verdict, so those cells use `r_ours`. Coverage: every data view has all its nuclei except `macs_Zge20`
  (68 of 70); the MACS bands have 97 of 104 nuclides.
- **TALYS-port** (listed, not counted): TALYS-2 default input computed with this project's port of TALYS-2, the
  rival called "stock" on the board until 23 October 2026. On the same rows the port matches the program to
  ≤ 0.002 dex rms for capture, MACS and fission, and to 0.013–0.023 dex rms for (n,p) and (n,α) (part of which is
  the program's grid); its cells give the same verdicts as the program's, except the four (n,2n) cells, which the
  port, computed on the census grid, wins.
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
| `verdict` | WIN / TIE / LOSS / N/A (after the N/A rule; see [The statistic](#the-statistic)) |
| `counted_on_board` | Engine: the K126 bands are a second label set; restricted to measured values it holds the same nuclides as K185, so they are listed but not counted; `TALYS-port` cells and empty MACS bands are listed but not counted; counted N/A cells are counted as N/A. TERRA: N/A cells are not counted |
| `scoring` | in-sample, or leave-one-series-out (TERRA refitted without the series being judged; libraries stay in-sample). On the TERRA board 32 counted cells are leave-one-series-out: 28 uncertainty-coverage cells and the 4 `THX I_g` (capture resonance integral) cells. The 8 `THX sigma_th` cells keep "[LEO-series]" in their names but have been scored in-sample (TERRA's shipped estimator on all series, as the libraries are) since 8 October 2026 |
| `ours_residual` | Engine: which of our columns the cell uses: `r_ours`, `r_ours_talysgrid` (the four (n,2n) cells against TALYS-2.24) or `err_ours` (MACS bands) |
| `na_reason` | Why a cell is N/A: `rival gives no value`, `too few nuclei`, `rival run failed` or `empty band` (a MACS band with no scored nuclide; not counted); empty when the cell is scored |

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
| `r_ours`, `r_TALYS-2.24`, `r_TALYS-port`, `r_R_T`, `r_CoH3`, `r_YAHFC` | The residuals, in dex. Empty where a code has no value |
| `r_ours_talysgrid` | Our residual with our curve sampled on the TALYS program's 64-point grid and interpolated the same way as the program's; used only for the (n,2n) cells against TALYS-2.24 |

### `d_pernuc.csv`

| Column | Meaning |
|---|---|
| `view`, `rival`, `nucleus` | Which comparison and nucleus |
| `order` | The nucleus's position in the bootstrap |
| `agg` | How the view combines nuclei |
| `rows` | Rows counted for this nucleus |
| `W` | `Σ w` over those rows |
| `S_ours`, `S_rival` | `Σ w r²` for ours (from the cell's `ours_residual` column) and for the rival |
| `rms_ours`, `rms_rival` | The per-nucleus errors, `sqrt(S/W)`, in dex |

### `k_pernuc.csv`

| Column | Meaning |
|---|---|
| `nucleus`, `Z`, `A` | The nuclide |
| `z_band` | Its Z band |
| `in_K126` | Whether it is in the 126-nuclide label set |
| `in_scope` | Whether it is scored. It is not when its compiled value is an estimate or has a documented defect |
| `err_ours`, `err_TALYS-2.24`, `err_TALYS-port`, `err_R_T`, `err_CoH3`, `err_YAHFC` | `log10(code MACS / compiled MACS)` at kT = 30 keV, in dex |

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
