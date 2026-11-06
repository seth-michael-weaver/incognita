/* German (Deutsch): diffusion (Kritische Größe und Leckage) */
WT.L.ch.diffusion = {
  num: "Lektion 14", title: "Kritische Größe und Leckage", short: "Kritische Größe",
  html: `
<div class="step">
  <h3>Neutronen wandern, manche entweichen</h3>
  <p>Ein Neutron läuft im Zickzack von Stoß zu Stoß, bis etwas es absorbiert. Entsteht es nahe am Rand, kann es hinauswandern und verloren gehen. Ein größerer Kern hat im Verhältnis zu seinem Volumen weniger Oberfläche, also entweicht ein kleinerer Anteil.</p>
  <div class="ctl"><label for="df-w0">Kernbreite (cm)</label><input id="df-w0" type="range" data-bind="w" data-instant min="20" max="200" step="2" value="60"><output data-show="w" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Die Form des Flusses</h3>
  <p>Die Neutronenpopulation stellt sich auf eine Form ein, die am Rand auf etwa null fällt: ein Kosinus quer durch eine Platte, sin(<i>r</i>)/<i>r</i> in einer Kugel, eine Bessel-Funktion mal einem Kosinus in einem Zylinder. Wie stark sie sich krümmen muss, ist das <b>geometrische Buckling</b> <i>B</i>².</p>
  <div class="btns"><button class="btn ghost" data-act="dfslab" aria-pressed="false">Platte</button><button class="btn ghost" data-act="dfsph" aria-pressed="true">Kugel</button><button class="btn ghost" data-act="dfcyl" aria-pressed="false">Zylinder</button></div>
  <div class="ctl"><label for="df-w1">Kernbreite (cm)</label><input id="df-w1" type="range" data-bind="w" data-instant min="20" max="200" step="2" value="80"><output data-show="w" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Kritische Größe</h3>
  <p>Die Ein-Gruppen-Diffusion liefert <i>k</i><sub>eff</sub> = <i>k</i><sub>∞</sub> / (1 + <i>M</i>²<i>B</i>²), mit der Migrationsfläche <i>M</i>² von etwa 60 cm² in einem Wasserreaktor. Der Kern ist kritisch, wenn <i>B</i>² gleich dem materiellen Buckling (<i>k</i><sub>∞</sub> − 1)/<i>M</i>² ist. Finde diese Größe.</p>
  <div class="btns"><button class="btn ghost" data-act="dfslab" aria-pressed="false">Platte</button><button class="btn ghost" data-act="dfsph" aria-pressed="true">Kugel</button><button class="btn ghost" data-act="dfcyl" aria-pressed="false">Zylinder</button></div>
  <div class="ctl"><label for="df-w2">Kernbreite (cm)</label><input id="df-w2" type="range" data-bind="w" data-instant min="20" max="200" step="1" value="90"><output data-show="w" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Ein Reflektor spart Neutronen</h3>
  <p>Umgib einen Plattenkern mit Wasser: Einige der austretenden Neutronen werden zurückgestreut. Der Fluss fällt am Kernrand nicht mehr auf null, also erreicht ein dünnerer Kern dasselbe <i>k</i>; der Gewinn ist die <b>Reflektorersparnis</b>, hier etwa 6 cm pro Seite.</p>
  <div class="btns"><button class="btn ghost" data-act="dfrefl" aria-pressed="true">Wasserreflektor</button></div>
  <div class="ctl"><label for="df-w3">Kernbreite (cm)</label><input id="df-w3" type="range" data-bind="w" data-instant min="20" max="120" step="1" value="44"><output data-show="w" data-fmt="0"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "B² = (π/a)² = {#} × {#}⁻⁴ cm⁻²": "B² = (π/a)² = {#} × {#}⁻⁴ cm⁻²",
  "B² = (π/R)² = {#} × {#}⁻⁴ cm⁻²": "B² = (π/R)² = {#} × {#}⁻⁴ cm⁻²",
  "B² = ({#}/R)² + (π/H)² = {#} × {#}⁻⁴ cm⁻²": "B² = ({#}/R)² + (π/H)² = {#} × {#}⁻⁴ cm⁻²",
  "{#} × {#}⁻⁴ cm⁻²": "{#} × {#}⁻⁴ cm⁻²",
  "bare: k_eff {#} · critical at {#} cm": "nackt: k_eff {#} · kritisch bei {#} cm",
  "reflected: k_eff {#} · bare: {#} · savings {#} cm per side": "reflektiert: k_eff {#} · nackt: {#} · Ersparnis {#} cm pro Seite",
  "core width →": "Kernbreite →",
  "critical {#} cm": "kritisch {#} cm",
  "critical: B² = B²ₘ, k_eff = {#}": "kritisch: B² = B²ₘ, k_eff = {#}",
  "slab": "Platte",
  "sphere": "Kugel",
  "cylinder": "Zylinder",
  "slab core": "Plattenkern",
  "slab {#} cm wide · smaller core → sharper bend → larger B²": "Platte, {#} cm breit · kleinerer Kern → stärkere Krümmung → größeres B²",
  "sphere {#} cm wide · smaller core → sharper bend → larger B²": "Kugel, {#} cm breit · kleinerer Kern → stärkere Krümmung → größeres B²",
  "cylinder {#} cm wide · smaller core → sharper bend → larger B²": "Zylinder, {#} cm breit · kleinerer Kern → stärkere Krümmung → größeres B²",
  "drag the edge": "Rand ziehen",
  "flux across the middle": "Fluss quer durch die Mitte",
  "illustration": "Illustration",
  "k = {#}": "k = {#}",
  "k_eff = k∞ × ({#} − leak) = {#}": "k_eff = k∞ × ({#} − Leckage) = {#}",
  "k_eff = {#} / ({#} + {#} cm² × {#}e{#} cm⁻²) = {#}": "k_eff = {#} / ({#} + {#} cm² × {#}e{#} cm⁻²) = {#}",
  "leak: walk {#} % · diffusion {#} %": "Leckage: Irrflug {#} % · Diffusion {#} %",
  "leak: walk … · diffusion {#} %": "Leckage: Irrflug … · Diffusion {#} %",
  "red: leaked": "rot: entwichen",
  "red: leaked out · blue: absorbed inside": "rot: entwichen · blau: im Inneren absorbiert",
  "share leaking: random walk {#} % · diffusion theory {#} %": "entweichender Anteil: Irrflug {#} % · Diffusionstheorie {#} %",
  "share leaking: random walk … · diffusion theory {#} %": "entweichender Anteil: Irrflug … · Diffusionstheorie {#} %",
  "water": "Wasser",
  "{#} cm": "{#} cm",
  "−D∇²φ + Σₐφ = (νΣ_f / k) φ": "−D∇²φ + Σₐφ = (νΣ_f / k) φ",
});
