# BUGTIER3: tiers, bands and MACS flags of library v0.2.2, and how the site shows them (2026-11-07)

Bug hunt round 3, scoring. Scope: how library v0.2.2 assigns and reports its tiers (MEASURED / ANCHORED /
INTERPOLATED / EXTRAPOLATED), the validated range, the uncertainty bands, the ANCHORED rescaling, the MACS flags and the
MACS and rate tables; the tier display of the Data explorer (`docs/walkthrough/js/data.js`, `data/index.json`); and the
Scoreboard page against `docs/walkthrough/data/board/cells.csv` and `familywise.csv`.

Tests: `tests/test_bugtier3.py`. Site findings are fixed. Library findings that would change a shipped file of
`library/v0.2.2` (its files and docs are checksummed in `SHA256SUMS`) or a published Scoreboard number are drafted
below and not applied. Their tests are `xfail(strict=True)`, so each one fails once its item is applied, and its marker
must then come off.

## What was checked and holds

Over all 6,168 rows of `capture_v022.parquet` and the CSV tables:
- **Bands.** Every `unc68_log10` and `unc95_log10` point is finite, > 0, and u68 ≤ u95 (u95/u68 from 1.67 to 4.49).
  The bands are symmetric half-widths in log10, so every band contains its curve. The (n,p) grid has
  lo95 ≤ lo68 ≤ value ≤ hi68 ≤ hi95 on every row, with no negative values.
- **Factors.** `unc68_factor_30keV` is the 68 % band at E_lab = 30 keV (log-log, to 1e-16).
  - `unc68_factor_<kT>keV` in `macs_kt_v022.csv` is the band at E_lab = kT, as RATES.md says.
  - No factor is < 1 or NaN.
  - `capture_v022.parquet`, `macs30_v022.csv` and `macs_kt_v022.csv` agree on MACS30, its factor, tier, flag,
    `in_validated_range`, `model_form_flag` and `alt_macs30_mb` (to 2e-13).
- **MACS and rates.** Every MACS and rate is finite and positive. The REACLIB residual is above 0.3 dex for 2 nuclides
  (max 0.335).
- **Flags.** `in_validated_range` is exactly Z 26–83. `macs30_flag` (and `macs_flag`) is set exactly where
  `resolved_upper_ev` > 3 keV (545 nuclides).
- **ANCHORED.** Each ANCHORED factor is applied once. The v0.2.2 curve is the v0.2 curve times `v022_extra_factor` at all
  64 points (to 1e-12). Below 1 keV it is the unscaled engine shape times the same total factor (to 1e-9). MACS30
  equals the anchor (6e-16).
- **Model-form widening.** At the grid point nearest 30 keV (31.8 keV), the widened 95 % band contains
  `alt_value_30keV_b` for all 1,131 `pe_kev` / `fists2` nuclides.
- **Site.** For every nuclide, the site's `index.json` and `data/n/<Z>/<A>.json` carry the library's tier, validated
  flag, MACS flag, curve, bands, MACS(kT) and their factors, to their 4 (bands 3) significant digits.
- **Scoreboard.** `scoreboard-data.js` and the inline `WT.boardFW` match `cells.csv` and `familywise.csv`.
  - Counts: engine 47 WIN / 19 TIE / 0 LOSS / 14 N/A, and the same per rival. TERRA 217 / 108 / 1 / 28, per rival
    too.
  - The 19 cells of the not-a-win table and the 13 "read with care" cells match their n, scores, gap and interval
    (4 decimals), verdict and corrected verdicts.
  - Family-wise ranges 24–31 (19 views) and 21–27 (66 cells), the error range 0.063–0.237 dex (16–73 %), the median
    win gap 0.072 dex, and 3 "engine behind" ties.
  - Every WIN / TIE / LOSS label follows its interval, corrected ones included.

Not a defect, noted: **interpolation across shell closures** cannot bias a value in v0.2–v0.2.2. The tier is a label,
and every curve is the engine's own prediction, not interpolated from neighbours. For 20 INTERPOLATED nuclides, every
MEASURED neighbour within 2 sits at or across a magic number (Cu-58..60, Zn-60, Sb-112..118, Te-114..119, Eu-146,
Bi-204..206). If the tier is ever used to pick an interval again, that is worth a look.

## Fixed (site display; no library value or Scoreboard number changes)

