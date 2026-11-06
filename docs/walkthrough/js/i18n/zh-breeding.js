/* Chinese: breeding (增殖新燃料) */
WT.L.ch.breeding = {
  num: "第1课", title: "增殖新燃料", short: "增殖",
  html: `
<div class="step">
  <h3>可转换核素变成易裂变核素</h3>
  <p>铀-238 几乎不裂变，但它能俘获一个中子。再经过两次 β 衰变（每次核内都有一个中子变成质子），它就变成了容易裂变的钚-239。钍-232 也是如此，最终变成铀-233。</p>
  <div class="btns"><button class="btn ghost" data-act="bcU" aria-pressed="true">铀-238</button> <button class="btn ghost" data-act="bcT" aria-pressed="false">钍-232</button></div>
</div>
<div class="step">
  <h3>中子的收支</h3>
  <p>易裂变燃料每吸收一个中子，就放出 <i>η</i> 个新中子。其中一个必须引起下一次裂变，还有一些会损失掉；剩下的才能用于增殖。用铀-235 和慢中子，每烧掉一个易裂变核，只能产生约 0.6 个新的易裂变核。</p>
  <div class="btns"><button class="btn ghost" data-act="bfU5" aria-pressed="true">U-235</button> <button class="btn ghost" data-act="bfP9" aria-pressed="false">Pu-239</button> <button class="btn ghost" data-act="bfU3" aria-pressed="false">U-233</button></div>
  <div class="btns"><button class="btn ghost" data-act="bsT" aria-pressed="true">慢中子</button> <button class="btn ghost" data-act="bsF" aria-pressed="false">快中子</button></div>
</div>
<div class="step">
  <h3>快中子能增殖</h3>
  <p>要实现增殖，一个中子必须维持链式反应，至少还要有一个去产生新燃料，所以 <i>η</i> 超过 2 的部分必须大于损失。快堆中的钚-239 约为 2.4，绰绰有余。</p>
  <div class="ctl"><label for="br-l1">损失的中子</label><input id="br-l1" type="range" data-bind="L" data-instant min="0.05" max="0.8" step="0.01" value="0.2"><output data-show="L" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>用慢中子的钍</h3>
  <p>在慢中子下，钚-239 只有约 2.1，而铀-233 有 2.29。这点余量让钍反应堆只要浪费的中子极少，就能用慢中子增殖。把损失调低，直到它开始增殖。</p>
  <div class="ctl"><label for="br-l2">损失的中子</label><input id="br-l2" type="range" data-bind="L" data-instant min="0.05" max="0.8" step="0.01" value="0.35"><output data-show="L" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>转换比</h3>
  <p>转换比是每烧掉一个易裂变核所产生的易裂变核数。小于 1 时，燃料会慢慢耗尽（转换堆，如今天的水堆）；大于 1 时，反应堆最后拥有的燃料比开始时还多（增殖堆）。</p>
  <div class="btns"><button class="btn ghost" data-act="bfU5" aria-pressed="true">U-235</button> <button class="btn ghost" data-act="bfP9" aria-pressed="false">Pu-239</button> <button class="btn ghost" data-act="bfU3" aria-pressed="false">U-233</button></div>
  <div class="btns"><button class="btn ghost" data-act="bsT" aria-pressed="true">慢中子</button> <button class="btn ghost" data-act="bsF" aria-pressed="false">快中子</button></div>
</div>`,
};
Object.assign(WT.L.labels, {
  // chain scene
  "+ n": "+ n",
  "Np{#}": "Np{#}", "Pa{#}": "Pa{#}", "Pu{#}": "Pu{#}", "Th{#}": "Th{#}", "U{#}": "U{#}",
  "Th{#} → U{#}": "Th{#} → U{#}",
  "U{#} → Pu{#}": "U{#} → Pu{#}",
  "catch": "俘获",
  "fertile": "可转换",
  "fertile: barely splits": "可转换：几乎不裂变",
  "fissile": "易裂变",
  "fissile: splits easily": "易裂变：容易裂变",
  "{#} p": "{#} p",
  "{#} protons": "{#} 个质子",
  "{#} d": "{#} 天",
  "{#} min": "{#} min",
  "electron": "电子",
  "e⁻": "e⁻",
  "antineutrino": "反中微子",
  "a batch of {a} waiting · day {b}": "一批 {a} 在等待 · 第 {b} 天",
  "{a} waiting: day {b}": "{a} 等待中：第 {b} 天",
  "{a} % now {b}": "{a} % 已成 {b}",
  "after {#} weeks, {#} % has become Pu{#}": "{#} 周后，{#} % 已变成 Pu{#}",
  "after {#} months, {#} % has become U{#}": "{#} 个月后，{#} % 已变成 U{#}",
  "slow step: Np{#}, half-life {#} d": "慢的一步：Np{#}，半衰期 {#} 天",
  "slow step: Pa{#}, half-life {#} d": "慢的一步：Pa{#}，半衰期 {#} 天",
  "the slow step is Np{#} (half-life {#} days)": "最慢的一步是 Np{#}（半衰期 {#} 天）",
  "the slow step is Pa{#} (half-life {#} days)": "最慢的一步是 Pa{#}（半衰期 {#} 天）",
  // budget scene
  "slow neutrons": "慢中子",
  "fast neutrons": "快中子",
  "next fission": "下一次裂变",
  "next fission: keeps the chain going": "下一次裂变：维持链式反应",
  "breeds: U{#} → Pu{#}": "增殖：U{#} → Pu{#}",
  "breeds: Th{#} → U{#}": "增殖：Th{#} → U{#}",
  "lost": "损失",
  "lost: water, steel, poisons, leakage": "损失：水、钢、毒物、泄漏",
  "{a} per absorption": "每次吸收 {a}",
  "chain": "链式",
  "breed": "增殖",
  "η = {a}": "η = {a}",
  "η ≈ {a}": "η ≈ {a}",
  "{#}: breeding line": "{#}：增殖线",
  "neutrons per absorption": "每次吸收的中子数",
  "neutrons out per neutron absorbed in the fuel": "燃料每吸收一个中子放出的中子数",
  "conversion ratio ≈ η − {#} − lost = {a}: breeds": "转换比 ≈ η − {#} − 损失 = {a}：增殖",
  "conversion ratio ≈ η − {#} − lost = {a}: breeds, makes more fuel than it burns": "转换比 ≈ η − {#} − 损失 = {a}：增殖，产生的燃料多于消耗的",
  "conversion ratio ≈ η − {#} − lost = {a}: converts": "转换比 ≈ η − {#} − 损失 = {a}：转换",
  "conversion ratio ≈ η − {#} − lost = {a}: converts, makes less fuel than it burns": "转换比 ≈ η − {#} − 损失 = {a}：转换，产生的燃料少于消耗的",
  // conversion-ratio scene
  "U{#} (fertile)": "U{#}（可转换）",
  "Th{#} (fertile)": "Th{#}（可转换）",
  "split": "已裂变",
  "split (fission products)": "已裂变（裂变产物）",
  "burned {a}": "消耗 {a}",
  "made {a}": "产生 {a}",
  "{a} · slow neutrons": "{a} · 慢中子",
  "{a} · fast neutrons": "{a} · 快中子",
  "conversion ratio {a}: a breeder": "转换比 {a}：增殖堆",
  "conversion ratio {a}: a converter": "转换比 {a}：转换堆",
  "illustration": "示意图",
});
