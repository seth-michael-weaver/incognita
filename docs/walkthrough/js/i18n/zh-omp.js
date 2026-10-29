/* Simplified Chinese: omp (第 5 章，光学模型) */
WT.L.ch.omp = {
  num: "第 5 章", title: "光学模型", short: "光学模型",
  lead: "在做任何其他事情之前，程序先问一个更简单的问题：在入射中子看来，原子核是什么样子？",
  html: `
<div class="step">
  <p>在量子力学中，中子也是一列波。图中一列波从左边滚滚而来，波峰显示为明亮的条纹，朝着一个原子核（虚线圆）前进。此时还没有任何东西作用于它，所以波峰径直穿了过去。</p>
  <div class="ctl"><label for="omp-e">中子能量 (MeV)</label><input id="omp-e" type="range" data-bind="E" min="0.2" max="40" step="0.1" value="8"><output data-show="E" data-fmt="1"></output></div>
  <p>拖动能量滑块，观察底部的波长，单位是飞米（fm，10⁻¹⁵ m）。慢中子的波很长：在约 9 MeV 以下，一个波长比整个原子核还宽。</p>
</div>
<div class="step">
  <h3>实部势：折射</h3>
  <p><b>光学势</b>是整个原子核作用在中子上的平均力。它的<em>实部</em>是一个约 50 MeV 深的势阱：中子进入后速度加快，所以波峰挤在一起。程序给它取 Woods–Saxon 形状：中心平坦而深，在表面平滑地降到零。</p>
</div>
<div class="step">
  <h3>虚部势：吸收</h3>
  <p>原子核后面的阴影，是因发生反应而损失的中子。势的<em>虚部</em>描述的正是它们：它不让波弯折，而是让波衰减，主要发生在表面附近（彩色圆环）。</p>
  <div class="ctl"><label for="omp-w">吸收 W (MeV)</label><input id="omp-w" type="range" data-bind="W" min="0" max="14" step="0.5" value="7"><output data-show="W" data-fmt="1"></output></div>
  <p>把 <i>W</i> 拖到 0，阴影就被填满了：没有吸收，就没有反应。光学模型的名字由此而来：原子核像一颗朦胧的玻璃球，一部分光被折射，一部分被吸收。</p>
</div>
<div class="step">
  <h3>分波与碰撞参数</h3>
  <p>迎面看去，靶被分成一圈圈圆环，每个环对应一个<b>分波</b> <i>l</i> = 0, 1, 2, … 在距中心 <i>b</i> 处经过的中子带有<b>角动量</b> <i>l</i> ≈ <i>k b</i>，其中 <i>k</i> 随能量增大。圆环颜色越深，它的<b>穿透系数</b> <i>T<sub>l</sub></i> 越大，即该环中的中子被吸收的概率越大。</p>
  <div class="ctl"><label for="omp-e3">中子能量 (MeV)</label><input id="omp-e3" type="range" data-bind="E" min="0.2" max="40" step="0.1" value="8"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="fire">发射 200 个中子</button></div>
  <p>橙色闪光表示被吸收的中子；柱条把每个环的吸收比例与模型的 <i>T<sub>l</sub></i>（刻度线）相比较。内环几乎全部吸收，外环则让中子通过。在低能时圆环很大，只有 <i>l</i> = 0 起作用。</p>
</div>
<div class="step">
  <h3>离心势垒</h3>
  <p>角动量很大的中子从太远处经过，碰不到原子核：这就是<b>离心势垒</b>。从上方看，这里每个中子都属于同一个分波 <i>l</i>，因此都在相同的<b>掠过距离</b> <i>b</i> ≈ (<i>l</i>+½)/<i>k</i>（虚线圆）处经过。</p>
  <p>但每个中子都是一列波，在大约一个约化波长 λ̄ 的范围内是模糊的（光晕）。即使路径偏离了原子核，模糊的边缘仍可能擦到表面而进入：这就是<b>隧穿效应</b>。</p>
  <div class="ctl"><label for="omp-l">分波 l</label><input id="omp-l" type="range" data-bind="L" min="0" max="8" step="1" value="3" data-instant><output data-show="L" data-fmt="0"></output></div>
  <div class="ctl"><label for="omp-e2">能量 (MeV)</label><input id="omp-e2" type="range" data-bind="E" min="0.2" max="40" step="0.1" value="8"><output data-show="E" data-fmt="1"></output></div>
  <p>增大 <i>l</i>，路径向外移：进入的中子变少。提高能量，同一个 <i>l</i> 从更近处经过，模糊也更小。程序通过在完整的势中求解薛定谔方程（量子力学的波动方程），精确地得到每个 <i>T<sub>l</sub></i>。它送进一列波，测量其中有多少未被吸收而重新出射：返回的波记作 <i>S</i>，它的平方 |<i>S</i>|² 就是返回的份额。没有返回的部分被原子核吸收了，这份缺失的份额就是 <i>T<sub>l</sub></i>。</p>
  <div class="formula">T<sub>lj</sub> = 1 − |S<sub>lj</sub>|²</div>
</div>
<div class="step">
  <h3>反应截面</h3>
  <p>右边的圆盘表示原子核在中子看来有多大：这就是<b>反应截面</b>，单位是靶恩（10⁻²⁴ cm²）。每个圆环贡献它的面积乘以 <i>T<sub>l</sub></i>。虚线圆是几何尺寸。</p>
  <div class="ctl"><label for="omp-e4">中子能量 (MeV)</label><input id="omp-e4" type="range" data-bind="E" min="0.2" max="40" step="0.1" value="8"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="sum">重新求和</button></div>
  <p>改变能量，求和会重新进行：低能时，一两个大圆环几乎构成整个圆盘；高能时，许多细环各添一小片，圆盘逐渐接近几何尺寸。</p>
  <div class="formula">σ<sub>R</sub> = (π/k²) Σ (2l+1) T<sub>l</sub></div>
  <p>这些 <i>T<sub>l</sub></i> 供给程序的其余部分：它们决定受激原子核的每个自旋态形成的频率；反过来用，又决定每种粒子重新出射的难易程度。</p>
  <div class="aside">代码位置：<code>omp/parameters.py</code>（Koning–Delaroche 全局势；锕系核的色散势），<code>omp/schrodinger.py</code>（Numerov 积分与库仑波函数匹配），<code>omp/inverse.py</code>（由细致平衡得到出射粒子），<code>omp/regional.py</code>（可选，默认关闭：针对形变稀土靶核的势阱区域性调整，拟合实测的 S₀ 和 S₁）。</div>
</div>`,
};
Object.assign(WT.L.labels, {
  "absorbing surface": "吸收表面",
  "shadow: neutrons lost to reactions": "阴影：因反应损失的中子",
  "wavelength {#} fm   ·   nucleus {#} fm across": "波长 {#} fm   ·   原子核直径 {#} fm",
  "crests crowd inside the well": "波峰在势阱内挤紧",
  "l={#}": "l={#}",
  "nuclear radius": "原子核半径",
  "reaction cross section ≈ {#} b": "反应截面 ≈ {#} b",
  "geometric size π(R+λ̄)² ≈ {#} b · darker ring = more absorbed · orange flash = absorbed": "几何尺寸 π(R+λ̄)² ≈ {#} b · 越深 = 吸收越多 · 橙色 = 被吸收",
  "absorbed, ring by ring": "逐环吸收情况",
  "bar: your neutrons · tick: model Tₗ": "柱：你的中子 · 刻度：模型 Tₗ",
  "rings: shade = Tₗ": "圆环：深浅 = Tₗ",
  "geometric size π(R+λ̄)²": "几何尺寸 π(R+λ̄)²",
  "reaction cross section": "反应截面",
  "ring l={#}: ({#}l+{#})·Tₗ·π/k² = +{#} b": "环 l={#}：({#}l+{#})·Tₗ·π/k² = +{#} b",
  "all {#} rings added": "{#} 个环全部加完",
  "σ_R = {#} b": "σ_R = {#} b",
  "geometric {#} b": "几何 {#} b",
  "geometric {#} b · darker = more absorbed · orange = absorbed": "几何 {#} b · 越深 = 吸收越多 · 橙色 = 被吸收",
  "swing distance b ≈ (l+½)/k = {#} fm": "掠过距离 b ≈ (l+½)/k = {#} fm",
  "nuclear radius R = {#} fm · wave fuzz λ̄ = {#} fm": "原子核半径 R = {#} fm · 波的模糊 λ̄ = {#} fm",
  "path crosses the nucleus: most get in": "路径穿过原子核：大多进入",
  "path misses the nucleus: only the fuzzy edge can tunnel in": "路径偏离原子核：只有模糊边缘能隧穿进入",
  "absorbed {#} of {#} · model Tₗ = {#}": "吸收 {#}/{#} · 模型 Tₗ = {#}",
});
