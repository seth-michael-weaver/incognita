/* Danish: reactor (Sådan laver en reaktor strøm) */
WT.L.ch.reactor = {
  num: "Lektion 6", title: "Sådan laver en reaktor strøm", short: "Reaktor",
  html: `
<div class="step">
  <h3>Brændslet</h3>
  <p>Uran bages til keramiske piller på størrelse med en fingerspids, stables i lange metalstave, og stavene samles i bundter, brændselselementer. Én pille giver omtrent lige så meget varme som at brænde et ton kul.</p>
  <div class="ctl"><label for="rea-z">Zoom ud</label><input id="rea-z" type="range" data-bind="z" min="0" max="3" step="0.01" value="0"><output data-show="z" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Spaltning af atomer giver varme</h3>
  <p>I kernen opvarmer de spaltende uranatomer vandet, der strømmer op forbi stavene. Det samme vand bremser neutronerne, så de kan spalte flere atomer. Højt tryk forhindrer det i at koge, selv ved 325 °C.</p>
</div>
<div class="step">
  <h3>Damp driver turbinen</h3>
  <p>Det varme vand afgiver sin varme gennem tynde rør til et andet kredsløb, som koger. Dampen driver en turbine og en generator, og koldt flod- eller havvand gør den igen til vand. Omkring en tredjedel af varmen bliver til elektricitet.</p>
</div>
<div class="step">
  <h3>Kontrolstave</h3>
  <p>Kontrolstave suger neutroner op. Skub dem ind, og færre atomer spaltes: mindre varme, mindre damp, mindre strøm. Træk dem ud, og effekten stiger.</p>
  <div class="ctl"><label for="rea-rod">Kontrolstave inde (%)</label><input id="rea-rod" type="range" data-bind="ins" data-instant min="0" max="100" step="1" value="15"><output data-show="ins" data-fmt="0"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "(not to scale)": "(ikke målfast)",
  "UO₂ pellet, {#} cm": "UO₂-pille, {#} cm",
  "about two thirds of the heat leaves through the condenser": "omkring to tredjedele af varmen forsvinder gennem kondensatoren",
  "about {#} pellets in a metal tube": "omkring {#} piller i et metalrør",
  "about {#} rods in a cylinder about {#} m across": "omkring {#} stave i en cylinder på omkring {#} m i diameter",
  "about {#} tonne of coal (or {#} m³ of gas)": "omkring {#} ton kul (eller {#} m³ gas)",
  "about a tonne of coal": "omkring et ton kul",
  "assembly": "element",
  "assembly: {#} rods": "element: {#} stave",
  "chain reaction stopped; the fuel still gives off afterheat": "kædereaktionen stoppet; brændslet afgiver stadig efterhenfaldsvarme",
  "chain stopped; fuel still warm (afterheat)": "kæden stoppet; brændslet stadig varmt (efterhenfaldsvarme)",
  "condenser": "kondensator",
  "control rods": "kontrolstave",
  "core": "kerne",
  "core: {#} assemblies": "kerne: {#} elementer",
  "drag sideways to zoom": "træk sidelæns for at zoome",
  "drag sideways to zoom out": "træk sidelæns for at zoome ud",
  "electric {#} MW": "elektrisk {#} MW",
  "electricity {#} MW": "elektricitet {#} MW",
  "fuel assembly from above: {#} rods": "brændselselement set ovenfra: {#} stave",
  "fuel rod, about {#} m long": "brændselsstav, omkring {#} m lang",
  "fuel rod, ~{#} m": "brændselsstav, ~{#} m",
  "gen.": "gen.",
  "generator": "generator",
  "heat {#} MW": "varme {#} MW",
  "illustration": "illustration",
  "pellet": "pille",
  "reactor": "reaktor",
  "reactor vessel": "reaktortank",
  "rings: control-rod guide tubes": "ringe: føringsrør til kontrolstave",
  "rings: tubes the control rods slide into": "ringe: rør, som kontrolstavene glider ind i",
  "rod": "stav",
  "same heat, roughly": "omtrent samme varme",
  "sea or river water": "hav- eller flodvand",
  "steam gen.": "dampgen.",
  "steam generator": "dampgenerator",
  "steam ~{#} °C": "damp ~{#} °C",
  "the core from above: {#} assemblies": "kernen set ovenfra: {#} elementer",
  "the turbine's speed is fixed by the grid; more steam pushes harder": "turbinens hastighed er fastlagt af nettet; mere damp skubber hårdere",
  "the water also slows the neutrons": "vandet bremser også neutronerne",
  "the water carries the heat and slows the neutrons": "vandet bærer varmen væk og bremser neutronerne",
  "turbine": "turbine",
  "turbine speed fixed by the grid; more steam, more push": "turbinehastighed fastlagt af nettet; mere damp, mere kraft",
  "uranium oxide pellet, about {#} cm": "uranoxidpille, omkring {#} cm",
  "{#} bar keeps the water liquid at {#} °C": "{#} bar holder vandet flydende ved {#} °C",
  "{#} bar: hot, but no boiling": "{#} bar: varmt, men ingen kogning",
  "{#} tonne of coal": "{#} ton kul",
  "{#} °C in": "{#} °C ind",
  "{#} °C out": "{#} °C ud",
  "{#}/{#} of the heat goes to the water": "{#}/{#} af varmen går til vandet",
  "~{#} pellets inside": "~{#} piller indeni",
  "~{#} rods, ~{#} m across": "~{#} stave, ~{#} m i diameter",
});
