# Fusion chapters: plan

Four new chapters, 29–32 (numbers follow page order), in a new **Part three · Fusion** after the six Expert chapters.

Revised 2026-11-03 after rebasing onto origin/main, which had gained ten chapters (xsec, binding, landscape, neutrons,
fisout, products, tof, slowing, doppler, critical), page-order numbering and standard physics titles.

## Where they go, and why

- **After chapter 28, as part three.** Chapters 1–28 follow one neutron into one heavy nucleus, in the order the engine
  computes it. Fusion is a different reaction family: two light, charged nuclei, a plasma, a magnet. Putting it in the
  middle (say after Fission) would break that order, and would shift every later chapter number and the instructors
  tables in 14 languages. Chapter 2 (binding) already shows fusion energy from the binding curve, and chapter 5 (neutrons)
  the Coulomb barrier in one dimension; part three picks up from there.
- Part three climbs through the levels on its own: 29 Intro, 30 Intermediate, 31 Advanced, 32 Expert. The part
  head says so. Each chapter's level tag comes from `LEVEL` in kit.js, the same as the other chapters.
- The last chapter brings it back to neutrons in materials, where INCOGNITA actually has data.

## Survey: visual techniques already on the site

| Technique | Where |
|---|---|
| Canvas-2D lit spheres (`g.ball`), packed nuclei (`g.nucleus`), jiggling nucleons | everywhere |
| Additive glow and streaks, 3D-projected nucleus, scroll zoom, click to fire | intro (hero) |
| CPU per-pixel field via `ImageData` (eikonal wave, phase bands) | omp, direct |
| Profile "landscapes" with gradient ground (`g.ground`, `fground`) | fission, compound, densities, layers |
| Doors with lit gaps (`g.door`) for channel shares | decay, gamma, measure |
| Particle streams and piles / histograms that fill up | preeq, cascade, measure, resonance |
| Breit–Wigner peak forests, ladders and shelves of levels | resonance, structure, averages |
| Monte Carlo cascades, one history at a time, tallies | cascade, strength, exciton |
| Complex-plane path (S-matrix), Numerov wave animated | optical |
| Liquid drop that necks and splits | fission |
| Binding curve with a fuse slider (fusion Q from B/A) | binding |
| 1-D Coulomb barrier with a rolling ball, proton vs neutron | neutrons |
| 2-D chart of nuclides from AME/NUBASE data | landscape |
| Neutron random walk in water (one neutron, collision tally) | slowing |
| Point-kinetics ODE against time | critical |
| Tap a bar on the drawing | products |
| Hero rendered in a worker; a three.js layer (`js/kit3d.js`) exists but no page loads it | intro, kit3d |
| Rings of impact parameter, disc of equal area | omp |

Controls are sliders and buttons in the text column; on the drawing only the hero takes clicks and products takes taps.
No page runs WebGL. No chapter has a shader-rendered field, phase-plane dynamics, charged-particle orbits, Poincaré
sections, or transport with branching histories in a layered geometry.

## New techniques (none used before on the site)

1. **WebGL fragment shaders** (new `WT.shader` in kit.js; the result is drawn into the chapter canvas, with a
   CPU fallback at low resolution when WebGL is missing): the Coulomb crater relief (29) and the Gamow heat field (30).
2. **Direct manipulation on the drawing**: pull-and-release slingshot (29), drag the temperature line through the field
   (30), drag a machine's operating point in the Lawson plane (30), click the cross-section to start a field line (31).
   Phones: tapping places the point and the picture still scrolls (`touch-action: pan-y`); every drag also has a slider.
3. **Live 0-D power-balance ODE in a phase plane**: release the plasma and it heats up or dies, with a comet trail.
4. **Charged-particle orbits with a Boris pusher**, drawn in 3D perspective that you can turn by dragging (31).
5. **Poincaré sections that build up**, from a symplectic field-line map (the tokamap): nested surfaces, islands, chaos (31).
6. **Layered Monte Carlo transport with branching histories** ((n,2n) daughters), many nuclides, a "long-exposure"
   tally layer (an off-screen canvas that keeps every breeding site, then slowly fades) and live counters (32). The
   slowing chapter walks one neutron in water; this one runs thousands per second through a slab and tallies by depth.
