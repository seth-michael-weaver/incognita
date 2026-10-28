/* Spanish: cascade (chapter 8) */
WT.es.ch.cascade = {
  num: "Capítulo 11", title: "Bajando por la carta", short: "Cascada",
  lead: "Una emisión rara vez es el final: el núcleo que queda suele seguir lo bastante caliente para volver a emitir.",
  html: `
<div class="step">
  <p>Un neutrón ha salido del núcleo compuesto (izquierda), y el <b>núcleo residual</b> que deja (derecha) sigue caliente. La bola naranja es la energía. El estado fundamental del residual está más alto, en la <b>energía de separación</b> S<sub>n</sub> del neutrón, lo que cuesta arrancarlo.</p>
  <p>Cada vez que sale un neutrón, la bola cae lo que vale la energía cinética del neutrón. Donde se detiene es la <b>excitación</b> del residual, su energía de sobra; los puntos de la derecha cuentan los aterrizajes.</p>
  <div class="ctl"><label for="cs-e">Energía del neutrón</label><input id="cs-e" type="range" data-bind="E" min="1" max="30" step="0.5" value="15"><output data-show="E" data-fmt="1"></output></div>
  <p>Los neutrones emitidos suelen ser lentos, así que la mayoría de las caídas son cortas. Los puntos azules quedan por encima del umbral de neutrones (línea discontinua): pueden permitirse un segundo neutrón, la reacción (n,2n). Por debajo de unos 11 MeV ninguno llega.</p>
</div>
<div class="step">
  <h3>Un paseo por la carta</h3>
  <p>Las corrientes son reacciones que recorren una esquina de la <b>carta de núclidos</b>, los núcleos ordenados por número de neutrones N (en horizontal) y de protones Z (en vertical). Todas empiezan en la casilla remarcada del núcleo compuesto; cada casilla lleva el nombre de la reacción que termina allí.</p>
  <p>Un <em class="n">neutrón</em> emitido mueve una casilla a la izquierda, un <em class="p">protón</em> una hacia abajo, una <em class="a">partícula alfa</em> (dos protones, dos neutrones) dos en diagonal. El ancho de la corriente es cuánto da ese paso; el tono y el porcentaje, dónde terminan las reacciones.</p>
  <div class="ctl"><label for="cs-e4">Energía del neutrón</label><input id="cs-e4" type="range" data-bind="E" min="1" max="30" step="0.5" value="14"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="fire">Lanzar 200 reacciones</button></div>
  <p>Cada paso cuesta de 7 a 11 MeV de energía de separación, así que incluso a 30 MeV el recorrido tiene como mucho tres o cuatro pasos.</p>
</div>
<div class="step">
  <h3>De arriba abajo, intervalo a intervalo</h3>
  <p>El motor vacía cada núcleo de arriba abajo, una rebanada de energía, o <b>intervalo</b>, cada vez. A la derecha, el residual de la primera emisión; a la izquierda, su hijo, con un neutrón menos. Las bolas naranjas son reacciones que esperan en cada intervalo. Aquí los intervalos miden 1 MeV; el motor usa unos 40 por núcleo, ajustados a la energía disponible.</p>
  <p>Cuando el marcador barre un intervalo, cada bola toma una salida según la competencia del capítulo 9: un fotón (<em class="g">γ</em>) la baja a un intervalo inferior, un <em class="n">neutrón</em> la lleva al hijo, un protón o una alfa la sacan del dibujo. Por debajo de todos los umbrales, los fotones llevan el resto al estado fundamental (gris). Después se barre el hijo.</p>
  <div class="ctl"><label for="cs-e3">Energía del neutrón</label><input id="cs-e3" type="range" data-bind="E" min="8" max="30" step="0.5" value="18"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="restart">Empezar de nuevo</button></div>
  <p>Los fotones solo bajan, y cada núcleo se termina antes que sus hijos, así que nada cae en un intervalo ya vaciado.</p>
</div>
<div class="step">
  <h3>Ponerle nombre a la historia</h3>
  <p>Se reproduce una reacción cada vez: el marcador salta por la carta y cada partícula emitida cae en la bandeja. La bandeja llena nombra el <b>canal exclusivo</b>, como (n,2n); los fotones no cuentan. El motor da a cada canal su propia sección eficaz (su probabilidad, como un área efectiva del blanco).</p>
  <div class="btns"><button class="btn ghost" data-act="next">Siguiente canal</button></div>
  <p>Recórrelos. (n,np) se reproduce dos veces, primero con el neutrón y luego con el protón: misma casilla, misma bandeja, un solo canal. Después, un deuterón fantasma (un protón y un neutrón ligados) llega a esa casilla en un solo salto: su bandeja dice d, otro canal, (n,d).</p>
</div>
<div class="step">
  <h3>Dónde termina todo</h3>
  <p>Cada casilla tiene ahora estantes: de tinta para el <b>estado fundamental</b>, verde (en dos casillas) para un <b>isómero</b>, un estado excitado que vive lo bastante como para contar como un producto aparte. La altura del montón es la <b>producción residual</b>: cuánto de cada núcleo fabricaron las reacciones.</p>
  <div class="ctl"><label for="cs-e2">Energía del neutrón</label><input id="cs-e2" type="range" data-bind="E" min="1" max="30" step="0.5" value="14"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="fire">Lanzar 200 reacciones</button></div>
  <p>Arrastra la energía: el siguiente lote la usa y los montones viejos se desvanecen. La producción se aleja del punto de partida a medida que pueden salir más partículas. Toda historia termina en un estante, y una medida por activación ve exactamente estos montones: se irradia una muestra y luego se cuentan las desintegraciones de cada producto.</p>
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
