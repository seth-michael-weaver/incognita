# FIDELITY1 -- engine vs stock TALYS-2.25 on default decks

Branch `fidelity1` (from `kwcov6`). Driver: `scripts/kwcov/fidelity.py` (b2_response's runner; stock cached in
`~/kwcov/b2` / `~/kwcov/b6`, engine in `~/kwcov/fid`, JSON of the final tables in `~/kwcov/fid/final_*.json`).
Fixes: `physics/hf/fidfix.py`, switch `INCOGNITA_FIDFIX` (default OFF). Tests: `tests/hf/test_fidfix.py`.

Modes in every table:

* **default**: the engine as the kwcov batches ran it (no switch, no deck line).
* **TALYS mode**: every INCOGNITA default that is ON and not TALYS switched to TALYS (`fidelity.TALYS_DECK` /
  `TALYS_ENV`): deck `fluxclose n; npwindow n; chancap n; nnleak n; exactfis n; alphatemp 0; sfexit n; kevleak2 n;
  heavymacs2 n; ftglobal n; ccexitnbnf n; tfold n; ctwcont n; alphaentr 0`, env `INCOGNITA_GRIDTOP=n
  INCOGNITA_SPECCLOSE=0 INCOGNITA_LOWEPOT=0 INCOGNITA_TARMASSFIX=0 INCOGNITA_ISOROTPASS=0`. The list is every
  `Incognita extension ... not TALYS` option of `input/defaults.py` whose default is on, plus every env switch whose
  default is on (`grep environ.get("INCOGNITA_...", "1"|"y")`). The production switches of
  `scripts/talysworld/engine_env.py` (GGDEADEND, DWBAUNIT, LEVCOMPLETE, TRAPFIX, WFCNORM, ...) are OFF in this
  repository's engine unless a launcher sets them, and the kwcov runs set none of them.
* **+fix**: `INCOGNITA_FIDFIX=ldcn,besttables,fitrisomer` (the three port fixes below).

Decision recorded: a gap counts as **deliberate** when TALYS mode closes it and a single INCOGNITA switch accounts for
all of it. Deliberate defaults are not flipped (they are calibrated, promoted engine options). A gap that survives TALYS
mode is a **port bug** and gets an opt-in fix.

## 1. Losses (what does not match stock, and why)

### 1.1 Gaps of the default engine on default decks: all deliberate

Every gap from the kwcov batches disappears in TALYS mode, and one switch accounts for each. None is a port bug.

