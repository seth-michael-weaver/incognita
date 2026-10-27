/* Simplified Chinese (简体中文): averages (chapter 18, 从共振到平均) */
WT.L.ch.averages = {
  num: "第 27 章", title: "从共振到平均", short: "共振到平均",
  lead: "第 15 章画出了共振序列。这里把它们变成截面：R 矩阵公式、参数背后的统计规律、温度的影响，以及对许多共振的平均如何变成 Hauser–Feshbach。",
  html: `
<div class="step">
  <h3>R 矩阵，逐个能级</h3>
  <p>在重核中，几 keV 以下每个复合核能级都单独显现，截面可以用能级参数精确写出：能量 <i>E</i><sub>λ</sub>、约化中子宽度和俘获宽度。评价工作使用 <b>R 矩阵</b>理论，最常用的是 <b>Reich–Moore</b> 形式，它保留中子道中能级之间的干涉，并把众多俘获道当作一个吸收宽度处理。</p>
  <div class="formula">R(E) = Σ<sub>λ</sub> γ<sub>λ</sub>² / (E<sub>λ</sub> − E − iΓ<sub>λγ</sub>/2) ,  U = e<sup>−2iφ</sup> (1 + iPR) / (1 − iPR)</div>
  <div class="formula">σ<sub>tot</sub> = (2π/k²) g (1 − Re U) ,  σ<sub>γ</sub> = (π/k²) g (1 − |U|²)</div>
  <div class="btns"><button class="btn ghost" data-act="rm" aria-pressed="true">Reich–Moore</button><button class="btn ghost" data-act="bw" aria-pressed="false">单能级 Breit–Wigner</button></div>
  <p>上面的线是总截面，下面的线是俘获，对应自旋为 0 的类铀-238 靶核上的一个 s 波能级序列。在能级之间，共振振幅与势散射振幅相消的地方，总截面降到势散射以下。单能级形式把各能级的截面相加，而不是把振幅相加；它在峰上很接近，在谷中却是错的，那里许多能级的尾部叠加起来，总截面甚至可能变为负值。</p>
</div>
<div class="step">
  <h3>参数背后的统计规律</h3>
  <p>未经测量的原子核没有共振序列，只有平均值：<i>D</i>₀、强度函数 <i>S</i>₀ = ⟨Γ<sub>n</sub>⁰⟩/<i>D</i>₀ 和 ⟨Γ<sub>γ</sub>⟩。其余由随机矩阵理论给出：同一自旋宇称的能级间距服从 Wigner 间距分布，约化中子宽度服从 Porter–Thomas 分布，即一个自由度的 χ² 分布。</p>
  <div class="formula">P(s) = (πs/2) e<sup>−πs²/4</sup> ,  P(y) = e<sup>−y/2</sup> / √(2πy) ,  s = 间距/D₀, y = Γ<sub>n</sub>⁰/⟨Γ<sub>n</sub>⁰⟩</div>
  <div class="btns"><button class="btn" data-act="more">再抽取十个序列</button></div>
  <p>直方图收集了迄今抽取的每个序列的间距和宽度；曲线是这两条规律。俘获宽度是数百个光子道之和，几乎不涨落，所以取为固定值。</p>
</div>
<div class="step">
  <h3>热使峰变模糊</h3>
  <p>靶核在运动。能量为 <i>E</i> 的中子与它们相遇时，相对能量有一个宽度为 Δ = √(4<i>E</i> <i>kT</i>/<i>A</i>) 的分布，每个共振都透过这一分布被看到：这就是<b>多普勒展宽</b>。对单个能级，结果是 ψ 函数，即洛伦兹函数与高斯函数的卷积。</p>
  <div class="formula">σ<sub>γ</sub>(E,T) = σ₀ (Γ<sub>γ</sub>/Γ) ψ(x, ξ) ,  x = 2(E − E<sub>λ</sub>)/Γ ,  ξ = Γ/Δ</div>
  <div class="ctl"><label for="av-t">温度 (K)</label><input id="av-t" type="range" data-bind="TK" min="0" max="3000" step="10" value="300"><output data-show="TK" data-fmt="0"></output></div>
  <p>放大的共振是序列最低几个共振中最强的一个；虚线是它在 0 K 时的形状。加热使峰值降低、两翼变宽，而俘获峰下的面积保持不变。在厚样品中，这并不是中性的：峰被自屏蔽，两翼则没有，所以更热的燃料俘获更多。这就是反应堆的多普勒反馈。</p>
</div>
<div class="step">
  <h3>平均就是 Hauser–Feshbach</h3>
  <p>对许多共振平均后，俘获变成能量的光滑函数。窗口在序列上滑动，边走边画出它的平均值；光滑的线是 Hauser–Feshbach 值，穿透系数为 <i>T<sub>n</sub></i> = 2π⟨Γ<sub>n</sub>⟩/<i>D</i> 和 <i>T<sub>γ</sub></i> = 2π⟨Γ<sub>γ</sub>⟩/<i>D</i>。</p>
  <div class="ctl"><label for="av-w">窗口宽度（能级数）</label><input id="av-w" type="range" data-bind="win" min="2" max="40" step="1" value="12" data-instant><output data-show="win" data-fmt="0"></output></div>
  <div class="btns"><button class="btn ghost" data-act="ladder">换一个序列</button></div>
  <p>窄窗口分散得很大：只有少数几个共振，宽度服从 Porter–Thomas 分布。宽窗口则稳定在下面那条线上，即含宽度涨落修正的线。上面那条线是平均的乘积，在这里偏高 25% 到 47%，在 ⟨Γ<sub>n</sub>⟩ 为 ⟨Γ<sub>γ</sub>⟩ 的一到三倍的地方（约 100 eV 到 1 keV）偏高最多。（有 p 波和更多开放道时，修正较小。）对于一个中子道、Porter–Thomas 宽度和固定的俘获宽度，修正后的值是精确的：(2π²/k²<i>D</i>) <i>g</i> ⟨Γ<sub>n</sub>Γ<sub>γ</sub>/Γ⟩。</p>
</div>
<div class="step">
  <h3>可分辨、不可分辨、光滑</h3>
  <p>一次测量能分辨什么，取决于它的能量分辨率，而分辨率随能量升高而变差。图中的线是仪器所看到的截面，经过按 <i>E</i><sup>3/2</sup> 增长的分辨率展宽，就像飞行时间测量那样。在低能处每个能级都单独存在，其参数可以拟合：这是可分辨共振区。再往上，能级融合成一条涨落的带，其统计规律已知，但单个峰无法分辨：这是不可分辨共振区，用平均参数描述，对自屏蔽则用由抽样共振序列构建的概率表描述。再往上，由 Hauser–Feshbach 和光学模型接手。</p>
  <div class="ctl"><label for="av-r">仪器分辨率（相对值）</label><input id="av-r" type="range" data-bind="res" min="0.2" max="3" step="0.05" value="1"><output data-show="res" data-fmt="2"></output></div>
  <p>INCOGNITA 的数据库目前还没有可分辨共振区。它的曲线一直到最低能量都是 Hauser–Feshbach 平均值；在实测共振已被分辨的地方，<a href="data.html" data-keep-lang>全部核素</a>页面把曲线标为平均值。共振参数，以及由它们构建的经多普勒展宽的逐点截面，正在开发中。</p>
  <div class="aside">代码位置：<code>physics/resonance/ladder.py</code>（随机矩阵间距、Porter–Thomas 宽度、单能级截面、系综），<code>ladder_statistics.py</code>（用实测共振序列检验这些规律），<code>compound/wfc.py</code>（平均值所趋向的宽度涨落修正）。图中的 Reich–Moore、ψ–χ 和分辨率公式在此处计算，所用参数是示意性的类铀-238 参数；Hauser–Feshbach 引擎，因而数据库，目前还不计算共振区截面。</div>
</div>`,
};
(function () {
  const L = {
    // axes
    "{#} eV": "{#} eV", "{#} keV": "{#} keV", "{#} b": "{#} b",
    "{#}⁻¹ b": "{#}⁻¹ b", "{#}¹ b": "{#}¹ b", "{#}² b": "{#}² b", "{#}³ b": "{#}³ b", "{#}⁴ b": "{#}⁴ b",
    // scene 1
    "potential scattering {#}πR′² ≈ {#} b": "势散射 {#}πR′² ≈ {#} b",
    "Reich–Moore (dashed: single-level)": "Reich–Moore（虚线：单能级）",
    "single-level Breit–Wigner (dashed: Reich–Moore)": "单能级 Breit–Wigner（虚线：Reich–Moore）",
    "total": "总截面", "capture": "俘获",
    // scene 2
    "spacings: Wigner": "间距：Wigner",
    "s = spacing / D₀": "s = 间距 / D₀",
    "reduced neutron widths: Porter–Thomas": "约化中子宽度：Porter–Thomas",
    "y = Γn⁰ / ⟨Γn⁰⟩": "y = Γn⁰ / ⟨Γn⁰⟩",
    "{#} ladders · {#} spacings": "{#} 个序列 · {#} 个间距",
    "s = {#}": "s = {#}",
    // scene 3
    "capture near the {#} eV resonance": "{#} eV 共振附近的俘获",
    "area {#} b·eV ({#} K: {#})": "面积 {#} b·eV（{#} K：{#}）",
    "target nuclei at {#} K": "靶核温度 {#} K",
    "target nuclei at rest": "靶核静止",
    // scene 4
    "Hauser–Feshbach, no correction": "Hauser–Feshbach，不加修正",
    "with width fluctuations": "含宽度涨落",
    "average capture cross section": "平均俘获截面",
    "{#} levels around {#} eV: {#} b · HF {#} b without, {#} b with the correction": "{#} 个能级（{#} eV 附近）：{#} b · HF 无修正 {#} b，有修正 {#} b",
    // scene 5
    "resolved": "可分辨", "unresolved": "不可分辨", "averaged": "平均",
    "capture as measured with finite resolution · dashed: Hauser–Feshbach with fluctuations": "以有限分辨率测得的俘获 · 虚线：含涨落的 Hauser–Feshbach",
    "resolution reaches D₀/{#} at {#} eV": "分辨率达到 D₀/{#}：{#} eV 处",
    "resolution reaches D₀/{#} at {#} keV": "分辨率达到 D₀/{#}：{#} keV 处",
    "time of flight: the arrival time measures the energy": "飞行时间：到达时刻给出能量",
  };
  // labels that carry cross sections printed as "12 b" or "3.4k b" (each value independently)
  const B = ["{#} b", "{#}k b"];
  for (const a of B) for (const b of B) {
    L[`{#} eV · total ${a} · capture ${b}`] = `{#} eV · 总截面 ${a} · 俘获 ${b}`;
    L[`Γ = {#} meV · Δ = {#} meV · peak ${a} ({#} K: ${b})`] = `Γ = {#} meV · Δ = {#} meV · 峰值 ${a}（{#} K：${b}）`;
  }
  L["{#}k b"] = "{#}k b";
  Object.assign(WT.L.labels, L);
})();
Object.assign(WT.L.glossary, {
  rMatrix: {
    term: "R 矩阵理论", aliases: ["R 矩阵"],
    short: "用道半径内的能级能量和约化宽度精确描述共振反应、并在道半径外与自由波匹配的理论。",
    more: "评价工作把它的参数拟合到实测共振。单能级和多能级 Breit–Wigner 以及 Reich–Moore 形式都是对完整理论的近似。",
    chapter: "averages",
  },
  reichMoore: {
    term: "Reich–Moore", aliases: ["Reich–Moore"],
    short: "大多数重核评价中采用的 R 矩阵近似：中子道精确处理，众多光子道则按每个能级一个吸收宽度处理。",
    chapter: "averages",
  },
  doppler: {
    term: "多普勒展宽", aliases: ["多普勒展宽"],
    short: "靶核热运动对共振的抹平作用：峰值降低、两翼变宽，而孤立峰的面积保持不变。",
    formula: "Δ = √(4 E kT / A)",
    chapter: "averages",
  },
  resolvedRegion: {
    term: "可分辨与不可分辨共振区", aliases: ["可分辨共振区", "不可分辨共振区"],
    short: "在某一能量以下，每个共振都单独测得（可分辨）；在其上，只知道它们的平均参数（不可分辨），直到平均值变得光滑。",
    more: "在不可分辨共振区，自屏蔽用概率表处理，即由抽样共振序列构建的截面分布。",
    chapter: "averages",
  },
});
