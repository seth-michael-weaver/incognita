/* Japanese: everyday (暮らしの中の原子力) */
WT.L.ch.everyday = {
  num: "レッスン 4", title: "暮らしの中の原子力", short: "暮らしの中で",
  html: `
<div class="step">
  <h3>PET検査</h3>
  <p>フッ素18のトレーサー（半減期110分）は陽電子を放出し、その一つひとつが背中合わせに飛び去る2本の511 keVガンマ線に変わります。ホットスポットをドラッグしてください。リングはペアごとに線を引き、線はトレーサーのある場所で交わります。</p>
</div>
<div class="step">
  <h3>放射線治療</h3>
  <p>いくつもの方向からのビームが腫瘍の上で重なるので、腫瘍は全線量を受け、健康な組織を通る各経路はその一部しか受けません。ドラッグしてビームを回し、脊髄から外してください。</p>
  <div class="ctl"><label for="ev-n">ビーム</label><input id="ev-n" type="range" data-bind="nb" data-instant min="1" max="7" step="1" value="5"><output data-show="nb" data-fmt="0"></output></div>
  <div class="ctl"><label for="ev-r">回転</label><input id="ev-r" type="range" data-bind="rotd" data-instant min="0" max="360" step="1" value="20"><output class="ev-rot"></output></div>
</div>
<div class="step">
  <h3>テクネチウム99m</h3>
  <p>核医学検査の大半を支えるこの同位体は、体の外のカメラで見える140 keVのガンマ線を出し、半減期が6時間なので1日たつとほとんど残りません。病院では<a href="#chains-3">モリブデン99から「搾り取り」ます</a>。</p>
  <div class="ctl"><label for="ev-t">投与後の時間</label><input id="ev-t" type="range" data-bind="th" data-instant min="0" max="48" step="0.5" value="0"><output data-show="th" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>放射性炭素年代測定</h3>
  <p>生き物は炭素14を取り込み続け、死後は半減期5730年で崩壊していきます。年代を設定するか、残量を測って年代を読み取ってください。</p>
  <div class="ctl"><label for="ev-a">年代（年）</label><input id="ev-a" type="range" data-bind="age" data-instant min="0" max="50000" step="10" value="5300"><output class="ev-age"></output></div>
  <div class="ctl"><label for="ev-f">残る炭素14（%）</label><input id="ev-f" type="range" data-bind="fr" data-instant min="0.3" max="100" step="0.1" value="52.7"><output class="ev-fr"></output></div>
</div>
<div class="step">
  <h3>煙感知器</h3>
  <p>密封されたアメリシウム241のかけらが小さな空気の隙間にアルファ粒子を送り込み、微小な電流を運ぶイオンをつくります。煙がイオンを捕まえると電流が下がり、警報が鳴ります。</p>
  <div class="ctl"><label for="ev-s">煙</label><input id="ev-s" type="range" data-bind="sm" data-instant min="0" max="1" step="0.01" value="0"><output class="ev-sm"></output></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "Am{#}": "Am{#}",
  "Mo{#} ({#} h)": "Mo{#}（{#} 時間）",
  "Tc{#}m ({#} h)": "Tc{#}m（{#} 時間）",
  "a strong gamma signal, easy to image": "ガンマ線の信号が強く、撮像しやすい",
  "alarm": "警報",
  "alpha particles make ions in the air": "アルファ粒子が空気中でイオンをつくる",
  "americium{#} (sealed)": "アメリシウム{#}（密封）",
  "americium{#} · half-life {#} years · alphas reach about {#} cm in air": "アメリシウム{#} · 半減期 {#} 年 · アルファ線の空気中の飛程は約 {#} cm",
  "beyond ~{#} years too little is left to measure": "約 {#} 年を超えると残りが少なすぎて測れない",
  "carbon{#}": "炭素{#}",
  "clean air: steady current": "きれいな空気：電流は一定",
  "current": "電流",
  "detector ring": "検出器リング",
  "dose": "線量",
  "fluorine{#} · half-life {#} min · {#} pairs recorded": "フッ素{#} · 半減期 {#} 分 · 記録したペア {#}",
  "gamma camera": "ガンマカメラ",
  "half-life {#} y": "半減期 {#} 年",
  "illustration": "イメージ図",
  "molybdenum{#}, half-life {#} h": "モリブデン{#}、半減期 {#} 時間",
  "nitrogen{#} (after a beta decay)": "窒素{#}（ベータ崩壊の後）",
  "pairs of {#} keV gamma rays, back to back": "背中合わせの {#} keV ガンマ線のペア",
  "physical decay only": "物理的な崩壊のみ",
  "spinal cord": "脊髄",
  "technetium{#}m, half-life {#} h": "テクネチウム{#}m、半減期 {#} 時間",
  "tracer": "トレーサー",
  "tumour": "腫瘍",
  "tumour {#} % · spinal cord {#} % · healthy tissue at most {#} %": "腫瘍 {#} % · 脊髄 {#} % · 健康な組織は最大 {#} %",
  "tumour {#} % · spinal cord {#} % · other tissue at most {#} %": "腫瘍 {#} % · 脊髄 {#} % · ほかの組織は最大 {#} %",
  "years": "年",
  "{#} beams cross: the tumour gets their sum": "{#} 本のビームが交差：腫瘍はその合計を受ける",
  "{#} h": "{#} 時間",
  "{#} h: {#} % left": "{#} 時間：残り {#} %",
  "{#} half-lives": "半減期 {#} 回分",
  "{#} keV gamma rays": "{#} keV ガンマ線",
  "{#} of {#} left": "残り {#}/{#}",
  "{#} years · {#} % left": "{#} 年 · 残り {#} %",
  "Ötzi the Iceman, ~{#} y": "アイスマンのエッツィ、約 {#} 年",
  "tracer (drag me)": "トレーサー（ドラッグ）",
  "each decay: two {#} keV gamma rays, back to back": "崩壊ごとに背中合わせの {#} keV ガンマ線が2本",
  "one beam: more dose near the skin than in the tumour": "ビーム1本：腫瘍より皮膚近くの線量が多い",
  "a beam crosses the spinal cord: turn the beams": "ビームが脊髄を通っている：ビームを回して",
  "fading: half is gone every {#} hours": "減衰中：{#} 時間ごとに半分に",
  "after a day, about {#} % is left": "1日後、残りは約 {#} %",
  "nitrogen{#}": "窒素{#}",
  "~{#} y: too little to measure": "約 {#} 年：少なすぎて測れない",
  "smoke: current down, alarm!": "煙：電流が下がり、警報！",
  "some ions caught: current dipping": "イオンの一部が捕まる：電流が低下",
});
