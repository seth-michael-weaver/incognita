/* Simplified Chinese: structure (第 1 章，原子核由什么构成) */
WT.L.ch.structure = {
  num: "第 1 章", title: "原子核由什么构成", short: "结构",
  lead: "在程序（我们的核反应软件）发射第一个中子之前，它需要先描述靶核：它结合得有多紧，可以处于哪些能量状态，以及它是什么形状。",
  html: `
<div class="step">
  <p>图中是一个铁原子核：一个由<em class="p">质子</em>和<em class="n">中子</em>（统称<b>核子</b>）紧密堆成的球，由短程的<b>强相互作用</b>束缚在一起。每个核子只感受到最近的邻居，所以每个原子核的密度都大致相同。</p>
  <div class="ctl"><label for="st-n">中子数（铁有 26 个质子）</label><input id="st-n" type="range" data-bind="N" min="24" max="38" step="1" value="30" data-instant><output data-show="N" data-fmt="0"></output></div>
  <p>拖动滑块增减中子；每一种选择都是一种不同的<b>同位素</b>。柱条显示以 MeV（百万电子伏特）为单位的每核子<b>结合能</b>：即把原子核拆散所需的能量。它在稳定同位素附近达到峰值。</p>
</div>
<div class="step">
  <h3>分离能</h3>
  <p>取出一个粒子所需的能量是它的<b>分离能</b>：中子为 <i>S<sub>n</sub></i>，质子为 <i>S<sub>p</sub></i>，<b>α粒子</b>（两个质子和两个中子结合在一起）为 <i>S<sub>α</sub></i>。图中把原子核画成一个势阱，能量向上增加；每次拉动都把最上面的粒子拉出，越过虚线“自由”线，仪表记录所付出的代价。</p>
  <div class="btns"><button class="btn ghost" data-act="pn">拉出一个中子</button><button class="btn ghost" data-act="pp">拉出一个质子</button><button class="btn ghost" data-act="pa">拉出一个 α</button></div>
  <p>程序用两个原子核质量之差求得每个分离能：能用实测值时用实测值，否则用质量模型。</p>
  <div class="ctl"><label for="st-n2">中子数</label><input id="st-n2" type="range" data-bind="N" min="24" max="38" step="1" value="30" data-instant><output data-show="N" data-fmt="0"></output></div>
  <p>拖动中子数，再拉出一个中子：<i>S<sub>n</sub></i> 呈锯齿状变化，因为核子会配对，偶数个时最后一个被束缚得更紧。只有带来足够能量支付这一代价，反应才能放出一个粒子。这些代价就是整个计算的<b>阈能</b>。</p>
</div>
<div class="step">
  <h3>激发态与 γ 衰变</h3>
  <p>原子核只能容纳某些确定数值的额外能量：图中的横线（这里是铁-56），最底部是<b>基态</b>。每个能级有一个<b>自旋</b> <i>J</i>（角动量）和一个<b>宇称</b>，+ 或 −（它的波在镜中是否看起来一样）；2<sup>+</sup> 表示自旋 2、宇称 +。</p>
  <p>橙色小球是处于高能级的原子核。它一次下降一个能级，每一跳放出一个带走能量差的<em class="g">光子</em>（γ射线）。路径的宽度和百分比是每一跳的实测概率，即<b>分支比</b>。</p>
  <div class="btns"><button class="btn" data-act="drop">激发原子核</button></div>
  <p>多按几次：同一个能级会经由不同路径到达基态。程序为每个原子核保留约三十个实测能级及其分支比；更高处则把密集的能级当作平滑的<b>连续区</b>处理。在虚线 <i>S<sub>n</sub></i> 之上，原子核可以发射中子。</p>
</div>
<div class="step">
  <h3>同质异能态：长寿命的激发态</h3>
  <p>如果一个能级唯一的退激途径需要很大的自旋变化 Δ<i>J</i>，它衰变得就非常慢。右边有 64 个原子核处在这样的能级上；每个都等待一段随机的时间，然后跃迁下来，放出一个<em class="g">光子</em>。经过一个<b>半衰期</b>后，一半已经跃迁。</p>
  <div class="ctl"><label for="st-dj">自旋变化 ΔJ</label><input id="st-dj" type="range" data-bind="dJ" min="1" max="5" step="1" value="2" data-instant><output data-show="dJ" data-fmt="0"></output></div>
  <div class="ctl"><label for="st-eg">光子能量 (MeV)</label><input id="st-eg" type="range" data-bind="Eg" min="0.05" max="1.5" step="0.05" value="0.3"><output data-show="Eg" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="excite">全部激发</button></div>
  <p>增大 Δ<i>J</i>，放出光子的速度就变慢：自旋每多一个单位，等待时间就延长十万倍甚至更多；光子能量越低，等待也越长（以对数坐标显示）。寿命超过约一秒的能级称为<b>同质异能态</b>，程序把它当作终点，与基态同等对待。</p>
</div>
<div class="step">
  <h3>原子核的形变</h3>
  <p>许多原子核并不是圆的。<i>β₂</i>（读作“贝塔二”）衡量拉伸程度：0 是球形，正值像橄榄球那样被拉长，负值被压扁成圆盘。右边的梯子显示每种形状产生的能级。</p>
  <p>拉长的原子核可以转动，产生 0<sup>+</sup>、2<sup>+</sup>、4<sup>+</sup>、6<sup>+</sup> 能级，间距按 <i>J</i>(<i>J</i>+1) 增大：这是<b>转动核</b>。球形原子核可以振动；每一份振动能量即一个<b>声子</b>，增加相同的能量，所以能级等间距排列：这是<b>振动核</b>。</p>
  <div class="ctl"><label for="st-beta">形变 β₂</label><input id="st-beta" type="range" data-bind="beta" min="-0.3" max="0.45" step="0.01" value="0.28"><output data-show="beta" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="still">静止</button><button class="btn ghost" data-act="vib">振动</button><button class="btn ghost" data-act="rot">转动</button></div>
  <p>拖动 <i>β₂</i> 并按按钮：拉伸越大，转动核的能级越靠拢。振动核平均而言是圆的，所以它起伏时滑块保持不动；而球在这个意义上不能转动（转动它没有任何变化），所以在 <i>β₂</i> = 0 附近，转动带消失。程序为每个原子核存储形变值和一个标签：球形、振动核或转动核。第 6 章展示了经过的中子如何利用它们。</p>
</div>
<div class="step">
  <h3>中子阈以上的共振参数</h3>
  <p>加入靶核的慢中子落在略高于 <i>S<sub>n</sub></i> 的地方，即左边的小方框里。右边的面板把这个方框放大了数千倍，中子能量从左到右增加。</p>
  <div class="ctl"><label for="st-fe">束流能量</label><input id="st-fe" type="range" data-bind="fe" min="0" max="1" step="0.001" value="0.3" data-instant><output id="st-fe-out"></output></div>
  <div class="btns"><button class="btn ghost" data-act="fplay" id="st-fplay">暂停扫描</button></div>
  <p>在大多数能量下，束流径直穿过。在某些确定的能量下，中子加原子核恰好对应一个隐藏的能级，束流的大部分被吸收：这就是<b>共振</b>。在峰上，画出的原子核会膨胀：这并不是尺寸真的变了，而是中子的波与原子核的波重叠时，中子实际“看到”的靶变大了。随后原子核以<em class="g">光子</em>或中子的形式把能量放出。曲线表示被吸收的份额；竖条标出找到的每个共振。</p>
  <div class="btns"><button class="btn ghost" data-act="fFe">铁-56</button><button class="btn ghost" data-act="fAu">金-197</button><button class="btn ghost" data-act="fU">铀-238</button></div>
  <p>每个原子核都有自己的条形码，尺度各不相同：铁的共振之间相隔数千电子伏特，金和铀只有几十电子伏特。三个平均量可以概括它：<i>D₀</i>，平均间距；⟨Γ<sub>γ</sub>⟩，<b>光子宽度</b>，对每个峰几乎相同；<i>S₀</i>，<b>强度函数</b>，表示慢中子进入的难易程度。</p>
  <p>每个量都用来检验后面的一步。程序的能级密度参数是逐个原子核拟合 <i>D₀</i> 得到的；⟨Γ<sub>γ</sub>⟩ 检验光子发射，<i>S₀</i> 检验下一章的光学模型。对于没有测量值的原子核，程序使用对大量原子核拟合出的趋势。</p>
  <div class="aside">代码位置：<code>structure/masses.py</code>（实测质量、实测范围之外的模型质量、分离能），<code>structure/levels.py</code>（分立能级、分支比、同质异能态、推测的自旋）和 <code>levjpar.py</code>（可选，默认关闭：重新推测对该原子核不可能出现的已列自旋），<code>structure/deformation.py</code>（β₂ 及球形/振动核/转动核标签）和 <code>collrule.py</code>（可选，默认关闭：根据靶核的实测能级选取其标签），<code>structure/resonances.py</code>（D₀、S₀、S₁、⟨Γγ⟩）。</div>
</div>`,
};
(function () {
  const L = {
    // scene: packed drop
    "{#}Fe": "{#}Fe",
    "{#} protons · {#} neutrons": "{#} 个质子 · {#} 个中子",
    "binding energy per nucleon: about {#} MeV": "每核子结合能：约 {#} MeV",
    "binding per nucleon, one bar per isotope →": "每核子结合能，每个同位素一根柱 →",
    // scene: well
    "free": "自由",
    "free: outside the nucleus": "自由：在原子核外",
    "neutrons": "中子",
    "protons": "质子",
    "an alpha forms from the top pairs": "顶部的核子对组成一个 α",
    "neutron {#}": "中子 {#}",
    "proton {#}": "质子 {#}",
    "alpha {#}": "α {#}",
    "n {#}": "n {#}",
    "p {#}": "p {#}",
    "energy paid": "付出的能量",
    "energy to pull": "拉出所需能量",
    "(MeV)": "(MeV)",
    "each one out (MeV)": "每个拉出 (MeV)",
    "higher mark =": "标记越高 =",
    "harder to remove": "越难取出",
    "pulling out a neutron: {#} MeV paid": "拉出一个中子：付出 {#} MeV",
    "pulling out a proton: {#} MeV paid": "拉出一个质子：付出 {#} MeV",
    "pulling out an alpha: {#} MeV paid": "拉出一个 α：付出 {#} MeV",
    // scene: levels and gamma drops
    "continuum: too many levels to list": "连续区：能级多得无法列出",
    "neutron threshold Sₙ ≈ {#} MeV": "中子阈能 Sₙ ≈ {#} MeV",
    "ground state": "基态",
    "MeV": "MeV",
    "each line: an energy, a spin J and a parity (±)": "每条线：一个能量、自旋 J 和宇称 (±)",
    "path width and % = measured odds of each hop": "路径宽度和 % = 每一跳的实测概率",
    // scene: isomer
    "ground": "基态",
    "J = {#}/{#}": "J = {#}/{#}",
    "ΔJ = {#}": "ΔJ = {#}",
    "still excited: {#} of {#}": "仍处激发态：{#}/{#}",
    "longer than a second: an isomer, a stop in its own right": "超过一秒：同质异能态，本身就是一个终点",
    "shown slowed down (log scale)": "慢放显示（对数坐标）",
    "shown slowed down: the slower they pop, the longer the real wait (log scale)": "慢放显示：放出越慢，实际等待越长（对数坐标）",
    // scene: shape
    "ripples at the surface: a vibrator": "表面振动：振动核",
    "stretched and rotating: a rotor": "拉长并转动：转动核",
    "round: a sphere": "圆的：球形",
    "stretched (prolate): a football": "拉长（长椭球）：橄榄球",
    "squashed: an oblate disc": "压扁：扁椭球圆盘",
    "{#} phonons": "{#} 个声子",
    "no regular": "没有规则的",
    "level pattern": "能级图样",
    "spacing grows like J(J+{#})": "间距按 J(J+{#}) 增大",
    "equal steps, one phonon each": "等间距，每级一个声子",
    "its lowest levels": "最低的几个能级",
    "β₂ = {#}": "β₂ = {#}",
    // scene: resonance fingerprint
    "continuum": "连续区",
    "Sₙ ≈ {#} MeV": "Sₙ ≈ {#} MeV",
    "slow neutron": "慢中子",
    "a slow neutron lands here:": "慢中子落在这里：",
    "lands here": "落在这里",
    "Sₙ + its kinetic energy": "Sₙ + 中子动能",
    "×{#} million": "×{#} 百万",
    "×{#} thousand": "×{#} 千",
    "magnified": "放大",
    "swells on a peak: the size the neutron effectively “sees” (waves overlap), not a real size change": "在峰上膨胀：这是中子实际“看到”的大小（波相互重叠），并非尺寸真的改变",
    "share taken in": "吸收份额",
    "share of the beam taken in": "束流被吸收的份额",
    "{#} (Sₙ)": "{#} (Sₙ)",
    "{#} = exactly Sₙ": "{#} = 恰为 Sₙ",
    "{#} keV": "{#} keV",
    "{#} eV": "{#} eV",
    "neutron energy →": "中子能量 →",
    "neutron's kinetic energy →": "中子动能 →",
    "D₀ ≈ {#} keV: the average gap": "D₀ ≈ {#} keV：平均间距",
    "D₀ ≈ {#} eV: the average gap": "D₀ ≈ {#} eV：平均间距",
    "S₀: average peak strength": "S₀：峰的平均强度",
    "S₀: how strong the peaks are on average (how easily a neutron gets in)": "S₀：峰的平均强度（中子进入的难易程度）",
    "⟨Γγ⟩ ≈ {#} eV: photon width": "⟨Γγ⟩ ≈ {#} eV：光子宽度",
    "⟨Γγ⟩ ≈ {#} eV: photon width, about the same for every peak": "⟨Γγ⟩ ≈ {#} eV：光子宽度，各峰几乎相同",
    "⟨Γγ⟩ ≈ {#} eV: a hairline here": "⟨Γγ⟩ ≈ {#} eV：在此细如发丝",
    "⟨Γγ⟩ ≈ {#} eV: a hairline here; neutrons widen these peaks": "⟨Γγ⟩ ≈ {#} eV：在此细如发丝；中子使这些峰变宽",
    "peaks drawn about {#}× wider than life so they show": "峰画得比实际宽约 {#}× 以便看清",
  };
  // beam readout and per-target labels
  for (const u of ["keV", "eV"]) L[`beam of neutrons at {#} ${u}`] = `中子束流 {#} ${u}`;
  const EL = { iron: "铁", gold: "金", uranium: "铀" };
  for (const en in EL) {
    L[`${en}{#} levels`] = `${EL[en]}{#} 能级`;
    L[`${en}{#}: took in {#} of the last {#}`] = `${EL[en]}{#}：吸收了 {#} 个（最近 {#} 个中）`;
  }
  // isomer half-life in every unit fmtTime can produce
  const TU = { femtoseconds: "飞秒", picoseconds: "皮秒", nanoseconds: "纳秒", microseconds: "微秒",
    milliseconds: "毫秒", seconds: "秒", minutes: "分钟", hours: "小时", days: "天", years: "年" };
  for (const en in TU) L[`half-life about {#} ${en}`] = `半衰期约 {#} ${TU[en]}`;
  L["half-life about {#}×{#}^{#} years"] = "半衰期约 {#}×{#}^{#} 年";
  Object.assign(WT.L.labels, L);
})();
