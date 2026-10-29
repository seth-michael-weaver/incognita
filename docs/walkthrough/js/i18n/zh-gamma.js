/* Simplified Chinese: gamma (chapter 7, photon emission) */
WT.L.ch.gamma = {
  num: "第 10 章", title: "γ 射线发射", short: "光子",
  lead: "当没有粒子离开时，原子核通过发射光子来冷却：光子即γ射线，高能光的粒子。这个出口在任何能量下都是开放的。",
  html: `
<div class="step">
  <p>一个处于 8 MeV（百万电子伏特）的热态不断发射光子（γ）；梯子旁边的堆积记录它们落在哪里。2 MeV 以下的状态是少数几个有名称的梯级；2 MeV 以上则是随能量急剧变密的状态群（灰点）。每个光子带走它跃迁的能量 <i>E<sub>γ</sub></i>，画面亮度与 <i>E<sub>γ</sub></i>³ 成正比。</p>
  <div class="formula">T<sub>γ</sub>(E<sub>γ</sub>) = 2π · E<sub>γ</sub><sup>2l+1</sup> · f(E<sub>γ</sub>)</div>
  <p>用文字说：能量为 <i>E<sub>γ</sub></i> 的光子逃出来有多容易（<i>T<sub>γ</sub></i>，即第 9 章中光子的门），对常见的一类光子（偶极，<i>l</i> = 1）按 <i>E<sub>γ</sub></i>³ 增长，再乘以<b>光子强度函数</b> <i>f</i>：这个原子核在该能量下辐射的难易程度。然后它还必须找到一个可以落入的状态。小的跃迁有一大群状态等着，却几乎出不来；大的跃迁很容易出来，却几乎找不到状态。胜出的位于两者之间。</p>
  <div class="ctl"><label for="gm-e0">初始能量</label><input id="gm-e0" type="range" data-bind="E0" min="3" max="9" step="0.5" value="8"><output data-show="E0" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="emit">发射 100 个</button></div>
  <p>堆积的峰值位于初始能量以下几 MeV 处：大多数光子携带 2 到 4 MeV。移动初始能量，峰值随之移动。</p>
</div>
<div class="step">
  <h3>巨偶极共振</h3>
  <p>右边的大峰是<b>巨偶极共振</b>：所有质子（斜线）与所有中子（实心）来回相对晃动。它的频率决定了原子核最容易吸收和发射的光子能量。曲线是对数坐标下的光子强度函数 <i>f</i>（每上一格就增大十倍）。</p>
  <div class="ctl"><label for="gm-a">质量数 A</label><input id="gm-a" type="range" data-bind="A" min="40" max="240" step="1" value="112"><output data-show="A" data-fmt="0"></output></div>
  <p>拖动质量数 A（质子数加中子数）：重核晃动得更慢，在 12 到 14 MeV 附近振荡；轻核则在 20 MeV 附近。退激的原子核发射的光子只有几 MeV，所以最重要的是阴影部分的低能尾巴。</p>
</div>
<div class="step">
  <h3>低能磁偶极强度</h3>
  <p>形变的原子核还会以磁的方式辐射：它的质子（斜线）和中子（实心）像两个橄榄球，彼此相对摆动，就像剪刀的两片刀刃。这种<b>剪刀模式</b>位于 3 MeV 附近。8 MeV 附近的<b>自旋翻转</b>则是单个核子翻转自旋（小箭头），任何形状都有。</p>
  <div class="ctl"><label for="gm-b">形变 β₂</label><input id="gm-b" type="range" data-bind="beta" min="0" max="0.35" step="0.01" value="0.25"><output data-show="beta" data-fmt="2"></output></div>
  <p>拖动形变 β₂（0 为球形）。拉伸得越厉害，剪刀光子飞出越多；球形则完全没有。在最低能量处强度再次上升：这就是<b>低能上翘</b>（upbend），一股细流般的软光子，引擎会随原子核形变增大而削弱它。一个默认关闭的可选开关使用更强的剪刀模式系统学，与奥斯陆的测量相符（在铀中强四到五倍）。</p>
</div>
<div class="step">
  <h3>γ 级联</h3>
  <p>级联是一个接一个发射的光子，从顶部的能量区间（状态太密而无法逐一列出，第 8 章）一直到有名称的能级，这些能级被拉开以便阅读（实心梯级为宇称 +，空心为 −）。到了这里，引擎不再估算，而是遵循列表给出的<b>分支比</b>：每个能级衰变到每个更低能级的实测概率。</p>
  <div class="btns"><button class="btn" data-act="drop">释放一次级联</button></div>
  <p>多按几次按钮：上半部分每次都不同；结尾则沿着少数几条测量过的路径之一。</p>
</div>
<div class="step">
  <h3>同质异能态的产生</h3>
  <p>0.40 MeV 处的 11/2− 能级是一个<b>同质异能态</b>：它的自旋与下方能级相差太大，光子几乎无法连接它们，所以它的寿命从几秒到几年不等，落到那里的级联就停在那里。引擎把寿命超过一秒的任何能级都当作终点。每个小球代表一次级联，最终落入同质异能态的堆积或基态的堆积。</p>
  <div class="ctl"><label for="gm-j">入射自旋</label><input id="gm-j" type="range" data-bind="J0" min="0" max="8" step="1" value="2" data-instant><output id="gm-jout">5/2</output></div>
  <p>拖动入射自旋，即级联开始之处，堆积会重新开始。最终落在同质异能态上的份额，即<b>同质异能比</b>，取决于它：高自旋起点喂养高自旋的同质异能态；低自旋起点则绕过它，滑落到基态。</p>
</div>
<div class="step">
  <h3>辐射俘获</h3>
  <p>刚吸收一个慢中子的原子核有两扇出口之门（第 9 章）：光子（上方）和重新出射的中子（右方）。每扇门的缝隙就是它的<b>宽度</b>，单位 eV：原子核经由这扇门衰变的快慢。光子宽度几乎不变；中子宽度随中子速度增大。</p>
  <div class="ctl"><label for="gm-e">中子能量</label><input id="gm-e" type="range" data-bind="lgE" min="-2" max="3.3" step="0.02" value="0"><output id="gm-eout">1.0 keV</output></div>
  <p>拖动中子能量，从 10 eV 到 2 MeV。<b>俘获</b>，即 (n,γ)，指中子留下而一个光子离开：在 10 eV 时它几乎总是胜出，而在几 keV 以上只占很小的份额。阈能处的光子宽度已对数百个原子核测量过，可用于检验光子强度函数。默认情况下引擎使用自己的计算值；一个可选开关会对每个已测原子核的光子强度函数进行缩放，直到两者一致。</p>
  <div class="aside">代码位置：<code>gamma/parameters.py</code>（列表 E1 强度；巨共振、自旋翻转、剪刀模式和低能上翘的系统学），<code>gamma/strength.py</code>（各多极性的 <i>f</i>(E<sub>γ</sub>)），<code>gamma/transmission.py</code>（T<sub>γ</sub> 与平均辐射宽度），<code>structure/levels.py</code>（分支比、同质异能态），<code>emission/multiple.py</code>（级联）。可选，默认关闭：<code>gamma/scissors.py</code>（更强的剪刀模式），<code>gamma/ggnorm.py</code>（拟合实测 ⟨Γγ⟩，直到铅），<code>gamma/actphys.py</code>（两者兼用，适用于锕系核）。</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // scene 1: emit
  "energy ↑": "能量 ↑",
  "named levels": "有名称的能级",
  "a crowd of states": "密集的状态",
  "{#} MeV": "{#} MeV",
  "hot state, {#} MeV": "热态，{#} MeV",
  "most photons ≈ {#} MeV": "多数光子 ≈ {#} MeV",
  "small drops: faint (E³ tiny)": "小跃迁：暗淡（E³ 很小）",
  "big drops: bright, but few states to land on": "大跃迁：明亮，但可落入的状态少",
  // scene 2: gdr
  "protons": "质子",
  "neutrons": "中子",
  "A = {#}: rings at {#} MeV": "A = {#}：在 {#} MeV 振荡",
  "peak {#} MeV": "峰值 {#} MeV",
  "giant resonance at {#} MeV": "巨共振位于 {#} MeV",
  "width ≈ {#} MeV": "宽度 ≈ {#} MeV",
  "decays use this": "衰变用这部分",
  "shaded: the tail decays use": "阴影：衰变所用的尾巴",
  "photon energy (MeV) →": "光子能量（MeV）→",
  "photon strength f (log scale) ↑": "光子强度 f（对数）↑",
  // scene 3: m1
  "a sphere has no blades: no scissors": "球形没有刀刃：无剪刀模式",
  "scissors ≈ {#} MeV: strength {#} % of the most stretched": "剪刀 ≈ {#} MeV：强度为最大拉伸时的 {#} %",
  "spin-flip ≈ {#} MeV: steady, any shape (thick photons)": "自旋翻转 ≈ {#} MeV：稳定，任何形状（粗光子）",
  "upbend below {#} MeV: soft photons, plenty at this shape": "上翘 {#} MeV 以下：软光子，此形状下很多",
  "upbend below {#} MeV: soft photons, fewer at this shape": "上翘 {#} MeV 以下：软光子，此形状下较少",
  "upbend below {#} MeV: soft photons, few at this shape": "上翘 {#} MeV 以下：软光子，此形状下很少",
  // scene 4: cascade
  "ground state": "基态",
  "isomer": "同质异能态",
  "isomer: long-lived": "同质异能态：长寿命",
  "bins: too dense to list": "能量区间：太密无法列出",
  "one photon at a time": "一次一个光子",
  "measured branching ratios": "实测分支比",
  "▬ parity +   ▭ parity −": "▬ 宇称 +   ▭ 宇称 −",
  // scene 5: isomer
  "entrance: J = {#}/{#}": "入射：J = {#}/{#}",
  "isomer: {#} ({#} %)": "同质异能态：{#}（{#} %）",
  "ground state: {#} ({#} %)": "基态：{#}（{#} %）",
  "many cascades: ≈ {#} % isomer": "多次级联：≈ {#} % 同质异能态",
  "over many cascades from J = {#}/{#}: ≈ {#} % end on the isomer": "从 J = {#}/{#} 的多次级联：≈ {#} % 终止于同质异能态",
  // scene 6: capture
  "photon door: {#} eV, barely changes": "光子之门：{#} eV，几乎不变",
  "captured (n,γ): {#} ({#} %)": "俘获 (n,γ)：{#}（{#} %）",
  "neutron: {#} eV": "中子：{#} eV",
  "neutron door: {#} eV, wider when faster": "中子之门：{#} eV，越快越宽",
  "back out: {#} ({#} %)": "重新出射：{#}（{#} %）",
  "more doors open (target left excited)": "更多门开放（靶核留在激发态）",
  "{#} eV neutrons →": "{#} eV 中子 →",
  "{#} keV neutrons →": "{#} keV 中子 →",
  "{#} MeV neutrons →": "{#} MeV 中子 →",
  "slow neutrons: the photon door wins": "慢中子：光子之门胜出",
  "the neutron door wins; capture takes about {#} %": "中子之门胜出；俘获约占 {#} %",
  "fast: capture is a rare event": "快中子：俘获很罕见",
});

// canvas labels added 2026-10-29 (I18NLABELS_B)
Object.assign(WT.L.labels, {
  "{#} cascades from J = {#}/{#}: ≈ {#} % end on the isomer": "{#} 次级联，从 J = {#}/{#} 出发：≈ {#} % 终止于同质异能态",
});
