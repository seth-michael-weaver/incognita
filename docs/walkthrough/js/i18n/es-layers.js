/* Spanish: layers (chapter 12). The scoreboard counts come from WT.board (js/scoreboard-data.js, loaded first), as in
 * js/ch/layers.js; a missing block or field drops the number, not the sentence. */
(function () {
  const B = WT.board || {};
  const nOf = (v) => (typeof v === "number" && isFinite(v) ? v : null);
  const tally = (o) => {
    if (!o) return null;
    const w = nOf(o.WIN), t = nOf(o.TIE), l = nOf(o.LOSS);
    if (w === null || t === null || l === null) return null;
    return { w, t, l, d: nOf(o.decided) ?? w + t + l };
  };
  const TE = tally(B.incognita), TT = tally(B.terra);
  const LIBS = B.terra && Array.isArray(B.terra.by_rival) ? B.terra.by_rival.map((r) => r && r.rival).filter((s) => typeof s === "string") : [];
  const ASOF = (() => {
    const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(B.asof || ""); if (!m) return null;
    const mes = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"][+m[2] - 1];
    return mes ? `${+m[3]} de ${mes} de ${m[1]}` : null;
  })();
  const figs = (T) => (T ? `<div class="figs" aria-label="${T.w} victorias, ${T.t} empates, ${T.l} derrotas"><div class="w"><b>${T.w}</b><span>victoria</span></div><div><b>${T.t}</b><span>empate</span></div><div class="l"><b>${T.l}</b><span>derrota</span></div></div>` : "");
  const libs = LIBS.length ? `las principales bibliotecas de datos evaluados (${LIBS.join(", ")})` : "las principales bibliotecas de datos evaluados";
  const engineScore = TE ? ` De ${TE.d} de esas comparaciones, va claramente por delante en ${TE.w}, empata en ${TE.t} y va por detrás en ${TE.l}.` : "";
  const terraScore = TT ? `Frente a ${libs}, va por delante en ${TT.w} de ${TT.d} comparaciones, empata en ${TT.t} y va por detrás en ${TT.l}.` : `Se compara con ${libs}.`;

  WT.es.ch.layers = {
    num: "Capítulo 21", title: "Cómo se organiza el modelo en capas", short: "Capas",
    lead: "Lo que entregamos se construye en capas sobre el motor, y cada capa tiene que ganarse su sitio frente a las mediciones.",
    html: `
<div class="step">
  <div class="layer-chip on">En uso</div>
  <h3>Capa 1 · Una regla para cada núcleo</h3>
  <p>La línea azul es la predicción del motor para una reacción. El motor es la capa de abajo: la misma física y los mismos ajustes globales para todos los núclidos, sin nada ajustado a las secciones eficaces de ningún núcleo concreto.</p>
  <div class="btns"><button class="btn ghost" data-act="reveal" aria-pressed="false">Mostrar las mediciones</button></div>
  <p>Eso lo hace comprobable frente a las mediciones y frente a otros códigos de modelos calculados sobre los mismos núcleos. No es una prueba a ciegas: los ajustes globales se eligieron observando estas mismas comparaciones.${engineScore}</p>
  ${figs(TE)}
</div>
<div class="step">
  <div class="layer-chip null">Probada: aún sin mejora</div>
  <h3>Capa 2 · Las mediciones propias de cada núcleo</h3>
  <p>Esta capa cambia la regla global por los valores medidos de cada núcleo: su espaciado de niveles D0, sus funciones de fuerza S0 y S1 (con qué facilidad absorbe neutrones lentos), su anchura gamma media ⟨Γγ⟩ y sus niveles de energía conocidos.</p>
  <div class="btns"><button class="btn ghost" data-act="ms0" aria-pressed="true">Regla global</button><button class="btn ghost" data-act="ms1" aria-pressed="false">Mediciones propias</button></div>
  <p>Actívala y la línea apenas se mueve. Las pruebas hasta ahora no han encontrado una mejora global: la única variante que ayuda a una reacción cerca de su umbral empeora la captura de neutrones. Así que esta capa sigue apagada por ahora.</p>
</div>
<div class="step">
  <div class="layer-chip cand">Candidata</div>
  <h3>Capa 3 · Seguir los buenos datos (TERRA)</h3>
  <p>Donde una reacción se ha medido bien, la línea debe seguir a las mediciones. La tercera capa, TERRA, hace pasar la línea del motor por los buenos datos donde los hay y vuelve al motor donde no.</p>
  <div class="ctl"><label for="lay-cov">Parte del rango de energía medida (%)</label><input id="lay-cov" type="range" data-bind="cov" min="0" max="1" step="0.01" value="0.45"><output data-show="covPct" data-fmt="0"></output></div>
  <p>${terraScore} La mayoría son dentro de la muestra: TERRA ha visto esas mediciones, igual que las bibliotecas.</p>
  ${figs(TT)}
</div>
<div class="step">
  <div class="layer-chip wip">En desarrollo</div>
  <h3>Capa 4 · Barras de error honestas</h3>
  <p>La capa de arriba pone alrededor de la línea una banda que debería contener el valor verdadero unas dos veces de cada tres (una banda del 68 %): estrecha donde los buenos datos la fijan, más ancha donde no.</p>
  <div class="ctl"><label for="lay-band">Anchura de la banda · mediciones dentro (%)</label><input id="lay-band" type="range" data-bind="band" min="0.2" max="2.5" step="0.05" value="1"><output data-show="inside" data-fmt="0"></output></div>
  <p>Arrástrala y cuenta las mediciones que quedan dentro. Demasiado estrecha, y la banda promete una precisión que no tiene; demasiado ancha, y no dice nada. La banda del propio motor aún no está adoptada: acierta cuando se juntan todas las reacciones, pero todavía no en cada familia de reacciones. TERRA lleva sus propias bandas, y forman parte de sus comparaciones de arriba.</p>
</div>
<div class="step">
  <h3>Estado actual</h3>
  <p>Una capa solo se adopta después de probarla frente a las mediciones, y se queda apagada si no ayuda. Hoy el motor está en uso y TERRA es candidata; la capa de estructura medida y la banda de incertidumbre del motor siguen en pruebas.</p>
  <p><a href="scoreboard.html" data-keep-lang>Ver el marcador completo →</a> Todas las comparaciones que no ganamos, cada rival y cómo leerlo.</p>
  <div class="aside">${ASOF ? `Resultados a ${ASOF}, del` : "Resultados del"} registro de investigación del proyecto. Las curvas del dibujo son ilustrativas.</div>
</div>`,
  };
})();
Object.assign(WT.es.labels, {
  "{#} · engine": "{#} · motor",
  "{#} · measured structure": "{#} · estructura medida",
  "{#} · TERRA: anchored to data": "{#} · TERRA: anclado a los datos",
  "{#} · uncertainty band": "{#} · banda de incertidumbre",
  "measured here": "medido aquí",
  "neutron energy →": "energía del neutrón →",
  "how often the reaction happens": "con qué frecuencia ocurre la reacción",
  "hollow dots: measurements the engine is compared with": "puntos huecos: mediciones con las que se compara el motor",
  "own measured values: the line barely moves": "valores medidos propios: la línea apenas se mueve",
  "global rule": "regla global",
  "no measurements: TERRA falls back to the engine": "sin mediciones: TERRA vuelve al motor",
  "solid: follows the data · dashed: the engine alone": "continua: sigue los datos · discontinua: solo el motor",
  "{#} of {#} measurements inside the band (aim: about {#} %)": "{#} de {#} mediciones dentro de la banda (objetivo: un {#} %)",
  "no measurements to check the band against": "no hay mediciones con las que comprobar la banda",
});
Object.assign(WT.es.ui, { nav_board: "Marcador" });
/* attributes referenced in the English chapter script (for the structure check): data-act="${act}" */