| case | ours (default) | stock | gap | gap, TALYS mode | routine | cause | kind |
|---|---|---|---|---|---|---|---|
| Fe-56 (n,p) 14 MeV | 139.87 mb | 124.82 | **+12.1 %** | 0.00 % | `density/npwindow.py` (`bumps` via `density/models._adjusted`) | NPWINDOW: target-rho factor exp(dc sqrt(S_n)) on Ex >= max(Ecut+2, S_n-6) for targets with no measured D0 of their own (Fe-56 = Fe-55+n: none). Changes Fe-56's continuum density as the (n,n') residual, so less flux to (n,n')/(n,2n) and more to charged exits | deliberate (NPWPROMO) |
| Fe-56 (n,a) 14 MeV | 39.66 | 35.73 | **+11.0 %** | 0.00 % | same | same | deliberate |
| Fe-56 (n,2n) / (n,np) / (n,n') 14 MeV | 468.06 / 50.80 / 734.17 | 480.84 / 48.79 / 742.71 | -2.7 / +4.1 / -1.1 % | 0.00 % | same | same | deliberate |
| Fe-56 compound-only (n,p) 14 MeV (B5: 151.5 vs 131.5 with `gadjust`) | | | +15 % | 0.00 % (`gadjust 26 57 0.9` response 0.00 %) | same | same: the flux pre-equilibrium returns to the CN decays through the NPWINDOW-modified Fe-56 density | deliberate |
| Co-59 (n,p) / (n,a) 14 MeV | 52.77 / 38.45 | 50.16 / 36.61 | +5.2 / +5.0 % | 0.00 % | same | same (Co-59 = Co-58+n: no D0) | deliberate |
| Zr-90 (n,p) / (n,a) / (n,np) 14 MeV | 30.95 / 3.22 / 91.87 | 29.11 / 2.99 / 86.87 | +6.3 / +7.7 / +5.8 % | 0.00 % | same | same | deliberate |
| Fe-56 n spectrum 14 MeV, shape normalised | | | 6.7 % (p 9.9 %, a 5.4 %, gamma 2.3 %) | 0.05 % (all ejectiles integral <= 3e-5) | same | same (`b4_compare.py`, `npwindow n` alone gives the TALYS-mode numbers) | deliberate |
| U-238 fission 1 / 5 / 14 MeV | 58.63 / 685.20 / 1325.11 | 62.26 / 625.03 / 1270.62 | -5.8 / **+9.6** / **+4.3 %** | 0.00 / 0.01 / 0.00 % | `fission/wkb.py` (IDEA_EXACTFIS: `exactfis` per-hump correction C_k(U)) | exact 1-D per-hump transmission instead of TALYS's WKB table (fm5/6) | deliberate (`exactfis y` default) |
| U-238 (n,2n) 14 MeV | 1015.83 | 1049.76 | **-3.2 %** | +0.01 % | same | the fission it gains is taken from (n,2n) and inelastic | deliberate |
| U-238 (n,n') 5 MeV | 2697.79 | 2757.58 | -2.2 % | 0.00 % | same | same | deliberate |
| Au-197 capture 1 MeV | 104.37 | 143.59 | **-27.3 %** | +0.01 % | `compound/ccexitnb.py` (CCEXITNB2 rule) | for a target with no fission channel, the first CN's neutron exits to discrete NON-band target levels take the g.s. coupled-channels Tjlinc instead of the spherical inverse Tl: much more (n,n') to those levels, less capture and compound elastic | deliberate (CCEXITNB2, `ccexitnbnf y` default) |
| Au-197 (n,n') 0.1 / 1 MeV | 357.70 / 2003.88 | 156.82 / 1734.21 | +128 / +15.6 % | 0.00 % | same | same | deliberate |
| Au-197 elastic 1 MeV / capture 0.1 MeV | 3558.20 / 492.32 | 3788.05 / 505.55 | -6.1 / -2.6 % | 0.00 % | same | same (compound elastic) | deliberate |
| Au-197 capture 5 MeV | 16.51 | 17.12 | -3.5 % | +0.02 % | `density/npwindow.py` | NPWINDOW (Au-197 = Au-196+n: no D0) | deliberate |

The `npwindow n` / `exactfis n` / `ccexitnbnf n` columns (one switch flipped on top of default) reproduce the TALYS-mode
numbers to the digits printed; flipping each of `fluxclose`, `chancap`, `nnleak`, `kevleak2`, `alphatemp`, `gridtop`,
`heavymacs2` alone moved nothing in these cases.

### 1.2 Keyword responses that failed because of those defaults

`|ln(R/S)|`, R = engine(deck)/engine(no deck), S the same for stock, worst over channels with stock > 1 mb at 1/5/14 MeV
(Fe-56, Co-59, U-238; limit 2 %):

| deck | target | default | TALYS mode | TALYS mode + fix |
|---|---|---|---|---|
| fit y | Fe-56 | **4.01 %** (np 14) | 0.00 % | 0.00 % |
| cstrip a 1.1 | Fe-56 | 0.27 % | 0.00 % | 0.00 % |
| gadjust 26 57 0.9 | Fe-56 | 1.89 % | 0.00 % | 0.00 % |
| skipcn 26 56 | Fe-56 | **9.42 %** (npn 14) | 0.00 % | 0.00 % |
| ldmodel 2 | Fe-56 | **2.85 %** (na 14) | 0.00 % | 0.00 % |
| optmodall y | Fe-56 | **6.87 %** (na 14) | 0.00 % | 0.00 % |
| ldmodel 2; ldmodelCN 1 | Fe-56 | **7.81 %** | **7.91 %** (npn 14) | 0.00 % |
| best y | Fe-56 | **6.67 %** | **7.49 %** (npn 14) | 0.05 % |
| ngfit y | Co-59 | **8.22 %** (ng g.s. 1) | **8.22 %** | 0.00 % |
| best y | Co-59 | **8.22 %** | **8.22 %** | 0.32 % (np 5) |
| best y | U-238 | **9.19 %** (fission 5) | **2.77 %** (capture 14) | 2.77 % |
| ldmodel 1 92 238 | U-238 | **3.08 %** (n2n 14) | 1.08 % (capture 14) | 1.08 % |

So every kwcov response loss on Fe-56 was the default offset (NPWINDOW) or one of the two `best`-file bugs below, and
U-238's were EXACTFIS (under the U-238 best file EXACTFIS has no effect: `best y` fission is 0.00 % in both modes).
`preeqmode 3` (B7) is refused on this branch (`not ported: bonetti.f90`), so it was not retested.

### 1.3 Port bugs found (survive TALYS mode)

| case | ours, TALYS mode | stock | gap | + fix | routine | cause | kind |
|---|---|---|---|---|---|---|---|
| Fe-56 `ldmodel 2; ldmodelCN 1`, (n,np) 14 MeV | 43.07 | 46.62 | **-7.6 %** ((n,2n) -1.4, (n,n') +1.1 %) | 0.00 % | `input/defaults.Options.ldmodel_of`, reached through `compound/dens_reference._build_gamma_parameters` (`default_options` of a pseudo-target per chained CN) | the port builds options for a pseudo-target per compound nucleus of the chain; there the chain nucleus is (Zix, Nix) = (0, 0) and took `ldmodelCN`. TALYS gives `ldmodelCN` to the run's initial CN only (input_densitymodel.f90:245-249) | **port bug** (`ldcn`) |
| Fe-56 `best y` 5 MeV nonelastic / elastic / total | 1335.56 / 2213.31 / 3548.87 | 1343.83 / 2206.74 / 3550.57 | **-0.62** / +0.30 / -0.05 % | 0.00 % | `input/fitlib._cards` (best-file dirs for `omp/ompdeck.resolve`) | `awdadjust n 1. awdadjust-n.table`: TALYS opens the name in the cwd only; TENDL ships the table in `best/Fe056/tables/` (the stock harness copies it). The port searches best dir and `misc/tables` but not `tables/`, and `misc/tables/awdadjust-n.table` is a different table (0.80 vs 0.81 at 5 MeV) | **port bug** (`besttables`; resolution, not physics) |
| Co-59 `ngfit y` (and `best y`), Co-60 g.s. / isomer capture 1 MeV | 2.02 / 3.01 | 2.20 / 2.84 | **-7.9 / +6.1 %** (total capture exact) | 0.00 % | `input/fitlib._cards` (xsfit cells) -> `structure/levels.py` Risomer | ng.par gives `risomer 27 60 2.95161` for the INITIAL CN. TALYS reads that nucleus's levels (structure.f90:74, Risomer applied at levels.f90:313) before it calls xsfit (structure.f90:80), so the fitted risomer never acts in TALYS-2.25. The port applied it. (Stock with the three ng.par lines minus `risomer` reproduces stock `ngfit y` exactly.) | **port departure** (`fitrisomer`); arguably a TALYS ordering bug the port "corrected" |

### 1.4 Still open (traced to an area, not to one routine)

| case | ours | stock | gap | note |
|---|---|---|---|---|
| U-238 capture 14 MeV, default deck | 1.12 mb | 1.14 | -1.5 % (0.02 mb) | in every mode, also TALYS mode; total -0.01 %, elastic -0.02 %, (n,n') -0.25 % at 14 MeV too, so the incident coupled-channels solve at 14 MeV is the first suspect (ECIS numerics, within A-inc 1 %). Not chased: sub-0.1 mb. |
| U-238 capture 14 MeV, `best y` | 1.15 | 1.21 | -4.2 % (0.06 mb) | same cell; makes U-238 `best y` / `ldmodel 1 92 238` responses 2.77 / 1.08 % |

## 2. The fixes (opt-in, `INCOGNITA_FIDFIX`, default OFF)

`physics/hf/fidfix.py`: `INCOGNITA_FIDFIX` = comma list of `ldcn`, `besttables`, `fitrisomer`, or `all`. OFF never
changes a value (each hook asks `fidfix.on(name)` first); the switch is part of the stage-cache key (INCOGNITA_ prefix)
and of fitlib's card-cache key.

* **ldcn** -- `Options.ldmodel_of(0, 0)`: with an explicit `ldmodelCN`, an options set whose target is not the active
  run's target (`fitlib.active()`) is a pseudo-target build, and its (0, 0) takes the TALYS value of that nucleus in the
  real run (per-nucleus card, else `ldmodelall`). Only decks with an explicit `ldmodelCN` differing from `ldmodel` move.
* **besttables** -- `fitlib._cards`: the best file's `tables/` directory is searched before its `misc/tables`.
* **fitrisomer** -- `fitlib._cards`: a `risomer` cell from a fit file (`*fit y`, xsfit) for the initial compound
  nucleus is dropped; deck / best-file `risomer` lines and fitted values for other nuclei stay.

Tests (`tests/hf/test_fidfix.py`): switch parsing; `ldmodel_of` OFF = old rule, ON = run CN only, per-nucleus card kept,
inert without `ldmodelCN` or without an active run; Fe-56 `best y` reads D(5 MeV) 0.80 OFF / 0.81 ON; Co-59 `ngfit y`
drops exactly `risomer 27 60` ON and keeps a deck `risomer`.

Effect with the switch on (TALYS mode + fix vs stock):

| deck | worst channel before | after |
|---|---|---|
| Fe-56 `ldmodel 2; ldmodelCN 1` | (n,np) 14 MeV -7.6 % | 0.00 % |
| Fe-56 `best y` | (n,np) 14 MeV -7.2 %, nonelastic 5 MeV -0.62 % | +0.05 %, 0.00 % |
| Co-59 `ngfit y` | g.s. capture 1 MeV -7.9 % | 0.00 % |
| Co-59 `best y` | g.s. capture 1 MeV -7.9 %, (n,np) 14 MeV -6.5 % | 0.00 %, +0.19 % (worst: (n,p) 5 MeV +0.33 %) |

On default decks the fixes change nothing: `default+fix` = `default` for Fe-56, Co-59, Zr-90, U-238, Au-197 at every
energy (same digits, final tables). Test run (WSL, engine venv, switch unset): `test_fidfix.py` 8 passed;
`test_engine_c.py` 4 passed (bit-identical gate unchanged, no reference value touched); `test_kwcov_b2/b5/b6.py`
64 passed; `test_fitlib.py` + `test_npwindow.py` 13 passed.

## 3. Impact if the fixes were on by default

None on the published library. The production runs (`~/libv02/inputs`, engine 16606b356d6e, `NUCLIDO_TALYS_FIT=nodata`)
use the `nodata` arm: no best file, no fit file (`fitlib.modes`: `nodata` -> {nodata, s8}); their deck lines
(`lines_P`, `lines_A`, 6,417 files) are only ftable / ctable / wtable / globalwtable / dwbaimag / cstrip / alphaomp,
with no `ldmodelCN`, no `best`, no `*fit`, no table file. Checked by running the nodata arm with the fixes off and on
(section 4). What would move is only decks with `best y` (Fe-56: (n,np) 14 MeV ~+7 %, (n,2n) +1.5 %, nonelastic 5 MeV
+0.6 %; Co-59: (n,np) 14 MeV ~+7 %, Co-60 g.s. capture +9 % / isomer -6 % at 1 MeV), `*fit y` decks with a fitted
`risomer` of the CN, and user decks with `ldmodelCN` != `ldmodel`.

The deliberate defaults (NPWINDOW, EXACTFIS, CCEXITNB2) are what separate the library from stock TALYS, and they are
not changed here.

## 4. Production arm (`INCOGNITA_TALYS_FIT=nodata`, the library recipe): fixes and NPWINDOW

Engine only, 30 keV (MACS region) and 14 MeV; "fix" = `INCOGNITA_FIDFIX=ldcn,besttables,fitrisomer`; last column
NPWINDOW off (`INCOGNITA_NPWINDOW=0`). Stock column = stock DEFAULT deck (not the nodata recipe), for scale only.

| target | channel | E | nodata | nodata + fix | nodata, NPWINDOW off | NPWINDOW effect |
|---|---|---|---|---|---|---|
| Fe-56 | capture | 30 keV | 29.96 | 29.96 | 29.96 | 0 |
| Fe-56 | (n,p) / (n,a) / (n,2n) | 14 MeV | 140.07 / 39.66 / 460.84 | identical | 125.00 / 35.73 / 473.42 | +12.1 / +11.0 / -2.7 % |
| Co-59 | capture | 30 keV | 59.00 | 59.00 | 59.00 | 0 |
| Co-59 | (n,p) / (n,a) / (n,2n) | 14 MeV | 53.65 / 38.46 / 756.97 | identical | 50.97 / 36.62 / 763.71 | +5.3 / +5.0 / -0.9 % |
| Zr-90 | capture | 30 keV | 30.67 | 30.67 | 30.67 | 0 |
| Zr-90 | (n,p) / (n,a) / (n,2n) | 14 MeV | 30.95 / 3.22 / 638.55 | identical | 29.11 / 2.99 / 630.55 | +6.3 / +7.7 / +1.3 % |
| Au-197 | capture | 30 keV / 14 MeV | 825.80 / 1.26 | identical | 825.80 / 1.26 | 0 / -0.3 % |

So: turning the three fixes on by default moves **nothing** in the library recipe (every digit identical). The 14 MeV
charged-particle excess vs stock TALYS that the library carries is NPWINDOW's (+5 to +12 % on (n,p)/(n,a) for
D0-unanchored targets); MACS / 30 keV capture is untouched by it (the factor acts on the target's continuum above
max(Ecut+2, S_n-6), which a 30 keV neutron cannot reach as (n,n')).

## 5. B8 fission gaps (coordinator 2026-11-08): traced, same deliberate causes

| case | default | stock | gap | TALYS mode | one switch off | cause |
|---|---|---|---|---|---|---|
| Th-232 fission 5 / 14 MeV | 560.03 / 1138.53 | 457.81 / 1026.95 | **+22.3 / +10.9 %** | 0.00 / +0.01 % | `npwindow n`: +1.6 / +1.8 %; `exactfis n`: +20.5 / +9.2 %; both: 0.00 / +0.01 % | NPWINDOW (Th-232 = Th-231+n: no D0) lowers the (n,n') competition of the first CN, so more first-chance (Th-233) fission; EXACTFIS the last 1.6-1.8 % |
| Th-232 (n,2n) 14 / (n,n') 5 MeV | 1278.37 / 2754.94 | 1361.60 / 2860.07 | -6.1 / -3.7 % | 0.00 % | same | same |
| U-235 fission 5 MeV / (n,2n) 14 MeV | 1308.91 / 120.79 | 1282.16 / 132.09 | +2.1 / -8.6 % | 0.00 % | `exactfis n`: 0.00 / +0.01 % | EXACTFIS (U-235 is D0-anchored: NPWINDOW does not apply) |
| U-238 fission 14 MeV / (n,2n) 14 MeV | 1325.11 / 1015.83 | 1270.62 / 1049.76 | +4.3 / -3.2 % | 0.00 % | `exactfis n`: same | EXACTFIS (section 1.1) |

B8's per-chance numbers (Th-233 +27 % at 14 MeV, U-235 first chance +17.6 % at 5 MeV) are pieces of these totals; the
totals close to 0.00 % in TALYS mode with the same one or two switches, so no fission port bug is indicated. Not
checked here: the per-chance split itself in TALYS mode (B8's harness, `~/kwcov/stock/b8/`).

## 6. psfsgl (KWCOV B15, branch `kwcov15`): tabulated PSF energies in single precision

The fourth opt-in fix, `INCOGNITA_FIDFIX=psfsgl` (default OFF; `fidfix.py` docstring, `gamma/parameters.py`
`table_arrays` and the Tqrpa grid). It closes B13's loss (1): U-239 f_E1 (strength 9, T-dependent smlo2019 table) at
Egamma = 0.4 / 0.6 MeV was 9.08e-10 / 1.54e-9 against stock 2.12e-9 / 1.01e-9 (psf092239.E1 89 %, cross_g.tot
19.7 %). Cause: gammapar.f90 stores `ee + etable` and the wtable stretch `Emid + (Eq - Emid) * wt` in real(sgl), so
even at wt = 1 the energies become 0.39999962 / 0.60000038, and Tqrpa is the single-precision sum of 0.2 steps; the
port did both in double (0.40000000000000036), so `locate` and the `eb <= et` / `ee <= et` choice of
fstrength.f90:401-411 (temperature column vs photoabsorption column) flipped wherever a table energy equals a Tqrpa
temperature. With the fix: 2.1185e-9 / 1.0096e-9 = stock; other energies move ~5e-7 relative.

Engine impact (fidelity.py, default and TALYS mode, with and without the fix; mb):

| target | cell | default | default + psfsgl | TALYS mode | TALYS mode + psfsgl | stock |
|---|---|---|---|---|---|---|
| U-238 | capture 0.1 MeV | 113.52 | 113.52 | 113.62 | 113.61 | 113.61 |
| U-238 | capture 0.5 MeV | 81.32 | **81.23** | 81.36 (+0.12 %) | **81.26 (0.00 %)** | 81.26 |
| U-238 | capture 1 MeV | 86.82 | 86.82 | 86.70 | 86.70 | 86.70 |
| U-238 | fission 5 MeV | 685.20 | 685.14 | 625.09 | 625.03 | 625.03 |
| U-238 | every other cell (0.1-14 MeV) | | <= 0.01 % | | <= 0.01 % | |
| Fe-56, Co-59 | every channel, 0.03 / 0.5 / 1 / 5 / 14 MeV | | identical to 0.01 mb | | | |
| Au-197 | capture 0.03 / 0.5 / 1 / 5 MeV | 834.36 / 207.81 / 104.37 / 16.51 | identical | 834.35 / 238.59 / 143.60 / 17.12 | identical | |

So on by default it would move U-238 capture at 0.5 MeV by -0.11 % (towards stock) and leave the rest at print level.
