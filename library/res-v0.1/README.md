# INCOGNITA resonance-region hybrids res-v0.1 (OpenMC HDF5)

9 nuclides whose resonance region is INCOGNITA's own **and passed a physics judge** (differential data, pre-registered). Built 2026-10-27.

**These are HYBRIDS, not full own evaluations.** Only the resolved resonance range is INCOGNITA's own. Everything else (unresolved range,
fast-region cross sections, angular and energy distributions, nu-bar, fission spectra) is ENDF/B-VIII.1, used as a carrier.
Processed with NJOY 2016 and OpenMC 0.16 at 293.6/600/900 K.

## Losses and limits first
- **Pu-239: no passing own resonance file.** INCOGNITA's earlier Pu-239 file fails its own gates (fission resonance integral 387.5 b vs
  301 ± 10 b measured; thermal elastic 15.3 b vs 7.7 ± 0.5 b) and puts the PCI-001 benchmark 22 % low. Five refits to raw EXFOR data
  failed their pre-registered gates. A diagnosis is under way.
- **U-238 and O-16:** the own files make benchmark cases worse (U-238 PMF6 +90 pcm beyond 2σ; O-16 four cases by 141–172 pcm), and the
  new U-238 refit failed its held-out transmission check. Not released.
- **Not released, no physics judge yet (15):** Cr52, Gd157, Hf177, Hf178, Pu241, Ta181, Th232, U235, W182, W183, W184, W186, Zr91, Zr92, Zr96. These are earlier INCOGNITA resonance files (COVERAGE/URRPROD
  recipes) that pass our processing checks only. The same recipe produced the failing Pu-239 file, so they are held until judged.
- **Rejected by our own processing checks:** Cl-35 (NJOY LRF3→LRF7 two-range capture defect), Ni-60 (one reconstruction bin 4.6e-3 at
  4.75 keV, limit 2e-3). **Refits that failed:** Cr-52, Cu-63, Ni-62, Ni-64, Na-23 (resonance refit), Zr-91 (thermal refit worsened a
  benchmark by 117 pcm), Zr-92/94/96 resonance refits.
- **Provisional** verdicts (Ni-58, Zr-90, Cu-65) rest on few training sets; Cu-65 is worse than ENDF/B-VIII.1 in one hold-out range.
- "no DEV case": no criticality benchmark in our development set is sensitive to that nuclide; it is judged on differential data only.
  DEV Δk = k(this file in ENDF/B-VIII.1) − k(ENDF/B-VIII.1), same seed, ±35 pcm; "worsen" = change in |C/E| vs ENDF/B-VIII.1
  (negative = closer to experiment). Held-out benchmarks were never run on this set.

## Files
| nuclide | tier | own part (card) | judge | DEV Δk vs ENDF/B-VIII.1 (pcm) | sha256 |
|---|---|---|---|---|---|
| Fe56 | STRICT | own Reich–Moore fit to EXFOR transmission (STRUCTRRR) | PASS — held-out transmission χ²/pt 2.60 vs ENDF/B-VIII.1 2.99; thermal elastic fixed (old own file 21.9 b, measured 12.9 b) | LCT8c1:-65±35(worsen -12); LCT8c5:-4±35(worsen -2); LCT8c11:+22±35(worsen +22); MCT2pnl-30:+43±35(worsen -43); MCT2pnl-33:-22±35(worsen -22); MCT2pnl-35:-45±35(worsen -45) | `de6802208fbf9f8f…` |
| Ni58 | STRICT | own Reich–Moore fit to EXFOR transmission (STRUCTRRR) | PASS-provisional — provisional (one training set); G1 1.28 after one added level | MCT2pnl-30:+12±35(worsen -12); MCT2pnl-33:-6±35(worsen -6); MCT2pnl-35:-93±35(worsen -93) | `59c908d8afbb68c5…` |
| Zr90 | STRICT | own Reich–Moore fit to EXFOR transmission (ZRFIT) | PASS-provisional — provisional; held-out check cannot tell it from ENDF/B-VIII.1 | MCT2pnl-30:-68±35(worsen +68); MCT2pnl-33:+4±35(worsen +4); MCT2pnl-35:-103±35(worsen -95) | `e32d7da3746bd4a0…` |
| Cu65 | PROVISIONAL | own Reich–Moore fit to EXFOR transmission (STRUCT2) | PASS-provisional — provisional; elastic ~10 % high below 1 keV; worse than ENDF/B-VIII.1 in 10–100 eV hold-out | no DEV case | `d68662f4eba8d61a…` |
| Gd155 | STRICT | own Reich–Moore fit to EXFOR (GELINA + J-PARC) (GD155FIT) | no-harm PASS — no-harm PASS: capture RI 1495 b vs 1532 ± 8.5 b measured (misses 2σ by 2.7 b; old own file 535 b) | no DEV case | `03f75e9a075fe581…` |
| Pu240 | STRICT | EXFOR-reported resonance parameters, assembled by INCOGNITA (RESPEAKS2) | PASS — experimenter parameters; Explorer peaks live since 10-26 | MCT2pnl-30:+47±35(worsen -47); MCT2pnl-33:+32±35(worsen +32); MCT2pnl-35:-24±35(worsen -24); PCI1:+96±35(worsen -96); PMF1:-23±35(worsen +23); PMF6:+40±35(worsen -40) | `164e24a239854fc7…` |
| F19 | STRICT | own statistical ladder, bound level refitted to EXFOR thermal constants (THERMFIX) | PASS — thermal σ_el 4.70 → 3.63 b (measured 3.70); hold-out σ_tot C/E 1.24 → 0.96 | no DEV case | `c235b4ce0aeb6cb1…` |
| Na23 | STRICT | own statistical ladder, bound level refitted to EXFOR thermal constants (THERMFIX) | PASS — thermal σ_el 8.31 → 3.27 b (measured 3.26); b_coh not met | LCT8c5:+33±35(worsen +33) | `dc030292ad7afb82…` |
| Zr94 | STRICT | own statistical ladder, bound level refitted to EXFOR thermal constants (THERMFIX) | PASS — thermal σ_el 6.30 → 8.03 b (measured 8.48) | MCT2pnl-30:-41±35(worsen +41); MCT2pnl-33:+29±35(worsen +29); MCT2pnl-35:-42±35(worsen -42) | `2ff7a23fe1dadb22…` |

Tier STRICT = every RESINTEG selection rule met and no finished DEV case worsens; Cu-65 is capped at PROVISIONAL by its card (STRUCT2 PASS-provisional, no DEV case).
Inside names match ENDF/B-VIII.1's (e.g. `Fe56`). To use one, replace that entry in your `cross_sections.xml`
(`openmc.data.DataLibrary`: remove the existing entry, then `register_file` ours). `MANIFEST.json` here lists arm, tier and verdict per file.
