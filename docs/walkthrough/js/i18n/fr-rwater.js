/* French: rwater (Réacteurs refroidis à l'eau) */
WT.L.ch.rwater = {
  num: "Leçon 1", title: "Réacteurs refroidis à l'eau", short: "Réacteurs à eau",
  lead: "Presque tous les réacteurs de puissance actuels sont refroidis à l'eau. Ils diffèrent par la façon dont l'eau évacue la chaleur.",
  html: `
<div class="step">
  <h3>Eau pressurisée (REP)</h3>
  <p>L'eau sous haute pression porte la chaleur jusqu'à un générateur de vapeur ; un second circuit produit la vapeur.</p>
</div>
<div class="step">
  <h3>Eau bouillante (REB)</h3>
  <p>L'eau bout dans le cœur lui-même et la vapeur va droit à la turbine : un seul circuit.</p>
</div>
<div class="step">
  <h3>Eau lourde (CANDU)</h3>
  <p>L'eau lourde ralentit les neutrons sans en absorber beaucoup, si bien que l'uranium naturel suffit.</p>
</div>
<div class="step">
  <h3>Graphite et eau bouillante (RBMK)</h3>
  <p>Le graphite ralentit les neutrons ; l'eau bout dans des centaines de tubes séparés.</p>
</div>
<div class="step">
  <h3>Petit réacteur modulaire (SMR)</h3>
  <p>Un petit REP dont tout tient dans une seule cuve, construit en usine.</p>
</div>
<div class="step">
  <h3>Eau supercritique (SCWR)</h3>
  <p>Au-delà de 221 bar, l'eau ne bout jamais : le réacteur peut fonctionner plus chaud et convertir davantage de chaleur en électricité.</p>
</div>`,
};

Object.assign(WT.L.labels, {
  "BWR": "REB",
  "CANDU; Canada, India, Romania, Argentina": "CANDU ; Canada, Inde, Roumanie, Argentine",
  "Generation IV design, not yet built": "concept de Génération IV, pas encore construit",
  "NuScale (US), Linglong One (China)": "NuScale (États-Unis), Linglong One (Chine)",
  "PHWR": "PHWR",
  "PWR": "REP",
  "RBMK": "RBMK",
  "SCWR": "SCWR",
  "SMR": "SMR",
  "about {#} % of reactors; US, Japan, Sweden": "environ {#} % des réacteurs ; États-Unis, Japon, Suède",
  "about {#} in {#} of the world's reactors": "environ {#} réacteurs sur {#} dans le monde",
  "all in one vessel": "tout dans une seule cuve",
  "boiling water in tubes": "eau bouillante dans des tubes",
  "boils in the core": "bout dans le cœur",
  "calandria: cool heavy water": "calandre : eau lourde froide",
  "calandria: cool heavy water slows the neutrons": "calandre : l'eau lourde froide ralentit les neutrons",
  "condenser": "condenseur",
  "control rods from below": "barres de commande par le bas",
  "coolant out": "sortie caloporteur",
  "core": "cœur",
  "core, pump-free loop and steam generator in one vessel": "cœur, circulation naturelle sans pompe et générateur de vapeur dans une seule cuve",
  "electricity": "électricité",
  "gen.": "altern.",
  "generator": "alternateur",
  "graphite": "graphite",
  "graphite blocks slow the neutrons": "des blocs de graphite ralentissent les neutrons",
  "horizontal pressure tubes, refuelled while running": "tubes de force horizontaux, rechargés en marche",
  "illustration": "illustration",
  "outlet": "sortie",
  "pressure": "pression",
  "pressure tubes": "tubes de force",
  "reactor vessel": "cuve du réacteur",
  "rods from below": "barres par le bas",
  "steam gen.": "GV",
  "steam generator": "générateur de vapeur",
  "the Chernobyl type; a few still run in Russia": "le type de Tchernobyl ; quelques-uns fonctionnent encore en Russie",
  "thermal neutrons · moderator: graphite · coolant: boiling water": "neutrons thermiques · modérateur : graphite · caloporteur : eau bouillante",
  "thermal neutrons · moderator: heavy water · coolant: heavy water": "neutrons thermiques · modérateur : eau lourde · caloporteur : eau lourde",
  "thermal neutrons · moderator: light water · coolant: boiling water": "neutrons thermiques · modérateur : eau légère · caloporteur : eau bouillante",
  "thermal neutrons · moderator: light water · coolant: supercritical water": "neutrons thermiques · modérateur : eau légère · caloporteur : eau supercritique",
  "thermal neutrons · moderator: light water · coolant: water": "neutrons thermiques · modérateur : eau légère · caloporteur : eau",
  "thermal · mod.: graphite · cool.: boiling water": "thermiques · mod. : graphite · calo. : eau bouillante",
  "thermal · mod.: heavy water · cool.: heavy water": "thermiques · mod. : eau lourde · calo. : eau lourde",
  "thermal · mod.: light water · cool.: boiling water": "thermiques · mod. : eau légère · calo. : eau bouillante",
  "thermal · mod.: light water · cool.: supercritical water": "thermiques · mod. : eau légère · calo. : eau supercritique",
  "thermal · mod.: light water · cool.: water": "thermiques · mod. : eau légère · calo. : eau",
  "turbine": "turbine",
  "vessel": "cuve",
  "water boils in the core": "l'eau bout dans le cœur",
  "water boils in ~{#} pressure tubes": "l'eau bout dans ~{#} tubes de force",
  "{#} bar": "{#} bar",
  "{#} bar: hotter than boiling, still one fluid": "{#} bar : plus chaud que l'ébullition, toujours un seul fluide",
  "{#} bar: never boils": "{#} bar : ne bout jamais",
  "{#} °C": "{#} °C",
});
