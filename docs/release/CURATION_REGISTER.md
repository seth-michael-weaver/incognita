# The Incognita EXFOR curation register (v2, 2026-09-23)

This register lists which EXFOR capture datasets we exclude, downweight or renormalise, and why. It is:
- **Open.** CC-BY data, and the code that regenerates it is in this repository.
- **Rule-based.** Every decision comes from a rule committed before it was applied.
- **Library-free.** No evaluated-library value (ENDF/B, JENDL, JEFF, TENDL, CENDL, BROND, FENDL, IRDFF, BRUSLIB)
  and no model output is used as evidence anywhere.

Every decision carries a machine-readable reason code and its evidence: the scatter statistic against independent
EXFOR series, the EXFOR flags, the standard used, and verbatim quotes of the EXFOR record.

- **Rule:** [`CURATION_RULE_v2.md`](CURATION_RULE_v2.md), committed 7ba77701 before any decision was made.
- **Code:** `incognita/curation/`.
- **Outputs:** `data/curation/`.

## Read this first: known problems

1. **The spot audit found 1 wrong decision in 30, and 2 it could not settle** (details below).
   - The wrong one is a twin false positive. `40072034` pointers 2 and 3 are two DIFFERENT samples that happen to
     share the rounded value 45 mb. The twin rule's single-cell "exact copy in the same entry" clause cannot tell
     that apart from a duplicate compilation.
   - Scaled to the 396 twin decisions, expect a handful of such cases.
2. **R10 (the isotopic systematic that closes the Hf-176 gap) has a design flaw.** It can fire when the one
   in-nuclide reference AGREES with the datum. Seen once: Yb-170 `23053002/2` at 286 keV is excluded (R10d, with
   R12 as corroboration) although the single Yb-170 reference sits 0.10 dex from it.
   - Its x5 margin also rests on an assumption that the data weaken. Even-N isotopes 4 neutrons apart in the
     rare earths can differ by about x5 at 30 keV (e.g. Yb-170/Yb-174). The rule assumed at most about x3-4.
   - R10 fires on 4 datasets in total: Hf-176 Moxon (both pointers), Pt-198 `22580015`, Gd-160 `10298004` and the
     Yb-170 case.
   - Fixing this needs a v3 rule with its own pre-registration. v2 was not changed after its outcome was seen.
3. **The four gaps of rule v1 were closed knowing which datasets they touch.** They are therefore not blind tests
   of v2:
   - Hf-176 one-vs-one (R10);
   - MACS kinds not compared (R11);
   - duplicate references (R3d);
   - the 3 MeV cut (R8 per scored cell).
4. **U-236 (`12450002`) still flips from exclude to keep.** R3d does remove the exact duplicate from its reference
   set, which was the v1 gap. The four remaining independent series are 0.30-0.42 dex below it. One of them is at
   0.298 dex, just under the x2 threshold (0.301), so R5 does not fire. The rule is applied as written.
5. **8,733 differential cells below the statistical-region gate are never tested by the scatter rules.** The gate
   is E < max(1 keV, 40 D0), with D0 from RIPL. So resolved-resonance-region data are curated only by the record,
   identity and physics rules. The library resolved-range bounds used by the older sweep were dropped because
   they are library values.
6. **Record readings are human and incomplete.** The 51 record findings are transcribed from earlier campaigns
   (MEVCHECK, AUSTD, DATAPASS, REGEXCL, INDEP_CURATE). Nobody has read every EXFOR record.
   - The audit found one reading worth adding: Bormann `20899008`, COMMENT "No details of correction for secondary
     neutron...". If registered, it would raise that line from downweight to exclude.
   - MEVCHECK and INDEP_CURATE disagree on whether a 1 mm Cd wrap documents a shield against low-energy neutrons.
     v2 keeps both sets of findings as transcribed.
7. **Capture only.** The register sweeps MT102 capture; no other channel has register lines.
8. **The WP-12 automatic trust layer is not part of this register.** That layer holds the automatic exclusion of
   upper limits, non-convertible units and compilations, and the trust weights. It is library-free by
   construction (`data/curate/quality_model.py`), but its validation gate uses Mughabghab-Atlas thermal values,
   and v2 does not re-audit it.
9. **EXFOR values can embed library information themselves.** Example: Ge-73 `23451007` ANALYSIS states that a
   library shape scaled x1.7 was used to extrapolate the MACS. The register cannot see this. It is out of scope.

## What is verified and what is not

