/* Chinese: rays (α、β、γ 与中子) */
WT.L.ch.rays = {
  num: "第2课", title: "α、β、γ 与中子", short: "辐射",
  html: `
<div class="step">
  <h3>四种辐射</h3>
  <p><em class="a">α</em> 是由两个质子和两个中子组成的沉重团块。<b>β</b> 是高速电子。<em class="g">γ</em> 是光，只是能量太高，肉眼看不见。<em class="n">中子</em>则完全不带电。每一种都要靠不同的东西来挡住。</p>
</div>
<div class="step">
  <h3>纸和铝</h3>
  <p>α 粒子个头大又带电，一进去就撞上原子：一张纸就能挡住它们。β 电子走得更远，但几毫米厚的铝也能把它们挡住。</p>
  <div class="btns"><button class="btn ghost" data-act="sh_paper" aria-pressed="true">纸</button><button class="btn ghost" data-act="sh_al" aria-pressed="false">铝</button></div>
</div>
<div class="step">
  <h3>γ 射线：减半，却永不为零</h3>
  <p>γ 射线不带电，通常从原子旁边穿过。每厘米铅给每个光子同样的被俘获机会，所以每一层都把剩下的减半。射线束越来越弱，却永远不会完全为零。</p>
  <div class="ctl"><label for="ry-pb">铅（cm）</label><input id="ry-pb" type="range" data-bind="pb" data-instant min="0" max="5" step="0.1" value="1"><output data-show="pb" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>中子：光靠铅不够</h3>
  <p>中子撞上沉重的铅核，就像乒乓球撞上保龄球：速度几乎不减。水中的氢和中子一样重，所以每撞一次中子都会变慢，直到慢得足以被吞没。</p>
  <div class="btns"><button class="btn ghost" data-act="nm_pb" aria-pressed="true">铅</button><button class="btn ghost" data-act="nm_water" aria-pressed="false">水</button></div>
  <div class="ctl"><label for="ry-nx">厚度（cm）</label><input id="ry-nx" type="range" data-bind="nx" data-instant min="0" max="60" step="1" value="30"><output data-show="nx" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>搭建屏蔽层</h3>
  <p>一层层叠加，直到四束射线全被挡住。γ 射线永远不会降到恰好为零，只会降到极小的份额。</p>
  <div class="btns"><button class="btn ghost" data-act="add_paper">+ 纸</button><button class="btn ghost" data-act="add_al">+ 铝</button><button class="btn ghost" data-act="add_pb">+ 铅</button><button class="btn ghost" data-act="add_water">+ 水</button><button class="btn" data-act="clear">清空</button></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "alpha": "α",
  "beta": "β",
  "gamma": "γ",
  "neutron": "中子",
  "paper": "纸",
  "aluminium {#} mm": "铝 {#} mm",
  "Al {#} mm": "Al {#} mm",
  "lead {#} cm": "铅 {#} cm",
  "water {#} cm": "水 {#} cm",
  "no shield": "无屏蔽",
  "all four beams stopped": "四束射线全被挡住",
  "all four stopped": "四束全被挡住",
  "all through": "全部穿过",
  "stopped": "被挡住",
  "{#} % through": "{#} % 穿过",
  "{#} in {#}": "{#}/{#}",
  "{#} in {#} million": "{#}/({#}×10⁶)",
  "{#} in a billion": "{#}/10⁹",
  "flash = stopped inside the shield": "闪光 = 在屏蔽层内被挡住",
  "each source fires a steady beam": "每个源发射一束稳定的射线",
  "flash = stopped": "闪光 = 被挡住",
  "four beams": "四束射线",
  "not to scale": "未按比例",
  "drag ↔": "拖动 ↔",
  "gamma rays (caesium{#})": "γ 射线（铯{#}）",
  "cm of lead": "铅厚 cm",
  "share still going": "仍在前进的份额",
  "gets through: {#} % · halved every {#} mm of lead": "穿过：{#} % · 每 {#} mm 铅减半",
  "gets through: {#} in {#} · halved every {#} mm of lead": "穿过：{#}/{#} · 每 {#} mm 铅减半",
  "gets through: {#} in {#} million · halved every {#} mm of lead": "穿过：{#}/({#}×10⁶) · 每 {#} mm 铅减半",
  "gets through: {#} in a billion · halved every {#} mm of lead": "穿过：{#}/10⁹ · 每 {#} mm 铅减半",
  "gets through: all through · halved every {#} mm of lead": "穿过：全部 · 每 {#} mm 铅减半",
  "through: all · halved every {#} mm": "穿过：全部 · 每 {#} mm 减半",
  "through: {#} % · halved every {#} mm": "穿过：{#} % · 每 {#} mm 减半",
  "through: {#} in {#} · halved every {#} mm": "穿过：{#}/{#} · 每 {#} mm 减半",
  "through: {#} in {#} million · halved every {#} mm": "穿过：{#}/({#}×10⁶) · 每 {#} mm 减半",
  "through: {#} in a billion · halved every {#} mm": "穿过：{#}/10⁹ · 每 {#} mm 减半",
  "counted: {#} of {#}": "计数：{#}/{#}",
  "got through {#} % · bounced back {#} % · slowed and caught {#} %": "穿过 {#} % · 反弹 {#} % · 慢化后被俘获 {#} %",
  "through {#} % · back {#} % · caught {#} %": "穿过 {#} % · 反弹 {#} % · 被俘获 {#} %",
  "bright = fast neutron · red = hydrogen nucleus knocked away · green flash = swallowed": "亮 = 快中子 · 红 = 被撞飞的氢核 · 绿色闪光 = 被吞没",
  "bright = fast · dim = slowed": "亮 = 快 · 暗 = 已慢化",
  "simplified model": "简化模型",
});
