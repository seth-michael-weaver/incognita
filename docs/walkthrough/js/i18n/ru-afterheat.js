/* Russian: afterheat (Тепло после остановки) */
WT.L.ch.afterheat = {
  num: "Урок 1", title: "Тепло после остановки", short: "Остаточное тепло",
  html: `
<div class="step">
  <h3>Цепная реакция останавливается</h3>
  <p>Опущенные регулирующие стержни прекращают деление атомов примерно за минуту. Но топливо продолжает светиться: осколки от прежних делений радиоактивны, и их распады по-прежнему выделяют тепло.</p>
  <div class="btns"><button class="btn" data-act="ahDrop">Опустить стержни</button> <button class="btn ghost" data-act="ahUp">Перезапуск</button></div>
</div>
<div class="step">
  <h3>Затухает, но медленно</h3>
  <p>Сразу после остановки это тепло составляет около 6–7 % полной мощности. Через час — около 1 %, через сутки — около половины процента, через неделю — четверть процента. Доли небольшие, но от очень большого числа.</p>
  <div class="ctl"><label for="ah-t">Время после остановки</label><input id="ah-t" type="range" data-bind="lt" data-instant min="0" max="7.5" step="0.01" value="3.56"></div>
</div>
<div class="step">
  <h3>Вода должна двигаться</h3>
  <p>Поэтому активную зону охлаждают и после остановки. Насосы прокачивают воду мимо топлива и уносят тепло. Выключите их — и температура поползёт вверх: теплу некуда деваться.</p>
  <div class="btns"><button class="btn ghost" data-act="ahPump" aria-pressed="true">Насосы</button></div>
</div>
<div class="step">
  <h3>Охлаждение без насосов</h3>
  <p>Горячая вода поднимается, холодная опускается. Контур, ведущий к бассейну над активной зоной, поддерживает движение воды вовсе без насосов. Ряд новых проектов полагается на это в течение нескольких суток.</p>
  <div class="btns"><button class="btn ghost" data-act="ahPump" aria-pressed="false">Насосы</button> <button class="btn ghost" data-act="ahPass" aria-pressed="true">Пассивный контур</button></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "{a} s": "{a} с",
  "{a} min": "{a} мин",
  "{a} hours": "{a} ч",
  "{a} days": "{a} сут",
  "{a} months": "{a} мес.",
  "illustration": "иллюстрация",
  "splitting atoms": "деление атомов",
  "heat from splitting atoms": "тепло от деления атомов",
  "decaying fragments": "распад осколков",
  "heat from decaying fragments": "тепло от распада осколков",
  "full power": "полная мощность",
  "running at full power": "работа на полной мощности",
  "{a} after the rods dropped": "{a} после опускания стержней",
  "total heat: {a} % of full power": "всего тепла: {a} % полной мощности",
  "the splitting dies away in about a minute": "деление затухает примерно за минуту",
  "the splitting dies away within about a minute": "деление затухает примерно за минуту",
  "the decay heat stays and fades slowly": "остаточное тепло остаётся и спадает медленно",
  "the decay heat stays, and fades only slowly": "остаточное тепло остаётся и спадает лишь медленно",
  "{#} min": "{#} мин",
  "{#} hour": "{#} ч",
  "{#} day": "{#} сут",
  "{#} week": "{#} нед.",
  "{#} year": "{#} год",
  "heat, share of full power": "тепло, доля полной мощности",
  "heat, as a share of full power": "тепло как доля полной мощности",
  "{a} after shutdown: {b} % of full power": "{a} после остановки: {b} % полной мощности",
  "{#} MW core: {a} MW, like {b} kettles": "зона {#} МВт: {a} МВт, как {b} чайников",
  "for a {#} MW core: {a} MW, as much as {b} electric kettles": "для зоны {#} МВт: {a} МВт, как у {b} электрочайников",
  "pool, up high": "бассейн наверху",
  "water pool, placed higher": "бассейн с водой выше зоны",
  "cooler": "охладитель",
  "heat exchanger": "теплообменник",
  "pump on": "насос вкл.",
  "pump running": "насос работает",
  "pump off": "насос выкл.",
  "pump stopped": "насос остановлен",
  "boiling": "кипение",
  "the water starts to boil": "вода закипает",
  "normal": "норма",
  "too hot": "перегрев",
  "temperature": "температура",
  "core temperature": "температура зоны",
  "{a} after shutdown · heat {b} % of full power": "{a} после остановки · тепло {b} % полной мощности",
  "too hot: cooling must be restored": "перегрев: нужно восстановить охлаждение",
  "too hot: the water would start to boil away; cooling must be restored": "перегрев: вода начнёт выкипать; нужно восстановить охлаждение",
  "temperature climbing": "температура растёт",
  "temperature climbing: the heat has nowhere to go": "температура растёт: теплу некуда деваться",
  "pumps carry the heat away": "насосы отводят тепло",
  "steady: the pumps carry the heat away": "стабильно: насосы отводят тепло",
  "steady, with no pumps": "стабильно, без насосов",
  "steady: natural circulation carries the heat away": "стабильно: тепло отводит естественная циркуляция",
  "steady": "стабильно",
});
