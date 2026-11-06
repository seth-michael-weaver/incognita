/* Portuguese (pt-PT): economy (O balanço neutrónico) */
WT.L.ch.economy = {
  num: "Lição 1", title: "O balanço neutrónico", short: "Balanço neutrónico",
  html: `
<div class="step">
  <h3>Mil neutrões</h3>
  <p>Segue 1000 neutrões rápidos ao longo de uma geração. Alguns causam fissões extra, alguns escapam, alguns são capturados pelo caminho, e os restantes cindem urânio-235 para produzir o milhar seguinte. Seis fatores multiplicam-se para dar <i>k</i> = <i>η f p ε P</i><sub>FNL</sub> <i>P</i><sub>TNL</sub>.</p>
</div>
<div class="step">
  <h3>Enriquecimento</h3>
  <p>Mais urânio-235 no combustível significa que mais neutrões são absorvidos onde causam fissão. Com urânio natural (0,7 %) e água comum, <i>k</i> nunca chega a 1.</p>
  <div class="ctl"><label for="eco-e">Urânio-235 (%)</label><input id="eco-e" type="range" data-bind="enr" min="0.7" max="5" step="0.1" value="3"><output data-show="enr" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Água entre as varetas</h3>
  <p>Água a menos, e os neutrões em abrandamento são capturados pelo urânio-238; água a mais, e é a própria água que os absorve. Há uma proporção ótima, e os reatores de água são construídos um pouco abaixo dela.</p>
  <div class="ctl"><label for="eco-m">Água por combustível (× típico)</label><input id="eco-m" type="range" data-bind="m" min="0.3" max="4" step="0.05" value="1"><output data-show="m" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Tamanho</h3>
  <p>Os neutrões que nascem perto da superfície podem escapar. Um núcleo pequeno perde demasiados; um maior retém-nos. Encontra o tamanho em que <i>k</i> passa por 1.</p>
  <div class="ctl"><label for="eco-s">Tamanho do núcleo (× típico)</label><input id="eco-s" type="range" data-bind="s" min="0.3" max="2" step="0.05" value="0.6"><output data-show="s" data-fmt="2"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "fast fission": "fissão rápida",
  "fast leak": "fuga rápida",
  "leaks out, fast": "escapam, rápidos",
  "U{#} catches": "captura U{#}",
  "caught by U{#}": "capturados pelo U{#}",
  "slow leak": "fuga lenta",
  "leaks out, slow": "escapam, lentos",
  "water, steel…": "água, aço…",
  "water, steel, boron": "água, aço, boro",
  "P fast {#}": "P rápido {#}",
  "P slow {#}": "P lento {#}",
  "p {#}": "p {#}",
  "f {#}": "f {#}",
  "slowing": "abrandam.",
  "slowing down": "abrandamento",
  "{#} split U{#}": "{#} fissões de U{#}",
  "next: {#}": "seguinte: {#}",
  "next generation: {#}": "geração seguinte: {#}",
  "k = {#}": "k = {#}",
  "critical: steady": "crítico: estável",
  "grows": "cresce",
  "dies away": "extingue-se",
  "best ≈ {#}×": "ótimo ≈ {#}×",
  "less water": "menos água",
  "more water": "mais água",
  "{#} % leak out": "{#} % escapam",
  "k = η {#} × f {#} × p {#} × ε {#} × P {#} × P {#}": "k = η {#} × f {#} × p {#} × ε {#} × P {#} × P {#}",
  "textbook set (D&H); trends illustrative": "valores de manual (D&H); tendências ilustrativas",
  "factors: textbook set (Duderstadt & Hamilton) at {#} %; slider trends illustrative": "fatores: valores de manual (Duderstadt & Hamilton) a {#} %; tendências dos cursores ilustrativas",
});
