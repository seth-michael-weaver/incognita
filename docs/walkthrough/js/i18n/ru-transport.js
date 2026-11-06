/* Russian: transport (Перенос нейтронов и метод Монте-Карло) */
WT.L.ch.transport = {
  num: "Урок 1", title: "Перенос нейтронов и метод Монте-Карло", short: "Монте-Карло",
  html: `
<div class="step">
  <h3>Уравнение переноса</h3>
  <p>Строго говоря, нейтроны подчиняются уравнению Больцмана для углового потока <i>ψ</i>(<b>r</b>, <b>Ω</b>, <i>E</i>): <b>Ω</b>·∇<i>ψ</i> + Σ<sub>t</sub><i>ψ</i> = ∫∫Σ<sub>s</sub><i>ψ</i>′ d<b>Ω</b>′d<i>E</i>′ + (<i>χ</i>/4π<i>k</i>)∫<i>ν</i>Σ<sub>f</sub><i>φ</i>′ d<i>E</i>′. Метод Монте-Карло решает его, разыгрывая нейтроны по одному: пролёт <i>s</i> = −ln <i>ξ</i> / Σ<sub>t</sub>, затем рассеяние, захват или деление.</p>
  <div class="btns"><button class="btn" data-act="trnew">Новый нейтрон</button></div>
</div>
<div class="step">
  <h3>Где диффузия ошибается</h3>
  <p>Диффузионное приближение предполагает почти одинаковый поток во всех направлениях. Оно не работает в пределах одного-двух свободных пробегов от поверхности и в сильных поглотителях. Сравните его с потоком Монте-Карло в пластине с однородным источником, увеличивая поглощение.</p>
  <div class="ctl"><label for="tr-pa">Поглощение Σ<sub>a</sub>/Σ<sub>t</sub></label><input id="tr-pa" type="range" data-bind="pa" data-instant min="0.05" max="0.8" step="0.05" value="0.5"><output data-show="pa" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>Метод итераций источника</h3>
  <p>Чтобы найти <i>k</i><sub>eff</sub>, точки делений каждого поколения становятся источником следующего; <i>k</i> — число сохранённых точек на один запущенный нейтрон. Начните с плохого приближения, все нейтроны у одного края, и посмотрите, как источник расплывается в фундаментальную моду.</p>
  <div class="btns"><button class="btn" data-act="trbad">Начать с плохого приближения</button></div>
</div>
<div class="step">
  <h3>Сошёлся ли источник?</h3>
  <p>Энтропия Шеннона <i>H</i> = −Σ <i>p</i><sub>b</sub> log<sub>2</sub> <i>p</i><sub>b</sub> источника, разбитого по ячейкам, выходит на плато, когда источник установился; только после этого поколения усредняются. Погрешность <i>k</i> убывает как 1/√<i>N</i> с числом учтённых историй.</p>
  <div class="ctl"><label for="tr-n">Историй на поколение</label><input id="tr-n" type="range" data-bind="nh" data-instant min="100" max="2000" step="100" value="400"><output data-show="nh" data-fmt="0"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "vacuum": "вакуум",
  "glow: collision density": "свечение: плотность столкновений",
  "amber glow: where collisions pile up": "янтарное свечение: где копятся столкновения",
  "tap the slab to start neutrons": "коснитесь пластины, чтобы запустить нейтроны",
  "scatter": "рассеяние",
  "capture": "захват",
  "fission": "деление",
  "leak": "утечка",
  "chance to fly at least s:  e^(−Σₜ s)": "вероятность пролететь не меньше s:  e^(−Σₜ s)",
  "{#} free paths": "свободных пробегов: {#}",
  "ξ = {#}  →  s = −ln ξ / Σₜ = {#} free paths": "ξ = {#}  →  s = −ln ξ / Σₜ = {#} свободного пробега",
  "infinite medium S/Σₐ": "бесконечная среда S/Σₐ",
  "Monte Carlo": "Монте-Карло",
  "diffusion": "диффузия",
  "flux": "поток",
  "diffusion vs Monte Carlo: +{#} % at the surface, +{#} % in the middle": "диффузия против Монте-Карло: +{#} % у поверхности, +{#} % в середине",
  "diffusion vs Monte Carlo: +{#} % at the surface, {#} % in the middle": "диффузия против Монте-Карло: +{#} % у поверхности, {#} % в середине",
  "diffusion vs Monte Carlo: {#} % at the surface, +{#} % in the middle": "диффузия против Монте-Карло: {#} % у поверхности, +{#} % в середине",
  "diffusion vs Monte Carlo: {#} % at the surface, {#} % in the middle": "диффузия против Монте-Карло: {#} % у поверхности, {#} % в середине",
  "tap: drop the source there": "коснитесь: источник туда",
  "tap the slab to drop the whole source there": "коснитесь пластины, чтобы перенести туда весь источник",
  "generation {#}": "поколение {#}",
  "source · dashed: fundamental mode": "источник · штрих: фундаментальная мода",
  "fission source · dashed: fundamental mode": "источник делений · штрих: фундаментальная мода",
  "source entropy H (bits)": "энтропия источника H (бит)",
  "inactive | active": "неактивные | активные",
  "inactive  |  active generations": "неактивные  |  активные поколения",
  "k per generation": "k по поколениям",
  "generation {#}: k = {#} · H = {#} bits": "поколение {#}: k = {#} · H = {#} бит",
  "starting…": "запуск…",
  "k_eff = {#} ± {#} ({#} × {#} histories) · diffusion {#}": "k_eff = {#} ± {#} ({#} × {#} историй) · диффузия {#}",
  "{#} generations, averaging starts after {#}": "поколений: {#}, усреднение начнётся после {#}",
  "illustrative one-group data": "иллюстративные одногрупповые данные",
});
