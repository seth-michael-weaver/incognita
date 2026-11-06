/* Danish (Dansk): fuelcycle (Brændselskredsløbet) */
WT.L.ch.fuelcycle = {
  num: "Lektion 1", title: "Brændselskredsløbet", short: "Brændselskredsløb",
  html: `
<div class="step">
  <h3>Uran graves op</h3>
  <p>Malm er mest sten, og kun 0,7 % af uranet i den er uran-235, den slags der let spaltes.</p>
  <div class="ctl"><label for="fc-g">Malmindhold (% uran)</label><input id="fc-g" type="range" data-bind="lg" data-instant min="-1.7" max="1.3" step="0.01" value="-1"></div>
</div>
<div class="step">
  <h3>Berigning er en massebalance</h3>
  <p>Som gas deles uranet i en lille strøm, der er rigere på uran-235, brændslet, og en stor udtyndet, tails.</p>
  <div class="ctl"><label for="fc-p">Brændslets berigning (% U-235)</label><input id="fc-p" type="range" data-bind="xp" data-instant min="3" max="5" step="0.05" value="4.5"><output data-show="xp" data-fmt="2"></output></div>
  <div class="ctl"><label for="fc-t">Tails (% U-235)</label><input id="fc-t" type="range" data-bind="xt" data-instant min="0.15" max="0.35" step="0.01" value="0.25"><output data-show="xt" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Piller, stave, elementer</h3>
  <p>Det berigede uran brændes til keramiske piller, forsegles i stave og samles i elementer; <a href="#reactor">næste lektion</a> følger dem ind i kernen.</p>
  <div class="ctl"><label for="fc-f">Brændsel (ton uran)</label><input id="fc-f" type="range" data-bind="ft" data-instant min="1" max="27" step="1" value="1"><output data-show="ft" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>År i kernen</h3>
  <p>Over tre til seks år spaltes nogle få procent af de tunge atomer, og der efterlades fissionsprodukter og lidt nyt plutonium (<a href="#burnup">udbrænding</a>).</p>
  <div class="ctl"><label for="fc-b">Udbrænding (GWd pr. ton)</label><input id="fc-b" type="range" data-bind="bu" data-instant min="0" max="60" step="1" value="50"><output data-show="bu" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Afkøling, derefter to veje</h3>
  <p>Brugt brændsel køler af i et bassin og derefter i tørre beholdere; bagefter bliver det enten begravet dybt, som det er, eller oparbejdet, så uranet og plutoniummet bruges igen (<a href="#waste">brugt brændsel</a>, <a href="#breeding">avl</a>).</p>
  <div class="btns"><button class="btn ghost" data-act="frO" aria-pressed="true">Direkte deponering</button> <button class="btn ghost" data-act="frR" aria-pressed="false">Oparbejdning</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "{#} are U{#}": "{#} er U{#}",
  "{#} are uranium{#}": "{#} er uran{#}",
  "{#} t used": "{#} t brugt",
  "{#} t used fuel": "{#} t brugt brændsel",
  "{#} U atoms": "{#} U-atomer",
  "{#} uranium atoms": "{#} uranatomer",
  "{a} % of the heavy atoms split": "{a} % af de tunge atomer spaltet",
  "{a} kg waste → glass": "{a} kg affald → glas",
  "{a} of one block": "{a} af én blok",
  "{a} t of enriched uranium, as {b} t of uranium dioxide (UO₂) ceramic": "{a} t beriget uran, som {b} t keramisk urandioxid (UO₂)",
  "{a} t ore": "{a} t malm",
  "{a} t uranium = {b} t UO₂": "{a} t uran = {b} t UO₂",
  "→ ≈ {a} t MOX fuel": "→ ≈ {a} t MOX-brændsel",
  "≈ {a} GWh of electricity": "≈ {a} GWh elektricitet",
  "≈ {a} SWU of separative work per kg of fuel": "≈ {a} SWU separationsarbejde pr. kg brændsel",
  "≈ a big reactor's yearly reload": "≈ en stor reaktors årlige genopladning",
  "≥ {#} y": "≥ {#} år",
  "≥ {#} years": "≥ {#} år",
  "1 t fuel + {a} t tails": "1 t brændsel + {a} t tails",
  "about what a {#} MWe reactor loads in a year": "omtrent hvad en reaktor på {#} MWe lader på et år",
  "assemblies": "elementer",
  "assemblies of {#} rods": "elementer med {#} stave",
  "at least {#} years": "mindst {#} år",
  "cask": "beholder",
  "Convert": "Konvertering",
  "decades": "årtier",
  "decades in air": "årtier i luft",
  "deep repository, {#}–{#} m down": "dybt slutdepot, {#}–{#} m nede",
  "Disposal": "Deponering",
  "dry cask": "tør beholder",
  "End": "Slut",
  "enrich": "berig",
  "Enrich": "Berigning",
  "enrichment plant (UF₆ gas)": "berigningsanlæg (UF₆-gas)",
  "Fabricate": "Fremstilling",
  "feed/fuel = (xp − xt)/(xf − xt) = {a}": "fødning/brændsel = (xp − xt)/(xf − xt) = {a}",
  "fission prod.": "fissionsprod.",
  "fission products": "fissionsprodukter",
  "fission products + minor actinides {a} kg → ≈ 0.2 t glass": "fissionsprodukter + mindre actinider {a} kg → ≈ 0,2 t glas",
  "fuel 1 kg": "brændsel 1 kg",
  "grade {a} % U": "indhold {a} % U",
  "illustration": "illustration",
  "Mill": "Udvinding",
  "Mine": "Mine",
  "minor actinides": "mindre actinider",
  "most mines: above {#} %": "de fleste miner: over {#} %",
  "natural / fuel = (xp − xt) / (xf − xt) = ({a} − {b}) / ({c} − {b}) = {d}": "naturligt / brændsel = (xp − xt) / (xf − xt) = ({a} − {b}) / ({c} − {b}) = {d}",
  "natural U {a} kg": "naturligt U {a} kg",
  "natural uranium {a} kg": "naturligt uran {a} kg",
  "of electricity from this tonne": "elektricitet fra dette ton",
  "once-through: the whole tonne is disposed of": "direkte deponering: hele tonnet deponeres",
  "one tonne of fuel: each square is {#} kg": "ét ton brændsel: hver firkant er {#} kg",
  "one tonne: each square {#} kg": "ét ton: hver firkant {#} kg",
  "ore ≈ {a} t · block = 100 t": "malm ≈ {a} t · blok = 100 t",
  "ore for one tonne of fuel: ≈ {a} t  (each block 100 t)": "malm til ét ton brændsel: ≈ {a} t  (hver blok 100 t)",
  "pellets": "piller",
  "pellets, {#} cm tall": "piller, {#} cm høje",
  "plutonium": "plutonium",
  "plutonium {a} kg": "plutonium {a} kg",
  "pool": "bassin",
  "Pool · cask": "Bassin · beholder",
  "pool ≥ {#} years": "bassin ≥ {#} år",
  "Reactor": "Reaktor",
  "recycle": "genbrug",
  "repository": "slutdepot",
  "repository {#}–{#} m deep": "slutdepot {#}–{#} m dybt",
  "reprocess": "oparbejd",
  "reprocessing": "oparbejdning",
  "richest, Canada: up to {#} %": "rigeste, Canada: op til {#} %",
  "rods, {#} m": "stave, {#} m",
  "rods, about {#} m long": "stave, omkring {#} m lange",
  "separative work ≈ {a} SWU per kg of fuel · lower tails: less uranium, more work": "separationsarbejde ≈ {a} SWU pr. kg brændsel · lavere tails: mindre uran, mere arbejde",
  "Store": "Lager",
  "tails {a} kg": "tails {a} kg",
  "the rest: uranium{#}": "resten: uran{#}",
  "the whole tonne": "hele tonnet",
  "typical discharge {#}–{#}": "typisk udtagning {#}–{#}",
  "U {a} t → re-enrich": "U {a} t → berig igen",
  "uranium {a} t": "uran {a} t",
  "uranium{#}": "uran{#}",
  "uranium{#} (and {#})": "uran{#} (og {#})",
});
