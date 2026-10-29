/* Simplified Chinese (简体中文): exciton (chapter 17, 激子模型的定量计算) */
WT.L.ch.exciton = {
  num: "第 26 章", title: "激子模型的定量计算", short: "激子模型",
  lead: "第 7 章跟随一个快中子经历了几次碰撞。这里给出在每个阶段决定下一步是再碰撞一次还是逃逸的速率，以及这些速率叠加出的能谱。",
  html: `
<div class="step">
  <h3>计数粒子–空穴态</h3>
  <p>激子模型按受激粒子数 <i>p</i> 和空穴数 <i>h</i> 对趋向平衡的原子核分类，<i>n</i> = <i>p</i> + <i>h</i>。进入靶核的中子从 <i>p</i> = 1、<i>h</i> = 0 开始；每次碰撞增加一对。每个阶段重要的是能量在 <i>n</i> 个激子之间有多少种分配方式：即粒子–空穴态密度。</p>
  <div class="formula">ω(p,h,E) = g<sup>n</sup> (E − A<sub>p,h</sub>)<sup>n−1</sup> / (p! h! (n−1)!) ,  A<sub>p,h</sub> = max(p,h)²/g − (p² + h² + p + h)/4g</div>
  <div class="ctl"><label for="ex-n">粒子数 p（空穴数 p − 1）</label><input id="ex-n" type="range" data-bind="pp" min="2" max="6" step="1" value="3" data-instant><output data-show="pp" data-fmt="0"></output></div>
  <div class="btns"><button class="btn ghost" data-act="pauli" aria-pressed="true">泡利修正</button></div>
  <p><i>g</i> ≈ <i>A</i>/15 MeV⁻¹ 是费米能附近的单粒子能级密度。<i>A<sub>p,h</sub></i> 是<b>泡利</b>修正：两个粒子不能占据同一能级，所以最低的组态要付出能量，阈值附近的密度随之下降。曲线以其计数命名：3p2h 表示 3 个粒子、2 个空穴。示意图每次显示一个随机抽取的、粒子数为所选 <i>p</i> 的组态：每个空穴就是费米面以下缺少的一个核子。</p>
</div>
<div class="step">
  <h3>跃迁率与发射率</h3>
  <p>从每个阶段出发，可能发生两件事。一次碰撞产生另一对，速率为 λ<sup>+</sup>，按费米黄金规则，它等于矩阵元的平方乘以可到达的态密度。或者一个粒子离开，速率为 <i>W</i>，由细致平衡从逆截面以及有、无逃逸粒子时的态密度之比给出。</p>
  <div class="formula">λ<sup>+</sup>(n) = (2π/ħ) M² ω<sub>acc</sub> ,  W(p,h,ε) = (2s+1)/(π²ħ³) με σ<sub>inv</sub>(ε) ω(p−1,h,U) / ω(p,h,E)</div>
  <div class="ctl"><label for="ex-e">中子能量 (MeV)</label><input id="ex-e" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="20"><output data-show="Ein" data-fmt="1"></output></div>
  <p>每个阶段以其计数标记（2p1h：2 个粒子、1 个空穴）。柱条是每个阶段的两个速率，采用对数坐标：λ<sup>+</sup> 的量级为 10²² s⁻¹，<i>W</i> 在第一阶段约为它的十分之一，并且每过一个阶段都在下降，因为每多一对，领头粒子能携带的能量就更少。引擎采用 Koning–Duijvestijn 形式的 M²，它随每个激子的能量增大而减小：</p>
  <div class="formula">M² = (C₁ A<sub>p</sub> / A³) · [7.48 + 4.62×10⁵ / (E/(n A<sub>p</sub>) + 10.7)³]  MeV²</div>
</div>
<div class="step">
  <h3>链随时间的演化</h3>
  <p>忽略少见的、消去一对的碰撞（永不返回近似，never-come-back），布居服从一条简单的链：每个阶段由前一阶段填充，并流向下一阶段和连续区。柱条运行的就是这个主方程；时间以 10⁻²² s 为单位。</p>
  <div class="formula">dP(n)/dt = λ<sup>+</sup>(n−2) P(n−2) − [λ<sup>+</sup>(n) + W(n)] P(n)</div>
  <div class="ctl"><label for="ex-e2">中子能量 (MeV)</label><input id="ex-e2" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="20"><output data-show="Ein" data-fmt="1"></output></div>
  <p>整条链在几个 10⁻²² s 内就结束了。途中逃逸的份额就是预平衡发射；其余部分在引擎中（与 TALYS 一样）最多到六个粒子之后，交给复合核。对时间积分给每个阶段一个强度 τ(<i>n</i>)·<i>P</i>(<i>n</i>)，引擎计算的正是这个乘积。</p>
</div>
<div class="step">
  <h3>高能尾部</h3>
  <p>发射谱是各阶段的布居乘寿命乘发射率之和，再加上剩余部分的蒸发。单单 <i>n</i> = 3 这一阶段，即两个粒子加一个空穴，就能达到最高的出射能量：它的谱朝端点只是线性下降。之后的每个阶段都更软。</p>
  <div class="formula">dσ/dε = σ<sub>CN</sub> Σ<sub>n</sub> P(n) τ(n) W(n,ε) + 蒸发</div>
  <div class="ctl"><label for="ex-e3">中子能量 (MeV)</label><input id="ex-e3" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="20"><output data-show="Ein" data-fmt="1"></output></div>
  <p>提高能量，谱就变硬：预平衡尾部一直延伸到端点，而蒸发峰停留在 1 到 2 MeV。在约 10 MeV 以上，实测的高能中子只有靠这条尾部才能重现。</p>
</div>
<div class="step">
  <h3>预平衡份额</h3>
  <p>发射中属于预平衡的份额随入射能量增长，这里从 5 MeV 附近的百分之几增长到 40 MeV 时的约 40%。它取决于一个可调常数，即矩阵元的整体大小：相互作用越弱，平衡越慢，早期发射越多。</p>
  <div class="ctl"><label for="ex-c">矩阵元常数 C₁</label><input id="ex-c" type="range" data-bind="c1" min="0.3" max="3" step="0.05" value="1"><output data-show="c1" data-fmt="2"></output></div>
  <p>虚线是 C₁ = 1，即引擎的默认值；实线随滑块变化。C₁ 减半，份额增加 1.5 到 1.9 倍，而不是 2 倍：每个阶段的逃逸概率是 W/(λ<sup>+</sup> + W)，而不是 W/λ<sup>+</sup>，而且能存活到后续阶段的原子核更少。</p>
</div>
<div class="step">
  <h3>两分量，以及第二次逃逸</h3>
  <p>引擎分别追踪质子和中子（<i>p</i><sub>π</sub>、<i>h</i><sub>π</sub>、<i>p</i><sub>ν</sub>、<i>h</i><sub>ν</sub>），对同类和异类粒子对采用不同的矩阵元，对靠近表面的第一次碰撞采用较浅的势阱深度，并对集团采用 Kalbach 规则。在 20 MeV 以上，它还允许仍带有激子的剩余核在达到平衡之前再发射一个快粒子。</p>
  <div class="ctl"><label for="ex-e4">中子能量 (MeV)</label><input id="ex-e4" type="range" data-bind="Ein" min="5" max="60" step="0.5" value="20"><output data-show="Ein" data-fmt="1"></output></div>
  <p>这条曲线是它的一个玩具版本：从三激子阶段第一次发射之后，剩余核中剩下的粒子在下一次碰撞之前逃逸的概率。它在 20 MeV 以下很小，在其上增长，引擎正是在那里打开多次预平衡发射。</p>
  <div class="aside">代码位置：<code>density/particle_hole.py</code>（Williams 态密度、泡利修正和有限势阱修正，单分量与两分量），<code>preeq/exciton.py</code>（矩阵元、发射率与跃迁率、寿命、永不返回近似的解），<code>preeq/complex.py</code>（Kalbach 拾取、削裂和敲出），<code>preeq/multi.py</code>（多次预平衡，默认从 20 MeV 起）。图中是单分量模型，配以示意性的逆截面，靶核类似铁-56。</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // scene 1: state densities
  "E (MeV)": "E (MeV)",
  "ω(p, h, E) per MeV": "ω(p, h, E)，每 MeV",
  "{#}p{#}h": "{#}p{#}h",
  "dashed: no Pauli correction": "虚线：无泡利修正",
  "Fermi level": "费米能级",
  "{#} particles, {#} holes": "{#} 个粒子，{#} 个空穴",
  // scene 2: rates
  "rate (s⁻¹)": "速率 (s⁻¹)",
  "n = {#}": "n = {#}",
  "W/λ⁺ = {#}": "W/λ⁺ = {#}",
  "blue: λ⁺, the next collision · yellow: W, neutron escape": "蓝：λ⁺，下一次碰撞 · 黄：W，中子逃逸",
  "E = {#} + Sₙ = {#} MeV · τ(n={#}) = {#} × {#}⁻²² s": "E = {#} + Sₙ = {#} MeV · τ(n={#}) = {#} × {#}⁻²² s",
  // scene 3: master equation
  "compound": "复合核",
  "{#} %": "{#} %",
  "emitted before equilibrium: {#} % (of {#} % in the end)": "平衡前发射：{#} %（最终共 {#} %）",
  "t = {#} × {#}⁻²² s": "t = {#} × {#}⁻²² s",
  // scene 4: spectrum
  "outgoing neutron energy ε (MeV)": "出射中子能量 ε (MeV)",
  "dσ/dε (mb/MeV)": "dσ/dε (mb/MeV)",
  "evaporation": "蒸发",
  "ε = {#} MeV: {#} % from n = {#}": "ε = {#} MeV：{#} % 来自 n = {#}",
  "pre-equilibrium {#} % of the emission · solid: total": "预平衡占发射的 {#} % · 实线：总和",
  // scene 5: share
  "{#} MeV": "{#} MeV",
  "pre-equilibrium share of the emission": "预平衡在发射中所占份额",
  "{#} MeV: {#} %": "{#} MeV：{#} %",
  "C₁ = {#} (dashed: {#})": "C₁ = {#}（虚线：{#}）",
  // scene 6: second escape
  "{#} MeV: multiple pre-equilibrium on": "{#} MeV：开启多次预平衡",
  "chance of a second fast emission (toy estimate)": "第二次快速发射的概率（粗略估计）",
  "residual: {#}p{#}h": "剩余核：{#}p{#}h",
});
Object.assign(WT.L.glossary, {
  neverComeBack: {
    term: "永不返回近似", aliases: ["永不返回近似", "never-come-back"],
    short: "一种近似：在趋向平衡的早期，碰撞只增加粒子–空穴对，从不消去它们。",
    more: "它把主方程变成一条可以逐级积分的简单链。只要激子数远低于其平衡值，它就成立，而预平衡发射正发生在这一阶段。",
    chapter: "exciton",
  },
});
/* attributes referenced in the English chapter script (for the structure check): data-act="pauli" */
