/* Italian: reactor (Come un reattore produce elettricità) */
WT.L.ch.reactor = {
  num: "Lezione 1", title: "Come un reattore produce elettricità", short: "Reattore",
  html: `
<div class="step">
  <h3>Il combustibile</h3>
  <p>L'uranio viene cotto in pastiglie di ceramica grandi come un polpastrello, impilate in lunghe barrette metalliche, e le barrette sono raggruppate in elementi di combustibile. Una sola pastiglia dà all'incirca tanto calore quanto la combustione di una tonnellata di carbone.</p>
  <div class="ctl"><label for="rea-z">Allontana lo zoom</label><input id="rea-z" type="range" data-bind="z" min="0" max="3" step="0.01" value="0"><output data-show="z" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>La fissione degli atomi produce calore</h3>
  <p>Nel nocciolo, gli atomi di uranio che si spezzano scaldano l'acqua che sale lungo le barrette. La stessa acqua rallenta i neutroni, così che possano spezzare altri atomi. L'alta pressione le impedisce di bollire, anche a 325 °C.</p>
</div>
<div class="step">
  <h3>Il vapore fa girare la turbina</h3>
  <p>L'acqua calda cede il suo calore, attraverso tubi sottili, a un secondo circuito, che bolle. Il vapore fa girare una turbina e un alternatore, poi l'acqua fredda di un fiume o del mare lo riporta allo stato liquido. Circa un terzo del calore diventa elettricità.</p>
</div>
<div class="step">
  <h3>Le barre di controllo</h3>
  <p>Le barre di controllo assorbono i neutroni. Inseriscile e si spezzano meno atomi: meno calore, meno vapore, meno elettricità. Estraile e la potenza sale.</p>
  <div class="ctl"><label for="rea-rod">Barre di controllo inserite (%)</label><input id="rea-rod" type="range" data-bind="ins" data-instant min="0" max="100" step="1" value="15"><output data-show="ins" data-fmt="0"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "reactor": "reattore",
  "reactor vessel": "recipiente in pressione",
  "control rods": "barre di controllo",
  "core": "nocciolo",
  "steam gen.": "gen. vapore",
  "steam generator": "generatore di vapore",
  "turbine": "turbina",
  "gen.": "altern.",
  "generator": "alternatore",
  "condenser": "condensatore",
  "sea or river water": "acqua di mare o di fiume",
  "{#} °C out": "uscita {#} °C",
  "{#} °C in": "ingresso {#} °C",
  "steam ~{#} °C": "vapore ~{#} °C",
  "{#} bar: hot, but no boiling": "{#} bar: calda, ma non bolle",
  "{#} bar keeps the water liquid at {#} °C": "{#} bar tengono l'acqua liquida a {#} °C",
  "the water also slows the neutrons": "l'acqua rallenta anche i neutroni",
  "the water carries the heat and slows the neutrons": "l'acqua porta via il calore e rallenta i neutroni",
  "heat {#} MW": "calore {#} MW",
  "electric {#} MW": "elettrica {#} MW",
  "electricity {#} MW": "elettricità {#} MW",
  "chain stopped; fuel still warm (afterheat)": "catena ferma; combustibile ancora caldo (calore di decadimento)",
  "chain reaction stopped; the fuel still gives off afterheat": "reazione a catena ferma; il combustibile emette ancora calore di decadimento",
  "turbine speed fixed by the grid; more steam, more push": "velocità fissata dalla rete; più vapore, più spinta",
  "the turbine's speed is fixed by the grid; more steam pushes harder": "la velocità della turbina è fissata dalla rete; più vapore spinge più forte",
  "{#}/{#} of the heat goes to the water": "{#}/{#} del calore va nell'acqua",
  "about two thirds of the heat leaves through the condenser": "circa due terzi del calore escono dal condensatore",
  "illustration": "illustrazione",
  "drag sideways to zoom": "trascina di lato per lo zoom",
  "drag sideways to zoom out": "trascina di lato per allontanare lo zoom",
  "UO₂ pellet, {#} cm": "pastiglia di UO₂, {#} cm",
  "uranium oxide pellet, about {#} cm": "pastiglia di ossido di uranio, circa {#} cm",
  "{#} tonne of coal": "{#} tonnellata di carbone",
  "about {#} tonne of coal (or {#} m³ of gas)": "circa {#} tonnellata di carbone (o {#} m³ di gas)",
  "same heat, roughly": "all'incirca lo stesso calore",
  "fuel rod, ~{#} m": "barretta di combustibile, ~{#} m",
  "fuel rod, about {#} m long": "barretta di combustibile, lunga circa {#} m",
  "~{#} pellets inside": "~{#} pastiglie dentro",
  "about {#} pellets in a metal tube": "circa {#} pastiglie in un tubo metallico",
  "(not to scale)": "(non in scala)",
  "assembly: {#} rods": "elemento: {#} barrette",
  "fuel assembly from above: {#} rods": "elemento di combustibile visto dall'alto: {#} barrette",
  "rings: control-rod guide tubes": "anelli: tubi guida delle barre",
  "rings: tubes the control rods slide into": "anelli: tubi in cui scorrono le barre di controllo",
  "core: {#} assemblies": "nocciolo: {#} elementi",
  "the core from above: {#} assemblies": "il nocciolo visto dall'alto: {#} elementi",
  "~{#} rods, ~{#} m across": "~{#} barrette, ~{#} m di diametro",
  "about {#} rods in a cylinder about {#} m across": "circa {#} barrette in un cilindro di circa {#} m di diametro",
  "~51,000 rods, ~3.4 m across": "~51.000 barrette, ~3,4 m di diametro",
  "about 51,000 rods in a cylinder about 3.4 m across": "circa 51.000 barrette in un cilindro di circa 3,4 m di diametro",
  "pellet": "pastiglia",
  "rod": "barretta",
  "assembly": "elemento",
});
