/* Japanese: waste (使用済み燃料の時間変化) */
WT.L.ch.waste = {
  num: "レッスン 1", title: "使用済み燃料の時間変化", short: "使用済み燃料",
  html: `
<div class="step">
  <h3>何が出てくるか</h3>
  <p>炉心で4〜5年過ごした燃料ペレットも、大部分はまだウランです。数パーセントが<b>核分裂生成物</b>、つまり分裂した原子です。約1 %がプルトニウムで、ごくわずかにアメリシウムなどのより重い<b>マイナーアクチノイド</b>（MA）が含まれます。</p>
  <div class="btns"><button class="btn" data-act="sort">原子を仕分ける</button></div>
</div>
<div class="step">
  <h3>最初の数百年</h3>
  <p>この曲線は、使用済み燃料を飲み込んだときの有害度を、その燃料の原料となったウラン鉱石と比べたものです。はじめは核分裂生成物が支配的ですが、その多くは半減期が約30年です。300年ほどたつと鉱石のレベルを下回ります。</p>
  <div class="ctl"><label for="wst-t1">取り出し後の年数</label><input id="wst-t1" type="range" data-bind="lt" data-instant min="0" max="6" step="0.01" value="1.5"><output data-show="yr" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>次はプルトニウム</h3>
  <p>残るのはプルトニウムとアメリシウムで、半減期は数百年から数万年です。これらのために、使用済み燃料は10万年以上にわたって鉱石のレベルを上回ります。</p>
  <div class="ctl"><label for="wst-t2">取り出し後の年数</label><input id="wst-t2" type="range" data-bind="lt" data-instant min="0" max="6" step="0.01" value="4"><output data-show="yr" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>リサイクルと核変換</h3>
  <p>プルトニウムを取り出して新しい燃料として燃やすと、その期間は約1万年に縮まります。さらに高速炉でマイナーアクチノイドも分裂させれば、残るのは核分裂生成物だけで、数百年で済みます。</p>
  <div class="btns"><button class="btn ghost" data-act="rp" aria-pressed="false">プルトニウムをリサイクル</button><button class="btn ghost" data-act="tm" aria-pressed="false">マイナーアクチノイドを核変換</button></div>
</div>`,
};
Object.assign(WT.L.labels, {
  // buttons (WT.tr)
  "Sort the atoms": "原子を仕分ける",
  "Mix them again": "もう一度混ぜる",
  // the pellet
  "uranium": "ウラン",
  "fission products": "核分裂生成物",
  "fission prod.": "核分裂生成物",
  "plutonium": "プルトニウム",
  "minor actinides": "マイナーアクチノイド",
  "minor act.": "MA",
  "~{#} %": "約 {#} %",
  "a used fuel pellet, {#} atoms": "使用済み燃料ペレット（原子 {#} 個）",
  "a used fuel pellet, {#} atoms shown": "使用済み燃料ペレット（原子 {#} 個を表示）",
  "the glow: fission products are the most radioactive": "光：核分裂生成物の放射能が最も強い",
  "the glow: the fission products are by far the most radioactive part": "光：核分裂生成物の放射能が群を抜いて強い",
  // time landscape
  "spent fuel": "使用済み燃料",
  "spent fuel, one tonne": "使用済み燃料 1 トン",
  "the ore": "鉱石",
  "the ore it was made from": "原料の鉱石",
  "{#} yr": "{#} 年",
  "uranium ore level": "ウラン鉱石のレベル",
  "the uranium ore it was made from": "原料のウラン鉱石",
  "{#} million": "{#}00万",
  "years after unloading (log scale) →": "取り出し後の年数（対数目盛）→",
  "hazard vs ore (log)": "有害度／鉱石（対数）",
  "hazard if swallowed, relative to the ore (log scale)": "経口摂取時の有害度、鉱石との比（対数目盛）",
  "Am, Cm, Np": "Am、Cm、Np",
  "americium, curium…": "アメリシウム、キュリウム…",
  "americium": "アメリシウム",
  "{#} years: {#} × the ore": "{#} 年：鉱石の {#} 倍",
  "below the ore it came from": "原料の鉱石を下回る",
  "mostly from fission products": "主に核分裂生成物から",
  "mostly from plutonium": "主にプルトニウムから",
  "mostly from americium": "主にアメリシウムから",
  "reaches the ore level after ~{#} years": "約 {#} 年で鉱石のレベルに達する",
  "recycle + transmute": "リサイクル＋核変換",
  "recycle Pu and transmute minor actinides": "Pu をリサイクルし、MA を核変換",
  "plutonium recycled": "Pu リサイクル",
  "plutonium recycled, minor actinides in the waste": "Pu はリサイクル、MA は廃棄物に残る",
  "only minor actinides removed": "MA のみ除去",
  "minor actinides removed, plutonium left in": "MA を除去、Pu は残す",
  "spent fuel as it is": "使用済み燃料のまま",
  "spent fuel kept as it is": "使用済み燃料をそのまま保管",
  "illustrative shape (after OECD-NEA)": "形は説明用（OECD-NEA に基づく）",
});
