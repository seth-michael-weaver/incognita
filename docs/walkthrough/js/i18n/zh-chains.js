/* Chinese: chains (衰变链与放射平衡) */
WT.L.ch.chains = {
  num: "第4课", title: "衰变链与放射平衡", short: "衰变链",
  html: `
<div class="step">
  <h3>母体、子体、孙体</h3>
  <p>新生成的原子核常常也不稳定。母体衰变成子体，子体再衰变成稳定的孙体。子体先积累，然后逐渐消失；积累得多高，取决于它相对于母体衰变得有多快。</p>
  <div class="ctl"><label for="ch-t2">子体半衰期（s）</label><input id="ch-t2" type="range" data-bind="T2" data-instant min="0.5" max="9" step="0.5" value="1.5"><output data-show="T2" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="refill">新样品</button></div>
</div>
<div class="step">
  <h3>长期平衡：镭与氡</h3>
  <p>镭-226 的半衰期为 1600 年；它的子体氡-222 是一种气体，半衰期只有 3.8 天。在密封的罐子里，氡不断积累，直到它衰变的速度与生成的速度相等：<i>A</i><sub>Rn</sub> = <i>A</i><sub>Ra</sub>(1 − e<sup>−λt</sup>)，其中 λ 是氡的衰变常数。几周之后，两者的衰变率就相同了。</p>
  <div class="btns"><button class="btn" data-act="vent">打开罐子</button></div>
</div>
<div class="step">
  <h3>暂时平衡：锝“母牛”</h3>
  <p>医院拿到一根装有钼-99（66 小时）的柱子，它不断产生锝-99m（6 小时），这是用得最多的医用示踪剂。每天早上把锝洗脱出来，它又会重新长回，跟随缓慢衰减的钼一起变化。</p>
  <div class="btns"><button class="btn" data-act="milk">给发生器“挤奶”</button><button class="btn ghost" data-act="genre">新发生器</button></div>
</div>
<div class="step">
  <h3>沿铀衰变链而下</h3>
  <p>铀-238 要经过十四步才变成稳定的铅。在这张图上，一次 α 衰变向下移两格、向左移两格，一次 β 衰变向上移一格、向左移一格。在古老而未受扰动的铀矿中，每个成员的衰变率都相同。</p>
  <div class="btns"><button class="btn" data-act="next">下一次衰变</button><button class="btn ghost" data-act="restart">重新开始</button></div>
</div>`,
};
Object.assign(WT.L.labels, {
  // generations
  "parent ({#} s): {#}": "母体（{#} s）：{#}",
  "daughter ({#} s): {#}": "子体（{#} s）：{#}",
  "granddaughter (stable): {#}": "孙体（稳定）：{#}",
  "parent {#}": "母体 {#}",
  "daughter {#}": "子体 {#}",
  "stable {#}": "稳定 {#}",
  "daughter peaks: {#} %": "子体峰值：{#} %",
  "{#} s": "{#} s",
  "illustrative half-lives": "示意性半衰期",
  // radium jar
  "radium{#}": "镭{#}",
  "radon{#} gas": "氡{#} 气体",
  "radium": "镭",
  "radium activity": "镭的活度",
  "radon": "氡",
  "radon activity": "氡的活度",
  "{#} d": "{#} 天",
  "days →": "天 →",
  "day {#}: radon at {#} % of radium": "第 {#} 天：氡达到镭的 {#} %",
  "A(Rn) = A(Ra) × ({#} − exp(−λt))": "A(Rn) = A(Ra) × ({#} − exp(−λt))",
  "A(radon) = A(radium) × ({#} − exp(−λt))": "A(氡) = A(镭) × ({#} − exp(−λt))",
  // generator
  "Mo{#}": "Mo{#}",
  "molybdenum{#}": "钼{#}",
  "Tc{#}m out": "Tc{#}m 流出",
  "Tc{#}m to the patient": "Tc{#}m 送往患者",
  "dashed: never milked": "虚线：从不“挤奶”",
  "activity": "活度",
  "{#} h since last milking · Tc{#}m at {#} % of Mo{#}": "距上次“挤奶” {#} h · Tc{#}m 为 {#} % 的 Mo{#}",
  "regrows to its peak in about {#} hours": "约 {#} 小时后重新长到峰值",
  // uranium series
  "U": "U", "Th": "Th", "Pa": "Pa", "Ra": "Ra", "Rn": "Rn", "Po": "Po", "Pb": "Pb", "Bi": "Bi", "At": "At", "Fr": "Fr", "Ac": "Ac",
  "neutrons →": "中子 →",
  "protons ↑": "质子 ↑",
  "grey: stable": "灰色：稳定",
  "alpha: loses {#} protons and {#} neutrons": "α：失去 {#} 个质子和 {#} 个中子",
  "alpha: {#} p, {#} n": "α：{#} p，{#} n",
  "beta: a neutron becomes a proton": "β：一个中子变成质子",
  "beta: n → p": "β：n → p",
  "U{#} · half-life {#} billion yr · alpha next": "U{#} · 半衰期 {#}×10⁹ 年 · 下一步 α",
  "U{#} · half-life {#} yr · alpha next": "U{#} · 半衰期 {#} 年 · 下一步 α",
  "Th{#} · half-life {#} days · beta next": "Th{#} · 半衰期 {#} 天 · 下一步 β",
  "Th{#} · half-life {#} yr · alpha next": "Th{#} · 半衰期 {#} 年 · 下一步 α",
  "Pa{#}m · half-life {#} min · beta next": "Pa{#}m · 半衰期 {#} min · 下一步 β",
  "Ra{#} · half-life {#} yr · alpha next": "Ra{#} · 半衰期 {#} 年 · 下一步 α",
  "Rn{#} · half-life {#} days · alpha next": "Rn{#} · 半衰期 {#} 天 · 下一步 α",
  "Po{#} · half-life {#} min · alpha next": "Po{#} · 半衰期 {#} min · 下一步 α",
  "Po{#} · half-life {#} µs · alpha next": "Po{#} · 半衰期 {#} µs · 下一步 α",
  "Po{#} · half-life {#} days · alpha next": "Po{#} · 半衰期 {#} 天 · 下一步 α",
  "Pb{#} · half-life {#} min · beta next": "Pb{#} · 半衰期 {#} min · 下一步 β",
  "Pb{#} · half-life {#} years · beta next": "Pb{#} · 半衰期 {#} 年 · 下一步 β",
  "Bi{#} · half-life {#} min · beta next": "Bi{#} · 半衰期 {#} min · 下一步 β",
  "Bi{#} · half-life {#} days · beta next": "Bi{#} · 半衰期 {#} 天 · 下一步 β",
  "Pb{#}: stable, the chain ends": "Pb{#}：稳定，衰变链到此结束",
  "step {#} of {#} · tap the nucleus": "第 {#} / {#} 步 · 点按原子核",
});