| # | finding | where | count |
|---|---|---|---|
| S1 | INTERPOLATED nuclides with kept curated capture cells were labelled "Interpolated. Not measured", with the measurements drawn beside the text. The shown tier now says "Measured (library tier not updated)", as it already did for EXTRAPOLATED ones | `data.js` `shownTier` | 33 |
| S2 | "How far to trust this" said "bands cover as stated" for ANCHORED nuclides. The coverage check behind it scored MEASURED nuclei only; v0.2's own ANCHORED coverage row has 32 points, "too few to read" | `data.js` `trustPanel` | 21 |
| S3 | The ANCHORED text said "No measured cross sections", but 14 of the 21 have kept curated capture cells shown below it: below 1 keV for 11, and at keV energies for Zn-70, Ge-76 and Te-120 | `dx_tr_t1`, 14 languages | 14 |
| S4 | The EXTRAPOLATED text said "not close to measured nuclei". 205 EXTRAPOLATED nuclides in Z 26–83 with structure data are within 2 (\|ΔZ\| + \|ΔN\|) of a MEASURED nucleus, for example Co-60 (Co-59) | `dx_tr_t3`, 14 languages | 205 |
| S5 | The tier-5 text named only "extrapolated"; with S1 it now says "interpolated or extrapolated" | `dx_tr_t5`, 14 languages | |

`docs/GUIDE.md`: a note under the tier table on what the files show about the tier rule (see C and D).

## Amendment drafts (not applied)

| item | finding | files touched | published numbers touched |
|---|---|---|---|
| A | ANCHORED factors are listed from a rounded v0.2 factor | `anchored_rescale_v022.csv`, `value_source` of 5 rows, BUILD.md | none (curves, MACS, rates unchanged) |
| B | `model_form_max_dex_sub1MeV` = 0 for the 3 `gg_deadend` nuclides; `alt_value_30keV_b` is the 31.8 keV value | `capture_v022.parquet` (column), README | none |
| C | tiers disagree with their definition on 60 nuclides with kept keV capture data | `tier` of 60 nuclides, the bands that take a tier interval, every per-tier table | per-tier tables in BUILD.md / VERIFY |
| D | the tier and validated-range definitions in the docs are incomplete | library README, BUILD.md, site texts (done for the site) | none |
| E | 4 TERRA coverage cells are N/A by a "<5 nuclei" label with 5–6 nuclei | `cells.csv`, Scoreboard section 2 | TERRA TIE 108 → 112, N/A 28 → 24 (if the counts are right) |
| F | `macs_flag` uses the 30 keV criterion at every kT | RATES.md, `macs_kt_v022.csv` | none |

### A. ANCHORED factor bookkeeping (`build_library_v022.py`)

**Cause.**
- `main()` reads the v0.2 factor back from the text of `value_source` ("blind curve x 0.817"), which v0.2 wrote with 3
  decimals: `f_old = float(m_old.group(1))`.
- `v02_factor`, `v022_factor = f_old * f` and the new `value_source` text all inherit that rounding.
- The curve does not. It is the v0.2 curve times the exact extra factor `f`.
- The exact v0.2 factor is already in `below1keV_engine_v022.parquet`, column `anchored_v02_factor`. Times `f`, it
  equals σ(1 keV) / engine(1 keV) of the shipped curve to 3e-16.

**Size.** The listed total is off by up to 6.7e-4, relative. In `value_source`, the 3-decimal factor rounds to a
different 3rd decimal for 5 nuclides:

