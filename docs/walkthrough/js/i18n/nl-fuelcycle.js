/* Dutch (Nederlands): fuelcycle (De splijtstofcyclus) */
WT.L.ch.fuelcycle = {
  num: "Les 1", title: "De splijtstofcyclus", short: "Splijtstofcyclus",
  html: `
<div class="step">
  <h3>Uranium delven</h3>
  <p>Erts is grotendeels gesteente, en maar 0,7 % van het uranium erin is uranium-235, de soort die makkelijk splijt.</p>
  <div class="ctl"><label for="fc-g">Ertsgehalte (% uranium)</label><input id="fc-g" type="range" data-bind="lg" data-instant min="-1.7" max="1.3" step="0.01" value="-1"></div>
</div>
<div class="step">
  <h3>Verrijking is een massabalans</h3>
  <p>Als gas wordt het uranium gesplitst in een kleine stroom die rijker is aan uranium-235, de brandstof, en een grote verarmde, de tails.</p>
  <div class="ctl"><label for="fc-p">Verrijking van de brandstof (% U-235)</label><input id="fc-p" type="range" data-bind="xp" data-instant min="3" max="5" step="0.05" value="4.5"><output data-show="xp" data-fmt="2"></output></div>
  <div class="ctl"><label for="fc-t">Tails (% U-235)</label><input id="fc-t" type="range" data-bind="xt" data-instant min="0.15" max="0.35" step="0.01" value="0.25"><output data-show="xt" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Tabletten, staven, elementen</h3>
  <p>Het verrijkte uranium wordt tot keramische tabletten gebakken, in staven ingesloten en tot elementen gebundeld; <a href="#reactor">de volgende les</a> volgt ze de kern in.</p>
  <div class="ctl"><label for="fc-f">Brandstof (ton uranium)</label><input id="fc-f" type="range" data-bind="ft" data-instant min="1" max="27" step="1" value="1"><output data-show="ft" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Jaren in de kern</h3>
  <p>In drie tot zes jaar splijten een paar procent van de zware atomen; er blijven splijtingsproducten en wat nieuw plutonium achter (<a href="#burnup">opbrand</a>).</p>
  <div class="ctl"><label for="fc-b">Opbrand (GWd per ton)</label><input id="fc-b" type="range" data-bind="bu" data-instant min="0" max="60" step="1" value="50"><output data-show="bu" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Afkoelen, dan twee routes</h3>
  <p>Gebruikte brandstof koelt af in een bassin en daarna in droge containers; vervolgens wordt hij ofwel zoals hij is diep begraven, ofwel opgewerkt zodat uranium en plutonium opnieuw worden gebruikt (<a href="#waste">gebruikte brandstof</a>, <a href="#breeding">kweken</a>).</p>
  <div class="btns"><button class="btn ghost" data-act="frO" aria-pressed="true">Directe berging</button> <button class="btn ghost" data-act="frR" aria-pressed="false">Opwerken</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "{#} are U{#}": "{#} zijn U{#}",
  "{#} are uranium{#}": "{#} zijn uranium{#}",
  "{#} t used": "{#} t gebruikt",
  "{#} t used fuel": "{#} t gebruikte brandstof",
  "{#} U atoms": "{#} U-atomen",
  "{#} uranium atoms": "{#} uraniumatomen",
  "{a} % of the heavy atoms split": "{a} % van de zware atomen gespleten",
  "{a} kg waste → glass": "{a} kg afval → glas",
  "{a} of one block": "{a} van één blok",
  "{a} t of enriched uranium, as {b} t of uranium dioxide (UO₂) ceramic": "{a} t verrijkt uranium, als {b} t keramisch uraniumdioxide (UO₂)",
  "{a} t ore": "{a} t erts",
  "{a} t uranium = {b} t UO₂": "{a} t uranium = {b} t UO₂",
  "→ ≈ {a} t MOX fuel": "→ ≈ {a} t MOX-brandstof",
  "≈ {a} GWh of electricity": "≈ {a} GWh stroom",
  "≈ {a} SWU of separative work per kg of fuel": "≈ {a} SWU scheidingsarbeid per kg brandstof",
  "≈ a big reactor's yearly reload": "≈ de jaarlijkse herlading van een grote reactor",
  "≥ {#} y": "≥ {#} j",
  "≥ {#} years": "≥ {#} jaar",
  "1 t fuel + {a} t tails": "1 t brandstof + {a} t tails",
  "about what a {#} MWe reactor loads in a year": "ongeveer wat een reactor van {#} MWe per jaar laadt",
  "assemblies": "elementen",
  "assemblies of {#} rods": "elementen van {#} staven",
  "at least {#} years": "minstens {#} jaar",
  "cask": "container",
  "Convert": "Conversie",
  "decades": "decennia",
  "decades in air": "decennia aan de lucht",
  "deep repository, {#}–{#} m down": "diepe eindberging, {#}–{#} m diep",
  "Disposal": "Berging",
  "dry cask": "droge container",
  "End": "Einde",
  "enrich": "verrijken",
  "Enrich": "Verrijken",
  "enrichment plant (UF₆ gas)": "verrijkingsfabriek (UF₆-gas)",
  "Fabricate": "Fabricage",
  "feed/fuel = (xp − xt)/(xf − xt) = {a}": "voeding/brandstof = (xp − xt)/(xf − xt) = {a}",
  "fission prod.": "splijtingsprod.",
  "fission products": "splijtingsproducten",
  "fission products + minor actinides {a} kg → ≈ 0.2 t glass": "splijtingsproducten + minor actiniden {a} kg → ≈ 0,2 t glas",
  "fuel 1 kg": "brandstof 1 kg",
  "grade {a} % U": "gehalte {a} % U",
  "illustration": "illustratie",
  "Mill": "Ertsverwerking",
  "Mine": "Mijn",
  "minor actinides": "minor actiniden",
  "most mines: above {#} %": "de meeste mijnen: boven {#} %",
  "natural / fuel = (xp − xt) / (xf − xt) = ({a} − {b}) / ({c} − {b}) = {d}": "natuurlijk / brandstof = (xp − xt) / (xf − xt) = ({a} − {b}) / ({c} − {b}) = {d}",
  "natural U {a} kg": "natuurlijk U {a} kg",
  "natural uranium {a} kg": "natuurlijk uranium {a} kg",
  "of electricity from this tonne": "aan stroom uit deze ton",
  "once-through: the whole tonne is disposed of": "directe berging: de hele ton wordt geborgen",
  "one tonne of fuel: each square is {#} kg": "één ton brandstof: elk vakje is {#} kg",
  "one tonne: each square {#} kg": "één ton: elk vakje {#} kg",
  "ore ≈ {a} t · block = 100 t": "erts ≈ {a} t · blok = 100 t",
  "ore for one tonne of fuel: ≈ {a} t  (each block 100 t)": "erts voor één ton brandstof: ≈ {a} t  (elk blok 100 t)",
  "pellets": "tabletten",
  "pellets, {#} cm tall": "tabletten, {#} cm hoog",
  "plutonium": "plutonium",
  "plutonium {a} kg": "plutonium {a} kg",
  "pool": "bassin",
  "Pool · cask": "Bassin · container",
  "pool ≥ {#} years": "bassin ≥ {#} jaar",
  "Reactor": "Reactor",
  "recycle": "recyclen",
  "repository": "eindberging",
  "repository {#}–{#} m deep": "eindberging {#}–{#} m diep",
  "reprocess": "opwerken",
  "reprocessing": "opwerking",
  "richest, Canada: up to {#} %": "rijkste, Canada: tot {#} %",
  "rods, {#} m": "staven, {#} m",
  "rods, about {#} m long": "staven, ongeveer {#} m lang",
  "separative work ≈ {a} SWU per kg of fuel · lower tails: less uranium, more work": "scheidingsarbeid ≈ {a} SWU per kg brandstof · lagere tails: minder uranium, meer arbeid",
  "Store": "Opslag",
  "tails {a} kg": "tails {a} kg",
  "the rest: uranium{#}": "de rest: uranium{#}",
  "the whole tonne": "de hele ton",
  "typical discharge {#}–{#}": "typische ontlaadopbrand {#}–{#}",
  "U {a} t → re-enrich": "U {a} t → opnieuw verrijken",
  "uranium {a} t": "uranium {a} t",
  "uranium{#}": "uranium{#}",
  "uranium{#} (and {#})": "uranium{#} (en {#})",
});
