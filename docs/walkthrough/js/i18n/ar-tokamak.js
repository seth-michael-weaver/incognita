/* Arabic: tokamak (الفصل 31، الحصر المغناطيسي) */
WT.L.ch.tokamak = {
  num: "الفصل 31", title: "الحصر المغناطيسي", short: "الحصر",
  lead: "لا يمكن لأي جدار أن يلامس غازًا حرارته 100 مليون درجة. لكن المجال المغناطيسي يستطيع احتواءه، لأن الجسيمات المشحونة لا تستطيع عبور خطوط المجال.",
  html: `
<div class="step">
  <h3>الدوران في مجال مغناطيسي</h3>
  <p>عَبر المجال لا تستطيع الشحنة إلا أن تدور في دائرة؛ وعلى امتداده تنزلق. اسحب الصورة لتديرها.</p>
  <div class="ctl"><label for="tk-b">المجال B (تسلا)</label><input id="tk-b" type="range" data-bind="B" min="1" max="12" step="0.1" value="5"><output data-show="B" data-fmt="1"></output></div>
  <div class="btns tk-sp"><button class="btn ghost" data-act="spd" aria-pressed="true">ديوترون</button> <button class="btn ghost" data-act="spa" aria-pressed="false">ألفا</button> <button class="btn ghost" data-act="spe" aria-pressed="false">إلكترون</button></div>
  <div class="formula">ρ = √(2mE) / (|q| B)</div>
</div>
<div class="step">
  <h3>خطوط المجال الحلقية ومعامل الأمان</h3>
  <p>للمجال المستقيم طرفان مفتوحان، فاثنِه على شكل حلقة ولُفَّه: هذا هو التوكاماك. كل دورة تترك نقطة حيث يعبر الخط المقطع.</p>
  <div class="ctl"><label for="tk-q">معامل الأمان q</label><input id="tk-q" type="range" data-bind="q" min="1" max="4" step="0.01" value="2.62" data-instant><output data-show="q" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="q32">q = 3/2</button> <button class="btn ghost" data-act="q2">q = 2</button> <button class="btn ghost" data-act="qg">q = النسبة الذهبية</button></div>
</div>
<div class="step">
  <h3>الجزر المغناطيسية وفوضى خطوط المجال</h3>
  <p>تمزّق التموجات في المجال السطوحَ إلى جزر حيث تكون q كسرًا بسيطًا، ثم إلى فوضى. انقر لتبدأ خط مجال.</p>
  <div class="ctl"><label for="tk-k">الاضطراب K</label><input id="tk-k" type="range" data-bind="K" min="0" max="6" step="0.05" value="1.5" data-instant><output data-show="K" data-fmt="2"></output></div>
  <div class="formula">ψ′ = ψ − (K/2π) ψ′/(1+ψ′) sin θ<br>θ′ = θ + 2π/q(ψ′) − (K/2π) cos θ/(1+ψ′)²</div>
</div>`,
};
