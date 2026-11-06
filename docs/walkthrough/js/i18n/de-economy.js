/* German (Deutsch): economy (Die Neutronenbilanz) */
WT.L.ch.economy = {
  num: "Lektion 7", title: "Die Neutronenbilanz", short: "Neutronenbilanz",
  html: `
<div class="step">
  <h3>Tausend Neutronen</h3>
  <p>Verfolge 1000 schnelle Neutronen durch eine Generation. Einige lösen zusätzliche Spaltungen aus, manche entweichen, manche werden unterwegs eingefangen, und der Rest spaltet Uran-235 und erzeugt die nächsten tausend. Sechs Faktoren ergeben multipliziert <i>k</i> = <i>η f p ε P</i><sub>FNL</sub> <i>P</i><sub>TNL</sub>.</p>
</div>
<div class="step">
  <h3>Anreicherung</h3>
  <p>Mehr Uran-235 im Brennstoff heißt, dass mehr Neutronen dort absorbiert werden, wo sie Spaltungen auslösen. Mit Natururan (0,7 %) und gewöhnlichem Wasser erreicht <i>k</i> nie 1.</p>
  <div class="ctl"><label for="eco-e">Uran-235 (%)</label><input id="eco-e" type="range" data-bind="enr" min="0.7" max="5" step="0.1" value="3"><output data-show="enr" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Wasser zwischen den Stäben</h3>
  <p>Zu wenig Wasser, und die sich abbremsenden Neutronen werden von Uran-238 eingefangen; zu viel, und das Wasser selbst absorbiert sie. Es gibt ein bestes Verhältnis, und Wasserreaktoren werden etwas darunter gebaut.</p>
  <div class="ctl"><label for="eco-m">Wasser pro Brennstoff (× typisch)</label><input id="eco-m" type="range" data-bind="m" min="0.3" max="4" step="0.05" value="1"><output data-show="m" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Größe</h3>
  <p>Neutronen, die nahe der Oberfläche entstehen, können entweichen. Ein kleiner Kern verliert zu viele; ein größerer hält sie. Finde die Größe, bei der <i>k</i> die 1 überschreitet.</p>
  <div class="ctl"><label for="eco-s">Kerngröße (× typisch)</label><input id="eco-s" type="range" data-bind="s" min="0.3" max="2" step="0.05" value="0.6"><output data-show="s" data-fmt="2"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "P fast {#}": "P schnell {#}",
  "P slow {#}": "P langsam {#}",
  "U{#} catches": "U{#} fängt ein",
  "best ≈ {#}×": "optimal ≈ {#}×",
  "caught by U{#}": "von U{#} eingefangen",
  "critical: steady": "kritisch: konstant",
  "dies away": "stirbt ab",
  "f {#}": "f {#}",
  "factors: textbook set (Duderstadt & Hamilton) at {#} %; slider trends illustrative": "Faktoren: Lehrbuchsatz (Duderstadt & Hamilton) bei {#} %; Trends der Regler zur Veranschaulichung",
  "fast fission": "Schnellspaltung",
  "fast leak": "schnelles Entweichen",
  "grows": "wächst",
  "k = {#}": "k = {#}",
  "k = η {#} × f {#} × p {#} × ε {#} × P {#} × P {#}": "k = η {#} × f {#} × p {#} × ε {#} × P {#} × P {#}",
  "leaks out, fast": "entweicht schnell",
  "leaks out, slow": "entweicht langsam",
  "less water": "weniger Wasser",
  "more water": "mehr Wasser",
  "next generation: {#}": "nächste Generation: {#}",
  "next: {#}": "nächste: {#}",
  "p {#}": "p {#}",
  "slow leak": "langsames Entweichen",
  "slowing": "Abbremsung",
  "slowing down": "Abbremsung",
  "textbook set (D&H); trends illustrative": "Lehrbuchsatz (D&H); Trends zur Veranschaulichung",
  "water, steel, boron": "Wasser, Stahl, Bor",
  "water, steel…": "Wasser, Stahl …",
  "{#} % leak out": "{#} % entweichen",
  "{#} split U{#}": "{#} spalten U{#}",
});
