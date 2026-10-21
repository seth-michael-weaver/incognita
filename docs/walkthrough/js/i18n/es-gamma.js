/* Spanish: gamma (Chapter 7, photon emission) */
WT.es.ch.gamma = {
  num: "Capítulo 7", title: "Desprender luz", short: "Fotones",
  lead: "Cuando ninguna partícula puede salir, o simplemente ninguna sale, el núcleo se enfría emitiendo fotones: rayos gamma, partículas de luz de altísima energía. Esta salida está abierta a cualquier energía.",
  html: `
<div class="step">
  <p>La imagen vuelve a mostrar la escalera de energía, con un estado caliente que brilla a 8 MeV (millones de electronvoltios). Desprende fotones (γ); cada uno se lleva la energía del salto, <i>E<sub>γ</sub></i>, y deja al núcleo en un estado más bajo. Por debajo de 2 MeV los estados son unos pocos peldaños con nombre; por encima, son una multitud que se espesa rápidamente con la energía (los puntos grises). Cada fotón se dibuja más grueso y brillante en proporción a <i>E<sub>γ</sub></i>³, que crece rápidamente con la energía del fotón (para fotones dipolares, el tipo más común).</p>
  <div class="formula">T<sub>γ</sub>(E<sub>γ</sub>) = 2π · E<sub>γ</sub><sup>2l+1</sup> · f(E<sub>γ</sub>)</div>
  <p>Aquí <i>T<sub>γ</sub></i> es el coeficiente de transmisión del fotón (el factor de “cuán abierta está la puerta” del capítulo 6), <i>l</i> = 1 para fotones dipolares, y <i>f</i>(<i>E<sub>γ</sub></i>) es la <b>función de fuerza gamma</b>, la facilidad con que el núcleo radia a esa energía. La probabilidad de un salto es <i>T<sub>γ</sub></i> por la multitud de estados donde cae. Los saltos pequeños caen en una multitud grande pero son tenues; los grandes son brillantes pero encuentran pocos estados. El montón junto a la escalera recoge dónde caen.</p>
  <div class="ctl"><label for="gm-e0">Energía inicial</label><input id="gm-e0" type="range" data-bind="E0" min="3" max="9" step="0.5" value="8"><output data-show="E0" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="emit">Emitir 100</button></div>
  <p>El montón alcanza su máximo unos MeV por debajo del inicio: los fotones más probables llevan entre 2 y 4 MeV. Mueve la energía inicial y el máximo se mueve con ella.</p>
</div>
<div class="step">
  <h3>Todo el núcleo vibra</h3>
  <p>A la izquierda, los protones (rayados) y los neutrones (rellenos) del núcleo oscilan unos contra otros. A la derecha está la función de fuerza gamma <i>f</i> a cada energía del fotón, con la altura en escala logarítmica (cada paso hacia arriba es diez veces más). Su gran pico es la <b>resonancia gigante dipolar</b>: todos los protones oscilando contra todos los neutrones. La frecuencia de ese movimiento fija la energía de fotón que el núcleo absorbe y emite con más facilidad.</p>
  <div class="ctl"><label for="gm-a">Número másico A</label><input id="gm-a" type="range" data-bind="A" min="40" max="240" step="1" value="112"><output data-show="A" data-fmt="0"></output></div>
  <p>Arrastra el número másico A, la cantidad de protones más neutrones: la oscilación se hace más lenta en los núcleos pesados. Estos vibran hacia 12 a 14 MeV; los ligeros, cerca de 20. Los fotones de un núcleo que se desexcita llevan solo unos pocos MeV, muy por debajo del pico, así que lo que más importa es la cola sombreada de baja energía.</p>
</div>
<div class="step">
  <h3>La tijera y el upbend</h3>
  <p>La imagen muestra un núcleo deformado como dos balones de rugby, protones (rayados) y neutrones (rellenos). Pueden balancearse uno contra otro como las hojas de unas tijeras. Este <b>modo tijera</b> es una vibración magnética cerca de 3 MeV, y cada oscilación puede emitir un fotón. Una segunda fuente magnética, cerca de 8 MeV, es el <b>spin-flip</b> (inversión de espín): nucleones individuales que invierten su espín (las flechas pequeñas), algo que ocurre con cualquier forma.</p>
  <div class="ctl"><label for="gm-b">Deformación β₂</label><input id="gm-b" type="range" data-bind="beta" min="0" max="0.35" step="0.01" value="0.25"><output data-show="beta" data-fmt="2"></output></div>
  <p>Arrastra la deformación β₂, una medida de cuán estirado está el núcleo (0 es una esfera). Cuanto más estirado, con más fuerza se balancean las hojas y más fotones de tijera salen; una esfera no tiene hojas. A las energías de fotón más bajas la fuerza vuelve a subir: es el <b>upbend</b> (repunte), observado en muchos núcleos medidos como un goteo de fotones blandos. El motor lo hace más débil a medida que el núcleo se deforma.</p>
</div>
<div class="step">
  <h3>Escalera abajo</h3>
  <p>La imagen muestra la escalera con intervalos arriba, donde los estados son demasiado densos para listarlos (capítulo 5), y niveles medidos con nombre abajo (estirados, para que se puedan leer), cada uno con su espín y paridad: un peldaño macizo es paridad +, uno hueco paridad −. Desde un intervalo, el núcleo emite fotones uno tras otro, cada uno cayendo en un intervalo más bajo, hasta llegar a los niveles medidos. A partir de ahí el motor deja de estimar: cada nivel medido decae con probabilidades medidas, llamadas <b>razones de ramificación</b>, y las sigue.</p>
  <div class="btns"><button class="btn" data-act="drop">Soltar una cascada</button></div>
  <p>Pulsa el botón unas cuantas veces. Cada pulsación sigue una historia posible. La parte de arriba cambia cada vez, pero el final siempre sigue uno de unos pocos caminos medidos.</p>
</div>
<div class="step">
  <h3>Repisas que retienen</h3>
  <p>La imagen marca un nivel como especial: el nivel 11/2− a 0,40 MeV. Su espín es tan distinto del de los niveles inferiores que un fotón apenas puede conectarlos, así que vive segundos, horas o incluso años. Un nivel de vida larga como este es un <b>isómero</b>, y lo que cae ahí se queda. El motor trata cualquier nivel que viva más de un segundo como un punto final propio. Cada bola es una cascada, que baja de peldaño en peldaño y desprende un fotón en cada salto; termina en el montón del isómero o en el del estado fundamental.</p>
  <div class="ctl"><label for="gm-j">Espín de entrada</label><input id="gm-j" type="range" data-bind="J0" min="0" max="8" step="1" value="2" data-instant><output id="gm-jout">5/2</output></div>
  <p>Arrastra el espín de entrada, el espín del estado donde empiezan las cascadas, y mira cómo los montones vuelven a empezar. La fracción que termina en el isómero, la <b>razón isomérica</b>, depende de ese espín inicial. Un inicio de espín alto alimenta el isómero de espín alto; un inicio de espín bajo lo esquiva y baja hasta el estado fundamental, el nivel más bajo.</p>
</div>
<div class="step">
  <h3>Captura</h3>
  <p>La imagen muestra un núcleo que acaba de absorber un neutrón lento, con dos puertas de salida, como en el capítulo 6: fotones (arriba) y neutrones (derecha). Por debajo del umbral de neutrones, la energía necesaria para liberar un neutrón, la puerta del fotón es la única. Justo por encima tiene un rival: el neutrón que vuelve a salir. La abertura de cada puerta es su <b>anchura</b>, en eV, que mide lo rápido que el núcleo decae por ella. La anchura del fotón apenas cambia con la energía; la del neutrón crece a medida que el neutrón va más rápido.</p>
  <div class="ctl"><label for="gm-e">Energía del neutrón</label><input id="gm-e" type="range" data-bind="lgE" min="-2" max="3.3" step="0.02" value="0"><output id="gm-eout">1.0 keV</output></div>
  <p>Arrastra la energía del neutrón, de 10 eV a 2 MeV. La <b>captura</b>, escrita (n,γ), significa que el neutrón se queda y sale un fotón: a 10 eV gana casi siempre; por encima de unos pocos keV la puerta del neutrón se ha abierto de par en par y la captura pasa a ser una fracción pequeña. La anchura total del fotón en el umbral se ha medido para cientos de núcleos a partir de sus resonancias, así que el motor contrasta con ella su función de fuerza gamma.</p>
  <div class="aside">En el código: <code>gamma/parameters.py</code> (sistemáticas de la resonancia gigante, spin-flip, tijera y upbend; fuerzas tabuladas), <code>gamma/strength.py</code> (<i>f</i>(E<sub>γ</sub>) para cada multipolo), <code>gamma/transmission.py</code> (T<sub>γ</sub> y la anchura radiativa media), <code>structure/levels.py</code> (razones de ramificación, isómeros), <code>emission/multiple.py</code> (la cascada).</div>
</div>`,
};
Object.assign(WT.es.labels, {
  // scene 1: emit
  "energy ↑": "energía ↑",
  "named levels": "niveles con nombre",
  "a crowd of states": "una multitud de estados",
  "{#} MeV": "{#} MeV",
  "hot state, {#} MeV": "estado caliente, {#} MeV",
  "most photons ≈ {#} MeV": "más frecuentes ≈ {#} MeV",
  "small drops: faint (E³ tiny)": "saltos pequeños: tenues (E³ diminuto)",
  "big drops: bright, but few states to land on": "saltos grandes: brillantes, pero con pocos estados donde caer",
  // scene 2: gdr
  "protons": "protones",
  "neutrons": "neutrones",
  "A = {#}: rings at {#} MeV": "A = {#}: vibra a {#} MeV",
  "peak {#} MeV": "pico {#} MeV",
  "giant resonance at {#} MeV": "resonancia gigante a {#} MeV",
  "width ≈ {#} MeV": "anchura ≈ {#} MeV",
  "decays use this": "la que se usa",
  "shaded: the tail decays use": "sombreado: la cola que se usa",
  "photon energy (MeV) →": "energía del fotón (MeV) →",
  "photon strength f (log scale) ↑": "función de fuerza f (escala log) ↑",
  // scene 3: m1
  "a sphere has no blades: no scissors": "una esfera no tiene hojas: no hay tijera",
  "scissors ≈ {#} MeV: strength {#} % of the most stretched": "tijera ≈ {#} MeV: fuerza al {#} % de la más estirada",
  "spin-flip ≈ {#} MeV: steady, any shape (thick photons)": "spin-flip ≈ {#} MeV: constante, cualquier forma (fotones gruesos)",
  "upbend below {#} MeV: soft photons, plenty at this shape": "upbend bajo {#} MeV: fotones blandos, muchos con esta forma",
  "upbend below {#} MeV: soft photons, fewer at this shape": "upbend bajo {#} MeV: fotones blandos, menos con esta forma",
  "upbend below {#} MeV: soft photons, few at this shape": "upbend bajo {#} MeV: fotones blandos, pocos con esta forma",
  // scene 4: cascade
  "ground state": "estado fundamental",
  "isomer": "isómero",
  "isomer: long-lived": "isómero: vida larga",
  "bins: too dense to list": "intervalos: demasiado densos",
  "one photon at a time": "un fotón cada vez",
  "measured branching ratios": "ramificaciones medidas",
  "▬ parity +   ▭ parity −": "▬ paridad +   ▭ paridad −",
  // scene 5: isomer
  "entrance: J = {#}/{#}": "entrada: J = {#}/{#}",
  "isomer: {#} ({#} %)": "isómero: {#} ({#} %)",
  "ground state: {#} ({#} %)": "estado fundamental: {#} ({#} %)",
  "many cascades: ≈ {#} % isomer": "muchas cascadas: ≈ {#} % isómero",
  "over many cascades from J = {#}/{#}: ≈ {#} % end on the isomer": "en muchas cascadas desde J = {#}/{#}: ≈ {#} % acaban en el isómero",
  // scene 6: capture
  "photon door: {#} eV, barely changes": "puerta del fotón: {#} eV, casi no cambia",
  "captured (n,γ): {#} ({#} %)": "capturados (n,γ): {#} ({#} %)",
  "neutron: {#} eV": "neutrón: {#} eV",
  "neutron door: {#} eV, wider when faster": "puerta del neutrón: {#} eV, más ancha si va más rápido",
  "back out: {#} ({#} %)": "vuelven a salir: {#} ({#} %)",
  "more doors open (target left excited)": "más puertas (blanco excitado)",
  "{#} eV neutrons →": "neutrones de {#} eV →",
  "{#} keV neutrons →": "neutrones de {#} keV →",
  "{#} MeV neutrons →": "neutrones de {#} MeV →",
  "slow neutrons: the photon door wins": "neutrones lentos: gana la puerta del fotón",
  "the neutron door wins; capture takes about {#} %": "gana la puerta del neutrón; la captura se lleva ≈ {#} %",
  "fast: capture is a rare event": "rápidos: la captura es un suceso raro",
});
