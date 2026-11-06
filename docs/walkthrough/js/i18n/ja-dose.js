/* Japanese: dose (放射線の線量) */
WT.L.ch.dose = {
  num: "レッスン 3", title: "放射線の線量", short: "線量",
  html: `
<div class="step">
  <h3>シーベルトは何を測るのか</h3>
  <p>線量はまず、体1キログラムあたりに吸収されたエネルギーとして測ります。<b>シーベルト</b>は、そのエネルギーに体への害の大きさで重みをつけたものです。アルファ粒子が運ぶエネルギーは、少数の密な飛跡に詰め込まれているので、同じエネルギーでもガンマ線の20倍に数えます。</p>
  <div class="btns"><button class="btn ghost" data-act="rg" aria-pressed="true">ガンマ線</button><button class="btn ghost" data-act="ra" aria-pressed="false">アルファ粒子</button></div>
</div>
<div class="step">
  <h3>身近な線量</h3>
  <p>この塔の目盛りは、1つ上がるごとに10倍になります。光る玉をドラッグして比べてみましょう。胸部CT検査1回はバナナ数千本分、自然放射線の1年分は飛行機数十回分の線量です。</p>
  <div class="ctl"><label for="ds-l">線量</label><input id="ds-l" type="range" data-bind="ld" data-instant min="-7" max="1" step="0.02" value="-2.15"><output class="ds-out"></output></div>
</div>
<div class="step">
  <h3>あなたの1年を積み上げる</h3>
  <p>だれでも自然から年に約2.4ミリシーベルトを受けています。その大部分は、地面から出るラドンガスによるものです。自分の飛行機の利用、検査、住む場所の標高を加えてみましょう。</p>
  <div class="ctl"><label for="ds-f">大西洋横断フライト（回）</label><input id="ds-f" type="range" data-bind="fl" data-instant min="0" max="40" step="1" value="4"><output data-show="fl" data-fmt="0"></output></div>
  <div class="ctl"><label for="ds-ct">胸部CT検査（回）</label><input id="ds-ct" type="range" data-bind="ct" data-instant min="0" max="3" step="1" value="0"><output data-show="ct" data-fmt="0"></output></div>
  <div class="ctl"><label for="ds-h">住まいの標高（m）</label><input id="ds-h" type="range" data-bind="alt" data-instant min="0" max="3500" step="50" value="300"><output data-show="alt" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>一度に受ける大きな線量</h3>
  <p>約100ミリシーベルト以下では、がんのリスクが増えるとしても小さすぎて測れません。安全の規則では、リスクは線量に比例して増えると仮定しています。一度に約1シーベルトを受けると、細胞があまりに多く傷つくため、放射線障害が始まります。</p>
  <div class="ctl"><label for="ds-a">一度に受ける線量</label><input id="ds-a" type="range" data-bind="la" data-instant min="-3" max="1" step="0.02" value="-1"><output class="ds-out2"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  // units and readouts
  "{#} µSv": "{#} µSv",
  "{#} mSv": "{#} mSv",
  "{#} Sv": "{#} Sv",
  "mSv": "mSv",
  // tissue
  "cell nuclei in a patch of body": "体の一部の細胞核",
  "cell nuclei in a patch of body tissue": "体の組織の一部にある細胞核",
  "{#} milligray of alpha: a few cells hit hard": "アルファ線 {#} ミリグレイ：少数の細胞に強い打撃",
  "{#} milligray of gamma: about one track per cell": "ガンマ線 {#} ミリグレイ：細胞1個に約1本の飛跡",
  "same energy · counts as {#} millisieverts": "同じエネルギー · {#} ミリシーベルトと数える",
  "counts as {#} millisievert": "{#} ミリシーベルトと数える",
  "illustration": "イメージ図",
  // dose tower items
  "eating a banana  ·  {#} µSv": "バナナを1本食べる  ·  {#} µSv",
  "banana  ·  {#} µSv": "バナナ  ·  {#} µSv",
  "dental X-ray  ·  {#} µSv": "歯科X線撮影  ·  {#} µSv",
  "chest X-ray  ·  {#} µSv": "胸部X線撮影  ·  {#} µSv",
  "flight across the Atlantic  ·  {#} µSv": "大西洋横断フライト  ·  {#} µSv",
  "Atlantic flight  ·  {#} µSv": "大西洋便  ·  {#} µSv",
  "a year of natural background  ·  {#} mSv": "自然放射線の1年分  ·  {#} mSv",
  "{#} yr background  ·  {#} mSv": "自然放射線 {#} 年  ·  {#} mSv",
  "chest CT scan  ·  {#} mSv": "胸部CT検査  ·  {#} mSv",
  "chest CT  ·  {#} mSv": "胸部CT  ·  {#} mSv",
  "yearly limit for radiation workers  ·  {#} mSv": "放射線業務従事者の年間限度  ·  {#} mSv",
  "worker limit/yr  ·  {#} mSv": "従事者の年限度  ·  {#} mSv",
  "a year on the Kerala coast (high spots)  ·  {#} mSv": "ケララ海岸で1年（高い地点）  ·  {#} mSv",
  "Kerala, {#} yr  ·  {#} mSv": "ケララ、{#} 年  ·  {#} mSv",
  "a year in the highest Ramsar homes  ·  {#} mSv": "ラムサールの最も高い家で1年  ·  {#} mSv",
  "Ramsar, {#} yr  ·  {#} mSv": "ラムサール、{#} 年  ·  {#} mSv",
  "at once: radiation sickness begins  ·  {#} Sv": "一度に：放射線障害が始まる  ·  {#} Sv",
  "at once: about half die untreated  ·  {#} Sv": "一度に：治療しないと約半数が死亡  ·  {#} Sv",
  "{#} Sv at once  ·  {#} Sv": "一度に {#} Sv  ·  {#} Sv",
  "{#}–{#} Sv at once  ·  {#} Sv": "一度に {#}–{#} Sv  ·  {#} Sv",
  "typical values": "代表的な値",
  // dose tower comparison line
  "{#} µSv: the dose of {#} bananas": "{#} µSv：バナナ {#} 本分の線量",
  "{#} mSv: the dose of {#} bananas": "{#} mSv：バナナ {#} 本分の線量",
  "{#} µSv: {#} bananas, or {#} flights": "{#} µSv：バナナ {#} 本、またはフライト {#} 回",
  "{#} µSv: {#} thousand bananas, or {#} flights": "{#} µSv：バナナ {#} 千本、またはフライト {#} 回",
  "{#} µSv: {#} million bananas, or {#} flights": "{#} µSv：バナナ {#} 百万本、またはフライト {#} 回",
  "{#} µSv: {#} bananas, or {#} thousand flights": "{#} µSv：バナナ {#} 本、またはフライト {#} 千回",
  "{#} µSv: {#} thousand bananas, or {#} thousand flights": "{#} µSv：バナナ {#} 千本、またはフライト {#} 千回",
  "{#} µSv: {#} million bananas, or {#} thousand flights": "{#} µSv：バナナ {#} 百万本、またはフライト {#} 千回",
  "{#} mSv: {#} bananas, or {#} flights": "{#} mSv：バナナ {#} 本、またはフライト {#} 回",
  "{#} mSv: {#} thousand bananas, or {#} flights": "{#} mSv：バナナ {#} 千本、またはフライト {#} 回",
  "{#} mSv: {#} million bananas, or {#} flights": "{#} mSv：バナナ {#} 百万本、またはフライト {#} 回",
  "{#} mSv: {#} bananas, or {#} thousand flights": "{#} mSv：バナナ {#} 本、またはフライト {#} 千回",
  "{#} mSv: {#} thousand bananas, or {#} thousand flights": "{#} mSv：バナナ {#} 千本、またはフライト {#} 千回",
  "{#} mSv: {#} million bananas, or {#} thousand flights": "{#} mSv：バナナ {#} 百万本、またはフライト {#} 千回",
  "{#} Sv: {#} bananas, or {#} flights": "{#} Sv：バナナ {#} 本、またはフライト {#} 回",
  "{#} Sv: {#} thousand bananas, or {#} flights": "{#} Sv：バナナ {#} 千本、またはフライト {#} 回",
  "{#} Sv: {#} million bananas, or {#} flights": "{#} Sv：バナナ {#} 百万本、またはフライト {#} 回",
  "{#} Sv: {#} bananas, or {#} thousand flights": "{#} Sv：バナナ {#} 本、またはフライト {#} 千回",
  "{#} Sv: {#} thousand bananas, or {#} thousand flights": "{#} Sv：バナナ {#} 千本、またはフライト {#} 千回",
  "{#} Sv: {#} million bananas, or {#} thousand flights": "{#} Sv：バナナ {#} 百万本、またはフライト {#} 千回",
  "{#} mSv: {#} bananas, {#} flights or {#} years of background": "{#} mSv：バナナ {#} 本、フライト {#} 回、自然放射線 {#} 年分",
  "{#} mSv: {#} thousand bananas, {#} flights or {#} years of background": "{#} mSv：バナナ {#} 千本、フライト {#} 回、自然放射線 {#} 年分",
  "{#} mSv: {#} million bananas, {#} flights or {#} years of background": "{#} mSv：バナナ {#} 百万本、フライト {#} 回、自然放射線 {#} 年分",
  "{#} mSv: {#} bananas, {#} thousand flights or {#} years of background": "{#} mSv：バナナ {#} 本、フライト {#} 千回、自然放射線 {#} 年分",
  "{#} mSv: {#} thousand bananas, {#} thousand flights or {#} years of background": "{#} mSv：バナナ {#} 千本、フライト {#} 千回、自然放射線 {#} 年分",
  "{#} mSv: {#} million bananas, {#} thousand flights or {#} years of background": "{#} mSv：バナナ {#} 百万本、フライト {#} 千回、自然放射線 {#} 年分",
  "{#} Sv: {#} bananas, {#} flights or {#} years of background": "{#} Sv：バナナ {#} 本、フライト {#} 回、自然放射線 {#} 年分",
  "{#} Sv: {#} thousand bananas, {#} flights or {#} years of background": "{#} Sv：バナナ {#} 千本、フライト {#} 回、自然放射線 {#} 年分",
  "{#} Sv: {#} million bananas, {#} flights or {#} years of background": "{#} Sv：バナナ {#} 百万本、フライト {#} 回、自然放射線 {#} 年分",
  "{#} Sv: {#} bananas, {#} thousand flights or {#} years of background": "{#} Sv：バナナ {#} 本、フライト {#} 千回、自然放射線 {#} 年分",
  "{#} Sv: {#} thousand bananas, {#} thousand flights or {#} years of background": "{#} Sv：バナナ {#} 千本、フライト {#} 千回、自然放射線 {#} 年分",
  "{#} Sv: {#} million bananas, {#} thousand flights or {#} years of background": "{#} Sv：バナナ {#} 百万本、フライト {#} 千回、自然放射線 {#} 年分",
  // your year
  "radon in the air  {#}": "空気中のラドン  {#}",
  "radon  {#}": "ラドン  {#}",
  "rocks and soil  {#}": "岩石と土壌  {#}",
  "ground  {#}": "大地  {#}",
  "food and water  {#}": "食物と水  {#}",
  "food  {#}": "食物  {#}",
  "cosmic rays  {#}": "宇宙線  {#}",
  "cosmic rays at {#} m  {#}": "標高 {#} m の宇宙線  {#}",
  "cosmic  {#}": "宇宙線  {#}",
  "{#} flights  {#}": "フライト {#} 回  {#}",
  "flights  {#}": "フライト  {#}",
  "{#} chest CT  {#}": "胸部CT {#} 回  {#}",
  "CT  {#}": "CT  {#}",
  "average {#}": "平均 {#}",
  "world average {#} mSv": "世界平均 {#} mSv",
  "worker limit {#}": "従事者限度 {#}",
  "worker limit {#} mSv": "従事者の限度 {#} mSv",
  "your year: {#} mSv": "あなたの1年：{#} mSv",
  "more than the yearly worker limit": "従事者の年間限度を超える",
  "{#} times the world average": "世界平均の {#} 倍",
  "close to the world average": "世界平均に近い",
  // dose at once
  "tracks through each cell nucleus: about {#}": "細胞核1個を通る飛跡：約 {#} 本",
  "tracks through each cell nucleus: about {#} (a few drawn)": "細胞核1個を通る飛跡：約 {#} 本（一部のみ描画）",
  "tracks through each cell nucleus: about {#} thousand (a few drawn)": "細胞核1個を通る飛跡：約 {#} 千本（一部のみ描画）",
  "tracks through each cell nucleus: about {#} million (a few drawn)": "細胞核1個を通る飛跡：約 {#} 百万本（一部のみ描画）",
  "no effect seen": "影響は見られない",
  "risk assumed": "リスクを仮定",
  "small added risk assumed": "わずかなリスク増を仮定",
  "sickness": "放射線障害",
  "lethal": "致死",
  "often lethal": "しばしば致死",
  "{#} mSv at once: any extra risk too small to measure": "一度に {#} mSv：リスク増は小さすぎて測れない",
  "{#} Sv at once: any extra risk too small to measure": "一度に {#} Sv：リスク増は小さすぎて測れない",
  "{#} mSv at once: no sickness; risk assumed to rise with dose": "一度に {#} mSv：障害なし、リスクは線量とともに増すと仮定",
  "{#} Sv at once: no sickness; risk assumed to rise with dose": "一度に {#} Sv：障害なし、リスクは線量とともに増すと仮定",
  "{#} mSv at once: radiation sickness: nausea, low blood counts": "一度に {#} mSv：放射線障害（吐き気、血球数の減少）",
  "{#} Sv at once: radiation sickness: nausea, low blood counts": "一度に {#} Sv：放射線障害（吐き気、血球数の減少）",
  "{#} mSv at once: about half die without treatment": "一度に {#} mSv：治療しないと約半数が死亡",
  "{#} Sv at once: about half die without treatment": "一度に {#} Sv：治療しないと約半数が死亡",
});
