/* Dutch (Nederlands): economy (De neutronenbalans) */
WT.L.ch.economy = {
  num: "Les 7", title: "De neutronenbalans", short: "Neutronenbalans",
  html: `
<div class="step">
  <h3>Duizend neutronen</h3>
  <p>Volg 1000 snelle neutronen door één generatie. Een paar veroorzaken extra splijtingen, sommige lekken weg, sommige worden onderweg gevangen, en de rest splijt uranium-235 om de volgende duizend te maken. Zes factoren vermenigvuldigen tot <i>k</i> = <i>η f p ε P</i><sub>FNL</sub> <i>P</i><sub>TNL</sub>.</p>
</div>
<div class="step">
  <h3>Verrijking</h3>
  <p>Meer uranium-235 in de brandstof betekent dat meer neutronen worden geabsorbeerd waar ze splijting veroorzaken. Met natuurlijk uranium (0,7 %) en gewoon water haalt <i>k</i> nooit 1.</p>
  <div class="ctl"><label for="eco-e">Uranium-235 (%)</label><input id="eco-e" type="range" data-bind="enr" min="0.7" max="5" step="0.1" value="3"><output data-show="enr" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Water tussen de staven</h3>
  <p>Te weinig water en de afremmende neutronen worden door uranium-238 gevangen; te veel en het water zelf absorbeert ze. Er is een beste verhouding, en waterreactoren worden iets daaronder gebouwd.</p>
  <div class="ctl"><label for="eco-m">Water per brandstof (× typisch)</label><input id="eco-m" type="range" data-bind="m" min="0.3" max="4" step="0.05" value="1"><output data-show="m" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Grootte</h3>
  <p>Neutronen die dicht bij het oppervlak ontstaan, kunnen ontsnappen. Een kleine kern lekt er te veel; een grotere houdt ze vast. Zoek de grootte waarbij <i>k</i> door 1 gaat.</p>
  <div class="ctl"><label for="eco-s">Kerngrootte (× typisch)</label><input id="eco-s" type="range" data-bind="s" min="0.3" max="2" step="0.05" value="0.6"><output data-show="s" data-fmt="2"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "P fast {#}": "P snel {#}",
  "P slow {#}": "P traag {#}",
  "U{#} catches": "U{#} vangt",
  "best ≈ {#}×": "optimum ≈ {#}×",
  "caught by U{#}": "gevangen door U{#}",
  "critical: steady": "kritiek: constant",
  "dies away": "sterft uit",
  "f {#}": "f {#}",
  "factors: textbook set (Duderstadt & Hamilton) at {#} %; slider trends illustrative": "factoren: leerboekset (Duderstadt & Hamilton) bij {#} %; trends van de schuifjes illustratief",
  "fast fission": "snelle splijting",
  "fast leak": "snel lek",
  "grows": "groeit",
  "k = {#}": "k = {#}",
  "k = η {#} × f {#} × p {#} × ε {#} × P {#} × P {#}": "k = η {#} × f {#} × p {#} × ε {#} × P {#} × P {#}",
  "leaks out, fast": "lekt weg, snel",
  "leaks out, slow": "lekt weg, traag",
  "less water": "minder water",
  "more water": "meer water",
  "next generation: {#}": "volgende generatie: {#}",
  "next: {#}": "volgende: {#}",
  "p {#}": "p {#}",
  "slow leak": "traag lek",
  "slowing": "afremmen",
  "slowing down": "afremming",
  "textbook set (D&H); trends illustrative": "leerboekset (D&H); trends illustratief",
  "water, steel, boron": "water, staal, boor",
  "water, steel…": "water, staal…",
  "{#} % leak out": "{#} % lekt weg",
  "{#} split U{#}": "{#} splijten U{#}",
});
