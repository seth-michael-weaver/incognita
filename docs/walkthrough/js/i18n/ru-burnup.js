/* Russian: burnup (Выгорание топлива) */
WT.L.ch.burnup = {
  num: "Урок 1", title: "Выгорание топлива", short: "Выгорание",
  html: `
<div class="step">
  <h3>Таблетка за время работы</h3>
  <p>Перед вами тысяча атомов из свежей топливной таблетки: 45 из них — уран-235, остальные — уран-238. Запустите реактор и смотрите, как уран-235 делится, а на его месте появляются новые атомы. <b>Выгорание</b> измеряет полученную энергию в гигаватт-сутках на тонну урана; в водяных реакторах топливо выгружают примерно при 45–55.</p>
  <div class="ctl"><label for="bu-d1">Сутки на полной мощности</label><input id="bu-d1" type="range" data-bind="d" data-instant min="0" max="1400" step="10" value="400"><output data-show="d" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Подключается плутоний</h3>
  <p>Уран-238 захватывает нейтроны и становится плутонием-239, который тоже делится. К концу работы топлива больше половины делений приходится на плутоний; за всё время он даёт около трети энергии.</p>
  <div class="ctl"><label for="bu-d2">Сутки на полной мощности</label><input id="bu-d2" type="range" data-bind="d" data-instant min="0" max="1400" step="10" value="1000"><output data-show="d" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Накапливаются яды</h3>
  <p>Каждое деление оставляет два продукта деления, и некоторые из них поглощают нейтроны. Урана-235 становится меньше, ядов — больше, и <i>k</i><sub>∞</sub> (число новых делений на одно деление в бесконечной решётке из этого топлива) постепенно снижается, пока топливо уже не может само поддерживать цепную реакцию.</p>
  <div class="ctl"><label for="bu-d3">Сутки на полной мощности</label><input id="bu-d3" type="range" data-bind="d" data-instant min="0" max="1400" step="10" value="700"><output data-show="d" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Бор и перегрузки</h3>
  <p>В активной зоне соседствуют свежее, среднее и старое топливо. У свежего топлива избыток реактивности, поэтому бор, растворённый в охлаждающей воде, поглощает этот избыток и постепенно разбавляется. Когда концентрация бора доходит до нуля, самую старую треть выгружают и загружают свежее топливо.</p>
  <div class="ctl"><label for="bu-m">Месяцы на полной мощности</label><input id="bu-m" type="range" data-bind="m" data-instant min="0" max="54" step="0.5" value="8"><output data-show="m" data-fmt="1"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "illustrative model": "иллюстративная модель",
  "{a} days · burnup {b} GWd/t": "{a} сут · выгорание {b} ГВт·сут/т",
  "uranium{#}": "уран{#}",
  "plutonium{#}": "плутоний{#}",
  "other Pu": "прочий Pu",
  "other plutonium": "прочий плутоний",
  "fission products": "продукты деления",
  "fission products (pairs)": "продукты деления (пары)",
  "{a} in {#}": "{a} из {#}",
  "uranium{#}: the remaining ~{#}–{#} %": "уран{#}: остальные ~{#}–{#} %",
  "plutonium's share": "доля плутония",
  "fissions": "деления",
  "fissions now": "деления сейчас",
  "energy so far": "энергия с начала",
  "U{#}": "U{#}",
  "Pu": "Pu",
  "split": "разделившиеся",
  "plutonium": "плутоний",
  "each dot: {#} atom in {#}": "точка: {#} атом из {#}",
  "each dot: one atom in a thousand": "каждая точка — один атом из тысячи",
  "k = {#}": "k = {#}",
  "GWd/t →": "ГВт·сут/т →",
  "burnup (GWd/t) →": "выгорание (ГВт·сут/т) →",
  "typical discharge": "обычная выгрузка",
  "typical discharge {#}–{#}": "обычная выгрузка {#}–{#}",
  "can't keep a chain going alone": "само цепь не поддержит",
  "this fuel alone can no longer keep a chain going": "это топливо само уже не поддерживает цепную реакцию",
  "k∞ reaches {#}": "k∞ доходит до {#}",
  "k∞ = {a}": "k∞ = {a}",
  "fission products catch {a} % of neutrons": "продукты деления захватывают {a} % нейтронов",
  "fresh": "свежее",
  "{#} cycle": "{#} цикл",
  "one cycle old": "отработало один цикл",
  "{#} cycles": "{#} цикла",
  "two cycles old": "отработало два цикла",
  "reload": "перегрузка",
  "boron (ppm)": "бор (ppm)",
  "boron in the water (ppm)": "бор в воде (ppm)",
  "months →": "месяцы →",
  "months at full power →": "месяцы на полной мощности →",
  "{a} ppm": "{a} ppm",
  "cycle {a} months · fuel leaves at {b} GWd/t": "цикл {a} мес. · топливо выгружают при {b} ГВт·сут/т",
});
