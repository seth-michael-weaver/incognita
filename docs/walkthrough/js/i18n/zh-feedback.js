/* Chinese: feedback (反应堆的稳定性与反馈) */
WT.L.ch.feedback = {
  num: "第1课", title: "反应堆的稳定性与反馈", short: "反馈",
  html: `
<div class="step">
  <h3>一个回路：功率、热量、反应性</h3>
  <p>功率升高会加热燃料和水，而它们的温度又改变反应性 <i>ρ</i>，反应性决定功率。引入一个阶跃反应性，观察信号沿回路传播一圈。系数为负时，它会把功率往回推。</p>
  <div class="ctl"><label for="fb-r">反应性阶跃（pcm）</label><input id="fb-r" type="range" data-bind="rs" data-instant min="50" max="300" step="10" value="200"><output data-show="rs" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">引入</button> <button class="btn ghost" data-act="fbRes">复位</button></div>
</div>
<div class="step">
  <h3>多普勒：快速的刹车</h3>
  <p>燃料越热，铀-238 不经裂变俘获的中子就越多（<a href="#doppler">多普勒展宽</a>）。燃料在几秒内就会升温，所以这道刹车最先起作用，而且在水堆中总是负的。这里它是唯一的反馈。</p>
  <div class="ctl"><label for="fb-d">多普勒系数（pcm/K）</label><input id="fb-d" type="range" data-bind="aD" data-instant min="-5" max="-1" step="0.1" value="-2.5"><output data-show="aD" data-fmt="1"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">引入</button> <button class="btn ghost" data-act="fbRes">复位</button></div>
</div>
<div class="step">
  <h3>慢化剂加入</h3>
  <p>水温升高，密度变小，慢化中子的能力就变差。在正常硼浓度下的压水堆中，这使慢化剂温度系数也为负：这是第二道、较慢的刹车，功率稳定在更低的水平。</p>
  <div class="ctl"><label for="fb-m">慢化剂系数（pcm/K）</label><input id="fb-m" type="range" data-bind="aM" data-instant min="-60" max="0" step="1" value="-30"><output data-show="aM" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">引入</button> <button class="btn ghost" data-act="fbRes">复位</button></div>
</div>
<div class="step">
  <h3>当反馈为正时</h3>
  <p>如果冷却剂项为正且超过多普勒效应，功率越高反应性就越大，功率便会失控。水堆在设计上采用负系数；有些堆型，例如低功率下的 RBMK，可能具有正的空泡系数。</p>
  <div class="ctl"><label for="fb-c">冷却剂系数（pcm/K）</label><input id="fb-c" type="range" data-bind="aM" data-instant min="-60" max="150" step="5" value="150"><output data-show="aM" data-fmt="0"></output></div>
  <div class="btns"><button class="btn" data-act="fbIns">引入</button> <button class="btn ghost" data-act="fbRes">复位</button></div>
</div>`,
};
Object.assign(WT.L.labels, {
  // loop arrows and nodes
  "heat": "热量",
  "heats water": "加热水",
  "chain reaction": "链式反应",
  "chain": "链式",
  "αD −": "αD −", "αM +": "αM +", "αM −": "αM −", "αM {#}": "αM {#}",
  "αC +": "αC +", "αC −": "αC −", "αC {#}": "αC {#}",
  "P {#} %": "P {#} %",
  "fuel +{#} K": "燃料 +{#} K",
  "fuel {#} K": "燃料 {#} K",
  "fuel ΔT +{#} K": "燃料 ΔT +{#} K",
  "fuel ΔT {#} K": "燃料 ΔT {#} K",
  "water +{#} K": "水 +{#} K",
  "water {#} K": "水 {#} K",
  "water ΔT +{#} K": "水 ΔT +{#} K",
  "water ΔT {#} K": "水 ΔT {#} K",
  "ρ +{#} pcm": "ρ +{#} pcm",
  "ρ {#} pcm": "ρ {#} pcm",
  // formulas
  "ρ = ρext + αD ΔTf + αM ΔTm": "ρ = ρext + αD ΔTf + αM ΔTm",
  "C dT/dt = P − h (T − Tc)": "C dT/dt = P − h (T − Tc)",
  "Doppler α_D = {a} pcm/K": "多普勒 α_D = {a} pcm/K",
  "moderator α_M = {a} pcm/K": "慢化剂 α_M = {a} pcm/K",
  "coolant α_C = {a} pcm/K": "冷却剂 α_C = {a} pcm/K",
  "inserted ρ_ext = {a}": "引入的 ρ_ext = {a}",
  // power trace
  "+{a} pcm": "+{a} pcm",
  "power": "功率",
  "last {#} s →": "最近 {#} s →",
  "last {#} seconds →": "最近 {#} 秒 →",
  // verdict
  "power ran away · protection would shut it down": "功率失控 · 保护系统会停堆",
  "power ran away · in a real plant the protection system would shut it down": "功率失控 · 在实际电站中，保护系统会使反应堆停堆",
  "steady at {#} % · press Insert": "稳定在 {#} % · 按“引入”",
  "steady at {#} % power · press Insert to add reactivity": "稳定在 {#} % 功率 · 按“引入”加入反应性",
  "power coefficient {a} pcm per {#} %: settles": "功率系数 {a} pcm / {#} %：趋于稳定",
  "power coefficient {a} pcm per {#} % power: self-stabilising": "功率系数 {a} pcm / {#} % 功率：自稳定",
  "power coefficient +{a} pcm per {#} %: runs away": "功率系数 +{a} pcm / {#} %：失控",
  "power coefficient +{a} pcm per {#} % power: runs away": "功率系数 +{a} pcm / {#} % 功率：失控",
  "illustrative model": "示意模型",
});
