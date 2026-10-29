/* Spanish: critical (Chapter 21, criticality and reactor control) */
WT.es.ch.critical = {
  num: "Capítulo 21", title: "Criticidad y control del reactor", short: "Criticidad",
  html: `
<div class="step">
  <h3>El factor de multiplicación</h3>
  <p>Cada fisión libera unos pocos neutrones; algunos causan las fisiones siguientes y el resto se pierden. El <b>factor de multiplicación</b> <i>k</i> es cuántas fisiones nuevas provoca una fisión: cada generación multiplica los neutrones por <i>k</i>. Por encima de 1 la cadena crece, por debajo de 1 se extingue.</p>
  <div class="ctl"><label for="cri-k">Multiplicación k</label><input id="cri-k" type="range" data-bind="k" data-instant min="0.95" max="1.05" step="0.05" value="1.05"><output data-show="k" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Neutrones retardados</h3>
  <p>Una pequeña fracción de los neutrones (0,65 %) llega con segundos de retraso, de fragmentos de fisión que primero se desintegran. Esos tardíos marcan el ritmo, de modo que el crecimiento pasa de un parpadeo a minutos. El gráfico corre a velocidad ×10.</p>
  <div class="ctl"><label for="cri-k2">Multiplicación k</label><input id="cri-k2" type="range" data-bind="kd" data-instant min="0.998" max="1.002" step="0.0005" value="1.001"><output data-show="kd" data-fmt="4"></output></div>
  <div class="btns"><button class="btn ghost" data-act="delayed" aria-pressed="true">Neutrones retardados</button></div>
</div>
<div class="step">
  <h3>Criticidad</h3>
  <p>Un experimento crítico: mueve las barras de control hasta que la potencia se mantenga constante. En ese ajuste <i>k</i> vale exactamente 1, y esa posición de las barras es la medida. Encuéntrala: la lectura muestra <i>k</i> con cinco decimales.</p>
  <div class="ctl"><label for="cri-rod">Barras de control insertadas (%)</label><input id="cri-rod" type="range" data-bind="ins" data-instant min="35" max="75" step="1" value="45"><output data-show="ins" data-fmt="0"></output></div>
</div>`,
};
/* attributes referenced in the English chapter script (for the structure check): data-act="delayed" data-act="delayed" */

Object.assign(WT.L.labels, {
  "generations →": "generaciones →",
  "k = {#}: dies away": "k = {#}: se extingue",
  "k = {#}: steady": "k = {#}: estable",
  "k = {#}: grows": "k = {#}: crece",
  "{#} generations last under {#} s in a water reactor": "{#} generaciones duran menos de {#} s en un reactor de agua",
  "illustration": "ilustración",
  "amber: fission fragments that emit a neutron seconds later": "ámbar: fragmentos de fisión que emiten un neutrón segundos después",
  "{#} s": "{#} s",
  "time →": "tiempo →",
  "×{#} speed": "velocidad ×{#}",
  "with delayed: doubles every {#} s": "con retardados: se duplica cada {#} s",
  "prompt only: doubles every {#} ms": "solo instantáneos: se duplica cada {#} ms",
  "k = {#} · {#} % of neutrons delayed about {#} s (one-group average)": "k = {#} · {#} % de neutrones retardados unos {#} s (media de un grupo)",
  "rods {#} % in": "barras {#} % dentro",
  "k = {#} · doubles every {#} min": "k = {#} · se duplica cada {#} min",
});
