/* Spanish: structure (Capítulo 1, de qué está hecho un núcleo) */
WT.es.ch.structure = {
  num: "Capítulo 1", title: "De qué está hecho un núcleo", short: "Estructura",
  lead: "Antes de que el motor (nuestro software de reacciones) dispare un solo neutrón, necesita una descripción del núcleo blanco: con cuánta fuerza se mantiene unido, en qué estados de energía puede estar y qué forma tiene.",
  html: `
<div class="step">
  <p>La imagen muestra un núcleo de hierro: una bola compacta de <em class="p">protones</em> y <em class="n">neutrones</em>, llamados en conjunto <b>nucleones</b>. La <b>fuerza fuerte</b>, una atracción de muy corto alcance entre nucleones, los mantiene unidos. Cada nucleón solo siente a sus vecinos más cercanos, así que la bola tiene más o menos la misma densidad sea cual sea su tamaño.</p>
  <div class="ctl"><label for="st-n">Neutrones (el hierro tiene 26 protones)</label><input id="st-n" type="range" data-bind="N" min="24" max="38" step="1" value="30" data-instant><output data-show="N" data-fmt="0"></output></div>
  <p>Arrastra para añadir o quitar neutrones. Cada elección es un <b>isótopo</b> distinto: el mismo elemento con otro número de neutrones. La <b>energía de ligadura</b> es la energía necesaria para desarmar el núcleo entero, en MeV (millones de electronvoltios, la unidad de energía habitual para los núcleos). Las barras de abajo la muestran por nucleón. Es máxima cerca de los isótopos estables y cae a ambos lados.</p>
</div>
<div class="step">
  <h3>Lo que cuesta sacar uno</h3>
  <p>Ahora la imagen muestra el núcleo como un pozo, con la energía hacia arriba. Los neutrones (izquierda) y los protones (derecha) se sientan por parejas en niveles dentro de él. La línea discontinua de arriba significa «libre»: fuera del núcleo. Una línea discontinua levanta la partícula de más arriba y la saca, y el medidor de la derecha se llena con la energía pagada. Esa subida es la <b>energía de separación</b>: <i>S<sub>n</sub></i> para un neutrón, <i>S<sub>p</sub></i> para un protón, <i>S<sub>α</sub></i> para una <b>partícula alfa</b> (un grupo compacto de dos protones y dos neutrones, que recupera buena parte de su coste al ligarse entre sí). Cada extracción deja una marca en el medidor: cuanto más alta la marca, más difícil es sacar esa partícula.</p>
  <div class="btns"><button class="btn ghost" data-act="pn">Sacar un neutrón</button><button class="btn ghost" data-act="pp">Sacar un protón</button><button class="btn ghost" data-act="pa">Sacar una alfa</button></div>
  <p>El motor usa energías de separación, no la ligadura total. Cada una es la diferencia entre dos masas nucleares: medidas donde se puede, tomadas de un modelo de masas donde no.</p>
  <div class="ctl"><label for="st-n2">Neutrones</label><input id="st-n2" type="range" data-bind="N" min="24" max="38" step="1" value="30" data-instant><output data-show="N" data-fmt="0"></output></div>
  <p>Arrastra el número de neutrones y vuelve a sacar un neutrón: <i>S<sub>n</sub></i> sube y baja en zigzag. A los nucleones les gusta emparejarse, así que con un número par de neutrones el último está más ligado. Una reacción solo puede expulsar una partícula si aporta energía suficiente para pagar su energía de separación. Estos costes son los <b>umbrales</b> de todo el cálculo.</p>
</div>
<div class="step">
  <h3>Niveles de energía, y la caída</h3>
  <p>La imagen muestra los niveles de energía del hierro-56 como líneas horizontales, con la energía hacia arriba. La línea de abajo es el <b>estado fundamental</b>: el núcleo sin energía extra. Un núcleo solo puede guardar ciertas cantidades exactas de energía extra, una por línea, como estantes en los que puede posarse pero nunca entre ellos. Cada nivel tiene un <b>espín</b> <i>J</i> (cuánto momento angular lleva el núcleo) y una <b>paridad</b>, + o − (si su onda cuántica se ve igual en un espejo). La etiqueta 2<sup>+</sup> significa espín 2, paridad +.</p>
  <p>La bola naranja es un núcleo que quedó en un nivel alto. Cae nivel a nivel, y cada salto emite un <em class="g">fotón</em> (una partícula de luz, aquí un rayo gamma) que se lleva la diferencia de energía. Los caminos curvos muestran adónde puede saltar después; su grosor y su porcentaje son las probabilidades medidas, llamadas <b>razones de ramificación</b>.</p>
  <div class="btns"><button class="btn" data-act="drop">Excitar el núcleo</button></div>
  <p>Púlsalo varias veces: el mismo nivel de partida llega al estado fundamental por rutas distintas. El motor guarda unos treinta niveles medidos por núcleo, con estas probabilidades. Más arriba los niveles se apiñan tanto que se confunden, y el motor los trata como un <b>continuo</b> suave. La línea discontinua de arriba es <i>S<sub>n</sub></i>: por encima, el núcleo tiene energía suficiente para emitir un neutrón.</p>
</div>
<div class="step">
  <h3>Un nivel sin salida fácil</h3>
  <p>A la derecha hay 64 núcleos, todos en el mismo nivel excitado (brillando). Cada uno espera un tiempo aleatorio, luego cae al estado fundamental y sale un <em class="g">fotón</em>. Pasada una <b>vida media</b>, la mitad ya ha caído. A la izquierda está el nivel en el que se encuentran: su única salida lleva a un nivel de espín muy distinto, así que el fotón debe llevarse la diferencia de espín, Δ<i>J</i>. Un fotón que lleva mucho espín se emite muy despacio.</p>
  <div class="ctl"><label for="st-dj">Cambio de espín ΔJ</label><input id="st-dj" type="range" data-bind="dJ" min="1" max="5" step="1" value="2" data-instant><output data-show="dJ" data-fmt="0"></output></div>
  <div class="ctl"><label for="st-eg">Energía del fotón (MeV)</label><input id="st-eg" type="range" data-bind="Eg" min="0.05" max="1.5" step="0.05" value="0.3"><output data-show="Eg" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="excite">Excitarlos a todos</button></div>
  <p>Sube Δ<i>J</i> y los fotones salen más despacio: cada unidad extra de espín hace la espera cien mil veces más larga o más. Una energía de fotón menor la alarga aún más. (Los tiempos reales van de femtosegundos a años, así que la pantalla los estira en escala logarítmica.) Un nivel que vive más de un segundo, aproximadamente, se llama <b>isómero</b>. El motor trata los isómeros como puntos finales por derecho propio, como el estado fundamental.</p>
</div>
<div class="step">
  <h3>Redondo, o no</h3>
  <p>El núcleo de la izquierda está estirado como un balón de fútbol americano, y se queda quieto hasta que pulses un botón. Muchos núcleos no son redondos. El número <i>β₂</i> («beta dos») mide el estiramiento: 0 es una esfera, positivo es estirado a lo largo de un eje, negativo es aplastado como un disco. La escalera de la derecha muestra los niveles que produce cada tipo de núcleo.</p>
  <p>Un núcleo estirado puede rotar. Una rotación más rápida da los niveles 0<sup>+</sup>, 2<sup>+</sup>, 4<sup>+</sup>, 6<sup>+</sup>, con separaciones que crecen como <i>J</i>(<i>J</i>+1). Esto es un <b>rotor</b>. Un núcleo redondo, en cambio, puede ondular en su superficie. Cada unidad de ondulación, un <b>fonón</b>, añade la misma energía, así que sus niveles están igualmente espaciados. Esto es un <b>vibrador</b>.</p>
  <div class="ctl"><label for="st-beta">Deformación β₂</label><input id="st-beta" type="range" data-bind="beta" min="-0.3" max="0.45" step="0.01" value="0.28"><output data-show="beta" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="still">Quieto</button><button class="btn ghost" data-act="vib">Vibrando</button><button class="btn ghost" data-act="rot">Rotando</button></div>
  <p>Arrastra <i>β₂</i> y pulsa los botones. Un estiramiento mayor junta más los niveles del rotor. El motor guarda un <i>β₂</i> por núcleo y una etiqueta que dice si sus niveles bajos parecen de rotor o de vibrador. El capítulo 3 muestra cómo un neutrón que pasa usa ambas cosas.</p>
</div>
<div class="step">
  <h3>Huellas justo por encima del umbral</h3>
  <p>A la izquierda está la escalera de niveles del núcleo que se forma cuando un neutrón se une al blanco, hasta más allá de <i>S<sub>n</sub></i>. Un neutrón lento cae en la cajita: en <i>S<sub>n</sub></i> más su propia energía cinética. El panel de la derecha es esa caja ampliada miles de veces, con la energía del neutrón de izquierda a derecha.</p>
  <div class="ctl"><label for="st-fe">Energía del haz</label><input id="st-fe" type="range" data-bind="fe" min="0" max="1" step="0.001" value="0.3" data-instant><output id="st-fe-out"></output></div>
  <div class="btns"><button class="btn ghost" data-act="fplay" id="st-fplay">Pausar el barrido</button></div>
  <p>Un haz de neutrones, todos a la energía del marcador, vuela hacia el núcleo. A la mayoría de las energías lo atraviesan sin más. A ciertas energías exactas, el neutrón más el núcleo coinciden con uno de los niveles escondidos en la caja, y buena parte del haz queda capturada. Eso es una <b>resonancia</b>. Luego el núcleo devuelve la energía como un <em class="g">fotón</em> o vuelve a expulsar un neutrón. La curva registra la fracción capturada mientras la energía hace el barrido; las barras debajo marcan cada resonancia encontrada: la huella dactilar del núcleo. Medir cuánto tardan los neutrones en volar hasta una muestra mide exactamente esto.</p>
  <div class="btns"><button class="btn ghost" data-act="fFe">Hierro-56</button><button class="btn ghost" data-act="fAu">Oro-197</button><button class="btn ghost" data-act="fU">Uranio-238</button></div>
  <p>Cada núcleo tiene su propio código de barras, a su propia escala: miles de electronvoltios entre las resonancias del hierro, decenas en el oro y el uranio. Tres promedios lo resumen. <i>D₀</i> es la separación media entre resonancias. ⟨Γ<sub>γ</sub>⟩, la <b>anchura fotónica</b>, es lo ancho que es un pico porque el nivel pierde su energía en forma de luz; es casi igual para todos los picos. <i>S₀</i>, la <b>función de fuerza</b>, es lo intensos que son los picos en promedio: con qué facilidad entra un neutrón lento.</p>
  <p>Cada uno calibra un paso posterior. <i>D₀</i> fija lo rápido que crece el número de niveles con la energía, núcleo a núcleo. ⟨Γ<sub>γ</sub>⟩ pone a prueba la emisión de fotones. <i>S₀</i> es un objetivo para el modelo óptico del capítulo siguiente. Donde un núcleo nunca se ha medido, el motor usa tendencias ajustadas sobre muchos núcleos.</p>
  <div class="aside">En el código: <code>structure/masses.py</code> (masas medidas, masas de modelo más allá de ellas, energías de separación), <code>structure/levels.py</code> (niveles discretos, ramificaciones, isómeros, espines estimados), <code>structure/deformation.py</code> (β₂ y la etiqueta rotor/vibrador), <code>structure/resonances.py</code> (D₀, S₀, S₁, ⟨Γγ⟩).</div>
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
