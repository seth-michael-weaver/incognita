/* French: economy (Le bilan neutronique) */
WT.L.ch.economy = {
  num: "Leçon 1", title: "Le bilan neutronique", short: "Bilan neutronique",
  html: `
<div class="step">
  <h3>Mille neutrons</h3>
  <p>Suivez 1000 neutrons rapides pendant une génération. Quelques-uns provoquent des fissions supplémentaires, certains fuient hors du cœur, d'autres sont capturés en route, et le reste fissionne l'uranium 235 pour donner le millier suivant. Six facteurs se multiplient pour donner <i>k</i> = <i>η f p ε P</i><sub>FNL</sub> <i>P</i><sub>TNL</sub>.</p>
</div>
<div class="step">
  <h3>L'enrichissement</h3>
  <p>Plus il y a d'uranium 235 dans le combustible, plus les neutrons sont absorbés là où ils provoquent une fission. Avec de l'uranium naturel (0,7 %) et de l'eau ordinaire, <i>k</i> n'atteint jamais 1.</p>
  <div class="ctl"><label for="eco-e">Uranium 235 (%)</label><input id="eco-e" type="range" data-bind="enr" min="0.7" max="5" step="0.1" value="3"><output data-show="enr" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>L'eau entre les crayons</h3>
  <p>Trop peu d'eau, et les neutrons en cours de ralentissement sont capturés par l'uranium 238 ; trop d'eau, et c'est l'eau elle-même qui les absorbe. Il existe un rapport optimal, et les réacteurs à eau sont conçus un peu en dessous.</p>
  <div class="ctl"><label for="eco-m">Eau par combustible (× typique)</label><input id="eco-m" type="range" data-bind="m" min="0.3" max="4" step="0.05" value="1"><output data-show="m" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>La taille</h3>
  <p>Les neutrons nés près de la surface peuvent s'échapper. Un petit cœur en perd trop ; un plus grand les retient. Trouvez la taille où <i>k</i> franchit 1.</p>
  <div class="ctl"><label for="eco-s">Taille du cœur (× typique)</label><input id="eco-s" type="range" data-bind="s" min="0.3" max="2" step="0.05" value="0.6"><output data-show="s" data-fmt="2"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "fast fission": "fission rapide",
  "fast leak": "fuite rapide",
  "leaks out, fast": "fuient, rapides",
  "U{#} catches": "capture U{#}",
  "caught by U{#}": "capturés par l'U{#}",
  "slow leak": "fuite lente",
  "leaks out, slow": "fuient, lents",
  "water, steel…": "eau, acier…",
  "water, steel, boron": "eau, acier, bore",
  "P fast {#}": "P rapide {#}",
  "P slow {#}": "P lent {#}",
  "p {#}": "p {#}",
  "f {#}": "f {#}",
  "slowing": "ralentis.",
  "slowing down": "ralentissement",
  "{#} split U{#}": "{#} fissions d'U{#}",
  "next: {#}": "suivante : {#}",
  "next generation: {#}": "génération suivante : {#}",
  "k = {#}": "k = {#}",
  "critical: steady": "critique : stable",
  "grows": "croît",
  "dies away": "s'éteint",
  "best ≈ {#}×": "optimum ≈ {#}×",
  "less water": "moins d'eau",
  "more water": "plus d'eau",
  "{#} % leak out": "{#} % s'échappent",
  "k = η {#} × f {#} × p {#} × ε {#} × P {#} × P {#}": "k = η {#} × f {#} × p {#} × ε {#} × P {#} × P {#}",
  "textbook set (D&H); trends illustrative": "valeurs de manuel (D&H) ; tendances illustratives",
  "factors: textbook set (Duderstadt & Hamilton) at {#} %; slider trends illustrative": "facteurs : valeurs de manuel (Duderstadt & Hamilton) à {#} % ; tendances des curseurs illustratives",
});