**Verified (by code, or by reading the record):**
- Every record quote is found verbatim in `entry.zip`. The build refuses to run otherwise.
- The twin detection reproduces the 396 pairs of `docs/results/twins.csv` exactly.
- The series partition reproduces the shared series table exactly (1,401 series).
- R11 reproduces MACSCHECK: 261 testable pairs, the same 5 flagged series.
- No library name appears in any output file (test `tests/test_curation_register.py`).
- The drop-in file parses with `data/curate/review_log`.
- The 30 audited decisions were read against the EXFOR records, and their data values checked against the DATA
  sections.

**Not verified:**
- The 237 v2 decisions (128 datasets) that no v1 line covers were made by the rule and not read by a human, except
  the audit's stratum (b).
- Whether any change helps or hurts a model. Nothing was trained or scored.

## Numbers

**Coverage.** 33,659 capture cells (dataset x 0.1-dex bin, usable, value > 0). Of these:
- 19,177 were tested by the data rules;
- 8,733 are below the statistical-region gate;
- 2,984 are partial or isomeric-state quantities, handled by the record and identity rules only;
- 1,092 are of non-comparable kinds (spectrum-averaged or raw).

**Decisions: 590 records.**

| decision | records | cells |
|---|---|---|
| exclude | 479 | 1,510 |
| downweight x0.25 | 104 | 213 |
| renorm | 7 | – |

Scope: 517 dataset-level, 73 cell-scoped.

**By reason code:**

| reason code | records |
|---|---|
| R3 twin superseded | 396 |
| R5x inter-dataset scatter | 52 |
| R5d inter-dataset scatter | 51 |
| R8 uncorrected low-energy background | 27 |
| L2 data + record (ladder step 2) | 14 |
| R6d series systematic | 12 |
| R9 14-MeV cross-nuclide | 8 |
| R4 renormalised to the Au standard | 7 |
| R2x not the scored quantity | 6 |
| R1 record-proven error | 4 |
| R10x isotopic systematic | 4 |
| R2d partial state as total | 3 |
| R11d MACS contradicts series | 3 |
| R7 physics bound | 2 |
| R11x MACS contradicts series | 1 |

**Duplicate candidates.** 293 cross-series pairs were dropped from reference sets by R3d
(`curation_duplicate_candidates_v2.csv`). They are listed, not decided.

**Agreement with the v1 register (524 lines):** 483 agree, 41 flip.

| v1 line class | lines | flips |
|---|---|---|
| L2: a library VALUE was the evidence | 77 | 32 |
| L0: library named only in a "no library used" disclaimer | 51 | 9 |
| L1: library named only inside quoted EXFOR text (Kr-84) | 1 | 0 |
| never cited a library (twins, (a)/(b), MACSCHECK, most MEVCHECK) | 395 | 0 |

- **Transitions:** exclude→keep 20, exclude→downweight 14, downweight→exclude 5, downweight→keep 2.
- **The L2 flips are the independence fix.** The library clause had supplied the "second opinion". Without it,
  30 of the 67 old rule-(c) machine-sweep lines no longer qualify: 19 → keep, 11 → downweight via R5d/R9.
  The other 2 L2 flips are the REGEXCL lines Zr-96 `32814008` (one-vs-one; R8 only) and Tb-159 `33113002`
  (R5d), both exclude→downweight.
- **The 9 L0 flips are rule differences:**
  - five downweight→exclude where R5 plus R8/R12 combine (ladder step 2): Nd-148 `11675019`, I-127
    `11675015`, U-238 `11945013` and `40244104` (4 MeV), and Au-197 `21962003`;
  - U-236 (item 4 above);
  - two MEVCHECK (d) lines that R5 does not reproduce, downweight→keep: U-238 Barry `21187002` and Mo-98
    Stupegia `11624006`;
  - Leipunskiy U-238 2.7 MeV `40244104`, exclude→downweight (R8 only).
- **Against INDEP_CURATE's re-decision of the 129 library-citing lines (rule v1):** v2 agrees on 101 and differs
  on 28. The differences:
  - 17 keep→exclude:
    - from the gap fixes: Hf-176 R10x (14 lines), Pt-198 R10x (1), Kr-84 R11x (1);
    - Ce-142 `40975019` (1): R1, the same author's x10 slip, a record finding that v1 applied only to its
      MEVCHECK line.
  - 5 downweight→exclude through R12 (Nd-150, Rh-103 x3, Nd-148) or R8 per cell (Ba-138 Colditz).
  - 4 keep→downweight through R8 per cell (Colditz x3, Leipunskiy).
  - 1 exclude→downweight (Os-192 `40007008`, a different reference pool).

