/* Simplified Chinese: decay (chapter 6) */
WT.L.ch.decay = {
  num: "第 9 章", title: "复合核的衰变", short: "衰变",
  lead: "复合核必须通过发射一个粒子或一个光子来释放能量。本章把每一种出路画成一扇门。引擎的任务是算出通量（到达这里的反应流）中有多大份额从每扇门离开。",
  html: `
<div class="step">
  <p>每个出口一扇门：<em class="g">光子</em>（γ）、<em class="n">中子</em>（n）、<em class="p">质子</em>（p）、<em class="a">α粒子</em>（α：两个质子加两个中子），以及仅对重核开放的<em class="f">裂变</em>（一分为二）。每扇门中亮起的缝隙就是该出口的份额，小球也以同样的比例涌出；灰色的门是关闭的。由于已经忘记了自己的形成方式，原子核按一个权重成比例地使用每扇门 b：</p>
  <div class="formula">份额<sub>b</sub> = T<sub>b</sub> · ρ<sub>b</sub> / Σ<sub>c</sub> T<sub>c</sub> · ρ<sub>c</sub></div>
  <p><b>穿透系数</b> <i>T</i> 是到达边缘的粒子能够穿出的概率；对粒子而言，它来自第 5 章的光学模型，只是反过来运行。写在每扇门旁的<b>能级密度</b> ρ 计算剩余核最终可以处于的状态数。按 <i>T</i> 乘以 ρ 分配份额，就是 <b>Hauser–Feshbach</b> 规则。在 10 MeV 时，中子之门几乎包揽一切。</p>
</div>
<div class="step">
  <h3>蒸发谱</h3>
  <p>中子之门按出射能量 ε 分开（左慢右快）。每扇门的缝隙 <i>T</i>(ε) 对更快的中子更宽。门下方是剩余核可以处于的众多状态：慢中子把大部分能量留在核内，那里状态极多，所以这些状态群向右逐渐缩小。</p>
  <div class="ctl"><label for="dc-sp">剩余能量</label><input id="dc-sp" type="range" data-bind="spare" min="1" max="12" step="0.5" value="5"><output data-show="spare" data-fmt="1"></output></div>
  <p>门 × 状态数，使堆积形成一个驼峰，即<b>蒸发谱</b>，就像热液体中逸出的蒸汽。拖动剩余能量（单位 MeV，即百万电子伏特）：堆积重新开始，而峰值始终停在 1 MeV 附近，由核温度决定。多出来的能量主要使剩余核更热。</p>
</div>
<div class="step">
  <h3>发射中的库仑势垒</h3>
  <p>质子在距中心不同距离 r 处的能量：内部是一个势阱，外部是由电（库仑）排斥形成的山丘，按 1/r 减弱。在山顶以下，在势阱中来回碰撞的质子只能通过<b>隧穿效应</b>穿过阴影部分，这是一种量子效应，要撞击壁很多次才成功一次。几率的算法与第 4 章相同：这一段越宽越高，“10<sup>N</sup> 次撞击中有 1 次”里的零就越多。</p>
  <div class="ctl"><label for="dc-ce">粒子能量</label><input id="dc-ce" type="range" data-bind="eps" min="0.5" max="12" step="0.1" value="3"><output data-show="eps" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="toggleAlpha">切换质子 / α</button></div>
  <p>把能量调低，看隧道如何变宽；然后切换到 α 粒子，它带两个电荷，面对的山丘约高一倍。这就是为什么不带电的中子一旦能够离开，通常就胜出，而质子和 α 出口主要在轻核和高能量时才重要。</p>
</div>
<div class="step">
  <h3>反应道阈值</h3>
  <p>每扇粒子之门只有在其<b>分离能</b>之上才会打开，分离能就是把该粒子拉出所需的代价：这里中子为 8 MeV，质子为 9 MeV，α 为 7 MeV。在中子的 8 MeV 以下，几乎每次衰变都发光。</p>
  <div class="ctl"><label for="dc-e">激发能</label><input id="dc-e" type="range" data-bind="E" min="5" max="24" step="0.1" value="7"><output data-show="E" data-fmt="1"></output></div>
  <p>把激发能拖过 8 MeV。在大约 1 MeV 之内，中子之门大开，光子份额下降到百分之一。α 之门最先解锁，在 7 MeV，却几乎打不开：它的库仑山丘（第 4 章）使它直到能量高出很多时仍几乎关着。质子之门在 9 MeV 解锁，同样一直很窄，被它自己的山丘所阻挡。</p>
</div>
<div class="step">
  <h3>角动量与宇称守恒</h3>
  <p>复合核（上方）的自旋为 <i>J</i>；剩余核的状态在下方按自旋 <i>J</i>′ 放在不同的抽屉里。中子带走自旋和宇称的差别：以轨道角动量 <i>l</i> 离开时，它最多改变自旋 <i>l</i> + ½，并在 <i>l</i> 为奇数时翻转宇称。<i>l</i> 越大，门越窄；每个抽屉的门对应能到达它的最小 <i>l</i>。实心落点保持宇称；空心落点翻转宇称。</p>
  <div class="ctl"><label for="dc-j">复合核自旋 J</label><input id="dc-j" type="range" data-bind="J" min="0" max="10" step="1" value="2" data-instant><output id="dc-jout">5/2</output></div>
  <p>把 <i>J</i> 调高。打开的门移向高自旋抽屉，而那里的状态很少，装满状态的抽屉则被关在门后。高自旋复合核发射粒子很慢，这就给了光子和同质异能态（长寿命状态，第 10 章）机会。</p>
</div>
<div class="step">
  <h3>弹性增强</h3>
  <p>在低能量下，复合核是一组尖锐的<b>共振</b>，即中子很容易被吸收的能量；这里画出八个，每行一个。每个共振的门宽都是随机的：左边是入口（中子道），宽度为 <i>x</i>；右边是其他门（这里主要是光子），宽度为 <i>y</i>。</p>
  <div class="btns"><button class="btn" data-act="fire">发射 40 个中子</button><button class="btn ghost" data-act="reroll">新的共振</button></div>
  <p>按“发射”，跟踪中子。中子进入某一行的概率正比于该行的入口宽度 <i>x</i>。进入之后，它按各宽度的比例选择出路：以概率 <i>x</i> / (<i>x</i> + Σ<i>y</i>) 从入口退回，否则从其他某个门离开。托盘记录它们去了哪里。</p>
  <p>关键在于：入口宽的那一行进入的中子更多，送回的中子也更多。所以回来的比单凭平均宽度所猜测的要多。真实的返回份额（<b>乘积的平均</b>）超过简单估计（<b>平均的乘积</b>）；两者都写在顶部。</p>
  <p>它们的比值就是<b>弹性增强</b>。引擎的<b>宽度涨落修正</b>应用了它：把这部分额外的通量从其他门移回入口。</p>
  <div class="ctl"><label for="dc-n">其他门</label><input id="dc-n" type="range" data-bind="Nch" min="1" max="12" step="1" value="2" data-instant><output data-show="Nch" data-fmt="0"></output></div>
  <p>增加门的数目。出口很多时，它们的总宽度不再涨落，所以这一修正主要在开放的门很少时才重要。引擎用 Moldauer 公式，对能量不超过靶核中子分离能的入射中子施加这一修正，更高能量则不加。</p>
</div>
<div class="step">
  <h3>直接反应之后的通量</h3>
  <p>本章的门只分配真正留下来的中子。第 6 章和第 7 章已经分走了它们的一份：有些中子只擦边撞一下就飞走（直接反应），有些碰撞一两次后快速射出（预平衡）。只有其余的留在里面加热原子核。右侧的计数器记录每一种结局；留下来的永远不会离开原子核，只是被计数。</p>
  <div class="ctl"><label for="dc-einc">中子能量</label><input id="dc-einc" type="range" data-bind="Einc" min="1" max="30" step="0.5" value="8"><output data-show="Einc" data-fmt="1"></output></div>
  <p>只有留下的中子才参加门之间的竞争。拖动中子能量：在几 MeV 时几乎全部留下；到 30 MeV 时，约有一半在达到平衡之前就已离开。</p>
  <div class="aside">代码位置：<code>compound/prepare.py</code>（按自旋和宇称的出口权重 T·ρ、选择定则），<code>compound/target.py</code>（含宽度涨落的首次衰变），<code>compound/continuum.py</code>（之后每个能量区间的衰变），<code>compound/wfc.py</code>（Moldauer、HRTW、GOE 修正），<code>compound/normalization.py</code>（留给复合核的通量），<code>omp/inverse.py</code>（反向运行的门）。</div>
</div>`,
};
(function () {
  const L = {
    "{#} MeV": "{#} MeV",
    "n": "n", "p": "p", "fission": "裂变",
    "heavy only": "仅重核",
    "heavy nuclei only": "仅限重核",
    "shut below {#} MeV": "{#} MeV 以下关闭",
    "the neutron door takes nearly everything": "中子之门几乎包揽一切",
    "below the neutron threshold, nearly all decays emit light": "低于中子阈能，几乎全部衰变发光",
    "the doors share the decays": "各门分担衰变",
    // hump
    "{#} MeV to spare": "剩余 {#} MeV",
    "door gap = T(ε)": "门缝 = T(ε)",
    "doors: one per neutron energy ε, gap = T(ε)": "门：每个中子能量 ε 一扇，缝 = T(ε)",
    "× states left behind": "× 剩余状态",
    "× states the leftover nucleus can be in: many after a slow neutron": "× 剩余核可处的状态：慢中子之后很多",
    "most ≈ {#} MeV": "峰值 ≈ {#} MeV",
    "= the pile": "= 堆积",
    "= where the neutrons land: the evaporation spectrum": "= 中子的落点：蒸发谱",
    "slow": "慢",
    "slow neutrons": "慢中子",
    "fast: {#} MeV →": "快：{#} MeV →",
    "fast: {#} MeV (beyond, up to {#}, almost none)": "快：{#} MeV（此后直到 {#}，几乎没有）",
    "fast: {#}": "快：{#}",
    "fast: {#} MeV, the neutron takes it all": "快：{#} MeV，中子带走全部",
    // coulomb
    "well ↓": "势阱 ↓",
    "well (much deeper) ↓": "势阱（深得多）↓",
    "hilltop ≈ {#} MeV": "山顶 ≈ {#} MeV",
    "falls as {#}/r": "按 {#}/r 下降",
    "Coulomb hill, falling as {#}/r": "库仑山丘，按 {#}/r 下降",
    "tunnel: wider than the picture": "隧道：比画面还宽",
    "tunnel {#} fm": "隧道 {#} fm",
    "proton energy {#} MeV": "质子能量 {#} MeV",
    "alpha energy {#} MeV": "α 能量 {#} MeV",
    "proton energy {#} MeV ↑": "质子能量 {#} MeV ↑",
    "alpha energy {#} MeV ↑": "α 能量 {#} MeV ↑",
    "above the hilltop: it rolls straight out": "高于山顶：直接滚出",
    "below the top, must tunnel: nearly every knock gets through": "低于山顶需隧穿：几乎每次撞击都能穿过",
    "below the top, must tunnel: about {#} knock in {#} gets through": "低于山顶需隧穿：约 {#}/{#} 的撞击能穿过",
    "below the top, must tunnel: about {#} knock in {#} × {#}^{#} gets through": "低于山顶需隧穿：约 {#}/({#} × {#}^{#}) 的撞击能穿过",
    "out": "出射",
    "through after {#} knock": "撞击 {#} 次后穿出",
    "through after {#} knocks": "撞击 {#} 次后穿出",
    "knocks so far: {#}": "已撞击：{#} 次",
    "distance r from the centre (fm) →": "到中心的距离 r（fm）→",
    // spin
    "J = {#}/{#}, parity +": "J = {#}/{#}，宇称 +",
    "l={#}": "l={#}",
    "leftover states by spin J′ →": "按自旋 J′ 的剩余状态 →",
    "drawers: states of the leftover nucleus by spin J′ (faint: states it holds) →": "抽屉：剩余核按自旋 J′ 的状态（淡色：所含状态）→",
    "open doors reach {#} %": "开放的门到达 {#} %",
    "open doors reach about {#} % of the states": "开放的门到达约 {#} % 的状态",
    "● parity kept (even l)   ○ flipped (odd l)": "● 宇称不变（l 偶）   ○ 翻转（l 奇）",
    // wfc
    "entrance x": "入口 x",
    "entrance, width x": "入口，宽度 x",
    "{#} other doors, y": "{#} 扇其他门，y",
    "{#} other door, widths y": "{#} 扇其他门，宽度 y",
    "{#} other doors, widths y": "{#} 扇其他门，宽度 y",
    "back out the entrance: {#} of {#}": "从入口返回：{#}/{#}",
    "out another door: {#}": "从其他门离开：{#}",
    // norm
    "absorbed neutrons, {#} MeV →": "被吸收的中子，{#} MeV →",
    "direct: {#} %": "直接：{#} %",
    "pre-equilibrium: {#} %": "预平衡：{#} %",
    "compound nucleus: {#} %": "复合核：{#} %",
    "one glancing hit on the surface": "在表面擦边撞一下",
    "a knock or two, then out fast": "碰撞一两次，然后快速射出",
    "stayed: on to the door competition": "留下：参加门的竞争",
  };
  // door hint with level-count wording (fmt: "1", "N", "N thousand", "N million") and T possibly in e-notation
  const cnt = [["{#} state", "{#} 个状态"], ["{#} states", "{#} 个状态"], ["{#} thousand states", "{#} 千个状态"], ["{#} million states", "{#} 百万个状态"]];
  for (const [e, s] of cnt) {
    L[`weak door × ≈ ${e}`] = `弱门 × ≈ ${s}`;
    L[`T ≈ {#} × ≈ ${e}`] = `T ≈ {#} × ≈ ${s}`;
    L[`T ≈ {#}e{#} × ≈ ${e}`] = `T ≈ {#}e{#} × ≈ ${s}`;
  }
  // share comparisons: each pct is "{#} %" or "≈ {#} %"
  const P = ["{#} %", "≈ {#} %"];
  for (const a of P) for (const b of P) {
    L[`back out ${a}, not ${b}: × {#}`] = `返回 ${a}，而非 ${b}：× {#}`;
    L[`share back out: average of products ${a} · product of averages ${b} · × {#}`] = `返回份额：乘积的平均 ${a} · 平均的乘积 ${b} · × {#}`;
    L[`other doors ${a}, not ${b}`] = `其他门 ${a}，而非 ${b}`;
    L[`other doors together: ${a} instead of ${b}`] = `其他门合计：${a}，而非 ${b}`;
  }
  Object.assign(WT.L.labels, L);
})();