7. **Data fetched live from the library**: chapter 32 reads `data/n/<Z>/<A>.json` and interpolates INCOGNITA's
   (n,α), (n,p), (n,2n) at 14.1 MeV.

## Chapters

The text stays minimal: a step heading, one short line, the controls, and for 30–32 a formula line. Labels on the
drawings do the rest.

### 29 · Fusion energy and the Coulomb barrier (Intro)
0. **Fusion energy from the binding curve** — moved here from the Binding chapter (to keep the fusion
   material together). It draws the Binding chapter's curve (its frame, mode 2) with A + A → 2A. Binding keeps the curve
   and fission, plus a one-line pointer "→ Fusion"; the Neutrons chapter keeps its general proton barrier with a pointer
   to this chapter's barrier step (#fusion-2).
1. **Over the hill** — a WebGL relief of the d–t potential seen from above: a Coulomb hill that rises toward the triton
   and a nuclear crater at the top. Pull the deuteron back and let go: the pull sets its energy (1–400 keV), the aim
   sets its impact parameter. It follows the Coulomb (Rutherford) orbit, turns at r = 1.44 MeV·fm / E and sometimes
   tunnels in, with chance exp(−√(E_G/E)) inside one reduced wavelength. Counters: tries and fused.
   Slider: energy. Button: fire.
2. **What comes out** — reaction picker (D–T, D–D, D–³He, p–¹¹B). The products fly apart with momentum balanced, so
   the light one is fastest: D–T gives n 14.1 MeV + α 3.5 MeV. The barrier height (∝ Z₁Z₂) sits beside the energy out.
3. **Hot enough** — a box of deuterons and tritons with Maxwellian speeds at temperature T (slider, keV and million K).
   Fusions flash at a rate ∝ ⟨σv⟩(T) (Bosch–Hale fit); a meter shows the rate relative to 10 keV. The Sun's core is
   marked (1.3 keV; it burns p–p, far slower).

### 30 · The Gamow peak and ignition (Intermediate)
1. **The window** — a WebGL heat field over energy (x) and temperature (y): brightness = Maxwell tail × tunnelling
   chance. The ridge E₀ = (E_G (kT)²/4)^⅓ glows. Drag the T line; below, the slice: the falling tail, the rising
   tunnelling, their product (the Gamow peak) filled.
2. **Which fuel** — ⟨σv⟩(T) for D–T, D–D, D–³He as luminous ribbons on log axes (Bosch–Hale, 1–100 keV). Drag T.
   D–T peaks near 65 keV and is about 100× D–D at 10 keV.
3. **Ignition** — the Lawson plane: T against nτ_E, with the Q = 1, Q = 10 and ignition curves computed live from
   ⟨σv⟩ and bremsstrahlung. Drag the machine's operating point; Q is read out. Let go and a 0-D power balance runs:
   alpha heating against transport (τ_E falls with power, exponent −0.69 as in the IPB98 scaling) and
   bremsstrahlung. Below the curve the plasma cools and dies; above it heats itself and settles on the ignition curve.
   The triple-product minimum (≈ 3 × 10²¹ keV s m⁻³ near 14 keV) is marked.

### 31 · Magnetic confinement (Advanced)
1. **Charges circle** — deuterons and alphas spiral around field lines in 3D (Boris pusher). Slider B; drag to turn the
   view. Gyro-radius ρ = √(2mE)/(qB) is read out (10 keV deuteron at 5 T: 4 mm; 3.5 MeV alpha: 5 cm).
2. **Bend it into a ring** — a torus with one field line winding at safety factor q (slider). Each toroidal turn drops a
   dot on the cross-section (a Poincaré section): rational q closes after a few turns, irrational q fills a circle.
3. **Islands and chaos** — the tokamap (Balescu 1998), q from 1 at the axis to 4 at the edge. Slider K (perturbation):
   nested surfaces break into island chains at q = 2, 3/2, 3, then a chaotic edge. Click to start a field line there.
   The map is area-preserving, as field lines must be.

