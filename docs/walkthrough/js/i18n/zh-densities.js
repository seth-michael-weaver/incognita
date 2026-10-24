/* Simplified Chinese (简体中文): densities (chapter 15, 能级密度的拼接) */
WT.L.ch.densities = {
  num: "第 15 章", title: "能级密度的拼接", short: "能级密度",
  lead: "第 5 章把一块笔直的木板接到一片山坡上。本章把两者都写成公式，说明接点如何由计数的能级确定，以及接点不存在时会发生什么。",
  html: `
<div class="step">
  <h3>壳效应逐渐衰减的费米气体</h3>
  <p>引擎默认的能级密度 ldmodel 1 是 <b>Gilbert–Cameron</b> 复合公式：高能处为费米气体，低能处为恒温公式。费米气体只需要一个数，即能级密度参数 <i>a</i>，而在低能时这个数会感受到壳层。<b>Ignatyuk</b> 的形式让壳修正 δW 在低激发时充分起作用，并以阻尼速率 γ 逐渐消失，使原子核足够热时 <i>a</i>(<i>U</i>) 趋于平滑值 <i>ã</i>。</p>
  <div class="formula">a(U) = ã [1 + δW (1 − e<sup>−γU</sup>) / U] ,  ã = αA + βA<sup>2/3</sup> ,  γ = γ₁ / A<sup>1/3</sup></div>
  <div class="ctl"><label for="ld-dw">壳修正 δW (MeV)</label><input id="ld-dw" type="range" data-bind="dW" min="-6" max="4" step="0.1" value="1"><output data-show="dW" data-fmt="1"></output></div>
  <div class="formula">ρ<sub>F</sub>(E) = exp(2√(aU)) / (12√2 σ a<sup>1/4</sup> U<sup>5/4</sup>) ,  U = E − Δ ,  σ² = 0.01389 A<sup>5/3</sup> √(aU) / ã</div>
  <p>上方的曲线是若干 δW 下的 <i>a</i>(<i>U</i>)/<i>ã</i>，你设定的那条用粗线表示。下方是 ln ρ<sub>F</sub>。负的 δW（闭壳层）使密度降低一到两个数量级，而且这种压低消退得很慢：<i>a</i>(<i>U</i>) 按 δW/<i>U</i> 回到 <i>ã</i>，所以即使在 20 MeV，−6 MeV 的 δW 仍使密度降低约 40 倍。Δ 是对能修正，每一种配对的核子贡献 12/√A。</p>
</div>
<div class="step">
  <h3>下方的一条切线</h3>
  <p>在匹配能 <i>E<sub>x</sub></i> 以下，费米气体被<b>恒温</b>公式取代。两个条件确定它的两个参数：在 <i>E<sub>x</sub></i> 处数值相等、斜率相等，所以这条直线就是 ln ρ<sub>F</sub> 在该处的切线。</p>
  <div class="formula">ρ<sub>T</sub>(E) = (1/T) e<sup>(E − E₀)/T</sup> ,  1/T = d ln ρ<sub>F</sub>/dE |<sub>E<sub>x</sub></sub> ,  E₀ = E<sub>x</sub> − T ln[T ρ<sub>F</sub>(E<sub>x</sub>)]</div>
  <div class="ctl"><label for="ld-ex">匹配能 Eₓ (MeV)</label><input id="ld-ex" type="range" data-bind="Ex" min="4.6" max="14" step="0.05" value="7"><output data-show="Ex" data-fmt="2"></output></div>
  <p>滑动 <i>E<sub>x</sub></i>，切线随之转动：接点越高，<i>T</i> 越高（直线越平），<i>E</i>₀ 越低。任何 <i>E<sub>x</sub></i> 都给出一条光滑的曲线。哪一条正确，由计数的能级决定。</p>
</div>
<div class="step">
  <h3>由计数的能级寻找接点</h3>
  <p>阶梯是 <i>E</i> 以下已知能级的数目，采用对数坐标。恒温公式积分后是一条直线，<i>N</i>(<i>E</i>) = e<sup>(E − E₀)/T</sup> + 常数，它必须重现第 <i>N<sub>L</sub></i> 个能级到第 <i>N<sub>P</sub></i> 个能级之间的计数，即能级纲图中被认为完整的那一段。这是关于唯一未知数 <i>E<sub>x</sub></i> 的一个方程。</p>
  <div class="formula">F(E<sub>x</sub>) = e<sup>(E<sub>P</sub>−E₀)/T</sup> − e<sup>(E<sub>L</sub>−E₀)/T</sup> − (N<sub>P</sub> − N<sub>L</sub>) = 0</div>
  <div class="ctl"><label for="ld-ex2">试探 Eₓ (MeV)</label><input id="ld-ex2" type="range" data-bind="Ex" min="4.6" max="14" step="0.05" value="7"><output data-show="Ex" data-fmt="2"></output></div>
  <p>下方的面板是 <i>F</i>。引擎与 TALYS 一样，先把一个区段分成 100 步扫描，寻找符号变化，再用二分法求根；不断收窄的区间显示了二分过程。在 <i>F</i> = 0 处，试探直线正好落在阶梯上。</p>
</div>
<div class="step">
  <h3>没有接点的时候</h3>
  <p>对双闭壳原子核，低能处的费米气体被压低得如此厉害，以至于它的温度处处都很低，<i>F</i> 从不改变符号：不存在匹配能。这时 TALYS 取经验温度 <i>T</i> = −0.25 + 10.2/√(<i>A</i>(1 + γδW))，并寻找费米气体具有该温度的能量。在双闭壳附近，费米气体只有在远高于任何合理接点的地方才达到这个温度，或者根本达不到，所以接点也退回到系统学，<i>E<sub>x</sub></i> = 2.33 + 253/<i>A</i> + Δ，并确定 <i>E</i>₀ 使数值连续。</p>
  <div class="btns"><button class="btn ghost" data-act="tang" aria-pressed="false">在后备能量处取切线</button></div>
  <p>数值是连续的，但经验 <i>T</i> 并不是该能量处的费米气体温度，所以斜率发生跳变。在默认输入下，这种情况出现在 ²⁰⁵,²⁰⁶Tl、²⁰⁶⁻²⁰⁹Pb 和 ²¹⁰Bi，斜率跳变为 34% 到 62%；在那里改用费米气体的 <i>T</i>（TALYS 在输入中给定 <i>E<sub>x</sub></i> 时本来就这样做），就恢复了切线，并使铅区的俘获改变多达 20% 到 30%。INCOGNITA 在这里重现 TALYS 的做法；这一改动已报告给 TALYS 开发者。图中是一个类铅原子核的示意，其 <i>ã</i> 提高了 30%，使它的费米气体直到约 24 MeV（超出搜索范围）都低于经验温度；其斜率跳变 62%。</p>
</div>
<div class="step">
  <h3>用间距 D₀ 检验</h3>
  <p>在中子分离能处，密度可以直接测量：s 波共振的平均间距 <i>D</i>₀ 计数的是慢中子能够到达的那一个自旋和宇称的状态。对自旋为 0 的靶核，这只有 <i>J</i><sup>π</sup> = ½⁺。</p>
  <div class="formula">1/D₀ = ρ(S<sub>n</sub>, ½, +) = ½ ρ<sub>F</sub>(S<sub>n</sub>) · (2J+1)/(2σ²) · e<sup>−(J+½)²/2σ²</sup></div>
  <div class="ctl"><label for="ld-as">ã 的缩放因子</label><input id="ld-as" type="range" data-bind="as" min="0.8" max="1.2" step="0.005" value="1"><output data-show="as" data-fmt="3"></output></div>
  <p>图中是一个类铁-57 复合核，使用全局 <i>ã</i>，与实测值 25.4 ± 2.2 keV 比较。<i>ã</i> 改变百分之几，<i>D</i>₀ 就改变百分之几十；所以在 <i>D</i>₀ 已测量的地方，<i>S<sub>n</sub></i> 处的密度被牢牢确定，而在未测量的地方，它是俘获中最大的单项不确定度。评价工作会把 <i>a</i> 调整到 <i>D</i>₀，引擎所遵循的 TALYS 默认设置也是如此：对 <i>D</i>₀ 已测量的原子核，它读取针对该 <i>D</i>₀ 拟合的能级密度参数，只对其他原子核使用全局公式。</p>
  <div class="aside">代码位置：<code>density/parameters.py</code>（ã、Ignatyuk 阻尼、对能、自旋截断），<code>density/models.py</code>（费米气体、恒温、表格），<code>density/matching.py</code>（匹配方程的根、经验后备、重现 TALYS 自身的单精度细节）。图中使用 TALYS 对 ldmodel 1 的全局参数，配以示意性的能级纲图和壳修正（对类铅情形还取 <i>ã</i> × 1.3）；实测 <i>D</i>₀ 是 ⁵⁷Fe 的 RIPL 值。</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // axes
  "E (MeV)": "E (MeV)", "Eₓ (MeV)": "Eₓ (MeV)", "U (MeV)": "U (MeV)", "a(U) / ã": "a(U) / ã",
  "F = {#}": "F = {#}", "T = {#} MeV": "T = {#} MeV", "E₀ = {#} MeV": "E₀ = {#} MeV", "× e": "× e",
  // scene 1
  "U = {#} MeV · a = {#} MeV⁻¹ · T ≈ √(U/a) = {#} MeV": "U = {#} MeV · a = {#} MeV⁻¹ · T ≈ √(U/a) = {#} MeV",
  "ρ_F (states per MeV), A = {#}": "ρ_F（每 MeV 的状态数），A = {#}",
  "dashed: δW = {#}": "虚线：δW = {#}",
  "at {#} MeV: ×{#} against δW = {#}": "{#} MeV 处：×{#}（相对于 δW = {#}）",
  "at {#} MeV: ×{#}e{#} against δW = {#}": "{#} MeV 处：×{#}e{#}（相对于 δW = {#}）",
  // scene 2
  "joint Eₓ = {#} MeV": "接点 Eₓ = {#} MeV",
  "Fermi gas": "费米气体",
  "constant temperature": "恒温",
  "ln ρ (states per MeV), A = {#}": "ln ρ（每 MeV 的状态数），A = {#}",
  // scene 3
  "levels {#} to {#}: taken as complete": "第 {#} 至第 {#} 个能级：视为完整",
  "levels {#}–{#}": "能级 {#}–{#}",
  "number of levels below E": "E 以下的能级数",
  "trial Eₓ = {#} MeV: the line gives {#} levels for {#} counted": "试探 Eₓ = {#} MeV：直线给出 {#} 个能级，计数为 {#} 个",
  "F(Eₓ): predicted minus counted (signed log scale)": "F(Eₓ)：预言值减计数值（带符号的对数坐标）",
  "bisection step {#}: [{#}, {#}]": "二分第 {#} 步：[{#}, {#}]",
  "root Eₓ = {#} MeV": "根 Eₓ = {#} MeV",
  // scene 4
  "below: {#}/T with T = {#} MeV (Fermi-gas T)": "下方：{#}/T，T = {#} MeV（费米气体 T）",
  "below: {#}/T with T = {#} MeV (empirical T)": "下方：{#}/T，T = {#} MeV（经验 T）",
  "above: Fermi gas, T = {#} MeV": "上方：费米气体，T = {#} MeV",
  "slope jumps by {#} % at Eₓ = {#} MeV": "斜率跳变 {#} %，位于 Eₓ = {#} MeV",
  "tangent at Eₓ = {#} MeV: no jump": "Eₓ = {#} MeV 处相切：无跳变",
  "ln ρ, lead-like nucleus (A = {#}, δW = {#} MeV)": "ln ρ，类铅原子核（A = {#}，δW = {#} MeV）",
  "F changes sign: a root exists": "F 改变符号：存在根",
  "F(Eₓ) never reaches zero: no matching energy": "F(Eₓ) 始终不为零：没有匹配能",
  // scene 5
  "{#} keV": "{#} keV",
  "measured {#} ± {#} keV": "实测 {#} ± {#} keV",
  "computed D₀ = {#} keV": "计算 D₀ = {#} keV",
  "ã × {#} = {#} MeV⁻¹ · σ² = {#} · ρ(Sₙ) = {#} per MeV": "ã × {#} = {#} MeV⁻¹ · σ² = {#} · ρ(Sₙ) = 每 MeV {#} 个",
  "ã × {#} = {#} MeV⁻¹ · σ² = {#} · ρ(Sₙ) = {#}e{#} per MeV": "ã × {#} = {#} MeV⁻¹ · σ² = {#} · ρ(Sₙ) = 每 MeV {#}e{#} 个",
  "s-wave resonances above Sₙ, {#} keV shown: about {#} levels": "Sₙ 以上的 s 波共振，显示 {#} keV 范围：约 {#} 个能级",
  "iron{#}-like compound nucleus, Sₙ = {#} MeV, spin and parity ½⁺": "类铁{#} 复合核，Sₙ = {#} MeV，自旋宇称 ½⁺",
});
Object.assign(WT.L.glossary, {
  gilbertCameron: {
    term: "Gilbert–Cameron", aliases: ["Gilbert–Cameron"],
    short: "一种复合能级密度：低能处为恒温公式，在匹配能以上接到费米气体，接点处数值和斜率都相等。",
    more: "由 A. Gilbert 和 A. G. W. Cameron 于 1965 年提出。它是 TALYS 和本引擎的默认模型（ldmodel 1），配合 Ignatyuk 的能量依赖能级密度参数。",
    chapter: "densities",
  },
  ignatyuk: {
    term: "Ignatyuk", aliases: ["Ignatyuk"],
    short: "Ignatyuk 的能级密度参数形式：壳修正在低激发时充分起作用，并随能量衰减，使 a(U) 趋于其平滑值。",
    formula: "a(U) = ã [1 + δW (1 − e^(−γU)) / U]",
    chapter: "densities",
  },
});
