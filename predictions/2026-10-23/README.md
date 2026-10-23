# Predictions registered on 2026-10-23, before the measurements

This directory holds INCOGNITA's predictions for neutron-induced cross sections that are being measured, or have been measured
but not yet published, at the time of writing. They were computed and committed before anyone (including us) could see the
results. When the measurements appear, they will be scored by the fixed rule in `PREREG.md`, and the results will be added in a
new file next to this one. Nothing in this directory will be edited.

Why do this: a model can always be made to agree with data it has already seen. A prediction written down before the data exist
cannot. This is the only kind of test that cannot be tuned to.

## Source check and target classes
On 2026-10-23, before publication and before any measured value was looked at, every target was checked independently against
public sources (conference agendas and slides, proposals, papers, theses). The check sorted the 37 targets into four classes
(the `class` column of `targets.csv`, with the reason and the supporting web page):

| class | count | what it means | how it is scored |
|---|---|---|---|
| `BLIND` | 16 | the measurement is done or under analysis, and no values of it were public on 2026-10-23 | **the headline**: only these targets decide the overall verdict |
| `PRELIM` (PRELIM-PUBLIC) | 12 | preliminary values or first results were already shown in public (talks, conference slides, proceedings); we did not look at them | scored by the same rule, reported separately, never in the headline |
| `CONTROL` | 4 | the quantity is already well measured, or first results were published before registration | scored as controls, reported separately; not a blind test |
| `PLANNED` | 5 | the measurement is only planned | long shots: scored separately if and when the data appear |

Other changes made by the check, all before publication:
- One target was removed because the registered quantity has already been published (the Nb-94 Maxwellian-averaged capture cross
  section, derived from n_TOF time-of-flight data in Phys. Rev. Lett. 137, 082701 (2026)).
- Energy ranges were cut where earlier published data overlap: Al-26 (n,p) now starts at 150 keV and Al-26 (n,α) at 160 keV;
  Am-243 fission is limited to 0.1–0.5 MeV, because n_TOF fission data from 0.5 to 20 MeV are already published. The predictions
  themselves were not recomputed: the headline values in the new ranges are read off the same frozen curves.
- Sources, dates and experiment labels were corrected where the check found better public evidence. Experiment codes and details
  that could not be found in public sources are marked "not confirmed in public sources".

## What is here
| file | content |
|---|---|
| `targets.csv` | one row per target: nucleus, reaction, energy range, laboratory, experiment, status, expected date, public source, class, check verdict and evidence |
| `predictions/<target>.csv` | every model's prediction over the registered energy range (mb), with INCOGNITA's 68 % and 95 % bands |
| `cells.csv` | headline values at a few energies (or kT) per target, every model side by side, with the target's class |
| `curves.csv.gz` | every model's full curve, 1 keV–20 MeV (or kT 5–100 keV for Maxwellian averages) |
| `PREREG.md` | how each target will be scored, and what counts as a win, tie or loss |
| `MANIFEST.json` | engine version, counts per class, and the root hash of the internal frozen set these files were exported from |
| `SHA256SUMS` | SHA-256 of every file here |

## Models
INCOGNITA (engine version 2026-10-22, production settings). Rivals at their default input: TALYS-2 (our port of its default
recipe, and the TALYS-2.24 program itself where we had a stored default run), the TENDL no-data recipe, CoH3 and YAHFC where
available, NON-SMOKER and BRUSLIB for capture. Evaluated libraries (ENDF/B-VIII.1, JENDL-5, JEFF-4.0, TENDL-2025) are shown for
context only: they were adjusted to data, so they are not used to decide the score.

## How to check the timestamp
1. The registration time is the time of the git commit that added this directory. On GitHub, open the directory's history, or
   run `git log --format='%H %cI' -- predictions/2026-10-23/` in a clone. The commit is part of the public history, so it cannot
   be changed without rewriting every later commit, which anyone who cloned the repository would notice.
2. Check the files have not changed since: run `sha256sum -c SHA256SUMS` in this directory (on macOS: `shasum -a 256 -c SHA256SUMS`).
3. Compare with the publication date of each measurement. Only measurements first made public after the commit time count.

## Scoring in one paragraph
For each data point, the error is log10(predicted/measured). Per target, each model gets the root-mean-square error over the
points both models cover. INCOGNITA wins a target against a rival if its error is smaller by more than the larger of 0.02 (in
log10) and the measurement's stated normalisation uncertainty; loses if larger by the same margin; otherwise it is a tie. The
overall (headline) verdict against each rival uses only the `BLIND` targets, with a bootstrap over nuclei, and waits until at
least five of them on five nuclei are scored. The other classes are scored the same way and reported in their own tables. Full
rule: `PREREG.md`.

