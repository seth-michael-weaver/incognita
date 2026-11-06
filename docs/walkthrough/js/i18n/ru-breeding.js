/* Russian: breeding (Воспроизводство топлива) */
WT.L.ch.breeding = {
  num: "Урок 1", title: "Воспроизводство топлива", short: "Воспроизводство",
  html: `
<div class="step">
  <h3>Сырьевое становится делящимся</h3>
  <p>Уран-238 почти не делится, но может захватить нейтрон. После двух бета-распадов (каждый раз один нейтрон внутри ядра превращается в протон) он становится плутонием-239, который делится легко. Торий-232 проходит тот же путь и становится ураном-233.</p>
  <div class="btns"><button class="btn ghost" data-act="bcU" aria-pressed="true">Уран-238</button> <button class="btn ghost" data-act="bcT" aria-pressed="false">Торий-232</button></div>
</div>
<div class="step">
  <h3>Нейтронный баланс</h3>
  <p>Каждый нейтрон, поглощённый делящимся топливом, возвращает <i>η</i> новых нейтронов. Один должен вызвать следующее деление, часть теряется; всё, что остаётся, может нарабатывать новое топливо. С ураном-235 и медленными нейтронами на одно сгоревшее делящееся ядро образуется лишь около 0,6 новых.</p>
  <div class="btns"><button class="btn ghost" data-act="bfU5" aria-pressed="true">U-235</button> <button class="btn ghost" data-act="bfP9" aria-pressed="false">Pu-239</button> <button class="btn ghost" data-act="bfU3" aria-pressed="false">U-233</button></div>
  <div class="btns"><button class="btn ghost" data-act="bsT" aria-pressed="true">Медленные нейтроны</button> <button class="btn ghost" data-act="bsF" aria-pressed="false">Быстрые нейтроны</button></div>
</div>
<div class="step">
  <h3>Воспроизводство на быстрых нейтронах</h3>
  <p>Для воспроизводства один нейтрон должен продолжить цепь, а хотя бы один — создать новое топливо, поэтому <i>η</i> должно превышать 2 больше, чем на величину потерь. Плутоний-239 в быстром реакторе даёт около 2,4: с запасом.</p>
  <div class="ctl"><label for="br-l1">Потерянные нейтроны</label><input id="br-l1" type="range" data-bind="L" data-instant min="0.05" max="0.8" step="0.01" value="0.2"><output data-show="L" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Торий на медленных нейтронах</h3>
  <p>На медленных нейтронах плутоний-239 даёт лишь около 2,1, а уран-233 — 2,29. Этот запас позволяет ториевому реактору воспроизводить топливо на медленных нейтронах, если он теряет их очень мало. Уменьшайте потери, пока не начнётся воспроизводство.</p>
  <div class="ctl"><label for="br-l2">Потерянные нейтроны</label><input id="br-l2" type="range" data-bind="L" data-instant min="0.05" max="0.8" step="0.01" value="0.35"><output data-show="L" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Коэффициент воспроизводства</h3>
  <p>Коэффициент воспроизводства — это число образовавшихся делящихся ядер на одно сгоревшее. Ниже 1 топливо постепенно расходуется (конвертер, как современные водяные реакторы); выше 1 реактор заканчивает работу с бо́льшим количеством топлива, чем было в начале (размножитель).</p>
  <div class="btns"><button class="btn ghost" data-act="bfU5" aria-pressed="true">U-235</button> <button class="btn ghost" data-act="bfP9" aria-pressed="false">Pu-239</button> <button class="btn ghost" data-act="bfU3" aria-pressed="false">U-233</button></div>
  <div class="btns"><button class="btn ghost" data-act="bsT" aria-pressed="true">Медленные нейтроны</button> <button class="btn ghost" data-act="bsF" aria-pressed="false">Быстрые нейтроны</button></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "illustration": "иллюстрация",
  "U{#}": "U{#}",
  "Np{#}": "Np{#}",
  "Pu{#}": "Pu{#}",
  "Th{#}": "Th{#}",
  "Pa{#}": "Pa{#}",
  "{#} p": "{#} p",
  "{#} protons": "протонов: {#}",
  "fertile": "сырьевой",
  "fertile: barely splits": "сырьевой: почти не делится",
  "fissile": "делящийся",
  "fissile: splits easily": "делящийся: легко делится",
  "+ n": "+ n",
  "catch": "захват",
  "{#} min": "{#} мин",
  "{#} d": "{#} сут",
  "e⁻": "e⁻",
  "electron": "электрон",
  "antineutrino": "антинейтрино",
  "{a} waiting: day {b}": "{a} ждёт: день {b}",
  "a batch of {a} waiting · day {b}": "партия {a} ждёт распада · день {b}",
  "{a} % now {b}": "{a} % уже {b}",
  "after {#} weeks, {#} % has become Pu{#}": "через {#} недели {#} % превращается в Pu{#}",
  "after {#} months, {#} % has become U{#}": "через {#} месяца {#} % превращается в U{#}",
  "slow step: Np{#}, half-life {#} d": "медленный шаг: Np{#}, T½ = {#} сут",
  "the slow step is Np{#} (half-life {#} days)": "медленный шаг — Np{#} (период полураспада {#} сут)",
  "slow step: Pa{#}, half-life {#} d": "медленный шаг: Pa{#}, T½ = {#} сут",
  "the slow step is Pa{#} (half-life {#} days)": "медленный шаг — Pa{#} (период полураспада {#} сут)",
  "slow neutrons": "медленные нейтроны",
  "fast neutrons": "быстрые нейтроны",
  "next fission": "следующее деление",
  "U{#} → Pu{#}": "U{#} → Pu{#}",
  "Th{#} → U{#}": "Th{#} → U{#}",
  "lost": "потери",
  "next fission: keeps the chain going": "следующее деление: цепь продолжается",
  "breeds: U{#} → Pu{#}": "воспроизводство: U{#} → Pu{#}",
  "breeds: Th{#} → U{#}": "воспроизводство: Th{#} → U{#}",
  "lost: water, steel, poisons, leakage": "потери: вода, сталь, яды, утечка",
  "{a} per absorption": "{a} на поглощение",
  "chain": "цепь",
  "breed": "новое топливо",
  "η ≈ {a}": "η ≈ {a}",
  "η = {a}": "η = {a}",
  "{#}: breeding line": "{#}: порог воспроизводства",
  "neutrons per absorption": "нейтронов на поглощение",
  "neutrons out per neutron absorbed in the fuel": "нейтронов на один нейтрон, поглощённый в топливе",
  "conversion ratio ≈ η − {#} − lost = {a}: breeds": "КВ ≈ η − {#} − потери = {a}: размножитель",
  "conversion ratio ≈ η − {#} − lost = {a}: breeds, makes more fuel than it burns": "коэффициент воспроизводства ≈ η − {#} − потери = {a}: размножитель, топлива нарабатывается больше, чем сгорает",
  "conversion ratio ≈ η − {#} − lost = {a}: converts": "КВ ≈ η − {#} − потери = {a}: конвертер",
  "conversion ratio ≈ η − {#} − lost = {a}: converts, makes less fuel than it burns": "коэффициент воспроизводства ≈ η − {#} − потери = {a}: конвертер, топлива нарабатывается меньше, чем сгорает",
  "U{#} (fertile)": "U{#} (сырьевой)",
  "Th{#} (fertile)": "Th{#} (сырьевой)",
  "split": "разделившиеся",
  "split (fission products)": "разделившиеся (продукты деления)",
  "burned {a}": "сгорело: {a}",
  "made {a}": "наработано: {a}",
  "{a} · slow neutrons": "{a} · медленные нейтроны",
  "{a} · fast neutrons": "{a} · быстрые нейтроны",
  "conversion ratio {a}: a breeder": "коэффициент воспроизводства {a}: размножитель",
  "conversion ratio {a}: a converter": "коэффициент воспроизводства {a}: конвертер",
});
