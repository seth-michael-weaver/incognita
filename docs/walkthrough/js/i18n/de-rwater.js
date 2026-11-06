/* German (Deutsch): rwater (Wassergekühlte Reaktoren) */
WT.L.ch.rwater = {
  num: "Lektion 1", title: "Wassergekühlte Reaktoren", short: "Wasserreaktoren",
  lead: "Fast jeder Leistungsreaktor wird heute mit Wasser gekühlt. Sie unterscheiden sich darin, wie das Wasser die Wärme abführt.",
  html: `
<div class="step">
  <h3>Druckwasser (DWR)</h3>
  <p>Wasser unter hohem Druck bringt die Wärme zu einem Dampferzeuger; ein zweiter Kreislauf erzeugt den Dampf.</p>
</div>
<div class="step">
  <h3>Siedewasser (SWR)</h3>
  <p>Das Wasser siedet im Kern selbst, und der Dampf geht direkt zur Turbine: ein einziger Kreislauf.</p>
</div>
<div class="step">
  <h3>Schwerwasser (CANDU)</h3>
  <p>Schweres Wasser bremst Neutronen, ohne viele davon zu schlucken, deshalb reicht Natururan.</p>
</div>
<div class="step">
  <h3>Graphit und Siedewasser (RBMK)</h3>
  <p>Graphit bremst die Neutronen; das Wasser siedet in Hunderten einzelner Röhren.</p>
</div>
<div class="step">
  <h3>Klein und modular (SMR)</h3>
  <p>Ein kleiner DWR, bei dem alles in einem Behälter steckt, gebaut in einer Fabrik.</p>
</div>
<div class="step">
  <h3>Überkritisches Wasser (SCWR)</h3>
  <p>Oberhalb von 221 bar siedet Wasser nie, also kann der Reaktor heißer laufen und mehr Wärme in Strom verwandeln.</p>
</div>`,
};

Object.assign(WT.L.labels, {
  "BWR": "SWR",
  "CANDU; Canada, India, Romania, Argentina": "CANDU; Kanada, Indien, Rumänien, Argentinien",
  "Generation IV design, not yet built": "Generation-IV-Konzept, noch nicht gebaut",
  "NuScale (US), Linglong One (China)": "NuScale (USA), Linglong One (China)",
  "PHWR": "PHWR",
  "PWR": "DWR",
  "RBMK": "RBMK",
  "SCWR": "SCWR",
  "SMR": "SMR",
  "about {#} % of reactors; US, Japan, Sweden": "etwa {#} % der Reaktoren; USA, Japan, Schweden",
  "about {#} in {#} of the world's reactors": "etwa {#} von {#} Reaktoren weltweit",
  "all in one vessel": "alles in einem Behälter",
  "boiling water in tubes": "siedendes Wasser in Röhren",
  "boils in the core": "siedet im Kern",
  "calandria: cool heavy water": "Calandria: kühles Schwerwasser",
  "calandria: cool heavy water slows the neutrons": "Calandria: kühles Schwerwasser bremst die Neutronen",
  "condenser": "Kondensator",
  "control rods from below": "Steuerstäbe von unten",
  "coolant out": "Kühlmittel aus",
  "core": "Kern",
  "core, pump-free loop and steam generator in one vessel": "Kern, Naturumlauf ohne Pumpen und Dampferzeuger in einem Behälter",
  "electricity": "Strom",
  "gen.": "Gen.",
  "generator": "Generator",
  "graphite": "Graphit",
  "graphite blocks slow the neutrons": "Graphitblöcke bremsen die Neutronen",
  "horizontal pressure tubes, refuelled while running": "waagrechte Druckröhren, im Betrieb neu beladen",
  "illustration": "Illustration",
  "outlet": "Austritt",
  "pressure": "Druck",
  "pressure tubes": "Druckröhren",
  "reactor vessel": "Reaktordruckbehälter",
  "rods from below": "Stäbe von unten",
  "steam gen.": "Dampferz.",
  "steam generator": "Dampferzeuger",
  "the Chernobyl type; a few still run in Russia": "der Tschernobyl-Typ; einige laufen noch in Russland",
  "thermal neutrons · moderator: graphite · coolant: boiling water": "thermische Neutronen · Moderator: Graphit · Kühlmittel: siedendes Wasser",
  "thermal neutrons · moderator: heavy water · coolant: heavy water": "thermische Neutronen · Moderator: Schwerwasser · Kühlmittel: Schwerwasser",
  "thermal neutrons · moderator: light water · coolant: boiling water": "thermische Neutronen · Moderator: Leichtwasser · Kühlmittel: siedendes Wasser",
  "thermal neutrons · moderator: light water · coolant: supercritical water": "thermische Neutronen · Moderator: Leichtwasser · Kühlmittel: überkritisches Wasser",
  "thermal neutrons · moderator: light water · coolant: water": "thermische Neutronen · Moderator: Leichtwasser · Kühlmittel: Wasser",
  "thermal · mod.: graphite · cool.: boiling water": "thermisch · Mod.: Graphit · Kühlm.: siedendes Wasser",
  "thermal · mod.: heavy water · cool.: heavy water": "thermisch · Mod.: Schwerwasser · Kühlm.: Schwerwasser",
  "thermal · mod.: light water · cool.: boiling water": "thermisch · Mod.: Leichtwasser · Kühlm.: siedendes Wasser",
  "thermal · mod.: light water · cool.: supercritical water": "thermisch · Mod.: Leichtwasser · Kühlm.: überkritisches Wasser",
  "thermal · mod.: light water · cool.: water": "thermisch · Mod.: Leichtwasser · Kühlm.: Wasser",
  "turbine": "Turbine",
  "vessel": "Druckbehälter",
  "water boils in the core": "Wasser siedet im Kern",
  "water boils in ~{#} pressure tubes": "Wasser siedet in ~{#} Druckröhren",
  "{#} bar": "{#} bar",
  "{#} bar: hotter than boiling, still one fluid": "{#} bar: heißer als siedend, und doch ein einziges Fluid",
  "{#} bar: never boils": "{#} bar: siedet nie",
  "{#} °C": "{#} °C",
});
