/* German (Deutsch): fuelcycle (Der Brennstoffkreislauf) */
WT.L.ch.fuelcycle = {
  num: "Lektion 1", title: "Der Brennstoffkreislauf", short: "Brennstoffkreislauf",
  html: `
<div class="step">
  <h3>Uran abbauen</h3>
  <p>Erz ist größtenteils Gestein, und nur 0,7 % des Urans darin ist Uran-235, die Sorte, die sich leicht spaltet.</p>
  <div class="ctl"><label for="fc-g">Erzgehalt (% Uran)</label><input id="fc-g" type="range" data-bind="lg" data-instant min="-1.7" max="1.3" step="0.01" value="-1"></div>
</div>
<div class="step">
  <h3>Anreicherung ist eine Massenbilanz</h3>
  <p>Als Gas wird das Uran in einen kleinen, an Uran-235 reicheren Strom, den Brennstoff, und einen großen abgereicherten, die Tails, getrennt.</p>
  <div class="ctl"><label for="fc-p">Anreicherung des Brennstoffs (% U-235)</label><input id="fc-p" type="range" data-bind="xp" data-instant min="3" max="5" step="0.05" value="4.5"><output data-show="xp" data-fmt="2"></output></div>
  <div class="ctl"><label for="fc-t">Tails (% U-235)</label><input id="fc-t" type="range" data-bind="xt" data-instant min="0.15" max="0.35" step="0.01" value="0.25"><output data-show="xt" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Tabletten, Stäbe, Brennelemente</h3>
  <p>Das angereicherte Uran wird zu keramischen Tabletten gebrannt, in Stäbe eingeschweißt und zu Brennelementen gebündelt; <a href="#reactor">die nächste Lektion</a> folgt ihnen in den Kern.</p>
  <div class="ctl"><label for="fc-f">Brennstoff (Tonnen Uran)</label><input id="fc-f" type="range" data-bind="ft" data-instant min="1" max="27" step="1" value="1"><output data-show="ft" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Jahre im Kern</h3>
  <p>In drei bis sechs Jahren spalten sich einige Prozent der schweren Atome; zurück bleiben Spaltprodukte und etwas neues Plutonium (<a href="#burnup">Abbrand</a>).</p>
  <div class="ctl"><label for="fc-b">Abbrand (GWd pro Tonne)</label><input id="fc-b" type="range" data-bind="bu" data-instant min="0" max="60" step="1" value="50"><output data-show="bu" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Abkühlen, dann zwei Wege</h3>
  <p>Abgebrannter Brennstoff kühlt in einem Becken und dann in Trockenbehältern ab; danach wird er entweder so, wie er ist, tief vergraben oder wiederaufgearbeitet, damit Uran und Plutonium erneut genutzt werden (<a href="#waste">abgebrannter Brennstoff</a>, <a href="#breeding">Brüten</a>).</p>
  <div class="btns"><button class="btn ghost" data-act="frO" aria-pressed="true">Direkte Endlagerung</button> <button class="btn ghost" data-act="frR" aria-pressed="false">Wiederaufarbeitung</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "{#} are U{#}": "{#} sind U{#}",
  "{#} are uranium{#}": "{#} sind Uran{#}",
  "{#} t used": "{#} t verbraucht",
  "{#} t used fuel": "{#} t abgebrannter Brennstoff",
  "{#} U atoms": "{#} U-Atome",
  "{#} uranium atoms": "{#} Uranatome",
  "{a} % of the heavy atoms split": "{a} % der schweren Atome gespalten",
  "{a} % U": "{a} % U",
  "{a} % U-235": "{a} % U-235",
  "{a} GWd/t": "{a} GWd/t",
  "{a} GWh": "{a} GWh",
  "{a} kg": "{a} kg",
  "{a} kg waste → glass": "{a} kg Abfall → Glas",
  "{a} of one block": "{a} eines Blocks",
  "{a} t of enriched uranium, as {b} t of uranium dioxide (UO₂) ceramic": "{a} t angereichertes Uran, als {b} t Urandioxid-Keramik (UO₂)",
  "{a} t ore": "{a} t Erz",
  "{a} t U₃O₈": "{a} t U₃O₈",
  "{a} t UF₆": "{a} t UF₆",
  "{a} t UO₂": "{a} t UO₂",
  "{a} t uranium = {b} t UO₂": "{a} t Uran = {b} t UO₂",
  "→ ≈ {a} t MOX fuel": "→ ≈ {a} t MOX-Brennstoff",
  "≈ {a} GWh": "≈ {a} GWh",
  "≈ {a} GWh of electricity": "≈ {a} GWh Strom",
  "≈ {a} SWU of separative work per kg of fuel": "≈ {a} UTA Trennarbeit pro kg Brennstoff",
  "≈ a big reactor's yearly reload": "≈ die jährliche Nachladung eines großen Reaktors",
  "≥ {#} y": "≥ {#} a",
  "≥ {#} years": "≥ {#} Jahre",
  "1 t fuel + {a} t tails": "1 t Brennstoff + {a} t Tails",
  "about what a {#} MWe reactor loads in a year": "etwa das, was ein {#}-MWe-Reaktor pro Jahr lädt",
  "assemblies": "Brennelemente",
  "assemblies of {#} rods": "Brennelemente aus {#} Stäben",
  "at least {#} years": "mindestens {#} Jahre",
  "cask": "Behälter",
  "Convert": "Konversion",
  "decades": "Jahrzehnte",
  "decades in air": "Jahrzehnte an der Luft",
  "deep repository, {#}–{#} m down": "tiefes Endlager, {#}–{#} m unter der Erde",
  "Disposal": "Endlager",
  "dry cask": "Trockenbehälter",
  "End": "Ende",
  "enrich": "anreichern",
  "Enrich": "Anreichern",
  "enrichment plant (UF₆ gas)": "Anreicherungsanlage (UF₆-Gas)",
  "Fabricate": "Fertigung",
  "feed/fuel = (xp − xt)/(xf − xt) = {a}": "Feed/Brennstoff = (xp − xt)/(xf − xt) = {a}",
  "fission prod.": "Spaltprod.",
  "fission products": "Spaltprodukte",
  "fission products + minor actinides {a} kg → ≈ 0.2 t glass": "Spaltprodukte + minore Actinoide {a} kg → ≈ 0,2 t Glas",
  "fuel 1 kg": "Brennstoff 1 kg",
  "grade {a} % U": "Gehalt {a} % U",
  "illustration": "Illustration",
  "Mill": "Aufbereitung",
  "Mine": "Bergwerk",
  "minor actinides": "minore Actinoide",
  "most mines: above {#} %": "die meisten Bergwerke: über {#} %",
  "natural / fuel = (xp − xt) / (xf − xt) = ({a} − {b}) / ({c} − {b}) = {d}": "natürlich / Brennstoff = (xp − xt) / (xf − xt) = ({a} − {b}) / ({c} − {b}) = {d}",
  "natural U {a} kg": "Natururan {a} kg",
  "natural uranium {a} kg": "Natururan {a} kg",
  "of electricity from this tonne": "Strom aus dieser Tonne",
  "once-through: the whole tonne is disposed of": "direkte Endlagerung: die ganze Tonne wird entsorgt",
  "one tonne of fuel: each square is {#} kg": "eine Tonne Brennstoff: jedes Quadrat ist {#} kg",
  "one tonne: each square {#} kg": "eine Tonne: jedes Quadrat {#} kg",
  "ore ≈ {a} t · block = 100 t": "Erz ≈ {a} t · Block = 100 t",
  "ore for one tonne of fuel: ≈ {a} t  (each block 100 t)": "Erz für eine Tonne Brennstoff: ≈ {a} t  (jeder Block 100 t)",
  "pellets": "Tabletten",
  "pellets, {#} cm tall": "Tabletten, {#} cm hoch",
  "plutonium": "Plutonium",
  "plutonium {a} kg": "Plutonium {a} kg",
  "pool": "Becken",
  "Pool · cask": "Becken · Behälter",
  "pool ≥ {#} years": "Becken ≥ {#} Jahre",
  "Pu {a} kg → MOX": "Pu {a} kg → MOX",
  "Reactor": "Reaktor",
  "recycle": "Rückführung",
  "repository": "Endlager",
  "repository {#}–{#} m deep": "Endlager {#}–{#} m tief",
  "reprocess": "aufarbeiten",
  "reprocessing": "Wiederaufarbeitung",
  "richest, Canada: up to {#} %": "am reichsten, Kanada: bis {#} %",
  "rods, {#} m": "Stäbe, {#} m",
  "rods, about {#} m long": "Stäbe, etwa {#} m lang",
  "separative work ≈ {a} SWU per kg of fuel · lower tails: less uranium, more work": "Trennarbeit ≈ {a} UTA pro kg Brennstoff · niedrigere Tails: weniger Uran, mehr Arbeit",
  "Store": "Lager",
  "tails {a} kg": "Tails {a} kg",
  "the rest: uranium{#}": "der Rest: Uran{#}",
  "the whole tonne": "die ganze Tonne",
  "typical discharge {#}–{#}": "typischer Entladeabbrand {#}–{#}",
  "U {a} t → re-enrich": "U {a} t → wieder anreichern",
  "uranium {a} t": "Uran {a} t",
  "uranium{#}": "Uran{#}",
  "uranium{#} (and {#})": "Uran{#} (und {#})",
});
