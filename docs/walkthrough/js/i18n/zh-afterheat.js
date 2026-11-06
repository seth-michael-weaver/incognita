/* Chinese: afterheat (停堆后的热量) */
WT.L.ch.afterheat = {
  num: "第1课", title: "停堆后的热量", short: "衰变热",
  html: `
<div class="step">
  <h3>链式反应停止</h3>
  <p>插入控制棒后，大约一分钟之内原子就不再裂变了。但燃料仍在发光发热：先前裂变留下的碎片具有放射性，它们的衰变仍在放出热量。这就是<b>衰变热</b>（也叫余热）。</p>
  <div class="btns"><button class="btn" data-act="ahDrop">插入控制棒</button> <button class="btn ghost" data-act="ahUp">重新启动</button></div>
</div>
<div class="step">
  <h3>缓慢地衰减</h3>
  <p>刚停堆时，这部分热量约为满功率的 6–7 %。一小时后约为 1 %，一天后约为 0.5 %，一周后约为 0.25 %。比例虽小，但乘的是一个非常大的数。</p>
  <div class="ctl"><label for="ah-t">停堆后的时间</label><input id="ah-t" type="range" data-bind="lt" data-instant min="0" max="7.5" step="0.01" value="3.56"></div>
</div>
<div class="step">
  <h3>让水保持流动</h3>
  <p>所以停堆后堆芯仍要冷却。泵使水不断流过燃料，把热量带走。关掉泵，温度就会上升，因为热量无处可去。</p>
  <div class="btns"><button class="btn ghost" data-act="ahPump" aria-pressed="true">泵</button></div>
</div>
<div class="step">
  <h3>无泵冷却</h3>
  <p>热水上升，冷水下沉。一条通往高于堆芯的水池的回路，完全不用泵也能让水流动起来。一些较新的设计依靠这种方式冷却长达数天。</p>
  <div class="btns"><button class="btn ghost" data-act="ahPump" aria-pressed="false">泵</button> <button class="btn ghost" data-act="ahPass" aria-pressed="true">非能动回路</button></div>
</div>`,
};
Object.assign(WT.L.labels, {
  // time formats
  "{a} s": "{a} 秒",
  "{a} min": "{a} 分钟",
  "{a} hours": "{a} 小时",
  "{a} days": "{a} 天",
  "{a} months": "{a} 个月",
  "{#} min": "{#} min",
  "{#} hour": "{#} 小时",
  "{#} day": "{#} 天",
  "{#} week": "{#} 周",
  "{#} year": "{#} 年",
  // the drop
  "splitting atoms": "原子裂变",
  "heat from splitting atoms": "原子裂变产生的热",
  "decaying fragments": "碎片衰变",
  "heat from decaying fragments": "裂变碎片衰变产生的热",
  "full power": "满功率",
  "running at full power": "满功率运行中",
  "{a} after the rods dropped": "插棒后 {a}",
  "total heat: {a} % of full power": "总热量：满功率的 {a} %",
  "the splitting dies away in about a minute": "裂变约一分钟内停止",
  "the splitting dies away within about a minute": "裂变在约一分钟内逐渐停止",
  "the decay heat stays and fades slowly": "衰变热仍在，缓慢衰减",
  "the decay heat stays, and fades only slowly": "衰变热依然存在，只是缓慢地衰减",
  // the fading curve
  "heat, share of full power": "热量，占满功率比例",
  "heat, as a share of full power": "热量，占满功率的比例",
  "{a} after shutdown: {b} % of full power": "停堆后 {a}：满功率的 {b} %",
  "{#} MW core: {a} MW, like {b} kettles": "{#} MW 堆芯：{a} MW，相当于 {b} 个水壶",
  "for a {#} MW core: {a} MW, as much as {b} electric kettles": "对 {#} MW 的堆芯：{a} MW，相当于 {b} 个电水壶",
  // cooling
  "pool, up high": "高处水池",
  "water pool, placed higher": "位置较高的水池",
  "cooler": "冷却器",
  "heat exchanger": "热交换器",
  "pump on": "泵开",
  "pump off": "泵关",
  "pump running": "泵运行中",
  "pump stopped": "泵已停",
  "boiling": "沸腾",
  "the water starts to boil": "水开始沸腾",
  "normal": "正常",
  "too hot": "过热",
  "temperature": "温度",
  "core temperature": "堆芯温度",
  "{a} after shutdown · heat {b} % of full power": "停堆后 {a} · 热量为满功率的 {b} %",
  "too hot: cooling must be restored": "过热：必须恢复冷却",
  "too hot: the water would start to boil away; cooling must be restored": "过热：水将开始沸腾蒸干；必须恢复冷却",
  "temperature climbing": "温度上升",
  "temperature climbing: the heat has nowhere to go": "温度上升：热量无处可去",
  "pumps carry the heat away": "泵把热量带走",
  "steady: the pumps carry the heat away": "稳定：泵把热量带走",
  "steady, with no pumps": "稳定，无需泵",
  "steady: natural circulation carries the heat away": "稳定：自然循环把热量带走",
  "steady": "稳定",
  "illustration": "示意图",
});
