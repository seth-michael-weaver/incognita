/* Spanish: doppler (Chapter 20, Doppler broadening) */
WT.es.ch.doppler = {
  num: "Capítulo 20", title: "Ensanchamiento Doppler", short: "Doppler",
  html: `
<div class="step">
  <h3>Agitación térmica del blanco</h3>
  <p>Combustible más caliente: sus átomos se agitan más rápido. Cada átomo de uranio ya no está quieto cuando llega un neutrón.</p>
  <div class="ctl"><label for="dop-t1">Temperatura del combustible (K)</label><input id="dop-t1" type="range" data-bind="T" data-instant min="300" max="1500" step="10" value="600"><output data-show="T" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Ensanchamiento Doppler</h3>
  <p>La curva es la probabilidad de que el uranio-238 capture un neutrón, trazada frente a la energía del neutrón. Su altura es un área blanco en <b>barns</b> (un barn son 10<sup>−24</sup> cm², más o menos el tamaño que un núcleo muestra a un neutrón). Como los átomos se mueven, unos se encuentran con el neutrón de frente y otros huyen de él, así que el pico estrecho se difumina: más bajo y más ancho. Su área no cambia.</p>
  <div class="ctl"><label for="dop-t2">Temperatura del combustible (K)</label><input id="dop-t2" type="range" data-bind="T" data-instant min="300" max="1500" step="10" value="1200"><output data-show="T" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Autoapantallamiento de resonancias</h3>
  <p>Una pastilla de combustible es gruesa. La banda sombreada es la fracción de neutrones que detiene en cada energía. El centro del pico ya detiene todo, en caliente o en frío, así que un pico más bajo no pierde nada ahí; las alas más anchas atrapan más. Se pierden más neutrones por captura en lugar de causar fisión, y <i>k</i> baja por sí sola. (<i>k</i> es cuántas fisiones nuevas provoca cada fisión; el capítulo 21 lo explica.)</p>
  <div class="ctl"><label for="dop-t3">Temperatura del combustible (K)</label><input id="dop-t3" type="range" data-bind="T" data-instant min="300" max="1500" step="10" value="900"><output data-show="T" data-fmt="0"></output></div>
</div>`,
};
