/* Spanish: diffusion (Lección 1, tamaño crítico y fugas) */
WT.L.ch.diffusion = {
  num: "Lección 1", title: "Tamaño crítico y fugas", short: "Tamaño crítico",
  html: `
<div class="step">
  <h3>Los neutrones vagan y algunos se fugan</h3>
  <p>Un neutrón zigzaguea de colisión en colisión hasta que algo lo absorbe. Si nace cerca del borde, puede salir vagando y perderse. Un núcleo más grande tiene menos superficie para su volumen, así que se fuga una fracción menor.</p>
  <div class="ctl"><label for="df-w0">Anchura del núcleo (cm)</label><input id="df-w0" type="range" data-bind="w" data-instant min="20" max="200" step="2" value="60"><output data-show="w" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>La forma del flujo</h3>
  <p>La población de neutrones se asienta en una única forma que cae casi a cero en el borde: un coseno a través de una placa, sin(<i>r</i>)/<i>r</i> en una esfera, una función de Bessel por un coseno en un cilindro. Lo bruscamente que debe curvarse es el <b>laplaciano geométrico</b> (buckling) <i>B</i>².</p>
  <div class="btns"><button class="btn ghost" data-act="dfslab" aria-pressed="false">Placa</button><button class="btn ghost" data-act="dfsph" aria-pressed="true">Esfera</button><button class="btn ghost" data-act="dfcyl" aria-pressed="false">Cilindro</button></div>
  <div class="ctl"><label for="df-w1">Anchura del núcleo (cm)</label><input id="df-w1" type="range" data-bind="w" data-instant min="20" max="200" step="2" value="80"><output data-show="w" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Tamaño crítico</h3>
  <p>La difusión de un grupo da <i>k</i><sub>eff</sub> = <i>k</i><sub>∞</sub> / (1 + <i>M</i>²<i>B</i>²), con un área de migración <i>M</i>² de unos 60 cm² en un reactor de agua. El núcleo es crítico cuando <i>B</i>² iguala al laplaciano material (<i>k</i><sub>∞</sub> − 1)/<i>M</i>². Encuentra ese tamaño.</p>
  <div class="btns"><button class="btn ghost" data-act="dfslab" aria-pressed="false">Placa</button><button class="btn ghost" data-act="dfsph" aria-pressed="true">Esfera</button><button class="btn ghost" data-act="dfcyl" aria-pressed="false">Cilindro</button></div>
  <div class="ctl"><label for="df-w2">Anchura del núcleo (cm)</label><input id="df-w2" type="range" data-bind="w" data-instant min="20" max="200" step="1" value="90"><output data-show="w" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Un reflector ahorra neutrones</h3>
  <p>Rodea de agua un núcleo en placa: algunos de los neutrones que salen rebotan de vuelta. El flujo ya no cae a cero en el borde del núcleo, así que un núcleo más delgado alcanza la misma <i>k</i>; la ganancia es el <b>ahorro del reflector</b>, aquí unos 6 cm por lado.</p>
  <div class="btns"><button class="btn ghost" data-act="dfrefl" aria-pressed="true">Reflector de agua</button></div>
  <div class="ctl"><label for="df-w3">Anchura del núcleo (cm)</label><input id="df-w3" type="range" data-bind="w" data-instant min="20" max="120" step="1" value="44"><output data-show="w" data-fmt="0"></output></div>
</div>`,
};
/* attributes referenced in the English chapter script (for the structure check): data-act="${a}" data-act="dfrefl" */

Object.assign(WT.L.labels, {
  "drag the edge": "arrastra el borde",
  "{#} cm": "{#} cm",
  "red: leaked": "rojo: fugado",
  "red: leaked out · blue: absorbed inside": "rojo: fugado · azul: absorbido dentro",
  "leak: walk {#} % · diffusion {#} %": "fugas: paseo {#} % · difusión {#} %",
  "leak: walk … · diffusion {#} %": "fugas: paseo … · difusión {#} %",
  "share leaking: random walk {#} % · diffusion theory {#} %": "fracción que se fuga: paseo aleatorio {#} % · teoría de difusión {#} %",
  "share leaking: random walk … · diffusion theory {#} %": "fracción que se fuga: paseo aleatorio … · teoría de difusión {#} %",
  "k_eff = k∞ × ({#} − leak) = {#}": "k_eff = k∞ × ({#} − fugas) = {#}",
  "water": "agua",
  "slab core": "núcleo en placa",
  "slab": "placa",
  "sphere": "esfera",
  "cylinder": "cilindro",
  "flux across the middle": "flujo a través del centro",
  "slab {#} cm wide · smaller core → sharper bend → larger B²": "placa de {#} cm · núcleo menor → curva más brusca → B² mayor",
  "sphere {#} cm wide · smaller core → sharper bend → larger B²": "esfera de {#} cm · núcleo menor → curva más brusca → B² mayor",
  "cylinder {#} cm wide · smaller core → sharper bend → larger B²": "cilindro de {#} cm · núcleo menor → curva más brusca → B² mayor",
  "critical {#} cm": "crítico {#} cm",
  "core width →": "anchura del núcleo →",
  "critical: B² = B²ₘ, k_eff = {#}": "crítico: B² = B²ₘ, k_eff = {#}",
  "reflected: k_eff {#} · bare: {#} · savings {#} cm per side": "con reflector: k_eff {#} · desnudo: {#} · ahorro {#} cm por lado",
  "bare: k_eff {#} · critical at {#} cm": "desnudo: k_eff {#} · crítico a {#} cm",
  "illustration": "ilustración",
});
