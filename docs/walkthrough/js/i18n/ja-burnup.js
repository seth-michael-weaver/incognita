/* Japanese: burnup (燃料の燃焼度) */
WT.L.ch.burnup = {
  num: "レッスン 1", title: "燃料の燃焼度", short: "燃焼度",
  html: `
<div class="step">
  <h3>ペレットの一生</h3>
  <p>新しい燃料ペレットから原子を1000個取り出しました。45個がウラン235で、残りはウラン238です。原子炉を運転すると、ウラン235が分裂する一方で新しい原子が現れるのがわかります。<b>燃焼度</b>は取り出したエネルギーを、ウラン1トンあたりのギガワット日で数えたものです。軽水炉の燃料は約45〜55で取り出されます。</p>
  <div class="ctl"><label for="bu-d1">全出力での日数</label><input id="bu-d1" type="range" data-bind="d" data-instant min="0" max="1400" step="10" value="400"><output data-show="d" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>プルトニウムも加わる</h3>
  <p>ウラン238は中性子を捕獲してプルトニウム239になり、これも分裂します。燃料の寿命の後半には核分裂の半分以上がプルトニウムで起こり、寿命全体ではエネルギーの約3分の1がプルトニウムから得られます。</p>
  <div class="ctl"><label for="bu-d2">全出力での日数</label><input id="bu-d2" type="range" data-bind="d" data-instant min="0" max="1400" step="10" value="1000"><output data-show="d" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>毒物質がたまる</h3>
  <p>核分裂のたびに2個の核分裂生成物が残り、その一部は中性子を吸収します。ウラン235が減って毒物質が増えると、<i>k</i><sub>∞</sub>（この燃料を無限に並べた格子での、核分裂1回あたりの新しい核分裂の数）は下がっていき、やがて燃料だけでは連鎖反応を保てなくなります。</p>
  <div class="ctl"><label for="bu-d3">全出力での日数</label><input id="bu-d3" type="range" data-bind="d" data-instant min="0" max="1400" step="10" value="700"><output data-show="d" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>ホウ素と燃料交換</h3>
  <p>炉心には新しい燃料、中くらいの燃料、古い燃料が混ざっています。新しい燃料は反応度が大きすぎるので、冷却水に溶かしたホウ素が余分な中性子を吸収し、ホウ素は少しずつ薄められます。ホウ素がゼロになると、最も古い3分の1が取り出され、新しい燃料が入ります。</p>
  <div class="ctl"><label for="bu-m">全出力での月数</label><input id="bu-m" type="range" data-bind="m" data-instant min="0" max="54" step="0.5" value="8"><output data-show="m" data-fmt="1"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "GWd/t →": "GWd/t →",
  "Pu": "Pu",
  "U{#}": "U{#}",
  "boron (ppm)": "ホウ素 (ppm)",
  "boron in the water (ppm)": "水中のホウ素 (ppm)",
  "burnup (GWd/t) →": "燃焼度 (GWd/t) →",
  "can't keep a chain going alone": "単独では連鎖を保てない",
  "this fuel alone can no longer keep a chain going": "この燃料だけではもう連鎖反応を保てない",
  "k∞ reaches {#}": "k∞ が {#} に到達",
  "cycle {a} months · fuel leaves at {b} GWd/t": "サイクル {a} か月 · 燃料は {b} GWd/t で取り出し",
  "each dot: one atom in a thousand": "点1つ：原子1000個中の1個",
  "each dot: {#} atom in {#}": "点1つ：{#} 個 / {#} 個",
  "energy so far": "これまでのエネルギー",
  "fission products": "核分裂生成物",
  "fission products (pairs)": "核分裂生成物（2個1組）",
  "fission products catch {a} % of neutrons": "核分裂生成物が中性子の {a} % を吸収",
  "fissions": "核分裂",
  "fissions now": "現在の核分裂",
  "fresh": "新燃料",
  "one cycle old": "1サイクル経過",
  "two cycles old": "2サイクル経過",
  "{#} cycle": "{#} サイクル",
  "{#} cycles": "{#} サイクル",
  "illustrative model": "説明用のモデル",
  "k = {#}": "k = {#}",
  "k∞ = {a}": "k∞ = {a}",
  "months at full power →": "全出力での月数 →",
  "months →": "月数 →",
  "other Pu": "他の Pu",
  "other plutonium": "他のプルトニウム",
  "plutonium": "プルトニウム",
  "plutonium's share": "プルトニウムの割合",
  "plutonium{#}": "プルトニウム{#}",
  "uranium{#}": "ウラン{#}",
  "uranium{#}: the remaining ~{#}–{#} %": "ウラン{#}：残りの約 {#}–{#} %",
  "reload": "燃料交換",
  "split": "分裂済み",
  "typical discharge": "典型的な取出し",
  "typical discharge {#}–{#}": "典型的な取出し {#}–{#}",
  "{a} days · burnup {b} GWd/t": "{a} 日 · 燃焼度 {b} GWd/t",
  "{a} in {#}": "{a} / {#}",
  "{a} ppm": "{a} ppm",
});
