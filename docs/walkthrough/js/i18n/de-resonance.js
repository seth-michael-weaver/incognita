/* German (Deutsch): resonance (Kapitel 10, Resonanzen) */
WT.L.ch.resonance = {
  num: "Kapitel 10", title: "Scharfe Peaks", short: "Resonanzen",
  lead: "Bei genügend niedriger Energie sieht ein Neutron keinen glatten, gemittelten Kern mehr. Es sieht die einzelnen Energieniveaus des Compoundkerns, eines nach dem anderen.",
  html: `
<div class="step">
  <p>Jeder Peak ist eine <b>Resonanz</b>: ein Energieniveau des Compoundkerns, in das ein Neutron mit genau dieser Energie fallen kann. Seine Höhe ist dort der Wirkungsquerschnitt für den <b>Einfang</b> (Neutron absorbiert, Photonen heraus), auf logarithmischer Skala; seine Breite ist die Resonanzbreite Γ, etwa hundertmal breiter gezeichnet, als sie ist.</p>
  <div class="ctl"><label for="res-e">Neutronenenergie (eV)</label><input id="res-e" type="range" data-bind="En" min="0.5" max="300" step="0.1" value="30"><output data-show="En" data-fmt="1"></output></div>
  <p>Das Neutron hüpft in der Energie voran; wo es landet, kann es eingefangen werden, in einem Blitz aus Photonen. Auf einem Peak beträgt der Wirkungsquerschnitt Tausende Barn, und der Einfang ist fast sicher; zwischen den Peaks sind es einige Barn. Stell die Energie auf einen Peak und dann zwischen zwei.</p>
</div>
<div class="step">
  <h3>Peaks halten Abstand</h3>
  <p>Die mittlere Reihe zeigt, wie echte Niveaus liegen: Zwei Niveaus mit gleichem Spin und gleicher Parität stoßen sich ab, also sind Beinahe-Zusammenfälle selten. Die <b>Theorie der Zufallsmatrizen</b> beschreibt dieses Muster. Wirklich zufällige Positionen (obere Reihe) klumpen und lassen Lücken.</p>
  <div class="btns"><button class="btn" data-act="again">Neu ziehen</button></div>
  <p>Zieh neu für eine neue Stichprobe. ⟨r̃⟩ vergleicht jeden Abstand mit dem nächsten: etwa 0,39 für zufällige, 0,53 für sich abstoßende Niveaus; der Code verwendet das abstoßende Muster. Mischt man zwei Folgen, etwa zwei Spins (untere Reihe), verdeckt das die Abstoßung teilweise.</p>
</div>
<div class="step">
  <h3>Höhen streuen wild</h3>
  <p>Jetzt ist die Höhe jedes Peaks seine <b>Neutronenbreite</b> Γ<sub>n</sub>, auf linearer Skala: wie stark das Niveau an ein Neutron koppelt. Die gelbe Kappe ist seine γ-Breite Γ<sub>γ</sub>, wie schnell es Photonen aussendet; sie summiert Hunderte von Photonenwegen und ist daher für jedes Niveau fast gleich.</p>
  <div class="btns"><button class="btn" data-act="roll">Breite würfeln</button><button class="btn ghost" data-act="equal">Gleiche Breiten</button><button class="btn ghost" data-act="pt">Porter–Thomas</button></div>
  <p>Ein Niveau hat nur eine Möglichkeit, in Neutron plus Target zu zerfallen, also verhält sich seine Breite wie das Quadrat einer einzigen normalverteilten Zahl. Würfle eine: Die Kugel landet bei <i>x</i>, <i>x</i>² wird zur Höhe des nächsten Peaks, und ein Punkt fällt in den Stapel. Der Stapel drängt sich nahe null mit einem langen Ausläufer, das <b>Porter–Thomas</b>-Gesetz: Die meisten Niveaus sind schwach, einige wenige riesig. Gleiche Breiten zeigt stattdessen eine Reihe durchschnittlicher Peaks.</p>
</div>
<div class="step">
  <h3>Eine Leiter aus vier Zahlen</h3>
  <p>Die Peaks entstehen jetzt aus vier Mittelwerten, die du einstellen kannst. Für einen nicht gemessenen Kern lassen sich nur diese Mittelwerte vorhersagen: der mittlere Abstand <i>D</i><sub>0</sub>; die <b>Stärkefunktionen</b> <i>S</i><sub>0</sub> und <i>S</i><sub>1</sub>, die mittlere Neutronenbreite pro Abstandseinheit für s-Wellen-Neutronen (zentral) und p-Wellen-Neutronen (außermittig); und die mittlere γ-Breite. Daraus baut der Code eine <b>Leiter</b>: einen zufälligen Satz von Niveaus mit diesen Mittelwerten.</p>
  <div class="ctl"><label for="res-d0">Abstand D₀ (eV)</label><input id="res-d0" type="range" data-bind="D0" min="3" max="60" step="0.5" value="20"><output data-show="D0" data-fmt="1"></output></div>
  <div class="ctl"><label for="res-s0">Stärke S₀ (×10⁻⁴)</label><input id="res-s0" type="range" data-bind="S0" min="0.2" max="3" step="0.05" value="1"><output data-show="S0" data-fmt="2"></output></div>
  <div class="ctl"><label for="res-gg">γ-Breite ⟨Γγ⟩ (meV)</label><input id="res-gg" type="range" data-bind="Gg" min="10" max="80" step="1" value="23"><output data-show="Gg" data-fmt="0"></output></div>
  <p>Zieh an <i>D</i><sub>0</sub>, und die Peaks rücken auseinander oder drängen sich zusammen. Volle Peaks sind s-Wellen-Niveaus (positive Parität), umrandete Peaks p-Wellen-Niveaus (negative Parität). Neutronenbreiten wachsen wie √<i>E</i> für s-Wellen und wie <i>E</i><sup>3/2</sup> für p-Wellen, also beginnen die umrandeten Peaks klein und wachsen nach rechts.</p>
</div>
<div class="step">
  <h3>Hinunter bis thermisch</h3>
  <p>Dieselben Peaks auf logarithmischer Energieskala, bis hinunter zu Tausendsteln eines eV. Reaktorneutronen werden langsamer, indem sie an leichten Kernen abprallen und dabei jedes Mal etwa denselben Bruchteil ihrer Energie verlieren, also ist hier jeder Sprung gleich lang. Manche werden unterwegs von den Peaks eingefangen.</p>
  <div class="btns"><button class="btn" data-act="slow">10 Neutronen abbremsen</button></div>
  <p>Die durchkommen, kommen bei Raumtemperatur zur Ruhe, 0,025 eV, der <b>thermischen</b> Energie, weit unterhalb des ersten Peaks. Dort ist der Wirkungsquerschnitt, die Fläche der Scheibe, die Summe der Ausläufer der Resonanzen, einschließlich gebundener Niveaus knapp unter null; die Ausläufer wachsen wie 1/<i>v</i> (<i>v</i> die Geschwindigkeit des Neutrons), also steigt der Untergrund nach links an. Der Fang auf dem Weg nach unten wird durch das <b>Resonanzintegral</b> gemessen: den Wirkungsquerschnitt oberhalb von 0,5 eV, jede Energie mit 1/<i>E</i> gewichtet.</p>
</div>
<div class="step">
  <h3>Vorhersagbar ist nur die Statistik</h3>
  <p>Jede Reihe ist eine Leiter, gezogen aus denselben vier Zahlen, mit einer Scheibe, deren Fläche ihr thermischer Einfangquerschnitt ist. Die Klammer reicht bis zu dem Peak, der diesen Wert bestimmt, meist dem nächstgelegenen; sein Abstand ändert sich von Leiter zu Leiter, und die Scheibe schwankt um einen Faktor zehn oder mehr.</p>
  <div class="btns"><button class="btn" data-act="draw1">Eine Leiter ziehen</button><button class="btn ghost" data-act="more">20 ziehen</button></div>
  <p>Jeder Wert fällt in den Stapel rechts. Für einen nicht gemessenen Kern ist die Antwort eine Streuung von Werten, nicht eine Zahl, und kein besseres Modell kann sie verengen. Das Resonanzintegral, eine Summe über viele Peaks, streut weniger. Wo die Niveaus mehr als etwa 10 keV auseinanderliegen, wie bei leichten Kernen, liegt keines nahe thermisch: Der Einfang ist dort direkt, und der Code verweigert die Antwort.</p>
  <div class="aside">Im Code: <code>physics/resonance/ladder.py</code> (Abstände nach Zufallsmatrizen, Porter–Thomas-Breiten, Breit–Wigner-Wirkungsquerschnitte, thermischer Einfang und Resonanzintegral über ein Ensemble), <code>ladder_statistics.py</code> (dieselben Gesetze an gemessenen Leitern getestet), <code>ensemble_runner.py</code>. Diese laufen neben der Reaktions-Engine, nicht in ihr.</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // forest
  "{#} eV": "{#} eV", "+{#} eV": "+{#} eV",
  "height: peak capture (log) · width Γ ×{#}": "Höhe: Einfang am Peak (log) · Breite Γ ×{#}",
  "peak height: capture cross section (log scale) · width: resonance width Γ, drawn {#}× wide": "Höhe: Einfangquerschnitt (log. Skala) · Breite: Resonanzbreite Γ, {#}× breiter gezeichnet",
  "D₀ {#} eV · S₀ {#}×{#}⁻⁴ · S₁ {#}×{#}⁻⁴ · ⟨Γγ⟩ {#} meV": "D₀ {#} eV · S₀ {#}×{#}⁻⁴ · S₁ {#}×{#}⁻⁴ · ⟨Γγ⟩ {#} meV",
  "s-wave (+ parity)": "s-Welle (Parität +)", "p-wave (− parity)": "p-Welle (Parität −)",
  "caught {#} times in {#} landings": "{#}-mal eingefangen bei {#} Landungen",
  "each peak: one level of the compound nucleus": "jeder Peak: ein Niveau des Compoundkerns",
  "each peak: one level of the compound nucleus · about {#} eV apart": "jeder Peak: ein Niveau des Compoundkerns · etwa {#} eV Abstand",
  // spacing
  "random positions (Poisson)": "zufällige Positionen (Poisson)",
  "repelling levels (random-matrix)": "sich abstoßende Niveaus (Zufallsmatrix)",
  "two repelling sequences mixed": "zwei abstoßende Folgen gemischt",
  "clumps and gaps · ⟨r̃⟩ ≈ {#}": "Klumpen und Lücken · ⟨r̃⟩ ≈ {#}",
  "evenly kept apart · ⟨r̃⟩ ≈ {#}": "gleichmäßig getrennt · ⟨r̃⟩ ≈ {#}",
  "repulsion half hidden · ⟨r̃⟩ ≈ {#}": "Abstoßung halb verdeckt · ⟨r̃⟩ ≈ {#}",
  "clumps and gaps · spacing ratio ⟨r̃⟩ ≈ {#}": "Klumpen und Lücken · Abstandsverhältnis ⟨r̃⟩ ≈ {#}",
  "evenly kept apart · spacing ratio ⟨r̃⟩ ≈ {#}": "gleichmäßig getrennt · Abstandsverhältnis ⟨r̃⟩ ≈ {#}",
  "repulsion half hidden · spacing ratio ⟨r̃⟩ ≈ {#}": "Abstoßung halb verdeckt · Abstandsverhältnis ⟨r̃⟩ ≈ {#}",
  "⟨r̃⟩: {#} if random, {#} for random-matrix": "⟨r̃⟩: {#} bei Zufall, {#} bei Zufallsmatrix",
  "same average spacing in every row · ⟨r̃⟩: {#} if random, {#} for random-matrix": "gleicher mittlerer Abstand in jeder Reihe · ⟨r̃⟩: {#} bei Zufall, {#} bei Zufallsmatrix",
  // Porter-Thomas
  "height: neutron width Γn (linear)": "Höhe: Neutronenbreite Γn (linear)",
  "peak height: neutron width Γn, linear scale": "Peakhöhe: Neutronenbreite Γn, lineare Skala",
  "yellow: γ width": "gelb: γ-Breite",
  "yellow cap: γ width, nearly the same on every peak": "gelbe Kappe: γ-Breite, auf jedem Peak fast gleich",
  "equal widths: every peak the average": "gleiche Breiten: jeder Peak im Mittel",
  "rolled widths": "gewürfelte Breiten", "pile of rolled widths": "Stapel gewürfelter Breiten",
  "× average": "× Mittelwert", "(in units of the average)": "(in Einheiten des Mittelwerts)",
  "dashed: Porter–Thomas": "gestrichelt: Porter–Thomas", "dashed: the Porter–Thomas law": "gestrichelt: das Porter–Thomas-Gesetz",
  "bell-curve number x": "Normalverteilte Zahl x",
  "x = {#}  →  x² = {#}": "x = {#}  →  x² = {#}",
  "press Roll a width": "drück „Breite würfeln“",
  // thermal
  "bound level {#} eV": "gebundenes Niveau {#} eV",
  "a bound level at {#} eV: its tail lifts this end": "ein gebundenes Niveau bei {#} eV: sein Ausläufer hebt dieses Ende",
  "resonance integral ≈ {#} b": "Resonanzintegral ≈ {#} b",
  "resonance integral above {#} eV ≈ {#} b": "Resonanzintegral über {#} eV ≈ {#} b",
  "{#}/v": "{#}/v",
  "caught by a peak on the way down: {#} · reached thermal: {#}": "unterwegs von einem Peak gefangen: {#} · thermisch angekommen: {#}",
  "each hop: one bounce, the same fraction of energy lost": "jeder Sprung: ein Stoß, derselbe Energiebruchteil verloren",
  // ensemble
  "thermal neutron": "thermisches Neutron",
  "σ disc": "σ-Scheibe", "disc area = σ at {#} eV": "Scheibenfläche = σ bei {#} eV",
  "{#}k": "{#}k",
  "thermal σ (b)": "thermisches σ (b)", "thermal σ, barns": "thermisches σ, Barn",
  "{#} ladders · thermal ×{#} · res. integral ×{#}": "{#} Leitern · thermisch ×{#} · Res.-Integral ×{#}",
});
// labels that carry a cross section printed as "12 b" or "3.4k b"
(function () {
  const L = WT.L.labels;
  for (const b of ["{#} b", "{#}k b"]) {
    L[b] = b;
    L[`σ ≈ ${b} · caught on {#} % of landings`] = `σ ≈ ${b} · eingefangen bei {#} % der Landungen`;
    L[`σ ≈ ${b} · caught on <{#} % of landings`] = `σ ≈ ${b} · eingefangen bei <{#} % der Landungen`;
    L[`thermal, {#} eV: σ ≈ ${b}`] = `thermisch, {#} eV: σ ≈ ${b}`;
    L[`{#} ladders · thermal σ median ${b}, middle two thirds ×{#} · resonance integral only ×{#}`] =
      `{#} Leitern · thermisches σ Median ${b}, mittlere zwei Drittel ×{#} · Resonanzintegral nur ×{#}`;
  }
})();
