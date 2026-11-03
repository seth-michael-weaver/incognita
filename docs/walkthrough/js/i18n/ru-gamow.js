/* Russian: gamow (Глава 30, пик Гамова и зажигание) */
WT.L.ch.gamow = {
  num: "Глава 30", title: "Пик Гамова и зажигание", short: "Пик Гамова",
  lead: "Горячая плазма горит в узком окне энергий: ядра в нём достаточно быстры, чтобы туннелировать, и достаточно многочисленны, чтобы это имело значение.",
  html: `
<div class="step">
  <h3>Пик Гамова</h3>
  <p>Быстрых ядер мало; быстрые легче туннелируют. Их произведение светится: это пик Гамова. Перетащите линию температуры.</p>
  <div class="ctl"><label for="gw-t">Температура kT (keV)</label><input id="gw-t" type="range" data-bind="lT" min="0" max="2" step="0.01" value="1"><output data-show="T" data-fmt="1"></output></div>
  <div class="formula">E₀ = (E<sub>G</sub> (kT)² / 4)<sup>1/3</sup> · ширина 4√(E₀kT/3)</div>
</div>
<div class="step">
  <h3>Реактивность топлив</h3>
  <p>Сложите всё окно — получится реактивность ⟨σv⟩. D–T с большим отрывом выигрывает при любой температуре, доступной установке.</p>
  <div class="ctl"><label for="gw-t2">Температура kT (keV)</label><input id="gw-t2" type="range" data-bind="lT" min="0" max="2" step="0.01" value="1"><output data-show="T" data-fmt="1"></output></div>
  <div class="formula">⟨σv⟩ = ∫ σ(E) v f(E) dE</div>
</div>
<div class="step">
  <h3>Критерий Лоусона и зажигание</h3>
  <p>Перетащите плазму к нужным температуре и удержанию, затем отпустите. Выше верхней кривой она сама поддерживает свою температуру.</p>
  <div class="btns"><button class="btn" data-act="lowgo">Слабая установка</button> <button class="btn ghost" data-act="higo">Мощная установка</button></div>
  <div class="formula">зажигание: n τ<sub>E</sub> T ≳ 3·10²¹ keV s m⁻³</div>
</div>`,
};
