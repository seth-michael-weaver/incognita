/* Spanish: compound (chapter 5) */
WT.es.ch.compound = {
  num: "Capítulo 8", title: "El núcleo compuesto", short: "Núcleo compuesto",
  lead: "Cuando terminan los primeros choques rápidos, todos los nucleones comparten la energía. Este estado asentado es el núcleo compuesto. Para predecir qué hará después, el motor necesita saber de cuántas formas puede guardar su energía.",
  html: `
<div class="step">
  <p>Un neutrón choca contra un lado de un núcleo. Su energía, más la que se libera al ser capturado, empieza como un punto caliente (el resplandor naranja); los choques la van pasando, y en unos 10⁻²¹ segundos cada nucleón lleva una parte.</p>
  <div class="btns"><button class="btn" data-act="hit">Golpear desde otro lado</button></div>
  <p>Pulsa el botón para lanzar el neutrón desde otro lado. El resplandor siempre termina igual: el núcleo ha <b>olvidado cómo se formó</b>. Es el núcleo compuesto de Bohr. A partir de aquí solo importan tres datos: su energía, su espín (cuánto gira) y su paridad (una etiqueta + o − para su simetría especular).</p>
</div>
<div class="step">
  <h3>De los niveles discretos al continuo</h3>
  <p>La escalera de la izquierda contiene los estados del núcleo, con la energía hacia arriba; la ventana de la derecha amplía una franja de 1 MeV alrededor de la bola naranja. Cerca del fondo los peldaños están muy separados, y cada uno se ha medido. Más arriba, las formas de repartir la energía entre 56 nucleones se multiplican hasta que los peldaños se funden en una banda continua, el continuo.</p>
  <div class="ctl"><label for="cn-e">Energía de excitación</label><input id="cn-e" type="range" data-bind="E" min="0" max="20" step="0.1" value="6.5"><output data-show="E" data-fmt="1"></output></div>
  <p>Arrastra la energía de excitación (la energía guardada por encima del estado más bajo, en MeV) y observa la ventana. La <b>densidad de niveles</b> ρ, estados por MeV, crece aproximadamente como e<sup>2√(aE)</sup>, donde <i>a</i> marca el ritmo de cada núcleo: unos pocos por MeV a 3 MeV, cientos cerca de 8 MeV (donde un neutrón podría escapar), millones hacia 20 MeV. Ahí arriba el motor trabaja con la propia ρ.</p>
</div>
<div class="step">
  <h3>La densidad de niveles compuesta</h3>
  <p>La altura del terreno es la densidad de niveles en escala logarítmica, con la energía hacia la derecha. Abajo a la izquierda están los niveles contados. El tablón recto es la ley de <b>temperatura constante</b>: ρ se multiplica por e (unos 2,7) cada <i>T</i> MeV, donde <i>T</i> es la temperatura nuclear. La ladera es el <b>gas de Fermi</b>, que trata los nucleones como partículas independientes. Salvo para los blancos más pesados, donde lee densidades tabuladas, el motor usa esta pareja por defecto.</p>
  <div class="ctl"><label for="cn-ex">Energía de empalme</label><input id="cn-ex" type="range" data-bind="Ex" min="4.5" max="12" step="0.05" value="6"><output data-show="Ex" data-fmt="1"></output></div>
  <p>Arrastra la energía de empalme: la unión se desliza por la colina y el tablón gira para encontrarla con la misma altura y pendiente. Las dos pilas de abajo comparan los niveles que predice el tablón con los realmente contados. Solo una unión los iguala; ahí el tablón se pone verde. Esa es la energía que elige el motor.</p>
</div>
<div class="step">
  <h3>Efectos de capas y su amortiguamiento</h3>
  <p>Niveles de un solo nucleón, dos nucleones por nivel, para dos núcleos. A la izquierda, una capa cerrada: todo lo que hay bajo un gran hueco está lleno, así que cualquier movimiento paga el hueco entero. A la derecha, un núcleo de mitad de capa con el nivel superior medio lleno, así que hay movimientos baratos desde el principio. Cada contador muestra cuántas configuraciones admiten ese calor.</p>
  <div class="ctl"><label for="cn-u">Calor (excitación)</label><input id="cn-u" type="range" data-bind="U" min="0" max="40" step="0.5" value="3"><output data-show="U" data-fmt="1"></output></div>
  <p>Sube el calor y mira cómo saltan los nucleones. Con poco calor, a la capa cerrada le faltan configuraciones; con calor suficiente el hueco deja de importar y ambas cuentas crecen igual. El motor lo resume en un número por núcleo, el <b>parámetro de densidad de niveles</b> <i>a</i>: cuanto mayor es <i>a</i>, más rápido crece con el calor el número de configuraciones. Las agujas lo muestran para cada núcleo: empiezan separadas y, a lo largo de unos 10 MeV, ambas se asientan en el mismo valor suave (escrito <i>ã</i>, «a tilde»), el que tendría un núcleo sin huecos de capa.</p>
  <p>Así, el motor parte de cada núcleo con su efecto de capas, la energía extra que valen sus huecos (escrita δW), y deja que ese efecto se desvanezca al subir el calor.</p>
  <div class="aside">La fórmula: <i>a</i>(<i>U</i>) = <i>ã</i> · [1 + δW · (1 − e<sup>−γ<i>U</i></sup>) / <i>U</i>], con <i>U</i> el calor y γ (gamma, unos 0,1 por MeV aquí, menos en núcleos más pesados) la rapidez con que se desvanece el efecto de capas.</div>
</div>
<div class="step">
  <h3>Distribuciones de espín y paridad</h3>
  <p>Los estados de una energía caen en cajones según el espín <i>J</i>, el momento angular del núcleo: fichas rellenas para paridad +, huecas para −. Los cajones del medio son los que más se llenan, siguiendo (2<i>J</i>+1) e<sup>−(J+½)²/2σ²</sup>, donde el corte de espín σ fija la anchura. Las dos paridades salen más o menos iguales.</p>
  <div class="ctl"><label for="cn-u2">Excitación</label><input id="cn-u2" type="range" data-bind="U2" min="1" max="30" step="0.5" value="8"><output data-show="U2" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="deform">Deformar el núcleo</button></div>
  <p>Sube la excitación: σ crece, porque un núcleo más caliente puede llevar más espín. Luego pulsa Deformar. Un núcleo con forma de balón de rugby también puede girar como un todo, así que cada cajón gana estados (las fichas azules): es el <b>realce colectivo</b>. Por defecto, el motor solo lo añade para blancos de más de unos 215 nucleones.</p>
</div>
<div class="step">
  <h3>Intervalos de energía en el continuo</h3>
  <p>Por encima del último nivel contado, el motor corta el continuo en franjas de igual anchura en energía, llamadas intervalos (bins). En cada intervalo los puntos se agrupan en un bloque de ρ·ΔE estados (ΔE es la anchura del intervalo), repartido por espín y paridad como arriba.</p>
  <div class="ctl"><label for="cn-emax">Tope de la escalera</label><input id="cn-emax" type="range" data-bind="Emax" min="8" max="30" step="0.5" value="14"><output data-show="Emax" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="rebin">Volver a ordenar</button></div>
  <p>Arrastra el tope de la escalera, la mayor energía que puede aportar el neutrón. El mismo número de intervalos debe cubrir más energía, así que cada uno se hace más alto. La bola naranja baja de intervalo en intervalo: cada paso posterior (elegir una salida, la cascada de fotones, el recorrido por la carta) trabaja sobre estos intervalos. Aquí se dibujan diez; el motor usa hasta 40.</p>
  <div class="aside">En el código: <code>density/parameters.py</code> (<i>a</i>(U) de Ignatyuk, corte de espín, distribución de Wigner, realce colectivo), <code>density/models.py</code> (temperatura constante, gas de Fermi, tablas), <code>density/matching.py</code> (la energía de empalme a partir de los niveles contados), <code>core/grids.py</code> (intervalos de excitación).</div>
</div>`,
};
(function () {
  const L = {
    // scene 1
    "a neutron comes in": "llega un neutrón",
    "a hot spot: the energy is still local": "un punto caliente: la energía sigue localizada",
    "equilibrium: every nucleon holds a share": "equilibrio: cada nucleón tiene una parte",
    "no trace left of where it was hit": "no queda rastro de dónde se golpeó",
    // scene 2
    "ground state": "estado fundamental",
    "{#}–{#} MeV, magnified": "{#}–{#} MeV, ampliado",
    "no level in this slice": "ningún nivel en esta franja",
    "{#} rung in {#} MeV": "{#} peldaño en {#} MeV",
    "{#} rungs in {#} MeV": "{#} peldaños en {#} MeV",
    "{#} rung in this {#}-MeV slice": "{#} peldaño en esta franja de {#} MeV",
    "{#} rungs in this {#}-MeV slice": "{#} peldaños en esta franja de {#} MeV",
    "about {#} rungs: too close to draw": "unos {#} peldaños: imposible dibujarlos",
    "about {#}k rungs: too close to draw": "unos {#} mil peldaños: imposible dibujarlos",
    "about {#}M rungs: too close to draw": "unos {#} M de peldaños: imposible dibujarlos",
    "about {#}B rungs: too close to draw": "unos {#} mil M de peldaños: imposible dibujarlos",
    "about {#} rungs in this slice: too close to draw": "unos {#} peldaños en esta franja: imposible dibujarlos",
    "about {#} thousand rungs in this slice: too close to draw": "unos {#} mil peldaños en esta franja: imposible dibujarlos",
    "about {#} million rungs in this slice: too close to draw": "unos {#} millones de peldaños en esta franja: imposible dibujarlos",
    "about {#} billion rungs in this slice: too close to draw": "unos {#} mil millones de peldaños en esta franja: imposible dibujarlos",
    "each one measured: energy, spin and parity": "cada uno medido: energía, espín y paridad",
    "the rungs are multiplying": "los peldaños se multiplican",
    "a continuum: the engine uses ρ itself": "un continuo: el motor usa la propia ρ",
    "≈ energy to free a neutron": "≈ energía para liberar un neutrón",
    "energy ↑": "energía ↑",
    // scene 3
    "gap: plank below the rungs": "hueco: tablón bajo los peldaños",
    "gap: plank above the rungs": "hueco: tablón sobre los peldaños",
    "counted levels": "niveles contados",
    "CT plank": "tablón TC",
    "constant-temperature plank": "tablón de temperatura constante",
    "Fermi-gas hillside": "ladera del gas de Fermi",
    "joint {#} MeV": "unión {#} MeV",
    "energy →": "energía →",
    "+{#} more": "+{#} más",
    "{#} counted": "{#} contados",
    "{#} predicted": "{#} predichos",
    "{#}+ predicted": "{#}+ predichos",
    "equal: the plank rests on the counted rungs": "iguales: el tablón se apoya en los peldaños contados",
    "too few: the plank is too steep and sinks": "pocos: el tablón es demasiado empinado y se hunde",
    "too many: the plank is too shallow and floats": "demasiados: el tablón es demasiado plano y flota",
    // scene 4
    "closed shell": "capa cerrada",
    "mid-shell": "mitad de capa",
    "gap": "hueco",
    "no arrangement holds this heat": "ninguna configuración admite este calor",
    "≈ {#} arrangement": "≈ {#} configuración",
    "≈ {#} arrangements": "≈ {#} configuraciones",
    "≈ {#} thousand arrangements": "≈ {#} mil configuraciones",
    "≈ {#} million arrangements": "≈ {#} millones de configuraciones",
    "≈ {#} billion arrangements": "≈ {#} mil millones de configuraciones",
    "a ≈ {#}": "a ≈ {#}",
    "cold: nobody can move": "frío: nadie puede moverse",
    "temperature ≈ {#} MeV": "temperatura ≈ {#} MeV",
    // scene 5
    "states at {#} MeV": "estados a {#} MeV",
    "spin J →": "espín J →",
    "+ parity": "paridad +",
    "− parity": "paridad −",
    "rotation ×{#}": "rotación ×{#}",
    "added by rotation: ×{#} (a few drawn)": "añadidos por rotación: ×{#} (se dibujan algunos)",
    "spread σ ≈ {#}: most states near J ≈ {#}": "anchura σ ≈ {#}: la mayoría de estados cerca de J ≈ {#}",
    "deformed: it can rotate": "deformado: puede girar",
    "spherical": "esférico",
    // scene 6
    "≈ {#} thousand": "≈ {#} mil",
    "≈ {#} million": "≈ {#} millones",
    "≈ {#} billion": "≈ {#} mil millones",
    "≈ {#}k": "≈ {#} mil",
    "≈ {#}M": "≈ {#} M",
    "≈ {#}B": "≈ {#} mil M",
    "{#} bins, each {#} MeV wide": "{#} intervalos de {#} MeV cada uno",
    "counted": "contados",
    "states in each bin": "estados en cada intervalo",
  };
  Object.assign(WT.es.labels, L);
})();
