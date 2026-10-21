/* Spanish: cascade (chapter 8) */
WT.es.ch.cascade = {
  num: "Capítulo 8", title: "Bajando por la carta", short: "Cascada",
  lead: "Una emisión rara vez es el final. El núcleo que queda suele seguir caliente: guarda energía de sobra para volver a emitir.",
  html: `
<div class="step">
  <p>A la izquierda está el núcleo compuesto, blanco y neutrón fundidos en uno. Sus peldaños son niveles de energía: escasos cerca del estado fundamental, abajo, y cada vez más apretados hasta formar un continuo más arriba. La bola naranja es su energía. A la derecha está el <b>núcleo residual</b>, el que queda cuando sale un neutrón. Su estado fundamental está más alto, en la <b>energía de separación</b> S<sub>n</sub> del neutrón (lo que cuesta arrancarlo).</p>
  <p>Cada vez que sale un neutrón, la bola naranja cruza al otro lado y cae. La caída es la energía cinética que se llevó el neutrón; donde se detiene es la <b>excitación</b> (energía de sobra) que conserva el residual. Los puntos apilados a la derecha cuentan dónde aterrizaron.</p>
  <div class="ctl"><label for="cs-e">Energía del neutrón</label><input id="cs-e" type="range" data-bind="E" min="1" max="30" step="0.5" value="15"><output data-show="E" data-fmt="1"></output></div>
  <p>Los neutrones emitidos suelen ser lentos, así que la mayoría de las caídas son cortas y el residual sigue caliente. Los puntos azules quedan por encima del umbral de neutrones del residual (línea discontinua): pueden permitirse un segundo neutrón, la reacción (n,2n). Por debajo de unos 11 MeV ninguno llega.</p>
</div>
<div class="step">
  <h3>Un paseo por la carta</h3>
  <p>Cada casilla es un núcleo de una esquina de la <b>carta de núclidos</b>, el mapa de todos los núcleos según su número de neutrones N (en horizontal) y de protones Z (en vertical); las casillas difuminadas continúan hacia el resto de la carta. Toda reacción empieza en la casilla remarcada, el núcleo compuesto, una casilla a la derecha del blanco. Cada casilla lleva el nombre de la reacción que termina allí.</p>
  <p>Las corrientes son la reacción en movimiento. Emitir un <em class="n">neutrón</em> la mueve una casilla a la izquierda, un <em class="p">protón</em> una casilla hacia abajo, una <em class="a">partícula alfa</em> (dos protones y dos neutrones) dos casillas en diagonal. El ancho de una corriente indica cuánto da ese paso; el tono y el porcentaje, dónde termina.</p>
  <div class="btns"><button class="btn" data-act="fire">Lanzar 200 reacciones</button></div>
  <p>Cada paso cuesta una energía de separación de unos 7 a 11 MeV, así que incluso a 30 MeV el paseo tiene como mucho tres o cuatro pasos.</p>
</div>
<div class="step">
  <h3>De arriba abajo, intervalo a intervalo</h3>
  <p>Otra vez dos núcleos: a la derecha, el residual de la primera emisión; a la izquierda, su hijo, con un neutrón menos. El motor corta cada uno en rebanadas de energía llamadas <b>intervalos</b> (aquí de 1 MeV de alto; los del motor miden 0,5 MeV). Las bolas naranjas son reacciones que esperan en cada intervalo, colocadas por la primera emisión. El marcador baja desde arriba.</p>
  <p>Cuando llega a un intervalo, cada bola toma una salida según la competencia del capítulo 6. Un fotón (<em class="g">γ</em>) la baja a un intervalo inferior del mismo núcleo; un <em class="n">neutrón</em> la lleva a un intervalo del hijo; un protón o una alfa la llevan a otro núcleo, fuera de este dibujo. Por debajo de todos los umbrales, los fotones llevan lo que queda al estado fundamental (gris). Después se barre el hijo de la misma manera.</p>
  <div class="ctl"><label for="cs-e3">Energía del neutrón</label><input id="cs-e3" type="range" data-bind="E" min="8" max="30" step="0.5" value="18"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="restart">Empezar de nuevo</button></div>
  <p>Los fotones solo bajan, y el motor termina cada núcleo antes que sus hijos, así que nada cae nunca en un intervalo que ya se vació.</p>
</div>
<div class="step">
  <h3>Ponerle nombre a la historia</h3>
  <p>Se reproduce una reacción cada vez. El marcador naranja es el núcleo caliente saltando por la carta; en cada salto, la partícula que emite cae en la bandeja de abajo. La bandeja llena forma el <b>canal exclusivo</b>: una reacción nombrada por el conjunto de partículas que salieron, como (n,2n) para dos neutrones. Los fotones se van y no cuentan. El motor mantiene cada canal por separado y le da su propia sección eficaz (su probabilidad, expresada como un área efectiva del blanco).</p>
  <div class="btns"><button class="btn ghost" data-act="next">Siguiente canal</button></div>
  <p>Recórrelos. (n,np) se reproduce dos veces, primero con el neutrón y luego con el protón por delante: ambos terminan en la misma casilla con la misma bandeja, así que son un solo canal. Después, un fantasma muestra un deuterón (un protón y un neutrón ligados) llegando a esa casilla en un solo salto. Su bandeja dice d: otro canal, (n,d). El motor nombra los canales por lo que se emitió, no por dónde terminan.</p>
</div>
<div class="step">
  <h3>Dónde termina todo</h3>
  <p>Cada casilla tiene ahora estantes. El estante de tinta, abajo, es el <b>estado fundamental</b> del núcleo, su estado más bajo. El estante verde, en dos casillas, es un <b>isómero</b>: un estado excitado que vive lo bastante como para contar como un producto aparte. Cada reacción lanzada salta hasta donde termina, cae en un estante y emite su último fotón. La altura de cada montón es la <b>producción residual</b>: cuánto de ese núcleo fabricaron las reacciones.</p>
  <div class="ctl"><label for="cs-e2">Energía del neutrón</label><input id="cs-e2" type="range" data-bind="E" min="1" max="30" step="0.5" value="14"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="fire">Lanzar 200 reacciones</button></div>
  <p>Arrastra la energía: el siguiente lote la usa y los montones viejos se desvanecen. La producción se aleja del punto de partida a medida que pueden salir más partículas. Por debajo de todos los umbrales de partículas un núcleo solo puede emitir fotones, así que toda historia termina en uno de estos estantes. Una medida por activación ve exactamente estos montones: se irradia una muestra y luego se cuentan las desintegraciones de cada producto.</p>
  <div class="aside">En el código: <code>emission/multiple.py</code> (el bucle sobre núcleos e intervalos, la cascada γ), <code>emission/feeding.py</code> (mallas y datos de entrada para cada núcleo de la cadena), <code>compound/continuum.py</code> (la desintegración de un intervalo), <code>emission/channels.py</code> (canales exclusivos, producción residual, ramas isoméricas), <code>emission/binary.py</code> (la contabilidad de la primera emisión).</div>
</div>`,
};
Object.assign(WT.es.labels, {
  // reaction names on the squares (unchanged in Spanish)
  "(n,γ)": "(n,γ)", "(n,n′)": "(n,n′)", "(n,{#}n)": "(n,{#}n)", "(n,p)": "(n,p)", "(n,np)": "(n,np)", "(n,{#}np)": "(n,{#}np)",
  "(n,{#}p)": "(n,{#}p)", "(n,n{#}p)": "(n,n{#}p)", "(n,α)": "(n,α)", "(n,nα)": "(n,nα)",
  "compound": "compuesto", "target": "blanco",
  "N{#}": "N{#}", "N": "N", "N+{#}": "N+{#}", "Z": "Z", "Z{#}": "Z{#}",
  "neutron number →": "número de neutrones →",
  // scene 1
  "levels": "niveles",
  "Sₙ {#} MeV": "Sₙ {#} MeV", "Sₙ = {#} MeV": "Sₙ = {#} MeV",
  "ground": "fundamental",
  "residual": "residual", "residual (one neutron fewer)": "residual (un neutrón menos)",
  "n threshold": "umbral n", "its neutron threshold": "su umbral de neutrones",
  "{#} MeV": "{#} MeV",
  "drop = neutron's kinetic energy": "caída = energía cinética del neutrón",
  "{#} % land above the threshold: a second neutron can leave": "{#} % caen sobre el umbral: puede salir un segundo neutrón",
  "<{#} % land above the threshold: a second neutron can leave": "<{#} % caen sobre el umbral: puede salir un segundo neutrón",
  "all land below the threshold: only photons remain": "todos caen bajo el umbral: solo quedan fotones",
  "{#} % above threshold: (n,{#}n) possible": "{#} % sobre el umbral: (n,{#}n) posible",
  "<{#} % above threshold: (n,{#}n) possible": "<{#} % sobre el umbral: (n,{#}n) posible",
  "all below threshold: photons only": "todos bajo el umbral: solo fotones",
  // scene 2
  "incoming neutron: {#} MeV": "neutrón incidente: {#} MeV",
  "shade and % = where reactions end": "tono y % = dónde terminan",
  "stream width = flow · shade and % = share of reactions that end in that nucleus": "ancho = flujo · tono y % = fracción de reacciones que terminan en ese núcleo",
  // scene 3
  "residual (first step)": "residual (primer paso)",
  "daughter: n fewer": "hijo: un n menos", "daughter (one neutron fewer)": "hijo (un neutrón menos)",
  "now: {#}–{#} MeV": "ahora: {#}–{#} MeV", "{#}–{#} MeV": "{#}–{#} MeV",
  "done: {#} left by proton or alpha, the rest sit on ground states": "listo: {#} salieron por protón o alfa, el resto está en estados fundamentales",
  "done: everything sits on a ground state": "listo: todo está en un estado fundamental",
  "orange ball = reactions waiting in a bin · grey = settled on the ground state · pale bins = already emptied": "bola naranja = reacciones en espera · gris = en el estado fundamental · intervalos pálidos = ya vaciados",
  // scene 4
  "collected": "recogido",
  "tray: d": "bandeja: d",
  "a deuteron lands on the same square, but its tray reads d: channel (n,d)": "un deuterón llega a la misma casilla, pero su bandeja dice d: canal (n,d)",
  "tray: n n  →  (n,{#}n)": "bandeja: n n  →  (n,{#}n)",
  "tray: n  →  (n,n′)": "bandeja: n  →  (n,n′)",
  "tray: p  →  (n,p)": "bandeja: p  →  (n,p)",
  "tray: n p  →  (n,np)": "bandeja: n p  →  (n,np)",
  "tray: n p  →  (n,np) · same square, same tray": "bandeja: n p  →  (n,np) · misma casilla, misma bandeja",
  "tray: a  →  (n,α)": "bandeja: a  →  (n,α)",
  "tray: n n n  →  (n,{#}n)": "bandeja: n n n  →  (n,{#}n)",
  "tray empty, only photons: (n,γ), capture": "bandeja vacía, solo fotones: (n,γ), captura",
  "each emitted particle falls into the tray": "cada partícula emitida cae en la bandeja",
  "no particle gets out: only photons": "no sale ninguna partícula: solo fotones",
  "incoming neutron: {#} MeV · channel {#} of {#}": "neutrón incidente: {#} MeV · canal {#} de {#}",
  // scene 5
  "isomer": "isómero",
  "batch of {#} at {#} MeV": "lote de {#} a {#} MeV",
  "ink shelf: ground state · green: isomer": "tinta: estado fundamental · verde: isómero",
  "ink shelf: ground state · green shelf: isomer · pile height = how much of that nucleus was made": "estante de tinta: fundamental · verde: isómero · altura = cuánto se produjo de ese núcleo",
});
