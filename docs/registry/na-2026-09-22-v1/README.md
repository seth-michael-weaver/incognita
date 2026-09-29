# Prospective (n,a) registry na-2026-09-22-v1

Predictions made BEFORE any measurement exists: 171 long-lived targets (Z 24-83; 53 stable, 118 radioactive with T1/2 > 30 d) that have NO neutron (n,a) or (n,xa) record in EXFOR (local copy of 2026-09-09).
Energies [5, 8, 10, 12, 13, 14, 14.5, 15, 16, 18, 20] MeV. Columns: v1 = the confirmed (n,a) recipe (docs/release/na_v1/README.md); hybrid = v1 shifted toward a 14 MeV (N-Z)/A systematics (NOT yet confirmed: this registry is its test); default_talys = what TENDL's no-data recipe gives.
Intervals: empirical |log10(model/data)| quantiles of v1 on the fresh confirm sets (68 %: 0.300 dex, 95 %: 0.697 dex; default TALYS on the same sets: 0.486 / 0.960). They include measurement scatter.
Scoring rule (fixed now): when a measurement of sigma(n,a) or sigma(n,xa) on a listed target appears, score log10(model/data) for v1, hybrid and default at the measured energy (log-log interpolation in this grid); report rms, bias and the fraction inside the 68/95 % bands, per model.
Each row carries entry_hash = sha256 of its canonical JSON; MANIFEST lists the sha256 of every file; MANIFEST.sha256 is the hash to timestamp.

## Rivals (added 2026-09-22, after the stamp)
`rivals.csv` (sha256 cf55bd82013d4d2a2dc5eb2583c6541dd4dcd387d9c841fd59f13eeb27115add): JENDL-5, TENDL-2025, ENDF/B-VIII.1, JEFF-3.3 and CENDL-3.2 on the same targets and grid ((n,a) = MT107; (n,xa) = sum of alpha-emitting MTs). These are published library values, not our predictions, so they need no timestamp; the watch scores them next to v1 so a new measurement is a head-to-head none of the models has seen.

## Note for this distribution
The frozen files predate the project's rename and keep their original labels (for example the pre-rename name of the
(n,α) recipe switch, now `INCOGNITA_NA_V1`, in the `model` column of `predictions.csv`), so that their hashes still
verify against the timestamped manifest. `rivals.csv` holds evaluated-library values and is not distributed here; it can
be rebuilt from libraries you stage.
