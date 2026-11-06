/* Spanish: reactor (Cómo produce electricidad un reactor) */
WT.L.ch.reactor = {
  num: "Lección 1", title: "Cómo produce electricidad un reactor", short: "Reactor",
  html: `
<div class="step">
  <h3>El combustible</h3>
  <p>El uranio se hornea en pastillas cerámicas del tamaño de la yema de un dedo, que se apilan en largas varillas metálicas, y las varillas se agrupan en elementos combustibles. Una pastilla da más o menos tanto calor como quemar una tonelada de carbón.</p>
  <div class="ctl"><label for="rea-z">Alejar</label><input id="rea-z" type="range" data-bind="z" min="0" max="3" step="0.01" value="0"><output data-show="z" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Partir átomos produce calor</h3>
  <p>En el núcleo, los átomos de uranio que se parten calientan el agua que sube junto a las varillas. Esa misma agua frena los neutrones para que puedan partir más átomos. La alta presión impide que hierva, incluso a 325 °C.</p>
</div>
<div class="step">
  <h3>El vapor mueve la turbina</h3>
  <p>El agua caliente cede su calor, a través de tubos finos, a un segundo circuito, que hierve. El vapor hace girar una turbina y un generador; luego el agua fría de un río o del mar lo vuelve a convertir en agua. Alrededor de un tercio del calor se convierte en electricidad.</p>
</div>
<div class="step">
  <h3>Barras de control</h3>
  <p>Las barras de control absorben neutrones. Introdúcelas y se parten menos átomos: menos calor, menos vapor, menos electricidad. Sácalas y la potencia sube.</p>
  <div class="ctl"><label for="rea-rod">Barras de control insertadas (%)</label><input id="rea-rod" type="range" data-bind="ins" data-instant min="0" max="100" step="1" value="15"><output data-show="ins" data-fmt="0"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "reactor": "reactor",
  "reactor vessel": "vasija del reactor",
  "control rods": "barras de control",
  "core": "núcleo",
  "steam gen.": "gen. de vapor",
  "steam generator": "generador de vapor",
  "turbine": "turbina",
  "gen.": "gen.",
  "generator": "generador",
  "condenser": "condensador",
  "sea or river water": "agua de mar o de río",
  "{#} °C out": "salida {#} °C",
  "{#} °C in": "entrada {#} °C",
  "steam ~{#} °C": "vapor ~{#} °C",
  "{#} bar: hot, but no boiling": "{#} bar: caliente, pero sin hervir",
  "{#} bar keeps the water liquid at {#} °C": "{#} bar mantienen el agua líquida a {#} °C",
  "the water also slows the neutrons": "el agua también frena los neutrones",
  "the water carries the heat and slows the neutrons": "el agua se lleva el calor y frena los neutrones",
  "heat {#} MW": "calor {#} MW",
  "electric {#} MW": "eléctrica {#} MW",
  "electricity {#} MW": "electricidad {#} MW",
  "chain stopped; fuel still warm (afterheat)": "cadena detenida; combustible aún caliente (calor residual)",
  "chain reaction stopped; the fuel still gives off afterheat": "reacción en cadena detenida; el combustible aún desprende calor residual",
  "turbine speed fixed by the grid; more steam, more push": "velocidad fijada por la red; más vapor, más empuje",
  "the turbine's speed is fixed by the grid; more steam pushes harder": "la red fija la velocidad de la turbina; más vapor empuja con más fuerza",
  "{#}/{#} of the heat goes to the water": "{#}/{#} del calor va al agua",
  "about two thirds of the heat leaves through the condenser": "unos dos tercios del calor salen por el condensador",
  "illustration": "ilustración",
  "drag sideways to zoom": "arrastra de lado para alejar",
  "drag sideways to zoom out": "arrastra hacia los lados para alejar la vista",
  "UO₂ pellet, {#} cm": "pastilla de UO₂, {#} cm",
  "uranium oxide pellet, about {#} cm": "pastilla de óxido de uranio, de {#} cm aprox.",
  "{#} tonne of coal": "{#} tonelada de carbón",
  "about {#} tonne of coal (or {#} m³ of gas)": "{#} tonelada de carbón aprox. (o {#} m³ de gas)",
  "same heat, roughly": "más o menos el mismo calor",
  "fuel rod, ~{#} m": "varilla combustible, ~{#} m",
  "fuel rod, about {#} m long": "varilla combustible, de unos {#} m",
  "~{#} pellets inside": "~{#} pastillas dentro",
  "about {#} pellets in a metal tube": "unas {#} pastillas en un tubo metálico",
  "(not to scale)": "(no a escala)",
  "assembly: {#} rods": "elemento: {#} varillas",
  "fuel assembly from above: {#} rods": "elemento combustible visto desde arriba: {#} varillas",
  "rings: control-rod guide tubes": "anillos: tubos guía de las barras",
  "rings: tubes the control rods slide into": "anillos: tubos por los que entran las barras de control",
  "core: {#} assemblies": "núcleo: {#} elementos",
  "the core from above: {#} assemblies": "el núcleo visto desde arriba: {#} elementos",
  "~{#} rods, ~{#} m across": "~{#} varillas, ~{#} m de diámetro",
  "about {#} rods in a cylinder about {#} m across": "unas {#} varillas en un cilindro de unos {#} m de diámetro",
  "~51,000 rods, ~3.4 m across": "~51 000 varillas, ~3,4 m de diámetro",
  "about 51,000 rods in a cylinder about 3.4 m across": "unas 51 000 varillas en un cilindro de unos 3,4 m de diámetro",
  "pellet": "pastilla",
  "rod": "varilla",
  "assembly": "elemento",
});
