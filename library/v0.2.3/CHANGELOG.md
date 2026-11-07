# Library changelog

## v0.2.3 (2026-11-07)

A corrections-only errata release of v0.2.2 (BUGTIER3 items A, B, D, F: `docs/release/amendments/BUGTIER3.md`). No
cross section, band, MACS, rate or REACLIB fit changes: `VERIFY_V023.json` compares every column of every file with
v0.2.2. Counts of changed cells are in README.md and BUILD.md.

- **A. ANCHORED factor bookkeeping.** `build_library_v022.py` read the v0.2 factor back from v0.2's 3-decimal
  `value_source` text ("blind curve x 0.817"). The listed v0.2.2 totals were therefore off by up to 6.7e-4
  (relative; Ge-76), while the curves carry the exact factor. v0.2.3 takes the v0.2 factor at full precision from
  `anchored_v02_factor` (`below1keV_engine_v022.parquet`; it agrees with the text to < 5e-4).
  - `anchored_rescale_v023.csv`: `v02_factor` and `v022_factor` changed on all 21 rows. Each `v022_factor` now equals
    σ(1 keV) / engine(1 keV) of the shipped curve to 2.2e-16. Example, Fe-60: 0.81723 → 0.81755.
  - `value_source` "blind curve x f" now rounds the true factor. In `capture_v023.parquet` the text changes for 5 of
    the 21: Fe-60 0.817 → 0.818, Se-76 0.973 → 0.974, Te-120 1.168 → 1.169, Ba-132 1.664 → 1.665, Hf-182 0.873 → 0.874.
  - Also found: `macs30_v022.csv` (and `macs30_v021.csv`) still carried v0.2's ANCHORED `value_source` text, with the
    v0.2 factor ("blind curve x 0.817 (measured MACS30 anchor)"). `macs30_v023.csv` now has the capture file's text
    (21 rows).
  - The curves, MACS and rates do not change. Recomputed from v0.2 with the v0.2.2 build's own functions, the 21
    ANCHORED curves, MACS and rates agree with the shipped values to ≤ 1e-15. The last ulp depends on the
    floating-point platform; non-ANCHORED nuclides recomputed on the same machine differ by as much.
- **B. Model-form columns.** `model_form_max_dex_sub1MeV` was 0.0 for the 3 `gg_deadend` nuclides, the "not widened"
  convention. It is now |log10(alt / σ)| at 31.8 keV, the one energy where their alternative is kept: Mo-86 3.59,
  Tc-87 1.11, Rh-105 2.43 dex (a lower bound on the difference below 1 MeV). Bands unchanged. The README now says that
  `alt_value_30keV_b` is the alternative at the grid point nearest 30 keV (31.8 keV), not at 30 keV.
- **D. Definitions.** The README states the full INTERPOLATED rule: Z 26–83, |ΔZ| + |ΔN| ≤ 2 from a MEASURED nucleus,
  and v0.1's "rich side" exclusion. It also says that `in_validated_range` is a Z cut. "Only Z 26–83 is validated" no
  longer appears: of the 3,707 nuclides in that range, 2,451 have no structure data.
- **F. Per-kT MACS flag.** `macs_flag` in `macs_kt_v022.csv` repeated `macs30_flag` (resolved resonances above 3 keV)
  at every kT. v0.2.3 uses each kT's own criterion, `resolved_upper_ev` > kT/10:
  - new columns `macs_flag_5keV` ... `macs_flag_100keV` (True/False) in `macs_kt_v023.csv`;
  - `macs_flag` is set where any of them is: 879 nuclides, against 545. The 334 newly flagged have resolved resonances
    up to 0.52-2.9 keV: 75 MEASURED, 6 ANCHORED, 90 INTERPOLATED, 163 EXTRAPOLATED. The text of the other 545 now names
    their kT range;
  - at high kT the criterion is stricter, so some of v0.2.2's flags no longer apply there: 22 at 40 keV, 106 at 100 keV
    (`macs_flag_<kT>keV` False, `macs_flag` still set);
  - new column `rate_flag_below_T9` in `rates_v023.csv` (1,061 nuclides);
  - `macs30_flag` is unchanged.
