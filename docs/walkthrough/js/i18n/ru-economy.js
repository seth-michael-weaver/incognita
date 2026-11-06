/* Russian: economy (Нейтронный баланс) */
WT.L.ch.economy = {
  num: "Урок 1", title: "Нейтронный баланс", short: "Нейтронный баланс",
  html: `
<div class="step">
  <h3>Тысяча нейтронов</h3>
  <p>Проследите за 1000 быстрых нейтронов в течение одного поколения. Несколько вызывают дополнительные деления, часть утекает наружу, часть захватывается по пути, а остальные делят уран-235 и дают следующую тысячу. Шесть множителей в произведении дают <i>k</i> = <i>η f p ε P</i><sub>FNL</sub> <i>P</i><sub>TNL</sub>.</p>
</div>
<div class="step">
  <h3>Обогащение</h3>
  <p>Чем больше урана-235 в топливе, тем больше нейтронов поглощается там, где они вызывают деление. С природным ураном (0,7 %) и обычной водой <i>k</i> никогда не достигает 1.</p>
  <div class="ctl"><label for="eco-e">Уран-235 (%)</label><input id="eco-e" type="range" data-bind="enr" min="0.7" max="5" step="0.1" value="3"><output data-show="enr" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Вода между стержнями</h3>
  <p>Слишком мало воды — и замедляющиеся нейтроны захватывает уран-238; слишком много — и их поглощает сама вода. Есть наилучшее соотношение, и водяные реакторы строят чуть ниже него.</p>
  <div class="ctl"><label for="eco-m">Вода на топливо (× типичное)</label><input id="eco-m" type="range" data-bind="m" min="0.3" max="4" step="0.05" value="1"><output data-show="m" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Размер</h3>
  <p>Нейтроны, родившиеся у поверхности, могут вылететь наружу. Малая активная зона теряет их слишком много, большая удерживает. Найдите размер, при котором <i>k</i> переходит через 1.</p>
  <div class="ctl"><label for="eco-s">Размер зоны (× типичный)</label><input id="eco-s" type="range" data-bind="s" min="0.3" max="2" step="0.05" value="0.6"><output data-show="s" data-fmt="2"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "fast fission": "деление быстрыми",
  "fast leak": "утечка быстрых",
  "leaks out, fast": "утечка, быстрые",
  "U{#} catches": "захват U{#}",
  "caught by U{#}": "захвачены U{#}",
  "slow leak": "утечка медленных",
  "leaks out, slow": "утечка, медленные",
  "water, steel…": "вода, сталь…",
  "water, steel, boron": "вода, сталь, бор",
  "P fast {#}": "P быстр. {#}",
  "P slow {#}": "P медл. {#}",
  "p {#}": "p {#}",
  "f {#}": "f {#}",
  "slowing": "замедление",
  "slowing down": "замедление",
  "{#} split U{#}": "{#} делят U{#}",
  "U{#}": "U{#}",
  "next: {#}": "дальше: {#}",
  "next generation: {#}": "следующее поколение: {#}",
  "k = {#}": "k = {#}",
  "critical: steady": "критично: постоянно",
  "grows": "нарастает",
  "dies away": "затухает",
  "best ≈ {#}×": "оптимум ≈ {#}×",
  "less water": "меньше воды",
  "more water": "больше воды",
  "{#} % leak out": "{#} % утекает",
  "k = η {#} × f {#} × p {#} × ε {#} × P {#} × P {#}": "k = η {#} × f {#} × p {#} × ε {#} × P {#} × P {#}",
  "textbook set (D&H); trends illustrative": "учебный набор (D&H); тренды условны",
  "factors: textbook set (Duderstadt & Hamilton) at {#} %; slider trends illustrative": "множители: учебный набор (Duderstadt & Hamilton) при {#} %; тренды ползунков условны",
});
