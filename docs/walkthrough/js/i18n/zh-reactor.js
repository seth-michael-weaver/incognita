/* Chinese: reactor (反应堆如何发电) */
WT.L.ch.reactor = {
  num: "第1课", title: "反应堆如何发电", short: "反应堆",
  html: `
<div class="step">
  <h3>燃料</h3>
  <p>铀被烧结成指尖大小的陶瓷芯块，叠装在细长的金属棒里，许多燃料棒再捆成组件。一个芯块放出的热量，大致相当于燃烧一吨煤。</p>
  <div class="ctl"><label for="rea-z">缩小视图</label><input id="rea-z" type="range" data-bind="z" min="0" max="3" step="0.01" value="0"><output data-show="z" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>原子分裂产生热</h3>
  <p>在堆芯里，分裂的铀原子加热了沿燃料棒向上流过的水。这些水同时使中子慢化，让它们能分裂更多的原子。高压使水即使在 325 °C 也不会沸腾。</p>
</div>
<div class="step">
  <h3>蒸汽推动汽轮机</h3>
  <p>热水通过细管把热量传给第二个回路，那里的水沸腾。蒸汽带动汽轮机和发电机旋转，然后冰冷的河水或海水把它重新冷凝成水。大约三分之一的热量变成了电。</p>
</div>
<div class="step">
  <h3>控制棒</h3>
  <p>控制棒吸收中子。把它们插入，分裂的原子就变少：热少了，蒸汽少了，电也少了。把它们拔出，功率就上升。</p>
  <div class="ctl"><label for="rea-rod">控制棒插入深度（%）</label><input id="rea-rod" type="range" data-bind="ins" data-instant min="0" max="100" step="1" value="15"><output data-show="ins" data-fmt="0"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  // fuel zoom
  "drag sideways to zoom": "左右拖动以缩放",
  "drag sideways to zoom out": "左右拖动以缩小视图",
  "UO₂ pellet, {#} cm": "UO₂ 芯块，{#} cm",
  "uranium oxide pellet, about {#} cm": "氧化铀芯块，约 {#} cm",
  "{#} tonne of coal": "{#} 吨煤",
  "about {#} tonne of coal (or {#} m³ of gas)": "约 {#} 吨煤（或 {#} m³ 天然气）",
  "same heat, roughly": "热量大致相同",
  "fuel rod, ~{#} m": "燃料棒，约 {#} m",
  "fuel rod, about {#} m long": "燃料棒，长约 {#} m",
  "~{#} pellets inside": "内装约 {#} 个芯块",
  "about {#} pellets in a metal tube": "金属管内装约 {#} 个芯块",
  "(not to scale)": "（未按比例）",
  "assembly: {#} rods": "组件：{#} 根棒",
  "fuel assembly from above: {#} rods": "燃料组件俯视图：{#} 根棒",
  "rings: control-rod guide tubes": "圆环：控制棒导向管",
  "rings: tubes the control rods slide into": "圆环：控制棒插入的导向管",
  "core: {#} assemblies": "堆芯：{#} 个组件",
  "the core from above: {#} assemblies": "堆芯俯视图：{#} 个组件",
  "~{#} rods, ~{#} m across": "约 {#} 根棒，直径约 {#} m",
  "about {#} rods in a cylinder about {#} m across": "约 {#} 根棒，排成直径约 {#} m 的圆柱",
  "pellet": "芯块",
  "rod": "燃料棒",
  "assembly": "组件",
  "core": "堆芯",
  // plant
  "reactor": "反应堆",
  "reactor vessel": "反应堆压力容器",
  "control rods": "控制棒",
  "steam gen.": "蒸汽发生器",
  "steam generator": "蒸汽发生器",
  "turbine": "汽轮机",
  "gen.": "发电机",
  "generator": "发电机",
  "condenser": "冷凝器",
  "sea or river water": "海水或河水",
  "{#} °C out": "出口 {#} °C",
  "{#} °C in": "入口 {#} °C",
  "steam ~{#} °C": "蒸汽约 {#} °C",
  "{#} bar: hot, but no boiling": "{#} bar：很热，但不沸腾",
  "{#} bar keeps the water liquid at {#} °C": "{#} bar 的压力使水在 {#} °C 时仍保持液态",
  "the water also slows the neutrons": "水还使中子慢化",
  "the water carries the heat and slows the neutrons": "水带走热量，并使中子慢化",
  "heat {#} MW": "热功率 {#} MW",
  "electric {#} MW": "电功率 {#} MW",
  "electricity {#} MW": "电功率 {#} MW",
  "chain stopped; fuel still warm (afterheat)": "链式反应停止；燃料仍发热（余热）",
  "chain reaction stopped; the fuel still gives off afterheat": "链式反应已停止；燃料仍在释放余热",
  "turbine speed fixed by the grid; more steam, more push": "转速由电网锁定；蒸汽越多，推力越大",
  "the turbine's speed is fixed by the grid; more steam pushes harder": "汽轮机的转速由电网固定；蒸汽越多，推动越有力",
  "{#}/{#} of the heat goes to the water": "{#}/{#} 的热量排入水中",
  "about two thirds of the heat leaves through the condenser": "约三分之二的热量经冷凝器排出",
  "illustration": "示意图",
});
