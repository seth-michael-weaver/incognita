/* Russian: waste (Отработавшее топливо во времени) */
WT.L.ch.waste = {
  num: "Урок 1", title: "Отработавшее топливо во времени", short: "Отработавшее топливо",
  html: `
<div class="step">
  <h3>Что выходит из реактора</h3>
  <p>После четырёх-пяти лет в активной зоне топливная таблетка по-прежнему состоит в основном из урана. Несколько процентов составляют <b>продукты деления</b> — расколотые атомы. Около 1 % приходится на плутоний, и есть следы более тяжёлых <b>младших актинидов</b>, например америция.</p>
  <div class="btns"><button class="btn" data-act="sort">Рассортировать атомы</button></div>
</div>
<div class="step">
  <h3>Первые столетия</h3>
  <p>Кривая сравнивает опасность отработавшего топлива при попадании внутрь с опасностью урановой руды, из которой оно сделано. Сначала преобладают продукты деления, но у большинства из них период полураспада около 30 лет: примерно через 300 лет их вклад опускается ниже уровня руды.</p>
  <div class="ctl"><label for="wst-t1">Лет после выгрузки</label><input id="wst-t1" type="range" data-bind="lt" data-instant min="0" max="6" step="0.01" value="1.5"><output data-show="yr" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Затем плутоний</h3>
  <p>Остаются плутоний и америций с периодами полураспада от сотен до десятков тысяч лет. Они держат отработавшее топливо выше уровня руды больше ста тысяч лет.</p>
  <div class="ctl"><label for="wst-t2">Лет после выгрузки</label><input id="wst-t2" type="range" data-bind="lt" data-instant min="0" max="6" step="0.01" value="4"><output data-show="yr" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Переработка и трансмутация</h3>
  <p>Если извлечь плутоний и сжечь его как новое топливо, срок сокращается примерно до десяти тысяч лет. Если ещё и разделить младшие актиниды в быстрых реакторах, останутся только продукты деления: несколько сотен лет.</p>
  <div class="btns"><button class="btn ghost" data-act="rp" aria-pressed="false">Переработать плутоний</button><button class="btn ghost" data-act="tm" aria-pressed="false">Трансмутировать младшие актиниды</button></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "Sort the atoms": "Рассортировать атомы",
  "Mix them again": "Снова перемешать",
  "uranium": "уран",
  "fission products": "продукты деления",
  "fission prod.": "продукты дел.",
  "plutonium": "плутоний",
  "minor actinides": "младшие актиниды",
  "minor act.": "младшие акт.",
  "a used fuel pellet, {#} atoms": "отработавшая таблетка, {#} атомов",
  "a used fuel pellet, {#} atoms shown": "отработавшая топливная таблетка, показано {#} атомов",
  "the glow: fission products are the most radioactive": "свечение: продукты деления радиоактивнее всего",
  "the glow: the fission products are by far the most radioactive part": "свечение: продукты деления — намного более радиоактивная часть, чем остальное",
  "spent fuel": "отработавшее топливо",
  "spent fuel, one tonne": "отработавшее топливо, одна тонна",
  "the ore": "руда",
  "the ore it was made from": "руда, из которой его сделали",
  "{#} yr": "{#} г.",
  "{#} million": "{#} млн",
  "uranium ore level": "уровень урановой руды",
  "the uranium ore it was made from": "урановая руда, из которой его сделали",
  "years after unloading (log scale) →": "лет после выгрузки (лог. шкала) →",
  "hazard vs ore (log)": "опасность к руде (лог.)",
  "hazard if swallowed, relative to the ore (log scale)": "опасность при попадании внутрь относительно руды (лог. шкала)",
  "Am, Cm, Np": "Am, Cm, Np",
  "americium, curium…": "америций, кюрий…",
  "{#} years: {#} × the ore": "{#} г.: {#} × уровень руды",
  "below the ore it came from": "ниже исходной руды",
  "mostly from fission products": "в основном от продуктов деления",
  "mostly from plutonium": "в основном от плутония",
  "mostly from americium": "в основном от америция",
  "recycle + transmute": "переработка + трансмутация",
  "recycle Pu and transmute minor actinides": "переработка Pu и трансмутация младших актинидов",
  "plutonium recycled": "плутоний переработан",
  "plutonium recycled, minor actinides in the waste": "плутоний переработан, младшие актиниды в отходах",
  "only minor actinides removed": "удалены только младшие актиниды",
  "minor actinides removed, plutonium left in": "младшие актиниды удалены, плутоний оставлен",
  "spent fuel as it is": "топливо как есть",
  "spent fuel kept as it is": "отработавшее топливо без переработки",
  "reaches the ore level after ~{#} years": "достигает уровня руды через ~{#} лет",
  "reaches the ore level after ~{#},{#} years": "достигает уровня руды через ~{#} {#} лет",
  "illustrative shape (after OECD-NEA)": "условная форма (по данным OECD-NEA)",
});
