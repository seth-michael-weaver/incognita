/* Simplified Chinese (简体中文): stars (元素从哪里来) */
WT.L.ch.stars = {
  num: "第1课", title: "元素从哪里来", short: "恒星",
  html: `
<div class="step">
  <h3>聚变止于铁</h3>
  <p>恒星把轻核一路聚变到铁；几乎所有更重的元素都是靠添加中子造出来的。</p>
</div>
<div class="step">
  <h3>慢路径</h3>
  <p>在巨星中，中子来得很稀少，所以不稳定的核会先发生 β 衰变：路径沿着稳定核呈锯齿状前进。</p>
  <div class="ctl"><label for="st-k">中子俘获次数</label><input id="st-k" type="range" data-bind="k" min="0" max="213" step="1" value="112"></div>
</div>
<div class="step">
  <h3>快路径</h3>
  <p>在中子星并合中，中子涌入的速度快于原子核衰变；之后这些富中子核再衰变回稳定区。</p>
  <div class="ctl"><label for="st-rt">衰变回去</label><input id="st-rt" type="range" data-bind="rt" min="0" max="1" step="0.01" value="0"></div>
</div>
<div class="step">
  <h3>幻数造成峰</h3>
  <p>中子数为 50、82 或 126 的核几乎不俘获中子，因此物质在那里堆积：s 峰位于锶、钡和铅，r 峰稍轻一些。</p>
  <div class="btns"><button class="btn ghost" data-act="stS" aria-pressed="true">s 过程峰</button> <button class="btn ghost" data-act="stR" aria-pressed="true">r 过程峰</button></div>
</div>
<div class="step">
  <h3>易俘获者稀少</h3>
  <p>对只由 s 过程产生的同位素，丰度 Nₛ 乘以俘获截面 σ 在幻数之间几乎不变。这里的 σ 是 INCOGNITA 在 30 keV 下的计算值。</p>
  <div class="btns"><button class="btn ghost" data-act="stvs" aria-pressed="false">σ</button> <button class="btn ghost" data-act="stvn" aria-pressed="false">Nₛ</button> <button class="btn ghost" data-act="stvsn" aria-pressed="true">σ × Nₛ</button></div>
</div>
<div class="step">
  <h3>与测量值对照</h3>
  <p>INCOGNITA 的 30 keV 值除以测量值，共 94 个稳定核素（<a href="scoreboard.html">对比</a>）。</p>
</div>`,
};
Object.assign(WT.L.labels, {
  "A ≈ {#}": "A ≈ {#}",
  "Ba": "Ba",
  "Ba{#}": "Ba{#}",
  "Big Bang": "大爆炸",
  "Fe": "Fe",
  "H": "H",
  "He": "He",
  "INCOGNITA ÷ measured, {#} keV": "INCOGNITA ÷ 测量值，{#} keV",
  "INCOGNITA's {#} keV capture rate (MACS) ÷ measured": "INCOGNITA 的 {#} keV 俘获率（MACS）÷ 测量值",
  "INCOGNITA: capture at {#} keV (MACS)": "INCOGNITA：{#} keV 处的俘获（MACS）",
  "Lodders et al. {#}": "Lodders et al. {#}",
  "Lu{#}": "Lu{#}",
  "N = {#}": "N = {#}",
  "O": "O",
  "Pb": "Pb",
  "Pb{#}": "Pb{#}",
  "Sm{#}": "Sm{#}",
  "Sn": "Sn",
  "Sr": "Sr",
  "Sr{#}": "Sr{#}",
  "abundances: Lodders, Palme & Gail {#}": "丰度：Lodders, Palme & Gail {#}",
  "abundances: Lodders, Palme & Gail {#} · point at the curve": "丰度：Lodders, Palme & Gail {#} · 指向曲线",
  "atoms per million silicon atoms (Solar System)": "每百万个硅原子对应的原子数（太阳系）",
  "atoms per {#}⁶ silicon": "每 {#}⁶ 个硅原子",
  "beta decay (n → p)": "β 衰变（n → p）",
  "flat between magic numbers, steps down at each": "幻数之间平坦，每个幻数处下一个台阶",
  "fusion": "聚变",
  "fusion in stars": "恒星中的聚变",
  "made by neutron capture": "由中子俘获生成",
  "magic N: captures poorly, matter piles up": "幻数 N：难俘获，物质堆积",
  "magic neutron number: it captures poorly, so matter piles up here": "中子幻数：难以俘获，所以物质在这里堆积",
  "mass number A": "质量数 A",
  "mass number A (protons + neutrons)": "质量数 A（质子 + 中子）",
  "mb": "mb",
  "nearly flat between magic numbers, a step down at each": "幻数之间几乎平坦，每个幻数处下一个台阶",
  "neutron capture": "中子俘获",
  "neutrons N →": "中子数 N →",
  "peaks: sources Lodders et al. {#}": "峰：数据来源 Lodders et al. {#}",
  "plus a weaker s-process (massive stars)": "另有较弱的 s 过程（大质量恒星）",
  "r {#}": "r {#}",
  "r-path: illustration": "r 路径：示意",
  "r-peak Pt": "r 峰 Pt",
  "r-peak Se, Kr": "r 峰 Se、Kr",
  "r-peak Te, Xe": "r 峰 Te、Xe",
  "r-process: a flood of neutrons makes very neutron-rich nuclei": "r 过程：中子洪流造出极富中子的核",
  "r-process: very neutron-rich nuclei": "r 过程：极富中子的核",
  "ringed: s-only isotopes · measured: compiled values (KADoNiS) · a development comparison, not an independent test": "带圈：纯 s 同位素 · 测量值：汇编值（KADoNiS）· 开发中的对比，不是独立检验",
  "ringed: s-only · measured: KADoNiS": "带圈：纯 s · 测量值：KADoNiS",
  "s Ba": "s Ba",
  "s Pb": "s Pb",
  "s Sr": "s Sr",
  "s-only isotopes · bars: INCOGNITA {#} %": "纯 s 同位素 · 误差棒：INCOGNITA {#} %",
  "s-only isotopes · σ: INCOGNITA (bars: its {#} % range; open circle: scaled to a measurement) · Nₛ: Lodders et al. {#}": "纯 s 同位素 · σ：INCOGNITA（误差棒：其 {#} % 区间；空心圆：按测量值标定）· Nₛ：Lodders et al. {#}",
  "s-peak Ba": "s 峰 Ba",
  "s-peak Pb": "s 峰 Pb",
  "s-peak Sr": "s 峰 Sr",
  "seen in {#}: merger GW{#}": "{#} 年观测到：并合 GW{#}",
  "seen in {#}: the neutron-star merger GW{#} and its kilonova": "{#} 年观测到：中子星并合 GW{#} 及其千新星",
  "wait": "等待",
  "waiting point": "等待点",
  "weak s-process too": "还有弱 s 过程",
  "σ × Nₛ (mb × atoms per million Si)": "σ × Nₛ（mb × 每百万 Si 原子数）",
  "σ × Nₛ (mb × atoms per {#}⁶ Si)": "σ × Nₛ（mb × 每 {#}⁶ Si 原子数）",
  "↑ protons Z": "↑ 质子数 Z",
  "A = {a}: mostly {b}, {c} atoms per million silicon": "A = {a}：主要是 {b}，每百万硅原子 {c} 个",
  "decayed back: r-made stable isotopes": "已衰变回来：r 过程生成的稳定同位素",
  "decayed back: each lands on the most neutron-rich stable isobar": "已衰变回来：各自落在最富中子的稳定同量异位素上",
  "beta decays, A fixed": "β 衰变，A 不变",
  "beta decays carry them back, mass number A fixed": "β 衰变把它们带回来，质量数 A 不变",
  "{a} · N = {b} · σ = {c} mb": "{a} · N = {b} · σ = {c} mb",
  "{a} · N = {b} · INCOGNITA: σ = {c} mb at {#} keV": "{a} · N = {b} · INCOGNITA：σ = {c} mb（{#} keV）",
  "{a} · unstable: beta decay": "{a} · 不稳定：β 衰变",
  "{a} · unstable: it beta-decays before the next neutron": "{a} · 不稳定：在下一个中子到来前就 β 衰变",
  "end: the lead–bismuth cycle": "终点：铅–铋循环",
  "end of the road: Bi{#} → Po{#} → alpha decay back to Pb{#}": "路的尽头：Bi{#} → Po{#} → α 衰变回到 Pb{#}",
  "drag along the path": "沿路径拖动",
  "drag along the path, or use the slider": "沿路径拖动，或使用滑块",
  "{a}: INCOGNITA σ = {b} mb": "{a}：INCOGNITA σ = {b} mb",
  "{a}: σ = {b} mb × Nₛ = {c} → σNₛ = {d}": "{a}：σ = {b} mb × Nₛ = {c} → σNₛ = {d}",
  " (σ scaled to a measured value)": "（σ 已按测量值标定）",
  "σ alone: scattered": "仅 σ：分散",
  "σ alone jumps around from isotope to isotope": "仅看 σ，各同位素之间上下跳动",
  "Nₛ alone: scattered": "仅 Nₛ：分散",
  "Nₛ alone jumps around the other way": "仅看 Nₛ，则朝相反方向跳动",
  "{a}: INCOGNITA's engine {b} (the library then scales to it)": "{a}：INCOGNITA 引擎 {b}（库随后按测量值标定）",
  "{a}: INCOGNITA σ = {b} mb, {c}": "{a}：INCOGNITA σ = {b} mb，{c}",
  "{a} nuclides · typical difference {b} %": "{a} 个核素 · 典型差异 {b} %",
  "{a} stable nuclides · typical difference {b} % (median), rms {c} %": "{a} 个稳定核素 · 典型差异 {b} %（中位数），均方根 {c} %",
  "{a} % above measured": "比测量值高 {a} %",
  "{a} % below measured": "比测量值低 {a} %",
});
