/* Japanese: tokamak (第31章、磁場閉じ込め) */
WT.L.ch.tokamak = {
  num: "第31章", title: "磁場閉じ込め", short: "閉じ込め",
  lead: "1億度のガスに触れられる壁はありません。磁場なら保持できます。荷電粒子は磁力線を横切れないからです。",
  html: `
<div class="step">
  <h3>磁場中の旋回運動</h3>
  <p>磁場を横切る向きには、電荷は円を描くことしかできません。磁場に沿っては滑っていきます。図をドラッグすると回転します。</p>
  <div class="ctl"><label for="tk-b">磁場 B（テスラ）</label><input id="tk-b" type="range" data-bind="B" min="1" max="12" step="0.1" value="5"><output data-show="B" data-fmt="1"></output></div>
  <div class="btns tk-sp"><button class="btn ghost" data-act="spd" aria-pressed="true">重陽子</button> <button class="btn ghost" data-act="spa" aria-pressed="false">α粒子</button> <button class="btn ghost" data-act="spe" aria-pressed="false">電子</button></div>
  <div class="formula">ρ = √(2mE) / (|q| B)</div>
</div>
<div class="step">
  <h3>トロイダル磁力線と安全係数</h3>
  <p>まっすぐな磁場には開いた端があります。そこで輪に曲げてねじります。これがトカマクです。1周するたびに、磁力線が断面を横切る位置に点が残ります。</p>
  <div class="ctl"><label for="tk-q">安全係数 q</label><input id="tk-q" type="range" data-bind="q" min="1" max="4" step="0.01" value="2.62" data-instant><output data-show="q" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="q32">q = 3/2</button> <button class="btn ghost" data-act="q2">q = 2</button> <button class="btn ghost" data-act="qg">q = 黄金比</button></div>
</div>
<div class="step">
  <h3>磁気島と磁力線のカオス</h3>
  <p>磁場のさざ波が、q が簡単な分数になるところで磁気面を引き裂いて磁気島をつくり、さらにカオスに変えます。クリックすると磁力線を1本たどりはじめます。</p>
  <div class="ctl"><label for="tk-k">摂動 K</label><input id="tk-k" type="range" data-bind="K" min="0" max="6" step="0.05" value="1.5" data-instant><output data-show="K" data-fmt="2"></output></div>
  <div class="formula">ψ′ = ψ − (K/2π) ψ′/(1+ψ′) sin θ<br>θ′ = θ + 2π/q(ψ′) − (K/2π) cos θ/(1+ψ′)²</div>
</div>`,
};
