# v0.1 library build (2026-09-23; E1 constant 1.0425)

6168 nuclei: EXTRAPOLATED 5611, INTERPOLATED 316, MEASURED 220, ANCHORED 21

Unmeasured chart-run nuclei left EXTRAPOLATED, by reason: {'rich side': 256, 'distance > 2': 1409, 'Z outside 26-83': 301, 'not in chart run': 3645, 'no structure data (CAPFAR)': 0, 'no data under register v2': 5}

| tier | nuclei | median 68 % factor at 30 keV | median 95 % factor at 30 keV |
|---|---|---|---|
| ANCHORED | 21 | x1.16 | x1.48 |
| EXTRAPOLATED | 5611 | x1.58 | x2.42 |
| INTERPOLATED | 316 | x1.34 | x1.80 |
| MEASURED | 220 | x1.24 | x1.65 |

No ENDF-6 transport files (independence policy, v0.1 scope). Floor-leak check: 0 shipped curves carry an engine floor/dropout point. The sealed coverage test of the shipped interval is docs/release/uq/FINAL674.md.

## Provenance (2026-09-23)
- The library-value-free recipe (no prior blend, KADoNiS measured-only, own E1 constant 1.0425), plus these fixes:
  (1) engine output-floor and dropout points repaired in every engine curve we use (floor-leak check 0 of 6,168);
  (2) resonance-bound fallbacks (MEASURED at bound 0: 22 -> 0);
  (3) our E1 width in the TALYS surrogate as well (the surrogate's default behaved as absolute width ~1.0, not the table constant) and in the spread arms;
  (4) curation register v2. Sn-126, Sn-128, Sn-130, Sn-132 and Tm-171 have no capture data left under v2, so they are EXTRAPOLATED.
- Registered vault read (folds 6-7) vs the RC: **WORSE by the registered rule**. Accuracy is within tolerance: D0-withheld +0.0063 [-0.0008, +0.0133], D0-assisted -0.0047 [-0.0103, +0.0014]. The D0-withheld 95 % coverage is 88.1 % (RC 91.6 %), outside the allowance.
- Channel tables are unchanged from the previous build (the same engine runs with our E1 constant)..
