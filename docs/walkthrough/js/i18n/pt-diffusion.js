/* Portuguese (pt-PT): diffusion (Lição 1, dimensão crítica e fugas) */
WT.L.ch.diffusion = {
  num: "Lição 1", title: "Dimensão crítica e fugas", short: "Dimensão crítica",
  html: `
<div class="step">
  <h3>Os neutrões vagueiam, alguns escapam</h3>
  <p>Um neutrão ziguezagueia de colisão em colisão até que algo o absorve. Se nasce perto do bordo, pode vaguear para fora e perder-se. Um núcleo maior tem menos superfície para o seu volume, por isso escapa uma fração menor.</p>
  <div class="ctl"><label for="df-w0">Largura do núcleo (cm)</label><input id="df-w0" type="range" data-bind="w" data-instant min="20" max="200" step="2" value="60"><output data-show="w" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>A forma do fluxo</h3>
  <p>A população de neutrões assenta numa única forma que cai até quase zero no bordo: um cosseno através de uma placa, sin(<i>r</i>)/<i>r</i> numa esfera, uma função de Bessel vezes um cosseno num cilindro. O quanto tem de se curvar é o <b>laplaciano geométrico</b> <i>B</i>² (o <i>buckling</i>).</p>
  <div class="btns"><button class="btn ghost" data-act="dfslab" aria-pressed="false">Placa</button><button class="btn ghost" data-act="dfsph" aria-pressed="true">Esfera</button><button class="btn ghost" data-act="dfcyl" aria-pressed="false">Cilindro</button></div>
  <div class="ctl"><label for="df-w1">Largura do núcleo (cm)</label><input id="df-w1" type="range" data-bind="w" data-instant min="20" max="200" step="2" value="80"><output data-show="w" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Dimensão crítica</h3>
  <p>A difusão a um grupo dá <i>k</i><sub>eff</sub> = <i>k</i><sub>∞</sub> / (1 + <i>M</i>²<i>B</i>²), com a área de migração <i>M</i>² de cerca de 60 cm² num reator de água. O núcleo é crítico quando <i>B</i>² iguala o laplaciano material (<i>k</i><sub>∞</sub> − 1)/<i>M</i>². Encontra essa dimensão.</p>
  <div class="btns"><button class="btn ghost" data-act="dfslab" aria-pressed="false">Placa</button><button class="btn ghost" data-act="dfsph" aria-pressed="true">Esfera</button><button class="btn ghost" data-act="dfcyl" aria-pressed="false">Cilindro</button></div>
  <div class="ctl"><label for="df-w2">Largura do núcleo (cm)</label><input id="df-w2" type="range" data-bind="w" data-instant min="20" max="200" step="1" value="90"><output data-show="w" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Um refletor poupa neutrões</h3>
  <p>Rodeia um núcleo em placa com água: alguns dos neutrões que saem são devolvidos por dispersão. O fluxo já não cai a zero no bordo do núcleo, e um núcleo mais fino atinge o mesmo <i>k</i>; o ganho é a <b>economia de refletor</b>, aqui cerca de 6 cm de cada lado.</p>
  <div class="btns"><button class="btn ghost" data-act="dfrefl" aria-pressed="true">Refletor de água</button></div>
  <div class="ctl"><label for="df-w3">Largura do núcleo (cm)</label><input id="df-w3" type="range" data-bind="w" data-instant min="20" max="120" step="1" value="44"><output data-show="w" data-fmt="0"></output></div>
</div>`,
};
/* attributes referenced in the English chapter script (for the structure check): data-act="${a}" data-act="dfrefl" */

Object.assign(WT.L.labels, {
  "drag the edge": "arrasta o bordo",
  "{#} cm": "{#} cm",
  "red: leaked": "vermelho: escapou",
  "red: leaked out · blue: absorbed inside": "vermelho: escapou · azul: absorvido no interior",
  "leak: walk {#} % · diffusion {#} %": "fugas: passeio {#} % · difusão {#} %",
  "leak: walk … · diffusion {#} %": "fugas: passeio … · difusão {#} %",
  "share leaking: random walk {#} % · diffusion theory {#} %": "fração de fugas: passeio aleatório {#} % · teoria da difusão {#} %",
  "share leaking: random walk … · diffusion theory {#} %": "fração de fugas: passeio aleatório … · teoria da difusão {#} %",
  "k_eff = k∞ × ({#} − leak) = {#}": "k_eff = k∞ × ({#} − fugas) = {#}",
  "water": "água",
  "slab core": "núcleo em placa",
  "slab": "placa",
  "sphere": "esfera",
  "cylinder": "cilindro",
  "flux across the middle": "fluxo através do centro",
  "slab {#} cm wide · smaller core → sharper bend → larger B²": "placa de {#} cm · núcleo menor → curvatura mais forte → B² maior",
  "sphere {#} cm wide · smaller core → sharper bend → larger B²": "esfera de {#} cm · núcleo menor → curvatura mais forte → B² maior",
  "cylinder {#} cm wide · smaller core → sharper bend → larger B²": "cilindro de {#} cm · núcleo menor → curvatura mais forte → B² maior",
  "critical {#} cm": "crítico {#} cm",
  "core width →": "largura do núcleo →",
  "critical: B² = B²ₘ, k_eff = {#}": "crítico: B² = B²ₘ, k_eff = {#}",
  "reflected: k_eff {#} · bare: {#} · savings {#} cm per side": "com refletor: k_eff {#} · nu: {#} · economia {#} cm por lado",
  "bare: k_eff {#} · critical at {#} cm": "nu: k_eff {#} · crítico a {#} cm",
  "illustration": "ilustração",
});
