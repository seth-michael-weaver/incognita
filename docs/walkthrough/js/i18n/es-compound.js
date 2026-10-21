/* Spanish: compound (chapter 5) */
WT.es.ch.compound = {
  num: "Capítulo 5", title: "Repartir la energía", short: "Núcleo compuesto",
  lead: "Cuando terminan los primeros choques rápidos, la energía queda repartida entre todos los nucleones. Este estado asentado es el núcleo compuesto. Para predecir qué hará después, el motor necesita saber de cuántas formas distintas puede guardar su energía.",
  html: `
<div class="step">
  <p>La imagen muestra un neutrón que choca contra un lado de un núcleo. Su energía, más la que se libera al ser capturado, empieza como un punto caliente: el resplandor naranja alrededor de los nucleones que golpea. Los choques la van pasando, y en unos 10⁻²¹ segundos cada nucleón lleva una parte.</p>
  <div class="btns"><button class="btn" data-act="hit">Golpear desde otro lado</button></div>
  <p>Pulsa el botón para lanzar el neutrón desde otro lado. El núcleo siempre termina con el mismo resplandor uniforme: ha <b>olvidado cómo se formó</b>. Esta es la idea de Niels Bohr del núcleo compuesto. Significa que el resto del cálculo solo necesita tres datos de este estado: su energía total, su espín (cuánto gira) y su paridad (una etiqueta + o − para su simetría especular). Su historia no importa.</p>
</div>
<div class="step">
  <h3>De niveles separados a un continuo</h3>
  <p>A la izquierda hay una escalera de energía. Cada peldaño es un estado en el que puede estar el núcleo, con la energía aumentando hacia arriba. La ventana de la derecha amplía una franja de 1 MeV de la escalera alrededor de la bola naranja, el núcleo. Cerca del fondo los peldaños están muy separados, y cada uno se ha medido. Más arriba, el número de formas de repartir la energía entre 56 nucleones crece tan deprisa que los peldaños se multiplican hasta fundirse en una banda continua, llamada el continuo.</p>
  <div class="ctl"><label for="cn-e">Energía de excitación</label><input id="cn-e" type="range" data-bind="E" min="0" max="20" step="0.1" value="6.5"><output data-show="E" data-fmt="1"></output></div>
  <p>Arrastra la energía de excitación (la energía que el núcleo guarda por encima de su estado más bajo, en MeV, millones de electronvoltios) y observa los peldaños en la ventana. La <b>densidad de niveles</b> ρ, el número de estados por MeV, crece aproximadamente como e<sup>2√(aE)</sup>, donde <i>a</i> es un número propio de cada núcleo que fija lo rápido que crece la cuenta. Eso da unos pocos estados por MeV a 3 MeV, cientos cerca de 8 MeV (donde un neutrón podría escapar) y millones hacia 20 MeV. Nadie puede enumerar estados tan juntos, así que ahí arriba el motor trabaja con la propia ρ.</p>
</div>
<div class="step">
  <h3>Tres piezas unidas en una energía</h3>
  <p>La imagen es un terreno cuya altura es la densidad de niveles en escala logarítmica (cada escalón hacia arriba multiplica la cuenta por el mismo factor), con la energía hacia la derecha. Abajo a la izquierda están los niveles contados, apilados como peldaños. El tablón recto es la ley de <b>temperatura constante</b>: ρ se multiplica por e (unos 2,7) por cada <i>T</i> MeV añadidos, donde <i>T</i> es la temperatura nuclear. La ladera de la derecha es la fórmula del <b>gas de Fermi</b>, que trata los nucleones como un gas de partículas independientes; se curva a medida que sube la energía.</p>
  <div class="ctl"><label for="cn-ex">Energía de empalme</label><input id="cn-ex" type="range" data-bind="Ex" min="4.5" max="12" step="0.05" value="6"><output data-show="Ex" data-fmt="1"></output></div>
  <p>Arrastra la energía de empalme: la unión se desliza por la ladera y el tablón gira para encontrarse siempre suavemente con la colina, con la misma altura y la misma pendiente. Su otro extremo también debe apoyarse en los peldaños contados. Las dos pilas de abajo comparan los niveles que predice el tablón con los realmente contados. Solo una unión los iguala; ahí el tablón se pone verde. Esa es la energía que elige el motor.</p>
</div>
<div class="step">
  <h3>Capas que se funden</h3>
  <p>La imagen muestra los niveles de energía de un nucleón cada vez, dos nucleones por nivel, para dos núcleos. A la izquierda, una capa cerrada: todos los niveles bajo un gran hueco están llenos, así que nada puede moverse sin pagar el hueco entero. A la derecha, un núcleo de mitad de capa cuyo nivel superior está medio lleno, así que hay movimientos baratos desde el principio. El contador bajo cada uno muestra cuántas configuraciones admiten ese calor.</p>
  <div class="ctl"><label for="cn-u">Calor (excitación)</label><input id="cn-u" type="range" data-bind="U" min="0" max="40" step="0.5" value="3"><output data-show="U" data-fmt="1"></output></div>
  <p>Sube el calor y mira cómo los nucleones saltan a niveles vacíos. Con poco calor, a la capa cerrada le faltan configuraciones; con calor suficiente el hueco deja de importar y ambas cuentas crecen igual. El <b>parámetro de densidad de niveles</b> <i>a</i> recoge esto: las agujas empiezan separadas y convergen en el valor suave <i>ã</i> a lo largo de unos 10 MeV. El motor deja que los efectos de capa se desvanezcan con esta fórmula, donde δW es la corrección de capas (cuánto se aleja el núcleo de lo suave) y γ fija lo rápido que se desvanece:</p>
  <div class="formula">a(U) = ã · [1 + δW · (1 − e<sup>−γU</sup>) / U]</div>
</div>
<div class="step">
  <h3>Ordenados por espín y paridad</h3>
  <p>La imagen reparte los estados de una energía en cajones según el espín <i>J</i>, el momento angular del núcleo. Cada ficha que cae es un estado: rellena para paridad +, hueca para paridad −. Los cajones del medio son los que más se llenan, siguiendo la forma de Wigner (2<i>J</i>+1) e<sup>−(J+½)²/2σ²</sup>, donde σ, el corte de espín, fija lo ancha que es la distribución. Las dos paridades salen más o menos iguales.</p>
  <div class="ctl"><label for="cn-u2">Excitación</label><input id="cn-u2" type="range" data-bind="U2" min="1" max="30" step="0.5" value="8"><output data-show="U2" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="deform">Deformar el núcleo</button></div>
  <p>Sube la excitación: σ crece, porque un núcleo más caliente puede llevar más espín, y las fichas se extienden a cajones más altos. Luego pulsa Deformar. Un núcleo con forma de balón de rugby también puede girar como un todo, cosa que una esfera no puede, así que cada cajón gana estados extra (las fichas azules). Esto es el <b>realce colectivo</b>.</p>
</div>
<div class="step">
  <h3>Troceado en intervalos</h3>
  <p>La imagen vuelve a mostrar la escalera, con el continuo como puntos que se apiñan más a medida que sube la energía. El motor no puede seguir millones de estados sueltos, así que por encima del último nivel contado corta el continuo en cajones de igual anchura en energía, llamados intervalos (bins). En cada intervalo los puntos se agrupan en un bloque que contiene ρ·ΔE estados, donde ΔE es la anchura del intervalo, y cada bloque se reparte después por espín y paridad como en los cajones de arriba.</p>
  <div class="ctl"><label for="cn-emax">Tope de la escalera</label><input id="cn-emax" type="range" data-bind="Emax" min="8" max="30" step="0.5" value="14"><output data-show="Emax" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="rebin">Volver a ordenar</button></div>
  <p>Arrastra el tope de la escalera, la mayor energía que puede aportar el neutrón incidente. El mismo número de cajones debe cubrir más energía, así que cada uno se hace más alto y contiene más estados. La bola naranja muestra cómo los usa el resto del cálculo: el núcleo baja de intervalo en intervalo, y cada paso posterior (elegir una salida, la cascada de fotones, el recorrido por la carta de núclidos) trabaja intervalo a intervalo sobre esta estructura. Aquí se dibujan 10 intervalos; el motor usa unas pocas decenas.</p>
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
