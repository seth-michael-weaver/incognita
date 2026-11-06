/* Simplified Chinese (简体中文): sandbox (搭建一座反应堆) */
WT.L.ch.sandbox = {
  num: "第1课", title: "搭建一座反应堆", short: "搭建反应堆", lead: "选择燃料、慢化剂、冷却剂和尺寸，看看链式反应能否自持。一个简化的教科书模型。",
  html: `
<div class="step">
  <h3>四因子</h3>
  <p>如果没有中子泄漏，每吸收一个中子就会产生 <i>k</i><sub>∞</sub> = <i>η f p ε</i> 个新中子；这座天然铀石墨堆刚好够格。</p>
</div>
<div class="step">
  <h3>选择慢化剂</h3>
  <p>使用天然铀时，只有重水或石墨能让 <i>k</i><sub>∞</sub> 超过 1：轻水慢化中子的本领很好，但吸收得太多。</p>
  <div class="btns" role="group" aria-label="慢化剂"><button class="btn ghost" data-act="mo_h2o">轻水</button> <button class="btn ghost" data-act="mo_d2o">重水</button> <button class="btn ghost" data-act="mo_c">石墨</button></div>
  <div class="ctl"><label for="sb-m1">慢化剂与燃料之比</label><input id="sb-m1" type="range" data-bind="lm" min="-0.5" max="2.3" step="0.01" value="0.3"><output class="sb-m"></output></div>
</div>
<div class="step">
  <h3>浓缩燃料</h3>
  <p>只需百分之几的铀-235，普通水就能用，所以今天大多数反应堆都采用它。</p>
  <div class="btns" role="group" aria-label="燃料"><button class="btn ghost" data-act="fu_nat">天然铀</button> <button class="btn ghost" data-act="fu_leu">浓缩铀</button> <button class="btn ghost" data-act="fu_mox">MOX（Pu）</button> <button class="btn ghost" data-act="fu_th">钍 + U-233</button></div>
  <div class="ctl"><label for="sb-e1">易裂变份额（%）</label><input id="sb-e1" type="range" data-bind="enr" min="0.7" max="30" step="0.1" value="3"><output data-show="enr" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>尺寸与泄漏</h3>
  <p>中子会从表面逃逸，所以 <i>k</i> = <i>k</i><sub>∞</sub> / (1 + <i>M</i>²<i>B</i>²)。把这座天然铀石墨堆的边缘拖到虚线圆处。</p>
  <div class="ctl"><label for="sb-r1">堆芯半径（m）</label><input id="sb-r1" type="range" data-bind="R" min="0.2" max="6" step="0.05" value="2"><output data-show="R" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>当冷却剂沸腾时</h3>
  <p>在用水冷却的石墨堆芯中，沸腾会提高 <i>k</i>，因为水的吸收作用大于慢化作用：这正是切尔诺贝利 RBMK 的缺陷。试试其他冷却剂。</p>
  <div class="btns" role="group" aria-label="冷却剂"><button class="btn ghost" data-act="co_h2o">水</button> <button class="btn ghost" data-act="co_gas">CO₂ / 氦</button> <button class="btn ghost" data-act="co_na">钠</button></div>
</div>
<div class="step">
  <h3>自己搭一座</h3>
  <p>随你搭配。快堆没有慢化剂，需要多得多的易裂变燃料。</p>
  <div class="btns" role="group" aria-label="燃料"><button class="btn ghost" data-act="fu_nat">天然铀</button> <button class="btn ghost" data-act="fu_leu">浓缩铀</button> <button class="btn ghost" data-act="fu_mox">MOX（Pu）</button> <button class="btn ghost" data-act="fu_th">钍 + U-233</button></div>
  <div class="ctl"><label for="sb-e2">易裂变份额（%）</label><input id="sb-e2" type="range" data-bind="enr" min="0.7" max="30" step="0.1" value="3"><output data-show="enr" data-fmt="1"></output></div>
  <div class="btns" role="group" aria-label="慢化剂"><button class="btn ghost" data-act="mo_none">无慢化剂</button> <button class="btn ghost" data-act="mo_h2o">轻水</button> <button class="btn ghost" data-act="mo_d2o">重水</button> <button class="btn ghost" data-act="mo_c">石墨</button></div>
  <div class="ctl"><label for="sb-m2">慢化剂与燃料之比</label><input id="sb-m2" type="range" data-bind="lm" min="-0.5" max="2.3" step="0.01" value="0.3"><output class="sb-m"></output></div>
  <div class="btns" role="group" aria-label="冷却剂"><button class="btn ghost" data-act="co_h2o">水</button> <button class="btn ghost" data-act="co_d2o">重水</button> <button class="btn ghost" data-act="co_gas">CO₂ / 氦</button> <button class="btn ghost" data-act="co_na">钠</button> <button class="btn ghost" data-act="co_pb">铅</button> <button class="btn ghost" data-act="co_salt">熔盐</button></div>
  <div class="ctl"><label for="sb-r2">堆芯半径（m）</label><input id="sb-r2" type="range" data-bind="R" min="0.2" max="6" step="0.05" value="2"><output data-show="R" data-fmt="2"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "CO₂ / helium gas coolant": "CO₂ / 氦气冷却剂",
  "MOX {#} % Pu": "MOX {#} % Pu",
  "MOX, {#} % plutonium{#}": "MOX，{#} % 钚{#}",
  "R {#} m": "R {#} m",
  "absorbed in fuel": "被燃料吸收",
  "can never sustain a chain, at any size": "无论多大都无法维持链式反应",
  "caught by fuel": "被燃料俘获",
  "coolant boils away: k ↑": "冷却剂沸干：k ↑",
  "coolant boils: k ↑": "冷却剂沸腾：k ↑",
  "coolant boils: k ≈": "冷却剂沸腾：k ≈",
  "coolant lost: k barely changes": "失去冷却剂：k 几乎不变",
  "coolant lost: k ↑": "失去冷却剂：k ↑",
  "critical size": "临界尺寸",
  "escape capture": "逃脱俘获",
  "f": "f",
  "fast fission": "快中子裂变",
  "fission": "裂变",
  "fuel": "燃料",
  "fuel heats up: k ↓ (Doppler)": "燃料升温：k ↓（多普勒）",
  "fuel hotter: k ↓": "燃料变热：k ↓",
  "graphite moderator": "石墨慢化剂",
  "graphite moderator · CO₂ / helium gas coolant": "石墨慢化剂 · CO₂ / 氦气冷却剂",
  "graphite moderator · water coolant": "石墨慢化剂 · 水冷却剂",
  "k": "k",
  "k∞": "k∞",
  "leak": "泄漏",
  "leak out": "泄漏出去",
  "light water moderator": "轻水慢化剂",
  "light water moderator · water coolant": "轻水慢化剂 · 水冷却剂",
  "mod./cool.": "慢化/冷却",
  "moderator, coolant": "慢化剂、冷却剂",
  "natural U": "天然铀",
  "natural uranium ({#} % U{#})": "天然铀（{#} % U{#}）",
  "never critical": "永不临界",
  "no chain, any size": "多大都无链式反应",
  "no leakage": "无泄漏",
  "no moderator: a fast reactor · sodium coolant": "无慢化剂：快堆 · 钠冷却剂",
  "no moderator: fast": "无慢化剂：快堆",
  "no size is big enough": "多大都不够",
  "p": "p",
  "per fuel absorption": "每次燃料吸收",
  "radius {#} m": "半径 {#} m",
  "radius {#} m · drag the edge": "半径 {#} m · 拖动边缘",
  "simplified model": "简化模型",
  "simplified one-group model · illustration": "简化单群模型 · 示意",
  "stays in": "留在堆内",
  "stays in (M² {#} cm²)": "留在堆内（M² {#} cm²）",
  "sustains a chain, {#} % to spare (ρ)": "可维持链式反应，余量 {#} %（ρ）",
  "sustains: +{#} % spare": "可维持：余量 +{#} %",
  "too small: critical at radius {#} m": "太小：半径 {#} m 时才临界",
  "too small: needs {#} m": "太小：需要 {#} m",
  "uranium, {#} % U{#}": "铀，{#} % U{#}",
  "water boils: k ↑": "水沸腾：k ↑",
  "water boils: k ↓": "水沸腾：k ↓",
  "water coolant": "水冷却剂",
  "water heats or boils: k ↑": "水升温或沸腾：k ↑",
  "water heats or boils: k ↓": "水升温或沸腾：k ↓",
  "where the neutrons go": "中子的去向",
  "{#} % U{#}": "{#} % U{#}",
  "enriched U": "浓缩铀",
  "light water": "轻水",
  "heavy water": "重水",
  "lead": "铅",
  "molten salt": "熔盐",
  "sodium": "钠",
  "coolant": "冷却剂",
  "= η f, if nothing leaked": "= η f，若无泄漏",
  "= η f p ε, if nothing leaked": "= η f p ε，若无泄漏",
  "stays in: {#} / ({#} + M²B²), M² = {#} cm²": "留在堆内：{#} / ({#} + M²B²)，M² = {#} cm²",
  "neutrons per absorption in fuel": "燃料每吸收一个中子产生的中子数",
  "share absorbed in fuel": "被燃料吸收的份额",
  "no slowing down, no resonance loss": "无慢化，无共振损失",
  "escape capture while slowing": "慢化时逃脱俘获",
  "fast fission counted in η": "快中子裂变已计入 η",
  "bonus from fast fission": "快中子裂变的增益",
  "thorium, {#} % U{#}": "钍，{#} % U{#}",
  "Th + {#} % U{#}": "Th + {#} % U{#}",
  "uranium, {#} % U{#} (highly enriched)": "铀，{#} % U{#}（高浓铀）",
  "critical at {#} m": "{#} m 时临界",
  "coolant heats: k ↑": "冷却剂升温：k ↑",
  "coolant heats: k ↓": "冷却剂升温：k ↓",
  "coolant boils away: k ↓": "冷却剂沸干：k ↓",
  "coolant lost: k ↓": "失去冷却剂：k ↓",
  "heavy water coolant": "重水冷却剂",
  "sodium coolant": "钠冷却剂",
  "lead coolant": "铅冷却剂",
  "molten salt coolant": "熔盐冷却剂",
  "heavy water moderator": "重水慢化剂",
  "heavy water moderator · heavy water coolant": "重水慢化剂 · 重水冷却剂",
  "heavy water moderator · water coolant": "重水慢化剂 · 水冷却剂",
  "graphite moderator · sodium coolant": "石墨慢化剂 · 钠冷却剂",
  "no moderator: a fast reactor · lead coolant": "无慢化剂：快堆 · 铅冷却剂",
  "no moderator: a fast reactor · CO₂ / helium gas coolant": "无慢化剂：快堆 · CO₂ / 氦气冷却剂",
  "no moderator: a fast reactor · molten salt coolant": "无慢化剂：快堆 · 熔盐冷却剂",
  "water moderates": "由水慢化",
  "heavy water moderates": "由重水慢化",
  "no moderator, but the water moderates": "无慢化剂，但水起慢化作用",
  "no moderator, but the heavy water moderates": "无慢化剂，但重水起慢化作用",
});
