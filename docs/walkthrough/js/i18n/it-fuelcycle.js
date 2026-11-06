/* Italian (Italiano): fuelcycle (Il ciclo del combustibile) */
WT.L.ch.fuelcycle = {
  num: "Lezione 1", title: "Il ciclo del combustibile", short: "Ciclo del combustibile",
  html: `
<div class="step">
  <h3>Estrarre l'uranio</h3>
  <p>Il minerale è quasi tutto roccia, e solo lo 0,7 % dell'uranio che contiene è uranio-235, quello che si fissiona facilmente.</p>
  <div class="ctl"><label for="fc-g">Tenore del minerale (% di uranio)</label><input id="fc-g" type="range" data-bind="lg" data-instant min="-1.7" max="1.3" step="0.01" value="-1"></div>
</div>
<div class="step">
  <h3>L'arricchimento è un bilancio di massa</h3>
  <p>Sotto forma di gas, l'uranio viene separato in un piccolo flusso più ricco di uranio-235, il combustibile, e in uno grande impoverito, le code.</p>
  <div class="ctl"><label for="fc-p">Arricchimento del combustibile (% U-235)</label><input id="fc-p" type="range" data-bind="xp" data-instant min="3" max="5" step="0.05" value="4.5"><output data-show="xp" data-fmt="2"></output></div>
  <div class="ctl"><label for="fc-t">Code (% U-235)</label><input id="fc-t" type="range" data-bind="xt" data-instant min="0.15" max="0.35" step="0.01" value="0.25"><output data-show="xt" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Pastiglie, barrette, elementi</h3>
  <p>L'uranio arricchito viene sinterizzato in pastiglie ceramiche, sigillato in barrette e raggruppato in elementi; <a href="#reactor">la prossima lezione</a> li segue dentro il nocciolo.</p>
  <div class="ctl"><label for="fc-f">Combustibile (tonnellate di uranio)</label><input id="fc-f" type="range" data-bind="ft" data-instant min="1" max="27" step="1" value="1"><output data-show="ft" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Anni nel nocciolo</h3>
  <p>In tre-sei anni qualche per cento degli atomi pesanti si fissiona, lasciando prodotti di fissione e un po' di plutonio nuovo (<a href="#burnup">burnup</a>).</p>
  <div class="ctl"><label for="fc-b">Burnup (GWd per tonnellata)</label><input id="fc-b" type="range" data-bind="bu" data-instant min="0" max="60" step="1" value="50"><output data-show="bu" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Raffreddare, poi due strade</h3>
  <p>Il combustibile esaurito si raffredda in piscina e poi in contenitori a secco; dopo viene sepolto in profondità così com'è, oppure ritrattato per riutilizzarne uranio e plutonio (<a href="#waste">combustibile esaurito</a>, <a href="#breeding">fertilizzazione</a>).</p>
  <div class="btns"><button class="btn ghost" data-act="frO" aria-pressed="true">Ciclo aperto</button> <button class="btn ghost" data-act="frR" aria-pressed="false">Ritrattamento</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "{#} are U{#}": "{#} sono U{#}",
  "{#} are uranium{#}": "{#} sono uranio{#}",
  "{#} t used": "{#} t usate",
  "{#} t used fuel": "{#} t di combustibile esaurito",
  "{#} U atoms": "{#} atomi di U",
  "{#} uranium atoms": "{#} atomi di uranio",
  "{a} % of the heavy atoms split": "{a} % degli atomi pesanti fissionati",
  "{a} kg waste → glass": "{a} kg di rifiuti → vetro",
  "{a} of one block": "{a} di un blocco",
  "{a} t of enriched uranium, as {b} t of uranium dioxide (UO₂) ceramic": "{a} t di uranio arricchito, sotto forma di {b} t di ceramica di biossido di uranio (UO₂)",
  "{a} t ore": "{a} t di minerale",
  "{a} t uranium = {b} t UO₂": "{a} t di uranio = {b} t di UO₂",
  "→ ≈ {a} t MOX fuel": "→ ≈ {a} t di combustibile MOX",
  "≈ {a} GWh of electricity": "≈ {a} GWh di elettricità",
  "≈ {a} SWU of separative work per kg of fuel": "≈ {a} SWU di lavoro separativo per kg di combustibile",
  "≈ a big reactor's yearly reload": "≈ la ricarica annuale di un grande reattore",
  "≥ {#} y": "≥ {#} anni",
  "≥ {#} years": "≥ {#} anni",
  "1 t fuel + {a} t tails": "1 t di combustibile + {a} t di code",
  "about what a {#} MWe reactor loads in a year": "più o meno ciò che carica in un anno un reattore da {#} MWe",
  "assemblies": "elementi",
  "assemblies of {#} rods": "elementi da {#} barrette",
  "at least {#} years": "almeno {#} anni",
  "cask": "contenitore",
  "Convert": "Conversione",
  "decades": "decenni",
  "decades in air": "decenni in aria",
  "deep repository, {#}–{#} m down": "deposito geologico, a {#}–{#} m di profondità",
  "Disposal": "Smaltimento",
  "dry cask": "contenitore a secco",
  "End": "Fine",
  "enrich": "arricchire",
  "Enrich": "Arricchimento",
  "enrichment plant (UF₆ gas)": "impianto di arricchimento (gas UF₆)",
  "Fabricate": "Fabbricazione",
  "feed/fuel = (xp − xt)/(xf − xt) = {a}": "alimentazione/combustibile = (xp − xt)/(xf − xt) = {a}",
  "fission prod.": "prod. di fissione",
  "fission products": "prodotti di fissione",
  "fission products + minor actinides {a} kg → ≈ 0.2 t glass": "prodotti di fissione + attinidi minori {a} kg → ≈ 0,2 t di vetro",
  "fuel 1 kg": "combustibile 1 kg",
  "grade {a} % U": "tenore {a} % U",
  "illustration": "illustrazione",
  "Mill": "Macinazione",
  "Mine": "Miniera",
  "minor actinides": "attinidi minori",
  "most mines: above {#} %": "quasi tutte le miniere: oltre {#} %",
  "natural / fuel = (xp − xt) / (xf − xt) = ({a} − {b}) / ({c} − {b}) = {d}": "naturale / combustibile = (xp − xt) / (xf − xt) = ({a} − {b}) / ({c} − {b}) = {d}",
  "natural U {a} kg": "U naturale {a} kg",
  "natural uranium {a} kg": "uranio naturale {a} kg",
  "of electricity from this tonne": "di elettricità da questa tonnellata",
  "once-through: the whole tonne is disposed of": "ciclo aperto: l'intera tonnellata va smaltita",
  "one tonne of fuel: each square is {#} kg": "una tonnellata di combustibile: ogni quadrato vale {#} kg",
  "one tonne: each square {#} kg": "una tonnellata: ogni quadrato {#} kg",
  "ore ≈ {a} t · block = 100 t": "minerale ≈ {a} t · blocco = 100 t",
  "ore for one tonne of fuel: ≈ {a} t  (each block 100 t)": "minerale per una tonnellata di combustibile: ≈ {a} t  (ogni blocco 100 t)",
  "pellets": "pastiglie",
  "pellets, {#} cm tall": "pastiglie alte {#} cm",
  "plutonium": "plutonio",
  "plutonium {a} kg": "plutonio {a} kg",
  "pool": "piscina",
  "Pool · cask": "Piscina · contenitore",
  "pool ≥ {#} years": "piscina ≥ {#} anni",
  "Reactor": "Reattore",
  "recycle": "riciclo",
  "repository": "deposito",
  "repository {#}–{#} m deep": "deposito a {#}–{#} m",
  "reprocess": "ritrattare",
  "reprocessing": "ritrattamento",
  "richest, Canada: up to {#} %": "le più ricche, Canada: fino al {#} %",
  "rods, {#} m": "barrette, {#} m",
  "rods, about {#} m long": "barrette lunghe circa {#} m",
  "separative work ≈ {a} SWU per kg of fuel · lower tails: less uranium, more work": "lavoro separativo ≈ {a} SWU per kg di combustibile · code più basse: meno uranio, più lavoro",
  "Store": "Deposito",
  "tails {a} kg": "code {a} kg",
  "the rest: uranium{#}": "il resto: uranio{#}",
  "the whole tonne": "l'intera tonnellata",
  "typical discharge {#}–{#}": "scarico tipico {#}–{#}",
  "U {a} t → re-enrich": "U {a} t → riarricchire",
  "uranium {a} t": "uranio {a} t",
  "uranium{#}": "uranio{#}",
  "uranium{#} (and {#})": "uranio{#} (e {#})",
});
