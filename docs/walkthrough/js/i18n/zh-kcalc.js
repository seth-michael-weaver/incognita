/* Chinese (Simplified): kcalc (Computing criticality) */
WT.L.ch.kcalc = {
  num: "第1课", title: "临界计算", short: "计算 k",
  html: `
<div class="step">
  <h3>基准装置</h3>
  <p>ICSBEP 中的四个快中子金属临界装置，按比例绘制。Godiva 和 Jezebel 是裸球；Flattop-25 和 Flattop-Pu 带天然铀反射层。</p>
</div>
<div class="step">
  <h3>计算的 <i>k</i><sub>eff</sub></h3>
  <p>OpenMC，连续能量，三维几何。四个结果都在基准的 ±1σ 之内。拟合不使用 <i>k</i><sub>eff</sub>。</p>
</div>
<div class="step">
  <h3>灵敏度分布</h3>
  <p><i>k</i><sub>eff</sub> 对各反应的伴随灵敏度，按单位对数能降。</p>
  <div class="btns"><button class="btn ghost" data-act="se0" aria-pressed="true">Godiva</button><button class="btn ghost" data-act="se1" aria-pressed="false">Jezebel</button><button class="btn ghost" data-act="se2" aria-pressed="false">Flattop-Pu</button></div>
</div>
<div class="step">
  <h3>直接扰动验证</h3>
  <p>由灵敏度预测的 <i>k</i><sub>eff</sub> 变化与重新计算结果的比较，共 63 组扰动数据。</p>
</div>
<div class="step">
  <h3>C5G7 反应堆堆芯</h3>
  <p>OECD/NEA C5G7 四分之一堆芯，1,056 根 UO<sub>2</sub> 和 MOX 燃料棒：二维，以及插入控制棒的三维扩展。<i>k</i><sub>eff</sub> 在二维中与参考值相差不超过 19&nbsp;pcm，在每个三维构型中不超过 9&nbsp;pcm。</p>
  <div class="btns"><button class="btn ghost" data-act="c50" aria-pressed="true">2-D</button><button class="btn ghost" data-act="c51" aria-pressed="false">3-D</button><button class="btn ghost" data-act="c52" aria-pressed="false">控制棒 A</button><button class="btn ghost" data-act="c53" aria-pressed="false">控制棒 B</button></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "{#} pcm  (±{#} benchmark)": "{#} pcm  (基准 ±{#})",
  "+{#} pcm  (±{#} benchmark)": "+{#} pcm  (基准 ±{#})",
  "Calculated − experimental k, with the benchmark ±{#}σ band": "计算 − 实验 k，附基准 ±{#}σ 区间",
  "Drag to rotate": "拖动旋转",
  "Godiva, integral sensitivity: ν {#}, fission {#} (% k per % change)": "Godiva, 积分灵敏度：ν {#}，裂变 {#}（每 1 % 变化引起的 k 的 %）",
  "Jezebel, integral sensitivity: ν {#}, fission {#} (% k per % change)": "Jezebel, 积分灵敏度：ν {#}，裂变 {#}（每 1 % 变化引起的 k 的 %）",
  "Flattop-Pu, integral sensitivity: ν {#}, fission {#} (% k per % change)": "Flattop-Pu, 积分灵敏度：ν {#}，裂变 {#}（每 1 % 变化引起的 k 的 %）",
  "Godiva: ν {#}, fission {#}": "Godiva: ν {#}，裂变 {#}",
  "Jezebel: ν {#}, fission {#}": "Jezebel: ν {#}，裂变 {#}",
  "Flattop-Pu: ν {#}, fission {#}": "Flattop-Pu: ν {#}，裂变 {#}",
  "UO₂: {#} × mean": "UO₂: {#} × 平均值",
  "MOX {#} %: {#} × mean": "MOX {#} %: {#} × 平均值",
  "OpenMC re-solve, Δk (pcm)": "OpenMC 重新计算，Δk (pcm)",
  "Predicted from sensitivities, Δk (pcm)": "由灵敏度预测，Δk (pcm)",
  "predicted Δk, pcm": "预测 Δk，pcm",
  "U{#} capture": "U{#} 俘获",
  "Pu{#} capture": "Pu{#} 俘获",
  "U{#} elastic": "U{#} 弹性散射",
  "Pu{#} elastic": "Pu{#} 弹性散射",
  "U{#} fission": "U{#} 裂变",
  "Pu{#} fission": "Pu{#} 裂变",
  "U{#} inelastic": "U{#} 非弹性散射",
  "Pu{#} inelastic": "Pu{#} 非弹性散射",
  "U{#} neutrons per fission (ν)": "U{#} 每次裂变中子数 (ν)",
  "Pu{#} neutrons per fission (ν)": "Pu{#} 每次裂变中子数 (ν)",
  "Relative pin power (hover a pin)": "燃料棒相对功率（将指针移到燃料棒上）",
  "Relative pin power (tap a pin)": "燃料棒相对功率（点按燃料棒）",
  "To scale.": "按比例。",
  "To scale. Drag to rotate.": "按比例。拖动旋转。",
  "core {#} cm, reflector {#} cm": "堆芯 {#} cm，反射层 {#} cm",
  "radius {#} cm": "半径 {#} cm",
  "{#} cm in {#} cm": "{#} cm / {#} cm",
  "k = {#}; reference {#} ({#} pcm)": "k = {#}；参考值 {#}（{#} pcm）",
  "k = {#}; reference {#} (+{#} pcm)": "k = {#}；参考值 {#}（+{#} pcm）",
  "k {#}, reference {#}": "k {#}，参考值 {#}",
  "plutonium in natural uranium": "天然铀包覆的钚",
  "plutonium metal": "金属钚",
  "uranium{#} in natural uranium": "天然铀包覆的铀{#}",
  "uranium{#} metal": "金属铀{#}",
  "water": "水",
  "×{#} of mean": "平均值的 ×{#}",
  "U{#} ν": "U{#} ν",
  "Pu{#} ν": "Pu{#} ν",
  "Godiva   k = {#}": "Godiva   k = {#}",
  "Godiva {#}": "Godiva {#}",
  "Godiva: rms {#} pcm": "Godiva: rms {#} pcm",
  "Jezebel   k = {#}": "Jezebel   k = {#}",
  "Jezebel {#}": "Jezebel {#}",
  "Jezebel: rms {#} pcm": "Jezebel: rms {#} pcm",
  "Flattop-Pu   k = {#}": "Flattop-Pu   k = {#}",
  "Flattop-Pu {#}": "Flattop-Pu {#}",
  "Flattop-Pu: rms {#} pcm": "Flattop-Pu: rms {#} pcm",
  "Flattop{#}   k = {#}": "Flattop{#}   k = {#}",
  "Flattop{#} {#}": "Flattop{#} {#}",
  "{#} pcm (±{#})": "{#} pcm (±{#})",
  "+{#} pcm (±{#})": "+{#} pcm (±{#})",
  "{#} cm": "{#} cm",
  "{#} keV": "{#} keV",
  "{#} MeV": "{#} MeV",
  "OpenMC Δk": "OpenMC Δk"
});
