/* French: reactor (Comment un réacteur produit de l'électricité) */
WT.L.ch.reactor = {
  num: "Leçon 1", title: "Comment un réacteur produit de l'électricité", short: "Réacteur",
  html: `
<div class="step">
  <h3>Le combustible</h3>
  <p>L'uranium est cuit en pastilles de céramique de la taille d'un bout de doigt, empilées dans de longs crayons métalliques, eux-mêmes réunis en assemblages. Une pastille donne à peu près autant de chaleur que la combustion d'une tonne de charbon.</p>
  <div class="ctl"><label for="rea-z">Zoom arrière</label><input id="rea-z" type="range" data-bind="z" min="0" max="3" step="0.01" value="0"><output data-show="z" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Fissionner des atomes produit de la chaleur</h3>
  <p>Dans le cœur, les atomes d'uranium qui fissionnent chauffent l'eau qui remonte le long des crayons. Cette même eau ralentit les neutrons pour qu'ils puissent fissionner d'autres atomes. Une forte pression l'empêche de bouillir, même à 325 °C.</p>
</div>
<div class="step">
  <h3>La vapeur fait tourner la turbine</h3>
  <p>L'eau chaude cède sa chaleur, à travers de fins tubes, à un second circuit, qui se met à bouillir. La vapeur fait tourner une turbine et un alternateur, puis l'eau froide d'une rivière ou de la mer la recondense en eau. Environ un tiers de la chaleur devient de l'électricité.</p>
</div>
<div class="step">
  <h3>Les barres de commande</h3>
  <p>Les barres de commande absorbent les neutrons. Enfoncez-les et moins d'atomes fissionnent : moins de chaleur, moins de vapeur, moins d'électricité. Retirez-les et la puissance monte.</p>
  <div class="ctl"><label for="rea-rod">Barres de commande enfoncées (%)</label><input id="rea-rod" type="range" data-bind="ins" data-instant min="0" max="100" step="1" value="15"><output data-show="ins" data-fmt="0"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "reactor": "réacteur",
  "reactor vessel": "cuve du réacteur",
  "control rods": "barres de commande",
  "core": "cœur",
  "steam gen.": "GV",
  "steam generator": "générateur de vapeur",
  "turbine": "turbine",
  "gen.": "altern.",
  "generator": "alternateur",
  "condenser": "condenseur",
  "sea or river water": "eau de mer ou de rivière",
  "{#} °C out": "sortie {#} °C",
  "{#} °C in": "entrée {#} °C",
  "steam ~{#} °C": "vapeur ~{#} °C",
  "{#} bar: hot, but no boiling": "{#} bar : chaude, mais sans ébullition",
  "{#} bar keeps the water liquid at {#} °C": "{#} bar maintiennent l'eau liquide à {#} °C",
  "the water also slows the neutrons": "l'eau ralentit aussi les neutrons",
  "the water carries the heat and slows the neutrons": "l'eau emporte la chaleur et ralentit les neutrons",
  "heat {#} MW": "chaleur {#} MW",
  "electric {#} MW": "électrique {#} MW",
  "electricity {#} MW": "électricité {#} MW",
  "chain stopped; fuel still warm (afterheat)": "chaîne arrêtée ; combustible encore chaud (chaleur résiduelle)",
  "chain reaction stopped; the fuel still gives off afterheat": "réaction en chaîne arrêtée ; le combustible dégage encore de la chaleur résiduelle",
  "turbine speed fixed by the grid; more steam, more push": "turbine calée sur le réseau ; plus de vapeur, plus de poussée",
  "the turbine's speed is fixed by the grid; more steam pushes harder": "la vitesse de la turbine est fixée par le réseau ; plus de vapeur pousse plus fort",
  "{#}/{#} of the heat goes to the water": "{#}/{#} de la chaleur part dans l'eau",
  "about two thirds of the heat leaves through the condenser": "environ deux tiers de la chaleur partent par le condenseur",
  "illustration": "illustration",
  "drag sideways to zoom": "glissez de côté pour zoomer",
  "drag sideways to zoom out": "glissez de côté pour faire un zoom arrière",
  "UO₂ pellet, {#} cm": "pastille d'UO₂, {#} cm",
  "uranium oxide pellet, about {#} cm": "pastille d'oxyde d'uranium, environ {#} cm",
  "{#} tonne of coal": "{#} tonne de charbon",
  "about {#} tonne of coal (or {#} m³ of gas)": "environ {#} tonne de charbon (ou {#} m³ de gaz)",
  "same heat, roughly": "à peu près la même chaleur",
  "fuel rod, ~{#} m": "crayon combustible, ~{#} m",
  "fuel rod, about {#} m long": "crayon combustible, environ {#} m de long",
  "~{#} pellets inside": "~{#} pastilles dedans",
  "about {#} pellets in a metal tube": "environ {#} pastilles dans une gaine métallique",
  "(not to scale)": "(pas à l'échelle)",
  "assembly: {#} rods": "assemblage : {#} crayons",
  "fuel assembly from above: {#} rods": "assemblage combustible vu de dessus : {#} crayons",
  "rings: control-rod guide tubes": "anneaux : tubes guides des barres",
  "rings: tubes the control rods slide into": "anneaux : tubes où coulissent les barres de commande",
  "core: {#} assemblies": "cœur : {#} assemblages",
  "the core from above: {#} assemblies": "le cœur vu de dessus : {#} assemblages",
  "~{#} rods, ~{#} m across": "~{#} crayons, ~{#} m de diamètre",
  "about {#} rods in a cylinder about {#} m across": "environ {#} crayons dans un cylindre d'environ {#} m de diamètre",
  "~51,000 rods, ~3.4 m across": "~51 000 crayons, ~3,4 m de diamètre",
  "about 51,000 rods in a cylinder about 3.4 m across": "environ 51 000 crayons dans un cylindre d'environ 3,4 m de diamètre",
  "pellet": "pastille",
  "rod": "crayon",
  "assembly": "assemblage",
});
