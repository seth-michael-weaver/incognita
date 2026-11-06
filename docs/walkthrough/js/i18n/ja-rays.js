/* Japanese: rays (アルファ線、ベータ線、ガンマ線、中性子線) */
WT.L.ch.rays = {
  num: "レッスン 2", title: "アルファ線、ベータ線、ガンマ線、中性子線", short: "放射線",
  html: `
<div class="step">
  <h3>4種類の放射線</h3>
  <p><em class="a">アルファ線</em>は、陽子2個と中性子2個からなる重いかたまりです。<b>ベータ線</b>は速い電子です。<em class="g">ガンマ線</em>は光の一種ですが、エネルギーが高すぎて目には見えません。<em class="n">中性子</em>は電荷をまったくもちません。それぞれ、止められるものが違います。</p>
</div>
<div class="step">
  <h3>紙とアルミニウム</h3>
  <p>アルファ粒子は大きく電荷をもつので、すぐに原子にぶつかります。紙1枚で止まります。ベータ線の電子はもっと先まで進みますが、厚さ数ミリのアルミニウムで止まります。</p>
  <div class="btns"><button class="btn ghost" data-act="sh_paper" aria-pressed="true">紙</button><button class="btn ghost" data-act="sh_al" aria-pressed="false">アルミニウム</button></div>
</div>
<div class="step">
  <h3>ガンマ線：半分になっても、ゼロにはならない</h3>
  <p>ガンマ線は電荷をもたず、たいていは原子のそばを素通りします。鉛を1 cm進むごとに、どの光子にも同じ確率で吸収される機会があるので、一定の厚さごとに残りが半分になります。ビームは弱まりますが、ちょうどゼロになることはありません。</p>
  <div class="ctl"><label for="ry-pb">鉛（cm）</label><input id="ry-pb" type="range" data-bind="pb" data-instant min="0" max="5" step="0.1" value="1"><output data-show="pb" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>中性子：鉛では足りない</h3>
  <p>重い鉛の原子核に中性子がはね返されるのは、ボウリングの球にピンポン球が当たるようなもので、速さはほとんど変わりません。水の中の水素は中性子と同じ重さなので、ぶつかるたびに中性子は遅くなり、やがて吸収されるほど遅くなります。</p>
  <div class="btns"><button class="btn ghost" data-act="nm_pb" aria-pressed="true">鉛</button><button class="btn ghost" data-act="nm_water" aria-pressed="false">水</button></div>
  <div class="ctl"><label for="ry-nx">厚さ（cm）</label><input id="ry-nx" type="range" data-bind="nx" data-instant min="0" max="60" step="1" value="30"><output data-show="nx" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>遮蔽をつくる</h3>
  <p>4本のビームがすべて止まるまで層を重ねてみましょう。ガンマ線はちょうどゼロにはならず、ごくわずかな割合まで減るだけです。</p>
  <div class="btns"><button class="btn ghost" data-act="add_paper">+ 紙</button><button class="btn ghost" data-act="add_al">+ アルミニウム</button><button class="btn ghost" data-act="add_pb">+ 鉛</button><button class="btn ghost" data-act="add_water">+ 水</button><button class="btn" data-act="clear">クリア</button></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "alpha": "アルファ線",
  "beta": "ベータ線",
  "gamma": "ガンマ線",
  "neutron": "中性子",
  "paper": "紙",
  "Al {#} mm": "Al {#} mm",
  "aluminium {#} mm": "アルミニウム {#} mm",
  "lead {#} cm": "鉛 {#} cm",
  "water {#} cm": "水 {#} cm",
  "no shield": "遮蔽なし",
  "all four beams stopped": "4本のビームすべてを遮断",
  "all four stopped": "4本とも遮断",
  "each source fires a steady beam": "各線源が一定のビームを放つ",
  "flash = stopped inside the shield": "閃光 = 遮蔽の中で停止",
  "flash = stopped": "閃光 = 停止",
  "four beams": "4本のビーム",
  "not to scale": "縮尺は不正確",
  "stopped": "遮断",
  "all through": "全透過",
  "{#} % through": "{#} % 透過",
  "{#} in {#}": "{#}/{#}",
  "{#} in {#} million": "{#}/{#}百万",
  "{#} in a billion": "{#}/十億",
  "drag ↔": "ドラッグ ↔",
  "gamma rays (caesium{#})": "ガンマ線（セシウム{#}）",
  "cm of lead": "鉛の cm",
  "share still going": "まだ進んでいる割合",
  "gets through: {#} % · halved every {#} mm of lead": "透過：{#} % · 鉛 {#} mm ごとに半減",
  "gets through: {#} in {#} · halved every {#} mm of lead": "透過：{#}/{#} · 鉛 {#} mm ごとに半減",
  "gets through: {#} in {#} million · halved every {#} mm of lead": "透過：{#}/{#}百万 · 鉛 {#} mm ごとに半減",
  "gets through: {#} in a billion · halved every {#} mm of lead": "透過：{#}/十億 · 鉛 {#} mm ごとに半減",
  "through: all · halved every {#} mm": "透過：全部 · {#} mm ごとに半減",
  "through: {#} % · halved every {#} mm": "透過：{#} % · {#} mm ごとに半減",
  "through: {#} in {#} · halved every {#} mm": "透過：{#}/{#} · {#} mm ごとに半減",
  "through: {#} in {#} million · halved every {#} mm": "透過：{#}/{#}百万 · {#} mm ごとに半減",
  "through: {#} in a billion · halved every {#} mm": "透過：{#}/十億 · {#} mm ごとに半減",
  "counted: {#} of {#}": "計数：{#}/{#}",
  "got through {#} % · bounced back {#} % · slowed and caught {#} %": "透過 {#} % · はね返り {#} % · 減速して吸収 {#} %",
  "through {#} % · back {#} % · caught {#} %": "透過 {#} % · 反射 {#} % · 吸収 {#} %",
  "bright = fast neutron · red = hydrogen nucleus knocked away · green flash = swallowed": "明るい = 速い中性子 · 赤 = はじき飛ばされた水素原子核 · 緑の閃光 = 吸収",
  "bright = fast · dim = slowed": "明るい = 速い · 暗い = 減速",
  "simplified model": "簡略化したモデル",
});
