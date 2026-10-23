/* German (Deutsch): omp (Kapitel 2, das optische Modell) */
WT.L.ch.omp = {
  num: "Kapitel 2", title: "Eine trübe Kristallkugel", short: "Optisches Modell",
  lead: "Vor allem anderen stellt die Engine eine einfachere Frage: Wie sieht der Kern für ein ankommendes Neutron aus?",
  html: `
<div class="step">
  <p>In der Quantenmechanik ist ein Neutron auch eine Welle. Das Bild zeigt eine, die von links heranrollt, ihre Wellenberge als helle Streifen, auf einen Kern zu (der gestrichelte Kreis). Noch wirkt nichts auf sie, also laufen die Wellenberge einfach hindurch.</p>
  <div class="ctl"><label for="omp-e">Neutronenenergie (MeV)</label><input id="omp-e" type="range" data-bind="E" min="0.2" max="40" step="0.1" value="8"><output data-show="E" data-fmt="1"></output></div>
  <p>Ändere die Energie und beobachte unten die Wellenlänge, in Femtometern (fm, 10⁻¹⁵ m). Langsame Neutronen haben lange Wellen: Unterhalb von etwa 9 MeV ist eine Wellenlänge breiter als dieser ganze Kern.</p>
</div>
<div class="step">
  <h3>Der Realteil zieht an</h3>
  <p>Das <b>optische Potential</b> ist die gemittelte Kraft des ganzen Kerns auf das Neutron. Sein <em>Realteil</em> ist ein etwa 50 MeV tiefer Topf: Das Neutron wird darin schneller, also drängen sich die Wellenberge zusammen. Die Engine gibt ihm eine Woods–Saxon-Form, flach und tief in der Mitte, an der Oberfläche sanft auf null abfallend.</p>
</div>
<div class="step">
  <h3>Der Imaginärteil absorbiert</h3>
  <p>Der Schatten hinter dem Kern sind die Neutronen, die an Reaktionen verloren gehen. Der <em>Imaginärteil</em> des Potentials bildet sie ab: Er schwächt die Welle, statt sie abzulenken, vor allem nahe der Oberfläche (der farbige Ring).</p>
  <div class="ctl"><label for="omp-w">Absorption W (MeV)</label><input id="omp-w" type="range" data-bind="W" min="0" max="14" step="0.5" value="7"><output data-show="W" data-fmt="1"></output></div>
  <p>Zieh <i>W</i> auf 0, und der Schatten füllt sich: keine Absorption, keine Reaktionen. Daher der Name optisches Modell: Der Kern ist eine trübe Glaskugel, die teils ablenkt und teils absorbiert.</p>
</div>
<div class="step">
  <h3>Es kommt aufs Zielen an</h3>
  <p>Von vorn gesehen zerfällt das Target in Ringe, einen pro <b>Partialwelle</b> <i>l</i> = 0, 1, 2, … Ein Neutron, das im Abstand <i>b</i> vom Zentrum vorbeifliegt, trägt den <b>Drehimpuls</b> <i>l</i> ≈ <i>k b</i>, wobei <i>k</i> mit der Energie wächst. Je dunkler ein Ring, desto größer sein <b>Transmissionskoeffizient</b> <i>T<sub>l</sub></i>: die Wahrscheinlichkeit, dass ein Neutron in diesem Ring absorbiert wird.</p>
  <div class="ctl"><label for="omp-e3">Neutronenenergie (MeV)</label><input id="omp-e3" type="range" data-bind="E" min="0.2" max="40" step="0.1" value="8"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="fire">200 Neutronen abfeuern</button></div>
  <p>Orange Blitze sind absorbierte Neutronen; die Balken vergleichen den absorbierten Anteil jedes Rings mit dem <i>T<sub>l</sub></i> des Modells (der Strich). Innere Ringe absorbieren fast alles, äußere lassen Neutronen durch. Bei niedriger Energie sind die Ringe riesig, und nur <i>l</i> = 0 zählt.</p>
</div>
<div class="step">
  <h3>Am Kern vorbeischwingen</h3>
  <p>Ein Neutron mit viel Drehimpuls fliegt zu weit außen vorbei, um den Kern zu berühren: Das ist die <b>Zentrifugalbarriere</b>. Von oben gesehen gehört hier jedes Neutron zu einer Partialwelle <i>l</i>, also fliegt es im selben <b>Vorbeiflugabstand</b> <i>b</i> ≈ (<i>l</i>+½)/<i>k</i> vorbei (der gestrichelte Kreis).</p>
  <p>Aber jedes Neutron ist eine Welle, verschwommen über etwa eine reduzierte Wellenlänge λ̄ (der Schein). Selbst wenn seine Bahn danebengeht, kann der verschwommene Rand die Oberfläche streifen und hineingelangen: der <b>Tunneleffekt</b>.</p>
  <div class="ctl"><label for="omp-l">Partialwelle l</label><input id="omp-l" type="range" data-bind="L" min="0" max="8" step="1" value="3" data-instant><output data-show="L" data-fmt="0"></output></div>
  <div class="ctl"><label for="omp-e2">Energie (MeV)</label><input id="omp-e2" type="range" data-bind="E" min="0.2" max="40" step="0.1" value="8"><output data-show="E" data-fmt="1"></output></div>
  <p>Erhöhe <i>l</i>, und die Bahn wandert nach außen: Weniger kommen hinein. Erhöhe die Energie, und dasselbe <i>l</i> fliegt näher vorbei, mit weniger Unschärfe. Die Engine bestimmt jedes <i>T<sub>l</sub></i> exakt, indem sie die Schrödinger-Gleichung durch das volle Potential löst; <i>S</i> misst, wie viel Welle wieder herauskommt.</p>
  <div class="formula">T<sub>lj</sub> = 1 − |S<sub>lj</sub>|²</div>
</div>
<div class="step">
  <h3>Das Target aufsummieren</h3>
  <p>Die Scheibe rechts zeigt, wie groß der Kern für das Neutron aussieht: der <b>Reaktionsquerschnitt</b>, in Barn (10⁻²⁴ cm²). Jeder Ring trägt seine Fläche mal <i>T<sub>l</sub></i> dazu bei. Der gestrichelte Kreis ist die geometrische Größe.</p>
  <div class="ctl"><label for="omp-e4">Neutronenenergie (MeV)</label><input id="omp-e4" type="range" data-bind="E" min="0.2" max="40" step="0.1" value="8"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="sum">Noch einmal aufsummieren</button></div>
  <p>Ändere die Energie, und die Summe läuft erneut: Bei niedriger Energie machen ein oder zwei große Ringe fast die ganze Scheibe aus; bei hoher Energie tragen viele dünne Ringe schmale Streifen bei, und die Scheibe nähert sich der geometrischen Größe.</p>
  <div class="formula">σ<sub>R</sub> = (π/k²) Σ (2l+1) T<sub>l</sub></div>
  <p>Die <i>T<sub>l</sub></i> speisen den Rest der Engine: Sie entscheiden, wie oft sich jeder Spin des angeregten Kerns bildet, und, rückwärts angewandt, wie leicht jedes Teilchen wieder herauskommt.</p>
  <div class="aside">Im Code: <code>omp/parameters.py</code> (globales Potential nach Koning–Delaroche; dispersive Potentiale für Aktiniden), <code>omp/schrodinger.py</code> (Numerov-Integration und Coulomb-Anschluss), <code>omp/inverse.py</code> (auslaufende Teilchen über detailliertes Gleichgewicht), <code>omp/regional.py</code> (optional, standardmäßig aus: eine regionale Anpassung des Topfs für deformierte Targets der Seltenen Erden, angepasst an gemessene S₀ und S₁).</div>
</div>`,
};
Object.assign(WT.L.labels, {
  "absorbing surface": "absorbierende Oberfläche",
  "shadow: neutrons lost to reactions": "Schatten: an Reaktionen verlorene Neutronen",
  "wavelength {#} fm   ·   nucleus {#} fm across": "Wellenlänge {#} fm   ·   Kern {#} fm breit",
  "crests crowd inside the well": "Wellenberge drängen sich im Topf",
  "l={#}": "l={#}",
  "nuclear radius": "Kernradius",
  "reaction cross section ≈ {#} b": "Reaktionsquerschnitt ≈ {#} b",
  "geometric size π(R+λ̄)² ≈ {#} b · darker ring = more absorbed · orange flash = absorbed": "geom. Größe π(R+λ̄)² ≈ {#} b · dunkler = mehr absorbiert · orange = absorbiert",
  "absorbed, ring by ring": "absorbiert, Ring für Ring",
  "bar: your neutrons · tick: model Tₗ": "Balken: deine Neutronen · Strich: Modell-Tₗ",
  "rings: shade = Tₗ": "Ringe: Tönung = Tₗ",
  "geometric size π(R+λ̄)²": "geometrische Größe π(R+λ̄)²",
  "reaction cross section": "Reaktionsquerschnitt",
  "ring l={#}: ({#}l+{#})·Tₗ·π/k² = +{#} b": "Ring l={#}: ({#}l+{#})·Tₗ·π/k² = +{#} b",
  "all {#} rings added": "alle {#} Ringe addiert",
  "σ_R = {#} b": "σ_R = {#} b",
  "geometric {#} b": "geometrisch {#} b",
  "geometric {#} b · darker = more absorbed · orange = absorbed": "geometrisch {#} b · dunkler = mehr absorbiert · orange = absorbiert",
  "swing distance b ≈ (l+½)/k = {#} fm": "Vorbeiflugabstand b ≈ (l+½)/k = {#} fm",
  "nuclear radius R = {#} fm · wave fuzz λ̄ = {#} fm": "Kernradius R = {#} fm · Wellenunschärfe λ̄ = {#} fm",
  "path crosses the nucleus: most get in": "Bahn kreuzt den Kern: die meisten kommen hinein",
  "path misses the nucleus: only the fuzzy edge can tunnel in": "Bahn verfehlt den Kern: nur der unscharfe Rand kann hineintunneln",
  "absorbed {#} of {#} · model Tₗ = {#}": "absorbiert {#} von {#} · Modell-Tₗ = {#}",
});