## Caveats
- Several targets are radioactive or have few or no earlier measurements; these are the hardest and most informative tests.
- Most targets have older measurements of the same reaction; a target is blind because the new measurement is not yet public,
  not because the reaction was never measured.
- In the resolved-resonance region the models give resonance averages, so those points are not in the headline.
- The schedules in `targets.csv` are the laboratories' public plans; some measurements may be delayed or cancelled. A cancelled
  target is marked void, with the date, before any of its values are known.
- La-147 capture is an indirect (beta-Oslo) case: the registered reaction is 147La(n,γ)148La; the same plan also names
  146La(n,γ)147La, which is not registered here.

## Targets
One representative value per target (INCOGNITA, mb, with its 68 % band); every energy and every model is in the files.
The class of each target is in the `class` column of `targets.csv`, with the reason (`class_reason`) and the public page that supports it
(`verification_url`; `prior_public_url` where earlier results are public).

### Blind headline (confirmed measured or under analysis, no values public): 16

| target | laboratory | registered range | status | INCOGNITA at | value [68 %] |
|---|---|---|---|---|---|
| Cs-135_macs | CERN n_TOF NEAR (activation; counting at Felsenkeller) | kT 5-100 keV | measured-analysis | kT = 30 keV | 91.49 [76.6, 109] |
| Nd-146_macs | CERN n_TOF NEAR (+EAR2 TOF) | kT 5-100 keV | measured-analysis | kT = 30 keV | 90.51 [75.8, 108] |
| Er-164_capture | CERN n_TOF EAR1 | 3000-300000 eV | measured-analysis | E = 30000 eV | 1176 [892, 1.55e+03] |
| Sm-147_capture | CERN n_TOF EAR1 | 3000-300000 eV | measured-analysis | E = 30000 eV | 796.7 [648, 979] |
| Sm-149_capture | CERN n_TOF EAR1 | 3000-300000 eV | measured-analysis | E = 30000 eV | 1550 [1.26e+03, 1.9e+03] |
| Sm-152_capture | CERN n_TOF EAR1 | 3000-300000 eV | measured-analysis | E = 30000 eV | 477.6 [362, 630] |
| Sb-121_capture | CERN n_TOF EAR1 | 3000-300000 eV | measured-analysis | E = 30000 eV | 597.4 [486, 734] |
| Sb-123_capture | CERN n_TOF EAR1 | 3000-300000 eV | measured-analysis | E = 30000 eV | 379.8 [309, 467] |
| Sr-87_capture | CERN n_TOF EAR1+EAR2 | 3000-300000 eV | measured-analysis | E = 30000 eV | 136.9 [90.3, 208] |
| Pu-241_capture | CERN n_TOF EAR1 (TAC + fission chamber) | 3000-100000 eV | measured-analysis | E = 30000 eV | 824.2 [635, 1.07e+03] |
| Am-243_fission | CERN n_TOF EAR1+EAR2 | 100000-500000 eV | measured-analysis | E = 400000 eV | 138 [96.8, 197] |
| Al-26_np | CERN n_TOF EAR2 | 150000-1e+06 eV | measured-analysis | E = 1e+06 eV | 602.7 [447, 814] |
| Al-26_na | CERN n_TOF EAR2 | 160000-1e+06 eV | measured-analysis | E = 1e+06 eV | 64.33 [33.3, 124] |
| Ca-41_na | CERN n_TOF EAR2 | 1000-1e+06 eV | measured-analysis | E = 1e+06 eV | 118.3 [51.2, 274] |
| Nd-143_capture | LANSCE DANCE | 1000-100000 eV | measured-analysis | E = 30000 eV | 218.1 [178, 268] |
| Xe-124_capture | CSNS Back-n | 1000-100000 eV | measured-analysis (GTAF detector and 'trial measurement' not confirmed in public sources) | E = 30000 eV | 570.4 [464, 701] |

### PRELIM-PUBLIC (preliminary values already shown in public; scored separately): 12

