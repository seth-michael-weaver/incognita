/* Russian: spectrum (Быстрые и тепловые реакторы) */
WT.L.ch.spectrum = {
  num: "Урок 1", title: "Быстрые и тепловые реакторы", short: "Быстрые и тепловые",
  html: `
<div class="step">
  <h3>Насколько быстры нейтроны</h3>
  <p>Нейтроны рождаются быстрыми, около 2 MeV. В водяном реакторе они отскакивают от водорода, пока не станут такими же медленными, как атомы самой воды: <b>тепловыми</b>. В быстром реакторе замедлителя нет, и они остаются быстрыми. Переместите ползунок между этими случаями.</p>
  <div class="ctl"><label for="spc-m1">Замедление</label><input id="spc-m1" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="1"><output data-show="mod" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Лишние нейтроны</h3>
  <p><i>η</i> — сколько нейтронов ядро топлива возвращает на каждый поглощённый нейтрон. Один поддерживает цепную реакцию; чтобы воспроизводить новое топливо, нужен ещё один в запасе, то есть <i>η</i> заметно больше 2. Плутоний-239 достигает этого только на быстрых нейтронах.</p>
  <div class="ctl"><label for="spc-m2">Замедление</label><input id="spc-m2" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="0"><output data-show="mod" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Сжигание остатков</h3>
  <p>Тяжёлые остатки вроде америция медленные нейтроны в основном просто поглощают и становятся тяжелее. Быстрые нейтроны делят гораздо большую их долю, поэтому быстрый реактор может их сжигать.</p>
  <div class="ctl"><label for="spc-m3">Замедление</label><input id="spc-m3" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="0"><output data-show="mod" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Цена</h3>
  <p>Медленный нейтрон гораздо вероятнее вызывает деление: при 1 MeV мишень в сотни раз меньше. Поэтому быстрой активной зоне нужно гораздо более богатое топливо: около 15–25 % плутония вместо 3–5 % урана-235.</p>
  <div class="ctl"><label for="spc-m4">Замедление</label><input id="spc-m4" type="range" data-bind="mod" data-instant min="0" max="1" step="0.01" value="1"><output data-show="mod" data-fmt="2"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "U{#}": "U{#}",
  "Pu{#}": "Pu{#}",
  "Np{#}": "Np{#}",
  "Am{#}": "Am{#}",
  "Cm{#}": "Cm{#}",
  "{#} % split": "{#} % делится",
  "water: neutrons slow down": "вода: нейтроны замедляются",
  "water reactor: hydrogen slows the neutrons": "водяной реактор: водород замедляет нейтроны",
  "sodium: they stay fast": "натрий: они остаются быстрыми",
  "fast reactor: sodium barely slows them": "быстрый реактор: натрий их почти не замедляет",
  "partly moderated": "частичное замедление",
  "sodium": "натрий",
  "no moderator (sodium)": "без замедлителя (натрий)",
  "water": "вода",
  "thermal": "тепловые",
  "resonances": "резонансы",
  "slowing down (resonances)": "замедление (резонансы)",
  "fast": "быстрые",
  "{#} MeV": "{#} MeV",
  "{#} keV": "{#} keV",
  "{#} eV": "{#} eV",
  "neutron energy →": "энергия нейтрона →",
  "born ~{#} MeV": "рождаются при ~{#} MeV",
  "born near {#} MeV": "рождаются около {#} MeV",
  "η = {#}: one to continue, one to breed": "η = {#}: один для цепи, один для воспроизводства",
  "average η: U{#} {#} · Pu{#} {#}": "среднее η: U{#} {#} · Pu{#} {#}",
  "averaged over this spectrum:  η(U{#}) ≈ {#}   η(Pu{#}) ≈ {#}": "среднее по этому спектру:  η(U{#}) ≈ {#}   η(Pu{#}) ≈ {#}",
  "{#} b": "{#} b",
  "≈ {#} b": "≈ {#} b",
  "Pu{#} fission target": "мишень деления Pu{#}",
  "Pu{#} fission cross section (target size)": "сечение деления Pu{#} (размер мишени)",
  "{#} MeV: a target ~{#} times smaller": "{#} MeV: мишень в ~{#} раз меньше",
  "at {#} MeV the target is about {#} times smaller than at {#} eV": "при {#} MeV мишень примерно в {#} раз меньше, чем при {#} eV",
  "most neutrons end up thermal": "большинство нейтронов становятся тепловыми",
  "most neutrons are slowed all the way to thermal": "большинство нейтронов замедляется до тепловых энергий",
  "most stay between {#} keV and {#} MeV": "большинство остаётся между {#} keV и {#} MeV",
  "most neutrons stay between {#} keV and {#} MeV": "большинство нейтронов остаётся между {#} keV и {#} MeV",
  "many linger at in-between energies": "многие задерживаются на промежуточных энергиях",
  "many neutrons linger at in-between energies": "многие нейтроны задерживаются на промежуточных энергиях",
  "thermal ≈ {#} eV, ~{#} km/s": "тепловые ≈ {#} eV, ~{#} км/с",
  "thermal: kT ≈ {#} eV in hot water, about {#} km/s": "тепловые: kT ≈ {#} eV в горячей воде, около {#} км/с",
  "the rest are captured and grow heavier": "остальные захватывают нейтрон и тяжелеют",
  "the rest are captured: the nucleus just grows heavier": "остальные захватывают нейтрон: ядро просто становится тяжелее",
  "illustrative shapes": "условные формы",
});
