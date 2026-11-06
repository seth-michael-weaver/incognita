/* Italian: burnup (Il burnup del combustibile) */
WT.L.ch.burnup = {
  num: "Lezione 1", title: "Il burnup del combustibile", short: "Burnup",
  html: `
<div class="step">
  <h3>Una pastiglia nel corso della sua vita</h3>
  <p>Ecco mille atomi di una pastiglia di combustibile nuova: 45 sono uranio-235, il resto uranio-238. Fai funzionare il reattore e guarda l'uranio-235 scindersi mentre compaiono atomi nuovi. Il <b>burnup</b> (grado di combustione) misura l'energia estratta, in gigawatt-giorno per tonnellata di uranio; i reattori ad acqua si fermano intorno a 45–55.</p>
  <div class="ctl"><label for="bu-d1">Giorni a piena potenza</label><input id="bu-d1" type="range" data-bind="d" data-instant min="0" max="1400" step="10" value="400"><output data-show="d" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Entra in gioco il plutonio</h3>
  <p>L'uranio-238 cattura neutroni e diventa plutonio-239, che a sua volta si scinde. Verso fine vita più della metà delle fissioni avviene nel plutonio; sull'intera vita del combustibile ne proviene circa un terzo dell'energia.</p>
  <div class="ctl"><label for="bu-d2">Giorni a piena potenza</label><input id="bu-d2" type="range" data-bind="d" data-instant min="0" max="1400" step="10" value="1000"><output data-show="d" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>I veleni si accumulano</h3>
  <p>Ogni fissione lascia due prodotti di fissione, e alcuni di essi assorbono neutroni. Con meno uranio-235 e più veleni, <i>k</i><sub>∞</sub> (nuove fissioni per fissione in un reticolo infinito di questo combustibile) cala lentamente, finché il combustibile non riesce più a sostenere da solo una reazione a catena.</p>
  <div class="ctl"><label for="bu-d3">Giorni a piena potenza</label><input id="bu-d3" type="range" data-bind="d" data-instant min="0" max="1400" step="10" value="700"><output data-show="d" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Boro e ricariche</h3>
  <p>Un nocciolo mescola combustibile nuovo, di mezza età e vecchio. Il combustibile nuovo ha troppa reattività, così il boro disciolto nell'acqua di raffreddamento assorbe l'eccesso e viene diluito a poco a poco. Quando arriva a zero, il terzo più vecchio esce ed entra combustibile nuovo.</p>
  <div class="ctl"><label for="bu-m">Mesi a piena potenza</label><input id="bu-m" type="range" data-bind="m" data-instant min="0" max="54" step="0.5" value="8"><output data-show="m" data-fmt="1"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "illustrative model": "modello illustrativo",
  // scenes 1-3: the pellet
  "{a} days · burnup {b} GWd/t": "{a} giorni · burnup {b} GWd/t",
  "uranium{#}": "uranio{#}",
  "plutonium{#}": "plutonio{#}",
  "other Pu": "altro Pu",
  "other plutonium": "altro plutonio",
  "fission products": "prodotti di fissione",
  "fission products (pairs)": "prodotti di fissione (coppie)",
  "{a} in {#}": "{a} su {#}",
  "uranium{#}: the remaining ~{#}–{#} %": "uranio{#}: il restante ~{#}–{#} %",
  "plutonium's share": "quota del plutonio",
  "fissions": "fissioni",
  "fissions now": "fissioni ora",
  "energy so far": "energia finora",
  "Pu": "Pu",
  "plutonium": "plutonio",
  "split": "fissionati",
  "each dot: {#} atom in {#}": "ogni punto: {#} atomo su {#}",
  "each dot: one atom in a thousand": "ogni punto: un atomo su mille",
  // scene 3: k-infinity
  "k = {#}": "k = {#}",
  "GWd/t →": "GWd/t →",
  "burnup (GWd/t) →": "burnup (GWd/t) →",
  "typical discharge": "scarico tipico",
  "typical discharge {#}–{#}": "scarico tipico {#}–{#}",
  "can't keep a chain going alone": "da solo non sostiene la catena",
  "this fuel alone can no longer keep a chain going": "da solo questo combustibile non sostiene più una reazione a catena",
  "k∞ reaches {#}": "k∞ arriva a {#}",
  "k∞ = {a}": "k∞ = {a}",
  "fission products catch {a} % of neutrons": "i prodotti di fissione catturano il {a} % dei neutroni",
  // scene 4: the core and boron
  "fresh": "nuovo",
  "{#} cycle": "{#} ciclo",
  "one cycle old": "usato per un ciclo",
  "{#} cycles": "{#} cicli",
  "two cycles old": "usato per due cicli",
  "reload": "ricarica",
  "boron (ppm)": "boro (ppm)",
  "boron in the water (ppm)": "boro nell'acqua (ppm)",
  "months →": "mesi →",
  "months at full power →": "mesi a piena potenza →",
  "{a} ppm": "{a} ppm",
  "cycle {a} months · fuel leaves at {b} GWd/t": "ciclo di {a} mesi · il combustibile esce a {b} GWd/t",
});
