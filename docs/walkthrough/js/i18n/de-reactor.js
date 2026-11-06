/* German (Deutsch): reactor (Wie ein Reaktor Strom erzeugt) */
WT.L.ch.reactor = {
  num: "Lektion 6", title: "Wie ein Reaktor Strom erzeugt", short: "Reaktor",
  html: `
<div class="step">
  <h3>Der Brennstoff</h3>
  <p>Uran wird zu keramischen Tabletten von der Größe einer Fingerkuppe gebrannt, in lange Metallstäbe gestapelt, und die Stäbe werden zu Brennelementen gebündelt. Eine Tablette liefert ungefähr so viel Wärme wie die Verbrennung einer Tonne Kohle.</p>
  <div class="ctl"><label for="rea-z">Herauszoomen</label><input id="rea-z" type="range" data-bind="z" min="0" max="3" step="0.01" value="0"><output data-show="z" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Atomspaltung erzeugt Wärme</h3>
  <p>Im Kern heizen die sich spaltenden Uranatome das Wasser, das an den Stäben vorbei nach oben strömt. Dasselbe Wasser bremst die Neutronen ab, damit sie weitere Atome spalten können. Hoher Druck verhindert, dass es siedet, selbst bei 325 °C.</p>
</div>
<div class="step">
  <h3>Dampf treibt die Turbine</h3>
  <p>Das heiße Wasser gibt seine Wärme durch dünne Rohre an einen zweiten Kreislauf ab, der siedet. Der Dampf dreht eine Turbine und einen Generator, dann verwandelt kaltes Fluss- oder Meerwasser ihn wieder in Wasser. Etwa ein Drittel der Wärme wird zu Strom.</p>
</div>
<div class="step">
  <h3>Steuerstäbe</h3>
  <p>Steuerstäbe schlucken Neutronen. Fährt man sie ein, spalten sich weniger Atome: weniger Wärme, weniger Dampf, weniger Strom. Zieht man sie heraus, steigt die Leistung.</p>
  <div class="ctl"><label for="rea-rod">Steuerstäbe eingefahren (%)</label><input id="rea-rod" type="range" data-bind="ins" data-instant min="0" max="100" step="1" value="15"><output data-show="ins" data-fmt="0"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "(not to scale)": "(nicht maßstabsgetreu)",
  "UO₂ pellet, {#} cm": "UO₂-Tablette, {#} cm",
  "about two thirds of the heat leaves through the condenser": "etwa zwei Drittel der Wärme gehen über den Kondensator ab",
  "about {#} pellets in a metal tube": "etwa {#} Tabletten in einem Metallrohr",
  "about {#} rods in a cylinder about {#} m across": "etwa {#} Stäbe in einem Zylinder von etwa {#} m Durchmesser",
  "about {#} tonne of coal (or {#} m³ of gas)": "etwa {#} Tonne Kohle (oder {#} m³ Gas)",
  "about a tonne of coal": "etwa eine Tonne Kohle",
  "assembly": "Brennelement",
  "assembly: {#} rods": "Brennelement: {#} Stäbe",
  "chain reaction stopped; the fuel still gives off afterheat": "Kettenreaktion gestoppt; der Brennstoff gibt noch Nachwärme ab",
  "chain stopped; fuel still warm (afterheat)": "Kette gestoppt; Brennstoff noch warm (Nachwärme)",
  "condenser": "Kondensator",
  "control rods": "Steuerstäbe",
  "core": "Kern",
  "core: {#} assemblies": "Kern: {#} Brennelemente",
  "drag sideways to zoom": "seitlich ziehen zum Zoomen",
  "drag sideways to zoom out": "seitlich ziehen zum Herauszoomen",
  "electric {#} MW": "elektrisch {#} MW",
  "electricity {#} MW": "Strom {#} MW",
  "fuel assembly from above: {#} rods": "Brennelement von oben: {#} Stäbe",
  "fuel rod, about {#} m long": "Brennstab, etwa {#} m lang",
  "fuel rod, ~{#} m": "Brennstab, ~{#} m",
  "gen.": "Gen.",
  "generator": "Generator",
  "heat {#} MW": "Wärme {#} MW",
  "illustration": "Illustration",
  "pellet": "Tablette",
  "reactor": "Reaktor",
  "reactor vessel": "Reaktordruckbehälter",
  "rings: control-rod guide tubes": "Ringe: Führungsrohre der Steuerstäbe",
  "rings: tubes the control rods slide into": "Ringe: Rohre, in die die Steuerstäbe gleiten",
  "rod": "Stab",
  "same heat, roughly": "ungefähr gleiche Wärme",
  "sea or river water": "Meer- oder Flusswasser",
  "steam gen.": "Dampferz.",
  "steam generator": "Dampferzeuger",
  "steam ~{#} °C": "Dampf ~{#} °C",
  "the core from above: {#} assemblies": "der Kern von oben: {#} Brennelemente",
  "the turbine's speed is fixed by the grid; more steam pushes harder": "die Drehzahl der Turbine gibt das Netz vor; mehr Dampf drückt stärker",
  "the water also slows the neutrons": "das Wasser bremst auch die Neutronen",
  "the water carries the heat and slows the neutrons": "das Wasser trägt die Wärme ab und bremst die Neutronen",
  "turbine": "Turbine",
  "turbine speed fixed by the grid; more steam, more push": "Drehzahl vom Netz vorgegeben; mehr Dampf, mehr Kraft",
  "uranium oxide pellet, about {#} cm": "Uranoxidtablette, etwa {#} cm",
  "{#} bar keeps the water liquid at {#} °C": "{#} bar halten das Wasser bei {#} °C flüssig",
  "{#} bar: hot, but no boiling": "{#} bar: heiß, aber kein Sieden",
  "{#} tonne of coal": "{#} Tonne Kohle",
  "{#} °C in": "{#} °C ein",
  "{#} °C out": "{#} °C aus",
  "{#}/{#} of the heat goes to the water": "{#}/{#} der Wärme geht ins Wasser",
  "~{#} pellets inside": "~{#} Tabletten darin",
  "~{#} rods, ~{#} m across": "~{#} Stäbe, ~{#} m Durchmesser",
});
