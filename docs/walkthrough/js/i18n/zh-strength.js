/* Simplified Chinese (简体中文): strength (chapter 16, 光子强度详解) */
WT.L.ch.strength = {
  num: "第 25 章", title: "光子强度详解", short: "光子强度",
  lead: "第 10 章展示了热的原子核偏爱哪些光子。本章写出强度函数，把它们一路推到穿透系数和平均辐射宽度，并运行由它们驱动的级联。",
  html: `
<div class="step">
  <h3>E1：巨偶极共振的尾部</h3>
  <p><b>光子强度函数</b> <i>f<sub>XL</sub></i>(<i>E</i><sub>γ</sub>) 是 <i>XL</i> 型光子的平均约化概率：电偶极 E1、磁偶极 M1，依此类推。对 E1，它由 18 MeV 附近的巨偶极共振主导，但 <i>S<sub>n</sub></i> 处的衰变用的是 1 到 7 MeV 的光子，远在其尾部，而尾部的形状正是全部问题所在。</p>
  <div class="formula">f<sub>E1</sub> = K σ₀Γ₀ · E<sub>γ</sub> Γ(E<sub>γ</sub>,T) / [(E<sub>γ</sub>² − E₀²)² + E<sub>γ</sub>² Γ(E<sub>γ</sub>,T)²] / (1 − e<sup>−E<sub>γ</sub>/T</sup>) ,  Γ(E<sub>γ</sub>,T) = (Γ₀/E₀)(E<sub>γ</sub> + 4π²T²/E₀)</div>
  <div class="ctl"><label for="ps-t">末态温度 T (MeV)</label><input id="ps-t" type="range" data-bind="T" min="0" max="1.5" step="0.01" value="0.7"><output data-show="T" data-fmt="2"></output></div>
  <p>虚线是标准洛伦兹型（SLO），即拟合光吸收数据得到的形状。由于宽度恒定，它在衰变窗口内把强度高估 2 到 5 倍，这是球形核上早已知道的失败。实线是简化修正洛伦兹型（<b>SMLO</b>）：它的宽度随光子能量和末态温度增大，这降低了窗口内的尾部，但在光子能量为零处留下有限的强度，正如衰变数据所要求的。把 <i>T</i> 拖到 0，这个低能下限就消失了。</p>
</div>
<div class="step">
  <h3>M1：自旋翻转、剪刀模式、低能上翘</h3>
  <p>M1 强度较弱，但不可忽略：41<i>A</i><sup>−1/3</sup> MeV 附近的自旋翻转共振，形变核中 3 MeV 附近的剪刀模式（强度按 β² 增长），以及低能上翘，即在 Oslo 方法数据和壳模型计算中看到的、向光子能量零点的上升。</p>
  <div class="ctl"><label for="ps-b">形变 β（剪刀模式）</label><input id="ps-b" type="range" data-bind="beta" min="0" max="0.35" step="0.01" value="0.2"><output data-show="beta" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="up" aria-pressed="true">低能上翘</button></div>
  <p>后面的浅色线是 E1。在最低的光子能量处，这里约 2 MeV 以下，低能上翘使 M1 可以与之相当甚至超过它（标记指出位置），所以它对级联的软端以及远离稳定线的俘获都很重要。引擎默认的 M1 是带低能上翘的 IAEA 推荐，逐核列表；默认的 E1 是列表形式的 SMLO-2019；这里的解析形式代替那些表格。</p>
</div>
<div class="step">
  <h3>Brink–Axel</h3>
  <p><b>Brink–Axel 假设</b>认为，强度取决于光子能量，而与原子核从哪里出发无关：同一个 <i>f</i> 既适用于 <i>S<sub>n</sub></i> 处的共振，也适用于 4 MeV 处的一个状态。（SMLO 通过 <i>T</i> 保留了一点弱的依赖。）于是每个起始能量的发射正比于穿透系数乘以末态密度。</p>
  <div class="formula">T<sub>XL</sub>(E<sub>γ</sub>) = 2π E<sub>γ</sub><sup>2L+1</sup> f<sub>XL</sub>(E<sub>γ</sub>) ,  dΓ/dE<sub>γ</sub> ∝ T<sub>XL</sub>(E<sub>γ</sub>) ρ(E<sub>x</sub> − E<sub>γ</sub>)</div>
  <div class="ctl"><label for="ps-x">起始能量 Eₓ (MeV)</label><input id="ps-x" type="range" data-bind="Ex" min="2" max="7.6" step="0.05" value="7.6"><output data-show="Ex" data-fmt="2"></output></div>
  <p>上升的 <i>E</i><sub>γ</sub>³<i>f</i> 与下降的 ρ 相乘，形成一个驼峰。从 <i>S<sub>n</sub></i> 出发，这里的峰值在 4 到 5 MeV 附近。从较低处出发，它在起始能量处被截断；在匹配能以下，ρ 是恒温指数函数，从每个起点出发的形状都一样，只是被截断。检验这一假设的方法是比较在不同激发能下提取的强度，Oslo 类分析正是这样做的。</p>
</div>
<div class="step">
  <h3>平均辐射宽度</h3>
  <p>对 s 波共振（自旋为 0 的靶核上 <i>J</i><sup>π</sup> = ½⁺）经 E1 或 M1 可达的所有末态求和，就得到它们的平均总光子宽度。它已由共振形状对几百个原子核测出，是检验 <i>S<sub>n</sub></i> 处强度的主要手段。</p>
  <div class="formula">⟨Γ<sub>γ</sub>⟩ = D₀/2π · Σ<sub>XL</sub> Σ<sub>J′π′</sub> ∫₀^{S<sub>n</sub>} T<sub>XL</sub>(E<sub>γ</sub>) ρ(S<sub>n</sub> − E<sub>γ</sub>, J′, π′) dE<sub>γ</sub></div>
  <div class="ctl"><label for="ps-s">强度的缩放因子</label><input id="ps-s" type="range" data-bind="scale" min="0.3" max="5" step="0.01" value="1"><output data-show="scale" data-fmt="2"></output></div>
  <p>曲线逐个光子地显示宽度来自哪里：主要是 3 到 7 MeV，且主要是 E1，M1 约贡献 15%。在这里，用解析形式和示意性的能级密度代替引擎的表格，得到的宽度只有实测值 0.92 eV 的约六分之一：宽度对 <i>S<sub>n</sub></i> 以下的能级密度和强度的尾部就是这么敏感。引擎所遵循的 TALYS 默认设置对这个原子核给出约 1.3 eV。滑块施加的就是评价工作会拟合的那个整体因子。当 Γ<sub>γ</sub> ≪ Γ<sub>n</sub> 时，keV 能区的俘获几乎正比于 ⟨Γ<sub>γ</sub>⟩，所以这里的一个因子就是 (n,γ) 中的一个因子。TALYS 可以把强度重新标定到实测 ⟨Γ<sub>γ</sub>⟩（<code>gnorm</code>）；在 INCOGNITA 中，这种对级联中每个原子核都施加的重新标定是一个可选开关，默认关闭。</p>
</div>
<div class="step">
  <h3>级联</h3>
  <p>第一个光子之后，同样的规则重复进行：从每个新的能量出发，下一个光子按 <i>T</i>(<i>E</i><sub>γ</sub>) ρ(<i>E<sub>x</sub></i> − <i>E</i><sub>γ</sub>) 抽取，直到原子核到达已知能级。每段历史只有几个光子；它们的总谱就是俘获后量能器看到的谱。</p>
  <div class="btns"><button class="btn ghost" data-act="up2" aria-pressed="true">低能上翘</button><button class="btn ghost" data-act="clear">重新开始</button></div>
  <p>低能上翘增加了软光子，也使多重数略有增加。引擎并不抽取历史：它自上而下、逐个能量区间地转移布居（第 11 章），这样得到同样的平均值，却没有抽样噪声。</p>
  <div class="aside">代码位置：<code>gamma/strength.py</code>（TALYS 支持的所有强度模型；默认为 SMLO-2019 表格和带低能上翘的 IAEA M1），<code>gamma/parameters.py</code>（巨共振系统学、表格），<code>gamma/transmission.py</code>（T = 2π E<sup>2L+1</sup> f），<code>gamma/ggnorm.py</code>（可选的 ⟨Γγ⟩ 归一化），<code>emission/</code>（级联）。图中对一个类铁-57 原子核使用解析形式和系统学；实测 ⟨Γγ⟩ 是 ⁵⁷Fe 的 RIPL 值。</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // scene 1: E1
  "E{#} strength f (MeV⁻³), A = {#}": "E{#} 强度 f (MeV⁻³)，A = {#}",
  "Eγ (MeV)": "Eγ (MeV)",
  "photons that decay uses": "衰变所用的光子",
  "GDR: E₀ = {#} MeV, Γ₀ = {#} MeV, σ₀ = {#} mb": "GDR：E₀ = {#} MeV，Γ₀ = {#} MeV，σ₀ = {#} mb",
  "dashed: SLO": "虚线：SLO",
  "at {#} MeV: SMLO / SLO = {#}": "{#} MeV 处：SMLO / SLO = {#}",
  "protons against neutrons": "质子相对中子振动",
  // scene 2: M1
  "M{#} strength f (MeV⁻³), A = {#}": "M{#} 强度 f (MeV⁻³)，A = {#}",
  "spin-flip": "自旋翻转",
  "scissors, β = {#}": "剪刀模式，β = {#}",
  "upbend": "低能上翘",
  "faint: E{#} at T = {#} MeV": "浅色：E{#}（T = {#} MeV）",
  "M{#} > E{#} below {#} MeV": "M{#} > E{#}（{#} MeV 以下）",
  "E{#} dominates at every energy here": "这里 E{#} 在所有能量上占主导",
  "scissors: the two deformed clouds rock": "剪刀模式：两团形变的云相对摆动",
  // scene 3: Brink-Axel
  "from {#} MeV": "从 {#} MeV 出发",
  "peak at Eγ ≈ {#} MeV": "峰值位于 Eγ ≈ {#} MeV",
  "primary spectrum T(Eγ) ρ(Eₓ − Eγ), each scaled to its peak": "初级谱 T(Eγ) ρ(Eₓ − Eγ)，各自按峰值归一",
  // scene 4: <Gamma_gamma>
  "contribution to ⟨Γγ⟩ per MeV of photon energy: E{#} (yellow), M{#} (purple, on top)": "每 MeV 光子能量对 ⟨Γγ⟩ 的贡献：E{#}（黄），M{#}（紫，叠在上面）",
  "{#} eV": "{#} eV",
  "measured {#} eV": "实测 {#} eV",
  "computed ⟨Γγ⟩ = {#} meV (E{#} {#} %, M{#} {#} %)": "计算 ⟨Γγ⟩ = {#} meV（E{#} {#} %，M{#} {#} %）",
  // scene 5: cascades
  "Sₙ": "Sₙ",
  "all photons from all cascades": "所有级联的全部光子",
  "{#} cascades · mean multiplicity {#}": "{#} 次级联 · 平均多重数 {#}",
});
Object.assign(WT.L.glossary, {
  smlo: {
    term: "SMLO", aliases: ["SMLO"],
    short: "简化修正洛伦兹型：一种 E1 强度函数，其宽度随光子能量和末态温度增大。",
    more: "由 V. Plujko 及其合作者提出，并在 IAEA 光子强度函数数据库（2019）中对每个原子核列表给出。本引擎与 TALYS-2 一样，默认的 E1 就是这份 SMLO-2019 表格。",
    chapter: "strength",
  },
  brinkAxel: {
    term: "Brink–Axel 假设", aliases: ["Brink–Axel 假设", "Brink–Axel"],
    short: "一种假设：光子强度函数只依赖于光子能量，而与发射它的状态的激发能无关。",
    more: "它使一个针对基态测量或计算的强度能够用于整个级联。检验方法是在不同激发能下提取强度；它近似成立，对某些原子核和能量的偏离仍有争论。",
    chapter: "strength",
  },
});