**Where the changes land (set membership only; no score was read).** 317 cells in 153 datasets change against v1:
- 258 cells are in Stage C LSO rows;
- 49 are DEV cells and 79 are vault cells;
- 207 are terra capture rows;
- 6 are in the post-2012 blind population:
  - Yb-168 thermal `30839004`, Yb-174 `30858003` and W-186 `31869003/1-2` resonance integrals: keep→exclude by R5x;
  - Zr-96 14 MeV and Tb-159 5.08 MeV: exclude→downweight.

**The frozen 674/669-bin blind sets are not redefined by this register.** A register-adjusted blind set needs its
own registered look in `BLIND_LOOKS.md`. None was made.

**Spot audit (30 decisions, pre-registered seed 20260923, three strata of 10).** 27 SUPPORTED, 1 NOT SUPPORTED,
2 UNCLEAR.

| stratum | supported | not supported | unclear |
|---|---|---|---|
| (a) twins | 9 | 1 (Pb `40072034/3`, different samples) | 0 |
| (b) other decisions | 9 | 0 | 1 (Kononov Dy-164 `40621006`: references disagree among themselves) |
| (c) flips vs v1 | 9 | 0 | 1 (Moxon Hf-180 177 keV: keep follows the rule, but the point is 0.65 dex above the median) |

- 18 of the 27 cite record text that bears on the decision: a STATUS SPSDD/DEP/CURVE, a compiler COMMENT such
  as "Data about 5 times too large", or a missing or documented correction.
- 9 rest on data alone: the record is silent, and the scatter statistic was checked against the DATA section.
- File: `data/curation/validation/audit_verdicts.csv`.

## Regenerate

```
# inputs under $INCOGNITA_MAIN (default: the repository root), see docs/release/INPUTS.md:
#   raw/exfor/entry.zip (IAEA EXFOR master), staging/exfor_capture_Z26-92.parquet,
#   curated/exfor_capture_Z26-92_trust.parquet (EXFOR BIB flags), features/validation_cache/exfor_cells.parquet,
#   raw/ripl4/RIPL-4/resonances/resonances_L0.dat
python -m incognita.curation.build       # ~20 s, 2 cores
python -m incognita.curation.validate
pytest tests/test_curation_register.py
```

The trust parquet is used only for its EXFOR flags (SF9, compilation, author, facility, detector, year, target Z
and A). Its WP-12 trust is used only as the tie-break between two copies of the same numbers (twin direction).

## Files (`data/curation/`)

| file | content |
|---|---|
| `curation_register_v2.jsonl` | one record per decision (schema below and in `curation_register_v2.schema.json`) |
| `curation_register_v2.csv` | flat: one row per (decision, cell) |
| `review_decisions_v2.jsonl` | drop-in in the `data/curate/review_decisions.jsonl` format, for training code. A point-scoped downweight carries `factor` 0.25. A reader without point-scoped downweight support must skip it. |
| `curation_cells_v2.parquet` | every capture cell with every test statistic, KEEP included |
| `record_findings.jsonl` | the 51 human readings of EXFOR records, with verbatim quotes |
| `curation_twins_v2.csv`, `curation_duplicate_candidates_v2.csv`, `curation_r11_series_v2.csv` | R3 pairs, R3d pairs, all 261 R11 tests |
| `validation/` | `v1_lines_vs_v2.csv`, `flips.csv`, `new_decisions.csv`, `feeds_v2.csv`, `audit_sample.csv`, `audit_verdicts.csv`, summaries |

### Record schema (one JSON object per line)

| field | meaning |
|---|---|
| `id` | stable id `CR2-<entry>-<subentry>-<pointer>-<hash>` |
| `dataset_key`, `entry`, `subentry`, `pointer` | the EXFOR dataset |
| `nuclide`, `z`, `a`, `kind`, `first_author`, `year` | what was measured, by whom, when |
| `decision` | `exclude`, `downweight` (trust x0.25, so sigma x4) or `renorm` |
| `factor` | 0.25 for a downweight; the value multiplier for a renorm |
| `scope` | `dataset` (every cell) or `cells` (only those listed) |
| `reason_code` | the deciding rule (table below) |
| `rules_fired` | every rule that fired on these cells |
| `cells[]` | for each 0.1-dex cell: `bin`, `e_lo_ev`, `e_hi_ev`, `mean_b`, `sig_x`, `rules` and `evidence`, plus `points` (the EXFOR points in the cell). `evidence` holds: `r5` (d, n_ref, the reference offsets and series, spread, the dropped duplicates), `r6` (series median), `r9`, `r10` (neighbour medians) and `r12` (STATUS flags) |
| `evidence` | dataset level: `twin` (partner, how, factor, sd); `record_findings` (id, rule, verbatim EXFOR quotes, note, origin); `r11` (MACS groups with kT, value, coverage, ratio) |
| `standard` | for R4: the standard, the documented and reference values, and their source |
| `flags` | SF9, derived, EXFOR STATUS codes, no_uncertainty |
| `v1` | links to the v1 register lines on the same dataset (validation only) |
| `summary` | one-line human-readable reason |

