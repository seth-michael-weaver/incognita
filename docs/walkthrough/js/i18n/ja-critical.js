/* Japanese: critical (第21章、臨界と原子炉の制御) */
WT.L.ch.critical = {
  num: "第21章", title: "臨界と原子炉の制御", short: "臨界",
  html: `
<div class="step">
  <h3>増倍率</h3>
  <p>1回の核分裂は数個の中性子を放出します。そのうちのいくつかが次の核分裂を起こし、残りは失われます。<b>増倍率</b><i>k</i>は、1回の核分裂が新たに何回の核分裂につながるかを表し、世代ごとに中性子の数は<i>k</i>倍になります。1より大きければ連鎖反応は成長し、1より小さければ減衰します。</p>
  <div class="ctl"><label for="cri-k">増倍率 k</label><input id="cri-k" type="range" data-bind="k" data-instant min="0.95" max="1.05" step="0.05" value="1.05"><output data-show="k" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>遅発中性子</h3>
  <p>中性子のわずかな割合（0.65 %）は、先に崩壊する核分裂片から、数秒遅れて到着します。この遅れた中性子が反応の進み具合を決めるため、成長は一瞬から数分へと遅くなります。グラフは10倍速で進みます。</p>
  <div class="ctl"><label for="cri-k2">増倍率 k</label><input id="cri-k2" type="range" data-bind="kd" data-instant min="0.998" max="1.002" step="0.0005" value="1.001"><output data-show="kd" data-fmt="4"></output></div>
  <div class="btns"><button class="btn ghost" data-act="delayed" aria-pressed="true">遅発中性子</button></div>
</div>
<div class="step">
  <h3>臨界</h3>
  <p>臨界実験では、出力が一定になるまで制御棒を動かします。その設定では<i>k</i>がちょうど1であり、その制御棒の位置が測定結果です。見つけてみてください。表示には<i>k</i>が小数第5位まで出ます。</p>
  <div class="ctl"><label for="cri-rod">挿入した制御棒（%）</label><input id="cri-rod" type="range" data-bind="ins" data-instant min="35" max="75" step="1" value="45"><output data-show="ins" data-fmt="0"></output></div>
</div>`,
};
/* attributes referenced in the English chapter script (for the structure check): data-act="delayed" data-act="delayed" */

// canvas labels added 2026-10-29 (I18NLABELS_B)
Object.assign(WT.L.labels, {
  "generations →": "世代 →",
  "k = {#}: dies away": "k = {#}：減衰",
  "k = {#}: steady": "k = {#}：一定",
  "k = {#}: grows": "k = {#}：成長",
  "{#} generations last under {#} s in a water reactor": "{#} 世代は軽水炉で {#} s 未満",
  "illustration": "イメージ図",
  "amber: fission fragments that emit a neutron seconds later": "琥珀色：数秒後に中性子を出す核分裂片",
  "{#} s": "{#} s",
  "time →": "時間 →",
  "×{#} speed": "×{#} 倍速",
  "with delayed: doubles every {#} s": "遅発中性子あり：{#} s ごとに倍増",
  "prompt only: doubles every {#} ms": "即発のみ：{#} ms ごとに倍増",
  "k = {#} · {#} % of neutrons delayed about {#} s (one-group average)": "k = {#} · 中性子の {#} % が約 {#} s 遅れる（1群平均）",
  "rods {#} % in": "制御棒 {#} % 挿入",
  "k = {#} · doubles every {#} min": "k = {#} · {#} 分ごとに倍増",
});
