/* Danish: omp (Kapitel 5, den optiske model) */
WT.L.ch.omp = {
  num: "Kapitel 5", title: "En tåget krystalkugle", short: "Optisk model",
  lead: "Før alt andet stiller motoren et enklere spørgsmål: hvordan ser kernen ud for en indkommende neutron?",
  html: `
<div class="step">
  <p>I kvantemekanik er en neutron også en bølge. Billedet viser én, der ruller ind fra venstre med bølgetoppene som lyse bånd, mod en kerne (den stiplede cirkel). Endnu påvirker intet den, så bølgetoppene går lige igennem.</p>
  <div class="ctl"><label for="omp-e">Neutronenergi (MeV)</label><input id="omp-e" type="range" data-bind="E" min="0.2" max="40" step="0.1" value="8"><output data-show="E" data-fmt="1"></output></div>
  <p>Træk i energien og se bølgelængden nederst, i femtometer (fm, 10⁻¹⁵ m). Langsomme neutroner har lange bølger: under ca. 9 MeV er én bølgelængde bredere end hele denne kerne.</p>
</div>
<div class="step">
  <h3>Realdelen trækker</h3>
  <p>Det <b>optiske potential</b> er den gennemsnitlige kraft fra hele kernen på neutronen. Dets <em>realdel</em> er en brønd, ca. 50 MeV dyb: neutronen bliver hurtigere indeni, så bølgetoppene presses sammen. Motoren giver den en Woods–Saxon-form, flad og dyb i midten og jævnt aftagende til nul ved overfladen.</p>
</div>
<div class="step">
  <h3>Imaginærdelen absorberer</h3>
  <p>Skyggen bag kernen er de neutroner, der går tabt til reaktioner. Potentialets <em>imaginærdel</em> beskriver dem: den formindsker bølgen i stedet for at afbøje den, mest nær overfladen (den farvede ring).</p>
  <div class="ctl"><label for="omp-w">Absorption W (MeV)</label><input id="omp-w" type="range" data-bind="W" min="0" max="14" step="0.5" value="7"><output data-show="W" data-fmt="1"></output></div>
  <p>Træk <i>W</i> ned til 0, og skyggen fyldes ud: ingen absorption, ingen reaktioner. Deraf navnet optisk model: kernen er en tåget glaskugle, der dels afbøjer, dels absorberer.</p>
</div>
<div class="step">
  <h3>Sigtet betyder noget</h3>
  <p>Set forfra deler målet sig i ringe, én for hver <b>partialbølge</b> <i>l</i> = 0, 1, 2, … En neutron, der passerer i afstanden <i>b</i> fra centrum, har <b>impulsmoment</b> <i>l</i> ≈ <i>k b</i>, hvor <i>k</i> vokser med energien. Jo mørkere en ring er, desto større er dens <b>transmissionskoefficient</b> <i>T<sub>l</sub></i>: sandsynligheden for, at en neutron i den ring bliver absorberet.</p>
  <div class="ctl"><label for="omp-e3">Neutronenergi (MeV)</label><input id="omp-e3" type="range" data-bind="E" min="0.2" max="40" step="0.1" value="8"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="fire">Affyr 200 neutroner</button></div>
  <p>Orange glimt er absorberede neutroner; søjlerne tæller hver rings absorberede andel op mod modellens <i>T<sub>l</sub></i> (stregen). De inderste ringe absorberer næsten alt, de yderste lader neutronerne passere. Ved lav energi er ringene enorme, og kun <i>l</i> = 0 betyder noget.</p>
</div>
<div class="step">
  <h3>Forbi kernen i en bue</h3>
  <p>En neutron med stort impulsmoment passerer for langt ude til at røre kernen: det er <b>centrifugalbarrieren</b>. Set ovenfra hører hver neutron her til én partialbølge <i>l</i>, så den passerer i samme <b>passageafstand</b> <i>b</i> ≈ (<i>l</i>+½)/<i>k</i> (den stiplede cirkel).</p>
  <p>Men hver neutron er en bølge, udtværet over ca. én reduceret bølgelængde λ̄ (skæret). Selv når banen går udenom, kan den udtværede kant strejfe overfladen og komme ind: <b>tunnelering</b>.</p>
  <div class="ctl"><label for="omp-l">Partialbølge l</label><input id="omp-l" type="range" data-bind="L" min="0" max="8" step="1" value="3" data-instant><output data-show="L" data-fmt="0"></output></div>
  <div class="ctl"><label for="omp-e2">Energi (MeV)</label><input id="omp-e2" type="range" data-bind="E" min="0.2" max="40" step="0.1" value="8"><output data-show="E" data-fmt="1"></output></div>
  <p>Hæv <i>l</i>, og banen flytter udad: færre kommer ind. Hæv energien, og samme <i>l</i> passerer tættere på, med mindre udtværing. Motoren finder hvert <i>T<sub>l</sub></i> eksakt ved at løse Schrödingerligningen gennem hele potentialet; <i>S</i> måler, hvor meget af bølgen der kommer ud igen.</p>
  <div class="formula">T<sub>lj</sub> = 1 − |S<sub>lj</sub>|²</div>
</div>
<div class="step">
  <h3>Målet lægges sammen</h3>
  <p>Skiven til højre er, hvor stor kernen ser ud for neutronen: <b>reaktionstværsnittet</b>, i barn (10⁻²⁴ cm²). Hver ring bidrager med sit areal gange <i>T<sub>l</sub></i>. Den stiplede cirkel er den geometriske størrelse.</p>
  <div class="ctl"><label for="omp-e4">Neutronenergi (MeV)</label><input id="omp-e4" type="range" data-bind="E" min="0.2" max="40" step="0.1" value="8"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="sum">Læg sammen igen</button></div>
  <p>Skift energien, og summen kører igen: ved lav energi udgør én eller to store ringe næsten hele skiven; ved høj energi bidrager mange tynde ringe med små skiver, og skiven nærmer sig den geometriske størrelse.</p>
  <div class="formula">σ<sub>R</sub> = (π/k²) Σ (2l+1) T<sub>l</sub></div>
  <p>Hvert <i>T<sub>l</sub></i> føder resten af motoren: de afgør, hvor ofte hvert spin af den exciterede kerne dannes, og, kørt baglæns, hvor let hver partikel kommer ud igen.</p>
  <div class="aside">I koden: <code>omp/parameters.py</code> (Koning–Delaroches globale potential; dispersive potentialer for actinider), <code>omp/schrodinger.py</code> (Numerov-integration og Coulomb-tilpasning), <code>omp/inverse.py</code> (udgående partikler via detaljeret balance), <code>omp/regional.py</code> (valgfri, slået fra som standard: en regional justering af brønden for deformerede sjældne jordarters mål, tilpasset målte S₀ og S₁).</div>
</div>`,
};
Object.assign(WT.L.labels, {
  "absorbing surface": "absorberende overflade",
  "shadow: neutrons lost to reactions": "skygge: neutroner tabt til reaktioner",
  "wavelength {#} fm   ·   nucleus {#} fm across": "bølgelængde {#} fm   ·   kerne {#} fm bred",
  "crests crowd inside the well": "bølgetoppene presses sammen i brønden",
  "l={#}": "l={#}",
  "nuclear radius": "kerneradius",
  "reaction cross section ≈ {#} b": "reaktionstværsnit ≈ {#} b",
  "geometric size π(R+λ̄)² ≈ {#} b · darker ring = more absorbed · orange flash = absorbed": "geometrisk størrelse π(R+λ̄)² ≈ {#} b · mørkere = mere absorption · orange = absorberet",
  "absorbed, ring by ring": "absorberet, ring for ring",
  "bar: your neutrons · tick: model Tₗ": "søjle: dine neutroner · streg: model-Tₗ",
  "rings: shade = Tₗ": "ringe: farvetone = Tₗ",
  "geometric size π(R+λ̄)²": "geometrisk størrelse π(R+λ̄)²",
  "reaction cross section": "reaktionstværsnit",
  "ring l={#}: ({#}l+{#})·Tₗ·π/k² = +{#} b": "ring l={#}: ({#}l+{#})·Tₗ·π/k² = +{#} b",
  "all {#} rings added": "alle {#} ringe lagt sammen",
  "σ_R = {#} b": "σ_R = {#} b",
  "geometric {#} b": "geometrisk {#} b",
  "geometric {#} b · darker = more absorbed · orange = absorbed": "geometrisk {#} b · mørkere = mere absorption · orange = absorberet",
  "swing distance b ≈ (l+½)/k = {#} fm": "passageafstand b ≈ (l+½)/k = {#} fm",
  "nuclear radius R = {#} fm · wave fuzz λ̄ = {#} fm": "kerneradius R = {#} fm · udtværing λ̄ = {#} fm",
  "path crosses the nucleus: most get in": "banen krydser kernen: de fleste kommer ind",
  "path misses the nucleus: only the fuzzy edge can tunnel in": "banen går udenom: kun den udtværede kant kan tunnelere ind",
  "absorbed {#} of {#} · model Tₗ = {#}": "absorberet {#} af {#} · model-Tₗ = {#}",
});
