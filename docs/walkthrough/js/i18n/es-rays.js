/* Spanish: rays (Alfa, beta, gamma y neutrones) */
WT.L.ch.rays = {
  num: "Lección 2", title: "Alfa, beta, gamma y neutrones", short: "Radiación",
  html: `
<div class="step">
  <h3>Cuatro tipos de radiación</h3>
  <p>La radiación <em class="a">alfa</em> es un grupo pesado de dos protones y dos neutrones. La <b>beta</b> es un electrón rápido. La <em class="g">gamma</em> es luz, con demasiada energía para verse. Los <em class="n">neutrones</em> no tienen carga alguna. A cada una la detienen cosas distintas.</p>
</div>
<div class="step">
  <h3>Papel y aluminio</h3>
  <p>Las partículas alfa son grandes y tienen carga, así que chocan con los átomos enseguida: una hoja de papel las detiene. Los electrones beta llegan más lejos, pero unos pocos milímetros de aluminio también los detienen.</p>
  <div class="btns"><button class="btn ghost" data-act="sh_paper" aria-pressed="true">Papel</button><button class="btn ghost" data-act="sh_al" aria-pressed="false">Aluminio</button></div>
</div>
<div class="step">
  <h3>Rayos gamma: a la mitad, nunca a cero</h3>
  <p>Los rayos gamma no tienen carga y casi siempre pasan de largo junto a los átomos. Cada centímetro de plomo da a cada uno la misma probabilidad de ser atrapado, así que cada capa reduce a la mitad lo que queda. El haz se debilita, pero nunca llega del todo a cero.</p>
  <div class="ctl"><label for="ry-pb">Plomo (cm)</label><input id="ry-pb" type="range" data-bind="pb" data-instant min="0" max="5" step="0.1" value="1"><output data-show="pb" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Neutrones: el plomo no basta</h3>
  <p>Un neutrón que rebota en un pesado núcleo de plomo es como una pelota de ping-pong que choca con una bola de bolera: conserva su velocidad. El hidrógeno del agua pesa lo mismo que un neutrón, así que cada choque lo frena, hasta que es lo bastante lento para ser absorbido.</p>
  <div class="btns"><button class="btn ghost" data-act="nm_pb" aria-pressed="true">Plomo</button><button class="btn ghost" data-act="nm_water" aria-pressed="false">Agua</button></div>
  <div class="ctl"><label for="ry-nx">Espesor (cm)</label><input id="ry-nx" type="range" data-bind="nx" data-instant min="0" max="60" step="1" value="30"><output data-show="nx" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Construye un blindaje</h3>
  <p>Apila capas hasta detener los cuatro haces. Los rayos gamma nunca bajan exactamente a cero, solo a una fracción diminuta.</p>
  <div class="btns"><button class="btn ghost" data-act="add_paper">+ Papel</button><button class="btn ghost" data-act="add_al">+ Aluminio</button><button class="btn ghost" data-act="add_pb">+ Plomo</button><button class="btn ghost" data-act="add_water">+ Agua</button><button class="btn" data-act="clear">Quitar</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "alpha": "alfa",
  "beta": "beta",
  "gamma": "gamma",
  "neutron": "neutrón",
  "paper": "papel",
  "aluminium {#} mm": "aluminio {#} mm",
  "Al {#} mm": "Al {#} mm",
  "lead {#} cm": "plomo {#} cm",
  "water {#} cm": "agua {#} cm",
  "no shield": "sin blindaje",
  "stopped": "detenido",
  "all through": "pasa todo",
  "{#} % through": "pasa el {#} %",
  "{#} in {#}": "{#} de {#}",
  "{#} in {#} million": "{#} de {#} millones",
  "{#} in a billion": "{#} de mil millones",
  "drag ↔": "arrastra ↔",
  "all four stopped": "los cuatro detenidos",
  "all four beams stopped": "los cuatro haces detenidos",
  "flash = stopped inside the shield": "destello = detenido en el blindaje",
  "each source fires a steady beam": "cada fuente emite un haz continuo",
  "flash = stopped": "destello = detenido",
  "four beams": "cuatro haces",
  "not to scale": "no a escala",
  "gamma rays (caesium{#})": "rayos gamma (cesio{#})",
  "cm of lead": "cm de plomo",
  "share still going": "fracción que sigue",
  "through: all · halved every {#} mm": "pasa: todo · mitad cada {#} mm",
  "through: {#} % · halved every {#} mm": "pasa: {#} % · mitad cada {#} mm",
  "through: {#} in {#} · halved every {#} mm": "pasa: {#} de {#} · mitad cada {#} mm",
  "gets through: {#} % · halved every {#} mm of lead": "atraviesa: {#} % · se reduce a la mitad cada {#} mm de plomo",
  "gets through: {#} in {#} · halved every {#} mm of lead": "atraviesa: {#} de {#} · se reduce a la mitad cada {#} mm de plomo",
  "counted: {#} of {#}": "contados: {#} de {#}",
  "through {#} % · back {#} % · caught {#} %": "pasan {#} % · vuelven {#} % · capturados {#} %",
  "got through {#} % · bounced back {#} % · slowed and caught {#} %": "atraviesan {#} % · rebotan hacia atrás {#} % · frenados y capturados {#} %",
  "bright = fast · dim = slowed": "brillante = rápido · tenue = frenado",
  "bright = fast neutron · red = hydrogen nucleus knocked away · green flash = swallowed": "brillante = neutrón rápido · rojo = núcleo de hidrógeno expulsado · destello verde = absorbido",
  "simplified model": "modelo simplificado",
});
