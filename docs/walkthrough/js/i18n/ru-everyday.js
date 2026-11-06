/* Russian: everyday (Ядерная физика в повседневной жизни) */
WT.L.ch.everyday = {
  num: "Урок 4", title: "Ядерная физика в повседневной жизни", short: "Повседневное",
  html: `
<div class="step">
  <h3>ПЭТ</h3>
  <p>Индикатор с фтором-18 (период полураспада 110 минут) испускает позитроны, и каждый превращается в два гамма-кванта по 511 кэВ, разлетающихся в противоположные стороны. Перетащите горячую точку: кольцо проводит линию для каждой пары, и линии пересекаются там, где находится индикатор.</p>
</div>
<div class="step">
  <h3>Лучевая терапия</h3>
  <p>Пучки с нескольких направлений сходятся на опухоли, так что она получает полную дозу, а каждый путь через здоровые ткани — лишь её долю. Перетаскивайте, чтобы поворачивать пучки и уводить их от спинного мозга.</p>
  <div class="ctl"><label for="ev-n">Пучки</label><input id="ev-n" type="range" data-bind="nb" data-instant min="1" max="7" step="1" value="5"><output data-show="nb" data-fmt="0"></output></div>
  <div class="ctl"><label for="ev-r">Поворот</label><input id="ev-r" type="range" data-bind="rotd" data-instant min="0" max="360" step="1" value="20"><output class="ev-rot"></output></div>
</div>
<div class="step">
  <h3>Технеций-99m</h3>
  <p>Изотоп, на котором основано большинство сцинтиграфических исследований, испускает гамма-квант 140 кэВ, который видит камера снаружи тела, а при периоде полураспада 6 часов через сутки от него остаётся мало. Больницы <a href="#chains-3">«доят» его из молибдена-99</a>.</p>
  <div class="ctl"><label for="ev-t">Часы после введения</label><input id="ev-t" type="range" data-bind="th" data-instant min="0" max="48" step="0.5" value="0"><output data-show="th" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Радиоуглеродное датирование</h3>
  <p>Живые организмы постоянно поглощают углерод-14; после смерти он распадается с периодом полураспада 5730 лет. Задайте возраст или измерьте остаток, чтобы определить возраст.</p>
  <div class="ctl"><label for="ev-a">Возраст (лет)</label><input id="ev-a" type="range" data-bind="age" data-instant min="0" max="50000" step="10" value="5300"><output class="ev-age"></output></div>
  <div class="ctl"><label for="ev-f">Осталось углерода-14 (%)</label><input id="ev-f" type="range" data-bind="fr" data-instant min="0.3" max="100" step="0.1" value="52.7"><output class="ev-fr"></output></div>
</div>
<div class="step">
  <h3>Дымовые извещатели</h3>
  <p>Запаянная крупинка америция-241 посылает альфа-частицы через небольшой воздушный зазор, создавая ионы, которые переносят крошечный ток. Дым захватывает ионы, ток падает, и срабатывает сигнал.</p>
  <div class="ctl"><label for="ev-s">Дым</label><input id="ev-s" type="range" data-bind="sm" data-instant min="0" max="1" step="0.01" value="0"><output class="ev-sm"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "Am{#}": "Am{#}",
  "Mo{#} ({#} h)": "Mo{#} ({#} ч)",
  "Tc{#}m ({#} h)": "Tc{#}m ({#} ч)",
  "a strong gamma signal, easy to image": "сильный гамма-сигнал, легко получить снимок",
  "alarm": "сигнал",
  "alpha particles make ions in the air": "альфа-частицы ионизируют воздух",
  "americium{#} (sealed)": "америций{#} (запаян)",
  "americium{#} · half-life {#} years · alphas reach about {#} cm in air": "америций{#} · период полураспада {#} лет · пробег альфа в воздухе около {#} см",
  "beyond ~{#} years too little is left to measure": "после ~{#} лет остаётся слишком мало для измерения",
  "carbon{#}": "углерод{#}",
  "clean air: steady current": "чистый воздух: ток постоянен",
  "current": "ток",
  "detector ring": "кольцо детекторов",
  "dose": "доза",
  "fluorine{#} · half-life {#} min · {#} pairs recorded": "фтор{#} · период полураспада {#} мин · зарегистрировано пар: {#}",
  "gamma camera": "гамма-камера",
  "half-life {#} y": "период полураспада {#} лет",
  "illustration": "иллюстрация",
  "molybdenum{#}, half-life {#} h": "молибден{#}, период полураспада {#} ч",
  "nitrogen{#} (after a beta decay)": "азот{#} (после бета-распада)",
  "pairs of {#} keV gamma rays, back to back": "пары гамма-квантов {#} кэВ, в противоположные стороны",
  "physical decay only": "только физический распад",
  "spinal cord": "спинной мозг",
  "technetium{#}m, half-life {#} h": "технеций{#}m, период полураспада {#} ч",
  "tracer": "индикатор",
  "tumour": "опухоль",
  "tumour {#} % · spinal cord {#} % · healthy tissue at most {#} %": "опухоль {#} % · спинной мозг {#} % · здоровые ткани не более {#} %",
  "tumour {#} % · spinal cord {#} % · other tissue at most {#} %": "опухоль {#} % · спинной мозг {#} % · прочие ткани не более {#} %",
  "years": "лет",
  "{#} beams cross: the tumour gets their sum": "пересекаются пучков: {#}; опухоль получает их сумму",
  "{#} h": "{#} ч",
  "{#} h: {#} % left": "{#} ч: осталось {#} %",
  "{#} half-lives": "периодов полураспада: {#}",
  "{#} keV gamma rays": "гамма-кванты {#} кэВ",
  "{#} of {#} left": "осталось {#} из {#}",
  "{#} years · {#} % left": "{#} лет · осталось {#} %",
  "Ötzi the Iceman, ~{#} y": "Эци, ледяной человек, ~{#} лет",
  "tracer (drag me)": "индикатор (перетащите)",
  "each decay: two {#} keV gamma rays, back to back": "каждый распад: два гамма-кванта {#} кэВ в противоположные стороны",
  "one beam: more dose near the skin than in the tumour": "один пучок: у кожи доза больше, чем в опухоли",
  "a beam crosses the spinal cord: turn the beams": "пучок проходит через спинной мозг: поверните пучки",
  "fading: half is gone every {#} hours": "угасает: каждые {#} часов уходит половина",
  "after a day, about {#} % is left": "через сутки остаётся около {#} %",
  "nitrogen{#}": "азот{#}",
  "~{#} y: too little to measure": "~{#} лет: слишком мало для измерения",
  "smoke: current down, alarm!": "дым: ток упал, тревога!",
  "some ions caught: current dipping": "часть ионов захвачена: ток падает",
});
