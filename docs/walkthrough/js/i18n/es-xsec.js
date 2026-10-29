/* Spanish: xsec (Chapter 2, what is a cross section?) */
WT.es.ch.xsec = {
  num: "Capítulo 2", title: "¿Qué es una sección eficaz?", short: "Sección eficaz",
  html: `
<div class="step">
  <p>Cada disco es el área blanco de un núcleo: su <b>sección eficaz</b>, que se escribe σ (sigma). La imagen mira desde arriba una lámina fina de núcleos mientras llueven neutrones sobre ella en puntos al azar. Un neutrón que cae dentro de un disco reacciona con ese núcleo (un destello naranja); uno que cae entre los discos pasa de largo (simplemente se desvanece).</p>
  <p>Así, la fracción que reacciona es simplemente la fracción de la lámina que cubren los discos. El pequeño cuadrado negro es la unidad de área, un <b>barn</b>, 10⁻²⁴ cm²: la cara real de un núcleo mide más o menos un barn.</p>
  <div class="ctl"><label for="xs-e1">Energía del neutrón (eV)</label><input id="xs-e1" type="range" data-bind="lgE" data-instant min="-2.3" max="2" step="0.01" value="2"><output data-show="Eshow" data-fmt="2"></output></div>
</div>
<div class="step">
  <p>Los neutrones más lentos ven blancos más grandes. El disco no es el tamaño real del núcleo: es lo grande que parece el núcleo a un neutrón de esta energía, y un neutrón lento pasa más tiempo cerca del núcleo, así que es más probable que sea capturado. En la captura esto hace que σ crezca como 1/velocidad.</p>
  <p>La curva bajo la lámina es σ en todas las energías (las dos escalas son logarítmicas); el punto naranja marca la energía que elegiste. Baja hasta los neutrones más lentos y observa cómo crecen los discos y sube la fracción que reacciona.</p>
  <div class="ctl"><label for="xs-e2">Energía del neutrón (eV)</label><input id="xs-e2" type="range" data-bind="lgE" data-instant min="-2.3" max="2" step="0.01" value="-1.6"><output data-show="Eshow" data-fmt="2"></output></div>
</div>
<div class="step">
  <p>En una resonancia el blanco se hincha. A 7 eV el neutrón y el núcleo juntos tienen exactamente la energía de uno de los niveles del propio núcleo, así que se absorbe con muchísima más facilidad: el disco crece unas cincuenta veces en área, aquí hasta unos 400 barns.</p>
  <p>Aléjate un poco de 7 eV y el disco se encoge de golpe: el pico de la curva es estrecho. Los núcleos reales tienen muchos picos así; el capítulo 1 mostró su código de barras.</p>
  <div class="ctl"><label for="xs-e3">Energía del neutrón (eV)</label><input id="xs-e3" type="range" data-bind="lgE" data-instant min="-2.3" max="2" step="0.005" value="0.845"><output data-show="Eshow" data-fmt="2"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "this square: {#} barn = {#}⁻²⁴ cm²": "este cuadrado: {#} barn = {#}⁻²⁴ cm²",
  "σ: the target area at each energy": "σ: el área blanco a cada energía",
  "σ ≈ {#} b · reacted {#} % · passed through {#} %": "σ ≈ {#} b · reaccionan {#} % · pasan {#} %",
  "each falling dot is a neutron: an orange flash means it hit a disc and reacted, a fading dot passed through": "cada punto que cae es un neutrón: un destello naranja indica que dio en un disco y reaccionó; uno que se desvanece pasó de largo",
});
