# Curation rule v2: a library-free EXFOR curation register (pre-registered 2026-09-23)

This file was committed BEFORE the v2 rule was applied to any decision. Its predecessor is the INDEP_CURATE rule v1
(branch `lab branch indep-curate`, commit 32662c3f, `docs/results/indep_curate_rule.md`). v1 re-decided only the 129
register lines that name an evaluated library. v2 closes v1's four known gaps and is applied to ALL 524 lines of
`data/curate/review_decisions.jsonl` (md5 a84fc94d), and chart-wide to every capture cell. It is the rule that
`incognita/curation/` implements.

Changes from v1 (section numbers below):
- G1, one series against one (Hf-176 Moxon 1974): new R10, an isotopic systematic (§2).
- G2, MACS kinds not compared (Kr-84): new R11, which is MACSCHECK's method adopted as written (§2).
- G3, duplicate copies counted as independent references (U-236): new R3d (§2).
- G4, the 3 MeV cut (Colditz at 2.9 MeV): R8 is now scoped per scored cell, not per raw point (§2).
- New: R12, a corroborating record-quality flag. The statistical-region gate (§1). Chart-wide application with a
  two-pass order (§3). The validation protocol (§4).

Honesty note. G1-G4 were found by reading v1's outcome on known cases. The v2 rules that close them were therefore
written knowing which datasets they would touch. The thresholds come from physics or from the earlier rules
(MACSCHECK, twins, MEVCHECK), not from fitting to those cases. The report must still say that these four cases are
not blind tests of v2.

## 0. Evidence

Allowed:
- EXFOR: values, quoted uncertainties, and BIB fields (REACTION SF5-SF9, STATUS, MONITOR, CORRECTION, ERR-ANALYS,
  COMMENT, DECAY-DATA, INC-SOURCE, SAMPLE, METHOD).
- The EXFOR-derived series table (`series_id` = FLOOR union-find of shared entry, or first author + facility +
  detector, plus twin edges).
- IAEA neutron standards (2017) and the Au-197 kT = 25/30 keV reference values used by AUSTD.
- NUBASE2020, ENSDF, RIPL-3/4 (resonance spacings D0, spins) and AME.
- Textbook physics bounds.

Forbidden:
- Any value from an evaluated library (ENDF/B, JENDL, JEFF, TENDL, CENDL, BROND, FENDL, IRDFF, BRUSLIB, or any
  other). **This includes the libraries' resolved-resonance-range bounds** (`validation.differential.rrr_bounds`).
  The old rule-(c) sweep used those bounds, and §1 replaces them with a RIPL D0 gate.
- KADoNiS recommended values. Only EXFOR MACS measurements may be used.
- Our model, TALYS, or any model output.
- The WP-12 automatic trust, consensus and decisions. v2 does not use them as evidence. They stay a separate
  automatic layer, which is exported next to the register and labelled as such.

## 1. Universe and quantities

- **Channel.** Capture (MT 102), ground-state total (state '', branch ''). This is every line of the v1 register.
  The other channels have no register lines, and v2 does not sweep them. That is a stated limitation.
- **Cell.** One dataset in one 0.1-dex energy bin (`bin = floor(10 log10 E) + 100`), from the WP-12 cell table
  `exfor_cells.parquet`. The datum is x = log10(mean_b). For a point-scoped test, x is the log10 of the point's
  value. Only `usable` cells with mean_b > 0 are used.
- **Uncertainty.** sigma_x = log10(1 + rel), where rel = sqrt(stat_rel^2 + sys_rel^2) as reported. If that is
  missing, rel = sem_rel. If that is missing too, rel = 10 %.
- **Constants.** X15 = log10 1.5, X2 = log10 2, X3 = log10 3, X5 = log10 5.
- **Comparable kinds (R5, R6, R10).** The comparison is exact-kind only. Kinds containing `spa`, `fis` or `raw` are
  never compared, because spectrum-averaged and raw quantities depend on the facility's spectrum or processing.
