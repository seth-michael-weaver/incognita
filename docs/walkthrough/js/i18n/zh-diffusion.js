/* Chinese: diffusion (临界尺寸与泄漏) */
WT.L.ch.diffusion = {
  num: "第1课", title: "临界尺寸与泄漏", short: "临界尺寸",
  html: `
<div class="step">
  <h3>中子漫游，部分泄漏</h3>
  <p>中子在一次次碰撞之间折来折去，直到被某种原子核吸收。在边缘附近产生的中子可能游出堆芯而损失掉。堆芯越大，其表面积相对于体积越小，泄漏的份额也就越小。</p>
  <div class="ctl"><label for="df-w0">堆芯宽度（cm）</label><input id="df-w0" type="range" data-bind="w" data-instant min="20" max="200" step="2" value="60"><output data-show="w" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>通量的形状</h3>
  <p>中子数目会稳定成一种形状，在边缘处降到约为零：平板中是余弦，球中是 sin(<i>r</i>)/<i>r</i>，圆柱中是贝塞尔函数乘以余弦。它必须弯曲的剧烈程度就是<b>几何曲率</b> <i>B</i>²。</p>
  <div class="btns"><button class="btn ghost" data-act="dfslab" aria-pressed="false">平板</button><button class="btn ghost" data-act="dfsph" aria-pressed="true">球</button><button class="btn ghost" data-act="dfcyl" aria-pressed="false">圆柱</button></div>
  <div class="ctl"><label for="df-w1">堆芯宽度（cm）</label><input id="df-w1" type="range" data-bind="w" data-instant min="20" max="200" step="2" value="80"><output data-show="w" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>临界尺寸</h3>
  <p>单群扩散理论给出 <i>k</i><sub>eff</sub> = <i>k</i><sub>∞</sub> / (1 + <i>M</i>²<i>B</i>²)，其中水堆的徙动面积 <i>M</i>² 约为 60 cm²。当 <i>B</i>² 等于材料曲率 (<i>k</i><sub>∞</sub> − 1)/<i>M</i>² 时，堆芯达到临界。找出这个尺寸。</p>
  <div class="btns"><button class="btn ghost" data-act="dfslab" aria-pressed="false">平板</button><button class="btn ghost" data-act="dfsph" aria-pressed="true">球</button><button class="btn ghost" data-act="dfcyl" aria-pressed="false">圆柱</button></div>
  <div class="ctl"><label for="df-w2">堆芯宽度（cm）</label><input id="df-w2" type="range" data-bind="w" data-instant min="20" max="200" step="1" value="90"><output data-show="w" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>反射层节省中子</h3>
  <p>用水包围平板堆芯：一些离开堆芯的中子会被散射回来。通量在堆芯边缘不再降为零，所以更薄的堆芯就能达到同样的 <i>k</i>；这一收益就是<b>反射层节省</b>，这里每侧约 6 cm。</p>
  <div class="btns"><button class="btn ghost" data-act="dfrefl" aria-pressed="true">水反射层</button></div>
  <div class="ctl"><label for="df-w3">堆芯宽度（cm）</label><input id="df-w3" type="range" data-bind="w" data-instant min="20" max="120" step="1" value="44"><output data-show="w" data-fmt="0"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  // random walk
  "drag the edge": "拖动边缘",
  "{#} cm": "{#} cm",
  "red: leaked": "红：泄漏",
  "red: leaked out · blue: absorbed inside": "红：泄漏出去 · 蓝：在内部被吸收",
  "leak: walk {#} % · diffusion {#} %": "泄漏：随机游走 {#} % · 扩散 {#} %",
  "leak: walk … · diffusion {#} %": "泄漏：随机游走 … · 扩散 {#} %",
  "share leaking: random walk {#} % · diffusion theory {#} %": "泄漏份额：随机游走 {#} % · 扩散理论 {#} %",
  "share leaking: random walk … · diffusion theory {#} %": "泄漏份额：随机游走 … · 扩散理论 {#} %",
  "k_eff = k∞ × ({#} − leak) = {#}": "k_eff = k∞ × ({#} − 泄漏) = {#}",
  // shapes
  "slab": "平板",
  "sphere": "球",
  "cylinder": "圆柱",
  "slab core": "平板堆芯",
  "water": "水",
  "flux across the middle": "穿过中部的通量",
  "−D∇²φ + Σₐφ = (νΣ_f / k) φ": "−D∇²φ + Σₐφ = (νΣ_f / k) φ",
  "B² = (π/a)² = {#} × {#}⁻⁴ cm⁻²": "B² = (π/a)² = {#} × {#}⁻⁴ cm⁻²",
  "B² = (π/R)² = {#} × {#}⁻⁴ cm⁻²": "B² = (π/R)² = {#} × {#}⁻⁴ cm⁻²",
  "B² = ({#}/R)² + (π/H)² = {#} × {#}⁻⁴ cm⁻²": "B² = ({#}/R)² + (π/H)² = {#} × {#}⁻⁴ cm⁻²",
  "{#} × {#}⁻⁴ cm⁻²": "{#} × {#}⁻⁴ cm⁻²",
  "slab {#} cm wide · smaller core → sharper bend → larger B²": "平板宽 {#} cm · 堆芯越小 → 弯曲越剧烈 → B² 越大",
  "sphere {#} cm wide · smaller core → sharper bend → larger B²": "球宽 {#} cm · 堆芯越小 → 弯曲越剧烈 → B² 越大",
  "cylinder {#} cm wide · smaller core → sharper bend → larger B²": "圆柱宽 {#} cm · 堆芯越小 → 弯曲越剧烈 → B² 越大",
  // k_eff against width
  "k = {#}": "k = {#}",
  "critical {#} cm": "临界 {#} cm",
  "core width →": "堆芯宽度 →",
  "critical: B² = B²ₘ, k_eff = {#}": "临界：B² = B²ₘ，k_eff = {#}",
  "k_eff = {#} / ({#} + {#} cm² × {#}e{#} cm⁻²) = {#}": "k_eff = {#} / ({#} + {#} cm² × {#}e{#} cm⁻²) = {#}",
  "reflected: k_eff {#} · bare: {#} · savings {#} cm per side": "有反射层：k_eff {#} · 裸堆：{#} · 节省每侧 {#} cm",
  "bare: k_eff {#} · critical at {#} cm": "裸堆：k_eff {#} · 临界宽度 {#} cm",
  "illustration": "示意图",
});
