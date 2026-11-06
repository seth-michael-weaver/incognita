/* Japanese: spentfuel (使用済み燃料を核種ごとに) */
WT.L.ch.spentfuel = {
  num: "レッスン 1", title: "使用済み燃料を核種ごとに", short: "核種ごとに",
  html: `
<div class="step">
  <h3>中に何があるか</h3>
  <p>取り出しから1年後のPWR燃料1トン（濃縮度4.2 %、50 GWd/t）：質量のほぼすべてはウランで、放射能のほぼすべては数キログラムに集中しています。</p>
</div>
<div class="step">
  <h3>放射能か放射性毒性か</h3>
  <p>ベクレルは崩壊の数を数え、シーベルトは各崩壊を飲み込んだときの害で重みづけします。そのためアルファ放出体が大きくなります。</p>
  <div class="btns"><button class="btn ghost" data-act="mA" aria-pressed="false">放射能（Bq）</button> <button class="btn ghost" data-act="mT" aria-pressed="true">放射性毒性（Sv）</button></div>
</div>
<div class="step">
  <h3>いつ誰が支配するか</h3>
  <p>帯にカーソルを合わせるかタップすると名前が出ます。時間軸に沿ってドラッグすると順位が変わります。</p>
</div>
<div class="step">
  <h3>プルトニウムをリサイクル</h3>
  <p>4年後の再処理でプルトニウムを（ウランと一緒に）取り出します。どれだけ取り残されるでしょうか？</p>
  <div class="btns"><span class="sf-k" style="font:600 13px var(--sans);color:var(--soft);margin-right:4px;align-self:center">Pu removed</span> <button class="btn ghost" data-act="pu0" aria-pressed="true">0 %</button> <button class="btn ghost" data-act="pu99" aria-pressed="false">99 %</button> <button class="btn ghost" data-act="pu999" aria-pressed="false">99.9 %</button></div>
</div>
<div class="step">
  <h3>マイナーアクチノイドも取り除く</h3>
  <p>アメリシウム、キュリウム、ネプツニウムも取り出すと、取り残された1 %または0.1 %が時間を決めます。</p>
  <div class="btns"><span class="sf-k" style="font:600 13px var(--sans);color:var(--soft);margin-right:4px;align-self:center">Pu removed</span> <button class="btn ghost" data-act="pu0" aria-pressed="true">0 %</button> <button class="btn ghost" data-act="pu99" aria-pressed="false">99 %</button> <button class="btn ghost" data-act="pu999" aria-pressed="false">99.9 %</button></div>
  <div class="btns"><span class="sf-k" style="font:600 13px var(--sans);color:var(--soft);margin-right:4px;align-self:center">Am, Cm, Np removed</span> <button class="btn ghost" data-act="ma0" aria-pressed="true">0 %</button> <button class="btn ghost" data-act="ma99" aria-pressed="false">99 %</button> <button class="btn ghost" data-act="ma999" aria-pressed="false">99.9 %</button></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "Am{#}": "Am{#}",
  "Am{#} {#} %": "Am{#} {#} %",
  "Cm{#}": "Cm{#}",
  "Cs{#}": "Cs{#}",
  "I{#}": "I{#}",
  "NEA {#} + computed": "NEA {#} + 計算",
  "Np{#}": "Np{#}",
  "Pu{#}": "Pu{#}",
  "Pu{#} {#} %": "Pu{#} {#} %",
  "Sr{#}": "Sr{#}",
  "Sr{#} + Y{#}": "Sr{#} + Y{#}",
  "Tc{#}": "Tc{#}",
  "activity": "放射能",
  "activity after {#} year (log scale)": "{#} 年後の放射能（対数目盛）",
  "below the ore after ≈ {#} years": "約 {#} 年で鉱石以下に",
  "computed (Bateman decay, ICRP{#}) · band height = share of the total": "計算値（Bateman 崩壊、ICRP{#}）· 帯の高さ = 全体に占める割合",
  "computed · band height = share": "計算値 · 帯の高さ = 割合",
  "drag along the time axis · hover a band": "時間軸に沿ってドラッグ · 帯にカーソルを合わせる",
  "inventory: OECD-NEA {#} ({#} %, {#} GWd/t) + computed fission products": "インベントリ：OECD-NEA {#}（{#} %、{#} GWd/t）+ 計算した核分裂生成物",
  "mass": "質量",
  "mass (log scale)": "質量（対数目盛）",
  "most of the {#} kg of fission products is stable; activity includes short-lived daughters": "核分裂生成物 {#} kg の大部分は安定；放射能には短寿命の娘核種を含む",
  "once-through": "ワンススルー",
  "once-through (no recycling)": "ワンススルー（リサイクルなし）",
  "ore: {#}×{#}⁵ Sv": "鉱石：{#}×{#}⁵ Sv",
  "other FP": "その他のFP",
  "other FP: mostly stable": "その他のFP：大部分は安定",
  "other fission products": "その他の核分裂生成物",
  "radiotoxicity if swallowed (Sv), relative to the ore": "経口摂取時の放射性毒性（Sv）、鉱石との比",
  "radiotoxicity ÷ ore": "放射性毒性 ÷ 鉱石",
  "reprocessing at {#} yr": "{#} 年で再処理",
  "the ore it came from: {#} t natural uranium + daughters = {#}×{#}⁵ Sv": "元の鉱石：天然ウラン {#} t + 娘核種 = {#}×{#}⁵ Sv",
  "then mostly Am{#} ({#} %)": "そのときの主役は Am{#}（{#} %）",
  "then mostly Pb{#} + Po{#} ({#} %)": "そのときの主役は Pb{#} + Po{#}（{#} %）",
  "then mostly Sr{#} + Y{#} ({#} %)": "そのときの主役は Sr{#} + Y{#}（{#} %）",
  "uranium": "ウラン",
  "years after unloading (log scale) →": "取り出し後の年数（対数目盛）→",
  "{#} g": "{#} g",
  "{#} kg": "{#} kg",
  "{#} million": "{#}00万",
  "{#} years:": "{#} 年：",
  "{#} yr": "{#} 年",
  "{#}¹³ Bq": "{#}¹³ Bq",
  "{#}¹⁰ Bq": "{#}¹⁰ Bq",
  "{#}¹⁶ Bq": "{#}¹⁶ Bq",
  "other Am, Cm": "その他の Am、Cm",
  "decay daughters (Ra, Pb, Po, Th…)": "娘核種（Ra、Pb、Po、Th…）",
  "daughters": "娘核種",
  "still above the ore after a million years": "100万年後もまだ鉱石より上",
  "drag the time · tap a band": "時間をドラッグ · 帯をタップ",
  "activity ÷ ore": "放射能 ÷ 鉱石",
  "activity (Bq), relative to the ore": "放射能（Bq）、鉱石との比",
});
