/* Spanish: gamma (Chapter 7, photon emission) */
WT.es.ch.gamma = {
  num: "Capítulo 10", title: "Desprender luz", short: "Fotones",
  lead: "Cuando no sale ninguna partícula, el núcleo se enfría emitiendo fotones: rayos gamma, partículas de luz de alta energía. Esta salida está abierta a cualquier energía.",
  html: `
<div class="step">
  <p>Un estado caliente a 8 MeV (millones de electronvoltios) desprende fotones (γ); el montón junto a la escalera recoge dónde caen. Por debajo de 2 MeV los estados son unos pocos peldaños con nombre; por encima, una multitud que se espesa rápidamente con la energía (puntos grises). Cada fotón se lleva la energía de su salto, <i>E<sub>γ</sub></i>, y se dibuja más brillante en proporción a <i>E<sub>γ</sub></i>³.</p>
  <div class="formula">T<sub>γ</sub>(E<sub>γ</sub>) = 2π · E<sub>γ</sub><sup>2l+1</sup> · f(E<sub>γ</sub>)</div>
  <p><i>T<sub>γ</sub></i> es el coeficiente de transmisión del fotón (la puerta del capítulo 9), <i>l</i> = 1 para fotones dipolares, y <i>f</i> es la <b>función de fuerza gamma</b>: la facilidad con que el núcleo radia a esa energía. La probabilidad de un salto es <i>T<sub>γ</sub></i> por la multitud de estados donde cae: los saltos pequeños encuentran muchos estados pero son tenues; los grandes son brillantes pero encuentran pocos.</p>
  <div class="ctl"><label for="gm-e0">Energía inicial</label><input id="gm-e0" type="range" data-bind="E0" min="3" max="9" step="0.5" value="8"><output data-show="E0" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="emit">Emitir 100</button></div>
  <p>El montón alcanza su máximo unos MeV por debajo del inicio: la mayoría de los fotones llevan de 2 a 4 MeV. Mueve la energía inicial y el máximo la sigue.</p>
</div>
<div class="step">
  <h3>Todo el núcleo vibra</h3>
  <p>El gran pico de la derecha es la <b>resonancia gigante dipolar</b>: todos los protones (rayados, a la izquierda) oscilando contra todos los neutrones (rellenos). Su frecuencia fija la energía de fotón que el núcleo absorbe y emite con más facilidad. La curva es la función de fuerza gamma <i>f</i>, en escala logarítmica (cada paso hacia arriba es diez veces más).</p>
  <div class="ctl"><label for="gm-a">Número másico A</label><input id="gm-a" type="range" data-bind="A" min="40" max="240" step="1" value="112"><output data-show="A" data-fmt="0"></output></div>
  <p>Arrastra el número másico A (protones más neutrones): los núcleos pesados oscilan más despacio y vibran hacia 12 a 14 MeV; los ligeros, cerca de 20. Un núcleo que se desexcita emite fotones de solo unos pocos MeV, así que lo que más importa es la cola sombreada de baja energía.</p>
</div>
<div class="step">
  <h3>La tijera y el upbend</h3>
  <p>Un núcleo deformado también radia de forma magnética: sus protones (rayados) y neutrones (rellenos), dos balones de rugby, se balancean uno contra otro como las hojas de unas tijeras. Este <b>modo tijera</b> está cerca de 3 MeV. El <b>spin-flip</b> (inversión de espín), cerca de 8 MeV, son nucleones individuales que invierten su espín (las flechas pequeñas), con cualquier forma.</p>
  <div class="ctl"><label for="gm-b">Deformación β₂</label><input id="gm-b" type="range" data-bind="beta" min="0" max="0.35" step="0.01" value="0.25"><output data-show="beta" data-fmt="2"></output></div>
  <p>Arrastra la deformación β₂ (0 es una esfera). Cuanto más estirado, más fotones de tijera salen; una esfera no tiene ninguno. A las energías más bajas la fuerza vuelve a subir: es el <b>upbend</b> (repunte), un goteo de fotones blandos, que el motor debilita a medida que el núcleo se deforma. Una opción, desactivada por defecto, usa sistemáticas de tijera más intensas que concuerdan con medidas de Oslo (de cuatro a cinco veces más intensas en el uranio).</p>
</div>
<div class="step">
  <h3>Escalera abajo</h3>
  <p>Una cascada son fotones emitidos uno tras otro, desde los intervalos de arriba (estados demasiado densos para listarlos, capítulo 8) hasta los niveles con nombre, estirados para que se puedan leer (peldaño macizo paridad +, hueco −). Ahí el motor deja de estimar y sigue las <b>razones de ramificación</b> tabuladas: las probabilidades medidas de que cada nivel decaiga a cada uno de los inferiores.</p>
  <div class="btns"><button class="btn" data-act="drop">Soltar una cascada</button></div>
  <p>Pulsa el botón unas cuantas veces: la parte de arriba cambia cada vez; el final sigue uno de unos pocos caminos medidos.</p>
</div>
<div class="step">
  <h3>Repisas que retienen</h3>
  <p>El nivel 11/2− a 0,40 MeV es un <b>isómero</b>: su espín es tan distinto del de los niveles inferiores que un fotón apenas puede conectarlos, así que vive de segundos a años, y lo que cae ahí se queda. El motor trata cualquier nivel que viva más de un segundo como un punto final. Cada bola es una cascada, que termina en el montón del isómero o en el del estado fundamental.</p>
  <div class="ctl"><label for="gm-j">Espín de entrada</label><input id="gm-j" type="range" data-bind="J0" min="0" max="8" step="1" value="2" data-instant><output id="gm-jout">5/2</output></div>
  <p>Arrastra el espín de entrada, donde empiezan las cascadas, y los montones vuelven a empezar. La fracción que termina en el isómero, la <b>razón isomérica</b>, depende de él: un inicio de espín alto alimenta el isómero de espín alto; uno de espín bajo lo esquiva y baja hasta el estado fundamental.</p>
</div>
<div class="step">
  <h3>Captura</h3>
  <p>Un núcleo que acaba de absorber un neutrón lento tiene dos puertas de salida (capítulo 9): fotones (arriba) y el neutrón que vuelve a salir (derecha). La abertura de cada puerta es su <b>anchura</b>, en eV: lo rápido que el núcleo decae por ella. La anchura del fotón apenas cambia; la del neutrón crece con la velocidad del neutrón.</p>
  <div class="ctl"><label for="gm-e">Energía del neutrón</label><input id="gm-e" type="range" data-bind="lgE" min="-2" max="3.3" step="0.02" value="0"><output id="gm-eout">1.0 keV</output></div>
  <p>Arrastra la energía del neutrón, de 10 eV a 2 MeV. La <b>captura</b>, (n,γ), significa que el neutrón se queda y sale un fotón: a 10 eV gana casi siempre y por encima de unos pocos keV pasa a ser una fracción pequeña. La anchura del fotón en el umbral está medida para cientos de núcleos, y sirve para comprobar la función de fuerza gamma. Por defecto el motor usa la suya; una opción escala la función de fuerza de cada núcleo medido hasta que coincidan.</p>
  <div class="aside">En el código: <code>gamma/parameters.py</code> (fuerzas E1 tabuladas; sistemáticas de la resonancia gigante, spin-flip, tijera y upbend), <code>gamma/strength.py</code> (<i>f</i>(E<sub>γ</sub>) para cada multipolo), <code>gamma/transmission.py</code> (T<sub>γ</sub> y la anchura radiativa media), <code>structure/levels.py</code> (razones de ramificación, isómeros), <code>emission/multiple.py</code> (la cascada). Opcionales, desactivadas por defecto: <code>gamma/scissors.py</code> (tijera más intensa), <code>gamma/ggnorm.py</code> (ajustar al ⟨Γγ⟩ medido, hasta el plomo), <code>gamma/actphys.py</code> (ambas, para actínidos).</div>
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
