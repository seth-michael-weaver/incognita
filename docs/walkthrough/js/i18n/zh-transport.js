/* Chinese: transport (中子输运与蒙特卡罗方法) */
WT.L.ch.transport = {
  num: "第1课", title: "中子输运与蒙特卡罗方法", short: "蒙特卡罗",
  html: `
<div class="step">
  <h3>输运方程</h3>
  <p>严格地说，中子服从关于角通量 <i>ψ</i>(<b>r</b>, <b>Ω</b>, <i>E</i>) 的玻尔兹曼方程：<b>Ω</b>·∇<i>ψ</i> + Σ<sub>t</sub><i>ψ</i> = ∫∫Σ<sub>s</sub><i>ψ</i>′ d<b>Ω</b>′d<i>E</i>′ + (<i>χ</i>/4π<i>k</i>)∫<i>ν</i>Σ<sub>f</sub><i>φ</i>′ d<i>E</i>′。蒙特卡罗方法逐个模拟中子来求解它：飞行 <i>s</i> = −ln <i>ξ</i> / Σ<sub>t</sub>，然后发生散射、被俘获或引起裂变。</p>
  <div class="btns"><button class="btn" data-act="trnew">新中子</button></div>
</div>
<div class="step">
  <h3>扩散理论失效之处</h3>
  <p>扩散理论假定各方向的通量几乎相同。在距表面一两个平均自由程以内以及强吸收体中，这一假定不再成立。在带均匀源的平板中，逐步增大吸收，把它与蒙特卡罗通量进行比较。</p>
  <div class="ctl"><label for="tr-pa">吸收 Σ<sub>a</sub>/Σ<sub>t</sub></label><input id="tr-pa" type="range" data-bind="pa" data-instant min="0.05" max="0.8" step="0.05" value="0.5"><output data-show="pa" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>幂迭代</h3>
  <p>为求 <i>k</i><sub>eff</sub>，每一代的裂变点成为下一代的源；<i>k</i> 就是每个起始中子存入的裂变点数。从一个很差的初始猜测出发，让所有中子都从一侧边缘开始，观察源如何扩展为基模。</p>
  <div class="btns"><button class="btn" data-act="trbad">从差的猜测重新开始</button></div>
</div>
<div class="step">
  <h3>源收敛了吗？</h3>
  <p>分格统计的源的香农熵 <i>H</i> = −Σ <i>p</i><sub>b</sub> log<sub>2</sub> <i>p</i><sub>b</sub> 在源稳定后趋于平稳；只有到那时才对各代取平均。<i>k</i> 的误差棒随所计粒子历史数按 1/√<i>N</i> 缩小。</p>
  <div class="ctl"><label for="tr-n">每代历史数</label><input id="tr-n" type="range" data-bind="nh" data-instant min="100" max="2000" step="100" value="400"><output data-show="nh" data-fmt="0"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  // free flights
  "vacuum": "真空",
  "amber glow: where collisions pile up": "琥珀色辉光：碰撞密集之处",
  "glow: collision density": "辉光：碰撞密度",
  "tap the slab to start neutrons": "点击平板发射中子",
  "scatter": "散射",
  "capture": "俘获",
  "fission": "裂变",
  "leak": "泄漏",
  "chance to fly at least s:  e^(−Σₜ s)": "飞行至少 s 的概率：e^(−Σₜ s)",
  "{#} free paths": "{#} 个自由程",
  "ξ = {#}  →  s = −ln ξ / Σₜ = {#} free paths": "ξ = {#}  →  s = −ln ξ / Σₜ = {#} 个自由程",
  // diffusion vs Monte Carlo
  "infinite medium S/Σₐ": "无限介质 S/Σₐ",
  "Monte Carlo": "蒙特卡罗",
  "diffusion": "扩散",
  "flux": "通量",
  "diffusion vs Monte Carlo: +{#} % at the surface, +{#} % in the middle": "扩散与蒙特卡罗相比：表面处 +{#} %，中部 +{#} %",
  "diffusion vs Monte Carlo: +{#} % at the surface, {#} % in the middle": "扩散与蒙特卡罗相比：表面处 +{#} %，中部 {#} %",
  "diffusion vs Monte Carlo: {#} % at the surface, +{#} % in the middle": "扩散与蒙特卡罗相比：表面处 {#} %，中部 +{#} %",
  "diffusion vs Monte Carlo: {#} % at the surface, {#} % in the middle": "扩散与蒙特卡罗相比：表面处 {#} %，中部 {#} %",
  // power iteration
  "tap the slab to drop the whole source there": "点击平板，把整个源放到那里",
  "tap: drop the source there": "点击：把源放到那里",
  "generation {#}": "第 {#} 代",
  "fission source · dashed: fundamental mode": "裂变源 · 虚线：基模",
  "source · dashed: fundamental mode": "源 · 虚线：基模",
  "source entropy H (bits)": "源熵 H（比特）",
  "inactive  |  active generations": "非活跃代  |  活跃代",
  "inactive | active": "非活跃 | 活跃",
  "k per generation": "每代的 k",
  "generation {#}: k = {#} · H = {#} bits": "第 {#} 代：k = {#} · H = {#} 比特",
  "starting…": "启动中…",
  "k_eff = {#} ± {#} ({#} × {#} histories) · diffusion {#}": "k_eff = {#} ± {#}（{#} × {#} 个历史）· 扩散 {#}",
  "{#} generations, averaging starts after {#}": "{#} 代，第 {#} 代之后开始平均",
  "illustrative one-group data": "示意性单群数据",
});
