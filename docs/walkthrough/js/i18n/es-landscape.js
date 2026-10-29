/* Spanish: landscape (Chapter 4, the landscape of nuclei) */
WT.es.ch.landscape = {
  num: "Capítulo 4", title: "El paisaje de los núcleos", short: "Paisaje",
  lead: "Todos los núcleos que alguien ha producido, en un solo mapa: 3 338 hasta ahora, y solo 252 duran para siempre.",
  html: `
<div class="step">
  <h3>La carta de núclidos</h3>
  <p>Cada cuadradito es un núcleo que se ha observado de verdad en un experimento: los neutrones se cuentan a lo ancho, los protones hacia arriba. Los cuadrados pálidos se han visto, pero su masa aún no se ha pesado, solo estimado. Los cuadrados <b>oscuros</b> son los 252 que nunca se desintegran. Los demás se desmoronan: los naranjas en un parpadeo, los azules solo después de años. La fila <em style="font-style:normal;color:var(--proton);font-weight:600">roja</em> es el elemento que eliges con el deslizador: todos sus isótopos conocidos.</p>
  <div class="ctl"><label for="ls-z">Mirar el elemento (protones Z)</label><input id="ls-z" type="range" data-bind="zSel" data-instant min="1" max="110" step="1" value="26"><output data-show="zSel" data-fmt="0"></output></div>
  <p class="ctl-result" id="ls-z-out" aria-live="polite"></p>
</div>
<div class="step">
  <h3>La energía de ligadura en la carta</h3>
  <p>Ahora cada cuadrado se colorea según su <b>energía de ligadura por nucleón</b>, es decir, con qué fuerza se sujeta cada neutrón o protón (capítulo 3). Los núcleos estables se sitúan a lo largo de una cresta de ligadura fuerte; si te apartas de ella, con demasiados neutrones o demasiados protones, la ligadura baja. La más fuerte de todas es la del níquel-62. Las líneas finas marcan los <b>números mágicos</b> (8, 20, 28, 50, 82, 126), donde los núcleos están especialmente bien ligados.</p>
</div>
<div class="step">
  <h3>Desintegración beta hacia la estabilidad</h3>
  <p>Los núcleos con el mismo número total de nucleones (el mismo <b>número másico</b> A) están sobre una línea diagonal del mapa, mostrada en <em style="font-style:normal;color:var(--proton);font-weight:600">rojo</em>. Empieza con demasiados neutrones, como les ocurre a los fragmentos de un núcleo de uranio partido. En la <b>desintegración beta</b> un neutrón se convierte en protón, de modo que el núcleo avanza un lugar por su línea hacia el centro, más fuertemente ligado, una y otra vez, hasta llegar a la cresta y detenerse. El pequeño gráfico muestra la misma cadena como un valle por el que rueda el núcleo. Prueba A = 137: la cadena pasa por el cesio-137, el producto de larga vida de los accidentes de reactor.</p>
  <div class="ctl"><label for="ls-a">Número másico A</label><input id="ls-a" type="range" data-bind="aSel" data-instant min="8" max="250" step="1" value="137"><output data-show="aSel" data-fmt="0"></output></div>
  <p class="ctl-result" id="ls-a-out" aria-live="polite"></p>
</div>
<div class="step">
  <h3>Cobertura de INCOGNITA</h3>
  <p>El mismo mapa, coloreado según lo que contiene nuestra biblioteca para cada núcleo. <em style="font-style:normal;color:var(--fission);font-weight:600">Verde</em>: evaluado a partir de sus resonancias medidas. El resto tiene un archivo de modelo construido solo por el motor: <b>oscuro</b> para los estables o de vida larga (nivel A), <em style="font-style:normal;color:var(--accent);font-weight:600">azul</em> para más de un día (nivel B), <em style="font-style:normal;color:var(--warm);font-weight:600">naranja</em> para los de vida más corta (nivel C). Los grises no están en la biblioteca (sobre todo los núcleos más ligeros, y unos pocos que el motor no puede ejecutar).</p>
</div>`,
};
