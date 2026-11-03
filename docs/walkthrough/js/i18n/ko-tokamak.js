/* Korean: tokamak (31장, 자기 가둠) */
WT.L.ch.tokamak = {
  num: "31장", title: "자기 가둠", short: "가둠",
  lead: "어떤 벽도 1억 도의 기체에 닿을 수 없습니다. 하전 입자는 자기력선을 가로지를 수 없으므로 자기장이 그 기체를 붙잡아 둘 수 있습니다.",
  html: `
<div class="step">
  <h3>자기장 속의 회전 운동</h3>
  <p>자기장을 가로지르는 방향으로는 전하가 원을 그릴 수밖에 없고, 자기장을 따라서는 미끄러져 갑니다. 그림을 끌어 돌려 보세요.</p>
  <div class="ctl"><label for="tk-b">자기장 B (테슬라)</label><input id="tk-b" type="range" data-bind="B" min="1" max="12" step="0.1" value="5"><output data-show="B" data-fmt="1"></output></div>
  <div class="btns tk-sp"><button class="btn ghost" data-act="spd" aria-pressed="true">중양성자</button> <button class="btn ghost" data-act="spa" aria-pressed="false">알파</button> <button class="btn ghost" data-act="spe" aria-pressed="false">전자</button></div>
  <div class="formula">ρ = √(2mE) / (|q| B)</div>
</div>
<div class="step">
  <h3>토로이달 자기력선과 안전 인자</h3>
  <p>곧은 자기장은 양 끝이 열려 있으므로, 고리 모양으로 구부리고 비틉니다. 이것이 토카막입니다. 한 바퀴 돌 때마다 자기력선이 단면을 지나는 곳에 점이 하나 찍힙니다.</p>
  <div class="ctl"><label for="tk-q">안전 인자 q</label><input id="tk-q" type="range" data-bind="q" min="1" max="4" step="0.01" value="2.62" data-instant><output data-show="q" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="q32">q = 3/2</button> <button class="btn ghost" data-act="q2">q = 2</button> <button class="btn ghost" data-act="qg">q = 황금비</button></div>
</div>
<div class="step">
  <h3>자기 섬과 자기력선의 혼돈</h3>
  <p>자기장의 잔물결은 q가 간단한 분수인 곳에서 자기면을 찢어 자기 섬으로 만들고, 이어서 혼돈으로 만듭니다. 클릭해서 자기력선을 하나 시작하세요.</p>
  <div class="ctl"><label for="tk-k">섭동 K</label><input id="tk-k" type="range" data-bind="K" min="0" max="6" step="0.05" value="1.5" data-instant><output data-show="K" data-fmt="2"></output></div>
  <div class="formula">ψ′ = ψ − (K/2π) ψ′/(1+ψ′) sin θ<br>θ′ = θ + 2π/q(ψ′) − (K/2π) cos θ/(1+ψ′)²</div>
</div>`,
};
