/* Simplified Chinese: compound (chapter 5) */
WT.L.ch.compound = {
  num: "第 8 章", title: "复合核", short: "复合核",
  lead: "最初的快速碰撞结束后，所有核子共同分享能量。这种安定下来的状态就是复合核。要预言它接下来会做什么，引擎需要知道它有多少种方式来容纳自己的能量。",
  html: `
<div class="step">
  <p>一个中子撞上原子核的一侧。它的能量，加上被俘获时释放的能量，起初集中在一个热点上（橙色光晕）；碰撞把能量不断传递出去，大约 10⁻²¹ 秒之内，每个核子都分到一份。</p>
  <div class="btns"><button class="btn" data-act="hit">从另一侧撞击</button></div>
  <p>按下按钮，让中子从另一侧射入。光晕的结局总是一样：原子核已经<b>忘记了自己是如何形成的</b>。这就是玻尔的复合核。从这里开始，只有三个量是重要的：它的能量、它的自旋（转动有多快）和它的宇称（表示镜像对称性的 + 或 − 标记）。</p>
</div>
<div class="step">
  <h3>从分立能级到连续区</h3>
  <p>左边的梯子容纳原子核的各个状态，能量向上增加；右边的窗口放大橙色小球附近 1 MeV 宽的一段。靠近底部，梯级相距很远，每一级都已经测量过。再往上，在 56 个核子之间分配能量的方式急剧增多，直到梯级模糊成一条实心的带，即连续区。</p>
  <div class="ctl"><label for="cn-e">激发能</label><input id="cn-e" type="range" data-bind="E" min="0" max="20" step="0.1" value="6.5"><output data-show="E" data-fmt="1"></output></div>
  <p>拖动激发能（高于最低状态所储存的能量，单位 MeV），观察窗口。<b>能级密度</b> ρ，即每 MeV 的状态数，大致按 e<sup>2√(aE)</sup> 增长，其中 <i>a</i> 决定每个原子核的增长速度：3 MeV 处每 MeV 只有几个，8 MeV 附近（中子可以逃逸的地方）有数百个，到 20 MeV 则有数百万个。在那么高的地方，引擎直接使用 ρ 本身。</p>
</div>
<div class="step">
  <h3>组合能级密度</h3>
  <p>地形的高度是对数坐标下的能级密度，能量向右增加。左下方是计数得到的能级。笔直的木板是<b>恒温公式</b>：每增加 <i>T</i> MeV，ρ 就乘以 e（约 2.7），其中 <i>T</i> 是核温度。山坡是<b>费米气体</b>，它把核子当作独立粒子处理。除了最重的靶核会读取列表给出的能级密度外，引擎默认使用这一对模型。</p>
  <div class="ctl"><label for="cn-ex">匹配能</label><input id="cn-ex" type="range" data-bind="Ex" min="4.5" max="12" step="0.05" value="6"><output data-show="Ex" data-fmt="1"></output></div>
  <p>拖动匹配能：接点沿山坡滑动，木板随之转动，以相同的高度和斜率与之相接。下方的两摞比较木板预言的能级数与实际计数的能级数。只有一个接点能使两者相等；此时木板变成绿色。这就是引擎选定的能量。</p>
</div>
<div class="step">
  <h3>壳效应及其衰减</h3>
  <p>两个原子核的单核子能级，每个能级容纳两个核子。左边是闭合壳层：一个大能隙以下全部填满，所以任何跃迁都要付出整个能隙的代价。右边是壳层中部的原子核，最上面的能级只填了一半，所以一开始就有代价很低的跃迁。每个计数器显示能容纳给定热量的排布方式有多少。</p>
  <div class="ctl"><label for="cn-u">热量（激发）</label><input id="cn-u" type="range" data-bind="U" min="0" max="40" step="0.5" value="3"><output data-show="U" data-fmt="1"></output></div>
  <p>把热量调高，看核子如何跃迁。热量较低时，闭合壳层的排布方式严重不足；热量足够时，能隙不再重要，两边的计数以相同方式增长。引擎把这一点概括为每个原子核的一个数，即<b>能级密度参数</b> <i>a</i>：<i>a</i> 越大，排布方式的数目随热量增长得越快。指针显示了每个原子核的 <i>a</i>：它们起初分开，在大约 10 MeV 的范围内都落到同一个平滑值（记作 <i>ã</i>，读作“a 波浪”），也就是没有壳层能隙的原子核会有的值。</p>
  <p>因此，引擎为每个原子核从它的壳效应出发（能隙值得的额外能量，记作 δW），并让这一效应随热量升高而逐渐消失。</p>
  <div class="aside">公式：<i>a</i>(<i>U</i>) = <i>ã</i> · [1 + δW · (1 − e<sup>−γ<i>U</i></sup>) / <i>U</i>]，其中 <i>U</i> 是热量，γ（伽马，这里约为每 MeV 0.1，较重的原子核更小）表示壳效应消失的快慢。</div>
</div>
<div class="step">
  <h3>自旋与宇称分布</h3>
  <p>同一能量的状态按自旋 <i>J</i>（原子核的角动量）放入不同的抽屉：实心标记表示 + 宇称，空心表示 −。中间的抽屉装得最多，遵循 (2<i>J</i>+1) e<sup>−(J+½)²/2σ²</sup>，其中自旋截断参数 σ 决定分布的宽度。两种宇称的数目大致相等。</p>
  <div class="ctl"><label for="cn-u2">激发</label><input id="cn-u2" type="range" data-bind="U2" min="1" max="30" step="0.5" value="8"><output data-show="U2" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="deform">使原子核形变</button></div>
  <p>把激发调高：σ 增大，因为更热的原子核能够携带更大的自旋。然后按“形变”。橄榄球形状的原子核还能整体转动，所以每个抽屉都会增加状态（蓝色标记）：这就是<b>集体增强</b>。默认情况下，引擎只对核子数超过约 215 的靶核加入这一效应。</p>
</div>
<div class="step">
  <h3>连续区中的能量区间</h3>
  <p>在最后一个计数能级以上，引擎把连续区切成能量宽度相等的片段，称为能量区间（bin）。在每个能量区间中，点聚合成一个包含 ρ·ΔE 个状态的方块（ΔE 是区间宽度），并像上面一样按自旋和宇称分类。</p>
  <div class="ctl"><label for="cn-emax">梯子顶端</label><input id="cn-emax" type="range" data-bind="Emax" min="8" max="30" step="0.5" value="14"><output data-show="Emax" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="rebin">重新分类</button></div>
  <p>拖动梯子顶端，即中子所能带来的最大能量。同样数目的能量区间必须覆盖更大的能量范围，所以每个区间都变高了。橙色小球逐个区间下落：之后的每一步（选择出口、光子级联、在核素图上的行走）都在这些能量区间上进行。这里画了十个；引擎最多使用 40 个。</p>
  <div class="aside">代码位置：<code>density/parameters.py</code>（Ignatyuk 的 <i>a</i>(U)、自旋截断参数、Wigner 分布、集体增强），<code>density/models.py</code>（恒温公式、费米气体、数据表），<code>density/matching.py</code>（由计数能级确定匹配能），<code>core/grids.py</code>（激发能量区间）。</div>
</div>`,
};
(function () {
  const L = {
    // scene 1
    "a neutron comes in": "一个中子射入",
    "a hot spot: the energy is still local": "热点：能量仍集中在局部",
    "equilibrium: every nucleon holds a share": "平衡：每个核子各分一份",
    "no trace left of where it was hit": "撞击位置已无迹可寻",
    // scene 2
    "ground state": "基态",
    "{#}–{#} MeV, magnified": "{#}–{#} MeV，放大",
    "no level in this slice": "此段内没有能级",
    "{#} rung in {#} MeV": "{#} 级（{#} MeV 内）",
    "{#} rungs in {#} MeV": "{#} 级（{#} MeV 内）",
    "{#} rung in this {#}-MeV slice": "{#} 级（本段宽 {#} MeV）",
    "{#} rungs in this {#}-MeV slice": "{#} 级（本段宽 {#} MeV）",
    "about {#} rungs: too close to draw": "约 {#} 级：太密，无法画出",
    "about {#}k rungs: too close to draw": "约 {#} 千级：太密，无法画出",
    "about {#}M rungs: too close to draw": "约 {#} 百万级：太密，无法画出",
    "about {#}B rungs: too close to draw": "约 {#} 十亿级：太密，无法画出",
    "about {#} rungs in this slice: too close to draw": "本段约 {#} 级：太密，无法画出",
    "about {#} thousand rungs in this slice: too close to draw": "本段约 {#} 千级：太密，无法画出",
    "about {#} million rungs in this slice: too close to draw": "本段约 {#} 百万级：太密，无法画出",
    "about {#} billion rungs in this slice: too close to draw": "本段约 {#} 十亿级：太密，无法画出",
    "each one measured: energy, spin and parity": "每一级都已测量：能量、自旋和宇称",
    "the rungs are multiplying": "梯级急剧增多",
    "a continuum: the engine uses ρ itself": "连续区：引擎直接用 ρ",
    "≈ energy to free a neutron": "≈ 释放一个中子所需能量",
    "energy ↑": "能量 ↑",
    // scene 3
    "gap: plank below the rungs": "偏差：木板低于梯级",
    "gap: plank above the rungs": "偏差：木板高于梯级",
    "counted levels": "计数能级",
    "CT plank": "恒温木板",
    "constant-temperature plank": "恒温公式木板",
    "Fermi-gas hillside": "费米气体山坡",
    "joint {#} MeV": "接点 {#} MeV",
    "energy →": "能量 →",
    "+{#} more": "另 {#} 个",
    "{#} counted": "计数 {#}",
    "{#} predicted": "预言 {#}",
    "{#}+ predicted": "预言 {#}+",
    "equal: the plank rests on the counted rungs": "相等：木板落在计数梯级上",
    "too few: the plank is too steep and sinks": "太少：木板太陡，下沉",
    "too many: the plank is too shallow and floats": "太多：木板太平，上浮",
    // scene 4
    "closed shell": "闭合壳层",
    "mid-shell": "壳层中部",
    "gap": "能隙",
    "no arrangement holds this heat": "没有排布能容纳此热量",
    "≈ {#} arrangement": "≈ {#} 种排布",
    "≈ {#} arrangements": "≈ {#} 种排布",
    "≈ {#} thousand arrangements": "≈ {#} 千种排布",
    "≈ {#} million arrangements": "≈ {#} 百万种排布",
    "≈ {#} billion arrangements": "≈ {#} 十亿种排布",
    "a ≈ {#}": "a ≈ {#}",
    "cold: nobody can move": "冷：没有核子能移动",
    "temperature ≈ {#} MeV": "温度 ≈ {#} MeV",
    // scene 5
    "states at {#} MeV": "{#} MeV 处的状态",
    "spin J →": "自旋 J →",
    "+ parity": "+ 宇称",
    "− parity": "− 宇称",
    "rotation ×{#}": "转动 ×{#}",
    "added by rotation: ×{#} (a few drawn)": "转动增加：×{#}（只画出几个）",
    "spread σ ≈ {#}: most states near J ≈ {#}": "宽度 σ ≈ {#}：多数状态在 J ≈ {#} 附近",
    "deformed: it can rotate": "形变：可以转动",
    "spherical": "球形",
    // scene 6
    "≈ {#} thousand": "≈ {#} 千",
    "≈ {#} million": "≈ {#} 百万",
    "≈ {#} billion": "≈ {#} 十亿",
    "≈ {#}k": "≈ {#} 千",
    "≈ {#}M": "≈ {#} 百万",
    "≈ {#}B": "≈ {#} 十亿",
    "{#} bins, each {#} MeV wide": "{#} 个区间，每个宽 {#} MeV",
    "counted": "计数",
    "states in each bin": "每个区间的状态数",
  };
  Object.assign(WT.L.labels, L);
})();
