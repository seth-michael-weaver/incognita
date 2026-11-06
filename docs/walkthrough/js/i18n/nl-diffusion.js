/* Dutch (Nederlands): diffusion (Kritieke grootte en lekkage) */
WT.L.ch.diffusion = {
  num: "Les 14", title: "Kritieke grootte en lekkage", short: "Kritieke grootte",
  html: `
<div class="step">
  <h3>Neutronen zwerven, sommige lekken weg</h3>
  <p>Een neutron zigzagt van botsing naar botsing tot iets het absorbeert. Ontstaat het dicht bij de rand, dan kan het naar buiten zwerven en verloren gaan. Een grotere kern heeft minder oppervlak voor zijn volume, dus lekt een kleiner deel weg.</p>
  <div class="ctl"><label for="df-w0">Kernbreedte (cm)</label><input id="df-w0" type="range" data-bind="w" data-instant min="20" max="200" step="2" value="60"><output data-show="w" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>De vorm van de flux</h3>
  <p>De neutronenpopulatie komt tot rust in één vorm die aan de rand tot ongeveer nul daalt: een cosinus door een plaat, sin(<i>r</i>)/<i>r</i> in een bol, een besselfunctie maal een cosinus in een cilinder. Hoe scherp ze moet buigen, is de <b>geometrische buckling</b> <i>B</i>².</p>
  <div class="btns"><button class="btn ghost" data-act="dfslab" aria-pressed="false">Plaat</button><button class="btn ghost" data-act="dfsph" aria-pressed="true">Bol</button><button class="btn ghost" data-act="dfcyl" aria-pressed="false">Cilinder</button></div>
  <div class="ctl"><label for="df-w1">Kernbreedte (cm)</label><input id="df-w1" type="range" data-bind="w" data-instant min="20" max="200" step="2" value="80"><output data-show="w" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Kritieke grootte</h3>
  <p>Diffusie met één groep geeft <i>k</i><sub>eff</sub> = <i>k</i><sub>∞</sub> / (1 + <i>M</i>²<i>B</i>²), met het migratieoppervlak <i>M</i>² ongeveer 60 cm² in een waterreactor. De kern is kritiek als <i>B</i>² gelijk is aan de materiële buckling (<i>k</i><sub>∞</sub> − 1)/<i>M</i>². Zoek die grootte.</p>
  <div class="btns"><button class="btn ghost" data-act="dfslab" aria-pressed="false">Plaat</button><button class="btn ghost" data-act="dfsph" aria-pressed="true">Bol</button><button class="btn ghost" data-act="dfcyl" aria-pressed="false">Cilinder</button></div>
  <div class="ctl"><label for="df-w2">Kernbreedte (cm)</label><input id="df-w2" type="range" data-bind="w" data-instant min="20" max="200" step="1" value="90"><output data-show="w" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Een reflector spaart neutronen</h3>
  <p>Omring een plaatvormige kern met water: sommige neutronen die vertrekken, worden teruggestrooid. De flux zakt aan de kernrand niet meer tot nul, dus een dunnere kern haalt dezelfde <i>k</i>; de winst is de <b>reflectorbesparing</b>, hier ongeveer 6 cm per kant.</p>
  <div class="btns"><button class="btn ghost" data-act="dfrefl" aria-pressed="true">Waterreflector</button></div>
  <div class="ctl"><label for="df-w3">Kernbreedte (cm)</label><input id="df-w3" type="range" data-bind="w" data-instant min="20" max="120" step="1" value="44"><output data-show="w" data-fmt="0"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "B² = (π/a)² = {#} × {#}⁻⁴ cm⁻²": "B² = (π/a)² = {#} × {#}⁻⁴ cm⁻²",
  "B² = (π/R)² = {#} × {#}⁻⁴ cm⁻²": "B² = (π/R)² = {#} × {#}⁻⁴ cm⁻²",
  "B² = ({#}/R)² + (π/H)² = {#} × {#}⁻⁴ cm⁻²": "B² = ({#}/R)² + (π/H)² = {#} × {#}⁻⁴ cm⁻²",
  "{#} × {#}⁻⁴ cm⁻²": "{#} × {#}⁻⁴ cm⁻²",
  "bare: k_eff {#} · critical at {#} cm": "kaal: k_eff {#} · kritiek bij {#} cm",
  "reflected: k_eff {#} · bare: {#} · savings {#} cm per side": "gereflecteerd: k_eff {#} · kaal: {#} · besparing {#} cm per kant",
  "core width →": "kernbreedte →",
  "critical {#} cm": "kritiek {#} cm",
  "critical: B² = B²ₘ, k_eff = {#}": "kritiek: B² = B²ₘ, k_eff = {#}",
  "slab": "plaat",
  "sphere": "bol",
  "cylinder": "cilinder",
  "slab core": "plaatkern",
  "slab {#} cm wide · smaller core → sharper bend → larger B²": "plaat {#} cm breed · kleinere kern → scherpere buiging → grotere B²",
  "sphere {#} cm wide · smaller core → sharper bend → larger B²": "bol {#} cm breed · kleinere kern → scherpere buiging → grotere B²",
  "cylinder {#} cm wide · smaller core → sharper bend → larger B²": "cilinder {#} cm breed · kleinere kern → scherpere buiging → grotere B²",
  "drag the edge": "sleep de rand",
  "flux across the middle": "flux door het midden",
  "illustration": "illustratie",
  "k = {#}": "k = {#}",
  "k_eff = k∞ × ({#} − leak) = {#}": "k_eff = k∞ × ({#} − lek) = {#}",
  "k_eff = {#} / ({#} + {#} cm² × {#}e{#} cm⁻²) = {#}": "k_eff = {#} / ({#} + {#} cm² × {#}e{#} cm⁻²) = {#}",
  "leak: walk {#} % · diffusion {#} %": "lek: wandeling {#} % · diffusie {#} %",
  "leak: walk … · diffusion {#} %": "lek: wandeling … · diffusie {#} %",
  "red: leaked": "rood: weggelekt",
  "red: leaked out · blue: absorbed inside": "rood: weggelekt · blauw: binnen geabsorbeerd",
  "share leaking: random walk {#} % · diffusion theory {#} %": "lekkend deel: willekeurige wandeling {#} % · diffusietheorie {#} %",
  "share leaking: random walk … · diffusion theory {#} %": "lekkend deel: willekeurige wandeling … · diffusietheorie {#} %",
  "water": "water",
  "{#} cm": "{#} cm",
  "−D∇²φ + Σₐφ = (νΣ_f / k) φ": "−D∇²φ + Σₐφ = (νΣ_f / k) φ",
});
