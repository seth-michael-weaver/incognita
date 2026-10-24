/* Danish: optical (chapter 14, Expert) */
WT.L.ch.optical = {
  num: "Kapitel 14", title: "Den optiske model, løst", short: "Optisk model, løst",
  lead: "Kapitel 2 tegnede det optiske potential som en tåget glaskugle. Her er det, som motoren bruger det: en global parametrisering, en radial Schrödingerligning integreret skridt for skridt og en tilpasningsbetingelse, der gør bølgen til transmissionskoefficienter.",
  html: `
<div class="step">
  <h3>Koning–Delaroche-potentialet</h3>
  <p>For neutroner og protoner på kugleformede targetkerner er standarden potentialet af <b>Koning–Delaroche</b> (KD03): Woods–Saxon-former, hvis dybder ændrer sig jævnt med energien og med targetkernens masse og neutronoverskud, fra en global formel eller, for de kerner, KD03 tilpassede én for én, såsom jern-56, fra en lokal tilpasning af samme form. Billedet bruger den globale formel for neutroner på jern-56. Den reelle brønd (blå) binder; de imaginære dele (røde) absorberer, i volumenet og, ved lav energi mest, i en tynd skal ved overfladen.</p>
  <div class="ctl"><label for="op-e">Neutronenergi (MeV)</label><input id="op-e" type="range" data-bind="E" min="0.1" max="80" step="0.1" value="5"><output data-show="E" data-fmt="1"></output></div>
  <div class="formula">U(r) = −V<sub>V</sub> f(r) − iW<sub>V</sub> f(r) + 4i a<sub>D</sub>W<sub>D</sub> df<sub>D</sub>/dr + 2(V<sub>so</sub> + iW<sub>so</sub>) (1/r) df<sub>so</sub>/dr ⟨l·σ⟩</div>
  <p>Prøveneutronerne krydser ved den energi, du vælger, og falmer, hvor absorptionen bider: deres middelfri vejlængde er ħ<i>v</i>/2|<i>W</i>|. Hver dybde er en funktion af <i>E</i> − <i>E</i><sub>F</sub>, målt fra Fermienergien: den reelle dybde falder langsomt, overfladeabsorptionen <i>W</i><sub>D</sub> topper nær 10 MeV, og volumenabsorptionen <i>W</i><sub>V</sub> vokser jævnt, til den tager over, her over omkring 45 MeV.</p>
</div>
<div class="step">
  <h3>Integration af den radiale ligning</h3>
  <p>Hver partialbølge adlyder sin egen radiale ligning. Motoren integrerer den udad fra <i>r</i> = 0 med <b>Numerov-metoden</b>, en trepunktsregel, der er nøjagtig til sjette potens af skridtlængden, gennem hele det komplekse potential.</p>
  <div class="formula">u″<sub>lj</sub>(r) = [ l(l+1)/r² + (2μ/ħ²) U<sub>lj</sub>(r) − k² ] u<sub>lj</sub>(r)</div>
  <div class="ctl"><label for="op-l">Partialbølge l</label><input id="op-l" type="range" data-bind="L" min="0" max="10" step="1" value="1" data-instant><output data-show="L" data-fmt="0"></output></div>
  <div class="ctl"><label for="op-e2">Neutronenergi (MeV)</label><input id="op-e2" type="range" data-bind="E" min="0.1" max="80" step="0.1" value="5"><output data-show="E" data-fmt="1"></output></div>
  <p>Den fuldt optrukne linje er bølgen i tid, Re[<i>u</i> e<sup>−iωt</sup>]; den stiplede linje er den frie bølge, som om kernen ikke var der. Inde i brønden er bølgen kortere (neutronen er hurtigere) og mindre (absorberet); udenfor kommer den tilbage med en faseforskydning.</p>
</div>
<div class="step">
  <h3>Fra bølgen til S og T</h3>
  <p>Ud over omkring 12 fm er potentialet forsvundet, og bølgen må være en blanding af en indgående og en udgående fri bølge, <i>u</i> ∝ <i>H</i><sup>−</sup> − <i>S</i> <i>H</i><sup>+</sup>. Ved at tilpasse det integrerede <i>u</i> i to radier fastlægges elementet <i>S<sub>lj</sub></i> i <b>S-matricen</b>: den udgående amplitude med sin fase.</p>
  <div class="btns"><button class="btn ghost" data-act="abs" aria-pressed="false">Slå absorptionen fra</button></div>
  <div class="formula">S<sub>lj</sub> = η<sub>lj</sub> e<sup>2iδ<sub>lj</sub></sup> ,  T<sub>lj</sub> = 1 − |S<sub>lj</sub>|²</div>
  <p>Prikken er <i>S</i> i den komplekse plan, inden for enhedscirklen; dens spor er banen, mens energien gennemløber 0,1 til 40 MeV. Uden absorption er |<i>S</i>| = 1: prikken løber på cirklen, bølgen ændrer kun fase, og <i>T</i> = 0. Afstanden ind fra cirklen er det, compoundkernen og alle andre reaktioner får.</p>
</div>
<div class="step">
  <h3>Spin–bane-leddet splitter j</h3>
  <p><b>Spin–bane</b>-leddet er tiltrækkende for <i>j</i> = <i>l</i> + ½ og frastødende for <i>j</i> = <i>l</i> − ½. Det er lille, nogle få MeV ved overfladen, men det skubber de to transmissioner for hvert <i>l</i> fra hinanden, mest nær den partialbølge, der strejfer overfladen.</p>
  <div class="ctl"><label for="op-e3">Neutronenergi (MeV)</label><input id="op-e3" type="range" data-bind="E" min="0.1" max="80" step="0.1" value="5"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="so" aria-pressed="false">Slå spin–bane fra</button></div>
  <p>Hauser–Feshbach (kapitel 13) bruger de to hver for sig; summeret med deres vægte, (<i>l</i>+1)<i>T</i><sub>l,l+½</sub> + <i>l</i> <i>T</i><sub>l,l−½</sub>, giver de reaktionstværsnittet næsten uændret, og derfor begrænser totale tværsnit knap spin–bane-styrken, så der er brug for polarisationsdata.</p>
</div>
<div class="step">
  <h3>Tværsnittene</h3>
  <p>Summen over partialbølgerne giver de observable, som potentialet tilpasses til. Reaktionstværsnittet tæller den fjernede flux, det totale tværsnit følger af foroveramplituden, og forskellen mellem dem er formelastisk spredning.</p>
  <div class="formula">σ<sub>R</sub> = (π/k²) Σ<sub>l</sub> [(l+1)T<sub>l,l+½</sub> + l T<sub>l,l−½</sub>] ,  σ<sub>tot</sub> = (2π/k²) Σ<sub>lj</sub> (j+½)(1 − Re S<sub>lj</sub>)</div>
  <div class="ctl"><label for="op-e4">Neutronenergi (MeV)</label><input id="op-e4" type="range" data-bind="E" min="0.2" max="50" step="0.1" value="5"><output data-show="E" data-fmt="1"></output></div>
  <p>KD03 blev tilpasset til den slags data for mange kerner, fra 1 keV til 200 MeV; jerns totale tværsnit, mellem 3,5 og 4 b ved nogle få MeV og 2,5 b ved 14 MeV, kommer ud inden for omkring 5 procent uden justering til netop denne kerne, de brede maksima inklusive: de er kernens størrelse set mod neutronens bølgelængde.</p>
</div>
<div class="step">
  <h3>Lavenergienden</h3>
  <p>Under nogle få keV betyder kun s-bølgen noget, og <i>T</i><sub>0</sub> vokser som √<i>E</i>: en hældning på en halv i dette log–log-plot. Konstanten er <b>styrkefunktionen</b> <i>S</i><sub>0</sub> = <i>T</i><sub>0</sub>/(2π√<i>E</i>), med <i>E</i> i eV, den samme størrelse, som resonansanalyser måler som Σ Γ<sub>n</sub><sup>0</sup>/Δ<i>E</i>.</p>
  <p>Et globalt potential tilpasses mest ved MeV-energier, og lavenergienden er dets svageste punkt. For jern-56 giver dette <i>S</i><sub>0</sub> ≈ 5,5 × 10⁻⁴, og den lokale KD03-tilpasning næsten det samme, mens den målte værdi (RIPL) er 2,3 ± 0,6 × 10⁻⁴: jern ligger nær toppen af 3s-størrelsesresonansen omkring <i>A</i> ≈ 55, hvor <i>S</i><sub>0</sub> er mest følsom over for potentialet. Derfor er de målte <i>S</i><sub>0</sub> og <i>S</i><sub>1</sub> et separat, valgfrit input til motoren.</p>
  <div class="aside">I koden: <code>omp/parameters.py</code> (KD03 og de andre globale potentialer), <code>omp/potential.py</code> (de radiale formfaktorer), <code>omp/schrodinger.py</code> (Numerov-integration og tilpasning, med Coulombfunktioner efter Steeds metode for ladede partikler; den erstatter ECIS for kugleformede targetkerner og er kontrolleret mod ECIS' T<sub>lj</sub>), <code>ecis/</code> (porteringen af koblede kanaler for deformerede targetkerner), <code>omp/sfunc.py</code> (valgfrit: målte S₀, S₁). Billedet løser selv ligningen, ikke-relativistisk, for neutroner på jern-56.</div>
</div>`,
};
(function () {
  const L = {
    // axes and units
    "{#} fm": "{#} fm", "{#} MeV": "{#} MeV", "{#} keV": "{#} keV", "{#} eV": "{#} eV", "{#} b": "{#} b",
    // scene 1: potential
    "real well, depth {#} MeV": "reel brønd, dybde {#} MeV",
    "surface absorption, peak {#} MeV": "overfladeabsorption, top {#} MeV",
    "volume absorption {#} MeV": "volumenabsorption {#} MeV",
    "spin–orbit for l = {#}, j = {#}/{#}: {#} MeV": "spin–bane for l = {#}, j = {#}/{#}: {#} MeV",
    "E = {#} MeV": "E = {#} MeV",
    "mean free path: {#} fm at the surface, {#} fm in the centre": "middelfri vejlængde: {#} fm ved overfladen, {#} fm i centrum",
    "mean free path: {#} fm at the surface, > {#} fm in the centre": "middelfri vejlængde: {#} fm ved overfladen, > {#} fm i centrum",
    "mean free path: > {#} fm at the surface, {#} fm in the centre": "middelfri vejlængde: > {#} fm ved overfladen, {#} fm i centrum",
    "mean free path: > {#} fm at the surface, > {#} fm in the centre": "middelfri vejlængde: > {#} fm ved overfladen, > {#} fm i centrum",
    "real": "reel", "volume": "volumen", "surface": "overflade",
    "depths (MeV) against energy (MeV)": "dybder (MeV) mod energi (MeV)",
    // scene 2: wave
    "potential: real (blue), imaginary (red)": "potential: reelt (blåt), imaginært (rødt)",
    "nuclear surface": "kerneoverflade",
    "l = {#}, j = {#}+½ · E = {#} MeV · |S| = {#} · δ = {#}° · T = {#}": "l = {#}, j = {#}+½ · E = {#} MeV · |S| = {#} · δ = {#}° · T = {#}",
    "solid: the wave now · shaded: its size |u| · dashed: free wave": "fuldt optrukket: bølgen nu · skraveret: dens størrelse |u| · stiplet: fri bølge",
    // scene 3: S-matrix
    "Re S": "Re S", "Im S": "Im S",
    "|S| = {#}: nothing absorbed": "|S| = {#}: intet absorberet",
    "l = {#}, j = {#}+½ · E = {#} MeV": "l = {#}, j = {#}+½ · E = {#} MeV",
    "|S| = {#} · T = {#} − |S|² = {#}": "|S| = {#} · T = {#} − |S|² = {#}",
    "l = {#}, j = {#}+½": "l = {#}, j = {#}+½",
    "|S| = {#}": "|S| = {#}",
    "T = {#} − |S|² = {#}": "T = {#} − |S|² = {#}",
    "trail: S as E runs {#} → {#} MeV": "spor: S, mens E går {#} → {#} MeV",
    "no absorption: S stays on the circle": "ingen absorption: S bliver på cirklen",
    // scene 4: spin-orbit
    "T = {#}": "T = {#}", "l": "l",
    "hollow: j = l − ½ · solid: j = l + ½": "hul: j = l − ½ · fyldt: j = l + ½",
    "hollow (purple): j = l − ½ · solid (blue): j = l + ½": "hul (lilla): j = l − ½ · fyldt (blå): j = l + ½",
    "reaction cross section {#} b (without spin–orbit {#} b)": "reaktionstværsnit {#} b (uden spin–bane {#} b)",
    "reaction cross section {#} b (spin–orbit off)": "reaktionstværsnit {#} b (spin–bane slået fra)",
    "grazing l ≈ kR = {#}": "strejfende l ≈ kR = {#}",
    // scene 5: cross sections
    "total {#} b": "totalt {#} b",
    "reaction {#} b": "reaktion {#} b",
    "shape elastic {#} b": "formelastisk {#} b",
    "n + ⁵⁶Fe, KD{#}, computed here": "n + ⁵⁶Fe, KD{#}, beregnet her",
    // scene 6: S0
    "T₀ (s-wave)": "T₀ (s-bølge)",
    "T₁ (p-wave, j = {#}/{#}): slope {#}/{#}": "T₁ (p-bølge, j = {#}/{#}): hældning {#}/{#}",
    "dashed: {#}πS₀√E, slope ½": "stiplet: {#}πS₀√E, hældning ½",
    "S₀ = {#} × {#}⁻⁴ from this potential": "S₀ = {#} × {#}⁻⁴ fra dette potential",
  };
  Object.assign(WT.L.labels, L);
})();
Object.assign(WT.L.glossary, {
  koningDelaroche: {
    term: "Koning–Delaroche-potentialet", aliases: ["Koning–Delaroche", "Koning–Delaroche-potentialet", "KD03"],
    short: "Det globale optiske potential for neutroner og protoner af A. J. Koning og J.-P. Delaroche (2003), fra 1 keV til 200 MeV og massetal 24 til 209.",
    more: "Dets dybder, radier og diffusiteter er glatte funktioner af energi, masse og neutronoverskud, tilpasset én gang til en stor mængde målte tværsnit og vinkelfordelinger. Det er standarden for nukleoner i TALYS og i motoren.",
    chapter: "optical",
  },
  numerov: {
    term: "Numerov-metoden", aliases: ["Numerov-metoden", "Numerov-metode", "Numerov-integration", "Numerov"],
    short: "En trepunktsregel til at integrere andenordensligninger uden et førsteafledt led, som den radiale Schrödingerligning, med en fejl af orden h⁶ pr. skridt.",
    formula: "(1 − h²Q_n+1/12) u_n+1 = 2(1 + 5h²Q_n/12) u_n − (1 − h²Q_n−1/12) u_n−1",
    chapter: "optical",
  },
  sMatrix: {
    term: "S-matrix", aliases: ["S-matricen", "S-matrix", "S-matrixelement", "S-matrixelementet"],
    short: "Amplituderne, der forbinder indgående og udgående bølger; for elastisk spredning i én partialbølge et enkelt komplekst tal S = η e^(2iδ).",
    more: "|S| = 1 betyder, at intet absorberes, og kun fasen δ ændres; underskuddet 1 − |S|² er transmissionskoefficienten, den flux, der går til reaktioner.",
    chapter: "optical",
  },
  spinOrbit: {
    term: "Spin–bane-led", aliases: ["Spin–bane-leddet", "spin–bane-leddet", "Spin–bane", "spin–bane", "spin-bane", "spin–bane-styrken"],
    short: "Den del af kernepotentialet, der afhænger af, om nukleonens spin er parallelt eller antiparallelt med dens baneimpulsmoment.",
    more: "Det er tiltrækkende for j = l + ½ og frastødende for j = l − ½ og topper ved kerneoverfladen. Den samme vekselvirkning giver skalmodellens magiske tal.",
    chapter: "optical",
  },
});
