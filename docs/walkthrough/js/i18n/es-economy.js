/* Spanish: economy (El balance neutrónico) */
WT.L.ch.economy = {
  num: "Lección 1", title: "El balance neutrónico", short: "Balance neutrónico",
  html: `
<div class="step">
  <h3>Mil neutrones</h3>
  <p>Sigue a 1000 neutrones rápidos durante una generación. Unos pocos causan fisiones adicionales, algunos se fugan, otros son capturados por el camino, y el resto parte uranio-235 para producir el millar siguiente. Seis factores se multiplican para dar <i>k</i> = <i>η f p ε P</i><sub>FNL</sub> <i>P</i><sub>TNL</sub>.</p>
</div>
<div class="step">
  <h3>Enriquecimiento</h3>
  <p>Más uranio-235 en el combustible significa que más neutrones se absorben donde causan fisión. Con uranio natural (0,7 %) y agua ordinaria, <i>k</i> nunca llega a 1.</p>
  <div class="ctl"><label for="eco-e">Uranio-235 (%)</label><input id="eco-e" type="range" data-bind="enr" min="0.7" max="5" step="0.1" value="3"><output data-show="enr" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>El agua entre las varillas</h3>
  <p>Con poca agua, el uranio-238 captura los neutrones mientras se frenan; con demasiada, es la propia agua la que los absorbe. Hay una proporción óptima, y los reactores de agua se construyen un poco por debajo de ella.</p>
  <div class="ctl"><label for="eco-m">Agua por combustible (× típica)</label><input id="eco-m" type="range" data-bind="m" min="0.3" max="4" step="0.05" value="1"><output data-show="m" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Tamaño</h3>
  <p>Los neutrones que nacen cerca de la superficie pueden escapar. Un núcleo pequeño pierde demasiados; uno más grande los retiene. Encuentra el tamaño en el que <i>k</i> cruza 1.</p>
  <div class="ctl"><label for="eco-s">Tamaño del núcleo (× típico)</label><input id="eco-s" type="range" data-bind="s" min="0.3" max="2" step="0.05" value="0.6"><output data-show="s" data-fmt="2"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "fast fission": "fisión rápida",
  "fast leak": "fuga rápida",
  "leaks out, fast": "se fugan, rápidos",
  "U{#} catches": "captura en U{#}",
  "caught by U{#}": "capturados por U{#}",
  "slow leak": "fuga lenta",
  "leaks out, slow": "se fugan, lentos",
  "water, steel…": "agua, acero…",
  "water, steel, boron": "agua, acero, boro",
  "P fast {#}": "P rápida {#}",
  "P slow {#}": "P lenta {#}",
  "p {#}": "p {#}",
  "f {#}": "f {#}",
  "slowing": "frenado",
  "slowing down": "moderación",
  "{#} split U{#}": "{#} fisionan U{#}",
  "next: {#}": "siguiente: {#}",
  "next generation: {#}": "siguiente generación: {#}",
  "k = {#}": "k = {#}",
  "critical: steady": "crítico: estable",
  "grows": "crece",
  "dies away": "se extingue",
  "best ≈ {#}×": "óptimo ≈ {#}×",
  "less water": "menos agua",
  "more water": "más agua",
  "{#} % leak out": "se fuga el {#} %",
  "k = η {#} × f {#} × p {#} × ε {#} × P {#} × P {#}": "k = η {#} × f {#} × p {#} × ε {#} × P {#} × P {#}",
  "textbook set (D&H); trends illustrative": "valores de manual (D&H); tendencias ilustrativas",
  "factors: textbook set (Duderstadt & Hamilton) at {#} %; slider trends illustrative": "factores: valores de manual (Duderstadt & Hamilton) al {#} %; tendencias de los deslizadores ilustrativas",
});
