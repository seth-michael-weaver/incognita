# RESFILL site data: capture (and elastic/total) from 1e-5 eV to the 1 keV join, every explorer nuclide

Produced by RESFILL (PREREG `rl/resfill/PREREG.md` 4e4433624 + amendments d4ea930b5). INCOGNITA's own model only:
no Atlas/RIPL resonance values, no TARES, no evaluated library as input. ENDF/B-VIII.1 was used only as a comparator.

## Files
- `rr_index.json`: `{schema, T_K, E_unit, xs_unit, engine, prereg, n, kinds, rows[]}`; one row per nuclide:
  `Z, A, sym, kind, n` (points), `anchored` (curve forced through the measured thermal capture), `thermal_exp`
  (an EXFOR thermal value exists), `hold` (RI held out for judging), `fallback`, `segments` [[lo, hi, kind]], `join`.
- `rr/<Z>/<A>.json`, one per explorer row (6168), at most 600 points, 0 K:
  - `Z, A, sym, kind, label` (show `label` beside the curve), `T_K` = 0, `units` {E: eV, xs: b}
  - `segments`: [{lo, hi, kind, what}] describing what each energy range is
  - `E` (eV, ascending), `cap`, `el`, `tot`, and `fis` for fissile targets (barns, same grid as `E`)
  - `thermal`: {E: 0.0253, cap_model_b, exp: {value, unc, entries (EXFOR), tier} or null, anchored}
  - `ri`: {cut_eV: 0.5, model_b, exp or null, role}; RI = ∫σγ/E dE from 0.5 eV (to 20 MeV, explorer curve above 1 keV)
  - `join`: {E_eV: 1000, cap_explorer_b, ratio}: where this curve meets the explorer's 64-point grid
  - `seed` (statistical/own-fit: realisation rule, r, seed, K; null for smooth), `sources`, `engine`
  - fallback files only: `fallback_from_statistical: true`, `note`
- Points are down-sampled from the full NJOY RECONR (0 K, err = errmax = 1e-4) curve: every capture peak ≥ 1 % of the
  largest peak and its valleys are kept, the rest is log-log filled. Plot with log-log interpolation between points.
  Narrow resonances in dense ladders are thinned: the curve shows the resonance structure, not every resonance.

## Kinds (counts) and whether they may go public
| kind | n | public? | suggested label |
|---|---|---|---|
| `own-fit` | 2 (U-238, Gd-157) | yes | "INCOGNITA's own resonance fit to EXFOR data below 300 eV; statistical resonances 300 eV–1 keV" |
| `statistical` | 395 | yes: G2 passed (narrowly) | "statistical resonances from INCOGNITA's own average parameters, not measured resonances" (+ "passes through the measured thermal capture" when anchored) |
| `smooth` | 5771 (12 are fallbacks) | yes | "smooth: no resonances drawn; 1/v capture …" (the file's `label` says whether it goes through a measurement) |

Statistical resonances are ONE random realisation with the right average spacing and widths: individual peak
positions are NOT the real resonances. Unanchored smooth curves extend the 1 keV model value as 1/v; real thermal
values can differ by orders of magnitude.

Total size ≈ 18.8 MB.
