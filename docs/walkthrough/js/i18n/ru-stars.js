/* Russian: stars (Откуда берутся элементы) */
WT.L.ch.stars = {
  num: "Урок 1", title: "Откуда берутся элементы", short: "Звёзды",
  html: `
<div class="step">
  <h3>Синтез останавливается на железе</h3>
  <p>Звёзды синтезируют лёгкие ядра вплоть до железа; почти всё более тяжёлое строится добавлением нейтронов.</p>
</div>
<div class="step">
  <h3>Медленный путь</h3>
  <p>В звёздах-гигантах нейтроны приходят редко, поэтому нестабильное ядро сначала испытывает бета-распад: путь зигзагом идёт вдоль стабильных ядер.</p>
  <div class="ctl"><label for="st-k">Захваты нейтронов</label><input id="st-k" type="range" data-bind="k" min="0" max="213" step="1" value="112"></div>
</div>
<div class="step">
  <h3>Быстрый путь</h3>
  <p>При слиянии нейтронных звёзд нейтроны прибывают быстрее, чем ядра успевают распасться; затем перегруженные нейтронами ядра распадаются обратно к стабильности.</p>
  <div class="ctl"><label for="st-rt">Распад обратно</label><input id="st-rt" type="range" data-bind="rt" min="0" max="1" step="0.01" value="0"></div>
</div>
<div class="step">
  <h3>Магические числа дают пики</h3>
  <p>Ядра с 50, 82 или 126 нейтронами почти не захватывают, поэтому вещество там накапливается: s-пики у стронция, бария и свинца, r-пики чуть легче.</p>
  <div class="btns"><button class="btn ghost" data-act="stS" aria-pressed="true">Пики s-процесса</button> <button class="btn ghost" data-act="stR" aria-pressed="true">Пики r-процесса</button></div>
</div>
<div class="step">
  <h3>Мало там, где захват лёгок</h3>
  <p>Для изотопов, создаваемых только s-процессом, произведение распространённости Nₛ на сечение захвата σ почти постоянно между магическими числами. σ здесь — значение, рассчитанное INCOGNITA при 30 кэВ.</p>
  <div class="btns"><button class="btn ghost" data-act="stvs" aria-pressed="false">σ</button> <button class="btn ghost" data-act="stvn" aria-pressed="false">Nₛ</button> <button class="btn ghost" data-act="stvsn" aria-pressed="true">σ × Nₛ</button></div>
</div>
<div class="step">
  <h3>Сверка с измерениями</h3>
  <p>Значения INCOGNITA при 30 кэВ, делённые на измеренные, для 94 стабильных нуклидов (<a href="scoreboard.html">сводная таблица</a>).</p>
</div>`,
};
Object.assign(WT.L.labels, {
  "A ≈ {#}": "A ≈ {#}",
  "Ba": "Ba",
  "Ba{#}": "Ba{#}",
  "Big Bang": "Большой взрыв",
  "Fe": "Fe",
  "H": "H",
  "He": "He",
  "INCOGNITA ÷ measured, {#} keV": "INCOGNITA ÷ измерения, {#} кэВ",
  "INCOGNITA's {#} keV capture rate (MACS) ÷ measured": "скорость захвата INCOGNITA при {#} кэВ (MACS) ÷ измерения",
  "INCOGNITA: capture at {#} keV (MACS)": "INCOGNITA: захват при {#} кэВ (MACS)",
  "Lodders et al. {#}": "Lodders et al. {#}",
  "Lu{#}": "Lu{#}",
  "N = {#}": "N = {#}",
  "O": "O",
  "Pb": "Pb",
  "Pb{#}": "Pb{#}",
  "Sm{#}": "Sm{#}",
  "Sn": "Sn",
  "Sr": "Sr",
  "Sr{#}": "Sr{#}",
  "abundances: Lodders, Palme & Gail {#}": "распространённости: Lodders, Palme & Gail {#}",
  "abundances: Lodders, Palme & Gail {#} · point at the curve": "распространённости: Lodders, Palme & Gail {#} · наведите на кривую",
  "atoms per million silicon atoms (Solar System)": "атомов на миллион атомов кремния (Солнечная система)",
  "atoms per {#}⁶ silicon": "атомов на {#}⁶ Si",
  "beta decay (n → p)": "бета-распад (n → p)",
  "flat between magic numbers, steps down at each": "ровно между магическими числами, ступень вниз у каждого",
  "fusion": "синтез",
  "fusion in stars": "синтез в звёздах",
  "made by neutron capture": "образуются захватом нейтронов",
  "magic N: captures poorly, matter piles up": "магическое N: захват слабый, вещество копится",
  "magic neutron number: it captures poorly, so matter piles up here": "магическое число нейтронов: захват слабый, поэтому вещество копится здесь",
  "mass number A": "массовое число A",
  "mass number A (protons + neutrons)": "массовое число A (протоны + нейтроны)",
  "mb": "мб",
  "nearly flat between magic numbers, a step down at each": "почти ровно между магическими числами, ступень вниз у каждого",
  "neutron capture": "захват нейтрона",
  "neutrons N →": "нейтроны N →",
  "peaks: sources Lodders et al. {#}": "пики: источники Lodders et al. {#}",
  "plus a weaker s-process (massive stars)": "плюс более слабый s-процесс (массивные звёзды)",
  "r {#}": "r {#}",
  "r-path: illustration": "путь r-процесса: иллюстрация",
  "r-peak Pt": "r-пик Pt",
  "r-peak Se, Kr": "r-пик Se, Kr",
  "r-peak Te, Xe": "r-пик Te, Xe",
  "r-process: a flood of neutrons makes very neutron-rich nuclei": "r-процесс: поток нейтронов создаёт сильно нейтроноизбыточные ядра",
  "r-process: very neutron-rich nuclei": "r-процесс: сильно нейтроноизбыточные ядра",
  "ringed: s-only isotopes · measured: compiled values (KADoNiS) · a development comparison, not a blind test": "в кружке: чистые s-изотопы · измерения: сводные значения (KADoNiS) · сравнение при разработке, не слепой тест",
  "ringed: s-only · measured: KADoNiS": "в кружке: только s · измерения: KADoNiS",
  "s Ba": "s Ba",
  "s Pb": "s Pb",
  "s Sr": "s Sr",
  "s-only isotopes · bars: INCOGNITA {#} %": "чистые s-изотопы · полосы: INCOGNITA {#} %",
  "s-only isotopes · σ: INCOGNITA (bars: its {#} % range; open circle: scaled to a measurement) · Nₛ: Lodders et al. {#}": "чистые s-изотопы · σ: INCOGNITA (полосы: её {#} % интервал; пустой кружок: привязка к измерению) · Nₛ: Lodders et al. {#}",
  "s-peak Ba": "s-пик Ba",
  "s-peak Pb": "s-пик Pb",
  "s-peak Sr": "s-пик Sr",
  "seen in {#}: merger GW{#}": "наблюдалось в {#}: слияние GW{#}",
  "seen in {#}: the neutron-star merger GW{#} and its kilonova": "наблюдалось в {#}: слияние нейтронных звёзд GW{#} и его килоновая",
  "wait": "ожид.",
  "waiting point": "точка ожидания",
  "weak s-process too": "и слабый s-процесс",
  "σ × Nₛ (mb × atoms per million Si)": "σ × Nₛ (мб × атомов на миллион Si)",
  "σ × Nₛ (mb × atoms per {#}⁶ Si)": "σ × Nₛ (мб × атомов на {#}⁶ Si)",
  "↑ protons Z": "↑ протоны Z",
  "A = {a}: mostly {b}, {c} atoms per million silicon": "A = {a}: в основном {b}, {c} атомов на миллион кремния",
  "decayed back: r-made stable isotopes": "распались обратно: стабильные r-изотопы",
  "decayed back: each lands on the most neutron-rich stable isobar": "распались обратно: каждое попадает на самый нейтроноизбыточный стабильный изобар",
  "beta decays, A fixed": "бета-распады, A неизменно",
  "beta decays carry them back, mass number A fixed": "бета-распады возвращают их, массовое число A не меняется",
  "{a} · N = {b} · σ = {c} mb": "{a} · N = {b} · σ = {c} мб",
  "{a} · N = {b} · INCOGNITA: σ = {c} mb at {#} keV": "{a} · N = {b} · INCOGNITA: σ = {c} мб при {#} кэВ",
  "{a} · unstable: beta decay": "{a} · нестабилен: бета-распад",
  "{a} · unstable: it beta-decays before the next neutron": "{a} · нестабилен: бета-распадается раньше следующего нейтрона",
  "end: the lead–bismuth cycle": "конец: свинцово-висмутовый цикл",
  "end of the road: Bi{#} → Po{#} → alpha decay back to Pb{#}": "конец пути: Bi{#} → Po{#} → альфа-распад обратно в Pb{#}",
  "drag along the path": "тяните вдоль пути",
  "drag along the path, or use the slider": "тяните вдоль пути или используйте ползунок",
  "{a}: INCOGNITA σ = {b} mb": "{a}: INCOGNITA σ = {b} мб",
  "{a}: σ = {b} mb × Nₛ = {c} → σNₛ = {d}": "{a}: σ = {b} мб × Nₛ = {c} → σNₛ = {d}",
  " (σ scaled to a measured value)": " (σ привязано к измеренному значению)",
  "σ alone: scattered": "одно σ: разброс",
  "σ alone jumps around from isotope to isotope": "одно σ скачет от изотопа к изотопу",
  "Nₛ alone: scattered": "одно Nₛ: разброс",
  "Nₛ alone jumps around the other way": "одно Nₛ скачет в обратную сторону",
  "{a}: INCOGNITA's engine {b} (the library then scales to it)": "{a}: движок INCOGNITA {b} (библиотека затем привязана к измерению)",
  "{a}: INCOGNITA σ = {b} mb, {c}": "{a}: INCOGNITA σ = {b} мб, {c}",
  "{a} nuclides · typical difference {b} %": "нуклидов: {a} · типичное расхождение {b} %",
  "{a} stable nuclides · typical difference {b} % (median), rms {c} %": "стабильных нуклидов: {a} · типичное расхождение {b} % (медиана), ср. кв. {c} %",
  "{a} % above measured": "на {a} % выше измерения",
  "{a} % below measured": "на {a} % ниже измерения",
});
