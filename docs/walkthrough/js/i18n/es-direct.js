/* Spanish: direct (Capítulo 6, reacciones directas) */
WT.es.ch.direct = {
  num: "Capítulo 6", title: "Reacciones directas", short: "Reacciones directas",
  lead: "No todo neutrón que llega al núcleo es engullido. Algunos rozan su superficie, le dan un empujón y siguen volando.",
  html: `
<div class="step">
  <p>Un neutrón que solo roza el núcleo puede empujarlo una vez a un nivel excitado y seguir volando, casi siempre hacia delante y solo un poco más lento. Eso es una <b>reacción directa</b>: un solo paso, que termina en unos 10⁻²² segundos. Aquí un neutrón pasa a una distancia <i>b</i>, el <b>parámetro de impacto</b>, en radios nucleares <i>R</i>; el anillo punteado es la piel del núcleo.</p>
  <div class="ctl"><label for="di-b">Puntería b (en radios)</label><input id="di-b" type="range" data-bind="b" min="0" max="1.5" step="0.01" value="1.0"><output data-show="b" data-fmt="2"></output></div>
  <p>Arrastra <i>b</i>. Por debajo de 0,8, más o menos, el neutrón es engullido. Cerca de 1 roza el núcleo y lo deja en su primer nivel excitado, 2⁺. Por encima de 1,2, aproximadamente, no acierta y solo se desvía: <b>dispersión elástica</b>, con el núcleo intacto.</p>
</div>
<div class="step">
  <h3>Excitación rotacional de núcleos deformados</h3>
  <p>Un empujón pone a rotar un núcleo estirado (capítulo 1) y lo sube por la escalera de su <b>banda rotacional</b>: 0⁺, 2⁺, 4⁺, 6⁺, 8⁺. El neutrón puede empujar el núcleo hacia arriba y el núcleo puede devolver el empujón, así que ningún nivel puede calcularse por separado. El motor los resuelve todos a la vez: <b>canales acoplados</b>, donde cada canal es un resultado, aquí un nivel de la banda.</p>
  <div class="btns"><button class="btn" data-act="kick">Subirlo un nivel</button><button class="btn ghost" data-act="rpause">Pausar / seguir</button></div>
  <div class="ctl"><label for="di-beta">Deformación β₂</label><input id="di-beta" type="range" data-bind="beta2" min="0.05" max="0.4" step="0.01" value="0.25"><output data-show="beta2" data-fmt="2"></output></div>
  <p>Los arcos muestran qué niveles están conectados: <i>λ</i> = 2, el estiramiento global, conecta vecinos; <i>λ</i> = 4, un abultamiento más fino, salta dos. Arrastra <i>β₂</i>: un núcleo más estirado conecta sus niveles con más fuerza, y los arcos se engrosan. Como la banda se calcula junto con el neutrón entrante, el motor sabe exactamente cuántos neutrones se lleva y pasa solo el resto a las rutas más lentas de los capítulos siguientes.</p>
</div>
<div class="step">
  <h3>Vibraciones de superficie</h3>
  <p>Un núcleo redondo puede ondular, y la energía de ondulación viene en paquetes iguales llamados <b>fonones</b>. Un fonón de la ondulación balón–disco (<i>λ</i> = 2) da el nivel 2⁺; dos dan tres niveles, 0⁺, 2⁺ y 4⁺, al doble de energía. Llegar a ellos exige dos empujones seguidos. El motor resuelve estos niveles junto con el estado fundamental.</p>
  <div class="ctl"><label for="di-lam">Forma de la onda λ</label><input id="di-lam" type="range" data-bind="lam" min="2" max="3" step="1" value="2" data-instant><output data-show="lam" data-fmt="0"></output></div>
  <div class="btns"><button class="btn ghost" data-act="ph1">Un fonón</button><button class="btn ghost" data-act="ph2">Dos fonones</button></div>
  <p>Pon <i>λ</i> = 3 para una ondulación en forma de pera, cuyo primer nivel es 3⁻. Pulsa los botones para añadir uno o dos fonones.</p>
</div>
<div class="step">
  <h3>Reacciones directas de un solo paso</h3>
  <p>Para la mayoría de los niveles la conexión es débil y basta un empujón: la <b>DWBA</b> (aproximación de Born de ondas distorsionadas). La onda entrante del capítulo 5 empuja el núcleo una vez, en el borde, donde el potencial cae de profundo a cero; el borde brilla donde lo golpean las crestas. La onda circular que sale son los neutrones que dejaron el núcleo excitado.</p>
  <div class="ctl"><label for="di-bd">Deformación del nivel β</label><input id="di-bd" type="range" data-bind="bd" min="0.02" max="0.4" step="0.01" value="0.2"><output data-show="bd" data-fmt="2"></output></div>
  <p>Arrastra <i>β</i>: el borde tiembla más y los círculos brillan más, como <i>β</i>²: el doble de deformación, cuatro veces más. El motor toma el <i>β</i> de cada nivel de valores medidos, o de sistemáticas donde no se conoce. Cómo se reparten en ángulo los neutrones dispersados es una salida extra opcional.</p>
</div>
<div class="step">
  <h3>Resonancias gigantes</h3>
  <p>Todos los nucleones pueden moverse juntos: respirar, aplastarse y estirarse, u oscilar hacia una forma de pera. Son las <b>resonancias gigantes</b>. En este núcleo de masa media se sitúan entre unos 7 y 25 MeV, cada una con varios MeV de ancho, demasiado anchas para contar como un solo nivel; las jorobas marcan la <b>energía de excitación</b> de cada una.</p>
  <p>El motor fija la intensidad total de cada una con una <b>regla de suma</b>, un límite de la física básica a la fuerza con que un núcleo puede responder, y la reparte como una joroba por encima del último nivel conocido. Estas jorobas, más los empujones a niveles altos, forman el <b>continuo colectivo</b>.</p>
  <div class="btns"><button class="btn ghost" data-act="mono">Respiración</button><button class="btn ghost" data-act="quad">Aplastamiento</button><button class="btn ghost" data-act="oct">Pera</button></div>
  <p>La más conocida, los protones oscilando contra los neutrones (la resonancia gigante dipolar), sobre todo absorbe y emite luz, así que pertenece al capítulo 10.</p>
</div>
<div class="step">
  <h3>Captura directa</h3>
  <p>Un neutrón libre puede caer directamente en una <b>órbita</b> vacía del pozo (una energía permitida para un neutrón dentro) y enviar la energía sobrante como un <em class="g">fotón</em>. El núcleo nunca se calienta. Esto es la <b>captura directa</b>. El motor puede calcularla con el mismo pozo del capítulo 5: la onda libre fuera, la órbita ligada dentro y el fotón que las conecta. Es opcional y está desactivada por defecto.</p>
  <div class="btns"><button class="btn" data-act="drop">Dejar caer un neutrón</button></div>
  <p>La captura directa importa sobre todo donde la ruta habitual, repartir la energía del neutrón, es débil: núcleos ligeros y núcleos lejos de la estabilidad, con pocos niveles y muy separados.</p>
</div>
<div class="step">
  <h3>Flujo directo frente a flujo compuesto</h3>
  <p>El motor reparte la sección eficaz de reacción del capítulo 5 en orden: primero las reacciones directas, luego las colisiones rápidas, y solo lo que queda forma un núcleo compuesto. En la imagen cada neutrón acaba en uno de tres destinos: <b>directo</b> (roza y sigue), rápido (arranca un nucleón antes de que la energía se reparta: <b>preequilibrio</b>, capítulo 7) o engullido (un <b>núcleo compuesto</b>, capítulo 8). Los montones los cuentan.</p>
  <div class="ctl"><label for="di-e">Energía del neutrón (MeV)</label><input id="di-e" type="range" data-bind="E" min="1" max="60" step="0.5" value="14"><output data-show="E" data-fmt="1"></output></div>
  <p>Arrastra la energía y mira cómo se vuelven a llenar los montones. A unos pocos MeV casi todos los neutrones son engullidos. A decenas de MeV, las reacciones directas y las colisiones rápidas juntas se llevan una gran parte.</p>
  <div class="aside">En el código: <code>ecis/formfactor.py</code>, <code>ecis/coupling.py</code>, <code>ecis/solver.py</code> (potencial deformado, canales acoplados para rotores y vibradores), <code>ecis/dwba.py</code> y <code>direct/dwba.py</code> (empujón único, resonancias gigantes, continuo colectivo), <code>direct/racapcalc.py</code> (captura directa, opcional, desactivada por defecto), <code>compound/normalization.py</code> (la contabilidad).</div>
</div>`,
};
Object.assign(WT.es.labels, {
  // scene: aim
  "skin (surface)": "piel (superficie)",
  "b = {#} R": "b = {#} R",
  "absorbed: its energy is shared by all nucleons": "absorbido: su energía se reparte entre todos los nucleones",
  "{#}⁺ level": "nivel {#}⁺",
  "one push leaves the nucleus on {#}⁺; neutron flies on": "un empujón deja el núcleo en {#}⁺; el neutrón sigue",
  "a miss: deflected, nucleus unchanged (elastic)": "pasa de largo: desviado, núcleo intacto (elástica)",
  // scene: rotor
  "at rest: {#}⁺": "en reposo: {#}⁺",
  "rotating: {#}⁺": "rotando: {#}⁺",
  "rotating: {#}⁺ (paused)": "rotando: {#}⁺ (en pausa)",
  "λ = {#}": "λ = {#}",
  "levels solved together": "niveles resueltos a la vez",
  // scene: vibrator
  "quadrupole ripple: football ↔ disc": "onda cuadrupolar: balón ↔ disco",
  "octupole ripple: pear ↔ pear": "onda octupolar: pera ↔ pera",
  "{#}⁺  no phonon": "{#}⁺  sin fonón",
  "{#}⁺  one phonon": "{#}⁺  un fonón",
  "{#}⁻  one phonon": "{#}⁻  un fonón",
  "{#}⁺ {#}⁺ {#}⁺  two phonons": "{#}⁺ {#}⁺ {#}⁺  dos fonones",
  "{#}⁺ {#}⁺ {#}⁺ {#}⁺  two phonons": "{#}⁺ {#}⁺ {#}⁺ {#}⁺  dos fonones",
  "one push": "un empujón",
  "two pushes": "dos empujones",
  "two phonons": "dos fonones",
  "equal energy steps": "pasos de energía iguales",
  // scene: DWBA
  "rim: the push happens here": "borde: aquí ocurre el empujón",
  "incoming wave": "onda entrante",
  "outgoing: nucleus left excited": "saliente: núcleo excitado",
  "outgoing circles: the nucleus left on an excited level": "círculos salientes: el núcleo quedó en un nivel excitado",
  "push strength ∝ β²: {#}× that at β = {#}": "intensidad del empujón ∝ β²: {#}× la de β = {#}",
  // scene: giant resonances
  "breathing": "respiración",
  "squash and stretch": "aplastar y estirar",
  "pear": "pera",
  "breathing (monopole)": "respiración (monopolo)",
  "squash and stretch (quadrupole)": "aplastar y estirar (cuadrupolo)",
  "pear-shaped (octupole), low and high": "en forma de pera (octupolo), baja y alta",
  "about {#} MeV up": "a unos {#} MeV",
  "last known level": "último nivel conocido",
  "excitation energy (MeV) →": "energía de excitación (MeV) →",
  // scene: direct capture
  "free: outside the nucleus": "libre: fuera del núcleo",
  "empty orbit": "órbita vacía",
  "drops straight in; a photon carries off the spare energy": "cae directamente; un fotón se lleva la energía sobrante",
  // scene: ledger
  "direct": "directa",
  "fast (pre-eq.)": "rápida (preeq.)",
  "compound": "compuesto",
  "direct: grazed, flew on": "directa: rozó y siguió",
  "fast collision: one out at once": "colisión rápida: uno sale al instante",
  "compound: swallowed": "compuesto: engullido",
  "{#}% (model {#}%)": "{#}% (modelo {#}%)",
  "{#}% seen · model {#}%": "{#}% visto · modelo {#}%",
  "{#} MeV neutrons on a medium-mass nucleus (illustrative shares)": "neutrones de {#} MeV sobre un núcleo de masa media (fracciones ilustrativas)",
});
