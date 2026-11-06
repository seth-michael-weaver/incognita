/* Danish: economy (Neutronbalancen) */
WT.L.ch.economy = {
  num: "Lektion 7", title: "Neutronbalancen", short: "Neutronbalance",
  html: `
<div class="step">
  <h3>Tusind neutroner</h3>
  <p>Følg 1000 hurtige neutroner gennem én generation. Nogle få giver ekstra fissioner, nogle slipper ud, nogle fanges undervejs, og resten spalter uran-235 og laver de næste tusind. Seks faktorer ganges sammen til <i>k</i> = <i>η f p ε P</i><sub>FNL</sub> <i>P</i><sub>TNL</sub>.</p>
</div>
<div class="step">
  <h3>Berigning</h3>
  <p>Mere uran-235 i brændslet betyder, at flere neutroner absorberes der, hvor de giver fission. Med naturligt uran (0,7 %) og almindeligt vand når <i>k</i> aldrig 1.</p>
  <div class="ctl"><label for="eco-e">Uran-235 (%)</label><input id="eco-e" type="range" data-bind="enr" min="0.7" max="5" step="0.1" value="3"><output data-show="enr" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Vand mellem stavene</h3>
  <p>For lidt vand, og de neutroner, der bremses, fanges af uran-238; for meget, og vandet selv absorberer dem. Der findes et bedste forhold, og vandreaktorer bygges lidt under det.</p>
  <div class="ctl"><label for="eco-m">Vand pr. brændsel (× typisk)</label><input id="eco-m" type="range" data-bind="m" min="0.3" max="4" step="0.05" value="1"><output data-show="m" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Størrelse</h3>
  <p>Neutroner født nær overfladen kan slippe ud. En lille kerne lækker for mange; en større holder på dem. Find den størrelse, hvor <i>k</i> krydser 1.</p>
  <div class="ctl"><label for="eco-s">Kernestørrelse (× typisk)</label><input id="eco-s" type="range" data-bind="s" min="0.3" max="2" step="0.05" value="0.6"><output data-show="s" data-fmt="2"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "P fast {#}": "P hurtig {#}",
  "P slow {#}": "P langsom {#}",
  "U{#} catches": "U{#} fanger",
  "best ≈ {#}×": "bedst ≈ {#}×",
  "caught by U{#}": "fanget af U{#}",
  "critical: steady": "kritisk: konstant",
  "dies away": "dør ud",
  "f {#}": "f {#}",
  "factors: textbook set (Duderstadt & Hamilton) at {#} %; slider trends illustrative": "faktorer: lærebogssæt (Duderstadt & Hamilton) ved {#} %; skydernes tendenser illustrative",
  "fast fission": "hurtig fission",
  "fast leak": "hurtig lækage",
  "grows": "vokser",
  "k = {#}": "k = {#}",
  "k = η {#} × f {#} × p {#} × ε {#} × P {#} × P {#}": "k = η {#} × f {#} × p {#} × ε {#} × P {#} × P {#}",
  "leaks out, fast": "slipper ud, hurtig",
  "leaks out, slow": "slipper ud, langsom",
  "less water": "mindre vand",
  "more water": "mere vand",
  "next generation: {#}": "næste generation: {#}",
  "next: {#}": "næste: {#}",
  "p {#}": "p {#}",
  "slow leak": "langsom lækage",
  "slowing": "bremsning",
  "slowing down": "nedbremsning",
  "textbook set (D&H); trends illustrative": "lærebogssæt (D&H); tendenser illustrative",
  "water, steel, boron": "vand, stål, bor",
  "water, steel…": "vand, stål…",
  "{#} % leak out": "{#} % slipper ud",
  "{#} split U{#}": "{#} spalter U{#}",
});
