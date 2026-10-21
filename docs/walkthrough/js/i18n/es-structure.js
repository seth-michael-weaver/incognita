/* Spanish: structure (Capítulo 1, de qué está hecho un núcleo) */
WT.es.ch.structure = {
  num: "Capítulo 1", title: "De qué está hecho un núcleo", short: "Estructura",
  lead: "Antes de que el motor (nuestro software de reacciones) dispare un solo neutrón, necesita una descripción del núcleo blanco: con cuánta fuerza se mantiene unido, en qué estados de energía puede estar y qué forma tiene.",
  html: `
<div class="step">
  <p>La imagen muestra un núcleo de hierro: una bola compacta de <em class="p">protones</em> y <em class="n">neutrones</em> (<b>nucleones</b>), unidos por la <b>fuerza fuerte</b>, de muy corto alcance. Cada nucleón solo siente a sus vecinos más cercanos, así que todos los núcleos tienen más o menos la misma densidad.</p>
  <div class="ctl"><label for="st-n">Neutrones (el hierro tiene 26 protones)</label><input id="st-n" type="range" data-bind="N" min="24" max="38" step="1" value="30" data-instant><output data-show="N" data-fmt="0"></output></div>
  <p>Arrastra para añadir o quitar neutrones; cada elección es un <b>isótopo</b> distinto. Las barras muestran la <b>energía de ligadura</b> por nucleón en MeV (millones de electronvoltios): la energía necesaria para desarmar el núcleo. Es máxima cerca de los isótopos estables.</p>
</div>
<div class="step">
  <h3>Lo que cuesta sacar uno</h3>
  <p>La energía para sacar una partícula es su <b>energía de separación</b>: <i>S<sub>n</sub></i> para un neutrón, <i>S<sub>p</sub></i> para un protón, <i>S<sub>α</sub></i> para una <b>partícula alfa</b> (dos protones y dos neutrones ligados entre sí). La imagen muestra el núcleo como un pozo, con la energía hacia arriba; cada extracción lleva la partícula de más arriba más allá de la línea discontinua «libre», y el medidor registra el coste.</p>
  <div class="btns"><button class="btn ghost" data-act="pn">Sacar un neutrón</button><button class="btn ghost" data-act="pp">Sacar un protón</button><button class="btn ghost" data-act="pa">Sacar una alfa</button></div>
  <p>El motor obtiene cada una como la diferencia entre dos masas nucleares: medidas donde se puede, de un modelo de masas donde no.</p>
  <div class="ctl"><label for="st-n2">Neutrones</label><input id="st-n2" type="range" data-bind="N" min="24" max="38" step="1" value="30" data-instant><output data-show="N" data-fmt="0"></output></div>
  <p>Arrastra el número de neutrones y vuelve a sacar un neutrón: <i>S<sub>n</sub></i> sube y baja en zigzag, porque los nucleones se emparejan y con un número par el último está más ligado. Una reacción solo puede expulsar una partícula si aporta energía suficiente para pagar ese coste. Estos costes son los <b>umbrales</b> de todo el cálculo.</p>
</div>
<div class="step">
  <h3>Niveles de energía, y la caída</h3>
  <p>Un núcleo solo puede guardar ciertas cantidades exactas de energía extra: las líneas, aquí para el hierro-56, con el <b>estado fundamental</b> abajo. Cada nivel tiene un <b>espín</b> <i>J</i> (momento angular) y una <b>paridad</b>, + o − (si su onda se ve igual en un espejo); 2<sup>+</sup> significa espín 2, paridad +.</p>
  <p>La bola naranja es un núcleo en un nivel alto. Cae nivel a nivel, y cada salto emite un <em class="g">fotón</em> (un rayo gamma) que se lleva la diferencia de energía. El grosor y el porcentaje de los caminos son las probabilidades medidas de cada salto, las <b>razones de ramificación</b>.</p>
  <div class="btns"><button class="btn" data-act="drop">Excitar el núcleo</button></div>
  <p>Púlsalo varias veces: el mismo nivel llega al estado fundamental por rutas distintas. El motor guarda unos treinta niveles medidos por núcleo, con sus probabilidades; más arriba trata los niveles apiñados como un <b>continuo</b> suave. Por encima de la línea discontinua, <i>S<sub>n</sub></i>, el núcleo puede emitir un neutrón.</p>
</div>
<div class="step">
  <h3>Un nivel sin salida fácil</h3>
  <p>Un nivel cuya única salida exige un gran cambio de espín, Δ<i>J</i>, decae muy despacio. A la derecha, 64 núcleos están en un nivel así; cada uno espera un tiempo aleatorio, luego cae y sale un <em class="g">fotón</em>. Pasada una <b>vida media</b>, la mitad ya ha caído.</p>
  <div class="ctl"><label for="st-dj">Cambio de espín ΔJ</label><input id="st-dj" type="range" data-bind="dJ" min="1" max="5" step="1" value="2" data-instant><output data-show="dJ" data-fmt="0"></output></div>
  <div class="ctl"><label for="st-eg">Energía del fotón (MeV)</label><input id="st-eg" type="range" data-bind="Eg" min="0.05" max="1.5" step="0.05" value="0.3"><output data-show="Eg" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="excite">Excitarlos a todos</button></div>
  <p>Sube Δ<i>J</i> y los fotones salen más despacio: cada unidad extra de espín hace la espera cien mil veces más larga o más, y una energía de fotón menor también la alarga (en escala logarítmica). Un nivel que vive más de un segundo, aproximadamente, es un <b>isómero</b>, y el motor lo trata como un punto final, igual que el estado fundamental.</p>
</div>
<div class="step">
  <h3>Redondo, o no</h3>
  <p>Muchos núcleos no son redondos. <i>β₂</i> («beta dos») mide el estiramiento: 0 es una esfera, positivo es estirado como un balón de fútbol americano, negativo es aplastado como un disco. La escalera de la derecha muestra los niveles que produce cada tipo.</p>
  <p>Un núcleo estirado puede rotar, y da los niveles 0<sup>+</sup>, 2<sup>+</sup>, 4<sup>+</sup>, 6<sup>+</sup> con separaciones que crecen como <i>J</i>(<i>J</i>+1): un <b>rotor</b>. Uno redondo puede ondular; cada unidad de ondulación, un <b>fonón</b>, añade la misma energía, así que sus niveles están igualmente espaciados: un <b>vibrador</b>.</p>
  <div class="ctl"><label for="st-beta">Deformación β₂</label><input id="st-beta" type="range" data-bind="beta" min="-0.3" max="0.45" step="0.01" value="0.28"><output data-show="beta" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="still">Quieto</button><button class="btn ghost" data-act="vib">Vibrando</button><button class="btn ghost" data-act="rot">Rotando</button></div>
  <p>Arrastra <i>β₂</i> y pulsa los botones: un estiramiento mayor junta más los niveles del rotor. El motor guarda deformaciones por núcleo y una etiqueta: esférico, vibrador o rotor. El capítulo 3 muestra cómo las usa un neutrón que pasa.</p>
</div>
<div class="step">
  <h3>Huellas justo por encima del umbral</h3>
  <p>Un neutrón lento que se une al blanco cae justo por encima de <i>S<sub>n</sub></i>, en la cajita de la izquierda. El panel de la derecha amplía esa caja miles de veces, con la energía del neutrón de izquierda a derecha.</p>
  <div class="ctl"><label for="st-fe">Energía del haz</label><input id="st-fe" type="range" data-bind="fe" min="0" max="1" step="0.001" value="0.3" data-instant><output id="st-fe-out"></output></div>
  <div class="btns"><button class="btn ghost" data-act="fplay" id="st-fplay">Pausar el barrido</button></div>
  <p>A la mayoría de las energías el haz atraviesa sin más. A ciertas energías exactas, el neutrón más el núcleo coinciden con un nivel escondido y buena parte del haz queda capturada: una <b>resonancia</b>. Luego el núcleo devuelve la energía como un <em class="g">fotón</em> o un neutrón. La curva muestra la fracción capturada; las barras marcan cada resonancia encontrada.</p>
  <div class="btns"><button class="btn ghost" data-act="fFe">Hierro-56</button><button class="btn ghost" data-act="fAu">Oro-197</button><button class="btn ghost" data-act="fU">Uranio-238</button></div>
  <p>Cada núcleo tiene su propio código de barras, a su propia escala: miles de electronvoltios entre las resonancias del hierro, decenas en el oro y el uranio. Tres promedios lo resumen: <i>D₀</i>, la separación media; ⟨Γ<sub>γ</sub>⟩, la <b>anchura fotónica</b>, casi igual en todos los picos; y <i>S₀</i>, la <b>función de fuerza</b>, con qué facilidad entra un neutrón lento.</p>
  <p>Cada uno pone a prueba un paso posterior. Los parámetros de densidad de niveles del motor se ajustaron a <i>D₀</i>, núcleo a núcleo; ⟨Γ<sub>γ</sub>⟩ pone a prueba la emisión de fotones, y <i>S₀</i> el modelo óptico del capítulo siguiente. Para los núcleos no medidos, el motor usa tendencias ajustadas sobre muchos núcleos.</p>
  <div class="aside">En el código: <code>structure/masses.py</code> (masas medidas, masas de modelo más allá de ellas, energías de separación), <code>structure/levels.py</code> (niveles discretos, ramificaciones, isómeros, espines estimados) y <code>levjpar.py</code> (opcional, desactivado por defecto: vuelve a estimar un espín de la lista que es imposible para ese núcleo), <code>structure/deformation.py</code> (β₂ y la etiqueta esférico/vibrador/rotor) y <code>collrule.py</code> (opcional, desactivado por defecto: elige la etiqueta del blanco a partir de sus niveles medidos), <code>structure/resonances.py</code> (D₀, S₀, S₁, ⟨Γγ⟩).</div>
</div>`,
};
(function () {
  const L = {
    // scene: packed drop
    "{#}Fe": "{#}Fe",
    "{#} protons · {#} neutrons": "{#} protones · {#} neutrones",
    "binding energy per nucleon: about {#} MeV": "energía de ligadura por nucleón: unos {#} MeV",
    "binding per nucleon, one bar per isotope →": "ligadura por nucleón, una barra por isótopo →",
    // scene: well
    "free": "libre",
    "free: outside the nucleus": "libre: fuera del núcleo",
    "neutrons": "neutrones",
    "protons": "protones",
    "an alpha forms from the top pairs": "las parejas de arriba forman una alfa",
    "neutron {#}": "neutrón {#}",
    "proton {#}": "protón {#}",
    "alpha {#}": "alfa {#}",
    "n {#}": "n {#}",
    "p {#}": "p {#}",
    "energy paid": "energía pagada",
    "energy to pull": "energía para sacar",
    "(MeV)": "(MeV)",
    "each one out (MeV)": "cada una (MeV)",
    "higher mark =": "marca más alta =",
    "harder to remove": "más difícil de sacar",
    "pulling out a neutron: {#} MeV paid": "sacando un neutrón: {#} MeV pagados",
    "pulling out a proton: {#} MeV paid": "sacando un protón: {#} MeV pagados",
    "pulling out an alpha: {#} MeV paid": "sacando una alfa: {#} MeV pagados",
    // scene: levels and gamma drops
    "continuum: too many levels to list": "continuo: demasiados niveles para listarlos",
    "neutron threshold Sₙ ≈ {#} MeV": "umbral de neutrones Sₙ ≈ {#} MeV",
    "ground state": "estado fundamental",
    "MeV": "MeV",
    "each line: an energy, a spin J and a parity (±)": "cada línea: una energía, un espín J y una paridad (±)",
    "path width and % = measured odds of each hop": "grosor del camino y % = probabilidad medida de cada salto",
    // scene: isomer
    "ground": "fundamental",
    "J = {#}/{#}": "J = {#}/{#}",
    "ΔJ = {#}": "ΔJ = {#}",
    "still excited: {#} of {#}": "aún excitados: {#} de {#}",
    "longer than a second: an isomer, a stop in its own right": "más de un segundo: un isómero, una parada por derecho propio",
    "shown slowed down (log scale)": "mostrado a cámara lenta (escala log.)",
    "shown slowed down: the slower they pop, the longer the real wait (log scale)": "a cámara lenta: cuanto más despacio salen, más larga es la espera real (escala log.)",
    // scene: shape
    "ripples at the surface: a vibrator": "ondula en la superficie: un vibrador",
    "stretched and rotating: a rotor": "estirado y rotando: un rotor",
    "round: a sphere": "redondo: una esfera",
    "stretched (prolate): a football": "estirado (prolato): un balón",
    "squashed: an oblate disc": "aplastado: un disco oblato",
    "{#} phonons": "{#} fonones",
    "no regular": "sin patrón",
    "level pattern": "de niveles regular",
    "spacing grows like J(J+{#})": "la separación crece como J(J+{#})",
    "equal steps, one phonon each": "pasos iguales, un fonón cada uno",
    "its lowest levels": "sus niveles más bajos",
    "β₂ = {#}": "β₂ = {#}",
    // scene: resonance fingerprint
    "continuum": "continuo",
    "Sₙ ≈ {#} MeV": "Sₙ ≈ {#} MeV",
    "slow neutron": "neutrón lento",
    "a slow neutron lands here:": "un neutrón lento cae aquí:",
    "lands here": "cae aquí",
    "Sₙ + its kinetic energy": "Sₙ + su energía cinética",
    "×{#} million": "×{#} millones",
    "×{#} thousand": "×{#} mil",
    "magnified": "ampliado",
    "share taken in": "fracción capturada",
    "share of the beam taken in": "fracción del haz capturada",
    "{#} (Sₙ)": "{#} (Sₙ)",
    "{#} = exactly Sₙ": "{#} = justo Sₙ",
    "{#} keV": "{#} keV",
    "{#} eV": "{#} eV",
    "neutron energy →": "energía del neutrón →",
    "neutron's kinetic energy →": "energía cinética del neutrón →",
    "D₀ ≈ {#} keV: the average gap": "D₀ ≈ {#} keV: la separación media",
    "D₀ ≈ {#} eV: the average gap": "D₀ ≈ {#} eV: la separación media",
    "S₀: average peak strength": "S₀: intensidad media de los picos",
    "S₀: how strong the peaks are on average (how easily a neutron gets in)": "S₀: intensidad media de los picos (con qué facilidad entra un neutrón)",
    "⟨Γγ⟩ ≈ {#} eV: photon width": "⟨Γγ⟩ ≈ {#} eV: anchura fotónica",
    "⟨Γγ⟩ ≈ {#} eV: photon width, about the same for every peak": "⟨Γγ⟩ ≈ {#} eV: anchura fotónica, casi igual en todos los picos",
    "⟨Γγ⟩ ≈ {#} eV: a hairline here": "⟨Γγ⟩ ≈ {#} eV: aquí, un hilo",
    "⟨Γγ⟩ ≈ {#} eV: a hairline here; neutrons widen these peaks": "⟨Γγ⟩ ≈ {#} eV: aquí, un hilo; los neutrones ensanchan estos picos",
    "peaks drawn about {#}× wider than life so they show": "picos dibujados unos {#}× más anchos que en realidad para que se vean",
  };
  // beam readout and per-target labels
  for (const u of ["keV", "eV"]) L[`beam of neutrons at {#} ${u}`] = `haz de neutrones a {#} ${u}`;
  const EL = { iron: "hierro", gold: "oro", uranium: "uranio" };
  for (const en in EL) {
    L[`${en}{#} levels`] = `niveles del ${EL[en]}{#}`;
    L[`${en}{#}: took in {#} of the last {#}`] = `${EL[en]}{#}: capturó {#} de los últimos {#}`;
  }
  // isomer half-life in every unit fmtTime can produce
  const TU = { femtoseconds: "femtosegundos", picoseconds: "picosegundos", nanoseconds: "nanosegundos", microseconds: "microsegundos",
    milliseconds: "milisegundos", seconds: "segundos", minutes: "minutos", hours: "horas", days: "días", years: "años" };
  for (const en in TU) L[`half-life about {#} ${en}`] = `vida media de unos {#} ${TU[en]}`;
  L["half-life about {#}×{#}^{#} years"] = "vida media de unos {#}×{#}^{#} años";
  Object.assign(WT.es.labels, L);
})();
