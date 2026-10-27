/* Dutch (Nederlands): omp (Hoofdstuk 5, het optisch model) */
WT.L.ch.omp = {
  num: "Hoofdstuk 5", title: "Een troebele glazen bol", short: "Optisch model",
  lead: "Voor alles stelt de motor een eenvoudigere vraag: hoe ziet de kern eruit voor een binnenkomend neutron?",
  html: `
<div class="step">
  <p>In de quantummechanica is een neutron ook een golf. De afbeelding toont er een die van links binnenrolt, met de golftoppen als heldere banden, op weg naar een kern (de gestippelde cirkel). Er werkt nog niets op, dus de toppen gaan er recht doorheen.</p>
  <div class="ctl"><label for="omp-e">Neutronenergie (MeV)</label><input id="omp-e" type="range" data-bind="E" min="0.2" max="40" step="0.1" value="8"><output data-show="E" data-fmt="1"></output></div>
  <p>Sleep de energie en kijk onderaan naar de golflengte, in femtometer (fm, 10⁻¹⁵ m). Langzame neutronen hebben lange golven: onder ongeveer 9 MeV is één golflengte breder dan deze hele kern.</p>
</div>
<div class="step">
  <h3>Het reële deel trekt aan</h3>
  <p>De <b>optische potentiaal</b> is de gemiddelde kracht van de hele kern op het neutron. Het <em>reële deel</em> is een put van ongeveer 50 MeV diep: binnenin versnelt het neutron, dus de golftoppen dringen samen. De motor geeft hem een Woods–Saxon-vorm, vlak en diep in het midden, die aan het oppervlak geleidelijk naar nul wegzakt.</p>
</div>
<div class="step">
  <h3>Het imaginaire deel absorbeert</h3>
  <p>De schaduw achter de kern zijn de neutronen die aan reacties verloren gaan. Het <em>imaginaire deel</em> van de potentiaal beschrijft ze: het laat de golf krimpen in plaats van hem af te buigen, vooral dicht bij het oppervlak (de gekleurde ring).</p>
  <div class="ctl"><label for="omp-w">Absorptie W (MeV)</label><input id="omp-w" type="range" data-bind="W" min="0" max="14" step="0.5" value="7"><output data-show="W" data-fmt="1"></output></div>
  <p>Sleep <i>W</i> naar 0 en de schaduw vult zich: geen absorptie, geen reacties. Vandaar de naam optisch model: de kern is een troebele glazen bol die deels afbuigt en deels absorbeert.</p>
</div>
<div class="step">
  <h3>Richten doet ertoe</h3>
  <p>Recht van voren gezien valt het doel uiteen in ringen, één per <b>partiële golf</b> <i>l</i> = 0, 1, 2, … Een neutron dat op afstand <i>b</i> van het middelpunt passeert, draagt een <b>impulsmoment</b> <i>l</i> ≈ <i>k b</i>, waarbij <i>k</i> groeit met de energie. Hoe donkerder een ring, hoe groter zijn <b>transmissiecoëfficiënt</b> <i>T<sub>l</sub></i>: de kans dat een neutron in die ring wordt geabsorbeerd.</p>
  <div class="ctl"><label for="omp-e3">Neutronenergie (MeV)</label><input id="omp-e3" type="range" data-bind="E" min="0.2" max="40" step="0.1" value="8"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="fire">Schiet 200 neutronen af</button></div>
  <p>Oranje flitsen zijn geabsorbeerde neutronen; de staafjes zetten het geabsorbeerde deel van elke ring af tegen de <i>T<sub>l</sub></i> van het model (het streepje). Binnenste ringen absorberen bijna alles, buitenste ringen laten neutronen door. Bij lage energie zijn de ringen enorm en telt alleen <i>l</i> = 0.</p>
</div>
<div class="step">
  <h3>Langs de kern zwaaien</h3>
  <p>Een neutron met veel impulsmoment passeert te ver weg om de kern te raken: dat is de <b>centrifugale barrière</b>. Van bovenaf gezien hoort elk neutron hier bij één partiële golf <i>l</i>, dus het passeert op dezelfde <b>passeerafstand</b> <i>b</i> ≈ (<i>l</i>+½)/<i>k</i> (de gestippelde cirkel).</p>
  <p>Maar elk neutron is een golf, uitgesmeerd over ongeveer één gereduceerde golflengte λ̄ (de gloed). Zelfs als zijn baan mist, kan de vage rand het oppervlak raken en naar binnen komen: <b>tunnelen</b>.</p>
  <div class="ctl"><label for="omp-l">Partiële golf l</label><input id="omp-l" type="range" data-bind="L" min="0" max="8" step="1" value="3" data-instant><output data-show="L" data-fmt="0"></output></div>
  <div class="ctl"><label for="omp-e2">Energie (MeV)</label><input id="omp-e2" type="range" data-bind="E" min="0.2" max="40" step="0.1" value="8"><output data-show="E" data-fmt="1"></output></div>
  <p>Verhoog <i>l</i> en de baan schuift naar buiten: er komen er minder binnen. Verhoog de energie en dezelfde <i>l</i> passeert dichterbij, met minder uitsmering. De motor vindt elke <i>T<sub>l</sub></i> exact door de schrödingervergelijking door de volledige potentiaal op te lossen; <i>S</i> meet hoeveel golf er weer uitkomt.</p>
  <div class="formula">T<sub>lj</sub> = 1 − |S<sub>lj</sub>|²</div>
</div>
<div class="step">
  <h3>Het doel bij elkaar optellen</h3>
  <p>De schijf rechts is hoe groot de kern lijkt voor het neutron: de <b>werkzame doorsnede voor reactie</b>, in barn (10⁻²⁴ cm²). Elke ring voegt er zijn oppervlak maal <i>T<sub>l</sub></i> aan toe. De gestippelde cirkel is de geometrische grootte.</p>
  <div class="ctl"><label for="omp-e4">Neutronenergie (MeV)</label><input id="omp-e4" type="range" data-bind="E" min="0.2" max="40" step="0.1" value="8"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="sum">Opnieuw optellen</button></div>
  <p>Verander de energie en de som loopt opnieuw: bij lage energie vormen een of twee grote ringen bijna de hele schijf; bij hoge energie voegen veel dunne ringen reepjes toe en nadert de schijf de geometrische grootte.</p>
  <div class="formula">σ<sub>R</sub> = (π/k²) Σ (2l+1) T<sub>l</sub></div>
  <p>De <i>T<sub>l</sub></i> voeden de rest van de motor: ze bepalen hoe vaak elke spin van de aangeslagen kern ontstaat en, omgekeerd gebruikt, hoe makkelijk elk deeltje weer naar buiten komt.</p>
  <div class="aside">In de code: <code>omp/parameters.py</code> (globale potentiaal van Koning–Delaroche; dispersieve potentialen voor actiniden), <code>omp/schrodinger.py</code> (Numerov-integratie en coulombaansluiting), <code>omp/inverse.py</code> (uitgaande deeltjes via gedetailleerd evenwicht), <code>omp/regional.py</code> (optioneel, standaard uit: een regionale aanpassing van de put voor vervormde trefkernen uit de zeldzame aarden, gefit aan gemeten S₀ en S₁).</div>
</div>`,
};
Object.assign(WT.L.labels, {
  "absorbing surface": "absorberend oppervlak",
  "shadow: neutrons lost to reactions": "schaduw: neutronen verloren aan reacties",
  "wavelength {#} fm   ·   nucleus {#} fm across": "golflengte {#} fm   ·   kern {#} fm breed",
  "crests crowd inside the well": "golftoppen dringen samen in de put",
  "l={#}": "l={#}",
  "nuclear radius": "kernstraal",
  "reaction cross section ≈ {#} b": "werkzame doorsnede voor reactie ≈ {#} b",
  "geometric size π(R+λ̄)² ≈ {#} b · darker ring = more absorbed · orange flash = absorbed": "geom. grootte π(R+λ̄)² ≈ {#} b · donkerder = meer absorptie · oranje = geabsorbeerd",
  "absorbed, ring by ring": "geabsorbeerd, ring voor ring",
  "bar: your neutrons · tick: model Tₗ": "staaf: jouw neutronen · streepje: Tₗ",
  "rings: shade = Tₗ": "ringen: tint = Tₗ",
  "geometric size π(R+λ̄)²": "geometrische grootte π(R+λ̄)²",
  "reaction cross section": "werkzame doorsnede voor reactie",
  "ring l={#}: ({#}l+{#})·Tₗ·π/k² = +{#} b": "ring l={#}: ({#}l+{#})·Tₗ·π/k² = +{#} b",
  "all {#} rings added": "alle {#} ringen opgeteld",
  "σ_R = {#} b": "σ_R = {#} b",
  "geometric {#} b": "geometrisch {#} b",
  "geometric {#} b · darker = more absorbed · orange = absorbed": "geometrisch {#} b · donkerder = meer absorptie · oranje = geabsorbeerd",
  "swing distance b ≈ (l+½)/k = {#} fm": "passeerafstand b ≈ (l+½)/k = {#} fm",
  "nuclear radius R = {#} fm · wave fuzz λ̄ = {#} fm": "kernstraal R = {#} fm · uitsmering λ̄ = {#} fm",
  "path crosses the nucleus: most get in": "baan kruist de kern: de meeste komen binnen",
  "path misses the nucleus: only the fuzzy edge can tunnel in": "baan mist de kern: alleen de vage rand tunnelt naar binnen",
  "absorbed {#} of {#} · model Tₗ = {#}": "geabsorbeerd {#} van {#} · model-Tₗ = {#}",
});
