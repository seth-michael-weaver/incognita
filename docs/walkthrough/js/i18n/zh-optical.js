/* Simplified Chinese (简体中文): optical (chapter 14, 光学模型的求解) */
WT.L.ch.optical = {
  num: "第 14 章", title: "求解光学模型", short: "光学模型求解",
  lead: "第 2 章把光学势画成一个半透明的玻璃球。这里展示引擎实际使用它的方式：一套全局参数化，一个逐步积分的径向薛定谔方程，以及把波转化为穿透系数的匹配条件。",
  html: `
<div class="step">
  <h3>Koning–Delaroche 势</h3>
  <p>对球形靶核上的中子和质子，默认采用 <b>Koning–Delaroche</b> 势（KD03）：Woods–Saxon 形状，其深度随能量以及靶核的质量和中子过剩平滑变化，取自全局公式；对于 KD03 逐个拟合过的原子核（如铁-56），则取自同一形式的局部拟合。图中对中子入射铁-56 使用全局公式。实部势阱（蓝色）起束缚作用；虚部（红色）起吸收作用，既在体内吸收，也在表面的一个薄壳层中吸收，低能时主要是后者。</p>
  <div class="ctl"><label for="op-e">中子能量 (MeV)</label><input id="op-e" type="range" data-bind="E" min="0.1" max="80" step="0.1" value="5"><output data-show="E" data-fmt="1"></output></div>
  <div class="formula">U(r) = −V<sub>V</sub> f(r) − iW<sub>V</sub> f(r) + 4i a<sub>D</sub>W<sub>D</sub> df<sub>D</sub>/dr + 2(V<sub>so</sub> + iW<sub>so</sub>) (1/r) df<sub>so</sub>/dr ⟨l·σ⟩</div>
  <p>探测中子以你设定的能量穿过，在吸收起作用的地方逐渐消失：它们的平均自由程为 ħ<i>v</i>/2|<i>W</i>|。每个深度都是 <i>E</i> − <i>E</i><sub>F</sub> 的函数，即从费米能算起：实部深度缓慢下降，面吸收 <i>W</i><sub>D</sub> 在 10 MeV 附近达到峰值，体吸收 <i>W</i><sub>V</sub> 持续增长，直到占据主导，在这里是约 45 MeV 以上。</p>
</div>
<div class="step">
  <h3>积分径向方程</h3>
  <p>每个分波满足各自的径向方程。引擎用 <b>Numerov 方法</b>从 <i>r</i> = 0 向外积分，穿过完整的复势；这是一种三点格式，精度达到步长的六次方。</p>
  <div class="formula">u″<sub>lj</sub>(r) = [ l(l+1)/r² + (2μ/ħ²) U<sub>lj</sub>(r) − k² ] u<sub>lj</sub>(r)</div>
  <div class="ctl"><label for="op-l">分波 l</label><input id="op-l" type="range" data-bind="L" min="0" max="10" step="1" value="1" data-instant><output data-show="L" data-fmt="0"></output></div>
  <div class="ctl"><label for="op-e2">中子能量 (MeV)</label><input id="op-e2" type="range" data-bind="E" min="0.1" max="80" step="0.1" value="5"><output data-show="E" data-fmt="1"></output></div>
  <p>实线是随时间变化的波 Re[<i>u</i> e<sup>−iωt</sup>]；虚线是自由波，即原子核不存在时的样子。在势阱内，波长变短（中子更快），振幅变小（被吸收）；在外面，它带着相移回来。</p>
</div>
<div class="step">
  <h3>从波到 S 和 T</h3>
  <p>在约 12 fm 以外，势已经消失，波必然是入射自由波与出射自由波的混合，<i>u</i> ∝ <i>H</i><sup>−</sup> − <i>S</i> <i>H</i><sup>+</sup>。在两个半径处与积分得到的 <i>u</i> 匹配，就确定了 <b>S 矩阵</b>元 <i>S<sub>lj</sub></i>：带相位的出射波振幅。</p>
  <div class="btns"><button class="btn ghost" data-act="abs" aria-pressed="false">关闭吸收</button></div>
  <div class="formula">S<sub>lj</sub> = η<sub>lj</sub> e<sup>2iδ<sub>lj</sub></sup> ,  T<sub>lj</sub> = 1 − |S<sub>lj</sub>|²</div>
  <p>圆点是复平面上的 <i>S</i>，位于单位圆内；它的轨迹是能量从 0.1 扫到 40 MeV 时走过的路径。没有吸收时 |<i>S</i>| = 1：圆点沿圆周运动，波只改变相位，<i>T</i> = 0。圆点到圆周的距离，就是复合核以及所有其他反应所得到的部分。</p>
</div>
<div class="step">
  <h3>自旋–轨道使 j 分裂</h3>
  <p><b>自旋–轨道</b>项对 <i>j</i> = <i>l</i> + ½ 是吸引的，对 <i>j</i> = <i>l</i> − ½ 是排斥的。它很小，在表面处只有几 MeV，但它把每个 <i>l</i> 的两个穿透系数分开，在擦过表面的那个分波附近分开得最多。</p>
  <div class="ctl"><label for="op-e3">中子能量 (MeV)</label><input id="op-e3" type="range" data-bind="E" min="0.1" max="80" step="0.1" value="5"><output data-show="E" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="so" aria-pressed="false">关闭自旋–轨道</button></div>
  <p>Hauser–Feshbach（第 13 章）分别使用这两个穿透系数；按权重求和，(<i>l</i>+1)<i>T</i><sub>l,l+½</sub> + <i>l</i> <i>T</i><sub>l,l−½</sub>，得到的反应截面几乎不变。这就是为什么总截面几乎不能约束自旋–轨道强度，而需要极化数据。</p>
</div>
<div class="step">
  <h3>截面</h3>
  <p>对分波求和，就得到用来拟合光学势的可观测量。反应截面计入被移走的通量，总截面由前向振幅得出，两者之差是形状弹性散射。</p>
  <div class="formula">σ<sub>R</sub> = (π/k²) Σ<sub>l</sub> [(l+1)T<sub>l,l+½</sub> + l T<sub>l,l−½</sub>] ,  σ<sub>tot</sub> = (2π/k²) Σ<sub>lj</sub> (j+½)(1 − Re S<sub>lj</sub>)</div>
  <div class="ctl"><label for="op-e4">中子能量 (MeV)</label><input id="op-e4" type="range" data-bind="E" min="0.2" max="50" step="0.1" value="5"><output data-show="E" data-fmt="1"></output></div>
  <p>KD03 针对许多原子核、从 1 keV 到 200 MeV 的这类数据进行了拟合；铁的总截面在几 MeV 时介于 3.5 到 4 b 之间，在 14 MeV 时为 2.5 b，无需针对这个原子核调整，就能在约 5% 以内得到，连宽阔的极大值也包括在内：它们反映的是原子核尺寸与中子波长的对比。</p>
</div>
<div class="step">
  <h3>低能端</h3>
  <p>在几 keV 以下只有 s 波起作用，<i>T</i><sub>0</sub> 按 √<i>E</i> 增长：在这张双对数图上斜率为二分之一。比例常数就是<b>强度函数</b> <i>S</i><sub>0</sub> = <i>T</i><sub>0</sub>/(2π√<i>E</i>)，<i>E</i> 以 eV 为单位；共振分析把同一个量测量为 Σ Γ<sub>n</sub><sup>0</sup>/Δ<i>E</i>。</p>
  <p>全局势主要在 MeV 能区拟合，低能端是它最薄弱的地方。对铁-56，这个势给出 <i>S</i><sub>0</sub> ≈ 5.5 × 10⁻⁴，局部 KD03 拟合给出的值也几乎相同，而测量值（RIPL）为 2.3 ± 0.6 × 10⁻⁴：铁位于 <i>A</i> ≈ 55 附近 3s 尺寸共振的峰值附近，那里的 <i>S</i><sub>0</sub> 对势最为敏感。这就是为什么实测的 <i>S</i><sub>0</sub> 和 <i>S</i><sub>1</sub> 是引擎一个单独的可选输入。</p>
  <div class="aside">代码位置：<code>omp/parameters.py</code>（KD03 及其他全局势），<code>omp/potential.py</code>（径向形状因子），<code>omp/schrodinger.py</code>（Numerov 积分与匹配，带电粒子的库仑函数用 Steed 方法计算；对球形靶核它取代 ECIS，并与 ECIS 的 T<sub>lj</sub> 对照检验），<code>ecis/</code>（用于形变靶核的耦合道移植），<code>omp/sfunc.py</code>（可选：实测 S₀、S₁）。图中自行求解该方程，采用非相对论运动学，对象是中子入射铁-56。</div>
</div>`,
};
(function () {
  const L = {
    // axes and units
    "{#} fm": "{#} fm", "{#} MeV": "{#} MeV", "{#} keV": "{#} keV", "{#} eV": "{#} eV", "{#} b": "{#} b",
    // scene 1: potential
    "real well, depth {#} MeV": "实部势阱，深度 {#} MeV",
    "surface absorption, peak {#} MeV": "面吸收，峰值 {#} MeV",
    "volume absorption {#} MeV": "体吸收 {#} MeV",
    "spin–orbit for l = {#}, j = {#}/{#}: {#} MeV": "l = {#}、j = {#}/{#} 的自旋–轨道：{#} MeV",
    "E = {#} MeV": "E = {#} MeV",
    "mean free path: {#} fm at the surface, {#} fm in the centre": "平均自由程：表面 {#} fm，中心 {#} fm",
    "mean free path: {#} fm at the surface, > {#} fm in the centre": "平均自由程：表面 {#} fm，中心 > {#} fm",
    "mean free path: > {#} fm at the surface, {#} fm in the centre": "平均自由程：表面 > {#} fm，中心 {#} fm",
    "mean free path: > {#} fm at the surface, > {#} fm in the centre": "平均自由程：表面 > {#} fm，中心 > {#} fm",
    "real": "实部", "volume": "体", "surface": "面",
    "depths (MeV) against energy (MeV)": "深度 (MeV) 随能量 (MeV) 的变化",
    // scene 2: wave
    "potential: real (blue), imaginary (red)": "势：实部（蓝），虚部（红）",
    "nuclear surface": "原子核表面",
    "l = {#}, j = {#}+½ · E = {#} MeV · |S| = {#} · δ = {#}° · T = {#}": "l = {#}, j = {#}+½ · E = {#} MeV · |S| = {#} · δ = {#}° · T = {#}",
    "solid: the wave now · shaded: its size |u| · dashed: free wave": "实线：此刻的波 · 阴影：其大小 |u| · 虚线：自由波",
    // scene 3: S-matrix
    "Re S": "Re S", "Im S": "Im S",
    "|S| = {#}: nothing absorbed": "|S| = {#}：无吸收",
    "l = {#}, j = {#}+½ · E = {#} MeV": "l = {#}, j = {#}+½ · E = {#} MeV",
    "|S| = {#} · T = {#} − |S|² = {#}": "|S| = {#} · T = {#} − |S|² = {#}",
    "l = {#}, j = {#}+½": "l = {#}, j = {#}+½",
    "|S| = {#}": "|S| = {#}",
    "T = {#} − |S|² = {#}": "T = {#} − |S|² = {#}",
    "trail: S as E runs {#} → {#} MeV": "轨迹：E 从 {#} → {#} MeV 时的 S",
    "no absorption: S stays on the circle": "无吸收：S 停留在圆周上",
    // scene 4: spin-orbit
    "T = {#}": "T = {#}", "l": "l",
    "hollow: j = l − ½ · solid: j = l + ½": "空心：j = l − ½ · 实心：j = l + ½",
    "hollow (purple): j = l − ½ · solid (blue): j = l + ½": "空心（紫）：j = l − ½ · 实心（蓝）：j = l + ½",
    "reaction cross section {#} b (without spin–orbit {#} b)": "反应截面 {#} b（无自旋–轨道时 {#} b）",
    "reaction cross section {#} b (spin–orbit off)": "反应截面 {#} b（自旋–轨道已关闭）",
    "grazing l ≈ kR = {#}": "擦边分波 l ≈ kR = {#}",
    // scene 5: cross sections
    "total {#} b": "总截面 {#} b",
    "reaction {#} b": "反应截面 {#} b",
    "shape elastic {#} b": "形状弹性 {#} b",
    "n + ⁵⁶Fe, KD{#}, computed here": "n + ⁵⁶Fe，KD{#}，在此计算",
    // scene 6: S0
    "T₀ (s-wave)": "T₀（s 波）",
    "T₁ (p-wave, j = {#}/{#}): slope {#}/{#}": "T₁（p 波，j = {#}/{#}）：斜率 {#}/{#}",
    "dashed: {#}πS₀√E, slope ½": "虚线：{#}πS₀√E，斜率 ½",
    "S₀ = {#} × {#}⁻⁴ from this potential": "此势给出 S₀ = {#} × {#}⁻⁴",
  };
  Object.assign(WT.L.labels, L);
})();
Object.assign(WT.L.glossary, {
  koningDelaroche: {
    term: "Koning–Delaroche 势", aliases: ["Koning–Delaroche", "KD03"],
    short: "A. J. Koning 和 J.-P. Delaroche（2003）给出的中子和质子全局光学势，适用于 1 keV 到 200 MeV、质量数 24 到 209。",
    more: "它的深度、半径和弥散度都是能量、质量和中子过剩的平滑函数，一次性拟合了大量实测截面和角分布。它是 TALYS 和本引擎中核子的默认光学势。",
    chapter: "optical",
  },
  numerov: {
    term: "Numerov 方法", aliases: ["Numerov 方法", "Numerov"],
    short: "一种积分不含一阶导数项的二阶方程（例如径向薛定谔方程）的三点格式，每步误差为 h⁶ 量级。",
    formula: "(1 − h²Q_n+1/12) u_n+1 = 2(1 + 5h²Q_n/12) u_n − (1 − h²Q_n−1/12) u_n−1",
    chapter: "optical",
  },
  sMatrix: {
    term: "S 矩阵", aliases: ["S 矩阵"],
    short: "联系入射波与出射波的振幅；对一个分波中的弹性散射，它就是一个复数 S = η e^(2iδ)。",
    more: "|S| = 1 表示没有任何吸收，只有相移 δ 改变；亏缺部分 1 − |S|² 就是穿透系数，即被反应带走的通量。",
    chapter: "optical",
  },
  spinOrbit: {
    term: "自旋–轨道项", aliases: ["自旋–轨道", "自旋-轨道"],
    short: "核势中取决于核子自旋与其轨道角动量平行还是反平行的那一部分。",
    more: "它对 j = l + ½ 是吸引的，对 j = l − ½ 是排斥的，峰值位于原子核表面。同一种相互作用产生了壳模型中的幻数。",
    chapter: "optical",
  },
});