### Reason codes

| code | rule | grade |
|---|---|---|
| `R1_RECORD_PROVEN_ERROR` | the record contradicts itself (error band, x10 slip, author disclaimer, same author's later measurement) | exclude |
| `R2X_NOT_THE_SCORED_QUANTITY` | SF9 DERIV importing an external constant, or a single component | exclude |
| `R2D_PARTIAL_STATE_AS_TOTAL` | single-state production curated as total, with an unbounded missing branch (NUBASE) | downweight-grade |
| `R3_TWIN_SUPERSEDED` | the same measurement compiled twice; the superseded copy | exclude |
| `R3D_DUPLICATE_REFERENCE_DROPPED` | a cross-series copy dropped from a reference set | info |
| `R4_RENORMALISED_TO_STANDARD` | obsolete monitor value renormalised to the current Au reference | renorm |
| `R5X_/R5D_INTER_DATASET_SCATTER` | >= 2 independent series all > x2 on one side and > 2 sigma. Exclude if > x3 with >= 3 references (or a tight pair) | exclude / downweight |
| `R6X_/R6D_SERIES_SYSTEMATIC` | the series' own offset elsewhere predicts this one within x1.5 (leave-one-out) | exclude / downweight |
| `R7_PHYSICS_BOUND` | above pi (R + lambda-bar)^2 at the incident energy (sig/av kinds only) | exclude |
| `R8_UNCORRECTED_LOW_ENERGY_BACKGROUND` | MeV activation, low-energy source component, no correction documented; cells whose bin extends above 3 MeV | downweight-grade |
| `R9_CROSS_NUCLIDE_14MEV_SYSTEMATIC` | >= 12 MeV, beyond x5 of >= 5 other nuclides (\|dA\| <= 30) | downweight-grade |
| `R10X_/R10D_ISOTOPIC_SYSTEMATIC` | one-vs-one or zero cells: beyond x5 of >= 2 even-dN isotopes away from shell closures | exclude / downweight |
| `R11X_/R11D_MACS_CONTRADICTS_SERIES` | the series' Maxwellian average against >= 2 independent MACS measurements (MACSCHECK) | exclude / downweight |
| `R12_RECORD_QUALITY` | STATUS PRELM/CURVE or no uncertainty given; corroborates only | – |
| `L2_DATA_PLUS_RECORD` | a data downweight plus a record finding (ladder step 2) | exclude |

## Implementation notes (decided before the audit, logged here)

- **I1.** R7 was first applied at the nominal energy of spectrum-averaged (`spa`) and MACS cells, where it fired
  on legitimate values. The bound is defined at the incident energy, so it now covers only `sig`/`av` kinds.
  This was found on the first chart-wide run, before any audit.
  - Consequence: a Mo-95 MACS table at kT = 5-9 keV reading 760-1018 "b" (almost certainly mb) is no longer caught.
- **I2.** The record-family rules reach partial and isomeric-state datasets (the AUSTD renormalisations of Pt-196m
  production, for example). The data rules test only ground-state total capture.
- **I3.** R8 findings are MEVCHECK's (b) findings as transcribed. They include "INC-SOURCE not stated" (MEVCHECK
  b2), plus INDEP_CURATE's two Cd-wrapped D-T sets.
- **I4.** The DATAPASS (a) author disclaimer on U-238 `22541002/003` covers all energies above 2 keV. R1 is scoped
  to what the record proves, so v2 excludes the 38 cells above 2 keV. v1 excluded only bin 153.
- **I5.** Nothing was trained or scored. No BLIND_LOOKS row was needed.

## Consuming it (INDEP_FIX and others)

- Use `review_decisions_v2.jsonl` wherever `data/curate/review_decisions.jsonl` is read (for example
  `GRIND_REGISTER_BRANCH=<path>`).
- It REPLACES the v1 register; it does not add to it.
- Register v1 (md5 a84fc94d) is unchanged in `data/curate/`.
