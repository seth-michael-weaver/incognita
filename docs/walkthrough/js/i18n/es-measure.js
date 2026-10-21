/* Spanish: measure (chapter 11) */
WT.es.ch.measure = {
  num: "Capítulo 11", title: "Lo que sale", short: "Observables",
  lead: "Todo lo anterior ocurrió dentro del núcleo. Un experimento, un reactor o una estrella solo ven un puñado de números. Este capítulo muestra cómo los reúne el motor.",
  html: `
<div class="step">
  <p>Un haz de neutrones, que llega desde la izquierda, atraviesa una lámina delgada de núcleos. El disco pálido alrededor de cada núcleo es su <b>sección eficaz</b>: el área que un neutrón tiene que acertar para que ocurra una reacción. No es el tamaño real del núcleo. Se mide en barns (10⁻²⁴ cm², más o menos la cara de un núcleo de uranio). La fracción del haz que reacciona es esa área multiplicada por cuántos núcleos encuentra el haz.</p>
  <div class="ctl"><label for="mea-e">Energía del neutrón (MeV)</label><input id="mea-e" type="range" data-bind="E" min="0.1" max="20" step="0.1" value="2"><output data-show="E" data-fmt="1"></output></div>
  <p>Baja la energía y los discos se hinchan: un neutrón lento se comporta como una onda ancha, así que puede reaccionar desde más lejos. A alta energía el disco se encoge hacia el tamaño del propio núcleo.</p>
</div>
<div class="step">
  <h3>Con la energía se abren nuevas salidas</h3>
  <p>Cada puerta alrededor del núcleo es una salida, o <b>canal</b>: el neutrón rebota hacia fuera (elástico), deja el blanco excitado (n′, inelástico), arranca un segundo o un tercer neutrón (2n, 3n), es capturado y solo salen fotones (γ), o en su lugar sale un protón o una partícula α. Una puerta con candado tiene un <b>umbral</b>: la reacción cuesta más energía de la que trae el neutrón. La franja de abajo marca dónde se abre cada puerta.</p>
  <div class="ctl"><label for="mea-e2">Energía del neutrón (MeV)</label><input id="mea-e2" type="range" data-bind="E" min="0.1" max="20" step="0.1" value="2"><output data-show="E" data-fmt="1"></output></div>
  <p>Arrastra la energía más allá de un umbral y esa puerta se abre con un destello. Las partículas salen por cada puerta a un ritmo fijado por su fracción, y los cubos de abajo se llenan según esas fracciones; cada puerta nueva les quita parte a las demás. La dispersión inelástica se abre en el primer nivel excitado, un segundo neutrón cuesta unos 7,5 MeV, un tercero unos 14. Los umbrales salen de masas medidas; las fracciones, de la competencia del capítulo 6.</p>
</div>
<div class="step">
  <h3>Lo que ve un detector</h3>
  <p>Un experimento no puede observar el núcleo. Envía el haz en pulsos, y un anillo de detectores alrededor del blanco cronometra el vuelo de cada neutrón: los rápidos llegan primero, los lentos después, así que el tiempo de llegada da la energía. Cada mitad del anillo forma un montón de neutrones ordenados por energía.</p>
  <div class="ctl"><label for="mea-ein">Energía incidente (MeV)</label><input id="mea-ein" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="30"><output data-show="Ein" data-fmt="0"></output></div>
  <p>Los dos montones muestran una joroba de neutrones lentos en torno a 1 a 2 MeV. Son neutrones <b>evaporados</b>: se desprenden del núcleo compuesto después de que la energía se ha repartido entre todos sus nucleones, y salen igual en todas las direcciones. Solo el montón delantero tiene una larga cola de neutrones rápidos. Estos salen de las primeras colisiones, antes de que la energía se reparta, y todavía se mueven más o menos en la dirección del haz: la parte de <b>preequilibrio</b>. Sube la energía incidente y la cola crece.</p>
</div>
<div class="step">
  <h3>Hacia dónde van</h3>
  <p>La forma de pétalo muestra cuántos neutrones salen en cada dirección; el haz llega desde la izquierda. Los neutrones evaporados han olvidado la dirección del haz y salen por igual en todas direcciones. Los rápidos de preequilibrio la recuerdan y se inclinan hacia delante. La regla de Kalbach lo describe: una sola pendiente <i>a</i>, que crece con la energía de salida, fija cuánto se inclinan hacia delante. El motor se detiene en cuántas partículas salen con cada energía; no calcula sus direcciones.</p>
  <div class="ctl"><label for="mea-eo">Energía de salida (MeV)</label><input id="mea-eo" type="range" data-bind="Eout" min="1" max="45" step="0.5" value="25"><output data-show="Eout" data-fmt="1"></output></div>
  <p>Baja la energía de salida y el pétalo se redondea: los neutrones lentos son sobre todo evaporados.</p>
  <div class="formula">dσ/dΩ ∝ e<sup>a cos θ</sup></div>
</div>
<div class="step">
  <h3>En una estrella</h3>
  <p>Dentro de una estrella los neutrones forman un gas caliente entre los núcleos del blanco. Sus velocidades siguen una distribución de Maxwell fijada por la temperatura, expresada como una energía <i>kT</i> (30 keV son unos 350 millones de grados). Cuanto más larga es la estela de un neutrón, más rápido se mueve. Cada vez que pasa junto a un núcleo puede ser capturado, un destello, con una probabilidad que fija la sección eficaz a su energía.</p>
  <div class="ctl"><label for="mea-kt">Temperatura kT (keV)</label><input id="mea-kt" type="range" data-bind="kT" min="5" max="100" step="1" value="30"><output data-show="kT" data-fmt="0"></output></div>
  <p>Cada neutrón capturado cae al montón de abajo, según su energía. El montón es la ventana que cuenta: los neutrones lentos se capturan con facilidad pero son pocos y pasan rara vez, los más rápidos son escasos, así que la mayoría de las capturas vienen de una franja en torno a unos pocos <i>kT</i>. La tasa de captura sobre todo el gas es la <b>sección eficaz promediada sobre Maxwell</b> (MACS), aquí en milibarns (mb). Calienta el gas y la ventana se desplaza a energías más altas, donde el núcleo es un blanco más pequeño. El motor da la sección eficaz de captura; el promedio sobre el gas se hace después, a partir de esa curva.</p>
</div>
<div class="step">
  <h3>El blanco también está caliente</h3>
  <p>Los estantes son los niveles de energía más bajos del blanco, marcados con su espín y su energía, y las bolas muestran qué fracción de los núcleos del blanco está en cada uno a esta temperatura. En una estrella algunos blancos ya están excitados. Más calor significa más núcleos en los estantes de arriba, y un nivel con espín <i>J</i> aloja más porque tiene 2<i>J</i>+1 orientaciones. Cada nivel excitado es una entrada distinta al mismo núcleo compuesto.</p>
  <div class="ctl"><label for="mea-kt2">Temperatura kT (keV)</label><input id="mea-kt2" type="range" data-bind="kT" min="5" max="100" step="1" value="30"><output data-show="kT" data-fmt="0"></output></div>
  <p>Sube la temperatura y mira cómo los núcleos suben. Una tasa estelar completa calcula la reacción desde cada nivel poblado y suma los resultados con estas fracciones; los pesos suman la función de partición <i>G</i>, y el cociente respecto a la tasa desde el estado fundamental solo es el <b>factor de realce estelar</b>. El motor no da este paso: calcula cada reacción con el blanco en su estado fundamental.</p>
</div>
<div class="step">
  <h3>¿Qué grado de certeza tiene todo esto?</h3>
  <p>Los tres mandos son datos de entrada del modelo, cada uno conocido solo con un margen de algunos por ciento: la profundidad del pozo óptico (el potencial que siente el neutrón), la densidad de niveles (cuántos estados hay por MeV) y la intensidad fotónica (la facilidad con que el núcleo emite luz). Cada ejecución del motor los gira a valores aleatorios dentro de esos márgenes y añade un disco tenue, su sección eficaz de captura, a tres energías del neutrón. Leer la dispersión de muchas ejecuciones da una incertidumbre honesta: <b>Monte Carlo total</b>.</p>
  <div class="btns"><button class="btn" data-act="tmc1">Ejecutar una variante</button><button class="btn ghost" data-act="tmc">Ejecutar 10</button><button class="btn ghost" data-act="clear">Borrar</button></div>
  <p>Un borde nítido significa que los datos de entrada fijan la respuesta; un borde difuso, que no. A 10 MeV el pozo óptico también importa y el borde es el más borroso. Ahí es donde nuevas medidas ayudarían más.</p>
  <div class="aside">En el código: <code>emission/channels.py</code> (canales exclusivos y residuales), <code>preeq/</code> y <code>emission/</code> (espectros de emisión), <code>tmc.py</code> (el muestreador de Monte Carlo total). Los promedios de Maxwell se calculan después de la ejecución a partir de las curvas de captura del motor (<code>validation/differential/core.py</code>). Las distribuciones angulares y los blancos excitados térmicamente no se calculan.</div>
</div>`,
};
Object.assign(WT.es.labels, {
  // area
  "each disc: σ ≈ {#} b": "cada disco: σ ≈ {#} b",
  "each disc: cross section σ ≈ {#} b, the area a neutron must hit": "cada disco: sección eficaz σ ≈ {#} b, el área que hay que acertar",
  "beam →": "haz →",
  "nucleus's own face ≈ {#} b · {#} % reacts": "cara del núcleo ≈ {#} b · reacciona el {#} %",
  "the nucleus's own face ≈ {#} b · {#} % of the beam reacts in this foil": "la cara del propio núcleo ≈ {#} b · en esta lámina reacciona el {#} % del haz",
  "slow: the neutron's wave reaches well past the surface": "lento: la onda del neutrón llega mucho más allá de la superficie",
  "the target still looks bigger than the nucleus": "el blanco aún parece mayor que el núcleo",
  "fast: close to the nucleus's own size": "rápido: cerca del tamaño del propio núcleo",
  // doors
  "elastic": "elástico", "n′ inelastic": "n′ inelástico", "{#}n": "{#}n", "γ capture": "captura γ", "p": "p", "α": "α", "n′": "n′",
  "opens at {#} MeV": "se abre a {#} MeV",
  "{#} MeV": "{#} MeV",
  // detect
  "forward half": "mitad delantera", "backward half": "mitad trasera",
  "pulsed beam": "haz pulsado", "pulsed beam →": "haz pulsado →",
  "backward": "atrás", "backward detectors": "detectores traseros",
  "forward": "delante", "forward detectors": "detectores delanteros",
  "outgoing neutron energy from the flight time (MeV) →": "energía del neutrón saliente según el tiempo de vuelo (MeV) →",
  "fast tail": "cola rápida", "fast tail: pre-equilibrium": "cola rápida: preequilibrio",
  "evaporated hump": "joroba evaporada", "hump: evaporated, every way alike": "joroba: evaporados, igual en todas direcciones",
  "{#} % leave before the energy is shared": "el {#} % sale antes de que la energía se reparta",
  // angle
  "beam": "haz",
  "forward-to-backward ratio ≈ {#}  ·  slope a ≈ {#}": "cociente delante/atrás ≈ {#}  ·  pendiente a ≈ {#}",
  "mostly evaporated: every direction alike": "sobre todo evaporados: todas las direcciones por igual",
  "a mix: the fast share leans forward": "una mezcla: la parte rápida se inclina hacia delante",
  "mostly pre-equilibrium: strongly forward": "sobre todo preequilibrio: muy hacia delante",
  "forward →": "delante →",
  // star
  "{#} keV": "{#} keV",
  "kT = {#} keV": "kT = {#} keV",
  "energies of captured neutrons": "energías de los neutrones capturados",
  "each capture drops here, by the neutron's energy: the window that counts": "cada captura cae aquí según la energía del neutrón: la ventana que cuenta",
  "MACS ≈ {#} mb at kT = {#} keV · captures watched: {#}": "MACS ≈ {#} mb a kT = {#} keV · capturas observadas: {#}",
  // hot target
  "{#}⁺  ground state": "{#}⁺  fundamental", "{#}⁺  {#} keV": "{#}⁺  {#} keV",
  "target levels, with the share of nuclei sitting on each": "niveles del blanco, con la fracción de núcleos en cada uno",
  "{#} % start from the ground state · partition function G ≈ {#}": "el {#} % parte del estado fundamental · función de partición G ≈ {#}",
  // TMC
  "optical well": "pozo óptico", "optical well depth": "profundidad del pozo óptico",
  "level density": "densidad de niveles", "photon strength": "intensidad fotónica",
  "σ ≈ {#} b ": "σ ≈ {#} b ", "σ ≈ {#} mb ": "σ ≈ {#} mb ",
  "σ ≈ {#} b ±{#} %": "σ ≈ {#} b ±{#} %", "σ ≈ {#} mb ±{#} %": "σ ≈ {#} mb ±{#} %",
  "dashed: best inputs · each disc drawn at its own scale": "discontinuo: mejores datos · cada disco a su escala",
  "dashed ring: the best-value inputs · each energy drawn at its own scale (disc area ∝ σ)": "anillo discontinuo: datos de mejor valor · cada energía a su propia escala (área ∝ σ)",
  "{#} runs of the engine, each with its inputs nudged at random": "{#} ejecuciones del motor, cada una con sus datos de entrada movidos al azar",
});
