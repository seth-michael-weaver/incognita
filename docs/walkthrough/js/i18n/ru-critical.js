/* Russian: critical (Глава 21, критичность и управление реактором) */
/* (structure-check parity with ch/critical.js script selectors: data-act="delayed" data-act="delayed") */
WT.L.ch.critical = {
  num: "Глава 21", title: "Критичность и управление реактором", short: "Критичность",
  html: `
<div class="step">
  <h3>Коэффициент размножения</h3>
  <p>Каждое деление высвобождает несколько нейтронов; одни вызывают следующие деления, остальные теряются. <b>Коэффициент размножения</b> <i>k</i> показывает, к скольким новым делениям приводит одно деление: с каждым поколением число нейтронов умножается на <i>k</i>. При <i>k</i> больше 1 цепная реакция нарастает, при меньше 1 — затухает.</p>
  <div class="ctl"><label for="cri-k">Коэффициент размножения k</label><input id="cri-k" type="range" data-bind="k" data-instant min="0.95" max="1.05" step="0.05" value="1.05"><output data-show="k" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Запаздывающие нейтроны</h3>
  <p>Небольшая доля нейтронов (0,65 %) появляется с опозданием в секунды — от осколков деления, которые сначала должны распасться. Именно эти запоздавшие нейтроны задают темп, поэтому нарастание замедляется от мгновения до минут. График идёт в ускорении ×10.</p>
  <div class="ctl"><label for="cri-k2">Коэффициент размножения k</label><input id="cri-k2" type="range" data-bind="kd" data-instant min="0.998" max="1.002" step="0.0005" value="1.001"><output data-show="kd" data-fmt="4"></output></div>
  <div class="btns"><button class="btn ghost" data-act="delayed" aria-pressed="true">Запаздывающие нейтроны</button></div>
</div>
<div class="step">
  <h3>Критичность</h3>
  <p>Критический эксперимент: перемещайте регулирующие стержни, пока мощность не перестанет меняться. При таком положении <i>k</i> в точности равно 1, а положение стержней и есть результат измерения. Найдите его: индикатор показывает <i>k</i> с пятью знаками после запятой.</p>
  <div class="ctl"><label for="cri-rod">Стержни введены (%)</label><input id="cri-rod" type="range" data-bind="ins" data-instant min="35" max="75" step="1" value="45"><output data-show="ins" data-fmt="0"></output></div>
</div>`,
};
