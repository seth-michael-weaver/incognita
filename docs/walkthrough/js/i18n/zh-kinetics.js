/* Chinese: kinetics (反应堆动力学：六组缓发中子与倒时方程) */
WT.L.ch.kinetics = {
  num: "第1课", title: "反应堆动力学：六组缓发中子与倒时方程", short: "动力学",
  html: `
<div class="step">
  <h3>六组迟到的中子</h3>
  <p>缓发中子来自大约六组裂变产物，半衰期从 0.23 s 到 56 s（Keepin，铀-235）。2 s 组和 22 s 组放出其中的大部分，而长寿命的组则保存着大部分等待中的存量：平均缓发时间 Σ <i>a</i><sub>i</sub>/<i>λ</i><sub>i</sub> ≈ 13 s。停止裂变，看各组以各自的速度衰减。</p>
  <div class="btns"><button class="btn" data-act="kistop" aria-pressed="false">停止裂变</button></div>
</div>
<div class="step">
  <h3>倒时方程</h3>
  <p>在六组点堆动力学方程中代入 <i>n</i> ∝ e<sup><i>ωt</i></sup>，得到 <i>ρ</i> = <i>ω</i>Λ + Σ <i>β</i><sub>i</sub><i>ω</i>/(<i>ω</i> + <i>λ</i><sub>i</sub>)：七条分支被位于 −<i>λ</i><sub>i</sub> 的极点隔开。一个阶跃 <i>ρ</i> 与每条分支各相交一次；最右边的根给出稳定周期 <i>T</i> = 1/<i>ω</i><sub>1</sub>，其余六项逐渐衰亡。</p>
  <div class="ctl"><label for="ki-r1">反应性 ρ（$）</label><input id="ki-r1" type="range" data-bind="rd" data-instant min="-2" max="1.3" step="0.01" value="0.3"><output data-show="rd" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>瞬跳与瞬发临界</h3>
  <p>阶跃反应性先在几毫秒内使功率跃升 <i>P</i><sub>1</sub>/<i>P</i><sub>0</sub> ≈ <i>β</i>/(<i>β</i> − <i>ρ</i>)，然后按稳定周期上升。当 <i>ρ</i> = 1 $ 时，仅靠瞬发中子就已临界，周期骤降到接近 Λ/(<i>ρ</i> − <i>β</i>)。</p>
  <div class="ctl"><label for="ki-r2">反应性 ρ（$）</label><input id="ki-r2" type="range" data-bind="rj" data-instant min="0.05" max="1.3" step="0.01" value="0.5"><output data-show="rj" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>紧急停堆之后</h3>
  <p>引入很大的负反应性：功率立即降到约 <i>β</i>/(<i>β</i> − <i>ρ</i>)，此后下降的速度不会快于寿命最长那一组的衰变。无论停堆多深，周期都趋于 −1/<i>λ</i><sub>1</sub> ≈ −80 s。</p>
  <div class="ctl"><label for="ki-r3">反应性 ρ（$）</label><input id="ki-r3" type="range" data-bind="rs" data-instant min="-30" max="-0.5" step="0.5" value="-10"><output data-show="rs" data-fmt="1"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  // button text (WT.tr)
  "Stop fissions": "停止裂变",
  "Restart fissions": "恢复裂变",
  // six groups
  "half-life · share emitted": "半衰期 · 发射份额",
  "waiting stock": "等待中的存量",
  "delayed neutrons out": "放出的缓发中子",
  "{#} s": "{#} s",
  "{#} %": "{#} %",
  "mean delay Σ aᵢ/λᵢ = {#} s · β = {#} (U{#})": "平均缓发时间 Σ aᵢ/λᵢ = {#} s · β = {#}（铀{#}）",
  "{#} s after stopping · delayed emission {#} % of the start": "停止后 {#} s · 缓发中子发射为初始的 {#} %",
  "Keepin six-group data": "Keepin 六组数据",
  // inhour
  "prompt critical": "瞬发临界",
  "drag ρ": "拖动 ρ",
  "prompt root": "瞬发根",
  "prompt root ≈ −(β−ρ)/Λ": "瞬发根 ≈ −(β−ρ)/Λ",
  "ω ({#}/s), stretched": "ω（{#}/s），拉伸",
  "ω ({#}/s), axis stretched (asinh)": "ω（{#}/s），坐标轴拉伸（asinh）",
  "ρ = {#}: power stays flat": "ρ = {#}：功率保持不变",
  "stable period T = {#}/ω₁ = {#} ms": "稳定周期 T = {#}/ω₁ = {#} ms",
  "stable period T = {#}/ω₁ = {#} s": "稳定周期 T = {#}/ω₁ = {#} s",
  "stable period T = {#}/ω₁ = {#} min": "稳定周期 T = {#}/ω₁ = {#} min",
  "stable period T = {#}/ω₁ = {#} h": "稳定周期 T = {#}/ω₁ = {#} h",
  // prompt jump
  "drag the rods out": "向外拖动控制棒",
  "drag the rods in": "向内拖动控制棒",
  "prompt jump β/(β−ρ) = {#}": "瞬跳 β/(β−ρ) = {#}",
  "power": "功率",
  "prompt critical · period {#} ms (Λ = {#} µs)": "瞬发临界 · 周期 {#} ms（Λ = {#} µs）",
  "prompt critical · period {#} s (Λ = {#} µs)": "瞬发临界 · 周期 {#} s（Λ = {#} µs）",
  "ρ = {#} $ · stable period {#} ms": "ρ = {#} $ · 稳定周期 {#} ms",
  "ρ = {#} $ · stable period {#} s": "ρ = {#} $ · 稳定周期 {#} s",
  "ρ = {#} $ · stable period {#} min": "ρ = {#} $ · 稳定周期 {#} min",
  "ρ = {#} $ · stable period {#} h": "ρ = {#} $ · 稳定周期 {#} h",
  // scram
  "prompt drop to {#}": "瞬降至 {#}",
  "slope e^(−t/{#} s)": "斜率 e^(−t/{#} s)",
  "slope e^(−t / {#} s): the {#} s group": "斜率 e^(−t / {#} s)：{#} s 组",
  "power ×{#} speed": "功率 ×{#} 倍速",
  "ρ = {#} $ · stable period {#} s (limit {#} s)": "ρ = {#} $ · 稳定周期 {#} s（极限 {#} s）",
  "ρ = {#} $ · stable period {#} ms (limit {#} s)": "ρ = {#} $ · 稳定周期 {#} ms（极限 {#} s）",
  "ρ = {#} $ · stable period {#} min (limit {#} s)": "ρ = {#} $ · 稳定周期 {#} min（极限 {#} s）",
  "{#} ms": "{#} ms",
  "{#} min": "{#} min",
  "{#} h": "{#} h",
});