- **Statistical-region gate (new; replaces the library RRR bound).** A differential `sig` cell takes part in R5,
  R6 and R10 only if at least one of these holds:
  - its bin's lower edge is >= E_stat. Here E_stat = max(1 keV, 40 * D0). D0 is the RIPL s-wave resonance spacing
    of the target (column D3, else Db, of `ripl4_resonances_L0.csv`). If the target has no D0, use the median D0 of
    the RIPL nuclides with the same Z and N parities and |dA| <= 10. If there are none, E_stat = 100 keV.
    Reason: a 0.1-dex bin spans 0.26 E, so at E >= 40 D0 it holds >= 10 s-wave resonances. Bin means from
    different resolutions and samples are then comparable within the Porter-Thomas fluctuation, about 45 %,
    which is well inside the x2 threshold.
  - it is the thermal cell (every point between 0.02 and 0.03 eV), which is a single well-defined quantity.

  Integral kinds (`ri`, `mxw`, `av`, ...) are not gated.
- **Series of a dataset.** Its `series_id`. A dataset missing from the series table gets its own series, keyed by
  its EXFOR entry.

## 2. Rules

Each rule fires independently. §3 gives the order in which they are evaluated and the combination ladder.

### Record family: human readings of the EXFOR record
These rules come from a person reading the EXFOR record. Each is listed in `data/curation/record_findings.jsonl`
with its rule code, scope (dataset, or points or cells) and a VERBATIM quote of the record. The build refuses to
run if a quote is not found in that subentry's text (or in the entry's SUBENT 001) in `entry.zip`. v2 adds no new
readings: the findings are those of MEVCHECK, AUSTD, DATAPASS (a), REGEXCL (a) and INDEP_CURATE's RECORD table.

- **R1, record-proven error → EXCLUDE (or unit fix), scoped to what the record proves.** The record contradicts
  itself. Examples: an error inconsistent with the stated band; a factor-10 slip; an author disclaimer covering
  the energy; the same author's later measurement of the same sample differing by an exact power of ten.
- **R2x, not the scored quantity → EXCLUDE.** SF9 DERIV/CALC that imports an external constant or keeps only one
  component.
- **R2d, single-state production curated as total capture, with an unbounded missing branch (NUBASE) →
  DOWNWEIGHT-grade.**
- **R4, renormalisation.** The factor must equal the current standard or reference value divided by the value
  documented in the record (MONITOR / ANALYSIS). Otherwise the renormalisation is dropped.
- **R8, background mechanism → DOWNWEIGHT-grade; never excludes alone.** MeV activation whose record documents a
  low-energy source component (thick-target D-D, room-return or epithermal field behind only Cd) and documents no
  correction for it.
  - **Scope is per scored cell (G4):** R8 applies to the cells whose 0.1-dex bin extends above 3 MeV (upper bin
    edge > 3 MeV).
  - v1 compared the raw point energy with 3 MeV. MEVCHECK's implementation, the origin of the rule, assigned points
    to scored bins (bin 164, 2.51-3.16 MeV, whose scoring energy is 3.03 MeV). The register acts on scored cells,
    so v2 uses the cell.

### Identity family: machine rules on EXFOR
- **R3, twin superseded → EXCLUDE the superseded copy.** The rule is `scripts/twins.py` unchanged:
  - A BIB cross-reference (STATUS SPSDD, or "renormalized / revised gold / new gold" in Subent X), or two datasets
    of one nuclide/kind with the same cells whose values differ by a constant factor (sd of the log10 ratio
    < 0.004 dex).
  - Either way, the pair must be confirmed by the numbers: factor in [0.8, 1.25], and sd < 0.01 dex (x) or
    < 0.004 dex (d).
  - A single-cell data pair needs an exact copy (< 3e-5 dex) and the same entry, or the same first author and year.
  - Direction: the documented renormalised copy is kept. Failing that, the higher-trust copy (WP-12 trust is used
    here only as a tie-break between two copies of the same numbers), then the earlier accession.
- **R3d, non-independent reference (G3); no decision by itself.** While testing datum D, a candidate reference
  dataset Q from another series is NOT independent of D if either:
  - Q's value in the tested cell equals D's within 3e-5 dex, or
  - over >= 2 shared cells, Q/D is constant (sd < 0.004 dex, factor in [0.8, 1.25]).

  Q is dropped from D's reference set, and the pair is listed as a duplicate candidate.

