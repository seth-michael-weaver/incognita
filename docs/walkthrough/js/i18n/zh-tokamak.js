/* Simplified Chinese (简体中文): magnetic confinement (chapter 31) */
WT.L.ch.tokamak = {
  num: "第 31 章", title: "磁约束", short: "磁约束",
  lead: "没有任何器壁能接触一亿度的气体。磁场却能约束它，因为带电粒子无法横穿磁力线。",
  html: `
<div class="step">
  <h3>磁场中的回旋运动</h3>
  <p>垂直于磁场，电荷只能绕圈；沿着磁场，它可以滑动。拖动图像来旋转它。</p>
  <div class="ctl"><label for="tk-b">磁场 B（特斯拉）</label><input id="tk-b" type="range" data-bind="B" min="1" max="12" step="0.1" value="5"><output data-show="B" data-fmt="1"></output></div>
  <div class="btns tk-sp"><button class="btn ghost" data-act="spd" aria-pressed="true">氘核</button> <button class="btn ghost" data-act="spa" aria-pressed="false">α 粒子</button> <button class="btn ghost" data-act="spe" aria-pressed="false">电子</button></div>
  <div class="formula">ρ = √(2mE) / (|q| B)</div>
</div>
<div class="step">
  <h3>环向磁力线与安全因子</h3>
  <p>直的磁场两端是开口的，所以把它弯成一个环并加以扭转：这就是托卡马克。磁力线每绕一圈，就在穿过截面的地方留下一个点。</p>
  <div class="ctl"><label for="tk-q">安全因子 q</label><input id="tk-q" type="range" data-bind="q" min="1" max="4" step="0.01" value="2.62" data-instant><output data-show="q" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="q32">q = 3/2</button> <button class="btn ghost" data-act="q2">q = 2</button> <button class="btn ghost" data-act="qg">q = 黄金比</button></div>
</div>
<div class="step">
  <h3>磁岛与磁力线混沌</h3>
  <p>磁场中的微小起伏会在 q 为简单分数的地方把磁面撕裂成磁岛，进而变成混沌。点击以发出一条磁力线。</p>
  <div class="ctl"><label for="tk-k">扰动 K</label><input id="tk-k" type="range" data-bind="K" min="0" max="6" step="0.05" value="1.5" data-instant><output data-show="K" data-fmt="2"></output></div>
  <div class="formula">ψ′ = ψ − (K/2π) ψ′/(1+ψ′) sin θ<br>θ′ = θ + 2π/q(ψ′) − (K/2π) cos θ/(1+ψ′)²</div>
</div>`,
};
