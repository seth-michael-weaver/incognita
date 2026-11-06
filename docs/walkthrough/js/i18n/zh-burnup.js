/* Chinese: burnup (燃料燃耗) */
WT.L.ch.burnup = {
  num: "第1课", title: "燃料燃耗", short: "燃耗",
  html: `
<div class="step">
  <h3>一块芯块的一生</h3>
  <p>这里是一块新燃料芯块中的一千个原子：45 个是铀-235，其余是铀-238。让反应堆运行起来，看铀-235 不断裂变，同时出现新的原子。<b>燃耗</b>计量的是取出的能量，单位是每吨铀的吉瓦·日；水堆的燃料大约在 45–55 时卸出。</p>
  <div class="ctl"><label for="bu-d1">满功率天数</label><input id="bu-d1" type="range" data-bind="d" data-instant min="0" max="1400" step="10" value="400"><output data-show="d" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>钚加入进来</h3>
  <p>铀-238 俘获中子后变成钚-239，而钚-239 也会裂变。到寿期后段，一半以上的裂变发生在钚中；在整个寿期内，约三分之一的能量来自钚。</p>
  <div class="ctl"><label for="bu-d2">满功率天数</label><input id="bu-d2" type="range" data-bind="d" data-instant min="0" max="1400" step="10" value="1000"><output data-show="d" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>毒物不断积累</h3>
  <p>每次裂变留下两个裂变产物，其中一些会吸收中子。铀-235 越来越少、毒物越来越多，<i>k</i><sub>∞</sub>（由这种燃料构成的无限大栅格中，每次裂变引起的新裂变数）逐渐下降，直到这种燃料单靠自己再也维持不了链式反应。</p>
  <div class="ctl"><label for="bu-d3">满功率天数</label><input id="bu-d3" type="range" data-bind="d" data-instant min="0" max="1400" step="10" value="700"><output data-show="d" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>硼与换料</h3>
  <p>堆芯中混装着新燃料、用过一段的燃料和旧燃料。新燃料的反应性过多，所以溶解在冷却水中的硼吸收掉多余的部分，并被慢慢稀释。硼浓度降到零时，最旧的三分之一燃料卸出，换入新燃料。</p>
  <div class="ctl"><label for="bu-m">满功率月数</label><input id="bu-m" type="range" data-bind="m" data-instant min="0" max="54" step="0.5" value="8"><output data-show="m" data-fmt="1"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  // pellet scenes
  "{a} days · burnup {b} GWd/t": "{a} 天 · 燃耗 {b} GWd/t",
  "uranium{#}": "铀{#}",
  "plutonium{#}": "钚{#}",
  "other plutonium": "其他钚同位素",
  "other Pu": "其他 Pu",
  "fission products": "裂变产物",
  "fission products (pairs)": "裂变产物（对）",
  "{a} in {#}": "{a} / {#}",
  "uranium{#}: the remaining ~{#}–{#} %": "铀{#}：其余约 {#}–{#} %",
  "plutonium's share": "钚所占份额",
  "fissions": "裂变",
  "fissions now": "当前裂变",
  "energy so far": "累计能量",
  "U{#}": "U{#}",
  "Pu": "Pu",
  "plutonium": "钚",
  "split": "已裂变",
  "each dot: one atom in a thousand": "每个点：千分之一的原子",
  "each dot: {#} atom in {#}": "每点：{#} 个原子，共 {#} 个",
  // k-infinity
  "k = {#}": "k = {#}",
  "GWd/t →": "GWd/t →",
  "burnup (GWd/t) →": "燃耗（GWd/t）→",
  "typical discharge": "典型卸料燃耗",
  "typical discharge {#}–{#}": "典型卸料燃耗 {#}–{#}",
  "can't keep a chain going alone": "单靠自身无法维持链式反应",
  "this fuel alone can no longer keep a chain going": "这种燃料单靠自身已无法维持链式反应",
  "k∞ reaches {#}": "k∞ 降到 {#}",
  "k∞ = {a}": "k∞ = {a}",
  "fission products catch {a} % of neutrons": "裂变产物俘获 {a} % 的中子",
  // core with boron
  "fresh": "新燃料",
  "one cycle old": "用过一个循环",
  "two cycles old": "用过两个循环",
  "{#} cycle": "{#} 个循环",
  "{#} cycles": "{#} 个循环",
  "reload": "换料",
  "boron (ppm)": "硼（ppm）",
  "boron in the water (ppm)": "水中的硼（ppm）",
  "months →": "月 →",
  "months at full power →": "满功率月数 →",
  "{a} ppm": "{a} ppm",
  "cycle {a} months · fuel leaves at {b} GWd/t": "循环 {a} 个月 · 燃料卸出时 {b} GWd/t",
  "illustrative model": "示意模型",
});