### Physics family
- **R7, physics bound → EXCLUDE.** Capture value <= 0, or above pi (R + lambda-bar)^2 with R = 1.25 A^(1/3) fm and
  lambda-bar = 4.55 / sqrt(E/MeV) fm.

### Data family: EXFOR against EXFOR
**Reference set of a cell.** Datasets of the same (nuclide, kind, bin) that meet all of these:
- a different series_id and a different EXFOR entry;
- not excluded in pass A (§3);
- not DERIV/CALC/EVAL/RECOM (SF9) and not `is_calc_eval`;
- not R3d-dependent;
- comparable kind; in the statistical region.

Each reference series contributes one value, the mean log10 of its datasets. If fewer than 2 reference series sit
in the bin, bins +-1 are added (the widening is recorded). d = x - median(ref); spread = max - min.

- **R5, inter-dataset scatter.** Requires n_ref >= 2, ALL references on the same side of x by > X2, and
  |d| > 2 sigma_x. Then EXCLUDE if |d| > X3 and (n_ref >= 3 or spread <= X15); otherwise DOWNWEIGHT-grade.
  With n_ref = 1 or 0, R5 never fires.
- **R6, series systematic.** For target cell c0 of series S, take S's OTHER cells that have a same-bin R5 offset
  (n_ref >= 1). R6 fires when:
  - at least 3 of them have the sign of d_c0 and |d| > X2;
  - their median predicts d_c0 within X15 (leave-one-out);
  - their references come from >= 2 distinct series.

  Then EXCLUDE if |d_c0| > X3 and > 2 sigma_x; DOWNWEIGHT-grade if |d_c0| > X2.
- **R9, cross-nuclide systematic at >= 12 MeV.** The reference is independent-series values in the same or
  adjacent bin on >= 5 OTHER nuclides with |dA| <= 30, one median per nuclide. A datum beyond X5 of their median
  → DOWNWEIGHT-grade.
