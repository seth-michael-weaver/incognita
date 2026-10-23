/* Simplified Chinese (简体中文): fission (chapter 9) */
WT.L.ch.fission = {
  num: "第 9 章", title: "一分为二", short: "裂变",
  lead: "最重的原子核拥有较轻原子核所没有的出口：不是抛出一个粒子，而是整个原子核撕裂成两半。这就是裂变。",
  html: `
<div class="step">
  <p>重原子核的行为就像一滴带电液体。表面张力（灰色箭头）把它拉成球形；质子全都带正电，把它向外推开（红色箭头）。对铀来说，这两者几乎平衡。</p>
  <div class="ctl"><label for="fis-d">拉伸液滴</label><input id="fis-d" type="range" data-bind="def" min="0" max="1" step="0.01" value="0"><output data-show="def" data-fmt="2"></output></div>
  <p>拖动滑块拉伸液滴，观察下方小能量曲线上的点。拉伸会增加表面，这要消耗能量；但也让电荷分散开，这会释放能量。越过曲线顶点后，电荷占上风：颈部形成，两半带着约 200 MeV 的能量飞散开来。</p>
</div>
<div class="step">
  <h3>形状的能量地形</h3>
  <p>这条曲线给出每种形状的能量，从球形（左）到断开（右）。光滑的液滴只给出一座山丘，但核子是成组地填充能级的，这些组称为<b>壳层</b>；在最重的元素中，壳层效应在山丘上挖出一个阱：形成<b>双峰势垒</b>，原子核可以在拉长的形状中停留一段时间。</p>
  <p>程序并不假定这条曲线的形状：它从一个微观计算中逐点读取每个形变（拉伸程度）下的能量。</p>
</div>
<div class="step">
  <h3>穿过山丘的隧道</h3>
  <p>小球代表处在第一个谷中的激发原子核，其激发能为橙色虚线所示，低于 6 MeV 的山顶。按经典物理它永远无法越过；量子力学则允许它<b>隧穿</b>颜色较深的禁区，概率 <i>T</i> 随禁区变厚而指数下降。</p>
  <div class="ctl"><label for="fis-e">激发能</label><input id="fis-e" type="range" data-bind="E" min="3" max="8" step="0.05" value="5"><output data-show="E" data-fmt="2"></output></div>
  <p>提高能量，看着 <i>T</i> 随禁区变薄而上升。教科书中的简便方法（Hill–Wheeler 公式）把山顶当作抛物线（蓝色虚线）。程序则沿着真实形状计算，真实形状在低处更宽，所以远低于山顶时其概率更小。<i>K</i> 衡量挡在路上的山有多少。</p>
  <div class="formula">T = 1 / (1 + e<sup>2K</sup>),  K = ∫ √(2μ(V−E)) dβ / ħ</div>
</div>
<div class="step">
  <h3>山顶上的门</h3>
  <p>山顶上的门就是<b>过渡态</b>，即原子核在势垒顶上被拉伸时的量子态。每个过渡态都有自旋和宇称（0⁺、2⁻、…），起着门的作用；发亮的缝隙表示它开得多大。原子核只能穿过与自身自旋和宇称相同的门，而且当能量越过某扇门的高度时，这扇门才逐渐打开。</p>
  <div class="ctl"><label for="fis-e2">激发能</label><input id="fis-e2" type="range" data-bind="E" min="3" max="8" step="0.05" value="5"><output data-show="E" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="jpAll">任意自旋</button><button class="btn ghost" data-act="jp0">复合核 0⁺</button><button class="btn ghost" data-act="jp1">复合核 1⁻</button></div>
  <p>选定一种自旋和宇称：只有匹配的门才算数，总开度随之下降。在更高处，门密集成<b>连续区</b>，程序按其密度来计数，与处理普通能级的方法相同。</p>
</div>
<div class="step">
  <h3>串联的两座山</h3>
  <p>现在出现两座山，各有一扇门（圆圈；填充部分表示开度）。原子核从左边到来；越过第一座山的原子核被困在阱中，在两扇门之间来回弹跳，直到从其中一边离开。两个概率像串联电阻一样组合，因此主要由更难越过的那座山决定。</p>
  <div class="ctl"><label for="fis-b">外峰高度</label><input id="fis-b" type="range" data-bind="Bb" min="3.5" max="7.5" step="0.05" value="5.6"><output data-show="Bb" data-fmt="2"></output></div>
  <div class="formula">1/T = 1/T<sub>A</sub> + 1/T<sub>B</sub></div>
  <p>把外峰往上拖，看着通向裂变的流量被扼住，无论内侧的门开得多大。</p>
</div>
<div class="step">
  <h3>不止一次机会</h3>
  <p>铀-238 吸收中子，成为激发能为 <i>E</i>*（虚线）的铀-239。如果它没有裂变，也可能改为发射一个中子；虚线随之下降，留下的铀-238 仍然很热，会尝试越过自己的势垒：这就是<b>第二次机会</b>裂变，(n,n′f)。各堆收集每个原子核的最终结局。</p>
  <div class="ctl"><label for="fis-en">中子能量</label><input id="fis-en" type="range" data-bind="En" min="0" max="25" step="0.1" value="7"><output data-show="En" data-fmt="1"></output></div>
  <p>提高能量，后面的尝试开始成功；第三次机会在 12 MeV 附近打开。每一次新的机会都表现为实测<b>裂变截面</b>（原子核发生裂变的可能性）上的一个台阶。程序计算的是裂变发生的频率，而不是裂成哪些碎片。</p>
  <div class="aside">代码位置：<code>fission/wkb.py</code>（形变能路径与 WKB 积分），<code>fission/barriers.py</code>（Hill–Wheeler 公式、过渡态、势垒能级密度），<code>fission/transmission.py</code>（串联的峰、按自旋和宇称计算的 T<sub>fis</sub>），<code>fission/chain.py</code>（级联中每个原子核的势垒）。</div>
</div>`,
};
Object.assign(WT.L.labels, {
  // drop
  "surface tension pulls it round": "表面张力使其变圆",
  "the protons push it apart": "质子将其推开",
  "a charged drop, nearly round": "带电液滴，近乎球形",
  "stretched: more surface, charge further apart": "拉长：表面更大，电荷更分散",
  "a neck forms": "形成颈部",
  "two fragments, carrying about {#} MeV": "两个碎片，带走约 {#} MeV",
  "energy of the drop": "液滴能量",
  // landscape
  "ground state": "基态", "inner barrier": "内势垒", "second well": "第二势阱",
  "outer barrier": "外势垒", "split (scission)": "断裂", "one smooth hill": "单一光滑山丘",
  "shell effects carving the second well": "壳效应挖出第二势阱",
  "round → stretched → necked → split": "球形 → 拉长 → 出现颈部 → 断裂",
  "stretch (deformation) →": "拉伸（形变）→",
  // tunnel
  "forbidden zone": "禁区",
  "excitation {#} MeV": "激发能 {#} MeV",
  "hilltop {#} MeV": "峰顶 {#} MeV",
  "parabola fit": "抛物线拟合",
  "passes over the top": "从峰顶越过",
  // gates
  "continuum: a density": "连续区：按密度",
  "continuum of gates: counted as a density": "门的连续区：按密度计数",
  "gates: transition states": "门：过渡态",
  "E = {#} MeV": "E = {#} MeV",
  "all gates: total opening {#}": "所有门：总开度 {#}",
  "all gates: total opening {#} + {#} from the continuum": "所有门：总开度 {#} + 连续区 {#}",
  "{#}⁺ gates only: total opening {#}": "仅 {#}⁺ 门：总开度 {#}",
  "{#}⁺ gates only: total opening {#} + {#} from the continuum": "仅 {#}⁺ 门：总开度 {#} + 连续区 {#}",
  "{#}⁻ gates only: total opening {#}": "仅 {#}⁻ 门：总开度 {#}",
  "{#}⁻ gates only: total opening {#} + {#} from the continuum": "仅 {#}⁻ 门：总开度 {#} + 连续区 {#}",
  // series
  "nuclei arriving →": "到来的原子核 →",
  "trapped in the well": "困在阱中",
  "fission": "裂变",
  "so far: {#} through, {#} turned back": "目前：{#} 通过，{#} 折返",
  // chance
  "²³⁹U*  E* = {#} MeV": "²³⁹U*  E* = {#} MeV", "²³⁸U*  E* = {#} MeV": "²³⁸U*  E* = {#} MeV", "²³⁷U*  E* = {#} MeV": "²³⁷U*  E* = {#} MeV",
  "↑ E* above the picture": "↑ E* 超出画面",
  "fission!": "裂变！",
  "emits a neutron, cools, tries again": "发射中子，冷却，再试一次",
  "too cool to split: a photon, no fission": "太冷无法裂变：发射光子，不裂变",
  "attempt {#}: barrier {#} % open": "第 {#} 次尝试：势垒开度 {#} %",
  "{#}st chance (n,f)": "第 {#} 次机会 (n,f)", "{#}nd chance (n,n′f)": "第 {#} 次机会 (n,n′f)", "{#}rd chance (n,{#}nf)": "第 {#} 次机会 (n,{#}nf)",
  "{#}st (n,f)": "第 {#} 次 (n,f)", "{#}nd (n,n′f)": "第 {#} 次 (n,n′f)", "{#}rd (n,{#}nf)": "第 {#} 次 (n,{#}nf)",
  "no fission": "未裂变",
});
// labels carrying a transmission T, printed either as 0.12 or as 3.4·10⁻5 (two number shapes)
(function () {
  const L = WT.L.labels, F = ["{#}", "{#}·{#}⁻{#}"];
  for (const a of F) {
    L[`inner gate T ≈ ${a}`] = `内门 T ≈ ${a}`;
    L[`outer gate T ≈ ${a}`] = `外门 T ≈ ${a}`;
    L[`both hills: T ≈ ${a}, {#} % of what arrives gets through`] = `两座山：T ≈ ${a}，到达者中 {#} % 通过`;
    for (const b of F) {
      L[`T ≈ ${a} real shape · ${b} parabola`] = `T ≈ ${a} 真实形状 · ${b} 抛物线`;
      L[`chance to tunnel T ≈ ${a} on the real shape, ${b} on the parabola`] = `隧穿概率 T ≈ ${a}（真实形状），${b}（抛物线）`;
    }
  }
})();
