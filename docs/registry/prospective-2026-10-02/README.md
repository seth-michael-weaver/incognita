# INCOGNITA prospective freezes, 2026-10-02

These are sha256 hashes of frozen INCOGNITA predictions, published **before** the corresponding measurements are released,
so that anyone can later check that the predictions were not changed after the data appeared.
Only the hashes are published here. The predicted values themselves (curves, MACS, resonance averages, level densities,
gamma strengths, 68/95 % intervals) will be released later in the files these hashes cover; `sha256sum -c HASHES.txt` then verifies them.

Engine: INCOGNITA's TALYS-2-based engine, physics configuration B55. No evaluated-library values enter these predictions.
The interval layer (B57) is calibrated on already-measured nuclei; for nuclei far from measured ones its bounds may be too narrow.
Not blind for us (we have seen data): Tm-171 MACS, Nb-94 MACS, Sn-130.

## Freezes
| id | what | MANIFEST sha256 |
|---|---|---|
| B47_knockfix2 | board row (906 targets) | `1baa03425f18b2143b5bacadce41f387082fc3cb6c450e2929a92388f39dc13a` |
| B53_physbase | PB* physics baseline (906) | `ce3e0a276473b2643f1cccc7ebefae6efb77f2391aaf8df8c0325ca142d58b36` |
| B54_combine8 | PB* + peunits (1,216) | `66f112918ba82ce9bb2dada9d1cd2dabe3e1ff5403a5da214984b5cc9c04da61` |
| B55_ctrefit | PB* + ctwindow2 + k_CR (1,216): curves, 8 channels | `35523f180b21a527372e39409f6a9832ae71e6e9e1e8263140ede16522ef8578` |
| B56_fo_new | B55 recipe on 8 new targets: La-146, La-147, Sr-94, Ga-75, Sn-130, Tm-171, Eu-155, Hf-182 | `c64926cd977d17c389bd6e3228864b5332b7368062ba2071722203e4ecad5d6b` |
| B57_fo_int | 68/95 % interval layer on B55+B56 (spent-calibrated; see README) | `d810179f013de0dfd2b864068729516c14d970bdbe592e2a8a303267cd257a26` |
| B58_fo_macs | MACS kT 5-100 keV (+ bounds) for 1,224 targets | `4b3b8d00a3be41dfec58a3e11e6b6e032d801f688d7eeaac51991116aaba1ae5` |
| B59_fo_res | D0, D1, <Gg>s/p, S0, S1, R' for 1,224 targets | `81197bc5f117399e55a5ca85ea2b81b5864b3dae777145f984014e20a2284c72` |
| B60_fo_ing | rho(Ex[,J,pi]) and fE1/fM1(Eg) for 25 beta-Oslo/surrogate/Oslo compounds | `01c428f9493a64be264ad05b60de94c41219494cede4ebbcfd66d58e2d44635d` |

## Targets these freezes are meant for
| nuclide | measurement | freeze with the curves |
|---|---|---|
| Cs-135 | (n,g) MACS by activation | B55_ctrefit |
| Ti-44 | (n,p), (n,a) | B55_ctrefit |
| Ca-41 | (n,a) (also (n,p)) | B55_ctrefit |
| Y-88 | transmission -> resonance params / capture constraint | B55_ctrefit |
| La-147 | (n,g) via beta-Oslo (NLD+gSF of La-148) | B56_fo_new |
| Ga-75 | (d,p g) surrogate for (n,g) | B56_fo_new |
| Se-84 | d(84Se,p) surrogate for (n,g) | B55_ctrefit |
| In-110 | (n,g) via simultaneous (p,g)/(p,n) (HECTOR) | B55_ctrefit |
| Se-79 | (n,g) TOF | B55_ctrefit |
| Nd-146 | (n,g) TOF + MACS activation | B55_ctrefit |
| Sn-130 | d(130Sn,p) surrogate for (n,g) | B56_fo_new |
| Pu-241 | (n,g)/(n,f) ratio; (n,f) | B55_ctrefit |
| K-40 | (n,p0/1), (n,a0) | B55_ctrefit |
| Ni-56 | (n,p) via surrogate | B55_ctrefit |
| Ge-80 | (d,p g) surrogate; level lifetimes (RIKEN) | B55_ctrefit |
| Y-88 | (n,2n) on NIF capsule deposit | B55_ctrefit |
| Sr-93 | (n,g) via beta-Oslo (Sr-93..95 NLD+gSF) | B55_ctrefit |
| Zr-98 | NLD + gSF via beta-Oslo of Y-97..100 -> Zr-96..99(n,g) | B55_ctrefit |
| Ba-142 | (n,g) via beta-Oslo of Cs-143 (NLD+gSF Ba-143) | B55_ctrefit |
| Sm-157 | beta-Oslo NLD+gSF Sm-156..159 (PAC-approved) | B55_ctrefit |
| Xe-135 | (n,g) via beta-Oslo / inverse-Oslo of Xe-136 | B55_ctrefit |
| Nb-96 | (n,g) via (p,g)/(p,n) | B55_ctrefit |
| Sm-147 | (n,g) | B55_ctrefit |
| K-39 | (n,p), (n,cp) | B55_ctrefit |
| Sr-87 | (n,g) | B55_ctrefit |
| U-236 | (n,f) | B55_ctrefit |
| Am-243 | (n,f) | B55_ctrefit |
| Sm-151 | transmission | B55_ctrefit |
| Tm-171 | transmission | B56_fo_new |
| Zn-68 | (n,g) | B55_ctrefit |
| Zr-90 | (n,g) fast (surrogate benchmark) | B55_ctrefit |
| Tc-99 | (n,g) high energy | B55_ctrefit |
| Al-26 | (n,p), (n,a) | B55_ctrefit |
| Cl-35 | (n,p) | B55_ctrefit |
| Nb-94 | SACS/MACS activation | B55_ctrefit |
| Zr-88 | (n,g) cascade, isomer ratio; n_TOF absorption | B55_ctrefit |
| Ra-228 | (n,g) thermal -> Th-229 | B55_ctrefit |
| U-239 | surrogate Pg/Pn/P2n/Pf (d,p) on U-238 in ESR | B55_ctrefit |
| Cl-36 | none | B55_ctrefit |
| Nb-94 | (n,g) TOF | B55_ctrefit |
| Tl-204 | (n,g) | B55_ctrefit |
| Zr-89 | (n,g) via 90Zr(p,p'g) surrogate | B55_ctrefit |
| Xe-132 | NLD+gSF Xe-133 (inverse Oslo) | B55_ctrefit |
| Sr-85 | (n,g) via (p,ag) surrogate | B55_ctrefit |
| Eu-155 | (n,g) TOF; also Kr-81, Pm-147, Gd-153, Ho-163, Ta-179; n_ACT@BDF: Cs-137, Ce-144, Fe-60, Hf-182, Pm-147, Ho-163, Tm-171 | B56_fo_new |
| O-17 | (n,a) | B55_ctrefit |
| Mg-25 | (n,a) | B55_ctrefit |
| Ta-180 | Oslo NLD/gSF Ta-180,181 | B55_ctrefit |

## Timestamp
`HASHES.txt.ots` is an OpenTimestamps proof (pending at commit time; Bitcoin-anchored within hours). Verify with `ots verify HASHES.txt.ots`. The git commit time on GitHub is a second, independent timestamp.
