/* Chinese: rwater (水冷反应堆) */
WT.L.ch.rwater = {
  num: "第1课", title: "水冷反应堆", short: "水冷堆",
  lead: "如今几乎所有动力堆都用水冷却。它们的区别在于水如何把热量带出来。",
  html: `
<div class="step">
  <h3>压水堆（PWR）</h3>
  <p>高压水把热量带到蒸汽发生器；由第二个回路产生蒸汽。</p>
</div>
<div class="step">
  <h3>沸水堆（BWR）</h3>
  <p>水直接在堆芯里沸腾，蒸汽直接送往汽轮机：只有一个回路。</p>
</div>
<div class="step">
  <h3>重水堆（CANDU）</h3>
  <p>重水能使中子慢化，却很少吸收中子，所以用天然铀就够了。</p>
</div>
<div class="step">
  <h3>石墨沸水堆（RBMK）</h3>
  <p>石墨使中子慢化；水在数百根相互独立的管道里沸腾。</p>
</div>
<div class="step">
  <h3>小型模块化堆（SMR）</h3>
  <p>一座小型压水堆，所有部件都装在一个容器里，在工厂中制造。</p>
</div>
<div class="step">
  <h3>超临界水堆（SCWR）</h3>
  <p>压力超过 221 bar 时，水不会沸腾，因此可以运行在更高温度下，把更多热量变成电。</p>
</div>`,
};
Object.assign(WT.L.labels, {
  "BWR": "BWR",
  "CANDU; Canada, India, Romania, Argentina": "CANDU；加拿大、印度、罗马尼亚、阿根廷",
  "Generation IV design, not yet built": "第四代设计，尚未建成",
  "NuScale (US), Linglong One (China)": "NuScale（美国）、玲龙一号（中国）",
  "PHWR": "PHWR",
  "PWR": "PWR",
  "RBMK": "RBMK",
  "SCWR": "SCWR",
  "SMR": "SMR",
  "about {#} % of reactors; US, Japan, Sweden": "约占反应堆的 {#} %；美国、日本、瑞典",
  "about {#} in {#} of the world's reactors": "约占全世界反应堆的 {#}/{#}",
  "all in one vessel": "全部在一个容器内",
  "boiling water in tubes": "管内沸腾的水",
  "boils in the core": "在堆芯内沸腾",
  "calandria: cool heavy water": "排管容器：低温重水",
  "calandria: cool heavy water slows the neutrons": "排管容器：低温重水使中子慢化",
  "condenser": "冷凝器",
  "control rods from below": "控制棒从下方插入",
  "coolant out": "冷却剂出口",
  "core": "堆芯",
  "core, pump-free loop and steam generator in one vessel": "堆芯、无泵回路和蒸汽发生器同在一个容器内",
  "electricity": "发电效率",
  "gen.": "发电机",
  "generator": "发电机",
  "graphite": "石墨",
  "graphite blocks slow the neutrons": "石墨块使中子慢化",
  "horizontal pressure tubes, refuelled while running": "水平压力管，可不停堆换料",
  "illustration": "示意图",
  "outlet": "出口",
  "pressure": "压力",
  "pressure tubes": "压力管",
  "reactor vessel": "反应堆压力容器",
  "rods from below": "控制棒从下插入",
  "steam gen.": "蒸汽发生器",
  "steam generator": "蒸汽发生器",
  "the Chernobyl type; a few still run in Russia": "切尔诺贝利堆型；俄罗斯仍有几座在运行",
  "thermal neutrons · moderator: graphite · coolant: boiling water": "热中子 · 慢化剂：石墨 · 冷却剂：沸腾的水",
  "thermal neutrons · moderator: heavy water · coolant: heavy water": "热中子 · 慢化剂：重水 · 冷却剂：重水",
  "thermal neutrons · moderator: light water · coolant: boiling water": "热中子 · 慢化剂：轻水 · 冷却剂：沸腾的水",
  "thermal neutrons · moderator: light water · coolant: supercritical water": "热中子 · 慢化剂：轻水 · 冷却剂：超临界水",
  "thermal neutrons · moderator: light water · coolant: water": "热中子 · 慢化剂：轻水 · 冷却剂：水",
  "thermal · mod.: graphite · cool.: boiling water": "热 · 慢化：石墨 · 冷却：沸水",
  "thermal · mod.: heavy water · cool.: heavy water": "热 · 慢化：重水 · 冷却：重水",
  "thermal · mod.: light water · cool.: boiling water": "热 · 慢化：轻水 · 冷却：沸水",
  "thermal · mod.: light water · cool.: supercritical water": "热 · 慢化：轻水 · 冷却：超临界水",
  "thermal · mod.: light water · cool.: water": "热 · 慢化：轻水 · 冷却：水",
  "turbine": "汽轮机",
  "vessel": "压力容器",
  "water boils in the core": "水在堆芯内沸腾",
  "water boils in ~{#} pressure tubes": "水在约 {#} 根压力管中沸腾",
  "{#} bar": "{#} bar",
  "{#} bar: hotter than boiling, still one fluid": "{#} bar：高于沸点，仍是单一流体",
  "{#} bar: never boils": "{#} bar：从不沸腾",
  "{#} °C": "{#} °C",
});
