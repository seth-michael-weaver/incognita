/* Danish: diffusion (Kritisk størrelse og lækage) */
WT.L.ch.diffusion = {
  num: "Lektion 14", title: "Kritisk størrelse og lækage", short: "Kritisk størrelse",
  html: `
<div class="step">
  <h3>Neutroner vandrer, nogle slipper ud</h3>
  <p>En neutron går i zigzag fra stød til stød, indtil noget absorberer den. Er den født nær kanten, kan den vandre ud og gå tabt. En større kerne har mindre overflade i forhold til sit rumfang, så en mindre andel slipper ud.</p>
  <div class="ctl"><label for="df-w0">Kernebredde (cm)</label><input id="df-w0" type="range" data-bind="w" data-instant min="20" max="200" step="2" value="60"><output data-show="w" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Fluxens form</h3>
  <p>Neutronbestanden falder til ro i én form, der falder til omkring nul ved kanten: en cosinus på tværs af en plade, sin(<i>r</i>)/<i>r</i> i en kugle, en besselfunktion gange en cosinus i en cylinder. Hvor skarpt den skal bøje, er den <b>geometriske buckling</b> <i>B</i>².</p>
  <div class="btns"><button class="btn ghost" data-act="dfslab" aria-pressed="false">Plade</button><button class="btn ghost" data-act="dfsph" aria-pressed="true">Kugle</button><button class="btn ghost" data-act="dfcyl" aria-pressed="false">Cylinder</button></div>
  <div class="ctl"><label for="df-w1">Kernebredde (cm)</label><input id="df-w1" type="range" data-bind="w" data-instant min="20" max="200" step="2" value="80"><output data-show="w" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Kritisk størrelse</h3>
  <p>Diffusion med én gruppe giver <i>k</i><sub>eff</sub> = <i>k</i><sub>∞</sub> / (1 + <i>M</i>²<i>B</i>²), med migrationsarealet <i>M</i>² omkring 60 cm² i en vandreaktor. Kernen er kritisk, når <i>B</i>² er lig med materialebucklingen (<i>k</i><sub>∞</sub> − 1)/<i>M</i>². Find den størrelse.</p>
  <div class="btns"><button class="btn ghost" data-act="dfslab" aria-pressed="false">Plade</button><button class="btn ghost" data-act="dfsph" aria-pressed="true">Kugle</button><button class="btn ghost" data-act="dfcyl" aria-pressed="false">Cylinder</button></div>
  <div class="ctl"><label for="df-w2">Kernebredde (cm)</label><input id="df-w2" type="range" data-bind="w" data-instant min="20" max="200" step="1" value="90"><output data-show="w" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>En reflektor sparer neutroner</h3>
  <p>Omgiv en pladeformet kerne med vand: nogle af de neutroner, der forlader den, spredes tilbage. Fluxen falder ikke længere til nul ved kernens kant, så en tyndere kerne når samme <i>k</i>; gevinsten er <b>reflektorbesparelsen</b>, her omkring 6 cm pr. side.</p>
  <div class="btns"><button class="btn ghost" data-act="dfrefl" aria-pressed="true">Vandreflektor</button></div>
  <div class="ctl"><label for="df-w3">Kernebredde (cm)</label><input id="df-w3" type="range" data-bind="w" data-instant min="20" max="120" step="1" value="44"><output data-show="w" data-fmt="0"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "B² = (π/a)² = {#} × {#}⁻⁴ cm⁻²": "B² = (π/a)² = {#} × {#}⁻⁴ cm⁻²",
  "B² = (π/R)² = {#} × {#}⁻⁴ cm⁻²": "B² = (π/R)² = {#} × {#}⁻⁴ cm⁻²",
  "B² = ({#}/R)² + (π/H)² = {#} × {#}⁻⁴ cm⁻²": "B² = ({#}/R)² + (π/H)² = {#} × {#}⁻⁴ cm⁻²",
  "{#} × {#}⁻⁴ cm⁻²": "{#} × {#}⁻⁴ cm⁻²",
  "bare: k_eff {#} · critical at {#} cm": "bar: k_eff {#} · kritisk ved {#} cm",
  "reflected: k_eff {#} · bare: {#} · savings {#} cm per side": "reflekteret: k_eff {#} · bar: {#} · besparelse {#} cm pr. side",
  "core width →": "kernebredde →",
  "critical {#} cm": "kritisk {#} cm",
  "critical: B² = B²ₘ, k_eff = {#}": "kritisk: B² = B²ₘ, k_eff = {#}",
  "slab": "plade",
  "sphere": "kugle",
  "cylinder": "cylinder",
  "slab core": "pladekerne",
  "slab {#} cm wide · smaller core → sharper bend → larger B²": "plade {#} cm bred · mindre kerne → skarpere bøjning → større B²",
  "sphere {#} cm wide · smaller core → sharper bend → larger B²": "kugle {#} cm bred · mindre kerne → skarpere bøjning → større B²",
  "cylinder {#} cm wide · smaller core → sharper bend → larger B²": "cylinder {#} cm bred · mindre kerne → skarpere bøjning → større B²",
  "drag the edge": "træk i kanten",
  "flux across the middle": "flux på tværs af midten",
  "illustration": "illustration",
  "k = {#}": "k = {#}",
  "k_eff = k∞ × ({#} − leak) = {#}": "k_eff = k∞ × ({#} − lækage) = {#}",
  "k_eff = {#} / ({#} + {#} cm² × {#}e{#} cm⁻²) = {#}": "k_eff = {#} / ({#} + {#} cm² × {#}e{#} cm⁻²) = {#}",
  "leak: walk {#} % · diffusion {#} %": "lækage: vandring {#} % · diffusion {#} %",
  "leak: walk … · diffusion {#} %": "lækage: vandring … · diffusion {#} %",
  "red: leaked": "rød: sluppet ud",
  "red: leaked out · blue: absorbed inside": "rød: sluppet ud · blå: absorberet indeni",
  "share leaking: random walk {#} % · diffusion theory {#} %": "andel der slipper ud: tilfældig vandring {#} % · diffusionsteori {#} %",
  "share leaking: random walk … · diffusion theory {#} %": "andel der slipper ud: tilfældig vandring … · diffusionsteori {#} %",
  "water": "vand",
  "{#} cm": "{#} cm",
  "−D∇²φ + Σₐφ = (νΣ_f / k) φ": "−D∇²φ + Σₐφ = (νΣ_f / k) φ",
});
