/* Simplified Chinese: direct (第 6 章，直接反应) */
WT.L.ch.direct = {
  num: "第 6 章", title: "直接反应", short: "直接反应",
  lead: "并不是每个到达原子核的中子都会被吞没。有些只擦过它的表面，推它一下，然后继续飞走。",
  html: `
<div class="step">
  <p>只擦过原子核的中子可以推它一下，使它跃迁到某个激发能级，然后继续飞行，大多朝前方，速度只慢了一点。这就是<b>直接反应</b>：一步完成，历时约 10⁻²² 秒。图中一个中子在距离 <i>b</i> 处飞过，这个距离称为<b>碰撞参数</b>，以原子核半径 <i>R</i> 为单位；点线圆是原子核的表皮。</p>
  <div class="ctl"><label for="di-b">瞄准距离 b（以半径计）</label><input id="di-b" type="range" data-bind="b" min="0" max="1.5" step="0.01" value="1.0"><output data-show="b" data-fmt="2"></output></div>
  <p>拖动 <i>b</i>。小于约 0.8 时中子被吞没。接近 1 时它擦边而过，使原子核处于第一激发能级 2⁺。大于约 1.2 时它错过原子核，只是偏转：这是<b>弹性散射</b>，原子核没有变化。</p>
</div>
<div class="step">
  <h3>变形核的转动激发</h3>
  <p>推一下就能让拉长的原子核（第 1 章）转动起来，沿着它的<b>转动带</b>逐级上升：0⁺、2⁺、4⁺、6⁺、8⁺。中子能把原子核推上去，原子核也能反推回来，所以任何一个能级都无法单独求解。程序把它们一起求解：这就是<b>耦合道</b>方法，每个反应道对应一种结局，这里就是转动带中的一个能级。</p>
  <div class="btns"><button class="btn" data-act="kick">推上一级</button><button class="btn ghost" data-act="rpause">暂停 / 继续</button></div>
  <div class="ctl"><label for="di-beta">形变 β₂</label><input id="di-beta" type="range" data-bind="beta2" min="0.05" max="0.4" step="0.01" value="0.25"><output data-show="beta2" data-fmt="2"></output></div>
  <p>弧线表示哪些能级相互耦合：<i>λ</i> = 2 是整体拉伸，连接相邻能级；<i>λ</i> = 4 是更精细的隆起，跨越两级。拖动 <i>β₂</i>：原子核拉得越长，能级之间的耦合越强，弧线越粗。由于转动带是与入射中子一起求出的，引擎确切知道它要吸收多少中子，并且只把其余的中子交给后面几章中较慢的途径。</p>
</div>
<div class="step">
  <h3>表面振动</h3>
  <p>球形原子核可以振动，振动能量以相等的能量包出现，称为<b>声子</b>。橄榄球形与圆盘形之间的振动（<i>λ</i> = 2）的一个声子给出 2⁺ 能级；两个声子给出 0⁺、2⁺ 和 4⁺ 三个能级，能量为前者的两倍。要到达这些能级需要连推两下。程序把这些能级与基态一起求解。</p>
  <div class="ctl"><label for="di-lam">振动形状 λ</label><input id="di-lam" type="range" data-bind="lam" min="2" max="3" step="1" value="2" data-instant><output data-show="lam" data-fmt="0"></output></div>
  <div class="btns"><button class="btn ghost" data-act="ph1">一个声子</button><button class="btn ghost" data-act="ph2">两个声子</button></div>
  <p>设 <i>λ</i> = 3 得到梨形振动，其第一个能级是 3⁻。点按钮可加入一个或两个声子。</p>
</div>
<div class="step">
  <h3>单步直接反应</h3>
  <p>对大多数能级来说耦合很弱，推一次就够了：这就是 <b>DWBA</b>（扭曲波玻恩近似）。第 5 章的入射波在边缘处推原子核一次，那里的势从很深降到零；波峰撞击之处边缘会发光。向外扩散的圆形波，就是使原子核留在激发态后离开的中子。</p>
  <div class="ctl"><label for="di-bd">能级的形变 β</label><input id="di-bd" type="range" data-bind="bd" min="0.02" max="0.4" step="0.01" value="0.2"><output data-show="bd" data-fmt="2"></output></div>
  <p>拖动 <i>β</i>：边缘晃动得更厉害，圆圈也更亮，强度正比于 <i>β</i>²：形变加倍，散射的中子变为四倍。程序从实测值中获取每个能级的 <i>β</i>，没有实测值时则取自系统学。散射中子的角分布是可选的附加输出。</p>
</div>
<div class="step">
  <h3>巨共振</h3>
  <p>所有核子可以一起运动：呼吸式胀缩、压扁和拉长，或摆成梨形。这些就是<b>巨共振</b>。在这个中等质量的原子核中，它们位于约 7 到 25 MeV 处，每个宽达数 MeV，宽得无法算作一个能级；图中的峰标出了每个巨共振的<b>激发能</b>。</p>
  <p>程序根据<b>求和规则</b>确定每个巨共振的总强度（这是由基本物理给出的原子核响应强度上限），并把它铺成最后一个已知能级之上的一个峰。这些峰加上推向高能级的激发，构成了<b>集体连续区</b>。</p>
  <div class="btns"><button class="btn ghost" data-act="mono">呼吸</button><button class="btn ghost" data-act="quad">压扁</button><button class="btn ghost" data-act="oct">梨形</button></div>
  <p>最著名的一个是质子相对于中子来回振荡（巨偶极共振），它主要吸收和发射光，因此留到第 10 章再讲。</p>
</div>
<div class="step">
  <h3>直接俘获</h3>
  <p>一个自由中子可以直接落入势阱中一个空的<b>轨道</b>（单个中子在核内允许具有的能量），并把多余的能量以<em class="g">光子</em>形式放出。原子核根本没有被加热。这就是<b>直接俘获</b>。程序可以用第 5 章的同一个势阱来计算它：外面是自由波，里面是束缚轨道，光子把两者联系起来。这一计算是可选的，默认关闭。</p>
  <div class="btns"><button class="btn" data-act="drop">放入一个中子</button></div>
  <p>当通常的途径（分享中子的能量）很弱时，直接俘获最为重要：例如轻核和远离稳定线的原子核，它们的能级少且间隔大。</p>
</div>
<div class="step">
  <h3>直接反应与复合核通量</h3>
  <p>程序按顺序分配第 5 章的反应截面：先是直接反应，再是快速碰撞，剩下的部分才形成复合核。图中每个中子都会遇到三种命运之一：<b>直接</b>（擦边后飞走）、快速（在能量扩散之前打出一个核子：<b>预平衡</b>，第 7 章）或被吞没（形成<b>复合核</b>，第 8 章）。各堆分别计数。</p>
  <div class="ctl"><label for="di-e">中子能量 (MeV)</label><input id="di-e" type="range" data-bind="E" min="1" max="60" step="0.5" value="14"><output data-show="E" data-fmt="1"></output></div>
  <p>拖动能量，看各堆重新累积。在几 MeV 时几乎每个中子都被吞没。在几十 MeV 时，直接反应和快速碰撞合起来占了很大一部分。</p>
  <div class="aside">代码位置：<code>ecis/formfactor.py</code>、<code>ecis/coupling.py</code>、<code>ecis/solver.py</code>（形变势，转动核和振动核的耦合道），<code>ecis/dwba.py</code> 和 <code>direct/dwba.py</code>（单次推动、巨共振、集体连续区），<code>direct/racapcalc.py</code>（直接俘获，可选，默认关闭），<code>compound/normalization.py</code>（总账）。</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // scene: aim
  "skin (surface)": "表皮（表面）",
  "b = {#} R": "b = {#} R",
  "absorbed: its energy is shared by all nucleons": "被吸收：能量由所有核子分享",
  "{#}⁺ level": "{#}⁺ 能级",
  "one push leaves the nucleus on {#}⁺; neutron flies on": "推一下使原子核处于 {#}⁺；中子继续飞行",
  "a miss: deflected, nucleus unchanged (elastic)": "错过：偏转，原子核不变（弹性）",
  // scene: rotor
  "at rest: {#}⁺": "静止：{#}⁺",
  "rotating: {#}⁺": "转动：{#}⁺",
  "rotating: {#}⁺ (paused)": "转动：{#}⁺（暂停）",
  "λ = {#}": "λ = {#}",
  "levels solved together": "能级一起求解",
  // scene: vibrator
  "quadrupole ripple: football ↔ disc": "四极振动：橄榄球 ↔ 圆盘",
  "octupole ripple: pear ↔ pear": "八极振动：梨形 ↔ 梨形",
  "{#}⁺  no phonon": "{#}⁺  无声子",
  "{#}⁺  one phonon": "{#}⁺  一个声子",
  "{#}⁻  one phonon": "{#}⁻  一个声子",
  "{#}⁺ {#}⁺ {#}⁺  two phonons": "{#}⁺ {#}⁺ {#}⁺  两个声子",
  "{#}⁺ {#}⁺ {#}⁺ {#}⁺  two phonons": "{#}⁺ {#}⁺ {#}⁺ {#}⁺  两个声子",
  "one push": "推一下",
  "two pushes": "推两下",
  "two phonons": "两个声子",
  "equal energy steps": "等间距能量台阶",
  // scene: DWBA
  "rim: the push happens here": "边缘：推动发生在这里",
  "incoming wave": "入射波",
  "outgoing: nucleus left excited": "出射：原子核留在激发态",
  "outgoing circles: the nucleus left on an excited level": "出射圆波：原子核留在激发能级",
  "push strength ∝ β²: {#}× that at β = {#}": "推动强度 ∝ β²：{#}×（相对 β = {#}）",
  // scene: giant resonances
  "breathing": "呼吸",
  "squash and stretch": "压扁与拉长",
  "pear": "梨形",
  "breathing (monopole)": "呼吸（单极）",
  "squash and stretch (quadrupole)": "压扁与拉长（四极）",
  "pear-shaped (octupole), low and high": "梨形（八极），低能与高能",
  "about {#} MeV up": "约 {#} MeV 处",
  "last known level": "最后一个已知能级",
  "excitation energy (MeV) →": "激发能 (MeV) →",
  // scene: direct capture
  "free: outside the nucleus": "自由：在原子核外",
  "empty orbit": "空轨道",
  "drops straight in; a photon carries off the spare energy": "直接落入；光子带走多余能量",
  // scene: ledger
  "direct": "直接",
  "fast (pre-eq.)": "快速（预平衡）",
  "compound": "复合核",
  "direct: grazed, flew on": "直接：擦过后飞走",
  "fast collision: one out at once": "快速碰撞：立即打出一个",
  "compound: swallowed": "复合核：被吞没",
  "{#}% (model {#}%)": "{#}%（模型 {#}%）",
  "{#}% seen · model {#}%": "观测 {#}% · 模型 {#}%",
  "{#} MeV neutrons on a medium-mass nucleus (illustrative shares)": "{#} MeV 中子轰击中等质量原子核（示意比例）",
});
