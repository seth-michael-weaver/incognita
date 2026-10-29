/* Simplified Chinese: products (第 15 章，裂变产物与衰变热) */
WT.L.ch.products = {
  num: "第 15 章", title: "裂变产物与衰变热", short: "裂变产物",
  html: `
<div class="step">
  <p>两块碎片并不相等：一轻一重。图表对每个碎片质量数 A（质子数加中子数），给出产生它的裂变所占的份额。有两个隆起：轻碎片在 A = 95 附近，重碎片在 139 附近。对半分裂（A = 117 附近）要少见约一百倍。</p>
  <p>每条虚线比下一条高十倍，因此罕见的质量也能显示出来。点按一根柱子或拖动滑块：下方是该种分裂的两块碎片。它们的质量之和是 234，而不是 236（铀-235 加中子），因为还有约 2.4 个中子飞走了。</p>
  <div class="ctl"><label for="pr-a">轻碎片的 A</label><input id="pr-a" type="range" data-bind="pick" data-instant min="70" max="117" step="1" value="95"><output data-show="pick" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>停堆之后，它们的衰变仍在持续加热燃料。这些碎片具有放射性：它们一个接一个地衰变，每次衰变都放出热量，不论链式反应是否在进行。</p>
  <div class="ctl"><label for="pr-t">停堆后的时间</label><input id="pr-t" type="range" data-bind="lgt" data-instant min="0" max="8.5" step="0.01" value="0"><output id="pr-tout">1 s</output></div>
  <p>拖动时间。反应堆停止一秒后，这些衰变仍提供约 6 % 的满功率；一天后约为百分之零点五；一年后为万分之几，在大型反应堆里仍有将近一兆瓦。这就是乏燃料要在冷却池中存放数年的原因。曲线是 Way–Wigner 经验规则：用一个简单公式描述运行一年后全部碎片的总衰变。两个坐标轴在每个刻度处都跳升十倍。</p>
</div>`,
};

// canvas labels added 2026-10-29 (I18NLABELS_B)
Object.assign(WT.L.labels, {
  "fragment mass number A →": "碎片质量数 A →",
  "share of fissions that make it (each line ×{#})": "产生它的裂变份额（每条线 ×{#}）",
  "Rb{#} · {#} %": "Rb{#} · {#} %",
  "Xe{#} · {#} %": "Xe{#} · {#} %",
  "+ about {#} neutrons": "+ 约 {#} 个中子",
  "{#} % of full power": "满功率的 {#} %",
  "≈ {#} MW in a {#} MW reactor · {#} s after shutdown": "≈ {#} MW（{#} MW 反应堆）· 停堆后 {#} s",
  "{#} min": "{#} min",
  "{#} h": "{#} h",
  "{#} day": "{#} 天",
  "{#} yr": "{#} 年",
  "time after shutdown (each mark much later) →": "停堆后的时间（每个刻度晚得多）→",
  "Way–Wigner rule of thumb, after a year at full power": "Way–Wigner 经验规则，满功率运行一年后",
});
