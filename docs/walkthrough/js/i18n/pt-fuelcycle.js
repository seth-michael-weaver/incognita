/* Portuguese (Português): fuelcycle (O ciclo do combustível) */
WT.L.ch.fuelcycle = {
  num: "Lição 1", title: "O ciclo do combustível", short: "Ciclo do combustível",
  html: `
<div class="step">
  <h3>Extrair o urânio</h3>
  <p>O minério é sobretudo rocha, e apenas 0,7 % do urânio que contém é urânio-235, o tipo que se cinde facilmente.</p>
  <div class="ctl"><label for="fc-g">Teor do minério (% de urânio)</label><input id="fc-g" type="range" data-bind="lg" data-instant min="-1.7" max="1.3" step="0.01" value="-1"></div>
</div>
<div class="step">
  <h3>O enriquecimento é um balanço de massa</h3>
  <p>Em forma de gás, o urânio é separado num pequeno fluxo mais rico em urânio-235, o combustível, e num grande fluxo empobrecido, os rejeitados.</p>
  <div class="ctl"><label for="fc-p">Enriquecimento do combustível (% U-235)</label><input id="fc-p" type="range" data-bind="xp" data-instant min="3" max="5" step="0.05" value="4.5"><output data-show="xp" data-fmt="2"></output></div>
  <div class="ctl"><label for="fc-t">Rejeitados (% U-235)</label><input id="fc-t" type="range" data-bind="xt" data-instant min="0.15" max="0.35" step="0.01" value="0.25"><output data-show="xt" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Pastilhas, varetas, elementos</h3>
  <p>O urânio enriquecido é sinterizado em pastilhas cerâmicas, selado em varetas e agrupado em elementos; <a href="#reactor">a próxima lição</a> segue-os até ao núcleo.</p>
  <div class="ctl"><label for="fc-f">Combustível (toneladas de urânio)</label><input id="fc-f" type="range" data-bind="ft" data-instant min="1" max="27" step="1" value="1"><output data-show="ft" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Anos no núcleo</h3>
  <p>Ao longo de três a seis anos, alguns por cento dos átomos pesados cindem-se, deixando produtos de fissão e algum plutónio novo (<a href="#burnup">taxa de queima</a>).</p>
  <div class="ctl"><label for="fc-b">Taxa de queima (GWd por tonelada)</label><input id="fc-b" type="range" data-bind="bu" data-instant min="0" max="60" step="1" value="50"><output data-show="bu" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Arrefecer, depois dois caminhos</h3>
  <p>O combustível irradiado arrefece numa piscina e depois em contentores secos; a seguir é enterrado a grande profundidade tal como está, ou reprocessado para que o urânio e o plutónio voltem a ser usados (<a href="#waste">combustível irradiado</a>, <a href="#breeding">regeneração</a>).</p>
  <div class="btns"><button class="btn ghost" data-act="frO" aria-pressed="true">Ciclo aberto</button> <button class="btn ghost" data-act="frR" aria-pressed="false">Reprocessar</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "{#} are U{#}": "{#} são U{#}",
  "{#} are uranium{#}": "{#} são urânio{#}",
  "{#} t used": "{#} t usadas",
  "{#} t used fuel": "{#} t de combustível irradiado",
  "{#} U atoms": "{#} átomos de U",
  "{#} uranium atoms": "{#} átomos de urânio",
  "{a} % of the heavy atoms split": "{a} % dos átomos pesados cindidos",
  "{a} kg waste → glass": "{a} kg de resíduos → vidro",
  "{a} of one block": "{a} de um bloco",
  "{a} t of enriched uranium, as {b} t of uranium dioxide (UO₂) ceramic": "{a} t de urânio enriquecido, como {b} t de cerâmica de dióxido de urânio (UO₂)",
  "{a} t ore": "{a} t de minério",
  "{a} t uranium = {b} t UO₂": "{a} t de urânio = {b} t de UO₂",
  "→ ≈ {a} t MOX fuel": "→ ≈ {a} t de combustível MOX",
  "≈ {a} GWh of electricity": "≈ {a} GWh de eletricidade",
  "≈ {a} SWU of separative work per kg of fuel": "≈ {a} UTS de trabalho de separação por kg de combustível",
  "≈ a big reactor's yearly reload": "≈ a recarga anual de um reator grande",
  "≥ {#} y": "≥ {#} anos",
  "≥ {#} years": "≥ {#} anos",
  "1 t fuel + {a} t tails": "1 t de combustível + {a} t de rejeitados",
  "about what a {#} MWe reactor loads in a year": "cerca do que um reator de {#} MWe carrega por ano",
  "assemblies": "elementos",
  "assemblies of {#} rods": "elementos de {#} varetas",
  "at least {#} years": "pelo menos {#} anos",
  "cask": "contentor",
  "Convert": "Conversão",
  "decades": "décadas",
  "decades in air": "décadas ao ar",
  "deep repository, {#}–{#} m down": "repositório profundo, a {#}–{#} m",
  "Disposal": "Deposição",
  "dry cask": "contentor seco",
  "End": "Fim",
  "enrich": "enriquecer",
  "Enrich": "Enriquecer",
  "enrichment plant (UF₆ gas)": "fábrica de enriquecimento (gás UF₆)",
  "Fabricate": "Fabrico",
  "feed/fuel = (xp − xt)/(xf − xt) = {a}": "alimentação/combustível = (xp − xt)/(xf − xt) = {a}",
  "fission prod.": "prod. de fissão",
  "fission products": "produtos de fissão",
  "fission products + minor actinides {a} kg → ≈ 0.2 t glass": "produtos de fissão + actinídeos menores {a} kg → ≈ 0,2 t de vidro",
  "fuel 1 kg": "combustível 1 kg",
  "grade {a} % U": "teor {a} % U",
  "illustration": "ilustração",
  "Mill": "Tratamento",
  "Mine": "Mina",
  "minor actinides": "actinídeos menores",
  "most mines: above {#} %": "a maioria das minas: acima de {#} %",
  "natural / fuel = (xp − xt) / (xf − xt) = ({a} − {b}) / ({c} − {b}) = {d}": "natural / combustível = (xp − xt) / (xf − xt) = ({a} − {b}) / ({c} − {b}) = {d}",
  "natural U {a} kg": "U natural {a} kg",
  "natural uranium {a} kg": "urânio natural {a} kg",
  "of electricity from this tonne": "de eletricidade desta tonelada",
  "once-through: the whole tonne is disposed of": "ciclo aberto: a tonelada inteira vai para deposição",
  "one tonne of fuel: each square is {#} kg": "uma tonelada de combustível: cada quadrado são {#} kg",
  "one tonne: each square {#} kg": "uma tonelada: cada quadrado {#} kg",
  "ore ≈ {a} t · block = 100 t": "minério ≈ {a} t · bloco = 100 t",
  "ore for one tonne of fuel: ≈ {a} t  (each block 100 t)": "minério para uma tonelada de combustível: ≈ {a} t  (cada bloco 100 t)",
  "pellets": "pastilhas",
  "pellets, {#} cm tall": "pastilhas de {#} cm de altura",
  "plutonium": "plutónio",
  "plutonium {a} kg": "plutónio {a} kg",
  "pool": "piscina",
  "Pool · cask": "Piscina · contentor",
  "pool ≥ {#} years": "piscina ≥ {#} anos",
  "Reactor": "Reator",
  "recycle": "reciclar",
  "repository": "repositório",
  "repository {#}–{#} m deep": "repositório a {#}–{#} m",
  "reprocess": "reprocessar",
  "reprocessing": "reprocessamento",
  "richest, Canada: up to {#} %": "as mais ricas, Canadá: até {#} %",
  "rods, {#} m": "varetas, {#} m",
  "rods, about {#} m long": "varetas com cerca de {#} m",
  "separative work ≈ {a} SWU per kg of fuel · lower tails: less uranium, more work": "trabalho de separação ≈ {a} UTS por kg de combustível · rejeitados mais baixos: menos urânio, mais trabalho",
  "Store": "Armazém",
  "tails {a} kg": "rejeitados {a} kg",
  "the rest: uranium{#}": "o resto: urânio{#}",
  "the whole tonne": "a tonelada inteira",
  "typical discharge {#}–{#}": "descarga típica {#}–{#}",
  "U {a} t → re-enrich": "U {a} t → reenriquecer",
  "uranium {a} t": "urânio {a} t",
  "uranium{#}": "urânio{#}",
  "uranium{#} (and {#})": "urânio{#} (e {#})",
});
