# Adopting capture set v2

**v2.2 (2026-11-07).** The files here are now v2.2 (README section "v2.2"): v2.1 plus 6 agent-checked lines (rule
D11_TOTAL_XS) excluding the Celenk 1991 thermal values (EXFOR 22234002-007: V-51, Co-59, Cu-63, In-115, Dy-164,
Au-197), which are total cross sections of the foils, not capture. 116 decisions move from v2.1: 6 by the lines and 110
keep <-> downweight by the automatic layer's re-learning (none to or from exclude). v2.1 is rebuilt by the same script
(ladder step S9). A card that pinned v2 or v2.1 by its `SHA256SUMS` lines keeps what it pinned; the v2.1 tables are in
git history (commit 3fe96822).
Website (`scripts/build_site_data.py`, regenerated on v2.2): 59 of the 6 244 nuclide files and `index.json` change
(marks keep <-> downweight of the re-learned datasets, the six Celenk points now drawn as excluded where the page shows
them; the Co-59 -> Co-60m partial is not drawn). Index: only `n_use` changes, for 4 nuclides (V-51 112 -> 111, Cu-63
145 -> 144, In-115 143 -> 142, Au-197 934 -> 933); tier, MACS 30 keV and its uncertainty are identical for all 6 183
nuclides, and no nucleus changes its measured / not measured label.

**v2.1 (2026-11-07).** The files here are now v2.1 (README section "v2.1"): 15 agent-checked lines (12 duplicate
excludes, Mo-95 fix-unit, Te-120 exclude, W-186 kT EV -> KEV) and centre-of-mass energies converted to lab (11 datasets).
A card adopting the capture set names v2 or v2.1 by the `SHA256SUMS` lines it pins; v2 is rebuilt by the same script
(ladder step S8). The counts below are those of v2.

CAPSET-v2 is a new version. Nothing that is sealed, frozen or already scored reads it, and nothing in this commit
changes a model, a library file, a score or a sealed read. This note lists what WOULD change if a future card or
rescore adopts it, and how to adopt it without touching a sealed read.

## What reads the capture tables today

| reader | file it reads (v1) | what changes with v2 |
|---|---|---|
| validation scorer (`validation/cache.py` `cache_exfor_cells`, `channel_trust`; `validation/differential/core.py`) and every research scoreboard built on it | `curated/exfor_capture_Z26-92_trust.parquet`, `features/validation_cache/exfor_cells.parquet` | which cells count and with what trust: 646 more excluded datasets (Z 26-92), 353 fewer downweighted, 87 + 22 new datasets; cell uncertainties change only where ERR-S/ERR-T/ERR-SYS are split (8 % of cells larger by > 5 %, now carrying the derived systematic part), so chi2-type scores and Birge ratios / inflations move a little |
| WP-12 trust and inflation (the "trust" columns, the review log) | the trust table | `ladder_v2.csv`: 1 035 of 10 619 Z 26-92 v2 decisions (105 of 1 695 for Z 1-25) differ from v1 as shipped (with its 12 review lines; v2.1: 1 038 and 109); step S1 (newer snapshot and review files, no fix) alone moves 610 |
| model training data (`models/stage_c_data.py` reads `curated/exfor_capture_Z26-92_trust.parquet`) | trust table | the training set of any NEW fit; existing models and library v0.2/v0.2.1 are not rebuilt |
| curation register v2 (`incognita/curation`, `../curation_register_v2.*`) | `exfor_cells.parquet` + trust | its R3 twins overlap D5 (both exclude superseded copies); its data rules would see different references. Re-running it on v2 is a new register version that needs its own pre-registration (CURATION_RULE_v2 §4.3) |
| website Data explorer (`scripts/build_site_data.py`) | `../inputs/` tables | measured points and their keep / downweight / exclude marks only (see below) |
| sealed holdouts and blind bin sets (674/669-bin blind sets, resfresh / HELDOUT sets) | their own frozen files | nothing: they are not redefined by v2 |

## Recommended adoption (PREAMBLE gate-calibration rule, 2026-11-06)

1. **Do not swap the files under a running card or a sealed read.** Cards that were registered on v1 finish on v1.
   A sealed read already done stays a v1 result; do not re-read it on v2.
2. **Adopt per new card, in its PREREG.** A card that wants v2 names it in the PREREG (path + `SHA256SUMS` line of
   both trust and cells files), before any score is computed, and includes the Gate calibration section: the null
   pass rate of every gate computed with v2's uncertainties (split datasets now carry their derived systematic
   part, so their per-cell sigma is larger and chi2/N quantiles move), and rule 8 (no dy proportional to the observed value; v2's cells are
   mean-based and the fit is Peelle re-based).
3. **Point the reader, do not overwrite.** `validation/cache.py` takes the trust from `$INCOGNITA_MAIN/curated/` and the
   cells from `features/validation_cache/` (`INCOGNITA_EXFOR_CELLS` for the register). Use a separate
   `INCOGNITA_MAIN` (or a new cache tag) whose `curated/exfor_capture_Z26-92_trust.parquet` and
   `features/validation_cache/exfor_cells.parquet` are copies of the v2 files, so the v1 cache that frozen cards use is
   never rewritten. For Z 1-25 the same with the `_Z1-25_v2` pair.
4. **DEV first.** Compare v1 and v2 scores on DEV only (folds the PREREG allows), report the difference per defect
   using `ladder_v2.csv` (S1 isolates the snapshot drift from the fixes), then the card's one sealed read on v2.
5. **Blind sets.** The frozen blind/holdout bin sets stay as defined. A v2-adjusted blind set (bins whose datasets v2
   now excludes) is a new registered look, not a redefinition; counting membership is allowed, reading scores is not.
6. **Ingest.** New staging for other channels can use the same parser fixes with `INCOGNITA_X4_V2=1` (or a comma list);
   the default stays off so v1 files remain reproducible.

## What changed on the website (this branch)

`scripts/build_site_data.py` now reads the v2 tables (`--curation v1` reproduces the old pages). This is a display
change only: the library curves, tiers, MACS values and every score on the site are unchanged. What a reader sees
differently: 118 more measured datasets (114 of them not excluded), the keep / downweight / exclude mark of the datasets whose decision changed,
wider error bars where a dataset splits ERR-S / ERR-T without ERR-SYS (the systematic part is now included), and,
below Z 26 only, the page's own "measured / not measured (Z < 26)" label where a nucleus gains or loses its last
non-excluded cell (the label is computed by the page from the curation, not taken from the library).

Result of the regeneration in this branch: 359 of the 6 244 nuclide files and `index.json` change (measured points,
their marks and error bars, the measured-cell counts); the index columns tier, MACS 30 keV and its uncertainty are
identical for all 6 183 nuclides, and no Z < 26 nucleus changes its measured / not measured label.