| nuclide | `v02_factor` listed | v0.2 factor of the curve | `v022_factor` listed | factor of the curve | listed / curve − 1 | `value_source` | should read |
|---|---|---|---|---|---|---|---|
| Fe-60 | 0.817 | 0.81733 | 0.81723 | 0.81755 | −4.0e-4 | x 0.817 | x 0.818 |
| Zn-70 | 0.875 | 0.87477 | 0.87509 | 0.87486 | +2.6e-4 | x 0.875 | |
| Ge-76 | 0.631 | 0.63142 | 0.63100 | 0.63142 | −6.7e-4 | x 0.631 | |
| Se-76 | 0.974 | 0.97436 | 0.97332 | 0.97369 | −3.7e-4 | x 0.973 | x 0.974 |
| Pd-102 | 1.267 | 1.26726 | 1.26781 | 1.26807 | −2.1e-4 | x 1.268 | |
| Te-120 | 1.172 | 1.17220 | 1.16850 | 1.16870 | −1.7e-4 | x 1.168 | x 1.169 |
| Xe-126 | 0.963 | 0.96317 | 0.95976 | 0.95994 | −1.8e-4 | x 0.960 | |
| Cs-135 | 1.767 | 1.76710 | 1.75297 | 1.75307 | −5.6e-5 | x 1.753 | |
| Ba-132 | 1.672 | 1.67210 | 1.66445 | 1.66455 | −5.7e-5 | x 1.664 | x 1.665 |
| Ce-136 | 0.971 | 0.97076 | 0.96530 | 0.96506 | +2.5e-4 | x 0.965 | |
| Ce-138 | 0.845 | 0.84469 | 0.84295 | 0.84264 | +3.7e-4 | x 0.843 | |
| Pm-147 | 0.936 | 0.93617 | 0.92652 | 0.92669 | −1.8e-4 | x 0.927 | |
| Eu-154 | 1.016 | 1.01618 | 1.00872 | 1.00890 | −1.7e-4 | x 1.009 | |
| Eu-155 | 0.973 | 0.97264 | 0.96204 | 0.96168 | +3.7e-4 | x 0.962 | |
| Ho-163 | 0.532 | 0.53213 | 0.52697 | 0.52710 | −2.5e-4 | x 0.527 | |
| Hf-174 | 1.144 | 1.14409 | 1.13704 | 1.13714 | −8.2e-5 | x 1.137 | |
| Hf-182 | 0.876 | 0.87635 | 0.87331 | 0.87366 | −4.0e-4 | x 0.873 | x 0.874 |
| Os-184 | 0.616 | 0.61589 | 0.61144 | 0.61134 | +1.7e-4 | x 0.611 | |
| Pt-190 | 0.858 | 0.85841 | 0.85182 | 0.85223 | −4.8e-4 | x 0.852 | |
| Hg-196 | 0.639 | 0.63907 | 0.63469 | 0.63476 | −1.1e-4 | x 0.635 | |
| Tl-204 | 1.332 | 1.33203 | 1.32035 | 1.32038 | −2.2e-5 | x 1.320 | |

BUILD.md's "ANCHORED: new scale factors" table repeats the listed values. For example, Fe-60 "v0.2.2 factor 0.8172"
should read 0.8176.

**Proposed change.**
- In `build_library_v022.py`, take `f_old = LOWE.at[n, "anchored_v02_factor"]`, keeping the text as a cross-check to
  ±5e-4. Then rebuild `anchored_rescale_v022.csv` and the 21 ANCHORED `value_source` strings.
- That changes `capture_v022.parquet`, `macs30_v022.csv` and `macs_kt_v022.csv` (value_source only, 5 rows differ in
  text), the CSV, BUILD.md, SHA256SUMS and VERIFY.
- No σ, band, MACS or rate changes.
- Tests: `test_anchored_rescale_total_factor_is_the_curves_own`, `test_anchored_value_source_factor_rounds_the_true_factor`.

### B. Model-form columns

**`model_form_max_dex_sub1MeV` for `gg_deadend`.** The column is 0.0 for Mo-86, Tc-87 and Rh-105. Their alternative
value at 31.8 keV differs from the curve by 3.59, 1.11 and 2.43 dex, and the README says the move comes from the
dead-end fix. The 0.0 is the "not widened" convention leaking into a column that reads as a measured difference.

Proposed: fill it with the real difference, or NaN with a note. Test: `test_model_form_max_dex_covers_the_alternative`.

**`alt_value_30keV_b` is the alternative at the 31.8 keV grid point, not at 30 keV.**
- At the grid point, the widened 95 % band holds it for all 1,131 flagged nuclides.
- Read against the curve interpolated to 30 keV, it falls outside the band for 326 of them, by 0.014 dex (median) and
  at most 0.023 dex.
- The site already compares it at the grid point. Proposed: say "nearest grid point (31.8 keV)" in the README column
  description. Changing the column would change the file and gains nothing.

### C. Tiers that disagree with their own definition

