# INCOGNITA thermal scattering laws, tsl-v0.1

These are two S(α,β) laws built from our own models: molecular dynamics or DFT phonons, processed through NJOY LEAPR. No evaluated
thermal scattering law was used as input. ENDF/B-VIII.1 appears only as a comparator.

**In one line:** both laws tie ENDF/B-VIII.1 on criticality benchmarks and on sample-independent measurements. Neither is
shown to be better. Their value is independence: a second, open, physics-built answer for the two most common moderator materials.

## H in H₂O (`water/`)
- **Model:** TIP4P/2005f MD (1024 molecules, 293.6–600 K, OpenMM). H-projected VACF density of states; Egelstaff–Schofield
  diffusion from the MD; LEAPR; Sears free-atom σ = 20.488 b.
- **Passes**
  - Total cross section vs EXFOR, 10 µeV–10 eV: mean C/E 1.004–1.036 by band (VIII.1 1.000–1.037).
  - Criticality, Δk vs VIII.1: development set LCT-008/MCT-002, 6/6 within ±35 pcm, range −54 to +75 pcm. Held-out set
    PST-001/HST-001, 6/6 within ±35 pcm, mean +38 ± 14 pcm. |C−E| shrinks in 3 cases and grows in 3.
- **Losses (true)**
  - MD diffusion is 8–11 % slower than measured at 293–350 K, so the quasi-elastic peak is about 10 % too narrow.
  - Both files sit +3–4 % above measurement below 10 meV, ours and VIII.1 alike.
  - Double-differential spectra: median area C/E 1.150 (VIII.1 1.147); shape RMS 0.351 (VIII.1 0.343).
  - Our table ends at 4.9 eV, with free gas above it; VIII.1 runs to 10 eV.

## Be metal (`be-metal/`)
- **Model:** DFPT harmonic phonons (hcp Be), incoherent inelastic, coherent elastic from the lattice.
- **Passes**
  - 14/14 ICSBEP Be cases within 3σ. Δk vs VIII.1 has mean −17 ± 17 pcm and ranges from −167 to +125 pcm.
  - Ultracold-neutron up-scattering, 93–296 K: mean C/E 0.926.
  - Temperature dependence of transmission: r 0.81.
- **Losses (true)**
  - Double-differential spectra: R 0.57, about the same as VIII.1's 0.58. The cause is the incoherent approximation, which both files use.
  - Bragg-edge positions fail by the letter of the gate for every file tested, VIII.1 included.
  - Below 200 K, UCN up-scattering C/E is 0.76.

## Not included
- **Graphite.** Every own graphite law so far fails at least one pre-registered gate (GR1, GR2, GRAPHFUNC arm L). Work continues (GRAPHFUNC2).

## Files
See `SHA256SUMS`. Each law ships as an ENDF-6 MF7 tape (water 3.2 MB, Be 9.5 MB). The OpenMC HDF5 files (177 MB, 574 MB) are too large
for git. Rebuild them with `openmc.data.njoy.make_ace_thermal` (error 0.001, nbin 16), then `openmc.data.ThermalScattering.from_ace`.
Our build hashes: water b6085fe5…, Be 5e2c3cb6….
Every number above comes from the pre-registered validation cards TSLWATER, LIGHTEVAL1 §2 and TSLSOLID3. Those cards are not yet in this repository.
