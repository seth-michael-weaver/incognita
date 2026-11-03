/* Simplified Chinese (简体中文): fusion (chapter 29) */
WT.L.ch.fusion = {
  num: "第 29 章", title: "聚变能与库仑势垒", short: "聚变",
  lead: "聚变与裂变方向相反：两个轻核结合在一起，结合后的整体比各部分加起来更轻。",
  html: `
<div class="step">
  <h3>从结合能曲线看聚变能</h3>
  <p>把两个轻核结合起来：如果新的原子核在结合能曲线上更高，就会放出能量。越过铁峰之后，结合反而要消耗能量。</p>
  <div class="ctl"><label for="fu-a">每个轻核的 A</label><input id="fu-a" type="range" data-bind="fuse" data-instant min="2" max="60" step="1" value="2"><output data-show="fuse" data-fmt="0"></output></div>
  <p class="ctl-result" id="fu-fuse-out" aria-live="polite"></p>
</div>
<div class="step">
  <h3>库仑势垒与隧穿</h3>
  <p>把氘核往后拉，然后松手。两个原子核都带电，所以大多数射击都被山丘弹开；只有少数能隧穿过去。</p>
  <div class="ctl"><label for="fu-e">推力 (keV)</label><input id="fu-e" type="range" data-bind="lE" min="0.5" max="2.6" step="0.01" value="1.7"><output data-show="E" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fire">发射</button></div>
</div>
<div class="step">
  <h3>反应产物与 Q 值</h3>
  <p>结合后的一对比两个部分更轻。缺失的质量化作高速粒子飞出。</p>
  <div class="btns fu-fuels"><button class="btn ghost" data-act="DT" aria-pressed="true">D–T</button> <button class="btn ghost" data-act="DD" aria-pressed="false">D–D</button> <button class="btn ghost" data-act="DHe" aria-pressed="false">D–³He</button> <button class="btn ghost" data-act="pB" aria-pressed="false">p–¹¹B</button></div>
</div>
<div class="step">
  <h3>热核反应率</h3>
  <p>在热气体中，跑得最快的原子核能穿过去。每一次闪光就是一次聚变。</p>
  <div class="ctl"><label for="fu-t">温度 (keV)</label><input id="fu-t" type="range" data-bind="lT" min="0" max="2" step="0.01" value="1"><output data-show="T" data-fmt="1"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  // fusion: hill, products, gas
  "Coulomb hill": "库仑山丘",
  "D–D": "D–D", "D–T": "D–T", "D–³He": "D–³He",
  "Sun's core": "太阳核心",
  "almost never": "几乎不会",
  "bubble-chamber view, magnetic field into the page: charged products curl, the neutron leaves no track": "气泡室视图，磁场垂直纸面向里：带电产物打弯，中子不留径迹",
  "deuteron": "氘核",
  "deuteron: pull back, let go": "氘核：往后拉，松手",
  "fusion rate: {a} the rate at {b} keV": "聚变率：{b} keV 时的 {a}",
  "hill to climb: charge product Z₁Z₂ = {#}": "要爬的山：电荷乘积 Z₁Z₂ = {#}",
  "missing {#} u  =  {#} MeV out": "缺失 {#} u  =  放出 {#} MeV",
  "neutron escapes": "中子逃逸",
  "push {a} keV · chance to tunnel head-on {b}": "推力 {a} keV · 正面隧穿概率 {b}",
  "screen radius is logarithmic: {#} fm to {#} fm": "屏幕半径为对数刻度：{#} fm 到 {#} fm",
  "tap to fire": "轻触发射",
  "tries {#} · fused {#}": "尝试 {#} · 聚变 {#}",
  "triton": "氚核",
  "turns at {#} fm": "在 {#} fm 处折返",
  "{#} keV": "{#} keV", "{#} MeV": "{#} MeV", "{#} cm": "{#} cm",
  "{#} keV = {#} million K": "{#} keV = {#} 百万 K",
  "{#} in {a}": "{a} 分之 {#}",
  "{a} %": "{a} %",
  "{a} + {a} → {b}: about {c} MeV released": "{a} + {a} → {b}：放出约 {c} MeV",
  "{a} + {a} → {b}: costs {c} MeV": "{a} + {a} → {b}：消耗 {c} MeV",
  "{a} keV · chance {b}": "{a} keV · 概率 {b}",
  "{a} · two branches, equally likely": "{a} · 两个分支，概率相同",
  // gamow
  "E = kT": "E = kT",
  "Gamow peak E₀": "伽莫夫峰 E₀",
  "Q = {#}": "Q = {#}",
  "Q = ∞: no heating needed": "Q = ∞：无需加热",
  "burning on its own": "自持燃烧",
  "cooled down: plasma lost": "冷却：等离子体熄灭",
  "cooling": "冷却中",
  "drag or tap a point; it runs on its own": "拖动或轻触一点，它会自行演化",
  "easiest: {a} keV, nτT {b}": "最容易处：{a} keV，nτT {b}",
  "energy of the colliding pair (keV)": "碰撞对的能量 (keV)",
  "few are this fast": "这么快的很少",
  "heating itself": "自加热",
  "hold: heaters on (Q = fusion power / heating) · let go: heaters off, the plasma is on its own": "按住：加热开（Q = 聚变功率 / 加热功率）· 松手：加热关，等离子体自行维持",
  "ignition (Q = ∞)": "点火 (Q = ∞)",
  "kT (keV)": "kT (keV)",
  "kT {#} keV · E₀ {#} keV · width {#} keV": "kT {#} keV · E₀ {#} keV · 宽度 {#} keV",
  "kT {a} keV · D–T {b} m³/s · {c}× D–D": "kT {a} keV · D–T {b} m³/s · D–D 的 {c} 倍",
  "keeps itself hot": "自行保持高温",
  "n τE (s/m³)": "n τE (s/m³)",
  "peak near {#} keV": "峰值约 {#} keV",
  "plasma": "等离子体",
  "product ×{a}": "乘积 ×{a}",
  "time slowed {a}×": "时间放慢 {a} 倍",
  "tunnels more easily": "更易隧穿",
  "{a} keV · nτ {b} · {c}": "{a} keV · nτ {b} · {c}",
  "⟨σv⟩ (m³/s)": "⟨σv⟩ (m³/s)",
  // tokamak
  "B": "B",
  "K {#} · field lines lost to the wall: {#}": "K {#} · 撞到器壁的磁力线：{#}",
  "axis, q = {#}": "磁轴，q = {#}",
  "deuteron {#} keV": "氘核 {#} keV",
  "edge: q = {#} · lines that cross it are lost": "边缘：q = {#} · 越过的磁力线丢失",
  "electron {#} keV": "电子 {#} keV",
  "alpha {#} MeV": "α 粒子 {#} MeV",
  "laps {#}": "圈数 {#}",
  "negative: turns the other way": "负电荷：反向旋转",
  "q = {#}": "q = {#}",
  "q = {#}/{#}: closes after {#} lap": "q = {#}/{#}：{#} 圈后闭合",
  "q = {#}/{#}: closes after {#} laps": "q = {#}/{#}：{#} 圈后闭合",
  "q = {#}: no simple fraction, the dots fill the circle": "q = {#}：非简单分数，点填满圆周",
  "the cut, flat": "截面，展平",
  "{a} · ρ up to {b} · {c} turns a second": "{a} · ρ 最大 {b} · 每秒 {c} 圈",
  // blanket
  "Copper{#}": "铜{#}",
  "Silicon{#} (SiC)": "硅{#} (SiC)",
  "Steel (iron{#})": "钢（铁{#}）",
  "TBR {#}": "TBR {#}",
  "Tungsten{#}": "钨{#}",
  "Vanadium{#}": "钒{#}",
  "after {#} years at {#} MW/m² · {#} MeV neutrons only · σ from INCOGNITA library v{#}": "{#} 年后，{#} MW/m² · 仅 {#} MeV 中子 · σ 取自 INCOGNITA 数据库 v{#}",
  "binding per nucleon (MeV)": "每核子结合能 (MeV)",
  "could not load the library file": "无法加载数据库文件",
  "grain boundary": "晶界",
  "helium stays and gathers into bubbles; hydrogen mostly diffuses out": "氦留下并聚成气泡；氢大多扩散出去",
  "helium {#} appm": "氦 {#} appm",
  "hydrogen {#} appm": "氢 {#} appm",
  "lead–lithium": "铅锂",
  "liquid lithium": "液态锂",
  "loading INCOGNITA's cross sections…": "正在加载 INCOGNITA 截面…",
  "per fusion neutron · {#} neutrons · cross sections are simple fits": "每个聚变中子 · {#} 个中子 · 截面为简单拟合",
  "shield": "屏蔽层",
  "tritium made, by depth": "按深度的产氚量",
  "wall": "第一壁",
  "σ at {#} MeV:  (n,α) {#} mb · (n,p) {#} mb · (n,{#}n) {#} mb": "{#} MeV 时的 σ：(n,α) {#} mb · (n,p) {#} mb · (n,{#}n) {#} mb",
  "⁶Li {#} · ⁷Li {#} · (n,{#}n) {#}": "⁶Li {#} · ⁷Li {#} · (n,{#}n) {#}",
  "⁶Li {#} · ⁷Li {#} · (n,{#}n) {#} · captured {#} · leaked {#}": "⁶Li {#} · ⁷Li {#} · (n,{#}n) {#} · 俘获 {#} · 泄漏 {#}",
});
