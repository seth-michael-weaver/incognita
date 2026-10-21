/* Spanish: direct (Capítulo 3, reacciones directas) */
WT.es.ch.direct = {
  num: "Capítulo 3", title: "Un golpe de refilón", short: "Reacciones directas",
  lead: "No todo neutrón que llega al núcleo es engullido. Algunos rozan su superficie, le dan un empujón y siguen volando.",
  html: `
<div class="step">
  <p>La imagen muestra un neutrón que pasa volando junto a un núcleo. Su distancia a la línea central es <i>b</i>, el <b>parámetro de impacto</b>, dado aquí en radios nucleares <i>R</i>. El anillo punteado es la delgada capa exterior del núcleo, su piel. Un neutrón apuntado al centro es absorbido, y su energía acaba repartida entre todos los nucleones. Un neutrón que solo roza la piel puede hacer algo más rápido: empujar el núcleo una vez a un nivel excitado y seguir volando, casi siempre hacia delante y solo un poco más lento. Eso es una <b>reacción directa</b>: un solo paso, que termina en unos 10⁻²² segundos.</p>
  <div class="ctl"><label for="di-b">Puntería b (en radios)</label><input id="di-b" type="range" data-bind="b" min="0" max="1.5" step="0.01" value="1.0"><output data-show="b" data-fmt="2"></output></div>
  <p>Arrastra <i>b</i>. Por debajo de 0,8, más o menos, el neutrón es engullido. Cerca de 1 roza el núcleo y lo deja en su primer nivel excitado, 2⁺. Por encima de 1,2, aproximadamente, no acierta y solo se desvía: <b>dispersión elástica</b>, que deja el núcleo sin cambios.</p>
</div>
<div class="step">
  <h3>Poner a girar un núcleo estirado</h3>
  <p>A la izquierda hay un núcleo estirado, con forma de balón de fútbol americano (capítulo 1). El empujón de un neutrón que pasa lo pone a rotar. Cada rotación más rápida es un nivel de su <b>banda rotacional</b>, la escalera de la derecha: 0⁺, 2⁺, 4⁺, 6⁺, 8⁺. El neutrón puede empujar el núcleo escalera arriba, y el núcleo puede devolver el empujón, así que ningún nivel puede calcularse por separado. El motor los resuelve todos a la vez. Esto se llama <b>canales acoplados</b>: cada canal es un resultado posible, aquí un nivel de la banda, y cada uno influye en los demás.</p>
  <div class="btns"><button class="btn" data-act="kick">Subirlo un nivel</button><button class="btn ghost" data-act="rpause">Pausar / seguir</button></div>
  <div class="ctl"><label for="di-beta">Deformación β₂</label><input id="di-beta" type="range" data-bind="beta2" min="0.05" max="0.4" step="0.01" value="0.25"><output data-show="beta2" data-fmt="2"></output></div>
  <p>Los arcos muestran qué niveles están conectados. <i>λ</i> nombra la parte de la forma que hace la conexión: <i>λ</i> = 2 es el estiramiento global, y conecta niveles vecinos; <i>λ</i> = 4 es un abultamiento más fino, y salta dos niveles de una vez. Arrastra <i>β₂</i>: un núcleo más estirado conecta sus niveles con más fuerza, así que los arcos se engrosan. Como la banda se resuelve junto con la onda entrante, los coeficientes de transmisión de este paso ya descuentan lo que se lleva la banda.</p>
</div>
<div class="step">
  <h3>Ondas sobre una esfera</h3>
  <p>A la izquierda hay un núcleo redondo cuya superficie ondula. La energía de ondulación viene en paquetes fijos llamados <b>fonones</b>, y cada uno añade la misma energía. La escalera de la derecha muestra el resultado. Un fonón de la ondulación balón–disco (<i>λ</i> = 2) da el nivel 2⁺. Dos fonones dan tres niveles, 0⁺, 2⁺ y 4⁺, al doble de energía. El motor resuelve estos niveles junto con el estado fundamental. Llegar a los niveles de dos fonones exige dos empujones seguidos.</p>
  <div class="ctl"><label for="di-lam">Forma de la onda λ</label><input id="di-lam" type="range" data-bind="lam" min="2" max="3" step="1" value="2" data-instant><output data-show="lam" data-fmt="0"></output></div>
  <div class="btns"><button class="btn ghost" data-act="ph1">Un fonón</button><button class="btn ghost" data-act="ph2">Dos fonones</button></div>
  <p>Pon <i>λ</i> = 3 para una ondulación en forma de pera, cuyo primer nivel es 3⁻. Pulsa los botones para añadir uno o dos fonones.</p>
</div>
<div class="step">
  <h3>Un empujón, una vez</h3>
  <p>La imagen muestra una onda de neutrones que llega desde la izquierda sobre un núcleo cuyo borde está ligeramente estirado y tiembla. Para la mayoría de los niveles la conexión es débil, y basta un método más sencillo: dejar que la onda entrante del capítulo 2 empuje el núcleo una sola vez y luego calcular la onda saliente. Este método de un empujón se llama <b>DWBA</b> (aproximación de Born de ondas distorsionadas). El empujón solo puede ocurrir en el borde, donde el potencial del capítulo 2 cae de profundo a cero en aproximadamente medio femtómetro; el borde brilla en naranja donde lo golpean las crestas. Desde ahí se extiende una segunda onda, circular: los neutrones que dejaron el núcleo en un nivel excitado.</p>
  <div class="ctl"><label for="di-bd">Deformación del nivel β</label><input id="di-bd" type="range" data-bind="bd" min="0.02" max="0.4" step="0.01" value="0.2"><output data-show="bd" data-fmt="2"></output></div>
  <p>Arrastra <i>β</i>: el borde tiembla más y los círculos salientes brillan más. Su intensidad crece como <i>β</i>², así que un nivel con el doble de deformación se excita cuatro veces más a menudo. El motor busca el <i>β</i> de cada nivel conocido en una tabla de valores medidos, y calcula cómo se reparten en ángulo los neutrones dispersados para cada uno.</p>
</div>
<div class="step">
  <h3>Se mueve el núcleo entero</h3>
  <p>La imagen muestra tres maneras en que todos los nucleones pueden moverse juntos. El núcleo puede respirar hacia dentro y hacia fuera, aplastarse y estirarse, u oscilar hacia una forma de pera. Estos movimientos son <b>resonancias gigantes</b>. En este núcleo de masa media se sitúan entre unos 7 y 25 MeV por encima del estado fundamental, y cada una tiene varios MeV de ancho: demasiado anchas para contar como un solo nivel. Las pequeñas jorobas de abajo marcan dónde cae cada una en <b>energía de excitación</b>, la energía por encima del estado fundamental.</p>
  <p>El motor fija la intensidad total de cada una con una <b>regla de suma</b>, un límite que impone la física básica a la fuerza con que un núcleo puede responder a ese movimiento. Reparte esa intensidad como una joroba por encima del último nivel conocido. Estas jorobas, más los empujones a niveles altos, forman el <b>continuo colectivo</b>.</p>
  <div class="btns"><button class="btn ghost" data-act="mono">Respiración</button><button class="btn ghost" data-act="quad">Aplastamiento</button><button class="btn ghost" data-act="oct">Pera</button></div>
  <p>El movimiento más conocido, los protones oscilando contra los neutrones, es la resonancia gigante dipolar. Sobre todo absorbe y emite luz, así que pertenece al capítulo 7.</p>
</div>
<div class="step">
  <h3>Directo a una órbita</h3>
  <p>La imagen vuelve a mostrar el pozo. Los neutrones llenan sus <b>órbitas</b> inferiores (las energías permitidas para un neutrón dentro); dos cerca de la cima están vacías. Un neutrón libre puede caer directamente en una órbita vacía y enviar la energía sobrante en forma de <em class="g">fotón</em>. El núcleo nunca se calienta. Esto es la <b>captura directa</b>. El motor la calcula con el mismo pozo del capítulo 2: la onda libre fuera, la órbita ligada dentro y el fotón que las conecta.</p>
  <div class="btns"><button class="btn" data-act="drop">Dejar caer un neutrón</button></div>
  <p>La captura directa importa sobre todo donde la ruta habitual, absorber el neutrón y repartir su energía, es débil: núcleos ligeros y núcleos lejos de la estabilidad, que tienen pocos niveles y muy separados.</p>
</div>
<div class="step">
  <h3>Lo directo se lleva su parte primero</h3>
  <p>La imagen muestra un haz de neutrones que reaccionan todos con el núcleo (la sección eficaz de reacción del capítulo 2), y cada trayectoria acaba en uno de tres destinos. Un neutrón que roza el borde da un empujón y sigue volando: una reacción <b>directa</b>. Uno que entra puede arrancar un nucleón de inmediato, antes de que la energía tenga tiempo de repartirse: una colisión rápida, o emisión de <b>preequilibrio</b> (capítulo 4). El resto son engullidos, y el núcleo brilla mientras su energía se reparte entre todos sus nucleones: un <b>núcleo compuesto</b> (capítulo 5). Los montones de abajo cuentan los destinos a medida que ocurren.</p>
  <div class="ctl"><label for="di-e">Energía del neutrón (MeV)</label><input id="di-e" type="range" data-bind="E" min="1" max="60" step="0.5" value="14"><output data-show="E" data-fmt="1"></output></div>
  <p>Arrastra la energía y mira cómo se vuelven a llenar los montones. A unos pocos MeV casi todos los neutrones son engullidos. A decenas de MeV, las reacciones directas y las colisiones rápidas juntas se llevan una gran parte. El motor hace sus cuentas en ese orden: primero resta cada pieza directa, luego las colisiones rápidas; solo lo que queda forma un núcleo compuesto.</p>
  <div class="aside">En el código: <code>ecis/formfactor.py</code>, <code>ecis/coupling.py</code>, <code>ecis/solver.py</code> (potencial deformado, canales acoplados para rotores y vibradores), <code>ecis/dwba.py</code> y <code>direct/dwba.py</code> (empujón único, resonancias gigantes, continuo colectivo), <code>direct/racapcalc.py</code> (captura directa), <code>compound/normalization.py</code> (la contabilidad).</div>
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
