/* Russian: tokamak (Глава 31, магнитное удержание) */
WT.L.ch.tokamak = {
  num: "Глава 31", title: "Магнитное удержание", short: "Удержание",
  lead: "Никакая стенка не может касаться газа в 100 миллионов градусов. Удержать его может магнитное поле, потому что заряженные частицы не могут пересекать силовые линии.",
  html: `
<div class="step">
  <h3>Вращение в магнитном поле</h3>
  <p>Поперёк поля заряд может только кружить; вдоль поля он скользит. Перетащите картинку, чтобы повернуть её.</p>
  <div class="ctl"><label for="tk-b">Поле B (тесла)</label><input id="tk-b" type="range" data-bind="B" min="1" max="12" step="0.1" value="5"><output data-show="B" data-fmt="1"></output></div>
  <div class="btns tk-sp"><button class="btn ghost" data-act="spd" aria-pressed="true">Дейтрон</button> <button class="btn ghost" data-act="spa" aria-pressed="false">Альфа</button> <button class="btn ghost" data-act="spe" aria-pressed="false">Электрон</button></div>
  <div class="formula">ρ = √(2mE) / (|q| B)</div>
</div>
<div class="step">
  <h3>Тороидальные силовые линии и запас устойчивости</h3>
  <p>У прямого поля открытые концы, поэтому согните его в кольцо и закрутите: получится токамак. На каждом обороте линия оставляет точку там, где пересекает сечение.</p>
  <div class="ctl"><label for="tk-q">Запас устойчивости q</label><input id="tk-q" type="range" data-bind="q" min="1" max="4" step="0.01" value="2.62" data-instant><output data-show="q" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="q32">q = 3/2</button> <button class="btn ghost" data-act="q2">q = 2</button> <button class="btn ghost" data-act="qg">q = золотое</button></div>
</div>
<div class="step">
  <h3>Магнитные острова и хаос силовых линий</h3>
  <p>Возмущения поля рвут поверхности на острова там, где q — простая дробь, а затем в хаос. Щёлкните, чтобы запустить силовую линию.</p>
  <div class="ctl"><label for="tk-k">Возмущение K</label><input id="tk-k" type="range" data-bind="K" min="0" max="6" step="0.05" value="1.5" data-instant><output data-show="K" data-fmt="2"></output></div>
  <div class="formula">ψ′ = ψ − (K/2π) ψ′/(1+ψ′) sin θ<br>θ′ = θ + 2π/q(ψ′) − (K/2π) cos θ/(1+ψ′)²</div>
</div>`,
};
