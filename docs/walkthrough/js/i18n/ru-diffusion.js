/* Russian: diffusion (Критический размер и утечка) */
WT.L.ch.diffusion = {
  num: "Урок 1", title: "Критический размер и утечка", short: "Критический размер",
  html: `
<div class="step">
  <h3>Нейтроны блуждают, часть утекает</h3>
  <p>Нейтрон движется зигзагом от столкновения к столкновению, пока что-нибудь его не поглотит. Родившись у края, он может выйти наружу и потеряться. У большей зоны поверхность меньше по отношению к объёму, поэтому утекает меньшая доля.</p>
  <div class="ctl"><label for="df-w0">Ширина зоны (см)</label><input id="df-w0" type="range" data-bind="w" data-instant min="20" max="200" step="2" value="60"><output data-show="w" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Форма потока</h3>
  <p>Распределение нейтронов устанавливается в единую форму, спадающую почти до нуля на краю: косинус поперёк пластины, sin(<i>r</i>)/<i>r</i> в шаре, функция Бесселя, умноженная на косинус, в цилиндре. Насколько круто она должна изгибаться, показывает <b>геометрический параметр</b> <i>B</i>².</p>
  <div class="btns"><button class="btn ghost" data-act="dfslab" aria-pressed="false">Пластина</button><button class="btn ghost" data-act="dfsph" aria-pressed="true">Шар</button><button class="btn ghost" data-act="dfcyl" aria-pressed="false">Цилиндр</button></div>
  <div class="ctl"><label for="df-w1">Ширина зоны (см)</label><input id="df-w1" type="range" data-bind="w" data-instant min="20" max="200" step="2" value="80"><output data-show="w" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Критический размер</h3>
  <p>Одногрупповая диффузия даёт <i>k</i><sub>eff</sub> = <i>k</i><sub>∞</sub> / (1 + <i>M</i>²<i>B</i>²), где площадь миграции <i>M</i>² в водяном реакторе около 60 см². Зона критична, когда <i>B</i>² равен материальному параметру (<i>k</i><sub>∞</sub> − 1)/<i>M</i>². Найдите этот размер.</p>
  <div class="btns"><button class="btn ghost" data-act="dfslab" aria-pressed="false">Пластина</button><button class="btn ghost" data-act="dfsph" aria-pressed="true">Шар</button><button class="btn ghost" data-act="dfcyl" aria-pressed="false">Цилиндр</button></div>
  <div class="ctl"><label for="df-w2">Ширина зоны (см)</label><input id="df-w2" type="range" data-bind="w" data-instant min="20" max="200" step="1" value="90"><output data-show="w" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Отражатель сберегает нейтроны</h3>
  <p>Окружите плоскую зону водой: часть вылетевших нейтронов рассеивается обратно. Поток уже не падает до нуля на краю зоны, и более тонкая зона достигает того же <i>k</i>; выигрыш называется <b>эффективной добавкой отражателя</b>, здесь около 6 см с каждой стороны.</p>
  <div class="btns"><button class="btn ghost" data-act="dfrefl" aria-pressed="true">Водяной отражатель</button></div>
  <div class="ctl"><label for="df-w3">Ширина зоны (см)</label><input id="df-w3" type="range" data-bind="w" data-instant min="20" max="120" step="1" value="44"><output data-show="w" data-fmt="0"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "drag the edge": "тяните край",
  "{#} cm": "{#} см",
  "red: leaked": "красные: утекли",
  "red: leaked out · blue: absorbed inside": "красные: утекли наружу · синие: поглощены внутри",
  "leak: walk {#} % · diffusion {#} %": "утечка: блуждание {#} % · диффузия {#} %",
  "leak: walk … · diffusion {#} %": "утечка: блуждание … · диффузия {#} %",
  "share leaking: random walk {#} % · diffusion theory {#} %": "доля утечки: случайное блуждание {#} % · теория диффузии {#} %",
  "share leaking: random walk … · diffusion theory {#} %": "доля утечки: случайное блуждание … · теория диффузии {#} %",
  "k_eff = k∞ × ({#} − leak) = {#}": "k_eff = k∞ × ({#} − утечка) = {#}",
  "water": "вода",
  "slab core": "плоская зона",
  "slab": "пластина",
  "sphere": "шар",
  "cylinder": "цилиндр",
  "flux across the middle": "поток через середину",
  "−D∇²φ + Σₐφ = (νΣ_f / k) φ": "−D∇²φ + Σₐφ = (νΣ_f / k) φ",
  "B² = (π/a)² = {#} × {#}⁻⁴ cm⁻²": "B² = (π/a)² = {#} × {#}⁻⁴ cm⁻²",
  "B² = (π/R)² = {#} × {#}⁻⁴ cm⁻²": "B² = (π/R)² = {#} × {#}⁻⁴ cm⁻²",
  "B² = ({#}/R)² + (π/H)² = {#} × {#}⁻⁴ cm⁻²": "B² = ({#}/R)² + (π/H)² = {#} × {#}⁻⁴ cm⁻²",
  "{#} × {#}⁻⁴ cm⁻²": "{#} × {#}⁻⁴ cm⁻²",
  "slab {#} cm wide · smaller core → sharper bend → larger B²": "пластина шириной {#} см · меньше зона → круче изгиб → больше B²",
  "sphere {#} cm wide · smaller core → sharper bend → larger B²": "шар шириной {#} см · меньше зона → круче изгиб → больше B²",
  "cylinder {#} cm wide · smaller core → sharper bend → larger B²": "цилиндр шириной {#} см · меньше зона → круче изгиб → больше B²",
  "k = {#}": "k = {#}",
  "critical {#} cm": "критично при {#} см",
  "core width →": "ширина зоны →",
  "critical: B² = B²ₘ, k_eff = {#}": "критично: B² = B²ₘ, k_eff = {#}",
  "k_eff = {#} / ({#} + {#} cm² × {#}e{#} cm⁻²) = {#}": "k_eff = {#} / ({#} + {#} cm² × {#}e{#} cm⁻²) = {#}",
  "reflected: k_eff {#} · bare: {#} · savings {#} cm per side": "с отражателем: k_eff {#} · без: {#} · добавка {#} см с каждой стороны",
  "bare: k_eff {#} · critical at {#} cm": "без отражателя: k_eff {#} · критично при {#} см",
  "illustration": "иллюстрация",
});
