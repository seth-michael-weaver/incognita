/* Simplified Chinese: xsec (第 2 章，什么是截面) */
WT.L.ch.xsec = {
  num: "第 2 章", title: "什么是截面？", short: "截面",
  html: `
<div class="step">
  <p>每个圆盘是一个原子核的靶面积：它的<b>截面</b>，记作 σ（西格玛）。画面是从正上方俯视一层薄薄的原子核，中子则落在这层上的随机位置。落入圆盘内的中子与该原子核发生反应（橙色闪光）；落在圆盘之间的中子径直穿过（只是渐渐淡去）。</p>
  <p>因此发生反应的份额，就是圆盘覆盖这层面积的份额。黑色小方块是面积单位，即 1 <b>靶恩</b>（barn），10⁻²⁴ cm²：原子核真实的横截面大约就是一靶恩。</p>
  <div class="ctl"><label for="xs-e1">中子能量 (eV)</label><input id="xs-e1" type="range" data-bind="lgE" data-instant min="-2.3" max="2" step="0.01" value="2"><output data-show="Eshow" data-fmt="2"></output></div>
</div>
<div class="step">
  <p>越慢的中子看到的靶越大。圆盘并不是原子核的真实大小：它表示在这个能量下原子核对中子“显得有多大”，而慢中子在原子核附近停留的时间更长，因此更容易被捕获。对于俘获反应，这使 σ 按 1/速度 增长。</p>
  <p>薄层下方的曲线是 σ 随全部能量的变化（两个坐标轴都是对数刻度）；橙色圆点标出你选的能量。向下拖到最慢的中子，看圆盘变大、反应份额上升。</p>
  <div class="ctl"><label for="xs-e2">中子能量 (eV)</label><input id="xs-e2" type="range" data-bind="lgE" data-instant min="-2.3" max="2" step="0.01" value="-1.6"><output data-show="Eshow" data-fmt="2"></output></div>
</div>
<div class="step">
  <p>在共振处，靶会“膨胀”。在 7 eV 时，中子与原子核合在一起的能量恰好等于原子核自身某个能级的能量，因此被吸收得容易得多：圆盘面积增大约五十倍，这里达到约 400 靶恩。</p>
  <p>稍微偏离 7 eV，圆盘立刻缩回去：曲线上的峰很窄。真实的原子核有许多这样的峰；第 1 章展示过它们的“条形码”。</p>
  <div class="ctl"><label for="xs-e3">中子能量 (eV)</label><input id="xs-e3" type="range" data-bind="lgE" data-instant min="-2.3" max="2" step="0.005" value="0.845"><output data-show="Eshow" data-fmt="2"></output></div>
</div>`,
};

// canvas labels added 2026-10-29 (I18NLABELS_B)
Object.assign(WT.L.labels, {
  "this square: {#} barn = {#}⁻²⁴ cm²": "这个方块：{#} 靶恩 = {#}⁻²⁴ cm²",
  "σ: the target area at each energy": "σ：各能量下的靶面积",
  "σ ≈ {#} b · reacted {#} % · passed through {#} %": "σ ≈ {#} b · 反应 {#} % · 穿过 {#} %",
  "each falling dot is a neutron: an orange flash means it hit a disc and reacted, a fading dot passed through": "每个落下的圆点是一个中子：橙色闪光表示击中圆盘并反应，渐隐的圆点表示穿过",
});