- **Not applied.** BUGTIER3 item C (reclassifying the tiers of about 60 nuclides with kept keV capture data) and item E
  (4 TERRA coverage cells labelled N/A) are separate decisions. They are listed as known issues in README.md.
- **Code:** `scripts/release/build_library_v023.py`, `scripts/release/verify_library_v023.py`.
- **Reader:** `python -m incognita.library show <nuclide> --version v0.2.3`.

v0.2, v0.2.1 and v0.2.2 stay unchanged in their directories.

## v0.2.2 (2026-11-07)

A correction of the Maxwellian averages, rates and REACLIB fits of v0.2.1. The engine, the nuclides, the tiers, the bands,
the threshold channels and the capture curves from 1 keV to 20 MeV (all but the 21 ANCHORED ones) are unchanged. See
BUILD.md for the numbers.

- **The v0.2.1 issue: 1/v below 1 keV.** v0.2.1 extended every curve below its first grid point (E_lab = 1 keV) as 1/v
  (`scripts/release/build_library_v021.py`, `macs_cm`, the `lo` term). The production engine's own capture falls more
  steeply than that: between 2 eV and 1 keV its slope d ln σ / d ln E has median −0.71 (5-95 %: −0.93 .. −0.43), against
  −0.5 for 1/v. So v0.2.1's low-temperature rates were mostly too low: v0.2.1 / engine was 0.79-0.85 at T9 = 0.01 and
  0.93-0.96 at 0.03 for Au-197, Fe-56 and Dy-164, and 0.97-0.98 for their MACS at 5 keV.
- **Fix 1: the engine below 1 keV.** v0.2.2 ran the production engine (engine-20261022-3, nucleus 16606b356d6e; the v0.2
  environment, deck, runner and inputs) on its production energy grid plus 15 points from 2 eV to 0.66 keV, for every
  nucleus with a production input (6,150, 6,361 runs, 0 failures), composed with v0.2's rule for each nucleus. Below 1 keV
  the curve is now these engine values (`sigma_below1keV_b`, `below1keV_source`), log-log interpolated, 1/v only below 2 eV.
  - Each run reproduces v0.2 above 1 keV: 5,692 nuclei to < 1e-9 at all 64 points (14 control nuclei to ≤ 5e-13).
  - 133 runs differ from v0.2 at the 1 keV point (by 1e-9 to 1 %); their part below 1 keV is scaled by that
    difference to join the curve.
  - 55 nuclei keep v0.2.1's 1/v extension, and `below1keV_source` says why: 18 have no production input (v0.1 values),
    29 runs differ from v0.2 at 1 keV by more than 1 %, and 8 runs sit on the engine's output floor below 1 keV.
- **Fix 2: reduced mass.** The rate used μ = A/(A+1) u (v0.2.1, and v0.2's make_rates.py). The reduced mass is
  μ = m_n·M/(m_n+M), m_n = 1.00866 u, M the target's atomic mass (AME2020; the mass number A in u for the 2,846 nuclides
  AME2020 does not list, which changes μ by < 1e-5). The old μ was too small by 1.00866·(A+1)/(A+1.00866), so every rate
  was 0.40-0.43 % too high (v_T = √(2kT/μ)). The same masses now set the centre-of-mass energy, E = E_lab·M/(M+m_n)
  instead of A/(A+1); that moves any MACS by less than 0.1 % (median −0.003 %). `rates_v022.csv` lists `target_mass_u`
  and `reduced_mass_u`.
- **Net change, v0.2.2 / v0.2.1 − 1 (median, 5-95 %).** Rates: +8.8 % (−3.9 .. +31 %) at T9 = 0.01, +2.1 % at 0.03,
  +0.1 % at 0.1, −0.32 % at 0.3, −0.41 % at 1, −0.43 % from 3 up. MACS: +1.1 % (−0.2 .. +4.4 %) at 5 keV, +0.42 % at
  10 keV, +0.09 % at 30 keV, +0.01 % at 100 keV.
- **ANCHORED** (21): one more factor (0.989-1.001) makes the MACS30, now including the engine below 1 keV, equal the
  measured anchor. `anchored_rescale_v022.csv` lists the factors.
- **New files:** `below1keV_engine_v022.parquet` (the engine runs below 1 keV), `masses_v022.csv`,
  `compound_smin_v022.csv` and `grid_dependent_v022.csv` (the known issue below).
