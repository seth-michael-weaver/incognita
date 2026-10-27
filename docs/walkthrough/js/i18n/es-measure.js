/* Spanish: measure (chapter 11) */
WT.es.ch.measure = {
  num: "Capítulo 17", title: "Lo que sale", short: "Observables",
  lead: "Un experimento, un reactor o una estrella solo ven un puñado de números. Este capítulo muestra cómo el motor convierte lo que pasa dentro del núcleo en esos números.",
  html: `
<div class="step">
  <p>El disco pálido alrededor de cada núcleo es su <b>sección eficaz</b>: el área que un neutrón tiene que acertar para que ocurra una reacción, no el tamaño real del núcleo. Un haz llega desde la izquierda y atraviesa una lámina delgada de núcleos; la fracción que reacciona es esa área por el número de núcleos que encuentra. La unidad es el barn (10⁻²⁴ cm², más o menos la cara de un núcleo de uranio).</p>
  <div class="ctl"><label for="mea-e">Energía del neutrón (MeV)</label><input id="mea-e" type="range" data-bind="E" min="0.1" max="20" step="0.1" value="2"><output data-show="E" data-fmt="1"></output></div>
  <p>Baja la energía y los discos se hinchan: un neutrón lento es una onda ancha y reacciona desde más lejos. A alta energía el disco se encoge hacia el propio núcleo.</p>
</div>
<div class="step">
  <h3>Con la energía se abren nuevas salidas</h3>
  <p>Cada puerta es una salida, o <b>canal</b>: el neutrón rebota hacia fuera (elástico), deja el blanco excitado (n′), arranca más neutrones (2n, 3n), es capturado y solo salen fotones (γ), o en su lugar sale un protón o una partícula α. Una puerta con candado tiene un <b>umbral</b>: la reacción cuesta más energía de la que trae el neutrón.</p>
  <div class="ctl"><label for="mea-e2">Energía del neutrón (MeV)</label><input id="mea-e2" type="range" data-bind="E" min="0.1" max="20" step="0.1" value="2"><output data-show="E" data-fmt="1"></output></div>
  <p>Arrastra la energía más allá de un umbral y esa puerta se abre con un destello; los cubos se llenan según la fracción de cada canal, y cada puerta nueva les quita parte a las demás. Los umbrales salen de las masas de los núcleos; las fracciones, de la competencia del capítulo 9.</p>
</div>
<div class="step">
  <h3>Lo que ve un detector</h3>
  <p>Los dos montones son los neutrones que llegan a la mitad delantera y a la trasera de un anillo de detectores, ordenados por energía. El haz va en pulsos, así que el tiempo de vuelo de cada neutrón da su energía: los rápidos llegan primero.</p>
  <div class="ctl"><label for="mea-ein">Energía incidente (MeV)</label><input id="mea-ein" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="30"><output data-show="Ein" data-fmt="0"></output></div>
  <p>Los dos montones tienen una joroba de neutrones lentos, <b>evaporados</b>: se desprenden del núcleo compuesto una vez repartida la energía, igual en todas las direcciones. Solo el montón delantero tiene una larga cola rápida: neutrones de <b>preequilibrio</b>, que salen de las primeras colisiones moviéndose todavía más o menos con el haz. Sube la energía incidente y la cola crece.</p>
</div>
<div class="step">
  <h3>Hacia dónde van</h3>
  <p>El pétalo muestra cuántos neutrones salen en cada dirección; el haz llega desde la izquierda. Los evaporados han olvidado el haz y salen igual en todas direcciones; los rápidos de preequilibrio se inclinan hacia delante. La regla de Kalbach fija cuánto, con una sola pendiente <i>a</i> que crece con la energía de salida. El motor también puede escribir estas distribuciones angulares, como salida opcional.</p>
  <div class="ctl"><label for="mea-eo">Energía de salida (MeV)</label><input id="mea-eo" type="range" data-bind="Eout" min="1" max="45" step="0.5" value="25"><output data-show="Eout" data-fmt="1"></output></div>
  <p>Baja la energía de salida y el pétalo se redondea: los neutrones lentos son sobre todo evaporados.</p>
  <div class="formula">dσ/dΩ ∝ e<sup>a cos θ</sup></div>
</div>
<div class="step">
  <h3>En una estrella</h3>
  <p>El montón de abajo recoge las energías de los neutrones capturados en el gas caliente de una estrella. Sus velocidades siguen una distribución de Maxwell fijada por la temperatura <i>kT</i> (30 keV son unos 350 millones de grados); las estelas más largas son neutrones más rápidos, y cada paso junto a un núcleo puede acabar en un destello de captura.</p>
  <div class="ctl"><label for="mea-kt">Temperatura kT (keV)</label><input id="mea-kt" type="range" data-bind="kT" min="5" max="100" step="1" value="30"><output data-show="kT" data-fmt="0"></output></div>
  <p>Los neutrones lentos se capturan con facilidad pero pasan rara vez, y los rápidos son pocos, así que la mayoría de las capturas vienen de una ventana de unos pocos <i>kT</i>. La tasa sobre todo el gas es la <b>sección eficaz promediada sobre Maxwell</b> (MACS), en milibarns (mb). Calienta el gas y la ventana se desplaza a energías más altas, donde el blanco es más pequeño. La MACS se obtiene integrando la curva de captura del motor.</p>
</div>
<div class="step">
  <h3>El blanco también está caliente</h3>
  <p>Las bolas muestran qué fracción de los núcleos del blanco está en cada uno de sus niveles más bajos a esta temperatura. En una estrella algunos blancos ya están excitados, y cada nivel excitado es una entrada distinta al mismo núcleo compuesto. Un nivel con espín <i>J</i> aloja más porque tiene 2<i>J</i>+1 orientaciones.</p>
  <div class="ctl"><label for="mea-kt2">Temperatura kT (keV)</label><input id="mea-kt2" type="range" data-bind="kT" min="5" max="100" step="1" value="30"><output data-show="kT" data-fmt="0"></output></div>
  <p>Sube la temperatura y mira cómo los núcleos suben. Una tasa estelar calcula la captura desde cada nivel poblado y suma los resultados con estas fracciones; los pesos suman la función de partición <i>G</i>, y el cociente respecto a la tasa desde el estado fundamental es el <b>factor de realce estelar</b>. El motor puede hacerlo como opción, apagada por defecto; normalmente cada blanco parte de su estado fundamental.</p>
</div>
<div class="step">
  <h3>¿Qué grado de certeza tiene todo esto?</h3>
  <p>Cada disco tenue es una ejecución del motor con sus datos de entrada movidos al azar: la profundidad del pozo óptico, la densidad de niveles y la intensidad fotónica, cada una conocida solo con un margen de algunos por ciento. La dispersión de muchas ejecuciones es una incertidumbre honesta: <b>Monte Carlo total</b>.</p>
  <div class="btns"><button class="btn" data-act="tmc1">Ejecutar una variante</button><button class="btn ghost" data-act="tmc">Ejecutar 10</button><button class="btn ghost" data-act="clear">Borrar</button></div>
  <p>Un borde nítido significa que los datos de entrada fijan la respuesta; un borde difuso, que no, y ahí es donde nuevas medidas ayudarían más.</p>
  <div class="aside">En el código: <code>emission/channels.py</code> (canales exclusivos y residuales), <code>specout.py</code> y <code>specang.py</code> (espectros de salida, distribuciones angulares y secciones eficaces doblemente diferenciales, que solo se escriben si se piden), <code>astro/stellar.py</code> (captura desde niveles del blanco poblados térmicamente, opcional), <code>tmc.py</code> (el muestreador de Monte Carlo total). Las MACS del estado fundamental se obtienen de las curvas de captura en <code>validation/differential/core.py</code>.</div>
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
  "{#}n · {#} MeV": "{#}n · {#} MeV", "p · {#} MeV": "p · {#} MeV", "α · {#} MeV": "α · {#} MeV", "n′ inelastic · {#} MeV": "n′ inelástico · {#} MeV",
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
