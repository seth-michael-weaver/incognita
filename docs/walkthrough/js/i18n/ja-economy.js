/* Japanese: economy (中性子の収支) */
WT.L.ch.economy = {
  num: "レッスン 3", title: "中性子の収支", short: "中性子の収支",
  html: `
<div class="step">
  <h3>1000個の中性子</h3>
  <p>1000個の高速中性子を1世代分追いかけてみましょう。いくつかは余分な核分裂を起こし、いくつかは外へ漏れ、いくつかは途中で捕獲され、残りがウラン235を分裂させて次の1000個をつくります。6つの因子を掛け合わせると<i>k</i> = <i>η f p ε P</i><sub>FNL</sub> <i>P</i><sub>TNL</sub>になります。</p>
</div>
<div class="step">
  <h3>濃縮度</h3>
  <p>燃料中のウラン235が多いほど、核分裂を起こす場所で吸収される中性子が増えます。天然ウラン（0.7 %）と普通の水では、<i>k</i>は決して1に届きません。</p>
  <div class="ctl"><label for="eco-e">ウラン235（%）</label><input id="eco-e" type="range" data-bind="enr" min="0.7" max="5" step="0.1" value="3"><output data-show="enr" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>燃料棒の間の水</h3>
  <p>水が少なすぎると、減速中の中性子がウラン238に捕獲されます。多すぎると、今度は水そのものが中性子を吸収します。最適な比があり、軽水炉はそれより少し下に設計されています。</p>
  <div class="ctl"><label for="eco-m">燃料あたりの水（標準の何倍か）</label><input id="eco-m" type="range" data-bind="m" min="0.3" max="4" step="0.05" value="1"><output data-show="m" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>大きさ</h3>
  <p>表面近くで生まれた中性子は外へ逃げられます。小さな炉心では漏れが多すぎ、大きな炉心では中性子を保てます。<i>k</i>が1を超える大きさを見つけてください。</p>
  <div class="ctl"><label for="eco-s">炉心の大きさ（標準の何倍か）</label><input id="eco-s" type="range" data-bind="s" min="0.3" max="2" step="0.05" value="0.6"><output data-show="s" data-fmt="2"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "fast fission": "高速核分裂",
  "fast leak": "高速漏れ",
  "leaks out, fast": "高速で漏れる",
  "U{#} catches": "U{#} が捕獲",
  "caught by U{#}": "U{#} に捕獲される",
  "slow leak": "熱中性子の漏れ",
  "leaks out, slow": "減速後に漏れる",
  "water, steel…": "水、鋼…",
  "water, steel, boron": "水、鋼、ホウ素",
  "P fast {#}": "P 高速 {#}",
  "P slow {#}": "P 熱 {#}",
  "p {#}": "p {#}",
  "f {#}": "f {#}",
  "U{#}": "U{#}",
  "slowing": "減速",
  "slowing down": "減速",
  "{#} split U{#}": "{#} 個が U{#} を分裂",
  "next: {#}": "次：{#}",
  "next generation: {#}": "次の世代：{#}",
  "k = {#}": "k = {#}",
  "critical: steady": "臨界：一定",
  "grows": "成長",
  "dies away": "減衰",
  "best ≈ {#}×": "最適 ≈ {#}×",
  "less water": "水が少ない",
  "more water": "水が多い",
  "{#} % leak out": "{#} % が漏れる",
  "k = η {#} × f {#} × p {#} × ε {#} × P {#} × P {#}": "k = η {#} × f {#} × p {#} × ε {#} × P {#} × P {#}",
  "textbook set (D&H); trends illustrative": "教科書の値（D&H）、傾向は説明用",
  "factors: textbook set (Duderstadt & Hamilton) at {#} %; slider trends illustrative": "因子：教科書の値（Duderstadt & Hamilton、{#} %）、スライダーによる傾向は説明用",
});
