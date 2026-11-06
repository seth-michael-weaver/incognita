/* Dutch (Nederlands): reactor (Hoe een reactor stroom maakt) */
WT.L.ch.reactor = {
  num: "Les 6", title: "Hoe een reactor stroom maakt", short: "Reactor",
  html: `
<div class="step">
  <h3>De brandstof</h3>
  <p>Uranium wordt gebakken tot keramische tabletten zo groot als een vingertop, gestapeld in lange metalen staven, en de staven worden gebundeld tot brandstofelementen. Eén tablet levert ongeveer evenveel warmte als het verbranden van een ton steenkool.</p>
  <div class="ctl"><label for="rea-z">Uitzoomen</label><input id="rea-z" type="range" data-bind="z" min="0" max="3" step="0.01" value="0"><output data-show="z" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Atomen splijten maakt warmte</h3>
  <p>In de kern verwarmen de splijtende uraniumatomen het water dat langs de staven omhoog stroomt. Hetzelfde water remt de neutronen af zodat ze meer atomen kunnen splijten. Hoge druk voorkomt dat het kookt, zelfs bij 325 °C.</p>
</div>
<div class="step">
  <h3>Stoom drijft de turbine aan</h3>
  <p>Het hete water geeft zijn warmte via dunne buizen af aan een tweede kringloop, die kookt. De stoom laat een turbine en een generator draaien, waarna koud rivier- of zeewater hem weer tot water condenseert. Ongeveer een derde van de warmte wordt elektriciteit.</p>
</div>
<div class="step">
  <h3>Regelstaven</h3>
  <p>Regelstaven slokken neutronen op. Duw ze erin en er splijten minder atomen: minder warmte, minder stoom, minder stroom. Trek ze eruit en het vermogen stijgt.</p>
  <div class="ctl"><label for="rea-rod">Regelstaven erin (%)</label><input id="rea-rod" type="range" data-bind="ins" data-instant min="0" max="100" step="1" value="15"><output data-show="ins" data-fmt="0"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "(not to scale)": "(niet op schaal)",
  "UO₂ pellet, {#} cm": "UO₂-tablet, {#} cm",
  "about two thirds of the heat leaves through the condenser": "ongeveer twee derde van de warmte verdwijnt via de condensor",
  "about {#} pellets in a metal tube": "ongeveer {#} tabletten in een metalen buis",
  "about {#} rods in a cylinder about {#} m across": "ongeveer {#} staven in een cilinder van ongeveer {#} m doorsnede",
  "about {#} tonne of coal (or {#} m³ of gas)": "ongeveer {#} ton steenkool (of {#} m³ gas)",
  "about a tonne of coal": "ongeveer een ton steenkool",
  "assembly": "element",
  "assembly: {#} rods": "element: {#} staven",
  "chain reaction stopped; the fuel still gives off afterheat": "kettingreactie gestopt; de brandstof geeft nog nawarmte af",
  "chain stopped; fuel still warm (afterheat)": "keten gestopt; brandstof nog warm (nawarmte)",
  "condenser": "condensor",
  "control rods": "regelstaven",
  "core": "kern",
  "core: {#} assemblies": "kern: {#} elementen",
  "drag sideways to zoom": "sleep opzij om te zoomen",
  "drag sideways to zoom out": "sleep opzij om uit te zoomen",
  "electric {#} MW": "elektrisch {#} MW",
  "electricity {#} MW": "elektriciteit {#} MW",
  "fuel assembly from above: {#} rods": "brandstofelement van boven: {#} staven",
  "fuel rod, about {#} m long": "brandstofstaaf, ongeveer {#} m lang",
  "fuel rod, ~{#} m": "brandstofstaaf, ~{#} m",
  "gen.": "gen.",
  "generator": "generator",
  "heat {#} MW": "warmte {#} MW",
  "illustration": "illustratie",
  "pellet": "tablet",
  "reactor": "reactor",
  "reactor vessel": "reactorvat",
  "rings: control-rod guide tubes": "ringen: geleidebuizen voor regelstaven",
  "rings: tubes the control rods slide into": "ringen: buizen waarin de regelstaven schuiven",
  "rod": "staaf",
  "same heat, roughly": "ongeveer dezelfde warmte",
  "sea or river water": "zee- of rivierwater",
  "steam gen.": "stoomgen.",
  "steam generator": "stoomgenerator",
  "steam ~{#} °C": "stoom ~{#} °C",
  "the core from above: {#} assemblies": "de kern van boven: {#} elementen",
  "the turbine's speed is fixed by the grid; more steam pushes harder": "het toerental van de turbine ligt vast door het net; meer stoom duwt harder",
  "the water also slows the neutrons": "het water remt ook de neutronen af",
  "the water carries the heat and slows the neutrons": "het water voert de warmte af en remt de neutronen af",
  "turbine": "turbine",
  "turbine speed fixed by the grid; more steam, more push": "toerental vast door het net; meer stoom, meer kracht",
  "uranium oxide pellet, about {#} cm": "uraniumoxidetablet, ongeveer {#} cm",
  "{#} bar keeps the water liquid at {#} °C": "{#} bar houdt het water vloeibaar bij {#} °C",
  "{#} bar: hot, but no boiling": "{#} bar: heet, maar geen koken",
  "{#} tonne of coal": "{#} ton steenkool",
  "{#} °C in": "{#} °C in",
  "{#} °C out": "{#} °C uit",
  "{#}/{#} of the heat goes to the water": "{#}/{#} van de warmte gaat naar het water",
  "~{#} pellets inside": "~{#} tabletten erin",
  "~{#} rods, ~{#} m across": "~{#} staven, ~{#} m doorsnede",
});
