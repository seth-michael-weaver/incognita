/* Russian: sandbox (Собери реактор) */
WT.L.ch.sandbox = {
  num: "Урок 1", title: "Собери реактор", short: "Собери реактор", lead: "Выберите топливо, замедлитель, теплоноситель и размер и посмотрите, сможет ли цепная реакция поддерживать себя. Упрощённая учебная модель.",
  html: `
<div class="step">
  <h3>Четыре сомножителя</h3>
  <p>Если бы нейтроны не утекали, каждый поглощённый давал бы <i>k</i><sub>∞</sub> = <i>η f p ε</i> новых; эта графитовая кладка из природного урана едва дотягивает.</p>
</div>
<div class="step">
  <h3>Выберите замедлитель</h3>
  <p>С природным ураном только тяжёлая вода или графит позволяют <i>k</i><sub>∞</sub> превысить 1: лёгкая вода хорошо замедляет нейтроны, но слишком много поглощает.</p>
  <div class="btns" role="group" aria-label="Замедлитель"><button class="btn ghost" data-act="mo_h2o">Лёгкая вода</button> <button class="btn ghost" data-act="mo_d2o">Тяжёлая вода</button> <button class="btn ghost" data-act="mo_c">Графит</button></div>
  <div class="ctl"><label for="sb-m1">Замедлителя на топливо</label><input id="sb-m1" type="range" data-bind="lm" min="-0.5" max="2.3" step="0.01" value="0.3"><output class="sb-m"></output></div>
</div>
<div class="step">
  <h3>Обогатите топливо</h3>
  <p>Нескольких процентов урана-235 достаточно, чтобы работала обычная вода, — поэтому её и используют большинство современных реакторов.</p>
  <div class="btns" role="group" aria-label="Топливо"><button class="btn ghost" data-act="fu_nat">Природный U</button> <button class="btn ghost" data-act="fu_leu">Обогащённый U</button> <button class="btn ghost" data-act="fu_mox">МОКС (Pu)</button> <button class="btn ghost" data-act="fu_th">Торий + U-233</button></div>
  <div class="ctl"><label for="sb-e1">Доля делящегося (%)</label><input id="sb-e1" type="range" data-bind="enr" min="0.7" max="30" step="0.1" value="3"><output data-show="enr" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>Размер и утечка</h3>
  <p>Нейтроны уходят через поверхность, поэтому <i>k</i> = <i>k</i><sub>∞</sub> / (1 + <i>M</i>²<i>B</i>²). Растяните край этой графитовой кладки из природного урана до пунктирного кольца.</p>
  <div class="ctl"><label for="sb-r1">Радиус активной зоны (м)</label><input id="sb-r1" type="range" data-bind="R" min="0.2" max="6" step="0.05" value="2"><output data-show="R" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Когда теплоноситель закипает</h3>
  <p>В графитовой зоне с водяным охлаждением кипение повышает <i>k</i>, потому что вода больше поглощала, чем замедляла: изъян РБМК в Чернобыле. Попробуйте другие теплоносители.</p>
  <div class="btns" role="group" aria-label="Теплоноситель"><button class="btn ghost" data-act="co_h2o">Вода</button> <button class="btn ghost" data-act="co_gas">CO₂ / гелий</button> <button class="btn ghost" data-act="co_na">Натрий</button></div>
</div>
<div class="step">
  <h3>Соберите свой</h3>
  <p>Можно всё. У быстрого реактора нет замедлителя, и ему нужно гораздо больше делящегося топлива.</p>
  <div class="btns" role="group" aria-label="Топливо"><button class="btn ghost" data-act="fu_nat">Природный U</button> <button class="btn ghost" data-act="fu_leu">Обогащённый U</button> <button class="btn ghost" data-act="fu_mox">МОКС (Pu)</button> <button class="btn ghost" data-act="fu_th">Торий + U-233</button></div>
  <div class="ctl"><label for="sb-e2">Доля делящегося (%)</label><input id="sb-e2" type="range" data-bind="enr" min="0.7" max="30" step="0.1" value="3"><output data-show="enr" data-fmt="1"></output></div>
  <div class="btns" role="group" aria-label="Замедлитель"><button class="btn ghost" data-act="mo_none">Без замедлителя</button> <button class="btn ghost" data-act="mo_h2o">Лёгкая вода</button> <button class="btn ghost" data-act="mo_d2o">Тяжёлая вода</button> <button class="btn ghost" data-act="mo_c">Графит</button></div>
  <div class="ctl"><label for="sb-m2">Замедлителя на топливо</label><input id="sb-m2" type="range" data-bind="lm" min="-0.5" max="2.3" step="0.01" value="0.3"><output class="sb-m"></output></div>
  <div class="btns" role="group" aria-label="Теплоноситель"><button class="btn ghost" data-act="co_h2o">Вода</button> <button class="btn ghost" data-act="co_d2o">Тяжёлая вода</button> <button class="btn ghost" data-act="co_gas">CO₂ / гелий</button> <button class="btn ghost" data-act="co_na">Натрий</button> <button class="btn ghost" data-act="co_pb">Свинец</button> <button class="btn ghost" data-act="co_salt">Расплав солей</button></div>
  <div class="ctl"><label for="sb-r2">Радиус активной зоны (м)</label><input id="sb-r2" type="range" data-bind="R" min="0.2" max="6" step="0.05" value="2"><output data-show="R" data-fmt="2"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "CO₂ / helium gas coolant": "газовый теплоноситель CO₂ / гелий",
  "MOX {#} % Pu": "МОКС {#} % Pu",
  "MOX, {#} % plutonium{#}": "МОКС, {#} % плутония{#}",
  "R {#} m": "R {#} м",
  "absorbed in fuel": "поглощено в топливе",
  "can never sustain a chain, at any size": "цепная реакция невозможна ни при каком размере",
  "caught by fuel": "захвачено топливом",
  "coolant boils away: k ↑": "теплоноситель выкипает: k ↑",
  "coolant boils: k ↑": "теплоноситель кипит: k ↑",
  "coolant boils: k ≈": "теплоноситель кипит: k ≈",
  "coolant lost: k barely changes": "потеря теплоносителя: k почти не меняется",
  "coolant lost: k ↑": "потеря теплоносителя: k ↑",
  "critical size": "критический размер",
  "escape capture": "избежали захвата",
  "f": "f",
  "fast fission": "деление быстрыми",
  "fission": "деление",
  "fuel": "топливо",
  "fuel heats up: k ↓ (Doppler)": "топливо нагревается: k ↓ (Доплер)",
  "fuel hotter: k ↓": "топливо горячее: k ↓",
  "graphite moderator": "графитовый замедлитель",
  "graphite moderator · CO₂ / helium gas coolant": "графитовый замедлитель · газовый теплоноситель CO₂ / гелий",
  "graphite moderator · water coolant": "графитовый замедлитель · водяной теплоноситель",
  "k": "k",
  "k∞": "k∞",
  "leak": "утечка",
  "leak out": "утекают",
  "light water moderator": "замедлитель — лёгкая вода",
  "light water moderator · water coolant": "замедлитель — лёгкая вода · водяной теплоноситель",
  "mod./cool.": "замедл./теплон.",
  "moderator, coolant": "замедлитель, теплоноситель",
  "natural U": "природный U",
  "natural uranium ({#} % U{#})": "природный уран ({#} % U{#})",
  "never critical": "никогда не критичен",
  "no chain, any size": "цепи нет при любом размере",
  "no leakage": "без утечки",
  "no moderator: a fast reactor · sodium coolant": "без замедлителя: быстрый реактор · натриевый теплоноситель",
  "no moderator: fast": "без замедлителя: быстрый",
  "no size is big enough": "никакого размера не хватит",
  "p": "p",
  "per fuel absorption": "на поглощение в топливе",
  "radius {#} m": "радиус {#} м",
  "radius {#} m · drag the edge": "радиус {#} м · тяните за край",
  "simplified model": "упрощённая модель",
  "simplified one-group model · illustration": "упрощённая одногрупповая модель · иллюстрация",
  "stays in": "остаются",
  "stays in (M² {#} cm²)": "остаются (M² {#} см²)",
  "sustains a chain, {#} % to spare (ρ)": "цепь поддерживается, запас {#} % (ρ)",
  "sustains: +{#} % spare": "поддерживается: запас +{#} %",
  "too small: critical at radius {#} m": "слишком мал: критичен при радиусе {#} м",
  "too small: needs {#} m": "слишком мал: нужно {#} м",
  "uranium, {#} % U{#}": "уран, {#} % U{#}",
  "water boils: k ↑": "вода кипит: k ↑",
  "water boils: k ↓": "вода кипит: k ↓",
  "water coolant": "водяной теплоноситель",
  "water heats or boils: k ↑": "вода греется или кипит: k ↑",
  "water heats or boils: k ↓": "вода греется или кипит: k ↓",
  "where the neutrons go": "куда уходят нейтроны",
  "{#} % U{#}": "{#} % U{#}",
  "enriched U": "обогащённый U",
  "light water": "лёгкая вода",
  "heavy water": "тяжёлая вода",
  "lead": "свинец",
  "molten salt": "расплав солей",
  "sodium": "натрий",
  "coolant": "теплоноситель",
  "= η f, if nothing leaked": "= η f, если бы ничего не утекало",
  "= η f p ε, if nothing leaked": "= η f p ε, если бы ничего не утекало",
  "stays in: {#} / ({#} + M²B²), M² = {#} cm²": "остаются: {#} / ({#} + M²B²), M² = {#} см²",
  "neutrons per absorption in fuel": "нейтронов на поглощение в топливе",
  "share absorbed in fuel": "доля поглощённых в топливе",
  "no slowing down, no resonance loss": "нет замедления — нет резонансных потерь",
  "escape capture while slowing": "избежать захвата при замедлении",
  "fast fission counted in η": "деление быстрыми учтено в η",
  "bonus from fast fission": "прибавка от деления быстрыми",
  "thorium, {#} % U{#}": "торий, {#} % U{#}",
  "Th + {#} % U{#}": "Th + {#} % U{#}",
  "uranium, {#} % U{#} (highly enriched)": "уран, {#} % U{#} (высокообогащённый)",
  "critical at {#} m": "критичен при {#} м",
  "coolant heats: k ↑": "теплоноситель греется: k ↑",
  "coolant heats: k ↓": "теплоноситель греется: k ↓",
  "coolant boils away: k ↓": "теплоноситель выкипает: k ↓",
  "coolant lost: k ↓": "потеря теплоносителя: k ↓",
  "heavy water coolant": "теплоноситель — тяжёлая вода",
  "sodium coolant": "натриевый теплоноситель",
  "lead coolant": "свинцовый теплоноситель",
  "molten salt coolant": "теплоноситель — расплав солей",
  "heavy water moderator": "замедлитель — тяжёлая вода",
  "heavy water moderator · heavy water coolant": "замедлитель — тяжёлая вода · теплоноситель — тяжёлая вода",
  "heavy water moderator · water coolant": "замедлитель — тяжёлая вода · водяной теплоноситель",
  "graphite moderator · sodium coolant": "графитовый замедлитель · натриевый теплоноситель",
  "no moderator: a fast reactor · lead coolant": "без замедлителя: быстрый реактор · свинцовый теплоноситель",
  "no moderator: a fast reactor · CO₂ / helium gas coolant": "без замедлителя: быстрый реактор · газовый теплоноситель CO₂ / гелий",
  "no moderator: a fast reactor · molten salt coolant": "без замедлителя: быстрый реактор · теплоноситель — расплав солей",
  "water moderates": "замедляет вода",
  "heavy water moderates": "замедляет тяжёлая вода",
  "no moderator, but the water moderates": "без замедлителя, но замедляет вода",
  "no moderator, but the heavy water moderates": "без замедлителя, но замедляет тяжёлая вода",
});
