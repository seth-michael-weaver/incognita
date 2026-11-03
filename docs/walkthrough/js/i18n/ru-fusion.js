/* Russian: fusion (Глава 29, энергия синтеза и кулоновский барьер) */
WT.L.ch.fusion = {
  num: "Глава 29", title: "Энергия синтеза и кулоновский барьер", short: "Синтез",
  lead: "Синтез идёт в обратную сторону по сравнению с делением: два лёгких ядра соединяются, и пара весит меньше своих частей.",
  html: `
<div class="step">
  <h3>Энергия синтеза по кривой энергии связи</h3>
  <p>Соедините два лёгких ядра: если новое ядро лежит на кривой энергии связи выше, энергия выделяется. За железным максимумом слияние требует затрат энергии.</p>
  <div class="ctl"><label for="fu-a">A каждого лёгкого ядра</label><input id="fu-a" type="range" data-bind="fuse" data-instant min="2" max="60" step="1" value="2"><output data-show="fuse" data-fmt="0"></output></div>
  <p class="ctl-result" id="fu-fuse-out" aria-live="polite"></p>
</div>
<div class="step">
  <h3>Кулоновский барьер и туннельный эффект</h3>
  <p>Оттяните дейтрон назад и отпустите. Оба ядра заряжены, поэтому большинство выстрелов отскакивает от холма; лишь немногие проходят сквозь него туннелированием.</p>
  <div class="ctl"><label for="fu-e">Толчок (keV)</label><input id="fu-e" type="range" data-bind="lE" min="0.5" max="2.6" step="0.01" value="1.7"><output data-show="E" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fire">Выстрел</button></div>
</div>
<div class="step">
  <h3>Продукты реакции и энергия Q</h3>
  <p>Соединённая пара легче двух частей. Недостающая масса улетает в виде быстрых частиц.</p>
  <div class="btns fu-fuels"><button class="btn ghost" data-act="DT" aria-pressed="true">D–T</button> <button class="btn ghost" data-act="DD" aria-pressed="false">D–D</button> <button class="btn ghost" data-act="DHe" aria-pressed="false">D–³He</button> <button class="btn ghost" data-act="pB" aria-pressed="false">p–¹¹B</button></div>
</div>
<div class="step">
  <h3>Скорость термоядерной реакции</h3>
  <p>В горячем газе проходят самые быстрые ядра. Каждая вспышка — один акт синтеза.</p>
  <div class="ctl"><label for="fu-t">Температура (keV)</label><input id="fu-t" type="range" data-bind="lT" min="0" max="2" step="0.01" value="1"><output data-show="T" data-fmt="1"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "B": "B",
  "Copper{#}": "Медь{#}",
  "Coulomb hill": "кулоновский холм",
  "D–D": "D–D",
  "D–T": "D–T",
  "D–³He": "D–³He",
  "E = kT": "E = kT",
  "Gamow peak E₀": "пик Гамова E₀",
  "K {#} · field lines lost to the wall: {#}": "K {#} · линий ушло на стенку: {#}",
  "Q = {#}": "Q = {#}",
  "Q = ∞: no heating needed": "Q = ∞: нагрев не нужен",
  "Silicon{#} (SiC)": "Кремний{#} (SiC)",
  "Steel (iron{#})": "Сталь (железо{#})",
  "Sun's core": "центр Солнца",
  "TBR {#}": "TBR {#}",
  "Tungsten{#}": "Вольфрам{#}",
  "Vanadium{#}": "Ванадий{#}",
  "after {#} years at {#} MW/m² · {#} MeV neutrons only · σ from INCOGNITA library v{#}": "за {#} г. при {#} MW/m² · только нейтроны {#} MeV · σ из библиотеки INCOGNITA v{#}",
  "almost never": "почти никогда",
  "alpha {#} MeV": "альфа {#} MeV",
  "axis, q = {#}": "ось, q = {#}",
  "binding per nucleon (MeV)": "связь на нуклон (MeV)",
  "bubble-chamber view, magnetic field into the page: charged products curl, the neutron leaves no track": "пузырьковая камера, поле направлено в страницу: заряженные продукты закручиваются, нейтрон следа не оставляет",
  "burning on its own": "горит сама",
  "cooled down: plasma lost": "остыла: плазма потеряна",
  "cooling": "остывает",
  "could not load the library file": "не удалось загрузить файл библиотеки",
  "deuteron": "дейтрон",
  "deuteron {#} keV": "дейтрон {#} keV",
  "deuteron: pull back, let go": "дейтрон: оттяните и отпустите",
  "drag or tap a point; it runs on its own": "перетащите или коснитесь точки; дальше само",
  "easiest: {a} keV, nτT {b}": "легче всего: {a} keV, nτT {b}",
  "edge: q = {#} · lines that cross it are lost": "край: q = {#} · пересёкшие его линии теряются",
  "electron {#} keV": "электрон {#} keV",
  "energy of the colliding pair (keV)": "энергия сталкивающейся пары (keV)",
  "few are this fast": "таких быстрых мало",
  "fusion rate: {a} the rate at {b} keV": "скорость синтеза: {a} от скорости при {b} keV",
  "grain boundary": "граница зерна",
  "heating itself": "греет сама себя",
  "helium stays and gathers into bubbles; hydrogen mostly diffuses out": "гелий остаётся и собирается в пузырьки; водород в основном уходит диффузией",
  "helium {#} appm": "гелий {#} appm",
  "hill to climb: charge product Z₁Z₂ = {#}": "высота холма: произведение зарядов Z₁Z₂ = {#}",
  "hold: heaters on (Q = fusion power / heating) · let go: heaters off, the plasma is on its own": "держите: нагрев включён (Q = мощность синтеза / нагрев) · отпустите: нагрев выключен, плазма сама по себе",
  "hydrogen {#} appm": "водород {#} appm",
  "ignition (Q = ∞)": "зажигание (Q = ∞)",
  "kT (keV)": "kT (keV)",
  "kT {#} keV · E₀ {#} keV · width {#} keV": "kT {#} keV · E₀ {#} keV · ширина {#} keV",
  "kT {a} keV · D–T {b} m³/s · {c}× D–D": "kT {a} keV · D–T {b} m³/s · {c}× D–D",
  "keeps itself hot": "сама держит нагрев",
  "laps {#}": "оборотов: {#}",
  "lead–lithium": "свинец–литий",
  "liquid lithium": "жидкий литий",
  "loading INCOGNITA's cross sections…": "загрузка сечений INCOGNITA…",
  "missing {#} u  =  {#} MeV out": "недостаёт {#} u  =  выделено {#} MeV",
  "n τE (s/m³)": "n τE (s/m³)",
  "negative: turns the other way": "отрицательный: крутится обратно",
  "neutron escapes": "нейтрон уходит",
  "peak near {#} keV": "пик около {#} keV",
  "per fusion neutron · {#} neutrons · cross sections are simple fits": "на нейтрон синтеза · нейтронов: {#} · сечения — простые аппроксимации",
  "plasma": "плазма",
  "product ×{a}": "произведение ×{a}",
  "push {a} keV · chance to tunnel head-on {b}": "толчок {a} keV · шанс туннелирования в лоб {b}",
  "q = {#}": "q = {#}",
  "q = {#}/{#}: closes after {#} lap": "q = {#}/{#}: замыкается после {#}-го оборота",
  "q = {#}/{#}: closes after {#} laps": "q = {#}/{#}: замыкается после {#}-го оборота",
  "q = {#}: no simple fraction, the dots fill the circle": "q = {#}: не простая дробь, точки заполняют круг",
  "screen radius is logarithmic: {#} fm to {#} fm": "радиус на экране логарифмический: от {#} fm до {#} fm",
  "shield": "защита",
  "tap to fire": "коснитесь — выстрел",
  "the cut, flat": "сечение, развёрнутое",
  "time slowed {a}×": "время замедлено в {a} раз",
  "tries {#} · fused {#}": "попыток: {#} · слияний: {#}",
  "tritium made, by depth": "наработка трития по глубине",
  "triton": "тритон",
  "tunnels more easily": "легче туннелирует",
  "turns at {#} fm": "разворот на {#} fm",
  "wall": "стенка",
  "{#} MeV": "{#} MeV",
  "{#} cm": "{#} см",
  "{#} in {a}": "{#} из {a}",
  "{#} keV": "{#} keV",
  "{#} keV = {#} million K": "{#} keV = {#} млн K",
  "{a} %": "{a} %",
  "{a} + {a} → {b}: about {c} MeV released": "{a} + {a} → {b}: выделяется около {c} MeV",
  "{a} + {a} → {b}: costs {c} MeV": "{a} + {a} → {b}: затраты {c} MeV",
  "{a} keV · chance {b}": "{a} keV · шанс {b}",
  "{a} keV · nτ {b} · {c}": "{a} keV · nτ {b} · {c}",
  "{a} · two branches, equally likely": "{a} · две равновероятные ветви",
  "{a} · ρ up to {b} · {c} turns a second": "{a} · ρ до {b} · {c} об/с",
  "σ at {#} MeV:  (n,α) {#} mb · (n,p) {#} mb · (n,{#}n) {#} mb": "σ при {#} MeV:  (n,α) {#} mb · (n,p) {#} mb · (n,{#}n) {#} mb",
  "⁶Li {#} · ⁷Li {#} · (n,{#}n) {#}": "⁶Li {#} · ⁷Li {#} · (n,{#}n) {#}",
  "⁶Li {#} · ⁷Li {#} · (n,{#}n) {#} · captured {#} · leaked {#}": "⁶Li {#} · ⁷Li {#} · (n,{#}n) {#} · захвачено {#} · утекло {#}",
  "⟨σv⟩ (m³/s)": "⟨σv⟩ (m³/s)",
});