- **Code:** `scripts/release/collect_below1keV_v022.py` (on the machine with the engine runs),
  `scripts/release/build_library_v022.py`, `scripts/release/verify_library_v022.py`.
- **Reader:** `python -m incognita.library show <nuclide> --version v0.2.2`.

### Known issue: grid-dependent engine values (not changed in v0.2.2)

The engine's value at one energy can depend on the other energies in the same run. The cause was found on branch
`gridfix` (2bac71aa): the engine's outgoing-energy grid ends at E + S_n + 1 MeV, with E the run's highest incident
energy. When the compound nucleus is unbound to alpha or proton emission (separation energy S < 0), a run whose top
energy is low (a one-point or short grid) drops the fastest alphas or protons. With pre-equilibrium on, that inflates
capture, by up to ×62 (branch `talysworld`, `scripts/talysworld/CHECK.md` and `check_points.csv`: capture and (n,p) on
I-109, Pa-200, Ra-215, Fr-190, Bi-178, Tl-174, Te-104). Grids that reach ≥ ~5 MeV converge.

- v0.2 and v0.2.2 come from the wide production grid (top 20.5 MeV), so their values for these nuclei are right to about
  1.5 % at keV energies (a second, smaller mechanism, sfactor carry-over, remains). Above about 21 MeV + S_min the
  emission is still cut. The real fix is the engine's GRIDTOP setting, which the next engine release turns on.
- It is the short-grid and one-energy runs that are wrong, not the library. v0.2.2 used only the wide grid: the runs on
  2 eV - 1 keV alone missed v0.2's 1 keV value for 2,323 nuclei (by > 10 % for 184) and were discarded.
- Affected: 2,364 nuclides whose compound nucleus has S_min < −1 MeV (2,309 via alpha, 55 via proton), flagged
  `engine_grid_dependent` in `capture_v022.parquet` and `macs_kt_v022.csv` and listed in `grid_dependent_v022.csv`
  (S_min for every nuclide: `compound_smin_v022.csv`). 892 are in Z 26-83; 49 are MEASURED (Nd-143 to U-238; the list
  is in BUILD.md), 6 ANCHORED, 100 INTERPOLATED and 2,209 EXTRAPOLATED.

v0.2 and v0.2.1 stay unchanged in `library/v0.2` and `library/v0.2.1`.

## v0.2.1 (2026-11-06)

A correction of the Maxwellian averages, rates and REACLIB fits of v0.2. The engine, the nuclides, the tiers, the bands,
the threshold channels and the capture curves (all but 21) are unchanged. See BUILD.md for the numbers.

- **Bug: lab-frame MACS.** v0.2 (and the v0.1 and preview builds, which used the same formula) integrated
  sigma(E) E exp(-E/kT) over the laboratory neutron energy. The MACS is defined over the centre-of-mass energy
  E = E_lab A/(A+1) (KADoNiS; Beer, Voss & Winters 1992). The code was nucleus `research/rl/libv02/code/build.py:33-35`
  (MACS30 and the ANCHORED scaling), `mform.py:25-27` (`alt_macs30_mb`) and nuc-local `scripts/release/make_rates.py`
  (`macs_kt`, rates, REACLIB). For a falling cross section, the lab formula is biased high by about (1+1/A)^alpha.
  At 30 keV, with the 1 keV cut held fixed, the median bias was +3.1 % for A < 20, +1.7 % for A 20-39, +1.0 % for
  A 40-79, +0.5 % for A 80-149 and +0.2 % for A >= 150. The range was -7 % to +5 %: curves rising with energy were
  biased low.
- **Bug: integrals cut at 1 keV.** Every integral started at the grid's first point, so the part below 1 keV was left
  out. That made v0.2 low by a median 7 % at kT = 5 keV, 2.6 % at 10 keV and 0.3 % at 30 keV, and by about half for the
  rate at T9 = 0.01. v0.2.1 extends sigma below 1 keV as 1/v and publishes the size of that extension
  (`share_below1keV_<kT>keV`).
- **Net change of MACS30** (v0.2 / v0.2.1 - 1, median): +2.6 % for A < 20, +0.75 % for 20-39, +0.15 % for 40-79, -0.2 %
  for 80-149, -0.4 % for A >= 150. The two errors partly cancel.