The tiers are v0.1's and v0.2 kept them ("The tier of every nucleus is the same as in v0.1"). Against the curated
capture set:
- **Both sets agree.** Capture set v2, and v1 too (`data/curation/inputs/exfor_cells.parquet`), give the same list.
- **Not measured by tier, measured in the data.** 57 INTERPOLATED or EXTRAPOLATED nuclides in Z ≥ 26 have kept
  (keep / downweight) capture cross sections at E ≥ 1 keV or measured MACS. By the definition they are MEASURED:
  - INTERPOLATED (21), with the number of keV cells: Co-57 (1), Co-58 (3), Ni-59 (3), Cu-64 (1), Ga-70 (1),
    Ge-68 (1), Kr-85 (1), Tc-98 (2), Ru-99 (1), In-113 (29), I-125 (3), I-126 (1), Xe-133 (1), Xe-135 (3), Cs-134 (1),
    La-138 (1), Eu-152 (1), Dy-158 (1), Hf-181 (1), Ta-179 (1), W-185 (1).
  - EXTRAPOLATED (36): Ni-65 (2), Cu-66 (1), Sr-90 (2), Sr-92 (1), Sr-94 (1), Sr-96 (1), Nb-94 (4), Ru-105 (1),
    Ru-106 (1), Ag-111 (1), Sb-124 (1), I-130 (1), I-131 (2), Cs-137 (2), La-140 (1), Ce-144 (1), Pr-142 (1),
    Pr-143 (1), Pm-148 (1), Pm-149 (1), Gd-148 (1), Dy-165 (1), Tm-170 (1), Tm-171 (4), Lu-177 (1), Ta-182 (1),
    W-187 (1), W-188 (1), Os-193 (1), Au-198 (3), Ac-227 (4), Th-230 (1), Th-233 (1), Pa-231 (4), Pa-232 (2), U-232 (2).
  - Kept data only below 1 keV: As-73, Sn-113, I-128, Xe-131, Ba-133, Sm-145, Yb-169, Lu-173, W-181, Ir-192, Hg-194,
    Pb-205, Co-60, Sn-126, Ba-140, Ir-194, Ra-226 (17). These sit outside the curve's 1 keV–20 MeV range, so the tier
    may stand.
- **ANCHORED with keV cross sections.** ANCHORED means "no capture cross-section data". Zn-70 (4 cells), Ge-76 (30) and
  Te-120 (1) have kept keV cross-section cells. The other ANCHORED nuclides have kept MACS cells, and some have
  thermal-range cells, which the definition allows.
- **MEASURED.** None is without kept data: all 220 have kept cross-section cells in v1 and v2.

Many of the 57 have one or two cells, often from a single integral or activation measurement. v0.1 probably applied a
threshold that its README does not state.

**Size, if reclassified to MEASURED.**
- `tier` changes for up to 60 nuclides.
- The bands change wherever the tier's v0.1 interval was the larger half of max(UNCCAL, v0.1 tier interval):
  `unc_kind` says "larger at 30 keV: v0.1 tier interval" for 208 INTERPOLATED and 5,308 EXTRAPOLATED rows overall.
  The new interval would be the MEASURED one (median 30 keV 68 % factor ×1.24 against ×1.34 / ×1.58).
- Curves, MACS and rates do not change.
- The per-tier tables in v0.2 and v0.2.2 BUILD.md, VERIFY_V02.json and the site's counts would change.

**Alternative (smaller).** Keep the tiers and state the rule that produced them: v0.1's measured set, and the
threshold. The site already shows these nuclides as measured (S1).

Tests: `test_unmeasured_tiers_have_no_kept_kev_capture_data`, `test_anchored_have_no_kept_kev_cross_sections`.

### D. Definitions in the library docs (README of v0.1, v0.2, v0.2.2: "All as in v0.2")

1. **INTERPOLATED.** The README defines it as "unmeasured, with structure data, within two neutrons or protons of
   measured nuclei".
   - The distance is |ΔZ| + |ΔN| to a MEASURED nucleus. It equals `chart_distance` for all 316 INTERPOLATED and 21
     ANCHORED nuclides. 58 INTERPOLATED nuclides have a measured neighbour only diagonally (one proton and one
     neutron).
   - The rule also requires Z 26–83 (GUIDE.md says so; the README does not).
   - It also requires something v0.1's build calls "rich side": 256 were left out for it (`library/v0.1/BUILD.md`).
   - So 205 EXTRAPOLATED nuclides in Z 26–83 with structure data are within 2 of a MEASURED nucleus. Of them, 171 are
     at least as neutron-rich as every measured neighbour.

   Proposed README text: "unmeasured, with structure data, Z 26–83, at most |ΔZ| + |ΔN| = 2 from a MEASURED
   nucleus, and not on the rich side of it (v0.1 build rule; 205 nuclides meet the distance but not the rest)".