| target | laboratory | registered range | status | INCOGNITA at | value [68 %] |
|---|---|---|---|---|---|
| Ag-109_macs | CERN n_TOF NEAR (B4C-filtered spectra) | kT 5-100 keV | PRELIM-SHOWN (C/E for the 109Ag(n,g)110mAg partial on public slides, 2026-10) | kT = 30 keV | 673.8 [564, 805] |
| Se-79_macs | CERN n_TOF EAR1 i-TED + EAR2 sTED | kT 5-100 keV | PRELIM-SHOWN (preliminary resonances shown; values not recorded) | kT = 30 keV | 231.7 [153, 351] |
| Cu-63_macs | CERN n_TOF EAR1 | kT 5-100 keV | PRELIM-SHOWN (preliminary results at ENC 2025) | kT = 30 keV | 112.3 [74.2, 170] |
| Cu-65_macs | CERN n_TOF EAR1 | kT 5-100 keV | PRELIM-SHOWN (preliminary results at ENC 2025) | kT = 30 keV | 57.1 [37.7, 86.5] |
| K-39_np | CERN n_TOF EAR2 | 5e+06-2e+07 eV | PRELIM-SHOWN (first results shown; values not recorded) | E = 1.4e+07 eV | 100.9 [68.7, 148] |
| K-39_na | CERN n_TOF EAR2 | 5e+06-2e+07 eV | PRELIM-SHOWN (first results shown; values not recorded) | E = 1.4e+07 eV | 122.9 [78.5, 192] |
| Gd-160_capture | CERN n_TOF EAR1+EAR2 | 3000-300000 eV | PRELIM-SHOWN (preliminary in EPJ Web Conf 284 09002 2023; final analyses concluded) | E = 30000 eV | 150.5 [114, 198] |
| Mo-100_capture | CERN n_TOF EAR1+EAR2 | 3000-300000 eV | PRELIM-SHOWN (first EAR2 results at a public conference, 2025-09) | E = 30000 eV | 95.16 [77.4, 117] |
| Sn-124_capture | CERN n_TOF EAR2 | 3000-300000 eV | PRELIM-SHOWN (preliminary results on public slides) | E = 30000 eV | 18.86 [15.3, 23.2] |
| Pu-241_fission | CERN n_TOF EAR1+EAR2 | 1000-2e+07 eV | PRELIM-SHOWN (very preliminary results, 2025-12) | E = 1e+06 eV | 1281 [899, 1.83e+03] |
| U-236_fission | CERN n_TOF EAR1+EAR2 | 100000-2e+07 eV | PRELIM-SHOWN (preliminary results, 2026-06) | E = 1e+06 eV | 473.7 [332, 675] |
| Y-88_n2n | LLNL NIF (radiochemically doped capsules) | 1.3e+07-1.5e+07 eV | PRELIM-SHOWN (results announced for APS DPP 2025; not looked at) | E = 1.4e+07 eV | 1113 [948, 1.31e+03] |

### Controls, not blind (already measured or first results published; kept on record): 4

| target | laboratory | registered range | status | INCOGNITA at | value [68 %] |
|---|---|---|---|---|---|
| Ni-64_macs | CERN n_TOF EAR2 | kT 5-100 keV | PRELIM-PUBLIC (first results published 2026-04) | kT = 30 keV | 11.22 [7.41, 17] |
| U-238_capture | CERN n_TOF EAR1 | 3000-300000 eV | measured-analysis | E = 30000 eV | 416.1 [321, 540] |
| F-19_na | GANIL SPIRAL2 NFS (SCALP) | 1e+06-2e+07 eV | PRELIM-SHOWN (2021 run in a 2024 PhD thesis); second run planned | E = 1.4e+07 eV | 11.29 [7.21, 17.7] |
| U-238_n2n | GANIL SPIRAL2 NFS (GRAPhEME+GAINS) | 6.2e+06-2e+07 eV | measured-analysis | E = 1.4e+07 eV | 1032 [837, 1.27e+03] |

### Planned measurements (long shots; scored separately if they appear): 5

| target | laboratory | registered range | status | INCOGNITA at | value [68 %] |
|---|---|---|---|---|---|
| O-16_na | GANIL SPIRAL2 NFS (SCALP active target) | 2.4e+06-2e+07 eV | planned | E = 1.4e+07 eV | 173.4 [111, 271] |
| F-19_np | GANIL SPIRAL2 NFS (SCALP) | 4e+06-2e+07 eV | planned (needs H-free detector upgrade) | E = 1.4e+07 eV | 14.72 [10, 21.6] |
| Y-88_capture | LANSCE DICER (transmission) | 1000-100000 eV | planned (fall 2026 run) | E = 30000 eV | 397.9 [263, 603] |
| Zr-90_capture | LANSCE DANCE (Notre Dame) | 1000-500000 eV | planned | E = 30000 eV | 25.51 [20.8, 31.3] |
| La-147_capture | ANL nuCARIBU + SuN (beta-Oslo) | 1000-1e+06 eV | planned (H2 2026) | E = 30000 eV | 55.35 [45, 68] |
