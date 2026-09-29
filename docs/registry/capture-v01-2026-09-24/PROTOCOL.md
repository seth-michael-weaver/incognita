# Capture registry v0.1 (library-value-free model), frozen 2026-09-24

**Status: frozen.** `MANIFEST.sha256` lists the sha256 of `capture_nuclides.csv`, `capture_ng_grid.csv.gz` and this file.
`MANIFEST.sha256.ots` is its OpenTimestamps proof (stamped 2026-09-24 at the maintainer's ruling; only the hash left the
machine). The proof is pending until a Bitcoin block includes it; the upgraded (anchored) proof replaces it when available.
It proves the predictions existed by the stamp date. Verify: `sha256sum -c MANIFEST.sha256`, then `ots verify MANIFEST.sha256.ots`.

**Why it exists (REDTEAM M6).** The stamped capture registry `blind-2026-09-13-v0` was frozen from the release candidate, whose
Stage B blended ENDF/B-VII.1 values in Fe–Sn and the actinides, and its MACS columns are ~11 % low (erratum in `../CHAIN.jsonl`).
It stays published as a pre-independence registry. This folder holds the same targets predicted by the shipped model.

**Targets.** The 2,524 nuclides of `blind-2026-09-13-v0` minus Fe-74 (not in the v0.1 library): 2,523. `status_at_freeze` is copied
from v0 (determined at the v0 freeze, 2026-09-13; not re-derived). Scored, as for v0, are the nuclides with no keV–MeV differential
capture data at that freeze (never_measured, macs_only, thermal_or_integral_only): 2,292.

**Model.** INCOGNITA v0.1 library (`library/v0.1/`, INDEP_FIX2 build, 2026-09-23), taken verbatim:
```
69f956eac5acb563a7aac5e02b8f2567948e335501657b9bc047f0dfbb6ecb59  capture_v01_indep.parquet
ffce1c21b2049b2da290ad85e8cd9cc86b98596dfa110fd973d1f074553fa2c4  macs_kt_v01_indep.csv
```
- `capture_ng_grid.csv.gz`: σ(n,γ) on the library's 64-point grid (1 keV–20 MeV) with the 68 % and 95 % half-widths in log10.
- `capture_nuclides.csv`: tier, σ at 30 keV, and MACS at kT = 5–100 keV with the 68 % factor at each kT.

**Scoring.** `scripts/registry/score_capture_registry.py --registry <this folder>` (same columns as v0): rms of log10(prediction /
measurement) on EXFOR data compiled after the freeze, and the 68 % coverage of `log10_halfwidth`, next to the staged libraries.
