/* French (Français): fuelcycle (Le cycle du combustible) */
WT.L.ch.fuelcycle = {
  num: "Leçon 1", title: "Le cycle du combustible", short: "Cycle du combustible",
  html: `
<div class="step">
  <h3>Extraire l'uranium</h3>
  <p>Le minerai est surtout de la roche, et seulement 0,7 % de l'uranium qu'il contient est de l'uranium 235, celui qui se fissionne facilement.</p>
  <div class="ctl"><label for="fc-g">Teneur du minerai (% d'uranium)</label><input id="fc-g" type="range" data-bind="lg" data-instant min="-1.7" max="1.3" step="0.01" value="-1"></div>
</div>
<div class="step">
  <h3>L'enrichissement est un bilan matière</h3>
  <p>Sous forme de gaz, l'uranium est séparé en un petit flux plus riche en uranium 235, le combustible, et un gros flux appauvri, les rejets.</p>
  <div class="ctl"><label for="fc-p">Enrichissement du combustible (% U-235)</label><input id="fc-p" type="range" data-bind="xp" data-instant min="3" max="5" step="0.05" value="4.5"><output data-show="xp" data-fmt="2"></output></div>
  <div class="ctl"><label for="fc-t">Rejets (% U-235)</label><input id="fc-t" type="range" data-bind="xt" data-instant min="0.15" max="0.35" step="0.01" value="0.25"><output data-show="xt" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Pastilles, crayons, assemblages</h3>
  <p>L'uranium enrichi est fritté en pastilles céramiques, scellé dans des crayons et regroupé en assemblages ; <a href="#reactor">la leçon suivante</a> les suit jusque dans le cœur.</p>
  <div class="ctl"><label for="fc-f">Combustible (tonnes d'uranium)</label><input id="fc-f" type="range" data-bind="ft" data-instant min="1" max="27" step="1" value="1"><output data-show="ft" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Des années dans le cœur</h3>
  <p>En trois à six ans, quelques pour cent des atomes lourds se fissionnent, laissant des produits de fission et un peu de plutonium nouveau (<a href="#burnup">taux de combustion</a>).</p>
  <div class="ctl"><label for="fc-b">Taux de combustion (GWj par tonne)</label><input id="fc-b" type="range" data-bind="bu" data-instant min="0" max="60" step="1" value="50"><output data-show="bu" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Refroidir, puis deux voies</h3>
  <p>Le combustible usé refroidit en piscine puis en châteaux secs ; ensuite il est soit enfoui en profondeur tel quel, soit retraité pour réutiliser son uranium et son plutonium (<a href="#waste">combustible usé</a>, <a href="#breeding">surgénération</a>).</p>
  <div class="btns"><button class="btn ghost" data-act="frO" aria-pressed="true">Cycle ouvert</button> <button class="btn ghost" data-act="frR" aria-pressed="false">Retraitement</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "{#} are U{#}": "{#} sont de l'U{#}",
  "{#} are uranium{#}": "{#} sont de l'uranium{#}",
  "{#} t used": "{#} t usées",
  "{#} t used fuel": "{#} t de combustible usé",
  "{#} U atoms": "{#} atomes d'U",
  "{#} uranium atoms": "{#} atomes d'uranium",
  "{a} % of the heavy atoms split": "{a} % des atomes lourds fissionnés",
  "{a} GWd/t": "{a} GWj/t",
  "{a} kg waste → glass": "{a} kg de déchets → verre",
  "{a} of one block": "{a} d'un bloc",
  "{a} t of enriched uranium, as {b} t of uranium dioxide (UO₂) ceramic": "{a} t d'uranium enrichi, sous forme de {b} t de céramique de dioxyde d'uranium (UO₂)",
  "{a} t ore": "{a} t de minerai",
  "{a} t uranium = {b} t UO₂": "{a} t d'uranium = {b} t d'UO₂",
  "→ ≈ {a} t MOX fuel": "→ ≈ {a} t de combustible MOX",
  "≈ {a} GWh of electricity": "≈ {a} GWh d'électricité",
  "≈ {a} SWU of separative work per kg of fuel": "≈ {a} UTS de travail de séparation par kg de combustible",
  "≈ a big reactor's yearly reload": "≈ la recharge annuelle d'un gros réacteur",
  "≥ {#} y": "≥ {#} ans",
  "≥ {#} years": "≥ {#} ans",
  "1 t fuel + {a} t tails": "1 t de combustible + {a} t de rejets",
  "about what a {#} MWe reactor loads in a year": "à peu près ce que charge par an un réacteur de {#} MWe",
  "assemblies": "assemblages",
  "assemblies of {#} rods": "assemblages de {#} crayons",
  "at least {#} years": "au moins {#} ans",
  "cask": "château",
  "Convert": "Conversion",
  "decades": "décennies",
  "decades in air": "des décennies à l'air",
  "deep repository, {#}–{#} m down": "stockage profond, à {#}–{#} m",
  "Disposal": "Stockage",
  "dry cask": "château sec",
  "End": "Fin",
  "enrich": "enrichir",
  "Enrich": "Enrichissement",
  "enrichment plant (UF₆ gas)": "usine d'enrichissement (gaz UF₆)",
  "Fabricate": "Fabrication",
  "feed/fuel = (xp − xt)/(xf − xt) = {a}": "alimentation/combustible = (xp − xt)/(xf − xt) = {a}",
  "fission prod.": "prod. de fission",
  "fission products": "produits de fission",
  "fission products + minor actinides {a} kg → ≈ 0.2 t glass": "produits de fission + actinides mineurs {a} kg → ≈ 0,2 t de verre",
  "fuel 1 kg": "combustible 1 kg",
  "grade {a} % U": "teneur {a} % U",
  "illustration": "illustration",
  "Mill": "Traitement",
  "Mine": "Mine",
  "minor actinides": "actinides mineurs",
  "most mines: above {#} %": "la plupart des mines : plus de {#} %",
  "natural / fuel = (xp − xt) / (xf − xt) = ({a} − {b}) / ({c} − {b}) = {d}": "naturel / combustible = (xp − xt) / (xf − xt) = ({a} − {b}) / ({c} − {b}) = {d}",
  "natural U {a} kg": "U naturel {a} kg",
  "natural uranium {a} kg": "uranium naturel {a} kg",
  "of electricity from this tonne": "d'électricité avec cette tonne",
  "once-through: the whole tonne is disposed of": "cycle ouvert : toute la tonne est stockée",
  "one tonne of fuel: each square is {#} kg": "une tonne de combustible : chaque carré vaut {#} kg",
  "one tonne: each square {#} kg": "une tonne : chaque carré {#} kg",
  "ore ≈ {a} t · block = 100 t": "minerai ≈ {a} t · bloc = 100 t",
  "ore for one tonne of fuel: ≈ {a} t  (each block 100 t)": "minerai pour une tonne de combustible : ≈ {a} t  (chaque bloc 100 t)",
  "pellets": "pastilles",
  "pellets, {#} cm tall": "pastilles de {#} cm de haut",
  "plutonium": "plutonium",
  "plutonium {a} kg": "plutonium {a} kg",
  "pool": "piscine",
  "Pool · cask": "Piscine · château",
  "pool ≥ {#} years": "piscine ≥ {#} ans",
  "Reactor": "Réacteur",
  "recycle": "recyclage",
  "repository": "stockage",
  "repository {#}–{#} m deep": "stockage à {#}–{#} m",
  "reprocess": "retraiter",
  "reprocessing": "retraitement",
  "richest, Canada: up to {#} %": "les plus riches, Canada : jusqu'à {#} %",
  "rods, {#} m": "crayons, {#} m",
  "rods, about {#} m long": "crayons d'environ {#} m",
  "separative work ≈ {a} SWU per kg of fuel · lower tails: less uranium, more work": "travail de séparation ≈ {a} UTS par kg de combustible · rejets plus bas : moins d'uranium, plus de travail",
  "Store": "Entreposage",
  "tails {a} kg": "rejets {a} kg",
  "the rest: uranium{#}": "le reste : uranium{#}",
  "the whole tonne": "toute la tonne",
  "typical discharge {#}–{#}": "déchargement typique {#}–{#}",
  "U {a} t → re-enrich": "U {a} t → réenrichir",
  "uranium {a} t": "uranium {a} t",
  "uranium{#}": "uranium{#}",
  "uranium{#} (and {#})": "uranium{#} (et {#})",
});
