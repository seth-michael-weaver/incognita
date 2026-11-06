/* Russian: rays (Альфа, бета, гамма и нейтроны) */
WT.L.ch.rays = {
  num: "Урок 1", title: "Альфа, бета, гамма и нейтроны", short: "Излучение",
  html: `
<div class="step">
  <h3>Четыре вида излучения</h3>
  <p><em class="a">Альфа-частица</em> — тяжёлый комок из двух протонов и двух нейтронов. <b>Бета-частица</b> — быстрый электрон. <em class="g">Гамма-излучение</em> — это свет, слишком энергичный, чтобы его увидеть. <em class="n">Нейтроны</em> вообще не несут заряда. Каждое излучение останавливает своё.</p>
</div>
<div class="step">
  <h3>Бумага и алюминий</h3>
  <p>Альфа-частицы крупные и заряженные, поэтому сразу врезаются в атомы: их останавливает лист бумаги. Бета-электроны проходят дальше, но и их останавливают несколько миллиметров алюминия.</p>
  <div class="btns"><button class="btn ghost" data-act="sh_paper" aria-pressed="true">Бумага</button><button class="btn ghost" data-act="sh_al" aria-pressed="false">Алюминий</button></div>
</div>
<div class="step">
  <h3>Гамма-лучи: вдвое меньше, но не ноль</h3>
  <p>Гамма-лучи не имеют заряда и обычно пролетают мимо атомов. Каждый сантиметр свинца даёт каждому кванту один и тот же шанс быть поглощённым, поэтому каждый слой уменьшает остаток вдвое. Пучок слабеет, но никогда не исчезает полностью.</p>
  <div class="ctl"><label for="ry-pb">Свинец (cm)</label><input id="ry-pb" type="range" data-bind="pb" data-instant min="0" max="5" step="0.1" value="1"><output data-show="pb" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Нейтроны: свинца мало</h3>
  <p>Нейтрон, отскакивающий от тяжёлого ядра свинца, — как шарик для пинг-понга, ударяющийся о шар для боулинга: он сохраняет скорость. Водород в воде весит столько же, сколько нейтрон, поэтому каждое столкновение его замедляет, пока он не станет достаточно медленным, чтобы быть поглощённым.</p>
  <div class="btns"><button class="btn ghost" data-act="nm_pb" aria-pressed="true">Свинец</button><button class="btn ghost" data-act="nm_water" aria-pressed="false">Вода</button></div>
  <div class="ctl"><label for="ry-nx">Толщина (cm)</label><input id="ry-nx" type="range" data-bind="nx" data-instant min="0" max="60" step="1" value="30"><output data-show="nx" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Постройте защиту</h3>
  <p>Добавляйте слои, пока не будут остановлены все четыре пучка. Гамма-лучи никогда не падают ровно до нуля, лишь до крошечной доли.</p>
  <div class="btns"><button class="btn ghost" data-act="add_paper">+ Бумага</button><button class="btn ghost" data-act="add_al">+ Алюминий</button><button class="btn ghost" data-act="add_pb">+ Свинец</button><button class="btn ghost" data-act="add_water">+ Вода</button><button class="btn" data-act="clear">Очистить</button></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "drag ↔": "тяните ↔",
  "paper": "бумага",
  "aluminium {#} mm": "алюминий {#} mm",
  "Al {#} mm": "Al {#} mm",
  "lead {#} cm": "свинец {#} cm",
  "water {#} cm": "вода {#} cm",
  "no shield": "без защиты",
  "alpha": "альфа", "beta": "бета", "gamma": "гамма", "neutron": "нейтрон",
  "stopped": "остановлено",
  "all through": "проходит всё",
  "{#} % through": "проходит {#} %",
  "{#} in {#}": "{#} из {#}",
  "{#} in {#} million": "{#} из {#} млн",
  "{#} in a billion": "{#} из миллиарда",
  "all four stopped": "все четыре остановлены",
  "all four beams stopped": "все четыре пучка остановлены",
  "flash = stopped inside the shield": "вспышка = остановлено в защите",
  "each source fires a steady beam": "каждый источник даёт ровный пучок",
  "flash = stopped": "вспышка = остановлено",
  "four beams": "четыре пучка",
  "not to scale": "не в масштабе",
  "gamma rays (caesium{#})": "гамма-лучи (цезий{#})",
  "cm of lead": "cm свинца",
  "share still going": "доля, идущая дальше",
  "through: all · halved every {#} mm": "проходит: всё · вдвое на каждые {#} mm",
  "through: {#} % · halved every {#} mm": "проходит: {#} % · вдвое на каждые {#} mm",
  "through: {#} in {#} · halved every {#} mm": "проходит: {#} из {#} · вдвое на каждые {#} mm",
  "gets through: {#} % · halved every {#} mm of lead": "проходит: {#} % · вдвое на каждые {#} mm свинца",
  "gets through: {#} in {#} · halved every {#} mm of lead": "проходит: {#} из {#} · вдвое на каждые {#} mm свинца",
  "counted: {#} of {#}": "сосчитано: {#} из {#}",
  "through {#} % · back {#} % · caught {#} %": "прошли {#} % · назад {#} % · поглощены {#} %",
  "got through {#} % · bounced back {#} % · slowed and caught {#} %": "прошли {#} % · отразились {#} % · замедлены и поглощены {#} %",
  "bright = fast · dim = slowed": "яркие = быстрые · тусклые = замедленные",
  "bright = fast neutron · red = hydrogen nucleus knocked away · green flash = swallowed": "яркий = быстрый нейтрон · красный = выбитое ядро водорода · зелёная вспышка = поглощён",
  "simplified model": "упрощённая модель",
});