2. **Validated range.** "Only Z 26–83 is validated" reads as if Z 26–83 were validated. `in_validated_range` is a Z
   cut only.
   - Of the 3,707 nuclides it marks, 2,451 have no structure data.
   - 195 moved by more than 1 dex since v0.1 (`v01_mover_note`), 576 are model-form flagged, and 892 are
     `engine_grid_dependent`.

   Proposed text: "`in_validated_range` marks Z 26–83, the proton range the validation covered. It does not say that
   a nuclide's value was validated: far from stability, see `v01_mover_note` and `model_form_flag`."

The site texts were changed in S3–S5. `docs/GUIDE.md` carries both notes. The library README and BUILD.md are
checksummed and wait for this amendment.

### E. TERRA coverage cells labelled "N/A (<5 nuclei)" with 5 or 6 nuclei (Scoreboard section 2)

Four counted-as-N/A cells in `cells.csv` carry `n_nuclei` ≥ 5. Under the stated TERRA rule ("fewer than 5 for the
series-aware and uncertainty-coverage cells") they should be scored:

| cell | rival | `n_nuclei` | gap [95 % interval] | verdict if scored |
|---|---|---|---|---|
| COV-IS fission | ENDF/B-VIII.1 | 6 | +0.041 [−0.033, +0.093] | TIE |
| COV-CE fission | ENDF/B-VIII.1 | 6 | +0.098 [−0.191, +0.159] | TIE |
| COV-IS fission | JEFF-4.0 | 5 | −0.012 [−0.090, +0.066] | TIE |
| COV-CE fission | JEFF-4.0 | 5 | +0.097 [−0.179, +0.197] | TIE |

Meanwhile `SURR COV-IS fission` and `SURR COV-CE fission` against JENDL-5 and TENDL-2025, also with 5 nuclei, are
scored: TIE and TIE against JENDL-5, WIN and TIE against TENDL-2025.

Two readings:
- **The label is right and `n_nuclei` is not the count the rule used.** For example, the rule may count nuclei that
  have the library's own covariance, which ENDF/B and JEFF give for fewer fission targets. Then only
  `n_nuclei` / `na_reason` need a note in `data/board/README.md`.
- **The rule was misapplied.** Then the TERRA board changes:
  - totals: 217 WIN / 108 TIE / 1 LOSS / 28 N/A becomes 217 / 112 / 1 / 24;
  - coverage split: TIE 42 → 46;
  - ENDF/B-VIII.1: TIE 25 → 27, N/A 7 → 5;
  - JEFF-4.0: TIE 21 → 23, N/A 11 → 9.

  No WIN or LOSS changes either way.

The TERRA cells cannot be recomputed from this repository (README, "What is not here"), so this needs the TERRA ledger.
Test: `test_terra_na_label_matches_its_nucleus_count`.

### F. `macs_flag` at low kT

`macs_flag` in `macs_kt_v022.csv` repeats `macs30_flag`: resolved resonances above 3 keV, the criterion for a 30 keV
window. At kT = 5 keV the comparable bound is about 0.5 keV.
- 334 nuclides have `resolved_upper_ev` between 0.5 and 3 keV and no flag: 75 MEASURED, 6 ANCHORED, 90 INTERPOLATED,
  163 EXTRAPOLATED.
- RATES.md says "use the rate products where `macs_flag` is empty". For these 334 nuclides, the low-kT MACS and the
  rates below T9 ≈ 0.1 integrate the resolved region the flag is meant to warn about.
- Below T9 ≈ 0.05, every nuclide's rate rests mainly on the curve below 1 keV, as RATES.md already notes.
- `resolved_upper_ev` is known for only 1,239 nuclides (165 of 449 with Z < 26). An empty flag elsewhere means
  "unknown", not "clear".

Proposed: a per-kT flag (resolved range above kT/10) or a RATES.md sentence stating the 30 keV criterion and the
unknown case. No value changes.
