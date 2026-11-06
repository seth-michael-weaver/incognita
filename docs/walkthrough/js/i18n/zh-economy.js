/* Chinese: economy (中子的收支) */
WT.L.ch.economy = {
  num: "第1课", title: "中子的收支", short: "中子收支",
  html: `
<div class="step">
  <h3>一千个中子</h3>
  <p>跟随 1000 个快中子走完一代。少数引起额外的裂变，一些泄漏出去，一些在途中被俘获，其余的使铀-235 裂变，产生下一代的一千个中子。六个因子相乘得到 <i>k</i> = <i>η f p ε P</i><sub>FNL</sub> <i>P</i><sub>TNL</sub>。</p>
</div>
<div class="step">
  <h3>富集度</h3>
  <p>燃料中的铀-235 越多，就有越多的中子被吸收在能引起裂变的地方。用天然铀（0.7 %）和普通水，<i>k</i> 永远达不到 1。</p>
  <div class="ctl"><label for="eco-e">铀-235（%）</label><input id="eco-e" type="range" data-bind="enr" min="0.7" max="5" step="0.1" value="3"><output data-show="enr" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>燃料棒之间的水</h3>
  <p>水太少，正在慢化的中子会被铀-238 俘获；水太多，水本身又会吸收它们。存在一个最佳比例，而水堆的设计略低于这个比例。</p>
  <div class="ctl"><label for="eco-m">水与燃料之比（× 典型值）</label><input id="eco-m" type="range" data-bind="m" min="0.3" max="4" step="0.05" value="1"><output data-show="m" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>尺寸</h3>
  <p>在表面附近产生的中子可能逃逸。小堆芯泄漏的中子太多；大一些的堆芯能把它们留住。找出 <i>k</i> 越过 1 时的尺寸。</p>
  <div class="ctl"><label for="eco-s">堆芯尺寸（× 典型值）</label><input id="eco-s" type="range" data-bind="s" min="0.3" max="2" step="0.05" value="0.6"><output data-show="s" data-fmt="2"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  // stations around the loop
  "fast fission": "快中子裂变",
  "fast leak": "快中子泄漏",
  "leaks out, fast": "快中子泄漏出去",
  "U{#} catches": "U{#} 俘获",
  "caught by U{#}": "被 U{#} 俘获",
  "slow leak": "慢中子泄漏",
  "leaks out, slow": "慢中子泄漏出去",
  "water, steel…": "水、钢……",
  "water, steel, boron": "水、钢、硼",
  "P fast {#}": "P 快 {#}",
  "P slow {#}": "P 慢 {#}",
  "p {#}": "p {#}",
  "f {#}": "f {#}",
  "slowing": "慢化",
  "slowing down": "慢化",
  "{#} split U{#}": "{#} 个使 U{#} 裂变",
  "U{#}": "U{#}",
  // k
  "next: {#}": "下一代：{#}",
  "next generation: {#}": "下一代：{#}",
  "k = {#}": "k = {#}",
  "critical: steady": "临界：保持稳定",
  "grows": "增长",
  "dies away": "逐渐衰亡",
  // water curve
  "best ≈ {#}×": "最佳 ≈ {#}×",
  "less water": "水更少",
  "more water": "水更多",
  // size
  "{#} % leak out": "{#} % 泄漏出去",
  // bottom line
  "k = η {#} × f {#} × p {#} × ε {#} × P {#} × P {#}": "k = η {#} × f {#} × p {#} × ε {#} × P {#} × P {#}",
  "textbook set (D&H); trends illustrative": "教科书数值（D&H）；趋势为示意",
  "factors: textbook set (Duderstadt & Hamilton) at {#} %; slider trends illustrative": "因子：{#} % 时的教科书数值（Duderstadt & Hamilton）；滑块趋势为示意",
});
