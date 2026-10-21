/* Spanish: layers (chapter 12) */
WT.es.ch.layers = {
  num: "Capítulo 12", title: "Cómo se organiza el modelo en capas", short: "Capas",
  lead: "Todo lo anterior era un solo motor. Lo que de verdad entregamos se construye en capas sobre él, y cada capa tiene que ganarse su sitio frente a las mediciones.",
  html: `
<div class="step">
  <div class="layer-chip on">En uso</div>
  <h3>Capa 1 · Una regla para cada núcleo</h3>
  <p>El motor que acabas de recorrer es la capa de abajo. Aplica la misma física, con los mismos ajustes globales, a todos los núclidos, y nunca se ajusta a las secciones eficaces con las que se le juzga. La línea azul es su predicción para una reacción.</p>
  <div class="btns"><button class="btn ghost" data-act="reveal" aria-pressed="false">Mostrar las mediciones</button></div>
  <p>Eso es lo que lo hace comprobable: se puntúa con mediciones que nunca vio, frente a otros códigos de modelos calculados sobre los mismos núcleos. A 21 de octubre de 2026 va por delante, con todo el intervalo del 95 % por debajo de cero, en 53 de 71 de esas comparaciones, empata en 17 y va por detrás en 1.</p>
  <div class="figs" aria-label="53 victorias, 17 empates, 1 derrota"><div class="w"><b>53</b><span>victoria</span></div><div><b>17</b><span>empate</span></div><div class="l"><b>1</b><span>derrota</span></div></div>
</div>
<div class="step">
  <div class="layer-chip null">Probada: aún sin mejora</div>
  <h3>Capa 2 · Las mediciones propias de cada núcleo</h3>
  <p>Algunas propiedades de un núcleo se miden directamente: cuánto se separan sus resonancias (el espaciado de niveles D0), con qué facilidad absorbe neutrones lentos (las funciones de fuerza S0 y S1), con qué rapidez emite rayos gamma (⟨Γγ⟩) y sus niveles de energía conocidos. La segunda capa da a cada núcleo sus propios valores medidos en lugar de la regla global.</p>
  <div class="btns"><button class="btn ghost" data-act="ms0" aria-pressed="true">Regla global</button><button class="btn ghost" data-act="ms1" aria-pressed="false">Mediciones propias</button></div>
  <p>Actívala y la línea apenas se mueve. Ese es el resultado honesto de hoy. Las últimas pruebas fueron a por las comparaciones que no ganamos y no encontraron mejora: ajustar al ⟨Γγ⟩ medido movió la captura en la dirección equivocada, el S0 medido no siguió los fallos, y un ajuste de la densidad de niveles núcleo a núcleo alejó de los datos a las tierras raras. En parte se debe a que el motor ya usa el S1 y el D0 medidos para esos núcleos. Un resultado apunta en la otra dirección: ajustar la densidad de niveles de cada núcleo a sus propios niveles y D0 medidos convierte la única derrota que queda, (n,p) cerca de su umbral, en un empate, pero empeora la captura de neutrones, así que por ahora la capa sigue apagada.</p>
</div>
<div class="step">
  <div class="layer-chip cand">Candidata</div>
  <h3>Capa 3 · Seguir los buenos datos (TERRA)</h3>
  <p>Donde una reacción se ha medido bien, la mejor estimación debe seguir a las mediciones. La tercera capa, TERRA, toma la línea del motor y, donde hay buenos datos, hace pasar el resultado por ellos. Donde no los hay, vuelve al motor.</p>
  <div class="ctl"><label for="lay-cov">Parte del rango de energía medida (%)</label><input id="lay-cov" type="range" data-bind="cov" min="0" max="1" step="0.01" value="0.45"><output data-show="covPct" data-fmt="0"></output></div>
  <p>Frente a las cuatro grandes bibliotecas de datos evaluados (ENDF/B-VIII.1, JEFF-4.0, JENDL-5 y TENDL-2025), el candidato actual, R072w del 11 de octubre de 2026, va por delante en 217 de 326 comparaciones, empata en 108 y va por detrás en 1. La mayoría son dentro de la muestra: TERRA ha visto esas mediciones, igual que las bibliotecas. Está en curso una reconstrucción sobre el motor actual, R073.</p>
  <div class="figs" aria-label="217 victorias, 108 empates, 1 derrota"><div class="w"><b>217</b><span>victoria</span></div><div><b>108</b><span>empate</span></div><div class="l"><b>1</b><span>derrota</span></div></div>
</div>
<div class="step">
  <div class="layer-chip wip">En desarrollo</div>
  <h3>Capa 4 · Barras de error honestas</h3>
  <p>Un número sin incertidumbre es media respuesta. La capa de arriba pone alrededor de la línea una banda que debería contener el valor verdadero unas dos veces de cada tres (una banda del 68 %): estrecha donde los buenos datos la fijan, más ancha donde no.</p>
  <div class="ctl"><label for="lay-band">Anchura de la banda · mediciones dentro (%)</label><input id="lay-band" type="range" data-bind="band" min="0.2" max="2.5" step="0.05" value="1"><output data-show="inside" data-fmt="0"></output></div>
  <p>Arrástrala y cuenta las mediciones que quedan dentro. Demasiado estrecha, y la banda promete una precisión que no tiene; demasiado ancha, y no dice nada. La banda del propio motor aún no está adoptada. La última versión acierta cuando se juntan todas las reacciones (73 % dentro de su banda del 68 %, 95 % dentro de su banda del 95 %), pero ninguna variante cumple aún los dos objetivos en cada una de las seis familias de reacciones. TERRA lleva sus propias bandas, y forman parte de sus comparaciones de arriba.</p>
</div>
<div class="step">
  <h3>Dónde estamos</h3>
  <p>Una capa solo se adopta después de probarla frente a las mediciones, y se queda apagada si no ayuda. Hoy el motor está en uso y TERRA es candidata; la capa de estructura medida y la banda de incertidumbre del motor siguen en pruebas.</p>
  <p><a href="scoreboard.html" data-keep-lang>Ver el marcador completo →</a> Todas las comparaciones que no ganamos, cada rival y cómo leerlo.</p>
  <div class="aside">Cifras a 21 de octubre de 2026, del registro de investigación del proyecto. Las curvas del dibujo son ilustrativas.</div>
</div>`,
};
Object.assign(WT.es.labels, {
  "{#} · blind engine": "{#} · motor ciego",
  "{#} · measured structure": "{#} · estructura medida",
  "{#} · TERRA: anchored to data": "{#} · TERRA: anclado a los datos",
  "{#} · uncertainty band": "{#} · banda de incertidumbre",
  "measured here": "medido aquí",
  "neutron energy →": "energía del neutrón →",
  "how often the reaction happens": "con qué frecuencia ocurre la reacción",
  "hollow dots: measurements the engine never saw": "puntos huecos: mediciones que el motor nunca vio",
  "own measured values: the line barely moves": "valores medidos propios: la línea apenas se mueve",
  "global rule": "regla global",
  "no measurements: TERRA falls back to the engine": "sin mediciones: TERRA vuelve al motor",
  "solid: follows the data · dashed: the engine alone": "continua: sigue los datos · discontinua: solo el motor",
  "{#} of {#} measurements inside the band (aim: about {#} %)": "{#} de {#} mediciones dentro de la banda (objetivo: un {#} %)",
  "no measurements to check the band against": "no hay mediciones con las que comprobar la banda",
});
Object.assign(WT.es.ui, { nav_board: "Marcador" });
