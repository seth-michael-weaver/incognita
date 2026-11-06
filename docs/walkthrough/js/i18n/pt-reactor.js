/* Portuguese (pt-PT): reactor (Como um reator produz eletricidade) */
WT.L.ch.reactor = {
  num: "Lição 1", title: "Como um reator produz eletricidade", short: "Reator",
  html: `
<div class="step">
  <h3>O combustível</h3>
  <p>O urânio é cozido em pastilhas cerâmicas do tamanho da ponta de um dedo, empilhadas em longas varetas metálicas, e as varetas são agrupadas em elementos combustíveis. Uma pastilha dá mais ou menos tanto calor como queimar uma tonelada de carvão.</p>
  <div class="ctl"><label for="rea-z">Afastar</label><input id="rea-z" type="range" data-bind="z" min="0" max="3" step="0.01" value="0"><output data-show="z" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Cindir átomos produz calor</h3>
  <p>No núcleo, os átomos de urânio que se cindem aquecem a água que sobe ao longo das varetas. A mesma água abranda os neutrões para que possam cindir mais átomos. Uma pressão elevada impede-a de ferver, mesmo a 325 °C.</p>
</div>
<div class="step">
  <h3>O vapor faz girar a turbina</h3>
  <p>A água quente passa o seu calor, através de tubos finos, a um segundo circuito, que ferve. O vapor faz girar uma turbina e um alternador, e depois a água fria de um rio ou do mar volta a transformá-lo em água. Cerca de um terço do calor torna-se eletricidade.</p>
</div>
<div class="step">
  <h3>Barras de controlo</h3>
  <p>As barras de controlo absorvem neutrões. Insere-as e cindem-se menos átomos: menos calor, menos vapor, menos eletricidade. Retira-as e a potência sobe.</p>
  <div class="ctl"><label for="rea-rod">Barras de controlo inseridas (%)</label><input id="rea-rod" type="range" data-bind="ins" data-instant min="0" max="100" step="1" value="15"><output data-show="ins" data-fmt="0"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "reactor": "reator",
  "reactor vessel": "vaso do reator",
  "control rods": "barras de controlo",
  "core": "núcleo",
  "steam gen.": "GV",
  "steam generator": "gerador de vapor",
  "turbine": "turbina",
  "gen.": "altern.",
  "generator": "alternador",
  "condenser": "condensador",
  "sea or river water": "água do mar ou do rio",
  "{#} °C out": "saída {#} °C",
  "{#} °C in": "entrada {#} °C",
  "steam ~{#} °C": "vapor ~{#} °C",
  "{#} bar: hot, but no boiling": "{#} bar: quente, mas sem ferver",
  "{#} bar keeps the water liquid at {#} °C": "{#} bar mantêm a água líquida a {#} °C",
  "the water also slows the neutrons": "a água também abranda os neutrões",
  "the water carries the heat and slows the neutrons": "a água transporta o calor e abranda os neutrões",
  "heat {#} MW": "calor {#} MW",
  "electric {#} MW": "elétrica {#} MW",
  "electricity {#} MW": "eletricidade {#} MW",
  "chain stopped; fuel still warm (afterheat)": "cadeia parada; combustível ainda quente (calor residual)",
  "chain reaction stopped; the fuel still gives off afterheat": "reação em cadeia parada; o combustível ainda liberta calor residual",
  "turbine speed fixed by the grid; more steam, more push": "velocidade fixada pela rede; mais vapor, mais força",
  "the turbine's speed is fixed by the grid; more steam pushes harder": "a velocidade da turbina é fixada pela rede; mais vapor empurra com mais força",
  "{#}/{#} of the heat goes to the water": "{#}/{#} do calor vai para a água",
  "about two thirds of the heat leaves through the condenser": "cerca de dois terços do calor saem pelo condensador",
  "illustration": "ilustração",
  "drag sideways to zoom": "arrasta para o lado para afastar",
  "drag sideways to zoom out": "arrasta para o lado para afastar a vista",
  "UO₂ pellet, {#} cm": "pastilha de UO₂, {#} cm",
  "uranium oxide pellet, about {#} cm": "pastilha de óxido de urânio, cerca de {#} cm",
  "{#} tonne of coal": "{#} tonelada de carvão",
  "about {#} tonne of coal (or {#} m³ of gas)": "cerca de {#} tonelada de carvão (ou {#} m³ de gás)",
  "same heat, roughly": "mais ou menos o mesmo calor",
  "fuel rod, ~{#} m": "vareta de combustível, ~{#} m",
  "fuel rod, about {#} m long": "vareta de combustível, com cerca de {#} m",
  "~{#} pellets inside": "~{#} pastilhas lá dentro",
  "about {#} pellets in a metal tube": "cerca de {#} pastilhas num tubo metálico",
  "(not to scale)": "(fora de escala)",
  "assembly: {#} rods": "elemento: {#} varetas",
  "fuel assembly from above: {#} rods": "elemento combustível visto de cima: {#} varetas",
  "rings: control-rod guide tubes": "anéis: tubos-guia das barras",
  "rings: tubes the control rods slide into": "anéis: tubos onde deslizam as barras de controlo",
  "core: {#} assemblies": "núcleo: {#} elementos",
  "the core from above: {#} assemblies": "o núcleo visto de cima: {#} elementos combustíveis",
  "~{#} rods, ~{#} m across": "~{#} varetas, ~{#} m de diâmetro",
  "about {#} rods in a cylinder about {#} m across": "cerca de {#} varetas num cilindro com cerca de {#} m de diâmetro",
  "~51,000 rods, ~3.4 m across": "~51 000 varetas, ~3,4 m de diâmetro",
  "about 51,000 rods in a cylinder about 3.4 m across": "cerca de 51 000 varetas num cilindro com cerca de 3,4 m de diâmetro",
  "pellet": "pastilha",
  "rod": "vareta",
  "assembly": "elemento",
});