### 32 · Breeding blanket and first wall (Expert)
1. **Breed the fuel** — 14.1 MeV neutrons random-walk through a slab: steel first wall, Pb–17Li breeder, steel shield.
   Collisions sample elastic (exact kinematics, isotropic in the centre of mass), inelastic, (n,2n) on lead, capture,
   ⁶Li(n,t)α (1/v plus the 240 keV resonance) and ⁷Li(n,n′t)α (threshold 2.8 MeV). Every tritium site stays on a
   long-exposure layer. Sliders: ⁶Li enrichment, breeder depth. Counters: TBR, leaked, captured. Formula:
   TBR = (⁶Li(n,t) + ⁷Li(n,n′t)) / fusion neutrons.
2. **Lead multiplies** — switch PbLi ↔ pure liquid lithium; (n,2n) splits show as forks; the TBR and the n2n count
   respond. Cross sections are simple fits, so numbers are illustrative; the trends are real.
3. **What the wall takes** — a steel (or tungsten, vanadium, copper, silicon) lattice. Helium and hydrogen atoms appear at
   the rate set by **INCOGNITA's own (n,α), (n,p) and (n,2n) at 14.1 MeV**, read live from the v0.2 library files that
   the Every nuclide page uses. Sliders: wall load (MW/m²) and years. Readout in appm (14.1 MeV neutrons that have not
   collided yet, only). Link: "Every nuclide" for Fe-56 etc.

## Truth check of INCOGNITA claims (searched this repo)

- `library/v0.2` and `docs/walkthrough/data/n/`: (n,p), (n,2n), (n,α) and capture on a 1 keV–20 MeV grid for nuclides
  from oxygen (Z = 8) up. Fe-56 at 14.1 MeV: (n,p) 121 mb, (n,α) 45 mb, (n,2n) 461 mb; the curated EXFOR points beside
  it are ≈ 112, 44, 450 mb. **Claim made:** chapter 32 step 3 uses these predictions, labelled as INCOGNITA's library.
- No Li, Be or H isotopes in the library (lowest Z is 8). No charged-particle fusion cross sections, no plasma or
  transport code in physics/, validation/ or astro/. The engine's particle list includes d, t, ³He and α
  (`core/constants.py` PARSYM, as in TALYS), but fusion reactivities are not computed by it. `physics/charged/` is
  proton and alpha beams for medical radionuclide production (TALYS/TENDL residuals, stopping, thick-target yields),
  not fusion.
  **So chapters 29–31 and the breeding part of 32 are physics explanation**, with numbers from published fits
  (Bosch–Hale 1992 reactivities, standard constants) or labelled illustrative. No claim that INCOGNITA computes them.
- No "In the code" aside for 29–31. Chapter 32's aside names `library/v0.2/channels_v02.parquet` and the data page.

## Build checklist

- `js/ch/fusion.js`, `gamow.js`, `tokamak.js`, `blanket.js`; `WT.shader` in kit.js; `LEVEL` entries; part head and
  sections in index.html (only my hunks staged); script tags; bump `?v=`.
- Glossary entries (fusion, deuterium, tritium, plasma, Gamow peak, reactivity, Lawson criterion, triple product,
  ignition, tokamak, gyro-radius, safety factor, Poincaré section, magnetic island, breeding blanket, TBR, appm …);
  glossary_check.py `ORDER`.
- instructors.js rows; README (32 chapters, three parts); llms.txt and sitemap.xml
  (now tracked upstream) need no change: the page URL is the same.
- Translations: English only for now. Other languages fall back to English per string, as kit.js does for any missing
  key (`WT.L.ch[id]` absent → English chapter; canvas labels → English, logged in `WT.missing`).
- Tests: `node --check` and esbuild; headless Chrome `?shot=<ch>:<step>` desktop 1440×900 and phone 390×844 (CDP device
  emulation, DPR 3) and at 125 % scale; one Chrome at a time.
