/* Spanish: burnup (El quemado del combustible) */
WT.L.ch.burnup = {
  num: "Lección 1", title: "El quemado del combustible", short: "Quemado",
  html: `
<div class="step">
  <h3>Una pastilla a lo largo de su vida</h3>
  <p>Aquí hay mil átomos de una pastilla de combustible nueva: 45 son de uranio-235 y el resto de uranio-238. Pon en marcha el reactor y mira cómo se fisiona el uranio-235 mientras aparecen átomos nuevos. El <b>grado de quemado</b> cuenta la energía extraída, en gigavatios-día por tonelada de uranio; los reactores de agua se detienen hacia 45–55.</p>
  <div class="ctl"><label for="bu-d1">Días a plena potencia</label><input id="bu-d1" type="range" data-bind="d" data-instant min="0" max="1400" step="10" value="400"><output data-show="d" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Entra en juego el plutonio</h3>
  <p>El uranio-238 captura neutrones y se convierte en plutonio-239, que también se fisiona. Al final de la vida del combustible, más de la mitad de las fisiones ocurren en el plutonio; a lo largo de toda su vida, cerca de un tercio de la energía procede de él.</p>
  <div class="ctl"><label for="bu-d2">Días a plena potencia</label><input id="bu-d2" type="range" data-bind="d" data-instant min="0" max="1400" step="10" value="1000"><output data-show="d" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Se acumulan los venenos</h3>
  <p>Cada fisión deja dos productos de fisión, y algunos absorben neutrones. Con menos uranio-235 y más veneno, <i>k</i><sub>∞</sub> (fisiones nuevas por fisión en una red infinita de este combustible) va bajando hasta que el combustible ya no puede mantener solo una reacción en cadena.</p>
  <div class="ctl"><label for="bu-d3">Días a plena potencia</label><input id="bu-d3" type="range" data-bind="d" data-instant min="0" max="1400" step="10" value="700"><output data-show="d" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Boro y recargas</h3>
  <p>Un núcleo mezcla combustible nuevo, de media vida y viejo. El combustible nuevo tiene demasiada reactividad, así que boro disuelto en el agua de refrigeración absorbe el exceso y se va diluyendo poco a poco. Cuando llega a cero, sale el tercio más viejo y entra combustible nuevo.</p>
  <div class="ctl"><label for="bu-m">Meses a plena potencia</label><input id="bu-m" type="range" data-bind="m" data-instant min="0" max="54" step="0.5" value="8"><output data-show="m" data-fmt="1"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "illustrative model": "modelo ilustrativo",
  // scenes 1-3: the pellet
  "{a} days · burnup {b} GWd/t": "{a} días · quemado {b} GWd/t",
  "uranium{#}": "uranio{#}",
  "plutonium{#}": "plutonio{#}",
  "other Pu": "otro Pu",
  "other plutonium": "otro plutonio",
  "fission products": "productos de fisión",
  "fission products (pairs)": "productos de fisión (pares)",
  "{a} in {#}": "{a} de {#}",
  "uranium{#}: the remaining ~{#}–{#} %": "uranio{#}: el resto, ~{#}–{#} %",
  "plutonium's share": "parte del plutonio",
  "fissions": "fisiones",
  "fissions now": "fisiones ahora",
  "energy so far": "energía acumulada",
  "Pu": "Pu",
  "plutonium": "plutonio",
  "split": "fisionados",
  "each dot: {#} atom in {#}": "cada punto: {#} átomo de {#}",
  "each dot: one atom in a thousand": "cada punto: un átomo de cada mil",
  // scene 3: k-infinity
  "k = {#}": "k = {#}",
  "GWd/t →": "GWd/t →",
  "burnup (GWd/t) →": "quemado (GWd/t) →",
  "typical discharge": "descarga típica",
  "typical discharge {#}–{#}": "descarga típica {#}–{#}",
  "can't keep a chain going alone": "ya no mantiene solo la cadena",
  "this fuel alone can no longer keep a chain going": "este combustible ya no puede mantener solo una reacción en cadena",
  "k∞ reaches {#}": "k∞ llega a {#}",
  "k∞ = {a}": "k∞ = {a}",
  "fission products catch {a} % of neutrons": "los productos de fisión capturan el {a} % de los neutrones",
  // scene 4: the core and boron
  "fresh": "nuevo",
  "{#} cycle": "{#} ciclo",
  "one cycle old": "un ciclo de uso",
  "{#} cycles": "{#} ciclos",
  "two cycles old": "dos ciclos de uso",
  "reload": "recarga",
  "boron (ppm)": "boro (ppm)",
  "boron in the water (ppm)": "boro en el agua (ppm)",
  "months →": "meses →",
  "months at full power →": "meses a plena potencia →",
  "{a} ppm": "{a} ppm",
  "cycle {a} months · fuel leaves at {b} GWd/t": "ciclo de {a} meses · el combustible sale a {b} GWd/t",
});
