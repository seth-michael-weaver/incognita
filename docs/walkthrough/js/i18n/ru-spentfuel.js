/* Russian: spentfuel (Отработавшее топливо, нуклид за нуклидом) */
WT.L.ch.spentfuel = {
  num: "Урок 1", title: "Отработавшее топливо, нуклид за нуклидом", short: "Нуклид за нуклидом",
  html: `
<div class="step">
  <h3>Что внутри</h3>
  <p>Тонна топлива PWR через год после выгрузки (обогащение 4,2 %, 50 ГВт·сут/т): почти вся масса — уран, почти вся активность сосредоточена в нескольких килограммах.</p>
</div>
<div class="step">
  <h3>Активность или радиотоксичность</h3>
  <p>Беккерели считают распады; зиверты взвешивают каждый распад по вреду при проглатывании, что поднимает альфа-излучатели.</p>
  <div class="btns"><button class="btn ghost" data-act="mA" aria-pressed="false">Активность (Бк)</button> <button class="btn ghost" data-act="mT" aria-pressed="true">Радиотоксичность (Зв)</button></div>
</div>
<div class="step">
  <h3>Кто и когда доминирует</h3>
  <p>Наведите или коснитесь полосы, чтобы узнать её название; тяните вдоль оси времени, чтобы упорядочить их.</p>
</div>
<div class="step">
  <h3>Рецикл плутония</h3>
  <p>Переработка через четыре года извлекает плутоний (а с ним и уран). Сколько остаётся?</p>
  <div class="btns"><span class="sf-k" style="font:600 13px var(--sans);color:var(--soft);margin-right:4px;align-self:center">Pu removed</span> <button class="btn ghost" data-act="pu0" aria-pressed="true">0 %</button> <button class="btn ghost" data-act="pu99" aria-pressed="false">99 %</button> <button class="btn ghost" data-act="pu999" aria-pressed="false">99,9 %</button></div>
</div>
<div class="step">
  <h3>Извлеките и младшие актиниды</h3>
  <p>Извлеките также америций, кюрий и нептуний: тогда время определяет оставшийся 1 % или 0,1 %.</p>
  <div class="btns"><span class="sf-k" style="font:600 13px var(--sans);color:var(--soft);margin-right:4px;align-self:center">Pu removed</span> <button class="btn ghost" data-act="pu0" aria-pressed="true">0 %</button> <button class="btn ghost" data-act="pu99" aria-pressed="false">99 %</button> <button class="btn ghost" data-act="pu999" aria-pressed="false">99,9 %</button></div>
  <div class="btns"><span class="sf-k" style="font:600 13px var(--sans);color:var(--soft);margin-right:4px;align-self:center">Am, Cm, Np removed</span> <button class="btn ghost" data-act="ma0" aria-pressed="true">0 %</button> <button class="btn ghost" data-act="ma99" aria-pressed="false">99 %</button> <button class="btn ghost" data-act="ma999" aria-pressed="false">99,9 %</button></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "Am{#}": "Am{#}",
  "Am{#} {#} %": "Am{#} {#} %",
  "Cm{#}": "Cm{#}",
  "Cs{#}": "Cs{#}",
  "I{#}": "I{#}",
  "NEA {#} + computed": "NEA {#} + расчёт",
  "Np{#}": "Np{#}",
  "Pu{#}": "Pu{#}",
  "Pu{#} {#} %": "Pu{#} {#} %",
  "Sr{#}": "Sr{#}",
  "Sr{#} + Y{#}": "Sr{#} + Y{#}",
  "Tc{#}": "Tc{#}",
  "activity": "активность",
  "activity after {#} year (log scale)": "активность через {#} год (лог. шкала)",
  "below the ore after ≈ {#} years": "ниже руды через ≈ {#} лет",
  "computed (Bateman decay, ICRP{#}) · band height = share of the total": "расчёт (распад по Бейтману, ICRP{#}) · высота полосы = доля в сумме",
  "computed · band height = share": "расчёт · высота полосы = доля",
  "drag along the time axis · hover a band": "тяните вдоль оси времени · наведите на полосу",
  "inventory: OECD-NEA {#} ({#} %, {#} GWd/t) + computed fission products": "состав: OECD-NEA {#} ({#} %, {#} ГВт·сут/т) + расчётные продукты деления",
  "mass": "масса",
  "mass (log scale)": "масса (лог. шкала)",
  "most of the {#} kg of fission products is stable; activity includes short-lived daughters": "бо́льшая часть из {#} кг продуктов деления стабильна; активность включает короткоживущие дочерние",
  "once-through": "открытый цикл",
  "once-through (no recycling)": "открытый цикл (без рецикла)",
  "ore: {#}×{#}⁵ Sv": "руда: {#}×{#}⁵ Зв",
  "other FP": "прочие ПД",
  "other FP: mostly stable": "прочие ПД: в основном стабильны",
  "other fission products": "прочие продукты деления",
  "radiotoxicity if swallowed (Sv), relative to the ore": "радиотоксичность при проглатывании (Зв) относительно руды",
  "radiotoxicity ÷ ore": "радиотоксичность ÷ руда",
  "reprocessing at {#} yr": "переработка через {#} г.",
  "the ore it came from: {#} t natural uranium + daughters = {#}×{#}⁵ Sv": "исходная руда: {#} т природного урана + дочерние = {#}×{#}⁵ Зв",
  "then mostly Am{#} ({#} %)": "тогда в основном Am{#} ({#} %)",
  "then mostly Pb{#} + Po{#} ({#} %)": "тогда в основном Pb{#} + Po{#} ({#} %)",
  "then mostly Sr{#} + Y{#} ({#} %)": "тогда в основном Sr{#} + Y{#} ({#} %)",
  "uranium": "уран",
  "years after unloading (log scale) →": "лет после выгрузки (лог. шкала) →",
  "{#} g": "{#} г",
  "{#} kg": "{#} кг",
  "{#} million": "{#} млн",
  "{#} years:": "{#} лет:",
  "{#} yr": "{#} г.",
  "{#}¹³ Bq": "{#}¹³ Бк",
  "{#}¹⁰ Bq": "{#}¹⁰ Бк",
  "{#}¹⁶ Bq": "{#}¹⁶ Бк",
  "other Am, Cm": "прочие Am, Cm",
  "decay daughters (Ra, Pb, Po, Th…)": "дочерние продукты (Ra, Pb, Po, Th…)",
  "daughters": "дочерние",
  "still above the ore after a million years": "всё ещё выше руды через миллион лет",
  "drag the time · tap a band": "тяните время · коснитесь полосы",
  "activity ÷ ore": "активность ÷ руда",
  "activity (Bq), relative to the ore": "активность (Бк) относительно руды",
});
