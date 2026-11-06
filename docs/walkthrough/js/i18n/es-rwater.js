/* Spanish: rwater (Reactores refrigerados por agua) */
WT.L.ch.rwater = {
  num: "Lección 1", title: "Reactores refrigerados por agua", short: "Reactores de agua",
  lead: "Casi todos los reactores de potencia actuales se refrigeran con agua. Se diferencian en cómo el agua saca el calor.",
  html: `
<div class="step">
  <h3>Agua a presión (PWR)</h3>
  <p>El agua a alta presión lleva el calor a un generador de vapor; un segundo circuito produce el vapor.</p>
</div>
<div class="step">
  <h3>Agua en ebullición (BWR)</h3>
  <p>El agua hierve en el propio núcleo y el vapor va directo a la turbina: un solo circuito.</p>
</div>
<div class="step">
  <h3>Agua pesada (CANDU)</h3>
  <p>El agua pesada frena los neutrones sin absorber muchos, así que basta con uranio natural.</p>
</div>
<div class="step">
  <h3>Grafito y agua en ebullición (RBMK)</h3>
  <p>El grafito frena los neutrones; el agua hierve en cientos de tubos separados.</p>
</div>
<div class="step">
  <h3>Pequeño modular (SMR)</h3>
  <p>Un PWR pequeño con todo dentro de una sola vasija, construido en fábrica.</p>
</div>
<div class="step">
  <h3>Agua supercrítica (SCWR)</h3>
  <p>Por encima de 221 bar el agua nunca hierve, así que puede trabajar más caliente y convertir más calor en electricidad.</p>
</div>`,
};

Object.assign(WT.L.labels, {
  "BWR": "BWR",
  "CANDU; Canada, India, Romania, Argentina": "CANDU; Canadá, India, Rumanía, Argentina",
  "Generation IV design, not yet built": "diseño de Generación IV, aún sin construir",
  "NuScale (US), Linglong One (China)": "NuScale (EE. UU.), Linglong One (China)",
  "PHWR": "PHWR",
  "PWR": "PWR",
  "RBMK": "RBMK",
  "SCWR": "SCWR",
  "SMR": "SMR",
  "about {#} % of reactors; US, Japan, Sweden": "en torno al {#} % de los reactores; EE. UU., Japón, Suecia",
  "about {#} in {#} of the world's reactors": "unos {#} de cada {#} reactores del mundo",
  "all in one vessel": "todo en una vasija",
  "boiling water in tubes": "agua hirviendo en tubos",
  "boils in the core": "hierve en el núcleo",
  "calandria: cool heavy water": "calandria: agua pesada fría",
  "calandria: cool heavy water slows the neutrons": "calandria: agua pesada fría que frena los neutrones",
  "condenser": "condensador",
  "control rods from below": "barras de control desde abajo",
  "coolant out": "salida del refrigerante",
  "core": "núcleo",
  "core, pump-free loop and steam generator in one vessel": "núcleo, circuito sin bombas y generador de vapor en una sola vasija",
  "electricity": "electricidad",
  "gen.": "gen.",
  "generator": "generador",
  "graphite": "grafito",
  "graphite blocks slow the neutrons": "los bloques de grafito frenan los neutrones",
  "horizontal pressure tubes, refuelled while running": "tubos de presión horizontales, recarga en marcha",
  "illustration": "ilustración",
  "outlet": "salida",
  "pressure": "presión",
  "pressure tubes": "tubos de presión",
  "reactor vessel": "vasija del reactor",
  "rods from below": "barras desde abajo",
  "steam gen.": "gen. de vapor",
  "steam generator": "generador de vapor",
  "the Chernobyl type; a few still run in Russia": "el tipo de Chernóbil; aún funcionan algunos en Rusia",
  "thermal neutrons · moderator: graphite · coolant: boiling water": "neutrones térmicos · moderador: grafito · refrigerante: agua en ebullición",
  "thermal neutrons · moderator: heavy water · coolant: heavy water": "neutrones térmicos · moderador: agua pesada · refrigerante: agua pesada",
  "thermal neutrons · moderator: light water · coolant: boiling water": "neutrones térmicos · moderador: agua ligera · refrigerante: agua en ebullición",
  "thermal neutrons · moderator: light water · coolant: supercritical water": "neutrones térmicos · moderador: agua ligera · refrigerante: agua supercrítica",
  "thermal neutrons · moderator: light water · coolant: water": "neutrones térmicos · moderador: agua ligera · refrigerante: agua",
  "thermal · mod.: graphite · cool.: boiling water": "térmico · mod.: grafito · refr.: agua en ebullición",
  "thermal · mod.: heavy water · cool.: heavy water": "térmico · mod.: agua pesada · refr.: agua pesada",
  "thermal · mod.: light water · cool.: boiling water": "térmico · mod.: agua ligera · refr.: agua en ebullición",
  "thermal · mod.: light water · cool.: supercritical water": "térmico · mod.: agua ligera · refr.: agua supercrítica",
  "thermal · mod.: light water · cool.: water": "térmico · mod.: agua ligera · refr.: agua",
  "turbine": "turbina",
  "vessel": "vasija",
  "water boils in the core": "el agua hierve en el núcleo",
  "water boils in ~{#} pressure tubes": "el agua hierve en ~{#} tubos de presión",
  "{#} bar": "{#} bar",
  "{#} bar: hotter than boiling, still one fluid": "{#} bar: más caliente que el punto de ebullición, y sigue siendo un solo fluido",
  "{#} bar: never boils": "{#} bar: nunca hierve",
  "{#} °C": "{#} °C",
});
