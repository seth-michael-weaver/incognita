/* Simplified Chinese (简体中文): measure (chapter 11) */
WT.L.ch.measure = {
  num: "第 17 章", title: "可观测量", short: "可观测量",
  lead: "实验、反应堆或恒星能“看到”的只有寥寥几个数字。本章展示引擎如何把原子核内部发生的事情转化为这些数字。",
  html: `
<div class="step">
  <p>每个原子核周围的浅色圆盘是它的<b>截面</b>：中子必须击中这块面积才会发生反应，它并不是原子核的真实大小。一束中子从左边射来，穿过一片由原子核组成的薄靶；发生反应的比例等于这块面积乘以中子遇到的原子核数目。单位是靶恩（10⁻²⁴ cm²，大约相当于一个铀原子核的正面面积）。</p>
  <div class="ctl"><label for="mea-e">中子能量 (MeV)</label><input id="mea-e" type="range" data-bind="E" min="0.1" max="20" step="0.1" value="2"><output data-show="E" data-fmt="1"></output></div>
  <p>降低能量，圆盘就会胀大：慢中子是一列宽阔的波，在更远处就能发生反应。能量高时，圆盘收缩到接近原子核本身。</p>
</div>
<div class="step">
  <h3>激发函数</h3>
  <p>每扇门是一个出口，即一个<b>反应道</b>：中子被弹出（弹性），使靶核处于激发态（n′），打出更多中子（2n、3n），被俘获后只放出光子（γ），或者改为放出一个质子或 α 粒子。上了锁的门有一个<b>阈能</b>：这个反应所需的能量超过了中子带来的能量。</p>
  <div class="ctl"><label for="mea-e2">中子能量 (MeV)</label><input id="mea-e2" type="range" data-bind="E" min="0.1" max="20" step="0.1" value="2"><output data-show="E" data-fmt="1"></output></div>
  <p>把能量拖过某个阈能，那扇门就会一闪而开；各个桶按每个反应道所占的份额装满，每扇新开的门都会从其他门那里分走一部分份额。阈能由原子核的质量决定；份额则来自第 9 章所讲的竞争。</p>
</div>
<div class="step">
  <h3>发射能谱</h3>
  <p>两堆分别是到达环形探测器前半部和后半部的中子，按能量排列。中子束是脉冲式的，因此每个中子的飞行时间给出它的能量：快中子先到。</p>
  <div class="ctl"><label for="mea-ein">入射能量 (MeV)</label><input id="mea-ein" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="30"><output data-show="Ein" data-fmt="0"></output></div>
  <p>两堆都有一个由慢速<b>蒸发</b>中子形成的鼓包：能量分配均匀之后，它们从复合核中“蒸发”出来，各个方向都一样。只有前向的那堆有一条长长的高能尾巴：这是<b>预平衡</b>中子，它们在最初几次碰撞中就离开了，运动方向仍大致与入射束一致。提高入射能量，尾巴就会变长。</p>
</div>
<div class="step">
  <h3>角分布</h3>
  <p>花瓣形图案显示有多少中子飞向各个方向；中子束从左边射来。蒸发中子已经“忘记”了入射方向，向各个方向均匀飞出；快速的预平衡中子则偏向前方。偏多少由 Kalbach 规则决定，其中只有一个斜率参数 <i>a</i>，它随出射能量增大。引擎也可以把这些角分布作为可选输出写出来。</p>
  <div class="ctl"><label for="mea-eo">出射能量 (MeV)</label><input id="mea-eo" type="range" data-bind="Eout" min="1" max="45" step="0.5" value="25"><output data-show="Eout" data-fmt="1"></output></div>
  <p>降低出射能量，花瓣就变圆：慢中子大多是蒸发出来的。</p>
  <div class="formula">dσ/dΩ ∝ e<sup>a cos θ</sup></div>
</div>
<div class="step">
  <h3>麦克斯韦平均截面</h3>
  <p>下方的一堆收集了在恒星炽热气体中被俘获的中子的能量。它们的速度服从由温度 <i>kT</i> 决定的麦克斯韦分布（30 keV 约合 3.5 亿度）；轨迹越长表示中子越快，每次从原子核旁经过都可能以一次俘获闪光告终。</p>
  <div class="ctl"><label for="mea-kt">温度 kT (keV)</label><input id="mea-kt" type="range" data-bind="kT" min="5" max="100" step="1" value="30"><output data-show="kT" data-fmt="0"></output></div>
  <p>慢中子容易被俘获，但很少经过；快中子数量又少，所以大部分俘获来自宽度为几个 <i>kT</i> 的窗口。整团气体上的反应率就是<b>宏观麦克斯韦平均截面</b>（MACS），单位为毫靶（mb）。把气体加热，窗口就移向更高的能量，那里的靶面积更小。MACS 由引擎给出的俘获曲线积分（折算）得到。</p>
</div>
<div class="step">
  <h3>热激发的靶核</h3>
  <p>小球显示在这个温度下，靶核处在其最低几个能级上的比例。在恒星中，有些靶核已经处于激发态，而每个激发能级都是通向同一个复合核的不同入口。自旋为 <i>J</i> 的能级容纳得更多，因为它有 2<i>J</i>+1 个取向。</p>
  <div class="ctl"><label for="mea-kt2">温度 kT (keV)</label><input id="mea-kt2" type="range" data-bind="kT" min="5" max="100" step="1" value="30"><output data-show="kT" data-fmt="0"></output></div>
  <p>升高温度，看原子核向上跃迁。恒星反应率对每个有布居的能级分别计算俘获，再按这些比例相加；权重之和就是配分函数 <i>G</i>，而它与基态反应率之比就是<b>恒星增强因子</b>。引擎可以把这作为一个选项来计算，默认关闭；通常每个靶核都从基态出发。</p>
</div>
<div class="step">
  <h3>不确定度与协方差</h3>
  <p>每个淡淡的圆盘都是引擎的一次运行，其输入数据被随机微调：光学势阱的深度、能级密度和光子强度，它们各自都只知道到几个百分点以内。多次运行结果的离散程度就是一种诚实的不确定度：<b>全蒙特卡罗</b>。</p>
  <div class="btns"><button class="btn" data-act="tmc1">运行一个变体</button><button class="btn ghost" data-act="tmc">运行 10 次</button><button class="btn ghost" data-act="clear">清除</button></div>
  <p>边缘清晰，说明输入数据把答案确定下来了；边缘模糊，说明没有，而那里正是新测量最能发挥作用的地方。</p>
  <div class="aside">代码位置：<code>emission/channels.py</code>（排他反应道与剩余核），<code>specout.py</code> 和 <code>specang.py</code>（出射能谱、角分布和双微分截面，仅在要求时输出），<code>astro/stellar.py</code>（从热布居的靶核能级出发的俘获，可选），<code>tmc.py</code>（全蒙特卡罗抽样程序）。基态 MACS 由 <code>validation/differential/core.py</code> 中的俘获曲线折算得到。</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // area
  "each disc: σ ≈ {#} b": "每个圆盘：σ ≈ {#} b",
  "each disc: cross section σ ≈ {#} b, the area a neutron must hit": "每个圆盘：截面 σ ≈ {#} b，即中子须击中的面积",
  "beam →": "中子束 →",
  "nucleus's own face ≈ {#} b · {#} % reacts": "原子核正面 ≈ {#} b · {#} % 发生反应",
  "the nucleus's own face ≈ {#} b · {#} % of the beam reacts in this foil": "原子核自身正面 ≈ {#} b · 束流中 {#} % 在此薄靶中反应",
  "slow: the neutron's wave reaches well past the surface": "慢：中子的波远远伸出表面之外",
  "the target still looks bigger than the nucleus": "靶仍显得比原子核大",
  "fast: close to the nucleus's own size": "快：接近原子核本身大小",
  // doors
  "elastic": "弹性", "n′ inelastic": "n′ 非弹性", "{#}n": "{#}n", "γ capture": "γ 俘获", "p": "p", "α": "α", "n′": "n′",
  "{#}n · {#} MeV": "{#}n · {#} MeV", "p · {#} MeV": "p · {#} MeV", "α · {#} MeV": "α · {#} MeV", "n′ inelastic · {#} MeV": "n′ 非弹性 · {#} MeV",
  "opens at {#} MeV": "{#} MeV 时开启",
  "{#} MeV": "{#} MeV",
  // detect
  "forward half": "前半部", "backward half": "后半部",
  "pulsed beam": "脉冲束", "pulsed beam →": "脉冲束 →",
  "backward": "后向", "backward detectors": "后向探测器",
  "forward": "前向", "forward detectors": "前向探测器",
  "outgoing neutron energy from the flight time (MeV) →": "由飞行时间得出的出射中子能量 (MeV) →",
  "fast tail": "高能尾", "fast tail: pre-equilibrium": "高能尾：预平衡",
  "evaporated hump": "蒸发鼓包", "hump: evaporated, every way alike": "鼓包：蒸发，各向相同",
  "{#} % leave before the energy is shared": "{#} % 在能量分配前离开",
  // angle
  "beam": "中子束",
  "forward-to-backward ratio ≈ {#}  ·  slope a ≈ {#}": "前后比 ≈ {#}  ·  斜率 a ≈ {#}",
  "mostly evaporated: every direction alike": "大多为蒸发：各向相同",
  "a mix: the fast share leans forward": "混合：快速部分偏向前方",
  "mostly pre-equilibrium: strongly forward": "大多为预平衡：强烈前倾",
  "forward →": "前向 →",
  // star
  "{#} keV": "{#} keV",
  "kT = {#} keV": "kT = {#} keV",
  "energies of captured neutrons": "被俘获中子的能量",
  "each capture drops here, by the neutron's energy: the window that counts": "每次俘获按中子能量落在此处：起作用的窗口",
  "MACS ≈ {#} mb at kT = {#} keV · captures watched: {#}": "MACS ≈ {#} mb（kT = {#} keV）· 已观察俘获：{#}",
  // hot target
  "{#}⁺  ground state": "{#}⁺  基态", "{#}⁺  {#} keV": "{#}⁺  {#} keV",
  "target levels, with the share of nuclei sitting on each": "靶核能级及各能级上原子核所占比例",
  "{#} % start from the ground state · partition function G ≈ {#}": "{#} % 从基态出发 · 配分函数 G ≈ {#}",
  // TMC
  "optical well": "光学势阱", "optical well depth": "光学势阱深度",
  "level density": "能级密度", "photon strength": "光子强度",
  "σ ≈ {#} b ": "σ ≈ {#} b ", "σ ≈ {#} mb ": "σ ≈ {#} mb ",
  "σ ≈ {#} b ±{#} %": "σ ≈ {#} b ±{#} %", "σ ≈ {#} mb ±{#} %": "σ ≈ {#} mb ±{#} %",
  "dashed: best inputs · each disc drawn at its own scale": "虚线：最佳输入 · 各圆盘按各自比例绘制",
  "dashed ring: the best-value inputs · each energy drawn at its own scale (disc area ∝ σ)": "虚线环：最佳值输入 · 各能量按各自比例绘制（圆盘面积 ∝ σ）",
  "{#} runs of the engine, each with its inputs nudged at random": "引擎运行 {#} 次，每次随机微调输入",
});

// canvas labels added 2026-10-29 (I18NLABELS_B)
Object.assign(WT.L.labels, {
  "target levels, with the share of nuclei sitting on each (energy scale stretched near the bottom)": "靶核能级及各能级上原子核所占的份额（底部附近能量刻度已拉伸）",
});
