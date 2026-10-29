/* Simplified Chinese (简体中文): hauser (chapter 13, Hauser–Feshbach 逐道计算，含宽度涨落修正) */
WT.L.ch.hauser = {
  num: "第 22 章", title: "Hauser–Feshbach，逐道计算", short: "Hauser–Feshbach",
  lead: "第 9 章把各出口之间的竞争讲成一扇扇门。这里给出门背后的公式，一次一个道，以及只有少数几个道开放时它所需要的修正。",
  html: `
<div class="step">
  <h3>每个道一个穿透系数</h3>
  <p>一个<b>道</b>是一个完整的出口地址：哪种粒子，剩余核留在哪个状态，粒子的轨道角动量 <i>l</i> 和总角动量 <i>j</i> = <i>l</i> ± ½。第 5 章的光学模型给每个道一个<b>穿透系数</b> <i>T<sub>lj</sub></i>。图中的柱是入射中子的穿透系数，靶核自旋为 0。</p>
  <div class="ctl"><label for="hf-e">中子能量 (MeV)</label><input id="hf-e" type="range" data-bind="lgE" min="-3" max="0.7" step="0.01" value="-0.3"><output data-show="Eshow" data-fmt="3"></output></div>
  <p>在 1 keV 时只有 <i>l</i> = 0 开放，<i>T</i> ≈ 2π<i>S</i><sub>0</sub>√<i>E</i>，只有百分之几。在低能下，<i>l</i> 每增加一个单位，大约要付出 (<i>kR</i>)² 的因子，所以随着能量升高，柱子一根接一根地打开。每根柱以权重 g<sub>J</sub><i>T</i> 向复合核输送通量：</p>
  <div class="formula">σ<sub>CN</sub> = (π/k²) Σ<sub>J,π</sub> g<sub>J</sub> Σ<sub>lj</sub> T<sub>lj</sub> ,  g<sub>J</sub> = (2J+1) / [(2s+1)(2I+1)]</div>
</div>
<div class="step">
  <h3>一次一个自旋和宇称</h3>
  <p>角动量和宇称守恒，所以复合核在每个 <i>J</i><sup>π</sup> 中独立衰变。在一个块内，每个开放的出射道以各自的 <i>T</i> 参与竞争：弹性道回到基态；非弹性道到每个激发能级（一根柱把耦合到同一 <i>J</i> 的各个 (<i>l</i>, <i>j</i>) 加在一起）；3.6 MeV 以上的连续区，其每个能量区间按能级密度加权，算作许多个道；还有俘获，合并成一个极小的 <i>T</i><sub>γ</sub> = 2π⟨Γ<sub>γ</sub>⟩/<i>D</i>。高度采用对数坐标。</p>
  <div class="ctl"><label for="hf-j">自旋宇称块</label><input id="hf-j" type="range" data-bind="jb" min="0" max="9" step="1" value="2" data-instant><output data-show="jbShow" data-fmt="0"></output></div>
  <div class="ctl"><label for="hf-e2">中子能量 (MeV)</label><input id="hf-e2" type="range" data-bind="lgE" min="-3" max="0.7" step="0.01" value="-0.3"><output data-show="Eshow" data-fmt="3"></output></div>
  <p>底部的横条是 <b>Hauser–Feshbach</b> 分配：经道 <i>a</i> 进入的通量中，每个出口分得 <i>T<sub>b</sub></i>/Σ<i>T<sub>c</sub></i> 的份额。在 0.85 MeV 以下只有弹性和俘获开放，弹性几乎包揽一切。</p>
  <div class="formula">σ<sub>ab</sub> = (π/k²) Σ<sub>J,π</sub> g<sub>J</sub> T<sub>a</sub> T<sub>b</sub> / Σ<sub>c</sub> T<sub>c</sub> · W<sub>ab</sub></div>
</div>
<div class="step">
  <h3>宽度涨落</h3>
  <p>朴素公式会略微低估弹性散射，修正则把一小部分通量从其他出口移回弹性道。原因如下。</p>
  <p>当 <i>W<sub>ab</sub></i> = 1 时，公式乘的是平均值。平均值背后的共振，其宽度是涨落的（Porter–Thomas，第 15 章）；而对弹性散射，让中子进来的宽度正是让它出去的宽度，所以二者是关联的。于是对弹性道，乘积的平均大于平均的乘积，弹性道多得的部分由其他出口让出。</p>
  <div class="btns"><button class="btn ghost" data-act="w0" aria-pressed="false">不加修正</button><button class="btn ghost" data-act="w1" aria-pressed="true">Moldauer</button></div>
  <div class="ctl"><label for="hf-e3">中子能量 (MeV)</label><input id="hf-e3" type="range" data-bind="lgE" min="-3" max="0.7" step="0.01" value="-0.3"><output data-show="Eshow" data-fmt="3"></output></div>
  <p>标签给出有修正的 σ 除以无修正的 σ。在第一个非弹性阈以下，弹性已经拿走几乎全部通量，几乎不变，而俘获减少 10% 到 25%。在 1 到 1.5 MeV 之间，复合弹性增加 15% 到 35%，第一个 2⁺ 能级减少约三分之一。随着更多能级和连续区打开，复合弹性在通量中只占很小的份额：它自己的因子向 2 增大，但它从其他道拿走的部分变少，其他道的因子回到 1 附近。在 Moldauer 的方案中，每个道有一个自由度数 ν<sub>c</sub>，<i>W</i> 是一个一维积分，用 TALYS 的 32 点 Gauss–Laguerre 求积计算。</p>
  <div class="formula">W<sub>ab</sub> = (1 + 2δ<sub>ab</sub>/ν<sub>a</sub>) ∫₀^∞ dx Π<sub>c</sub> (1 + 2T<sub>c</sub>x / ν<sub>c</sub>ΣT)<sup>−(δ<sub>ac</sub>+δ<sub>bc</sub>+ν<sub>c</sub>/2)</sup></div>
  <div class="formula">ν<sub>c</sub> = 1.78 + (T<sub>c</sub><sup>1.212</sup> − 0.78) e<sup>−0.228 ΣT</sup></div>
</div>
<div class="step">
  <h3>Moldauer 与 HRTW</h3>
  <p>这些曲线在整个能区上做同样的计算：复合弹性、第一个 2⁺ 能级和俘获的比值，实线为 Moldauer，虚线为 <b>HRTW</b> 方案。HRTW 用一个弹性因子 <i>W<sub>a</sub></i> 和迭代求得的有效穿透系数 <i>V<sub>a</sub></i> 代替积分。</p>
  <div class="ctl"><label for="hf-e4">中子能量 (MeV)</label><input id="hf-e4" type="range" data-bind="lgE" min="-3" max="0.7" step="0.01" value="-0.3"><output data-show="Eshow" data-fmt="3"></output></div>
  <div class="formula">σ<sub>ab</sub> ∝ V<sub>a</sub>V<sub>b</sub> / ΣV<sub>c</sub> · [1 + δ<sub>ab</sub>(W<sub>a</sub> − 1)] ,  V<sub>a</sub> = T<sub>a</sub> / [1 + (W<sub>a</sub> − 1) V<sub>a</sub>/ΣV]</div>
  <p>对弹性和非弹性，两者符合得很好；对 keV 能区的俘获，HRTW 多减去最多 10%。在 0.85 到 2 MeV 之间，俘获甚至会增加：那里的总宽度由少数几个涨落的中子宽度主导，而 1/Γ 的平均大于 1/⟨Γ⟩。两种方案都是对精确随机矩阵（GOE）结果的拟合，TALYS 也以三重积分的形式提供这一精确结果。INCOGNITA 移植了全部三种（<code>widthmode</code> 1、2、3）；默认采用 Moldauer，用于能量不超过靶核中子分离能的入射中子。</p>
</div>
<div class="step">
  <h3>弹性增强的极限</h3>
  <p>弹性增强最大能有多大？介于 2 倍到 3 倍之间，取决于共振是彼此分开还是相互重叠。</p>
  <p>两个极限说明了这一效应的大小。取 <i>N</i> 个相同的道，不考虑俘获，改变它们的总和 ΣT，它等于 2π 乘以平均总宽度与能级间距之比 Γ/<i>D</i>。对孤立共振（ΣT ≪ 1）且道数很多时，每个宽度服从一个自由度的 Porter–Thomas 分布，弹性增强为 ⟨Γ<sub>a</sub>²⟩/⟨Γ<sub>a</sub>⟩² = 3。当共振强烈重叠（ΣT ≫ 2π）时，截面像随机波一样涨落（Ericson 涨落），增强降到 2。</p>
  <div class="ctl"><label for="hf-n">开放道数 N</label><input id="hf-n" type="range" data-bind="nch" min="2" max="60" step="1" value="30" data-instant><output data-show="nch" data-fmt="0"></output></div>
  <p>对 <i>N</i> 个孤立的道，精确值为 3<i>N</i>/(<i>N</i>+2)（菱形）：只有两个道时，增强不能超过 1.5，因为这时总宽度的涨落与弹性宽度一样大。Moldauer 的方案重现了这一极限；当开放的弱道很多时，HRTW 达不到它。插图按移动点对应的宽度画出共振。在 Moldauer 公式中，多道极限为 1 + 2/ν：孤立共振时 ν → 1，共振重叠时 ν → 1.78。这在完全重叠时给出 2.12 而不是 2：是该拟合的一个小误差。</p>
  <div class="aside">代码位置：<code>compound/prepare.py</code>（每个 <i>J</i><sup>π</sup> 的出射道及其穿透系数），<code>compound/target.py</code>（Hauser–Feshbach 求和），<code>compound/wfc.py</code>（Moldauer、HRTW 和 GOE，移植自 TALYS）。图中用示意性的输入计算同样的公式：类铁靶核的硬球穿透系数、七个能级、一个恒温连续区，以及一个合并的俘获道。</div>
</div>`,
};
(function () {
  const L = {
    // scene 1: incident T_lj
    "T = {#}": "T = {#}",
    "l={#}": "l={#}",
    "hollow: j = l − ½ · solid: j = l + ½": "空心：j = l − ½ · 实心：j = l + ½",
    "compound nucleus": "复合核",
    "compound nucleus · σ(CN) ≈ {#} b": "复合核 · σ(CN) ≈ {#} b",
    "σ(CN) ≈ {#} b": "σ(CN) ≈ {#} b",
    "E = {#} MeV · kR = {#}": "E = {#} MeV · kR = {#}",
    "E = {#} keV · kR = {#}": "E = {#} keV · kR = {#}",
    "transmission Tₗⱼ of the incident neutron": "入射中子的穿透系数 Tₗⱼ",
    // scene 2: one J^pi block
    "elastic": "弹性", "cont.": "连续区", "γ": "γ",
    "level energy (MeV) under each column": "柱下为能级能量 (MeV)",
    "residual level (energy in MeV) · n×: number of (l, j) channels summed": "剩余核能级（能量，MeV）· n×：求和的 (l, j) 道数",
    "{#}/{#}⁺ block · in through l = {#}, Tₐ = {#}": "{#}/{#}⁺ 块 · 经 l = {#} 进入，Tₐ = {#}",
    "{#}/{#}⁻ block · in through l = {#}, Tₐ = {#}": "{#}/{#}⁻ 块 · 经 l = {#} 进入，Tₐ = {#}",
    "elastic {#} %": "弹性 {#} %", "higher {#} %": "更高能级 {#} %",
    "{#}⁺ {#} %": "{#}⁺ {#} %", "γ {#} %": "γ {#} %", "{#}×": "{#}×",
    "Hauser–Feshbach split: T / ΣT for each exit": "Hauser–Feshbach 分配：各出口的 T / ΣT",
    // scene 3: HF vs WFC
    "closed": "关闭",
    "compound elastic": "复合弹性", "first {#}⁺ level": "第一个 {#}⁺ 能级",
    "higher levels": "更高能级", "capture": "俘获",
    "{#} mb": "{#} mb", "×{#}": "×{#}",
    "with Moldauer's correction": "含 Moldauer 修正",
    "Hauser–Feshbach without correction": "不加修正的 Hauser–Feshbach",
    "compound formation {#} mb at {#} MeV": "复合核形成 {#} mb，{#} MeV",
    "compound formation {#} mb at {#} keV": "复合核形成 {#} mb，{#} keV",
    // scene 4: ratio curves
    "{#} keV": "{#} keV", "{#} MeV": "{#} MeV",
    "{#}⁺ opens": "{#}⁺ 打开", "continuum": "连续区", "continuum opens": "连续区打开",
    "elastic ×{#} (Moldauer) · ×{#} (HRTW)": "弹性 ×{#} (Moldauer) · ×{#} (HRTW)",
    "capture ×{#} (Moldauer) · ×{#} (HRTW)": "俘获 ×{#} (Moldauer) · ×{#} (HRTW)",
    "first {#}⁺ ×{#} (Moldauer) · ×{#} (HRTW)": "第一个 {#}⁺ ×{#} (Moldauer) · ×{#} (HRTW)",
    "solid: Moldauer · dashed: HRTW": "实线：Moldauer · 虚线：HRTW",
    "σ with correction / σ without": "有修正的 σ / 无修正的 σ",
    // scene 5: limits
    "ΣT = {#}πΓ/D →": "ΣT = {#}πΓ/D →",
    "elastic enhancement Wₐₐ": "弹性增强 Wₐₐ",
    "T → {#} per channel": "每个道 T → {#}",
    "exact, isolated: {#}N/(N+{#}) = {#}": "精确值（孤立）：{#}N/(N+{#}) = {#}",
    "Porter–Thomas: {#}": "Porter–Thomas：{#}",
    "Ericson: {#}": "Ericson：{#}",
    "{#} channels · ΣT = {#} · Wₐₐ = {#}": "{#} 个道 · ΣT = {#} · Wₐₐ = {#}",
    "isolated resonances: Γ ≪ D": "孤立共振：Γ ≪ D",
    "resonances begin to overlap": "共振开始重叠",
    "strongly overlapping: Γ ≫ D": "强烈重叠：Γ ≫ D",
  };
  Object.assign(WT.L.labels, L);
})();
Object.assign(WT.L.glossary, {
  hrtw: {
    term: "HRTW", aliases: ["HRTW"],
    short: "Hofmann、Richert、Tepel 和 Weidenmüller 提出的宽度涨落修正方案：每个道一个弹性因子，有效穿透系数通过迭代求得。",
    more: "它与 Moldauer 的方案一样，是对随机矩阵数值计算的拟合。TALYS 以 widthmode 2 提供它；默认是 Moldauer (1)，精确的 GOE 三重积分 (3) 作为参照。",
    chapter: "hauser",
  },
  ericson: {
    term: "Ericson 涨落", aliases: ["Ericson 涨落"],
    short: "许多共振重叠时，截面随能量发生的随机涨落，其能量尺度由共振的平均总宽度决定。",
    more: "它是强重叠极限下的同一种统计规律；在孤立共振情形，这种统计给出 Porter–Thomas 宽度。在强重叠极限下，弹性增强因子趋于 2。",
    chapter: "hauser",
  },
});
/* attributes referenced in the English chapter script (for the structure check): data-act="w0" data-act="w1" data-show="jbShow" */
