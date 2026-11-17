/* Russian: kcalc (Computing criticality) */
WT.L.ch.kcalc = {
  num: "Урок 1", title: "Расчёт критичности", short: "Расчёт k",
  html: `
<div class="step">
  <h3>Бенчмарки</h3>
  <p>Четыре быстрые металлические критические сборки из ICSBEP, в масштабе. Godiva и Jezebel — голые шары; у Flattop-25 и Flattop-Pu отражатель из природного урана.</p>
</div>
<div class="step">
  <h3>Расчётный <i>k</i><sub>eff</sub></h3>
  <p>OpenMC, непрерывная энергия, 3-D-геометрия. Все четыре в пределах ±1σ бенчмарка. <i>k</i><sub>eff</sub> не используется при подгонке.</p>
</div>
<div class="step">
  <h3>Профили чувствительности</h3>
  <p>Сопряжённая чувствительность <i>k</i><sub>eff</sub> к каждой реакции на единицу летаргии.</p>
  <div class="btns"><button class="btn ghost" data-act="se0" aria-pressed="true">Godiva</button><button class="btn ghost" data-act="se1" aria-pressed="false">Jezebel</button><button class="btn ghost" data-act="se2" aria-pressed="false">Flattop-Pu</button></div>
</div>
<div class="step">
  <h3>Проверка прямым возмущением</h3>
  <p>Предсказанные и пересчитанные изменения <i>k</i><sub>eff</sub>, 63 возмущённых набора данных.</p>
</div>
<div class="step">
  <h3>Активная зона C5G7</h3>
  <p>OECD/NEA C5G7, 2-D четверть зоны, 1056 твэлов UO<sub>2</sub> и MOX. <i>k</i><sub>eff</sub> −19&nbsp;pcm от эталона; максимальная ошибка мощности твэла 0,13&nbsp;%.</p>
</div>`,
};

Object.assign(WT.L.labels, {
  "{#} pcm  (±{#} benchmark)": "{#} pcm  (бенчмарк ±{#})",
  "+{#} pcm  (±{#} benchmark)": "+{#} pcm  (бенчмарк ±{#})",
  "Calculated − experimental k, with the benchmark ±{#}σ band": "Расчётный − экспериментальный k, с полосой ±{#}σ бенчмарка",
  "Drag to rotate": "Перетащите, чтобы повернуть",
  "Godiva, integral sensitivity: ν {#}, fission {#} (% k per % change)": "Godiva, интегральная чувствительность: ν {#}, деление {#} (% k на % изменения)",
  "Jezebel, integral sensitivity: ν {#}, fission {#} (% k per % change)": "Jezebel, интегральная чувствительность: ν {#}, деление {#} (% k на % изменения)",
  "Flattop-Pu, integral sensitivity: ν {#}, fission {#} (% k per % change)": "Flattop-Pu, интегральная чувствительность: ν {#}, деление {#} (% k на % изменения)",
  "Godiva: ν {#}, fission {#}": "Godiva: ν {#}, деление {#}",
  "Jezebel: ν {#}, fission {#}": "Jezebel: ν {#}, деление {#}",
  "Flattop-Pu: ν {#}, fission {#}": "Flattop-Pu: ν {#}, деление {#}",
  "UO₂: {#} × mean": "UO₂: {#} × среднего",
  "MOX {#} %: {#} × mean": "MOX {#} %: {#} × среднего",
  "OpenMC re-solve, Δk (pcm)": "Пересчёт OpenMC, Δk (pcm)",
  "Predicted from sensitivities, Δk (pcm)": "Предсказано по чувствительностям, Δk (pcm)",
  "predicted Δk, pcm": "предсказанное Δk, pcm",
  "U{#} capture": "U{#}: захват",
  "Pu{#} capture": "Pu{#}: захват",
  "U{#} elastic": "U{#}: упругое",
  "Pu{#} elastic": "Pu{#}: упругое",
  "U{#} fission": "U{#}: деление",
  "Pu{#} fission": "Pu{#}: деление",
  "U{#} inelastic": "U{#}: неупругое",
  "Pu{#} inelastic": "Pu{#}: неупругое",
  "U{#} neutrons per fission (ν)": "U{#}: нейтроны на деление (ν)",
  "Pu{#} neutrons per fission (ν)": "Pu{#}: нейтроны на деление (ν)",
  "Relative pin power (hover a pin)": "Относительная мощность твэла (наведите на твэл)",
  "Relative pin power (tap a pin)": "Относительная мощность твэла (коснитесь твэла)",
  "To scale.": "В масштабе.",
  "To scale. Drag to rotate.": "В масштабе. Перетащите, чтобы повернуть.",
  "core {#} cm, reflector {#} cm": "ядро {#} см, отражатель {#} см",
  "radius {#} cm": "радиус {#} см",
  "{#} cm in {#} cm": "{#} см в {#} см",
  "k = {#}; reference {#} ({#} pcm)": "k = {#}; эталон {#} ({#} pcm)",
  "k {#}, reference {#}": "k {#}, эталон {#}",
  "plutonium in natural uranium": "плутоний в природном уране",
  "plutonium metal": "металлический плутоний",
  "uranium{#} in natural uranium": "уран{#} в природном уране",
  "uranium{#} metal": "металлический уран{#}",
  "water": "вода",
  "×{#} of mean": "×{#} от среднего",
  "U{#} ν": "U{#} ν",
  "Pu{#} ν": "Pu{#} ν",
  "Godiva   k = {#}": "Godiva   k = {#}",
  "Godiva {#}": "Godiva {#}",
  "Godiva: rms {#} pcm": "Godiva: rms {#} pcm",
  "Jezebel   k = {#}": "Jezebel   k = {#}",
  "Jezebel {#}": "Jezebel {#}",
  "Jezebel: rms {#} pcm": "Jezebel: rms {#} pcm",
  "Flattop-Pu   k = {#}": "Flattop-Pu   k = {#}",
  "Flattop-Pu {#}": "Flattop-Pu {#}",
  "Flattop-Pu: rms {#} pcm": "Flattop-Pu: rms {#} pcm",
  "Flattop{#}   k = {#}": "Flattop{#}   k = {#}",
  "Flattop{#} {#}": "Flattop{#} {#}",
  "{#} pcm (±{#})": "{#} pcm (±{#})",
  "+{#} pcm (±{#})": "+{#} pcm (±{#})",
  "{#} cm": "{#} cm",
  "{#} keV": "{#} keV",
  "{#} MeV": "{#} MeV",
  "OpenMC Δk": "OpenMC Δk"
});
