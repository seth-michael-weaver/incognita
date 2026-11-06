/* Russian: feedback (Устойчивость реактора и обратные связи) */
WT.L.ch.feedback = {
  num: "Урок 1", title: "Устойчивость реактора и обратные связи", short: "Обратные связи",
  html: `
<div class="step">
  <h3>Петля: мощность, тепло, реактивность</h3>
  <p>Рост мощности нагревает топливо и воду, а их температуры меняют реактивность <i>ρ</i>, которая и задаёт мощность. Добавьте скачок реактивности и смотрите, как сигнал обходит петлю. При отрицательных коэффициентах петля противодействует.</p>
  <div class="ctl"><label for="fb-r">Скачок реактивности (pcm)</label><input id="fb-r" type="range" data-bind="rs" data-instant min="50" max="300" step="10" value="200"><output data-show="rs" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">Ввести</button> <button class="btn ghost" data-act="fbRes">Сброс</button></div>
</div>
<div class="step">
  <h3>Доплер: быстрый тормоз</h3>
  <p>Более горячее топливо сильнее захватывает нейтроны в уране-238 без деления (<a href="#doppler">доплеровское уширение</a>). Топливо нагревается за секунды, поэтому этот тормоз срабатывает первым, а в водяных реакторах он всегда отрицателен. Здесь это единственная обратная связь.</p>
  <div class="ctl"><label for="fb-d">Доплеровский коэффициент (pcm/K)</label><input id="fb-d" type="range" data-bind="aD" data-instant min="-5" max="-1" step="0.1" value="-2.5"><output data-show="aD" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">Ввести</button> <button class="btn ghost" data-act="fbRes">Сброс</button></div>
</div>
<div class="step">
  <h3>Подключается замедлитель</h3>
  <p>Тёплая вода менее плотная, поэтому хуже замедляет нейтроны. В реакторе с водой под давлением при обычной концентрации бора из-за этого и коэффициент замедлителя становится отрицательным: второй, более медленный тормоз, и мощность устанавливается ниже.</p>
  <div class="ctl"><label for="fb-m">Коэффициент замедлителя (pcm/K)</label><input id="fb-m" type="range" data-bind="aM" data-instant min="-60" max="0" step="1" value="-30"><output data-show="aM" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">Ввести</button> <button class="btn ghost" data-act="fbRes">Сброс</button></div>
</div>
<div class="step">
  <h3>Когда обратная связь положительна</h3>
  <p>Если вклад теплоносителя положителен и перевешивает Доплер, рост мощности добавляет реактивность, и мощность идёт вразнос. Водяные реакторы проектируют с отрицательными коэффициентами; у некоторых конструкций, например у РБМК на малой мощности, паровой коэффициент реактивности мог быть положительным.</p>
  <div class="ctl"><label for="fb-c">Коэффициент теплоносителя (pcm/K)</label><input id="fb-c" type="range" data-bind="aM" data-instant min="-60" max="150" step="5" value="150"><output data-show="aM" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">Ввести</button> <button class="btn ghost" data-act="fbRes">Сброс</button></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "heat": "тепло",
  "heats water": "греет воду",
  "chain": "цепь",
  "chain reaction": "цепная реакция",
  "αM +": "αM +",
  "αM −": "αM −",
  "αM {#}": "αM {#}",
  "αC +": "αC +",
  "αC −": "αC −",
  "αC {#}": "αC {#}",
  "αD −": "αD −",
  "P {#} %": "P {#} %",
  "fuel +{#} K": "топливо +{#} K",
  "fuel {#} K": "топливо {#} K",
  "fuel ΔT +{#} K": "топливо ΔT +{#} K",
  "fuel ΔT {#} K": "топливо ΔT {#} K",
  "water +{#} K": "вода +{#} K",
  "water {#} K": "вода {#} K",
  "water ΔT +{#} K": "вода ΔT +{#} K",
  "water ΔT {#} K": "вода ΔT {#} K",
  "ρ +{#} pcm": "ρ +{#} pcm",
  "ρ {#} pcm": "ρ {#} pcm",
  "ρ = ρext + αD ΔTf + αM ΔTm": "ρ = ρext + αD ΔTf + αM ΔTm",
  "C dT/dt = P − h (T − Tc)": "C dT/dt = P − h (T − Tc)",
  "Doppler α_D = {a} pcm/K": "Доплер α_D = {a} pcm/K",
  "coolant α_C = {a} pcm/K": "теплоноситель α_C = {a} pcm/K",
  "moderator α_M = {a} pcm/K": "замедлитель α_M = {a} pcm/K",
  "inserted ρ_ext = {a}": "введено ρ_ext = {a}",
  "+{a} pcm": "+{a} pcm",
  "power": "мощность",
  "last {#} s →": "последние {#} с →",
  "last {#} seconds →": "последние {#} секунд →",
  "power ran away · protection would shut it down": "разгон мощности · защита заглушила бы реактор",
  "power ran away · in a real plant the protection system would shut it down": "разгон мощности · на настоящей станции аварийная защита заглушила бы реактор",
  "steady at {#} % · press Insert": "стабильно на {#} % · нажмите «Ввести»",
  "steady at {#} % power · press Insert to add reactivity": "стабильно на {#} % мощности · нажмите «Ввести», чтобы добавить реактивность",
  "power coefficient {a} pcm per {#} %: settles": "мощностной коэффициент {a} pcm на {#} %: стабилизируется",
  "power coefficient {a} pcm per {#} % power: self-stabilising": "мощностной коэффициент {a} pcm на {#} % мощности: самостабилизация",
  "power coefficient +{a} pcm per {#} %: runs away": "мощностной коэффициент +{a} pcm на {#} %: разгон",
  "power coefficient +{a} pcm per {#} % power: runs away": "мощностной коэффициент +{a} pcm на {#} % мощности: разгон",
  "illustrative model": "иллюстративная модель",
});
