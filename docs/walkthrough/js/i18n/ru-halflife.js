/* Russian: halflife (Радиоактивность и период полураспада) */
WT.L.ch.halflife = {
  num: "Урок 1", title: "Радиоактивность и период полураспада", short: "Полураспад",
  lead: "Некоторые атомы нестабильны: рано или поздно их ядро распадается, испускает излучение и превращается в другое. Никто не скажет, когда распадётся отдельное ядро, но образец в целом идёт точно, как часы.",
  html: `
<div class="step">
  <h3>Образец, распадающийся случайно</h3>
  <p>Каждый светящийся шарик — нестабильное ядро. Любое из них может распасться в любой момент: испустить вспышку излучения и превратиться в спокойный стабильный атом. Нажмите на ядро, чтобы оно распалось.</p>
  <div class="btns"><button class="btn" data-act="refill">Свежий образец</button></div>
</div>
<div class="step">
  <h3>Половина, затем ещё половина</h3>
  <p>Никто не скажет, какое ядро распадётся следующим, но вся совокупность предсказуема: через один <b>период полураспада</b> остаётся около половины, через два — четверть, затем восьмая часть. Сделайте период полураспада длиннее или короче.</p>
  <div class="ctl"><label for="hl-th">Период полураспада (секунды)</label><input id="hl-th" type="range" data-bind="Th" data-instant min="1" max="8" step="0.5" value="3"><output data-show="Th" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="refill">Свежий образец</button></div>
</div>
<div class="step">
  <h3>У ядер нет памяти</h3>
  <p>Проследите за одним уцелевшим ядром. Сколько бы оно уже ни прожило, его шанс продержаться ещё один период полураспада по-прежнему один к двум: ядро не стареет.</p>
  <div class="btns"><button class="btn ghost" data-act="tag">Следить за другим</button><button class="btn ghost" data-act="refill">Свежий образец</button></div>
</div>
<div class="step">
  <h3>Реальные периоды полураспада</h3>
  <p>У реальных изотопов они составляют от дней до миллиардов лет. На этой растянутой оси времени каждый изотоп обрывается вниз на своём периоде полураспада. Выберите изотоп и сдвигайте время вперёд.</p>
  <div class="btns"><button class="btn ghost" data-act="iso0" aria-pressed="false">Иод-131</button><button class="btn ghost" data-act="iso1" aria-pressed="true">Цезий-137</button><button class="btn ghost" data-act="iso2" aria-pressed="false">Углерод-14</button><button class="btn ghost" data-act="iso3" aria-pressed="false">Уран-238</button></div>
  <div class="ctl"><label for="hl-t1">Прошло времени</label><input id="hl-t1" type="range" data-bind="lt" data-instant min="3" max="17.8" step="0.02" value="8.98"><output class="hl-tout"></output></div>
</div>
<div class="step">
  <h3>Активность: распады в секунду</h3>
  <p>По одному грамму каждого изотопа рядом. Короткий период полураспада означает много распадов каждую секунду, но недолго; при длинном образец слабо светится веками. Сдвигайте время и смотрите, как лампы гаснут одна за другой.</p>
  <div class="ctl"><label for="hl-t2">Прошло времени</label><input id="hl-t2" type="range" data-bind="lt" data-instant min="3" max="17.8" step="0.02" value="4.94"><output class="hl-tout"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "survived {#} half-lives": "прожило {#} периода полураспада",
  "chance to last one more: {#} in {#}": "шанс прожить ещё один: {#} к {#}",
  "survived {#} half-lives · still {#} in {#}": "прожило {#} периода · всё ещё {#} к {#}",
  "it popped: follow another": "распалось: следим за другим",
  "{#} of {#} still unstable": "{#} из {#} ещё нестабильны",
  "{#} half-life": "{#} период",
  "half-lives →": "периоды полураспада →",
  "nuclei left": "осталось ядер",
  "{#} of {#} left · half-life {#} s": "осталось {#} из {#} · период полураспада {#} s",
  "every survivor has the same {#}-in{#} chance per half-life": "у каждого уцелевшего ядра тот же шанс {#} к {#} за период полураспада",
  "every survivor has the same 1-in-2 chance per half-life": "у каждого уцелевшего ядра тот же шанс 1 к 2 за период полураспада",
  "illustrative half-life": "условный период полураспада",
  "{#} hour": "{#} ч", "{#} h": "{#} ч",
  "{#} day": "{#} сут", "{#} d": "{#} сут",
  "{#} year": "{#} год", "{#} yr": "{#} г.",
  "{#} years": "{#} лет",
  "{#}³ yr": "{#}³ лет", "{#}⁶ yr": "{#}⁶ лет", "{#}⁹ yr": "{#}⁹ лет",
  "{#} million years": "{#} млн лет",
  "{#} billion years": "{#} млрд лет",
  "drag": "тяните",
  "iodine{#} · half-life {#} days": "иод{#} · период полураспада {#} сут",
  "caesium{#} · half-life {#} years": "цезий{#} · период полураспада {#} лет",
  "carbon{#} · half-life {#} years": "углерод{#} · период полураспада {#} лет",
  "uranium{#} · half-life {#} billion years": "уран{#} · период полураспада {#} млрд лет",
  "medicine, fission product": "медицина, продукт деления",
  "fission product": "продукт деления",
  "radiocarbon dating": "радиоуглеродное датирование",
  "natural uranium": "природный уран",
  "I{#}": "I{#}", "Cs{#}": "Cs{#}", "C{#}": "C{#}", "U{#}": "U{#}",
  "iodine{#}": "иод{#}", "caesium{#}": "цезий{#}", "carbon{#}": "углерод{#}", "uranium{#}": "уран{#}",
  "all": "все",
  "{#} % left after {#} minutes": "осталось {#} % через {#} мин",
  "{#} % left after {#} hours": "осталось {#} % через {#} ч",
  "{#} % left after {#} days": "осталось {#} % через {#} сут",
  "{#} % left after {#} months": "осталось {#} % через {#} мес.",
  "{#} % left after {#} years": "осталось {#} % через {#} лет",
  "{#} % left after {#} thousand years": "осталось {#} % через {#} тыс. лет",
  "{#} % left after {#} million years": "осталось {#} % через {#} млн лет",
  "{#} % left after {#} billion years": "осталось {#} % через {#} млрд лет",
  "under {#} % left after {#} minutes": "осталось меньше {#} % через {#} мин",
  "under {#} % left after {#} hours": "осталось меньше {#} % через {#} ч",
  "under {#} % left after {#} days": "осталось меньше {#} % через {#} сут",
  "under {#} % left after {#} months": "осталось меньше {#} % через {#} мес.",
  "under {#} % left after {#} years": "осталось меньше {#} % через {#} лет",
  "under {#} % left after {#} thousand years": "осталось меньше {#} % через {#} тыс. лет",
  "under {#} % left after {#} million years": "осталось меньше {#} % через {#} млн лет",
  "under {#} % left after {#} billion years": "осталось меньше {#} % через {#} млрд лет",
  "½ {#} days": "½ {#} сут", "½ {#} years": "½ {#} лет",
  "½ {#} billion years": "½ {#} млрд лет", "½ {#} bn years": "½ {#} млрд лет",
  "~{#} /s": "~{#} /s", "almost none": "почти нет",
  "{#} /s": "{#} /s", "under {#} /s": "меньше {#} /s",
  "{#}×{#}³ /s": "{#}×{#}³ /s", "{#}×{#}⁴ /s": "{#}×{#}⁴ /s", "{#}×{#}⁵ /s": "{#}×{#}⁵ /s",
  "{#}×{#}⁶ /s": "{#}×{#}⁶ /s", "{#}×{#}⁷ /s": "{#}×{#}⁷ /s", "{#}×{#}⁸ /s": "{#}×{#}⁸ /s",
  "{#}×{#}⁹ /s": "{#}×{#}⁹ /s", "{#}×{#}¹⁰ /s": "{#}×{#}¹⁰ /s", "{#}×{#}¹¹ /s": "{#}×{#}¹¹ /s",
  "{#}×{#}¹² /s": "{#}×{#}¹² /s", "{#}×{#}¹³ /s": "{#}×{#}¹³ /s", "{#}×{#}¹⁴ /s": "{#}×{#}¹⁴ /s",
  "{#}×{#}¹⁵ /s": "{#}×{#}¹⁵ /s", "{#}×{#}¹⁶ /s": "{#}×{#}¹⁶ /s",
  "pops per second (log)": "распадов в секунду (лог.)",
  "pops per second, {#} gram (each line ×{#})": "распадов в секунду, {#} грамм (каждая линия ×{#})",
  "one gram of each, after {#} minutes": "по грамму каждого, через {#} мин",
  "one gram of each, after {#} hours": "по грамму каждого, через {#} ч",
  "one gram of each, after {#} days": "по грамму каждого, через {#} сут",
  "one gram of each, after {#} months": "по грамму каждого, через {#} мес.",
  "one gram of each, after {#} years": "по грамму каждого, через {#} лет",
  "one gram of each, after {#} thousand years": "по грамму каждого, через {#} тыс. лет",
  "one gram of each, after {#} million years": "по грамму каждого, через {#} млн лет",
  "one gram of each, after {#} billion years": "по грамму каждого, через {#} млрд лет",
});
