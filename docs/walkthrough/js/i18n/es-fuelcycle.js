/* Spanish (Español): fuelcycle (El ciclo del combustible) */
WT.L.ch.fuelcycle = {
  num: "Lección 1", title: "El ciclo del combustible", short: "Ciclo del combustible",
  html: `
<div class="step">
  <h3>Extraer el uranio</h3>
  <p>El mineral es casi todo roca, y solo el 0,7 % del uranio que contiene es uranio-235, el que se fisiona con facilidad.</p>
  <div class="ctl"><label for="fc-g">Ley del mineral (% de uranio)</label><input id="fc-g" type="range" data-bind="lg" data-instant min="-1.7" max="1.3" step="0.01" value="-1"></div>
</div>
<div class="step">
  <h3>El enriquecimiento es un balance de masas</h3>
  <p>En forma de gas, el uranio se separa en una pequeña corriente más rica en uranio-235, el combustible, y una grande empobrecida, las colas.</p>
  <div class="ctl"><label for="fc-p">Enriquecimiento del combustible (% U-235)</label><input id="fc-p" type="range" data-bind="xp" data-instant min="3" max="5" step="0.05" value="4.5"><output data-show="xp" data-fmt="2"></output></div>
  <div class="ctl"><label for="fc-t">Colas (% U-235)</label><input id="fc-t" type="range" data-bind="xt" data-instant min="0.15" max="0.35" step="0.01" value="0.25"><output data-show="xt" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Pastillas, varillas, elementos</h3>
  <p>El uranio enriquecido se sinteriza en pastillas cerámicas, se sella en varillas y se agrupa en elementos; <a href="#reactor">la siguiente lección</a> los sigue hasta el núcleo.</p>
  <div class="ctl"><label for="fc-f">Combustible (toneladas de uranio)</label><input id="fc-f" type="range" data-bind="ft" data-instant min="1" max="27" step="1" value="1"><output data-show="ft" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Años en el núcleo</h3>
  <p>En tres a seis años se fisionan unos pocos por ciento de los átomos pesados, dejando productos de fisión y algo de plutonio nuevo (<a href="#burnup">quemado</a>).</p>
  <div class="ctl"><label for="fc-b">Quemado (GWd por tonelada)</label><input id="fc-b" type="range" data-bind="bu" data-instant min="0" max="60" step="1" value="50"><output data-show="bu" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Enfriar y luego dos caminos</h3>
  <p>El combustible gastado se enfría en una piscina y después en contenedores secos; luego se entierra a gran profundidad tal cual, o se reprocesa para volver a usar su uranio y su plutonio (<a href="#waste">combustible gastado</a>, <a href="#breeding">reproducción</a>).</p>
  <div class="btns"><button class="btn ghost" data-act="frO" aria-pressed="true">Ciclo abierto</button> <button class="btn ghost" data-act="frR" aria-pressed="false">Reprocesar</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "{#} are U{#}": "{#} son U{#}",
  "{#} are uranium{#}": "{#} son uranio{#}",
  "{#} t used": "{#} t usadas",
  "{#} t used fuel": "{#} t de combustible gastado",
  "{#} U atoms": "{#} átomos de U",
  "{#} uranium atoms": "{#} átomos de uranio",
  "{a} % of the heavy atoms split": "{a} % de los átomos pesados fisionados",
  "{a} kg waste → glass": "{a} kg de residuos → vidrio",
  "{a} of one block": "{a} de un bloque",
  "{a} t of enriched uranium, as {b} t of uranium dioxide (UO₂) ceramic": "{a} t de uranio enriquecido, como {b} t de cerámica de dióxido de uranio (UO₂)",
  "{a} t ore": "{a} t de mineral",
  "{a} t uranium = {b} t UO₂": "{a} t de uranio = {b} t de UO₂",
  "→ ≈ {a} t MOX fuel": "→ ≈ {a} t de combustible MOX",
  "≈ {a} GWh of electricity": "≈ {a} GWh de electricidad",
  "≈ {a} SWU of separative work per kg of fuel": "≈ {a} UTS de trabajo de separación por kg de combustible",
  "≈ a big reactor's yearly reload": "≈ la recarga anual de un reactor grande",
  "≥ {#} y": "≥ {#} años",
  "≥ {#} years": "≥ {#} años",
  "1 t fuel + {a} t tails": "1 t de combustible + {a} t de colas",
  "about what a {#} MWe reactor loads in a year": "más o menos lo que carga al año un reactor de {#} MWe",
  "assemblies": "elementos",
  "assemblies of {#} rods": "elementos de {#} varillas",
  "at least {#} years": "al menos {#} años",
  "cask": "contenedor",
  "Convert": "Conversión",
  "decades": "décadas",
  "decades in air": "décadas al aire",
  "deep repository, {#}–{#} m down": "almacén geológico profundo, a {#}–{#} m",
  "Disposal": "Almacén final",
  "dry cask": "contenedor seco",
  "End": "Final",
  "enrich": "enriquecer",
  "Enrich": "Enriquecer",
  "enrichment plant (UF₆ gas)": "planta de enriquecimiento (gas UF₆)",
  "Fabricate": "Fabricación",
  "feed/fuel = (xp − xt)/(xf − xt) = {a}": "alimentación/combustible = (xp − xt)/(xf − xt) = {a}",
  "fission prod.": "prod. de fisión",
  "fission products": "productos de fisión",
  "fission products + minor actinides {a} kg → ≈ 0.2 t glass": "productos de fisión + actínidos minoritarios {a} kg → ≈ 0,2 t de vidrio",
  "fuel 1 kg": "combustible 1 kg",
  "grade {a} % U": "ley {a} % U",
  "illustration": "ilustración",
  "Mill": "Tratamiento",
  "Mine": "Mina",
  "minor actinides": "actínidos minoritarios",
  "most mines: above {#} %": "la mayoría de las minas: más del {#} %",
  "natural / fuel = (xp − xt) / (xf − xt) = ({a} − {b}) / ({c} − {b}) = {d}": "natural / combustible = (xp − xt) / (xf − xt) = ({a} − {b}) / ({c} − {b}) = {d}",
  "natural U {a} kg": "U natural {a} kg",
  "natural uranium {a} kg": "uranio natural {a} kg",
  "of electricity from this tonne": "de electricidad con esta tonelada",
  "once-through: the whole tonne is disposed of": "ciclo abierto: toda la tonelada va al almacén final",
  "one tonne of fuel: each square is {#} kg": "una tonelada de combustible: cada cuadrado son {#} kg",
  "one tonne: each square {#} kg": "una tonelada: cada cuadrado {#} kg",
  "ore ≈ {a} t · block = 100 t": "mineral ≈ {a} t · bloque = 100 t",
  "ore for one tonne of fuel: ≈ {a} t  (each block 100 t)": "mineral para una tonelada de combustible: ≈ {a} t  (cada bloque 100 t)",
  "pellets": "pastillas",
  "pellets, {#} cm tall": "pastillas de {#} cm de alto",
  "plutonium": "plutonio",
  "plutonium {a} kg": "plutonio {a} kg",
  "pool": "piscina",
  "Pool · cask": "Piscina · contenedor",
  "pool ≥ {#} years": "piscina ≥ {#} años",
  "Reactor": "Reactor",
  "recycle": "reciclar",
  "repository": "almacén final",
  "repository {#}–{#} m deep": "almacén final a {#}–{#} m",
  "reprocess": "reprocesar",
  "reprocessing": "reprocesado",
  "richest, Canada: up to {#} %": "las más ricas, Canadá: hasta el {#} %",
  "rods, {#} m": "varillas, {#} m",
  "rods, about {#} m long": "varillas de unos {#} m",
  "separative work ≈ {a} SWU per kg of fuel · lower tails: less uranium, more work": "trabajo de separación ≈ {a} UTS por kg de combustible · colas más bajas: menos uranio, más trabajo",
  "Store": "Almacén",
  "tails {a} kg": "colas {a} kg",
  "the rest: uranium{#}": "el resto: uranio{#}",
  "the whole tonne": "toda la tonelada",
  "typical discharge {#}–{#}": "descarga típica {#}–{#}",
  "U {a} t → re-enrich": "U {a} t → reenriquecer",
  "uranium {a} t": "uranio {a} t",
  "uranium{#}": "uranio{#}",
  "uranium{#} (and {#})": "uranio{#} (y {#})",
});
