/* Simplified Chinese (简体中文): the Gamow peak and ignition (chapter 30) */
WT.L.ch.gamow = {
  num: "第 30 章", title: "伽莫夫峰与点火", short: "伽莫夫峰",
  lead: "热等离子体通过一个狭窄的能量窗口燃烧：快到足以隧穿，又多到足以起作用。",
  html: `
<div class="step">
  <h3>伽莫夫峰</h3>
  <p>快的原子核很少；快的更容易隧穿。两者的乘积发亮：这就是伽莫夫峰。拖动温度线。</p>
  <div class="ctl"><label for="gw-t">温度 kT (keV)</label><input id="gw-t" type="range" data-bind="lT" min="0" max="2" step="0.01" value="1"><output data-show="T" data-fmt="1"></output></div>
  <div class="formula">E₀ = (E<sub>G</sub> (kT)² / 4)<sup>1/3</sup> · 宽度 4√(E₀kT/3)</div>
</div>
<div class="step">
  <h3>燃料的反应率参数</h3>
  <p>把整个窗口加起来，就得到反应率参数 ⟨σv⟩。在装置能达到的任何温度下，D–T 都遥遥领先。</p>
  <div class="ctl"><label for="gw-t2">温度 kT (keV)</label><input id="gw-t2" type="range" data-bind="lT" min="0" max="2" step="0.01" value="1"><output data-show="T" data-fmt="1"></output></div>
  <div class="formula">⟨σv⟩ = ∫ σ(E) v f(E) dE</div>
</div>
<div class="step">
  <h3>劳森判据与点火</h3>
  <p>把等离子体拖到某个温度和约束，然后松手。在最上面那条曲线之上，它能自行保持高温。</p>
  <div class="btns"><button class="btn" data-act="lowgo">试试弱装置</button> <button class="btn ghost" data-act="higo">试试强装置</button></div>
  <div class="formula">点火：n τ<sub>E</sub> T ≳ 3·10²¹ keV s m⁻³</div>
</div>`,
};
