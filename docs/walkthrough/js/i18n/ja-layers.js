/* Japanese: layers (第12章). The scoreboard counts come from WT.board (js/scoreboard-data.js, loaded first), as in
 * js/ch/layers.js; a missing block or field drops the number, not the sentence. */
(function () {
  const B = WT.board || {};
  const nOf = (v) => (typeof v === "number" && isFinite(v) ? v : null);
  const tally = (o) => {
    if (!o) return null;
    const w = nOf(o.WIN), t = nOf(o.TIE), l = nOf(o.LOSS);
    if (w === null || t === null || l === null) return null;
    return { w, t, l, d: nOf(o.decided) ?? w + t + l };
  };
  const TE = tally(B.incognita), TT = tally(B.terra);
  const LIBS = B.terra && Array.isArray(B.terra.by_rival) ? B.terra.by_rival.map((r) => r && r.rival).filter((s) => typeof s === "string") : [];
  const ASOF = (() => {
    const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(B.asof || ""); if (!m) return null;
    return `${m[1]}年${+m[2]}月${+m[3]}日`;
  })();
  const figs = (T) => (T ? `<div class="figs" aria-label="${T.w}勝、${T.t}分け、${T.l}敗"><div class="w"><b>${T.w}</b><span>勝ち</span></div><div><b>${T.t}</b><span>引き分け</span></div><div class="l"><b>${T.l}</b><span>負け</span></div></div>` : "");
  const libs = LIBS.length ? `主要な評価済みデータライブラリ（${LIBS.join("、")}）` : "主要な評価済みデータライブラリ";
  const engineScore = TE ? `そうした比較${TE.d}件のうち、明確に上回ったのが${TE.w}件、引き分けが${TE.t}件、下回ったのが${TE.l}件です。` : "";
  const terraScore = TT ? `${libs}と比べて、${TT.d}件の比較のうち${TT.w}件で上回り、${TT.t}件で引き分け、${TT.l}件で下回っています。` : `${libs}と比較しています。`;

  WT.L.ch.layers = {
    num: "第12章", title: "模型はどのように層をなすか", short: "層",
    lead: "私たちが提供するものは、エンジンの上に層を重ねてつくられています。どの層も、測定と照らし合わせて自分の居場所を勝ち取らなければなりません。",
    html: `
<div class="step">
  <div class="layer-chip on">使用中</div>
  <h3>第1層 · すべての原子核に1つの規則</h3>
  <p>青い線は、ある反応に対するエンジンの予測です。エンジンはいちばん下の層で、すべての核種に同じ物理と同じ大域的な設定を使い、評価の基準となる断面積に合わせて調整されることは決してありません。</p>
  <div class="btns"><button class="btn ghost" data-act="reveal" aria-pressed="false">測定値を表示</button></div>
  <p>だからこそ検証が可能です。一度も見たことのない測定値で採点され、同じ原子核で計算した他の模型コードと比べられます。${engineScore}</p>
  ${figs(TE)}
</div>
<div class="step">
  <div class="layer-chip null">検証済み：まだ改善なし</div>
  <h3>第2層 · 各原子核の測定値</h3>
  <p>この層は、大域的な規則を各原子核固有の測定値に置き換えます。準位間隔D0、強度関数S0とS1（遅い中性子をどれだけ吸収しやすいか）、平均ガンマ線幅⟨Γγ⟩、そして既知のエネルギー準位です。</p>
  <div class="btns"><button class="btn ghost" data-act="ms0" aria-pressed="true">大域的な規則</button><button class="btn ghost" data-act="ms1" aria-pressed="false">固有の測定値</button></div>
  <p>オンにしても、線はほとんど動きません。これまでの検証では全体としての改善は見つかっていません。しきい値近くの反応を改善する唯一の変種は、中性子捕獲を悪化させてしまいます。そのため、この層は今のところオフのままです。</p>
</div>
<div class="step">
  <div class="layer-chip cand">候補</div>
  <h3>第3層 · 良いデータに従う（TERRA）</h3>
  <p>反応がよく測定されているところでは、線は測定値に従うべきです。第3層のTERRAは、良いデータがあるところではエンジンの線をそのデータに通し、ないところではエンジンに戻ります。</p>
  <div class="ctl"><label for="lay-cov">測定済みのエネルギー範囲の割合（%）</label><input id="lay-cov" type="range" data-bind="cov" min="0" max="1" step="0.01" value="0.45"><output data-show="covPct" data-fmt="0"></output></div>
  <p>${terraScore}その多くはサンプル内の比較です。ライブラリと同様、TERRAはそれらの測定値を見ています。</p>
  ${figs(TT)}
</div>
<div class="step">
  <div class="layer-chip wip">開発中</div>
  <h3>第4層 · 正直な誤差棒</h3>
  <p>いちばん上の層は、線のまわりに、3回に2回ほど真の値を含むはずの帯（68%の帯）を置きます。良いデータが値を押さえているところでは狭く、そうでないところでは広くなります。</p>
  <div class="ctl"><label for="lay-band">帯の幅 · 内側の測定値（%）</label><input id="lay-band" type="range" data-bind="band" min="0.2" max="2.5" step="0.05" value="1"><output data-show="inside" data-fmt="0"></output></div>
  <p>動かして、帯の内側にある測定値を数えてみましょう。狭すぎれば帯は持っていない精度を主張することになり、広すぎれば何も語りません。エンジン自身の帯はまだ採用されていません。すべての反応をまとめれば狙いどおりですが、反応の系統ごとにはまだ達成できていないからです。TERRAは独自の帯をもっており、それは上の比較に含まれています。</p>
</div>
<div class="step">
  <h3>現状</h3>
  <p>層が採用されるのは測定値と照らし合わせて検証された後だけで、役に立たなければオフのままです。現在、エンジンは使用中で、TERRAは候補です。測定された構造の層とエンジンの不確かさの帯は、まだ検証中です。</p>
  <p><a href="scoreboard.html" data-keep-lang>スコアボード全体を見る →</a> 勝てなかった比較のすべて、各対抗相手、そしてその読み方。</p>
  <div class="aside">${ASOF ? `${ASOF}時点のスコア。出典は` : "スコアの出典は"}プロジェクトの研究台帳です。図の曲線は説明用です。</div>
</div>`,
  };
})();
Object.assign(WT.L.labels, {
  "{#} · blind engine": "{#} · ブラインドのエンジン",
  "{#} · measured structure": "{#} · 測定された構造",
  "{#} · TERRA: anchored to data": "{#} · TERRA：データに固定",
  "{#} · uncertainty band": "{#} · 不確かさの帯",
  "measured here": "ここは測定済み",
  "neutron energy →": "中性子エネルギー →",
  "how often the reaction happens": "反応の起こりやすさ",
  "hollow dots: measurements the engine never saw": "白抜きの点：エンジンが見ていない測定値",
  "own measured values: the line barely moves": "固有の測定値：線はほぼ動かない",
  "global rule": "大域的な規則",
  "no measurements: TERRA falls back to the engine": "測定なし：TERRAはエンジンに戻る",
  "solid: follows the data · dashed: the engine alone": "実線：データに従う · 点線：エンジンのみ",
  "{#} of {#} measurements inside the band (aim: about {#} %)": "測定値{#}個 / {#}個が帯の内側（目標：約{#}%）",
  "no measurements to check the band against": "帯を確かめる測定値なし",
});
Object.assign(WT.L.ui, { nav_board: "スコアボード" });