- **R10, isotopic systematic (G1).** Applies only where R5 cannot judge (in-nuclide n_ref <= 1 after widening).
  The cell must be differential `sig`, in the statistical region, with 10 keV <= bin lower edge < 12 MeV.
  - **Reference nuclides:** same Z, same N parity, 0 < |dN| <= 4. Neither the target nor the reference may have
    N within 2 of a magic number (28, 50, 82, 126), because capture drops by an order of magnitude at shell
    closures.
  - **Reference data:** ground-state total capture, same kind, same or adjacent bin, independent series (a series
    and entry different from the datum's), not excluded in pass A, not derived. One median per reference nuclide;
    >= 2 reference nuclides are needed.
  - **Statistic:** d10 = x - median of the per-nuclide medians. The per-nuclide medians must agree with each other
    (max - min <= X3); otherwise no test.
  - **Fires** if |d10| > X5 and |d10| > 2 sigma_x.
  - **EXCLUDE** if in-nuclide n_ref = 1 and that one independent series sits on the same side as the neighbours,
    beyond X3 from x (two independent lines of evidence). **Otherwise DOWNWEIGHT-grade.**
  - Why X5: at >= 10 keV, even-N isotopes of one element that are away from shell closures differ in capture by
    at most about x3-4 over |dN| <= 4 (e.g. Hf-176/Hf-180 at 30 keV are about x4 apart). x5 on the median of >= 2
    neighbours that agree within x3 is a conservative margin.
- **R11, MACS against differential (G2).** This is MACSCHECK (`docs/results/macscheck.md` §1 plus both
  amendments in §2), adopted unchanged except for its input filters:
  - **IMs.** Independent MACS measurements (kind `mxw`, kT 20-40 keV, not compilation/derived) that are not
    excluded in pass A. The WP-12 `decision` column is not used.
  - **Series curve.** The differential curve is the series' comparable `sig`/`av` cells that are not excluded in
    pass A.
  - **Averaging.** The series is Maxwellian-averaged over its own coverage (f >= 0.8).
  - **Flag.** >= 2 independent IM groups (merged by series, or by author + year; same-author IMs within 2 years
    are dropped). >= 2 of them must disagree by > x1.5 in one direction and agree with each other within x1.5, and
    the groups against must outnumber the groups within x1.5.
  - **Grade.** EXCLUDE with >= 3 groups against; otherwise DOWNWEIGHT-grade.
  - **Scope.** Dataset-level, on every dataset of the series for that nuclide.
- **R12, record-quality flag (corroborating only; never decides alone).** The record is preliminary or digitised
  (STATUS contains PRELM or CURVE), or the dataset reports no uncertainty (stat, sys and sem all missing).
  - In the ladder, R12 counts as a record-family finding. It can raise one data DOWNWEIGHT-grade finding (R5d,
    R6d, R9, R10d, R11d) to EXCLUDE.
  - It is read from EXFOR (STATUS) and the data columns, for every dataset where a data rule fires.
  - It formalises the judgment behind the one earlier manual exclusion, a preliminary figure-read
    curve with no uncertainties.

## 3. Order and combination

- **Pass A (evidence that does not depend on other data):** R1, R2x, R2d, R3, R4, R7, R8 and the R12 flags. Their
  EXCLUDEs leave the reference pool. DOWNWEIGHTs stay in it. R4-renormalised values enter the pool renormalised.
- **Pass B:** R5, R6, R9, R10 and R11, evaluated ONCE against the pass-A pool.
  - A pass-B exclusion never removes a reference from another pass-B test. There is no iteration and no order
    dependence.
  - R3d is applied inside every pass-B reference set.
- **Ladder, per cell:**
  1. Any of R1, R2x, R3, R7, R5x, R6x, R10x or R11x → EXCLUDE.
  2. A data DOWNWEIGHT-grade finding {R5d, R6d, R9, R10d, R11d} plus a record finding {R2d, R8, R12} → EXCLUDE.
  3. Any single DOWNWEIGHT-grade finding (R12 excepted) → DOWNWEIGHT x0.25.
  4. Otherwise KEEP.
- **Renormalisation.** R4 is decided separately. The ladder still applies to the renormalised values.
- **Granularity.** Decisions are made per cell. A register record is dataset-level when the rule is dataset-level
  by nature (R2x, R3, R11, dataset-scoped R1/R2d/R8 findings) or when every in-scope cell of the dataset gets the
  same decision. Otherwise it is cell-scoped and lists the cells and their EXFOR points.

## 4. Validation (fixed now, before any v2 decision exists)

1. **Agreement with the v1 register.** For each of the 524 lines, the v2 decision on the line's own scope: EXCLUDE
   / DOWNWEIGHT / KEEP / RENORM. The "strongest cell" rule applies, and a point-scoped line is judged on its
   points.
   - Report agreement, the transition matrix, and every flip with its reason codes and evidence numbers.
   - Report separately the lines whose old evidence was a library value (v1 class L2): those flips are the
     independence fix. Flips elsewhere are rule differences.
2. **New decisions.** List all chart-wide v2 decisions with no v1 line, by rule. They are not in the v1 register
   and have not been read by a human. That is said wherever they are counted.
3. **Spot audit of 30 decisions against the EXFOR record** (entry.zip), drawn with `numpy.random.default_rng(20260923)`
   in three strata of 10:
   - (a) R3 twin decisions;
   - (b) other v2 non-KEEP decisions;
   - (c) flips against v1.

   Each is read against the subentry text and the data. The verdict is SUPPORTED / NOT SUPPORTED / UNCLEAR, with
   the quote. Every NOT SUPPORTED is reported. No rule is changed after the audit. Any change would be v3, with
   its own pre-registration.
4. **Nothing is trained or scored.** No blind, vault or fold 6-7 score is read. Counting how many decisions fall
   in the blind or DEV/vault cell sets is set membership, not a score read, and it is reported as membership only.
   The frozen 674/669-bin blind sets are NOT redefined by v2. Any register-adjusted blind set needs its own
   registered look.

## 5. Output

- `curation_register_v2.jsonl` and `.csv`: one record per decision. The schema is in `incognita/curation/schema.py`
  and `docs/release/CURATION_REGISTER.md`. Every record has:
  - a reason code;
  - the rules fired;
  - the evidence numbers (d, n_ref, reference offsets and series, spread, sigma_x, R6/R9/R10/R11 statistics);
  - the standard used (for R4);
  - the record quotes (for the record family).
- A drop-in `review_decisions`-format file for INDEP_FIX's follow-up.
- No library value appears in any output field. The build greps its own outputs for library names followed by
  numbers, and fails if it finds any.
