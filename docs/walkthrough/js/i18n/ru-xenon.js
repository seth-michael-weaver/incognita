/* Russian: xenon (Отравление ксеноном) */
WT.L.ch.xenon = {
  num: "Урок 1", title: "Отравление ксеноном", short: "Ксенон",
  html: `
<div class="step">
  <h3>Яд, рождённый делением</h3>
  <p>Около 6,6 % делений через йод-135 приводят к ксенону-135 — самому сильному из известных поглотителей нейтронов. Он накапливается около двух суток, пока выгорание под действием нейтронов и распад не начнут убирать его так же быстро, как он образуется. При большей мощности он и выгорает быстрее, поэтому его уровень выходит на насыщение.</p>
  <div class="ctl"><label for="xe-p1">Мощность (%)</label><input id="xe-p1" type="range" data-bind="P" data-instant min="10" max="100" step="5" value="100"><output data-show="P" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Йодная яма</h3>
  <p>После остановки выгорание прекращается, но уже накопленный йод продолжает превращаться в ксенон. Отравление достигает максимума примерно через девять часов и превышает то, что могут вернуть стержни, поэтому реактор нельзя снова запустить; яд уходит за два-три дня.</p>
  <div class="ctl"><label for="xe-th">Часы после остановки</label><input id="xe-th" type="range" data-bind="th" data-instant min="0" max="72" step="0.5" value="9"><output data-show="th" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Остановка и повторный пуск</h3>
  <p>Теперь всё идёт в реальном времени, три часа в секунду. Остановите реактор, затем попробуйте запустить снова: в яме пуск невозможен; позже нейтроны выжигают ксенон. Даже простое изменение мощности раскачивает ксенон на много часов.</p>
  <div class="ctl"><label for="xe-p3">Мощность (%)</label><input id="xe-p3" type="range" data-bind="P" data-instant min="10" max="100" step="5" value="100"><output data-show="P" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="xeshut">Остановить</button><button class="btn ghost" data-act="xerestart">Запустить снова</button></div>
</div>
<div class="step">
  <h3>Ксеноновые колебания</h3>
  <p>В большой активной зоне две её половины связаны слабо. Введите стержни в одну сторону: там меньше поток, меньше ксенона выгорает, и мощность перетекает в другую половину, а затем возвращается — примерно раз в сутки. В более крупных зонах колебания нарастают, если операторы их не гасят.</p>
  <div class="ctl"><label for="xe-wd">Размер зоны (м)</label><input id="xe-wd" type="range" data-bind="wd" data-instant min="1.5" max="3.5" step="0.1" value="3"><output data-show="wd" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="xepush">Ввести стержни слева</button></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "fission → iodine{#} ({#} h) → xenon{#} ({#} h) → Cs{#}": "деление → йод{#} ({#} ч) → ксенон{#} ({#} ч) → Cs{#}",
  "xenon{#} + n → Xe{#}: {#} million barns": "ксенон{#} + n → Xe{#}: {#} млн барн",
  "fission → iodine{#} ({#} h) → xenon{#} ({#} h) → Cs{#}  ·  Xe{#} swallows neutrons: {#} million barns": "деление → йод{#} ({#} ч) → ксенон{#} ({#} ч) → Cs{#}  ·  Xe{#} поглощает нейтроны: {#} млн барн",
  "spare reactivity": "запас реактивности",
  "spare reactivity the rods can give": "запас реактивности, который дают стержни",
  "{#} h": "{#} ч",
  "equilibrium {#} %": "равновесие {#} %",
  "xenon worth (% of k)": "вес ксенона (% от k)",
  "{#} % power · {#} h after start-up · xenon {#} %": "мощность {#} % · {#} ч после пуска · ксенон {#} %",
  "no restart": "пуск невозможен",
  "too poisoned to restart": "слишком отравлен для пуска",
  "shutdown": "остановка",
  "drag": "тяните",
  "peak {#} % at {#} h": "пик {#} % через {#} ч",
  "{#} h after shutdown · xenon {#} % · restart possible": "{#} ч после остановки · ксенон {#} % · пуск возможен",
  "{#} h after shutdown · xenon {#} % · cannot restart": "{#} ч после остановки · ксенон {#} % · пуск невозможен",
  "shut down": "остановлен",
  "refused: more xenon than spare reactivity": "отказ: ксенона больше, чем запас реактивности",
  "restarted": "запущен снова",
  "tap the core to shut down": "коснитесь зоны, чтобы остановить",
  "tap the core to restart": "коснитесь зоны, чтобы запустить",
  "power": "мощность",
  "running at {#} % · xenon {#} %": "работает на {#} % · ксенон {#} %",
  "shut down · in the pit · xenon {#} %": "остановлен · в яме · ксенон {#} %",
  "shut down · restart possible · xenon {#} %": "остановлен · пуск возможен · ксенон {#} %",
  "left {#} %": "слева {#} %",
  "right {#} %": "справа {#} %",
  "tap a side to push rods in": "коснитесь половины, чтобы ввести стержни",
  "more power left": "больше мощности слева",
  "more power right": "больше мощности справа",
  "swing period {#} h · {#} m core: the swing dies away": "период колебаний {#} ч · зона {#} м: колебания затухают",
  "swing period {#} h · {#} m core: the swing dies away slowly": "период колебаний {#} ч · зона {#} м: колебания медленно затухают",
  "swing period {#} h · {#} m core: the swing grows": "период колебаний {#} ч · зона {#} м: колебания нарастают",
  "{#} m core: push the rods to start a swing": "зона {#} м: введите стержни, чтобы вызвать колебания",
  "illustration": "иллюстрация",
});