- **ANCHORED** (21): one more factor (0.992-1.002) makes the centre-of-mass MACS30 equal the measured anchor.
  `anchored_rescale_v021.csv` lists the factors.
- `alt_macs30_mb` is scaled by the shipped curve's own MACS30 ratio, because the alternative curves are not kept.
- The nucleus research code was not edited. The corrected computation is `scripts/release/build_library_v021.py`, and
  `scripts/release/verify_library_v021.py` checks it independently: 12 nuclides agree to 1.2e-9, and the 1/v and
  constant closed forms agree to 1e-9.
- **Reader.** `python -m incognita.library show <nuclide> --version v0.2.1`.

v0.2 stays unchanged in `library/v0.2`. Its MACS, rates and REACLIB fits carry the two errors above.

## v0.2 (2026-10-23)

Same 6,168 nuclides, same files and same tiers as v0.1. What changed is where the numbers come from. BUILD.md has the
details and the checks.

- **Engine.** Every curve now comes from the production engine `engine-20261022-3`, the engine the scoreboard scores
  (release tag `engine-2026-10-22`). v0.1 was built with an older engine.
- **Curves are engine predictions.** In v0.1, MEASURED and INTERPOLATED curves came from a model trained on the
  measurements. In v0.2 every curve is the engine's blind prediction; none is fitted to its own nucleus's data. The one
  per-nucleus use of data is unchanged: ANCHORED curves (21) are scaled by one factor to a measured 30 keV MACS.
  The tier now only describes the data situation of a nucleus, not the method.
- **Learned (n,p) correction dropped.** It was fitted on top of the older engine and does not apply to this one. (n,p),
  (n,2n) and (n,α) come from the same engine runs as capture; `grid_np_v02.parquet` keeps v0.1's 361 (n,p) targets with
  the engine's (n,p) band. The columns `tendl_fitted_other_data`, `outside_training_*`, `e1_constant_*` and `recipe_mb`
  are gone.
- **Bands.** At each energy, the wider of the engine's own band and the nucleus's v0.1 band, so no band is narrower
  than in v0.1. No new band was calibrated.
- **Model-form flags and widened bands.** 1,134 nuclides carry `model_form_flag`: 1,108 `pe_kev` (keV capture depends
  on pre-equilibrium emission at low energies, which this engine includes and TALYS/TENDL start near 1 MeV), 23
  `fists2` (fission-transmission setting, actinides) and 3 `gg_deadend` (Mo-86, Tc-87, Rh-105: the value relies on the
  engine's fix of a missing gamma-decay width; noted, not widened). For `pe_kev` and `fists2` the 68 % and 95 % bands
  below 1 MeV are widened to contain the other choice (median 95 % factor at 30 keV on these nuclides x2.7 -> x4.3,
  largest x7.3e4). All flagged nuclides are EXTRAPOLATED. `alt_value_30keV_b` and `alt_macs30_mb` give the other choice.
- **Large movers.** 318 nuclides moved by more than 10x in their 30 keV MACS against v0.1, almost all far from
  stability; `v01_mover_note` names the cause. On the MEASURED tier the typical change is small (median -0.02 dex).
- **Counts.** 6,168 nuclides: 220 MEASURED, 21 ANCHORED, 316 INTERPOLATED, 5,611 EXTRAPOLATED. 18 drip-line nuclides
  without a production input keep their v0.1 values (`value_source` says so).
- **Reader.** `python -m incognita.library show <nuclide> --version v0.2` (or `capture_curve(..., version="v0.2")`)
  reads this library; without `--version` the reader still reads v0.1.

v0.1 stays unchanged in `library/v0.1`.

## v0.1 (2026-09)

First release. See `library/v0.1/README.md`.

## Checksum note (2026-11-06)

- `library/v0.2/SHA256SUMS` listed a stale hash for `README.md` since v0.2 was published (2026-10-29): the README was edited after the sums were made. Only that line was wrong; every v0.2 data file verifies. The line is corrected in v0.2/SHA256SUMS; no v0.2 file changed.
- `.gitattributes` now exempts `library/**` and `data/curation/**` from line-ending conversion, so `sha256sum -c` passes on Windows checkouts too.
